#!/usr/bin/env python3
"""Sonda giornaliera per il test delle fonti "Passi alpini aperti oggi?" (15/10-15/11/2026).

Legge le fonti ufficiali (o quasi ufficiali) di 40 passi alpini e aggiunge una riga per
ogni coppia (passo, fonte) a registro.jsonl, nella stessa cartella dello script.

Uso (dalla radice del repository):
    python3 studio-business/intelaiatura/passi-test/sonda.py            # lettura + registro
    python3 studio-business/intelaiatura/passi-test/sonda.py --prova    # lettura senza scrivere
    python3 studio-business/intelaiatura/passi-test/sonda.py --riepilogo  # primo giorno "chiuso" per passo

Solo libreria standard. Ogni fonte ha il suo timeout e il suo try/except: se una fonte cade,
i suoi passi finiscono come "unknown" con il motivo nell'estratto, e le altre vanno avanti.
Nel registro non si salva HTML: solo un estratto breve (max 240 caratteri).
"""
import concurrent.futures as cf
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

try:
    from zoneinfo import ZoneInfo
    ROMA = ZoneInfo("Europe/Rome")
except Exception:  # pragma: no cover
    ROMA = dt.timezone(dt.timedelta(hours=1))

QUI = os.path.dirname(os.path.abspath(__file__))
REGISTRO = os.path.join(QUI, "registro.jsonl")
UA = "Mozilla/5.0 (X11; Linux x86_64) passi-test/1.0 (test fonti, 1 lettura al giorno)"
TIMEOUT = 25
MAX_SNIP = 240

# --------------------------------------------------------------------------------------
# Fonti
# --------------------------------------------------------------------------------------
URL_BZ_PASSI = "https://static-verkehr.provinz.bz.it/publications/rss/berg-und-passstrassen.xml"
URL_BZ_LAGE = "https://static-verkehr.provinz.bz.it/publications/rss/aktuelle-lage.xml"
URL_TCS = "https://www.tcs.ch/fr/tools/inforoute-situation-trafic/cols-en-suisse.php"
URL_PIEMONTE = "https://www.muoversinpiemonte.it/passes"
URL_HA05 = "https://www.inforoute05.fr/ws/geojson/fr/col/TODAY"
URL_SAVOIE_LISTA = "https://savoie-route.fr/api/v1/evenements/carto"
URL_SAVOIE_DETT = "https://savoie-route.fr/api/v1/evenements/allDataCarto"
URL_AM06 = "https://www.inforoutes06.fr/mod_turbolead/mod/inforoute/index.php?action=374&protect=1"
URL_GROSSGLOCKNER = "https://www.grossglockner.at/de"
URL_TIMMELSJOCH = "https://www.timmelsjoch.com/"
URL_CCISS = ("https://www.cciss.it/web/cciss/situazione-della-viabilita?p_p_id=2_WAR_ccissservizimapsportlet"
             "&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_cacheability=cacheLevelPage"
             "&p_p_col_id=column-2&p_p_col_pos=3&p_p_col_count=4"
             "&_2_WAR_ccissservizimapsportlet_so=44.0%2C6.6&_2_WAR_ccissservizimapsportlet_ne=47.1%2C13.0"
             "&_2_WAR_ccissservizimapsportlet_z=9")

# Livello della fonte: "ente" = ente pubblico (Provincia, Regione, Dipartimento, Ministero/ANAS);
# "gestore" = società che gestisce la strada a pedaggio; "club" = TCS (Touring Club Svizzero).
FONTI = {
    "bz": ("Provincia autonoma di Bolzano, Centrale viabilità (RSS passi)", "ente", URL_BZ_PASSI),
    "tcs": ("TCS, Cols en Suisse", "club", URL_TCS),
    "piemonte": ("Regione Piemonte / 5T, Muoversi in Piemonte", "ente", URL_PIEMONTE),
    "ha05": ("Département Hautes-Alpes, Inforoute 05", "ente", URL_HA05),
    "savoie": ("Département de la Savoie, Savoie-Route", "ente", "https://savoie-route.fr/"),
    "am06": ("Département Alpes-Maritimes / Métropole NCA, Inforoutes 06", "ente", URL_AM06),
    "grohag": ("Großglockner Hochalpenstraßen AG (società del Land)", "gestore", URL_GROSSGLOCKNER),
    "timmelsjoch": ("Timmelsjoch Hochalpenstraße AG", "gestore", URL_TIMMELSJOCH),
    "cciss": ("CCISS (Ministero Infrastrutture), eventi ANAS/Province: solo chiusure", "ente", "https://www.cciss.it/web/cciss/situazione-della-viabilita"),
}

