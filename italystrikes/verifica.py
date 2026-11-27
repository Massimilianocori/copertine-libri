"""Controllo delle pagine per azienda e per data di Italy Strikes (italystrikes/sito/), da lanciare dopo genera.py.

Uso (dalla radice del repository):
    python3 italystrikes/genera.py && python3 italystrikes/verifica.py     # esce con 1 se c'è almeno un errore
    python3 italystrikes/verifica.py --rete    # in più rilegge le pagine ufficiali di dati/fasce.json e cerca le citazioni

Copre le pagine nate il 27/11/2026: /it/aziende/, /it/sciopero-<azienda>/, /it/sciopero-<giorno>-<mese>-<anno>/,
/strike-<day>-<month>-<year>/ e le 26 pagine dei 13 aeroporti aggiunti lo stesso giorno (punto 7). Non controlla il resto del sito. Legge i dati grezzi (dati/scioperi.json), non il generatore.

1. Dati: ogni azienda di dati/aziende.json ha i link in dati/link.json (validi); ogni citazione di dati/fasce.json ha una
   pagina sullo stesso dominio di un link dell'azienda; prove fisse sull'abbinamento dei nomi (ATM di Messina non è ATM
   Milano, «Trenitalia Tper» non è Trenitalia, la nota con «escluso» non nomina nessuno).
2. Pagine attese: una per azienda, l'indice, una per ogni giorno di sciopero nazionale (italiano e inglese, collegate con
   hreflang); nessuna pagina per un giorno senza sciopero nazionale nei dati; tutte in sitemap, senza noindex, con il
   canonical giusto e almeno un link interno da un'altra pagina.
3. Ogni sciopero mostrato (scheda, frase di risposta, riga dello storico) esiste nei dati; la sua data e il testo degli
   orari sono quelli del registro; uno sciopero revocato è scritto come revocato.
4. Ogni data scritta per esteso e ogni orario (HH.MM) nel corpo della pagina viene da uno sciopero mostrato, da una
   citazione di dati/fasce.json mostrata, o è la data di generazione / il limite dei 30 giorni / l'inizio dell'archivio.
5. La risposta in cima non afferma scioperi che non sono nei dati: «sì» solo se c'è uno sciopero attivo che nomina
   l'azienda (o uno sciopero nazionale attivo quel giorno); «nessuno sciopero» solo se nei dati non ce n'è nessuno.
   L'impronta data-firma è quella che il JS ricalcola dai dati incorporati (altrimenti la risposta sparirebbe subito).
6. Ogni link esterno nel corpo è in dati/link.json, in dati/fasce.json o è una fonte dei dati (registro, Commissione
   di garanzia); la pagina di un'azienda porta il suo link ufficiale.
7. Aeroporti con una scheda in dati/aeroporti.json (controlla_aeroporti): una pagina italiana e una inglese per ognuno, collegate
   con hreflang, in sitemap, raggiunte dagli indici, dalla home, dalle città e dalle aziende della stessa città; l'elenco «prossimi
   scioperi» è uguale ai dati pubblicati (vista.json) e contiene ogni sciopero del registro che nomina l'aeroporto; lo storico
   contiene tutti e soli gli scioperi passati che lo riguardano in particolare, con data e orari del registro; gestore e fonti
   sono quelli dei dati; almeno 110 parole proprie (fuori da ogni gruppo di 5 parole presente in almeno 3 pagine del sito);
   prove fisse sull'abbinamento dei nomi («Friuli Venezia Giulia» non è Venezia, «BARI» è una parola intera).
"""
import html
import json
import re
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urljoin, urlparse

RADICE = Path(__file__).resolve().parent
sys.path.insert(0, str(RADICE))
import aziende as AZ  # noqa: E402

SITO, DATI = RADICE / "sito", RADICE / "dati"
URL_SITO = "https://italy-strikes-today.netlify.app"
FONTI_DATI = ("https://scioperi.mit.gov.it/", "https://www.cgsse.it/", "https://github.com/ondata/", "https://creativecommons.org/")
MESI_IT, MESI_EN = AZ.MESI_IT, AZ.MESI_EN
MES_IT = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]
MES_EN = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
ARCHIVIO_DAL = "2026-10-10"

errori, avvisi = [], []


def err(pagina, testo):
    errori.append(f"{pagina}: {testo}")


def carica(nome):
    return json.loads((DATI / nome).read_text(encoding="utf-8"))


SCIOPERI = carica("scioperi.json")
LINK = carica("link.json")
VISTA = carica("vista.json")
VOCI = {v["id"]: v for v in VISTA["scioperi"]}
ADESIONI = carica("adesioni.json")["voci"] if (DATI / "adesioni.json").exists() else {}
GENERATO = date.fromisoformat(VISTA["generato_il"][:10])
OGGI = GENERATO.isoformat()
LIMITE = (GENERATO + timedelta(days=AZ.GIORNI_AVANTI)).isoformat()


def link_valido(chiave):
    v = LINK.get(chiave)
    return v.get("url") if isinstance(v, dict) and str(v.get("status")) in ("200", "browser") and v.get("url") else None


def attivo(s):
    return s["stato"] not in ("revocato", "rimosso dal registro")


def in_arrivo(s):
    return s["fine"] >= OGGI and s["stato"] != "concluso"


def nazionale(s):
    return s["regione"].strip().upper() == "ITALIA"


def ore_leggibili(testo):
    t = testo.lower().replace("modalita'", "modalità")
    for sigla in ("tpl", "ncc", "rfi", "enav"):
        t = re.sub(rf"\b{sigla}\b", sigla.upper(), t)
    return t[:1].upper() + t[1:] if t else t


def orari(testo):
    """Orari HH.MM o HH:MM nel testo, in forma unica (9.01 = 09:01: le pagine inglesi li scrivono con i due punti)."""
    return {f"{int(h)}:{m}" for h, m in re.findall(r"\b(\d{1,2})[.:](\d{2})\b", testo)}


def date_in(testo):
    """Date scritte per esteso o abbreviate (con l'anno) nel testo, in italiano e in inglese -> insieme di ISO."""
    out = set()
    for elenco in (MESI_IT, MESI_EN, MES_IT, MES_EN):
        for g, m, a in re.findall(r"\b(\d{1,2})\s+(" + "|".join(elenco) + r")\s+(\d{4})\b", testo.lower()):
            try:
                out.add(date(int(a), elenco.index(m) + 1, int(g)).isoformat())
            except ValueError:
                out.add(f"data impossibile {g} {m} {a}")
    return out


def piano(h):
    h = re.sub(r"(?is)<(script|style|svg)\b.*?</\1>", " ", h)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def corpo(testo):
    """<main> senza la riga di freschezza (ore dei controlli), il modulo degli avvisi e gli script."""
    m = re.search(r"(?s)<main\b.*?</main>", testo)
    h = m.group(0) if m else ""
    h = re.sub(r'(?s)<p class="fresco".*?</p>', " ", h)
    h = re.sub(r'(?s)<section class="card" id="(?:avvisi|alerts)".*?</section>', " ", h)
    h = re.sub(r'(?s)<section class="aff\b.*?</section>', " ", h)  # riquadro dei partner: lo controlla monetizzazione.py
    return h


