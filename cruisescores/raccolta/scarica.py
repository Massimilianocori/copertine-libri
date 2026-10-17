"""Scarica dal CDC (Vessel Sanitation Program) i dati grezzi di Cruise Ship Health Scores in cruisescores/cache/ (fuori da git).

Uso (dalla radice del repository):
    python3 cruisescores/raccolta/scarica.py             # aggiornamento: Green Sheet + navi cambiate + rapporti mancanti
    python3 cruisescores/raccolta/scarica.py --tutto     # riscarica la storia di tutte le navi (i rapporti già in cache restano)
    python3 cruisescores/raccolta/scarica.py --controllo # solo Green Sheet e modulo: dice se il CDC ha cambiato qualcosa

Fonte: strumento del CDC https://wwwn.cdc.gov/InspectionQueryTool/ (ASP.NET con sessione).
  1. InspectionGreenSheetRpt.aspx  -> ultimo voto di ogni nave "attiva" (nome, data, voto, link al rapporto).
  2. InspectionSearch.aspx         -> elenco delle navi e delle compagnie del modulo (GET) e, per ogni nave,
                                      la ricerca "All Dates" (POST con __VIEWSTATE): tutte le ispezioni con compagnia, data, voto.
  3. InspectionDetailReport.aspx?ColI=...  -> infrazioni per esteso (servono i cookie di sessione: senza, il CDC rimanda al modulo).
     InspectionSummaryReport.aspx         -> punti tolti per voce, del rapporto aperto subito prima nella stessa sessione.

Regole: una richiesta ogni 1-2 secondi (PAUSA), un solo collegamento alla volta, cache su disco e ripresa: un file già
scaricato non si riscarica (scrittura atomica: o c'è intero o non c'è). I rapporti scaricati sono quelli delle ultime
N_RAPPORTI ispezioni di ogni nave pubblicata (vedi navi_da_pubblicare in comune.py).
"""
import html
import random
import re
import sys
import time
from datetime import date
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune as C  # noqa: E402

PAUSA = (1.0, 2.0)  # secondi tra una richiesta e l'altra
BASE = "https://wwwn.cdc.gov/InspectionQueryTool/"
UA = "Mozilla/5.0 (compatible; cruise-health-scores data refresh; weekly, 1 request every 1-2 s)"

S = requests.Session()
S.headers["User-Agent"] = UA
_ultima = [0.0]
CONTO = {"richieste": 0, "errori": 0}


def attendi():
    pausa = random.uniform(*PAUSA)
    trascorso = time.time() - _ultima[0]
    if trascorso < pausa:
        time.sleep(pausa - trascorso)
    _ultima[0] = time.time()


def richiesta(metodo, url, **kw):
    for i in range(5):
        attendi()
        CONTO["richieste"] += 1
        try:
            r = S.request(metodo, url, timeout=120, **kw)
            if r.status_code == 200:
                # Lo strumento del CDC dichiara iso-8859-1 e i dati sono davvero in codifica Windows (° = 0xB0, ’ = 0x92);
                # solo la cornice del sito ha pezzi in UTF-8 (menu delle lingue), che non usiamo. Le pagine www.cdc.gov sono UTF-8.
                r.encoding = "cp1252" if "wwwn.cdc.gov/InspectionQueryTool" in url else "utf-8"
                return r
            print(f"  HTTP {r.status_code} su {url} (tentativo {i + 1})")
        except requests.RequestException as e:
            print(f"  errore di rete su {url}: {e} (tentativo {i + 1})")
        CONTO["errori"] += 1
        time.sleep(5 * (i + 1))
    raise SystemExit(f"Impossibile scaricare {url} dopo 5 tentativi: fermo qui (al prossimo avvio riprende dalla cache).")


def scrivi(percorso, testo):
    percorso.parent.mkdir(parents=True, exist_ok=True)
    tmp = percorso.with_suffix(percorso.suffix + ".tmp")
    tmp.write_text(testo, encoding="utf-8")
    tmp.replace(percorso)


def campi_nascosti(t):
    return {n: html.unescape(v) for n, v in re.findall(r'<input type="hidden" name="(__[A-Z]+)" id="[^"]+" value="([^"]*)"', t)}


_modulo = {}


def apri_modulo():
    """GET del modulo: nuova sessione (cookie) e campi nascosti ASP.NET da rimandare nei POST."""
    r = richiesta("GET", BASE + "InspectionSearch.aspx")
    if "lbox_RegisteredName" not in r.text:
        raise SystemExit("Il modulo del CDC è cambiato (manca l'elenco delle navi): controllare a mano prima di continuare.")
    _modulo.clear()
    _modulo.update(campi_nascosti(r.text))
    return r.text


