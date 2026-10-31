"""Animali in viaggio (sezione "Pets", dal 31/10/2026): dal Regno Unito all'UE con cane, gatto o furetto. Rilegge le fonti ufficiali e segnala i cambi.

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/animali.py             rilegge le fonti, controlla le frasi citate, legge le tabelle, scrive dati/animali.json
    python3 -I beforeyoufly/raccolta/animali.py --cache     come sopra ma senza rete, dalle copie in raccolta/.cache/animali/
    python3 -I beforeyoufly/raccolta/animali.py --domanda   rilegge anche l'autocompletamento di Google (dati/animali_domanda.json)
    python3 -I beforeyoufly/raccolta/animali.py --testo ID  stampa il testo normalizzato di una fonte (per scrivere le citazioni)

Regole (decise il 31/10/2026, piano: studio-business/intelaiatura/idee-2026-10-30-animali.md, sezioni 2-4):
  - Solo fonti ufficiali: GOV.UK (guide dell'APHA e di Defra, lette dall'API dei contenuti di GOV.UK, licenza OGL v3.0) e Commissione europea
    (DG SANTE, food.ec.europa.eu, riutilizzo con citazione della fonte). EUR-Lex risponde 202 vuoto dal server (controllo anti-robot): non si
    aggira; le regole UE (Regolamento delegato (UE) 2026/131: la pagina della Commissione lo cita come testo in vigore e parla di passaporti
    «issued before 22 April 2026»; che abbia preso il posto del Regolamento (UE) 576/2013 non è scritto nella pagina, quindi il sito non lo dice)
    si citano dalla pagina della Commissione che le riassume.
  - I fatti sono scritti a mano in dati/animali_manuali.json: ogni frase mostrata sul sito tra virgolette è una citazione parola per parola
    ("citazioni"). Nessun consiglio veterinario: ogni pagina rimanda al veterinario e alla pagina ufficiale.
  - Le tabelle ufficiali delle compagnie aeree e delle rotte via mare e treno approvate per entrare in Gran Bretagna (GOV.UK, pubblicazione
    "Pet travel: approved air, sea and rail carriers and routes") si leggono dall'API dei contenuti e si copiano riga per riga. Degli operatori
    charter (voli privati, circa 570 righe) si salvano solo il numero e l'impronta: alcuni nomi coincidono con nomi di assistenti di
    intelligenza artificiale, che i dati e il sito non devono contenere; la pagina rimanda alla sezione "Charter airlines" di GOV.UK.
  - I collegamenti della Commissione per ogni Paese (punti di ingresso dei viaggiatori e informazioni nazionali) si leggono dalle due pagine
    della Commissione e si mostrano come link "della Commissione": non leggiamo le pagine nazionali (metà non risponde dal server).
  - La lettura vale solo con HTTP 200. Se una fonte non risponde 200, se una citazione non c'è più nel testo normalizzato o se una tabella
    è vuota, lo script NON sovrascrive dati/animali.json ed esce con 1: si ricontrolla a mano.
  - Impronta (SHA-256, 16 caratteri) della "zona citata" di ogni fonte, come raccolta/pedaggi.py: se cambia, il cambio va in
    dati/animali_cambi.json (rileggere la pagina). Per le tabelle l'impronta è quella delle righe lette.
  - Pagine grezze in raccolta/.cache/animali/ (escluse da git).
"""
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
CACHE = Path(__file__).resolve().parent / ".cache" / "animali"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
GOVUK_API = "https://www.gov.uk/api/content/"
UE = "https://food.ec.europa.eu/animals/live-animal-movements/dogs-cats-and-ferrets/"
PUBBL = "government/publications/pet-travel-approved-air-sea-and-rail-carriers-and-routes"

