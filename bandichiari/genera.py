#!/usr/bin/env python3
"""Genera il sito statico di BandiChiari da dati/bandi.json.

Uso:  python3 bandichiari/genera.py
Output: bandichiari/sito/ (index, schede bando, pagine per regione e per tema,
privacy, sitemap, robots). Lo stato dei bandi (aperto, in apertura, in scadenza,
chiuso) si ricalcola a ogni esecuzione in base alla data di oggi.
"""
import html
import json
import pathlib
import re
import shutil
import sys
from datetime import date

BASE = pathlib.Path(__file__).resolve().parent
SITO = BASE / "sito"
CFG = json.loads((BASE / "config.json").read_text(encoding="utf-8"))
OGGI = date.today()

REGIONI = ["Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna", "Friuli Venezia Giulia",
           "Lazio", "Liguria", "Lombardia", "Marche", "Molise", "Piemonte", "Puglia", "Sardegna",
           "Sicilia", "Toscana", "Trentino-Alto Adige", "Umbria", "Valle d'Aosta", "Veneto"]
TEMI = ["avvio attività", "macchinari", "digitale", "energia", "assunzioni", "export", "formazione",
        "ricerca e sviluppo", "sicurezza", "turismo", "agricoltura", "commercio", "liquidità"]
BENEF = ["micro", "piccole", "medie", "startup", "nuove imprese", "professionisti", "donne", "giovani", "under 35"]
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
        "settembre", "ottobre", "novembre", "dicembre"]
OBBLIGATORI = ["slug", "titolo", "ente", "regioni", "beneficiari", "finanzia", "tipo", "importo",
               "agevolazione", "stato", "sintesi", "requisiti", "cosa_preparare", "fonte_ufficiale"]

DISCLAIMER = ("BandiChiari è un servizio di informazione indipendente: non è un ente pubblico e non presenta "
              "domande per conto delle imprese. Le schede riassumono i bandi ufficiali; prima di partecipare "
              "verifica sempre il testo del bando sulla fonte ufficiale.")


def e(t):
    return html.escape(str(t), quote=True)


def slugify(t):
    t = t.lower().replace("'", "-").replace("à", "a").replace("è", "e").replace("ù", "u").replace("ì", "i").replace("ò", "o")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def data_it(s):
    d = date.fromisoformat(s)
    return f"{d.day} {MESI[d.month - 1]} {d.year}"


def mese_anno():
    return f"{MESI[OGGI.month - 1]} {OGGI.year}"


# ---------------------------------------------------------------- dati
def carica():
    bandi = json.loads((BASE / "dati/bandi.json").read_text(encoding="utf-8"))
    visti = set()
    for b in bandi:
        manca = [k for k in OBBLIGATORI if not b.get(k)]
        if manca:
            sys.exit(f"Bando {b.get('slug')}: mancano {manca}")
        if b["slug"] in visti:
            sys.exit(f"Slug duplicato: {b['slug']}")
        visti.add(b["slug"])
        b["regioni"] = ["tutte"] if "tutte" in b["regioni"] else b["regioni"]
        for r in b["regioni"]:
            if r != "tutte" and r not in REGIONI:
                sys.exit(f"Bando {b['slug']}: regione sconosciuta {r!r}")
        # stato calcolato su oggi
        sc = b.get("scadenza")
        ap = b.get("apertura")
        b["giorni"] = (date.fromisoformat(sc) - OGGI).days if sc else None
        if sc and b["giorni"] < 0:
            b["stato_ora"] = "chiuso"
        elif ap and date.fromisoformat(ap) > OGGI:
            b["stato_ora"] = "in apertura"
        else:
            b["stato_ora"] = "a sportello" if b["stato"] == "a sportello" and not sc else "aperto"
    # ordine: in scadenza prima, poi senza data, poi in apertura
    def chiave(b):
        if b["stato_ora"] == "in apertura":
            return (2, b.get("apertura") or "")
        return (0, b["scadenza"]) if b.get("scadenza") else (1, b["titolo"])
    return sorted(bandi, key=chiave)


