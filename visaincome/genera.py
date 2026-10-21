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
from collections import defaultdict
from datetime import date
from html import escape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
URL_SITO = "https://visa-income-checker.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti), 10/10/2026: non rimuoverlo

# Contatore visite GoatCounter, account condiviso "rete-siti" della rete (nessun cookie, nessun dato personale conservato).
# Il percorso inviato comprende l'host (location.host + percorso), così nel cruscotto https://rete-siti.goatcounter.com
# ogni sito si distingue dagli altri. Da localhost, da file:// e dalle reti private count.js non invia nulla
# (allow_local resta spento): le prove in locale non contano come visite. Unico punto da cambiare per tutto il sito.
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
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
        ld.append(jsonld_extra)
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
<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">
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
{corpo}
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
<ul><li><a href="{rel}visa-refusal-rates/">Visa refusal rates</a></li><li><a href="{rel}about/">About</a></li><li><a href="{rel}how-it-works/">How it works and sources</a></li><li><a href="{rel}contact/">Contact</a></li><li><a href="{rel}privacy.html">Privacy</a></li><li><a href="{rel}contact/?ref=spotted-a-change">Spotted a change? Tell us</a></li></ul>
</div></div>
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
            '<p class="small" style="margin:0">Some of these are affiliate links: if you buy through them we may earn a small commission, at no extra cost to you.</p></section>')


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
{link_rifiuti(nome, rel)}"""
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
    corpo = f"""<section class="hero"><h1>Privacy notice</h1><p class="small">Last updated: October 2026</p></section><div class="testo">
<h2>Who is responsible</h2><p>The data controller is Massimiliano Cori (Italy), who runs {NOME} as an independent project. You can contact us through the <a href="contact/">contact form</a>.</p>
<h2>What we collect</h2><p>Only what you type in the contact form: your email, the visa or country and your message. We also record the page or link you came from, to understand which pages need corrections. The calculator runs in your browser: the household, currency and income you type in it are not sent to us.</p>
<h2>Exchange rates</h2><p>To show up-to-date conversions, your browser downloads a small file of exchange rates from GitHub (raw.githubusercontent.com), which receives your IP address as for any web request. No other data is sent.</p>
<h2>Why</h2><p>To answer your messages and correct the site. The legal basis is your consent (Art. 6(1)(a) GDPR), which you can withdraw at any time.</p>
<h2>Who processes data for us</h2><p>The site and its form are hosted by Netlify, Inc., which stores form data on our behalf and may process it outside the EU with the safeguards required by the GDPR (standard contractual clauses). We do not sell or share your data.</p>
<h2>Cookies, visit counter and affiliate links</h2><p>This site does not use profiling cookies. To count visits we use <a href="https://www.goatcounter.com/" rel="noopener">GoatCounter</a>, a privacy-friendly counter: it sets no cookies and stores nothing in your browser, builds no profiles and does not store your IP address, your full browser signature or any identifier. It keeps only aggregate numbers (page, hour or day, browser, country, screen width) on servers in the European Union and shares nothing with third parties; see <a href="https://www.goatcounter.com/help/privacy" rel="noopener">GoatCounter's privacy policy</a>. Some pages contain an affiliate link to SafetyWing (marked "Affiliate"): our site sets no cookie for it, but if you click it you go to SafetyWing's website, which uses its own cookies under its own privacy policy and tells SafetyWing that you came from us. If we add advertising in the future, we will update this notice and ask for your consent where required before any advertising cookies are used.</p>
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