# --------------------------------------------------------------------------------------
# I 40 passi: id -> (nome, paese, [(fonte, chiave), ...]); la prima fonte è la principale.
# chiave: testo da cercare nella fonte (regex, minuscole) oppure regola CCISS:
# (codice strada, località sulla strada, nome del passo): un evento conta se è sulla strada
# e cita una località del passo, oppure se cita il nome del passo.
# --------------------------------------------------------------------------------------
PASSI = {
    "stelvio": ("Passo dello Stelvio / Stilfserjoch", "IT", [("bz", r"stilfserjoch"), ("cciss", ("SS38", r"bormio|trafoi|cantoniera|passo|giogo|umbrail|confine", r"passo dello stelvio|stilfserjoch"))]),
    "gotthard": ("Passo del San Gottardo / Gotthardpass", "CH", [("tcs", "gothard")]),
    "furka": ("Passo della Furka / Furkapass", "CH", [("tcs", "furka")]),
    "grossglockner": ("Großglockner Hochalpenstraße", "AT", [("grohag", "grossglockner")]),
    "bernina": ("Passo del Bernina", "CH", [("tcs", "bernina")]),
    "gardena": ("Passo Gardena / Grödnerjoch", "IT", [("bz", r"grödnerjoch")]),
    "rombo": ("Passo del Rombo / Timmelsjoch", "IT/AT", [("bz", r"timmelsjoch"), ("timmelsjoch", "timmelsjoch")]),
    "gavia": ("Passo di Gavia", "IT", [("cciss", ("SS300", r".*", r"gavia"))]),
    "giau": ("Passo Giau", "IT", [("cciss", ("SP638", r".*", r"giau"))]),
    "gransanbernardo": ("Colle del Gran San Bernardo / Grand-St-Bernard", "IT/CH", [("tcs", "grand-st-bernard"), ("cciss", ("SS27", r"colle|confine|rh[eé]my|etroubles", r"colle del gran san bernardo"))]),
    "iseran": ("Col de l'Iseran", "FR", [("savoie", r"col de l'iseran")]),
    "sanbernardino": ("Passo del San Bernardino", "CH", [("tcs", "san bernardino")]),
    "galibier": ("Col du Galibier", "FR", [("savoie", r"^col du galibier"), ("ha05", r"col du galibier")]),
    "spluga": ("Passo dello Spluga / Splügenpass", "IT/CH", [("tcs", "splügen"), ("cciss", ("SS36", r"madesimo|campodolcino|pianazzo|isola|confine|passo", r"passo dello spluga"))]),
    "susten": ("Passo del Susten / Sustenpass", "CH", [("tcs", "susten")]),
    "rolle": ("Passo Rolle", "IT", [("cciss", ("SS50", r"rolle|san martino di castrozza|paneveggio", r"passo rolle"))]),
    "grimsel": ("Passo del Grimsel / Grimselpass", "CH", [("tcs", "grimsel")]),
    "sella": ("Passo Sella / Sellajoch", "IT", [("bz", r"sellajoch")]),
    "fedaia": ("Passo Fedaia", "IT", [("cciss", ("SS641", r".*", r"fedaia"))]),
    "agnello": ("Colle dell'Agnello / Col Agnel", "IT/FR", [("piemonte", r"agnello"), ("ha05", r"col agnel")]),
    "falzarego": ("Passo Falzarego", "IT", [("bz", r"falzaregopass"), ("cciss", ("SR48|SS48", r"falzarego", r"falzarego"))]),
    "valparola": ("Passo Valparola", "IT", [("bz", r"valparolapass")]),
    "foscagno": ("Passo del Foscagno", "IT", [("cciss", ("SS301", r".*", r"foscagno"))]),
    "nivolet": ("Colle del Nivolet", "IT", [("piemonte", r"nivolet")]),
    "pordoi": ("Passo Pordoi / Pordoijoch", "IT", [("bz", r"pordoijoch")]),
    "giovo": ("Passo del Giovo / Jaufenpass", "IT", [("bz", r"jaufenpass")]),
    "sanpellegrino": ("Passo San Pellegrino", "IT", [("cciss", ("SS346", r".*", r"san pellegrino"))]),
    "moncenisio": ("Colle del Moncenisio / Col du Mont-Cenis", "FR/IT", [("savoie", r"col du mont cenis"), ("piemonte", r"moncenisio")]),
    "nufenen": ("Passo della Novena / Nufenenpass", "CH", [("tcs", "nufenen")]),
    "fluela": ("Passo del Flüela / Flüelapass", "CH", [("tcs", "flüela")]),
    "bonette": ("Col de la Bonette", "FR", [("am06", r"bonette")]),
    "staller": ("Passo Stalle / Staller Sattel", "IT/AT", [("bz", r"staller sattel")]),
    "mortirolo": ("Passo del Mortirolo", "IT", [("cciss", ("", r"", r"mortirolo"))]),
    "manghen": ("Passo Manghen", "IT", [("cciss", ("SP31", r"manghen|baessa|ponte stue|telve|molina", r"manghen"))]),
    "fauniera": ("Colle Fauniera (dei Morti)", "IT", [("cciss", ("", r"", r"fauniera|colle dei morti"))]),
    "albula": ("Passo dell'Albula / Albulapass", "CH", [("tcs", "albula")]),
    "madeleine": ("Col de la Madeleine", "FR", [("savoie", r"^col de la madeleine$")]),
    "umbrail": ("Passo Umbrail / Pass Umbrail", "CH/IT", [("tcs", "umbrail")]),
    "piccolosanbernardo": ("Colle del Piccolo San Bernardo / Col du Petit-Saint-Bernard", "IT/FR", [("savoie", r"petit saint bernard"), ("cciss", ("SS26", r"la thuile|confine|colle", r"piccolo san bernardo"))]),
    "lombarda": ("Colle della Lombarda / Col de la Lombarde", "IT/FR", [("piemonte", r"lombarda"), ("am06", r"lombarde")]),
}

