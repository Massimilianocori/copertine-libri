#!/usr/bin/env python3
"""Genera le pagine per settore di Rispondoio e i file SEO.

Uso (dalla radice del repo):
    python3 strumenti/genera_pagine.py

Produce:
    assets/rispondoio.css      stile della homepage (estratto da index.html)
    per/index.html             indice dei settori
    per/<slug>/index.html      una pagina per ogni settore in strumenti/settori.py
    sitemap.xml, robots.txt

index.html resta la fonte unica: modulo di attivazione, calcolatore, logo e
favicon vengono copiati da lì. Dopo aver modificato index.html o settori.py,
rilancia lo script.
"""
import html
import json
import pathlib
import re
import sys
from datetime import date

RADICE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RADICE / "strumenti"))
from settori import FAQ_COMUNI, SETTORI  # noqa: E402

# Dominio pubblico del sito (canonical e sitemap). Cambialo se usi un altro dominio.
SITO = "https://rispondoio.net"

PIANI = [  # canone mensile trimestrale / annuale, minuti inclusi (come in index.html)
    ("Basic", 79, 67, "200 minuti al mese", False),
    ("Standard", 129, 109, "500 minuti al mese", False),
    ("Pro", 229, 189, "1.000 minuti al mese", True),
]

CHECK = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>')


def e(testo):
    return html.escape(testo, quote=True)


def blocco(sorgente, inizio, fine):
    m = re.search(re.escape(inizio) + r".*?" + re.escape(fine), sorgente, re.S)
    if not m:
        sys.exit(f"Blocco {inizio} non trovato in index.html")
    return m.group(0)


def icona(path):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round">{path}</svg>')


def main():
    index = (RADICE / "index.html").read_text(encoding="utf-8")

    # 1. CSS della homepage → file condiviso (font incorporati compresi)
    css = re.search(r"<style>(.*?)</style>", index, re.S).group(1)
    (RADICE / "assets").mkdir(exist_ok=True)
    (RADICE / "assets/rispondoio.css").write_text(
        "/* GENERATO da strumenti/genera_pagine.py a partire da index.html: non modificare a mano. */\n"
        + css.strip() + "\n", encoding="utf-8")

    favicon = re.search(r'<link rel="icon"[^>]*>', index).group(0)
    logo = re.search(r'<span class="mark" aria-hidden="true">.*?</span>', index, re.S).group(0)

    # Modulo di attivazione: lo stesso della homepage. Netlify registra il form da
    # index.html; qui niente data-netlify (il nome del form deve essere unico),
    # l'invio AJAX usa il campo nascosto form-name.
    modulo = blocco(index, "<!-- LEAD-MODAL:START -->", "<!-- LEAD-MODAL:END -->")
    modulo = modulo.replace(' data-netlify="true"', "").replace(' netlify-honeypot="bot-field"', "")
    calcolatore = blocco(index, "<!-- ROI:START -->", "<!-- ROI:END -->")

    def pagina(rel, titolo, descrizione, url, corpo, settore_form="", jsonld=None):
        """rel = prefisso per tornare alla radice (es. '../../')."""
        mod = modulo.replace('href="privacy.html"', f'href="{rel}privacy.html"')
        ld = ""
        if jsonld:
            ld = ('<script type="application/ld+json">'
                  + json.dumps(jsonld, ensure_ascii=False) + "</script>\n")
        return f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{e(titolo)}</title>
<meta name="description" content="{e(descrizione)}" />
<link rel="canonical" href="{url}" />
<meta name="theme-color" content="#F5F7FB" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{e(titolo)}" />
<meta property="og:description" content="{e(descrizione)}" />
<meta property="og:url" content="{url}" />
<meta property="og:locale" content="it_IT" />
{favicon}
<link rel="stylesheet" href="{rel}assets/rispondoio.css" />
<link rel="stylesheet" href="{rel}assets/rispondoio-lead.css" />
<link rel="stylesheet" href="{rel}assets/rispondoio-settori.css" />
{ld}</head>
<body data-settore="{e(settore_form)}">
<!-- GENERATO da strumenti/genera_pagine.py: modifica strumenti/settori.py e rilancia lo script. -->
<header class="nav" id="nav">
  <div class="container nav-inner">
    <a href="{rel}" class="brand" aria-label="Rispondoio — home">
      {logo}
      Rispondoio
    </a>
    <nav class="nav-links" aria-label="Principale">
      <a href="{rel}per/">Settori</a>
      <a href="{rel}#come-funziona">Come funziona</a>
      <a href="#calcolatore">Calcolatore</a>
      <a href="{rel}#prezzi">Prezzi</a>
    </nav>
    <button type="button" class="btn btn-primary js-lead" data-plan="Da decidere insieme" data-origine="nav" style="padding:.75rem 1.2rem">Attiva</button>
  </div>
