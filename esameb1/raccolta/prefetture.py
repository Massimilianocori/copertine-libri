"""Raccolta ripetibile delle pagine «Cittadinanza» delle 106 Prefetture (sezione /cittadinanza/ di EsameB1).

Uso (dalla radice del repository):
    python3 esameb1/raccolta/prefetture.py              # scarica le pagine, aggiorna dati/prefetture.json e dati/fonti/prefetture/*.txt
    python3 esameb1/raccolta/prefetture.py --candidati milano   # frasi «locali» candidate di una prefettura (dalla cache)
    python3 esameb1/raccolta/prefetture.py --allegati   # ricontrolla solo lo stato HTTP degli allegati (il sito linka solo i 200)
    python3 esameb1/raccolta/prefetture.py --controlla  # solo controllo: link 200 e frasi citate in dati/prefetture_locali.json
                                                        # ancora presenti nella pagina della Prefettura (esce con 1 se no)

Cosa fa la raccolta:
1. Elenco delle prefetture dalla home di prefettura.interno.gov.it (link /it/prefetture/<slug>); se la home cambia
   forma usa l'elenco scritto qui sotto (106 nomi, letto il 31/10/2026).
2. Per ognuna scarica https://prefettura.interno.gov.it/it/prefetture/<slug>/cittadinanza e tiene SOLO:
   - i campi della «rubrica» dell'ufficio con etichette di ufficio (Sezione, Nome ufficio, Ricevimento, Email ufficio,
     PEC, Telefono, Indirizzo, Orario...). I campi con nomi di persone (Dirigenti, Addetti, Responsabile...) si scartano;
   - gli indirizzi email scritti nel testo che sono caselle d'ufficio (dominio interno.it, nessun nome.cognome);
   - gli allegati (titolo, link, dimensione) e la data «Ultimo aggiornamento»;
   - le «Pagine correlate» (titolo e link: avvisi, contatti, notifiche...); quelle che sembrano avvisi o contatti si
     scaricano anche loro;
   - il testo ripulito della pagina e degli avvisi in una cartella temporanea (CACHE, fuori dal repository: i testi
     possono contenere nomi di funzionari, che il sito non pubblica). Servono a scegliere i punti locali:
     `--candidati <slug>` stampa solo le frasi che sembrano locali (indirizzi, caselle, avvisi, orari, tempi).
3. dati/prefetture.json: un record per prefettura con stato HTTP, data di lettura e campi sopra. I punti «locali»
   (cosa la Prefettura scrive di suo) li sceglie una persona leggendo il testo, con la frase esatta copiata, in
   dati/prefetture_locali.json: il generatore li usa solo se la frase è ancora nel testo salvato.

Una richiesta ogni ~1,5 secondi, user agent dichiarato, nessun aggiramento di blocchi. Nessun dato personale salvato.
"""
import html
import json
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
CACHE = Path(tempfile.gettempdir()) / "esameb1-prefetture"  # testi delle pagine: fuori dal repository (possono contenere nomi di funzionari)
BASE = "https://prefettura.interno.gov.it"
UA = "Mozilla/5.0 (X11; Linux x86_64) EsameB1-controllo-fonti/1.0 (+https://esameb1.netlify.app)"
OGGI = date.today().isoformat()

ELENCO = ("agrigento alessandria ancona aosta arezzo ascoli-piceno asti avellino bari barletta-andria-trani belluno benevento "
          "bergamo biella bologna bolzano brescia brindisi cagliari caltanissetta campobasso caserta catania catanzaro chieti como "
          "cosenza cremona crotone cuneo enna fermo ferrara firenze foggia forli-cesena frosinone genova gorizia grosseto imperia "
          "isernia laquila latina lecce lecco livorno lodi lucca macerata mantova massa-carrara matera messina milano modena "
          "monza-e-brianza napoli novara nuoro oristano padova palermo parma pavia perugia pesaro-urbino pescara piacenza pisa "
          "pistoia pordenone potenza prato ragusa ravenna reggio-calabria reggio-emilia rieti rimini roma rovigo salerno sassari "
          "savona siena siracusa sondrio spezia taranto teramo terni torino trapani trento treviso trieste udine varese venezia "
          "verbano-cusio-ossola vercelli verona vibo-valentia vicenza viterbo").split()