# ---------------------------------------------------------------- 1. dati
def controlla_dati():
    slug = [a["slug"] for a in AZ.AZIENDE]
    if len(slug) != len(set(slug)) or len({a["pagina"] for a in AZ.AZIENDE}) != len(slug):
        err("aziende.json", "slug o pagine doppie")
    for a in AZ.AZIENDE:
        try:
            re.compile(a["re"])
        except re.error as e:
            err("aziende.json", f"{a['slug']}: espressione non valida ({e})")
        if not a["link"]:
            err("aziende.json", f"{a['slug']}: nessun link ufficiale")
        for x in a["link"]:
            if not link_valido(x["chiave"]):
                err("aziende.json", f"{a['slug']}: il link {x['chiave']} non è in link.json (o non è valido)")
    for f in AZ.FASCE:
        a = AZ.PER_SLUG.get(f["azienda"])
        if not a:
            err("fasce.json", f"azienda sconosciuta: {f['azienda']}")
            continue
        domini = {urlparse(link_valido(x["chiave"]) or "").netloc.removeprefix("www.") for x in a["link"]}
        if urlparse(f["url"]).netloc.removeprefix("www.") not in domini:
            err("fasce.json", f"{f['azienda']}: {f['url']} non è sul dominio di un link dell'azienda in link.json")
        try:
            date.fromisoformat(f["letto_il"])
            if f["data"]:
                date.fromisoformat(f["data"])
        except ValueError:
            err("fasce.json", f"{f['azienda']}: data non valida")
        if not f["citazioni"] or any(not c["testo"].strip() or not c["etichetta"].strip() for c in f["citazioni"]):
            err("fasce.json", f"{f['azienda']}: citazione vuota")
    # prove fisse sull'abbinamento dei nomi (rischio 2 del piano: nomi scritti in modi diversi)
    def s(cat, reg="Italia", prov="Tutte", sett="Trasporto pubblico locale", note="", mod="24 ORE"):
        return {"categoria": cat, "regione": reg, "provincia": prov, "settore": sett, "note": note, "modalita": mod}
    prove = [
        (s("ATM", "Sicilia", "Messina"), []), (s("PERSONALE SOCC. GRUPPO ATM DI MILANO", "Lombardia"), ["atm"]),
        (s("AMT", "Liguria", "Genova"), ["amt-genova"]), (s("AMT", "Sicilia", "Catania"), []),
        (s("AMAT", "Puglia", "Taranto"), []), (s("AMAT", "Sicilia", "Palermo"), ["amat-palermo"]),
        (s("PERSONALE SOC. TRENITALIA TPER", "Emilia-Romagna", sett="Ferroviario"), []),
        (s("GRUPPO FSI, MERCITALIA RAIL, TRENITALIA, TRENITALIA TPER SCARL", sett="Ferroviario"), ["trenitalia"]),
        (s("PERSONALE SOC. TPER DI BOLOGNA", "Emilia-Romagna", "Bologna"), ["tper"]),
        (s("ITALO NTV", sett="Ferroviario"), ["italo"]), (s("PERSONALE SOC. TRENORD", "Lombardia", sett="Ferroviario"), ["trenord"]),
        (s("PERSONALE NAVIGANTE SOC. EASYJET AIRLINES LIMITED", sett="Aereo"), ["easyjet"]),
        (s("PERSONALE SOC. RYANAIR E MALTA AIR", sett="Aereo"), ["ryanair"]),
        (s("SCIOPERO GENERALE", sett="Generale", note="ESCLUSO PERSONALE SOC. ATAC E COTRAL", reg="Lazio"), []),
        (s("PERSONALE IMPRESE FERROVIARIE", sett="Plurisettoriale", note="*PER TPL SOCC. GTT, EAV"), ["gtt", "eav"]),
        (s("PERSONALE SOC. ATAC DI ROMA", "Lazio", "Roma"), ["atac"]), (s("PERSONALE SOC. COTRAL", "Lazio"), ["cotral"]),
        (s("PERSONALE SOC. ANM DI NAPOLI", "Campania", "Napoli"), ["anm"]), (s("PERSONALE SOC. EAV", "Campania"), ["eav"]),
        (s("PERSONALE SOC. GTT DI TORINO", "Piemonte", "Torino"), ["gtt"]), (s("PERSONALE SOC. ACTV DI VENEZIA", "Veneto", "Venezia"), ["actv"]),
        (s("PERSONALE SOC. AUTOLINEE TOSCANE", "Toscana"), ["autolinee-toscane"]), (s("PERSONALE SOC AMTAB DI BARI", "Puglia", "Bari"), ["amtab"]),
        (s("PERSONALE SOC. ATVO DI VENEZIA", "Veneto", "Venezia"), []), (s("PERSONALE SOC. AIR CAMPANIA DI NAPOLI", "Campania", "Napoli"), []),
    ]
    for rec, atteso in prove:
        if AZ.nominate(rec) != atteso:
            err("aziende.py", f"abbinamento sbagliato per «{rec['categoria']}» ({rec['regione']}): {AZ.nominate(rec)} invece di {atteso}")
    # sciopero di sola rete o di un'azienda sola non deve diventare «può riguardare» per aziende estranee
    gen = [
        (s("FATA SRL", "Calabria", "Cosenza"), ["local-transport"], "local", []),
        (s("CONSORZIO STABILE IMPERO, GAM, PS SERVIZI", sett="Ferroviario"), ["trains"], "national", []),
        (s("LA LUCENTE SPA", "Emilia-Romagna", "Bologna", sett="Aereo"), ["flights"], "airport", []),
        (s("PERSONALE SOC. ENAV", sett="Aereo"), ["flights"], "national", ["ryanair", "easyjet"]),
        (s("RFI", "Veneto", "Verona", sett="Ferroviario"), ["trains"], "local", []),
        (s("SCIOPERO GENERALE", "Lombardia", sett="Generale"), ["general-strikes", "trains", "local-transport"], "regional",
         ["trenitalia", "atm", "trenord", "italo"]),
    ]
    for rec, sett, amb, atteso in gen:
        if AZ.generici(rec, sett, amb, []) != atteso:
            err("aziende.py", f"«può riguardare» sbagliato per «{rec['categoria']}»: {AZ.generici(rec, sett, amb, [])} invece di {atteso}")


def controlla_lettura():
    """Prove fisse su leggi() di genera.py (revisione del 27/11/2026): appalti ferroviari, esclusioni, taxi."""
    import genera as G
    base = {"id": "prova", "inizio": "2026-12-17", "fine": "2026-12-17", "rilevanza": "Nazionale", "regione": "Italia", "provincia": "Tutte",
            "sindacati": "X", "proclamazione": "2026-12-01", "note": "", "stato": "in programma"}
    appalti = G.leggi({**base, "settore": "Ferroviario", "settore_cgsse": "Appalti ferroviari", "fonte": "cgsse", "url_dettaglio": "https://www.cgsse.it/x",
                       "categoria": "CONSORZIO STABILE IMPERO, GAM, PS SERVIZI", "modalita": "ASTENSIONE DI MEZZO TURNO PER OGNI TURNO DI LAVORO"})
    if AZ.nazionale_passeggeri(appalti) or "ditte in appalto" not in appalti["titolo_it"] or appalti["az_gen"] or appalti["settore_it"] != "Appalti ferroviari":
        err("genera.py", "uno sciopero degli appalti ferroviari è trattato come sciopero dei treni (pagina per data o titolo)")
    if AZ.date_nazionali([appalti], date(2026, 12, 1)):
        err("aziende.py", "pagina per data creata per uno sciopero dei soli appalti ferroviari")
    # MIT 8612 (30/10/2026) e CGSSE 382981 (20/11/2026): scioperi generali che escludono i trasporti
    v = G.leggi({**base, "settore": "Generale", "categoria": "SCIOPERO GENERALE CATEGORIE PUBBLICHE E PRIVATE*", "modalita": "INTERA GIORNATA",
                 "note": "* ESCLUSO INTERO SETTORE TRASPORTI"})
    if [x for x in v["settori"] if x in AZ.PASSEGGERI] or v["az_gen"] or AZ.nazionale_passeggeri(v):
        err("genera.py", f"«ESCLUSO INTERO SETTORE TRASPORTI» non esclude i trasporti: {v['settori']} {v['az_gen']}")
    v = G.leggi({**base, "settore": "Generale", "categoria": "TUTTI I SETTORI PUBBLICI E PRIVATI",
                 "modalita": "INTERA GIORNATA AD ESCLUSIONE DEL TRASPORTO PUBBLICO LOCALE, TRASPORTO FERROVIARIO, TRASPORTO MERCI SU ROTAIA.PER LA SANITÀ LO SCIOPERO È ARTICOLATO DALL'INIZIO DEL PRIMO TURNO"})
    if "trains" in v["settori"] or "local-transport" in v["settori"] or "flights" not in v["settori"] or \
            {"atm", "trenitalia", "italo", "atac"} & set(v["az_gen"]) or "ryanair" not in v["az_gen"]:
        err("genera.py", f"esclusione scritta negli orari non letta: {v['settori']} {v['az_gen']}")
    for i in ("8612", "cgsse-382981"):   # le due voci vere, finché sono nei dati
        if i in SCIOPERI:
            w = G.leggi(SCIOPERI[i])
            if {"atm", "trenitalia"} & set(w["az_gen"]):
                err("genera.py", f"lo sciopero {i} esclude treni e trasporto locale ma «può riguardare» ATM o Trenitalia")
    v = G.leggi({**base, "settore": "Taxi", "categoria": "SERVIZIO TAXI", "modalita": "DALLE ORE 8.00 ALLE ORE 22.00"})
    if v["chi_gen"] != "Taxi drivers" or v["chi_gen_it"] != "Tassisti":
        err("genera.py", "sciopero dei taxi: «Chi» non dice tassisti")
    a, b = dict(appalti), dict(appalti)
    b["ore"] = "ALTRI ORARI"
    if AZ.firma([a]) == AZ.firma([b]):
        err("aziende.py", "l'impronta non cambia quando cambiano gli orari")
    if "+'|'+v.ore" not in G.JS:
        err("genera.py", "la firma nel JS non comprende gli orari")