def cerca_nave(id_nave):
    d = dict(_modulo)
    d.update({
        "ctl00$ContentPlaceHolder1$rb_Cruiseline_Vessel": "rb_Vessel",
        "ctl00$ContentPlaceHolder1$lbox_RegisteredName": str(id_nave),
        "ctl00$ContentPlaceHolder1$rb_InspectionDateCriteria": "rb_AllDate",
        "ctl00$ContentPlaceHolder1$rb_InspectionScoreCriteria": "rb_InspectionScoreAll",
        "ctl00$ContentPlaceHolder1$txtFromSearchDate": "",
        "ctl00$ContentPlaceHolder1$txtToSearchDate": "",
        "ctl00$ContentPlaceHolder1$cmdSearch": "Search",
    })
    for tentativo in range(2):
        r = richiesta("POST", BASE + "InspectionSearch.aspx", data=d)
        if "InspectionResults.aspx" in r.url or "dgMasterList" in r.text:
            if "dgMasterList$ctl01$ctl01" in r.text:
                raise SystemExit(f"La nave {id_nave} ha più di 100 ispezioni (più pagine di risultati): gestire la paginazione.")
            return r.text
        if "No records found" in r.text or "no record" in r.text.lower():
            return r.text
        apri_modulo()  # sessione o __VIEWSTATE scaduti: si riapre il modulo e si riprova
        d.update(_modulo)
    raise SystemExit(f"Ricerca della nave {id_nave}: risposta inattesa dal CDC.")


def scarica_rapporto(coli, id_isp):
    """Rapporto completo + riepilogo dei punti, nella stessa sessione e uno dopo l'altro."""
    det_f = C.CACHE / "rapporti" / f"{id_isp}.detail.html"
    sum_f = C.CACHE / "rapporti" / f"{id_isp}.summary.html"
    if det_f.exists() and sum_f.exists():
        return False
    for tentativo in range(3):
        r = richiesta("GET", BASE + "InspectionDetailReport.aspx?ColI=" + coli)
        if "Inspection Detail Report" not in r.text:
            apri_modulo()
            continue
        r2 = richiesta("GET", BASE + "InspectionSummaryReport.aspx")
        if "Inspection Summary Report" not in r2.text:
            apri_modulo()
            continue
        t1 = C.testo_semplice(r.text)
        t2 = C.testo_semplice(r2.text)
        testa = lambda t: re.search(r"Cruise Ship:\|(.*?)\|Cruise Line:\|(.*?)\|Inspection Date:\|(.*?)\|Inspection Score:\|(\d+)", t)
        a, b = testa(t1), testa(t2)
        if not a or not b or a.groups() != b.groups():
            print(f"  rapporto {id_isp}: il riepilogo non corrisponde al rapporto, riprovo")
            apri_modulo()
            continue
        scrivi(det_f, r.text)
        scrivi(sum_f, r2.text)
        return True
    print(f"  ATTENZIONE: rapporto {id_isp} non scaricato (riprovare al prossimo avvio)")
    CONTO["errori"] += 1
    return False


PAGINE_INFO = {  # pagine informative del CDC citate nel sito (soglia, frequenza, aree) e tabelle delle epidemie
    "faq": "https://www.cdc.gov/vessel-sanitation/faq/index.html",
    "otto-aree": "https://www.cdc.gov/vessel-sanitation/communication-resources/operational-inspections.html",
    "ispezioni": "https://www.cdc.gov/vessel-sanitation/php/our-role/public-health-inspections.html",
    "epidemie": "https://www.cdc.gov/vessel-sanitation/cruise-ship-outbreaks/index.html",
    "epidemie-2025-2024": "https://www.cdc.gov/vessel-sanitation/cruise-ship-outbreaks/earlier-outbreaks.html",
    "epidemie-2023": "https://www.cdc.gov/vessel-sanitation/cruise-ship-outbreaks/earlier-outbreaks-2023.html",
}


