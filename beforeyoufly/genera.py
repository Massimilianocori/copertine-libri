"""Genera il sito statico Before You Fly in beforeyoufly/sito/ da beforeyoufly/dati/.

Uso (dalla radice del repository):
    python3 beforeyoufly/genera.py

Dati:
    dati/passaporti.json   regole di validità del passaporto e testo dei visti (passaporto britannico) per 226 pagine FCDO (raccolta/passaporti.py)
    dati/aeroporti.json    regole sui liquidi lette a mano sulle pagine ufficiali degli aeroporti (ricontrollo: raccolta/liquidi.py)
    dati/ees_etias.json    frasi ufficiali su EES ed ETIAS (raccolta/eesetias.py)
    dati/affiliati.json    riquadro affiliati (vuoto finché non ci sono URL)

Il controllo del passaporto gira nel browser (JS in pagina, nessuno script esterno). La stessa logica è scritta qui in Python
(verifica_passaporto) per gli esempi e per verifica.py, che confronta Python e JS su casi fatti a mano e casuali.
"""
import json
import re
import shutil
from datetime import date, timedelta
from html import escape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
URL_SITO = "https://before-you-fly.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti): non rimuoverlo

# Contatore visite GoatCounter, account condiviso "rete-siti" della rete (nessun cookie, nessun dato personale conservato).
# Il percorso inviato comprende l'host (location.host + percorso), così nel cruscotto https://rete-siti.goatcounter.com
# ogni sito si distingue dagli altri. Da localhost, da file:// e dalle reti private count.js non invia nulla
# (allow_local resta spento): le prove in locale non contano come visite. Unico punto da cambiare per tutto il sito.
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
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
nav.menu{display:flex;gap:4px;font-size:.92rem}
nav.menu a{display:flex;align-items:center;gap:7px;color:var(--on-board-2);text-decoration:none;padding:8px 12px;border-radius:8px;white-space:nowrap}
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
.tiles small{grid-column:1/-1;align-self:start;font-size:.86rem;color:var(--on-board-2);line-height:1.45;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
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
@media (max-width:640px){.tab td,.tab th{min-width:120px}.tab td:first-child,.tab th:first-child{min-width:150px}}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:10px}
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
details.card>summary{cursor:pointer;min-height:44px;padding:6px 0;line-height:1.45}
.faq h3{margin-top:18px}
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
@media (max-width:860px){.tiles{grid-template-columns:1fr}.tre{grid-template-columns:1fr}.calc .campi,.calc .campi:has([data-campo=emissione]:not([hidden])){grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:480px){.calc .campi,.calc .campi:has([data-campo=emissione]:not([hidden])){grid-template-columns:1fr}}
@media (max-width:760px){nav.menu{display:none}.nav-m{display:block}header.top .wrap{min-height:60px}footer .f-grid{grid-template-columns:1fr}.band-in{padding-top:24px;padding-bottom:26px}.checker-b{padding:16px}
.tiles{grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:20px}.tiles a{grid-template-columns:1fr;grid-template-rows:auto;justify-items:start;align-content:start;gap:8px;padding:12px;min-height:104px}.tiles .sq{width:40px;height:40px}.tiles .sq .ico{width:22px;height:22px}
.tiles h2{font-size:.95rem}.tiles small{display:none}.checker-h{letter-spacing:.06em;font-size:.74rem}.band-h2{margin-top:22px}}
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
    "globe": '<circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19"/><path d="M12 2.5c2.6 2.6 4 6 4 9.5s-1.4 6.9-4 9.5c-2.6-2.6-4-6-4-9.5s1.4-6.9 4-9.5z"/>',
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
def pagina(percorso, titolo, descrizione, corpo, briciole=None, indicizza=True, js="", assoluto=False, testata="", ld_extra=None):
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
    ld += ld_extra or []
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    robots = "" if indicizza else '<meta name="robots" content="noindex">'
    canonico = f'<link rel="canonical" href="{url_pag}">' if indicizza else ""
    script = f"<script>{js or FORM_JS}</script>"
    voci_menu = [("passport-validity/", "passport", "Passport validity"), ("liquids/", "bottle", "Liquids by airport"),
                 ("ees-etias/", "scan", "EES &amp; ETIAS"), ("about/", "book", "Sources")]
    menu = "".join(f'<a href="{rel}{u}"' + (' aria-current="page"' if u == percorso else "") + f'>{ico(i)}{t}</a>' for u, i, t in voci_menu)
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
<meta property="og:image:alt" content="{NOME}: passport validity, liquids rules by airport, EES and ETIAS">
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
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
<a class="logo" href="{rel}">{MARCHIO}<span>Before <b>You Fly</b></span></a>
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
<a class="logo" href="{rel}">{MARCHIO}<span>Before <b>You Fly</b></span></a>
<p><strong>{NOME}</strong> is an independent site, not affiliated with any government, airport or airline. Every rule is quoted from an official source, linked under it with the date we checked it.
<strong>Rules change: the airline, the airport and border officials have the final say.</strong> Nothing on this site is legal advice.</p>
<p>Passport validity rules: contains public sector information from the FCDO foreign travel advice on GOV.UK, licensed under the <a href="{OGL}" rel="noopener">Open Government Licence v3.0</a>.</p>
</div><div>
<h2>Explore</h2>
<ul><li><a href="{rel}about/">About and sources</a></li><li><a href="{rel}contact/">Contact</a></li><li><a href="{rel}privacy.html">Privacy</a></li><li><a href="{rel}contact/?ref=spotted-a-change">Spotted a change? Tell us</a></li></ul>
</div></div>
<p class="f-base">Official sources only, quoted word for word.</p>
</div></footer>
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
    voci = [v for k, v in AFFILIATI.items() if not k.startswith("_") and isinstance(v, dict) and v.get("url")]
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
# nome nel <title> come lo cerca la gente ("barcelona airport liquid rules"); nel testo resta il nome completo del file
NOMI_TITOLO = {"madeira": "Madeira Funchal", "barcelona": "Barcelona", "alicante": "Alicante", "malaga": "Malaga", "lanzarote": "Lanzarote", "doha": "Doha Hamad",
               "athens": "Athens", "dubai": "Dubai", "malta": "Malta"}
SIGLA_PAESE = {"United States": "US", "Canada": "Canadian"}


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


def titoli_liquidi(A, nazionale=False):
    if nazionale:
        x, e = SIGLA_PAESE.get(A["paese"], A["paese"]), sigla_ente(A)
        return [f"{x} Airport Liquid Rules {ANNO} ({e}): 100 ml or More?", f"{x} Airport Liquid Rules {ANNO} ({e})"]
    n, i = nome_titolo(A), A["iata"]
    return [f"{n} Airport ({i}) Liquid Rules {ANNO}: 100 ml or 2 litres?", f"{n} Airport ({i}) Liquid Rules {ANNO}: 100 ml or 2L?",
            f"{n} Airport ({i}) Liquid Rules {ANNO}", f"{n} ({i}) Liquid Rules {ANNO}"]


def descrizioni_liquidi(A, nazionale=False):
    d, r, sx, c = dove_liq(A, nazionale), risposta_liq(A), A["sintesi"], data_lunga(A["controllato_il"])
    return [f"Can you take liquids over 100 ml at {d}? {r}. {sx}. Quoted from the official page, checked {c}.",
            f"Can you take liquids over 100 ml at {d}? {r}. {sx}. Official page quoted.",
            f"Liquids over 100 ml at {d}? {r}. {sx}.",
            f"Can you take liquids over 100 ml at {d}? {r}. Official rules quoted word for word, checked {c}.",
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


FAQ_LIQ = [  # (chiave, domanda, filtro sulle frasi ufficiali): la frase deve parlare proprio di quello che chiede la domanda
    ("limite", "Can I take liquids over 100 ml through security at {d}?", re.compile(r"100|litre|liter|2,000|3\.4|\bml\b", re.I)),
    ("busta", "Do liquids have to go in a plastic bag at {d}?",
     re.compile(r"plastic bag|re-?sealable|clear bag|transparent bag|lit(?:re|er) bag|liquid bag|quart-sized bag|20 ?cm ?x ?20|20 x 20|1L in capacity", re.I)),
    ("fuori", "Do I have to take liquids out of my bag at security at {d}?",
     re.compile(r"remov|take them out|stay in|remain in|separately|separate from|tray|leave (?:your )?liquids|kept in your", re.I)),
    ("terminal", "Are the liquids rules different by terminal or checkpoint at {d}?",
     re.compile(r"\bterminals?\b|\bgates?\b|security areas?|control areas?|transfer|\blanes?\b|signs|CT technology|CT scanners?|computed tomography"
                r"|which security checkpoint|some security checkpoints|following checkpoints|entrance security|one stop security", re.I)),
    ("borraccia", "Can I take a reusable bottle or flask through security at {d}?", re.compile(r"bottle|flask|thermos|double-walled|insulated", re.I)),
]


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
    """Fino a 4 domande vere. Ogni risposta è fatta SOLO di citazioni ufficiali intere (mai tagliate, mai testo nostro):
    la stessa citazione può rispondere a due domande diverse. verifica.py lo controlla."""
    pool = frasi_ufficiali_liq(A)
    gruppi = gruppi_liq(A, list(A["citazioni"])) + gruppi_liq(A, [f for f in pool if f not in A["citazioni"]])
    out = []
    for i, (chiave, dom, rx) in enumerate(FAQ_LIQ):
        if chiave in A.get("faq_salta", []):  # domanda che non si adatta a questa pagina (es. Zurigo: dipende dal viaggio, non dal varco)
            continue
        if i == 0:  # prima domanda: le citazioni principali (più eccezioni e contrasti dove la regola dipende dal varco)
            ff = list(pool) if A["regola"] in ("dipende", "contraddice") else list(A["citazioni"])
        else:
            ff = [f for g in gruppi if any(rx.search(x) and not re.search(r"tamper|duty", x, re.I) for x in g) for f in g]
        if not ff or any(ff == g and len(g) > 1 for _, g in out):  # niente blocchi lunghi ripetuti identici
            continue
        out.append((dom.format(d=dove_liq(A, nazionale)), ff))
    return out[:4]


def html_faq(A, faq):
    if not faq:
        return "", []
    h = "".join(f"<h3>{escape(q)}</h3>{cit_html(ff)}" for q, ff in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": prefisso_faq(A) + " ".join(f"“{f}”" for f in ff)}} for q, ff in faq]}
    return (f'<section class="faq"><h2>Questions about liquids at {escape(A["nome"])}</h2>'
            f'<p class="small">Every answer below is quoted word for word from the official page, not written by us.</p>{h}{fonte_liq(A)}</section>'), [ld]


def pagina_aeroporto(A, nazionale=False):
    rel = "../../"
    titolo_breve = A["nome"]
    if nazionale:
        h1 = f"{A['paese']} airports liquids rules {ANNO}: 100 ml or more? ({sigla_ente(A)})"
    else:
        h1 = f"{A['nome'] if A['slug'] != 'madeira' else 'Madeira Funchal'} Airport ({A['iata']}) liquid rules {ANNO}: 100 ml or 2 litres?"
    eccezioni = ("<h2>Exceptions and other details (official)</h2>" + cit_html(A["eccezioni"])) if A.get("eccezioni") else ""
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
    link_simili = ""
    if simili:
        link_simili = (f"<h2>Other airports in {escape(A['paese'])}</h2><div class=\"griglia\">" +
                       "".join(f'<a href="{rel}liquids/{B["slug"]}/">{escape(B["nome"])} ({B["iata"]})<small>{escape(etichetta(B))}</small></a>' for B in simili) + "</div>")
    faq_html, faq_ld = html_faq(A, faq_liquidi(A, nazionale))
    corpo = f"""<section class="hero"><h1>{escape(h1)}</h1></section>
<section class="card summary" aria-label="Summary">
<div class="s-top"><span class="sq">{ico("bottle")}</span><span>Liquids · hand luggage</span><span>{escape(A.get("iata") or A.get("paese") or "")}</span></div>
<div class="s-body">
<p class="cifra">Can I take liquids over 100 ml through security at {escape(dove_liq(A, nazionale))}? <strong>{escape(frase_risposta(A))} {badge(A['regola'], A)}</strong></p>
<p class="lead">Short answer based on the official page quoted below{", which is Aena's general hand-luggage page, not a page for this airport" if A.get('gestore') == 'aena' else ''}.</p>
{fonte_liq(A)}
</div>
</section>
{AVVISO_LIQ}
<h2>What the official page says</h2>
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
    ultimo = data_lunga(max(PASS["controllato_il"], AER["controllato_il"], EES["controllato_il"]))
    testata = f"""<div class="band"><div class="wrap band-in">
<section class="hero">{h1_diviso(f"Before You Fly: passport validity, airport liquids rules and EU entry checks ({ANNO})")}
<p class="scope"><span class="pill">{ico("passport")}British passport only</span><span>Passport rules are the UK government's (FCDO), for British citizens.</span></p>
<p class="sub">Three checks before you fly, answered from official sources only.</p>
<p class="trust"><span>{ico("shield")}Official sources · last checked {ultimo}</span><span>{ico("lock")}Your dates stay in your browser</span></p></section>
<ul class="tiles">
<li><a href="passport-validity/"><span class="sq">{ico("passport")}</span><h2>Passport validity</h2><small>FCDO passport validity and visa rules for British passports, {len(PAESI)} destinations, a date checker for {auto} of them. Last checked: {data_lunga(PASS['controllato_il'])}.</small></a></li>
<li><a href="liquids/"><span class="sq">{ico("bottle")}</span><h2>Liquids by airport</h2><small>100 ml or 2 litres? {len(AER['aeroporti'])} airports plus the US and Canada rules, from official pages.</small></a></li>
<li><a href="ees-etias/"><span class="sq">{ico("scan")}</span><h2>EES &amp; ETIAS</h2><small>EES is fully operational; ETIAS is {stato_etias} (European Commission).</small></a></li>
</ul>
<h2 class="band-h2">Check your passport dates</h2>
{modulo_checker('tutti-dati', True, link='passport-validity/')}
</div></div>"""
    corpo = f"""<p class="lead" style="margin-top:28px">Three things to check before you fly, answered from official sources only: is your passport valid long enough for your destination, can you take more than 100 ml of liquids through security, and what EES and ETIAS mean for your trip. Every rule is quoted word for word with its source and the date we checked it.</p>
{AVVISO_PASS}
{AD}
<h2>Popular destinations</h2>
{nota_sch}<div class="griglia">{griglia_pass}</div>
<p><a href="passport-validity/">All {len(PAESI)} destinations</a></p>
<h2>Airports that allow up to 2 litres (official pages)</h2>
<div class="griglia">{griglia_2l}</div>
<p><a href="liquids/">All airports, including those that depend on the checkpoint</a></p>
{box_affiliati()}
{dati_json('tutti-dati', [dati_client(P) for P in PAESI])}"""
    pagina("", f"Before You Fly {ANNO}: Passport Validity, Visas, Liquids, EES",
           f"Passport validity and visa rules (FCDO) for {len(PAESI)} destinations, liquid limits at {len(AER['aeroporti'])} airports and EES/ETIAS status, quoted from official sources.",
           corpo, js=MOTORE_JS + APP_JS, testata=testata)


def about():
    rel = "../"
    manuali = [P for P in PAESI if not P["regola"]]
    lista_man = "".join(f'<li><a href="{rel}passport-validity/{P["slug"]}/">{escape(P["nome"])}</a>: {escape(P["motivo"])}</li>' for P in manuali)
    senza = "".join(f"<li>{escape(P['nome'])}: {escape(P['motivo'])}</li>" for P in SENZA_PAGINA)
    corpo = f"""<section class="hero"><h1>About {NOME} and our sources</h1></section><div class="testo">
<p>{NOME} is an independent project. It collects official travel rules and shows them word for word, with the link and the date we checked them. We are not affiliated with any government, airport or airline.</p>
<h2>Rules we follow</h2>
<ul><li>Only official sources: the UK government (GOV.UK, FCDO), the European Commission and EU portals, airport operators, and national aviation security authorities (TSA, CATSA, Hong Kong Civil Aviation Department).</li>
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
<h2>Liquids rules</h2>
<p>Each airport's official security page, last read by us on {data_lunga(AER['controllato_il'])} (the date is shown on each page). Some airport sites block simple automated requests or load their text with JavaScript: we read those in a browser and say so on the page. Spanish airports use the general hand-luggage page of Aena, which runs Spain's public airports (it lists no airport- or lane-specific exceptions, and it does not say that it applies at every airport: each Spanish airport page says so); Hong Kong uses the Civil Aviation Department page; the US and Canada each have one national rule (TSA, CATSA). See the full list and the airports we left out on the <a href="{rel}liquids/">liquids page</a>.</p>
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
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{OGGI.isoformat()}</lastmod></url>" for u in URLS)
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
           'or the <a href="/liquids/">liquids rules by airport</a>.</p></section>', indicizza=False, assoluto=True)


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
    if not frasi_ees("etias") or not frasi_ees("ees"):
        errori.append("EES/ETIAS: nessuna frase ufficiale trovata (rilanciare raccolta/eesetias.py)")
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
    indice_passaporti()
    for P in PAESI:
        pagina_paese(P)
    indice_liquidi()
    for A in AER["aeroporti"]:
        pagina_aeroporto(A)
    for N in AER["nazionali"]:
        pagina_aeroporto(N, nazionale=True)
    pagina_ees()
    about()
    contatti()
    privacy()
    extra()
    auto = sum(1 for P in PAESI if P["regola"])
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili + 404; {len(PAESI)} paesi ({auto} con controllo automatico), "
          f"{len(AER['aeroporti'])} aeroporti + {len(AER['nazionali'])} regole nazionali, pagina EES/ETIAS.")


if __name__ == "__main__":
    main()
