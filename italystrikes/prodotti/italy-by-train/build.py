"""Costruisce il PDF "Italy by Train: the strike-proof guide" (6x9 pollici).

Uso: python3 italystrikes/prodotti/italy-by-train/build.py
Esce: out/italy-by-train.pdf (+ anteprime PNG e un provino di tutte le pagine).

Sorgenti: contenuto.html (testo), copertina.html (copertina), fonti/ (tabelle ufficiali Trenitalia
e testi di legge), font/ (caratteri con licenza OFL). I dati statistici sono calcolati dal registro
(dati/scioperi.json). Solo fatti con fonte: le fonti sono nell'appendice del PDF.

Passaggi: copertina -> interno (passata 1 con marcatori per trovare le pagine dei capitoli) ->
indice con i numeri di pagina veri -> interno (passata 2) -> unione con la copertina ->
numeri di pagina stampati con reportlab (non su copertina, frontespizio e pagine delle parti).
"""
import collections
import html
import io
import json
import re
import statistics
import subprocess
from datetime import date
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

QUI = Path(__file__).resolve().parent
RADICE = QUI.parent.parent
OUT = QUI / "out"
FONT = QUI / "font"
EDIZIONE = "Edition 1 · October 2026"
TITOLO = "Italy by Train: the strike-proof guide"
MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

# Testi aggiuntivi verificati (vuoti = sezione assente). Vedi fonti/ per le fonti.
EXTRA = json.loads((QUI / "extra.json").read_text(encoding="utf-8")) if (QUI / "extra.json").exists() else {}


def data_lunga(d):
    return f"{d.day} {MESI[d.month - 1]} {d.year}"


def istantanea():
    d = json.loads((RADICE / "dati" / "scioperi.json").read_text(encoding="utf-8"))
    voci = list(d.values())
    n = len(voci)
    sett = collections.Counter(v["settore"] for v in voci)
    giorni = collections.Counter(date.fromisoformat(v["inizio"]).weekday() for v in voci)
    ant = sorted((date.fromisoformat(v["inizio"]) - date.fromisoformat(v["proclamazione"])).days for v in voci)
    reg = json.loads((RADICE / "dati" / "registro.json").read_text(encoding="utf-8"))
    en = {"Trasporto pubblico locale": "Local public transport (bus, metro, tram)", "Aereo": "Air transport", "Trasporto merci": "Freight",
          "Generale": "General strikes", "Plurisettoriale": "Multi-sector strikes", "Ferroviario": "Rail", "Marittimo": "Ferries and ports",
          "Circolazione e sicurezza stradale": "Motorway services", "Taxi": "Taxis"}
    righe = "".join(f"<tr><td>{en.get(k, k)}</td><td class='n m'>{c}</td></tr>" for k, c in sett.most_common())
    return {
        "SNAP_DATA": data_lunga(date.fromisoformat(reg["registro_aggiornato_al"][:10])),
        "SNAP_N": str(n), "SNAP_RIGHE": righe, "SNAP_VEN": str(giorni.get(4, 0)),
        "SNAP_NAZ": str(sum(1 for v in voci if v["rilevanza"].strip().lower() == "nazionale")),
        "SNAP_VEN_STESSO": str(max(collections.Counter(v["inizio"] for v in voci if date.fromisoformat(v["inizio"]).weekday() == 4).values())),
        "SNAP_24": str(sum(1 for v in voci if "24 ORE" in v["modalita"].upper())),
        "SNAP_4": str(sum(1 for v in voci if v["modalita"].upper().startswith("4 ORE"))),
        "SNAP_MIN": str(ant[0]), "SNAP_MAX": str(ant[-1]), "SNAP_MED": f"{statistics.median(ant):g}",
    }