MESI = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6, "luglio": 7,
        "agosto": 8, "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12}


# --------------------------------------------------------------------------------------
# Utilità
# --------------------------------------------------------------------------------------
def scarica(url, dati=None, tipo=None, timeout=TIMEOUT):
    intest = {"User-Agent": UA, "Accept-Language": "it,de;q=0.8,fr;q=0.7,en;q=0.5"}
    corpo = None
    if dati is not None:
        corpo = json.dumps(dati).encode("utf-8")
        intest["Content-Type"] = "application/json"
    if tipo:
        intest["Accept"] = tipo
    req = urllib.request.Request(url, data=corpo, headers=intest, method="POST" if corpo else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def testo(s):
    s = re.sub(r"<script.*?</script>|<style.*?</style>", " ", s, flags=re.S | re.I)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"\s+", " ", s).strip()


def corto(s):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s[:MAX_SNIP]


def esito(stato, estratto, base="esplicito", http=None):
    return {"status": stato, "raw_snippet": corto(estratto), "basis": base, "http": http}


# --------------------------------------------------------------------------------------
# Lettori: ognuno riceve {chiave: pass_id} e restituisce {pass_id: esito}
# --------------------------------------------------------------------------------------
CHIUSO_DE = re.compile(r"wintersperre|gesperrt|sperre|geschlossen", re.I)
NON_TOTALE_DE = re.compile(r"nachtsperre|zeitweilig|bis zu \d+ minuten|einbahn|von \d\d:\d\d bis \d\d:\d\d uhr|^ab ", re.I)
APERTO_DE = re.compile(r"keine beschränkungen|geöffnet|befahrbar|fahrverbot|verbot für|einbahn", re.I)