</header>
<main>
{corpo}
</main>
<footer class="footer">
  <div class="container">
    <div class="footer-top">
      <div>
        <a href="{rel}" class="brand">{logo} Rispondoio</a>
        <p class="footer-blurb">L'assistente vocale AI che risponde al telefono della tua attività, capisce e prenota — 24 ore su 24.</p>
      </div>
      <div class="footer-links">
        <div class="footer-col"><h4>Prodotto</h4><a href="{rel}#come-funziona">Come funziona</a><a href="{rel}#prezzi">Prezzi</a><a href="{rel}per/">Settori</a></div>
        <div class="footer-col"><h4>Info</h4><a href="mailto:io@rispondoio.net">io@rispondoio.net</a><a href="{rel}privacy.html">Privacy</a></div>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© {date.today().year} Rispondoio. Tutti i diritti riservati.</span>
      <span class="vat">Prezzi IVA esclusa</span>
    </div>
  </div>
</footer>
{mod}
<script src="{rel}assets/rispondoio-lead.js" defer></script>
</body>
</html>
"""

    altri_link = lambda corrente: "".join(  # noqa: E731
        f'<a href="../{s["slug"]}/">{e(s["nome"])}</a>' for s in SETTORI if s["slug"] != corrente)

    # 2. Una pagina per settore
    for s in SETTORI:
        url = f"{SITO}/per/{s['slug']}/"
        perse, conv, valore = s["roi"]
        roi = calcolatore.replace(
            'data-perse="10" data-conv="40" data-valore="60"',
            f'data-perse="{perse}" data-conv="{conv}" data-valore="{valore}"')
        roi = roi.replace(
            "Sposta i cursori con i numeri della tua attività",
            f"Valori di esempio per {e(s['chi'])}: mettici i tuoi numeri")
        roi = roi.replace('class="section-head center reveal"', 'class="section-head center"').replace(
            'class="roi reveal"', 'class="roi"')

        dialogo = "\n".join(
            f'          <div class="dlg-line {chi}"><b>{"Cliente" if chi == "c" else "Rispondoio"}</b>{e(t)}</div>'
            for chi, t in s["dialogo"])
        problemi = "\n".join(
            f'      <div class="pain"><span class="n">0{i}</span><h3>{e(t)}</h3><p>{e(d)}</p></div>'
            for i, (t, d) in enumerate(s["problemi"], 1))
        fa = "\n".join(f"      <li>{CHECK}<span>{e(x)}</span></li>" for x in s["fa"])
        piani = "\n".join(
            f'''      <div class="mini-plan{' featured' if top else ''}">
        <h3>{nome}</h3>
        <div class="price">€ {tri}<small> / mese</small></div>
        <div class="meta">{minuti} · oppure € {ann}/mese con l'annuale</div>
        <button type="button" class="btn {'btn-primary' if top else 'btn-ghost'} btn-block js-lead" data-plan="{nome}" data-origine="prezzi settore">Inizia con {nome}</button>
      </div>''' for nome, tri, ann, minuti, top in PIANI)
        faq_tutte = s["faq"] + FAQ_COMUNI
        faq = "\n".join(
            f"      <details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in faq_tutte)

        corpo = f"""
<section class="sx-hero">
  <div class="container sx-grid">
    <div>
      <div class="sx-crumbs"><a href="../../">Rispondoio</a> › <a href="../">Settori</a> › {e(s['nome'])}</div>
      <span class="kicker">Rispondoio per {e(s['chi'])}</span>
      <h1 class="display"><span class="grad">{e(s['h1'])}</span></h1>
      <p class="lead">{e(s['lead'])}</p>
      <div class="hero-cta">
        <button type="button" class="btn btn-primary btn-lg js-lead" data-plan="Da decidere insieme" data-origine="hero">Richiedi l'attivazione</button>
        <a class="btn btn-ghost btn-lg" href="../../#top">Prova la demo vocale</a>
      </div>
      <div class="hero-trust"><span class="live">Attivo 24/7</span><span>· configurato da noi · assistenza umana</span></div>
    </div>
    <div class="dlg" aria-label="Esempio di chiamata">
      <div class="dlg-head"><b>Esempio di chiamata</b><span>{e(s['nome'])}</span></div>
      <div class="dlg-list">
{dialogo}
      </div>
      <div class="cc-confirm"><span class="ico" aria-hidden="true">{CHECK}</span><div><b>Appuntamento in agenda</b><span>Email di notifica inviata al titolare</span></div></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head center">
      <span class="kicker">Il problema</span>
      <h2 class="display"><span class="grad">Ogni chiamata persa è un cliente che va altrove.</span></h2>
    </div>
    <div class="pain-grid">
{problemi}
    </div>
  </div>
</section>

<section class="section" style="background:var(--surface);border-block:1px solid var(--border)">
  <div class="container">
    <div class="section-head center">
      <span class="kicker">Cosa fa per te</span>
      <h2 class="display"><span class="grad">Risponde, capisce, prenota.</span></h2>
      <p class="lead">Lo scriviamo sulla tua attività: servizi, orari, prezzi e regole sono quelli che ci dai tu.</p>
    </div>
    <ul class="does">
{fa}
    </ul>
  </div>