# ---------------------------------------------------------------- 2-6. pagine
def leggi_pagina(percorso):
    f = SITO / percorso / "index.html"
    if not f.exists():
        err(percorso, "pagina mancante")
        return None
    return f.read_text(encoding="utf-8")


def controlli_comuni(percorso, testo, sitemap, lingua):
    if f'<link rel="canonical" href="{URL_SITO}/{percorso}">' not in testo:
        err(percorso, "canonical mancante o sbagliato")
    if "noindex" in testo.split("</head>")[0]:
        err(percorso, "noindex")
    if f"<loc>{URL_SITO}/{percorso}</loc>" not in sitemap:
        err(percorso, "non è in sitemap")
    if len(re.findall(r"<h1\b", testo)) != 1:
        err(percorso, "serve un solo h1")
    if f'<html lang="{lingua}">' not in testo:
        err(percorso, f"lingua della pagina diversa da {lingua}")
    m = re.search(r"<title>(.*?)</title>", testo)
    if not m or not m.group(1).strip():
        err(percorso, "titolo mancante")
    visibile = piano(corpo(testo))
    for parola in ("undefined", "NaN", "None", "TODO", "{", "}"):
        if re.search(rf"(?<![A-Za-z]){re.escape(parola)}(?![A-Za-z])", visibile):
            err(percorso, f"testo di servizio nel corpo: {parola}")


def controlla_contenuto(percorso, testo, date_extra=(), orari_extra=(), link_extra=()):
    """Punti 3, 4 e 6: scioperi mostrati, date, orari, link esterni. Restituisce gli id mostrati."""
    h = corpo(testo)
    ids = set(re.findall(r'<article class="sc[^"]*" id="s([^"]+)"', h)) | set(re.findall(r'data-sid="([^"]+)"', h))
    for i in ids:
        if i not in SCIOPERI:
            err(percorso, f"sciopero {i} mostrato ma non presente in dati/scioperi.json")
    ids &= set(SCIOPERI)
    # schede: testo ufficiale degli orari e date della scheda
    for i, blocco in re.findall(r'(?s)<article class="sc[^"]*" id="s([^"]+)">(.*?)</article>', h):
        if i not in SCIOPERI:
            continue
        s = SCIOPERI[i]
        if html.escape(s["modalita"]) not in blocco and s["modalita"] not in html.unescape(blocco):
            err(percorso, f"scheda {i}: manca il testo degli orari del registro «{s['modalita'][:50]}»")
        quando = re.search(r'(?s)<div class="quando">(.*?)<small>', blocco)
        attese = {s["inizio"], s["fine"]}
        trovate = date_in(piano(quando.group(1))) if quando else set()
        if not trovate or not trovate <= attese:
            err(percorso, f"scheda {i}: data {sorted(trovate)} diversa dal registro {sorted(attese)}")
        if s["stato"] == "revocato" and not re.search(r"Revocato|Called off", blocco):
            err(percorso, f"scheda {i}: sciopero revocato non segnalato")
    # frasi di risposta e righe dello storico
    for tag, i, dentro in re.findall(r'(?s)<(li|tr|p) data-sid="([^"]+)"[^>]*>(.*?)</\1>', h):
        if i not in SCIOPERI:
            continue
        s, t = SCIOPERI[i], piano(dentro)
        trovate = date_in(t)
        if not trovate <= {s["inizio"], s["fine"]}:
            err(percorso, f"riga {i}: data {sorted(trovate)} diversa dal registro ({s['inizio']} – {s['fine']})")
        if tag != "p" and not orari(t) <= orari(s["modalita"]):
            err(percorso, f"riga {i}: orari {sorted(orari(t) - orari(s['modalita']))} non presenti nel registro")
        if tag != "p" and "«" in t and ore_leggibili(s["modalita"]) not in t:
            err(percorso, f"riga {i}: il testo tra virgolette non è quello del registro")
        if s["stato"] == "revocato" and not re.search(r"[Rr]evocato|[Cc]alled off", t):
            err(percorso, f"riga {i}: sciopero revocato non segnalato")
    # date e orari di tutta la pagina
    fasce = []
    for chiave in re.findall(r'data-fasce="([^"]+)"', h):
        az, _, giorno = html.unescape(chiave).partition("|")
        trovate = [f for f in AZ.FASCE if f["azienda"] == az and f["data"] == giorno]
        if not trovate:
            err(percorso, f"citazione mostrata ma non presente in fasce.json: {chiave}")
        fasce += trovate
    for blocco in re.findall(r'(?s)<div class="cit"[^>]*>(.*?)</div>', h):
        for q in re.findall(r"(?s)<q>(.*?)</q>", blocco):
            if not any(html.unescape(q) == c["testo"] for f in fasce for c in f["citazioni"]):
                err(percorso, f"citazione non uguale a fasce.json: «{html.unescape(q)[:60]}»")
        m = re.search(r'<a href="([^"]+)"', blocco.split('class="small"')[-1])
        if not m or not any(html.unescape(m.group(1)) == f["url"] for f in fasce):
            err(percorso, "citazione senza il link alla sua fonte")
    # avviso di un'azienda per un giorno preciso: solo se quel giorno c'è ancora uno sciopero attivo che la riguarda
    for f in fasce:
        if f["data"] and f["data"] >= OGGI and not any(
                v["inizio"] <= f["data"] <= v["fine"] and attivo(v) and f["azienda"] in v["az"] + v["az_gen"] for v in VISTA["scioperi"]):
            err(percorso, f"avviso di {f['azienda']} per il {f['data']} mostrato, ma quel giorno non c'è uno sciopero attivo che la riguarda")
    # sindacati secondo la Commissione di garanzia: uguali a dati/adesioni.json
    for i in re.findall(r'data-adesioni="([^"]+)"', h):
        a = ADESIONI.get(i)
        blocco = piano(re.search(rf'(?s)<p data-adesioni="{re.escape(i)}">(.*?)</p>', h).group(1))
        if not a or a["proclamanti"] not in blocco or a["aderenti"] not in blocco or f'href="{a["url"]}"' not in h:
            err(percorso, f"adesioni dello sciopero {i} diverse da dati/adesioni.json")
    date_ok = {OGGI, LIMITE, ARCHIVIO_DAL} | set(date_extra) | {a["letto_il"] for a in ADESIONI.values()}
    orari_ok = set(orari_extra)
    for i in ids:
        s = SCIOPERI[i]
        date_ok |= {s["inizio"], s["fine"], s.get("proclamazione") or "", s.get("rimosso_il") or ""}
        orari_ok |= orari(s["modalita"]) | orari(s.get("note", ""))
    for f in fasce:
        date_ok |= {f["letto_il"], f["data"]}
        for c in f["citazioni"]:
            orari_ok |= orari(c["testo"])
        orari_ok |= orari(f["fonte"])
    visibile = piano(h)
    for x in sorted(date_in(visibile) - date_ok):
        err(percorso, f"data {x} nel testo ma non nei dati mostrati")
    for x in sorted(orari(visibile) - orari_ok):
        err(percorso, f"orario {x} nel testo ma non nel registro né in una citazione")
    # link esterni
    ammessi = {v["url"] for k, v in LINK.items() if link_valido(k)} | {f["url"] for f in AZ.FASCE} | set(link_extra)
    for s in SCIOPERI.values():
        ammessi |= {s.get("url_dettaglio") or "", s.get("revoca_cgsse") or ""}
    for u in set(re.findall(r'href="(https?://[^"]+)"', h)):
        u = html.unescape(u)
        if u.startswith(URL_SITO) or u in ammessi or u.startswith(FONTI_DATI):
            continue
        err(percorso, f"link esterno non presente in link.json / fasce.json: {u}")
    return ids


