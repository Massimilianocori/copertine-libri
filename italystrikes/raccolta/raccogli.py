"""Legge il registro ufficiale degli scioperi del MIT e aggiorna italystrikes/dati/scioperi.json.

Uso (dalla radice del repository):
    python3 italystrikes/raccolta/raccogli.py            # scarica RSS + prospetto HTML
    python3 italystrikes/raccolta/raccogli.py --rss FILE # usa un RSS salvato (prove, primo seme)

Il registro mostra solo gli scioperi in programma: lo storico lo teniamo noi, per id MIT (guid dell'RSS).
Stati: "in programma", "concluso" (data fine passata), "rimosso dal registro" (sparito prima della fine:
probabile revoca, mai presentato come certo), "revocato" (solo se la colonna Note del registro lo dice).
Nessuna dipendenza esterna. Se il registro non risponde si tengono i dati dell'ultima lettura buona; dopo 24 ore
si usa la fonte di riserva (calendario della Commissione di garanzia sciopero, copia onData: raccolta/fonte_cgsse.py),
che aggiunge solo scioperi nuovi del trasporto passeggeri (voci "fonte": "cgsse"). Esce con codice 1 se il registro
cambia formato, o se non risponde da 3 giorni o più e la riserva non è utilizzabile.
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
            # Fonte giù: si tengono i dati dell'ultima lettura buona e si segna da quando manca.
            # Dopo 24 ore si usa la riserva CGSSE. Il workflow fallisce (ed è una email per Massimiliano) solo se il
            # blocco dura da 3 giorni o più e la riserva non è utilizzabile (con la riserva il commit dei dati deve partire).
            stato = json.loads(STATO.read_text(encoding="utf-8")) if STATO.exists() else {}
            adesso = datetime.now(ROMA)
            if not stato.get("fonte_non_raggiungibile_dal"):
                stato["fonte_non_raggiungibile_dal"] = oggi.isoformat()
                stato["primo_tentativo_fallito"] = adesso.strftime("%Y-%m-%d %H:%M")
            dal = stato["fonte_non_raggiungibile_dal"]
            stato["ultimo_tentativo_fallito"] = adesso.strftime("%Y-%m-%d %H:%M")
            stato["ultimo_errore"] = str(e)[:200]
            # stato vecchio senza l'ora del primo errore: si conta dalla fine di quel giorno (mai prima del vero)
            primo = datetime.fromisoformat(stato.get("primo_tentativo_fallito") or f"{dal} 23:59").replace(tzinfo=ROMA)
            ore = (adesso - primo).total_seconds() / 3600
            riserva = riserva_cgsse(oggi) if ore > 24 else None
            if riserva:
                stato["riserva_cgsse"] = riserva
            else:
                stato.pop("riserva_cgsse", None)
                if ore <= 24:
                    print(f"Riserva CGSSE non usata: il registro MIT non risponde da {ore:.0f} ore (servono più di 24).")
            STATO.write_text(json.dumps(stato, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            giorni = (oggi - date.fromisoformat(dal)).days
            msg = f"registro MIT non raggiungibile dal {dal} ({giorni} giorni; {e}). Dati dell'ultima lettura buona mantenuti"
            msg += "; scioperi nuovi dalla riserva CGSSE." if riserva else "."
            if giorni >= 3 and not riserva:
                raise SystemExit("ERRORE: " + msg)
            print("ATTENZIONE: " + msg)
            return
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
        if vecchio is not None:
            vecchio.pop("revoca_cgsse", None)  # sciopero ancora nel registro: vale il suo stato, non la revoca CGSSE
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
        if id_ in voci or s["stato"] in ("concluso", "rimosso dal registro") or s.get("fonte") == "cgsse":
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

    sostituite, da_controllare = ritorno_mit(archivio, oggi)
    ordinato = ordina(archivio)
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
    for c, m, p in sostituite:
        print(f"  VOCE CGSSE SOSTITUITA: {c['id']} -> MIT {m['id']} ({c['inizio']} {c['settore']}, punteggio {p})")
    for c in da_controllare:
        print(f"ATTENZIONE: voce CGSSE senza sciopero MIT corrispondente, da controllare a mano: {c['id']} {c['inizio']} "
              f"{c['settore']} {c['regione']}/{c['provincia']} {c['categoria'][:50]} ({c['stato']}) {c.get('url_dettaglio', '')}")


def ordina(archivio):
    return dict(sorted(archivio.items(), key=lambda kv: (kv[1]["inizio"], not kv[0].isdigit(),
                                                         int(kv[0]) if kv[0].isdigit() else kv[0])))


# ---------------------------------------------------------------- fonte di riserva: calendario CGSSE (copia onData)
# Regole (decise il 27/10/2026, vedi NOTE.md): si usa solo se il registro MIT non risponde da più di 24 ore e se la
# copia onData è confermata recente (ultimo commit del file da meno di 96 ore; se l'API GitHub non risponde, controllo
# prudente sulle date nel file: meno di 48 ore); aggiunge solo scioperi nuovi del trasporto passeggeri con luogo riconosciuto;
# non cambia mai i campi delle voci MIT, salvo lo stato "revocato" se l'abbinamento ha punteggio >= 3,5.
SOGLIA_REVOCA = 3.5
ETA_MAX_ORE = 96  # sull'ultimo commit del file: onData fa un commit solo se il file cambia (giorni senza scioperi nuovi)
ETA_MAX_ORE_FILE = 48  # sulle date nel file, quando l'API GitHub non risponde: limite prudente (sciopero a 29-30 giorni)
URL_COMMIT_CGSSE = ("https://api.github.com/repos/ondata/liberiamoli-tutti/commits"
                    "?path=scioperi/data/cgsse/cgsse_data.jsonl&sha=main&per_page=1")
SETTORI_PASSEGGERI = {"Ferroviario", "Trasporto pubblico locale", "Aereo", "Marittimo", "Generale", "Plurisettoriale"}
PARTI_PASSEGGERI = {"TRASPORTO PUBBLICO LOCALE", "TRASPORTO AEREO", "TRASPORTO FERROVIARIO", "APPALTI FERROVIARI",
                    "TRASPORTO MARITTIMO", "PLURISETTORIALE TRASPORTI"}


def cgsse():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import fonte_cgsse
    return fonte_cgsse


def eta_copia_cgsse(righe, adesso):
    """Ore dall'ultimo aggiornamento della copia onData, come lo si sa e limite in ore da applicare. Prima la data
    dell'ultimo commit del file (API GitHub, limite ETA_MAX_ORE); se l'API non risponde, CGSSE_AGGIORNATA_IL (data ISO
    del commit, per le prove a mano da un server da cui l'API è chiusa; stesso limite); altrimenti la data più recente
    nel file: la copia arriva a 30 giorni dal giorno in cui è fatta, quindi la sua età è al massimo (giorni mancanti
    a oggi + 30, più il giorno in corso); limite ETA_MAX_ORE_FILE, cioè serve uno sciopero a 29-30 giorni da oggi
    (in caso di dubbio non si usa)."""
    import os
    try:
        req = urllib.request.Request(URL_COMMIT_CGSSE, headers={"User-Agent": UA, "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            quando = json.loads(r.read())[0]["commit"]["committer"]["date"]
        come = "ultimo commit del file (API GitHub)"
    except Exception as e:  # noqa: BLE001
        quando = os.environ.get("CGSSE_AGGIORNATA_IL")
        come = f"CGSSE_AGGIORNATA_IL (API GitHub non raggiungibile: {str(e)[:80]})"
    if quando:
        t = datetime.fromisoformat(quando.replace("Z", "+00:00"))
        t = t if t.tzinfo else t.replace(tzinfo=ROMA)
        return (adesso - t).total_seconds() / 3600, come, t.astimezone(ROMA).strftime("%Y-%m-%d %H:%M"), ETA_MAX_ORE
    ultima = max((r.get("data_al_iso") or r.get("data_iso") or "") for r in righe)
    if not ultima:
        return 9999, "nessuna data nel file", "", ETA_MAX_ORE_FILE
    giorni = (adesso.date() + timedelta(days=30) - date.fromisoformat(ultima)).days
    return ((max(giorni, 0) + 1) * 24, f"data più recente nel file ({ultima}; API GitHub non raggiungibile)", "",
            ETA_MAX_ORE_FILE)


def passeggeri(v, fc):
    """Trasporto passeggeri: treni, trasporto locale, aereo e marittimo passeggeri, generali che toccano i trasporti."""
    if v["settore"] not in SETTORI_PASSEGGERI:
        return False
    testo = (v["categoria"] + " " + v["modalita"]).upper()
    if v["settore"] in ("Aereo", "Marittimo") and re.search(r"CARGO|\bMERCI\b|PORTUAL|RIMORCHI", testo):
        return False
    if v["settore"] == "Generale" and re.search(r"ESCLUS\w*\b.*TRASPORT", testo):
        return False
    if v["settore"] == "Plurisettoriale":
        return bool(PARTI_PASSEGGERI & {fc.norma(p) for p in v["settore_cgsse"].split(",")})
    return True


def riserva_cgsse(oggi):
    """Scioperi nuovi e revoche dalla copia onData del calendario CGSSE. Restituisce il riassunto per registro.json,
    oppure None se la copia non è utilizzabile (nessun dato toccato)."""
    adesso = datetime.now(ROMA)
    try:
        fc = cgsse()
        righe = fc.leggi_jsonl(fc.scarica(fc.URL_COPIA))
        if not righe:
            raise ValueError("copia vuota")
        ore, come, aggiornata, limite = eta_copia_cgsse(righe, adesso)
    except Exception as e:  # noqa: BLE001
        print(f"ATTENZIONE: riserva CGSSE non utilizzabile ({str(e)[:200]}).")
        return None
    if ore > limite:
        print(f"ATTENZIONE: riserva CGSSE non usata: la copia onData potrebbe avere fino a {ore:.0f} ore, non è confermata "
              f"sotto le {limite} ({come}).")
        return None
    voci = [v for k, r in fc.unisci(righe).items() if (v := fc.voce(k, r, oggi.isoformat()))]
    archivio = json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else {}
    mit = {k: s for k, s in archivio.items() if s.get("fonte") != "cgsse"}
    coppie, sole, _ = fc.confronta(voci, mit, oggi.isoformat())
    nuovi, aggiornati, revoche = [], [], []
    for v, s, p in coppie:  # stesso sciopero già nel registro MIT: conta solo una revoca
        if v["stato"] != "revocato" or s["stato"] == "revocato":
            continue
        if p >= SOGLIA_REVOCA:
            archivio[s["id"]]["modifiche"].append({"il": oggi.isoformat(), "campi": {"stato": [s["stato"], "revocato"]},
                                                   "fonte": "cgsse", "url": v["url_dettaglio"]})
            archivio[s["id"]].update(stato="revocato", revoca_cgsse=v["url_dettaglio"])
            revoche.append((s, v, p))
        else:
            print(f"ATTENZIONE: revoca CGSSE {v['id']} abbinata a MIT {s['id']} con punteggio {p} (< {SOGLIA_REVOCA}): "
                  f"stato MIT non cambiato, controllare {v['url_dettaglio']}")
    for v in sole:
        vecchia = archivio.get(v["id"])
        if vecchia is not None:  # voce CGSSE di una lettura precedente: si aggiorna dalla copia nuova
            diff = {k: [vecchia.get(k, ""), v[k]] for k in CAMPI + ["stato"] if vecchia.get(k, "") != v[k]}
            if diff:
                vecchia["modifiche"].append({"il": oggi.isoformat(), "campi": diff})
                vecchia.update({k: n for k, (_, n) in diff.items()})
                aggiornati.append(v["id"])
            vecchia["visto_ultimo"] = oggi.isoformat()
        elif v["stato"] == "revocato":  # revoca di uno sciopero che non abbiamo: niente da aggiungere
            simili = sorted(((fc.somiglia(v, s), s["id"]) for s in mit.values()), reverse=True)
            if simili and simili[0][0] > 0:
                print(f"ATTENZIONE: revoca CGSSE {v['id']} ({v['inizio']} {v['settore']}) somiglia a MIT {simili[0][1]} "
                      f"(punteggio {round(simili[0][0], 2)} < {SOGLIA_REVOCA}): stato MIT non cambiato, controllare {v['url_dettaglio']}")
        elif passeggeri(v, fc) and not fc.luogo(v["ambito_cgsse"], v["settore_cgsse"])[3]:
            archivio[v["id"]] = v
            nuovi.append(v)
    for s in archivio.values():
        if s.get("fonte") == "cgsse" and s["fine"] < oggi.isoformat() and s["stato"] == "in programma":
            s["stato"] = "concluso"
    FILE.write_text(json.dumps(ordina(archivio), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Riserva CGSSE (copia onData del {aggiornata or '?'}, {ore:.0f} ore; {come}): {len(righe)} righe, "
          f"{len(coppie)} scioperi già nel registro MIT; nuovi {len(nuovi)}, aggiornati {len(aggiornati)}, revoche {len(revoche)}.")
    for v in nuovi:
        print(f"  NUOVO DA CGSSE: {v['id']} {v['inizio']} {v['settore']} {v['rilevanza']} {v['regione']}/{v['provincia']} "
              f"{v['categoria'][:50]} {v['url_dettaglio']}")
    for s, v, p in revoche:
        print(f"  REVOCATO (CGSSE): MIT {s['id']} {s['inizio']} {s['settore']} {s['categoria'][:50]} = {v['id']} "
              f"(punteggio {p}) {v['url_dettaglio']}")
    return {"usata_il": adesso.strftime("%Y-%m-%d %H:%M"), "copia_aggiornata_il": aggiornata, "controllo_eta": come,
            "fonte": fc.URL_COPIA, "nuovi": len(nuovi), "revoche": len(revoche)}


def ritorno_mit(archivio, oggi):
    """Registro MIT di nuovo leggibile: le voci MIT sostituiscono le voci CGSSE abbinate; le altre restano."""
    voci_cg = [s for s in archivio.values() if s.get("fonte") == "cgsse"]
    if not voci_cg:
        return [], []
    fc = cgsse()
    mit = {k: s for k, s in archivio.items() if s.get("fonte") != "cgsse"}
    coppie, sole, _ = fc.confronta(voci_cg, mit, "0000-00-00")
    for c, _, _ in coppie:
        del archivio[c["id"]]
    for c in sole:
        if c["fine"] < oggi.isoformat() and c["stato"] == "in programma":
            c["stato"] = "concluso"
    return coppie, [c for c in sole if c["stato"] != "concluso"]


def maree():
    """Previsione della marea a Venezia (pagina acqua alta): se fallisce non ferma la raccolta degli scioperi."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import maree as m
        m.main()
    except Exception as e:  # noqa: BLE001
        print(f"ATTENZIONE: previsione maree non aggiornata ({e}).")


def cambi_bce():
    """Cambi BCE per il sito Visa Income Checker (visaincome/): il workflow salva solo italystrikes/dati, quindi
    la copia viva sta qui (italystrikes/dati/cambi-bce.json). Se fallisce non ferma la raccolta degli scioperi."""
    import os
    import subprocess
    script = Path(__file__).resolve().parent.parent.parent / "visaincome" / "raccolta" / "cambi.py"
    if not script.exists():
        return
    env = dict(os.environ, CAMBI_FILE=str(Path(__file__).resolve().parent.parent / "dati" / "cambi-bce.json"))
    r = subprocess.run([sys.executable, str(script)], env=env, capture_output=True, text=True)
    print((r.stdout or r.stderr).strip() or "Cambi BCE: nessun messaggio")


if __name__ == "__main__":
    main()
    maree()
    cambi_bce()
