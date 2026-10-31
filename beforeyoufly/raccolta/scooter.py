"""Scooter e motorini in vacanza (sezione "Scooter rental: which licence?"): rilegge le regole ufficiali sulla patente per 50 cc e 125 cc.

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/scooter.py             rilegge le fonti, controlla le frasi citate, scrive dati/scooter.json
    python3 -I beforeyoufly/raccolta/scooter.py --cache     come sopra ma senza rete, dalle copie in raccolta/.cache/scooter/
    python3 -I beforeyoufly/raccolta/scooter.py --domanda   legge anche l'autocompletamento di Google per le ricerche nuove (dati/scooter_domanda.json)
    python3 -I beforeyoufly/raccolta/scooter.py --testo ID  stampa il testo normalizzato di una fonte (per scrivere le citazioni)

Regole (decise il 31/10/2026):
  - Solo fonti ufficiali: codice della strada o regolamento delle patenti pubblicato dallo Stato (BOE, gesetze-im-internet.de, Normattiva),
    il portale ufficiale dell'amministrazione (service-public.gouv.fr), i consigli di viaggio del governo britannico (FCDO, API di GOV.UK,
    Open Government Licence v3.0) quando dicono quale patente serve. Niente noleggiatori, blog, forum o guide.
  - Le regole (50 cc, 125 cc, oltre 125 cc, patente di provenienza) sono scritte a mano in dati/scooter_manuali.json, ognuna legata alle
    frasi ufficiali che la dicono (citazioni parola per parola nella lingua originale, con la nostra traduzione inglese).
  - Una pagina Paese esiste solo se la regola sulla patente è scritta in una fonte ufficiale che si legge (HTTP 200). I Paesi provati e non
    letti stanno in "non_letti" con l'indirizzo: lo script li rilegge una volta e registra HTTP e quante frasi della pagina dicono quale
    categoria di patente serve per un motorino o uno scooter (espressione "cerca" di ogni voce): verifica.py controlla che il motivo scritto
    sia coerente (pagina che non risponde = HTTP diverso da 200; regola assente = HTTP 200 e 0 frasi).
  - Nessun nuovo tentativo su un errore HTTP (403, 404, 503...): l'esito si registra così com'è. Solo gli errori di rete si ritentano (3 volte).
  - Se una fonte non risponde 200 o una citazione non c'è più, lo script NON sovrascrive dati/scooter.json ed esce con 1.
  - Impronta (SHA-256, 16 caratteri) della "zona citata" di ogni fonte; se cambia, il cambio va in dati/scooter_cambi.json.
  - Pagine grezze in raccolta/.cache/scooter/ (escluse da git).
"""
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
CACHE = Path(__file__).resolve().parent / ".cache" / "scooter"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
FCDO_API = "https://www.gov.uk/api/content/foreign-travel-advice/"
ENTE_FCDO = "Foreign, Commonwealth & Development Office (GOV.UK)"

