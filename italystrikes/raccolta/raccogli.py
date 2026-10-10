"""Legge il registro ufficiale degli scioperi del MIT e aggiorna italystrikes/dati/scioperi.json.

Uso (dalla radice del repository):
    python3 italystrikes/raccolta/raccogli.py            # scarica RSS + prospetto HTML
    python3 italystrikes/raccolta/raccogli.py --rss FILE # usa un RSS salvato (prove, primo seme)

Il registro mostra solo gli scioperi in programma: lo storico lo teniamo noi, per id MIT (guid dell'RSS).
Stati: "in programma", "concluso" (data fine passata), "rimosso dal registro" (sparito prima della fine:
probabile revoca, mai presentato come certo), "revocato" (solo se la colonna Note del registro lo dice).
Nessuna dipendenza esterna. Esce con codice 1 se il registro non risponde o cambia formato (nessun dato toccato).
"""
import hashlib
import html
import json
import re
import sys
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
FONTI = DATI / "fonti"
FILE = DATI / "scioperi.json"
STATO = DATI / "registro.json"
URL_RSS = "https://scioperi.mit.gov.it/mit2/public/scioperi/rss"
URL_HTML = "https://scioperi.mit.gov.it/mit2/public/scioperi"
ROMA = ZoneInfo("Europe/Rome")
UA = "Mozilla/5.0 (compatible; italystrikes-reader/1.0; +https://italystrikes.netlify.app/about/)"
CAMPI = ["inizio", "fine", "settore", "rilevanza", "regione", "provincia", "sindacati", "categoria",
         "modalita", "proclamazione", "ricezione", "note"]


