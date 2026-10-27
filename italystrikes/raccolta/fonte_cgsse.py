"""Fonte di riserva per gli scioperi: il calendario della Commissione di garanzia sciopero
(www.cgsse.it/calendario-scioperi). La usa raccogli.py (riserva_cgsse, ritorno_mit) quando il registro MIT non risponde
da più di 24 ore: regole in NOTE.md, sezione 27/10/2026. Lanciato da solo serve per i confronti e non scrive in dati/.

Il sito cgsse.it non risponde dal nostro server né da GitHub Actions (blocca gli indirizzi non italiani).
Il calendario è copiato ogni giorno, senza modifiche di contenuto, dall'associazione onData
(github.com/ondata/liberiamoli-tutti, cartella scioperi/, licenza CC BY 4.0, uscita italiana via Tor):
questo lettore legge quella copia e produce voci nello stesso formato di dati/scioperi.json.
Ogni voce porta il link alla scheda ufficiale CGSSE (campo "url_dettaglio").

Limiti della copia (da sapere prima di usarla):
- finestra: dal 1/1/2025 a oggi + 30 giorni (gli scioperi oltre 30 giorni compaiono solo dopo);
- nessuna data di proclamazione, nessuna regione/provincia separate (solo "ambito geografico" in testo);
- la copia è cumulativa: una revoca o una correzione aggiunge una seconda riga con lo stesso link.
  Regola: revocato se una qualsiasi riga lo dice; per gli altri campi vale la riga più nuova se si passa
  --precedente (la copia del giorno prima), altrimenti l'ultima nel file.

Uso (dalla radice del repository; NON scrive in dati/):
    python3 italystrikes/raccolta/fonte_cgsse.py                        # scarica la copia onData
    python3 italystrikes/raccolta/fonte_cgsse.py --file COPIA.jsonl     # usa una copia salvata
        [--precedente COPIA_PRIMA.jsonl] [--dal 2026-10-23] [--out VOCI.json]
        [--confronta italystrikes/dati/scioperi.json]
"""
import json
import re
import sys
import unicodedata
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

URL_COPIA = "https://raw.githubusercontent.com/ondata/liberiamoli-tutti/main/scioperi/data/cgsse/cgsse_data.jsonl"
URL_UFFICIALE = "https://www.cgsse.it/calendario-scioperi"
ROMA = ZoneInfo("Europe/Rome")
UA = "Mozilla/5.0 (compatible; italystrikes-reader/1.0; +https://italy-strikes-today.netlify.app/about/)"
CAMPI = ["inizio", "fine", "settore", "rilevanza", "regione", "provincia", "sindacati", "categoria",
         "modalita", "proclamazione", "ricezione", "note"]

# settore CGSSE (una parte dell'elenco separato da virgole) -> settore del registro MIT
SETTORI_TRASPORTO = {
    "TRASPORTO PUBBLICO LOCALE": "Trasporto pubblico locale",
    "TRASPORTO AEREO": "Aereo",
    "TRASPORTO FERROVIARIO": "Ferroviario",
    "APPALTI FERROVIARI": "Ferroviario",
    "TRASPORTO MARITTIMO": "Marittimo",
    "TRASPORTO MERCI SU ROTAIA": "Trasporto merci",
    "TRASPORTO MERCI SU GOMMA": "Trasporto merci",
    "CIRCOLAZIONE E SICUREZZA STRADALE": "Circolazione e sicurezza stradale",
    "TAXI": "Taxi",
    "NOLEGGIO CON CONDUCENTE": "Taxi",
    "PLURISETTORIALE TRASPORTI": "Plurisettoriale",
}

REGIONI = {
    "ABRUZZO": "Abruzzo", "BASILICATA": "Basilicata", "CALABRIA": "Calabria", "CAMPANIA": "Campania",
    "EMILIA ROMAGNA": "Emilia-Romagna", "EMILIA-ROMAGNA": "Emilia-Romagna",
    "FRIULI VENEZIA GIULIA": "Friuli-Venezia Giulia", "FRIULI-VENEZIA GIULIA": "Friuli-Venezia Giulia",
    "LAZIO": "Lazio", "LIGURIA": "Liguria", "LOMBARDIA": "Lombardia", "MARCHE": "Marche", "MOLISE": "Molise",
    "PIEMONTE": "Piemonte", "PUGLIA": "Puglia", "SARDEGNA": "Sardegna", "SICILIA": "Sicilia", "TOSCANA": "Toscana",
    "TRENTINO ALTO ADIGE": "Trentino-Alto Adige", "TRENTINO-ALTO ADIGE": "Trentino-Alto Adige",
    "UMBRIA": "Umbria", "VALLE D'AOSTA": "Valle d'Aosta", "VENETO": "Veneto",
}

