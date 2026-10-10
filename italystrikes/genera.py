"""Genera il sito statico Italy Strikes Today in italystrikes/sito/ da italystrikes/dati/.

Uso (dalla radice del repository):
    python3 italystrikes/genera.py              # dati/vista.json + tutto il sito
    python3 italystrikes/genera.py --solo-dati  # solo dati/vista.json (aggiornamento giornaliero senza deploy)

Dati: scioperi.json e registro.json (da raccolta/raccogli.py), luoghi.json, operatori.json, link.json (link
ufficiali verificati). Ogni sciopero in pagina porta id MIT, data di proclamazione e link al registro.
Le pagine contengono i dati del giorno di generazione; il JS ricalcola oggi/domani nel browser (ora di Roma)
e scarica dati/vista.json da GitHub se più recente. Nessuna dipendenza esterna.
"""
import json
import os
import re
import shutil
import sys
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

RADICE = Path(__file__).resolve().parent
sys.path.insert(0, str(RADICE))
DATI = RADICE / "dati"
SITO = RADICE / "sito"
URL_SITO = "https://italy-strikes-today.netlify.app"  # cambiare qui se il nome del sito su Netlify è diverso
NOME = "Italy Strikes Today"
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console, proprietà https://italy-strikes-today.netlify.app (non rimuoverla)
# Satelliti (calcolatore codice fiscale, guida multe ZTL): spenti finché Massimiliano non dice sì alla pubblicazione.
# Per vederli in prova senza pubblicarli: ITALYSTRIKES_SATELLITI=1 python3 italystrikes/genera.py (in una copia).
SATELLITI_ATTIVI = True  # sì di Massimiliano il 10/10/2026
# Versione italiana in /it/ (genera_it.py): spenta finché Massimiliano non dice sì alla pubblicazione.
# Anteprima senza pubblicare: ITALYSTRIKES_IT=1 python3 italystrikes/genera.py (in una copia della cartella).
VERSIONE_IT_ATTIVA = True  # sì di Massimiliano il 10/10/2026: esce con la pubblicazione settimanale del 17/10
IMPACT_VERIFICA = "30566286-17ab-476e-b7be-3af44af9c845"  # Impact (programma affiliati Airalo), aggiunto il 10/10/2026: non rimuoverlo
URL_DATI_LIVE = ("https://raw.githubusercontent.com/Massimilianocori/copertine-libri/"
                 "ccr-b7fd6b9e-n096cr/italystrikes/dati/vista.json")
URL_REGISTRO = "https://scioperi.mit.gov.it/mit2/public/scioperi"
ROMA = ZoneInfo("Europe/Rome")
ADESSO = datetime.now(ROMA)
OGGI = ADESSO.date()

MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
        "November", "December"]
MES = [m[:3] for m in MESI]
GG = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
GIORNI = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

scioperi = json.loads((DATI / "scioperi.json").read_text(encoding="utf-8"))
registro = json.loads((DATI / "registro.json").read_text(encoding="utf-8"))
luoghi = json.loads((DATI / "luoghi.json").read_text(encoding="utf-8"))
operatori = json.loads((DATI / "operatori.json").read_text(encoding="utf-8"))
LINK = json.loads((DATI / "link.json").read_text(encoding="utf-8")) if (DATI / "link.json").exists() else {}
AFFILIATI = json.loads((DATI / "affiliati.json").read_text(encoding="utf-8")) if (DATI / "affiliati.json").exists() else {}
CITTA = luoghi["citta"]
CITTA_IT = luoghi.get("citta_it", [])
AEROPORTI = luoghi["aeroporti"]
APT = {a["slug"]: a for a in AEROPORTI}
REG_EN = luoghi["regioni_en"]
PROV_EN = luoghi["province_en"]

SETTORI = {  # slug: (nome, titolo pagina, settore MIT)
    "trains": ("Trains", "Train strikes in Italy", "Ferroviario"),
    "flights": ("Flights and airports", "Flight and airport strikes in Italy", "Aereo"),
    "local-transport": ("Local transport", "Bus, metro and tram strikes in Italy", "Trasporto pubblico locale"),
    "ferries": ("Ferries and ports", "Ferry and port strikes in Italy", "Marittimo"),
    "taxis": ("Taxis", "Taxi strikes in Italy", "Taxi"),
    "general-strikes": ("General strikes", "General strikes in Italy", "Generale"),
    "motorways": ("Motorways", "Motorway and road service strikes in Italy", "Circolazione e sicurezza stradale"),
    "freight": ("Freight", "Freight transport strikes in Italy", "Trasporto merci"),
}
PASSEGGERI = ["trains", "flights", "local-transport", "ferries", "taxis"]
SETTORE_EN = {"Aereo": "air transport", "Ferroviario": "rail", "Trasporto pubblico locale": "local public transport",
              "Marittimo": "ferry and port", "Trasporto merci": "freight", "Taxi": "taxi", "Ncc": "private hire (NCC)",
              "Circolazione e sicurezza stradale": "motorway services", "Generale": "general",
              "Plurisettoriale": "multi-sector", "Elicotteri": "helicopter", "Appalti ferroviari": "rail contractors"}
SETTORE_SLUG = {"Aereo": ["flights"], "Ferroviario": ["trains"], "Appalti ferroviari": ["trains"],
                "Trasporto pubblico locale": ["local-transport"], "Marittimo": ["ferries"], "Trasporto merci": ["freight"],
                "Taxi": ["taxis"], "Ncc": ["taxis"], "Circolazione e sicurezza stradale": ["motorways"]}
RIL_EN = {"Nazionale": "National", "Interregionale": "Interregional", "Regionale": "Regional",
          "Provinciale": "Provincial", "Locale": "Local", "Territoriale": "Territorial", "Aziendale": "Company-level"}
MENZIONI = [  # parole del registro -> settore (per scioperi generali e plurisettoriali)
    (r"FERROVIAR|TRENI\b|MERCI SU ROTAIA", "trains"), (r"\bTPL\b|TRASPORTO PUBBLICO LOCALE", "local-transport"),
    (r"\bAEREO\b|AEROPORT|TRASPORTO AEREO", "flights"), (r"AUTOSTRAD", "motorways"), (r"MARITTIM|PORTUAL", "ferries"),
    (r"\bTAXI\b", "taxis")]
ESCLUSIONI = [(r"TRASPORTO AEREO|\bAEREO\b", "flights"), (r"FERROVIARIO", "trains"),
              (r"TRASPORTO PUBBLICO LOCALE|\bTPL\b", "local-transport"), (r"MARITTIMO", "ferries")]
NOMI_SETT = {"trains": "rail", "flights": "air", "local-transport": "local transport", "ferries": "ferries/maritime",
             "taxis": "taxis", "motorways": "motorways", "freight": "freight"}


def L(chiave):
    v = LINK.get(chiave)
    # "200": verificato dal server; "browser": dominio ufficiale che blocca le richieste automatiche (vedi link.json)
    return v.get("url") if isinstance(v, dict) and str(v.get("status")) in ("200", "browser") and v.get("url") else None


# ---------------------------------------------------------------- date
def d(iso):
    return date.fromisoformat(iso)


def data_breve(x):
    return f"{GG[x.weekday()]} {x.day} {MES[x.month - 1]} {x.year}"


def data_lunga(x):
    return f"{GIORNI[x.weekday()]} {x.day} {MESI[x.month - 1]} {x.year}"


def intervallo(a, b):
    a, b = d(a), d(b)
    if a == b:
        return data_breve(a)
    if a.year == b.year and a.month == b.month:
        return f"{GG[a.weekday()]} {a.day} – {GG[b.weekday()]} {b.day} {MES[b.month - 1]} {b.year}"
    return f"{data_breve(a)} – {data_breve(b)}"


def ora_it():
    return ADESSO.strftime("%d %b %Y, %H:%M").lstrip("0")


# ---------------------------------------------------------------- traduzione dei dati del registro
def ore_en(testo):
    """Rende la colonna 'modalità' in inglese. Se resta qualcosa di non tradotto restituisce '' (si mostra solo l'originale)."""
    t = " " + testo.upper().replace("’", "'") + " "
    t = re.sub(r"(\d{1,2})[.:](\d{2})", lambda m: f"{int(m.group(1)):02d}:{m.group(2)}", t)
    t = re.sub(r"\bDEL (\d{1,2})/(\d{1,2})\b", lambda m: f"on {int(m.group(1))} {MES[int(m.group(2)) - 1]}", t)
    sost = [
        (r"MODALITA' NON COMUNICATE", "times not announced"), (r"MODALITA' TERRITORIALI", "times set locally"),
        (r"VARIE MODALITA'", "with various time slots"), (r"INTERA PRESTAZIONE LAVORATIVA", "whole shift"),
        (r"INTERA PRESTAZIONE", "whole shift"), (r"INTERA GIORNATA DI LAVORO", "whole working day"),
        (r"INTERA GIORNATA", "whole day"), (r"SECONDO MEZZO TURNO DEL TURNO DI LAVORO", "second half of the shift"),
        (r"PRIMO TURNO", "first shift"), (r"SECONDO TURNO", "second shift"), (r"TERZO TURNO", "third shift"),
        (r"FINE TURNO", "end of shift"), (r"INIZIO TURNO", "start of shift"),
        (r"TRASPORTO MERCI SU ROTAIA", "rail freight"), (r"APPALTI FERROVIARI", "rail contractors"),
        (r"SETTORE FERROVIARIO", "rail"), (r"FERROVIARIO", "rail"), (r"AUTOSTRADE", "motorways"),
        (r"\*?TPL", "local transport"), (r"AEREO", "air"), (r"MARITTIMO", "maritime"),
        (r"(\d+) ORE", r"\1 hours"), (r"\b1 hours\b", "1 hour"), (r"DALLE", "from"), (r"ALLE", "to"), (r"\bE\b", "and"),
        (r"\bORE\b", ""),
    ]
    for a, b in sost:
        t = re.sub(a, b, t)
    t = re.sub(r"\s+", " ", t).strip(" -")
    if re.search(r"[A-Z]{2,}", t.replace("NCC", "")):
        return ""
    t = t.replace(" - ", "; ").replace(" / ", "; ")
    return t[0].upper() + t[1:] if t else ""


def operatore(cat, lingua="en"):
    up = cat.upper()
    for o in operatori:
        if re.search(o["re"], up):
            if lingua == "it":
                if o.get("navigante_it") and "NAVIGANTE" in up:
                    return o["navigante_it"]
                return o.get("it", "")
            if o.get("navigante") and "NAVIGANTE" in up:
                return o["navigante"]
            return o["en"]
    return ""


SETT_TIT_IT = {"Aereo": "trasporto aereo", "Ferroviario": "treni", "Trasporto pubblico locale": "trasporto pubblico locale",
               "Marittimo": "traghetti e porti", "Trasporto merci": "trasporto merci", "Taxi": "taxi", "Ncc": "NCC",
               "Circolazione e sicurezza stradale": "autostrade e soccorso stradale", "Appalti ferroviari": "appalti ferroviari",
               "Elicotteri": "elicotteri"}
NOMI_SETT_IT = {"trains": "treni", "flights": "aerei", "local-transport": "trasporto locale", "ferries": "traghetti",
                "taxis": "taxi", "motorways": "autostrade", "freight": "merci"}


def ore_leggibili(testo):
    """Colonna 'modalità' del registro in minuscolo leggibile (stesso contenuto)."""
    t = testo.lower().replace("modalita'", "modalità")
    for sigla in ("tpl", "ncc", "rfi", "enav"):
        t = re.sub(rf"\b{sigla}\b", sigla.upper(), t)
    return t[:1].upper() + t[1:] if t else t


def aeroporti_in(testo):
    up = testo.upper()
    trovati = [a["slug"] for a in AEROPORTI if any(p in up for p in a["parole"])]
    altri = [p for p in luoghi["altri_aeroporti"] if p in up]
    return trovati, altri