def scarica(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def iso(d):
    d = d.strip()
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", d)
    if not m:
        raise ValueError(f"data non riconosciuta: {d!r}")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"


def pulisci(t):
    return re.sub(r"\s+", " ", html.unescape(t or "")).strip()


def leggi_rss(testo):
    agg = re.search(r"aggiornato alla data:\s*(\d{2}/\d{2}/\d{4})", testo)
    voci = {}
    for item in re.findall(r"<item>(.*?)</item>", testo, re.S):
        guid = re.search(r"<guid>[^<]*?/(\d+)\s*</guid>", item)
        titolo = pulisci(re.search(r"<title>(.*?)</title>", item, re.S).group(1))
        desc = re.search(r"<description><!\[CDATA\[(.*?)\]\]></description>", item, re.S).group(1)
        parti = {}
        for riga in re.split(r"<br\s*/?>", desc):
            if ":" in riga:
                k, v = riga.split(":", 1)
                parti[pulisci(k).lower()] = pulisci(v)
        t = dict(re.findall(r"(Data inizio|Settore|Rilevanza|Regione|Provincia):\s*(.*?)(?=\s+-\s+\w[\w ]*:|$)", titolo))
        v = {
            "id": guid.group(1),
            "inizio": iso(t["Data inizio"]),
            "fine": iso(parti["data fine"]),
            "settore": pulisci(parti.get("settore", t.get("Settore", ""))),
            "rilevanza": pulisci(parti.get("rilevanza", t.get("Rilevanza", ""))),
            "regione": pulisci(parti.get("regione", t.get("Regione", ""))),
            "provincia": pulisci(parti.get("provincia", t.get("Provincia", ""))),
            "sindacati": parti.get("sindacati", ""),
            "categoria": parti.get("categoria interessata", ""),
            "modalita": parti.get("modalità", parti.get("modalita", "")),
            "proclamazione": iso(parti["data proclamazione"]),
            "ricezione": parti.get("data ricezione", ""),
            "note": "",
        }
        voci[v["id"]] = v
    return (iso(agg.group(1)) if agg else None), voci


def leggi_html(testo):
    """Righe del prospetto (contiene la colonna Note, assente nell'RSS). Nessun id: si abbina per contenuto."""
    i = testo.find('id="scioperiLarge"')
    if i < 0:
        raise ValueError("tabella scioperiLarge non trovata")
    corpo = re.search(r"<tbody>(.*?)</tbody>", testo[i:], re.S).group(1)
    righe = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", corpo, re.S):
        c = [pulisci(re.sub(r"<[^>]+>", " ", x)) for x in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
        if len(c) < 13:
            continue
        righe.append({"inizio": iso(c[1]), "fine": iso(c[2]), "sindacati": c[3], "settore": c[4], "categoria": c[5],
                      "modalita": c[6], "rilevanza": c[7], "note": c[8], "proclamazione": iso(c[9]),
                      "regione": c[10], "provincia": c[11], "ricezione": c[12]})
    return righe


def chiave(v):
    return tuple(pulisci(v[k]).upper() for k in ("inizio", "fine", "settore", "rilevanza", "regione", "provincia",
                                                  "sindacati", "categoria", "modalita", "proclamazione"))


def main():
    args = sys.argv[1:]
    oggi = datetime.now(ROMA).date()
    if "--rss" in args:
        rss_testo = Path(args[args.index("--rss") + 1]).read_text(encoding="utf-8")
        html_testo = None
    else:
        try:
            rss_testo = scarica(URL_RSS)
            html_testo = scarica(URL_HTML)
        except Exception as e:  # noqa: BLE001
            raise SystemExit(f"ERRORE: registro MIT non raggiungibile ({e}). Nessun dato modificato.")
    try:
        aggiornato, voci = leggi_rss(rss_testo)
        righe = leggi_html(html_testo) if html_testo else []
    except Exception as e:  # noqa: BLE001
        raise SystemExit(f"ERRORE: formato del registro cambiato ({e}). Nessun dato modificato.")
    if not voci:
        raise SystemExit("ERRORE: RSS senza scioperi (registro vuoto o formato cambiato). Nessun dato modificato.")

    # Note dal prospetto HTML
    per_chiave = {}
    for r in righe:
        per_chiave.setdefault(chiave(r), []).append(r)
    senza_html = 0
    for v in voci.values():
        trovate = per_chiave.get(chiave(v))
        if trovate:
            v["note"] = trovate.pop(0)["note"]
        elif righe:
            senza_html += 1
    if righe and len(righe) != len(voci):
        print(f"ATTENZIONE: RSS {len(voci)} scioperi, prospetto HTML {len(righe)} righe.")
    if senza_html:
        print(f"ATTENZIONE: {senza_html} scioperi dell'RSS senza riga corrispondente nel prospetto (note mancanti).")

    archivio = json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else {}
    nuovi, cambiati, rimossi, conclusi = [], [], [], []
    for id_, v in voci.items():
        vecchio = archivio.get(id_)
        stato = "revocato" if re.search(r"\bREVOC", v["note"].upper()) else "in programma"
        if vecchio is None:
            archivio[id_] = {"id": id_, **{k: v[k] for k in CAMPI}, "stato": stato,
                             "visto_prima": oggi.isoformat(), "visto_ultimo": oggi.isoformat(), "modifiche": []}
            nuovi.append(id_)
            continue
        diff = {k: [vecchio.get(k, ""), v[k]] for k in CAMPI if vecchio.get(k, "") != v[k]
                and not (k == "note" and not v[k] and html_testo is None)}
        if diff:
            vecchio["modifiche"].append({"il": oggi.isoformat(), "campi": diff})
            for k, (_, nuovo) in diff.items():
                vecchio[k] = nuovo
            cambiati.append(id_)
        if vecchio["stato"] != stato:
            vecchio["stato"] = stato
            cambiati.append(id_)
        vecchio["visto_ultimo"] = oggi.isoformat()
    for id_, s in archivio.items():
        if id_ in voci or s["stato"] in ("concluso", "rimosso dal registro"):
            continue
        if date.fromisoformat(s["fine"]) < oggi:
            s["stato"] = "concluso"
            conclusi.append(id_)
        elif s["stato"] in ("in programma", "revocato"):
            if s["stato"] == "in programma":
                s["stato"] = "rimosso dal registro"
                s["rimosso_il"] = oggi.isoformat()
                rimossi.append(id_)
    # scioperi ancora nel registro ma con data fine passata: conclusi
    for id_ in voci:
        s = archivio[id_]
        if date.fromisoformat(s["fine"]) < oggi and s["stato"] == "in programma":
            s["stato"] = "concluso"
            conclusi.append(id_)

    ordinato = dict(sorted(archivio.items(), key=lambda kv: (kv[1]["inizio"], int(kv[0]))))
    DATI.mkdir(parents=True, exist_ok=True)
    FILE.write_text(json.dumps(ordinato, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    impronta = hashlib.sha256(json.dumps(voci, sort_keys=True).encode()).hexdigest()[:16]
    stato_prec = json.loads(STATO.read_text(encoding="utf-8")) if STATO.exists() else {}
    STATO.write_text(json.dumps({
        "registro_aggiornato_al": aggiornato or stato_prec.get("registro_aggiornato_al"),
        "letto_il": datetime.now(ROMA).strftime("%Y-%m-%d %H:%M"),
        "scioperi_nel_registro": len(voci), "impronta": impronta,
        "fonte_rss": URL_RSS, "fonte_prospetto": URL_HTML}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # copia dell'RSS solo se il contenuto è cambiato; si tengono 30 giorni
    if html_testo is not None and impronta != stato_prec.get("impronta"):
        FONTI.mkdir(exist_ok=True)
        (FONTI / f"rss-{oggi.isoformat()}.xml").write_text(rss_testo, encoding="utf-8")
    limite = oggi - timedelta(days=30)
    for f in FONTI.glob("rss-*.xml"):
        try:
            if date.fromisoformat(f.stem[4:]) < limite:
                f.unlink()
        except ValueError:
            pass

    print(f"Registro aggiornato al {aggiornato}: {len(voci)} scioperi in programma; archivio {len(ordinato)}.")
    print(f"Nuovi {len(nuovi)}, modificati {len(set(cambiati))}, rimossi dal registro {len(rimossi)}, conclusi {len(conclusi)}.")
    for etichetta, lista in (("NUOVI", nuovi), ("RIMOSSI DAL REGISTRO", rimossi)):
        for id_ in lista:
            s = ordinato[id_]
            print(f"  {etichetta}: {id_} {s['inizio']} {s['settore']} {s['rilevanza']} {s['regione']}/{s['provincia']}")


def maree():
    """Previsione della marea a Venezia (pagina acqua alta): se fallisce non ferma la raccolta degli scioperi."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import maree as m
        m.main()
    except Exception as e:  # noqa: BLE001
        print(f"ATTENZIONE: previsione maree non aggiornata ({e}).")


if __name__ == "__main__":
    main()
    maree()
