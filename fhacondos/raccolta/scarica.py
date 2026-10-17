"""Scarica dal modulo HUD "FHA Condominium Lookup" gli elenchi dei condomini in fhacondos/cache/ (fuori da git).

Uso (dalla radice del repository):
    python3 fhacondos/raccolta/scarica.py                       # scarico completo (circa 15-25 minuti)
    python3 fhacondos/raccolta/scarica.py --stati VA,FL,CO --tipi A   # solo alcuni Stati / tipi (test)
    python3 fhacondos/raccolta/scarica.py --edizione 2026-10-17 # riprende un'edizione già iniziata

Fonte: https://entp.hud.gov/idapp/html/condlook.cfm (modulo ColdFusion). Funzionamento verificato il 17/10/2026:
  1. GET di condlook.cfm: il server dà i cookie di sessione (CFID, CFTOKEN, cookie_entp).
  2. POST a condo1.cfm con i campi del modulo e la pagina di provenienza (Referer): prima pagina, 25 righe.
     Il testo "(N records were selected, records 1 through 25 displayed)" dà il totale della ricerca.
  3. Pagine successive: POST a condo1.cfm con gli stessi campi in maiuscolo + startAt=26, 51, ... (modulo "getMoreData"
     della pagina). maxRows non cambia la dimensione della pagina: sono sempre 25 righe.
Ricerche fatte per ogni Stato o territorio (54 voci del menu):
  - A = approvati, tipo di ricerca "Project" (una riga per condominio, senza le fasi/"submission");
  - E = scaduti con data di scadenza negli ultimi MESI_RECENTI mesi;
  - W = ritirati con data dello stato negli ultimi MESI_RECENTI mesi.
Ritmo: una richiesta ogni 1,2-2 secondi, una sola alla volta. Ogni pagina è salvata in
cache/<edizione>/<tipo>/<ST>/p<startAt>.html; se esiste già non si riscarica (ripresa automatica).
Alla fine di ogni ricerca si scrive <ST>.json con il totale dichiarato dal modulo e le pagine scaricate.
"""
import argparse
import json
import random
import re
import sys
import time
from datetime import date
from pathlib import Path

import requests

RADICE = Path(__file__).resolve().parent.parent
CACHE = RADICE / "cache"
BASE = "https://entp.hud.gov/idapp/html/"
MODULO = BASE + "condlook.cfm"
RISULTATI = BASE + "condo1.cfm"
UA = "Mozilla/5.0 (X11; Linux x86_64) fha-condo-list-weekly-refresh/1.0"
MESI_RECENTI = 24
PAUSA = (1.2, 2.0)

STATI = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
    "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "GU": "Guam",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky",
    "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
    "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "PR": "Puerto Rico", "RI": "Rhode Island",
    "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VI": "Virgin Islands", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}

RE_TOTALE = re.compile(r"\((\d+) records? (?:were|was) selected")
RE_POCHI = re.compile(r"\((\d+) records? displayed")
NESSUN_RISULTATO = "NO RECORDS MATCH YOUR SELECTION CRITERIA"  # risposta del modulo quando la ricerca non trova nulla


class Sessione:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": UA})
        self.ultimo = 0.0
        self.richieste = 0
        self.apri()

    def pausa(self):
        attesa = random.uniform(*PAUSA) - (time.time() - self.ultimo)
        if attesa > 0:
            time.sleep(attesa)
        self.ultimo = time.time()

    def apri(self):
        self.pausa()
        r = self.s.get(MODULO, timeout=60)
        r.raise_for_status()
        self.richieste += 1

    def post(self, dati, referer, tentativi=5):
        for i in range(tentativi):
            self.pausa()
            try:
                r = self.s.post(RISULTATI, data=dati, headers={"Referer": referer}, timeout=90)
                self.richieste += 1
                testo = r.content.decode("latin-1")
                if r.status_code == 200 and ("records were selected" in testo or "records displayed" in testo
                                             or "record was selected" in testo or "record displayed" in testo
                                             or NESSUN_RISULTATO in testo):
                    return testo
                motivo = f"HTTP {r.status_code}"
            except requests.RequestException as e:
                motivo = str(e)[:120]
            print(f"    tentativo {i + 1} fallito ({motivo}), nuova sessione", flush=True)
            time.sleep(5 * (i + 1))
            try:
                self.s.cookies.clear()
                self.apri()
            except requests.RequestException:
                pass
        raise RuntimeError("il modulo HUD non risponde: riprovare più tardi (lo scarico riprende da dove era rimasto)")


