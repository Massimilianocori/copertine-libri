"""Blue Badge all'estero (sezione "blue-badge-abroad/", dal 4/11/2026): dove vale il Blue Badge britannico in Europa, cosa dicono i consigli di
viaggio, le regole locali di parcheggio e la carta europea di parcheggio e della disabilità. Rilegge le fonti ufficiali e segnala i cambi.

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/bluebadge.py             rilegge le fonti, controlla le frasi citate e la tabella GOV.UK, scrive dati/bluebadge.json
    python3 -I beforeyoufly/raccolta/bluebadge.py --cache     come sopra ma senza rete, dalle copie in raccolta/.cache/bluebadge/
    python3 -I beforeyoufly/raccolta/bluebadge.py --domanda   rilegge anche l'autocompletamento di Google (dati/bluebadge_domanda.json)
    python3 -I beforeyoufly/raccolta/bluebadge.py --testo ID  stampa il testo normalizzato di una fonte (per scrivere le citazioni)

Regole (decise il 4/11/2026, piano: studio-business/intelaiatura/idee-2026-11-04-europa.md, idea 2):
  - Solo fonti ufficiali: GOV.UK (Department for Transport, guida "Using a Blue Badge in Europe" e pagina "Find out where Blue Badge holders can
    park"; consigli di viaggio FCDO; notizia del governo sull'accordo con la Spagna), lette dall'API dei contenuti di GOV.UK (licenza OGL v3.0);
    Commissione europea (Your Europe, pagina generale e una pagina per Paese UE; pagina della DG Giustizia sulle due carte europee); governi
    nazionali (Italia: Dipartimento per le politiche in favore delle persone con disabilità, circolare MIT del 28/9/2026; Francia:
    service-public.gouv.fr). La guida GOV.UK collega ogni Paese alle pagine della FIA: NON le usiamo (non è un ente pubblico).
    EUR-Lex risponde 202 (controllo anti-robot): la direttiva (UE) 2024/2841 si cita dalla pagina della Commissione che la riassume.
  - La tabella GOV.UK "Links to country information" (Paese, "UK Blue Badge recognised", "More information") si legge riga per riga e si
    confronta con dati/bluebadge_manuali.json: se una cella cambia, lo script NON scrive ed esce con 1 (si rilegge a mano e si corregge l'esito).
  - I consigli di viaggio FCDO: per i Paesi senza citazione si controlla che la pagina non nomini il Blue Badge (se lo nomina, esce con 1).
  - I fatti sono scritti a mano in dati/bluebadge_manuali.json: ogni frase tra virgolette sul sito è una citazione parola per parola; le citazioni
    non in inglese hanno la traduzione nostra ("tr"). Nessun consiglio legale: ogni pagina dice di controllare i cartelli e le regole del posto.
  - La lettura vale solo con HTTP 200. NESSUN nuovo tentativo su HTTPError (403, 404, 5xx: non si aggirano i blocchi); fino a 3 tentativi solo per
    errori di rete. Se una fonte non risponde 200 o una citazione non c'è più, lo script NON sovrascrive dati/bluebadge.json ed esce con 1.
  - Impronta (SHA-256, 16 caratteri) della zona citata e della tabella GOV.UK (per la pagina della pubblicazione GOV.UK: delle note di modifica);
    se cambia, il cambio va in dati/bluebadge_cambi.json. Di ogni fonte si salva anche l'impronta del testo intero ("impronta_testo", solo
    registrata: i consigli FCDO cambiano spesso in parti che non riguardano il Blue Badge).
  - Una pagina Paese solo se almeno una ricerca vera (dati/bluebadge_domanda.json) nomina il Paese (o un'isola del Paese) con "badge" o
    "disabled parking"; ogni FAQ ha la sua ricerca vera.
  - Pagine grezze in raccolta/.cache/bluebadge/ (escluse da git).
  - Ricontrollo: una volta al mese (la guida GOV.UK cambia spesso: Francia 8/2025, Spagna 9/2025 e 1/2026, Italia 10/2026).
"""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
CACHE = Path(__file__).resolve().parent / ".cache" / "bluebadge"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
GOVUK_API = "https://www.gov.uk/api/content/"
GOV = "https://www.gov.uk/"
YE = "https://europa.eu/youreurope/citizens/travel/transport-disability/parking-card-disabilities-people/"
PUBBL = "government/publications/blue-badge-using-it-in-the-eu"
DFT = "GOV.UK (Department for Transport)"
FCDO = "GOV.UK (Foreign, Commonwealth & Development Office)"
YE_ENTE = "Your Europe (European Commission)"

