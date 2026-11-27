"""Controllo del sito generato di EsameB1 (esameb1/sito/), da lanciare dopo python3 esameb1/genera.py.

Uso (dalla radice del repository):
    python3 esameb1/verifica.py        # stampa il riepilogo; esce con 1 se c'è almeno un errore

Controlla, su tutte le pagine HTML:
- meta di verifica di Search Console (entrambe le proprietà), canonical giusto, un solo h1;
- sitemap e noindex coerenti (una pagina noindex non è in sitemap, una pagina in indice sì; la 404 è esclusa);
- sitemap.xml indice di sitemap di sezione, lastmod uguale al registro dati/lastmod.json, robots.txt con il solo indice,
  sitemap-vecchi-indirizzi.xml fuori dall'indice e con soli vecchi indirizzi vivi; la home non linka pagine noindex (25/11/2026);
- AdSense mai nelle pagine noindex; cancello della pubblicità rifatto qui (controlli_cancello): niente script e niente link di
  affiliazione sotto la soglia di parole proprie, niente script nelle privacy, script nella home;
- JSON-LD valido; ogni domanda e risposta del FAQPage è visibile nel testo della pagina;
- link interni e ancore (#id) esistenti;
- titoli ≤ 65 e description ≤ 155 caratteri, nessun titolo o description doppi tra le pagine in indice;
- nessuna parola di servizio rimasta nel testo (TODO, None, undefined, NaN, nomi di modelli).
- pagina /per-le-scuole/ e pulsante «Sei questa sede?» (27/11/2026, controlli_scuole): modulo Netlify «scuole» con tutti i campi, tre eventi di
  clic, pulsante su ogni scheda sede delle pagine città e solo lì, pulsante fuori dall'impronta del lastmod, regola «sponsorizzato» scritta,
  nessun pulsante che vende e nessun link di pagamento, cancello della pubblicità rispettato.
- pagine CPIA (/cpia/<slug>/, dal 20/11/2026) contro dati/cpia.json e dati/parole_cpia.json: una pagina per ogni CPIA dei dati e nessuna in più,
  titolo che comincia con la ricerca misurata (volume > 0), codice della scuola e tutte le sedi dell'anagrafe in pagina, fonte del Ministero
  con data di lettura, ogni testo tra «» uguale a una frase citata nei dati, riquadro del libro con l'etichetta libro-cpia e nessun link sponsorizzato.
- formato «citabile» (27/11/2026, controlli_citabile, dati/citabile.json): riquadro dei dati ufficiali solo nelle pagine dell'elenco, una volta sola;
  data «Pagina aggiornata il» = dateModified = lastmod del registro e della sitemap, e fuori dall'impronta; ogni riga con link alla fonte
  ufficiale e data del controllo; cifre del riquadro uguali ai dati; titolo, H1 e description uguali a prima; Pass, libro e pubblicità al loro posto.
Nato dallo script di controllo usato nelle revisioni del 31/10-12/11/2026 (scratchpad), scritto qui il 13/11/2026.
"""
import collections
import json
import re
import sys
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urlparse

SITO = Path(__file__).resolve().parent / "sito"
URL = "https://esameb1.eu/"
VERIFICHE = ("btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI", "oqTPjb5TjEbrEBUVj-ToW2AiPp1Vw85qL8ZHibY28FI")
VIETATE = ("TODO", "Lorem", "None", "undefined", "NaN", " null ", "Claude", "GPT", "Anthropic", "Gemini")


def testo(h):
    h = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", h)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", h)))


