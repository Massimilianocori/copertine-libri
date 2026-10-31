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
from datetime import date, timedelta
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


def pagina(percorso, titolo, descrizione, corpo, briciole=None, indicizza=True, calcolatore=False, jsonld_extra=None, assoluto=False, testata="", ordina=False, script=""):
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
    if script:  # calcolatori delle sezioni per studenti (STUDIO_JS)
        js += f"<script>{script}</script>"
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
<ul><li><a href="{rel}visa-refusal-rates/">Visa refusal rates</a></li><li><a href="{rel}moved-to/">Who moved where (by nationality)</a></li><li><a href="{rel}uk-english-test/">UK visa English tests (SELT)</a></li><li><a href="{rel}thailand-dtv-visa/">Thailand DTV visa by embassy</a></li><li><a href="{rel}us-opt/">US OPT and STEM OPT: fees and deadlines</a></li><li><a href="{rel}uk-graduate-visa/">UK Graduate visa: 2 years or 18 months</a></li><li><a href="{rel}mexico-residency/">Mexico residency: fees and income by consulate</a></li><li><a href="{rel}study-in-italy/">Study in Italy: visa funds and DSU scholarships</a></li><li><a href="{rel}italy-7-percent-flat-tax/">Italy 7% flat tax for foreign pensioners</a></li><li><a href="{rel}about/">About</a></li><li><a href="{rel}how-it-works/">How it works and sources</a></li><li><a href="{rel}contact/">Contact</a></li><li><a href="{rel}privacy.html">Privacy</a></li><li><a href="{rel}contact/?ref=spotted-a-change">Spotted a change? Tell us</a></li></ul>
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
{link_rifiuti(P['paese'], rel)}
{link_selt(P, rel)}{link_graduate(P, rel)}{link_studio_it(P, rel)}{link_flat7_it(P, rel)}"""
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
{link_studio_it({"paese": nome}, rel)}{link_flat7_it({"paese": nome}, rel)}
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
<h2>UK visa English tests (SELT)</h2>
<p class="lead">Which English level each UK visa needs (A1 for a first spouse visa, B1 for settlement and citizenship, B2 for settlement from {data_lunga(DATA_B2)}) and the {intero(len(CENTRI_UK))} approved test centres in the UK and {intero(len(CENTRI_EST))} abroad (Home Office lists of {data_lunga(DATA_ELENCO)}).</p>
<p><a href="{SEZ_SELT}">UK visa English tests: levels and test centres</a> · {" · ".join(f'<a href="{SEZ_SELT}{SLUG_SELT[x]}/">{escape(NOMI_PAESI_SELT.get(x, x))}</a>' for x in ("London", "Birmingham", "Manchester", "Pakistan", "India", "Nigeria") if x in CITTA_PAG + PAESI_PAG)}</p>
<h2>Thailand DTV visa by embassy</h2>
<p class="lead">The DTV fee and who can apply change from one Thai embassy to another: {costo_dtv(next(L for L in LET_DTV if L["id"] == "vientiane")["costo"])} in Vientiane, {costo_dtv(next(L for L in LET_DTV if L["id"] == "london")["costo"])} in London, {costo_dtv(next(L for L in LET_DTV if L["id"] == "washington-dc")["costo"])} in Washington (official pages read on {data_lunga(LETTO_DTV)}), and since 31 August 2026 you apply where you live permanently.</p>
<p><a href="{SEZ_DTV}">Thailand DTV visa: all embassies</a> · {" · ".join(f'<a href="{SEZ_DTV}{L["id"]}/">{escape(L["sede"])}</a>' for L in PAG_DTV if L["id"] in ("london", "ho-chi-minh-city", "vientiane", "kuala-lumpur", "singapore", "new-delhi"))}</p>
<h2>Students: US OPT and the UK Graduate visa</h2>
<p class="lead">OPT and the STEM OPT extension cost {usd(vo("tassa_online"))} online or {usd(vo("tassa_carta"))} on paper (Form I-765), and you file from {vo("finestra")["prima"]} days before to {vo("finestra")["dopo"]} days after your program end date (USCIS, read on {data_lunga(LETTO_OPT)}). The UK Graduate visa lasts 2 years if you apply by 31 December 2026 and 18 months from 1 January 2027 (GOV.UK, read on {data_lunga(LETTO_GRAD)}).</p>
<p><a href="{SEZ_OPT}">US OPT and STEM OPT: fees and deadlines</a> · <a href="{SEZ_OPT}opt-application-deadline-calculator/">OPT deadline calculator</a> · <a href="{SEZ_OPT}opt-unemployment-days/">OPT unemployment days</a> · <a href="{SEZ_GRAD}">UK Graduate visa</a> · <a href="{SEZ_GRAD}18-months/">Graduate visa 18 months</a> · <a href="{SEZ_GRAD}cost/">Graduate visa cost</a></p>
<h2>Mexico residency by consulate</h2>
<p class="lead">A Mexican temporary resident card costs {mxn(TASSE_MX["1"][1])} for up to one year in {ANNO} (Diario Oficial, read on {data_lunga(LETTO_MX)}), and the visa asks for a net income above {mxn(pesos_uma(GIORNI_MX["tr"][0]))} a month, which each consulate publishes in its own currency.</p>
<p><a href="{SEZ_MX}">Mexico residency: fees and income by consulate</a> · <a href="{SEZ_MX}income-requirements/">Income requirements</a> · <a href="{SEZ_MX}fees/">Fees {ANNO}</a> · {" · ".join(f'<a href="{SEZ_MX}{C["id"]}/">{escape(C["sede"])}</a>' for C in CONS_MX if C["id"] in ("new-york", "las-vegas", "san-diego", "london", "vancouver"))}</p>
<h2>Study in Italy: visa funds and DSU scholarships</h2>
<p class="lead">The Italian student visa for 2026/27 asks for {eur(LIT["mezzi"])} a year (Ministry of University and Research procedures, read on {data_lunga(LETTO_IT)}), and regional DSU scholarships pay an off-campus student at least {eur(LIT["dsu_fs"])} when the family's ISEE stays under the limit, up to {eur(LIT["isee_max"])}.</p>
<p><a href="{SEZ_IT}">Study in Italy 2026/27</a> · <a href="{SEZ_IT}student-visa-funds/">Visa bank balance</a> · <a href="{SEZ_IT}isee-parificato/">ISEE parificato</a> · <a href="{SEZ_IT}dsu-scholarship-deadlines/">DSU deadlines</a> · {" · ".join(f'<a href="{SEZ_IT}{E["id"]}/">{escape(E["nome"])}</a>' for E in ENTI_IT if E["id"] in ("university-of-milan", "politecnico-di-milano", "disco-lazio", "er-go", "university-of-padua"))}</p>
<h2>Italy 7% flat tax for foreign pensioners</h2>
<p class="lead">A person with a foreign pension who moves to a town of up to {intero(SOGLIA_F7)} inhabitants in southern Italy or in the earthquake areas can pay 7% on foreign income for ten years (article 24-ter of the income tax code, read on {data_lunga(LETTO_F7)}). Check any town against ISTAT's population figure for the year that counts.</p>
<p><a href="{SEZ_F7}">Italy 7% flat tax: rules and town check</a> · <a href="{SEZ_F7}regions/">7% tax regions and earthquake towns</a></p>
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
<p>We publish a visa only when we can read the complete rule on an official page or in the official gazette. Not covered on the date we checked, because the official source was not readable or was incomplete: Greece (digital nomad visa, financially independent person), Cyprus, Malta (Nomad Residence Permit), Estonia, Czechia, Romania, Latvia, Iceland, Costa Rica, Brazil, Panama, Colombia and the United Arab Emirates. See <a href="{rel}how-it-works/">How it works</a>.</p>
<p>{ico("passport")} <strong>Mexico:</strong> the temporary resident visa asks for a net income above {intero(GIORNI_MX["tr"][0])} days of UMA ({mxn(pesos_uma(GIORNI_MX["tr"][0]))} a month in {ANNO}), and each consulate publishes it in its own currency. See <a href="{rel}{SEZ_MX}">Mexico residency: fees and income requirements by consulate</a>.</p>
<p>{ico("passport")} <strong>Thailand (DTV):</strong> the Destination Thailand Visa asks for savings (usually 500,000 baht in the bank), not a monthly income, and each Thai embassy sets its own fee and residence rule. See <a href="{rel}{SEZ_DTV}">Thailand DTV visa by embassy: fees and who can apply where</a>.</p>"""
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
<h2>8. UK visa English tests</h2>
<p>The <a href="{rel}uk-english-test/">UK visa English tests (SELT)</a> pages use the Home Office lists of approved test centres and approved tests (ODS files on GOV.UK, updated every few weeks), the GOV.UK guidance for each visa and the Statement of Changes HC 1691 for the B2 level from {data_lunga(DATA_B2)}. A script downloads the lists every week, checks that the sentences we rely on are still in the official pages, and stops if anything changed. We do not show test fees: they are set by each provider.</p>
<h2>Licences and attributions</h2>
<ul><li>Laws, decrees and official notices (BOE, Gazzetta Ufficiale, Bundesanzeiger, Normattiva) are cited as facts with a link to the official text; we do not reproduce the documents.</li>
<li>Exchange rates: European Central Bank, euro foreign exchange reference rates (source: ECB).</li>
<li>UK: contains public sector information licensed under the Open Government Licence v3.0 (GOV.UK and Home Office immigration statistics).</li>
<li>Schengen visa statistics: European Commission, DG Migration and Home Affairs (reuse authorised with acknowledgement of the source).</li>
<li>Other ministry and immigration authority pages are cited with links; the amounts are facts taken from them.</li></ul>
<h2>Not covered yet</h2>
<p>Greece (digital nomad visa and financially independent person visa), Cyprus, Malta, Estonia, Czechia, Romania, Latvia, Iceland, Costa Rica, Brazil, Panama, Colombia and the United Arab Emirates: the official page could not be read by our checks or gave conflicting figures. Colombia's rule is in Colombian pesos, a currency the ECB does not publish. Thailand's DTV has no income threshold (it asks for savings) and its fee and residence rule change from embassy to embassy: see <a href="{rel}{SEZ_DTV}">Thailand DTV visa by embassy</a>. Mexico's amount depends on the consulate: see <a href="{rel}{SEZ_MX}">Mexico residency by consulate</a>.</p>
<h2>9. Thailand DTV visa and Ireland's PPS numbers</h2>
<p>The <a href="{rel}{SEZ_DTV}">Thailand DTV visa</a> pages quote the official DTV pages of the Thai embassies and consulates. A script reads each page again and checks that every fee and rule we show is still written there; if a page changes, nothing is updated until we read it again. The Ireland pages in <a href="{rel}{SEZ_TR}">Who moved where</a> use the monthly PPS number files of Ireland's Department of Social Protection (CC BY 4.0); a script checks that the months add up to the yearly totals.</p>
<h2>10. US OPT and the UK Graduate visa</h2>
<p>The <a href="{rel}{SEZ_OPT}">US OPT and STEM OPT</a> pages use the USCIS fee schedule (Form G-1055), the USCIS pages on Form I-765, OPT and STEM OPT, the SEVP help pages and the Federal Register; the <a href="{rel}{SEZ_GRAD}">UK Graduate visa</a> pages use GOV.UK, the Immigration Rules (Appendix Graduate), the Statement of Changes HC 1333 and the Home Office fees table. A script reads every page again and checks that each figure we show is still written there; if a page changes, nothing is updated until we read it again. Proposals and rules on hold are labelled as such. The date calculators run in your browser.</p>
<h2>11. Mexico residency</h2>
<p>The <a href="{rel}{SEZ_MX}">Mexico residency</a> pages use the Ley Federal de Derechos and Annex 4 of the {ANNO} Miscellaneous Tax Resolution (Diario Oficial) for the fees, the visa guidelines of 25 July 2025 for the days of UMA, INEGI for the UMA value, and the official pages of the Mexican consulates for the amounts in their currency. A consulate is listed only if its own page writes the amount and is from {ANNO}. A script reads every source again and checks that each figure is still written there; if a page changes, nothing is updated until we read it again. We re-read the fees and the UMA every January (new Miscellaneous Tax Resolution, new UMA from 1 February).</p>
<h2>12. Study in Italy</h2>
<p>The <a href="{rel}{SEZ_IT}">Study in Italy</a> pages use the Ministry of University and Research and Foreign Ministry procedures for international students (published on Universitaly), the Ministry's decrees on scholarship amounts, ISEE limits and particularly poor countries, Poste Italiane and the Polizia di Stato for the residence permit costs, Normattiva for the health service contribution and the ISEE equivalence scale, the Bank of Italy for the annual average exchange rates, and the 2026/27 calls of the regional scholarship agencies and universities. A script reads every source again and checks that each figure is still written there; if a call changes, nothing is updated until we read it again. The ISEE estimate is ours and is labelled as such: the CAF or the agency calculates the official figure. We re-read the calls every summer, when the new ones come out.</p>
<h2>13. Italy 7% flat tax for foreign pensioners</h2>
<p>The <a href="{rel}{SEZ_F7}">Italy 7% flat tax</a> pages use the text of article 24-ter of the income tax code and of the laws that changed it (Normattiva), the guidance of the Agenzia delle Entrate, the earthquake lists (Decree-Law 189/2016 on Normattiva and the Abruzzo Region's list for 2009) and ISTAT's resident population of every Italian town on 1 January. A script reads every source again and checks that each rule we quote is still written there. The town check says only whether a town is in one of the areas of the law and whether ISTAT's figure is within the limit: it does not say that anyone qualifies. We load ISTAT's new figures every January.</p>
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
    # Frase su SafetyWing del testo senza pubblicità: solo se il link SafetyWing è attivo (dal 17 al 30/10/2026 era sospeso e la
    # frase non era vera). Con AdSense acceso o link attivi vale comunque il testo comune di monetizzazione.py.
    FRASE_SW = (' Some pages contain an affiliate link to SafetyWing (marked "Affiliate"): our site sets no cookie for it, but if you click it '
                "you go to SafetyWing's website, which uses its own cookies under its own privacy policy and tells SafetyWing that you came from us."
                if URL_SAFETYWING else "")
    cookie = MON.privacy_cookie("en", SITO_ID, ci_sono_affiliati())
    if cookie and URL_SAFETYWING:
        cookie += ("\n<p>Affiliate links to SafetyWing (travel medical insurance) appear in the box marked “Affiliate” on the visa refusal "
                   "rate pages" + (" and on the Thailand DTV visa pages" if URL_SW_DTV else "") + (" and on the Mexico residency pages" if URL_SW_MX else "") + (" and on the Study in Italy health insurance page" if URL_SW_IT else "") + ". Buying a policy does not change the decision on your visa.</p>")
    if cookie and URL_ITALKI:
        cookie += ("\n<p>Affiliate links to italki (online English teachers) appear in the box marked “Affiliate” on the UK visa English test pages. "
                   "Lessons do not change your test result or the decision on your visa.</p>")
    cookie = cookie or f"""<h2>Cookies, visit counter{' and affiliate links' if URL_SAFETYWING else ''}</h2><p>This site does not use profiling cookies. To count visits we use <a href="https://www.goatcounter.com/" rel="noopener">GoatCounter</a>, a privacy-friendly counter: it sets no cookies and stores nothing in your browser, builds no profiles and does not store your IP address, your full browser signature or any identifier. It keeps only aggregate numbers (page, hour or day, browser, country, screen width) on servers in the European Union and shares nothing with third parties; see <a href="https://www.goatcounter.com/help/privacy" rel="noopener">GoatCounter's privacy policy</a>.{FRASE_SW} If we add advertising in the future, we will update this notice and ask for your consent where required before any advertising cookies are used.</p>"""
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
            f'<p class="small">SafetyWing sells travel medical insurance for travellers and nomads online. {MON.RIGA_EN} '
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
<p class="lead" style="margin-top:6px">{frase_basso} Of the {len(PAESI_RIF)} countries with the most applications, {escape(art(nome))} ranks {pos} (1 = lowest rate). Multiple-entry visas: {pct(quota_mev(MEV_PAESE[A1][p]))} of uniform visas issued in {A1} (<a href="#multiple-entry">by country</a>).</p>
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
{sezione_mev(p, rel)}
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
<p><a href="../">Schengen visa refusal rates by country, {A1}</a> · <a href="../multiple-entry-schengen-visa/">Multiple-entry Schengen visas by country</a> · <a href="../uk/">UK visa refusal rates by nationality</a> · <a href="../australia-visas/">Australia</a> · <a href="../new-zealand-visas/">New Zealand</a> · <a href="../canada-visas/">Canada</a> · <a href="{rel}">Visa income calculator</a></p>
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
<h2 id="multiple-entry">Multiple-entry Schengen visas ({A1})</h2>
<p class="lead">In {A1}, {pct(quota_mev(MEV_TOT[A1]))} of the {intero(MEV_TOT[A1][0])} uniform visas issued were multiple-entry visas ({pct(quota_mev(MEV_TOT[A0]))} in {A0}). Which Schengen countries issue them most often, and the share in each country where people apply: <a href="multiple-entry-schengen-visa/">multiple-entry Schengen visas by country ({A1})</a>. The file does not say how long the visas were valid for.</p>
{fonte_ue_p(A1, A0)}
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


# ---------------------------------------------------------------- Visti a ingressi multipli (MEV), 30/10/2026
# Dalla colonna "Multiple entry uniform visas (MEVs) issued" dello stesso file della Commissione (8° elemento delle righe di dati/rifiuti.json).
# Quota MEV = MEV ÷ visti uniformi rilasciati (compresi i MEV), come la colonna "Share of MEVs" del file. Gli LTV non entrano.
# Il file non dice la durata di validità dei visti (1, 3, 5 anni...): le pagine lo scrivono.
SOGLIA_MEV = 500   # visti uniformi rilasciati minimi (Stato × Paese, o Paese) per mostrare la quota MEV senza asterisco
PERCORSO_MEV = f"{SEZ}multiple-entry-schengen-visa/"
DATA_COMMISSIONE_MEV = "2026-10-30"  # pagina "Applying for a Schengen visa" riletta il 30/10/2026 (HTTP 200): definizioni di visto a ingresso singolo e multiplo
URL_METADATI_UE = ("https://home-affairs.ec.europa.eu/document/download/b4626219-fa37-4650-8216-0c2bda466c74_en"
                   "?filename=visa_statistics_-_quality_and_metadata_reporting.pdf")
DATA_METADATI_UE = "2026-10-30"  # PDF dei metadati riletto il 30/10/2026 (HTTP 200): "single entry, double or multiple entries (MEV)"


def mev_raggruppa(anno, i, filtro=None):
    """{chiave: [visti uniformi rilasciati, di cui MEV]} raggruppando per Stato (i=0) o Paese di domanda (i=1)."""
    out = defaultdict(lambda: [0, 0])
    for r in UE[anno]:
        if filtro is None or filtro(r):
            out[r[i]][0] += r[4]
            out[r[i]][1] += r[7]
    return dict(out)


def quota_mev(v):
    return v[1] / v[0] if v and v[0] else None


MEV_STATO = {a: mev_raggruppa(a, 0) for a in ANNI_UE}
MEV_PAESE = {a: mev_raggruppa(a, 1) for a in ANNI_UE}
MEV_TOT = {a: [sum(r[4] for r in UE[a]), sum(r[7] for r in UE[a])] for a in ANNI_UE}


def cella_mev(q, poco=False):
    """Cella con la quota MEV e una barretta (piena = 100%)."""
    if q is None:
        return '<td class="n" data-v="">–</td>'
    larg = max(2, min(100, round(q * 100, 1)))
    return (f'<td class="n" data-v="{q:.6f}"><span class="tb" aria-hidden="true"><i style="width:{larg}%"></i></span>'
            f'<span class="tv">{pct(q)}{"*" if poco else ""}</span></td>')


def punti_mev(v1, v0):
    """Variazione in punti solo se entrambi gli anni superano la soglia."""
    if not v0 or v1[0] < SOGLIA_MEV or v0[0] < SOGLIA_MEV:
        return "–", ""
    return punti(quota_mev(v1), quota_mev(v0)), f"{quota_mev(v1) - quota_mev(v0):.6f}"


def mev_stati_paese(p):
    """Stati con almeno SOGLIA_MEV visti rilasciati nel Paese p (anno più recente), dalla quota più alta; e gli Stati sotto soglia."""
    s1 = mev_raggruppa(A1, 0, lambda r: r[1] == p)
    s0 = mev_raggruppa(A0, 0, lambda r: r[1] == p)
    ok = sorted([(s, v, s0.get(s)) for s, v in s1.items() if v[0] >= SOGLIA_MEV], key=lambda x: (-quota_mev(x[1]), x[0]))
    sotto = sorted(s for s, v in s1.items() if 0 < v[0] < SOGLIA_MEV)
    return ok, sotto


COSA_MEV = (f'A multiple-entry visa "allows several visits to the Schengen area for as long as the visa is valid"; a single-entry visa allows one entry '
            f'(<a href="{URL_COMMISSIONE_DOMANDA}" rel="noopener">European Commission</a>, checked on {data_lunga(DATA_COMMISSIONE_MEV)}). '
            f'Every visit is still a short stay, of up to 90 days in any 180-day period. A multiple-entry visa is not a long-stay visa, a work permit or a residence permit.')
LIMITI_MEV = ("The Commission's file only says whether each visa allows multiple entries: it does not say how long the visas were valid for. "
              "The share describes visas issued in the past, not your chances: the consulate decides the number of entries and the validity of each visa.")


def tabella_mev_paese(ok, rel):
    righe = []
    for s, v, v0 in ok:
        d, dv = punti_mev(v, v0)
        righe.append(f'<tr><td><a href="{rel}{SEZ}schengen/{SLUG_STATO[s]}/">{escape(s)}</a></td>{cella_mev(quota_mev(v))}'
                     f'{cella_mev(quota_mev(v0), bool(v0) and v0[0] < SOGLIA_MEV)}<td class="n" data-v="{dv}">{d}</td>'
                     f'<td class="n" data-v="{v[0]}">{intero(v[0])}</td><td class="n" data-v="{v[1]}">{intero(v[1])}</td></tr>')
    return ('<div class="tab compatta"><table class="ord"><thead><tr>' + th_ord("Schengen country", False, "ascending") +
            th_ord(f"Multiple-entry {A1}") + th_ord(f"{A0}") + th_ord("Change") + th_ord("Visas issued") + th_ord("Multiple-entry visas") +
            f'</tr></thead><tbody>{"".join(righe)}</tbody></table></div>')


def sezione_mev(p, rel):
    """Riquadro "Multiple-entry Schengen visas issued in <Paese>" delle pagine dei rifiuti per Paese."""
    nome = nome_paese(p)
    v1, v0 = MEV_PAESE[A1][p], MEV_PAESE[A0].get(p)
    q1, q0 = quota_mev(v1), quota_mev(v0)
    ok, sotto = mev_stati_paese(p)
    if len(ok) >= 2:
        kpi = (f'<div><b>{pct(q0)}</b><span>in {A0}</span></div><div><b>{punti(q1, q0) if q0 is not None else "–"}</b><span>change on {A0}</span></div>'
               f'<div><b>{escape(ok[0][0])}</b><span>highest share: {pct(quota_mev(ok[0][1]))}</span></div>'
               f'<div><b>{escape(ok[-1][0])}</b><span>lowest share: {pct(quota_mev(ok[-1][1]))}</span></div>')
        frase = (f'Among the {len(ok)} Schengen countries that issued at least {intero(SOGLIA_MEV)} visas in {escape(art(nome))} in {A1}, '
                 f'<strong>{escape(ok[0][0])}</strong> gave the highest share of multiple-entry visas ({pct(quota_mev(ok[0][1]))}) and '
                 f'<strong>{escape(ok[-1][0])}</strong> the lowest ({pct(quota_mev(ok[-1][1]))}).')
    else:
        kpi = (f'<div><b>{pct(q0)}</b><span>in {A0}</span></div><div><b>{punti(q1, q0) if q0 is not None else "–"}</b><span>change on {A0}</span></div>'
               f'<div><b>{intero(v1[0])}</b><span>uniform visas issued</span></div><div><b>{intero(v1[1])}</b><span>multiple-entry visas</span></div>')
        frase = (f'Fewer than two Schengen countries issued {intero(SOGLIA_MEV)} or more visas in {escape(art(nome))} in {A1}, so there is no comparison between countries.')
    tab = ""
    if ok:
        tab = (f'<p class="small">Schengen countries that issued at least {intero(SOGLIA_MEV)} uniform visas in {escape(art(nome))} in {A1}, from the highest share of multiple-entry visas. '
               f'Tap a column heading to sort. "Change" is in percentage points; * fewer than {intero(SOGLIA_MEV)} visas issued in {A0}.'
               + (f' Not shown (fewer than {intero(SOGLIA_MEV)} visas issued): {escape(", ".join(sotto))}.' if sotto else "") + '</p>'
               f'{tabella_mev_paese(ok, rel)}\n{fonte_ue_p(A1, A0)}')
    return f"""<h2 id="multiple-entry">Multiple-entry Schengen visas issued in {escape(art(nome))} ({A1})</h2>
<section class="card summary" aria-label="Multiple-entry visas">
<div class="s-top">{ico("calendar")}<span>Multiple-entry visas</span><span>{escape(nome)} · {A1}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Schengen visas issued in {escape(art(nome))} · {A1}</span><span class="sr">: </span><strong>{pct(q1)}</strong> were multiple-entry visas ({intero(v1[1])} of {intero(v1[0])} uniform visas issued)</p>
<div class="kpi">{kpi}</div>
<p class="lead" style="margin-top:6px">{frase} All Schengen visas issued worldwide in {A1}: {pct(quota_mev(MEV_TOT[A1]))} multiple-entry. <a href="{rel}{PERCORSO_MEV}">Multiple-entry Schengen visas by country and by place of application</a>.</p>
{fonte_ue_p(A1, A0)}
</div></section>
{tab}
<p class="avviso"><strong>What this share means, and what it does not.</strong> {COSA_MEV} {LIMITI_MEV}</p>"""


def pagina_rif_mev():
    rel = "../../"
    v1, v0 = MEV_TOT[A1], MEV_TOT[A0]
    q1, q0 = quota_mev(v1), quota_mev(v0)
    stati = sorted(STATI_UE, key=lambda s: (-quota_mev(MEV_STATO[A1][s]), s))
    alto, basso = stati[0], stati[-1]
    f1 = F_UE[A1]
    righe_s = []
    for s in stati:
        v, w = MEV_STATO[A1][s], MEV_STATO[A0].get(s)
        d, dv = punti_mev(v, w)
        righe_s.append(f'<tr><td><a href="../schengen/{SLUG_STATO[s]}/">{escape(s)}</a></td>{cella_mev(quota_mev(v))}{cella_mev(quota_mev(w))}'
                       f'<td class="n" data-v="{dv}">{d}</td><td class="n" data-v="{v[0]}">{intero(v[0])}</td><td class="n" data-v="{v[1]}">{intero(v[1])}</td></tr>')
    paesi = sorted(PAESI_RIF, key=lambda p: (-quota_mev(MEV_PAESE[A1][p]), p))
    righe_p = []
    for p in paesi:
        v, w = MEV_PAESE[A1][p], MEV_PAESE[A0].get(p)
        d, dv = punti_mev(v, w)
        ok, _ = mev_stati_paese(p)
        cima = (f'{escape(ok[0][0])} ({pct(quota_mev(ok[0][1]))})' if len(ok) >= 2 else "–")
        righe_p.append(f'<tr><td><a href="../{SLUG_RIF[p]}/#multiple-entry">{escape(nome_paese(p))}</a></td>{cella_mev(quota_mev(v))}{cella_mev(quota_mev(w))}'
                       f'<td class="n" data-v="{dv}">{d}</td><td class="n" data-v="{v[0]}">{intero(v[0])}</td><td class="n" data-v="{v[1]}">{intero(v[1])}</td><td style="white-space:nowrap">{cima}</td></tr>')
    top = [p for p in sorted(PAESI_RIF, key=lambda p: -MEV_PAESE[A1][p][0])[:10]]
    piu, meno = paesi[:3], paesi[-3:][::-1]
    elenco = lambda xs: ", ".join(f"{escape(art(nome_paese(x)))} ({pct(quota_mev(MEV_PAESE[A1][x]))})" for x in xs[:-1]) + \
        f" and {escape(art(nome_paese(xs[-1])))} ({pct(quota_mev(MEV_PAESE[A1][xs[-1]]))})"

    def q_paese(p):
        v, w = MEV_PAESE[A1][p], MEV_PAESE[A0].get(p)
        ok, _ = mev_stati_paese(p)
        extra = (f" Among Schengen countries with at least {intero(SOGLIA_MEV)} visas issued there, {ok[0][0]} had the highest share ({pct(quota_mev(ok[0][1]))}) "
                 f"and {ok[-1][0]} the lowest ({pct(quota_mev(ok[-1][1]))}).") if len(ok) >= 2 else ""
        return (f"In {A1}, Schengen consulates in {art(nome_paese(p))} issued {intero(v[1])} multiple-entry visas out of {intero(v[0])} uniform visas: {pct(quota_mev(v))} "
                f"({pct(quota_mev(w))} in {A0}).{extra} The figures count visas issued in {art(nome_paese(p))}, whatever the applicant's nationality. "
                f'Details: <a href="../{SLUG_RIF[p]}/#multiple-entry">{escape(nome_paese(p))} page</a>.')

    de, ch = MEV_STATO[A1]["Germany"], MEV_STATO[A1]["Switzerland"]
    domande = [
        ("Which Schengen country gives multiple-entry visas most often?",
         f"In {A1}, {alto} had the highest share: {pct(quota_mev(MEV_STATO[A1][alto]))} of the {intero(MEV_STATO[A1][alto][0])} uniform visas it issued were multiple-entry visas. "
         f"Next came {', '.join(f'{s} ({pct(quota_mev(MEV_STATO[A1][s]))})' for s in stati[1:4])}. The lowest share was {basso}'s ({pct(quota_mev(MEV_STATO[A1][basso]))}). "
         f"Each country's figure mixes applicants from many places, so compare countries in the place where you apply (see the table by place of application)."),
        ("What does a multiple-entry Schengen visa mean?",
         f"The European Commission says a multiple-entry visa allows several visits to the Schengen area for as long as the visa is valid, while a single-entry visa allows you to enter the Schengen area once. "
         f"Each visit is a short stay of up to 90 days in any 180-day period. It is not a long-stay visa or a residence permit."),
        ("Multiple-entry vs single-entry Schengen visa: what do the statistics count?",
         f"The Commission's file gives the total number of uniform visas issued and, within it, the number of multiple-entry visas (MEVs). The rest are single-entry or double-entry visas "
         f'(<a href="{URL_METADATI_UE}" rel="noopener">Commission metadata</a>). Visas with limited territorial validity are counted separately and are not in these shares.'),
        ("How long is a multiple-entry Schengen visa valid?",
         f"The statistics do not say. The Commission's file records whether a visa allows multiple entries, not its validity, so we cannot tell how many were valid for a few months, one year or several years. "
         f"The validity is printed on each visa and is decided by the consulate."),
        ("Can I get a multiple-entry Schengen visa the first time I apply?",
         f"These figures cannot answer that: they do not record whether applicants had visited the Schengen area before. The consulate decides the number of entries and the validity of each visa. "
         f"What the figures show is that {pct(q1)} of all uniform visas issued in {A1} were multiple-entry visas."),
        ("Multiple-entry Schengen visa requirements: is the passport rule different?",
         f"Yes, on one point. The European Commission says the passport's expiry date should be at least 3 months after you leave the Schengen area, and for multiple-entry visas at least 3 months after your departure from the last country visited "
         f'(<a href="{URL_COMMISSIONE_DOMANDA}" rel="noopener">Applying for a Schengen visa</a>, checked on {data_lunga(DATA_COMMISSIONE_MEV)}). Check the full list of documents with the consulate.'),
        ("Multiple-entry Schengen visa for Indians: how many were issued in India?", q_paese("INDIA")),
        ("Multiple-entry Schengen visa for Pakistani applicants: how many were issued in Pakistan?", q_paese("PAKISTAN")),
        ("How often do Germany and Switzerland give multiple-entry Schengen visas?",
         f"In {A1}, {pct(quota_mev(de))} of the {intero(de[0])} uniform visas issued by Germany were multiple-entry visas, and {pct(quota_mev(ch))} of the {intero(ch[0])} issued by Switzerland. "
         f"The share in the place where you apply can be very different: see the country pages."),
    ]
    corpo = f"""<section class="hero">{h1_diviso(f"Multiple-entry Schengen visas in {A1}: which countries issue them most often")}
<p class="lead">In {A1}, <strong>{pct(q1)}</strong> of the {intero(v1[0])} uniform Schengen visas issued were multiple-entry visas ({intero(v1[1])}), according to the European Commission's <a href="{escape(f1["url"])}" rel="noopener">Visa statistics for consulates {A1}</a> (file {escape(f1["file"])}, downloaded on {data_lunga(f1["scaricato_il"])}); {escape(alto)} issued the highest share ({pct(quota_mev(MEV_STATO[A1][alto]))}) and {escape(basso)} the lowest ({pct(quota_mev(MEV_STATO[A1][basso]))}).</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("calendar")}<span>Multiple-entry Schengen visas</span><span>{A1}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">All Schengen countries · all consulates · {A1}</span><span class="sr">: </span><strong>{pct(q1)}</strong> of uniform visas issued were multiple-entry ({intero(v1[1])} of {intero(v1[0])})</p>
<div class="kpi"><div><b>{pct(q0)}</b><span>in {A0} ({intero(v0[1])} of {intero(v0[0])})</span></div><div><b>{punti(q1, q0)}</b><span>change on {A0}</span></div><div><b>{escape(alto)}</b><span>highest share: {pct(quota_mev(MEV_STATO[A1][alto]))}</span></div><div><b>{escape(basso)}</b><span>lowest share: {pct(quota_mev(MEV_STATO[A1][basso]))}</span></div></div>
<p class="lead" style="margin-top:6px">By place of application ({len(PAESI_RIF)} countries with at least {intero(SOGLIA_PAGINA)} applications): highest shares in {elenco(piu)}; lowest in {elenco(meno)}.</p>
{fonte_ue_p(A1, A0)}
</div></section>
<p class="avviso"><strong>Statistics, not advice.</strong> {COSA_MEV} {LIMITI_MEV}</p>
{AD}
<h2>Multiple-entry visas by Schengen country ({A1})</h2>
<p class="small">All {len(STATI_UE)} Schengen countries that process visas, from the highest share of multiple-entry visas among the uniform visas they issued. Tap a column heading to sort. "Change" is in percentage points on {A0}.</p>
<div class="tab compatta"><table class="ord"><thead><tr>{th_ord("Schengen country", False, "ascending")}{th_ord(f"Multiple-entry {A1}")}{th_ord(f"{A0}")}{th_ord("Change")}{th_ord("Visas issued")}{th_ord("Multiple-entry visas")}</tr></thead><tbody>{"".join(righe_s)}</tbody></table></div>
{fonte_ue_p(A1, A0)}
<h2>Multiple-entry visas by place of application ({A1})</h2>
<p class="small">The {len(PAESI_RIF)} countries with at least {intero(SOGLIA_PAGINA)} Schengen visa applications in {A1}, from the highest share. The last column is the Schengen country with the highest share among those that issued at least {intero(SOGLIA_MEV)} visas there. Tap a column heading to sort, or type to filter.</p>
<p class="filtro"><label><span class="sr">Filter countries</span><input type="search" placeholder="Filter: e.g. India" data-filtro="t-mev" autocomplete="off"></label></p>
<div class="tab compatta"><table class="ord" id="t-mev"><thead><tr>{th_ord("Applied in", False, "ascending")}{th_ord(f"Multiple-entry {A1}")}{th_ord(f"{A0}")}{th_ord("Change")}{th_ord("Visas issued")}{th_ord("Multiple-entry visas")}{th_ord("Highest share", False, "ascending")}</tr></thead><tbody>{"".join(righe_p)}</tbody></table></div>
{fonte_ue_p(A1, A0)}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>What these figures do not say</h2>
<ul class="testo">
<li><strong>Where the visa was issued, not your passport.</strong> The Commission counts visas by the country where the application was made: the figures for "India" are visas issued in India, including visas issued to residents of other nationalities.</li>
<li><strong>Share of multiple-entry visas</strong> = multiple-entry uniform visas issued ÷ all uniform visas issued (multiple-entry visas included), the same as the "Share of MEVs" column in the Commission's file. Refused applications are not in the share: for those, see the <a href="../">refusal rates</a>.</li>
<li><strong>No validity length.</strong> The file does not say how long each multiple-entry visa was valid for.</li>
<li><strong>Minimum {intero(SOGLIA_MEV)} visas.</strong> On the country pages we compare Schengen countries only where they issued at least {intero(SOGLIA_MEV)} visas in that place; smaller numbers swing too much from year to year.</li>
<li><strong>Where to apply.</strong> You must apply to the country of your main destination (or, for equal stays, the first you enter): see the <a href="{URL_COMMISSIONE_DOMANDA}" rel="noopener">European Commission page on applying for a Schengen visa</a>.</li></ul>
<h2>Busiest places of application</h2>
<div class="griglia">{''.join(f'<a href="../{SLUG_RIF[x]}/#multiple-entry"><span class="ic">{ico("passport")}</span><span>Multiple-entry visas issued in {escape(art(nome_paese(x)))}<small>{pct(quota_mev(MEV_PAESE[A1][x]))} of {intero(MEV_PAESE[A1][x][0])} visas in {A1}</small></span></a>' for x in top)}</div>
{box_assicurazione(rel)}
<h2>Official sources</h2>
<ul class="fonti">
<li><a href="{escape(f1["url"])}" rel="noopener">Visa statistics for consulates {A1}</a> – European Commission, XLSX ({escape(f1["file"])}), downloaded on {data_lunga(f1["scaricato_il"])}; columns "Total uniform visas issued (including MEV)" and "Multiple entry uniform visas (MEVs) issued"</li>
<li><a href="{escape(F_UE[A0]["url"])}" rel="noopener">Visa statistics for consulates {A0}</a> – European Commission, XLSX, downloaded on {data_lunga(F_UE[A0]["scaricato_il"])}</li>
<li><a href="{URL_METADATI_UE}" rel="noopener">Visa statistics: quality and metadata reporting</a> – European Commission, PDF, read on {data_lunga(DATA_METADATI_UE)}</li>
<li><a href="{URL_COMMISSIONE_DOMANDA}" rel="noopener">Applying for a Schengen visa</a> – European Commission, checked on {data_lunga(DATA_COMMISSIONE_MEV)}</li></ul>
<p class="small">© European Union. Reuse of Commission data is allowed under the <a href="https://commission.europa.eu/legal-notice_en" rel="noopener">Commission's reuse policy</a> (CC BY 4.0); the shares and changes on this page are our own calculations from the files above.</p>
<p><a href="../">Schengen visa refusal rates by country, {A1}</a> · <a href="../uk/">UK visa refusal rates by nationality</a> · <a href="{rel}">Visa income calculator</a></p>"""
    ld = [ld_faq(domande),
          ld_dataset(f"Multiple-entry Schengen visas by country, {A1}",
                     "Share of multiple-entry visas among uniform Schengen visas issued, by Schengen country and by country of application, recalculated from the European Commission's visa statistics for consulates.",
                     PERCORSO_MEV, [F_UE[A1]["url"], F_UE[A0]["url"]], f"{A0}/{A1}", "https://creativecommons.org/licenses/by/4.0/")]
    titolo = f"Multiple-entry Schengen visa: which countries give them most ({A1})"
    descr = (f"Official {A1} figures: {pct(q1)} of uniform Schengen visas issued were multiple-entry. {alto} had the highest share ({pct(quota_mev(MEV_STATO[A1][alto]))}), "
             f"{basso} the lowest. By Schengen country and by place of application, from the European Commission.")
    pagina(PERCORSO_MEV, titolo, descr, corpo, ordina=True, jsonld_extra=ld,
           briciole=[("Visa refusal rates", SEZ), ("Multiple-entry Schengen visas", PERCORSO_MEV)])


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


# Irlanda (30/10/2026): numeri PPS (PPSN) assegnati per nazionalità e mese (Department of Social Protection, CC BY 4.0, raccolta/ppsn.py).
# La pagina "nazionalità × Irlanda" esiste se i primi permessi Eurostat OPPURE i PPS assegnati nell'ultimo anno intero sono almeno SOGLIA_TR.
PPS = json.loads((DATI / "ppsn.json").read_text(encoding="utf-8"))
PPS_NAZ = PPS["nazionalita"]
PPS_MESI = PPS["mesi"]
PPS_ULTIMO = PPS_MESI[-1]                                           # es. 2026-09
PPS_YTD = PPS_ULTIMO[:4] if PPS_ULTIMO[5:] != "12" else None         # anno in corso (se non è finito)
PPS_PIENO = str(int(PPS_ULTIMO[:4]) - 1) if PPS_YTD else PPS_ULTIMO[:4]   # ultimo anno intero (es. 2025)
F_PPS = PPS["fonti"]


def pps_anno(c, a):
    x = PPS_NAZ.get(c)
    return x["anni"].get(a) if x else None


def pps_periodo(c, anno, fino=None):
    """Somma dei mesi da gennaio al mese 'fino' (MM) dell'anno, dal file mensile."""
    fino = fino or PPS_ULTIMO[5:]
    x = PPS_NAZ.get(c)
    if not x:
        return None
    v = [x["mesi"].get(f"{anno}-{m:02d}") for m in range(1, int(fino) + 1)]
    return None if any(y is None for y in v) else sum(v)


PPS_OK = [c for c in NAZ_TR if (pps_anno(c, PPS_PIENO) or 0) >= SOGLIA_TR]
COPPIE_TR = {c: sorted([d for d in DEST_TR if (val_tr(c, d, Y1) or 0) >= SOGLIA_TR or (d == "ireland" and c in PPS_OK)],
                       key=lambda d: -(val_tr(c, d, Y1) or 0)) for c in NAZ_TR}


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
    if d == "ireland" and c in PPS_OK:
        piccolo = f"{intero(pps_anno(c, PPS_PIENO))} PPS numbers in {PPS_PIENO}"
    else:
        piccolo = f"{intero(val_tr(c, d, Y1))} {misura} in {Y1}"
    return (f'<a href="{rel_sez}{slug}/{d}/">{icona}<span>{escape(testo)}'
            f'<small>{piccolo}</small></span></a>')


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


# ---------- pagina nazionalità × Irlanda (PPS assegnati, Department of Social Protection; più i primi permessi Eurostat), 30/10/2026
def fonte_pps_p(extra=""):
    m = F_PPS["mensile"]
    a = F_PPS["annuale"]
    return (f'<p class="fonte">Source: Department of Social Protection (Ireland), <a href="{escape(F_PPS["pagina"]["url"])}" rel="noopener">{escape(F_PPS["pagina"]["titolo"])}</a> '
            f'(gov.ie, page updated on {data_lunga(F_PPS["pagina"]["aggiornata"])}): <a href="{escape(m["url"])}" rel="noopener">PPSN registrations by year, month and country</a> and '
            f'<a href="{escape(a["url"])}" rel="noopener">by year and country</a> (CSV, downloaded on {data_lunga(m["scaricato_il"])}), data to {mese_testo(PPS_ULTIMO)}. {extra}'
            f'Licence: <a href="{escape(F_PPS["scheda"]["licenza_url"])}" rel="license noopener">{escape(F_PPS["scheda"]["licenza"])}</a> '
            f'(<a href="{escape(F_PPS["scheda"]["url"])}" rel="noopener">data.gov.ie</a>).</p>')


def periodo_pps():
    return f"January–{MESI[int(PPS_ULTIMO[5:]) - 1]}"


def cosa_pps(c):
    _, X, cit, _, _, _ = NAZ_TR[c]
    S = F_PPS["servizio"]
    return (f'<section class="card cosa" aria-labelledby="cosa-h"><h2 id="cosa-h">What this number is, and what it is not</h2><ul class="testo">'
            f'<li><strong>It is</strong> the number of PPS numbers (Personal Public Service numbers) that Ireland\'s Department of Social Protection allocated to people with '
            f'{escape(cit.replace(" citizens", ""))} nationality, by month and year. GOV.IE says a PPS number "{escape(S["frasi"][0])}".</li>'
            f'<li><strong>It is not</strong> a count of people who arrived: the online service is open to "{escape(S["frasi"][1])}", some people get a number before or long after they arrive, '
            f'and some never move or leave again (<a href="{escape(S["url"])}" rel="noopener">GOV.IE, {escape(S["titolo"])}</a>, read on {data_lunga(S["letta_il"])}).</li>'
            f'<li><strong>It leaves out</strong> {escape(X)} who already had a PPS number (for example from an earlier stay), and it counts each person by the nationality recorded by the Department.</li>'
            f'<li><strong>It is not</strong> the number of {escape(X)} living in Ireland, which is much larger. Nothing on this page counts residents.</li></ul></section>')


def tabella_pps_mesi(c, cit):
    anni = sorted({m[:4] for m in PPS_MESI})
    x = PPS_NAZ[c]["mesi"]
    righe = []
    for i in range(12):
        celle = "".join(cella_n(x.get(f"{a}-{i + 1:02d}")) for a in anni)
        righe.append(f'<tr><th scope="row">{MESI[i]}</th>{celle}</tr>')
    tot = "".join(cella_n(sum(v for k, v in x.items() if k.startswith(a) and v is not None)) for a in anni)
    righe.append(f'<tr class="tot-r"><th scope="row">Total</th>{tot}</tr>')
    intest = "".join(f'<th class="n" scope="col">{a}{" (to " + MESI[int(PPS_ULTIMO[5:]) - 1][:3] + ")" if a == PPS_YTD else ""}</th>' for a in anni)
    return (f'<div class="tab compatta"><table id="t-pps-mesi"><caption class="sr">PPS numbers allocated to {escape(cit)} by month, {anni[0]}–{anni[-1]}</caption>'
            f'<thead><tr><th scope="col">Month</th>{intest}</tr></thead><tbody>{"".join(righe)}</tbody></table></div>')


def tabella_pps_anni(c, cit):
    righe = []
    anni = PPS["anni"]
    for a in reversed(anni):
        v, v0 = pps_anno(c, a), pps_anno(c, str(int(a) - 1))
        tutti = PPS["tutte"]["anni"].get(a)
        quota = f'{v / tutti * 100:.1f}%' if v is not None and tutti else "–"
        nome = f"{a} ({periodo_pps()})" if a == PPS_YTD else a
        cambio = cella_var(v, v0) if a != PPS_YTD else '<td class="n">–</td>'
        righe.append(f'<tr><td>{nome}</td>{cella_n(v)}{cambio}<td class="n">{quota}</td></tr>')
    return (f'<div class="tab compatta"><table id="t-pps-anni"><caption class="sr">PPS numbers allocated to {escape(cit)} by year, {anni[0]}–{anni[-1]}</caption>'
            f'<thead><tr><th scope="col">Year</th><th class="n" scope="col">PPS numbers</th><th class="n" scope="col">Change</th><th class="n" scope="col">Share of all PPS numbers</th></tr></thead>'
            f'<tbody>{"".join(righe)}</tbody></table></div>')


def pagina_tr_ie(c):
    slug, X, cit, paese, _, parola = NAZ_TR[c]
    d = "ireland"
    rel = "../../../"
    percorso = f"{SEZ_TR}{slug}/{d}/"
    fino = PPS_ULTIMO[5:]
    n_ytd = pps_periodo(c, PPS_YTD) if PPS_YTD else None
    n_ytd0 = pps_periodo(c, PPS_PIENO, fino) if PPS_YTD else None
    n1, n0 = pps_anno(c, PPS_PIENO), pps_anno(c, str(int(PPS_PIENO) - 1))
    tutti1 = PPS["tutte"]["anni"][PPS_PIENO]
    per = f"{periodo_pps()} {PPS_YTD}" if PPS_YTD else PPS_PIENO
    per0 = f"{periodo_pps()} {PPS_PIENO}"
    r1 = riga_eu(c, "IE", Y1)
    t1 = r1[0] if r1 else None
    s1 = segni_eu(c, "IE", Y1)
    agg = data_lunga(F_PPS["pagina"]["aggiornata"])
    if PPS_YTD:
        risposta = (f"Ireland's Department of Social Protection allocated <strong>{intero(n_ytd)}</strong> PPS numbers to {escape(cit)} from {per.replace('–', ' to ')}, "
                    f"and <strong>{intero(n1)}</strong> in {PPS_PIENO} (gov.ie, file updated on {agg}). ")
        confronto = (f"From {per0.replace('–', ' to ')} the figure was {intero(n_ytd0)}, so the change on the same months of {PPS_PIENO} is {variazione(n_ytd, n_ytd0)}."
                     if n_ytd0 else "")
    else:
        risposta = (f"Ireland's Department of Social Protection allocated <strong>{intero(n1)}</strong> PPS numbers to {escape(cit)} in {PPS_PIENO} (gov.ie, file updated on {agg}). ")
        confronto = ""
    prudente = "These are the most recent official monthly figures by nationality, but PPS numbers allocated are not the same as people who moved to Ireland: see what the number is and is not, below."
    # Eurostat (primi permessi)
    if r1 and t1 is not None and t1 >= SOGLIA_POCO:
        righe_m = "".join(f'<tr><td>{nome}</td>{cella_n(r1[i], segno_html(s1, i))}<td class="n">{f"{r1[i] / t1 * 100:.1f}%" if r1[i] is not None and t1 else "–"}</td></tr>'
                          for i, nome in MOTIVI_TR)
        righe_m += f'<tr class="tot-r"><td>All reasons</td>{cella_n(t1, segno_html(s1, 0))}<td class="n">100%</td></tr>'
        righe_s = "".join(f'<tr><td>{a}</td>{cella_n(riga_eu(c, "IE", a)[0], segno_html(segni_eu(c, "IE", a), 0))}</tr>' for a in anni_naz(c) if riga_eu(c, "IE", a))
        sez_eu = (f'<h2 id="permits">First residence permits issued by Ireland to {escape(cit)} ({Y1})</h2>'
                  f'<p>Ireland issued <strong>{intero(t1)}</strong> first residence permits to {escape(cit)} in {Y1}, according to Eurostat (data updated on {data_lunga(F_ES["aggiornato_il"])}). '
                  f'{frase_cambio(t1, (riga_eu(c, "IE", Y0) or [None])[0], Y0)} {motivi_frase(r1)} This is a different measure from PPS numbers: never add the two together.</p>'
                  f'<div class="tab compatta motivi"><table><caption class="sr">First residence permits issued by Ireland to {escape(cit)}, by reason, {Y1}</caption>'
                  f'<thead><tr><th scope="col">Reason</th><th class="n" scope="col">{Y1}</th><th class="n" scope="col">Share</th></tr></thead><tbody>{righe_m}</tbody></table></div>'
                  f'{fonte_es_p()}'
                  f'<div class="tab compatta"><table><caption class="sr">First residence permits issued by Ireland to {escape(cit)} by year</caption>'
                  f'<thead><tr><th scope="col">Year</th><th class="n" scope="col">First residence permits</th></tr></thead><tbody>{righe_s}</tbody></table></div>'
                  f'{fonte_es_p("Eurostat revises past years when countries correct their data. ")}'
                  + (f'<p class="small">{nota_segni(c, "IE", anni_naz(c))}</p>' if nota_segni(c, "IE", anni_naz(c)) else ""))
    else:
        sez_eu = (f'<h2 id="permits">First residence permits</h2><p>Ireland issued {intero(t1) if t1 is not None else "no"} first residence permits to {escape(cit)} in {Y1} (Eurostat, '
                  f'data updated on {data_lunga(F_ES["aggiornato_il"])}). Ireland and the UK are in the <a href="https://www.irishimmigration.ie/at-the-border/common-travel-area/" rel="noopener">Common Travel Area</a>, '
                  f'within which "Irish and British citizens can travel freely" (Irish Immigration Service Delivery), so for British citizens this page relies on PPS numbers.</p>' if c == "UK" else "")
    domande = [
        (f"How many {parola} moved to Ireland in {PPS_YTD or PPS_PIENO}?",
         (f"There is no count of moves. The most recent official figure: Ireland allocated {intero(n_ytd)} PPS numbers to {cit} from {per.replace('–', ' to ')}"
          + (f" ({variazione(n_ytd, n_ytd0)} on the same months of {PPS_PIENO})" if n_ytd0 else "") + f", according to the Department of Social Protection (data to {mese_testo(PPS_ULTIMO)})."
          if PPS_YTD else f"Ireland allocated {intero(n1)} PPS numbers to {cit} in {PPS_PIENO}.")),
        (f"How many {parola} moved to Ireland in {PPS_PIENO}?",
         f"Ireland allocated {intero(n1)} PPS numbers to {cit} in {PPS_PIENO} ({variazione(n1, n0)} on {int(PPS_PIENO) - 1}), {n1 / tutti1 * 100:.1f}% of all PPS numbers allocated that year."
         + (f" Separately, Ireland issued {intero(t1)} first residence permits to {cit} in {Y1} (Eurostat)." if t1 and t1 >= SOGLIA_POCO else "")),
        (f"How many {parola} are in Ireland?",
         "This page does not count residents. PPS numbers and residence permits are new allocations in a period; people who have lived in Ireland for years, "
         "or who got their PPS number earlier, are not in these figures."),
        ("Is a PPS number the same as a visa or a residence permit?",
         "No. GOV.IE describes the PPS number as a number that helps you access social welfare benefits, public services and information in Ireland. Visas and residence permits are separate documents."),
    ]
    altri = [x for x in sorted(PPS_OK, key=lambda x: -(pps_anno(x, PPS_PIENO) or 0)) if x != c and "ireland" in COPPIE_TR[x]]
    griglia = "".join(f'<a href="../../{NAZ_TR[x][0]}/ireland/"><span class="ic">{ico("passport")}</span><span>{escape(NAZ_TR[x][1])}'
                      f'<small>{intero(pps_anno(x, PPS_PIENO))} PPS numbers in {PPS_PIENO}</small></span></a>' for x in altri)
    kpi = [(intero(n_ytd0) if n_ytd0 is not None else "–", f"{per0}"), (variazione(n_ytd, n_ytd0) if n_ytd0 else "–", "change on the same months"),
           (intero(n1), f"in {PPS_PIENO}, full year"), (f"{n1 / tutti1 * 100:.1f}%", f"of all PPS numbers allocated in {PPS_PIENO}")]
    corpo = f"""<section class="hero"><h1>How many {escape(X)} moved to Ireland in {PPS_YTD or PPS_PIENO}? PPS numbers by month</h1>
<p class="lead">{risposta}{confronto} {prudente}</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{bandiera("Ireland")}<span>PPS numbers allocated</span><span>{escape(cit)} · {per}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Ireland · {escape(cit)} · {per}</span><span class="sr">: </span><strong>{intero(n_ytd if PPS_YTD else n1)}</strong> PPS numbers</p>
<div class="kpi">{"".join(f'<div><b>{v}</b><span>{escape(e)}</span></div>' for v, e in kpi)}</div>
{fonte_pps_p()}
</div></section>
{cosa_pps(c)}
{AD}
<h2>PPS numbers allocated to {escape(cit)}, month by month</h2>
<p class="small">Each cell is the number of PPS numbers allocated in that month. The Department publishes monthly figures by nationality from January {PPS_MESI[0][:4]}.</p>
{tabella_pps_mesi(c, cit)}
{fonte_pps_p()}
<h2>PPS numbers allocated to {escape(cit)}, year by year ({PPS["anni"][0]}–{PPS["anni"][-1]})</h2>
{tabella_pps_anni(c, cit)}
{fonte_pps_p("Yearly figures are from the yearly file; the share is of all PPS numbers allocated in the year, Irish citizens included. ")}
{f'<p class="small">In 2020 the yearly file lists British citizens under two world regions (European Union and Europe excluding EU); the figure here is the sum of the two rows.</p>' if c == "UK" else ''}
{sez_eu}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>Visas and statistics for Ireland on this site</h2>
{lista_link(link_sito_dest(d, rel) + link_sito_naz(c, rel))}
{f'<h2>Other nationalities in Ireland: PPS numbers in {PPS_PIENO}</h2><div class="griglia">{griglia}</div>' if griglia else ''}
<p><a href="../">How many {escape(X)} moved abroad</a> · <a href="../../">Who moved where: all nationalities</a> · <a href="{rel}">Visa income calculator</a></p>"""
    anno_t = PPS_YTD or PPS_PIENO
    titolo = titolo_breve([f"How many {X} moved to Ireland in {anno_t}? PPS numbers by month",
                           f"How many {X} moved to Ireland in {anno_t}? Monthly PPS data", f"{X} moving to Ireland {anno_t}: PPS numbers by month",
                           f"{X} moving to Ireland {anno_t}: PPS numbers"])
    descr = (f"{intero(n_ytd if PPS_YTD else n1)} PPS numbers allocated to {cit} in Ireland ({per}); {intero(n1)} in {PPS_PIENO}. Month by month since {PPS_MESI[0][:4]}, "
             f"year by year since {PPS['anni'][0]}. Department of Social Protection data.")
    ld = ld_dataset(f"PPS numbers allocated to {cit} in Ireland, {PPS['anni'][0]}-{PPS_ULTIMO}", "Department of Social Protection PPSN registrations by nationality, by month and year.",
                    percorso, [F_PPS["mensile"]["url"], F_PPS["annuale"]["url"]], f"{PPS['anni'][0]}/{PPS_ULTIMO}", F_PPS["scheda"]["licenza_url"])
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande), ld],
           briciole=[("Who moved where", SEZ_TR), (X, f"{SEZ_TR}{slug}/"), ("Ireland", percorso)])


def blocco_pps_hub(c):
    """Riquadro 'Ireland: PPS numbers by month' nella pagina della nazionalità (link alla pagina Irlanda se esiste)."""
    if c not in PPS_NAZ:
        return ""
    _, X, cit = NAZ_TR[c][:3]
    n_ytd = pps_periodo(c, PPS_YTD) if PPS_YTD else None
    n1 = pps_anno(c, PPS_PIENO)
    link = ("ireland/" if "ireland" in COPPIE_TR[c] else None)
    testo = (f"Ireland also publishes a monthly count by nationality: {intero(n_ytd)} PPS numbers allocated to {escape(cit)} from {periodo_pps().replace('–', ' to ')} {PPS_YTD}, "
             f"{intero(n1)} in {PPS_PIENO} (Department of Social Protection, data to {mese_testo(PPS_ULTIMO)}). A PPS number is not a count of arrivals."
             if PPS_YTD else f"Ireland allocated {intero(n1)} PPS numbers to {escape(cit)} in {PPS_PIENO} (Department of Social Protection).")
    return (f'<section class="card" id="ireland-pps"><h2 style="margin-top:0">{ico("calendar")} Ireland: PPS numbers by month</h2><p>{testo}</p>'
            + (f'<p><a href="{link}">How many {escape(X)} moved to Ireland: PPS numbers month by month</a></p>' if link else
               f'<p class="small">Fewer than {intero(SOGLIA_TR)} in {PPS_PIENO}: no separate page.</p>')
            + fonte_pps_p() + '</section>')


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
    if c in PPS_NAZ and PPS_YTD:
        domande.append((f"How many {parola} moved to Ireland in {PPS_YTD}?",
                        f"Ireland allocated {intero(pps_periodo(c, PPS_YTD))} PPS numbers to {cit} from {periodo_pps().replace('–', ' to ')} {PPS_YTD} "
                        f"(Department of Social Protection); PPS numbers allocated are not the same as people who moved. "
                        + ('<a href="ireland/">Month by month</a>.' if "ireland" in COPPIE_TR[c] else "")))
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
{blocco_pps_hub(c)}
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
                     f'{cella_n(ca["anni"][Y1] if ca else None)}{cella_n(sum(uk["anni"][Y1]) if uk else None)}{cella_n(pps_anno(c, PPS_PIENO))}</tr>')
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
<div class="tab compatta"><table class="ord larga"><caption class="sr">Moves abroad by nationality, {Y1}: EU first residence permits, EFTA first permits, new permanent residents of Canada, UK visas granted</caption><thead><tr>{th_ord("Nationality", False, "ascending")}{th_ord(f"EU {Y1}")}{th_ord(f"EU {Y0}")}{th_ord("Change")}{th_ord("EFTA")}{th_ord("Canada")}{th_ord("UK")}{th_ord(f"Ireland PPS {PPS_PIENO}")}</tr></thead><tbody>{"".join(righe)}</tbody></table></div>
{fonte_es_p()}
{fonte_pr_p()}
{fonte_ukv_p()}
{fonte_pps_p()}
{f'<p class="small">b = in {Y1} Eurostat marks a break in the time series for a country that issued at least 10% of these permits: ' + "; ".join(rotture_idx) + f'. Part of the change from {Y0} may come from that.</p>' if rotture_idx else ''}
<h2>Nationalities</h2>
<div class="griglia">{schede}</div>
<h2 id="ireland">Ireland: PPS numbers by nationality, month by month</h2>
<p class="lead">Ireland's Department of Social Protection publishes every month how many PPS numbers it allocated to each nationality (data to {mese_testo(PPS_ULTIMO)}, page updated on {data_lunga(F_PPS["pagina"]["aggiornata"])}). These are the most recent official monthly figures by nationality, but PPS numbers allocated are not the same as people who moved to Ireland.</p>
<div class="griglia">{"".join(f'<a href="{NAZ_TR[c][0]}/ireland/"><span class="ic">{ico("passport")}</span><span>{escape(NAZ_TR[c][1])} in Ireland<small>{intero(pps_periodo(c, PPS_YTD) if PPS_YTD else pps_anno(c, PPS_PIENO))} PPS numbers, {periodo_pps() + " " + PPS_YTD if PPS_YTD else PPS_PIENO}</small></span></a>' for c in sorted(PPS_OK, key=lambda x: -(pps_anno(x, PPS_PIENO) or 0)) if "ireland" in COPPIE_TR[c])}</div>
<h2>How to read these figures</h2>
<ul class="testo">
<li><strong>EU and EFTA (Eurostat):</strong> residence permits valid for at least 3 months issued to non-EU citizens for the first time. They are not a count of moves or of residents, and they leave out people who also hold an EU passport.</li>
<li><strong>Canada (IRCC):</strong> new permanent residents by citizenship. Many already lived in Canada on a temporary permit; temporary workers and students are not counted.</li>
<li><strong>United Kingdom (Home Office):</strong> work, study and family visas granted to people applying from outside the UK, including dependants. Visitors are not counted.</li>
<li><strong>Ireland (Department of Social Protection):</strong> PPS numbers allocated by nationality, by month from {PPS_MESI[0][:4]} and by year from {PPS["anni"][0]}. A PPS number gives access to public services; people living abroad can also get one, so it is not a count of moves.</li>
<li><strong>Updates:</strong> Eurostat publishes each year once, in the autumn of the year after, and revises past years when countries correct their data. IRCC updates its file every month and the Home Office every quarter.</li>
<li>We show a nationality and country page when there were at least {intero(SOGLIA_TR)} permits, new permanent residents or visas in {Y1}.</li></ul>
<h2>Official sources</h2>
<ul class="fonti">
<li><a href="{escape(F_ES["pagina"])}" rel="noopener">Eurostat, {escape(F_ES["titolo"])}</a> – data updated on {data_lunga(F_ES["aggiornato_il"])}, downloaded from the Eurostat API on {data_lunga(F_ES["scaricato_il"])}; <a href="{escape(F_ES["metadati"])}" rel="noopener">definitions and metadata</a>; <a href="{escape(F_ES["licenza_url"])}" rel="license noopener">free re-use with acknowledgement</a>.</li>
<li><a href="{escape(F_PR["pagina"])}" rel="noopener">IRCC, Permanent Residents – Monthly IRCC Updates</a> – <a href="{escape(F_PR["url"])}" rel="noopener">CSV</a> updated on {data_rfc(F_PR["ultima_modifica"])}, data to {mese_testo(F_PR["ultimo_mese"])}. Contains information licensed under the <a href="{escape(F_PR["licenza_url"])}" rel="license noopener">{escape(F_PR["licenza"])}</a>.</li>
<li><a href="{escape(F_UKV["url"])}" rel="noopener">Home Office, {escape(F_UKV["titolo"])}</a> – published {escape(F_UKV["pubblicato"])}, next update {escape(F_UKV["prossimo"])}. Contains public sector information licensed under the <a href="{escape(F_UKV["licenza_url"])}" rel="license noopener">{escape(F_UKV["licenza"])}</a>.</li>
<li><a href="{escape(F_PPS["pagina"]["url"])}" rel="noopener">Department of Social Protection, {escape(F_PPS["pagina"]["titolo"])}</a> – page updated on {data_lunga(F_PPS["pagina"]["aggiornata"])}, data to {mese_testo(PPS_ULTIMO)}; licence <a href="{escape(F_PPS["scheda"]["licenza_url"])}" rel="license noopener">{escape(F_PPS["scheda"]["licenza"])}</a> (<a href="{escape(F_PPS["scheda"]["url"])}" rel="noopener">data.gov.ie</a>).</li></ul>
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
    chiave = (lambda x: -(pps_anno(x, PPS_PIENO) or 0)) if d == "ireland" else (lambda x: -(val_tr(x, d, Y1) or 0))
    chi = [c for c in sorted(NAZ_TR, key=chiave) if d in COPPIE_TR[c]]
    if not chi:
        return ""
    misura = ("work, study and family visas granted by the UK in " + Y1 + " (Home Office)" if d == "uk"
              else f"PPS numbers allocated in {PPS_PIENO} (Department of Social Protection; a PPS number is not a count of arrivals), with first residence permits (Eurostat) as a separate measure" if d == "ireland"
              else f"first residence permits issued in {Y1} (Eurostat)")
    nf = DEST_TR[d][3]
    return (f'<h2>Who moved to {escape(nf)} in {Y1}</h2><p class="lead">{"New PPS numbers by nationality in " + escape(nf) if d == "ireland" else "How many people of each nationality moved to " + escape(nf)}: {misura}.</p>'
            f'<div class="griglia">{"".join(scheda_coppia(c, d, rel + SEZ_TR, chi=True) for c in chi)}</div>')


def genera_trasferimenti():
    pagina_tr_indice()
    for c in NAZ_TR:
        pagina_tr_naz(c)
        for d in COPPIE_TR[c]:
            if d == "ireland":
                pagina_tr_ie(c)
                continue
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
    pagina_rif_mev()
    pagina_rif_uk()
    pagina_rif_uk_famiglia()
    pagina_rif_au()
    pagina_rif_nz()
    pagina_rif_ca()


def controlli_rifiuti():
    errori = []
    if len(PAESI_RIF) < 40:
        errori.append(f"rifiuti: solo {len(PAESI_RIF)} Paesi con pagina")
    if len(set(SLUG_RIF.values())) != len(SLUG_RIF) or set(SLUG_RIF.values()) & {"uk", "schengen", "multiple-entry-schengen-visa"}:
        errori.append("rifiuti: slug dei Paesi duplicati o riservati")
    if len(PAESI_FACILE) < 30:
        errori.append(f"rifiuti: solo {len(PAESI_FACILE)} Paesi con la pagina 'easiest Schengen visa'")
    senza = [p for p in PAESI_RIF if p not in DEMONIMI]
    if senza:
        errori.append(f"rifiuti: aggettivo di nazionalità mancante per {', '.join(senza)} (DEMONIMI)")
    for k, f in RIF["fonti"].items():
        if not f.get("url", "").startswith("https://"):
            errori.append(f"rifiuti: fonte {k} senza URL")
    for a in ANNI_UE:  # visti a ingressi multipli (30/10/2026): 8° elemento di ogni riga, mai negativo
        if any(len(r) < 8 or r[7] < 0 for r in UE[a]):
            errori.append(f"rifiuti: righe {a} senza la colonna dei visti a ingressi multipli: rilanciare raccolta/rifiuti.py")
    if URL_SAFETYWING and not URL_SAFETYWING.startswith("https://safetywing.com/"):
        errori.append("rifiuti: link SafetyWing non valido in dati/affiliati.json (_safetywing_schengen)")
    if not URL_SAFETYWING and not _SW.get("url_sospeso", "").startswith("https://safetywing.com/"):
        errori.append("rifiuti: link SafetyWing né attivo né sospeso in dati/affiliati.json (_safetywing_schengen)")
    return errori


# ---------------------------------------------------------------- UK visa English tests (SELT), 30/10/2026
# Dati: dati/selt.json (raccolta/selt.py): elenchi ufficiali dei centri e dei test approvati dal Home Office (GOV.UK, OGL v3.0),
# frasi delle guide GOV.UK sui livelli per visto e dello Statement of Changes HC 1691 (B2 per la residenza dal 26/3/2027).
# Pagine: /uk-english-test/ (indice), /uk-english-test/<città>/ (città britanniche), /uk-english-test/<paese>/ (Paesi esteri),
# solo per i luoghi con domanda (autocompletamento salvato in selt.json, soglia SOGLIA_DOMANDA di raccolta/selt.py).
SELT = json.loads((DATI / "selt.json").read_text(encoding="utf-8"))
SEZ_SELT = "uk-english-test/"
F_SELT = SELT["fonti"]
LIV = SELT["livelli"]
HC1691 = F_SELT["hc1691"]
SOGLIA_DOMANDA_SELT = SELT["domanda"].get("soglia", 1)
CENTRI_UK = SELT["centri"]["uk"]        # [fornitore, nome, città, indirizzo, disponibilità]
CENTRI_EST = SELT["centri"]["estero"]   # [fornitore, nome, Paese, città, indirizzo, disponibilità]
FORN = SELT["fornitori"]
_I = AFFILIATI.get("_italki_selt", {})
URL_ITALKI = _I.get("url", "")
NOMI_FORN = {"IELTS SELT Consortium": "IELTS SELT Consortium", "LanguageCert": "LanguageCert", "Pearson": "Pearson (PTE)",
             "Trinity College London": "Trinity College London", "PSI": "PSI Services (Skills for English)"}
NOMI_PAESI_SELT = {"USA": "United States", "Bosnia & Herzegovina": "Bosnia and Herzegovina", "Democratic Republic of Congo": "DR Congo",
                   "Cyprus (South)": "Cyprus (south)", "Cyprus (North)": "Northern Cyprus", "Virgin Islands (US)": "US Virgin Islands"}
SLUG_CITTA_SELT = {"Newcastle upon Tyne": "newcastle"}
CITTA_SELT = sorted({r[2] for r in CENTRI_UK})
PAESI_SELT = sorted({r[2] for r in CENTRI_EST})
DOM_C = SELT["domanda"].get("citta", {})
DOM_P = SELT["domanda"].get("paesi", {})
CITTA_PAG = [c for c in CITTA_SELT if len(DOM_C.get(c, [])) >= SOGLIA_DOMANDA_SELT]
PAESI_PAG = [p for p in PAESI_SELT if len(DOM_P.get(p, [])) >= SOGLIA_DOMANDA_SELT]
SLUG_SELT = {**{c: SLUG_CITTA_SELT.get(c) or slug_testo(c) for c in CITTA_SELT},
             **{p: slug_testo(NOMI_PAESI_SELT.get(p, p)) for p in PAESI_SELT}}
DATA_ELENCO = F_SELT["centri_uk"]["data_elenco"]
ANNO_SELT = DATA_ELENCO[:4]
DATA_B2 = HC1691["in_vigore"]


def nome_p_selt(p, maiuscola=False):
    return art(NOMI_PAESI_SELT.get(p, p), maiuscola)


def nome_test(t):
    """Nome del test come nell'elenco ufficiale, con 'LanguageCert' scritto come nei file e un refuso evidente corretto ('Grace 3')."""
    t = re.sub(r"\s+", " ", t.replace("LANGUAGECERT", "LanguageCert").replace("Life Skills–", "Life Skills –")).strip()
    return t.replace("(GESE) Grace 3", "(GESE) Grade 3")


def nome_forn_test(f):
    """Fornitore come scritto negli elenchi dei test ('PSI Service (UK) Ltd') -> nome breve usato nelle pagine."""
    return NOMI_FORN.get("PSI" if f.startswith("PSI") else f, f)


def test_di(f):
    return ", ".join(nome_test(x) for x in FORN[f]["test"])


def elenco_e(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def titolo_breve(varianti):
    return next(t for t in varianti + [varianti[-1]] if len(t) <= 70)


def centri_n(n):
    return f"{intero(n)} approved centre{'s' if n != 1 else ''}"


def fonte_selt_p(estero=False, entrambi=False):
    chiavi = ["centri_uk", "centri_estero"] if entrambi else (["centri_estero"] if estero else ["centri_uk"])
    nomi = {"centri_uk": "List of approved test centres in the UK", "centri_estero": "List of approved test centres outside the UK"}
    files = "; ".join(f'<a href="{escape(F_SELT[k]["url"])}" rel="noopener">{nomi[k]}</a> (ODS, list dated {data_lunga(F_SELT[k]["data_elenco"])}, '
                      f'downloaded on {data_lunga(F_SELT[k]["scaricato_il"])})' for k in chiavi)
    return (f'<p class="fonte">Source: Home Office, {files}, from the GOV.UK page <a href="{F_SELT["pagina"]["url"]}" rel="noopener">'
            f'{escape(F_SELT["pagina"]["titolo"])}</a> (updated {data_lunga(F_SELT["pagina"]["aggiornata"])}). Contains public sector information licensed under the '
            f'<a href="{F_SELT["pagina"]["licenza_url"]}" rel="noopener">Open Government Licence v3.0</a>.</p>')


def fonte_liv(chiave, testo_link=None):
    L = LIV[chiave]
    return f'<a href="{L["url"]}" rel="noopener">{escape(testo_link or L["titolo"])}</a> (GOV.UK, read on {data_lunga(L["letta_il"])})'


def fonte_hc():
    return (f'<a href="{HC1691["memorandum"]}" rel="noopener">explanatory memorandum to the Statement of Changes HC 1691</a>, paragraphs 5.60–5.62, '
            f'and the <a href="{HC1691["testo"]}" rel="noopener">rule changes</a> (published on GOV.UK on {data_lunga(HC1691["pubblicato"])}, read on {data_lunga(HC1691["letto_il"])})')


AVVISO_SELT = ('<p class="avviso"><strong>Not immigration or legal advice.</strong> This page lists the Home Office\'s approved test centres and the '
               'levels written in the GOV.UK guidance on the dates shown. Some people do not need a test (for example nationals of some English-speaking '
               'countries, people over 65, or people with a degree taught in English). Check the guidance for your own route on GOV.UK, and the provider\'s '
               'website for dates and fees, before you book.</p>')


def righe_livelli(rel):
    """Tabella 'quale livello per quale visto' (frasi delle guide GOV.UK salvate in selt.json, controllate da raccolta/selt.py)."""
    v = [
        ("Partner or parent visa (family), first application", "A1", "Speaking and listening", fonte_liv("partner_primo", "Family visas: knowledge of English")),
        ("Partner or parent visa, extending after 2.5 years", "A2", "Speaking and listening", fonte_liv("partner_proroga", "Family visas: knowledge of English")),
        (f"Settlement (indefinite leave to remain), application made before {data_lunga(DATA_B2)}", "B1", "Speaking and listening",
         fonte_liv("cittadinanza_residenza", "Prove your knowledge of English for citizenship and settling")),
        (f"Settlement on the routes listed in HC 1691, application made on or after {data_lunga(DATA_B2)}", "B2", "Speaking and listening", fonte_hc()),
        ("British citizenship", "B1", "Speaking and listening", fonte_liv("cittadinanza_residenza", "Prove your knowledge of English for citizenship and settling")),
        ("Skilled Worker and Health and Care Worker visas (new applications)", "B2", "Reading, writing, speaking and listening",
         fonte_liv("skilled_worker", "Skilled Worker visa") + "; " + fonte_liv("health_care", "Health and Care Worker visa")),
        ("Student visa, course at degree level or above", "B2", "Reading, writing, speaking and listening", fonte_liv("studente", "Student visa")),
        ("Student visa, course below degree level", "B1", "Reading, writing, speaking and listening", fonte_liv("studente", "Student visa")),
        ("High Potential Individual and Scale-up Worker visas", "B2", "Reading, writing, speaking and listening",
         fonte_liv("hpi", "High Potential Individual visa") + "; " + fonte_liv("scale_up", "Scale-up Worker visa")),
    ]
    return "".join(f'<tr><td>{escape(a)}</td><td><strong>{b}</strong></td><td>{c}</td><td class="small">{d}</td></tr>' for a, b, c, d in v), len(v)


def tabella_livelli(rel):
    righe, _ = righe_livelli(rel)
    return (f'<div class="tab compatta"><table id="t-livelli"><thead><tr><th scope="col">Application</th><th scope="col">Minimum level (CEFR)</th>'
            f'<th scope="col">Skills tested</th><th scope="col">Official source</th></tr></thead><tbody>{righe}</tbody></table></div>'
            f'<p class="small">Skills tested: GOV.UK, <a href="{F_SELT["pagina"]["url"]}" rel="noopener">{escape(F_SELT["pagina"]["titolo"])}</a> '
            f'(citizenship, parent, partner and settlement: speaking and listening test; Skilled Worker, Health and Care Worker, Student, High Potential Individual '
            f'and Scale-up: reading, writing, speaking and listening). People who already had a Skilled Worker or Health and Care Worker visa before 8 January 2026 '
            f'and are extending need B1 ({fonte_liv("skilled_worker_prima", "Skilled Worker visa")}).</p>')


def test_per_livello(dove, livello, tipo):
    return [(r[3], nome_test(r[2]), r[4]) for r in SELT["test"][dove] if r[0] == livello and r[1] == tipo]


def nessun_b2_due_abilita():
    """True se negli elenchi ufficiali non c'è un test B2 di sola comprensione e produzione orale (2-facet)."""
    return not test_per_livello("uk", "B2", "2-facet") and not test_per_livello("estero", "B2", "2-facet")


def tabella_test():
    righe = []
    for liv, tipo, uso in (("A1", "2-facet", "First partner or parent visa"), ("A2", "2-facet", "Partner or parent extension after 2.5 years"),
                           ("B1", "2-facet", "Settlement and citizenship (speaking and listening)"), ("B1", "4-facet", "Student below degree level (four skills)"),
                           ("B2", "4-facet", "Skilled Worker, Health and Care Worker, degree-level Student and others (four skills)"),
                           ("B2", "2-facet", f"Settlement from {data_lunga(DATA_B2)} (speaking and listening)")):
        uk = test_per_livello("uk", liv, tipo)
        es = test_per_livello("estero", liv, tipo)
        fmt = lambda xs: "<br>".join(f"{escape(n)} <span class=\"small\">({escape(nome_forn_test(f))}; minimum grade: {escape(m)})</span>" for f, n, m in xs) or "<em>None on the list</em>"  # noqa: E731
        righe.append(f'<tr><td><strong>{liv}</strong> · {"speaking and listening" if tipo == "2-facet" else "four skills"}<br><span class="small">{escape(uso)}</span></td>'
                     f'<td>{fmt(uk)}</td><td>{fmt(es)}</td></tr>')
    return (f'<div class="tab compatta"><table id="t-test"><thead><tr><th scope="col">Level and use</th><th scope="col">Approved tests taken in the UK</th>'
            f'<th scope="col">Approved tests taken outside the UK</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>'
            f'<p class="fonte">Source: Home Office, <a href="{F_SELT["test_uk"]["url"]}" rel="noopener">List of approved secure English language tests taken in the UK</a> and '
            f'<a href="{F_SELT["test_estero"]["url"]}" rel="noopener">taken outside the UK</a> (ODS, downloaded on {data_lunga(F_SELT["test_uk"]["scaricato_il"])}), '
            f'Open Government Licence v3.0. "Four skills" = reading, writing, speaking and listening. The full lists also include C1 and C2.</p>')


def sezione_b2(rel, breve=False):
    vuoto = nessun_b2_due_abilita()
    nota_test = (f' On the approved lists we read on {data_lunga(F_SELT["test_uk"]["scaricato_il"])}, there is no speaking-and-listening-only test at B2: '
                 f'every B2 test listed assesses all four skills.' if vuoto else "")
    if breve:
        return (f'<section class="card" id="b2-2027"><h2 style="margin-top:0">{ico("calendar")} B2 for settlement from {data_lunga(DATA_B2)}</h2>'
                f'<p>For settlement applications made on or after {data_lunga(DATA_B2)}, the UK Statement of Changes HC 1691 raises the English level from B1 to '
                f'<strong>B2 in speaking and listening</strong> on the routes it lists (Skilled Worker, Settlement Family Life, Long Residence, Global Talent and others). '
                f'Applications made before that date still need B1.{nota_test} <a href="{rel}{SEZ_SELT}#b2-2027">What changes in 2027</a>.</p>'
                f'<p class="fonte">Source: {fonte_hc()}.</p></section>')
    return f"""<h2 id="b2-2027">The 2027 change: B2 for settlement</h2>
<p><strong>From {data_lunga(DATA_B2)}, settlement applications on many routes need English at B2 in speaking and listening instead of B1.</strong> The explanatory memorandum to the Statement of Changes HC 1691 says: "This change increases the English language requirement for settlement to B2 level […] for a number of immigration routes where the existing requirement is at B1 level" and "These changes will come into force on 26 March 2027." The rules apply the new level by date of application: before {data_lunga(DATA_B2)}, B1; on or after that date, B2.</p>
<ul class="testo"><li><strong>Routes listed in the memorandum:</strong> Appendix KoLL (the general knowledge of language and life rules for settlement), Skilled Worker, Minister of Religion, Representative of an Overseas Business, UK Ancestry, Global Talent, Scale-up, Innovator Founder, International Sportsperson, Child Relative (Sponsors with Protection), Long Residence, Bereaved Partner, Private Life and Settlement Family Life.</li>
<li><strong>Who it affects:</strong> the memorandum says the changes "will therefore apply to those already on a pathway to settlement in the UK"; the start was put off to 2027 to give people time to meet the new level.</li>
<li><strong>Citizenship</strong> is not one of the routes listed. The GOV.UK guide for citizenship and settling still asks for B1 or above: {fonte_liv("cittadinanza_residenza", "Prove your knowledge of English for citizenship and settling")}.</li>
<li><strong>Test results last 2 years</strong> for a new application, so check the date your result was awarded against the date you plan to apply.</li></ul>
<p>{nota_test.strip() or ""} Check the provider's website before you book a test for a settlement application made on or after {data_lunga(DATA_B2)}.</p>
<p class="fonte">Source: {fonte_hc()}.</p>"""


def box_italki(rel):
    """Riquadro «Prepare for the speaking test» (italki, voce _italki_selt di dati/affiliati.json): dopo le informazioni ufficiali.
    Vuoto se il link non è attivo. Nessun prezzo, nessuna promessa sul risultato del test o sul visto."""
    if not URL_ITALKI:
        return ""
    return (f'<section class="card aff-r" aria-labelledby="aff-i-h"><div class="aff-r-t"><span class="ic">{ico("user")}</span>'
            f'<h2 id="aff-i-h">Prepare for the speaking test</h2><span class="aff-tag">Affiliate</span></div>'
            f'<p>For partner, parent, settlement and citizenship applications the SELT tests speaking and listening only. Speaking English often with a teacher, '
            f'even online, is one way to prepare. On italki you choose an English teacher and pay per lesson.</p>'
            f'<p class="aff-r-cta"><a class="btn" href="{escape(URL_ITALKI)}" rel="sponsored noopener" target="_blank">Find an English teacher on italki{ico("arrow")}'
            f'<span class="sr"> (opens in a new tab)</span></a></p>'
            f'<p class="small">{MON.RIGA_EN} A teacher cannot book your test or change your result: you book the test only on the provider\'s website, and lessons '
            f'do not change the decision on your visa.</p></section>')


def come_prenotare(estero=False):
    forn = ["IELTS SELT Consortium", "LanguageCert", "Pearson", "PSI"] if estero else ["IELTS SELT Consortium", "LanguageCert", "Pearson", "Trinity College London"]
    link = elenco_e(f'<a href="{escape(FORN[f]["url"])}" rel="noopener">{escape(NOMI_FORN[f])}</a>' for f in forn)
    return (f'<ul class="testo"><li>Book on the provider\'s own website: {link}. GOV.UK says to check the provider\'s website for dates and to make sure the centre is open: '
            f'"Do not contact the test centre directly."</li>'
            f'<li>Book the SELT version of the test (for example IELTS for UKVI or IELTS Life Skills, not ordinary IELTS). The approved names are: '
            + "; ".join(f'{escape(NOMI_FORN[f])}: {escape(test_di(f))}' for f in forn) + '.</li>'
            f'<li>"You should be able to take a test within 28 days of booking, but it may not always be at the location nearest to you." '
            f'Use the name exactly as it is on your passport or identity document.</li>'
            f'<li>Test results are valid for 2 years from the date the test is awarded. After you pass, you get a SELT reference number to use in your application.</li>'
            f'<li>Fees are set by each provider and are not on the Home Office lists, so we do not show them. If you book through an agent, GOV.UK says its fees should be '
            f'"the same as, or lower than, the price on the test provider\'s website".</li></ul>'
            f'<p class="fonte">Source: GOV.UK, <a href="{F_SELT["pagina"]["url"]}" rel="noopener">{escape(F_SELT["pagina"]["titolo"])}</a> '
            f'(updated {data_lunga(F_SELT["pagina"]["aggiornata"])}, read on {data_lunga(F_SELT["pagina"]["letta_il"])}).</p>')


def link_luoghi_selt(rel_sez, escludi=None):
    c = " · ".join(f'<a href="{rel_sez}{SLUG_SELT[x]}/">{escape(x)}</a>' for x in CITTA_PAG if x != escludi)
    p = " · ".join(f'<a href="{rel_sez}{SLUG_SELT[x]}/">{escape(NOMI_PAESI_SELT.get(x, x))}</a>' for x in PAESI_PAG if x != escludi)
    return f'<h2>Other places</h2><p><strong>UK:</strong> {c}</p><p><strong>Outside the UK:</strong> {p}</p>'


def fornitori_di(righe, i=0):
    ordine = ["IELTS SELT Consortium", "LanguageCert", "Pearson", "Trinity College London", "PSI"]
    return [f for f in ordine if any(r[i] == f for r in righe)]


def pagina_selt_citta(c):
    rel = "../../"
    percorso = f"{SEZ_SELT}{SLUG_SELT[c]}/"
    qui = [r for r in CENTRI_UK if r[2] == c]
    chiave = "Newcastle" if c.startswith("Newcastle") else c
    altri = [r for r in CENTRI_UK if r[2] != c and re.search(r"\b" + re.escape(chiave) + r"\b", r[1])]
    qui.sort(key=lambda r: (r[0], r[1]))
    forn = fornitori_di(qui)
    n = len(qui)
    righe = "".join(f'<tr><td>{escape(NOMI_FORN[r[0]])}</td><td>{escape(r[1])}</td><td>{escape(r[3])}</td></tr>' for r in qui)
    righe_altri = "".join(f'<tr><td>{escape(NOMI_FORN[r[0]])}</td><td>{escape(r[1])}</td><td>{escape(r[3])} <span class="small">(listed under {escape(r[2])})</span></td></tr>' for r in altri)
    nomi_forn = elenco_e(NOMI_FORN[f] for f in forn)
    domande = [
        (f"Where can I take a SELT in {c}?",
         f"The Home Office list dated {data_lunga(DATA_ELENCO)} has {centri_n(n)} in {c}: " + "; ".join(f"{r[1]} ({NOMI_FORN[r[0]]})" for r in qui) +
         ". Book on the provider's website, not at the centre."),
        (f"Which English test do I need for a UK visa?",
         f"A1 speaking and listening for a first partner or parent visa, A2 to extend after 2.5 years, B1 for settlement and citizenship, and B2 (four skills) for "
         f"Skilled Worker and most degree-level Student visas. For settlement applications made on or after {data_lunga(DATA_B2)} on the routes listed in HC 1691, B2 in speaking and listening."),
        (f"Does every centre in {c} offer every test?",
         "The Home Office list does not say which tests or dates each centre offers. Check the provider's booking page: GOV.UK says you should be able to take a test "
         "within 28 days of booking, but not always at the nearest location."),
        ("How much does the test cost?",
         "Fees are set by each provider and are not on the Home Office lists, so we do not show them. Check the provider's website before you book."),
    ]
    london = ""
    if c in ("Croydon", "Stratford", "Uxbridge") and "London" in CITTA_PAG:
        london = f'<p class="small">{escape(c)} is in Greater London: see also <a href="../{SLUG_SELT["London"]}/">SELT test centres in London</a>.</p>'
    elif c == "London":
        vicini = [x for x in ("Croydon", "Stratford", "Uxbridge") if x in CITTA_SELT]
        london = ('<p class="small">The official list puts some Greater London centres under their own town: ' +
                  ", ".join((f'<a href="../{SLUG_SELT[x]}/">{x}</a>' if x in CITTA_PAG else x) + f" ({sum(1 for r in CENTRI_UK if r[2] == x)})" for x in vicini) + ".</p>")
    corpo = f"""<section class="hero">{h1_diviso(f"SELT test centres in {c}: {centri_n(n)} for UK visas")}
<p class="lead">There {"are" if n != 1 else "is"} <strong>{centri_n(n)}</strong> for UK visa English tests (SELT) in {escape(c)}, run by {escape(nomi_forn)}, according to the Home Office list of approved test centres dated {data_lunga(DATA_ELENCO)} (GOV.UK, downloaded on {data_lunga(F_SELT["centri_uk"]["scaricato_il"])}). You book the test on the provider's website, not at the centre.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{bandiera("United Kingdom")}<span>{escape(c)}</span><span>list of {data_lunga(DATA_ELENCO)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Approved SELT centres in {escape(c)}</span><span class="sr">: </span><strong>{n}</strong> from {len(forn)} provider{"s" if len(forn) != 1 else ""}</p>
<div class="kpi">{"".join(f'<div><b>{sum(1 for r in qui if r[0] == f)}</b><span>{escape(NOMI_FORN[f])}</span></div>' for f in forn)}</div>
{fonte_selt_p()}
</div></section>
{AVVISO_SELT}
{AD}
<h2>Approved test centres in {escape(c)}</h2>
<div class="tab compatta"><table id="t-centri"><thead><tr><th scope="col">Provider</th><th scope="col">Centre</th><th scope="col">Address</th></tr></thead><tbody>{righe}</tbody></table></div>
{fonte_selt_p()}
<p class="small">The test names to book for each provider are under <a href="#how-to-book">How to book</a>.</p>
{london}
{f'<h3>Listed under another town, with {escape(chiave)} in the centre name</h3><div class="tab compatta"><table><thead><tr><th scope="col">Provider</th><th scope="col">Centre</th><th scope="col">Address</th></tr></thead><tbody>{righe_altri}</tbody></table></div>' if altri else ""}
<h2>Which level for which visa</h2>
{tabella_livelli(rel)}
{sezione_b2(rel, breve=True)}
<h2 id="how-to-book">How to book</h2>
{come_prenotare()}
{box_italki(rel)}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
{link_luoghi_selt("../", c)}
<p><a href="../">UK visa English tests: all centres and levels</a> · <a href="{rel}uk-spouse-visa/">UK spouse visa income requirement</a> · <a href="{rel}{SEZ}uk/family-visas/">UK family visa refusal rates</a></p>"""
    titolo = titolo_breve([f"SELT test centres in {c}: {centri_n(n)} for UK visas ({ANNO_SELT})",
                           f"SELT test centres in {c}: {centri_n(n)} ({ANNO_SELT})", f"SELT test centres in {c} ({ANNO_SELT})"])
    descr = (f"{centri_n(n).capitalize()} for UK visa English tests (SELT) in {c}: {nomi_forn}. Addresses from the Home Office list of "
             f"{data_lunga(DATA_ELENCO)}, which level you need, and the B2 change from {data_lunga(DATA_B2)}.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande)],
           briciole=[("UK visa English tests", SEZ_SELT), (c, percorso)])


def pagina_selt_paese(p):
    rel = "../../"
    percorso = f"{SEZ_SELT}{SLUG_SELT[p]}/"
    qui = sorted([r for r in CENTRI_EST if r[2] == p], key=lambda r: (r[3], r[0], r[1]))
    n = len(qui)
    citta = {}
    for r in qui:
        citta[r[3]] = citta.get(r[3], 0) + 1
    ord_citta = sorted(citta, key=lambda x: (-citta[x], x))
    forn = fornitori_di(qui)
    nome = nome_p_selt(p)
    nomi_forn = elenco_e(NOMI_FORN[f] for f in forn)
    a1 = [t for t in test_per_livello("estero", "A1", "2-facet") if any(f == t[0] or (t[0].startswith("PSI") and f == "PSI") for f in forn)]
    righe = "".join(f'<tr><td>{escape(r[3])}</td><td>{escape(NOMI_FORN[r[0]])}</td><td>{escape(r[1])}</td><td>{escape(r[4])}</td></tr>' for r in qui)
    elenco_citta = ", ".join(f"{x} ({citta[x]})" for x in ord_citta[:8]) + (f" and {len(ord_citta) - 8} more" if len(ord_citta) > 8 else "")
    domande = [
        (f"Where can I take the A1 English test for a UK spouse visa in {nome}?",
         f"At an approved SELT centre: the Home Office list dated {data_lunga(DATA_ELENCO)} has {centri_n(n)} in {nome}, in {elenco_citta}. "
         f"The A1 speaking and listening tests approved outside the UK from the providers with centres in {nome} are: "
         + "; ".join(f"{t[1]} from {nome_forn_test(t[0])}" for t in a1) + "."),
        (f"How many SELT test centres are there in {nome}?",
         f"{centri_n(n).capitalize()} in {len(citta)} cit{'ies' if len(citta) != 1 else 'y'}, from {nomi_forn} (Home Office list dated {data_lunga(DATA_ELENCO)})."),
        ("Does every centre offer every test?",
         "The Home Office list does not say which tests or dates each centre offers. Check the provider's booking page before you travel."),
        ("How much does the test cost?",
         "Fees are set by each provider and are not on the Home Office lists, so we do not show them. If you use an agent, GOV.UK says its fees "
         "should be the same as, or lower than, the price on the provider's website."),
        ("Is the English level for UK settlement going up?",
         f"Yes, on many routes: for settlement applications made on or after {data_lunga(DATA_B2)}, HC 1691 raises the level from B1 to B2 in speaking and listening."),
    ]
    filtro = (f'<p class="filtro"><label><span class="sr">Filter by city</span><input type="search" placeholder="Filter by city: e.g. {escape(ord_citta[0])}" '
              f'data-filtro="t-centri" autocomplete="off"></label></p>' if n > 12 else "")
    corpo = f"""<section class="hero">{h1_diviso(f"UK visa English test in {nome}: {centri_n(n)} (SELT)")}
<p class="lead">There {"are" if n != 1 else "is"} <strong>{centri_n(n)}</strong> for UK visa English tests (SELT) in {escape(nome)}, in {escape(elenco_citta)}, run by {escape(nomi_forn)}, according to the Home Office list of approved test centres outside the UK dated {data_lunga(DATA_ELENCO)} (GOV.UK, downloaded on {data_lunga(F_SELT["centri_estero"]["scaricato_il"])}). The first partner (spouse) visa needs A1 in speaking and listening.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("globe")}<span>{escape(NOMI_PAESI_SELT.get(p, p))}</span><span>list of {data_lunga(DATA_ELENCO)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Approved SELT centres in {escape(nome)}</span><span class="sr">: </span><strong>{n}</strong> in {len(citta)} cit{"ies" if len(citta) != 1 else "y"}</p>
<div class="kpi">{"".join(f'<div><b>{sum(1 for r in qui if r[0] == f)}</b><span>{escape(NOMI_FORN[f])}</span></div>' for f in forn)}</div>
{fonte_selt_p(estero=True)}
</div></section>
{AVVISO_SELT}
{AD}
<h2>Approved test centres in {escape(nome)}</h2>
{filtro}
<div class="tab compatta"><table id="t-centri"><thead><tr><th scope="col">City</th><th scope="col">Provider</th><th scope="col">Centre</th><th scope="col">Address</th></tr></thead><tbody>{righe}</tbody></table></div>
{fonte_selt_p(estero=True)}
<h2>Which level for which visa</h2>
{tabella_livelli(rel)}
{sezione_b2(rel, breve=True)}
<h2>How to book</h2>
{come_prenotare(estero=True)}
{box_italki(rel)}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
{link_luoghi_selt("../", p)}
<p><a href="../">UK visa English tests: all centres and levels</a> · <a href="{rel}uk-spouse-visa/">UK spouse visa income requirement</a> · <a href="{rel}{SEZ}uk/family-visas/">UK family visa refusal rates</a></p>"""
    titolo = titolo_breve([f"UK visa English test in {nome}: {centri_n(n)} (SELT, {ANNO_SELT})",
                           f"UK visa English test in {nome}: {n} SELT centres ({ANNO_SELT})", f"SELT test centres in {nome} ({ANNO_SELT})",
                           f"SELT centres in {nome}"])
    descr = (f"{centri_n(n).capitalize()} for UK visa English tests (SELT) in {nome}: {nomi_forn}. Cities and addresses from the Home Office list of "
             f"{data_lunga(DATA_ELENCO)}, the A1 test for the spouse visa and the B2 change from {data_lunga(DATA_B2)}.")
    pagina(percorso, titolo, descr, corpo, ordina=n > 12, jsonld_extra=[ld_faq(domande)],
           briciole=[("UK visa English tests", SEZ_SELT), (NOMI_PAESI_SELT.get(p, p), percorso)])


def pagina_selt_indice():
    rel = "../"
    percorso = SEZ_SELT
    n_uk, n_est = len(CENTRI_UK), len(CENTRI_EST)
    righe_c = []
    for c in sorted(CITTA_SELT, key=lambda x: (-sum(1 for r in CENTRI_UK if r[2] == x), x)):
        qui = [r for r in CENTRI_UK if r[2] == c]
        nome = f'<a href="{SLUG_SELT[c]}/">{escape(c)}</a>' if c in CITTA_PAG else escape(c)
        righe_c.append(f'<tr><td>{nome}</td><td class="n" data-v="{len(qui)}">{len(qui)}</td><td>{escape(", ".join(NOMI_FORN[f] for f in fornitori_di(qui)))}</td></tr>')
    righe_p = []
    for p in sorted(PAESI_SELT, key=lambda x: (-sum(1 for r in CENTRI_EST if r[2] == x), x)):
        qui = [r for r in CENTRI_EST if r[2] == p]
        nome = f'<a href="{SLUG_SELT[p]}/">{escape(NOMI_PAESI_SELT.get(p, p))}</a>' if p in PAESI_PAG else escape(NOMI_PAESI_SELT.get(p, p))
        righe_p.append(f'<tr><td>{nome}</td><td class="n" data-v="{len(qui)}">{len(qui)}</td><td class="n" data-v="{len({r[3] for r in qui})}">{len({r[3] for r in qui})}</td>'
                       f'<td>{escape(", ".join(NOMI_FORN[f] for f in fornitori_di(qui)))}</td></tr>')
    per_forn_uk = {f: sum(1 for r in CENTRI_UK if r[0] == f) for f in fornitori_di(CENTRI_UK)}
    domande = [
        ("What English level do I need for a UK spouse visa?",
         f"A1 in speaking and listening for the first partner visa, and A2 when you extend after 2.5 years (GOV.UK). For settlement after 5 years, B1 for applications made "
         f"before {data_lunga(DATA_B2)}; HC 1691 raises it to B2 in speaking and listening for applications made on or after that date on the routes it lists, which include "
         f"Settlement Family Life. GOV.UK says a B1 or higher result from your first visa can be used again for settlement if it is still on the approved list; "
         f"on those routes a B1 result counts only for applications made before {data_lunga(DATA_B2)}."),
        ("Is the B2 English requirement for ILR confirmed?",
         f"Yes. The Statement of Changes HC 1691, published on GOV.UK on {data_lunga(HC1691['pubblicato'])}, sets B2 for settlement applications made on or after "
         f"{data_lunga(DATA_B2)} on the routes it lists. Its explanatory memorandum says: \"These changes will come into force on 26 March 2027.\""),
        ("What is the difference between IELTS for UKVI and IELTS Life Skills?",
         "On the Home Office lists, IELTS Life Skills tests speaking and listening (A1, A2 and B1: the levels for partner, parent, settlement and citizenship applications), "
         "while IELTS for UKVI tests all four skills (B1 to C2, with a minimum score in each skill), used for work and study visas."),
        ("How long is a SELT result valid?",
         "Two years from the date the test is awarded, for a new application. For citizenship, and in some cases settlement, GOV.UK explains when an older B1 or higher result can still be used."),
        ("Can I take the test outside the UK?",
         f"Yes. Outside the UK the approved providers are PSI Services, IELTS SELT Consortium, LanguageCert and Pearson, with {intero(n_est)} centres in "
         f"{len(PAESI_SELT)} countries and territories on the list dated {data_lunga(DATA_ELENCO)}. If there is no approved centre in your country, you have to travel to another country."),
        ("How much does a SELT cost?",
         "Fees are set by each provider. They are not on the Home Office lists, so we do not show them: check the provider's website."),
    ]
    ld = [ld_faq(domande), ld_dataset("Approved UK visa English test (SELT) centres", f"{n_uk} centres in the UK and {n_est} outside the UK approved by the Home Office.",
                                       percorso, [F_SELT["centri_uk"]["url"], F_SELT["centri_estero"]["url"]], ANNO_SELT,
                                       F_SELT["pagina"]["licenza_url"])]
    corpo = f"""<section class="hero">{h1_diviso("UK visa English tests (SELT): test centres by city and the 2027 B2 change")}
<p class="lead">To prove your English for a UK visa with a test, you must pass a Secure English Language Test (SELT) at one of the <strong>{intero(n_uk)} approved centres in the UK</strong> or <strong>{intero(n_est)} outside the UK</strong> (Home Office lists dated {data_lunga(DATA_ELENCO)}, GOV.UK page updated {data_lunga(F_SELT["pagina"]["aggiornata"])}). The level depends on the visa: A1 for a first partner visa, A2 to extend it, B1 for settlement and citizenship, and <strong>B2 for settlement applications made on or after {data_lunga(DATA_B2)}</strong> on the routes listed in the Statement of Changes HC 1691.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{bandiera("United Kingdom")}<span>UK visa English tests</span><span>lists of {data_lunga(DATA_ELENCO)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Approved SELT centres</span><span class="sr">: </span><strong>{intero(n_uk + n_est)}</strong> ({intero(n_uk)} in the UK, {intero(n_est)} outside)</p>
<div class="kpi"><div><b>{len(CITTA_SELT)}</b><span>UK towns and cities with a centre</span></div><div><b>{len(PAESI_SELT)}</b><span>countries and territories outside the UK</span></div><div><b>{len(per_forn_uk)}</b><span>providers in the UK ({escape(", ".join(NOMI_FORN[f].split(" (")[0] for f in per_forn_uk))})</span></div><div><b>B2</b><span>for settlement from {data_lunga(DATA_B2)}</span></div></div>
{fonte_selt_p(entrambi=True)}
</div></section>
{AVVISO_SELT}
{AD}
<h2>Which level for which visa</h2>
{tabella_livelli(rel)}
{sezione_b2(rel)}
<h2>Which test to book</h2>
<p>Each provider has its own SELT version. Book the exact test on the Home Office list for your level: for example IELTS Life Skills A1 for a first partner visa, not ordinary IELTS.</p>
{tabella_test()}
<h2 id="uk-centres">Test centres in the UK</h2>
<p class="small">{intero(n_uk)} centres in {len(CITTA_SELT)} towns and cities, by number of centres. Tap a column heading to sort.</p>
<div class="tab compatta"><table class="ord" id="t-uk-c"><thead><tr>{th_ord("Town or city", False, "ascending")}{th_ord("Centres")}<th scope="col">Providers</th></tr></thead><tbody>{"".join(righe_c)}</tbody></table></div>
{fonte_selt_p()}
<h2 id="outside-uk">Test centres outside the UK</h2>
<p class="small">{intero(n_est)} centres in {len(PAESI_SELT)} countries and territories, by number of centres. Type to filter, or tap a column heading to sort.</p>
<p class="filtro"><label><span class="sr">Filter countries</span><input type="search" placeholder="Filter: e.g. Pakistan" data-filtro="t-est" autocomplete="off"></label></p>
<div class="tab compatta"><table class="ord" id="t-est"><thead><tr>{th_ord("Country or territory", False, "ascending")}{th_ord("Centres")}{th_ord("Cities")}<th scope="col">Providers</th></tr></thead><tbody>{"".join(righe_p)}</tbody></table></div>
{fonte_selt_p(estero=True)}
<p class="small">Country names are as written in the Home Office file, with a few spellings made consistent ({escape(", ".join(f"{a} → {b}" for a, b in SELT["normalizzazioni"]["paesi"].items()))}). In the UK list, "Newcastle" and "Newcastle Upon Tyne" are shown together as Newcastle upon Tyne.</p>
<h2>How to book</h2>
{come_prenotare()}
{box_italki(rel)}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
{link_luoghi_selt("")}
<p><a href="{rel}uk-spouse-visa/">UK spouse visa income requirement</a> · <a href="{rel}{SEZ}uk/family-visas/">UK spouse and family visa refusal rates</a> · <a href="{rel}uk-skilled-worker-visa/">UK Skilled Worker salary threshold</a></p>"""
    titolo = "UK visa English test (SELT): levels, test centres and B2 from 2027"
    descr = (f"Which English test for which UK visa (A1, A2, B1, B2), the {intero(n_uk)} approved SELT centres in the UK and {intero(n_est)} abroad "
             f"(Home Office lists of {data_lunga(DATA_ELENCO)}), and B2 for settlement from {data_lunga(DATA_B2)}.")
    pagina(percorso, titolo, descr, corpo, ordina=True, jsonld_extra=ld, briciole=[("UK visa English tests", percorso)])


def link_selt(P, rel):
    """Riga di collegamento dalle pagine dei visti UK alla sezione dei test di inglese."""
    if P.get("paese") != "United Kingdom":
        return ""
    return (f'<p class="small">{ico("check")} English test for this visa: see <a href="{rel}{SEZ_SELT}">UK visa English tests (SELT): levels and approved test centres</a>, '
            f'including B2 for settlement from {data_lunga(DATA_B2)}.</p>')


def genera_selt():
    pagina_selt_indice()
    for c in CITTA_PAG:
        pagina_selt_citta(c)
    for p in PAESI_PAG:
        pagina_selt_paese(p)


def controlli_selt():
    errori = []
    if len(CENTRI_UK) < 40 or len(CENTRI_EST) < 600:
        errori.append(f"selt: troppo pochi centri ({len(CENTRI_UK)}, {len(CENTRI_EST)})")
    if len(set(SLUG_SELT.values())) != len(SLUG_SELT):
        errori.append("selt: slug di città e Paesi duplicati")
    if {r[0] for r in CENTRI_UK + CENTRI_EST} - set(NOMI_FORN):
        errori.append(f"selt: fornitori senza nome: {({r[0] for r in CENTRI_UK + CENTRI_EST} - set(NOMI_FORN))}")
    if not CITTA_PAG or not PAESI_PAG:
        errori.append("selt: nessuna città o nessun Paese con domanda (rilanciare raccolta/selt.py --domanda)")
    if DATA_B2 != "2027-03-26" or "These changes will come into force on 26 March 2027" not in " ".join(HC1691["frasi_memorandum"]):
        errori.append("selt: data del B2 diversa da quella letta nella nota esplicativa di HC 1691")
    for k in ("partner_primo", "partner_proroga", "cittadinanza_residenza", "skilled_worker", "skilled_worker_prima", "health_care", "studente", "hpi", "scale_up"):
        if k not in LIV or LIV[k].get("http") != 200:
            errori.append(f"selt: livello {k} non letto")
    if URL_ITALKI and not URL_ITALKI.startswith("https://www.italki.com/"):
        errori.append("selt: link italki non valido in dati/affiliati.json (_italki_selt)")
    if any(f not in FORN or not FORN[f].get("url", "").startswith("https://") for f in NOMI_FORN):
        errori.append("selt: link dei fornitori mancanti in dati/selt.json")
    return errori


# ---------------------------------------------------------------- Thailand DTV visa, embassy by embassy (30/10/2026)
# Dati: dati/dtv.json (raccolta/dtv.py): elenco ufficiale delle sedi (www.thaiembassy.org), pagine DTV lette con i frammenti di testo
# controllati a ogni lancio, regola generale dal 31/8/2026 ed esenzione dal visto di 30 giorni dal 15/9/2026.
# Pagine: /thailand-dtv-visa/ (indice con la tabella delle sedi) e /thailand-dtv-visa/<sede>/ solo per le sedi con domanda e dati.
DTV = json.loads((DATI / "dtv.json").read_text(encoding="utf-8"))
SEZ_DTV = "thailand-dtv-visa/"
LET_DTV = DTV["letture"]
SEDI_DTV = DTV["sedi"]
GEN_DTV = DTV["generale"]
LETTO_DTV = DTV["letto_il"]
_SWD = AFFILIATI.get("_safetywing_dtv", {})
URL_SW_DTV = _SWD.get("url", "")
PAG_DTV = [L for L in LET_DTV if L["domanda"] and ("costo" in L or "residenza" in L)]
VALUTE_DTV = {"GBP": ("£", ""), "USD": ("US$", ""), "EUR": ("€", ""), "THB": ("", " baht"), "MYR": ("RM", ""), "SGD": ("S$", ""),
              "EGP": ("", " Egyptian pounds"), "PLN": ("", " złoty"), "INR": ("₹", ""), "CNY": ("", " yuan")}


def costo_dtv(c):
    pre, post = VALUTE_DTV[c["valuta"]]
    return f'{pre}{intero(c["importo"])}{post}' + ("" if pre in ("£", "€", "US$", "S$", "RM", "₹") else f' ({c["valuta"]})')


def eur_dtv(c):
    if c["valuta"] == "EUR":
        return c["importo"]
    r = CAMBI["tassi"].get(c["valuta"])
    return c["importo"] / r if r else None


def pagina_dtv_url(L, i=None):
    return L["pagine"][L[i]["p"] if i else 0]["url"]


def citazione(v):
    """Frammento ufficiale tra virgolette (con la nostra traduzione se la pagina non è in inglese)."""
    if v.get("traduzione"):
        return f'{escape(v["traduzione"])}: “{escape(v["frammento"])}”'
    return f'“{escape(v["frammento"].rstrip("."))}”'


def residenza_dtv(L, breve=False):
    r = L.get("residenza")
    if not r:
        return "Not written in the text of the page"
    data = L["pagine"][r["p"]]["modificata"]
    if r["tipo"] == "vecchia":
        return f'Page last updated on {data_lunga(data)}, before the 31 August 2026 change: {citazione(r)}'
    return citazione(r)


def paese_art(p):
    """Nome del Paese con l'articolo quando l'inglese lo vuole (the United Kingdom, the United States...)."""
    return ("the " + p) if p.startswith(("United ", "Philippines", "Netherlands", "Czech Republic", "Republic of")) else p


def nome_sede(L):
    return f'Royal Thai {"Embassy" if L["tipo"] == "Embassy" else "Consulate-General"} in {L["sede"]}'


def fonte_dtv_p(L):
    voci = "; ".join(f'<a href="{escape(pg["url"])}" rel="noopener">{escape(pg["titolo"])}</a> (updated by the {"embassy" if L["tipo"] == "Embassy" else "consulate"} on '
                     f'{data_lunga(pg["modificata"])})' for pg in L["pagine"])
    return f'<p class="fonte">Source: {escape(nome_sede(L))}, official website: {voci}. Read on {data_lunga(LETTO_DTV)}.</p>'


def fonte_regola_p():
    o, m = GEN_DTV["regola_osaka"], GEN_DTV["regola_mosca"]
    a = DTV["fonti"]["annuncio_mfa"]
    return (f'<p class="fonte">Sources: <a href="{escape(a["url"])}" rel="noopener">announcement of the Department of Consular Affairs</a>, Ministry of Foreign Affairs of Thailand, '
            f'dated {data_lunga(a["data"])} (in Thai), as reported by the <a href="{escape(m["url"])}" rel="noopener">Royal Thai Embassy in Moscow</a> and the '
            f'<a href="{escape(o["url"])}" rel="noopener">Royal Thai Consulate-General in Osaka</a> (pages read on {data_lunga(LETTO_DTV)}).</p>')


def fonte_esenzione_p():
    l, w = GEN_DTV["esenzione_londra"], GEN_DTV["esenzione_washington"]
    return (f'<p class="fonte">Sources: Royal Thai Embassy, London, <a href="{escape(l["url"])}" rel="noopener">Visa Exemption and Visa on Arrival Schemes</a> '
            f'(updated {data_lunga(l["modificata"])}); Royal Thai Embassy, Washington, DC, <a href="{escape(w["url"])}" rel="noopener">New Visa Exemption and Visa on Arrival</a> '
            f'(updated {data_lunga(w["modificata"])}). Read on {data_lunga(LETTO_DTV)}.</p>')


AVVISO_DTV = ('<p class="avviso"><strong>Not legal or immigration advice.</strong> This page reports what the official pages of the Thai embassies and consulates said '
              'on the date we read them. Each mission decides on its own applications and can ask for more documents or an interview; paying the fee does not mean '
              'the visa will be granted, and the fee is not refunded. Check the official page of the mission and the '
              f'<a href="{DTV["fonti"]["evisa"]["url"]}" rel="noopener">Thai e-Visa website</a> before you apply.</p>')


def regola_dtv(rel, breve=False):
    a = DTV["fonti"]["annuncio_mfa"]
    if breve:
        return (f'<section class="card" id="rule-2026"><h2 style="margin-top:0">{ico("calendar")} The rule since 31 August 2026</h2>'
                f'<p>Since 31 August 2026 DTV applicants must submit <strong>proof of permanent residence in the country or territory where they apply</strong> and a '
                f'<strong>criminal record certificate</strong> (Department of Consular Affairs, announcement of {data_lunga(a["data"])}). '
                f'Applications submitted before that date follow the old rules. <a href="{rel}{SEZ_DTV}#rule-2026">What changed</a>.</p>{fonte_regola_p()}</section>')
    return f"""<h2 id="rule-2026">What changed on 31 August 2026</h2>
<p>The Department of Consular Affairs of Thailand's Ministry of Foreign Affairs announced on {data_lunga(a["data"])} two changes to the documents for DTV applications, in force since 00.00 on 31 August 2026 (Thailand time):</p>
<ul class="testo"><li><strong>Proof of permanent residence</strong> replaces the earlier "document indicating current location". The Consulate-General in Osaka words it as “{escape(GEN_DTV["regola_osaka"]["frammenti"][1])}”.</li>
<li><strong>A certificate of criminal record clearance</strong> is added, “{escape(GEN_DTV["regola_osaka"]["frammenti"][2])}” (Osaka).</li>
<li>Applications submitted before 31 August 2026 are processed under the earlier requirements.</li></ul>
<p>In practice this means you apply where you live permanently, not where you happen to be travelling. Some missions spell it out: Singapore grants the DTV only to Singapore citizens and permanent residents; Vientiane asks applicants to be Lao nationals or permanent residents of the Lao PDR; Ho Chi Minh City accepts only a Temporary or Permanent Residence Card from foreigners. Check the row for your mission in the table.</p>
{fonte_regola_p()}"""


def esenzione_dtv(rel, breve=False):
    if breve:
        return (f'<p class="small">{ico("check")} Not sure you need a DTV? Since 15 September 2026, British, Irish and US passport holders, among others, can visit Thailand '
                f'without a visa for up to 30 days for tourism. <a href="{rel}{SEZ_DTV}#visa-exemption">Visa exemption rules</a>.</p>')
    l = GEN_DTV["esenzione_londra"]["frammenti"]
    return f"""<h2 id="visa-exemption">Visa exemption: 30 days since 15 September 2026</h2>
<p>For short tourist trips you may not need a DTV at all. Since 15 September 2026 the visa exemption is <strong>30 days</strong>: the Royal Thai Embassy in London writes that British and Irish passport holders, "as well as foreign travellers from many other countries", "{escape(l[2])}", and the Embassy in Washington lists 60 countries and territories, the United States among them (the list is an image on its page).</p>
<ul class="testo"><li>Eligible passport holders can use the exemption "{escape(l[3])}" (London).</li>
<li>Immigration officers may ask for "{escape(l[4])}" and for proof of accommodation and onward travel within 30 days.</li>
<li>The London page says "{escape(l[5])}", through Thailand's Immigration Bureau.</li>
<li>For Indian ordinary passport holders, the Embassy in New Delhi says the 30-day exemption "remains effective from 15 September 2026 until further announcement".</li></ul>
{fonte_esenzione_p()}"""


def box_assicurazione_dtv(rel):
    """Riquadro SafetyWing dopo le informazioni ufficiali. Le pagine DTV lette non chiedono un'assicurazione: il riquadro lo dice."""
    base = ("None of the DTV pages we read asks for health insurance (they ask for a passport, a photo, proof of residence, bank statements, "
            "a criminal record certificate and proof of the purpose of your stay).")
    if not URL_SW_DTV:
        return ""
    return (f'<section class="card aff-r" aria-labelledby="aff-d-h"><div class="aff-r-t"><span class="ic">{ico("shield")}</span>'
            f'<h2 id="aff-d-h">Health cover for a long stay</h2><span class="aff-tag">Affiliate</span></div>'
            f'<p>{base} A DTV allows stays of up to 180 days per entry. If you want health cover for a long stay, '
            f'compare policies before you travel.</p>'
            f'<p class="aff-r-cta"><a class="btn" href="{escape(URL_SW_DTV)}" rel="sponsored noopener" target="_blank">See SafetyWing nomad insurance{ico("arrow")}'
            f'<span class="sr"> (opens in a new tab)</span></a></p>'
            f'<p class="small">SafetyWing sells travel medical insurance for travellers and nomads online. {MON.RIGA_EN} Insurance is not a DTV requirement on the pages we read '
            f'and does not change the decision on your visa.</p></section>')


def riga_dtv(L, rel_sez):
    link = f'<a href="{rel_sez}{L["id"]}/">{escape(L["sede"])}</a>' if L in PAG_DTV else escape(L["sede"])
    c = L.get("costo")
    costo = (f'<td data-v="{eur_dtv(c) or 0:.2f}">{costo_dtv(c)}</td>' if c else '<td data-v="">Not written on the page</td>')
    e = eur_dtv(c) if c else None
    eur = f'<td class="n" data-v="{e:.2f}">€{intero(round(e))}</td>' if e else '<td class="n" data-v="">–</td>'
    pg = L["pagine"][0]
    agg = max(x["modificata"] for x in L["pagine"])
    return (f'<tr><td>{link}<br><span class="small">{escape(L["paese"])} · {"embassy" if L["tipo"] == "Embassy" else "consulate"}</span></td>{costo}{eur}'
            f'<td class="small">{residenza_dtv(L)}</td><td><a href="{escape(pg["url"])}" rel="noopener">official page</a></td>'
            f'<td data-v="{agg.replace("-", "")}">{data_lunga(agg)}</td></tr>')


def pagina_dtv_indice():
    rel = "../"
    percorso = SEZ_DTV
    con_costo = [L for L in LET_DTV if "costo" in L]
    con_res = [L for L in LET_DTV if "residenza" in L]
    lon = next(L for L in LET_DTV if L["id"] == "london")
    vie = next(L for L in LET_DTV if L["id"] == "vientiane")
    was = next(L for L in LET_DTV if L["id"] == "washington-dc")
    ordinate = sorted(LET_DTV, key=lambda L: (0 if "costo" in L else 1, L["paese"], L["sede"]))
    righe = "".join(riga_dtv(L, "") for L in ordinate)
    lette = {L["sito"].split("//")[1].replace("www.", "") for L in LET_DTV}
    altre = [s for s in SEDI_DTV if not s["dtv"]]
    def stato(s):
        if s["http"] != 200:
            return "website not reachable from our checks"
        if s.get("sistema") == "other":
            return "own website (different system), not read"
        if s.get("lingua_home") == "th":
            return "website in Thai, no DTV page found"
        return "no DTV page found"
    righe_altre = "".join(f'<tr><td>{escape(s["sede"])}</td><td>{escape(s["paese"])}</td><td><a href="{escape(s["sito"])}" rel="noopener">website</a></td><td class="small">{stato(s)}</td></tr>'
                          for s in sorted(altre, key=lambda s: (s["paese"], s["sede"])))
    vecchie = [L for L in LET_DTV if L.get("residenza", {}).get("tipo") == "vecchia"]
    prima = sorted([L for L in LET_DTV if max(x["modificata"] for x in L["pagine"]) < "2026-08-31"], key=lambda L: L["sede"])
    eur = sorted(((eur_dtv(L["costo"]), L["id"]) for L in con_costo if eur_dtv(L["costo"])))
    domande = [
        ("How much does the Thailand DTV visa cost?",
         f"It depends on the embassy or consulate, and each charges in its own currency. On the pages we read on {data_lunga(LETTO_DTV)}: "
         + "; ".join(f'{L["sede"]} {costo_dtv(L["costo"])}' for L in sorted(con_costo, key=lambda L: L["sede"])) + "."),
        ("Can I apply for the DTV in a country where I am only a tourist?",
         "Not since 31 August 2026 at most missions: applicants must submit proof of permanent residence in the country or territory where they apply. "
         "For example, Ho Chi Minh City accepts only a Temporary or Permanent Residence Card from foreigners, and Singapore grants the DTV only to its citizens and permanent residents."),
        ("Do I need health insurance for the DTV?",
         "None of the DTV pages we read lists health insurance among the required documents. Check the official page of your mission, because requirements can change."),
        ("How much money do I need in the bank for the DTV?",
         "Most pages ask for financial evidence of at least 500,000 baht, usually bank statements for the last 3 months. Some write it in their own currency: "
         "£12,000 in London, US$16,000 in Washington, €15,000 in Helsinki; Hong Kong asks for 150,000 Hong Kong dollars and Cairo for 850,000 Egyptian pounds."),
        ("Where do I apply for the DTV?",
         f"Online, on the Thai e-Visa website ({DTV['fonti']['evisa']['url']}), choosing the embassy or consulate for the place where you live. Some missions add their own rules: "
         "Vientiane takes the fee in cash and needs an appointment."),
        ("Do I need a DTV for a short holiday?",
         "Maybe not. Since 15 September 2026 many nationalities, including British, Irish and US citizens, can enter Thailand without a visa for up to 30 days for tourism."),
    ]
    ld = [ld_faq(domande), ld_dataset("Thailand DTV visa fees and residence rules by embassy",
                                      f"Fees and residence rules for the Destination Thailand Visa read on the official pages of {len(LET_DTV)} Thai embassies and consulates.",
                                      percorso, [DTV["fonti"]["elenco"]["url"]], LETTO_DTV, "https://creativecommons.org/licenses/by/4.0/")]
    corpo = f"""<section class="hero">{h1_diviso(f"Thailand DTV visa by embassy: fees and who can apply where ({ANNO})")}
<p class="lead">The Destination Thailand Visa (DTV) fee depends on where you apply: <strong>{costo_dtv(vie["costo"])}</strong> in cash at the embassy in Vientiane, <strong>{costo_dtv(lon["costo"])}</strong> in London and <strong>{costo_dtv(was["costo"])}</strong> in Washington, according to the official pages of the Thai embassies and consulates we read on {data_lunga(LETTO_DTV)}. Since 31 August 2026 you also need proof of permanent residence in the country where you apply and a criminal record certificate (Thai Ministry of Foreign Affairs).</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("passport")}<span>Thailand DTV visa</span><span>read on {data_lunga(LETTO_DTV)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Thai embassies and consulates with a DTV page we could read</span><span class="sr">: </span><strong>{len(LET_DTV)}</strong> of {len(SEDI_DTV)}</p>
<div class="kpi"><div><b>{len(con_costo)}</b><span>with the fee written on the page</span></div><div><b>{len(con_res)}</b><span>with a residence rule on the page</span></div><div><b>€{intero(round(eur[0][0]))}–€{intero(round(eur[-1][0]))}</b><span>fee range in euros (ECB rates of {data_lunga(CAMBI["data"])})</span></div><div><b>30 days</b><span>visa exemption since 15 September 2026</span></div></div>
<p class="fonte">Source: official websites of the Thai embassies and consulates-general (list: <a href="{DTV["fonti"]["elenco"]["url"]}" rel="noopener">Ministry of Foreign Affairs of Thailand</a>), read on {data_lunga(LETTO_DTV)}. Every row links to the page it comes from.</p>
</div></section>
{AVVISO_DTV}
{AD}
<h2 id="table">DTV fee and residence rule, embassy by embassy</h2>
<p class="small">One row per embassy or consulate whose DTV page we could read. "Who can apply here" quotes the page. "Updated" is the date the mission last edited the page. Euro amounts are approximate (ECB reference rates of {data_lunga(CAMBI["data"])}); you pay in the currency shown. Type to filter, or tap a column heading to sort.</p>
<p class="filtro"><label><span class="sr">Filter by city or country</span><input type="search" placeholder="Filter: e.g. Vietnam" data-filtro="t-dtv" autocomplete="off"></label></p>
<div class="tab compatta"><table class="ord larga" id="t-dtv"><caption class="sr">Thailand DTV visa fee and residence rule by Thai embassy and consulate</caption><thead><tr>{th_ord("Embassy or consulate", False, "ascending")}{th_ord("Fee")}{th_ord("≈ in euros")}<th scope="col">Who can apply here (residence)</th><th scope="col">Official page</th>{th_ord("Updated")}</tr></thead><tbody>{righe}</tbody></table></div>
<p class="fonte">Source: the official page linked in each row (websites of the Royal Thai Embassies and Consulates-General, Ministry of Foreign Affairs of Thailand), read on {data_lunga(LETTO_DTV)}. Fees in US dollars for Los Angeles, New York and Chicago come from the consulates' fee tables, which give the amount without a currency sign.</p>
<p class="small">{len(prima)} of these pages were last updated before 31 August 2026 ({", ".join(L["sede"] for L in prima)}), so the ones that do not quote the new residence rule may be out of date; {len(vecchie)} of them ({", ".join(L["sede"] for L in vecchie)}) still describe the earlier rule. Several missions publish the DTV rules only as images or in Thai: we list them with "Not written on the page". Check with the mission before you apply.</p>
{regola_dtv(rel)}
{esenzione_dtv(rel)}
<h2>How to apply</h2>
<ul class="testo"><li>Apply online on the <a href="{DTV["fonti"]["evisa"]["url"]}" rel="noopener">Thai e-Visa website</a> and choose the embassy or consulate for the place where you live permanently.</li>
<li>Prepare the documents on your mission's page: passport, photo, proof of permanent residence, bank statements (usually at least 500,000 baht over 3 months), a criminal record certificate and proof of the purpose (remote work, Muay Thai or cooking course, medical treatment, or being the spouse or child of a DTV holder).</li>
<li>The DTV is valid for 5 years with multiple entries and stays of up to 180 days per entry, extendable once by up to 180 days at the Immigration Bureau, as the London page and others say.</li>
<li>Processing can take a month or more (Kuala Lumpur: "approximately 1 month or more"). Fees are not refunded.</li></ul>
<p class="fonte">Source: <a href="{escape(lon["pagine"][0]["url"])}" rel="noopener">Royal Thai Embassy, London, Destination Thailand Visa</a> (updated {data_lunga(lon["pagine"][0]["modificata"])}) and the pages linked in the table, read on {data_lunga(LETTO_DTV)}.</p>
{box_assicurazione_dtv(rel)}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>Embassy pages on this site</h2>
<div class="griglia">{"".join(f'<a href="{L["id"]}/"><span class="ic">{ico("passport")}</span><span>DTV visa in {escape(L["sede"])}<small>{costo_dtv(L["costo"]) if "costo" in L else "fee not on the page"} · {escape(L["paese"])}</small></span></a>' for L in sorted(PAG_DTV, key=lambda L: L["sede"]))}</div>
<h2 id="other-missions">Other Thai embassies and consulates</h2>
<p class="small">{len(altre)} of the {len(SEDI_DTV)} missions on the Ministry's list: we did not find a DTV page we could read on their websites on {data_lunga(LETTO_DTV)} (we looked at the menu and the visa pages). Check their websites or the e-Visa system.</p>
<p class="filtro"><label><span class="sr">Filter missions</span><input type="search" placeholder="Filter: e.g. Japan" data-filtro="t-altre" autocomplete="off"></label></p>
<div class="tab compatta"><table class="ord" id="t-altre"><thead><tr>{th_ord("Mission", False, "ascending")}{th_ord("Country", False, "ascending")}<th scope="col">Website</th><th scope="col">What we found</th></tr></thead><tbody>{righe_altre}</tbody></table></div>
<p class="fonte">Source: list of Royal Thai Embassies and Consulates-General, <a href="{DTV["fonti"]["elenco"]["url"]}" rel="noopener">Ministry of Foreign Affairs of Thailand</a>, read on {data_lunga(LETTO_DTV)}.</p>
<p><a href="{rel}digital-nomad-visa-income-requirements/">Digital nomad visa income requirements in Europe</a> · <a href="{rel}{SEZ}">Visa refusal rates</a> · <a href="{rel}">Visa income calculator</a></p>"""
    titolo = f"Thailand DTV visa by embassy {ANNO}: fees and residence rules"
    descr = (f"DTV visa fee and residence rule at {len(LET_DTV)} Thai embassies and consulates: {costo_dtv(vie['costo'])} in Vientiane, {costo_dtv(lon['costo'])} in London, "
             f"{costo_dtv(was['costo'])} in Washington. Proof of permanent residence since 31 August 2026; 30-day visa exemption since 15 September 2026.")
    pagina(percorso, titolo, descr, corpo, ordina=True, jsonld_extra=ld, briciole=[("Thailand DTV visa by embassy", percorso)])


def pagina_dtv_sede(L):
    rel = "../../"
    percorso = f"{SEZ_DTV}{L['id']}/"
    c, r, s = L.get("costo"), L.get("residenza"), L.get("saldo")
    stesso = [x for x in LET_DTV if x["paese"] == L["paese"] and x["id"] != L["id"]]
    agg = max(x["modificata"] for x in L["pagine"])
    chi = nome_sede(L)
    frasi = []
    if c:
        pc = L["pagine"][c["p"]]["modificata"]
        note = [escape(c["nota"])] if c.get("nota") else []
        if pc < "2026-08-31" and pc != agg:
            note.append(f'fee page last updated on {data_lunga(pc)}')
        frasi.append(f'lists the DTV fee as <strong>{costo_dtv(c)}</strong>' + (f' ({"; ".join(note)})' if note else ""))
    else:
        frasi.append('does not write the DTV fee in the text of its page')
    if r:
        if r["tipo"] == "vecchia":
            frasi.append(f'its page, last updated on {data_lunga(L["pagine"][r["p"]]["modificata"])} before the 31 August 2026 change, says on residence: {citazione(r)}')
        elif r.get("traduzione"):
            frasi.append(f'on residence, the page says that applicants {escape(r["traduzione"].replace(" (our translation from Spanish)", ""))} (our translation from Spanish)')
        else:
            frasi.append(f'on residence, the page says: {citazione(r)}')
    elif agg < "2026-08-31":
        frasi.append(f"its page, last updated on {data_lunga(agg)} before the 31 August 2026 change, does not write a residence rule; the general rule since that date is proof of permanent residence in the country where you apply")
    else:
        frasi.append("its page does not write a residence rule, so the general rule applies: proof of permanent residence in the country where you apply, since 31 August 2026")
    prima = (f'The {escape(chi)} ' + "; ".join(frasi[:1]) + "".join("; " + f for f in frasi[1:]) + f' (official page updated on {data_lunga(agg)}, read on {data_lunga(LETTO_DTV)}).')
    righe = []
    if c:
        righe.append(("Fee", costo_dtv(c) + (f' <span class="small">≈ €{intero(round(eur_dtv(c)))}</span>' if eur_dtv(c) and c["valuta"] != "EUR" else ""),
                      f'“{escape(c["frammento"])}”' + (f' · {escape(c["nota"])}' if c.get("nota") else ""), L["pagine"][c["p"]]))
    else:
        righe.append(("Fee", "Not written on the page", "Check the e-Visa system when you apply.", L["pagine"][0]))
    righe.append(("Who can apply here", residenza_dtv(L) if r else "Not written on the page (general rule: proof of permanent residence in the country where you apply)",
                  "" if not r else ("Page updated before 31 August 2026" if r["tipo"] == "vecchia" else ""), L["pagine"][r["p"]] if r else L["pagine"][0]))
    if s:
        righe.append(("Money to show", citazione(s), "", L["pagine"][s["p"]]))
    for a in L.get("altre", []):
        righe.append(("Also on the page", citazione(a), "", L["pagine"][a["p"]]))
    tab = "".join(f'<tr><th scope="row" style="vertical-align:top">{escape(a)}</th><td style="vertical-align:top">{b}{(" <span class=\"small\">" + cc + "</span>") if cc and a != "Fee" else ""}'
                  f'{("<br><span class=\"small\">" + cc + "</span>") if cc and a == "Fee" else ""}</td>'
                  f'<td style="vertical-align:top"><a href="{escape(pg["url"])}" rel="noopener">{escape(pg["titolo"][:60])}</a><br><span class="small">updated {data_lunga(pg["modificata"])}</span></td></tr>'
                  for a, b, cc, pg in righe)
    nota_paese = ""
    if L["id"] == "ho-chi-minh-city":
        h = next((x for x in LET_DTV if x["id"] == "hanoi"), None)
        if h:
            nota_paese = (f'<p>The Royal Thai Embassy in Hanoi also has a DTV page (<a href="{escape(h["pagine"][0]["url"])}" rel="noopener">official page</a>, '
                          f'updated {data_lunga(h["pagine"][0]["modificata"])}), but its content is published as images in Thai, so we could not read the fee or the rules there.</p>')
    domande = [
        (f"How much is the DTV visa in {L['sede']}?",
         (f"The {chi} lists the fee as {costo_dtv(c)}" + (f" ({c['nota']})" if c.get("nota") else "") + f", on its page updated on {data_lunga(L['pagine'][c['p']]['modificata'])}. Fees are not refunded."
          if c else f"The {chi} does not write the fee on its DTV page. The e-Visa system shows it when you apply.")),
        (f"Can I apply for the DTV in {L['sede']} if I do not live in {paese_art(L['paese'])}?",
         ("Since 31 August 2026 applicants must submit proof of permanent residence in the country or territory where they apply. "
          + ((f"The {chi}'s page was last updated on {data_lunga(L['pagine'][r['p']]['modificata'])}, before that change, and still says: {re.sub(r'<[^>]+>', '', citazione(r))}." if r["tipo"] == "vecchia"
              else f"The {chi} writes that applicants {r['traduzione'].replace(' (our translation from Spanish)', '')} (our translation from Spanish): “{r['frammento']}”." if r.get("traduzione")
              else f"The {chi} writes: {re.sub(r'<[^>]+>', '', citazione(r))}.") if r else "This mission's page does not add its own wording."))),
        (f"How much money do I need for the DTV in {L['sede']}?",
         (f"The {chi} asks for financial evidence: " + re.sub(r"<[^>]+>", "", citazione(s)) + "." if s else "Most missions ask for at least 500,000 baht in bank statements over 3 months; this page does not give an amount.")),
        ("Do I need health insurance for the DTV?", "The DTV pages we read, this one included, do not list health insurance among the required documents."),
    ]
    altri_paese = (f'<h2>Other Thai missions in {escape(paese_art(L["paese"]))}</h2><ul class="testo">' + "".join(
        f'<li>{(f"<a href=\"../{x["id"]}/\">" + escape(x["sede"]) + "</a>") if x in PAG_DTV else escape(x["sede"])}: '
        f'{("fee " + costo_dtv(x["costo"])) if "costo" in x else "fee not written on the page"}; residence: {residenza_dtv(x)[0].lower() + residenza_dtv(x)[1:] if not x.get("residenza") else residenza_dtv(x)}</li>' for x in stesso) + "</ul>") if stesso else ""
    corpo = f"""<section class="hero"><h1>Thailand DTV visa in {escape(L["sede"])}: fee and who can apply ({ANNO})</h1>
<p class="lead">{prima}</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{bandiera(L["paese"]) if '<svg class="flag"' in bandiera(L["paese"]) else ico("passport")}<span>{escape(chi)}</span><span>read on {data_lunga(LETTO_DTV)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">DTV fee in {escape(L["sede"])}</span><span class="sr">: </span><strong>{costo_dtv(c) if c else "not on the page"}</strong></p>
<div class="kpi"><div><b>{("€" + intero(round(eur_dtv(c)))) if c and eur_dtv(c) else "–"}</b><span>approximately, in euros (ECB {data_lunga(CAMBI["data"])})</span></div><div><b>{"Yes" if r and r["tipo"] != "vecchia" else ("Old rule" if r else "Not written")}</b><span>residence rule on the page</span></div><div><b>{data_lunga(agg)}</b><span>page last updated by the mission</span></div><div><b>5 years</b><span>validity, multiple entries</span></div></div>
{fonte_dtv_p(L)}
</div></section>
{AVVISO_DTV}
{AD}
<h2>What the official page says</h2>
<div class="tab compatta"><table id="t-sede"><caption class="sr">DTV rules at the {escape(chi)}</caption><thead><tr><th scope="col">Item</th><th scope="col">Official wording</th><th scope="col">Page</th></tr></thead><tbody>{tab}</tbody></table></div>
{fonte_dtv_p(L)}
{nota_paese}
{regola_dtv(rel, breve=True)}
{esenzione_dtv(rel, breve=True)}
{altri_paese}
{box_assicurazione_dtv(rel)}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<p><a href="../">Thailand DTV visa: all embassies and consulates</a> · <a href="{rel}digital-nomad-visa-income-requirements/">Digital nomad visa income requirements</a> · <a href="{rel}">Visa income calculator</a></p>"""
    titolo = titolo_breve([f"Thailand DTV visa in {L['sede']} ({ANNO}): fee and who can apply", f"DTV visa {L['sede']} {ANNO}: fee and residence rule",
                           f"DTV visa {L['sede']} {ANNO}: fee and rules", f"DTV visa {L['sede']} ({ANNO})"])
    descr = (f"DTV visa at the {chi}: " + (f"fee {costo_dtv(c)}" if c else "fee not written on the page")
             + f", who can apply there (residence rule), money to show and the official page (updated {data_lunga(agg)}, read {data_lunga(LETTO_DTV)}).")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande)],
           briciole=[("Thailand DTV visa by embassy", SEZ_DTV), (L["sede"], percorso)])


def genera_dtv():
    pagina_dtv_indice()
    for L in PAG_DTV:
        pagina_dtv_sede(L)


def controlli_dtv():
    errori = []
    if len(SEDI_DTV) < 80:
        errori.append(f"dtv: elenco delle sedi troppo corto ({len(SEDI_DTV)})")
    if len(LET_DTV) < 20 or len(PAG_DTV) < 5:
        errori.append("dtv: troppo poche sedi lette o con pagina")
    for L in LET_DTV:
        if "costo" in L and L["costo"]["valuta"] not in VALUTE_DTV:
            errori.append(f"dtv: valuta {L['costo']['valuta']} senza simbolo (VALUTE_DTV)")
        if any(not pg.get("modificata") or pg.get("http") != 200 for pg in L["pagine"]):
            errori.append(f"dtv: pagina di {L['id']} senza data o non letta")
    if URL_SW_DTV and not URL_SW_DTV.startswith("https://safetywing.com/"):
        errori.append("dtv: link SafetyWing non valido in dati/affiliati.json (_safetywing_dtv)")
    if len({L["id"] for L in LET_DTV}) != len(LET_DTV):
        errori.append("dtv: id doppi")
    return errori


# ---------------------------------------------------------------- Studenti: US OPT / STEM OPT e UK Graduate visa (30/10/2026)
# Dati: dati/opt.json (raccolta/opt.py: USCIS, ICE/SEVP, Federal Register, eCFR) e dati/graduate.json (raccolta/graduate.py: GOV.UK).
# Ogni cifra delle pagine viene da "letture" (valore + frammento del testo ufficiale, ricontrollato a ogni raccolta).
# I calcolatori (STUDIO_JS) girano nel browser; verifica.py confronta i loro risultati con un calcolo Python indipendente.
OPT = json.loads((DATI / "opt.json").read_text(encoding="utf-8"))
GRAD = json.loads((DATI / "graduate.json").read_text(encoding="utf-8"))
SEZ_OPT = "us-opt/"
SEZ_GRAD = "uk-graduate-visa/"
LO, FO, FR_OPT = OPT["letture"], OPT["fonti"], OPT["federal_register"]
LG, FG = GRAD["letture"], GRAD["fonti"]
LETTO_OPT, LETTO_GRAD = OPT["letto_il"], GRAD["letto_il"]
_MESI_US = {m: i + 1 for i, m in enumerate(MESI)}


def vo(k):
    return LO[k]["valore"]


def vg(k):
    return LG[k]["valore"]


def data_us(s):
    """'10/07/2026' (USCIS) o 'July 27, 2026' (Study in the States) -> ISO; '' se non si legge."""
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", s or "")
    if m:
        return f"{m.group(3)}-{m.group(1)}-{m.group(2)}"
    m = re.fullmatch(r"([A-Z][a-z]+) (\d{1,2}), (\d{4})", s or "")
    if m and m.group(1) in _MESI_US:
        return f"{m.group(3)}-{_MESI_US[m.group(1)]:02d}-{int(m.group(2)):02d}"
    return ""


def usd(n):
    return f"${n:,}"


def gbp(x):
    """£1,552.50 / £937 (senza ,00 per gli importi interi), come gbp() del JS."""
    s = f"{x:,.2f}"
    return "£" + (s[:-3] if s.endswith(".00") else s)


def link_fonte_opt(k):
    f = FO[k]
    agg = data_us(f.get("aggiornata", ""))
    return (f'<a href="{escape(f["url"])}" rel="noopener">{escape(f["editore"].split(" (")[0])}, {escape(f["titolo"])}</a>'
            + (f' (page updated {data_lunga(agg)})' if agg else ""))


def link_fr(k, breve=False):
    d = FR_OPT[k]
    tipo = {"Proposed Rule": "proposed rule", "Rule": "final rule", "Notice": "notice"}[d["type"]]
    if breve:
        return f'<a href="{escape(d["html_url"])}" rel="noopener">{escape(d["citation"])}</a>'
    return f'Federal Register, <a href="{escape(d["html_url"])}" rel="noopener">{escape(d["title"])}</a> ({tipo}, {escape(d["citation"])}, {data_lunga(d["publication_date"])})'


def fonte_opt_p(chiavi=(), fr=(), extra=""):
    voci = [link_fonte_opt(k) for k in chiavi] + [link_fr(k) for k in fr]
    return f'<p class="fonte">Source{"s" if len(voci) > 1 else ""}: {"; ".join(voci)}{extra}. Read on {data_lunga(LETTO_OPT)}.</p>'


def link_fonte_grad(k):
    f = FG[k]
    return f'<a href="{escape(f["url"])}" rel="noopener">GOV.UK, {escape(f["titolo_nostro"])}</a>'


def fonte_grad_p(chiavi=(), extra=""):
    voci = [link_fonte_grad(k) for k in chiavi]
    return (f'<p class="fonte">Source{"s" if len(voci) > 1 else ""}: {"; ".join(voci)}{extra}. Read on {data_lunga(LETTO_GRAD)}. '
            f'Contains public sector information licensed under the Open Government Licence v3.0.</p>')


AVVISO_OPT = ('<p class="avviso"><strong>Not legal or immigration advice.</strong> This page reports what USCIS, ICE (SEVP) and the Federal Register said on the date we read them. '
              'Your designated school official (DSO) and USCIS decide on your case, and rules can change quickly: check with your DSO and USCIS before you file.</p>')
AVVISO_GRAD = ('<p class="avviso"><strong>Not legal or immigration advice.</strong> This page reports what GOV.UK and the Immigration Rules said on the date we read them. '
               'The Home Office decides on your application and can change the rules or the fees: check GOV.UK or ask the Home Office before you apply.</p>')

# Costanti dei calcolatori, dai dati ufficiali (le stesse nel JS e nei controlli)
K_FINESTRA = {"prima": vo("finestra")["prima"], "dopo": vo("finestra")["dopo"], "dso": vo("finestra")["dso"], "inizio": vo("inizio_max"),
              "nuova": vo("regola_30")}
K_STEM = {"prima": vo("finestra_stem")["prima"], "dso": vo("finestra_stem")["dso"], "proroga": vo("proroga_stem")}
K_DISOCC = {"opt": vo("disoccupazione"), "stem": vo("disoccupazione_stem")}
K_GRAD = {"cambio": vg("durata_18_mesi")["dal"], "m_prima": vg("durata_2_anni")["mesi"], "m_dopo": vg("durata_18_mesi")["mesi"],
          "m_phd": vg("durata_phd")["mesi"], "sett": vg("decisione_settimane"), "tassa": vg("tassa"), "ihs_a": vg("ihs_adulti"), "ihs_m": vg("ihs_minori")}

STUDIO_JS = r"""
(function(){
var M=['January','February','March','April','May','June','July','August','September','October','November','December'];
function pd(s){var m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(s||'');if(!m)return null;var d=new Date(Date.UTC(+m[1],+m[2]-1,+m[3]));return (d.getUTCMonth()===+m[2]-1&&d.getUTCDate()===+m[3])?d:null;}
function ad(d,n){return new Date(d.getTime()+n*864e5);}
function iso(d){return d.toISOString().slice(0,10);}
function am(d,n){var t=new Date(Date.UTC(d.getUTCFullYear(),d.getUTCMonth()+n,1));var u=new Date(Date.UTC(t.getUTCFullYear(),t.getUTCMonth()+1,0)).getUTCDate();return new Date(Date.UTC(t.getUTCFullYear(),t.getUTCMonth(),Math.min(d.getUTCDate(),u)));}
function gg(a,b){return Math.round((pd(b)-pd(a))/864e5);}
function dl(s){var d=pd(s);return d?d.getUTCDate()+' '+M[d.getUTCMonth()]+' '+d.getUTCFullYear():'';}
function gbp(x){var s=(Math.round(x*100)/100).toFixed(2);if(s.slice(-3)==='.00')s=s.slice(0,-3);return '£'+s.replace(/\B(?=(\d{3})+(?!\d))/g,',');}
var C={
finestra:function(fine,dso,k){var e=pd(fine);if(!e)return null;var r={apre:iso(ad(e,-k.prima)),chiude:iso(ad(e,k.dopo)),limite:'fine',inizio_max:iso(ad(e,k.inizio)),chiude_30:iso(ad(e,k.nuova))};
 var d=pd(dso);if(d){var l=iso(ad(d,k.dso));r.dso_entro=l;if(l<r.chiude){r.chiude=l;r.limite='dso';}if(l<r.chiude_30)r.chiude_30=l;if(iso(d)>r.apre){r.apre=iso(d);r.apre_dso=true;}}
 r.impossibile=r.apre>r.chiude;return r;},
disoccupazione:function(inizio,limite,usati,oggi){var s=pd(inizio);if(!s)return null;var r={limite:limite,ultimo:iso(ad(s,limite-1)),oltre:iso(ad(s,limite))};
 if(usati!==null&&usati!==''&&!isNaN(+usati)){var u=Math.max(0,Math.floor(+usati));r.usati=u;r.rimasti=Math.max(0,limite-u);var o=pd(oggi);if(o&&r.rimasti>0)r.ultimo_da_oggi=iso(ad(o,r.rimasti-1));}return r;},
stem:function(scad,dso,k){var e=pd(scad);if(!e)return null;var r={apre:iso(ad(e,-k.prima)),scade:iso(e),proroga_fino:iso(ad(e,k.proroga))};
 var d=pd(dso);if(d){r.dso_entro=iso(ad(d,k.dso));if(iso(d)>r.apre){r.apre=iso(d);r.apre_dso=true;}}r.impossibile=r.apre>=r.scade||!!(r.dso_entro&&r.dso_entro<r.apre);return r;},
graduate:function(dom,tipo,dec,scad,k){var a=pd(dom);if(!a)return null;var m=tipo==='phd'?k.m_phd:(dom<k.cambio?k.m_prima:k.m_dopo);
 var d8=ad(a,k.sett*7);var r={mesi:m,prima_del_cambio:dom<k.cambio,giorni_al_cambio:gg(dom,k.cambio),fine_subito:iso(am(a,m)),decisione_8:iso(d8),fine_8:iso(am(d8,m))};
 var d=pd(dec);if(d){if(iso(d)<dom)r.dec_errore=true;else{r.decisione=iso(d);r.fine=iso(am(d,m));}}
 var s=pd(scad);if(s){r.scad=iso(s);r.tardi=dom>=iso(s);}return r;},
costo:function(mesi,adulti,figli,k){adulti=Math.max(1,Math.floor(+adulti||1));figli=Math.max(0,Math.floor(+figli||0));var ia=k.ihs_a*mesi/12,im=k.ihs_m*mesi/12;
 var t=(adulti+figli)*k.tassa,i=adulti*ia+figli*im;return {tasse:t,ihs:i,totale:t+i,ihs_adulto:ia,ihs_figlio:im,persone:adulti+figli};}
};
window.CALC_STUDIO=C;window.CALC_STUDIO_DATA={dl:dl,gbp:gbp};
function oggi(){var n=new Date();return n.getFullYear()+'-'+String(n.getMonth()+1).padStart(2,'0')+'-'+String(n.getDate()).padStart(2,'0');}
function riga(l,v,n){return '<li><span class="r-lab">'+l+'</span><b>'+v+'</b>'+(n?'<span class="small">'+n+'</span>':'')+'</li>';}
function stato(a,b,t){if(t<a)return 'The window opens in '+gg(t,a)+' day'+(gg(t,a)===1?'':'s')+'.';if(t<=b)return 'The window is open: '+(gg(t,b)+1)+' day'+(gg(t,b)===0?'':'s')+' left, today included.';return 'This window has closed.';}
var R={
finestra:function(f,k){var r=C.finestra(f.fine.value,f.dso.value,k);if(!r)return '<p class="small">Enter your program end date (on your Form I-20).</p>';
 if(r.impossibile)return '<div class="esito warn">With these dates there is no valid filing day: USCIS must receive Form I-765 within '+k.dso+' days of the DSO recommendation and no later than '+k.dopo+' days after the program end date. Ask your DSO.</div>';
 var t=oggi();return '<p class="r-lab">File Form I-765 for post-completion OPT</p><p class="tot">'+dl(r.apre)+' <span>to</span> '+dl(r.chiude)+'</p>'+
 '<p class="r-anno">'+stato(r.apre,r.chiude,t)+'</p><ul class="r-righe">'+
 riga('Earliest filing date',dl(r.apre),r.apre_dso?'the day your DSO recommends OPT in SEVIS':k.prima+' days before the program end date')+
 riga('Last filing date',dl(r.chiude),r.limite==='dso'?k.dso+' days after the DSO recommendation (earlier than '+k.dopo+' days after the program end date)':k.dopo+' days after the program end date'+(r.dso_entro?'':'; with a DSO recommendation, also within '+k.dso+' days of it'))+
 riga('Latest OPT start date you can request',dl(r.inizio_max),k.inizio+' days after the program end date')+
 '</ul><p class="small">On hold: a final rule of 17 July 2026 would cut the '+k.dopo+' days after the program end date to '+k.nuova+', making the last day '+dl(r.chiude_30)+(r.chiude_30===r.chiude?' (the same date: the DSO limit comes first)':'')+'; a federal court postponed it and USCIS applies the previous rules.</p>';},
disoccupazione:function(f,k){var lim=f.tipo.value==='stem'?k.stem:k.opt;var t=oggi();var r=C.disoccupazione(f.inizio.value,lim,f.usati.value,t);if(!r)return '<p class="small">Enter the start date on your OPT EAD card.</p>';
 var h='<p class="r-lab">Unemployment limit</p><p class="tot">'+lim+' <span>days in total</span></p><ul class="r-righe">'+
 riga('If you have no job from the start date','Day '+lim+' is '+dl(r.ultimo),'from '+dl(r.oltre)+' you would be over the limit');
 if(lim===k.stem&&r.usati===undefined)h+='<li class="small">The '+k.stem+' days include the days used during post-completion OPT (at most '+k.opt+'): enter them under "Days already used".</li>';
 if(r.usati!==undefined){h+=riga('Days left','<span>'+r.rimasti+'</span>',r.usati+' of '+lim+' days used');if(r.ultimo_da_oggi)h+=riga('If you stay without a job from today','Last day within the limit: '+dl(r.ultimo_da_oggi),'');else h+='<li class="esito no">No unemployment days left.</li>';}
 return h+'</ul>';},
stem:function(f,k){var r=C.stem(f.scad.value,f.dso.value,k);if(!r)return '<p class="small">Enter the end date on your current OPT EAD card.</p>';
 if(r.impossibile)return '<div class="esito warn">With these dates there is no valid filing day: ask your DSO.</div>';
 var dsoPrima=!!(r.dso_entro&&r.dso_entro<r.scade);
 return '<p class="r-lab">File the STEM OPT extension (Form I-765)</p><p class="tot">'+dl(r.apre)+(dsoPrima?' <span>to</span> '+dl(r.dso_entro):' <span>to before</span> '+dl(r.scade))+'</p>'+(dsoPrima?'<p class="r-anno">The '+k.dso+'-day limit from the DSO recommendation ends before your EAD expires, so it is your real deadline.</p>':'')+'<ul class="r-righe">'+
 riga('Window opens',dl(r.apre),r.apre_dso?'the day your DSO recommends the extension':k.prima+' days before your current OPT EAD expires')+
 riga('File before your current EAD expires',dl(r.scade),r.dso_entro?'and within '+k.dso+' days of the DSO recommendation: by '+dl(r.dso_entro):'and within '+k.dso+' days of the DSO recommendation')+
 riga('If the EAD expires while the application is pending','You can keep working up to '+dl(r.proroga_fino),'automatic extension of up to '+k.proroga+' days, if you filed on time')+'</ul>';},
graduate:function(f,k){var r=C.graduate(f.dom.value,f.tipo.value,f.dec.value,f.scad?f.scad.value:'',k);if(!r)return '<p class="small">Enter the date you will apply.</p>';
 var dur=r.mesi===36?'3 years':(r.mesi===24?'2 years':'18 months');var h='';
 if(r.tardi)h+='<div class="esito no">Your Student visa expires on '+dl(r.scad)+': you must apply before that date.</div>';
 h+='<p class="r-lab">Your Graduate visa lasts</p><p class="tot">'+dur+'</p><p class="r-anno">'+(r.mesi===36?'PhD or other doctoral qualification: 3 years, before and after 1 January 2027.':(r.prima_del_cambio?'Applying on or before 31 December 2026: 2 years. '+(r.giorni_al_cambio>0?'From 1 January 2027 it would be 18 months.':''):'Applying on or after 1 January 2027: 18 months.'))+'</p><ul class="r-righe">';
 if(r.decisione)h+=riga('Decision on '+dl(r.decisione),'Ends about '+dl(r.fine),dur+' from the decision date');
 else if(r.dec_errore)h+='<li class="esito warn">The decision date cannot be before the application date.</li>';
 h+=riga('If approved the day you apply','Ends about '+dl(r.fine_subito),'')+riga('If approved after '+k.sett+' weeks ('+dl(r.decisione_8)+')','Ends about '+dl(r.fine_8),'')+'</ul>';
 var c=C.costo(r.mesi,f.adulti?f.adulti.value:1,f.figli?f.figli.value:0,k);
 h+='<p class="r-lab" style="margin-top:14px">Cost for '+c.persone+' '+(c.persone===1?'person':'people')+'</p><p class="tot" style="font-size:1.9rem">'+gbp(c.totale)+'</p><p class="small">'+gbp(c.tasse)+' application fees + '+gbp(c.ihs)+' health surcharge ('+gbp(c.ihs_adulto)+' per adult'+(c.ihs_figlio&&f.figli&&+f.figli.value>0?', '+gbp(c.ihs_figlio)+' per child':'')+'). The visa starts on the decision date; the exact end date is on your eVisa.</p>';
 return h;}
};
document.querySelectorAll('[data-studio]').forEach(function(box){var tipo=box.getAttribute('data-studio');var k=JSON.parse(box.getAttribute('data-k'));var f=box.querySelector('form');var out=box.querySelector('[data-out]');
 if(f.dom&&!f.dom.value)f.dom.value=oggi();
 function go(){try{out.innerHTML=R[tipo](f,k);}catch(e){out.innerHTML='';}}
 f.addEventListener('input',go);f.addEventListener('change',go);f.addEventListener('submit',function(e){e.preventDefault();go();});go();});
})();
"""

CSS_STUDIO = (".r-righe{list-style:none;margin:12px 0 0;padding:0;display:grid;gap:8px}"
              ".r-righe li{background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:9px 12px;font-size:.92rem;line-height:1.4}"
              ".r-righe li b{display:block;font-family:var(--serif);font-size:1.08rem;color:var(--ink);margin:2px 0;font-variant-numeric:tabular-nums}"
              ".r-righe li .r-lab{display:block}.r-righe li .small{display:block}"
              ".calc .tot span{font-size:.95rem}.stato{display:inline-block;font-size:.72rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;"
              "border-radius:6px;padding:2px 8px;border:1px solid var(--line-2);white-space:nowrap}.stato.vigore{background:var(--ok-2);color:var(--ok)}"
              ".stato.proposta{background:var(--warn-2);color:var(--warn)}.stato.sospesa{background:var(--accent-2);color:var(--accent)}"
              "table.pila tbody th{text-transform:none;letter-spacing:0;font-size:.92rem;background:none;color:var(--ink);vertical-align:top}"
              "@media (max-width:640px){table.pila thead{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}"
              "table.pila,table.pila tbody,table.pila tr,table.pila th,table.pila td{display:block;width:100%}"
              "table.pila tr{border-bottom:1px solid var(--line);padding:8px 0}table.pila tr:last-child{border-bottom:0}"
              ".tab.compatta table.pila td,.tab.compatta table.pila th{border:0;padding:3px 14px;min-width:0;text-align:left;white-space:normal;background:none}"
              "table.pila tbody th{font-weight:700;padding-top:6px}"
              "table.pila td[data-l]::before{content:attr(data-l);display:block;font-weight:700;color:var(--ink-3);font-size:.72rem;text-transform:uppercase;letter-spacing:.06em}}")


def pila(tab):
    """Tabella che sotto i 640 px diventa una pila di schede: classe "pila" e data-l (intestazione della colonna) su ogni cella."""
    teste = [re.sub(r"<[^>]+>", "", h).strip() for h in re.findall(r"<th[^>]*>(.*?)</th>", re.search(r"<thead>(.*?)</thead>", tab, re.S).group(1), re.S)]
    def riga(m):
        i = [0]
        def cella(c):
            n = i[0]
            i[0] += 1
            return f'<{c.group(1)} data-l="{escape(teste[n]) if n < len(teste) else ""}"'
        return re.sub(r"<(td|th)(?= |>)", cella, m.group(0))
    corpo = re.sub(r"<tr>.*?</tr>", riga, re.search(r"<tbody>.*?</tbody>", tab, re.S).group(0), flags=re.S)
    tab = re.sub(r"<tbody>.*?</tbody>", lambda _: corpo, tab, count=1, flags=re.S)
    return re.sub(r"<table ", '<table class="pila" ', tab, count=1)


def calc_box(tipo, k, campi, titolo, nota=""):
    """Calcolatore (riquadro .calc): campi = HTML dei campi del modulo; il risultato lo scrive STUDIO_JS."""
    return (f'<section class="card calc" data-studio="{tipo}" data-k=\'{json.dumps(k, separators=(",", ":"))}\' aria-label="{escape(titolo)}">'
            f'<div class="calc-grid"><form autocomplete="off"><h2 style="margin:0 0 14px;font-size:1.2rem">{ico("calc")} {escape(titolo)}</h2><div class="campi">{campi}</div>'
            f'{f"<p class=\"small\" style=\"margin:12px 0 0\">{nota}</p>" if nota else ""}</form>'
            f'<div class="calc-out"><div class="risultato" data-out aria-live="polite"><noscript>Turn on JavaScript to use the calculator; the rules are in the tables below.</noscript></div></div></div></section>')


def campo_data(nome, etichetta, icona="calendar", pieno=True, valore=""):
    return (f'<label{" class=\"pieno\"" if pieno else ""}><span class="lt">{ico(icona)}{etichetta}</span>'
            f'<input type="date" name="{nome}" value="{valore}" min="2020-01-01" max="2035-12-31"></label>')


def calc_finestra():
    return calc_box("finestra", K_FINESTRA,
                    campo_data("fine", "Program end date (on your Form I-20)") + campo_data("dso", "DSO recommendation date in SEVIS (optional)", "check"),
                    "OPT filing window calculator", "Post-completion OPT. The calculator uses the rules USCIS applies today; it runs in your browser and sends nothing.")


def calc_disoccupazione():
    campi = (campo_data("inizio", "OPT start date (on your EAD card)") +
             f'<label><span class="lt">{ico("list")}Type of OPT</span><select name="tipo"><option value="opt">Post-completion OPT ({K_DISOCC["opt"]} days)</option>'
             f'<option value="stem">With STEM extension ({K_DISOCC["stem"]} days)</option></select></label>'
             f'<label><span class="lt">{ico("calc")}Days already used (optional)</span><input type="number" name="usati" min="0" max="150" inputmode="numeric" placeholder="e.g. 20"></label>')
    return calc_box("disoccupazione", K_DISOCC, campi, "OPT unemployment days calculator",
                    "Days already used: the unemployment counter in your SEVP Portal or your DSO can tell you. Runs in your browser.")


def calc_stem():
    return calc_box("stem", K_STEM, campo_data("scad", "End date of your current OPT EAD") + campo_data("dso", "DSO recommendation date for the extension (optional)", "check"),
                    "STEM OPT extension filing window", "Runs in your browser and sends nothing.")


def calc_graduate(tipo="altro"):
    opz = "".join(f'<option value="{v}"{" selected" if v == tipo else ""}>{t}</option>' for v, t in
                  (("altro", "Bachelor's or master's degree (or other eligible course)"), ("phd", "PhD or other doctoral qualification")))
    campi = (campo_data("dom", "Date you apply") +
             f'<label class="pieno"><span class="lt">{ico("passport")}Qualification</span><select name="tipo">{opz}</select></label>' +
             campo_data("dec", "Decision date, if you know it (optional)", "check", pieno=False) +
             campo_data("scad", "Student visa expiry (optional)", "alert", pieno=False) +
             f'<label><span class="lt">{ico("user")}Adults incl. you</span><input type="number" name="adulti" min="1" max="10" value="1" inputmode="numeric"></label>'
             f'<label><span class="lt">{ico("child")}Children under 18</span><input type="number" name="figli" min="0" max="10" value="0" inputmode="numeric"></label>')
    return calc_box("graduate", K_GRAD, campi, "Graduate visa length, end date and cost",
                    "Partner and children count only if they are your dependants. Runs in your browser and sends nothing.")


# ---------- testi comuni OPT
def tabella_costi_opt():
    p = FR_OPT["tasse_opt"]
    righe = [
        ("Form I-765, filed online (OPT, STEM OPT)", usd(vo("tassa_online")), '<span class="stato vigore">In force</span>', link_fonte_opt("g1055_i765")),
        ("Form I-765, filed on paper", usd(vo("tassa_carta")), '<span class="stato vigore">In force</span>', link_fonte_opt("g1055_i765")),
        (f"Premium processing (Form I-907): decision within {vo('premium_giorni')} business days", usd(vo("premium")),
         f'<span class="stato vigore">In force</span> <span class="small">since {data_lunga(vo("premium_dal"))}; it was {usd(vo("premium_prima"))}</span>',
         link_fonte_opt("g1055_i907") + "; " + link_fr("premium", breve=True)),
        ("Extra fee of Public Law 119-21 (H.R. 1) on some work permits", "Not listed for OPT",
         '<span class="small">The fee schedule lists it for categories such as parolees, TPS and asylum applicants, not for the OPT categories (c)(3)</span>',
         link_fonte_opt("g1055_i765")),
        ("Proposed OPT fee, paid by the school", f'{usd(vo("proposta_importi")["iniziale"])} first OPT · {usd(vo("proposta_importi")["successiva"])} later OPT',
         f'<span class="stato proposta">Proposal</span> <span class="small">not in force; comments until {data_lunga(p["comments_close_on"])}</span>',
         link_fr("tasse_opt", breve=True)),
    ]
    corpo = "".join(f'<tr><th scope="row">{a}</th><td class="n">{b}</td><td>{c}</td><td class="small">{d}</td></tr>' for a, b, c, d in righe)
    return pila(f'<div class="tab compatta"><table id="t-costi-opt"><caption class="sr">OPT and STEM OPT costs</caption><thead><tr><th scope="col">What</th><th scope="col" class="n">Amount</th>'
            f'<th scope="col">Status</th><th scope="col">Official source</th></tr></thead><tbody>{corpo}</tbody></table></div>')


def tabella_finestre_opt():
    f, s = vo("finestra"), vo("finestra_stem")
    righe = [
        ("Pre-completion OPT", f"Up to {f['prima']} days before you complete one full academic year, after the DSO recommendation", "You cannot start work before the full academic year"),
        ("Post-completion OPT", f"From {f['prima']} days before to {f['dopo']} days after your program end date",
         f"Within {f['dso']} days of the DSO recommendation in SEVIS; start date no later than {vo('inizio_max')} days after the program end date"),
        ("24-month STEM OPT extension", f"Up to {s['prima']} days before your current OPT EAD expires", f"Within {s['dso']} days of the DSO recommendation"),
    ]
    corpo = "".join(f'<tr><th scope="row">{a}</th><td>{b}</td><td>{c}</td></tr>' for a, b, c in righe)
    return (pila(f'<div class="tab compatta"><table id="t-finestre-opt"><caption class="sr">When to file Form I-765 for OPT</caption><thead><tr><th scope="col">Type</th>'
            f'<th scope="col">When to file Form I-765</th><th scope="col">Also</th></tr></thead><tbody>{corpo}</tbody></table></div>')
            + fonte_opt_p(("i765", "opt", "stem", "sevp_opt", "ice")))


def tabella_stato_opt(rel):
    p, ds, pr, h = FR_OPT["tasse_opt"], FR_OPT["durata_fissa"], FR_OPT["premium"], FR_OPT["hr1_2027"]
    righe = [
        (f'OPT fees of {usd(vo("proposta_importi")["iniziale"])} and {usd(vo("proposta_importi")["successiva"])}', '<span class="stato proposta">Proposal</span>',
         f'Proposed on {data_lunga(p["publication_date"])}; comments close on {data_lunga(p["comments_close_on"])}. Not in force. <a href="{rel}{SEZ_OPT}opt-fee-proposal/">Details</a>', link_fr("tasse_opt", True)),
        (f'Filing deadline and grace period cut from 60 to {vo("regola_30")} days', '<span class="stato sospesa">Final rule on hold</span>',
         f'Published on {data_lunga(ds["publication_date"])}, due to take effect on {data_lunga(ds["effective_on"])}; a federal court postponed it on {data_lunga(vo("rinvio_regola"))} and USCIS applies the previous rules. '
         f'<a href="{rel}{SEZ_OPT}opt-grace-period/">Details</a>', link_fr("durata_fissa", True)),
        (f'Premium processing fee {usd(vo("premium"))}', '<span class="stato vigore">In force</span>', f'Since {data_lunga(pr["effective_on"])} (inflation adjustment).', link_fr("premium", True)),
        ('H.R. 1 fees, fiscal year 2027', '<span class="stato vigore">In force</span>',
         f'Adjusted from {data_lunga(h["effective_on"])}; they apply to other categories (for example parolees, TPS and asylum applicants), not to OPT.', link_fr("hr1_2027", True)),
    ]
    corpo = "".join(f'<tr><th scope="row">{a}</th><td>{b}</td><td>{c}</td><td class="small">{d}</td></tr>' for a, b, c, d in righe)
    return (pila(f'<div class="tab compatta"><table id="t-stato-opt"><caption class="sr">OPT rule changes and their status</caption><thead><tr><th scope="col">Change</th><th scope="col">Status</th>'
            f'<th scope="col">What it means today</th><th scope="col">Federal Register</th></tr></thead><tbody>{corpo}</tbody></table></div>')
            + fonte_opt_p(("i765", "g1055_i765"), ("tasse_opt", "durata_fissa", "premium", "hr1_2027")))


def link_opt(rel, escludi=""):
    voci = [("", "US OPT and STEM OPT: fees and deadlines"), ("opt-application-deadline-calculator/", "OPT application deadline calculator"),
            ("opt-unemployment-days/", "OPT unemployment days (90 / 150)"), ("stem-opt-extension-fee/", "STEM OPT extension fee and window"),
            ("opt-fee-proposal/", "The $70,000 OPT fee proposal"), ("opt-grace-period/", "OPT grace period: 60 or 30 days")]
    return ('<div class="griglia">' + "".join(f'<a href="{rel}{SEZ_OPT}{p}"><span class="ic">{ico("calendar" if "calc" in p or "days" in p else "coins" if "fee" in p else "passport")}</span><span>{t}</span></a>'
                                              for p, t in voci if p != escludi) + "</div>")


def esempi_finestra():
    """Tre esempi calcolati qui (Python), uguali al calcolatore."""
    righe = ""
    for fine in ("2026-12-18", "2027-05-15", "2027-08-31"):
        e = date.fromisoformat(fine)
        a, c, c30 = e - timedelta(days=K_FINESTRA["prima"]), e + timedelta(days=K_FINESTRA["dopo"]), e + timedelta(days=K_FINESTRA["nuova"])
        righe += (f'<tr><td>{data_lunga(fine)}</td><td>{data_lunga(a.isoformat())}</td><td>{data_lunga(c.isoformat())}</td>'
                  f'<td class="small">{data_lunga(c30.isoformat())}</td></tr>')
    return pila(f'<div class="tab compatta"><table id="t-esempi-opt"><caption class="sr">Examples of OPT filing windows</caption><thead><tr><th scope="col">Program end date</th>'
            f'<th scope="col">Earliest filing</th><th scope="col">Last filing (rule applied today)</th><th scope="col">Last filing if the 30-day rule takes effect</th></tr></thead>'
            f'<tbody>{righe}</tbody></table></div>')


# ---------- pagine OPT
def pagina_opt_indice():
    rel = "../"
    percorso = SEZ_OPT
    f, s = vo("finestra"), vo("finestra_stem")
    domande = [
        ("How much does OPT cost in 2026?",
         f"The Form I-765 filing fee is {usd(vo('tassa_online'))} if you file online and {usd(vo('tassa_carta'))} on paper (USCIS fee schedule, edition read on {data_lunga(LETTO_OPT)}). "
         f"Premium processing costs {usd(vo('premium'))} more and gets a decision within {vo('premium_giorni')} business days."),
        ("When can I apply for OPT?",
         f"For post-completion OPT, USCIS must receive Form I-765 from {f['prima']} days before to {f['dopo']} days after your program end date, and within {f['dso']} days of your DSO's recommendation in SEVIS."),
        ("How long is OPT?", f"Up to {vo('mesi_opt')} months at each education level; with a STEM degree you can apply for a {vo('mesi_stem')}-month extension."),
        ("How many days can I be unemployed on OPT?",
         f"{K_DISOCC['opt']} days in total on post-completion OPT, and {K_DISOCC['stem']} days in total if you also get the STEM extension (the {K_DISOCC['stem']} include the days used before)."),
        ("Is the $70,000 OPT fee in force?",
         f"No. It is a proposed rule published on {data_lunga(FR_OPT['tasse_opt']['publication_date'])}; comments close on {data_lunga(FR_OPT['tasse_opt']['comments_close_on'])}. "
         "As proposed, the school would pay it, not the student. A final rule would have to be published before it applies."),
        ("Has the OPT deadline changed to 30 days?",
         f"Not for now. A final rule of {data_lunga(FR_OPT['durata_fissa']['publication_date'])} would cut the 60 days to 30, but a federal court postponed it on {data_lunga(vo('rinvio_regola'))} "
         "and USCIS says it is applying the previous rules. Check with your DSO before relying on the 60 days."),
    ]
    corpo = f"""<section class="hero">{h1_diviso(f"US OPT and STEM OPT: fees, filing deadlines and unemployment days ({ANNO})")}
<p class="lead">Form I-765 for OPT or a STEM OPT extension costs <strong>{usd(vo("tassa_online"))} online or {usd(vo("tassa_carta"))} on paper</strong>, and for post-completion OPT you can file it from {f["prima"]} days before to {f["dopo"]} days after your program end date, according to the USCIS fee schedule and Form I-765 page read on {data_lunga(LETTO_OPT)}. OPT lasts up to {vo("mesi_opt")} months per education level, plus {vo("mesi_stem")} months with the STEM extension, with at most {K_DISOCC["opt"]} days of unemployment ({K_DISOCC["stem"]} with STEM).</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("passport")}<span>US OPT and STEM OPT</span><span>read on {data_lunga(LETTO_OPT)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Form I-765 filing fee (OPT and STEM OPT)</span><span class="sr">: </span><strong>{usd(vo("tassa_online"))} online · {usd(vo("tassa_carta"))} paper</strong></p>
<div class="kpi"><div><b>{usd(vo("premium"))}</b><span>premium processing, decision within {vo("premium_giorni")} business days</span></div><div><b>{f["prima"]} / {f["dopo"]} days</b><span>before / after the program end date</span></div><div><b>{vo("mesi_opt")} + {vo("mesi_stem")} months</b><span>OPT + STEM extension</span></div><div><b>{K_DISOCC["opt"]} / {K_DISOCC["stem"]} days</b><span>unemployment limit (OPT / with STEM)</span></div></div>
{fonte_opt_p(("g1055_i765", "g1055_i907", "i765", "sevp_disoccupazione"))}
</div></section>
{AVVISO_OPT}
{AD}
{calc_finestra()}
{calc_disoccupazione()}
<h2 id="fees">OPT and STEM OPT fees in {ANNO}</h2>
<p>OPT and the STEM extension use the same form and the same fee. The fee schedule lists online filing at {usd(vo("tassa_online"))} and paper filing at {usd(vo("tassa_carta"))}; USCIS accepts Form I-765 online for post-completion OPT and for the STEM extension.</p>
{tabella_costi_opt()}
{fonte_opt_p(("g1055_i765", "g1055_i907", "premium", "online"), ("premium",))}
<h2 id="deadlines">When to file</h2>
{tabella_finestre_opt()}
<p>You cannot start working until USCIS approves Form I-765 and you have the Employment Authorization Document (EAD). If you file the STEM extension on time and your OPT EAD expires while it is pending, your work authorization is extended automatically for up to {vo("proroga_stem")} days.</p>
<h2 id="unemployment">Unemployment days</h2>
<p>On post-completion OPT you can be unemployed for <strong>{K_DISOCC["opt"]} days</strong> in total. With the STEM extension the total is <strong>{K_DISOCC["stem"]} days</strong>, which includes the days used during post-completion OPT. SEVIS counts from the actual OPT start date and adds each day without employer information in your record. <a href="opt-unemployment-days/">How the days are counted</a>.</p>
{fonte_opt_p(("sevp_disoccupazione", "stem"))}
<h2 id="changes">Proposed or on hold: what is not the rule today</h2>
<p>Several changes to OPT were published in {ANNO}. Only some are in force:</p>
{tabella_stato_opt(rel)}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>OPT pages on this site</h2>
{link_opt(rel, "")}
<p><a href="{rel}{SEZ_GRAD}">Studying in the UK instead? UK Graduate visa: 2 years or 18 months</a> · <a href="{rel}{SEZ}united-states/">Schengen visa refusal rates for applications made in the United States</a></p>"""
    titolo = f"US OPT and STEM OPT {ANNO}: fees, deadlines and calculator"
    descr = (f"OPT costs {usd(vo('tassa_online'))} online or {usd(vo('tassa_carta'))} on paper (Form I-765); file from {f['prima']} days before to {f['dopo']} days after your program end date. "
             f"Calculator for the filing window and the {K_DISOCC['opt']}/{K_DISOCC['stem']} unemployment days, and the status of the $70,000 fee proposal.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande)], briciole=[("US OPT and STEM OPT", percorso)], script=STUDIO_JS)


def pagina_opt_scadenza():
    rel = "../../"
    percorso = f"{SEZ_OPT}opt-application-deadline-calculator/"
    f = vo("finestra")
    domande = [
        ("What is the OPT application deadline?",
         f"USCIS must receive Form I-765 for post-completion OPT no later than {f['dopo']} days after your program end date and within {f['dso']} days of the date your DSO enters the recommendation in SEVIS, whichever comes first."),
        ("How early can I apply for OPT?", f"Up to {f['prima']} days before your program end date, once your DSO has recommended OPT in SEVIS."),
        ("Does the 30-day DSO rule matter if I am still within 60 days?",
         f"Yes. Both limits apply: if your DSO recommended OPT on 1 June and your program ended on 15 May, the {f['dso']}-day limit ends on 1 July, before the {f['dopo']}-day limit."),
        ("What start date can I ask for?", f"A date on or after your program end date and no more than {vo('inizio_max')} days after it (SEVP)."),
        ("Is the deadline now 30 days after the program end date?",
         f"A final rule of {data_lunga(FR_OPT['durata_fissa']['publication_date'])} would make it {vo('regola_30')} days, but its effective date was postponed by a federal court on {data_lunga(vo('rinvio_regola'))}; USCIS says it applies the previous rules ({f['dopo']} days). The calculator shows both dates."),
    ]
    corpo = f"""<section class="hero"><h1>OPT application deadline calculator ({ANNO})</h1>
<p class="lead">For post-completion OPT you can file Form I-765 from <strong>{f["prima"]} days before to {f["dopo"]} days after your program end date</strong>, and within {f["dso"]} days of your DSO's recommendation in SEVIS (USCIS, Form I-765 page, read on {data_lunga(LETTO_OPT)}). Enter your dates to see your window.</p></section>
{calc_finestra()}
{AVVISO_OPT}
{AD}
<h2>The three dates that decide your window</h2>
<ul class="testo"><li><strong>Program end date</strong> (on your Form I-20): the window opens {f["prima"]} days before it and closes {f["dopo"]} days after it.</li>
<li><strong>DSO recommendation date</strong>: USCIS must receive your application within {f["dso"]} days of the day your DSO enters the recommendation in SEVIS. If that comes first, it is your real deadline.</li>
<li><strong>Requested start date</strong>: on or after the program end date and no more than {vo("inizio_max")} days after it.</li></ul>
{fonte_opt_p(("i765", "opt", "sevp_opt"))}
<h2>Examples</h2>
<p>Without a DSO date. The last column shows the date under the postponed rule of {data_lunga(FR_OPT["durata_fissa"]["publication_date"])}, which is not applied today.</p>
{esempi_finestra()}
{fonte_opt_p(("i765",), ("durata_fissa",))}
<h2>Fees</h2>
<p>Form I-765 costs {usd(vo("tassa_online"))} online or {usd(vo("tassa_carta"))} on paper; premium processing costs {usd(vo("premium"))} more and gets a decision within {vo("premium_giorni")} business days. You cannot start working before you receive the EAD.</p>
{fonte_opt_p(("g1055_i765", "g1055_i907", "premium"))}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>More on OPT</h2>
{link_opt(rel, "opt-application-deadline-calculator/")}"""
    titolo = f"OPT application deadline calculator: {f['prima']} days before, {f['dopo']} after"
    descr = (f"Find your OPT filing window: Form I-765 from {f['prima']} days before to {f['dopo']} days after your program end date, within {f['dso']} days of the DSO "
             f"recommendation (USCIS, read {data_lunga(LETTO_OPT)}). Shows the postponed 30-day rule too.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande)],
           briciole=[("US OPT and STEM OPT", SEZ_OPT), ("OPT application deadline calculator", percorso)], script=STUDIO_JS)


def pagina_opt_disoccupazione():
    rel = "../../"
    percorso = f"{SEZ_OPT}opt-unemployment-days/"
    o, s = K_DISOCC["opt"], K_DISOCC["stem"]
    agg = data_us(FO["sevp_disoccupazione"]["aggiornata"])
    domande = [
        ("How many unemployment days are allowed on OPT?", f"{o} days in total during post-completion OPT, and {s} days in total if you get the 24-month STEM extension."),
        ("Do the 150 STEM days start from zero?", f"No. The {s} days include the days you used during post-completion OPT: if you used 40, you have {s - 40} left for the STEM extension."),
        ("When does the unemployment clock start?", "SEVIS looks back to the actual OPT start date and counts each day without employer information in your record."),
        ("Do weekends count as unemployment days?", "SEVP's help page says SEVIS counts each day without employer information; it does not exclude weekends. Ask your DSO how your days were counted."),
        ("What happens after the limit?", f"SEVP's SEVIS Help Hub lists “Exceeded Unemployment Time” among the reasons a DHS official can terminate a student's SEVIS record: more than {o} days of unemployment on post-completion OPT, or more than {s} with the STEM extension. Talk to your DSO before you reach the limit."),
    ]
    corpo = f"""<section class="hero"><h1>OPT unemployment days: {o} days, or {s} with STEM ({ANNO})</h1>
<p class="lead">On post-completion OPT you can be unemployed for <strong>{o} days in total</strong>, and for <strong>{s} days in total</strong> if you also get the 24-month STEM extension, according to SEVP's SEVIS Help Hub (page updated {data_lunga(agg)}, read on {data_lunga(LETTO_OPT)}). The calculator shows when you would reach the limit.</p></section>
{calc_disoccupazione()}
{AVVISO_OPT}
{AD}
<h2>How SEVIS counts the days</h2>
<ul class="testo"><li>It looks back to the <strong>actual OPT start date</strong> of that period of OPT.</li>
<li>It counts <strong>each day without employer information</strong> in your SEVIS record. A record without employer information counts as unemployed, so report a new job to your DSO quickly (within 10 days).</li>
<li>The {s} days of the STEM extension <strong>include</strong> the days used during post-completion OPT (USCIS: "an additional 60 days").</li></ul>
{fonte_opt_p(("sevp_disoccupazione", "sevp_opt", "stem"))}
<h2>Examples</h2>
<div class="tab compatta"><table id="t-esempi-disocc"><caption class="sr">Examples of unemployment limits</caption><thead><tr><th scope="col">OPT start date</th><th scope="col">Limit</th><th scope="col">Day {o} (no job from the start)</th></tr></thead><tbody>
{"".join(f'<tr><td>{data_lunga(d)}</td><td>{o} days</td><td>{data_lunga((date.fromisoformat(d) + timedelta(days=o - 1)).isoformat())}</td></tr>' for d in ("2026-06-01", "2026-12-15", "2027-07-01"))}
</tbody></table></div>
<p class="small">If you have a job for part of the time, only the days without employer information count: use the "days already used" field with the number from your SEVP Portal.</p>
<h2>After OPT ends</h2>
<p>When your OPT ends, the F-1 grace period to leave or change status is 60 days under the rules USCIS applies today; a final rule that would cut it to 30 days is on hold. <a href="../opt-grace-period/">OPT grace period: 60 or 30 days</a>.</p>
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>More on OPT</h2>
{link_opt(rel, "opt-unemployment-days/")}"""
    titolo = f"OPT unemployment days: {o} days, {s} with STEM (calculator)"
    descr = (f"OPT allows {o} days of unemployment in total, {s} with the STEM extension (SEVP, read {data_lunga(LETTO_OPT)}). "
             "Calculator: when you reach the limit, how SEVIS counts the days, and examples.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande)],
           briciole=[("US OPT and STEM OPT", SEZ_OPT), ("OPT unemployment days", percorso)], script=STUDIO_JS)


def pagina_opt_stem():
    rel = "../../"
    percorso = f"{SEZ_OPT}stem-opt-extension-fee/"
    s = vo("finestra_stem")
    domande = [
        ("How much is the STEM OPT extension fee?",
         f"{usd(vo('tassa_online'))} online or {usd(vo('tassa_carta'))} on paper (Form I-765, the same fee as OPT). Premium processing costs {usd(vo('premium'))} more."),
        ("When should I apply for the STEM OPT extension?",
         f"Up to {s['prima']} days before your current OPT EAD expires, and within {s['dso']} days of your DSO's recommendation in SEVIS."),
        ("Can I keep working while the STEM extension is pending?",
         f"Yes, if you filed on time and your OPT EAD expires while the application is pending: your work authorization is extended automatically for up to {vo('proroga_stem')} days."),
        ("Is there a $30,000 STEM OPT fee?",
         f"Not today. DHS proposed on {data_lunga(FR_OPT['tasse_opt']['publication_date'])} a fee of {usd(vo('proposta_importi')['successiva'])} for any OPT after the first, STEM extension included, paid by the school. It is a proposal, not a rule."),
        ("How many unemployment days do I have on STEM OPT?", f"{K_DISOCC['stem']} in total, including the days used during post-completion OPT."),
    ]
    corpo = f"""<section class="hero"><h1>STEM OPT extension fee {ANNO}: {usd(vo("tassa_online"))} online, {usd(vo("tassa_carta"))} by mail</h1>
<p class="lead">The 24-month STEM OPT extension is filed on Form I-765 with the same fee as OPT: <strong>{usd(vo("tassa_online"))} online or {usd(vo("tassa_carta"))} on paper</strong>, plus {usd(vo("premium"))} if you want premium processing, according to the USCIS fee schedule (Form G-1055) read on {data_lunga(LETTO_OPT)}. You can file up to {s["prima"]} days before your current OPT EAD expires.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("coins")}<span>STEM OPT extension</span><span>read on {data_lunga(LETTO_OPT)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Form I-765 fee for the STEM extension</span><span class="sr">: </span><strong>{usd(vo("tassa_online"))} online · {usd(vo("tassa_carta"))} paper</strong></p>
<div class="kpi"><div><b>{usd(vo("premium"))}</b><span>premium processing (optional)</span></div><div><b>{vo("mesi_stem")} months</b><span>length of the extension</span></div><div><b>{s["prima"]} days</b><span>before your OPT EAD expires: window opens</span></div><div><b>{vo("proroga_stem")} days</b><span>automatic extension while pending</span></div></div>
{fonte_opt_p(("g1055_i765", "g1055_i907", "stem"))}
</div></section>
{AVVISO_OPT}
{AD}
{calc_stem()}
<h2>What you file</h2>
<ul class="testo"><li>Form I-765 with the fee, your employer's name as listed in E-Verify and its E-Verify company identification number.</li>
<li>A Form I-20 endorsed by your DSO within the last 60 days, after your DSO has reviewed the Form I-983 training plan.</li>
<li>A copy of your STEM degree (on the DHS STEM Designated Degree Program List).</li></ul>
{fonte_opt_p(("stem", "ice"))}
<h2>Fees</h2>
{tabella_costi_opt()}
<p class="small">The proposed fee would be paid by the school before the DSO recommends OPT, for recommendations dated on or after the effective date of a final rule; it is not in force. <a href="../opt-fee-proposal/">What the proposal says</a>.</p>
{fonte_opt_p(("g1055_i765", "g1055_i907"), ("tasse_opt",))}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>More on OPT</h2>
{link_opt(rel, "stem-opt-extension-fee/")}"""
    titolo = f"STEM OPT extension fee {ANNO}: {usd(vo('tassa_online'))} online, {usd(vo('tassa_carta'))} by mail"
    descr = (f"STEM OPT extension: Form I-765 fee {usd(vo('tassa_online'))} online or {usd(vo('tassa_carta'))} on paper, premium processing {usd(vo('premium'))} (USCIS, read {data_lunga(LETTO_OPT)}). "
             f"Filing window calculator, {vo('proroga_stem')}-day extension, and the proposed school fee.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande)],
           briciole=[("US OPT and STEM OPT", SEZ_OPT), ("STEM OPT extension fee", percorso)], script=STUDIO_JS)


def pagina_opt_proposta():
    rel = "../../"
    percorso = f"{SEZ_OPT}opt-fee-proposal/"
    p = FR_OPT["tasse_opt"]
    i, s = vo("proposta_importi")["iniziale"], vo("proposta_importi")["successiva"]
    domande = [
        ("Is the $70,000 OPT fee in force?", f"No. It is a notice of proposed rulemaking published on {data_lunga(p['publication_date'])}. It would apply only after DHS publishes a final rule."),
        ("Who would pay the OPT fee?", f"As proposed, the SEVP-certified school, for each F-1 student, before the DSO recommends OPT in SEVIS. It is separate from the {usd(vo('tassa_online'))}/{usd(vo('tassa_carta'))} Form I-765 fee."),
        ("Would it apply to the STEM OPT extension?", f"Yes, as proposed: {usd(s)} for any OPT after the first, STEM extension included."),
        ("When would it start?", f"DHS proposes that the final rule take effect {vo('proposta_60_giorni')} days after it is published; the fee would apply to DSO recommendations dated on or after that day."),
        ("Can I comment?", f"Yes, until {data_lunga(p['comments_close_on'])}, on regulations.gov, docket {vo('proposta_docket')}."),
    ]
    corpo = f"""<section class="hero"><h1>OPT ${i:,} fee proposal: what DHS proposed and where it stands</h1>
<p class="lead">On {data_lunga(p["publication_date"])} DHS proposed a fee of <strong>{usd(i)} for a student's first OPT and {usd(s)} for any later OPT</strong>, paid by the school; it is a proposal, not a rule, and comments close on {data_lunga(p["comments_close_on"])} (Federal Register, {escape(p["citation"])}, read on {data_lunga(LETTO_OPT)}). Today OPT still costs the Form I-765 fee of {usd(vo("tassa_online"))} online or {usd(vo("tassa_carta"))} on paper.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("alert")}<span>Proposed rule, not in force</span><span>read on {data_lunga(LETTO_OPT)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Proposed OPT fee per student, paid by the school</span><span class="sr">: </span><strong>{usd(i)} first OPT · {usd(s)} later OPT</strong></p>
<div class="kpi"><div><b>Proposal</b><span>status on {data_lunga(LETTO_OPT)}</span></div><div><b>{data_lunga(p["comments_close_on"])}</b><span>comments close</span></div><div><b>{vo("proposta_60_giorni")} days</b><span>after a final rule: proposed start</span></div><div><b>{usd(vo("tassa_online"))}</b><span>what you pay today (I-765 online)</span></div></div>
<p class="fonte">Source: {link_fr("tasse_opt")}, summary and proposed 8 CFR 214.13(i); docket {escape(vo("proposta_docket"))}. Read on {data_lunga(LETTO_OPT)}.</p>
</div></section>
{AVVISO_OPT}
{AD}
<h2>What the proposal says</h2>
<ul class="testo"><li>A <strong>{usd(i)}</strong> fee "for initial OPT" and <strong>{usd(s)}</strong> "for any subsequent OPT", for each F-1 student.</li>
<li>The school (the SEVP-certified institution) would pay it before the DSO recommends OPT in SEVIS; USCIS would not grant the work permit before the fee is paid.</li>
<li>The {usd(s)} fee would apply to any OPT after the first one, "regardless of whether it is another pre-completion OPT, postcompletion OPT, or STEM OPT extension".</li>
<li>DHS proposes that the final rule take effect {vo("proposta_60_giorni")} days after publication, for DSO recommendations dated on or after that day.</li></ul>
{fonte_opt_p((), ("tasse_opt",))}
<h2>What it does not change today</h2>
<p>Nothing changes until a final rule is published. Form I-765 still costs {usd(vo("tassa_online"))} online or {usd(vo("tassa_carta"))} on paper, the filing window is unchanged, and the proposal may change after the comments. The Federal Register will publish any final rule; we will update this page when it does.</p>
{tabella_stato_opt(rel)}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>More on OPT</h2>
{link_opt(rel, "opt-fee-proposal/")}"""
    titolo = f"OPT ${i:,} fee proposal: what DHS proposed and its status"
    descr = (f"DHS proposed on {data_lunga(p['publication_date'])} a {usd(i)} fee for first OPT and {usd(s)} for later OPT, paid by schools. Not in force; comments until "
             f"{data_lunga(p['comments_close_on'])} ({p['citation']}). What it would change and what you pay today.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande)],
           briciole=[("US OPT and STEM OPT", SEZ_OPT), ("OPT fee proposal", percorso)], script=STUDIO_JS)


def pagina_opt_grazia():
    rel = "../../"
    percorso = f"{SEZ_OPT}opt-grace-period/"
    ds = FR_OPT["durata_fissa"]
    ec = OPT["ecfr"]
    domande = [
        ("What is the OPT grace period in 2026?",
         f"60 days under the rules USCIS applies today. A final rule of {data_lunga(ds['publication_date'])} would cut it to {vo('regola_grazia_30')} days, but a federal court postponed it on {data_lunga(vo('rinvio_regola'))}."),
        ("Is the OPT application deadline 60 or 30 days after graduation?",
         f"USCIS's Form I-765 page still says no later than 60 days after your program end date and says USCIS will proceed under the previous regulatory provisions while the court order stands."),
        ("Why does the online Code of Federal Regulations say 30 days?",
         f"The eCFR shows the text as amended by the rule from {data_lunga('2026-09-15')}. The court order postponed the rule's effective date; USCIS says it is applying the previous rules. Ask your DSO which dates SEVIS uses for you."),
        ("Can the 30-day rule come back?", "Yes. USCIS writes that DHS disagrees with the order and will implement the rule if the order is lifted. Check this page and your DSO."),
    ]
    corpo = f"""<section class="hero"><h1>OPT grace period {ANNO}: 60 days, and the 30-day rule on hold</h1>
<p class="lead">After you finish your program or your OPT, the F-1 grace period is still <strong>60 days</strong> under the rules USCIS applies today: a final rule published on {data_lunga(ds["publication_date"])} would cut it to {vo("regola_grazia_30")} days, but a federal court postponed it on {data_lunga(vo("rinvio_regola"))} and USCIS says it is applying the previous rules (USCIS, Form I-765 page, read on {data_lunga(LETTO_OPT)}).</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("calendar")}<span>F-1 grace period and OPT deadline</span><span>read on {data_lunga(LETTO_OPT)}</span></div>
<div class="s-body">
<div class="kpi"><div><b>60 days</b><span>grace period, rules applied today</span></div><div><b>{vo("finestra")["dopo"]} days</b><span>after the program end date: OPT filing deadline today</span></div><div><b>{vo("regola_30")} days</b><span>under the rule on hold</span></div><div><b>{data_lunga(vo("rinvio_regola"))}</b><span>court order postponing the rule</span></div></div>
{fonte_opt_p(("i765",), ("durata_fissa",))}
</div></section>
{AVVISO_OPT}
{AD}
<h2>What the July {ANNO} rule would change</h2>
<ul class="testo"><li>F-1 students would be admitted for a fixed period (up to 4 years) instead of "duration of status".</li>
<li>The grace period after a program or OPT would be {vo("regola_grazia_30")} days instead of 60.</li>
<li>The last day to file for post-completion OPT, and the latest start date you can request, would move from 60 to {vo("regola_30")} days after the program end date.</li></ul>
{fonte_opt_p((), ("durata_fissa",))}
<h2>Where it stands</h2>
<p>The rule was due to take effect on {data_lunga(ds["effective_on"])}. On {data_lunga(vo("rinvio_regola"))} the U.S. District Court for the District of Massachusetts postponed its effective date; USCIS writes: "Until such time, USCIS will proceed under the previous regulatory provisions." The online Code of Federal Regulations (eCFR) already shows the amended text ({ec["giorni_dopo_fine_programma"]} days, version of {data_lunga(ec["ultima_versione"])}); the previous text, with 60 days, is the <a href="{escape(ec["precedente"]["url"])}" rel="noopener">version of {data_lunga(ec["precedente"]["data"])}</a>.</p>
<p class="fonte">Sources: {link_fonte_opt("i765")}; <a href="{escape(ec["pagina"])}" rel="noopener">eCFR, 8 CFR 214.2</a> (versions of {data_lunga(ec["ultima_versione"])} and {data_lunga(ec["precedente"]["data"])}). Read on {data_lunga(LETTO_OPT)}.</p>
<h2>Your OPT filing window under both rules</h2>
{calc_finestra()}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>More on OPT</h2>
{link_opt(rel, "opt-grace-period/")}"""
    titolo = f"OPT grace period {ANNO}: 60 days, and the 30-day rule on hold"
    descr = (f"The F-1 grace period after OPT is still 60 days: the {data_lunga(ds['publication_date'])} rule cutting it to 30 days was postponed by a court on "
             f"{data_lunga(vo('rinvio_regola'))} (USCIS, read {data_lunga(LETTO_OPT)}). What would change and your filing window.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande)],
           briciole=[("US OPT and STEM OPT", SEZ_OPT), ("OPT grace period", percorso)], script=STUDIO_JS)


# ---------- UK Graduate visa
def ihs(mesi, rate):
    return rate * mesi / 12


def tabella_costi_grad():
    righe = ""
    for mesi, nome in ((24, "2 years (apply on or before 31 December 2026)"), (18, "18 months (apply on or after 1 January 2027)"), (36, "3 years (PhD)")):
        a = ihs(mesi, K_GRAD["ihs_a"])
        c = ihs(mesi, K_GRAD["ihs_m"])
        righe += (f'<tr><th scope="row">{nome}</th><td class="n">{gbp(K_GRAD["tassa"])}</td><td class="n">{gbp(a)}</td><td class="n"><strong>{gbp(K_GRAD["tassa"] + a)}</strong></td>'
                  f'<td class="n">{gbp(K_GRAD["tassa"] + c)}</td></tr>')
    return pila(f'<div class="tab compatta"><table id="t-costi-grad"><caption class="sr">UK Graduate visa cost per person</caption><thead><tr><th scope="col">Visa length</th>'
            f'<th scope="col" class="n">Application fee</th><th scope="col" class="n">Health surcharge (adult)</th><th scope="col" class="n">Total, one adult</th>'
            f'<th scope="col" class="n">Total, child under 18</th></tr></thead><tbody>{righe}</tbody></table></div>')


def tabella_famiglie_grad():
    righe = ""
    for nome, a, f in (("You alone", 1, 0), ("You and your partner", 2, 0), ("Partner and 1 child", 2, 1), ("Partner and 2 children", 2, 2)):
        celle = "".join(f'<td class="n">{gbp((a + f) * K_GRAD["tassa"] + a * ihs(m, K_GRAD["ihs_a"]) + f * ihs(m, K_GRAD["ihs_m"]))}</td>' for m in (24, 18, 36))
        righe += f'<tr><th scope="row">{nome}</th>{celle}</tr>'
    return pila(f'<div class="tab compatta"><table id="t-famiglie-grad"><caption class="sr">UK Graduate visa total cost by family</caption><thead><tr><th scope="col">Who applies</th>'
            f'<th scope="col" class="n">2 years</th><th scope="col" class="n">18 months</th><th scope="col" class="n">3 years (PhD)</th></tr></thead><tbody>{righe}</tbody></table></div>')


def tabella_durata_grad():
    righe = [("Bachelor's, master's or other eligible course", "2 years", "18 months"), ("PhD or other doctoral qualification", "3 years", "3 years")]
    corpo = "".join(f'<tr><th scope="row">{a}</th><td>{b}</td><td>{c}</td></tr>' for a, b, c in righe)
    return pila(f'<div class="tab compatta"><table id="t-durata-grad"><caption class="sr">UK Graduate visa length by application date</caption><thead><tr><th scope="col">Qualification</th>'
            f'<th scope="col">Apply on or before 31 December 2026</th><th scope="col">Apply on or after 1 January 2027</th></tr></thead><tbody>{corpo}</tbody></table></div>')


def link_grad(rel, escludi=None):
    voci = [("", "UK Graduate visa: length, cost and end date"), ("18-months/", "Graduate visa 18 months from 2027"),
            ("cost/", "Graduate visa cost 2026"), ("phd/", "Graduate visa after a PhD: 3 years")]
    return ('<div class="griglia">' + "".join(f'<a href="{rel}{SEZ_GRAD}{p}"><span class="ic">{ico("coins" if "cost" in p else "calendar")}</span><span>{t}</span></a>'
                                              for p, t in voci if p != escludi) + "</div>")


def citazione_regola():
    return (f'<blockquote class="indice"><p style="margin:0">“{escape(LG["regola_18"]["frammento"])}”</p></blockquote>'
            f'<p class="fonte">Source: {link_fonte_grad("appendice")}, GR 8.1 (amended by {link_fonte_grad("hc1333")}). Read on {data_lunga(LETTO_GRAD)}. '
            f'Contains public sector information licensed under the Open Government Licence v3.0.</p>')


def faq_grad_comuni():
    return [
        ("How long is the UK Graduate visa?",
         "2 years if you apply on or before 31 December 2026 and 18 months if you apply on or after 1 January 2027. After a PhD or other doctoral qualification it lasts 3 years."),
        ("How much does the Graduate visa cost?",
         f"{gbp(K_GRAD['tassa'])} application fee plus the immigration health surcharge of {gbp(K_GRAD['ihs_a'])} a year: {gbp(ihs(24, K_GRAD['ihs_a']))} for 2 years, "
         f"{gbp(ihs(18, K_GRAD['ihs_a']))} for 18 months, {gbp(ihs(36, K_GRAD['ihs_a']))} for 3 years."),
        ("When does the Graduate visa start?", "From the day your application is approved, not from the day you apply. You usually get a decision within 8 weeks."),
        ("Can I extend the Graduate visa?", "No. You may be able to switch to another visa, for example a Skilled Worker visa."),
    ]


def pagina_grad_indice():
    rel = "../"
    percorso = SEZ_GRAD
    domande = faq_grad_comuni() + [
        ("Does the date I apply or the date of the decision count?", "The date you apply: the 18 months apply to applications made on or after 1 January 2027. The visa then runs from the decision date."),
        ("Can my partner and children come?", "If they are your dependants on your current Student visa (or children born in the UK during it), they can apply; their visa ends on the same date as yours."),
    ]
    corpo = f"""<section class="hero">{h1_diviso(f"UK Graduate visa: how long it lasts, what it costs and when it ends ({ANNO})")}
<p class="lead">A UK Graduate visa lasts <strong>2 years if you apply on or before 31 December 2026 and 18 months if you apply on or after 1 January 2027</strong> (3 years after a PhD), and costs {gbp(K_GRAD["tassa"])} plus the immigration health surcharge of {gbp(K_GRAD["ihs_a"])} a year, according to the GOV.UK Graduate visa guide read on {data_lunga(LETTO_GRAD)}. The calculator gives your length, end date and cost.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("passport")}<span>UK Graduate visa</span><span>read on {data_lunga(LETTO_GRAD)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Length for bachelor's and master's graduates</span><span class="sr">: </span><strong>2 years → 18 months from 1 January 2027</strong></p>
<div class="kpi"><div><b>3 years</b><span>after a PhD, unchanged</span></div><div><b>{gbp(K_GRAD["tassa"])}</b><span>application fee per person</span></div><div><b>{gbp(K_GRAD["ihs_a"])}</b><span>health surcharge per year (adult)</span></div><div><b>{gbp(K_GRAD["tassa"] + ihs(24, K_GRAD["ihs_a"]))}</b><span>total for one adult, 2 years</span></div></div>
{fonte_grad_p(("guida", "appendice"))}
</div></section>
{AVVISO_GRAD}
{AD}
{calc_graduate()}
<h2 id="length">How long the Graduate visa lasts</h2>
{tabella_durata_grad()}
<p>What counts is the <strong>date you apply</strong>. The visa then starts on the day your application is approved and runs from that date; your partner's and children's visas end on the same date as yours.</p>
{citazione_regola()}
<p>The Home Office's explanatory memorandum to HC 1333 adds: “{escape(LG["memorandum_526"]["frammento"])}” <a href="18-months/">What the 18-month change means</a>.</p>
{fonte_grad_p(("memorandum",))}
<h2 id="cost">What it costs</h2>
<p>Each person pays the {gbp(K_GRAD["tassa"])} application fee and the immigration health surcharge (IHS): {gbp(K_GRAD["ihs_a"])} a year for adults and {gbp(K_GRAD["ihs_m"])} a year for children under 18. For 18 months the surcharge is one year plus half a year.</p>
{tabella_costi_grad()}
{fonte_grad_p(("guida", "ihs", "tariffe"), f' (table "{escape(GRAD["tariffa_ods"]["titolo"])}")')}
<h2 id="apply">When and how to apply</h2>
<ul class="testo"><li>You must be in the UK and apply <strong>before your Student visa expires</strong>.</li>
<li>You can apply once your university or college has told the Home Office that you have successfully completed your course; you do not have to wait for graduation.</li>
<li>You usually get a decision within 8 weeks, and you can stay in the UK while you wait.</li>
<li>You cannot extend a Graduate visa; you may be able to switch to another visa, for example a <a href="{rel}uk-skilled-worker-visa/">Skilled Worker visa (salary thresholds)</a>.</li></ul>
{fonte_grad_p(("guida",))}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>Graduate visa pages</h2>
{link_grad(rel, "")}
<p><a href="{rel}uk-english-test/">UK visa English tests (SELT)</a> · <a href="{rel}{SEZ_OPT}">Studying in the US? OPT and STEM OPT fees and deadlines</a> · <a href="{rel}{SEZ}uk/">UK visa refusal rates by nationality</a></p>"""
    titolo = f"UK Graduate visa {ANNO}: 2 years or 18 months, cost and end date"
    descr = (f"UK Graduate visa: 2 years if you apply by 31 December 2026, 18 months from 1 January 2027, 3 years after a PhD; {gbp(K_GRAD['tassa'])} fee plus "
             f"{gbp(K_GRAD['ihs_a'])} a year health surcharge (GOV.UK, read {data_lunga(LETTO_GRAD)}). Calculator for end date and cost.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande)], briciole=[("UK Graduate visa", percorso)], script=STUDIO_JS)


def pagina_grad_18():
    rel = "../../"
    percorso = f"{SEZ_GRAD}18-months/"
    domande = [
        ("When does the Graduate visa change to 18 months?", "For applications made on or after 1 January 2027. If you apply on or before 31 December 2026, you get 2 years."),
        ("Does the 18 months apply to PhD graduates?", "No. After a PhD or other doctoral qualification the Graduate visa stays at 3 years."),
        ("If I apply in December 2026 and the decision comes in 2027, do I get 2 years?",
         "The rule looks at the date the application is made: an application made before 1 January 2027 falls under the 2-year rule. The visa then runs from the decision date."),
        ("Why is the Graduate visa being cut to 18 months?",
         "The Home Office's explanatory memorandum says the change follows the May 2025 Immigration White Paper and that too many graduates were not moving into graduate-level jobs."),
        ("Does the shorter visa cost less?",
         f"The application fee is the same ({gbp(K_GRAD['tassa'])}); the health surcharge is lower: {gbp(ihs(18, K_GRAD['ihs_a']))} for 18 months instead of {gbp(ihs(24, K_GRAD['ihs_a']))} for 2 years."),
    ]
    esempi = "".join(f'<tr><td>{data_lunga(d)}</td><td>{q}</td><td>{dur}</td></tr>' for d, q, dur in
                     (("2026-12-15", "Master's degree", "2 years"), ("2026-12-31", "Bachelor's degree", "2 years"), ("2027-01-01", "Master's degree", "18 months"),
                      ("2027-03-10", "PhD", "3 years")))
    corpo = f"""<section class="hero"><h1>Graduate visa 18 months: the change from 1 January 2027</h1>
<p class="lead">From <strong>1 January 2027</strong> the UK Graduate visa lasts <strong>18 months instead of 2 years</strong> for bachelor's and master's graduates; the date that counts is the day you apply, and PhD graduates keep 3 years (Immigration Rules, Appendix Graduate GR 8.1, as amended by Statement of Changes HC 1333; read on GOV.UK on {data_lunga(LETTO_GRAD)}).</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("calendar")}<span>Graduate visa length</span><span>read on {data_lunga(LETTO_GRAD)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Apply on or after 1 January 2027</span><span class="sr">: </span><strong>18 months</strong></p>
<div class="kpi"><div><b>2 years</b><span>apply on or before 31 December 2026</span></div><div><b>3 years</b><span>PhD, before and after</span></div><div><b>{gbp(ihs(18, K_GRAD["ihs_a"]))}</b><span>health surcharge for 18 months</span></div><div><b>{gbp(ihs(24, K_GRAD["ihs_a"]))}</b><span>health surcharge for 2 years</span></div></div>
{fonte_grad_p(("appendice", "hc1333", "guida"))}
</div></section>
{AVVISO_GRAD}
{AD}
{calc_graduate()}
<h2>The rule</h2>
{citazione_regola()}
<p>The Home Office's explanatory memorandum to HC 1333 (paragraph 5.26) says: “{escape(LG["memorandum_526"]["frammento"])}”</p>
{fonte_grad_p(("memorandum",))}
<h2>Examples</h2>
<div class="tab compatta"><table id="t-esempi-grad"><caption class="sr">Graduate visa length by application date</caption><thead><tr><th scope="col">You apply on</th><th scope="col">Qualification</th><th scope="col">Graduate visa length</th></tr></thead><tbody>{esempi}</tbody></table></div>
<h2>If you finish your course in late 2026</h2>
<ul class="testo"><li>You can apply once your university or college has told the Home Office that you completed the course: you do not have to wait for graduation.</li>
<li>You must be in the UK and apply before your Student visa expires.</li>
<li>Applying in December 2026 gives 2 years; applying from 1 January 2027 gives 18 months. Ask your university when it will report your completion.</li></ul>
{fonte_grad_p(("guida",))}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>More on the Graduate visa</h2>
{link_grad(rel, "18-months/")}"""
    titolo = "Graduate visa 18 months: the change from 1 January 2027"
    descr = (f"The UK Graduate visa drops from 2 years to 18 months for applications made on or after 1 January 2027; PhD stays 3 years (Appendix Graduate, HC 1333, "
             f"read {data_lunga(LETTO_GRAD)}). Calculator and examples.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande)],
           briciole=[("UK Graduate visa", SEZ_GRAD), ("18 months from 2027", percorso)], script=STUDIO_JS)


def pagina_grad_costo():
    rel = "../../"
    percorso = f"{SEZ_GRAD}cost/"
    t24 = K_GRAD["tassa"] + ihs(24, K_GRAD["ihs_a"])
    t18 = K_GRAD["tassa"] + ihs(18, K_GRAD["ihs_a"])
    t36 = K_GRAD["tassa"] + ihs(36, K_GRAD["ihs_a"])
    domande = [
        ("How much is the Graduate visa in 2026?", f"{gbp(t24)} for one adult applying on or before 31 December 2026: {gbp(K_GRAD['tassa'])} fee plus {gbp(ihs(24, K_GRAD['ihs_a']))} health surcharge for 2 years."),
        ("How much is it from January 2027?", f"{gbp(t18)} for one adult: the same {gbp(K_GRAD['tassa'])} fee plus {gbp(ihs(18, K_GRAD['ihs_a']))} health surcharge for 18 months."),
        ("How much do dependants pay?", f"Each dependant pays the {gbp(K_GRAD['tassa'])} fee and the health surcharge: the adult rate for a partner, {gbp(K_GRAD['ihs_m'])} a year for a child under 18."),
        ("Do I pay the health surcharge if I have private insurance?", "Yes: GOV.UK says you still need to pay it even if you have private medical insurance."),
        ("Is the fee refunded if I am refused?", "GOV.UK says you get the fee back only if you cancel before UKVI has started processing your application. Check GOV.UK for the health surcharge."),
    ]
    corpo = f"""<section class="hero"><h1>Graduate visa cost {ANNO}: {gbp(K_GRAD["tassa"])} fee plus health surcharge</h1>
<p class="lead">The UK Graduate visa costs <strong>{gbp(K_GRAD["tassa"])}</strong> per person plus the immigration health surcharge: {gbp(ihs(24, K_GRAD["ihs_a"]))} for 2 years, {gbp(ihs(18, K_GRAD["ihs_a"]))} for 18 months and {gbp(ihs(36, K_GRAD["ihs_a"]))} for 3 years, so <strong>{gbp(t24)}</strong> in total for one adult applying in 2026 (GOV.UK Graduate visa guide and Home Office fees table of {escape(GRAD["tariffa_ods"]["titolo"].split(", ")[-1])}, read on {data_lunga(LETTO_GRAD)}).</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("coins")}<span>Graduate visa cost, one adult</span><span>read on {data_lunga(LETTO_GRAD)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">2 years (apply on or before 31 December 2026)</span><span class="sr">: </span><strong>{gbp(t24)}</strong></p>
<div class="kpi"><div><b>{gbp(t18)}</b><span>18 months (from 1 January 2027)</span></div><div><b>{gbp(t36)}</b><span>3 years (PhD)</span></div><div><b>{gbp(K_GRAD["tassa"])}</b><span>application fee, also for dependants</span></div><div><b>{gbp(K_GRAD["ihs_m"])}</b><span>health surcharge per year, child under 18</span></div></div>
{fonte_grad_p(("guida", "ihs", "tariffe"))}
</div></section>
{AVVISO_GRAD}
{AD}
{calc_graduate()}
<h2>Cost per person</h2>
{tabella_costi_grad()}
{fonte_grad_p(("guida", "ihs", "tariffe"))}
<h2>Cost for a family</h2>
<p>Partner and children count only if they are your dependants. Totals include the {gbp(K_GRAD["tassa"])} fee for each person and the health surcharge ({gbp(K_GRAD["ihs_a"])} a year for adults, {gbp(K_GRAD["ihs_m"])} for children under 18).</p>
{tabella_famiglie_grad()}
<h2>How the health surcharge is worked out</h2>
<ul class="testo"><li>{gbp(K_GRAD["ihs_a"])} per year for adults and {gbp(K_GRAD["ihs_m"])} per year for applicants under 18 at the time of application.</li>
<li>For a visa of more than one year and up to 18 months, you pay one year plus half a year: {gbp(ihs(18, K_GRAD["ihs_a"]))} for an adult.</li>
<li>Dependants aged 18 or over usually pay the same amount as you. You pay even if you have private medical insurance.</li></ul>
{fonte_grad_p(("ihs",))}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>More on the Graduate visa</h2>
{link_grad(rel, "cost/")}"""
    titolo = f"Graduate visa cost {ANNO}: {gbp(K_GRAD['tassa'])} fee plus health surcharge"
    descr = (f"UK Graduate visa cost: {gbp(K_GRAD['tassa'])} fee plus health surcharge, {gbp(t24)} for one adult for 2 years, {gbp(t18)} for 18 months, {gbp(t36)} for 3 years "
             f"(GOV.UK, read {data_lunga(LETTO_GRAD)}). Family totals and calculator.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande)],
           briciole=[("UK Graduate visa", SEZ_GRAD), ("Cost", percorso)], script=STUDIO_JS)


def pagina_grad_phd():
    rel = "../../"
    percorso = f"{SEZ_GRAD}phd/"
    t36 = K_GRAD["tassa"] + ihs(36, K_GRAD["ihs_a"])
    domande = [
        ("How long is the Graduate visa after a PhD?", "3 years, if you completed a PhD or other doctoral qualification with your Student visa."),
        ("Does the 2027 change affect PhD graduates?", "No. The 18 months from 1 January 2027 apply to other qualifications; PhD graduates continue to get 3 years."),
        ("How much does the PhD Graduate visa cost?", f"{gbp(t36)} for one adult: {gbp(K_GRAD['tassa'])} fee plus {gbp(ihs(36, K_GRAD['ihs_a']))} health surcharge for 3 years."),
        ("When does it start?", "On the day your application is approved. You must apply before your Student visa expires, from inside the UK."),
    ]
    corpo = f"""<section class="hero"><h1>Graduate visa after a PhD: 3 years, also after 2027</h1>
<p class="lead">After a PhD or other doctoral qualification the UK Graduate visa lasts <strong>3 years</strong>, and this does not change on 1 January 2027, when other graduates move to 18 months (Immigration Rules, Appendix Graduate GR 8.1, and the HC 1333 explanatory memorandum, read on GOV.UK on {data_lunga(LETTO_GRAD)}). It costs {gbp(K_GRAD["tassa"])} plus {gbp(ihs(36, K_GRAD["ihs_a"]))} of health surcharge.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("passport")}<span>Graduate visa after a PhD</span><span>read on {data_lunga(LETTO_GRAD)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Length</span><span class="sr">: </span><strong>3 years</strong></p>
<div class="kpi"><div><b>{gbp(t36)}</b><span>total, one adult</span></div><div><b>{gbp(ihs(36, K_GRAD["ihs_a"]))}</b><span>health surcharge, 3 years</span></div><div><b>{gbp(K_GRAD["tassa"])}</b><span>application fee</span></div><div><b>8 weeks</b><span>usual time for a decision</span></div></div>
{fonte_grad_p(("guida", "appendice", "memorandum"))}
</div></section>
{AVVISO_GRAD}
{AD}
{calc_graduate("phd")}
<h2>The rule</h2>
<p>The table in GR 8.1 gives "PhD or other doctoral qualification: 3 years" from the date of decision, with no cut-off date. The memorandum to HC 1333 says the 18 months apply "with PhD graduates continuing to receive three years of leave".</p>
{fonte_grad_p(("appendice", "memorandum"))}
<h2>Cost</h2>
{tabella_costi_grad()}
{fonte_grad_p(("guida", "ihs", "tariffe"))}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>More on the Graduate visa</h2>
{link_grad(rel, "phd/")}"""
    titolo = "Graduate visa after a PhD: 3 years, also after 2027"
    descr = (f"After a PhD the UK Graduate visa lasts 3 years, also for applications from 1 January 2027 (Appendix Graduate, read {data_lunga(LETTO_GRAD)}); "
             f"cost {gbp(t36)} for one adult. Calculator for end date and cost.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande)],
           briciole=[("UK Graduate visa", SEZ_GRAD), ("After a PhD", percorso)], script=STUDIO_JS)


def link_graduate(P, rel):
    """Riga dalla pagina UK Skilled Worker alla sezione Graduate visa."""
    if P.get("slug") != "uk-skilled-worker-visa":
        return ""
    return (f'<p class="small">{ico("check")} Finishing a UK degree? The <a href="{rel}{SEZ_GRAD}">Graduate visa</a> lasts 2 years if you apply by 31 December 2026 '
            f'and 18 months from 1 January 2027; you can switch to Skilled Worker from it.</p>')


def genera_studio():
    pagina_opt_indice()
    pagina_opt_scadenza()
    pagina_opt_disoccupazione()
    pagina_opt_stem()
    pagina_opt_proposta()
    pagina_opt_grazia()
    pagina_grad_indice()
    pagina_grad_18()
    pagina_grad_costo()
    pagina_grad_phd()


def controlli_studio():
    errori = []
    for nome, D in (("opt", OPT), ("graduate", GRAD)):
        cont = {k: D[k] for k in (("letture", "fonti", "federal_register", "ecfr") if nome == "opt" else ("letture", "fonti", "tariffa_ods"))}
        import hashlib
        if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != D["impronta"]:
            errori.append(f"{nome}: impronta del JSON diversa dal contenuto (file modificato a mano?)")
        if any(f.get("http") not in (200, None) for f in D["fonti"].values()):
            errori.append(f"{nome}: fonte non letta (HTTP diverso da 200)")
    if FR_OPT["tasse_opt"]["type"] != "Proposed Rule":
        errori.append("opt: la proposta sulle tasse OPT non è più una proposta: rileggere e aggiornare le pagine")
    if OPT["ecfr"]["giorni_dopo_fine_programma"] not in (30, 60):
        errori.append("opt: eCFR senza il numero di giorni")
    if K_GRAD["cambio"] != "2027-01-01" or K_GRAD["m_dopo"] != 18:
        errori.append("graduate: data o durata del cambio diverse da quelle scritte nei testi (1/1/2027, 18 mesi): rivedere i testi")
    return errori


CSS += CSS_STUDIO  # stili dei calcolatori e delle etichette di stato (tutte le pagine hanno lo stesso CSS)


# ---------------------------------------------------------------- Mexico residency: costi ufficiali e requisiti di reddito per consolato (31/10/2026)
# Dati: dati/mexico.json, scritto da raccolta/mexico.py (LFD e Anexo 4 RMF 2026, decreto DOF 7/11/2025, UMA INEGI, Lineamientos DOF 25/7/2025,
# pagine ufficiali dei consolati). Ogni cifra viene da "letture" o da "consolati" (valore + frammento del testo ufficiale).
# Il calcolatore (MX_JS) gira nel browser; verifica.py (controllo 21) lo confronta con un calcolo Python indipendente.
MX = json.loads((DATI / "mexico.json").read_text(encoding="utf-8"))
SEZ_MX = "mexico-residency/"
LMX = {k: v["valore"] for k, v in MX["letture"].items()}
FMX = MX["fonti"]
CONS_MX = MX["consolati"]
ESCL_MX = MX["esclusi"]
LETTO_MX = MX["letto_il"]
UMA_MX = LMX["uma_diaria"]
GIORNI_MX = {"tr": (LMX["rt_reddito_giorni"], LMX["rt_saldo_giorni"]), "pr": (LMX["rp_reddito_giorni"], LMX["rp_saldo_giorni"]), "fam": LMX["familiare_giorni"]}
TASSE_MX = {"1": LMX["a4_rt"]["1"], "2": LMX["a4_rt"]["2"], "3": LMX["a4_rt"]["3"], "4": LMX["a4_rt"]["4"], "pr": LMX["a4_rp"],
            "cambio": LMX["a4_cambio"], "repos": LMX["a4_repos"], "visa": LMX["a4_visa"]}
_SWM = AFFILIATI.get("_safetywing_mexico", {})
URL_SW_MX = _SWM.get("url", "")
SIMBOLI_MX = {"USD": ("US$", ""), "CAD": ("C$", ""), "GBP": ("£", ""), "EUR": ("€", ""), "MXN": ("MXN ", "")}


def pesos_uma(giorni):
    return round(giorni * UMA_MX, 2)


def mxn(x):
    """MXN 11,141 / MXN 79,770.80."""
    return "MXN " + (f"{x:,.0f}" if float(x).is_integer() else f"{x:,.2f}")


def importo_mx(x, valuta):
    s, d = SIMBOLI_MX[valuta]
    return s + (f"{x:,.0f}" if float(x).is_integer() else f"{x:,.2f}") + d


def conv_mx(x, da, a):
    """Conversione con i cambi BCE di riserva (EUR = 1); stessi passaggi di conv() in MX_JS."""
    t = dict(CAMBI["tassi"], EUR=1)
    return x / t[da] * t[a]


def circa_mx(x, da, a):
    v = conv_mx(x, da, a)
    return importo_mx(round(v) if v >= 100 else round(v, 2), a)


def ufficio_mx(C):
    return "embassy" if C["tipo"].startswith("Embassy") else "consulate"


def data_cons_mx(C, breve=False):
    p = C["pagine"][0]
    d = C["data_pagina"]
    if not d:
        return "no date on the page" if breve else "undated page; its peso amounts match the 2026 UMA"
    return (f"PDF dated {data_lunga(d)}" if p.get("formato") == "pdf" else f"page updated {data_lunga(d)}")


def prima_uma_mx(C):
    """La pagina del consolato ha una data anteriore al comunicato INEGI sull'UMA dell'anno (8/1/2026): non può usare l'UMA 2026."""
    return bool(C["data_pagina"]) and C["data_pagina"] < FMX["uma"]["data"]


def link_cons_mx(C, i=0, testo=None):
    p = C["pagine"][i]
    return f'<a href="{escape(p["url"])}" rel="noopener">{escape(testo or ("official page" if p.get("formato") != "pdf" else "official PDF"))}</a>'


def fonte_mx_link(k):
    f = FMX[k]
    return f'<a href="{escape(f["url"])}" rel="noopener">{escape(f["editore"])}, {escape(f["titolo"])}</a>'


def fonte_mx_p(chiavi=(), extra=""):
    voci = [fonte_mx_link(k) for k in chiavi]
    return f'<p class="fonte">Source{"s" if len(voci) + bool(extra) > 1 else ""}: {"; ".join(voci)}{("; " if voci and extra else "") + extra}. Read on {data_lunga(LETTO_MX)}.</p>'


def fonte_cons_p(C):
    pag = "; ".join(link_cons_mx(C, i, f'{"PDF" if p.get("formato") == "pdf" else "page"} {i + 1}') for i, p in enumerate(C["pagine"])) if len(C["pagine"]) > 1 else link_cons_mx(C)
    return (f'<p class="fonte">Source: Mexican {ufficio_mx(C)} in {escape(C["sede"])}, {pag} ({data_cons_mx(C, True)}), read on {data_lunga(LETTO_MX)}.</p>')


AVVISO_MX = ('<p class="avviso"><strong>Not legal or immigration advice.</strong> This page reports what Mexican law, the visa guidelines and the official pages of the '
             'consulates said on the date we read them. The consulate decides on your visa and can ask for more documents; amounts in dollars, pounds or '
             'Canadian dollars change when the consulate updates its exchange rate. Check your consulate\'s page before you apply.</p>')


def tabella_uma_mx():
    righe = [("Temporary residence: monthly income (last 6 months, net)", GIORNI_MX["tr"][0], "more than"),
             ("Temporary residence: average monthly balance (last 12 months)", GIORNI_MX["tr"][1], "equivalent to"),
             ("Permanent residence (retirees and pensioners): monthly pension (last 6 months)", GIORNI_MX["pr"][0], "more than"),
             ("Permanent residence (retirees and pensioners): average monthly balance (last 12 months)", GIORNI_MX["pr"][1], "equivalent to"),
             ("Each family member joining a resident: income or balance", GIORNI_MX["fam"], "more than / equivalent to")]
    corpo = "".join(f'<tr><th scope="row">{a}</th><td class="n">{intero(g)}</td><td class="n">{mxn(pesos_uma(g))}</td><td class="small">{w}</td></tr>' for a, g, w in righe)
    return (f'<div class="tab compatta"><table id="t-uma-mx"><caption class="sr">Mexican residence visa solvency in UMA days and pesos</caption><thead><tr>'
            f'<th scope="col">Requirement</th><th scope="col" class="n">Days of UMA</th><th scope="col" class="n">In pesos (2026 UMA: MXN {UMA_MX})</th>'
            f'<th scope="col">Wording</th></tr></thead><tbody>{corpo}</tbody></table></div>')


def tabella_tasse_mx(dettaglio=False):
    righe = [(f"Temporary resident card, up to 1 year", "Art. 8, VI a)", TASSE_MX["1"]),
             ("Temporary resident card, 2 years", "Art. 8, VI b)", TASSE_MX["2"]),
             ("Temporary resident card, 3 years", "Art. 8, VI c)", TASSE_MX["3"]),
             ("Temporary resident card, 4 years", "Art. 8, VI d)", TASSE_MX["4"]),
             ("Permanent resident card", "Art. 8, VII", TASSE_MX["pr"]),
             ("Change of immigration status (paid on top of the new card)", "Art. 9", TASSE_MX["cambio"]),
             ("Replacement of a resident card", "Art. 8", TASSE_MX["repos"]),
             ("Visa at a Mexican consulate (ordinary visa in a foreign passport)", "Art. 22, III d)", TASSE_MX["visa"])]
    corpo = ""
    for a, art, (legge, paga) in righe:
        corpo += (f'<tr><th scope="row">{a}</th><td class="n"><strong>{mxn(paga)}</strong></td><td class="n small">{mxn(legge)}</td>'
                  f'<td class="n">≈ {circa_mx(paga, "MXN", "USD")}</td><td class="n">≈ {circa_mx(paga, "MXN", "EUR")}</td>'
                  + (f'<td class="n">≈ {circa_mx(paga, "MXN", "GBP")}</td><td class="n">≈ {circa_mx(paga, "MXN", "CAD")}</td>' if dettaglio else "")
                  + f'<td class="small">{art} LFD</td></tr>')
    extra_th = '<th scope="col" class="n">≈ GBP</th><th scope="col" class="n">≈ CAD</th>' if dettaglio else ""
    return (f'<div class="tab compatta"><table id="t-tasse-mx"><caption class="sr">Mexico immigration fees 2026</caption><thead><tr><th scope="col">What you pay for</th>'
            f'<th scope="col" class="n">You pay ({ANNO})</th><th scope="col" class="n">Amount in the law</th><th scope="col" class="n">≈ USD</th><th scope="col" class="n">≈ EUR</th>{extra_th}'
            f'<th scope="col">Legal basis</th></tr></thead><tbody>{corpo}</tbody></table></div>')


def cella_mx(C, tipo, cosa):
    v = C.get(tipo, {}).get(cosa)
    if not v:
        return '<td class="n small" data-v="">not on the pages we read</td>'
    usd = conv_mx(v["importo"], C["valuta"], "USD")
    pre = "approx. " if C.get("approssimato") else ""
    return f'<td class="n" data-v="{usd:.2f}">{pre}{importo_mx(v["importo"], C["valuta"])}</td>'


def riga_cons_mx(C, rel_sez):
    t = C.get("tassa")
    return (f'<tr><td><a href="{rel_sez}{C["id"]}/">{escape(C["sede"])}</a><br><span class="small">{escape(C["paese"])} · {ufficio_mx(C)}</span></td>'
            f'{cella_mx(C, "tr", "reddito")}{cella_mx(C, "tr", "saldo")}{cella_mx(C, "pr", "reddito")}{cella_mx(C, "pr", "saldo")}'
            f'<td class="n" data-v="{conv_mx(t["importo"], t["valuta"], "USD") if t else 0:.2f}">{importo_mx(t["importo"], t["valuta"]) if t else "–"}</td>'
            f'<td data-v="{(C["data_pagina"] or "0").replace("-", "")}">{data_lunga(C["data_pagina"]) if C["data_pagina"] else "no date"}</td>'
            f'<td>{link_cons_mx(C)}</td></tr>')


def tabella_cons_mx(rel_sez, id_t="t-cons-mx"):
    ordinati = sorted(CONS_MX, key=lambda C: (C["paese"] != "United States", C["paese"], C["sede"]))
    righe = "".join(riga_cons_mx(C, rel_sez) for C in ordinati)
    return (f'<p class="filtro"><label><span class="sr">Filter by city or country</span><input type="search" placeholder="Filter: e.g. Canada" data-filtro="{id_t}" autocomplete="off"></label></p>'
            f'<div class="tab compatta"><table class="ord larga" id="{id_t}"><caption class="sr">Income and savings asked by Mexican consulates for residence visas</caption><thead><tr>'
            f'{th_ord("Consulate", False, "ascending")}{th_ord("Temporary: income a month", True, "ascending")}{th_ord("Temporary: savings", True, "ascending")}'
            f'{th_ord("Permanent: pension a month", True, "ascending")}{th_ord("Permanent: savings", True, "ascending")}{th_ord("Visa fee", True, "ascending")}'
            f'{th_ord("Page date")}<th scope="col">Official page</th></tr></thead><tbody>{righe}</tbody></table></div>'
            f'<p class="fonte">Source: the official page linked in each row (Mexican consulates and embassy consular sections, consulmex.sre.gob.mx), read on {data_lunga(LETTO_MX)}. '
            f'Amounts are in the currency the page uses. "Income" means net monthly income from a job or pension over the last 6 months; "savings" means the average monthly '
            f'balance over the last 12 months. Sorting by amount uses ECB reference rates of {data_lunga(CAMBI["data"])}.</p>')


# ---------- calcolatore: reddito o risparmi -> raggiunge la cifra di ogni consolato letto?
K_MX = {"cons": [{"id": C["id"], "sede": C["sede"], "val": C["valuta"],
                  "tr": [C["tr"]["reddito"]["importo"], C["tr"]["saldo"]["importo"]],
                  "pr": ([C["pr"]["reddito"]["importo"], C["pr"]["saldo"]["importo"]] if "pr" in C else None),
                  "appr": bool(C.get("approssimato"))} for C in sorted(CONS_MX, key=lambda C: C["sede"])],
        "uma": {"tr": [pesos_uma(GIORNI_MX["tr"][0]), pesos_uma(GIORNI_MX["tr"][1])], "pr": [pesos_uma(GIORNI_MX["pr"][0]), pesos_uma(GIORNI_MX["pr"][1])]},
        "tassi": {k: (1 if k == "EUR" else CAMBI["tassi"][k]) for k in ("EUR", "USD", "GBP", "CAD", "MXN")}, "data_cambi": data_lunga(CAMBI["data"])}

MX_JS = r"""
(function(){
var S={USD:'US$',CAD:'C$',GBP:'£',EUR:'€',MXN:'MXN '};
function r2(x){return Math.round(x*100)/100;}
function conv(x,da,a,t){return x/t[da]*t[a];}
function fmt(x,v){var d=Math.abs(x-Math.round(x))<1e-9?0:2;var s=x.toFixed(d).replace(/\B(?=(\d{3})+(?!\d))/g,',');return S[v]+s;}
var C={mx:function(importo,val,cosa,tipo,k){var x=+importo;if(!(x>=0)||importo===''||importo===null)return null;var i=cosa==='saldo'?1:0;var out=[],nok=0,n=0;
 k.cons.forEach(function(c){var s=c[tipo];if(!s){out.push({id:c.id,assente:true});return;}var soglia=s[i];var tuo=c.val===val?x:r2(conv(x,val,c.val,k.tassi));
  var ok=tuo>=soglia;n++;if(ok)nok++;out.push({id:c.id,soglia:soglia,val:c.val,tuo:tuo,stessa:c.val===val,ok:ok,appr:c.appr});});
 var su=k.uma[tipo][i];var tu=val==='MXN'?x:r2(conv(x,val,'MXN',k.tassi));
 return {righe:out,uma:{soglia:su,tuo:tu,ok:i===1?tu>=su:tu>su},nok:nok,n:n};}};
window.CALC_MX=C;
function nome(k,id){for(var j=0;j<k.cons.length;j++)if(k.cons[j].id===id)return k.cons[j].sede;return id;}
document.querySelectorAll('[data-mx]').forEach(function(box){var k=JSON.parse(box.getAttribute('data-k'));var f=box.querySelector('form');var out=box.querySelector('[data-out]');var rel=box.getAttribute('data-rel')||'';
 function go(){try{var cosa=f.cosa.value,tipo=f.tipo.value,val=f.valuta.value;var r=C.mx(f.importo.value,val,cosa,tipo,k);
  if(!r){out.innerHTML='<p class="small">Type your '+(cosa==='saldo'?'average monthly bank balance':'net monthly income')+' to compare it with the figure each consulate publishes.</p>';return;}
  var h='<p class="r-lab">'+(tipo==='pr'?'Permanent residence':'Temporary residence')+' · '+(cosa==='saldo'?'savings':'income')+'</p><p class="tot">'+r.nok+' <span>of '+r.n+' consulates</span></p>'+
   '<p class="r-anno">Your '+(cosa==='saldo'?'balance':'income')+' reaches the published figure at '+r.nok+' of the '+r.n+' consulates we read.</p><ul class="r-righe">';
  r.righe.forEach(function(x){if(x.assente)return;h+='<li class="'+(x.ok?'mx-ok':'mx-no')+'"><span class="r-lab">'+(x.ok?'✓ Reaches':'✗ Below')+' · <a href="'+rel+x.id+'/">'+nome(k,x.id)+'</a></span><b>'+(x.appr?'approx. ':'')+fmt(x.soglia,x.val)+'</b><span class="small">'+(x.stessa?'':'yours ≈ '+fmt(x.tuo,x.val)+' at ECB rates of '+k.data_cambi)+'</span></li>';});
  h+='</ul><p class="small" style="margin-top:10px">Guidelines (UMA): '+(cosa==='saldo'?'balance equivalent to ':'more than ')+fmt(r.uma.soglia,'MXN')+' a month; yours '+(val==='MXN'?'is ':'≈ ')+fmt(r.uma.tuo,'MXN')+' → '+(r.uma.ok?(cosa==='saldo'?'reaches it':'above'):(cosa==='saldo'?'below':'not above'))+'. Consulates convert with their own rate and date; an income exactly equal to a figure may not be enough where the page says "more than".</p>';
  out.innerHTML=h;}catch(e){out.innerHTML='';}}
 f.addEventListener('input',go);f.addEventListener('change',go);f.addEventListener('submit',function(e){e.preventDefault();go();});go();});
})();
"""
CSS += (".r-righe li.mx-ok{border-color:var(--ok)}.r-righe li.mx-ok .r-lab{color:var(--ok)}.r-righe li.mx-no .r-lab{color:var(--no)}"
        ".r-righe li .r-lab a{color:inherit}")


def calc_mx(rel_sez, valuta="USD", tipo="tr"):
    opz_v = "".join(f'<option value="{v}"{" selected" if v == valuta else ""}>{v}</option>' for v in ("USD", "CAD", "GBP", "EUR", "MXN"))
    campi = (f'<label><span class="lt">{ico("wallet")}Amount</span><input type="number" name="importo" min="0" step="any" placeholder="e.g. 4500" inputmode="decimal"></label>'
             f'<label><span class="lt">{ico("exchange")}Currency</span><select name="valuta">{opz_v}</select></label>'
             f'<label class="pieno"><span class="lt">{ico("list")}The amount is</span><select name="cosa"><option value="reddito">Net monthly income (job or pension)</option>'
             f'<option value="saldo">Average monthly bank balance (savings)</option></select></label>'
             f'<label class="pieno"><span class="lt">{ico("passport")}Residence</span><select name="tipo"><option value="tr"{" selected" if tipo == "tr" else ""}>Temporary (1 to 4 years)</option>'
             f'<option value="pr"{" selected" if tipo == "pr" else ""}>Permanent (retirees and pensioners)</option></select></label>')
    nota = (f'Compared with the figure each consulate publishes, in its currency; other currencies are converted with ECB reference rates of {data_lunga(CAMBI["data"])}. '
            f'For one applicant: family members add their own amount. Nothing you type leaves your browser.')
    return (f'<section class="card calc" data-mx data-rel="{rel_sez}" data-k=\'{json.dumps(K_MX, separators=(",", ":"))}\' aria-label="Mexico residency income checker">'
            f'<div class="calc-grid"><form autocomplete="off"><h2 style="margin:0 0 14px;font-size:1.2rem">{ico("calc")} Do you reach the consulates\' figures?</h2>'
            f'<div class="campi">{campi}</div><p class="small" style="margin:12px 0 0">{nota}</p></form>'
            f'<div class="calc-out"><div class="risultato" data-out aria-live="polite"><noscript>Turn on JavaScript to use the checker; the figures are in the table below.</noscript></div></div></div></section>')


def box_assicurazione_mx(rel):
    """Riquadro SafetyWing dopo le informazioni ufficiali: le pagine dei consolati lette non chiedono un'assicurazione."""
    if not URL_SW_MX:
        return ""
    return (f'<section class="card aff-r" aria-labelledby="aff-m-h"><div class="aff-r-t"><span class="ic">{ico("shield")}</span>'
            f'<h2 id="aff-m-h">Health cover while you move</h2><span class="aff-tag">Affiliate</span></div>'
            f'<p>None of the consulate pages we read asks for health insurance for a temporary or permanent resident visa: they ask for a passport, a photo, '
            f'proof of income or savings and the fee. If you want health cover for the months you travel and settle in, compare policies before you go.</p>'
            f'<p class="aff-r-cta"><a class="btn" href="{escape(URL_SW_MX)}" rel="sponsored noopener" target="_blank">See SafetyWing nomad insurance{ico("arrow")}'
            f'<span class="sr"> (opens in a new tab)</span></a></p>'
            f'<p class="small">SafetyWing sells travel medical insurance for travellers and nomads online. {MON.RIGA_EN} Insurance is not a requirement on the '
            f'consulate pages we read and does not change the consulate\'s decision.</p></section>')


def griglia_cons_mx(rel_sez, escludi=None):
    return ('<div class="griglia">' + "".join(
        f'<a href="{rel_sez}{C["id"]}/"><span class="ic">{ico("passport")}</span><span>{escape(C["sede"])}<small>temporary: {"approx. " if C.get("approssimato") else ""}'
        f'{importo_mx(C["tr"]["reddito"]["importo"], C["valuta"])} a month · {escape(C["paese"])}</small></span></a>'
        for C in sorted(CONS_MX, key=lambda C: C["sede"]) if C["id"] != escludi) + "</div>")


def esclusi_mx():
    righe = "".join(f'<li><a href="{escape(e["url"])}" rel="noopener">{escape(e["sede"])}</a>: {escape(e["nota"])}'
                    + (" (figures from before 2026, not used)" if e["motivo"] == "vecchia" else "") + "</li>" for e in ESCL_MX)
    return (f'<h2 id="not-included">Consulates not in the table</h2><p class="small">We only list a consulate when its own page writes the amount and the page is from {ANNO} '
            f'(or uses the {ANNO} UMA). Pages we opened on {data_lunga(LETTO_MX)} but did not use:</p><ul class="testo small">{righe}</ul>'
            '<p class="small">Many other consulates publish their requirements too: if yours is not here, its page is the reference.</p>')


def link_mx(rel_sez, escludi=""):
    voci = [("", "Mexico residency: fees and income by consulate", "passport"), ("income-requirements/", "Income requirements by consulate", "wallet"),
            ("fees/", f"Mexico residency fees {ANNO}", "coins")]
    return ('<div class="griglia">' + "".join(f'<a href="{rel_sez}{p}"><span class="ic">{ico(i)}</span><span>{t}</span></a>' for p, t, i in voci if p != escludi) + "</div>")


def domande_comuni_mx():
    tr1, tr4, pr = TASSE_MX["1"][1], TASSE_MX["4"][1], TASSE_MX["pr"][1]
    return [
        ("How much does it cost to get residency in Mexico?",
         f"Two payments. The visa at a Mexican consulate (US$56 at the US consulates we read; {mxn(TASSE_MX['visa'][1])} in the law), then the resident card from the "
         f"National Migration Institute (INM) in Mexico: {mxn(tr1)} for a temporary resident card of up to one year, {mxn(tr4)} for four years, {mxn(pr)} for a permanent "
         f"resident card ({ANNO} amounts, Annex 4 of the Miscellaneous Tax Resolution)."),
        ("What is the income requirement for Mexican temporary residency?",
         f"The visa guidelines ask for a net monthly income of more than {intero(GIORNI_MX['tr'][0])} days of UMA over the last six months: {mxn(pesos_uma(GIORNI_MX['tr'][0]))} "
         f"with the {ANNO} UMA of MXN {UMA_MX}. Or an average balance of {intero(GIORNI_MX['tr'][1])} days of UMA ({mxn(pesos_uma(GIORNI_MX['tr'][1]))}) over the last 12 months. "
         "Each consulate publishes the amount in its own currency."),
        ("What is the income requirement for Mexican permanent residency?",
         f"For retirees and pensioners: a monthly pension of more than {intero(GIORNI_MX['pr'][0])} days of UMA ({mxn(pesos_uma(GIORNI_MX['pr'][0]))}) over the last six months, "
         f"or an average balance of {intero(GIORNI_MX['pr'][1])} days of UMA ({mxn(pesos_uma(GIORNI_MX['pr'][1]))}) over the last 12 months."),
        ("Why do Mexican consulates ask for different amounts?",
         "The rule is in pesos and the consulates convert it with their own exchange rate on the day they update their page. A page updated in January can show a "
         "lower dollar figure than one updated in May. Washington still writes its amounts in pesos, a little above the UMA calculation."),
    ]


# ---------- pagine
def pagina_mx_indice():
    rel = "../"
    percorso = SEZ_MX
    sd = next(C for C in CONS_MX if C["id"] == "san-diego")
    lon = next(C for C in CONS_MX if C["id"] == "london")
    van = next(C for C in CONS_MX if C["id"] == "vancouver")
    tr_r = pesos_uma(GIORNI_MX["tr"][0])
    usd_tr = sorted(conv_mx(C["tr"]["reddito"]["importo"], C["valuta"], "USD") for C in CONS_MX)
    domande = domande_comuni_mx() + [
        ("Do I pay again when I renew my temporary resident card?",
         "Yes. The Ley Federal de Derechos says that renewing a resident document costs the same fee as issuing it."),
        ("Is there a discount on the resident card fee?",
         "Since 2026 the law gives a 50% reduction to temporary and permanent residents who show the INM that they are in Mexico for family unity, for a job offer "
         "from a registered employer, or invited by an organisation for unpaid activities."),
    ]
    ld = [ld_faq(domande), ld_dataset("Mexico residence visa income and savings requirements by consulate",
                                      f"Income and savings amounts published by {len(CONS_MX)} Mexican consulates for temporary and permanent resident visas, with Mexico's {ANNO} immigration fees.",
                                      percorso, [FMX["lineamientos"]["url"], FMX["anexo4"]["url"], FMX["uma"]["url"]], LETTO_MX, "https://creativecommons.org/licenses/by/4.0/")]
    corpo = f"""<section class="hero">{h1_diviso(f"Mexico residency {ANNO}: official fees and income requirements by consulate")}
<p class="lead">A Mexican temporary resident card for up to one year costs <strong>{mxn(TASSE_MX["1"][1])}</strong> and a permanent resident card <strong>{mxn(TASSE_MX["pr"][1])}</strong> in {ANNO}, according to Annex 4 of Mexico's {ANNO} Miscellaneous Tax Resolution (Diario Oficial, 28 December 2025) read on {data_lunga(LETTO_MX)}. For the visa you first need a net monthly income above {intero(GIORNI_MX["tr"][0])} days of UMA, {mxn(tr_r)} with the {ANNO} UMA of MXN {UMA_MX} (INEGI), which each consulate turns into its own currency: {importo_mx(sd["tr"]["reddito"]["importo"], "USD")} in San Diego, {importo_mx(lon["tr"]["reddito"]["importo"], "GBP")} in London, {importo_mx(van["tr"]["reddito"]["importo"], "CAD")} in Vancouver.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("passport")}<span>Mexico residency</span><span>read on {data_lunga(LETTO_MX)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Temporary resident visa: net income a month (last 6 months)</span><span class="sr">: </span><strong>{mxn(tr_r)}</strong> ({intero(GIORNI_MX["tr"][0])} × UMA)</p>
<div class="kpi"><div><b>{mxn(TASSE_MX["1"][1])}</b><span>temporary resident card, up to 1 year</span></div><div><b>{mxn(TASSE_MX["pr"][1])}</b><span>permanent resident card</span></div><div><b>MXN {UMA_MX}</b><span>UMA a day, from {data_lunga(LMX["uma_dal"])}</span></div><div><b>{importo_mx(round(usd_tr[0]), "USD")}–{importo_mx(round(usd_tr[-1]), "USD")}</b><span>income figure at the {len(CONS_MX)} consulates we read, ≈ in US dollars</span></div></div>
{fonte_mx_p(("anexo4", "lineamientos", "uma"))}
</div></section>
{AVVISO_MX}
{AD}
{calc_mx("")}
<h2 id="consulates">What each consulate asks for</h2>
<p class="small">One row per consulate whose official page writes the amount, read on {data_lunga(LETTO_MX)}. Type to filter, or tap a column heading to sort. You need income <em>or</em> savings, not both.</p>
{tabella_cons_mx("")}
<h2 id="uma">How the amounts are set: days of UMA</h2>
<p>The visa guidelines of the Interior and Foreign ministries (in force since August 2025) count solvency in days of UMA, the reference unit Mexico uses in place of the minimum wage. INEGI set the {ANNO} UMA at MXN {UMA_MX} a day from {data_lunga(LMX["uma_dal"])}. Multiply and you get the peso amounts; the consulates then convert them.</p>
{tabella_uma_mx()}
{fonte_mx_p(("lineamientos", "uma"))}
<p class="small">The London embassy publishes exactly these peso amounts with a pound conversion (HSBC rate of 30 January 2026). Washington writes its own peso figures, {mxn(next(C for C in CONS_MX if C["id"] == "washington-dc")["tr"]["reddito"]["importo"])} of income and {mxn(next(C for C in CONS_MX if C["id"] == "washington-dc")["tr"]["saldo"]["importo"])} of savings, {(lambda W: f"{(W['tr']['reddito']['importo'] / tr_r - 1) * 100:.1f}% and {(W['tr']['saldo']['importo'] / pesos_uma(GIORNI_MX['tr'][1]) - 1) * 100:.1f}%")(next(C for C in CONS_MX if C["id"] == "washington-dc"))} above the UMA calculation; the page does not say how they are calculated. US consulates that updated their page at different times show different dollar figures for the same rule, and New York's PDF (5 January 2026) is older than INEGI's announcement of the {ANNO} UMA (8 January 2026).</p>
<h2 id="fees">Fees in {ANNO}</h2>
<p>After the consulate issues the visa you have 30 days from arrival to apply for the resident card at the National Migration Institute (INM), as the consulate pages say (for example <a href="{escape(next(C for C in CONS_MX if C["id"] == "portland")["pagine"][0]["url"])}" rel="noopener">Portland</a>); the INM charges the fees of the Ley Federal de Derechos. The amounts below are the {ANNO} figures of Annex 4 of the Miscellaneous Tax Resolution: "you pay" is the rounded amount ("con ajuste"). Renewing a card costs the same as issuing it.</p>
{tabella_tasse_mx()}
{fonte_mx_p(("anexo4", "lfd", "decreto"), f"conversions at ECB reference rates of {data_lunga(CAMBI['data'])}")}
<p><a href="fees/">All {ANNO} fees, the 50% reduction and examples</a> · <a href="income-requirements/">Income requirements in detail</a></p>
{box_assicurazione_mx(rel)}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>Consulate pages on this site</h2>
{griglia_cons_mx("")}
{esclusi_mx()}
<p><a href="{rel}digital-nomad-visa-income-requirements/">Digital nomad visa income requirements in Europe</a> · <a href="{rel}{SEZ_DTV}">Thailand DTV visa by embassy</a> · <a href="{rel}">Visa income calculator</a></p>"""
    titolo = f"Mexico residency {ANNO}: fees and income requirements by consulate"
    descr = (f"Mexico {ANNO}: temporary resident card {mxn(TASSE_MX['1'][1])}, permanent {mxn(TASSE_MX['pr'][1])} (DOF). Income needed: {mxn(tr_r)} a month "
             f"({intero(GIORNI_MX['tr'][0])} UMA) and what {len(CONS_MX)} consulates ask in USD, CAD and GBP, with a checker.")
    pagina(percorso, titolo, descr, corpo, ordina=True, jsonld_extra=ld, briciole=[("Mexico residency", percorso)], script=MX_JS)


def pagina_mx_reddito():
    rel = "../../"
    percorso = f"{SEZ_MX}income-requirements/"
    tr_r, tr_s = pesos_uma(GIORNI_MX["tr"][0]), pesos_uma(GIORNI_MX["tr"][1])
    pr_r, pr_s = pesos_uma(GIORNI_MX["pr"][0]), pesos_uma(GIORNI_MX["pr"][1])
    fam = pesos_uma(GIORNI_MX["fam"])
    righe = ""
    for C in sorted(CONS_MX, key=lambda C: conv_mx(C["tr"]["reddito"]["importo"], C["valuta"], "USD")):
        r = C["tr"]["reddito"]["importo"]
        implicito = tr_r / conv_mx(r, C["valuta"], "MXN") if C["valuta"] != "MXN" else 1
        righe += (f'<tr><td><a href="../{C["id"]}/">{escape(C["sede"])}</a></td><td class="n">{"approx. " if C.get("approssimato") else ""}{importo_mx(r, C["valuta"])}</td>'
                  f'<td class="n">{importo_mx(C["tr"]["saldo"]["importo"], C["valuta"])}</td>'
                  f'<td class="n">{"–" if C["valuta"] == "USD" else "≈ " + circa_mx(r, C["valuta"], "USD")}</td><td class="small">{data_cons_mx(C, True)}</td></tr>')
    usa = sorted((C for C in CONS_MX if C["valuta"] == "USD" and not C.get("approssimato")), key=lambda C: C["tr"]["reddito"]["importo"])
    basso, alto = usa[0], usa[-1]
    tab = (f'<div class="tab compatta"><table id="t-reddito-mx"><caption class="sr">Temporary residence income by consulate</caption><thead><tr><th scope="col">Consulate</th>'
           f'<th scope="col" class="n">Income a month</th><th scope="col" class="n">or savings</th><th scope="col" class="n">≈ in USD</th><th scope="col">Page date</th></tr></thead>'
           f'<tbody>{righe}</tbody></table></div>')
    righe_pr = "".join(f'<tr><td><a href="../{C["id"]}/">{escape(C["sede"])}</a></td><td class="n">{importo_mx(C["pr"]["reddito"]["importo"], C["valuta"])}</td>'
                       f'<td class="n">{importo_mx(C["pr"]["saldo"]["importo"], C["valuta"])}</td><td class="small">{data_cons_mx(C, True)}</td></tr>'
                       for C in sorted(CONS_MX, key=lambda C: C["sede"]) if "pr" in C)
    tab_pr = (f'<div class="tab compatta"><table id="t-pensione-mx"><caption class="sr">Permanent residence pension and savings by consulate</caption><thead><tr><th scope="col">Consulate</th>'
              f'<th scope="col" class="n">Pension a month</th><th scope="col" class="n">or savings</th><th scope="col">Page date</th></tr></thead><tbody>{righe_pr}</tbody></table></div>')
    domande = [
        ("Is the income requirement before or after tax?",
         "After tax. The guidelines speak of monthly income \"libres de gravámenes\" (free of taxes), and the consulates write \"after taxes\" or \"net\"."),
        ("Can I use savings instead of income?",
         f"Yes, one or the other. For temporary residence: an average monthly balance of {intero(GIORNI_MX['tr'][1])} days of UMA ({mxn(tr_s)}) over the last 12 months."),
        ("How much more do I need for my spouse or children?",
         f"The guidelines ask for {intero(GIORNI_MX['fam'])} days of UMA ({mxn(fam)}) for each family member, as income or balance. Las Vegas writes US$1,498 per family member, Vancouver and Montreal C$2,090."),
        ("Which UMA do the consulates use?",
         f"The UMA of the year: MXN {UMA_MX} a day from {data_lunga(LMX['uma_dal'])} to 31 January 2027 (INEGI). A page dated before 8 January {ANNO}, when INEGI announced the {ANNO} UMA, cannot be based on it: New York's PDF is dated 5 January {ANNO} and does not say which UMA it uses."),
    ] + domande_comuni_mx()[3:]
    corpo = f"""<section class="hero">{h1_diviso(f"Mexico residency income requirements {ANNO}: by consulate")}
<p class="lead">For a Mexican temporary resident visa the guidelines ask for a net monthly income of more than <strong>{intero(GIORNI_MX["tr"][0])} days of UMA, {mxn(tr_r)}</strong> over the last six months, or savings of {mxn(tr_s)}, with the {ANNO} UMA of MXN {UMA_MX} (visa guidelines, Diario Oficial of 25 July 2025, and INEGI) read on {data_lunga(LETTO_MX)}. In the consulates' own currencies that is between {importo_mx(min(C["tr"]["reddito"]["importo"] for C in CONS_MX if C["valuta"] == "USD"), "USD")} and {importo_mx(max(C["tr"]["reddito"]["importo"] for C in CONS_MX if C["valuta"] == "USD"), "USD")} at the US consulates we read.</p></section>
{AVVISO_MX}
{calc_mx("../")}
{AD}
<h2>The rule in pesos</h2>
{tabella_uma_mx()}
{fonte_mx_p(("lineamientos", "uma"))}
<ul class="testo"><li><strong>Income</strong>: from a job or a pension, net of tax, in each of the last six months, with the bank statements that show it.</li>
<li><strong>Savings</strong>: the average monthly balance of your bank or investment accounts over the last twelve months.</li>
<li><strong>Permanent residence</strong> on this route is for retirees and pensioners: a pension of more than {mxn(pr_r)} a month, or savings of {mxn(pr_s)} (the guidelines list both under "jubilados o pensionados").</li></ul>
<h2 id="temporary">Temporary residence: what each consulate asks</h2>
{tab}
<p class="fonte">Source: the official page of each consulate (linked on its page here), read on {data_lunga(LETTO_MX)}. "≈ in USD" converts the published figure with ECB reference rates of {data_lunga(CAMBI["data"])}.</p>
<p class="small">The same rule gives different dollar figures because each consulate converts the pesos on the day it updates its page: {basso["sede"]} ({data_cons_mx(basso, True)}) is lowest, {alto["sede"]} ({data_cons_mx(alto, True)}) highest among the US consulates.{"".join(f" The {X['sede']} PDF ({data_lunga(X['data_pagina'])}) is older than INEGI's announcement of the {ANNO} UMA (8 January {ANNO}) and does not say which UMA it uses." for X in CONS_MX if prima_uma_mx(X))} Portland gives the UMA days and an "approx." dollar figure.</p>
<h2 id="permanent">Permanent residence (retirees): pension or savings</h2>
<p>The guidelines ask for a monthly pension of more than {intero(GIORNI_MX["pr"][0])} days of UMA ({mxn(pr_r)}) over the last six months, or an average balance of {mxn(pr_s)} over the last 12 months.</p>
{tab_pr}
<p class="fonte">Source: the official page of each consulate, read on {data_lunga(LETTO_MX)}. Consulates without a permanent-residence figure in this table did not publish one on the pages we read.</p>
{box_assicurazione_mx(rel)}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>More on Mexico residency</h2>
{link_mx("../", "income-requirements/")}
{griglia_cons_mx("../")}"""
    titolo = f"Mexico residency income requirements {ANNO}: every consulate we read"
    descr = (f"Mexico temporary residency income {ANNO}: more than {intero(GIORNI_MX['tr'][0])} days of UMA ({mxn(tr_r)} a month) or {mxn(tr_s)} in savings; "
             f"permanent {mxn(pr_r)}. What {len(CONS_MX)} consulates ask in USD, CAD and GBP.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande)], briciole=[("Mexico residency", SEZ_MX), ("Income requirements", percorso)], script=MX_JS)


def pagina_mx_tasse():
    rel = "../../"
    percorso = f"{SEZ_MX}fees/"
    t1, t2, t3, t4, tp = (TASSE_MX[k][1] for k in ("1", "2", "3", "4", "pr"))
    visa_us = 56
    esempi = [("One person, temporary residence for 1 year", 1, t1), ("Couple, temporary residence for 1 year", 2, t1),
              ("One person, permanent residence", 1, tp), ("Couple, permanent residence", 2, tp)]
    righe_es = "".join(f'<tr><th scope="row">{a}</th><td class="n">{importo_mx(n * visa_us, "USD")}</td><td class="n">{mxn(n * c)}</td>'
                       f'<td class="n">≈ {circa_mx(n * c, "MXN", "USD")}</td></tr>' for a, n, c in esempi)
    tab_es = (f'<div class="tab compatta"><table id="t-esempi-mx"><caption class="sr">Examples of the total cost</caption><thead><tr><th scope="col">Example</th>'
              f'<th scope="col" class="n">Visa at a US consulate</th><th scope="col" class="n">Card at the INM</th><th scope="col" class="n">Card ≈ USD</th></tr></thead>'
              f'<tbody>{righe_es}</tbody></table></div>')
    domande = [
        ("How much is a Mexican temporary resident card in 2026?",
         f"{mxn(t1)} for up to one year, {mxn(t2)} for two years, {mxn(t3)} for three years and {mxn(t4)} for four years (Annex 4 of the {ANNO} Miscellaneous Tax Resolution)."),
        ("How much is a Mexican permanent resident card in 2026?", f"{mxn(tp)} (Annex 4 of the {ANNO} Miscellaneous Tax Resolution); amount in the law {mxn(TASSE_MX['pr'][0])}."),
        ("Why are the 2026 fees different from older guides?",
         f"A decree published in the Diario Oficial on 7 November 2025 set new amounts for the resident cards from 1 January {ANNO}, and Annex 4 of the {ANNO} Miscellaneous Tax Resolution lists them. Guides written before {ANNO} show the earlier amounts."),
        ("Can I pay less?",
         "The law gives 50% off the card to residents who show the INM that they are in Mexico for family unity, for a job offer from a registered employer, or invited by an organisation for unpaid activities."),
        ("How much is the visa at the consulate?",
         f"The law sets {mxn(TASSE_MX['visa'][1])} for an ordinary visa; consulates charge it in their currency: US$56 at each of the US consulates we read."),
    ]
    corpo = f"""<section class="hero">{h1_diviso(f"Mexico residency fees {ANNO}: temporary and permanent resident cards")}
<p class="lead">In {ANNO} a Mexican temporary resident card costs <strong>{mxn(t1)}</strong> for up to one year, {mxn(t2)} for two, {mxn(t3)} for three and {mxn(t4)} for four years, and a permanent resident card <strong>{mxn(tp)}</strong>, according to Annex 4 of the {ANNO} Miscellaneous Tax Resolution (Diario Oficial, 28 December 2025) read on {data_lunga(LETTO_MX)}. The visa at the consulate is a separate fee.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("coins")}<span>Mexico immigration fees {ANNO}</span><span>read on {data_lunga(LETTO_MX)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Temporary resident card, up to 1 year</span><span class="sr">: </span><strong>{mxn(t1)}</strong> ≈ {circa_mx(t1, "MXN", "USD")}</p>
<div class="kpi"><div><b>{mxn(t4)}</b><span>temporary, 4 years</span></div><div><b>{mxn(tp)}</b><span>permanent resident card</span></div><div><b>{mxn(TASSE_MX["cambio"][1])}</b><span>change of status, on top of the new card</span></div><div><b>50%</b><span>off for family unity, job offer or invitation</span></div></div>
{fonte_mx_p(("anexo4", "lfd"), f"≈ at ECB reference rates of {data_lunga(CAMBI['data'])}")}
</div></section>
{AVVISO_MX}
{AD}
<h2>All fees</h2>
<p>"You pay" is the rounded amount that Annex 4 lists for {ANNO} ("cuota con ajuste"); "amount in the law" is the figure written in the Ley Federal de Derechos. You pay in pesos in Mexico; the other currencies are only a guide.</p>
{pila(tabella_tasse_mx(dettaglio=True))}
{fonte_mx_p(("anexo4", "lfd", "decreto"), f"conversions at ECB reference rates of {data_lunga(CAMBI['data'])}")}
<h2>What a move costs in fees: examples</h2>
<p>The visa at a US consulate (US$56 per application on the pages we read) plus the card at the INM. The card fee is per card; the examples use the full fee (if a partner comes through family unity, the 50% reduction below may apply to that card).</p>
{tab_es}
<p class="fonte">Sources: Annex 4 of the {ANNO} Miscellaneous Tax Resolution and the pages of the US consulates in the <a href="../">consulate table</a>, read on {data_lunga(LETTO_MX)}.</p>
<h2>Renewals, changes and the 50% reduction</h2>
<ul class="testo"><li><strong>Renewal</strong>: renewing a temporary resident card costs the same fee as issuing it (Ley Federal de Derechos, art. 8).</li>
<li><strong>Change of status</strong> (for example from temporary to permanent): {mxn(TASSE_MX["cambio"][1])}, plus the fee of the new card (art. 9).</li>
<li><strong>Replacement</strong> of a lost or damaged card: {mxn(TASSE_MX["repos"][1])}.</li>
<li><strong>50% reduction</strong> (new from {ANNO}): temporary and permanent residents who show the INM that they are in Mexico for family unity, for a job offer from a registered employer, or invited by an organisation to take part in unpaid activities pay half.</li></ul>
{fonte_mx_p(("lfd", "decreto"))}
{box_assicurazione_mx(rel)}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>More on Mexico residency</h2>
{link_mx("../", "fees/")}"""
    titolo = f"Mexico residency fees {ANNO}: temporary and permanent card costs"
    descr = (f"Mexico residency fees {ANNO} (DOF): temporary resident card {mxn(t1)} (1 year) to {mxn(t4)} (4 years), permanent {mxn(tp)}, change of status "
             f"{mxn(TASSE_MX['cambio'][1])}, 50% reduction, visa fee.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande)], briciole=[("Mexico residency", SEZ_MX), (f"Fees {ANNO}", percorso)])


def pagina_mx_cons(C):
    rel = "../../"
    percorso = f"{SEZ_MX}{C['id']}/"
    v = C["valuta"]
    uff = ufficio_mx(C)
    tr_r, tr_s = C["tr"]["reddito"]["importo"], C["tr"]["saldo"]["importo"]
    appr = "approximately " if C.get("approssimato") else ""
    pr = C.get("pr")
    tassa = C.get("tassa")
    nome_uff = f"Mexican {uff} in {C['sede']}"
    fonte_tipo = "official PDF" if C["pagine"][0].get("formato") == "pdf" else "official visa page"
    citazioni = []
    for tipo, etich in (("tr", "Temporary residence"), ("pr", "Permanent residence")):
        for cosa, e2 in (("reddito", "income"), ("saldo", "savings")):
            x = C.get(tipo, {}).get(cosa)
            if x:
                citazioni.append((f"{etich}: {e2}", importo_mx(x["importo"], v), x["frammento"], x["p"]))
    if tassa:
        citazioni.append(("Visa fee", importo_mx(tassa["importo"], tassa["valuta"]), tassa["frammento"], tassa["p"]))
    for a in C.get("altre", []):
        citazioni.append(("Also on the page", "–", a["frammento"], a["p"]))
    righe_c = "".join(f'<tr><th scope="row">{a}</th><td class="n">{b}</td><td class="small">“{escape(c)}”</td><td>{link_cons_mx(C, p)}</td></tr>' for a, b, c, p in citazioni)
    tab_c = pila(f'<div class="tab compatta"><table id="t-cit-mx"><caption class="sr">What the official page says</caption><thead><tr><th scope="col">What</th>'
                 f'<th scope="col" class="n">Amount</th><th scope="col">Words on the official page</th><th scope="col">Page</th></tr></thead><tbody>{righe_c}</tbody></table></div>')
    pesos_r = pesos_uma(GIORNI_MX["tr"][0])
    if v == "MXN":
        confronto = (f"The {nome_uff} writes the amounts in pesos: {mxn(tr_r)} against {mxn(pesos_r)} from the guidelines ({intero(GIORNI_MX['tr'][0])} × MXN {UMA_MX}), "
                     f"{(tr_r / pesos_r - 1) * 100:.1f}% more; savings {mxn(tr_s)} against {mxn(pesos_uma(GIORNI_MX['tr'][1]))}, {(tr_s / pesos_uma(GIORNI_MX['tr'][1]) - 1) * 100:.1f}% more. "
                     "The page does not say how these amounts were calculated; it says that all amounts are calculated in Mexican pesos and that you can check the official exchange rate on the day of your appointment.")
    elif prima_uma_mx(C):
        confronto = (f"The {C['sede']} {uff}'s {'PDF' if fonte_tipo == 'official PDF' else 'page'} is dated {data_lunga(C['data_pagina'])}, before INEGI announced the {ANNO} UMA ({data_lunga(FMX['uma']['data'])}), "
                     f"and it does not say which UMA or exchange rate it uses. With the {ANNO} UMA the guidelines' amount is {mxn(pesos_r)} ({intero(GIORNI_MX['tr'][0])} × MXN {UMA_MX}), "
                     f"≈ {circa_mx(pesos_r, 'MXN', v)} at ECB rates of {data_lunga(CAMBI['data'])}, {'more' if conv_mx(pesos_r, 'MXN', v) > tr_r else 'less'} than the {importo_mx(tr_r, v)} on the page. "
                     f"Ask the {uff} which figure applies on the day of your appointment.")
    else:
        tasso = pesos_r / tr_r
        confronto = (f"The guidelines' {mxn(pesos_r)} ({intero(GIORNI_MX['tr'][0])} × MXN {UMA_MX}) divided by {importo_mx(tr_r, v)} gives a rate of about "
                     f"{tasso:.2f} pesos per {'pound' if v == 'GBP' else ('Canadian dollar' if v == 'CAD' else 'dollar')}: the {uff} converted the peso amount with its own rate when it updated the page "
                     f"({data_cons_mx(C)}). At ECB rates of {data_lunga(CAMBI['data'])} the peso amount is ≈ {circa_mx(pesos_r, 'MXN', v)}.")
    stessi = [X for X in CONS_MX if X["paese"] == C["paese"] and X["id"] != C["id"]]
    lead_pr = (f" For permanent residence it asks for a monthly pension of {importo_mx(pr['reddito']['importo'], v)} or savings of {importo_mx(pr['saldo']['importo'], v)}." if pr else "")
    domande = [
        (f"How much income do I need for Mexican temporary residency in {C['sede']}?",
         f"{appr.capitalize()}{importo_mx(tr_r, v)} a month after tax over the last six months, or an average balance of {appr}{importo_mx(tr_s, v)} over the last 12 months, "
         f"according to the {nome_uff} ({data_cons_mx(C)})."),
    ]
    if pr:
        domande.append((f"How much do I need for Mexican permanent residency in {C['sede']}?",
                        f"A monthly pension of {importo_mx(pr['reddito']['importo'], v)} over the last six months, or an average balance of {importo_mx(pr['saldo']['importo'], v)} over the last 12 months."))
    if tassa:
        domande.append((f"How much is the visa fee at the {uff} in {C['sede']}?",
                        f"{importo_mx(tassa['importo'], tassa['valuta'])} per application, as the {uff}'s page says. The resident card in Mexico is a separate fee: {mxn(TASSE_MX['1'][1])} for up to one year ({ANNO})."))
    domande.append(("Why is the figure different from other consulates?",
                    "The rule is in pesos (days of UMA). Each consulate converts it with its own exchange rate on the day it updates its page, so the same rule gives slightly different amounts."))
    corpo = f"""<section class="hero"><h1>Mexico residency at the {escape(uff)} in {escape(C["sede"])}: income and savings ({ANNO})</h1>
<p class="lead">The {escape(nome_uff)} asks for a net monthly income of {appr}<strong>{importo_mx(tr_r, v)}</strong> or savings of {appr}<strong>{importo_mx(tr_s, v)}</strong> for a temporary resident visa, according to its {fonte_tipo} ({data_cons_mx(C)}) read on {data_lunga(LETTO_MX)}.{lead_pr}{f" The visa application costs {importo_mx(tassa['importo'], tassa['valuta'])}." if tassa else ""}</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("passport")}<span>{escape(nome_uff)}</span><span>read on {data_lunga(LETTO_MX)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Temporary resident visa: income a month (last 6 months, after tax)</span><span class="sr">: </span><strong>{appr}{importo_mx(tr_r, v)}</strong></p>
<div class="kpi"><div><b>{appr}{importo_mx(tr_s, v)}</b><span>or savings (average balance, 12 months)</span></div><div><b>{importo_mx(pr["reddito"]["importo"], v) if pr else "–"}</b><span>{"permanent: pension a month" if pr else "permanent: not on the pages we read"}</span></div><div><b>{importo_mx(tassa["importo"], tassa["valuta"]) if tassa else "–"}</b><span>{"visa application fee" if tassa else "visa fee: not on the pages we read"}</span></div><div><b>{mxn(TASSE_MX["1"][1])}</b><span>resident card in Mexico, up to 1 year</span></div></div>
{fonte_cons_p(C)}
</div></section>
{AVVISO_MX}
{AD}
<h2>What the official page says</h2>
{tab_c}
{fonte_cons_p(C)}
<h2>How the figure compares with the rule in pesos</h2>
<p>{confronto}</p>
{fonte_mx_p(("lineamientos", "uma"))}
<h2>Check your income</h2>
{calc_mx("../", "MXN" if v == "MXN" else v)}
<h2>After the visa: the resident card</h2>
<p>The visa lets you enter Mexico once; within 30 days you apply for the resident card at the National Migration Institute (INM) and pay its fee in pesos: {mxn(TASSE_MX["1"][1])} for up to one year, {mxn(TASSE_MX["4"][1])} for four years, {mxn(TASSE_MX["pr"][1])} for a permanent card ({ANNO}). <a href="../fees/">All fees</a>.</p>
{fonte_mx_p(("anexo4",))}
{box_assicurazione_mx(rel)}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>{"Other Mexican consulates in " + escape(art(C["paese"])) if stessi else "Other Mexican consulates"}</h2>
{griglia_cons_mx("../", C["id"])}
<p><a href="../">All consulates and the {ANNO} fees</a> · <a href="../income-requirements/">Income requirements by consulate</a></p>"""
    t = f"Mexican {uff} in {C['sede']}: residency income requirements {ANNO}"
    if len(t) > 70:
        t = f"Mexican {uff} in {C['sede']}: residency income {ANNO}"
    descr = (f"Mexico temporary residency at the {uff} in {C['sede']}: {appr}{importo_mx(tr_r, v)} a month or {appr}{importo_mx(tr_s, v)} in savings"
             + (f"; permanent {importo_mx(pr['reddito']['importo'], v)} a month" if pr else "") + f" (official page, read {data_lunga(LETTO_MX)}).")
    pagina(percorso, t, descr, corpo, jsonld_extra=[ld_faq(domande)], briciole=[("Mexico residency", SEZ_MX), (C["sede"], percorso)], script=MX_JS)


def genera_mx():
    pagina_mx_indice()
    pagina_mx_reddito()
    pagina_mx_tasse()
    for C in CONS_MX:
        pagina_mx_cons(C)


def controlli_mx():
    import hashlib
    errori = []
    cont = {k: MX[k] for k in ("letture", "fonti", "consolati", "esclusi")}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != MX["impronta"]:
        errori.append("mexico: impronta del JSON diversa dal contenuto (file modificato a mano?)")
    if any(f.get("http") != 200 for f in FMX.values()):
        errori.append("mexico: fonte non letta (HTTP diverso da 200)")
    if not (8 <= len(CONS_MX) <= 15):
        errori.append(f"mexico: {len(CONS_MX)} consolati (attesi 8-15)")
    for C in CONS_MX:
        if C["valuta"] not in SIMBOLI_MX or (C["valuta"] != "EUR" and C["valuta"] not in CAMBI["tassi"]):
            errori.append(f"mexico: valuta {C['valuta']} senza cambio BCE ({C['id']})")
        if C["data_pagina"] and C["data_pagina"] < "2026-01-01":
            errori.append(f"mexico: pagina di {C['id']} prima del 2026")
    if URL_SW_MX and not URL_SW_MX.startswith("https://safetywing.com/"):
        errori.append("mexico: link SafetyWing non valido in dati/affiliati.json (_safetywing_mexico)")
    return errori


# ---------------------------------------------------------------- Study in Italy: soldi per il visto e borse DSU per gli studenti internazionali (31/10/2026)
# Dati: dati/studio_italia.json, scritto da raccolta/studio_italia.py (circolare MUR/MAECI 2026-2028, decreti MUR 175 e 176/2026, D.M. 176/2026,
# Poste Italiane, Polizia di Stato, Normattiva, Banca d'Italia, bandi 2026/27 di 9 enti). Ogni cifra viene da "letture" o da "enti" (valore + frammento).
# Il calcolatore (ISEE_JS) gira nel browser; verifica.py (controllo 22) lo confronta con un calcolo Python indipendente.
SI = json.loads((DATI / "studio_italia.json").read_text(encoding="utf-8"))
SEZ_IT = "study-in-italy/"
LIT = {k: v["valore"] for k, v in SI["letture"].items()}
FIT = SI["fonti"]
ENTI_IT = SI["enti"]
NON_LETTI_IT = SI["non_letti"]
POVERI_IT = SI["poveri"]
LETTO_IT = SI["letto_il"]
CAMBI_IT = SI["cambi_bdi"]["anni"]
_SWI = AFFILIATI.get("_safetywing_italia", {})
URL_SW_IT = _SWI.get("url", "")
# Paesi del menu del calcolatore: (nome inglese, nome nell'Allegato 1 del bando UNIMI o "")
# Gli altri Paesi dell'Allegato 1 (soprattutto UE ed EFTA) non hanno bisogno del visto: si scelgono come "Other country".
PAESI_ALL1_IT = {"Australia": "AUSTRALIA", "Bahrain": "BAHREIN", "Canada": "CANADA", "Chile": "CILE", "Hong Kong": "HONG KONG", "Israel": "ISRAELE",
                 "Japan": "GIAPPONE", "Kuwait": "KUWAIT", "New Zealand": "NUOVA ZELANDA", "Oman": "OMAN", "Panama": "PANAMA", "Qatar": "QATAR",
                 "Russia": "RUSSIA", "Saudi Arabia": "ARABIA SAUDITA", "Singapore": "SINGAPORE", "South Korea": "COREA DEL SUD", "Switzerland": "SVIZZERA",
                 "Taiwan": "TAIWAN", "United Arab Emirates": "EMIRATI ARABI UNITI", "United Kingdom": "REGNO UNITO", "United States": "STATI UNITI D' AMERICA",
                 "Uruguay": "URUGUAY", "Costa Rica": "COSTA RICA", "Trinidad and Tobago": "TRINIDAD E TOBAGO", "Norway": "NORVEGIA"}
ALTRI_PAESI_IT = ["Albania", "Algeria", "Argentina", "Armenia", "Azerbaijan", "Belarus", "Bolivia", "Bosnia and Herzegovina", "Brazil", "Cameroon", "China",
                  "Colombia", "Côte d'Ivoire", "Ecuador", "Egypt", "Georgia", "Ghana", "India", "Indonesia", "Iran", "Iraq", "Jordan", "Kazakhstan", "Kenya",
                  "Kosovo", "Kyrgyzstan", "Lebanon", "Libya", "Malaysia", "Mexico", "Moldova", "Mongolia", "Montenegro", "Morocco", "Nigeria", "North Macedonia",
                  "Pakistan", "Palestine", "Paraguay", "Peru", "Philippines", "Serbia", "South Africa", "Sri Lanka", "Tajikistan", "Thailand", "Tunisia",
                  "Turkey", "Turkmenistan", "Ukraine", "Uzbekistan", "Venezuela", "Vietnam", "Zimbabwe"]
NOMI_POVERI_IT = {"Democratic People's Republic of Korea": "North Korea", "Lao People's Democratic Republic": "Laos", "Syrian Arab Republic": "Syria",
                  "Democratic Republic of the Congo": "DR Congo"}
PAESI_IT = sorted(set(ALTRI_PAESI_IT) | set(PAESI_ALL1_IT) | {NOMI_POVERI_IT.get(p, p) for p in POVERI_IT})
POVERI_BREVI = [NOMI_POVERI_IT.get(p, p) for p in POVERI_IT]
VALUTE_IT = ["EUR"] + list(CAMBI_IT["2025"])
NOMI_VALUTE_IT = {"EUR": "euro", "USD": "US dollar", "GBP": "pound sterling", "INR": "Indian rupee", "PKR": "Pakistani rupee", "BDT": "Bangladeshi taka",
                  "NGN": "Nigerian naira", "IRR": "Iranian rial", "NPR": "Nepalese rupee", "LKR": "Sri Lankan rupee", "EGP": "Egyptian pound",
                  "TRY": "Turkish lira", "MAD": "Moroccan dirham", "GHS": "Ghanaian cedi", "KES": "Kenyan shilling", "ETB": "Ethiopian birr",
                  "CNY": "Chinese yuan", "VND": "Vietnamese dong", "IDR": "Indonesian rupiah", "PHP": "Philippine peso", "UZS": "Uzbek sum",
                  "KZT": "Kazakh tenge", "AZN": "Azerbaijani manat", "BRL": "Brazilian real", "MXN": "Mexican peso", "COP": "Colombian peso"}
VALUTA_PAESE_IT = {"India": "INR", "Pakistan": "PKR", "Bangladesh": "BDT", "Nigeria": "NGN", "Iran": "IRR", "Nepal": "NPR", "Sri Lanka": "LKR",
                   "Egypt": "EGP", "Turkey": "TRY", "Morocco": "MAD", "Ghana": "GHS", "Kenya": "KES", "Ethiopia": "ETB", "China": "CNY", "Vietnam": "VND",
                   "Indonesia": "IDR", "Philippines": "PHP", "Uzbekistan": "UZS", "Kazakhstan": "KZT", "Azerbaijan": "AZN", "Brazil": "BRL", "Mexico": "MXN",
                   "Colombia": "COP", "United States": "USD", "United Kingdom": "GBP"}


def eur(x):
    """€10,179.85 / €25,000."""
    x = float(x)
    return "€" + (f"{x:,.0f}" if x.is_integer() else f"{x:,.2f}")


def ent(i):
    return next(E for E in ENTI_IT if E["id"] == i)


def link_fonte_it(k, testo=None):
    f = FIT[k]
    return f'<a href="{escape(f["url"])}" rel="noopener">{escape(testo or (f["editore"] + ", " + f["titolo"]))}</a>'


def fonte_it_p(chiavi=(), extra=""):
    voci = [link_fonte_it(k) for k in chiavi]
    return (f'<p class="fonte">Source{"s" if len(voci) + bool(extra) > 1 else ""}: {"; ".join(voci)}{("; " if voci and extra else "") + extra}. '
            f'Read on {data_lunga(LETTO_IT)}.</p>')


def data_bando(E):
    f = FIT[E["fonti"][0]]
    return f"PDF dated {data_lunga(f['data'])}" if f.get("data") else "official PDF"


def scad_testo(E, breve=False):
    s = E["scadenza"]
    t = data_lunga(s["valore"]) + (f", {s['ora']} Italian time" if s.get("ora") and not breve else "")
    return t


def metodo_testo(E):
    if E["metodo"] == "caf":
        if E["id"] == "ersu-palermo":
            return "an ISEE parificato calculated by an Italian CAF (tax assistance centre)"
        if E["id"] == "ersu-catania":
            return "an ISEE parificato from the CAF chosen by ERSU Catania"
        if E["id"] == "adisu-campania":
            return "an ISEE parificato filled in at a CAF (tax assistance centre)"
        return "an ISEE parificato from the CAF (tax assistance centre) that has an agreement with the " + ("university" if E["id"] in ("politecnico-di-milano", "university-of-padua") else "agency")
    if E.get("allegato1"):
        return "documents only from the countries in Annex 1 of the call; everyone else is placed in the first income band"
    return "legalised and translated documents sent to the agency, which calculates the indicator"


def fs_testo(E):
    """Borsa massima per fuori sede, con quello che comprende (pasti, alloggio) se il bando lo scrive."""
    fs = E["fs"]["valore"]
    sv = E.get("servizi")
    if E["id"] == "dsu-toscana":
        return f"{eur(fs)} in cash plus a free room and two free meals a day (valued at {eur(sv['alloggio'])} and {eur(sv['mensa'])})"
    if E["id"] == "disco-lazio":
        return f"{eur(fs)} plus two free meals a day (valued at {eur(sv['mensa'])})"
    if E["id"] in ("university-of-milan", "politecnico-di-milano"):
        return f"{eur(fs)} plus one free meal a day ({eur(fs + sv['mensa'])} in all)"
    if E["id"] == "er-go":
        return f"{eur(fs)}, part of which can be taken as meals"
    if E["id"] == "university-of-padua":
        return f"{eur(fs)}, part of it paid as one meal a day (and as rent if you live in an ESU residence)"
    if E["id"] == "adisu-campania":
        return f"{eur(fs)}, 15% more if your ISEE is at most half of the {eur(E['isee']['valore'])} limit"
    return eur(fs)


def stato_scad(d):
    return '<span class="stato sospesa">Closed</span>' if d < LETTO_IT else '<span class="stato vigore">Open</span>'


AVVISO_IT = ('<p class="avviso"><strong>Not legal or immigration advice.</strong> This page reports what the Italian ministries and the regional '
             'scholarship calls said on the date we read them. The consulate decides on your visa, and the agency or university decides on your '
             'scholarship after checking your documents. Always read the official call before you apply.</p>')


# ---------- calcolatore ISEE / ISPE parificato (stima prudente)
K_IT = {"enti": [{"id": E["id"], "nome": E["nome"], "isee": E["isee"]["valore"], "ispe": E["ispe"]["valore"], "fs": E["fs"]["valore"], "fs_isee": E["fs"]["fino_isee"]}
                 for E in ENTI_IT],
        "scala": LIT["scala"], "mq": 500, "quota": 0.2, "cambi": CAMBI_IT, "poveri": POVERI_BREVI, "unimi": sorted(PAESI_ALL1_IT)}

ISEE_JS = r"""
(function(){
function r2(x){return Math.round(x*100)/100;}
function scala(n,s){if(n<=5)return s[String(n)];return r2(s['5']+(n-5)*s.oltre);}
function num(v){if(v===''||v===null||v===undefined)return 0;var x=+v;return x>=0?x:NaN;}
var C={isee:function(i,k){
 var n=Math.floor(+i.n);if(!(n>=1&&n<=20))return null;if(i.reddito===''||i.reddito===null||i.reddito===undefined)return null;
 var red=num(i.reddito),ris=num(i.risparmi),mq=num(i.mq),mut=num(i.mutuo);if(isNaN(red)||isNaN(ris)||isNaN(mq)||isNaN(mut))return null;
 var t=i.val==='EUR'?1:(k.cambi[i.anno]||{})[i.val];if(!t)return null;
 var isr=r2(red/t),mob=r2(ris/t),imm=r2(Math.max(0,mq*k.mq-r2(mut/t))),isp=r2(mob+imm),ise=r2(isr+k.quota*isp),sc=scala(n,k.scala);
 var isee=r2(ise/sc),ispe=r2(isp/sc);
 var righe=k.enti.map(function(e){var a=isee<=e.isee,b=ispe<=e.ispe;return {id:e.id,ok_isee:a,ok_ispe:b,ok:a&&b,top:(a&&b&&isee<=e.fs_isee)};});
 return {t:t,isr:isr,mob:mob,imm:imm,isp:isp,ise:ise,scala:sc,isee:isee,ispe:ispe,righe:righe,
  povero:k.poveri.indexOf(i.paese)>=0,unimi_auto:(i.paese!==''&&i.paese!=='other'&&k.unimi.indexOf(i.paese)<0)};}};
window.CALC_IT=C;
function fmt(x){var d=Math.abs(x-Math.round(x))<1e-9?0:2;return '€'+x.toFixed(d).replace(/\B(?=(\d{3})+(?!\d))/g,',');}
function nome(k,id){for(var j=0;j<k.enti.length;j++)if(k.enti[j].id===id)return k.enti[j];return null;}
document.querySelectorAll('[data-isee]').forEach(function(box){var k=JSON.parse(box.getAttribute('data-k'));var f=box.querySelector('form');var out=box.querySelector('[data-out]');
 var rel=box.getAttribute('data-rel')||'';var primo=box.getAttribute('data-primo')||'';var V=JSON.parse(box.getAttribute('data-v')||'{}');var ultimoPaese='';
 function go(){try{
  if(f.paese.value!==ultimoPaese){ultimoPaese=f.paese.value;if(V[ultimoPaese])f.valuta.value=V[ultimoPaese];}
  var r=C.isee({n:f.n.value,val:f.valuta.value,anno:f.anno.value,reddito:f.reddito.value,risparmi:f.risparmi.value,mq:f.mq.value,mutuo:f.mutuo.value,paese:f.paese.value},k);
  if(!r){out.innerHTML='<p class="small">Type your family\'s total gross income for the year to see an estimate.</p>';return;}
  var h='';
  if(r.povero)h+='<p class="it-nota"><b>Particularly poor country.</b> For students whose family lives in '+f.paese.value+', the calls ask for a certificate from the Italian embassy that you do not belong to a well-known high-income family, in place of the income calculation (check your call).</p>';
  h+='<p class="r-lab">Estimated ISEE (prudent)</p><p class="tot">'+fmt(r.isee)+'</p><p class="r-anno">ISPE (assets) '+fmt(r.ispe)+' · scale '+r.scala.toFixed(2)+' for '+f.n.value+' '+(+f.n.value===1?'person':'people')+'</p><ul class="r-righe">';
  var rr=r.righe.slice();if(primo)rr.sort(function(a,b){return (b.id===primo)-(a.id===primo);});
  rr.forEach(function(x){var e=nome(k,x.id);var lab=x.ok?'✓ Within both limits':(!x.ok_isee&&!x.ok_ispe?'✗ Above both limits':(!x.ok_isee?'✗ Above the ISEE limit':'✗ Above the ISPE limit'));
   h+='<li class="'+(x.ok?'it-ok':'it-no')+'"><span class="r-lab">'+lab+' · <a href="'+rel+e.id+'/">'+e.nome+'</a></span><b>ISEE up to '+fmt(e.isee)+' · ISPE up to '+fmt(e.ispe)+'</b>'+
    '<span class="small">'+(x.top?'Your estimate is in the band for the '+fmt(e.fs)+' off-campus amount (ISEE up to '+fmt(e.fs_isee)+').':(x.ok?'Within the limits, above the '+fmt(e.fs)+' band (ISEE up to '+fmt(e.fs_isee)+'): a smaller amount.':''))+
    (x.id==='university-of-milan'&&r.unimi_auto?' At this university, students from countries outside Annex 1 of the call are placed in the first band without the calculation.':'')+'</span></li>';});
  h+='</ul><p class="small" style="margin-top:10px">Income '+fmt(r.isr)+' + 20% of assets ('+fmt(r.mob)+' savings + '+fmt(r.imm)+' buildings) = '+fmt(r.ise)+', divided by '+r.scala.toFixed(2)+'. '+
   (f.valuta.value==='EUR'?'':'Converted at '+r.t+' '+f.valuta.value+' per euro, the Bank of Italy average for '+f.anno.value+'. ')+
   'An estimate: the CAF or the agency calculates the official figure from your documents. The deductions we leave out can only lower it; a different exchange rate or income we have not counted can raise it.</p>';
  out.innerHTML=h;}catch(e){out.innerHTML='';}}
 f.addEventListener('input',go);f.addEventListener('change',go);f.addEventListener('submit',function(e){e.preventDefault();go();});go();});
})();
"""
CSS += (".r-righe li.it-ok{border-color:var(--ok)}.r-righe li.it-ok .r-lab{color:var(--ok)}.r-righe li.it-no .r-lab{color:var(--no)}"
        ".r-righe li .r-lab a{color:inherit}.it-nota{background:var(--warn-2);border-radius:var(--r-s);padding:9px 12px;font-size:.92rem;margin:0 0 12px}"
        ".formula-it{font-family:var(--serif);font-size:1.05rem;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:12px 14px;overflow-wrap:anywhere}")


def calc_it(rel_sez, primo=""):
    opz_p = ('<option value="">Choose a country</option>' + "".join(f'<option value="{escape(p)}">{escape(p)}</option>' for p in PAESI_IT)
             + '<option value="other">Other country</option>')
    opz_v = "".join(f'<option value="{v}"{" selected" if v == "EUR" else ""}>{v} – {NOMI_VALUTE_IT[v]}</option>' for v in VALUTE_IT)
    campi = (f'<label class="pieno"><span class="lt">{ico("globe")}Where your family lives</span><select name="paese">{opz_p}</select></label>'
             f'<label><span class="lt">{ico("family")}People in the family</span><input type="number" name="n" min="1" max="20" step="1" value="4" inputmode="numeric"></label>'
             f'<label><span class="lt">{ico("calendar")}Income year</span><select name="anno"><option value="2025" selected>2025</option><option value="2024">2024</option></select></label>'
             f'<label class="pieno"><span class="lt">{ico("exchange")}Currency</span><select name="valuta">{opz_v}</select></label>'
             f'<label class="pieno"><span class="lt">{ico("wallet")}Total gross income of the family in that year</span><input type="number" name="reddito" min="0" step="any" placeholder="e.g. 18000" inputmode="decimal"></label>'
             f'<label><span class="lt">{ico("coins")}Savings and investments (31 Dec)</span><input type="number" name="risparmi" min="0" step="any" placeholder="0" inputmode="decimal"></label>'
             f'<label><span class="lt">{ico("list")}Buildings owned (m², all)</span><input type="number" name="mq" min="0" step="any" placeholder="e.g. 120" inputmode="decimal"></label>'
             f'<label class="pieno"><span class="lt">{ico("list")}Mortgage still owed (same currency)</span><input type="number" name="mutuo" min="0" step="any" placeholder="0" inputmode="decimal"></label>')
    nota = (f'Prudent estimate with the formula in the calls: income plus 20% of assets (savings plus buildings at {eur(500)} per m²), divided by the '
            f'equivalence scale of DPCM 159/2013. We leave out the allowances and scale increases that can only lower the result. Currencies are converted '
            f'at the Bank of Italy annual average, as the calls ask. Nothing you type leaves your browser.')
    return (f'<section class="card calc" data-isee data-rel="{rel_sez}" data-primo="{primo}" data-v=\'{json.dumps(VALUTA_PAESE_IT, separators=(",", ":"))}\' '
            f'data-k=\'{json.dumps(K_IT, separators=(",", ":"), ensure_ascii=False).replace(chr(39), "&#39;")}\' aria-label="ISEE parificato estimate">'
            f'<div class="calc-grid"><form autocomplete="off"><h2 style="margin:0 0 14px;font-size:1.2rem">{ico("calc")} Estimate your ISEE parificato</h2>'
            f'<div class="campi">{campi}</div><p class="small" style="margin:12px 0 0">{nota}</p></form>'
            f'<div class="calc-out"><div class="risultato" data-out aria-live="polite"><noscript>Turn on JavaScript to use the estimate; the limits are in the table below.</noscript></div></div></div></section>')


# ---------- tabelle e blocchi comuni
def tabella_enti_it(rel_sez):
    righe = ""
    for E in sorted(ENTI_IT, key=lambda E: -E["fs"]["valore"] - (E.get("servizi", {}).get("valore", 0) if E["id"] in ("dsu-toscana", "disco-lazio") else 0)):
        righe += (f'<tr><th scope="row"><a href="{rel_sez}{E["id"]}/">{escape(E["nome"])}</a><span class="small"><br>{escape(", ".join(E["citta"][:3]))}</span></th>'
                  f'<td class="n">{eur(E["isee"]["valore"])}</td><td class="n">{eur(E["ispe"]["valore"])}</td><td>{fs_testo(E)} <span class="small">(ISEE up to {eur(E["fs"]["fino_isee"])})</span></td>'
                  f'<td>{scad_testo(E, True)} {stato_scad(E["scadenza"]["valore"])}</td><td class="small">{escape(metodo_testo(E))}</td>'
                  f'<td><a href="{escape(FIT[E["fonti"][0]]["url"])}" rel="noopener">call</a> <span class="small">({data_bando(E)})</span></td></tr>')
    tab = (f'<div class="tab compatta"><table id="t-enti-it"><caption class="sr">DSU scholarships 2026/27 for international students by agency</caption><thead><tr>'
           f'<th scope="col">Agency or university</th><th scope="col" class="n">ISEE limit</th><th scope="col" class="n">ISPE limit</th><th scope="col">Off-campus amount (top band)</th>'
           f'<th scope="col">2026/27 deadline</th><th scope="col">Income abroad</th><th scope="col">Official call</th></tr></thead><tbody>{righe}</tbody></table></div>')
    return pila(tab)


def non_letti_it():
    voci = "".join(f'<li><a href="{escape(x["url"])}" rel="noopener">{escape(x["nome"])}</a>: {escape(x["motivo"])}.</li>' for x in NON_LETTI_IT)
    return (f'<h2 id="not-covered">Agencies we could not read</h2><p class="small">We searched for these 2026/27 calls on {data_lunga(LETTO_IT)} and publish no figures '
            f'for them until we can read the official call:</p><ul class="testo small">{voci}</ul>')


def griglia_enti_it(rel_sez, escludi=""):
    return ('<div class="griglia">' + "".join(
        f'<a href="{rel_sez}{E["id"]}/"><span class="ic">{ico("coins")}</span><span>{escape(E["nome"])}<small>{escape(E["regione"])} · up to {eur(E["fs"]["valore"])}'
        f'{" + room and meals" if E["id"] == "dsu-toscana" else (" + meals" if E["id"] in ("disco-lazio", "university-of-milan", "politecnico-di-milano") else "")} · ISEE {eur(E["isee"]["valore"])}</small></span></a>'
        for E in ENTI_IT if E["id"] != escludi) + "</div>")


PAGINE_TEMA_IT = [("student-visa-funds/", "Student visa funds: €10,179.85 a year", "wallet"), ("isee-parificato/", "ISEE parificato: formula, documents, calculator", "calc"),
                  ("dsu-scholarship-deadlines/", "DSU deadlines and amounts by region", "calendar"), ("particularly-poor-countries/", "Particularly poor countries list", "globe"),
                  ("health-insurance/", "Health cover: SSN €700 or a policy", "shield")]


def link_tema_it(rel_sez, escludi=""):
    voci = [("", "Study in Italy: overview", "passport")] + PAGINE_TEMA_IT
    return ('<div class="griglia">' + "".join(f'<a href="{rel_sez}{p}"><span class="ic">{ico(i)}</span><span>{t}</span></a>' for p, t, i in voci if p != escludi) + "</div>")


def costi_permesso_it():
    base = LIT["ps_marca"] + LIT["ps_poste"] + LIT["ps_documento"]
    righe = [("Revenue stamp (marca da bollo) on the form", LIT["ps_marca"], "poste"), ("Fee paid at the post office counter", LIT["ps_poste"], "poste"),
             ("Electronic permit card (postal payment slip)", LIT["ps_documento"], "poste"),
             ("Contribution, permit of more than 3 months and up to 1 year", LIT["ps_contributo_1"], "polizia"),
             ("Contribution, permit of more than 1 year and up to 2 years (instead of the line above)", LIT["ps_contributo_2"], "polizia")]
    corpo = "".join(f'<tr><th scope="row">{a}</th><td class="n">{eur(v)}</td><td class="small">{escape(FIT[k]["editore"])}</td></tr>' for a, v, k in righe)
    corpo += (f'<tr><th scope="row"><strong>Total, permit up to 1 year</strong></th><td class="n"><strong>{eur(round(base + LIT["ps_contributo_1"], 2))}</strong></td><td class="small">sum</td></tr>'
              f'<tr><th scope="row"><strong>Total, permit of 1 to 2 years</strong></th><td class="n"><strong>{eur(round(base + LIT["ps_contributo_2"], 2))}</strong></td><td class="small">sum</td></tr>')
    return (f'<div class="tab compatta"><table id="t-permesso-it"><caption class="sr">Cost of a study residence permit in Italy</caption><thead><tr><th scope="col">What you pay</th>'
            f'<th scope="col" class="n">Amount</th><th scope="col">Source</th></tr></thead><tbody>{corpo}</tbody></table></div>')


def mezzi_valute_it():
    """10.179,85 € nelle valute più usate: cambi BCE di riserva (dati/cambi.json) dove la BCE pubblica la valuta, media 2025 della Banca d'Italia per le altre."""
    righe = ""
    for v in ("USD", "GBP", "INR", "CNY", "TRY", "IDR", "PHP", "BRL", "MXN", "PKR", "BDT", "NGN", "IRR", "NPR", "LKR", "EGP", "GHS", "KES", "MAD", "VND", "UZS"):
        if v in CAMBI["tassi"]:
            t, fonte = CAMBI["tassi"][v], f'ECB, {data_lunga(CAMBI["data"])}'
        else:
            t, fonte = CAMBI_IT["2025"][v], "Bank of Italy, 2025 average"
        x = LIT["mezzi"] * t
        righe += f'<tr><th scope="row">{v} <span class="small">({NOMI_VALUTE_IT[v]})</span></th><td class="n">{x:,.0f}</td><td class="n small">{t:,.4f}</td><td class="small">{fonte}</td></tr>'
    return pila(f'<div class="tab compatta"><table id="t-mezzi-it"><caption class="sr">Italian student visa funds in other currencies</caption><thead><tr><th scope="col">Currency</th>'
                f'<th scope="col" class="n">{eur(LIT["mezzi"])} is about</th><th scope="col" class="n">Rate (per euro)</th><th scope="col">Rate source</th></tr></thead><tbody>{righe}</tbody></table></div>')


def tabella_scala_it():
    s = LIT["scala"]
    righe = "".join(f'<tr><th scope="row">{n}</th><td class="n">{s[str(n)]:.2f}</td></tr>' for n in range(1, 6))
    righe += f'<tr><th scope="row">each extra person</th><td class="n">+{s["oltre"]:.2f}</td></tr>'
    return (f'<div class="tab compatta"><table id="t-scala-it"><caption class="sr">ISEE equivalence scale</caption><thead><tr><th scope="col">People in the family</th>'
            f'<th scope="col" class="n">Scale</th></tr></thead><tbody>{righe}</tbody></table></div>')


def esempio_isee_it():
    """Esempio: famiglia di 4, reddito 2025 di 1.500.000 PKR, risparmi 600.000 PKR, casa di 120 m²."""
    t = CAMBI_IT["2025"]["PKR"]
    red, ris, mq = 1500000, 600000, 120
    isr, mob = _r2_it(red / t), _r2_it(ris / t)
    imm = _r2_it(max(0, mq * 500 - 0))
    isp = _r2_it(mob + imm)
    ise = _r2_it(isr + 0.2 * isp)
    sc = LIT["scala"]["4"]
    return {"t": t, "red": red, "ris": ris, "mq": mq, "isr": isr, "mob": mob, "imm": imm, "isp": isp, "ise": ise, "sc": sc,
            "isee": _r2_it(ise / sc), "ispe": _r2_it(isp / sc)}


def _r2_it(x):
    return math.floor(x * 100 + 0.5) / 100


def box_assicurazione_it(rel):
    if not URL_SW_IT:
        return ""
    return (f'<section class="card aff-r" aria-labelledby="aff-i-h"><div class="aff-r-t"><span class="ic">{ico("shield")}</span>'
            f'<h2 id="aff-i-h">Travel medical cover before the SSN</h2><span class="aff-tag">Affiliate</span></div>'
            f'<p>The official routes are the ones above: voluntary registration with the National Health Service (at least {eur(LIT["ssn_minimo"])} a year) '
            f'or a policy with no limits on urgent hospital care for your whole stay. SafetyWing sells travel medical insurance online; if you want cover for '
            f'the journey, compare policies before you go. We have not checked whether a police headquarters (Questura) accepts it for the residence '
            f'permit, so ask before you rely on it.</p>'
            f'<p class="aff-r-cta"><a class="btn" href="{escape(URL_SW_IT)}" rel="sponsored noopener" target="_blank">See SafetyWing travel medical insurance{ico("arrow")}'
            f'<span class="sr"> (opens in a new tab)</span></a></p>'
            f'<p class="small">{MON.RIGA_EN} Insurance from us or anyone else does not change the decision on your visa or permit; SSN registration is the official route.</p></section>')


def domande_comuni_it():
    return [
        ("How much money do I need for an Italian student visa in 2026/27?",
         f"{eur(LIT['mezzi'])} a year, according to the procedures of the Ministry of University and Research and the Foreign Ministry valid for 2026/27 and "
         "2027/28. The money must come from legal, traceable sources, preferably your own or your family's."),
        ("Does a DSU scholarship count as proof of funds for the visa?",
         "Only when it has been awarded. The procedures say that applying for, or being eligible for, a regional scholarship does not count without an explicit "
         "certificate that the scholarship was assigned to you."),
        ("What are the ISEE and ISPE limits for DSU scholarships in 2026/27?",
         f"The national maximum is {eur(LIT['isee_max'])} for the ISEE and {eur(LIT['ispe_max'])} for the ISPE (MUR Directorial Decree 176 of 10 February 2026); "
         f"each region can set lower limits, from {eur(min(E['isee']['valore'] for E in ENTI_IT))} in the calls we read."),
        ("How much is the DSU scholarship for off-campus students?",
         f"The Ministry's minimum for 2026/27 is {eur(LIT['dsu_fs'])} a year (MUR Directorial Decree 175 of 10 February 2026), paid in full when the ISEE is up to "
         f"two thirds of the agency's limit and reduced above that, down to half. Most calls add 15% for the lowest incomes: "
         f"{eur(max(E['fs']['valore'] for E in ENTI_IT))} at the agencies that pay it in cash. Some agencies pay part of it as free meals or a room."),
    ]


# ---------- pagine
def pagina_it_indice():
    rel = "../"
    percorso = SEZ_IT
    domande = domande_comuni_it() + [
        ("What is the ISEE parificato?",
         "The economic indicator that replaces the Italian ISEE when your family's income and assets are abroad. It adds up the family's income and 20% of its "
         "assets, then divides by a scale that depends on the number of people. A CAF or the agency calculates it from official documents from your country."),
        ("When do the DSU calls for 2027/28 open?",
         f"We do not know yet. The 2026/27 calls we read opened between {data_lunga(min(E['scadenza']['aperta_dal'] for E in ENTI_IT if E['scadenza'].get('aperta_dal')))} "
         f"and {data_lunga(max(E['scadenza']['aperta_dal'] for E in ENTI_IT if E['scadenza'].get('aperta_dal')))} and closed between "
         f"{data_lunga(min(E['scadenza']['valore'] for E in ENTI_IT))} and {data_lunga(max(E['scadenza']['valore'] for E in ENTI_IT))}. Watch your agency's website from June 2027."),
    ]
    ld = [ld_faq(domande), ld_dataset("DSU scholarships 2026/27 for international students in Italy",
                                      f"ISEE and ISPE limits, off-campus amounts, deadlines and rules for income abroad from the 2026/27 calls of {len(ENTI_IT)} Italian right-to-study agencies and universities.",
                                      percorso, [FIT["circolare"]["url"], FIT["dd175"]["url"], FIT["dd176"]["url"]] + [FIT[E["fonti"][0]]["url"] for E in ENTI_IT],
                                      "2026/2027", "https://creativecommons.org/licenses/by/4.0/")]
    fs_max = max(E["fs"]["valore"] for E in ENTI_IT)
    corpo = f"""<section class="hero">{h1_diviso("Study in Italy 2026/27: visa funds, DSU scholarships and ISEE parificato")}
<p class="lead">To get an Italian student visa for 2026/27 you must show <strong>{eur(LIT["mezzi"])}</strong> a year, according to the procedures of the Ministry of University and Research and the Foreign Ministry read on {data_lunga(LETTO_IT)}. The Ministry's minimum DSU scholarship for an off-campus student is <strong>{eur(LIT["dsu_fs"])}</strong> (up to {eur(fs_max)} for the lowest incomes, less as the ISEE nears the limit) if the family's ISEE stays under {eur(LIT["isee_max"])} or a lower regional limit.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("passport")}<span>Study in Italy</span><span>read on {data_lunga(LETTO_IT)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Funds for the student visa, a year</span><span class="sr">: </span><strong>{eur(LIT["mezzi"])}</strong></p>
<div class="kpi"><div><b>{eur(LIT["dsu_fs"])}</b><span>minimum DSU scholarship, off-campus student</span></div><div><b>{eur(LIT["isee_max"])}</b><span>highest ISEE limit allowed</span></div><div><b>{eur(LIT["ispe_max"])}</b><span>highest ISPE limit allowed</span></div><div><b>{data_lunga(LIT["visto_scadenza"])}</b><span>last day for visa applications, 2026/27 bachelor's and master's degree courses</span></div></div>
{fonte_it_p(("circolare", "dd175", "dd176"))}
</div></section>
{AVVISO_IT}
{AD}
{calc_it("")}
<h2 id="agencies">DSU scholarships 2026/27 by agency</h2>
<p class="small">One row per call we read on {data_lunga(LETTO_IT)}. You need both indicators under the limit. "Off-campus" (fuori sede) is the rate for students who rent near the university; students whose family lives abroad generally count as off-campus when they pay rent near the university for the period the call requires. All the 2026/27 application windows have closed.</p>
{tabella_enti_it("")}
<p class="fonte">Source: the official call linked in each row, read on {data_lunga(LETTO_IT)}. Amounts are for the general case in the first year: STEM courses for women, students with disabilities and later years have other amounts in the calls.</p>
<h2 id="visa">The visa: money, deadline and permit</h2>
<p>The procedures for 2026/27 and 2027/28 set the funds at {eur(LIT["mezzi"])} a year, from legal and traceable sources, preferably your own or a relative's up to the fourth degree. A DSU scholarship counts only once it has been awarded. For bachelor's and master's degree courses (laurea, laurea magistrale, single-cycle) and AFAM academic diplomas, the visa application must reach the consulate by {data_lunga(LIT["visto_scadenza"])} (for 2027/28, by {data_lunga(LIT["visto_scadenza_27"])}); universities can set an earlier date, and other courses (university Master, PhD, Erasmus, single courses, foundation) have no fixed date but not after classes start. Within {LIT["permesso_giorni"]} working days of arrival you apply for the residence permit, which costs {eur(round(LIT["ps_marca"] + LIT["ps_poste"] + LIT["ps_documento"] + LIT["ps_contributo_1"], 2))} for up to one year.</p>
{fonte_it_p(("circolare", "poste", "polizia"))}
<p><a href="student-visa-funds/">Visa funds in your currency and the permit costs</a> · <a href="health-insurance/">Health insurance: SSN or a policy</a></p>
<h2 id="isee">Income abroad: the ISEE parificato</h2>
<p>If your family lives abroad you cannot get a normal Italian ISEE. The calls use an "ISEE parificato": the family's income plus 20% of its assets (savings, and buildings counted at {eur(500)} per square metre), divided by the equivalence scale (2.46 for a family of four). Some agencies want it from a CAF they have an agreement with; others calculate it themselves from your documents. In most calls, students from the {len(POVERI_IT)} countries on the Ministry's "particularly poor" list (Bangladesh and Nepal among them) bring a certificate from the Italian embassy instead.</p>
{fonte_it_p(("scala", "dm176"))}
<p><a href="isee-parificato/">ISEE parificato: formula, documents and who calculates it</a> · <a href="particularly-poor-countries/">Particularly poor countries 2026/27</a> · <a href="dsu-scholarship-deadlines/">Deadlines and amounts by region</a></p>
{non_letti_it()}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>Agency pages</h2>
{griglia_enti_it("")}
<h2>More on studying in Italy</h2>
{link_tema_it("", "")}
<p><a href="{rel}italy-digital-nomad-visa/">Italy digital nomad visa income</a> · <a href="{rel}{SEZ_GRAD}">UK Graduate visa</a> · <a href="{rel}{SEZ_OPT}">US OPT</a> · <a href="{rel}{SEZ}">Schengen visa refusal rates</a></p>"""
    titolo = "Study in Italy 2026/27: visa funds, DSU scholarships and ISEE"
    descr = (f"Italian student visa 2026/27: {eur(LIT['mezzi'])} a year. DSU scholarships from {eur(LIT['dsu_fs'])} for off-campus students, ISEE and ISPE limits "
             f"of {len(ENTI_IT)} agencies, deadlines and an ISEE parificato estimate.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=ld, briciole=[("Study in Italy", percorso)], script=ISEE_JS)


def pagina_it_mezzi():
    rel = "../../"
    percorso = f"{SEZ_IT}student-visa-funds/"
    base = LIT["ps_marca"] + LIT["ps_poste"] + LIT["ps_documento"]
    domande = domande_comuni_it()[:2] + [
        ("Can my parents' bank account be used for the Italian student visa?",
         "The procedures prefer funds in your own name but accept funds made available by your family, up to relatives of the fourth degree. The consulate "
         "checks where the money comes from and whether it fits your family's income and assets."),
        ("How much does the Italian residence permit for study cost?",
         f"{eur(round(base + LIT['ps_contributo_1'], 2))} for a permit of up to one year: a {eur(LIT['ps_marca'])} revenue stamp, {eur(LIT['ps_poste'])} at the post office, "
         f"{eur(LIT['ps_documento'])} for the card and a {eur(LIT['ps_contributo_1'])} contribution ({eur(LIT['ps_contributo_2'])} for 1 to 2 years)."),
        ("When must I apply for the residence permit?",
         f"Within {LIT['permesso_giorni']} working days of arriving in Italy, through the post office or the university's desk. Renew it at least "
         f"{LIT['rinnovo_giorni']} days before it expires."),
    ]
    corpo = f"""<section class="hero"><h1>Italy student visa bank balance 2026/27: {eur(LIT["mezzi"])} a year</h1>
<p class="lead">The Italian student visa for 2026/27 asks for <strong>{eur(LIT["mezzi"])}</strong> a year of means of support, according to the Ministry of University and Research and Foreign Ministry procedures (published on Universitaly, PDF dated {data_lunga(FIT["circolare"]["data"])}) read on {data_lunga(LETTO_IT)}. The same amount applies to 2027/28. For 2026/27 bachelor's and master's degree courses (laurea, laurea magistrale, single-cycle) and AFAM academic diplomas, the visa application must reach the consulate by {data_lunga(LIT["visto_scadenza"])}, or by an earlier date your university sets; other courses (university Master, PhD, Erasmus, single courses, foundation) have no fixed date but not after classes start.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("wallet")}<span>Student visa (type D)</span><span>read on {data_lunga(LETTO_IT)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Means of support, a year</span><span class="sr">: </span><strong>{eur(LIT["mezzi"])}</strong></p>
<div class="kpi"><div><b>{data_lunga(LIT["visto_scadenza"])}</b><span>visa deadline, 2026/27 bachelor's and master's degree courses</span></div><div><b>{LIT["permesso_giorni"]} working days</b><span>to apply for the residence permit after arrival</span></div><div><b>{eur(round(base + LIT["ps_contributo_1"], 2))}</b><span>residence permit up to 1 year</span></div><div><b>{eur(LIT["ssn_minimo"])}</b><span>minimum SSN registration a year</span></div></div>
{fonte_it_p(("circolare",))}
</div></section>
{AVVISO_IT}
{AD}
<h2>What the procedures say about the money</h2>
<ul class="testo"><li>“{escape(SI["letture"]["mezzi"]["frammento"])}”: {eur(LIT["mezzi"])} a year.</li>
<li>The money must be legal and traceable, preferably yours or made available by your family (relatives up to the fourth degree). Where your country allows it, an account in your name with recurring or locked funds is preferred.</li>
<li>The consulate checks where the funds come from, the account's movements and whether they fit your family's income and assets.</li>
<li>Funds can also come from Italian institutions, universities, governments or foreign institutions the embassy considers reliable. A DSU scholarship counts only with a certificate that it has been awarded: “{escape(SI["letture"]["mezzi_borsa"]["frammento"])}”.</li>
<li>You also need housing in Italy; being eligible for a university residence place is not enough.</li></ul>
{fonte_it_p(("circolare",))}
<p class="small">The procedures give a yearly amount only. Some consulates write it as a monthly amount on their own pages: check the page of the consulate where you apply.</p>
<h2>{eur(LIT["mezzi"])} in your currency</h2>
{mezzi_valute_it()}
<p class="fonte">Conversion: ECB reference rates of {data_lunga(CAMBI["data"])} where the ECB publishes the currency; Bank of Italy 2025 annual average for the others (the ECB does not publish them). The consulate uses its own rate on the day: keep a margin.</p>
<h2>After you arrive: the residence permit</h2>
<p>Within {LIT["permesso_giorni"]} working days of arrival you send the application for a study residence permit (permesso di soggiorno per studio) through a post office kit or your university's desk; the post office gives you a receipt and an appointment at the police headquarters (Questura) for fingerprints. Renew it at least {LIT["rinnovo_giorni"]} days before it expires.</p>
{costi_permesso_it()}
{fonte_it_p(("poste", "polizia", "circolare"))}
<h2>Health cover</h2>
<p>When you apply for the permit you must show health cover for medical care and hospital stays: a consular declaration under a health agreement between Italy and your country, or a policy with no limits on urgent hospital care for the whole stay. Once you hold a study permit, the law also lets you register voluntarily with the National Health Service (SSN), for at least {eur(LIT["ssn_minimo"])} a year. <a href="../health-insurance/">The options in detail</a>.</p>
{fonte_it_p(("circolare", "ssn"))}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
{link_tema_it("../", "student-visa-funds/")}"""
    titolo = f"Italy student visa bank balance 2026/27: {eur(LIT['mezzi'])} a year"
    descr = (f"Italian student visa 2026/27: {eur(LIT['mezzi'])} a year of funds (MUR procedures), in USD, INR, PKR, BDT, NGN and more; visa deadline "
             f"{data_lunga(LIT['visto_scadenza'])}; residence permit {eur(round(base + LIT['ps_contributo_1'], 2))}.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande)], briciole=[("Study in Italy", SEZ_IT), ("Student visa funds", percorso)])


def pagina_it_isee():
    rel = "../../"
    percorso = f"{SEZ_IT}isee-parificato/"
    es = esempio_isee_it()
    righe = ""
    for E in ENTI_IT:
        anno = f"income of {E['anno_redditi']}" if E.get("anno_redditi") else "see the call"
        sc = E.get("estero_scadenza")
        righe += (f'<tr><th scope="row"><a href="../{E["id"]}/">{escape(E["nome"])}</a></th><td>{escape(metodo_testo(E))}</td>'
                  f'<td class="small">“{escape(E["estero"]["frammento"])}”</td><td>{data_lunga(sc) if sc else scad_testo(E, True)}</td><td class="small">{anno}</td></tr>')
    tab = pila(f'<div class="tab compatta"><table id="t-metodo-it"><caption class="sr">Who calculates the ISEE parificato at each agency</caption><thead><tr><th scope="col">Agency</th>'
               f'<th scope="col">Who calculates it</th><th scope="col">Words in the call</th><th scope="col">Documents due by</th><th scope="col">Year</th></tr></thead><tbody>{righe}</tbody></table></div>')
    domande = [
        ("What is the ISEE parificato?",
         "The indicator Italian scholarship agencies use when a student's family income and assets are abroad. It replaces the ISEE that Italian residents get from INPS."),
        ("How is the ISEE parificato calculated?",
         f"Total income of the family in the year, plus 20% of its assets (savings and investments, and buildings at {eur(500)} per square metre), divided by "
         f"the equivalence scale: 1 for one person, 1.57 for two, 2.04 for three, 2.46 for four, 2.85 for five, plus 0.35 for each extra person. "
         "The ISPE is the assets alone divided by the same scale."),
        ("Which documents do I need for the ISEE parificato?",
         "Official documents from your country, legalised (or apostilled) and translated into Italian, showing: who is in the family, each member's income for the "
         "year, the buildings each member owns with their area in square metres, and savings and investments at 31 December. Self-declarations are not accepted."),
        ("Where do I get the ISEE parificato?",
         "From a CAF (tax assistance centre) that has an agreement with your agency or university, where the call asks for it (DiSCo Lazio, Politecnico di Milano, "
         "Padua, ERSU Palermo and Catania, ADISU Campania). ER.GO, DSU Toscana and the University of Milan calculate it themselves from the documents you upload."),
        ("Which exchange rate is used?",
         "The Bank of Italy average for the income year, as the calls of ER.GO and DiSCo say; DSU Toscana writes the 2025 average euro exchange rate."),
    ]
    corpo = f"""<section class="hero"><h1>ISEE parificato 2026/27: formula, documents and calculator</h1>
<p class="lead">The ISEE parificato adds your family's income to 20% of its assets, counting buildings abroad at <strong>{eur(500)} per square metre</strong>, and divides by the equivalence scale, according to the 2026/27 scholarship calls (University of Milan, ER.GO, DSU Toscana, DiSCo) and DPCM 159/2013 read on {data_lunga(LETTO_IT)}. It must stay under each agency's limit, from {eur(min(E["isee"]["valore"] for E in ENTI_IT))} to {eur(max(E["isee"]["valore"] for E in ENTI_IT))}.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("calc")}<span>ISEE parificato</span><span>read on {data_lunga(LETTO_IT)}</span></div>
<div class="s-body">
<p class="formula-it">ISEE = (income + 20% × (savings + m² × {eur(500)} − mortgage)) ÷ scale<br>ISPE = (savings + m² × {eur(500)} − mortgage) ÷ scale</p>
<div class="kpi"><div><b>{eur(LIT["isee_max"])}</b><span>highest ISEE limit allowed (MUR)</span></div><div><b>{eur(LIT["ispe_max"])}</b><span>highest ISPE limit allowed (MUR)</span></div><div><b>2.46</b><span>scale for a family of four</span></div><div><b>{eur(500)}/m²</b><span>value of a building abroad</span></div></div>
{fonte_it_p(("unimi", "scala", "dd176"))}
</div></section>
{AVVISO_IT}
{AD}
{calc_it("../")}
<h2>The formula, step by step</h2>
<ol class="testo"><li><strong>Income</strong>: the gross income of every family member in the year, converted into euros at the Bank of Italy average rate for that year.</li>
<li><strong>Assets</strong>: savings and investments at 31 December, plus the buildings the family owns (land is not counted) at {eur(500)} per square metre, minus any mortgage still owed.</li>
<li><strong>Economic situation</strong>: income plus 20% of the assets.</li>
<li><strong>Divide by the scale</strong> for the number of people in the family. The result is the ISEE; the assets divided by the scale are the ISPE.</li></ol>
<p>The University of Milan's call describes it this way: “{escape(ent("university-of-milan")["estero_regola"]["frammento"])}”. The allowances of the Italian ISEE (on rent, on savings, on the family home) and the extra points of the scale for families with children are applied by the CAF or the agency case by case; our estimate leaves them out, so with the same documents and exchange rate the official figure can only be the same or lower.</p>
<h3>The equivalence scale</h3>
{tabella_scala_it()}
{fonte_it_p(("scala", "unimi", "ergo"))}
<h3>An example</h3>
<p>A family of four in Pakistan with a 2025 income of PKR {es["red"]:,}, savings of PKR {es["ris"]:,} and a {es["mq"]} m² house: at {es["t"]} rupees per euro (Bank of Italy 2025 average) the income is {eur(es["isr"])} and the assets {eur(es["isp"])} ({eur(es["mob"])} + {es["mq"]} × {eur(500)}). ISEE = ({eur(es["isr"])} + 20% × {eur(es["isp"])}) ÷ {es["sc"]} = <strong>{eur(es["isee"])}</strong>; ISPE = {eur(es["isp"])} ÷ {es["sc"]} = <strong>{eur(es["ispe"])}</strong>.</p>
<h2>Who calculates it, agency by agency</h2>
{tab}
<p class="fonte">Source: the 2026/27 calls linked on each agency page, read on {data_lunga(LETTO_IT)}. "Year": the year of the income the call asks for, where it says so.</p>
<h2>The documents</h2>
<ul class="testo"><li>Family composition, from the registry office or another public authority (with divorce or death certificates if a parent is missing).</li>
<li>Each member's gross income in the year, from the tax authority (or the employer's certificate, or the payslips), and a statement for members with no income.</li>
<li>Buildings each member owns, with the area in square metres; or a statement that nobody owns any.</li>
<li>Savings and investments of each member at 31 December, and any mortgage still owed.</li>
<li>All legalised by the Italian embassy (or apostilled where allowed) and translated into Italian; ER.GO and DiSCo say that no self-declaration or affidavit is accepted.</li></ul>
{fonte_it_p(("ergo", "disco", "unimi"))}
<p class="small">Students from countries on the <a href="../particularly-poor-countries/">particularly poor list</a> bring a certificate from the Italian embassy instead of the income documents. ER.GO and DSU Toscana warn that they have authorised no paid agents or intermediaries; at DiSCo the CAFs with an agreement assist students for free.</p>
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
{link_tema_it("../", "isee-parificato/")}"""
    titolo = "ISEE parificato 2026/27: formula, documents and calculator"
    descr = (f"How the ISEE parificato is calculated for international students in Italy: income + 20% of assets, buildings at {eur(500)}/m², equivalence scale; "
             f"documents, CAF rules of {len(ENTI_IT)} agencies and an estimate in your currency.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande)], briciole=[("Study in Italy", SEZ_IT), ("ISEE parificato", percorso)], script=ISEE_JS)


def pagina_it_scadenze():
    rel = "../../"
    percorso = f"{SEZ_IT}dsu-scholarship-deadlines/"
    righe = ""
    for E in sorted(ENTI_IT, key=lambda E: E["scadenza"]["valore"]):
        s = E["scadenza"]
        sc = E.get("estero_scadenza")
        righe += (f'<tr><th scope="row"><a href="../{E["id"]}/">{escape(E["nome"])}</a></th><td>{data_lunga(s["aperta_dal"]) if s.get("aperta_dal") else "–"}</td>'
                  f'<td>{scad_testo(E)} {stato_scad(s["valore"])}</td><td>{(data_lunga(sc) + " " + stato_scad(sc)) if sc else "same as the application"}</td>'
                  f'<td class="n">{eur(E["fs"]["valore"])}</td></tr>')
    tab = pila(f'<div class="tab compatta"><table id="t-scadenze-it"><caption class="sr">DSU scholarship deadlines 2026/27</caption><thead><tr><th scope="col">Agency</th>'
               f'<th scope="col">Opened</th><th scope="col">Application deadline</th><th scope="col">Income-abroad documents</th><th scope="col" class="n">Top off-campus amount</th></tr></thead>'
               f'<tbody>{righe}</tbody></table></div>')
    prima = min(ENTI_IT, key=lambda E: E["scadenza"]["valore"])
    ultima = max(ENTI_IT, key=lambda E: E["scadenza"]["valore"])
    aperte = [E for E in ENTI_IT if E.get("estero_scadenza") and E["estero_scadenza"] >= LETTO_IT]
    domande = [
        ("What is the DSU scholarship deadline for 2026/27?",
         f"It depends on the agency: from {scad_testo(prima, True)} ({prima['nome']}) to {scad_testo(ultima, True)} ({ultima['nome']}) in the calls we read. "
         "All the 2026/27 application windows have closed."),
        ("What is the DSU scholarship deadline for 2027/28?",
         f"No 2027/28 call has been published yet. The 2026/27 calls we read opened between {data_lunga(min(E['scadenza']['aperta_dal'] for E in ENTI_IT if E['scadenza'].get('aperta_dal')))} "
         f"and {data_lunga(max(E['scadenza']['aperta_dal'] for E in ENTI_IT if E['scadenza'].get('aperta_dal')))}: check your agency's site from June 2027."),
        ("Can I apply for a DSU scholarship before I get the visa?",
         "Yes. The calls are open to students who are not enrolled yet, and several agencies give international students more time for the income documents. "
         "The scholarship counts for the visa only once it has been awarded."),
    ]
    corpo = f"""<section class="hero"><h1>DSU scholarship Italy 2026/27: deadlines and amounts by region</h1>
<p class="lead">The 2026/27 DSU calls closed between <strong>{scad_testo(prima, True)}</strong> ({escape(prima["nome"])}) and <strong>{scad_testo(ultima, True)}</strong> ({escape(ultima["nome"])}), according to the official calls of {len(ENTI_IT)} agencies and universities read on {data_lunga(LETTO_IT)}. {"Some still accept income-abroad documents from applicants: " + ", ".join(f"{E['nome']} until {data_lunga(E['estero_scadenza'])}" for E in sorted(aperte, key=lambda E: E["estero_scadenza"])) + "." if aperte else ""}</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("calendar")}<span>DSU calls 2026/27</span><span>read on {data_lunga(LETTO_IT)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Minimum off-campus scholarship (MUR)</span><span class="sr">: </span><strong>{eur(LIT["dsu_fs"])}</strong></p>
<div class="kpi"><div><b>{eur(LIT["dsu_pend"])}</b><span>commuting student</span></div><div><b>{eur(LIT["dsu_sede"])}</b><span>student living at home</span></div><div><b>+{LIT["dsu_istat"]}%</b><span>update from 2025/26 (ISTAT prices)</span></div><div><b>{len(ENTI_IT)}</b><span>calls read</span></div></div>
{fonte_it_p(("dd175",))}
</div></section>
{AVVISO_IT}
{AD}
<h2>Deadlines and amounts</h2>
{tab}
<p class="fonte">Source: the 2026/27 calls linked on each agency page, read on {data_lunga(LETTO_IT)}. "Top off-campus amount" is the highest amount for the general case; DSU Toscana adds a free room and meals, DiSCo and the two Milan universities add meals.</p>
<h2>How the amount is set</h2>
<p>The Ministry sets minimum amounts each year: for 2026/27 {eur(LIT["dsu_fs"])} for an off-campus student, {eur(LIT["dsu_pend"])} for a commuter and {eur(LIT["dsu_sede"])} for a student living at home, {LIT["dsu_istat"]}% more than in 2025/26. The full amount is paid when the ISEE is up to two thirds of the agency's limit; above that it falls, down to half. Most calls add 15% when the ISEE is up to half of the limit, which gives {eur(round(LIT["dsu_fs"] * 1.15, 2))} for an off-campus student.</p>
{fonte_it_p(("dd175", "ergo", "adisurc"))}
{non_letti_it()}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>Agency pages</h2>
{griglia_enti_it("../")}
{link_tema_it("../", "dsu-scholarship-deadlines/")}"""
    titolo = "DSU scholarship Italy 2026/27: deadlines and amounts by region"
    descr = (f"DSU scholarship deadlines 2026/27 in Italy, agency by agency ({scad_testo(prima, True)} to {scad_testo(ultima, True)}), document deadlines still open "
             f"and off-campus amounts from {eur(LIT['dsu_fs'])}.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande)], briciole=[("Study in Italy", SEZ_IT), ("DSU deadlines", percorso)])


def pagina_it_poveri():
    rel = "../../"
    percorso = f"{SEZ_IT}particularly-poor-countries/"
    lista = "".join(f"<li>{escape(NOMI_POVERI_IT.get(p, p))}</li>" for p in POVERI_IT)
    menzioni = [E for E in ENTI_IT if E.get("poveri")]
    domande = [
        ("Which countries are particularly poor for Italian scholarships in 2026/27?",
         f"{len(POVERI_IT)} countries listed in MUR Ministerial Decree 176 of 24 February 2026, including Bangladesh, Nepal, Ethiopia, Myanmar, Senegal and Afghanistan. "
         "India, Pakistan, Nigeria and Iran are not on the list."),
        ("What changes for students from a particularly poor country?",
         "In most calls, instead of documenting the family's income and assets, you bring a certificate from the Italian embassy in your country saying that you do not belong to "
         "a family that is well known for its high income and social standing. Some calls also accept it from a partner university or a guarantor institution."),
        ("Is Pakistan on the particularly poor countries list?",
         "No. Students whose family lives in Pakistan document their income and assets and get an ISEE parificato. The same applies to India, Nigeria and Iran."),
    ]
    corpo = f"""<section class="hero"><h1>Particularly poor countries 2026/27: the list for Italian scholarships</h1>
<p class="lead">For 2026/27 the Italian Ministry of University and Research lists <strong>{len(POVERI_IT)} particularly poor countries</strong>, including Bangladesh and Nepal, in Ministerial Decree 176 of 24 February 2026 read on {data_lunga(LETTO_IT)}. In most of the 2026/27 DSU calls we read, students whose family lives there bring a certificate from the Italian embassy instead of the ISEE parificato.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("globe")}<span>Particularly poor countries</span><span>read on {data_lunga(LETTO_IT)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Countries on the 2026/27 list</span><span class="sr">: </span><strong>{len(POVERI_IT)}</strong></p>
{fonte_it_p(("dm176",))}
</div></section>
{AVVISO_IT}
{AD}
<h2>The list</h2>
<ul class="testo" style="columns:2 12rem">{lista}</ul>
{fonte_it_p(("dm176",))}
<h2>What the calls ask instead</h2>
<p>A certificate from the Italian diplomatic representation in your country stating that you do not belong to a family “notoriamente di alto reddito ed elevato livello sociale” (well known for its high income and social standing). The calls of {", ".join(E["nome"] for E in menzioni)} mention the list; ERSU Palermo and ERSU Catania also keep some scholarships for these students and for refugees. The University of Milan places students from every country outside its Annex 1 in the first band, and the University of Padua's call does not mention the list. DiSCo and Politecnico di Milano also accept it from a university in your country that has an agreement with the Italian one; Politecnico di Milano and ADISU Campania accept it, for first-year students, from Italian institutions that act as guarantors and would repay it if it is revoked. The certificate must arrive by the call's deadline.</p>
{fonte_it_p(("ergo", "dsut", "disco", "polimi", "palermo", "catania", "adisurc"))}
<p class="small">The Ministry draws up the list every year with the Foreign Ministry, starting from the OECD list of countries that receive development aid. If your family lives in a country that is not on it, you need the <a href="../isee-parificato/">ISEE parificato</a>. ER.GO also accepts the certificate from students coming from areas affected by conflict or humanitarian crises not on the list.</p>
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
{link_tema_it("../", "particularly-poor-countries/")}"""
    titolo = "Particularly poor countries 2026/27: list for Italian scholarships"
    descr = (f"The {len(POVERI_IT)} particularly poor countries of MUR Ministerial Decree 176/2026 (Bangladesh, Nepal, Ethiopia and more): what DSU scholarship calls ask "
             "from their students instead of the ISEE parificato.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande)], briciole=[("Study in Italy", SEZ_IT), ("Particularly poor countries", percorso)])


def pagina_it_salute():
    rel = "../../"
    percorso = f"{SEZ_IT}health-insurance/"
    domande = [
        ("How much is the SSN voluntary registration for students in Italy?",
         f"At least {eur(LIT['ssn_minimo'])} a year: the law (art. 34 of Legislative Decree 286/1998) sets that minimum for students with a study permit. "
         "The registration does not cover dependent family members. The law lets the Health Ministry update the amount by decree, so check it with your local health authority (ASL)."),
        ("Is private health insurance accepted for the Italian student permit?",
         "Yes, if it is valid in Italy and has no limits or exceptions on the cost of urgent hospital care for the whole stay (a foreign policy), or if an Italian "
         "insurer declares the same (an Italian policy). A consular declaration under an agreement between Italy and your country also works."),
        ("When do I show the health insurance?",
         "When you apply for the residence permit, according to the 2026/27 procedures, which list a consular declaration, a foreign policy or an Italian policy. "
         "SSN voluntary registration is open to students who hold a study permit."),
    ]
    corpo = f"""<section class="hero"><h1>Health insurance for the Italian student visa: SSN or a policy</h1>
<p class="lead">Students with a study permit can join Italy's National Health Service (SSN) for at least <strong>{eur(LIT["ssn_minimo"])} a year</strong>, according to article 34 of Legislative Decree 286/1998 on Normattiva read on {data_lunga(LETTO_IT)}. For the residence permit application itself, the 2026/27 procedures list three forms of cover: a consular declaration under a health agreement, or a foreign or Italian policy with no limits on urgent hospital care.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("shield")}<span>Health cover</span><span>read on {data_lunga(LETTO_IT)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">SSN voluntary registration, students, a year</span><span class="sr">: </span><strong>at least {eur(LIT["ssn_minimo"])}</strong></p>
{fonte_it_p(("ssn", "circolare"))}
</div></section>
{AVVISO_IT}
{AD}
<h2>The three options in the procedures</h2>
<ol class="testo"><li>A consular declaration of your right to health care under an agreement between Italy and your country.</li>
<li>A foreign insurance policy valid in Italy, “{escape(SI["letture"]["assicurazione_polizza"]["frammento"])}” (with no limits or exceptions on the charges for urgent hospital care for its whole duration).</li>
<li>A policy with an Italian insurer, with the insurer's declaration that it has no such limits.</li></ol>
<p>Separately, the law opens voluntary registration with the SSN to “{escape(SI["letture"]["ssn_studenti"]["frammento"])}” (foreigners in Italy with a study permit). The contribution is “{escape(SI["letture"]["ssn_minimo"]["frammento"])}” (at least {eur(LIT["ssn_minimo"])} a year for students) and does not cover dependants. The law allows a yearly decree of the Health Ministry to update the minimum, so ask your ASL for the amount when you register. The procedures do not list SSN registration among the forms of cover for the permit application, so ask your university's international office what to show until you are registered.</p>
{fonte_it_p(("circolare", "ssn"))}
{box_assicurazione_it(rel)}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
{link_tema_it("../", "health-insurance/")}"""
    titolo = f"Italy student visa health insurance: SSN {eur(LIT['ssn_minimo'])} or a policy"
    descr = (f"Health cover for the Italian study permit: the three forms in the 2026/27 MUR procedures (consular declaration or a policy with no limits on urgent "
             f"hospital care) and SSN voluntary registration from {eur(LIT['ssn_minimo'])} a year (art. 34 TU 286/1998).")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=[ld_faq(domande)], briciole=[("Study in Italy", SEZ_IT), ("Health insurance", percorso)])


def pagina_it_ente(E):
    rel = "../../"
    percorso = f"{SEZ_IT}{E['id']}/"
    fb = FIT[E["fonti"][0]]
    citazioni = [("ISEE and ISPE limits", f'{eur(E["isee"]["valore"])} / {eur(E["ispe"]["valore"])}', E["isee"]["frammento"], E["isee"]["fonte"])]
    if E["ispe"]["frammento"] != E["isee"]["frammento"]:
        citazioni[0] = ("ISEE limit", eur(E["isee"]["valore"]), E["isee"]["frammento"], E["isee"]["fonte"])
        citazioni.append(("ISPE limit", eur(E["ispe"]["valore"]), E["ispe"]["frammento"], E["ispe"]["fonte"]))
    if E.get("isee_conferma"):
        citazioni.append(("ISEE bands (confirm the €25,000 limit)", f'{eur(E["fs"]["fino_isee"])}', E["isee_conferma"]["frammento"], E["isee_conferma"]["fonte"]))
    citazioni.append(("Highest off-campus amount", eur(E["fs"]["valore"]), E["fs"]["frammento"], E["fs"]["fonte"]))
    for c, lab in (("fs_cifra", "Highest off-campus amount (table)"), ("fs_fascia", "Band for that amount"), ("fs_base", "Full base amount"), ("servizi", "Services included")):
        if E.get(c) and E[c]["frammento"] not in [x[2] for x in citazioni]:
            citazioni.append((lab, eur(E[c]["valore"]) if "valore" in E[c] else "–", E[c]["frammento"], E[c]["fonte"]))
    citazioni.append(("Application deadline", scad_testo(E, True), E["scadenza"]["frammento"], E["scadenza"]["fonte"]))
    citazioni.append(("Income abroad", "–", E["estero"]["frammento"], E["estero"]["fonte"]))
    for c, lab in (("estero_scad_fr", "Income-abroad documents due"), ("estero_cambio", "Exchange rate"), ("estero_regola", "Formula"), ("poveri", "Particularly poor countries")):
        if E.get(c):
            citazioni.append((lab, data_lunga(E["estero_scadenza"]) if c == "estero_scad_fr" else ("certificate" if c == "poveri" else "–"), E[c]["frammento"], E[c]["fonte"]))
    righe_c = "".join(f'<tr><th scope="row">{a}</th><td class="n">{b}</td><td class="small">“{escape(c)}”</td><td>{link_fonte_it(k, "PDF")}</td></tr>' for a, b, c, k in citazioni)
    tab_c = pila(f'<div class="tab compatta"><table id="t-cit-it"><caption class="sr">What the official call says</caption><thead><tr><th scope="col">What</th>'
                 f'<th scope="col" class="n">Value</th><th scope="col">Words in the call (Italian)</th><th scope="col">Source</th></tr></thead><tbody>{righe_c}</tbody></table></div>')
    sc = E.get("estero_scadenza")
    if E["metodo"] == "caf":
        estero = (f"Students whose family's income and assets are abroad need {escape(metodo_testo(E))}. You bring the official documents from your country "
                  f"(family composition, income, buildings with their area, savings), legalised and translated into Italian, and the CAF issues the "
                  f"ISEE and ISPE parificato" + (f"; if you applied by the deadline, the call gives you until {data_lunga(sc)} to submit it" if sc else f", by the application deadline") + ".")
    elif E.get("allegato1"):
        estero = (f"The University of Milan asks for income documents only from students whose family lives in one of the {len(SI['unimi_allegato1'])} countries of Annex 1 "
                  f"of its call (mostly high-income ones such as the United States, the United Kingdom, Canada, Japan, the Gulf states and EU countries) and calculates "
                  f"the ISEE parificato itself. Students from every other country, including India, Pakistan, Nigeria, Bangladesh and Iran, are placed in the first "
                  f"income band, the one with the highest amount; the university can ask for the documents later to check.")
    else:
        estero = (f"{escape(E['nome'])} calculates the economic situation itself from the documents you upload: family composition, income, buildings with "
                  f"their area and savings, issued by the authorities of your country, legalised and translated into Italian, by the application deadline. "
                  f"It does not accept self-declarations.")
    altri_regione = [X for X in ENTI_IT if X["regione"] == E["regione"] and X["id"] != E["id"]]
    domande = [
        (f"What is the ISEE limit for the {E['nome']} scholarship in 2026/27?",
         f"{eur(E['isee']['valore'])} for the ISEE and {eur(E['ispe']['valore'])} for the ISPE, according to the 2026/27 call. Both must be under the limit."),
        (f"How much is the {E['nome']} scholarship for off-campus students?",
         f"{fs_testo(E)[0].upper() + fs_testo(E)[1:]} with an ISEE up to {eur(E['fs']['fino_isee'])}; less above that."),
        (f"What was the {E['nome']} scholarship deadline for 2026/27?",
         f"{scad_testo(E)}." + (f" International students with income abroad who applied in time {'had' if sc < LETTO_IT else 'have'} until {data_lunga(sc)} for the ISEE parificato or the documents." if sc else "")
         + " The 2027/28 call is not out yet."),
        (f"How do international students prove their income for {E['nome']}?",
         re.sub(r"<[^>]+>", "", estero)),
    ]
    inglese = f' <a href="{escape(fb["inglese"])}" rel="noopener">English translation of the call</a> (the Italian text prevails).' if fb.get("inglese") else ""
    corpo = f"""<section class="hero"><h1>{escape(E["nome"])} scholarship 2026/27: ISEE limit, amount and deadline</h1>
<p class="lead">{escape(E["nome"])} gives off-campus students <strong>{fs_testo(E)}</strong> with an ISEE up to {eur(E["fs"]["fino_isee"])}, and accepts an ISEE up to <strong>{eur(E["isee"]["valore"])}</strong> and an ISPE up to <strong>{eur(E["ispe"]["valore"])}</strong>, according to its official 2026/27 call ({data_bando(E)}) read on {data_lunga(LETTO_IT)}. The application deadline was {scad_testo(E, True)}.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("coins")}<span>{escape(E["nome_lungo"])}</span><span>read on {data_lunga(LETTO_IT)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Off-campus scholarship, ISEE up to {eur(E["fs"]["fino_isee"])}</span><span class="sr">: </span><strong>{eur(E["fs"]["valore"])}</strong></p>
<div class="kpi"><div><b>{eur(E["isee"]["valore"])}</b><span>ISEE limit</span></div><div><b>{eur(E["ispe"]["valore"])}</b><span>ISPE limit</span></div><div><b>{scad_testo(E, True)}</b><span>application deadline {stato_scad(E["scadenza"]["valore"])}</span></div><div><b>{data_lunga(sc) if sc else ("CAF" if E["metodo"] == "caf" else "documents")}</b><span>{"income-abroad documents due" if sc else "how income abroad is assessed"}</span></div></div>
<p class="fonte">Source: {link_fonte_it(E["fonti"][0])} ({data_bando(E)}), read on {data_lunga(LETTO_IT)}.{inglese}</p>
</div></section>
{AVVISO_IT}
{AD}
<p>For students at {escape(E["universita"])} ({escape(", ".join(E["citta"]))}).</p>
{f'<p class="small">{ico("alert")} Note: {escape(E["isee"]["nota"])}.</p>' if E["isee"].get("nota") else ""}
<h2>What the official call says</h2>
{tab_c}
<p class="fonte">Source: {"; ".join(link_fonte_it(k) for k in E["fonti"])}, read on {data_lunga(LETTO_IT)}. Quotes are short extracts of the Italian text; the call is the reference.</p>
<h2>International students: income abroad</h2>
<p>{estero}</p>
<p class="small">{poveri_ente_it(E)} How the indicator is calculated: <a href="../isee-parificato/">ISEE parificato</a>.</p>
<h2>Estimate your ISEE and ISPE</h2>
{calc_it("../", E["id"])}
<h2>The visa is separate</h2>
<p>The scholarship does not replace the visa funds: you must show {eur(LIT["mezzi"])} a year, and a DSU scholarship counts only once it has been awarded. <a href="../student-visa-funds/">Visa funds and permit costs</a>.</p>
{fonte_it_p(("circolare",))}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>{"Other calls in " + escape(E["regione"]) if altri_regione else "Other agencies"}</h2>
{griglia_enti_it("../", E["id"])}
{link_tema_it("../")}"""
    t = f"{E['nome']} scholarship 2026/27: ISEE limit, amount and deadline"
    if len(t) > 70:
        t = f"{E['nome']} scholarship 2026/27: ISEE limit and amount"
    descr = (f"{E['nome']} DSU scholarship 2026/27: ISEE up to {eur(E['isee']['valore'])}, ISPE up to {eur(E['ispe']['valore'])}, off-campus up to "
             f"{eur(E['fs']['valore'])}, deadline {scad_testo(E, True)}, and how international students prove income abroad.")
    pagina(percorso, t, descr, corpo, jsonld_extra=[ld_faq(domande)], briciole=[("Study in Italy", SEZ_IT), (E["nome"], percorso)], script=ISEE_JS)


def poveri_ente_it(E):
    """Frase sui Paesi particolarmente poveri: solo quello che il bando dell'ente dice."""
    if E.get("poveri"):
        return (f'Family in a <a href="../particularly-poor-countries/">particularly poor country</a> (such as Bangladesh or Nepal)? The {escape(E["nome"])} call '
                f'asks for a certificate from the Italian embassy stating that you do not belong to a well-known high-income family (see the quote above).')
    if E.get("allegato1"):
        return ('Bangladesh, Nepal and the other <a href="../particularly-poor-countries/">particularly poor countries</a> are not in Annex 1, so their '
                'students are placed in the first band like everyone outside it.')
    return (f'The {escape(E["nome"])} call does not mention the <a href="../particularly-poor-countries/">particularly poor countries</a> list: '
            f'if your family lives in one of them, ask the office what to bring.')


def link_studio_it(P, rel):
    """Riga dalle pagine Italia del sito alla sezione Study in Italy."""
    if P.get("paese") != "Italy":
        return ""
    return (f'<p class="small">{ico("check")} Coming to Italy to study? The student visa asks for {eur(LIT["mezzi"])} a year in 2026/27: '
            f'<a href="{rel}{SEZ_IT}">Study in Italy: visa funds, DSU scholarships and ISEE</a>.</p>')


def genera_it():
    pagina_it_indice()
    pagina_it_mezzi()
    pagina_it_isee()
    pagina_it_scadenze()
    pagina_it_poveri()
    pagina_it_salute()
    for E in ENTI_IT:
        pagina_it_ente(E)


def controlli_it():
    import hashlib
    errori = []
    cont = {k: SI[k] for k in ("letture", "fonti", "enti", "non_letti", "poveri", "unimi_allegato1", "cambi_bdi")}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != SI["impronta"]:
        errori.append("studio_italia: impronta del JSON diversa dal contenuto (file modificato a mano?)")
    if any(f.get("http") != 200 for f in FIT.values()):
        errori.append("studio_italia: fonte non letta (HTTP diverso da 200)")
    if not (8 <= len(ENTI_IT) <= 12):
        errori.append(f"studio_italia: {len(ENTI_IT)} enti (attesi 8-12)")
    for E in ENTI_IT:
        if E["isee"]["valore"] > LIT["isee_max"] or E["ispe"]["valore"] > LIT["ispe_max"]:
            errori.append(f"studio_italia: {E['id']} sopra i limiti nazionali")
    for it_ in PAESI_ALL1_IT.values():
        if it_ not in SI["unimi_allegato1"]:
            errori.append(f"studio_italia: {it_} non nell'allegato 1 UNIMI")
    if set(PAESI_ALL1_IT) & set(POVERI_BREVI):
        errori.append("studio_italia: un Paese è sia nell'allegato 1 UNIMI sia tra i poveri")
    for v in VALUTE_IT[1:]:
        if v not in NOMI_VALUTE_IT or v not in CAMBI_IT["2024"]:
            errori.append(f"studio_italia: valuta {v} senza nome o senza cambio 2024")
    if URL_SW_IT and not URL_SW_IT.startswith("https://safetywing.com/"):
        errori.append("studio_italia: link SafetyWing non valido in dati/affiliati.json (_safetywing_italia)")
    return errori


# ================================================================ Italy 7% flat tax for foreign pensioners (31/10/2026)
# Dati: dati/flat7.json (raccolta/flat7.py). Regola: art. 24-ter TUIR fino al 31/12/2026, art. 247 del D.Lgs. 117/2026 dal 1/1/2027.
# Il sito NON dice che un Comune "qualifica": dice se è in un'area della legge e se la popolazione ISTAT dell'anno giusto è entro la soglia.
F7 = json.loads((DATI / "flat7.json").read_text(encoding="utf-8"))
SEZ_F7 = "italy-7-percent-flat-tax/"
L7 = {k: v["valore"] for k, v in F7["letture"].items()}
FF7 = F7["fonti"]
LETTO_F7 = F7["letto_il"]
SOGLIA_F7 = L7["soglia"]
REGIONI_F7 = L7["regioni"]
# anno del trasferimento -> anno della popolazione ISTAT (1° gennaio dell'anno prima) e se il dato è una stima
ANNI_F7 = [(v["trasferimento"], a, v["stima"]) for a, v in sorted(F7["anni_popolazione"].items())]
COMUNI_F7 = F7["comuni"]  # [codice, nome, altro nome, sigla, regione, pop 1/1/2025, pop 1/1/2026]
PER_CODICE_F7 = {c[0]: c for c in COMUNI_F7}
SISMA_F7 = {}
for _x in F7["sisma2016"]:
    SISMA_F7.setdefault(_x["codice"], []).append(_x)
FUSI_F7 = {k for k, v in SISMA_F7.items() if all(x["nota"].startswith("fuso") for x in v)}  # Comuni nati da fusioni (Valfornace)
NOMI_REG_F7 = {"Sicilia": "Sicily", "Sardegna": "Sardinia", "Puglia": "Puglia (Apulia)", "Toscana": "Tuscany", "Lombardia": "Lombardy",
               "Piemonte": "Piedmont", "Valle d'Aosta/Vallée d'Aoste": "Aosta Valley", "Trentino-Alto Adige/Südtirol": "Trentino-South Tyrol"}
VICINO_F7 = 1000  # "vicino alla soglia": popolazione tra soglia − 1.000 e soglia + 1.000 in uno dei due anni


def reg_en(r):
    return NOMI_REG_F7.get(r, r)


def area_f7(c):
    """0 = fuori dalle aree della legge; 1 = una delle 8 regioni; 2 = allegati del sisma 2016-2017 fuori dalle 8 regioni;
    3 = Comune nato dalla fusione di Comuni degli allegati (Valfornace): da chiedere all'Agenzia."""
    if c[4] in REGIONI_F7:
        return 1
    if c[0] in FUSI_F7:
        return 3
    return 2 if c[0] in SISMA_F7 else 0


def pop_f7(c, anno_pop):
    return c[5] if anno_pop == "2025" else c[6]


def stato_f7(c, anno_pop):
    """'area' (fuori dalle aree), 'ok' (entro la soglia), 'over' (sopra la soglia)."""
    if not area_f7(c):
        return "area"
    return "ok" if pop_f7(c, anno_pop) <= SOGLIA_F7 else "over"


def nome_c_f7(c):
    return f'{c[1]}{" / " + c[2] if c[2] else ""} ({c[3]})'


def link_fonte_f7(k, testo=None):
    f = FF7[k]
    return f'<a href="{escape(f["url"])}" rel="noopener">{escape(testo or (f["editore"] + ", " + f["titolo"]))}</a>'


def fonte_f7_p(chiavi=(), extra=""):
    voci = [link_fonte_f7(k) for k in chiavi]
    return (f'<p class="fonte">Source{"s" if len(voci) + bool(extra) > 1 else ""}: {"; ".join(voci)}{("; " if voci and extra else "") + extra}. '
            f'Read on {data_lunga(LETTO_F7)}.</p>')


def anno_pop_testo(anno_pop, breve=False):
    stima = F7["anni_popolazione"][anno_pop]["stima"]
    return f"1 January {anno_pop}" + ((" (estimate)" if breve else " (ISTAT estimate)") if stima else "")


AVVISO_F7 = ('<p class="avviso"><strong>Not tax or legal advice.</strong> This page summarises the law and the guidance of the Agenzia delle Entrate '
             '(Italy\'s tax agency) on the date we read them. Whether you can use the 7% regime depends on your pension, the country you move from '
             'and your own tax position, and the Agenzia delle Entrate decides. Check with an Italian tax adviser (commercialista) or the Agenzia '
             'delle Entrate before you choose a town or move.</p>')

FRASE_DECIDE_F7 = ("Being under the limit does not mean you qualify: the Agenzia delle Entrate decides, and the conditions on your pension, "
                   "your previous residence and the country you move from also apply.")


# ---------- ricerca del Comune (JS): dati in towns.json, caricati quando si usa la casella
def dati_tool_f7():
    return {"soglia": SOGLIA_F7, "vicino": VICINO_F7, "letto": LETTO_F7,
            "anni": [[t, a, s] for t, a, s in ANNI_F7],
            "reg": sorted({reg_en(c[4]) for c in COMUNI_F7}),
            "c": [[c[1], c[2], c[3], 0, area_f7(c), c[5], c[6]] for c in COMUNI_F7]}


def scrivi_dati_tool_f7():
    d = dati_tool_f7()
    idx = {r: i for i, r in enumerate(d["reg"])}
    for riga, c in zip(d["c"], COMUNI_F7):
        riga[3] = idx[reg_en(c[4])]
    (SITO / SEZ_F7).mkdir(parents=True, exist_ok=True)
    (SITO / SEZ_F7 / "towns.json").write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


F7_JS = r"""
(function(){
function key(s){return (s||'').normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase().replace(/[^a-z]/g,'');}
var C={
 stato:function(r,i,d){if(!r[4])return 'area';return r[5+i]<=d.soglia?'ok':'over';},
 cerca:function(q,d,n){var k=key(q);if(!k)return [];if(!d._k){d._k=d.c.map(function(r){return [key(r[0]),key(r[1])];});}
  var a=[],b=[],c=[];for(var j=0;j<d.c.length;j++){var x=d._k[j];
   if(x[0]===k||x[1]===k)a.push(j);else if(x[0].indexOf(k)===0||(x[1]&&x[1].indexOf(k)===0))b.push(j);else if(k.length>2&&(x[0].indexOf(k)>0||(x[1]&&x[1].indexOf(k)>0)))c.push(j);}
  function o(p,q){return d.c[q][5]-d.c[p][5];}
  return a.sort(o).concat(b.sort(o),c.sort(o)).slice(0,n||8);}};
window.F7=C;
function num(x){return String(x).replace(/\B(?=(\d{3})+(?!\d))/g,',');}
function esc(s){return String(s).replace(/[&<>"]/g,function(m){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m];});}
function nome(r){return esc(r[0])+(r[1]?' / '+esc(r[1]):'')+' ('+esc(r[2])+')';}
function scheda(r,d){var reg=d.reg[r[3]];var h='<p class="r-lab">'+esc(reg)+'</p><p class="f7-nome">'+nome(r)+'</p><ul class="r-righe">';
 d.anni.forEach(function(a,i){var st=C.stato(r,i,d),p=r[5+i],lab,cl;
  if(st==='area'){lab='✗ Not in one of the areas in the law';cl='f7-no';}
  else if(st==='ok'){lab='✓ Under the '+num(d.soglia)+' limit';cl='f7-ok';}else{lab='✗ Over the '+num(d.soglia)+' limit';cl='f7-no';}
  var nota=[];if(a[2])nota.push('ISTAT estimate: the final figure can differ.');
  if(st!=='area'&&Math.abs(p-d.soglia)<=d.vicino)nota.push('Close to the limit: check the figure with ISTAT and the Agenzia delle Entrate.');
  if(a[0]===d.anni[0][0]&&st!=='area')nota.push('The 30,000 limit applies from 7 April 2026 (20,000 before).');
  h+='<li class="'+cl+'"><span class="r-lab">Move in '+a[0]+' · ISTAT, 1 January '+a[1]+(a[2]?' (estimate)':'')+'</span><b>'+num(p)+' inhabitants</b><span class="small"><strong class="f7-v">'+lab+'</strong>'+(nota.length?' '+nota.join(' '):'')+'</span></li>';});
 h+='</ul>';
 if(r[4]===1)h+='<p class="small">'+esc(reg)+' is one of the eight regions named in the law.</p>';
 else if(r[4]===2)h+='<p class="small">This town is on the 2016-2017 earthquake lists (annexes to Decree-Law 189/2016).</p>';
 else if(r[4]===3)h+='<p class="it-nota">The earthquake annexes name Fiordimonte and Pievebovigliana, which merged into Valfornace on 1 January 2017. Ask the Agenzia delle Entrate whether the whole town counts.</p>';
 else h+='<p class="small">The law covers towns in Sicily, Calabria, Sardinia, Campania, Basilicata, Abruzzo, Molise and Puglia, and the towns on the 2009 and 2016-2017 earthquake lists.</p>';
 h+='<p class="small" style="margin-top:10px">Being under the limit does not mean you qualify: the Agenzia delle Entrate decides, and the conditions on your pension, your previous residence and the country you move from also apply.</p>';
 return h;}
document.querySelectorAll('[data-f7]').forEach(function(box){var f=box.querySelector('form'),inp=f.querySelector('input'),lista=box.querySelector('[data-lista]'),out=box.querySelector('[data-out]');
 var d=null,carica=null;
 function load(){if(carica)return carica;out.innerHTML='<p class="small">Loading the ISTAT figures for every Italian town…</p>';
  carica=fetch(box.getAttribute('data-src')).then(function(r){if(!r.ok)throw 0;return r.json();}).then(function(x){d=x;out.innerHTML='<p class="small">Type a town and choose it from the list.</p>';return x;})
  .catch(function(){carica=null;out.innerHTML='<p class="small">The town figures could not be loaded. Try again, or look the town up on ISTAT\'s demo.istat.it.</p>';});return carica;}
 function mostra(j){out.innerHTML=scheda(d.c[j],d);lista.innerHTML='';inp.value=d.c[j][0];}
 function suggerisci(){if(!d){load().then(function(){if(d)suggerisci();});return;}var r=C.cerca(inp.value,d,8);
  if(!inp.value.trim()){lista.innerHTML='';return;}
  if(!r.length){lista.innerHTML='<li class="small">No Italian town with that name in ISTAT\'s list.</li>';return;}
  lista.innerHTML=r.map(function(j){var x=d.c[j];return '<li><button type="button" data-j="'+j+'">'+nome(x)+'<span>'+esc(d.reg[x[3]])+'</span></button></li>';}).join('');}
 inp.addEventListener('focus',load);inp.addEventListener('input',suggerisci);
 lista.addEventListener('click',function(e){var b=e.target.closest('button');if(b)mostra(+b.getAttribute('data-j'));});
 f.addEventListener('submit',function(e){e.preventDefault();if(!d){load().then(function(){if(d){var r=C.cerca(inp.value,d,1);if(r.length)mostra(r[0]);}});return;}var r=C.cerca(inp.value,d,1);if(r.length)mostra(r[0]);});
 box.querySelectorAll('[data-prova]').forEach(function(a){a.addEventListener('click',function(e){e.preventDefault();inp.value=a.textContent;load().then(function(){if(d){var r=C.cerca(inp.value,d,1);if(r.length)mostra(r[0]);}});});});});
})();
"""
CSS += (".f7-nome{font-family:var(--serif);font-size:1.45rem;line-height:1.2;margin:4px 0 0;color:var(--ink)}"
        ".r-righe li.f7-ok{border-color:var(--ok)}.r-righe li.f7-ok .f7-v{color:var(--ok)}.r-righe li.f7-no .f7-v{color:var(--no)}.f7-v{display:block}"
        ".f7-lista{list-style:none;margin:10px 0 0;padding:0;display:grid;gap:6px}"
        ".f7-lista button{font:inherit;width:100%;text-align:left;background:var(--card);border:1px solid var(--line-2);border-radius:var(--r-s);padding:9px 12px;"
        "cursor:pointer;color:var(--ink);display:flex;justify-content:space-between;gap:10px;min-height:44px;align-items:center}"
        ".f7-lista button span{font-size:.82rem;color:var(--ink-3);white-space:nowrap}.f7-lista button:hover,.f7-lista button:focus{border-color:var(--accent)}"
        ".f7-prove{font-size:.88rem;margin:10px 0 0}.f7-prove a{margin-right:6px}")


def strumento_f7(rel_sez):
    prove = " · ".join(f'<a href="#" data-prova>{x}</a>' for x in ("Ostuni", "Grottaglie", "Fabriano", "Cefalù", "Lecce"))
    return (f'<section class="card calc" data-f7 data-src="{rel_sez}towns.json" aria-label="Town population check">'
            f'<div class="calc-grid"><form autocomplete="off" role="search"><h2 style="margin:0 0 14px;font-size:1.2rem">{ico("calc")} Town population check</h2>'
            f'<div class="campi"><label class="pieno"><span class="lt">{ico("globe")}Italian town (comune)</span>'
            f'<input type="search" name="comune" placeholder="e.g. Ostuni" autocomplete="off" spellcheck="false" aria-describedby="f7-nota"></label></div>'
            f'<ul class="f7-lista" data-lista aria-live="polite"></ul><p class="f7-prove small">Try: {prove}</p>'
            f'<p class="small" id="f7-nota" style="margin:12px 0 0">ISTAT resident population on 1 January {ANNI_F7[0][1]} (for a move in {ANNI_F7[0][0]}) '
            f'and 1 January {ANNI_F7[1][1]} (ISTAT estimate, for a move in {ANNI_F7[1][0]}), for all {intero(len(COMUNI_F7))} Italian towns, downloaded on '
            f'{data_lunga(LETTO_F7)}. The check runs in your browser.</p></form>'
            f'<div class="calc-out"><div class="risultato" data-out aria-live="polite"><noscript>Turn on JavaScript to search a town; the regional figures are in the '
            f'tables below, and every town\'s population is on <a href="{escape(F7["pagina_istat"])}" rel="noopener">ISTAT\'s demo.istat.it</a>.</noscript></div></div></div></section>')


# ---------- tabelle
def conteggi_f7():
    """Per regione: [Comuni, entro soglia anno 1, entro soglia anno 2] (8 regioni) e Comuni degli allegati fuori dalle 8 regioni."""
    a1, a2 = ANNI_F7[0][1], ANNI_F7[1][1]
    reg = {}
    for c in COMUNI_F7:
        ar = area_f7(c)
        if not ar:
            continue
        k = (1 if ar == 1 else 2, c[4])
        v = reg.setdefault(k, [0, 0, 0])
        v[0] += 1
        v[1] += pop_f7(c, a1) <= SOGLIA_F7
        v[2] += pop_f7(c, a2) <= SOGLIA_F7
    return reg


def tabella_regioni_f7(rel_sez=""):
    a1, a2 = ANNI_F7[0][1], ANNI_F7[1][1]
    reg = conteggi_f7()
    righe, tot = "", [0, 0, 0]
    ordine = [(1, r) for r in REGIONI_F7] + sorted(k for k in reg if k[0] == 2)
    for k in ordine:
        v = reg[k]
        tot = [x + y for x, y in zip(tot, v)]
        dove = "" if k[0] == 1 else '<span class="small"> (earthquake lists)</span>'
        righe += (f'<tr><th scope="row">{escape(reg_en(k[1]))}{dove}</th><td class="n">{intero(v[0])}</td>'
                  f'<td class="n">{intero(v[1])}</td><td class="n">{intero(v[2])}</td><td class="n">{intero(v[0] - v[1])}</td></tr>')
    righe += (f'<tr><th scope="row">Total</th><td class="n"><b>{intero(tot[0])}</b></td><td class="n"><b>{intero(tot[1])}</b></td>'
              f'<td class="n"><b>{intero(tot[2])}</b></td><td class="n"><b>{intero(tot[0] - tot[1])}</b></td></tr>')
    tab = (f'<div class="tab compatta"><table id="t-regioni-f7"><caption class="sr">Towns under the {intero(SOGLIA_F7)} limit by region</caption><thead><tr>'
           f'<th scope="col">Region</th><th scope="col" class="n">Towns</th><th scope="col" class="n">Under, move in {ANNI_F7[0][0]}</th>'
           f'<th scope="col" class="n">Under, move in {ANNI_F7[1][0]}</th><th scope="col" class="n">Over, move in {ANNI_F7[0][0]}</th></tr></thead>'
           f'<tbody>{righe}</tbody></table></div>'
           f'<p class="small">"Under": towns with up to {intero(SOGLIA_F7)} inhabitants on 1 January {a1} (for a move in {ANNI_F7[0][0]}) or on 1 January {a2}, ISTAT estimate (for a move in {ANNI_F7[1][0]}). '
           f'"Towns": all the towns of the region, or for Lazio, Marche and Umbria only those on the 2016-2017 earthquake lists.</p>')
    return tab, tot


def vicini_f7():
    a1, a2 = ANNI_F7[0][1], ANNI_F7[1][1]
    return sorted([c for c in COMUNI_F7 if area_f7(c) and (abs(c[5] - SOGLIA_F7) <= VICINO_F7 or abs(c[6] - SOGLIA_F7) <= VICINO_F7)],
                  key=lambda c: (reg_en(c[4]), c[1]))


def cella_stato_f7(c, anno_pop):
    s = stato_f7(c, anno_pop)
    return '<span class="stato vigore">Under</span>' if s == "ok" else '<span class="stato sospesa">Over</span>'


def tabella_vicini_f7():
    a1, a2 = ANNI_F7[0][1], ANNI_F7[1][1]
    righe = "".join(f'<tr><th scope="row">{escape(nome_c_f7(c))}<span class="small"><br>{escape(reg_en(c[4]))}</span></th>'
                    f'<td class="n">{intero(c[5])} {cella_stato_f7(c, a1)}</td><td class="n">{intero(c[6])} {cella_stato_f7(c, a2)}</td></tr>' for c in vicini_f7())
    tab = (f'<div class="tab compatta"><table id="t-vicini-f7"><caption class="sr">Towns near the {intero(SOGLIA_F7)} limit</caption><thead><tr>'
           f'<th scope="col">Town</th><th scope="col" class="n">1 January {a1} (move in {ANNI_F7[0][0]})</th>'
           f'<th scope="col" class="n">1 January {a2}, estimate (move in {ANNI_F7[1][0]})</th></tr></thead><tbody>{righe}</tbody></table></div>')
    return pila(tab)


def fonti_elenco_f7():
    voci = []
    for k in ("art24ter", "l34", "art247", "art377", "art24ter_2027", "all1", "all2", "all2bis", "ade", "circ21e", "bura2009", "istat2025", "istat2026", "elenco", "soppressi"):
        f = FF7[k]
        extra = ""
        if k in ("istat2025", "istat2026") and f.get("last_modified"):
            extra = f' (file dated {data_lunga(_data_http(f["last_modified"]))})'
        voci.append(f'<li>{link_fonte_f7(k)}{extra}, read on {data_lunga(f["letto_il"])}</li>')
    return '<ul class="fonti">' + "".join(voci) + "</ul>"


def _data_http(s):
    from email.utils import parsedate_to_datetime
    return parsedate_to_datetime(s).date().isoformat()


def domande_f7():
    a1 = ANNI_F7[0]
    return [
        ("Who can use Italy's 7% flat tax?",
         "A person who receives a pension paid from abroad, was not tax resident in Italy in the five tax years before, moves from a country that has an "
         "administrative cooperation (tax information exchange) agreement with Italy, and moves their tax residence to an eligible town. "
         "The Agenzia delle Entrate decides whether you meet the conditions."),
        ("Which towns count for the 7% tax?",
         f"Towns of up to {intero(SOGLIA_F7)} inhabitants in Sicily, Calabria, Sardinia, Campania, Basilicata, Abruzzo, Molise and Puglia, and towns "
         f"of up to {intero(SOGLIA_F7)} on the lists of the 2009 (L'Aquila) and 2016-2017 (central Italy) earthquakes, which add towns in Lazio, Marche and Umbria. "
         f"The limit was 20,000 until 6 April 2026."),
        ("Which population figure counts?",
         f"ISTAT's resident population on 1 January of the year before your move, according to the Agenzia delle Entrate: 1 January {a1[1]} for a move "
         f"in {a1[0]}. The same figure counts for all ten years, unless you move to another town."),
        ("Is it 9 or 10 years?",
         "Ten tax years in all: the law covers the year you move and the next nine, and the Agency's Circular 21/E says the maximum is ten years "
         "(a move in 2019 runs to 2028). The Agency's summary page talks of \"nine tax periods\": that follows the law's wording (\"the first nine "
         "tax periods after\" the year the option takes effect), and the year of the move comes on top, which is why the circular counts ten."),
        ("Does the 7% apply only to the pension?",
         "No. The law applies the 7% to foreign income of any kind (pensions, investment income, rent from property abroad), but you must "
         "receive a foreign pension to use it. You can leave out the income from one or more countries; that income is then taxed normally."),
        ("Does the 7% tax change in 2027?",
         "The rule moves to article 247 of the new income tax code (Legislative Decree 117/2026), which applies from 1 January 2027. "
         f"The text is the same, with the same {intero(SOGLIA_F7)} limit."),
    ]


def link_f7(rel):
    return (f'<p><a href="{rel}{SEZ_F7}">Italy 7% flat tax: rules and town check</a> · <a href="{rel}{SEZ_F7}regions/">7% tax regions and earthquake towns</a> · '
            f'<a href="{rel}italy-digital-nomad-visa/">Italy digital nomad visa income</a> · <a href="{rel}country/italy/">Italy visa income requirements</a></p>')


def pagina_f7_indice():
    percorso = SEZ_F7
    a1, a2 = ANNI_F7[0], ANNI_F7[1]
    tab, tot = tabella_regioni_f7()
    fuori = conteggi_f7()
    n_sisma = sum(v[1] for k, v in fuori.items() if k[0] == 2)
    domande = domande_f7() + [
        ("Is my town eligible?",
         "Use the town check above: it tells you whether the town is in one of the areas named in the law and whether ISTAT's figure for the right year is "
         f"within {intero(SOGLIA_F7)}. {FRASE_DECIDE_F7}"),
        ("Some guides say earthquake towns must have under 3,000 inhabitants. Is that right?",
         f"Not any more. The text in force says \"in any case\" up to {intero(SOGLIA_F7)} for the eight regions and both earthquake lists, and the Agency's page "
         f"says the same. The 3,000 cap for earthquake towns applied from December 2019 to March 2022; from 29 March 2022 the limit was 20,000 for all the areas."),
    ]
    ld = [ld_faq(domande)]
    corpo = f"""<section class="hero">{h1_diviso("Italy 7% flat tax for foreign pensioners: the rules and a town population check")}
<p class="lead">Article 24-ter of Italy's income tax code (Normattiva, read on {data_lunga(LETTO_F7)}) lets a person with a foreign pension pay a flat <strong>7%</strong> on all foreign income for ten years after moving to a town of up to <strong>{intero(SOGLIA_F7)}</strong> inhabitants in eight southern regions or on the earthquake lists. The population that counts is ISTAT's figure on 1 January of the year before the move: <strong>1 January {a1[1]}</strong> for a move in {a1[0]}.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("sun")}<span>Italy 7% flat tax</span><span>read on {data_lunga(LETTO_F7)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Tax on foreign income, each year</span><span class="sr">: </span><strong>7%</strong></p>
<div class="kpi"><div><b>{intero(SOGLIA_F7)}</b><span>maximum inhabitants (since 7 April 2026; 20,000 before)</span></div><div><b>10 tax years</b><span>the year you move and the next nine</span></div><div><b>5 tax years</b><span>not tax resident in Italy before the move</span></div><div><b>{intero(tot[1])}</b><span>towns under the limit on 1 January {a1[1]}, in the areas of the law</span></div></div>
{fonte_f7_p(("art24ter", "l34", "ade"))}
</div></section>
{AVVISO_F7}
{AD}
{strumento_f7("")}
<h2 id="who">Who can use it</h2>
<p>The conditions in article 24-ter and in the Agency's guidance:</p>
<ul class="testo">
<li><strong>A foreign pension.</strong> You receive pension income paid by a foreign payer (the law says "redditi da pensione … erogati da soggetti esteri").</li>
<li><strong>Five years out.</strong> You were not tax resident in Italy in the five tax years before the year the option starts.</li>
<li><strong>The country you come from.</strong> You move from a country with which Italy has an administrative cooperation agreement in force, which the Agency explains as an instrument for exchanging tax information.</li>
<li><strong>The town.</strong> You move your tax residence to a town of up to {intero(SOGLIA_F7)} inhabitants in Sicily, Calabria, Sardinia, Campania, Basilicata, Abruzzo, Molise or Puglia, or to a town on the 2009 or 2016-2017 earthquake lists, which add towns in Lazio, Marche and Umbria.</li>
</ul>
<p>If you meet them, the 7% replaces Italian income tax on <em>all</em> your foreign income, not only the pension, for the year you move and the next nine tax years. You choose it in your Italian tax return for the year you move, and pay the tax in one instalment by the deadline for the income tax balance. You can leave out the income from one or more countries (that income is then taxed normally, with the foreign tax credit). You can revoke the option, but after a revocation, or if the conditions stop being met, you cannot choose it again.</p>
{fonte_f7_p(("art24ter", "circ21e"))}
<h2 id="population">Which population year counts</h2>
<p>The Agenzia delle Entrate looks at ISTAT's resident population on 1 January of the year before the first year of the option. That figure counts for all ten years, even if the town grows later. If you move to another eligible town, the new town's figure on 1 January of the year before that move counts.</p>
<div class="tab"><table><thead><tr><th scope="col">You move in</th><th scope="col">ISTAT figure that counts</th><th scope="col">Status of the figure</th></tr></thead><tbody>
<tr><td>{a1[0]}</td><td>1 January {a1[1]}</td><td>ISTAT figure</td></tr>
<tr><td>{a2[0]}</td><td>1 January {a2[1]}</td><td>ISTAT estimate ("stima"): the final figure can differ</td></tr></tbody></table></div>
<p class="small">The Agency refers to ISTAT's annual municipal population count; the town check uses ISTAT's resident population on 1 January from demo.istat.it. If ISTAT or the Agency gives a different number for your town, theirs counts.</p>
{fonte_f7_p(("ade", "circ21e", "istat2025", "istat2026"))}
<h2 id="regions">Towns under the limit by region</h2>
<p class="small">Our count from ISTAT's figures. The eight regions count all their towns; Lazio, Marche and Umbria count only the towns on the 2016-2017 earthquake lists ({intero(n_sisma)} under the limit). The earthquake towns in Abruzzo and the 57 towns of the 2009 earthquake list are all in Abruzzo, so they are already in the Abruzzo row.</p>
{tab}
{fonte_f7_p(("istat2025", "istat2026", "all1", "all2", "all2bis", "bura2009"))}
<p><a href="regions/">Region by region: the towns over the limit and the full earthquake lists</a></p>
<h2 id="near">Towns near the limit</h2>
<p>Towns in the areas of the law whose population was within {intero(VICINO_F7)} of {intero(SOGLIA_F7)} on either date. For these, the year of your move decides which figure counts, and a small change in the ISTAT figure matters: check it with ISTAT and the Agency.</p>
{tabella_vicini_f7()}
{fonte_f7_p(("istat2025", "istat2026"))}
<h2 id="changes">What changed in 2026 and what changes in 2027</h2>
<ul class="testo">
<li><strong>7 April 2026:</strong> Law 34 of 11 March 2026 (article 26) raised the limit from 20,000 to {intero(SOGLIA_F7)} inhabitants. The Agency's page, updated on {data_lunga(L7["ade_aggiornata"])}, says the new limit applies from 7 April 2026. Neither the law nor the Agency's page we read says how a move between 1 January and 6 April 2026 to a town between 20,001 and {intero(SOGLIA_F7)} inhabitants is treated: ask the Agency or a tax adviser.</li>
<li><strong>Earthquake towns:</strong> the text in force applies the same {intero(SOGLIA_F7)} limit "in any case" to the eight regions and to both earthquake lists. Guides that give a 3,000 cap for earthquake towns are quoting the version in force from December 2019 to March 2022 (Circular 21/E of 2020 still describes it); from 29 March 2022 the limit was 20,000 for all the areas.</li>
<li><strong>1 January 2027:</strong> the whole income tax code of 1986 is replaced by a new one (Legislative Decree 117 of 19 June 2026). The 7% regime becomes its article 247, with the same wording and the same {intero(SOGLIA_F7)} limit.</li>
</ul>
{fonte_f7_p(("l34", "ade", "art247", "art377", "art24ter_2027"))}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<h2>Sources</h2>
{fonti_elenco_f7()}
<p class="small">To live in Italy as a pensioner from outside the EU you also need the right visa and residence permit (usually the elective residence visa). We do not show an income amount for that visa because the official rules set no fixed figure.</p>
<h2>More on Italy</h2>
{link_f7("../")}"""
    titolo = "Italy 7% flat tax for foreign pensioners: rules and town check"
    descr = (f"Italy's 7% flat tax for foreign pensioners: towns up to {intero(SOGLIA_F7)} inhabitants in 8 southern regions and the earthquake areas, "
             f"10 years, ISTAT population on 1 January of the year before the move. Check any town.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=ld, briciole=[("Italy 7% flat tax", percorso)], script=F7_JS)


def pagina_f7_regioni():
    percorso = f"{SEZ_F7}regions/"
    a1, a2 = ANNI_F7[0], ANNI_F7[1]
    tab, tot = tabella_regioni_f7("../")
    cont = conteggi_f7()
    n_sisma = sum(v[1] for k, v in cont.items() if k[0] == 2)
    # Comuni sopra la soglia nelle 8 regioni
    sopra = ""
    for r in REGIONI_F7:
        cc = sorted([c for c in COMUNI_F7 if c[4] == r and c[5] > SOGLIA_F7], key=lambda c: -c[5])
        voci = ", ".join(f'{escape(c[1])} ({c[3]}) {intero(c[5])}' for c in cc)
        sopra += f'<details class="f7-det"><summary>{escape(reg_en(r))}: {len(cc)} town{"s" if len(cc) != 1 else ""} over {intero(SOGLIA_F7)}</summary><p class="small">{voci}</p></details>'
    # Comuni degli allegati fuori dalle 8 regioni
    sisma = ""
    for r in sorted({c[4] for c in COMUNI_F7 if area_f7(c) in (2, 3)}):
        cc = sorted([c for c in COMUNI_F7 if c[4] == r and area_f7(c) in (2, 3)], key=lambda c: c[1])
        righe = ""
        for c in cc:
            ann = ", ".join(sorted({{"all1": "Annex 1", "all2": "Annex 2", "all2bis": "Annex 2-bis"}[x["allegato"]] + (f' (as {x["nome"]})' if x["nota"] else "")
                                    for x in SISMA_F7[c[0]]}))
            righe += (f'<tr><th scope="row">{escape(nome_c_f7(c))}</th><td>{escape(ann)}</td><td class="n">{intero(c[5])} {cella_stato_f7(c, a1[1])}</td>'
                      f'<td class="n">{intero(c[6])} {cella_stato_f7(c, a2[1])}</td></tr>')
        n_ok = sum(c[5] <= SOGLIA_F7 for c in cc)
        t = (f'<div class="tab compatta"><table id="t-sisma-{slug_testo(r)}"><caption class="sr">Earthquake-list towns in {escape(reg_en(r))}</caption><thead><tr>'
             f'<th scope="col">Town</th><th scope="col">Earthquake list</th><th scope="col" class="n">1 January {a1[1]} (move in {a1[0]})</th>'
             f'<th scope="col" class="n">1 January {a2[1]}, estimate (move in {a2[0]})</th></tr></thead><tbody>{righe}</tbody></table></div>')
        sisma += f'<h3>{escape(reg_en(r))}: {len(cc)} towns on the lists, {n_ok} under {intero(SOGLIA_F7)}</h3>{pila(t)}'
    ab = sorted([PER_CODICE_F7[k] for k in SISMA_F7 if PER_CODICE_F7[k][4] == "Abruzzo"], key=lambda c: c[1])
    ab_sopra = [c for c in ab if c[5] > SOGLIA_F7]
    s09 = [PER_CODICE_F7[x["codice"]] for x in F7["sisma2009"]]
    s09_sopra = [c for c in s09 if c[5] > SOGLIA_F7]
    domande = [domande_f7()[1], domande_f7()[2],
               ("Which towns in Umbria, Marche and Lazio count?",
                f"Only the towns on the 2016-2017 earthquake lists, and only up to {intero(SOGLIA_F7)} inhabitants: on 1 January {a1[1]}, "
                + ", ".join(f"{cont[(2, r)][1]} in {reg_en(r)}" for r in ("Umbria", "Marche", "Lazio") if (2, r) in cont)
                + ". The tables on this page list them all with ISTAT's figures."),
               ("Why is Fabriano on the list but not Macerata or Rieti?",
                f"All three are on the 2016 earthquake lists, but Macerata and Rieti have more than {intero(SOGLIA_F7)} inhabitants; Fabriano had "
                f"{intero(next(c[5] for c in COMUNI_F7 if c[1] == 'Fabriano'))} on 1 January {a1[1]}.")]
    ld = [ld_faq(domande)]
    corpo = f"""<section class="hero">{h1_diviso("Italy 7% tax regions and earthquake towns: population check")}
<p class="lead">Article 24-ter of Italy's income tax code (Normattiva, read on {data_lunga(LETTO_F7)}) covers towns of up to <strong>{intero(SOGLIA_F7)}</strong> inhabitants in Sicily, Calabria, Sardinia, Campania, Basilicata, Abruzzo, Molise and Puglia, plus the towns on the 2009 and 2016-2017 earthquake lists. With ISTAT's figures on 1 January {a1[1]} (the ones that count for a move in {a1[0]}), that is <strong>{intero(tot[1])}</strong> towns under the limit, {intero(n_sisma)} of them in Lazio, Marche and Umbria.</p></section>
{AVVISO_F7}
{AD}
<h2 id="regions">Region by region</h2>
{tab}
{fonte_f7_p(("istat2025", "istat2026", "art24ter"))}
{strumento_f7("../")}
<h2 id="over">Towns over the limit in the eight regions</h2>
<p>These towns are in the eight regions but had more than {intero(SOGLIA_F7)} inhabitants on 1 January {a1[1]} (ISTAT). Every other town in these regions was under the limit on that date.</p>
{sopra}
{fonte_f7_p(("istat2025",))}
<h2 id="earthquake">Earthquake towns in Lazio, Marche and Umbria</h2>
<p>The law adds the towns in Annexes 1, 2 and 2-bis to Decree-Law 189/2016 (the central Italy earthquakes of August and October 2016 and January 2017), with the same {intero(SOGLIA_F7)} limit. Outside the eight regions, these are the towns on the lists. Three names on the lists no longer exist: Acquacanina merged into Fiastra, and Fiordimonte and Pievebovigliana into Valfornace, on 1 January 2017 (ISTAT). Fiastra is on the list in its own name; for Valfornace, ask the Agenzia delle Entrate.</p>
{sisma}
{fonte_f7_p(("all1", "all2", "all2bis", "soppressi", "istat2025", "istat2026"))}
<h2 id="abruzzo">Earthquake towns in Abruzzo and the 2009 list</h2>
<p>The 2016-2017 lists also name {len(ab)} towns in Abruzzo, and the Abruzzo Region lists 57 towns in the area of the 6 April 2009 earthquake (L'Aquila), all in Abruzzo. Abruzzo is one of the eight regions, so these lists add no new towns: the same {intero(SOGLIA_F7)} limit applies. Over the limit: {", ".join(f"{escape(c[1])} ({intero(c[5])})" for c in sorted(ab_sopra + s09_sopra, key=lambda c: c[1]))}.</p>
{fonte_f7_p(("all1", "all2", "all2bis", "bura2009", "istat2025"))}
<h2>Questions people ask</h2>
<div class="testo">{faq_html(domande)}</div>
<p><a href="../">Italy 7% flat tax: who can use it, which population year counts, what changes in 2027</a></p>
<h2>Sources</h2>
{fonti_elenco_f7()}
<h2>More on Italy</h2>
{link_f7("../../")}"""
    titolo = "Italy 7% tax regions and earthquake towns: 2026 population check"
    descr = (f"Italy 7% flat tax: towns under {intero(SOGLIA_F7)} by region, the towns over the limit, and the earthquake towns in Umbria, Marche and Lazio, "
             f"with ISTAT population on 1 January {a1[1]} and {a2[1]}.")
    pagina(percorso, titolo, descr, corpo, jsonld_extra=ld, briciole=[("Italy 7% flat tax", SEZ_F7), ("Regions", percorso)], script=F7_JS)


CSS += (".f7-det{border:1px solid var(--line);border-radius:var(--r-s);background:var(--card);padding:4px 14px;margin:8px 0}"
        ".f7-det summary{cursor:pointer;font-weight:600;padding:8px 0}.f7-det p{margin:4px 0 10px}")


def link_flat7_it(P, rel):
    """Riga dalle pagine Italia del sito alla pagina della flat tax del 7%."""
    if P.get("paese") != "Italy":
        return ""
    return (f'<p class="small">{ico("check")} Moving to southern Italy with a foreign pension? '
            f'<a href="{rel}{SEZ_F7}">Italy 7% flat tax for foreign pensioners: the rules and a town population check</a>.</p>')


def genera_f7():
    pagina_f7_indice()
    pagina_f7_regioni()
    scrivi_dati_tool_f7()


def controlli_f7():
    import hashlib
    errori = []
    cont = {k: F7[k] for k in ("letture", "fonti", "sisma2016", "sisma2009", "comuni", "anni_popolazione", "pagina_istat")}
    if hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20] != F7["impronta"]:
        errori.append("flat7: impronta del JSON diversa dal contenuto (file modificato a mano?)")
    if any(f.get("http") != 200 for f in FF7.values()):
        errori.append("flat7: fonte non letta (HTTP diverso da 200)")
    if SOGLIA_F7 != 30000 or L7["art247"] != 30000:
        errori.append("flat7: soglia diversa da 30.000 (i testi delle pagine e delle FAQ sono scritti con 30.000 e 20.000): rivedere")
    if len(REGIONI_F7) != 8 or any(r not in {c[4] for c in COMUNI_F7} for r in REGIONI_F7):
        errori.append("flat7: regioni della legge non trovate nell'elenco ISTAT")
    if [a for _, a, _ in ANNI_F7] != ["2025", "2026"]:
        errori.append("flat7: anni della popolazione diversi da 2025 e 2026: rivedere i testi (prima frase, FAQ, strumento)")
    if any(x["codice"] not in PER_CODICE_F7 for x in F7["sisma2016"] + F7["sisma2009"]):
        errori.append("flat7: Comune degli allegati senza codice ISTAT valido")
    if any(PER_CODICE_F7[x["codice"]][4] != "Abruzzo" for x in F7["sisma2009"]):
        errori.append("flat7: un Comune del sisma 2009 non è in Abruzzo: rivedere i testi")
    if FUSI_F7 != {"043058"}:
        errori.append(f"flat7: Comuni nati da fusione diversi da Valfornace ({sorted(FUSI_F7)}): rivedere il testo dello strumento")
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
    errori += controlli_selt()
    errori += controlli_dtv()
    errori += controlli_studio()
    errori += controlli_mx()
    errori += controlli_it()
    errori += controlli_f7()
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
    genera_selt()
    genera_dtv()
    genera_studio()
    genera_mx()
    genera_it()
    genera_f7()
    pagina_come_funziona()
    about()
    contatti()
    privacy()
    extra()
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili; {len(PROG)} programmi in {len(PAESI)} paesi; "
          f"cambi BCE del {CAMBI['data']}; visti rifiutati: {len(PAESI_RIF)} Paesi, {len(STATI_UE)} Stati Schengen ({A1}), UK fino al {TRIM[-1]}; "
          f"Australia {len(AU_OK)} nazionalità ({AU_A1}), Nuova Zelanda {len(NZ_OK)} ({NZ_A1}), Canada {len(CA_OK)} ({CA_A1}); "
          f"trasferimenti: {len(NAZ_TR)} nazionalità, {sum(len(v) for v in COPPIE_TR.values())} pagine nazionalità × Paese ({Y1}); "
          f"test di inglese UK (SELT): {len(CITTA_PAG)} città e {len(PAESI_PAG)} Paesi con pagina (elenco del {DATA_ELENCO}); "
          f"DTV Thailandia: {len(LET_DTV)} sedi lette su {len(SEDI_DTV)}, {len(PAG_DTV)} con pagina; Irlanda (PPS): {len(PPS_OK)} nazionalità, dati a {PPS_ULTIMO}; "
          f"Messico: {len(CONS_MX)} consolati, UMA {UMA_MX}; Study in Italy: {len(ENTI_IT)} enti DSU, mezzi {LIT['mezzi']} €; "
          f"flat tax 7%: {len(COMUNI_F7)} Comuni ISTAT, {sum(1 for c in COMUNI_F7 if stato_f7(c, '2025') == 'ok')} entro {SOGLIA_F7} (1/1/2025).")


if __name__ == "__main__":
    main()