# provincia (nome come nel registro MIT) -> regione
PROVINCE = {
    "Chieti": "Abruzzo", "L'Aquila": "Abruzzo", "Pescara": "Abruzzo", "Teramo": "Abruzzo",
    "Matera": "Basilicata", "Potenza": "Basilicata",
    "Catanzaro": "Calabria", "Cosenza": "Calabria", "Crotone": "Calabria", "Reggio di Calabria": "Calabria",
    "Vibo Valentia": "Calabria",
    "Avellino": "Campania", "Benevento": "Campania", "Caserta": "Campania", "Napoli": "Campania", "Salerno": "Campania",
    "Bologna": "Emilia-Romagna", "Ferrara": "Emilia-Romagna", "Forli'-Cesena": "Emilia-Romagna",
    "Modena": "Emilia-Romagna", "Parma": "Emilia-Romagna", "Piacenza": "Emilia-Romagna", "Ravenna": "Emilia-Romagna",
    "Reggio nell'Emilia": "Emilia-Romagna", "Rimini": "Emilia-Romagna",
    "Gorizia": "Friuli-Venezia Giulia", "Pordenone": "Friuli-Venezia Giulia", "Trieste": "Friuli-Venezia Giulia",
    "Udine": "Friuli-Venezia Giulia",
    "Frosinone": "Lazio", "Latina": "Lazio", "Rieti": "Lazio", "Roma": "Lazio", "Viterbo": "Lazio",
    "Genova": "Liguria", "Imperia": "Liguria", "La Spezia": "Liguria", "Savona": "Liguria",
    "Bergamo": "Lombardia", "Brescia": "Lombardia", "Como": "Lombardia", "Cremona": "Lombardia", "Lecco": "Lombardia",
    "Lodi": "Lombardia", "Mantova": "Lombardia", "Milano": "Lombardia", "Monza e della Brianza": "Lombardia",
    "Pavia": "Lombardia", "Sondrio": "Lombardia", "Varese": "Lombardia",
    "Ancona": "Marche", "Ascoli Piceno": "Marche", "Fermo": "Marche", "Macerata": "Marche", "Pesaro e Urbino": "Marche",
    "Campobasso": "Molise", "Isernia": "Molise",
    "Alessandria": "Piemonte", "Asti": "Piemonte", "Biella": "Piemonte", "Cuneo": "Piemonte", "Novara": "Piemonte",
    "Torino": "Piemonte", "Verbano-Cusio-Ossola": "Piemonte", "Vercelli": "Piemonte",
    "Bari": "Puglia", "Barletta-Andria-Trani": "Puglia", "Brindisi": "Puglia", "Foggia": "Puglia", "Lecce": "Puglia",
    "Taranto": "Puglia",
    "Cagliari": "Sardegna", "Nuoro": "Sardegna", "Oristano": "Sardegna", "Sassari": "Sardegna",
    "Sud Sardegna": "Sardegna",
    "Agrigento": "Sicilia", "Caltanissetta": "Sicilia", "Catania": "Sicilia", "Enna": "Sicilia", "Messina": "Sicilia",
    "Palermo": "Sicilia", "Ragusa": "Sicilia", "Siracusa": "Sicilia", "Trapani": "Sicilia",
    "Arezzo": "Toscana", "Firenze": "Toscana", "Grosseto": "Toscana", "Livorno": "Toscana", "Lucca": "Toscana",
    "Massa-Carrara": "Toscana", "Pisa": "Toscana", "Pistoia": "Toscana", "Prato": "Toscana", "Siena": "Toscana",
    "Bolzano": "Trentino-Alto Adige", "Trento": "Trentino-Alto Adige",
    "Perugia": "Umbria", "Terni": "Umbria",
    "Aosta": "Valle d'Aosta",
    "Belluno": "Veneto", "Padova": "Veneto", "Rovigo": "Veneto", "Treviso": "Veneto", "Venezia": "Veneto",
    "Verona": "Veneto", "Vicenza": "Veneto",
}
# grafie CGSSE diverse e comuni non capoluogo visti nel calendario -> provincia
ALIAS = {
    "REGGIO CALABRIA": "Reggio di Calabria", "REGGIO EMILIA": "Reggio nell'Emilia", "FORLI": "Forli'-Cesena",
    "FORLI-CESENA": "Forli'-Cesena", "MONZA": "Monza e della Brianza", "BARLETTA": "Barletta-Andria-Trani",
    "FIUMICINO": "Roma", "CIAMPINO": "Roma", "GENZANO DI ROMA": "Roma", "LANUVIO": "Roma", "ARICCIA": "Roma",
    "ALBANO LAZIALE": "Roma", "LAMEZIA TERME": "Catanzaro", "VOLLA": "Napoli", "TORRE DEL GRECO": "Napoli",
    "MARANO DI NAPOLI": "Napoli", "CASORIA": "Napoli", "PORTICI": "Napoli", "ELMAS": "Cagliari", "OLBIA": "Sassari",
    "ALGHERO": "Sassari", "MOLFETTA": "Bari", "VASTO": "Chieti", "LANCIANO": "Chieti", "TERMOLI": "Campobasso",
    "ROVERETO": "Trento", "CORIGLIANO-ROSSANO": "Cosenza", "SPINADESCO": "Cremona", "VADO LIGURE": "Savona",
    "SAN DONA' DI PIAVE": "Venezia", "VILLAFRANCA DI VERONA": "Verona",
}