def controlla_ambito_cgsse():
    """Prove fisse (revisione del 27/11/2026): per le voci della Commissione di garanzia l'aeroporto viene dall'ambito geografico,
    non dalla sola provincia. Casi veri del calendario 2025-2026: ADR Security «FIUMICINO» non è Ciampino (CGSSE 383505)."""
    import genera as G
    base = {"id": "prova", "inizio": "2026-12-17", "fine": "2026-12-17", "settore": "Aereo", "sindacati": "X", "proclamazione": "", "note": "",
            "stato": "in programma", "modalita": "DALLE ORE 10.00 ALLE ORE 18.00", "fonte": "cgsse", "settore_cgsse": "Trasporto aereo",
            "url_dettaglio": "https://www.cgsse.it/x"}
    prove = [("ADR SECURITY", "FIUMICINO", "Locale", "Lazio", "Roma", ["rome-fiumicino"], "Airport: Rome Fiumicino"),
             ("AVIATION SERVICES", "FIUMICINO, CIAMPINO", "Locale", "Lazio", "Roma", ["rome-fiumicino", "rome-ciampino"], None),
             ("ENAV", "ROMA", "Locale", "Lazio", "Roma", ["rome-fiumicino", "rome-ciampino"], None),
             ("AIRPORT HANDLING", "MILANO, VARESE", "Territoriale", "Lombardia", "Tutte", ["milan-malpensa", "milan-linate"], None),
             ("AIREST RETAIL", "TREVISO, VENEZIA", "Territoriale", "Veneto", "Tutte", ["venice", "treviso"], None),
             ("ENAV", "OLBIA", "Locale", "Sardegna", "Sassari", ["olbia"], "Airport: Olbia Costa Smeralda"),
             ("SOGEAAL SPA", "ALGHERO", "Locale", "Sardegna", "Sassari", [], "Airport: Alghero"),
             ("GEASAR", "ALGHERO", "Locale", "Sardegna", "Sassari", [], "Airport: Alghero"),
             ("GEASAR", "OLBIA", "Locale", "Sardegna", "Sassari", ["olbia"], None),
             ("AEROPORTI DI PUGLIA", "BARI", "Locale", "Puglia", "Bari", ["bari"], None),
             ("ENAV, TECHNO SKY", "SICILIA", "Regionale", "Sicilia", "Tutte", ["catania", "palermo"], None),
             ("SACAL GH SPA", "LAMEZIA TERME", "Locale", "Calabria", "Catanzaro", ["lamezia-terme"], None),
             ("AEROPORTO FRIULI VENEZIA GIULIA", "FRIULI VENEZIA GIULIA", "Regionale", "Friuli-Venezia Giulia", "Tutte", ["trieste"], None),
             ("GDA HANDLING", "BRESCIA", "Locale", "Lombardia", "Brescia", [], None)]
    for cat, ambito, ril, reg, prov, atteso, dove in prove:
        v = G.leggi({**base, "categoria": cat, "ambito_cgsse": ambito, "rilevanza": ril, "regione": reg, "provincia": prov})
        if v["aeroporti"] != atteso or (dove and v["dove"] != dove):
            err("abbinamento", f"CGSSE «{cat}» ambito «{ambito}» -> {v['aeroporti']} ({v['dove']}), atteso {atteso}" + (f" ({dove})" if dove else ""))
    # il registro MIT non ha l'ambito: resta la provincia
    v = G.leggi({**base, "fonte": "", "categoria": "PERSONALE SOC. ADR SECURITY", "rilevanza": "Locale", "regione": "Lazio", "provincia": "Roma"})
    if v["aeroporti"] != ["rome-fiumicino", "rome-ciampino"]:
        err("abbinamento", f"registro MIT, provincia di Roma senza scalo -> {v['aeroporti']}, attesi Fiumicino e Ciampino")
    # nomi dei gestori: sciopero nazionale del solo gestore -> solo i suoi scali; gestore con più scali e una provincia -> quello scalo
    mit = [("PERSONALE SOC. SEA", "Nazionale", "Italia", "Tutte", ["milan-malpensa", "milan-linate"]),
           ("PERSONALE SOC. SEA", "Regionale", "Lombardia", "Tutte", ["milan-malpensa", "milan-linate"]),
           ("PERSONALE SOC. SEA PRIME", "Locale", "Lombardia", "Milano", ["milan-linate"]),
           ("PERSONALE SOC. AEROPORTI DI PUGLIA", "Locale", "Puglia", "Brindisi", ["brindisi"]),
           ("PERSONALE SOC. AEROPORTI DI PUGLIA", "Regionale", "Puglia", "Tutte", ["bari", "brindisi"]),
           ("PERSONALE SOC. SAC", "Nazionale", "Italia", "Tutte", ["catania"]),
           ("PERSONALE SOC. SACAL", "Nazionale", "Italia", "Tutte", ["lamezia-terme"]),
           ("PERSONALE SOC. TOSCANA AEROPORTI", "Nazionale", "Italia", "Tutte", ["pisa", "florence"]),
           ("PERSONALE SOC. GESAC", "Nazionale", "Italia", "Tutte", ["naples"]),
           ("PERSONALE SOC. SAVE", "Nazionale", "Italia", "Tutte", ["venice"]),
           ("PERSONALE SOC. SACBO", "Nazionale", "Italia", "Tutte", ["bergamo"]),
           ("PERSONALE SOC. ADR", "Nazionale", "Italia", "Tutte", ["rome-fiumicino", "rome-ciampino"])]
    for cat, ril, reg, prov, atteso in mit:
        v = G.leggi({**base, "fonte": "", "categoria": cat, "rilevanza": ril, "regione": reg, "provincia": prov})
        if v["aeroporti"] != atteso:
            err("abbinamento", f"registro MIT «{cat}» {reg}/{prov} -> {v['aeroporti']}, atteso {atteso}")
    v = G.leggi({**base, "fonte": "", "categoria": "PERSONALE SOC. ENAV", "rilevanza": "Nazionale", "regione": "Italia", "provincia": "Tutte"})
    if len(v["aeroporti"]) != len(G.AEROPORTI):
        err("abbinamento", "sciopero nazionale ENAV: deve riguardare tutti gli aeroporti")
    v = G.leggi({**base, "categoria": "SEA SPA", "ambito_cgsse": "NAZIONALE", "rilevanza": "Nazionale", "regione": "Italia", "provincia": "Tutte"})
    if v["aeroporti"] != ["milan-malpensa", "milan-linate"]:
        err("abbinamento", f"CGSSE «SEA SPA» nazionale -> {v['aeroporti']}, attesi Malpensa e Linate")