# Paesi della tabella GOV.UK: iso2, nome sul sito, nome nella tabella GOV.UK, percorso FCDO, percorso Your Europe (None = non UE),
# nomi nelle ricerche (il primo è il nome del Paese; gli altri sono isole o nomi alternativi cercati dalle persone)
PAESI = [
    ("AT", "Austria", "Austria", "austria", "austria", ["austria"]),
    ("BE", "Belgium", "Belgium", "belgium", "belgium", ["belgium"]),
    ("BG", "Bulgaria", "Bulgaria", "bulgaria", "bulgaria", ["bulgaria"]),
    ("HR", "Croatia", "Croatia", "croatia", "croatia", ["croatia"]),
    ("CY", "Cyprus", "Cyprus", "cyprus", "cyprus", ["cyprus"]),
    ("CZ", "Czechia", "Czech Republic", "czech-republic", "czechia", ["czech republic"]),
    ("DK", "Denmark", "Denmark", "denmark", "denmark", ["denmark"]),
    ("EE", "Estonia", "Estonia", "estonia", "estonia", ["estonia"]),
    ("FI", "Finland", "Finland", "finland", "finland", ["finland"]),
    ("FR", "France", "France", "france", "france", ["france"]),
    ("DE", "Germany", "Germany", "germany", "germany", ["germany"]),
    ("GR", "Greece", "Greece", "greece", "greece", ["greece"]),
    ("HU", "Hungary", "Hungary", "hungary", "hungary", ["hungary"]),
    ("IS", "Iceland", "Iceland", "iceland", None, ["iceland"]),
    ("IE", "Ireland", "Ireland", "ireland", "ireland", ["ireland"]),
    ("IT", "Italy", "Italy", "italy", "italy", ["italy"]),
    ("LV", "Latvia", "Latvia", "latvia", "latvia", ["latvia"]),
    ("LI", "Liechtenstein", "Liechtenstein", "liechtenstein", None, ["liechtenstein"]),
    ("LT", "Lithuania", "Lithuania", "lithuania", "lithuania", ["lithuania"]),
    ("LU", "Luxembourg", "Luxembourg", "luxembourg", "luxembourg", ["luxembourg"]),
    ("MT", "Malta", "Malta", "malta", "malta", ["malta"]),
    ("NL", "Netherlands", "Netherlands", "netherlands", "netherlands", ["netherlands", "holland"]),
    ("NO", "Norway", "Norway", "norway", None, ["norway"]),
    ("PL", "Poland", "Poland", "poland", "poland", ["poland"]),
    ("PT", "Portugal", "Portugal", "portugal", "portugal", ["portugal"]),
    ("RO", "Romania", "Romania", "romania", "romania", ["romania"]),
    ("SK", "Slovakia", "Slovakia", "slovakia", "slovakia", ["slovakia"]),
    ("SI", "Slovenia", "Slovenia", "slovenia", "slovenia", ["slovenia"]),
    ("ES", "Spain", "Spain (including Balearic and Canary Isles)", "spain", "spain", ["spain", "tenerife", "lanzarote", "majorca", "mallorca", "canary islands"]),
    ("SE", "Sweden", "Sweden", "sweden", "sweden", ["sweden"]),
    ("CH", "Switzerland", "Switzerland", "switzerland", None, ["switzerland"]),
]