def leggi(s):
    """Sciopero del registro -> voce del sito (campi già in inglese)."""
    sett, ril, reg, prov = s["settore"], s["rilevanza"], s["regione"], s["provincia"]
    up_note = s["note"].upper()
    testo = (s["categoria"] + " " + s["modalita"]).upper()
    generale = sett in ("Generale", "Plurisettoriale")
    settori = list(SETTORE_SLUG.get(sett, []))
    generico = False
    esclusi = []
    menzionati = []
    if generale:
        settori = ["general-strikes"]
        menzionati = list(dict.fromkeys(slug for rx, slug in MENZIONI if re.search(rx, testo)))
        tutti = ["trains", "flights", "local-transport", "ferries"]
        if sett == "Generale" or not menzionati:
            generico = True
            settori += tutti + [x for x in menzionati if x not in tutti]
        else:
            settori += menzionati
    if "CARGO" in s["categoria"].upper() and settori == ["flights"]:
        settori = ["freight"]
    if "ESCLUS" in up_note:
        dopo = up_note[up_note.find("ESCLUS"):]
        esclusi = [slug for rx, slug in ESCLUSIONI if re.search(rx, dopo)]
        settori = [x for x in settori if x not in esclusi]
    nazionale = reg.strip().upper() == "ITALIA"
    tutta_regione = prov.strip().upper() in ("TUTTE", "")
    # aeroporti
    apt, apt_altri = ([], [])
    if "flights" in settori:
        if sett == "Aereo":
            apt, apt_altri = aeroporti_in(s["categoria"])
        if not apt and not apt_altri:
            apt = [a["slug"] for a in AEROPORTI if nazionale or (a["regione"] == reg and (tutta_regione or a["provincia"] == prov))]
    # città: settori passeggeri nazionali, della regione o della provincia; aeroporti collegati
    citta = []
    passeggeri = [x for x in settori if x in PASSEGGERI]
    for c in CITTA:
        if not passeggeri:
            continue
        if passeggeri == ["flights"]:
            if any(a in apt for a in c["aeroporti"]):
                citta.append(c["slug"])
            continue
        if nazionale or (reg == c["regione"] and (tutta_regione or prov == c["provincia"])):
            citta.append(c["slug"])
        elif any(a in apt for a in c["aeroporti"]):
            citta.append(c["slug"])
    # dove
    if nazionale:
        dove = "Whole of Italy"
        ambito = "national"
    elif tutta_regione:
        dove = f"{REG_EN.get(reg, reg)} region"
        ambito = "regional"
    else:
        dove = f"{PROV_EN.get(prov, prov)} area ({REG_EN.get(reg, reg)})"
        ambito = "local"
    if apt or apt_altri:
        nomi = [APT[a]["nome"] for a in apt] if (apt and len(apt) < len(AEROPORTI)) else []
        nomi += [x.title() for x in apt_altri]
        if nomi:
            dove = ("Airport: " if len(nomi) == 1 else "Airports: ") + ", ".join(nomi)
            ambito = "airport"
    chi = operatore(s["categoria"])
    if generale:
        titolo = "General strike" if sett == "Generale" else "Multi-sector strike"
    else:
        titolo = f"{SETTORE_EN.get(sett, sett).capitalize()} strike"
        if chi:
            titolo += f" – {chi}"
    if ambito == "national":
        titolo = "National " + titolo[0].lower() + titolo[1:]
    elif ambito == "regional":
        titolo = f"{REG_EN.get(reg, reg)}: {titolo[0].lower() + titolo[1:]}"
    elif ambito == "local":
        titolo = f"{PROV_EN.get(prov, prov)}: {titolo[0].lower() + titolo[1:]}"
    nota_en = []
    if generale and generico and not esclusi:
        if menzionati:
            nota_en.append("A general strike can involve all public transport; the register gives specific hours for: "
                           + ", ".join(NOMI_SETT[x] for x in menzionati) + ".")
        else:
            nota_en.append("The register does not list the sectors: a general strike can involve all public transport.")
    if s["note"].lstrip().startswith("*") and "*" in s["modalita"]:
        nota_en.append("The part marked * applies only to the companies listed in the register note.")
    if esclusi:
        nota_en.append("The register note excludes: " + ", ".join(NOMI_SETT[x] for x in esclusi) + ".")
    if generale and not [x for x in settori if x in PASSEGGERI]:
        nota_en.append("Public transport is not expected to be involved, according to the register.")
    if "CARGO" in s["categoria"].upper():
        nota_en.append("This strike concerns a cargo operator.")
    # --- versione italiana
    citta_it = []
    for c in CITTA_IT:
        if not passeggeri:
            continue
        if passeggeri == ["flights"]:
            if any(a in apt for a in c["aeroporti"]):
                citta_it.append(c["slug"])
            continue
        if nazionale or (reg == c["regione"] and (tutta_regione or prov == c["provincia"])) or any(a in apt for a in c["aeroporti"]):
            citta_it.append(c["slug"])
    if nazionale:
        dove_it = "Tutta Italia"
    elif tutta_regione:
        dove_it = f"Regione {reg}"
    else:
        dove_it = f"Provincia di {prov} ({reg})"
    if apt or apt_altri:
        nomi = [APT[a]["nome_it"] for a in apt] if (apt and len(apt) < len(AEROPORTI)) else []
        nomi += [x.title() for x in apt_altri]
        if nomi:
            dove_it = ("Aeroporto: " if len(nomi) == 1 else "Aeroporti: ") + ", ".join(nomi)
    chi_it = operatore(s["categoria"], "it")
    if generale:
        titolo_it = "sciopero generale" if sett == "Generale" else "sciopero plurisettoriale"
    else:
        titolo_it = f"sciopero {SETT_TIT_IT.get(sett, sett.lower())}"
        if chi_it:
            titolo_it += f" – {chi_it}"
    if ambito == "national":
        if generale:
            titolo_it = titolo_it[0].upper() + titolo_it[1:] + " nazionale"
        else:
            titolo_it = titolo_it.replace("sciopero", "Sciopero nazionale", 1)
    elif ambito == "regional":
        titolo_it = f"{reg}: {titolo_it}"
    elif ambito == "local":
        titolo_it = f"{prov}: {titolo_it}"
    else:
        titolo_it = titolo_it[0].upper() + titolo_it[1:]
    nota_it = []
    if generale and generico and not esclusi:
        if menzionati:
            nota_it.append("Uno sciopero generale può coinvolgere tutti i trasporti; il registro indica orari specifici per: "
                           + ", ".join(NOMI_SETT_IT[x] for x in menzionati) + ".")
        else:
            nota_it.append("Il registro non elenca i settori: uno sciopero generale può coinvolgere tutti i trasporti.")
    if s["note"].lstrip().startswith("*") and "*" in s["modalita"]:
        nota_it.append("La parte con l'asterisco vale solo per le aziende elencate nella nota del registro.")
    if esclusi:
        nota_it.append("La nota del registro esclude: " + ", ".join(NOMI_SETT_IT[x] for x in esclusi) + ".")
    if generale and not [x for x in settori if x in PASSEGGERI]:
        nota_it.append("Secondo il registro i trasporti pubblici non sono coinvolti.")
    if "CARGO" in s["categoria"].upper():
        nota_it.append("Riguarda un operatore di trasporto merci.")
    stato = s["stato"]
    return {
        "id": s["id"], "inizio": s["inizio"], "fine": s["fine"], "stato": stato,
        "titolo": titolo, "settori": settori, "citta": citta, "aeroporti": apt, "ambito": ambito, "dove": dove,
        "chi": chi, "categoria": s["categoria"], "sindacati": s["sindacati"], "ore": s["modalita"], "ore_en": ore_en(s["modalita"]),
        "rilevanza": RIL_EN.get(ril, ril), "settore_it": sett, "settore_en": SETTORE_EN.get(sett, sett),
        "note": s["note"], "nota_en": " ".join(nota_en), "proclamazione": s["proclamazione"],
        "rimosso_il": s.get("rimosso_il", ""), "regione": reg, "provincia": prov,
        "titolo_it": titolo_it, "dove_it": dove_it, "chi_it": chi_it, "nota_it": " ".join(nota_it),
        "ore_it": ore_leggibili(s["modalita"]), "citta_it": citta_it,
    }


VOCI = [leggi(s) for s in scioperi.values()]
VOCI.sort(key=lambda v: (v["inizio"], 0 if v["ambito"] == "national" else 1, v["titolo"]))
AGGIORNATO = registro.get("registro_aggiornato_al") or OGGI.isoformat()
LETTO = registro.get("letto_il", "")


def recenti():
    """Voci da incorporare nelle pagine e in vista.json: dagli ultimi 35 giorni in poi."""
    limite = (OGGI - timedelta(days=35)).isoformat()
    return [v for v in VOCI if v["fine"] >= limite]