# ---------------------------------------------------------------- 7. aeroporti con scheda (27/11/2026)
LUOGHI = carica("luoghi.json")
APT_FILE = carica("aeroporti.json") if (DATI / "aeroporti.json").exists() else {"aeroporti": {}, "letto_il": "", "fonti_comuni": {}}
SCHEDE_APT = APT_FILE["aeroporti"]
SOGLIA_PAROLE = 110


def parola_intera(parola, testo):
    return re.search(r"(?<![A-Z0-9])" + re.escape(parola) + r"(?![A-Z0-9])", testo) is not None


def nominati(categoria):
    """Aeroporti del sito nominati in una «categoria» del registro, rifatto qui senza usare genera.py."""
    up = re.sub(r"FRIULI[\s-]*VENEZIA[\s-]*GIULIA", "FRIULI VG", categoria.upper())
    return {a["slug"] for a in LUOGHI["aeroporti"] if any(parola_intera(p, up) for p in a["parole"])}


def nominato_qui(slug, x):
    """Lo sciopero x nomina l'aeroporto slug e il luogo dichiarato non lo esclude. Rifatto qui senza usare genera.py:
    per le voci della Commissione di garanzia il luogo è l'ambito geografico (ADR Security «FIUMICINO» non è Ciampino),
    per il registro MIT è la provincia quando il nome indica più scali (SEA in provincia di Milano è Linate)."""
    nomi = nominati(x["categoria"])
    if slug not in nomi:
        return False
    apt = {a["slug"]: a for a in LUOGHI["aeroporti"]}
    prov = lambda a: {p.upper() for p in [a.get("provincia", "")] + a.get("province", []) if p}
    if x.get("ambito_cgsse"):
        luoghi_ambito = set()
        for pezzo in [p.strip().upper() for p in x["ambito_cgsse"].split(",") if p.strip()]:
            qui = nominati(pezzo)
            if not qui and not altri_nominati(pezzo):
                qui = {s for s, a in apt.items() if pezzo in prov(a) or a["regione"].upper().replace("-", " ") == pezzo.replace("-", " ")}
            luoghi_ambito |= qui
        return slug in luoghi_ambito if (nomi & luoghi_ambito) else not luoghi_ambito
    if len(nomi) > 1 and x["provincia"].strip().upper() not in ("TUTTE", ""):
        in_prov = {s for s in nomi if x["provincia"].upper() in prov(apt[s])}
        return slug in in_prov if in_prov else True
    return True


def altri_nominati(categoria):
    return any(parola_intera(p, categoria.upper()) for p in LUOGHI["altri_aeroporti"])


def parole_proprie():
    """{pagina: parole proprie} per tutto il sito: parole del <main> (senza riquadro dei partner, briciole, script, stili, icone,
    menu a tendina) fuori da ogni gruppo di 5 parole presente in almeno 3 pagine. Stessa misura del cancello AdSense della rete."""
    import collections
    parole = {}
    for f in sorted(SITO.rglob("*.html")):
        h = f.read_text(encoding="utf-8")
        m = re.search(r"(?s)<main[^>]*>(.*?)</main>", h)
        if not m:
            continue
        c = re.sub(r'(?s)<section class="aff\b.*?</section>', " ", m.group(1))
        c = re.sub(r"(?is)<(nav|script|style|svg|select)\b.*?</\1>", " ", c)
        parole[f.relative_to(SITO).as_posix()] = re.findall(r"\w+", html.unescape(re.sub(r"<[^>]+>", " ", c)).lower())
    quante, gruppi = collections.Counter(), {}
    for rel, w in parole.items():
        gruppi[rel] = [tuple(w[i:i + 5]) for i in range(len(w) - 4)]
        quante.update(set(gruppi[rel]))
    out = {}
    for rel, w in parole.items():
        comune = [False] * len(w)
        for i, g in enumerate(gruppi[rel]):
            if quante[g] >= 3:
                comune[i:i + 5] = [True] * 5
        out[rel] = comune.count(False)
    return out