def controlli_cpia(err):
    """Pagine /cpia/<slug>/ contro i dati: vedi l'elenco in cima al file. Restituisce il numero di pagine CPIA controllate."""
    dati = SITO.parent / "dati"
    if not (dati / "cpia.json").exists():
        return 0
    D = json.loads((dati / "cpia.json").read_text(encoding="utf-8"))
    volumi = json.loads((dati / "parole_cpia.json").read_text(encoding="utf-8"))["parole"]
    attese = {c["slug"] for c in D["cpia"]}
    trovate = {p.parent.name for p in (SITO / "cpia").glob("*/index.html")}
    for sl in sorted(attese ^ trovate):
        err.append(f"cpia/{sl}/: pagina senza dati o dati senza pagina")
    if not (SITO / "cpia" / "index.html").exists():
        err.append("cpia/index.html: manca l'indice dei CPIA")
    giorno, mese, anno = int(D["anagrafe"]["letta_il"][8:]), int(D["anagrafe"]["letta_il"][5:7]), D["anagrafe"]["letta_il"][:4]
    mesi = "gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre".split()
    letta = f"{giorno} {mesi[mese - 1]} {anno}"
    for c in D["cpia"]:
        f = SITO / "cpia" / c["slug"] / "index.html"
        if not f.exists():
            continue
        h = f.read_text(encoding="utf-8")
        rel = f"cpia/{c['slug']}/index.html"
        corpo = h[h.find("<main"):h.find("</main>")]
        t = testo(corpo)
        titolo = unescape(re.search(r"<title>(.*?)</title>", h, re.S).group(1))
        if not volumi.get(c["ricerca"], 0) > 0 or not titolo.lower().startswith(c["ricerca"].lower()):
            err.append(f"{rel}: il titolo non comincia con una ricerca misurata («{c['ricerca']}»)")
        if not re.fullmatch(r"[A-Z]{2}MM[0-9A-Z]{6}", c["codice"]) or c["codice"] not in t:
            err.append(f"{rel}: codice della scuola assente o non valido")
        for s in c["sedi"]:
            if s["codice"] not in t or s["cap"] not in t or "Non Disponibile" in t or "CARCER" in (s["nome"] + " " + s["indirizzo"]).upper():
                err.append(f"{rel}: sede {s['codice']} dell'anagrafe non in pagina")
        if "dati.istruzione.it" not in corpo or f"letta il {letta}" not in t:
            err.append(f"{rel}: manca la fonte del Ministero con la data di lettura")
        citate = {re.sub(r"\s+", " ", x["testo"]) for voci in c["citazioni"].values() for x in voci} | {c["nome_anagrafe"], "Centro territoriale"}
        avvisi = {x["citazione"] for x in json.loads((dati / "avvisi_sedi.json").read_text(encoding="utf-8"))["avvisi"]}  # avviso ufficiale di una sede
        for frase in re.findall(r"«([^»]+)»", t):
            if frase.strip() not in citate | avvisi:
                err.append(f"{rel}: testo tra virgolette non citato nei dati: {frase[:60]}")
        for x in citate - {"Centro territoriale"}:
            if x not in t:
                err.append(f"{rel}: frase dei dati non in pagina: {x[:60]}")
        libro = re.findall(r'<a [^>]*data-libro-proprio="si"[^>]*>', corpo)
        if not libro or any('data-goatcounter-click="esameb1.eu/clic/libro-cpia"' not in x for x in libro):
            err.append(f"{rel}: riquadro del libro assente o con un'altra etichetta")
        if "sponsored" in corpo:
            err.append(f"{rel}: link sponsorizzato in una pagina CPIA")
        for tema, parola in (("test_a2", "test A2"), ("certificazioni", "esami")):
            if not c["citazioni"].get(tema) and parola in titolo:
                err.append(f"{rel}: il titolo promette «{parola}» ma nei dati non c'è una frase del CPIA")
    return len(attese & trovate)


CLIC_SCUOLE = ("esameb1.eu/clic/scuole-licenza", "esameb1.eu/clic/scuole-scheda")
CLIC_SEDE = "esameb1.eu/clic/sede-sei-tu"
PAGAMENTI = r"stripe\.com|paypal|gumroad|lemonsqueezy|paddle\.com|checkout|satispay|sumup|buy\.|/pay/|/paga"
RE_PULSANTE_SEDE = re.compile(r'<a class="sede-tu" href="([^"]*?)(?:&amp;provincia=1)?(#modulo)" data-goatcounter-click="([^"]*)"[^>]*>([^<]*)</a>')


