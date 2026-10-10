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
import shutil
from datetime import date
from html import escape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
URL_SITO = "https://visa-income-checker.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti), 10/10/2026: non rimuoverlo
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
    if valuta == "EUR":
        return "€" + testo
    if valuta == "GBP":
        return "£" + testo
    return f"{valuta} {testo}"


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
                     + (f'<br><span class="small">What it says: {escape(f["nota"])}</span>' if f.get("nota") else "") + "</li>")
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
:root{--bg:#F6F7F4;--card:#FFFFFF;--ink:#17201B;--ink-2:#46534B;--ink-3:#66746B;--line:#DCE2DC;
--accent:#1E6B52;--accent-2:#E5F2EC;--ok:#1E6B47;--ok-2:#E6F2EB;--warn:#8A4B00;--warn-2:#FFF2DF;--no:#9B2C2C;--no-2:#FBE9E9;--mute:#EEF1EE;--radius:14px}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0F1512;--card:#17201B;--ink:#ECF2EE;--ink-2:#B8C6BD;
--ink-3:#8C9B92;--line:#28362F;--accent:#7FD1B0;--accent-2:#17302A;--ok:#7FD3A6;--ok-2:#173226;--warn:#FFB867;--warn-2:#33250F;--no:#FF9C9C;--no-2:#3A1D1D;--mute:#1E2924}}
:root[data-theme="dark"]{--bg:#0F1512;--card:#17201B;--ink:#ECF2EE;--ink-2:#B8C6BD;--ink-3:#8C9B92;--line:#28362F;--accent:#7FD1B0;
--accent-2:#17302A;--ok:#7FD3A6;--ok-2:#173226;--warn:#FFB867;--warn-2:#33250F;--no:#FF9C9C;--no-2:#3A1D1D;--mute:#1E2924}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;font-size:17px;line-height:1.6}
a{color:var(--accent)}
.wrap{max-width:980px;margin:0 auto;padding:0 16px}
header.top{border-bottom:1px solid var(--line);background:var(--card)}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:58px}
.logo{font-weight:800;font-size:1.12rem;color:var(--ink);text-decoration:none;letter-spacing:-.01em;white-space:nowrap}
.logo span{color:var(--accent)}
nav.menu{display:flex;gap:14px;flex-wrap:wrap;font-size:.95rem}
nav.menu a{color:var(--ink-2);text-decoration:none}
nav.menu a:hover{color:var(--accent)}
.hero{padding:28px 0 4px}
h1{font-size:clamp(1.45rem,4.6vw,2.15rem);line-height:1.18;letter-spacing:-.02em;margin:0 0 12px}
h2{font-size:1.3rem;margin:32px 0 12px;letter-spacing:-.01em}
h3{font-size:1.05rem;margin:20px 0 8px}
.lead{font-size:1.07rem;color:var(--ink-2);max-width:740px;margin:0 0 6px}
.small{font-size:.88rem;color:var(--ink-3)}
.avviso{background:var(--warn-2);border-left:4px solid var(--warn);padding:11px 14px;border-radius:8px;font-size:.94rem;margin:16px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px;min-width:0}
.cifra{font-size:1.05rem;margin:12px 0 0}
.cifra strong{font-size:1.5rem;color:var(--accent)}
.fonte{font-size:.85rem;color:var(--ink-3);margin:6px 0 0;overflow-wrap:anywhere}
.fonte a{color:var(--ink-3)}
.calc{display:grid;gap:12px}
.calc .campi{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.calc label{display:grid;gap:4px;font-weight:600;font-size:.93rem;min-width:0}
.calc input,.calc select{font:inherit;padding:9px 11px;border:1px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink);width:100%;min-width:0}
.calc .pieno{grid-column:1/-1}
.risultato{background:var(--accent-2);border-radius:12px;padding:14px 16px;min-width:0;overflow-wrap:anywhere}
.risultato .tot{font-size:1.6rem;font-weight:800;color:var(--accent);line-height:1.2}
.risultato .conv{font-size:1.05rem;font-weight:700;margin-top:2px}
.risultato ul{margin:8px 0 0;padding-left:20px;font-size:.93rem}
.esito{margin-top:10px;padding:9px 12px;border-radius:10px;font-weight:600;font-size:.95rem}
.esito.si{background:var(--ok-2);color:var(--ok)}
.esito.no{background:var(--no-2);color:var(--no)}
.formula{font-size:.9rem;color:var(--ink-2);margin:8px 0 0}
.tab{overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid var(--line);border-radius:12px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-size:.93rem}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
td.n,th.n{text-align:right;white-space:nowrap}
th{background:var(--mute);font-size:.85rem}
tr:last-child td{border-bottom:0}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px}
.griglia a{display:block;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px;text-decoration:none;color:var(--ink);font-weight:600;min-width:0;overflow-wrap:anywhere}
.griglia a small{display:block;font-weight:400;color:var(--ink-3)}
.griglia a:hover{border-color:var(--accent)}
.testo p,.testo li{max-width:760px}
.fonti li{margin-bottom:8px;overflow-wrap:anywhere}
.form{display:grid;gap:12px}
.form label{display:grid;gap:4px;font-weight:600;font-size:.95rem}
.form input,.form select,.form textarea{font:inherit;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink);width:100%}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:400;font-size:.9rem;color:var(--ink-2)}
.form .check input{width:auto;margin-top:4px}
.btn{font:inherit;font-weight:700;background:var(--accent);color:#fff;border:0;border-radius:10px;padding:12px 18px;cursor:pointer}
:root[data-theme="dark"] .btn{color:#0F1512}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .btn{color:#0F1512}}
.btn:disabled{opacity:.6;cursor:wait}
.hp{position:absolute;left:-9999px}
.ok{background:var(--ok-2);border:1px solid var(--ok);padding:14px;border-radius:10px}
.errore{color:var(--warn);font-weight:600}
.ad-slot:empty{display:none}
.briciole{font-size:.85rem;color:var(--ink-3);margin-top:14px}
.briciole a{color:var(--ink-3)}
.indice{border-left:4px solid var(--accent);padding:10px 14px;background:var(--card);border-radius:0 10px 10px 0;margin:12px 0}
footer{margin-top:50px;border-top:1px solid var(--line);padding:22px 0 40px;font-size:.88rem;color:var(--ink-3)}
footer a{color:var(--ink-3)}
@media (max-width:760px){.calc .campi{grid-template-columns:1fr}
header.top .wrap{flex-direction:column;align-items:flex-start;gap:4px;padding-top:10px;padding-bottom:10px}nav.menu{gap:12px;font-size:.92rem}}
"""

# Motore di calcolo in JS: deve dare gli stessi risultati di calcola() e converti() (verifica.py li confronta).
MOTORE_JS = r"""
var DEC={"IDR":0,"JPY":0,"KRW":0,"ISK":0,"HUF":0};
var LIMITI={adulti:[1,20],figli:[0,20],pagamenti:[12,14]};
function r2(x){return Math.floor(x*100+0.5+1e-9)/100;}
function arrot(x,c){return DEC[c]===0?Math.floor(x+0.5+1e-9):r2(x);}
function limita(n,x){var l=LIMITI[n],v=parseInt(x,10);if(isNaN(v))v=l[0];return Math.max(l[0],Math.min(l[1],v));}
function grp(n,dec){var s=dec?r2(n).toFixed(2):String(Math.floor(n+0.5+1e-9));var p=s.split('.');p[0]=p[0].replace(/\B(?=(\d{3})+(?!\d))/g,',');return p.join('.');}
function soldi(v,c){var t=grp(v,DEC[c]===0?0:2);return c==='EUR'?'€'+t:(c==='GBP'?'£'+t:c+' '+t);}
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
    function riempiG(){var p=selP.value;selG.innerHTML=D.programmi.filter(function(P){return P.paese===p;}).map(function(P){return '<option value="'+P.slug+'">'+esc(P.nome)+'</option>';}).join('');}
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
      var h='<div class="small">Official minimum for '+o.adulti+' adult'+(o.adulti>1?'s':'')+(o.figli?' and '+o.figli+' child'+(o.figli>1?'ren':''):'')+(o.familiari_ignorati?' (family members not counted)':'')+'</div>';
      if(o.periodo==='month'&&o.pagamenti!==12){h+='<div class="tot">'+soldi(o.mensile,val)+' a month × '+o.pagamenti+'</div><div>= '+soldi(o.annuale,val)+' a year ('+soldi(o.mensile12,val)+' a month over 12 payments)</div>';}
      else{h+='<div class="tot">'+soldi(o.mensile,val)+' a month</div><div>'+soldi(o.annuale,val)+' a year</div>';}
      if(cur!==val)h+='<div class="conv">≈ '+soldi(cv.mensile,cur)+' a month'+(o.periodo==='month'&&o.pagamenti!==12?' × '+o.pagamenti:'')+' · '+soldi(cv.annuale,cur)+' a year</div>';
      h+='<ul>';o.righe.forEach(function(r){h+='<li>'+esc(testo(V,r))+(r[1]>1?' × '+r[1]:'')+' = <strong>'+soldi(r[3],val)+'</strong>'+(o.periodo==='month'?' a month':' a year')+'</li>';});
      if(o.tetto)h+='<li>Capped at the maximum set by the rule.</li>';
      if(o.familiari_ignorati)h+='<li>'+esc(o.motivo)+'</li>';h+='</ul>';
      avvisi.forEach(function(a){h+='<p class="small" style="margin:6px 0 0"><strong>Note:</strong> '+esc(a)+'</p>';});
      h+='<p class="formula"><strong>Rule:</strong> '+esc(V.regola)+'</p>';
      var fo=P.fonti[0];h+='<p class="fonte">Official source: <a href="'+esc(fo.url)+'" rel="noopener">'+esc(fo.titolo)+'</a> · checked on '+dl(fo.controllato_il)+'</p>';
      if(cur!==val)h+='<p class="fonte">ECB reference rate of '+dl(CAMBI.data)+'. Indicative conversion.</p>';
      var mio=parseFloat(q('reddito').value),k=limita('pagamenti',q('pagamenti').value);
      if(mio>0){var e=esito(P,o,mio,k,cur,CAMBI.tassi);var mioV=converti(mio,cur,val,CAMBI.tassi),annoV=r2(mioV*k);
        var tuo='Your income of '+soldi(mio,cur)+' a month × '+k+' (≈ '+soldi(mioV,val)+' a month, '+soldi(annoV,val)+' a year)';
        if(e==='nd')h+='<div class="esito no" style="background:var(--warn-2);color:var(--ink)">'+esc(P.condizioni||'')+'</div>';
        else if(e==='si')h+='<div class="esito si">'+tuo+' is at or above this minimum. The consulate still assesses your documents.</div>';
        else if(e==='parziale')h+='<div class="esito no" style="background:var(--warn-2);color:var(--ink)">'+tuo+' meets one form of the amount but not the other (monthly amount or yearly total): ask the consulate how it assesses your income.</div>';
        else h+='<div class="esito no">'+tuo+' is below this minimum.</div>';}
      var np=box.querySelector('[data-nota-pagamenti]');if(np){np.textContent=P.nota_pagamenti||'';np.hidden=!P.nota_pagamenti;}
      if(!fisso){h+='<p class="small" style="margin:8px 0 0"><a href="'+box.getAttribute('data-rel')+P.slug+'/">Full rules and official sources for the '+esc(P.paese+' '+P.nome)+'</a></p>';}
      box.querySelector('[data-out]').innerHTML=h;
      q('reddito').previousElementSibling.textContent='Your monthly income in '+cur+' (optional)';}
    selP.addEventListener('change',function(){riempiG();riempiV();calcolaOra();});
    selG.addEventListener('change',function(){riempiV();calcolaOra();});
    f.addEventListener('input',function(e){if(e.target===selP||e.target===selG)return;calcolaOra(e);});
    f.addEventListener('change',function(e){if(e.target===selP||e.target===selG)return;calcolaOra(e);});
    f.addEventListener('submit',function(e){e.preventDefault();});
    box.__calcola=calcolaOra;calcolaOra();}
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
         "nomi_valute": {k: v[0] for k, v in VALUTE.items()}, "url_cambi": URL_CAMBI_LIVE}
    return ('<script type="application/json" id="dati-visti">' +
            json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>")


def pagina(percorso, titolo, descrizione, corpo, briciole=None, indicizza=True, calcolatore=False, jsonld_extra=None, assoluto=False):
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
    dati = blocco_dati() if calcolatore else ""
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
<meta name="theme-color" content="#1E6B52">
{robots}
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%231E6B52'/%3E%3Ctext x='32' y='44' font-family='Arial' font-weight='700' font-size='30' text-anchor='middle' fill='white'%3E%E2%82%AC%3C/text%3E%3C/svg%3E">
<style>{CSS}</style>
{ld_html}
</head>
<body>
<header class="top"><div class="wrap">
<a class="logo" href="{rel}">Visa Income <span>Checker</span></a>
<nav class="menu" aria-label="Menu">
<a href="{rel}">Calculator</a><a href="{rel}digital-nomad-visa-income-requirements/">Digital nomad visas</a><a href="{rel}work-visa-salary-thresholds/">Work visas</a><a href="{rel}how-it-works/">How it works</a><a href="{rel}about/">About</a>
</nav>
</div></header>
<main class="wrap">
{bc}
{corpo}
</main>
<footer><div class="wrap">
<p><strong>{NOME}</strong> is an independent site, not affiliated with any government, consulate or immigration authority. Every amount is calculated from an official source (law, official gazette, ministry, immigration authority or statistics office) linked under the figure with the date we checked it.
<strong>Requirements change, and consulates can ask for more: always check the official page or the consulate.</strong> Nothing on this site is immigration, legal or tax advice.</p>
<p>Exchange rates: euro foreign exchange reference rates of the European Central Bank (source: ECB), for information only.</p>
<p><a href="{rel}about/">About</a> · <a href="{rel}how-it-works/">How it works and sources</a> · <a href="{rel}contact/">Contact</a> · <a href="{rel}privacy.html">Privacy</a> · <a href="{rel}contact/?ref=spotted-a-change">Spotted a change? Tell us</a></p>
</div></footer>
{dati}
{js}
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
    return f"""<div class="card" data-calcolatore data-rel="{rel}" data-programma="{escape(programma)}" data-paese="{escape(paese)}" data-valuta="{valuta}">
<form class="calc" autocomplete="off">
<div class="campi">
<label data-campo="paese">Country<select name="paese"></select></label>
<label data-campo="programma">Visa or permit<select name="programma"></select></label>
<label class="pieno" data-campo="variante">Category<select name="variante"></select></label>
<label>Adults (including you)<input type="number" name="adulti" min="1" max="20" value="1" inputmode="numeric"></label>
<label>Children under 18<input type="number" name="figli" min="0" max="20" value="0" inputmode="numeric"></label>
<label>Show amounts also in<select name="valuta"></select></label>
<label><span>Your monthly income (optional)</span><input type="number" name="reddito" min="0" step="any" placeholder="e.g. 3500" inputmode="decimal"></label>
<label>Your income is paid<select name="pagamenti"><option value="12">12 times a year</option><option value="13">13 times a year</option><option value="14">14 times a year</option></select></label>
<p class="small pieno" data-nota-pagamenti hidden style="margin:0"></p>
</div>
</form>
<div class="risultato" data-out aria-live="polite"><noscript>Turn on JavaScript to use the calculator. The tables below show the official amounts.</noscript></div>
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
                        "".join(f'<a href="{rel}{p["slug"]}/">{escape(nome_prog(p))}<small>{escape(riassunto(p))}</small></a>' for p in sorelle) + "</div>")
    link_simili = (f'<h2>Compare: other {escape(CATEGORIE[P["categoria"]].lower())}s</h2><div class="griglia">' +
                   "".join(f'<a href="{rel}{p["slug"]}/">{escape(nome_prog(p))}<small>{escape(riassunto(p))}</small></a>' for p in simili) + "</div>") if simili else ""
    fam_tit = "How much for a family" if V0["famiglia"]["tipo"] != "nessuno" else "Family members"
    note = "".join(f"<li>{escape(n)}</li>" for n in P["note"])
    corpo = f"""<section class="hero"><h1>{escape(titolo_prog(P))}</h1>
<p class="lead">{escape(P['descrizione'])} Official name: <em>{escape(P['nome_ufficiale'])}</em>.</p>
<p class="cifra">Minimum for the main applicant{(' (' + escape(V0['nome'].lower()) + ')') if len(P['varianti']) > 1 else ''}: {figura}</p>
{fonte_breve(P)}
{eur_eq}
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
<p><a href="{rel}country/{P['paese_slug']}/">All visa income requirements in {escape(P['paese'])}</a> · <a href="{rel}digital-nomad-visa-income-requirements/">Digital nomad visa income requirements {ANNO}</a> · <a href="{rel}work-visa-salary-thresholds/">Work visa salary thresholds {ANNO}</a></p>"""
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
<div class="griglia" style="margin-top:20px">{''.join(f'<a href="{rel}{p["slug"]}/">{escape(nome_prog(p))}<small>{escape(riassunto(p))}</small></a>' for p in pp)}</div>
<p><a href="{rel}">All countries</a> · <a href="{rel}digital-nomad-visa-income-requirements/">Digital nomad visas compared</a></p>"""
    pagina(f"country/{slug}/", f"{nome} visa income requirements {ANNO}: official amounts and calculator",
           f"Official minimum income and salary thresholds for {nome} visas in {ANNO}, with family members, currency conversion and sources.",
           corpo, calcolatore=True, briciole=[(nome, f"country/{slug}/")])


def home():
    gruppi = []
    for slug, nome in PAESI.items():
        pp = [p for p in PROG if p["paese_slug"] == slug]
        gruppi.append(f'<a href="country/{slug}/">{escape(nome)}<small>{len(pp)} visa{"s" if len(pp) > 1 else ""}</small></a>')
    lista = "".join(f'<a href="{p["slug"]}/">{escape(nome_prog(p))}<small>{escape(riassunto(p))}</small></a>' for p in PROG)
    corpo = f"""<section class="hero"><h1>Visa income checker {ANNO}: how much income do you need for a digital nomad, retirement or work visa?</h1>
<p class="lead">The official minimum income for {len(PROG)} visas and permits in {len(PAESI)} countries, calculated from the official base (minimum wage, IPREM, average salary, legal salary thresholds) for you and each family member, and converted into your currency with the latest European Central Bank reference rates.</p></section>
{modulo_calcolatore(rel='', paese='Spain')}
{AVVISO}
{AD}
<h2>All visas</h2>
<div class="griglia">{lista}</div>
<h2>Countries</h2>
<div class="griglia">{''.join(gruppi)}</div>
<h2>Compare</h2>
<p><a href="digital-nomad-visa-income-requirements/">Digital nomad visa income requirements {ANNO}</a> (with passive income visas) · <a href="work-visa-salary-thresholds/">EU Blue Card and work visa salary thresholds {ANNO}</a></p>
<h2>Why our numbers can differ from other sites</h2>
<p>Many thresholds are a percentage of an index that changes every year (a minimum wage, an average salary), so pages that still show last year's figure are out of date. With the {ANNO} indices, on {data_lunga('2026-10-10')}: Spain's digital nomad visa is 200% of the {ANNO} minimum wage, €2,442 a month over 14 payments (€34,188 a year, the same as €2,849 a month over 12 payments); Croatia's is 2.5 × the 2025 average net salary, €3,622.50 a month; Portugal's D8 is 4 × €920 = €3,680 a month. We recalculate from the official index and show the source and the date under every figure.</p>
{box_affiliati()}"""
    pagina("", f"Visa Income Checker {ANNO}: minimum income for digital nomad, retirement and work visas (calculator)",
           f"How much income do you need? Official {ANNO} minimum income for {len(PROG)} visas (Spain, Portugal, Croatia, Italy, Hungary, Blue Cards, UK) for you and your family, in USD, GBP, INR, PHP and more.",
           corpo, calcolatore=True)


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
    corpo = f"""<section class="hero"><h1>Digital nomad visa income requirements {ANNO}: country by country</h1>
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
<h2>Licences and attributions</h2>
<ul><li>Laws, decrees and official notices (BOE, Gazzetta Ufficiale, Bundesanzeiger, Normattiva) are cited as facts with a link to the official text; we do not reproduce the documents.</li>
<li>Exchange rates: European Central Bank, euro foreign exchange reference rates (source: ECB).</li>
<li>UK: contains public sector information licensed under the Open Government Licence v3.0 (GOV.UK).</li>
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
<h2>Cookies</h2><p>This site does not use profiling cookies or analytics tools. If we add advertising or affiliate links in the future, we will update this notice and ask for your consent where required before any advertising cookies are used.</p>
<h2>How long</h2><p>Messages are kept for up to 12 months after our last exchange.</p>
<h2>Your rights</h2><p>You can ask for access, correction, deletion, restriction, portability and objection (Articles 15–22 GDPR) and you can complain to the Italian data protection authority (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>) or the authority in your country.</p></div>"""
    pagina("privacy.html", f"Privacy | {NOME}", f"Privacy notice of {NOME}.", corpo)


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
""")
    pagina("404.html", f"Page not found | {NOME}", "Page not found.",
           '<section class="hero"><h1>Page not found</h1><p class="lead">Go to the <a href="/">visa income calculator</a>.</p></section>', indicizza=False, assoluto=True)


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
    home()
    for P in PROG:
        pagina_programma(P)
    for s in PAESI:
        pagina_paese(s)
    pagina_confronto_nomadi()
    pagina_confronto_lavoro()
    pagina_come_funziona()
    about()
    contatti()
    privacy()
    extra()
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili; {len(PROG)} programmi in {len(PAESI)} paesi; "
          f"cambi BCE del {CAMBI['data']}.")


if __name__ == "__main__":
    main()