def controlla_aeroporti(sitemap):
    """Restituisce i percorsi delle pagine controllate (per il controllo dei link interni)."""
    apt = {a["slug"]: a for a in LUOGHI["aeroporti"]}
    n_apt = len(apt)
    vista = {v["id"]: v for v in VISTA["scioperi"]}
    # dati
    for slug, s in SCHEDE_APT.items():
        if slug not in apt:
            err("aeroporti.json", f"{slug}: scheda senza aeroporto in luoghi.json")
            continue
        a = apt[slug]
        for campo in ("gestore", "uff_it", "uff_en", "luogo_it", "luogo_en"):
            if not s.get(campo):
                err("aeroporti.json", f"{slug}: manca {campo}")
        if s.get("classe") not in ("strategico", "interesse nazionale"):
            err("aeroporti.json", f"{slug}: classe ENAC non valida")
        if not s.get("fonti") or any(not f["url"].startswith("https://") for f in s["fonti"]):
            err("aeroporti.json", f"{slug}: fonte mancante o non https")
        if a.get("link") and not link_valido(a["link"]):
            err("luoghi.json", f"{slug}: link «{a['link']}» assente o non valido in link.json")
        if len(s.get("testo_it", [])) != 2 or len(s.get("testo_en", [])) != 2:
            err("aeroporti.json", f"{slug}: servono due paragrafi in italiano e due in inglese")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", APT_FILE.get("letto_il", "")) or APT_FILE["letto_il"] > OGGI:
        err("aeroporti.json", "letto_il mancante o nel futuro")
    # prove fisse sull'abbinamento dei nomi
    prove = [("PERSONALE SOC. ENAV APT BARI", {"bari"}), ("PERSONALE SOC. BARILLA", set()),
             ("PERSONALE SOC. AEROPORTO FRIULI VENEZIA GIULIA", {"trieste"}),
             ("PERSONALE SOC. SICURITALIA IVRI AEROPORTO MARCO POLO DI VENEZIA", {"venice"}),
             ("PERSONALE SOC. AVIATION SERVICES AEROPORTI DI ROMA FIUMICINO E CIAMPINO", {"rome-fiumicino", "rome-ciampino"}),
             ("PERSONALE SOC. AEROPORTI DI PUGLIA", {"bari", "brindisi"}), ("PERSONALE SOC. SAGAT HANDLING", {"turin"}),
             ("PERSONALE SOC. SOGEAAL AEROPORTO DI ALGHERO", set()), ("PERSONALE SOC. GEASAR", {"olbia"}),
             ("PERSONALE SOC. AER TRE AEROPORTO DI TREVISO", {"treviso"}), ("PERSONALE SOC. ENAV", set()),
             # nomi dei gestori (revisione del 27/11/2026): senza, uno sciopero nazionale del solo gestore finiva su tutti gli aeroporti
             ("PERSONALE SOC. SEA", {"milan-malpensa", "milan-linate"}), ("SEA SPA", {"milan-malpensa", "milan-linate"}),
             ("PERSONALE SOC. SACBO", {"bergamo"}), ("PERSONALE SOC. GESAC", {"naples"}), ("SAVE SPA", {"venice"}),
             ("PERSONALE SOC. TOSCANA AEROPORTI", {"pisa", "florence"}), ("PERSONALE SOC. ADR SECURITY", {"rome-fiumicino", "rome-ciampino"}),
             ("PERSONALE SOC. AEROPORTI DI ROMA", {"rome-fiumicino", "rome-ciampino"}), ("PERSONALE SOC. SAC", {"catania"}),
             ("PERSONALE SOC. SAC SERVICE", {"catania"}), ("SACAL SPA", {"lamezia-terme"}), ("SACAL GH SPA", {"lamezia-terme"}),
             ("PERSONALE SOC. S.A.CAL.", {"lamezia-terme"}), ("PERSONALE SOC. SACE", set()), ("PERSONALE SOC. SEAS", set()),
             ("PERSONALE SOC. SAVELLI", set()), ("PERSONALE NAVIGANTE SOC. EASYJET AIRLINES LIMITED", set())]
    for cat, atteso in prove:
        if nominati(cat) != atteso:
            err("abbinamento", f"«{cat}» -> {sorted(nominati(cat))}, atteso {sorted(atteso)}")
    olbia = apt.get("olbia")
    if olbia and ("Sassari" in [olbia.get("provincia")] + olbia.get("province", [])):
        err("luoghi.json", "Olbia non va abbinata alla provincia di Sassari (c'è anche Alghero)")
    # i dati pubblicati (vista.json) seguono i nomi del registro
    for i, s in SCIOPERI.items():
        if s["settore"] != "Aereo" or i not in vista or "CARGO" in s["categoria"].upper():
            continue
        nomi = nominati(s["categoria"])
        if s.get("ambito_cgsse"):  # voci della Commissione di garanzia: l'ambito geografico può restringere (prove fisse in controlla_ambito_cgsse)
            if nomi and not set(vista[i]["aeroporti"]) <= nomi and set(vista[i]["aeroporti"]) & nomi:
                err("vista.json", f"sciopero {i}: aeroporti {sorted(vista[i]['aeroporti'])}, ma il registro nomina {sorted(nomi)}")
            continue
        if nomi and set(vista[i]["aeroporti"]) != nomi:
            err("vista.json", f"sciopero {i}: aeroporti {sorted(vista[i]['aeroporti'])}, ma il registro nomina {sorted(nomi)}")
        if not nomi and altri_nominati(s["categoria"]) and vista[i]["aeroporti"]:
            err("vista.json", f"sciopero {i}: nomina un aeroporto senza pagina ma è attribuito a {vista[i]['aeroporti']}")
    proprie = parole_proprie()
    pagine = []
    home_it = (SITO / "it" / "index.html").read_text(encoding="utf-8")
    home_en = (SITO / "index.html").read_text(encoding="utf-8")
    ind_it = (SITO / "it" / "aeroporti" / "index.html").read_text(encoding="utf-8")
    ind_en = (SITO / "airports" / "index.html").read_text(encoding="utf-8")
    lette = {APT_FILE.get("letto_il", "")}
    for slug, s in SCHEDE_APT.items():
        if slug not in apt:
            continue
        a = apt[slug]
        province = [x for x in [a.get("provincia", "")] + a.get("province", []) if x]
        p_it, p_en = f"it/aeroporti/{a['slug_it']}/", f"airports/{slug}/"
        pagine += [p_it, p_en]
        # indici, home, città, aziende
        for nome, t, href in (("it/aeroporti/", ind_it, f'href="{a["slug_it"]}/"'), ("airports/", ind_en, f'href="{slug}/"'),
                              ("it/", home_it, f'href="/it/aeroporti/{a["slug_it"]}/"'), ("", home_en, f'href="airports/{slug}/"')):
            if href not in t:
                err(nome or "/", f"manca il link all'aeroporto {slug}")
        for c in LUOGHI["citta_it"]:
            if slug in c["aeroporti"]:
                t = (SITO / "it" / c["slug"] / "index.html").read_text(encoding="utf-8")
                if f'href="/it/aeroporti/{a["slug_it"]}/"' not in t:
                    err(f"it/{c['slug']}/", f"manca il link all'aeroporto {slug}")
                for az in AZ.AZIENDE:
                    if c["slug"] in az["citta"]:
                        t = (SITO / "it" / az["pagina"] / "index.html").read_text(encoding="utf-8")
                        if f'href="/it/aeroporti/{a["slug_it"]}/"' not in t:
                            err(f"it/{az['pagina']}/", f"manca il link all'aeroporto {slug}")
        for c in LUOGHI["citta"]:
            if slug in c["aeroporti"]:
                t = (SITO / c["slug"] / "index.html").read_text(encoding="utf-8")
                if f'href="../airports/{slug}/"' not in t:
                    err(f"{c['slug']}/", f"manca il link all'aeroporto {slug}")
        # attesi dai dati
        attesi_prossimi = {i for i, v in vista.items() if slug in v["aeroporti"] and in_arrivo(v)}
        nominato_prossimi = {i for i, x in SCIOPERI.items() if x["settore"] == "Aereo" and nominato_qui(slug, x) and in_arrivo(x)
                             and "CARGO" not in x["categoria"].upper()}
        nominato_passati = {i for i, x in SCIOPERI.items() if x["settore"] == "Aereo" and nominato_qui(slug, x) and x["fine"] < OGGI
                            and "CARGO" not in x["categoria"].upper()}
        for percorso, lingua, altra in ((p_it, "it", p_en), (p_en, "en", p_it)):
            testo = leggi_pagina(percorso)
            if not testo:
                continue
            controlli_comuni(percorso, testo, sitemap, lingua)
            for hl, dest in (("it", p_it), ("en", p_en)):
                if f'<link rel="alternate" hreflang="{hl}" href="{URL_SITO}/{dest}">' not in testo:
                    err(percorso, f"hreflang {hl} mancante o sbagliato")
            titolo = html.unescape(re.search(r"<title>(.*?)</title>", testo).group(1))
            nome = a["nome_it"] if lingua == "it" else a["nome"]
            if nome not in titolo or f"({a['iata']})" not in titolo:
                err(percorso, "il titolo non porta nome e codice dell'aeroporto")
            h = corpo(testo)
            visibile = piano(h)
            fissi = orari(" ".join(s["testo_it"] + s["testo_en"])) | {"7:00", "10:00", "18:00", "21:00"}
            riquadri = {(GENERATO + timedelta(days=1)).isoformat(), (GENERATO + timedelta(days=6)).isoformat()}  # riquadri oggi / domani / 7 giorni
            controlla_contenuto(percorso, testo, date_extra=lette | riquadri | date_in(" ".join(s["testo_it"] + s["testo_en"])),
                                           orari_extra=fissi, link_extra=[f["url"] for f in s["fonti"]] + [v["url"] for v in APT_FILE["fonti_comuni"].values()])
            # prossimi scioperi = dati pubblicati
            m = re.search(r'(?s)<div class="lista"[^>]*data-filtro="airport:' + re.escape(slug) + r'"[^>]*>(.*?)</div>\s*(?:<section|<div class="ad-slot"|<h2)', h)
            in_lista = set(re.findall(r'<article class="sc[^"]*" id="s([^"]+)"', m.group(1))) if m else set()
            if not m:
                err(percorso, "manca l'elenco dei prossimi scioperi dell'aeroporto")
            if in_lista != attesi_prossimi:
                err(percorso, f"prossimi scioperi diversi dai dati: in più {sorted(in_lista - attesi_prossimi)}, mancano {sorted(attesi_prossimi - in_lista)}")
            for i in sorted(nominato_prossimi - in_lista):
                err(percorso, f"lo sciopero {i} nomina l'aeroporto nel registro ma non è nell'elenco")
            # storico = scioperi passati che riguardano l'aeroporto in particolare
            ms = re.search(r'(?s)<ul class="apt-storico">(.*?)</ul>', h)
            storico = set(re.findall(r'<li data-sid="([^"]+)"', ms.group(1))) if ms else set()
            for i in sorted(storico):
                x = SCIOPERI.get(i)
                if not x:
                    continue  # già segnalato da controlla_contenuto
                if x["fine"] >= OGGI:
                    err(percorso, f"storico: lo sciopero {i} non è passato")
                qui = slug in nominati(x["categoria"]) or (x["regione"] == a["regione"] and (
                    x["provincia"].strip().upper() in ("TUTTE", "") or x["provincia"] in province))
                if not qui:
                    err(percorso, f"storico: lo sciopero {i} non nomina l'aeroporto e non è della sua regione o provincia")
                if nazionale(x) and slug not in nominati(x["categoria"]):
                    err(percorso, f"storico: lo sciopero {i} è nazionale e non nomina l'aeroporto")
                if not date_in(piano(re.search(rf'(?s)<li data-sid="{re.escape(i)}"[^>]*>(.*?)</li>', ms.group(1)).group(1))):
                    err(percorso, f"storico: la riga {i} non ha la data")
            for i in sorted(nominato_passati - storico):
                err(percorso, f"storico: manca lo sciopero {i}, che nel registro nomina l'aeroporto")
            if not storico and not re.search(r"nessuno sciopero già passato ha riguardato|no past strike has concerned", visibile):
                err(percorso, "storico vuoto senza la frase che lo dice")
            # scheda: gestore, fonti, data di lettura, sito ufficiale
            gestore = s.get("gestore_en", s["gestore"]) if lingua == "en" else s["gestore"]
            if f'<td>{html.escape(gestore, quote=False)}</td>' not in h:
                err(percorso, "manca il gestore dei dati")
            for f in s["fonti"]:
                if f'href="{html.escape(f["url"])}"' not in h:
                    err(percorso, f"manca il link alla fonte {f['url']}")
            giorno = int(APT_FILE["letto_il"][8:])
            if not re.search(rf"(Lette il|Read on) {giorno} ", visibile):
                err(percorso, "manca la data di lettura delle fonti")
            u = link_valido(a["link"]) if a.get("link") else None
            if u and f'href="{html.escape(u)}"' not in h:
                err(percorso, "manca il link al sito ufficiale dell'aeroporto")
            if bool(s["isola"]) != bool(re.search(r"su un'isola|on an island", visibile)):
                err(percorso, "regola del collegamento con le isole: presente o assente contro i dati")
            n = proprie.get(percorso + "index.html", 0)
            if n < SOGLIA_PAROLE:
                err(percorso, f"{n} parole proprie: sotto la soglia di {SOGLIA_PAROLE}")
            if "data-ad" in h and n < SOGLIA_PAROLE:
                err(percorso, "pubblicità su una pagina sotto la soglia")
    # nessuna pagina aeroporto fuori dai dati, e gli altri aeroporti restano tutti
    for cartella, chiave in ((SITO / "it" / "aeroporti", "slug_it"), (SITO / "airports", "slug")):
        presenti = {p.name for p in cartella.iterdir() if p.is_dir()}
        attese = {a[chiave] for a in LUOGHI["aeroporti"]}
        if presenti != attese:
            err(cartella.relative_to(SITO).as_posix() + "/", f"pagine aeroporto diverse dai dati: {sorted(presenti ^ attese)}")
    if n_apt != len({a["iata"] for a in LUOGHI["aeroporti"]}):
        err("luoghi.json", "codici IATA doppi")
    return pagine, proprie