def scrivi_vista():
    vista = {"registro_aggiornato_al": AGGIORNATO, "letto_il": LETTO, "generato_il": ADESSO.strftime("%Y-%m-%d %H:%M"),
             "fonte": URL_REGISTRO, "scioperi": recenti()}
    (DATI / "vista.json").write_text(json.dumps(vista, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- filtri (uguali nel JS)
def nel_giorno(v, giorno):
    return v["inizio"] <= giorno.isoformat() <= v["fine"]


def finestra(nome):
    """(da, a) inclusi, come nel JS."""
    if nome == "today":
        return OGGI, OGGI
    if nome == "tomorrow":
        t = OGGI + timedelta(days=1)
        return t, t
    if nome == "thisweek":
        return OGGI, OGGI + timedelta(days=6 - OGGI.weekday())
    if nome == "nextweek":
        lun = OGGI + timedelta(days=7 - OGGI.weekday())
        return lun, lun + timedelta(days=6)
    if nome.startswith("days:"):
        return OGGI, OGGI + timedelta(days=int(nome[5:]) - 1)
    if nome == "upcoming":
        return OGGI, date(2100, 1, 1)
    if nome.startswith("month:"):
        y, m = map(int, nome[6:].split("-"))
        fine = date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)
        return date(y, m, 1), fine
    raise ValueError(nome)


def filtra(nome_finestra, filtro):
    da, a = finestra(nome_finestra)
    out = []
    for v in VOCI:
        if v["fine"] < da.isoformat() or v["inizio"] > a.isoformat():
            continue
        if not nome_finestra.startswith("month:") and (v["stato"] == "concluso" or v["fine"] < OGGI.isoformat()):
            continue
        tipo, _, val = filtro.partition(":")
        if tipo == "city" and val not in v["citta"]:
            continue
        if tipo == "airport" and val not in v["aeroporti"]:
            continue
        if tipo == "sector" and val not in v["settori"]:
            continue
        if tipo == "passengers" and not any(x in PASSEGGERI for x in v["settori"]):
            continue
        out.append(v)
    return out


# ---------------------------------------------------------------- pezzi comuni
CSS = """
:root{--bg:#F6F5F1;--card:#FFFFFF;--ink:#16202B;--ink-2:#46525E;--ink-3:#6B7681;--line:#E1DED6;
--accent:#B3261E;--accent-2:#FBEAE8;--ok:#1E6B47;--ok-2:#E6F2EB;--warn:#8A4B00;--warn-2:#FFF2DF;--mute:#EEECE6;--radius:14px}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#11161C;--card:#18212A;--ink:#EEF2F5;--ink-2:#BAC5CF;
--ink-3:#8E9BA7;--line:#28333E;--accent:#FF8A80;--accent-2:#3A1D1B;--ok:#7FD3A6;--ok-2:#173226;--warn:#FFB867;--warn-2:#33250F;--mute:#1F2933}}
:root[data-theme="dark"]{--bg:#11161C;--card:#18212A;--ink:#EEF2F5;--ink-2:#BAC5CF;--ink-3:#8E9BA7;--line:#28333E;--accent:#FF8A80;
--accent-2:#3A1D1B;--ok:#7FD3A6;--ok-2:#173226;--warn:#FFB867;--warn-2:#33250F;--mute:#1F2933}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;font-size:17px;line-height:1.6}
a{color:var(--accent)}
.wrap{max-width:980px;margin:0 auto;padding:0 16px}
header.top{border-bottom:1px solid var(--line);background:var(--card)}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:58px}
.logo{font-weight:800;font-size:1.12rem;color:var(--ink);text-decoration:none;letter-spacing:-.01em;white-space:nowrap}
.logo span{color:var(--accent)}
nav.menu{display:flex;gap:14px;flex-wrap:wrap;font-size:.95rem}
nav.menu a{color:var(--ink-2);text-decoration:none}
nav.menu a:hover{color:var(--accent)}
.hero{padding:30px 0 6px}
h1{font-size:clamp(1.55rem,4.6vw,2.3rem);line-height:1.18;letter-spacing:-.02em;margin:0 0 12px}
h2{font-size:1.32rem;margin:34px 0 12px;letter-spacing:-.01em}
h3{font-size:1.06rem;margin:20px 0 8px}
.lead{font-size:1.07rem;color:var(--ink-2);max-width:740px;margin:0 0 6px}
.small{font-size:.9rem;color:var(--ink-3)}
.fresco{font-size:.88rem;color:var(--ink-3);margin:6px 0 0}
.fresco strong{color:var(--ink-2)}
.avviso{background:var(--warn-2);border-left:4px solid var(--warn);padding:11px 14px;border-radius:8px;font-size:.94rem;margin:16px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px}
.riquadri{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:18px 0}
.riq{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:14px 16px;text-decoration:none;color:var(--ink);min-width:0}
.riq .t{font-size:.85rem;font-weight:700;text-transform:uppercase;letter-spacing:.04em;color:var(--ink-3)}
.riq .n{font-size:1.9rem;font-weight:800;line-height:1.2}
.riq .s{font-size:.9rem;color:var(--ink-2)}
.riq.si{border-color:var(--accent)}
.riq.si .n{color:var(--accent)}
.lista{display:grid;gap:10px}
.vuoto{background:var(--ok-2);border:1px solid var(--line);border-radius:var(--radius);padding:14px 16px;color:var(--ink)}
.sc{display:grid;grid-template-columns:170px 1fr;gap:4px 16px;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:14px 16px;min-width:0;overflow-wrap:anywhere}
.sc.naz{border-left:4px solid var(--accent)}
.sc .quando{font-weight:700}
.sc .quando small{display:block;font-weight:400;color:var(--ink-3);font-size:.85rem}
.sc .cosa{min-width:0}
.sc .tit{font-weight:700}
.sc .dett{font-size:.93rem;color:var(--ink-2);margin-top:2px}
.sc .dett b{color:var(--ink);font-weight:600}
.sc .it{font-size:.85rem;color:var(--ink-3)}
.badge{display:inline-block;font-size:.76rem;font-weight:700;letter-spacing:.02em;padding:2px 8px;border-radius:6px;background:var(--mute);color:var(--ink-2);margin:0 6px 4px 0}
.badge.naz{background:var(--accent-2);color:var(--accent)}
.badge.stato{background:var(--warn-2);color:var(--warn)}
.badge.oggi{background:var(--accent);color:var(--bg)}
.fonte{font-size:.8rem;color:var(--ink-3);margin-top:4px}
.fonte a{color:var(--ink-3)}
.filtri{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0 14px}
.filtri button{font:inherit;font-size:.9rem;border:1px solid var(--line);background:var(--card);color:var(--ink);padding:6px 12px;border-radius:999px;cursor:pointer}
.filtri button[aria-pressed="true"]{background:var(--ink);border-color:var(--ink);color:var(--bg)}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}
.griglia a{display:block;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px;text-decoration:none;color:var(--ink);font-weight:600}
.griglia a small{display:block;font-weight:400;color:var(--ink-3)}
.griglia a:hover{border-color:var(--accent)}
.testo p,.testo li{max-width:760px}
details{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin:8px 0}
details summary{cursor:pointer;font-weight:650}
.form{display:grid;gap:12px}
.form label{display:grid;gap:4px;font-weight:600;font-size:.95rem}
.form input,.form select,.form textarea{font:inherit;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink);width:100%}
.form .due-campi{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:400;font-size:.9rem;color:var(--ink-2)}
.form .check input{width:auto;margin-top:4px}
.btn{font:inherit;font-weight:700;background:var(--accent);color:#fff;border:0;border-radius:10px;padding:12px 18px;cursor:pointer}
.btn:disabled{opacity:.6;cursor:wait}
.hp{position:absolute;left:-9999px}
.ok{background:var(--ok-2);border:1px solid var(--ok);padding:14px;border-radius:10px}
.errore{color:var(--warn);font-weight:600}
.ad-slot:empty{display:none}
.briciole{font-size:.85rem;color:var(--ink-3);margin-top:14px}
.briciole a{color:var(--ink-3)}
footer{margin-top:50px;border-top:1px solid var(--line);padding:22px 0 40px;font-size:.88rem;color:var(--ink-3)}
footer a{color:var(--ink-3)}
@media (max-width:760px){.riquadri{grid-template-columns:1fr}.sc{grid-template-columns:1fr}.form .due-campi{grid-template-columns:1fr}
header.top .wrap{flex-direction:column;align-items:flex-start;gap:4px;padding-top:10px;padding-bottom:10px}nav.menu{gap:12px;font-size:.92rem}}
"""

JS = r"""
(function(){
  var MES=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var GG=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
  var PASS=['trains','flights','local-transport','ferries','taxis'];
  function oggiRoma(){try{return new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/Rome',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());}catch(e){var x=new Date();return x.toISOString().slice(0,10);}}
  function pd(iso){var p=iso.split('-');return new Date(Date.UTC(+p[0],+p[1]-1,+p[2]));}
  function iso(x){return x.toISOString().slice(0,10);}
  function add(isoD,n){var x=pd(isoD);x.setUTCDate(x.getUTCDate()+n);return iso(x);}
  function wd(isoD){return (pd(isoD).getUTCDay()+6)%7;}
  function breve(isoD){var x=pd(isoD);return GG[wd(isoD)]+' '+x.getUTCDate()+' '+MES[x.getUTCMonth()]+' '+x.getUTCFullYear();}
  function interv(a,b){if(a===b)return breve(a);var x=pd(a),y=pd(b);
    if(x.getUTCFullYear()===y.getUTCFullYear()&&x.getUTCMonth()===y.getUTCMonth())return GG[wd(a)]+' '+x.getUTCDate()+' – '+GG[wd(b)]+' '+y.getUTCDate()+' '+MES[y.getUTCMonth()]+' '+y.getUTCFullYear();
    return breve(a)+' – '+breve(b);}
  var OGGI=oggiRoma();
  function fin(n){
    if(n==='today')return[OGGI,OGGI];
    if(n==='tomorrow'){var t=add(OGGI,1);return[t,t];}
    if(n==='thisweek')return[OGGI,add(OGGI,6-wd(OGGI))];
    if(n==='nextweek'){var l=add(OGGI,7-wd(OGGI));return[l,add(l,6)];}
    if(n.indexOf('days:')===0)return[OGGI,add(OGGI,+n.slice(5)-1)];
    if(n==='upcoming')return[OGGI,'2100-01-01'];
    if(n.indexOf('month:')===0){var p=n.slice(6).split('-');var y=+p[0],m=+p[1];var f=new Date(Date.UTC(y,m,0));return[n.slice(6)+'-01',iso(f)];}
    return[OGGI,OGGI];}
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function filtra(dati,n,f){var r=fin(n),da=r[0],a=r[1],out=[];
    dati.forEach(function(v){
      if(v.fine<da||v.inizio>a)return;
      if(n.indexOf('month:')!==0&&(v.stato==='concluso'||v.fine<OGGI))return;
      var p=f.split(':'),t=p[0],val=p.slice(1).join(':');
      if(t==='city'&&v.citta.indexOf(val)<0)return;
      if(t==='airport'&&v.aeroporti.indexOf(val)<0)return;
      if(t==='sector'&&v.settori.indexOf(val)<0)return;
      if(t==='passengers'&&!v.settori.some(function(x){return PASS.indexOf(x)>=0;}))return;
      out.push(v);});
    return out;}
  function scheda(v){
    var oggi=v.inizio<=OGGI&&OGGI<=v.fine, fin_=v.fine<OGGI;
    var b='';
    if(oggi&&v.stato!=='rimosso dal registro'&&v.stato!=='revocato')b+='<span class="badge oggi">Today</span>';
    if(v.ambito==='national')b+='<span class="badge naz">Whole of Italy</span>';
    b+='<span class="badge">'+esc(v.settore_en.charAt(0).toUpperCase()+v.settore_en.slice(1))+'</span>';
    if(v.stato==='rimosso dal registro')b+='<span class="badge stato">No longer in the register</span>';
    if(v.stato==='revocato')b+='<span class="badge stato">Called off (register note)</span>';
    if(fin_||v.stato==='concluso')b+='<span class="badge">Ended</span>';
    var h='<article class="sc'+(v.ambito==='national'?' naz':'')+'" id="s'+v.id+'"><div class="quando">'+esc(interv(v.inizio,v.fine))+'<small>'+esc(v.dove)+'</small></div><div class="cosa">'+b;
    h+='<div class="tit">'+esc(v.titolo)+'</div>';
    h+='<div class="dett"><b>Hours:</b> '+(v.ore_en?esc(v.ore_en)+' <span class="it">(register: '+esc(v.ore)+')</span>':'<span lang="it">'+esc(v.ore)+'</span>')+'</div>';
    h+='<div class="dett"><b>Who:</b> '+(v.chi?esc(v.chi)+' <span class="it" lang="it">('+esc(v.categoria)+')</span>':'<span lang="it">'+esc(v.categoria)+'</span>')+'</div>';
    if(v.nota_en)h+='<div class="dett">'+esc(v.nota_en)+'</div>';
    if(v.note)h+='<div class="dett"><b>Register note:</b> <span lang="it">'+esc(v.note)+'</span></div>';
    if(v.stato==='rimosso dal registro')h+='<div class="dett">No longer listed in the official register as of '+esc(breve(v.rimosso_il))+' (likely called off): check with the operator.</div>';
    h+='<div class="fonte">Unions: '+esc(v.sindacati)+' · announced '+esc(breve(v.proclamazione))+' · <a href="'+'URL_REG'+'" rel="noopener">official register (MIT id '+esc(v.id)+')</a></div>';
    return h+'</div></article>';}
  function vuoto(n){var r=fin(n);var w={'today':'today ('+breve(r[0])+')','tomorrow':'tomorrow ('+breve(r[0])+')','thisweek':'for the rest of this week','nextweek':'next week ('+interv(r[0],r[1])+')'}[n]||'in this period';
    return '<div class="vuoto"><strong>No strikes listed '+w+'</strong> in the official register for this selection. Strikes must be announced at least 10 days ahead, but check again before you travel.</div>';}
  function disegna(dati){
    document.querySelectorAll('[data-finestra]').forEach(function(el){
      var lista=filtra(dati,el.dataset.finestra,el.dataset.filtro||'all');
      var max=+(el.dataset.max||0);if(max&&lista.length>max)lista=lista.slice(0,max);
      el.innerHTML=lista.length?lista.map(scheda).join(''):vuoto(el.dataset.finestra);});
    document.querySelectorAll('[data-conta]').forEach(function(el){
      var n=filtra(dati,el.dataset.conta,el.dataset.filtro||'passengers').length;
      el.textContent=n;var box=el.closest('.riq');if(box)box.classList.toggle('si',n>0);});
    document.querySelectorAll('[data-giorno]').forEach(function(el){var r=fin(el.dataset.giorno);el.textContent=interv(r[0],r[1]);});}
  var nodo=document.getElementById('dati');
  if(nodo){
    var D=JSON.parse(nodo.textContent);disegna(D.scioperi);
    if(window.fetch){fetch('URL_LIVE',{cache:'no-store'}).then(function(r){if(!r.ok)throw 0;return r.json();}).then(function(L){
      if(L&&L.scioperi&&L.letto_il>D.letto_il){disegna(L.scioperi);
        document.querySelectorAll('[data-letto]').forEach(function(e){e.textContent=L.letto_il+' (Italy time)';});
        document.querySelectorAll('[data-reg]').forEach(function(e){e.textContent=breve(L.registro_aggiornato_al);});}
    }).catch(function(){});}
  }
  document.querySelectorAll('.filtri').forEach(function(g){var bott=g.querySelectorAll('button');var bersaglio=document.getElementById(g.dataset.per);
    bott.forEach(function(b){b.addEventListener('click',function(){bott.forEach(function(x){x.setAttribute('aria-pressed','false');});
      b.setAttribute('aria-pressed','true');bersaglio.dataset.filtro=b.dataset.filtro;disegna(window.__D||JSON.parse(nodo.textContent).scioperi);});});});
  var src=document.querySelectorAll('input[name=source]');
  var v='';try{var q=new URLSearchParams(location.search);v=q.get('ref')||q.get('utm_source')||document.referrer||'direct';}catch(e){v='direct';}
  src.forEach(function(i){i.value=String(v).slice(0,200);});
  document.querySelectorAll('form.ajax').forEach(function(form){
    form.addEventListener('submit',function(ev){ev.preventDefault();
      var err=form.querySelector('[data-errore]');err.hidden=true;
      var a=form.querySelector('[name=from]'),b=form.querySelector('[name=to]');
      if(a&&b&&a.value&&b.value&&b.value<a.value){b.setCustomValidity('The end date must be after the start date');}else if(b){b.setCustomValidity('');}
      if(!form.checkValidity()){form.reportValidity();return;}
      var bt=form.querySelector('button');bt.disabled=true;
      fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(new FormData(form)).toString()})
      .then(function(r){if(!r.ok)throw new Error(r.status);form.hidden=true;form.parentNode.querySelector('[data-ok]').hidden=false;})
      .catch(function(){err.hidden=false;bt.disabled=false;});});});
  document.querySelectorAll('input[type=date][data-min-oggi]').forEach(function(i){i.min=OGGI;});
})();
""".replace("URL_LIVE", URL_DATI_LIVE).replace("'URL_REG'", "'" + URL_REGISTRO + "'")

# Il JS ridisegna con i dati più recenti; per i filtri tiene l'ultima versione in window.__D
JS = JS.replace("disegna(L.scioperi);", "window.__D=L.scioperi;disegna(L.scioperi);")

URLS = []


def pagina(percorso, titolo, descrizione, corpo, briciole=None, con_dati=False, indicizza=True, jsonld_extra=None):
    """Scrive sito/<percorso>/index.html (o il file indicato) con la struttura comune."""
    file = percorso if percorso.endswith(".html") else (percorso + "index.html")
    profondita = file.count("/")
    rel = "../" * profondita or "./"
    url_pag = URL_SITO + "/" + (percorso if not percorso.endswith("index.html") else percorso[:-10])
    if indicizza:
        URLS.append(percorso)
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": NOME, "url": URL_SITO + "/"}] if percorso == "" else []
    if briciole:
        voci = [{"@type": "ListItem", "position": 1, "name": "Home", "item": URL_SITO + "/"}]
        for i, (nome, p) in enumerate(briciole, start=2):
            voci.append({"@type": "ListItem", "position": i, "name": nome, "item": URL_SITO + "/" + p})
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": voci})
        bc = '<nav class="briciole" aria-label="Breadcrumb"><a href="' + rel + '">Home</a>' + "".join(
            f' › <a href="{rel}{p}">{escape(n)}</a>' for n, p in briciole[:-1]) + f" › {escape(briciole[-1][0])}</nav>"
    else:
        bc = ""
    if jsonld_extra:
        ld.append(jsonld_extra)
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    dati_html = ""
    if con_dati:
        dati = {"letto_il": LETTO, "registro_aggiornato_al": AGGIORNATO, "scioperi": recenti()}
        dati_html = '<script type="application/json" id="dati">' + json.dumps(dati, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>"
    verifica = f'<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">' if GOOGLE_VERIFICA else ""
    alt_it = None
    if italiano_attivo():
        import genera_it
        alt_it = genera_it.percorso_it(percorso)
        if alt_it is not None:
            verifica += (f'<link rel="alternate" hreflang="en" href="{url_pag}"><link rel="alternate" hreflang="it" href="{URL_SITO}/{alt_it}">'
                         f'<link rel="alternate" hreflang="x-default" href="{url_pag}">')
    verifica += f'<meta name="impact-site-verification" value="{IMPACT_VERIFICA}">' if IMPACT_VERIFICA else ""
    robots = "" if indicizza else '<meta name="robots" content="noindex">'
    testo = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titolo)}</title>