FONTI = {
    "gov_eu": {"url": GOVUK_API + PUBBL + "/using-a-blue-badge-in-the-european-union", "pagina": GOV + PUBBL + "/using-a-blue-badge-in-the-european-union",
               "tipo": "govuk", "ente": DFT, "titolo": "GOV.UK: Using a Blue Badge in Europe", "lingua": "en"},
    "gov_pub": {"url": GOVUK_API + PUBBL, "pagina": GOV + PUBBL, "tipo": "govuk", "ente": DFT,
                "titolo": "GOV.UK: Using a Blue Badge in Europe (publication page and change history)", "lingua": "en"},
    "gov_park": {"url": GOVUK_API + "where-registered-disabled-drivers-can-park", "pagina": GOV + "where-registered-disabled-drivers-can-park",
                 "tipo": "govuk", "ente": "GOV.UK", "titolo": "GOV.UK: Find out where Blue Badge holders can park", "lingua": "en"},
    "gov_es": {"url": GOVUK_API + "government/news/strategic-bilateral-framework-between-the-kingdom-of-spain-and-the-united-kingdom-of-great-britain-and-northern-ireland-3-september-2025",
               "pagina": GOV + "government/news/strategic-bilateral-framework-between-the-kingdom-of-spain-and-the-united-kingdom-of-great-britain-and-northern-ireland-3-september-2025",
               "tipo": "govuk", "ente": "GOV.UK (Prime Minister's Office and Foreign, Commonwealth & Development Office)",
               "titolo": "GOV.UK: Strategic Bilateral Framework between Spain and the UK, 3 September 2025", "lingua": "en"},
    "ye_gen": {"url": YE + "index_en.htm", "tipo": "html", "ente": YE_ENTE, "titolo": "Your Europe: EU parking card for people with disabilities", "lingua": "en"},
    "ec_carte": {"url": "https://commission.europa.eu/strategy-and-policy/policies/justice-and-fundamental-rights/disability/european-disability-card-and-european-parking-card-persons-disabilities_en",
                 "tipo": "html", "ente": "European Commission", "titolo": "European Commission: European Disability Card and European Parking Card for persons with disabilities",
                 "lingua": "en"},
    "it_uso": {"url": "https://www.disabilita.governo.it/it/contrassegno-unico-disabili-europeo-cude/come-usare-il-contrassegno-in-italia-e-in-europa/", "tipo": "html",
               "ente": "Italian Government, Department for policies for persons with disabilities", "titolo": "Disabilita.governo.it: Come usare il Contrassegno in Italia e in Europa",
               "lingua": "it"},
    "it_ztl": {"url": "https://www.disabilita.governo.it/it/contrassegno-unico-disabili-europeo-cude/piattaforma-unica-nazionale-informatica-per-le-targhe-associate-al-cude/",
               "tipo": "html", "ente": "Italian Government, Department for policies for persons with disabilities",
               "titolo": "Disabilita.governo.it: Piattaforma unica nazionale per le targhe associate al CUDE", "lingua": "it"},
    "it_circ": {"url": "https://www.disabilita.governo.it/media/ntijwphx/m_infregistro-ufficialei002362028-09-2026.pdf", "tipo": "pdf",
                "ente": "Italian Ministry of Infrastructure and Transport and Department for policies for persons with disabilities",
                "titolo": "Circolare del 28 settembre 2026: Riconoscimento dei contrassegni di parcheggio rilasciati dal Regno Unito (Blue Badge)", "lingua": "it"},
    "fr_cmi": {"url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F34049", "tipo": "html", "ente": "Service-Public.gouv.fr (French Government)",
               "titolo": "Service-Public.gouv.fr: Carte mobilité inclusion (CMI)", "lingua": "fr"},
}
for _iso, _n, _g, _fc, _ye, _q in PAESI:
    FONTI[f"fcdo_{_iso}"] = {"url": GOVUK_API + "foreign-travel-advice/" + _fc, "pagina": GOV + "foreign-travel-advice/" + _fc, "tipo": "govuk", "ente": FCDO,
                             "titolo": f"GOV.UK: {_n} travel advice", "lingua": "en"}
    if _ye:
        FONTI[f"ye_{_iso}"] = {"url": YE + _ye + "/index_en.htm", "tipo": "html", "ente": YE_ENTE,
                               "titolo": f"Your Europe: EU parking card for people with disabilities – {_n}", "lingua": "en"}