def badge_stato(b):
    s = b["stato_ora"]
    if s == "chiuso":
        return '<span class="badge closed">Chiuso</span>'
    if s == "in apertura":
        return f'<span class="badge soon">Apre il {e(data_it(b["apertura"]))}</span>'
    if b["giorni"] is not None:
        g = b["giorni"]
        cls = "urgent" if g <= 15 else "open"
        testo = "Scade oggi" if g == 0 else f"Scade tra {g} giorni" if g <= 30 else f"Scade il {data_it(b['scadenza'])}"
        return f'<span class="badge {cls}">{e(testo)}</span>'
    return '<span class="badge open">Aperto a sportello</span>'


def card(b):
    reg = "Tutta Italia" if b["regioni"] == ["tutte"] else ", ".join(b["regioni"]) if len(b["regioni"]) <= 3 else f'{len(b["regioni"])} regioni'
    return (f'<a class="card" href="/bandi/{b["slug"]}/" data-regioni="{e("|".join(b["regioni"]))}" '
            f'data-finanzia="{e("|".join(b["finanzia"]))}" data-benef="{e("|".join(b["beneficiari"]))}">'
            f'<h3>{e(b["titolo"])}</h3><span class="ente">{e(b["ente"])} · {e(reg)}</span>'
            f'<span class="agev">{e(b["agevolazione"])} · {e(b["importo"])}</span>'
            f'<span class="foot">{badge_stato(b)}<span class="badge gold">{e(b["tipo"])}</span></span></a>')


# ---------------------------------------------------------------- layout
def pagina(titolo, descrizione, percorso, corpo, ld=None, noindex=False):
    url = CFG["sito"] + percorso
    ldj = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n' if ld else ""
    robots = '<meta name="robots" content="noindex" />\n' if noindex else ""
    return f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{e(titolo)}</title>
<meta name="description" content="{e(descrizione)}" />
<link rel="canonical" href="{url}" />
{robots}<meta property="og:type" content="website" />
<meta property="og:title" content="{e(titolo)}" />
<meta property="og:description" content="{e(descrizione)}" />
<meta property="og:url" content="{url}" />
<meta property="og:locale" content="it_IT" />
<meta name="theme-color" content="#F7F5EF" />
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%230F5C3E'/%3E%3Ctext x='16' y='22' font-family='Georgia' font-size='18' font-weight='700' fill='white' text-anchor='middle'%3EB%3C/text%3E%3C/svg%3E" />
<link rel="stylesheet" href="/assets/style.css" />
{ldj}</head>
<body>
<header class="nav"><div class="wrap">
  <a class="logo" href="/"><span class="mk" aria-hidden="true">B</span>BandiChiari</a>
  <nav class="nav-links" aria-label="Principale">
    <a href="/#cerca">Cerca bandi</a><a href="/#prezzi">Prezzi</a>
    <a class="btn btn-primary btn-sm" href="/#iscriviti">Ricevili ogni settimana</a>
  </nav>
</div></header>
<main>
{corpo}
</main>
<footer class="footer"><div class="wrap">
  <div class="cols">
    <div><a class="logo" href="/"><span class="mk" aria-hidden="true">B</span>BandiChiari</a>
      <p>{e(DISCLAIMER)}</p></div>
    <div><p><a href="/#cerca">Cerca bandi</a><br><a href="/regioni/">Bandi per regione</a><br><a href="/temi/">Bandi per tema</a><br><a href="/privacy.html">Privacy e condizioni</a></p></div>
  </div>
  <p>© {OGGI.year} BandiChiari · Ultimo aggiornamento: {e(data_it(OGGI.isoformat()))}</p>