def norma(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", t).strip().upper()


PROV_NORMA = {norma(p): p for p in PROVINCE}


def scarica(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def leggi_jsonl(testo):
    righe = []
    for n, riga in enumerate(testo.splitlines(), 1):
        if riga.strip():
            try:
                righe.append(json.loads(riga))
            except ValueError as e:
                raise ValueError(f"riga {n} non leggibile: {e}") from e
    return righe


def settore_mit(settore_cgsse):
    """Settore del registro MIT, oppure None se lo sciopero non riguarda i trasporti."""
    parti = [norma(p) for p in (settore_cgsse or "").split(",") if p.strip()]
    if any(p.startswith("GENERALE") for p in parti):
        return "Generale"
    trasporti = {SETTORI_TRASPORTO[p] for p in parti if p in SETTORI_TRASPORTO}
    if not trasporti:
        # "Plurisettoriale nazionale" da solo: può toccare i trasporti (es. USI-CIT); con scuola/sanità no
        return "Plurisettoriale" if parti and all(p.startswith("PLURISETTORIALE") for p in parti) else None
    if len(trasporti) > 1 or any(p.startswith("PLURISETTORIALE") for p in parti):
        return "Plurisettoriale"
    return trasporti.pop()


def luogo(ambito, settore_cgsse):
    """(rilevanza, regione, provincia, da_verificare) come nel registro MIT."""
    a = norma(ambito)
    livello = next((p.split()[-1] for p in norma(settore_cgsse).split(", ")
                    if p.startswith(("GENERALE ", "PLURISETTORIALE "))), "")
    if a in ("NAZIONALE", "") or livello == "NAZIONALE":
        return "Nazionale", "Italia", "Tutte", a == ""
    pezzi = [p.strip() for p in a.split(",") if p.strip()]
    regioni, province, ignoti = set(), [], []
    for p in pezzi:
        if p in REGIONI:
            regioni.add(REGIONI[p])
        elif p in PROV_NORMA or p in ALIAS:
            prov = PROV_NORMA.get(p) or ALIAS[p]
            province.append(prov)
            regioni.add(PROVINCE[prov])
        else:
            ignoti.append(p)
    if ignoti and not regioni:
        return "Locale", "", ambito.strip().title(), True
    if len(regioni) > 1:
        return "Interregionale", "Italia", "Tutte", bool(ignoti)
    reg = regioni.pop()
    if not province:
        return "Regionale", reg, "Tutte", bool(ignoti)
    if len(set(province)) == 1 and not ignoti:
        return "Locale", reg, province[0], False
    return "Territoriale", reg, "Tutte", bool(ignoti)


def sindacati(t):
    t = re.sub(r"Proclamante:\s*", "", t or "")
    t = re.sub(r"\|?Aderente:\s*", " (ADERENTE: ", t)
    t = t + ")" if "(ADERENTE:" in t else t
    return re.sub(r"\s*,\s*", "/", t.strip()).upper()


def unisci(righe, precedenti=None):
    """Una voce per link CGSSE: revocato se una riga lo dice; altri campi dalla riga più nuova."""
    viste_prima = {json.dumps(r, sort_keys=True) for r in (precedenti or [])}
    per_link = {}
    for r in righe:
        link = r.get("dettagli_link") or ""
        m = re.search(r"/(\d+)$", link)
        if not m:
            continue
        nuova = json.dumps(r, sort_keys=True) not in viste_prima
        cur = per_link.get(m.group(1))
        settori = ((cur or {}).get("_settori") or []) + [r.get("settore") or ""]
        if cur is None or nuova or not cur["_nuova"]:
            revocato = (cur or {}).get("revocato", False) or bool(r.get("revocato"))
            per_link[m.group(1)] = cur = {**r, "_nuova": nuova, "revocato": revocato}
        else:
            cur["revocato"] = cur["revocato"] or bool(r.get("revocato"))
        cur["_settori"] = settori
    # stesso link con settori diversi (es. "Plurisettoriale nazionale" e "Scuola, Sanità"): vale quello dei trasporti
    for r in per_link.values():
        trasporto = [s for s in r["_settori"] if settore_mit(s)]
        if trasporto and not settore_mit(r.get("settore")):
            r["settore"] = trasporto[-1]
    return per_link


def voce(id_cgsse, r, oggi):
    sett = settore_mit(r.get("settore"))
    if sett is None:
        return None
    inizio = r.get("data_dal_iso") or r.get("data_iso")
    fine = r.get("data_al_iso") or inizio
    if not inizio:
        return None
    ril, reg, prov, dubbio = luogo(r.get("ambito_geografico"), r.get("settore"))
    note = "REVOCATO (CGSSE)" if r["revocato"] else ""
    if dubbio:
        note = (note + " " if note else "") + f"[luogo da verificare: {r.get('ambito_geografico', '')}]"
    v = {
        "id": f"cgsse-{id_cgsse}",
        "inizio": inizio, "fine": fine, "settore": sett, "rilevanza": ril, "regione": reg, "provincia": prov,
        "sindacati": sindacati(r.get("sindacato")),
        "categoria": norma(r.get("azienda")),
        "modalita": re.sub(r"\s+", " ", (r.get("modalita") or "").strip().rstrip("]")).upper(),
        "proclamazione": "",  # non presente nell'elenco CGSSE (solo nella scheda di dettaglio)
        "ricezione": "",
        "note": note,
        "stato": "revocato" if r["revocato"] else ("concluso" if fine < oggi else "in programma"),
        "visto_prima": oggi, "visto_ultimo": oggi, "modifiche": [],
        "fonte": "cgsse", "url_dettaglio": r.get("dettagli_link", ""),
        "settore_cgsse": r.get("settore", ""), "ambito_cgsse": r.get("ambito_geografico", ""),
    }
    return v


# --- confronto con dati/scioperi.json -------------------------------------------------------------------
PAROLE_VUOTE = {"PERSONALE", "SOC", "SOCC", "SPA", "SRL", "S", "P", "A", "DI", "DEL", "DELLA", "E", "IL", "LA", "DEI",
                "AEROPORTO", "AEROPORTI", "SEDE", "SEDI", "PRESSO", "ADDETTO", "OPERANTI", "IMPIEGATO", "SITO",
                "DELL", "DA", "IN", "PER", "TUTTE", "CATEGORIE", "PUBBLICHE", "PRIVATE", "SETTORI", "PUBBLICI",
                "PRIVATI", "SCIOPERO", "GENERALE", "TUTTI", "ANCHE", "APPALTO", "LAVORATORI", "AZIENDE", "GRUPPO"}


def parole(t):
    return {w for w in re.findall(r"[A-Z0-9]{2,}", norma(t)) if w not in PAROLE_VUOTE}


def sigle(t):
    t = norma(t).replace("UILTRASPORTI", "UILT").replace("UITRASPORTI", "UILT")
    t = t.replace("CONFEDERAZIONE COBAS", "COBAS")
    return {w for w in re.findall(r"[A-Z]{3,}", t) if w not in {"OSR", "OSP", "OST", "RSA", "RSU", "LAVORO",
                                                               "PRIVATO", "ADERENTE", "UNICA"}}


def somiglia(a, b):
    """Punteggio da 0 a 4,5: stessa data e settore compatibile sono obbligatori (1), poi categoria (+1),
    sindacati in comune (+1 e fino a +1 per la quota di sigle in comune), stessa regione (+0,5)."""
    if a["inizio"] != b["inizio"]:
        return 0
    gen = {"Generale", "Plurisettoriale"}
    if a["settore"] != b["settore"] and not ({a["settore"], b["settore"]} <= gen):
        return 0
    p = 1
    if parole(a["categoria"]) & parole(b["categoria"]):
        p += 1
    sa, sb = sigle(a["sindacati"]), sigle(b["sindacati"])
    if sa & sb:
        p += 1 + len(sa & sb) / len(sa | sb)  # più sigle in comune, punteggio più alto
    elif a["settore"] in gen:
        return 0  # scioperi generali dello stesso giorno: senza sindacati in comune non sono lo stesso
    if a["regione"] and b["regione"] and a["regione"] == b["regione"]:
        p += 0.5
    return p


def confronta(voci, archivio, dal):
    nostri = [s for s in archivio.values() if s["fine"] >= dal]
    loro = [v for v in voci if v["fine"] >= dal]
    # abbinamento globale: prima le coppie con il punteggio più alto, ogni voce usata una volta sola
    tutte = sorted(((somiglia(v, s), v["id"], s["id"]) for v in loro for s in nostri), reverse=True)
    presi_loro, presi_nostri, coppie = set(), set(), []
    per_id = {v["id"]: v for v in loro}
    for p, idv, ids in tutte:
        if p < 2 or idv in presi_loro or ids in presi_nostri:
            continue
        presi_loro.add(idv)
        presi_nostri.add(ids)
        coppie.append((per_id[idv], archivio[ids], round(p, 2)))
    coppie.sort(key=lambda c: (c[0]["inizio"], c[0]["id"]))
    nuovi = [v for v in loro if v["id"] not in presi_loro]
    mancanti = [s for s in nostri if s["id"] not in presi_nostri]
    return coppie, nuovi, mancanti


def main():
    args = sys.argv[1:]

    def opz(nome, default=None):
        return args[args.index(nome) + 1] if nome in args else default

    oggi = datetime.now(ROMA).date().isoformat()
    try:
        testo = Path(opz("--file")).read_text(encoding="utf-8") if opz("--file") else scarica(URL_COPIA)
        righe = leggi_jsonl(testo)
        prec = leggi_jsonl(Path(opz("--precedente")).read_text(encoding="utf-8")) if opz("--precedente") else None
    except Exception as e:  # noqa: BLE001
        raise SystemExit(f"ERRORE: copia CGSSE non leggibile ({e}).")
    if not righe:
        raise SystemExit("ERRORE: copia CGSSE vuota.")
    dal = opz("--dal", oggi)
    unite = unisci(righe, prec)
    voci = [v for k, r in unite.items() if (v := voce(k, r, oggi))]
    voci.sort(key=lambda v: (v["inizio"], v["id"]))
    futuri = [v for v in voci if v["fine"] >= dal]
    print(f"Copia CGSSE: {len(righe)} righe, {len(unite)} scioperi distinti, {len(voci)} dei trasporti; "
          f"{len(futuri)} con fine dal {dal} in poi (fonte ufficiale: {URL_UFFICIALE}).")
    if opz("--out"):
        Path(opz("--out")).write_text(json.dumps({v["id"]: v for v in futuri}, ensure_ascii=False, indent=1) + "\n",
                                      encoding="utf-8")
        print(f"Voci scritte in {opz('--out')}")
    if opz("--confronta"):
        archivio = json.loads(Path(opz("--confronta")).read_text(encoding="utf-8"))
        coppie, nuovi, mancanti = confronta(voci, archivio, dal)
        print(f"\nCoincidono con i nostri dati: {len(coppie)}")
        for v, s, p in coppie:
            diverso = " STATO DIVERSO" if (v["stato"] == "revocato") != (s["stato"] in ("revocato", "rimosso dal registro")) else ""
            print(f"  {v['inizio']} {v['settore']:<26} MIT {s['id']} ({s['stato']}) = {v['id']} ({v['stato']}) "
                  f"[{p}]{diverso}  {s['categoria'][:50]}")
        print(f"\nSolo nella fonte CGSSE: {len(nuovi)}")
        for v in nuovi:
            print(f"  {v['inizio']}{'→' + v['fine'] if v['fine'] != v['inizio'] else ''} {v['settore']} | {v['rilevanza']} "
                  f"{v['regione']}/{v['provincia']} | {v['categoria'][:60]} | {v['sindacati'][:40]} | {v['stato']} | {v['id']}")
        print(f"\nSolo nei nostri dati (MIT): {len(mancanti)}")
        for s in mancanti:
            print(f"  {s['inizio']} {s['settore']} | {s['rilevanza']} {s['regione']}/{s['provincia']} | "
                  f"{s['categoria'][:60]} | {s['stato']} | MIT {s['id']}")


if __name__ == "__main__":
    main()