def treni():
    t = json.loads((QUI / "fonti" / "treni-garantiti-2026.json").read_text(encoding="utf-8"))
    citta = {"Roma Termini": "Rome Termini", "Milano Centrale": "Milan Centrale", "Napoli Centrale": "Naples Centrale",
             "Venezia Santa Lucia": "Venice S. Lucia", "Torino Porta Nuova": "Turin P. Nuova", "Salerno": "Salerno",
             "La Spezia Centrale": "La Spezia C."}
    righe = [r for r in t["A"] if r["da"] in citta and r["a"] in citta]
    hh = lambda s: s.zfill(5)
    righe.sort(key=lambda r: (tuple(sorted((citta[r["da"]], citta[r["a"]]))), citta[r["da"]], hh(r["p"])))
    note = {"4": "Fri–Sun, 14 Jun–13 Sep: extended to Bardonecchia", "5": "not on Saturdays"}  # note (4) e (5) della Tabella A
    corpo, ultimo = [], None
    for r in righe:
        coppia = tuple(sorted((citta[r["da"]], citta[r["a"]])))
        stile = " style='border-top:1pt solid #1A1F26'" if ultimo and coppia != ultimo else ""
        ultimo = coppia
        corpo.append(f"<tr{stile}><td class='m'>{r['n']}</td><td>{citta[r['da']]}</td><td class='m'>{hh(r['p'])}</td>"
                     f"<td>{citta[r['a']]}" + (f"<br><span class='piccolo'>{note[r['nota']]}</span>" if r.get('nota') in note else "")
                     + f"</td><td class='m'>{hh(r['ar'])}</td></tr>")
    tab = ("<table style='table-layout:fixed'><colgroup><col style='width:12%'><col style='width:28%'><col style='width:12%'>"
           "<col style='width:34%'><col style='width:14%'></colgroup><tr><th>Train</th><th>From</th><th>Dep.</th><th>To</th><th>Arr.</th></tr>" + "".join(corpo) + "</table>")
    return {"TAB_NA": str(len(t["A"])), "TAB_NB": str(len(t["B"])), "TAB_ESTRATTO": tab, "TAB_N_ESTRATTO": str(len(righe))}


def tessere(testo, n, cls=""):
    testo = testo.ljust(n)[:n]
    return "".join(f"<div class='t {cls if c != ' ' else 'v'}'>{html.escape(c) if c != ' ' else ''}</div>" for c in testo)


def copertina():
    t = json.loads((QUI / "fonti" / "treni-garantiti-2026.json").read_text(encoding="utf-8"))
    per_numero = {r["n"]: r for r in t["A"]}
    breve = {"Bolzano Bozen": "BOLZANO", "Milano Centrale": "MILANO C.LE", "Torino Porta Nuova": "TORINO P.N.",
             "Lecce": "LECCE", "Ventimiglia": "VENTIMIGLIA"}
    righe = []
    for num in ["8502", "9512", "9308", "8620", "8315", "518"]:  # treni reali della Tabella A in partenza da Roma Termini
        r = per_numero[num]
        assert r["da"] == "Roma Termini", num
        righe.append("<div class='riga'>" + tessere(r["p"].zfill(5), 5) + tessere("", 1) + tessere(num, 4) + tessere("", 1)
                     + tessere(breve[r["a"]], 11) + tessere("", 1) + tessere("GARANTITO", 9, "am") + "</div>")
    avviso = tessere("SCIOPERO", 8, "r") + tessere("", 1) + tessere("TRENI GARANTITI", 23)
    colonne = ("<span style='grid-column:1/6'>Orario</span><span style='grid-column:7/11'>Treno</span>"
               "<span style='grid-column:12/23'>Destinazione</span><span style='grid-column:24/33'>Note</span>")
    h = (QUI / "copertina.html").read_text(encoding="utf-8")
    h = h.replace("url(font/", "url(../font/").replace("repeat(30,1fr)", "repeat(32,1fr)")
    for k, v in {"EDIZIONE": EDIZIONE, "AVVISO": avviso, "COLONNE": colonne, "RIGHE": "".join(righe)}.items():
        h = h.replace("{{" + k + "}}", v)
    (OUT / "copertina.html").write_text(h, encoding="utf-8")


def stampa(src, dst, outline):
    js = f"""
const {{ chromium }} = require('/opt/node-tools/node_modules/playwright');
(async () => {{
  const b = await chromium.launch({{ executablePath: '/opt/pw-browsers/chromium' }});
  const p = await b.newPage();
  await p.goto('file://{src}', {{ waitUntil: 'networkidle' }});
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({{ path: '{dst}', preferCSSPageSize: true, printBackground: true, outline: {str(outline).lower()}, tagged: true }});
  await b.close();
}})();
"""
    (OUT / "stampa.js").write_text(js, encoding="utf-8")
    subprocess.run(["node", str(OUT / "stampa.js")], check=True)


