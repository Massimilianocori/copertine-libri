"""Aggiornamento dei dati delle aste (PVP) e dei valori OMI di zona.

Uso (dalla radice del repository):
    python3 aste/raccolta/aggiorna.py            # giornaliero: elenco aste attive, dettagli dei lotti nuovi, OMI delle zone nuove,
                                                 # scrive aste/dati/lotti.json, auto.json, omi.json, live.json
    python3 aste/raccolta/aggiorna.py --offline  # rielabora solo dalla cache (nessuna richiesta)

Cosa legge:
- PVP, ricerca pubblica (POST .../ric-ms/ricerca/vendite): immobili residenziali e autoveicoli con vendita da oggi in poi,
  ordinati per data decrescente, 500 per pagina (circa 25 richieste in tutto);
- PVP, dettaglio pubblico (GET .../ve-ms/vendite/{id}/restricted) solo per i lotti nuovi dei comuni con una pagina città:
  si tengono solo i campi del bene (vedi rete.dettaglio_pulito), mai "soggetti" o allegati;
- Agenzia delle Entrate, GEOPOI (consultazione pubblica OMI): perimetri delle zone (una richiesta per comune e semestre),
  elenco zone, quotazioni delle sole zone che contengono almeno un lotto.
Le risposte grezze restano in aste/cache/ (fuori da git). In aste/dati/ vanno solo campi del lotto, senza dati personali.
"""
import argparse
import json
import re
import sys
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from html import unescape
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rete  # noqa: E402

RADICE = rete.RADICE
CACHE = rete.CACHE
DATI = RADICE / "dati"
ROMA = ZoneInfo("Europe/Rome")
ADESSO = datetime.now(ROMA)
OGGI = ADESSO.date()
ANNO_MAX = 2030            # date oltre questo anno: errori di battitura nel PVP, il lotto si scarta
ORIZZONTE = 730            # e comunque non oltre 24 mesi da oggi
SOGLIA_CITTA = 8           # lotti residenziali attivi nel comune per avere una pagina città (e il calcolo OMI)
MQ_MIN, MQ_MAX = 18, 1200  # superfici fuori da questo intervallo non si usano
RAPPORTO_MIN, RAPPORTO_MAX = 0.25, 3.0  # €/m² del lotto rispetto alla media OMI: fuori da qui la superficie è dubbia
CATEGORIE = {
    "case": {"tipoLotto": "IMMOBILI", "categoriaLotto": "IMMOBILE_RESIDENZIALE"},
    "auto": {"tipoLotto": "MOBILI", "categoriaLotto": "AUTOVEICOLI_E_CICLI"},
}


def norm(s):
    s = unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def scrivi(percorso, dati, compatto=True):
    percorso.parent.mkdir(parents=True, exist_ok=True)
    testo = json.dumps(dati, ensure_ascii=False, separators=(",", ":") if compatto else None,
                       indent=None if compatto else 1, sort_keys=False)
    percorso.write_text(testo + "\n", encoding="utf-8")


def scrivi_righe(percorso, testa, chiave, voci):
    """JSON con una voce per riga: i commit giornalieri cambiano solo le righe dei lotti cambiati (diff piccoli)."""
    percorso.parent.mkdir(parents=True, exist_ok=True)
    righe = [json.dumps(testa, ensure_ascii=False, separators=(",", ":"))[:-1] + f',"{chiave}":' + ("{" if isinstance(voci, dict) else "[")]
    if isinstance(voci, dict):
        corpo = [json.dumps(k) + ":" + json.dumps(v, ensure_ascii=False, separators=(",", ":")) for k, v in voci.items()]
    else:
        corpo = [json.dumps(v, ensure_ascii=False, separators=(",", ":")) for v in voci]
    testo = righe[0] + "\n" + ",\n".join(corpo) + "\n" + ("}" if isinstance(voci, dict) else "]") + "}\n"
    json.loads(testo)
    percorso.write_text(testo, encoding="utf-8")