</div></footer>
<script src="/assets/app.js" defer></script>
</body>
</html>
"""


def filtri(regione_fissa=None, tema_fisso=None):
    opt_r = "".join(f'<option{" selected" if r == regione_fissa else ""}>{e(r)}</option>' for r in REGIONI)
    opt_t = "".join(f'<option value="{e(t)}"{" selected" if t == tema_fisso else ""}>{e(t.capitalize())}</option>' for t in TEMI)
    opt_b = "".join(f'<option value="{e(b)}">{e(b.capitalize())}</option>' for b in BENEF)
    return f"""<div class="filters">
      <label class="field"><span>La tua regione</span><select name="f-regione"><option value="">Tutte le regioni</option>{opt_r}</select></label>
      <label class="field"><span>Cosa vuoi finanziare</span><select name="f-finanzia"><option value="">Qualsiasi cosa</option>{opt_t}</select></label>
      <label class="field"><span>La tua impresa</span><select name="f-benef"><option value="">Qualsiasi impresa</option>{opt_b}</select></label>
      <a class="btn btn-ghost" href="/#iscriviti">Avvisami dei nuovi</a>
    </div>"""


def finder(bandi, regione_fissa=None, tema_fisso=None):
    aperti = [b for b in bandi if b["stato_ora"] != "chiuso"]
    fisso = " data-fisso" if (regione_fissa or tema_fisso) else ""
    return f"""<div class="finder" data-finder{fisso}>
    {filtri(regione_fissa, tema_fisso)}
    <p class="count" data-count><b>{len(aperti)}</b> bandi aperti o in apertura.</p>
    <div class="results">
      {"".join(card(b) for b in aperti)}
      <p class="empty" data-empty hidden>Nessun bando aperto con questi filtri in questo momento. <a href="/#iscriviti">Iscriviti</a>: ti avvisiamo appena ne esce uno.</p>
    </div>
  </div>"""


def cta_box(regione=None):
    q = f"?regione={e(regione)}" if regione else ""
    dove = f" in {e(regione)}" if regione else ""
    return f"""<div class="cta-box">
      <h2>Non perdere il prossimo bando{dove}.</h2>
      <p>Ogni settimana leggiamo i nuovi bandi e ti mandiamo solo quelli adatti alla tua impresa, spiegati chiari, con la scadenza in evidenza.</p>
      <a class="btn btn-primary" href="/{q}#iscriviti">Ricevili ogni settimana</a>
    </div>"""


# ---------------------------------------------------------------- pagine
def home(bandi):
    n_aperti = sum(1 for b in bandi if b["stato_ora"] != "chiuso")
    m, a = CFG["prezzo_mensile"], CFG["prezzo_annuale"]
    opt_r = "".join(f"<option>{e(r)}</option>" for r in REGIONI)
    checks = "".join(f'<label><input type="checkbox" name="finanzia" value="{e(t)}"> {e(t.capitalize())}</label>' for t in TEMI)
    regioni_chips = "".join(f'<a href="/regioni/{slugify(r)}/">{e(r)}</a>' for r in REGIONI)
    temi_chips = "".join(f'<a href="/temi/{slugify(t)}/">{e(t.capitalize())}</a>' for t in TEMI
                         if any(t in b["finanzia"] for b in bandi))
    faq = [
        ("Presentate voi la domanda per il bando?", "No. BandiChiari ti dice quali bandi fanno per te, quanto puoi ottenere, i requisiti e cosa preparare. La domanda la presenti tu o il tuo commercialista o consulente, che potrà partire già sapendo cosa serve."),
        ("Da dove prendete le informazioni?", "Dalle fonti ufficiali: ministeri, Invitalia, regioni, Camere di commercio e il portale nazionale degli incentivi. Ogni scheda riporta il link alla fonte ufficiale e la data dell'ultima verifica."),
        ("Ogni quanto aggiornate?", "Ogni settimana cerchiamo i bandi nuovi e ricontrolliamo date e stato di quelli già pubblicati. Gli iscritti ricevono il riepilogo per email."),
        ("Posso disdire quando voglio?", f"Sì. L'abbonamento mensile si disdice in qualsiasi momento e non si rinnova più; l'annuale vale 12 mesi. La newsletter gratuita si annulla con un clic."),
        ("Quanto costa?", f"La ricerca sul sito e la newsletter settimanale per regione sono gratis. Il servizio su misura costa {m} € al mese oppure {a} € l'anno."),
    ]
    faq_html = "".join(f"<details><summary>{e(q)}</summary><p>{e(r)}</p></details>" for q, r in faq)
    stripe_m = e(CFG.get("stripe_link_mensile") or "")
    stripe_a = e(CFG.get("stripe_link_annuale") or "")
    corpo = f"""