# id -> indirizzo letto, ente, titolo, lingua; "fcdo": paese dell'API dei consigli di viaggio (il link della pagina è la parte che contiene le frasi)
FONTI = {
    "fr_f45": {"url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F45", "lingua": "fr",
               "ente": "Service-Public.fr (French government, Direction de l'information légale et administrative)",
               "titolo": "Service-Public.fr: Peut-on conduire un scooter 3 roues ou une moto 125 avec le permis B ?"},
    "fr_f2890": {"url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F2890", "lingua": "fr",
                 "ente": "Service-Public.fr (French government, Direction de l'information légale et administrative)",
                 "titolo": "Service-Public.fr: Brevet de sécurité routière (BSR), catégorie AM du permis de conduire"},
    "fr_f2832": {"url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F2832", "lingua": "fr",
                 "ente": "Service-Public.fr (French government, Direction de l'information légale et administrative)",
                 "titolo": "Service-Public.fr: Permis moto : permis A1 ou permis 125 (moto légère)"},
    "es_rgc": {"url": "https://www.boe.es/buscar/act.php?id=BOE-A-2009-9481", "lingua": "es",
               "ente": "Boletín Oficial del Estado (Spanish government)",
               "titolo": "BOE: Real Decreto 818/2009, Reglamento General de Conductores (consolidated text)"},
    "es_fcdo": {"fcdo": "spain", "lingua": "en", "ente": ENTE_FCDO, "titolo": "GOV.UK: Spain travel advice"},
    "de_fev6": {"url": "https://www.gesetze-im-internet.de/fev_2010/__6.html", "lingua": "de",
                "ente": "German Federal Ministry of Justice (gesetze-im-internet.de)",
                "titolo": "Fahrerlaubnis-Verordnung (FeV), § 6: Einteilung der Fahrerlaubnisklassen"},
    "de_fev6b": {"url": "https://www.gesetze-im-internet.de/fev_2010/__6b.html", "lingua": "de",
                 "ente": "German Federal Ministry of Justice (gesetze-im-internet.de)",
                 "titolo": "Fahrerlaubnis-Verordnung (FeV), § 6b: Fahrerlaubnis der Klasse B mit der Schlüsselzahl 196"},
    "gr_fcdo": {"fcdo": "greece", "lingua": "en", "ente": ENTE_FCDO, "titolo": "GOV.UK: Greece travel advice"},
    "th_fcdo": {"fcdo": "thailand", "lingua": "en", "ente": ENTE_FCDO, "titolo": "GOV.UK: Thailand travel advice"},
}

# Ricerche da rileggere con --domanda (autocompletamento, client=firefox, hl=en, gl=us e gl=uk): le FAQ e le pagine si legano a queste
DOMANDA = [
    "can i rent a scooter in", "125cc with car licence", "can you drive 125cc with car licence in", "rent scooter in greece with",
    "can you rent a scooter in greece with", "can you rent a moped in greece with", "rent a moped in", "rent a scooter in spain with",
    "can you ride a 125cc in spain with a car licence", "125cc car licence spain", "can i ride a 125 in france with a car licence",
    "rent scooter france car licence", "125cc car licence france", "125cc car licence germany", "b196 germany",
    "can you rent a scooter in germany", "do you need a motorcycle license to rent a scooter in",
    "rent a scooter in france", "can you rent a scooter in france", "can you ride a 125cc in france", "can you ride a 125 in france",
    "do you need a license for a scooter in", "can i ride a moped with a car licence in",
]
# Frasi che dicono quale categoria di patente serve per un motorino o uno scooter (per i Paesi "non letti" la pagina ne deve avere 0)
CERCA_FCDO = r"(?:moped|scooter)[^.]{0,160}\b(?:category|categories|A1|AM)\b|\b(?:category|A1|AM)\b[^.]{0,160}(?:moped|scooter)"