# Nome da mostrare e regione di ogni prefettura (per l'indice per regione). Aosta: in Valle d'Aosta le funzioni prefettizie
# le svolge la Regione; Bolzano e Trento: Commissariato del Governo.
NOMI = {
    "agrigento": ("Agrigento", "Sicilia"), "alessandria": ("Alessandria", "Piemonte"), "ancona": ("Ancona", "Marche"),
    "aosta": ("Aosta", "Valle d'Aosta"), "arezzo": ("Arezzo", "Toscana"), "ascoli-piceno": ("Ascoli Piceno", "Marche"),
    "asti": ("Asti", "Piemonte"), "avellino": ("Avellino", "Campania"), "bari": ("Bari", "Puglia"),
    "barletta-andria-trani": ("Barletta-Andria-Trani", "Puglia"), "belluno": ("Belluno", "Veneto"), "benevento": ("Benevento", "Campania"),
    "bergamo": ("Bergamo", "Lombardia"), "biella": ("Biella", "Piemonte"), "bologna": ("Bologna", "Emilia-Romagna"),
    "bolzano": ("Bolzano", "Trentino-Alto Adige"), "brescia": ("Brescia", "Lombardia"), "brindisi": ("Brindisi", "Puglia"),
    "cagliari": ("Cagliari", "Sardegna"), "caltanissetta": ("Caltanissetta", "Sicilia"), "campobasso": ("Campobasso", "Molise"),
    "caserta": ("Caserta", "Campania"), "catania": ("Catania", "Sicilia"), "catanzaro": ("Catanzaro", "Calabria"),
    "chieti": ("Chieti", "Abruzzo"), "como": ("Como", "Lombardia"), "cosenza": ("Cosenza", "Calabria"),
    "cremona": ("Cremona", "Lombardia"), "crotone": ("Crotone", "Calabria"), "cuneo": ("Cuneo", "Piemonte"),
    "enna": ("Enna", "Sicilia"), "fermo": ("Fermo", "Marche"), "ferrara": ("Ferrara", "Emilia-Romagna"),
    "firenze": ("Firenze", "Toscana"), "foggia": ("Foggia", "Puglia"), "forli-cesena": ("Forlì-Cesena", "Emilia-Romagna"),
    "frosinone": ("Frosinone", "Lazio"), "genova": ("Genova", "Liguria"), "gorizia": ("Gorizia", "Friuli-Venezia Giulia"),
    "grosseto": ("Grosseto", "Toscana"), "imperia": ("Imperia", "Liguria"), "isernia": ("Isernia", "Molise"),
    "laquila": ("L'Aquila", "Abruzzo"), "latina": ("Latina", "Lazio"), "lecce": ("Lecce", "Puglia"),
    "lecco": ("Lecco", "Lombardia"), "livorno": ("Livorno", "Toscana"), "lodi": ("Lodi", "Lombardia"),
    "lucca": ("Lucca", "Toscana"), "macerata": ("Macerata", "Marche"), "mantova": ("Mantova", "Lombardia"),
    "massa-carrara": ("Massa-Carrara", "Toscana"), "matera": ("Matera", "Basilicata"), "messina": ("Messina", "Sicilia"),
    "milano": ("Milano", "Lombardia"), "modena": ("Modena", "Emilia-Romagna"), "monza-e-brianza": ("Monza e della Brianza", "Lombardia"),
    "napoli": ("Napoli", "Campania"), "novara": ("Novara", "Piemonte"), "nuoro": ("Nuoro", "Sardegna"),
    "oristano": ("Oristano", "Sardegna"), "padova": ("Padova", "Veneto"), "palermo": ("Palermo", "Sicilia"),
    "parma": ("Parma", "Emilia-Romagna"), "pavia": ("Pavia", "Lombardia"), "perugia": ("Perugia", "Umbria"),
    "pesaro-urbino": ("Pesaro e Urbino", "Marche"), "pescara": ("Pescara", "Abruzzo"), "piacenza": ("Piacenza", "Emilia-Romagna"),
    "pisa": ("Pisa", "Toscana"), "pistoia": ("Pistoia", "Toscana"), "pordenone": ("Pordenone", "Friuli-Venezia Giulia"),
    "potenza": ("Potenza", "Basilicata"), "prato": ("Prato", "Toscana"), "ragusa": ("Ragusa", "Sicilia"),
    "ravenna": ("Ravenna", "Emilia-Romagna"), "reggio-calabria": ("Reggio Calabria", "Calabria"), "reggio-emilia": ("Reggio Emilia", "Emilia-Romagna"),
    "rieti": ("Rieti", "Lazio"), "rimini": ("Rimini", "Emilia-Romagna"), "roma": ("Roma", "Lazio"),
    "rovigo": ("Rovigo", "Veneto"), "salerno": ("Salerno", "Campania"), "sassari": ("Sassari", "Sardegna"),
    "savona": ("Savona", "Liguria"), "siena": ("Siena", "Toscana"), "siracusa": ("Siracusa", "Sicilia"),
    "sondrio": ("Sondrio", "Lombardia"), "spezia": ("La Spezia", "Liguria"), "taranto": ("Taranto", "Puglia"),
    "teramo": ("Teramo", "Abruzzo"), "terni": ("Terni", "Umbria"), "torino": ("Torino", "Piemonte"),
    "trapani": ("Trapani", "Sicilia"), "trento": ("Trento", "Trentino-Alto Adige"), "treviso": ("Treviso", "Veneto"),
    "trieste": ("Trieste", "Friuli-Venezia Giulia"), "udine": ("Udine", "Friuli-Venezia Giulia"), "varese": ("Varese", "Lombardia"),
    "venezia": ("Venezia", "Veneto"), "verbano-cusio-ossola": ("Verbano-Cusio-Ossola", "Piemonte"), "vercelli": ("Vercelli", "Piemonte"),
    "verona": ("Verona", "Veneto"), "vibo-valentia": ("Vibo Valentia", "Calabria"), "vicenza": ("Vicenza", "Veneto"),
    "viterbo": ("Viterbo", "Lazio"),
}