<section class="hero"><div class="wrap">
  <span class="kicker">Bandi e contributi per le imprese · {e(mese_anno())}</span>
  <h1>I bandi giusti per la tua impresa,<br>spiegati chiari.</h1>
  <p class="lead">Leggiamo ogni settimana i bandi nazionali e regionali e ti diciamo, in parole semplici, quali fanno per te: quanto puoi ottenere, chi può partecipare, cosa preparare e quando scadono.</p>
  <div class="hero-cta"><a class="btn btn-primary" href="#cerca">Cerca i bandi per te</a><a class="btn btn-ghost" href="#iscriviti">Ricevili ogni settimana</a></div>
  <div class="hero-facts"><span><b>{n_aperti}</b> bandi aperti o in apertura</span><span><b>20</b> regioni coperte</span><span>Aggiornato il <b>{e(data_it(OGGI.isoformat()))}</b></span></div>
</div></section>

<section class="section" id="cerca" style="padding-top:0"><div class="wrap">
  {finder(bandi)}
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head center"><span class="kicker">Come funziona</span><h2>Meno tempo a cercare, più tempo per la domanda.</h2></div>
  <div class="steps">
    <div class="step"><span class="n">1</span><h3>Ci dici chi sei</h3><p>Regione, dimensione, settore e cosa vuoi finanziare: macchinari, digitale, energia, assunzioni, una nuova attività.</p></div>
    <div class="step"><span class="n">2</span><h3>Noi leggiamo i bandi</h3><p>Ogni settimana controlliamo le fonti ufficiali e scartiamo quelli che non fanno per te.</p></div>
    <div class="step"><span class="n">3</span><h3>Tu ricevi solo i tuoi</h3><p>Un'email con i bandi adatti, spiegati in due righe, con importi, requisiti, documenti e scadenza.</p></div>
  </div>
</div></section>

<section class="section" id="prezzi"><div class="wrap">
  <div class="section-head center"><span class="kicker">Prezzi</span><h2>Un bando trovato vale molto più dell'abbonamento.</h2>
    <p class="lead">Un contributo a fondo perduto vale spesso migliaia di euro. Saperlo in tempo è la parte che conta.</p></div>
  <div class="plans">
    <div class="plan"><h3>Gratis</h3><div class="price">0 €</div><div class="sub">per sempre</div>
      <ul><li>Ricerca su tutti i bandi del sito</li><li>Schede spiegate in parole semplici</li><li>Email settimanale con i nuovi bandi della tua regione</li></ul>
      <a class="btn btn-ghost btn-block" href="#iscriviti" data-scegli-piano="gratis">Iscriviti gratis</a></div>
    <div class="plan"><h3>Su misura</h3><div class="price">{m} €<small> / mese</small></div><div class="sub">disdici quando vuoi</div>
      <ul><li>Solo i bandi adatti al tuo profilo</li><li>Avviso 15 giorni prima di ogni scadenza</li><li>Lista dei documenti da preparare per ogni bando</li><li>Risposta via email alle tue domande sui bandi</li></ul>
      <a class="btn btn-primary btn-block" href="#iscriviti" data-scegli-piano="mensile">Attiva su misura</a></div>
    <div class="plan top"><h3>Su misura annuale</h3><div class="price">{a} €<small> / anno</small></div><div class="sub">{round(a / 12, 2):.2f} € al mese, risparmi {m * 12 - a} €</div>
      <ul><li>Tutto il piano Su misura</li><li>12 mesi di bandi selezionati</li><li>Un solo pagamento</li></ul>
      <a class="btn btn-primary btn-block" href="#iscriviti" data-scegli-piano="annuale">Attiva l'annuale</a></div>
  </div>
  <p style="text-align:center;color:var(--ink-3);font-size:.9rem;margin-top:1rem">Prezzi IVA inclusa. Pagamento sicuro con Stripe.</p>
