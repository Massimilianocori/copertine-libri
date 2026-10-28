"""Genera il sito statico Before You Fly in beforeyoufly/sito/ da beforeyoufly/dati/.

Uso (dalla radice del repository):
    python3 beforeyoufly/genera.py

Dati:
    dati/passaporti.json   regole di validità del passaporto e testo dei visti (passaporto britannico) per 226 pagine FCDO (raccolta/passaporti.py)
    dati/aeroporti.json    regole sui liquidi lette a mano sulle pagine ufficiali degli aeroporti (ricontrollo: raccolta/liquidi.py)
    dati/ees_etias.json    frasi ufficiali su EES ed ETIAS (raccolta/eesetias.py)
    dati/bagagli.json      misure del bagaglio a mano lette sulle pagine ufficiali delle compagnie, regola UE (ricontrollo: raccolta/bagagli.py)
    dati/affiliati.json    riquadro affiliati (vuoto finché non ci sono URL)

Il controllo del passaporto gira nel browser (JS in pagina, nessuno script esterno). La stessa logica è scritta qui in Python
(verifica_passaporto) per gli esempi e per verifica.py, che confronta Python e JS su casi fatti a mano e casuali.
"""
import json
import re
import shutil
import unicodedata
from datetime import date, timedelta
from html import escape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
URL_SITO = "https://before-you-fly.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti): non rimuoverlo

ALTRI_SITI = [  # blocco "Other useful tools for your trip" in fondo a ogni pagina (URL dai genera.py dei rispettivi siti)
    ("https://italy-strikes-today.netlify.app/", "Italy Strikes Today", "Transport strikes in Italy today and tomorrow, from the official register"),
    ("https://tourist-tax-calculator.netlify.app/", "Tourist Tax Calculator", "City tax per night in 200+ European destinations"),
    ("https://visa-income-checker.netlify.app/", "Visa Income Checker", "Income requirements and refusal rates for visas"),
    ("https://cruise-health-scores.netlify.app/", "Cruise Health Scores", "CDC sanitation scores of every cruise ship"),
]
ALTRI_SITI_IT = [  # lo stesso blocco nelle pagine italiane (it/documenti/)
    ("https://italy-strikes-today.netlify.app/it/", "Italy Strikes Today", "Scioperi dei trasporti in Italia oggi e domani, dal registro ufficiale"),
    ("https://tourist-tax-calculator.netlify.app/", "Tourist Tax Calculator", "Tassa di soggiorno per notte in oltre 200 destinazioni europee"),
    ("https://visa-income-checker.netlify.app/", "Visa Income Checker", "Requisiti di reddito e tassi di rifiuto dei visti"),
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
NOME = "Before You Fly"
ANNO = 2026
OGGI = date.today()

PASS = json.loads((DATI / "passaporti.json").read_text(encoding="utf-8"))
AER = json.loads((DATI / "aeroporti.json").read_text(encoding="utf-8"))
EES = json.loads((DATI / "ees_etias.json").read_text(encoding="utf-8"))
AFFILIATI = json.loads((DATI / "affiliati.json").read_text(encoding="utf-8")) if (DATI / "affiliati.json").exists() else {}
CAMBI_PASS = json.loads((DATI / "passaporti_cambi.json").read_text(encoding="utf-8")) if (DATI / "passaporti_cambi.json").exists() else {"cambi": []}

PAESI = [p for p in PASS["paesi"] if p["testo"]]  # con testo ufficiale da mostrare (Antartide: sezione vuota, niente pagina)
SENZA_PAGINA = [p for p in PASS["paesi"] if not p["testo"]]
MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
OGL = "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"
URLS = []


# ---------------------------------------------------------------- utilità
def data_lunga(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {MESI[d.month - 1]} {d.year}"


def piu_mesi(iso, m):
    """Stessa data m mesi dopo (o prima, se m < 0); giorno ridotto all'ultimo del mese se non esiste. Uguale nel JS."""
    y, mo, d = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
    mo += m
    y += (mo - 1) // 12
    mo = (mo - 1) % 12 + 1
    ultimo = [31, 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mo - 1]
    return f"{y:04d}-{mo:02d}-{min(d, ultimo):02d}"


LIMITE_TITOLO = 65
LIMITE_DESCRIZIONE = 160


def scegli(candidati, limite):
    """Il primo candidato che sta nel limite; se nessuno ci sta, l'ultimo (il più corto previsto)."""
    for c in candidati:
        if len(c) <= limite:
            return c
    return candidati[-1]


def piu_giorni(iso, n):
    return (date.fromisoformat(iso) + timedelta(days=n)).isoformat()


def giorni(a, b):
    """Giorni da a a b (b - a)."""
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


# ---------------------------------------------------------------- motore del controllo passaporto (uguale al JS)
def verifica_passaporto(R, emissione, scadenza, arrivo, partenza):
    """R = regola (dict con 'condizioni', 'emissione_anni') oppure None.
    Ritorna {'esito': 'ok'|'no'|'manuale'|'errore', 'controlli': [...], 'margine', 'stretto', 'scade_prima', 'errore'}."""
    out = {"esito": "", "controlli": [], "margine": None, "stretto": False, "scade_prima": False, "errore": ""}
    if not R:
        out["esito"] = "manuale"
        return out
    if not (scadenza and arrivo and partenza):
        out.update(esito="errore", errore="dates")
        return out
    if partenza < arrivo:
        out.update(esito="errore", errore="order")
        return out
    if R.get("emissione_anni"):
        if not emissione:
            out.update(esito="errore", errore="issue")
            return out
        if emissione > arrivo or emissione > scadenza:
            out.update(esito="errore", errore="issue_order")
            return out
    margini = []
    for c in R["condizioni"]:
        base = arrivo if c["base"] == "arrivo" else partenza
        soglia = piu_mesi(base, c["n"]) if c["u"] == "m" else piu_giorni(base, c["n"])
        minima = soglia if c["op"] == ">=" else piu_giorni(soglia, 1)
        m = giorni(minima, scadenza)
        out["controlli"].append({"tipo": "scadenza", "base": c["base"], "minima": minima, "ok": m >= 0, "margine": m})
        margini.append(m)
    if R.get("emissione_anni"):
        limite = piu_mesi(arrivo, -12 * R["emissione_anni"])
        minima = piu_giorni(limite, 1)  # "less than 10 years before the date you arrive"
        m = giorni(minima, emissione)
        out["controlli"].append({"tipo": "emissione", "base": "arrivo", "minima": minima, "ok": m >= 0, "margine": m})
        margini.append(m)
    out["margine"] = min(margini)
    out["scade_prima"] = scadenza < partenza
    # mai "ok" se il passaporto scade prima della partenza (anche quando la regola conta dal giorno di arrivo)
    out["esito"] = "ok" if all(x["ok"] for x in out["controlli"]) and not out["scade_prima"] else "no"
    out["stretto"] = out["esito"] == "ok" and out["margine"] < 7
    return out


MOTORE_JS = r"""
function bfD(iso){var p=iso.split('-');return Date.UTC(+p[0],+p[1]-1,+p[2])/864e5;}
function bfI(n){return new Date(Math.round(n)*864e5).toISOString().slice(0,10);}
function bfPad(n,l){var s=String(n);while(s.length<l)s='0'+s;return s;}
function bfPiuMesi(iso,m){var y=+iso.slice(0,4),mo=+iso.slice(5,7)+m,d=+iso.slice(8,10);y+=Math.floor((mo-1)/12);mo=((mo-1)%12+12)%12+1;
  var bis=(y%4===0&&(y%100!==0||y%400===0));var ult=[31,bis?29:28,31,30,31,30,31,31,30,31,30,31][mo-1];return bfPad(y,4)+'-'+bfPad(mo,2)+'-'+bfPad(Math.min(d,ult),2);}
function bfPiuGiorni(iso,n){return bfI(bfD(iso)+n);}
function bfGiorni(a,b){return Math.round(bfD(b)-bfD(a));}
function verificaPassaporto(R,em,sc,ar,pa){
  var out={esito:'',controlli:[],margine:null,stretto:false,scade_prima:false,errore:''};
  if(!R){out.esito='manuale';return out;}
  if(!(sc&&ar&&pa)){out.esito='errore';out.errore='dates';return out;}
  if(pa<ar){out.esito='errore';out.errore='order';return out;}
  if(R.emissione_anni){if(!em){out.esito='errore';out.errore='issue';return out;}
    if(em>ar||em>sc){out.esito='errore';out.errore='issue_order';return out;}}
  var mm=[];
  R.condizioni.forEach(function(c){var base=c.base==='arrivo'?ar:pa;var s=c.u==='m'?bfPiuMesi(base,c.n):bfPiuGiorni(base,c.n);
    var minima=c.op==='>='?s:bfPiuGiorni(s,1);var m=bfGiorni(minima,sc);out.controlli.push({tipo:'scadenza',base:c.base,minima:minima,ok:m>=0,margine:m});mm.push(m);});
  if(R.emissione_anni){var lim=bfPiuMesi(ar,-12*R.emissione_anni);var mi=bfPiuGiorni(lim,1);var m2=bfGiorni(mi,em);
    out.controlli.push({tipo:'emissione',base:'arrivo',minima:mi,ok:m2>=0,margine:m2});mm.push(m2);}
  out.margine=Math.min.apply(null,mm);out.scade_prima=sc<pa;out.esito=(out.controlli.every(function(x){return x.ok;})&&!out.scade_prima)?'ok':'no';
  out.stretto=out.esito==='ok'&&out.margine<7;return out;}
"""

APP_JS = r"""
(function(){
  var MESI=['January','February','March','April','May','June','July','August','September','October','November','December'];
  function lunga(iso){var p=iso.split('-');return (+p[2])+' '+MESI[+p[1]-1]+' '+p[0];}
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function pl(n,w){return n+' '+w+(n===1?'':'s');}
  function citaz(lista){return lista.map(function(x){return '<blockquote class="cit"><p>'+esc(x)+'</p></blockquote>';}).join('');}
  function monta(box){
    var D=JSON.parse(document.getElementById(box.dataset.dati).textContent);var f=box.querySelector('form');
    var q=function(n){return f.querySelector('[name='+n+']');};var sel=q('paese');
    if(sel&&D.length>1){sel.innerHTML='<option value="">Choose a destination…</option>'+D.map(function(P,i){return '<option value="'+i+'">'+esc(P.n)+'</option>';}).join('');}
    function cur(){return D.length===1?D[0]:(sel.value===''?null:D[+sel.value]);}
    function etichette(R){var luogo=R&&R.luogo_uscita;var sch=R&&R.schengen;
      f.querySelector('[data-lab=arrivo]').textContent=sch?'Date you first enter the Schengen area':'Date you arrive';
      f.querySelector('[data-lab=partenza]').textContent=luogo?('Date you leave '+luogo+(sch?' (last Schengen country)':'')):'Date you leave';
      box.querySelector('[data-nota-schengen]').hidden=!sch;}
    function aggiorna(){
      var P=cur();var out=box.querySelector('[data-out]');var em=f.querySelector('[data-campo=emissione]');
      var R=P&&P.r;em.hidden=!(R&&R.emissione_anni);etichette(R);
      if(!P){out.innerHTML='<p class="small" style="margin:0">Choose a destination and enter your dates.</p>';return;}
      var link=box.dataset.link?'<p class="small" style="margin:8px 0 0"><a href="'+esc(box.dataset.link+P.s)+'/">Read the full official FCDO text for '+esc(P.n)+'</a></p>':'';
      var testo='<p class="small" style="margin:8px 0 0">Official FCDO text:</p>'+citaz(P.t);
      var extra=(P.a.length?'<p class="small" style="margin:8px 0 0"><strong>The FCDO also says:</strong></p>'+citaz(P.a):'')+
        (P.o.length?'<p class="small" style="margin:8px 0 0"><strong>Different rules for other cases (FCDO):</strong></p>'+citaz(P.o):'');
      if(!R){out.innerHTML='<div class="esito manuale"><strong>No automatic check for this destination.</strong> The FCDO text is not a validity period we turn into a date calculation. Read it word for word:</div>'+
        testo+extra+link;return;}
      var o=verificaPassaporto(R,q('emissione').value,q('scadenza').value,q('arrivo').value,q('partenza').value);
      if(o.esito==='errore'){var msg={dates:'Enter your passport expiry date, the date you arrive and the date you leave.',order:'The date you leave must be on or after the date you arrive.',
        issue:'This destination also has a rule on the passport issue date: enter the date of issue.',issue_order:'The issue date must be before the date you arrive and before the expiry date.'}[o.errore];
        out.innerHTML='<p class="small" style="margin:0">'+msg+'</p>'+extra+link;return;}
      var nome=R.consiglio?'the FCDO advice':'the rule as stated by the FCDO';var h;
      function ic(n){return '<svg class="ico" aria-hidden="true" focusable="false"><use href="#i-'+n+'"/></svg>';}
      if(o.scade_prima)h='<div class="esito no">'+ic('x')+'<strong>Your passport expires before you leave: it will not be valid for your whole stay.</strong></div><ul>';
      else h='<div class="esito '+(o.esito==='ok'?'si':'no')+'">'+ic(o.esito==='ok'?'check':'x')+'<strong>'+(o.esito==='ok'?'Your dates meet '+nome:'Your dates do NOT meet '+nome)+'</strong></div><ul>';
      if(o.scade_prima)h+='<li class="ko"><span class="m">✗</span> Your passport expires on <strong>'+lunga(q('scadenza').value)+'</strong>, before the day you leave ('+lunga(q('partenza').value)+').</li>';
      o.controlli.forEach(function(c){
        if(c.tipo==='scadenza')h+='<li class="'+(c.ok?'ok':'ko')+'"><span class="m">'+(c.ok?'✓':'✗')+'</span> Expiry date needed: on or after <strong>'+lunga(c.minima)+'</strong> ('+(c.base==='arrivo'?'counted from the day you arrive':'counted from the day you leave')+'). '+
          (c.ok?pl(c.margine,'day')+' to spare.':'Yours is '+pl(-c.margine,'day')+' short.')+'</li>';
        else h+='<li class="'+(c.ok?'ok':'ko')+'"><span class="m">'+(c.ok?'✓':'✗')+'</span> Date of issue needed: on or after <strong>'+lunga(c.minima)+'</strong> ('+esc(R.emissione_testo||'')+'). '+(c.ok?'':'Yours is '+pl(-c.margine,'day')+' too early.')+'</li>';});
      h+='</ul>';
      if(o.stretto)h+='<p class="small">Only just: less than a week to spare. Airlines and border officials may count dates differently. Check with your airline.</p>';
      out.innerHTML=h+extra+testo+link;}
    f.addEventListener('input',aggiorna);f.addEventListener('change',aggiorna);f.addEventListener('submit',function(e){e.preventDefault();});aggiorna();}
  document.querySelectorAll('[data-checker]').forEach(monta);
  document.querySelectorAll('[data-filtro]').forEach(function(inp){var lista=document.getElementById(inp.dataset.filtro);
    inp.addEventListener('input',function(){var v=inp.value.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
      lista.querySelectorAll('[data-voce]').forEach(function(a){var t=a.textContent.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');a.hidden=!!v&&t.indexOf(v)<0;});});});
})();
"""

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

CSS = """
@font-face{font-family:"Outfit";font-style:normal;font-weight:700;font-display:swap;src:url(/assets/fonts/outfit-700.woff2) format("woff2")}
@font-face{font-family:"DM Mono";font-style:normal;font-weight:400;font-display:swap;src:url(/assets/fonts/dm-mono-400.woff2) format("woff2")}
:root{--bg:#F2F3F5;--card:#FFFFFF;--ink:#101418;--ink-2:#39414B;--ink-3:#58616C;--line:#DADDE3;--line-2:#C4C9D1;
--board:#14181D;--board-2:#1E242B;--on-board:#F2F4F7;--on-board-2:#AFB7C2;--sign:#FFC72C;--sign-ink:#14181D;
--accent:#0B5BD3;--accent-h:#0848A8;--on-accent:#FFFFFF;--accent-2:#E7EFFC;
--ok:#126B41;--ok-2:#E3F4EA;--no:#AE2828;--no-2:#FCE8E8;--warn:#8A4B00;--warn-2:#FFF1DC;--mute:#EEF0F3;
--sh-1:0 1px 2px rgba(16,20,24,.06),0 1px 1px rgba(16,20,24,.04);--sh-2:0 22px 44px -22px rgba(16,20,24,.4),0 2px 8px rgba(16,20,24,.06);
--r:14px;--r-s:10px;--head:"Outfit","Avenir Next","Segoe UI",system-ui,sans-serif;--mono:"DM Mono",ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0B0D10;--card:#15191E;--ink:#EEF1F4;--ink-2:#C3C9D1;--ink-3:#98A1AC;--line:#262C34;--line-2:#363E49;
--board:#050608;--board-2:#12161B;--on-board:#EEF1F4;--on-board-2:#A3ACB8;--accent:#86B6FF;--accent-h:#AFCDFF;--on-accent:#0B0D10;--accent-2:#14233D;
--ok:#7FD9A6;--ok-2:#12301F;--no:#FF9F9F;--no-2:#3A1B1D;--warn:#FFB867;--warn-2:#33250F;--mute:#1B2027;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 22px 44px -22px rgba(0,0,0,.85),0 2px 8px rgba(0,0,0,.4)}}
:root[data-theme="dark"]{--bg:#0B0D10;--card:#15191E;--ink:#EEF1F4;--ink-2:#C3C9D1;--ink-3:#98A1AC;--line:#262C34;--line-2:#363E49;
--board:#050608;--board-2:#12161B;--on-board:#EEF1F4;--on-board-2:#A3ACB8;--accent:#86B6FF;--accent-h:#AFCDFF;--on-accent:#0B0D10;--accent-2:#14233D;
--ok:#7FD9A6;--ok-2:#12301F;--no:#FF9F9F;--no-2:#3A1B1D;--warn:#FFB867;--warn-2:#33250F;--mute:#1B2027;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 22px 44px -22px rgba(0,0,0,.85),0 2px 8px rgba(0,0,0,.4)}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;font-size:17px;line-height:1.6;overflow-wrap:break-word}
a{color:var(--accent);text-underline-offset:2px;text-decoration-thickness:1px}
a:hover{color:var(--accent-h)}
:focus-visible{outline:3px solid var(--sign);outline-offset:2px;border-radius:4px;box-shadow:0 0 0 6px rgba(20,24,29,.85)}
.skip{position:absolute;left:-9999px;top:8px;background:var(--sign);color:var(--sign-ink);padding:8px 14px;border-radius:8px;z-index:50;font-weight:700}
.skip:focus{left:12px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.ico{width:1.15em;height:1.15em;flex:none;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;vertical-align:-.2em}
.wrap{max-width:1040px;margin:0 auto;padding:0 16px}
header.top{background:var(--board);color:var(--on-board);position:relative;z-index:20}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:64px}
.logo{display:flex;align-items:center;gap:11px;font-family:var(--head);font-weight:700;font-size:1.22rem;color:var(--on-board);text-decoration:none;white-space:nowrap;letter-spacing:-.01em}
.logo:hover{color:#fff}
.logo svg{width:36px;height:36px;flex:none}
.logo b{color:var(--sign);font-weight:inherit}
nav.menu{display:flex;gap:2px;font-size:.9rem}
nav.menu a{display:flex;align-items:center;gap:6px;color:var(--on-board-2);text-decoration:none;padding:8px 9px;border-radius:8px;white-space:nowrap}
nav.menu a .ico{color:var(--sign)}
nav.menu a:hover,nav.menu a[aria-current]{color:#fff;background:rgba(255,255,255,.08)}
.nav-m{display:none}
.nav-m summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:8px;font-weight:700;font-size:.95rem;padding:9px 14px;border-radius:10px;background:var(--sign);color:var(--sign-ink);min-height:44px}
.nav-m summary::-webkit-details-marker{display:none}
.nav-m nav{position:absolute;left:16px;right:16px;top:calc(100% + 4px);background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-2);padding:8px;display:grid}
.nav-m nav a{display:flex;align-items:center;gap:10px;padding:12px 14px;border-radius:8px;color:var(--ink);text-decoration:none;font-weight:600}
.nav-m nav a .ico{color:var(--accent)}
.nav-m nav a:hover{background:var(--accent-2)}
.band{background:linear-gradient(180deg,var(--board) 0,var(--board-2) 100%);color:var(--on-board);border-bottom:1px solid var(--line)}
.band-in{padding-top:34px;padding-bottom:36px}
.band .hero{padding:0;max-width:780px}
.eyebrow,.band h1 .h1-a{font-family:var(--mono);font-size:.82rem;font-weight:400;letter-spacing:.14em;text-transform:uppercase}
.hero{padding:24px 0 4px}
h1,h2,h3{font-family:var(--head);font-weight:700}
h1{font-size:clamp(1.7rem,4.8vw,2.55rem);line-height:1.1;letter-spacing:-.02em;margin:0 0 10px;text-wrap:balance}
h1 .h1-a{display:block}
h1 .h1-b{display:block;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-weight:600;font-size:clamp(1rem,2.4vw,1.15rem);color:var(--ink-2);letter-spacing:0;margin-top:8px;line-height:1.35}
h1 .h1-b::first-letter{text-transform:uppercase}
.band h1 .h1-a{display:inline-flex;align-items:center;gap:10px;color:var(--sign);margin-bottom:14px}
.band h1 .h1-a::before{content:"";width:22px;height:3px;background:var(--sign)}
.band h1 .h1-b{display:block;font-family:var(--head);font-weight:700;margin-top:0;color:#fff;font-size:clamp(1.9rem,5.4vw,3rem);line-height:1.06;letter-spacing:-.025em}
.band h1 .h1-b::first-letter{text-transform:uppercase}
.sub{font-size:1.1rem;color:var(--on-board-2);margin:14px 0 0;max-width:640px;text-wrap:balance}
.tiles{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:26px 0 0;padding:0;list-style:none}
.tiles li{display:flex}
.tiles a{flex:1;display:grid;grid-template-columns:auto 1fr;grid-template-rows:auto 1fr;gap:10px 14px;align-items:center;align-content:start;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:var(--r);padding:14px 16px;color:var(--on-board);text-decoration:none;min-height:100%;transition:background .15s,border-color .15s}
.tiles a:hover{background:rgba(255,255,255,.1);border-color:var(--sign)}
.tiles .sq{display:grid;place-items:center;width:48px;height:48px;border-radius:10px;background:var(--sign);color:var(--sign-ink)}
.tiles .sq .ico{width:28px;height:28px;stroke-width:2.2}
.tiles h2{font-size:1.12rem;line-height:1.2;margin:0;color:var(--on-board)}
.tiles h2::before,.band-h2::before{display:none}
.band-h2{color:#fff;font-size:1.2rem;margin:30px 0 0}
.band-h2+.checker{margin-top:12px}
.tiles small{grid-column:1/-1;align-self:start;font-size:.86rem;color:var(--on-board-2);line-height:1.45;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}
.scope{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin:14px 0 0;font-size:.95rem;color:var(--on-board-2)}
.scope .pill{display:inline-flex;align-items:center;gap:8px;background:var(--sign);color:var(--sign-ink);font-weight:700;border-radius:999px;padding:5px 14px 5px 10px;font-size:.92rem;line-height:1.3}
.scope .pill .ico{width:18px;height:18px;stroke-width:2.2}
.trust{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.88rem;color:var(--on-board-2);margin:18px 0 0}
.trust span{display:inline-flex;align-items:center;gap:7px}
.trust .ico{color:var(--sign)}
h2{font-size:1.45rem;line-height:1.22;margin:40px 0 14px;letter-spacing:-.01em;display:flex;align-items:baseline;gap:10px}
main h2::before{content:"";flex:none;width:10px;height:10px;border-radius:2px;background:var(--sign);transform:translateY(-1px)}
h3{font-size:1.1rem;margin:22px 0 8px}
.lead{font-size:1.04rem;color:var(--ink-2);max-width:760px;margin:0 0 8px}
.small{font-size:.88rem;color:var(--ink-3)}
.avviso{position:relative;background:var(--warn-2);border:1px solid color-mix(in srgb,var(--warn) 25%,transparent);padding:12px 16px 12px 46px;border-radius:var(--r-s);font-size:.93rem;margin:18px 0;color:var(--ink)}
.avviso::before{content:"";position:absolute;left:16px;top:14px;width:20px;height:20px;background:var(--warn);-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cpath d='M12 16v-4M12 8h.01'/%3E%3C/svg%3E") center/contain no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cpath d='M12 16v-4M12 8h.01'/%3E%3C/svg%3E") center/contain no-repeat}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:20px;min-width:0;box-shadow:var(--sh-1)}
.summary{padding:0;overflow:hidden;margin-top:8px;box-shadow:var(--sh-2)}
.s-top{display:flex;align-items:center;gap:10px;background:var(--board);color:var(--on-board-2);padding:9px 18px;font-family:var(--mono);font-size:.78rem;letter-spacing:.1em;text-transform:uppercase}
.s-top .sq{display:grid;place-items:center;width:26px;height:26px;border-radius:6px;background:var(--sign);color:var(--sign-ink)}
.s-top .sq .ico{width:16px;height:16px;stroke-width:2.3}
.s-top span:last-child{margin-left:auto}
.s-body{padding:18px 20px}
.s-body .lead{font-size:.95rem;margin:10px 0 0}
.cifra{font-size:1.02rem;margin:0 0 4px;color:var(--ink-2)}
.cifra strong{display:block;font-family:var(--head);font-size:clamp(1.3rem,3.6vw,1.7rem);line-height:1.25;color:var(--ink);letter-spacing:-.01em;margin-top:4px}
.cifra .badge{vertical-align:middle;margin-left:4px}
.badge{display:inline-flex;align-items:center;gap:6px;font-family:var(--mono);font-weight:400;border-radius:6px;padding:3px 10px;font-size:.82rem;white-space:nowrap;letter-spacing:.02em;border:1px solid transparent}
.b-2l{background:var(--ok-2);color:var(--ok);border-color:color-mix(in srgb,var(--ok) 35%,transparent)}
.b-100ml{background:var(--mute);color:var(--ink);border-color:var(--line-2)}
.b-dipende,.b-contraddice{background:var(--warn-2);color:var(--warn);border-color:color-mix(in srgb,var(--warn) 35%,transparent)}
.fonte{font-size:.84rem;color:var(--ink-3);margin:8px 0 0;overflow-wrap:anywhere}
.fonte a{color:var(--ink-2)}
blockquote.cit{position:relative;margin:12px 0;padding:14px 16px 14px 46px;border:1px solid var(--line);border-left:4px solid var(--sign);background:var(--card);border-radius:0 var(--r-s) var(--r-s) 0;font-size:.97rem;box-shadow:var(--sh-1)}
blockquote.cit::before{content:"\\201C";position:absolute;left:14px;top:4px;font-family:var(--head);font-size:2.2rem;line-height:1;color:var(--ink-3)}
blockquote.cit p{margin:0 0 8px}blockquote.cit p:last-child{margin:0}
blockquote.cit ul{margin:0 0 8px;padding-left:20px}
.checker{padding:0;overflow:hidden;box-shadow:var(--sh-2);border-color:var(--line-2)}
.band .checker{margin-top:26px}
.band .card,.band .checker,.band .risultato{color:var(--ink)}
.band .card a:not(.btn){color:var(--accent)}
.checker-h{display:flex;align-items:center;gap:10px;background:var(--sign);color:var(--sign-ink);padding:10px 18px;font-family:var(--mono);font-size:.8rem;letter-spacing:.12em;text-transform:uppercase}
.checker-h .ico{width:18px;height:18px}
.checker-b{padding:20px}
.calc{display:grid;gap:12px}
.calc .campi{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.calc .campi:has([data-campo=emissione]:not([hidden])){grid-template-columns:repeat(4,minmax(0,1fr))}
.calc label{display:grid;gap:6px;align-content:end;font-weight:600;font-size:.9rem;line-height:1.35;min-width:0;color:var(--ink-2)}
.calc .lt{display:flex;align-items:center;gap:7px}
.calc .lt .ico{color:var(--accent);width:1.05em;height:1.05em}
.calc input,.calc select,.cerca,.form input,.form select,.form textarea{font:inherit;font-size:1rem;color:var(--ink);background:var(--card);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:10px 12px;width:100%;min-width:0;min-height:46px;transition:border-color .15s,box-shadow .15s}
.calc input:hover,.calc select:hover{border-color:var(--ink-3)}
.calc input:focus,.calc select:focus,.cerca:focus,.form input:focus,.form textarea:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 20%,transparent)}
.calc .pieno{grid-column:1/-1}
.risultato{background:var(--mute);border:1px solid var(--line);border-radius:var(--r-s);padding:16px;min-width:0;overflow-wrap:anywhere}
.risultato>ul{list-style:none;margin:12px 0 0;padding:0;display:grid;gap:8px;font-size:.93rem}
.risultato>ul li{background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:10px 12px}
.risultato .m{font-weight:700;margin-right:4px}
.risultato li.ok .m{color:var(--ok)}.risultato li.ko .m{color:var(--no)}
.esito{display:flex;align-items:center;gap:12px;border-radius:var(--r-s);padding:12px 14px;font-size:1.02rem;border:1px solid transparent}
.esito>.ico{width:30px;height:30px;stroke-width:2.2}
.esito strong{font-family:var(--head);font-size:1.12rem;line-height:1.3}
.esito.si{background:var(--ok-2);color:var(--ok);border-color:color-mix(in srgb,var(--ok) 35%,transparent)}
.esito.no{background:var(--no-2);color:var(--no);border-color:color-mix(in srgb,var(--no) 35%,transparent)}
.esito.manuale{background:var(--warn-2);color:var(--warn);border-color:color-mix(in srgb,var(--warn) 35%,transparent);display:block}
.esito.manuale strong{font-size:1rem}
.tab{overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid var(--line);border-radius:var(--r);background:var(--card);box-shadow:var(--sh-1)}
table{border-collapse:collapse;width:100%;font-size:.92rem}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:var(--board);color:var(--on-board-2);font-family:var(--mono);font-weight:400;font-size:.76rem;letter-spacing:.08em;text-transform:uppercase}
td .small{font-family:var(--mono);font-size:.8rem}
tbody tr:hover td{background:color-mix(in srgb,var(--accent-2) 50%,transparent)}
tr:last-child td{border-bottom:0}
@media (max-width:640px){.tab td,.tab th{min-width:120px}.tab td:first-child,.tab th:first-child{min-width:150px}
.tab-e thead{display:none}.tab-e tr{display:grid;grid-template-columns:1fr 1fr;gap:6px 14px;padding:12px 14px;border-bottom:1px solid var(--line)}
.tab-e tr:last-child{border-bottom:0}.tab-e td,.tab-e td:first-child{min-width:0;padding:0;border:0}.tab-e td:first-child{grid-column:1/-1;font-weight:600}
.tab-e td:nth-child(4){grid-column:1/-1;font-size:.8rem;color:var(--ink-3)}
.tab-e td[data-l]::before{content:attr(data-l);display:block;font-family:var(--mono);font-size:.7rem;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3)}}
.cifra .nota-s{display:block;font-size:.9rem;color:var(--ink-3);margin-top:2px}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:10px}
.fatti-it{margin:0;display:grid;gap:10px}
.fatti-it>div{border-left:4px solid var(--line-2);background:var(--mute);border-radius:0 var(--r-s) var(--r-s) 0;padding:10px 14px}
.fatti-it>div.t-ok{border-left-color:var(--ok);background:var(--ok-2)}
.fatti-it>div.t-no{border-left-color:var(--no);background:var(--no-2)}
.fatti-it>div.t-warn{border-left-color:var(--warn);background:var(--warn-2)}
.fatti-it dt{font-family:var(--mono);font-size:.74rem;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3)}
.fatti-it dd{margin:3px 0 0;font-family:var(--head);font-size:clamp(1.08rem,2.6vw,1.3rem);line-height:1.3;color:var(--ink);font-weight:700}
.fatti-it dd a{font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;font-size:.86rem;font-weight:400;white-space:nowrap;margin-left:6px}
.s-it span{white-space:nowrap}
.griglia.g-it{grid-template-columns:repeat(auto-fill,minmax(140px,1fr))}
.griglia a{display:block;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:12px 14px;text-decoration:none;color:var(--ink);font-weight:700;min-width:0;overflow-wrap:anywhere;box-shadow:var(--sh-1);transition:border-color .15s,box-shadow .15s,transform .15s}
.griglia a small{display:block;font-weight:400;color:var(--ink-3);font-size:.84rem;margin-top:2px;line-height:1.4}
.griglia a:hover{border-color:var(--accent);box-shadow:var(--sh-2);transform:translateY(-1px);color:var(--ink)}
.tre{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:18px}
.tre .card{position:relative;padding-top:18px}
.tre .card h2{margin-top:0;font-size:1.15rem}
.tre .card h2::before{display:none}
.tre .sq{display:grid;place-items:center;width:44px;height:44px;border-radius:10px;background:var(--sign);color:var(--sign-ink);margin-bottom:10px}
.stat{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 0;padding:0;list-style:none}
.stat li{background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:10px 14px;box-shadow:var(--sh-1);font-size:.9rem;color:var(--ink-2)}
.stat strong{display:block;font-family:var(--head);font-size:1.6rem;line-height:1.1;color:var(--ink)}
.cerca-box{position:relative}
.cerca-box .ico{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:var(--ink-3);pointer-events:none}
.cerca{padding-left:42px;margin:6px 0 12px}
.testo p,.testo li{max-width:760px}
.form{display:grid;gap:14px}
.form label{display:grid;gap:6px;font-weight:600;font-size:.95rem}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:400;font-size:.9rem;color:var(--ink-2)}
.form .check input{width:auto;min-height:0;margin-top:4px}
.btn{font:inherit;font-weight:700;background:var(--sign);color:var(--sign-ink);border:0;border-radius:var(--r-s);padding:12px 22px;cursor:pointer;min-height:46px}
.btn:hover{filter:brightness(.95)}
.btn:disabled{opacity:.6;cursor:wait}
.hp{position:absolute;left:-9999px}
.ok{background:var(--ok-2);border:1px solid var(--ok);padding:14px;border-radius:var(--r-s)}
.errore{color:var(--warn);font-weight:600}
.ad-slot:empty{display:none}
.b-gratis{background:var(--ok-2);color:var(--ok);border-color:color-mix(in srgb,var(--ok) 35%,transparent)}
.b-altre{background:var(--warn-2);color:var(--warn);border-color:color-mix(in srgb,var(--warn) 35%,transparent)}
.b-no{background:var(--no-2);color:var(--no);border-color:color-mix(in srgb,var(--no) 35%,transparent)}
.calc .campi-b{grid-template-columns:repeat(4,minmax(0,1fr))}
.risultato>ul.stat{display:flex;margin:6px 0 0}
.risultato h3{margin:16px 0 0;font-size:1rem}
.risultato h3.es-gratis{color:var(--ok)}.risultato h3.es-altre{color:var(--warn)}.risultato h3.es-no{color:var(--no)}
.risultato ul.esiti li .small{display:block;margin-top:2px}
.tab-b .badge{white-space:normal}
.risultato .stat li{padding:6px 10px;font-size:.84rem}.risultato .stat strong{font-size:1.25rem}
blockquote.cit{font-feature-settings:"calt" 0}
details.card>summary{cursor:pointer;min-height:44px;padding:6px 0;line-height:1.45}
.faq h3{margin-top:18px}
.altri-pass{display:flex;align-items:center;flex-wrap:wrap;gap:6px 10px;margin:14px 0 0;font-size:.95rem;color:var(--ink-2)}
.altri-pass .ico{color:var(--accent)}
.briciole{font-family:var(--mono);font-size:.8rem;color:var(--ink-3);margin-top:18px;letter-spacing:.02em}
.briciole a{color:var(--ink-3)}
footer{margin-top:64px;background:var(--board);color:var(--on-board-2);font-size:.88rem;padding:40px 0 34px;border-top:4px solid var(--sign)}
footer a{color:var(--on-board)}
footer a:hover{color:var(--sign)}
footer .f-grid{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:28px}
footer .logo{margin-bottom:12px}
footer p{margin:0 0 10px;max-width:660px}
footer strong{color:var(--on-board)}
footer ul{list-style:none;margin:0;padding:0;display:grid;gap:8px}
footer h2{font-family:var(--mono);font-weight:400;font-size:.76rem;letter-spacing:.14em;text-transform:uppercase;color:var(--sign);margin:4px 0 12px}
footer h2::before{display:none}
footer .f-base{border-top:1px solid rgba(255,255,255,.12);margin-top:24px;padding-top:16px;font-size:.82rem;max-width:none}
footer .f-altri{border-top:1px solid rgba(255,255,255,.12);margin-top:24px;padding-top:18px}
footer .f-altri h2{margin:0 0 10px}
footer .f-altri ul{gap:6px}
footer .f-altri li{max-width:660px}
footer .f-altri a{font-weight:600}
@media (max-width:860px){.tiles{grid-template-columns:1fr}.tre{grid-template-columns:1fr}.calc .campi,.calc .campi:has([data-campo=emissione]:not([hidden])){grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:480px){.calc .campi,.calc .campi:has([data-campo=emissione]:not([hidden])){grid-template-columns:1fr}}
@media (max-width:760px){nav.menu{display:none}.nav-m{display:block}header.top .wrap{min-height:60px}footer .f-grid{grid-template-columns:1fr}.band-in{padding-top:24px;padding-bottom:26px}.checker-b{padding:16px}
.tiles{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:20px}.tiles a{grid-template-columns:1fr;grid-template-rows:auto;justify-items:start;align-content:start;gap:8px;padding:12px;min-height:104px}.tiles .sq{width:40px;height:40px}.tiles .sq .ico{width:22px;height:22px}
.tiles h2{font-size:.95rem}.tiles small{display:none}.checker-h{letter-spacing:.06em;font-size:.74rem}.band-h2{margin-top:22px}}
@media (max-width:640px){.tab.tab-b thead{display:none}.tab.tab-b tr{display:block;padding:10px 14px;border-bottom:1px solid var(--line)}.tab.tab-b tr:last-child{border-bottom:0}
.tab.tab-b td,.tab.tab-b td:first-child{display:block;min-width:0;padding:2px 0;border:0}
.tab.tab-b td[data-l]::before{content:attr(data-l);display:block;font-family:var(--mono);font-size:.7rem;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);margin-top:6px}
.tab.tab-b td:first-child::before{margin-top:0}}
@media (max-width:480px){.calc .campi-b{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:1060px){nav.menu{display:none}.nav-m{display:block}}
.esito.manuale.e-srv{display:flex}.griglia.g-srv{grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}a.a-badge{text-decoration:none}a.a-badge:hover .badge,a.a-badge:focus-visible .badge{text-decoration:underline}
@media (max-width:640px){.tab.tab-srv tr{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:12px}.tab.tab-srv td:first-child{grid-column:1/-1}}
.b-muto{background:var(--mute);color:var(--ink-2);border-color:var(--line-2)}
.griglia.g-pat{grid-template-columns:repeat(auto-fill,minmax(260px,1fr));margin-top:16px}.griglia.g-pat a .ico{color:var(--accent);margin-right:4px}
.tab-pat td:nth-child(4){font-size:.9rem;color:var(--ink-2);min-width:16em}.tab-pat td:last-child{white-space:nowrap}
@media (max-width:640px){.tab.tab-pat tr{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:12px}.tab.tab-pat td:first-child,.tab.tab-pat td:nth-child(4){grid-column:1/-1}.tab-pat td:nth-child(4){min-width:0}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

ICONE = {
    "passport": '<rect x="4.5" y="2.5" width="15" height="19" rx="2"/><circle cx="12" cy="10" r="3.5"/><path d="M8.5 10h7M12 6.5c1 1 1.4 2.2 1.4 3.5s-.4 2.5-1.4 3.5c-1-1-1.4-2.2-1.4-3.5s.4-2.5 1.4-3.5zM9 17.5h6"/>',
    "bottle": '<path d="M9.5 2.5h5M10.5 2.5v3.3L8 9.2V20a1.5 1.5 0 0 0 1.5 1.5h5A1.5 1.5 0 0 0 16 20V9.2l-2.5-3.4V2.5"/><path d="M8 13h8M8 17h8"/>',
    "takeoff": '<path d="M2.5 21h19"/><path d="M4.2 13.6 6.7 16l4-1.1 9.3-2.6a1.9 1.9 0 0 0-1-3.7l-3.8 1L9.4 5.8l-2.1.6 2.9 4.7-3.6 1-2-1.7-1.5.4z"/>',
    "scan": '<path d="M3 8V5.5A2.5 2.5 0 0 1 5.5 3H8M16 3h2.5A2.5 2.5 0 0 1 21 5.5V8M21 16v2.5a2.5 2.5 0 0 1-2.5 2.5H16M8 21H5.5A2.5 2.5 0 0 1 3 18.5V16"/><circle cx="12" cy="10" r="3"/><path d="M7.5 17.5a4.5 4.5 0 0 1 9 0"/>',
    "calendar": '<rect x="3" y="4.5" width="18" height="17" rx="2.5"/><path d="M16 2.5v4M8 2.5v4M3 10h18"/>',
    "cal-in": '<rect x="3" y="4.5" width="18" height="17" rx="2.5"/><path d="M16 2.5v4M8 2.5v4M3 10h18"/><path d="M9 15.5h6M12.5 13l2.5 2.5-2.5 2.5"/>',
    "cal-out": '<rect x="3" y="4.5" width="18" height="17" rx="2.5"/><path d="M16 2.5v4M8 2.5v4M3 10h18"/><path d="M15 15.5H9M11.5 13 9 15.5l2.5 2.5"/>',
    "check": '<circle cx="12" cy="12" r="9.5"/><path d="M8 12.5l2.7 2.7L16 10"/>',
    "x": '<circle cx="12" cy="12" r="9.5"/><path d="M9 9l6 6M15 9l-6 6"/>',
    "alert": '<path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17h.01"/>',
    "shield": '<path d="M12 22s8-3.5 8-10V5.5L12 2.5 4 5.5V12c0 6.5 8 10 8 10z"/><path d="M8.5 12l2.5 2.5 4.5-4.5"/>',
    "search": '<circle cx="11" cy="11" r="7.5"/><path d="M21 21l-4.5-4.5"/>',
    "lock": '<rect x="4.5" y="10.5" width="15" height="11" rx="2"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "book": '<path d="M4 4.5A1.5 1.5 0 0 1 5.5 3H11v18H5.5A1.5 1.5 0 0 1 4 19.5zM20 4.5A1.5 1.5 0 0 0 18.5 3H13v18h5.5a1.5 1.5 0 0 0 1.5-1.5z"/>',
    "bag": '<rect x="4" y="7.5" width="16" height="12.5" rx="2.5"/><path d="M9 7.5V5a1.5 1.5 0 0 1 1.5-1.5h3A1.5 1.5 0 0 1 15 5v2.5M8 20v1.5M16 20v1.5M9 11.5v5M15 11.5v5"/>',
    "globe": '<circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19"/><path d="M12 2.5c2.6 2.6 4 6 4 9.5s-1.4 6.9-4 9.5c-2.6-2.6-4-6-4-9.5s1.4-6.9 4-9.5z"/>',
    "car": '<path d="M5 16.5V12l1.8-4.6A2 2 0 0 1 8.7 6h6.6a2 2 0 0 1 1.9 1.4L19 12v4.5"/><path d="M3.5 12h17v4.5h-17zM7 16.5V19M17 16.5V19"/><circle cx="7.5" cy="14.2" r=".9"/><circle cx="16.5" cy="14.2" r=".9"/>',
    "apps": '<rect x="3.5" y="3.5" width="7" height="7" rx="1.8"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.8"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.8"/><path d="M17 13.5v7M13.5 17h7"/>',
}


def ico(nome, cls="ico"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="#i-{nome}"/></svg>'


SPRITE = ('<svg xmlns="http://www.w3.org/2000/svg" style="display:none">' +
          "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONE.items()) + "</svg>")
# Marchio: cartello aeroportuale giallo con aereo in decollo (stesso disegno nel favicon e nell'immagine Open Graph)
_M = ('<rect width="40" height="40" rx="8" fill="#FFC72C"/>'
      '<path d="M8 31.5h24" stroke="#14181D" stroke-width="2.6" stroke-linecap="round"/>'
      '<path d="M8.6 21.2l3.6 3.4 5.8-1.6 13.4-3.7a2.7 2.7 0 0 0-1.4-5.3l-5.5 1.5-7.1-6.4-3 .9 4.2 6.8-5.2 1.4-2.9-2.5-2.2.6z" fill="#14181D"/>')
MARCHIO = f'<svg viewBox="0 0 40 40" aria-hidden="true" focusable="false">{_M}</svg>'
FAVICON = "data:image/svg+xml," + (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'>{_M}</svg>"
                                    .replace('"', "'").replace("#", "%23").replace("<", "%3C").replace(">", "%3E"))


def h1_diviso(testo):
    """H1 identico nel testo (per i motori di ricerca), diviso in due righe visive al primo ': '."""
    if ": " not in testo:
        return f"<h1>{escape(testo)}</h1>"
    a, b = testo.split(": ", 1)
    return f'<h1><span class="h1-a">{escape(a)}</span><span class="sr">: </span><span class="h1-b">{escape(b)}</span></h1>'


AD = '<div class="ad-slot" aria-hidden="true"></div>'
AVVISO_PASS = ('<p class="avviso"><strong>For British passport holders only.</strong> These are the rules published by the UK government (FCDO) for British '
               'citizens. If you hold another passport, check your own government\'s advice. The airline and the border officials of the destination '
               'decide whether you can travel or enter: this site is information, not legal advice.</p>')
AVVISO_LIQ = ('<p class="avviso"><strong>Rules can differ by terminal, checkpoint or lane and can change at short notice.</strong> We quote the airport\'s '
              'official page on the date shown. Check with the airport (and your airline) before you pack, and check the airport you fly home from: '
              'it may still have the 100 ml limit.</p>')


# ---------------------------------------------------------------- impaginazione
PIEDE_ESTERI = ""  # attribuzioni Canada/Australia nel piè di pagina (riempito da main() quando ci sono i dati)


def pagina(percorso, titolo, descrizione, corpo, briciole=None, indicizza=True, js="", assoluto=False, testata="", ld_extra=None, lingua="en"):
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
        bc = ('<nav class="briciole" aria-label="' + ("Percorso" if lingua == "it" else "Breadcrumb") + '"><a href="' + rel + '">Home</a>' +
              "".join(f' › <a href="{rel}{p}">{escape(n)}</a>' for n, p in briciole[:-1]) + f" › {escape(briciole[-1][0])}</nav>")
    ld += ld_extra or []
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    robots = "" if indicizza else '<meta name="robots" content="noindex">'
    canonico = f'<link rel="canonical" href="{url_pag}">' if indicizza else ""
    script = f"<script>{js or FORM_JS}</script>"
    it = lingua == "it"
    og_locale = '\n<meta property="og:locale" content="it_IT">' if it else ""
    if it:
        voci_menu = [(f"{IT_BASE}/", "passport", "Documenti e visti"), (f"{IT_BASE}/#metodo", "book", "Fonte e metodo"),
                     ("passport-validity/", "globe", "English (UK passport)")]
    else:
        voci_menu = [("passport-validity/", "passport", "Passport validity"), ("liquids/", "bottle", "Liquids by airport"), ("cabin-bags/", "bag", "Cabin bags"),
                     ("ees-etias/", "scan", "EES &amp; ETIAS"), (f"{SRV_BASE}/", "apps", "Apps by country"),
                     ("about/", "book", "Sources")]
    menu = "".join(f'<a href="{rel}{u}"' + (' aria-current="page"' if u == percorso else "") + f'>{ico(i)}{t}</a>' for u, i, t in voci_menu)
    piede = PIEDE_IT.replace("{rel}", rel) if it else f"""<footer><div class="wrap">
<div class="f-grid"><div>
<a class="logo" href="{rel}">{MARCHIO}<span>Before <b>You Fly</b></span></a>
<p><strong>{NOME}</strong> is an independent site, not affiliated with any government, airport or airline. Every rule is quoted from an official source, linked under it with the date we checked it.
<strong>Rules change: the airline, the airport and border officials have the final say.</strong> Nothing on this site is legal advice.</p>
<p>Passport validity rules: contains public sector information from the FCDO foreign travel advice on GOV.UK, licensed under the <a href="{OGL}" rel="noopener">Open Government Licence v3.0</a>.{PIEDE_ESTERI}</p>
</div><div>
<h2>Explore</h2>
<ul><li><a href="{rel}about/">About and sources</a></li><li><a href="{rel}contact/">Contact</a></li><li><a href="{rel}privacy.html">Privacy</a></li><li><a href="{rel}contact/?ref=spotted-a-change">Spotted a change? Tell us</a></li></ul>
</div></div>
{blocco_altri(ALTRI_SITI, "Other useful tools for your trip")}
<p class="f-base">Official sources only, quoted word for word.</p>
</div></footer>"""
    testo = f"""<!DOCTYPE html>
<html lang="{lingua}">
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
<meta property="og:image:alt" content="{NOME}: {"documenti e visti per chi viaggia con la cittadinanza italiana" if it else "passport validity, liquids rules by airport, cabin bag sizes, EES and ETIAS"}">{og_locale}
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#14181D">
<meta name="color-scheme" content="light dark">
{robots}
<link rel="icon" href="{FAVICON}">
<link rel="preload" href="/assets/fonts/outfit-700.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS}</style>
{ld_html}
</head>
<body>
{SPRITE}
<a class="skip" href="#main">{"Vai al contenuto" if it else "Skip to content"}</a>
<header class="top"><div class="wrap">
<a class="logo" href="{rel}">{MARCHIO}<span>Before <b>You Fly</b></span></a>
<nav class="menu" aria-label="Menu">{menu}</nav>
<details class="nav-m"><summary aria-label="{"Apri il menu" if it else "Open the menu"}">{ico("menu")}Menu</summary><nav aria-label="Menu">{menu}</nav></details>
</div></header>
<main id="main">
{testata}
<div class="wrap">
{bc}
{corpo}
</div>
</main>
{piede}
{script}
{SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")


def box_affiliati():
    """Riquadro affiliati: vuoto (non mostrato) finché dati/affiliati.json non ha URL."""
    voci = [v for k, v in AFFILIATI.items() if not k.startswith("_") and k != "bagagli" and isinstance(v, dict) and v.get("url")]
    if not voci:
        return ""
    righe = "".join(f'<li><a href="{escape(v["url"])}" rel="sponsored noopener" target="_blank">{escape(v["titolo"])}</a> '
                    f'<span class="small">{escape(v.get("nome", ""))} {escape(v["testo"])}</span></li>' for v in voci)
    return (f'<section class="card" style="margin-top:22px"><h2 style="margin-top:0">Before you go</h2><ul style="margin:0 0 8px;padding-left:20px">{righe}</ul>'
            '<p class="small" style="margin:0">Some of these are affiliate links: if you buy through them we may earn a small commission, at no extra cost to you.</p></section>')


def dati_json(id_, oggetto):
    return (f'<script type="application/json" id="{id_}">' +
            json.dumps(oggetto, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>")


# ---------------------------------------------------------------- passaporti: testi
def unita(n, u):
    if u == "m":
        return "1 month" if n == 1 else f"{n} months"
    return "1 day" if n == 1 else f"{n} days"


def sintesi_regola(R):
    """Riassunto in parole della regola riconosciuta (solo per le regole 'auto')."""
    if not R:
        return ""
    parti = []
    luogo = R.get("luogo_uscita")
    for c in R["condizioni"]:
        dove = f"leave {luogo}" if (luogo and c["base"] == "partenza") else ("arrive" if c["base"] == "arrivo" else "leave")
        if c["n"] == 0 and c["op"] == ">=":
            parti.append("valid for the whole stay (until the day you leave)")
        elif c["n"] == 0:
            parti.append("expiry date after the day you leave")
        else:
            q = "more than" if c["op"] == ">" else "at least"
            parti.append(f"{q} {unita(c['n'], c['u'])} after the day you {dove}")
    testo = " and ".join(parti)
    if R.get("emissione_anni"):
        testo = f"{R.get('emissione_testo') or 'issued less than 10 years before the date you arrive'}, and expiry date {testo}"
    return testo[0].upper() + testo[1:]


def breve_regola(R, P=None):
    """Etichetta corta per tabelle e liste."""
    if P is not None and P["slug"] == "ireland":
        return "No passport legally required (FCDO): check your carrier"
    if not R:
        return "Check the official text"
    parti = []
    for c in R["condizioni"]:
        if c["n"] == 0:
            parti.append("Valid for the whole stay" if c["op"] == ">=" else "Beyond departure")
        else:
            parti.append(f"{'>' if c['op'] == '>' else ''}{unita(c['n'], c['u'])} after {'arrival' if c['base'] == 'arrivo' else 'departure'}")
    s = " + ".join(parti)
    if R.get("emissione_anni"):
        if R.get("schengen"):
            s = "Schengen: " + s.replace("departure", "leaving the area") + " + 10-year issue rule"
        elif R.get("luogo_uscita"):
            s = f"{s.replace('departure', 'leaving ' + R['luogo_uscita'])} + issued within 10 years"
        else:
            s += " + 10-year issue rule"
    if R.get("consiglio"):
        s += " (FCDO advice)"
    return s


def blocchi_client(P):
    """Testo ufficiale da mostrare nel risultato: blocchi interi, separati (niente tagli a metà, niente frasi cucite)."""
    bb = P["testo"]
    if bb and bb[0]["t"] != "h3":
        out = []
        for b in bb:
            if b["t"] == "h3":
                break
            out.append(b["x"])
    else:
        out = [b["x"] for b in bb]
    return out[:12]


def dati_client(P):
    R = P["regola"]
    r = ({k: R.get(k) for k in ("condizioni", "emissione_anni", "schengen", "luogo_uscita", "emissione_testo", "consiglio")} if R else None)
    return {"s": P["slug"], "n": P["nome"], "r": r, "t": blocchi_client(P), "a": P.get("avvisi", []), "o": P.get("altre_regole", [])}


def testo_ufficiale(P):
    """Testo ufficiale FCDO parola per parola (paragrafi, elenchi, sottotitoli)."""
    h, lista = [], []
    for b in P["testo"]:
        if b["t"] == "li":
            lista.append(f"<li>{escape(b['x'])}</li>")
            continue
        if lista:
            h.append("<ul>" + "".join(lista) + "</ul>")
            lista = []
        if b["t"] == "h3":
            h.append(f"<p><strong>{escape(b['x'])}</strong></p>")
        else:
            h.append(f"<p>{escape(b['x'])}</p>")
    if lista:
        h.append("<ul>" + "".join(lista) + "</ul>")
    return '<blockquote class="cit">' + "".join(h) + "</blockquote>"


def fonte_pass(P):
    return (f'<p class="fonte">Official source: <a href="{escape(P["url_ingresso"])}" rel="noopener">GOV.UK – {escape(P["nome"])} travel advice, Entry requirements (FCDO)</a> · '
            f'page last updated {data_lunga(P["aggiornata"])} · checked on {data_lunga(PASS["controllato_il"])}</p>')


def modulo_checker(id_dati, con_paese, link=""):
    sel = f'<label class="pieno"><span class="lt">{ico("globe")}Destination</span><select name="paese"></select></label>' if con_paese else ""
    return f"""<div class="card checker" data-checker data-dati="{id_dati}" data-link="{escape(link)}">
<div class="checker-h">{ico("passport")}<span>Passport check · British passport</span></div>
<div class="checker-b">
<form class="calc" autocomplete="off">
<div class="campi">
{sel}
<label><span class="lt">{ico("calendar")}Passport expiry date</span><input type="date" name="scadenza"></label>
<label data-campo="emissione" hidden><span class="lt">{ico("calendar")}Passport date of issue</span><input type="date" name="emissione"></label>
<label><span class="lt">{ico("cal-in")}<span data-lab="arrivo">Date you arrive</span></span><input type="date" name="arrivo"></label>
<label><span class="lt">{ico("cal-out")}<span data-lab="partenza">Date you leave</span></span><input type="date" name="partenza"></label>
</div>
</form>
<p class="small" data-nota-schengen hidden style="margin:10px 0 0">Schengen rules count your whole trip in the Schengen area: if you visit several Schengen countries, enter the day you first enter the area and the day you leave the last Schengen country.</p>
<div class="risultato" data-out aria-live="polite" style="margin-top:14px"><noscript>Turn on JavaScript to use the checker. The official rule is quoted on this page.</noscript></div>
<p class="small" style="margin:12px 0 0">{ico("lock")} The check runs in your browser: your dates are not sent anywhere. It applies the FCDO sentence literally (for example “6 months” is counted as the same day of the month 6 months later).</p>
</div>
</div>"""


# ---------------------------------------------------------------- visti (sezione "Visa requirements" della pagina FCDO)
def visto(P):
    return P.get("visto") or {"testo": [], "sintesi": None, "titolo_sezione": None}


def blocchi_html(bb):
    """Blocchi FCDO parola per parola (paragrafi, elenchi, sottotitoli) dentro una citazione."""
    h, lista = [], []
    for b in bb:
        if b["t"] == "li":
            lista.append(f"<li>{escape(b['x'])}</li>")
            continue
        if lista:
            h.append("<ul>" + "".join(lista) + "</ul>")
            lista = []
        h.append(f"<p><strong>{escape(b['x'])}</strong></p>" if b["t"] == "h3" else f"<p>{escape(b['x'])}</p>")
    if lista:
        h.append("<ul>" + "".join(lista) + "</ul>")
    return '<blockquote class="cit">' + "".join(h) + "</blockquote>"


def visto_breve(P):
    """Etichetta per il riepilogo, la tabella e la descrizione: il riassunto riconosciuto o un rimando alla citazione."""
    V = visto(P)
    if V["sintesi"]:
        return V["sintesi"]
    return "read the FCDO visa text" if V["testo"] else "no visa section on the FCDO page"


def fonte_visto(P):
    return (f'<p class="fonte">Official source: <a href="{escape(P["url_ingresso"])}" rel="noopener">GOV.UK – {escape(P["nome"])} travel advice, Entry requirements (FCDO)</a>, '
            f'section “{escape(visto(P)["titolo_sezione"] or "Visa requirements")}” · page last updated {data_lunga(P["aggiornata"])} · checked on {data_lunga(PASS["controllato_il"])}</p>')


VISIBILI_VISTO = re.compile(r"^applying for|arrival card|customs form|declaration form|electronic travel|travel authori[sz]ation|nzeta|landing and departure", re.I)


def nota_ees(P):
    """Pagine Schengen: rimando allo stato di EES/ETIAS, con le frasi ufficiali della pagina EES (se ancora trovate)."""
    if visto(P).get("schema") != "schengen":
        return ""
    ees = any("fully operational" in f["frase"] for f in frasi_ees("ees"))
    etias = any("currently not in operation" in f["frase"] for f in frasi_ees("etias"))
    azione = any("You do not need to take any action before you arrive at the border" in g["frase"] for g in EES["govuk"]["frasi"] if g["trovata"])
    if not (ees and etias and azione):
        return '<p class="small">Entering the Schengen area: see <a href="../../ees-etias/">EES and ETIAS status</a> (official EU and GOV.UK statements).</p>'
    return ('<p class="small"><strong>Entering the Schengen area:</strong> the EU Entry/Exit System (EES) is fully operational (European Commission), '
            'so your fingerprints and photo may be registered at the border; GOV.UK says you do not need to take any action before you arrive. '
            f'ETIAS is not in operation yet. Details and sources: <a href="../../ees-etias/">EES and ETIAS status</a> (checked on {data_lunga(EES["controllato_il"])}).</p>')


def sezione_visto(P):
    V = visto(P)
    dom = f'<h2 id="visa">Do I need a visa for {escape(P["nome"])} with a British passport?</h2>'
    if not V["testo"]:
        return (dom + f'<p class="avviso">The FCDO entry requirements page for {escape(P["nome"])} had no “Visa requirements” section when we checked it on '
                f'{data_lunga(PASS["controllato_il"])}, so we have nothing to quote. Read the <a href="{escape(P["url"])}" rel="noopener">full FCDO travel advice on GOV.UK</a> '
                'or ask the embassy of the country before you travel.</p>')
    # visibile: il paragrafo iniziale e i sottotitoli su come chiedere il visto o l'autorizzazione e sui moduli da compilare
    # prima dell'arrivo ("Applying for ...", ETA, arrival card...); il resto nel riquadro apribile
    gruppi = []
    for b in V["testo"]:
        if b["t"] == "h3" or not gruppi:
            gruppi.append([])
        gruppi[-1].append(b)
    testa, resto = list(gruppi[0]), []
    for g in gruppi[1:]:
        (testa if g[0]["t"] == "h3" and VISIBILI_VISTO.search(g[0]["x"]) else resto).extend(g)
    if V["sintesi"]:
        breve = (f'<p class="cifra">In short: <strong>{escape(V["sintesi"])}.</strong></p>'
                 '<p class="small">Our one-line summary of the first FCDO sentence below, which matches a wording we recognise. It applies to British citizen passport holders; '
                 'read the full official text, which may add conditions.</p>')
    elif (V.get("motivo") or "").startswith(("The FCDO text describes an electronic", "The FCDO text also mentions")):
        breve = f'<p class="small">We quote the FCDO text word for word and do not summarise it. {escape(V["motivo"])}</p>'
    else:
        breve = ('<p class="small">We quote the FCDO text word for word and do not summarise it: its first sentence has conditions or a wording we do not turn into a one-line answer.</p>')
    altro = (f'<details class="card" style="margin-top:12px"><summary><strong>More from the FCDO visa section</strong> (extensions, border checks and other cases)</summary>{blocchi_html(resto)}</details>'
             if resto else "")
    return dom + breve + nota_ees(P) + blocchi_html(testa) + altro + fonte_visto(P)


def titoli_passaporto(P):
    n = P["nome"]
    return [f"{n} Visa & Passport Validity for British Passport Holders {ANNO}", f"{n} Visa & Passport Validity for British Citizens {ANNO}",
            f"{n} Visa & Passport Rules for UK Citizens {ANNO}", f"{n} Visa & Passport Rules {ANNO}", f"{n} Visa & Passport {ANNO}"]


def descrizioni_passaporto(P, sint):
    n, R = P["nome"], P["regola"]
    V = visto(P)
    vis = V["sintesi"] or ("The FCDO visa text is quoted word for word" if V["testo"] else "The FCDO page has no visa section")
    return [f"Do you need a visa for {n} with a British passport? {vis}. Passport validity: {sint}. Official FCDO text, with dates.",
            f"Do you need a visa for {n} with a British passport? {vis}. Plus the FCDO passport validity rule{' and a date checker' if R else ''}.",
            f"Do you need a visa for {n} with a British passport? Official FCDO visa and passport validity text, quoted with dates.",
            f"{n} visa and passport validity for British passport holders ({ANNO}): FCDO text quoted, with dates."]


# ---------------------------------------------------------------- pagine passaporto
def irlanda(P):
    """Irlanda: niente regola di validità; le due frasi FCDO su passaporto non obbligatorio e richieste dei vettori (se ancora presenti)."""
    tt = [b["x"] for b in P["testo"]]
    a = next((x for x in tt if "not legally required to show a passport" in x), None)
    b = next((x for x in tt if "airlines and ferry operators" in x), None)
    return (a, b) if a and b else None


def pagina_paese(P):
    rel = "../../"
    R = P["regola"]
    ie = irlanda(P) if P["slug"] == "ireland" else None
    if ie:
        cifra = (f'<p class="cifra"><strong>No passport is legally required for British nationals under the Common Travel Area, but your airline or ferry may require one.</strong> In the FCDO\'s words:</p>'
                 f'<blockquote class="cit"><p>{escape(ie[0])}</p></blockquote><blockquote class="cit"><p>{escape(ie[1])}</p></blockquote>')
        lead = f"What the UK government (FCDO) says about passports and ID for British nationals travelling to {escape(P['nome'])}, quoted word for word."
    elif R:
        tipo = "FCDO advice" if R.get("consiglio") else "FCDO rule"
        cifra = f'<p class="cifra">Passport validity ({tipo}): <strong>{escape(sintesi_regola(R))}</strong></p>'
        if R.get("consiglio"):
            cifra += '<p class="small">The FCDO words this as advice (“should” or “make sure”), not as a strict requirement: the full sentence is quoted below.</p>'
        lead = (f"Whether you need a visa and how long your British passport must be valid to enter {escape(P['nome'])}, as published by the UK Foreign, "
                "Commonwealth &amp; Development Office (FCDO), quoted word for word, with a checker for your dates.")
    else:
        cifra = (f'<p class="cifra"><strong>Read the official text below.</strong> {escape(P["motivo"] or "")} '
                 'We quote it word for word and do not summarise it.</p>')
        lead = (f"What the UK Foreign, Commonwealth &amp; Development Office (FCDO) says about visas and passport validity for British travellers to {escape(P['nome'])}, "
                "quoted word for word.")
    avvisi = ""
    if P["avvisi"]:
        avvisi += ("<h2>Also in the official text</h2>" + "".join(f'<blockquote class="cit"><p>{escape(a)}</p></blockquote>' for a in P["avvisi"]))
    if P.get("altre_regole"):
        avvisi += ("<h2>Different rules for other cases (official)</h2>" + "".join(f'<blockquote class="cit"><p>{escape(a)}</p></blockquote>' for a in P["altre_regole"]))
    pagine = (f'<p><strong>Blank pages:</strong> the official text says “…{escape(P["pagine_bianche"])}…”. The checker does not count pages.</p>'
              if P["pagine_bianche"] else "")
    cambi = ""
    if P["cambi_ingresso"]:
        cambi = ("<h2>Recent FCDO updates to the entry requirements</h2><ul>" +
                 "".join(f"<li>{data_lunga(c['data'])}: “{escape(c['nota'])}”</li>" for c in P["cambi_ingresso"][:5]) + "</ul>")
    tutti_simili = [Q for Q in PAESI if Q is not P and breve_regola(Q["regola"], Q) == breve_regola(R, P)] if R else []
    simili = tutti_simili[:12]
    link_simili = ""
    if simili:
        altri = len(tutti_simili) - len(simili)
        link_simili = (f"<h2>Same FCDO rule ({escape(breve_regola(R, P))})</h2><div class=\"griglia\">" +
                       "".join(f'<a href="{rel}passport-validity/{Q["slug"]}/">{escape(Q["nome"])}</a>' for Q in simili) + "</div>" +
                       (f'<p><a href="{rel}passport-validity/">and {altri} more {"destination" if altri == 1 else "destinations"} with the same rule: see all</a></p>' if altri else ""))
    titolo_sez = P["titolo_sezione"] or "Passport validity requirements"
    if R:
        checker = f"<h2>Check your passport for {escape(P['nome'])}</h2>" + modulo_checker("paese-dati", False)
    else:
        checker = ('<p class="avviso"><strong>No automatic check for this destination.</strong> The official text above is not a validity period '
                   'we turn into a date calculation. Read it, and check with your airline or carrier.</p>')
    V = visto(P)
    riga_visto = (f'<p class="cifra" style="margin-top:14px">Visa (FCDO): <strong>{escape(V["sintesi"])}.</strong> <a href="#visa">Official visa text</a></p>' if V["sintesi"] else
                  f'<p class="cifra" style="margin-top:14px">Visa (FCDO): <strong><a href="#visa">{"Read the official visa text below" if V["testo"] else "No visa section on the FCDO page"}</a></strong></p>')
    corpo = f"""<section class="hero"><h1>{escape(P['nome'])} entry requirements for British passport holders ({ANNO}): visa and passport validity</h1></section>
<section class="card summary" aria-label="Summary">
<div class="s-top"><span class="sq">{ico("passport")}</span><span>FCDO · British passport</span><span>Updated {data_lunga(P["aggiornata"])}</span></div>
<div class="s-body">
{cifra}
{riga_visto}
{fonte_pass(P)}
<p class="lead">{lead}</p>
</div>
</section>
{altri_passaporti(rel, uk_slug=P["slug"])}
{link_guida(rel, ISO_DA_FCDO.get(P["slug"]), "uk")}
{sezione_visto(P)}
<h2>Passport validity: official text “{escape(titolo_sez)}”</h2>
{testo_ufficiale(P)}
{fonte_pass(P)}
{checker}
{AVVISO_PASS}
{AD}
{avvisi}
{pagine}
{cambi}
<p>Read the full <a href="{escape(P['url'])}" rel="noopener">FCDO travel advice for {escape(P['nome'])}</a> (safety, visas, health) before you travel.</p>
<p class="small">Spotted a change? <a href="{rel}contact/?ref=pass-{P['slug']}">Tell us</a>.</p>
{box_affiliati()}
{link_simili}
<p><a href="{rel}passport-validity/">Passport validity rules for all destinations</a> · <a href="{rel}liquids/">Liquids rules by airport</a> · <a href="{rel}ees-etias/">EES and ETIAS status</a></p>
{dati_json('paese-dati', [dati_client(P)])}"""
    sint = sintesi_regola(R) if R else ("no passport legally required, but carriers may require one" if ie else "read the official FCDO text")
    descr = scegli(descrizioni_passaporto(P, sint), LIMITE_DESCRIZIONE)
    pagina(f"passport-validity/{P['slug']}/", scegli(titoli_passaporto(P), LIMITE_TITOLO), descr, corpo,
           briciole=[("Passport validity", "passport-validity/"), (P["nome"], f"passport-validity/{P['slug']}/")], js=MOTORE_JS + APP_JS)


def cambi_recenti(giorni_max=60):
    lim = (date.fromisoformat(PASS["controllato_il"]) - timedelta(days=giorni_max)).isoformat()
    voci = [(c["data"], P, c["nota"]) for P in PAESI for c in P["cambi_ingresso"] if c["data"] >= lim]
    voci.sort(key=lambda x: (x[0], x[1]["nome"]), reverse=True)
    return voci


def indici_altri(rel):
    """Link agli indici dei passaporti canadese e australiano (se ci sono i dati)."""
    ll = [f'<a href="{rel}{ESTERI[k]["base"]}/">{ESTERI[k]["agg"]} passport ({len(VOCI[k])} destinations)</a>' for k in ESTERI if VOCI[k]]
    if VOCI_IT:
        ll.append(f'<a href="{rel}{IT_BASE}/" hreflang="it">Italian citizens: <span lang="it">documenti per italiani</span> ({len(VOCI_IT)} Paesi)</a>')
    return f'<p class="altri-pass">{ico("passport")}<span>Other passports: {" · ".join(ll)}</span></p>' if ll else ""


def indice_passaporti():
    rel = "../"
    righe = "".join(f'<tr data-voce><td><a href="{rel}passport-validity/{P["slug"]}/">{escape(P["nome"])}</a></td><td>{escape(breve_regola(P["regola"], P))}</td>'
                    f'<td>{escape(visto_breve(P)[0].upper() + visto_breve(P)[1:])}</td><td>{data_lunga(P["aggiornata"])}</td></tr>' for P in PAESI)
    n_visti = sum(1 for P in PAESI if visto(P)["sintesi"])
    auto = sum(1 for P in PAESI if P["regola"])
    cambi = cambi_recenti()
    lista_cambi = "".join(f'<li>{data_lunga(d)} – <a href="{rel}passport-validity/{P["slug"]}/">{escape(P["nome"])}</a>: “{escape(n)}”</li>' for d, P, n in cambi[:40])
    rilevati = [c for c in CAMBI_PASS["cambi"] if c.get("sezione", "passport") == "passport"][:20]
    lista_rilevati = ""
    if rilevati:
        lista_rilevati = ("<h2>Passport validity text changes we detected</h2><ul>" +
                          "".join(f'<li>{data_lunga(c["rilevato_il"])} – <a href="{rel}passport-validity/{c["slug"]}/">{escape(c["nome"])}</a></li>' for c in rilevati) + "</ul>")
    corpo = f"""<section class="hero">{h1_diviso(f"Passport validity and visa rules for UK travellers ({ANNO}): every destination")}
<p class="lead">How long a British passport must be valid for {len(PAESI)} destinations, from the UK government's foreign travel advice (FCDO), quoted word for word. For {auto} destinations the checker applies the rule to your dates; for the other {len(PAESI) - auto} the official sentence has conditions we do not turn into a calculation, so we show it and you read it.</p>
<p class="lead">Each destination page also quotes the FCDO “Visa requirements” section and answers “Do I need a visa?”. For {n_visti} destinations the first FCDO visa sentence matches a wording we recognise and we add a one-line summary; for the others we only quote the official text.</p>
<p class="fonte">Source: <a href="https://www.gov.uk/foreign-travel-advice" rel="noopener">GOV.UK foreign travel advice (FCDO)</a>, read through the GOV.UK Content API · last checked: {data_lunga(PASS['controllato_il'])}.</p>
{indici_altri(rel)}
</section>
{modulo_checker('tutti-dati', True, link=rel + 'passport-validity/')}
{AVVISO_PASS}
{AD}
<h2>All destinations</h2>
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Type a country, e.g. Spain, Turkey, USA" data-filtro="lista-paesi" aria-label="Search destinations"></div>
<div class="tab"><table><thead><tr><th>Destination</th><th>Passport validity (short)</th><th>Visa (short)</th><th>FCDO page last updated</th></tr></thead><tbody id="lista-paesi">{righe}</tbody></table></div>
<p class="small">“Valid for the whole stay”: valid until the day you leave. “10-year issue rule”: the passport must have been issued less than 10 years before you arrive. Always read the full official sentence on each page.</p>
<h2>Entry requirements updated by the FCDO in the last 60 days</h2>
<p class="small">From the change notes the FCDO publishes on each travel advice page (only notes that mention the entry requirements page).</p>
<ul>{lista_cambi or '<li>None.</li>'}</ul>
{lista_rilevati}
<h2>The Schengen 10-year issue rule</h2>
<p>For the Schengen area the FCDO says your passport must have a ‘date of issue’ less than 10 years before the date you arrive, and an ‘expiry date’ at least 3 months after the day you plan to leave. In the FCDO's words, “if you renewed your passport before 1 October 2018, it might have a date of issue that is more than 10 years ago, making it invalid for entry to the Schengen area”. The checker asks for the issue date only for destinations with this rule.</p>
{box_affiliati()}
{dati_json('tutti-dati', [dati_client(P) for P in PAESI])}"""
    pagina("passport-validity/", f"Passport Validity & Visa Rules by Country {ANNO} (UK Passport)",
           f"How long must a British passport be valid, and do you need a visa? Official FCDO rules for {len(PAESI)} destinations, quoted word for word, with a date checker.",
           corpo, briciole=[("Passport validity", "passport-validity/")], js=MOTORE_JS + APP_JS)


# ---------------------------------------------------------------- passaporti canadese e australiano (Government of Canada, Smartraveller)
# Stessa regola delle pagine britanniche: il testo ufficiale è SEMPRE citato parola per parola; il riassunto di una riga esiste solo se
# raccolta/passaporti_ca.py o raccolta/passaporti_au.py lo hanno ricavato da uno schema riconosciuto (verifica.py lo ricalcola).
def _chiave_nome(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\(.*?\)", "", s).replace("&", " and ")
    s = re.sub(r"\bsaint\b", "st", s)
    s = re.sub(r"[^a-z ]", " ", s)
    s = re.sub(r"\bthe\b", "", s)
    return " ".join(s.split())


UK_PER_NOME = {_chiave_nome(P["nome"]): P["slug"] for P in PASS["paesi"]}
# destinazione della fonte -> pagine britanniche dello stesso territorio (controllate a mano il 17/10/2026); lista vuota = nessuna pagina britannica
UK_ALIAS = {
    "ca": {"CV": ["cape-verde"], "FM": ["federated-states-of-micronesia"], "CG": ["congo"], "SX": ["st-maarten"], "PM": ["st-pierre-and-miquelon"],
           "TR": ["turkey"], "US": ["usa"], "BQ": ["bonaire-st-eustatius-saba"], "CK": ["cook-islands-tokelau-and-niue"], "NU": ["cook-islands-tokelau-and-niue"],
           "TK": ["cook-islands-tokelau-and-niue"], "MF": ["st-martin-and-st-barthelemy"], "BL": ["st-martin-and-st-barthelemy"], "IL": ["israel", "palestine"],
           "AQ": [], "AS": [], "PT-20": [], "IC": [], "GL": [], "GU": [], "MP": [], "PR": [], "GB": [], "VI": []},
    "au": {"cabo-verde": ["cape-verde"], "turkiye": ["turkey"], "united-states-america": ["usa"], "usa": ["usa"], "micronesia": ["federated-states-of-micronesia"],
           "israel-and-occupied-palestinian-territories": ["israel", "palestine"], "palestinian-territories": ["palestine"],
           "republic-congo": ["congo"], "democratic-republic-congo": ["democratic-republic-of-the-congo"], "cote-divoire-ivory-coast": ["cote-d-ivoire"],
           "united-kingdom": [], "cook-islands": ["cook-islands-tokelau-and-niue"], "niue": ["cook-islands-tokelau-and-niue"],
           "brunei-darussalam": ["brunei"], "czech-republic": ["czechia"], "kyrgyz-republic": ["kyrgyzstan"], "macau": ["macao"], "guam": []},
}
UK_NOMI = {P["slug"]: P["nome"] for P in PASS["paesi"]}
UK_CON_PAGINA = {P["slug"] for P in PAESI}

ESTERI = {
    "ca": {"file": "passaporti_ca.json", "base": "canadian-passport", "agg": "Canadian", "pop": "Canadians", "ente": "Government of Canada",
           "etichetta": "Government of Canada", "icona_top": "Canadian passport", "sezione": "Entry and exit requirements",
           "ente_frase": "the Government of Canada", "un": "a"},
    "au": {"file": "passaporti_au.json", "base": "australian-passport", "agg": "Australian", "pop": "Australians", "ente": "Smartraveller (Australian Government)",
           "etichetta": "Smartraveller", "icona_top": "Australian passport", "sezione": "Travel",
           "ente_frase": "Smartraveller, the Australian Government's travel advice service", "un": "an"},
}
for _k, _c in ESTERI.items():
    _f = DATI / _c["file"]
    _c["dati"] = json.loads(_f.read_text(encoding="utf-8")) if _f.exists() else None


def _uk_di(k, p):
    chiave = p["iso"] if k == "ca" else p["slug_fonte"]
    if chiave in UK_ALIAS[k]:
        return [s for s in UK_ALIAS[k][chiave] if s in UK_CON_PAGINA]
    s = UK_PER_NOME.get(_chiave_nome(p["nome"]))
    return [s] if s in UK_CON_PAGINA else []


CON_ARTICOLO = {"USA", "Netherlands", "Philippines", "Bahamas", "Maldives", "Dominican Republic", "Central African Republic", "Comoros", "Azores",
                "Democratic Republic of the Congo", "Republic of Congo", "Republic of the Congo", "Seychelles", "Czech Republic", "Vatican City", "Gambia"}


def nome_frase(v):
    """Nome della destinazione dentro una frase: 'the USA', 'the United Kingdom', 'the Cook Islands'; uguale altrimenti."""
    n = v["nome"]
    if n.startswith("The "):
        return "the " + n[4:]
    if n in CON_ARTICOLO or n.startswith(("United ", "Federated ")) or n.endswith(("Islands", "Isles")):
        return "the " + n
    return n


# Contenuto sottile (revisione del 17/10/2026): una destinazione ha una pagina SOLO se la fonte dà testo specifico del Paese sulla validità del
# passaporto o sui visti. Le altre (per l'Australia: solo il testo generico di Smartraveller, uguale per tutti, più frasi di contorno; per il
# Canada: l'Antartide, che rimanda ai Paesi di transito) non hanno pagina, non sono nella sitemap né nei link: l'indice le elenca con il
# collegamento diretto alla pagina ufficiale.
CONTORNO_AU = re.compile(r"^(?:Entry and exit (?:conditions|requirements) can change|Contact (?:the |an |your )?(?:nearest )?[^.]*(?:embassy|consulate|high commission)"
                         r"|You should contact|You can contact|Make sure you meet all entry|If you don't(?: meet the conditions)?, the Australian|Each country or territory"
                         r"|Every country or territory|More information|Find out about returning|Countries with a risk|Some airlines may want|Check with|For more information"
                         r"|Check your visa needs)", re.I)
VALIDITA_AU = re.compile(r"\bvalid(?:ity)?\b[^.]*\b(?:\d+|six|three) (?:months?|days?)|\b(?:\d+|six|three) (?:months?|days?)[^.]*\bvalid(?:ity)?\b"
                         r"|valid for (?:the|your) (?:duration|intended|length|period)", re.I)
VISTO_AU = re.compile(r"\bvisas?\b|visa-free|\be-?visa|schengen|tourist card|entry (?:and exit )?form|arrival card|travel authori[sz]ation|\bETA\b", re.I)


def frasi_paese_au(p):
    """Frasi del Paese (non generiche, non di contorno) nella sottosezione dei visti di Smartraveller."""
    out = []
    for b in p["visto"]["testo"]:
        if b.get("generico") or b["t"] in ("h3", "h4", "li"):
            continue
        out += [x.strip() for x in re.split(r"(?<=[.!?])\s+", b["x"]) if x.strip() and not CONTORNO_AU.match(x.strip())]
    return out


def ha_testo_specifico(k, p):
    if k == "ca":
        return bool(p["passaporto"]["testo"]) or any(b["x"].startswith("Tourist visa") for b in p["visto"]["testo"])
    return bool(p["passaporto"].get("frase") and VALIDITA_AU.search(p["passaporto"]["frase"])) or any(VISTO_AU.search(x) for x in frasi_paese_au(p))


PROPRIO_NOME = {"ca": {"BQ"}}  # la pagina canadese "Bonaire" copre solo Bonaire: nome e slug suoi, anche se la pagina britannica è Bonaire/St Eustatius/Saba
SENZA_PAGINA_ESTERI = {k: [] for k in ESTERI}


def _voci(k):
    D = ESTERI[k]["dati"]
    if not D:
        return []
    out = []
    for p in D["paesi"]:
        if not (p["passaporto"]["testo"] or p["visto"]["testo"]):
            continue
        if not ha_testo_specifico(k, p):
            SENZA_PAGINA_ESTERI[k].append(p)
            continue
        out.append({"k": k, "p": p, "uk": _uk_di(k, p)})
    # slug: quello della pagina britannica se il legame è uno a uno, altrimenti quello della fonte
    quanti = {}
    for v in out:
        for s in v["uk"]:
            quanti[s] = quanti.get(s, 0) + 1
    for v in out:
        uno = len(v["uk"]) == 1 and quanti[v["uk"][0]] == 1 and v["p"].get("iso", v["p"]["slug_fonte"]) not in PROPRIO_NOME.get(k, set())
        v["slug"] = v["uk"][0] if uno else v["p"]["slug_fonte"]
        v["nome"] = UK_NOMI[v["uk"][0]] if uno else re.sub(r"\s*\((?:Kinshasa|Brazzaville|FSM|Ivory Coast|East Timor)\)", "", v["p"]["nome"]).replace("Gambia, The", "The Gambia")
        v["url_pag"] = f"{ESTERI[k]['base']}/{v['slug']}/"
    out.sort(key=lambda v: _chiave_nome(v["nome"]))
    return out


VOCI = {k: _voci(k) for k in ESTERI}
PER_UK = {k: {} for k in ESTERI}  # pagina britannica -> pagine canadesi/australiane dello stesso territorio
for _k in ESTERI:
    for _v in VOCI[_k]:
        for _s in _v["uk"]:
            PER_UK[_k].setdefault(_s, []).append(_v)
PER_CHIAVE = {k: {(v["uk"][0] if v["uk"] else _chiave_nome(v["nome"])): v for v in VOCI[k]} for k in ESTERI}


def _chiave_voce(v):
    return v["uk"][0] if v["uk"] else _chiave_nome(v["nome"])


def altri_passaporti(rel, uk_slug=None, voce=None):
    """'Other passports: British · Canadian · Australian' con i link alle pagine della stessa destinazione che esistono."""
    link = []
    if voce is not None and voce["uk"]:
        link += [f'<a href="{rel}passport-validity/{s}/">British passport{(" (" + escape(UK_NOMI[s]) + ")") if (len(voce["uk"]) > 1 or UK_NOMI[s] != voce["nome"]) else ""}</a>'
                 for s in voce["uk"]]
    for k in ESTERI:
        if voce is not None and voce["k"] == k:
            continue
        if uk_slug:
            ww = PER_UK[k].get(uk_slug, [])
        elif voce["uk"]:
            # stessa destinazione: se la pagina britannica copre più territori (Isole Cook, Tokelau e Niue) si tiene solo quello con lo stesso nome
            ww = []
            for s in voce["uk"]:
                cc = PER_UK[k].get(s, [])
                if len(cc) > 1:
                    cc = [w for w in cc if _chiave_nome(w["p"]["nome"]) == _chiave_nome(voce["p"]["nome"])]
                ww += [w for w in cc if w not in ww]
        else:
            ww = [PER_CHIAVE[k][_chiave_voce(voce)]] if _chiave_voce(voce) in PER_CHIAVE[k] else []
        qui = voce["nome"] if voce is not None else UK_NOMI.get(uk_slug, "")
        for w in ww:  # il nome tra parentesi se i link sono più d'uno o se la pagina collegata copre un territorio diverso (Israel and Palestine)
            etich = len(ww) > 1 or _chiave_nome(w["nome"]) != _chiave_nome(qui)
            link.append(f'<a href="{rel}{w["url_pag"]}">{ESTERI[k]["agg"]} passport{(" (" + escape(w["nome"]) + ")") if etich else ""}</a>')
    if uk_slug:
        link += link_italiani(rel, uk_slug)
    return f'<p class="altri-pass">{ico("passport")}<span>Other passports: {" · ".join(link)}</span></p>' if link else ""


def avviso_estero(k, rel):
    c = ESTERI[k]
    if k == "ca":
        chi = ("These rules are published by the Government of Canada (Global Affairs Canada) for Canadian citizens travelling on a regular Canadian passport. "
               "Before You Fly is an independent site: it is not a Government of Canada site and is not endorsed by the Government of Canada.")
    else:
        chi = ("These rules are published by Smartraveller, the Australian Government's travel advice service (Department of Foreign Affairs and Trade), for "
               "Australian citizens. Before You Fly is an independent site: it is not an Australian Government site and is not endorsed by DFAT.")
    return (f'<p class="avviso"><strong>For {c["agg"]} passport holders.</strong> {chi} The airline and the border officials of the destination decide whether '
            f'you can travel or enter: this site is information, not legal advice. British passport? See the <a href="{rel}passport-validity/">UK (FCDO) rules</a>.</p>')


def licenza_estera(k):
    D = ESTERI[k]["dati"]
    if k == "ca":
        return (f'{escape(D["attribuzione"][:-len("Open Government Licence – Canada.")])}<a href="{escape(D["licenza_url"])}" rel="noopener">Open Government Licence – Canada</a>.')
    return (f'Content from {escape(D["attribuzione"])}, licensed under <a href="{escape(D["licenza_url"])}" rel="noopener">CC BY 4.0</a> '
            f'(<a href="{escape(D["copyright_url"])}" rel="noopener">copyright notice</a>). Changes: we quote excerpts unchanged and leave out some general notes; the short summaries are ours.')


def fonte_estera(v, sezione):
    k, p = v["k"], v["p"]
    D = ESTERI[k]["dati"]
    if k == "ca":
        nome_fonte = f'Government of Canada – {escape(p["nome"])} travel advice and advisories (travel.gc.ca)'
        date_txt = f'page last updated {data_lunga(p["aggiornata"])}'
    else:
        nome_fonte = f'Smartraveller (Australian Government) – {escape(p["nome"])} travel advice'
        date_txt = (f'page updated {data_lunga(p["aggiornata"])}' if p.get("aggiornata") else "update date not shown") + \
                   (f', still current at {data_lunga(p["ancora_valida_il"])} (Australian time)' if p.get("ancora_valida_il") else "")
    return (f'<p class="fonte">Official source: <a href="{escape(p["url"])}" rel="noopener">{nome_fonte}</a>, section “{escape(sezione)}” · {date_txt} · '
            f'checked on {data_lunga(D["controllato_il"])} · {licenza_estera(k)}</p>')


def breve_visto_estero(v):
    """Etichetta corta per l'indice, ricavata solo dal riassunto (che viene da uno schema fisso): nessun fatto nuovo."""
    V = v["p"]["visto"]
    x = V["sintesi"]
    if not x:
        return "read the official visa text" if V["testo"] else "no visa section on the official page"
    m = re.search(r"(?:not required for stays |without a visa for |don't need a visa to visit .+? for |^Tourists can visit .+? for |^You can stay in .+? for )(?:of )?(up to a maximum of |up to |less than |fewer than )?(\d+|six) (days|months|weeks)( or less)?", x)
    if re.match(r"^(?:Tourist visa required|You need a visa)", x):
        b = "Required"
    elif m:
        b = f"Not required: {(m.group(1) or '').replace('up to a maximum of ', 'up to ')}{m.group(2)} {m.group(3)}{m.group(4) or ''}"
        b += " in any 180 days" if re.search(r"\b180[- ]day period", x) else ""
        b += " (tourists)" if re.match(r"^(?:Tourists|Australian tourists)", x) or "for tourism" in x else ""
    else:
        b = "Not required (tourism)" if "tourism" in x or "tourist" in x.lower() and "Tourist visa" not in x else "Not required"
    if "ETIAS" in x:
        b += "; ETIAS: applications not yet open"
    return b


def breve_validita_estera(v):
    P = v["p"]["passaporto"]
    if P.get("breve"):
        return P["breve"]
    if v["k"] == "au" and not P.get("frase"):
        return "General advice only (no country rule)"
    return "Read the official text" if P["testo"] else "No passport text"


AUTORIZZ_VISIBILE = re.compile(r"authori[sz]ation|\bETIAS\b|\beTA\b|\bETA\b|\be-?visa|arrival|declaration|immigration form|tourist card|migration card|ED card|"
                               r"regist|online|fee|tax", re.I)


def sezioni_altre(v):
    """Altre sezioni della parte d'ingresso: visibili quelle su autorizzazioni, moduli, registrazioni, Schengen, EES/ETIAS...; le altre nel riquadro apribile."""
    vis, chiuse = [], []
    for a in v["p"].get("altre_sezioni", []):
        bb = [{"t": "h3", "x": a["titolo"]}] + a["testo"]
        (vis if (a.get("visibile") or v["k"] == "au" or AUTORIZZ_VISIBILE.search(a["titolo"])) else chiuse).append(bb)
    return vis, chiuse


def sezione_visto_estero(v, rel):
    k, p, c = v["k"], v["p"], ESTERI[v["k"]]
    V = p["visto"]
    n = escape(nome_frase(v))
    dom = f'<h2 id="visa">Do {c["pop"]} need a visa for {n}?</h2>'
    if not V["testo"]:
        return (dom + f'<p class="avviso">The {escape(c["ente"])} page for {n} had no visa section when we checked it on '
                f'{data_lunga(c["dati"]["controllato_il"])}, so we have nothing to quote. Read the <a href="{escape(p["url"])}" rel="noopener">full official travel advice</a> '
                'or ask the embassy of the country before you travel.</p>')
    if V["sintesi"]:
        breve = (f'<p class="cifra">In short: <strong>{escape(V["sintesi"])}.</strong></p>'
                 f'<p class="small">Our one-line summary of the first official line below, which matches a wording we recognise. It applies to {c["agg"]} citizens; '
                 'read the full official text, which may add conditions.</p>')
    else:
        breve = f'<p class="small">We quote the official text word for word and do not summarise it. {escape(V["motivo"] or "")}</p>'
    vis, chiuse = sezioni_altre(v)
    altre_vis = "".join(blocchi_html(bb) for bb in vis)
    altro = ""
    if chiuse:
        altro = (f'<details class="card" style="margin-top:12px"><summary><strong>More from the official “{escape(c["sezione"])}” section</strong> '
                 f'(other requirements)</summary>{"".join(blocchi_html(bb) for bb in chiuse)}</details>')
    titolo = escape(V.get("titolo_sezione") or "Visas")
    return (dom + breve + f'<p class="small" style="margin-bottom:0">Official text, “{titolo}”:</p>' + blocchi_html(V["testo"]) +
            (f'<p class="small" style="margin-bottom:0">Also in the official “{escape(c["sezione"])}” section:</p>' + altre_vis if altre_vis else "") +
            altro + fonte_estera(v, V.get("titolo_sezione") or "Visas"))


def passaporto_da_mostrare(k, testo):
    """Smartraveller: la sottosezione "Passport" ripete su ogni pagina gli stessi riquadri generici ("Lost or stolen passport", "Passport with 'X'
    gender identifier"). Si mostrano il blocco "Validity" e ogni parte che contiene testo del Paese; i riquadri solo generici no (meno testo
    duplicato tra le pagine). Il Canada cita già solo "Regular Canadian passport"."""
    if k != "au":
        return testo
    gruppi, cur = [], []
    for b in testo:
        if b["t"] == "h4" and cur:
            gruppi.append(cur)
            cur = []
        cur.append(b)
    if cur:
        gruppi.append(cur)
    tenere = [g for i, g in enumerate(gruppi) if i == 0 and g[0]["t"] != "h4" or g[0]["t"] == "h4" and g[0]["x"].strip().lower() == "validity"
              or any(not b.get("generico") and b["t"] != "h4" for b in g)]
    return [b for g in tenere for b in g]


def sezione_validita_estera(v):
    k, p, c = v["k"], v["p"], ESTERI[v["k"]]
    P = p["passaporto"]
    n = escape(nome_frase(v))
    dom = f'<h2 id="passport">How long must my {c["agg"]} passport be valid for {n}?</h2>'
    if not P["testo"]:
        return dom + (f'<p class="avviso">The {escape(c["ente"])} page for {n} had no passport text for regular passports when we checked it. '
                      f'Read the <a href="{escape(p["url"])}" rel="noopener">full official travel advice</a> or ask the embassy of the country.</p>')
    if P["sintesi"]:
        breve = (f'<p class="cifra">In short: <strong>{escape(P["sintesi"])}.</strong></p>'
                 '<p class="small">Our one-line summary of the official sentence below, which matches a wording we recognise. Your airline may apply stricter rules.</p>')
    elif k == "au" and not P.get("frase"):
        breve = (f'<p class="cifra"><strong>In its “Travel” section, Smartraveller gives no passport validity period specific to {escape(nome_frase(v))}.</strong></p>'
                 '<p class="small">The official “Passport” text below is Smartraveller\'s general advice, the same on every destination page. '
                 'Check the rule with the embassy of the country and with your airline before you travel.</p>')
    else:
        breve = f'<p class="small">We quote the official text word for word and do not summarise it. {escape(P["motivo"] or "")}</p>'
    tit = (P.get("titolo_sezione") or "Regular Canadian passport") if k == "ca" else "Passport"
    mostra = passaporto_da_mostrare(k, P["testo"])
    nota = ""
    tolti = [b["x"] for b in P["testo"] if b["t"] == "h4" and b not in mostra]
    if tolti:
        nota = (f'<p class="small">The same section also has Smartraveller\'s general notes ({escape(", ".join("“" + x + "”" for x in tolti))}), '
                f'the same on every destination page: read them on the <a href="{escape(p["url"])}" rel="noopener">official page</a>.</p>')
    return (dom + breve + f'<p class="small" style="margin-bottom:0">Official text, “{tit}”:</p>' + blocchi_html(mostra) + nota + fonte_estera(v, tit))


def titoli_estero(v):
    n, pop = v["nome"], ESTERI[v["k"]]["pop"]
    return [f"{n} Entry Requirements for {pop} {ANNO}: Visa & Passport", f"{n} Entry Rules for {pop} {ANNO}: Visa & Passport",
            f"{n} Entry Requirements for {pop} {ANNO}",
            f"{n} Visa & Passport for {pop} {ANNO}", f"{n}: Entry Rules for {pop} {ANNO}", f"{n} for {pop} {ANNO}"]


def descrizioni_estero(v):
    c = ESTERI[v["k"]]
    n, pop = nome_frase(v), c["pop"]
    vis = v["p"]["visto"]["sintesi"]
    val = v["p"]["passaporto"]["sintesi"]
    fonte = "Government of Canada" if v["k"] == "ca" else "Smartraveller"
    return [f"Do {pop} need a visa for {n}? {vis or 'Official visa text quoted word for word'}. Passport: {val or 'official text quoted'}. {fonte} text, dated.",
            f"Do {pop} need a visa for {n}? {vis or 'Official visa text quoted word for word'}. Plus passport validity, from the {fonte} page, dated.",
            f"Do {pop} need a visa for {n}? {vis or 'The official text, quoted word for word'}.",
            f"Do {pop} need a visa for {n}? Visa and passport validity rules from the {fonte} page, quoted word for word.",
            f"{v['nome']}: visa and passport rules for {pop} ({ANNO}), quoted from the {fonte} page."]


NOTE_SINTESI = re.compile(r"^(.*?)(?: \((the official text adds more details|read the official text for how long you can stay)\))?(; ETIAS will be required, .*)?$")


def sint_box(x):
    """Riassunto nel riquadro in alto: la parte principale in grande, le note tra parentesi in piccolo (stesso testo del riassunto)."""
    m = NOTE_SINTESI.match(x)
    nota = m.group(2)
    return (f'<strong>{escape(m.group(1) + (m.group(3) or ""))}.</strong>' +
            (f'<span class="nota-s">({escape(nota)})</span>' if nota else ""))


def pagina_estera(v):
    rel = "../../"
    k, p, c = v["k"], v["p"], ESTERI[v["k"]]
    V, P = p["visto"], p["passaporto"]
    n = escape(v["nome"])
    riga_visto = (f'<p class="cifra" style="margin-top:4px">Visa ({escape(c["etichetta"])}): {sint_box(V["sintesi"])} <a href="#visa">Official visa text</a></p>'
                  if V["sintesi"] else
                  f'<p class="cifra" style="margin-top:4px">Visa ({escape(c["etichetta"])}): <strong><a href="#visa">{"Read the official visa text below" if V["testo"] else "No visa section on the official page"}</a></strong></p>')
    if P["sintesi"]:
        riga_val = f'<p class="cifra">Passport validity ({escape(c["etichetta"])}): {sint_box(P["sintesi"])} <a href="#passport">Official text</a></p>'
    elif k == "au" and not P.get("frase"):
        riga_val = (f'<p class="cifra">Passport validity ({escape(c["etichetta"])}): <strong><a href="#passport">No country-specific rule: general advice only</a></strong></p>')
    else:
        riga_val = f'<p class="cifra">Passport validity ({escape(c["etichetta"])}): <strong><a href="#passport">Read the official text below</a></strong></p>'
    aggiornata = p.get("aggiornata")
    lead = (f"Whether {c['pop']} need a visa for {escape(nome_frase(v))} and how long {c['un']} {c['agg']} passport must be valid, as published by {escape(c['ente_frase'])}, "
            "quoted word for word with the date of the official page.")
    corpo = f"""<section class="hero"><h1>{n} entry requirements for {c['agg']} passport holders ({ANNO}): visa and passport validity</h1></section>
<section class="card summary" aria-label="Summary">
<div class="s-top"><span class="sq">{ico("passport")}</span><span>{escape(c["icona_top"])}</span><span>{"Updated " + data_lunga(aggiornata) if aggiornata else ""}</span></div>
<div class="s-body">
{riga_visto}
{riga_val}
{fonte_estera(v, c["sezione"])}
<p class="lead">{lead}</p>
</div>
</section>
{altri_passaporti(rel, voce=v)}
{link_guida(rel, v["p"].get("iso") if k == "ca" else ISO_DA_AU.get(_chiave_nome(v["p"]["nome"])), k)}
{sezione_visto_estero(v, rel)}
{sezione_validita_estera(v)}
{avviso_estero(k, rel)}
{AD}
<p>Read the full <a href="{escape(p['url'])}" rel="noopener">official travel advice for {escape(nome_frase(v))}</a> (safety, health, local laws) before you travel.</p>
<p class="small">Spotted a change? <a href="{rel}contact/?ref={k}-{v['slug']}">Tell us</a>.</p>
{box_affiliati()}
<p><a href="{rel}{c['base']}/">{c['agg']} passport: all destinations</a> · <a href="{rel}passport-validity/">British passport rules</a> · <a href="{rel}liquids/">Liquids rules by airport</a> · <a href="{rel}ees-etias/">EES and ETIAS status</a></p>"""
    ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": f"{v['nome']} entry requirements for {c['agg']} passport holders ({ANNO})",
           "url": f"{URL_SITO}/{v['url_pag']}", "inLanguage": "en", "isBasedOn": p["url"], "dateModified": c["dati"]["controllato_il"],
           "isPartOf": {"@type": "WebSite", "name": NOME, "url": URL_SITO + "/"}}]
    pagina(v["url_pag"], scegli(titoli_estero(v), LIMITE_TITOLO), scegli(descrizioni_estero(v), LIMITE_DESCRIZIONE), corpo,
           briciole=[(f"{c['agg']} passport", f"{c['base']}/"), (v["nome"], v["url_pag"])], js=MOTORE_JS + APP_JS, ld_extra=ld)


def indice_estero(k):
    rel = "../"
    c, D = ESTERI[k], ESTERI[k]["dati"]
    voci = VOCI[k]
    righe = "".join(f'<tr data-voce><td><a href="{rel}{v["url_pag"]}">{escape(v["nome"])}</a></td><td data-l="Passport">{escape(breve_validita_estera(v))}</td>'
                    f'<td data-l="Visa">{escape(breve_visto_estero(v)[0].upper() + breve_visto_estero(v)[1:])}</td>'
                    f'<td>{("Updated " + data_lunga(v["p"]["aggiornata"])) if v["p"].get("aggiornata") else "–"}</td></tr>'
                    for v in voci)
    n_val = sum(1 for v in voci if v["p"]["passaporto"]["sintesi"])
    n_vis = sum(1 for v in voci if v["p"]["visto"]["sintesi"])
    senza = SENZA_PAGINA_ESTERI[k]
    senza_pagina = ""
    if senza:
        lista = ", ".join(f'<a href="{escape(p["url"])}" rel="noopener">{escape(p["nome"])}</a>' for p in senza)
        senza_pagina = (f'<p class="small">No page here for {len(senza)} destination{"s" if len(senza) > 1 else ""}: when we checked, the official '
                        f'{escape(c["etichetta"])} advice gave no destination-specific visa or passport validity text for '
                        f'{"them" if len(senza) > 1 else "it"}. Read the official advice directly: {lista}.</p>')
    if k == "ca":
        fonte = (f'<p class="fonte">Source: <a href="https://travel.gc.ca/travelling/advisories" rel="noopener">Government of Canada, Travel advice and advisories</a> '
                 f'(Global Affairs Canada), read through the official open data files (<a href="{escape(D["dataset_url"])}" rel="noopener">open.canada.ca dataset</a>) · '
                 f'last checked: {data_lunga(D["controllato_il"])} · {licenza_estera(k)}</p>')
        spiega = (f"For {n_val} destinations the Government of Canada sentence on regular Canadian passports matches a wording we recognise and we add a one-line summary; "
                  f"for {n_vis} destinations the “Tourist visa” line does too. Where the official text also mentions an electronic travel authorization (eTA/ETA), an e-visa, "
                  "an arrival card, an online form or registration, a tourist card or a fee, we do not summarise the visa line: we quote it, with those sections in full.")
    else:
        fonte = (f'<p class="fonte">Source: <a href="https://www.smartraveller.gov.au/destinations" rel="noopener">Smartraveller destinations</a> '
                 f'(Australian Government, Department of Foreign Affairs and Trade) · last checked: {data_lunga(D["controllato_il"])} · {licenza_estera(k)}</p>')
        spiega = (f"Smartraveller writes its advice in prose, so we summarise very little: {n_vis} visa summaries and {n_val} passport validity summaries, only where the official "
                  "sentence matches a fixed wording. For most destinations Smartraveller gives only its general passport advice (“Many countries require your passport to be "
                  "valid for at least 6 months…”), which we quote as general advice, not as a rule of the country.")
    corpo = f"""<section class="hero">{h1_diviso(f"{c['agg']} passport: visa and passport validity rules for every destination ({ANNO})")}
<p class="lead">Do {c['pop']} need a visa, and how long must {c['un']} {c['agg']} passport be valid? For {len(voci)} destinations, the text of {escape(c['ente_frase'])}, quoted word for word, with the date of each official page.</p>
<p class="lead">{spiega}</p>
{fonte}
</section>
{avviso_estero(k, rel)}
{AD}
<h2>All destinations</h2>
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Type a country, e.g. Japan, Mexico, France" data-filtro="lista-{k}" aria-label="Search destinations"></div>
<div class="tab tab-e"><table><thead><tr><th>Destination</th><th>Passport validity (short)</th><th>Visa (short)</th><th>Official page updated</th></tr></thead><tbody id="lista-{k}">{righe}</tbody></table></div>
<p class="small">Short labels are ours; always read the official text on each page. “After departure”: counted from the day you leave the country.</p>
{senza_pagina}
<p>Other passports: <a href="{rel}passport-validity/">British passport (FCDO)</a> · {" · ".join(f'<a href="{rel}{ESTERI[j]["base"]}/">{ESTERI[j]["agg"]} passport</a>' for j in ESTERI if j != k and VOCI[j])}</p>
{box_affiliati()}"""
    titolo = f"{c['agg']} Passport: Visa & Passport Rules by Country {ANNO}"
    pagina(f"{c['base']}/", titolo,
           f"Do {c['pop']} need a visa? How long must {c['un']} {c['agg']} passport be valid? Official rules for {len(voci)} destinations, quoted word for word, with dates.",
           corpo, briciole=[(f"{c['agg']} passport", f"{c['base']}/")], js=MOTORE_JS + APP_JS)


# ---------------------------------------------------------------- documenti per chi ha la cittadinanza italiana (Viaggiare Sicuri), in italiano
# Fonte: schede Paese di Viaggiare Sicuri (Unità di Crisi della Farnesina), lette da raccolta/documenti_it.py. Licenza dei testi non indicata:
# le pagine NON riportano i testi delle schede, ma solo i fatti con parole nostre (da modelli fissi, o scritti a mano in dati/documenti_it_manuali.json),
# citazioni brevi (al massimo 20 parole), la data della scheda e il link. Se un fatto non è inequivocabile: "Consulta la scheda ufficiale".
IT_BASE = "it/documenti"
_f_it = DATI / "documenti_it.json"
DOC_IT = json.loads(_f_it.read_text(encoding="utf-8")) if _f_it.exists() else None
MESI_IT = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
VS_HOME = "https://www.viaggiaresicuri.it/"
VS_DOCUMENTI = "https://www.viaggiaresicuri.it/approfondimenti-insights/documentidiviaggio"
PIEDE_IT = f"""<footer><div class="wrap">
<div class="f-grid"><div>
<a class="logo" href="{{rel}}">{MARCHIO}<span>Before <b>You Fly</b></span></a>
<p><strong>{NOME}</strong> è un sito indipendente: <strong>non è della Farnesina, del Ministero degli Affari Esteri né del Governo italiano</strong> e non è collegato a governi, aeroporti o compagnie aeree.
Per chi ha la cittadinanza italiana riportiamo i fatti delle schede Paese di <a href="{VS_HOME}" rel="noopener">Viaggiare Sicuri</a> (Unità di Crisi della Farnesina) con parole nostre, con brevi citazioni, la data della scheda e il link.</p>
<p><strong>Le regole cambiano: controlla la scheda ufficiale prima di partire.</strong> Compagnia aerea e autorità di frontiera decidono se puoi partire o entrare; niente su questo sito è una consulenza legale.</p>
</div><div>
<h2>Esplora</h2>
<ul><li><a href="{{rel}}{IT_BASE}/">Documenti e visti, tutti i Paesi</a></li><li><a href="{{rel}}{IT_BASE}/#metodo">Fonte e metodo</a></li><li lang="en"><a href="{{rel}}contact/?ref=it">Contact (English)</a></li><li lang="en"><a href="{{rel}}privacy.html">Privacy (English)</a></li></ul>
</div></div>
{blocco_altri(ALTRI_SITI_IT, "Altri strumenti utili per il viaggio")}
<p class="f-base">Solo fonti ufficiali, con data e link.</p>
</div></footer>"""


def data_it(iso):
    d = date.fromisoformat(iso)
    return f"{'1°' if d.day == 1 else d.day} {MESI_IT[d.month - 1]} {d.year}"


def data_it_breve(iso):
    d = date.fromisoformat(iso)
    return f"{d.day}/{d.month}/{d.year}"


def con_art(prep, data):
    """«il 18 ottobre», ma «l'11 settembre», «dell'8/10/2026», «all'11 aprile» (8, 11, 80... si leggono con la vocale)."""
    if re.match(r"(?:8|11)(?!\d)|8\d", data):
        return {"il": "l'", "del": "dell'", "al": "all'"}[prep] + data
    return f"{prep} {data}"


def _slug_it(nome):
    s = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().lower().replace("'", " ")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def _nomi_it():
    out = {}
    f = DATI / "paesi_it.txt"
    if not f.exists():
        return out
    for r in f.read_text(encoding="utf-8").splitlines():
        if not r.strip() or r.startswith("#"):
            continue
        iso, nome, luogo = r.split("|")
        out[iso] = {"nome": nome, "luogo": luogo, "slug": _slug_it(nome)}
    return out


NOMI_IT = _nomi_it()
# pagina britannica dello stesso territorio: dalla tabella ISO2 del Canada (stessi legami controllati in UK_ALIAS) più questi casi a mano
UK_PER_IT_MANO = {"CAN": ["canada"], "ISR": ["israel"], "PSE": ["palestine"], "GBR": [], "GUM": [], "MNP": [], "VIR": [], "PRI": [], "ASM": []}


def _uk_di_it(p):
    if p["iso3"] in UK_PER_IT_MANO:
        return [s for s in UK_PER_IT_MANO[p["iso3"]] if s in UK_CON_PAGINA]
    D = ESTERI["ca"]["dati"]
    if not D:
        return []
    ca = {q["iso"]: q for q in D["paesi"]}
    q = ca.get(p.get("iso2")) or ca.get({"KS": "XK"}.get(p.get("iso2"), ""))
    uk = _uk_di("ca", q) if q else []
    return uk if len(uk) == 1 else []


def ha_pagina_it(p):
    """Pagina solo con contenuto specifico del Paese: il visto riassunto, oppure una regola sulla carta d'identità (sì, a condizioni, no),
    oppure sia il documento sia la validità riassunti. Le altre schede (solo "serve il passaporto", o nulla di sicuro) non hanno pagina."""
    return bool(p["visto"].get("esito") or p["documento"].get("esito") in ("cie", "cie_condizioni", "solo_passaporto")
                or (p["documento"].get("esito") and p["validita"].get("esito")))


def _voci_it():
    if not DOC_IT:
        return [], []
    con, senza = [], []
    for p in DOC_IT["paesi"]:
        n = NOMI_IT[p["iso3"]]
        v = {"p": p, "nome": n["nome"], "luogo": n["luogo"], "slug": n["slug"], "url_pag": f"{IT_BASE}/{n['slug']}/", "uk": _uk_di_it(p)}
        (con if ha_pagina_it(p) else senza).append(v)
    chiave = lambda v: unicodedata.normalize("NFKD", v["nome"]).encode("ascii", "ignore").decode().lower()
    return sorted(con, key=chiave), sorted(senza, key=chiave)


VOCI_IT, SENZA_PAGINA_IT = _voci_it()
IT_PER_UK = {}
for _v in VOCI_IT:
    for _s in _v["uk"]:
        IT_PER_UK.setdefault(_s, []).append(_v)
IT_PER_ISO = {v["p"]["iso3"]: v for v in VOCI_IT}


def link_italiani(rel, uk_slug):
    """Dalle pagine britanniche: 'Italian citizens: documenti per italiani' verso la pagina italiana dello stesso territorio."""
    vv = IT_PER_UK.get(uk_slug, [])
    return [f'<a href="{rel}{v["url_pag"]}" hreflang="it">Italian citizens: <span lang="it">documenti per italiani'
            f'{(" (" + escape(v["nome"]) + ")") if len(vv) > 1 else ""}</span></a>' for v in vv]


# ---- etichette (parole nostre, solo dai fatti)
def doc_it(D):
    """(etichetta breve, frase) del documento."""
    e = D.get("esito")
    breve = {"cie": "Basta la carta d'identità elettronica (CIE), oppure il passaporto", "cie_condizioni": "Carta d'identità solo a certe condizioni",
             "solo_passaporto": "Serve il passaporto: la carta d'identità non basta",
             "passaporto": "Serve il passaporto"}.get(e, "Consulta la scheda ufficiale")
    if D.get("sintesi"):
        return breve, D["sintesi"]
    frase = {"cie": "Si entra con la carta d'identità elettronica (CIE) oppure con il passaporto.",
             "cie_condizioni": "La scheda ammette la carta d'identità solo in alcuni casi: leggi la condizione qui sotto e la scheda ufficiale.",
             "solo_passaporto": "La scheda dice che serve il passaporto: la carta d'identità non basta.",
             "passaporto": "La scheda indica il passaporto e non cita la carta d'identità tra i documenti per entrare."}.get(e)
    return breve, frase or ("Non lo riassumiamo: " + _minuscola(D.get("motivo") or "").rstrip(".") + ".")


def val_it(V):
    e = V.get("esito")
    if V.get("sintesi"):
        breve = {"numero": f"Almeno {V.get('n')} {V.get('unita')}", "soggiorno": "Per tutto il soggiorno", "rientro": "Oltre la data del rientro",
                 "in_corso": "In corso di validità"}.get(e, "Consulta la scheda")
        return breve, V["sintesi"]
    if e == "numero":
        rif = (", contati dall'ingresso nel Paese" if V.get("dall_ingresso") else " oltre la data di uscita dal Paese" if V.get("dall_uscita")
               else " oltre la fine del soggiorno" if V.get("oltre_soggiorno") else "")
        return (f"Almeno {V['n']} {V['unita']}", f"Almeno {V['n']} {V['unita']} di validità residua{rif}.")
    if e == "soggiorno":
        return "Per tutto il soggiorno", "Il documento deve essere valido per tutta la durata del soggiorno."
    if e == "rientro":
        return "Oltre la data del rientro", "Il passaporto deve scadere dopo la data prevista per il rientro."
    if e == "in_corso":
        return "In corso di validità", "Basta che il documento sia in corso di validità: la scheda non indica un numero minimo di mesi."
    return "Consulta la scheda", "Non lo riassumiamo: " + _minuscola(V.get("motivo") or "").rstrip(".") + "."


def vis_it(S):
    """(etichetta breve per l'indice, titolo, frasi in più)."""
    e = S.get("esito")
    if e == "non_necessario":
        titolo = "Non serve il visto" + (" per turismo" if S.get("turismo") else "")
        breve = "Non serve" + "".join(" + " + f["nome"].split(" (")[0] for f in S.get("formalita", []) if f["tipo"] != "tessera turistica a pagamento")
    elif e == "necessario":
        titolo, breve = "Sì, serve il visto", "Serve"
    elif e == "all_arrivo":
        titolo, breve = "Visto all'arrivo, senza richiesta prima di partire", "All'arrivo"
    elif e == "autorizzazione":
        nomi = [f["nome"] for f in S.get("formalita", [])]
        titolo, breve = "Serve un'autorizzazione elettronica" + (f" ({nomi[0]})" if nomi else ""), "Autorizzazione" + (f" {nomi[0]}" if nomi else "")
    else:
        return "Vedi scheda", "Consulta la scheda ufficiale", []
    altre = []
    if S.get("fino_al"):
        altre.append(f"Secondo la scheda questa regola vale fino {con_art('al', data_it(S['fino_al']))}.")
    return breve, titolo, altre


def _con_articolo(f):
    """«l'autorizzazione elettronica ESTA», «la carta d'arrivo digitale Thailand Digital Arrival Card (TDAC)», «il formulario d'ingresso»."""
    nome, tipo = f["nome"], f["tipo"]
    if nome.split()[0] in ("formulario", "modulo"):  # «il formulario d'ingresso», «il modulo ED online (...)»
        return "il " + nome
    art = {"autorizzazione": "l'", "carta": "la ", "tessera": "la "}.get(tipo.split()[0], "il ")
    return f"{art}{tipo} {nome}"


def _art_nome(f):
    """Nome breve con l'articolo, per le descrizioni: «l'ESTA», «la Thailand Digital Arrival Card», «il formulario d'ingresso»."""
    nome = f["nome"].split(" (")[0]
    if re.match(r"[AEIOUaeiou]", nome):
        return "l'" + nome
    if nome[:1].islower():
        return "il " + nome
    return ("la " if re.match(r"(?:autorizzazione|carta|tessera)", f["tipo"]) else "il ") + nome


def titolo_visto_it(S):
    """Titolo del visto con le autorizzazioni e i moduli obbligatori: chi legge solo il riquadro in alto non deve perderli."""
    _, titolo, _ = vis_it(S)
    form = [f for f in S.get("formalita", []) if S.get("esito") == "non_necessario" and f["tipo"] != "tessera turistica a pagamento"]
    if form:
        titolo += ", ma serve " + " e ".join(_con_articolo(f) for f in form)
    return titolo


def _minuscola(x):
    return x[:1].lower() + x[1:]


def _prima_frase(x):
    """(prima frase, resto): il riquadro in alto e «In breve» mostrano solo la prima frase di un riassunto lungo."""
    m = re.search(r"(?<=[a-zà-ù0-9)»])\. (?=[A-ZÀ-Ý«])", x)
    return (x[:m.start() + 1], x[m.end():]) if m else (x, "")


def _cit(q):
    return f'<blockquote class="cit"><p>{escape(q)}</p></blockquote>'


def _cit_lista(qq):
    """Citazioni senza doppioni (una citazione contenuta in un'altra non si ripete)."""
    out = []
    for q in qq:
        if q and not any(q in x for x in out):
            out = [x for x in out if x not in q] + [q]
    return "".join(_cit(q) for q in out)


def fonte_it(p, campi):
    nomi = " e ".join(f"«{c}»" for c in campi)
    return (f'<p class="fonte">Fonte: <a href="{escape(p["url"])}" rel="noopener">Viaggiare Sicuri – scheda «{escape(p["nome_fonte"])}»</a> '
            f'(Unità di Crisi del Ministero degli Affari Esteri e della Cooperazione Internazionale), {"campi" if len(campi) > 1 else "campo"} {nomi} · '
            f'scheda aggiornata {con_art("il", data_it(p["aggiornata"]))} · letta da noi {con_art("il", data_it(DOC_IT["controllato_il"]))}</p>')


AVVISO_IT = ('<p class="avviso"><strong>Le regole cambiano: controlla la scheda ufficiale prima di partire.</strong> Questo sito non è della Farnesina né del '
             'Governo italiano. Riportiamo con parole nostre i fatti della scheda di Viaggiare Sicuri, che vale per chi ha la cittadinanza italiana; la compagnia '
             'aerea e le autorità di frontiera decidono se puoi partire o entrare. Per i minori e per chi ha anche un\'altra cittadinanza la scheda ha regole proprie.</p>')


def nota_manuale_it(p, f):
    """Ogni fatto scritto a mano dice quando l'abbiamo scritto e su quale versione della scheda."""
    if not f.get("manuale"):
        return ""
    return (f'<p class="small">Riassunto scritto a mano da noi {con_art("il", data_it(f.get("scritto_il") or DOC_IT["controllato_il"]))} sulla scheda aggiornata '
            f'{con_art("il", data_it(p["aggiornata"]))}: se la scheda cambia, lo togliamo finché non la rileggiamo.</p>')


def sezione_doc_it(v):
    p, n = v["p"], escape(v["luogo"])
    D, V = p["documento"], p["validita"]
    b, frase = doc_it(D)
    h = f'<h2 id="documento">Serve il passaporto per andare {n}? Basta la carta d\'identità?</h2>'
    if not D.get("esito"):
        h += (f'<p><strong>Consulta la scheda ufficiale.</strong> {escape(frase)} Leggi il campo «Passaporto» della '
              f'<a href="{escape(p["url"])}" rel="noopener">scheda ufficiale</a>.</p>')
    else:
        h += f'<p class="cifra">In breve: <strong>{escape(b)}.</strong></p><p>{escape(frase)}</p>'
        h += '<p class="small" style="margin-bottom:0">Dalla scheda, campo «Passaporto» (citazioni brevi):</p>' + _cit_lista(list(D.get("citazioni") or [D.get("citazione")]))
        if D.get("condizione") and not D.get("sintesi"):
            h += '<p class="small" style="margin-bottom:0">La condizione indicata dalla scheda:</p>' + _cit_lista([D["condizione"]])
        if D.get("note_speciali") and not D.get("sintesi"):
            h += ('<p class="small">La scheda contiene anche avvertenze su casi particolari (per esempio carte d\'identità rinnovate con proroga, documenti '
                  f'provvisori cartacei o documenti danneggiati): leggile nella <a href="{escape(p["url"])}" rel="noopener">scheda ufficiale</a> e, per i '
                  f'documenti italiani, nell\'approfondimento <a href="{VS_DOCUMENTI}" rel="noopener">«Documenti di viaggio»</a> di Viaggiare Sicuri.</p>')
        h += nota_manuale_it(p, D)
    h += f'<h2 id="validita">Quanto deve essere valido {"il documento" if D.get("esito") == "cie" else "il passaporto"} per andare {n}?</h2>'
    bv, fv = val_it(V)
    if not V.get("esito"):
        h += (f'<p><strong>Consulta la scheda ufficiale.</strong> {escape(fv)} Leggi il campo «Passaporto» della '
              f'<a href="{escape(p["url"])}" rel="noopener">scheda ufficiale</a>.</p>')
    else:
        fv1, fv2 = _prima_frase(fv)
        h += (f'<p class="cifra">In breve: <strong>{escape(fv1.rstrip("."))}.</strong></p>' + (f'<p>{escape(fv2)}</p>' if fv2 else "")
              + ('<p class="small">La validità indicata dalla scheda vale per il documento con cui viaggi, carta d\'identità o passaporto.</p>' if D.get("esito") == "cie" else "")
              + '<p class="small" style="margin-bottom:0">Dalla scheda, campo «Passaporto»:</p>' + _cit_lista(V.get("citazioni") or [V.get("citazione")])
              + nota_manuale_it(p, V))
    return h + fonte_it(p, ["Passaporto"])


def sezione_visto_it(v):
    p, n = v["p"], escape(v["luogo"])
    S = p["visto"]
    h = f'<h2 id="visto">Serve il visto per andare {n}?</h2>'
    breve, titolo, altre = vis_it(S)
    campo_v = TITOLI_CAMPI_IT.get(S.get("campo") or "visto", "Visto di ingresso")
    if not S.get("esito"):
        return h + (f'<p><strong>Consulta la scheda ufficiale.</strong> Non riassumiamo questo campo: {escape(_minuscola(S.get("motivo") or "").rstrip("."))}. '
                    f'Leggi il campo «Visto di ingresso» della <a href="{escape(p["url"])}" rel="noopener">scheda ufficiale</a>.</p>') + fonte_it(p, ["Visto di ingresso"])
    h += f'<p class="cifra">In breve: <strong>{escape(titolo_visto_it(S))}.</strong></p>'
    if S.get("sintesi"):
        t = S["sintesi"]
        if t.startswith(titolo + "."):
            t = t[len(titolo) + 1:].lstrip()
        h += f'<p>{escape(t)}</p>' if t else ""
    if S.get("durata"):
        h += f'<p>Durata indicata dalla scheda: «{escape(S["durata"])}».</p>'
    elif (S["esito"] == "non_necessario" and not S.get("sintesi") and p["documento"].get("esito") != "cie"
          and not re.search(r"\bU\.?E\.?\b|Schengen", S.get("citazione") or "")):
        h += '<p>Per sapere quanto tempo puoi restare senza visto, leggi la scheda.</p>'
    form = S.get("formalita", [])  # già nel titolo «In breve» (titolo_visto_it)
    for x in altre:
        h += f"<p>{escape(x)}</p>"
    note = list(S.get("note", []))
    if not S.get("manuale"):
        if S.get("consigli"):
            note.append("La scheda consiglia anche di compilare un modulo o una registrazione online: leggi i dettagli.")
        if S.get("registrazione_locale"):
            note.append("La scheda indica anche una registrazione dopo l'arrivo (di solito fatta dall'albergo, altrimenti presso la polizia o gli uffici indicati).")
        if S.get("tasse"):
            note.append("La scheda cita anche tasse o costi da pagare: importi, casi e modalità nella scheda.")
        if S.get("altri_casi"):
            note.append("Per soggiorni più lunghi, lavoro, studio, transiti o altri casi la scheda dà regole diverse.")
        if S["esito"] == "necessario":
            if S.get("arrivo") or S.get("online"):
                note.append("Come ottenerlo (consolato o ambasciata, richiesta online, rilascio all'arrivo) e quanto costa: la scheda lo spiega, leggila prima di partire.")
            else:
                note.append("Come e dove chiederlo: leggi la scheda prima di partire.")
            if S.get("eccezioni"):
                note.append("La scheda indica anche eccezioni o casi particolari.")
    pp = S.get("obblighi_pp", [])
    if pp:
        note.append("Nel riquadro «Documenti e visti» la scheda scrive anche un obbligo per chi entra (modulo, dichiarazione, assicurazione o registrazione): leggi la citazione qui sotto e la scheda prima di partire.")
    if note:
        h += "<ul>" + "".join(f"<li>{escape(x)}</li>" for x in note) + "</ul>"
    # citazioni a gruppi, ognuno con la sua etichetta: sul visto, su ogni autorizzazione o modulo, sugli altri dettagli
    h += f'<p class="small" style="margin-bottom:0">Dalla scheda, campo «{campo_v}» (citazioni brevi). Sul visto:</p>' + _cit_lista(list(S.get("citazioni") or [S.get("citazione")]))
    for f in form:
        h += f'<p class="small" style="margin-bottom:0">Su {escape(f["nome"])}:</p>' + _cit_lista([f["citazione"]])
    if S.get("citazioni_note"):
        h += '<p class="small" style="margin-bottom:0">Sugli altri dettagli:</p>' + _cit_lista(S["citazioni_note"])
    if pp:
        h += '<p class="small" style="margin-bottom:0">Dalla scheda, riquadro «Documenti e visti» (In primo piano):</p>' + _cit_lista(pp)
    h += nota_manuale_it(p, S)
    return h + fonte_it(p, [campo_v] + (["Documenti e visti"] if pp and campo_v != "Documenti e visti" else []))


def faq_it(v):
    """Domande e risposte solo dai fatti riassunti (le stesse frasi della pagina)."""
    p, n = v["p"], v["luogo"]
    D, V, S = p["documento"], p["validita"], p["visto"]
    data = data_it(p["aggiornata"])
    coda = f" (scheda Viaggiare Sicuri aggiornata {con_art('il', data)})."
    out = []
    if D.get("esito"):
        b, frase = doc_it(D)
        if D["esito"] != "cie_condizioni":  # con le condizioni la risposta giusta è quella sulla carta d'identità, qui sotto
            r1 = frase if D["esito"] != "cie" else "No, non per forza: " + frase[0].lower() + frase[1:]
            if r1.startswith("No: "):  # la frase risponde a «Basta la carta d'identità?» (Regno Unito): qui la risposta è sì
                r1 = "Sì: " + r1[4:]
            out.append((f"Serve il passaporto per andare {n}?", r1.rstrip(".") + coda))
        r = {"cie": "Sì: " + frase[0].lower() + frase[1:], "cie_condizioni": frase, "solo_passaporto": frase,
             "passaporto": "Non secondo la scheda della Farnesina, che indica il passaporto e non cita la carta d'identità tra i documenti per entrare."}[D["esito"]]
        out.append((f"Basta la carta d'identità per andare {n}?", r.rstrip(".") + coda))
    if V.get("esito"):
        doc = "il documento" if D.get("esito") == "cie" else "il passaporto"
        out.append((f"Quanto deve essere valido {doc} per andare {n}?", val_it(V)[1].rstrip(".") + coda))
    if S.get("esito"):
        breve, titolo, altre = vis_it(S)
        r = S.get("sintesi") or (titolo_visto_it(S) + (f"; durata indicata dalla scheda: «{S['durata']}»" if S.get("durata") else ""))
        out.append((f"Serve il visto per andare {n}?", r.rstrip(".") + coda))
    return out


def titoli_it(v):
    N, cie = v["nome"], v["p"]["documento"].get("esito") == "cie"
    if v["p"]["documento"].get("esito") == "cie_condizioni":  # Egitto, Turchia, Georgia, Montenegro: si cerca «... con la carta d'identità»
        return [f"{N}: basta la carta d'identità? Documenti per italiani {ANNO}", f"{N}: basta la carta d'identità? Documenti {ANNO}",
                f"{N}: carta d'identità o passaporto? {ANNO}", f"{N}: documenti per italiani {ANNO}", f"{N}: documenti {ANNO}"]
    if cie:
        return [f"{N} con la carta d'identità? Documenti per italiani {ANNO}", f"{N} con la carta d'identità? Documenti {ANNO}",
                f"{N}: carta d'identità o passaporto? {ANNO}", f"{N}: documenti per italiani {ANNO}", f"{N}: documenti {ANNO}"]
    return [f"{N}: serve il passaporto? Documenti e visto per italiani {ANNO}", f"{N}: serve il passaporto? Visto per italiani {ANNO}",
            f"{N}: passaporto e visto per italiani {ANNO}", f"{N}: documenti per italiani {ANNO}", f"{N}: documenti {ANNO}"]


def descrizioni_it(v):
    p = v["p"]
    db = {"cie": "passaporto o carta d'identità", "cie_condizioni": "carta d'identità solo a certe condizioni", "solo_passaporto": "solo passaporto",
          "passaporto": "serve il passaporto"}.get(p["documento"].get("esito"), "documento: vedi scheda")
    vb = val_it(p["validita"])[0] if p["validita"].get("esito") else ""
    sb = vis_it(p["visto"])[0]
    form = [_art_nome(f) for f in p["visto"].get("formalita", []) if f["tipo"] != "tessera turistica a pagamento"]
    vis = {"Non serve": "visto non necessario", "Serve": "visto necessario", "All'arrivo": "visto all'arrivo", "Vedi scheda": "visto: vedi la scheda"}.get(
        sb, ("visto non necessario, ma serve " + " e ".join(form)) if sb.startswith("Non serve") else "visto: " + _minuscola(sb))
    validita = f"; validità: {vb.lower()}" if vb else ""
    if p["validita"].get("esito") == "in_corso":  # non «validità: in corso di validità»
        db, validita = db + " in corso di validità", ""
    d = data_it_breve(p["aggiornata"])
    return [f"Per entrare {v['luogo']} con la cittadinanza italiana: {db}{validita}; {vis}. Fatti della scheda Farnesina {con_art("del", d)}, con link.",
            f"{v['nome']}, per italiani: {db}{validita}; {vis}. Fatti della scheda Farnesina {con_art("del", d)}.",
            f"{v['nome']}, per italiani: {db}; {vis}. Scheda Farnesina {con_art("del", d)}.",
            f"{v['nome']}: documenti e visto per chi ha la cittadinanza italiana, dalla scheda Farnesina {con_art("del", d)}."]


def pagina_it(v):
    rel = "../../../"
    p = v["p"]
    D, V, S = p["documento"], p["validita"], p["visto"]
    db, _ = doc_it(D)
    vb = _prima_frase(val_it(V)[1])[0] if V.get("esito") else "Consulta la scheda ufficiale"
    vt = titolo_visto_it(S)
    t_doc = {"cie": "t-ok", "cie_condizioni": "t-warn"}.get(D.get("esito"), "")
    t_vis = ("t-warn" if S.get("formalita") or S.get("obblighi_pp") else "t-ok") if S.get("esito") == "non_necessario" else \
        {"necessario": "t-no", "all_arrivo": "t-warn", "autorizzazione": "t-warn"}.get(S.get("esito"), "")
    riga = lambda tono, etichetta, valore, ancora: (f'<div class="{tono}"><dt>{etichetta}</dt><dd>{escape(valore.rstrip("."))}. '
                                                   f'<a href="#{ancora}">Dettagli ›</a></dd></div>')
    righe = ('<dl class="fatti-it">' + riga(t_doc, "Documento", db, "documento")
             + riga("", "Validità " + ("del documento" if D.get("esito") == "cie" else "del passaporto"), vb, "validita")
             + riga(t_vis, "Visto", vt, "visto") + "</dl>")
    extra = ""
    for x in p.get("note_extra", []):
        extra += (f'<h2>Da sapere prima di partire</h2><p>{escape(x["testo"])}</p>'
                  f'<p class="small" style="margin-bottom:0">Dalla scheda, campo «{escape(TITOLI_CAMPI_IT[x["campo"]])}»:</p>' + _cit_lista(x["citazioni"])
                  + nota_manuale_it(p, x))
    crono = [c for c in p.get("cronologia", []) if re.search(r"Requisiti|Revisione generale", c["nota"], re.I)][:2]
    if crono:
        extra += ('<p class="small">Ultimi aggiornamenti della scheda che riguardano i requisiti di ingresso (dalla cronologia della scheda): ' +
                  "; ".join(f"{data_it_breve(c['data'])}, «{escape(c['nota'])}»" for c in crono) + ".</p>")
    faq = faq_it(v)
    faq_html = ('<section class="faq"><h2>Domande frequenti</h2>' +
                "".join(f"<h3>{escape(q)}</h3><p>{escape(a)}</p>" for q, a in faq) + "</section>") if faq else ""
    uk = "".join(f'<p class="altri-pass" lang="en">{ico("passport")}<span>British passport: <a href="{rel}passport-validity/{s}/" hreflang="en">{escape(UK_NOMI[s])} entry requirements for British passport holders</a></span></p>'
                 for s in v["uk"])
    simili = []
    if D.get("esito") == "cie":
        simili = [w for w in VOCI_IT if w is not v and w["p"]["documento"].get("esito") == "cie"][:12]
    grid = (f'<h2>Altri Paesi dove si entra con la carta d\'identità</h2><div class="griglia g-it">' +
            "".join(f'<a href="{rel}{w["url_pag"]}">{escape(w["nome"])}</a>' for w in simili) + "</div>") if simili else ""
    corpo = f"""<section class="hero"><h1>Documenti per viaggiare {escape(v['luogo'])}: passaporto, carta d'identità e visto</h1></section>
<section class="card summary" aria-label="In breve">
<div class="s-top s-it"><span class="sq">{ico("passport")}</span><span>Per italiani</span><span>Scheda {con_art("del", data_it_breve(p["aggiornata"]))}</span></div>
<div class="s-body">
{righe}
{fonte_it(p, ["Passaporto", "Visto di ingresso"])}
<p class="lead">Che documento serve a chi ha la cittadinanza italiana per entrare {escape(v['luogo'])}, quanto deve essere valido e se serve il visto: i fatti della scheda ufficiale di Viaggiare Sicuri, scritti con parole nostre, con brevi citazioni, la data della scheda e il link.</p>
</div>
</section>
{uk}
{AVVISO_IT}
{sezione_doc_it(v)}
{sezione_visto_it(v)}
{extra}
<p>Nella <a href="{escape(p['url'])}" rel="noopener">scheda ufficiale</a> trovi anche le regole per i viaggi dei minori, le formalità doganali e valutarie, la sicurezza e la situazione sanitaria del Paese.</p>
{faq_html}
{grid}
<p><a href="{rel}{IT_BASE}/">Documenti e visti: tutti i Paesi</a> · <a href="{rel}{IT_BASE}/#metodo">Come leggiamo le schede</a></p>"""
    ld = [{"@context": "https://schema.org", "@type": "WebPage", "name": f"Documenti per viaggiare {v['luogo']}: passaporto, carta d'identità e visto",
           "url": f"{URL_SITO}/{v['url_pag']}", "inLanguage": "it", "isBasedOn": p["url"], "dateModified": DOC_IT["controllato_il"],
           "isPartOf": {"@type": "WebSite", "name": NOME, "url": URL_SITO + "/"}}]
    if faq:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "it",
                   "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
    pagina(v["url_pag"], scegli(titoli_it(v), LIMITE_TITOLO), scegli(descrizioni_it(v), LIMITE_DESCRIZIONE), corpo,
           briciole=[("Documenti per italiani", f"{IT_BASE}/"), (v["nome"], v["url_pag"])], js=FILTRO_JS, ld_extra=ld, lingua="it")


TITOLI_CAMPI_IT = {"passaporto": "Passaporto", "visto": "Visto di ingresso", "primo_piano": "Documenti e visti"}  # "primo_piano" = riquadro "In primo piano"
FILTRO_JS = r"""
(function(){document.querySelectorAll('[data-filtro]').forEach(function(inp){var lista=document.getElementById(inp.dataset.filtro);
  inp.addEventListener('input',function(){var v=inp.value.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
    lista.querySelectorAll('[data-voce]').forEach(function(a){var t=a.textContent.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');a.hidden=!!v&&t.indexOf(v)<0;});});});})();
"""


def _breve_doc_indice(p):
    e = p["documento"].get("esito")
    d = {"cie": "Passaporto o carta d'identità", "cie_condizioni": "Carta d'identità solo a condizioni", "solo_passaporto": "Solo passaporto",
         "passaporto": "Passaporto"}.get(e, "Vedi scheda")
    V = p["validita"]
    if V.get("esito") == "numero":
        d += f" · almeno {V['n']} {V['unita']}"
    elif V.get("esito") == "soggiorno":
        d += " · valido per il soggiorno"
    elif V.get("esito") == "rientro":
        d += " · scadenza dopo il rientro"
    return d


MOLTO_CERCATI_IT = ["EGY", "TUR", "USA", "GBR", "ALB", "TUN", "MAR", "THA", "JPN", "MDV", "CUB", "DOM", "MEX", "CPV", "KEN", "TZA", "GEO", "MNE"]


def indice_it():
    rel = "../../"
    righe = []
    for v in sorted(VOCI_IT + SENZA_PAGINA_IT, key=lambda v: unicodedata.normalize("NFKD", v["nome"]).encode("ascii", "ignore").decode().lower()):
        p = v["p"]
        if v in VOCI_IT:
            nome = f'<a href="{rel}{v["url_pag"]}">{escape(v["nome"])}</a>'
            doc, vis = _breve_doc_indice(p), vis_it(p["visto"])[0]
        else:
            rim = p.get("rimando")
            dest = IT_PER_ISO.get(rim)
            nome = (f'{escape(v["nome"])} <span class="small">(<a href="{escape(p["url"])}" rel="noopener">scheda ufficiale</a>'
                    + (f', che rimanda a <a href="{rel}{dest["url_pag"]}">{escape(dest["nome"])}</a>' if dest else "") + ")</span>")
            doc, vis = "Vedi scheda", "Vedi scheda"
        righe.append(f'<tr data-voce><td>{nome}</td><td data-l="Documento">{escape(doc)}</td><td data-l="Visto">{escape(vis)}</td>'
                     f'<td>Scheda {con_art("del", data_it_breve(p["aggiornata"]))}</td></tr>')
    cie = [v for v in VOCI_IT if v["p"]["documento"].get("esito") == "cie"]
    cond = [v for v in VOCI_IT if v["p"]["documento"].get("esito") == "cie_condizioni"]
    n_doc = sum(1 for v in VOCI_IT if v["p"]["documento"].get("esito"))
    n_val = sum(1 for v in VOCI_IT if v["p"]["validita"].get("esito"))
    n_vis = sum(1 for v in VOCI_IT if v["p"]["visto"].get("esito"))
    n_man = sum(1 for v in VOCI_IT for k in ("documento", "validita", "visto") if v["p"][k].get("manuale"))
    tot = len(VOCI_IT) + len(SENZA_PAGINA_IT)
    senza = ", ".join(f'<a href="{escape(v["p"]["url"])}" rel="noopener">{escape(v["nome"])}</a>' for v in SENZA_PAGINA_IT)
    corpo = f"""<section class="hero">{h1_diviso(f"Documenti per l'estero con la cittadinanza italiana: passaporto, carta d'identità e visto ({ANNO})")}
<p class="lead">Serve il passaporto o basta la carta d'identità? Quanto deve essere valido il passaporto? Serve il visto? Per {tot} Paesi e territori, i fatti delle schede ufficiali di Viaggiare Sicuri (Farnesina), scritti con parole nostre, con la data di ogni scheda e il link.</p>
<p class="fonte">Fonte: <a href="{VS_HOME}" rel="noopener">Viaggiare Sicuri</a>, Unità di Crisi del Ministero degli Affari Esteri e della Cooperazione Internazionale, schede Paese (campi «Passaporto» e «Visto di ingresso») · lette da noi {con_art("il", data_it(DOC_IT["controllato_il"]))}</p>
</section>
{AVVISO_IT}
<h2>Le mete più cercate</h2>
<div class="griglia g-it">{"".join(f'<a href="{rel}{IT_PER_ISO[i]["url_pag"]}">{escape(IT_PER_ISO[i]["nome"])}<small>{escape(_breve_doc_indice(IT_PER_ISO[i]["p"]).split(" · ")[0])}<br>Visto: {escape(_minuscola(vis_it(IT_PER_ISO[i]["p"]["visto"])[0]))}</small></a>' for i in MOLTO_CERCATI_IT if i in IT_PER_ISO)}</div>
<h2>Tutti i Paesi</h2>
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Scrivi un Paese, per esempio Egitto, Turchia, Stati Uniti" data-filtro="lista-it" aria-label="Cerca un Paese"></div>
<div class="tab tab-e"><table><thead><tr><th>Paese</th><th>Passaporto o carta d'identità</th><th>Visto</th><th>Scheda ufficiale</th></tr></thead><tbody id="lista-it">{"".join(righe)}</tbody></table></div>
<p class="small">Etichette brevi nostre. «Vedi scheda»: la scheda non permette un riassunto sicuro (condizioni, casi diversi, autorizzazioni o moduli senza dettagli chiari): leggila. «Non serve + ETA»: niente visto, ma un'autorizzazione elettronica o un modulo obbligatorio prima di partire o all'arrivo.</p>
<h2>Dove si entra con la carta d'identità</h2>
<p>Secondo le schede, si entra con la carta d'identità elettronica (CIE) oppure con il passaporto in {len(cie)} Paesi e territori:</p>
<div class="griglia g-it">{"".join(f'<a href="{rel}{v["url_pag"]}">{escape(v["nome"])}</a>' for v in cie)}</div>
<p>Solo a certe condizioni (per esempio solo per turismo, solo da alcuni confini o solo per soggiorni brevi): {", ".join(f'<a href="{rel}{v["url_pag"]}">{escape(v["nome"])}</a>' for v in cond) or "nessuno"}. Per le carte d'identità rinnovate con proroga, i documenti provvisori cartacei e i viaggi dei minori leggi anche l'approfondimento <a href="{VS_DOCUMENTI}" rel="noopener">«Documenti di viaggio»</a> di Viaggiare Sicuri.</p>
<h2 id="metodo">Fonte e metodo</h2>
<div class="testo">
<p><strong>Fonte.</strong> Le schede Paese di <a href="{VS_HOME}" rel="noopener">Viaggiare Sicuri</a>, il sito dell'Unità di Crisi della Farnesina, lette dai file pubblici che il sito stesso usa ({DOC_IT["schede_elenco"]} schede, {con_art("il", data_it(DOC_IT["controllato_il"]))}). Per ogni Paese usiamo i campi «Passaporto» e «Visto di ingresso» della sezione «Requisiti di ingresso»; il riquadro «Documenti e visti» della sezione «In primo piano» serve come controllo (se dice il contrario, non riassumiamo) e per segnalare, con una citazione, gli obblighi scritti solo lì (moduli, dichiarazioni, assicurazioni). Ogni pagina mostra la data di aggiornamento della scheda e il link.</p>
<p><strong>Testi e licenza.</strong> Viaggiare Sicuri non indica una licenza per i testi delle schede. Per questo non li ripubblichiamo: riportiamo i fatti (documento richiesto, validità residua, visto, autorizzazioni, durata ammessa) con parole nostre e citiamo solo frasi brevi, tra virgolette, quando servono per precisione. Per tutto il resto rimandiamo alla scheda ufficiale.</p>
<p><strong>Regole prudenti.</strong> Riassumiamo un fatto solo se la scheda lo scrive con una formula chiara (per esempio «Passaporto oppure CIE», «con almeno 6 (sei) mesi di validità residua», «Il visto d'ingresso non è necessario»). Non riassumiamo quando la frase ha condizioni o casi diversi, quando le validità indicate sono più d'una, quando l'esenzione dal visto è temporanea o «preventiva», o quando la scheda parla di autorizzazioni elettroniche, moduli o registrazioni senza dettagli chiari: in quei casi la pagina scrive «Consulta la scheda ufficiale». Per {n_man} fatti di Paesi molto cercati (per esempio Regno Unito, Stati Uniti, Egitto, Turchia, Thailandia) la lettura automatica non bastava e li abbiamo scritti a mano leggendo la scheda: valgono solo per la versione della scheda letta, e se la scheda cambia vengono scartati finché non la rileggiamo.</p>
<p><strong>Risultato ({data_it(DOC_IT["controllato_il"])}).</strong> {len(VOCI_IT)} pagine Paese; documento riassunto per {n_doc} Paesi, validità del passaporto per {n_val}, visto per {n_vis}. Nessuna pagina per {len(SENZA_PAGINA_IT)} schede, dove non c'era abbastanza da riassumere con sicurezza: {senza}.</p>
<p>Le regole valgono per chi ha la cittadinanza italiana. La compagnia aerea e le autorità di frontiera del Paese decidono se puoi partire o entrare.</p>
</div>"""
    pagina(f"{IT_BASE}/", f"Documenti per l'estero {ANNO}: passaporto, carta d'identità, visto",
           f"Serve il passaporto o basta la carta d'identità? Serve il visto? Per {tot} Paesi, i fatti delle schede Farnesina (Viaggiare Sicuri) con data e link.",
           corpo, briciole=[("Documenti per italiani", f"{IT_BASE}/")], js=FILTRO_JS, lingua="it")


# ---------------------------------------------------------------- liquidi
ETICHETTE = {"2l": "Up to 2 litres", "100ml": "100 ml", "dipende": "Depends on checkpoint", "contraddice": "Official pages disagree"}
RISPOSTA = {"2l": "2 litres", "100ml": "100 ml", "dipende": "It depends on the checkpoint", "contraddice": "Official pages disagree – plan for 100 ml"}


def etichetta(A):
    """Etichetta breve della regola; 'etichetta' nel file la sostituisce dove la regola non dipende dal varco (Zurigo: dal viaggio)."""
    return A.get("etichetta") or ETICHETTE[A["regola"]]


def badge(regola, A=None):
    return f'<span class="badge b-{regola}">{escape(etichetta(A)) if A else ETICHETTE[regola]}</span>'


def cit_html(frasi):
    return '<blockquote class="cit">' + "".join(f"<p>{escape(f)}</p>" for f in frasi) + "</blockquote>"


def fonte_liq(A):
    lett = "" if A["lettura"] == "diretta" else " (the site blocks simple automated requests or needs JavaScript, so we read it in a browser)"
    return (f'<p class="fonte">Official source: <a href="{escape(A["url"])}" rel="noopener">{escape(A["titolo_fonte"])}</a> · checked on '
            f'{data_lunga(A["controllato_il"])}{lett}</p>')


def contesto_html(rel):
    out = []
    for C in AER["contesto"]:
        nota = f'<p class="small">{escape(C["nota"])}</p>' if C.get("nota") else ""
        lic = f' Licence: <a href="{OGL}" rel="noopener">{escape(C["licenza"])}</a>.' if C.get("licenza") else ""
        out.append(f'<h3>{escape(C["ente"])}</h3>{cit_html(C["citazioni"])}{nota}'
                   f'<p class="fonte">Source: <a href="{escape(C["url"])}" rel="noopener">{escape(C["titolo"])}</a> · checked on {data_lunga(C["controllato_il"])}.{lic}</p>')
    return "".join(out)


# Risposta diretta in alto (sì/no) presa dalla regola in dati/aeroporti.json; "risposta" nel file la sostituisce dove serve una sfumatura.
SI_NO = {"2l": "Yes", "100ml": "No", "dipende": "It depends on the checkpoint", "contraddice": "Not clear: the official texts disagree"}
# nome nel <title> come lo cerca la gente ("heathrow liquid rules", "barcelona airport liquid rules"); nel testo resta il nome completo del file
NOMI_TITOLO = {"madeira": "Madeira Funchal", "barcelona": "Barcelona", "alicante": "Alicante", "malaga": "Malaga", "lanzarote": "Lanzarote", "doha": "Doha Hamad",
               "athens": "Athens", "dubai": "Dubai", "malta": "Malta", "heathrow": "Heathrow", "gatwick": "Gatwick", "stansted": "Stansted", "luton": "Luton",
               "rome-fiumicino": "Rome Fiumicino", "milan-malpensa": "Milan Malpensa", "milan-linate": "Milan Linate", "gothenburg-landvetter": "Gothenburg",
               "stockholm-arlanda": "Stockholm Arlanda", "madrid": "Madrid", "palma-de-mallorca": "Palma", "amsterdam-schiphol": "Amsterdam Schiphol",
               "liverpool": "Liverpool", "berlin": "Berlin"}
SIGLA_PAESE = {"United States": "US", "Canada": "Canadian"}
# contesto (GOV.UK / Your Europe) da citare nelle FAQ quando la pagina dell'aeroporto non dice il dettaglio: per Paese
PAESI_UE = {"Ireland", "Germany", "Austria", "Italy", "Finland", "Sweden", "Denmark", "Netherlands", "Czechia", "Poland", "Portugal", "Spain", "Greece", "Malta",
            "Belgium", "Hungary", "France", "Croatia", "Cyprus", "Luxembourg", "Slovakia", "Slovenia", "Romania", "Bulgaria", "Estonia", "Latvia", "Lithuania"}


def nome_titolo(A):
    return NOMI_TITOLO.get(A["slug"], A["nome"])


def dove_liq(A, nazionale=False):
    """Come si nomina l'aeroporto nelle domande: 'Barcelona-El Prat (BCN)' oppure 'US airports'."""
    if nazionale:
        return f"{SIGLA_PAESE.get(A['paese'], A['paese'])} airports"
    return f"{A['nome']} ({A['iata']})"


def risposta_liq(A):
    return A.get("risposta") or SI_NO[A["regola"]]


def frase_risposta(A):
    return f"{risposta_liq(A)}. {A['sintesi']}."


def sigla_ente(A):
    return A["ente"].split("(")[-1].rstrip(")")


def dipende_da(A):
    """'checkpoint' o 'journey' (Zurigo): da cosa dipende la regola, dall'etichetta del file."""
    return etichetta(A).lower().replace("depends on ", "").strip() or "checkpoint"


def titoli_liquidi(A, nazionale=False):
    """Titoli scritti come le ricerche ('<aeroporto> liquid rules 2026', '100ml'), con la regola vera nel titolo; la prima forma che sta in 65 caratteri."""
    if nazionale:
        x, e = SIGLA_PAESE.get(A["paese"], A["paese"]), sigla_ente(A)
        return [f"{x} Airport Liquid Rules {ANNO} ({e}): 100ml Limit Still Applies", f"{x} Airport Liquid Rules {ANNO} ({e}): 100ml Limit",
                f"{x} Airport Liquid Rules {ANNO} ({e})"]
    n, i, r = nome_titolo(A), A["iata"], A["regola"]
    if r == "2l":
        code = [f"{n} Airport ({i}) Liquid Rules {ANNO}: 2 Litres Allowed, Not 100ml", f"{n} ({i}) Liquid Rules {ANNO}: 2 Litres Allowed, Not 100ml",
                f"{n} ({i}) Liquid Rules {ANNO}: Up to 2 Litres"]
    elif r == "100ml":
        code = [f"{n} Airport ({i}) Liquid Rules {ANNO}: 100ml Limit Still Applies", f"{n} ({i}) Liquid Rules {ANNO}: 100ml Limit Still Applies",
                f"{n} ({i}) Liquid Rules {ANNO}: 100ml Limit"]
    elif r == "dipende":
        da = dipende_da(A).capitalize()
        code = [f"{n} Airport ({i}) Liquid Rules {ANNO}: 100ml or 2 Litres by {da}", f"{n} ({i}) Liquid Rules {ANNO}: 100ml or 2 Litres by {da}",
                f"{n} ({i}) Liquid Rules {ANNO}: 100ml or 2L by {da}"]
    else:  # contraddice
        code = [f"{n} Airport ({i}) Liquid Rules {ANNO}: 100ml or 2 Litres? Pages Disagree", f"{n} ({i}) Liquid Rules {ANNO}: 100ml or 2 Litres? Pages Disagree",
                f"{n} ({i}) Liquid Rules {ANNO}: 100ml or 2 Litres?"]
    return code + [f"{n} ({i}) Liquid Rules {ANNO}"]


def h1_liquidi(A, nazionale=False):
    """H1 coerente con il titolo: nome completo, sigla, 'liquid rules 2026', '100ml' e 'hand luggage' come scrive chi cerca."""
    if nazionale:
        return f"{A['paese']} airport liquid rules {ANNO} ({sigla_ente(A)}): the 100ml limit for liquids in hand luggage"
    n, i, r = A["nome"], A["iata"], A["regola"]
    coda = {"2l": "up to 2 litres per container in hand luggage, not 100ml", "100ml": "the 100ml limit for liquids in hand luggage",
            "dipende": f"100ml or 2 litres in hand luggage, depending on the {dipende_da(A)}",
            "contraddice": "100ml or 2 litres in hand luggage? The official pages disagree"}[r]
    if A["slug"] == "belfast-international":  # la pagina dice "up to 2 litres" senza "per container"
        coda = "liquids up to 2 litres in hand luggage, not 100ml"
    return f"{n} Airport ({i}) liquid rules {ANNO}: {coda}"


def frase_diretta(A, nazionale=False):
    """Risposta diretta in una o due frasi, costruita solo dalla regola, dalla risposta e dalla sintesi del file."""
    d, r, s = dove_liq(A, nazionale), risposta_liq(A), A["sintesi"]
    s_min = s if s.split()[0] in ("Terminal", "Terminals") else s[0].lower() + s[1:]  # iniziale minuscola dopo i due punti, salvo i nomi propri
    if A["regola"] == "2l":
        return f"{r}: at {d} you can take liquids over 100ml through security, as the official page quoted below says: {s_min}."
    if A["regola"] == "100ml":
        return f"{r}: at {d} the 100ml rule still applies to liquids in hand luggage, as the official page quoted below says: {s_min}."
    if A["regola"] == "dipende":
        return f"{r}. At {d}: {s_min}. The official page is quoted below."
    return f"{r}. At {d}, two official texts give different limits: {s_min}. Both are quoted below."


def descrizioni_liquidi(A, nazionale=False):
    d, r, sx, c = dove_liq(A, nazionale), risposta_liq(A), A["sintesi"], data_lunga(A["controllato_il"])
    return [f"Can you take liquids over 100ml in hand luggage at {d}? {r}. {sx}. Official page quoted word for word, checked {c}.",
            f"Can you take liquids over 100ml in hand luggage at {d}? {r}. {sx}. Official page quoted, checked {c}.",
            f"Liquids over 100ml in hand luggage at {d}? {r}. {sx}. Official page quoted.",
            f"Liquids over 100ml at {d}? {r}. {sx}.",
            f"Can you take liquids over 100ml in hand luggage at {d}? {r}. Official rules quoted word for word, checked {c}.",
            f"{d} liquid rules {ANNO}: {r}. The official page quoted word for word, with the date we checked it."]


def frasi_ufficiali_liq(A):
    """Citazioni della pagina ufficiale principale da cui possono venire le risposte delle FAQ (mai testo nostro)."""
    ff = list(A["citazioni"]) + list(A.get("eccezioni", []))
    K = A.get("contrasto")
    if A["regola"] == "contraddice" and K and K.get("url") == A["url"]:  # stessa pagina (Monaco)
        ff.append(K["citazione"])
    return ff


def prefisso_faq(A):
    return f"Quoted from {A['titolo_fonte']} (checked on {data_lunga(A['controllato_il'])}): "


def contesto_di(A):
    """La pagina di governo da citare quando la pagina dell'aeroporto non dice il dettaglio: GOV.UK per il Regno Unito, Your Europe per l'UE, altrimenti nessuna."""
    if A.get("paese") == "United Kingdom":
        k = "uk"
    elif A.get("paese") in PAESI_UE:
        k = "eu"
    else:
        return None
    return next(C for C in AER["contesto"] if C["id"] == k)


def prefisso_contesto(C):
    return f"Quoted from {C['titolo']} (checked on {data_lunga(C['controllato_il'])}): "


RX_FUORI_TEMA = re.compile(r"body scanner|walk through|security scanner that|non-invasive", re.I)  # frasi sui portali per le persone, non sui liquidi
FAQ_LIQ = [  # (chiave, domanda, filtro sulle frasi ufficiali): la frase deve parlare proprio di quello che chiede la domanda; None = citazioni principali
    ("limite", "Can I take liquids over 100ml through security at {d}?", None),
    ("terminal", "Are the liquids rules different by terminal or checkpoint at {d}?",
     re.compile(r"\bterminals?\b|\bgates?\b|security areas?|control areas?|transfer|\blanes?\b|signs|CT technology|CT scanners?|computed tomography"
                r"|which security checkpoint|some security checkpoints|following checkpoints|entrance security|one stop security", re.I)),
    ("scanner", "Does {d} have the new CT scanners, and can liquids stay in my bag?",
     re.compile(r"CT scanners?|CT security|CT technology|computed tomography|next[- ]generation|new (?:security )?technology|new scanners?|state of the art security"
                r"|stay in|remain in|remain within|leave (?:your )?liquids|inside hand|in their hand|in your (?:hand|cabin) (?:luggage|bag)|take them out|remov"
                r"|separately|separate from|tray|kept in your", re.I)),
    ("busta", "Do liquids have to go in a plastic bag at {d}, and how big can it be?",
     re.compile(r"plastic bags?|re-?sealable|clear bag|transparent bag|lit(?:re|er) bag|liquid bag|quart-sized bag|20 ?cm ?x ?20|20 x 20|1L in capacity", re.I)),
    ("baby", "Can I take baby food and medicines over 100ml through security at {d}?",
     re.compile(r"\bbaby\b|infant|breast milk|formula|medicin|medication|prescription|dietary|inhaler", re.I)),
    ("dutyfree", "Can I carry duty-free liquids over 100ml through {d}?",
     re.compile(r"duty[- ]free|tamper|STEB|bought after|purchased after|airport shops|security bag|bought in the airport|sealed (?:duty|security|bag containing)", re.I)),
    ("borraccia", "Can I take a reusable bottle or flask through security at {d}?", re.compile(r"bottle|flask|thermos|double-walled|double-skinned|insulated", re.I)),
    ("2026", "What are the liquid rules at {d} in {anno}, and are they changing?", None),
]
# Risposte nostre quando la pagina ufficiale non dice il dettaglio: dicono che la pagina non lo dice e rimandano alla regola standard.
# verifica.py controlla che ogni risposta in testo nostro corrisponda a uno di questi modelli.
MANCA_LIQ = {
    "scanner": "The passages we quote from the official page do not say whether {n} uses CT scanners or whether liquids can stay in your bag: follow the signs and the staff at the checkpoint.",
    "busta": "The passages we quote from the official page do not mention a plastic bag or a limit on the number of bags.",
    "baby": "The passages we quote from the official page do not list exemptions for baby food or medicines.",
    "dutyfree": "The passages we quote from the official page do not cover duty-free liquids bought at another airport.",
}
RINVIO_LIQ = {  # coda del rimando alla regola standard, per contesto (uk, eu, nessuno)
    "uk": "GOV.UK sets out the standard rule and exemptions for UK airports on its hand luggage restrictions page; check with the airport and your airline before you pack.",
    "eu": "Your Europe sets out the standard EU rule and exemptions; check with the airport and your airline before you pack.",
    None: "Check with the airport and your airline before you pack.",
}


def gruppi_liq(A, ff):
    """Le frasi ufficiali a gruppi, nell'ordine della pagina: un titolo (frase che finisce con ':' o elencata in 'intestazioni')
    resta unito alle frasi che lo seguono, così una risposta non cita mai un titolo da solo né una frase fuori dal suo titolo."""
    tit = set(A.get("intestazioni", []))

    def apre(x):
        return x in tit or x.rstrip().endswith(":")
    out = []
    for f in ff:
        if apre(f) or not out or not apre(out[-1][0]):
            out.append([f])
        else:
            out[-1].append(f)
    return out


def faq_liquidi(A, nazionale=False):
    """Sei domande (quattro se la pagina non dà spunti). Ogni risposta è: le citazioni ufficiali intere che parlano di quel tema
    (mai tagliate), oppure, se la pagina non lo dice, una frase nostra da MANCA_LIQ + RINVIO_LIQ che lo dichiara, con la citazione
    della pagina di governo (GOV.UK / Your Europe) dove c'è. La prima e l'ultima risposta partono dalla regola e dalla sintesi del file.
    Ritorna [(domanda, testo nostro o '', [(prefisso fonte, [citazioni])])]; verifica.py ricontrolla tutto."""
    pool = frasi_ufficiali_liq(A)
    gruppi = gruppi_liq(A, list(A["citazioni"])) + gruppi_liq(A, [f for f in pool if f not in A["citazioni"]])
    d, C, pre = dove_liq(A, nazionale), contesto_di(A), prefisso_faq(A)
    ctx = C["id"] if C else None
    voci = {}
    for chiave, dom, rx in FAQ_LIQ:
        if chiave in A.get("faq_salta", []):  # domanda che non si adatta a questa pagina (es. Zurigo: dipende dal viaggio, non dal varco)
            continue
        q = dom.format(d=d, anno=ANNO)
        if chiave == "limite":
            ff = list(pool) if A["regola"] in ("dipende", "contraddice") else list(A["citazioni"])
            voci[chiave] = (q, frase_risposta(A), [(pre, ff)])
        elif chiave == "2026":
            testo = (f"As of {data_lunga(A['controllato_il'])}, the official page says: {frase_risposta(A)} Rules can change at short notice and the "
                     f"airport's page is our only source, so check it again before you fly.")
            blocchi = [(prefisso_contesto(C), [x for x in C["citazioni"] if "depend on the airport" in x or "up to 2 litres" in x])] if C and ctx == "uk" else \
                      ([(prefisso_contesto(C), list(C["citazioni"]))] if C else [])
            voci[chiave] = (q, testo, blocchi)
        else:
            ff = [f for g in gruppi if any(rx.search(x) and not RX_FUORI_TEMA.search(x) and not (chiave != "dutyfree" and re.search(r"tamper|duty", x, re.I)) for x in g) for f in g]
            if ff:
                voci[chiave] = (q, "", [(pre, ff)])
            elif chiave in MANCA_LIQ:
                testo = MANCA_LIQ[chiave].format(n=A["nome"]) + ("" if chiave == "scanner" else " " + RINVIO_LIQ[ctx])
                blocchi = [(prefisso_contesto(C), list(C["citazioni"]))] if (C and chiave == "busta") else []
                voci[chiave] = (q, testo, blocchi)
    # ordine: limite, terminal (solo con citazioni), i temi con citazioni, poi quelli senza, borraccia (solo con citazioni), 2026; al massimo 6
    centro = [k for k in ("scanner", "busta", "baby", "dutyfree") if k in voci]
    centro = [k for k in centro if voci[k][2] and not voci[k][1]] + [k for k in centro if not (voci[k][2] and not voci[k][1])]
    ordine = ["limite"] + (["terminal"] if "terminal" in voci else []) + centro + (["borraccia"] if "borraccia" in voci else []) + ["2026"]
    while len(ordine) > 6:
        senza = [k for k in ordine if k in MANCA_LIQ and voci[k][1]]
        ordine.remove(senza[-1] if senza else ordine[-2])
    return [voci[k] for k in ordine]


def testo_faq(intro, blocchi):
    """Testo della risposta per il JSON-LD: frase nostra (se c'è) + 'Quoted from <fonte> (checked on <data>): “…” “…”' per ogni blocco."""
    parti = ([intro] if intro else []) + [p + " ".join(f"“{f}”" for f in ff) for p, ff in blocchi if ff]
    return " ".join(parti)


def html_faq(A, faq):
    if not faq:
        return "", []
    h = ""
    for q, intro, blocchi in faq:
        h += f"<h3>{escape(q)}</h3>" + (f"<p>{escape(intro)}</p>" if intro else "")
        for p, ff in blocchi:
            if ff:
                h += cit_html(ff) + ("" if p == prefisso_faq(A) else f'<p class="fonte">{escape(p.rstrip(": "))}.</p>')
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": testo_faq(intro, blocchi)}} for q, intro, blocchi in faq]}
    return (f'<section class="faq"><h2>Questions about liquids at {escape(A["nome"])}: 100ml rule, bags, scanners, baby food, duty-free</h2>'
            f'<p class="small">Quotations are word for word from the official pages named; the plain-text answers are ours and come only from the rule '
            f'and summary shown at the top of this page. Where the passages we quote do not say, we say so.</p>{h}{fonte_liq(A)}</section>'), [ld]


def pagina_aeroporto(A, nazionale=False):
    rel = "../../"
    titolo_breve = A["nome"]
    h1 = h1_liquidi(A, nazionale)
    eccezioni = (f"<h2>Liquids in hand luggage at {escape(A['nome'])}: exceptions and other details (official)</h2>" + cit_html(A["eccezioni"])) if A.get("eccezioni") else ""
    fonte2 = ""
    if A.get("fonte2"):
        f2 = A["fonte2"]
        fonte2 = ((cit_html(f2["citazioni"]) if f2.get("citazioni") else "") +
                  f'<p class="fonte">Also from: <a href="{escape(f2["url"])}" rel="noopener">{escape(f2["titolo"])}</a> · checked on {data_lunga(A["controllato_il"])}</p>')
    contrasto = ""
    if A.get("contrasto"):
        K = A["contrasto"]
        commento = K.get("commento") or "We do not choose between the two: if you cannot confirm the rule for your checkpoint with the airport, pack for 100 ml."
        contrasto = (f'<h2>{escape(K.get("intestazione") or "But another official text says something different")}</h2>{cit_html([K["citazione"]])}'
                     f'<p class="fonte">Source: <a href="{escape(K["url"])}" rel="noopener">{escape(K["titolo"])}</a> · checked on {data_lunga(A["controllato_il"])}</p>'
                     f'<p>{escape(commento)}</p>')
    nota = f'<p class="small">{escape(A["nota"])}</p>' if A.get("nota") else ""
    simili = [B for B in AER["aeroporti"] if B is not A and B.get("paese") == A.get("paese")]
    titolo_simili = f"Other airports in {A['paese']}"
    if not simili and not nazionale:  # Paese con un solo aeroporto (Jersey): gli altri della stessa area
        simili = [B for B in AER["aeroporti"] if B is not A and B.get("area") == A.get("area")]
        titolo_simili = f"Other airports: {A['area']}"
    link_simili = ""
    if simili:
        link_simili = (f"<h2>{escape(titolo_simili)}</h2><div class=\"griglia\">" +
                       "".join(f'<a href="{rel}liquids/{B["slug"]}/">{escape(B["nome"])} ({B["iata"]})<small>{escape(etichetta(B))}</small></a>' for B in simili) + "</div>")
    faq_html, faq_ld = html_faq(A, faq_liquidi(A, nazionale))
    corpo = f"""<section class="hero"><h1>{escape(h1)}</h1></section>
<section class="card summary" aria-label="Summary">
<div class="s-top"><span class="sq">{ico("bottle")}</span><span>Liquids · hand luggage</span><span>{escape(A.get("iata") or A.get("paese") or "")}</span></div>
<div class="s-body">
<p class="cifra">Can I take liquids over 100 ml through security at {escape(dove_liq(A, nazionale))}? <strong>{escape(frase_risposta(A))} {badge(A['regola'], A)}</strong></p>
<p class="lead">{escape(frase_diretta(A, nazionale))}{escape(" The source is Aena's general hand-luggage page, not a page for this airport.") if A.get('gestore') == 'aena' else ''}</p>
{fonte_liq(A)}
</div>
</section>
{AVVISO_LIQ}
<h2>100ml rule at {escape(A['nome'])}: what the official page says</h2>
{cit_html(A['citazioni'])}
{fonte_liq(A)}
{fonte2}
{nota}
{eccezioni}
{contrasto}
{AD}
{faq_html}
{link_simili}
<h2>Flying back?</h2>
<p>The UK government's advice is to check the rules “at the airport you’re flying from” and “at any other airports you’ll be travelling through, including your return journey” (<a href="https://www.gov.uk/hand-luggage-restrictions/liquids" rel="noopener">GOV.UK, hand luggage restrictions</a>). See the <a href="{rel}liquids/">liquids rules at {len(AER['aeroporti'])} airports</a>{'' if nazionale else f', the <a href="{rel}liquids/us-airports-tsa/">US (TSA) rule</a> and the <a href="{rel}liquids/canada-airports-catsa/">Canada (CATSA) rule</a>'}.</p>
<h2>Cabin bag size for your airline</h2>
<p>How big can your hand luggage be? See the <a href="{rel}cabin-bags/">cabin bag size by airline</a> ({len(COMPAGNIE)} airlines, from their official pages) or <a href="{rel}cabin-bags/does-my-bag-fit/">check if your bag fits</a>.</p>
<h2>Medicines, baby food and duty-free</h2>
<p>Exemptions are set out on the official page linked above. For UK airports, GOV.UK lists them on its <a href="https://www.gov.uk/hand-luggage-restrictions/liquids" rel="noopener">hand luggage restrictions page</a>; for EU airports, see <a href="https://europa.eu/youreurope/citizens/travel/carry/luggage-restrictions/index_en.htm" rel="noopener">Your Europe</a>.</p>
<p class="small">Spotted a change? <a href="{rel}contact/?ref=liq-{A['slug']}">Tell us</a>.</p>
{box_affiliati()}
<p><a href="{rel}liquids/">All airports</a> · <a href="{rel}passport-validity/">Passport validity and visa rules</a> · <a href="{rel}ees-etias/">EES and ETIAS status</a></p>"""
    pagina(f"liquids/{A['slug']}/", scegli(titoli_liquidi(A, nazionale), LIMITE_TITOLO), scegli(descrizioni_liquidi(A, nazionale), LIMITE_DESCRIZIONE), corpo,
           briciole=[("Liquids by airport", "liquids/"), (titolo_breve, f"liquids/{A['slug']}/")], ld_extra=faq_ld)


def indice_liquidi():
    rel = "../"
    gruppi = {}
    for A in AER["aeroporti"]:
        gruppi.setdefault(A["area"], []).append(A)
    conta = {k: sum(1 for A in AER["aeroporti"] if A["regola"] == k) for k in ETICHETTE}
    tabelle = []
    for area in ["UK and Ireland", "Europe", "Middle East and Asia", "Australia and North America"]:
        if area not in gruppi:
            continue
        righe = "".join(f'<tr><td><a href="{rel}liquids/{A["slug"]}/">{escape(A["nome"])}</a> <span class="small">{A["iata"]}</span></td><td>{escape(A["paese"])}</td>'
                        f'<td>{badge(A["regola"], A)}</td><td>{escape(A["sintesi"])}</td><td><a href="{escape(A["url"])}" rel="noopener">official</a>, {data_lunga(A["controllato_il"])}</td></tr>'
                        for A in sorted(gruppi[area], key=lambda x: x["nome"]))
        tabelle.append(f'<h2>{escape(area)}</h2><div class="tab"><table><thead><tr><th>Airport</th><th>Country</th><th>Limit per container</th><th>Details</th><th>Source</th></tr></thead><tbody>{righe}</tbody></table></div>')
    naz = "".join(f'<tr><td><a href="{rel}liquids/{N["slug"]}/">{escape(N["nome"])}</a></td><td>{badge(N["regola"])}</td><td>{escape(N["sintesi"])}</td>'
                  f'<td><a href="{escape(N["url"])}" rel="noopener">official</a>, {data_lunga(N["controllato_il"])}</td></tr>' for N in AER["nazionali"])
    esclusi = "".join(f"<li><strong>{escape(E['nome'])}</strong>: {escape(E['motivo'])}</li>" for E in AER["esclusi"])
    corpo = f"""<section class="hero">{h1_diviso(f"Liquids rules by airport {ANNO}: 100 ml or 2 litres?")}
<p class="lead">What is the liquid limit at your airport? Some airports with new CT scanners now let you carry liquids in containers of up to 2 litres; many still apply the 100 ml limit, and some only at certain checkpoints. Here is what each airport's official page says, quoted word for word, with the date we checked it.</p>
<p class="cifra" style="margin-top:10px">Of the {len(AER['aeroporti'])} airports below:</p>
<ul class="stat"><li><strong>{conta['2l']}</strong> up to 2 litres</li><li><strong>{conta['100ml']}</strong> 100 ml</li><li><strong>{conta['dipende']}</strong> depends on the checkpoint</li><li><strong>{conta['contraddice']}</strong> with official pages that disagree</li></ul>
</section>
{AVVISO_LIQ}
{''.join(tabelle[:1])}
{AD}
{''.join(tabelle[1:])}
<h2>National rules (one rule for every airport)</h2>
<div class="tab"><table><thead><tr><th>Country</th><th>Limit</th><th>Details</th><th>Source</th></tr></thead><tbody>{naz}</tbody></table></div>
<h2>What governments say</h2>
{contesto_html(rel)}
<h2>Airports not included (yet)</h2>
<p>We only publish an airport when we can read its official page and the rule on it is clear. Not included on {data_lunga(AER['controllato_il'])}:</p>
<ul>{esclusi}</ul>
<p class="small">Last checked: {data_lunga(AER['controllato_il'])} (each airport row shows its own date). Spotted a change? <a href="{rel}contact/?ref=liquids">Tell us</a>.</p>
<p>Packing hand luggage? See the <a href="{rel}cabin-bags/">cabin bag size by airline</a>.</p>
{box_affiliati()}"""
    pagina("liquids/", f"Airport Liquid Rules {ANNO}: 100 ml or 2 Litres? ({len(AER['aeroporti'])} Airports)",
           f"The liquid limit at {len(AER['aeroporti'])} airports: which allow 2 litres and which keep 100 ml (Heathrow, Barcelona, Berlin, Prague, Palma…), plus US TSA rules. Official, dated.",
           corpo, briciole=[("Liquids by airport", "liquids/")])


# ---------------------------------------------------------------- EES / ETIAS
def frasi_ees(argomento):
    return [f for f in EES["frasi"] if f["argomento"] == argomento and f["trovata"]]


def fonti_ees(frasi):
    chiavi = []
    for f in frasi:
        if f["pagina"] not in chiavi:
            chiavi.append(f["pagina"])
    out = []
    for k in chiavi:
        p = EES["pagine"][k]
        mod = f", page updated {data_lunga(p['modificata'])}" if p.get("modificata") else ""
        out.append(f'<a href="{escape(p["url"])}" rel="noopener">{escape(p["titolo"])}</a>{mod}')
    return f'<p class="fonte">Official source: {" · ".join(out)} · checked on {data_lunga(EES["controllato_il"])}</p>'


def pagina_ees():
    rel = "../"
    etias = frasi_ees("etias")
    ees = frasi_ees("ees")
    gov = [g["frase"] for g in EES["govuk"]["frasi"] if g["trovata"]]
    G = EES["govuk"]
    stato_etias = "Not in operation" if any("currently not in operation" in f["frase"] for f in etias) else "Check the official page"
    stato_ees = "Fully operational since 10 April 2026" if any("fully operational" in f["frase"] for f in ees) else "Check the official page"
    corpo = f"""<section class="hero"><h1>EES and ETIAS: official status today ({MESI[date.fromisoformat(EES['controllato_il']).month - 1]} {ANNO})</h1>
<p class="lead">The EU's Entry/Exit System (EES) and the future travel authorisation ETIAS, in the European Commission's own words, with what UK travellers need to do now according to GOV.UK. No predictions: only official statements, with the date we checked them.</p>
</section>
<div class="tre">
<section class="card"><span class="sq">{ico("scan")}</span><h2>EES</h2><p class="cifra"><strong>{escape(stato_ees)}</strong></p><p class="small" style="margin:0">Registration of fingerprints and a facial image at the Schengen border for short stays.</p></section>
<section class="card"><span class="sq">{ico("shield")}</span><h2>ETIAS</h2><p class="cifra"><strong>{escape(stato_etias)}</strong></p><p class="small" style="margin:0">Start date: the EU says it will announce it several months before launch.</p></section>
<section class="card"><span class="sq">{ico("passport")}</span><h2>Your passport</h2><p class="small" style="margin:0">Schengen rules for British passports: <a href="{rel}passport-validity/france/">10-year issue rule and 3 months after you leave</a>.</p></section>
</div>
<h2>ETIAS: what the European Commission says</h2>
{cit_html([f['frase'] for f in etias])}
{fonti_ees(etias)}
<p>We do not publish expected start dates for ETIAS: the Commission says the EU will announce the date several months before launch. Last checked: {data_lunga(EES['controllato_il'])}.</p>
{AD}
<h2>EES: what the European Commission says</h2>
{cit_html([f['frase'] for f in ees])}
{fonti_ees(ees)}
<h2>What UK travellers need to do now (GOV.UK)</h2>
{cit_html(gov)}
<p class="fonte">Official source: <a href="{escape(G['url'])}" rel="noopener">{escape(G['titolo'])}</a> · page updated {data_lunga(G['aggiornata'])} · checked on {data_lunga(EES['controllato_il'])} · <a href="{OGL}" rel="noopener">Open Government Licence v3.0</a>. The same text appears in the FCDO advice for other Schengen countries.</p>
<h2>Official EU website for EES and ETIAS</h2>
<p>The EU's official site for travellers is travel-europe.europa.eu: <a href="{escape(EES['sito_ufficiale']['ees'])}" rel="noopener">EES page</a> and <a href="{escape(EES['sito_ufficiale']['etias'])}" rel="noopener">ETIAS page</a>. Our server could not read it on {data_lunga(EES['controllato_il'])} (its security certificate chain was incomplete for automated tools), so we quote the European Commission pages above instead.</p>
<p class="avviso">This page is information, not legal advice. Border guards apply the rules at the border. Before you travel, check the official pages linked above and your airline, ferry or train operator.</p>
{box_affiliati()}
<p><a href="{rel}passport-validity/">Passport validity rules</a> · <a href="{rel}liquids/">Liquids rules by airport</a></p>"""
    pagina("ees-etias/", f"EES and ETIAS status {ANNO}: official EU statements",
           "Is ETIAS in operation? Is EES live? The European Commission's own statements, and what UK travellers must do now according to GOV.UK, with dates.",
           corpo, briciole=[("EES and ETIAS", "ees-etias/")])


# ---------------------------------------------------------------- bagaglio a mano per compagnia aerea
# Dati: dati/bagagli.json (misure lette sulle pagine ufficiali delle compagnie, ognuna con la frase copiata parola per parola).
# Il confronto "la mia borsa entra?" è scritto qui in Python (entra_borsa, esito_compagnia) e identico in JS (BAG_JS): verifica.py li confronta.
BAG = json.loads((DATI / "bagagli.json").read_text(encoding="utf-8")) if (DATI / "bagagli.json").exists() else {"compagnie": [], "escluse": []}
COMPAGNIE = BAG["compagnie"]
BAG_BASE = "cabin-bags"
BAG_STRUMENTO = f"{BAG_BASE}/does-my-bag-fit/"
BAG_UE = f"{BAG_BASE}/eu-personal-item-rule/"
# Misure comuni (le più cercate: borse vendute "per Ryanair", "per easyJet", trolley da cabina): slug come lo scrive la gente
MISURE_COMUNI = [("40x30x20", (40, 30, 20)), ("40x30x15", (40, 30, 15)), ("40x20x25", (40, 20, 25)), ("45x36x20", (45, 36, 20)),
                 ("40x30x25", (40, 30, 25)), ("55x40x20", (55, 40, 20)), ("55x40x23", (55, 40, 23)), ("55x35x25", (55, 35, 25)),
                 ("55x40x25", (55, 40, 25)), ("56x45x25", (56, 45, 25))]
INCLUSO = {"tutte": "Free with every fare", "alcune": "Only with some fares, cabins or as a paid extra"}
ESITO = {"gratis": "Free with every fare", "altre": "Only with some fares or paid", "no": "Too big for the cabin"}
DOVE = {"sotto": "Under the seat", "sopra": "Overhead locker"}
EPS = 1e-6


def entra_borsa(misure, unita, b):
    """La borsa (3 misure nell'unità 'cm' o 'in') sta nel limite b? Si confrontano le misure ordinate (lato più lungo con il limite più lungo,
    e così via): è la condizione esatta perché una scatola stia in un'altra senza inclinarla. In pollici si usano i pollici ufficiali se la
    compagnia li pubblica, altrimenti i centimetri (1 in = 2,54 cm). Il totale (Delta: 45 pollici / 114 cm) si controlla nella stessa unità."""
    if unita == "in" and b.get("pollici") and b.get("pollici_ufficiali"):
        lim, mis, u = list(b["pollici"]), list(misure), "in"
    else:
        lim, mis, u = list(b["cm"]), [x * 2.54 for x in misure] if unita == "in" else list(misure), "cm"
    mis.sort(reverse=True)
    lim.sort(reverse=True)
    ok = all(mis[i] <= lim[i] + EPS for i in range(3))
    if b.get("totale") and sum(mis) > b["totale"][u] + EPS:
        ok = False
    return ok


def esito_compagnia(misure, unita, C):
    """'gratis' se entra in una borsa compresa in ogni tariffa, 'altre' se entra solo in una borsa con alcune tariffe o a pagamento, 'no' altrimenti."""
    esito, quale = "no", None
    for b in C["borse"]:
        if entra_borsa(misure, unita, b):
            if b["incluso"] == "tutte" and esito != "gratis":
                esito, quale = "gratis", b["id"]
            elif b["incluso"] == "alcune" and esito == "no":
                esito, quale = "altre", b["id"]
    return esito, quale


BAG_JS = r"""
function bfNum(s){s=String(s==null?'':s).trim().replace(',','.');if(!/^\d+(\.\d+)?$/.test(s))return NaN;return parseFloat(s);}
function bfEntra(m,u,b){var lim,mis,un;
  if(u==='in'&&b.i&&b.iu){lim=b.i.slice();mis=m.slice();un='in';}else{lim=b.c.slice();mis=u==='in'?m.map(function(x){return x*2.54;}):m.slice();un='cm';}
  var d=function(a,b){return b-a;};mis.sort(d);lim.sort(d);var ok=true;for(var k=0;k<3;k++){if(mis[k]>lim[k]+1e-6)ok=false;}
  var tot=null;if(b.t){tot=b.t[un];if(mis[0]+mis[1]+mis[2]>tot+1e-6)ok=false;}
  return {ok:ok,mis:mis,lim:lim,u:un,tot:tot};}
function bfCompagnia(m,u,C){var es='no',q=null;C.b.forEach(function(b){var r=bfEntra(m,u,b);
  if(r.ok){if(b.inc==='tutte'&&es!=='gratis'){es='gratis';q=b;}else if(b.inc==='alcune'&&es==='no'){es='altre';q=b;}}});return {esito:es,borsa:q};}
(function(){
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function n2(x){return String(Math.round(x*100)/100);}
  function tre(a,u){return a.map(n2).join(' × ')+' '+u;}
  var box=document.querySelector('[data-borsa]');if(!box)return;
  var D=JSON.parse(document.getElementById(box.dataset.dati).textContent);var f=box.querySelector('form');var out=box.querySelector('[data-out]');
  var ETI={gratis:'Free with every fare',altre:'Only with some fares or paid',no:'Too big for the cabin'};
  function aggiorna(){
    var u=f.querySelector('[name=unita]').value;var v=['a','b','c'].map(function(n){return bfNum(f.querySelector('[name='+n+']').value);});
    var vuoti=['a','b','c'].every(function(n){return !f.querySelector('[name='+n+']').value.trim();});
    if(vuoti){out.innerHTML='<p class="small" style="margin:0">Enter the three sides of your bag (any order), including wheels and handles.</p>';return;}
    var max=u==='in'?120:300;
    if(v.some(function(x){return isNaN(x)||x<=0||x>max;})){out.innerHTML='<p class="errore" data-errore-borsa style="margin:0">Enter three numbers greater than 0 (up to '+max+' '+u+'), for example 40, 30 and 20. Use a dot or a comma for decimals.</p>';return;}
    var gruppi={gratis:[],altre:[],no:[]};
    D.forEach(function(C){var r=bfCompagnia(v,u,C);gruppi[r.esito].push([C,r]);});
    var ord=v.slice().sort(function(a,b){return b-a;});
    var h='<p class="cifra" style="margin:0 0 6px">Your bag, longest side first: <strong>'+tre(ord,u)+'</strong></p><ul class="stat" data-conti>'+
      ['gratis','altre','no'].map(function(k){return '<li><strong data-conto="'+k+'">'+gruppi[k].length+'</strong> '+ETI[k].toLowerCase()+'</li>';}).join('')+'</ul>';
    ['gratis','altre','no'].forEach(function(k){if(!gruppi[k].length)return;
      h+='<h3 class="es-'+k+'">'+ETI[k]+' ('+gruppi[k].length+')</h3><ul class="esiti" data-gruppo="'+k+'">';
      gruppi[k].forEach(function(x){var C=x[0],r=x[1],sp;
        if(r.borsa){var e=bfEntra(v,u,r.borsa);sp='Fits the '+esc(r.borsa.n)+' ('+(r.borsa.w==='sotto'?'under the seat':'overhead locker')+'): your bag '+tre(e.mis,e.u)+' against the limit '+tre(e.lim,e.u)+(e.u==='cm'&&!r.borsa.cu&&r.borsa.i?' (≈, official '+tre(r.borsa.i,'in')+')':'')+(e.tot?(', total '+n2(e.tot)+' '+e.u):'')+(r.borsa.p?' · weight limit: '+esc(r.borsa.p):'')+'.';}
        else{sp='Bigger than every size '+esc(C.n)+' publishes: '+C.b.map(function(b){var e=bfEntra(v,u,b);return esc(b.n)+' '+tre(e.lim,e.u)+(e.u==='cm'&&!b.cu&&b.i?' (≈, official '+tre(b.i,'in')+')':'')+(e.tot?(' (total '+n2(e.tot)+' '+e.u+')'):'');}).join('; ')+'.'+(C.ps?' '+esc(C.n)+' also allows a personal item but publishes no size for it.':'');}
        if(C.m)sp+=' <em>'+esc(C.m)+'</em>';
        h+='<li data-slug="'+C.s+'"><a href="'+esc(box.dataset.base+C.s)+'/"><strong>'+esc(C.n)+'</strong></a> <span class="small">'+sp+'</span></li>';});
      h+='</ul>';});
    out.innerHTML=h;}
  f.addEventListener('input',aggiorna);f.addEventListener('change',aggiorna);f.addEventListener('submit',function(e){e.preventDefault();aggiorna();});aggiorna();
})();
"""


def n2(x):
    return f"{round(x, 2):g}"


def dims(a, u, dec=2):
    return " x ".join(f"{round(x, dec):g}" for x in a) + f" {u}"


def misura_testo(b, C=None):
    """Misura nell'unità della fonte, con l'altra unità (ufficiale se la fonte la scrive, altrimenti conversione nostra con ≈).
    Per il Nord America prima i pollici, se la compagnia li pubblica."""
    if C is not None and nordamerica(C) and b["cm_ufficiali"] and b.get("pollici") and b.get("pollici_ufficiali"):
        return dims(b["pollici"], "in") + f" ({dims(b['cm'], 'cm')})"
    if b["cm_ufficiali"]:
        s = dims(b["cm"], "cm")
        if b.get("pollici") and b.get("pollici_ufficiali"):
            return s + f" ({dims(b['pollici'], 'in')})"
        return s + f" (≈ {dims([x / 2.54 for x in b['cm']], 'in', 1)})"
    return dims(b["pollici"], "in") + f" (≈ {dims(b['cm'], 'cm', 1)})"


def misura_breve(b, C=None):
    """Forma breve per titoli ed elenchi, dal lato più lungo ("40x30x20 cm", come si cerca); pollici per il Nord America se la compagnia li pubblica."""
    pollici = (not b["cm_ufficiali"]) or (C is not None and nordamerica(C) and b.get("pollici") and b.get("pollici_ufficiali"))
    v = sorted(b["pollici"] if pollici else b["cm"], reverse=True)
    return "x".join(n2(x) for x in v) + (" in" if pollici else " cm")


def borsa_gratis(C, tipo=None):
    return next((b for b in C["borse"] if b["incluso"] == "tutte" and (tipo is None or b["tipo"] == tipo)), None)


def poss(nome):
    """Genitivo inglese: "Delta Air Lines'", "Ryanair's"."""
    return nome + ("'" if nome.endswith("s") else "'s")


def nordamerica(C):
    return C["area"] == "North America"


def nome_sotto(C):
    return "personal item" if nordamerica(C) else "under-seat bag"


def risposta_bag(C):
    """Risposta diretta in alto: la borsa gratis sotto il sedile (o, se non ha misura, la borsa compresa nella cappelliera)."""
    s = borsa_gratis(C, "sotto") or borsa_gratis(C, "sopra")
    if nordamerica(C) and s.get("pollici") and s.get("pollici_ufficiali"):
        m = dims(s["pollici"], "in") + (f" ({dims(s['cm'], 'cm')})" if s["cm_ufficiali"] else "")
    else:
        m = dims(s["cm"], "cm") if s["cm_ufficiali"] else dims(s["pollici"], "in")
    if s["tipo"] == "sotto":
        return f"{C['nome']} free {'personal item' if nordamerica(C) else 'bag'}: {m} under the seat"
    return f"{C['nome']} free carry-on: {m} in the overhead bin"


def titoli_bag(C):
    n = C["nome"].replace(" Airlines", "").replace(" Air Lines", "")
    s, o = borsa_gratis(C, "sotto"), borsa_gratis(C, "sopra")
    alt = next((b for b in C["borse"] if b["tipo"] == "sopra"), None)
    if nordamerica(C):
        if s and alt:
            a, p_ = misura_breve(alt, C), misura_breve(s, C)
            return [f"{n} Carry-On Size {ANNO}: {a} + {p_} Personal Item", f"{n} Carry-On Size {ANNO}: {a.replace(' in', '')} & {p_.replace(' in', '')} in",
                    f"{n} Carry-On & Personal Item Size {ANNO}", f"{n} Carry-On Size {ANNO}"]
        return [f"{n} Carry-On Size {ANNO}: {misura_breve(o, C)} & Personal Item", f"{n} Carry-On Size {ANNO}: {misura_breve(o, C)}", f"{n} Carry-On Size {ANNO}"]
    if s:
        return [f"{n} Cabin Bag Size {ANNO}: Free Bag {misura_breve(s)}", f"{n} Hand Luggage Size {ANNO}: {misura_breve(s)}", f"{n} Cabin Bag Size {ANNO}"]
    return [f"{n} Cabin Bag Size {ANNO}: Carry-On {misura_breve(o)}", f"{n} Cabin Bag Size {ANNO}"]


def descrizioni_bag(C):
    s, alt = borsa_gratis(C, "sotto"), next((b for b in C["borse"] if b["tipo"] == "sopra"), None)
    pezzi = []
    if s:
        pezzi.append(f"free {nome_sotto(C)} {misura_breve(s, C)}")
    if alt:
        pezzi.append(f"{'carry-on' if nordamerica(C) else 'cabin bag'} {misura_breve(alt, C)}" + (" (every fare)" if alt["incluso"] == "tutte" else " (some fares or paid)"))
    d = f"{C['nome']} {ANNO}: " + ", ".join(pezzi)
    return [f"{d}. Quoted from {poss(C['nome'])} official page with the date checked, plus a bag size checker.",
            f"{d}. Quoted from the official page, with the date checked.", f"{d}.", f"{C['nome']} cabin bag size {ANNO}: the official sizes, quoted word for word."]


def fonte_bag(C, chiavi=None):
    ff = [C["fonti"][k] for k in (chiavi or C["fonti"])]
    lett = any(f["lettura"] == "browser" for f in ff)
    return ('<p class="fonte">Official source: ' + " · ".join(f'<a href="{escape(f["url"])}" rel="noopener">{escape(f["titolo"])}</a>' for f in ff) +
            f' · checked on {data_lunga(C["controllato_il"])}' + (" (read in a browser)" if lett else "") + "</p>")


def cit_bag(cc):
    """Citazioni ufficiali: le righe della pagina restano righe separate."""
    return '<blockquote class="cit">' + "".join("<p>" + "<br>".join(escape(r) for r in c["righe"]) + "</p>" for c in cc) + "</blockquote>"


def testo_cit(c):
    return " ".join(c["righe"])


def unici(cc):
    out, visti = [], set()
    for c in cc:
        k = (c["f"], testo_cit(c))
        if k not in visti:
            visti.add(k)
            out.append(c)
    return out


def prefisso_bag(C, cc):
    nomi = []
    for c in cc:
        t = C["fonti"][c["f"]]["titolo"]
        if t not in nomi:
            nomi.append(t)
    return f"Quoted from {'; '.join(nomi)} (checked on {data_lunga(C['controllato_il'])}): "


def faq_bag(C):
    """Domande vere; ogni risposta è fatta SOLO di citazioni ufficiali intere (verifica.py lo controlla)."""
    out = []
    s = borsa_gratis(C, "sotto")
    if s:
        out.append((f"What size {nome_sotto(C)} can I bring for free on {C['nome']}?" if nordamerica(C) else f"What size is the free {C['nome']} under-seat bag?", s["cit"]))
    sopra = [c for b in C["borse"] if b["tipo"] == "sopra" for c in b["cit"]]
    if sopra:
        out.append((f"What is the {C['nome']} carry-on size limit?" if nordamerica(C) else f"What are the {C['nome']} cabin bag size and weight limits?", unici(sopra)))
    out.append((f"Is a {'carry-on bag' if nordamerica(C) else 'cabin bag'} included in every {C['nome']} fare?", unici([c for t in C["tariffe"] for c in t["cit"]])))
    if C["avvisi"]:
        out.append((f"Does {C['nome']} check the size of cabin bags?", C["avvisi"]))
    return out


def html_faq_bag(C):
    faq = faq_bag(C)
    h = "".join(f"<h3>{escape(q)}</h3>{cit_bag(cc)}" for q, cc in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": prefisso_bag(C, cc) + " ".join(f"“{testo_cit(c)}”" for c in cc)}} for q, cc in faq]}
    return (f'<section class="faq"><h2>Questions about {escape(C["nome"])} cabin bags</h2>'
            f'<p class="small">Every answer below is quoted word for word from {escape(poss(C["nome"]))} official page, not written by us.</p>{h}{fonte_bag(C)}</section>'), [ld]


AVVISO_BAG = ('<p class="avviso"><strong>Airlines change their bag rules and measure bags their own way</strong> (usually in a sizer at the airport, with wheels and '
              'handles). We quote each airline\'s official page on the date shown; the official rule and the airline staff decide. Check your booking before you fly.</p>')


def box_bagagli():
    """Riquadro per un futuro link a borse della misura giusta: vuoto (non mostrato) finché dati/affiliati.json non ha l'URL della voce 'bagagli'."""
    v = AFFILIATI.get("bagagli") or {}
    if not v.get("url"):
        return ""
    return (f'<section class="card" style="margin-top:22px"><h2 style="margin-top:0">{escape(v["titolo"])}</h2><p><a href="{escape(v["url"])}" rel="sponsored noopener" target="_blank">'
            f'{escape(v.get("nome", ""))}</a> {escape(v["testo"])}</p><p class="small" style="margin:0">Affiliate link: if you buy through it we may earn a small commission, at no extra cost to you.</p></section>')


def dati_bag_client():
    return [{"s": C["slug"], "n": C["nome"], "ps": bool(C.get("personale_senza_misura")), "m": C.get("nota_strumento"),
             "b": [{"n": b["nome"], "w": b["tipo"], "c": b["cm"], "cu": bool(b["cm_ufficiali"]), "i": b.get("pollici"), "iu": bool(b.get("pollici_ufficiali")), "t": b.get("totale"),
                    "inc": b["incluso"], "p": b.get("peso")} for b in C["borse"]]} for C in COMPAGNIE]


def modulo_borsa(rel):
    return f"""<section class="card checker" data-borsa data-dati="borse-dati" data-base="{rel}{BAG_BASE}/" aria-label="Does my bag fit?">
<div class="checker-h">{ico("bag")}<span>Does my bag fit? · {len(COMPAGNIE)} airlines</span></div>
<div class="checker-b"><form class="calc" novalidate>
<div class="campi campi-b">
<label><span class="lt">Side 1</span><input name="a" inputmode="decimal" autocomplete="off" placeholder="e.g. 40"></label>
<label><span class="lt">Side 2</span><input name="b" inputmode="decimal" autocomplete="off" placeholder="e.g. 30"></label>
<label><span class="lt">Side 3</span><input name="c" inputmode="decimal" autocomplete="off" placeholder="e.g. 20"></label>
<label><span class="lt">Unit</span><select name="unita"><option value="cm">cm</option><option value="in">inches</option></select></label>
</div>
<p class="small" style="margin:0">Any order: we compare your longest side with each airline's longest limit, the middle with the middle and the shortest with the shortest (the bag can be turned, not tilted). Measure the whole bag, wheels, handles and pockets included.</p>
<div class="risultato" data-out aria-live="polite"></div>
</form></div></section>"""


def nota_confronto():
    return ('<p class="small">How we compare: sides sorted from longest to shortest on both sides, so a 20 x 40 x 30 cm bag counts as 40 x 30 x 20 cm. '
            'An airline may measure in a fixed position (for example height x width x depth, or in its sizer) and may weigh the bag: the airline\'s official rule decides, '
            'not this page. In inches we use the airline\'s own inch figures where it publishes them, otherwise its centimetre figures (1 in = 2.54 cm). '
            'Where an airline publishes inches only, the centimetres shown with “≈” are our conversion.</p>')


def box_liquidi_bag(C, rel):
    """Riquadro sui liquidi nelle pagine compagnie: regola generale dei 100 ml (citazione GOV.UK) e rimando all'indice degli aeroporti.
    Nessuna regola per compagnia: il limite lo decide l'aeroporto, non la compagnia."""
    G = next(x for x in AER["contesto"] if x["id"] == "uk")
    due = sum(1 for A in AER["aeroporti"] if A["regola"] == "2l")
    return (f'<section class="card" style="margin-top:22px" aria-label="Liquids in hand luggage"><h2 style="margin-top:0">Liquids in your {escape(C["nome"])} cabin bag: the 100ml rule</h2>'
            f'<p>The liquid limit is set by the airport you go through security at, not by {escape(C["nome"])}. At most airports each container in your hand luggage '
            f'must be 100ml or less; {due} of the {len(AER["aeroporti"])} airports we track allow up to 2 litres, and some apply '
            f'different limits at different checkpoints.</p>{cit_html(G["citazioni"][:2])}'
            f'<p class="fonte">Quoted from <a href="{escape(G["url"])}" rel="noopener">{escape(G["titolo"])}</a> · checked on {data_lunga(G["controllato_il"])}. '
            f'Licence: <a href="{OGL}" rel="noopener">{escape(G["licenza"])}</a>.</p>'
            f'<p style="margin:0"><a href="{rel}liquids/">Liquid rules at {len(AER["aeroporti"])} airports, quoted from their official pages</a></p></section>')


def pagina_compagnia(C):
    rel = "../../"
    s, o = borsa_gratis(C, "sotto"), borsa_gratis(C, "sopra")
    righe = "".join(f'<tr><td data-l="Bag"><strong>{escape(b["nome"][0].upper() + b["nome"][1:])}</strong></td><td data-l="Where">{DOVE[b["tipo"]]}</td>'
                    f'<td data-l="Max size">{escape(misura_testo(b, C))}{" · total " + n2(b["totale"]["cm"]) + " cm / " + n2(b["totale"]["in"]) + " in" if b.get("totale") else ""}</td>'
                    f'<td data-l="Weight">{escape(b.get("peso") or "not stated")}</td><td data-l="Included"><span class="badge b-{"gratis" if b["incluso"] == "tutte" else "altre"}">'
                    f'{INCLUSO[b["incluso"]]}</span></td></tr>' for b in C["borse"])
    citaz = "".join(f'<h3>{escape(b["nome"][0].upper() + b["nome"][1:])}</h3>{cit_bag(b["cit"])}' for b in C["borse"])
    tar = "".join(f'<tr><td data-l="Fare">{escape(t["nome"])}</td><td data-l="Under the seat">{escape(t["sotto"])}</td><td data-l="Overhead">{escape(t["sopra"])}</td></tr>' for t in C["tariffe"])
    cit_tar = cit_bag(unici([c for t in C["tariffe"] for c in t["cit"]]))
    seconda = []
    for b in C["borse"]:
        if b is not (s or o):
            seconda.append(f'{b["nome"][0].upper() + b["nome"][1:]} ({DOVE[b["tipo"]].lower()}): {misura_testo(b, C)}' + (f', {b["peso"]}' if b.get("peso") else "") + f' – {INCLUSO[b["incluso"]].lower()}')
    extra = (f'<h2>Other official details</h2>{cit_bag(C["extra"])}') if C.get("extra") else ""
    nota = f'<p class="small">{escape(C["nota"])}</p>' if C.get("nota") else ""
    misura = f'<p class="avviso">{escape(C["misura"])}</p>' if C.get("misura") else ""
    ambito = f'<p class="small">These rules are for: {escape(C["ambito"])}.</p>' if C.get("ambito") else ""
    avvisi = (f'<h2>If your bag is too big</h2>{cit_bag(C["avvisi"])}') if C["avvisi"] else ""
    taglie = [(sl, m, esito_compagnia(m, "cm", C)[0]) for sl, m in MISURE_COMUNI]
    lista_taglie = "".join(f'<a href="{rel}{BAG_BASE}/size/{sl}/">{sl.replace("x", " x ")} cm<small>{ESITO[e]}</small></a>' for sl, m, e in taglie)
    altre = "".join(f'<a href="{rel}{BAG_BASE}/{D["slug"]}/">{escape(D["nome"])}<small>{escape(misura_breve(borsa_gratis(D, "sotto") or borsa_gratis(D, "sopra"), D))} free</small></a>'
                    for D in COMPAGNIE if D is not C and D["area"] == C["area"])
    faq_html, faq_ld = html_faq_bag(C)
    corpo = f"""<section class="hero"><h1>{escape(C["nome"])} {"carry-on size" if nordamerica(C) else "cabin bag size"} {ANNO}: {"personal item and carry-on" if nordamerica(C) else "free under-seat bag and cabin bag"} by fare</h1></section>
<section class="card summary" aria-label="Summary">
<div class="s-top"><span class="sq">{ico("bag")}</span><span>Cabin bags · {escape(C["nome"])}</span><span>{escape(C["paese"])}</span></div>
<div class="s-body">
<p class="cifra">What can I take on board for free? <strong>{escape(risposta_bag(C))}{" · " + escape((s or o)["peso"]) if (s or o).get("peso") else ""}</strong></p>
{"".join(f'<p class="lead">{escape(x)}.</p>' for x in seconda)}
{f'<p class="lead">Personal item: allowed with every fare, but {escape(C["nome"])} publishes no size for it (see the official wording below).</p>' if C.get("personale_senza_misura") else ""}
{ambito}
{fonte_bag(C)}
</div></section>
{AVVISO_BAG}
{misura}
<h2>{escape(C["nome"])} bags you can take on board</h2>
<div class="tab tab-b"><table><thead><tr><th>Bag</th><th>Where</th><th>Max size</th><th>Weight</th><th>Included</th></tr></thead><tbody>{righe}</tbody></table></div>
<p class="small">Sizes in the order {escape(C["nome"])} writes them. “≈” marks our conversion; the other figures are {escape(poss(C["nome"]))} own.</p>
<h2>What {escape(poss(C["nome"]))} official page says</h2>
{citaz}
{fonte_bag(C)}
{nota}
<h2>Cabin bag by fare</h2>
<div class="tab tab-b"><table><thead><tr><th>Fare</th><th>Under the seat</th><th>Overhead locker</th></tr></thead><tbody>{tar}</tbody></table></div>
<p class="small">Our short summary of the official wording below.</p>
{cit_tar}
{avvisi}
{extra}
{AD}
{faq_html}
{box_liquidi_bag(C, rel)}
<h2>Does my bag fit {escape(C["nome"])}?</h2>
<p>Check your own bag against {escape(C["nome"])} and {len(COMPAGNIE) - 1} other airlines with the <a href="{rel}{BAG_STRUMENTO}">bag size checker</a>. Common bag sizes:</p>
<div class="griglia">{lista_taglie}</div>
<h2>Other airlines ({escape(C["area"])})</h2>
<div class="griglia">{altre}</div>
<p class="small">Spotted a change? <a href="{rel}contact/?ref=bag-{C['slug']}">Tell us</a>.</p>
{box_bagagli()}
<p><a href="{rel}{BAG_BASE}/">Cabin bag size by airline</a> · <a href="{rel}{BAG_UE}">EU free personal item rule</a> · <a href="{rel}liquids/">Liquids rules by airport</a></p>"""
    pagina(f"{BAG_BASE}/{C['slug']}/", scegli(titoli_bag(C), LIMITE_TITOLO), scegli(descrizioni_bag(C), LIMITE_DESCRIZIONE), corpo,
           briciole=[("Cabin bags", f"{BAG_BASE}/"), (C["nome"], f"{BAG_BASE}/{C['slug']}/")], ld_extra=faq_ld)


def esiti_misura(m):
    return {k: [C for C in COMPAGNIE if esito_compagnia(m, "cm", C)[0] == k] for k in ESITO}


def titoli_misura(sl):
    return [f"{sl} Bag: Which Airlines Accept It Free? ({ANNO}, {len(COMPAGNIE)} Airlines)", f"{sl} cm Bag: Which Airlines Accept It? ({ANNO})", f"{sl} Bag Airlines {ANNO}"]


def pagina_misura(sl, m):
    rel = "../../../"
    E = esiti_misura(m)
    def riga(C, k):
        q = esito_compagnia(m, "cm", C)[1]
        b = next((x for x in C["borse"] if x["id"] == q), None)
        dett = (f'{escape(b["nome"])} ({DOVE[b["tipo"]].lower()}), max {escape(misura_testo(b, C))}' if b else
                "; ".join(f'{escape(x["nome"])} max {escape(misura_testo(x, C))}' for x in C["borse"]))
        return (f'<tr data-esito="{k}" data-slug="{C["slug"]}"><td data-l="Airline"><a href="{rel}{BAG_BASE}/{C["slug"]}/">{escape(C["nome"])}</a></td>'
                f'<td data-l="Result"><span class="badge b-{k}">{ESITO[k]}</span></td><td data-l="Allowance">{dett}</td></tr>')
    righe = "".join(riga(C, k) for k in ESITO for C in E[k])
    def elenco(k):
        return ", ".join(C["nome"] for C in E[k]) or "none"
    altre_m = "".join(f'<a href="{rel}{BAG_BASE}/size/{s2}/">{s2.replace("x", " x ")} cm<small>{len(esiti_misura(m2)["gratis"])} free with every fare</small></a>'
                      for s2, m2 in MISURE_COMUNI if s2 != sl)
    corpo = f"""<section class="hero"><h1>{sl.replace("x", " x ")} cm bag: which airlines accept it in {ANNO}?</h1>
<p class="lead">A bag of {dims(m, "cm")} (≈ {dims([x / 2.54 for x in m], "in", 1)}, our conversion), compared with the official cabin bag sizes of {len(COMPAGNIE)} airlines.</p></section>
<section class="card summary" aria-label="Summary">
<div class="s-top"><span class="sq">{ico("bag")}</span><span>Bag size · {sl}</span><span>{len(COMPAGNIE)} airlines</span></div>
<div class="s-body">
<p class="cifra">Free with every fare at <strong>{len(E["gratis"])} airline{"s" if len(E["gratis"]) != 1 else ""}</strong> <span class="nota-s">{escape(elenco("gratis"))}</span></p>
<p class="cifra">Only with some fares or as a paid extra at <strong>{len(E["altre"])}</strong> <span class="nota-s">{escape(elenco("altre"))}</span></p>
<p class="cifra">Too big for the cabin allowances at <strong>{len(E["no"])}</strong> <span class="nota-s">{escape(elenco("no"))}</span></p>
<p class="fonte">Calculated from the official pages of each airline, checked on {data_lunga(BAG["controllato_il"])}.</p>
</div></section>
{AVVISO_BAG}
<h2>Airline by airline</h2>
<div class="tab tab-b"><table><thead><tr><th>Airline</th><th>Result</th><th>Allowance it fits (or the sizes it does not fit)</th></tr></thead><tbody>{righe}</tbody></table></div>
{nota_confronto()}
{AD}
<h2>Check another size</h2>
<p>Enter your own bag in the <a href="{rel}{BAG_STRUMENTO}">bag size checker</a>, or see another common size:</p>
<div class="griglia">{altre_m}</div>
{box_bagagli()}
<p><a href="{rel}{BAG_BASE}/">Cabin bag size by airline</a> · <a href="{rel}{BAG_UE}">EU free personal item rule</a></p>"""
    desc = (f"Does a {sl} cm bag fit? Free with every fare at {len(E['gratis'])} of {len(COMPAGNIE)} airlines, {len(E['altre'])} only with some fares or paid. "
            "From official pages.")
    pagina(f"{BAG_BASE}/size/{sl}/", scegli(titoli_misura(sl), LIMITE_TITOLO), scegli([desc, f"Does a {sl} cm bag fit? {len(E['gratis'])} airlines accept it free with every fare."], LIMITE_DESCRIZIONE),
           corpo, briciole=[("Cabin bags", f"{BAG_BASE}/"), (f"{sl} bag", f"{BAG_BASE}/size/{sl}/")])


def pagina_strumento():
    rel = "../../"
    corpo = f"""<section class="hero">{h1_diviso(f"Does my bag fit? Cabin bag size checker for {len(COMPAGNIE)} airlines ({ANNO})")}
<p class="lead">Enter the three sides of your bag and see which airlines accept it free with every fare, which only with some fares or as a paid extra, and where it is too big. The sizes come from each airline's official page, quoted on the airline pages with the date we checked them.</p></section>
{modulo_borsa(rel)}
{nota_confronto()}
{AVVISO_BAG}
{AD}
<h2>Common bag sizes</h2>
<div class="griglia">{"".join(f'<a href="{rel}{BAG_BASE}/size/{sl}/">{sl.replace("x", " x ")} cm<small>{len(esiti_misura(m)["gratis"])} free with every fare</small></a>' for sl, m in MISURE_COMUNI)}</div>
<p><a href="{rel}{BAG_BASE}/">All airlines in one table</a> · <a href="{rel}{BAG_UE}">EU free personal item rule</a></p>
{box_bagagli()}
{dati_json('borse-dati', dati_bag_client())}"""
    pagina(BAG_STRUMENTO, f"Does My Bag Fit? Cabin Bag Size Checker ({len(COMPAGNIE)} Airlines, {ANNO})",
           f"Enter your bag's size in cm or inches: see which of {len(COMPAGNIE)} airlines accept it free, only with some fares or paid. Official sizes.",
           corpo, briciole=[("Cabin bags", f"{BAG_BASE}/"), ("Does my bag fit?", BAG_STRUMENTO)], js=BAG_JS)


def indice_bagagli():
    rel = "../"
    gruppi = {}
    for C in COMPAGNIE:
        gruppi.setdefault(C["area"], []).append(C)

    def cella(C, tipo, inc):
        bb = [b for b in C["borse"] if b["tipo"] == tipo and b["incluso"] == inc]
        if not bb:
            if tipo == "sotto" and inc == "tutte" and C.get("personale_senza_misura"):
                return '<span class="small">Personal item, no size published</span>'
            return "–"
        return "<br>".join(escape(misura_testo(b, C)) + (f' <span class="small">{escape(b["peso"])}</span>' if b.get("peso") else "") for b in bb)
    tabelle = []
    for area in ["Europe", "North America", "Middle East and Australia"]:
        if area not in gruppi:
            continue
        righe = "".join(f'<tr data-voce><td data-l="Airline"><a href="{rel}{BAG_BASE}/{C["slug"]}/"><strong>{escape(C["nome"])}</strong></a></td>'
                        f'<td data-l="Free: under the seat">{cella(C, "sotto", "tutte")}</td><td data-l="Free: overhead">{cella(C, "sopra", "tutte")}</td>'
                        f'<td data-l="Some fares or paid">{cella(C, "sopra", "alcune") if cella(C, "sopra", "alcune") != "–" else cella(C, "sotto", "alcune")}</td>'
                        f'<td data-l="Source"><a href="{escape(next(iter(C["fonti"].values()))["url"])}" rel="noopener">official</a>, <span style="white-space:nowrap">{data_lunga(C["controllato_il"])}</span></td></tr>'
                        for C in sorted(gruppi[area], key=lambda x: x["nome"].lower()))
        tabelle.append(f'<h2>{escape(area)}</h2><div class="tab tab-b"><table><thead><tr><th>Airline</th><th>Free with every fare: under the seat</th><th>Free with every fare: overhead</th>'
                       f'<th>Only some fares or paid</th><th>Source</th></tr></thead><tbody id="lista-{area.split()[0].lower()}">{righe}</tbody></table></div>')
    esclusi = "".join(f"<li><strong>{escape(E['nome'])}</strong>: {escape(E['motivo'])}.</li>" for E in BAG["escluse"])
    n_gratis_sopra = sum(1 for C in COMPAGNIE if borsa_gratis(C, "sopra"))
    corpo = f"""<section class="hero">{h1_diviso(f"Cabin bag size by airline ({ANNO}): free under-seat bag and cabin bag")}
<p class="lead">How big can your free bag be, and when do you have to pay for a cabin bag? The official hand luggage sizes of {len(COMPAGNIE)} airlines, quoted word for word from each airline's own page with the date we checked it. {n_gratis_sopra} of them include a cabin bag for the overhead locker in every fare; the others include only a smaller bag that must fit under the seat.</p>
<p class="cifra" style="margin-top:10px"><a href="{rel}{BAG_STRUMENTO}">Does my bag fit? Check your bag against all {len(COMPAGNIE)} airlines</a></p>
</section>
{AVVISO_BAG}
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Type an airline, e.g. Ryanair, easyJet, United" data-filtro-multi aria-label="Search airlines"></div>
{''.join(tabelle[:1])}
{AD}
{''.join(tabelle[1:])}
<p class="small">Sizes in the order each airline writes them; “≈” marks our conversion. Weight limits as the airline states them (“combined” means the under-seat bag and the cabin bag together).</p>
<h2>Bag sizes: which airlines accept them?</h2>
<div class="griglia">{"".join(f'<a href="{rel}{BAG_BASE}/size/{sl}/">{sl.replace("x", " x ")} cm<small>{len(esiti_misura(m)["gratis"])} free with every fare</small></a>' for sl, m in MISURE_COMUNI)}</div>
<h2>New EU rule: a free personal item from 23 October 2027</h2>
<p>Regulation (EU) 2026/2202 says that airlines “shall permit passengers to carry a personal item into the cabin and at no extra cost”, defined as up to 40 x 30 x 15 cm or a bag that fits under the seat in front. <a href="{rel}{BAG_UE}">What the regulation says, quoted, and its exact status</a>.</p>
<h2>Airlines not included (yet)</h2>
<p>We only publish an airline when we can read its official page and the sizes on it. Not included on {data_lunga(BAG['controllato_il'])}:</p>
<ul>{esclusi}</ul>
<p class="small">Last checked: {data_lunga(BAG['controllato_il'])}. Spotted a change? <a href="{rel}contact/?ref=cabin-bags">Tell us</a>.</p>
{box_bagagli()}"""
    pagina(f"{BAG_BASE}/", f"Cabin Bag Size by Airline {ANNO}: Free & Paid ({len(COMPAGNIE)} Airlines)",
           f"Hand luggage size limits of {len(COMPAGNIE)} airlines (Ryanair, easyJet, Wizz Air, BA, United…): the free under-seat bag and the cabin bag, from official pages.",
           corpo, briciole=[("Cabin bags", f"{BAG_BASE}/")], js=APP_JS_FILTRO)


# filtro dell'indice: una casella per più tabelle
APP_JS_FILTRO = r"""
(function(){var inp=document.querySelector('[data-filtro-multi]');if(!inp)return;
  inp.addEventListener('input',function(){var v=inp.value.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
    document.querySelectorAll('tr[data-voce]').forEach(function(a){var t=a.textContent.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');a.hidden=!!v&&t.indexOf(v)<0;});});})();
"""


def cit_ue(k):
    return next(c for c in BAG["ue"]["citazioni"] if c["id"] == k)


def fonte_ue(chiavi):
    U = BAG["ue"]
    return ('<p class="fonte">Official source: ' + " · ".join(f'<a href="{escape(U["fonti"][k]["url"])}" rel="noopener">{escape(U["fonti"][k]["titolo"])}</a>' for k in chiavi) +
            f' · checked on {data_lunga(U["controllato_il"])}</p>')


def pagina_ue():
    rel = "../../"
    U = BAG["ue"]
    def cc(*kk):
        return cit_bag([cit_ue(k) for k in kk])
    iter_ = "".join(f'<tr><td data-l="Date">{data_lunga(x["data"])}</td><td data-l="Step">{escape(x["evento"])}</td></tr>' for x in U["iter"])
    oggi = (40, 30, 15)
    gia = [C for C in COMPAGNIE if any(b["incluso"] == "tutte" and entra_borsa(oggi, "cm", b) for b in C["borse"])]
    non = [C for C in COMPAGNIE if C not in gia]
    lista = lambda L: ", ".join(f'<a href="{rel}{BAG_BASE}/{C["slug"]}/">{escape(C["nome"])}</a>' for C in L) or "none"
    corpo = f"""<section class="hero"><h1>EU free personal item rule: 40 x 30 x 15 cm from 23 October 2027</h1>
<p class="lead">The EU has changed its air passenger rights rules. Here is what the new regulation says about hand luggage, in its own words, and where the law stands today. No predictions: official texts, with the date we checked them; the few lines in our own words are marked as such.</p></section>
<div class="tre">
<section class="card"><span class="sq">{ico("book")}</span><h2>Status</h2><p class="cifra"><strong>Adopted and published</strong></p><p class="small" style="margin:0">Regulation (EU) 2026/2202, Official Journal L of 2 October 2026. Legislative Observatory: “Procedure completed”.</p></section>
<section class="card"><span class="sq">{ico("calendar")}</span><h2>Applies from</h2><p class="cifra"><strong>23 October 2027</strong></p><p class="small" style="margin:0">Article 3 of the regulation (quoted below).</p></section>
<section class="card"><span class="sq">{ico("bag")}</span><h2>Personal item</h2><p class="cifra"><strong>Free, 40 x 30 x 15 cm</strong></p><p class="small" style="margin:0">Or a bag that fits under the seat in front. No EU weight standard: airlines may set reasonable weight limits (European Commission).</p></section>
</div>
<h2>The regulation</h2>
{cc("titolo", "gu")}
{fonte_ue(["reg"])}
<h2>What counts as a personal item and as hand baggage</h2>
{cc("definizione", "bagaglio")}
<h2>Article 11a: personal item and hand baggage</h2>
{cc("art11a", "stiva")}
<p class="small">In short (our words): the personal item must be free; a piece of hand baggage must be allowed in the cabin subject to space, but the regulation does not say it must be free. Read the full text on EUR-Lex.</p>
<h2>When it applies</h2>
{cc("applicazione")}
{fonte_ue(["reg"])}
<h2>What the European Commission says</h2>
{cc("standard", "prezzi", "peso")}
{fonte_ue(["qa"])}
<p class="small">The same Commission page, written before the final votes, also says:</p>
{cc("passi")}
<p class="small">The Legislative Observatory below shows that both institutions have since adopted the text and that it was published in the Official Journal on 2 October 2026; the regulation itself sets the date of application (23 October 2027, quoted above).</p>
{AD}
<h2>Where the law stands: the steps</h2>
<div class="tab tab-b"><table><thead><tr><th>Date</th><th>Step (European Parliament Legislative Observatory)</th></tr></thead><tbody>{iter_}</tbody></table></div>
{cc("stato", "atto")}
{fonte_ue(["oeil"])}
<h2>The airlines on this site today</h2>
<p>Today (sizes checked on {data_lunga(BAG['controllato_il'])}), a 40 x 30 x 15 cm bag already fits the allowance included in every fare at {len(gia)} of the {len(COMPAGNIE)} airlines we list: {lista(gia)}. It does not fit a bag included in every fare at: {lista(non)}.</p>
<p class="small">This is a size comparison, not a legal opinion. The regulation also accepts a personal item defined as a bag that “fits under the seat in front”, and it applies only to the flights covered by Regulation (EC) No 261/2004: we do not judge whether any airline's rules comply. Airlines may change their rules before 23 October 2027.</p>
<p><a href="{rel}{BAG_BASE}/">Cabin bag size by airline</a> · <a href="{rel}{BAG_STRUMENTO}">Does my bag fit?</a></p>"""
    pagina(BAG_UE, f"EU Free Personal Item Rule: 40x30x15 cm from 23 October 2027",
           "Regulation (EU) 2026/2202: a free personal item of 40 x 30 x 15 cm from 23 October 2027. The official text, its status and what the Commission says.",
           corpo, briciole=[("Cabin bags", f"{BAG_BASE}/"), ("EU personal item rule", BAG_UE)])


# ---------------------------------------------------------------- "Is [service] available in [country]?" (dal 28/10/2026)
# Dati: dati/servizi.json (liste ufficiali dei Paesi, lette da raccolta/servizi.py), dati/servizi_domanda.json (ricerche vere
# dell'autocompletamento di Google: una pagina servizio × Paese esiste SOLO per queste coppie), dati/paesi_iso.json (codici e nomi).
# Regole: si scrive solo cosa dice la fonte; "non nella lista" non vuol dire "vietato" e le pagine lo dicono; nessun consiglio per aggirare
# blocchi, termini o leggi; nessun riquadro VPN (affiliazioni non attive); nessun assistente di intelligenza artificiale tra i servizi.
SRV_BASE = "available-in"
_f_srv = DATI / "servizi.json"
SRV = json.loads(_f_srv.read_text(encoding="utf-8")) if _f_srv.exists() else None
_f_dom = DATI / "servizi_domanda.json"
SRV_DOMANDA = json.loads(_f_dom.read_text(encoding="utf-8")) if _f_dom.exists() else {"servizi": {}}
PAESI_ISO = {p["iso2"]: p for p in json.loads((DATI / "paesi_iso.json").read_text(encoding="utf-8"))["paesi"]} if (DATI / "paesi_iso.json").exists() else {}
SERVIZI_SRV = SRV["servizi"] if SRV else []
SRV_PER = {S["slug"]: S for S in SERVIZI_SRV}
LASTMOD = {}  # percorso -> data vera dell'ultimo cambio del contenuto (sitemap); le pagine senza voce prendono la data di oggi
# Nome breve della fonte nelle frasi e "lista" come la descrive la fonte stessa (frasi *_lista in dati/servizi.json)
SRV_TESTI = {
    "starlink": {"fonte": "Starlink map data", "lista": "Starlink's official availability map"},
    "apple-pay": {"fonte": "Apple Support", "lista": "Apple's list of countries and regions where you can add cards from participating banks and card issuers to Apple Pay"},
    "apple-music": {"fonte": "Apple Support", "lista": "Apple's list of where Apple Music is available"},
    "apple-tv": {"fonte": "Apple Support", "lista": "Apple's list of where the Apple TV subscription is available"},
    "youtube-premium": {"fonte": "YouTube Help", "lista": "YouTube's list of countries and territories where YouTube Premium memberships are available"},
    "spotify": {"fonte": "Spotify Support", "lista": "Spotify's list of countries and regions where you can sign up for Spotify"},
}
# Starlink: parole della legenda della mappa ufficiale (codice di starlink.com/map letto il 28/10/2026; vedi raccolta/servizi.py)
STARLINK_LEGENDA = {"si": "Area is available for service now.", "in_arrivo": "Pending service coverage or regulatory approval."}
CON_THE_ISO = {"US", "GB", "AE", "PH", "NL", "BS", "MV", "DO", "CF", "KM", "SC", "GM", "CD", "CG", "IM", "IO", "TF", "UM"}


def nome_srv(c):
    return PAESI_ISO[c]["nome"]


def frase_srv(c, maiuscola=False):
    """Nome del Paese dentro una frase: 'the Philippines', 'the United States'; con maiuscola a inizio frase."""
    n = nome_srv(c)
    if c in CON_THE_ISO or n.endswith("Islands"):
        n = ("The " if maiuscola else "the ") + n
    return n


def alias_srv(c):
    """Nomi alternativi (UAE, Dubai, Türkiye, Ivory Coast...) nascosti nella riga, perché la ricerca delle tabelle li trovi."""
    al = PAESI_ISO[c].get("alias") or []
    return f'<span hidden> {escape(" · ".join(al))}</span>' if al else ""


def slug_srv(c):
    s = unicodedata.normalize("NFKD", nome_srv(c)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def stato_srv(S, c):
    v = S["paesi"].get(c)
    return (v["stato"], v) if v else ("assente", None)


def breve_srv(S, c):
    """Risposta breve per titolo, tabella e riquadro."""
    st, v = stato_srv(S, c)
    if st == "si":
        return "Yes"
    if st == "in_arrivo":
        return "Coming soon"
    if st == "per_regione":
        return "By region"
    if st == "no":
        if S["slug"] == "starlink":
            return "No service shown"
        if S["slug"] == "youtube-premium":
            return (v.get("nota") or "Not available").capitalize()
        return "Not listed"
    return "Not on the list"


def classe_srv(st):
    return {"si": "si", "in_arrivo": "manuale", "per_regione": "manuale", "no": "no", "assente": "no"}[st]


def badge_srv(S, c, con_nota=True):
    st, v = stato_srv(S, c)
    k = {"si": "gratis", "in_arrivo": "altre", "per_regione": "altre", "no": "no", "assente": "no"}[st]
    nota = f' <span class="small">{escape(v["nota"])}</span>' if (con_nota and v and v.get("nota") and st == "si") else ""
    return f'<span class="badge b-{k}">{escape(breve_srv(S, c))}</span>{nota}'


def data_controllo_srv(S):
    return data_lunga(S["letto_il"])


def risposta_srv(S, c):
    """Prima frase della pagina: sì/no, cosa dice la fonte, fonte e data. Solo modelli fissi (verifica.py li ricalcola)."""
    st, v = stato_srv(S, c)
    T, d = SRV_TESTI[S["slug"]], data_controllo_srv(S)
    P, Pm = frase_srv(c), frase_srv(c, True)
    if S["slug"] == "starlink":
        if st == "si":
            return f"Yes. Starlink's official availability map shows {P} as “Available” ({T['fonte']}, checked on {d})."
        if st == "in_arrivo":
            nota = f", with the note “{v['nota']}”" if v.get("nota") else ""
            return f"Not yet. Starlink's official availability map shows {P} as “Coming soon”{nota} ({T['fonte']}, checked on {d})."
        if st == "per_regione":
            return (f"It depends on the region. Starlink's official availability map gives no single status for {P}: it shows each region "
                    f"separately ({T['fonte']}, checked on {d}).")
        if st == "no":
            return (f"No. Starlink's official availability map shows no Starlink service for {P}: it is not marked “Available” or “Coming soon” "
                    f"({T['fonte']}, checked on {d}).")
        return f"Not known. {Pm} is not in Starlink's official availability map data ({T['fonte']}, checked on {d})."
    if st == "si":
        nota = f" The list adds: “{v['nota']}”." if v.get("nota") else ""
        return f"Yes. {Pm} is on {T['lista']} ({T['fonte']}, checked on {d}).{nota}"
    if st == "no":
        if S["slug"] == "youtube-premium":
            return f"No, not at the moment. YouTube's list of Premium membership locations shows {P} as “{v['nota']}” ({T['fonte']}, checked on {d})."
        if S["slug"] == "apple-music":
            return f"No. Apple's page lists {P}, but not Apple Music among the services available there ({T['fonte']}, checked on {d})."
        if S["slug"] == "apple-tv":
            app = (f" For the Apple TV app it says: “{v['nota']}”." if v.get("nota") else "") if v.get("app_tv") else " It does not list the Apple TV app there either."
            return f"No. Apple's page lists {P}, but not the Apple TV subscription ({T['fonte']}, checked on {d}).{app}"
    return f"No, not according to the official list. {Pm} is not on {T['lista']} ({T['fonte']}, checked on {d})."


def significato_srv(S, c):
    """Seconda frase: cosa vuol dire (e cosa NON vuol dire) la risposta. Frasi fisse."""
    st, _ = stato_srv(S, c)
    pay = (" This list is about cards from local banks. It does not say whether a card from your own bank works abroad: that depends on your bank."
           if S["slug"] == "apple-pay" else "")
    if st == "assente" and S["slug"] != "starlink":
        return (f"Not being on the list is not the same as being banned: the list only shows where {S['fornitore'].split(' (')[0]} offers it, "
                "and it does not give reasons." + pay)
    if st == "no" and S["slug"] != "starlink":
        return "The official page does not give reasons."
    if S["slug"] == "starlink":
        n = S.get("extra", {}).get("regioni_separate", 0)
        return ("The map shows one status per country and some regions separately"
                + (f" ({n} regions in the data file)" if n else "") + ", so check your exact address on the official map.")
    if S["slug"] == "apple-pay":
        return pay.strip()
    return "Lists change: check the official page before you pay for a subscription."


def titoli_srv(S, c):
    n, P, b = S["nome"], frase_srv(c), breve_srv(S, c)
    b_tit = {"Not on the list": "Not on the Official List", "Coming soon": "Coming Soon", "No service shown": "No Service Shown",
             "Not listed": "Not Listed", "By region": "Depends on the Region"}.get(b, b.title() if b != "Yes" else b)
    return [f"Is {n} Available in {P}? {b_tit} ({ANNO})", f"Is {n} Available in {P}? ({ANNO})", f"{n} in {P}: {b_tit} ({ANNO})",
            f"{n} in {P} ({ANNO})"]


def descrizioni_srv(S, c):
    r = risposta_srv(S, c)
    corto = f"Is {S['nome']} available in {frase_srv(c)}? {breve_srv(S, c)}, according to the official list checked on {data_controllo_srv(S)}."
    return [r, corto, f"Is {S['nome']} available in {frase_srv(c)}? {breve_srv(S, c)}, from the official list."]


def pagine_srv(S):
    """Paesi con una pagina servizio × Paese: solo le coppie trovate nell'autocompletamento (dati/servizi_domanda.json)."""
    return sorted((c for c in SRV_DOMANDA["servizi"].get(S["slug"], {}) if c in PAESI_ISO), key=lambda c: slug_srv(c))


def url_srv(S, c=None):
    return f"{SRV_BASE}/{S['slug']}/" + (f"{slug_srv(c)}/" if c else "")


def link_srv(S, c, rel):
    """Link alla pagina servizio × Paese se esiste, altrimenti alla riga della tabella del servizio."""
    if c in pagine_srv(S):
        return f"{rel}{url_srv(S, c)}"
    return f"{rel}{url_srv(S)}#{c.lower()}"


def fonte_srv(S):
    d = f"checked on {data_controllo_srv(S)}"
    pub = f", page published on {data_lunga(S['data_fonte'])}" if S.get("data_fonte") else ""
    cambio = f"; list unchanged since our first check on {data_lunga(S['cambiato_il'])}" if S["cambiato_il"] != S["letto_il"] else ""
    file_ = f', data file <a href="{escape(S["url_fonte"])}" rel="noopener">{escape(S["url_fonte"])}</a>' if S["url_fonte"] != S["pagina"] else ""
    return (f'<p class="fonte">Source: <a href="{escape(S["pagina"])}" rel="noopener">{escape(S["titolo_fonte"])}</a>{file_}, {d}{pub}{cambio}. '
            f'We copy the list as published and match each name to an ISO country code; we add nothing.</p>')


def cit_srv(chiavi):
    ff = [SRV["frasi"][k]["frase"] for k in chiavi if k in SRV["frasi"]]
    return cit_html(ff) if ff else ""


# frasi ufficiali da citare per servizio: (sulla lista, per chi viaggia o si trasferisce)
CIT_SRV = {
    "apple-pay": (["apple_pay_lista"], ["apple_pay_accettato", "apple_pay_cash"]),
    "apple-music": (["apple_media_lista"], ["apple_media_varia"]),
    "apple-tv": (["apple_media_lista"], ["apple_media_varia"]),
    "youtube-premium": (["youtube_lista", "youtube_nota"], ["youtube_paese", "youtube_viaggio_no", "youtube_offline", "youtube_30"]),
    "spotify": (["spotify_lista"], ["spotify_paese", "spotify_trasloco"]),
    "starlink": ([], []),
}


def ingresso_srv(c, rel):
    """Link alle pagine Paese già esistenti di Before You Fly (passaporto britannico, canadese, australiano, documenti per italiani)."""
    link = []
    v_ca = next((v for v in VOCI.get("ca", []) if v["p"].get("iso") == c), None)
    uk = list(v_ca["uk"]) if v_ca else []
    if not uk:
        uk = [s for s in [UK_PER_NOME.get(_chiave_nome(nome_srv(c)))] if s in UK_CON_PAGINA]
    for s in uk:
        link.append(f'<a href="{rel}passport-validity/{s}/">British passport: {escape(UK_NOMI[s])} entry requirements</a>')
    if v_ca:
        link.append(f'<a href="{rel}{v_ca["url_pag"]}">Canadian passport: {escape(v_ca["nome"])}</a>')
    for s in uk:
        for w in PER_UK.get("au", {}).get(s, []):
            link.append(f'<a href="{rel}{w["url_pag"]}">Australian passport: {escape(w["nome"])}</a>')
    for v in VOCI_IT:
        if v["p"].get("iso2") == c:
            link.append(f'<a href="{rel}{v["url_pag"]}" hreflang="it">Italian citizens: <span lang="it">{escape(v["nome"])}</span></a>')
    return link


def faq_srv(S, c):
    P = frase_srv(c)
    r = risposta_srv(S, c)
    out = [(f"Is {S['nome']} available in {P}?", r)]
    if S["slug"] == "youtube-premium":
        out.append((f"Is YouTube Music Premium available in {P}?",
                    f"YouTube uses one list for both (“{SRV['frasi']['youtube_titolo']['frase']}”). {r}"))
    if S["slug"] == "apple-tv":
        out.append((f"Is Apple TV+ available in {P}?", f"Apple now calls its streaming service the Apple TV subscription. {r}"))
    out.append((f"Where does this answer about {S['nome']} in {P} come from?",
                f"From {S['titolo_fonte']} ({S['pagina']}), read on {data_controllo_srv(S)}. We copy the list as published and only match "
                "country names to ISO country codes."))
    return out


def html_faq_srv(S, c):
    faq = faq_srv(S, c)
    h = "".join(f"<h3>{escape(q)}</h3><p>{escape(a)}</p>" for q, a in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    return f'<section class="faq"><h2>Questions</h2>{h}</section>', [ld]


def pagina_srv_paese(S, c):
    rel = "../../../"
    st, v = stato_srv(S, c)
    P, n = frase_srv(c), S["nome"]
    icona = {"si": "check", "in_arrivo": "alert", "per_regione": "alert", "no": "x", "assente": "x"}[st]
    nomi_fonte = [x for x in (v or {}).get("nomi_fonte", []) if _chiave_nome(x) != _chiave_nome(nome_srv(c))]
    sotto = (f'<p>{escape(S["fornitore"].split(" (")[0])} writes the name as “{escape(" / ".join(nomi_fonte))}”.</p>' if nomi_fonte else "")
    c_lista, c_viaggio = CIT_SRV[S["slug"]]
    if S["slug"] == "starlink":
        cosa_dice = (f'<p>On the official map, “Available” means, in Starlink\'s words: “{STARLINK_LEGENDA["si"]}” “Coming soon” means: '
                     f'“{STARLINK_LEGENDA["in_arrivo"]}” Places with neither status are shown without any service. A few countries have no '
                     'status of their own: the map colours each of their regions separately (“By region” in our tables).</p>')
    else:
        cosa_dice = f'<p>The official page introduces its list with these words:</p>{cit_srv(c_lista)}'
    se_no = st != "si"
    tit_viaggio = (f"If {n} is not available in {P}" if se_no else f"Travelling or moving to {P} with {n}")
    if S["slug"] == "starlink":
        viaggio = ("<p>Check your exact address on Starlink's official map before you buy equipment or travel with it: the status can change and can "
                   "differ within a country.</p>")
    elif S["slug"] == "apple-pay":
        viaggio = f'<p>What Apple says about paying abroad and about Apple Cash:</p>{cit_srv(c_viaggio)}'
    else:
        viaggio = f'<p>What {escape(S["fornitore"].split(" (")[0])} says about using it in another country:</p>{cit_srv(c_viaggio)}'
    viaggio += ("<p>Lists change, often without notice. Check the official page before you rely on the service or pay for anything, and follow the "
                "provider's terms and the law of the country you are in.</p>")
    altri = "".join(f'<tr data-voce><td data-l="Service"><a href="{link_srv(S2, c, rel)}">{escape(S2["nome"])}</a></td>'
                    f'<td data-l="In {escape(nome_srv(c))}">{badge_srv(S2, c)}</td><td data-l="Checked">{data_controllo_srv(S2)}</td></tr>'
                    for S2 in SERVIZI_SRV)
    ingresso = ingresso_srv(c, rel)
    faq_h, faq_ld = html_faq_srv(S, c)
    corpo = f"""<section class="hero"><h1>Is {escape(n)} available in {escape(P)}?</h1></section>
<section class="card summary" aria-label="Answer">
<div class="s-top"><span class="sq">{ico("apps")}</span><span>{escape(n)} · {escape(nome_srv(c))}</span><span>{ANNO}</span></div>
<div class="s-body">
<div class="esito e-srv {classe_srv(st)}">{ico(icona)}<strong>{escape(breve_srv(S, c))}</strong></div>
<p class="lead" id="answer">{escape(risposta_srv(S, c))}</p>
<p class="lead">{escape(significato_srv(S, c))}</p>
{fonte_srv(S)}
</div></section>
<h2>What the official source says</h2>
{cosa_dice}
{sotto}
<p><a href="{rel}{url_srv(S)}">All countries for {escape(n)}</a> (table with every country and region on the official list).</p>
{AD}
<h2>{escape(tit_viaggio)}</h2>
{viaggio}
<h2>Other services in {escape(P)}</h2>
<div class="tab tab-b"><table><caption class="sr">Official availability of {len(SERVIZI_SRV)} services in {escape(P)}</caption><thead><tr><th>Service</th><th>In {escape(nome_srv(c))}</th><th>Checked</th></tr></thead><tbody>{altri}</tbody></table></div>
{f'<h2>Before you travel to {escape(P)}</h2><ul>' + "".join(f"<li>{x}</li>" for x in ingresso) + "</ul>" if ingresso else ""}
{link_guida(rel, c)}
{faq_h}
<p class="small">Spotted a change? <a href="{rel}contact/?ref=available-in">Tell us</a>. <a href="{rel}{SRV_BASE}/">All services by country</a>.</p>"""
    pagina(url_srv(S, c), scegli(titoli_srv(S, c), LIMITE_TITOLO), scegli(descrizioni_srv(S, c), LIMITE_DESCRIZIONE), corpo,
           briciole=[("Available in?", f"{SRV_BASE}/"), (n, url_srv(S)), (nome_srv(c), url_srv(S, c))], ld_extra=faq_ld, js=APP_JS_FILTRO)
    LASTMOD[url_srv(S, c)] = S["letto_il"]


def ordine_srv(c):
    return unicodedata.normalize("NFKD", nome_srv(c)).encode("ascii", "ignore").decode().lower()


def titoli_srv_servizio(S):
    return [f"Where Is {S['nome']} Available? All Countries ({ANNO} Official List)", f"Where Is {S['nome']} Available? Countries List ({ANNO})",
            f"{S['nome']} Countries ({ANNO})"]


def pagina_srv_servizio(S):
    rel = "../../"
    n = S["nome"]
    con = [c for c in PAESI_ISO if stato_srv(S, c)[0] == "si"]
    arr = [c for c in PAESI_ISO if stato_srv(S, c)[0] == "in_arrivo"]
    T, d = SRV_TESTI[S["slug"]], data_controllo_srv(S)
    if S["slug"] == "starlink":
        reg = [c for c in PAESI_ISO if stato_srv(S, c)[0] == "per_regione"]
        prima = (f"Starlink's official availability map shows {len(con)} countries and territories as “Available” and {len(arr)} as “Coming soon”"
                 + (f"; it shows {len(reg)} ({', '.join(nome_srv(c) for c in sorted(reg, key=ordine_srv))}) region by region" if reg else "")
                 + f" ({T['fonte']}, checked on {d}).")
    else:
        prima = f"{len(con)} countries and territories are on {T['lista']} ({T['fonte']}, checked on {d})."
    pagine = pagine_srv(S)

    def nota(c):
        st, v = stato_srv(S, c)
        if not v:
            return "–"
        x = []
        if v.get("nomi_fonte") and any(_chiave_nome(y) != _chiave_nome(nome_srv(c)) for y in v["nomi_fonte"]):
            x.append("listed as “" + " / ".join(v["nomi_fonte"]) + "”")
        if v.get("nota"):
            x.append(("Apple TV app: " if S["slug"] == "apple-tv" else "") + "“" + v["nota"] + "”")
        if S["slug"] == "apple-tv" and st == "no" and not v.get("app_tv"):
            x.append("no Apple TV app listed")
        return escape("; ".join(x)) or "–"
    righe = "".join(f'<tr data-voce id="{c.lower()}"><td data-l="Country or region">' +
                    (f'<a href="{rel}{url_srv(S, c)}">{escape(nome_srv(c))}</a>' if c in pagine else escape(nome_srv(c))) + alias_srv(c) +
                    f'</td><td data-l="{escape(n)}">{badge_srv(S, c)}</td><td data-l="Official wording">{nota(c)}</td></tr>'
                    for c in sorted(PAESI_ISO, key=ordine_srv))
    c_lista, _ = CIT_SRV[S["slug"]]
    if S["slug"] == "starlink":
        spiega = (f'<p>On the official map, “Available” means, in Starlink\'s words: “{STARLINK_LEGENDA["si"]}” “Coming soon” means: '
                  f'“{STARLINK_LEGENDA["in_arrivo"]}” We show the note the data file gives for “Coming soon” places (for example “Starting in 2026” or '
                  '“Pending regulatory approval”). “No service shown” means the map marks the place with neither status; “By region” means the map gives the country '
                  'no status of its own and colours each region separately; “Not on the list” means the data file has no entry for it. '
                  f'{escape(significato_srv(S, "US"))}</p>')
    else:
        spiega = (f'<p>The official page introduces its list with these words:</p>{cit_srv(c_lista)}'
                  f'<p>“Not on the list” means the official page does not name that country or region. It does not mean {escape(n)} is banned there, and the page gives no reasons.</p>')
    griglia = "".join(f'<a href="{rel}{url_srv(S, c)}">{escape(nome_srv(c))}<small>{escape(breve_srv(S, c))}</small></a>' for c in pagine)
    corpo = f"""<section class="hero">{h1_diviso(f"Where is {n} available? Official list of countries ({ANNO})")}
<p class="lead" id="answer">{escape(prima)}</p></section>
<ul class="stat"><li><strong>{len(con)}</strong>{"“Available”" if S["slug"] == "starlink" else "on the list"}</li>{f'<li><strong>{len(arr)}</strong>“Coming soon”</li>' if S["slug"] == "starlink" else ""}<li><strong>{d}</strong>last checked</li></ul>
{fonte_srv(S)}
<h2>Is {escape(n)} available in my country?</h2>
<div class="griglia g-srv">{griglia}</div>
{AD}
<h2>All countries and regions</h2>
{spiega}
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Type a country, e.g. India" data-filtro-multi aria-label="Search countries"></div>
<div class="tab tab-b tab-srv"><table><caption class="sr">{escape(n)}: availability by country, from the official list checked on {d}</caption><thead><tr><th>Country or region</th><th>{escape(n)}</th><th>Official wording</th></tr></thead><tbody>{righe}</tbody></table></div>
<p class="small">{len(PAESI_ISO)} countries and territories (ISO 3166-1 codes, plus Kosovo). Spotted a change? <a href="{rel}contact/?ref=available-in">Tell us</a>.</p>
<p><a href="{rel}{SRV_BASE}/">All services by country</a></p>"""
    desc = [f"Where is {n} available? {prima}", f"Where is {n} available? {len(con)} countries on the official list, checked on {d}. Every country, yes or no."]
    pagina(url_srv(S), scegli(titoli_srv_servizio(S), LIMITE_TITOLO), scegli(desc, LIMITE_DESCRIZIONE), corpo,
           briciole=[("Available in?", f"{SRV_BASE}/"), (n, url_srv(S))], js=APP_JS_FILTRO)
    LASTMOD[url_srv(S)] = S["letto_il"]


def indice_srv():
    rel = "../"
    d = data_lunga(max(S["letto_il"] for S in SERVIZI_SRV))
    nomi = ", ".join(S["nome"] for S in SERVIZI_SRV[:-1]) + " and " + SERVIZI_SRV[-1]["nome"]
    tab_s = "".join(f'<tr data-voce><td data-l="Service"><a href="{rel}{url_srv(S)}"><strong>{escape(S["nome"])}</strong></a></td>'
                    f'<td data-l="Countries on the list">{sum(1 for c in PAESI_ISO if stato_srv(S, c)[0] == "si")}</td>'
                    f'<td data-l="Official source"><a href="{escape(S["pagina"])}" rel="noopener">{escape(S["titolo_fonte"])}</a></td>'
                    f'<td data-l="Checked">{data_controllo_srv(S)}</td></tr>' for S in SERVIZI_SRV)
    righe = "".join(f'<tr data-voce><td data-l="Country or region"><strong>{escape(nome_srv(c))}</strong>{alias_srv(c)}</td>' +
                    "".join(f'<td data-l="{escape(S["nome"])}"><a class="a-badge" href="{link_srv(S, c, rel)}">{badge_srv(S, c, False)}</a></td>' for S in SERVIZI_SRV) + "</tr>"
                    for c in sorted(PAESI_ISO, key=ordine_srv))
    popolari = []
    for c in ("PK", "IN", "NG", "PH", "CN", "AE", "MX", "ZA", "CA", "GB"):
        for S in SERVIZI_SRV:
            if c in pagine_srv(S) and len(popolari) < 18:
                popolari.append(f'<a href="{rel}{url_srv(S, c)}">{escape(S["nome"])} in {escape(frase_srv(c))}<small>{escape(breve_srv(S, c))}</small></a>')
    corpo = f"""<section class="hero">{h1_diviso(f"Is it available in my country? Apps and services by country ({ANNO})")}
<p class="lead" id="answer">The official country lists of {nomi}, as each provider publishes them, checked on {d}. Every answer links to the provider's own page.</p></section>
<p class="avviso"><strong>“Not on the list” is not the same as “banned”.</strong> We copy each provider's list as published and only say what it says. Lists change without notice: check the official page before you pay for a subscription or equipment.</p>
<h2>The {len(SERVIZI_SRV)} services and their official lists</h2>
<div class="tab tab-b"><table><caption class="sr">Services, number of countries on each official list, source and date checked</caption><thead><tr><th>Service</th><th>Countries on the list</th><th>Official source</th><th>Checked</th></tr></thead><tbody>{tab_s}</tbody></table></div>
<h2>Most searched</h2>
<div class="griglia">{"".join(popolari)}</div>
{AD}
<h2>Every country, every service</h2>
<p>“Yes” means the country is on the provider's list; for Starlink, “Coming soon”, “No service shown” and “By region” describe the provider's map. Click an answer for the details and the source.</p>
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Type a country, e.g. Nigeria" data-filtro-multi aria-label="Search countries"></div>
<div class="tab tab-b tab-srv"><table><caption class="sr">Official availability of {len(SERVIZI_SRV)} services in {len(PAESI_ISO)} countries and territories, checked on {d}</caption><thead><tr><th>Country or region</th>{"".join(f"<th>{escape(S['nome'])}</th>" for S in SERVIZI_SRV)}</tr></thead><tbody>{righe}</tbody></table></div>
<h2>How we check</h2>
<p>We include a service only if the provider itself publishes a list of countries that we can read without a browser, and we read it again before every update. Services whose list exists only inside an app or a script, or that block automated reading, are left out. Country names are matched to ISO 3166-1 codes; regions inside a country (for example the Canary Islands) are not shown separately. More on the <a href="{rel}about/#available-in">About page</a>. Spotted a change? <a href="{rel}contact/?ref=available-in">Tell us</a>.</p>"""
    pagina(f"{SRV_BASE}/", f"Is It Available in My Country? Apps by Country ({ANNO})",
           scegli([f"Is {nomi} available in your country? Official country lists, checked on {d}.",
                   f"Official country lists of {len(SERVIZI_SRV)} services (Starlink, Apple Pay, Spotify…), checked on {d}."], LIMITE_DESCRIZIONE),
           corpo, briciole=[("Available in?", f"{SRV_BASE}/")], js=APP_JS_FILTRO)
    LASTMOD[f"{SRV_BASE}/"] = max(S["letto_il"] for S in SERVIZI_SRV)


def home_srv():
    """Paragrafo e griglia nella home."""
    if not SERVIZI_SRV:
        return ""
    voci = []
    for S, c in (("starlink", "PK"), ("apple-pay", "IN"), ("youtube-premium", "PK"), ("spotify", "CN"), ("apple-tv", "NG"), ("starlink", "PH"),
                 ("apple-music", "CN"), ("apple-pay", "PH")):
        if S in SRV_PER and c in pagine_srv(SRV_PER[S]):
            voci.append(f'<a href="{url_srv(SRV_PER[S], c)}">{escape(SRV_PER[S]["nome"])} in {escape(frase_srv(c))}<small>{escape(breve_srv(SRV_PER[S], c))}</small></a>')
    return (f'<h2>Is it available where you are going?</h2><p>Starlink, Apple Pay, Apple Music, Apple TV, YouTube Premium and Spotify publish their own lists '
            f'of countries. We copy them as published, with the source and the date: <a href="{SRV_BASE}/">every country and every service in one table</a>.</p>'
            f'<div class="griglia">{"".join(voci)}</div>')


def about_srv(rel):
    if not SERVIZI_SRV:
        return ""
    righe = "".join(f'<li><strong>{escape(S["nome"])}</strong>: <a href="{escape(S["pagina"])}" rel="noopener">{escape(S["titolo_fonte"])}</a>'
                    + (f' (data file {escape(S["url_fonte"])})' if S["url_fonte"] != S["pagina"] else "") + f', checked on {data_controllo_srv(S)}.</li>'
                    for S in SERVIZI_SRV)
    return f"""<h2 id="available-in">Apps and services by country</h2>
<p>Sources: the providers' own lists of countries, read with a normal web request (no browser) and copied as published:</p>
<ul>{righe}</ul>
<p>Rules: a country is “Yes” only if the provider's list names it; “Not on the list” means the list does not name it, which is not the same as a ban. For Starlink we show the statuses of the official availability map (“Available”, “Coming soon” with the note the map gives, no service shown, or “By region” when the map colours a country region by region), as the map's own legend explains them. Names are matched to ISO 3166-1 country codes; regions inside a country are not shown separately. We give no advice on getting around restrictions. A page for a single service and country exists only where people search for it. The lists are facts published by each provider; the trademarks belong to their owners, and Before You Fly is not affiliated with any of them.</p>"""


# ---------------------------------------------------------------- "Can I drive in [country] with my UK / Canadian / Australian licence?" (dal 28/10/2026)
# Dati: dati/patenti.json (frasi ufficiali sul permesso internazionale, lette da raccolta/patenti.py: tabella GOV.UK + consigli FCDO,
# travel.gc.ca, Smartraveller; esito da schemi fissi o da fatti scritti a mano in dati/patenti_manuali.json) e dati/patenti_domanda.json
# (ricerche vere dell'autocompletamento: una pagina Paese × patente esiste SOLO per le coppie in "pagine" e solo se la fonte dice qualcosa).
# Regole: la prima frase dice sì / no / dipende con la frase dell'ente tra virgolette, la fonte e la data; se la fonte non dice nulla:
# "Not stated by <ente>", mai una deduzione; nessun consiglio legale personale; nessun link affiliato (NOLEGGIO_AUTO resta vuoto).
PAT_BASE = "driving-abroad"
_f_pat = DATI / "patenti.json"
PAT = json.loads(_f_pat.read_text(encoding="utf-8")) if _f_pat.exists() else None
_f_pat_dom = DATI / "patenti_domanda.json"
PAT_DOM = json.loads(_f_pat_dom.read_text(encoding="utf-8")) if _f_pat_dom.exists() else {"pagine": {}, "patenti": {}}
PAT_PER = {p["iso2"]: p for p in PAT["paesi"]} if PAT else {}
PAT_G = PAT["frasi_generali"] if PAT else {}
# Segnaposto spento per un futuro riquadro "Hire a car" (noleggio auto, link affiliato): finché è vuoto non compare nulla.
# verifica.py blocca i link affiliati nelle pagine di questa sezione: per accenderlo serve la decisione di Massimiliano e un controllo nuovo.
NOLEGGIO_AUTO = ""
PATENTI = {
    "uk": {"slug": "uk-licence", "agg": "UK", "lic": "UK licence", "ente": "GOV.UK", "Ente": "GOV.UK", "paese": "the UK",
           "titolo": "UK Licence", "chi": "a UK photocard driving licence", "Lic": "UK licence", "art": "a",
           "fonte": "GOV.UK"},
    "ca": {"slug": "canadian-licence", "agg": "Canadian", "lic": "Canadian licence", "ente": "the Government of Canada", "Ente": "The Government of Canada",
           "paese": "Canada", "titolo": "Canadian Licence", "chi": "a Canadian driver's licence", "Lic": "Canadian licence",
           "art": "a", "fonte": "Government of Canada"},
    "au": {"slug": "australian-licence", "agg": "Australian", "lic": "Australian licence", "ente": "Smartraveller", "Ente": "Smartraveller",
           "paese": "Australia", "titolo": "Australian Licence", "chi": "an Australian driver's licence",
           "Lic": "Australian licence", "art": "an", "fonte": "Smartraveller"},
}
# esito -> (etichetta breve, classe del badge, inizio della prima frase, parola nel titolo)
ESITI_PAT = {
    "si": ("IDP needed", "b-no", "Yes.", "Yes"),
    "no": ("No IDP needed", "b-gratis", "No.", "No"),
    "dipende": ("It depends", "b-altre", "It depends", "It Depends"),  # la prima frase continua con "on how long you stay…" (dipende_da_pat)
    "consigliato": ("Recommended", "b-altre", "Recommended.", "Recommended"),
    "locale": ("Local permit needed", "b-no", "An IDP alone is not enough: you need a local licence or permit.", "Local Permit Needed"),
    "non_detto": ("Not stated", "b-muto", "", "Not Stated"),
    "da_leggere": ("Read the official text", "b-muto", "", ""),
}
ICONA_PAT = {"si": "alert", "no": "check", "dipende": "alert", "consigliato": "alert", "locale": "x", "non_detto": "alert", "da_leggere": "alert"}
CLASSE_PAT = {"si": "manuale", "no": "si", "dipende": "manuale", "consigliato": "manuale", "locale": "no", "non_detto": "manuale", "da_leggere": "manuale"}


NOMI_TITOLO_PAT = {"US": "the USA", "GB": "the UK", "AE": "the UAE", "KR": "South Korea", "CZ": "Czechia"}
LIMITE_TITOLO_PAT = 70  # titoli di questa sezione: fino a 70 caratteri con l'anno (richiesta del 28/10/2026)


def nome_titolo_pat(c, maiuscola=False):
    n = NOMI_TITOLO_PAT.get(c) or frase_srv(c)
    return n[0].upper() + n[1:] if maiuscola else n


def voce_pat(k, c):
    p = PAT_PER.get(c)
    return p[k] if p else None


def pagine_pat(k):
    """Paesi con la pagina Paese × patente: coppie cercate davvero (patenti_domanda.json, "pagine") e con qualcosa di detto dalla fonte."""
    out = []
    for c in PAT_DOM.get("pagine", {}).get(k, []):
        v = voce_pat(k, c)
        if v and c in PAESI_ISO and v["esito"] not in ("non_detto", "da_leggere"):
            out.append(c)
    return sorted(out, key=ordine_srv)


PAGINE_PAT = {k: (pagine_pat(k) if PAT else []) for k in PATENTI}


def url_pat(k, c=None):
    return f"{PAT_BASE}/{PATENTI[k]['slug']}/" + (f"{slug_srv(c)}/" if c else "")


def link_pat(k, c, rel):
    return f"{rel}{url_pat(k, c)}" if c in PAGINE_PAT[k] else f"{rel}{url_pat(k)}#{c.lower()}"


def badge_pat(k, c):
    e = voce_pat(k, c)["esito"]
    return f'<span class="badge {ESITI_PAT[e][1]}">{escape(ESITI_PAT[e][0])}</span>'


def nota_uk(v):
    return v.get("tabella", {}).get("nota", "") if v.get("tabella") else ""


def parti_frasi(k, v):
    """Frasi chiave divise per provenienza (Regno Unito: tabella GOV.UK o consigli FCDO)."""
    if k != "uk":
        return [], v["frasi"]
    nota = piano_t(nota_uk(v))
    tab = [x for x in v["frasi"] if nota and piano_t(x) in nota]
    return tab, [x for x in v["frasi"] if x not in tab]


def piano_t(s):
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')).strip()


def cita_pat(ff):
    """Frasi ufficiali tra virgolette; una frase che finisce con ':' si unisce alla voce che segue con '…' (voce di elenco)."""
    out, i = [], 0
    while i < len(ff):
        x = ff[i].strip()
        while x.endswith(":") and i + 1 < len(ff):
            i += 1
            x = x + " … " + ff[i].strip()
        out.append(f"“{x}”")
        i += 1
    return " ".join(out)


def data_pat(k, v):
    """Data della lettura della fonte usata per la risposta."""
    if k == "uk" and not v.get("letto_il"):
        return PAT["fonti"]["uk"]["letto_il"]
    return v["letto_il"]


def fonte_breve_pat(k, v, c):
    P = frase_srv(c)
    if k == "uk":
        tab, fc = parti_frasi(k, v)
        if tab and fc:
            return f"GOV.UK international driving permit table and FCDO travel advice for {P}"
        if tab or (not fc and v.get("tabella")):
            return "GOV.UK international driving permit table"
        return f"FCDO travel advice for {P}, GOV.UK"
    if k == "ca":
        return f"Government of Canada travel advice for {P}, travel.gc.ca"
    return f"Smartraveller advice for {P}"


# "It depends": da cosa dipende, letto SOLO nelle frasi citate (schemi fissi); casi particolari scritti a mano (revisione del 28/10/2026)
DIPENDE_A_MANO = {
    ("au", "IS"): "on how long you have held your licence and on whether you hire a car",
    ("au", "GR"): "on your type of licence (Smartraveller says to ask the Greek embassy or consulate)",
    ("uk", "OM"): "on how long you stay (the first 6 weeks, in a rental car)",
    ("ca", "AE"): "on the emirate: Dubai or the rest of the UAE",
    ("au", "FJ"): "on how long you stay",
    ("ca", "RO"): "on how long you stay",
    ("au", "AZ"): "on your travel and car insurance (Smartraveller says to check with your insurer and car provider)",
}
DIPENDE_SCHEMI = [
    (re.compile(r"\bstates?\b|\bprovinces?\b|\bterritories\b|\bDubai\b|\bemirates?\b", re.I), "on the state or province where you drive"),
    (re.compile(r"\bup to\b|\bfor (?:the first|a period of|\d+|one|two|three|six|twelve)\b|\bfirst (?:year|\d+)|\blonger\b|\bbeyond\b|"
                r"\bmore than \d|\blimited time\b|\bafter (?:\d+|one|that|this)\b|\bfor periods\b", re.I), "on how long you stay"),
    (re.compile(r"\bhir(?:e|ing)\b|\brent(?:al|ing)?\b", re.I), "on whether you hire a car"),
    (re.compile(r"translat|notari[sz]ed", re.I), "on whether you carry a translation of your licence instead of an IDP"),
]


def dipende_da_pat(k, c, v):
    """'on how long you stay and on whether you hire a car': ciò che le frasi citate nominano; vuoto se non nominano nulla."""
    if (k, c) in DIPENDE_A_MANO:
        return DIPENDE_A_MANO[(k, c)]
    t = " ".join(v["frasi"])
    regione = {"US": "on the state where you drive", "CA": "on the province or territory where you drive"}.get(c)
    parti = [(regione or testo) if testo.startswith("on the state") else testo for rx, testo in DIPENDE_SCHEMI if rx.search(t)]
    if not parti:
        return ""
    return parti[0] if len(parti) == 1 else ", ".join(parti[:-1]) + " and " + parti[-1]


def risposta_pat(k, c):
    """Prima frase della pagina: sì / no / dipende, frase dell'ente tra virgolette, fonte e data. Solo modelli fissi (verifica.py li ricalcola)."""
    v, T = voce_pat(k, c), PATENTI[k]
    e, ff, P = v["esito"], v["frasi"], frase_srv(c)
    d = data_lunga(data_pat(k, v))
    src = fonte_breve_pat(k, v, c)
    if e == "dipende":
        da = dipende_da_pat(k, c, v)
        return f"It depends{' ' + da if da else ''}. {T['Ente']} says: {cita_pat(ff)} ({src}, checked on {d})."
    if e in ("si", "no", "consigliato", "locale"):
        return f"{ESITI_PAT[e][2]} {T['Ente']} says: {cita_pat(ff)} ({src}, checked on {d})."
    if e == "non_detto":
        if ff:
            return (f"Not stated by {T['ente']}: its advice for {P} does not say whether you need an international driving permit. "
                    f"It says: {cita_pat(ff)} ({src}, checked on {d}).")
        if k == "uk" and v.get("tabella"):
            return (f"Not stated by GOV.UK. Its international driving permit table lists {P} with the {v['tabella']['tipo']} IDP, but neither the table "
                    f"nor the FCDO travel advice for {P} says whether you need one with a UK photocard licence (checked on {d}).")
        return f"Not stated by {T['ente']}: its travel advice for {P} says nothing about an international driving permit (checked on {d})."
    return f"Read the official text below: {T['ente']}'s wording for {P} does not fit a simple answer (checked on {d})."


RX_CONV_NO = re.compile(r"no longer accepts the (19(?:26|49|68))|The (19(?:26|49|68)) IDP is not accepted", re.I)


def conv_fcdo_diversa(k, v):
    """Convenzioni nominate dai consigli FCDO (escluse quelle "not accepted") ma diverse da quella della tabella GOV.UK (Libano: tabella 1949,
    FCDO «a 1968 international driving permit … The 1949 IDP is not accepted anymore»). Vuoto se coincidono o se l'FCDO non ne nomina."""
    if k != "uk" or not v.get("tabella"):
        return []
    tutte = {m for b in v["testo"] for m in re.findall(r"\b(19(?:26|49|68))\b", b["x"])}
    rifiutate = {x for b in v["testo"] for g in RX_CONV_NO.findall(b["x"]) for x in g if x}
    return sorted(tutte - rifiutate - {v["tabella"]["tipo"]})


def tipo_breve_pat(k, v):
    """Colonna "Type" delle tabelle per patente: la convenzione; se FCDO e tabella GOV.UK non coincidono, tutte e due."""
    c = v.get("convenzione")
    if not c:
        return "–"
    altre = conv_fcdo_diversa(k, v)
    return f"{c} (table); {' and '.join(altre)} (FCDO)" if altre else c


def conv_pat(k, v):
    """Tipo di permesso (convenzione) come lo scrive la fonte; nulla se la fonte non lo dice."""
    c = v.get("convenzione")
    if not c:
        return ""
    if k == "uk" and v.get("tabella"):
        altre = conv_fcdo_diversa(k, v)
        if altre:
            return (f"{c} in the GOV.UK table, but the FCDO travel advice names the {' and '.join(altre)} permit"
                    + (" and says the 1949 IDP is no longer accepted" if any(RX_CONV_NO.search(b["x"]) for b in v["testo"]) else "")
                    + ": read both below")
        return f"{c} (GOV.UK table)"
    return f"{c} (named on the official page)"


# etichette dei link "Useful links" delle schede canadesi (senza punto finale): non sono frasi della scheda, non si mostrano
ETICHETTA_LINK_CA = re.compile(r"^(?:More about the )?International driving permits?$|^[^.!?:]* [–-] [^.!?:]*[^.!?:;)]$", re.I)


def testo_fonte_pat(k, v, c):
    """Citazione completa della fonte, con titolo, link e date."""
    T, P = PATENTI[k], frase_srv(c)
    out = []
    if k == "uk" and v.get("tabella"):
        r = v["tabella"]
        out.append(f'<h3>GOV.UK: international driving permit table</h3><div class="tab tab-b"><table><caption class="sr">Row of the GOV.UK international driving permit '
                   f'table for {escape(P)}</caption><thead><tr><th>Country or territory</th><th>Type of IDP</th><th>More information</th></tr></thead><tbody>'
                   f'<tr><td data-l="Country or territory">{escape(r["nome"])}</td><td data-l="Type of IDP">{escape(r["tipo"])}</td>'
                   f'<td data-l="More information">{escape(r["nota"]) or "–"}</td></tr></tbody></table></div>')
        if v.get("tabella_regione"):
            rr = v["tabella_regione"]
            out.append(f'<p>The table also has a row for <strong>{escape(rr["nome"])}</strong>: type of IDP {escape(rr["tipo"])}'
                       + (f', “{escape(rr["nota"])}”' if rr["nota"] else ", no further information") + ".</p>")
        g = PAT["fonti"]["uk"]
        out.append(f'<p class="fonte">Source: <a href="{escape(g["pagina_idp"])}" rel="noopener">GOV.UK, Driving abroad: check if you need an international driving permit (IDP)</a>, '
                   f'page updated {data_lunga(g["guida_aggiornata"])}, checked on {data_lunga(g["letto_il"])}. GOV.UK says: “{escape(PAT_G["uk_tabella"])}”</p>')
    if v["testo"]:
        if k == "uk":
            tit = f"FCDO travel advice for {escape(P)}" + (f": “{escape(v['titolo_sezione'])}”" if v.get("titolo_sezione") else "")
        elif k == "ca":
            tit = f"Government of Canada travel advice for {escape(P)}: “Laws and culture” › “{escape(v.get('titolo_sezione') or 'Driving')}”"
        else:
            tit = f"Smartraveller advice for {escape(P)}: “Local travel”" + (f" › “{escape(v['titolo_sezione'])}”" if v.get("titolo_sezione") else "")
        bb = [b for b in v["testo"] if not (k == "ca" and b["t"] == "p" and ETICHETTA_LINK_CA.search(b["x"]))]
        out.append(f"<h3>{tit}</h3>{blocchi_html(bb)}")
        agg = f", page updated {data_lunga(v['aggiornata'])}" if v.get("aggiornata") else ""
        ancora = f", “still current at” {data_lunga(v['ancora_valida_il'])} (Australian time)" if v.get("ancora_valida_il") else ""
        nome_link = {"uk": f"FCDO travel advice: {v.get('nome_fonte') or P}", "ca": f"travel.gc.ca: {v.get('nome_fonte') or P}",
                     "au": f"Smartraveller: {v.get('nome_fonte') or P}"}[k]
        out.append(f'<p class="fonte">Source: <a href="{escape(v["url"])}" rel="noopener">{escape(nome_link)}</a>{agg}{ancora}, checked on {data_lunga(v["letto_il"])}. '
                   "Quoted word for word; we show only the sentences about driving licences and permits.</p>")
    elif v.get("url"):
        out.append(f'<p>The {escape(T["ente"])} travel advice for {escape(P)} has nothing about driving licences or permits '
                   f'(<a href="{escape(v["url"])}" rel="noopener">official page</a>, checked on {data_lunga(v["letto_il"])}).</p>')
    return "".join(out)


def dove_idp(k):
    """Dove si ottiene il permesso e quanto vale: SOLO frasi ufficiali generali (controllate da raccolta/patenti.py)."""
    if k == "uk":
        g = PAT["fonti"]["uk"]
        return (f'<p>GOV.UK says:</p>{cit_html([PAT_G["uk_paypoint"], PAT_G["uk_costo"], PAT_G["uk_durata"], PAT_G["uk_sempre_patente"]])}'
                f'<p class="fonte">Source: <a href="{escape(g["pagina_get"])}" rel="noopener">GOV.UK, Get an international driving permit (IDP)</a> and '
                f'<a href="{escape(g["pagina_idp"])}" rel="noopener">Check if you need an IDP</a>, checked on {data_lunga(g["letto_il"])}.</p>')
    if k == "ca":
        g = PAT["fonti"]["ca"]
        mod = f", page modified {data_lunga(g['idp_modificata'])}" if g.get("idp_modificata") else ""
        return (f'<p>The Government of Canada says:</p>{cit_html([PAT_G["ca_caa"], PAT_G["ca_anno"], PAT_G["ca_classe"]])}'
                f'<p class="fonte">Source: <a href="{escape(g["pagina_idp"])}" rel="noopener">travel.gc.ca, International Driving Permit</a>{mod}, checked on {data_lunga(g["letto_il"])}.</p>')
    g = PAT["fonti"]["au"]
    return (f'<p>Smartraveller says (in its advice for Vietnam):</p>{cit_html([PAT_G["au_falsi"], PAT_G["au_aaa"]])}'
            f'<p class="fonte">Source: <a href="{escape(g["pagina_aaa"])}" rel="noopener">Smartraveller: Vietnam</a>, checked on {data_lunga(PAT_PER["VN"]["au"]["letto_il"])}.</p>')


def faq_pat(k, c):
    v, T, P = voce_pat(k, c), PATENTI[k], frase_srv(c)
    r = risposta_pat(k, c)
    out = [(f"Do I need an international driving permit for {P} with {T['chi']}?", r)]
    if v["esito"] in ("si", "no", "dipende", "consigliato"):
        out.append((f"Can I drive in {P} with my {T['lic']}?", f"{T['Ente']} says: {cita_pat(v['frasi'])}"))
    if v["esito"] in ("si", "dipende", "consigliato"):
        if k == "uk":
            if v.get("tabella"):
                a = f"GOV.UK's international driving permit table lists the {v['tabella']['tipo']} IDP for {P}."
                if conv_fcdo_diversa(k, v):
                    a += f" The FCDO travel advice for {P} names the {' and '.join(conv_fcdo_diversa(k, v))} permit."
            else:
                a = f"GOV.UK's international driving permit table does not list {P}. GOV.UK says: “{PAT_G['uk_non_in_tabella']}”"
        elif v.get("convenzione"):
            a = f"The {T['fonte']} advice for {P} names the {v['convenzione']} permit."
        else:
            a = f"The {T['fonte']} advice for {P} does not say which convention (1926, 1949 or 1968) the permit must follow."
        out.append((f"Which international driving permit do I need for {P}?", a))
    luogo = {"uk": f"GOV.UK says: “{PAT_G['uk_paypoint']}” “{PAT_G['uk_costo']}”",
             "ca": f"The Government of Canada says: “{PAT_G['ca_caa']}” “{PAT_G['ca_anno']}”",
             "au": f"Smartraveller says: “{PAT_G['au_aaa']}”"}[k]
    out.append((f"Where do I get an international driving permit in {T['paese']}?", luogo))
    out.append((f"Where does this answer come from?", f"From the official travel advice of {T['ente']}, read on {data_lunga(data_pat(k, v))} and quoted word for word on this page. "
                "It is information, not legal advice."))
    return out


def html_faq_pat(k, c):
    faq = faq_pat(k, c)
    h = "".join(f"<h3>{escape(q)}</h3><p>{escape(a)}</p>" for q, a in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    return f'<section class="faq"><h2>Questions</h2>{h}</section>', [ld]


def titoli_pat(k, c):
    T, b = PATENTI[k], ESITI_PAT[voce_pat(k, c)["esito"]][3]
    P, Pm = nome_titolo_pat(c), nome_titolo_pat(c, True)
    L = f"{T['art']} {T['titolo']}"
    return [f"Do I Need an IDP for {P} with {L}? {b} ({ANNO})", f"Do I Need an IDP for {P} with {L}? ({ANNO})",
            f"Driving in {P} with {L}: IDP? ({ANNO})", f"{Pm}: IDP with {L} ({ANNO})", f"{Pm} IDP, {T['agg']} Licence ({ANNO})"]


def descrizioni_pat(k, c):
    T, P, v = PATENTI[k], frase_srv(c), voce_pat(k, c)
    b = ESITI_PAT[v["esito"]][0]
    d = data_lunga(data_pat(k, v))
    return [f"Do you need an international driving permit to drive in {P} with {T['chi']}? {b}: official {T['fonte']} advice, quoted, checked on {d}.",
            f"International driving permit for {P} with {T['art']} {T['lic']}: {b}. Official {T['fonte']} advice, checked on {d}.",
            f"{nome_titolo_pat(c, True)}, {T['lic']}: {b}. Official advice, checked on {d}."]


AVVISO_PAT = ('<p class="avviso"><strong>Rules change, and car hire companies can ask for more than the law.</strong> We quote the official travel advice '
              'word for word, with its date; this is information, not legal advice. If you are unsure, ask the embassy of the country you are visiting, '
              'your car hire company or your travel insurer before you travel.</p>')


def box_noleggio():
    """Segnaposto del riquadro "Hire a car": spento finché NOLEGGIO_AUTO è vuoto."""
    return NOLEGGIO_AUTO


def pagina_pat(k, c):
    rel = "../../../"
    v, T, P = voce_pat(k, c), PATENTI[k], frase_srv(c)
    e = v["esito"]
    altri = []
    for k2 in PATENTI:
        if k2 != k and voce_pat(k2, c):
            altri.append(f'<tr data-voce><td data-l="Licence"><a href="{link_pat(k2, c, rel)}">{escape(PATENTI[k2]["Lic"])}</a></td>'
                         f'<td data-l="In {escape(nome_srv(c))}">{badge_pat(k2, c)}</td><td data-l="Checked">{data_lunga(data_pat(k2, voce_pat(k2, c)))}</td></tr>')
    ingresso = ingresso_srv(c, rel)
    conv = conv_pat(k, v)
    faq_h, faq_ld = html_faq_pat(k, c)
    corpo = f"""<section class="hero"><h1>Can I drive in {escape(P)} with {T['art']} {escape(T['lic'])}? Do I need an international driving permit?</h1></section>
<section class="card summary" aria-label="Answer">
<div class="s-top"><span class="sq">{ico("car")}</span><span>{escape(T['lic'])} · {escape(nome_srv(c))}</span><span>{ANNO}</span></div>
<div class="s-body">
<div class="esito e-srv {CLASSE_PAT[e]}">{ico(ICONA_PAT[e])}<strong>{escape(ESITI_PAT[e][0])}</strong></div>
<p class="lead" id="answer">{escape(risposta_pat(k, c))}</p>
{(f'<p class="lead">If you need a permit anyway (for example because your car hire company asks for one), the type is: <strong>{escape(conv)}</strong>.</p>' if e == "no" else f'<p class="lead">Type of international driving permit: <strong>{escape(conv)}</strong>.</p>') if conv else ""}
</div></section>
{AVVISO_PAT}
<h2>What the official source says</h2>
{testo_fonte_pat(k, v, c)}
{AD}
<h2>What to bring and where to get an IDP</h2>
{dove_idp(k)}
{box_noleggio()}
{f'<h2>Other licences in {escape(P)}</h2><div class="tab tab-b"><table><caption class="sr">International driving permit in {escape(P)} for other licences, from official advice</caption><thead><tr><th>Licence</th><th>In {escape(nome_srv(c))}</th><th>Checked</th></tr></thead><tbody>{"".join(altri)}</tbody></table></div>' if altri else ""}
{f'<h2>Before you travel to {escape(P)}</h2><ul>' + "".join(f"<li>{x}</li>" for x in ingresso) + "</ul>" if ingresso else ""}
{faq_h}
<p class="small">Spotted a change? <a href="{rel}contact/?ref=driving-abroad">Tell us</a>. <a href="{rel}{url_pat(k)}">Every country for {T['art']} {escape(T['lic'])}</a> · <a href="{rel}{PAT_BASE}/">Driving abroad: all licences</a>.</p>"""
    pagina(url_pat(k, c), scegli(titoli_pat(k, c), LIMITE_TITOLO_PAT), scegli(descrizioni_pat(k, c), LIMITE_DESCRIZIONE), corpo,
           briciole=[("Driving abroad", f"{PAT_BASE}/"), (T["Lic"], url_pat(k)), (nome_srv(c), url_pat(k, c))],
           ld_extra=faq_ld, js=APP_JS_FILTRO)
    LASTMOD[url_pat(k, c)] = data_pat(k, v)


def conteggi_pat(k):
    from collections import Counter
    return Counter(p[k]["esito"] for p in PAT["paesi"] if p[k])


def prima_frase_patente(k):
    """Prima frase della pagina di una patente: conteggi per esito, fonte e data."""
    n, T = conteggi_pat(k), PATENTI[k]
    d = data_lunga(max(p[k]["letto_il"] or PAT["fonti"]["uk"]["letto_il"] for p in PAT["paesi"] if p[k]))
    fonte = {"uk": "GOV.UK (international driving permit table and FCDO travel advice)", "ca": "the Government of Canada (travel.gc.ca)",
             "au": "Smartraveller (Australian Government)"}[k]
    return (f"With {T['chi']}, the official advice of {fonte} says you need an international driving permit in {n['si']} countries and territories, "
            f"you do not need one in {n['no']}, it depends in {n['dipende']} (usually on how long you stay or on hiring a car), it is recommended in "
            f"{n['consigliato']}, and a local licence or permit is needed in {n['locale']}; it says nothing about permits for {n['non_detto']} (last checked {d}).")


def titoli_patente(k):
    T = PATENTI[k]
    return [f"Do I Need an IDP with {T['art']} {T['titolo']}? Every Country ({ANNO})", f"IDP with {T['art']} {T['titolo']}: Every Country ({ANNO})"]


def pagina_patente(k):
    rel = "../../"
    T = PATENTI[k]
    n = conteggi_pat(k)
    paesi = sorted((p for p in PAT["paesi"] if p[k] and p["iso2"] in PAESI_ISO), key=lambda p: ordine_srv(p["iso2"]))
    righe = []
    for p in paesi:
        c, v = p["iso2"], p[k]
        nome = (f'<a href="{rel}{url_pat(k, c)}">{escape(nome_srv(c))}</a>' if c in PAGINE_PAT[k] else escape(nome_srv(c))) + alias_srv(c)
        parola = cita_pat(v["frasi"]) if v["frasi"] else "–"
        righe.append(f'<tr data-voce id="{c.lower()}"><td data-l="Country or territory">{nome}</td><td data-l="IDP?">{badge_pat(k, c)}</td>'
                     f'<td data-l="Type">{escape(tipo_breve_pat(k, v))}</td><td data-l="Official wording">{escape(parola)}</td>'
                     f'<td data-l="Checked">{data_lunga(data_pat(k, v))}</td></tr>')
    griglia = "".join(f'<a href="{rel}{url_pat(k, c)}">{escape(nome_srv(c))}<small>{escape(ESITI_PAT[voce_pat(k, c)["esito"]][0])}</small></a>' for c in PAGINE_PAT[k])
    tipo = ("“Type” is the type of IDP that GOV.UK's table lists for the country (1926, 1949 or 1968), even where you do not need one with a photocard licence."
            if k == "uk" else f"“Type” is shown only where the {T['ente']} page names the convention (1926, 1949 or 1968).")
    corpo = f"""<section class="hero">{h1_diviso(f"Do I need an international driving permit with {T['art']} {T['lic']}? Every country ({ANNO})")}
<p class="lead" id="answer">{escape(prima_frase_patente(k))}</p></section>
<ul class="stat"><li><strong>{n['si']}</strong>IDP needed</li><li><strong>{n['no']}</strong>no IDP needed</li><li><strong>{n['dipende']}</strong>it depends</li><li><strong>{n['consigliato'] + n['locale']}</strong>recommended or local permit</li></ul>
{AVVISO_PAT}
<h2>Most searched with {T['art']} {escape(T['lic'])}</h2>
<div class="griglia g-srv">{griglia}</div>
{AD}
<h2>Every country and territory</h2>
<p>Each answer quotes the official sentence that decides it. “It depends” means the official text sets a condition (length of stay, hiring a car, a translation, the region); “Not stated” means the official advice for that country says nothing about permits. {escape(tipo)} Click a country for the full official text.</p>
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Type a country, e.g. Japan" data-filtro-multi aria-label="Search countries"></div>
<div class="tab tab-b tab-pat"><table><caption class="sr">International driving permit with {T['art']} {escape(T['lic'])}, by country, from official advice</caption><thead><tr><th>Country or territory</th><th>IDP?</th><th>Type</th><th>Official wording</th><th>Checked</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>
<h2>Where to get an international driving permit</h2>
{dove_idp(k)}
<h2>How we read the official advice</h2>
<p>{metodo_pat(k)} More on the <a href="{rel}about/#driving-abroad">About page</a>. Spotted a change? <a href="{rel}contact/?ref=driving-abroad">Tell us</a>.</p>
<p><a href="{rel}{PAT_BASE}/">Driving abroad: UK, Canadian and Australian licences</a></p>"""
    desc = [f"Do you need an international driving permit with {T['art']} {T['lic']}? Every country, from official {T['fonte']} advice: {n['si']} yes, {n['no']} no, {n['dipende']} it depends.",
            f"International driving permit with {T['art']} {T['lic']}: every country, from official advice."]
    pagina(url_pat(k), scegli(titoli_patente(k), LIMITE_TITOLO_PAT), scegli(desc, LIMITE_DESCRIZIONE), corpo,
           briciole=[("Driving abroad", f"{PAT_BASE}/"), (T["Lic"], url_pat(k))], js=APP_JS_FILTRO)
    LASTMOD[url_pat(k)] = max(data_pat(k, p[k]) for p in PAT["paesi"] if p[k])


def metodo_pat(k):
    if k == "uk":
        return ("For UK licences we read two GOV.UK pages: the international driving permit table (“Country or territory / Type of IDP / More information”) and "
                "the driving paragraphs of the FCDO travel advice for each country. A table row with nothing under “More information” only tells you the type of "
                "IDP: the answer then comes from the FCDO advice. When the two pages disagree we give the more cautious answer and quote both.")
    if k == "ca":
        return ("For Canadian licences we read the “Driving” part of the “Laws and culture” section of the Government of Canada travel advice for each destination, "
                "through the official open data files. “Must carry an international driving permit” is “IDP needed”; “should carry” is “Recommended”.")
    return ("For Australian licences we read the driving paragraphs (“Driving permit” and similar) of the “Local travel” part of the Smartraveller advice for each "
            "destination. Smartraveller blocks simple automated requests, so its pages are read in a browser.")


def pagina_hub_pat():
    rel = "../"
    nomi = {k: PATENTI[k]["lic"] for k in PATENTI}
    tutti = sorted((p for p in PAT["paesi"] if p["iso2"] in PAESI_ISO), key=lambda p: ordine_srv(p["iso2"]))
    righe = "".join(f'<tr data-voce id="{p["iso2"].lower()}"><td data-l="Country or territory"><strong>{escape(nome_srv(p["iso2"]))}</strong>{alias_srv(p["iso2"])}</td>' +
                    "".join((f'<td data-l="{escape(nomi[k])}"><a class="a-badge" href="{link_pat(k, p["iso2"], rel)}">{badge_pat(k, p["iso2"])}</a></td>' if p[k]
                             else f'<td data-l="{escape(nomi[k])}">–</td>') for k in PATENTI) + "</tr>" for p in tutti)
    carte = "".join(f'<a href="{rel}{url_pat(k)}">{ico("car")} {escape(PATENTI[k]["Lic"])}: every country'
                    f'<small>{conteggi_pat(k)["si"]} IDP needed · {conteggi_pat(k)["no"]} not needed · {conteggi_pat(k)["dipende"]} it depends</small></a>' for k in PATENTI)
    popolari = []
    for k, c in (("uk", "JP"), ("uk", "US"), ("uk", "IT"), ("ca", "IT"), ("ca", "JP"), ("au", "JP"), ("au", "IT"), ("uk", "ES"), ("ca", "GB"), ("au", "GB"),
                 ("uk", "AU"), ("au", "US"), ("ca", "US"), ("uk", "TH"), ("au", "ID"), ("uk", "GR")):
        if c in PAGINE_PAT[k] and len(popolari) < 15:
            popolari.append(f'<a href="{rel}{url_pat(k, c)}">{escape(nome_srv(c))}, {escape(nomi[k])}<small>{escape(ESITI_PAT[voce_pat(k, c)["esito"]][0])}</small></a>')
    d = data_lunga(PAT["controllato_il"])
    corpo = f"""<section class="hero">{h1_diviso(f"Driving abroad: do I need an international driving permit? UK, Canadian and Australian licences ({ANNO})")}
<p class="lead" id="answer">Whether you need an international driving permit (IDP) depends on the country you visit and on the licence you hold. For each country we quote what the UK government (GOV.UK and FCDO), the Government of Canada (travel.gc.ca) and the Australian Government (Smartraveller) say about driving there with their licence, with the date we checked it (last check {d}).</p></section>
<div class="griglia g-pat">{carte}</div>
{AVVISO_PAT}
<h2>Most searched</h2>
<div class="griglia">{"".join(popolari)}</div>
{AD}
<h2>Every country, every licence</h2>
<p>Click an answer for the official sentence, the source and the date. “Not stated” means that government's advice for the country says nothing about driving permits.</p>
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Type a country, e.g. Italy" data-filtro-multi aria-label="Search countries"></div>
<div class="tab tab-b tab-srv"><table><caption class="sr">Do you need an international driving permit? Official advice for UK, Canadian and Australian licences, by country, checked on {d}</caption><thead><tr><th>Country or territory</th>{"".join(f"<th>{escape(nomi[k])}</th>" for k in PATENTI)}</tr></thead><tbody>{righe}</tbody></table></div>
<h2>How we check</h2>
<p>{metodo_pat("uk")} {metodo_pat("ca")} {metodo_pat("au")} We only use official government sources and never fill a gap with our own reading: where the advice is silent, we say so. More on the <a href="{rel}about/#driving-abroad">About page</a>.</p>"""
    pagina(f"{PAT_BASE}/", f"Driving Abroad: Do I Need an IDP? UK, Canada, Australia ({ANNO})",
           scegli([f"Do you need an international driving permit? Official GOV.UK, Government of Canada and Smartraveller advice for every country, checked on {d}.",
                   f"International driving permit by country for UK, Canadian and Australian licences, from official advice."], LIMITE_DESCRIZIONE),
           corpo, briciole=[("Driving abroad", f"{PAT_BASE}/")], js=APP_JS_FILTRO)
    LASTMOD[f"{PAT_BASE}/"] = PAT["controllato_il"]


def link_guida(rel, c, prima=None):
    """'Driving in X: UK licence · Canadian licence · Australian licence' verso le pagine Paese × patente che esistono (prima quella indicata)."""
    if not PAT or not c:
        return ""
    ordine = ([prima] if prima else []) + [k for k in PATENTI if k != prima]
    ll = [f'<a href="{rel}{url_pat(k, c)}">{escape(PATENTI[k]["lic"])}</a>' for k in ordine if c in PAGINE_PAT[k]]
    if not ll:
        return ""
    return f'<p class="altri-pass">{ico("car")}<span>Driving in {escape(frase_srv(c))}, do you need an international driving permit? {" · ".join(ll)}</span></p>'


# pagine passaporto -> codice ISO (per il link "Driving in X"): britanniche dalla pagina FCDO, canadesi dal codice, australiane dal nome
ISO_DA_FCDO = {p["uk"]["slug_fcdo"]: p["iso2"] for p in (PAT["paesi"] if PAT else []) if p["uk"] and p["uk"].get("slug_fcdo") and p["iso2"] not in ("TK", "NU", "BL")}
ISO_DA_AU = {_chiave_nome(p["au"]["nome_fonte"]): p["iso2"] for p in (PAT["paesi"] if PAT else []) if p["au"] and p["au"].get("nome_fonte")}


def home_pat():
    if not PAT:
        return ""
    voci = []
    for k, c in (("uk", "JP"), ("uk", "US"), ("ca", "IT"), ("au", "JP"), ("uk", "IT"), ("ca", "GB"), ("au", "US"), ("uk", "TH")):
        if c in PAGINE_PAT[k]:
            voci.append(f'<a href="{url_pat(k, c)}">{escape(nome_srv(c))}, {escape(PATENTI[k]["lic"])}<small>{escape(ESITI_PAT[voce_pat(k, c)["esito"]][0])}</small></a>')
    return (f'<h2>Driving abroad: do you need an international driving permit?</h2><p>What GOV.UK, the Government of Canada and Smartraveller say about '
            f'driving in each country with a UK, Canadian or Australian licence, quoted with the date: <a href="{PAT_BASE}/">every country and every licence</a>.</p>'
            f'<div class="griglia">{"".join(voci)}</div>')


def about_pat(rel):
    if not PAT:
        return ""
    g = PAT["fonti"]
    return f"""<h2 id="driving-abroad">Driving abroad: international driving permits</h2>
<p>Sources: for UK licences, the GOV.UK guide “Driving abroad” (<a href="{escape(g['uk']['pagina_idp'])}" rel="noopener">check if you need an international driving permit</a>, page updated {data_lunga(g['uk']['guida_aggiornata'])}, {g['uk']['righe_tabella']} rows in the table) and the driving paragraphs of the FCDO travel advice for each country; for Canadian licences, the “Driving” part of the “Laws and culture” section of the Government of Canada travel advice (travel.gc.ca, through the official open data files) and its <a href="{escape(g['ca']['pagina_idp'])}" rel="noopener">International Driving Permit page</a>; for Australian licences, the driving paragraphs of the “Local travel” part of the Smartraveller advice for each destination, read in a browser. All read on {data_lunga(PAT['controllato_il'])}, except Smartraveller ({data_lunga(g['au']['letto_dal'])}{"" if g['au']['letto_dal'] == g['au']['letto_al'] else " to " + data_lunga(g['au']['letto_al'])}). Licences: Open Government Licence v3.0, Open Government Licence – Canada, CC BY 4.0.</p>
<p>Rules: the answer comes only from the official sentence, which we quote on the page. An answer is “IDP needed” only when the official text says you must have one, “No IDP needed” only when it says you can drive with your licence (or that you do not need an IDP), “It depends” when it sets a condition (length of stay, hiring a car, a translation, the region), “Recommended” when it says you should carry one, and “Local permit needed” when it says you need a local licence or permit. When official pages disagree, we give the more cautious answer and quote both. Where the advice is silent we write “Not stated”. Most answers are read with fixed wording rules; the rest were read one by one on 28 October 2026 and are checked again whenever the official text changes. A page for a single country and licence exists only where people search for it. This is information, not legal advice.</p>"""


# ---------------------------------------------------------------- home e pagine di servizio
def home():
    auto = sum(1 for P in PAESI if P["regola"])
    due = [A for A in AER["aeroporti"] if A["regola"] == "2l"]
    griglia_2l = "".join(f'<a href="liquids/{A["slug"]}/">{escape(A["nome"])}<small>{escape(A["paese"])}</small></a>' for A in due)
    popolari = ["spain", "france", "italy", "portugal", "greece", "turkey", "usa", "united-arab-emirates", "thailand", "egypt", "morocco", "mexico",
                "cyprus", "croatia", "netherlands", "germany", "dominican-republic", "jamaica", "india", "japan"]
    mappa = {P["slug"]: P for P in PAESI}
    def _breve_pop(P):
        R = P["regola"]
        return "Schengen rule" if (R and R.get("schengen") and breve_regola(R, P) == regola_sch) else breve_regola(R, P)
    sch = [mappa[s] for s in popolari if s in mappa and mappa[s]["regola"] and mappa[s]["regola"].get("schengen")]
    regola_sch = breve_regola(sch[0]["regola"], sch[0]) if sch else ""
    nota_sch = (f'<p class="small" style="margin:0 0 12px"><strong>{escape(regola_sch)}</strong> for the Schengen countries below ({len([P for P in sch if breve_regola(P["regola"], P) == regola_sch])} of them): '
                f'{escape(sintesi_regola(sch[0]["regola"]))} (FCDO). Each page quotes the official text.</p>') if sch else ""
    griglia_pass = "".join(f'<a href="passport-validity/{s}/">{escape(mappa[s]["nome"])}<small>{escape(_breve_pop(mappa[s]))}</small></a>'
                           for s in popolari if s in mappa)
    stato_etias = "not in operation" if any("currently not in operation" in f["frase"] for f in frasi_ees("etias")) else "see the official page"
    ultimo = data_lunga(max(PASS["controllato_il"], AER["controllato_il"], EES["controllato_il"], BAG.get("controllato_il", "")))
    testata = f"""<div class="band"><div class="wrap band-in">
<section class="hero">{h1_diviso(f"Before You Fly: passport validity, airport liquids rules, cabin bag sizes and EU entry checks ({ANNO})")}
<p class="scope"><span class="pill">{ico("passport")}British passport checker</span><span>Passport rules from the UK government (FCDO), for British citizens.{"".join(f' {ESTERI[k]["agg"]} passport: <a href="{ESTERI[k]["base"]}/" style="color:var(--sign)">{len(VOCI[k])} destinations</a>.' for k in ESTERI if VOCI[k])}</span></p>
<p class="sub">Five checks before you fly, answered from official sources only.</p>
{f'<p class="scope" lang="it"><span class="pill">{ico("passport")}Cittadinanza italiana</span><span><a href="{IT_BASE}/" hreflang="it" style="color:var(--sign)">Documenti per viaggiare all\'estero</a>: passaporto, carta d\'identità e visto per {len(VOCI_IT)} Paesi, dalle schede della Farnesina (Viaggiare Sicuri).</span></p>' if VOCI_IT else ""}
<p class="trust"><span>{ico("shield")}Official sources · last checked {ultimo}</span><span>{ico("lock")}Your dates stay in your browser</span></p></section>
<ul class="tiles">
<li><a href="passport-validity/"><span class="sq">{ico("passport")}</span><h2>Passport validity</h2><small>FCDO passport validity and visa rules for British passports, {len(PAESI)} destinations, a date checker for {auto} of them. Last checked: {data_lunga(PASS['controllato_il'])}.</small></a></li>
<li><a href="liquids/"><span class="sq">{ico("bottle")}</span><h2>Liquids by airport</h2><small>100 ml or 2 litres? {len(AER['aeroporti'])} airports plus the US and Canada rules, from official pages.</small></a></li>
<li><a href="cabin-bags/"><span class="sq">{ico("bag")}</span><h2>Cabin bags</h2><small>Free under-seat bag and cabin bag sizes for {len(COMPAGNIE)} airlines, plus a “does my bag fit?” checker.</small></a></li>
<li><a href="ees-etias/"><span class="sq">{ico("scan")}</span><h2>EES &amp; ETIAS</h2><small>EES is fully operational; ETIAS is {stato_etias} (European Commission).</small></a></li>
{f'<li><a href="{SRV_BASE}/"><span class="sq">{ico("apps")}</span><h2>Apps by country</h2><small>Starlink, Apple Pay, Spotify, YouTube Premium: the official country lists.</small></a></li>' if SERVIZI_SRV else ""}
{f'<li><a href="{PAT_BASE}/"><span class="sq">{ico("car")}</span><h2>Driving abroad</h2><small>Do you need an international driving permit? UK, Canadian and Australian licences, every country.</small></a></li>' if PAT else ""}
</ul>
<h2 class="band-h2">Check your passport dates</h2>
{modulo_checker('tutti-dati', True, link='passport-validity/')}
</div></div>"""
    corpo = f"""<p class="lead" style="margin-top:28px">Six things to check before you fly, answered from official sources only: is your passport valid long enough for your destination, can you take more than 100 ml of liquids through security, how big your cabin bag can be on your airline, what EES and ETIAS mean for your trip, which apps and services work in your destination, and whether you need an international driving permit to drive there. Every rule is quoted word for word with its source and the date we checked it.</p>
{AVVISO_PASS}
{AD}
<h2>Popular destinations</h2>
{nota_sch}<div class="griglia">{griglia_pass}</div>
<p><a href="passport-validity/">All {len(PAESI)} destinations</a></p>
<h2>Airports that allow up to 2 litres (official pages)</h2>
<div class="griglia">{griglia_2l}</div>
<p><a href="liquids/">All airports, including those that depend on the checkpoint</a></p>
<h2>Cabin bag size by airline</h2>
<p>The free bag you can take on board and when you pay for a cabin bag, from each airline's own page: <a href="cabin-bags/">{len(COMPAGNIE)} airlines in one table</a>, or <a href="cabin-bags/does-my-bag-fit/">check if your bag fits</a>.</p>
<div class="griglia">{"".join(f'<a href="cabin-bags/{C["slug"]}/">{escape(C["nome"])}<small>{escape(misura_breve(borsa_gratis(C, "sotto") or borsa_gratis(C, "sopra")))} free</small></a>' for C in COMPAGNIE if C["slug"] in ("ryanair", "easyjet", "wizz-air", "jet2", "british-airways", "vueling", "lufthansa", "klm"))}</div>
{home_srv()}
{home_pat()}
{box_affiliati()}
{dati_json('tutti-dati', [dati_client(P) for P in PAESI])}"""
    pagina("", f"Before You Fly {ANNO}: Passport, Visas, Liquids, Cabin Bags, EES",
           f"Passport and visa rules (FCDO) for {len(PAESI)} destinations, liquid limits at {len(AER['aeroporti'])} airports, cabin bag sizes of {len(COMPAGNIE)} airlines, EES/ETIAS. Official sources.",
           corpo, js=MOTORE_JS + APP_JS, testata=testata)


def about_esteri(rel):
    out = []
    for k in ESTERI:
        if not VOCI[k]:
            continue
        D, voci = ESTERI[k]["dati"], VOCI[k]
        nv = sum(1 for v in voci if v["p"]["visto"]["sintesi"])
        np_ = sum(1 for v in voci if v["p"]["passaporto"]["sintesi"])
        if k == "ca":
            out.append(f"""<h2>Canadian passport (Government of Canada)</h2>
<p>Source: the “Entry and exit requirements” section (“Regular Canadian passport” and “Visas”) of the Government of Canada travel advice and advisories for each destination (<a href="https://travel.gc.ca/travelling/advisories" rel="noopener">travel.gc.ca</a>, Global Affairs Canada), read through the official open data files of the dataset <a href="{escape(D['dataset_url'])}" rel="noopener">Country Travel Advice and Advisories</a>, last checked on {data_lunga(D['controllato_il'])}. Each page shows the date the official page was last updated.</p>
<p>Licence: {licenza_estera(k)} We reproduce the text unchanged; the summaries and short labels are ours. Before You Fly is not a Government of Canada site and is not endorsed by the Government of Canada.</p>
<p>Summaries: a one-line passport validity summary only when the official sentence matches a fixed wording (for example “Your passport must be valid for at least 6 months beyond the date you expect to leave …” or “… for the expected duration of your stay”) and names the destination ({np_} of {len(voci)} destinations); a visa summary only when the first line of the “Visas” section is “Tourist visa: not required for stays up to N days”, “Tourist visa: not required” or “Tourist visa: required”, with no time limit or exception, and when nothing in the entry section mentions an electronic travel authorization (eTA/ETA), an e-visa, an arrival card, an online form or registration, a tourist card or a fee ({nv} destinations). For the Schengen countries whose page says that ETIAS will be required (“You will be required to apply online and pay for an ETIAS before you travel”), the summary says so and adds, in the official words, that “Applications are not yet open”. A “Tourist visa: required” line is not summarised when the official text talks about a visa on arrival or an e-visa. Destinations whose official text has nothing specific on visas or passport validity get no page; the Canadian passport index links them to the official page.</p>""")
        else:
            out.append(f"""<h2>Australian passport (Smartraveller)</h2>
<p>Source: the “Travel” section (“Visas and border measures” or “Visas”, “Other formalities”, “European Entry and Exit Systems”, “Passport” and the other entry subsections) of the Smartraveller travel advice for each destination (<a href="https://www.smartraveller.gov.au/destinations" rel="noopener">smartraveller.gov.au</a>, Australian Government, Department of Foreign Affairs and Trade), last checked on {data_lunga(D['controllato_il'])}. The site blocks simple automated requests, so we read it in a browser. Each page shows the “Updated” and “Still current at” dates of the official page.</p>
<p>Licence: {licenza_estera(k)} Smartraveller's logos and trademarks are not used. Before You Fly is not an Australian Government site and is not endorsed by DFAT.</p>
<p>Summaries: Smartraveller writes in prose and, for most destinations, gives only its general passport advice (the same on every page), which we quote as general advice and never as a rule of the country. We add a one-line summary only when an official sentence matches a fixed wording and has no condition such as “usually”, “may” or “if you”, and (for visas) when nothing in the section mentions an eVisa, an electronic travel authority, an arrival card, an online form or registration, a visa on arrival, a tourist card or a fee: {nv} visa summaries and {np_} passport validity summaries for {len(voci)} destinations. A destination gets a page only if its Smartraveller text says something specific to it about visas, entry formalities or passport validity; the others ({len(SENZA_PAGINA_ESTERI[k])}, where the text is only general advice and contact details) are linked from the Australian passport index straight to Smartraveller.</p>""")
    return "".join(out)


def about_it(rel):
    if not VOCI_IT:
        return ""
    return f"""<h2>Italian citizens (Viaggiare Sicuri, in Italian)</h2>
<p>Source: the country pages of <a href="{VS_HOME}" rel="noopener">Viaggiare Sicuri</a>, run by the Crisis Unit of the Italian Ministry of Foreign Affairs (Farnesina), read through the public data files the site itself uses ({DOC_IT['schede_elenco']} pages, last checked on {data_lunga(DOC_IT['controllato_il'])}): the “Passaporto” and “Visto di ingresso” fields of the entry requirements section. Each page shows the date of the official page.</p>
<p>Licence: Viaggiare Sicuri states no licence for its texts, so we do not republish them. The <a href="{rel}{IT_BASE}/" hreflang="it">Italian section</a> gives the facts in our own words (document required, remaining passport validity, visa, electronic authorisations, length of stay), with short quotes of at most 20 words, the date and the link; a fact is summarised only when the official wording is unambiguous, otherwise the page says to read the official page. Before You Fly is not a site of the Farnesina or of the Italian Government.</p>"""


def about():
    rel = "../"
    manuali = [P for P in PAESI if not P["regola"]]
    lista_man = "".join(f'<li><a href="{rel}passport-validity/{P["slug"]}/">{escape(P["nome"])}</a>: {escape(P["motivo"])}</li>' for P in manuali)
    senza = "".join(f"<li>{escape(P['nome'])}: {escape(P['motivo'])}</li>" for P in SENZA_PAGINA)
    corpo = f"""<section class="hero"><h1>About {NOME} and our sources</h1></section><div class="testo">
<p>{NOME} is an independent project. It collects official travel rules and shows them word for word, with the link and the date we checked them. We are not affiliated with any government, airport or airline.</p>
<h2>Rules we follow</h2>
<ul><li>Only official sources: the UK government (GOV.UK, FCDO), the Government of Canada (travel.gc.ca), the Australian Government (Smartraveller), the European Commission and EU portals, airport operators, airlines (for their own bag rules), and national aviation security authorities (TSA, CATSA, Hong Kong Civil Aviation Department).</li>
<li>Every rule is quoted, not rewritten. Our short summaries are labelled as such and the official text is always on the same page.</li>
<li>If we cannot read an official page, or it is unclear, we leave it out and say so.</li>
<li>When two official texts disagree, we show both and do not choose.</li>
<li>This is information, not legal advice. Airlines, airports and border officials decide.</li></ul>
<h2>Passport validity (FCDO)</h2>
<p>Source: the “Passport validity requirements” and “Visa requirements” sections of the FCDO foreign travel advice for each destination, read through the GOV.UK Content API (<a href="https://www.gov.uk/api/content/foreign-travel-advice" rel="noopener">api/content/foreign-travel-advice</a>), last checked on {data_lunga(PASS['controllato_il'])}. The FCDO advice is written for British citizens.</p>
<p>Licence: contains public sector information licensed under the <a href="{OGL}" rel="noopener">Open Government Licence v3.0</a>. We reproduce the FCDO text unchanged; summaries, the short labels and the date checker are ours.</p>
<p>How the checker works: it applies the FCDO sentence literally. “At least 6 months after the date you arrive” means the expiry date must be on or after the same day of the month 6 months after arrival (if that day does not exist, the last day of that month). “More than” means at least one day later. “Valid for the duration of your stay” means not expiring before the day you leave. The Schengen “date of issue less than 10 years before the date you arrive” means issued after the same day 10 years before arrival.</p>
<h3>Visa requirements (FCDO)</h3>
<p>Each destination page quotes, word for word, the “Visa requirements” section of the same FCDO entry requirements page, with the page's last updated date and the date we checked it. We add a one-line summary (“In short”) only when the first sentence of that section matches one of a few fixed wordings, for example “You can visit X without a visa for up to 90 days” or “You must have a visa to visit X”, and contains no condition such as “usually”, “unless”, “until” or “if you”; for visa-free summaries the section must also not mention a travel authorisation (ETA, eTA, ESTA), an entry fee or a tourist card. On {data_lunga(PASS['controllato_il'])} this gave a summary for {sum(1 for P in PAESI if visto(P)["sintesi"])} destinations; the other {sum(1 for P in PAESI if not visto(P)["sintesi"])} show only the official text (or say that the FCDO page has no visa section).</p>
<p>Destinations where we do not apply the passport validity rule automatically ({len(manuali)}), because the official sentence has conditions we do not turn into a calculation:</p>
<ul>{lista_man}</ul>
{f'<p>No page published (the official section is empty):</p><ul>{senza}</ul>' if senza else ''}
{about_esteri(rel)}
{about_it(rel)}
<h2>Liquids rules</h2>
<p>Each airport's official security page, last read by us on {data_lunga(AER['controllato_il'])} (the date is shown on each page). Some airport sites block simple automated requests or load their text with JavaScript: we read those in a browser and say so on the page. Spanish airports use the general hand-luggage page of Aena, which runs Spain's public airports (it lists no airport- or lane-specific exceptions, and it does not say that it applies at every airport: each Spanish airport page says so); Hong Kong uses the Civil Aviation Department page; the US and Canada each have one national rule (TSA, CATSA). See the full list and the airports we left out on the <a href="{rel}liquids/">liquids page</a>.</p>
<h2>Cabin bag sizes</h2>
<p>Each airline's official baggage page, last read by us on {data_lunga(BAG['controllato_il'])} (the date and the link are on each airline page). Most airline sites need JavaScript or block simple automated requests, so we read them in a browser. Every size is quoted word for word; the short labels (“Free with every fare”, “Only with some fares, cabins or as a paid extra”) and the conversions marked “≈” are ours. An airline is included only if its official page shows the sizes; the airlines we left out and why are listed on the <a href="{rel}cabin-bags/">cabin bags page</a>. The bag checker compares the sides sorted from longest to shortest; airlines may measure differently, and their rule decides. The <a href="{rel}cabin-bags/eu-personal-item-rule/">EU personal item page</a> quotes Regulation (EU) 2026/2202 (EUR-Lex), the European Parliament's Legislative Observatory and the European Commission.</p>
{about_srv(rel)}
{about_pat(rel)}
<h2>EES and ETIAS</h2>
<p>European Commission (DG Migration and Home Affairs) pages and GOV.UK travel advice, last checked on {data_lunga(EES['controllato_il'])}. See the <a href="{rel}ees-etias/">EES and ETIAS page</a>.</p>
<h2>Corrections</h2>
<p>Spotted a change or a mistake? <a href="{rel}contact/?ref=about">Tell us</a>.</p></div>"""
    pagina("about/", f"About and sources | {NOME}", "Where our travel rules come from: official sources, check dates, licences and the destinations we leave out.",
           corpo, briciole=[("About and sources", "about/")])


def contatti():
    rel = "../"
    corpo = f"""<section class="hero"><h1>Contact</h1><p class="lead">Spotted a change in an official rule, a mistake, or an airport you would like us to add? Write to us here.</p></section>
<section class="card"><form class="form ajax" name="contact" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="contact"><input type="hidden" name="source" value="">
<p class="hp"><label>Do not fill this in <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Your email<input type="email" name="email" required autocomplete="email"></label>
<label>Country or airport (optional)<input type="text" name="topic" maxlength="200"></label>
<label>Message<textarea name="message" rows="6" required maxlength="4000"></textarea></label>
<label class="check"><input type="checkbox" name="consent" value="yes" required><span>I have read the <a href="{rel}privacy.html">privacy notice</a>.</span></label>
<button class="btn" type="submit">Send</button><p class="errore" data-errore hidden>Sorry, it did not work. Please try again.</p></form>
<div class="ok" data-ok hidden><strong>Thank you.</strong> We will check the official source and reply by email.</div></section>"""
    pagina("contact/", f"Contact | {NOME}", f"Contact {NOME}: report a change in an official travel rule or ask for an airport.", corpo,
           briciole=[("Contact", "contact/")])


def privacy():
    corpo = f"""<section class="hero"><h1>Privacy notice</h1><p class="small">Last updated: October 2026</p></section><div class="testo">
<h2>Who is responsible</h2><p>The data controller is Massimiliano Cori (Italy), who runs {NOME} as an independent project. You can contact us through the <a href="contact/">contact form</a>.</p>
<h2>What we collect</h2><p>Only what you type in the contact form: your email, the country or airport and your message. We also record the page or link you came from, to understand which pages need corrections. The passport checker runs in your browser: the dates you type are not sent to us.</p>
<h2>Why</h2><p>To answer your messages and correct the site. The legal basis is your consent (Art. 6(1)(a) GDPR), which you can withdraw at any time.</p>
<h2>Who processes data for us</h2><p>The site and its form are hosted by Netlify, Inc., which stores form data on our behalf and may process it outside the EU with the safeguards required by the GDPR (standard contractual clauses). We do not sell or share your data.</p>
<h2>Cookies and visit counter</h2><p>This site does not use profiling cookies. To count visits we use <a href="https://www.goatcounter.com/" rel="noopener">GoatCounter</a>, a privacy-friendly counter: it sets no cookies and stores nothing in your browser, builds no profiles and does not store your IP address, your full browser signature or any identifier. It keeps only aggregate numbers (page, hour or day, browser, country, screen width) on servers in the European Union and shares nothing with third parties; see <a href="https://www.goatcounter.com/help/privacy" rel="noopener">GoatCounter's privacy policy</a>. If we add advertising or affiliate links in the future, we will update this notice and ask for your consent where required before any advertising cookies are used.</p>
<h2>How long</h2><p>Messages are kept for up to 12 months after our last exchange.</p>
<h2>Your rights</h2><p>You can ask for access, correction, deletion, restriction, portability and objection (Articles 15–22 GDPR) and you can complain to the Italian data protection authority (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>) or the authority in your country.</p></div>"""
    pagina("privacy.html", f"Privacy | {NOME}", f"Privacy notice of {NOME}.", corpo)


def extra():
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n")
    (SITO / f"{CHIAVE_INDEXNOW}.txt").write_text(CHIAVE_INDEXNOW)  # file chiave IndexNow: non in sitemap, non linkato
    # lastmod: data vera dell'ultima lettura della fonte per le pagine "Available in?" (LASTMOD), data di oggi per le altre
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{LASTMOD.get(u, OGGI.isoformat())}</lastmod></url>" for u in URLS)
    (SITO / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n')
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Deploy only when something changed in beforeyoufly/sito.
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
           '<section class="hero"><h1>Page not found</h1><p class="lead">Go to the <a href="/">home page</a>, the <a href="/passport-validity/">passport validity rules</a> '
           'the <a href="/liquids/">liquids rules by airport</a>, the <a href="/cabin-bags/">cabin bag size by airline</a> <a href="/available-in/">apps and services by country</a> or <a href="/driving-abroad/">driving abroad with your licence</a>.</p></section>', indicizza=False, assoluto=True)


def copia_grafica():
    """Font (licenza OFL inclusa) e immagine Open Graph da grafica/ a sito/assets/."""
    (SITO / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (RADICE / "grafica" / "fonts").iterdir():
        shutil.copy(f, SITO / "assets" / "fonts" / f.name)
    shutil.copy(RADICE / "grafica" / "og.png", SITO / "assets" / "og.png")


def controlli():
    errori = []
    for P in PASS["paesi"]:
        for k in ("slug", "nome", "url", "aggiornata"):
            if not P.get(k):
                errori.append(f"passaporto {P.get('slug')}: manca {k}")
        if P["regola"] and not P["regola"].get("frase"):
            errori.append(f"passaporto {P['slug']}: regola senza frase ufficiale")
    if len(PAESI) < 200:
        errori.append(f"solo {len(PAESI)} paesi con testo ufficiale")
    for A in AER["aeroporti"] + AER["nazionali"]:
        for k in ("slug", "nome", "regola", "sintesi", "citazioni", "url", "titolo_fonte", "controllato_il"):
            if not A.get(k):
                errori.append(f"aeroporto {A.get('slug')}: manca {k}")
        if A.get("regola") not in ETICHETTE:
            errori.append(f"aeroporto {A.get('slug')}: regola sconosciuta {A.get('regola')}")
        if A.get("regola") == "contraddice" and not A.get("contrasto"):
            errori.append(f"aeroporto {A['slug']}: 'contraddice' senza la seconda fonte")
    slug = [A["slug"] for A in AER["aeroporti"] + AER["nazionali"]]
    if len(set(slug)) != len(slug):
        errori.append("slug aeroporti duplicati")
    for C in COMPAGNIE:
        for k in ("slug", "nome", "area", "fonti", "borse", "tariffe", "controllato_il"):
            if not C.get(k):
                errori.append(f"compagnia {C.get('slug')}: manca {k}")
        for b in C.get("borse", []):
            if b.get("incluso") not in INCLUSO or b.get("tipo") not in DOVE or len(b.get("cm") or []) != 3 or not b.get("cit"):
                errori.append(f"compagnia {C['slug']}: borsa {b.get('id')} incompleta")
            for c in b.get("cit", []):
                if c["f"] not in C["fonti"]:
                    errori.append(f"compagnia {C['slug']}: citazione con fonte sconosciuta {c['f']}")
        if not (borsa_gratis(C, "sotto") or borsa_gratis(C, "sopra")):
            errori.append(f"compagnia {C['slug']}: nessuna borsa compresa in ogni tariffa")
    if len({C["slug"] for C in COMPAGNIE}) != len(COMPAGNIE):
        errori.append("slug compagnie duplicati")
    if not frasi_ees("etias") or not frasi_ees("ees"):
        errori.append("EES/ETIAS: nessuna frase ufficiale trovata (rilanciare raccolta/eesetias.py)")
    if DOC_IT:
        for p in DOC_IT["paesi"]:
            if p["iso3"] not in NOMI_IT:
                errori.append(f"documenti_it {p['iso3']}: manca il nome italiano in dati/paesi_it.txt")
            for k in ("url", "aggiornata", "documento", "validita", "visto", "impronte"):
                if not p.get(k):
                    errori.append(f"documenti_it {p['iso3']}: manca {k}")
        sl = [v["slug"] for v in VOCI_IT + SENZA_PAGINA_IT]
        if len(set(sl)) != len(sl):
            errori.append("documenti_it: slug duplicati")
    for S in SERVIZI_SRV:
        for k in ("slug", "nome", "pagina", "url_fonte", "letto_il", "cambiato_il", "impronta", "paesi"):
            if not S.get(k):
                errori.append(f"servizio {S.get('slug')}: manca {k}")
        for c, v in S.get("paesi", {}).items():
            if c not in PAESI_ISO or v.get("stato") not in ("si", "no", "in_arrivo", "per_regione"):
                errori.append(f"servizio {S['slug']}: Paese {c} sconosciuto o stato {v.get('stato')}")
        if S.get("slug") not in SRV_TESTI:
            errori.append(f"servizio {S.get('slug')}: mancano i testi in SRV_TESTI")
    if PAT:
        for p in PAT["paesi"]:
            if p["iso2"] not in PAESI_ISO:
                errori.append(f"patenti {p['iso2']}: codice non in paesi_iso.json")
            for k in PATENTI:
                v = p[k]
                if v and (v["esito"] not in ESITI_PAT or not v.get("letto_il") and not (k == "uk" and v.get("tabella"))):
                    errori.append(f"patenti {p['iso2']} {k}: esito {v['esito']} o data di lettura mancante")
        for k in ("uk_paypoint", "uk_costo", "uk_durata", "uk_sempre_patente", "uk_tabella", "uk_non_in_tabella", "ca_caa", "ca_anno", "ca_classe", "au_aaa", "au_falsi"):
            if not PAT_G.get(k):
                errori.append(f"patenti: manca la frase generale {k}")
        if NOLEGGIO_AUTO:
            errori.append("patenti: NOLEGGIO_AUTO non è vuoto (riquadro noleggio non approvato)")
    if errori:
        raise SystemExit("ERRORI NEI DATI:\n" + "\n".join(errori))


def main():
    global PIEDE_ESTERI
    controlli()
    PIEDE_ESTERI = "".join((" Canadian passport pages: " if k == "ca" else " Australian passport pages: ") + licenza_estera(k) for k in ESTERI if VOCI[k])
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
    indice_passaporti()
    for P in PAESI:
        pagina_paese(P)
    for k in ESTERI:
        if VOCI[k]:
            indice_estero(k)
            for v in VOCI[k]:
                pagina_estera(v)
    indice_liquidi()
    for A in AER["aeroporti"]:
        pagina_aeroporto(A)
    for N in AER["nazionali"]:
        pagina_aeroporto(N, nazionale=True)
    pagina_ees()
    if COMPAGNIE:
        indice_bagagli()
        for C in COMPAGNIE:
            pagina_compagnia(C)
        for sl, m in MISURE_COMUNI:
            pagina_misura(sl, m)
        pagina_strumento()
        pagina_ue()
    if VOCI_IT:
        indice_it()
        for v in VOCI_IT:
            pagina_it(v)
    if SERVIZI_SRV:
        indice_srv()
        for S in SERVIZI_SRV:
            pagina_srv_servizio(S)
            for c in pagine_srv(S):
                pagina_srv_paese(S, c)
    if PAT:
        pagina_hub_pat()
        for k in PATENTI:
            pagina_patente(k)
            for c in PAGINE_PAT[k]:
                pagina_pat(k, c)
    about()
    contatti()
    privacy()
    extra()
    auto = sum(1 for P in PAESI if P["regola"])
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili + 404; {len(PAESI)} paesi ({auto} con controllo automatico), "
          f"{len(AER['aeroporti'])} aeroporti + {len(AER['nazionali'])} regole nazionali, pagina EES/ETIAS; "
          f"bagaglio a mano: {len(COMPAGNIE)} compagnie, {len(MISURE_COMUNI)} misure, strumento, pagina UE; "
          + ", ".join(f"passaporto {ESTERI[k]['agg']}: {len(VOCI[k])} pagine" for k in ESTERI)
          + f"; documenti per italiani: indice + {len(VOCI_IT)} pagine Paese ({len(SENZA_PAGINA_IT)} schede senza pagina)"
          + f"; available in: indice + {len(SERVIZI_SRV)} servizi + {sum(len(pagine_srv(S)) for S in SERVIZI_SRV)} pagine servizio × Paese"
          + (f"; driving abroad: indice + {len(PATENTI)} patenti + {sum(len(PAGINE_PAT[k]) for k in PATENTI)} pagine Paese × patente "
             f"({', '.join(f'{k} {len(PAGINE_PAT[k])}' for k in PATENTI)})" if PAT else ""))


if __name__ == "__main__":
    main()