<meta name="description" content="{escape(descrizione)}">
<link rel="canonical" href="{url_pag}">
<meta property="og:title" content="{escape(titolo)}">
<meta property="og:description" content="{escape(descrizione)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{URL_SITO}/og.png">
<meta property="og:url" content="{url_pag}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#B3261E">
{verifica}{robots}
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%23B3261E'/%3E%3Ctext x='32' y='44' font-family='Arial' font-weight='700' font-size='30' text-anchor='middle' fill='white'%3E!%3C/text%3E%3C/svg%3E">
<style>{CSS}</style>
{ld_html}
</head>
<body>
<header class="top"><div class="wrap">
<a class="logo" href="{rel}">Italy Strikes <span>Today</span></a>
<nav class="menu" aria-label="Menu">
<a href="{rel}today/">Today</a><a href="{rel}tomorrow/">Tomorrow</a><a href="{rel}this-week/">This week</a><a href="{rel}#cities">Cities</a><a href="{rel}airports/">Airports</a><a href="{rel}guides/">Guides</a>{f'<a href="{rel}{alt_it}" hreflang="it" lang="it">Italiano</a>' if alt_it is not None else ""}
</nav>
</div></header>
<main class="wrap">
{bc}
{corpo}
</main>
<footer><div class="wrap">
<p><strong>{NOME}</strong> is an independent site. Data from the <a href="{URL_REGISTRO}" rel="noopener">official strike register of the Italian Ministry of Infrastructure and Transport (MIT)</a>; we are not affiliated with MIT, unions or transport operators.
<strong>Strikes can be called off or changed at short notice. Always check with your train operator, airline or local transport company before travelling.</strong> Nothing on this site is legal advice.</p>
<p>Official register last updated: <span data-reg>{data_breve(d(AGGIORNATO))}</span> · checked <span data-letto>{escape(LETTO)} (Italy time)</span><br>
<a href="{rel}about/">About and sources</a> · <a href="{rel}contact/">Contact</a> · <a href="{rel}privacy.html">Privacy</a> · <a href="{rel}guides/">Guides</a></p>
</div></footer>
{dati_html}
<script>{JS}</script>
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")


def scheda(v):
    """Uguale a scheda() nel JS (stessa struttura)."""
    oggi_si = v["inizio"] <= OGGI.isoformat() <= v["fine"]
    finito = v["fine"] < OGGI.isoformat()
    b = ""
    if oggi_si and v["stato"] not in ("rimosso dal registro", "revocato"):
        b += '<span class="badge oggi">Today</span>'
    if v["ambito"] == "national":
        b += '<span class="badge naz">Whole of Italy</span>'
    b += f'<span class="badge">{escape(v["settore_en"][0].upper() + v["settore_en"][1:])}</span>'
    if v["stato"] == "rimosso dal registro":
        b += '<span class="badge stato">No longer in the register</span>'
    if v["stato"] == "revocato":
        b += '<span class="badge stato">Called off (register note)</span>'
    if finito or v["stato"] == "concluso":
        b += '<span class="badge">Ended</span>'
    ore = (f'{escape(v["ore_en"])} <span class="it">(register: {escape(v["ore"])})</span>' if v["ore_en"]
           else f'<span lang="it">{escape(v["ore"])}</span>')
    chi = (f'{escape(v["chi"])} <span class="it" lang="it">({escape(v["categoria"])})</span>' if v["chi"]
           else f'<span lang="it">{escape(v["categoria"])}</span>')
    h = (f'<article class="sc{" naz" if v["ambito"] == "national" else ""}" id="s{v["id"]}"><div class="quando">{escape(intervallo(v["inizio"], v["fine"]))}'
         f'<small>{escape(v["dove"])}</small></div><div class="cosa">{b}<div class="tit">{escape(v["titolo"])}</div>'
         f'<div class="dett"><b>Hours:</b> {ore}</div><div class="dett"><b>Who:</b> {chi}</div>')
    if v["nota_en"]:
        h += f'<div class="dett">{escape(v["nota_en"])}</div>'
    if v["note"]:
        h += f'<div class="dett"><b>Register note:</b> <span lang="it">{escape(v["note"])}</span></div>'
    if v["stato"] == "rimosso dal registro":
        h += (f'<div class="dett">No longer listed in the official register as of {data_breve(d(v["rimosso_il"]))} '
              f'(likely called off): check with the operator.</div>')
    h += (f'<div class="fonte">Unions: {escape(v["sindacati"])} · announced {data_breve(d(v["proclamazione"]))} · '
          f'<a href="{URL_REGISTRO}" rel="noopener">official register (MIT id {escape(v["id"])})</a></div></div></article>')
    return h


def vuoto_html(nome):
    da, a = finestra(nome)
    w = {"today": f"today ({data_breve(da)})", "tomorrow": f"tomorrow ({data_breve(da)})", "thisweek": "for the rest of this week",
         "nextweek": f"next week ({intervallo(da.isoformat(), a.isoformat())})"}.get(nome, "in this period")
    return (f'<div class="vuoto"><strong>No strikes listed {w}</strong> in the official register for this selection. '
            'Strikes must be announced at least 10 days ahead, but check again before you travel.</div>')


def blocco(nome, filtro="all", massimo=0, id_=""):
    lista = filtra(nome, filtro)
    if massimo:
        lista = lista[:massimo]
    contenuto = "".join(scheda(v) for v in lista) if lista else vuoto_html(nome)
    attr_id = f' id="{id_}"' if id_ else ""
    attr_max = f' data-max="{massimo}"' if massimo else ""
    return f'<div class="lista"{attr_id} data-finestra="{nome}" data-filtro="{filtro}"{attr_max}>{contenuto}</div>'


def riquadri(filtro="passengers", base=""):
    out = []
    for nome, etich, url in (("today", "Today", "today/"), ("tomorrow", "Tomorrow", "tomorrow/"), ("thisweek", "This week", "this-week/")):
        n = len(filtra(nome, filtro))
        da, a = finestra(nome)
        out.append(f'<a class="riq{" si" if n else ""}" href="{base}{url}"><div class="t">{etich}</div>'
                   f'<div class="n" data-conta="{nome}" data-filtro="{filtro}">{n}</div>'
                   f'<div class="s"><span data-giorno="{nome}">{escape(intervallo(da.isoformat(), a.isoformat()))}</span> · strikes listed</div></a>')
    return '<div class="riquadri">' + "".join(out) + "</div>"


def fresco():
    return (f'<p class="fresco">Official register last updated: <strong data-reg>{data_breve(d(AGGIORNATO))}</strong> · '
            f'checked <span data-letto>{escape(LETTO)} (Italy time)</span> · source: <a href="{URL_REGISTRO}" rel="noopener">MIT strike register</a></p>')


AVVISO = ('<p class="avviso">Strikes can be called off or changed at short notice. Always check with your train operator, '
          'airline or local transport company before travelling.</p>')
AD = '<div class="ad-slot" aria-hidden="true"></div>'


def box_affiliati():
    """Riquadro 'Stuck by a strike?' con i link di affiliazione; vuoto finché non ci sono URL (vedi dati/affiliati.json)."""
    voci = [v for k, v in AFFILIATI.items() if not k.startswith("_") and v.get("url")]
    if not voci:
        return ""
    righe = "".join(
        f'<li><a href="{escape(v["url"])}" rel="sponsored noopener" target="_blank">{escape(v["titolo"])}</a> '
        f'<span class="small">({escape(v["nome"])}) {escape(v["testo"])}</span></li>' for v in voci)
    return (f'<section class="card" style="margin-top:22px"><h2 style="margin-top:0">Stuck by a strike? Alternatives</h2>'
            f'<ul style="margin:0 0 8px;padding-left:20px">{righe}</ul>'
            f'<p class="small" style="margin:0">Some of these are affiliate links: if you book through them we may earn a small commission, '
            f'at no extra cost to you. It helps keep this site free.</p></section>')


def opzioni_luoghi():
    o = '<option value="Anywhere in Italy">Anywhere in Italy</option>'
    o += "".join(f'<option value="{escape(c["nome"])}">{escape(c["nome"])}</option>' for c in CITTA)
    o += "".join(f'<option value="Airport {a["iata"]}">{escape(a["nome"])} airport ({a["iata"]})</option>' for a in AEROPORTI)
    return o