</div></section>

<section class="section" id="iscriviti"><div class="wrap narrow">
  <div class="section-head center"><span class="kicker">Iscrizione</span><h2>Dicci chi sei, al resto pensiamo noi.</h2></div>
  <div class="form-box" data-form-box>
    <div data-step="form">
    <form class="form" name="iscrizione" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field" data-stripe-mensile="{stripe_m}" data-stripe-annuale="{stripe_a}">
      <input type="hidden" name="form-name" value="iscrizione">
      <p class="hp"><label>Non compilare <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
      <label class="field"><span>Email</span><input type="email" name="email" required autocomplete="email"></label>
      <label class="field"><span>Nome</span><input type="text" name="nome" required autocomplete="given-name"></label>
      <label class="field"><span>Regione della sede</span><select name="regione" required><option value="">Scegli…</option>{opt_r}</select></label>
      <label class="field"><span>Dimensione</span><select name="dimensione" required><option value="">Scegli…</option><option>Devo ancora aprire</option><option>Libero professionista</option><option>Micro (fino a 9 addetti)</option><option>Piccola (10–49)</option><option>Media (50–249)</option></select></label>
      <label class="field full"><span>Settore e attività</span><input type="text" name="attivita" required placeholder="Es. ristorante, officina meccanica, studio di grafica…"></label>
      <div class="field full"><span>Cosa vorresti finanziare</span><div class="checks">{checks}</div></div>
      <div class="field full"><span>Piano</span><div class="checks">
        <label><input type="radio" name="piano" value="gratis" checked> Gratis</label>
        <label><input type="radio" name="piano" value="mensile"> Su misura {m} €/mese</label>
        <label><input type="radio" name="piano" value="annuale"> Su misura {a} €/anno</label></div></div>
      <label class="consent full"><input type="checkbox" name="privacy" value="accettata" required><span>Ho letto l'<a href="/privacy.html" target="_blank">informativa privacy e le condizioni</a> e voglio ricevere le email di BandiChiari. Posso annullare in qualsiasi momento.</span></label>
      <div class="full"><button class="btn btn-primary btn-block" type="submit">Iscriviti</button>
        <p data-errore hidden style="color:var(--red);text-align:center;margin:.6rem 0 0">Invio non riuscito: controlla la connessione e riprova.</p>
        <p style="text-align:center;color:var(--ink-3);font-size:.85rem;margin:.6rem 0 0">Con i piani Su misura passi al pagamento sicuro con Stripe.</p></div>
    </form>
    </div>
    <div class="done" data-step="ok" hidden><h3>Iscrizione ricevuta.</h3><p>Grazie! La prima email arriva con il prossimo aggiornamento settimanale.</p></div>
  </div>
</div></section>

<section class="section"><div class="wrap narrow">
  <div class="section-head center"><span class="kicker">Domande frequenti</span><h2>Prima di iscriverti.</h2></div>
  <div class="faq">{faq_html}</div>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head"><span class="kicker">Bandi per regione</span></div><div class="chips">{regioni_chips}</div>
  <div class="section-head" style="margin-top:2rem"><span class="kicker">Bandi per tema</span></div><div class="chips">{temi_chips}</div>