def controlli_scuole(err, sotto_soglia):
    """Prova di domanda «EsameB1 per le sedi e le scuole» (27/11/2026). Controlli scritti qui, senza usare genera_scuole.py:
    a) la pagina c'è, è in indice e supera il cancello della pubblicità (non è tra le pagine sotto la soglia e ha lo script);
    b) modulo Netlify «scuole»: attributo data-netlify, trappola per i robot, tutti i campi, le 4 scelte del ruolo e le 3 dell'interesse,
       messaggio di conferma; action "/" (nessun invio a terzi);
    c) i due eventi di clic sui pulsanti «Mi interessa», una volta ciascuno, su un link che porta solo a #modulo: nessun pulsante vende;
    d) nessun link di pagamento e nessuna parola da negozio nei pulsanti; i due prezzi veri e l'avviso «non vendiamo niente» ci sono;
    e) regola della scheda a pagamento scritta («sponsorizzato», una per città, mai nell'elenco ufficiale) e «non affiliato»; oggi nessuna
       pagina città ha una scheda a pagamento;
    f) pagine città: ogni scheda sede finisce con il pulsante «Sei questa sede?» (evento sede-sei-tu, link a /per-le-scuole/?citta=<slug
       della pagina>#modulo), una volta sola; fuori dalle pagine città il pulsante non c'è;
    g) il pulsante è fuori dall'impronta del lastmod: l'impronta di genera.py della pagina con e senza pulsanti è la stessa ed è quella
       scritta in dati/lastmod.json;
    h) privacy con la frase sul modulo; link alla pagina da «Chi siamo» e dalla prova online.
    Restituisce (schede con il pulsante, pagine città controllate)."""
    f = SITO / "per-le-scuole" / "index.html"
    if not f.exists():
        err.append("per-le-scuole/index.html: la pagina non esiste")
        return 0, 0
    h = f.read_text(encoding="utf-8")
    head, corpo = h[:h.find("</head>")], m_main(h)
    t = testo(corpo)
    if '<meta name="robots" content="noindex' in head:
        err.append("per-le-scuole/: la pagina è in noindex")
    if "per-le-scuole/index.html" in sotto_soglia or SCRIPT_ADSENSE not in head:
        err.append(f"per-le-scuole/: sotto il cancello della pubblicità ({sotto_soglia.get('per-le-scuole/index.html')} parole proprie) o senza script")
    moduli = re.findall(r"<form\b([^>]*)>(.*?)</form>", corpo, re.S)
    if len(moduli) != 1:
        err.append(f"per-le-scuole/: {len(moduli)} moduli, ne serve uno")
    else:
        attr, dentro = moduli[0]
        for pezzo in ('name="scuole"', 'data-netlify="true"', 'netlify-honeypot="bot-field"', 'method="POST"', 'action="/"'):
            if pezzo not in attr:
                err.append(f"per-le-scuole/: nel <form> manca {pezzo}")
        campi = {"form-name": r'<input type="hidden" name="form-name" value="scuole">', "bot-field": r'<input name="bot-field"',
                 "scuola": r'<input type="text" name="scuola" required', "citta": r'<input type="text" name="citta" required',
                 "ruolo": r'<select name="ruolo" required', "candidati": r'<select name="candidati"', "interesse": r'<select name="interesse" required',
                 "email": r'<input type="email" name="email" required', "messaggio": r'<textarea name="messaggio"(?![^>]*required)'}
        for nome, modello in campi.items():
            if len(re.findall(modello, dentro)) != 1:
                err.append(f"per-le-scuole/: campo «{nome}» del modulo assente, doppio o diverso")
        scelte = {n: [unescape(x) for x in re.findall(r"<option value=\"([^\"]+)\"", sel)] for n, sel in re.findall(r'<select name="(\w+)"[^>]*>(.*?)</select>', dentro, re.S)}
        ruoli = " ".join(scelte.get("ruolo", [])).lower()
        if len(scelte.get("ruolo", [])) != 4 or any(x not in ruoli for x in ("sede d'esame", "scuola", "cooperativa", "altro")):
            err.append("per-le-scuole/: le scelte del ruolo non sono sede d'esame, scuola, cooperativa, altro")
        if scelte.get("interesse") != ["gratis", "licenza", "scheda"] or re.search(r"<option[^>]*\bselected", dentro):
            err.append("per-le-scuole/: le scelte dell'interesse non sono gratis (per prima), licenza, scheda, o una scelta è già fatta")
        if len(scelte.get("candidati", [])) < 3:
            err.append("per-le-scuole/: mancano le scelte sul numero di candidati")
        if not re.search(r'<div class="ok" data-ok hidden>', corpo) or "data-errore" not in dentro or 'type="submit"' not in dentro:
            err.append("per-le-scuole/: mancano il pulsante di invio, il messaggio di conferma o quello di errore")
    for clic in CLIC_SCUOLE:
        tag = re.findall(r"<(\w+)\b([^>]*data-goatcounter-click=\"" + re.escape(clic) + r"\"[^>]*)>", h)
        if len(tag) != 1 or tag[0][0] != "a" or 'href="#modulo"' not in tag[0][1] or f'data-interesse="{clic.rsplit("-", 1)[1]}"' not in tag[0][1]:
            err.append(f"per-le-scuole/: l'evento {clic} deve stare una volta sola, su un link che porta al modulo con l'interesse scelto")
    for href in re.findall(r'<a\b[^>]*href="([^"]+)"', corpo) + re.findall(r'<form\b[^>]*action="([^"]+)"', corpo):
        if re.search(PAGAMENTI, href, re.I):
            err.append(f"per-le-scuole/: link di pagamento {href}")
    for etichetta in re.findall(r'<(?:a class="btn[^"]*"|button)\b[^>]*>(.*?)</(?:a|button)>', corpo, re.S):
        if re.search(r"\b(acquista|compra|paga|ordina|abbonati|carrello)\b", testo(etichetta), re.I):
            err.append(f"per-le-scuole/: pulsante che vende: {testo(etichetta).strip()[:50]}")
    for frase in ("199 €", "29 €", "Oggi non vendiamo niente e non chiediamo pagamenti", "«sponsorizzato»", "una per città",
                  "non entra mai nell'elenco ufficiale delle sedi e non ne cambia l'ordine", "non è affiliato a CILS, CELI, PLIDA o CERT.IT", "MEPA",
                  "mai i file degli enti"):
        if frase.lower() not in t.lower():
            err.append(f"per-le-scuole/: nel testo manca «{frase}»")
    n_schede = n_pagine = 0
    impronta = None
    try:  # g) l'impronta è quella di genera.py: qui si controlla solo che non veda i pulsanti (tolti con l'espressione scritta in questo file)
        sys.path.insert(0, str(SITO.parent))
        import genera
        impronta = genera.impronta_contenuto
    except Exception as e:  # noqa: BLE001
        err.append(f"pulsante «Sei questa sede?»: impossibile leggere l'impronta di genera.py ({e})")
    registro = json.loads((SITO.parent / "dati" / "lastmod.json").read_text(encoding="utf-8"))["pagine"]
    for p in sorted(SITO.rglob("*.html")):
        rel = p.relative_to(SITO).as_posix()
        x = p.read_text(encoding="utf-8")
        pulsanti = RE_PULSANTE_SEDE.findall(x)
        parti = rel.split("/")
        if not (parti[0] == "citta" and len(parti) == 3):
            if pulsanti or "sede-sei-tu" in x:
                err.append(f"{rel}: pulsante «Sei questa sede?» fuori dalle pagine città")
            continue
        n_pagine += 1
        schede = re.findall(r'<li class="s-[A-Z]+">(.*?)</li>', m_main(x), re.S)
        atteso = (f"../../per-le-scuole/?citta={parti[1]}", "#modulo", CLIC_SEDE, "Sei questa sede? Aggiungi corso e date")
        if not schede:
            err.append(f"{rel}: nessuna scheda sede")
        for sc in schede:
            suoi = RE_PULSANTE_SEDE.findall(sc)
            if len(suoi) != 1 or suoi[0] != atteso or not sc.rstrip().endswith("</a>") or sc.index("Fonte:") > sc.index('class="sede-tu"'):
                err.append(f"{rel}: una scheda sede è senza il pulsante «Sei questa sede?», lo ha doppio, diverso o non in fondo")
                break
        n_schede += len(schede)
        if len(pulsanti) != len(schede) or x.count("sede-sei-tu") != len(schede):
            err.append(f"{rel}: {len(pulsanti)} pulsanti «Sei questa sede?» per {len(schede)} schede")
        if re.search(r"sponsorizzat", testo(re.sub(r'<section class="card prep".*?</section>', " ", m_main(x), flags=re.S)), re.I):
            err.append(f"{rel}: la parola «sponsorizzato» in una pagina città (oggi nessuna scheda è a pagamento)")
        if impronta:
            senza = RE_PULSANTE_SEDE.sub("", x)
            voce = registro.get(rel[:-len("index.html")], [None, None])[1]
            # TODO (27/11/2026): far scrivere a genera.py il registro dopo soglia_parole_proprie(), poi togliere questa eccezione.
            # le pagine sotto la soglia della pubblicità perdono i link di affiliazione dopo la scrittura del registro: lì il confronto con il registro non vale
            if senza == x or impronta(x) != impronta(senza) or (voce is not None and rel not in sotto_soglia and voce != impronta(senza)):
                err.append(f"{rel}: il pulsante «Sei questa sede?» entra nell'impronta del lastmod")
    if n_pagine == 0:
        err.append("pagine città: nessuna trovata")
    priv = testo((SITO / "privacy.html").read_text(encoding="utf-8"))
    dopo = priv[priv.find("per le sedi d'esame e le scuole"):][:700] if "per le sedi d'esame e le scuole" in priv else ""
    if any(x not in dopo for x in ("solo per risponderti", "art. 6.1.b GDPR", "Li cancelliamo dopo averti risposto")):
        err.append("privacy.html: manca la frase sul modulo delle scuole (dati usati solo per rispondere, base giuridica, cancellazione)")
    if "Li cancelliamo dopo averti risposto" not in t:
        err.append("per-le-scuole/: sotto il modulo manca quando cancelliamo i dati")
    # numero di sedi scritto in pagina: mai più delle schede diverse che stanno davvero nelle pagine città (conto rifatto qui)
    diverse = set()
    for p in sorted((SITO / "citta").glob("*/index.html")):
        diverse.update(RE_PULSANTE_SEDE.sub("", sc) for sc in re.findall(r'<li class="s-[A-Z]+">(.*?)</li>', m_main(p.read_text(encoding="utf-8")), re.S))
    scritto = re.search(r"schede di oltre (\d+) sedi d'esame, in (\d+) pagine città", t)
    if not scritto or not 0 < len(diverse) - int(scritto.group(1)) <= 100 or int(scritto.group(2)) != n_pagine:
        err.append(f"per-le-scuole/: numero di sedi o di pagine città diverso dal vero ({len(diverse)} schede diverse, {n_pagine} pagine)")
    for frase in ("senza audio", "l'ascolto con audio è in preparazione", "con o senza IVA", "quante visite ha avuto la pagina della tua città"):
        if frase not in t:
            err.append(f"per-le-scuole/: nel testo manca «{frase}»")
    for da, rel_link in (("chi-siamo/index.html", "../per-le-scuole/"), ("prova-b1-online/index.html", "../per-le-scuole/")):
        if f'href="{rel_link}"' not in m_main((SITO / da).read_text(encoding="utf-8")):
            err.append(f"{da}: manca il link a /per-le-scuole/")
    if "Insegni" not in testo(m_main((SITO / "prova-b1-online" / "index.html").read_text(encoding="utf-8"))):
        err.append("prova-b1-online/: manca la riga «Insegni…?»")
    return n_schede, n_pagine