# Etichette della rubrica che descrivono l'ufficio (si tengono). Tutte le altre (Dirigenti, Addetti, Responsabile,
# Funzionari...) possono contenere nomi di persone e si scartano.
ETICHETTE_UFFICIO = {"sezione", "nome ufficio", "ricevimento", "email ufficio", "pec", "pec ufficio", "telefono", "telefoni", "telefono ufficio",
                     "indirizzo", "sede", "ubicazione", "orario", "orari", "orario di ricevimento", "fax", "email", "posta elettronica certificata"}
TESTO_UFFICIO = {"descrizione", "codice provvedimento"}  # voci della rubrica che restano nel testo ma non sono campi di contatto


def richiesta(url, tentativi=2):
    errore = ""
    for t in range(tentativi):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, r.read(), r.geturl()
        except urllib.error.HTTPError as e:
            return e.code, b"", url
        except Exception as e:
            errore = str(e)
            time.sleep(3 * (t + 1))
    return 0, errore.encode(), url


def pulisci(frammento):
    t = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", frammento)
    t = re.sub(r"(?i)<(br|/p|/li|/h\d|/div|/tr|/td|/th)[^>]*>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    t = re.sub(r"[ \t]+", " ", t)
    return "\n".join(r.strip() for r in t.split("\n") if r.strip())


PAROLE_UFFICIO = ("comunicazione", "polo", "legalizzazion", "cittadinanza", "protocollo", "pref", "urp", "immigrazione", "sportello", "ufficio", "area", "diritti", "civili")


def solo_numeri(testo):
    """Solo i numeri di telefono di un campo (i nomi delle persone accanto ai numeri non si salvano)."""
    return [re.sub(r"\s+", " ", n).strip() for n in re.findall(r"\+?\d[\d /.-]{5,}\d", testo) if sum(c.isdigit() for c in n) >= 8]


def caselle(frammento):
    """Indirizzi email in un pezzo di HTML o testo (anche dentro mailto:, con %20 o spazi codificati)."""
    t = urllib.parse.unquote(html.unescape(frammento)).replace("\xa0", " ")
    return {m.lower().strip(".") for m in re.findall(r"(?<![\w.+-])[a-z0-9][\w.+-]*@[a-z0-9-]+(?:\.[a-z0-9-]+)+", t, re.I)}


def casella_ufficio(mail):
    """Solo caselle d'ufficio del Ministero (…interno.it) con una parola d'ufficio nel nome: nessuna casella personale."""
    m = mail.lower().rstrip(".")
    locale, _, dominio = m.partition("@")
    parti = re.split(r"[._-]", locale)
    return dominio.endswith("interno.it") and any(p.startswith(k) for p in parti for k in PAROLE_UFFICIO)


def leggi(slug):
    url = f"{BASE}/it/prefetture/{slug}/cittadinanza"
    stato, corpo, finale = richiesta(url)
    nome, regione = NOMI.get(slug, (slug.replace("-", " ").title(), ""))
    r = {"slug": slug, "nome": nome, "regione": regione, "url": url, "stato": stato, "letto_il": OGGI}
    if stato != 200:
        return r, ""
    t = corpo.decode("utf-8", "replace")
    titolo = re.search(r"<title>([^<]*)</title>", t)
    r["titolo_pagina"] = html.unescape(titolo.group(1)).strip() if titolo else ""
    nome = re.search(r"Prefettura di ([^<|\-–]+)", r["titolo_pagina"]) or re.search(r'class="site-name[^"]*"[^>]*>([^<]+)<', t)
    i, j = t.find("<main"), t.find("</main>")
    main = t[i:j] if i >= 0 and j > i else t
    # rubrica dell'ufficio: <div class="label">X</div><div class="value">Y</div>. Si tengono solo le etichette d'ufficio;
    # le voci con altre etichette (Dirigenti, Addetti, Responsabile...) si tolgono anche dal testo salvato.
    rubrica = {}
    voce = re.compile(r'<div class="item"><div class="label">(.*?)</div>\s*<div class="value[^"]*">(.*?)</div>\s*</div>', re.S)
    for lab, val in voce.findall(main):
        etichetta = pulisci(lab).strip().lower()
        if etichetta in ETICHETTE_UFFICIO:
            valore = pulisci(val).replace("\n", " · ")
            if etichetta.startswith("email") or "pec" in etichetta or "posta" in etichetta:
                valore = " · ".join(m for m in caselle(val) if casella_ufficio(m))
            if etichetta.startswith("telefon") or etichetta == "fax":
                valore = " · ".join(dict.fromkeys(solo_numeri(valore)))  # nella rubrica i numeri sono spesso accanto al nome dell'addetto
            if valore:
                rubrica.setdefault(pulisci(lab).strip(), []).append(valore)
    r["rubrica"] = {k: " · ".join(dict.fromkeys(v)) for k, v in rubrica.items()}
    main = voce.sub(lambda m: m.group(0) if pulisci(m.group(1)).strip().lower() in ETICHETTE_UFFICIO | TESTO_UFFICIO else " ", main)
    # caselle d'ufficio scritte nel testo
    r["email_testo"] = sorted({m for m in caselle(main) if casella_ufficio(m)} - {m for v in r["rubrica"].values() for m in caselle(v)})
    # allegati
    r["allegati"] = [{"titolo": html.unescape(tit).strip(), "url": (BASE + u if u.startswith("/") else u)}
                     for u, tit in re.findall(r'<a href="([^"]+)" type="[^"]*"[^>]*>([^<]+)</a>', main)]
    agg = re.search(r"Ultimo aggiornamento\s*</[^>]+>\s*(?:<[^>]+>\s*)*([^<]+)<", main)
    r["ultimo_aggiornamento"] = pulisci(agg.group(1)) if agg else ""
    corr = t.split("field--name-field-related-pages", 1)
    r["correlate"] = ([{"titolo": html.unescape(tit).strip(), "url": BASE + u}
                       for u, tit in re.findall(r'<a href="(/it/prefetture/[^"]+)" hreflang="it">([^<]+)</a>', corr[1].split("</div>\n  </div>")[0])]
                      if len(corr) > 1 else [])
    testo = pulisci(main.split("Ultimo aggiornamento")[0])
    r["caratteri"] = len(testo)
    for chiave, parole in {"contributo_250": ("250",), "portale": ("portaleservizi", "portale"), "spid": ("spid",),
                           "giuramento": ("giuramento",), "appuntamento": ("appuntamento",), "tempi": ("tempi", "termine di conclusione", "mesi")}.items():
        r[chiave] = any(p in testo.lower() for p in parole)
    return r, testo


AVVISO = re.compile(r"avvis|comunica|notific|giurament|termin|tempi|appuntament|convoca|orari|ricevimento|contatt|modalit|pagament|"
                    r"contributo|rimbors|integrazion|document|spid|pec|istanz|domand", re.I)


NO_CORRELATA = re.compile(r"decreti emessi|elenco|esito|graduatori", re.I)  # liste di pratiche: non servono e sono lunghe


def leggi_correlata(url):
    """Testo di una pagina correlata (avviso, contatti...), con la data «Ultimo aggiornamento». ("", "") se non si legge."""
    stato, corpo, _ = richiesta(url)
    if stato != 200:
        return "", ""
    t = corpo.decode("utf-8", "replace")
    i, j = t.find("<main"), t.find("</main>")
    main = t[i:j] if i >= 0 and j > i else t
    agg = re.search(r"Ultimo aggiornamento\s*</[^>]+>\s*(?:<[^>]+>\s*)*([^<]+)<", main)
    voce = re.compile(r'<div class="item"><div class="label">(.*?)</div>\s*<div class="value[^"]*">(.*?)</div>\s*</div>', re.S)
    main = voce.sub(lambda m: m.group(0) if pulisci(m.group(1)).strip().lower() in ETICHETTE_UFFICIO | TESTO_UFFICIO else " ", main)
    return pulisci(main.split("Ultimo aggiornamento")[0]), (pulisci(agg.group(1)) if agg else "")


def stato_allegati(r):
    """Stato HTTP di ogni allegato (richiesta di 1 byte): il sito linka solo gli allegati che rispondono 200
    (alcuni file linkati dalle pagine delle Prefetture rispondono 500)."""
    for a in r.get("allegati", []):
        req = urllib.request.Request(a["url"], headers={"User-Agent": UA, "Range": "bytes=0-0"})
        try:
            with urllib.request.urlopen(req, timeout=40) as x:
                a["stato"] = 200 if x.status in (200, 206) else x.status
        except urllib.error.HTTPError as e:
            a["stato"] = e.code
        except Exception:
            a["stato"] = 0
        time.sleep(1.0)


def solo_allegati():
    """--allegati: ricontrolla solo lo stato degli allegati in dati/prefetture.json (senza riscaricare le pagine)."""
    d = json.loads((DATI / "prefetture.json").read_text(encoding="utf-8"))
    for r in d["prefetture"]:
        stato_allegati(r)
        print(r["slug"], [a["stato"] for a in r.get("allegati", [])], flush=True)
    (DATI / "prefetture.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def raccogli():
    stato, corpo, _ = richiesta(f"{BASE}/it/prefetture")
    trovati = sorted(set(re.findall(r'href="/it/prefetture/([a-z0-9-]+)"', corpo.decode("utf-8", "replace")))) if stato == 200 else []
    elenco = trovati if len(trovati) >= 100 else ELENCO
    if trovati and set(trovati) != set(ELENCO):
        print("AVVISO: l'elenco delle prefetture è cambiato:", sorted(set(trovati) ^ set(ELENCO)))
    CACHE.mkdir(parents=True, exist_ok=True)
    out = []
    for n, slug in enumerate(elenco, 1):
        r, testo = leggi(slug)
        parti = [f"# {r['url']} (letto il {OGGI})\n{testo}"] if testo else []
        for c in r.get("correlate", []):
            if (AVVISO.search(c["titolo"]) or re.search(r"cittadinanza|concessione", c["titolo"], re.I)) and not NO_CORRELATA.search(c["titolo"]):
                time.sleep(1.5)
                tc, agg = leggi_correlata(c["url"])
                c["letta"] = bool(tc)
                c["ultimo_aggiornamento"] = agg
                if tc:
                    parti.append(f"# {c['url']} (letto il {OGGI}) — {c['titolo']}\n{tc}")
        stato_allegati(r)
        if parti:
            (CACHE / f"{slug}.txt").write_text("\n\n".join(parti) + "\n", encoding="utf-8")
        out.append(r)
        print(f"{n:3d} {slug:24s} {r['stato']} {r.get('caratteri', 0):6d} car. {len(r.get('rubrica', {}))} campi "
              f"{len(r.get('allegati', []))} allegati {len(r.get('correlate', []))} correlate", flush=True)
        time.sleep(1.5)
    (DATI / "prefetture.json").write_text(json.dumps({
        "_nota": "Raccolto da raccolta/prefetture.py: solo campi d'ufficio (nessun nome di persona) delle pagine «Cittadinanza» delle Prefetture.",
        "letto_il": OGGI, "fonte_elenco": f"{BASE}/it/prefetture", "prefetture": out}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{sum(1 for r in out if r['stato'] == 200)}/{len(out)} pagine lette (200). Testi in {CACHE}")


LOCALE = re.compile(r"@|\b(via|viale|piazza|corso|largo|piazzale)\s+[A-Z0-9]|\btel\.?|telefon|orari|dalle ore|lunedì|martedì|mercoledì|giovedì|venerdì|"
                    r"appuntament|questa prefettura|quest'ufficio|presente ufficio|questo ufficio|si avvisa|si informa|si comunica|si rende noto|avviso|"
                    r"notific|giuramento|tempi|mesi|giorni|ritard|attes|sportello|convoca|ricevimento|pagopa|rimbors|patronat", re.I)


def normalizza(t):
    t = t.replace("\xa0", " ")
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("«", '"'), ("»", '"'), ("–", "-"), ("—", "-")):
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip().lower()


def candidati(slug, max_altre=3):
    """Frasi della pagina (e degli avvisi) che sembrano locali e che non si ripetono in più di max_altre altre prefetture
    (il testo nazionale copiato da molte pagine si salta)."""
    f = CACHE / f"{slug}.txt"
    if not f.exists():
        raise SystemExit(f"manca {f}: lanciare prima la raccolta")
    conta = {}
    for g in CACHE.glob("*.txt"):
        for riga in {normalizza(x) for x in g.read_text(encoding="utf-8").split("\n") if len(x) > 25}:
            conta[riga] = conta.get(riga, 0) + 1
    visti = set()
    for riga in f.read_text(encoding="utf-8").split("\n"):
        n = normalizza(riga)
        if riga.startswith("# "):
            print(riga[:200])
        elif n not in visti and LOCALE.search(riga) and conta.get(n, 0) <= max_altre + 1:
            visti.add(n)
            print("  " + riga[:420])


def testo_vivo(url, cache):
    """Testo normalizzato di una pagina (Prefettura: solo <main>; altre: tutta la pagina), scaricato ora. None se non risponde 200."""
    if url not in cache:
        stato, corpo, _ = richiesta(url)
        if stato != 200:
            cache[url] = None
        else:
            t = corpo.decode("utf-8", "replace")
            i, j = t.find("<main"), t.find("</main>")
            cache[url] = normalizza(pulisci(t[i:j] if i >= 0 and j > i else t))
        time.sleep(1.0)
    return cache[url]


def controlla():
    """Link 200 e frasi citate ancora presenti nelle pagine vive: dati nazionali (dati/cittadinanza.json) e punti locali scelti
    a mano (dati/prefetture_locali.json: frasi della pagina Cittadinanza della Prefettura o della pagina correlata indicata)."""
    naz = json.loads((DATI / "cittadinanza.json").read_text(encoding="utf-8"))
    locali = json.loads((DATI / "prefetture_locali.json").read_text(encoding="utf-8"))
    errori, frasi, cache = [], 0, {}
    for k, f in naz["fonti"].items():
        stato, _, _ = richiesta(f["url"])
        if stato != 200:
            errori.append(f"fonte nazionale {k}: {stato}")
    for c in naz["citazioni"]:
        frasi += 1
        t = testo_vivo(naz["fonti"][c["fonte"]]["url"], cache)
        if t is None or normalizza(c["testo"]) not in t:
            errori.append(f"nazionale/{c['fonte']}: frase non trovata: «{c['testo']}»")
    for slug, p in locali["prefetture"].items():
        base = f"{BASE}/it/prefetture/{slug}/cittadinanza"
        for punto in p.get("punti", []) + p.get("contatti", []):
            url = punto.get("url") or base
            t = testo_vivo(url, cache)
            if t is None:
                errori.append(f"{slug}: pagina non raggiungibile {url}")
                continue
            for c in punto["citazioni"]:
                frasi += 1
                if normalizza(c) not in t:
                    errori.append(f"{slug}: frase non trovata in {url}: «{c}»")
        for link in p.get("link", []):
            s, _, _ = richiesta(link["url"])
            if s != 200:
                errori.append(f"{slug}: link {s} {link['url']}")
    print(f"Prefetture con punti locali: {len(locali['prefetture'])}; pagine lette: {len(cache)}; frasi: {frasi}; errori: {len(errori)}")
    for e in errori:
        print("ERRORE:", e)
    return 1 if errori else 0


if __name__ == "__main__":
    if "--candidati" in sys.argv:
        candidati(sys.argv[sys.argv.index("--candidati") + 1])
        sys.exit(0)
    if "--allegati" in sys.argv:
        solo_allegati()
        sys.exit(0)
    if "--controlla" in sys.argv:
        sys.exit(controlla())
    raccogli()