</div></section>
"""
    ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "BandiChiari", "url": CFG["sito"] + "/",
          "inLanguage": "it"}
    return pagina(f"Bandi e contributi per imprese {OGGI.year}, spiegati chiari | BandiChiari",
                  "Tutti i bandi e contributi aperti per imprese e professionisti, nazionali e regionali, "
                  "spiegati in parole semplici: importi, requisiti, documenti e scadenze. Aggiornato ogni settimana.",
                  "/", corpo, ld)


def scheda(b):
    reg = "Tutta Italia" if b["regioni"] == ["tutte"] else ", ".join(b["regioni"])
    regione_link = None if b["regioni"] == ["tutte"] else b["regioni"][0]
    righe = [("Agevolazione", b["agevolazione"]), ("Importo", b["importo"]), ("Tipo", b["tipo"]),
             ("Ente", b["ente"]), ("Dove", reg),
             ("Apertura", data_it(b["apertura"]) if b.get("apertura") else "—"),
             ("Scadenza", data_it(b["scadenza"]) if b.get("scadenza") else "A sportello, fino a esaurimento fondi"),
             ("Per chi", ", ".join(b["beneficiari"]))]
    facts = "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in righe)
    avviso = ""
    if b["stato_ora"] == "chiuso":
        avviso = '<div class="alert closed"><b>Questo bando è chiuso.</b> Iscriviti per sapere quando esce la prossima edizione o un bando simile.</div>'
    elif b.get("affidabilita") == "media":
        avviso = '<div class="alert warn">Alcuni dettagli di questo bando potrebbero cambiare: controlla la fonte ufficiale prima di presentare la domanda.</div>'
    temi = "".join(f'<a href="/temi/{slugify(t)}/">{e(t.capitalize())}</a>' for t in b["finanzia"] if t in TEMI)
    corpo = f"""
<section class="section"><div class="wrap narrow doc">
  <div class="crumbs"><a href="/">BandiChiari</a> › {f'<a href="/regioni/{slugify(regione_link)}/">{e(regione_link)}</a>' if regione_link else '<a href="/#cerca">Bandi nazionali</a>'} › {e(b['titolo'])}</div>
  <div>{badge_stato(b)} <span class="badge gold">{e(b['tipo'])}</span></div>
  <h1>{e(b['titolo'])}</h1>
  <p class="lead">{e(b['sintesi'])}</p>
  {avviso}
  <dl class="facts">{facts}</dl>
  <h2>Chi può partecipare</h2>
  <ul>{"".join(f"<li>{e(x)}</li>" for x in b['requisiti'])}</ul>
  <h2>Cosa preparare</h2>
  <ul>{"".join(f"<li>{e(x)}</li>" for x in b['cosa_preparare'])}</ul>
  <h2>Fonte ufficiale</h2>
  <p><a href="{e(b['fonte_ufficiale'])}" rel="noopener" target="_blank">{e(b['fonte_ufficiale'])}</a><br>
  <small>Ultima verifica: {e(data_it(b.get('ultima_verifica') or OGGI.isoformat()))}. {e(DISCLAIMER)}</small></p>
  {f'<h2>Temi</h2><div class="chips">{temi}</div>' if temi else ''}
  {cta_box(regione_link)}
</div></section>
"""
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "BandiChiari", "item": CFG["sito"] + "/"},
        {"@type": "ListItem", "position": 2, "name": b["titolo"], "item": f"{CFG['sito']}/bandi/{b['slug']}/"}]}
    desc = f"{b['titolo']}: {b['agevolazione']}, {b['importo']}. Requisiti, documenti e scadenza spiegati in parole semplici."
    return pagina(f"{b['titolo']} {OGGI.year}: requisiti, importi e scadenza | BandiChiari", desc[:300],
                  f"/bandi/{b['slug']}/", corpo, ld)


def indice_regione(bandi, regione):
    pertinenti = [b for b in bandi if b["regioni"] == ["tutte"] or regione in b["regioni"]]
    regionali = sum(1 for b in pertinenti if b["regioni"] != ["tutte"] and b["stato_ora"] != "chiuso")
    corpo = f"""