def scarica_info():
    """Le pagine www.cdc.gov rispondono 403 (Akamai) a requests ma non a curl: si usa curl, con la stessa pausa.
    Se una pagina non arriva si tiene la copia vecchia in cache e si avvisa (non blocca l'aggiornamento dei voti)."""
    import subprocess
    for nome, url in PAGINE_INFO.items():
        attendi()
        CONTO["richieste"] += 1
        r = subprocess.run(["curl", "-sS", "-L", "--max-time", "90", "-w", "\n%{http_code}", url], capture_output=True)
        corpo, _, codice = r.stdout.decode("utf-8", errors="replace").rpartition("\n")
        if codice.strip() == "200" and len(corpo) > 5000:
            scrivi(C.CACHE / "info" / f"{nome}.html", corpo)
        else:
            CONTO["errori"] += 1
            print(f"   ATTENZIONE: {url} -> HTTP {codice.strip() or '?'} (resta la copia in cache, se c'è)")
    if not (C.CACHE / "info" / "faq.html").exists():
        print("   ATTENZIONE: FAQ del CDC mai scaricata: estrai.py si fermerà finché non arriva.")
        return
    faq = (C.CACHE / "info" / "faq.html").read_text(encoding="utf-8")
    if "85 or below" not in faq or "two unannounced inspections" not in faq:
        print("   ATTENZIONE: la FAQ del CDC non dice più '85 or below' o 'two unannounced inspections': rileggere la guida del sito.")


def main():
    tutto = "--tutto" in sys.argv
    oggi = date.today().isoformat()
    print("1/4 Green Sheet")
    g = richiesta("GET", BASE + "InspectionGreenSheetRpt.aspx").text
    verdi = C.leggi_green_sheet(g)
    if len(verdi) < 100 or "85 or lower are NOT satisfactory" not in g:
        raise SystemExit(f"Il Green Sheet è cambiato ({len(verdi)} navi, soglia non trovata): controllare a mano.")
    scrivi(C.CACHE / "greensheet.html", g)
    print(f"   {len(verdi)} navi nel Green Sheet")

    print("2/4 Modulo di ricerca (elenco navi e compagnie)")
    t = apri_modulo()
    navi, compagnie = C.leggi_elenchi(t)
    scrivi(C.CACHE / "search.html", t)
    print(f"   {len(navi)} navi e {len(compagnie)} compagnie nel modulo")
    print("   pagine informative e epidemie (www.cdc.gov)")
    scarica_info()
    if "--controllo" in sys.argv:
        print(f"Controllo concluso: {CONTO['richieste']} richieste. Il CDC risponde come previsto.")
        return

    print("3/4 Storia delle ispezioni di ogni nave")
    ultime_verdi = {v["id_isp"]: v for v in verdi}
    fatte = 0
    for i, (id_nave, nome) in enumerate(sorted(navi.items(), key=lambda kv: kv[1].lower())):
        f = C.CACHE / "navi" / f"{id_nave}.html"
        if f.exists() and not tutto:
            storia = C.leggi_storia(f.read_text(encoding="utf-8"))
            # si riscarica solo se il Green Sheet ha un'ispezione di questa nave che la cache non ha ancora
            ids = {x["id_isp"] for x in storia}
            nomi = {x["nave"] for x in storia}
            if not any(v["id_isp"] not in ids and v["nave_n"] in {C.norm(n) for n in nomi | {nome}} for v in verdi):
                continue
        testo = cerca_nave(id_nave)
        scrivi(f, testo)
        fatte += 1
        if fatte % 20 == 0:
            print(f"   {fatte} navi scaricate ({i + 1}/{len(navi)})")
    print(f"   storie scaricate ora: {fatte}")

    print("4/4 Rapporti delle ultime ispezioni")
    storie = {}
    for id_nave in navi:
        f = C.CACHE / "navi" / f"{id_nave}.html"
        if f.exists():
            storie[id_nave] = C.leggi_storia(f.read_text(encoding="utf-8"))
    scelte = C.navi_da_pubblicare(navi, storie, verdi)
    da_fare = []
    for id_nave in scelte:
        for x in storie[id_nave][:C.N_RAPPORTI]:
            da_fare.append((x["coli"], x["id_isp"]))
    nuovi = 0
    for j, (coli, id_isp) in enumerate(da_fare):
        if scarica_rapporto(coli, id_isp):
            nuovi += 1
            if nuovi % 25 == 0:
                print(f"   {nuovi} rapporti nuovi ({j + 1}/{len(da_fare)})")
    mancanti = [i for _, i in da_fare if not (C.CACHE / "rapporti" / f"{i}.summary.html").exists()]
    scrivi(C.CACHE / "scaricato_il.txt", oggi + "\n")
    print(f"Fatto: {CONTO['richieste']} richieste, {CONTO['errori']} errori/riprove; rapporti nuovi {nuovi}, "
          f"richiesti {len(da_fare)}, mancanti {len(mancanti)}{': ' + ', '.join(map(str, mancanti[:20])) if mancanti else ''}.")
    if mancanti:
        sys.exit(2)


if __name__ == "__main__":
    main()
