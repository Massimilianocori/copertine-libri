"""Genera il sito statico Before You Fly in beforeyoufly/sito/ da beforeyoufly/dati/.

Uso (dalla radice del repository):
    python3 beforeyoufly/genera.py

Dati:
    dati/passaporti.json   regole di validità del passaporto (passaporto britannico) per 226 pagine FCDO (raccolta/passaporti.py)
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
      if(o.scade_prima)h='<div class="esito no"><strong>Your passport expires before you leave: it will not be valid for your whole stay.</strong></div><ul>';
      else h='<div class="esito '+(o.esito==='ok'?'si':'no')+'"><strong>'+(o.esito==='ok'?'Your dates meet '+nome:'Your dates do NOT meet '+nome)+'</strong></div><ul>';
      if(o.scade_prima)h+='<li>✗ Your passport expires on <strong>'+lunga(q('scadenza').value)+'</strong>, before the day you leave ('+lunga(q('partenza').value)+').</li>';
      o.controlli.forEach(function(c){
        if(c.tipo==='scadenza')h+='<li>'+(c.ok?'✓ ':'✗ ')+'Expiry date needed: on or after <strong>'+lunga(c.minima)+'</strong> ('+(c.base==='arrivo'?'counted from the day you arrive':'counted from the day you leave')+'). '+
          (c.ok?pl(c.margine,'day')+' to spare.':'Yours is '+pl(-c.margine,'day')+' short.')+'</li>';
        else h+='<li>'+(c.ok?'✓ ':'✗ ')+'Date of issue needed: on or after <strong>'+lunga(c.minima)+'</strong> ('+esc(R.emissione_testo||'')+'). '+(c.ok?'':'Yours is '+pl(-c.margine,'day')+' too early.')+'</li>';});
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
:root{--bg:#F4F6F8;--card:#FFFFFF;--ink:#13202B;--ink-2:#43525F;--ink-3:#63727F;--line:#D9E1E8;
--accent:#0E6E7A;--accent-2:#E3F2F3;--ok:#1E6B47;--ok-2:#E6F2EB;--no:#A12D2D;--no-2:#FBE9E9;--warn:#8A4B00;--warn-2:#FFF2DF;--mute:#ECF0F4;--radius:14px}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0E1519;--card:#162127;--ink:#ECF2F5;--ink-2:#B6C5CE;
--ink-3:#8A9AA5;--line:#263640;--accent:#6FD0DB;--accent-2:#14303A;--ok:#7FD3A6;--ok-2:#173226;--no:#FF9C9C;--no-2:#3A1C1C;--warn:#FFB867;--warn-2:#33250F;--mute:#1C2A32}}
:root[data-theme="dark"]{--bg:#0E1519;--card:#162127;--ink:#ECF2F5;--ink-2:#B6C5CE;--ink-3:#8A9AA5;--line:#263640;--accent:#6FD0DB;
--accent-2:#14303A;--ok:#7FD3A6;--ok-2:#173226;--no:#FF9C9C;--no-2:#3A1C1C;--warn:#FFB867;--warn-2:#33250F;--mute:#1C2A32}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;font-size:17px;line-height:1.6;overflow-wrap:break-word}
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
.lead{font-size:1.07rem;color:var(--ink-2);max-width:760px;margin:0 0 6px}
.small{font-size:.88rem;color:var(--ink-3)}
.avviso{background:var(--warn-2);border-left:4px solid var(--warn);padding:11px 14px;border-radius:8px;font-size:.94rem;margin:16px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px;min-width:0}
.cifra{font-size:1.05rem;margin:12px 0}
.cifra strong{font-size:1.35rem;color:var(--accent)}
.badge{display:inline-block;font-weight:800;border-radius:999px;padding:2px 12px;font-size:.92rem;white-space:nowrap}
.b-2l{background:var(--ok-2);color:var(--ok)}.b-100ml{background:var(--mute);color:var(--ink)}.b-dipende,.b-contraddice{background:var(--warn-2);color:var(--warn)}
.fonte{font-size:.85rem;color:var(--ink-3);margin:6px 0 0;overflow-wrap:anywhere}
.fonte a{color:var(--ink-3)}
blockquote.cit{margin:10px 0;padding:10px 14px;border-left:4px solid var(--accent);background:var(--card);border-radius:0 10px 10px 0;font-size:.97rem}
blockquote.cit p{margin:0 0 8px}blockquote.cit p:last-child{margin:0}
blockquote.cit ul{margin:0 0 8px;padding-left:20px}
.calc{display:grid;gap:12px}
.calc .campi{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.calc label{display:grid;gap:4px;font-weight:600;font-size:.93rem;min-width:0}
.calc input,.calc select{font:inherit;padding:9px 11px;border:1px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink);width:100%;min-width:0}
.calc .pieno{grid-column:1/-1}
.risultato{background:var(--accent-2);border-radius:12px;padding:14px 16px;min-width:0;overflow-wrap:anywhere}
.risultato ul{margin:8px 0 0;padding-left:20px;font-size:.93rem}
.esito{border-radius:10px;padding:8px 12px}
.esito.si{background:var(--ok-2);color:var(--ok)}.esito.no{background:var(--no-2);color:var(--no)}.esito.manuale{background:var(--warn-2);color:var(--warn)}
.tab{overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid var(--line);border-radius:12px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-size:.93rem}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:var(--mute);font-size:.85rem}
tr:last-child td{border-bottom:0}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:8px}
.griglia a{display:block;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px;text-decoration:none;color:var(--ink);font-weight:600;min-width:0;overflow-wrap:anywhere}
.griglia a small{display:block;font-weight:400;color:var(--ink-3)}
.griglia a:hover{border-color:var(--accent)}
.tre{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.tre .card h2{margin-top:0;font-size:1.12rem}
.cerca{font:inherit;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink);width:100%;margin:6px 0 12px}
.testo p,.testo li{max-width:760px}
.form{display:grid;gap:12px}
.form label{display:grid;gap:4px;font-weight:600;font-size:.95rem}
.form input,.form select,.form textarea{font:inherit;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink);width:100%}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:400;font-size:.9rem;color:var(--ink-2)}
.form .check input{width:auto;margin-top:4px}
.btn{font:inherit;font-weight:700;background:var(--accent);color:#fff;border:0;border-radius:10px;padding:12px 18px;cursor:pointer}
:root[data-theme="dark"] .btn{color:#0E1519}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .btn{color:#0E1519}}
.btn:disabled{opacity:.6;cursor:wait}
.hp{position:absolute;left:-9999px}
.ok{background:var(--ok-2);border:1px solid var(--ok);padding:14px;border-radius:10px}
.errore{color:var(--warn);font-weight:600}
.ad-slot:empty{display:none}
.briciole{font-size:.85rem;color:var(--ink-3);margin-top:14px}
.briciole a{color:var(--ink-3)}
footer{margin-top:50px;border-top:1px solid var(--line);padding:22px 0 40px;font-size:.88rem;color:var(--ink-3)}
footer a{color:var(--ink-3)}
@media (max-width:760px){.calc .campi,.tre{grid-template-columns:1fr}
header.top .wrap{flex-direction:column;align-items:flex-start;gap:4px;padding-top:10px;padding-bottom:10px}nav.menu{gap:12px;font-size:.92rem}}
"""