<section class="hero"><div class="wrap">
  <div class="crumbs"><a href="/">BandiChiari</a> › <a href="/regioni/">Regioni</a> › {e(regione)}</div>
  <span class="kicker">Aggiornato a {e(mese_anno())}</span>
  <h1>Bandi per imprese in {e(regione)}</h1>
  <p class="lead">I contributi aperti per chi ha un'impresa o un'attività in {e(regione)}: {regionali} bandi regionali e locali più quelli nazionali, spiegati in parole semplici.</p>
</div></section>
<section class="section" style="padding-top:0"><div class="wrap">
  {finder(pertinenti, regione_fissa=regione)}
  {cta_box(regione)}
</div></section>"""
    return pagina(f"Bandi per imprese in {regione} {OGGI.year}: contributi aperti | BandiChiari",
                  f"Bandi e contributi aperti per imprese in {regione} a {mese_anno()}: fondo perduto, finanziamenti "
                  "agevolati e crediti d'imposta, con importi, requisiti e scadenze.",
                  f"/regioni/{slugify(regione)}/", corpo)


def indice_tema(bandi, tema):
    pertinenti = [b for b in bandi if tema in b["finanzia"]]
    corpo = f"""
<section class="hero"><div class="wrap">
  <div class="crumbs"><a href="/">BandiChiari</a> › <a href="/temi/">Temi</a> › {e(tema.capitalize())}</div>
  <span class="kicker">Aggiornato a {e(mese_anno())}</span>
  <h1>Bandi per {e(tema)}</h1>
  <p class="lead">I bandi e contributi aperti che finanziano {e(tema)}, nazionali e regionali. Scegli la tua regione per vedere solo quelli validi per te.</p>
</div></section>
<section class="section" style="padding-top:0"><div class="wrap">
  {finder(pertinenti, tema_fisso=tema)}
  {cta_box()}