def leggi_bz(chiavi):
    st, xml = scarica(URL_BZ_PASSI)
    voci = []
    for it in ET.fromstring(xml.encode("utf-8")).iter("item"):
        voci.append(((it.findtext("title") or "").strip(), (it.findtext("description") or "").strip(), it.findtext("pubDate") or ""))
    try:  # avvisi del giorno: servono a vedere una "Wintersperre" pubblicata solo lì
        _, xml2 = scarica(URL_BZ_LAGE)
        lage = [((i.findtext("title") or "").strip(), (i.findtext("description") or "").strip())
                for i in ET.fromstring(xml2.encode("utf-8")).iter("item")]
    except Exception:
        lage = []
    out = {}
    for chiave, pid in chiavi.items():
        trov = [v for v in voci if re.search(chiave, v[0], re.I)]
        if not trov:
            out[pid] = esito("unknown", "voce del passo non presente nel feed", http=st)
            continue
        tit, desc, data = trov[0]
        estr = f"{tit}: {desc} [{data[5:16]}]"
        extra = [d for t, d in lage if re.search(chiave, t, re.I) and CHIUSO_DE.search(d) and not NON_TOTALE_DE.search(d)]
        if re.search(r"wintersperre", desc, re.I) or (CHIUSO_DE.search(desc) and not NON_TOTALE_DE.search(desc)):
            out[pid] = esito("closed", estr, http=st)
        elif extra:
            out[pid] = esito("closed", f"{tit} (avviso del giorno): {extra[0]}", http=st)
        elif re.search(r"keine beschränkungen|geöffnet|befahrbar", desc, re.I):
            out[pid] = esito("open", estr, http=st)
        elif APERTO_DE.search(desc):
            out[pid] = esito("open", estr, base="implicito (solo limitazioni ai mezzi)", http=st)
        else:
            out[pid] = esito("unknown", estr, http=st)
    return out


def leggi_tcs(chiavi):
    st, pag = scarica(URL_TCS)
    blocchi = {}
    for parte in pag.split('<li class="item" data-search="')[1:]:
        blocchi[parte.split('"', 1)[0].strip().lower()] = parte[:20000]
    out = {}
    for chiave, pid in chiavi.items():
        b = blocchi.get(chiave)
        if b is None:
            out[pid] = esito("unknown", "passo non presente nella pagina TCS", http=st)
            continue
        icona = re.search(r"tcs-icon_status_(\w+)\.svg", b)
        info = re.search(r'status-additional-info">(.*?)<(?:/?br|span)', b, re.S)
        agg = re.search(r"Dernière actualisation\s*:\s*([\d.: ]+)", b)
        frase = testo(info.group(1)) if info else ""
        estr = f"{frase} (agg. {agg.group(1).strip() if agg else '?'}; icona {icona.group(1) if icona else '?'})"
        prima = frase.split(",")[0].lower()
        ic = icona.group(1).lower() if icona else ""
        if re.search(r"\bferm", prima) or ic in ("closed", "close", "fermé", "ferme"):
            out[pid] = esito("closed", estr, http=st)
        elif ic == "open" and re.search(r"\bouvert", prima):
            out[pid] = esito("open", estr, http=st)
        else:
            out[pid] = esito("unknown", estr, http=st)
    return out


def leggi_piemonte(chiavi):
    st, pag = scarica(URL_PIEMONTE)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', pag, re.S)
    dati = json.loads(m.group(1))["props"]["pageProps"]["passData"]
    ora = dt.datetime.now(dt.timezone.utc).timestamp() * 1000
    out = {}
    for chiave, pid in chiavi.items():
        trov = [p for p in dati if re.search(chiave, p.get("name", ""), re.I)]
        if not trov:
            out[pid] = esito("unknown", "colle non presente nei dati", http=st)
            continue
        p = trov[0]
        a, b = p.get("closed_from"), p.get("closed_until")
        f = lambda x: dt.datetime.fromtimestamp(x / 1000, ROMA).strftime("%d/%m/%Y %H:%M") if x else "-"
        estr = f"{p['name']}: closed_from {f(a)} closed_until {f(b)}"
        chiuso = a is not None and a <= ora and (b is None or ora <= b)
        out[pid] = esito("closed" if chiuso else "open", estr, http=st)
    return out