def modulo(rel):
    return f"""<section class="card" id="alerts" style="margin-top:30px">
<h2 style="margin-top:0">Get an email if a strike hits your travel dates</h2>
<p class="small" style="margin-top:-4px">Free, no spam. We check the official register every day and write to you only if a strike is listed for your dates and places.</p>
<form class="form ajax" name="alerts" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="alerts">
<input type="hidden" name="source" value="">
<p class="hp"><label>Do not fill this in <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Your email<input type="email" name="email" required autocomplete="email" placeholder="name@example.com"></label>
<div class="due-campi"><label>Travel from<input type="date" name="from" required data-min-oggi></label>
<label>Travel to<input type="date" name="to" required data-min-oggi></label></div>
<label>Where<select name="place" required>{opzioni_luoghi()}</select></label>
<label class="check"><input type="checkbox" name="consent" value="yes" required>
<span>I agree to receive strike alerts by email from {NOME} for these dates. I can unsubscribe at any time. I have read the <a href="{rel}privacy.html">privacy notice</a>.</span></label>
<button class="btn" type="submit">Send me alerts</button>
<p class="errore" data-errore hidden>Sorry, it did not work. Please try again in a moment.</p>
</form>
<div class="ok" data-ok hidden><strong>Done!</strong> We will email you if a strike is listed for your travel dates.</div>
</section>"""


def griglia_citta(rel):
    return '<div class="griglia">' + "".join(
        f'<a href="{rel}{c["slug"]}/">{escape(c["nome"])}<small>{len(filtra("upcoming", "city:" + c["slug"]))} upcoming</small></a>' for c in CITTA) + "</div>"


def griglia_settori(rel):
    return '<div class="griglia">' + "".join(
        f'<a href="{rel}{s}/">{escape(n)}<small>{len(filtra("upcoming", "sector:" + s))} upcoming</small></a>' for s, (n, _, _) in SETTORI.items()) + "</div>"


def mesi_da_mostrare():
    mesi = {(OGGI.year, OGGI.month)}
    for v in VOCI:
        mesi.add((d(v["inizio"]).year, d(v["inizio"]).month))
    y, m = OGGI.year, OGGI.month
    for _ in range(2):  # i due mesi dopo l'ultimo con scioperi, o almeno i prossimi due
        m += 1
        if m == 13:
            y, m = y + 1, 1
        mesi.add((y, m))
    ultimo = max(mesi)
    y, m = ultimo
    nxt = (y + (m == 12), m % 12 + 1)
    mesi.add(nxt)
    return sorted(mesi)


def url_mese(y, m):
    return f"{y}/{MESI[m - 1].lower()}/"


def griglia_mesi(rel):
    return '<div class="griglia">' + "".join(
        f'<a href="{rel}{url_mese(y, m)}">{MESI[m - 1]} {y}<small>{len(filtra(f"month:{y}-{m:02d}", "all"))} listed</small></a>'
        for y, m in mesi_da_mostrare() if (y, m) >= (OGGI.year, OGGI.month)) + "</div>"


def strumenti_home():
    if not satelliti_attivi():
        return ""
    return ('<h2>Tools for visitors</h2><div class="griglia"><a href="codice-fiscale-calculator/">Codice fiscale calculator'
            '<small>Italian tax code for foreigners</small></a><a href="ztl-fines/">ZTL fines in Italy<small>amounts, deadlines, how to pay</small></a></div>')


# ---------------------------------------------------------------- pagine
def home():
    rel = "./"
    corpo = f"""<section class="hero">
<h1>Italy strikes today and tomorrow</h1>
<p class="lead">Every transport strike in Italy from the official government register, in plain English: trains, flights and airports, buses and metro, ferries and taxis. Updated every day.</p>
{fresco()}
</section>
{riquadri("passengers", "")}
{AVVISO}
{AD}
<h2>Today and tomorrow</h2>
<p class="small">Strikes that can affect travellers (passenger transport and general strikes).</p>
{blocco("today", "passengers")}
<h3>Tomorrow</h3>
{blocco("tomorrow", "passengers")}
{box_affiliati()}
<h2 id="next">Next 30 days</h2>
<div class="filtri" data-per="prossimi" role="group" aria-label="Filter by type">
<button type="button" data-filtro="passengers" aria-pressed="true">All passenger transport</button>
<button type="button" data-filtro="sector:trains" aria-pressed="false">Trains</button>
<button type="button" data-filtro="sector:flights" aria-pressed="false">Flights</button>
<button type="button" data-filtro="sector:local-transport" aria-pressed="false">Bus and metro</button>
<button type="button" data-filtro="sector:general-strikes" aria-pressed="false">General strikes</button>
<button type="button" data-filtro="all" aria-pressed="false">Everything (incl. freight)</button>
</div>
{blocco("days:30", "passengers", id_="prossimi")}
<h2 id="cities">Strikes by city</h2>
{griglia_citta(rel)}
<h2>By type of transport</h2>
{griglia_settori(rel)}
<h2>By month</h2>
{griglia_mesi(rel)}
<h2>Airports</h2>
<div class="griglia">{"".join(f'<a href="airports/{a["slug"]}/">{escape(a["nome"])}<small>{a["iata"]}</small></a>' for a in AEROPORTI)}</div>
{modulo(rel)}
{strumenti_home()}
<h2>Good to know</h2>
<div class="testo">
<p>Strikes in Italian public transport must be announced at least 10 days in advance and are listed in the register of the Ministry of Infrastructure and Transport. During most strikes some services are guaranteed: <a href="guides/guaranteed-trains/">guaranteed trains</a>, <a href="guides/flights-during-strikes/">guaranteed flights</a> and <a href="guides/local-transport-strike-hours/">guaranteed hours for buses and metro</a>.</p>
<p>New to Italian strikes? Start with <a href="guides/how-strikes-work-in-italy/">how strikes work in Italy</a>.</p>
</div>
{AD}"""
    pagina("", "Italy strikes today and tomorrow – official register, updated daily", 
           "Is there a strike in Italy today or tomorrow? Trains, flights, airports, buses and metro, from the official Italian government register, in English. Updated daily.",
           corpo, con_dati=True)


def pagina_finestra(slug, nome, h1, titolo, descr):
    rel = "../"
    da, a = finestra(nome)
    corpo = f"""<section class="hero"><h1>{escape(h1)}</h1>
<p class="lead"><span data-giorno="{nome}">{escape(intervallo(da.isoformat(), a.isoformat()))}</span>. Transport strikes listed in the official Italian register for passenger transport and general strikes.</p>
{fresco()}</section>
{AVVISO}
{blocco(nome, "passengers")}
{box_affiliati()}
{AD}
<h2>Other strikes in the register</h2>
<p class="small">Freight, motorway services and other strikes that do not normally affect passengers.</p>
{blocco(nome, "sector:freight")}
{blocco(nome, "sector:motorways")}
<h2>Check your city</h2>
{griglia_citta(rel)}
{modulo(rel)}"""
    pagina(f"{slug}/", titolo, descr, corpo, briciole=[(h1, f"{slug}/")], con_dati=True)


def pagina_mese(y, m):
    rel = "../../"
    chiave = f"month:{y}-{m:02d}"
    n = len(filtra(chiave, "all"))
    passato = (y, m) < (OGGI.year, OGGI.month)
    nome = f"{MESI[m - 1]} {y}"
    intro = (f"All transport strikes in Italy in {nome} from the official register: dates, hours, cities and who is striking."
             if n else f"No strikes are listed yet for {nome}. Strikes must be announced at least 10 days in advance: check back, the page updates every day.")
    archivio = ""
    if (y, m) == (2026, 10):
        archivio = '<p class="small">Our archive starts on 10 October 2026: strikes earlier in October are not shown.</p>'
    corpo = f"""<section class="hero"><h1>Italy strikes in {nome}</h1>
<p class="lead">{intro}</p>{fresco()}{archivio}</section>
{AVVISO}
<h2>Strikes affecting travellers</h2>
{blocco(chiave, "passengers")}
{box_affiliati()}
{AD}
<h2>Freight and other strikes</h2>
{blocco(chiave, "sector:freight")}
{blocco(chiave, "sector:motorways")}
<h2>Other months</h2>
{griglia_mesi(rel)}
{modulo(rel)}"""
    descr = (f"Italy transport strikes in {nome}: train, flight, airport, bus and metro strikes with dates and hours, from the official register."
             if not passato else f"Transport strikes that were listed in Italy in {nome}, from the official register.")
    pagina(url_mese(y, m), f"Italy strikes {nome}: trains, flights, buses – full list", descr, corpo,
           briciole=[(nome, url_mese(y, m))], con_dati=True)


TESTO_SETTORE = {
    "trains": "Rail strikes can stop Trenitalia, Italo and regional trains such as Trenord. National rail strikes often start at 21:00 the evening before and end at 21:00 on the strike day. Some trains are always guaranteed.",
    "flights": "Air transport strikes can involve an airline's crew, air traffic control (ENAV), airport ground handling or security staff. Flights scheduled between 07:00 and 10:00 and between 18:00 and 21:00 must operate, plus a list of essential flights published by ENAC.",
    "local-transport": "Local transport strikes stop city buses, metro and trams, usually for 4 or 24 hours. Each city has guaranteed hours, often during the morning and evening rush.",
    "ferries": "Maritime strikes can affect ferries to the islands and port services. Connections to small islands are often guaranteed.",
    "taxis": "Taxi strikes are less common and usually local.",
    "general-strikes": "A general strike can involve all sectors, including transport. The register says which transport sectors join and at what times.",
    "motorways": "Motorway strikes involve toll booth staff, roadside assistance or service staff. Traffic usually keeps moving.",
    "freight": "Freight strikes involve lorry drivers or rail freight. They do not normally affect passenger travel, but large lorry stoppages can slow down roads.",
}


def pagina_settore(slug):
    nome, titolo, _ = SETTORI[slug]
    rel = "../"
    guida = {"trains": "guides/guaranteed-trains/", "flights": "guides/flights-during-strikes/",
             "local-transport": "guides/local-transport-strike-hours/", "general-strikes": "guides/general-strikes/"}.get(slug)
    extra = f'<p>Read more: <a href="{rel}{guida}">what still runs during a strike</a>.</p>' if guida else ""
    corpo = f"""<section class="hero"><h1>{escape(titolo)}</h1>
<p class="lead">{escape(TESTO_SETTORE[slug])}</p>{extra}{fresco()}</section>
{riquadri("sector:" + slug, rel)}
{AVVISO}
<h2>Upcoming {escape(nome.lower())} strikes</h2>
{blocco("upcoming", "sector:" + slug)}
{box_affiliati()}
{AD}
<h2>Other types of transport</h2>
{griglia_settori(rel)}
{modulo(rel)}"""
    pagina(f"{slug}/", f"{titolo}: today, tomorrow and upcoming dates",
           f"{titolo}: every upcoming date from the official register, with hours and who is striking. Updated daily.",
           corpo, briciole=[(nome, f"{slug}/")], con_dati=True)


def link_operatori(c):
    out = []
    for k in c["operatori"]:
        u = L(k)
        if u:
            out.append(f'<a href="{escape(u)}" rel="noopener">{escape(LINK[k].get("nome", "local transport operator"))}</a>')
    return out


