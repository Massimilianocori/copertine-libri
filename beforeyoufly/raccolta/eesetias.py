"""Controlla lo stato ufficiale di EES ed ETIAS e scrive dati/ees_etias.json.

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/eesetias.py

Fonti (tutte ufficiali):
  - Commissione europea, DG Migration and Home Affairs: pagina Smart Borders, pagina EES, notizia del 30/3/2026.
  - GOV.UK (FCDO), travel advice Spain, sezione "New Schengen entry requirements" (Content API, OGL v3).
  Il sito travel-europe.europa.eu (sito ufficiale EES/ETIAS) non è leggibile dal server: certificato TLS incompleto.
  Non si disattiva la verifica TLS: lo si cita solo come link.

Il sito pubblica SOLO le frasi elencate in FRASI_UE che risultano presenti, parola per parola, nella pagina scaricata.
Se una frase sparisce (per esempio "ETIAS is currently not in operation"), lo script lo segnala ed esce con 1:
è il segnale che lo stato è cambiato e la pagina va riscritta a mano.
"""
import json
import re
import sys
import urllib.request
from datetime import date
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"

PAGINE_UE = {
    "smart_borders": ("https://home-affairs.ec.europa.eu/policies/schengen/smart-borders_en", "European Commission – Smart Borders"),
    "ees": ("https://home-affairs.ec.europa.eu/policies/schengen/smart-borders/entry-exit-system_en", "European Commission – Entry/Exit System (EES)"),
    "notizia": ("https://home-affairs.ec.europa.eu/news/entryexit-system-will-become-fully-operational-10-april-2026-2026-03-30_en",
                "European Commission news, 30 March 2026 – The Entry/Exit System will become fully operational on 10 April 2026"),
}
# (chiave pagina, argomento, frase esatta da cercare)
FRASI_UE = [
    ("smart_borders", "etias", "ETIAS is currently not in operation and no applications for travel authorisations are collected at this point."),
    ("smart_borders", "etias", "The European Union will inform about the specific date for the start of ETIAS several months prior to its launch."),
    ("smart_borders", "ees", "The Entry Exit System is fully operational since 10 April 2026."),
    ("ees", "ees", "The EES is an automated IT system for registering non-EU nationals travelling for a short stay, each time they cross the external borders of 29 European countries using the system."),
    ("ees", "ees", "The system registers the person's name, travel document data, biometric data (fingerprints and captured facial images) and the date and place of entry and exit, in full respect of fundamental rights and data protection."),
    ("ees", "ees", "As of 10 April 2026, the EES replaces the stamping of passports allowing the automatic detection of overstayers (travellers who have exceeded the maximum duration of their authorised stay)."),
    ("ees", "ees", "On 30 July 2025, the Commission set 12 October 2025 as the launch date for the progressive start of operations of the Entry/Exit System (EES). The system became fully operational on 10 April 2026."),
    ("notizia", "ees", "The EU’s new Entry/Exit System (EES) started operations on 12 October 2025 with a progressive roll-out in 29 European countries."),
]
GOVUK = ("https://www.gov.uk/api/content/foreign-travel-advice/spain", "https://www.gov.uk/foreign-travel-advice/spain/entry-requirements",
         "GOV.UK (FCDO) – Spain travel advice, Entry requirements: 'New Schengen entry requirements'")
FRASI_GOVUK = [
    "This means that when you travel into the Schengen area for short stays, you may need to register your biometric details, such as fingerprints and a photo. There is no cost for EES registration.",
    "On your first visit into a Schengen country, you may be asked to register your details at a special booth before proceeding to the immigration desk.",
    "Children aged 11 or younger will not have their fingerprints scanned but can be required to have their photo taken.",
    "You do not need to take any action before you arrive at the border on entry to the Schengen area, but EES may take each passenger extra time to complete so be prepared to wait longer than usual at the border and to allow more time for immigration controls when you depart the Schengen area.",
    "If you are departing the Schengen area by plane, allow extra time to reach your departure gate as EES checks may take place before boarding.",
    "If you enter the Schengen area through the Port of Dover, Eurotunnel at Folkestone or Eurostar at St Pancras International, any information will be taken at the border before you leave the UK.",
    "Your digital EES record is valid for 3 years.",
    "If you are long-term resident in a Schengen country, you are exempt from EES in all Schengen countries.",
]


def leggi(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.status, r.read().decode("utf-8", "replace")


def testo(html_):
    t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", html_)
    t = re.sub(r"</?(?:strong|b|em|i|a|span|abbr)\b[^>]*>", "", t)  # tag in linea: nessuno spazio
    t = unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return re.sub(r"\s+", " ", t)


def norm(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def main():
    oggi = date.today().isoformat()
    pagine, mancanti = {}, []
    for k, (url, titolo) in PAGINE_UE.items():
        try:
            stato, h = leggi(url)
        except Exception as e:  # noqa: BLE001
            print(f"ERRORE {url}: {e}")
            stato, h = 0, ""
        m = re.search(r'"dateModified"\s*:\s*"([0-9-]{10})', h)
        pagine[k] = {"url": url, "titolo": titolo, "http": stato, "modificata": m.group(1) if m else None, "_t": norm(testo(h))}
    frasi = []
    for k, arg, f in FRASI_UE:
        c = norm(f) in pagine[k]["_t"]
        if not c:
            mancanti.append(f"{k}: {f[:80]}")
        frasi.append({"pagina": k, "argomento": arg, "frase": f, "trovata": c})
    try:
        _, corpo = leggi(GOVUK[0])
        j = json.loads(corpo)
        ent = [p for p in j["details"]["parts"] if p["slug"] == "entry-requirements"][0]["body"]
        t_gov = norm(testo(ent))
        agg = j["public_updated_at"][:10]
    except Exception as e:  # noqa: BLE001
        print(f"ERRORE GOV.UK: {e}")
        t_gov, agg = "", None
    gov = []
    for f in FRASI_GOVUK:
        c = norm(f) in t_gov
        if not c:
            mancanti.append(f"govuk: {f[:80]}")
        gov.append({"frase": f, "trovata": c})
    for p in pagine.values():
        p.pop("_t")
    out = {"controllato_il": oggi, "pagine": pagine, "frasi": frasi,
           "govuk": {"url": GOVUK[1], "api": GOVUK[0], "titolo": GOVUK[2], "aggiornata": agg, "frasi": gov,
                     "licenza": "Open Government Licence v3.0"},
           "sito_ufficiale": {"ees": "https://travel-europe.europa.eu/ees_en", "etias": "https://travel-europe.europa.eu/etias_en",
                              "nota": "Official EU website for EES and ETIAS. Not readable from our server (incomplete TLS certificate chain), so we link to it but quote the European Commission pages above."}}
    (DATI / "ees_etias.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Frasi ufficiali trovate: {sum(f['trovata'] for f in frasi)}/{len(frasi)} (UE), {sum(g['trovata'] for g in gov)}/{len(gov)} (GOV.UK)")
    if mancanti:
        print("ATTENZIONE: frasi non più presenti (lo stato può essere cambiato, ricontrollare a mano):")
        for m in mancanti:
            print("  -", m)
        sys.exit(1)


if __name__ == "__main__":
    main()