DOMANDA_MODELLI = ["blue badge {p}", "blue badge in {p}", "uk blue badge {p}", "can i use my blue badge in {p}", "disabled parking {p}"]
DOMANDA_GENERALI = ["blue badge europe", "blue badge abroad", "using blue badge abroad", "can i use my blue badge abroad", "can i use my blue badge in europe",
                    "uk blue badge in europe", "blue badge eu", "european disability card", "european parking card", "eu disability card",
                    "european disability card uk", "blue badge ztl", "blue badge italy ztl", "blue badge parking abroad", "disabled parking europe",
                    "is my blue badge valid in"]
RX_PAROLE = re.compile(r"badge|disabled parking|disability parking|disabled badge", re.I)
# Luoghi britannici con il nome di un Paese (Denmark Hill a Londra, Denmark Street a Bristol, Holland Park, South Holland nel Lincolnshire) e
# l'Irlanda del Nord (Regno Unito): non sono ricerche sul Paese
RX_NON_PAESE = re.compile(r"denmark hill|denmark street|holland park|south holland|northern ireland")


def leggi(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-GB,en;q=0.9", "Accept": "text/html,application/json,application/pdf"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.geturl(), r.read()


def testo_html(html_):
    """Testo visibile normalizzato (stesso metodo di raccolta/trasporti.py)."""
    t = re.sub(r"(?is)<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>|<!--.*?-->", " ", html_)
    t = re.sub(r"(?i)</?(?:strong|b|em|i|a|span|abbr|sup|u|font)\b[^>]*>", "", t)
    t = unescape(re.sub(r"<[^>]+>", " ", t))
    for x in ("​", "⁣", "﻿", "­"):
        t = t.replace(x, "")
    t = re.sub(r"\s+", " ", t.replace("\xa0", " "))
    return re.sub(r" ([,.;:!?])", r"\1", t).strip()


def testo_pdf(raw):
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "f.pdf"
        f.write_bytes(raw)
        t = subprocess.run(["pdftotext", "-enc", "UTF-8", str(f), "-"], capture_output=True, check=True).stdout.decode("utf-8", "replace")
    t = re.sub(r"\s+", " ", t.replace("\f", " ").replace("\xa0", " "))
    return re.sub(r" ([,.;:!?])", r"\1", t).strip()


def corpo_govuk(raw):
    """HTML del contenuto di una pagina GOV.UK dall'API: parti di una guida, corpo, o i campi di una pagina di servizio locale."""
    det = json.loads(raw).get("details", {})
    if det.get("parts"):
        return " ".join(f"<h2>{p['title']}</h2>{p['body']}" for p in det["parts"])
    if det.get("body"):
        b = det["body"]
        return b if isinstance(b, str) else " ".join(x.get("content", "") for x in b)
    return " ".join(det.get(k) or "" for k in ("introduction", "need_to_know", "more_information"))


def testo_fonte(raw, tipo="html"):
    if tipo == "pdf":
        return testo_pdf(raw)
    s = raw.decode("utf-8", "replace")
    return testo_html(corpo_govuk(s) if tipo == "govuk" else s)


MESI_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]


def aggiornato(raw, tipo):
    """Data dell'ultimo aggiornamento dichiarato dalla fonte: GOV.UK public_updated_at; Your Europe «Last checked: GG/MM/AAAA»; Commissione
    dateModified; service-public «Vérifié le …»; altrimenti None."""
    s = raw.decode("utf-8", "replace") if tipo != "pdf" else ""
    if tipo == "govuk":
        return (json.loads(s).get("public_updated_at") or "")[:10] or None
    m = re.search(r"Last checked: (\d{2})/(\d{2})/(\d{4})", testo_html(s))
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    m = re.search(r"Vérifié le (\d{1,2}) (" + "|".join(MESI_FR) + r") (\d{4})", testo_html(s))
    if m:
        return f"{m.group(3)}-{MESI_FR.index(m.group(2)) + 1:02d}-{int(m.group(1)):02d}"
    m = re.search(r'"dateModified":\s*"(\d{4}-\d{2}-\d{2})', s)
    return m.group(1) if m else None