def indice(h, pagine):
    voci = []
    for m in re.finditer(r'<section class="parte"><div class="k">(.*?)</div><div class="h"><em>(.*?)</em>|'
                         r'<section class="capitolo[^"]*"[^>]*>\s*<div class="kick"><span class="tile">(\w+)</span>[^<]*</div>\s*<h1>(.*?)</h1>', h):
        if m.group(1):
            voci.append(f"<li class='parte-i'><span class='tt'>{m.group(1)} · {m.group(2)}</span></li>")
        else:
            num, tit = m.group(3), m.group(4)
            pg = pagine.get("C" + num, "")
            voci.append(f"<li><span class='nn'>{num}</span><span class='tt'>{tit}</span><span class='pp'>{pg}</span></li>")
    return "<ul class='indice'>" + "".join(voci) + "</ul>"


def tipografia(h):
    """Virgolette e apostrofi tipografici nel testo (non nei tag e non nello stile)."""
    testa, corpo = h.split("</style>", 1)

    def testo(m):
        t = m.group(0)
        t = re.sub(r'(?<=[\s(>\[])"', "\u201c", t)
        t = t.replace('"', "\u201d").replace("'", "\u2019")
        return t
    corpo = re.sub(r">[^<]+<", testo, corpo)
    return testa + "</style>" + corpo


def con_marcatori(h):
    h = re.sub(r'(<section class="capitolo[^"]*"[^>]*>\s*<div class="kick"><span class="tile">(\w+)</span>)',
               lambda m: m.group(1).replace('<div class="kick">', f'<span class="marca">QQC{m.group(2)}QQ</span><div class="kick">', 1), h)
    n = [0]

    def parte(m):
        n[0] += 1
        return m.group(0) + f'<span class="marca">QQP{n[0]}QQ</span>'
    return re.sub(r'<section class="parte">', parte, h)


def mappa_pagine(pdf):
    r = PdfReader(str(pdf))
    pagine, parti = {}, []
    for i, p in enumerate(r.pages):
        for m in re.finditer(r"QQ([CP]\w+?)QQ", (p.extract_text() or "").replace(" ", "")):
            if m.group(1).startswith("C"):
                pagine.setdefault(m.group(1), i + 2)  # +1 base 1, +1 copertina
            else:
                parti.append(i + 1)  # indice 0-based nel PDF finale (copertina in testa)
    return pagine, parti