def leggi_ha05(chiavi):
    st, txt = scarica(URL_HA05)
    d = json.loads(txt)
    if isinstance(d, str):
        d = json.loads(d)
    out = {}
    for chiave, pid in chiavi.items():
        trov = [f for f in d.get("features", []) if re.search(chiave, f.get("nomCol", ""), re.I)]
        if not trov:
            out[pid] = esito("unknown", "col non presente", http=st)
            continue
        f = trov[0]
        stato = (f.get("etatCol") or "").upper()
        sit = "; ".join((s.get("title", "") + " " + s.get("content", "")) for s in f.get("situationsIcons", []))
        estr = f"{f.get('nomCol')}: {stato} (generato {d.get('generated')}) {sit}"
        out[pid] = esito({"OUVERT": "open", "FERME": "closed", "FERMÉ": "closed"}.get(stato, "unknown"), estr, http=st)
    return out


def leggi_savoie(chiavi):
    st, txt = scarica(URL_SAVOIE_LISTA, dati={"id": 5})
    lista = json.loads(txt)
    out = {}
    for chiave, pid in chiavi.items():
        trov = [c for c in lista if re.search(chiave, (c.get("FRLabel") or "").lower())]
        if not trov:
            out[pid] = esito("unknown", "col non presente nella lista", http=st)
            continue
        c = trov[0]
        etat_txt = ""
        try:  # dettaglio: testo ufficiale dello stato (OUVERT / FERME ...)
            _, dtxt = scarica(URL_SAVOIE_DETT, dati={"idAll": c["idtInfo"]})
            det = json.loads(dtxt)
            det = det[0] if isinstance(det, list) and det else {}
            etat_txt = (det.get("FREtat") or "").upper()
            maj = det.get("maj", "")
        except Exception as e:
            maj = f"dettaglio non letto: {type(e).__name__}"
        codice = c.get("Etat")
        estr = f"{c.get('FRLabel')}: Etat={codice} ({etat_txt or '-'}), maj {maj}"
        if "FERM" in etat_txt or (not etat_txt and codice == 0):
            out[pid] = esito("closed", estr, http=st)
        elif etat_txt.startswith("OUVERT") and codice == 2:
            out[pid] = esito("open", estr, http=st)
        elif not etat_txt and codice == 2:
            out[pid] = esito("open", estr, base="implicito (codice verde, dettaglio non letto)", http=st)
        else:
            out[pid] = esito("unknown", estr, http=st)
    return out


def leggi_am06(chiavi):
    st, txt = scarica(URL_AM06)
    feats = json.loads(txt).get("features", [])
    cols = [f["properties"] for f in feats
            if (f.get("properties") or {}).get("code") in ("C14 Ouvert", "C14 fermé", "C111", "C112", "fermeture_hivernale")]
    out = {}
    for chiave, pid in chiavi.items():
        trov = [p for p in cols if re.search(chiave, p.get("titre", ""), re.I)]
        if not trov:
            out[pid] = esito("unknown", "col non presente tra i 'cols routiers'", http=st)
            continue
        p = trov[0]
        codice = p.get("code", "")
        estr = f"{codice} | {p.get('titre')} | {testo(p.get('description') or '')[:120]} | {p.get('date')}"
        if codice in ("C14 fermé", "fermeture_hivernale", "C111"):
            out[pid] = esito("closed", estr, http=st)
        elif codice == "C14 Ouvert":
            out[pid] = esito("open", estr, http=st)
        else:
            out[pid] = esito("unknown", estr, http=st)
    return out


def leggi_grohag(chiavi):
    st, pag = scarica(URL_GROSSGLOCKNER)
    t = testo(pag)
    m = re.search(r"Aktueller Status für PKW:\s*(\w+)", t)
    out = {}
    for _, pid in chiavi.items():
        if not m:
            out[pid] = esito("unknown", "frase 'Aktueller Status für PKW' non trovata", http=st)
            continue
        v = m.group(1).lower()
        estr = t[m.start(): m.start() + 200]
        out[pid] = esito("open" if v.startswith("geöffnet") else "closed" if v.startswith(("gesperrt", "geschlossen")) else "unknown", estr, http=st)
    return out