def pagina_citta(c):
    rel = "../"
    ops = link_operatori(c)
    apt = [APT[a] for a in c["aeroporti"]]
    apt_html = ", ".join(f'<a href="{rel}airports/{a["slug"]}/">{escape(a["nome"])}</a>' for a in apt)
    corpo = f"""<section class="hero"><h1>{escape(c["nome"])} strikes today and upcoming</h1>
<p class="lead">Transport strikes that can affect {escape(c["nome"])} ({escape(c["it"])}): national train, flight and general strikes, strikes in {escape(REG_EN.get(c["regione"], c["regione"]))} and local bus, metro and tram strikes.</p>{fresco()}</section>
{riquadri("city:" + c["slug"], rel)}
{AVVISO}
<h2>Upcoming strikes affecting {escape(c["nome"])}</h2>
{blocco("upcoming", "city:" + c["slug"])}
{box_affiliati()}
{AD}
<h2>Useful links for {escape(c["nome"])}</h2>
<ul>
{"".join(f"<li>Local transport: {o} (guaranteed hours during strikes are on the operator's site)</li>" for o in ops)}
{f"<li>Airports: {apt_html}</li>" if apt else ""}
<li><a href="{rel}guides/guaranteed-trains/">Guaranteed trains during strikes</a></li>
<li><a href="{rel}guides/local-transport-strike-hours/">Bus and metro guaranteed hours</a></li>
</ul>
<h2>Other cities</h2>
{griglia_citta(rel)}
{modulo(rel)}"""
    pagina(f"{c['slug']}/", f"{c['nome']} strike today? Trains, buses, metro and flights",
           f"Is there a strike in {c['nome']} today or tomorrow? Upcoming transport strikes affecting {c['nome']}: trains, metro, buses, flights. Official register, updated daily.",
           corpo, briciole=[(c["nome"], f"{c['slug']}/")], con_dati=True)


def pagina_aeroporto(a):
    rel = "../../"
    u = L(a["link"])
    sito = f'<a href="{escape(u)}" rel="noopener">official airport website</a>' if u else "the official airport website"
    enac = L("enac_voli_garantiti")
    corpo = f"""<section class="hero"><h1>{escape(a["nome"])} airport ({a["iata"]}) strikes</h1>
<p class="lead">Strikes that can affect flights at {escape(a["nome"])}: national air traffic control and airline strikes, and strikes of staff working at this airport.</p>{fresco()}</section>
{riquadri("airport:" + a["slug"], rel)}
{AVVISO}
<h2>Upcoming strikes</h2>
{blocco("upcoming", "airport:" + a["slug"])}
{box_affiliati()}
{AD}
<h2>What to do</h2>
<ul>
<li>Check your flight with your airline and on the {sito}.</li>
<li>During air transport strikes, flights scheduled between 07:00 and 10:00 and between 18:00 and 21:00 must operate{f', as well as the <a href="{escape(enac)}" rel="noopener">essential flights listed by ENAC</a>' if enac else ''}. More in <a href="{rel}guides/flights-during-strikes/">flights during strikes</a>.</li>
</ul>
<h2>Other airports</h2>
<div class="griglia">{"".join(f'<a href="{rel}airports/{x["slug"]}/">{escape(x["nome"])}<small>{x["iata"]}</small></a>' for x in AEROPORTI if x is not a)}</div>
{modulo(rel)}"""
    pagina(f"airports/{a['slug']}/", f"{a['nome']} ({a['iata']}) strike: today and upcoming",
           f"Is there a strike at {a['nome']} airport ({a['iata']})? Upcoming air traffic control, airline and airport staff strikes, from the official Italian register.",
           corpo, briciole=[("Airports", "airports/"), (a["nome"], f"airports/{a['slug']}/")], con_dati=True)


def indice_aeroporti():
    rel = "../"
    corpo = f"""<section class="hero"><h1>Italian airport strikes</h1>
<p class="lead">Air transport strikes in Italy by airport. National strikes (air traffic control, airlines) can affect every airport.</p>{fresco()}</section>
<div class="griglia">{"".join(f'<a href="{a["slug"]}/">{escape(a["nome"])}<small>{a["iata"]} · {len(filtra("upcoming", "airport:" + a["slug"]))} upcoming</small></a>' for a in AEROPORTI)}</div>
{AVVISO}
<h2>All upcoming flight and airport strikes</h2>
{blocco("upcoming", "sector:flights")}
{modulo(rel)}"""
    pagina("airports/", "Italy airport strikes: Rome, Milan, Venice, Naples and more",
           "Upcoming strikes at Italian airports and of airlines and air traffic control, from the official register. Updated daily.",
           corpo, briciole=[("Airports", "airports/")], con_dati=True)


# ---------------------------------------------------------------- guide
def a_(chiave, testo):
    u = L(chiave)
    return f'<a href="{escape(u)}" rel="noopener">{testo}</a>' if u else testo


def guide():
    rel = "../../"
    G = []

    def guida(slug, titolo, descr, html):
        G.append((slug, titolo, descr))
        corpo = f'<section class="hero"><h1>{escape(titolo)}</h1><p class="lead">{escape(descr)}</p></section><div class="testo">{html}</div>{AD}{modulo(rel)}'
        pagina(f"guides/{slug}/", titolo + f" | {NOME}", descr, corpo, briciole=[("Guides", "guides/"), (titolo, f"guides/{slug}/")])

    guida("how-strikes-work-in-italy", "How strikes work in Italy",
          "Why there are so many transport strikes in Italy, how much notice is required and what keeps running.", f"""
<p>In Italy, strikes in essential public services – including trains, flights, local transport and ferries – are regulated by {a_("legge_146_1990", "Law 146 of 1990")}. The main rules that matter to travellers:</p>
<ul>
<li><strong>At least 10 days' notice.</strong> Unions must announce a strike at least 10 days before it starts. That is why a strike that is not in the register a week before your trip is unlikely to happen.</li>
<li><strong>Minimum services.</strong> Some services must keep running: guaranteed trains, guaranteed flights in set time slots, and guaranteed hours for buses and metro.</li>
<li><strong>The official register.</strong> Every announced strike is listed by the Ministry of Infrastructure and Transport in its <a href="{URL_REGISTRO}" rel="noopener">strike register</a>. This site reads that register every day.</li>
<li><strong>An independent authority</strong>, the {a_("cgsse_home", "Commissione di garanzia")} (strike guarantee commission), checks that the rules are respected and can ask unions to change or postpone strikes.</li>
<li><strong>Calling off.</strong> Strikes are sometimes called off or postponed, even a few days before. When a strike disappears from the register before its date, we flag it.</li>
<li><strong>Holiday periods.</strong> Some periods (for example around Christmas and in parts of the summer) are protected and transport strikes are not allowed then. The exact dates depend on the sector.</li>
</ul>
<h2>How long do strikes last?</h2>
<p>Local bus and metro strikes are often 4 hours or 24 hours. National rail strikes usually run from 21:00 the evening before to 21:00 on the strike day. Air transport strikes are often 4 or 24 hours. Every strike on this site shows the exact hours from the register.</p>
<h2>Where to check</h2>
<p>Use the <a href="{rel}today/">today</a> and <a href="{rel}tomorrow/">tomorrow</a> pages, your <a href="{rel}#cities">city</a> or your <a href="{rel}airports/">airport</a>, and always confirm with your operator.</p>""")

    guida("guaranteed-trains", "Guaranteed trains during strikes in Italy",
          "Which trains still run during a rail strike in Italy, and where to find the official list.", f"""
<p>During a national rail strike, some trains are guaranteed by law. The details are published by each operator before every strike:</p>
<ul>
<li><strong>Trenitalia</strong> (Frecciarossa, Intercity, regional trains): see {a_("trenitalia_garantiti", "Trenitalia's list of guaranteed trains")} (in Italian), {a_("trenitalia_en", "Trenitalia's strike information in English")}{" and " + a_("trenitalia_infomobilita", "Trenitalia live travel news") if L("trenitalia_infomobilita") else ""}.</li>
<li><strong>Italo</strong>: strike notices and the list of guaranteed trains appear on {a_("italo_scioperi", "Italo's home page")} before each strike.</li>
<li><strong>Trenord</strong> (Lombardy, including Malpensa Express): see {a_("trenord_scioperi", "Trenord's strike information")}.</li>
</ul>
<h2>Typical rules</h2>
<ul>
<li>Trenitalia regional trains run in the peak hours: on weekdays from 06:00 to 09:00 and from 18:00 to 21:00; on public holidays from 07:00 to 10:00 and from 18:00 to 21:00.</li>
<li>Some long-distance trains (Frecce, Intercity) are guaranteed every day: they are in Trenitalia's table of guaranteed trains.</li>
<li>Trains already travelling when the strike starts reach their final destination if it can be reached within one hour of the start of the strike; after that they may stop at an earlier station.</li>
</ul>
<p>Source: {a_("trenitalia_garantiti", "Trenitalia, guaranteed services in case of strike")} (checked 10 October 2026). Other operators have their own lists: always check the one for your strike and train.</p>
<h2>Refunds</h2>
<p>If your train is cancelled because of a strike you can usually ask the operator for a refund or change. Rules and deadlines are on the operator's site; see also {a_("eu_rail_rights", "EU rail passenger rights")}.</p>
<p>See <a href="{rel}trains/">upcoming train strikes</a>.</p>""")

    guida("flights-during-strikes", "Flights during strikes in Italy",
          "What happens to your flight during an Italian air transport strike: guaranteed time slots and guaranteed flights.", f"""
<p>Air transport strikes in Italy can involve an airline's pilots and cabin crew, air traffic control (ENAV), airport ground handling or security staff. A strike of one airline's crew only affects that airline; an air traffic control strike can affect all flights in the area it covers.</p>
<h2>What is guaranteed</h2>
<ul>
<li>Flights scheduled between <strong>07:00 and 10:00</strong> and between <strong>18:00 and 21:00</strong> must operate during strikes (protected time slots).</li>
<li>A list of essential flights (for example to the islands) is guaranteed as well: see {a_("enac_voli_garantiti", "ENAC's guaranteed flights")} (Italian civil aviation authority, checked 10 October 2026).</li>
<li>Your airline decides which flights to cancel and must tell you.</li>
</ul>
<h2>What to do</h2>
<ul><li>Check your flight status with your airline the day before and on the day.</li>
<li>If your flight is cancelled, the airline must offer a refund or rerouting. Whether compensation is due depends on who is striking: check {a_("eu_air_rights", "EU air passenger rights")} and your airline.</li></ul>
<p>See <a href="{rel}flights/">upcoming flight strikes</a> and <a href="{rel}airports/">strikes by airport</a>.</p>""")

    ops = "".join(f'<li><strong>{escape(c["nome"])}</strong>: {", ".join(link_operatori(c)) or "check the local operator"}</li>' for c in CITTA)
    guida("local-transport-strike-hours", "Bus and metro strikes in Italy: guaranteed hours",
          "During local transport strikes, buses, trams and metro still run at set times. Here is where to find them for each city.", f"""
<p>Local transport strikes (city buses, metro, trams, water buses) last 4 hours or 24 hours. During a 24-hour strike each company must guarantee service in two time windows, usually the morning commute and part of the afternoon or evening. The exact hours are different in every city.</p>
<ul>{ops}</ul>
<p>Strikes of only 4 hours usually have no guaranteed hours inside the 4 hours. Check the operator page for your strike.</p>
<p>Taxis are not normally affected by bus and metro strikes, but they are in high demand on those days.</p>""")

    guida("general-strikes", "What a general strike in Italy means for travellers",
          "General strikes can involve all sectors at once. How to read the register and what usually happens to transport.", f"""
<p>A <em>sciopero generale</em> (general strike) is called by one or more unions for many sectors at the same time. Big confederations sometimes call national general strikes; smaller unions call them more often, with less impact.</p>
<ul>
<li>The register says which transport sectors join and at what hours. For example, rail often from 21:00 the evening before to 21:00 on the day; local transport with the guaranteed hours of each city.</li>
<li>Sometimes the register note excludes some sectors (for example air transport). We show the original note and a short summary.</li>
<li>Guaranteed services still apply in each sector: <a href="{rel}guides/guaranteed-trains/">trains</a>, <a href="{rel}guides/flights-during-strikes/">flights</a>, <a href="{rel}guides/local-transport-strike-hours/">buses and metro</a>.</li>
</ul>
<p>See <a href="{rel}general-strikes/">upcoming general strikes</a>.</p>""")

    guida("how-to-read-the-register", "How to read the Italian strike register",
          "The official register of the Ministry of Infrastructure and Transport, column by column, with our English terms.", f"""
<p>The <a href="{URL_REGISTRO}" rel="noopener">register</a> is published by the Ministry of Infrastructure and Transport (MIT) and updated by its office for union disputes. It lists announced strikes only; past strikes are removed.</p>
<table style="width:100%;border-collapse:collapse;font-size:.95rem"><tr><th style="text-align:left">Register (Italian)</th><th style="text-align:left">On this site</th></tr>
<tr><td>Inizio / Fine</td><td>Start / end date</td></tr><tr><td>Settore</td><td>Sector: Aereo = air, Ferroviario = rail, Trasporto pubblico locale = local transport, Marittimo = ferries and ports, Trasporto merci = freight, Generale = general strike, Plurisettoriale = multi-sector, Circolazione e sicurezza stradale = motorway services</td></tr>
<tr><td>Rilevanza</td><td>Scope: Nazionale (national), Regionale, Provinciale, Locale</td></tr>
<tr><td>Modalità</td><td>Hours (we show the original and an English version)</td></tr>
<tr><td>Categoria interessata</td><td>Who is striking (company and staff)</td></tr>
<tr><td>Sindacati</td><td>Unions</td></tr><tr><td>Data proclamazione</td><td>Date the strike was announced</td></tr>
<tr><td>Note</td><td>Notes, for example excluded sectors (shown as "Register note")</td></tr></table>
<p>Each strike on this site shows the MIT id so you can find it in the register. If a strike disappears from the register before its date we mark it as "No longer in the register": it was probably called off, but check with the operator.</p>""")

    guida("refunds-and-your-rights", "Strikes, refunds and your rights",
          "Where to find the official rules on refunds when a train or flight is cancelled because of a strike.", f"""
<p>We do not give legal advice. These are the official sources:</p>
<ul>
<li>Flights: {a_("eu_air_rights", "EU air passenger rights (Your Europe)")} and your airline's conditions.</li>
<li>Trains: {a_("eu_rail_rights", "EU rail passenger rights (Your Europe)")}, {a_("trenitalia_garantiti", "Trenitalia")}, {a_("italo_scioperi", "Italo")}.</li>
<li>Local transport: the operator's site (see <a href="{rel}guides/local-transport-strike-hours/">bus and metro strikes</a>).</li>
</ul>
<p>If you booked a package or a tour, contact the organiser as well.</p>""")

    strumenti = ""
    if satelliti_attivi():
        strumenti = ('<h2>Tools for visitors</h2><div class="griglia"><a href="../codice-fiscale-calculator/">Codice fiscale calculator'
                     '<small>Italian tax code for foreigners</small></a><a href="../ztl-fines/">ZTL fines in Italy<small>amounts, deadlines, how to pay</small></a></div>')
    corpo = '<section class="hero"><h1>Guides</h1><p class="lead">Short, practical guides about transport strikes in Italy.</p></section><div class="griglia">' + "".join(
        f'<a href="{s}/">{escape(t)}</a>' for s, t, _ in G) + "</div>" + strumenti
    pagina("guides/", "Guides to strikes in Italy | " + NOME, "Practical guides for travellers about transport strikes in Italy.", corpo,
           briciole=[("Guides", "guides/")])