def leggi(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-GB,en;q=0.9,fr;q=0.8,es;q=0.8,de;q=0.8",
                                               "Accept": "text/html,application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.geturl(), r.read(), r.headers.get_content_charset()


def leggi_una_volta(url):
    """(stato o None, url finale, byte o None, charset, errore): nessun nuovo tentativo su un errore HTTP; errori di rete al massimo 3 tentativi."""
    errore = None
    for tentativo in range(3):
        try:
            stato, finale, raw, cs = leggi(url)
            return stato, finale, raw, cs, None
        except urllib.error.HTTPError as e:
            return e.code, url, None, None, f"HTTP {e.code}"
        except Exception as e:
            errore = e
            time.sleep(5 + 10 * tentativo)
    return None, url, None, None, str(errore)


def url_lettura(F):
    return FCDO_API + F["fcdo"] if F.get("fcdo") else F["url"]


def decodifica(raw, cs=None):
    """Byte -> testo: charset dell'intestazione HTTP, poi quello dichiarato nella pagina, poi UTF-8 (gesetze-im-internet.de è ISO-8859-1)."""
    if not cs:
        m = re.search(rb"""<meta[^>]+charset=["']?([A-Za-z0-9_-]+)""", raw[:4000], re.I)
        cs = m.group(1).decode() if m else "utf-8"
    try:
        return raw.decode(cs)
    except (LookupError, UnicodeDecodeError):
        return raw.decode("utf-8", "replace")


def testo_html(h):
    """Testo visibile normalizzato (come raccolta/biglietti.py), senza i suggerimenti a comparsa di service-public (role="tooltip")."""
    t = re.sub(r'(?is)<span[^>]*role="tooltip"[^>]*>.*?</span>', "", h)
    t = re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>|<!--.*?-->", " ", t)
    t = re.sub(r"(?i)</?(?:strong|b|em|i|a|span|abbr|sup|u|font)\b[^>]*>", "", t)
    t = unescape(re.sub(r"<[^>]+>", " ", t))
    for x in ("​", "⁣", "﻿", "\xad"):
        t = t.replace(x, "")
    t = re.sub(r"\s+", " ", t.replace("\xa0", " "))
    return re.sub(r" ([,.;:!?])", r"\1", t).strip()


def parti_fcdo(raw):
    """API dei consigli di viaggio: [(slug della parte, testo)] e data di aggiornamento pubblicata."""
    d = json.loads(raw.decode("utf-8"))
    return [(p.get("slug", ""), testo_html(p.get("body", ""))) for p in d["details"].get("parts", [])], (d.get("public_updated_at") or "")[:10]


def testo_fonte(fid, raw, cs=None):
    F = FONTI[fid]
    if F.get("fcdo"):
        return " ".join(t for _, t in parti_fcdo(raw)[0])
    return testo_html(decodifica(raw, cs))


def frasi_fonte(M, fid):
    return [c["x"] for p in M["paesi"] for c in p["citazioni"] if c["f"] == fid] + [c["x"] for c in M.get("generali", []) if c["f"] == fid]


def impronta_zona(testo, frasi):
    pos = [(testo.find(x), len(x)) for x in frasi]
    if not pos or any(i < 0 for i, _ in pos):
        return None
    a, b = min(i for i, _ in pos), max(i + n for i, n in pos)
    return hashlib.sha256(testo[a:b].encode("utf-8")).hexdigest()[:16]


def file_cache(fid):
    return CACHE / (f"{fid}.json" if FONTI.get(fid, {}).get("fcdo") else f"{fid}.html")


def tutte_ricerche(D):
    return {s for g in D["ricerche"].values() for ss in g.values() for s in ss}


def domanda(tutte=False):
    f = DATI / "scooter_domanda.json"
    prima = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"ricerche": {}}
    out = prima.get("ricerche") or {}
    date_q = prima.get("letto_il_per_ricerca") or {}
    nuove = 0
    for gl in ("us", "uk"):
        for q in DOMANDA:
            if not tutte and q in out.get(gl, {}):
                continue
            u = "https://suggestqueries.google.com/complete/search?client=firefox&gl=%s&hl=en&q=%s" % (gl, urllib.parse.quote(q))
            try:
                sugg = json.loads(leggi(u)[2].decode("utf-8", "replace"))[1]
            except Exception as e:  # una richiesta persa non ferma la raccolta
                print(f"  autocompletamento {gl} {q!r}: {e}")
                continue
            out.setdefault(gl, {})[q] = sugg
            date_q[q] = date.today().isoformat()
            nuove += 1
            time.sleep(0.25)
    doc = {"_nota": "Ricerche vere (autocompletamento di Google, client=firefox, hl=en, gl=us e gl=uk) su scooter, motorini e patente in vacanza. "
                    "Ogni pagina Paese e ogni domanda delle FAQ si lega a una di queste ricerche (campo 'query' in scooter_manuali.json). "
                    "Riscritto da raccolta/scooter.py --domanda (solo le ricerche nuove; --tutte le rilegge tutte).",
           "letto_il": max(date_q.values()), "letto_il_per_ricerca": date_q, "domande": DOMANDA, "ricerche": out}
    f.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("domanda:", nuove, "ricerche lette ora,", sum(len(v) for g in out.values() for v in g.values()), "suggerimenti in tutto")