AD = '<div class="ad-slot" aria-hidden="true"></div>'
AVVISO_PASS = ('<p class="avviso"><strong>For British passport holders only.</strong> These are the rules published by the UK government (FCDO) for British '
               'citizens. If you hold another passport, check your own government\'s advice. The airline and the border officials of the destination '
               'decide whether you can travel or enter: this site is information, not legal advice.</p>')
AVVISO_LIQ = ('<p class="avviso"><strong>Rules can differ by terminal, checkpoint or lane and can change at short notice.</strong> We quote the airport\'s '
              'official page on the date shown. Check with the airport (and your airline) before you pack, and check the airport you fly home from: '
              'it may still have the 100 ml limit.</p>')


# ---------------------------------------------------------------- impaginazione
def pagina(percorso, titolo, descrizione, corpo, briciole=None, indicizza=True, js="", assoluto=False):
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
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    robots = "" if indicizza else '<meta name="robots" content="noindex">'
    canonico = f'<link rel="canonical" href="{url_pag}">' if indicizza else ""
    script = f"<script>{js or FORM_JS}</script>"
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
<meta name="theme-color" content="#0E6E7A">
{robots}
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230E6E7A'/%3E%3Cpath d='M14 36 L50 22 L46 30 L30 36 L46 42 L50 50 Z' fill='white'/%3E%3C/svg%3E">
<style>{CSS}</style>
{ld_html}
</head>
<body>
<header class="top"><div class="wrap">
<a class="logo" href="{rel}">Before <span>You Fly</span></a>
<nav class="menu" aria-label="Menu">
<a href="{rel}passport-validity/">Passport validity</a><a href="{rel}liquids/">Liquids by airport</a><a href="{rel}ees-etias/">EES &amp; ETIAS</a><a href="{rel}about/">Sources</a>
</nav>
</div></header>
<main class="wrap">
{bc}
{corpo}
</main>
<footer><div class="wrap">
<p><strong>{NOME}</strong> is an independent site, not affiliated with any government, airport or airline. Every rule is quoted from an official source, linked under it with the date we checked it.
<strong>Rules change: the airline, the airport and border officials have the final say.</strong> Nothing on this site is legal advice.</p>
<p>Passport validity rules: contains public sector information from the FCDO foreign travel advice on GOV.UK, licensed under the <a href="{OGL}" rel="noopener">Open Government Licence v3.0</a>.</p>
<p><a href="{rel}about/">About and sources</a> · <a href="{rel}contact/">Contact</a> · <a href="{rel}privacy.html">Privacy</a> · <a href="{rel}contact/?ref=spotted-a-change">Spotted a change? Tell us</a></p>
</div></footer>
{script}
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
        return "Read the official text"
    parti = []
    for c in R["condizioni"]:
        if c["n"] == 0:
            parti.append("Length of stay" if c["op"] == ">=" else "Beyond departure")
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
    sel = '<label class="pieno">Destination<select name="paese"></select></label>' if con_paese else ""
    return f"""<div class="card" data-checker data-dati="{id_dati}" data-link="{escape(link)}">
<form class="calc" autocomplete="off">
<div class="campi">
{sel}
<label>Passport expiry date<input type="date" name="scadenza"></label>
<label data-campo="emissione" hidden>Passport date of issue<input type="date" name="emissione"></label>
<label><span data-lab="arrivo">Date you arrive</span><input type="date" name="arrivo"></label>
<label><span data-lab="partenza">Date you leave</span><input type="date" name="partenza"></label>
</div>
</form>
<p class="small" data-nota-schengen hidden style="margin:10px 0 0">Schengen rules count your whole trip in the Schengen area: if you visit several Schengen countries, enter the day you first enter the area and the day you leave the last Schengen country.</p>
<div class="risultato" data-out aria-live="polite" style="margin-top:12px"><noscript>Turn on JavaScript to use the checker. The official rule is quoted on this page.</noscript></div>
<p class="small" style="margin:10px 0 0">The check runs in your browser: your dates are not sent anywhere. It applies the FCDO sentence literally (for example “6 months” is counted as the same day of the month 6 months later).</p>
</div>"""


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
        cifra = f'<p class="cifra">{tipo} for {escape(P["nome"])}: <strong>{escape(sintesi_regola(R))}</strong></p>'
        if R.get("consiglio"):
            cifra += '<p class="small">The FCDO words this as advice (“should” or “make sure”), not as a strict requirement: the full sentence is quoted below.</p>'
        lead = (f"How long your British passport must be valid to enter {escape(P['nome'])}, as published by the UK Foreign, Commonwealth &amp; Development Office (FCDO), "
                "quoted word for word, with a checker for your dates.")
    else:
        cifra = (f'<p class="cifra"><strong>Read the official text below.</strong> {escape(P["motivo"] or "")} '
                 'We quote it word for word and do not summarise it.</p>')
        lead = (f"What the UK Foreign, Commonwealth &amp; Development Office (FCDO) says about passport validity for British travellers to {escape(P['nome'])}, "
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
    simili = [Q for Q in PAESI if Q is not P and breve_regola(Q["regola"], Q) == breve_regola(R, P)][:12] if R else []
    link_simili = ""
    if simili:
        link_simili = (f"<h2>Same FCDO rule ({escape(breve_regola(R, P))})</h2><div class=\"griglia\">" +
                       "".join(f'<a href="{rel}passport-validity/{Q["slug"]}/">{escape(Q["nome"])}</a>' for Q in simili) + "</div>")
    titolo_sez = P["titolo_sezione"] or "Passport validity requirements"
    if R:
        checker = f"<h2>Check your passport for {escape(P['nome'])}</h2>" + modulo_checker("paese-dati", False)
    else:
        checker = ('<p class="avviso"><strong>No automatic check for this destination.</strong> The official text above is not a validity period '
                   'we turn into a date calculation. Read it, and check with your airline or carrier.</p>')
    corpo = f"""<section class="hero"><h1>{escape(P['nome'])} passport validity rules for UK travellers ({ANNO})</h1>
<p class="lead">{lead}</p>
{cifra}
{fonte_pass(P)}
</section>
<h2>Official text: “{escape(titolo_sez)}”</h2>
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
    descr = (f"{P['nome']} passport validity for British passport holders ({ANNO}): {sint}. Official FCDO text quoted, with the page's last updated date"
             + (" and a date checker." if R else "."))
    pagina(f"passport-validity/{P['slug']}/", f"{P['nome']} passport validity rules for UK travellers ({ANNO})", descr, corpo,
           briciole=[("Passport validity", "passport-validity/"), (P["nome"], f"passport-validity/{P['slug']}/")], js=MOTORE_JS + APP_JS)


def cambi_recenti(giorni_max=60):
    lim = (date.fromisoformat(PASS["controllato_il"]) - timedelta(days=giorni_max)).isoformat()
    voci = [(c["data"], P, c["nota"]) for P in PAESI for c in P["cambi_ingresso"] if c["data"] >= lim]
    voci.sort(key=lambda x: (x[0], x[1]["nome"]), reverse=True)
    return voci


def indice_passaporti():
    rel = "../"
    righe = "".join(f'<tr data-voce><td><a href="{rel}passport-validity/{P["slug"]}/">{escape(P["nome"])}</a></td><td>{escape(breve_regola(P["regola"], P))}</td>'
                    f'<td>{data_lunga(P["aggiornata"])}</td></tr>' for P in PAESI)
    auto = sum(1 for P in PAESI if P["regola"])
    cambi = cambi_recenti()
    lista_cambi = "".join(f'<li>{data_lunga(d)} – <a href="{rel}passport-validity/{P["slug"]}/">{escape(P["nome"])}</a>: “{escape(n)}”</li>' for d, P, n in cambi[:40])
    rilevati = CAMBI_PASS["cambi"][:20]
    lista_rilevati = ""
    if rilevati:
        lista_rilevati = ("<h2>Passport validity text changes we detected</h2><ul>" +
                          "".join(f'<li>{data_lunga(c["rilevato_il"])} – <a href="{rel}passport-validity/{c["slug"]}/">{escape(c["nome"])}</a></li>' for c in rilevati) + "</ul>")
    corpo = f"""<section class="hero"><h1>Passport validity rules for UK travellers ({ANNO}): every destination</h1>
<p class="lead">How long a British passport must be valid for {len(PAESI)} destinations, from the UK government's foreign travel advice (FCDO), quoted word for word. For {auto} destinations the checker applies the rule to your dates; for the other {len(PAESI) - auto} the official sentence has conditions we do not turn into a calculation, so we show it and you read it.</p>
<p class="fonte">Source: <a href="https://www.gov.uk/foreign-travel-advice" rel="noopener">GOV.UK foreign travel advice (FCDO)</a>, read through the GOV.UK Content API · last checked: {data_lunga(PASS['controllato_il'])}.</p>
</section>
{modulo_checker('tutti-dati', True, link=rel + 'passport-validity/')}
{AVVISO_PASS}
{AD}
<h2>All destinations</h2>
<input class="cerca" type="search" placeholder="Type a country, e.g. Spain, Turkey, USA" data-filtro="lista-paesi" aria-label="Search destinations">
<div class="tab"><table><thead><tr><th>Destination</th><th>FCDO rule (short)</th><th>FCDO page last updated</th></tr></thead><tbody id="lista-paesi">{righe}</tbody></table></div>
<p class="small">“Length of stay”: valid until the day you leave. “10-year issue rule”: the passport must have been issued less than 10 years before you arrive. Always read the full official sentence on each page.</p>
<h2>Entry requirements updated by the FCDO in the last 60 days</h2>
<p class="small">From the change notes the FCDO publishes on each travel advice page (only notes that mention the entry requirements page).</p>
<ul>{lista_cambi or '<li>None.</li>'}</ul>
{lista_rilevati}
<h2>The Schengen 10-year issue rule</h2>
<p>For the Schengen area the FCDO says your passport must have a ‘date of issue’ less than 10 years before the date you arrive, and an ‘expiry date’ at least 3 months after the day you plan to leave. In the FCDO's words, “if you renewed your passport before 1 October 2018, it might have a date of issue that is more than 10 years ago, making it invalid for entry to the Schengen area”. The checker asks for the issue date only for destinations with this rule.</p>
{box_affiliati()}
{dati_json('tutti-dati', [dati_client(P) for P in PAESI])}"""
    pagina("passport-validity/", f"Passport validity rules by country for UK travellers ({ANNO}): checker for {len(PAESI)} destinations",
           f"How many months must a British passport be valid? Official FCDO rules for {len(PAESI)} destinations, quoted word for word, with a date checker and recent changes.",
           corpo, briciole=[("Passport validity", "passport-validity/")], js=MOTORE_JS + APP_JS)


# ---------------------------------------------------------------- liquidi
ETICHETTE = {"2l": "Up to 2 litres", "100ml": "100 ml", "dipende": "Depends on checkpoint", "contraddice": "Official pages disagree"}
RISPOSTA = {"2l": "2 litres", "100ml": "100 ml", "dipende": "It depends on the checkpoint", "contraddice": "Official pages disagree – plan for 100 ml"}


def badge(regola):
    return f'<span class="badge b-{regola}">{ETICHETTE[regola]}</span>'


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


def pagina_aeroporto(A, nazionale=False):
    rel = "../../"
    titolo_breve = A["nome"]
    if nazionale:
        h1 = f"{A['paese']} airports liquids rules {ANNO}: 100 ml or more? ({A['ente'].split('(')[-1].rstrip(')')})"
    else:
        h1 = f"{A['nome']} liquids rules {ANNO}: 100 ml or 2 litres?"
    eccezioni = ("<h2>Exceptions and lane-specific rules (official)</h2>" + cit_html(A["eccezioni"])) if A.get("eccezioni") else ""
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
                       "".join(f'<a href="{rel}liquids/{B["slug"]}/">{escape(B["nome"])}<small>{ETICHETTE[B["regola"]]}</small></a>' for B in simili) + "</div>")
    corpo = f"""<section class="hero"><h1>{escape(h1)}</h1>
<p class="cifra">Answer: <strong>{escape(RISPOSTA[A['regola']])}</strong> {badge(A['regola'])}</p>
<p class="lead">{escape(A['sintesi'])}.</p>
{fonte_liq(A)}
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
<h2>Flying back?</h2>
<p>The UK government's advice is to check the rules “at the airport you’re flying from” and “at any other airports you’ll be travelling through, including your return journey” (<a href="https://www.gov.uk/hand-luggage-restrictions/liquids" rel="noopener">GOV.UK, hand luggage restrictions</a>). See the <a href="{rel}liquids/">liquids rules at {len(AER['aeroporti'])} airports</a>{'' if nazionale else f', the <a href="{rel}liquids/us-airports-tsa/">US (TSA) rule</a> and the <a href="{rel}liquids/canada-airports-catsa/">Canada (CATSA) rule</a>'}.</p>
<h2>Medicines, baby food and duty-free</h2>
<p>Exemptions are set out on the official page linked above. For UK airports, GOV.UK lists them on its <a href="https://www.gov.uk/hand-luggage-restrictions/liquids" rel="noopener">hand luggage restrictions page</a>; for EU airports, see <a href="https://europa.eu/youreurope/citizens/travel/carry/luggage-restrictions/index_en.htm" rel="noopener">Your Europe</a>.</p>
<p class="small">Spotted a change? <a href="{rel}contact/?ref=liq-{A['slug']}">Tell us</a>.</p>
{box_affiliati()}
{link_simili}
<p><a href="{rel}liquids/">All airports</a> · <a href="{rel}passport-validity/">Passport validity rules</a> · <a href="{rel}ees-etias/">EES and ETIAS status</a></p>"""
    descr = (f"{titolo_breve} liquids rule {ANNO}: {RISPOSTA[A['regola']].lower()}. {A['sintesi']}. Quoted from the official page, with the date we checked it.")
    pagina(f"liquids/{A['slug']}/", h1, descr, corpo, briciole=[("Liquids by airport", "liquids/"), (titolo_breve, f"liquids/{A['slug']}/")])


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
                        f'<td>{badge(A["regola"])}</td><td>{escape(A["sintesi"])}</td><td><a href="{escape(A["url"])}" rel="noopener">official</a>, {data_lunga(A["controllato_il"])}</td></tr>'
                        for A in sorted(gruppi[area], key=lambda x: x["nome"]))
        tabelle.append(f'<h2>{escape(area)}</h2><div class="tab"><table><thead><tr><th>Airport</th><th>Country</th><th>Limit per container</th><th>Details</th><th>Source</th></tr></thead><tbody>{righe}</tbody></table></div>')
    naz = "".join(f'<tr><td><a href="{rel}liquids/{N["slug"]}/">{escape(N["nome"])}</a></td><td>{badge(N["regola"])}</td><td>{escape(N["sintesi"])}</td>'
                  f'<td><a href="{escape(N["url"])}" rel="noopener">official</a>, {data_lunga(N["controllato_il"])}</td></tr>' for N in AER["nazionali"])
    esclusi = "".join(f"<li><strong>{escape(E['nome'])}</strong>: {escape(E['motivo'])}</li>" for E in AER["esclusi"])
    corpo = f"""<section class="hero"><h1>Liquids rules by airport {ANNO}: 100 ml or 2 litres?</h1>
<p class="lead">Some airports with new CT scanners now let you carry liquids in containers of up to 2 litres; many still apply the 100 ml limit, and some only at certain checkpoints. Here is what each airport's official page says, quoted word for word, with the date we checked it.</p>
<p class="cifra">Of the {len(AER['aeroporti'])} airports below: <strong>{conta['2l']}</strong> up to 2 litres · <strong>{conta['100ml']}</strong> 100 ml · <strong>{conta['dipende']}</strong> depends on the checkpoint · <strong>{conta['contraddice']}</strong> with official pages that disagree.</p>
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
    pagina("liquids/", f"Liquids rules by airport {ANNO}: 100 ml or 2 litres? ({len(AER['aeroporti'])} airports, official sources)",
           f"Which airports allow 2 litres of liquids? Official rules for {len(AER['aeroporti'])} airports (Heathrow, Gatwick, Dublin, Manchester, Frankfurt, Rome, Madrid…) plus the US TSA and Canada rules, quoted with dates.",
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
<section class="card"><h2>EES</h2><p class="cifra"><strong>{escape(stato_ees)}</strong></p><p class="small" style="margin:0">Registration of fingerprints and a facial image at the Schengen border for short stays.</p></section>
<section class="card"><h2>ETIAS</h2><p class="cifra"><strong>{escape(stato_etias)}</strong></p><p class="small" style="margin:0">Start date: the EU says it will announce it several months before launch.</p></section>
<section class="card"><h2>Your passport</h2><p class="small" style="margin:0">Schengen rules for British passports: <a href="{rel}passport-validity/france/">10-year issue rule and 3 months after you leave</a>.</p></section>
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
    griglia_pass = "".join(f'<a href="passport-validity/{s}/">{escape(mappa[s]["nome"])}<small>{escape(breve_regola(mappa[s]["regola"], mappa[s]))}</small></a>'
                           for s in popolari if s in mappa)
    stato_etias = "not in operation" if any("currently not in operation" in f["frase"] for f in frasi_ees("etias")) else "see the official page"
    corpo = f"""<section class="hero"><h1>Before You Fly: passport validity, airport liquids rules and EU entry checks ({ANNO})</h1>
<p class="lead">Three things to check before you fly, answered from official sources only: is your passport valid long enough for your destination, can you take more than 100 ml of liquids through security, and what EES and ETIAS mean for your trip. Every rule is quoted word for word with its source and the date we checked it.</p>
</section>
<div class="tre">
<section class="card"><h2><a href="passport-validity/">Passport validity</a></h2><p class="small" style="margin:0">FCDO rules for British passports, {len(PAESI)} destinations, a date checker for {auto} of them. Last checked: {data_lunga(PASS['controllato_il'])}.</p></section>
<section class="card"><h2><a href="liquids/">Liquids by airport</a></h2><p class="small" style="margin:0">100 ml or 2 litres? {len(AER['aeroporti'])} airports plus the US and Canada rules, from official pages.</p></section>
<section class="card"><h2><a href="ees-etias/">EES &amp; ETIAS</a></h2><p class="small" style="margin:0">EES is fully operational; ETIAS is {stato_etias} (European Commission).</p></section>
</div>
<h2>Check your passport dates</h2>
{modulo_checker('tutti-dati', True, link='passport-validity/')}
{AVVISO_PASS}
{AD}
<h2>Popular destinations</h2>
<div class="griglia">{griglia_pass}</div>
<p><a href="passport-validity/">All {len(PAESI)} destinations</a></p>
<h2>Airports that allow up to 2 litres (official pages)</h2>
<div class="griglia">{griglia_2l}</div>
<p><a href="liquids/">All airports, including those that depend on the checkpoint</a></p>
{box_affiliati()}
{dati_json('tutti-dati', [dati_client(P) for P in PAESI])}"""
    pagina("", f"Before You Fly {ANNO}: passport validity checker, liquids rules by airport, EES and ETIAS status",
           f"Is your passport valid long enough? Can you take 2 litres through security? Official FCDO passport rules for {len(PAESI)} destinations, liquids rules for {len(AER['aeroporti'])} airports and EES/ETIAS status, with sources and dates.",
           corpo, js=MOTORE_JS + APP_JS)


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
<p>Source: the “Passport validity requirements” section of the FCDO foreign travel advice for each destination, read through the GOV.UK Content API (<a href="https://www.gov.uk/api/content/foreign-travel-advice" rel="noopener">api/content/foreign-travel-advice</a>), last checked on {data_lunga(PASS['controllato_il'])}. The FCDO advice is written for British citizens.</p>
<p>Licence: contains public sector information licensed under the <a href="{OGL}" rel="noopener">Open Government Licence v3.0</a>. We reproduce the FCDO text unchanged; summaries, the short labels and the date checker are ours.</p>
<p>How the checker works: it applies the FCDO sentence literally. “At least 6 months after the date you arrive” means the expiry date must be on or after the same day of the month 6 months after arrival (if that day does not exist, the last day of that month). “More than” means at least one day later. “Valid for the duration of your stay” means not expiring before the day you leave. The Schengen “date of issue less than 10 years before the date you arrive” means issued after the same day 10 years before arrival.</p>
<p>Destinations where we do not apply the rule automatically ({len(manuali)}), because the official sentence has conditions we do not turn into a calculation:</p>
<ul>{lista_man}</ul>
{f'<p>No page published (the official section is empty):</p><ul>{senza}</ul>' if senza else ''}
<h2>Liquids rules</h2>
<p>Each airport's official security page, last read by us on {data_lunga(AER['controllato_il'])} (the date is shown on each page). Some airport sites block simple automated requests or load their text with JavaScript: we read those in a browser and say so on the page. Spanish airports use the general hand-luggage page of Aena, which runs Spain's public airports (it lists no airport- or lane-specific exceptions); Hong Kong uses the Civil Aviation Department page; the US and Canada each have one national rule (TSA, CATSA). See the full list and the airports we left out on the <a href="{rel}liquids/">liquids page</a>.</p>
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
  # Deploy only when something changed in beforeyoufly/sito.
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
           '<section class="hero"><h1>Page not found</h1><p class="lead">Go to the <a href="/">home page</a>, the <a href="/passport-validity/">passport validity rules</a> '
           'or the <a href="/liquids/">liquids rules by airport</a>.</p></section>', indicizza=False, assoluto=True)


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