</div></section>"""
    return pagina(f"Bandi per {tema} {OGGI.year}: contributi per imprese | BandiChiari",
                  f"Bandi e contributi aperti per {tema} a {mese_anno()}: importi, requisiti e scadenze spiegati chiari.",
                  f"/temi/{slugify(tema)}/", corpo)


def elenco(titolo, percorso, voci, base):
    chips = "".join(f'<a href="/{base}/{slugify(v)}/">{e(v.capitalize() if base == "temi" else v)}</a>' for v in voci)
    corpo = f"""<section class="hero"><div class="wrap"><div class="crumbs"><a href="/">BandiChiari</a> › {e(titolo)}</div>
  <h1>{e(titolo)}</h1><div class="chips" style="margin-top:1.5rem">{chips}</div></div></section>"""
    return pagina(f"{titolo} | BandiChiari", f"{titolo}: tutti i bandi aperti per imprese, aggiornati ogni settimana.",
                  percorso, corpo)


def privacy():
    corpo = f"""<section class="section"><div class="wrap narrow doc">
  <h1>Privacy e condizioni</h1>
  <p class="lead">Ultimo aggiornamento: {e(mese_anno())}.</p>
  <h2>Chi tratta i dati</h2>
  <p>Titolare del trattamento è {e(CFG['titolare'])}, che gestisce BandiChiari. Per qualsiasi richiesta sui tuoi dati rispondi a una delle nostre email{(' o scrivi a <a href="mailto:' + e(CFG['email']) + '">' + e(CFG['email']) + '</a>') if CFG.get('email') else ''}.</p>
  <h2>Quali dati e perché</h2>
  <ul>
    <li><b>Iscrizione:</b> email, nome, regione, dimensione, attività, temi di interesse e piano scelto. Servono a selezionare e inviarti i bandi adatti (base giuridica: il servizio che richiedi, art. 6.1.b GDPR, e il tuo consenso alle email, art. 6.1.a).</li>
    <li><b>Pagamenti:</b> gestiti da Stripe. Non vediamo né conserviamo i dati della tua carta.</li>
  </ul>
  <p>Non vendiamo i dati e non li cediamo a terzi per pubblicità.</p>
  <h2>Fornitori</h2>
  <p>Netlify (hosting e ricezione dei moduli), Stripe (pagamenti), Google (invio delle email). Alcuni possono trattare dati fuori dall'UE con le garanzie previste dal GDPR.</p>
  <h2>Per quanto tempo</h2>
  <p>Finché resti iscritto. Se annulli l'iscrizione cancelliamo i tuoi dati entro 30 giorni, salvo quelli che la legge ci obbliga a conservare per i pagamenti.</p>
  <h2>I tuoi diritti</h2>
  <p>Accesso, rettifica, cancellazione, limitazione, portabilità e opposizione (artt. 15–22 GDPR). Puoi anche presentare reclamo al <a href="https://www.garanteprivacy.it" rel="noopener">Garante per la protezione dei dati personali</a>. Il sito non usa cookie di profilazione né strumenti di analisi.</p>
  <h2>Condizioni del servizio</h2>
  <ul>
    <li>{e(DISCLAIMER)}</li>
    <li>Non garantiamo che un bando sia adatto o che la domanda venga accolta: la valutazione finale spetta a te e all'ente che gestisce il bando.</li>
    <li>Il piano mensile si rinnova ogni mese e si disdice quando vuoi; il piano annuale copre 12 mesi. La disdetta ferma i rinnovi successivi.</li>
  </ul>
</div></section>"""
    return pagina("Privacy e condizioni | BandiChiari", "Informativa privacy e condizioni del servizio BandiChiari.",
                  "/privacy.html", corpo, noindex=True)


def scrivi(rel, testo):
    p = SITO / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(testo, encoding="utf-8")


def main():
    bandi = carica()
    for cartella in ("bandi", "regioni", "temi"):
        shutil.rmtree(SITO / cartella, ignore_errors=True)
    scrivi("index.html", home(bandi))
    for b in bandi:
        scrivi(f"bandi/{b['slug']}/index.html", scheda(b))
    for r in REGIONI:
        scrivi(f"regioni/{slugify(r)}/index.html", indice_regione(bandi, r))
    temi_usati = [t for t in TEMI if any(t in b["finanzia"] for b in bandi)]
    for t in temi_usati:
        scrivi(f"temi/{slugify(t)}/index.html", indice_tema(bandi, t))
    scrivi("regioni/index.html", elenco("Bandi per regione", "/regioni/", REGIONI, "regioni"))
    scrivi("temi/index.html", elenco("Bandi per tema", "/temi/", temi_usati, "temi"))
    scrivi("privacy.html", privacy())
    urls = (["/", "/regioni/", "/temi/"] + [f"/bandi/{b['slug']}/" for b in bandi]
            + [f"/regioni/{slugify(r)}/" for r in REGIONI] + [f"/temi/{slugify(t)}/" for t in temi_usati])
    scrivi("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "".join(f"  <url><loc>{CFG['sito']}{u}</loc><lastmod>{OGGI.isoformat()}</lastmod></url>\n" for u in urls)
           + "</urlset>\n")
    scrivi("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {CFG['sito']}/sitemap.xml\n")
    aperti = sum(1 for b in bandi if b["stato_ora"] != "chiuso")
    print(f"{len(bandi)} bandi ({aperti} aperti o in apertura), {len(urls)} pagine")


if __name__ == "__main__":
    main()