def leggi_timmelsjoch(chiavi):
    st, pag = scarica(URL_TIMMELSJOCH)
    t = testo(pag)
    m = re.search(r"Timmelsjoch Hochalpenstraße (ist|hat)[^.]{0,120}\.", t)
    out = {}
    for _, pid in chiavi.items():
        if not m:
            out[pid] = esito("unknown", "frase di stato non trovata", http=st)
            continue
        f = m.group(0)
        if re.search(r"gesperrt|geschlossen|wintersperre", f, re.I):
            s = "closed"
        elif re.search(r"geöffnet|befahrbar", f, re.I):
            s = "open"
        else:
            s = "unknown"
        out[pid] = esito(s, f, http=st)
    return out


def _inizio_evento(det, adesso):
    """Data di inizio da frasi come 'dalle 21:00 del 12 alle 06:00 del 28 ottobre 2026'."""
    m = re.search(r"dalle (\d{1,2}):(\d{2}) del (\d{1,2})(?: (\w+))?(?: (\d{4}))?", det)
    if not m:
        return None
    hh, mm, gg, mese, anno = m.groups()
    if not mese or mese.lower() not in MESI:
        m2 = re.search(r"alle \d{1,2}:\d{2} del \d{1,2} (\w+)(?: (\d{4}))?", det[m.end():])
        mese = m2.group(1) if m2 else None
        anno = anno or (m2.group(2) if m2 else None)
    if not anno:
        m3 = re.search(r"\b(20\d\d)\b", det)
        anno = m3.group(1) if m3 else str(adesso.year)
    try:
        return dt.datetime(int(anno), MESI[mese.lower()], int(gg), int(hh), int(mm), tzinfo=ROMA)
    except Exception:
        return None


def leggi_cciss(chiavi):
    st, txt = scarica(URL_CCISS, tipo="application/json", timeout=40)
    eventi = json.loads(txt).get("eventiTrafficoList") or []
    adesso = dt.datetime.now(ROMA)
    out = {}
    for (strada, luogo, nome), pid in chiavi.items():
        rilevanti = []
        for e in eventi:
            tit = e.get("titolo") or ""
            det = (e.get("dettaglio") or "").replace("\n", " ")
            tutto = (tit + " " + det).lower()
            codice = re.sub(r"^(?:LS/)?(S[SPR])\s*(\d)", r"\1\2", tit.strip(), flags=re.I)
            sulla_strada = bool(strada) and re.match(r"(%s)(?![0-9A-Za-z])" % strada, codice, re.I) and re.search(luogo, tutto)
            resto = (det[len(tit):] if det.startswith(tit) else det).lower()  # senza il nome della strada
            if not (sulla_strada or re.search(nome, resto)):
                continue
            rilevanti.append((e, det))
        chiusure = []
        for e, det in rilevanti:
            ev = (e.get("evento") or "").lower()
            if "chius" not in ev and "chius" not in det.lower():
                continue
            if "notturna" in ev and "tratto chiuso" not in ev.replace("chiusura notturna", ""):
                continue
            ini = _inizio_evento(det, adesso)
            if ini and ini > adesso:
                continue
            chiusure.append(det)
        if chiusure:
            out[pid] = esito("closed", f"[{len(chiusure)} chiusure] {chiusure[0]}", http=st)
        else:
            nota = f"nessuna chiusura in corso nel feed ({len(rilevanti)} eventi sulla strada)"
            if rilevanti:
                nota += ": " + rilevanti[0][1]
            out[pid] = esito("open", nota, base="implicito (nessuna chiusura segnalata)", http=st)
    return out


LETTORI = {"bz": leggi_bz, "tcs": leggi_tcs, "piemonte": leggi_piemonte, "ha05": leggi_ha05,
           "savoie": leggi_savoie, "am06": leggi_am06, "grohag": leggi_grohag,
           "timmelsjoch": leggi_timmelsjoch, "cciss": leggi_cciss}