</section>

{roi}

<section class="section" id="prezzi">
  <div class="container">
    <div class="section-head center">
      <span class="kicker">Prezzi</span>
      <h2 class="display"><span class="grad">Un piano per ogni volume di chiamate.</span></h2>
    </div>
    <div class="mini-plans">
{piani}
    </div>
    <p class="mini-fine">Prezzi IVA esclusa, piano trimestrale. Attivazione € 149 una tantum (gratuita su Standard e Pro con l'annuale). Minuti extra: 100 a € 25. <a href="../../#prezzi">Tutti i dettagli</a></p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head center">
      <span class="kicker">Domande frequenti</span>
      <h2 class="display"><span class="grad">Quello che ci chiedono di più.</span></h2>
    </div>
    <div class="faq">
{faq}
    </div>
  </div>
</section>

<section class="section final-cta">
  <div class="container">
    <div class="inner">
      <h2 class="display"><span class="grad">Il telefono squilla. Rispondoio risponde.</span></h2>
      <p>Lasciaci i dati della tua attività: prepariamo l'assistente e te lo facciamo provare prima di partire.</p>
      <div class="hero-cta"><button type="button" class="btn btn-light btn-lg js-lead" data-plan="Da decidere insieme" data-origine="cta finale">Richiedi l'attivazione</button></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container" style="text-align:center">
    <span class="kicker">Altri settori</span>
    <div class="others">{altri_link(s['slug'])}</div>
  </div>
</section>
"""
        jsonld = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Service",
                    "name": f"Rispondoio — {s['titolo']}",
                    "serviceType": "Assistente vocale AI per la gestione delle chiamate",
                    "description": s["descrizione"],
                    "areaServed": {"@type": "Country", "name": "Italia"},
                    "audience": {"@type": "BusinessAudience", "name": s["nome"]},
                    "provider": {"@type": "Organization", "name": "Rispondoio", "url": SITO + "/",
                                 "email": "io@rispondoio.net"},
                    "offers": [{"@type": "Offer", "name": n, "price": str(p), "priceCurrency": "EUR",
                                "description": f"{m}, canone mensile IVA esclusa"} for n, p, _, m, _ in PIANI],
                },
                {
                    "@type": "FAQPage",
                    "mainEntity": [{"@type": "Question", "name": q,
                                    "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq_tutte],
                },
            ],
        }
        dest = RADICE / "per" / s["slug"] / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(pagina("../../", f"{s['titolo']} | Rispondoio", s["descrizione"], url,
                               corpo, s["form"], jsonld), encoding="utf-8")

    # 3. Indice dei settori
    carte = "\n".join(f'''      <a class="hub-card" href="{s['slug']}/">
        <span class="ico" aria-hidden="true">{icona(s['icona'])}</span>
        <b>{e(s['nome'])}</b>
        <p>{e(s['h1'])}</p>
        <span class="sector-go">Scopri come &rarr;</span>
      </a>''' for s in SETTORI)
    corpo_hub = f"""
<section class="sx-hero">
  <div class="container">
    <div class="section-head center">
      <div class="sx-crumbs"><a href="../">Rispondoio</a> › Settori</div>
      <span class="kicker">Un assistente, scritto sulla tua attività</span>
      <h1 class="display"><span class="grad">Rispondoio per il tuo settore.</span></h1>
      <p class="lead">Ogni attività riceve chiamate diverse. Scegli la tua e guarda come risponde Rispondoio.</p>
    </div>
    <div class="hub-grid">
{carte}
    </div>
    <p class="mini-fine">Il tuo settore non c'è? <a href="#attiva" class="js-lead" data-plan="Da decidere insieme" data-origine="indice settori">Scrivici</a>: se il telefono squilla, Rispondoio può rispondere.</p>
  </div>
</section>
"""
    (RADICE / "per" / "index.html").write_text(
        pagina("../", "Segreteria telefonica AI per ogni settore | Rispondoio",
               "Rispondoio risponde al telefono di saloni, studi medici e dentistici, ristoranti, officine, "
               "agenzie e artigiani: 24 ore su 24, prenota in agenda durante la chiamata.",
               f"{SITO}/per/", corpo_hub),
        encoding="utf-8")

    # 4. Sitemap e robots
    oggi = date.today().isoformat()
    urls = [f"{SITO}/", f"{SITO}/per/"] + [f"{SITO}/per/{s['slug']}/" for s in SETTORI] + [f"{SITO}/privacy.html"]
    (RADICE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{oggi}</lastmod></url>\n" for u in urls)
        + "</urlset>\n", encoding="utf-8")
    (RADICE / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITO}/sitemap.xml\n", encoding="utf-8")

    print(f"Generate {len(SETTORI)} pagine settore + indice, sitemap.xml ({len(urls)} URL), robots.txt")


if __name__ == "__main__":
    main()
