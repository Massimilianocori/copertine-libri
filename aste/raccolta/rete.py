"""Richieste HTTP gentili verso il PVP e il servizio OMI (GEOPOI) dell'Agenzia delle Entrate.

Regole (vedi NOTE.md):
- firma da browser normale (il firewall del Ministero blocca le firme da script);
- poche richieste in parallelo (al massimo 2) e una pausa tra una richiesta e l'altra;
- nuovi tentativi con attese crescenti (20, 40, 80, 120 s) su errori di rete, 429 e 5xx;
- i dati personali del PVP (voce "soggetti", allegati, titolari di pegno) si scartano appena letti: non arrivano né alla
  cache né ai dati pubblicati.
"""
import json
import random
import re
import threading
import time
from pathlib import Path

import requests

RADICE = Path(__file__).resolve().parent.parent
CACHE = RADICE / "cache"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/129.0.0.0 Safari/537.36")
PVP = "https://pvp.giustizia.it"
GEOPOI = "https://www1.agenziaentrate.gov.it/servizi/geopoi_omi"
PAUSA = {"pvp.giustizia.it": 3.0, "www1.agenziaentrate.gov.it": 1.5}  # secondi minimi tra due richieste allo stesso servizio (PVP: 3 s, come nel test delle fonti)
PAUSA_BASE = 1.2
ATTESE = [20, 40, 80, 120]

_sessione = threading.local()
_ultimo = {}
_lock = threading.Lock()


def sessione():
    s = getattr(_sessione, "s", None)
    if s is None:
        s = requests.Session()
        s.headers.update({"User-Agent": UA, "Accept": "application/json, text/plain, */*",
                          "Accept-Language": "it-IT,it;q=0.9,en;q=0.6"})
        _sessione.s = s
    return s


def _aspetta(host):
    with _lock:
        ora = time.monotonic()
        prossimo = max(ora, _ultimo.get(host, 0) + PAUSA.get(host, PAUSA_BASE) + random.uniform(0, 0.8))
        _ultimo[host] = prossimo
    if prossimo > ora:
        time.sleep(prossimo - ora)


def chiedi(metodo, url, *, json_body=None, testo=False, tentativi=len(ATTESE) + 1, timeout=60):
    """Una richiesta con pausa e nuovi tentativi. Restituisce il JSON (o il testo) oppure solleva l'ultimo errore."""
    host = url.split("/")[2]
    ultimo = None
    for i in range(tentativi):
        _aspetta(host)
        try:
            r = sessione().request(metodo, url, json=json_body, timeout=timeout,
                                   headers={"Content-Type": "application/json"} if json_body is not None else None)
            if r.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(f"HTTP {r.status_code}", response=r)
            r.raise_for_status()
            if testo:
                r.encoding = r.encoding or "utf-8"
                return r.text
            if "blocked" in r.text[:400].lower() and not r.text.lstrip().startswith(("{", "[")):
                raise requests.HTTPError("pagina di blocco del firewall")
            return r.json()
        except (requests.RequestException, ValueError) as e:
            ultimo = e
            stato = getattr(getattr(e, "response", None), "status_code", None)
            if stato in (400, 401, 403, 404):
                raise
            if i < tentativi - 1:
                attesa = ATTESE[min(i, len(ATTESE) - 1)]
                print(f"  ! {url[:90]}… {e}: nuovo tentativo tra {attesa} s", flush=True)
                time.sleep(attesa)
    raise ultimo


# ---------------------------------------------------------------- indirizzi del PVP (cambiano a ogni aggiornamento del portale)
def endpoint_pvp():
    """Legge dalla pagina pubblica gli indirizzi correnti dei servizi JSON (es. ric-496b258c-986a1b71/ric-ms).
    Se la pagina non risponde usa gli ultimi indirizzi buoni salvati in cache/endpoint.json."""
    salvati = CACHE / "endpoint.json"
    try:
        home = chiedi("GET", PVP + "/pvp/it/lista_annunci.page", testo=True)
        bo = re.search(r"(bo-[0-9a-f]{8}-[0-9a-f]{8}/bo-ms)", home).group(1)
        conf = chiedi("GET", f"{PVP}/{bo}/fe-config/lista-annunci")
        ms = conf["msUrl"]
        e = {"ricerca": f"{PVP}/{ms['ricerca']}", "vendite": f"{PVP}/{ms['vendite']}", "backoffice": f"{PVP}/{bo}"}
        CACHE.mkdir(parents=True, exist_ok=True)
        salvati.write_text(json.dumps(e, indent=1), encoding="utf-8")
        return e
    except Exception as err:  # noqa: BLE001
        if salvati.exists():
            print(f"  ! indirizzi PVP non letti ({err}): uso quelli salvati", flush=True)
            return json.loads(salvati.read_text(encoding="utf-8"))
        raise


# ---------------------------------------------------------------- dettaglio di un lotto: solo i campi del bene
CAMPI_VENDITA = ("idVendita", "codTipoVendita", "descTipoVendita", "dataVendita", "oraVendita", "impoOffertaMinima",
                 "impoOffertaAumento", "impoBaseAsta", "codModVendita", "descModVendita", "dataTermPresOff",
                 "oraTermPresOff", "dataDiPubblicazione")
CAMPI_BENE = ("descrizione", "codTipoCategLotto", "codTipologiaBene", "descTipologiaBene", "disponibilita",
              "superficie", "numeroVani", "piano")
CAMPI_IND = ("codComune", "descComune", "codProvincia", "descProvincia", "descRegione", "via", "coordinate")


def _ind(i):
    i = i or {}
    return {k: i.get(k) for k in CAMPI_IND}


def dettaglio_pulito(grezzo):
    """Tiene solo i campi del bene. Scarta 'soggetti' (delegato, custode, giudice: nomi, email, codici fiscali),
    'allegati' e 'allegatoDTO' (PDF), dati della procedura e dei titolari di pegno, dati catastali."""
    b = grezzo.get("body", grezzo) or {}
    lotto = b.get("lotto") or {}
    return {
        **{k: b.get(k) for k in CAMPI_VENDITA},
        "lotto": {"descLotto": lotto.get("descLotto"), "codTipoCategLotto": lotto.get("codTipoCategLotto"),
                  "indirizzo": _ind(lotto.get("indirizzo"))},
        "beni": [{**{k: x.get(k) for k in CAMPI_BENE}, "indirizzo": _ind(x.get("indirizzo"))} for x in (b.get("beni") or [])],
    }