def firma_attesa(finestra, filtri):
    """Come firma() nel JS, sui dati di vista.json (gli stessi incorporati nelle pagine, nello stesso ordine)."""
    pezzi = []
    for f in filtri.split(","):
        tipo, _, val = f.partition(":")
        lista = []
        for v in VISTA["scioperi"]:
            if finestra.startswith("day:"):
                if not (v["inizio"] <= finestra[4:] <= v["fine"]):
                    continue
            elif v["fine"] < OGGI or v["stato"] == "concluso":
                continue
            if (tipo == "az" and val not in v["az"]) or (tipo == "azgen" and val not in v["az_gen"]):
                continue
            lista.append(v)
        pezzi.append(AZ.firma(lista))
    return "#".join(pezzi)


def controlla_risposta(percorso, testo):
    m = re.search(r'<section class="card risposta[^"]*"([^>]*)>', testo)
    if not m:
        err(percorso, "manca il riquadro di risposta")
        return None, ""
    attr = dict(re.findall(r'data-([a-z-]+)="([^"]*)"', m.group(1)))
    # tutte le guardie della pagina (risposta, avvisi delle aziende): impronta uguale a quella che il JS ricalcola
    for firma, fin, fil in re.findall(r'data-firma="([^"]*)" data-fin="([^"]*)" data-fil="([^"]*)"', testo):
        if html.unescape(firma) != firma_attesa(fin, fil):
            err(percorso, f"data-firma ({fin}, {fil}) diversa da quella che il JS calcola sui dati incorporati")
    if "firma" not in attr and attr.get("risposta") != "concluso":
        err(percorso, "risposta senza data-firma")
    sezione = re.search(r'(?s)<section class="card risposta.*?</section>', testo).group(0)
    return attr, sezione


def controlla_azienda(a, sitemap):
    percorso = f"it/{a['pagina']}/"
    testo = leggi_pagina(percorso)
    if testo is None:
        return
    controlli_comuni(percorso, testo, sitemap, "it")
    controlla_contenuto(percorso, testo)
    if f"Sciopero {a['nome_pagina']}" not in html.unescape(re.search(r"<title>(.*?)</title>", testo).group(1)):
        err(percorso, "il titolo non comincia con «Sciopero <azienda>»")
    primo = link_valido(a["link"][0]["chiave"])
    if primo and f'href="{html.escape(primo)}"' not in corpo(testo):
        err(percorso, "manca il link alla pagina ufficiale dell'azienda")
    attr, sezione = controlla_risposta(percorso, testo)
    if attr is None:
        return
    nominati = sorted((s for s in SCIOPERI.values() if a["slug"] in AZ.nominate(s) and in_arrivo(s) and attivo(s)),
                      key=lambda s: s["inizio"])
    larghi = [v for v in VISTA["scioperi"] if a["slug"] in v["az_gen"] and in_arrivo(v) and attivo(v)]
    tipo = attr.get("risposta")
    atteso = "si" if nominati else "generale" if larghi else "no"
    if tipo != atteso:
        err(percorso, f"la risposta dice «{tipo}» ma i dati dicono «{atteso}»")
    vale = re.search(r"(?s)<div data-vale>(.*?)</div>", sezione)
    t = piano(vale.group(1)) if vale else ""
    if atteso == "si":
        if AZ_lunga(nominati[0]["inizio"]) not in t and nominati[0]["inizio"] > OGGI:
            err(percorso, f"la risposta non indica il primo sciopero in elenco ({nominati[0]['inizio']})")
        mostrati = re.findall(r'<li data-sid="([^"]+)"', vale.group(1))
        for i in mostrati:
            if i in SCIOPERI and a["slug"] not in AZ.nominate(SCIOPERI[i]):
                err(percorso, f"sciopero {i} dato come sciopero dell'azienda, ma il registro non la nomina")
    else:
        if not re.search(r"Nessuno sciopero (proclamato solo|annunciato) per", t):
            err(percorso, "manca la frase «nessuno sciopero ...»")
        if f"nei prossimi {AZ.GIORNI_AVANTI} giorni" not in t or AZ_lunga(LIMITE) not in t:
            err(percorso, "la frase «nessuno sciopero» non dice il periodo (30 giorni, con la data limite)")
    for i in re.findall(r'<li data-sid="([^"]+)"', vale.group(1) if vale else ""):
        if i in SCIOPERI and not in_arrivo(SCIOPERI[i]):
            err(percorso, f"la risposta cita lo sciopero {i}, che è già passato")
    # storico: solo scioperi passati in cui il registro nomina l'azienda
    for i in re.findall(r'<tr data-sid="([^"]+)"', testo):
        if i in SCIOPERI and (a["slug"] not in AZ.nominate(SCIOPERI[i]) or in_arrivo(SCIOPERI[i])):
            err(percorso, f"storico: lo sciopero {i} non è uno sciopero passato dell'azienda")


def AZ_lunga(iso):
    x = date.fromisoformat(iso)
    giorni = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
    return f"{giorni[x.weekday()]} {x.day} {MESI_IT[x.month - 1]} {x.year}"