GRUPPI_UK_PAGINA = ["Visitor", "Study", "Work"]  # gruppi con una cifra in evidenza nelle pagine per nazionalità (dal 21/10/2026)
NOMI_BREVI_UK = {"Visitor": "visitor", "Study": "study", "Work": "work"}


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
            f'<p class="small">SafetyWing sells travel medical insurance online. This is an affiliate link: if you buy through it we may earn a commission, '
            f'at no extra cost to you. Buying insurance does not change the decision on your visa, and we do not know whether a given consulate accepts a given policy: check before you pay.</p></section>')


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
    gruppi_q = [g for g in ("Study", "Work") if g in ok]
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
        tab_q = (f'<h3>{" and ".join(NOMI_GRUPPI_UK[g].lower() for g in gruppi_q).capitalize()}, quarter by quarter</h3>'
                 f'<div class="tab compatta"><table class="ord"><thead><tr>{th_ord("Quarter", False, "ascending")}{testa}</tr></thead><tbody>{"".join(righe_q)}</tbody></table></div>'
                 f'<p class="fonte">Source: <a href="{escape(F_UK["url"])}" rel="noopener">Home Office, {escape(F_UK["titolo"])}</a> (XLSX, published {escape(F_UK["pubblicato"])}, downloaded on {data_lunga(F_UK["scaricato_il"])}). '
                 f'"Study" is the Home Office group for sponsored study (Student, Child Student) and short-term study visas; "Work" groups all work routes '
                 f'(Skilled Worker, Health and Care Worker, temporary and seasonal work, Global Business Mobility, talent and business visas, and their dependants). '
                 f'* Fewer than {SOGLIA_POCO} decisions; 2026 figures are provisional.</p>')
    nomi_g = [NOMI_BREVI_UK[g] for g in ok]
    tipi = nomi_g[0] if len(nomi_g) == 1 else ", ".join(nomi_g[:-1]) + " and " + nomi_g[-1]
    corpo = (f'<h2 id="uk">UK visa refusal rate for nationals of {escape(art(nome))}: {tipi} visas</h2>'
             f'<p class="lead">From {periodo_uk(T1)}, the UK refused <strong>{pct(uk_tasso(vis1))}</strong> of {NOMI_BREVI_UK[primo]} visa decisions for nationals of {escape(art(nome))} '
             f'({intero(vis1[1])} refused out of {intero(vis1[0] + vis1[1])}).{frase_altri} Unlike the Schengen figures, the UK counts applicants by <strong>nationality</strong>, wherever they apply.'
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
    titolo_h1 = f"Visa refusal rates for {art(nome)}: Schengen countries ({A1}), easiest and hardest" + (", and the UK" if con_uk else "")
    tipi_uk = ""
    if con_uk:
        nomi_g = [NOMI_BREVI_UK[g] for g in uk_r]
        tipi_uk = nomi_g[0] if len(nomi_g) == 1 else ", ".join(nomi_g[:-1]) + " and " + nomi_g[-1]
    corpo = f"""<section class="hero">{h1_diviso(titolo_h1)}
<p class="lead">How many Schengen visa applications made in {escape(art(nome))} were not issued in {A1}, country by country and consulate by consulate, with the easiest and hardest countries for {escape(demonimo(p))}{', and how many UK ' + tipi_uk + ' visa applications by nationals of ' + escape(art(nome)) + ' were refused' if con_uk else ''}. Official figures only.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{ico("passport")}<span>Visa refusal rates</span><span>{escape(nome)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Schengen visas · applications made in {escape(art(nome))} · {A1}</span><span class="sr">: </span><strong>{pct(t1)}</strong> not issued ({intero(v1[3])} of {intero(decisioni(v1))} decisions)</p>
<div class="kpi"><div><b>{intero(v1[0])}</b><span>applications</span></div><div><b>{intero(v1[1])}</b><span>uniform visas issued</span></div><div><b>{intero(v1[3])}</b><span>not issued</span></div><div><b>{punti(t1, t0) if t0 is not None else '–'}</b><span>change on {A0}{f' ({pct(t0)})' if t0 is not None else ''}</span></div></div>
<p class="lead" style="margin-top:6px">{frase_basso} Of the {len(PAESI_RIF)} countries with the most applications, {escape(art(nome))} ranks {pos} (1 = lowest rate).</p>
{fonte_ue_p(A1, A0)}
{uk_kpi}
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
{box_assicurazione(rel)}
<h2>How to read these figures</h2>
<ul class="testo">
<li><strong>Where you apply, not your passport.</strong> The Schengen figures count applications made in {escape(art(nome))}, including residents of other nationalities, and leave out nationals of {escape(art(nome))} who applied elsewhere.</li>
<li><strong>Not-issued rate</strong> = visas not issued ÷ (uniform visas issued + visas with limited territorial validity + visas not issued), the formula in the Commission's file. Applications still pending at the end of the year are not counted.</li>
<li><strong>If you are refused</strong>, the consulate must tell you why and how to appeal (<a href="{URL_COMMISSIONE_DOMANDA}" rel="noopener">European Commission</a>).</li>
<li>Full method: <a href="../#method">how we calculate the rates</a>.</li></ul>
<h2>Other countries where people apply</h2>
<div class="griglia">{griglia_altri}</div>
<p><a href="../">Schengen visa refusal rates by country, {A1}</a> · <a href="../uk/">UK visa refusal rates by nationality</a> · <a href="{rel}">Visa income calculator</a></p>"""
    titolo = f"Schengen visa rejection rate {nome} {A1}: by country, easiest and hardest" + (", plus UK" if con_uk else "")
    descr = (f"Official {A1} figures: {pct(t1)} of Schengen visa applications made in {art(nome)} were not issued."
             + (f" Easiest Schengen visa for {demonimo(p)}: {basso[0][0]} ({pct(tasso(basso[0][1]))}); hardest: {alto[0][0]} ({pct(tasso(alto[0][1]))})." if basso and alto else "")
             + " Every Schengen country and consulate"
             + (f", and the UK refusal rate for nationals of {art(nome)} ({', '.join(f'{NOMI_BREVI_UK[g]} {pct(uk_r[g][0])}' for g in uk_r)})" if con_uk else "") + ".")
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
    corpo = f"""<section class="hero">{h1_diviso(f"UK visa refusal rate by nationality: visitor, student and work visas, {periodo_uk(T1)}")}
<p class="lead">How many UK visa applications were refused, nationality by nationality, from the Home Office's official immigration statistics: visitor visas, student (study) visas and work visas side by side. Updated every quarter.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top">{bandiera("United Kingdom")}<span>UK entry clearance visas</span><span>{periodo_uk(T1)}</span></div>
<div class="s-body">
<p class="cifra"><span class="c-lab">Visitor visas · all nationalities</span><span class="sr">: </span><strong>{pct(uk_tasso(vis))}</strong> refused ({intero(vis[1])} of {intero(vis[0] + vis[1])} decisions)</p>
<div class="kpi"><div><b>{pct(uk_tasso(stu))}</b><span>study visas refused · {intero(stu[0] + stu[1])} decisions</span></div><div><b>{pct(uk_tasso(lav))}</b><span>work visas refused · {intero(lav[0] + lav[1])} decisions</span></div><div><b>{pct(uk_tasso(tot1))}</b><span>all entry clearance visas refused</span></div><div><b>{intero(tot1[0] + tot1[1])}</b><span>decisions on all visas</span></div></div>
{fonte_uk_p()}
</div></section>
{AVVISO_RIF.replace("you must apply to the Schengen country where you will spend the most time (or, for equal stays, the one you enter first), at the consulate responsible for the place where you legally live", "each application is assessed on its own documents")}
{AD}
<h2>Refusal rate by nationality</h2>
<p class="small">Nationalities with at least {SOGLIA_POCO} decisions on all visa types. "Visitor" = Standard Visitor visas (tourism, family visits, business); "Study" = Student, Child Student and short-term study visas; "Work" = all work routes (Skilled Worker, Health and Care Worker, temporary work and others). Tap a column heading to sort, or type to filter. * Fewer than {SOGLIA_POCO} decisions of that type.</p>
<p class="filtro"><label><span class="sr">Filter nationalities</span><input type="search" placeholder="Filter: e.g. Nigeria" data-filtro="t-uk" autocomplete="off"></label></p>
<div class="tab compatta"><table class="ord" id="t-uk"><thead><tr>{th_ord("Nationality", False, "ascending")}{th_ord("Visitor visas refused", primo="ascending")}{th_ord("Year before", primo="ascending")}{th_ord("Visitor decisions")}{th_ord("Study visas refused", primo="ascending")}{th_ord("Study decisions")}{th_ord("Work visas refused", primo="ascending")}{th_ord("Work decisions")}{th_ord("All visas refused", primo="ascending")}{th_ord("All visas: decisions")}</tr></thead><tbody>{"".join(righe)}</tbody></table></div>
{fonte_uk_p()}
<p class="small">"Year before" = {periodo_uk(T0)} (visitor visas). Nationals of many countries (for example the EU, the US, Canada and Australia) do not need a visa for short visits and travel with an electronic travel authorisation instead, so they appear with few or no visitor decisions but often with thousands of study and work decisions.</p>
<h2>How to read these figures</h2>
<ul class="testo"><li>The Home Office counts applicants by <strong>nationality</strong>, wherever they applied. An outcome in a quarter can relate to an application made in an earlier quarter.</li>
<li>The refusal rate is the share of decisions (grants and refusals) that were refusals: withdrawn and lapsed applications are left out, as in the Home Office "grant rate".</li>
<li>Figures from 2026 Q1 onwards are provisional and can be revised in the next release ({escape(F_UK["prossimo"])}).</li></ul>
<p><a href="../">Schengen visa refusal rates</a> · <a href="{rel}uk-skilled-worker-visa/">UK Skilled Worker salary threshold</a> · <a href="{rel}uk-spouse-visa/">UK spouse visa income requirement</a></p>"""
    pagina(f"{SEZ}uk/", f"UK visa refusal rate by nationality {TRIM[-1].split()[0]}: visitor, study and work visas (official)",
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
<p class="sub">Official figures from the European Commission and the UK Home Office: how many visa applications were not issued, by destination, by the country where people applied and by nationality.</p>
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
<li><a href="{URL_COMMISSIONE_DOMANDA}" rel="noopener">Applying for a Schengen visa</a> – European Commission, checked on {data_lunga(DATA_COMMISSIONE_DOMANDA)}</li></ul>
<p><a href="{rel}">Visa income calculator</a> · <a href="{rel}digital-nomad-visa-income-requirements/">Digital nomad visa income requirements</a></p>"""
    ld = {"@context": "https://schema.org", "@type": "Dataset", "name": f"Schengen and UK visa refusal rates {A1}",
          "description": "Visa refusal (not-issued) rates by Schengen country, by country of application and by consulate, and UK refusal rates by nationality, recalculated from official files.",
          "url": f"{URL_SITO}/{SEZ}", "creator": {"@type": "Organization", "name": NOME, "url": URL_SITO + "/"},
          "isBasedOn": [F_UE[A1]["url"], F_UE[A0]["url"], F_UK["url"]], "temporalCoverage": f"{A0}/{TRIM[-1].split()[0]}",
          "license": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"}
    pagina(SEZ, f"Schengen visa rejection rate by country {A1} (official) and UK visa refusal rates",
           f"Official {A1} Schengen visa rejection rates: {pct(t1)} of decisions were visas not issued. Every Schengen country, {len(PAESI_RIF)} countries where people apply, and UK refusal rates by nationality.",
           corpo, ordina=True, testata=testata, jsonld_extra=ld, briciole=[("Visa refusal rates", SEZ)])


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
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{OGGI.isoformat()}</lastmod></url>" for u in URLS)
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
    if errori:
        raise SystemExit("ERRORI NEI DATI:\n" + "\n".join(errori))


def main():
    controlli()
    if SITO.exists():
        conserva = {p.name: p.read_bytes() for p in SITO.glob("google*.html")}
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
    pagina_come_funziona()
    about()
    contatti()
    privacy()
    extra()
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili; {len(PROG)} programmi in {len(PAESI)} paesi; "
          f"cambi BCE del {CAMBI['data']}; visti rifiutati: {len(PAESI_RIF)} Paesi, {len(STATI_UE)} Stati Schengen ({A1}), UK fino al {TRIM[-1]}.")


if __name__ == "__main__":
    main()
