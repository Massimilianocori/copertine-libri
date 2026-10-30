"""Genera il sito statico Visa Income Checker in visaincome/sito/ da visaincome/dati/.

Uso (dalla radice del repository):
    python3 visaincome/genera.py

Dati:
    dati/programmi.json  indici ufficiali (SMI, IPREM, RMMG...) e programmi di visto, con regole e fonti (URL + data del controllo)
    dati/cambi.json      cambi di riferimento BCE (raccolta/cambi.py); le pagine li rileggono dal vivo da GitHub
    dati/affiliati.json  riquadro affiliati (vuoto finché non ci sono URL)

Il calcolatore gira nel browser (JS in pagina, nessuno script esterno). La stessa logica è scritta qui in Python
(calcola, converti) per le tabelle statiche e per i controlli di verifica.py, che confronta Python e JS.
"""
import json
import math
import re
import shutil
import sys
from collections import defaultdict
from datetime import date
from html import escape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
URL_SITO = "https://visa-income-checker.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti), 10/10/2026: non rimuoverlo

ALTRI_SITI = [  # blocco "Other useful tools for your trip" in fondo a ogni pagina (URL dai genera.py dei rispettivi siti)
    ("https://italy-strikes-today.netlify.app/", "Italy Strikes Today", "Transport strikes in Italy today and tomorrow, from the official register"),
    ("https://tourist-tax-calculator.netlify.app/", "Tourist Tax Calculator", "City tax per night in 200+ European destinations"),
    ("https://before-you-fly.netlify.app/", "Before You Fly", "Passport validity, airport liquid rules, cabin bag sizes"),
]


def blocco_altri(voci, titolo):
    """Blocco "Other useful tools for your trip" in fondo a ogni pagina (stesso modello di esameb1/esamidistato): un titolo piccolo e una riga
    per sito. Link normali (nessun nofollow), rel="noopener", mai a questo sito."""
    assert not any(u.startswith(URL_SITO) for u, _, _ in voci), "il blocco altri siti non deve linkare questo sito"
    li = "".join(f'<li><a href="{u}" rel="noopener">{escape(n)}</a> — {escape(d)}</li>' for u, n, d in voci)
    return f'<div class="f-altri"><h2>{escape(titolo)}</h2><ul>{li}</ul></div>'

# Contatore visite GoatCounter, account condiviso "rete-siti" della rete (nessun cookie, nessun dato personale conservato).
# Il percorso inviato comprende l'host (location.host + percorso), così nel cruscotto https://rete-siti.goatcounter.com
# ogni sito si distingue dagli altri. Da localhost, da file:// e dalle reti private count.js non invia nulla
# (allow_local resta spento): le prove in locale non contano come visite. Unico punto da cambiare per tutto il sito.
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
# IndexNow (Bing, Yandex, Naver, Seznam): chiave pubblica uguale per tutti i siti della rete. Il generatore scrive
# sito/<chiave>.txt (contenuto: la chiave) accanto a robots.txt; l'invio degli URL lo fa studio-business/strumenti/indexnow.py.
CHIAVE_INDEXNOW = "b5a26a844a465f58552debee2c8a0114"
# Monetizzazione (30/10/2026): codice editore AdSense, elenco dei siti con la pubblicità e domini di affiliazione ammessi stanno
# in un solo file comune, studio-business/strumenti/monetizzazione.json (logica in monetizzazione.py). Con il codice vuoto o con
# questo sito fuori elenco non cambia nulla: niente script nel <head>, niente ads.txt, privacy di oggi.
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402
SITO_ID = "visaincome"  # nome del sito in monetizzazione.json ("adsense_siti")
ADSENSE_HEAD = MON.script_adsense(SITO_ID)  # "" con AdSense spento; altrimenti a capo + script ufficiale, subito dopo il meta di verifica Google


def ci_sono_affiliati():
    """True se il sito pubblica almeno un link di affiliazione (voce con "url" in dati/affiliati.json e il link SafetyWing delle pagine dei rifiuti):
    accende la sezione privacy sui link di affiliazione. Domini ammessi in monetizzazione.json, controlli in verifica.py."""
    return any(isinstance(v, dict) and v.get("url") for k, v in AFFILIATI.items() if not k.startswith("_")) or bool(URL_SAFETYWING)


def riquadro_trasparenza(corpo, lingua="en"):
    """Riga di trasparenza sui link di affiliazione in fondo al contenuto della pagina ("Some links are affiliate links: ..."):
    vuota finché la pagina non ha link rel="sponsored" o se un riquadro di affiliazione la mostra già."""
    return MON.riga_trasparenza(corpo, lingua)


URL_CAMBI_LIVE = ("https://raw.githubusercontent.com/Massimilianocori/copertine-libri/"
                  "ccr-b7fd6b9e-n096cr/italystrikes/dati/cambi-bce.json")  # aggiornata 2 volte al giorno dal workflow di Italy Strikes
NOME = "Visa Income Checker"
ANNO = 2026
OGGI = date.today()

_D = json.loads((DATI / "programmi.json").read_text(encoding="utf-8"))
INDICI = _D["indici"]
PROG = _D["programmi"]
CAMBI = json.loads((DATI / "cambi.json").read_text(encoding="utf-8"))
AFFILIATI = json.loads((DATI / "affiliati.json").read_text(encoding="utf-8")) if (DATI / "affiliati.json").exists() else {}

MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
# Valute BCE: nome e decimali mostrati
VALUTE = {
    "EUR": ("Euro", 2), "USD": ("US dollar", 2), "GBP": ("Pound sterling", 2), "CAD": ("Canadian dollar", 2),
    "AUD": ("Australian dollar", 2), "NZD": ("New Zealand dollar", 2), "INR": ("Indian rupee", 2), "PHP": ("Philippine peso", 2),
    "ZAR": ("South African rand", 2), "BRL": ("Brazilian real", 2), "MXN": ("Mexican peso", 2), "TRY": ("Turkish lira", 2),
    "CNY": ("Chinese yuan", 2), "HKD": ("Hong Kong dollar", 2), "SGD": ("Singapore dollar", 2), "MYR": ("Malaysian ringgit", 2),
    "THB": ("Thai baht", 2), "IDR": ("Indonesian rupiah", 0), "JPY": ("Japanese yen", 0), "KRW": ("South Korean won", 0),
    "ILS": ("Israeli shekel", 2), "CHF": ("Swiss franc", 2), "NOK": ("Norwegian krone", 2), "SEK": ("Swedish krona", 2),
    "DKK": ("Danish krone", 2), "ISK": ("Icelandic krona", 0), "PLN": ("Polish zloty", 2), "CZK": ("Czech koruna", 2),
    "HUF": ("Hungarian forint", 0), "RON": ("Romanian leu", 2)}
VALUTE_TABELLA = ["EUR", "USD", "GBP", "CAD", "AUD", "NZD", "INR", "PHP", "ZAR", "BRL", "MXN", "TRY", "CNY", "SGD", "JPY"]
CATEGORIE = {"digital-nomad": "Digital nomad visa", "passive-income": "Passive income / retirement visa",
             "work": "Work permit / EU Blue Card", "family": "Family visa"}
PAESI = {}
for _p in PROG:
    PAESI.setdefault(_p["paese_slug"], _p["paese"])


# ---------------------------------------------------------------- utilità
def r2(x):
    """Arrotondamento al centesimo, mezzo in su (uguale nel JS)."""
    return math.floor(x * 100 + 0.5 + 1e-9) / 100


def arrotonda(x, valuta):
    return r2(x) if VALUTE.get(valuta, ("", 2))[1] == 2 else math.floor(x + 0.5 + 1e-9)


def soldi(v, valuta):
    dec = VALUTE.get(valuta, ("", 2))[1]
    testo = f"{r2(v):,.2f}" if dec == 2 else f"{int(math.floor(v + 0.5 + 1e-9)):,}"
    if testo.endswith(".00"):  # importi interi senza centesimi (uguale nel JS)
        testo = testo[:-3]
    if valuta == "EUR":
        return "€" + testo
    if valuta == "GBP":
        return "£" + testo
    return f"{valuta} {testo}"


def senza_zeri(t):
    """Nelle note di sintesi (non nelle citazioni ufficiali): '€600.00' -> '€600', come gli altri importi interi."""
    return re.sub(r"((?:[€£]|\b[A-Z]{3} )\d[\d,]*)\.00\b", r"\1", t)


def num(v):
    return "%g" % v


def data_lunga(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {MESI[d.month - 1]} {d.year}"


def per_slug(slug):
    return next(p for p in PROG if p["slug"] == slug)


def titolo_prog(P):
    return f"{P['paese']} {P['nome']} income requirement {ANNO}: how much you need (calculator)"


def nome_prog(P):
    return f"{P['paese']} {P['nome']}"


# ---------------------------------------------------------------- motore di calcolo (uguale al JS)
def unita(V):
    """(valore, valuta, periodo, pagamenti all'anno) della base di una variante."""
    b = V["base"]
    src = INDICI[b["indice"]] if "indice" in b else b
    per = src["periodo"]
    return src["valore"], src["valuta"], per, (src.get("pagamenti", 12) if per == "month" else 12)


LIMITI = {"adulti": (1, 20), "figli": (0, 20), "pagamenti": (12, 14)}


def limita(nome, x):
    lo, hi = LIMITI[nome]
    try:
        x = int(x)
    except (TypeError, ValueError):
        x = lo
    return max(lo, min(hi, x))


def calcola(P, vid, adulti, figli):
    """Importo minimo per richiedente + familiari.

    adulti = adulti compreso il richiedente (>= 1); figli = figli sotto i 18 anni.
    Restituisce dict con valuta, periodo, pagamenti (mensilità all'anno della regola), righe [testo, quanti, importo unitario, subtotale],
    totale (nel periodo della base), mensile (importo mensile della regola, per mensilità), annuale (= mensile × pagamenti, o la soglia annua),
    mensile12 (annuale / 12), familiari_ignorati (bool), motivo, tetto (bool).
    """
    V = next(v for v in P["varianti"] if v["id"] == vid)
    u, val, per, npag = unita(V)
    adulti = limita("adulti", adulti)
    figli = limita("figli", figli)
    righe = []
    principale = r2(u * V["fattore"])
    righe.append(["main", 1, principale, principale])
    fam = V["famiglia"]
    tipo = fam["tipo"]
    altri_adulti = adulti - 1
    ignorati = False
    if tipo == "tutti":
        n = altri_adulti + figli
        if n >= 1:
            a = r2(u * fam["primo"])
            righe.append(["first", 1, a, a])
        if n >= 2:
            b = r2(u * fam["altri"])
            righe.append(["other", n - 1, b, r2(b * (n - 1))])
    elif tipo == "per_eta":
        if altri_adulti:
            a = r2(u * fam["adulto"])
            righe.append(["adult", altri_adulti, a, r2(a * altri_adulti)])
        if figli:
            c = r2(u * fam["figlio"])
            righe.append(["child", figli, c, r2(c * figli)])
    elif tipo == "figli":
        if figli >= 1:
            a = r2(u * fam["primo"])
            righe.append(["firstchild", 1, a, a])
        if figli >= 2:
            b = r2(u * fam["altri"])
            righe.append(["otherchild", figli - 1, b, r2(b * (figli - 1))])
    elif tipo == "nessuno":
        ignorati = altri_adulti > 0 or figli > 0
    else:
        raise ValueError(tipo)
    totale = r2(sum(r[3] for r in righe))
    tetto = False
    if V.get("tetto") is not None:
        cap = r2(u * V["tetto"])
        if totale > cap:
            totale = cap
            tetto = True
    if per == "month":
        mensile, annuale = totale, r2(totale * npag)
        mensile12 = r2(annuale / 12)
    else:
        annuale, mensile = totale, r2(totale / 12)
        mensile12 = mensile
    return {"valuta": val, "periodo": per, "pagamenti": npag, "righe": righe, "totale": totale, "mensile": mensile, "annuale": annuale,
            "mensile12": mensile12, "familiari_ignorati": ignorati, "motivo": fam.get("motivo", ""), "tetto": tetto, "unita": u,
            "adulti": adulti, "figli": figli}


def converti(importo, da, a, tassi):
    """Converte con i cambi BCE (1 EUR = tassi[X] X), passando per l'euro; arrotonda alla valuta di arrivo."""
    if da == a:
        return arrotonda(importo, a)
    eur = importo if da == "EUR" else importo / tassi[da]
    return arrotonda(eur if a == "EUR" else eur * tassi[a], a)


def converti_scalato(importo, da, a, tassi, molt=1, div=1):
    """Converte e poi moltiplica/divide, arrotondando di nuovo: così mese e anno convertiti restano coerenti."""
    c = converti(importo, da, a, tassi)
    return c if molt == 1 and div == 1 else arrotonda(c * molt / div, a)


def converti_importi(o, a, tassi):
    """Mensile, annuale e mensile su 12 mesi nella valuta a: si converte l'importo del periodo della regola e si ricava l'altro."""
    val = o["valuta"]
    if o["periodo"] == "month":
        cm = converti(o["mensile"], val, a, tassi)
        cy = arrotonda(cm * o["pagamenti"], a)
        return {"mensile": cm, "annuale": cy, "mensile12": arrotonda(cy / 12, a) if o["pagamenti"] != 12 else cm}
    cy = converti(o["annuale"], val, a, tassi)
    cm = arrotonda(cy / 12, a)
    return {"mensile": cm, "annuale": cy, "mensile12": cm}


def esito(P, o, reddito, pagamenti, valuta, tassi):
    """Confronto tra il reddito dell'utente (al mese, nella valuta scelta, pagato 'pagamenti' volte l'anno) e la soglia.

    Restituisce 'nd' (programma senza verdetto: si mostrano le condizioni), 'si', 'no' o 'parziale'
    (Spagna: rispetta l'importo mensile ma non il totale annuo, o il contrario).
    """
    if P.get("esito") is False or not reddito or reddito <= 0:
        return "nd"
    k = limita("pagamenti", pagamenti)
    x = converti(reddito, valuta, o["valuta"], tassi)
    anno = r2(x * k)
    modo = P.get("confronto") or ("mese" if o["periodo"] == "month" else "anno")
    if modo == "mese":
        return "si" if x >= o["mensile"] else "no"
    if modo == "anno":
        return "si" if anno >= o["annuale"] else "no"
    a, b = x >= o["mensile"], anno >= o["annuale"]
    return "si" if a and b else ("no" if not a and not b else "parziale")


# ---------------------------------------------------------------- testi derivati dalle regole
def etichetta_fattore(V, f):
    """Testo tipo '2 × the SMI (€1,221.00 a month × 14 payments)' o '75% of the SMI (...)'."""
    b = V["base"]
    u, val, per, npag = unita(V)
    if "indice" in b:
        I = INDICI[b["indice"]]
        quando = ("a month" + (f" × {npag} payments" if npag != 12 else "")) if per == "month" else "a year"
        parte = f"{num(f)} × the {I['nome_breve']}" if f >= 1 else f"{num(round(f * 100, 6))}% of the {I['nome_breve']}"
        return f"{parte} ({soldi(u, val)} {quando})"
    if u == 1:
        return soldi(f, val)
    return f"{b['etichetta']}: {soldi(u * f, val)}"


def testo_riga(V, r):
    fam = V["famiglia"]
    k = r[0]
    if k == "main":
        return V.get("etichetta_principale", "Main applicant") + ": " + etichetta_fattore(V, V["fattore"])
    if k == "first":
        return "First family member: " + etichetta_fattore(V, fam["primo"])
    if k == "other":
        return "Each further family member: " + etichetta_fattore(V, fam["altri"])
    if k == "adult":
        return "Each further adult: " + etichetta_fattore(V, fam["adulto"])
    if k == "child":
        return "Each child: " + etichetta_fattore(V, fam["figlio"])
    if k == "firstchild":
        return "First child: " + etichetta_fattore(V, fam["primo"])
    if k == "otherchild":
        return "Each further child: " + etichetta_fattore(V, fam["altri"])
    return k


def periodo_testo(per):
    return "a month" if per == "month" else "a year"


def mese_testo(o, val=None, conv=None):
    """'€2,442.00 a month × 14 payments' oppure '€3,680.00 a month'."""
    val = val or o["valuta"]
    m = conv["mensile"] if conv else o["mensile"]
    return soldi(m, val) + " a month" + (f" × {o['pagamenti']} payments" if o["periodo"] == "month" and o["pagamenti"] != 12 else "")


def figura_testo(o, forte=True):
    """Cifra principale completa: mese, anno e (se le mensilità non sono 12) l'equivalente su 12 mesi."""
    val = o["valuta"]
    s = (lambda x: f"<strong>{x}</strong>") if forte else (lambda x: x)
    if o["periodo"] == "month" and o["pagamenti"] != 12:
        return (f"{s(soldi(o['mensile'], val))} a month × {o['pagamenti']} payments = {s(soldi(o['annuale'], val))} a year "
                f"({soldi(o['mensile12'], val)} a month if spread over 12 payments)")
    if o["periodo"] == "month":
        return f"{s(soldi(o['mensile'], val))} a month ({s(soldi(o['annuale'], val))} a year)"
    return f"{s(soldi(o['annuale'], val))} a year ({soldi(o['mensile'], val)} a month)"


def riassunto(P):
    """Riga breve: importo del richiedente principale (prima variante)."""
    V = P["varianti"][0]
    o = calcola(P, V["id"], 1, 0)
    val = o["valuta"]
    if o["periodo"] == "month":
        if o["pagamenti"] != 12:
            return f"{soldi(o['mensile'], val)} a month × {o['pagamenti']} ({soldi(o['annuale'], val)} a year)"
        return f"{soldi(o['mensile'], val)} a month"
    return f"{soldi(o['annuale'], val)} a year"


def fonti_prog(P):
    """Fonti del programma + fonti degli indici usati (senza doppioni)."""
    out, visti = [], set()
    for f in P["fonti"]:
        if f["url"] not in visti:
            out.append(f)
            visti.add(f["url"])
    for V in P["varianti"]:
        if "indice" in V["base"]:
            for f in INDICI[V["base"]["indice"]]["fonti"]:
                if f["url"] not in visti:
                    out.append(f)
                    visti.add(f["url"])
    return out


def fonti_html(fonti):
    righe = []
    for f in fonti:
        righe.append(f'<li><a href="{escape(f["url"])}" rel="noopener">{escape(f["titolo"])}</a> – {escape(f["editore"])}, {escape(f["formato"])}, '
                     f'checked on {data_lunga(f["controllato_il"])}'
                     + (f'<br><span class="small">What it says: {escape(senza_zeri(f["nota"]))}</span>' if f.get("nota") else "") + "</li>")
    return '<ul class="fonti">' + "".join(righe) + "</ul>"


def fonte_breve(P):
    f = P["fonti"][0]
    return (f'<p class="fonte">Official source: <a href="{escape(f["url"])}" rel="noopener">{escape(f["titolo"])}</a> ({escape(f["editore"])}) · '
            f'checked on {data_lunga(f["controllato_il"])}</p>')


def cambi_nota():
    return (f'Converted with the European Central Bank reference rates of <span data-cambi-data>{data_lunga(CAMBI["data"])}</span> '
            f'(updated automatically every working day). Indicative only: consulates may use another rate or ask for the amount in euros.')


# ---------------------------------------------------------------- CSS e JS
CSS = """
@font-face{font-family:"IBM Plex Serif";font-style:normal;font-weight:700;font-display:swap;src:url(/assets/fonts/ibm-plex-serif-700.woff2) format("woff2")}
:root{--bg:#F4F5F9;--card:#FFFFFF;--ink:#141B33;--ink-2:#3C4565;--ink-3:#596282;--line:#DCE0EC;--line-2:#C9CFE0;
--navy:#141B33;--navy-2:#1F2A52;--on-navy:#F4F5F9;--on-navy-2:#BFC6E0;--gold:#E0A526;--gold-ink:#8A5A00;--gold-2:#FFF6E0;--paper:#FBF8EF;
--accent:#2A3D8F;--accent-h:#1C2C70;--on-accent:#FFFFFF;--accent-2:#E8ECFA;
--ok:#126B41;--ok-2:#E2F4EA;--no:#A12A2A;--no-2:#FCE9E9;--warn:#8A4B00;--warn-2:#FFF1DC;--mute:#EEF0F6;
--sh-1:0 1px 2px rgba(20,27,51,.06),0 1px 1px rgba(20,27,51,.04);--sh-2:0 22px 44px -22px rgba(20,27,51,.35),0 2px 8px rgba(20,27,51,.06);
--r:14px;--r-s:10px;--serif:"IBM Plex Serif",Charter,"Bitstream Charter","Iowan Old Style",Georgia,serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0C1020;--card:#151A2E;--ink:#EEF0F8;--ink-2:#C2C8DE;--ink-3:#99A1BD;--line:#283052;--line-2:#343D63;
--navy:#080B17;--navy-2:#161D3A;--on-navy:#EEF0F8;--on-navy-2:#A9B1CF;--gold:#F2C14E;--gold-ink:#F2C14E;--gold-2:#2A2410;--paper:#1A2036;
--accent:#AFBDFF;--accent-h:#CDD6FF;--on-accent:#0C1020;--accent-2:#1E2650;
--ok:#7DDBA6;--ok-2:#12301F;--no:#FF9F9F;--no-2:#3A1B1D;--warn:#FFB867;--warn-2:#33250F;--mute:#1B2138;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 22px 44px -22px rgba(0,0,0,.8),0 2px 8px rgba(0,0,0,.4)}}
:root[data-theme="dark"]{--bg:#0C1020;--card:#151A2E;--ink:#EEF0F8;--ink-2:#C2C8DE;--ink-3:#99A1BD;--line:#283052;--line-2:#343D63;
--navy:#080B17;--navy-2:#161D3A;--on-navy:#EEF0F8;--on-navy-2:#A9B1CF;--gold:#F2C14E;--gold-ink:#F2C14E;--gold-2:#2A2410;--paper:#1A2036;
--accent:#AFBDFF;--accent-h:#CDD6FF;--on-accent:#0C1020;--accent-2:#1E2650;
--ok:#7DDBA6;--ok-2:#12301F;--no:#FF9F9F;--no-2:#3A1B1D;--warn:#FFB867;--warn-2:#33250F;--mute:#1B2138;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 22px 44px -22px rgba(0,0,0,.8),0 2px 8px rgba(0,0,0,.4)}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;font-size:17px;line-height:1.6;overflow-wrap:break-word}
a{color:var(--accent);text-underline-offset:2px;text-decoration-thickness:1px}
a:hover{color:var(--accent-h)}
:focus-visible{outline:3px solid var(--gold);outline-offset:2px;border-radius:4px}
.skip{position:absolute;left:-9999px;top:8px;background:var(--card);color:var(--ink);padding:8px 14px;border-radius:8px;z-index:50}
.skip:focus{left:12px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.ico{width:1.15em;height:1.15em;flex:none;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;vertical-align:-.2em}
.wrap{max-width:1060px;margin:0 auto;padding:0 16px}
header.top{background:var(--navy);color:var(--on-navy);position:relative;z-index:20;border-bottom:3px solid var(--gold)}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:64px}
.logo{display:flex;align-items:center;gap:11px;font-family:var(--serif);font-weight:700;font-size:1.15rem;color:var(--on-navy);text-decoration:none;white-space:nowrap;letter-spacing:-.005em}
.logo:hover{color:#fff}
.logo svg{width:34px;height:34px;flex:none}
.logo b{color:var(--gold);font-weight:inherit}
nav.menu{display:flex;gap:2px;font-size:.92rem}
nav.menu a{color:var(--on-navy-2);text-decoration:none;padding:7px 11px;border-radius:8px;white-space:nowrap}
nav.menu a:hover,nav.menu a[aria-current]{color:#fff;background:rgba(255,255,255,.08)}
.nav-m{display:none}
.nav-m summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:8px;font-weight:600;font-size:.95rem;padding:9px 14px;border:1px solid rgba(255,255,255,.28);border-radius:10px;color:var(--on-navy);min-height:44px}
.nav-m summary::-webkit-details-marker{display:none}
.nav-m[open] summary{background:rgba(255,255,255,.1);border-color:var(--gold)}
.nav-m nav{position:absolute;left:16px;right:16px;top:calc(100% + 4px);background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-2);padding:8px;display:grid}
.nav-m nav a{padding:12px 14px;border-radius:8px;color:var(--ink);text-decoration:none;font-weight:600}
.nav-m nav a:hover{background:var(--accent-2)}
.band{background:linear-gradient(180deg,var(--navy) 0,var(--navy-2) 72%,var(--bg) 72%);color:var(--on-navy)}
.band-in{position:relative;padding-top:38px;padding-bottom:8px}
.band .hero{padding:0 0 26px;max-width:760px;position:relative}
.band-deco{position:absolute;right:8px;top:30px;width:230px;height:150px;pointer-events:none;opacity:.9}
.hero{padding:24px 0 4px}
h1,h2,h3,.tot,.cifra strong{font-family:var(--serif);font-weight:700}
h1{font-size:clamp(1.7rem,4.6vw,2.6rem);line-height:1.12;letter-spacing:-.015em;margin:0 0 10px;text-wrap:balance}
h1 .h1-a{display:block}
h1 .h1-b{display:block;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-weight:600;font-size:clamp(1rem,2.4vw,1.15rem);color:var(--ink-2);letter-spacing:0;margin-top:8px;line-height:1.35}
h1 .h1-b::first-letter{text-transform:uppercase}
.band h1 .h1-a{display:inline-block;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-size:.78rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);border:1px solid rgba(224,165,38,.55);padding:5px 12px;border-radius:6px;margin-bottom:16px}
.band h1 .h1-b{font-family:var(--serif);font-weight:700;color:#fff;font-size:clamp(1.9rem,5.4vw,2.9rem);line-height:1.1;letter-spacing:-.02em;margin:0;text-wrap:balance}
.sub{font-size:1.1rem;color:var(--on-navy-2);margin:12px 0 16px;max-width:640px;text-wrap:balance}
.trust{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.88rem;color:var(--on-navy-2);margin:0}
.trust span{display:inline-flex;align-items:center;gap:7px}
.trust .ico{color:var(--gold)}
h2{font-size:1.45rem;line-height:1.22;margin:40px 0 14px;letter-spacing:-.01em}
h3{font-size:1.12rem;margin:22px 0 8px}
.lead{font-size:1.04rem;color:var(--ink-2);max-width:760px;margin:0 0 8px}
.small{font-size:.88rem;color:var(--ink-3)}
.avviso{position:relative;background:var(--warn-2);border:1px solid color-mix(in srgb,var(--warn) 25%,transparent);padding:12px 16px 12px 46px;border-radius:var(--r-s);font-size:.93rem;margin:18px 0;color:var(--ink)}
.avviso::before{content:"";position:absolute;left:16px;top:14px;width:20px;height:20px;background:var(--warn);-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round'%3E%3Cpath d='M12 3 2 20h20z'/%3E%3Cpath d='M12 10v4M12 17h.01'/%3E%3C/svg%3E") center/contain no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round'%3E%3Cpath d='M12 3 2 20h20z'/%3E%3Cpath d='M12 10v4M12 17h.01'/%3E%3C/svg%3E") center/contain no-repeat}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:20px;min-width:0;box-shadow:var(--sh-1)}
.summary{padding:0;overflow:hidden;margin-top:8px;box-shadow:var(--sh-2)}
.summary .s-top{display:flex;align-items:center;gap:10px;background:var(--navy);color:var(--on-navy-2);padding:10px 20px;font-size:.78rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;border-bottom:2px solid var(--gold)}
.summary .s-top .ico{color:var(--gold)}
.summary .s-top span:last-child{margin-left:auto;letter-spacing:.04em}
.summary .s-body{padding:20px 22px 18px;display:grid;gap:4px}
.summary .lead{font-size:.95rem;margin:10px 0 0}
.cifra{font-size:1rem;margin:0;color:var(--ink-2)}
.cifra{font-size:1.02rem;line-height:1.55}
.cifra .c-lab{display:block;font-size:.78rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--gold-ink);margin-bottom:4px}
.cifra strong{font-size:clamp(1.45rem,3.8vw,1.95rem);color:var(--ink);letter-spacing:-.01em;font-variant-numeric:tabular-nums;line-height:1.25}
.fonte{font-size:.84rem;color:var(--ink-3);margin:8px 0 0;overflow-wrap:anywhere}
.fonte a{color:var(--ink-2)}
.calc{padding:0;overflow:hidden;box-shadow:var(--sh-2);border-color:var(--line-2)}
.summary+h2,.hero+.calc{margin-top:22px}
.calc-grid{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr)}
.calc form{padding:22px}
.calc .campi{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.calc label{display:grid;gap:6px;align-content:end;font-weight:600;font-size:.9rem;line-height:1.35;min-width:0;color:var(--ink-2)}
.calc .lt{display:flex;align-items:center;gap:7px}
.calc .lt .ico{color:var(--accent);width:1.05em;height:1.05em}
.calc input,.calc select,.form input,.form select,.form textarea{font:inherit;font-size:1rem;color:var(--ink);background:var(--card);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:10px 12px;width:100%;min-width:0;min-height:46px;transition:border-color .15s,box-shadow .15s}
.calc input:hover,.calc select:hover{border-color:var(--ink-3)}
.calc input:focus,.calc select:focus,.form input:focus,.form textarea:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 20%,transparent)}
.calc .pieno{grid-column:1/-1}
.calc-out{background:var(--paper);border-left:1px solid var(--line);padding:22px;min-width:0;position:relative}
.calc-out::before{content:"";position:absolute;left:0;right:0;top:0;height:4px;background:repeating-linear-gradient(90deg,var(--gold) 0 18px,transparent 18px 26px)}
.risultato{min-width:0;overflow-wrap:anywhere}
.r-lab{font-size:.76rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3)}
.risultato .tot{font-size:clamp(2.1rem,6vw,2.75rem);line-height:1.05;color:var(--ink);letter-spacing:-.02em;margin:8px 0 2px;font-variant-numeric:tabular-nums}
.risultato .tot span{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-size:1rem;font-weight:600;color:var(--ink-2);letter-spacing:0}
.r-anno{font-size:1rem;color:var(--ink-2);font-variant-numeric:tabular-nums}
.risultato .conv{display:flex;align-items:flex-start;gap:8px;font-size:.95rem;font-weight:700;margin-top:12px;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:8px 12px;line-height:1.45;color:var(--ink);font-variant-numeric:tabular-nums}
.risultato .conv .ico{color:var(--gold-ink);margin-top:.15em}
.esito{display:flex;gap:10px;align-items:flex-start;margin:0 0 14px;padding:11px 14px;border-radius:var(--r-s);font-weight:600;font-size:.93rem;line-height:1.45;border:1px solid transparent}
.esito .ico{width:1.3em;height:1.3em;margin-top:.05em}
.esito.si{background:var(--ok-2);color:var(--ok);border-color:color-mix(in srgb,var(--ok) 30%,transparent)}
.esito.no{background:var(--no-2);color:var(--no);border-color:color-mix(in srgb,var(--no) 30%,transparent)}
.esito.warn{background:var(--warn-2);color:var(--ink);border-color:color-mix(in srgb,var(--warn) 30%,transparent)}
.esito.warn .ico{color:var(--warn)}
details.r-come{margin-top:14px;border-top:1px dashed var(--line-2);padding-top:6px;font-size:.88rem;color:var(--ink-2)}
details.r-come summary{cursor:pointer;font-weight:600;color:var(--ink);padding:6px 0;list-style:none;display:flex;align-items:center;gap:8px}
details.r-come summary::-webkit-details-marker{display:none}
details.r-come summary::after{content:"+";margin-left:auto;color:var(--accent);font-size:1.15rem}
details.r-come[open] summary::after{content:"–"}
details.r-come ul{margin:4px 0 6px;padding-left:18px}
.formula{font-size:.92rem;color:var(--ink-2);margin:8px 0 0}
.calc-link{margin:12px 0 0;font-weight:600;font-size:.9rem}
.tab{overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid var(--line);border-radius:var(--r);background:var(--card);box-shadow:var(--sh-1)}
table{border-collapse:collapse;width:100%;font-size:.92rem}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
td.n,th.n{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
th{background:var(--mute);font-size:.76rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2)}
tbody tr:nth-child(even) td{background:color-mix(in srgb,var(--mute) 45%,transparent)}
tr:last-child td{border-bottom:0}
@media (max-width:640px){.tab td,.tab th{min-width:120px}.tab td:first-child,.tab th:first-child{min-width:150px}}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}
.griglia a{display:flex;gap:12px;align-items:flex-start;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:13px 14px;text-decoration:none;color:var(--ink);font-weight:700;min-width:0;overflow-wrap:anywhere;box-shadow:var(--sh-1);transition:border-color .15s,box-shadow .15s,transform .15s}
.griglia a>span{min-width:0}
.griglia a small{display:block;font-weight:400;color:var(--ink-3);font-size:.85rem;margin-top:2px;font-variant-numeric:tabular-nums}
.griglia a:hover{border-color:var(--accent);box-shadow:var(--sh-2);transform:translateY(-1px);color:var(--ink)}
.griglia .ic,.cat .ic{display:grid;place-items:center;width:38px;height:38px;border-radius:10px;background:var(--accent-2);color:var(--accent);flex:none}
.griglia .ic.g{background:var(--gold-2);color:var(--gold-ink)}
.griglia .ic.f{background:none;position:relative;width:42px;height:38px;place-items:start center;padding-top:5px}
.flag{display:block;width:36px;height:24px;border-radius:4px;box-shadow:0 0 0 1px rgba(0,0,0,.14),0 1px 2px rgba(0,0,0,.12);overflow:hidden}
.griglia .ic .mini{position:absolute;right:-2px;bottom:-4px;display:grid;place-items:center;width:20px;height:20px;border-radius:6px;background:var(--card);color:var(--accent);box-shadow:0 0 0 1px var(--line)}
.griglia .ic .mini .ico{width:13px;height:13px}
.sel-f{position:relative;display:block}
.sel-f select{padding-left:52px}
.sel-flag{position:absolute;left:12px;top:50%;transform:translateY(-50%);pointer-events:none;display:flex}.sel-flag .flag{width:27px;height:18px;border-radius:3px}
.verdetto{display:flex;align-items:center;gap:10px;font-family:var(--serif);font-weight:700;font-size:clamp(1.35rem,3.4vw,1.6rem);line-height:1.2;letter-spacing:-.01em;margin:0 0 10px;font-variant-numeric:tabular-nums}
.verdetto .ico{width:1.15em;height:1.15em;flex:none;stroke-width:2.4}
.verdetto.si{color:var(--ok)}.verdetto.no{color:var(--no)}.verdetto.warn{color:var(--ink)}.verdetto.warn .ico{color:var(--warn)}
.cmp{display:grid;gap:6px;margin:0 0 10px}
.cmp-r{display:grid;grid-template-columns:64px 1fr auto;align-items:center;gap:8px;font-size:.8rem;color:var(--ink-3);font-variant-numeric:tabular-nums}
.cmp-r em{font-style:normal;font-weight:700;color:var(--ink-2)}
.cmp-b{display:block;height:10px;border-radius:999px}
.cmp-b.tu{background:var(--accent)}.cmp-b.min{background:var(--gold)}
.v-det{font-size:.85rem;color:var(--ink-2);margin:0 0 16px;padding-bottom:14px;border-bottom:1px dashed var(--line-2);line-height:1.5}
.r-bar{position:fixed;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom));z-index:30;display:flex;align-items:center;gap:10px;font:inherit;text-align:left;cursor:pointer;background:#141A33;color:#EEF0F8;border:1px solid #343D63;border-top:3px solid #E0A526;border-radius:14px;padding:10px 16px;min-height:52px;box-shadow:0 12px 30px -8px rgba(0,0,0,.45)}
.r-bar-tot{font-family:var(--serif);font-weight:700;font-size:1.08rem;font-variant-numeric:tabular-nums;white-space:nowrap}
.r-bar-info{flex:1;min-width:0;font-size:.85rem;opacity:.8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.r-bar-go{display:inline-flex;align-items:center;gap:4px;font-weight:700;font-size:.85rem;color:#E0A526}
@media (min-width:881px){.r-bar{display:none!important}}
.cat{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:0;padding:0;list-style:none}
.cat li{background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:14px;font-size:.88rem;color:var(--ink-2);box-shadow:var(--sh-1)}
.cat strong{display:block;color:var(--ink);font-size:.97rem;margin-top:8px}
.testo p,.testo li{max-width:760px}
.fonti li{margin-bottom:8px;overflow-wrap:anywhere}
.form{display:grid;gap:14px}
.form label{display:grid;gap:6px;font-weight:600;font-size:.95rem}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:400;font-size:.9rem;color:var(--ink-2)}
.form .check input{width:auto;min-height:0;margin-top:4px}
.btn{font:inherit;font-weight:700;background:var(--accent);color:var(--on-accent);border:0;border-radius:var(--r-s);padding:12px 22px;cursor:pointer;min-height:46px}
.btn:hover{background:var(--accent-h)}
.btn:disabled{opacity:.6;cursor:wait}
.hp{position:absolute;left:-9999px}
.ok{background:var(--ok-2);border:1px solid var(--ok);padding:14px;border-radius:var(--r-s)}
.errore{color:var(--warn);font-weight:600}
.ad-slot:empty{display:none}
.briciole{font-size:.85rem;color:var(--ink-3);margin-top:18px}
.briciole a{color:var(--ink-3)}
.indice{border:1px solid var(--line);border-left:4px solid var(--gold);padding:14px 16px;background:var(--card);border-radius:var(--r-s);margin:12px 0;box-shadow:var(--sh-1)}
footer{margin-top:64px;background:var(--navy);color:var(--on-navy-2);font-size:.88rem;padding:40px 0 34px;border-top:3px solid var(--gold)}
footer a{color:var(--on-navy)}
footer a:hover{color:var(--gold)}
footer .f-grid{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:28px}
footer .logo{margin-bottom:12px}
footer p{margin:0 0 10px;max-width:660px}
footer strong{color:var(--on-navy)}
footer ul{list-style:none;margin:0;padding:0;display:grid;gap:8px}
footer h2{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-size:.76rem;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);margin:4px 0 12px}
footer .f-base{border-top:1px solid rgba(255,255,255,.12);margin-top:24px;padding-top:16px;font-size:.82rem;max-width:none}
footer .f-altri{border-top:1px solid rgba(255,255,255,.12);margin-top:24px;padding-top:18px}
footer .f-altri h2{margin:0 0 10px}
footer .f-altri ul{gap:6px}
footer .f-altri li{max-width:660px}
footer .f-altri a{font-weight:600}
@media (max-width:880px){.calc-grid{grid-template-columns:1fr}.calc-out{border-left:0;border-top:1px solid var(--line)}.band-deco{display:none}.cat{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:1020px){nav.menu{display:none}.nav-m{display:block}}
@media (max-width:760px){nav.menu{display:none}.nav-m{display:block}header.top .wrap{min-height:60px}
.calc form,.calc-out{padding:18px}footer .f-grid{grid-template-columns:1fr}.band-in{padding-top:24px}.band{background:linear-gradient(180deg,var(--navy) 0,var(--navy-2) 80%,var(--bg) 80%)}}
@media (max-width:420px){.calc .campi{grid-template-columns:1fr 1fr;gap:12px}.calc .campi>label[data-campo=paese],.calc .campi>label[data-campo=programma],.calc .campi>label.l-red,.calc .campi>label.l-val{grid-column:1/-1}.summary .s-body{padding:18px}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
.tab.compatta td,.tab.compatta th{min-width:0}
.tab.compatta th{vertical-align:bottom}
.tab.compatta th .small{font-weight:600;letter-spacing:0;text-transform:none}
@media (max-width:640px){.tab.compatta td,.tab.compatta th{padding:9px 8px}.tab.compatta td:first-child,.tab.compatta th:first-child{min-width:118px}}
@media (max-width:640px){.tab.motivi td,.tab.motivi th{padding:9px 4px;font-size:.86rem}.tab.motivi th{letter-spacing:0}.tab.motivi td:first-child,.tab.motivi th:first-child{min-width:0;padding-left:10px}}
th button.ord{font:inherit;color:inherit;letter-spacing:inherit;text-transform:inherit;text-align:inherit;background:none;border:0;padding:0;cursor:pointer;display:inline-flex;align-items:center;gap:5px}
th button.ord::after{content:"";width:7px;height:10px;flex:none;opacity:.45;background:currentColor;-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 7 10'%3E%3Cpath d='M3.5 0 7 4H0zM3.5 10 0 6h7z'/%3E%3C/svg%3E") center/contain no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 7 10'%3E%3Cpath d='M3.5 0 7 4H0zM3.5 10 0 6h7z'/%3E%3C/svg%3E") center/contain no-repeat}
th[aria-sort] button.ord{color:var(--accent)}
th[aria-sort] button.ord::after{opacity:1}
th[aria-sort=ascending] button.ord::after{-webkit-mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 7 10'%3E%3Cpath d='M3.5 2 7 7H0z'/%3E%3C/svg%3E");mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 7 10'%3E%3Cpath d='M3.5 2 7 7H0z'/%3E%3C/svg%3E")}
th[aria-sort=descending] button.ord::after{-webkit-mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 7 10'%3E%3Cpath d='M3.5 8 0 3h7z'/%3E%3C/svg%3E");mask-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 7 10'%3E%3Cpath d='M3.5 8 0 3h7z'/%3E%3C/svg%3E")}
.tb{display:inline-block;width:52px;height:6px;border-radius:99px;background:var(--mute);margin-right:8px;vertical-align:middle;overflow:hidden;box-shadow:inset 0 0 0 1px var(--line)}
.tb i{display:block;height:100%;background:var(--accent);border-radius:99px}
.tv{display:inline-block;min-width:3.9em;text-align:right}
tr.poco td{color:var(--ink-3)}
tr.tot-r td{font-weight:700;border-top:2px solid var(--line-2)}
.kpi{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:10px 0 2px}
.kpi div{background:var(--paper);border:1px solid var(--line);border-radius:var(--r-s);padding:11px 13px;min-width:0}
.kpi b{display:block;font-family:var(--serif);font-size:clamp(1.1rem,2.6vw,1.4rem);line-height:1.2;font-variant-numeric:tabular-nums;color:var(--ink);overflow-wrap:anywhere}
.kpi span{display:block;font-size:.8rem;color:var(--ink-3);font-weight:600;margin-top:2px;line-height:1.35}
.kpi-uk{grid-template-columns:repeat(auto-fit,minmax(150px,max-content));margin:8px 0 0}
#t-uk th{white-space:normal}#t-uk td,#t-uk th{padding:9px 8px}#t-uk .tb{display:none}
table.larga th{white-space:normal}table.larga td,table.larga th{padding:9px 8px}table.larga td:not(:nth-child(2)) .tb{display:none}
.cifra-2{margin-top:14px;padding-top:12px;border-top:1px dashed var(--line-2)}
.cifra-2 strong{font-size:clamp(1.25rem,3.2vw,1.6rem)}
.due{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}
.due h3{margin-top:4px}
.classifica{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.classifica li{display:grid;grid-template-columns:26px minmax(0,1fr) auto;gap:10px;align-items:center;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:10px 14px;box-shadow:var(--sh-1)}
.classifica .pos{font-family:var(--serif);font-weight:700;color:var(--gold-ink);font-size:1.05rem}
.classifica a{font-weight:700}
.classifica small{display:block;color:var(--ink-3);font-size:.8rem}
.classifica .bar{display:block;height:6px;border-radius:99px;background:var(--mute);margin-top:6px;overflow:hidden}
.classifica .bar i{display:block;height:100%;background:var(--accent);border-radius:99px}
.classifica .bar.basso i{background:var(--ok)}.classifica .bar.alto i{background:var(--no)}
.classifica .v{font-family:var(--serif);font-weight:700;font-size:1.15rem;font-variant-numeric:tabular-nums}
.filtro{margin:0 0 10px;max-width:420px}
.filtro input{font:inherit;font-size:1rem;color:var(--ink);background:var(--card);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:10px 12px;width:100%;min-height:46px}
.filtro input:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 20%,transparent)}
.trim{list-style:none;margin:8px 0 0;padding:16px 14px 12px;display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:8px;background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-1)}
.trim li{display:flex;flex-direction:column;align-items:center;gap:6px;min-width:0;text-align:center}
.trim .tq-v{font-size:.78rem;font-weight:700;font-variant-numeric:tabular-nums;color:var(--ink-2);white-space:nowrap}
.trim .tq-c{display:flex;align-items:flex-end;height:110px;width:100%;max-width:44px;background:var(--mute);border-radius:6px 6px 0 0;overflow:hidden}
.trim .tq-b{display:block;width:100%;background:linear-gradient(180deg,var(--accent),color-mix(in srgb,var(--accent) 70%,var(--card)));border-radius:6px 6px 0 0}
.trim .tq-l{font-size:.74rem;color:var(--ink-3);line-height:1.25}
.aff-r{margin-top:28px;border-left:4px solid var(--gold)}
.aff-r-t{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.aff-r-t h2{margin:0;font-size:1.2rem;flex:1;min-width:200px}
.aff-r-t .ic{display:grid;place-items:center;width:40px;height:40px;border-radius:10px;background:var(--gold-2);color:var(--gold-ink);flex:none}
.aff-tag{font-size:.72rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);border:1px solid var(--line-2);border-radius:6px;padding:2px 8px}
.aff-r-cta{margin:14px 0 10px}
a.btn{display:inline-flex;align-items:center;gap:8px;text-decoration:none;color:var(--on-accent)}
a.btn:hover{color:var(--on-accent)}
.cerca{margin-bottom:26px;box-shadow:var(--sh-2);max-width:760px}
.cerca label .lt{display:flex;align-items:center;gap:8px;font-weight:700;color:var(--ink)}
.cerca .lt .ico{color:var(--accent)}
.vai-r{margin-top:8px}
.vai-r select{font:inherit;font-size:1.02rem;color:var(--ink);background:var(--card);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:11px 12px;width:100%;min-height:48px}
.vai-r select:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 20%,transparent)}
.s-top .flag{width:24px;height:16px;border-radius:3px}
ul.testo{padding-left:20px}
@media (max-width:760px){.kpi{grid-template-columns:repeat(2,minmax(0,1fr))}.due{grid-template-columns:1fr}}
@media (max-width:480px){.tb{display:none}.trim{gap:4px;padding:14px 8px 10px}.trim .tq-v{font-size:.68rem}}
.trim.m12{grid-template-columns:repeat(12,minmax(0,1fr));gap:6px}
@media (max-width:760px){.trim.m12{grid-template-columns:repeat(6,minmax(0,1fr));row-gap:16px}.trim.m12 .tq-c{height:84px}}
.kpi-uk a{color:inherit}
.cosa{margin:22px 0;border-left:4px solid var(--accent)}.cosa h2{margin-top:0;font-size:1.2rem}.cosa ul{margin:0;padding-left:20px}.cosa li{margin-bottom:6px}
.griglia .no-link{display:flex;gap:12px;align-items:flex-start;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:13px 14px;color:var(--ink);font-weight:700;min-width:0;box-shadow:var(--sh-1)}
.griglia .no-link>span{min-width:0}.griglia .no-link small{display:block;font-weight:400;color:var(--ink-3);font-size:.85rem;margin-top:2px}
td sup{font-size:.68em;color:var(--ink-3);margin-left:2px}
"""

ICONE = {
    "passport": '<rect x="4.5" y="2.5" width="15" height="19" rx="2"/><circle cx="12" cy="10" r="3.5"/><path d="M8.5 10h7M12 6.5c1 1 1.4 2.2 1.4 3.5s-.4 2.5-1.4 3.5c-1-1-1.4-2.2-1.4-3.5s.4-2.5 1.4-3.5zM9 17.5h6"/>',
    "briefcase": '<rect x="2.5" y="7" width="19" height="13.5" rx="2"/><path d="M8.5 7V5a1.5 1.5 0 0 1 1.5-1.5h4A1.5 1.5 0 0 1 15.5 5v2"/><path d="M2.5 12.5h19"/><path d="M11 12.5h2v2h-2z"/>',
    "laptop": '<rect x="4" y="4.5" width="16" height="11" rx="1.5"/><path d="M2 19.5h20"/><path d="M9 8.5l-2 2 2 2M15 8.5l2 2-2 2"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6 6 6M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4"/>',
    "family": '<circle cx="8" cy="6.5" r="2.5"/><circle cx="16" cy="6.5" r="2.5"/><circle cx="12" cy="13" r="2"/><path d="M4 21v-6.5A2.5 2.5 0 0 1 6.5 12h3M20 21v-6.5a2.5 2.5 0 0 0-2.5-2.5h-3"/><path d="M9.5 21v-2.5a2.5 2.5 0 0 1 5 0V21"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1"/>',
    "child": '<circle cx="12" cy="6" r="3"/><path d="M8 21v-5l-2-3 3-3h6l3 3-2 3v5"/>',
    "coins": '<ellipse cx="9" cy="6.5" rx="6" ry="3"/><path d="M3 6.5v4c0 1.7 2.7 3 6 3s6-1.3 6-3v-4"/><path d="M9 13.5v4c0 1.7 2.7 3 6 3s6-1.3 6-3v-4c0-1.6-2.4-2.9-5.5-3"/>',
    "exchange": '<path d="M4 8h13l-3.5-3.5M20 16H7l3.5 3.5"/>',
    "wallet": '<path d="M19 7V5.5A1.5 1.5 0 0 0 17.5 4h-12A2.5 2.5 0 0 0 3 6.5v11A2.5 2.5 0 0 0 5.5 20h14a1.5 1.5 0 0 0 1.5-1.5V9a1.5 1.5 0 0 0-1.5-1.5H5.5A2.5 2.5 0 0 1 3 6.5"/><path d="M16.5 13.5h.01"/>',
    "calendar": '<rect x="3" y="4.5" width="18" height="17" rx="2.5"/><path d="M16 2.5v4M8 2.5v4M3 10h18"/>',
    "globe": '<circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19"/><path d="M12 2.5c2.6 2.6 4 6 4 9.5s-1.4 6.9-4 9.5c-2.6-2.6-4-6-4-9.5s1.4-6.9 4-9.5z"/>',
    "list": '<path d="M9 6h11M9 12h11M9 18h11M4.5 6h.01M4.5 12h.01M4.5 18h.01"/>',
    "shield": '<path d="M12 22s8-3.5 8-10V5.5L12 2.5 4 5.5V12c0 6.5 8 10 8 10z"/><path d="M8.5 12l2.5 2.5 4.5-4.5"/>',
    "check": '<circle cx="12" cy="12" r="9.5"/><path d="M8 12.5l2.7 2.7L16 10"/>',
    "x": '<circle cx="12" cy="12" r="9.5"/><path d="M9 9l6 6M15 9l-6 6"/>',
    "alert": '<path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17h.01"/>',
    "calc": '<rect x="4.5" y="2.5" width="15" height="19" rx="2.5"/><path d="M8 7h8M8 12h.01M12 12h.01M16 12h.01M8 16h.01M12 16h.01M16 16h.01"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "scale": '<path d="M12 3v18M7 21h10M4 7h16"/><path d="M6.5 7 4 13a3 3 0 0 0 5 0zM17.5 7 15 13a3 3 0 0 0 5 0z"/>',
}
ICONA_CATEGORIA = {"digital-nomad": "laptop", "passive-income": "sun", "work": "briefcase", "family": "family"}


# Bandiere semplificate (SVG in linea, 3:2) per le schede dei paesi e dei visti e accanto al menu "Country"
_B = {
    "Austria": '<path fill="#C8102E" d="M0 0h30v20H0z"/><path fill="#fff" d="M0 6.67h30v6.66H0z"/>',
    "Croatia": '<path fill="#fff" d="M0 0h30v20H0z"/><path fill="#D52B1E" d="M0 0h30v6.67H0z"/><path fill="#0B3D91" d="M0 13.33h30V20H0z"/>'
               '<path fill="#fff" stroke="#D52B1E" stroke-width=".6" d="M12 5.5h6v6.5a3 3 0 0 1-6 0z"/><path fill="#D52B1E" d="M12 5.5h2v2h-2zM16 5.5h2v2h-2zM14 7.5h2v2h-2zM12 9.5h2v2h-2zM16 9.5h2v2h-2z"/>',
    "Denmark": '<path fill="#C8102E" d="M0 0h30v20H0z"/><path fill="#fff" d="M9 0h3.5v20H9zM0 8.25h30v3.5H0z"/>',
    "France": '<path fill="#fff" d="M0 0h30v20H0z"/><path fill="#0055A4" d="M0 0h10v20H0z"/><path fill="#EF4135" d="M20 0h10v20H20z"/>',
    "Germany": '<path fill="#000" d="M0 0h30v6.67H0z"/><path fill="#DD0000" d="M0 6.67h30v6.66H0z"/><path fill="#FFCE00" d="M0 13.33h30V20H0z"/>',
    "Hungary": '<path fill="#CE2939" d="M0 0h30v6.67H0z"/><path fill="#fff" d="M0 6.67h30v6.66H0z"/><path fill="#477050" d="M0 13.33h30V20H0z"/>',
    "Ireland": '<path fill="#fff" d="M0 0h30v20H0z"/><path fill="#169B62" d="M0 0h10v20H0z"/><path fill="#FF883E" d="M20 0h10v20H20z"/>',
    "Italy": '<path fill="#fff" d="M0 0h30v20H0z"/><path fill="#009246" d="M0 0h10v20H0z"/><path fill="#CE2B37" d="M20 0h10v20H20z"/>',
    "Netherlands": '<path fill="#AE1C28" d="M0 0h30v6.67H0z"/><path fill="#fff" d="M0 6.67h30v6.66H0z"/><path fill="#21468B" d="M0 13.33h30V20H0z"/>',
    "Portugal": '<path fill="#DA291C" d="M0 0h30v20H0z"/><path fill="#046A38" d="M0 0h12v20H0z"/><circle cx="12" cy="10" r="4" fill="#FFE900" stroke="#DA291C" stroke-width=".5"/>'
                '<path fill="#fff" stroke="#DA291C" stroke-width=".5" d="M10.4 8h3.2v2.6a1.6 1.6 0 0 1-3.2 0z"/>',
    "Spain": '<path fill="#AA151B" d="M0 0h30v20H0z"/><path fill="#F1BF00" d="M0 5h30v10H0z"/>',
    "Sweden": '<path fill="#006AA7" d="M0 0h30v20H0z"/><path fill="#FECC00" d="M9 0h3.5v20H9zM0 8.25h30v3.5H0z"/>',
    "United Kingdom": '<path fill="#012169" d="M0 0h30v20H0z"/><path stroke="#fff" stroke-width="4" d="M0 0l30 20M30 0L0 20"/>'
                      '<path stroke="#C8102E" stroke-width="1.6" d="M0 0l30 20M30 0L0 20"/><path stroke="#fff" stroke-width="6" d="M15 0v20M0 10h30"/>'
                      '<path stroke="#C8102E" stroke-width="3.4" d="M15 0v20M0 10h30"/>',
}


def bandiera(paese, cls="flag"):
    corpo = _B.get(paese)
    if not corpo:
        return ico("globe")
    return f'<svg class="{cls}" viewBox="0 0 30 20" aria-hidden="true" focusable="false">{corpo}</svg>'


def ico(nome, cls="ico"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="#i-{nome}"/></svg>'


SPRITE = ('<svg xmlns="http://www.w3.org/2000/svg" style="display:none">' +
          "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONE.items()) + "</svg>")
# Marchio: passaporto blu notte su tessera oro (stesso disegno nel favicon e nell'immagine Open Graph)
_M = ('<rect width="40" height="40" rx="9" fill="#E0A526"/><rect x="11" y="7" width="18" height="26" rx="2.5" fill="#141B33"/>'
      '<circle cx="20" cy="17" r="5" fill="none" stroke="#E0A526" stroke-width="1.8"/><path d="M15 17h10M20 12c1.6 1.5 2.2 3.2 2.2 5s-.6 3.5-2.2 5c-1.6-1.5-2.2-3.2-2.2-5s.6-3.5 2.2-5z" fill="none" stroke="#E0A526" stroke-width="1.4"/>'
      '<path d="M15.5 27.5h9" stroke="#E0A526" stroke-width="1.8" stroke-linecap="round"/>')
MARCHIO = f'<svg viewBox="0 0 40 40" aria-hidden="true" focusable="false">{_M}</svg>'
FAVICON = "data:image/svg+xml," + (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'>{_M}</svg>"
                                    .replace('"', "'").replace("#", "%23").replace("<", "%3C").replace(">", "%3E"))
DECO = ('<svg class="band-deco" viewBox="0 0 230 150" aria-hidden="true" focusable="false">'
        '<circle cx="115" cy="66" r="58" fill="none" stroke="#E0A526" stroke-opacity=".75" stroke-width="2" stroke-dasharray="4 7"/>'
        '<circle cx="115" cy="66" r="40" fill="none" stroke="#E0A526" stroke-opacity=".9" stroke-width="2"/>'
        '<path d="M83 66h64M115 34c10 9 14 20 14 32s-4 23-14 32c-10-9-14-20-14-32s4-23 14-32z" fill="none" stroke="#E0A526" stroke-opacity=".9" stroke-width="2"/>'
        '<text x="115" y="143" text-anchor="middle" font-family="ui-monospace,monospace" font-size="10" letter-spacing="2.5" fill="#E0A526" fill-opacity=".9">OFFICIAL · MINIMUM</text></svg>')
DECO_STAT = DECO.replace("OFFICIAL · MINIMUM", "OFFICIAL · STATISTICS")


def h1_diviso(testo):
    """H1 identico nel testo (per i motori di ricerca), diviso in due righe visive al primo ': '."""
    if ": " not in testo:
        return f"<h1>{escape(testo)}</h1>"
    a, b = testo.split(": ", 1)
    return f'<h1><span class="h1-a">{escape(a)}</span><span class="sr">: </span><span class="h1-b">{escape(b)}</span></h1>'


# Motore di calcolo in JS: deve dare gli stessi risultati di calcola() e converti() (verifica.py li confronta).
MOTORE_JS = r"""
var DEC={"IDR":0,"JPY":0,"KRW":0,"ISK":0,"HUF":0};
var LIMITI={adulti:[1,20],figli:[0,20],pagamenti:[12,14]};
function r2(x){return Math.floor(x*100+0.5+1e-9)/100;}
function arrot(x,c){return DEC[c]===0?Math.floor(x+0.5+1e-9):r2(x);}
function limita(n,x){var l=LIMITI[n],v=parseInt(x,10);if(isNaN(v))v=l[0];return Math.max(l[0],Math.min(l[1],v));}
function grp(n,dec){var s=dec?r2(n).toFixed(2):String(Math.floor(n+0.5+1e-9));var p=s.split('.');p[0]=p[0].replace(/\B(?=(\d{3})+(?!\d))/g,',');return p.join('.');}
function soldi(v,c){var t=grp(v,DEC[c]===0?0:2);if(t.slice(-3)==='.00')t=t.slice(0,-3);return c==='EUR'?'€'+t:(c==='GBP'?'£'+t:c+' '+t);}
function unita(D,V){var b=V.base,s=b.indice?D.indici[b.indice]:b;var per=s.periodo;return [s.valore,s.valuta,per,per==='month'?(s.pagamenti||12):12];}
function calcola(D,P,vid,adulti,figli){
  var V=null;P.varianti.forEach(function(v){if(v.id===vid)V=v;});if(!V)V=P.varianti[0];
  var uu=unita(D,V),u=uu[0],val=uu[1],per=uu[2],np=uu[3];adulti=limita('adulti',adulti);figli=limita('figli',figli);
  var righe=[],pr=r2(u*V.fattore);righe.push(['main',1,pr,pr]);var fam=V.famiglia,tp=fam.tipo,aa=adulti-1,ign=false,a,b,n;
  if(tp==='tutti'){n=aa+figli;if(n>=1){a=r2(u*fam.primo);righe.push(['first',1,a,a]);}if(n>=2){b=r2(u*fam.altri);righe.push(['other',n-1,b,r2(b*(n-1))]);}}
  else if(tp==='per_eta'){if(aa){a=r2(u*fam.adulto);righe.push(['adult',aa,a,r2(a*aa)]);}if(figli){b=r2(u*fam.figlio);righe.push(['child',figli,b,r2(b*figli)]);}}
  else if(tp==='figli'){if(figli>=1){a=r2(u*fam.primo);righe.push(['firstchild',1,a,a]);}if(figli>=2){b=r2(u*fam.altri);righe.push(['otherchild',figli-1,b,r2(b*(figli-1))]);}}
  else if(tp==='nessuno'){ign=aa>0||figli>0;}
  var tot=r2(righe.reduce(function(s,r){return s+r[3];},0)),cap=false;
  if(V.tetto!==undefined&&V.tetto!==null){var c=r2(u*V.tetto);if(tot>c){tot=c;cap=true;}}
  var m,y,m12;if(per==='month'){m=tot;y=r2(tot*np);m12=r2(y/12);}else{y=tot;m=r2(tot/12);m12=m;}
  return {valuta:val,periodo:per,pagamenti:np,righe:righe,totale:tot,mensile:m,annuale:y,mensile12:m12,familiari_ignorati:ign,motivo:fam.motivo||'',tetto:cap,unita:u,V:V,adulti:adulti,figli:figli};}
function converti(x,da,a,T){if(da===a)return arrot(x,a);var e=da==='EUR'?x:x/T[da];return arrot(a==='EUR'?e:e*T[a],a);}
function convertiScalato(x,da,a,T,mo,di){var c=converti(x,da,a,T);mo=mo||1;di=di||1;return (mo===1&&di===1)?c:arrot(c*mo/di,a);}
function convertiImporti(o,a,T){var v=o.valuta,cm,cy;
  if(o.periodo==='month'){cm=converti(o.mensile,v,a,T);cy=arrot(cm*o.pagamenti,a);return {mensile:cm,annuale:cy,mensile12:o.pagamenti!==12?arrot(cy/12,a):cm};}
  cy=converti(o.annuale,v,a,T);cm=arrot(cy/12,a);return {mensile:cm,annuale:cy,mensile12:cm};}
function esito(P,o,reddito,pagamenti,valuta,T){
  if(P.esito===false||!(reddito>0))return 'nd';var k=limita('pagamenti',pagamenti);var x=converti(reddito,valuta,o.valuta,T);var anno=r2(x*k);
  var modo=P.confronto||(o.periodo==='month'?'mese':'anno');
  if(modo==='mese')return x>=o.mensile?'si':'no';if(modo==='anno')return anno>=o.annuale?'si':'no';
  var a=x>=o.mensile,b=anno>=o.annuale;return (a&&b)?'si':((!a&&!b)?'no':'parziale');}
"""

APP_JS = r"""
(function(){
  var MESI=['January','February','March','April','May','June','July','August','September','October','November','December'];
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function dl(iso){var p=iso.split('-');return (+p[2])+' '+MESI[+p[1]-1]+' '+p[0];}
  function num(v){return String(Math.round(v*1e6)/1e6);}
  function cap(t){t=String(t||'');return t.charAt(0).toUpperCase()+t.slice(1);}
  var D=JSON.parse(document.getElementById('dati-visti').textContent);
  var CAMBI=D.cambi;
  function etich(V,f){var b=V.base,uu=unita(D,V),u=uu[0],val=uu[1],per=uu[2],np=uu[3];
    if(b.indice){var I=D.indici[b.indice];var q=per==='month'?('a month'+(np!==12?' × '+np+' payments':'')):'a year';
      return (f>=1?num(f)+' × the '+I.nome_breve:num(Math.round(f*100*1e6)/1e6)+'% of the '+I.nome_breve)+' ('+soldi(u,val)+' '+q+')';}
    if(u===1)return soldi(f,val);return b.etichetta+': '+soldi(u*f,val);}
  function testo(V,r){var f=V.famiglia,k=r[0];
    if(k==='main')return (V.etichetta_principale||'Main applicant')+': '+etich(V,V.fattore);if(k==='first')return 'First family member: '+etich(V,f.primo);
    if(k==='other')return 'Each further family member: '+etich(V,f.altri);if(k==='adult')return 'Each further adult: '+etich(V,f.adulto);
    if(k==='child')return 'Each child: '+etich(V,f.figlio);if(k==='firstchild')return 'First child: '+etich(V,f.primo);
    if(k==='otherchild')return 'Each further child: '+etich(V,f.altri);return k;}
  function aggiornaStatici(){
    document.querySelectorAll('[data-importo]').forEach(function(el){var a=el.getAttribute('data-a');if(!CAMBI.tassi[a]&&a!=='EUR')return;
      el.textContent=soldi(convertiScalato(+el.getAttribute('data-importo'),el.getAttribute('data-da'),a,CAMBI.tassi,+(el.getAttribute('data-molt')||1),+(el.getAttribute('data-div')||1)),a);});
    document.querySelectorAll('[data-cambi-data]').forEach(function(el){el.textContent=dl(CAMBI.data);});}
  function monta(box){
    var f=box.querySelector('form');var q=function(n){return f.querySelector('[name='+n+']');};
    var selP=q('paese'),selG=q('programma'),selV=q('variante'),selC=q('valuta');
    var fisso=box.getAttribute('data-programma');
    var paesi=[];D.programmi.forEach(function(P){if(paesi.indexOf(P.paese)<0)paesi.push(P.paese);});
    selP.innerHTML=paesi.map(function(p){return '<option>'+esc(p)+'</option>';}).join('');
    var vals=['EUR'].concat(Object.keys(CAMBI.tassi).sort());
    selC.innerHTML=vals.map(function(c){return '<option value="'+c+'">'+c+' – '+esc(D.nomi_valute[c]||c)+'</option>';}).join('');
    selC.value=box.getAttribute('data-valuta')||'USD';
    function prog(){var s=selG.value;for(var i=0;i<D.programmi.length;i++)if(D.programmi[i].slug===s)return D.programmi[i];return D.programmi[0];}
    function riempiG(){var p=selP.value;selG.innerHTML=D.programmi.filter(function(P){return P.paese===p;}).map(function(P){return '<option value="'+P.slug+'">'+esc(cap(P.nome))+'</option>';}).join('');
      var fl=box.querySelector('[data-flag]');if(fl)fl.innerHTML=(D.bandiere||{})[p]||'';}
    function riempiV(){var P=prog();selV.innerHTML=P.varianti.map(function(V){return '<option value="'+V.id+'">'+esc(V.nome)+'</option>';}).join('');
      f.querySelector('[data-campo=variante]').hidden=P.varianti.length<2;}
    if(fisso){var P0=null;D.programmi.forEach(function(P){if(P.slug===fisso)P0=P;});selP.value=P0.paese;riempiG();selG.value=fisso;
      f.querySelector('[data-campo=paese]').hidden=true;f.querySelector('[data-campo=programma]').hidden=true;}
    else{selP.value=box.getAttribute('data-paese')||paesi[0];riempiG();}
    riempiV();
    function calcolaOra(ev){
      var P=prog(),V=null;P.varianti.forEach(function(v){if(v.id===selV.value)V=v;});V=V||P.varianti[0];
      var avvisi=[];
      [['adulti','Adults'],['figli','Children']].forEach(function(c){var el=q(c[0]),raw=el.value,v=limita(c[0],raw);
        if(String(v)!==String(raw).trim()){avvisi.push(c[1]+' set to '+v+' (allowed: '+LIMITI[c[0]][0]+'–'+LIMITI[c[0]][1]+').');if(ev&&ev.type==='change')el.value=v;}});
      var o=calcola(D,P,V.id,q('adulti').value,q('figli').value),cur=selC.value,val=o.valuta,cv=convertiImporti(o,cur,CAMBI.tassi);
      function ic(n){return '<svg class="ico" aria-hidden="true" focusable="false"><use href="#i-'+n+'"/></svg>';}
      var h='',mio=parseFloat(q('reddito').value),k=limita('pagamenti',q('pagamenti').value),barTot='',barInfo='';
      if(mio>0){var e=esito(P,o,mio,k,cur,CAMBI.tassi);var mioV=converti(mio,cur,val,CAMBI.tassi),annoV=r2(mioV*k);
        var tuo='Your income of '+soldi(mio,cur)+' a month × '+k+' (≈ '+soldi(mioV,val)+' a month, '+soldi(annoV,val)+' a year)';
        var modo=P.confronto||(o.periodo==='month'?'mese':'anno'),mese=modo!=='anno';
        var tuoX=mese?mioV:annoV,sogliaX=mese?o.mensile:o.annuale,diff=Math.abs(r2(tuoX-sogliaX)),quando=mese?' a month':' a year';
        var barra=function(){var mx=Math.max(tuoX,sogliaX)||1;return '<div class="cmp" aria-hidden="true"><div class="cmp-r"><span>You</span><b class="cmp-b tu" style="width:'+Math.max(2,Math.round(tuoX/mx*100))+'%"></b><em>'+soldi(tuoX,val)+'</em></div>'+
          '<div class="cmp-r"><span>Minimum</span><b class="cmp-b min" style="width:'+Math.max(2,Math.round(sogliaX/mx*100))+'%"></b><em>'+soldi(sogliaX,val)+'</em></div></div>';};
        if(e==='nd')h+='<div class="esito warn">'+ic('alert')+'<span>'+esc(P.condizioni||'')+'</span></div>';
        else if(e==='si'){h+='<div class="verdetto si">'+ic('check')+'<span>You meet the minimum'+(diff>0?' by '+soldi(diff,val)+quando:'')+'</span></div>'+barra()+'<p class="v-det">'+tuo+' is at or above this minimum. The consulate still assesses your documents.</p>';
          barTot='✓ Meets the minimum';}
        else if(e==='parziale'){h+='<div class="verdetto warn">'+ic('alert')+'<span>Meets one form of the amount, not the other</span></div>'+barra()+'<p class="v-det">'+tuo+' meets one form of the amount but not the other (monthly amount or yearly total): ask the consulate how it assesses your income.</p>';
          barTot='! Check with the consulate';}
        else{h+='<div class="verdetto no">'+ic('x')+'<span>'+soldi(diff,val)+quando+' short</span></div>'+barra()+'<p class="v-det">'+tuo+' is below this minimum.</p>';
          barTot='✗ '+soldi(diff,val)+quando+' short';}}
      h+='<div class="r-lab">Official minimum for '+o.adulti+' adult'+(o.adulti>1?'s':'')+(o.figli?' and '+o.figli+' child'+(o.figli>1?'ren':''):'')+(o.familiari_ignorati?' (family members not counted)':'')+'</div>';
      if(o.periodo==='month'&&o.pagamenti!==12){h+='<div class="tot">'+soldi(o.mensile,val)+' <span>a month × '+o.pagamenti+'</span></div><div class="r-anno">= '+soldi(o.annuale,val)+' a year · '+soldi(o.mensile12,val)+' × 12</div>';}
      else{h+='<div class="tot">'+soldi(o.mensile,val)+' <span>a month</span></div><div class="r-anno">'+soldi(o.annuale,val)+' a year</div>';}
      if(cur!==val)h+='<div class="conv">'+ic('exchange')+'≈ '+soldi(cv.mensile,cur)+' a month'+(o.periodo==='month'&&o.pagamenti!==12?' × '+o.pagamenti:'')+' · '+soldi(cv.annuale,cur)+' a year</div>';
      avvisi.forEach(function(a){h+='<p class="small" style="margin:8px 0 0"><strong>Note:</strong> '+esc(a)+'</p>';});
      h+='<details class="r-come"><summary>'+ic('calc')+'How this amount is calculated</summary><ul>';
      o.righe.forEach(function(r){h+='<li>'+esc(testo(V,r))+(r[1]>1?' × '+r[1]:'')+' = <strong>'+soldi(r[3],val)+'</strong>'+(o.periodo==='month'?' a month':' a year')+'</li>';});
      if(o.tetto)h+='<li>Capped at the maximum set by the rule.</li>';
      if(o.familiari_ignorati)h+='<li>'+esc(o.motivo)+'</li>';h+='</ul>';
      h+='<p class="formula"><strong>Rule:</strong> '+esc(V.regola)+'</p></details>';
      var fo=P.fonti[0];h+='<p class="fonte">Official source: <a href="'+esc(fo.url)+'" rel="noopener">'+esc(fo.titolo)+'</a> · checked on '+dl(fo.controllato_il)+'</p>';
      if(cur!==val)h+='<p class="fonte">ECB reference rate of '+dl(CAMBI.data)+'. Indicative conversion.</p>';
      var np=box.querySelector('[data-nota-pagamenti]');if(np){np.textContent=P.nota_pagamenti||'';np.hidden=!P.nota_pagamenti;}
      if(!fisso){h+='<p class="calc-link"><a href="'+box.getAttribute('data-rel')+P.slug+'/">Full rules and official sources for the '+esc(P.paese+' '+P.nome)+'</a></p>';}
      box.querySelector('[data-out]').innerHTML=h;
      var bar=box.querySelector('[data-bar]');if(bar){bar.querySelector('.r-bar-tot').textContent=barTot||(soldi(o.mensile,val)+' a month'+(o.pagamenti!==12?' × '+o.pagamenti:''));
        if(!barTot&&o.periodo!=='month')bar.querySelector('.r-bar-tot').textContent=soldi(o.annuale,val)+' a year';
        bar.querySelector('.r-bar-info').textContent=P.paese+' '+P.nome;if(box.__obs)box.__obs();}
      f.querySelector('[data-lab=reddito]').textContent='Your monthly income in '+cur+' (optional)';}
    selP.addEventListener('change',function(){riempiG();riempiV();calcolaOra();});
    selG.addEventListener('change',function(){riempiV();calcolaOra();});
    f.addEventListener('input',function(e){if(e.target===selP||e.target===selG)return;calcolaOra(e);});
    f.addEventListener('change',function(e){if(e.target===selP||e.target===selG)return;calcolaOra(e);});
    f.addEventListener('submit',function(e){e.preventDefault();});
    box.__calcola=calcolaOra;calcolaOra();barra(box);}
  function barra(box){var bar=box.querySelector('[data-bar]'),out=box.querySelector('.calc-out'),fm=box.querySelector('form');
    if(!bar||!('IntersectionObserver' in window))return;var vOut=true,vForm=false,mq=window.matchMedia('(max-width:880px)');
    function agg(){bar.hidden=!(mq.matches&&vForm&&!vOut);}
    var ob=new IntersectionObserver(function(e){vOut=e[0].intersectionRatio>0.6;agg();},{threshold:[0,0.6,1]});
    box.__obs=function(){var t=out.querySelector('.verdetto,.tot');ob.disconnect();ob.observe(t||out);};box.__obs();
    new IntersectionObserver(function(e){vForm=e[0].isIntersecting;agg();}).observe(fm);
    if(mq.addEventListener)mq.addEventListener('change',agg);
    bar.addEventListener('click',function(){out.scrollIntoView({behavior:'smooth',block:'start'});});}
  var boxes=document.querySelectorAll('[data-calcolatore]');boxes.forEach(monta);
  if(window.fetch){fetch(D.url_cambi,{cache:'no-store'}).then(function(r){if(!r.ok)throw 0;return r.json();}).then(function(c){
    if(c&&c.tassi&&c.data&&c.tassi.USD&&c.data>=CAMBI.data){CAMBI=c;aggiornaStatici();boxes.forEach(function(b){if(b.__calcola)b.__calcola();});}}).catch(function(){});}
  var src=document.querySelectorAll('input[name=source]');var ref='';try{var qs=new URLSearchParams(location.search);ref=qs.get('ref')||document.referrer||'direct';}catch(e){ref='direct';}
  src.forEach(function(i){i.value=String(ref).slice(0,200);});
  document.querySelectorAll('form.ajax').forEach(function(form){form.addEventListener('submit',function(ev){ev.preventDefault();
    var err=form.querySelector('[data-errore]');err.hidden=true;if(!form.checkValidity()){form.reportValidity();return;}
    var bt=form.querySelector('button');bt.disabled=true;
    fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(new FormData(form)).toString()})
    .then(function(r){if(!r.ok)throw new Error(r.status);form.hidden=true;form.parentNode.querySelector('[data-ok]').hidden=false;})
    .catch(function(){err.hidden=false;bt.disabled=false;});});});
})();
"""

URLS = []
AD = '<div class="ad-slot" aria-hidden="true"></div>'
AVVISO = ('<p class="avviso"><strong>Not immigration or legal advice.</strong> These are the minimum amounts written in the official rules on the date we checked them. '
          'Requirements change, and consulates and immigration offices can ask for more or assess your documents differently: '
          'always check the official page or ask the consulate before you apply.</p>')


def blocco_dati():
    """Dati per il calcolatore: programmi (campi utili), indici, cambi di riserva, nomi delle valute."""
    campi_v = ("id", "nome", "base", "fattore", "regola", "famiglia", "tetto", "etichetta_principale")
    campi_p = ("esito", "condizioni", "confronto", "nota_pagamenti")
    progs = [dict({"slug": P["slug"], "paese": P["paese"], "nome": P["nome"],
                   "varianti": [{k: V[k] for k in campi_v if k in V} for V in P["varianti"]],
                   "fonti": [{k: P["fonti"][0][k] for k in ("titolo", "url", "controllato_il")}]},
                  **{k: P[k] for k in campi_p if k in P}) for P in PROG]
    ind = {k: {c: v[c] for c in ("valore", "valuta", "periodo", "nome_breve", "pagamenti") if c in v} for k, v in INDICI.items()}
    d = {"programmi": progs, "indici": ind, "cambi": {"data": CAMBI["data"], "tassi": CAMBI["tassi"]},
         "nomi_valute": {k: v[0] for k, v in VALUTE.items()}, "url_cambi": URL_CAMBI_LIVE,
         "bandiere": {P["paese"]: bandiera(P["paese"]) for P in PROG}}
    return ('<script type="application/json" id="dati-visti">' +
            json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>")


def pagina(percorso, titolo, descrizione, corpo, briciole=None, indicizza=True, calcolatore=False, jsonld_extra=None, assoluto=False, testata="", ordina=False):
    file = percorso if percorso.endswith(".html") else (percorso + "index.html")
    profondita = file.count("/")
    rel = "/" if assoluto else ("../" * profondita or "./")  # 404: link assoluti, Netlify la serve a qualsiasi profondità
    url_pag = URL_SITO + "/" + percorso
    if indicizza:
        URLS.append(percorso)
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": NOME, "url": URL_SITO + "/"}] if percorso == "" else []
    bc = ""
    if briciole:
        voci = [{"@type": "ListItem", "position": 1, "name": "Home", "item": URL_SITO + "/"}]
        for i, (n, p) in enumerate(briciole, start=2):
            voci.append({"@type": "ListItem", "position": i, "name": n, "item": URL_SITO + "/" + p})
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": voci})
        bc = ('<nav class="briciole" aria-label="Breadcrumb"><a href="' + rel + '">Home</a>' +
              "".join(f' › <a href="{rel}{p}">{escape(n)}</a>' for n, p in briciole[:-1]) + f" › {escape(briciole[-1][0])}</nav>")
    if jsonld_extra:
        ld += jsonld_extra if isinstance(jsonld_extra, list) else [jsonld_extra]
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    robots = "" if indicizza else '<meta name="robots" content="noindex">'
    canonico = f'<link rel="canonical" href="{url_pag}">' if indicizza else ""
    js = f"<script>{MOTORE_JS}{APP_JS}</script>" if calcolatore else f"<script>{FORM_JS}</script>"
    if ordina:
        js += f"<script>{ORDINA_JS}</script>"
    dati = blocco_dati() if calcolatore else ""
    voci_menu = [("", "Calculator"), ("digital-nomad-visa-income-requirements/", "Digital nomad visas"), ("work-visa-salary-thresholds/", "Work visas"),
                 ("visa-refusal-rates/", "Refusal rates"), ("how-it-works/", "How it works"), ("about/", "About")]
    menu = "".join(f'<a href="{rel}{u}"' + (' aria-current="page"' if u == percorso else "") + f'>{t}</a>' for u, t in voci_menu)
    testo = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">{ADSENSE_HEAD}
<title>{escape(titolo)}</title>
<meta name="description" content="{escape(descrizione)}">
{canonico}
<meta property="og:title" content="{escape(titolo)}">
<meta property="og:description" content="{escape(descrizione)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url_pag}">
<meta property="og:site_name" content="{NOME}">
<meta property="og:image" content="{URL_SITO}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{NOME}: official minimum income for visas, for you and your family">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#141B33">
<meta name="color-scheme" content="light dark">
{robots}
<link rel="icon" href="{FAVICON}">
<link rel="preload" href="/assets/fonts/ibm-plex-serif-700.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS}</style>
{ld_html}
</head>
<body>
{SPRITE}
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
<a class="logo" href="{rel}">{MARCHIO}<span>Visa Income <b>Checker</b></span></a>
<nav class="menu" aria-label="Menu">{menu}</nav>
<details class="nav-m"><summary aria-label="Open the menu">{ico("menu")}Menu</summary><nav aria-label="Menu">{menu}</nav></details>
</div></header>
<main id="main">
{testata}
<div class="wrap">
{bc}
{corpo}{riquadro_trasparenza(corpo)}
</div>
</main>
<footer><div class="wrap">
<div class="f-grid"><div>
<a class="logo" href="{rel}">{MARCHIO}<span>Visa Income <b>Checker</b></span></a>
<p><strong>{NOME}</strong> is an independent site, not affiliated with any government, consulate or immigration authority. Every amount and every statistic comes from an official source (law, official gazette, ministry, immigration authority, European Commission, Home Office or statistics office) linked under the figure with the date we checked or downloaded it.
<strong>Requirements change, and consulates can ask for more: always check the official page or the consulate.</strong> Nothing on this site is immigration, legal or tax advice.</p>
<p>Exchange rates: euro foreign exchange reference rates of the European Central Bank (source: ECB), for information only.</p>
</div><div>
<h2>Explore</h2>
<ul><li><a href="{rel}visa-refusal-rates/">Visa refusal rates</a></li><li><a href="{rel}moved-to/">Who moved where (by nationality)</a></li><li><a href="{rel}about/">About</a></li><li><a href="{rel}how-it-works/">How it works and sources</a></li><li><a href="{rel}contact/">Contact</a></li><li><a href="{rel}privacy.html">Privacy</a></li><li><a href="{rel}contact/?ref=spotted-a-change">Spotted a change? Tell us</a></li></ul>
</div></div>
{blocco_altri(ALTRI_SITI, "Other useful tools for your trip")}
<p class="f-base">Official sources only · the calculator runs in your browser · links marked "Affiliate" may earn us a commission.</p>
</div></footer>
{dati}
{js}
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")
    if indicizza:
        IMPRONTE[percorso] = impronta_contenuto(testo)


# ---------------------------------------------------------------- lastmod vero per ogni URL della sitemap (28/10/2026)
# Il registro dati/lastmod.json tiene per ogni pagina la data dell'ultima modifica del contenuto e la sua impronta
# (titolo, descrizione, JSON-LD e <main>: non il CSS, il menu o il piè di pagina, uguali in tutte le pagine).
# A ogni generazione: impronta uguale -> la data resta; diversa o pagina nuova -> data di oggi.
# Prima generazione senza registro: se la pagina è uguale a quella già in sito/, la data si ricava da git
# (ultimo commit in cui il contenuto della pagina è cambiato); altrimenti oggi.
REGISTRO_LASTMOD = DATI / "lastmod.json"
IMPRONTE = {}   # percorso -> impronta della pagina appena generata
VECCHIE = {}    # percorso -> impronta della pagina in sito/ prima della generazione


def impronta_contenuto(testo):
    import hashlib
    tit = re.search(r"<title>(.*?)</title>", testo, re.S)
    des = re.search(r'<meta name="description" content="(.*?)">', testo, re.S)
    ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', testo, re.S)
    main = re.search(r'<main id="main">(.*?)</main>', testo, re.S)
    pezzi = [tit.group(1) if tit else "", des.group(1) if des else ""] + ld + [main.group(1) if main else ""]
    return hashlib.sha256("\n".join(pezzi).encode("utf-8")).hexdigest()[:20]


def percorso_da_file(f):
    r = f.relative_to(SITO).as_posix()
    return r[:-len("index.html")] if r.endswith("index.html") else r


def data_da_git(percorso, impronta):
    """Data (AAAA-MM-GG) del commit da cui il contenuto della pagina è uguale a oggi, o None."""
    import subprocess
    file = (SITO / (percorso if percorso.endswith(".html") else percorso + "index.html")).relative_to(RADICE.parent).as_posix()
    repo = str(RADICE.parent)
    try:
        log = subprocess.run(["git", "-C", repo, "log", "--format=%H %cs", "--", file], capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    data = None
    for riga in log.split("\n"):
        if not riga.strip():
            continue
        h, d = riga.split()
        r = subprocess.run(["git", "-C", repo, "show", f"{h}:{file}"], capture_output=True, text=True, timeout=60)
        if r.returncode != 0 or impronta_contenuto(r.stdout) != impronta:
            break
        data = d
    return data


def date_lastmod():
    reg = json.loads(REGISTRO_LASTMOD.read_text(encoding="utf-8"))["pagine"] if REGISTRO_LASTMOD.exists() else {}
    oggi = OGGI.isoformat()
    nuovo = {}
    for u in URLS:
        imp = IMPRONTE[u]
        if u in reg and reg[u][1] == imp:
            d = reg[u][0]
        elif u not in reg and VECCHIE.get(u) == imp:
            d = data_da_git(u, imp) or oggi
        else:
            d = oggi
        nuovo[u] = [d, imp]
    REGISTRO_LASTMOD.write_text(json.dumps({"_nota": "Scritto da genera.py: percorso -> [data dell'ultima modifica del contenuto, impronta]. Non modificare a mano.",
                                            "pagine": dict(sorted(nuovo.items()))}, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    return {u: v[0] for u, v in nuovo.items()}


FORM_JS = r"""
(function(){
  var src=document.querySelectorAll('input[name=source]');var ref='';try{var qs=new URLSearchParams(location.search);ref=qs.get('ref')||document.referrer||'direct';}catch(e){ref='direct';}
  src.forEach(function(i){i.value=String(ref).slice(0,200);});
  document.querySelectorAll('form.ajax').forEach(function(form){form.addEventListener('submit',function(ev){ev.preventDefault();
    var err=form.querySelector('[data-errore]');err.hidden=true;if(!form.checkValidity()){form.reportValidity();return;}
    var bt=form.querySelector('button');bt.disabled=true;
    fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(new FormData(form)).toString()})
    .then(function(r){if(!r.ok)throw new Error(r.status);form.hidden=true;form.parentNode.querySelector('[data-ok]').hidden=false;})
    .catch(function(){err.hidden=false;bt.disabled=false;});});});
})();
"""


def modulo_calcolatore(rel="", programma="", paese="", valuta="USD"):
    return f"""<div class="card calc" data-calcolatore data-rel="{rel}" data-programma="{escape(programma)}" data-paese="{escape(paese)}" data-valuta="{valuta}">
<div class="calc-grid">
<form autocomplete="off">
<div class="campi">
<label data-campo="paese"><span class="lt">{ico("globe")}Country</span><span class="sel-f"><span class="sel-flag" data-flag></span><select name="paese"></select></span></label>
<label data-campo="programma"><span class="lt">{ico("passport")}Visa or permit</span><select name="programma"></select></label>
<label class="pieno" data-campo="variante"><span class="lt">{ico("list")}Category</span><select name="variante"></select></label>
<label><span class="lt">{ico("user")}Adults incl. you</span><input type="number" name="adulti" min="1" max="20" value="1" inputmode="numeric"></label>
<label><span class="lt">{ico("child")}Children under 18</span><input type="number" name="figli" min="0" max="20" value="0" inputmode="numeric"></label>
<label class="l-val"><span class="lt">{ico("exchange")}Show amounts also in</span><select name="valuta"></select></label>
<label class="l-red"><span class="lt">{ico("wallet")}<span data-lab="reddito">Your monthly income (optional)</span></span><input type="number" name="reddito" min="0" step="any" placeholder="e.g. 3500" inputmode="decimal"></label>
<label class="pieno"><span class="lt">{ico("calendar")}Your income is paid</span><select name="pagamenti"><option value="12">12 times a year</option><option value="13">13 times a year</option><option value="14">14 times a year</option></select></label>
<p class="small pieno" data-nota-pagamenti hidden style="margin:0"></p>
</div>
</form>
<div class="calc-out"><div class="risultato" data-out aria-live="polite"><noscript>Turn on JavaScript to use the calculator. The tables below show the official amounts.</noscript></div></div>
</div>
<button type="button" class="r-bar" data-bar hidden><span class="r-bar-tot"></span><span class="r-bar-info"></span><span class="r-bar-go">Result{ico("arrow")}</span></button>
</div>"""


def importo_live(x, da, a, molt=1, div=1):
    """Importo convertito (poi × molt ÷ div), rigenerato nel browser con i cambi aggiornati."""
    extra = (f' data-molt="{molt}"' if molt != 1 else "") + (f' data-div="{div}"' if div != 1 else "")
    return f'<span data-importo="{x}" data-da="{da}" data-a="{a}"{extra}>{soldi(converti_scalato(x, da, a, CAMBI["tassi"], molt, div), a)}</span>'


def box_affiliati():
    """Riquadro affiliati: vuoto (non mostrato) finché dati/affiliati.json non ha URL."""
    voci = [v for k, v in AFFILIATI.items() if not k.startswith("_") and isinstance(v, dict) and v.get("url")]
    if not voci:
        return ""
    righe = "".join(f'<li><a href="{escape(v["url"])}" rel="sponsored noopener" target="_blank">{escape(v["titolo"])}</a> '
                    f'<span class="small">{escape(v.get("nome", ""))} {escape(v["testo"])}</span></li>' for v in voci)
    return (f'<section class="card" style="margin-top:22px"><h2 style="margin-top:0">Preparing your application</h2><ul style="margin:0 0 8px;padding-left:20px">{righe}</ul>'
            f'<p class="small" style="margin:0">{MON.RIGA_EN}</p></section>')  # riga di trasparenza comune (monetizzazione.py)


# ---------------------------------------------------------------- pagine
def live_mese(o, a):
    """Importo mensile (per mensilità) convertito, coerente con convertiImporti del JS."""
    if o["periodo"] == "month":
        return importo_live(o["mensile"], o["valuta"], a)
    return importo_live(o["annuale"], o["valuta"], a, div=12)


def live_anno(o, a):
    if o["periodo"] == "month":
        return importo_live(o["mensile"], o["valuta"], a, molt=o["pagamenti"])
    return importo_live(o["annuale"], o["valuta"], a)


def x_pag(o):
    return f" × {o['pagamenti']}" if o["periodo"] == "month" and o["pagamenti"] != 12 else ""


FAMIGLIE = [("Single applicant", 1, 0), ("Couple", 2, 0), ("Couple + 1 child", 2, 1), ("Couple + 2 children (family of 4)", 2, 2),
            ("Couple + 3 children", 2, 3), ("Single parent + 1 child", 1, 1)]


def tabella_famiglie(P, V):
    fam = V["famiglia"]
    if fam["tipo"] == "nessuno":
        return f'<p><strong>Family members:</strong> {escape(fam["motivo"])}</p>'
    righe = []
    for nome, a, c in FAMIGLIE:
        o = calcola(P, V["id"], a, c)
        val = o["valuta"]
        righe.append(f'<tr><td>{nome}</td><td class="n">{soldi(o["mensile"], val)}{x_pag(o)}</td><td class="n">{soldi(o["annuale"], val)}</td>'
                     f'<td class="n">{live_mese(o, "USD")}{x_pag(o)}</td></tr>')
    o1 = calcola(P, V["id"], 1, 0)
    mese = "A month" + (f" (× {o1['pagamenti']} payments)" if x_pag(o1) else "")
    return (f'<div class="tab"><table><thead><tr><th>Household</th><th class="n">{mese}</th><th class="n">A year</th><th class="n">A month in USD</th></tr></thead>'
            f'<tbody>{"".join(righe)}</tbody></table></div>')


def tabella_valute(P, V):
    o1 = calcola(P, V["id"], 1, 0)
    val = o1["valuta"]
    righe = []
    for c in VALUTE_TABELLA:
        if c != "EUR" and c not in CAMBI["tassi"]:
            continue
        righe.append(f'<tr><td>{c} <span class="small">{escape(VALUTE[c][0])}</span></td><td class="n">{live_mese(o1, c)}{x_pag(o1)}</td>'
                     f'<td class="n">{live_anno(o1, c)}</td></tr>')
    return ('<div class="tab"><table><thead><tr><th>Currency</th><th class="n">Main applicant, a month</th><th class="n">A year</th></tr></thead>'
            f'<tbody>{"".join(righe)}</tbody></table></div><p class="fonte">{cambi_nota()}</p>')


def blocco_indice(V):
    if "indice" not in V["base"]:
        return ""
    I = INDICI[V["base"]["indice"]]
    pag = f" × {I['pagamenti']} payments" if I.get("pagamenti", 12) != 12 else ""
    return (f'<div class="indice"><strong>{escape(I["nome"])}: {soldi(I["valore"], I["valuta"])} {periodo_testo(I["periodo"])}{pag}</strong>'
            f'<br>{escape(I["calcolo"])}<br><span class="small">In force: {escape(I["in_vigore"])}. {escape(I["ricontrollo"])}</span>'
            f'<p class="fonte">Source of the index: ' + "; ".join(
                f'<a href="{escape(f["url"])}" rel="noopener">{escape(f["titolo"])}</a>, checked on {data_lunga(f["controllato_il"])}' for f in I["fonti"]) + "</p></div>")


def pagina_programma(P):
    rel = "../"
    V0 = P["varianti"][0]
    o = calcola(P, V0["id"], 1, 0)
    val = o["valuta"]
    figura = figura_testo(o)
    altre_var = ""
    if len(P["varianti"]) > 1:
        righe = []
        for V in P["varianti"]:
            ov = calcola(P, V["id"], 1, 0)
            righe.append(f'<tr><td>{escape(V["nome"])}</td><td class="n">{soldi(ov["mensile"], val)}{x_pag(ov)}</td><td class="n">{soldi(ov["annuale"], val)}</td>'
                         f'<td class="n">{live_anno(ov, "USD")}</td></tr>')
        altre_var = ('<h2>All categories</h2><div class="tab"><table><thead><tr><th>Category</th><th class="n">A month</th><th class="n">A year</th><th class="n">A year in USD</th></tr></thead>'
                     f'<tbody>{"".join(righe)}</tbody></table></div><p class="small">Rules: ' +
                     " ".join(f'<strong>{escape(V["nome"])}:</strong> {escape(V["regola"])}' for V in P["varianti"]) + "</p>")
    eur_eq = ""
    if val != "EUR":
        eur_eq = f'<p class="small">In euros: about {live_anno(o, "EUR")} a year ({cambi_nota()})</p>'
    sorelle = [p for p in PROG if p["paese_slug"] == P["paese_slug"] and p["slug"] != P["slug"]]
    simili = [p for p in PROG if p["categoria"] == P["categoria"] and p["paese_slug"] != P["paese_slug"]]
    link_sorelle = ""
    if sorelle:
        link_sorelle = (f'<h2>Other visas in {escape(P["paese"])}</h2><div class="griglia">' +
                        "".join(scheda(p, rel) for p in sorelle) + "</div>")
    link_simili = (f'<h2>Compare: other {escape(CATEGORIE[P["categoria"]].lower())}s</h2><div class="griglia">' +
                   "".join(scheda(p, rel) for p in simili) + "</div>") if simili else ""
    fam_tit = "How much for a family" if V0["famiglia"]["tipo"] != "nessuno" else "Family members"
    note = "".join(f"<li>{escape(n)}</li>" for n in P["note"])
    corpo = f"""<section class="hero">{h1_diviso(titolo_prog(P))}</section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico(ICONA_CATEGORIA[P['categoria']])}<span>{escape(CATEGORIE[P['categoria']])}</span><span>{escape(P['paese'])}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Minimum for the main applicant{(' (' + escape(V0['nome'].lower()) + ')') if len(P['varianti']) > 1 else ''}</span><span class="sr">: </span>{figura}</p>
{fonte_breve(P)}
{eur_eq}
<p class="lead">{escape(P['descrizione'])} Official name: <em>{escape(P['nome_ufficiale'])}</em>.</p>
</div>
</section>
<h2>How the amount is calculated</h2>
<p class="formula"><strong>Rule:</strong> {escape(V0['regola'])}</p>
{blocco_indice(V0)}
<p class="small"><strong>Income that counts:</strong> {escape(P['reddito'])}</p>
{('<p class="avviso">' + escape(P['condizioni']) + '</p>') if P.get('condizioni') else ''}
<h2>Calculator</h2>
{modulo_calcolatore(rel=rel, programma=P['slug'])}
{AVVISO}
{AD}
{altre_var}
<h2>{fam_tit}</h2>
{tabella_famiglie(P, V0)}
<p class="fonte">Calculated from the rule above · official source checked on {data_lunga(P['fonti'][0]['controllato_il'])}</p>
<h2>In your currency</h2>
{tabella_valute(P, V0)}
<h2>Good to know</h2>
<ul>{note}</ul>
<h2>Official sources</h2>
{fonti_html(fonti_prog(P))}
<p class="small">Spotted a change in the official amount? <a href="{rel}contact/?ref={P['slug']}">Tell us</a>.</p>
{box_affiliati()}
{link_sorelle}
{link_simili}
<p><a href="{rel}country/{P['paese_slug']}/">All visa income requirements in {escape(P['paese'])}</a> · <a href="{rel}digital-nomad-visa-income-requirements/">Digital nomad visa income requirements {ANNO}</a> · <a href="{rel}work-visa-salary-thresholds/">Work visa salary thresholds {ANNO}</a></p>
{link_rifiuti(P['paese'], rel)}"""
    descr = (f"{nome_prog(P)} {ANNO}: minimum {riassunto(P)} for the main applicant, with family members and conversion to USD, GBP, INR and more. "
             f"Official source and check date.")
    pagina(f"{P['slug']}/", titolo_prog(P), descr, corpo, calcolatore=True,
           briciole=[(P["paese"], f"country/{P['paese_slug']}/"), (nome_prog(P), f"{P['slug']}/")])


def pagina_paese(slug):
    rel = "../../"
    nome = PAESI[slug]
    pp = [p for p in PROG if p["paese_slug"] == slug]
    righe = []
    for P in pp:
        for V in P["varianti"]:
            o = calcola(P, V["id"], 1, 0)
            o4 = calcola(P, V["id"], 2, 2)
            val = o["valuta"]
            fam = (soldi(o4["mensile"], val) + x_pag(o4)) if V["famiglia"]["tipo"] != "nessuno" else "not set"
            righe.append(f'<tr><td><a href="{rel}{P["slug"]}/">{escape(P["nome"])}</a>{(" – " + escape(V["nome"])) if len(P["varianti"]) > 1 else ""}</td>'
                         f'<td class="n">{soldi(o["mensile"], val)}{x_pag(o)}</td><td class="n">{soldi(o["annuale"], val)}</td><td class="n">{fam}</td>'
                         f'<td><a href="{escape(P["fonti"][0]["url"])}" rel="noopener">official</a>, {data_lunga(P["fonti"][0]["controllato_il"])}</td></tr>')
    corpo = f"""<section class="hero"><h1>Visa income requirements in {escape(nome)} {ANNO}</h1>
<p class="lead">The official minimum income or salary for each {escape(nome)} visa we cover, calculated from the official rule, with a calculator for family members and other currencies.</p></section>
<div class="tab"><table><thead><tr><th>Visa or permit</th><th class="n">Main applicant, a month</th><th class="n">A year</th><th class="n">Family of 4, a month</th><th>Source</th></tr></thead><tbody>{''.join(righe)}</tbody></table></div>
<p class="small">Monthly amounts for annual thresholds are the annual amount divided by 12. "× 14": the amount is paid 14 times a year. "Not set": the official rule sets no amount for family members (see each page).</p>
{modulo_calcolatore(rel=rel, paese=nome)}
{AVVISO}
{AD}
<div class="griglia" style="margin-top:20px">{''.join(scheda(p, rel) for p in pp)}</div>
<p><a href="{rel}">All countries</a> · <a href="{rel}digital-nomad-visa-income-requirements/">Digital nomad visas compared</a></p>
{link_rifiuti(nome, rel)}
{blocco_tr_dest(nome, rel)}"""
    pagina(f"country/{slug}/", f"{nome} visa income requirements {ANNO}: official amounts and calculator",
           f"Official minimum income and salary thresholds for {nome} visas in {ANNO}, with family members, currency conversion and sources.",
           corpo, calcolatore=True, briciole=[(nome, f"country/{slug}/")])


def ultimo_controllo():
    date_ = [f["controllato_il"] for P in PROG for f in P["fonti"]] + [f["controllato_il"] for I in INDICI.values() for f in I["fonti"]]
    return data_lunga(max(date_))


CAT_HOME = [("laptop", "Digital nomad visas", "Spain, Portugal, Croatia, Hungary, Italy"),
            ("sun", "Passive income visas", "Spain non-lucrative, Portugal D7"),
            ("briefcase", "Work permits and Blue Cards", "Germany, Netherlands, France, Austria, Sweden, Denmark, Ireland, UK"),
            ("family", "Family visas", "UK spouse visa")]


def scheda(p, rel=""):
    return (f'<a href="{rel}{p["slug"]}/"><span class="ic f">{bandiera(p["paese"])}<span class="mini">{ico(ICONA_CATEGORIA[p["categoria"]])}</span></span>'
            f'<span>{escape(nome_prog(p))}<small>{escape(riassunto(p))}</small></span></a>')


def home():
    gruppi = []
    for slug, nome in PAESI.items():
        pp = [p for p in PROG if p["paese_slug"] == slug]
        gruppi.append(f'<a href="country/{slug}/"><span class="ic f">{bandiera(nome)}</span><span>{escape(nome)}<small>{len(pp)} visa{"s" if len(pp) > 1 else ""}</small></span></a>')
    lista = "".join(scheda(p) for p in PROG)
    cat = "".join(f'<li><span class="ic">{ico(i)}</span><strong>{t}</strong>{e}</li>' for i, t, e in CAT_HOME)
    testata = f"""<div class="band"><div class="wrap band-in">{DECO}
<section class="hero">{h1_diviso(f"Visa income checker {ANNO}: how much income do you need for a digital nomad, retirement or work visa?")}
<p class="sub">The official minimum for {len(PROG)} visas in {len(PAESI)} countries, for you and your family, in your currency.</p>
<p class="trust"><span>{ico("shield")}Official sources · last checked {ultimo_controllo()}</span><span>{ico("exchange")}ECB exchange rates</span></p></section>
{modulo_calcolatore(rel='', paese='Spain')}
</div></div>"""
    corpo = f"""{AVVISO}
{AD}
<h2>What the checker covers</h2>
<p class="lead">The official minimum income for {len(PROG)} visas and permits in {len(PAESI)} countries, calculated from the official base (minimum wage, IPREM, average salary, legal salary thresholds) for you and each family member, and converted into your currency with the latest European Central Bank reference rates.</p>
<ul class="cat">{cat}</ul>
<h2>All visas</h2>
<div class="griglia">{lista}</div>
<h2>Countries</h2>
<div class="griglia">{''.join(gruppi)}</div>
<h2>Compare</h2>
<p><a href="digital-nomad-visa-income-requirements/">Digital nomad visa income requirements {ANNO}</a> (with passive income visas) · <a href="work-visa-salary-thresholds/">EU Blue Card and work visa salary thresholds {ANNO}</a> · <a href="{SEZ}">Visa refusal rates {A1}</a></p>
<h2>Visa refusal rates</h2>
<p class="lead">How many visa applications are refused? Official {A1} Schengen figures by destination, by consulate and by the country where you apply, and UK refusal rates by nationality to {trimestre_testo(TRIM[-1])}.</p>
<div class="griglia">{''.join(f'<a href="{SEZ}{SLUG_RIF[p]}/"><span class="ic">{ico("passport")}</span><span>{escape(nome_paese(p))}<small>Schengen: {pct(tasso(PER_PAESE[A1][p]))} not issued in {A1}</small></span></a>' for p in ("INDIA", "NIGERIA", "PAKISTAN", "MOROCCO", "TÜRKIYE", "PHILIPPINES", "GHANA", "BANGLADESH"))}</div>
<p><a href="{SEZ}">Schengen visa rejection rates by country</a> · <a href="{SEZ}uk/">UK visa refusal rates by nationality</a></p>
<h2>Who moved where in {Y1}</h2>
<p class="lead">How many Americans, British people, Indians and others moved to Europe, Canada and the UK in {Y1}: official first residence permits by country and reason (Eurostat, updated {data_lunga(F_ES["aggiornato_il"])}), new permanent residents of Canada and UK visas granted.</p>
<div class="griglia">{''.join(f'<a href="{SEZ_TR}{NAZ_TR[c][0]}/"><span class="ic">{ico("globe")}</span><span>How many {escape(NAZ_TR[c][1])} moved to Europe<small>{intero(riga_eu(c, "EU27_2020", Y1)[0])} first permits in the EU in {Y1}</small></span></a>' for c in ("US", "UK", "CA", "AU", "IN", "PK", "NG", "PH"))}</div>
<p><a href="{SEZ_TR}">Who moved where: all {len(NAZ_TR)} nationalities</a></p>
<h2>Why our numbers can differ from other sites</h2>
<p>Many thresholds are a percentage of an index that changes every year (a minimum wage, an average salary), so pages that still show last year's figure are out of date. With the {ANNO} indices, on {data_lunga('2026-10-10')}: Spain's digital nomad visa is 200% of the {ANNO} minimum wage, €2,442 a month over 14 payments (€34,188 a year, the same as €2,849 a month over 12 payments); Croatia's is 2.5 × the 2025 average net salary, €3,622.50 a month; Portugal's D8 is 4 × €920 = €3,680 a month. We recalculate from the official index and show the source and the date under every figure.</p>
{box_affiliati()}"""
    pagina("", f"Visa Income Checker {ANNO}: minimum income for digital nomad, retirement and work visas (calculator)",
           f"How much income do you need? Official {ANNO} minimum income for {len(PROG)} visas (Spain, Portugal, Croatia, Italy, Hungary, Blue Cards, UK) for you and your family, in USD, GBP, INR, PHP and more.",
           corpo, calcolatore=True, testata=testata)


def riga_confronto(P, V, rel):
    o1 = calcola(P, V["id"], 1, 0)
    o2 = calcola(P, V["id"], 2, 0)
    o4 = calcola(P, V["id"], 2, 2)
    val = o1["valuta"]
    nessuno = V["famiglia"]["tipo"] == "nessuno"
    f = P["fonti"][0]
    nome = escape(nome_prog(P)) + ((" – " + escape(V["nome"])) if len(P["varianti"]) > 1 else "")
    return (converti_importi(o1, "EUR", CAMBI["tassi"])["mensile12"],
            f'<tr><td><a href="{rel}{P["slug"]}/">{nome}</a></td><td class="n">{soldi(o1["mensile"], val)}{x_pag(o1)}</td>'
            f'<td class="n">{"not set" if nessuno else soldi(o2["mensile"], val) + x_pag(o2)}</td>'
            f'<td class="n">{"not set" if nessuno else soldi(o4["mensile"], val) + x_pag(o4)}</td>'
            f'<td class="n">{live_mese(o1, "USD")}{x_pag(o1)}</td>'
            f'<td><a href="{escape(f["url"])}" rel="noopener">official</a>, {data_lunga(f["controllato_il"])}</td></tr>')


def pagina_confronto_nomadi():
    rel = "../"
    testa = ('<thead><tr><th>Visa</th><th class="n">Main applicant, a month</th><th class="n">Couple</th><th class="n">Family of 4</th>'
             '<th class="n">Main applicant in USD</th><th>Source</th></tr></thead>')
    dn = sorted((riga_confronto(P, V, rel) for P in PROG if P["categoria"] == "digital-nomad" for V in P["varianti"]), key=lambda x: x[0])
    pi = sorted((riga_confronto(P, V, rel) for P in PROG if P["categoria"] == "passive-income" for V in P["varianti"]), key=lambda x: x[0])
    corpo = f"""<section class="hero">{h1_diviso(f"Digital nomad visa income requirements {ANNO}: country by country")}
<p class="lead">The official minimum monthly income for each digital nomad visa we cover, for a single applicant, a couple and a family of four, calculated from the official rule. Sorted from the lowest to the highest.</p></section>
<div class="tab"><table>{testa}<tbody>{''.join(r[1] for r in dn)}</tbody></table></div>
<p class="fonte">{cambi_nota()}</p>
<p class="small">"Couple" and "family of 4" (2 adults, 2 children) add the official amounts for family members. "Not set": the official rule sets no amount for family members (Hungary does not allow family reunification for White Card holders; Italy applies the separate family reunification rules; for Portugal's D8 the Ministry does not say how family means combine with the applicant's amount). "× 14": Spain's amount is quoted per payment, 14 payments a year; the table is sorted by the yearly total.</p>
{AVVISO}
{AD}
<h2>Passive income and retirement visas</h2>
<div class="tab"><table>{testa}<tbody>{''.join(r[1] for r in pi)}</tbody></table></div>
<h2>Calculator</h2>
{modulo_calcolatore(rel=rel, paese='Portugal')}
<h2>Not covered yet</h2>
<p>We publish a visa only when we can read the complete rule on an official page or in the official gazette. Not covered on the date we checked, because the official source was not readable or was incomplete: Greece (digital nomad visa, financially independent person), Cyprus, Malta (Nomad Residence Permit), Estonia, Czechia, Romania, Latvia, Iceland, Costa Rica, Brazil, Panama, Colombia, Thailand (DTV), the United Arab Emirates and Mexico (amounts vary by consulate). See <a href="{rel}how-it-works/">How it works</a>.</p>"""
    pagina("digital-nomad-visa-income-requirements/", f"Digital nomad visa income requirements {ANNO}: official amounts by country (table)",
           f"Digital nomad visa income requirements {ANNO} compared: Spain, Portugal, Croatia, Hungary and Italy, for singles, couples and families of 4, in euros and US dollars, with official sources.",
           corpo, calcolatore=True, briciole=[(f"Digital nomad visa income requirements {ANNO}", "digital-nomad-visa-income-requirements/")])


def pagina_confronto_lavoro():
    rel = "../"
    righe = []
    for P in PROG:
        if P["categoria"] != "work":
            continue
        for V in P["varianti"]:
            o = calcola(P, V["id"], 1, 0)
            val = o["valuta"]
            eur = converti_importi(o, "EUR", CAMBI["tassi"])["annuale"]
            f = P["fonti"][0]
            righe.append((eur, f'<tr><td><a href="{rel}{P["slug"]}/">{escape(nome_prog(P))}</a>{(" – " + escape(V["nome"])) if len(P["varianti"]) > 1 else ""}</td>'
                               f'<td class="n">{soldi(o["annuale"], val)}</td><td class="n">{live_anno(o, "EUR")}</td>'
                               f'<td class="n">{live_anno(o, "USD")}</td>'
                               f'<td><a href="{escape(f["url"])}" rel="noopener">official</a>, {data_lunga(f["controllato_il"])}</td></tr>'))
    righe.sort(key=lambda x: x[0])
    corpo = f"""<section class="hero"><h1>EU Blue Card and work visa salary thresholds {ANNO}</h1>
<p class="lead">The official minimum gross salary for the EU Blue Card and similar work permits in the countries we cover, sorted from the lowest to the highest (converted to euros where needed).</p></section>
<div class="tab"><table><thead><tr><th>Permit</th><th class="n">A year (official currency)</th><th class="n">In EUR</th><th class="n">In USD</th><th>Source</th></tr></thead><tbody>{''.join(r[1] for r in righe)}</tbody></table></div>
<p class="fonte">{cambi_nota()}</p>
<p class="small">Salary thresholds are for the job holder and do not change with family members. Netherlands: the IND amounts exclude the 8% holiday allowance, so the yearly figure (monthly × 12) is lower than a full gross annual salary. UK: £33,400 and £37,500 are floors; the going rate for the occupation also applies. Family visas (such as the <a href="{rel}uk-spouse-visa/">UK spouse visa</a>) are not in this table.</p>
{AVVISO}
{AD}
<h2>Calculator</h2>
{modulo_calcolatore(rel=rel, paese='Germany', valuta='INR')}"""
    pagina("work-visa-salary-thresholds/", f"EU Blue Card salary thresholds {ANNO}: Germany, Netherlands, France, Austria, Sweden and more",
           f"Official {ANNO} salary thresholds for the EU Blue Card (Germany €50,700, Netherlands, France, Austria, Sweden), Denmark's pay limit, Ireland's Critical Skills permit and the UK Skilled Worker visa.",
           corpo, calcolatore=True, briciole=[(f"Work visa salary thresholds {ANNO}", "work-visa-salary-thresholds/")])


def pagina_come_funziona():
    rel = "../"
    indici = "".join(f'<h3>{escape(I["nome"])}: {soldi(I["valore"], I["valuta"])} {periodo_testo(I["periodo"])}{(" × " + str(I["pagamenti"]) + " payments") if I.get("pagamenti", 12) != 12 else ""}</h3><p>{escape(I["calcolo"])} {escape(I["ricontrollo"])}</p>{fonti_html(I["fonti"])}'
                     for I in INDICI.values())
    corpo = f"""<section class="hero"><h1>How the Visa Income Checker works</h1>
<p class="lead">How we turn official rules into amounts, where the numbers come from and what can make them change.</p></section>
<div class="testo">
<h2>1. The official rule</h2>
<p>For each visa we read the rule in an official source: a law or decree in the official gazette, a ministry or consulate page, or the immigration authority's page. The rule is either a fixed amount (for example €3,000 net a month for Hungary's White Card, €50,700 a year for Germany's Blue Card) or a percentage of an official index (for example 200% of Spain's minimum wage).</p>
<h2>2. The official index</h2>
<p>When the rule depends on an index, we take the index from the law that sets it or from the statistics office, and show how we got the monthly figure:</p>
{indici}
<h2>3. Family members</h2>
<p>Some rules add an amount for each family member (Spain, Portugal's D7, Croatia, the UK partner visa when extending under the pre-2024 rules). Others set no amount for family members, and we say so instead of inventing one. The calculator counts "adults including you" and "children under 18". If you type your income, the calculator compares it with the minimum: monthly rules are compared month by month, yearly thresholds with your yearly total (your monthly income × 12, 13 or 14 payments). For the UK visas it shows the other conditions instead of a yes/no, because the going rate for your occupation also counts.</p>
<h2>4. Monthly and yearly amounts</h2>
<p>When a rule is monthly, the yearly figure is the monthly amount × 12, except where the official wording counts 14 payments (Spain's digital nomad visa: €2,442 × 14 = €34,188, which equals €2,849 × 12). When a rule is yearly (most salary thresholds), the monthly figure is the yearly amount ÷ 12. In countries that pay 13th and 14th salaries, the monthly payslip is lower than this figure.</p>
<h2>5. Currency conversion</h2>
<p>We convert with the euro foreign exchange reference rates published by the European Central Bank every working day at around 16:00 CET. The rates are read again by your browser when you open a page, so the conversion follows the latest published rate. For an amount in another currency (for example pounds), we first convert it to euros and then to your currency. Conversions are indicative: consulates usually check the amount in the official currency, sometimes with their own rate, and exchange rates move.</p>
<p class="small">Source: ECB statistics – euro foreign exchange reference rates (<a href="https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml" rel="noopener">daily XML</a>). The reference rates are published for information purposes only.</p>
<h2>6. Checking and updating</h2>
<p>Every source shows the date we checked it. We re-check all programmes every January, when minimum wages, the Dutch and German salary thresholds, Denmark's pay limit and many other amounts change, and whenever an official page changes. If we cannot read an official source, we do not publish the visa.</p>
<h2>7. Visa refusal rates</h2>
<p>The <a href="{rel}visa-refusal-rates/">visa refusal rates</a> pages use the European Commission's yearly Schengen visa statistics (by Schengen country, consulate and country where the application was made) and the Home Office's quarterly UK entry clearance visa datasets (by nationality). A script downloads the official files, recalculates every rate and checks it against the official totals. <a href="{rel}visa-refusal-rates/#method">Full method</a>.</p>
<h2>Licences and attributions</h2>
<ul><li>Laws, decrees and official notices (BOE, Gazzetta Ufficiale, Bundesanzeiger, Normattiva) are cited as facts with a link to the official text; we do not reproduce the documents.</li>
<li>Exchange rates: European Central Bank, euro foreign exchange reference rates (source: ECB).</li>
<li>UK: contains public sector information licensed under the Open Government Licence v3.0 (GOV.UK and Home Office immigration statistics).</li>
<li>Schengen visa statistics: European Commission, DG Migration and Home Affairs (reuse authorised with acknowledgement of the source).</li>
<li>Other ministry and immigration authority pages are cited with links; the amounts are facts taken from them.</li></ul>
<h2>Not covered yet</h2>
<p>Greece (digital nomad visa and financially independent person visa), Cyprus, Malta, Estonia, Czechia, Romania, Latvia, Iceland, Costa Rica, Brazil, Panama, Colombia, Thailand, the United Arab Emirates and Mexico: the official page could not be read by our checks, gave conflicting figures, or (Mexico) the amount depends on the consulate. Colombia's rule is in Colombian pesos, a currency the ECB does not publish.</p>
</div>
{AVVISO}
{AD}"""
    pagina("how-it-works/", "How it works: official rules, indices and ECB exchange rates | Visa Income Checker",
           "How the Visa Income Checker calculates minimum income for visas: official rules, official indices (SMI, IPREM, RMMG, average salary), family members and ECB exchange rates.",
           corpo, briciole=[("How it works", "how-it-works/")])


def about():
    rel = "../"
    elenco = "".join(f'<h3><a href="{rel}{P["slug"]}/">{escape(nome_prog(P))}</a></h3>{fonti_html(fonti_prog(P))}' for P in PROG)
    corpo = f"""<section class="hero"><h1>About {NOME}</h1></section><div class="testo">
<p>{NOME} is an independent project that turns official visa income rules into a simple calculator, for the main applicant and each family member, in your currency. We are not affiliated with any government, consulate, immigration authority, law firm or visa agency.</p>
<h2>Rules we follow</h2>
<ul><li>Every amount comes from an official source (law, official gazette, ministry, consulate, immigration authority or statistics office). The link and the date we checked it are printed under the figure.</li>
<li>No blogs, agencies or other visa sites are used as sources. If we cannot read the official rule, the visa is not published.</li>
<li>This is information, not immigration or legal advice. Requirements change and consulates can ask for more: always check the official page or ask the consulate.</li></ul>
<h2>Visa refusal rates: sources</h2>
<ul class="fonti"><li><a href="{escape(F_UE[A1]["url"])}" rel="noopener">European Commission, Visa statistics for consulates {A1}</a> and <a href="{escape(F_UE[A0]["url"])}" rel="noopener">{A0}</a> (XLSX), downloaded on {data_lunga(F_UE[A1]["scaricato_il"])}</li>
<li><a href="{escape(F_UK["url"])}" rel="noopener">Home Office, {escape(F_UK["titolo"])}</a> (XLSX, published {escape(F_UK["pubblicato"])}), downloaded on {data_lunga(F_UK["scaricato_il"])}</li></ul>
<h2>All sources, visa by visa</h2>
{elenco}
<h2>Corrections</h2>
<p>Spotted a change or a mistake? <a href="{rel}contact/?ref=about">Tell us</a>.</p></div>"""
    pagina("about/", f"About and sources | {NOME}", "Who runs the Visa Income Checker and the official sources for every visa income requirement.",
           corpo, briciole=[("About", "about/")])


def contatti():
    rel = "../"
    corpo = f"""<section class="hero"><h1>Contact</h1><p class="lead">Spotted a change in an official amount, a mistake, or a visa you would like us to add? Write to us here. We cannot give advice on individual applications.</p></section>
<section class="card"><form class="form ajax" name="contact" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="contact"><input type="hidden" name="source" value="">
<p class="hp"><label>Do not fill this in <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Your email<input type="email" name="email" required autocomplete="email"></label>
<label>Visa or country (optional)<input type="text" name="visa" maxlength="200"></label>
<label>Message<textarea name="message" rows="6" required maxlength="4000"></textarea></label>
<label class="check"><input type="checkbox" name="consent" value="yes" required><span>I have read the <a href="{rel}privacy.html">privacy notice</a>.</span></label>
<button class="btn" type="submit">Send</button><p class="errore" data-errore hidden>Sorry, it did not work. Please try again.</p></form>
<div class="ok" data-ok hidden><strong>Thank you.</strong> We will check the official source and reply by email.</div></section>"""
    pagina("contact/", f"Contact | {NOME}", f"Contact {NOME}: report a change in an official visa income requirement or ask for a visa.", corpo,
           briciole=[("Contact", "contact/")])


def privacy():
    # Cookie, link di affiliazione e pubblicità: con AdSense acceso (monetizzazione.json) o con link di affiliazione, il testo
    # comune di monetizzazione.py (GoatCounter senza cookie, pubblicità con il consenso di Google); altrimenti il testo di oggi.
    cookie = MON.privacy_cookie("en", SITO_ID, ci_sono_affiliati()) or """<h2>Cookies, visit counter and affiliate links</h2><p>This site does not use profiling cookies. To count visits we use <a href="https://www.goatcounter.com/" rel="noopener">GoatCounter</a>, a privacy-friendly counter: it sets no cookies and stores nothing in your browser, builds no profiles and does not store your IP address, your full browser signature or any identifier. It keeps only aggregate numbers (page, hour or day, browser, country, screen width) on servers in the European Union and shares nothing with third parties; see <a href="https://www.goatcounter.com/help/privacy" rel="noopener">GoatCounter's privacy policy</a>. Some pages contain an affiliate link to SafetyWing (marked "Affiliate"): our site sets no cookie for it, but if you click it you go to SafetyWing's website, which uses its own cookies under its own privacy policy and tells SafetyWing that you came from us. If we add advertising in the future, we will update this notice and ask for your consent where required before any advertising cookies are used.</p>"""
    corpo = f"""<section class="hero"><h1>Privacy notice</h1><p class="small">Last updated: October 2026</p></section><div class="testo">
<h2>Who is responsible</h2><p>The data controller is Massimiliano Cori (Italy), who runs {NOME} as an independent project. You can contact us through the <a href="contact/">contact form</a>.</p>
<h2>What we collect</h2><p>Only what you type in the contact form: your email, the visa or country and your message. We also record the page or link you came from, to understand which pages need corrections. The calculator runs in your browser: the household, currency and income you type in it are not sent to us.</p>
<h2>Exchange rates</h2><p>To show up-to-date conversions, your browser downloads a small file of exchange rates from GitHub (raw.githubusercontent.com), which receives your IP address as for any web request. No other data is sent.</p>
<h2>Why</h2><p>To answer your messages and correct the site. The legal basis is your consent (Art. 6(1)(a) GDPR), which you can withdraw at any time.</p>
<h2>Who processes data for us</h2><p>The site and its form are hosted by Netlify, Inc., which stores form data on our behalf and may process it outside the EU with the safeguards required by the GDPR (standard contractual clauses). We do not sell or share your data.</p>
{cookie}
<h2>How long</h2><p>Messages are kept for up to 12 months after our last exchange.</p>
<h2>Your rights</h2><p>You can ask for access, correction, deletion, restriction, portability and objection (Articles 15–22 GDPR) and you can complain to the Italian data protection authority (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>) or the authority in your country.</p></div>"""
    pagina("privacy.html", f"Privacy | {NOME}", f"Privacy notice of {NOME}.", corpo)


# ---------------------------------------------------------------- Visa refusal rates (sezione approvata il 15/10/2026)
# Dati: dati/rifiuti.json, scritto da raccolta/rifiuti.py dai file ufficiali (Commissione Europea, Home Office).
RIF = json.loads((DATI / "rifiuti.json").read_text(encoding="utf-8"))
ANNI_UE = sorted(RIF["schengen"], key=int)
A1, A0 = ANNI_UE[-1], ANNI_UE[-2]  # anno più recente e anno di confronto
UE = RIF["schengen"]
F_UE = {a: RIF["fonti"][f"schengen_{a}"] for a in ANNI_UE}
F_UK = RIF["fonti"]["uk"]
TRIM = RIF["uk"]["trimestri"]
T1, T0 = TRIM[-4:], TRIM[-8:-4]  # anno che finisce con l'ultimo trimestre, e l'anno prima
UKN = RIF["uk"]["naz"]
SEZ = "visa-refusal-rates/"
SOGLIA_PAGINA = 10000     # domande nell'anno più recente per avere una pagina del Paese
SOGLIA_CLASSIFICA = 500   # decisioni minime per la classifica "lowest / highest"
SOGLIA_POCO = 100         # sotto questo numero di decisioni il tasso è segnato come poco significativo
SOGLIA_UK = 500           # decisioni minime (visti turistici, 4 trimestri) per mostrare il Regno Unito
URL_COMMISSIONE_DOMANDA = "https://home-affairs.ec.europa.eu/policies/schengen/visa-policy/applying-schengen-visa_en"
DATA_COMMISSIONE_DOMANDA = "2026-10-15"  # letta il 15/10/2026 (HTTP 200): dove fare domanda, assicurazione, rifiuto e ricorso
_SW = AFFILIATI.get("_safetywing_schengen", {})
URL_SAFETYWING = _SW.get("url", "")

_NOMI = {"TÜRKIYE": "Türkiye", "RUSSIAN FEDERATION": "Russia", "USA": "United States", "COTE D'IVOIRE": "Côte d'Ivoire",
         "CONGO (DEMOCRATIC REPUBLIC)": "DR Congo", "CONGO (BRAZZAVILLE)": "Republic of the Congo", "HONG KONG S.A.R.": "Hong Kong",
         "MACAO S.A.R.": "Macao", "PALESTINIAN AUTHORITY": "Palestinian territories"}
_SLUG = {"COTE D'IVOIRE": "cote-d-ivoire", "CONGO (DEMOCRATIC REPUBLIC)": "dr-congo", "CONGO (BRAZZAVILLE)": "republic-of-the-congo"}
# Nome della stessa nazionalità nei dati del Home Office (quando è diverso)
_NOMI_UK = {"TÜRKIYE": "Turkey", "RUSSIAN FEDERATION": "Russia", "USA": "United States", "COTE D'IVOIRE": "Ivory Coast",
            "CONGO (DEMOCRATIC REPUBLIC)": "Congo (Democratic Republic)", "CONGO (BRAZZAVILLE)": "Congo", "HONG KONG S.A.R.": "Hong Kong",
            "MACAO S.A.R.": "Macau", "PALESTINIAN AUTHORITY": "Palestine", "MYANMAR": "Myanmar (Burma)", "CZECH REPUBLIC": "Czechia"}
_NOMI_UK_INV = {v: k for k, v in _NOMI_UK.items()}


def nome_paese(n):
    if n in _NOMI:
        return _NOMI[n]
    t = n.title()
    for w in (" And ", " Of ", " The "):
        t = t.replace(w, w.lower())
    return t


def slug_testo(t):
    import unicodedata
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


_CON_ARTICOLO = {"United States", "United Kingdom", "United Arab Emirates", "Philippines", "Dominican Republic", "Republic of the Congo",
                 "Palestinian territories", "Netherlands", "Czech Republic", "Central African Republic", "Comoros", "Gambia", "Bahamas"}


def art(n, maiuscola=False):
    """Nome con l'articolo quando serve in inglese ('the United States', 'the Philippines')."""
    if n in _CON_ARTICOLO:
        return ("The " if maiuscola else "the ") + n
    return n


def slug_paese(n):
    return _SLUG.get(n) or slug_testo(nome_paese(n))


_PAROLE_MINUSCOLE = {"De", "Da", "Do", "Dos", "Das", "Del", "La", "Las", "Los", "Of", "Es", "Du", "Des", "Am", "And"}


def nome_consolato(n):
    """Nome del consolato dal file della Commissione (in maiuscolo) in forma leggibile:
    'WASHINGTON, DC' -> 'Washington, DC', 'PORT OF SPAIN' -> 'Port of Spain', 'RIO DE JANEIRO' -> 'Rio de Janeiro'."""
    parti = n.split(", ")
    testa = parti[0].title()
    parole = testa.split(" ")
    testa = " ".join(w.lower() if i > 0 and w in _PAROLE_MINUSCOLE else w for i, w in enumerate(parole))
    coda = [x.upper() if len(x) == 2 and x.isalpha() else x.title() for x in parti[1:]]
    return ", ".join([testa] + coda)


def nome_uk(n):
    return _NOMI_UK.get(n, nome_paese(n))


def somma(righe):
    v = [0, 0, 0, 0]  # domande, visti uniformi rilasciati, LTV rilasciati, non rilasciati
    for r in righe:
        v[0] += r[3]; v[1] += r[4]; v[2] += r[5]; v[3] += r[6]
    return v


def decisioni(v):
    return v[1] + v[2] + v[3]


def tasso(v):
    """Formula della Commissione: non rilasciati / (uniformi rilasciati + LTV + non rilasciati)."""
    d = decisioni(v)
    return v[3] / d if d else None


def raggruppa(anno, i, filtro=None):
    out = defaultdict(lambda: [0, 0, 0, 0])
    for r in UE[anno]:
        if filtro is None or filtro(r):
            v = out[r[i]]
            v[0] += r[3]; v[1] += r[4]; v[2] += r[5]; v[3] += r[6]
    return dict(out)


def uk_somma(naz, gruppi, trimestri):
    v = [0, 0, 0, 0]  # concessi, rifiutati, ritirati, decaduti
    for g in gruppi:
        for q in trimestri:
            x = UKN.get(naz, {}).get(g, {}).get(q)
            if x:
                for i in range(4):
                    v[i] += x[i]
    return v


def uk_tasso(v):
    d = v[0] + v[1]
    return v[1] / d if d else None


GRUPPI_UK = ["Visitor", "Study", "Work", "Family", "Other"]
NOMI_GRUPPI_UK = {"Visitor": "Visitor visas", "Study": "Study visas", "Work": "Work visas", "Family": "Family visas",
                  "Other": "Other visas"}


def pct(x, dec=1):
    return "–" if x is None else f"{x * 100:.{dec}f}%"


def intero(n):
    return f"{n:,}"


def punti(a, b):
    """Variazione in punti percentuali, testo."""
    if a is None or b is None:
        return "–"
    d = round((a - b) * 100, 1)
    if d == 0:
        return "no change"
    return f"{'+' if d > 0 else '−'}{abs(d):.1f} pts"


def trimestre_testo(q):
    a, t = q.split()
    return f"{t} {a}"


def periodo_breve(tt):
    """'2025 Q3–2026 Q2' -> '12 months to Jun 2026'."""
    a1, q1 = tt[-1].split()
    return f"12 months to {dict(Q1='Mar', Q2='Jun', Q3='Sep', Q4='Dec')[q1]} {a1}"


def periodo_uk(tt):
    """'2025 Q3–2026 Q2' -> 'July 2025 to June 2026'."""
    inizio = {"Q1": "January", "Q2": "April", "Q3": "July", "Q4": "October"}
    fine = {"Q1": "March", "Q2": "June", "Q3": "September", "Q4": "December"}
    a0, q0 = tt[0].split()
    a1, q1 = tt[-1].split()
    return f"{inizio[q0]} {a0} to {fine[q1]} {a1}"


STATI_UE = sorted(set(r[0] for r in UE[A1]))
PER_STATO = {a: raggruppa(a, 0) for a in ANNI_UE}
PER_PAESE = {a: raggruppa(a, 1) for a in ANNI_UE}
TOT_UE = {a: somma(UE[a]) for a in ANNI_UE}
_STATI_MAIUSC = {s.upper() for s in STATI_UE}
PAESI_RIF = [p for p, v in sorted(PER_PAESE[A1].items(), key=lambda x: -x[1][0]) if v[0] >= SOGLIA_PAGINA and p not in _STATI_MAIUSC]
SLUG_RIF = {p: slug_paese(p) for p in PAESI_RIF}
SLUG_STATO = {s: slug_testo(s) for s in STATI_UE}


GRUPPI_UK_PAGINA = ["Visitor", "Study", "Work", "Family"]  # gruppi con una cifra in evidenza nelle pagine per nazionalità (dal 21/10/2026; Family dal 28/10/2026)
NOMI_BREVI_UK = {"Visitor": "visitor", "Study": "study", "Work": "work", "Family": "family"}
# Tipo di visto "Family: Partner" del Home Office (coniugi e partner), salvato da raccolta/rifiuti.py accanto ai gruppi (28/10/2026).
# È una parte del gruppo Family: non entra mai nei totali "All visas" (che sommano solo GRUPPI_UK).
PARTNER_UK = "Family: Partner"
NOME_PARTNER_UK = "Partner (spouse) visas"
DEF_FAMIGLIA_UK = ('"Family" is the Home Office group for people joining a British citizen or a person settled in the UK '
                   '(partners, children and other relatives) and for refugee family reunion; "partner" is the Home Office visa type '
                   '"Family: Partner", the route for spouses, civil partners and unmarried partners.')


def decisioni_uk(nuk, g):
    v = uk_somma(nuk, [g], T1)
    return v[0] + v[1]


def gruppi_uk_ok(p):
    """Gruppi di visti UK (turismo, studio, lavoro) con almeno SOGLIA_UK decisioni negli ultimi 4 trimestri."""
    nuk = nome_uk(p)
    return [g for g in GRUPPI_UK_PAGINA if decisioni_uk(nuk, g) >= SOGLIA_UK]


def ha_uk(p):
    return bool(gruppi_uk_ok(p))


def decisioni_uk_visitor(nuk):
    return decisioni_uk(nuk, "Visitor")


# Aggettivo di nazionalità per le pagine "easiest Schengen visa" (chiave = nome nel file della Commissione).
DEMONIMI = {
    "CHINA": "Chinese", "TÜRKIYE": "Turkish", "INDIA": "Indian", "RUSSIAN FEDERATION": "Russian", "MOROCCO": "Moroccan",
    "SAUDI ARABIA": "Saudi", "UNITED KINGDOM": "UK", "ALGERIA": "Algerian", "UNITED ARAB EMIRATES": "Emirati", "THAILAND": "Thai",
    "PHILIPPINES": "Filipino", "EGYPT": "Egyptian", "INDONESIA": "Indonesian", "SOUTH AFRICA": "South African", "TUNISIA": "Tunisian",
    "USA": "US", "KAZAKHSTAN": "Kazakhstani", "BELARUS": "Belarusian", "KUWAIT": "Kuwaiti", "LEBANON": "Lebanese", "VIETNAM": "Vietnamese",
    "NIGERIA": "Nigerian", "ARMENIA": "Armenian", "IRAN": "Iranian", "ECUADOR": "Ecuadorian", "AZERBAIJAN": "Azerbaijani", "QATAR": "Qatari",
    "PAKISTAN": "Pakistani", "COTE D'IVOIRE": "Ivorian", "KENYA": "Kenyan", "JORDAN": "Jordanian", "ANGOLA": "Angolan", "SENEGAL": "Senegalese",
    "IRAQ": "Iraqi", "GHANA": "Ghanaian", "UZBEKISTAN": "Uzbek", "CAMEROON": "Cameroonian", "OMAN": "Omani", "DOMINICAN REPUBLIC": "Dominican",
    "CONGO (DEMOCRATIC REPUBLIC)": "Congolese", "CANADA": "Canadian", "LIBYA": "Libyan", "SINGAPORE": "Singaporean", "BANGLADESH": "Bangladeshi",
    "CUBA": "Cuban", "ISRAEL": "Israeli", "KYRGYZSTAN": "Kyrgyz", "IRELAND": "Irish", "CAPE VERDE": "Cape Verdean", "ETHIOPIA": "Ethiopian",
    "CONGO (BRAZZAVILLE)": "Congolese", "SRI LANKA": "Sri Lankan", "MAURITANIA": "Mauritanian", "BAHRAIN": "Bahraini", "GUINEA": "Guinean",
    "MONGOLIA": "Mongolian", "MOZAMBIQUE": "Mozambican", "SURINAME": "Surinamese", "UGANDA": "Ugandan", "SERBIA": "Serbian",
    "AUSTRALIA": "Australian", "GABON": "Gabonese", "MADAGASCAR": "Malagasy", "JAPAN": "Japanese", "BOLIVIA": "Bolivian", "TANZANIA": "Tanzanian",
    "HONG KONG S.A.R.": "Hong Kong", "BENIN": "Beninese", "CAMBODIA": "Cambodian", "CYPRUS": "Cypriot", "MALI": "Malian", "GEORGIA": "Georgian",
    "TOGO": "Togolese", "EQUATORIAL GUINEA": "Equatoguinean", "MACAO S.A.R.": "Macanese", "PALESTINIAN AUTHORITY": "Palestinian",
    "NEPAL": "Nepali", "MYANMAR": "Myanmar", "MALAYSIA": "Malaysian", "SUDAN": "Sudanese", "ZIMBABWE": "Zimbabwean", "ZAMBIA": "Zambian",
    "RWANDA": "Rwandan", "SYRIA": "Syrian", "YEMEN": "Yemeni", "AFGHANISTAN": "Afghan", "TAJIKISTAN": "Tajik", "TURKMENISTAN": "Turkmen",
    "MOLDOVA": "Moldovan", "UKRAINE": "Ukrainian", "ALBANIA": "Albanian", "KOSOVO": "Kosovar", "BOSNIA AND HERZEGOVINA": "Bosnian",
    "NORTH MACEDONIA": "Macedonian", "MONTENEGRO": "Montenegrin", "MEXICO": "Mexican", "BRAZIL": "Brazilian", "COLOMBIA": "Colombian",
    "PERU": "Peruvian", "VENEZUELA": "Venezuelan", "ARGENTINA": "Argentine", "CHILE": "Chilean", "JAMAICA": "Jamaican", "HAITI": "Haitian",
    "TRINIDAD AND TOBAGO": "Trinidadian", "NEW ZEALAND": "New Zealand", "SOUTH KOREA": "South Korean", "KOREA (REPUBLIC)": "South Korean",
    "TAIWAN": "Taiwanese", "BURKINA FASO": "Burkinabè", "NIGER": "Nigerien", "CHAD": "Chadian", "SIERRA LEONE": "Sierra Leonean",
    "LIBERIA": "Liberian", "GAMBIA": "Gambian", "GUINEA-BISSAU": "Bissau-Guinean", "DJIBOUTI": "Djiboutian", "ERITREA": "Eritrean",
    "SOMALIA": "Somali", "MALAWI": "Malawian", "NAMIBIA": "Namibian", "BOTSWANA": "Botswanan", "MAURITIUS": "Mauritian",
    "SEYCHELLES": "Seychellois", "BHUTAN": "Bhutanese", "LAOS": "Lao", "BRUNEI": "Bruneian", "MALDIVES": "Maldivian",
}


# Paesi i cui cittadini non hanno bisogno del visto Schengen (allegato II) o sono cittadini UE: lì le domande vengono da residenti
# di altre nazionalità, quindi "Irish applicants" o "UK applicants" sarebbe sbagliato; si scrive "applicants from Ireland" (revisione del 21/10/2026).
ESENTI_VISTO = {"AUSTRALIA", "CANADA", "CYPRUS", "GEORGIA", "HONG KONG S.A.R.", "IRELAND", "ISRAEL", "JAPAN", "SERBIA", "SINGAPORE",
                "UNITED ARAB EMIRATES", "UNITED KINGDOM", "USA"}


def demonimo(p):
    """'Pakistani applicants'; se manca l'aggettivo o i cittadini non hanno bisogno del visto: 'applicants from Pakistan'."""
    d = DEMONIMI.get(p)
    return f"{d} applicants" if d and p not in ESENTI_VISTO else f"applicants from {art(nome_paese(p))}"


_B.update({
    "Belgium": '<path fill="#000" d="M0 0h10v20H0z"/><path fill="#FDDA24" d="M10 0h10v20H10z"/><path fill="#EF3340" d="M20 0h10v20H20z"/>',
    "Bulgaria": '<path fill="#fff" d="M0 0h30v6.67H0z"/><path fill="#00966E" d="M0 6.67h30v6.66H0z"/><path fill="#D62612" d="M0 13.33h30V20H0z"/>',
    "Czech Republic": '<path fill="#fff" d="M0 0h30v10H0z"/><path fill="#D7141A" d="M0 10h30v10H0z"/><path fill="#11457E" d="M0 0l15 10L0 20z"/>',
    "Estonia": '<path fill="#0072CE" d="M0 0h30v6.67H0z"/><path fill="#000" d="M0 6.67h30v6.66H0z"/><path fill="#fff" d="M0 13.33h30V20H0z"/>',
    "Finland": '<path fill="#fff" d="M0 0h30v20H0z"/><path fill="#002F6C" d="M8.5 0h4.5v20H8.5zM0 7.75h30v4.5H0z"/>',
    "Greece": '<path fill="#0D5EAF" d="M0 0h30v20H0z"/><path fill="#fff" d="M0 2.22h30v2.22H0zM0 6.67h30v2.22H0zM0 11.11h30v2.22H0zM0 15.56h30v2.22H0z"/>'
              '<path fill="#0D5EAF" d="M0 0h11.1v11.1H0z"/><path fill="#fff" d="M4.44 0h2.22v11.1H4.44zM0 4.44h11.1v2.22H0z"/>',
    "Iceland": '<path fill="#02529C" d="M0 0h30v20H0z"/><path fill="#fff" d="M8 0h5v20H8zM0 7.5h30v5H0z"/><path fill="#DC1E35" d="M9.25 0h2.5v20h-2.5zM0 8.75h30v2.5H0z"/>',
    "Latvia": '<path fill="#9E3039" d="M0 0h30v20H0z"/><path fill="#fff" d="M0 8h30v4H0z"/>',
    "Lithuania": '<path fill="#FDB913" d="M0 0h30v6.67H0z"/><path fill="#006A44" d="M0 6.67h30v6.66H0z"/><path fill="#C1272D" d="M0 13.33h30V20H0z"/>',
    "Luxembourg": '<path fill="#EA141D" d="M0 0h30v6.67H0z"/><path fill="#fff" d="M0 6.67h30v6.66H0z"/><path fill="#51ADDA" d="M0 13.33h30V20H0z"/>',
    "Malta": '<path fill="#fff" d="M0 0h15v20H0z"/><path fill="#CF142B" d="M15 0h15v20H15z"/><path fill="#9A9A9A" d="M2.5 2.5h3v1h-1v1h1v1h-3v-1h1v-1h-1z"/>',
    "Norway": '<path fill="#BA0C2F" d="M0 0h30v20H0z"/><path fill="#fff" d="M8 0h5v20H8zM0 7.5h30v5H0z"/><path fill="#00205B" d="M9.25 0h2.5v20h-2.5zM0 8.75h30v2.5H0z"/>',
    "Poland": '<path fill="#fff" d="M0 0h30v10H0z"/><path fill="#DC143C" d="M0 10h30v10H0z"/>',
    "Romania": '<path fill="#002B7F" d="M0 0h10v20H0z"/><path fill="#FCD116" d="M10 0h10v20H10z"/><path fill="#CE1126" d="M20 0h10v20H20z"/>',
    "Slovakia": '<path fill="#fff" d="M0 0h30v6.67H0z"/><path fill="#0B4EA2" d="M0 6.67h30v6.66H0z"/><path fill="#EE1C25" d="M0 13.33h30V20H0z"/>'
                '<path fill="#EE1C25" stroke="#fff" stroke-width=".8" d="M6 4.5h8v6.5a4 4 0 0 1-8 0z"/><path fill="#fff" d="M9.4 6h1.2v6h-1.2zM8 7.3h4v1H8z"/>',
    "Slovenia": '<path fill="#fff" d="M0 0h30v6.67H0z"/><path fill="#005DA4" d="M0 6.67h30v6.66H0z"/><path fill="#ED1C24" d="M0 13.33h30V20H0z"/>'
                '<path fill="#005DA4" stroke="#ED1C24" stroke-width=".6" d="M6 3.5h6v5.5a3 3 0 0 1-6 0z"/><path fill="#fff" d="M7 8.5l2-2.5 2 2.5z"/>',
    "Switzerland": '<path fill="#DA291C" d="M0 0h30v20H0z"/><path fill="#fff" d="M13.25 4.5h3.5v11h-3.5zM9.5 8.25h11v3.5h-11z"/>',
})


def cella_tasso(t, poco=False):
    """Cella numerica con il tasso e una barretta proporzionale (piena dal 50% in su)."""
    if t is None:
        return '<td class="n" data-v="">–</td>'
    larg = max(2, min(100, round(t * 200, 1)))  # barra piena = 50% o più
    return (f'<td class="n" data-v="{t:.6f}"><span class="tb" aria-hidden="true"><i style="width:{larg}%"></i></span>'
            f'<span class="tv">{pct(t)}{"*" if poco else ""}</span></td>')


def th_ord(testo, n=True, primo="descending"):
    return f'<th class="{"n" if n else ""}" scope="col" data-primo="{primo}"><button type="button" class="ord">{testo}</button></th>'


def fonte_ue(anno, rel_pag=False):
    f = F_UE[anno]
    return (f'<a href="{escape(f["url"])}" rel="noopener">European Commission, Visa statistics for consulates {anno}</a> '
            f'({escape(f["formato"])}, downloaded on {data_lunga(f["scaricato_il"])})')


def fonte_ue_p(*anni):
    return (f'<p class="fonte">Source: ' + "; ".join(fonte_ue(a) for a in anni) +
            f'. Short-stay (Schengen) visas, calendar year. <a href="{escape(F_UE[A1]["pagina"])}" rel="noopener">All years on the Commission website</a>.</p>')


def fonte_uk_p():
    return (f'<p class="fonte">Source: <a href="{escape(F_UK["url"])}" rel="noopener">Home Office, {escape(F_UK["titolo"])}</a> '
            f'(XLSX, published {escape(F_UK["pubblicato"])}, downloaded on {data_lunga(F_UK["scaricato_il"])}; next update {escape(F_UK["prossimo"])}). '
            f'Refusal rate = refused ÷ (granted + refused), as in the Home Office grant rate; withdrawn and lapsed applications are excluded. '
            f'Figures from 2026 Q1 are provisional.</p>')


AVVISO_RIF = ('<p class="avviso"><strong>Statistics, not advice.</strong> These are official figures for all applications made in a past period. '
              'They cannot predict the decision on your application, and a lower rate does not make a visa easier for you: '
              'you must apply to the Schengen country where you will spend the most time (or, for equal stays, the one you enter first), '
              'at the consulate responsible for the place where you legally live. Always follow the consulate\'s official requirements.</p>')


def box_assicurazione(rel):
    """Assicurazione di viaggio (richiesta per il visto Schengen). Link di affiliazione SafetyWing con dicitura chiara."""
    req = (f'A Schengen visa application must include medical insurance covering emergency medical care, hospitalisation and repatriation '
           f'(<a href="{URL_COMMISSIONE_DOMANDA}" rel="noopener">European Commission</a>, checked on {data_lunga(DATA_COMMISSIONE_DOMANDA)}).')
    if not URL_SAFETYWING:
        return f'<section class="card aff-r"><h2>Travel medical insurance</h2><p>{req}</p></section>'
    return (f'<section class="card aff-r" aria-labelledby="aff-r-h"><div class="aff-r-t"><span class="ic">{ico("shield")}</span>'
            f'<h2 id="aff-r-h">Travel medical insurance for your application</h2><span class="aff-tag">Affiliate</span></div>'
            f'<p>{req} Check the minimum cover, the countries and the dates the consulate asks for, and the certificate you need, before you buy any policy.</p>'
            f'<p class="aff-r-cta"><a class="btn" href="{escape(URL_SAFETYWING)}" rel="sponsored noopener" target="_blank">See SafetyWing travel medical insurance{ico("arrow")}'
            f'<span class="sr"> (opens in a new tab)</span></a></p>'
            f'<p class="small">SafetyWing sells travel medical insurance online. {MON.RIGA_EN} '
            f'Buying insurance does not change the decision on your visa, and we do not know whether a given consulate accepts a given policy: check before you pay.</p></section>')


def tabella_stati_paese(p, rel):
    s1 = raggruppa(A1, 0, lambda r: r[1] == p)
    s0 = raggruppa(A0, 0, lambda r: r[1] == p)
    righe = []
    for s, v in sorted(s1.items(), key=lambda x: -x[1][0]):
        if v[0] == 0 and decisioni(v) == 0:
            continue
        poco = decisioni(v) < SOGLIA_POCO
        righe.append(f'<tr{" class=\"poco\"" if poco else ""}><td><a href="{rel}{SEZ}schengen/{SLUG_STATO[s]}/">{escape(s)}</a></td>'
                     f'{cella_tasso(tasso(v), poco)}{cella_tasso(tasso(s0[s]) if s in s0 else None)}'
                     f'<td class="n" data-v="{v[0]}">{intero(v[0])}</td><td class="n" data-v="{v[1]}">{intero(v[1])}</td>'
                     f'<td class="n" data-v="{v[3]}">{intero(v[3])}</td></tr>')
    return ('<div class="tab compatta"><table class="ord"><thead><tr>' + th_ord("Schengen country", False, "ascending") +
            th_ord(f"Not issued {A1}", primo="ascending") + th_ord(f"{A0}", primo="ascending") + th_ord("Applications") +
            th_ord("Visas issued") + th_ord("Not issued") +
            f'</tr></thead><tbody>{"".join(righe)}</tbody></table></div>'), s1, s0


def classifica(s1, inverso=False, n=5):
    ok = [(s, v) for s, v in s1.items() if decisioni(v) >= SOGLIA_CLASSIFICA]
    ok.sort(key=lambda x: tasso(x[1]), reverse=inverso)
    return ok[:n], len(ok)


def lista_classifica(voci, rel, classe="", mx=None):
    # mx: stessa scala per "Lowest" e "Highest", altrimenti le barre delle due liste non si possono confrontare
    mx = mx or max([tasso(v) for _, v in voci] + [0.01])
    li = "".join(f'<li><span class="pos">{i}</span><span><a href="{rel}{SEZ}schengen/{SLUG_STATO[s]}/">{escape(s)}</a>'
                 f'<small>{intero(decisioni(v))} decisions</small><span class="bar {classe}" aria-hidden="true"><i style="width:{max(2, round(tasso(v) / mx * 100))}%"></i></span></span>'
                 f'<span class="v">{pct(tasso(v))}</span></li>' for i, (s, v) in enumerate(voci, 1))
    return f'<ol class="classifica">{li}</ol>'


def tabella_consolati(p):
    righe = []
    for r in sorted((r for r in UE[A1] if r[1] == p), key=lambda r: -r[3]):
        v = r[3:7]
        v = [v[0], v[1], v[2], v[3]]
        if decisioni(v) == 0 and v[0] == 0:
            continue
        poco = decisioni(v) < SOGLIA_POCO
        righe.append(f'<tr{" class=\"poco\"" if poco else ""}><td>{escape(r[0])}</td><td>{escape(nome_consolato(r[2]))}</td>'
                     f'{cella_tasso(tasso(v), poco)}<td class="n" data-v="{v[0]}">{intero(v[0])}</td><td class="n" data-v="{v[3]}">{intero(v[3])}</td></tr>')
    return ('<div class="tab compatta"><table class="ord"><thead><tr>' + th_ord("Country", False, "ascending") + th_ord("Consulate", False, "ascending") +
            th_ord("Rate", primo="ascending") + th_ord("Applications") + th_ord("Not issued") + f'</tr></thead><tbody>{"".join(righe)}</tbody></table></div>'), len(righe)


def sezione_uk(p, nome):
    nuk = nome_uk(p)
    if p == "UNITED KINGDOM":
        return (f'<h2>UK visa refusal rates</h2><p>The UK figures are by nationality: see <a href="../uk/">UK visa refusal rates for all nationalities</a>.</p>'), None
    ok = gruppi_uk_ok(p)
    if not ok:
        d = decisioni_uk_visitor(nuk)
        return (f'<h2>UK visa refusal rate</h2><p>The Home Office data show {intero(d)} UK visitor visa decisions for nationals of {escape(art(nome))} '
                f'from {periodo_uk(T1)} (and fewer than {intero(SOGLIA_UK)} for study and work visas), fewer than the {intero(SOGLIA_UK)} we need to show a meaningful rate. '
                f'See <a href="../uk/">UK refusal rates for all nationalities</a>.</p>{fonte_uk_p()}'), None
    righe = []
    for g in GRUPPI_UK + ["All"]:
        gg = GRUPPI_UK if g == "All" else [g]
        v1, v0 = uk_somma(nuk, gg, T1), uk_somma(nuk, gg, T0)
        if v1[0] + v1[1] == 0:
            continue
        poco = v1[0] + v1[1] < SOGLIA_POCO
        cls = ' class="tot-r"' if g == "All" else (' class="poco"' if poco else "")
        righe.append(f'<tr{cls}><td>{"All visas" if g == "All" else NOMI_GRUPPI_UK[g]}</td>'
                     f'{cella_tasso(uk_tasso(v1), poco)}{cella_tasso(uk_tasso(v0))}'
                     f'<td class="n">{intero(v1[0] + v1[1])}</td><td class="n">{intero(v1[0])}</td><td class="n">{intero(v1[1])}</td></tr>')
        if g == "Family":  # sotto-voce: visti del partner (coniuge), solo con almeno SOGLIA_POCO decisioni
            p1, p0 = uk_somma(nuk, [PARTNER_UK], T1), uk_somma(nuk, [PARTNER_UK], T0)
            if p1[0] + p1[1] >= SOGLIA_POCO:
                righe.append(f'<tr{" class=\"poco\"" if p1[0] + p1[1] < SOGLIA_UK else ""}><td>of which {NOME_PARTNER_UK.lower()}</td>'
                             f'{cella_tasso(uk_tasso(p1), p1[0] + p1[1] < SOGLIA_UK)}{cella_tasso(uk_tasso(p0)) if p0[0] + p0[1] >= SOGLIA_POCO else cella_tasso(None)}'
                             f'<td class="n">{intero(p1[0] + p1[1])}</td><td class="n">{intero(p1[0])}</td><td class="n">{intero(p1[1])}</td></tr>')
    tassi = {g: (uk_tasso(uk_somma(nuk, [g], T1)), decisioni_uk(nuk, g)) for g in ok}
    primo = ok[0]  # turismo se c'è, altrimenti studio o lavoro
    vis1 = uk_somma(nuk, [primo], T1)
    # andamento trimestrale del gruppo principale
    tq = []
    for q in TRIM:
        v = uk_somma(nuk, [primo], [q])
        tq.append((q, uk_tasso(v), v[0] + v[1]))
    mx = max([t for _, t, _ in tq if t is not None] + [0.05])
    barre = "".join(f'<li><span class="tq-v">{pct(t)}</span><span class="tq-c"><span class="tq-b" style="height:{max(3, round((t or 0) / mx * 100))}%"></span></span>'
                    f'<span class="tq-l">{q.split()[1]}<br>{q.split()[0]}</span><span class="sr"> {intero(d)} decisions</span></li>' for q, t, d in tq)
    altri = [g for g in ok if g != primo]
    frase_altri = ""
    if altri:
        frase_altri = " " + "; ".join(f'<strong>{pct(tassi[g][0])}</strong> of {NOMI_BREVI_UK[g]} visa decisions were refused ({intero(tassi[g][1])} decisions)' for g in altri) + "."
    # studio e lavoro trimestre per trimestre (solo i gruppi con abbastanza decisioni)
    tab_q = ""
    gruppi_q = [g for g in ("Study", "Work", "Family") if g in ok]
    if gruppi_q:
        righe_q = []
        for q in TRIM:
            celle = ""
            for g in gruppi_q:
                v = uk_somma(nuk, [g], [q])
                d = v[0] + v[1]
                celle += f'{cella_tasso(uk_tasso(v), d < SOGLIA_POCO) if d else cella_tasso(None)}<td class="n" data-v="{d}">{intero(d)}</td>'
            righe_q.append(f'<tr><td>{trimestre_testo(q)}</td>{celle}</tr>')
        testa = "".join(f'{th_ord(f"{NOMI_GRUPPI_UK[g]} refused", primo="ascending")}{th_ord("Decisions")}' for g in gruppi_q)
        nomi_q = [NOMI_BREVI_UK[g] for g in gruppi_q]
        tab_q = (f'<h3>{(nomi_q[0] if len(nomi_q) == 1 else ", ".join(nomi_q[:-1]) + " and " + nomi_q[-1]).capitalize()} visas, quarter by quarter</h3>'
                 f'<div class="tab compatta"><table class="ord"><thead><tr>{th_ord("Quarter", False, "ascending")}{testa}</tr></thead><tbody>{"".join(righe_q)}</tbody></table></div>'
                 f'<p class="fonte">Source: <a href="{escape(F_UK["url"])}" rel="noopener">Home Office, {escape(F_UK["titolo"])}</a> (XLSX, published {escape(F_UK["pubblicato"])}, downloaded on {data_lunga(F_UK["scaricato_il"])}). '
                 f'"Study" is the Home Office group for sponsored study (Student, Child Student) and short-term study visas; "Work" groups all work routes '
                 f'(Skilled Worker, Health and Care Worker, temporary and seasonal work, Global Business Mobility, talent and business visas, and their dependants). '
                 + (DEF_FAMIGLIA_UK + " " if "Family" in gruppi_q else "") +
                 f'* Fewer than {SOGLIA_POCO} decisions; 2026 figures are provisional.</p>')
    nomi_g = [NOMI_BREVI_UK[g] for g in ok]
    tipi = nomi_g[0] if len(nomi_g) == 1 else ", ".join(nomi_g[:-1]) + " and " + nomi_g[-1]
    pf = uk_somma(nuk, [PARTNER_UK], T1)
    frase_partner = ""
    if "Family" in ok and pf[0] + pf[1] >= SOGLIA_POCO:
        frase_partner = (f' For partner (spouse) visas alone the rate was {pct(uk_tasso(pf))} ({intero(pf[1])} refused out of {intero(pf[0] + pf[1])} decisions'
                         + (', a small number' if pf[0] + pf[1] < SOGLIA_UK else '') + f'; <a href="../uk/family-visas/">compare all nationalities</a>).')
    corpo = (f'<h2 id="uk">UK visa refusal rate for nationals of {escape(art(nome))}: {tipi} visas</h2>'
             f'<p class="lead">From {periodo_uk(T1)}, the UK refused <strong>{pct(uk_tasso(vis1))}</strong> of {NOMI_BREVI_UK[primo]} visa decisions for nationals of {escape(art(nome))} '
             f'({intero(vis1[1])} refused out of {intero(vis1[0] + vis1[1])}).{frase_altri}{frase_partner} Unlike the Schengen figures, the UK counts applicants by <strong>nationality</strong>, wherever they apply.'
             + ((f' With only {intero(vis1[0] + vis1[1])} visitor visa decisions, read this rate with care: where most nationals can visit the UK without a visa, '
                 f'the people who apply for one are a small and unusual group.' if primo == "Visitor" else
                 f' With only {intero(vis1[0] + vis1[1])} {NOMI_BREVI_UK[primo]} visa decisions, read this rate with care: a few refusals move it a lot.')
                if vis1[0] + vis1[1] < 5000 else '') + '</p>'
             f'<div class="tab compatta"><table><thead><tr><th scope="col">Visa type</th><th class="n" scope="col">Refused<br><span class="small">{periodo_breve(T1)}</span></th>'
             f'<th class="n" scope="col">Year before<br><span class="small">{periodo_breve(T0)}</span></th><th class="n" scope="col">Decisions</th><th class="n" scope="col">Granted</th>'
             f'<th class="n" scope="col">Refused</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>'
             f'{fonte_uk_p()}'
             f'<h3>{NOMI_GRUPPI_UK[primo]}, quarter by quarter</h3><ol class="trim" aria-label="UK {NOMI_BREVI_UK[primo]} visa refusal rate by quarter">{barre}</ol>'
             f'<p class="fonte">Source: Home Office, same file as above (published {escape(F_UK["pubblicato"])}, downloaded on {data_lunga(F_UK["scaricato_il"])}). Each bar is the share of {NOMI_BREVI_UK[primo]} visa decisions '
             f'taken in that quarter that were refusals; 2026 figures are provisional.</p>{tab_q}')
    return corpo, tassi


def pagina_rif_paese(p):
    rel = "../../"
    nome = nome_paese(p)
    slug = SLUG_RIF[p]
    v1, v0 = PER_PAESE[A1][p], PER_PAESE[A0].get(p)
    t1, t0 = tasso(v1), (tasso(v0) if v0 else None)
    tab, s1, s0 = tabella_stati_paese(p, rel)
    basso, n_ok = classifica(s1)
    alto, _ = classifica(s1, inverso=True, n=3)
    tab_c, n_c = tabella_consolati(p)
    uk_html, uk_r = sezione_uk(p, nome)
    con_uk = bool(uk_r)
    au_html, au_r = sezione_au(p, nome)
    nz_html, nz_r = sezione_nz(p, nome)
    ca_html, ca_r = sezione_ca(p, nome)
    dest = [x for x, r in (("Australia", au_r), ("New Zealand", nz_r), ("Canada", ca_r)) if r]
    rank_paesi = sorted(PAESI_RIF, key=lambda x: tasso(PER_PAESE[A1][x]))
    pos = rank_paesi.index(p) + 1
    facile = p in PAESI_FACILE
    link_facile = 'easiest-schengen-visa/' if facile else ""
    if basso:
        sb, vb = basso[0]
        frase_basso = (f'Easiest Schengen visa from {escape(art(nome))}, by the numbers: the lowest not-issued rate among Schengen countries with at least {intero(SOGLIA_CLASSIFICA)} decisions was '
                       f'<strong>{escape(sb)} ({pct(tasso(vb))})</strong>' + (f'; the highest was <strong>{escape(alto[0][0])} ({pct(tasso(alto[0][1]))})</strong>' if alto else "") +
                       '.' + (f' <a href="{link_facile}">Full ranking by country and consulate</a>.' if facile else ""))
    else:
        frase_basso = f'No Schengen country took {intero(SOGLIA_CLASSIFICA)} or more decisions on applications made in {escape(art(nome))}.'
    if n_ok >= 2:
        scala = max([tasso(v) for _, v in basso + alto] + [0.01])
        clas = (f'<h2 id="easiest">Easiest Schengen visa from {escape(art(nome))}: lowest and highest refusal rates ({A1})</h2>'
                f'<p class="lead">Which Schengen country has the lowest rejection rate for {escape(demonimo(p))}? Among the {n_ok} Schengen countries that decided at least {intero(SOGLIA_CLASSIFICA)} applications made in {escape(art(nome))} in {A1}, '
                f'<strong>{escape(basso[0][0])}</strong> had the lowest not-issued rate ({pct(tasso(basso[0][1]))}) and <strong>{escape(alto[0][0])}</strong> the highest ({pct(tasso(alto[0][1]))}). '
                f'Smaller numbers move too much from year to year to compare. These rates describe past decisions, not your chances.'
                + (f' See the <a href="{link_facile}">easiest Schengen visa from {escape(art(nome))}: all countries and consulates ranked</a>.' if facile else "") + '</p>'
                f'<div class="due"><div><h3>Lowest refusal rates</h3>{lista_classifica(basso, rel, "basso", scala)}</div><div><h3>Highest refusal rates</h3>{lista_classifica(alto, rel, "alto", scala)}</div></div>'
                f'<p class="avviso"><strong>A lower rate is not a guarantee, and you cannot choose freely.</strong> Each rate mixes different travellers, purposes and documents. '
                f'You must apply to the country of your main destination: the rule is on the <a href="{URL_COMMISSIONE_DOMANDA}" rel="noopener">European Commission page on applying for a Schengen visa</a> '
                f'(checked on {data_lunga(DATA_COMMISSIONE_DOMANDA)}). Applying to a country you do not plan to visit mainly can itself lead to a refusal.</p>'
                f'{fonte_ue_p(A1)}')
    else:
        clas = ""
    cambio = (f'{punti(t1, t0)} on {A0} ({pct(t0)})' if t0 is not None else f"no {A0} figure")
    uk_kpi = ""
    if con_uk:
        g1 = list(uk_r)[0]
        altri_uk = [g for g in uk_r if g != g1]
        kpi_uk = (f'<div class="kpi kpi-uk">' + "".join(f'<div><b>{pct(uk_r[g][0])}</b><span>{NOMI_BREVI_UK[g]} visas refused · {intero(uk_r[g][1])} decisions</span></div>' for g in altri_uk) + '</div>') if altri_uk else ""
        uk_kpi = (f'<p class="cifra cifra-2"><span class="c-lab">United Kingdom · nationals of {escape(art(nome))} · {periodo_uk(T1)}</span>'
                  f'<strong>{pct(uk_r[g1][0])}</strong> of {NOMI_BREVI_UK[g1]} visa decisions refused <a href="#uk">(details)</a></p>{kpi_uk}'
                  f'<p class="fonte">Source: <a href="{escape(F_UK["url"])}" rel="noopener">Home Office, entry clearance visa outcomes</a>, published {escape(F_UK["pubblicato"])}, downloaded on {data_lunga(F_UK["scaricato_il"])}</p>')
    vicini = [x for x in rank_paesi if x != p]
    altri = sorted(vicini, key=lambda x: abs(PER_PAESE[A1][x][0] - v1[0]))[:8]
    griglia_altri = "".join(f'<a href="../{SLUG_RIF[x]}/"><span class="ic">{ico("globe")}</span><span>{escape(nome_paese(x))}<small>{pct(tasso(PER_PAESE[A1][x]))} not issued in {A1}</small></span></a>' for x in altri)
    altre = (["the UK"] if con_uk else []) + dest
    titolo_h1 = (f"Visa refusal rates for {art(nome)}: Schengen countries ({A1}), easiest and hardest"
                 + ((", and " + altre[0]) if len(altre) == 1 else (", " + ", ".join(altre[:-1]) + " and " + altre[-1]) if altre else ""))
    nota_dest = ""
    if p in ("AUSTRALIA", "CANADA"):
        dd = "australia-visas" if p == "AUSTRALIA" else "canada-visas"
        nota_dest = (f'<p class="avviso"><strong>Applying for a visa to {escape(nome)}?</strong> This page is about Schengen visas applied for <em>in</em> {escape(nome)}. '
                     f'For {escape(nome)}\'s own visas see <a href="../{dd}/">{escape(nome)} visa refusal and approval rates by nationality</a>.</p>')
    tipi_uk = ""
    if con_uk:
        nomi_g = [NOMI_BREVI_UK[g] for g in uk_r]
        tipi_uk = nomi_g[0] if len(nomi_g) == 1 else ", ".join(nomi_g[:-1]) + " and " + nomi_g[-1]
    corpo = f"""<section class="hero">{h1_diviso(titolo_h1)}
<p class="lead">How many Schengen visa applications made in {escape(art(nome))} were not issued in {A1}, country by country and consulate by consulate, with the easiest and hardest countries for {escape(demonimo(p))}{', and how many UK ' + tipi_uk + ' visa applications by nationals of ' + escape(art(nome)) + ' were refused' if con_uk else ''}{(', with the latest figures for ' + ', '.join(dest[:-1]) + (' and ' if len(dest) > 1 else '') + dest[-1]) if dest else ''}. Official figures only.</p></section>
{nota_dest}
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("passport")}<span>Visa refusal rates</span><span>{escape(nome)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Schengen visas · applications made in {escape(art(nome))} · {A1}</span><span class="sr">: </span><strong>{pct(t1)}</strong> not issued ({intero(v1[3])} of {intero(decisioni(v1))} decisions)</p>
<div class="kpi"><div><b>{intero(v1[0])}</b><span>applications</span></div><div><b>{intero(v1[1])}</b><span>uniform visas issued</span></div><div><b>{intero(v1[3])}</b><span>not issued</span></div><div><b>{punti(t1, t0) if t0 is not None else '–'}</b><span>change on {A0}{f' ({pct(t0)})' if t0 is not None else ''}</span></div></div>
<p class="lead" style="margin-top:6px">{frase_basso} Of the {len(PAESI_RIF)} countries with the most applications, {escape(art(nome))} ranks {pos} (1 = lowest rate).</p>
{fonte_ue_p(A1, A0)}
{uk_kpi}
{kpi_altri(au_r, nz_r, ca_r)}
</div></section>
{AVVISO_RIF}
{AD}
<h2>Schengen visa rejection rate by country, applications made in {escape(art(nome))}</h2>
<p class="small">Tap a column heading to sort. "Not issued" includes refusals and applications whose examination was discontinued. * Fewer than {SOGLIA_POCO} decisions: the rate can swing a lot.</p>
{tab}
{fonte_ue_p(A1, A0)}
{clas}
<h2>By consulate</h2>
<p class="lead">Each Schengen country's consulates (or visa sections) in {escape(art(nome))}, by number of applications in {A1}. Where a country is represented by another, the applications appear under the country that decided them.</p>
{tab_c}
{fonte_ue_p(A1)}
{uk_html}
{au_html}
{nz_html}
{ca_html}
{box_assicurazione(rel)}
<h2>How to read these figures</h2>
<ul class="testo">
<li><strong>Where you apply, not your passport.</strong> The Schengen figures count applications made in {escape(art(nome))}, including residents of other nationalities, and leave out nationals of {escape(art(nome))} who applied elsewhere.</li>
<li><strong>Not-issued rate</strong> = visas not issued ÷ (uniform visas issued + visas with limited territorial validity + visas not issued), the formula in the Commission's file. Applications still pending at the end of the year are not counted.</li>
<li><strong>If you are refused</strong>, the consulate must tell you why and how to appeal (<a href="{URL_COMMISSIONE_DOMANDA}" rel="noopener">European Commission</a>).</li>
<li><strong>Australia, New Zealand and Canada</strong> count applicants by citizenship (Canada: "source country"), like the UK, and each authority defines its rate differently: see the notes under each table.</li>
<li>Full method: <a href="../#method">how we calculate the rates</a>.</li></ul>
<h2>Other countries where people apply</h2>
<div class="griglia">{griglia_altri}</div>
<p><a href="../">Schengen visa refusal rates by country, {A1}</a> · <a href="../uk/">UK visa refusal rates by nationality</a> · <a href="../australia-visas/">Australia</a> · <a href="../new-zealand-visas/">New Zealand</a> · <a href="../canada-visas/">Canada</a> · <a href="{rel}">Visa income calculator</a></p>
{link_tr_naz(p, rel)}"""
    plus = (["UK"] if con_uk else []) + (["Australia"] if au_r else [])
    coda = (", plus " + " and ".join(plus)) if plus else ""
    # titolo entro 75 caratteri dove possibile (revisione 26/10/2026): si tolgono prima "by country", poi "easiest and hardest", mai UK/Australia
    varianti = [f"Schengen visa rejection rate {nome} {A1}: by country, easiest and hardest{coda}",
                f"Schengen visa rejection rate {nome} {A1}: easiest and hardest{coda}",
                f"Schengen visa rejection rate {nome} {A1} by country{coda}",
                f"Schengen visa rejection rate {nome} {A1}{coda}"]
    titolo = next((v for v in varianti if len(v) <= 75), varianti[-1])
    descr = (f"Official {A1} figures: {pct(t1)} of Schengen visa applications made in {art(nome)} were not issued."
             + (f" Easiest Schengen visa for {demonimo(p)}: {basso[0][0]} ({pct(tasso(basso[0][1]))}); hardest: {alto[0][0]} ({pct(tasso(alto[0][1]))})." if basso and alto else "")
             + " Every Schengen country and consulate"
             + (f", and the UK refusal rate for nationals of {art(nome)} ({', '.join(f'{NOMI_BREVI_UK[g]} {pct(uk_r[g][0])}' for g in uk_r)})" if con_uk else "") + "."
             + (f" Australia student visas: {pct(au_r[0])} refused ({AU_A1})." if au_r else "")
             + (" New Zealand and Canada figures too." if nz_r and ca_r else " New Zealand figures too." if nz_r else " Canada figures too." if ca_r else ""))
    pagina(f"{SEZ}{slug}/", titolo, descr, corpo, ordina=True,
           briciole=[("Visa refusal rates", SEZ), (nome, f"{SEZ}{slug}/")])


# Pagine "Easiest Schengen visa from <Paese>" (21/10/2026): solo per i Paesi in cui almeno SOGLIA_FACILE Stati Schengen hanno deciso
# almeno SOGLIA_CLASSIFICA domande nell'anno più recente, così "5 più bassi" e "3 più alti" non si sovrappongono e la classifica ha senso.
SOGLIA_FACILE = 8
PAESI_FACILE = [p for p in PAESI_RIF if classifica(raggruppa(A1, 0, lambda r, p=p: r[1] == p))[1] >= SOGLIA_FACILE]


def pagina_rif_facile(p):
    rel = "../../../"
    nome = nome_paese(p)
    slug = SLUG_RIF[p]
    dem = demonimo(p)
    percorso = f"{SEZ}{slug}/easiest-schengen-visa/"
    s1 = raggruppa(A1, 0, lambda r: r[1] == p)
    s0 = raggruppa(A0, 0, lambda r: r[1] == p)
    v1 = PER_PAESE[A1][p]
    ok, n_ok = classifica(s1, n=len(s1))
    basso, alto = ok[:5], list(reversed(ok))[:3]
    scala = max([tasso(v) for _, v in basso + alto] + [0.01])
    esclusi = [s for s, v in s1.items() if decisioni(v) < SOGLIA_CLASSIFICA and (v[0] or decisioni(v))]
    righe = []
    for i, (s, v) in enumerate(ok, 1):
        righe.append(f'<tr><td class="n" data-v="{i}">{i}</td><td><a href="{rel}{SEZ}schengen/{SLUG_STATO[s]}/">{escape(s)}</a></td>'
                     f'{cella_tasso(tasso(v))}{cella_tasso(tasso(s0[s]) if s in s0 else None)}'
                     f'<td class="n" data-v="{tasso(v) - tasso(s0[s]) if s in s0 and tasso(s0[s]) is not None else ""}">{punti(tasso(v), tasso(s0[s])) if s in s0 else "–"}</td>'
                     f'<td class="n" data-v="{decisioni(v)}">{intero(decisioni(v))}</td><td class="n" data-v="{v[3]}">{intero(v[3])}</td></tr>')
    tab = ('<div class="tab compatta"><table class="ord"><thead><tr>' + th_ord("#", primo="ascending") + th_ord("Schengen country", False, "ascending") +
           th_ord(f"Not issued {A1}", primo="ascending") + th_ord(f"{A0}", primo="ascending") + th_ord("Change", primo="ascending") + th_ord("Decisions") + th_ord("Not issued") +
           f'</tr></thead><tbody>{"".join(righe)}</tbody></table></div>')
    # consolati con almeno SOGLIA_CLASSIFICA decisioni, dal tasso più basso
    cons = []
    for r in UE[A1]:
        if r[1] == p:
            v = [r[3], r[4], r[5], r[6]]
            if decisioni(v) >= SOGLIA_CLASSIFICA:
                cons.append((r[0], r[2], v))
    cons.sort(key=lambda x: tasso(x[2]))
    righe_c = "".join(f'<tr><td class="n" data-v="{i}">{i}</td><td><a href="{rel}{SEZ}schengen/{SLUG_STATO[s]}/">{escape(s)}</a></td><td>{escape(nome_consolato(c))}</td>'
                      f'{cella_tasso(tasso(v))}<td class="n" data-v="{decisioni(v)}">{intero(decisioni(v))}</td><td class="n" data-v="{v[3]}">{intero(v[3])}</td></tr>'
                      for i, (s, c, v) in enumerate(cons, 1))
    tab_c = ('<div class="tab compatta"><table class="ord"><thead><tr>' + th_ord("#", primo="ascending") + th_ord("Country", False, "ascending") + th_ord("Consulate", False, "ascending") +
             th_ord("Rate", primo="ascending") + th_ord("Decisions") + th_ord("Not issued") + f'</tr></thead><tbody>{righe_c}</tbody></table></div>')
    sb, vb = basso[0]
    sa, va = alto[0]
    altri = [x for x in sorted(PAESI_FACILE, key=lambda x: abs(PER_PAESE[A1][x][0] - v1[0])) if x != p][:8]
    griglia_altri = "".join(f'<a href="../../{SLUG_RIF[x]}/easiest-schengen-visa/"><span class="ic">{ico("passport")}</span><span>Easiest Schengen visa from {escape(art(nome_paese(x)))}'
                            f'<small>lowest rate: {escape(classifica(raggruppa(A1, 0, lambda r, x=x: r[1] == x))[0][0][0])}</small></span></a>' for x in altri)
    domande = [
        (f"Which Schengen country has the lowest rejection rate for {dem}?",
         f"In {A1}, {sb} had the lowest not-issued rate ({pct(tasso(vb))}) among the {n_ok} Schengen countries that decided at least {intero(SOGLIA_CLASSIFICA)} applications made in {art(nome)}. "
         f"The next lowest were {', '.join(f'{s} ({pct(tasso(v))})' for s, v in basso[1:4])}."),
        (f"Which Schengen country rejects the most applications from {art(nome)}?",
         f"{sa}, with {pct(tasso(va))} of {intero(decisioni(va))} decisions not issued in {A1}"
         + (f", followed by {', '.join(f'{s} ({pct(tasso(v))})' for s, v in alto[1:3])}" if len(alto) > 1 else "") + "."),
        (f"Which Schengen visa is easiest to get from {art(nome)}?",
         f"There is no 'easy' Schengen visa: every country applies the same Visa Code, and you must apply to the country of your main destination. "
         f"The figures show that in {A1} consulates of {sb} in {art(nome)} issued visas to a larger share of applicants than consulates of {sa}, "
         f"but each rate mixes different travellers, purposes and documents. Rates describe past decisions, not your chances."),
        ("Can I apply to the country with the lowest refusal rate?",
         "Only if it is your main destination (where you will spend the most time) or, for equal stays, the first Schengen country you enter. "
         "Applying to a country you do not plan to visit mainly can itself lead to a refusal."),
    ]
    faq_html = "".join(f'<h3>{escape(q)}</h3><p>{escape(a)}</p>' for q, a in domande)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in domande]}
    corpo = f"""<section class="hero">{h1_diviso(f"Easiest Schengen visa from {art(nome)} ({A1}): countries with the lowest refusal rate")}
<p class="lead">Which Schengen country has the lowest rejection rate for {escape(dem)}? Official {A1} figures from the European Commission for every Schengen country and consulate that decided at least {intero(SOGLIA_CLASSIFICA)} applications made in {escape(art(nome))}, ranked from the lowest not-issued rate to the highest. Rates describe past decisions, not your chances.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("passport")}<span>Easiest Schengen visa</span><span>{escape(nome)} · {A1}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Lowest not-issued rate · applications made in {escape(art(nome))} · {A1}</span><span class="sr">: </span><strong>{escape(sb)}: {pct(tasso(vb))}</strong> not issued ({intero(vb[3])} of {intero(decisioni(vb))} decisions)</p>
<div class="kpi"><div><b>{escape(sa)}</b><span>highest rate: {pct(tasso(va))}</span></div><div><b>{pct(tasso(v1))}</b><span>all Schengen countries, applications made in {escape(art(nome))}</span></div><div><b>{n_ok}</b><span>countries with {intero(SOGLIA_CLASSIFICA)}+ decisions</span></div><div><b>{len(cons)}</b><span>consulates with {intero(SOGLIA_CLASSIFICA)}+ decisions</span></div></div>
<p class="lead" style="margin-top:6px">Rates are by the country where the application was made, not by passport: these are all applications lodged in {escape(art(nome))}. Full figures, consulate by consulate and the UK: <a href="../">Schengen visa rejection rate {escape(nome)} {A1}</a>.</p>
{fonte_ue_p(A1)}
</div></section>
{AVVISO_RIF}
{AD}
<h2>Lowest and highest refusal rates for {escape(dem)} ({A1})</h2>
<p class="lead">The {min(5, n_ok)} Schengen countries with the lowest not-issued rate and the {min(3, n_ok)} with the highest, among the {n_ok} that decided at least {intero(SOGLIA_CLASSIFICA)} applications made in {escape(art(nome))}.</p>
<div class="due"><div><h3>Lowest refusal rates</h3>{lista_classifica(basso, rel, "basso", scala)}</div><div><h3>Highest refusal rates</h3>{lista_classifica(alto, rel, "alto", scala)}</div></div>
<p class="avviso"><strong>A lower rate is not a guarantee, and you cannot choose freely.</strong> You must apply to the country of your main destination (or, for equal stays, the first you enter), at the consulate responsible for where you legally live: the rule is on the <a href="{URL_COMMISSIONE_DOMANDA}" rel="noopener">European Commission page on applying for a Schengen visa</a> (checked on {data_lunga(DATA_COMMISSIONE_DOMANDA)}). Rates describe past decisions, not your chances.</p>
{fonte_ue_p(A1)}
<h2>All Schengen countries ranked, applications made in {escape(art(nome))} ({A1})</h2>
<p class="small">Countries with at least {intero(SOGLIA_CLASSIFICA)} decisions, from the lowest not-issued rate. Tap a column heading to sort. "Change" is in percentage points on {A0}.{f' Not ranked (fewer than {intero(SOGLIA_CLASSIFICA)} decisions): {escape(", ".join(sorted(esclusi)))}; their figures are on the <a href="../">main {escape(nome)} page</a>.' if esclusi else ''}</p>
{tab}
{fonte_ue_p(A1, A0)}
<h2>Consulates in {escape(art(nome))} with the lowest refusal rates</h2>
<p class="lead">Each consulate or visa section that decided at least {intero(SOGLIA_CLASSIFICA)} applications in {A1}, from the lowest rate. Where a Schengen country is represented by another, the applications appear under the country that decided them.</p>
{tab_c}
{fonte_ue_p(A1)}
<h2>Questions people ask</h2>
<div class="testo">{faq_html}</div>
{box_assicurazione(rel)}
<h2>What "easiest" means here</h2>
<ul class="testo">
<li><strong>Where you apply, not your passport.</strong> The Commission counts applications by the country where they were lodged: the figures for {escape(art(nome))} include residents of other nationalities, and leave out nationals of {escape(art(nome))} who applied elsewhere.</li>
<li><strong>Not issued</strong> = refused plus applications whose examination was discontinued, ÷ (uniform visas issued + visas with limited territorial validity + not issued): the formula in the Commission's file.</li>
<li><strong>Minimum {intero(SOGLIA_CLASSIFICA)} decisions.</strong> A consulate that decided 40 applications can swing from 5% to 30% in a year without anything changing; we rank only countries and consulates with enough decisions.</li>
<li><strong>If you are refused</strong>, the consulate must tell you why and how to appeal (<a href="{URL_COMMISSIONE_DOMANDA}" rel="noopener">European Commission</a>). Full method: <a href="../../#method">how we calculate the rates</a>.</li></ul>
<h2>Easiest Schengen visa from other countries</h2>
<div class="griglia">{griglia_altri}</div>
<p><a href="../">Schengen visa rejection rate {escape(nome)} {A1}: every country, consulate and the UK</a> · <a href="../../">Visa refusal rates by country</a> · <a href="{rel}">Visa income calculator</a></p>"""
    titolo = f"Easiest Schengen visa from {art(nome)} {A1}: lowest refusal rate by country (official)"
    descr = (f"Easiest Schengen visa for {dem}: in {A1} {sb} had the lowest not-issued rate ({pct(tasso(vb))}) and {sa} the highest ({pct(tasso(va))}) "
             f"among {n_ok} Schengen countries with {intero(SOGLIA_CLASSIFICA)}+ decisions in {art(nome)}. Official ranking by country and consulate.")
    pagina(percorso, titolo, descr, corpo, ordina=True, jsonld_extra=ld,
           briciole=[("Visa refusal rates", SEZ), (nome, f"{SEZ}{slug}/"), ("Easiest Schengen visa", percorso)])


def pagina_rif_stato(s):
    rel = "../../../"
    v1, v0 = PER_STATO[A1][s], PER_STATO[A0].get(s)
    t1, t0 = tasso(v1), (tasso(v0) if v0 else None)
    p1 = raggruppa(A1, 1, lambda r: r[0] == s)
    p0 = raggruppa(A0, 1, lambda r: r[0] == s)
    rank = sorted(STATI_UE, key=lambda x: tasso(PER_STATO[A1][x]))
    pos = rank.index(s) + 1
    righe = []
    for p, v in sorted(p1.items(), key=lambda x: -x[1][0]):
        if v[0] == 0 and decisioni(v) == 0:
            continue
        poco = decisioni(v) < SOGLIA_POCO
        nome = (f'<a href="{rel}{SEZ}{SLUG_RIF[p]}/">{escape(nome_paese(p))}</a>' if p in SLUG_RIF else escape(nome_paese(p)))
        righe.append(f'<tr{" class=\"poco\"" if poco else ""}><td>{nome}</td>{cella_tasso(tasso(v), poco)}{cella_tasso(tasso(p0[p]) if p in p0 else None)}'
                     f'<td class="n" data-v="{v[0]}">{intero(v[0])}</td><td class="n" data-v="{v[3]}">{intero(v[3])}</td></tr>')
    cons = sorted((r for r in UE[A1] if r[0] == s and r[3] > 0), key=lambda r: -r[3])[:30]
    righe_c = "".join(f'<tr><td>{escape(nome_consolato(r[2]))}</td><td>{escape(nome_paese(r[1]))}</td>'
                      f'{cella_tasso(tasso([r[3], r[4], r[5], r[6]]), decisioni([r[3], r[4], r[5], r[6]]) < SOGLIA_POCO)}<td class="n" data-v="{r[3]}">{intero(r[3])}</td></tr>' for r in cons)
    alto = [(p, v) for p, v in p1.items() if decisioni(v) >= SOGLIA_CLASSIFICA]
    alto.sort(key=lambda x: -tasso(x[1]))
    frase_alto = (f'Highest rate among places with at least {intero(SOGLIA_CLASSIFICA)} decisions: {escape(nome_paese(alto[0][0]))} ({pct(tasso(alto[0][1]))}); '
                  f'lowest: {escape(nome_paese(alto[-1][0]))} ({pct(tasso(alto[-1][1]))}).') if len(alto) >= 2 else ""
    fl = bandiera(s)
    corpo = f"""<section class="hero">{h1_diviso(f"{s} Schengen visa rejection rate {A1}: by country where you apply")}
<p class="lead">Short-stay visa applications decided by {escape(s)}'s consulates in {A1}: how many were not issued, in each country where people applied. Official figures from the European Commission.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{fl if '<svg class="flag"' in fl else ico("globe")}<span>Schengen visa statistics</span><span>{escape(s)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">{escape(s)} · all consulates · {A1}</span><span class="sr">: </span><strong>{pct(t1)}</strong> of decisions were visas not issued</p>
<div class="kpi"><div><b>{intero(v1[0])}</b><span>applications</span></div><div><b>{intero(v1[1])}</b><span>uniform visas issued</span></div><div><b>{intero(v1[3])}</b><span>not issued</span></div><div><b>{pos} of {len(STATI_UE)}</b><span>rank (1 = lowest rate)</span></div></div>
<p class="lead" style="margin-top:6px">{f'In {A0}: {pct(t0)} ({punti(t1, t0)}).' if t0 is not None else ''} {frase_alto} Average for all Schengen countries in {A1}: {pct(tasso(TOT_UE[A1]))}.</p>
{fonte_ue_p(A1, A0)}
</div></section>
{AVVISO_RIF}
{AD}
<h2>{escape(s)} visa rejection rate by country where people apply</h2>
<p class="small">Every country where {escape(s)} decided applications in {A1}. Tap a column heading to sort, or type to filter. * Fewer than {SOGLIA_POCO} decisions.</p>
<p class="filtro"><label><span class="sr">Filter countries</span><input type="search" placeholder="Filter: e.g. India" data-filtro="t-paesi" autocomplete="off"></label></p>
<div class="tab compatta"><table class="ord" id="t-paesi"><thead><tr>{th_ord("Applied in", False, "ascending")}{th_ord(f"Rate {A1}", primo="ascending")}{th_ord(f"{A0}", primo="ascending")}{th_ord("Applications")}{th_ord("Not issued")}</tr></thead><tbody>{"".join(righe)}</tbody></table></div>
{fonte_ue_p(A1, A0)}
<h2>{escape(s)}'s busiest consulates</h2>
<div class="tab compatta"><table class="ord"><thead><tr>{th_ord("Consulate", False, "ascending")}{th_ord("Country", False, "ascending")}{th_ord("Rate", primo="ascending")}{th_ord("Applications")}</tr></thead><tbody>{righe_c}</tbody></table></div>
{fonte_ue_p(A1)}
{box_assicurazione(rel)}
<h2>Other Schengen countries</h2>
<div class="griglia">{''.join(scheda_stato(x, "../") for x in STATI_UE if x != s)}</div>
<p><a href="../../">All Schengen countries compared</a> · <a href="../../#method">How we calculate the rates</a> · <a href="{rel}">Visa income calculator</a></p>"""
    titolo = f"{s} visa rejection rate {A1} by country (Schengen, official figures)"
    descr = (f"{s} Schengen visa rejection rate {A1}: {pct(t1)} of {intero(decisioni(v1))} decisions were not issued. "
             f"Rates by country where people apply and by consulate, from the European Commission.")
    pagina(f"{SEZ}schengen/{SLUG_STATO[s]}/", titolo, descr, corpo, ordina=True,
           briciole=[("Visa refusal rates", SEZ), (f"{s} visa rejection rate", f"{SEZ}schengen/{SLUG_STATO[s]}/")])


def scheda_stato(s, pre):
    fl = bandiera(s)
    icona = f'<span class="ic f">{fl}</span>' if '<svg class="flag"' in fl else f'<span class="ic">{ico("globe")}</span>'
    return (f'<a href="{pre}{SLUG_STATO[s]}/">{icona}<span>{escape(s)}<small>{pct(tasso(PER_STATO[A1][s]))} not issued in {A1}</small></span></a>')


def righe_uk_tutte(rel):
    out = []
    for n in sorted(UKN):
        if n in ("Other and unknown", "Refugee", "Stateless", "British overseas citizens"):
            continue
        vis1, vis0 = uk_somma(n, ["Visitor"], T1), uk_somma(n, ["Visitor"], T0)
        tut1 = uk_somma(n, GRUPPI_UK, T1)
        dv = vis1[0] + vis1[1]
        dt = tut1[0] + tut1[1]
        if dt < SOGLIA_POCO:
            continue
        ec = _NOMI_UK_INV.get(n, n.upper())
        link = f'<a href="{rel}{SEZ}{SLUG_RIF[ec]}/#uk">{escape(n)}</a>' if ec in SLUG_RIF and ha_uk(ec) else escape(n)
        celle_sw = ""
        for g in ("Study", "Work"):
            vg = uk_somma(n, [g], T1)
            dg = vg[0] + vg[1]
            celle_sw += f'{cella_tasso(uk_tasso(vg), dg < SOGLIA_POCO) if dg else cella_tasso(None)}<td class="n" data-v="{dg}">{intero(dg)}</td>'
        out.append((dv, f'<tr><td>{link}</td>{cella_tasso(uk_tasso(vis1), dv < SOGLIA_POCO) if dv else cella_tasso(None)}'
                        f'{cella_tasso(uk_tasso(vis0)) if vis0[0] + vis0[1] else cella_tasso(None)}<td class="n" data-v="{dv}">{intero(dv)}</td>'
                        f'{celle_sw}{cella_tasso(uk_tasso(tut1))}<td class="n" data-v="{dt}">{intero(dt)}</td></tr>'))
    out.sort(key=lambda x: -x[0])
    return [r for _, r in out]


def uk_totale(gruppi, trimestri):
    """Somma di tutte le nazionalità (concessi, rifiutati, ritirati, decaduti)."""
    v = [0, 0, 0, 0]
    for n in UKN:
        for i, x in enumerate(uk_somma(n, gruppi, trimestri)):
            v[i] += x
    return v


ESCLUSE_UK = ("Other and unknown", "Refugee", "Stateless", "British overseas citizens")


def righe_famiglia_uk(rel, quante=None):
    """Righe della tabella dei visti di famiglia e del partner per nazionalità (almeno SOGLIA_POCO decisioni sulla famiglia),
    dalla nazionalità con più decisioni. Restituisce (righe, voci) con voci = [(nazionalità, famiglia, partner)]."""
    voci = []
    for n in UKN:
        if n in ESCLUSE_UK:
            continue
        f1 = uk_somma(n, ["Family"], T1)
        if f1[0] + f1[1] >= SOGLIA_POCO:
            voci.append((n, f1, uk_somma(n, [PARTNER_UK], T1), uk_somma(n, ["Family"], T0)))
    voci.sort(key=lambda x: -(x[1][0] + x[1][1]))
    if quante:
        voci = voci[:quante]
    righe = []
    for n, f1, p1, f0 in voci:
        ec = _NOMI_UK_INV.get(n, n.upper())
        link = f'<a href="{rel}{SEZ}{SLUG_RIF[ec]}/#uk">{escape(n)}</a>' if ec in SLUG_RIF and ha_uk(ec) else escape(n)
        df, dp, d0 = f1[0] + f1[1], p1[0] + p1[1], f0[0] + f0[1]
        righe.append(f'<tr><td>{link}</td>{cella_tasso(uk_tasso(f1), df < SOGLIA_UK)}'
                     + ('' if quante else (cella_tasso(uk_tasso(f0)) if d0 >= SOGLIA_POCO else cella_tasso(None)))
                     + f'<td class="n" data-v="{df}">{intero(df)}</td>'
                     f'{cella_tasso(uk_tasso(p1), dp < SOGLIA_UK) if dp >= SOGLIA_POCO else cella_tasso(None)}<td class="n" data-v="{dp}">{intero(dp)}</td></tr>')
    return righe, voci


def pagina_rif_uk_famiglia():
    """UK family and spouse visa refusal rate by nationality (28/10/2026): gruppo Family e tipo Family: Partner del file D02."""
    rel = "../../../"
    percorso = f"{SEZ}uk/family-visas/"
    fam1, fam0 = uk_totale(["Family"], T1), uk_totale(["Family"], T0)
    par1, par0 = uk_totale([PARTNER_UK], T1), uk_totale([PARTNER_UK], T0)
    righe, voci = righe_famiglia_uk(rel)
    grandi = [(n, f) for n, f, _p, _f0 in voci if f[0] + f[1] >= SOGLIA_UK]
    alti = sorted(grandi, key=lambda x: -uk_tasso(x[1]))[:5]
    bassi = sorted(grandi, key=lambda x: uk_tasso(x[1]))[:5]
    righe_q = []
    for q in TRIM:
        f, pq = uk_totale(["Family"], [q]), uk_totale([PARTNER_UK], [q])
        righe_q.append(f'<tr><td>{trimestre_testo(q)}</td>{cella_tasso(uk_tasso(f))}<td class="n" data-v="{f[0] + f[1]}">{intero(f[0] + f[1])}</td>'
                       f'{cella_tasso(uk_tasso(pq))}<td class="n" data-v="{pq[0] + pq[1]}">{intero(pq[0] + pq[1])}</td></tr>')
    elenco = lambda xs: ", ".join(f"{n} ({pct(uk_tasso(f))})" for n, f in xs)  # noqa: E731
    domande = [
        ("What is the UK spouse visa refusal rate?",
         f"From {periodo_uk(T1)} the Home Office refused {pct(uk_tasso(par1))} of decisions on partner visas, the route for spouses, civil partners and "
         f"unmarried partners ({intero(par1[1])} refused, {intero(par1[0])} granted). In the year before it was {pct(uk_tasso(par0))}."),
        ("What is the UK family visa refusal rate?",
         f"{pct(uk_tasso(fam1))} of all family visa decisions were refusals from {periodo_uk(T1)} ({intero(fam1[1])} of {intero(fam1[0] + fam1[1])}). "
         f"The family group also includes children, other relatives and refugee family reunion: without partner visas, "
         f"{pct(uk_tasso([fam1[0] - par1[0], fam1[1] - par1[1]]))} of those decisions were refusals."),
        ("Which nationalities have the highest UK family visa refusal rates?",
         f"Among nationalities with at least {intero(SOGLIA_UK)} family visa decisions from {periodo_uk(T1)}: {elenco(alti)}. The lowest: {elenco(bassi)}."),
        ("Does a low refusal rate mean a spouse visa will be approved?",
         "No. Each application is decided on its own evidence: the financial requirement, the relationship, accommodation and English language. "
         "These rates describe past decisions for all applicants of a nationality, not anyone's chances."),
    ]
    faq_html = "".join(f'<h3>{escape(q)}</h3><p>{escape(a)}</p>' for q, a in domande)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in domande]}
    corpo = f"""<section class="hero">{h1_diviso(f"UK family and spouse visa refusal rate by nationality: {periodo_uk(T1)}")}
<p class="lead">From {periodo_uk(T1)} the Home Office refused <strong>{pct(uk_tasso(par1))}</strong> of UK partner (spouse) visa decisions ({intero(par1[1])} of {intero(par1[0] + par1[1])}) and {pct(uk_tasso(fam1))} of all family visa decisions ({intero(fam1[1])} of {intero(fam1[0] + fam1[1])}), according to its official immigration statistics published on {escape(F_UK["pubblicato"])}. Below, nationality by nationality. The partner figure is shown on its own because the family group also includes children, other relatives and refugee family reunion.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{bandiera("United Kingdom")}<span>UK family visas</span><span>{periodo_uk(T1)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Partner (spouse) visas · all nationalities</span><span class="sr">: </span><strong>{pct(uk_tasso(par1))}</strong> refused ({intero(par1[1])} of {intero(par1[0] + par1[1])} decisions)</p>
<div class="kpi"><div><b>{pct(uk_tasso(fam1))}</b><span>all family visas refused · {intero(fam1[0] + fam1[1])} decisions</span></div><div><b>{pct(uk_tasso(par0))}</b><span>partner visas refused, {periodo_breve(T0)}</span></div><div><b>{pct(uk_tasso(fam0))}</b><span>family visas refused, {periodo_breve(T0)}</span></div><div><b>{len(grandi)}</b><span>nationalities with {intero(SOGLIA_UK)}+ family decisions</span></div></div>
<p class="lead" style="margin-top:6px">Highest family visa refusal rates among nationalities with at least {intero(SOGLIA_UK)} decisions: {escape(elenco(alti[:3]))}. Lowest: {escape(elenco(bassi[:3]))}.</p>
{fonte_uk_p()}
</div></section>
{AVVISO_RIF.replace("you must apply to the Schengen country where you will spend the most time (or, for equal stays, the one you enter first), at the consulate responsible for the place where you legally live", "each application is assessed on its own documents")}
{AD}
<h2>UK family and partner visa refusal rate by nationality</h2>
<p class="small">Nationalities with at least {SOGLIA_POCO} family visa decisions from {periodo_uk(T1)}, by number of decisions. Tap a column heading to sort, or type to filter. "Year before" = {periodo_uk(T0)}. * Fewer than {intero(SOGLIA_UK)} decisions: the rate can swing a lot. – Fewer than {SOGLIA_POCO} decisions.</p>
<p class="filtro"><label><span class="sr">Filter nationalities</span><input type="search" placeholder="Filter: e.g. Pakistan" data-filtro="t-fam" autocomplete="off"></label></p>
<div class="tab compatta"><table class="ord" id="t-fam"><thead><tr>{th_ord("Nationality", False, "ascending")}{th_ord("Family visas refused", primo="ascending")}{th_ord("Year before", primo="ascending")}{th_ord("Family decisions")}{th_ord("Partner visas refused", primo="ascending")}{th_ord("Partner decisions")}</tr></thead><tbody>{"".join(righe)}</tbody></table></div>
{fonte_uk_p()}
<p class="small">{DEF_FAMIGLIA_UK}</p>
<h2>Quarter by quarter, all nationalities</h2>
<div class="tab compatta"><table><thead><tr><th scope="col">Quarter</th><th class="n" scope="col">Family visas refused</th><th class="n" scope="col">Family decisions</th><th class="n" scope="col">Partner visas refused</th><th class="n" scope="col">Partner decisions</th></tr></thead><tbody>{"".join(righe_q)}</tbody></table></div>
{fonte_uk_p()}
<h2>Questions people ask</h2>
<div class="testo">{faq_html}</div>
<h2>How to read these figures</h2>
<ul class="testo"><li>The Home Office counts applicants by <strong>nationality</strong>, wherever they applied, and an outcome in a quarter can relate to an application made earlier.</li>
<li>The refusal rate is refused ÷ (granted + refused): withdrawn and lapsed applications are left out, as in the Home Office "grant rate".</li>
<li>These are entry clearance visas, applied for outside the UK. Partners who switch to a family visa from inside the UK are not counted here.</li>
<li>The income needed for a partner visa is on our <a href="{rel}uk-spouse-visa/">UK spouse visa income requirement</a> page.</li></ul>
<p><a href="../">UK visa refusal rates by nationality (all visa types)</a> · <a href="../../">Schengen visa refusal rates</a> · <a href="{rel}uk-spouse-visa/">UK spouse visa income requirement</a></p>"""
    titolo = f"UK spouse and family visa refusal rate by nationality {TRIM[-1].split()[0]}"
    descr = (f"Home Office data from {periodo_uk(T1)}: {pct(uk_tasso(par1))} of UK partner (spouse) visa decisions and {pct(uk_tasso(fam1))} of all family visa "
             f"decisions were refusals. Rates for {len(voci)} nationalities, quarter by quarter.")
    pagina(percorso, titolo, descr, corpo, ordina=True, jsonld_extra=ld,
           briciole=[("Visa refusal rates", SEZ), ("UK refusal rates by nationality", f"{SEZ}uk/"), ("Family and spouse visas", percorso)])


def pagina_rif_uk():
    rel = "../../"
    righe = righe_uk_tutte(rel)
    tot1 = [0, 0, 0, 0]
    vis = [0, 0, 0, 0]
    stu = [0, 0, 0, 0]
    lav = [0, 0, 0, 0]
    for n in UKN:
        for i, x in enumerate(uk_somma(n, GRUPPI_UK, T1)):
            tot1[i] += x
        for i, x in enumerate(uk_somma(n, ["Visitor"], T1)):
            vis[i] += x
        for i, x in enumerate(uk_somma(n, ["Study"], T1)):
            stu[i] += x
        for i, x in enumerate(uk_somma(n, ["Work"], T1)):
            lav[i] += x
    fam, par = uk_totale(["Family"], T1), uk_totale([PARTNER_UK], T1)
    corpo = f"""<section class="hero">{h1_diviso(f"UK visa refusal rate by nationality: visitor, student, work and family visas, {periodo_uk(T1)}")}
<p class="lead">How many UK visa applications were refused, nationality by nationality, from the Home Office's official immigration statistics: visitor visas, student (study) visas and work visas side by side. Updated every quarter.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{bandiera("United Kingdom")}<span>UK entry clearance visas</span><span>{periodo_uk(T1)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Visitor visas · all nationalities</span><span class="sr">: </span><strong>{pct(uk_tasso(vis))}</strong> refused ({intero(vis[1])} of {intero(vis[0] + vis[1])} decisions)</p>
<div class="kpi"><div><b>{pct(uk_tasso(stu))}</b><span>study visas refused · {intero(stu[0] + stu[1])} decisions</span></div><div><b>{pct(uk_tasso(lav))}</b><span>work visas refused · {intero(lav[0] + lav[1])} decisions</span></div><div><b>{pct(uk_tasso(fam))}</b><span>family visas refused · {intero(fam[0] + fam[1])} decisions</span></div><div><b>{pct(uk_tasso(par))}</b><span>partner (spouse) visas refused · {intero(par[0] + par[1])} decisions</span></div><div><b>{pct(uk_tasso(tot1))}</b><span>all entry clearance visas refused</span></div><div><b>{intero(tot1[0] + tot1[1])}</b><span>decisions on all visas</span></div></div>
{fonte_uk_p()}
</div></section>
{AVVISO_RIF.replace("you must apply to the Schengen country where you will spend the most time (or, for equal stays, the one you enter first), at the consulate responsible for the place where you legally live", "each application is assessed on its own documents")}
{AD}
<h2>Refusal rate by nationality</h2>
<p class="small">Nationalities with at least {SOGLIA_POCO} decisions on all visa types. "Visitor" = Standard Visitor visas (tourism, family visits, business); "Study" = Student, Child Student and short-term study visas; "Work" = all work routes (Skilled Worker, Health and Care Worker, temporary work and others). Tap a column heading to sort, or type to filter. * Fewer than {SOGLIA_POCO} decisions of that type.</p>
<p class="filtro"><label><span class="sr">Filter nationalities</span><input type="search" placeholder="Filter: e.g. Nigeria" data-filtro="t-uk" autocomplete="off"></label></p>
<div class="tab compatta"><table class="ord" id="t-uk"><thead><tr>{th_ord("Nationality", False, "ascending")}{th_ord("Visitor visas refused", primo="ascending")}{th_ord("Year before", primo="ascending")}{th_ord("Visitor decisions")}{th_ord("Study visas refused", primo="ascending")}{th_ord("Study decisions")}{th_ord("Work visas refused", primo="ascending")}{th_ord("Work decisions")}{th_ord("All visas refused", primo="ascending")}{th_ord("All visas: decisions")}</tr></thead><tbody>{"".join(righe)}</tbody></table></div>
{fonte_uk_p()}
<h2 id="family">Family and partner (spouse) visas</h2>
<p class="lead">From {periodo_uk(T1)} the UK refused <strong>{pct(uk_tasso(fam))}</strong> of family visa decisions ({intero(fam[1])} of {intero(fam[0] + fam[1])}) and <strong>{pct(uk_tasso(par))}</strong> of partner (spouse) visa decisions ({intero(par[1])} of {intero(par[0] + par[1])}). The family group also includes children, other relatives and refugee family reunion, which is why its rate is higher than the partner rate. <a href="family-visas/">UK family and spouse visa refusal rates for every nationality</a>.</p>
<div class="tab compatta"><table><thead><tr><th scope="col">Nationality</th><th class="n" scope="col">Family visas refused</th><th class="n" scope="col">Family decisions</th><th class="n" scope="col">Partner visas refused</th><th class="n" scope="col">Partner decisions</th></tr></thead><tbody>{"".join(righe_famiglia_uk(rel, 10)[0])}</tbody></table></div>
{fonte_uk_p()}
<p class="small">The 10 nationalities with the most family visa decisions. {DEF_FAMIGLIA_UK} * Fewer than {intero(SOGLIA_UK)} decisions.</p>
<p class="small">"Year before" = {periodo_uk(T0)} (visitor visas). Nationals of many countries (for example the EU, the US, Canada and Australia) do not need a visa for short visits and travel with an electronic travel authorisation instead, so they appear with few or no visitor decisions but often with thousands of study and work decisions.</p>
<h2>How to read these figures</h2>
<ul class="testo"><li>The Home Office counts applicants by <strong>nationality</strong>, wherever they applied. An outcome in a quarter can relate to an application made in an earlier quarter.</li>
<li>The refusal rate is the share of decisions (grants and refusals) that were refusals: withdrawn and lapsed applications are left out, as in the Home Office "grant rate".</li>
<li>Figures from 2026 Q1 onwards are provisional and can be revised in the next release ({escape(F_UK["prossimo"])}).</li></ul>
<h2>Other destinations</h2>
{schede_destinazioni("../")}
<p><a href="../">Schengen visa refusal rates</a> · <a href="{rel}uk-skilled-worker-visa/">UK Skilled Worker salary threshold</a> · <a href="{rel}uk-spouse-visa/">UK spouse visa income requirement</a></p>"""
    pagina(f"{SEZ}uk/", f"UK visa refusal rate by nationality {TRIM[-1].split()[0]}: visitor, study, work, family",
           f"UK visa refusal rates by nationality from {periodo_uk(T1)}: visitor visas {pct(uk_tasso(vis))} refused overall; India, Nigeria, Pakistan, Bangladesh, Ghana and more. Home Office data.",
           corpo, ordina=True, briciole=[("Visa refusal rates", SEZ), ("UK refusal rates by nationality", f"{SEZ}uk/")])


def pagina_rif_panoramica():
    rel = "../"
    t1, t0 = tasso(TOT_UE[A1]), tasso(TOT_UE[A0])
    righe_s = []
    for s in sorted(STATI_UE, key=lambda x: -PER_STATO[A1][x][0]):
        v = PER_STATO[A1][s]
        v0 = PER_STATO[A0].get(s)
        righe_s.append(f'<tr><td><a href="schengen/{SLUG_STATO[s]}/">{escape(s)}</a></td>{cella_tasso(tasso(v))}{cella_tasso(tasso(v0) if v0 else None)}'
                       f'<td class="n" data-v="{v[0]}">{intero(v[0])}</td><td class="n" data-v="{v[1]}">{intero(v[1])}</td><td class="n" data-v="{v[3]}">{intero(v[3])}</td></tr>')
    righe_p = []
    for p in PAESI_RIF:
        v = PER_PAESE[A1][p]
        v0 = PER_PAESE[A0].get(p)
        righe_p.append(f'<tr><td><a href="{SLUG_RIF[p]}/">{escape(nome_paese(p))}</a></td>{cella_tasso(tasso(v))}{cella_tasso(tasso(v0) if v0 else None)}'
                       f'<td class="n" data-v="{v[0]}">{intero(v[0])}</td><td class="n" data-v="{v[3]}">{intero(v[3])}</td></tr>')
    opzioni = "".join(f'<option value="{SLUG_RIF[p]}/">{escape(nome_paese(p))}</option>' for p in sorted(PAESI_RIF, key=nome_paese))
    uk_top = []
    for n in sorted(UKN, key=lambda n: -sum(uk_somma(n, ["Visitor"], T1)[:2]))[:12]:
        v = uk_somma(n, ["Visitor"], T1)
        ec = _NOMI_UK_INV.get(n, n.upper())
        link = f'<a href="{SLUG_RIF[ec]}/#uk">{escape(n)}</a>' if ec in SLUG_RIF and ha_uk(ec) else escape(n)
        uk_top.append(f'<tr><td>{link}</td>{cella_tasso(uk_tasso(v))}<td class="n">{intero(v[0] + v[1])}</td><td class="n">{intero(v[1])}</td></tr>')
    basso = sorted(STATI_UE, key=lambda x: tasso(PER_STATO[A1][x]))
    testata = f"""<div class="band"><div class="wrap band-in">{DECO_STAT}
<section class="hero">{h1_diviso(f"Visa refusal rates {A1}: Schengen visa rejection rate by country, and UK refusal rates")}
<p class="sub">Official figures from the European Commission and the UK Home Office: how many visa applications were not issued, by destination, by the country where people applied and by nationality. Also: <a href="australia-visas/">Australia</a>, <a href="new-zealand-visas/">New Zealand</a> and <a href="canada-visas/">Canada</a> by nationality.</p>
<p class="trust"><span>{ico("shield")}Official files · downloaded {data_lunga(F_UE[A1]["scaricato_il"])}</span><span>{ico("calendar")}Schengen {A1} · UK to {trimestre_testo(TRIM[-1])}</span></p></section>
<section class="card cerca"><form class="vai" action="#" onsubmit="return false"><label for="vai-paese"><span class="lt">{ico("globe")}Where do you apply from?</span></label>
<div class="vai-r"><select id="vai-paese" data-vai><option value="">Choose a country…</option>{opzioni}</select></div></form>
<p class="small" style="margin:8px 0 0">{len(PAESI_RIF)} countries with at least {intero(SOGLIA_PAGINA)} Schengen visa applications in {A1}. Each page shows the rate for every Schengen country and consulate, the easiest and hardest countries, and the UK refusal rate (visitor, study and work visas) where available.</p></section>
</div></div>"""
    corpo = f"""<section class="card summary" aria-label="Summary" style="margin-top:22px">
<div class="s-top">{ico("passport")}<span>Schengen short-stay visas</span><span>{A1}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">All Schengen countries · all consulates · {A1}</span><span class="sr">: </span><strong>{pct(t1)}</strong> of decisions were visas not issued</p>
<div class="kpi"><div><b>{intero(TOT_UE[A1][0])}</b><span>applications</span></div><div><b>{intero(TOT_UE[A1][1])}</b><span>uniform visas issued</span></div><div><b>{intero(TOT_UE[A1][3])}</b><span>not issued</span></div><div><b>{punti(t1, t0)}</b><span>change on {A0} ({pct(t0)})</span></div></div>
<p class="lead" style="margin-top:6px">Lowest rate in {A1}: {escape(basso[0])} ({pct(tasso(PER_STATO[A1][basso[0]]))}). Highest: {escape(basso[-1])} ({pct(tasso(PER_STATO[A1][basso[-1]]))}). Rates depend a lot on where each country's consulates are, so compare a country with others <em>in the same place</em> (see the country pages).</p>
{fonte_ue_p(A1, A0)}
</div></section>
{AVVISO_RIF}
{AD}
<h2>Schengen visa rejection rate by country ({A1})</h2>
<p class="small">All {len(STATI_UE)} Schengen countries that process visas (Liechtenstein is represented by Switzerland). Tap a column heading to sort.</p>
<div class="tab compatta"><table class="ord"><thead><tr>{th_ord("Schengen country", False, "ascending")}{th_ord(f"Rate {A1}", primo="ascending")}{th_ord(f"{A0}", primo="ascending")}{th_ord("Applications")}{th_ord("Visas issued")}{th_ord("Not issued")}</tr></thead><tbody>{"".join(righe_s)}</tbody></table></div>
{fonte_ue_p(A1, A0)}
<h2>Schengen visa rejection rate by country where people apply ({A1})</h2>
<p class="small">The {len(PAESI_RIF)} countries with at least {intero(SOGLIA_PAGINA)} applications. Tap a column heading to sort, or type to filter.</p>
<p class="filtro"><label><span class="sr">Filter countries</span><input type="search" placeholder="Filter: e.g. Pakistan" data-filtro="t-paesi" autocomplete="off"></label></p>
<div class="tab compatta"><table class="ord" id="t-paesi"><thead><tr>{th_ord("Applied in", False, "ascending")}{th_ord(f"Rate {A1}", primo="ascending")}{th_ord(f"{A0}", primo="ascending")}{th_ord("Applications")}{th_ord("Not issued")}</tr></thead><tbody>{"".join(righe_p)}</tbody></table></div>
{fonte_ue_p(A1, A0)}
<h2>Easiest Schengen visa, by country where you apply ({A1})</h2>
<p class="lead">"Which Schengen country has the lowest rejection rate for applicants from my country?" For the {len(PAESI_FACILE)} countries where at least {SOGLIA_FACILE} Schengen countries decided {intero(SOGLIA_CLASSIFICA)}+ applications, a page ranks every country and consulate from the lowest not-issued rate. Rates describe past decisions, not your chances.</p>
<div class="griglia">{''.join(f'<a href="{SLUG_RIF[x]}/easiest-schengen-visa/"><span class="ic">{ico("passport")}</span><span>Easiest Schengen visa from {escape(art(nome_paese(x)))}<small>lowest rate: {escape(classifica(raggruppa(A1, 0, lambda r, x=x: r[1] == x))[0][0][0])}</small></span></a>' for x in PAESI_FACILE[:12])}</div>
<p class="small">The other {len(PAESI_FACILE) - 12} rankings are linked from each country page.</p>
<h2>UK visitor visa refusal rate by nationality</h2>
<p class="lead">The 12 nationalities with the most UK visitor visa decisions from {periodo_uk(T1)}. <a href="uk/">All nationalities, with student and work visa refusal rates</a>.</p>
<div class="tab compatta"><table><thead><tr><th scope="col">Nationality</th><th class="n" scope="col">Refusal rate</th><th class="n" scope="col">Decisions</th><th class="n" scope="col">Refused</th></tr></thead><tbody>{"".join(uk_top)}</tbody></table></div>
{fonte_uk_p()}
<h2 id="destinations">Australia, New Zealand and Canada</h2>
<p class="lead">Refusal and approval rates by nationality from the immigration authorities of Australia (student and visitor visas), New Zealand (visitor, student and work visas) and Canada (temporary residents). Each country defines its rate differently: the notes on each page say how.</p>
{schede_destinazioni("")}
{box_assicurazione(rel)}
<h2 id="method">What these numbers mean</h2>
<div class="testo">
<h3>Schengen (European Commission)</h3>
<ul><li><strong>Source:</strong> the Commission's yearly "Visa statistics for consulates", which every Schengen country must report under Article 46 of the Visa Code. Latest year: {A1}; we also show {A0} for comparison. The next file (year {int(A1) + 1}) is usually published in spring.</li>
<li><strong>Not issued</strong> means refused, plus applications whose examination was discontinued (Commission metadata). We use the Commission's own formula: not issued ÷ (uniform visas issued + visas with limited territorial validity + not issued). Applications and decisions in a year do not match exactly, because some decisions fall in the next year.</li>
<li><strong>By the country where the application was made</strong>, not by nationality. The figures for "India" are applications lodged at consulates or visa centres in India, which also include residents of other nationalities.</li>
<li>Short-stay visas only (up to 90 days in any 180 days): tourism, business, family visits. Long-stay national visas (work, study, residence) are not included.</li></ul>
<h3>United Kingdom (Home Office)</h3>
<ul><li><strong>Source:</strong> the Home Office's quarterly entry clearance visa datasets, by <strong>nationality</strong>. We use the latest four quarters ({periodo_uk(T1)}) and the four before.</li>
<li><strong>Refusal rate</strong> = refused ÷ (granted + refused); withdrawn and lapsed applications are left out, as in the Home Office grant rate.</li></ul>
<h3>Australia, New Zealand and Canada</h3>
<ul><li><strong>Australia:</strong> Department of Home Affairs monthly student visa file (BP0015, refused ÷ granted + refused, by citizenship, financial years July–June) and six-monthly visitor visa report (grant rates for the largest groups).</li>
<li><strong>New Zealand:</strong> Immigration New Zealand monthly PDFs of visitor, student and work visa applications approved and declined by nationality; INZ's "declined" includes withdrawn applications.</li>
<li><strong>Canada:</strong> IRCC monthly files of temporary resident applications processed and approved by source country (visitor visas, study and work permits together). IRCC does not publish both numbers for study permits or visitor visas alone, so we show no refusal rate for them.</li>
<li>We show a rate only where there were at least {intero(SOGLIA_ALTRI)} decisions in the latest full year.</li></ul>
<h3>United States</h3>
<p>The US Department of State publishes a yearly B visa refusal rate by nationality, but its website could not be reached by our checks on {data_lunga(F_UE[A1]["scaricato_il"])}. We publish only figures we can download from the official source and check, so there are no US figures here.</p>
<h3>Checks</h3>
<p>Our script downloads the official files, recalculates every rate and checks it against the rate printed in the Commission's file, and checks the UK totals against the Home Office's published summary table. Every table on these pages shows its source and the date we downloaded it.</p>
</div>
<h2>Schengen countries</h2>
<div class="griglia">{''.join(scheda_stato(x, "schengen/") for x in STATI_UE)}</div>
<h2>Official sources</h2>
<ul class="fonti">
<li><a href="{escape(F_UE[A1]["url"])}" rel="noopener">Visa statistics for consulates {A1}</a> – European Commission, XLSX ({escape(F_UE[A1]["file"])}), downloaded on {data_lunga(F_UE[A1]["scaricato_il"])}</li>
<li><a href="{escape(F_UE[A0]["url"])}" rel="noopener">Visa statistics for consulates {A0}</a> – European Commission, XLSX, downloaded on {data_lunga(F_UE[A0]["scaricato_il"])}</li>
<li><a href="{escape(F_UE[A1]["pagina"])}" rel="noopener">Short-stay visas issued by Schengen countries (all years and metadata)</a> – European Commission, page updated on {data_lunga(F_UE[A1]["pagina_aggiornata"])}</li>
<li><a href="{escape(F_UK["url"])}" rel="noopener">{escape(F_UK["titolo"])}</a> – Home Office, XLSX, published {escape(F_UK["pubblicato"])}, downloaded on {data_lunga(F_UK["scaricato_il"])}. Contains public sector information licensed under the Open Government Licence v3.0.</li>
<li><a href="{URL_COMMISSIONE_DOMANDA}" rel="noopener">Applying for a Schengen visa</a> – European Commission, checked on {data_lunga(DATA_COMMISSIONE_DOMANDA)}</li>
<li><a href="{escape(F_AUS["url"])}" rel="noopener">{escape(F_AUS["titolo"])}</a> – Australian Government Department of Home Affairs, data.gov.au, downloaded on {data_lunga(F_AUS["scaricato_il"])}, {lic_link(F_AUS)}</li>
<li><a href="{escape(F2["nz_visitor"]["pagina"])}" rel="noopener">Immigration statistics</a> – Immigration New Zealand, PDFs downloaded on {data_lunga(F2["nz_visitor"]["scaricato_il"])}, Crown copyright, {lic_link(F2["nz_visitor"])}</li>
<li><a href="{escape(F2["ca_tr_processed"]["pagina"])}" rel="noopener">Operational Processing – Monthly IRCC Updates</a> – IRCC, downloaded on {data_lunga(F2["ca_tr_processed"]["scaricato_il"])}. Contains information licensed under the {lic_link(F2["ca_tr_processed"])}.</li></ul>
<p><a href="{rel}">Visa income calculator</a> · <a href="{rel}digital-nomad-visa-income-requirements/">Digital nomad visa income requirements</a></p>"""
    ld = {"@context": "https://schema.org", "@type": "Dataset", "name": f"Schengen and UK visa refusal rates {A1}",
          "description": "Visa refusal (not-issued) rates by Schengen country, by country of application and by consulate, and UK refusal rates by nationality, recalculated from official files.",
          "url": f"{URL_SITO}/{SEZ}", "creator": {"@type": "Organization", "name": NOME, "url": URL_SITO + "/"},
          "isBasedOn": [F_UE[A1]["url"], F_UE[A0]["url"], F_UK["url"]], "temporalCoverage": f"{A0}/{TRIM[-1].split()[0]}",
          "license": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"}
    pagina(SEZ, f"Schengen visa rejection rate by country {A1} (official) and UK visa refusal rates",
           f"Official {A1} Schengen visa rejection rates: {pct(t1)} of decisions were visas not issued. Every Schengen country, {len(PAESI_RIF)} countries where people apply, and UK refusal rates by nationality.",
           corpo, ordina=True, testata=testata, jsonld_extra=ld, briciole=[("Visa refusal rates", SEZ)])


# ---------------------------------------------------------------- Australia, Nuova Zelanda, Canada (26/10/2026)
# Dati: dati/rifiuti_altri.json, scritto da raccolta/rifiuti_altri.py dai file ufficiali (Home Affairs, Immigration New Zealand, IRCC).
# Le pagine di riepilogo stanno in australia-visas/, new-zealand-visas/, canada-visas/ perché /australia/ e /canada/ sono già
# le pagine Schengen "domande fatte in Australia / in Canada" (online dal 15/10/2026).
RIF2 = json.loads((DATI / "rifiuti_altri.json").read_text(encoding="utf-8"))
F2 = RIF2["fonti"]
SOGLIA_ALTRI = 500   # decisioni minime nell'ultimo anno completo per mostrare un tasso (Australia, Nuova Zelanda, Canada)
SEZ_AU, SEZ_NZ, SEZ_CA = f"{SEZ}australia-visas/", f"{SEZ}new-zealand-visas/", f"{SEZ}canada-visas/"

_B.update({
    "Australia": '<path fill="#012169" d="M0 0h30v20H0z"/><svg width="15" height="10" viewBox="0 0 30 20">' + _B["United Kingdom"] + '</svg>'
                 '<path fill="#fff" d="M7.5 12.6l.7 1.6 1.7-.4-.8 1.6 1.4 1-1.7.3.1 1.7-1.4-1-1.4 1 .1-1.7-1.7-.3 1.4-1-.8-1.6 1.7.4z"/>'
                 '<circle fill="#fff" cx="22.5" cy="4" r="1.1"/><circle fill="#fff" cx="19" cy="9" r="1.1"/><circle fill="#fff" cx="26" cy="8" r="1.1"/>'
                 '<circle fill="#fff" cx="22.5" cy="16" r="1.2"/><circle fill="#fff" cx="24.3" cy="11.6" r=".7"/>',
    "New Zealand": '<path fill="#012169" d="M0 0h30v20H0z"/><svg width="15" height="10" viewBox="0 0 30 20">' + _B["United Kingdom"] + '</svg>'
                   '<g fill="#C8102E" stroke="#fff" stroke-width=".5"><circle cx="22.5" cy="4.5" r="1.2"/><circle cx="19.5" cy="9.5" r="1.2"/>'
                   '<circle cx="25.5" cy="8.5" r="1"/><circle cx="22.5" cy="15.5" r="1.3"/></g>',
    "Canada": '<path fill="#fff" d="M0 0h30v20H0z"/><path fill="#D80621" d="M0 0h7.5v20H0zM22.5 0H30v20h-7.5z"/>'
              '<path fill="#D80621" d="M15 4l1.2 2.4 1.6-.6-.6 3.2 2.2-2 .6 1.4 1.8-.4-1 2.4.8.6-3.4 2.6.4 1.4-3.1-.5V16h-1v-1.5l-3.1.5.4-1.4-3.4-2.6.8-.6-1-2.4 1.8.4.6-1.4 2.2 2-.6-3.2 1.6.6z"/>',
})

# Nomi delle nazionalità nei tre file -> chiave come nel file della Commissione (per collegare le pagine e scrivere i nomi allo stesso modo).
_ALIAS_ALTRI = {
    # Australia (Home Affairs)
    "China, Peoples Republic of (excl SARs)": "CHINA", "Hong Kong (SAR of the PRC)": "HONG KONG S.A.R.", "Macau (SAR of the PRC)": "MACAO S.A.R.",
    "Turkiye": "TÜRKIYE", "United States of America": "USA", "Korea, South": "SOUTH KOREA", "Korea, North": "NORTH KOREA",
    "Germany, Fed Republic of": "GERMANY", "Ireland, Republic of": "IRELAND", "Netherlands, Kingdom of The": "NETHERLANDS",
    "Lao Peoples Dem Republic": "LAOS", "Yemen, Republic of": "YEMEN", "Syrian Arab Republic": "SYRIA", "Congo, Republic of": "CONGO (BRAZZAVILLE)",
    "Congo, Dem Republic of The": "CONGO (DEMOCRATIC REPUBLIC)", "Cote d'Ivoire": "COTE D'IVOIRE", "Cabo Verde": "CAPE VERDE",
    "Palestine, State of": "PALESTINIAN AUTHORITY", "Palestinian Authority": "PALESTINIAN AUTHORITY", "Czechia": "CZECH REPUBLIC",
    "Brunei Darussalam": "BRUNEI", "Republic of South Sudan": "SOUTH SUDAN", "Naoero": "NAURU", "St Vincent & the Grenadines": "SAINT VINCENT AND THE GRENADINES",
    "St Kitts and Nevis": "SAINT KITTS AND NEVIS", "Eswatini": "ESWATINI",
    # Nuova Zelanda (INZ)
    "Great Britain": "UNITED KINGDOM", "China": "CHINA", "Russia": "RUSSIAN FEDERATION", "Turkey": "TÜRKIYE", "Ivory Coast": "COTE D'IVOIRE",
    "Democratic Republic of Congo": "CONGO (DEMOCRATIC REPUBLIC)", "Congo": "CONGO (BRAZZAVILLE)", "Hong Kong": "HONG KONG S.A.R.", "Macau": "MACAO S.A.R.",
    "Palestine": "PALESTINIAN AUTHORITY", "Macedonia": "NORTH MACEDONIA", "Bosnia & Herzegovina": "BOSNIA AND HERZEGOVINA", "Timor Leste": "TIMOR-LESTE",
    "East Timor": "TIMOR-LESTE", "Equitorial Guinea": "EQUATORIAL GUINEA", "Guinea - Bissau": "GUINEA-BISSAU", "Swaziland": "ESWATINI",
    "Kosovo - Republic of": "KOSOVO", "Antigua & Barbuda": "ANTIGUA AND BARBUDA", "Sao Tome & Principe": "SAO TOME AND PRINCIPE",
    "St Kitts - Nevis": "SAINT KITTS AND NEVIS", "St Lucia": "SAINT LUCIA", "St Vincent and the Grenadines": "SAINT VINCENT AND THE GRENADINES",
    # Canada (IRCC)
    "People's Republic of China": "CHINA", "Socialist Republic of Vietnam": "VIETNAM", "Republic of Indonesia": "INDONESIA",
    "Republic of South Africa": "SOUTH AFRICA", "Korea, Republic of": "SOUTH KOREA", "Korea, People's Democratic Republic of": "NORTH KOREA",
    "Republic of Ireland": "IRELAND", "Republic of Ivory Coast": "COTE D'IVOIRE", "Federal Republic of Cameroon": "CAMEROON",
    "Peoples Republic of Benin": "BENIN", "Gabon Republic": "GABON", "Guinea, Republic of": "GUINEA", "Mali, Republic of": "MALI",
    "Mongolia, People's Republic of": "MONGOLIA", "Serbia, Republic of": "SERBIA", "Congo, Democratic Republic of the": "CONGO (DEMOCRATIC REPUBLIC)",
    "Congo, People's Republic of the": "CONGO (BRAZZAVILLE)", "Cape Verde Islands": "CAPE VERDE", "Togo, Republic of": "TOGO",
    "United Republic of Tanzania": "TANZANIA", "United Kingdom and Overseas Territories": "UNITED KINGDOM", "Myanmar (Burma)": "MYANMAR",
    "Palestinian Authority (Gaza/West Bank)": "PALESTINIAN AUTHORITY", "Macao": "MACAO S.A.R.", "Maldives, Republic of": "MALDIVES",
    "Panama, Republic of": "PANAMA", "Federal Republic of Germany": "GERMANY", "The Netherlands": "NETHERLANDS", "Bahama Islands, The": "BAHAMAS",
    "Surinam": "SURINAME", "Burkina-Faso": "BURKINA FASO", "Botswana, Republic of": "BOTSWANA", "Chad, Republic of": "CHAD",
    "Republic of the Niger": "NIGER", "Somalia, Democratic Republic of": "SOMALIA", "South Sudan, Republic Of": "SOUTH SUDAN",
    "Trinidad and Tobago, Republic of": "TRINIDAD AND TOBAGO", "Samoa, Independent State Of": "SAMOA", "Slovak Republic": "SLOVAKIA",
    "Montenegro, Republic of": "MONTENEGRO", "Bosnia-Hercegovina": "BOSNIA AND HERZEGOVINA", "Kosovo, Republic of": "KOSOVO",
    "Democratic Republic of Sudan": "SUDAN", "East Timor, Democratic Republic of": "TIMOR-LESTE", "Republic of Djibouti": "DJIBOUTI",
    "Republic of Palau": "PALAU", "Republic of The Marshall Islands": "MARSHALL ISLANDS", "Solomons, The": "SOLOMON ISLANDS",
    "St. Kitts-Nevis": "SAINT KITTS AND NEVIS", "St. Lucia": "SAINT LUCIA", "St. Vincent and the Grenadines": "SAINT VINCENT AND THE GRENADINES",
}
# Voci dei file che non sono nazionalità (escluse da tabelle e classifiche)
NON_NAZIONALITA = {"Not Specified", "Stateless Person", "UN Convention Refugee", "Refugee", "UNMIK Travel Document", "United Nations Organisation",
                   "Yugoslavia, Fed Republic of", "Serbia and Montenegro", "Unknown", "Stateless", "United Nations", "European Commission",
                   "Soviet Union", "Yugoslavia", "Kosovo - UN Mission in", "Pacific Island Trust Territory", "South Pacific commission",
                   "Other*", "Total", "Other countries"}


def chiave_altri(n):
    return _ALIAS_ALTRI.get(n, n.upper())


def nome_altri(n):
    return nome_paese(chiave_altri(n))


def nome_per_pagina(nomi_fonte, p):
    """Nome della nazionalità in un file (Australia, NZ, Canada) che corrisponde alla pagina del Paese p (chiave della Commissione)."""
    return next((n for n in nomi_fonte if n not in NON_NAZIONALITA and chiave_altri(n) == p), None)


def link_paese_altri(n, rel, ancora):
    """Nome con il link alla pagina del Paese (se c'è) e all'ancora della sezione."""
    k = chiave_altri(n)
    if k in SLUG_RIF and k not in ("AUSTRALIA", "CANADA"):
        return f'<a href="{rel}{SEZ}{SLUG_RIF[k]}/#{ancora}">{escape(nome_paese(k))}</a>'
    return escape(nome_paese(k))


def rapporto(v):
    """v = [sì, no] -> quota del no (rifiutati / respinti) su sì + no."""
    d = v[0] + v[1]
    return v[1] / d if d else None


def cella_quota(v, soglia_piena=SOGLIA_ALTRI, minimo=SOGLIA_POCO):
    """Tasso del 'no' con barretta; * sotto soglia_piena, '–' sotto minimo."""
    d = v[0] + v[1]
    if d < minimo:
        return cella_tasso(None)
    return cella_tasso(rapporto(v), d < soglia_piena)


def lic_link(f):
    return f'<a href="{escape(f["licenza_url"])}" rel="license noopener">{escape(f["licenza"])}</a>'


# ---------- Australia, studenti (BP0015)
AU = RIF2["au"]
AU_NAZ = AU["naz"]
AU_PIENI = [a for a in AU["anni"] if re.fullmatch(r"\d{4}-\d{2}", a)]
AU_A1, AU_A0 = AU_PIENI[-1], AU_PIENI[-2]
AU_YTD = AU["anni"][-1] if AU["anni"][-1] not in AU_PIENI else None
PO, PI, SEC, TUTTI = (0,), (2,), (1, 3), (0, 1, 2, 3)  # primari fuori dall'Australia, primari in Australia, familiari, tutti
NOMI_SETTORI = {"Higher Education Sector": "Higher education (university)", "Vocational Education and Training Sector": "Vocational education and training (VET)",
                "Postgraduate Research Sector": "Postgraduate research", "Independent ELICOS Sector": "English language courses (ELICOS)",
                "Non-Award Sector": "Non-award courses", "Schools Sector": "Schools", "Foreign Affairs or Defence Sector": "Foreign Affairs or Defence"}


def au_fy(a):
    """'2025-26' -> 'July 2025 to June 2026'."""
    y = int(a[:4])
    return f"July {y} to June {y + 1}"


def au_ytd_testo():
    m = re.search(r"(\d{4})-\d\d to \d{1,2} (\w+) (\d{4})", AU_YTD or "")
    if not m:
        return ""
    return f"July to {m.group(2)} {m.group(3)}" if m.group(1) == m.group(3) else f"July {m.group(1)} to {m.group(2)} {m.group(3)}"


def au_ytd_breve():
    m = re.search(r"to \d{1,2} (\w+) (\d{4})", AU_YTD or "")
    return f"Jul–{m.group(1)[:3]} {m.group(2)}" if m else ""


AU_FINO_AL = re.search(r"to (\d{1,2} \w+ \d{4})", AU_YTD or "").group(1) if AU_YTD else f"30 June {AU_A1[:2]}{AU_A1[-2:]}"


def au_v(n, anno, combo, chiave="y", sotto=None):
    """[concessi, rifiutati] per nazionalità n (None = tutte), anno, combinazioni (indici di AU['combo'])."""
    v = [0, 0]
    for x in (AU_NAZ.values() if n is None else [AU_NAZ.get(n, {})]):
        base = x.get(chiave, {}).get(anno, {})
        celle = base.get(sotto) if sotto is not None else base
        if not celle:
            continue
        for i in combo:
            v[0] += celle[i][0]
            v[1] += celle[i][1]
    return v


def au_mesi(n, quanti=12):
    """Ultimi 'quanti' mesi con dati: [(etichetta, [concessi, rifiutati]) ...] per i primari fuori dall'Australia."""
    out = []
    for a in AU["anni"][-ANNI_DETTAGLIO_AU:]:
        y = int(a[:4])
        for m in AU["mesi"]:
            mese = m.split()[1]
            anno_cal = y if mese in ("Jul", "Aug", "Sep", "Oct", "Nov", "Dec") else y + 1
            tot = au_v(None, a, PO, "m", m)
            if tot[0] + tot[1] == 0:
                continue
            out.append((f"{mese} {anno_cal}", au_v(n, a, PO, "m", m)))
    return out[-quanti:]


ANNI_DETTAGLIO_AU = 3
AU_OK = sorted([n for n in AU_NAZ if n not in NON_NAZIONALITA and sum(au_v(n, AU_A1, PO)) >= SOGLIA_ALTRI],
               key=lambda n: -sum(au_v(n, AU_A1, PO)))
F_AUS, F_AUT, F_AUC = F2["au_studenti"], F2.get("au_turisti"), F2.get("au_turisti_concessi")


def fonte_au_p(extra="", breve=False):
    f = F_AUS
    if breve:
        return (f'<p class="fonte">Source: <a href="{escape(f["url"])}" rel="noopener">Home Affairs, BP0015 Student visa grant rates</a>, same file as above '
                f'(decisions to {AU_FINO_AL}, downloaded on {data_lunga(f["scaricato_il"])}, {lic_link(f)}).{extra}</p>')
    return (f'<p class="fonte">Source: <a href="{escape(f["url"])}" rel="noopener">Australian Government Department of Home Affairs, BP0015 Student visa grant rates</a> '
            f'(XLSX on <a href="{escape(f["pagina"])}" rel="noopener">data.gov.au</a>, decisions to {AU_FINO_AL}, downloaded on {data_lunga(f["scaricato_il"])}), '
            f'licensed under {lic_link(f)}. Student visas (subclass 500); refusal rate = refused ÷ (granted + refused), the complement of the Department\'s grant rate. '
            f'The Department says the figures are provisional and is not responsible for our analysis.{extra}</p>')


# ---------- Australia, turisti (BR0112)
AU_TUR = RIF2["au_turisti"]
TRIM_AU = AU_TUR["trimestri"]


def trim_au_testo(t, breve=False):
    """'01/10/25–31/12/25' -> 'Oct–Dec 2025' (o 'October to December 2025')."""
    a, b = t.split("–")
    m0, m1, y = int(a.split("/")[1]), int(b.split("/")[1]), 2000 + int(b.split("/")[2])
    if breve:
        return f"{MESI[m0 - 1][:3]}–{MESI[m1 - 1][:3]} {y}"
    return f"{MESI[m0 - 1]} to {MESI[m1 - 1]} {y}"


def au_tur_ok(tab):
    """Nazionalità della tabella con almeno SOGLIA_ALTRI concessioni nell'ultimo trimestre (limite inferiore delle decisioni, file BP0018)."""
    righe = AU_TUR["tabelle"].get(tab, {}).get("righe", {})
    conc = AU_TUR["concessi_ultimo_trimestre"].get(tab, {})
    return [n for n in righe if n not in NON_NAZIONALITA and not n.startswith("All ") and conc.get(n, 0) >= SOGLIA_ALTRI]


NOMI_TUR = {"3.02": "Tourist visitor visas (subclass 600 and 676, as grouped in the report)", "3.03": "Sponsored tourist visitor visas (subclass 600, sponsored family stream)"}


def fonte_au_tur_p():
    f, c = F_AUT, F_AUC
    return (f'<p class="fonte">Source: <a href="{escape(f["url"])}" rel="noopener">Australian Government Department of Home Affairs, {escape(f["titolo"])}</a> '
            f'(PDF, tables 3.02 and 3.03, downloaded on {data_lunga(f["scaricato_il"])}), licensed under {lic_link(f)} (<a href="{escape(f["copyright"])}" rel="noopener">copyright notice</a>). '
            f'The report gives grant rates, not the number of decisions: we show a nationality only if the Department\'s '
            f'<a href="{escape(c["url"])}" rel="noopener">BP0018 visitor visas granted file</a> ({lic_link(c)}, downloaded on {data_lunga(c["scaricato_il"])}) counts at least '
            f'{intero(SOGLIA_ALTRI)} grants of that visa in the latest quarter, so the rate rests on at least {intero(SOGLIA_ALTRI)} decisions.</p>')


# ---------- Nuova Zelanda (INZ)
NZ = RIF2["nz"]["tipi"]
NZ_INFO = RIF2["nz"]["info"]["visitor"]
NZ_ANNI = NZ_INFO["anni"]
NZ_PARZIALE = not NZ_INFO["periodo"][1].startswith("30 June")
NZ_A1 = NZ_ANNI[-2] if NZ_PARZIALE else NZ_ANNI[-1]
NZ_A0 = NZ_ANNI[NZ_ANNI.index(NZ_A1) - 1]
NZ_YTD = NZ_ANNI[-1] if NZ_PARZIALE else None
NZ_TIPI = [("visitor", "Visitor visas", "visitor"), ("student", "Student visas", "student"), ("work", "Work visas", "work")]


def nz_fy(a):
    y = int(a[:4])
    return f"July {y} to June {y + 1}"


def nz_ytd_testo():
    fine = NZ_INFO["periodo"][1].split(" ", 1)[1]  # 'September 2026'
    return f"July to {fine}" if fine.endswith(NZ_YTD[:4]) else f"July {NZ_YTD[:4]} to {fine}"


def nz_v(n, tipo, anno):
    if n is None:
        v = [0, 0]
        for k, x in NZ[tipo].items():
            if k not in NON_NAZIONALITA:
                a = x.get(anno, [0, 0])
                v[0] += a[0]; v[1] += a[1]
        return v
    return NZ[tipo].get(n, {}).get(anno, [0, 0])


NZ_NOMI = sorted({n for t in NZ.values() for n in t if n not in NON_NAZIONALITA})
NZ_OK = sorted([n for n in NZ_NOMI if any(sum(nz_v(n, t, NZ_A1)) >= SOGLIA_ALTRI for t, _, _ in NZ_TIPI)],
               key=lambda n: -sum(sum(nz_v(n, t, NZ_A1)) for t, _, _ in NZ_TIPI))


def fonte_nz_p(tipi=("visitor", "student", "work"), breve=False):
    f = F2[f"nz_{tipi[0]}"]
    if breve:
        return (f'<p class="fonte">Source: <a href="{escape(f["pagina"])}" rel="noopener">Immigration New Zealand statistics</a>, same PDFs as above '
                f'(prepared {escape(f["preparato"])}, downloaded on {data_lunga(f["scaricato_il"])}, Crown copyright, {lic_link(f)}). '
                f'Declined includes withdrawn applications.</p>')
    link = "; ".join(f'<a href="{escape(F2[f"nz_{t}"]["url"])}" rel="noopener">{escape(F2[f"nz_{t}"]["titolo"])}</a>' for t in tipi)
    return (f'<p class="fonte">Source: Immigration New Zealand (Ministry of Business, Innovation and Employment): {link} '
            f'(PDF, prepared {escape(f["preparato"])}, decisions to {escape(f["periodo"][1])}, downloaded on {data_lunga(f["scaricato_il"])}). '
            f'Crown copyright, licensed under {lic_link(f)} (<a href="{escape(f["copyright"])}" rel="noopener">copyright notice</a>). '
            f'Decline rate = declined ÷ (approved + declined), applications; INZ counts withdrawn applications as declined. Financial years run from July to June.</p>')


# ---------- Canada (IRCC)
CA = RIF2["ca"]
CA_MESI = CA["tr_processed"]["mesi"]
_anni_ca = sorted({m[:4] for m in CA_MESI})
CA_PIENI = [a for a in _anni_ca if sum(1 for m in CA_MESI if m.startswith(a)) == 12]
CA_A1, CA_A0 = CA_PIENI[-1], CA_PIENI[-2]
CA_YTD = _anni_ca[-1] if _anni_ca[-1] not in CA_PIENI else None
CA_ULTIMO_MESE = MESI[int(CA_MESI[-1][5:]) - 1]


def ca_somma(file, n, anno):
    """Totale dell'anno: la colonna "Total" del file (IRCC la arrotonda dai dati non arrotondati, quindi è più precisa della somma dei mesi);
    se manca o non è pubblicata, la somma dei mesi ('--', da 1 a 4, conta 0). Restituisce anche il numero di mesi non pubblicati."""
    v = CA[file]["paesi"].get(n, {})
    xs = [x for m, x in v.items() if m.startswith(anno)]
    t = CA[file].get("totali", {}).get(n, {}).get(anno)
    return (t if t is not None else sum(x for x in xs if x is not None)), sum(1 for x in xs if x is None)


def cella_ca(file, n, anno):
    """Conteggio di un file IRCC in cella; '–' se il Paese non compare nel file (il file dei visti V-1 elenca solo i Paesi con visto)."""
    if n not in CA[file]["paesi"]:
        return '<td class="n" data-v="">–</td>'
    x = ca_somma(file, n, anno)[0]
    return f'<td class="n" data-v="{x}">{intero(x)}</td>'


def ca_quota(n, anno):
    """[approvati, esaminati] e quota approvata dei permessi temporanei."""
    ap, es = ca_somma("tr_approved", n, anno)[0], ca_somma("tr_processed", n, anno)[0]
    return ap, es, (ap / es if es else None)


CA_NOMI = [n for n in CA["tr_processed"]["paesi"] if n not in NON_NAZIONALITA]
CA_OK = sorted([n for n in CA_NOMI if ca_quota(n, CA_A1)[1] >= SOGLIA_ALTRI], key=lambda n: -ca_quota(n, CA_A1)[1])


NOMI_FILE_CA = {"tr_processed": "temporary resident applications processed", "tr_approved": "temporary resident applications approved",
                "sp_processed": "new study permit applications processed", "trv_approved": "visitor visas (V-1) approved"}


def fonte_ca_p(file=("tr_processed", "tr_approved")):
    f = F2[f"ca_{file[0]}"]
    link = ", ".join(f'<a href="{escape(F2[f"ca_{k}"]["url"])}" rel="noopener">{NOMI_FILE_CA[k]}</a>' for k in file)
    return (f'<p class="fonte">Source: Immigration, Refugees and Citizenship Canada (IRCC), <a href="{escape(f["pagina"])}" rel="noopener">Operational Processing – Monthly IRCC Updates</a>: '
            f'{link} (XLSX, data as of {escape(f["dati_al"])}, downloaded on {data_lunga(f["scaricato_il"])}). Contains information licensed under the '
            f'{lic_link(f)}. IRCC rounds counts to the nearest 5 and does not publish counts from 1 to 4; the data are operational and subject to change.</p>')


def barre_mesi(serie, etichetta, unita="decisions"):
    """Grafico a barre di 12 mesi (stesso stile dei trimestri UK)."""
    tt = [rapporto(v) for _, v in serie]
    mx = max([t for t in tt if t is not None] + [0.05])
    li = "".join(f'<li><span class="tq-v">{pct(t, 0) if t is not None else "–"}</span><span class="tq-c"><span class="tq-b" style="height:{max(3, round((t or 0) / mx * 100))}%"></span></span>'
                 f'<span class="tq-l">{m.split()[0]}<br>{m.split()[1]}</span><span class="sr"> {intero(v[0] + v[1])} {unita}</span></li>' for (m, v), t in zip(serie, tt))
    return f'<ol class="trim m12" aria-label="{escape(etichetta)}">{li}</ol>'


# ---------- sezioni nelle pagine per Paese
def sezione_au(p, nome):
    """Sezione Australia nella pagina del Paese p. Restituisce (html, cifra per il riquadro) o ('', None)."""
    if p == "AUSTRALIA":
        return "", None
    n = nome_per_pagina(AU_NAZ, p)
    if not n:
        return "", None
    v1 = au_v(n, AU_A1, PO)
    if sum(v1) < SOGLIA_ALTRI:
        return (f'<h2 id="australia">Australia student visa refusal rate</h2><p>In {AU_A1} Australia decided {intero(sum(v1))} student visa applications from primary applicants '
                f'who are nationals of {escape(art(nome))} and applied from outside Australia, fewer than the {intero(SOGLIA_ALTRI)} we need to show a meaningful rate. '
                f'See <a href="../australia-visas/">Australia visa refusal rates for all nationalities</a>.</p>'), None
    v0 = au_v(n, AU_A0, PO)
    vy = au_v(n, AU_YTD, PO) if AU_YTD else [0, 0]
    righe = []
    for etichetta, combo in (("Primary applicants applying from outside Australia", PO), ("Primary applicants applying in Australia", PI),
                             ("Family members (secondary applicants)", SEC), ("All student visa applicants", TUTTI)):
        a1, a0, ay = au_v(n, AU_A1, combo), au_v(n, AU_A0, combo), (au_v(n, AU_YTD, combo) if AU_YTD else [0, 0])
        if sum(a1) == 0:
            continue
        cls = ' class="tot-r"' if combo == TUTTI else ""
        righe.append(f'<tr{cls}><td>{etichetta}</td>{cella_quota(a1)}{cella_quota(a0)}{cella_quota(ay)}'
                     f'<td class="n" data-v="{sum(a1)}">{intero(sum(a1))}</td><td class="n" data-v="{a1[1]}">{intero(a1[1])}</td></tr>')
    tab = (f'<div class="tab compatta"><table class="ord larga"><thead><tr>{th_ord("Applicants", False, "ascending")}{th_ord(f"Refused {AU_A1}", primo="ascending")}'
           f'{th_ord(AU_A0, primo="ascending")}{th_ord(au_ytd_breve(), primo="ascending")}{th_ord(f"Decisions {AU_A1}")}{th_ord("Refused")}</tr></thead>'
           f'<tbody>{"".join(righe)}</tbody></table></div>')
    # per settore
    sett = AU_NAZ[n].get("s", {}).get(AU_A1, {})
    righe_s = []
    piccoli = []
    for s in sorted(sett, key=lambda s: -sum(sett[s][0])):
        v = sett[s][0]
        if sum(v) < SOGLIA_POCO:
            if sum(v):
                piccoli.append(NOMI_SETTORI.get(s, s))
            continue
        v0s = AU_NAZ[n]["s"].get(AU_A0, {}).get(s, [[0, 0]])[0]
        righe_s.append(f'<tr{" class=\"poco\"" if sum(v) < SOGLIA_ALTRI else ""}><td>{escape(NOMI_SETTORI.get(s, s))}</td>{cella_quota(v)}{cella_quota(v0s)}'
                       f'<td class="n" data-v="{sum(v)}">{intero(sum(v))}</td><td class="n" data-v="{v[1]}">{intero(v[1])}</td></tr>')
    tab_s = (f'<div class="tab compatta"><table class="ord"><thead><tr>{th_ord("Education sector", False, "ascending")}{th_ord(f"Refused {AU_A1}", primo="ascending")}'
             f'{th_ord(AU_A0, primo="ascending")}{th_ord("Decisions")}{th_ord("Refused")}</tr></thead><tbody>{"".join(righe_s)}</tbody></table></div>')
    # anni
    righe_a = []
    for a in AU["anni"][-11:]:
        po, tu = au_v(n, a, PO), au_v(n, a, TUTTI)
        if sum(tu) == 0:
            continue
        et = au_ytd_testo() + f" ({a[:7]})" if a == AU_YTD else a
        righe_a.append(f'<tr><td>{escape(et)}</td>{cella_quota(po)}<td class="n" data-v="{sum(po)}">{intero(sum(po))}</td>{cella_quota(tu)}<td class="n" data-v="{sum(tu)}">{intero(sum(tu))}</td></tr>')
    tab_a = (f'<div class="tab compatta"><table class="ord larga"><thead><tr>{th_ord("Financial year", False, "ascending")}{th_ord("Refused: primary, outside Australia", primo="ascending")}'
             f'{th_ord("Decisions")}{th_ord("Refused: all applicants", primo="ascending")}{th_ord("Decisions")}</tr></thead><tbody>{"".join(righe_a)}</tbody></table></div>')
    mesi = au_mesi(n)
    cambio = punti(rapporto(v1), rapporto(v0)) if sum(v0) else "–"
    frase_ytd = (f' From {au_ytd_testo()}: <strong>{pct(rapporto(vy))}</strong> ({intero(vy[1])} of {intero(sum(vy))} decisions'
                 + (', a small number: read with care' if sum(vy) < SOGLIA_ALTRI else '') + ').') if AU_YTD and sum(vy) >= SOGLIA_POCO else ""
    # turisti (se la nazionalità è nel rapporto con abbastanza concessioni)
    tur = ""
    righe_t = []
    for tab_id in ("3.02", "3.03"):
        if n in au_tur_ok(tab_id):
            rr = AU_TUR["tabelle"][tab_id]["righe"][n]
            celle = "".join(cella_tasso(1 - x) for x in rr)
            righe_t.append(f'<tr><td>{NOMI_TUR[tab_id]}</td>{celle}</tr>')
    if righe_t:
        testa = "".join(th_ord(trim_au_testo(t, True), primo="ascending") for t in TRIM_AU)
        tur = (f'<h3>Visitor visas: share not granted, quarter by quarter</h3>'
               f'<p class="lead">Home Affairs publishes visitor visa grant rates by citizenship only in its six-monthly visitor visa report, for the 15 countries it lists for each visa. For nationals of {escape(art(nome))}, these are the shares of decisions that were <strong>not</strong> grants (100% minus the grant rate).</p>'
               f'<div class="tab compatta"><table class="ord"><thead><tr>{th_ord("Visitor visa", False, "ascending")}{testa}</tr></thead><tbody>{"".join(righe_t)}</tbody></table></div>'
               f'{fonte_au_tur_p()}')
    corpo = (f'<h2 id="australia">Australia student visa refusal rate for nationals of {escape(art(nome))} ({AU_A1})</h2>'
             f'<p class="lead">In the Australian financial year {AU_A1} ({au_fy(AU_A1)}), Australia refused <strong>{pct(rapporto(v1))}</strong> of student visa decisions for primary applicants '
             f'who are nationals of {escape(art(nome))} and applied from outside Australia ({intero(v1[1])} refused out of {intero(sum(v1))}). '
             + (f'In {AU_A0}: {pct(rapporto(v0))} ({cambio}).' if sum(v0) >= SOGLIA_POCO else '') + frase_ytd +
             f' Like the UK, Australia counts applicants by <strong>citizenship</strong>, wherever they apply.</p>'
             f'{tab}{fonte_au_p(f" * Fewer than {intero(SOGLIA_ALTRI)} decisions; – fewer than {SOGLIA_POCO}.")}'
             f'<h3>Student visas by education sector (primary applicants outside Australia)</h3>{tab_s}{fonte_au_p(f" * Fewer than {intero(SOGLIA_ALTRI)} decisions; – fewer than {SOGLIA_POCO}." + (f" Not shown (fewer than {SOGLIA_POCO} decisions in {AU_A1}): {escape(', '.join(piccoli))}." if piccoli else ""), True)}'
             f'<h3>Month by month (primary applicants outside Australia)</h3>{barre_mesi(mesi, f"Australia student visa refusal rate by month, nationals of {nome}")}'
             f'<p class="fonte">Source: <a href="{escape(F_AUS["url"])}" rel="noopener">Home Affairs BP0015</a>, same file as above (decisions to {AU_FINO_AL}, downloaded on {data_lunga(F_AUS["scaricato_il"])}, {lic_link(F_AUS)}). Each bar is the share of decisions in that month that were refusals; monthly figures can be small and move a lot.</p>'
             f'<h3>Year by year</h3>{tab_a}{fonte_au_p(" Financial years run from July to June.", True)}'
             f'{tur}'
             f'<p class="small">All nationalities, by sector and month: <a href="../australia-visas/">Australia student visa refusal rate by nationality</a>.</p>')
    return corpo, (rapporto(v1), sum(v1))


def sezione_nz(p, nome):
    n = nome_per_pagina(NZ_NOMI, p)
    if not n or p == "NEW ZEALAND":
        return "", None
    ok = [(t, et, br) for t, et, br in NZ_TIPI if sum(nz_v(n, t, NZ_A1)) >= SOGLIA_ALTRI]
    if not ok:
        d = max(sum(nz_v(n, t, NZ_A1)) for t, _, _ in NZ_TIPI)
        return (f'<h2 id="new-zealand">New Zealand visa decline rate</h2><p>In {NZ_A1} Immigration New Zealand decided at most {intero(d)} visitor, student or work visa applications '
                f'from nationals of {escape(art(nome))} in each category, fewer than the {intero(SOGLIA_ALTRI)} we need to show a meaningful rate. '
                f'See <a href="../new-zealand-visas/">New Zealand visa decline rates for all nationalities</a>.</p>'), None
    righe = []
    for t, et, _ in NZ_TIPI:
        a1, a0 = nz_v(n, t, NZ_A1), nz_v(n, t, NZ_A0)
        ay = nz_v(n, t, NZ_YTD) if NZ_YTD else [0, 0]
        if sum(a1) == 0 and sum(a0) == 0:
            continue
        righe.append(f'<tr><td>{et}</td>{cella_quota(a1)}{cella_quota(a0)}{cella_quota(ay)}<td class="n" data-v="{sum(a1)}">{intero(sum(a1))}</td>'
                     f'<td class="n" data-v="{a1[1]}">{intero(a1[1])}</td></tr>')
    tab = (f'<div class="tab compatta"><table class="ord larga"><thead><tr>{th_ord("Visa type", False, "ascending")}{th_ord(f"Declined {NZ_A1}", primo="ascending")}'
           f'{th_ord(NZ_A0, primo="ascending")}{th_ord(nz_ytd_testo() if NZ_YTD else "", primo="ascending")}{th_ord(f"Decisions {NZ_A1}")}{th_ord("Declined")}</tr></thead>'
           f'<tbody>{"".join(righe)}</tbody></table></div>')
    righe_a = []
    for a in NZ_ANNI:
        celle = ""
        for t, _, _ in NZ_TIPI:
            v = nz_v(n, t, a)
            celle += f'{cella_quota(v)}<td class="n" data-v="{sum(v)}">{intero(sum(v))}</td>'
        et = f"{nz_ytd_testo()} ({a})" if a == NZ_YTD else a
        righe_a.append(f'<tr><td>{escape(et)}</td>{celle}</tr>')
    testa = "".join(f'{th_ord(f"{et} declined", primo="ascending")}{th_ord("Decisions")}' for _, et, _ in NZ_TIPI)
    tab_a = (f'<div class="tab compatta"><table class="ord larga"><thead><tr>{th_ord("Financial year", False, "ascending")}{testa}</tr></thead><tbody>{"".join(righe_a)}</tbody></table></div>')
    t1, _, br1 = ok[0]
    v1 = nz_v(n, t1, NZ_A1)
    altri = "; ".join(f'<strong>{pct(rapporto(nz_v(n, t, NZ_A1)))}</strong> of {br} visa applications ({intero(sum(nz_v(n, t, NZ_A1)))} decisions)' for t, _, br in ok[1:])
    corpo = (f'<h2 id="new-zealand">New Zealand visa decline rate for nationals of {escape(art(nome))} ({NZ_A1})</h2>'
             f'<p class="lead">In the New Zealand financial year {NZ_A1} ({nz_fy(NZ_A1)}), Immigration New Zealand declined <strong>{pct(rapporto(v1))}</strong> of {br1} visa applications '
             f'from nationals of {escape(art(nome))} ({intero(v1[1])} declined out of {intero(sum(v1))} decided)' + (f'; {altri}' if altri else '') + '. '
             f'INZ counts applications by the country that issued the passport, and its "declined" figure includes applications that were withdrawn, '
             f'so these rates are not directly comparable with the UK or Australian refusal rates.</p>'
             f'{tab}{fonte_nz_p()}'
             f'<h3>New Zealand, year by year</h3>{tab_a}{fonte_nz_p(breve=True)}'
             f'<p class="small">* Fewer than {intero(SOGLIA_ALTRI)} decisions; – fewer than {SOGLIA_POCO}. All nationalities: <a href="../new-zealand-visas/">New Zealand visa decline rate by nationality</a>.</p>')
    return corpo, (rapporto(v1), sum(v1), br1)


def sezione_ca(p, nome):
    if p == "CANADA":
        return "", None
    n = nome_per_pagina(CA_NOMI, p)
    if not n:
        return "", None
    ap, es, q = ca_quota(n, CA_A1)
    if es < SOGLIA_ALTRI:
        return (f'<h2 id="canada">Canada temporary resident applications</h2><p>IRCC processed {intero(es)} temporary resident applications from {escape(art(nome))} in {CA_A1}, '
                f'fewer than the {intero(SOGLIA_ALTRI)} we need to show a meaningful rate. See <a href="../canada-visas/">Canada temporary resident approval rates by country</a>.</p>'), None
    ap0, es0, q0 = ca_quota(n, CA_A0)
    apy, esy, qy = ca_quota(n, CA_YTD) if CA_YTD else (0, 0, None)
    sp = ca_somma("sp_processed", n, CA_A1)[0]
    trv = ca_somma("trv_approved", n, CA_A1)[0]
    righe = []
    for a in ([CA_YTD] if CA_YTD else []) + CA_PIENI[::-1]:
        x_ap, x_es, x_q = ca_quota(n, a)
        x_sp, x_trv = ca_somma("sp_processed", n, a)[0], ca_somma("trv_approved", n, a)[0]
        et = f"January to {CA_ULTIMO_MESE} {a}" if a == CA_YTD else a
        righe.append(f'<tr><td>{et}</td>{cella_tasso(x_q, x_es < SOGLIA_ALTRI) if x_es >= SOGLIA_POCO else cella_tasso(None)}<td class="n" data-v="{x_es}">{intero(x_es)}</td>'
                     f'<td class="n" data-v="{x_ap}">{intero(x_ap)}</td>{cella_ca("sp_processed", n, a)}{cella_ca("trv_approved", n, a)}</tr>')
    tab = (f'<div class="tab compatta"><table class="ord larga"><thead><tr>{th_ord("Period", False, "ascending")}{th_ord("Approved: all temporary resident applications")}'
           f'{th_ord("Processed")}{th_ord("Approved")}{th_ord("New study permits: processed")}{th_ord("Visitor visas: approved")}</tr></thead>'
           f'<tbody>{"".join(righe)}</tbody></table></div>')
    # ultimi 12 mesi: quota approvata
    serie = []
    for m in CA_MESI[-12:]:
        a_ = CA["tr_approved"]["paesi"].get(n, {}).get(m) or 0
        e_ = CA["tr_processed"]["paesi"].get(n, {}).get(m) or 0
        serie.append((f"{MESI[int(m[5:]) - 1][:3]} {m[:4]}", [e_ - a_ if e_ >= a_ else 0, a_]))  # rapporto() -> quota approvata
    corpo = (f'<h2 id="canada">Canada: temporary resident applications from {escape(art(nome))} approved ({CA_A1})</h2>'
             f'<p class="lead">In {CA_A1}, IRCC approved <strong>{pct(q)}</strong> of the temporary resident applications from {escape(art(nome))} that it processed '
             f'({intero(ap)} approved out of {intero(es)} people). This share mixes visitor visas, study permits and work permits, first applications and extensions; '
             f'"processed" includes applications refused and withdrawn, so the other {pct(1 - q)} were refused <em>or</em> withdrawn.'
             + (f' In {CA_A0}: {pct(q0)}.' if es0 >= SOGLIA_POCO else '') + (f' January to {CA_ULTIMO_MESE} {CA_YTD}: {pct(qy)} ({intero(esy)} processed).' if CA_YTD and esy >= SOGLIA_POCO else '') + '</p>'
             f'<p class="avviso"><strong>No study permit or visitor visa refusal rate.</strong> For each country IRCC publishes only the number of new study permit applications '
             f'<em>processed</em> ({intero(sp)} from {escape(art(nome))} in {CA_A1}) and the number of visitor visas <em>approved</em> ({intero(trv)}), never both for the same visa, '
             f'so a study permit or visitor visa refusal rate cannot be calculated from the official files.</p>'
             f'{tab}{fonte_ca_p(("tr_processed", "tr_approved", "sp_processed", "trv_approved"))}'
             f'<h3>Approved share, month by month (all temporary resident applications)</h3>{barre_mesi(serie, f"Canada temporary resident approval share by month, {nome}", "processed")}'
             f'<p class="fonte">Source: IRCC, same files as above (data as of {escape(F2["ca_tr_processed"]["dati_al"])}, downloaded on {data_lunga(F2["ca_tr_processed"]["scaricato_il"])}). '
             f'Each bar is approved ÷ processed in that month. Contains information licensed under the {lic_link(F2["ca_tr_processed"])}.</p>'
             f'<p class="small">All countries: <a href="../canada-visas/">Canada temporary resident approval rate by country</a>.</p>')
    return corpo, (q, es)


def kpi_altri(au_r, nz_r, ca_r):
    """Riga del riquadro di sintesi con le altre destinazioni e la fonte."""
    voci, fonti = [], []
    if au_r:
        voci.append(f'<div><b>{pct(au_r[0])}</b><span><a href="#australia">Australia</a> student visas refused · {AU_A1} · {intero(au_r[1])} decisions</span></div>')
        fonti.append(f'<a href="{escape(F_AUS["url"])}" rel="noopener">Home Affairs BP0015</a> (to {AU_FINO_AL}, {lic_link(F_AUS)})')
    if nz_r:
        voci.append(f'<div><b>{pct(nz_r[0])}</b><span><a href="#new-zealand">New Zealand</a> {nz_r[2]} visas declined · {NZ_A1} · {intero(nz_r[1])} decisions</span></div>')
        fonti.append(f'<a href="{escape(F2["nz_visitor"]["pagina"])}" rel="noopener">Immigration New Zealand</a> (to {escape(F2["nz_visitor"]["periodo"][1])}, {lic_link(F2["nz_visitor"])})')
    if ca_r:
        voci.append(f'<div><b>{pct(ca_r[0])}</b><span><a href="#canada">Canada</a> temporary resident applications approved · {CA_A1} · {intero(ca_r[1])} processed</span></div>')
        fonti.append(f'<a href="{escape(F2["ca_tr_processed"]["pagina"])}" rel="noopener">IRCC</a> ({CA_A1}, Open Government Licence – Canada)')
    if not voci:
        return ""
    return (f'<p class="cifra cifra-2"><span class="c-lab">Australia, New Zealand and Canada · by citizenship</span>'
            f'<span class="sr">: </span>Latest official full-year figures for nationals of this country</p><div class="kpi kpi-uk">{"".join(voci)}</div>'
            f'<p class="fonte">Sources: {"; ".join(fonti)}; downloaded on {data_lunga(F_AUS["scaricato_il"])}. Details and definitions below.</p>')


# ---------- pagine di riepilogo
def avviso_altri(testo_regola):
    return ('<p class="avviso"><strong>Statistics, not advice.</strong> These are official figures for all applications decided in a past period. '
            'They cannot predict the decision on your application, and they mix very different applicants, courses and documents. '
            f'{testo_regola} Always follow the official requirements of the immigration authority.</p>')


def pagina_rif_au():
    rel = "../../"
    tot1, tot0 = au_v(None, AU_A1, PO), au_v(None, AU_A0, PO)
    toty = au_v(None, AU_YTD, PO) if AU_YTD else [0, 0]
    tutti1 = au_v(None, AU_A1, TUTTI)
    righe = []
    for n in AU_OK:
        v1, v0 = au_v(n, AU_A1, PO), au_v(n, AU_A0, PO)
        vy = au_v(n, AU_YTD, PO) if AU_YTD else [0, 0]
        tu = au_v(n, AU_A1, TUTTI)
        r1, r0 = rapporto(v1), rapporto(v0)
        d = (r1 - r0) if (r0 is not None and sum(v0) >= SOGLIA_POCO) else None
        righe.append(f'<tr><td>{link_paese_altri(n, rel, "australia")}</td>{cella_quota(v1)}{cella_quota(v0)}'
                     f'<td class="n" data-v="{"" if d is None else f"{d:.6f}"}">{punti(r1, r0) if d is not None else "–"}</td>{cella_quota(vy)}'
                     f'<td class="n" data-v="{sum(v1)}">{intero(sum(v1))}</td>{cella_quota(tu)}</tr>')
    # settori, tutte le nazionalità
    righe_s = []
    sett_nomi = list(NOMI_SETTORI)
    for s in sett_nomi:
        v1, v0 = au_v(None, AU_A1, PO, "s", s), au_v(None, AU_A0, PO, "s", s)
        if sum(v1) == 0:
            continue
        righe_s.append(f'<tr><td>{escape(NOMI_SETTORI[s])}</td>{cella_quota(v1)}{cella_quota(v0)}<td class="n" data-v="{sum(v1)}">{intero(sum(v1))}</td>'
                       f'<td class="n" data-v="{v1[1]}">{intero(v1[1])}</td></tr>')
    # turisti
    blocchi_t = ""
    for tab_id in ("3.02", "3.03"):
        ok = au_tur_ok(tab_id)
        tt = AU_TUR["tabelle"].get(tab_id, {})
        if not ok:
            continue
        rr = tt["righe"]
        tutte = next((k for k in rr if k.startswith("All ")), None)
        righe_t = [f'<tr><td>{link_paese_altri(n, rel, "australia")}</td>{"".join(cella_tasso(1 - x) for x in rr[n])}'
                   f'<td class="n" data-v="{AU_TUR["concessi_ultimo_trimestre"][tab_id][n]}">{intero(AU_TUR["concessi_ultimo_trimestre"][tab_id][n])}</td></tr>' for n in ok]
        if tutte:
            righe_t.append(f'<tr class="tot-r"><td>All nationalities</td>{"".join(cella_tasso(1 - x) for x in rr[tutte])}<td class="n">–</td></tr>')
        esclusi = [nome_altri(n) for n in rr if n not in ok and n not in NON_NAZIONALITA and not n.startswith("All ")]
        testa = "".join(th_ord(trim_au_testo(t, True), primo="ascending") for t in TRIM_AU)
        blocchi_t += (f'<h3>{NOMI_TUR[tab_id]}: share not granted</h3>'
                      + (f'<p class="small">Also listed in the report, but with fewer than {intero(SOGLIA_ALTRI)} grants in the latest quarter, so not shown: {escape(", ".join(esclusi))}.</p>' if esclusi else '')
                      + f'<div class="tab compatta"><table class="ord"><thead><tr>{th_ord("Citizenship", False, "ascending")}{testa}{th_ord(f"Grants {trim_au_testo(TRIM_AU[-1], True)}")}</tr></thead>'
                        f'<tbody>{"".join(righe_t)}</tbody></table></div>{fonte_au_tur_p()}')
    mesi = au_mesi(None)
    opzioni = "".join(f'<option value="{rel}{SEZ}{SLUG_RIF[chiave_altri(n)]}/#australia">{escape(nome_altri(n))}</option>'
                      for n in sorted(AU_OK, key=nome_altri) if chiave_altri(n) in SLUG_RIF and chiave_altri(n) not in ("AUSTRALIA",))
    alto = sorted(AU_OK, key=lambda n: -rapporto(au_v(n, AU_A1, PO)))[:3]
    basso = sorted(AU_OK, key=lambda n: rapporto(au_v(n, AU_A1, PO)))[:3]
    corpo = f"""<section class="hero">{h1_diviso(f"Australia visa refusal rate by nationality: student visas {AU_A1}, and visitor visas")}
<p class="lead">How many Australian student visa applications were refused, nationality by nationality, from the Department of Home Affairs' official monthly file: by financial year, by month, by education sector, and whether the applicant was outside or in Australia. Visitor visa grant rates for the citizenships listed in the six-monthly report are below.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{bandiera("Australia")}<span>Australian student visas</span><span style="white-space:nowrap">{AU_A1}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Primary applicants outside Australia · all nationalities · {au_fy(AU_A1)}</span><span class="sr">: </span><strong>{pct(rapporto(tot1))}</strong> refused ({intero(tot1[1])} of {intero(sum(tot1))} decisions)</p>
<div class="kpi"><div><b>{pct(rapporto(tot0))}</b><span>in {AU_A0} ({punti(rapporto(tot1), rapporto(tot0))} in {AU_A1})</span></div><div><b>{pct(rapporto(toty))}</b><span>{au_ytd_testo()} · {intero(sum(toty))} decisions</span></div><div><b>{pct(rapporto(tutti1))}</b><span>all student visa applicants, {AU_A1}</span></div><div><b>{len(AU_OK)}</b><span>nationalities with {intero(SOGLIA_ALTRI)}+ decisions</span></div></div>
<p class="lead" style="margin-top:6px">Highest refusal rates in {AU_A1} among nationalities with at least {intero(SOGLIA_ALTRI)} decisions: {", ".join(f"{escape(nome_altri(n))} ({pct(rapporto(au_v(n, AU_A1, PO)))})" for n in alto)}. Lowest: {", ".join(f"{escape(nome_altri(n))} ({pct(rapporto(au_v(n, AU_A1, PO)))})" for n in basso)}.</p>
{fonte_au_p()}
</div></section>
{avviso_altri("A lower rate for your country, sector or month does not make your application more likely to succeed.")}
{AD}
<section class="card cerca"><form class="vai" action="#" onsubmit="return false"><label for="vai-au"><span class="lt">{ico("globe")}Your citizenship</span></label>
<div class="vai-r"><select id="vai-au" data-vai><option value="">Choose a country…</option>{opzioni}</select></div></form>
<p class="small" style="margin:8px 0 0">Country pages put the Australian figures next to the Schengen, UK, New Zealand and Canadian ones.</p></section>
<h2>Australia student visa refusal rate by nationality ({AU_A1})</h2>
<p class="small">Primary applicants applying from outside Australia, nationalities with at least {intero(SOGLIA_ALTRI)} decisions in {AU_A1} ({au_fy(AU_A1)}). "Change" is in percentage points on {AU_A0}. Tap a column heading to sort, or type to filter. * Fewer than {intero(SOGLIA_ALTRI)} decisions; – fewer than {SOGLIA_POCO}.</p>
<p class="filtro"><label><span class="sr">Filter nationalities</span><input type="search" placeholder="Filter: e.g. Nepal" data-filtro="t-au" autocomplete="off"></label></p>
<div class="tab compatta"><table class="ord larga" id="t-au"><thead><tr>{th_ord("Citizenship", False, "ascending")}{th_ord(f"Refused {AU_A1}", primo="ascending")}{th_ord(AU_A0, primo="ascending")}{th_ord("Change", primo="ascending")}{th_ord(au_ytd_breve(), primo="ascending")}{th_ord(f"Decisions {AU_A1}")}{th_ord("All applicants refused", primo="ascending")}</tr></thead><tbody>{"".join(righe)}</tbody></table></div>
{fonte_au_p(' "All applicants" adds primary applicants already in Australia and family members.')}
<h2>By education sector, all nationalities</h2>
<div class="tab compatta"><table class="ord"><thead><tr>{th_ord("Education sector", False, "ascending")}{th_ord(f"Refused {AU_A1}", primo="ascending")}{th_ord(AU_A0, primo="ascending")}{th_ord("Decisions")}{th_ord("Refused")}</tr></thead><tbody>{"".join(righe_s)}</tbody></table></div>
{fonte_au_p(" Primary applicants applying from outside Australia.", True)}
<h2>Month by month, all nationalities</h2>
{barre_mesi(mesi, "Australia student visa refusal rate by month, all nationalities")}
<p class="fonte">Source: Home Affairs BP0015, same file as above (decisions to {AU_FINO_AL}, downloaded on {data_lunga(F_AUS["scaricato_il"])}, {lic_link(F_AUS)}). Primary applicants outside Australia; each bar is the share of decisions in that month that were refusals.</p>
<h2 id="visitor">Australia visitor visa grant rates by citizenship</h2>
<p class="lead">For visitor visas Home Affairs publishes rates by citizenship only in its six-monthly visitor visa report, for the 15 citizenship countries it lists for each visa (the rest are grouped as "other countries"), quarter by quarter. Below: the share of decisions that were not grants (100% minus the published grant rate). Electronic travel authorities (ETA) and eVisitor are counted separately; the same report puts their grant rates at about 99%.</p>
{blocchi_t}
<h2>How to read these figures</h2>
<ul class="testo">
<li><strong>By citizenship.</strong> Home Affairs counts applicants by the country of citizenship (for dual citizens, the citizenship of the travel document or the one nominated in the application).</li>
<li><strong>Refusal rate</strong> = refused ÷ (granted + refused). Applications withdrawn or still being processed are not decisions. Grant rate = 100% − refusal rate.</li>
<li><strong>Primary applicants outside Australia</strong> are students applying from abroad; family members (secondary applicants) and students already in Australia are in the country tables.</li>
<li><strong>Financial years</strong> run from 1 July to 30 June. {AU_YTD and f"The current year ({au_ytd_testo()}) is incomplete." or ""} The file is updated monthly and figures can be revised.</li>
<li>Minimum {intero(SOGLIA_ALTRI)} decisions in {AU_A1} for a nationality to appear in the main table.</li></ul>
<h2>Official sources</h2>
<ul class="fonti">
<li><a href="{escape(F_AUS["url"])}" rel="noopener">{escape(F_AUS["titolo"])}</a> – Department of Home Affairs on <a href="{escape(F_AUS["pagina"])}" rel="noopener">data.gov.au</a>, XLSX, {intero(F_AUS["byte"])} bytes, downloaded on {data_lunga(F_AUS["scaricato_il"])}. Licence: {lic_link(F_AUS)}. Attribution: Australian Government Department of Home Affairs.</li>
<li><a href="{escape(F_AUT["url"])}" rel="noopener">{escape(F_AUT["titolo"])}</a> – Department of Home Affairs, PDF, downloaded on {data_lunga(F_AUT["scaricato_il"])}. Licence: {lic_link(F_AUT)} (<a href="{escape(F_AUT["copyright"])}" rel="noopener">copyright and disclaimer</a>).</li>
<li><a href="{escape(F_AUC["url"])}" rel="noopener">{escape(F_AUC["titolo"])}</a> – Department of Home Affairs on data.gov.au, XLSX, downloaded on {data_lunga(F_AUC["scaricato_il"])}, {lic_link(F_AUC)} (used only to check that each visitor visa rate rests on at least {intero(SOGLIA_ALTRI)} decisions).</li></ul>
<p><a href="../">Schengen visa refusal rates</a> · <a href="../uk/">UK visa refusal rates by nationality</a> · <a href="../new-zealand-visas/">New Zealand</a> · <a href="../canada-visas/">Canada</a> · <a href="{rel}">Visa income calculator</a></p>"""
    ld = {"@context": "https://schema.org", "@type": "Dataset", "name": f"Australia student visa refusal rates by nationality {AU_A1}",
          "description": "Australian student visa (subclass 500) refusal rates by citizenship, financial year, month and education sector, and visitor visa grant rates, recalculated from Department of Home Affairs files.",
          "url": f"{URL_SITO}/{SEZ_AU}", "creator": {"@type": "Organization", "name": NOME, "url": URL_SITO + "/"},
          "isBasedOn": [F_AUS["url"], F_AUT["url"]], "temporalCoverage": f"{AU['anni'][0][:4]}-07/{AU_FINO_AL[-4:]}", "license": F_AUS["licenza_url"]}
    pagina(SEZ_AU, f"Australia visa refusal rate by nationality {AU_A1}: students and visitors",
           f"Official Home Affairs data: Australia refused {pct(rapporto(tot1))} of student visa decisions for applicants outside Australia in {AU_A1}. "
           f"{len(AU_OK)} nationalities (India, Nepal, Pakistan, Bangladesh, Philippines and more), by month and sector, plus visitor visa grant rates.",
           corpo, ordina=True, jsonld_extra=ld, briciole=[("Visa refusal rates", SEZ), ("Australia", SEZ_AU)])


def pagina_rif_nz():
    rel = "../../"
    righe = []
    for n in NZ_OK:
        celle = ""
        for t, _, _ in NZ_TIPI:
            v = nz_v(n, t, NZ_A1)
            celle += f'{cella_quota(v)}<td class="n" data-v="{sum(v)}">{intero(sum(v))}</td>'
        righe.append(f'<tr><td>{link_paese_altri(n, rel, "new-zealand")}</td>{celle}</tr>')
    tot = {t: nz_v(None, t, NZ_A1) for t, _, _ in NZ_TIPI}
    tot0 = {t: nz_v(None, t, NZ_A0) for t, _, _ in NZ_TIPI}
    righe_a = []
    for a in NZ_ANNI:
        celle = ""
        for t, _, _ in NZ_TIPI:
            v = nz_v(None, t, a)
            celle += f'{cella_quota(v)}<td class="n" data-v="{sum(v)}">{intero(sum(v))}</td>'
        et = f"{nz_ytd_testo()} ({a})" if a == NZ_YTD else a
        righe_a.append(f'<tr><td>{escape(et)}</td>{celle}</tr>')
    testa = "".join(f'{th_ord(f"{et} declined", primo="ascending")}{th_ord("Decisions")}' for _, et, _ in NZ_TIPI)
    opzioni = "".join(f'<option value="{rel}{SEZ}{SLUG_RIF[chiave_altri(n)]}/#new-zealand">{escape(nome_altri(n))}</option>'
                      for n in sorted(NZ_OK, key=nome_altri) if chiave_altri(n) in SLUG_RIF)
    vis = [n for n in NZ_OK if sum(nz_v(n, "visitor", NZ_A1)) >= SOGLIA_ALTRI]
    alto = sorted(vis, key=lambda n: -rapporto(nz_v(n, "visitor", NZ_A1)))[:3]
    corpo = f"""<section class="hero">{h1_diviso(f"New Zealand visa decline rate by nationality {NZ_A1}: visitor, student and work visas")}
<p class="lead">How many New Zealand visa applications were declined, nationality by nationality, from Immigration New Zealand's official monthly statistics: visitor, student and work visas side by side, every financial year since {NZ_ANNI[0]}.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{bandiera("New Zealand")}<span>New Zealand temporary visas</span><span style="white-space:nowrap">{NZ_A1}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Visitor visas · all nationalities · {nz_fy(NZ_A1)}</span><span class="sr">: </span><strong>{pct(rapporto(tot["visitor"]))}</strong> declined ({intero(tot["visitor"][1])} of {intero(sum(tot["visitor"]))} applications decided)</p>
<div class="kpi"><div><b>{pct(rapporto(tot["student"]))}</b><span>student visas declined · {intero(sum(tot["student"]))} decisions</span></div><div><b>{pct(rapporto(tot["work"]))}</b><span>work visas declined · {intero(sum(tot["work"]))} decisions</span></div><div><b>{pct(rapporto(tot0["visitor"]))}</b><span>visitor visas declined in {NZ_A0}</span></div><div><b>{len(NZ_OK)}</b><span>nationalities with {intero(SOGLIA_ALTRI)}+ decisions of one type</span></div></div>
<p class="lead" style="margin-top:6px">Highest visitor visa decline rates in {NZ_A1} among nationalities with at least {intero(SOGLIA_ALTRI)} decisions: {", ".join(f"{escape(nome_altri(n))} ({pct(rapporto(nz_v(n, 'visitor', NZ_A1)))})" for n in alto)}.</p>
{fonte_nz_p()}
</div></section>
{avviso_altri("INZ's declined figure also includes withdrawn applications, so it is not the same measure as the UK or Australian refusal rate.")}
{AD}
<section class="card cerca"><form class="vai" action="#" onsubmit="return false"><label for="vai-nz"><span class="lt">{ico("globe")}Your passport</span></label>
<div class="vai-r"><select id="vai-nz" data-vai><option value="">Choose a country…</option>{opzioni}</select></div></form></section>
<h2>New Zealand visa decline rate by nationality ({NZ_A1})</h2>
<p class="small">Applications decided in {NZ_A1} ({nz_fy(NZ_A1)}), nationalities with at least {intero(SOGLIA_ALTRI)} decisions for at least one visa type. Tap a column heading to sort, or type to filter. * Fewer than {intero(SOGLIA_ALTRI)} decisions; – fewer than {SOGLIA_POCO}.</p>
<p class="filtro"><label><span class="sr">Filter nationalities</span><input type="search" placeholder="Filter: e.g. India" data-filtro="t-nz" autocomplete="off"></label></p>
<div class="tab compatta"><table class="ord larga" id="t-nz"><thead><tr>{th_ord("Nationality", False, "ascending")}{testa}</tr></thead><tbody>{"".join(righe)}</tbody></table></div>
{fonte_nz_p()}
<h2>Year by year, all nationalities</h2>
<div class="tab compatta"><table class="ord"><thead><tr>{th_ord("Financial year", False, "ascending")}{testa}</tr></thead><tbody>{"".join(righe_a)}</tbody></table></div>
{fonte_nz_p(breve=True)}
<h2>How to read these figures</h2>
<ul class="testo">
<li><strong>By nationality</strong> = the country that issued the passport (INZ definition).</li>
<li><strong>Declined</strong>, for INZ, includes applications that did not meet the criteria <em>and</em> applications withdrawn by the client or replaced by a new one. We divide declined by approved + declined, the applications INZ counts as decided.</li>
<li><strong>Applications, not people:</strong> one application can include several people (INZ also publishes the people counts).</li>
<li>Financial years run from 1 July to 30 June; {NZ_YTD and f"{NZ_YTD} so far covers {nz_ytd_testo()}." or ""} Electronic travel authorities (NZeTA) are not visas and are not counted.</li></ul>
<h2>Official sources</h2>
<ul class="fonti">{"".join(f'<li><a href="{escape(F2[f"nz_{t}"]["url"])}" rel="noopener">{escape(F2[f"nz_{t}"]["titolo"])}</a> – Immigration New Zealand, PDF ({intero(F2[f"nz_{t}"]["byte"])} bytes), prepared {escape(F2[f"nz_{t}"]["preparato"])}, downloaded on {data_lunga(F2[f"nz_{t}"]["scaricato_il"])}. Crown copyright, {lic_link(F2[f"nz_{t}"])}.</li>' for t, _, _ in NZ_TIPI)}
<li><a href="{escape(F2["nz_visitor"]["pagina"])}" rel="noopener">Immigration statistics</a> and <a href="{escape(F2["nz_visitor"]["copyright"])}" rel="noopener">copyright notice</a> – Immigration New Zealand.</li></ul>
<p><a href="../">Schengen visa refusal rates</a> · <a href="../uk/">UK</a> · <a href="../australia-visas/">Australia</a> · <a href="../canada-visas/">Canada</a> · <a href="{rel}">Visa income calculator</a></p>"""
    ld = {"@context": "https://schema.org", "@type": "Dataset", "name": f"New Zealand visa decline rates by nationality {NZ_A1}",
          "description": "Visitor, student and work visa applications approved and declined by nationality and financial year, from Immigration New Zealand statistics.",
          "url": f"{URL_SITO}/{SEZ_NZ}", "creator": {"@type": "Organization", "name": NOME, "url": URL_SITO + "/"},
          "isBasedOn": [F2[f"nz_{t}"]["url"] for t, _, _ in NZ_TIPI], "temporalCoverage": f"{NZ_ANNI[0][:4]}-07/{NZ_INFO['periodo'][1][-4:]}",
          "license": F2["nz_visitor"]["licenza_url"]}
    pagina(SEZ_NZ, f"New Zealand visa decline rate by nationality {NZ_A1}: visitor, study, work",
           f"Immigration New Zealand data: {pct(rapporto(tot['visitor']))} of visitor visa applications were declined in {NZ_A1}. "
           f"Visitor, student and work visa decline rates for {len(NZ_OK)} nationalities, year by year since {NZ_ANNI[0]}.",
           corpo, ordina=True, jsonld_extra=ld, briciole=[("Visa refusal rates", SEZ), ("New Zealand", SEZ_NZ)])


def pagina_rif_ca():
    rel = "../../"
    righe = []
    for n in CA_OK:
        ap, es, q = ca_quota(n, CA_A1)
        ap0, es0, q0 = ca_quota(n, CA_A0)
        apy, esy, qy = ca_quota(n, CA_YTD) if CA_YTD else (0, 0, None)
        sp, trv = ca_somma("sp_processed", n, CA_A1)[0], ca_somma("trv_approved", n, CA_A1)[0]
        righe.append(f'<tr><td>{link_paese_altri(n, rel, "canada")}</td>{cella_tasso(q)}{cella_tasso(q0) if es0 >= SOGLIA_POCO else cella_tasso(None)}'
                     f'{cella_tasso(qy, esy < SOGLIA_ALTRI) if esy >= SOGLIA_POCO else cella_tasso(None)}<td class="n" data-v="{es}">{intero(es)}</td>'
                     f'{cella_ca("sp_processed", n, CA_A1)}{cella_ca("trv_approved", n, CA_A1)}</tr>')
    ap, es, q = ca_quota("Total", CA_A1)
    ap0, es0, q0 = ca_quota("Total", CA_A0)
    apy, esy, qy = ca_quota("Total", CA_YTD) if CA_YTD else (0, 0, None)
    sp_t, trv_t = ca_somma("sp_processed", "Total", CA_A1)[0], ca_somma("trv_approved", "Total", CA_A1)[0]
    opzioni = "".join(f'<option value="{rel}{SEZ}{SLUG_RIF[chiave_altri(n)]}/#canada">{escape(nome_altri(n))}</option>'
                      for n in sorted(CA_OK, key=nome_altri) if chiave_altri(n) in SLUG_RIF and chiave_altri(n) != "CANADA")
    basso = sorted(CA_OK, key=lambda n: ca_quota(n, CA_A1)[2])[:3]
    corpo = f"""<section class="hero">{h1_diviso(f"Canada visa approval rate by country {CA_A1}: temporary resident applications (IRCC data)")}
<p class="lead">How many temporary resident applications from each country Canada approved, from IRCC's official monthly files: visitor visas, study permits and work permits together, with the number of study permit applications processed and visitor visas approved. Why there is no study permit or visitor visa refusal rate is explained below.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{bandiera("Canada")}<span>Canada temporary residents</span><span>{CA_A1}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">All temporary resident applications · all countries · {CA_A1}</span><span class="sr">: </span><strong>{pct(q)}</strong> approved ({intero(ap)} of {intero(es)} processed)</p>
<div class="kpi"><div><b>{pct(q0)}</b><span>approved in {CA_A0}</span></div><div><b>{pct(qy)}</b><span>January to {CA_ULTIMO_MESE} {CA_YTD} · {intero(esy)} processed</span></div><div><b>{intero(sp_t)}</b><span>new study permit applications processed in {CA_A1}</span></div><div><b>{intero(trv_t)}</b><span>visitor visas approved in {CA_A1}</span></div></div>
<p class="lead" style="margin-top:6px">Lowest approved shares in {CA_A1} among countries with at least {intero(SOGLIA_ALTRI)} applications processed: {", ".join(f"{escape(nome_altri(n))} ({pct(ca_quota(n, CA_A1)[2])})" for n in basso)}.</p>
{fonte_ca_p()}
</div></section>
<p class="avviso"><strong>What this rate is, and what it is not.</strong> IRCC publishes, for each country and month, the temporary resident applications it <em>processed</em> (approved, refused and withdrawn) and those it <em>approved</em>, for visitor visas, visitor records, study permits and work permits together, first applications and extensions. The approved share below is therefore a mixed figure, not a visitor visa or study permit approval rate. For study permits IRCC publishes only the applications processed, and for visitor visas only the visas approved, so a refusal rate for either cannot be calculated from the official files: we show those counts without a rate.</p>
{avviso_altri("The approved share mixes visitor visas, study permits and work permits, so it says little about any one application.")}
{AD}
<section class="card cerca"><form class="vai" action="#" onsubmit="return false"><label for="vai-ca"><span class="lt">{ico("globe")}Your country</span></label>
<div class="vai-r"><select id="vai-ca" data-vai><option value="">Choose a country…</option>{opzioni}</select></div></form></section>
<h2>Canada temporary resident approval rate by country ({CA_A1})</h2>
<p class="small">Countries with at least {intero(SOGLIA_ALTRI)} temporary resident applications processed in {CA_A1}, in persons. Tap a column heading to sort, or type to filter. * Fewer than {intero(SOGLIA_ALTRI)} processed; – fewer than {SOGLIA_POCO}.</p>
<p class="filtro"><label><span class="sr">Filter countries</span><input type="search" placeholder="Filter: e.g. Nigeria" data-filtro="t-ca" autocomplete="off"></label></p>
<div class="tab compatta"><table class="ord larga" id="t-ca"><thead><tr>{th_ord("Country", False, "ascending")}{th_ord(f"Approved {CA_A1}")}{th_ord(CA_A0)}{th_ord(f"Jan–{CA_ULTIMO_MESE[:3]} {CA_YTD}")}{th_ord(f"Processed {CA_A1}")}{th_ord("Study permits processed")}{th_ord("Visitor visas approved")}</tr></thead><tbody>{"".join(righe)}</tbody></table></div>
{fonte_ca_p(("tr_processed", "tr_approved", "sp_processed", "trv_approved"))}
<h2>How to read these figures</h2>
<ul class="testo">
<li><strong>Approved share</strong> = temporary resident applications approved ÷ processed, in persons, for the same countries and months. "Processed" includes approved, refused and withdrawn applications, so 100% minus this share is refused <em>or</em> withdrawn.</li>
<li><strong>Temporary resident applications</strong> include temporary resident (visitor) visas, visitor records, study permits and extensions, and work permits and extensions (IRCC definition in the files).</li>
<li><strong>Country</strong> is IRCC's "source country"; the files do not define it further.</li>
<li><strong>Visitor visas approved</strong> counts V-1 visas only (tourists and family visits, not visas issued to students or workers); "–" means the country is not in that file, usually because its citizens do not need a visitor visa.</li>
<li><strong>Rounding:</strong> counts are rounded to the nearest 5 and counts from 1 to 4 are not published, so small numbers are approximate. Data are operational and can change.</li></ul>
<h2>Official sources</h2>
<ul class="fonti">{"".join(f'<li><a href="{escape(F2[f"ca_{k}"]["url"])}" rel="noopener">{escape(F2[f"ca_{k}"]["titolo"])}</a> – IRCC, XLSX ({intero(F2[f"ca_{k}"]["byte"])} bytes), data as of {escape(F2[f"ca_{k}"]["dati_al"])}, downloaded on {data_lunga(F2[f"ca_{k}"]["scaricato_il"])}.</li>' for k in ("tr_processed", "tr_approved", "sp_processed", "trv_approved"))}
<li><a href="{escape(F2["ca_tr_processed"]["pagina"])}" rel="noopener">Operational Processing – Monthly IRCC Updates</a> – Open Government Portal. Contains information licensed under the {lic_link(F2["ca_tr_processed"])}.</li></ul>
<p><a href="../">Schengen visa refusal rates</a> · <a href="../uk/">UK</a> · <a href="../australia-visas/">Australia</a> · <a href="../new-zealand-visas/">New Zealand</a> · <a href="{rel}">Visa income calculator</a></p>"""
    ld = {"@context": "https://schema.org", "@type": "Dataset", "name": f"Canada temporary resident applications approved by country {CA_A1}",
          "description": "Temporary resident applications processed and approved by IRCC by source country and month, with new study permit applications processed and visitor visas approved.",
          "url": f"{URL_SITO}/{SEZ_CA}", "creator": {"@type": "Organization", "name": NOME, "url": URL_SITO + "/"},
          "isBasedOn": [F2[f"ca_{k}"]["url"] for k in ("tr_processed", "tr_approved", "sp_processed", "trv_approved")],
          "temporalCoverage": f"{CA_MESI[0]}/{CA_MESI[-1]}", "license": F2["ca_tr_processed"]["licenza_url"]}
    pagina(SEZ_CA, f"Canada visa approval rate by country {CA_A1}: temporary residents (IRCC data)",
           f"IRCC data: {pct(q)} of temporary resident applications processed in {CA_A1} were approved. Approval share for {len(CA_OK)} countries, "
           f"study permit applications processed and visitor visas approved, month by month.",
           corpo, ordina=True, jsonld_extra=ld, briciole=[("Visa refusal rates", SEZ), ("Canada", SEZ_CA)])


def schede_destinazioni(rel_sez):
    """Tre schede per la panoramica e la pagina UK."""
    tot_au = au_v(None, AU_A1, PO)
    tot_nz = nz_v(None, "visitor", NZ_A1)
    q_ca = ca_quota("Total", CA_A1)[2]
    return (f'<div class="griglia">'
            f'<a href="{rel_sez}australia-visas/"><span class="ic f">{bandiera("Australia")}</span><span>Australia: student visa refusal rate by nationality<small>{pct(rapporto(tot_au))} refused in {AU_A1} · {len(AU_OK)} nationalities</small></span></a>'
            f'<a href="{rel_sez}new-zealand-visas/"><span class="ic f">{bandiera("New Zealand")}</span><span>New Zealand: visitor, student and work visas<small>{pct(rapporto(tot_nz))} of visitor visas declined in {NZ_A1}</small></span></a>'
            f'<a href="{rel_sez}canada-visas/"><span class="ic f">{bandiera("Canada")}</span><span>Canada: temporary resident approval rate by country<small>{pct(q_ca)} approved in {CA_A1}</small></span></a></div>')


def controlli_altri():
    errori = []
    if len(AU_OK) < 30:
        errori.append(f"altri: solo {len(AU_OK)} nazionalità australiane con {SOGLIA_ALTRI}+ decisioni")
    if len(NZ_OK) < 30 or len(CA_OK) < 50:
        errori.append(f"altri: poche nazionalità (NZ {len(NZ_OK)}, Canada {len(CA_OK)})")
    for k, f in F2.items():
        if not f.get("url", "").startswith("https://") or not f.get("scaricato_il"):
            errori.append(f"altri: fonte {k} senza URL o data")
        if not f.get("licenza_url", "").startswith("https://"):
            errori.append(f"altri: fonte {k} senza licenza")
    # ogni nome dei file deve finire su una chiave nota o essere escluso, se ha una pagina o supera la soglia
    noti = set(DEMONIMI) | {r[1] for r in UE[A1]}
    for fonte, nomi in (("AU", AU_OK), ("NZ", NZ_OK), ("CA", CA_OK)):
        ignoti = [n for n in nomi if chiave_altri(n) not in noti and n not in NON_NAZIONALITA]
        if len(ignoti) > 12:
            errori.append(f"altri: {fonte} nomi senza corrispondenza: {ignoti[:12]}")
    for s in ("australia-visas", "new-zealand-visas", "canada-visas"):
        if s in SLUG_RIF.values():
            errori.append(f"altri: slug {s} già usato da una pagina Paese")
    return errori


# ---------------------------------------------------------------- "Who moved where" (28/10/2026): quanti [cittadini] si sono trasferiti in [Paese]
# Dati: dati/trasferimenti.json, scritto da raccolta/trasferimenti.py: Eurostat migr_resfirst (primi permessi di soggiorno, UE-27 + EFTA),
# IRCC (nuovi residenti permanenti in Canada), Home Office (visti di lavoro, studio e famiglia concessi dal Regno Unito).
# Ogni misura è diversa e lo dice la pagina: i tre numeri non si sommano mai tra loro.
TRA = json.loads((DATI / "trasferimenti.json").read_text(encoding="utf-8"))
SEZ_TR = "moved-to/"
SOGLIA_TR = 500   # minimo nell'ultimo anno (permessi, residenti permanenti o visti concessi) per una pagina nazionalità × Paese
ANNI_TR = TRA["anni"]
Y1, Y0 = ANNI_TR[-1], ANNI_TR[-2]   # anno più recente (2025) e anno prima
F_ES, F_PR, F_UKV = TRA["fonti"]["eurostat"], TRA["fonti"]["canada"], TRA["fonti"]["uk"]
EUD, EUN = TRA["eurostat"]["dati"], TRA["eurostat"]["note"]
NOMI_GEO = TRA["eurostat"]["nomi_destinazioni"]
GEO_EFTA = ["IS", "LI", "NO", "CH"]
GEO_UE = [g for g in NOMI_GEO if g != "EU27_2020" and g not in GEO_EFTA]
MOTIVI_TR = [(1, "Family"), (2, "Education"), (3, "Work"), (4, "Other")]   # indici nelle righe Eurostat
PRIMO_ANNO_UK = "2021"   # i britannici erano cittadini UE fino al 31/12/2020: per loro i permessi si contano dal 2021
SEGNI_TR = {"u": "low reliability", "b": "break in time series", "p": "provisional", "e": "estimated"}

# codice Eurostat -> (slug, persone al plurale, cittadini, Paese con l'articolo, chiave delle pagine dei visti rifiutati o None, parola delle ricerche)
NAZ_TR = {
    "US": ("americans", "Americans", "US citizens", "the United States", None, "Americans"),
    "UK": ("british", "British people", "British citizens", "the United Kingdom", None, "Brits"),
    "CA": ("canadians", "Canadians", "Canadian citizens", "Canada", None, "Canadians"),
    "AU": ("australians", "Australians", "Australian citizens", "Australia", None, "Australians"),
    "IN": ("indians", "Indians", "Indian citizens", "India", "INDIA", "Indians"),
    "PK": ("pakistanis", "Pakistanis", "Pakistani citizens", "Pakistan", "PAKISTAN", "Pakistanis"),
    "NG": ("nigerians", "Nigerians", "Nigerian citizens", "Nigeria", "NIGERIA", "Nigerians"),
    "PH": ("filipinos", "Filipinos", "Filipino citizens", "the Philippines", "PHILIPPINES", "Filipinos"),
    "CN": ("chinese", "Chinese citizens", "Chinese citizens", "China", "CHINA", "Chinese people"),
    "BR": ("brazilians", "Brazilians", "Brazilian citizens", "Brazil", None, "Brazilians"),
    "ZA": ("south-africans", "South Africans", "South African citizens", "South Africa", "SOUTH AFRICA", "South Africans"),
    "NZ": ("new-zealanders", "New Zealanders", "New Zealand citizens", "New Zealand", None, "New Zealanders"),
}
# nomi Eurostat -> nomi usati per bandiere e pagine Schengen (file della Commissione)
_GEO_SITO = {"Czechia": "Czech Republic"}

# destinazioni: slug -> (tipo, codice Eurostat, nome nelle tabelle, nome nelle frasi)
DEST_TR = {slug_testo(NOMI_GEO[g]): ("eu", g, NOMI_GEO[g], art(NOMI_GEO[g])) for g in GEO_UE + GEO_EFTA}
DEST_TR["canada"] = ("ca", None, "Canada", "Canada")
DEST_TR["uk"] = ("uk", None, "United Kingdom", "the UK")


def riga_eu(c, g, a):
    return EUD.get(c, {}).get(g, {}).get(a)


def segni_eu(c, g, a):
    return EUN.get(c, {}).get(g, {}).get(a, {})


def anni_naz(c):
    return [a for a in ANNI_TR if c != "UK" or a >= PRIMO_ANNO_UK]


def val_tr(c, d, a):
    """Numero principale della coppia (cittadinanza c, destinazione d) nell'anno a, o None."""
    tipo, g, _, _ = DEST_TR[d]
    if tipo == "eu":
        r = riga_eu(c, g, a)
        return r[0] if r else None
    if tipo == "ca":
        x = TRA["canada"]["cittadinanze"].get(c)
        return x["anni"].get(a) if x else None
    x = TRA["uk"]["cittadinanze"].get(c)
    v = x["anni"].get(a) if x else None
    return sum(v) if v else None


COPPIE_TR = {c: sorted([d for d in DEST_TR if (val_tr(c, d, Y1) or 0) >= SOGLIA_TR], key=lambda d: -val_tr(c, d, Y1)) for c in NAZ_TR}


def variazione(a, b):
    if a is None or not b:
        return "–"
    if a == b:
        return "0.0%"
    x = (a - b) / b * 100
    dec = 2 if abs(x) < 0.05 else 1   # 44,426 -> 44,446 = +0.05%, non "+0.0%"
    return f"{'+' if x > 0 else '−'}{abs(x):.{dec}f}%"


def frase_cambio(a, b, anno0):
    if b is None:
        return f"There is no {anno0} figure to compare."
    if a == b:
        return f"That is the same number as in {anno0}."
    return f"That is {intero(abs(a - b))} {'more' if a > b else 'fewer'} than in {anno0} ({intero(b)}), a change of {variazione(a, b)}."


def segno_html(s, i):
    """Segno Eurostat accanto al numero (u = poco affidabile, b = interruzione della serie)."""
    x = s.get(str(i))
    return f'<sup title="{escape(SEGNI_TR.get(x, x))}">{escape(x)}</sup>' if x else ""


def cella_n(v, mark=""):
    if v is None:
        return '<td class="n" data-v="">–</td>'
    return f'<td class="n" data-v="{v}">{intero(v)}{mark}</td>'


def cella_var(a, b):
    if a is None or not b:
        return '<td class="n" data-v="">–</td>'
    return f'<td class="n" data-v="{(a - b) / b:.6f}">{variazione(a, b)}</td>'


def data_rfc(s):
    """'Wed, 21 Oct 2026 12:13:53 GMT' -> '21 October 2026'."""
    from email.utils import parsedate_to_datetime
    try:
        return data_lunga(parsedate_to_datetime(s).date().isoformat())
    except (TypeError, ValueError):
        return ""


def mese_testo(ym):
    return f"{MESI[int(ym[5:]) - 1]} {ym[:4]}"


def fonte_es_p(extra=""):
    return (f'<p class="fonte">Source: <a href="{escape(F_ES["pagina"])}" rel="noopener">Eurostat, {escape(F_ES["titolo"])}</a>, '
            f'data updated on {data_lunga(F_ES["aggiornato_il"])}, downloaded on {data_lunga(F_ES["scaricato_il"])} '
            f'(<a href="{escape(F_ES["metadati"])}" rel="noopener">definitions</a>). First residence permits, persons. {extra}'
            f'Re-use: <a href="{escape(F_ES["licenza_url"])}" rel="license noopener">Eurostat copyright notice</a> (free re-use with acknowledgement, CC BY 4.0).</p>')


def fonte_pr_p():
    return (f'<p class="fonte">Source: <a href="{escape(F_PR["pagina"])}" rel="noopener">IRCC, {escape(F_PR["titolo"])}</a> '
            f'(<a href="{escape(F_PR["url"])}" rel="noopener">CSV</a>, updated on {data_rfc(F_PR["ultima_modifica"])}, data to {mese_testo(F_PR["ultimo_mese"])}, '
            f'downloaded on {data_lunga(F_PR["scaricato_il"])}). IRCC rounds each monthly count to the nearest multiple of 5; yearly figures are our sum of the months. '
            f'Contains information licensed under the <a href="{escape(F_PR["licenza_url"])}" rel="license noopener">{escape(F_PR["licenza"])}</a>.</p>')


def fonte_ukv_p():
    return (f'<p class="fonte">Source: <a href="{escape(F_UKV["url"])}" rel="noopener">Home Office, {escape(F_UKV["titolo"])}</a> '
            f'(XLSX, published {escape(F_UKV["pubblicato"])}, downloaded on {data_lunga(F_UKV["scaricato_il"])}; next update {escape(F_UKV["prossimo"])}). '
            f'Entry clearance visas granted, by nationality and year of decision. Figures from 2026 are provisional. '
            f'Contains public sector information licensed under the <a href="{escape(F_UKV["licenza_url"])}" rel="license noopener">{escape(F_UKV["licenza"])}</a>.</p>')


def ytd_ca():
    a = F_PR["anno_in_corso"]
    return (a, f"January–{MESI[int(F_PR['ultimo_mese'][5:]) - 1]} {a}") if a else (None, "")


def ytd_uk():
    a = F_UKV["anno_in_corso"]
    if not a:
        return None, ""
    fine = {"Q1": "March", "Q2": "June", "Q3": "September"}[F_UKV["ultimo_trimestre"].split()[1]]
    return a, f"January–{fine} {a}"


def cosa_eu(c, nome_d, hub=False):
    _, X, cit, _, _, _ = NAZ_TR[c]
    dove = "an EU country" if hub else nome_d
    return (f'<section class="card cosa" aria-labelledby="cosa-h"><h2 id="cosa-h">What this number is, and what it is not</h2><ul class="testo">'
            f'<li><strong>It is</strong> the number of {cit} who received a residence permit in {dove} for the first time in {Y1}: a permit valid for at least 3 months, '
            f'for family, education, work or other reasons. A permit also counts as "first" when the person had none for the same reason in the 6 months before.</li>'
            f'<li><strong>It is not</strong> a count of moves: some people who receive a permit never move, or leave soon after'
            + (', and someone who received permits in two countries is counted in both' if hub else '') + '.</li>'
            f'<li><strong>It leaves out</strong> {X} who also hold an EU passport (the statistics cover non-EU citizens only), stays shorter than 3 months and renewed permits.</li>'
            f'<li><strong>It is not</strong> the number of {X} living in {dove}, which is much larger.</li></ul></section>')


def cosa_ca(c):
    _, X, cit, _, _, _ = NAZ_TR[c]
    return (f'<section class="card cosa" aria-labelledby="cosa-h"><h2 id="cosa-h">What this number is, and what it is not</h2><ul class="testo">'
            f'<li><strong>It is</strong> the number of {cit} who became permanent residents of Canada in {Y1}, by citizenship, from IRCC\'s monthly open data.</li>'
            f'<li><strong>It is not</strong> the number who arrived in {Y1}: many new permanent residents already lived in Canada on a work or study permit, '
            f'and people who arrived on a temporary work or study permit are not counted until they become permanent residents.</li>'
            f'<li><strong>It is not</strong> the number of {X} living in Canada, which is much larger.</li>'
            f'<li>IRCC rounds each monthly count to the nearest multiple of 5 and shows counts between 0 and 5 as "--", so our yearly sums can differ slightly from IRCC\'s own yearly totals.</li></ul></section>')


def cosa_uk(c):
    _, X, cit, _, _, _ = NAZ_TR[c]
    return (f'<section class="card cosa" aria-labelledby="cosa-h"><h2 id="cosa-h">What this number is, and what it is not</h2><ul class="testo">'
            f'<li><strong>It is</strong> the number of work, study and family visas the UK granted to {cit} in {Y1}, applied for outside the UK, '
            f'including partners and children who came with a worker or student.</li>'
            f'<li><strong>It is not</strong> a count of moves: some people with a visa never travel, and study visas include short courses.</li>'
            f'<li><strong>It leaves out</strong> visitor visas, people who switched to another visa from inside the UK, and people who are also British or Irish citizens (they do not need a visa).</li>'
            f'<li><strong>It is not</strong> the number of {X} living in the UK, which is much larger.</li></ul></section>')


def ld_dataset(nome, descr, percorso, fonti, periodo, licenza):
    return {"@context": "https://schema.org", "@type": "Dataset", "name": nome, "description": descr, "url": f"{URL_SITO}/{percorso}",
            "creator": {"@type": "Organization", "name": NOME, "url": URL_SITO + "/"}, "isBasedOn": fonti, "temporalCoverage": periodo,
            "license": licenza}


def ld_faq(domande):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in domande]}


def faq_html(domande):
    return "".join(f'<h3>{escape(q)}</h3><p>{a}</p>' for q, a in domande)


def titolo_tr(X, dove, anno):
    varianti = [f"How many {X} moved to {dove} in {anno}? Official figures", f"How many {X} moved to {dove} in {anno}? Official data",
                f"How many {X} moved to {dove} in {anno}?"]
    return next((v for v in varianti if len(v) <= 70), varianti[-1])


def link_sito_dest(d, rel):
    """Pagine del sito sullo stesso Paese di destinazione: soglie di reddito dei visti, visti rifiutati."""
    tipo, g, nt, _ = DEST_TR[d]
    voci = []
    nome_sito = "United Kingdom" if d == "uk" else nt
    slug_sito = next((s for s, n in PAESI.items() if n == nome_sito), None)
    if slug_sito:
        voci.append((f"{rel}country/{slug_sito}/", f"{nome_sito} visa income requirements {ANNO}"))
        voci += [(f"{rel}{P['slug']}/", f"{nome_prog(P)}: income requirement") for P in PROG if P["paese_slug"] == slug_sito]
    nb = _GEO_SITO.get(nt, nt)
    if nb in SLUG_STATO:
        voci.append((f"{rel}{SEZ}schengen/{SLUG_STATO[nb]}/", f"{nb} Schengen visa rejection rate {A1}"))
    if d == "canada":
        voci.append((f"{rel}{SEZ_CA}", f"Canada visa approval rate by country {CA_A1}"))
    if d == "uk":
        voci += [(f"{rel}{SEZ}uk/", "UK visa refusal rate by nationality"), (f"{rel}{SEZ}uk/family-visas/", "UK spouse and family visa refusal rate by nationality")]
    return voci


def link_sito_naz(c, rel):
    k = NAZ_TR[c][4]
    if k and k in SLUG_RIF:
        return [(f"{rel}{SEZ}{SLUG_RIF[k]}/", f"Visa refusal rates for {art(nome_paese(k))}: Schengen, UK and more")]
    return []


def lista_link(voci):
    return '<ul class="testo">' + "".join(f'<li><a href="{h}">{escape(t)}</a></li>' for h, t in voci) + "</ul>"


def icona_dest(d):
    _, _, nt, _ = DEST_TR[d]
    fl = bandiera(_GEO_SITO.get(nt, nt))
    return f'<span class="ic f">{fl}</span>' if '<svg class="flag"' in fl else f'<span class="ic">{ico("globe")}</span>'


def scheda_coppia(c, d, rel_sez, chi=False):
    """Scheda della griglia verso la pagina c × d. chi=True: titolo con la nazionalità (per le pagine della stessa destinazione)."""
    slug, X = NAZ_TR[c][0], NAZ_TR[c][1]
    tipo, _, nt, nf = DEST_TR[d]
    misura = {"eu": "first permits", "ca": "new permanent residents", "uk": "visas granted"}[tipo]
    testo = X if chi else nt
    icona = f'<span class="ic">{ico("passport")}</span>' if chi else icona_dest(d)
    return (f'<a href="{rel_sez}{slug}/{d}/">{icona}<span>{escape(testo)}'
            f'<small>{intero(val_tr(c, d, Y1))} {misura} in {Y1}</small></span></a>')


def nome_motivo(n):
    """Nome del motivo dentro una frase: "Other" da solo non si legge ("the most common reason was other")."""
    return "other reasons" if n == "Other" else n.lower()


def motivi_frase(r):
    voci = sorted([(r[i], nome) for i, nome in MOTIVI_TR if r[i] is not None], key=lambda x: -x[0])
    if not voci or not r[0]:
        return ""
    return "By reason: " + ", ".join(f"{nome_motivo(n)} {intero(v)} ({v / r[0] * 100:.1f}%)" for v, n in voci) + "."


def anni_testo(xs):
    """['2019', '2021', '2022', '2023'] -> '2019 and 2021–2023' (solo gli anni consecutivi diventano un intervallo)."""
    gruppi = []
    for a in sorted(xs, key=int):
        if gruppi and int(a) == int(gruppi[-1][-1]) + 1:
            gruppi[-1].append(a)
        else:
            gruppi.append([a])
    parti = [g[0] if len(g) == 1 else (f"{g[0]} and {g[1]}" if len(g) == 2 else f"{g[0]}–{g[-1]}") for g in gruppi]
    return parti[0] if len(parti) == 1 else ", ".join(parti[:-1]) + " and " + parti[-1]


def nota_segni(c, g, anni):
    """Frase sui segni Eurostat della casella (Paese g, cittadinanza c), solo se ci sono."""
    u = [a for a in anni if "u" in segni_eu(c, g, a).values()]
    b = [a for a in anni if segni_eu(c, g, a).get("0") == "b"]
    out = []
    if b:
        out.append(f"Eurostat marks a break in the time series in {anni_testo(b)} (b): figures before and after are not fully comparable.")
    if u:
        out.append(f"Eurostat marks the figures for {anni_testo(u)} as having low reliability (u).")
    return " ".join(out)


# ---------- pagina nazionalità × Paese (Eurostat)
def pagina_tr_eu(c, d):
    slug, X, cit, _, _, parola = NAZ_TR[c]
    _, g, nt, nf = DEST_TR[d]
    rel = "../../../"
    percorso = f"{SEZ_TR}{slug}/{d}/"
    r1, r0 = riga_eu(c, g, Y1), riga_eu(c, g, Y0)
    t1, t0 = r1[0], (r0[0] if r0 else None)
    s1 = segni_eu(c, g, Y1)
    ue1 = riga_eu(c, "EU27_2020", Y1)
    in_ue = g in GEO_UE
    rank = sorted([x for x in GEO_UE if riga_eu(c, x, Y1) and riga_eu(c, x, Y1)[0] is not None], key=lambda x: -riga_eu(c, x, Y1)[0])
    pos = (rank.index(g) + 1) if in_ue else None
    quota = t1 / ue1[0] * 100 if in_ue and ue1 and ue1[0] else None
    lungo = r1[7]
    rottura = s1.get("0") == "b"
    frase_rottura = (f' Eurostat marks a break in the time series for {nf} in {Y1}, so part of the change may come from a change in how the permits are counted.' if rottura else "")
    poco = ' Eurostat marks this figure as having low reliability.' if s1.get("0") == "u" else ""
    risposta = (f'{nf[0].upper() + nf[1:]} issued <strong>{intero(t1)}</strong> first residence permits to {cit} in {Y1}, the main official indicator of how many moved there '
                f'(Eurostat, data updated on {data_lunga(F_ES["aggiornato_il"])}).')
    righe_m = []
    for i, nome in MOTIVI_TR:
        a, b = r1[i], (r0[i] if r0 else None)
        righe_m.append(f'<tr><td>{nome}</td>{cella_n(a, segno_html(s1, i))}<td class="n">{f"{a / t1 * 100:.1f}%" if a is not None and t1 else "–"}</td>'
                       f'{cella_n(b)}{cella_var(a, b)}</tr>')
    righe_m.append(f'<tr class="tot-r"><td>All reasons</td>{cella_n(t1, segno_html(s1, 0))}<td class="n">100%</td>{cella_n(t0)}{cella_var(t1, t0)}</tr>')
    anni = anni_naz(c)
    righe_s = []
    for a in anni:
        r = riga_eu(c, g, a)
        s = segni_eu(c, g, a)
        if not r:
            righe_s.append(f'<tr><td>{a}</td>' + '<td class="n">–</td>' * 6 + '</tr>')
            continue
        righe_s.append(f'<tr><td>{a}</td>{cella_n(r[0], segno_html(s, 0))}' + "".join(cella_n(r[i], segno_html(s, i)) for i, _ in MOTIVI_TR)
                       + f'{cella_n(r[7], segno_html(s, 7))}</tr>')
    nota = nota_segni(c, g, anni)
    nota_uk = (f" British citizens were EU citizens until the end of 2020 and did not need residence permits, so the series starts in {PRIMO_ANNO_UK}; "
               f"{PRIMO_ANNO_UK}, the first year after Brexit, may not be comparable with later years." if c == "UK" else "")
    principale = max(((r1[i], nome) for i, nome in MOTIVI_TR if r1[i] is not None), default=(None, ""))
    altre = [x for x in COPPIE_TR[c] if x != d][:8]
    stesse = [x for x in sorted(NAZ_TR, key=lambda x: -(val_tr(x, d, Y1) or 0)) if x != c and d in COPPIE_TR[x]][:8]
    domande = [
        (f"How many {parola} moved to {nf} in {Y1}?",
         f"{intero(t1)} {cit} received a first residence permit in {nf} in {Y1} (Eurostat). {frase_cambio(t1, t0, Y0)}"),
        (f"How many {parola} moved to {nf} in {Y0}?",
         (f"{intero(t0)} {cit} received a first residence permit in {nf} in {Y0}." if t0 is not None else f"Eurostat has no {Y0} figure for {cit} in {nf}.")),
        (f"Why do {parola} move to {nf}?",
         ((f"The largest group in {Y1} was other reasons ({intero(principale[0])} permits), Eurostat's category for permits not given for family, education or work. "
           if principale[1] == "Other" else f"The most common reason in {Y1} was {principale[1].lower()} ({intero(principale[0])} permits). ") if principale[0] else "")
         + motivi_frase(r1)),
    ]
    if in_ue and ue1:
        domande.append((f"How many {parola} moved to Europe in {Y1}?",
                        f'The 27 EU countries issued {intero(ue1[0])} first residence permits to {cit} in {Y1}; {nf} issued {quota:.1f}% of them. '
                        f'<a href="../">All countries</a>.'))
    domande.append((f"Is this the number of {X} living in {nf}?",
                    f"No. It counts only new permits issued in {Y1}. People who have lived there for years, renewed their permits or have an EU passport are not included."))
    kpi = [(intero(t0) if t0 is not None else "–", f"in {Y0}"), (variazione(t1, t0), f"change on {Y0}")]
    kpi.append((intero(lungo) if lungo is not None else "–", "valid for 12 months or more"))
    kpi.append((f"{pos} of {len(rank)}" if pos else "EFTA", f"rank among EU countries for {X}" if pos else "not in the EU total (Iceland, Liechtenstein, Norway, Switzerland)"))
    descr_lungo = (f" {intero(lungo)} of them ({lungo / t1 * 100:.1f}%) were valid for 12 months or more." if lungo is not None and t1 else "")
    corpo = f"""<section class="hero"><h1>How many {escape(X)} moved to {escape(nf)} in {Y1}?</h1>
<p class="lead">{risposta} {frase_cambio(t1, t0, Y0)}{frase_rottura}{poco} {motivi_frase(r1)}{descr_lungo}</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("globe")}<span>First residence permits</span><span>{escape(cit)} · {Y1}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">{escape(nt)} · {escape(cit)} · {Y1}</span><span class="sr">: </span><strong>{intero(t1)}</strong> first residence permits{segno_html(s1, 0)}</p>
<div class="kpi">{"".join(f'<div><b>{v}</b><span>{escape(e)}</span></div>' for v, e in kpi)}</div>
{f'<p class="lead" style="margin-top:6px">{nf[0].upper() + nf[1:]} issued {quota:.1f}% of all first permits given to {cit} in the EU in {Y1} ({intero(ue1[0])}). <a href="../">Every EU country</a>.</p>' if quota is not None else ''}
{fonte_es_p()}
</div></section>
{cosa_eu(c, nf)}
{AD}
<h2>Why {escape(X)} moved to {escape(nf)} in {Y1}: permits by reason</h2>
<div class="tab compatta motivi"><table><caption class="sr">First residence permits issued by {escape(nt)} to {escape(cit)}, by reason, {Y1} and {Y0}</caption><thead><tr><th scope="col">Reason</th><th class="n" scope="col">{Y1}</th><th class="n" scope="col">Share</th><th class="n" scope="col">{Y0}</th><th class="n" scope="col">Change</th></tr></thead><tbody>{"".join(righe_m)}</tbody></table></div>
{fonte_es_p()}
<p class="small"><strong>Family:</strong> joining or accompanying a family member. <strong>Education:</strong> study and other education. <strong>Work:</strong> paid employment (Eurostat's "employment reasons", also called remunerated activities), for example EU Blue Cards, other skilled work and seasonal work. <strong>Other:</strong> international protection and humanitarian status, permits for residence only, and other or unspecified reasons.</p>
<h2>{escape(X)} moving to {escape(nf)}, year by year ({anni[0]}–{Y1})</h2>
<div class="tab compatta"><table><caption class="sr">First residence permits issued by {escape(nt)} to {escape(cit)}, {anni[0]}–{Y1}</caption><thead><tr><th scope="col">Year</th><th class="n" scope="col">All reasons</th><th class="n" scope="col">Family</th><th class="n" scope="col">Education</th><th class="n" scope="col">Work</th><th class="n" scope="col">Other</th><th class="n" scope="col">Valid 12+ months</th></tr></thead><tbody>{"".join(righe_s)}</tbody></table></div>
{fonte_es_p("Eurostat revises past years when countries correct their data. ")}
{f'<p class="small">{nota}{nota_uk}</p>' if nota or nota_uk else ''}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>Visas and statistics for {escape(nf)} on this site</h2>
{lista_link(link_sito_dest(d, rel) + link_sito_naz(c, rel)) if link_sito_dest(d, rel) + link_sito_naz(c, rel) else ''}
{f'<h2>Where else {escape(X)} moved in {Y1}</h2><div class="griglia">{"".join(scheda_coppia(c, x, "../../") for x in altre)}</div>' if altre else ''}
{f'<h2>Who else moved to {escape(nf)} in {Y1}</h2><div class="griglia">{"".join(scheda_coppia(x, d, "../../", chi=True) for x in stesse)}</div>' if stesse else ''}
<p><a href="../">How many {escape(X)} moved to Europe in {Y1}</a> · <a href="../../">Who moved where: all nationalities</a> · <a href="{rel}">Visa income calculator</a></p>"""
    titolo = titolo_tr(X, nf, Y1)
    descr = (f"{intero(t1)} {cit} got a first residence permit in {nf} in {Y1} ({variazione(t1, t0)} on {Y0}). "
             + motivi_frase(r1) + f" Eurostat data updated {data_lunga(F_ES['aggiornato_il'])}.")
    ld = ld_dataset(f"First residence permits issued by {nt} to {cit}, {anni[0]}-{Y1}", f"Eurostat first residence permits by reason for {cit} in {nt}.",
                    percorso, [F_ES["pagina"]], f"{anni[0]}/{Y1}", "https://creativecommons.org/licenses/by/4.0/")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande), ld],
           briciole=[("Who moved where", SEZ_TR), (X, f"{SEZ_TR}{slug}/"), (nt, percorso)])


# ---------- pagina nazionalità × Canada (IRCC)
def pagina_tr_ca(c, d="canada"):
    slug, X, cit, _, _, parola = NAZ_TR[c]
    rel = "../../../"
    percorso = f"{SEZ_TR}{slug}/{d}/"
    dati = TRA["canada"]["cittadinanze"][c]
    t1, t0 = dati["anni"][Y1], dati["anni"].get(Y0)
    a_ytd, testo_ytd = ytd_ca()
    v_ytd = dati["anni"].get(a_ytd) if a_ytd else None
    righe = [f'<tr><td>{a}</td>{cella_n(dati["anni"].get(a))}{cella_var(dati["anni"].get(a), dati["anni"].get(str(int(a) - 1)))}</tr>' for a in ANNI_TR]
    if a_ytd:
        righe.append(f'<tr class="poco"><td>{testo_ytd}</td>{cella_n(v_ytd)}<td class="n">–</td></tr>')
    nome_ircc = dati["nome"]
    domande = [
        (f"How many {parola} moved to Canada in {Y1}?",
         f"{intero(t1)} {cit} became permanent residents of Canada in {Y1}, according to IRCC. {frase_cambio(t1, t0, Y0)}"),
        (f"How many {parola} moved to Canada in {Y0}?", f"{intero(t0)} {cit} became permanent residents of Canada in {Y0} (IRCC)." if t0 is not None else "No figure."),
        (f"How many {parola} have moved to Canada in {a_ytd}?" if a_ytd else "Is there a figure for this year?",
         (f"{intero(v_ytd)} {cit} became permanent residents of Canada from January to {MESI[int(F_PR['ultimo_mese'][5:]) - 1]} {a_ytd}, the latest month in IRCC's file. Monthly data are provisional and can change." if a_ytd else "Not yet.")),
        (f"Does this count all {parola} who moved to Canada?",
         "No. It counts new permanent residents only. People who arrived on a temporary work or study permit are not counted until they become permanent residents, "
         "and many new permanent residents were already living in Canada."),
    ]
    corpo = f"""<section class="hero"><h1>How many {escape(X)} moved to Canada in {Y1}?</h1>
<p class="lead"><strong>{intero(t1)}</strong> {escape(cit)} became permanent residents of Canada in {Y1}, according to IRCC's monthly figures (file updated on {data_rfc(F_PR["ultima_modifica"])}). {frase_cambio(t1, t0, Y0)}{f' From {testo_ytd.replace("–", " to ")}: {intero(v_ytd)}.' if a_ytd else ''}</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{bandiera("Canada")}<span>New permanent residents</span><span>{escape(cit)} · {Y1}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Canada · {escape(cit)} · {Y1}</span><span class="sr">: </span><strong>{intero(t1)}</strong> new permanent residents</p>
<div class="kpi"><div><b>{intero(t0) if t0 is not None else '–'}</b><span>in {Y0}</span></div><div><b>{variazione(t1, t0)}</b><span>change on {Y0}</span></div><div><b>{intero(v_ytd) if v_ytd is not None else '–'}</b><span>{testo_ytd or 'this year'}</span></div><div><b>{intero(TRA["canada"]["totale"][Y1])}</b><span>new permanent residents of all citizenships in {Y1}</span></div></div>
{fonte_pr_p()}
</div></section>
{cosa_ca(c)}
{AD}
<h2>{escape(X)} becoming permanent residents of Canada, year by year</h2>
<div class="tab compatta"><table><caption class="sr">New permanent residents of Canada, citizens of {escape(NAZ_TR[c][3])}, by year</caption><thead><tr><th scope="col">Year</th><th class="n" scope="col">New permanent residents</th><th class="n" scope="col">Change</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>
{fonte_pr_p()}
<p class="small">IRCC category: "{escape(nome_ircc)}". {f'In {", ".join(dati["mesi_nascosti"])} some months had between 0 and 5 people and are not published ("--" in the file).' if dati["mesi_nascosti"] else ''} This IRCC file does not say why people became permanent residents (work, family, refugee), so there is no breakdown by reason here.</p>
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>Visas and statistics for Canada on this site</h2>
{lista_link(link_sito_dest(d, rel) + link_sito_naz(c, rel))}
<h2>Where else {escape(X)} moved in {Y1}</h2><div class="griglia">{"".join(scheda_coppia(c, x, "../../") for x in [y for y in COPPIE_TR[c] if y != d][:8])}</div>
<p><a href="../">How many {escape(X)} moved abroad in {Y1}</a> · <a href="../../">Who moved where: all nationalities</a> · <a href="{rel}">Visa income calculator</a></p>"""
    ld = ld_dataset(f"New permanent residents of Canada, citizens of {NAZ_TR[c][3]}, {ANNI_TR[0]}-{Y1}", "IRCC monthly permanent residents by country of citizenship, summed by year.",
                    percorso, [F_PR["url"]], f"{ANNI_TR[0]}/{F_PR['ultimo_mese']}", F_PR["licenza_url"])
    pagina(percorso, titolo_tr(X, "Canada", Y1),
           f"{intero(t1)} {cit} became permanent residents of Canada in {Y1} ({variazione(t1, t0)} on {Y0}), IRCC data to {mese_testo(F_PR['ultimo_mese'])}. Year by year since {ANNI_TR[0]}.",
           corpo, jsonld_extra=[ld_faq(domande), ld], briciole=[("Who moved where", SEZ_TR), (X, f"{SEZ_TR}{slug}/"), ("Canada", percorso)])


# ---------- pagina nazionalità × Regno Unito (Home Office)
def pagina_tr_uk(c, d="uk"):
    slug, X, cit, _, _, parola = NAZ_TR[c]
    rel = "../../../"
    percorso = f"{SEZ_TR}{slug}/{d}/"
    dati = TRA["uk"]["cittadinanze"][c]
    gruppi = F_UKV["gruppi"]  # Work, Study, Family
    v1, v0 = dati["anni"][Y1], dati["anni"].get(Y0)
    t1, t0 = sum(v1), (sum(v0) if v0 else None)
    a_ytd, testo_ytd = ytd_uk()
    vy = dati["anni"].get(a_ytd) if a_ytd else None
    nomi = {"Work": "Work", "Study": "Study", "Family": "Family"}
    righe_m = "".join(f'<tr><td>{nomi[g]} visas</td>{cella_n(v1[i])}<td class="n">{v1[i] / t1 * 100:.1f}%</td>{cella_n(v0[i] if v0 else None)}{cella_var(v1[i], v0[i] if v0 else None)}</tr>'
                      for i, g in enumerate(gruppi))
    righe_m += f'<tr class="tot-r"><td>Work, study and family</td>{cella_n(t1)}<td class="n">100%</td>{cella_n(t0)}{cella_var(t1, t0)}</tr>'
    righe_s = "".join(f'<tr><td>{a}</td>{cella_n(sum(dati["anni"][a]))}' + "".join(cella_n(x) for x in dati["anni"][a]) + '</tr>' for a in ANNI_TR)
    if a_ytd:
        righe_s += f'<tr class="poco"><td>{testo_ytd}</td>{cella_n(sum(vy))}' + "".join(cella_n(x) for x in vy) + '</tr>'
    ordine = sorted(zip(v1, gruppi), key=lambda x: -x[0])
    per_tipo = ", ".join(f"{g.lower()} {intero(v)}" for v, g in ordine)
    nk = NAZ_TR[c][4]
    domande = [
        (f"How many {parola} moved to the UK in {Y1}?",
         f"The UK granted {intero(t1)} work, study and family visas to {cit} in {Y1} ({per_tipo}), according to the Home Office. {frase_cambio(t1, t0, Y0)}"),
        (f"How many {parola} moved to the UK in {Y0}?", f"The UK granted {intero(t0)} work, study and family visas to {cit} in {Y0}." if t0 is not None else "No figure."),
        (f"Why do {parola} move to the UK?", f"In {Y1} the most visas granted to {cit} were {ordine[0][1].lower()} visas ({intero(ordine[0][0])}), then {ordine[1][1].lower()} ({intero(ordine[1][0])}) and {ordine[2][1].lower()} ({intero(ordine[2][0])})."),
        (f"Is this the number of {X} living in the UK?", "No. It counts visas granted in one year to people applying from outside the UK, not people already living there."),
    ]
    corpo = f"""<section class="hero"><h1>How many {escape(X)} moved to the UK in {Y1}?</h1>
<p class="lead">The UK granted <strong>{intero(t1)}</strong> work, study and family visas to {escape(cit)} in {Y1}, according to the Home Office (data published {escape(F_UKV["pubblicato"])}). {frase_cambio(t1, t0, Y0)} By type: {per_tipo}.{f' From {testo_ytd.replace("–", " to ")} (provisional): {intero(sum(vy))}.' if a_ytd else ''}</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{bandiera("United Kingdom")}<span>UK visas granted</span><span>{escape(cit)} · {Y1}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">United Kingdom · {escape(cit)} · {Y1}</span><span class="sr">: </span><strong>{intero(t1)}</strong> work, study and family visas granted</p>
<div class="kpi"><div><b>{intero(t0) if t0 is not None else '–'}</b><span>in {Y0}</span></div><div><b>{variazione(t1, t0)}</b><span>change on {Y0}</span></div>{"".join(f'<div><b>{intero(v1[i])}</b><span>{g.lower()} visas</span></div>' for i, g in enumerate(gruppi) if g != "Family")}</div>
{fonte_ukv_p()}
</div></section>
{cosa_uk(c)}
{AD}
<h2>UK visas granted to {escape(cit)} by type ({Y1})</h2>
<div class="tab compatta motivi"><table><caption class="sr">UK work, study and family visas granted to {escape(cit)}, {Y1} and {Y0}</caption><thead><tr><th scope="col">Visa type</th><th class="n" scope="col">{Y1}</th><th class="n" scope="col">Share</th><th class="n" scope="col">{Y0}</th><th class="n" scope="col">Change</th></tr></thead><tbody>{righe_m}</tbody></table></div>
{fonte_ukv_p()}
<p class="small"><strong>Work:</strong> all work routes (Skilled Worker, Health and Care Worker, temporary and seasonal work, Global Business Mobility, talent and business visas) and their dependants. <strong>Study:</strong> sponsored study (Student, Child Student), dependants and short-term study. <strong>Family:</strong> joining a British citizen or a person settled in the UK, and refugee family reunion. Groups as defined by the Home Office.</p>
<h2>UK visas granted to {escape(cit)}, year by year</h2>
<div class="tab compatta"><table><caption class="sr">UK work, study and family visas granted to {escape(cit)} by year</caption><thead><tr><th scope="col">Year</th><th class="n" scope="col">Total</th>{"".join(f'<th class="n" scope="col">{g}</th>' for g in gruppi)}</tr></thead><tbody>{righe_s}</tbody></table></div>
{fonte_ukv_p()}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>Visas and statistics for the UK on this site</h2>
{lista_link(link_sito_dest(d, rel) + ([(f"{rel}{SEZ}{SLUG_RIF[nk]}/#uk", f"UK visa refusal rate for nationals of {art(nome_paese(nk))}")] if nk and nk in SLUG_RIF and ha_uk(nk) else []))}
<h2>Where else {escape(X)} moved in {Y1}</h2><div class="griglia">{"".join(scheda_coppia(c, x, "../../") for x in [y for y in COPPIE_TR[c] if y != d][:8])}</div>
<p><a href="../">How many {escape(X)} moved abroad in {Y1}</a> · <a href="../../">Who moved where: all nationalities</a> · <a href="{rel}">Visa income calculator</a></p>"""
    ld = ld_dataset(f"UK work, study and family visas granted to {cit}, {ANNI_TR[0]}-{Y1}", "Home Office entry clearance visas granted by nationality and year of decision.",
                    percorso, [F_UKV["url"]], f"{ANNI_TR[0]}/{F_UKV['ultimo_trimestre'].replace(' ', '-')}", F_UKV["licenza_url"])
    pagina(percorso, titolo_tr(X, "the UK", Y1),
           f"The UK granted {intero(t1)} work, study and family visas to {cit} in {Y1} ({variazione(t1, t0)} on {Y0}): {per_tipo}. Home Office data, year by year since {ANNI_TR[0]}.",
           corpo, jsonld_extra=[ld_faq(domande), ld], briciole=[("Who moved where", SEZ_TR), (X, f"{SEZ_TR}{slug}/"), ("United Kingdom", percorso)])


# ---------- pagina della nazionalità (hub)
def pagina_tr_naz(c):
    slug, X, cit, paese, _, parola = NAZ_TR[c]
    rel = "../../"
    percorso = f"{SEZ_TR}{slug}/"
    ue1, ue0 = riga_eu(c, "EU27_2020", Y1), riga_eu(c, "EU27_2020", Y0)
    t1, t0 = ue1[0], (ue0[0] if ue0 else None)
    efta1 = sum((riga_eu(c, g, Y1) or [0])[0] or 0 for g in GEO_EFTA)
    efta0 = sum((riga_eu(c, g, Y0) or [0])[0] or 0 for g in GEO_EFTA)
    top = sorted([g for g in GEO_UE if riga_eu(c, g, Y1) and riga_eu(c, g, Y1)[0] is not None], key=lambda g: -riga_eu(c, g, Y1)[0])
    slug_g = {g: slug_testo(NOMI_GEO[g]) for g in GEO_UE + GEO_EFTA}

    def riga_tab(g):
        r1, r0 = riga_eu(c, g, Y1), riga_eu(c, g, Y0)
        if not r1 or r1[0] is None:
            return ""
        s = segni_eu(c, g, Y1)
        nome = escape(NOMI_GEO[g])
        link = f'<a href="{slug_g[g]}/">{nome}</a>' if slug_g[g] in COPPIE_TR[c] else nome
        return (f'<tr><td>{link}</td>{cella_n(r1[0], segno_html(s, 0))}{cella_n(r0[0] if r0 else None)}{cella_var(r1[0], r0[0] if r0 else None)}'
                + "".join(cella_n(r1[i], segno_html(s, i)) for i, _ in MOTIVI_TR) + '</tr>')
    righe_ue = "".join(riga_tab(g) for g in top)
    righe_ue += (f'<tr class="tot-r"><td>EU-27 total</td>{cella_n(t1)}{cella_n(t0)}{cella_var(t1, t0)}' + "".join(cella_n(ue1[i]) for i, _ in MOTIVI_TR) + '</tr>')
    righe_efta = "".join(riga_tab(g) for g in sorted(GEO_EFTA, key=lambda g: -((riga_eu(c, g, Y1) or [0])[0] or 0)))
    anni = anni_naz(c)
    righe_s = "".join(f'<tr><td>{a}</td>{cella_n(riga_eu(c, "EU27_2020", a)[0])}' + "".join(cella_n(riga_eu(c, "EU27_2020", a)[i]) for i, _ in MOTIVI_TR)
                      + f'{cella_n(riga_eu(c, "EU27_2020", a)[7])}</tr>' for a in anni if riga_eu(c, "EU27_2020", a))
    rotture = [NOMI_GEO[g] for g in GEO_UE + GEO_EFTA if segni_eu(c, g, Y1).get("0") == "b"]
    poco = [NOMI_GEO[g] for g in GEO_UE + GEO_EFTA if segni_eu(c, g, Y1).get("0") == "u"]
    note = []
    if rotture:
        note.append(f'b = Eurostat marks a break in the time series in {Y1} for {", ".join(rotture)}: the change from {Y0} may partly reflect a change in how permits are counted.')
    if poco:
        note.append(f'u = Eurostat marks the {Y1} figures for {", ".join(poco)} as having low reliability.')
    # Canada e Regno Unito: misure diverse, mostrate a parte
    ca = TRA["canada"]["cittadinanze"].get(c)
    uk = TRA["uk"]["cittadinanze"].get(c)
    fuori = []
    if ca:
        fuori.append((f"canada", "Canada", f"{intero(ca['anni'][Y1])} new permanent residents in {Y1}", f"{variazione(ca['anni'][Y1], ca['anni'].get(Y0))} on {Y0} · IRCC"))
    if uk:
        fuori.append(("uk", "United Kingdom", f"{intero(sum(uk['anni'][Y1]))} work, study and family visas granted in {Y1}", f"{variazione(sum(uk['anni'][Y1]), sum(uk['anni'][Y0]))} on {Y0} · Home Office"))
    schede_fuori = "".join(
        (f'<a href="{d}/">' if d in COPPIE_TR[c] else '<div class="no-link">') + f'<span class="ic f">{bandiera(n)}</span><span>{escape(n)}<small>{escape(m)}<br>{escape(v)}</small></span>'
        + ('</a>' if d in COPPIE_TR[c] else '</div>') for d, n, m, v in fuori)
    frase_fuori = []
    if ca:
        frase_fuori.append(f"{intero(ca['anni'][Y1])} {cit} became permanent residents of Canada (IRCC)")
    if uk:
        frase_fuori.append(f"the UK granted {cit} {intero(sum(uk['anni'][Y1]))} work, study and family visas (Home Office)")
    _t3 = [f"{NOMI_GEO[g]} ({intero(riga_eu(c, g, Y1)[0])})" for g in top[:3]]
    t3 = ", ".join(_t3[:-1]) + " and " + _t3[-1] if len(_t3) > 1 else "".join(_t3)
    pesanti = [NOMI_GEO[g] for g in GEO_UE if NOMI_GEO[g] in rotture and (riga_eu(c, g, Y1)[0] or 0) >= 0.1 * t1]
    rottura_ue = (f" Part of the change may come from {', '.join(pesanti)}, where Eurostat marks a break in the time series in {Y1}." if pesanti else "")
    domande = [
        (f"How many {parola} moved to Europe in {Y1}?",
         f"{intero(t1)} {cit} received a first residence permit in an EU country in {Y1} (Eurostat). {frase_cambio(t1, t0, Y0)} "
         f"Another {intero(efta1)} received one in Iceland, Liechtenstein, Norway or Switzerland."),
        (f"Which European country do most {parola} move to?",
         f"In {Y1} the EU countries that issued the most first permits to {cit} were {t3}."),
    ]
    for g in top[:2]:
        domande.append((f"How many {parola} moved to {art(NOMI_GEO[g])} in {Y1}?",
                        f'{intero(riga_eu(c, g, Y1)[0])} {cit} received a first residence permit in {art(NOMI_GEO[g])} in {Y1}. '
                        + (f'<a href="{slug_g[g]}/">Details by reason and year</a>.' if slug_g[g] in COPPIE_TR[c] else "")))
    if ca:
        domande.append((f"How many {parola} moved to Canada in {Y1}?",
                        f"{intero(ca['anni'][Y1])} {cit} became permanent residents of Canada in {Y1} (IRCC). "
                        + ('<a href="canada/">Year by year</a>.' if "canada" in COPPIE_TR[c] else "")))
    if uk:
        domande.append((f"How many {parola} moved to the UK in {Y1}?",
                        f"The UK granted {intero(sum(uk['anni'][Y1]))} work, study and family visas to {cit} in {Y1} (Home Office). "
                        + ('<a href="uk/">By type and year</a>.' if "uk" in COPPIE_TR[c] else "")))
    domande.append((f"Is this the number of {X} living in Europe?",
                    f"No. These are new permits issued in {Y1}. {X} who have lived in Europe for years, renewed their permits or hold an EU passport are not counted."))
    nota_uk = (f'<p class="small">British citizens were EU citizens until the end of 2020 and did not need residence permits, so the series starts in {PRIMO_ANNO_UK}; '
               f'{PRIMO_ANNO_UK}, the first year after Brexit, may not be comparable with later years. Ireland issues few permits to British citizens because they can live there without one (Common Travel Area).</p>' if c == "UK" else "")
    corpo = f"""<section class="hero"><h1>How many {escape(X)} moved to Europe in {Y1}?</h1>
<p class="lead"><strong>{intero(t1)}</strong> {escape(cit)} received a first residence permit in one of the 27 EU countries in {Y1}, according to Eurostat (data updated on {data_lunga(F_ES["aggiornato_il"])}). {frase_cambio(t1, t0, Y0)}{rottura_ue} The most went to {t3}. Another {intero(efta1)} received one in Iceland, Liechtenstein, Norway or Switzerland.{(' Outside the EU and EFTA, in ' + Y1 + ', ' + ', and '.join(frase_fuori) + '.') if frase_fuori else ''}</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("globe")}<span>First residence permits in the EU</span><span>{escape(cit)} · {Y1}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">27 EU countries · {escape(cit)} · {Y1}</span><span class="sr">: </span><strong>{intero(t1)}</strong> first residence permits</p>
<div class="kpi"><div><b>{intero(t0) if t0 is not None else '–'}</b><span>in {Y0}</span></div><div><b>{variazione(t1, t0)}</b><span>change on {Y0}</span></div><div><b>{intero(efta1)}</b><span>Iceland, Liechtenstein, Norway, Switzerland ({variazione(efta1, efta0)})</span></div><div><b>{len([x for x in COPPIE_TR[c] if DEST_TR[x][0] == 'eu'])}</b><span>European countries with {intero(SOGLIA_TR)}+ permits</span></div></div>
<p class="lead" style="margin-top:6px">{motivi_frase(ue1)}</p>
{fonte_es_p()}
</div></section>
{cosa_eu(c, "the EU", hub=True)}
{AD}
<h2>How many {escape(X)} moved to each EU country in {Y1}</h2>
<p class="small">First residence permits issued to {escape(cit)}, by EU country, from the most. Tap a column heading to sort. Countries with at least {intero(SOGLIA_TR)} permits in {Y1} have their own page.</p>
<div class="tab compatta"><table class="ord larga" id="t-tr"><caption class="sr">First residence permits issued to {escape(cit)} by EU country, {Y1} and {Y0}, with reasons for {Y1}</caption><thead><tr>{th_ord("Country", False, "ascending")}{th_ord(Y1)}{th_ord(Y0)}{th_ord("Change")}{th_ord("Family")}{th_ord("Education")}{th_ord("Work")}{th_ord("Other")}</tr></thead><tbody>{righe_ue}</tbody></table></div>
{fonte_es_p()}
{f'<p class="small">{" ".join(note)}</p>' if note else ''}
<h2>Iceland, Liechtenstein, Norway and Switzerland</h2>
<div class="tab compatta"><table class="larga"><caption class="sr">First residence permits issued to {escape(cit)} by EFTA countries, {Y1} and {Y0}</caption><thead><tr><th scope="col">Country</th><th class="n" scope="col">{Y1}</th><th class="n" scope="col">{Y0}</th><th class="n" scope="col">Change</th><th class="n" scope="col">Family</th><th class="n" scope="col">Education</th><th class="n" scope="col">Work</th><th class="n" scope="col">Other</th></tr></thead><tbody>{righe_efta}</tbody></table></div>
{fonte_es_p("These four countries are not in the EU total. ")}
<h2>{escape(X)} moving to the EU, year by year ({anni[0]}–{Y1})</h2>
<div class="tab compatta"><table><caption class="sr">First residence permits issued to {escape(cit)} in the 27 EU countries by year and reason</caption><thead><tr><th scope="col">Year</th><th class="n" scope="col">All reasons</th><th class="n" scope="col">Family</th><th class="n" scope="col">Education</th><th class="n" scope="col">Work</th><th class="n" scope="col">Other</th><th class="n" scope="col">Valid 12+ months</th></tr></thead><tbody>{righe_s}</tbody></table></div>
{fonte_es_p("EU-27 = the 27 current EU countries in every year. Eurostat revises past years when countries correct their data. ")}
{nota_uk}
{f'<h2>{" and ".join(n for _, n, _, _ in fuori)}</h2><p class="lead">{" and ".join("Canada" if d == "canada" else "the UK" for d, _, _, _ in fuori)} {"publish" if len(fuori) > 1 else "publishes"} different figures, so {"they are" if len(fuori) > 1 else "it is"} not added to the European total: {"; ".join("Canada counts new permanent residents by citizenship" if d == "canada" else "the UK counts work, study and family visas granted" for d, _, _, _ in fuori)}.</p><div class="griglia">{schede_fuori}</div>' if fuori else ''}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
{f'<h2>Visa statistics for {escape(paese)}</h2>' + lista_link(link_sito_naz(c, rel)) if link_sito_naz(c, rel) else ''}
<h2>Other nationalities</h2>
<div class="griglia">{"".join(f'<a href="../{NAZ_TR[x][0]}/"><span class="ic">{ico("passport")}</span><span>{escape(NAZ_TR[x][1])}<small>{intero(riga_eu(x, "EU27_2020", Y1)[0])} first permits in the EU in {Y1}</small></span></a>' for x in NAZ_TR if x != c)}</div>
<p><a href="../">Who moved where: all nationalities</a> · <a href="{rel}{SEZ}">Visa refusal rates</a> · <a href="{rel}">Visa income calculator</a></p>"""
    titolo = next(v for v in (f"How many {X} moved to Europe in {Y1}? Official EU figures", f"How many {X} moved to Europe in {Y1}? EU figures",
                              f"How many {X} moved to Europe in {Y1}?") if len(v) <= 70)
    descr = (f"{intero(t1)} {cit} got a first residence permit in the EU in {Y1} ({variazione(t1, t0)} on {Y0}). Most went to {t3}. "
             f"Every EU country by reason, plus Canada and the UK. Eurostat data.")
    ld = ld_dataset(f"First residence permits issued to {cit} in the EU and EFTA, {anni[0]}-{Y1}", f"Eurostat first residence permits for {cit} by country and reason.",
                    percorso, [F_ES["pagina"]], f"{anni[0]}/{Y1}", "https://creativecommons.org/licenses/by/4.0/")
    pagina(percorso, titolo, descr, corpo, ordina=True, jsonld_extra=[ld_faq(domande), ld], briciole=[("Who moved where", SEZ_TR), (X, percorso)])


# ---------- indice della sezione
def pagina_tr_indice():
    rel = "../"
    righe = []
    rotture_idx = []
    for c in sorted(NAZ_TR, key=lambda x: -riga_eu(x, "EU27_2020", Y1)[0]):
        slug, X, cit = NAZ_TR[c][:3]
        u1, u0 = riga_eu(c, "EU27_2020", Y1)[0], (riga_eu(c, "EU27_2020", Y0) or [None])[0]
        efta = sum((riga_eu(c, g, Y1) or [0])[0] or 0 for g in GEO_EFTA)
        ca = TRA["canada"]["cittadinanze"].get(c)
        uk = TRA["uk"]["cittadinanze"].get(c)
        pesanti = [NOMI_GEO[g] for g in GEO_UE if segni_eu(c, g, Y1).get("0") == "b" and (riga_eu(c, g, Y1)[0] or 0) >= 0.1 * u1]
        if pesanti:
            rotture_idx.append(f"{X} ({', '.join(pesanti)})")
        righe.append(f'<tr><td><a href="{slug}/">{escape(X)}</a></td>{cella_n(u1, "<sup title=\"break in time series\">b</sup>" if pesanti else "")}{cella_n(u0)}{cella_var(u1, u0)}{cella_n(efta)}'
                     f'{cella_n(ca["anni"][Y1] if ca else None)}{cella_n(sum(uk["anni"][Y1]) if uk else None)}</tr>')
    us = riga_eu("US", "EU27_2020", Y1)[0], riga_eu("US", "EU27_2020", Y0)[0]
    uk_ = riga_eu("UK", "EU27_2020", Y1)[0]
    n_coppie = sum(len(v) for v in COPPIE_TR.values())
    schede = "".join(f'<a href="{NAZ_TR[c][0]}/"><span class="ic">{ico("passport")}</span><span>How many {escape(NAZ_TR[c][1])} moved to Europe<small>{intero(riga_eu(c, "EU27_2020", Y1)[0])} first permits in {Y1}</small></span></a>' for c in NAZ_TR)
    corpo = f"""<section class="hero"><h1>Who moved where in {Y1}: Europe, Canada and the UK by nationality</h1>
<p class="lead"><strong>{intero(us[0])}</strong> US citizens received a first residence permit in an EU country in {Y1} ({variazione(*us)} on {Y0}), and {intero(uk_)} British citizens did, according to Eurostat (data updated on {data_lunga(F_ES["aggiornato_il"])}). Here are the official figures for {len(NAZ_TR)} nationalities: first residence permits in the EU and EFTA countries (Eurostat), new permanent residents of Canada (IRCC) and UK work, study and family visas (Home Office).</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("globe")}<span>Who moved where</span><span>{Y1}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">US citizens · 27 EU countries · {Y1}</span><span class="sr">: </span><strong>{intero(us[0])}</strong> first residence permits ({variazione(*us)} on {Y0})</p>
<div class="kpi"><div><b>{len(NAZ_TR)}</b><span>nationalities</span></div><div><b>{len(GEO_UE) + len(GEO_EFTA)}</b><span>European countries, plus Canada and the UK</span></div><div><b>{n_coppie}</b><span>pages with {intero(SOGLIA_TR)}+ in {Y1}</span></div><div><b>{ANNI_TR[0]}–{Y1}</b><span>years covered</span></div></div>
{fonte_es_p()}
</div></section>
{AD}
<h2>By nationality ({Y1})</h2>
<p class="small">Three different measures, never added together: first residence permits in the 27 EU countries and in Iceland, Liechtenstein, Norway and Switzerland (Eurostat); new permanent residents of Canada (IRCC); work, study and family visas granted by the UK (Home Office). Tap a column heading to sort.</p>
<div class="tab compatta"><table class="ord larga"><caption class="sr">Moves abroad by nationality, {Y1}: EU first residence permits, EFTA first permits, new permanent residents of Canada, UK visas granted</caption><thead><tr>{th_ord("Nationality", False, "ascending")}{th_ord(f"EU {Y1}")}{th_ord(f"EU {Y0}")}{th_ord("Change")}{th_ord("EFTA")}{th_ord("Canada")}{th_ord("UK")}</tr></thead><tbody>{"".join(righe)}</tbody></table></div>
{fonte_es_p()}
{fonte_pr_p()}
{fonte_ukv_p()}
{f'<p class="small">b = in {Y1} Eurostat marks a break in the time series for a country that issued at least 10% of these permits: ' + "; ".join(rotture_idx) + f'. Part of the change from {Y0} may come from that.</p>' if rotture_idx else ''}
<h2>Nationalities</h2>
<div class="griglia">{schede}</div>
<h2>How to read these figures</h2>
<ul class="testo">
<li><strong>EU and EFTA (Eurostat):</strong> residence permits valid for at least 3 months issued to non-EU citizens for the first time. They are not a count of moves or of residents, and they leave out people who also hold an EU passport.</li>
<li><strong>Canada (IRCC):</strong> new permanent residents by citizenship. Many already lived in Canada on a temporary permit; temporary workers and students are not counted.</li>
<li><strong>United Kingdom (Home Office):</strong> work, study and family visas granted to people applying from outside the UK, including dependants. Visitors are not counted.</li>
<li><strong>Updates:</strong> Eurostat publishes each year once, in the autumn of the year after, and revises past years when countries correct their data. IRCC updates its file every month and the Home Office every quarter.</li>
<li>We show a nationality and country page when there were at least {intero(SOGLIA_TR)} permits, new permanent residents or visas in {Y1}.</li></ul>
<h2>Official sources</h2>
<ul class="fonti">
<li><a href="{escape(F_ES["pagina"])}" rel="noopener">Eurostat, {escape(F_ES["titolo"])}</a> – data updated on {data_lunga(F_ES["aggiornato_il"])}, downloaded from the Eurostat API on {data_lunga(F_ES["scaricato_il"])}; <a href="{escape(F_ES["metadati"])}" rel="noopener">definitions and metadata</a>; <a href="{escape(F_ES["licenza_url"])}" rel="license noopener">free re-use with acknowledgement</a>.</li>
<li><a href="{escape(F_PR["pagina"])}" rel="noopener">IRCC, Permanent Residents – Monthly IRCC Updates</a> – <a href="{escape(F_PR["url"])}" rel="noopener">CSV</a> updated on {data_rfc(F_PR["ultima_modifica"])}, data to {mese_testo(F_PR["ultimo_mese"])}. Contains information licensed under the <a href="{escape(F_PR["licenza_url"])}" rel="license noopener">{escape(F_PR["licenza"])}</a>.</li>
<li><a href="{escape(F_UKV["url"])}" rel="noopener">Home Office, {escape(F_UKV["titolo"])}</a> – published {escape(F_UKV["pubblicato"])}, next update {escape(F_UKV["prossimo"])}. Contains public sector information licensed under the <a href="{escape(F_UKV["licenza_url"])}" rel="license noopener">{escape(F_UKV["licenza"])}</a>.</li></ul>
<p><a href="{rel}{SEZ}">Visa refusal rates</a> · <a href="{rel}digital-nomad-visa-income-requirements/">Digital nomad visa income requirements</a> · <a href="{rel}">Visa income calculator</a></p>"""
    ld = ld_dataset(f"First residence permits, new permanent residents and visas granted by nationality, {ANNI_TR[0]}-{Y1}",
                    "Eurostat first residence permits (EU and EFTA), IRCC new permanent residents of Canada and Home Office visas granted, for 12 nationalities.",
                    SEZ_TR, [F_ES["pagina"], F_PR["url"], F_UKV["url"]], f"{ANNI_TR[0]}/{Y1}", "https://creativecommons.org/licenses/by/4.0/")
    pagina(SEZ_TR, f"Who moved where in {Y1}: Europe, Canada and the UK by nationality",
           f"How many Americans, British people, Indians and 9 more nationalities moved to Europe, Canada and the UK in {Y1}: "
           f"official first residence permits, new permanent residents and visas granted.", corpo, ordina=True, jsonld_extra=[ld],
           briciole=[("Who moved where", SEZ_TR)])


def blocco_tr_dest(nome_sito, rel):
    """Collegamenti dalle pagine Paese esistenti (/country/<slug>/) alle pagine 'How many ... moved to <Paese>'."""
    d = "uk" if nome_sito == "United Kingdom" else slug_testo(nome_sito)
    if d not in DEST_TR:
        return ""
    chi = [c for c in sorted(NAZ_TR, key=lambda x: -(val_tr(x, d, Y1) or 0)) if d in COPPIE_TR[c]]
    if not chi:
        return ""
    misura = ("work, study and family visas granted by the UK in " + Y1 + " (Home Office)" if d == "uk"
              else f"first residence permits issued in {Y1} (Eurostat)")
    nf = DEST_TR[d][3]
    return (f'<h2>Who moved to {escape(nf)} in {Y1}</h2><p class="lead">How many people of each nationality moved to {escape(nf)}: {misura}.</p>'
            f'<div class="griglia">{"".join(scheda_coppia(c, d, rel + SEZ_TR, chi=True) for c in chi)}</div>')


def genera_trasferimenti():
    pagina_tr_indice()
    for c in NAZ_TR:
        pagina_tr_naz(c)
        for d in COPPIE_TR[c]:
            {"eu": pagina_tr_eu, "ca": pagina_tr_ca, "uk": pagina_tr_uk}[DEST_TR[d][0]](c, d)


def controlli_trasferimenti():
    errori = []
    if set(NAZ_TR) - set(EUD):
        errori.append(f"trasferimenti: cittadinanze senza dati Eurostat: {set(NAZ_TR) - set(EUD)}")
    if len({v[0] for v in NAZ_TR.values()}) != len(NAZ_TR) or len(DEST_TR) != len(GEO_UE) + len(GEO_EFTA) + 2:
        errori.append("trasferimenti: slug duplicati")
    if len(GEO_UE) != 27:
        errori.append(f"trasferimenti: {len(GEO_UE)} Paesi UE invece di 27")
    for c in NAZ_TR:
        if not riga_eu(c, "EU27_2020", Y1) or not riga_eu(c, "EU27_2020", Y0):
            errori.append(f"trasferimenti: manca il totale UE-27 {Y0}/{Y1} per {c}")
    if sum(len(v) for v in COPPIE_TR.values()) < 100:
        errori.append("trasferimenti: meno di 100 pagine nazionalità × Paese")
    for k, f in TRA["fonti"].items():
        if not f.get("url", "").startswith("https://") or not f.get("licenza_url", "").startswith("https://"):
            errori.append(f"trasferimenti: fonte {k} senza URL o licenza")
    if not F_ES.get("aggiornato_il"):
        errori.append("trasferimenti: data di aggiornamento Eurostat mancante")
    return errori


ORDINA_JS = r"""
(function(){
  document.querySelectorAll('table.ord').forEach(function(t){
    var ths=t.tHead.rows[0].cells;
    Array.prototype.forEach.call(ths,function(th,i){var b=th.querySelector('button.ord');if(!b)return;
      b.addEventListener('click',function(){
        var cur=th.getAttribute('aria-sort'),dir=cur?(cur==='ascending'?'descending':'ascending'):(th.getAttribute('data-primo')||'descending');
        Array.prototype.forEach.call(ths,function(x){x.removeAttribute('aria-sort');});th.setAttribute('aria-sort',dir);
        var tb=t.tBodies[0],rows=Array.prototype.slice.call(tb.rows);
        rows.sort(function(a,c){var x=a.cells[i],y=c.cells[i],vx=x.getAttribute('data-v'),vy=y.getAttribute('data-v'),r;
          if(vx!==null||vy!==null){if(vx===''||vx===null)return 1;if(vy===''||vy===null)return -1;r=parseFloat(vx)-parseFloat(vy);}
          else r=x.textContent.trim().localeCompare(y.textContent.trim());
          return dir==='ascending'?r:-r;});
        rows.forEach(function(r){tb.appendChild(r);});});});});
  document.querySelectorAll('input[data-filtro]').forEach(function(inp){var t=document.getElementById(inp.getAttribute('data-filtro'));if(!t)return;
    inp.addEventListener('input',function(){var q=inp.value.trim().toLowerCase();
      Array.prototype.forEach.call(t.tBodies[0].rows,function(r){r.hidden=q&&r.cells[0].textContent.toLowerCase().indexOf(q)<0;});});});
  document.querySelectorAll('select[data-vai]').forEach(function(s){s.addEventListener('change',function(){if(s.value)location.href=s.value;});});
})();
"""


def link_tr_naz(p, rel):
    """Dalle pagine dei visti rifiutati di India, Pakistan, Nigeria, Filippine, Cina e Sudafrica alla pagina 'How many ... moved to Europe'."""
    c = next((k for k, v in NAZ_TR.items() if v[4] == p), None)
    if not c:
        return ""
    return (f'<p class="small">{ico("globe")} How many {escape(NAZ_TR[c][1])} moved abroad? <a href="{rel}{SEZ_TR}{NAZ_TR[c][0]}/">'
            f'How many {escape(NAZ_TR[c][1])} moved to Europe in {Y1}</a> (first residence permits by country and reason, Eurostat).</p>')


def link_rifiuti(paese, rel):
    """Riga di collegamento alla sezione dei visti rifiutati dalle pagine dei programmi e dei Paesi."""
    if paese in SLUG_STATO:
        return (f'<p class="small">{ico("passport")} Visiting {escape(paese)} first? See the <a href="{rel}{SEZ}schengen/{SLUG_STATO[paese]}/">'
                f'{escape(paese)} Schengen visa rejection rate by country ({A1})</a> and <a href="{rel}{SEZ}">all visa refusal rates</a>.</p>')
    if paese == "United Kingdom":
        return (f'<p class="small">{ico("passport")} See the <a href="{rel}{SEZ}uk/">UK visa refusal rate by nationality</a> '
                f'(Home Office, to {trimestre_testo(TRIM[-1])}).</p>')
    return f'<p class="small">{ico("passport")} See <a href="{rel}{SEZ}">visa refusal rates by country</a>.</p>'


def genera_rifiuti():
    pagina_rif_panoramica()
    for p in PAESI_RIF:
        pagina_rif_paese(p)
    for p in PAESI_FACILE:
        pagina_rif_facile(p)
    for s in STATI_UE:
        pagina_rif_stato(s)
    pagina_rif_uk()
    pagina_rif_uk_famiglia()
    pagina_rif_au()
    pagina_rif_nz()
    pagina_rif_ca()


def controlli_rifiuti():
    errori = []
    if len(PAESI_RIF) < 40:
        errori.append(f"rifiuti: solo {len(PAESI_RIF)} Paesi con pagina")
    if len(set(SLUG_RIF.values())) != len(SLUG_RIF) or set(SLUG_RIF.values()) & {"uk", "schengen"}:
        errori.append("rifiuti: slug dei Paesi duplicati o riservati")
    if len(PAESI_FACILE) < 30:
        errori.append(f"rifiuti: solo {len(PAESI_FACILE)} Paesi con la pagina 'easiest Schengen visa'")
    senza = [p for p in PAESI_RIF if p not in DEMONIMI]
    if senza:
        errori.append(f"rifiuti: aggettivo di nazionalità mancante per {', '.join(senza)} (DEMONIMI)")
    for k, f in RIF["fonti"].items():
        if not f.get("url", "").startswith("https://"):
            errori.append(f"rifiuti: fonte {k} senza URL")
    if URL_SAFETYWING and not URL_SAFETYWING.startswith("https://safetywing.com/"):
        errori.append("rifiuti: link SafetyWing non valido in dati/affiliati.json (_safetywing_schengen)")
    if not URL_SAFETYWING and not _SW.get("url_sospeso", "").startswith("https://safetywing.com/"):
        errori.append("rifiuti: link SafetyWing né attivo né sospeso in dati/affiliati.json (_safetywing_schengen)")
    return errori


def extra():
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n")
    (SITO / f"{CHIAVE_INDEXNOW}.txt").write_text(CHIAVE_INDEXNOW)  # file chiave IndexNow: non in sitemap, non linkato
    MON.scrivi_ads_txt(SITO_ID, SITO)  # sito/ads.txt solo con AdSense acceso (monetizzazione.json)
    date_ = date_lastmod()
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{date_[u]}</lastmod></url>" for u in URLS)
    (SITO / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n')
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in visaincome/sito (ogni pubblicazione consuma crediti Netlify).
  # I cambi BCE arrivano alle pagine da GitHub (italystrikes/dati/cambi-bce.json, aggiornato due volte al giorno dal workflow
  # di Italy Strikes) e non richiedono pubblicazioni; visaincome/dati/cambi.json è solo il valore di riserva scritto nelle pagine.
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."

[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    X-Frame-Options = "DENY"
    Permissions-Policy = "camera=(), microphone=(), geolocation=()"

[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=604800"
""")
    pagina("404.html", f"Page not found | {NOME}", "Page not found.",
           '<section class="hero"><h1>Page not found</h1><p class="lead">Go to the <a href="/">visa income calculator</a>.</p></section>', indicizza=False, assoluto=True)


def copia_grafica():
    """Font (licenza OFL inclusa) e immagine Open Graph da grafica/ a sito/assets/."""
    (SITO / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (RADICE / "grafica" / "fonts").iterdir():
        shutil.copy(f, SITO / "assets" / "fonts" / f.name)
    shutil.copy(RADICE / "grafica" / "og.png", SITO / "assets" / "og.png")


def controlli():
    errori = []
    for k, I in INDICI.items():
        for c in ("nome", "nome_breve", "valore", "valuta", "periodo", "calcolo", "fonti"):
            if I.get(c) in (None, "", []):
                errori.append(f"indice {k}: manca {c}")
        if not any(f["http"] == 200 for f in I["fonti"]):
            errori.append(f"indice {k}: nessuna fonte leggibile (200)")
    for P in PROG:
        for c in ("slug", "paese", "paese_slug", "nome", "nome_ufficiale", "categoria", "reddito", "descrizione", "varianti", "fonti"):
            if not P.get(c):
                errori.append(f"{P.get('slug')}: manca {c}")
        if P["categoria"] not in CATEGORIE:
            errori.append(f"{P['slug']}: categoria sconosciuta")
        for f in P["fonti"]:
            for c in ("titolo", "editore", "url", "formato", "controllato_il", "http"):
                if not f.get(c):
                    errori.append(f"{P['slug']}: fonte senza {c}")
            if f.get("http") != 200:
                errori.append(f"{P['slug']}: fonte non letta (http {f.get('http')})")
        for V in P["varianti"]:
            b = V["base"]
            if "indice" in b and b["indice"] not in INDICI:
                errori.append(f"{P['slug']}/{V['id']}: indice sconosciuto")
            _, val, per, _np = unita(V)
            if val not in VALUTE or (val != "EUR" and val not in CAMBI["tassi"]):
                errori.append(f"{P['slug']}/{V['id']}: valuta {val} senza cambio BCE")
            if per not in ("month", "year"):
                errori.append(f"{P['slug']}/{V['id']}: periodo {per}")
            if V["famiglia"]["tipo"] not in ("tutti", "per_eta", "figli", "nessuno"):
                errori.append(f"{P['slug']}/{V['id']}: famiglia sconosciuta")
            if V["famiglia"]["tipo"] == "nessuno" and not V["famiglia"].get("motivo"):
                errori.append(f"{P['slug']}/{V['id']}: manca il motivo per i familiari")
    if len({P["slug"] for P in PROG}) != len(PROG):
        errori.append("slug duplicati")
    errori += controlli_rifiuti()
    errori += controlli_altri()
    errori += controlli_trasferimenti()
    if errori:
        raise SystemExit("ERRORI NEI DATI:\n" + "\n".join(errori))


def main():
    controlli()
    if SITO.exists():
        conserva = {p.name: p.read_bytes() for p in SITO.glob("google*.html")}
        VECCHIE.update({percorso_da_file(f): impronta_contenuto(f.read_text(encoding="utf-8")) for f in SITO.rglob("*.html")})
        shutil.rmtree(SITO)
    else:
        conserva = {}
    SITO.mkdir()
    for nome, contenuto in conserva.items():
        (SITO / nome).write_bytes(contenuto)
    copia_grafica()
    home()
    for P in PROG:
        pagina_programma(P)
    for s in PAESI:
        pagina_paese(s)
    pagina_confronto_nomadi()
    pagina_confronto_lavoro()
    genera_rifiuti()
    genera_trasferimenti()
    pagina_come_funziona()
    about()
    contatti()
    privacy()
    extra()
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili; {len(PROG)} programmi in {len(PAESI)} paesi; "
          f"cambi BCE del {CAMBI['data']}; visti rifiutati: {len(PAESI_RIF)} Paesi, {len(STATI_UE)} Stati Schengen ({A1}), UK fino al {TRIM[-1]}; "
          f"Australia {len(AU_OK)} nazionalità ({AU_A1}), Nuova Zelanda {len(NZ_OK)} ({NZ_A1}), Canada {len(CA_OK)} ({CA_A1}); "
          f"trasferimenti: {len(NAZ_TR)} nazionalità, {sum(len(v) for v in COPPIE_TR.values())} pagine nazionalità × Paese ({Y1}).")


if __name__ == "__main__":
    main()