def numera(src, dst, salta):
    """Piede di pagina (titolo corrente + numero) con un solo PDF di sovrapposizione: i font sono incorporati una volta."""
    pdfmetrics.registerFont(TTFont("ISans", str(FONT / "InstrumentSans-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("GM", str(FONT / "GeistMono-Regular.ttf")))
    w = PdfWriter(clone_from=str(src))
    L, H = float(w.pages[0].mediabox.width), float(w.pages[0].mediabox.height)
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(L, H), initialFontName="ISans", initialFontSize=7.4)
    for i in range(len(w.pages)):
        if i not in salta:
            y = 0.42 * 72
            c.setFillColorRGB(0.45, 0.48, 0.52)
            c.setFont("ISans", 7.4)
            c.drawString(0.62 * 72, y, "Italy by Train · the strike-proof guide")
            c.setFont("GM", 8)
            c.drawRightString(L - 0.6 * 72, y, str(i + 1))
            c.setStrokeColorRGB(0.89, 0.87, 0.83)
            c.setLineWidth(0.6)
            c.line(0.62 * 72, y + 11, L - 0.6 * 72, y + 11)
        c.showPage()
    c.save()
    buf.seek(0)
    sovr = PdfReader(buf)
    for i, pag in enumerate(w.pages):
        if i not in salta:
            pag.merge_page(sovr.pages[i])
    w.add_metadata({"/Producer": "Italy Strikes Today", "/Title": TITOLO, "/Author": "Italy Strikes Today", "/Subject": "How to travel around Italy when transport goes on strike",
                    "/Keywords": "Italy, trains, strikes, sciopero, Trenitalia, travel", "/Creator": "Italy Strikes Today"})
    w.page_mode = "/UseOutlines"
    with open(dst, "wb") as f:
        w.write(f)


def main():
    OUT.mkdir(exist_ok=True)
    valori = {**istantanea(), **treni(), "EDIZIONE": EDIZIONE,
              "SAFETYWING": json.loads((RADICE / "dati" / "affiliati.json").read_text(encoding="utf-8"))["safetywing"]["url"],
              "RIGHE_FOGLIO": "".join(f"<tr><td class='m'>{i}</td>" + "<td></td>" * 8 + "</tr>" for i in range(1, 17)),
              "FRANCHIGIE": EXTRA.get("franchigie", ""), "FAQ_FRANCHIGIE": EXTRA.get("faq_franchigie", ""),
              "RIMBORSI_OPERATORI": EXTRA.get("rimborsi_operatori", ""), "FONTI_EXTRA": EXTRA.get("fonti_extra", "")}
    h = (QUI / "contenuto.html").read_text(encoding="utf-8")
    for k, v in valori.items():
        h = h.replace("{{" + k + "}}", v)
    h = tipografia(h)
    resto = set(re.findall(r"\{\{(\w+)\}\}", h)) - {"INDICE"}
    if resto:
        raise SystemExit(f"Segnaposto non sostituiti: {resto}")

    copertina()
    stampa(OUT / "copertina.html", OUT / "copertina.pdf", False)

    # passata 1: marcatori invisibili per trovare le pagine
    (OUT / "guida.html").write_text(con_marcatori(h.replace("{{INDICE}}", indice(h, {}))), encoding="utf-8")
    stampa(OUT / "guida.html", OUT / "passata1.pdf", False)
    pagine, parti = mappa_pagine(OUT / "passata1.pdf")
    # passata 2: indice con i numeri veri, senza marcatori
    (OUT / "guida.html").write_text(h.replace("{{INDICE}}", indice(h, pagine)), encoding="utf-8")
    stampa(OUT / "guida.html", OUT / "interno.pdf", True)

    w = PdfWriter(clone_from=str(OUT / "interno.pdf"))
    w.insert_page(PdfReader(str(OUT / "copertina.pdf")).pages[0], 0)
    w.write(str(OUT / "unito.pdf"))
    numera(OUT / "unito.pdf", OUT / "italy-by-train.pdf", {0, 1} | set(parti))
    for f in ["passata1.pdf", "unito.pdf", "interno.pdf"]:
        (OUT / f).unlink()

    for f in OUT.glob("*.png"):
        f.unlink()
    subprocess.run(["pdftoppm", "-png", "-r", "60", str(OUT / "italy-by-train.pdf"), str(OUT / "pg")], check=True)
    subprocess.run(["pdftoppm", "-png", "-r", "150", "-f", "1", "-l", "1", str(OUT / "italy-by-train.pdf"), str(OUT / "copertina")], check=True)
    # pagine di esempio per la pagina di vendita del sito (copertina, voci decodificate, tabella reale, situazioni)
    campioni = RADICE / "assets" / "guida"
    campioni.mkdir(parents=True, exist_ok=True)
    for f in campioni.glob("*.png"):
        f.unlink()
    for i, n in enumerate([1, pagine["C03"] + 2, pagine["C05"] + 2, pagine["C11"]], start=1):
        subprocess.run(["pdftoppm", "-png", "-r", "100", "-singlefile", "-f", str(n), "-l", str(n),
                        str(OUT / "italy-by-train.pdf"), str(campioni / f"pagina-{i}")], check=True)
    # numero di pagine nella scheda prodotto del sito
    fp = RADICE / "dati" / "prodotti.json"
    prod = json.loads(fp.read_text(encoding="utf-8"))
    prod["italy-by-train"]["pagine"] = len(PdfReader(str(OUT / "italy-by-train.pdf")).pages)
    prod["italy-by-train"]["frase"] = (f'a {prod["italy-by-train"]["pagine"]}-page PDF with the official rules, '
                                       f'your rights and plans that survive a strike day.')
    fp.write_text(json.dumps(prod, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(subprocess.run(["pdfinfo", str(OUT / "italy-by-train.pdf")], capture_output=True, text=True).stdout)
    print("Capitoli:", pagine, "Parti (indice 0):", parti)


if __name__ == "__main__":
    main()