# id -> url letto, pagina da mostrare ai lettori, ente, titolo, tipo (govuk = JSON dell'API dei contenuti, html = pagina)
FONTI = {
    "gov_estero": {"url": GOVUK_API + "taking-your-pet-abroad", "pagina": "https://www.gov.uk/taking-your-pet-abroad", "tipo": "govuk",
                   "ente": "GOV.UK (Animal and Plant Health Agency)", "titolo": "GOV.UK: Taking your pet dog, cat or ferret abroad"},
    "gov_gb": {"url": GOVUK_API + "bring-pet-to-great-britain", "pagina": "https://www.gov.uk/bring-pet-to-great-britain", "tipo": "govuk",
               "ente": "GOV.UK (Animal and Plant Health Agency)", "titolo": "GOV.UK: Bringing your pet dog, cat or ferret to Great Britain"},
    "gov_sps": {"url": GOVUK_API + "government/publications/sps-agreement-preparing-your-business/veterinary-sector-preparing-your-business",
                "pagina": "https://www.gov.uk/government/publications/sps-agreement-preparing-your-business/veterinary-sector-preparing-your-business",
                "tipo": "govuk", "ente": "GOV.UK (Department for Environment, Food & Rural Affairs)", "titolo": "GOV.UK: Veterinary sector: preparing your business (SPS agreement)"},
    "gov_rotte": {"url": GOVUK_API + PUBBL, "pagina": "https://www.gov.uk/" + PUBBL, "tipo": "govuk",
                  "ente": "GOV.UK (Animal and Plant Health Agency)", "titolo": "GOV.UK: Pet travel: approved air, sea and rail carriers and routes"},
    "gov_aria": {"url": GOVUK_API + PUBBL + "/approved-air-routes-for-pet-travel", "pagina": "https://www.gov.uk/" + PUBBL + "/approved-air-routes-for-pet-travel",
                 "tipo": "govuk", "ente": "GOV.UK (Animal and Plant Health Agency)", "titolo": "GOV.UK: Pet travel: airlines and airports you can use"},
    "gov_mare": {"url": GOVUK_API + PUBBL + "/pet-travel-sea-routes-and-companies-you-can-use",
                 "pagina": "https://www.gov.uk/" + PUBBL + "/pet-travel-sea-routes-and-companies-you-can-use",
                 "tipo": "govuk", "ente": "GOV.UK (Animal and Plant Health Agency)", "titolo": "GOV.UK: Pet travel: sea and rail routes and companies you can use"},
    "ue_condizioni": {"url": UE + "bringing-pet-eu-non-eu-country_en", "tipo": "html", "ente": "European Commission (DG Health and Food Safety)",
                      "titolo": "European Commission: Bringing a pet into the EU from a non-EU country"},
    "ue_ingresso": {"url": UE + "travellers-points-entry_en", "tipo": "html", "ente": "European Commission (DG Health and Food Safety)",
                    "titolo": "European Commission: Travellers' points of entry"},
    "ue_paesi": {"url": UE + "eu-countries-specific-information_en", "tipo": "html", "ente": "European Commission (DG Health and Food Safety)",
                 "titolo": "European Commission: EU countries' specific information"},
}