def rileggi_non_letti(M, prima, da_cache):
    """Paesi provati e senza pagina: rilegge una volta l'indirizzo (HTTP, data, frasi che dicono quale categoria serve)."""
    oggi = date.today().isoformat()
    vecchi = {x["nome"]: x for x in prima.get("non_letti", [])}
    out = []
    for x in M["non_letti"]:
        x = dict(x)
        if da_cache:
            P = vecchi.get(x["nome"]) or {}
            x.update({k: P.get(k) for k in ("http", "letto_il", "frasi_regola", "aggiornata_il")})
        else:
            u = FCDO_API + x["fcdo"] if x.get("fcdo") else x["url"]
            stato, _, raw, cs, err = leggi_una_volta(u)
            x["http"], x["letto_il"], x["frasi_regola"], x["aggiornata_il"] = stato, oggi, None, None
            if raw and stato == 200:
                if x.get("fcdo"):
                    parti, agg = parti_fcdo(raw)
                    t, x["aggiornata_il"] = " ".join(tt for _, tt in parti), agg
                else:
                    t = testo_html(decodifica(raw, cs))
                x["frasi_regola"] = len(re.findall(x["cerca"], t, re.I))
            print(f"  non letto {x['nome']}: {stato or err}, frasi con la regola {x['frasi_regola']}")
        out.append(x)
    return out