def leggi(percorso, default=None):
    try:
        return json.loads(percorso.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


# ---------------------------------------------------------------- 1. elenco delle aste attive
def data_valida(s):
    """'2027-01-20T11:00' -> datetime, oppure None se assente, passata o implausibile (es. 2918, 2088)."""
    try:
        d = datetime.fromisoformat(str(s)[:16])
    except ValueError:
        return None
    if d.year > ANNO_MAX or d.date() > OGGI + timedelta(days=ORIZZONTE) or d.date() < OGGI:
        return None
    return d


def scarica_elenco(ep, cat, offline=False):
    cartella = CACHE / "elenco"
    cartella.mkdir(parents=True, exist_ok=True)
    file = cartella / f"{cat}.json"
    if offline:
        return leggi(file, {}).get("lotti", [])
    lotti, pagina, scartati = [], 0, 0
    while True:
        url = f"{ep['ricerca']}/ricerca/vendite?language=it&page={pagina}&size=500&sort=dataOraVendita,desc"
        r = rete.chiedi("POST", url, json_body=CATEGORIE[cat])
        corpo = r.get("body") or {}
        cont = corpo.get("content") or []
        for x in cont:
            if data_valida(x.get("dataOraVendita")):
                lotti.append(x)
            else:
                scartati += 1
        ultima = cont[-1].get("dataOraVendita", "") if cont else ""
        print(f"  {cat}: pagina {pagina + 1}/{corpo.get('totalPages')} – ultima data {ultima}", flush=True)
        if not cont or corpo.get("last") or (ultima[:10] and ultima[:10] < OGGI.isoformat()):
            break
        pagina += 1
    # stesso id due volte (l'elenco cambia mentre si sfoglia): tiene la prima
    visti, unici = set(), []
    for x in lotti:
        if x["id"] not in visti:
            visti.add(x["id"])
            unici.append(x)
    scrivi(file, {"letto_il": ADESSO.isoformat(timespec="minutes"), "lotti": unici})
    print(f"  {cat}: {len(unici)} lotti con vendita da oggi in poi (date implausibili o passate scartate: {scartati})")
    return unici


# ---------------------------------------------------------------- 2. dettagli (solo campi del bene)
MAX_DETTAGLI = 700  # dettagli nuovi per esecuzione: il resto il giorno dopo (i lotti escono lo stesso, con i dati dell'elenco)


def scarica_dettagli(ep, ids, offline=False):
    """Una richiesta alla volta, ogni 3 secondi circa. Se il PVP smette di rispondere (es. pagina «Server Unavailable»)
    si ferma subito: i lotti senza dettaglio si pubblicano con i soli campi dell'elenco."""
    cartella = CACHE / "dettagli"
    cartella.mkdir(parents=True, exist_ok=True)
    mancanti = [i for i in ids if not (cartella / f"{i}.json").exists()]
    if offline or not mancanti:
        return
    da_fare = mancanti[:MAX_DETTAGLI]
    print(f"  dettagli nuovi: {len(mancanti)}; in questa esecuzione: {len(da_fare)} (uno alla volta, con pausa)", flush=True)
    for n, i in enumerate(da_fare, 1):
        try:
            g = rete.chiedi("GET", f"{ep['vendite']}/vendite/{i}/restricted", tentativi=3)
            scrivi(cartella / f"{i}.json", rete.dettaglio_pulito(g))
        except Exception as e:  # noqa: BLE001
            stato = getattr(getattr(e, "response", None), "status_code", None)
            if stato == 404:
                continue
            print(f"  ! il PVP non risponde ai dettagli ({e}): mi fermo qui, gli altri lotti usano i dati dell'elenco", flush=True)
            return
        if n % 100 == 0:
            print(f"  … {n}/{len(da_fare)}", flush=True)


def dettaglio(i):
    return leggi(CACHE / "dettagli" / f"{i}.json")


# ---------------------------------------------------------------- 3. superficie e diritto venduto (dal testo dell'annuncio)
_NUM = r"(\d{1,4}(?:[.,]\d{1,2})?)"
RX_MQ = re.compile(_NUM + r"\s*(?:mq\b|m\.q\.|m2\b|m²|mt\.?\s*q|metri\s+quadr|metri\s+q\b)", re.I)
RX_MQ_PRIMA = re.compile(r"(?:mq\.?|m²|superficie(?:\s+\w+){0,3}\s+(?:di|pari\s+a)\s*(?:circa\s*)?(?:mq\.?)?)\s*" + _NUM + r"(?!\s*%)", re.I)
ACCESSORI = re.compile(r"(giardin|terrazz|cortil|corte\b|terren|box|garage|autorimess|cantin|balcon|posto\s+auto|soffitt|"
                       r"lastric|area\s+(?:urbana|scoperta|esterna|pertinenz)|magazzin|deposit|locale\s+(?:deposito|tecnico)|"
                       r"portic|piscin|tettoi|sottotett|solaio|androne|scoperto|pertinenz|"
                       r"rimessa|stalla|fienile|ettar|\bha\b|\bare\b|catastal\w*\s+terren|scala\s+estern|negozi|ufficio|laboratori)", re.I)
# nomi di singoli vani: «soggiorno (sup. netta circa 22 m2)» è la misura di una stanza, non dell'abitazione
VANI = re.compile(r"(soggiorn|salott|camer\w*|cucin|angolo\s+cottura|bagn|\bw\.?c\b|ingresso|disimpegn|corridoi|ripostigl|"
                  r"lavanderi|studio|letto)", re.I)
SUP_TOTALE = re.compile(r"(superficie|consistenza|commercial|lord|complessiv|total|convenzional|catastal|utile|tutto|intero|intera|"
                        r"appartament|abitazion|alloggio|immobile)", re.I)
PRINCIPALE = re.compile(r"(commercial|lord|complessiv|abitazion|appartament|alloggio|villa|villino|unit[aà]\s+immobiliar|"
                        r"calpestabil|abitabil|interna|superficie|immobile)", re.I)
RX_QUOTA = re.compile(r"quota\s+(?:pari\s+a\s+|di\s+|del(?:l[ao])?\s+)?(\d{1,4})\s*/\s*(\d{1,4})", re.I)
RX_FRAZ = re.compile(r"\b(\d{1,4})\s*/\s*(\d{1,4})\s+(?:di\s+|della\s+|del\s+)?(?:piena\s+)?(?:propriet|nuda|usufrutto|indiviso)", re.I)
RX_DIRITTO = re.compile(r"(nuda\s+propriet|usufrutto|diritto\s+di\s+(?:superficie|abitazione|uso)\b|propriet[aà]\s+superficiaria)", re.I)


def _num(s):
    s = s.replace(".", "").replace(",", ".") if re.search(r"\d\.\d{3}\b", s) else s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def superficie(testo):
    """Metri quadri dell'abitazione scritti nel testo, oppure None se assenti o ambigui.
    Valori accanto a giardino, box, terrazzo, terreno… si scartano. Se c'è una superficie «commerciale/lorda/complessiva»
    si usa quella; altrimenti tutti i valori rimasti devono coincidere. Se il testo dà le misure dei singoli vani (soggiorno,
    camera, bagno…) e nessuna superficie commerciale o complessiva: None. Nel dubbio: None ('superficie non indicata')."""
    if not testo:
        return None
    t = unescape(testo).replace("\n", " ")
    candidati, forti, totali, stanze = [], [], [], 0
    visti = set()
    for m in list(RX_MQ.finditer(t)) + list(RX_MQ_PRIMA.finditer(t)):
        if m.start(1) in visti:
            continue
        visti.add(m.start(1))
        v = _num(m.group(1))
        if v is None:
            continue
        prima = t[max(0, m.start(1) - 120):m.start(1)]
        dopo = t[m.end():m.end() + 25]
        # un accessorio nella stessa frase (dall'ultima virgola o punto) esclude il numero
        frase = re.split(r"[.;,:]\s|\.\s*$", prima)[-1]
        if ACCESSORI.search(frase) or (ACCESSORI.search(prima) and not PRINCIPALE.search(prima)):
            continue
        if re.search(r"(di\s+cui|oltre(\s+a)?|\+)\s*(mq\.?|m²)?\s*$", prima, re.I):
            continue
        if re.match(r"\s*(?:di\s+|a\s+|ad\s+)?(?:giardin|terrazz|cortil|corte|terren|box|garage|cantin|balcon|area|scoperto|pertinenz)", dopo, re.I):
            continue
        # dati catastali: se l'ultima categoria citata prima del numero è un box, una cantina o un magazzino (C/2…C/7)
        # il numero è di quell'accessorio
        cat_prima = re.findall(r"\b([ABCDEF])\s*/\s*(\d{1,2})\b", prima[-100:])
        if cat_prima and cat_prima[-1][0].upper() == "C" and cat_prima[-1][1] in ("2", "3", "4", "6", "7"):
            continue
        # stesso pezzo di frase (fino alla virgola o al punto precedente): un vano senza parole come «superficie» o «totale»
        pezzo = re.split(r"[,;]|(?<!sup)(?<!ca)\.\s", prima[-60:])[-1]
        if VANI.search(pezzo) and not SUP_TOTALE.search(pezzo):
            stanze += 1
            continue
        v = round(v)
        if not (MQ_MIN <= v <= MQ_MAX):
            continue
        if SUP_TOTALE.search(prima[-45:]):
            totali.append(v)
        candidati.append(v)
        if re.search(r"(commercial|lord|complessiv)\w*[^.;]{0,25}$", prima, re.I):
            forti.append(v)
    if forti and len(set(forti)) == 1:
        return forti[0]
    if stanze and not totali:
        return None  # il testo dà solo le misure dei vani: non si sommano
    if candidati and len(set(candidati)) == 1:
        return candidati[0]
    return None


RX_UNICODE_FRAZ = re.compile(r"[½¼¾⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]")
RX_FRAZ_VICINO = re.compile(r"(?:propriet|diritt|quot|ragione|spettant|indivis|pari\s+a|per\s+la)[^.;]{0,40}?\b(\d{1,4})\s*/\s*(\d{1,4})\b"
                            r"|\b(\d{1,4})\s*/\s*(\d{1,4})\b[^.;]{0,25}?(?:propriet|diritt|indivis|quota)", re.I)
RX_INDIVISA = re.compile(r"(quota|propriet[aà])\s+indivis|\bmet[aà]\s+(?:indivisa|della|del|dell)", re.I)


RX_NON_VENDITA = re.compile(r"(gravant|ipotec|pignorament|formalit|trascrizion|estin|cancellat|cessat|libero\s+da|privo\s+di|trasformat|riscatt|affranca|legge|\bn\.\s*$)", re.I)
RX_SOLO_ACCESSORIO = re.compile(r"^\W{0,3}(?:\w+\s+){0,3}?(?:del|della|dello|dei|delle|di|sul|sulla)?\s*(giardin|cortil|corte|area|terren|box|garage|"
                                r"lastric|posto|androne|scal|parti\s+comuni|beni\s+comuni|vialett|strad|passo|accesso)", re.I)


def _vera_frazione(t, m):
    prima = t[max(0, m.start() - 60):m.start()]
    dopo = t[m.end():m.end() + 40]
    return not RX_NON_VENDITA.search(prima) and not RX_SOLO_ACCESSORIO.search(dopo)


def diritto(testo):
    """'piena' se si vende la piena proprietà dell'intero; 'parziale' se l'annuncio parla di una quota o di un diritto
    diverso (nuda proprietà, usufrutto, diritto di superficie…). Si ignorano quote citate per ipoteche o pignoramenti,
    diritti estinti e quote di soli accessori (giardino, cortile, parti comuni)."""
    t = unescape(testo or "")
    for m in list(RX_UNICODE_FRAZ.finditer(t)) + list(RX_INDIVISA.finditer(t)):
        if _vera_frazione(t, m):
            return "parziale"
    for rx in (RX_QUOTA, RX_FRAZ, RX_FRAZ_VICINO):
        for m in rx.finditer(t):
            g = [x for x in m.groups() if x]
            if len(g) >= 2:
                a, b = int(g[0]), int(g[1])
                if b and a < b and not 1900 <= b <= 2100 and _vera_frazione(t, m):
                    return "parziale"
    for m in RX_DIRITTO.finditer(t):
        if _vera_frazione(t, m):
            return "parziale"
    return "piena"


# ---------------------------------------------------------------- 4. OMI (Agenzia delle Entrate – GEOPOI, CC BY 4.0)
def semestre_corrente(offline=False):
    f = CACHE / "omi" / "semestri.json"
    if not offline:
        try:
            s = rete.chiedi("GET", f"{rete.GEOPOI}/zoneomi.php?richiesta=5")
            scrivi(f, s)
        except Exception as e:  # noqa: BLE001
            print(f"  ! semestri OMI non letti: {e}")
    s = leggi(f) or [{"SEMESTRE": "20252"}]
    return max(x["SEMESTRE"] for x in s)


def codice_catastale(prov, comune, offline=False):
    f = CACHE / "omi" / f"comuni-{prov}.json"
    lista = leggi(f)
    if lista is None and not offline:
        lista = rete.chiedi("GET", f"{rete.GEOPOI}/zoneomi.php?richiesta=2&prov={prov}")
        scrivi(f, lista)
    for x in lista or []:
        if norm(x["DIZIONE"]) == norm(comune):
            return x["CODCOM"]
    return None


def zone_comune(cod, sem, offline=False):
    """Perimetri (GeoJSON) ed elenco delle zone OMI di un comune."""
    fp = CACHE / "omi" / f"perimetri-{cod}-{sem}.json"
    fz = CACHE / "omi" / f"zone-{cod}-{sem}.json"
    per, zone = leggi(fp), leggi(fz)
    if per is None and not offline:
        r = rete.chiedi("GET", f"{rete.GEOPOI}/zoneomi.php?richiesta=6&codcom={cod}&semestre={sem}", timeout=180)
        per = r.get("dat") or {}
        scrivi(fp, per)
    if zone is None and not offline:
        zone = rete.chiedi("GET", f"{rete.GEOPOI}/zoneomi.php?richiesta=3&codcom={cod}")
        scrivi(fz, zone)
    # GEOPOI scrive le zone fatte di più pezzi come un solo "Polygon" con più anelli (pezzi e buchi insieme): per sapere se un
    # punto è nella zona si contano TUTTI gli anelli della zona (regola pari/dispari), non solo il primo.
    poligoni = []
    for f in (per or {}).get("features", []):
        g = f.get("geometry") or {}
        anelli = g.get("coordinates") or []
        if g.get("type") == "MultiPolygon":
            anelli = [a for p in anelli for a in p]
        anelli = [a for a in anelli if len(a) >= 3]
        if not anelli:
            continue
        xs = [p[0] for a in anelli for p in a]
        ys = [p[1] for a in anelli for p in a]
        poligoni.append((f["properties"]["zona"], (min(xs), min(ys), max(xs), max(ys)), anelli))
    return poligoni, {z["ZONA"]: z for z in (zone or [])}


def dentro(x, y, anello):
    c = False
    j = len(anello) - 1
    for i in range(len(anello)):
        xi, yi = anello[i][:2]
        xj, yj = anello[j][:2]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi:
            c = not c
        j = i
    return c


def zona_di(poligoni, lat, lon):
    """Zona OMI che contiene il punto: dentro un numero dispari di anelli della zona (i buchi sono le altre zone)."""
    for zona, (x0, y0, x1, y1), anelli in poligoni:
        if x0 <= lon <= x1 and y0 <= lat <= y1 and sum(dentro(lon, lat, a) for a in anelli) % 2 == 1:
            return zona
    return None


def quotazioni(cod, link, zona, sem, lat, lon, offline=False):
    """Valori €/m² della zona (destinazione residenziale) dalla scheda pubblica stampaomi.php."""
    f = CACHE / "omi" / "quotazioni" / f"{cod}-{zona}-{sem}.html"
    if f.exists():
        t = f.read_text(encoding="utf-8")
    elif offline:
        return None
    else:
        t = rete.chiedi("GET", f"{rete.GEOPOI}/stampaomi.php?{cod}/{link}/{sem}/R/{zona}/{lon:.5f}/{lat:.5f}", testo=True)
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(t, encoding="utf-8")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    celle = [unescape(c).strip() for c in re.sub(r"<[^>]+>", "|", t).split("|")]
    celle = [re.sub(r"\s+", " ", c) for c in celle if c.strip()]
    out = {"prevalente": None, "valori": {}}
    for i, c in enumerate(celle):
        if c == "Tipologia prevalente:" and i + 1 < len(celle):
            out["prevalente"] = celle[i + 1]
        if c == "Fascia:" and i + 1 < len(celle):
            out["fascia"] = celle[i + 1]
    # righe: Tipologia | STATO | min | max | L/N | loc min | loc max | L/N
    for i in range(len(celle) - 4):
        tip, stato, a, b, sup = celle[i:i + 5]
        if stato.upper() in ("NORMALE", "OTTIMO", "SCADENTE") and re.fullmatch(r"\d+", a) and re.fullmatch(r"\d+", b) and sup in ("L", "N"):
            out["valori"].setdefault(tip, {})[stato.upper() if stato.isupper() else stato.upper() + "*"] = [int(a), int(b), sup, stato.isupper()]
    return out if out["valori"] else None


TIPOLOGIA_OMI = {
    "ABITAZIONE_TIPO_SIGN": "Abitazioni signorili", "CASTELLI_PALAZZI": "Abitazioni signorili",
    "CASTEL_IMM_PREGIO_STR": "Abitazioni signorili",
    "ABITAZIONE_TIPO_CIV": "Abitazioni civili",
    "ABITAZIONE_TIPO_ECO": "Abitazioni di tipo economico", "ABITAZIONE_TIPO_POP": "Abitazioni di tipo economico",
    "ABITAZIONE_TIPO_UPOP": "Abitazioni di tipo economico", "ABITAZIONE_TIPO_RUR": "Abitazioni di tipo economico",
    "VILLA": "Ville e Villini", "ABITAZIONE_IN_VILLE": "Ville e Villini", "ABITAZIONE_IN_VILLINI": "Ville e Villini",
}
RESIDENZIALI_OMI = ("Abitazioni signorili", "Abitazioni civili", "Abitazioni di tipo economico", "Ville e Villini")


def valore_omi(q, cat_bene):
    """Sceglie la tipologia OMI per il lotto e restituisce [tipologia, min, max, media, stato, superficie L/N]."""
    if not q:
        return None
    voluta = TIPOLOGIA_OMI.get(cat_bene)
    prev = q.get("prevalente")
    ordine = [voluta] if voluta else []
    ordine += [prev if prev in RESIDENZIALI_OMI else None, "Abitazioni civili", "Abitazioni di tipo economico"]
    for tip in [t for t in ordine if t]:
        stati = q["valori"].get(tip)
        if not stati:
            continue
        for st in ("NORMALE", "NORMALE*", "OTTIMO", "OTTIMO*", "SCADENTE", "SCADENTE*"):
            if st in stati:
                a, b, sup, _ = stati[st]
                return [tip, a, b, round((a + b) / 2), st.rstrip("*").lower(), sup]
    return None


# ---------------------------------------------------------------- 5. pulizia dei campi pubblicati
# etichette del PVP: Libero, Occupato, Occupato senza titolo, In corso di liberazione, Non specificata
DISP = {"LIBER": "libero", "OCCUP": "occupato", "OCCST": "senza_titolo", "INCOR": "liberazione", "NON_SPECIFICATA": "nd"}
TIPI_BENE = {
    "APPARTAMENTO": "Appartamento", "ABITAZIONE_TIPO_CIV": "Abitazione civile", "ABITAZIONE_TIPO_ECO": "Abitazione economica",
    "ABITAZIONE_TIPO_POP": "Abitazione popolare", "ABITAZIONE_TIPO_UPOP": "Abitazione ultrapopolare",
    "ABITAZIONE_TIPO_SIGN": "Abitazione signorile", "ABITAZIONE_IN_VILLINI": "Villino", "ABITAZIONE_IN_VILLE": "Villa",
    "VILLA": "Villa", "ABITAZIONE_TIPO_RUR": "Abitazione rurale", "FABBRICATO": "Fabbricato",
    "FABBRICATO_IN_COSTR": "Fabbricato in costruzione", "CASTELLI_PALAZZI": "Palazzo storico",
    "CASTEL_IMM_PREGIO_STR": "Immobile di pregio", "ABITAZIONI_E_ALL_TIPICI": "Abitazione tipica",
}
# Lotti classificati «residenziali» sul PVP che in realtà sono solo box, garage, cantine, negozi, uffici o terreni
# (es. 40 garage di un condominio di Cuneo con categoria «abitazione civile»): si riconoscono dal titolo o dalle sole
# categorie catastali C/… e si scartano come «non abitazione».
RX_CATASTO = re.compile(r"\b(?:cat(?:egoria|\.)?|ctg\.?)\s*(?:catastale\s*)?([A-F])\s*/?\s*(\d{1,2})\b", re.I)
RX_TITOLO_NON_CASA = re.compile(r"^\W*(?:(?:lotto\s*[\w°]*|piena|nuda|intera|propriet\w*|diritt\w*|quota|superficie|pari|di|del|dello|"
                                r"della|dell['’]|su|sul|sulla|ad?|e|\d+\s*/\s*\d+)\W*){0,8}(garage|box|autorimess|"
                                r"posto\s+auto|posti\s+auto|cantin|magazzin|locale\s+(?:deposito|commerciale|magazzino)|deposito|"
                                r"negozio|ufficio|terreno|lastrico)", re.I)
RX_CASA = re.compile(r"(appartament|abitazion|abitativ|villa|villin|alloggio|\bcasa\b|residenzial|fabbricat|\bvani\b)", re.I)


def non_abitazione(titolo_lotto, testo):
    """True se il lotto è solo un accessorio, un locale commerciale, un ufficio o un terreno."""
    cat = [(a.upper(), n) for a, n in RX_CATASTO.findall(testo or "")]
    a_cat = {n for a, n in cat if a == "A"}
    if RX_TITOLO_NON_CASA.search(titolo_lotto or "") and not RX_CASA.search(titolo_lotto or ""):
        return True
    if cat and all(a == "C" for a, _ in cat) and not RX_CASA.search(testo or ""):
        return True
    if a_cat == {"10"} and re.search(r"uffic", testo or "", re.I) and not re.search(r"residenzial|abitativ|trasformat", testo or "", re.I):
        return True
    return False


PAROLE_MINUSCOLE = {"di", "del", "della", "dei", "delle", "degli", "da", "de", "la", "le", "lo", "il", "e", "in", "al", "alla",
                    "ai", "agli", "sul", "sulla", "dello", "d", "l", "via"}


def titolo(s):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    if not s:
        return s
    if s.isupper() or s.islower():
        parole = []
        for i, p in enumerate(re.split(r"(\s+|-|'|`|’|\()", s.lower())):
            if p and p not in PAROLE_MINUSCOLE or (i == 0 and p):
                p = p[:1].upper() + p[1:]
            parole.append(p)
        s = "".join(parole)
        s = re.sub(r"\bS\. ?", "S. ", s)
    return s.replace("`", "’").replace("'", "’")


def via_pulita(v):
    """Solo il nome della strada, senza numero civico, CAP e comune (il dettaglio completo è sul PVP)."""
    v = str(v or "").split(",")[0]
    # resti di civico, isolato o piano: «snc P T-1», «is.397», «n. SNC Frazione…», «s.n.c. - Località…»
    v = re.sub(r"\s+(?:n\.?\s*)?(?:snc\b|s\.n\.c\.?|s\.n\.|is\.\s*\d+|isol\.?\s*\d+|p\.\s*t\.?(?:\s|-|$)).*$", "", v, flags=re.I)
    v = re.sub(r"^(via|viale|piazza|corso|strada|contrada|località|frazione)\s+\1\b", r"\1", v.strip(), flags=re.I)  # «Via VIA DEMO»
    # taglia dal primo numero civico in poi ("Via Xiboli 313-315", "via C. Goldoni n.46", "Via Orciari 8 int. A"),
    # ma non i numeri che fanno parte del nome subito dopo il tipo di strada ("Via 4 Novembre", "Viale 2 Giugno")
    sp = [m.start() for m in re.finditer(r"\s", v.strip())]
    m = re.search(r"(?:\s|^)(?:nn?\.?\s*|nr\.?\s*|n°\s*|civico\s*|civ\.\s*|n\.c\.\s*)?\d", v.strip(), re.I)
    if m and len(sp) >= 2 and m.start() >= sp[1]:
        v = v.strip()[:m.start()]
    v = re.sub(r"\s+(?:n\.?|nn\.?|nr\.?|int\.?|interno|scala|sc\.?|piano|angolo|e|-)\s*$", "", v.strip(), flags=re.I)
    v = re.sub(r"\s(?:n\.?|nr\.?|civico|km\.?)\s*\d[\d/]*[a-z]?\s*$|\s(?:snc|s\.n\.c\.?|n\.ri|nn\.|cm)\s*$", "", v, flags=re.I)
    if re.fullmatch(r"(?i)\S+\s+(?:nd|n\.d\.?|n/d|--?)", v.strip()):
        return None  # «Via nd»: strada non indicata
    v = re.sub(r"[\s,]+\d+[\s/]*[a-zA-Z]?(?:/\d+)?\s*$", "", v)
    v = re.sub(r"\s+\d{5}\b.*$", "", v).strip(" ,.-")
    lettere = [c for c in v if c.isalpha()]
    if lettere and sum(c.isupper() for c in lettere) / len(lettere) > 0.6:
        v = v.upper()  # «C.DA GIUNCHI» -> «C.da Giunchi» con titolo() più sotto
    if not v or re.match(r"^\d", v) or len(v) < 4 or len(v) > 70:
        return None
    if not re.match(r"(?i)(via|viale|v\.le|piazza|p\.zza|piazzale|corso|c\.so|largo|vicolo|strada|contrada|c\.da|località|loc\.|"
                    r"lungo|salita|traversa|borgo|frazione|fraz\.|calle|campo|rione|circonvallazione|rampa|discesa|vico|"
                    r"galleria|parco|passaggio|calata|riviera|fondamenta|salizada|stradone|stradella|baluardo|regione|borgata)", v):
        return None
    v = titolo(v)
    v = v[:1].upper() + v[1:]
    v = re.sub(r"(?<=\s)(Dell|Dall|Sull|All|Nell|D)’(?=\w)", lambda m: m.group(1).lower() + "’", v)  # «Via Dell’Acate» -> «Via dell’Acate»
    return re.sub(r"(?<=\s)(Di|Del|Della|Dei|Degli|Delle|Dello|Da|Dal|Dalla|E|In|Al|Alla|Ai|Agli|Sul|Sulla)(?=\s)", lambda m: m.group(1).lower(), v)


def numero(x):
    try:
        x = float(str(x).replace(",", ".")) if isinstance(x, str) else float(x)
    except (TypeError, ValueError):
        return None
    return round(x) if x > 0 else None


def chiave_comune(citta, prov):
    return f"{norm(citta)}|{norm(prov)}"


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", norm(t)).strip("-")


MARCHE = ["Alfa Romeo", "Aston Martin", "Land Rover", "Mercedes-Benz", "Mercedes", "Rolls-Royce", "Harley-Davidson", "Moto Guzzi",
          "Abarth", "Audi", "BMW", "Chevrolet", "Chrysler", "Citroen", "Citroën", "Cupra", "Dacia", "Daewoo", "Daihatsu", "DR",
          "DS", "Ducati", "Ferrari", "Fiat", "Ford", "Honda", "Hyundai", "Iveco", "Jaguar", "Jeep", "Kawasaki", "Kia", "Kymco",
          "Lamborghini", "Lancia", "Lexus", "Maserati", "Mazda", "Mini", "Mitsubishi", "Nissan", "Opel", "Peugeot", "Piaggio",
          "Porsche", "Renault", "Seat", "Skoda", "Smart", "SsangYong", "Subaru", "Suzuki", "Tesla", "Toyota", "Volkswagen",
          "Volvo", "Yamaha", "Aprilia", "KTM", "Triumph", "MG", "BYD", "Isuzu", "Man", "Scania", "DAF", "Lynk", "Polestar"]
RX_MARCA = re.compile(r"\b(" + "|".join(re.escape(m) for m in sorted(MARCHE, key=len, reverse=True)) + r")\b", re.I)
TIPI_AUTO = {"AUTOVETTURE": "Automobile", "AUTOMEZZI_COMMERCIALI": "Veicolo commerciale",
             "MOTOVEICOLO_O_CICLOMOTORE": "Moto o ciclomotore", "VEICOLI": "Veicolo"}


def marca(testo):
    m = RX_MARCA.search(testo or "")
    if not m:
        return None
    for x in MARCHE:
        if x.lower() == m.group(1).lower():
            return {"Mercedes": "Mercedes-Benz", "Citroen": "Citroën"}.get(x, x)
    return None


def anno_auto(testo):
    m = re.search(r"immatricolazion\w*\s*(?:[:\-]|del|nel|anno|in data)?\s*(?:\d{1,2}[/.-]\d{1,2}[/.-])?((?:19[89]|20[0-2])\d)\b", testo or "", re.I)
    if not m:
        m = re.search(r"\banno\s*(?:di\s+immatricolazione)?\s*[:\-]?\s*((?:19[89]|20[0-2])\d)\b", testo or "", re.I)
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------- elaborazione
PRIORITA = ["Roma", "Milano", "Napoli", "Torino", "Palermo", "Genova", "Bologna", "Firenze", "Bari", "Catania", "Venezia", "Verona",
            "Messina", "Padova", "Trieste", "Brescia", "Taranto", "Parma", "Prato", "Modena", "Reggio di Calabria", "Reggio nell'Emilia",
            "Perugia", "Ravenna", "Livorno", "Cagliari", "Foggia", "Rimini", "Salerno", "Ferrara", "Sassari", "Latina", "Siracusa", "Pescara"]


def province_pvp(ep, offline=False):
    """Nome della provincia -> (sigla, regione), dai filtri pubblici della ricerca PVP (una richiesta, poi cache)."""
    f = CACHE / "filtri.json"
    dati = leggi(f)
    if dati is None and not offline and ep:
        try:
            dati = rete.chiedi("GET", f"{ep['backoffice']}/filtriRicercaVendite")
            scrivi(f, dati)
        except Exception as e:  # noqa: BLE001
            print(f"  ! filtri PVP non letti: {e}")
    out = {}
    for naz in ((dati or {}).get("body") or {}).get("nazioni", []):
        for reg in naz.get("regioni", []):
            for pr in reg.get("province", []):
                sigla = pr["codiceProvincia"] if pr["codiceProvincia"] not in ("-", "") else {"sud sardegna": "SU"}.get(norm(pr["descProvincia"]))
                if sigla:
                    out[norm(pr["descProvincia"])] = (sigla, reg["descRegione"])
    return out


def stato_disp(x):
    disp = sorted({DISP.get(c, "nd") for c in (x.get("disponibilita") or ["NON_SPECIFICATA"])})
    if len(disp) > 1:
        disp = [c for c in disp if c != "nd"] or ["nd"]
    return disp[0] if len(disp) == 1 else ("occupato" if "occupato" in disp else "misto")


def calcola_sconto(L):
    """€/m² e sconto solo se: superficie certa, piena proprietà, zona OMI trovata, rapporto plausibile."""
    mq, valore = L.get("mq"), L.get("omi")
    if mq and valore and L.get("diritto") == "piena":
        r_min = L["minima"] / mq / valore[3]
        r_base = L["base"] / mq / valore[3]
        if RAPPORTO_MIN <= r_min <= RAPPORTO_MAX * 0.75 and RAPPORTO_MIN <= r_base <= RAPPORTO_MAX:
            L["eur_mq_min"] = round(L["minima"] / mq)
            L["eur_mq_base"] = round(L["base"] / mq)
            L["sconto_min"] = round((r_min - 1) * 100)
            L["sconto_base"] = round((r_base - 1) * 100)
        else:
            L["mq_dubbio"] = True


def elabora(ep, case, auto, offline=False, offline_omi=None):
    offline_omi = offline if offline_omi is None else offline_omi
    precedenti = {L["id"]: L for L in (leggi(DATI / "lotti.json", {}) or {}).get("lotti", [])}
    # comuni con abbastanza lotti
    conta = {}
    for x in case:
        i = x.get("indirizzo") or {}
        if not i.get("citta") or not x.get("prezzoBaseAsta"):
            continue
        k = chiave_comune(i["citta"], i.get("provincia"))
        conta[k] = conta.get(k, 0) + 1
    scelti = {k for k, n in conta.items() if n >= SOGLIA_CITTA}
    # anche i lotti senza comune nell'elenco: il comune si legge nel dettaglio.
    # Ordine dei dettagli da scaricare: prima le città grandi, poi le altre per numero di aste, per ultimi i lotti senza comune.
    pos = {norm(c): i for i, c in enumerate(PRIORITA)}

    def ordine(x):
        i = x.get("indirizzo") or {}
        if not i.get("citta"):
            return (2, 0, 0, x["id"])
        return (0 if norm(i["citta"]) in pos else 1, pos.get(norm(i["citta"]), 0), -conta.get(chiave_comune(i["citta"], i.get("provincia")), 0), x["id"])
    ids = [x["id"] for x in sorted(case, key=ordine) if not (x.get("indirizzo") or {}).get("citta") or
           chiave_comune((x.get("indirizzo") or {}).get("citta"), (x.get("indirizzo") or {}).get("provincia")) in scelti]
    print(f"  comuni con almeno {SOGLIA_CITTA} lotti: {len(scelti)}; lotti da trattare: {len(ids)}")
    if not offline:
        scarica_dettagli(ep, ids)
    province = province_pvp(ep, offline)

    sem = semestre_corrente(offline_omi)
    omi_vecchio = leggi(DATI / "omi.json", {}) or {}
    omi = {"semestre": sem, "letto_il": OGGI.isoformat(), "comuni": {}}
    if omi_vecchio.get("semestre") == sem:
        omi["comuni"] = omi_vecchio.get("comuni", {})
        omi["letto_il"] = omi_vecchio.get("letto_il", OGGI.isoformat())
    cache_zone = {}

    lotti, scarti = [], {"senza dettaglio": 0, "campi mancanti": 0, "esito presente": 0, "non abitazione": 0}
    senza_dettaglio = 0
    da_trattare = set(ids)
    for x in case:
        if x["id"] not in da_trattare:
            continue
        d = dettaglio(x["id"])
        prev = precedenti.get(x["id"])
        if not d and prev and prev.get("fonte") == "dettaglio":
            # lotto già elaborato con il dettaglio in un giorno precedente (la cache può mancare): si aggiornano solo prezzi e date
            base, minima = numero(x.get("prezzoBaseAsta")), numero(x.get("offertaMinima"))
            dt = data_valida(x.get("dataOraVendita"))
            if x.get("esito") or not (base and minima and dt) or minima > base:
                scarti["esito presente" if x.get("esito") else "campi mancanti"] += 1
                continue
            L = {k: v for k, v in prev.items() if k not in ("eur_mq_min", "eur_mq_base", "sconto_min", "sconto_base", "mq_dubbio")}
            L.update({"base": base, "minima": minima, "rialzo": numero(x.get("rialzoMinimo")), "data": dt.isoformat(timespec="minutes"),
                      "pubblicato": x.get("dataPubblicazione"), "disp": stato_disp(x)})
            calcola_sconto(L)
            lotti.append(L)
            continue
        if not d:
            # senza dettaglio (non ancora scaricato o PVP non raggiungibile): si usano i campi dell'elenco
            i0 = x.get("indirizzo") or {}
            pr = province.get(norm(i0.get("provincia")))
            if not i0.get("citta") or not pr:
                scarti["senza dettaglio"] += 1
                continue
            d = {"lotto": {"indirizzo": {"descComune": i0["citta"], "codProvincia": pr[0], "descRegione": pr[1],
                                         "via": i0.get("via"), "coordinate": i0.get("coordinate")}}, "beni": []}
            senza_dettaglio += 1
            fonte = "elenco"
        else:
            fonte = "dettaglio"
        if x.get("esito"):
            scarti["esito presente"] += 1
            continue
        base, minima = numero(x.get("prezzoBaseAsta")), numero(x.get("offertaMinima"))
        dt = data_valida(x.get("dataOraVendita"))
        ind = (d.get("lotto") or {}).get("indirizzo") or {}
        beni = d.get("beni") or []
        if not ind.get("descComune") and beni:
            ind = beni[0].get("indirizzo") or {}
        comune = ind.get("descComune") or (x.get("indirizzo") or {}).get("citta")
        prov = ind.get("codProvincia")
        if not (base and minima and dt and comune and prov) or minima > base:
            scarti["campi mancanti"] += 1
            continue
        # solo abitazioni: lotti fatti solo di negozi, uffici, box o terreni (anche se classificati "residenziali") si scartano
        abitazioni = [b for b in beni if b.get("codTipologiaBene") in TIPI_BENE]
        if beni and not abitazioni:
            scarti["non abitazione"] += 1
            continue
        cat = (abitazioni[0].get("codTipologiaBene") if abitazioni else None) or (x.get("categoriaBene") or [None])[0]
        if cat not in TIPI_BENE:
            scarti["non abitazione"] += 1
            continue
        testo = " ".join([str((d.get("lotto") or {}).get("descLotto") or ""), str(x.get("descLotto") or "")] +
                         [str(b.get("descrizione") or "") for b in beni])
        titolo_lotto = str((d.get("lotto") or {}).get("descLotto") or x.get("descLotto") or "").strip()
        if non_abitazione(titolo_lotto, testo):
            scarti["non abitazione"] += 1
            continue
        n_abitazioni = max(1, len(abitazioni))
        mq = None
        if n_abitazioni == 1:
            campo = numero(abitazioni[0].get("superficie")) if abitazioni else None
            mq = campo if campo and MQ_MIN <= campo <= MQ_MAX else superficie(testo)
        dir_ = diritto(testo)
        disp = stato_disp(x)
        coord = ind.get("coordinate") or (x.get("indirizzo") or {}).get("coordinate") or {}
        lat, lon = coord.get("latitudine"), coord.get("longitudine")
        # zona OMI
        zona = valore = None
        cod = None
        if lat and lon and 35 < float(lat) < 48 and 6 < float(lon) < 19:
            ck = (prov, norm(comune))
            if ck not in cache_zone:
                try:
                    cod = codice_catastale(prov, comune, offline_omi)
                    cache_zone[ck] = (cod, *zone_comune(cod, sem, offline_omi)) if cod else (None, [], {})
                except Exception as e:  # noqa: BLE001
                    print(f"  ! zone OMI di {comune}: {e}")
                    cache_zone[ck] = (None, [], {})
            cod, poligoni, elenco = cache_zone[ck]
            z = zona_di(poligoni, float(lat), float(lon)) if poligoni else None
            if z and z in elenco:
                C = omi["comuni"].setdefault(cod, {"nome": titolo(comune), "prov": prov, "zone": {}})
                if z not in C["zone"]:
                    try:
                        q = quotazioni(cod, elenco[z]["LINK_ZONA"], z, sem, float(lat), float(lon), offline_omi)
                    except Exception as e:  # noqa: BLE001
                        print(f"  ! quotazioni {cod} {z}: {e}")
                        q = None
                    if q:
                        C["zone"][z] = {"nome": titolo(elenco[z]["DIZIONE"]), "fascia": elenco[z].get("FASCIA"),
                                        "prevalente": q.get("prevalente"), "valori": q["valori"]}
                if z in C["zone"]:
                    zona = [cod, z]
                    if cat != "FABBRICATO_IN_COSTR":
                        valore = valore_omi(C["zone"][z], cat)
        L = {
            "id": x["id"], "comune": titolo(comune), "prov": prov, "regione": ind.get("descRegione") or (province.get(norm(ind.get("descProvincia"))) or [None, None])[1], "via": via_pulita(ind.get("via") or (x.get("indirizzo") or {}).get("via")),
            "tipo": TIPI_BENE.get(cat, "Abitazione"), "cat": cat, "n_beni": len(beni), "n_abitazioni": n_abitazioni,
            "base": base, "minima": minima, "rialzo": numero(x.get("rialzoMinimo")), "data": dt.isoformat(timespec="minutes"),
            "termine": None, "pubblicato": x.get("dataPubblicazione"), "disp": disp,
            "modalita": d.get("descModVendita"), "tipo_vendita": d.get("descTipoVendita"),
            "tribunale": titolo((x.get("tribunale") or "").replace("Tribunale di ", "")) or None,
            "mq": mq, "diritto": dir_, "zona": zona, "omi": valore, "fonte": fonte,
        }
        if d.get("dataTermPresOff"):
            try:
                g, m_, a = d["dataTermPresOff"].split("/")
                L["termine"] = f"{a}-{m_}-{g}" + (f"T{d['oraTermPresOff']}" if d.get("oraTermPresOff") else "")
            except ValueError:
                pass
        calcola_sconto(L)
        lotti.append(L)
    per_comune = {}
    for L in lotti:
        per_comune[(L["comune"], L["prov"])] = per_comune.get((L["comune"], L["prov"]), 0) + 1
    fuori = sum(1 for L in lotti if per_comune[(L["comune"], L["prov"])] < SOGLIA_CITTA)
    lotti = [L for L in lotti if per_comune[(L["comune"], L["prov"])] >= SOGLIA_CITTA]
    print(f"  lotti pubblicabili: {len(lotti)} in {len([k for k, n in per_comune.items() if n >= SOGLIA_CITTA])} comuni; "
          f"scartati: {scarti}; in comuni sotto soglia dopo il dettaglio: {fuori}; pubblicati con i soli dati dell'elenco: {senza_dettaglio}")

    # veicoli (pagina nazionale, senza confronto di valore e senza testo dell'annuncio: può contenere la targa)
    veicoli = []
    for x in auto:
        if x.get("esito"):
            continue
        base, minima = numero(x.get("prezzoBaseAsta")), numero(x.get("offertaMinima"))
        dt = data_valida(x.get("dataOraVendita"))
        i = x.get("indirizzo") or {}
        cat = (x.get("categoriaBene") or [None])[0]
        if not (base and dt and i.get("citta")):
            continue
        veicoli.append({"id": x["id"], "tipo": TIPI_AUTO.get(cat, "Veicolo"), "marca": marca(x.get("descLotto")),
                        "anno": anno_auto(x.get("descLotto")), "comune": titolo(i["citta"]), "prov": titolo(i.get("provincia")),
                        "base": base, "minima": minima if minima and minima <= base else None, "data": dt.isoformat(timespec="minutes"),
                        "disp": None, "tribunale": titolo((x.get("tribunale") or "").replace("Tribunale di ", "")) or None})
    return lotti, veicoli, omi


def scrivi_live(case, auto, letto, pubblicati):
    """live.json: per ogni lotto attivo [prezzo base, offerta minima, data e ora della vendita]; le pagine lo leggono da GitHub
    per aggiornare i numeri e nascondere le aste passate o tolte, senza nuove pubblicazioni su Netlify."""
    ids = {}
    for x in case + auto:
        if x.get("esito") or x["id"] not in pubblicati:
            continue
        dt = data_valida(x.get("dataOraVendita"))
        if dt:
            ids[str(x["id"])] = [numero(x.get("prezzoBaseAsta")), numero(x.get("offertaMinima")), dt.isoformat(timespec="minutes")]
    scrivi_righe(DATI / "live.json", {"letto_il": letto, "n": len(ids)}, "lotti", ids)
    return len(ids)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="nessuna richiesta: rielabora la cache")
    ap.add_argument("--senza-pvp", action="store_true", help="PVP dalla cache (portale fermo), OMI in rete")
    a = ap.parse_args()
    t0 = time.time()
    no_pvp = a.offline or a.senza_pvp
    try:
        ep = None if no_pvp else rete.endpoint_pvp()
    except Exception as e:  # noqa: BLE001
        raise SystemExit(f"PVP non raggiungibile ({e}): dati NON aggiornati, riprovare più tardi.")
    print("1. Elenco aste attive (PVP)")
    try:
        case = scarica_elenco(ep, "case", no_pvp)
        auto = scarica_elenco(ep, "auto", no_pvp)
    except Exception as e:  # noqa: BLE001
        raise SystemExit(f"PVP non raggiungibile ({e}): dati NON aggiornati, riprovare più tardi.")
    if not case:
        raise SystemExit("Nessun lotto letto dal PVP: dati non aggiornati (portale fermo o indirizzi cambiati).")
    letto = (leggi(CACHE / "elenco" / "case.json", {}) or {}).get("letto_il", ADESSO.isoformat(timespec="minutes"))
    print("2-4. Dettagli, superfici e zone OMI")
    lotti, veicoli, omi = elabora(ep, case, auto, no_pvp, a.offline)
    lotti.sort(key=lambda L: (L["comune"], L["data"], L["id"]))
    veicoli.sort(key=lambda v: (v["data"], v["id"]))
    scrivi_righe(DATI / "lotti.json", {"letto_il": letto, "semestre_omi": omi["semestre"], "soglia_citta": SOGLIA_CITTA}, "lotti", lotti)
    scrivi_righe(DATI / "auto.json", {"letto_il": letto}, "veicoli", veicoli)
    scrivi(DATI / "omi.json", omi)
    n = scrivi_live(case, auto, letto, {L["id"] for L in lotti} | {v["id"] for v in veicoli})
    con = sum(1 for L in lotti if "sconto_min" in L)
    print(f"Fatto in {time.time() - t0:.0f} s: {len(lotti)} lotti residenziali ({con} con sconto €/m² sull'OMI), "
          f"{len(veicoli)} veicoli, live.json con {n} lotti.")


if __name__ == "__main__":
    main()