def campi_ricerca(stato, tipo, oggi, condo_id=""):
    """Campi della prima ricerca (come il modulo condlook.cfm)."""
    d = {"fapproval_method": "NEW", "fsorted_by": "condo_id", "fstate": stato, "fcounty": "", "fcondo_id": condo_id,
         "fcondo_name": "", "fcity": "", "fzip": "", "fstatus_code": tipo, "fsearch_type": "P",
         "fbegin_mo": "", "fbegin_dy": "", "fbegin_yr": "", "fend_mo": "", "fend_dy": "", "fend_yr": "",
         "came_from": "oth", "in_fhac": "true"}
    if tipo in ("E", "W"):
        inizio = sottrai_mesi(oggi, MESI_RECENTI)
        d.update({"fbegin_mo": f"{inizio.month:02d}", "fbegin_dy": f"{inizio.day:02d}", "fbegin_yr": str(inizio.year),
                  "fend_mo": f"{oggi.month:02d}", "fend_dy": f"{oggi.day:02d}", "fend_yr": str(oggi.year)})
    return d


def campi_pagina(prima, start):
    """Campi del modulo "getMoreData" (stessi valori, nomi in maiuscolo) per la pagina che inizia da start."""
    d = {k.upper(): v for k, v in prima.items()}
    d.update({"startAt": str(start), "maxRows": str(start + 24), "pageIn": MODULO, "thisPage": "condo1.cfm"})
    return d


def sottrai_mesi(d, mesi):
    a, m = d.year, d.month - mesi
    while m <= 0:
        m += 12
        a -= 1
    giorno = min(d.day, 28)
    return date(a, m, giorno)


def totale_dichiarato(testo):
    if NESSUN_RISULTATO in testo:
        return 0
    m = RE_TOTALE.search(testo)
    if m:
        return int(m.group(1))
    m = RE_POCHI.search(testo)
    if m:
        return int(m.group(1))
    return 0


def scarica_ricerca(sess, cartella, stato, tipo, oggi):
    dest = cartella / tipo / stato
    riepilogo = cartella / tipo / f"{stato}.json"
    if riepilogo.exists():
        return json.loads(riepilogo.read_text())
    dest.mkdir(parents=True, exist_ok=True)
    prima = campi_ricerca(stato, tipo, oggi)
    p1 = dest / "p00001.html"
    if p1.exists():
        testo = p1.read_text(encoding="latin-1")
    else:
        testo = sess.post(prima, MODULO)
        p1.write_text(testo, encoding="latin-1")
    totale = totale_dichiarato(testo)
    pagine = [p1.name]
    for start in range(26, totale + 1, 25):
        f = dest / f"p{start:05d}.html"
        if not f.exists():
            t = sess.post(campi_pagina(prima, start), RISULTATI)
            atteso = f"records {start} through"
            if atteso not in t:
                raise RuntimeError(f"{stato} {tipo}: la pagina {start} non è quella attesa")
            f.write_text(t, encoding="latin-1")
        pagine.append(f.name)
    info = {"stato": stato, "tipo": tipo, "totale_dichiarato": totale, "pagine": pagine, "data_ricerca": oggi.isoformat()}
    riepilogo.write_text(json.dumps(info, indent=1))
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stati", default="", help="sigle separate da virgola (vuoto = tutti)")
    ap.add_argument("--tipi", default="A,E,W", help="A approvati, E scaduti recenti, W ritirati recenti")
    ap.add_argument("--edizione", default=date.today().isoformat(), help="cartella della cache (data AAAA-MM-GG)")
    a = ap.parse_args()
    stati = [s.strip().upper() for s in a.stati.split(",") if s.strip()] or list(STATI)
    tipi = [t.strip().upper() for t in a.tipi.split(",") if t.strip()]
    oggi = date.fromisoformat(a.edizione)
    cartella = CACHE / a.edizione
    cartella.mkdir(parents=True, exist_ok=True)
    sess = Sessione()
    inizio = time.time()
    for tipo in tipi:
        for st in stati:
            info = scarica_ricerca(sess, cartella, st, tipo, oggi)
            print(f"{tipo} {st}: {info['totale_dichiarato']} righe dichiarate, {len(info['pagine'])} pagine "
                  f"({sess.richieste} richieste, {int(time.time() - inizio)} s)", flush=True)
    if set(stati) == set(STATI) and {"A", "E", "W"} <= set(tipi):
        (cartella / "completo.json").write_text(json.dumps({"stati": stati, "tipi": tipi, "fine": time.strftime("%Y-%m-%d %H:%M:%S")}))
    print(f"Fatto: {sess.richieste} richieste in {int(time.time() - inizio)} s. Cache: {cartella}")


if __name__ == "__main__":
    sys.exit(main())