# ---------------------------------------------------------------- satelliti
def italiano_attivo():
    return VERSIONE_IT_ATTIVA or os.environ.get("ITALYSTRIKES_IT") == "1"


def satelliti_attivi():
    return SATELLITI_ATTIVI or os.environ.get("ITALYSTRIKES_SATELLITI") == "1"


CF_JS = r"""
(function(){
  var ODD={},EVEN={},o=[1,0,5,7,9,13,15,17,19,21],oa=[1,0,5,7,9,13,15,17,19,21,2,4,18,20,11,3,6,8,12,14,16,10,22,25,24,23];
  for(var i=0;i<10;i++){ODD[String(i)]=o[i];EVEN[String(i)]=i;}
  for(i=0;i<26;i++){var ch=String.fromCharCode(65+i);ODD[ch]=oa[i];EVEN[ch]=i;}
  function pulisci(s){return (s||'').toUpperCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^A-Z]/g,'');}
  function cons(s){return s.replace(/[^BCDFGHJKLMNPQRSTVWXYZ]/g,'');}
  function voc(s){return s.replace(/[^AEIOU]/g,'');}
  function cognome(s){return (cons(s)+voc(s)+'XXX').slice(0,3);}
  function nome(s){var c=cons(s);return c.length>=4?c[0]+c[2]+c[3]:(c+voc(s)+'XXX').slice(0,3);}
  function calcola(cg,nm,data,sesso,luogo){
    var p=data.split('-'),y=p[0],m=+p[1],d=+p[2];
    var x=cognome(cg)+nome(nm)+y.slice(2)+'ABCDEHLMPRST'[m-1]+('0'+(d+(sesso==='F'?40:0))).slice(-2)+luogo;
    var t=0;for(var k=0;k<x.length;k++){t+=(k%2===0?ODD:EVEN)[x[k]];}
    return x+String.fromCharCode(65+t%26);
  }
  var f=document.getElementById('cf-form');if(!f)return;
  var tipo=f.querySelectorAll('input[name=tipo]'),boxE=document.getElementById('cf-estero'),boxI=document.getElementById('cf-italia');
  var comuni=null,inp=document.getElementById('cf-comune'),sugg=document.getElementById('cf-sugg'),scelto=null;
  function mostra(){var e=f.querySelector('input[name=tipo]:checked').value==='estero';boxE.hidden=!e;boxI.hidden=e;
    if(!e&&!comuni){fetch('comuni.json').then(function(r){return r.json();}).then(function(j){comuni=j.comuni;});}}
  tipo.forEach(function(r){r.addEventListener('change',mostra);});mostra();
  inp.addEventListener('input',function(){scelto=null;var q=inp.value.trim().toUpperCase();sugg.innerHTML='';if(!comuni||q.length<2)return;
    var n=0;for(var i=0;i<comuni.length&&n<8;i++){if(comuni[i][0].toUpperCase().indexOf(q)===0){var li=document.createElement('li');
      var b=document.createElement('button');b.type='button';b.textContent=comuni[i][0]+' ('+comuni[i][1]+')';b.dataset.c=comuni[i][2];b.dataset.n=comuni[i][0]+' ('+comuni[i][1]+')';
      b.addEventListener('click',function(){scelto=this.dataset.c;inp.value=this.dataset.n;sugg.innerHTML='';});li.appendChild(b);sugg.appendChild(li);n++;}}});
  f.addEventListener('submit',function(ev){ev.preventDefault();var out=document.getElementById('cf-out'),err=document.getElementById('cf-err');out.hidden=true;err.hidden=true;
    var cg=pulisci(f.surname.value),nm=pulisci(f.given.value),dt=f.birth.value,sx=f.querySelector('input[name=sex]:checked');
    var e=f.querySelector('input[name=tipo]:checked').value==='estero',luogo=e?f.country.value:scelto;
    var msg=!cg?'Please enter your surname (letters only).':!nm?'Please enter your given name(s).':!dt?'Please enter your date of birth.':!sx?'Please choose sex as shown on your passport.':!luogo?(e?'Please choose your country of birth.':'Please choose your place of birth from the list.'):'';
    if(msg){err.textContent=msg;err.hidden=false;return;}
    var c=calcola(cg,nm,dt,sx.value,luogo);document.getElementById('cf-code').textContent=c;out.hidden=false;});
  var cp=document.getElementById('cf-copy');if(cp)cp.addEventListener('click',function(){try{navigator.clipboard.writeText(document.getElementById('cf-code').textContent);cp.textContent='Copied';}catch(e){}});
})();
"""