def esegui(scrivi=True):
    inizio = dt.datetime.now(dt.timezone.utc)
    per_fonte = {}
    for pid, (_, _, fonti) in PASSI.items():
        for fonte, chiave in fonti:
            per_fonte.setdefault(fonte, {})[chiave] = pid
    risultati = {}
    errori = {}
    ex = cf.ThreadPoolExecutor(max_workers=len(per_fonte))
    fut = {ex.submit(LETTORI[f], ch): f for f, ch in per_fonte.items()}
    try:
        for fu in cf.as_completed(fut, timeout=150):
            f = fut[fu]
            try:
                risultati[f] = fu.result()
            except Exception as e:  # una fonte caduta non ferma le altre
                errori[f] = f"{type(e).__name__}: {str(e)[:150]}"
    except cf.TimeoutError:  # fonte bloccata: si chiude comunque entro i 3 minuti
        for fu, f in fut.items():
            if f not in risultati and f not in errori:
                errori[f] = "tempo scaduto (150 s)"
    ex.shutdown(wait=False, cancel_futures=True)
    oggi = dt.datetime.now(ROMA)
    righe = []
    for pid, (nome, paese, fonti) in PASSI.items():
        for i, (fonte, _) in enumerate(fonti):
            r = (risultati.get(fonte) or {}).get(pid)
            if r is None:
                r = esito("unknown", f"fonte non letta: {errori.get(fonte, 'nessun risultato')}", base="errore")
            righe.append({
                "date": oggi.strftime("%Y-%m-%d"),
                "ts": oggi.strftime("%Y-%m-%dT%H:%M%z"),
                "pass": pid,
                "status": r["status"],
                "basis": r["basis"],
                "raw_snippet": r["raw_snippet"],
                "source": fonte,
                "source_level": FONTI[fonte][1],
                "source_url": FONTI[fonte][2],
                "primary": i == 0,
                "http": r.get("http"),
            })
    if scrivi:
        with open(REGISTRO, "a", encoding="utf-8") as fh:
            for r in righe:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    durata = (dt.datetime.now(dt.timezone.utc) - inizio).total_seconds()
    prim = [r for r in righe if r["primary"]]
    conta = {s: sum(1 for r in prim if r["status"] == s) for s in ("open", "closed", "unknown")}
    print(f"{oggi:%Y-%m-%d %H:%M} | {len(PASSI)} passi, {len(righe)} righe | fonte principale: "
          f"aperti {conta['open']}, chiusi {conta['closed']}, sconosciuti {conta['unknown']} | {durata:.0f} s")
    for f, e in sorted(errori.items()):
        print(f"  FONTE CADUTA {f}: {e}")
    for r in righe:
        segno = "" if r["primary"] else "   (2a fonte)"
        print(f"  {r['pass']:20s} {r['status']:8s} {r['source']:12s}{segno} {r['raw_snippet'][:110]}")
    return righe


def riepilogo():
    """Per ogni passo: primo giorno in cui la fonte principale dice 'closed', e eventuali ritorni a 'open'."""
    if not os.path.exists(REGISTRO):
        print("registro vuoto")
        return
    per = {}
    for riga in open(REGISTRO, encoding="utf-8"):
        try:
            r = json.loads(riga)
        except Exception:
            continue
        per.setdefault((r["pass"], r["source"]), []).append(r)
    for (pid, fonte), rr in sorted(per.items()):
        rr.sort(key=lambda x: x["ts"])
        stati = "".join({"open": "A", "closed": "C", "unknown": "?"}[x["status"]] for x in rr)
        primo = next((x["date"] for x in rr if x["status"] == "closed"), "-")
        print(f"{pid:20s} {fonte:12s} primo 'chiuso': {primo:10s} sequenza: {stati}")


if __name__ == "__main__":
    if "--riepilogo" in sys.argv:
        riepilogo()
    else:
        esegui(scrivi="--prova" not in sys.argv)
    sys.stdout.flush()
    os._exit(0)  # non aspetta eventuali thread rimasti appesi a una fonte lenta