# Destinazioni: i 27 Paesi UE e la Norvegia (stesse regole UE per gli animali, nella lista del verme solitario di GOV.UK).
# nome = come lo scrivono le pagine della Commissione (link per Paese); query = come lo cercano le persone (autocompletamento).
PAESI = [
    ("AT", "Austria", "Austria", "austria"), ("BE", "Belgium", "Belgium", "belgium"), ("BG", "Bulgaria", "Bulgaria", "bulgaria"),
    ("HR", "Croatia", "Croatia", "croatia"), ("CY", "Cyprus", "Cyprus", "cyprus"), ("CZ", "Czechia", "Czechia", "czech republic"),
    ("DK", "Denmark", "Denmark", "denmark"), ("EE", "Estonia", "Estonia", "estonia"), ("FI", "Finland", "Finland", "finland"),
    ("FR", "France", "France", "france"), ("DE", "Germany", "Germany", "germany"), ("GR", "Greece", "Greece", "greece"),
    ("HU", "Hungary", "Hungary", "hungary"), ("IE", "Ireland", "Ireland", "ireland"), ("IT", "Italy", "Italy", "italy"),
    ("LV", "Latvia", "Latvia", "latvia"), ("LT", "Lithuania", "Lithuania", "lithuania"), ("LU", "Luxembourg", "Luxembourg", "luxembourg"),
    ("MT", "Malta", "Malta", "malta"), ("NL", "Netherlands", "The Netherlands", "netherlands"), ("PL", "Poland", "Poland", "poland"),
    ("PT", "Portugal", "Portugal", "portugal"), ("RO", "Romania", "Romania", "romania"), ("SK", "Slovakia", "Slovakia", "slovakia"),
    ("SI", "Slovenia", "Slovenia", "slovenia"), ("ES", "Spain", "Spain", "spain"), ("SE", "Sweden", "Sweden", "sweden"), ("NO", "Norway", "Norway", "norway"),
]

# Ricerche da rileggere con --domanda (autocompletamento, client=firefox, hl=en, gl=gb: il pubblico è chi parte dalla Gran Bretagna)
DOMANDA_MODELLI = ["taking dog to {p}", "taking dog to {p} from uk", "dog to {p} from uk", "taking cat to {p}"]
DOMANDA_GENERALI = ["animal health certificate", "animal health certificate dog", "ahc for dogs", "pet passport uk", "pet passport uk to eu",
                    "uk pet passport 2027", "pet passport 2027", "new pet passport rules uk", "taking dog to europe from uk", "taking dog abroad",
                    "taking a dog abroad from uk", "rabies vaccine dog travel", "how long after rabies vaccine can dog travel",
                    "tapeworm treatment for dogs travelling", "dog tapeworm treatment before travel", "bringing dog back to uk",
                    "bringing dog back to uk from france", "bringing dog to uk", "pet friendly airlines to uk", "dog friendly ferry",
                    "ferry with dog to", "eurotunnel dog", "flying dog to uk", "approved routes pet travel uk"]