def pagina_codice_fiscale():
    rel = "../"
    esteri = json.loads((RADICE / "satelliti" / "cf-esteri.json").read_text(encoding="utf-8"))
    comuni = json.loads((RADICE / "satelliti" / "cf-comuni.json").read_text(encoding="utf-8"))
    opz = "".join(f'<option value="{p["c"]}">{escape(p["en"])}</option>' for p in esteri["paesi"])
    url_ade = "https://www.agenziaentrate.gov.it/portale/web/english/nse/individuals/tax-identification-number-for-foreign-citizens"
    url_verifica = "https://telematici.agenziaentrate.gov.it/VerificaCF/Scegli.do?parameter=verificaCf"
    corpo = f"""<section class="hero"><h1>Codice fiscale calculator for foreigners</h1>
<p class="lead">Work out the Italian tax code (codice fiscale) that matches your personal data, then get the official one from the Italian authorities. Free, nothing is sent to us: the calculation happens in your browser.</p></section>
<p class="avviso">Only the Italian Revenue Agency (Agenzia delle Entrate) can assign your official codice fiscale. In rare cases (two people with the same data) the official code is different from the calculated one. Use this to check or prepare, not as a substitute.</p>
<section class="card"><form id="cf-form" class="form" novalidate>
<div class="due-campi"><label>Surname (as on your passport)<input name="surname" autocomplete="family-name" required></label>
<label>Given name(s), all of them<input name="given" autocomplete="given-name" required></label></div>
<div class="due-campi"><label>Date of birth<input type="date" name="birth" min="1900-01-01" required></label>
<fieldset style="border:0;padding:0;margin:0"><legend style="font-weight:600;font-size:.95rem">Sex (as on your passport)</legend>
<label class="check"><input type="radio" name="sex" value="M"> Male</label><label class="check"><input type="radio" name="sex" value="F"> Female</label></fieldset></div>
<fieldset style="border:0;padding:0;margin:0"><legend style="font-weight:600;font-size:.95rem">Place of birth</legend>
<label class="check"><input type="radio" name="tipo" value="estero" checked> Outside Italy</label><label class="check"><input type="radio" name="tipo" value="italia"> In Italy</label></fieldset>
<label id="cf-estero">Country of birth<select name="country"><option value="">Choose your country</option>{opz}</select></label>
<div id="cf-italia" hidden><label>Italian town of birth<input id="cf-comune" autocomplete="off" placeholder="Start typing, e.g. Roma"></label><ul id="cf-sugg" class="sugg"></ul></div>
<button class="btn" type="submit">Calculate</button>
<p class="errore" id="cf-err" hidden></p>
</form>
<div id="cf-out" class="ok" hidden><p style="margin:0">Your calculated codice fiscale:</p><p style="font-size:1.6rem;font-weight:800;letter-spacing:.08em;margin:6px 0" id="cf-code"></p>
<button type="button" class="btn" id="cf-copy" style="padding:6px 12px">Copy</button>
<p class="small" style="margin:8px 0 0">Check it with the Revenue Agency's free <a href="{url_verifica}" rel="noopener">verification service</a> (in Italian).</p></div></section>
{AD}
<div class="testo">
<h2>How to get your official codice fiscale</h2>
<p>From the <a href="{url_ade}" rel="noopener">Agenzia delle Entrate page for foreign citizens</a> (checked 10 October 2026):</p>
<ul>
<li><strong>If you live abroad:</strong> apply to the Italian consulate in your country of residence.</li>
<li><strong>In Italy, non-EU citizens:</strong> the Single Desk for Immigration (Sportello Unico per l'Immigrazione) issues it to people entering Italy for work or family reunification, and the police headquarters (Questura) when you apply for or renew a residence permit.</li>
<li><strong>In all other cases:</strong> at an office of the Agenzia delle Entrate, with a valid ID document (non-EU citizens: passport with visa if required, or residence permit, and proof of the right to stay). For a first codice fiscale you must <strong>book an in-person appointment</strong>.</li>
<li><strong>EU citizens:</strong> any Agenzia delle Entrate office, with an ID card or passport.</li>
</ul>
<h2>How the code is built</h2>
<p>It has 16 characters: 3 letters from your surname, 3 from your given names, 2 digits for the year of birth, a letter for the month, 2 digits for the day (plus 40 for women), a 4-character code for the place of birth (for people born abroad, "Z" and three digits for the country) and a final check letter.</p>
<h2>Limits of this calculator</h2>
<ul><li>Countries: the current list of the Italian national population register (ANPR, Ministry of the Interior). If you were born in a country that no longer exists, the official code may use a historical country code.</li>
<li>Italian towns: ISTAT list of current municipalities. Towns merged or abolished in the past are not included.</li>
<li>Same-data cases ("omocodia") are handled only by the Agenzia delle Entrate.</li></ul>
<p class="small">Sources: country codes from the <a href="{escape(esteri['meta']['fonte_esteri'])}" rel="noopener">ANPR foreign states table</a>; town codes from <a href="{escape(comuni['meta']['fonte_comuni'])}" rel="noopener">ISTAT</a>; read on {escape(esteri['meta']['letto_il'])}.</p>
</div>
<style>.sugg{{list-style:none;margin:4px 0 0;padding:0;display:grid;gap:4px}}.sugg button{{font:inherit;width:100%;text-align:left;padding:8px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink);cursor:pointer}}fieldset .check{{display:inline-flex;margin-right:16px}}</style>
<script>{CF_JS}</script>"""
    pagina("codice-fiscale-calculator/", "Codice fiscale calculator for foreigners (Italian tax code)",
           "Calculate the Italian codice fiscale for people born abroad or in Italy, and learn how foreigners get the official one from the Agenzia delle Entrate.",
           corpo, briciole=[("Codice fiscale calculator", "codice-fiscale-calculator/")])
    (SITO / "codice-fiscale-calculator" / "comuni.json").write_text(
        json.dumps({"comuni": comuni["comuni"]}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def pagina_ztl():
    rel = "../"
    cds = "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:1992-04-30;285"
    citta_link = [("Rome", "https://romamobilita.it/servizi-al-pubblico/ztl/", "Roma Servizi per la Mobilità (city transport agency)"),
                  ("Milan", "https://www.comune.milano.it/aree-tematiche/mobilita/area-c", "Comune di Milano, Area C"),
                  ("Bologna", "https://www.comune.bologna.it/servizi-informazioni/ztl", "Comune di Bologna")]
    lista = "".join(f'<li><strong>{c}</strong>: <a href="{u}" rel="noopener">{escape(n)}</a></li>' for c, u, n in citta_link)
    corpo = f"""<section class="hero"><h1>ZTL fines in Italy: how much, when they arrive, how to pay</h1>
<p class="lead">ZTL means <em>zona a traffico limitato</em>, a limited traffic zone in a historic centre. Cameras at the entry gates record every plate: if you drive in without a permit you get a fine, often months later and often through your rental company.</p></section>
<p class="avviso">This page explains the national rules. Hours, zones and permits are set by each city and change often: always check the official city website or ask your hotel before you drive into a centre. Nothing here is legal advice.</p>
<div class="testo">
<h2>How much is a ZTL fine?</h2>
<ul><li>Driving into a ZTL, a pedestrian area or a bus lane without a permit costs <strong>from €83 to €332</strong> (Italian Highway Code, <a href="{cds}~art7" rel="noopener">Article 7, paragraph 14</a>, text checked 10 October 2026).</li>
<li>If you pay <strong>within 60 days</strong> of the notice you pay the minimum (€83). If you pay <strong>within 5 days</strong> it is reduced by <strong>30%</strong> (about €58), plus the notification costs written on the notice (<a href="{cds}~art202" rel="noopener">Article 202</a>).</li>
<li>Each gate you pass through can be recorded as a separate violation, so one wrong turn can mean more than one notice.</li></ul>
<h2>When does the fine arrive?</h2>
<ul><li>For people who live abroad, the notice must be served <strong>within 360 days</strong> of the violation being recorded (<a href="{cds}~art201" rel="noopener">Article 201</a>); the period runs from when the authorities are able to identify the driver.</li>
<li>With a rental car, the police first contact the rental company, which gives them your name and address. Rental companies usually charge you their own administration fee for this, separate from the fine: check your rental contract.</li></ul>
<h2>How to avoid it</h2>
<ul><li>Look for the round sign with a red border and the words <em>Zona Traffico Limitato</em>, and for the display at the gate: "varco attivo" means the camera is on and you must not enter; "varco non attivo" means the zone is open at that moment.</li>
<li>If your hotel is inside a ZTL, ask it before you arrive: in many cities hotels can register your plate for access to drop off luggage.</li>
<li>Park outside the centre and walk or take public transport. Satellite navigators do not always warn about ZTLs.</li></ul>
<h2>How to pay or appeal</h2>
<ul><li>The notice (<em>verbale</em>) explains how to pay, usually by bank transfer or online with the code printed on it. Keep the receipt.</li>
<li>Appeals go to the Prefect or the Justice of the Peace (<em>Giudice di Pace</em>) within the deadlines written on the notice. If you think the fine is wrong, read the notice carefully and consider local legal advice.</li></ul>
<h2>Official city pages</h2>
<ul>{lista}</ul>
<p class="small">Florence, Pisa, Siena, Naples, Turin and other cities have their own ZTLs: search "ZTL" on the official website of the municipality (<em>comune</em>) or ask your hotel. We list only official pages we could check.</p>
</div>
{box_affiliati()}
{AD}"""
    pagina("ztl-fines/", "ZTL fines in Italy: how much, when they arrive, how to pay",
           "Italian ZTL fines explained in English: amounts (€83-€332), 30% discount within 5 days, 360-day deadline for foreign residents, rental cars, how to avoid and pay.",
           corpo, briciole=[("ZTL fines in Italy", "ztl-fines/")])


def about():
    rel = "../"
    corpo = f"""<section class="hero"><h1>About {NOME} and our sources</h1></section><div class="testo">
<p>{NOME} is an independent project that makes the official Italian strike register easy to read in English for travellers. We are not affiliated with the Italian government, unions or transport operators.</p>
<h2>Where the data comes from</h2>
<ul><li>The <a href="{URL_REGISTRO}" rel="noopener">strike register of the Ministry of Infrastructure and Transport</a> and its RSS feed. We read it every day and keep our own archive, because the register removes strikes once they are over.</li>
<li>Guaranteed services: we link to the operators and authorities that publish them (Trenitalia, Italo, Trenord, ENAC, local transport companies). We do not copy their lists.</li></ul>
<h2>How we translate</h2>
<p>Sectors, scope and hours are translated automatically with fixed rules. The original Italian text is always shown next to the translation. If our rules cannot translate the hours, we show only the original.</p>
<h2>Limits</h2>
<p>Strikes can be called off or changed at short notice, and the register may be updated after our daily check. Always confirm with your operator before travelling.</p>
<p>Questions or corrections? <a href="{rel}contact/">Contact us</a>.</p></div>"""
    pagina("about/", f"About and sources | {NOME}", "Where our strike data comes from and how we translate it.", corpo, briciole=[("About", "about/")])


def contatti():
    rel = "../"
    corpo = f"""<section class="hero"><h1>Contact</h1><p class="lead">Corrections, questions or feedback: write to us here.</p></section>
<section class="card"><form class="form ajax" name="contact" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="contact"><input type="hidden" name="source" value="">
<p class="hp"><label>Do not fill this in <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Your email<input type="email" name="email" required autocomplete="email"></label>
<label>Message<textarea name="message" rows="6" required maxlength="4000"></textarea></label>
<label class="check"><input type="checkbox" name="consent" value="yes" required><span>I have read the <a href="{rel}privacy.html">privacy notice</a>.</span></label>
<button class="btn" type="submit">Send</button><p class="errore" data-errore hidden>Sorry, it did not work. Please try again.</p></form>
<div class="ok" data-ok hidden><strong>Thank you.</strong> We will reply by email.</div></section>"""
    pagina("contact/", f"Contact | {NOME}", f"Contact {NOME}.", corpo, briciole=[("Contact", "contact/")])


def privacy():
    corpo = f"""<section class="hero"><h1>Privacy notice</h1><p class="small">Last updated: October 2026</p></section><div class="testo">
<h2>Who is responsible</h2><p>The data controller is Massimiliano Cori (Italy), who runs {NOME} as an independent project. You can contact us through the <a href="contact/">contact form</a> or by replying to any email we send.</p>
<h2>What we collect</h2><p>Only what you type in our forms: for strike alerts, your email, travel dates and place; for the contact form, your email and message. We also record the page or link you came from, to understand which channels work.</p>
<h2>Why</h2><p>To send you strike alerts for your travel dates, and to answer your messages. The legal basis is your consent (Art. 6(1)(a) GDPR), which you can withdraw at any time.</p>
<h2>Who processes data for us</h2><p>The site and its forms are hosted by Netlify, Inc., which stores form data on our behalf and may process it outside the EU with the safeguards required by the GDPR (standard contractual clauses). We do not sell or share your data.</p>
<h2>Cookies</h2><p>This site does not use profiling cookies or analytics tools. If we add advertising in the future, we will update this notice and ask for your consent where required before any advertising cookies are used.</p>
<h2>How long</h2><p>Alert data is kept until your travel dates have passed, and then deleted within 60 days, unless you ask us to delete it earlier.</p>
<h2>Your rights</h2><p>You can ask for access, correction, deletion, restriction, portability and objection (Articles 15–22 GDPR) and you can complain to the Italian data protection authority (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>) or the authority in your country.</p></div>"""
    pagina("privacy.html", f"Privacy | {NOME}", f"Privacy notice of {NOME}.", corpo)


def extra():
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n")
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{OGGI.isoformat()}</lastmod></url>" for u in URLS)
    (SITO / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n')
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in italystrikes/sito (ogni pubblicazione consuma crediti Netlify).
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."

[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    X-Frame-Options = "DENY"
    Permissions-Policy = "camera=(), microphone=(), geolocation=()"
""")
    pagina("404.html", f"Page not found | {NOME}", "Page not found.",
           '<section class="hero"><h1>Page not found</h1><p class="lead">Go to <a href="/">strikes today and tomorrow</a>.</p></section>', indicizza=False)


def controlli():
    errori = []
    for s in scioperi.values():
        for k in ("id", "inizio", "fine", "settore", "proclamazione"):
            if not s.get(k):
                errori.append(f"sciopero senza {k}: {s.get('id')}")
        if s.get("fine", "") < s.get("inizio", ""):
            errori.append(f"fine prima dell'inizio: {s['id']}")
    for v in VOCI:
        if v["settore_it"] not in SETTORE_EN:
            print(f"ATTENZIONE: settore nuovo non tradotto: {v['settore_it']} (id {v['id']})")
    if errori:
        raise SystemExit("ERRORI NEI DATI:\n" + "\n".join(errori))


def main():
    controlli()
    scrivi_vista()
    if "--solo-dati" in sys.argv:
        print(f"vista.json aggiornato: {len(recenti())} scioperi.")
        return
    conserva = {}
    if SITO.exists():
        conserva = {p.name: p.read_bytes() for p in SITO.glob("google*.html")}
        shutil.rmtree(SITO)
    SITO.mkdir()
    shutil.copy(RADICE / "assets" / "og.png", SITO / "og.png")
    for nome, contenuto in conserva.items():
        (SITO / nome).write_bytes(contenuto)
    home()
    pagina_finestra("today", "today", "Strikes in Italy today", "Italy strike today: trains, flights, buses – official list",
                    "Is there a strike in Italy today? Every transport strike listed for today in the official register: trains, flights, airports, buses, metro.")
    pagina_finestra("tomorrow", "tomorrow", "Strikes in Italy tomorrow", "Italy strike tomorrow: trains, flights, buses – official list",
                    "Is there a strike in Italy tomorrow? Every transport strike listed for tomorrow in the official register: trains, flights, airports, buses, metro.")
    pagina_finestra("this-week", "thisweek", "Strikes in Italy this week", "Italy strikes this week: trains, flights, buses, metro",
                    "Transport strikes in Italy for the rest of this week, from the official register, in English.")
    pagina_finestra("next-week", "nextweek", "Strikes in Italy next week", "Italy strikes next week: trains, flights, buses, metro",
                    "Transport strikes in Italy next week, from the official register, in English.")
    for y, m in mesi_da_mostrare():
        pagina_mese(y, m)
    for s in SETTORI:
        pagina_settore(s)
    for c in CITTA:
        pagina_citta(c)
    indice_aeroporti()
    for a in AEROPORTI:
        pagina_aeroporto(a)
    guide()
    if satelliti_attivi():
        pagina_codice_fiscale()
        pagina_ztl()
    about()
    contatti()
    privacy()
    if italiano_attivo():
        import genera_it
        genera_it.costruisci(sys.modules[__name__])
    extra()
    print(f"Sito generato in {SITO}: {len(URLS)} pagine; {len(filtra('upcoming', 'all'))} scioperi in programma, "
          f"{len(VOCI)} nell'archivio. Registro aggiornato al {AGGIORNATO}.")


if __name__ == "__main__":
    main()