def controlla_giorno(iso, lingua, sitemap):
    percorso = f"it/{AZ.slug_data_it(iso)}/" if lingua == "it" else f"{AZ.slug_data_en(iso)}/"
    testo = leggi_pagina(percorso)
    if testo is None:
        return
    controlli_comuni(percorso, testo, sitemap, lingua)
    ids = controlla_contenuto(percorso, testo, date_extra=[iso])
    altra = f"{AZ.slug_data_en(iso)}/" if lingua == "it" else f"it/{AZ.slug_data_it(iso)}/"
    if f'hreflang="{"en" if lingua == "it" else "it"}" href="{URL_SITO}/{altra}"' not in testo:
        err(percorso, "manca hreflang verso l'altra lingua")
    naz = [s for s in SCIOPERI.values() if s["inizio"] == iso and nazionale(s) and (s["id"] not in VOCI or AZ.nazionale_passeggeri(VOCI[s["id"]]))]
    if not naz:
        err(percorso, "pagina per un giorno senza sciopero nazionale nei dati")
        return
    for s in naz:
        if s["id"] not in ids:
            err(percorso, f"lo sciopero nazionale {s['id']} del giorno non è mostrato")
    for i in ids:
        if not (SCIOPERI[i]["inizio"] <= iso <= SCIOPERI[i]["fine"]):
            err(percorso, f"lo sciopero {i} non è di questo giorno")
    attr, sezione = controlla_risposta(percorso, testo)
    if attr is None:
        return
    atteso = "concluso" if iso < OGGI else "si" if any(attivo(s) for s in naz) else "revocato"
    if attr.get("risposta") != atteso:
        err(percorso, f"la risposta dice «{attr.get('risposta')}» ma i dati dicono «{atteso}»")
    if attr.get("giorno-pagina") != iso:
        err(percorso, "data-giorno-pagina diversa dalla data dell'indirizzo")
    titolo = html.unescape(re.search(r"<title>(.*?)</title>", testo).group(1))
    h1 = piano(re.search(r"(?s)<h1>(.*?)</h1>", testo).group(1))
    if date_in(titolo) != {iso} or date_in(h1) != {iso}:
        err(percorso, "titolo o h1 con una data diversa da quella della pagina")
    generale = any(s["settore"] in ("Generale", "Plurisettoriale") for s in naz)
    if re.search(r"generale|general strike", titolo, re.I) and not generale:
        err(percorso, "il titolo dice «sciopero generale» ma nei dati non c'è uno sciopero generale nazionale quel giorno")


def controlla_rete():
    """Rilegge le pagine ufficiali e cerca le citazioni (richieste normali, nessun aggiramento dei blocchi)."""
    def norm(t):
        t = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", t)
        t = html.unescape(re.sub(r"<[^>]+>", " ", t)).replace("’", "'").replace("\xa0", " ")
        return re.sub(r" ([,.;:])", r"\1", re.sub(r"\s+", " ", t))
    for f in AZ.FASCE:
        if f["data"] and f["data"] < OGGI:
            continue
        try:
            req = urllib.request.Request(f["url"], headers={"User-Agent": "Mozilla/5.0 (compatible; site-link-check)", "Accept": "*/*"})
            pagina = norm(urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace"))
        except Exception as e:  # noqa: BLE001
            avvisi.append(f"fasce.json: {f['url']} non letta ({e}): rileggere a mano")
            continue
        for c in f["citazioni"]:
            if norm(c["testo"]) not in pagina:
                err("fasce.json", f"{f['azienda']} {f['data']}: la pagina ufficiale non contiene più «{c['testo'][:70]}»")


def main():
    controlla_dati()
    controlla_lettura()
    controlla_ambito_cgsse()
    sitemap = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    # indice
    indice = leggi_pagina("it/aziende/")
    if indice:
        controlli_comuni("it/aziende/", indice, sitemap, "it")
        controlla_contenuto("it/aziende/", indice)
        for a in AZ.AZIENDE:
            if f'href="/it/{a["pagina"]}/"' not in indice:
                err("it/aziende/", f"manca il link a {a['pagina']}")
    for a in AZ.AZIENDE:
        controlla_azienda(a, sitemap)
    # giorni: pagine attese (dai dati) e pagine presenti
    attesi = set(AZ.date_nazionali(VISTA["scioperi"], GENERATO))
    presenti_it = {AZ.data_da_slug_it(p.name) for p in (SITO / "it").iterdir() if p.is_dir() and AZ.data_da_slug_it(p.name)}
    presenti_en = {AZ.data_da_slug_en(p.name) for p in SITO.iterdir() if p.is_dir() and AZ.data_da_slug_en(p.name)}
    for iso in sorted(attesi - presenti_it):
        err("it/", f"manca la pagina del giorno {iso}")
    for iso in sorted(attesi - presenti_en):
        err("/", f"manca la pagina inglese del giorno {iso}")
    if presenti_it != presenti_en:
        err("/", f"pagine per data diverse tra italiano e inglese: {sorted(presenti_it ^ presenti_en)}")
    for iso in sorted(presenti_it):
        controlla_giorno(iso, "it", sitemap)
    for iso in sorted(presenti_en):
        controlla_giorno(iso, "en", sitemap)
    pagine_apt, proprie = controlla_aeroporti(sitemap)
    # link interni: ogni pagina nuova è collegata da almeno un'altra pagina, e i suoi link interni esistono
    nuove = pagine_apt + ["it/aziende/"] + [f"it/{a['pagina']}/" for a in AZ.AZIENDE] + [f"it/{AZ.slug_data_it(i)}/" for i in presenti_it] \
        + [f"{AZ.slug_data_en(i)}/" for i in presenti_en]
    entranti = {p: 0 for p in nuove}
    for f in SITO.rglob("*.html"):
        rel = f.relative_to(SITO).as_posix()
        t = re.sub(r"(?is)<script\b.*?</script>", " ", f.read_text(encoding="utf-8"))
        cartella = (URL_SITO + "/" + rel).rsplit("/", 1)[0] + "/"
        for href in set(re.findall(r'<a [^>]*href="([^"#]+)', t)):
            if href.startswith(("http", "mailto:")):
                continue
            dest = urlparse(urljoin(cartella, href)).path.lstrip("/")
            pagina_rel = rel[:-10] if rel.endswith("index.html") else rel
            if dest in entranti and dest != pagina_rel:
                entranti[dest] += 1
            if pagina_rel in entranti:
                bersaglio = SITO / dest / "index.html" if (dest.endswith("/") or dest == "") else SITO / dest
                if not bersaglio.exists():
                    err(pagina_rel, f"link interno rotto: {href}")
    for p, n in entranti.items():
        if n == 0:
            err(p, "nessun link interno da altre pagine")
    for a in AZ.AZIENDE:   # dalle città e dagli aeroporti
        for c in a["citta"]:
            t = (SITO / "it" / c / "index.html").read_text(encoding="utf-8")
            if f'href="/it/{a["pagina"]}/"' not in t:
                err(f"it/{c}/", f"manca il link a {a['pagina']}")
    home = (SITO / "it" / "index.html").read_text(encoding="utf-8")
    for iso in sorted(i for i in attesi if i >= OGGI):
        if f'href="/it/{AZ.slug_data_it(iso)}/"' not in home:
            err("it/", f"la home non collega il giorno {iso}")
    if "--rete" in sys.argv:
        controlla_rete()
    for a in avvisi:
        print("AVVISO:", a)
    for e in errori:
        print("ERRORE:", e)
    print(f"verifica italystrikes: {len(AZ.AZIENDE)} pagine azienda, {len(presenti_it)} giorni (it) + {len(presenti_en)} (en), "
          f"{len(AZ.FASCE)} fonti di fasce; {len(pagine_apt)} pagine aeroporto nuove (parole proprie da "
          f"{min((proprie.get(p + 'index.html', 0) for p in pagine_apt), default=0)} a {max((proprie.get(p + 'index.html', 0) for p in pagine_apt), default=0)}); "
          f"{len(errori)} errori, {len(avvisi)} avvisi.")
    sys.exit(1 if errori else 0)


if __name__ == "__main__":
    main()