def tabella_govuk(raw):
    """Righe della tabella «Links to country information» della guida GOV.UK: Paese, cella «UK Blue Badge recognised», frase in più della
    colonna «More information» (tolto il rimando «Read more about parking for disabled people in …», che porta a un sito non pubblico)."""
    body = corpo_govuk(raw.decode("utf-8", "replace"))
    out = []
    for tb in re.findall(r"(?is)<tbody>(.*?)</tbody>", body):
        for tr in re.findall(r"(?is)<tr>(.*?)</tr>", tb):
            c = [testo_html(x) for x in re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", tr)]
            if len(c) == 3:
                extra = re.sub(r"^Read more about parking for disabled people in (?:the )?[^.]+\.\s*", "", c[2]).strip()
                out.append({"paese": c[0], "riconosciuto": c[1], "info": extra})
    return out


def storico_govuk(raw):
    """Note di modifica della pubblicazione GOV.UK (data e nota), dalla più recente."""
    det = json.loads(raw.decode("utf-8", "replace")).get("details", {})
    return [{"data": (x.get("public_timestamp") or "")[:10], "nota": (x.get("note") or "").strip()} for x in det.get("change_history", [])]


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


def file_cache(fid):
    tipo = FONTI[fid].get("tipo", "html")
    return CACHE / f"{fid}.{ {'govuk': 'json', 'pdf': 'pdf'}.get(tipo, 'html') }"


def tutte_ricerche(D):
    return {s for g in D["gl"].values() for ss in g.values() for s in ss}


def ricerche_paese(D, nomi):
    """Ricerche vere che nominano il Paese (o un'isola del Paese) insieme a "badge" o "disabled parking"."""
    rx = re.compile(r"\b(?:" + "|".join(re.escape(n) for n in nomi) + r")\b")
    return sorted(s for s in tutte_ricerche(D) if rx.search(s) and RX_PAROLE.search(s) and not RX_NON_PAESE.search(s))


def ricerche_domanda():
    return [m.format(p=q) for _, _, _, _, _, qq in PAESI for q in qq for m in DOMANDA_MODELLI] + DOMANDA_GENERALI


def domanda():
    out = {}
    for gl, qs in (("uk", ricerche_domanda()), ("us", DOMANDA_GENERALI)):
        for q in qs:
            u = "https://suggestqueries.google.com/complete/search?client=firefox&gl=%s&hl=en&q=%s" % (gl, urllib.parse.quote(q))
            try:
                sugg = json.loads(leggi(u)[2].decode("utf-8", "replace"))[1]
            except Exception as e:  # una richiesta persa non ferma la raccolta (nessun nuovo tentativo)
                print(f"  autocompletamento {gl} {q!r}: {e}")
                continue
            out.setdefault(gl, {})[q] = sugg
            time.sleep(0.25)
    doc = {"_nota": "Ricerche vere (autocompletamento di Google, client=firefox, hl=en, gl=uk per tutte le ricerche, gl=us solo per quelle generali) "
                    "sul Blue Badge all'estero e sulle carte europee. Una pagina Paese della sezione blue-badge-abroad/ esiste solo se una ricerca "
                    "nomina il Paese con 'badge' o 'disabled parking'; ogni FAQ ha la sua 'query' qui. Riscritto da raccolta/bluebadge.py --domanda.",
           "letto_il": date.today().isoformat(), "ricerche": ricerche_domanda(), "gl": out}
    (DATI / "bluebadge_domanda.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("domanda:", len(tutte_ricerche(doc)), "suggerimenti diversi")


def main():
    oggi = date.today().isoformat()
    da_cache = "--cache" in sys.argv
    CACHE.mkdir(parents=True, exist_ok=True)
    M = json.loads((DATI / "bluebadge_manuali.json").read_text(encoding="utf-8"))
    D = json.loads((DATI / "bluebadge_domanda.json").read_text(encoding="utf-8"))
    f_dati = DATI / "bluebadge.json"
    prima = json.loads(f_dati.read_text(encoding="utf-8")) if f_dati.exists() else {"fonti": {}}
    problemi, letture, cambi, testi, grezzi = [], {}, [], {}, {}
    ids = [c["id"] for c in M["citazioni"]]
    if len(ids) != len(set(ids)):
        problemi.append("id di citazione duplicati")
    if len({(c["f"], c["x"]) for c in M["citazioni"]}) != len(ids):
        problemi.append("citazioni ripetute (ogni frase di una fonte citata una sola volta)")
    for fid, F in FONTI.items():
        tipo = F.get("tipo", "html")
        f_cache = file_cache(fid)
        P = prima["fonti"].get(fid) or {}
        if da_cache:
            if not f_cache.exists():
                problemi.append(f"{fid}: nessuna copia in cache")
                continue
            raw, stato, finale = f_cache.read_bytes(), P.get("http"), P.get("url_finale")
        else:
            raw, errore = None, None
            for tentativo in range(3):
                try:
                    stato, finale, raw = leggi(F["url"])
                    break
                except urllib.error.HTTPError as e:
                    errore = e  # rifiuto del server (403, 404, 5xx): NESSUN nuovo tentativo
                    break
                except Exception as e:
                    errore = e  # solo errori di rete o di tempo
                    time.sleep(5 + 10 * tentativo)
            if raw is None:
                problemi.append(f"{fid}: lettura fallita ({errore})")
                continue
            f_cache.write_bytes(raw)
            time.sleep(0.4)
        if stato != 200:
            problemi.append(f"{fid}: HTTP {stato}")
        grezzi[fid] = raw
        t = testo_fonte(raw, tipo)
        testi[fid] = t
        frasi = frasi_fonte(M, fid)
        for x in frasi:
            if x not in t:
                problemi.append(f"{fid}: frase non trovata: {x[:90]!r}")
        imp = impronta_zona(t, frasi) if frasi else None
        letto = oggi if not da_cache else (P.get("letto_il") or oggi)
        letture[fid] = {"url": F["url"], "pagina": F.get("pagina", F["url"]), "url_finale": finale, "http": stato, "byte": len(raw), "ente": F["ente"],
                        "titolo": F["titolo"], "lingua": F["lingua"], "tipo": tipo, "letto_il": letto, "aggiornato_il": aggiornato(raw, tipo),
                        "impronta": imp, "frasi": len(frasi), "impronta_testo": impronta(t)}
        if P.get("impronta") and imp and P["impronta"] != imp:
            cambi.append({"data": oggi, "fonte": fid, "cosa": "zona citata", "prima": P["impronta"], "dopo": imp})
            print(f"  CAMBIATA la zona citata di {fid}: rileggere la pagina")
    # tabella GOV.UK e note di modifica
    righe = tabella_govuk(grezzi["gov_eu"]) if "gov_eu" in grezzi else []
    storico = storico_govuk(grezzi["gov_pub"]) if "gov_pub" in grezzi else []
    per_nome = {r["paese"]: r for r in righe}
    if len(righe) != len(PAESI) or set(per_nome) != {g for _, _, g, _, _, _ in PAESI}:
        problemi.append(f"gov_eu: la tabella ha {len(righe)} righe o Paesi diversi da quelli attesi ({len(PAESI)}): rileggere la pagina")
    if "gov_pub" in letture:  # la pagina della pubblicazione non ha frasi citate: l'impronta è quella delle note di modifica
        letture["gov_pub"]["impronta"] = impronta(json.dumps(storico, ensure_ascii=False, sort_keys=True))
    if "gov_eu" in letture:
        imp_t = impronta(json.dumps(righe, ensure_ascii=False, sort_keys=True))
        letture["gov_eu"]["impronta_tabella"] = imp_t
        P = prima["fonti"].get("gov_eu") or {}
        if P.get("impronta_tabella") and P["impronta_tabella"] != imp_t:
            cambi.append({"data": oggi, "fonte": "gov_eu", "cosa": "tabella", "prima": P["impronta_tabella"], "dopo": imp_t})
            print("  CAMBIATA la tabella GOV.UK: rileggere la pagina e gli esiti")
    MP = {p["iso2"]: p for p in M["paesi"]}
    ricerche = tutte_ricerche(D)
    paesi = []
    for iso, nome, nome_gov, fc, ye, qq in PAESI:
        m = MP.get(iso)
        r = per_nome.get(nome_gov)
        if not m:
            problemi.append(f"{iso}: Paese mancante in bluebadge_manuali.json")
            continue
        if r and (r["riconosciuto"] != m["riconosciuto"] or r["info"] != m.get("info", "")):
            problemi.append(f"{iso}: la riga GOV.UK è cambiata: {r} (attesa {m['riconosciuto']!r} / {m.get('info', '')!r})")
        cit_fcdo = [c for c in M["citazioni"] if c["f"] == f"fcdo_{iso}"]
        t = testi.get(f"fcdo_{iso}", "")
        nomina = "Blue Badge" in t
        if t and nomina and not cit_fcdo:
            problemi.append(f"fcdo_{iso}: il consiglio di viaggio ora nomina il Blue Badge: leggerlo e citarlo")
        cerca = ricerche_paese(D, qq)
        for q in m.get("faq", []):
            if q["query"] not in ricerche:
                problemi.append(f"{iso}: FAQ «{q['q']}» senza ricerca vera ({q['query']!r})")
        paesi.append({**m, "nome_gov": nome_gov, "fcdo_nomina": nomina, "ye": bool(ye), "ricerche": cerca, "pagina": bool(cerca)})
    for q in M.get("faq_indice", []) + M.get("faq_carte", []):
        if q["query"] not in ricerche:
            problemi.append(f"indice: FAQ «{q['q']}» senza ricerca vera ({q['query']!r})")
    for c in M["citazioni"]:
        if c["f"] not in FONTI:
            problemi.append(f"citazione {c['id']}: fonte {c['f']} sconosciuta")
        elif FONTI[c["f"]]["lingua"] != "en" and not c.get("tr"):
            problemi.append(f"citazione {c['id']}: manca la traduzione")
    if problemi:
        print("NON SCRITTO dati/bluebadge.json. Da controllare a mano:\n  " + "\n  ".join(problemi))
        sys.exit(1)
    for fid, L in letture.items():
        print(f"  {fid}: HTTP {L['http']}, {L['byte']} byte, {L['frasi']} frasi, aggiornata {L['aggiornato_il']}, impronta {L['impronta']}")
    doc = {"_nota": "Blue Badge all'estero: fatti scritti a mano in dati/bluebadge_manuali.json (citazioni parola per parola), fonti rilette da "
                    "raccolta/bluebadge.py (HTTP, data di lettura, data di aggiornamento della fonte, impronta della zona citata), tabella GOV.UK "
                    "copiata riga per riga, note di modifica della pubblicazione GOV.UK, Paesi con pagina (ricerche vere). Non modificare a mano.",
           "controllato_il": max(v["letto_il"] for v in letture.values()), "fonti": letture, "tabella_govuk": righe, "storico_govuk": storico,
           "paesi": paesi, "citazioni": M["citazioni"], "generali": M["generali"], "faq_indice": M.get("faq_indice", []), "faq_carte": M.get("faq_carte", [])}
    f_dati.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    if cambi:
        f_c = DATI / "bluebadge_cambi.json"
        storico_c = json.loads(f_c.read_text(encoding="utf-8")) if f_c.exists() else {"cambi": []}
        storico_c["cambi"] = cambi + storico_c["cambi"]
        f_c.write_text(json.dumps(storico_c, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Scritto {f_dati.relative_to(RADICE.parent)}: {len(letture)} fonti, {len(righe)} righe GOV.UK, {sum(p['pagina'] for p in paesi)} Paesi con pagina"
          + (f", {len(cambi)} cambi" if cambi else ""))


if __name__ == "__main__":
    if "--testo" in sys.argv:
        fid = sys.argv[sys.argv.index("--testo") + 1]
        f_cache = file_cache(fid)
        if not f_cache.exists():
            CACHE.mkdir(parents=True, exist_ok=True)
            f_cache.write_bytes(leggi(FONTI[fid]["url"])[2])
        print(testo_fonte(f_cache.read_bytes(), FONTI[fid].get("tipo", "html")))
        sys.exit(0)
    if "--domanda" in sys.argv:
        domanda()
        if "--solo-domanda" in sys.argv:
            sys.exit(0)
    main()