SOGLIA_PAROLE_PROPRIE = 110  # la stessa di genera.py (MIN_PAROLE_PROPRIE_ADSENSE): qui è scritta a mano apposta, mai sotto 100
SCRIPT_ADSENSE = "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"


def controlli_cancello(err):
    """Cancello della pubblicità (26/11/2026), misura rifatta qui senza usare genera.py: parole proprie = parole del <main> (senza
    riquadro di affiliazione, briciole, script, stili, icone, menu a tendina) fuori da ogni gruppo di 5 parole presente in almeno
    3 pagine. Ogni pagina sotto la soglia: niente script AdSense e niente link rel="sponsored". Ogni pagina con lo script: sopra la
    soglia, in indice, non privacy. La home ha lo script. L'elenco coincide con dati/cancello_pubblicita.json.
    Restituisce (pagine con script, pagine sotto la soglia, {pagina sotto la soglia: parole proprie})."""
    testi = {}
    for f in sorted(SITO.rglob("*.html")):
        h = f.read_text(encoding="utf-8")
        m = re.search(r"<main[^>]*>(.*?)</main>", h, re.S)
        if not m:
            continue
        corpo = re.sub(r'<section class="card prep".*?</section>', " ", m.group(1), flags=re.S)
        corpo = re.sub(r'<a class="sede-tu".*?</a>', " ", corpo, flags=re.S)  # 27/11/2026: pulsante «Sei questa sede?» delle schede, fuori dalla misura
        corpo = re.sub(r"<(nav|script|style|svg|select)\b.*?</\1>", " ", corpo, flags=re.S | re.I)
        testi[str(f.relative_to(SITO))] = (re.findall(r"\w+", unescape(re.sub(r"<[^>]+>", " ", corpo)).lower()), h)
    quante = collections.Counter()
    gruppi = {}
    for rel, (w, _) in testi.items():
        gruppi[rel] = [tuple(w[i:i + 5]) for i in range(len(w) - 4)]
        quante.update(set(gruppi[rel]))
    sotto, con_script = {}, 0
    for rel, (w, h) in testi.items():
        comune = [False] * len(w)
        for i, g in enumerate(gruppi[rel]):
            if quante[g] >= 3:
                comune[i:i + 5] = [True] * 5
        proprie = comune.count(False)
        head = h[:h.find("</head>")]
        script = SCRIPT_ADSENSE in head
        con_script += script
        noindex = '<meta name="robots" content="noindex' in head
        privacy = rel == "privacy.html" or rel.endswith("privacy/index.html")
        if SCRIPT_ADSENSE in h[h.find("</head>"):]:
            err.append(f"{rel}: script AdSense fuori dal <head>")
        if privacy:
            if script:
                err.append(f"{rel}: script AdSense in una pagina privacy")
            continue
        if proprie < SOGLIA_PAROLE_PROPRIE:
            if script:
                err.append(f"{rel}: script AdSense con {proprie} parole proprie (soglia {SOGLIA_PAROLE_PROPRIE})")
            if not noindex and rel != "404.html":
                if re.search(r'<a\b[^>]*\brel="[^"]*\bsponsored\b', h) or "di affiliazione" in unescape(re.sub(r"<[^>]+>", " ", m_main(h))):
                    err.append(f"{rel}: link di affiliazione o riga di trasparenza in una pagina sotto la soglia")
                sotto[rel] = proprie
        elif not script and not noindex and len(re.findall(r"\w+", unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(form|script|style|svg)\b.*?</\1>", " ", m_main(h), flags=re.S))))) >= 400:
            err.append(f"{rel}: {proprie} parole proprie e testo sufficiente, ma senza script AdSense")
    if SCRIPT_ADSENSE not in (SITO / "index.html").read_text(encoding="utf-8").split("</head>")[0]:
        err.append("index.html: la home non ha lo script AdSense")
    C = json.loads((SITO.parent / "dati" / "cancello_pubblicita.json").read_text(encoding="utf-8"))
    if SOGLIA_PAROLE_PROPRIE < 100 or C["soglia_parole_proprie"] != SOGLIA_PAROLE_PROPRIE:
        err.append("cancello della pubblicità: soglia sotto 100 o diversa tra verifica.py e dati/cancello_pubblicita.json")
    diverse = sorted((k, v, sotto.get(k)) for k, v in C["pagine"].items() if sotto.get(k) != v)
    if diverse:
        err.append(f"cancello della pubblicità: misura rifatta diversa da dati/cancello_pubblicita.json (pagina, là, qui): {diverse[:5]}")
    return con_script, len(sotto), sotto


def controlli_citabile(err, registro, lastmod_sitemap, sotto_soglia):
    """Formato «citabile» (27/11/2026, scheda studio-business/schede/2026-11-27-esameb1-citabile.md). Restituisce il numero di pagine controllate.
    a) il riquadro (id="dati-ufficiali") c'è una volta sola nelle pagine di dati/citabile.json e in nessun'altra; con "attivo": false in nessuna;
    b) «Pagina aggiornata il <data>», dateModified del nodo WebPage e lastmod (registro e sitemap) sono la stessa data; nessun segnaposto rimasto;
    c) la data è fuori dall'impronta: cambiandola l'impronta di genera.py non cambia ed è quella del registro;
    d) ogni riga della tabella ha almeno un link a una fonte fuori dal sito e «controllato il <data>»; isBasedOn = i link del riquadro;
    e) le cifre vengono dai dati: durata, punteggio, costo (pagine ente), costo breve e durata dei 4 enti (indice), numero dei file con link
       diretto di ogni gruppo, tutti presenti nella pagina (pagine dei livelli);
    f) titolo, H1 e description uguali a prima del formato (niente riscrittura dei titoli); FAQPage ancora primo JSON-LD;
    g) riquadro del Pass una volta sola dove c'era, riquadro del libro presente, script AdSense presente (pagine sopra la soglia)."""
    dati = SITO.parent / "dati"
    C = json.loads((dati / "citabile.json").read_text(encoding="utf-8"))
    attese = set(C["pagine"]) if C.get("attivo") else set()
    for rel in C.get("controllo", {}):  # pagine tenute fuori apposta fino al verdetto: esistono e non sono anche tra le trattate
        if rel in C["pagine"] or not (SITO / rel / "index.html").exists():
            err.append(f"{rel}: pagina di controllo del formato citabile che è anche trattata, o che non esiste")
    for f in sorted(SITO.rglob("*.html")):
        h = f.read_text(encoding="utf-8")
        rel = str(f.relative_to(SITO)).replace("index.html", "")
        if "9999-12-31" in h:
            err.append(f"{rel}: segnaposto della data del formato citabile rimasto nella pagina")
        if rel not in attese and ('class="cit-agg"' in h or 'class="card cit"' in h or 'class="cit card"' in h or '"@type": "WebPage"' in h):
            err.append(f"{rel}: elementi del formato citabile in una pagina fuori da dati/citabile.json")
    if not attese:
        return 0
    try:
        sys.path.insert(0, str(SITO.parent))
        import genera
    except Exception as e:  # noqa: BLE001
        err.append(f"formato citabile: impossibile leggere genera.py ({e})")
        return 0
    E = {e["sigla"]: e for e in json.loads((dati / "enti.json").read_text(encoding="utf-8"))}
    R = json.loads((dati / "risultati.json").read_text(encoding="utf-8"))["enti"]
    ES = {e["sigla"]: e for e in json.loads((dati / "esempi.json").read_text(encoding="utf-8"))["enti"]}
    FILE = {k: json.loads((dati / f"{k}.json").read_text(encoding="utf-8")) for k in ("esempi_livelli", "dopo_esame")}
    mesi = "gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre".split()
    for rel, voce in sorted(C["pagine"].items()):
        f = SITO / rel / "index.html"
        if not f.exists():
            err.append(f"{rel}: pagina di dati/citabile.json che non esiste")
            continue
        h = f.read_text(encoding="utf-8")
        riq = re.findall(r'<section class="(?:card cit|cit card)" id="dati-ufficiali".*?</section>', h, re.S)
        if len(riq) != 1 or h.count('id="dati-ufficiali"') != 1:
            err.append(f"{rel}: il riquadro dei dati ufficiali deve esserci una volta sola (trovati {len(riq)})")
            continue
        riq = riq[0]
        visibile = testo(riq)
        # b) una sola data, uguale ovunque
        giorno = registro.get(rel, [None])[0]
        m = re.search(r'<time class="cit-agg" datetime="(20\d\d-\d\d-\d\d)">([^<]+)</time>', riq)
        nodi = [n for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S) for n in [json.loads(b)] if isinstance(n, dict)]
        web = [n for n in nodi if n.get("@type") == "WebPage"]
        if not m or not giorno or m.group(1) != giorno or m.group(2) != f"{int(giorno[8:])} {mesi[int(giorno[5:7]) - 1]} {giorno[:4]}":
            err.append(f"{rel}: «Pagina aggiornata il» diversa dal registro dati/lastmod.json ({giorno})")
        if len(web) != 1 or web[0].get("dateModified") != giorno or web[0].get("url") != URL + rel or lastmod_sitemap.get(URL + rel) != giorno:
            err.append(f"{rel}: dateModified, indirizzo o lastmod della sitemap diversi dal registro ({giorno})")
        if not nodi or nodi[0].get("@type") != "FAQPage":
            err.append(f"{rel}: il primo JSON-LD deve restare il FAQPage")
        # c) la data fuori dall'impronta
        altra = re.sub(r'(<time class="cit-agg" datetime=")[^"]*(">)[^<]*', r"\g<1>2001-01-01\g<2>1 gennaio 2001", h).replace(f'"dateModified": "{giorno}"', '"dateModified": "2001-01-01"')
        if rel not in sotto_soglia and (altra == h or genera.impronta_contenuto(altra) != genera.impronta_contenuto(h)
                                       or genera.impronta_contenuto(h) != registro.get(rel, [None, None])[1]):
            err.append(f"{rel}: la data del formato citabile entra nell'impronta del lastmod, o l'impronta non è quella del registro")
        # d) fonte e data in ogni riga
        righe = re.findall(r"<tr>(.*?)</tr>", riq[riq.find("<tbody>"):], re.S)
        link_riq = []
        for r in righe:
            link = [unescape(u) for u in re.findall(r'<td class="cit-f"[^>]*>.*?</td>', r, re.S) for u in re.findall(r'href="(https://[^"]+)"', u)]
            link_riq += link
            if not link or any("esameb1" in u for u in link) or not re.search(r"controllato il \d{1,2} [a-z]+ 20\d\d", testo(r)):
                err.append(f"{rel}: una riga del riquadro è senza fonte ufficiale o senza data del controllo: {testo(r)[:60]}")
        if not righe or (web and sorted(set(web[0].get("isBasedOn", []))) != sorted(set(link_riq))):
            err.append(f"{rel}: isBasedOn diverso dalle fonti del riquadro, o riquadro senza righe")
        # e) cifre = dati
        attesi = []
        if voce["regola"] == "ente_b1":
            s_ = voce["ente"]
            attesi = [E[s_]["fatti"]["durata"]["prove"]["totale"], R[s_]["tabella"]["superare"], R[s_]["tabella"]["ripeti"], E[s_]["fatti"]["costo"]["testo"],
                      f"il {ES[s_]['esame']} dura {E[s_]['fatti']['durata']['prove']['totale']}", "Per superare serve", "se non superi una parte"]
            if ES[s_].get("link_diretti", True):
                attesi.append(f"{len(ES[s_]['file'])} file")
                if any(escape_(x["url"]) not in h for x in ES[s_]["file"]):
                    err.append(f"{rel}: un file ufficiale contato nel riquadro non è nella pagina")
        elif voce["regola"] == "indice_b1":
            for s_ in E:
                attesi += [E[s_]["fatti"]["durata"]["prove"]["totale"], E[s_]["fatti"]["costo"]["breve"], ES[s_]["esame"]]
        else:
            n = 0
            for g in voce["gruppi"]:
                D = FILE[g["dati"]]
                gr = D["gruppi"][g["gruppo"]] if g["dati"] == "esempi_livelli" else {"file": D["esempi"][g["gruppo"]], "esame": g["esame"]}
                attesi.append(gr["esame"])
                if gr.get("link_diretti", True):
                    n += len(gr["file"])
                    attesi.append(f"{len(gr['file'])} file")
                    if any(escape_(x["url"]) not in h for x in gr["file"]):
                        err.append(f"{rel}: un file contato nel riquadro ({gr['esame']}) non ha il link nella pagina")
            if len(voce["gruppi"]) > 1:
                attesi.append(f"In breve: {n} file ufficiali gratis con link diretto")
        if ("<details" in riq) != (len(righe) > 1):  # una riga sola: tabella aperta, senza comando; più righe: chiusa su telefono
            err.append(f"{rel}: tabella del riquadro con il comando «apri» sbagliato per {len(righe)} righe")
        if "fonti ufficiali e date dei controlli nella tabella" not in visibile or not re.search(r"Dati: [^·]*\((CILS|CELI|PLIDA|CERT\.IT)\)", visibile):
            err.append(f"{rel}: nella riga della data manca l'ente dei dati o «date dei controlli nella tabella»")
        compatto = re.sub(r"\s+", "", visibile).lower()
        for a in attesi:
            if re.sub(r"\s+", "", a).lower() not in compatto:
                err.append(f"{rel}: nel riquadro manca il dato «{a[:60]}» di dati/")
        # f) titolo, H1 e description come prima
        for nome, espr in (("titolo", r"<title>(.*?)</title>"), ("h1", r"<h1[^>]*>(.*?)</h1>"), ("description", r'<meta name="description" content="(.*?)">')):
            x = re.search(espr, h, re.S)
            if not x or x.group(1) != voce[nome]:
                err.append(f"{rel}: {nome} cambiato rispetto a dati/citabile.json (se il cambio è voluto, aggiorna lì la voce «{nome}»)")
        # g) Pass, libro, pubblicità
        if h.count('id="pass"') != (0 if rel.split("/")[1] in ("a1", "a2", "b2", "c1", "c2") else 1):
            err.append(f"{rel}: riquadro del Pass assente, doppio o comparso dove non c'era")
        if rel not in ("esempi/a2/", "esempi/b2/") and 'data-libro-proprio="si"' not in h:  # A2 e B2 non hanno mai avuto il riquadro del libro
            err.append(f"{rel}: riquadro del libro sparito")
        if rel not in sotto_soglia and "adsbygoogle" not in h[:h.find("</head>")]:
            err.append(f"{rel}: script AdSense sparito da una pagina sopra la soglia")
    return len(attese)


def escape_(u):
    return u.replace("&", "&amp;")


def m_main(h):
    m = re.search(r"<main[^>]*>(.*?)</main>", h, re.S)
    return m.group(1) if m else ""


def main():
    err = []
    pagine = sorted(SITO.rglob("*.html"))
    ids = {f: set(re.findall(r'\sid="([^"]+)"', f.read_text(encoding="utf-8"))) for f in pagine}
    # sitemap.xml è un indice (25/11/2026): le pagine stanno nelle sitemap di sezione elencate; lastmod vero da dati/lastmod.json
    indice = (SITO / "sitemap.xml").read_text(encoding="utf-8")
    file_sm = [u.rsplit("/", 1)[1] for u in re.findall(r"<loc>([^<]+)</loc>", indice)]
    if "<sitemapindex" not in indice or not file_sm:
        err.append("sitemap.xml: non è un indice di sitemap")
    voci = []
    for nome in file_sm:
        if nome == "sitemap-vecchi-indirizzi.xml" or not (SITO / nome).exists():
            err.append(f"sitemap.xml: {nome} non deve stare nell'indice o non esiste")
            continue
        voci += re.findall(r"<url><loc>([^<]+)</loc><lastmod>([^<]+)</lastmod></url>", (SITO / nome).read_text(encoding="utf-8"))
    sitemap = {u for u, _ in voci}
    if len(voci) != len(sitemap):
        err.append("sitemap: un indirizzo compare in più di una sitemap di sezione")
    registro = json.loads((SITO.parent / "dati" / "lastmod.json").read_text(encoding="utf-8"))["pagine"]
    for u, giorno in voci:
        if registro.get(u[len(URL):], [None])[0] != giorno or not re.fullmatch(r"20\d\d-\d\d-\d\d", giorno):
            err.append(f"sitemap: lastmod di {u} diverso dal registro dati/lastmod.json")
    robots = (SITO / "robots.txt").read_text(encoding="utf-8")
    if robots.count("Sitemap:") != 1 or f"Sitemap: {URL}sitemap.xml" not in robots:
        err.append("robots.txt: deve indicare solo sitemap.xml")
    vecchi = re.findall(r"<loc>([^<]+)</loc>", (SITO / "sitemap-vecchi-indirizzi.xml").read_text(encoding="utf-8"))
    for u in vecchi:  # vecchio host, e la pagina di oggi esiste allo stesso percorso (301 dal vecchio indirizzo, poi 200)
        perc = u[len("https://esameb1.netlify.app/"):]
        if not u.startswith("https://esameb1.netlify.app/") or not (SITO / (perc if perc.endswith(".html") else perc + "index.html")).is_file():
            err.append(f"sitemap-vecchi-indirizzi.xml: {u} non è un vecchio indirizzo con la pagina di oggi")
    if not vecchi:
        err.append("sitemap-vecchi-indirizzi.xml: vuota")
    # la home non linka pagine in noindex (25/11/2026)
    home = (SITO / "index.html").read_text(encoding="utf-8")
    for href in set(re.findall(r'<a [^>]*href="([^"#:]+/)"', home)):
        dest = SITO / href / "index.html"
        if dest.exists() and '<meta name="robots" content="noindex' in dest.read_text(encoding="utf-8"):
            err.append(f"index.html: link a una pagina in noindex: {href}")
    for f in pagine:
        if "<!--piu-usate:" in f.read_text(encoding="utf-8"):
            err.append(f"{f.relative_to(SITO)}: segnaposto «più usate» non riempito")
    n_link = n_faq = 0
    tit, des = collections.defaultdict(list), collections.defaultdict(list)
    for f in pagine:
        h = f.read_text(encoding="utf-8")
        rel = str(f.relative_to(SITO))
        head = h[:h.find("</head>")]
        for v in VERIFICHE:
            if v not in head:
                err.append(f"{rel}: manca la verifica di Search Console")
        m = re.search(r'<link rel="canonical" href="([^"]+)"', head)
        canon = URL + rel.replace("index.html", "")
        if not m or m.group(1) != canon:
            err.append(f"{rel}: canonical {m.group(1) if m else 'assente'}")
        noindex = '<meta name="robots" content="noindex' in head
        if f.name != "404.html" and noindex == (canon in sitemap):
            err.append(f"{rel}: sitemap e noindex incoerenti")
        if noindex and "adsbygoogle" in head:
            err.append(f"{rel}: AdSense in una pagina noindex")
        if h.count("<h1") != 1:
            err.append(f"{rel}: {h.count('<h1')} h1")
        visibile = testo(h)
        visibile_compatto = re.sub(r"\s+", "", visibile)  # i tag in mezzo alle frasi (link, grassetti) lasciano spazi in più
        for blocco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
            try:
                ld = json.loads(blocco)
            except ValueError:
                err.append(f"{rel}: JSON-LD non valido")
                continue
            grafo = ld.get("@graph", [ld]) if isinstance(ld, dict) else ld
            for nodo in grafo:
                if isinstance(nodo, dict) and nodo.get("@type") == "FAQPage":
                    for q in nodo["mainEntity"]:
                        n_faq += 1
                        for parte in (q["name"], q["acceptedAnswer"]["text"]):
                            if re.sub(r"\s+", "", parte) not in visibile_compatto:
                                err.append(f"{rel}: FAQ non visibile: {parte[:70]}")
        for parola in VIETATE:
            if parola in visibile:
                err.append(f"{rel}: parola «{parola.strip()}» nel testo")
        for href in re.findall(r'href="([^"]+)"', h):
            if href.startswith(("http:", "https:", "mailto:", "tel:", "data:")):
                continue
            n_link += 1
            u = urlparse(unescape(href))
            path = unquote(u.path)
            t = f if not path else ((SITO / path.lstrip("/")) if path.startswith("/") else (f.parent / path)).resolve()
            if path and (path.endswith("/") or t.is_dir()):
                t = t / "index.html"
            if not t.exists():
                if not (SITO / "netlify.toml").read_text(encoding="utf-8").count(f'from = "{path.rstrip("/")}'):
                    err.append(f"{rel}: link rotto {href}")
                continue
            if u.fragment and t.suffix == ".html" and u.fragment not in ids.get(t, set()):
                err.append(f"{rel}: ancora rotta {href}")
        if not noindex and f.name != "404.html":
            t_ = unescape(re.search(r"<title>(.*?)</title>", head, re.S).group(1))
            md = re.search(r'<meta name="description" content="([^"]*)"', head)
            d_ = unescape(md.group(1)) if md else ""
            tit[t_].append(rel)
            des[d_].append(rel)
            if len(t_) > 65 or not d_ or len(d_) > 155:
                err.append(f"{rel}: titolo {len(t_)} o description {len(d_)} fuori limite")
    doppi_t = {k: v for k, v in tit.items() if len(v) > 1 and k != "Privacy | EsameB1"}  # privacy it/en: stesso titolo, già noto
    doppi_d = {k: v for k, v in des.items() if len(v) > 1}
    for k, v in doppi_t.items():
        err.append(f"titolo doppio «{k}»: {v}")
    for k, v in doppi_d.items():
        err.append(f"description doppia «{k[:60]}»: {v}")
    n_cpia = controlli_cpia(err)
    con_script, sotto, sotto_soglia = controlli_cancello(err)
    n_schede = controlli_scuole(err, sotto_soglia)
    n_cit = controlli_citabile(err, registro, dict(voci), sotto_soglia)
    print(f"cancello della pubblicità (misura rifatta qui, soglia {SOGLIA_PAROLE_PROPRIE} parole proprie): script AdSense su {con_script} pagine, "
          f"{sotto} pagine in indice sotto la soglia senza script e senza link di affiliazione, privacy senza script, home con lo script")
    print(f"pagine CPIA controllate contro i dati: {n_cpia}")
    print(f"per le scuole: pagina, modulo «scuole», 3 eventi di clic, pulsante «Sei questa sede?» su {n_schede[0]} schede di {n_schede[1]} pagine città, fuori dall'impronta del lastmod")
    print(f"formato citabile: {n_cit} pagine (più le pagine di controllo, senza formato) con riquadro dei dati ufficiali, data = dateModified = lastmod, fonte e data in ogni riga, titoli e H1 invariati")
    print(f"pagine {len(pagine)}, in sitemap {len(sitemap)}, link interni {n_link}, domande FAQ {n_faq}, errori {len(err)}")
    for e in err[:60]:
        print("ERRORE:", e)
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