def leggi(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-GB,en;q=0.9", "Accept": "text/html,application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.geturl(), r.read().decode("utf-8", "replace")


def testo_html(html_):
    """Testo visibile normalizzato (stesso metodo di raccolta/pedaggi.py): niente script e stili, tag in linea tolti, spazi unificati."""
    t = re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>|<!--.*?-->", " ", html_)
    t = re.sub(r"(?i)</?(?:strong|b|em|i|a|span|abbr|sup|u|font)\b[^>]*>", "", t)
    t = unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ").replace("​", "").replace("⁣", "").replace("﻿", "")
    t = re.sub(r"\s+", " ", t)
    return re.sub(r" ([,.;:!?])", r"\1", t).strip()


def corpo_govuk(raw):
    """HTML del contenuto di una pagina GOV.UK dall'API: le parti di una guida (titolo + testo) o il corpo di una pagina."""
    d = json.loads(raw)
    det = d.get("details", {})
    if det.get("parts"):
        return " ".join(f"<h2>{p['title']}</h2>{p['body']}" for p in det["parts"])
    return det.get("body", "")


def testo_fonte(raw, tipo="html"):
    return testo_html(corpo_govuk(raw) if tipo == "govuk" else raw)


def aggiornato_govuk(raw):
    """Data dell'ultimo aggiornamento pubblico dichiarato da GOV.UK (public_updated_at), solo il giorno."""
    return (json.loads(raw).get("public_updated_at") or "")[:10] or None


def frasi_fonte(M, fid):
    return [c["x"] for c in M["citazioni"] if c["f"] == fid]


def impronta(testo):
    return hashlib.sha256(testo.encode("utf-8")).hexdigest()[:16]


def impronta_zona(testo, frasi):
    pos = [(testo.find(x), len(x)) for x in frasi]
    if not pos or any(i < 0 for i, _ in pos):
        return None
    a, b = min(i for i, _ in pos), max(i + n for i, n in pos)
    return impronta(testo[a:b])


def _celle(riga):
    return [testo_html(c) for c in re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", riga)]


def tabelle_aria(raw):
    """Compagnie aeree approvate (GOV.UK): sezione (commerciali / charter), compagnia, aeroporti britannici così come scritti."""
    body = corpo_govuk(raw)
    out = []
    for sez in re.split(r'(?i)<h2 id="', body)[1:]:
        tipo = "commerciale" if sez.startswith("commercial-airlines") else ("charter" if sez.startswith("charter-airlines") else None)
        if not tipo:
            continue
        for riga in re.findall(r"(?is)<tbody>(.*?)</tbody>", sez):
            for tr in re.findall(r"(?is)<tr>(.*?)</tr>", riga):
                c = _celle(tr)
                if len(c) >= 2 and c[0]:
                    out.append({"tipo": tipo, "compagnia": c[0], "aeroporti": c[1]})
    return out


def tabelle_mare(raw):
    """Rotte via mare (per Paese di partenza), crociere e treni approvati (GOV.UK), riga per riga."""
    body = corpo_govuk(raw)
    out = {"mare": [], "crociera": [], "treno": []}
    parti = re.split(r'(?i)<h2 id="', body)
    for sez in parti[1:]:
        if sez.startswith("ferry-routes"):
            for blocco in re.split(r'(?i)<h3 id="', sez)[1:]:
                da = testo_html(re.search(r"(?is)>(.*?)</h3>", blocco).group(1))
                da = re.sub(r"^From (the )?", "", da)
                for tr in re.findall(r"(?is)<tbody>.*?</tbody>", blocco):
                    for r in re.findall(r"(?is)<tr>(.*?)</tr>", tr):
                        c = _celle(r)
                        if len(c) == 2:
                            out["mare"].append({"da": da, "rotta": c[0], "compagnia": c[1]})
        for chiave, nome in (("cruise-routes", "crociera"), ("rail-routes", "treno")):
            if sez.startswith(chiave):
                for tr in re.findall(r"(?is)<tbody>.*?</tbody>", sez):
                    for r in re.findall(r"(?is)<tr>(.*?)</tr>", tr):
                        c = _celle(r)
                        if len(c) == 3:
                            out[nome].append({"da": c[0], "rotta": c[1], "compagnia": c[2]})
    return out


def link_ue(raw, base="https://food.ec.europa.eu"):
    """Link della Commissione per Paese: {nome della pagina: [url, ...]} (il primo è quello del nome, poi le versioni inglesi)."""
    main = raw[raw.find("<main"):raw.find("</main>")] if "<main" in raw else raw
    out, ultimo = {}, None
    for href, t in re.findall(r'(?is)<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', main):
        t = testo_html(t)
        href = unescape(href)
        if href.startswith("/"):
            href = base + href
        m = re.fullmatch(r"(.+?) \([A-Z]{2}\)", t)
        if m:
            ultimo = m.group(1)
            out[ultimo] = [href]
        elif ultimo and re.search(r"English version", t):
            out[ultimo].append(href)
        elif t == "United Kingdom (Northern Ireland)":
            out["United Kingdom (Northern Ireland)"] = [href]
            ultimo = None
    return out


def domanda():
    out = {"paesi": {}, "generali": {}}
    for iso, nome, _, q in PAESI:
        for m in DOMANDA_MODELLI:
            out["paesi"].setdefault(iso, {})[m.format(p=q)] = _sugg(m.format(p=q))
    for q in DOMANDA_GENERALI:
        out["generali"][q] = _sugg(q)
    doc = {"_nota": "Ricerche vere (autocompletamento di Google, client=firefox, hl=en, gl=gb) sugli animali in viaggio dalla Gran Bretagna. "
                    "Una pagina Paese esiste solo se una ricerca sul Paese ha suggerimenti; ogni FAQ della sezione pets/ ha la sua 'query' qui. "
                    "Riscritto da raccolta/animali.py --domanda.",
           "letto_il": date.today().isoformat(), "modelli": DOMANDA_MODELLI, "generali_lette": DOMANDA_GENERALI, **out}
    (DATI / "animali_domanda.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("domanda:", {k: sum(len(v) for v in d.values()) for k, d in out["paesi"].items()}, "generali:", sum(len(v) for v in out["generali"].values()))


def _sugg(q):
    u = "https://suggestqueries.google.com/complete/search?client=firefox&gl=gb&hl=en&q=" + urllib.parse.quote(q)
    try:
        s = json.loads(leggi(u)[2])[1]
    except Exception as e:  # una richiesta persa non ferma la raccolta
        print(f"  autocompletamento {q!r}: {e}")
        s = []
    time.sleep(0.25)
    return s


def main():
    oggi = date.today().isoformat()
    da_cache = "--cache" in sys.argv
    CACHE.mkdir(parents=True, exist_ok=True)
    M = json.loads((DATI / "animali_manuali.json").read_text(encoding="utf-8"))
    f_dati = DATI / "animali.json"
    prima = json.loads(f_dati.read_text(encoding="utf-8")) if f_dati.exists() else {"fonti": {}}
    problemi, letture, cambi, grezzi = [], {}, [], {}
    for fid, F in FONTI.items():
        tipo = F.get("tipo", "html")
        f_cache = CACHE / f"{fid}.{'json' if tipo == 'govuk' else 'html'}"
        P = prima["fonti"].get(fid) or {}
        if da_cache:
            if not f_cache.exists():
                problemi.append(f"{fid}: nessuna copia in cache")
                continue
            raw, stato, finale = f_cache.read_text(encoding="utf-8"), P.get("http"), P.get("url_finale")
        else:
            raw, errore = None, None
            for tentativo in range(4):
                try:
                    stato, finale, raw = leggi(F["url"])
                    break
                except Exception as e:
                    errore = e
                    time.sleep(5 + 10 * tentativo)
            if raw is None:
                problemi.append(f"{fid}: lettura fallita ({errore})")
                continue
            f_cache.write_text(raw, encoding="utf-8")
        if stato != 200:
            problemi.append(f"{fid}: HTTP {stato}")
        grezzi[fid] = raw
        t = testo_fonte(raw, tipo)
        frasi = frasi_fonte(M, fid)
        for x in frasi:
            if x not in t:
                problemi.append(f"{fid}: frase non trovata: {x[:90]!r}")
        imp = impronta_zona(t, frasi) if frasi else None
        letto = oggi if not da_cache else (P.get("letto_il") or oggi)
        letture[fid] = {"url": F["url"], "pagina": F.get("pagina", F["url"]), "url_finale": finale, "http": stato, "byte": len(raw.encode("utf-8")),
                        "ente": F["ente"], "titolo": F["titolo"], "letto_il": letto, "impronta": imp, "frasi": len(frasi),
                        "aggiornato_il": aggiornato_govuk(raw) if tipo == "govuk" else None}
        print(f"  {fid}: HTTP {stato}, {letture[fid]['byte']} byte, {len(frasi)} frasi, impronta {imp}")
    # tabelle e link per Paese
    aria = tabelle_aria(grezzi["gov_aria"]) if "gov_aria" in grezzi else []
    mare = tabelle_mare(grezzi["gov_mare"]) if "gov_mare" in grezzi else {"mare": [], "crociera": [], "treno": []}
    ingresso = link_ue(grezzi["ue_ingresso"]) if "ue_ingresso" in grezzi else {}
    info = link_ue(grezzi["ue_paesi"]) if "ue_paesi" in grezzi else {}
    if len(aria) < 100:
        problemi.append(f"gov_aria: solo {len(aria)} righe di compagnie aeree (attese centinaia): rileggere la pagina")
    if not mare["mare"] or not mare["treno"]:
        problemi.append("gov_mare: tabella delle rotte via mare o treno vuota")
    paesi = []
    for iso, nome, nome_ue, q in PAESI:
        a, b = ingresso.get(nome_ue), info.get(nome_ue)
        if not a:  # il link alle informazioni nazionali può mancare (Lussemburgo: "Under construction" sulla pagina della Commissione)
            problemi.append(f"{iso}: link della Commissione ai punti di ingresso mancante ({nome_ue})")
        paesi.append({"iso2": iso, "nome": nome, "nome_ue": nome_ue, "ingresso": a or [], "info": b or []})
    for fid, righe in (("gov_aria", aria), ("gov_mare", mare)):
        if fid in letture:
            imp_t = impronta(json.dumps(righe, ensure_ascii=False, sort_keys=True))
            letture[fid]["impronta_tabella"] = imp_t
            P = prima["fonti"].get(fid) or {}
            if P.get("impronta_tabella") and P["impronta_tabella"] != imp_t:
                cambi.append({"data": oggi, "fonte": fid, "cosa": "tabella", "prima": P["impronta_tabella"], "dopo": imp_t})
                print(f"  CAMBIATA la tabella di {fid}")
    for fid, L in letture.items():
        P = prima["fonti"].get(fid) or {}
        if P.get("impronta") and L["impronta"] and P["impronta"] != L["impronta"]:
            cambi.append({"data": oggi, "fonte": fid, "cosa": "zona citata", "prima": P["impronta"], "dopo": L["impronta"]})
            print(f"  CAMBIATA la zona citata di {fid}: rileggere la pagina")
    if problemi:
        print("NON SCRITTO dati/animali.json. Da controllare a mano:\n  " + "\n  ".join(problemi))
        sys.exit(1)
    doc = {"_nota": "Animali in viaggio dalla Gran Bretagna all'UE: citazioni scritte a mano in dati/animali_manuali.json, fonti rilette da "
                    "raccolta/animali.py (HTTP, data di lettura, impronta della zona citata), tabelle GOV.UK delle rotte approvate e link della "
                    "Commissione per Paese copiati dalle pagine ufficiali. Non modificare a mano: rilanciare lo script.",
           "controllato_il": max(v["letto_il"] for v in letture.values()), "fonti": letture,
           "rotte": {"aria": [r for r in aria if r["tipo"] == "commerciale"], "charter": sum(1 for r in aria if r["tipo"] == "charter"), **mare},
           "paesi": paesi, "citazioni": M["citazioni"], "faq": M["faq"]}
    f_dati.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    if cambi:
        f_c = DATI / "animali_cambi.json"
        storico = json.loads(f_c.read_text(encoding="utf-8")) if f_c.exists() else {"cambi": []}
        storico["cambi"] = cambi + storico["cambi"]
        f_c.write_text(json.dumps(storico, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Scritto {f_dati.relative_to(RADICE.parent)}: {len(letture)} fonti, {len(aria)} righe aeree (charter solo contate), {len(mare['mare'])} rotte via mare, "
          f"{len(mare['crociera'])} crociere, {len(mare['treno'])} treni, {len(paesi)} Paesi" + (f", {len(cambi)} cambi" if cambi else ""))


if __name__ == "__main__":
    if "--testo" in sys.argv:
        fid = sys.argv[sys.argv.index("--testo") + 1]
        F = FONTI[fid]
        f_cache = CACHE / f"{fid}.{'json' if F.get('tipo') == 'govuk' else 'html'}"
        if not f_cache.exists():
            CACHE.mkdir(parents=True, exist_ok=True)
            f_cache.write_text(leggi(F["url"])[2], encoding="utf-8")
        print(testo_fonte(f_cache.read_text(encoding="utf-8"), F.get("tipo", "html")))
        sys.exit(0)
    if "--domanda" in sys.argv:
        domanda()
    main()