def main():
    oggi = date.today().isoformat()
    da_cache = "--cache" in sys.argv
    CACHE.mkdir(parents=True, exist_ok=True)
    M = json.loads((DATI / "scooter_manuali.json").read_text(encoding="utf-8"))
    D = json.loads((DATI / "scooter_domanda.json").read_text(encoding="utf-8"))
    f_dati = DATI / "scooter.json"
    prima = json.loads(f_dati.read_text(encoding="utf-8")) if f_dati.exists() else {"fonti": {}}
    usate = sorted({c["f"] for p in M["paesi"] for c in p["citazioni"]} | {c["f"] for c in M.get("generali", [])})
    problemi, letture, cambi = [], {}, []
    for fid in usate:
        F = FONTI.get(fid)
        if not F:
            problemi.append(f"fonte {fid} non in FONTI")
            continue
        f_cache = file_cache(fid)
        P = prima["fonti"].get(fid) or {}
        if da_cache:
            if not f_cache.exists():
                problemi.append(f"{fid}: nessuna copia in cache")
                continue
            raw, stato, finale, cs = f_cache.read_bytes(), P.get("http"), P.get("url_finale"), P.get("charset")
        else:
            stato, finale, raw, cs, errore = leggi_una_volta(url_lettura(F))
            if raw is None:
                problemi.append(f"{fid}: lettura fallita ({errore})")
                continue
            f_cache.write_bytes(raw)
        if stato != 200:
            problemi.append(f"{fid}: HTTP {stato}")
        t = testo_fonte(fid, raw, cs)
        frasi = frasi_fonte(M, fid)
        mancano = [x for x in frasi if x not in t]
        for x in mancano:
            problemi.append(f"{fid}: frase non trovata: {x[:90]!r}")
        imp = impronta_zona(t, frasi)
        pagina, aggiornata = F.get("url"), None
        if F.get("fcdo"):  # il link è la parte dei consigli che contiene la prima frase citata
            parti, aggiornata = parti_fcdo(raw)
            slug = next((sl for sl, tt in parti if frasi and frasi[0] in tt), "")
            pagina = f"https://www.gov.uk/foreign-travel-advice/{F['fcdo']}" + (f"/{slug}" if slug else "")
        letto = oggi if not da_cache else (P.get("letto_il") or oggi)
        cambiato = P.get("cambiato_il") if P.get("impronta") == imp and P.get("cambiato_il") else letto
        if P.get("impronta") and imp and P["impronta"] != imp:
            cambi.append({"data": oggi, "fonte": fid, "url": url_lettura(F), "prima": P["impronta"], "dopo": imp})
            print(f"  CAMBIATA la zona citata di {fid}: rileggere la pagina (la regola può essere cambiata)")
        letture[fid] = {"url": url_lettura(F), "pagina": pagina, "url_finale": finale, "http": stato, "byte": len(raw), "charset": cs,
                        "ente": F["ente"], "titolo": F["titolo"], "lingua": F["lingua"], "letto_il": letto, "cambiato_il": cambiato,
                        "aggiornata_il": aggiornata, "impronta": imp, "frasi": len(frasi)}
        print(f"  {fid}: HTTP {stato}, {len(raw)} byte, {len(frasi)} frasi, {len(mancano)} mancanti, impronta {imp}")
    ricerche = tutte_ricerche(D)
    for p in M["paesi"]:
        ids = {c["id"] for c in p["citazioni"]}
        if p["query"] not in ricerche:
            problemi.append(f"{p['slug']}: pagina senza ricerca vera ({p['query']!r})")
        for q in p["faq"]:
            if q["query"] not in ricerche:
                problemi.append(f"{p['slug']}: FAQ «{q['q']}» senza ricerca vera ({q['query']!r})")
            if any(i not in ids for i in q.get("cit", [])):
                problemi.append(f"{p['slug']}: FAQ «{q['q']}» con citazione sconosciuta")
        for k, v in list(p["casi"].items()) + list(p["patenti"].items()):
            if any(i not in ids for i in v.get("cit", [])) or (v["esito"] != "non_detto" and not v.get("cit")):
                problemi.append(f"{p['slug']}: voce {k} senza citazione o con citazione sconosciuta")
        for c in p["citazioni"]:
            if FONTI[c["f"]]["lingua"] != "en" and not c.get("tr"):
                problemi.append(f"{p['slug']}: citazione {c['id']} non in inglese senza traduzione")
    non_letti = rileggi_non_letti(M, prima, da_cache)
    if problemi:
        print("NON SCRITTO dati/scooter.json. Da controllare a mano:\n  " + "\n  ".join(problemi))
        sys.exit(1)
    doc = {"_nota": "Patente per motorini (50 cc) e scooter (125 cc) in vacanza: regole scritte a mano in dati/scooter_manuali.json "
                    "(citazioni parola per parola, con traduzione), fonti rilette da raccolta/scooter.py (HTTP, data di lettura, impronta della zona citata). "
                    "Non modificare a mano: rilanciare lo script.",
           "controllato_il": max(v["letto_il"] for v in letture.values()), "fonti": letture, "paesi": M["paesi"],
           "generali": M.get("generali", []), "non_letti": non_letti}
    f_dati.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    if cambi:
        f_c = DATI / "scooter_cambi.json"
        storico = json.loads(f_c.read_text(encoding="utf-8")) if f_c.exists() else {"cambi": []}
        storico["cambi"] = cambi + storico["cambi"]
        f_c.write_text(json.dumps(storico, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Scritto {f_dati.relative_to(RADICE.parent)}: {len(M['paesi'])} Paesi, {len(letture)} fonti, {len(non_letti)} Paesi non letti"
          + (f", {len(cambi)} cambi" if cambi else ""))


if __name__ == "__main__":
    if "--testo" in sys.argv:
        fid = sys.argv[sys.argv.index("--testo") + 1]
        f_cache = file_cache(fid)
        CACHE.mkdir(parents=True, exist_ok=True)
        cs = None
        if not f_cache.exists():
            _, _, raw, cs = leggi(url_lettura(FONTI[fid]))
            f_cache.write_bytes(raw)
        print(testo_fonte(fid, f_cache.read_bytes(), cs))
        sys.exit(0)
    if "--domanda" in sys.argv:
        domanda(tutte="--tutte" in sys.argv)
        if "--solo-domanda" in sys.argv:
            sys.exit(0)
    main()
