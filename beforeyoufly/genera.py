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
import sys
import unicodedata
from datetime import date, datetime, timedelta
from html import escape
from urllib.parse import quote_plus, urlparse
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
URL_SITO = "https://before-you-fly.com"  # unico punto da cambiare se il nome del sito su Netlify è diverso
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti): non rimuoverlo
GOOGLE_VERIFICA_DOMINIO = "0ZhaE8igdTdGY_RGD8Gqv6PpMxkx1kyQFGo15A4UYoY"  # Search Console, proprietà https://before-you-fly.com (8/11/2026): non rimuoverlo

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
# Monetizzazione (30/10/2026): codice editore AdSense, elenco dei siti con la pubblicità e domini di affiliazione ammessi stanno
# in un solo file comune, studio-business/strumenti/monetizzazione.json (logica in monetizzazione.py). Con il codice vuoto o con
# questo sito fuori elenco non cambia nulla: niente script nel <head>, niente ads.txt, privacy di oggi.
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402
SITO_ID = "beforeyoufly"  # nome del sito in monetizzazione.json ("adsense_siti")
ADSENSE_HEAD = MON.script_adsense(SITO_ID)  # "" con AdSense spento; altrimenti a capo + script ufficiale, subito dopo il meta di verifica Google


def ci_sono_affiliati():
    """True se il sito pubblica almeno un link di affiliazione (voce con "url" in dati/affiliati.json e il riquadro noleggio NOLEGGIO_AUTO):
    accende la sezione privacy sui link di affiliazione. Domini ammessi in monetizzazione.json, controlli in verifica.py."""
    return any(isinstance(v, dict) and v.get("url") for k, v in AFFILIATI.items() if not k.startswith("_")) or bool(NOLEGGIO_AUTO) or bool(STAY22_BIG) or bool(SW_IN)


def riquadro_trasparenza(corpo, lingua="en"):
    """Riga di trasparenza sui link di affiliazione in fondo al contenuto della pagina ("Some links are affiliate links: ..."):
    vuota finché la pagina non ha link rel="sponsored" o se un riquadro di affiliazione la mostra già."""
    return MON.riga_trasparenza(corpo, lingua)


NOME = "Before You Fly"
ANNO = 2026
OGGI = date.today()

PASS = json.loads((DATI / "passaporti.json").read_text(encoding="utf-8"))
AER = json.loads((DATI / "aeroporti.json").read_text(encoding="utf-8"))
LIQ_DOMANDA = json.loads((DATI / "liquidi_domanda.json").read_text(encoding="utf-8"))  # ricerche vere degli aeroporti aggiunti il 5/11/2026
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
.cambio{margin:18px 0;border-left:4px solid var(--sign)}
.cambio h2{margin:0 0 10px;font-size:1.2rem}
.cambio ul{margin:0 0 10px;padding-left:20px}
.cambio li{margin:0 0 6px}
.cambio .small{margin:0}
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
a.btn{display:inline-flex;align-items:center;gap:8px;text-decoration:none;color:var(--sign-ink)}a.btn:hover{color:var(--sign-ink)}a.btn .ico{color:var(--sign-ink)}
.altri-pass.noleggio-home{flex-wrap:nowrap;align-items:flex-start}.noleggio-home .ico{flex:none;margin-top:4px}
.cal-link{display:flex;gap:8px;align-items:flex-start;margin:12px 0}.cal-link .ico{flex:none;margin-top:3px;color:var(--accent)}.cal-lista{padding-left:20px}.cal-lista .cal-link{margin:4px 0 10px}details.tutte{margin:10px 0}details.tutte summary{cursor:pointer;font-weight:700;padding:6px 0}.ufficiale{margin:22px 0}.ufficiale p{margin:0 0 10px}
.aff-tag{display:inline-block;vertical-align:middle;margin-left:6px;font-family:var(--mono);font-size:.68rem;font-weight:400;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);border:1px solid var(--line-2);border-radius:999px;padding:1px 8px}
.noleggio{margin:14px 0 22px}.noleggio p{margin:0 0 12px}.noleggio p.aff-nota{margin:0}.amz-lista{margin:0 0 12px;padding-left:20px}.amz-lista li{margin:4px 0}
caption.cap{caption-side:top;text-align:left;padding:10px 12px;font-size:.84rem;color:var(--ink-3);background:var(--card)}
.tab-g th[scope=row]{width:34%;background:transparent;color:var(--ink-3);border-right:1px solid var(--line)}
blockquote.cit p.trad{font-size:.9rem;color:var(--ink-2);border-top:1px dashed var(--line);padding-top:6px}
.avviso.avviso-idp{background:var(--no-2);border-color:color-mix(in srgb,var(--no) 35%,transparent);font-size:1rem}.avviso.avviso-idp::before{background:var(--no)}
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
    "paw": '<circle cx="7" cy="8.5" r="2"/><circle cx="12" cy="6" r="2"/><circle cx="17" cy="8.5" r="2"/><circle cx="19" cy="13.5" r="1.8"/><path d="M12 11.5c-3 0-6 4.2-6 6.6 0 1.8 1.4 2.4 3 2.4 1.2 0 2-.6 3-.6s1.8.6 3 .6c1.6 0 3-.6 3-2.4 0-2.4-3-6.6-6-6.6z"/>',
    "car": '<path d="M5 16.5V12l1.8-4.6A2 2 0 0 1 8.7 6h6.6a2 2 0 0 1 1.9 1.4L19 12v4.5"/><path d="M3.5 12h17v4.5h-17zM7 16.5V19M17 16.5V19"/><circle cx="7.5" cy="14.2" r=".9"/><circle cx="16.5" cy="14.2" r=".9"/>',
    "bed": '<path d="M3 5v15M3 16h18M21 20v-6.5a2.5 2.5 0 0 0-2.5-2.5H11v5"/><circle cx="7" cy="12.5" r="1.8"/>',
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
    lang_en = ' lang="en"' if lingua not in ("en", "it") else ""  # pagine in tedesco e francese (sezione India): menu e piè di pagina restano in inglese
    piede = PIEDE_IT.replace("{rel}", rel) if it else f"""<footer{lang_en}><div class="wrap">
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
<meta name="google-site-verification" content="{GOOGLE_VERIFICA_DOMINIO}">{ADSENSE_HEAD}
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
<header class="top"{lang_en}><div class="wrap">
<a class="logo" href="{rel}">{MARCHIO}<span>Before <b>You Fly</b></span></a>
<nav class="menu" aria-label="Menu">{menu}</nav>
<details class="nav-m"><summary aria-label="{"Apri il menu" if it else "Open the menu"}">{ico("menu")}Menu</summary><nav aria-label="Menu">{menu}</nav></details>
</div></header>
<main id="main">
{testata}
<div class="wrap">
{bc}
{corpo}{riquadro_trasparenza(corpo, lingua)}
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
    """Riquadro generico «Before you go» (assicurazione, eSIM, parcheggi/lounge: voci di dati/affiliati.json con 'url' pieno, tranne
    'bagagli' e le voci con '_'): vuoto (non mostrato) finché non ci sono URL.
    Dal 6/11/2026 (eSIM Roamable acceso) compare SOLO dove chi legge sta preparando un viaggio all'estero: pagine destinazione e indici
    del passaporto britannico (FCDO), canadese e australiano, e pagina EES/ETIAS. Tolto dalla home (pagina generica), dalle pagine e
    dall'indice dei liquidi (chi legge è spesso all'aeroporto di partenza o su un volo nazionale; le pagine di vacanza hanno già i
    riquadri noleggio e alloggio) e mai nel bagaglio a mano (lì c'è box_bagagli). verifica.py, punto 31, controlla questi posti."""
    voci = [v for k, v in AFFILIATI.items() if not k.startswith("_") and k != "bagagli" and isinstance(v, dict) and v.get("url")]
    if not voci:
        return ""
    righe = "".join(f'<li><a href="{escape(v["url"])}" rel="sponsored noopener" target="_blank">{escape(v["titolo"])}</a> '
                    f'<span class="small">{escape(v["nome"]) + ": " if v.get("nome") else ""}{escape(v["testo"])}</span></li>' for v in voci)
    return (f'<section class="card" style="margin-top:22px" aria-label="Before you go, affiliate links" data-affiliati><h2 style="margin-top:0">Before you go <span class="aff-tag">Affiliate</span></h2>'
            f'<ul style="margin:0 0 8px;padding-left:20px">{righe}</ul>'
            f'<p class="small" style="margin:0">{MON.RIGA_EN}</p></section>')  # riga di trasparenza comune (monetizzazione.py)


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
{link_guida(rel, ISO_DA_FCDO.get(P["slug"]), "uk")}{link_india(rel, ISO_DA_FCDO.get(P["slug"]), "uk")}
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
{link_guida(rel, v["p"].get("iso") if k == "ca" else ISO_DA_AU.get(_chiave_nome(v["p"]["nome"])), k)}{link_india(rel, v["p"].get("iso") if k == "ca" else ISO_DA_AU.get(_chiave_nome(v["p"]["nome"])), k)}
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
               "liverpool": "Liverpool", "berlin": "Berlin",
               # 5/11/2026: il nome come lo cercano (dati/liquidi_domanda.json, "<nome> airport liquid…")
               "thessaloniki": "Thessaloniki", "preveza-aktion": "Preveza", "milan-bergamo": "Bergamo", "bologna": "Bologna", "keflavik": "Keflavik",
               "glasgow-prestwick": "Prestwick", "teesside": "Teesside", "knock": "Knock", "almeria": "Almeria", "murcia": "Murcia", "girona": "Girona",
               "granada": "Granada", "santiago-de-compostela": "Santiago de Compostela"}
SIGLA_PAESE = {"United States": "US", "Canada": "Canadian"}
# contesto (GOV.UK / Your Europe) da citare nelle FAQ quando la pagina dell'aeroporto non dice il dettaglio: per Paese
PAESI_UE = {"Ireland", "Germany", "Austria", "Italy", "Finland", "Sweden", "Denmark", "Netherlands", "Czechia", "Poland", "Portugal", "Spain", "Greece", "Malta",
            "Belgium", "Hungary", "France", "Croatia", "Cyprus", "Luxembourg", "Slovakia", "Slovenia", "Romania", "Bulgaria", "Estonia", "Latvia", "Lithuania"}


# fonte di gruppo (una pagina del gestore per più aeroporti): lo dice la frase diretta in alto (verifica.py, punti 9 e 30)
FONTE_GRUPPO = {"aena": " The source is Aena's general hand-luggage page, not a page for this airport.",
                "hial": " The source is the security page of HIAL, the company that runs the airport, not a page for this airport alone."}


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


def frasi_fonte2_liq(A):
    """Dal 5/11/2026 (revisione) anche le citazioni della seconda pagina ufficiale entrano nelle FAQ, con il loro prefisso
    "Quoted from <titolo della seconda fonte>": così una FAQ non dice che le frasi citate non parlano di un tema che la seconda fonte tratta."""
    return list((A.get("fonte2") or {}).get("citazioni") or [])


def prefisso_fonte2(A):
    return f"Quoted from {A['fonte2']['titolo']} (checked on {data_lunga(A['controllato_il'])}): "


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
     re.compile(r"plastic bags?|re-?sealable|clear bag|transparent bag|lit(?:re|er) bag|liquid bag|quart-sized bag|zipper bag|zip-?lock bag|20 ?cm ?x ?20|20 x 20"
                r"|1L in capacity", re.I)),
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
# frase nostra fissa (senza numeri) quando una FAQ cita anche la seconda fonte e la scheda lo chiede ("faq_nota_fonte2": Dubrovnik)
NOTA_FONTE2_LIQ = "The second source quoted below does not mention any change to the liquids limit on the official page quoted first."
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
    gruppi2 = gruppi_liq(A, frasi_fonte2_liq(A))
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
            def tema(gg, fuori=None):
                return [f for g in gg if any(rx.search(x) and not RX_FUORI_TEMA.search(x) and not (chiave != "dutyfree" and re.search(r"tamper|duty", x, re.I))
                                             and not (fuori and fuori.search(x)) for x in g) for f in g]
            # seconda fonte: le frasi su medicine e neonati solo nella domanda sui neonati (Antalya: pagina delle eccezioni)
            ff, ff2 = tema(gruppi), tema(gruppi2, None if chiave in ("baby", "dutyfree") else dict((c, r) for c, _, r in FAQ_LIQ)["baby"])
            if ff or ff2:
                blocchi = ([(pre, ff)] if ff else []) + ([(prefisso_fonte2(A), ff2)] if ff2 else [])
                intro = NOTA_FONTE2_LIQ if (ff and ff2 and chiave in A.get("faq_nota_fonte2", [])) else ""
                voci[chiave] = (q, intro, blocchi)
            elif chiave in MANCA_LIQ:
                testo = MANCA_LIQ[chiave].format(n=A["nome"]) + ("" if chiave == "scanner" else " " + RINVIO_LIQ[ctx])
                # Your Europe (100 ml) non si cita sulla busta quando la pagina dell'aeroporto permette 2 litri (revisione del 5/11/2026)
                blocchi = [(prefisso_contesto(C), list(C["citazioni"]))] if (C and chiave == "busta" and A["regola"] != "2l") else []
                voci[chiave] = (q, testo, blocchi)
    # ordine: limite, terminal (solo con citazioni), i temi con citazioni, poi quelli senza, borraccia (solo con citazioni), 2026; al massimo 6
    centro = [k for k in ("scanner", "busta", "baby", "dutyfree") if k in voci]
    def citata(k):  # risposta fatta di citazioni dell'aeroporto (anche con la nota fissa sulla seconda fonte), non la frase "la pagina non lo dice"
        return bool(voci[k][2]) and (not voci[k][1] or voci[k][1] == NOTA_FONTE2_LIQ)
    centro = [k for k in centro if citata(k)] + [k for k in centro if not citata(k)]
    ordine = ["limite"] + (["terminal"] if "terminal" in voci else []) + centro + (["borraccia"] if "borraccia" in voci else []) + ["2026"]
    while len(ordine) > 6:
        senza = [k for k in ordine if k in MANCA_LIQ and not citata(k)]
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


# Riquadri di guadagno sulle pagine liquidi degli aeroporti di vacanza (5/11/2026), sempre DOPO la regola ufficiale e le eccezioni:
# "Hire a car at <aeroporto>" (DiscoverCars, stesso link generale NOLEGGIO_AUTO: DiscoverCars non documenta un parametro pubblico di
# destinazione) e, dove esiste già un link Stay22 per la stessa città, "Where to stay in <città>" (stesso link della sezione Ticket release dates).
# Elenchi in dati/affiliati.json ("liquidi" sotto _discovercars_noleggio e _stay22_alloggi). Mai sugli aeroporti di partenza tipici di chi legge
# (Regno Unito, Irlanda, isole della Manica, USA, Canada) né sugli scali di transito: controlli() qui sotto e verifica.py, punto 30.
NOLEGGIO_LIQ = list((AFFILIATI.get("_discovercars_noleggio") or {}).get("liquidi") or [])
ALLOGGI_LIQ = dict((AFFILIATI.get("_stay22_alloggi") or {}).get("liquidi") or {})
PAESI_PARTENZA_LIQ = {"United Kingdom", "Ireland", "Jersey", "Guernsey", "United States", "Canada"}
SCALI_TRANSITO_LIQ = {"istanbul", "dubai", "doha", "hong-kong"}


def box_noleggio_liq(A):
    """Riquadro "Hire a car at <aeroporto>" (DiscoverCars): '' se il noleggio è spento o l'aeroporto non è tra quelli di vacanza."""
    if not NOLEGGIO_AUTO or A["slug"] not in NOLEGGIO_LIQ:
        return ""
    n = f'{A["nome"]} Airport'
    return (f'<h2 id="hire-a-car">Hire a car at {escape(n)}</h2>'
            f'<section class="card noleggio" aria-label="Car hire, affiliate link" data-noleggio>'
            f'<p>Arriving at {escape(dove_liq(A))}? Compare rental companies and prices on DiscoverCars. The link opens the DiscoverCars search page: '
            f'choose {escape(n)} as your pick-up location.</p>'
            f'<p class="noleggio-btn"><a class="btn" href="{escape(NOLEGGIO_AUTO)}" rel="sponsored noopener" target="_blank">'
            f'{ico("car")}Compare car hire</a></p>'
            f'{MON.nota_trasparenza("en")}</section>')


def box_alloggio_liq(A):
    """Riquadro "Where to stay in <città>" (Stay22 → Booking.com): solo dove c'è già un link Stay22 della stessa città; '' altrimenti."""
    v = STAY22_BIG.get(ALLOGGI_LIQ.get(A["slug"], ""))
    if not v or A["slug"] not in NOLEGGIO_LIQ:
        return ""
    c = v["citta"]
    return (f'<h2 id="where-to-stay">Where to stay in {escape(c)} <span class="aff-tag">Affiliate</span></h2>'
            f'<section class="card noleggio" aria-label="Where to stay, affiliate link" data-alloggio>'
            f'<p>Staying in {escape(c)}? This link opens the Booking.com page of hotels across {escape(c)}: check the distance from '
            f'{escape(A["nome"])} Airport on the map before you book.</p>'
            f'<p class="noleggio-btn"><a class="btn" href="{escape(v["url"])}" rel="sponsored noopener" target="_blank">'
            f'{ico("bed")}See hotels in {escape(c)} on Booking.com</a></p>'
            f'<p class="small">Link through our partner Stay22. Prices and availability are only those shown on Booking.com.</p>'
            f'{MON.nota_trasparenza("en")}</section>')


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
<p class="lead">{escape(frase_diretta(A, nazionale))}{escape(FONTE_GRUPPO.get(A.get('gestore'), ''))}</p>
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
{"" if nazionale else box_noleggio_liq(A) + box_alloggio_liq(A)}
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
<p>Packing hand luggage? See the <a href="{rel}cabin-bags/">cabin bag size by airline</a>.</p>"""
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
{link_es_tb(rel)}
<h2>Official EU website for EES and ETIAS</h2>
<p>The EU's official site for travellers is travel-europe.europa.eu: <a href="{escape(EES['sito_ufficiale']['ees'])}" rel="noopener">EES page</a> and <a href="{escape(EES['sito_ufficiale']['etias'])}" rel="noopener">ETIAS page</a>. Our server could not read it on {data_lunga(EES['controllato_il'])} (its security certificate chain was incomplete for automated tools), so we quote the European Commission pages above instead.</p>
<p class="avviso">This page is information, not legal advice. Border guards apply the rules at the border. Before you travel, check the official pages linked above and your airline, ferry or train operator.</p>
{box_affiliati()}
<p><a href="{rel}passport-validity/">Passport validity rules</a> · <a href="{rel}liquids/">Liquids rules by airport</a>{f' · <a href="{rel}{TB_ES}/">Eurostar check-in times by station, with EES</a>' if TB_EUR else ""}</p>"""
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


# ---- Amazon Associates (acceso il 6/11/2026): link di RICERCA Amazon per la misura della pagina, solo nel bagaglio a mano.
# Mai ASIN né pagine prodotto: solo https://www.<dominio>/s?k=<misura + tipo di borsa>&tag=<tag del dominio>. Tag in dati/affiliati.json
# (voce "bagagli", campo "tag"); 'url' della voce è l'interruttore (vuoto = riquadro spento ovunque).
# Mercato scelto dal pubblico della pagina:
#   - compagnie europee (area "Europe") → amazon.co.uk: pubblico britannico ed europeo, misure in centimetri;
#   - compagnie di USA e Canada ("North America") → amazon.com, con i pollici ufficiali della compagnia;
#   - Medio Oriente e Australia (Emirates, Qatar, Qantas: pubblico misto) → entrambi;
#   - pagine per misura (/cabin-bags/size/<misura>/: centimetri, misure delle compagnie europee) → amazon.co.uk;
#   - indice e strumento «Does my bag fit?» (tutte le compagnie, pubblico misto) → entrambi, ricerca generica.
# verifica.py, punto 31, ricontrolla tag per dominio, assenza di ASIN, mercato per pagina e la frase obbligatoria di Amazon.
AMAZON_BAG = AFFILIATI.get("bagagli") or {}
AMAZON_ACCESO = bool((AMAZON_BAG.get("url") or "").strip())
AMAZON_TAG = dict(AMAZON_BAG.get("tag") or {})
AMAZON_FRASE = "As an Amazon Associate we earn from qualifying purchases."  # frase richiesta da Amazon Associates
AMAZON_NOME = {"amazon.co.uk": "Amazon.co.uk", "amazon.com": "Amazon.com"}
MERCATI_AREA = {"Europe": ["amazon.co.uk"], "North America": ["amazon.com"], "Middle East and Australia": ["amazon.co.uk", "amazon.com"]}


def amazon_link(dominio, ricerca):
    """Link di ricerca Amazon con il tag del dominio (nessun ASIN)."""
    return f"https://www.{dominio}/s?k={quote_plus(ricerca)}&tag={AMAZON_TAG[dominio]}"


def mercati_bag(C):
    return MERCATI_AREA.get(C["area"], ["amazon.co.uk", "amazon.com"])  # area sconosciuta: pubblico non chiaro, entrambi


def ricerche_compagnia(C):
    """(dominio, ricerca, etichetta) per ogni borsa della compagnia e ogni mercato della pagina, senza doppioni.
    amazon.co.uk: centimetri ufficiali; amazon.com: pollici ufficiali se la compagnia li pubblica, altrimenti centimetri."""
    out, viste = [], set()
    for dom in mercati_bag(C):
        for b in C["borse"]:
            sotto = b["tipo"] == "sotto"
            if dom == "amazon.com" and b.get("pollici") and b.get("pollici_ufficiali"):
                v, u = sorted(b["pollici"], reverse=True), "in"
            else:
                v, u = sorted(b["cm"], reverse=True), "cm"
            mis = "x".join(n2(x) for x in v)
            if dom == "amazon.com":
                tipo, nome = ("personal item bag", "Personal item bags") if sotto else ("carry on bag", "Carry-on bags")
            else:
                tipo, nome = ("under seat bag", "Under-seat bags") if sotto else ("cabin bag", "Cabin bags")
            ricerca = f"{mis}{' cm' if u == 'cm' and dom == 'amazon.com' else ''} {tipo}"
            if (dom, ricerca) in viste:
                continue
            viste.add((dom, ricerca))
            out.append((dom, ricerca, f"{nome} {mis.replace('x', ' x ')} {u} on {AMAZON_NOME[dom]}"))
    return out


def box_bagagli(C=None, misura=None):
    """Riquadro «Bags in the right size» con link di ricerca Amazon (voce 'bagagli' di dati/affiliati.json): '' se spento.
    C = pagina compagnia (le sue misure), misura = (slug, misure) della pagina per misura; nessuno dei due = indice o strumento."""
    if not AMAZON_ACCESO:
        return ""
    if C is not None:
        voci = ricerche_compagnia(C)
        frase = (f"These links open an Amazon search for bags in {escape(poss(C['nome']))} sizes. The results are Amazon's, not checked by us: "
                 f"measure each bag, wheels and handles included, against {escape(poss(C['nome']))} official limit above before you buy.")
    elif misura is not None:
        sl, m = misura
        tipo = "under seat bag" if max(m) <= 45 else "cabin bag"
        voci = [("amazon.co.uk", f"{sl} {tipo}", f"{sl.replace('x', ' x ')} cm {tipo.replace('under seat', 'under-seat')}s on Amazon.co.uk")]
        frase = (f"This link opens an Amazon search for {sl.replace('x', ' x ')} cm bags. The results are Amazon's, not checked by us: check the size of each "
                 "bag, wheels and handles included, and your airline's official limit before you buy.")
    else:
        voci = [("amazon.co.uk", "cabin bag", "Cabin and under-seat bags on Amazon.co.uk"), ("amazon.com", "carry on bag", "Carry-on and personal item bags on Amazon.com")]
        frase = ("These links open an Amazon search. Look up your airline's official limit first, then search with that size. "
                 "The results are Amazon's, not checked by us: measure each bag, wheels and handles included, before you buy.")
    righe = "".join(f'<li><a href="{escape(amazon_link(d, r))}" rel="sponsored noopener" target="_blank">{escape(e)}</a></li>' for d, r, e in voci)
    return (f'<h2 id="bags">{escape(AMAZON_BAG.get("titolo") or "Bags in the right size")} <span class="aff-tag">Affiliate</span></h2>'
            f'<section class="card noleggio" aria-label="Bags on Amazon, affiliate links" data-amazon>'
            f'<p>{frase}</p><ul class="amz-lista">{righe}</ul>'
            f'<p class="small aff-nota">{MON.RIGA_EN} {AMAZON_FRASE}</p></section>')


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
{box_bagagli(C)}
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
{box_bagagli(misura=(sl, m))}
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
{f'<p class="altri-pass">{ico("bag")}<span>Taking the train instead? <a href="{rel}{TB_BASE}/">Luggage rules on European trains</a>: Eurostar, TGV INOUI, OUIGO, Avlo, Italo, Deutsche Bahn and more</span></p>' if TB else ""}
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
    # dal 7/11/2026
    "google-wallet": {"fonte": "Google Wallet Help", "lista": "Google's list of countries where Google Wallet is available"},
    "wise": {"fonte": "Wise Help Centre", "lista": "Wise's list of countries and territories where you can hold money in your Wise account if you live there"},
    "uber": {"fonte": "Uber", "lista": "the list of countries on Uber's official cities page"},
    "stripe": {"fonte": "Stripe", "lista": "Stripe's list of countries and regions where Stripe is currently supported"},
}
# Google Wallet (dal 7/11/2026): la riga "Tap to pay" della pagina di ogni Paese (spunta verde o croce rossa), detta con parole fisse
# Revisione del 7/11/2026: frasi fisse per Uber (la pagina elenca città) e Stripe (etichette non spiegate, lista per le aziende)
UBER_CITTA = ("Uber's page lists cities, not whole countries: {P} is here because at least one city there is on the page; "
              "check your city on the official page.")
STRIPE_ETICHETTE = "Stripe's page does not explain these labels"
STRIPE_CHI = ("This list is about businesses opening a Stripe account to accept payments, not about paying with your card on a website "
              "or in a shop that uses Stripe.")
TOCCO_GW = {True: "The same page shows tap to pay (contactless payments in shops) as available there.",
            False: "The same page shows tap to pay (contactless payments in shops) as not available there."}
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


def solo_invio_wise(S, c):
    """Wise (revisione del 7/11/2026): Paese assente dalla tabella "hold money" ma nella lista "send to": "Not for holding money", non un No."""
    return S["slug"] == "wise" and c not in S["paesi"] and c in S.get("extra", {}).get("invio", [])


def breve_srv(S, c):
    """Risposta breve per titolo, tabella e riquadro."""
    st, v = stato_srv(S, c)
    if st == "si":
        return "Yes, no tap to pay" if S["slug"] == "google-wallet" and not v.get("tocco") else "Yes"
    if st == "in_arrivo":
        return "Coming soon"
    if st == "per_regione":
        return "By region"
    if st == "no":
        if S["slug"] == "starlink":
            return "No service shown"
        if S["slug"] == "youtube-premium":
            return (v.get("nota") or "Not available").capitalize()
        if S["slug"] == "wise":
            return "Not supported"  # tra i Paesi dove Wise "does not offer its services"
        return "Not listed"
    if solo_invio_wise(S, c):
        return "Not for holding money"
    return "Not on the list"


def classe_srv(st, S=None, c=None):
    if S is not None and solo_invio_wise(S, c):
        return "manuale"
    return {"si": "si", "in_arrivo": "manuale", "per_regione": "manuale", "no": "no", "assente": "no"}[st]


def badge_srv(S, c, con_nota=True):
    st, v = stato_srv(S, c)
    k = {"si": "gratis", "in_arrivo": "altre", "per_regione": "altre", "no": "no", "assente": "no"}[st]
    if solo_invio_wise(S, c):
        k = "altre"
    nota = f' <span class="small">{escape(v["nota"])}</span>' if (con_nota and v and v.get("nota") and st == "si") else ""
    if nota and S["slug"] == "stripe":
        nota = nota[:-7] + f' ({escape(STRIPE_ETICHETTE)})</span>'

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
    if solo_invio_wise(S, c):
        return (f"Not for holding money: {P} is not on {T['lista']} ({T['fonte']}, checked on {d}). Wise says “{SRV['frasi']['wise_ovunque']['frase']}”, "
                f"and {P} is on its list of countries and regions you can send money to.")
    if st == "si":
        nota = f" The list adds: “{v['nota']}”." if v.get("nota") else ""
        if S["slug"] == "google-wallet":
            nota = " " + TOCCO_GW[bool(v.get("tocco"))]
        if S["slug"] == "stripe" and nota:
            nota += f" {STRIPE_ETICHETTE}."
        if S["slug"] == "uber":
            nota = " " + UBER_CITTA.format(P=P)
        return f"Yes. {Pm} is on {T['lista']} ({T['fonte']}, checked on {d}).{nota}"
    if st == "no":
        if S["slug"] == "google-wallet":
            return f"No. Google's page lists {P}, but shows the Google Wallet app as not available there ({T['fonte']}, checked on {d})."
        if S["slug"] == "wise":
            return f"No. Wise lists {P} among the places where it does not offer its services ({T['fonte']}, checked on {d})."
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
    if S["slug"] == "stripe" and not S.get("_chi"):
        return STRIPE_CHI + " " + significato_srv({**S, "_chi": True}, c)
    if solo_invio_wise(S, c):
        return "This list is only about holding money in your account; Wise does not give reasons."
    if st == "assente" and S["slug"] == "wise":
        return (f"Not being on this list is not the same as being banned: Wise says “{SRV['frasi']['wise_ovunque']['frase']}”, "
                "and this list is only about holding money in your account.")
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
    if S["slug"] in ("google-wallet", "wise", "uber", "stripe"):
        return "Lists change: check the official page before you rely on the service."
    return "Lists change: check the official page before you pay for a subscription."


def titoli_srv(S, c):
    n, P, b = S["nome"], frase_srv(c), breve_srv(S, c)
    b_tit = {"Not on the list": "Not on the Official List", "Coming soon": "Coming Soon", "No service shown": "No Service Shown",
             "Not listed": "Not Listed", "By region": "Depends on the Region", "Not supported": "Not Supported",
             "Yes, no tap to pay": "Yes, No Tap to Pay", "Not for holding money": "Not for Holding Money"}.get(b, b.title() if b != "Yes" else b)
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
    "google-wallet": (["google_wallet_lista", "google_wallet_assente"], ["google_wallet_tocco", "google_pay_varia"]),
    "wise": (["wise_lista", "wise_nuovi"], ["wise_ovunque"]),  # per i Paesi "Not supported" anche wise_no, wise_no_invio, wise_no_cosa
    "uber": (["uber_lista"], []),
    "stripe": (["stripe_lista"], ["stripe_vendere"]),
}


def online_gp(c):
    """Google Pay online (lista "Pay online or in apps" della pagina Google Pay): frase fissa per il Paese."""
    if c in SRV_PER["google-wallet"].get("extra", {}).get("online", []):
        return f"Google's list of countries where you can pay with Google Pay on participating websites and apps includes {frase_srv(c)}."
    return f"{frase_srv(c, True)} is not on Google's list of countries where you can pay with Google Pay on participating websites and apps."


def tocco_gp(c):
    st, v = stato_srv(SRV_PER["google-wallet"], c)
    if st == "assente":
        return f"{frase_srv(c, True)} is not on Google's list of countries where Google Wallet (tap to pay in shops) is available."
    return f"For tap to pay in shops, Google's Wallet page shows it as {'available' if v.get('tocco') else 'not available'} in {frase_srv(c)}."


def invio_wise(c):
    return c in SRV_PER["wise"].get("extra", {}).get("invio", [])


def piu_srv(S, c):
    """Fatti in più delle fonti dei servizi del 7/11 (Google Pay online, Wise invio), sotto "What the official source says"."""
    P, Pm = frase_srv(c), frase_srv(c, True)
    if S["slug"] == "google-wallet":
        x = f'<h3>Paying online with Google Pay</h3><p>{escape(online_gp(c))} Google introduces that list with these words:</p>{cit_srv(["google_pay_online"])}'
        if c in ("IN", "SG"):
            x += f'<p>For sending money, Google says:</p>{cit_srv(["google_pay_invio"])}'
        return x
    if S["slug"] == "wise" and invio_wise(c):
        return (f'<h3>Sending money to {escape(P)}</h3><p>{escape(Pm)} is on Wise\'s list of countries and regions you can send money to. '
                f'Wise introduces that list with these words:</p>{cit_srv(["wise_invio_lista"])}')
    return ""


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
    if S["slug"] == "google-wallet":
        extra = f" Google also says: “{SRV['frasi']['google_pay_invio']['frase']}”" if c in ("IN", "SG") else ""
        out.append((f"Is Google Pay available in {P}?", f"{online_gp(c)} {tocco_gp(c)}{extra}"))
    if S["slug"] == "wise":
        st, _ = stato_srv(S, c)
        if invio_wise(c):
            out.append((f"Can I send money to {P} with Wise?", f"Yes. {frase_srv(c, True)} is on Wise's list of countries and regions you can send money to "
                                                            f"({SRV_TESTI['wise']['fonte']}, checked on {data_controllo_srv(S)})."))
        elif st == "no":
            out.append((f"Can I send money to {P} with Wise?", f"No. Wise says you can't “{SRV['frasi']['wise_no_invio']['frase']}” where it does not "
                                                            f"offer its services, and {P} is one of those places."))
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
    icona = "alert" if solo_invio_wise(S, c) else {"si": "check", "in_arrivo": "alert", "per_regione": "alert", "no": "x", "assente": "x"}[st]
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
    tit_viaggio = (f"If {n} is not available in {P}" if se_no else
                   {"stripe": f"Using Stripe from {P}", "uber": f"Using Uber in {P}"}.get(S["slug"], f"Travelling or moving to {P} with {n}"))
    if solo_invio_wise(S, c):
        tit_viaggio = f"Using Wise from {P}"
    if S["slug"] == "starlink":
        viaggio = ("<p>Check your exact address on Starlink's official map before you buy equipment or travel with it: the status can change and can "
                   "differ within a country.</p>")
    elif S["slug"] == "apple-pay":
        viaggio = f'<p>What Apple says about paying abroad and about Apple Cash:</p>{cit_srv(c_viaggio)}'
    elif c_viaggio:
        viaggio = f'<p>What {escape(S["fornitore"].split(" (")[0])} says about using it in another country:</p>{cit_srv(c_viaggio)}'
        if S["slug"] == "wise" and st == "no":
            viaggio += (f'<p>{escape(frase_srv(c, True))} is on Wise\'s list of places where it does not offer its services:</p>{cit_srv(["wise_no"])}'
                        f'<p>About those places, Wise says you can\'t:</p>{cit_srv(["wise_no_invio", "wise_no_cosa"])}')
    else:
        viaggio = ""
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
<div class="esito e-srv {classe_srv(st, S, c)}">{ico(icona)}<strong>{escape(breve_srv(S, c))}</strong></div>
<p class="lead" id="answer">{escape(risposta_srv(S, c))}</p>
<p class="lead">{escape(significato_srv(S, c))}</p>
{fonte_srv(S)}
</div></section>
<h2>What the official source says</h2>
{cosa_dice}
{f'<p><strong>What this list covers:</strong> {escape(S["cosa"])}.</p>' if S["slug"] == "stripe" else ""}
{sotto}
{piu_srv(S, c)}
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


def extra_servizio_srv(S):
    """Frasi fisse in testa alla pagina del servizio (revisione del 7/11/2026)."""
    if S["slug"] == "uber":
        return f'<p class="lead">{escape(UBER_CITTA.replace("{P} is here", "a country is here"))}</p>'
    if S["slug"] == "stripe":
        return (f'<p class="lead">{escape(STRIPE_CHI)} What this list covers: {escape(S["cosa"])}. Some countries carry the label “Preview” or '
                f'“Extended network”; {escape(STRIPE_ETICHETTE)}.</p>')
    if S["slug"] == "wise":
        return ('<p class="lead">“Not for holding money” means the country is not on this list but is on Wise\'s list of countries you can send money to.</p>')
    return ""


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
    elif S["slug"] == "google-wallet":
        tap = sum(1 for c in con if S["paesi"][c].get("tocco"))
        prima = (f"{len(con)} countries and territories are on {T['lista']} ({T['fonte']}, checked on {d}); the same page shows tap to pay as "
                 f"available in {tap} of them.")
    else:
        prima = f"{len(con)} countries and territories are on {T['lista']} ({T['fonte']}, checked on {d})."
    pagine = pagine_srv(S)

    def nota(c):
        st, v = stato_srv(S, c)
        if solo_invio_wise(S, c):
            return "on Wise's list of countries you can send money to"
        if not v:
            return "–"
        x = []
        if v.get("nomi_fonte") and any(_chiave_nome(y) != _chiave_nome(nome_srv(c)) for y in v["nomi_fonte"]):
            x.append("listed as “" + " / ".join(v["nomi_fonte"]) + "”")
        if v.get("nota"):
            x.append(("Apple TV app: " if S["slug"] == "apple-tv" else "") + "“" + v["nota"] + "”"
                     + (f" ({STRIPE_ETICHETTE})" if S["slug"] == "stripe" else ""))
        if S["slug"] == "apple-tv" and st == "no" and not v.get("app_tv"):
            x.append("no Apple TV app listed")
        if S["slug"] == "google-wallet":
            x.append("tap to pay " + ("available" if v.get("tocco") else "not available") + "; website " + ("available" if v.get("sito") else "not available"))
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
        if S["slug"] == "google-wallet":
            spiega += ("<p>Google's page has one entry per country, with three lines: the Google Wallet app, tap to pay and the Google Wallet website. "
                       "“Yes, no tap to pay” means the app is shown as available but tap to pay is not.</p>")
        if S["slug"] == "wise":
            spiega += (f'<p>“Not supported” means the country is on Wise\'s other list, of the places where it does not offer its services:</p>{cit_srv(["wise_no", "wise_no_cosa"])}'
                       f'<p>Wise also says:</p>{cit_srv(["wise_ovunque"])}')
    griglia = "".join(f'<a href="{rel}{url_srv(S, c)}">{escape(nome_srv(c))}<small>{escape(breve_srv(S, c))}</small></a>' for c in pagine)
    corpo = f"""<section class="hero">{h1_diviso(f"Where is {n} available? Official list of countries ({ANNO})")}
<p class="lead" id="answer">{escape(prima)}</p>{extra_servizio_srv(S)}</section>
<ul class="stat"><li><strong>{len(con)}</strong>{"“Available”" if S["slug"] == "starlink" else "on the list"}</li>{f'<li><strong>{len(arr)}</strong>“Coming soon”</li>' if S["slug"] == "starlink" else ""}{f'<li><strong>{sum(1 for c in con if S["paesi"][c].get("tocco"))}</strong>with tap to pay</li>' if S["slug"] == "google-wallet" else ""}<li><strong>{d}</strong>last checked</li></ul>
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
<p>“Yes” means the country is on the provider's list; for Starlink, “Coming soon”, “No service shown” and “By region” describe the provider's map. For Google Wallet, “Yes, no tap to pay” means the app is listed but tap to pay is not; for Wise, “Not supported” means Wise lists the country among the places where it does not offer its services, and “Not for holding money” means you can send money there but the country is not on Wise's list for holding money. Uber's page lists cities, not whole countries; Stripe's list is for businesses opening an account. Click an answer for the details and the source.</p>
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
    for S, c in (("starlink", "PK"), ("apple-pay", "IN"), ("google-wallet", "PH"), ("youtube-premium", "PK"), ("spotify", "CN"), ("wise", "PK"),
                 ("apple-tv", "NG"), ("starlink", "PH"), ("apple-music", "CN"), ("apple-pay", "PH")):
        if S in SRV_PER and c in pagine_srv(SRV_PER[S]):
            voci.append(f'<a href="{url_srv(SRV_PER[S], c)}">{escape(SRV_PER[S]["nome"])} in {escape(frase_srv(c))}<small>{escape(breve_srv(SRV_PER[S], c))}</small></a>')
    nomi = ", ".join(S["nome"] for S in SERVIZI_SRV[:-1]) + " and " + SERVIZI_SRV[-1]["nome"]
    return (f'<h2>Is it available where you are going?</h2><p>{escape(nomi)} publish their own lists '
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
<p>Rules: a country is “Yes” only if the provider's list names it; “Not on the list” means the list does not name it, which is not the same as a ban. For Starlink we show the statuses of the official availability map (“Available”, “Coming soon” with the note the map gives, no service shown, or “By region” when the map colours a country region by region), as the map's own legend explains them. For Google Wallet we also show the tap to pay line of Google's page for each country, and Google Pay's separate list for paying online; for Wise, the countries where you can hold money if you live there, the places where Wise does not offer its services (“Not supported”) and the countries you can send money to. Names are matched to ISO 3166-1 country codes; regions inside a country are not shown separately. We give no advice on getting around restrictions. A page for a single service and country exists only where people search for it. The lists are facts published by each provider; the trademarks belong to their owners, and Before You Fly is not affiliated with any of them.</p>"""


# ---------------------------------------------------------------- "Can I drive in [country] with my UK / Canadian / Australian licence?" (dal 28/10/2026)
# Dati: dati/patenti.json (frasi ufficiali sul permesso internazionale, lette da raccolta/patenti.py: tabella GOV.UK + consigli FCDO,
# travel.gc.ca, Smartraveller; esito da schemi fissi o da fatti scritti a mano in dati/patenti_manuali.json) e dati/patenti_domanda.json
# (ricerche vere dell'autocompletamento: una pagina Paese × patente esiste SOLO per le coppie in "pagine" e solo se la fonte dice qualcosa).
# Regole: la prima frase dice sì / no / dipende con la frase dell'ente tra virgolette, la fonte e la data; se la fonte non dice nulla:
# "Not stated by <ente>", mai una deduzione; nessun consiglio legale personale; link affiliati solo nel riquadro "Hire a car" (NOLEGGIO_AUTO, DiscoverCars, acceso dal 30/10/2026), dopo le regole ufficiali.
PAT_BASE = "driving-abroad"
_f_pat = DATI / "patenti.json"
PAT = json.loads(_f_pat.read_text(encoding="utf-8")) if _f_pat.exists() else None
_f_pat_dom = DATI / "patenti_domanda.json"
PAT_DOM = json.loads(_f_pat_dom.read_text(encoding="utf-8")) if _f_pat_dom.exists() else {"pagine": {}, "patenti": {}}
PAT_PER = {p["iso2"]: p for p in PAT["paesi"]} if PAT else {}
PAT_G = PAT["frasi_generali"] if PAT else {}
# Riquadro "Hire a car" (noleggio auto, link di affiliazione DiscoverCars), acceso il 30/10/2026: NOLEGGIO_AUTO è l'URL di
# dati/affiliati.json, voce "_discovercars_noleggio" (vuoto = riquadro spento, niente link). Link generale con il nostro a_aid, mai pagine
# Paese di DiscoverCars non verificate (il sito risponde 403 dal server). Il riquadro (box_noleggio) va sempre DOPO la risposta e le regole
# ufficiali, con rel="sponsored noopener", target="_blank" e la riga MON.RIGA_EN; con esito "IDP needed" o "Local permit needed" la frase
# sul permesso è un avviso a parte, fuori dal riquadro commerciale. Lo controllano controlli() qui e il punto 18 di verifica.py.
NOLEGGIO_AUTO = ((AFFILIATI.get("_discovercars_noleggio") or {}).get("url") or "").strip()
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
    ("au", "TH"): "on how long you stay (people living in Thailand for an extended period need a Thai licence)",
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


FRASE_NOLEGGIO = "Check the licence and IDP rules above before you book: the rental desk can refuse your booking without the right permit."


def avviso_noleggio_pat(k, c):
    """Con esito "IDP needed" o "Local permit needed": la frase sul permesso come avviso evidente (informazione di sicurezza, non pubblicità)."""
    v, T, P = voce_pat(k, c), PATENTI[k], frase_srv(c)
    if v["esito"] == "si":
        testa = (f"IDP needed in {P}:", f"the official advice quoted above says you need an international driving permit to drive there with "
                                         f"{T['art']} {T['lic']}.")
    elif v["esito"] == "locale":
        testa = (f"Local permit needed in {P}:", f"the official advice quoted above says an IDP alone is not enough with {T['art']} {T['lic']}, "
                                                  "and that you need a local licence or permit.")
    else:
        return ""
    return (f'<p class="avviso avviso-idp" data-avviso-idp><strong>{escape(testa[0])}</strong> {escape(testa[1])} '
            f'<strong>{escape(FRASE_NOLEGGIO)}</strong></p>')


def box_noleggio(k=None, c=None):
    """Riquadro "Hire a car" (DiscoverCars, link di affiliazione): '' finché NOLEGGIO_AUTO è vuoto. Senza Paese (indice e pagine per patente)
    il testo è generico. Va messo dopo la risposta e le regole ufficiali (verifica.py, punto 18, controlla la posizione)."""
    if not NOLEGGIO_AUTO:
        return ""
    P = frase_srv(c) if c else ""
    avviso = avviso_noleggio_pat(k, c) if k and c else ""
    regole = "" if avviso else " " + (FRASE_NOLEGGIO if c else FRASE_NOLEGGIO.replace("rules above", "rules for your country in the table above"))
    dove = f" in {P}" if P else " abroad"
    return (f'<h2 id="hire-a-car">Hire a car{escape(dove) if P else ""}</h2>\n{avviso}'
            f'<section class="card noleggio" aria-label="Car hire, affiliate link" data-noleggio>'
            f'<p>Hiring a car{escape(dove)}? Compare rental companies and prices on DiscoverCars.{escape(regole)}</p>'
            f'<p class="noleggio-btn"><a class="btn" href="{escape(NOLEGGIO_AUTO)}" rel="sponsored noopener" target="_blank">'
            f'{ico("car")}Compare car hire{escape(" in " + P) if P else ""}</a></p>'
            f'{MON.nota_trasparenza("en")}</section>')


def home_noleggio():
    """Riga discreta "Hire a car" nella sezione Driving abroad della home (stesso link DiscoverCars): '' con NOLEGGIO_AUTO vuoto."""
    if not NOLEGGIO_AUTO:
        return ""
    return (f'<p class="altri-pass noleggio-home" data-noleggio>{ico("car")}<span>Hiring a car abroad? Check the permit rules for your country first, then '
            f'<a href="{escape(NOLEGGIO_AUTO)}" rel="sponsored noopener" target="_blank">compare car hire on DiscoverCars</a>. {MON.RIGA_EN}</span></p>')


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
{box_noleggio(k, c)}
{link_ped(rel, c)}
{link_gom(rel, c)}{link_fl(rel, c)}{link_tr_paese(rel, c)}{link_sc_pat(rel, c)}{link_pet(rel, c) if k == "uk" else ""}{link_bb(rel, c) if k == "uk" else ""}
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
{box_noleggio(k)}
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
{box_noleggio()}
{f'<p class="altri-pass">{ico("car")}<span>Hiring a car? <a href="{rel}{PED_BASE}/">How to pay tolls and vignettes with a rental car in {len(PED_PAESI)} European countries</a></span></p>' if PED else ""}
{f'<p class="altri-pass">{ico("car")}<span>Driving in winter? <a href="{rel}{GOM_BASE}/">Winter tyres and snow chains with a rental car in {len(GOM_PAESI)} European countries</a></span></p>' if GOM else ""}
{f'<p class="altri-pass">{ico("car")}<span>Staying longer or moving? <a href="{rel}{FL_BASE}/">How long you can drive on a foreign licence in Canada, Australia and New Zealand, by province and state</a></span></p>' if FL else ""}
{f'<p class="altri-pass">{ico("globe")}<span>Not driving? <a href="{rel}{TR_BASE}/">Public transport fines, validation and contactless payment in {len(TR_CITTA)} cities</a></span></p>' if TR else ""}
{f'<p class="altri-pass">{ico("car")}<span>Blue Badge holder? <a href="{rel}{BB_BASE}/">Where your UK Blue Badge is recognised in Europe, country by country</a></span></p>' if BB else ""}
{f'<p class="altri-pass">{ico("car")}<span>Renting a scooter instead? <a href="{rel}{SC_BASE}/">Moped and 125 cc on a car licence: what the official texts say in {len(SC_PAESI)} countries</a></span></p>' if SC else ""}
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
            f'<div class="griglia">{"".join(voci)}</div>{home_noleggio()}')


def about_pat(rel):
    if not PAT:
        return ""
    g = PAT["fonti"]
    return f"""<h2 id="driving-abroad">Driving abroad: international driving permits</h2>
<p>Sources: for UK licences, the GOV.UK guide “Driving abroad” (<a href="{escape(g['uk']['pagina_idp'])}" rel="noopener">check if you need an international driving permit</a>, page updated {data_lunga(g['uk']['guida_aggiornata'])}, {g['uk']['righe_tabella']} rows in the table) and the driving paragraphs of the FCDO travel advice for each country; for Canadian licences, the “Driving” part of the “Laws and culture” section of the Government of Canada travel advice (travel.gc.ca, through the official open data files) and its <a href="{escape(g['ca']['pagina_idp'])}" rel="noopener">International Driving Permit page</a>; for Australian licences, the driving paragraphs of the “Local travel” part of the Smartraveller advice for each destination, read in a browser. All read on {data_lunga(PAT['controllato_il'])}, except Smartraveller ({data_lunga(g['au']['letto_dal'])}{"" if g['au']['letto_dal'] == g['au']['letto_al'] else " to " + data_lunga(g['au']['letto_al'])}). Licences: Open Government Licence v3.0, Open Government Licence – Canada, CC BY 4.0.</p>
<p>Rules: the answer comes only from the official sentence, which we quote on the page. An answer is “IDP needed” only when the official text says you must have one, “No IDP needed” only when it says you can drive with your licence (or that you do not need an IDP), “It depends” when it sets a condition (length of stay, hiring a car, a translation, the region), “Recommended” when it says you should carry one, and “Local permit needed” when it says you need a local licence or permit. When official pages disagree, we give the more cautious answer and quote both. Where the advice is silent we write “Not stated”. Most answers are read with fixed wording rules; the rest were read one by one on 28 October 2026 and are checked again whenever the official text changes. A page for a single country and licence exists only where people search for it. This is information, not legal advice.</p>"""


# ---------------------------------------------------------------- Pedaggi con l'auto a noleggio (30/10/2026)
# Fatti scritti a mano in dati/pedaggi_manuali.json (citazioni parola per parola, prove dei prezzi), fonti rilette da raccolta/pedaggi.py
# (HTTP 200, data di lettura, impronta della zona citata) che scrive dati/pedaggi.json. Riquadro DiscoverCars (stesso NOLEGGIO_AUTO della
# sezione Driving abroad) solo DOPO le regole ufficiali. Controlli: verifica.py, punto 20.
# Dal 31/10/2026 un Paese può avere un "cambio" con data (Croazia: caselli fino al 28/2/2027, pedaggio senza caselli dal 1/3/2027 per legge):
# riquadro con le frasi nostre (box_cambio_ped), citazioni del tema "dal_2027" con traduzione, titoli dei temi per Paese ("temi_titoli").
PED_BASE = "tolls-rental-car"
_f_ped = DATI / "pedaggi.json"
PED = json.loads(_f_ped.read_text(encoding="utf-8")) if _f_ped.exists() else None
PED_PAESI = sorted(PED["paesi"], key=lambda p: p["nome"]) if PED else []
PED_PER = {p["iso2"]: p for p in PED_PAESI}
LIMITE_TITOLO_PED = 70  # come la sezione Driving abroad: fino a 70 caratteri con l'anno
TEMI_PED = [("come", "How you pay"), ("dal_2027", "Changes already set by law"), ("prezzo", "Prices"), ("scadenza", "When and where to pay"), ("multa", "If you do not pay"), ("altro", "Also on the official pages")]


def url_ped(c=None):
    return f"{PED_BASE}/" + (f"{slug_srv(c)}/" if c else "")


def fonti_ped(p):
    """Fonti usate da un Paese, nell'ordine della prima citazione."""
    out = []
    for x in [c["f"] for c in p["citazioni"]] + [pr["f"] for pr in p.get("prezzi", [])]:
        if x not in out:
            out.append(x)
    return out


def data_ped(p):
    return max(PED["fonti"][f]["letto_il"] for f in fonti_ped(p))


def cit_ped(p, id_):
    return next(c for c in p["citazioni"] if c["id"] == id_)


def link_fonte_ped(fid):
    F = PED["fonti"][fid]
    return f'<a href="{escape(F["pagina"])}" rel="noopener">{escape(F["titolo"])}</a>'


def blocco_cit_ped(p, cc):
    """Citazioni ufficiali raggruppate per fonte: virgolette, traduzione nostra (se la fonte non è in inglese), fonte e data."""
    out, gruppi = [], []
    for c in cc:
        if gruppi and gruppi[-1][0] == c["f"]:
            gruppi[-1][1].append(c)
        else:
            gruppi.append((c["f"], [c]))
    tr = p.get("traduzioni", {})
    for fid, gg in gruppi:
        F = PED["fonti"][fid]
        h = "".join(f"<p>{escape(c['x'])}</p>" + (f'<p class="trad" lang="en"><em>Our translation:</em> {escape(tr[c["id"]])}</p>' if c["id"] in tr else "")
                    for c in gg)
        lingua = f' lang="{F["lingua"]}"' if F["lingua"] != "en" else ""
        out.append(f'<blockquote class="cit"{lingua}>{h}</blockquote><p class="fonte">Source: {link_fonte_ped(fid)} ({escape(F["ente"])}), '
                   f'checked on {data_lunga(F["letto_il"])}. Quoted word for word.</p>')
    return "".join(out)


def risposta_ped(p):
    """Prima frase: chi lo dice, quando, la risposta (sez. 7 del rapporto del 28/10: fonte e data nella prima frase)."""
    return f"According to {p['chi']}, checked on {data_lunga(data_ped(p))}, {p['risposta']}"


NOLEGGIO_NON_DETTO_PED = ("The official pages we read do not mention rental cars. Before you book, ask the rental company whether the car has a toll tag "
                          "and how it charges you for tolls and any fees.")
NOLEGGIO_NON_DETTO_VIG = ("The official pages we read do not say whether rental cars come with a vignette. Before you book, ask the rental company whether "
                          "the car will have a valid vignette for the dates of your trip.")


def sezione_noleggio_ped(p):
    cc = [c for c in p["citazioni"] if c["tema"] == "noleggio"]
    if p["noleggio"] == "detto":
        enti = list(dict.fromkeys(PED["fonti"][c["f"]]["ente"] for c in cc))  # chi lo dice davvero: l'ente delle fonti citate (accordo del verbo)
        chi = " and ".join(enti)
        return f"<p>{escape(chi)} {'says' if len(enti) == 1 else 'say'} this about rental cars:</p>{blocco_cit_ped(p, cc)}"
    testo = NOLEGGIO_NON_DETTO_VIG if p["vignetta"] else NOLEGGIO_NON_DETTO_PED
    extra = f"<p>{escape(p.get('noleggio_pre') or 'The official site also says:')}</p>{blocco_cit_ped(p, cc)}" if cc else ""
    return f'<p data-nol-non-detto>{escape(testo)}</p>{extra}'


def tabella_prezzi_ped(p):
    if not p.get("prezzi"):
        return ""
    righe = "".join(f'<tr><td data-l="Item">{escape(pr["voce"])}</td><td data-l="Price"><strong>{escape(pr["importo"])}</strong></td>'
                    f'<td data-l="Source">{link_fonte_ped(pr["f"])}</td></tr>' for pr in p["prezzi"])
    return (f'<h2 id="prices">Official prices</h2><div class="tab tab-b"><table><caption class="cap">Official prices for a car in {escape(p["nome_frase"])}, '
            f'read on {data_lunga(data_ped(p))}</caption><thead><tr><th>Item</th><th>Price</th><th>Source</th></tr></thead><tbody>{righe}</tbody></table></div>')


def faq_ped(p):
    out = []
    for f in p["faq"]:
        parti = ([f["pre"]] if f["pre"] else []) + [f"“{cit_ped(p, i)['x']}”" for i in f["cit"]] + ([f["post"]] if f["post"] else [])
        out.append((f["q"], " ".join(parti)))
    out.append(("Where does this answer come from?", f"From the official pages of {p['chi']}, read on {data_lunga(data_ped(p))} and quoted word for word on "
                                                     "this page. It is information, not legal advice."))
    return out


def html_faq_ped(p):
    faq = faq_ped(p)
    h = "".join(f"<h3>{escape(q)}</h3><p>{escape(a)}</p>" for q, a in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    return f'<section class="faq"><h2>Questions</h2>{h}</section>', [ld]


AVVISO_PED = ('<p class="avviso"><strong>Prices and rules change, and each rental company has its own toll fees.</strong> We quote the motorway operators and '
              'governments word for word, with the date we checked them; this is information, not legal advice. Before you drive, check the official page '
              'and ask the rental company how it charges you for tolls.</p>')
FRASE_NOLEGGIO_PED = {"pedaggio": "Before you book, ask how each company charges you for tolls.",
                      "vignetta": "Before you book, ask whether the car comes with a valid vignette for your dates.",
                      "indice": "Before you book, ask how each company charges you for tolls or a vignette."}


def box_noleggio_ped(c=None):
    """Riquadro "Hire a car" (DiscoverCars) per la sezione pedaggi: '' con NOLEGGIO_AUTO vuoto. Sempre dopo le regole ufficiali."""
    if not NOLEGGIO_AUTO:
        return ""
    P = PED_PER[c]["nome_frase"] if c else ""
    dove = f" in {P}" if P else " in Europe"
    frase = FRASE_NOLEGGIO_PED[("vignetta" if PED_PER[c]["vignetta"] else "pedaggio") if c else "indice"]
    return (f'<h2 id="hire-a-car">Hire a car{escape(dove)}</h2>'
            f'<section class="card noleggio" aria-label="Car hire, affiliate link" data-noleggio>'
            f'<p>Hiring a car{escape(dove)}? Compare rental companies and prices on DiscoverCars. {escape(frase)}</p>'
            f'<p class="noleggio-btn"><a class="btn" href="{escape(NOLEGGIO_AUTO)}" rel="sponsored noopener" target="_blank">'
            f'{ico("car")}Compare car hire{escape(" in " + P) if P else ""}</a></p>'
            f'{MON.nota_trasparenza("en")}</section>')


def link_ped(rel, c):
    """Riga 'Tolls in X with a rental car' (pagine Driving abroad dello stesso Paese)."""
    p = PED_PER.get(c)
    if not p:
        return ""
    cosa = "vignette and tolls" if p["vignetta"] else "tolls"
    return (f'<p class="altri-pass">{ico("car")}<span>Hiring a car in {escape(p["nome_frase"])}? '
            f'<a href="{rel}{url_ped(c)}">How to pay {cosa} in {escape(p["nome_frase"])} with a rental car</a></span></p>')


def h1_ped(p):
    if p["vignetta"]:
        n = len(p.get("prezzi", []))
        cosa = "Prices and rules" if n > 1 else ("Price and rules" if n == 1 else "Rules and what to check")  # niente "prezzi" senza prezzi letti
        return f"Do you need a vignette in {p['nome_frase']} with a rental car? {cosa} ({ANNO})"
    return f"How to pay tolls in {p['nome_frase']} with a rental car ({ANNO})"


def descrizione_ped(p):
    d = data_lunga(data_ped(p))
    cosa = "Vignette" if p["vignetta"] else "Tolls"
    come = p["come"][0].lower() + p["come"][1:] if p["come"][1:2].islower() else p["come"]  # "M50 (Dublin)" resta com'è
    return scegli([f"{cosa} in {p['nome_frase']} with a rental car – {come}. Official sources quoted, checked on {d}.",
                   f"{cosa} in {p['nome_frase']} with a rental car: how to pay, prices and rules from official sources, checked on {d}.",
                   f"{cosa} in {p['nome_frase']} with a rental car, from official sources ({d})."], LIMITE_DESCRIZIONE)


def box_cambio_ped(p):
    """Riquadro "dal giorno X (per legge)": frasi nostre, ognuna ripresa dalle citazioni sotto (Croazia dal 1/3/2027). '' senza cambio."""
    C = p.get("cambio")
    if not C:
        return ""
    fonti = [f for f in fonti_ped(p) if any(x["f"] == f and x["tema"] in ("dal_2027", "noleggio") for x in p["citazioni"])]
    righe = "".join(f"<li>{escape(x)}</li>" for x in C["frasi"])
    return (f'<section class="card cambio" aria-labelledby="change" data-cambio="{C["dal"]}"><h2 id="change">{escape(C["titolo"])}</h2><ul>{righe}</ul>'
            f'<p class="small">Our summary of the official texts quoted below: {", ".join(link_fonte_ped(f) for f in fonti)}, '
            f'checked on {data_lunga(max(PED["fonti"][f]["letto_il"] for f in fonti))}.</p></section>')


def pagina_ped(p):
    rel = "../../"
    c = p["iso2"]
    titoli_temi = {**dict(TEMI_PED), **p.get("temi_titoli", {})}
    temi = "".join(f'<h3>{escape(titoli_temi[k])}</h3>{blocco_cit_ped(p, [x for x in p["citazioni"] if x["tema"] == k])}'
                   for k, _ in TEMI_PED if any(x["tema"] == k for x in p["citazioni"]))
    sguardo = (f'<tr><th scope="row">How you pay</th><td>{escape(p["come"])}</td></tr>'
               f'<tr><th scope="row">Vignette</th><td>{"Yes" if p["vignetta"] else "No: tolls are charged per trip"}</td></tr>'
               f'<tr><th scope="row">Price for a car</th><td>{escape(p["prezzo_breve"])}</td></tr>'
               f'<tr><th scope="row">Rental cars</th><td>{escape(p["noleggio_breve"])}</td></tr>'
               f'<tr><th scope="row">Checked</th><td>{data_lunga(data_ped(p))}</td></tr>')
    altri = "".join(f'<a href="{rel}{url_ped(q["iso2"])}">{escape(q["nome"])}<small>{"Vignette" if q["vignetta"] else "Tolls per trip"}</small></a>'
                    for q in PED_PAESI if q["iso2"] != c)
    guida = link_guida(rel, c)
    faq_h, faq_ld = html_faq_ped(p)
    corpo = f"""<section class="hero">{h1_diviso(h1_ped(p))}</section>
<section class="card summary" aria-label="Answer">
<div class="s-top"><span class="sq">{ico("car")}</span><span>{"Vignette" if p["vignetta"] else "Tolls"} · {escape(p["nome"])}</span><span>{ANNO}</span></div>
<div class="s-body">
<p class="lead" id="answer">{escape(risposta_ped(p))}</p>
{f'<p class="small">{escape(p["nota"])}</p>' if p.get("nota") else ""}
</div></section>
{box_cambio_ped(p)}
{AVVISO_PED}
<h2>At a glance</h2>
<div class="tab tab-g"><table><caption class="cap">Tolls in {escape(p["nome_frase"])} with a rental car: summary of the official sources, checked on {data_lunga(data_ped(p))}</caption><tbody>{sguardo}</tbody></table></div>
{tabella_prezzi_ped(p)}
<h2 id="official">What the official sources say</h2>
{temi}
<h2 id="rental">With a rental car</h2>
{sezione_noleggio_ped(p)}
{AD}
{box_noleggio_ped(c)}
{f'<h2>Driving in {escape(p["nome_frase"])} with your licence</h2>{guida}' if guida else ""}
{link_gom(rel, c)}
{link_pet(rel, c)}
<h2>Other countries</h2>
<div class="griglia">{altri}</div>
{faq_h}
<p class="small">Spotted a change? <a href="{rel}contact/?ref=tolls-rental-car">Tell us</a>. <a href="{rel}{PED_BASE}/">Tolls with a rental car: all countries</a>.</p>"""
    pagina(url_ped(c), scegli([p["titolo"]], LIMITE_TITOLO_PED), descrizione_ped(p), corpo,
           briciole=[("Tolls with a rental car", f"{PED_BASE}/"), (p["nome"], url_ped(c))], ld_extra=faq_ld)
    LASTMOD[url_ped(c)] = data_ped(p)


def prima_frase_ped():
    v = [p for p in PED_PAESI if p["vignetta"]]
    t = [p for p in PED_PAESI if not p["vignetta"]]
    elenco = lambda pp: ", ".join(p["nome"] for p in pp[:-1]) + " and " + pp[-1]["nome"]
    return (f"Of the {len(PED_PAESI)} European countries on this page, {len(v)} use a vignette for cars on their motorways ({elenco(v)}) and {len(t)} charge "
            f"tolls per trip, at toll booths or by camera ({elenco(t)}); for each one we quote the motorway operator or the government, last checked on "
            f"{data_lunga(PED['controllato_il'])}.")


def titolo_indice_ped():
    return f"Tolls with a Rental Car in Europe: How to Pay, {len(PED_PAESI)} Countries ({ANNO})"


def pagina_indice_ped():
    rel = "../"
    righe = "".join(f'<tr data-voce id="{p["iso2"].lower()}"><td data-l="Country"><a href="{rel}{url_ped(p["iso2"])}">{escape(p["nome"])}</a></td>'
                    f'<td data-l="How you pay">{escape(p["come"])}</td><td data-l="Vignette">{"Yes" if p["vignetta"] else "No"}</td>'
                    f'<td data-l="Price for a car">{escape(p["prezzo_breve"])}</td><td data-l="Rental cars">{escape(p["noleggio_breve"])}</td>'
                    f'<td data-l="Checked">{data_lunga(data_ped(p))}</td></tr>' for p in PED_PAESI)
    griglia = "".join(f'<a href="{rel}{url_ped(p["iso2"])}">{escape(p["nome"])}<small>{escape("Vignette" if p["vignetta"] else "Tolls per trip")}</small></a>' for p in PED_PAESI)
    d = data_lunga(PED["controllato_il"])
    corpo = f"""<section class="hero">{h1_diviso(f"Tolls with a rental car in Europe: how to pay, country by country ({ANNO})")}
<p class="lead" id="answer">{escape(prima_frase_ped())}</p></section>
<div class="griglia">{griglia}</div>
{AVVISO_PED}
{AD}
<h2>Every country</h2>
<p>“How you pay”, “Price for a car” and “Rental cars” are our short summaries; each country page quotes the official sentences, with the link and the date. “Not mentioned” means that the official pages we read say nothing about rental cars.</p>
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Type a country, e.g. Portugal" data-filtro-multi aria-label="Search countries"></div>
<div class="tab tab-b tab-srv"><table><caption class="cap">Tolls and vignettes with a rental car in {len(PED_PAESI)} European countries, from official sources, checked on {d}</caption><thead><tr><th>Country</th><th>How you pay</th><th>Vignette</th><th>Price for a car</th><th>Rental cars</th><th>Checked</th></tr></thead><tbody>{righe}</tbody></table></div>
{box_noleggio_ped()}
<h2>How we check</h2>
<p>We read the pages of each motorway operator or government (for example Infraestruturas de Portugal, Transport Infrastructure Ireland, AutoPASS, Autostrade per l'Italia, ASFINAG and the Swiss Federal Office for Customs and Border Security) and quote them word for word. A price appears only if we read it on an official page that answered normally on the day of the check; otherwise we say so. We write that a rule is about rental cars only when the official text says so. More on the <a href="{rel}about/#tolls-rental-car">About page</a>. Spotted a change? <a href="{rel}contact/?ref=tolls-rental-car">Tell us</a>.</p>
<p><a href="{rel}{PAT_BASE}/">Driving abroad: do you need an international driving permit?</a>{f' · <a href="{rel}{GOM_BASE}/">Winter tyres and snow chains with a rental car</a>' if GOM else ''}</p>"""
    desc = scegli([f"How to pay tolls and vignettes with a rental car in {len(PED_PAESI)} European countries, from motorway operators and governments, checked on {d}.",
                   f"Tolls and vignettes with a rental car in {len(PED_PAESI)} European countries, from official sources."], LIMITE_DESCRIZIONE)
    pagina(f"{PED_BASE}/", scegli([titolo_indice_ped(), f"Tolls with a Rental Car in Europe ({ANNO})"], LIMITE_TITOLO_PED), desc, corpo,
           briciole=[("Tolls with a rental car", f"{PED_BASE}/")], js=APP_JS_FILTRO)
    LASTMOD[f"{PED_BASE}/"] = PED["controllato_il"]


def home_ped():
    if not PED:
        return ""
    voci = "".join(f'<a href="{url_ped(p["iso2"])}">{escape(p["nome"])}<small>{escape("Vignette" if p["vignetta"] else "Tolls per trip")}</small></a>' for p in PED_PAESI)
    return (f'<h2>Tolls with a rental car</h2><p>How to pay motorway tolls or buy a vignette in {len(PED_PAESI)} European countries, and what the official '
            f'sources say about rental cars: <a href="{PED_BASE}/">every country in one table</a>.</p><div class="griglia">{voci}</div>')


def about_ped(rel):
    if not PED:
        return ""
    enti = []
    for F in PED["fonti"].values():
        if F["ente"] not in enti:
            enti.append(F["ente"])
    return f"""<h2 id="tolls-rental-car">Tolls with a rental car</h2>
<p>Sources: the pages of the motorway operators and governments of {len(PED_PAESI)} European countries ({escape(", ".join(enti))}), {len(PED["fonti"])} pages in all, read on {data_lunga(PED["controllato_il"])}. Each country page links every page it quotes.</p>
<p>Rules: every sentence shown between quotation marks is copied word for word from the official page, and every price comes with the text that contains it. A price appears only if the official page answered normally on the day we checked it. We write that a rule is about rental cars only when the official text says so; otherwise the page says that the source does not mention rental cars. French and Spanish pages are quoted in the original language with our translation. We do not cover the toll programmes of rental companies, whose prices are commercial terms that we cannot check reliably. This is information, not legal advice.</p>"""


# ---------------------------------------------------------------- Gomme invernali e catene con l'auto a noleggio (30/10/2026)
# Fatti scritti a mano in dati/gomme_manuali.json (citazioni parola per parola, traduzioni nostre), fonti rilette da raccolta/gomme.py
# (HTTP 200, data di lettura, impronta della zona citata) che scrive dati/gomme.json. Pagina Paese solo con ricerche vere (gomme.json, "pagine").
# Riquadro DiscoverCars (stesso NOLEGGIO_AUTO) solo DOPO le regole ufficiali. Controlli: verifica.py, punto 21. Ricontrollo ogni ottobre.
GOM_BASE = "winter-tyres-rental-car"
_f_gom = DATI / "gomme.json"
GOM = json.loads(_f_gom.read_text(encoding="utf-8")) if _f_gom.exists() else None
GOM_PAESI = sorted(GOM["paesi"], key=lambda p: p["nome"]) if GOM else []
GOM_PER = {p["iso2"]: p for p in GOM_PAESI}
GOM_PAGINE = set(GOM["pagine"]) if GOM else set()
STAGIONE_GOM = "2026-27"  # stagione invernale nei titoli (la regola vale da novembre ad aprile)
LIMITE_TITOLO_GOM = 70
TEMI_GOM = [("quando", "When the rule applies"), ("dove", "Where it applies"), ("gomme", "Which tyres count"), ("catene", "Snow chains"),
            ("multa", "Fines and liability"), ("altro", "Also on the official pages")]
OBBLIGO_GOM = {"si": "Yes, on set dates", "situazionale": "Only in winter conditions", "no": "No"}
CLASSE_GOM = {"si": "manuale", "situazionale": "manuale", "no": "si"}
LINGUE_GOM = {"it": "Italian", "de": "German", "fr": "French", "sl": "Slovenian", "hr": "Croatian", "cs": "Czech", "sk": "Slovak", "es": "Spanish", "ca": "Catalan"}
FRASE_NOLEGGIO_GOM = "Ask the rental company whether winter tyres or chains are included and at what cost."
NOLEGGIO_NON_DETTO_GOM = "The official pages we read do not say whether rental cars come with winter tyres or chains. " + FRASE_NOLEGGIO_GOM


def url_gom(c=None):
    return f"{GOM_BASE}/" + (f"{slug_srv(c)}/" if c else "")


def ha_pagina_gom(c):
    return c in GOM_PER and c in GOM_PAGINE


def fonti_gom(p):
    out = []
    for c in p["citazioni"]:
        if c["f"] not in out:
            out.append(c["f"])
    return out


def enti_gom(p):
    """(ente, prima fonte di quell'ente) per la colonna "Source" dell'indice: un link per ente."""
    out = {}
    for f in fonti_gom(p):
        out.setdefault(GOM["fonti"][f]["ente"], f)
    return list(out.items())


def data_gom(p):
    return max(GOM["fonti"][f]["letto_il"] for f in fonti_gom(p))


def cit_gom(p, id_):
    return next(c for c in p["citazioni"] if c["id"] == id_)


def link_fonte_gom(fid, rel_titolo=None):
    F = GOM["fonti"][fid]
    return f'<a href="{escape(F["pagina"])}" rel="noopener">{escape(rel_titolo or F["titolo"])}</a>'


def blocco_cit_gom(p, cc):
    """Citazioni ufficiali raggruppate per fonte: virgolette, traduzione nostra (se la fonte non è in inglese), fonte e data."""
    out, gruppi = [], []
    for c in cc:
        if gruppi and gruppi[-1][0] == c["f"]:
            gruppi[-1][1].append(c)
        else:
            gruppi.append((c["f"], [c]))
    tr = p.get("traduzioni", {})
    for fid, gg in gruppi:
        F = GOM["fonti"][fid]
        h = "".join(f"<p>{escape(c['x'])}</p>" + (f'<p class="trad" lang="en"><em>Our translation:</em> {escape(tr[c["id"]])}</p>' if c["id"] in tr else "")
                    for c in gg)
        lingua = f' lang="{F["lingua"]}"' if F["lingua"] != "en" else ""
        out.append(f'<blockquote class="cit"{lingua}>{h}</blockquote><p class="fonte">Source: {link_fonte_gom(fid)} ({escape(F["ente"])}), '
                   f'checked on {data_lunga(F["letto_il"])}. Quoted word for word.</p>')
    return "".join(out)


def risposta_gom(p):
    """Prima frase: chi lo dice, quando, la risposta."""
    return f"According to {p['chi']}, checked on {data_lunga(data_gom(p))}, {p['risposta']}"


def testo_cit_gom(p, id_):
    """Testo di una citazione per le FAQ: in inglese (la frase ufficiale, o la nostra traduzione dichiarata nella domanda)."""
    c = cit_gom(p, id_)
    return p.get("traduzioni", {}).get(id_) or c["x"]


def faq_gom(p):
    out = []
    for f in p["faq"]:
        parti = ([f["pre"]] if f["pre"] else []) + [f"“{testo_cit_gom(p, i).strip('“”')}”" for i in f["cit"]] + ([f["post"]] if f["post"] else [])
        out.append((f["q"], " ".join(parti)))
    out.append((f"Does a rental car in {p['nome_frase']} come with winter tyres or snow chains?", NOLEGGIO_NON_DETTO_GOM))
    out.append(("Where does this answer come from?", f"From the official pages of {p['chi']}, read on {data_lunga(data_gom(p))} and quoted word for word "
                                                     "on this page (with our translation when the page is not in English). It is information, not legal advice."))
    return out


def html_faq_gom(faq):
    h = "".join(f"<h3>{escape(q)}</h3><p>{escape(a)}</p>" for q, a in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    return f'<section class="faq"><h2>Questions</h2>{h}</section>', [ld]


AVVISO_GOM = ('<p class="avviso"><strong>Local orders and road signs come first.</strong> We quote governments, police forces and road safety agencies '
              'word for word, with the date we checked them; this is information, not legal advice. Before you drive, check the signs on your route '
              'and ask the rental company whether winter tyres or chains are included and at what cost.</p>')


def box_noleggio_gom(c=None):
    """Riquadro "Hire a car" (DiscoverCars) per la sezione gomme: '' con NOLEGGIO_AUTO vuoto. Sempre dopo le regole ufficiali."""
    if not NOLEGGIO_AUTO:
        return ""
    P = GOM_PER[c]["nome_frase"] if c else ""
    dove = f" in {P}" if P else " in Europe"
    return (f'<h2 id="hire-a-car">Hire a car{escape(dove)}</h2>'
            f'<section class="card noleggio" aria-label="Car hire, affiliate link" data-noleggio>'
            f'<p>Hiring a car{escape(dove)} this winter? Compare rental companies and prices on DiscoverCars. Before you book, '
            f'{escape(FRASE_NOLEGGIO_GOM[0].lower() + FRASE_NOLEGGIO_GOM[1:])}</p>'
            f'<p class="noleggio-btn"><a class="btn" href="{escape(NOLEGGIO_AUTO)}" rel="sponsored noopener" target="_blank">'
            f'{ico("car")}Compare car hire{escape(" in " + P) if P else ""}</a></p>'
            f'{MON.nota_trasparenza("en")}</section>')


def link_gom(rel, c):
    """Riga 'Winter tyres in X with a rental car' (pagine Driving abroad e Tolls dello stesso Paese)."""
    if not ha_pagina_gom(c):
        return ""
    p = GOM_PER[c]
    return (f'<p class="altri-pass">{ico("car")}<span>Driving in {escape(p["nome_frase"])} this winter? '
            f'<a href="{rel}{url_gom(c)}">Winter tyres and snow chains in {escape(p["nome_frase"])} with a rental car</a></span></p>')


def h1_gom(p):
    return f"Winter tyres and snow chains in {p['nome_frase']} with a rental car ({STAGIONE_GOM})"


def descrizione_gom(p):
    d = data_lunga(data_gom(p))
    ob = OBBLIGO_GOM[p["obbligo"]]
    per = p["periodo_breve"]
    per = per[:1].lower() + per[1:]  # "No legal period" -> "no legal period" dopo la virgola
    return scegli([f"Winter tyres and snow chains in {p['nome_frase']} with a rental car: {ob.lower()}, {per}. Official sources, checked on {d}.",
                   f"Winter tyres and snow chains in {p['nome_frase']} with a rental car: dates and rules from official sources, checked on {d}.",
                   f"Winter tyres and snow chains in {p['nome_frase']} with a rental car, from official sources ({d})."], LIMITE_DESCRIZIONE)


def pagina_gom(p):
    rel = "../../"
    c = p["iso2"]
    temi = "".join(f'<h3>{escape(t)}</h3>{blocco_cit_gom(p, [x for x in p["citazioni"] if x["tema"] == k])}'
                   for k, t in TEMI_GOM if any(x["tema"] == k for x in p["citazioni"]))
    sguardo = (f'<tr><th scope="row">Obligation</th><td>{escape(OBBLIGO_GOM[p["obbligo"]])} – {escape(p["obbligo_breve"])}</td></tr>'
               f'<tr><th scope="row">Period</th><td>{escape(p["periodo_breve"])}</td></tr>'
               f'<tr><th scope="row">Snow chains</th><td>{escape(p["catene_breve"])}</td></tr>'
               f'<tr><th scope="row">Rental cars</th><td>Not covered by the official pages: ask the rental company</td></tr>'
               f'<tr><th scope="row">Checked</th><td>{data_lunga(data_gom(p))}</td></tr>')
    altri = "".join(f'<a href="{rel}{url_gom(q["iso2"])}">{escape(q["nome"])}<small>{escape(OBBLIGO_GOM[q["obbligo"]])}</small></a>'
                    for q in GOM_PAESI if q["iso2"] != c and ha_pagina_gom(q["iso2"]))
    guida = link_guida(rel, c)
    pedaggi = link_ped(rel, c)
    faq_h, faq_ld = html_faq_gom(faq_gom(p))
    corpo = f"""<section class="hero">{h1_diviso(h1_gom(p))}</section>
<section class="card summary" aria-label="Answer">
<div class="s-top"><span class="sq">{ico("car")}</span><span>Winter tyres · {escape(p["nome"])}</span><span>{STAGIONE_GOM}</span></div>
<div class="s-body">
<div class="esito e-srv {CLASSE_GOM[p["obbligo"]]}">{ico("check" if p["obbligo"] == "no" else "alert")}<strong>{escape(OBBLIGO_GOM[p["obbligo"]])} – {escape(p["obbligo_breve"])}</strong></div>
<p class="lead" id="answer">{escape(risposta_gom(p))}</p>
{f'<p class="small">{escape(p["nota"])}</p>' if p.get("nota") else ""}
</div></section>
{AVVISO_GOM}
<h2>At a glance</h2>
<div class="tab tab-g"><table><caption class="cap">Winter tyres and snow chains in {escape(p["nome_frase"])}: summary of the official sources, checked on {data_lunga(data_gom(p))}</caption><tbody>{sguardo}</tbody></table></div>
<h2 id="official">What the official sources say</h2>
{temi}
<h2 id="rental">With a rental car</h2>
<p data-nol-non-detto>{escape(NOLEGGIO_NON_DETTO_GOM)}</p>
{AD}
{box_noleggio_gom(c)}
{f'<h2>More for drivers in {escape(p["nome_frase"])}</h2>{guida}{pedaggi}' if guida or pedaggi else ""}
<h2>Other countries</h2>
<div class="griglia">{altri}</div>
{faq_h}
<p class="small">Spotted a change? <a href="{rel}contact/?ref=winter-tyres-rental-car">Tell us</a>. <a href="{rel}{GOM_BASE}/">Winter tyres with a rental car: all countries</a>.</p>"""
    pagina(url_gom(c), scegli([p["titolo"]], LIMITE_TITOLO_GOM), descrizione_gom(p), corpo,
           briciole=[("Winter tyres with a rental car", f"{GOM_BASE}/"), (p["nome"], url_gom(c))], ld_extra=faq_ld)
    LASTMOD[url_gom(c)] = data_gom(p)


def vecchie_gom():
    """Paesi la cui fonte più recente è di un inverno passato (campo fonte_vecchia in gomme_manuali.json): avviso nell'indice."""
    vv = [p for p in GOM_PAESI if p.get("fonte_vecchia")]
    if not vv:
        return ""
    return (f" For {elenco_gom(vv)} the newest official page we found was written for an earlier winter: "
            "the country page gives its date, so check the rule again before you travel.")


def elenco_gom(pp):
    nomi = [p["nome"] for p in pp]
    return nomi[0] if len(nomi) == 1 else ", ".join(nomi[:-1]) + " and " + nomi[-1]


def prima_frase_gom():
    g = {k: [p for p in GOM_PAESI if p["obbligo"] == k] for k in OBBLIGO_GOM}
    verbo = "has" if len(g["no"]) == 1 else "have"
    return (f"Of the {len(GOM_PAESI)} European countries on this page, {len(g['si'])} require winter tyres or snow chains on set dates, in some of them "
            f"only on signed roads or in signed areas ({elenco_gom(g['si'])}), {len(g['situazionale'])} only in winter road conditions "
            f"({elenco_gom(g['situazionale'])}) and {len(g['no'])} {verbo} no obligation ({elenco_gom(g['no'])}); for each one we quote the government, "
            f"the police or the road safety agency, last checked on {data_lunga(GOM['controllato_il'])}.")


def titolo_indice_gom():
    return f"Winter Tyres and Snow Chains with a Rental Car in Europe ({STAGIONE_GOM})"


def faq_indice_gom():
    M = json.loads((DATI / "gomme_manuali.json").read_text(encoding="utf-8"))
    it = GOM_PER.get("IT")
    risposte = {
        "do rental cars come with snow chains": f"None of the official pages we read for these {len(GOM_PAESI)} countries says whether rental cars come with "
                                                f"winter tyres or snow chains. {FRASE_NOLEGGIO_GOM}",
        "can you put snow chains on a rental car": "The official pages we read do not cover this. Ask the rental company whether chains are included, "
                                                   "whether you may fit them and at what cost.",
        "winter tyres car rental italy": ("The Italian official pages we read do not mention rental cars. In Italy the rule depends on the road: winter tyres, "
                                          "or snow chains on board, where a local order and road signs require them, and a Ministry directive sets the "
                                          f"period of these orders between 15 November and 15 April. {FRASE_NOLEGGIO_GOM}") if it else FRASE_NOLEGGIO_GOM,
    }
    return [(f["q"], risposte[f["query"]]) for f in M.get("faq_indice", []) if f["query"] in risposte]


def pagina_indice_gom():
    rel = "../"
    righe = []
    for p in GOM_PAESI:
        nome = (f'<a href="{rel}{url_gom(p["iso2"])}">{escape(p["nome"])}</a>' if ha_pagina_gom(p["iso2"]) else escape(p["nome"]))
        fonti = " · ".join(f'<a href="{escape(GOM["fonti"][f]["pagina"])}" rel="noopener">{escape(e)}</a>' for e, f in enti_gom(p))
        righe.append(f'<tr data-voce id="{p["iso2"].lower()}"><td data-l="Country">{nome}</td>'
                     f'<td data-l="Obligation"><strong>{escape(OBBLIGO_GOM[p["obbligo"]])}</strong> – {escape(p["obbligo_breve"])}</td>'
                     f'<td data-l="Period">{escape(p["periodo_breve"])}</td><td data-l="Snow chains">{escape(p["catene_breve"])}</td>'
                     f'<td data-l="Rental cars">Not covered</td><td data-l="Source">{fonti}</td>'
                     f'<td data-l="Checked">{data_lunga(data_gom(p))}</td></tr>')
    griglia = "".join(f'<a href="{rel}{url_gom(p["iso2"])}">{escape(p["nome"])}<small>{escape(OBBLIGO_GOM[p["obbligo"]])}</small></a>'
                      for p in GOM_PAESI if ha_pagina_gom(p["iso2"]))
    d = data_lunga(GOM["controllato_il"])
    faq_h, faq_ld = html_faq_gom(faq_indice_gom())
    corpo = f"""<section class="hero">{h1_diviso(f"Winter tyres and snow chains with a rental car in Europe ({STAGIONE_GOM})")}
<p class="lead" id="answer">{escape(prima_frase_gom())}</p></section>
<div class="griglia">{griglia}</div>
{AVVISO_GOM}
{AD}
<h2>Every country</h2>
<p>“Obligation”, “Period” and “Snow chains” are our short summaries; each country page quotes the official sentences, with the link and the date. “Not covered” means that the official pages we read do not say whether rental cars come with winter tyres or chains.{vecchie_gom()}</p>
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Type a country, e.g. Austria" data-filtro-multi aria-label="Search countries"></div>
<div class="tab tab-b tab-srv"><table><caption class="cap">Winter tyres and snow chains in {len(GOM_PAESI)} European countries, from official sources, checked on {d}</caption><thead><tr><th>Country</th><th>Obligation</th><th>Period</th><th>Snow chains</th><th>Rental cars</th><th>Source</th><th>Checked</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>
{box_noleggio_gom()}
{faq_h}
<h2>How we check</h2>
<p>We read the pages of ministries, police forces, road safety agencies and government portals (for example the Italian Ministry of Infrastructure and Transport, the Austrian transport ministry, Service-Public.fr, ch.ch, Statens vegvesen and Transportstyrelsen) and quote them word for word; pages in other languages are quoted in the original with our English translation. A country is listed only if its official page answered normally on the day of the check, and we say what we could not read. We write that a rule is about rental cars only when the official text says so: none of the pages we read does. We check every source again each October, before the winter season. More on the <a href="{rel}about/#winter-tyres-rental-car">About page</a>. Spotted a change? <a href="{rel}contact/?ref=winter-tyres-rental-car">Tell us</a>.</p>
<p><a href="{rel}{PAT_BASE}/">Driving abroad: do you need an international driving permit?</a> · <a href="{rel}{PED_BASE}/">Tolls with a rental car</a></p>"""
    desc = scegli([f"Winter tyres and snow chains with a rental car in {len(GOM_PAESI)} European countries: dates and rules from official sources, checked on {d}.",
                   f"Winter tyres and snow chains with a rental car in {len(GOM_PAESI)} European countries, from official sources."], LIMITE_DESCRIZIONE)
    pagina(f"{GOM_BASE}/", scegli([titolo_indice_gom(), f"Winter Tyres with a Rental Car in Europe ({STAGIONE_GOM})"], LIMITE_TITOLO_GOM), desc, corpo,
           briciole=[("Winter tyres with a rental car", f"{GOM_BASE}/")], js=APP_JS_FILTRO, ld_extra=faq_ld)
    LASTMOD[f"{GOM_BASE}/"] = GOM["controllato_il"]


def home_gom():
    if not GOM:
        return ""
    voci = "".join(f'<a href="{url_gom(p["iso2"])}">{escape(p["nome"])}<small>{escape(OBBLIGO_GOM[p["obbligo"]])}</small></a>'
                   for p in GOM_PAESI if ha_pagina_gom(p["iso2"]))
    return (f'<h2>Winter tyres and snow chains with a rental car</h2><p>When winter tyres or snow chains are required in {len(GOM_PAESI)} European '
            f'countries this winter, from official sources: <a href="{GOM_BASE}/">every country in one table</a>.</p><div class="griglia">{voci}</div>')


def about_gom(rel):
    if not GOM:
        return ""
    enti = list(dict.fromkeys(F["ente"] for F in GOM["fonti"].values()))
    return f"""<h2 id="winter-tyres-rental-car">Winter tyres and snow chains with a rental car</h2>
<p>Sources: the pages of ministries, police forces, road safety agencies and government portals of {len(GOM_PAESI)} European countries ({escape(", ".join(enti))}), {len(GOM["fonti"])} pages in all, read on {data_lunga(GOM["controllato_il"])}. Each country page links every page it quotes.</p>
<p>Rules: every sentence shown between quotation marks is copied word for word from the official page; pages in other languages are quoted in the original language with our English translation. A country is listed only if its official page answered normally on the day we checked it; where we could not read a source (for example the ANAS website in Italy), the page says so. We write that a rule is about rental cars only when the official text says so; otherwise the page says that the official pages do not say whether rental cars come with winter tyres or chains. We check every source again each October, before the winter season. This is information, not legal advice.</p>"""


# ---------------------------------------------------------------- Quando escono i biglietti delle grandi attrazioni (30/10/2026)
# Regole scritte a mano in dati/biglietti_manuali.json (citazioni parola per parola), fonti rilette da raccolta/biglietti.py (HTTP 200, data di
# lettura, impronta della zona citata) che scrive dati/biglietti.json. Le DATE non sono scritte da nessuna parte: le calcola eventi_big() dalla
# regola ufficiale, da oggi a MESI_BIG mesi dopo, a ogni generazione (verifica.py, punto 22, le ricalcola in modo indipendente). Per ogni
# attrazione un file .ics (stesso metodo dei calendari di italystrikes/genera.py: testo con escape, righe piegate a 75 byte, CRLF) con le uscite
# dei biglietti, i giorni gratis, le chiusure e gli orari speciali. Link solo alle biglietterie ufficiali indicate dalle pagine ufficiali.
# 31/10/2026: attrazioni a data fissa in Giappone e negli USA, con tre tipi di regola nuovi: "mensile" (il giorno N di ogni mese, per il
# mese M dopo: Museo Ghibli, Ghibli Park, sorteggio del Nintendo Museum, visita al Palazzo Imperiale), "date" (date fisse della tabella
# ufficiale: tornei di sumo) e "anticipo" (ogni giorno, N giorni prima della visita: Washington Monument; nessuna data nel calendario, la
# data di oggi + N la calcola il browser). Accanto alla prossima uscita, l'ora convertita a Londra, New York e Sydney.
from zoneinfo import ZoneInfo  # noqa: E402

BIG_BASE = "ticket-release-dates"
_f_big = DATI / "biglietti.json"
BIG = json.loads(_f_big.read_text(encoding="utf-8")) if _f_big.exists() else None
BIG_ATT = BIG["attrazioni"] if BIG else []
BIG_PER = {a["slug"]: a for a in BIG_ATT}
MESI_BIG = 6  # finestra delle date calcolate: da oggi a 6 mesi dopo
STAGIONE_BIG = "2026-27"  # anni nei titoli (la finestra va da fine ottobre 2026 ad aprile 2027): da cambiare quando la finestra passa al 2027-28
LIMITE_TITOLO_BIG = 70
GIORNI_SETT = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
# Riquadro "Guided tours with skip-the-line" (Viator, 8 %): SPENTO. Il programma non è ancora approvato (30/10/2026). Quando arriva il link
# generale con il nostro ID, scriverlo qui (https, dominio viator.com): il riquadro compare sotto la biglietteria ufficiale, con
# rel="sponsored noopener" e la riga di trasparenza (verifica.py, punto 22, e monetizzazione.py lo controllano). Vuoto = nessun riquadro.
VIATOR_TOUR = "https://www.viator.com/?pid=P00329132&mcid=42383&medium=link&campaign=byf-biglietti"
# Link di ricerca Viator per attrazione (acceso il 4/11/2026, verificati da Massimiliano); le altre attrazioni e l'indice usano VIATOR_TOUR.
VIATOR_PER_ATTRAZIONE = {
    "vatican-museums": "https://www.viator.com/searchResults/all?text=Vatican+Museums&pid=P00329132&mcid=42383&medium=link&campaign=byf-vaticano",
    "sagrada-familia": "https://www.viator.com/searchResults/all?text=Sagrada+Familia&pid=P00329132&mcid=42383&medium=link&campaign=byf-sagrada",
    "alhambra": "https://www.viator.com/searchResults/all?text=Alhambra&pid=P00329132&mcid=42383&medium=link&campaign=byf-alhambra",
    "pompeii": "https://www.viator.com/searchResults/all?text=Pompeii&pid=P00329132&mcid=42383&medium=link&campaign=byf-pompei",
    "last-supper-milan": "https://www.viator.com/searchResults/all?text=Last+Supper+Milan&pid=P00329132&mcid=42383&medium=link&campaign=byf-cenacolo",
    "anne-frank-house": "https://www.viator.com/searchResults/all?text=Anne+Frank+House&pid=P00329132&mcid=42383&medium=link&campaign=byf-annefrank",
}


def viator_link(a=None):
    """Link Viator del riquadro: quello dell'attrazione se c'è, altrimenti il link generale (anche nell'indice)."""
    return VIATOR_PER_ATTRAZIONE.get(a["slug"], VIATOR_TOUR) if a else VIATOR_TOUR


def viator_link_valido(u):
    """https, dominio viator.com tra quelli ammessi, pid uguale a quello del link generale."""
    from urllib.parse import parse_qs
    pid = parse_qs(urlparse(VIATOR_TOUR).query).get("pid", [""])[0]
    return (u.startswith("https://") and MON.dominio_ammesso(u) and MON.dominio_in(urlparse(u).hostname, ["viator.com"])
            and bool(pid) and parse_qs(urlparse(u).query).get("pid") == [pid])
# Riquadro "Where to stay" (Stay22 → Booking.com, AID massimilianocori): ACCESO dal 31/10/2026. Link in dati/affiliati.json, voce
# "_stay22_alloggi" → "link" (uno per attrazione, per slug; url vuoto = niente riquadro su quella pagina). Ogni link apre la pagina Booking.com
# degli hotel della CITTÀ (Napoli per Pompei), quindi il testo lo dice e non promette prezzi né disponibilità. Posizione: dopo la biglietteria
# ufficiale (e dopo l'eventuale riquadro Viator); nell'indice una riga con tutti i link dopo i calendari. verifica.py, punto 22, controlla tutto.
STAY22_BIG = {s: v for s, v in ((AFFILIATI.get("_stay22_alloggi") or {}).get("link") or {}).items() if (v.get("url") or "").strip()}
TIPI_BIG = {"uscita": "Tickets go on sale", "gratis": "Free entry", "chiusura": "Closed", "orario": "Special hours"}
TIPI_USCITA_BIG = ("settimanale", "prima_domenica", "mensile", "date", "anticipo")
# Fusi per la conversione dell'ora della prossima uscita (si salta quello dell'attrazione)
FUSI_ALTRI_BIG = [("London", "Europe/London"), ("New York", "America/New_York"), ("Sydney", "Australia/Sydney")]


def url_big(slug=None):
    return f"{BIG_BASE}/" + (f"{slug}/" if slug else "")


def url_ics_big(slug):
    return f"{BIG_BASE}/calendars/{slug}.ics"


def fonti_big(a):
    out = []
    for c in a["citazioni"]:
        if c["f"] not in out:
            out.append(c["f"])
    return out


def data_big(a):
    return max(BIG["fonti"][f]["letto_il"] for f in fonti_big(a))


def cit_big(a, id_):
    return next(c for c in a["citazioni"] if c["id"] == id_)


def fine_big():
    return piu_mesi(OGGI.isoformat(), MESI_BIG)


def pasqua(anno):
    """Domenica di Pasqua (calendario gregoriano, algoritmo anonimo di Meeus/Jones/Butcher)."""
    a, b, c = anno % 19, anno // 100, anno % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    mese = (h + l_ - 7 * m + 114) // 31
    giorno = (h + l_ - 7 * m + 114) % 31 + 1
    return date(anno, mese, giorno)


def domeniche_big(quale):
    """Prima o ultima domenica di ogni mese, dal mese di oggi a un mese dopo la fine della finestra (iso)."""
    out, y, m = [], OGGI.year, OGGI.month
    fine = date.fromisoformat(fine_big())
    while date(y, m, 1) <= fine + timedelta(days=31):
        if quale == "prima":
            d = date(y, m, 1)
            d += timedelta(days=(6 - d.weekday()) % 7)
        else:
            d = date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)
            d -= timedelta(days=(d.weekday() - 6) % 7)
        out.append(d)
        y, m = y + (m == 12), m % 12 + 1
    return out


def gratis_saltate(a):
    """Ultime domeniche della finestra senza ingresso gratuito per le eccezioni scritte nella fonte: [(data iso, motivo)]."""
    g = a.get("gratis")
    if not g or g["tipo"] != "ultima_domenica":
        return []
    out, fine = [], fine_big()
    for d in domeniche_big("ultima"):
        if not (OGGI.isoformat() <= d.isoformat() <= fine):
            continue
        if g.get("pasqua") and d == pasqua(d.year):
            out.append((d.isoformat(), "Easter Sunday"))
        elif d.strftime("%m-%d") in g.get("eccezioni_md", []):
            out.append((d.isoformat(), "one of the exceptions on the official list"))
    return out


def eventi_big(a):
    """Tutte le date calcolate dalle regole, da oggi a MESI_BIG mesi dopo: dict con data, ora (o None), tipo, regola, titolo, visita, testo."""
    oggi, fine = OGGI.isoformat(), fine_big()
    dentro = lambda d: oggi <= d.isoformat() <= fine  # noqa: E731
    giorni_f = [OGGI + timedelta(days=i) for i in range(giorni(oggi, fine) + 1)]
    ev = []
    for r in a["uscite"]:
        if r["tipo"] == "settimanale":
            for d in giorni_f:
                if d.weekday() == r["giorno"]:
                    ev.append({"data": d.isoformat(), "ora": r["ora"], "tipo": "uscita", "regola": r["id"], "titolo": r["titolo"],
                               "visita": (d + timedelta(days=r["visita_dopo_giorni"])).isoformat() if r.get("visita_dopo_giorni") else None})
        elif r["tipo"] == "prima_domenica":
            for s in domeniche_big("prima"):
                d = s - timedelta(days=r["giorni_prima"])
                if dentro(d):
                    ev.append({"data": d.isoformat(), "ora": r["ora"], "tipo": "uscita", "regola": r["id"], "titolo": r["titolo"],
                               "visita": s.isoformat()})
        elif r["tipo"] == "mensile":
            for d in giorni_f:
                if d.day == r["giorno"]:
                    m = d.month - 1 + r["mesi_dopo"]
                    v = date(d.year + m // 12, m % 12 + 1, 1)
                    ev.append({"data": d.isoformat(), "ora": r["ora"], "tipo": "uscita", "regola": r["id"], "titolo": r["titolo"],
                               "visita": v.isoformat(), "per": f"{MESI[v.month - 1]} {v.year}"})
        elif r["tipo"] == "date":
            for x in r["date"]:
                if dentro(date.fromisoformat(x["data"])):
                    ev.append({"data": x["data"], "ora": r["ora"], "tipo": "uscita", "regola": r["id"], "titolo": r["titolo"],
                               "visita": None, "per": x["per"]})
    g = a.get("gratis")
    if g:
        saltate = {d for d, _ in gratis_saltate(a)}
        for s in domeniche_big("prima" if g["tipo"] == "prima_domenica" else "ultima"):
            if dentro(s) and s.isoformat() not in saltate:
                ev.append({"data": s.isoformat(), "ora": None, "tipo": "gratis", "regola": g["tipo"], "titolo": f"{a['nome']}: free entry", "visita": None})
    C = a["chiusure"]
    for d in giorni_f:
        if d.strftime("%m-%d") in C["md"] or d.isoformat() in C["date"]:
            ev.append({"data": d.isoformat(), "ora": None, "tipo": "chiusura", "regola": "chiusure", "titolo": f"{a['nome']}: closed", "visita": None})
        for o in a["orari_speciali"]:
            if o.get("md") == d.strftime("%m-%d") or o.get("data") == d.isoformat():
                ev.append({"data": d.isoformat(), "ora": None, "tipo": "orario", "regola": "orari", "titolo": f"{a['nome']}: {o['testo'][:1].lower() + o['testo'][1:]}",
                           "visita": None, "testo": o["testo"]})
    ordine = {"chiusura": 0, "orario": 1, "gratis": 2, "uscita": 3}
    return sorted(ev, key=lambda e: (e["data"], ordine[e["tipo"]], e["ora"] or "", e["regola"]))


def prossimo_big(a, tipo, regola=None):
    return next((e for e in eventi_big(a) if e["tipo"] == tipo and (regola is None or e["regola"] == regola)), None)


def giorno_lungo(iso):
    return f"{GIORNI_SETT[date.fromisoformat(iso).weekday()]} {data_lunga(iso)}"


def giorno_breve(iso):
    d = date.fromisoformat(iso)
    return f"{GIORNI_SETT[d.weekday()][:3]} {d.day} {MESI[d.month - 1][:3]} {d.year}"


def cambio_ora_big(a):
    """Primo giorno della finestra in cui il fuso dell'attrazione passa all'ora legale (iso) o None."""
    z = ZoneInfo(a["fuso"])
    oggi, fine = OGGI, date.fromisoformat(fine_big())
    prima = datetime(oggi.year, oggi.month, oggi.day, 12, tzinfo=z).utcoffset()
    d = oggi
    while d <= fine:
        if datetime(d.year, d.month, d.day, 12, tzinfo=z).utcoffset() > prima:
            return d.isoformat()
        d += timedelta(days=1)
    return None


def nota_ora_big(a, r):
    """Avviso per le regole scritte in CET (Anne Frank House) quando nella finestra arriva l'ora legale."""
    if "CET" not in cit_big(a, r["cit"][0])["x"]:
        return ""
    c = cambio_ora_big(a)
    if not c:
        return ""
    h, mi = r["ora"].split(":")
    return (f"The official page writes {cit_ora_big(a, r)}. From {data_lunga(c)} {a['citta']} is on summer time (CEST): the page does not say whether "
            f"the release then moves to {int(h) + 1:02d}:{mi} Amsterdam time, so our calendar keeps {r['ora']} Amsterdam time, the earlier of the two.")


def cit_ora_big(a, r):
    m = re.search(r"\b\d{1,2}(?:[.:]\d{2})?\s?(?:am|a\.m\.|noon|pm|p\.m\.)?\s?CET\b|\b12 noon\b", cit_big(a, r["cit"][0])["x"])
    return m.group(0) if m else r["ora"]


def quando_big(e, a):
    return f"{giorno_lungo(e['data'])} at {e['ora']}" if e.get("ora") else giorno_lungo(e["data"])


FINE_PROX_BIG = "after the last date we calculated: check the official page"


def prox_big(cands, vuoto):
    """Una data "prossima" (HTML). Nella pagina c'è il primo candidato (iso, testo) calcolato alla generazione; BIG_JS mostra nel browser il
    primo candidato non ancora passato, così una pagina non rigenerata per settimane non dà per "prossima" una data passata."""
    if not cands:
        return escape(vuoto)
    js = json.dumps([[d, t] for d, t in cands] + [["9999-12-31", FINE_PROX_BIG]], ensure_ascii=False)
    return f'<span data-prox="{escape(js)}">{escape(cands[0][1])}</span>'


def risposta_big(a, html=False):
    """Prima frase: chi lo dice, quando lo abbiamo controllato, la risposta con la prossima data calcolata (html=True: date aggiornabili)."""
    def sost(m):
        k, _, r = m.group(1).partition(":")
        if k == "anticipo":
            g = next(x for x in a["uscite"] if x["id"] == r)["giorni"]
            t = giorno_lungo((OGGI + timedelta(days=g)).isoformat())
            return f'<span data-anticipo="{g}" data-fuso="{escape(a["fuso"])}">{escape(t)}</span>' if html else t
        if k in ("next", "visita", "per"):
            ee = [e for e in eventi_big(a) if e["tipo"] == "uscita" and e["regola"] == r]
            cands, vuoto = [(e["data"], quando_big(e, a) if k == "next" else e["per"] if k == "per" else giorno_lungo(e["visita"])) for e in ee], "not in the next six months"
        else:
            ee = [e for e in eventi_big(a) if e["tipo"] == ("gratis" if k == "next_free" else "chiusura")]
            cands, vuoto = [(e["data"], giorno_lungo(e["data"])) for e in ee], "none in the next six months"
        if html:
            return prox_big(cands, vuoto)
        return cands[0][1] if cands else vuoto
    testa = f"According to {a['chi']}, checked on {data_lunga(data_big(a))}, "
    segnaposto = r"\{([a-z_]+(?::[a-z-]+)?)\}"
    if not html:
        return testa + re.sub(segnaposto, sost, a["risposta"])
    parti = re.split(segnaposto, a["risposta"])  # pari: testo, dispari: nome del segnaposto
    return escape(testa) + "".join(escape(x) if i % 2 == 0 else sost(re.match(r"(.*)", x)) for i, x in enumerate(parti))


def avviso_date_big(prima_data):
    """Nascosto; BIG_JS lo mostra quando la data calcolata più vicina è passata (pagina non rigenerata da allora)."""
    return (f'<p class="avviso" data-vecchie="{prima_data}" hidden><strong>Some of the dates on this page have passed.</strong> We calculated them on '
            f'{data_lunga(OGGI.isoformat())}: the table and the “next” dates at the top skip past dates in your browser, but the text further down '
            f'may still name them. Check the official page before you book.</p>')


def testo_cit_big(a, id_):
    return cit_big(a, id_)["x"].strip("“”*")


def frase_uscite_big(a, regola):
    r = next(x for x in a["uscite"] if x["id"] == regola)
    if r["tipo"] == "anticipo":
        return (f"So today's release ({data_lunga(OGGI.isoformat())}) is for {giorno_lungo((OGGI + timedelta(days=r['giorni'])).isoformat())}: "
                f"for any visit date, count back {r['giorni']} day{'s' if r['giorni'] != 1 else ''}.")
    ee = [e for e in eventi_big(a) if e["tipo"] == "uscita" and e["regola"] == regola][:3]
    if not ee:
        return "There is no release under this rule in the next six months."
    tz = a["ora_locale"]
    if r["tipo"] in ("mensile", "date"):
        voci = [f"{giorno_lungo(e['data'])} (for {e['per']})" for e in ee]
        elenco = ", ".join(voci[:-1]) + " and " + voci[-1] if len(voci) > 1 else voci[0]
        return f"The next ones are {elenco}" + (f", at {ee[0]['ora']} {tz}." if ee[0]["ora"] else ".")
    if ee[0].get("visita") and next(r for r in a["uscite"] if r["id"] == regola)["tipo"] == "prima_domenica":
        return f"The next one is {giorno_lungo(ee[0]['data'])} at {ee[0]['ora']} {tz}, for {giorno_lungo(ee[0]['visita'])}."
    elenco = ", ".join(giorno_lungo(e["data"]) for e in ee[:-1]) + " and " + giorno_lungo(ee[-1]["data"]) if len(ee) > 1 else giorno_lungo(ee[0]["data"])
    frase = f"The next releases are on {elenco}, at {ee[0]['ora']} {tz}."
    if ee[0].get("visita"):
        frase += f" Six weeks after the first one is {giorno_lungo(ee[0]['visita'])}."
    return frase


def frase_gratis_big(a):
    ee = [e for e in eventi_big(a) if e["tipo"] == "gratis"][:3]
    if not ee:
        return "There is no free day in the next six months."
    elenco = ", ".join(giorno_lungo(e["data"]) for e in ee[:-1]) + " and " + giorno_lungo(ee[-1]["data"]) if len(ee) > 1 else giorno_lungo(ee[0]["data"])
    frase = f"The next free days are {elenco}."
    for d, motivo in gratis_saltate(a):
        frase += f" There is no free entry on {giorno_lungo(d)} ({motivo})."
    return frase


def risposta_giorno_big(a, md):
    """Risposta a "Is X open on <giorno>?" dalla lista ufficiale: chiuso, orario speciale o non nella lista. Prossima occorrenza del giorno."""
    y = OGGI.year if md >= OGGI.strftime("%m-%d") else OGGI.year + 1
    iso = f"{y}-{md}"
    gg = giorno_lungo(iso)
    if md in a["chiusure"]["md"]:
        return f"No. {gg} is on the official list of closing days:"
    o = next((o for o in a["orari_speciali"] if o.get("md") == md), None)
    if o:
        t = o["testo"]
        t = t[:1].lower() + t[1:]
        return f"Yes, with special hours on {gg} ({t}). The official page says:"
    if date.fromisoformat(iso).weekday() in a["chiusure"]["settimana"]:
        return f"No. {gg} falls on a weekly closing day. The official page says:"
    return f"Yes, as far as the official list shows: {gg} is not one of the closing days it lists. The official list says:"


def faq_big(a):
    out = []
    for f in a["faq"]:
        parti = [risposta_giorno_big(a, f["md"])] if f["tipo"] == "giorno" else []
        parti += [f["pre"]] if f["pre"] else []
        parti += [f"“{testo_cit_big(a, i)}”" for i in f["cit"]]
        if f["tipo"] == "uscita":
            parti.append(frase_uscite_big(a, f["regola"]))
        elif f["tipo"] == "gratis":
            parti.append(frase_gratis_big(a))
        parti += [f["post"]] if f["post"] else []
        out.append((f["q"], " ".join(parti)))
    out.append(("Where does this answer come from?", f"From {a['chi']}, read on {data_lunga(data_big(a))} and quoted word "
                                                     "for word on this page. The dates are calculated by us from the official rule, from today to six months "
                                                     "ahead; museums can change their rules, so check the official page before you book."))
    return out


def html_faq_big(faq):
    h = "".join(f"<h3>{escape(q)}</h3><p>{escape(r)}</p>" for q, r in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]}
    return f'<section class="faq"><h2>Questions</h2>{h}</section>', [ld]


def link_fonte_big(fid):
    F = BIG["fonti"][fid]
    return f'<a href="{escape(F["pagina"])}" rel="noopener">{escape(F["titolo"])}</a>'


def blocco_cit_big(a, ids):
    """Citazioni ufficiali raggruppate per fonte, con link e data."""
    out, gruppi = [], []
    for i in ids:
        c = cit_big(a, i)
        if gruppi and gruppi[-1][0] == c["f"]:
            gruppi[-1][1].append(c)
        else:
            gruppi.append((c["f"], [c]))
    for fid, cc in gruppi:
        F = BIG["fonti"][fid]
        paragrafi = "".join(f"<p>{escape(c['x'])}</p>" for c in cc)
        out.append(f'<blockquote class="cit">{paragrafi}</blockquote>'
                   f'<p class="fonte">Source: {link_fonte_big(fid)} ({escape(F["ente"])}), checked on {data_lunga(F["letto_il"])}. Quoted word for word.</p>')
    return "".join(out)


# ---- iCal (stesso metodo di italystrikes/genera.py: _ics_testo, _ics_riga)
def _ics_testo(t):
    return t.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _ics_riga(r):
    b = r.encode("utf-8")
    out, cur = [], b""
    for ch in r:
        c = ch.encode("utf-8")
        if len(cur) + len(c) > (75 if not out else 74):
            out.append(cur)
            cur = b""
        cur += c
    out.append(cur)
    return "\r\n ".join(x.decode("utf-8") for x in out) if len(b) > 75 else r


def _utc_big(a, iso, ora):
    h, m = (int(x) for x in ora.split(":"))
    d = date.fromisoformat(iso)
    return datetime(d.year, d.month, d.day, h, m, tzinfo=ZoneInfo(a["fuso"])).astimezone(ZoneInfo("UTC"))


def regola_di_big(a, e):
    if e["tipo"] == "uscita":
        return next(r for r in a["uscite"] if r["id"] == e["regola"])
    if e["tipo"] == "gratis":
        return a["gratis"]
    if e["tipo"] == "chiusura":
        return a["chiusure"]
    return next(o for o in a["orari_speciali"] if o.get("md") == e["data"][5:] or o.get("data") == e["data"])


def sommario_ics_big(a, e):
    if e["tipo"] == "uscita" and e.get("per"):
        return f"{e['titolo']} (for {e['per']})"
    if e["tipo"] == "uscita" and e.get("visita"):
        r = regola_di_big(a, e)
        return e["titolo"] + (f" (for {giorno_breve(e['visita'])})" if r["tipo"] == "prima_domenica" else f" (visit six weeks later: {giorno_breve(e['visita'])})")
    return e["titolo"]


def ics_big(a):
    stamp = f"{OGGI:%Y%m%d}T000000Z"
    pag = f"{URL_SITO}/{url_big(a['slug'])}"
    righe = ["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:-//{NOME}//Ticket release dates//EN", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
             f"X-WR-CALNAME:{_ics_testo(a['nome'] + ': ticket releases and closures')}", f"X-WR-TIMEZONE:{a['fuso']}",
             "REFRESH-INTERVAL;VALUE=DURATION:P1D", "X-PUBLISHED-TTL:P1D"]
    for e in eventi_big(a):
        r = regola_di_big(a, e)
        cit = " ".join(testo_cit_big(a, i) for i in r.get("cit", []))
        desc = (f"Official rule: “{cit}”\nSource: {', '.join(BIG['fonti'][f]['pagina'] for f in dict.fromkeys(cit_big(a, i)['f'] for i in r.get('cit', [])))}"
                f" (checked on {data_lunga(data_big(a))})\nDate calculated by {NOME} from the official rule. Rules can change: check the official page before you book.\n"
                f"Official tickets: {a['biglietteria']['url']}\n{pag}")
        uid = f"{a['slug']}-{e['tipo']}-{e['regola']}-{e['data']}@{urlparse(URL_SITO).hostname}"
        if e["ora"]:
            ini = _utc_big(a, e["data"], e["ora"])
            tempo = [f"DTSTART:{ini:%Y%m%dT%H%M%SZ}", f"DTEND:{ini + timedelta(minutes=30):%Y%m%dT%H%M%SZ}"]
        else:
            tempo = [f"DTSTART;VALUE=DATE:{e['data'].replace('-', '')}", f"DTEND;VALUE=DATE:{piu_giorni(e['data'], 1).replace('-', '')}"]
        righe += ["BEGIN:VEVENT", f"UID:{uid}", f"DTSTAMP:{stamp}", *tempo, f"SUMMARY:{_ics_testo(sommario_ics_big(a, e))}",
                  f"DESCRIPTION:{_ics_testo(desc)}", f"URL:{pag}", "TRANSP:TRANSPARENT", "STATUS:CONFIRMED", "END:VEVENT"]
    righe.append("END:VCALENDAR")
    return "\r\n".join(_ics_riga(x) for x in righe) + "\r\n"


def scrivi_ics_big():
    cart = SITO / BIG_BASE / "calendars"
    cart.mkdir(parents=True, exist_ok=True)
    for a in BIG_ATT:
        with open(SITO / url_ics_big(a["slug"]), "w", encoding="utf-8", newline="") as fh:
            fh.write(ics_big(a))


def link_cal_big(a, rel):
    from urllib.parse import quote
    https = f"{URL_SITO}/{url_ics_big(a['slug'])}"
    webcal = "webcal://" + https.split("://", 1)[1]
    google = "https://calendar.google.com/calendar/render?cid=" + quote(webcal, safe="")
    return (f'<p class="cal-link">{ico("cal-in")}<span><a href="{escape(google)}" rel="noopener">Add to Google Calendar</a> · '
            f'<a href="{escape(webcal)}">Apple / Outlook</a> · <a href="{rel}{url_ics_big(a["slug"])}" download>Download the .ics file</a></span></p>')


# ---- pagine
AVVISO_BIG = ('<p class="avviso"><strong>Museums and attractions can change their rules, add closures or release extra tickets at short notice.</strong> We quote their '
              'official pages word for word, with the date we checked them, and calculate the dates from the official rule. Before you book, check the '
              'official page. This site is not affiliated with any museum or ticket seller.</p>')
BIG_JS = r"""(function(){var d=new Date(),o=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
document.querySelectorAll('tr[data-data]').forEach(function(r){if(r.getAttribute('data-data')<o)r.hidden=true;});
document.querySelectorAll('[data-prox]').forEach(function(s){try{var c=JSON.parse(s.getAttribute('data-prox'));for(var i=0;i<c.length;i++){if(c[i][0]>=o){s.textContent=c[i][1];break;}}}catch(e){}});
document.querySelectorAll('[data-vecchie]').forEach(function(p){if(p.getAttribute('data-vecchie')<o)p.hidden=false;});
var G=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],M=['January','February','March','April','May','June','July','August','September','October','November','December'];
document.querySelectorAll('[data-anticipo]').forEach(function(s){var n=parseInt(s.getAttribute('data-anticipo'),10),y=d.getFullYear(),m=d.getMonth(),g=d.getDate();try{var q=new Intl.DateTimeFormat('en-CA',{timeZone:s.getAttribute('data-fuso'),year:'numeric',month:'2-digit',day:'2-digit'}).format(d).split('-');if(q.length===3){y=+q[0];m=+q[1]-1;g=+q[2];}}catch(e){}var x=new Date(y,m,g+n);s.textContent=G[x.getDay()]+' '+x.getDate()+' '+M[x.getMonth()]+' '+x.getFullYear();});})();"""


def box_ufficiale_big(a):
    B = a["biglietteria"]
    return (f'<section class="card ufficiale" aria-label="Official tickets"><h2 style="margin-top:0" id="official-tickets">Official tickets</h2>'
            f'<p>Official tickets for the {escape(a["nome_lungo"])} {escape(B.get("verbo", "are sold at"))} <a href="{escape(B["url"])}" rel="noopener">{escape(B["nome"])}</a>; '
            f'resellers may charge more.</p>{blocco_cit_big(a, list(dict.fromkeys(B["cit"] + [c["id"] for c in a["citazioni"] if c["tema"] == "biglietti"])))}</section>')


def box_tour_big(a=None):
    """Riquadro "Guided tours with skip-the-line" (Viator): '' finché VIATOR_TOUR è vuoto. Sempre dopo la biglietteria ufficiale."""
    if not VIATOR_TOUR:
        return ""
    dove = f" at the {a['nome_lungo']}" if a else ""
    return (f'<h2 id="guided-tours">Guided tours with skip-the-line</h2><section class="card noleggio" aria-label="Guided tours, affiliate link" data-tour>'
            f'<p>Official tickets sold out? A guided tour that includes the entry ticket{escape(dove)} can still be available, usually at a higher price than '
            f'the official ticket.</p><p class="noleggio-btn"><a class="btn" href="{escape(viator_link(a))}" rel="sponsored noopener" target="_blank">'
            f'{ico("calendar")}See guided tours on Viator</a></p>{MON.nota_trasparenza("en")}</section>')


def box_alloggio_big(a):
    """Riquadro "Where to stay" (Stay22, link di affiliazione verso Booking.com) della pagina attrazione: '' se l'attrazione non ha un link.
    Sempre dopo la biglietteria ufficiale."""
    v = STAY22_BIG.get(a["slug"])
    if not v:
        return ""
    return (f'<h2 id="where-to-stay">{escape(v["titolo"])} <span class="aff-tag">Affiliate</span></h2>'
            f'<section class="card noleggio" aria-label="Where to stay, affiliate link" data-alloggio>'
            f'<p>{escape(v["frase"])}</p><p class="noleggio-btn"><a class="btn" href="{escape(v["url"])}" rel="sponsored noopener" target="_blank">'
            f'{ico("bed")}See hotels in {escape(v["citta"])} on Booking.com</a></p>'
            f'<p class="small">Link through our partner Stay22. Prices and availability are only those shown on Booking.com.</p>'
            f'{MON.nota_trasparenza("en")}</section>')


def riga_alloggi_big(rel):
    """Riga "Where to stay" dell'indice (tutti i link Stay22, uno per città): '' senza link. Dopo i calendari."""
    voci = [(a, STAY22_BIG[a["slug"]]) for a in BIG_ATT if a["slug"] in STAY22_BIG]
    if not voci:
        return ""
    link = " · ".join(f'<a href="{escape(v["url"])}" rel="sponsored noopener" target="_blank">{escape(v["citta"])}</a>' for _, v in voci)
    return (f'<h2 id="where-to-stay">Where to stay <span class="aff-tag">Affiliate</span></h2>'
            f'<section class="card noleggio" aria-label="Where to stay, affiliate links" data-alloggio>'
            f'<p>Hotels on Booking.com in each city, through our partner Stay22: {link}. Each link opens the hotels of the whole city, '
            f'not only those near the attraction; for Pompeii it shows hotels in Naples, a common base for the visit.</p>'
            f'{MON.nota_trasparenza("en")}</section>')


def righe_eventi_big(a, ee):
    out = []
    for e in ee:
        if e["tipo"] == "uscita":
            r = regola_di_big(a, e)
            cosa = f"{escape(r['breve'])}" + (f" – for {escape(e['per'])}" if e.get("per") else
                                              f" – for {escape(giorno_lungo(e['visita']))}" if r["tipo"] == "prima_domenica" else
                                              f" ({escape(giorno_lungo(e['visita']))})" if e.get("visita") else "")
        elif e["tipo"] == "orario":
            cosa = escape(e["testo"])
        elif e["tipo"] == "gratis":
            cosa = escape(a["gratis"]["breve"])
        else:
            cosa = "on the official list of closing days"
        ora = f"{e['ora']} {escape(a['ora_locale'])}" if e["ora"] else ("All day" if e["tipo"] == "chiusura" else "Opening hours")
        tipo = regola_di_big(a, e).get("etichetta", TIPI_BIG["uscita"]) if e["tipo"] == "uscita" else TIPI_BIG[e["tipo"]]
        if e["tipo"] == "uscita" and not e["ora"]:
            ora = "Time not published"
        out.append(f'<tr data-data="{e["data"]}" data-tipo="{e["tipo"]}"><td data-l="Date">{escape(giorno_lungo(e["data"]))}</td>'
                   f'<td data-l="What"><strong>{escape(tipo)}</strong> – {cosa}</td><td data-l="Time">{ora}</td></tr>')
    return "".join(out)


def tabella_eventi_big(a):
    ee = eventi_big(a)
    testa = '<thead><tr><th>Date</th><th>What</th><th>Time</th></tr></thead>'
    cap = (f'<caption class="cap">{escape(a["nome"])}: dates calculated from the official rules, from {data_lunga(OGGI.isoformat())} to '
           f'{data_lunga(fine_big())}</caption>')
    if len(ee) <= 14:
        return f'<div class="tab tab-b tab-big"><table>{cap}{testa}<tbody>{righe_eventi_big(a, ee)}</tbody></table></div>'
    return (f'<div class="tab tab-b tab-big"><table>{cap}{testa}<tbody>{righe_eventi_big(a, ee[:12])}</tbody></table></div>'
            f'<details class="tutte"><summary>Show all {len(ee)} dates</summary><div class="tab tab-b tab-big"><table>'
            f'<caption class="cap">{escape(a["nome"])}: the other dates</caption>{testa}<tbody>{righe_eventi_big(a, ee[12:])}</tbody></table></div></details>')


def ora_altrove_big(a, iso, ora):
    """[(città, "HH:MM", giorno iso)] dell'ora locale dell'attrazione negli altri fusi (Londra, New York, Sydney), senza quello dell'attrazione."""
    u = _utc_big(a, iso, ora)
    out = []
    for nome, z in FUSI_ALTRI_BIG:
        if z == a["fuso"]:
            continue
        x = u.astimezone(ZoneInfo(z))
        out.append((nome, x.strftime("%H:%M"), x.date().isoformat()))
    return out


def frase_fusi_big(a, e):
    """Frase con l'ora della prossima uscita negli altri fusi (con il giorno quando cambia)."""
    pezzi = []
    for nome, hm, iso in ora_altrove_big(a, e["data"], e["ora"]):
        pezzi.append(f"{hm} in {nome}" + (f" ({giorno_lungo(iso)})" if iso != e["data"] else ""))
    elenco = ", ".join(pezzi[:-1]) + " and " + pezzi[-1] if len(pezzi) > 1 else pezzi[0]
    return f"The next one, {giorno_lungo(e['data'])} at {e['ora']} {a['ora_locale']}, is {elenco}."


def sezione_regole_big(a):
    """Come escono i biglietti: regole calcolate (con la citazione) e regole solo citate (con il motivo)."""
    out = []
    for r in a["uscite"]:
        nota = nota_ora_big(a, r)
        if r["tipo"] == "anticipo":
            calc = (f"There is no single date to put in a calendar: every day is a release day. For a visit on a given date, the release is "
                    f"{r['giorni']} day{'s' if r['giorni'] != 1 else ''} before, at {r['ora']} {a['ora_locale']}.")
            out.append(f'<h3>{escape(r["breve"])}</h3>{blocco_cit_big(a, r["cit"])}<p class="small">{escape(calc)}</p>')
            continue
        e = prossimo_big(a, "uscita", r["id"])
        fusi = f" {escape(frase_fusi_big(a, e))}" if e and e["ora"] else ""
        senza_ora = " The official text gives the day but not the time, so our calendar marks the whole day." if not r.get("ora") else ""
        out.append(f'<h3>{escape(r["breve"])}</h3>{blocco_cit_big(a, r["cit"])}'
                   f'<p class="small">We calculate these dates from the official rule.{" " + escape(nota) if nota else ""}{escape(senza_ora)}{fusi}</p>')
    for t in a["uscite_testo"]:
        out.append(f'<h3>{escape(t["titolo"])}</h3>{blocco_cit_big(a, t["cit"])}<p class="small">{escape(t["nota"])}</p>')
    return "".join(out)


def sezione_giorni_big(a):
    out = []
    g = a.get("gratis")
    if g:
        out.append(f'<h3 id="free-days">Free days: {escape(g["breve"])}</h3>{blocco_cit_big(a, g["cit"])}'
                   f'<p class="small">{escape(frase_gratis_big(a))}</p>')
    else:
        out.append('<h3 id="free-days">Free days</h3><p>The official pages we read list no free entry days for everyone.</p>')
    C = a["chiusure"]
    ch = [e for e in eventi_big(a) if e["tipo"] == "chiusura"]
    breve = C["breve"] or ("No closing day on the official list for the next six months" if not ch else "")
    nota_escl = " ".join(C.get("escluse_md", {}).values())
    sett = (" Also closed " + " and ".join(f"every {GIORNI_SETT[i]}" + (" except the last one of the month" if i == 6 and (g or {}).get("tipo") == "ultima_domenica" else "")
                                          for i in C["settimana"])
            + f" (weekly closing day{'s' if len(C['settimana']) > 1 else ''}, not listed in the table).") if C["settimana"] else ""
    prossimi = f'Next six months: {escape(", ".join(giorno_lungo(e["data"]) for e in ch) or "none")}.' if (ch or not C.get("nota")) else ""
    out.append(f'<h3 id="closures">Closing days: {escape(breve)}</h3>{blocco_cit_big(a, C["cit"])}'
               f'<p class="small">{prossimi}{escape(sett) if sett else ""}'
               f'{" " + escape(nota_escl) if nota_escl else ""}{" " + escape(C["nota"]) if C.get("nota") else ""}</p>')
    if a["orari_speciali"]:
        ids = list(dict.fromkeys(i for o in a["orari_speciali"] for i in o["cit"]))
        out.append(f'<h3>Special opening hours</h3>{blocco_cit_big(a, ids)}')
    out.append(f'<h3>Opening hours: {escape(a["orari"]["breve"])}</h3>{blocco_cit_big(a, a["orari"]["cit"])}')
    return "".join(out)


def titolo_big(a):
    return a["titolo"]


def descrizione_big(a):
    d = data_lunga(data_big(a))
    e = prossimo_big(a, "uscita")
    if e:
        cands = [f"{a['nome']}: next ticket release {giorno_breve(e['data'])}{' at ' + e['ora'] if e['ora'] else ''}, closures and free days, from the official website ({d}).",
                 f"{a['nome']}: next ticket release {giorno_breve(e['data'])}, closures and free days, from the official website."]
    else:
        cands = [f"{a['nome']}: when tickets go on sale, closing days and free days, from the official website, checked on {d}.",
                 f"{a['nome']}: when tickets go on sale, closing days and free days, from the official website."]
    return scegli(cands, LIMITE_DESCRIZIONE)


def pagina_big(a):
    rel = "../../"
    faq_h, faq_ld = html_faq_big(faq_big(a))
    altri = "".join(f'<a href="{rel}{url_big(b["slug"])}">{escape(b["nome"])}<small>{escape(b["citta"])}</small></a>' for b in BIG_ATT if b["slug"] != a["slug"])
    e = prossimo_big(a, "uscita")
    tutte = eventi_big(a)
    cand_usc = [(x["data"], quando_big(x, a)) for x in tutte if x["tipo"] == "uscita"]
    ant = [r for r in a["uscite"] if r["tipo"] == "anticipo"]
    r0 = next((r for r in a["uscite"] if e and r["id"] == e["regola"]), {})
    esito = (f'{ico("calendar")}<strong>{escape("Next " + r0["etichetta"].lower() if r0.get("etichetta") else "Next ticket release")}: '
             f'{prox_big(cand_usc, "")}{" (" + escape(a["ora_locale"]) + ")" if e["ora"] else ""}</strong>' if e else
             f'{ico("calendar")}<strong>{escape(ant[0]["breve"])}</strong>' if ant else
             f'{ico("alert")}<strong>No exact release day to calculate: see the official rule below</strong>')
    corpo = f"""<section class="hero">{h1_diviso(a["h1"])}</section>
<section class="card summary" aria-label="Answer">
<div class="s-top"><span class="sq">{ico("calendar")}</span><span>Tickets · {escape(a["nome"])}, {escape(a["citta"])}</span><span>{STAGIONE_BIG}</span></div>
<div class="s-body">
<div class="esito e-srv {"si" if e or ant else "manuale"}">{esito}</div>
<p class="lead" id="answer">{risposta_big(a, html=True)}</p>
<p class="small">Official tickets: <a href="{escape(a["biglietteria"]["url"])}" rel="noopener">{escape(a["biglietteria"]["nome"])}</a>. Dates calculated on {data_lunga(OGGI.isoformat())}.</p>
</div></section>
{avviso_date_big(tutte[0]["data"]) if tutte else ""}
{AVVISO_BIG}
<h2 id="dates">Next six months: ticket releases, free days and closures</h2>
{tabella_eventi_big(a)}
{link_cal_big(a, rel)}
<p class="small">The calendar file has the same dates as the table, with the official rule and the link in each event. It is rebuilt when we update this site; past dates are hidden from the table in your browser.</p>
{AD}
<h2 id="how">How tickets go on sale: the official rule</h2>
{sezione_regole_big(a)}
<h2 id="closed">Free days, closing days and opening hours</h2>
{sezione_giorni_big(a)}
{box_ufficiale_big(a)}
{box_tour_big(a)}
{box_alloggio_big(a)}
{link_tr_big(rel, a["slug"])}
{faq_h}
<h2>Other attractions</h2>
<div class="griglia">{altri}</div>
<p class="small">Spotted a change? <a href="{rel}contact/?ref=ticket-release-dates">Tell us</a>. <a href="{rel}{BIG_BASE}/">Ticket release dates: all attractions</a>.</p>"""
    pagina(url_big(a["slug"]), scegli([titolo_big(a)], LIMITE_TITOLO_BIG), descrizione_big(a), corpo,
           briciole=[("Ticket release dates", url_big()), (a["nome"], url_big(a["slug"]))], js=BIG_JS, ld_extra=faq_ld)


def regola_breve_big(a):
    if a["uscite"]:
        return "; ".join(r["breve"] for r in a["uscite"])
    return a["uscite_testo"][0]["titolo"] if a["uscite_testo"] else "Not published"


def prima_frase_big(html=False):
    calc = [a for a in BIG_ATT if a["uscite"]]
    prossimi = sorted(((e, a) for a in calc for e in eventi_big(a) if e["tipo"] == "uscita"), key=lambda x: (x[0]["data"], x[0]["ora"] or ""))
    cands = list(dict.fromkeys((e["data"], f"{'' if "'s " in a['nome'] else 'the '}{a['nome']} on {quando_big(e, a)}"
                                + (f" ({a['ora_locale']})" if e["ora"] else "")) for e, a in prossimi))
    aree = list(dict.fromkeys(a.get("area", "Europe") for a in BIG_ATT))
    aree_t = ", ".join(aree[:-1]) + " and " + aree[-1] if len(aree) > 1 else aree[0]
    aree_t = aree_t.replace("USA", "the USA")
    testa = (f"Of the {len(BIG_ATT)} major attractions on this page, in {aree_t}, {len(calc)} publish an exact rule for releasing tickets (a day of the "
             f"week, a day of the month, fixed dates or a set number of days ahead), and the next release we calculated is at ")
    coda = (f"; for each attraction we quote the official website, last checked on {data_lunga(BIG['controllato_il'])}, and calculate the dates "
            f"from its rule.")
    if html:
        return escape(testa) + prox_big(cands, "") + escape(coda)
    return testa + cands[0][1] + coda


def chiusura_sett_big(a):
    """Giorni di chiusura settimanali (non nella colonna "Next closing day" dell'indice, che ha solo le date)."""
    g = a.get("gratis") or {}
    out = []
    for i in a["chiusure"]["settimana"]:
        out.append(f"every {GIORNI_SETT[i]}" + (" except the last one of the month" if i == 6 and g.get("tipo") == "ultima_domenica" else ""))
    return ("also closed " + " and ".join(out)) if out else ""


def titolo_indice_big():
    return f"When Do Tickets Go on Sale? Major Attractions {STAGIONE_BIG} Release Dates"


def faq_indice_big():
    return [faq_big(a)[0] for a in BIG_ATT]


def pagina_indice_big():
    rel = "../"
    righe = []
    for a in BIG_ATT:
        ee = eventi_big(a)
        e = prossimo_big(a, "uscita")
        g = prossimo_big(a, "gratis")
        c = prossimo_big(a, "chiusura")
        B = a["biglietteria"]
        righe.append(f'<tr data-voce id="{a["slug"]}"><td data-l="Attraction"><a href="{rel}{url_big(a["slug"])}">{escape(a["nome"])}</a> '
                     f'<small>{escape(a["citta"])}</small></td>'
                     f'<td data-l="How tickets go on sale">{escape(regola_breve_big(a))}</td>'
                     f'<td data-l="Next release">{prox_big([(x["data"], quando_big(x, a)) for x in ee if x["tipo"] == "uscita"], "") if e else "Every day (rolling)" if any(r["tipo"] == "anticipo" for r in a["uscite"]) else "No exact date published"}</td>'
                     f'<td data-l="Next free day">{prox_big([(x["data"], giorno_lungo(x["data"])) for x in ee if x["tipo"] == "gratis"], "") if g else "None"}</td>'
                     f'<td data-l="Next closing day">{prox_big([(x["data"], giorno_lungo(x["data"])) for x in ee if x["tipo"] == "chiusura"], "") if c else "None on the official list"}'
                     f'{f" <small>({escape(chiusura_sett_big(a))})</small>" if chiusura_sett_big(a) else ""}</td>'
                     f'<td data-l="Official tickets"><a href="{escape(B["url"])}" rel="noopener">{escape(B["nome"])}</a></td>'
                     f'<td data-l="Checked">{data_lunga(data_big(a))}</td></tr>')
    griglia = "".join(f'<a href="{rel}{url_big(a["slug"])}">{escape(a["nome"])}<small>{escape(a["citta"])}</small></a>' for a in BIG_ATT)
    cal = "".join(f'<li><strong>{escape(a["nome"])}</strong>{link_cal_big(a, rel)}</li>' for a in BIG_ATT)
    escl = "".join(f'<li>{escape(x["nome"])}: {escape(x["motivo"])}</li>' for x in BIG["escluse"])
    faq_h, faq_ld = html_faq_big(faq_indice_big())
    d = data_lunga(BIG["controllato_il"])
    corpo = f"""<section class="hero">{h1_diviso(f"When do tickets go on sale? Major attractions: release dates, closures and free days ({STAGIONE_BIG})")}
<p class="lead" id="answer">{prima_frase_big(html=True)}</p></section>
<div class="griglia">{griglia}</div>
{avviso_date_big(min(x["data"] for b in BIG_ATT for x in eventi_big(b)))}
{AVVISO_BIG}
{AD}
<h2>Every attraction</h2>
<p>“How tickets go on sale” is our short summary of the official rule; each attraction page quotes it word for word, with the link and the date. We calculate a date only when the official rule is exact (a day of the week and a time, “the first Sunday of the month”, a day of the month, or the dates in an official schedule); when tickets are released every day for a set number of days ahead, the page counts the days for you. When the official page says “roughly”, gives no day, or two official texts disagree, we show the text and no date. Times are local to the attraction. Dates calculated on {data_lunga(OGGI.isoformat())}.</p>
<div class="tab tab-b tab-srv"><table><caption class="cap">Ticket releases, free days and closures at {len(BIG_ATT)} major attractions, from the official websites, checked on {d}</caption><thead><tr><th>Attraction</th><th>How tickets go on sale</th><th>Next release</th><th>Next free day</th><th>Next closing day</th><th>Official tickets</th><th>Checked</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>
<p class="small">Official tickets are sold at the websites in the table; resellers may charge more.</p>
<h2 id="calendars">Add the dates to your calendar</h2>
<p>One calendar per attraction, with the ticket releases, free days and closures of the next six months, the official rule and the link in each event.</p>
<ul class="cal-lista">{cal}</ul>
{box_tour_big()}
{riga_alloggi_big(rel)}
{faq_h}
<h2>Attractions we left out</h2>
<p>We include an attraction only if its official website answered normally on the day we checked it and writes down when tickets go on sale. For now we left out:</p>
<ul>{escl}</ul>
<h2>How we check</h2>
<p>We read the official websites of the museums and sites (and nothing else: no blogs, guides or ticket resellers), quote the rules word for word and calculate the dates of the next six months from them. The pages and the calendar files show the date of our last check. More on the <a href="{rel}about/#ticket-release-dates">About page</a>. Spotted a change? <a href="{rel}contact/?ref=ticket-release-dates">Tell us</a>.</p>"""
    desc = scegli([f"When tickets go on sale at {len(BIG_ATT)} major attractions in Europe, Japan and the USA (Last Supper, Ghibli Museum, sumo...), from official sites.",
                   f"When tickets go on sale, closing days and free days at {len(BIG_ATT)} major attractions, from the official websites."], LIMITE_DESCRIZIONE)
    pagina(url_big(), scegli([titolo_indice_big(), f"Ticket Release Dates {STAGIONE_BIG}: Major Attractions"], LIMITE_TITOLO_BIG), desc, corpo,
           briciole=[("Ticket release dates", url_big())], js=BIG_JS, ld_extra=faq_ld)


def home_big():
    if not BIG:
        return ""
    voci = "".join(f'<a href="{url_big(a["slug"])}">{escape(a["nome"])}<small>{escape(a["citta"])}</small></a>' for a in BIG_ATT)
    return (f'<h2>When do tickets go on sale?</h2><p>Ticket release dates, closing days and free days at {len(BIG_ATT)} major attractions, calculated '
            f'from the official rules, with a calendar file for each: <a href="{BIG_BASE}/">all attractions in one table</a>.</p><div class="griglia">{voci}</div>')


def about_big(rel):
    if not BIG:
        return ""
    enti = list(dict.fromkeys(F["ente"] for F in BIG["fonti"].values()))
    return f"""<h2 id="ticket-release-dates">Ticket release dates, closures and free days</h2>
<p>Sources: the official websites of {len(BIG_ATT)} major attractions ({escape(", ".join(enti))}), {len(BIG["fonti"])} pages in all, read on {data_lunga(BIG["controllato_il"])}. Each attraction page links every page it quotes.</p>
<p>Rules: every sentence shown between quotation marks is copied word for word from the official page. We calculate dates only from an exact official rule (a day of the week and a time, “the first Sunday of the month”, “the last Sunday of the month” with the exceptions the page lists, a day of the month, a fixed date, or a set number of days before the visit); the dates cover the next six months from the day we build the page, and the calendar files have the same dates. When the official page says “roughly”, gives no day, or two official texts disagree, we show the text and calculate nothing. We link only the ticket websites that the official pages name; other websites may resell tickets at a higher price. An attraction is included only if its official website answered normally on the day we checked it. This is information, not advice: museums decide.</p>"""


# ---------------------------------------------------------------- home e pagine di servizio
# ---------------------------------------------------------------- Patente straniera in Canada, Australia e Nuova Zelanda (31/10/2026)
# Regole per provincia, stato e territorio scritte a mano in dati/patente_straniera_manuali.json (citazioni parola per parola dalle pagine
# ufficiali), fonti rilette da raccolta/patente_straniera.py (HTTP 200, data di lettura, impronta della zona citata) che scrive
# dati/patente_straniera.json. Le pagine ufficiali che dal server non si aprono (403, pagina anti-robot) NON si aggirano: la riga della tabella
# lo dice e non c'è una pagina propria. Una pagina per ogni giurisdizione letta; nessuna pagina "Paese della patente × destinazione" (le
# ricerche esistono, ma il contenuto sarebbe la stessa regola ripetuta: la differenza vera, lo scambio senza esame per patenti del Regno Unito e
# degli Stati Uniti, sta in due colonne della tabella e in ogni pagina). Riquadro DiscoverCars (stesso NOLEGGIO_AUTO) dopo le regole.
FL_BASE = "foreign-licence-canada-australia-nz"
_f_fl = DATI / "patente_straniera.json"
FL = json.loads(_f_fl.read_text(encoding="utf-8")) if _f_fl.exists() else None
FL_GIUR = FL["giurisdizioni"] if FL else []
FL_LETTE = [g for g in FL_GIUR if g["letta"]]
FL_PER = {g["id"]: g for g in FL_GIUR}
LIMITE_TITOLO_FL = 70
FL_PAESI = {"CA": ("Canada", "canada", "provinces and territories"), "AU": ("Australia", "australia", "states and territories"),
            "NZ": ("New Zealand", "new-zealand", "")}
FL_TIPO = {"province": "province", "territory": "territory", "state": "state", "country": "country"}
TEMI_FL = [("visitatori", "Visitors and tourists"), ("residenti", "If you move there"), ("idp", "International driving permit and translation"),
           ("scambio", "Exchanging your licence"), ("altro", "Also on the official page")]
SCAMBIO_FL = {"si": "Yes", "non_detto": "Not stated"}
# Il Paese della pagina "Driving abroad" (ISO) -> paese della sezione
FL_ISO = {"CA": "CA", "AU": "AU", "NZ": "NZ"}


FL_CON_THE = {"nt", "act", "nt_au"}  # "the Northwest Territories", "the Australian Capital Territory", "the Northern Territory"


def frase_fl(g):
    return ("the " if g["id"] in FL_CON_THE else "") + g["nome"]


def url_fl(g=None):
    if g is None:
        return f"{FL_BASE}/"
    if g["paese"] == "NZ":
        return f"{FL_BASE}/new-zealand/"
    return f"{FL_BASE}/{FL_PAESI[g['paese']][1]}/{g['slug']}/"


def fonti_fl(g):
    out = []
    for c in g["citazioni"]:
        if c["f"] not in out:
            out.append(c["f"])
    return out


def data_fl(g):
    return max(FL["fonti"][f]["letto_il"] for f in fonti_fl(g))


def cit_fl(g, id_):
    return next(c for c in g["citazioni"] if c["id"] == id_)


def link_fonte_fl(fid):
    F = FL["fonti"][fid]
    return f'<a href="{escape(F["url"])}" rel="noopener">{escape(F["titolo"])}</a>'


def blocco_cit_fl(cc):
    """Citazioni raggruppate per fonte: virgolette, fonte, ente e data."""
    out, gruppi = [], []
    for c in cc:
        if gruppi and gruppi[-1][0] == c["f"]:
            gruppi[-1][1].append(c)
        else:
            gruppi.append((c["f"], [c]))
    for fid, gg in gruppi:
        F = FL["fonti"][fid]
        cc_h = "".join(f"<p>{escape(c['x'])}</p>" for c in gg)
        out.append(f'<blockquote class="cit">{cc_h}</blockquote>'
                   f'<p class="fonte">Source: {link_fonte_fl(fid)} ({escape(F["ente"])}), checked on {data_lunga(F["letto_il"])}. Quoted word for word.</p>')
    return "".join(out)


def risposta_fl(g):
    return f"According to {g['chi']}, checked on {data_lunga(data_fl(g))}, {g['risposta']}"


def bloccata_fl(bid, in_pagina=False):
    """Riga "non letta": la pagina ufficiale e cosa ha risposto al nostro controllo (nessun aggiramento)."""
    B = FL["bloccate"][bid]
    stato = (f"HTTP {B['http']}" if B["http"] and B["http"] != 200 else "a page that checks for robots") + (
        ", an anti-robot check" if B["antirobot"] and B["http"] and B["http"] != 200 else "")
    quando = f" on {data_lunga(B['provato_il'])}" if B.get("provato_il") else ""
    return (f'The official page (<a href="{escape(B["url"])}" rel="noopener">{escape(B["ente"])}</a>) did not open for our check{quando} '
            f'(it answered with {stato}), so ' + ('this page quotes only the official sources above.' if in_pagina else 'we do not state its rule here.'))


def faq_fl(g):
    out = []
    for f in g["faq"]:
        parti = ([f["pre"]] if f["pre"] else []) + [f"“{cit_fl(g, i)['x']}”" for i in f["cit"]] + ([f["post"]] if f["post"] else [])
        out.append((f["q"], " ".join(parti)))
    out.append((f"Is this legal advice for driving in {frase_fl(g)}?",
                f"No. We quote {g['chi']} word for word, as read on {data_lunga(data_fl(g))}. Rules change, and car rental companies and insurers "
                "can ask for more than the law: check with them and with the official page before you drive."))
    return out


def html_faq_fl(faq):
    h = "".join(f"<h3>{escape(q)}</h3><p>{escape(a)}</p>" for q, a in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    return f'<section class="faq"><h2>Questions</h2>{h}</section>', [ld]


AVVISO_FL = ('<p class="avviso"><strong>These rules differ from place to place, and they change.</strong> We quote the official pages '
             'word for word, with the date we checked them; this is information, not legal advice. Car rental companies and insurers can ask for '
             'more than the law, for example an international driving permit or a translation: ask them before you book.</p>')
FRASE_NOLEGGIO_FL = "Check the licence rules above before you book: the rental company can ask for more than the law, such as an IDP or a translation."


def box_noleggio_fl(g=None):
    """Riquadro "Hire a car" (DiscoverCars): '' con NOLEGGIO_AUTO vuoto. Sempre dopo la risposta e le regole ufficiali."""
    if not NOLEGGIO_AUTO:
        return ""
    P = frase_fl(g) if g else ""
    dove = f" in {P}" if P else " in Canada, Australia or New Zealand"
    return (f'<h2 id="hire-a-car">Hire a car{escape(dove)}</h2>'
            f'<section class="card noleggio" aria-label="Car hire, affiliate link" data-noleggio>'
            f'<p>Hiring a car{escape(dove)}? Compare rental companies and prices on DiscoverCars. {escape(FRASE_NOLEGGIO_FL)}</p>'
            f'<p class="noleggio-btn"><a class="btn" href="{escape(NOLEGGIO_AUTO)}" rel="sponsored noopener" target="_blank">'
            f'{ico("car")}Compare car hire{escape(" in " + P) if P else ""}</a></p>'
            f'{MON.nota_trasparenza("en")}</section>')


def link_fl(rel, c):
    """Riga 'Driving in X on a foreign licence' nelle pagine Driving abroad di Canada, Australia e Nuova Zelanda."""
    if not FL or c not in FL_ISO:
        return ""
    if c == "NZ":
        g = FL_PER.get("nz")
        return (f'<p class="altri-pass">{ico("car")}<span>Staying longer or moving there? New Zealand’s rules change for arrivals from 1 November 2026: <a href="{rel}{url_fl(g)}">how long you can drive in '
                f'New Zealand on an overseas licence</a></span></p>') if g else ""
    nome, slug, parti = FL_PAESI[c]
    return (f'<p class="altri-pass">{ico("car")}<span>Staying longer or moving there? <a href="{rel}{FL_BASE}/#{slug}">How long you can drive in '
            f'{escape(nome)} on a foreign licence, {escape(parti)}</a></span></p>')


def h1_fl(g):
    if g["paese"] == "NZ":
        return f"Driving in New Zealand on an overseas licence: how long, translation and IDP ({ANNO})"
    return f"Driving in {frase_fl(g)} on a foreign licence: visitors and new residents ({ANNO})"


def titoli_fl(g):
    n = frase_fl(g)
    if g["paese"] == "NZ":
        return [f"Driving in New Zealand on an Overseas Licence ({ANNO}): How Long?", f"Driving in NZ on an Overseas Licence ({ANNO})"]
    return [f"Driving in {n} on a Foreign Licence ({ANNO}): How Long?", f"Driving in {n} on a Foreign Licence ({ANNO})",
            f"{g['nome']}: Driving on a Foreign Licence ({ANNO})"]


def descrizione_fl(g):
    d = data_lunga(data_fl(g))
    v = g["visitatori"][:1].lower() + g["visitatori"][1:]
    r = g["residenti"][:1].lower() + g["residenti"][1:]
    return scegli([f"Foreign licence in {frase_fl(g)}: visitors, {v}; new residents, {r}. Official source, checked on {d}.",
                   f"Foreign licence in {frase_fl(g)}: visitors, {v}. Official source, checked on {d}.",
                   f"Driving in {frase_fl(g)} on a foreign licence: the official rules for visitors and new residents, checked on {d}.",
                   f"Driving in {frase_fl(g)} on a foreign licence: official rules, checked on {d}."], LIMITE_DESCRIZIONE)


def stesso_paese_fl(g):
    return [x for x in FL_GIUR if x["paese"] == g["paese"]]


def pagina_fl(g):
    rel = "../" * url_fl(g).count("/")
    temi = "".join(f'<h3>{escape(t)}</h3>{blocco_cit_fl([x for x in g["citazioni"] if x["tema"] == k])}'
                   for k, t in TEMI_FL if any(x["tema"] == k for x in g["citazioni"]))
    sguardo = (f'<tr><th scope="row">Visitors</th><td>{escape(g["visitatori"])}</td></tr>'
               f'<tr><th scope="row">New residents</th><td>{escape(g["residenti"])}</td></tr>'
               f'<tr><th scope="row">IDP and translation</th><td>{escape(g["idp"])}</td></tr>'
               f'<tr><th scope="row">UK licence, exchange without tests</th><td>{escape(g["uk_breve"])}</td></tr>'
               f'<tr><th scope="row">US licence, exchange without tests</th><td>{escape(g["us_breve"])}</td></tr>'
               f'<tr><th scope="row">Checked</th><td>{data_lunga(data_fl(g))}</td></tr>')
    non_letta = f'<p class="small" data-non-letta>{bloccata_fl(g["fonte_non_letta"], True)}</p>' if g.get("fonte_non_letta") else ""
    altri = "".join(f'<a href="{rel}{url_fl(x)}">{escape(x["nome"])}<small>{escape(x["visitatori"])}</small></a>'
                    for x in stesso_paese_fl(g) if x["id"] != g["id"] and x["letta"])
    guida = link_guida(rel, g["paese"])
    faq_h, faq_ld = html_faq_fl(faq_fl(g))
    paese = FL_PAESI[g["paese"]][0]
    corpo = f"""<section class="hero">{h1_diviso(h1_fl(g))}</section>
<section class="card summary" aria-label="Answer">
<div class="s-top"><span class="sq">{ico("car")}</span><span>Foreign licence · {escape(g["nome"])}</span><span>{ANNO}</span></div>
<div class="s-body">
<p class="lead" id="answer">{escape(risposta_fl(g))}</p>
{f'<p class="small">{escape(g["nota"])}</p>' if g.get("nota") else ""}
</div></section>
{AVVISO_FL}
<h2>At a glance</h2>
<div class="tab tab-g"><table><caption class="cap">Driving in {escape(frase_fl(g))} on a foreign licence: our summary of the official sources, checked on {data_lunga(data_fl(g))}</caption><tbody>{sguardo}</tbody></table></div>
<h2 id="official">What the official sources say</h2>
{temi}
{non_letta}
{AD}
{box_noleggio_fl(g)}
{f'<h2>Visiting {escape(paese)}?</h2>{guida}' if guida else ""}
{f'<h2>Other {escape(FL_PAESI[g["paese"]][2])} in {escape(paese)}</h2><div class="griglia">{altri}</div>' if altri else ""}
<p><a href="{rel}{FL_BASE}/">Canada, Australia and New Zealand: every province, state and territory in one table</a></p>
{faq_h}
<p class="small">Spotted a change? <a href="{rel}contact/?ref={FL_BASE}">Tell us</a>.</p>"""
    bc = [("Foreign licence: Canada, Australia, NZ", f"{FL_BASE}/")] + ([(paese, f"{FL_BASE}/#{FL_PAESI[g['paese']][1]}")] if g["paese"] != "NZ" else []) + [(g["nome"], url_fl(g))]
    pagina(url_fl(g), scegli(titoli_fl(g), LIMITE_TITOLO_FL), descrizione_fl(g), corpo, briciole=bc, ld_extra=faq_ld)
    LASTMOD[url_fl(g)] = data_fl(g)


def enti_fl(g):
    """(ente, prima fonte di quell'ente): un link per ente nella colonna delle fonti."""
    out = {}
    for f in fonti_fl(g):
        out.setdefault(FL["fonti"][f]["ente"], f)
    return list(out.items())


def riga_fl(g, rel):
    nome = f'<a href="{rel}{url_fl(g)}">{escape(g["nome"])}</a>' if g["letta"] else escape(g["nome"])
    if not g["letta"]:
        return (f'<tr data-voce id="{g["id"]}"><td data-l="Where">{nome}</td><td data-l="Rules" colspan="6">Not read. '
                f'{bloccata_fl(g["bloccata"])}</td></tr>')
    fonti = " · ".join(f'<a href="{escape(FL["fonti"][f]["url"])}" rel="noopener">{escape(e)}</a>' for e, f in enti_fl(g))
    return (f'<tr data-voce id="{g["id"]}"><td data-l="Where">{nome}</td><td data-l="Visitors">{escape(g["visitatori"])}</td>'
            f'<td data-l="New residents">{escape(g["residenti"])}</td><td data-l="IDP and translation">{escape(g["idp"])}</td>'
            f'<td data-l="UK licence exchange">{SCAMBIO_FL[g["uk"]]}</td><td data-l="US licence exchange">{SCAMBIO_FL[g["us"]]}</td>'
            f'<td data-l="Source, checked">{fonti}, {data_lunga(data_fl(g))}</td></tr>')


def tabella_fl(cod, rel):
    gg = [g for g in FL_GIUR if g["paese"] == cod]
    nome = FL_PAESI[cod][0]
    lette = sum(1 for g in gg if g["letta"])
    return (f'<div class="tab tab-b tab-srv"><table><caption class="cap">Driving in {escape(nome)} on a foreign licence: '
            f'{lette} of {len(gg)} official pages read, checked on {data_lunga(FL["controllato_il"])}</caption>'
            f'<thead><tr><th>Where</th><th>Visitors</th><th>New residents</th><th>IDP and translation</th><th>UK licence exchange</th>'
            f'<th>US licence exchange</th><th>Source, checked</th></tr></thead><tbody>{"".join(riga_fl(g, rel) for g in gg)}</tbody></table></div>')


def prima_frase_fl():
    lette = len(FL_LETTE)
    non = len(FL_GIUR) - lette
    return (f"According to the official pages of {lette} of the {len(FL_GIUR)} Canadian provinces and territories, Australian states and territories "
            f"and New Zealand, checked on {data_lunga(FL['controllato_il'])}, how long you can drive on a foreign licence depends on where you are and "
            f"on whether you are visiting or moving there; the tables below give each rule with its source, and the other {non} official pages "
            "did not open for our check, so we do not state their rules.")


def titolo_indice_fl():
    return [f"Driving in Canada, Australia and NZ on a Foreign Licence ({ANNO})", f"Foreign Licence in Canada, Australia and NZ ({ANNO})"]


def faq_indice_fl():
    """Risposte alle ricerche più frequenti, costruite dai riassunti delle giurisdizioni lette (numeri solo dalle citazioni)."""
    def elenco(cod, campo):
        return "; ".join(f"{g['nome']}: {g[campo][:1].lower() + g[campo][1:]}" for g in FL_LETTE if g["paese"] == cod)
    nz = FL_PER.get("nz")
    risposte = {
        "can i drive in canada with a uk license": "As a visitor, usually yes, but each province and territory sets the time limit. On the official pages "
                                                   f"we read: {elenco('CA', 'visitatori')}.",
        "can i drive in canada with a us license": "As a visitor, usually yes, and the same provincial limits apply as for other foreign licences. "
                                                   f"If you move, these provinces list US licences for exchange, in most cases without tests (see each page for the conditions): "
                                                   f"{', '.join(g['nome'] for g in FL_LETTE if g['paese'] == 'CA' and g['us'] == 'si')}.",
        "how long can i drive in australia with uk license": "It depends on the state and on your visa. On the official pages we read: "
                                                            f"{elenco('AU', 'visitatori')}. For permanent residents: {elenco('AU', 'residenti')}.",
        "can i drive in new zealand with a foreign license": (f"Yes, for a limited time: {nz['visitatori'][:1].lower() + nz['visitatori'][1:]}. "
                                                              "If your licence is not in English, you also need an accepted translation or an IDP.") if nz else "",
    }
    return [(f["q"], risposte[f["query"]]) for f in FL["faq_indice"] if risposte.get(f["query"])]


def pagina_indice_fl():
    rel = "../"
    sezioni = "".join(f'<h2 id="{FL_PAESI[cod][1]}">{escape(FL_PAESI[cod][0])}</h2>{tabella_fl(cod, rel)}{link_guida(rel, cod)}'
                      for cod in FL_PAESI)
    d = data_lunga(FL["controllato_il"])
    faq_h, faq_ld = html_faq_fl(faq_indice_fl())
    corpo = f"""<section class="hero">{h1_diviso(f"Driving in Canada, Australia and New Zealand on a foreign licence ({ANNO})")}
<p class="lead" id="answer">{escape(prima_frase_fl())}</p></section>
{AVVISO_FL}
<p>“Visitors”, “New residents” and “IDP and translation” are our short summaries; each page quotes the official sentences with the link and the date. “UK licence exchange” and “US licence exchange” say whether the official page lists that licence for exchange without a knowledge or road test when you move there (some pages waive only the knowledge test, or cover only most US states: see each page); “Not stated” means the page we read does not say.</p>
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Type a province or state, e.g. Ontario" data-filtro-multi aria-label="Search provinces and states"></div>
{sezioni}
{AD}
{box_noleggio_fl()}
{faq_h}
<h2>How we check</h2>
<p>We read the pages of the provincial, state and territorial licensing authorities and governments (for example the Ontario Ministry of Transportation, ICBC, the Government of Alberta, the NSW Government, the Queensland Government and NZ Transport Agency Waka Kotahi), and for Québec the Highway Safety Code on LegisQuébec, because the SAAQ website did not open for our check. We quote them word for word and give the date. Some official websites answer automated checks with an anti-robot page or an error: we do not try to pass those checks and we do not copy their rules from other websites, so those rows say “Not read”. We check every source again each month. More on the <a href="{rel}about/#{FL_BASE}">About page</a>. Spotted a change? <a href="{rel}contact/?ref={FL_BASE}">Tell us</a>.</p>
<p><a href="{rel}{PAT_BASE}/">Driving abroad: do you need an international driving permit?</a></p>"""
    desc = scegli([f"How long you can drive on a foreign licence in each Canadian province, Australian state and New Zealand, from official pages, checked on {d}.",
                   f"Foreign licence rules in Canada, Australia and New Zealand, from official pages, checked on {d}."], LIMITE_DESCRIZIONE)
    pagina(f"{FL_BASE}/", scegli(titolo_indice_fl(), LIMITE_TITOLO_FL), desc, corpo,
           briciole=[("Foreign licence: Canada, Australia, NZ", f"{FL_BASE}/")], js=APP_JS_FILTRO, ld_extra=faq_ld)
    LASTMOD[f"{FL_BASE}/"] = FL["controllato_il"]


def home_fl():
    if not FL:
        return ""
    voci = "".join(f'<a href="{url_fl(g)}">{escape(g["nome"])}<small>{escape(FL_PAESI[g["paese"]][0])}</small></a>'
                   for g in FL_LETTE if g["id"] in ("on", "bc", "ab", "qc", "nsw", "qld", "wa", "nz"))
    return (f'<h2>Driving in Canada, Australia and New Zealand on a foreign licence</h2><p>How long visitors and new residents can drive on a '
            f'foreign licence in each province, state and territory, from the official pages: <a href="{FL_BASE}/">every rule in one table</a>.</p>'
            f'<div class="griglia">{voci}</div>')


def about_fl(rel):
    if not FL:
        return ""
    enti = list(dict.fromkeys(F["ente"] for F in FL["fonti"].values()))
    non = [g["nome"] for g in FL_GIUR if not g["letta"]]
    return f"""<h2 id="{FL_BASE}">Driving in Canada, Australia and New Zealand on a foreign licence</h2>
<p>Sources: the official pages of the licensing authorities and governments ({escape(", ".join(enti))}), {len(FL["fonti"])} pages in all, read on {data_lunga(FL["controllato_il"])}. Each page links every page it quotes.</p>
<p>Rules: every sentence shown between quotation marks is copied word for word from the official page; the short summaries in the tables are ours. Some official websites answer automated checks with an error or an anti-robot page; we do not try to pass those checks and we do not take their rules from other websites, so we say that the page did not open and give no rule ({escape(", ".join(non))}). For Québec we quote the Highway Safety Code on LegisQuébec because the SAAQ website did not open. This is information, not legal advice.</p>"""


# ---------------------------------------------------------------- "Before you ride": regole del trasporto pubblico per città (31/10/2026)
# Come si paga (carta contactless, app, biglietto), se e come si convalida, multa ufficiale per chi viaggia senza biglietto valido.
# Fatti scritti a mano in dati/trasporti_manuali.json (citazioni parola per parola dalle pagine dell'azienda di trasporto, dell'autorità dei
# trasporti o del comune), fonti rilette da raccolta/trasporti.py (HTTP 200, data, impronta) che scrive dati/trasporti.json. Una pagina solo
# per le città con la multa letta da una pagina ufficiale attuale; le altre restano nell'indice come "Not read" con il motivo, senza dati.
# Nessun riquadro di affiliazione: nessun link Wise attivo nei dati (affiliati.json) al 31/10/2026; AdSense sì (spazio {AD}).
TR_BASE = "public-transport-rules"
_f_tr = DATI / "trasporti.json"
TR = json.loads(_f_tr.read_text(encoding="utf-8")) if _f_tr.exists() else None
TR_CITTA = TR["citta"] if TR else []
TR_LETTE = [c for c in TR_CITTA if c["letta"]]
TR_PER = {c["id"]: c for c in TR_CITTA}
LIMITE_TITOLO_TR = 70
TEMI_TR = [("multa", "Fines"), ("pagamento", "How to pay"), ("convalida", "Validating and tapping"), ("cambio", "Changes announced"),
           ("altro", "Also on the official pages")]
CONTACTLESS_TR = {"si": "Yes", "parziale": "Partly", "non_detto": "Not stated", "no": "No"}
CONVALIDA_TR = {"si": "Yes", "dipende": "It depends", "non_detto": "Not stated", "no": "No"}
LINGUE_TR = {"de": "German", "it": "Italian"}
# Paesi esclusi dai link nelle pagine Driving abroad: le pagine Canada, Australia e Nuova Zelanda sono già revisionate (contenuto da non toccare)
TR_NO_LINK_PAT = {"CA", "AU", "NZ"}
# Attrazioni di "When do tickets go on sale?" -> città della sezione (riga "Getting there by public transport?")
TR_BIG = {"last-supper-milan": "milan", "anne-frank-house": "amsterdam", "sagrada-familia": "barcelona"}


def url_tr(c=None):
    return f"{TR_BASE}/" if c is None else f"{TR_BASE}/{c['slug']}/"


def fonti_tr(c):
    out = []
    for x in c["citazioni"]:
        if x["f"] not in out:
            out.append(x["f"])
    return out


def data_tr(c):
    return max(TR["fonti"][f]["letto_il"] for f in fonti_tr(c))


def cit_tr(c, id_):
    return next(x for x in c["citazioni"] if x["id"] == id_)


def sic_tr(x):
    """Testo della citazione con «[sic]» dopo le parole sbagliate nella fonte (campo 'sic'; la citazione resta parola per parola)."""
    t = x["x"]
    for w in x.get("sic", []):
        t = t.replace(w, w + " [sic]")
    return t


def link_fonte_tr(fid):
    F = TR["fonti"][fid]
    return f'<a href="{escape(F["url"])}" rel="noopener">{escape(F["titolo"])}</a>'


def blocco_cit_tr(cc):
    """Citazioni raggruppate per fonte: virgolette, traduzione nostra (fonti non inglesi), fonte, ente e data."""
    out, gruppi = [], []
    for x in cc:
        if gruppi and gruppi[-1][0] == x["f"]:
            gruppi[-1][1].append(x)
        else:
            gruppi.append((x["f"], [x]))
    for fid, gg in gruppi:
        F = TR["fonti"][fid]
        h = "".join(f"<p>{escape(sic_tr(x))}</p>" + (f'<p class="trad" lang="en"><em>Our translation:</em> {escape(x["tr"])}</p>' if x.get("tr") else "")
                    for x in gg)
        lingua = f' lang="{F["lingua"]}"' if F["lingua"] != "en" else ""
        out.append(f'<blockquote class="cit"{lingua}>{h}</blockquote><p class="fonte">Source: {link_fonte_tr(fid)} ({escape(F["ente"])}), '
                   f'checked on {data_lunga(F["letto_il"])}. Quoted word for word.</p>')
    return "".join(out)


def risposta_tr(c):
    return f"According to {c['chi']}, checked on {data_lunga(data_tr(c))}, {c['risposta']}"


def faq_tr(c):
    """Domande da ricerche vere: parole nostre (pre, post) + citazioni; le citazioni non inglesi entrano con la traduzione nostra."""
    out = []
    for f in c["faq"]:
        parti = [f["pre"]] if f["pre"] else []
        for i in f["cit"]:
            x = cit_tr(c, i)
            parti.append(f"“{x.get('tr') or sic_tr(x)}”")
        if f["post"]:
            parti.append(f["post"])
        out.append((f["q"], " ".join(parti)))
    return out


def html_faq_tr(faq):
    h = "".join(f"<h3>{escape(q)}</h3><p>{escape(a)}</p>" for q, a in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    return f'<section class="faq"><h2>Questions</h2>{h}</section>', [ld]


AVVISO_TR = ('<p class="avviso"><strong>Fines and payment rules change, often at the start of the year.</strong> We quote the transport '
             'company’s own pages word for word, with the date we checked them; this is information, not legal advice. The inspector, '
             'the fine notice and the official page decide.</p>')


def mezzo_tr(c):
    # Edimburgo: letta solo la pagina dei tram, il titolo non promette tutta la rete. Amsterdam: lette solo le pagine GVB (tram, bus e metro
    # della città, non i treni): il titolo dice tram, bus e metro come la rete delle fonti ("GVB trams, buses and metro"), entro 70 caratteri
    return {"edinburgh": "Trams", "amsterdam": "Trams, Buses and Metro"}.get(c["id"], "Public Transport")


def h1_tr(c):
    return f"{c['nome']} {mezzo_tr(c).lower()}: the fine, validation and contactless payment ({ANNO})"


def titoli_tr(c):
    n, m = c["nome"], mezzo_tr(c)
    return [f"{n} {m} Fine, Validation and Contactless ({ANNO})", f"{n} {m}: Fine, Validation, Contactless ({ANNO})",
            f"{n} {m} Fine and Contactless ({ANNO})"]


def descrizione_tr(c):
    d = data_lunga(data_tr(c))
    m = c["multa"]
    return scegli([f"{c['nome']}: fine without a valid ticket {m}; contactless bank card: {CONTACTLESS_TR[c['contactless']].lower()}. Official source, checked on {d}.",
                   f"{c['nome']}: fine without a valid ticket {m}. Official source, checked on {d}.",
                   f"{c['nome']} public transport: the official fine, validation and contactless rules, checked on {d}."], LIMITE_DESCRIZIONE)


def cambio_tr(c):
    return f"{c['cambio']['testo']}" if c.get("cambio") else "None on the pages we read"


def pagina_tr(c):
    rel = "../../"
    temi = "".join(f'<h3>{escape(t)}</h3>{blocco_cit_tr([x for x in c["citazioni"] if x["tema"] == k])}'
                   for k, t in TEMI_TR if any(x["tema"] == k for x in c["citazioni"]))
    sguardo = (f'<tr><th scope="row">Network</th><td>{escape(c["rete"])}</td></tr>'
               f'<tr><th scope="row">Fine without a valid ticket</th><td>{escape(c["multa"])}</td></tr>'
               f'<tr><th scope="row">Contactless bank card</th><td>{escape(c["contactless_breve"])}</td></tr>'
               f'<tr><th scope="row">Validate or tap?</th><td>{escape(c["convalida_breve"])}</td></tr>'
               f'<tr><th scope="row">How to pay</th><td>{escape(c["pagamento"])}</td></tr>'
               f'<tr><th scope="row">Change announced</th><td>{escape(cambio_tr(c))}</td></tr>'
               f'<tr><th scope="row">Checked</th><td>{data_lunga(data_tr(c))}</td></tr>')
    altri = "".join(f'<a href="{rel}{url_tr(x)}">{escape(x["nome"])}<small>{escape(x["multa"].split(" (")[0])}</small></a>'
                    for x in TR_LETTE if x["id"] != c["id"])
    guida = link_guida(rel, c["iso2"])
    faq_h, faq_ld = html_faq_tr(faq_tr(c))
    corpo = f"""<section class="hero">{h1_diviso(h1_tr(c))}</section>
<section class="card summary" aria-label="Answer">
<div class="s-top"><span class="sq">{ico("globe")}</span><span>Public transport · {escape(c["nome"])}</span><span>{ANNO}</span></div>
<div class="s-body">
<p class="lead" id="answer">{escape(risposta_tr(c))}</p>
{f'<p class="small" data-nota>{escape(c["nota"])}</p>' if c.get("nota") else ""}
</div></section>
{AVVISO_TR}
<h2>At a glance</h2>
<div class="tab tab-g"><table><caption class="cap">{escape(c["nome"])} public transport: our summary of the official sources, checked on {data_lunga(data_tr(c))}</caption><tbody>{sguardo}</tbody></table></div>
<h2 id="official">What the official sources say</h2>
{temi}
{AD}
{f'<h2>Driving instead?</h2>{guida}' if guida else ""}
<h2>Other cities</h2>
<div class="griglia">{altri}</div>
<p><a href="{rel}{TR_BASE}/">Public transport rules in {len(TR_CITTA)} cities: every fine in one table</a></p>
{faq_h}
<p class="small">Spotted a change? <a href="{rel}contact/?ref={TR_BASE}">Tell us</a>.</p>"""
    pagina(url_tr(c), scegli(titoli_tr(c), LIMITE_TITOLO_TR), descrizione_tr(c), corpo,
           briciole=[("Public transport rules", f"{TR_BASE}/"), (c["nome"], url_tr(c))], ld_extra=faq_ld)
    LASTMOD[url_tr(c)] = data_tr(c)


def enti_tr(c):
    out = {}
    for f in fonti_tr(c):
        out.setdefault(TR["fonti"][f]["ente"], f)
    return list(out.items())


def non_letta_tr(c):
    """Riga "Not read": il motivo e la pagina ufficiale provata (nessun aggiramento, nessun dato)."""
    P = (TR.get("non_lette") or {}).get(c["id"]) or {}
    quando = f" (checked on {data_lunga(P['provato_il'])})" if P.get("provato_il") else ""
    return (f'Not read{quando}. {escape(c["motivo"])} Official page: <a href="{escape(c["url_provato"])}" rel="noopener">{escape(c["ente"])}</a>.')


def riga_tr(c, rel):
    if not c["letta"]:
        return (f'<tr data-voce id="{c["id"]}"><td data-l="City">{escape(c["nome"])}<br><small>{escape(c["paese"])}</small></td>'
                f'<td data-l="Rules" colspan="4">{non_letta_tr(c)}</td></tr>')
    fonti = " · ".join(f'<a href="{escape(TR["fonti"][f]["url"])}" rel="noopener">{escape(e)}</a>' for e, f in enti_tr(c))
    return (f'<tr data-voce id="{c["id"]}"><td data-l="City"><a href="{rel}{url_tr(c)}">{escape(c["nome"])}</a><br><small>{escape(c["paese"])}</small></td>'
            f'<td data-l="Fine without a valid ticket">{escape(c["multa"])}</td>'
            f'<td data-l="Contactless bank card">{CONTACTLESS_TR[c["contactless"]]}</td>'
            f'<td data-l="Validate or tap?">{CONVALIDA_TR[c["convalida"]]}</td>'
            f'<td data-l="Source, checked">{fonti}, {data_lunga(data_tr(c))}</td></tr>')


def prima_frase_tr():
    lette, tot = len(TR_LETTE), len(TR_CITTA)
    return (f"According to the official pages of the transport companies and authorities of {lette} of the {tot} cities we checked, read on "
            f"{data_lunga(TR['controllato_il'])}, the table below gives the fine for travelling without a valid ticket, whether you can pay with a "
            f"contactless bank card and whether you must validate or tap, with the source of each rule; for the other {tot - lette} cities the "
            "official page did not open for our check or did not state a current fine, so we give no rules for them.")


def titolo_indice_tr():
    return [f"Public Transport Fines, Validation and Contactless by City ({ANNO})", f"Public Transport Fines and Contactless by City ({ANNO})"]


def faq_indice_tr():
    """Risposte costruite dai riassunti delle città lette (i numeri vengono dalle citazioni, controllati da verifica.py)."""
    def elenco(campo, valori):
        return ", ".join(c["nome"] for c in TR_LETTE if c[campo] in valori)
    risposte = {
        "fine for no ticket": "It depends on the city. On the official pages we read: "
                              + "; ".join(f"{c['nome']}: {c['multa']}" for c in TR_LETTE) + ".",
        "contactless payment metro": (f"In some cities. Yes in {elenco('contactless', ('si',))}; partly (some lines, gates or tickets) in "
                                      f"{elenco('contactless', ('parziale',))}. The pages we read do not say for {elenco('contactless', ('non_detto',))}."),
    }
    return [(f["q"], risposte[f["query"]]) for f in TR["faq_indice"] if risposte.get(f["query"])]


def pagina_indice_tr():
    rel = "../"
    d = data_lunga(TR["controllato_il"])
    righe = "".join(riga_tr(c, rel) for c in TR_CITTA)
    faq_h, faq_ld = html_faq_tr(faq_indice_tr())
    corpo = f"""<section class="hero">{h1_diviso(f"Before you ride: public transport fines, validation and contactless payment by city ({ANNO})")}
<p class="lead" id="answer">{escape(prima_frase_tr())}</p></section>
{AVVISO_TR}
<p>“Fine without a valid ticket” is our short summary of the official amount (paying on the spot or late can change it: each city page quotes the rule). “Contactless bank card” says whether the official pages let you pay by tapping a bank card, phone or watch; “Validate or tap?” whether you must stamp, tap or check in. “Not stated” means the pages we read do not say.</p>
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Type a city or country, e.g. Prague" data-filtro-multi aria-label="Search cities"></div>
<div class="tab tab-b tab-srv"><table><caption class="cap">Public transport rules in {len(TR_CITTA)} cities: {len(TR_LETTE)} read from the official pages, checked on {d}</caption><thead><tr><th>City</th><th>Fine without a valid ticket</th><th>Contactless bank card</th><th>Validate or tap?</th><th>Source, checked</th></tr></thead><tbody>{righe}</tbody></table></div>
{AD}
{faq_h}
<h2>How we check</h2>
<p>We read the pages of each city’s transport company or transport authority (for example BVG, DPP, BKK, TMB, STIB-MIVB, OASA, Ruter, the TTC and TransLink) and quote them word for word with the date; German and Italian quotes come with our translation. A city gets a page only if its official page states a current fine for travelling without a valid ticket. Some official websites answer automated checks with an error or an anti-robot page: we do not try to pass those checks and we do not copy their rules from other websites, so those rows say “Not read”. We check every source again every three months, and in January, when many fines change. More on the <a href="{rel}about/#{TR_BASE}">About page</a>. Spotted a change? <a href="{rel}contact/?ref={TR_BASE}">Tell us</a>.</p>
<p><a href="{rel}{PAT_BASE}/">Driving instead? Do you need an international driving permit?</a></p>"""
    desc = scegli([f"Official public transport fines, contactless payment and validation rules in {len(TR_LETTE)} cities, from the transport companies, checked on {d}.",
                   f"Public transport fines and contactless rules by city, from official pages, checked on {d}."], LIMITE_DESCRIZIONE)
    pagina(f"{TR_BASE}/", scegli(titolo_indice_tr(), LIMITE_TITOLO_TR), desc, corpo,
           briciole=[("Public transport rules", f"{TR_BASE}/")], js=APP_JS_FILTRO, ld_extra=faq_ld)
    LASTMOD[f"{TR_BASE}/"] = TR["controllato_il"]


def link_tr_paese(rel, iso2):
    """Riga 'Using public transport in X?' nelle pagine Driving abroad dei Paesi con almeno una città letta (non CA, AU, NZ)."""
    if not TR or iso2 in TR_NO_LINK_PAT:
        return ""
    cc = [c for c in TR_LETTE if c["iso2"] == iso2]
    if not cc:
        return ""
    ll = " · ".join(f'<a href="{rel}{url_tr(c)}">{escape(c["nome"])}</a>' for c in cc)
    return (f'<p class="altri-pass">{ico("globe")}<span>Using public transport instead? The fine without a valid ticket, validation and '
            f'contactless payment: {ll}</span></p>')


def link_tr_big(rel, slug):
    """Riga 'Getting there by public transport?' nelle pagine "When do tickets go on sale?" delle attrazioni in una città letta."""
    c = TR_PER.get(TR_BIG.get(slug, ""))
    if not TR or not c or not c["letta"]:
        return ""
    return (f'<p class="altri-pass">{ico("globe")}<span>Getting there by public transport? <a href="{rel}{url_tr(c)}">{escape(c["nome"])}: '
            f'the fine without a valid ticket, validation and contactless payment</a></span></p>')


def home_tr():
    if not TR:
        return ""
    voci = "".join(f'<a href="{url_tr(c)}">{escape(c["nome"])}<small>{escape(c["multa"].split(" (")[0])}</small></a>' for c in TR_LETTE)
    return (f'<h2>Before you ride: public transport rules by city</h2><p>The official fine for travelling without a valid ticket, whether you '
            f'can tap a contactless bank card and whether you must validate, in {len(TR_LETTE)} cities, from the transport companies’ own pages: '
            f'<a href="{TR_BASE}/">every city in one table</a>.</p><div class="griglia">{voci}</div>')


# ---------------------------------------------------------------- Bagagli sui treni per compagnia + orari di arrivo Eurostar con l'EES (31/10/2026)
# Quanti bagagli, quanto grandi, supplementi, bici e sci, dalle pagine ufficiali delle compagnie ferroviarie (citazioni parola per parola).
# Fatti scritti a mano in dati/treni_bagagli_manuali.json, fonti rilette da raccolta/treni_bagagli.py (HTTP 200, data, impronta) che scrive
# dati/treni_bagagli.json. Una pagina solo per le compagnie con la regola letta da una pagina ufficiale attuale; le altre restano
# nell'indice come "Not read" con il motivo, senza dati. Pagina a parte: orari di arrivo Eurostar per stazione (tabella ufficiale) con l'EES.
# Nessun riquadro di affiliazione (nessun programma attivo pertinente in affiliati.json al 31/10/2026); AdSense sì (spazio {AD}).
TB_BASE = "train-luggage-rules"
TB_ES = "eurostar-check-in-times"
_f_tb = DATI / "treni_bagagli.json"
TB = json.loads(_f_tb.read_text(encoding="utf-8")) if _f_tb.exists() else None
TB_COMP = TB["compagnie"] if TB else []
TB_LETTE = [c for c in TB_COMP if c["letta"]]
TB_PER = {c["id"]: c for c in TB_COMP}
TB_EUR = (TB or {}).get("eurostar")
LIMITE_TITOLO_TB = 70
TEMI_TB = [("numero", "How many bags"), ("misure", "Size and weight"), ("extra", "Extra bags and fees"),
           ("speciali", "Bikes, skis, pushchairs and instruments"), ("cambio", "Changes announced"),
           ("ice", "ICE trains, on the same page"), ("altro", "Also on the official pages")]
LINGUE_TB = {"es": "Spanish"}
CLASSI_ES = [("standard", "Eurostar Standard and Plus"), ("premier", "Eurostar Premier"), ("accessibile", "Accessible travel")]


PRIME_PAROLE_MINUSCOLE_TB = {"One", "Up", "Hand", "Not", "No", "As", "Largest", "Bags", "Suitcase", "Each", "Medium", "Extra", "Excess"}


def minuscola_tb(s):
    """Riassunto dentro una frase (descrizione, FAQ dell'indice): prima parola comune in minuscolo ("Up to three items" -> "up to ...")."""
    return s[0].lower() + s[1:] if s.split(" ", 1)[0] in PRIME_PAROLE_MINUSCOLE_TB else s


def url_tb(c=None):
    return f"{TB_BASE}/" if c is None else f"{TB_BASE}/{c['slug']}/"


def fonti_tb(cc):
    out = []
    for x in cc:
        if x["f"] not in out:
            out.append(x["f"])
    return out


def data_tb(c):
    return max(TB["fonti"][f]["letto_il"] for f in fonti_tb(c["citazioni"]))


def cit_tb(cc, id_):
    return next(x for x in cc if x["id"] == id_)


def link_fonte_tb(fid):
    F = TB["fonti"][fid]
    return f'<a href="{escape(F["url"])}" rel="noopener">{escape(F["titolo"])}</a>'


def blocco_cit_tb(cc):
    """Citazioni raggruppate per fonte: virgolette, traduzione nostra (fonti non inglesi), fonte, ente e data."""
    out, gruppi = [], []
    for x in cc:
        if gruppi and gruppi[-1][0] == x["f"]:
            gruppi[-1][1].append(x)
        else:
            gruppi.append((x["f"], [x]))
    for fid, gg in gruppi:
        F = TB["fonti"][fid]
        h = "".join(f"<p>{escape(x['x'])}</p>" + (f'<p class="trad" lang="en"><em>Our translation:</em> {escape(x["tr"])}</p>' if x.get("tr") else "")
                    for x in gg)
        lingua = f' lang="{F["lingua"]}"' if F["lingua"] != "en" else ""
        out.append(f'<blockquote class="cit"{lingua}>{h}</blockquote><p class="fonte">Source: {link_fonte_tb(fid)} ({escape(F["ente"])}), '
                   f'checked on {data_lunga(F["letto_il"])}. Quoted word for word.</p>')
    return "".join(out)


def risposta_tb(c):
    return f"According to {c['chi']}, checked on {data_lunga(data_tb(c))}, {c['risposta']}"


def faq_cit_tb(ff, cc):
    """Domande da ricerche vere: parole nostre (pre, post) + citazioni; le citazioni non inglesi entrano con la traduzione nostra."""
    out = []
    for f in ff:
        parti = [f["pre"]] if f.get("pre") else []
        for i in f["cit"]:
            x = cit_tb(cc, i)
            parti.append(f"“{x.get('tr') or x['x']}”")
        if f.get("post"):
            parti.append(f["post"])
        out.append((f["q"], " ".join(parti)))
    return out


def faq_tb(c):
    return faq_cit_tb(c["faq"], c["citazioni"])


AVVISO_TB = ('<p class="avviso"><strong>Train companies change their luggage rules, and staff on board decide when a train is full.</strong> We quote '
             'each company’s own pages word for word, with the date we checked them; the short summaries are ours. Your ticket and the '
             'company’s current page decide.</p>')


def h1_tb(c):
    return f"{c['nome_titolo']} luggage allowance: how many bags, what size and extra bags ({ANNO})"


def titoli_tb(c):
    n = c["nome_titolo"]
    return [f"{n} Luggage Allowance: Bags, Size and Extra Fees ({ANNO})", f"{n} Luggage Allowance and Size Limits ({ANNO})",
            f"{n} Luggage Rules ({ANNO})"]


def descrizione_tb(c):
    d = data_lunga(data_tb(c))
    n, m = minuscola_tb(c["numero"]), minuscola_tb(c["misure"])
    return scegli([f"{c['nome_titolo']} luggage: {n}; {m}. Official rules quoted word for word, checked on {d}.",
                   f"{c['nome_titolo']} luggage: {n}. Official rules quoted word for word, checked on {d}.",
                   f"{c['nome_titolo']} luggage allowance, size limits and extra bag fees from the official page, checked on {d}."], LIMITE_DESCRIZIONE)


def link_es_tb(rel):
    if not TB_EUR:
        return ""
    return (f'<p class="altri-pass">{ico("scan")}<span>Travelling to or from London? <a href="{rel}{TB_ES}/">Eurostar check-in times by station, '
            f'with the EES border checks</a></span></p>')


def pagina_tb(c):
    rel = "../../"
    temi = "".join(f'<h3>{escape(t)}</h3>{blocco_cit_tb([x for x in c["citazioni"] if x["tema"] == k])}'
                   for k, t in TEMI_TB if any(x["tema"] == k for x in c["citazioni"]))
    sguardo = (f'<tr><th scope="row">Trains</th><td>{escape(c["treni"])}</td></tr>'
               f'<tr><th scope="row">Bags you can bring</th><td>{escape(c["numero"])}</td></tr>'
               f'<tr><th scope="row">Size limit</th><td>{escape(c["misure"])}</td></tr>'
               f'<tr><th scope="row">Weight</th><td>{escape(c["peso"])}</td></tr>'
               f'<tr><th scope="row">Extra bags and fees</th><td>{escape(c["extra"])}</td></tr>'
               f'<tr><th scope="row">Bikes, skis, pushchairs</th><td>{escape(c["speciali"])}</td></tr>'
               f'<tr><th scope="row">Checked</th><td>{data_lunga(data_tb(c))}</td></tr>')
    altri = "".join(f'<a href="{rel}{url_tb(x)}">{escape(x["nome_titolo"])}<small>{escape(x["paese"])}</small></a>'
                    for x in TB_LETTE if x["id"] != c["id"])
    faq_h, faq_ld = html_faq_tr(faq_tb(c))
    corpo = f"""<section class="hero">{h1_diviso(h1_tb(c))}</section>
<section class="card summary" aria-label="Answer">
<div class="s-top"><span class="sq">{ico("bag")}</span><span>Train luggage · {escape(c["nome"])}</span><span>{ANNO}</span></div>
<div class="s-body">
<p class="lead" id="answer">{escape(risposta_tb(c))}</p>
{f'<p class="small" data-nota>{escape(c["nota"])}</p>' if c.get("nota") else ""}
</div></section>
{AVVISO_TB}
<h2>At a glance</h2>
<div class="tab tab-g"><table><caption class="cap">{escape(c["nome"])} luggage: our summary of the official pages, checked on {data_lunga(data_tb(c))}</caption><tbody>{sguardo}</tbody></table></div>
<h2 id="official">What the official pages say</h2>
{temi}
{AD}
{link_es_tb(rel) if c["id"] == "eurostar" else ""}
<p class="altri-pass">{ico("bag")}<span>Flying instead? <a href="{rel}{BAG_BASE}/">Cabin bag size by airline</a> · <a href="{rel}liquids/">liquids rules by airport</a></span></p>
<h2>Other train companies</h2>
<div class="griglia">{altri}</div>
<p><a href="{rel}{TB_BASE}/">Luggage rules of {len(TB_COMP)} train companies in one table</a></p>
{faq_h}
<p class="small">Spotted a change? <a href="{rel}contact/?ref={TB_BASE}">Tell us</a>.</p>"""
    pagina(url_tb(c), scegli(titoli_tb(c), LIMITE_TITOLO_TB), descrizione_tb(c), corpo,
           briciole=[("Train luggage rules", f"{TB_BASE}/"), (c["nome_titolo"], url_tb(c))], ld_extra=faq_ld)
    LASTMOD[url_tb(c)] = data_tb(c)


def enti_tb(c):
    out = {}
    for f in fonti_tb(c["citazioni"]):
        out.setdefault(TB["fonti"][f]["ente"], f)
    return list(out.items())


def non_letta_tb(c):
    """Riga "Not read": il motivo e la pagina ufficiale provata (nessun aggiramento, nessun dato)."""
    P = (TB.get("non_lette") or {}).get(c["id"]) or {}
    quando = f" (checked on {data_lunga(P['provato_il'])})" if P.get("provato_il") else ""
    return f'Not read{quando}. {escape(c["motivo"])} Official page: <a href="{escape(c["url_provato"])}" rel="noopener">{escape(c["ente"])}</a>.'


def riga_tb(c, rel):
    if not c["letta"]:
        return (f'<tr data-voce id="{c["id"]}"><td data-l="Train company">{escape(c["nome"])}<br><small>{escape(c["paese"])}</small></td>'
                f'<td data-l="Rules" colspan="4">{non_letta_tb(c)}</td></tr>')
    fonti = " · ".join(f'<a href="{escape(TB["fonti"][f]["url"])}" rel="noopener">{escape(e)}</a>' for e, f in enti_tb(c))
    return (f'<tr data-voce id="{c["id"]}"><td data-l="Train company"><a href="{rel}{url_tb(c)}">{escape(c["nome"])}</a><br><small>{escape(c["paese"])}</small></td>'
            f'<td data-l="Bags you can bring">{escape(c["numero"])}</td>'
            f'<td data-l="Size limit">{escape(c["misure"])}</td>'
            f'<td data-l="Extra bags and fees">{escape(c["extra"])}</td>'
            f'<td data-l="Source, checked">{fonti}, {data_lunga(data_tb(c))}</td></tr>')


def prima_frase_tb():
    lette, tot = len(TB_LETTE), len(TB_COMP)
    return (f"According to the official pages of {lette} of the {tot} train companies we checked, read on {data_lunga(TB['controllato_il'])}, "
            "the table below gives how many bags you can bring, the size limits and the fees for extra bags, with the source of each rule; "
            f"for the other {tot - lette} the official page did not open for our check or did not state a rule, so we give no rules for them.")


def titolo_indice_tb():
    return [f"Luggage Rules on European Trains: {len(TB_LETTE)} Companies Compared ({ANNO})", f"Luggage Rules on European Trains ({ANNO})"]


def faq_indice_tb():
    """Risposte costruite dai riassunti delle compagnie lette (i numeri vengono dalle citazioni, controllati da verifica.py)."""
    risposte = {
        "luggage allowance on european trains": "It depends on the company. On the official pages we read: "
                                                + "; ".join(f"{c['nome_titolo']}: {minuscola_tb(c['numero'])}" for c in TB_LETTE) + ".",
        "luggage restrictions on trains in europe": "Each company sets its own limits (see the table above). On the official pages we read, "
                                                    "these companies charge for extra, oversized or non-compliant bags: "
                                                    + "; ".join(f"{c['nome_titolo']} ({minuscola_tb(c['extra'])})" for c in TB_LETTE
                                                                if re.search(r"[€£]\d", c["extra"])) + ".",
    }
    return [(f["q"], risposte[f["query"]]) for f in TB["faq_indice"] if risposte.get(f["query"])]


def pagina_indice_tb():
    rel = "../"
    d = data_lunga(TB["controllato_il"])
    righe = "".join(riga_tb(c, rel) for c in TB_COMP)
    faq_h, faq_ld = html_faq_tr(faq_indice_tb())
    corpo = f"""<section class="hero">{h1_diviso(f"Luggage rules on European trains: how many bags, what size and extra bag fees ({ANNO})")}
<p class="lead" id="answer">{escape(prima_frase_tb())}</p></section>
{AVVISO_TB}
<p>“Bags you can bring” and “Size limit” are our short summaries of each company’s official page; the company page quotes the rule word for word. “Not stated” means the pages we read do not say. Sizes are in the order the company writes them.</p>
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Type a company or country, e.g. Eurostar, Spain" data-filtro-multi aria-label="Search train companies"></div>
<div class="tab tab-b tab-srv"><table><caption class="cap">Luggage rules of {len(TB_COMP)} train companies: {len(TB_LETTE)} read from the official pages, checked on {d}</caption><thead><tr><th>Train company</th><th>Bags you can bring</th><th>Size limit</th><th>Extra bags and fees</th><th>Source, checked</th></tr></thead><tbody>{righe}</tbody></table></div>
{AD}
{link_es_tb(rel)}
<p class="altri-pass">{ico("bag")}<span>Flying instead? <a href="{rel}{BAG_BASE}/">Cabin bag size by airline</a> · <a href="{rel}liquids/">liquids rules by airport</a></span></p>
{faq_h}
<h2>How we check</h2>
<p>We read each train company’s own luggage pages (for TGV INOUI, SNCF’s booking site SNCF Connect) and quote them word for word with the date; Spanish quotes come with our translation. A company gets a page only if its official page states how many bags or how large they can be. Some official websites answer automated checks with an error or an anti-robot page: we do not try to pass those checks and we do not copy their rules from other websites, so those rows say “Not read”. We check every source again every three months. More on the <a href="{rel}about/#{TB_BASE}">About page</a>. Spotted a change? <a href="{rel}contact/?ref={TB_BASE}">Tell us</a>.</p>"""
    desc = scegli([f"How many bags, what size and extra bag fees on {len(TB_LETTE)} European train companies (Eurostar, TGV INOUI, OUIGO, Avlo, Italo, DB), from official pages, checked on {d}.",
                   f"Luggage rules of {len(TB_LETTE)} European train companies from their official pages, checked on {d}."], LIMITE_DESCRIZIONE)
    pagina(f"{TB_BASE}/", scegli(titolo_indice_tb(), LIMITE_TITOLO_TB), desc, corpo,
           briciole=[("Train luggage rules", f"{TB_BASE}/")], js=APP_JS_FILTRO, ld_extra=faq_ld)
    LASTMOD[f"{TB_BASE}/"] = TB["controllato_il"]


# ---- Eurostar: orari di arrivo per stazione con l'EES
def stazione_es(sid):
    return next(s for s in TB_EUR["stazioni"] if s["id"] == sid)


def data_es():
    return max(TB["fonti"][f]["letto_il"] for f in fonti_tb(TB_EUR["citazioni"]) + [TB_EUR["fonte_tabella"]])


def frasi_ees_es():
    """Dalla pagina EES già controllata (dati/ees_etias.json, raccolta/eesetias.py): data del pieno funzionamento e frase GOV.UK su St Pancras."""
    com = [f for f in frasi_ees("ees") if "fully operational" in f["frase"]]
    gov = [g["frase"] for g in EES["govuk"]["frasi"] if g["trovata"] and "St Pancras" in g["frase"]]
    return com, gov


def risposta_staz_es(s):
    a, c = s["arrivo"], s["chiusura"]
    chiude = "the gates close" if s["chiusura_tipo"] == "gate" else "ticket checks close"
    return (f"Eurostar’s table for {s['nome']} says to arrive {a['standard']} minutes before departure in Eurostar Standard and Eurostar Plus, "
            f"{a['premier']} minutes in Eurostar Premier and {a['accessibile']} minutes for accessible travel; {chiude} {c['standard']} minutes before "
            f"departure ({c['premier']} minutes in Premier).")


def faq_es():
    out = []
    for f in TB_EUR["faq"]:
        if f.get("stazione"):
            out.append((f["q"], risposta_staz_es(stazione_es(f["stazione"]))))
        else:
            out += faq_cit_tb([f], TB_EUR["citazioni"])
    return out


def prima_frase_es():
    L, P = stazione_es("london"), stazione_es("paris")
    return (f"According to Eurostar’s “When to arrive at the station” page, checked on {data_lunga(data_es())}, you should arrive at "
            f"{L['nome']} {L['arrivo']['standard']} minutes before departure in Eurostar Standard and Plus ({L['arrivo']['premier']} in Premier) "
            f"and at {P['nome']} {P['arrivo']['standard']} minutes before; Eurostar says the arrival time shown on your ticket already allows for "
            "any checks under the EU’s Entry/Exit System (EES), introduced from 12 October 2025.")


def titolo_es():
    return [f"Eurostar Check-in Times by Station, with EES Border Checks ({ANNO})", f"Eurostar Check-in Times by Station and EES ({ANNO})"]


def pagina_es():
    rel = "../"
    cc = TB_EUR["citazioni"]
    d = data_lunga(data_es())
    righe = "".join(
        f'<tr data-voce id="{s["id"]}"><td data-l="Station"><strong>{escape(s["nome"])}</strong></td>'
        + "".join(f'<td data-l="Arrive: {escape(n)}">{escape(s["arrivo"][k])} min</td>' for k, n in CLASSI_ES)
        + f'<td data-l="{"Gates close" if s["chiusura_tipo"] == "gate" else "Ticket checks close"}">'
          f'{escape(s["chiusura"]["standard"])} min <small>(Premier {escape(s["chiusura"]["premier"])} min; accessible travel {escape(s["chiusura"]["accessibile"])} min)</small></td></tr>'
        for s in TB_EUR["stazioni"])
    com, gov = frasi_ees_es()
    ees_ue = ""
    if com:
        ees_ue += f"{cit_html([f['frase'] for f in com])}{fonti_ees(com)}"
    if gov:
        G = EES["govuk"]
        ees_ue += (f"{cit_html(gov)}<p class=\"fonte\">Official source: <a href=\"{escape(G['url'])}\" rel=\"noopener\">{escape(G['titolo'])}</a> · "
                   f"page updated {data_lunga(G['aggiornata'])} · checked on {data_lunga(EES['controllato_il'])} · "
                   f"<a href=\"{OGL}\" rel=\"noopener\">Open Government Licence v3.0</a></p>")
    eur = TB_PER.get("eurostar")
    faq_h, faq_ld = html_faq_tr(faq_es())
    corpo = f"""<section class="hero">{h1_diviso(f"Eurostar check-in times by station, with the EES border checks ({ANNO})")}</section>
<section class="card summary" aria-label="Answer">
<div class="s-top"><span class="sq">{ico("scan")}</span><span>Eurostar · when to arrive</span><span>{ANNO}</span></div>
<div class="s-body">
<p class="lead" id="answer">{escape(prima_frase_es())}</p>
<p class="small" data-nota>{escape(TB_EUR["nota_ees"])}</p>
</div></section>
<p class="avviso"><strong>The time on your ticket comes first.</strong> Eurostar says its timings are for guidance and can change, and that your downloaded ticket shows the most up-to-date recommended arrival time. We quote Eurostar’s own pages word for word, with the date we checked them.</p>
<h2>Trains to and from London: recommended arrival time</h2>
<div class="tab tab-b tab-srv"><table><caption class="cap">Minutes before departure, from Eurostar’s table “Recommended arrival times when travelling to and from London”, checked on {d}</caption><thead><tr><th>Station</th>{"".join(f"<th>Arrive: {escape(n)}</th>" for _, n in CLASSI_ES)}<th>Gates or ticket checks close</th></tr></thead><tbody>{righe}</tbody></table></div>
<p class="fonte">Source: {link_fonte_tb(TB_EUR["fonte_tabella"])} (Eurostar), checked on {data_lunga(TB["fonti"][TB_EUR["fonte_tabella"]]["letto_il"])}. Numbers copied from the official table; at Amsterdam Centraal and Rotterdam Centraal the table says “ticket checks close” instead of “gate close”.</p>
{blocco_cit_tb([x for x in cc if x["tema"] == "arrivo"])}
{AD}
<h2>Trains between Belgium, France, the Netherlands and Germany</h2>
{blocco_cit_tb([x for x in cc if x["tema"] == "continente"])}
<h2>EES: what Eurostar says</h2>
{blocco_cit_tb([x for x in cc if x["tema"] == "ees"])}
<h3>EES kiosks at St Pancras</h3>
{blocco_cit_tb([x for x in cc if x["tema"] == "kiosk"])}
<h2>EES: what the European Commission and GOV.UK say</h2>
{ees_ue}
<p><a href="{rel}ees-etias/">EES and ETIAS: the official status today</a></p>
{f'<p class="altri-pass">{ico("bag")}<span>Packing? <a href="{rel}{url_tb(eur)}">Eurostar luggage allowance: {escape(eur["numero"])}</a> · <a href="{rel}{TB_BASE}/">luggage rules on European trains</a></span></p>' if eur and eur["letta"] else ""}
{faq_h}
<p class="small">This page is information, not legal advice. Border officers apply the rules at the border. Spotted a change? <a href="{rel}contact/?ref={TB_ES}">Tell us</a>.</p>"""
    desc = scegli([f"When to arrive for Eurostar at St Pancras, Paris Gare du Nord, Brussels, Amsterdam, Lille and Rotterdam, with the EES border checks. Official, checked on {d}.",
                   f"Eurostar recommended arrival times by station and the EES border checks, from Eurostar's own pages, checked on {d}."], LIMITE_DESCRIZIONE)
    pagina(f"{TB_ES}/", scegli(titolo_es(), LIMITE_TITOLO_TB), desc, corpo, briciole=[("Eurostar check-in times", f"{TB_ES}/")], ld_extra=faq_ld)
    LASTMOD[f"{TB_ES}/"] = data_es()


def home_tb():
    if not TB:
        return ""
    voci = "".join(f'<a href="{url_tb(c)}">{escape(c["nome_titolo"])}<small>{escape(c["numero"])}</small></a>' for c in TB_LETTE)
    es = (f' Taking the Eurostar? <a href="{TB_ES}/">Check-in times by station, with the EES border checks</a>.' if TB_EUR else "")
    return (f'<h2>Luggage rules on European trains</h2><p>How many bags you can bring, the size limits and the fees for extra bags on '
            f'{len(TB_LETTE)} train companies, from their own pages: <a href="{TB_BASE}/">every company in one table</a>.{es}</p>'
            f'<div class="griglia">{voci}</div>')


def about_tb(rel):
    if not TB:
        return ""
    enti = list(dict.fromkeys(F["ente"] for F in TB["fonti"].values()))
    non = [c["nome"] for c in TB_COMP if not c["letta"]]
    return f"""<h2 id="{TB_BASE}">Luggage rules on trains and Eurostar check-in times</h2>
<p>Sources: the official pages of the train companies ({escape(", ".join(enti))}), {len(TB["fonti"])} pages in all, read on {data_lunga(TB["controllato_il"])}. Each company page links every page it quotes. The <a href="{rel}{TB_ES}/">Eurostar check-in page</a> copies the numbers of Eurostar’s own table of recommended arrival times, and quotes Eurostar, the European Commission and GOV.UK on EES.</p>
<p>Rules: every sentence shown between quotation marks is copied word for word from the official page (Spanish with our translation); the short summaries in the tables are ours. A company gets a page only when its official page states how many bags or how large they can be. Some official websites answer automated checks with an error or an anti-robot page, or do not state a rule; we do not try to pass those checks and we do not take rules from other websites, so these companies have no page and the table says why: {escape(", ".join(non))}.</p>"""


def about_tr(rel):
    if not TR:
        return ""
    enti = list(dict.fromkeys(F["ente"] for F in TR["fonti"].values()))
    non = [c["nome"] for c in TR_CITTA if not c["letta"]]
    return f"""<h2 id="{TR_BASE}">Public transport rules by city</h2>
<p>Sources: the official pages of the transport companies and transport authorities ({escape(", ".join(enti))}), {len(TR["fonti"])} pages in all, read on {data_lunga(TR["controllato_il"])}. Each city page links every page it quotes.</p>
<p>Rules: every sentence shown between quotation marks is copied word for word from the official page (German and Italian with our translation); the short summaries in the table are ours. A city gets a page only when its official page states a current fine for travelling without a valid ticket. Some official websites answer automated checks with an error or an anti-robot page, or do not state the fine; we do not try to pass those checks and we do not take rules from other websites, so these cities have no page and the table says why: {escape(", ".join(non))}. This is information, not legal advice.</p>"""


# ---------------------------------------------------------------- Animali: dal Regno Unito all'UE con cane, gatto o furetto (31/10/2026)
# Piano: studio-business/intelaiatura/idee-2026-10-30-animali.md (sez. 2-4). Citazioni parola per parola da GOV.UK (APHA, Defra; OGL v3.0) e dalla
# Commissione europea, scritte a mano in dati/animali_manuali.json e rilette da raccolta/animali.py (HTTP 200, data, impronta), che copia anche
# le tabelle GOV.UK delle rotte approvate per entrare in Gran Bretagna e i link della Commissione per Paese in dati/animali.json.
# Pagine: indice, calcolatore delle date (motore Python = JS, verifica.py punto 26), passaporto britannico 2027 (pagina che segue la data),
# rotte approvate, una pagina "dal Regno Unito a [Paese]" solo per i Paesi con ricerche vere (dati/animali_domanda.json).
# Nessun consiglio veterinario ("check with your vet and the official page"); nessun link di affiliazione (nessun programma pertinente attivo).
PET_BASE = "pets"
_f_pet = DATI / "animali.json"
PET = json.loads(_f_pet.read_text(encoding="utf-8")) if _f_pet.exists() else None
_f_pet_dom = DATI / "animali_domanda.json"
PET_DOM = json.loads(_f_pet_dom.read_text(encoding="utf-8")) if _f_pet_dom.exists() else {"paesi": {}, "generali": {}}
PET_CALC = f"{PET_BASE}/date-calculator/"
PET_PASS = f"{PET_BASE}/uk-pet-passport-2027/"
PET_ROTTE = f"{PET_BASE}/approved-routes-great-britain/"
LIMITE_TITOLO_PET = 70
TENIA_PET = ["FI", "IE", "MT", "NO"]  # GOV.UK: verme solitario prima di entrare (più l'Irlanda del Nord, che non è una destinazione di questa sezione)
PET_CIT = {c["id"]: c for c in PET["citazioni"]} if PET else {}
PET_PAESI = PET["paesi"] if PET else []
PET_PER = {p["iso2"]: p for p in PET_PAESI}
PET_QUERY = {"CZ": "czech republic"}  # nome nelle ricerche, se diverso dal nome in minuscolo
PET_DAL_MARE = {"FR": "France", "NL": "Netherlands", "ES": "Spain"}  # Paesi con rotte via mare nella tabella GOV.UK (nome della tabella)


def ricerche_pet():
    """Tutte le ricerche vere lette (suggerimenti dell'autocompletamento), Paesi e generali."""
    out = set()
    for d in list(PET_DOM["paesi"].values()) + [PET_DOM["generali"]]:
        for ss in d.values():
            out.update(ss)
    return out


RICERCHE_PET = ricerche_pet()


def query_pet(p):
    return PET_QUERY.get(p["iso2"], p["nome"].lower())


def ricerca_paese_pet(p):
    """Prima ricerca vera "dal Regno Unito" per il Paese (None = niente pagina): un suggerimento che nomina il Paese e il Regno Unito."""
    q = query_pet(p)
    for m in ("taking dog to {p} from uk", "dog to {p} from uk", "taking a dog to {p} from uk"):
        if m.format(p=q) in RICERCHE_PET:
            return m.format(p=q)
    for ss in PET_DOM["paesi"].get(p["iso2"], {}).values():
        for s in ss:
            if q in s and re.search(r"\b(?:from|to) uk\b|\buk to\b", s):
                return s
    return None


PET_PAGINE = sorted([p for p in PET_PAESI if ricerca_paese_pet(p)], key=lambda p: p["nome"]) if PET else []


def slug_pet(p):
    return "uk-to-" + re.sub(r"[^a-z]+", "-", p["nome"].lower()).strip("-")


def url_pet(p=None):
    return f"{PET_BASE}/" + (f"{slug_pet(p)}/" if p else "")


def ha_pagina_pet(c):
    return any(p["iso2"] == c for p in PET_PAGINE)


def tenia_pet(c):
    return c in TENIA_PET


def data_pet(ids=None):
    """Data di lettura più recente delle fonti usate (tutte, se ids è None)."""
    ff = {PET_CIT[i]["f"] for i in ids} if ids else set(PET["fonti"])
    return max(PET["fonti"][f]["letto_il"] for f in ff)


def link_fonte_pet(fid):
    F = PET["fonti"][fid]
    return f'<a href="{escape(F["pagina"])}" rel="noopener">{escape(F["titolo"])}</a>'


def html_cit_pet(c):
    if c.get("elenco"):
        return f"<p>{escape(c['elenco'][0])}</p><ul>" + "".join(f"<li>{escape(x)}</li>" for x in c["elenco"][1:]) + "</ul>"
    return f"<p>{escape(c['x'])}</p>"


def testo_cit_pet(c):
    """Citazione come testo continuo (FAQ e JSON-LD): le voci di un elenco separate da punto e virgola."""
    if c.get("elenco"):
        return c["elenco"][0] + " " + "; ".join(c["elenco"][1:]) + "."
    return c["x"]


def blocco_cit_pet(ids):
    """Citazioni raggruppate per fonte, con link, ente e data di lettura (stesso formato delle altre sezioni)."""
    out, gruppi = [], []
    for i in ids:
        c = PET_CIT[i]
        if gruppi and gruppi[-1][0] == c["f"]:
            gruppi[-1][1].append(c)
        else:
            gruppi.append((c["f"], [c]))
    for fid, cc in gruppi:
        F = PET["fonti"][fid]
        agg = f", page updated on {data_lunga(F['aggiornato_il'])}" if F.get("aggiornato_il") and fid in ("gov_rotte", "gov_aria", "gov_mare", "gov_sps") else ""
        out.append(f'<blockquote class="cit">{"".join(html_cit_pet(c) for c in cc)}</blockquote><p class="fonte">Source: {link_fonte_pet(fid)} '
                   f'({escape(F["ente"])}){agg}, checked on {data_lunga(F["letto_il"])}. Quoted word for word.</p>')
    return "".join(out)


AVVISO_PET = ('<p class="avviso"><strong>This is not veterinary advice.</strong> A missing step can mean that your pet is refused entry or put into quarantine. '
              'We quote GOV.UK and the European Commission word for word, with the date we checked them. Check with your vet and the official page before you travel.</p>')
NOTA_OGL_PET = (f'<p class="small">GOV.UK text: contains public sector information licensed under the <a href="{OGL}" rel="noopener">Open Government Licence v3.0</a>. '
                'European Commission text: reuse authorised with acknowledgement of the source. Before You Fly is not a government site.</p>')


def faq_pet(voci, extra_data):
    """FAQ da dati/animali_manuali.json: pre + citazioni intere + post; l'ultima domanda dice da dove viene la risposta."""
    out = []
    for f in voci:
        parti = ([f["pre"]] if f.get("pre") else []) + [f"“{testo_cit_pet(PET_CIT[i])}”" for i in f.get("cit", [])] + ([f["post"]] if f.get("post") else [])
        out.append((f["q"], " ".join(parti)))
    out.append(("Where does this answer come from?", f"From GOV.UK and the European Commission, read on {data_lunga(extra_data)} and quoted word for word on "
                                                     "this page. It is information, not veterinary or legal advice: check with your vet and the official page."))
    return out


def html_faq_pet(faq):
    h = "".join(f"<h3>{escape(q)}</h3><p>{escape(a)}</p>" for q, a in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    return f'<section class="faq"><h2>Questions</h2>{h}</section>', [ld]


def faq_paese_pet(p):
    """FAQ della pagina Paese dai modelli di dati/animali_manuali.json ('paese'): solo le domande con una ricerca vera per quel Paese."""
    out = []
    t = tenia_pet(p["iso2"])
    for m in PET["faq"]["paese"]:
        if m.get("solo") == "tenia" and not t or m.get("solo") == "no_tenia" and t:
            continue
        q = next((x.format(p=query_pet(p)) for x in m["query"] if x.format(p=query_pet(p)) in RICERCHE_PET), None)
        if not q:
            continue
        sost = lambda s: s.replace("{paese}", p["nome"])
        out.append({"query": q, "q": sost(m["q"]), "cit": m["cit"], "pre": sost(m.get("pre", "")), "post": sost(m.get("post", ""))})
    return out


# ---- motore del calcolatore (uguale a PET_JS; verifica.py lo confronta su casi a mano e casuali)
def _data_pet_ok(s):
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", s or ""):
        return False
    try:
        d = date.fromisoformat(s)
    except ValueError:
        return False
    return 1990 <= d.year <= 2100


def _meno_ore(giorno, ora, h):
    return (datetime.fromisoformat(f"{giorno}T{ora}") - timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M")


def calcola_pet(I):
    """I: dict di stringhe (da, specie, dest, nascita, chip, vaccino, tipo, attesa, prelievo, arrivo, ora_arrivo, ritorno, ora_ritorno).
    Regole: GOV.UK (microchip prima o insieme al vaccino; 12 settimane; almeno 21 giorni pieni, il giorno 1 è il giorno dopo il vaccino; AHC valido
    10 giorni, il giorno 1 è quello del rilascio; verme solitario tra 120 e 24 ore prima dell'arrivo; rientro in Gran Bretagna con l'AHC meno di
    6 mesi dopo l'ingresso nell'UE) e Commissione europea (prelievo almeno 30 giorni dopo il vaccino, AHC non prima di 90 giorni dal prelievo)."""
    g = lambda k: str(I.get(k) or "").strip()
    da, specie, dest, tipo = g("da") or "gb", g("specie") or "cane", g("dest"), g("tipo") or "primo"
    if da not in ("gb", "elenco", "non_elenco") or specie not in ("cane", "gatto", "furetto") or tipo not in ("primo", "richiamo") or dest not in PET_PER:
        return {"errore": "scelta", "campo": None, "esito": None, "passi": [], "primo": None}
    for k in ("chip", "vaccino", "arrivo") + (("prelievo",) if da == "non_elenco" else ()):
        if not _data_pet_ok(g(k)):
            return {"errore": "data", "campo": k, "esito": None, "passi": [], "primo": None}
    for k in ("nascita", "ritorno"):
        if g(k) and not _data_pet_ok(g(k)):
            return {"errore": "data", "campo": k, "esito": None, "passi": [], "primo": None}
    ora_a, ora_r = g("ora_arrivo") or "12:00", g("ora_ritorno") or "12:00"
    for k, o in (("ora_arrivo", ora_a), ("ora_ritorno", ora_r)):
        if not re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", o):
            return {"errore": "ora", "campo": k, "esito": None, "passi": [], "primo": None}
    attesa = 0
    if tipo == "primo":
        a = g("attesa") or "21"
        if not re.fullmatch(r"[0-9]{1,3}", a) or not 21 <= int(a) <= 365:
            return {"errore": "attesa", "campo": "attesa", "esito": None, "passi": [], "primo": None}
        attesa = int(a)
    chip, vaccino, arrivo, nascita, ritorno = g("chip"), g("vaccino"), g("arrivo"), g("nascita"), g("ritorno")
    if arrivo < vaccino:
        return {"errore": "ordine", "campo": "arrivo", "esito": None, "passi": [], "primo": None}
    if ritorno and ritorno < arrivo:
        return {"errore": "ordine", "campo": "ritorno", "esito": None, "passi": [], "primo": None}
    passi = [{"id": "chip", "esito": "ok" if chip <= vaccino else "no", "d": {"chip": chip, "vaccino": vaccino}}]
    if nascita:
        dodici = piu_giorni(nascita, 84)
        passi.append({"id": "eta", "esito": "ok" if vaccino >= dodici else "no", "d": {"dodici": dodici}})
    if tipo == "primo":
        pronto = piu_giorni(vaccino, attesa + 1)
        passi.append({"id": "attesa", "esito": "ok" if pronto <= arrivo else "no", "d": {"pronto": pronto, "giorni": attesa}})
    else:
        pronto = vaccino
        passi.append({"id": "richiamo", "esito": "ok", "d": {"pronto": pronto}})
    if da == "non_elenco":
        prelievo = g("prelievo")
        minimo, ahc_dal = piu_giorni(vaccino, 30), piu_giorni(prelievo, 90)
        passi.append({"id": "sangue", "esito": "ok" if prelievo >= minimo and ahc_dal <= arrivo else "no",
                      "d": {"minimo": minimo, "ahc_dal": ahc_dal, "prelievo_ok": prelievo >= minimo}})
        pronto = max(pronto, ahc_dal)
    if pronto <= arrivo:
        passi.append({"id": "ahc", "esito": "ok", "d": {"dal": max(piu_giorni(arrivo, -9), pronto), "al": arrivo}})
    else:
        passi.append({"id": "ahc", "esito": "no", "d": {"primo": pronto, "ultimo": piu_giorni(pronto, 9)}})
    if specie == "cane" and dest in TENIA_PET:
        passi.append({"id": "tenia", "esito": "info", "d": {"dal": _meno_ore(arrivo, ora_a, 120), "al": _meno_ore(arrivo, ora_a, 24)}})
    if da == "gb" and ritorno:
        ultimo = piu_giorni(piu_mesi(arrivo, 6), -1)
        passi.append({"id": "ritorno", "esito": "ok" if ritorno <= ultimo else "no", "d": {"ultimo": ultimo}})
        if specie == "cane":
            if dest in TENIA_PET:
                passi.append({"id": "tenia_ritorno_no", "esito": "info", "d": {}})
            else:
                passi.append({"id": "tenia_ritorno", "esito": "info", "d": {"dal": _meno_ore(ritorno, ora_r, 120), "al": _meno_ore(ritorno, ora_r, 24)}})
    return {"errore": None, "campo": None, "esito": "no" if any(x["esito"] == "no" for x in passi) else "ok", "passi": passi, "primo": pronto}


PET_MOTORE_JS = r"""
var PET_TENIA=["FI","IE","MT","NO"];
function petPd(s){var m=/^([0-9]{4})-([0-9]{2})-([0-9]{2})$/.exec(s||'');if(!m)return null;var y=+m[1],mo=+m[2],d=+m[3];if(y<1990||y>2100)return null;
  var t=Date.UTC(y,mo-1,d),x=new Date(t);return (x.getUTCFullYear()===y&&x.getUTCMonth()===mo-1&&x.getUTCDate()===d)?t:null;}
function petFd(t){return new Date(t).toISOString().slice(0,10);}
function petPg(s,n){return petFd(petPd(s)+n*864e5);}
function petPm(s,m){var y=+s.slice(0,4),mo=+s.slice(5,7),d=+s.slice(8,10);mo+=m;y+=Math.floor((mo-1)/12);mo=((mo-1)%12+12)%12+1;
  var u=[31,(y%4===0&&(y%100!==0||y%400===0))?29:28,31,30,31,30,31,31,30,31,30,31][mo-1];return String(y).padStart(4,'0')+'-'+String(mo).padStart(2,'0')+'-'+String(Math.min(d,u)).padStart(2,'0');}
function petMo(g,o,h){var t=petPd(g)+((+o.slice(0,2))*60+(+o.slice(3,5)))*6e4-h*36e5;return new Date(t).toISOString().slice(0,16);}
function calcolaPet(I,PAESI){
  var g=function(k){return String(I[k]==null?'':I[k]).trim();};
  var da=g('da')||'gb',specie=g('specie')||'cane',dest=g('dest'),tipo=g('tipo')||'primo';
  var vuoto=function(e,c){return {errore:e,campo:c,esito:null,passi:[],primo:null};};
  if(['gb','elenco','non_elenco'].indexOf(da)<0||['cane','gatto','furetto'].indexOf(specie)<0||['primo','richiamo'].indexOf(tipo)<0||PAESI.indexOf(dest)<0)return vuoto('scelta',null);
  var obb=['chip','vaccino','arrivo'].concat(da==='non_elenco'?['prelievo']:[]);
  for(var i=0;i<obb.length;i++){if(petPd(g(obb[i]))===null)return vuoto('data',obb[i]);}
  var fac=['nascita','ritorno'];for(i=0;i<fac.length;i++){if(g(fac[i])&&petPd(g(fac[i]))===null)return vuoto('data',fac[i]);}
  var oa=g('ora_arrivo')||'12:00',orr=g('ora_ritorno')||'12:00',re=/^(?:[01][0-9]|2[0-3]):[0-5][0-9]$/;
  if(!re.test(oa))return vuoto('ora','ora_arrivo');if(!re.test(orr))return vuoto('ora','ora_ritorno');
  var attesa=0;if(tipo==='primo'){var a=g('attesa')||'21';if(!/^[0-9]{1,3}$/.test(a)||+a<21||+a>365)return vuoto('attesa','attesa');attesa=+a;}
  var chip=g('chip'),vaccino=g('vaccino'),arrivo=g('arrivo'),nascita=g('nascita'),ritorno=g('ritorno');
  if(arrivo<vaccino)return vuoto('ordine','arrivo');if(ritorno&&ritorno<arrivo)return vuoto('ordine','ritorno');
  var passi=[{id:'chip',esito:chip<=vaccino?'ok':'no',d:{chip:chip,vaccino:vaccino}}],pronto;
  if(nascita){var dodici=petPg(nascita,84);passi.push({id:'eta',esito:vaccino>=dodici?'ok':'no',d:{dodici:dodici}});}
  if(tipo==='primo'){pronto=petPg(vaccino,attesa+1);passi.push({id:'attesa',esito:pronto<=arrivo?'ok':'no',d:{pronto:pronto,giorni:attesa}});}
  else{pronto=vaccino;passi.push({id:'richiamo',esito:'ok',d:{pronto:pronto}});}
  if(da==='non_elenco'){var prelievo=g('prelievo'),minimo=petPg(vaccino,30),ahcDal=petPg(prelievo,90);
    passi.push({id:'sangue',esito:(prelievo>=minimo&&ahcDal<=arrivo)?'ok':'no',d:{minimo:minimo,ahc_dal:ahcDal,prelievo_ok:prelievo>=minimo}});
    if(ahcDal>pronto)pronto=ahcDal;}
  if(pronto<=arrivo){var dal=petPg(arrivo,-9);passi.push({id:'ahc',esito:'ok',d:{dal:dal>pronto?dal:pronto,al:arrivo}});}
  else passi.push({id:'ahc',esito:'no',d:{primo:pronto,ultimo:petPg(pronto,9)}});
  if(specie==='cane'&&PET_TENIA.indexOf(dest)>=0)passi.push({id:'tenia',esito:'info',d:{dal:petMo(arrivo,oa,120),al:petMo(arrivo,oa,24)}});
  if(da==='gb'&&ritorno){var ultimo=petPg(petPm(arrivo,6),-1);passi.push({id:'ritorno',esito:ritorno<=ultimo?'ok':'no',d:{ultimo:ultimo}});
    if(specie==='cane'){if(PET_TENIA.indexOf(dest)>=0)passi.push({id:'tenia_ritorno_no',esito:'info',d:{}});
      else passi.push({id:'tenia_ritorno',esito:'info',d:{dal:petMo(ritorno,orr,120),al:petMo(ritorno,orr,24)}});}}
  return {errore:null,campo:null,esito:passi.some(function(x){return x.esito==='no';})?'no':'ok',passi:passi,primo:pronto};
}
"""

PET_UI_JS = r"""
(function(){var box=document.querySelector('[data-pet-calc]');if(!box)return;
  var D=JSON.parse(document.getElementById('pet-dati').textContent),form=box.querySelector('form'),out=box.querySelector('[data-out]');
  var MESI=['January','February','March','April','May','June','July','August','September','October','November','December'];
  var gl=function(s){var d=new Date(petPd(s.slice(0,10)));return d.getUTCDate()+' '+MESI[d.getUTCMonth()]+' '+d.getUTCFullYear()+(s.length>10?' at '+s.slice(11,16):'');};
  var esc=function(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});};
  var NOMI_CAMPI={chip:'microchip date',vaccino:'rabies vaccination date',arrivo:'date you arrive in the EU',prelievo:'blood sample date',nascita:'date of birth',ritorno:'date you come back',ora_arrivo:'arrival time',ora_ritorno:'return time'};
  try{var q=new URLSearchParams(location.search).get('dest');if(q&&D.paesi[q])form.dest.value=q;}catch(e){}
  function testo(x,I){var d=x.d,n=D.paesi[I.dest];
    switch(x.id){
      case 'chip':return x.esito==='ok'?'Microchip: put in on '+gl(d.chip)+', on or before the rabies vaccination ('+gl(d.vaccino)+').':'The microchip ('+gl(d.chip)+') was put in after the rabies vaccination ('+gl(d.vaccino)+'). GOV.UK: your pet will need to be vaccinated again.';
      case 'eta':return x.esito==='ok'?'Age: your pet was at least 12 weeks old on the vaccination date (12 weeks old on '+gl(d.dodici)+').':'Your pet was under 12 weeks old on the vaccination date (12 weeks old on '+gl(d.dodici)+'): ask your vet, the vaccination does not meet the rule.';
      case 'attesa':return 'Rabies wait: '+d.giorni+' full days, counting from the day after the vaccination. Earliest day to get the animal health certificate and enter the EU: '+gl(d.pronto)+'.'+(x.esito==='no'?' That is after your arrival date.':'');
      case 'richiamo':return 'Booster with no break in the vaccine cover: GOV.UK says you do not need to wait. Ask your vet to confirm that there was no break.';
      case 'sangue':return 'Blood test: the sample must be taken at least 30 days after the vaccination (from '+gl(d.minimo)+')'+(d.prelievo_ok?'':' – your date is too early')+', and the certificate cannot be issued until 90 days after the sample ('+gl(d.ahc_dal)+').';
      case 'ahc':return x.esito==='ok'?'Animal health certificate: have it issued between '+gl(d.dal)+' and '+gl(d.al)+'. It is valid for entering the EU for 10 days, counting the day it is issued as day 1.':'You cannot enter on that date: the earliest day for the certificate is '+gl(d.primo)+', and with a certificate issued that day you can enter up to and including '+gl(d.ultimo)+'.';
      case 'tenia':return 'Tapeworm treatment for dogs going to '+n+': a vet must give it no earlier than '+gl(d.dal)+' and no later than '+gl(d.al)+' (between 120 and 24 hours before your arrival time).';
      case 'ritorno':return x.esito==='ok'?'Coming back to Great Britain with the same certificate: arrive by '+gl(d.ultimo)+' (less than 6 months after you entered the EU).':'You come back too late for the certificate: with an animal health certificate you must be back by '+gl(d.ultimo)+' (less than 6 months after you entered the EU). After that GOV.UK says you need a Great Britain pet health certificate.';
      case 'tenia_ritorno':return 'Tapeworm treatment before you come back to Great Britain: a vet must give it between '+gl(d.dal)+' and '+gl(d.al)+'.';
      case 'tenia_ritorno_no':return 'No tapeworm treatment is needed to come back to Great Britain directly from '+n+'.';}
    return '';}
  function aggiorna(){var I={};['da','specie','dest','nascita','chip','vaccino','tipo','attesa','prelievo','arrivo','ora_arrivo','ritorno','ora_ritorno'].forEach(function(k){I[k]=form[k]?form[k].value:'';});
    box.querySelector('[data-campo=prelievo]').hidden=I.da!=='non_elenco';box.querySelector('[data-campo=attesa]').hidden=I.tipo!=='primo';
    box.querySelectorAll('[data-solo-gb]').forEach(function(e){e.hidden=I.da!=='gb';});
    if(!I.chip||!I.vaccino||!I.arrivo){out.innerHTML='<p style="margin:0">Enter the microchip date, the rabies vaccination date and the date you plan to arrive in the EU.</p>';return;}
    var R=calcolaPet(I,Object.keys(D.paesi));
    if(R.errore){var m=R.errore==='attesa'?'The wait must be a whole number of days, at least 21 (ask your vet which wait applies to the vaccine used).':
      R.errore==='ordine'?(R.campo==='arrivo'?'The arrival date is before the vaccination date.':'The return date is before the arrival date.'):
      R.errore==='ora'?'Check the '+NOMI_CAMPI[R.campo]+' (hours and minutes).':'Check the '+(NOMI_CAMPI[R.campo]||'choices')+'.';
      out.innerHTML='<p data-errore-pet style="margin:0">'+esc(m)+'</p>';return;}
    out.innerHTML='<div class="esito '+(R.esito==='ok'?'si':'no')+'"><strong>'+(R.esito==='ok'?'Your dates work with these rules':'Your dates do not work: see the points marked ✗')+'</strong></div><ul>'+
      R.passi.map(function(x){return '<li class="'+(x.esito==='no'?'ko':'ok')+'" data-passo="'+x.id+'"><span class="m">'+(x.esito==='no'?'✗':(x.esito==='ok'?'✓':'•'))+'</span>'+esc(testo(x,I))+'</li>';}).join('')+
      '</ul><p class="small" style="margin:10px 0 0">Check these dates with your vet and the official pages before you travel.</p>';}
  form.addEventListener('input',aggiorna);form.addEventListener('change',aggiorna);aggiorna();})();
"""


def modulo_pet(dest=None):
    opz = "".join(f'<option value="{p["iso2"]}"{" selected" if p["iso2"] == (dest or "FR") else ""}>{escape(p["nome"])}</option>'
                  for p in sorted(PET_PAESI, key=lambda p: p["nome"]))
    return f"""<div class="card checker" data-pet-calc>
<div class="checker-h">{ico("paw")}<span>Pet travel dates · dog, cat or ferret</span></div>
<div class="checker-b">
<form class="calc" autocomplete="off">
<div class="campi">
<label><span class="lt">{ico("globe")}Travelling from</span><select name="da"><option value="gb" selected>Great Britain (England, Scotland, Wales)</option><option value="elenco">Another non-EU country on the EU list (no blood test)</option><option value="non_elenco">A non-EU country not on the EU list (blood test)</option></select></label>
<label><span class="lt">{ico("paw")}Pet</span><select name="specie"><option value="cane" selected>Dog</option><option value="gatto">Cat</option><option value="furetto">Ferret</option></select></label>
<label><span class="lt">{ico("globe")}Arriving in</span><select name="dest">{opz}</select></label>
<label><span class="lt">{ico("calendar")}Microchip date</span><input type="date" name="chip"></label>
<label><span class="lt">{ico("calendar")}Rabies vaccination date</span><input type="date" name="vaccino"></label>
<label><span class="lt">{ico("check")}Vaccination</span><select name="tipo"><option value="primo" selected>First vaccination (or a new course)</option><option value="richiamo">Booster, no break in cover</option></select></label>
<label data-campo="attesa"><span class="lt">{ico("calendar")}Wait your vet gives (days, at least 21)</span><input type="number" name="attesa" value="21" min="21" max="365" inputmode="numeric"></label>
<label data-campo="prelievo" hidden><span class="lt">{ico("calendar")}Blood sample date</span><input type="date" name="prelievo"></label>
<label><span class="lt">{ico("calendar")}Date of birth (optional)</span><input type="date" name="nascita"></label>
<label><span class="lt">{ico("cal-in")}Date you arrive in the EU</span><input type="date" name="arrivo"></label>
<label><span class="lt">{ico("cal-in")}Arrival time</span><input type="time" name="ora_arrivo" value="12:00"></label>
<label data-solo-gb><span class="lt">{ico("cal-out")}Date you come back to GB (optional)</span><input type="date" name="ritorno"></label>
<label data-solo-gb><span class="lt">{ico("cal-out")}Time you come back</span><input type="time" name="ora_ritorno" value="12:00"></label>
</div>
</form>
<div class="risultato" data-out aria-live="polite" style="margin-top:14px"><noscript>Turn on JavaScript to use the calculator. The official rules are quoted on this page.</noscript></div>
<p class="small" style="margin:12px 0 0">{ico("lock")} The calculator runs in your browser: your dates are not sent anywhere. It applies the official sentences quoted below literally; it is not veterinary advice.</p>
</div>
</div>{dati_json("pet-dati", {"paesi": {p["iso2"]: p["nome"] for p in PET_PAESI}})}"""


def frase_calcolo_pet(R, nome):
    """Testo dell'esempio statico (stesse frasi del JS per gli esiti 'ok')."""
    out = []
    for x in R["passi"]:
        d = x["d"]
        if x["id"] == "attesa":
            out.append(f"Rabies wait: {d['giorni']} full days, counting from the day after the vaccination. Earliest day to get the animal health certificate and enter the EU: {data_lunga(d['pronto'])}.")
        elif x["id"] == "ahc" and x["esito"] == "ok":
            out.append(f"Animal health certificate: have it issued between {data_lunga(d['dal'])} and {data_lunga(d['al'])}. It is valid for entering the EU for 10 days, counting the day it is issued as day 1.")
    return out


# ---- pagine
def link_paesi_pet(rel, salta=None):
    return "".join(f'<a href="{rel}{url_pet(p)}">{escape(p["nome"])}<small>{"Dogs: tapeworm treatment" if tenia_pet(p["iso2"]) else "AHC, no tapeworm to enter"}</small></a>'
                   for p in PET_PAGINE if p["iso2"] != salta)


def pagina_indice_pet():
    rel = "../"
    d = data_lunga(data_pet())
    ids_passi = [("microchip", "1. Microchip", ["e_chip"]), ("rabies", "2. Rabies vaccination and the wait", ["e_12sett", "e_21", "e_attesa_vet", "e_richiamo"]),
                 ("ahc", "3. Animal health certificate (AHC)", ["e_ahc10", "e_ahc_ov", "e_5pets", "e_ogni_viaggio", "e_proseguire", "e_dichiarazione", "e_passaporto_no", "u_uk"]),
                 ("tapeworm", "4. Tapeworm treatment (dogs, some countries)", ["e_tenia", "e_tenia_quando", "u_tenia_paesi"]),
                 ("arrival", "5. At the border", ["e_ingresso", "u_ingresso"]),
                 ("return", "6. Coming back to Great Britain", ["g_ahc", "g_oltre6", "g_tenia", "e_ritorno_tenia", "g_rotta", "g_quarantena"])]
    passi = "".join(f'<h2 id="{k}">{escape(t)}</h2>{blocco_cit_pet(ii)}' for k, t, ii in ids_passi)
    faq_h, faq_ld = html_faq_pet(faq_pet(PET["faq"]["indice"], data_pet()))
    corpo = f"""<section class="hero">{h1_diviso(f"Taking a dog or cat from the UK to the EU ({ANNO}): what you need")}
<p class="lead" id="answer">{escape(prima_frase_pet())}</p></section>
{box_2027_pet(rel)}
{AVVISO_PET}
<section class="card" aria-label="Date calculator"><h2 style="margin-top:0">{ico("calendar")}When can your pet travel?</h2>
<p>Enter the microchip and rabies vaccination dates and the day you arrive: the <a href="{rel}{PET_CALC}">pet travel date calculator</a> gives the earliest day for the animal health certificate, the 10-day window and the tapeworm times for dogs.</p></section>
<h2>Country by country</h2>
<p>Each page adds the tapeworm rule, the European Commission's links for the points of entry and the national rules, and the approved routes back to Great Britain.</p>
<div class="griglia">{link_paesi_pet(rel)}</div>
{AD}
<h2 id="steps">What GOV.UK and the European Commission say, step by step</h2>
<p>{escape(PET_CIT["e_regole_paese"]["x"])} (GOV.UK)</p>
{passi}
<h2>Approved routes into Great Britain</h2>
<p>To come back by air, sea or rail you must use a carrier and route approved by APHA (except from Ireland, the UK, the Channel Islands and the Isle of Man): <a href="{rel}{PET_ROTTE}">every approved airline, ferry and train</a>.</p>
{faq_h}
<p class="small">Spotted a change? <a href="{rel}contact/?ref=pets">Tell us</a>. Help from the government: {escape(PET_CIT["e_aiuto"]["x"])}</p>
{NOTA_OGL_PET}"""
    desc = scegli([f"Microchip, rabies vaccine and 21-day wait, animal health certificate, tapeworm: taking a dog or cat from the UK to the EU, from GOV.UK, checked {d}.",
                   f"Taking a dog or cat from the UK to the EU: AHC, rabies, tapeworm and return rules from GOV.UK, checked on {d}."], LIMITE_DESCRIZIONE)
    pagina(f"{PET_BASE}/", scegli([f"Taking a Dog or Cat from the UK to the EU ({ANNO}): AHC Rules"], LIMITE_TITOLO_PET), desc, corpo,
           briciole=[("Pets: UK to EU", f"{PET_BASE}/")], ld_extra=faq_ld)
    LASTMOD[f"{PET_BASE}/"] = data_pet()


def prima_frase_pet():
    return (f"According to GOV.UK (Animal and Plant Health Agency), checked on {data_lunga(data_pet(['e_chip', 'e_21', 'e_ahc10', 'e_passaporto_no']))}, "
            "to take a dog, cat or ferret from Great Britain to an EU country you need a microchip, a rabies vaccination given at least 21 full days "
            "before you travel and an animal health certificate (AHC) from an official vet, which is valid for entering the EU for 10 days; if you live in "
            "England, Scotland or Wales you cannot use a pet passport.")


def box_2027_pet(rel):
    return (f'<section class="card cambio" aria-labelledby="pp2027"><h2 id="pp2027">Changes expected in 2027</h2>'
            f'<p>GOV.UK says that pet owners will be able to get a multiuse pet passport for EU travel when the UK–EU SPS agreement takes effect: '
            f'“{escape(PET_CIT["s_data"]["x"])}” Until then, the animal health certificate rules on this page apply. '
            f'<a href="{rel}{PET_PASS}">What GOV.UK says so far about the 2027 pet passport</a>.</p></section>')


def pagina_calcolatore_pet():
    rel = "../../"
    es = calcola_pet({"da": "gb", "specie": "gatto", "dest": "FR", "chip": "2026-10-01", "vaccino": "2026-10-01", "tipo": "primo", "attesa": "30", "arrivo": "2026-11-10"})
    righe_es = "".join(f"<li>{escape(x)}</li>" for x in frase_calcolo_pet(es, "France"))
    ids_regole = ["e_chip", "e_12sett", "e_21", "e_richiamo", "e_ahc10", "e_tenia_quando", "g_ahc", "g_tenia", "g_sangue", "g_sangue_3mesi", "u_titolo", "u_esenti", "u_mare"]
    faq_h, faq_ld = html_faq_pet(faq_pet(PET["faq"]["calcolatore"], data_pet()))
    d = data_lunga(data_pet(ids_regole))
    corpo = f"""<section class="hero">{h1_diviso(f"When can my dog or cat enter the EU? Pet travel date calculator ({ANNO})")}
<p class="lead" id="answer">According to GOV.UK and the European Commission, checked on {d}, a dog, cat or ferret can get its animal health certificate and enter the EU at the earliest after a wait of at least 21 full days from its first rabies vaccination (day 1 is the day after the vaccination), and must then enter within 10 days of the certificate being issued; this calculator applies those rules to your dates.</p></section>
{modulo_pet()}
{AVVISO_PET}
<h2 id="example">GOV.UK's own example, through the calculator</h2>
<p>GOV.UK: “{escape(PET_CIT["e_esempio"]["x"])}” With a vaccination and microchip on 1 October 2026, a 30-day wait and arrival on 10 November 2026, the calculator gives:</p>
<ul>{righe_es}</ul>
<h2 id="rules">The rules the calculator applies</h2>
<p>Each result above comes from one of these official sentences. Where a rule depends on the vaccine, the vet or the journey (for example a longer wait for some vaccines, or extra days for a sea crossing), the calculator asks you or leaves it out: check with your vet.</p>
{blocco_cit_pet(ids_regole)}
<p>How we count: “at least 21 full days” with day 1 the day after the vaccination means that the earliest day is the vaccination date plus 22 days; “valid for travel any time within 10 days”, with day 1 the day of issue, means up to and including the issue date plus 9 days; “less than 6 months since the date you entered the EU” means up to the day before the same date 6 months later; 12 weeks of age is 84 days after the date of birth.</p>
{AD}
<h2>Country pages</h2>
<div class="griglia">{link_paesi_pet(rel)}</div>
{faq_h}
<p class="small"><a href="{rel}{PET_BASE}/">Taking a dog or cat from the UK to the EU: all the rules</a> · <a href="{rel}{PET_PASS}">UK pet passport 2027</a> · <a href="{rel}{PET_ROTTE}">Approved routes into Great Britain</a></p>
{NOTA_OGL_PET}"""
    desc = scegli([f"Earliest date your dog, cat or ferret can enter the EU: rabies wait, animal health certificate window, tapeworm times. Official rules, checked {d}.",
                   "Pet travel date calculator: rabies wait, AHC window and tapeworm times from GOV.UK and the European Commission."], LIMITE_DESCRIZIONE)
    pagina(PET_CALC, scegli([f"Pet Travel Date Calculator: UK to EU, Rabies Wait and AHC ({ANNO})"], LIMITE_TITOLO_PET), desc, corpo,
           briciole=[("Pets: UK to EU", f"{PET_BASE}/"), ("Date calculator", PET_CALC)], js=PET_MOTORE_JS + PET_UI_JS, ld_extra=faq_ld)
    LASTMOD[PET_CALC] = data_pet(ids_regole)


def pagina_passaporto_pet():
    rel = "../../"
    ids = ["s_data", "s_passaporto", "s_trattative", "s_calendario"]
    d = data_lunga(data_pet(ids))
    F = PET["fonti"]["gov_sps"]
    sguardo = (f'<tr><th scope="row">Today</th><td>An animal health certificate for each trip from Great Britain to the EU</td></tr>'
               f'<tr><th scope="row">Expected</th><td>A multiuse pet passport valid for EU travel</td></tr>'
               f'<tr><th scope="row">When</th><td>GOV.UK: “mid-2027”, subject to negotiations; no exact date on the pages we read</td></tr>'
               f'<tr><th scope="row">Cost and how to apply</th><td>Not published on the GOV.UK pages we read</td></tr>'
               f'<tr><th scope="row">Checked</th><td>{d} (GOV.UK page updated on {data_lunga(F["aggiornato_il"])})</td></tr>')
    faq_h, faq_ld = html_faq_pet(faq_pet(PET["faq"]["passaporto"], data_pet(ids)))
    corpo = f"""<section class="hero">{h1_diviso(f"UK pet passport 2027: what GOV.UK says so far")}
<p class="lead" id="answer">According to GOV.UK (Defra), checked on {d}, the UK–EU SPS agreement is intended to take effect in mid-2027, and pet owners will then be able to get a multiuse pet passport valid for EU travel instead of a new animal health certificate for each trip; GOV.UK gives no exact date or cost yet, and until then you still need an animal health certificate.</p></section>
{AVVISO_PET}
<h2>At a glance</h2>
<div class="tab tab-g"><table><caption class="cap">UK pet passport for EU travel: what the GOV.UK pages say, checked on {d}</caption><tbody>{sguardo}</tbody></table></div>
<h2 id="official">What GOV.UK says</h2>
{blocco_cit_pet(ids)}
<h2 id="today">What you need today</h2>
{blocco_cit_pet(["e_passaporto_no", "e_ahc10", "e_ogni_viaggio"])}
{blocco_cit_pet(["u_uk"])}
<p>Step by step: <a href="{rel}{PET_BASE}/">taking a dog or cat from the UK to the EU</a>, and the <a href="{rel}{PET_CALC}">date calculator</a>.</p>
{AD}
<h2>How we follow this page</h2>
<p>We re-read the GOV.UK page at every update of this site and compare the quoted text with the previous reading: when GOV.UK publishes a date, a cost or new steps, this page changes and shows the new date of the check. Last check: {d}.</p>
{faq_h}
<p class="small">Spotted a change? <a href="{rel}contact/?ref=pets-2027">Tell us</a>.</p>
{NOTA_OGL_PET}"""
    desc = scegli([f"Will UK pet passports return in 2027? What GOV.UK says about the SPS agreement and the multiuse pet passport, checked on {d}.",
                   f"UK pet passport 2027: what GOV.UK says so far, checked on {d}."], LIMITE_DESCRIZIONE)
    pagina(PET_PASS, scegli([f"UK Pet Passport 2027: What GOV.UK Says So Far (Checked {data_lunga(data_pet(ids)).split(' ', 1)[1]})",
                             "UK Pet Passport 2027: What GOV.UK Says So Far"], LIMITE_TITOLO_PET), desc, corpo,
           briciole=[("Pets: UK to EU", f"{PET_BASE}/"), ("UK pet passport 2027", PET_PASS)], ld_extra=faq_ld)
    LASTMOD[PET_PASS] = data_pet(ids)


def righe_rotte_pet(righe, colonne, filtro=None):
    out = []
    for r in righe:
        if filtro and not filtro(r):
            continue
        out.append("<tr data-voce>" + "".join(f'<td data-l="{escape(t)}">{escape(r[k])}</td>' for k, t in colonne) + "</tr>")
    return "".join(out)


def pagina_rotte_pet():
    rel = "../../"
    R = PET["rotte"]
    ids = ["r_solo", "r_esenzioni", "g_cargo", "a_stiva", "a_aggiornate", "m_limiti", "g_compagnia"]
    d = data_lunga(data_pet(ids))
    agg = data_lunga(PET["fonti"]["gov_aria"]["aggiornato_il"])
    nc = sum(1 for r in R["aria"] if r["tipo"] == "commerciale")
    nch = R["charter"]
    col_m = [("da", "From"), ("rotta", "Route"), ("compagnia", "Company")]
    col_a = [("compagnia", "Airline"), ("aeroporti", "UK airports (animal reception centre)")]
    faq_h, faq_ld = html_faq_pet(faq_pet(PET["faq"]["rotte"], data_pet(ids)))
    corpo = f"""<section class="hero">{h1_diviso(f"Bringing a pet to Great Britain: approved airlines, ferries and trains ({ANNO})")}
<p class="lead" id="answer">According to GOV.UK (Animal and Plant Health Agency), in lists updated on {agg} and checked on {d}, you can bring a pet dog, cat or ferret into England or Scotland only with an approved carrier on an approved route ({nc} commercial airlines, {nch} charter operators, {len(R["mare"])} ferry routes, {len(R["treno"])} rail routes and {len(R["crociera"])} cruise routes), unless you travel from the UK, the Channel Islands, the Isle of Man or Ireland; there are no approved routes to Wales.</p></section>
{AVVISO_PET}
<h2 id="official">What GOV.UK says</h2>
{blocco_cit_pet(ids)}
<h2 id="ferries">Ferry routes</h2>
<div class="tab tab-b"><table><caption class="cap">Approved ferry routes into Great Britain for pets (GOV.UK, updated on {data_lunga(PET["fonti"]["gov_mare"]["aggiornato_il"])}, checked on {data_lunga(PET["fonti"]["gov_mare"]["letto_il"])})</caption><thead><tr><th>From</th><th>Route</th><th>Company</th></tr></thead><tbody>{righe_rotte_pet(R["mare"], col_m)}</tbody></table></div>
<h2 id="rail">Rail (Eurotunnel and Eurostar)</h2>
<div class="tab tab-b"><table><caption class="cap">Approved rail routes for pets (GOV.UK)</caption><thead><tr><th>Country you’re travelling from</th><th>Route</th><th>Company</th></tr></thead><tbody>{righe_rotte_pet(R["treno"], [("da", "From"), ("rotta", "Route"), ("compagnia", "Company")])}</tbody></table></div>
<h2 id="cruises">Cruises</h2>
<div class="tab tab-b"><table><caption class="cap">Approved cruise routes for pets (GOV.UK)</caption><thead><tr><th>Country you’re travelling from</th><th>Route</th><th>Company</th></tr></thead><tbody>{righe_rotte_pet(R["crociera"], [("da", "From"), ("rotta", "Route"), ("compagnia", "Company")])}</tbody></table></div>
{AD}
<h2 id="airlines">Airlines and UK airports</h2>
<p>{escape(PET_CIT["a_stiva"]["x"])} (GOV.UK, about the {nc} commercial airlines.) Type an airline or an airport to filter.</p>
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Type an airline or airport, e.g. Air Canada or Manchester" data-filtro-multi aria-label="Search airlines and airports"></div>
<h3>Commercial airlines</h3>
<div class="tab tab-b"><table><caption class="cap">Approved commercial airlines for pets travelling to Great Britain (GOV.UK, updated on {agg})</caption><thead><tr><th>Airline</th><th>UK airports (animal reception centre)</th></tr></thead><tbody>{righe_rotte_pet(R["aria"], col_a, lambda r: r["tipo"] == "commerciale")}</tbody></table></div>
<h3>Charter airlines</h3>
<p>GOV.UK also lists {nch} approved charter operators (private and business flights), each with the UK airports it can fly pets to. We do not copy that list here: see <a href="{escape(PET["fonti"]["gov_aria"]["pagina"])}#charter-airlines" rel="noopener">section 2, “Charter airlines”, of the GOV.UK list</a>.</p>
<p class="small">Tables copied row by row from GOV.UK. Ask the carrier whether it will take your pet on your date before you book.</p>
{faq_h}
<p class="small"><a href="{rel}{PET_BASE}/">Taking a dog or cat from the UK to the EU</a> · <a href="{rel}{PET_CALC}">Pet travel date calculator</a> · <a href="{rel}{PET_PASS}">UK pet passport 2027</a></p>
{NOTA_OGL_PET}"""
    desc = scegli([f"Which airlines, ferries and trains can bring a dog, cat or ferret into Great Britain: the APHA approved routes from GOV.UK, updated {agg}.",
                   "Approved airlines, ferries and trains for pets travelling to Great Britain, from GOV.UK."], LIMITE_DESCRIZIONE)
    pagina(PET_ROTTE, scegli([f"Bringing a Pet to Great Britain: Approved Airlines and Ferries ({ANNO})", f"Pets into Great Britain: Approved Airlines and Ferries ({ANNO})"],
                             LIMITE_TITOLO_PET), desc, corpo, briciole=[("Pets: UK to EU", f"{PET_BASE}/"), ("Approved routes", PET_ROTTE)],
           js=APP_JS_FILTRO, ld_extra=faq_ld)
    LASTMOD[PET_ROTTE] = data_pet(ids)


def rotte_ritorno_pet(p):
    """Rotte via mare e treno approvate DAL Paese verso la Gran Bretagna (tabella GOV.UK)."""
    nome = PET_DAL_MARE.get(p["iso2"], p["nome"])
    R = PET["rotte"]
    return [r for r in R["mare"] if r["da"] == nome] + [r for r in R["treno"] if r["da"] == nome] + [r for r in R["crociera"] if r["da"] == nome]


def risposta_paese_pet(p):
    n = p["nome"]
    base = (f"According to GOV.UK and the European Commission, checked on {data_lunga(data_pet())}, to take a dog, cat or ferret from Great Britain to {n} you need "
            "a microchip, a rabies vaccination given at least 21 full days before you travel and an animal health certificate, valid for entering the EU for 10 days")
    if tenia_pet(p["iso2"]):
        return base + (f"; {n} is on GOV.UK's tapeworm list, so a vet must treat your dog no less than 24 hours and no more than 120 hours before you arrive, "
                       f"and no tapeworm treatment is needed to come back to Great Britain directly from {n}.")
    return base + f"; {n} is not on GOV.UK's tapeworm list, so dogs need no tapeworm treatment to enter, but they need one before coming back to Great Britain."


def pagina_paese_pet(p):
    rel = "../../"
    c, n = p["iso2"], p["nome"]
    t = tenia_pet(c)
    rotte = rotte_ritorno_pet(p)
    dp = data_lunga(data_pet())
    ing = "".join(f'<a href="{escape(u)}" rel="noopener">{"Points of entry" if i == 0 else "Points of entry (English version)"}</a> ' for i, u in enumerate(p["ingresso"]))
    info = "".join(f'<a href="{escape(u)}" rel="noopener">{"National information" if i == 0 else "National information (English version)"}</a> ' for i, u in enumerate(p["info"]))
    if c == "IE":
        ritorno_rotte = f"<p>Approved routes are not needed from Ireland. GOV.UK says:</p>{blocco_cit_pet(['g_rotta'])}"
        breve_rotte = "Not needed from Ireland (GOV.UK)"
    elif rotte:
        ritorno_rotte = (f'<div class="tab tab-b"><table><caption class="cap">Approved routes from {escape(n)} to Great Britain for pets (GOV.UK, updated on '
                         f'{data_lunga(PET["fonti"]["gov_mare"]["aggiornato_il"])})</caption><thead><tr><th>Route</th><th>Company</th></tr></thead><tbody>'
                         f'{righe_rotte_pet(rotte, [("rotta", "Route"), ("compagnia", "Company")])}</tbody></table></div>')
        breve_rotte = f"{len(rotte)} by sea or rail, plus approved airlines"
    else:
        ritorno_rotte = (f'<p>GOV.UK lists no approved ferry, rail or cruise route from {escape(n)}: by air, pets travel as cargo with an approved airline, '
                         f'or you can drive to an approved route from another country (for example the ferries and Eurotunnel from France). '
                         f'See <a href="{rel}{PET_ROTTE}#airlines">the approved airlines and UK airports</a> and <a href="{rel}{PET_ROTTE}#ferries">the ferry and rail routes</a>.</p>')
        breve_rotte = f"No sea or rail route from {n} in the GOV.UK list: approved airlines, or a listed route from another country"
    sguardo = (f'<tr><th scope="row">Document</th><td>Animal health certificate from an official vet (a pet passport cannot be used if you live in England, Scotland or Wales)</td></tr>'
               f'<tr><th scope="row">Rabies</th><td>At least 21 full days after the first vaccination</td></tr>'
               f'<tr><th scope="row">Tapeworm to enter (dogs)</th><td>{"Yes: 24 to 120 hours before you arrive" if t else "No"}</td></tr>'
               f'<tr><th scope="row">Tapeworm to return to GB (dogs)</th><td>{"No, directly from " + escape(n) if t else "Yes: 24 hours to 5 days before you arrive back"}</td></tr>'
               f'<tr><th scope="row">Approved routes back to GB</th><td>{escape(breve_rotte)}</td></tr>'
               f'<tr><th scope="row">Checked</th><td>{dp}</td></tr>')
    faq_h, faq_ld = html_faq_pet(faq_pet(faq_paese_pet(p), data_pet()))
    altri = link_paesi_pet(rel, salta=c)
    guida = link_guida_pet(rel, c)
    corpo = f"""<section class="hero">{h1_diviso(f"Taking your dog or cat from the UK to {n} ({ANNO})")}</section>
<section class="card summary" aria-label="Answer">
<div class="s-top"><span class="sq">{ico("paw")}</span><span>Pets · UK to {escape(n)}</span><span>{ANNO}</span></div>
<div class="s-body"><p class="lead" id="answer">{escape(risposta_paese_pet(p))}</p></div></section>
{box_2027_pet(rel)}
{AVVISO_PET}
<h2>At a glance</h2>
<div class="tab tab-g"><table><caption class="cap">Taking a pet from Great Britain to {escape(n)}: our summary of the official sources, checked on {dp}</caption><tbody>{sguardo}</tbody></table></div>
<section class="card" aria-label="Date calculator" style="margin-top:18px"><h2 style="margin-top:0">{ico("calendar")}Your dates for {escape(n)}</h2>
<p><a href="{rel}{PET_CALC}?dest={c}">Open the date calculator for {escape(n)}</a>: earliest day for the animal health certificate, the 10-day window{", the tapeworm times" if t else ""} and the date you must be back.</p></section>
<h2 id="official">What GOV.UK says</h2>
{blocco_cit_pet(["e_chip", "e_21", "e_ahc10", "e_ahc_ov", "e_passaporto_no"])}
<h2 id="tapeworm">Tapeworm treatment for dogs</h2>
{f"<p>{escape(n)} is on the GOV.UK list:</p>" if t else f"<p>{escape(n)} is not on the GOV.UK list, so there is no tapeworm rule to enter:</p>"}
{blocco_cit_pet(["e_tenia", "e_tenia_quando"] if t else ["e_tenia"])}
<h2 id="arrival">Arriving in {escape(n)}</h2>
{blocco_cit_pet(["e_ingresso", "e_regole_paese"])}
<p>The European Commission links these official pages for {escape(n)}: {ing}{info if info else "(no link to national information on the Commission page on " + dp + ")"}</p>
{blocco_cit_pet(["p_intro"])}
{AD}
<h2 id="return">Coming back to Great Britain from {escape(n)}</h2>
{blocco_cit_pet(["g_ahc", "g_oltre6"] + (["e_ritorno_tenia"] if t else ["g_tenia"]))}
{ritorno_rotte}
{guida}
<h2>Other countries</h2>
<div class="griglia">{altri}</div>
{faq_h}
<p class="small">Spotted a change? <a href="{rel}contact/?ref=pets">Tell us</a>. <a href="{rel}{PET_BASE}/">Taking a dog or cat from the UK to the EU: all the rules</a> · <a href="{rel}{PET_ROTTE}">Approved routes</a></p>
{NOTA_OGL_PET}"""
    desc = scegli([f"Taking a dog or cat from the UK to {n}: microchip, rabies wait, animal health certificate{', tapeworm' if t else ''} and the way back. Official, checked {dp}.",
                   f"Taking a dog or cat from the UK to {n}: rules from GOV.UK and the European Commission, checked on {dp}."], LIMITE_DESCRIZIONE)
    pagina(url_pet(p), scegli([f"Taking a Dog from the UK to {n} ({ANNO}): AHC and Rules", f"Taking a Dog from the UK to {n} ({ANNO})"], LIMITE_TITOLO_PET), desc, corpo,
           briciole=[("Pets: UK to EU", f"{PET_BASE}/"), (n, url_pet(p))], ld_extra=faq_ld)
    LASTMOD[url_pet(p)] = data_pet()


def link_guida_pet(rel, c):
    """Collegamenti con le sezioni sulla guida (patente britannica, pedaggi) dello stesso Paese: chi va in auto con il cane passa da lì."""
    voci = []
    if PAT and c in PAGINE_PAT.get("uk", []):
        voci.append(f'<a href="{rel}{url_pat("uk", c)}">Driving in {escape(PET_PER[c]["nome"])} with a UK licence</a>')
    if PED and c in PED_PER:
        voci.append(f'<a href="{rel}{url_ped(c)}">Tolls in {escape(PED_PER[c]["nome_frase"])}</a>')
    if not voci:
        return ""
    return f'<p class="altri-pass">{ico("car")}<span>Driving there with your pet? {" · ".join(voci)}</span></p>'


def link_pet(rel, c):
    """Riga 'Travelling with your dog?' nelle pagine dello stesso Paese di altre sezioni (Driving abroad UK, Tolls)."""
    p = PET_PER.get(c)
    if not PET or not p or not ha_pagina_pet(c):
        return ""
    return (f'<p class="altri-pass">{ico("paw")}<span>Taking your dog or cat? <a href="{rel}{url_pet(p)}">Pet rules from the UK to {escape(p["nome"])}: '
            f'animal health certificate, rabies{", tapeworm" if tenia_pet(c) else ""}</a></span></p>')


def home_pet():
    if not PET:
        return ""
    voci = "".join(f'<a href="{url_pet(p)}">{escape(p["nome"])}<small>{"Dogs: tapeworm treatment" if tenia_pet(p["iso2"]) else "AHC, no tapeworm to enter"}</small></a>'
                   for p in PET_PAGINE[:12])
    return (f'<h2>Travelling with a dog or cat from the UK</h2><p>Microchip, rabies vaccination, animal health certificate and tapeworm rules from GOV.UK: '
            f'<a href="{PET_BASE}/">taking a pet from the UK to the EU</a>, the <a href="{PET_CALC}">pet travel date calculator</a>, the '
            f'<a href="{PET_PASS}">2027 pet passport</a> and the <a href="{PET_ROTTE}">approved routes into Great Britain</a>.</p><div class="griglia">{voci}</div>')


def about_pet(rel):
    if not PET:
        return ""
    return f"""<h2 id="{PET_BASE}">Pets: from the UK to the EU</h2>
<p>Sources: GOV.UK guides of the Animal and Plant Health Agency (“Taking your pet dog, cat or ferret abroad”, “Bringing your pet dog, cat or ferret to Great Britain”), the Defra page on the UK–EU SPS agreement for the veterinary sector, the GOV.UK lists of approved air, sea and rail carriers and routes, read through the GOV.UK Content API, and three pages of the European Commission (DG Health and Food Safety) on bringing pets into the EU, the travellers' points of entry and each country's information, {len(PET["fonti"])} pages in all, read on {data_lunga(PET["controllato_il"])}. GOV.UK text is licensed under the <a href="{OGL}" rel="noopener">Open Government Licence v3.0</a>.</p>
<p>Rules: every sentence between quotation marks is copied word for word; the tables of approved routes are copied row by row; the summaries and the date calculator are ours. The European Commission's page says that the EU rules are now in Commission Delegated Regulation (EU) 2026/131; EUR-Lex does not answer our automated checks, so we quote the Commission's own summary of the rules rather than the regulation itself. We give no veterinary advice: every page says to check with your vet and the official page. A country gets a page only when people search for taking a pet there from the UK. This is information, not legal advice.</p>"""


# ---------------------------------------------------------------- Blue Badge all'estero, Paese per Paese, e le carte europee (4/11/2026)
# Piano: studio-business/intelaiatura/idee-2026-11-04-europa.md (idea 2). Fatti scritti a mano in dati/bluebadge_manuali.json (citazioni parola per
# parola da GOV.UK, FCDO, Your Europe e Commissione europea, governo italiano e francese), fonti rilette da raccolta/bluebadge.py (HTTP 200, data,
# impronta) che copia anche la tabella GOV.UK riga per riga e scrive dati/bluebadge.json. Una pagina Paese solo con una ricerca vera sul Paese.
# Nessun consiglio legale; nessun link di affiliazione (nessun programma pertinente; il riquadro DiscoverCars resta nelle sue sezioni); AdSense sì.
BB_BASE = "blue-badge-abroad"
BB_CARTE = f"{BB_BASE}/european-disability-card/"
_f_bb = DATI / "bluebadge.json"
BB = json.loads(_f_bb.read_text(encoding="utf-8")) if _f_bb.exists() else None
BB_PAESI = BB["paesi"] if BB else []
BB_PER = {p["iso2"]: p for p in BB_PAESI}
BB_PAGINE = [p for p in BB_PAESI if p["pagina"]]
BB_CIT = {c["id"]: c for c in BB["citazioni"]} if BB else {}
LIMITE_TITOLO_BB = 70
# Etichette nostre della cella "UK Blue Badge recognised" della tabella GOV.UK (la cella si mostra sempre parola per parola accanto)
ESITI_BB = {"si": "Recognised", "non_ue": "Accepts non-EU cards", "regioni": "Some regions only", "forse_no": "May not be recognised",
            "locale": "Decided locally", "non_detto": "No information"}
BREVE_BB = {"si": "Yes", "non_ue": "Accepted", "regioni": "In Some Regions", "forse_no": "Maybe Not", "locale": "It Depends", "non_detto": "No Information"}
LINGUE_BB = {"it": "Italian", "fr": "French"}
TEMI_YE_BB = [("generale", "General rules"), ("strada", "Parking on the street"), ("parcheggi", "In car parks")]


def url_bb(p=None):
    return f"{BB_BASE}/" + (f"{p['slug']}/" if p else "")


def ha_pagina_bb(c):
    return bool(BB_PER.get(c, {}).get("pagina"))


def fonte_bb(fid):
    return BB["fonti"][fid]


def link_fonte_bb(fid):
    F = fonte_bb(fid)
    return f'<a href="{escape(F["pagina"])}" rel="noopener">{escape(F["titolo"])}</a>'


def data_fonte_bb(fid):
    """'page updated on X, checked on Y' (la data di aggiornamento solo quando la fonte la dichiara)."""
    F = fonte_bb(fid)
    agg = f"page updated on {data_lunga(F['aggiornato_il'])}, " if F.get("aggiornato_il") else ""
    return f"{agg}checked on {data_lunga(F['letto_il'])}"


def blocco_cit_bb(ids):
    """Citazioni raggruppate per fonte, con link, ente e date; traduzione nostra sotto le citazioni non in inglese."""
    out, gruppi = [], []
    for i in ids:
        c = BB_CIT[i]
        if gruppi and gruppi[-1][0] == c["f"]:
            gruppi[-1][1].append(c)
        else:
            gruppi.append((c["f"], [c]))
    for fid, cc in gruppi:
        F = fonte_bb(fid)
        lingua = f' lang="{F["lingua"]}"' if F["lingua"] != "en" else ""
        h = "".join(f"<p>{escape(c['x'])}</p>" + (f'<p class="trad" lang="en"><em>Our translation:</em> {escape(c["tr"])}</p>' if c.get("tr") else "")
                    for c in cc)
        lin = f" Quoted word for word in {LINGUE_BB[F['lingua']]}." if F["lingua"] != "en" else " Quoted word for word."
        out.append(f'<blockquote class="cit"{lingua}>{h}</blockquote><p class="fonte">Source: {link_fonte_bb(fid)} ({escape(F["ente"])}), '
                   f'{data_fonte_bb(fid)}.{lin}</p>')
    return "".join(out)


def data_bb(ids):
    return max(fonte_bb(BB_CIT[i]["f"])["letto_il"] for i in ids)


def fonti_pagina_bb(p):
    """Fonti citate nella pagina di un Paese (per la data della pagina e i controlli)."""
    return sorted({BB_CIT[i]["f"] for i in ids_pagina_bb(p)} | {"gov_eu"})


def ids_pagina_bb(p):
    G, c = BB["generali"], p["iso2"]
    ids = list(G["govuk"]) + (G["disco"] if p["info"] else []) + list(G["fcdo"].get(c, []))
    if c == "ES":
        ids += G["spagna"]
    if c == "IT":
        ids += G["italia"]
    if c == "FR":
        ids += G["francia"]
    ids += list(G["ye"].get(c, {}).values()) + (G["ue_paese"] if p["ye"] else G["non_ue"])
    return list(dict.fromkeys(ids))


def data_pagina_bb(p):
    return max(fonte_bb(f)["letto_il"] for f in fonti_pagina_bb(p))


def prefisso_bb():
    F = fonte_bb("gov_eu")
    return (f"According to GOV.UK (Department for Transport), in guidance updated on {data_lunga(F['aggiornato_il'])} and checked on "
            f"{data_lunga(F['letto_il'])}, ")


def risposta_bb(p):
    return prefisso_bb() + p["risposta"]


def faq_bb(voci):
    """FAQ: pre + citazioni intere (la traduzione nostra per le fonti non in inglese, annunciata nel pre) + post (JSON-LD = testo visibile)."""
    out = []
    for f in voci:
        parti = (([f["pre"]] if f.get("pre") else []) + [f"“{BB_CIT[i].get('tr') or BB_CIT[i]['x']}”" for i in f.get("cit", [])]
                 + ([f["post"]] if f.get("post") else []))
        out.append((f["q"], " ".join(parti)))
    return out


def html_faq_bb(faq):
    h = "".join(f"<h3>{escape(q)}</h3><p>{escape(a)}</p>" for q, a in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    return f'<section class="faq"><h2>Questions</h2>{h}</section>', [ld]


AVVISO_BB = ('<p class="avviso"><strong>This is information, not legal advice.</strong> Parking rules for disabled people differ from town to town and '
             'change. We quote GOV.UK, the European Commission and national governments word for word, with the date we checked them. Always check the '
             'local signs and rules before you park, and ask the local authority when the official answer is unclear.</p>')
NOTA_LIC_BB = (f'<p class="small">GOV.UK text: contains public sector information licensed under the <a href="{OGL}" rel="noopener">Open Government Licence v3.0</a>. '
               'European Commission text: reuse authorised with acknowledgement of the source. Before You Fly is not a government site.</p>')


def storico_paese_bb(p):
    """Note di modifica della pubblicazione GOV.UK che nominano il Paese (data e nota, parola per parola)."""
    return [s for s in BB["storico_govuk"] if re.search(r"\b" + re.escape(p["nome"]) + r"\b", s["nota"])]


def riga_govuk_bb(p):
    return (f'<div class="tab tab-b"><table><caption class="cap">Row copied from the GOV.UK table “Links to country information”, '
            f'{data_fonte_bb("gov_eu")}</caption><thead><tr><th>Country or territory</th><th>UK Blue Badge recognised</th><th>More information</th></tr></thead>'
            f'<tbody><tr><td>{escape(p["nome_gov"])}</td><td>{escape(p["riconosciuto"])}</td><td>{escape(p["info"]) or "–"}</td></tr></tbody></table></div>')


def link_guida_bb(rel, c):
    """Collegamenti con Driving abroad (patente britannica) e con i pedaggi dello stesso Paese."""
    voci = []
    if PAT and c in PAGINE_PAT.get("uk", []):
        voci.append(f'<a href="{rel}{url_pat("uk", c)}">Driving in {escape(BB_PER[c]["nome"])} with a UK licence: do you need an IDP?</a>')
    if PED and c in PED_PER:
        voci.append(f'<a href="{rel}{url_ped(c)}">Tolls in {escape(PED_PER[c]["nome_frase"])}</a>')
    return f'<p class="altri-pass">{ico("car")}<span>Driving there? {" · ".join(voci)}</span></p>' if voci else ""


def link_bb(rel, c):
    """Riga 'Blue Badge holder?' nelle pagine Driving abroad della patente britannica dello stesso Paese."""
    p = BB_PER.get(c)
    if not BB or not p or not p["pagina"]:
        return ""
    return (f'<p class="altri-pass">{ico("car")}<span>Blue Badge holder? <a href="{rel}{url_bb(p)}">Using a UK Blue Badge in {escape(nf_bb(p))}: '
            f'{escape(esito_min_bb(p))} (GOV.UK) and where you can park</a></span></p>')


def nf_bb(p):
    """Nome del Paese nelle frasi ("the Netherlands")."""
    return p.get("nome_frase") or p["nome"]


def h1_bb(p):
    return f"Using a UK Blue Badge in {nf_bb(p)}: is it recognised and where can you park? ({ANNO})"


def titoli_bb(p):
    n = nf_bb(p)
    return [f"Can I Use My UK Blue Badge in {n}? {BREVE_BB[p['esito']]} ({ANNO})", f"UK Blue Badge in {n}? {BREVE_BB[p['esito']]} ({ANNO})",
            f"UK Blue Badge in {n} ({ANNO})"]


def descrizione_bb(p):
    d = data_lunga(data_pagina_bb(p))
    n = nf_bb(p)
    fine = "" if p["riconosciuto"].endswith(".") else "."
    cosa = "Local parking rules and what to carry" if p["ye"] else "What GOV.UK says and what to carry"
    cosa2 = "Local parking rules" if p["ye"] else "GOV.UK guidance"
    return scegli([f"UK Blue Badge in {n}: GOV.UK says “{p['riconosciuto']}”{fine} {cosa}, from official sources checked on {d}.",
                   f"UK Blue Badge in {n}: {esito_min_bb(p)} (GOV.UK). {cosa2} from official sources, checked on {d}.",
                   f"Using a UK Blue Badge in {n}: official sources, checked on {d}."], LIMITE_DESCRIZIONE)


def esito_min_bb(p):
    """Etichetta dell'esito con la prima lettera minuscola (le sigle, come EU, restano maiuscole)."""
    e = ESITI_BB[p["esito"]]
    return e[0].lower() + e[1:]


def sguardo_bb(p):
    G, c = BB["generali"], p["iso2"]
    fc = fonte_bb(f"fcdo_{c}")
    fcdo = ("Mentions the Blue Badge (quoted below)" if G["fcdo"].get(c) else "Does not mention the Blue Badge")
    st = storico_paese_bb(p)
    return (f'<tr><th scope="row">GOV.UK: UK Blue Badge recognised</th><td>“{escape(p["riconosciuto"])}” ({escape(ESITI_BB[p["esito"]])})</td></tr>'
            f'<tr><th scope="row">Extra requirement (GOV.UK)</th><td>{"“" + escape(p["info"]) + "”" if p["info"] else "None stated in the table"}</td></tr>'
            f'<tr><th scope="row">FCDO travel advice</th><td>{fcdo} (page updated on {data_lunga(fc["aggiornato_il"])})</td></tr>'
            f'<tr><th scope="row">Local parking rules</th><td>{"Your Europe page for the EU parking card (quoted below)" if p["ye"] else "Not covered by Your Europe (not in the EU)"}</td></tr>'
            f'<tr><th scope="row">Latest GOV.UK change for {escape(nf_bb(p))}</th><td>{escape(data_lunga(st[0]["data"]) + ": " + st[0]["nota"]) if st else "None in the change history"}</td></tr>'
            f'<tr><th scope="row">Checked</th><td>{data_lunga(data_pagina_bb(p))}</td></tr>')


def govuk_bb(p):
    """Frasi generali della guida GOV.UK con i titoli della guida («Check before you travel», «Local rules», «Supporting documents»);
    la frase sul disco orario solo nei Paesi con l'obbligo nella tabella (Danimarca, Svizzera)."""
    G = BB["generali"]
    locali = ["g_local", "g_research"] + (G["disco"] if p["info"] else []) + ["g_always"]
    return (f'<h3>Check before you travel</h3>{blocco_cit_bb(["g_check"])}<h3>Local rules</h3>{blocco_cit_bb(locali)}'
            f'<h3>Supporting documents</h3>{blocco_cit_bb(["g_docs"])}')


def pagina_paese_bb(p):
    rel = "../../"
    G, c, n = BB["generali"], p["iso2"], nf_bb(p)
    fc = G["fcdo"].get(c, [])
    fcdo = (blocco_cit_bb(fc) if fc else f'<p>The FCDO travel advice for {escape(n)} does not mention the Blue Badge ({link_fonte_bb(f"fcdo_{c}")}, '
                                             f'{data_fonte_bb(f"fcdo_{c}")}).</p>')
    nazionale = ""
    if c == "IT":
        nazionale = (f'<h2 id="italy">What the Italian government says</h2><p>A circular of 28 September 2026 from the Ministry of Infrastructure and Transport and '
                     f'the Department for policies for persons with disabilities tells the police and the towns how to treat UK Blue Badges:</p>'
                     f'{blocco_cit_bb(["it_c1", "it_c2", "it_c3"])}<p>The Department’s page on the Italian card adds:</p>{blocco_cit_bb(["it_uk", "it_bordo"])}'
                     f'<h3>Where you can park in Italy</h3><p>Yellow lines mark the reserved bays; blue lines mark paid parking bays.</p>'
                     f'{blocco_cit_bb(["it_gialle", "it_blu"])}'
                     f'<h3 id="ztl">Limited Traffic Zones (ZTL)</h3>{blocco_cit_bb(["it_ztl", "it_adesione", "it_altri"])}'
                     f'<p>The Italian pages describe permission or reporting through the town, before or after driving through depending on the town, and do not '
                     f'say how this works with a UK Blue Badge (our reading): ask the town (Comune) you are visiting.</p>')
    elif c == "ES":
        nazionale = (f'<h2 id="spain">Spain: recognition decided locally</h2><p>GOV.UK’s table marks Spain with a note:</p>{blocco_cit_bb(["g_spain"])}'
                     f'<p>In September 2025 the UK government said, after a meeting with the Spanish government:</p>{blocco_cit_bb(["es_accordo"])}'
                     f'<p>GOV.UK’s change history for Spain: {"; ".join(escape(data_lunga(s["data"]) + ": " + s["nota"].rstrip(".")) for s in storico_paese_bb(p))}.</p>')
    elif c == "FR":
        nazionale = (f'<h2 id="france">The French card (CMI)</h2><p>The French government describes the French card, the carte mobilité inclusion (CMI), like this:</p>'
                     f'{blocco_cit_bb(["fr_mention", "fr_cmi1", "fr_cmi2"])}<p>In short, for the French card: free of charge; a town may set a time limit, never '
                     f'under 12 hours; barrier car parks may charge. GOV.UK does not say whether a UK Blue Badge gets exactly the same in France, and Your Europe '
                     f'(below) says that you must pay where street parking is paid, except in Paris and some other cities.</p>')
    ye = G["ye"].get(c, {})
    if ye:
        intro = ("GOV.UK says what a recognised Blue Badge gives you (GOV.UK page from 2014):" if p["esito"] == "si" else
                 "If the Blue Badge is recognised where you park, GOV.UK says (GOV.UK page from 2014):")
        locali = (f'<p>{intro}</p>{blocco_cit_bb(["p_same"])}'
                  f'<p>Your Europe, the European Commission’s guide, gives these local rules for holders of the EU parking card in {escape(n)}:</p>'
                  + "".join(f'<h3>{t}</h3>{blocco_cit_bb([ye[k]])}' for k, t in TEMI_YE_BB if k in ye)
                  + f'<p>On using a parking card in another EU country, Your Europe says:</p>{blocco_cit_bb(["ye_warn", "ye_display"])}')
    else:
        locali = (f'<p>Your Europe, the European Commission’s guide to local parking rules, covers EU countries only, and {escape(n)} is not in the EU. '
                  f'GOV.UK says:</p>{blocco_cit_bb(["p_differ"])}')
    altri = "".join(f'<a href="{rel}{url_bb(x)}">{escape(x["nome"])}<small>{escape(ESITI_BB[x["esito"]])}</small></a>' for x in BB_PAGINE if x["iso2"] != c)
    faq_h, faq_ld = html_faq_bb(faq_bb(p["faq"]))
    d = data_lunga(data_pagina_bb(p))
    corpo = f"""<section class="hero">{h1_diviso(h1_bb(p))}</section>
<section class="card summary" aria-label="Answer">
<div class="s-top"><span class="sq">{ico("car")}</span><span>Blue Badge · {escape(p["nome"])}</span><span>{ANNO}</span></div>
<div class="s-body">
<p class="lead" id="answer">{escape(risposta_bb(p))}</p>
{f'<p class="small" data-nota>{escape(p["nota"])}</p>' if p.get("nota") else ""}
</div></section>
{AVVISO_BB}
<h2>At a glance</h2>
<div class="tab tab-g"><table><caption class="cap">UK Blue Badge in {escape(n)}: our summary of the official sources, checked on {d}</caption><tbody>{sguardo_bb(p)}</tbody></table></div>
<h2 id="official">What GOV.UK says</h2>
{riga_govuk_bb(p)}
{govuk_bb(p)}
<h3>FCDO travel advice for {escape(n)}</h3>
{fcdo}
{nazionale}
<h2 id="local">Where you can park: local rules</h2>
{locali}
{AD}
{link_guida_bb(rel, c)}
<p class="altri-pass">{ico("calendar")}<span>Coming in 2027 and 2028: <a href="{rel}{BB_CARTE}">the European Disability Card and European Parking Card</a></span></p>
<h2>Other countries</h2>
<div class="griglia">{altri}</div>
<p><a href="{rel}{BB_BASE}/">Blue Badge abroad: every country in one table</a> · <a href="{rel}{PAT_BASE}/">Driving abroad: do you need an international driving permit?</a></p>
{faq_h}
<p class="small">Spotted a change? <a href="{rel}contact/?ref={BB_BASE}">Tell us</a>.</p>
{NOTA_LIC_BB}"""
    pagina(url_bb(p), scegli(titoli_bb(p), LIMITE_TITOLO_BB), descrizione_bb(p), corpo,
           briciole=[("Blue Badge abroad", f"{BB_BASE}/"), (p["nome"], url_bb(p))], ld_extra=faq_ld)
    LASTMOD[url_bb(p)] = data_pagina_bb(p)


def conti_bb():
    return {e: [p for p in BB_PAESI if p["esito"] == e] for e in ESITI_BB}


def prima_frase_bb():
    k = conti_bb()
    nomi = lambda e: ", ".join(p["nome"] for p in k[e])
    frase = (f"the UK Blue Badge is recognised (“Yes”) in {len(k['si'])} of the {len(BB_PAESI)} European countries in its table; "
             f"{len(k['non_ue'])} more accept non-EU parking cards ({nomi('non_ue')})")
    poco = [p["nome"] + " (" + p["riconosciuto"].rstrip(".") + ")" for e in ("regioni", "forse_no", "non_detto") for p in k[e]]
    if k["locale"]:
        frase += f"; in {nomi('locale')} recognition is decided by local administrations"
    if poco:
        frase += f"; less clear: {'; '.join(poco)}"
    return prefisso_bb() + frase + "."


def riga_bb(p, rel):
    G = BB["generali"]
    nome = f'<a href="{rel}{url_bb(p)}">{escape(p["nome_gov"])}</a>' if p["pagina"] else escape(p["nome_gov"])  # nome come lo scrive GOV.UK
    fcdo = "Mentions it" if G["fcdo"].get(p["iso2"]) else "Does not mention it"
    return (f'<tr data-voce id="{p["iso2"].lower()}"><td data-l="Country">{nome}</td><td data-l="UK Blue Badge recognised (GOV.UK)">{escape(p["riconosciuto"])}</td>'
            f'<td data-l="More information (GOV.UK)">{escape(p["info"]) or "–"}</td><td data-l="FCDO travel advice">{fcdo}</td></tr>')


def pagina_indice_bb():
    rel = "../"
    d = data_lunga(BB["controllato_il"])
    righe = "".join(riga_bb(p, rel) for p in BB_PAESI)
    voci = "".join(f'<a href="{rel}{url_bb(p)}">{escape(p["nome"])}<small>{escape(ESITI_BB[p["esito"]])}</small></a>' for p in BB_PAGINE)
    faq_h, faq_ld = html_faq_bb(faq_bb(BB["faq_indice"]))
    corpo = f"""<section class="hero">{h1_diviso(f"Blue Badge abroad: where your UK Blue Badge is recognised in Europe ({ANNO})")}
<p class="lead" id="answer">{escape(prima_frase_bb())}</p></section>
{AVVISO_BB}
<h2>Countries</h2>
<div class="griglia">{voci}</div>
{AD}
<h2>Every country in the GOV.UK table</h2>
<p>The country names and the two GOV.UK columns are copied word for word from “Using a Blue Badge in Europe” ({data_fonte_bb("gov_eu")}). The last column says whether the FCDO travel advice for the country mentions the Blue Badge.</p>
<div class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="Type a country, e.g. Spain" data-filtro-multi aria-label="Search countries"></div>
<div class="tab tab-b tab-srv"><table><caption class="sr">Where the UK Blue Badge is recognised in Europe, from GOV.UK, checked on {d}</caption><thead><tr><th>Country</th><th>UK Blue Badge recognised (GOV.UK)</th><th>More information (GOV.UK)</th><th>FCDO travel advice</th></tr></thead><tbody>{righe}</tbody></table></div>
<h2 id="official">What GOV.UK says</h2>
{blocco_cit_bb(BB["generali"]["indice"])}
<h2 id="eu-cards">The European Disability Card and European Parking Card</h2>
{blocco_cit_bb(["ec_when"])}
<p>The European Commission’s page does not mention the UK Blue Badge. <a href="{rel}{BB_CARTE}">Who can get the two cards and the dates, from the European Commission</a>.</p>
<p class="altri-pass">{ico("car")}<span>Driving abroad? <a href="{rel}{PAT_BASE}/">Do you need an international driving permit? UK, Canadian and Australian licences</a></span></p>
{faq_h}
<h2>How we check</h2>
<p>We read the GOV.UK guide “Using a Blue Badge in Europe” (Department for Transport) and copy its table row by row, the FCDO travel advice for each country, the Your Europe pages of the European Commission on the EU parking card, and, for Italy and France, the national government pages. GOV.UK links each country to pages that are not run by a government: we do not use them. Every sentence between quotation marks is copied word for word, with the date; Italian and French quotes come with our translation. A country gets its own page when people search for using a Blue Badge there. We check the sources again every month. More on the <a href="{rel}about/#{BB_BASE}">About page</a>. Spotted a change? <a href="{rel}contact/?ref={BB_BASE}">Tell us</a>.</p>
{NOTA_LIC_BB}"""
    desc = scegli([f"Where the UK Blue Badge is recognised in Europe, country by country, from GOV.UK, with local parking rules and the EU cards. Checked on {d}.",
                   f"UK Blue Badge abroad: GOV.UK’s answer for {len(BB_PAESI)} European countries, checked on {d}."], LIMITE_DESCRIZIONE)
    pagina(f"{BB_BASE}/", scegli([f"Blue Badge Abroad ({ANNO}): Where Your UK Badge Is Recognised in Europe", f"Blue Badge Abroad ({ANNO})"], LIMITE_TITOLO_BB), desc, corpo,
           briciole=[("Blue Badge abroad", f"{BB_BASE}/")], js=APP_JS_FILTRO, ld_extra=faq_ld)
    LASTMOD[f"{BB_BASE}/"] = BB["controllato_il"]


def prima_frase_carte_bb():
    F = fonte_bb("ec_carte")
    return (f"According to the European Commission, page updated on {data_lunga(F['aggiornato_il'])} and checked on {data_lunga(F['letto_il'])}, EU countries "
            f"have to adopt the national laws for the European Disability Card and the European Parking Card by 5 June 2027 and issue the cards from 5 June 2028.")


def pagina_carte_bb():
    rel = "../../"
    G = BB["generali"]
    F = fonte_bb("ec_carte")
    righe = [("October 2024", "Directive (EU) 2024/2841 adopted", "ec_dir"), ("July 2026", "QR codes for the physical cards (delegated regulation)", "ec_qr"),
             ("5 June 2027", "EU countries adopt and publish their national laws", "ec_when"), ("5 June 2028", "EU countries apply the rules and issue the cards", "ec_when"),
             ("5 June 2029", "Assessment of remaining gaps in free movement", "ec_gaps"), ("5 December 2029", "The European Parking Card replaces national parking cards", "ec_replace")]
    tab = "".join(f'<tr><td data-l="When">{escape(a)}</td><td data-l="What">{escape(b)}</td></tr>' for a, b, _ in righe)
    faq_h, faq_ld = html_faq_bb(faq_bb(BB["faq_carte"]))
    corpo = f"""<section class="hero">{h1_diviso(f"European Disability Card and European Parking Card: what changes and when ({ANNO})")}</section>
<section class="card summary" aria-label="Answer">
<div class="s-top"><span class="sq">{ico("calendar")}</span><span>EU cards · dates</span><span>{ANNO}</span></div>
<div class="s-body"><p class="lead" id="answer">{escape(prima_frase_carte_bb())}</p>
<p class="small" data-nota>The European Commission’s page does not mention the United Kingdom or the UK Blue Badge. For where the UK Blue Badge is recognised today, see <a href="{rel}{BB_BASE}/">the GOV.UK table</a>.</p></div></section>
{AVVISO_BB}
<h2>Key dates</h2>
<div class="tab tab-b"><table><caption class="cap">European Disability Card and European Parking Card: dates from the European Commission, {data_fonte_bb("ec_carte")}</caption><thead><tr><th>When</th><th>What</th></tr></thead><tbody>{tab}</tbody></table></div>
<h2 id="official">What the European Commission says</h2>
{blocco_cit_bb(["ec_when", "ec_gaps", "ec_replace"])}
<h3>What the cards are</h3>
{blocco_cit_bb(G["carte_cosa"])}
<h3>Who can get them</h3>
{blocco_cit_bb(G["carte_chi"])}
<h3>The European Parking Card</h3>
{blocco_cit_bb(G["carte_parcheggio"])}
{AD}
<h3>Where the EU Disability Card already exists</h3>
{blocco_cit_bb(G["carte_pilota"])}
<h3>What comes next</h3>
{blocco_cit_bb(G["carte_poi"])}
<p>EUR-Lex, where the directive is published, does not answer our automated checks, so we quote the European Commission’s own summary of the rules.</p>
<p><a href="{rel}{BB_BASE}/">Blue Badge abroad: where your UK Blue Badge is recognised, country by country</a> · <a href="{rel}{PAT_BASE}/">Driving abroad</a></p>
{faq_h}
<p class="small">Spotted a change? <a href="{rel}contact/?ref={BB_BASE}">Tell us</a>.</p>
{NOTA_LIC_BB}"""
    d = data_lunga(F["letto_il"])
    pagina(BB_CARTE, scegli([f"European Disability Card and Parking Card: Key Dates ({ANNO})", f"European Disability Card ({ANNO})"], LIMITE_TITOLO_BB),
           scegli([f"European Disability Card and European Parking Card: national laws by 5 June 2027, cards from 5 June 2028. European Commission, checked {d}.",
                   f"European Disability Card and European Parking Card: the dates, from the European Commission, checked on {d}."], LIMITE_DESCRIZIONE), corpo,
           briciole=[("Blue Badge abroad", f"{BB_BASE}/"), ("European Disability Card", BB_CARTE)], ld_extra=faq_ld)
    LASTMOD[BB_CARTE] = F["letto_il"]


def home_bb():
    if not BB:
        return ""
    voci = "".join(f'<a href="{url_bb(p)}">{escape(p["nome"])}<small>{escape(ESITI_BB[p["esito"]])}</small></a>'
                   for p in BB_PAGINE if p["iso2"] in ("FR", "ES", "IT", "PT", "DE", "GR", "IE", "NL", "BE", "MT", "CY", "CH"))
    return (f'<h2>Blue Badge abroad</h2><p>Where the UK Blue Badge is recognised in Europe, from GOV.UK, with the local parking rules and the '
            f'<a href="{BB_CARTE}">European Disability Card dates</a>: <a href="{BB_BASE}/">every country in one table</a>.</p><div class="griglia">{voci}</div>')


def about_bb(rel):
    if not BB:
        return ""
    return f"""<h2 id="{BB_BASE}">Blue Badge abroad</h2>
<p>Sources: the GOV.UK guide “Using a Blue Badge in Europe” (Department for Transport) and its change history, the GOV.UK page “Find out where Blue Badge holders can park”, the FCDO travel advice for each country in the GOV.UK table, a GOV.UK news story on the UK–Spain framework, read through the GOV.UK Content API; the Your Europe pages of the European Commission on the EU parking card (general page and one page per EU country) and the European Commission’s page on the European Disability Card and European Parking Card; for Italy, the pages of the Department for policies for persons with disabilities and the circular of 28 September 2026; for France, Service-Public.gouv.fr. {len(BB["fonti"])} pages in all, read on {data_lunga(BB["controllato_il"])}. GOV.UK text is licensed under the <a href="{OGL}" rel="noopener">Open Government Licence v3.0</a>.</p>
<p>Rules: the GOV.UK table is copied row by row and every sentence between quotation marks is copied word for word (Italian and French with our translation); the short labels such as “Recognised” or “Decided locally” are ours and always sit next to the GOV.UK words. GOV.UK links each country to pages that are not run by a government: we do not use them. Where the official answer is vague, the page says so. A country gets its own page when people search for using a Blue Badge there. This is information, not legal advice.</p>"""


# ---------------------------------------------------------------- e-Visa per l'India: costo per nazionalità, visto all'arrivo, e-Arrival card (31/10/2026)
# Idea n. 1 (voto 7) di studio-business/intelaiatura/wf-2026-10-31-india-nri.md. Costi SOLO dalle due tabelle ufficiali in PDF del governo indiano
# (indianvisaonline.gov.in, Bureau of Immigration), estratte in automatico da raccolta/india_evisa.py in dati/india_evisa.json (verifica.py, punto 27,
# le rilegge dal PDF salvato con un secondo metodo e confronta numero di Paesi e valori). Citazioni brevi (al massimo 40 parole) da
# dati/india_evisa_manuali.json. Pagine per nazionalità solo con ricerche vere (dati/india_evisa_domanda.json); una pagina in tedesco e una in
# francese (ricerche vere "indien visum kosten", "visa inde prix"). Avviso evidente in ogni pagina: pagare solo sul sito ufficiale. Nessun link
# a rivenditori di visti. Affiliazione: solo SafetyWing (assicurazione medica di viaggio, già attivo nella rete, dominio in monetizzazione.json),
# riquadro dopo le informazioni ufficiali, solo nelle pagine in inglese; AdSense sì (spazio {AD}). CSS della sezione in STILE_IN, solo nelle sue pagine.
IN_BASE = "india-e-visa-fee"
IN_VOA = "india-visa-on-arrival"
IN_ARR = "india-e-arrival-card"
IN_DE = f"{IN_BASE}/indien-e-visum-kosten"
IN_FR = f"{IN_BASE}/prix-e-visa-inde"
_f_in = DATI / "india_evisa.json"
IN = json.loads(_f_in.read_text(encoding="utf-8")) if _f_in.exists() else None
IN_PAESI = IN["paesi"] if IN else []
IN_PER = {p["iso2"]: p for p in IN_PAESI}
IN_PAGINE = IN["pagine"] if IN else []
IN_PAG_PER = {g["iso2"]: g for g in IN_PAGINE}
IN_CIT = {c["id"]: c for c in IN["citazioni"]} if IN else {}
LIMITE_TITOLO_IN = 70
IN_EVISA = "https://indianvisaonline.gov.in/evisa/"
IN_EARRIVAL = "https://indianvisaonline.gov.in/earrival/"
COL_TV = [("tv30_apr_giu", "e-Tourist 30 days (April–June)"), ("tv30_lug_mar", "e-Tourist 30 days (July–March)"), ("tv1", "e-Tourist 1 year"),
          ("tv5", "e-Tourist 5 years")]
COL_ALTRI = [("business", "e-Business"), ("medico", "e-Medical"), ("accompagnatore", "e-Medical Attendant")]
COL_IN = COL_TV + COL_ALTRI
SW_IN = ((AFFILIATI.get("_safetywing_india") or {}).get("url") or "").strip()
MESI_DE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
MESI_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
NOMI_DE = {"DE": "Deutschland", "AT": "Österreich", "CH": "Schweiz", "LI": "Liechtenstein"}
NOMI_FR = {"FR": "France", "BE": "Belgique", "CH": "Suisse", "LU": "Luxembourg", "MC": "Monaco", "MA": "Maroc",
           "Algeria": "Algérie", "Democratic Republic of the Congo": "République démocratique du Congo"}
# tipi di visto nelle pagine in tedesco e francese
COL_DE = {"tv30_apr_giu": "e-Tourist 30 Tage (April–Juni)", "tv30_lug_mar": "e-Tourist 30 Tage (Juli–März)", "tv1": "e-Tourist 1 Jahr",
          "tv5": "e-Tourist 5 Jahre", "business": "e-Business", "medico": "e-Medical", "accompagnatore": "e-Medical Attendant"}
COL_FR = {"tv30_apr_giu": "e-Tourist 30 jours (avril–juin)", "tv30_lug_mar": "e-Tourist 30 jours (juillet–mars)", "tv1": "e-Tourist 1 an",
          "tv5": "e-Tourist 5 ans", "business": "e-Business", "medico": "e-Medical", "accompagnatore": "e-Medical Attendant"}
# traduzioni nostre delle citazioni mostrate nelle pagine in tedesco e francese
TRAD_IN = {
    "de": {"ev_ufficiale": "Nein, https://indianvisaonline.gov.in/evisa/ ist die einzige offizielle Website, um die e-Visa-Dienste zu beantragen.",
           "pdf_3": "Eine Bankgebühr von 3 % wird zusätzlich auf die jeweilige e-Visa-Gebühr erhoben.",
           "ev_4giorni": "Die Gebühr muss mindestens 4 Tage vor dem voraussichtlichen Reisedatum bezahlt werden, sonst wird der Antrag nicht bearbeitet.",
           "ev_rimborso": "Die e-Visa-Gebühr wird nach der Zahlung nicht erstattet, da sie für die Bearbeitung des Antrags gilt und nicht von der Erteilung oder Ablehnung der elektronischen Reisegenehmigung (ETA) abhängt."},
    "fr": {"ev_ufficiale": "Non, https://indianvisaonline.gov.in/evisa/ est le seul site officiel pour demander les services e-Visa.",
           "pdf_3": "Des frais bancaires de 3 % s’ajoutent aux frais d’e-Visa applicables.",
           "ev_4giorni": "Les frais doivent être payés au moins 4 jours avant la date de voyage prévue, sinon la demande ne sera pas traitée.",
           "ev_rimborso": "Les frais d’e-Visa ne sont pas remboursables une fois payés, car ils couvrent le traitement de la demande et ne dépendent ni de l’octroi ni du refus de l’autorisation électronique de voyage (ETA)."},
}
STILE_IN = ("<style>.tab-in[data-vista] td[data-c],.tab-in[data-vista] th[data-c]{display:none}.tab-in[data-vista=tutti] td[data-c],"
            ".tab-in[data-vista=tutti] th[data-c]{display:table-cell}"
            + "".join(f".tab-in[data-vista={k}] td[data-c={k}],.tab-in[data-vista={k}] th[data-c={k}]{{display:table-cell}}" for k, _ in COL_IN)
            + "@media (max-width:640px){.tab.tab-b.tab-in tr{display:grid}"
            + "".join(f".tab-in[data-vista={k}] td[data-c={k}]{{display:block}}" for k, _ in COL_IN)
            + ".tab-in[data-vista=tutti] td[data-c]{display:block}}"
            ".filtri-in{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:10px;align-items:end;margin:6px 0 4px}"
            ".filtri-in label{display:block;font-size:.85rem;color:var(--ink-2);min-width:0}.filtri-in .cerca{margin:4px 0 0}"
            ".filtri-in select{font:inherit;font-size:1rem;color:var(--ink);background:var(--card);border:1.5px solid var(--line-2);border-radius:var(--r-s);"
            "padding:10px 12px;width:100%;min-width:0;min-height:46px;margin-top:4px}"
            "@media (max-width:640px){.filtri-in{grid-template-columns:1fr}}"
            "td.n{font-variant-numeric:tabular-nums}.elenco-in{columns:2 180px;column-gap:24px;padding-left:20px}"
            "@media (max-width:640px){.tab.tab-in1 td,.tab.tab-in1 th,.tab.tab-in1 td:first-child,.tab.tab-in1 th:first-child{min-width:0;padding:8px 10px}"
            ".tab.tab-b td[data-l]::before{letter-spacing:.03em}}"
            "</style>")
IN_JS = r"""(function(){var t=document.querySelector('[data-in-tab]');if(!t)return;var inp=document.querySelector('[data-in-cerca]'),sel=document.querySelector('[data-in-tipo]'),n=document.querySelector('[data-in-n]');
function norm(s){return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');}
function f(){var v=norm(inp.value.trim()),k=0;t.querySelectorAll('tr[data-voce]').forEach(function(r){var ok=!v||norm(r.cells[0].textContent+' '+(r.getAttribute('data-alias')||'')).indexOf(v)>=0;r.hidden=!ok;if(ok)k++;});t.setAttribute('data-vista',sel.value);if(n)n.textContent=String(k);}
inp.addEventListener('input',f);sel.addEventListener('change',f);f();})();"""


def url_in(g=None):
    return f"{IN_BASE}/" if g is None else f"{IN_BASE}/{IN_PER[g['iso2']]['slug']}/"


def usd(v):
    return "–" if v is None else f"${v}"


def con3(v):
    """Costo con la commissione bancaria del 3 % (nostro calcolo, arrotondato al centesimo)."""
    if v is None:
        return "–"
    c = round(v * 103) / 100
    return f"${int(c)}" if c == int(c) else f"${c:.2f}"


def val_in(p, k):
    """Valore della tabella per il Paese p e la colonna k: None = nessun valore (Paese non nella tabella e-Tourist, o '-' nella tabella)."""
    src = p["tv"] if k.startswith("tv") else p["altri"]
    return None if src is None else src.get(k)


def grezzo_in(p, k):
    """Come la tabella scrive il valore: '00', '10', '-' o assente (Paese non nella tabella)."""
    fid = "fee_tv" if k.startswith("tv") else "fee_altri"
    r = next((r for r in IN["tabelle"][fid]["righe"] if r["iso2"] == p["iso2"]), None)
    if not r:
        return None
    return r["grezzi"][[c for c, _ in IN["tabelle"][fid]["colonne"]].index(k)]


def cella_in(p, k):
    g = grezzo_in(p, k)
    if g is None:
        return '<span class="small">not in table</span>'
    if g == "-":
        return '<span class="small">“-” (no fee given)</span>'
    return escape(usd(int(g)))


def data_tab_in(fid):
    return IN["tabelle"][fid]["data"]


def data_in():
    return IN["controllato_il"]


def data_file_in():
    return max(IN["fonti"][f]["file_del"] for f in ("fee_tv", "fee_altri"))


def moda_in(k):
    """Valore più frequente di una colonna e quanti Paesi lo hanno (Paesi presenti nella tabella, '-' escluso)."""
    vv = [val_in(p, k) for p in IN_PAESI if grezzo_in(p, k) not in (None, "-")]
    conta = {}
    for v in vv:
        conta[v] = conta.get(v, 0) + 1
    v = max(conta, key=lambda x: (conta[x], -x))
    return v, conta[v], len(vv)


def link_pdf_in(fid):
    F = IN["fonti"][fid]
    return f'<a href="{escape(F["url"])}" rel="noopener">{escape(F["titolo"])}</a>'


def fonte_tabelle_in(cosa="Figures copied from the official tables", con_3=True):
    return (f'<p class="fonte">Source: {link_pdf_in("fee_tv")}, dated {data_lunga(data_tab_in("fee_tv"))}, and {link_pdf_in("fee_altri")}, dated '
            f'{data_lunga(data_tab_in("fee_altri"))} (Bureau of Immigration, Ministry of Home Affairs, Government of India). Both files were updated on '
            f'the official website on {data_lunga(data_file_in())}; checked on {data_lunga(data_in())}. {cosa}'
            + ('; the “with 3% bank charge” figures are our calculation.</p>' if con_3 else '.</p>'))


def blocco_cit_in(ids, lingua="en"):
    """Citazioni raggruppate per fonte: virgolette, fonte, ente e data (in tedesco e francese con la traduzione nostra)."""
    out, gruppi = [], []
    for i in ids:
        c = IN_CIT[i]
        if gruppi and gruppi[-1][0] == c["f"]:
            gruppi[-1][1].append(c)
        else:
            gruppi.append((c["f"], [c]))
    for fid, cc in gruppi:
        F = IN["fonti"][fid]
        etichetta = {"de": "Unsere Übersetzung:", "fr": "Notre traduction :"}.get(lingua)
        h = "".join(f'<p lang="en">{escape(c["x"])}</p>' + (f'<p class="trad"><em>{etichetta}</em> {escape(TRAD_IN[lingua][c["id"]])}</p>' if etichetta else "")
                    for c in cc)
        if lingua == "de":
            fonte = f'Quelle: <a href="{escape(F["url"])}" rel="noopener">{escape(F["titolo"])}</a> (Bureau of Immigration, Regierung von Indien), geprüft am {data_de(F["letto_il"])}. Wörtlich zitiert.'
        elif lingua == "fr":
            fonte = f'Source : <a href="{escape(F["url"])}" rel="noopener">{escape(F["titolo"])}</a> (Bureau of Immigration, gouvernement de l’Inde), vérifié le {data_fr(F["letto_il"])}. Cité mot pour mot.'
        else:
            fonte = (f'Source: <a href="{escape(F["url"])}" rel="noopener">{escape(F["titolo"])}</a> (Bureau of Immigration, Government of India), '
                     f'checked on {data_lunga(F["letto_il"])}. Quoted word for word.')
        out.append(f'<blockquote class="cit">{h}</blockquote><p class="fonte">{fonte}</p>')
    return "".join(out)


def testo_cit_in(ids):
    return " ".join(f"“{IN_CIT[i]['x']}”" for i in ids)


def data_de(iso):
    d = date.fromisoformat(iso)
    return f"{d.day}. {MESI_DE[d.month - 1]} {d.year}"


def data_fr(iso):
    d = date.fromisoformat(iso)
    return f"{'1er' if d.day == 1 else d.day} {MESI_FR[d.month - 1]} {d.year}"


def avviso_in(lingua="en", cosa="visto"):
    """Avviso evidente: pagare solo sul sito ufficiale (in ogni pagina della sezione, subito dopo la risposta)."""
    a = f'<a href="{IN_EVISA}" rel="noopener">indianvisaonline.gov.in</a>'
    if cosa == "arrivo":
        return (f'<p class="avviso avviso-idp" data-avviso-ufficiale><strong>Use only the official site, <a href="{IN_EARRIVAL}" rel="noopener">indianvisaonline.gov.in</a>, '
                'or the official app.</strong> Do not pay an unofficial site to fill it in for you: the Government of India says it does not authorise '
                'agents to charge fees for the e-Arrival card. We are not the government.</p>')
    if lingua == "de":
        return (f'<p class="avviso avviso-idp" data-avviso-ufficiale><strong>Zahlen Sie nur auf der offiziellen Website {a}.</strong> Inoffizielle Websites '
                'verlangen mehr als die staatliche Gebühr. Wir sind keine Behörde und verkaufen keine Visa.</p>')
    if lingua == "fr":
        return (f'<p class="avviso avviso-idp" data-avviso-ufficiale><strong>Payez uniquement sur le site officiel {a}.</strong> Les sites non officiels '
                'facturent plus que les frais du gouvernement. Nous ne sommes pas une administration et ne vendons pas de visas.</p>')
    return (f'<p class="avviso avviso-idp" data-avviso-ufficiale><strong>Pay only on the official site, {a}.</strong> Unofficial sites charge more '
            'than the government fee shown here. We are not the government and we do not sell visas.</p>')


def html_faq_in(faq, titolo="Questions"):
    h = "".join(f"<h3>{escape(q)}</h3><p>{escape(a)}</p>" for q, a in faq)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    return f'<section class="faq"><h2>{escape(titolo)}</h2>{h}</section>', [ld]


def faq_cit_in(ff):
    """FAQ con parole nostre (pre, post) e citazioni (cit): risposta in testo semplice."""
    out = []
    for f in ff:
        parti = ([f["pre"]] if f.get("pre") else []) + [testo_cit_in(f.get("cit", []))] + ([f["post"]] if f.get("post") else [])
        out.append((f["q"], " ".join(x for x in parti if x)))
    return out


def box_assicurazione_in():
    """Riquadro SafetyWing (assicurazione medica di viaggio, link di affiliazione): '' finché _safetywing_india è vuoto. Dopo le regole ufficiali."""
    if not SW_IN:
        return ""
    return (f'<h2 id="travel-insurance">Optional: travel medical insurance for India <span class="aff-tag">Affiliate</span></h2>'
            f'<section class="card noleggio" aria-label="Travel medical insurance, affiliate link" data-assicurazione>'
            '<p><strong>Travel insurance is not a requirement for the India e-Visa or the visa on arrival:</strong> none of the official pages we quote, '
            'including the e-Visa page’s lists of documents, asks for it, so it is your choice. The e-Visa fee pays only for processing your '
            'application and includes no insurance. If you want cover for medical costs during your trip anyway, SafetyWing sells travel medical insurance online; check what '
            'the policy covers before you buy.</p>'
            f'<p class="noleggio-btn"><a class="btn" href="{escape(SW_IN)}" rel="sponsored noopener" target="_blank">{ico("shield")}See SafetyWing travel medical insurance</a></p>'
            f'{MON.nota_trasparenza("en")}</section>')


# ---- frasi con le cifre (solo dalle tabelle)
def tv_frase(p):
    """'$10 for 30 days (April to June), $25 for 30 days (July to March), $40 for one year and $484 for five years'."""
    v = [val_in(p, k) for k, _ in COL_TV]
    return f"{usd(v[0])} for 30 days (April to June), {usd(v[1])} for 30 days (July to March), {usd(v[2])} for one year and {usd(v[3])} for five years"


def altri_frase(p):
    """'the e-Business Visa is $242, the e-Medical Visa $129 and the e-Medical Attendant Visa $129' ("-" = nessun valore nella tabella)."""
    parti = []
    for i, (k, n) in enumerate(COL_ALTRI):
        g = grezzo_in(p, k)
        if g == "-":
            parti.append(f"the {n} Visa has “-” (no fee given)")
        else:
            parti.append(f"the {n} Visa {'is ' if i == 0 or grezzo_in(p, COL_ALTRI[i - 1][0]) == '-' else ''}{usd(val_in(p, k))}")
    return ", ".join(parti[:-1]) + " and " + parti[-1]


def risposta_in(g):
    p = IN_PER[g["iso2"]]
    c = g["cittadini"]
    inizio = (f"According to the Government of India’s official e-Visa fee tables (Bureau of Immigration), dated {data_lunga(data_tab_in('fee_tv'))} "
              f"and {data_lunga(data_tab_in('fee_altri'))} and checked on {data_lunga(data_in())}, ")
    if p["tv"] is None:
        return inizio + f"{p['nome_pdf']} is not in the e-Tourist Visa fee table; in the table for the other e-Visas, for {c} {altri_frase(p)}."
    return inizio + f"the e-Tourist Visa for {c} costs {tv_frase(p)}, plus a 3% bank charge; {altri_frase(p)}."


def confronto_in(p, chi):
    """Differenze dal valore più frequente di ogni colonna (cifre solo dalle tabelle)."""
    diverse = []
    for k, n in COL_IN:
        g = grezzo_in(p, k)
        if g in (None, "-"):
            continue
        m, cnt, tot = moda_in(k)
        if val_in(p, k) != m:
            diverse.append(f"{n} {usd(val_in(p, k))} (most common: {usd(m)}, for {cnt} of {tot} nationalities)")
    if not diverse:
        return f"{chi[0].upper() + chi[1:]} pay the most common fee in every column of the two official tables."
    return f"Fees for {chi} that differ from the most common fee in the official tables: " + "; ".join(diverse) + "."


def righe_tipi_in(p):
    out = []
    for k, n in COL_IN:
        g = grezzo_in(p, k)
        if g is None:
            out.append(f'<tr data-c="{k}"><th scope="row">{escape(n)}</th><td>Not in the e-Tourist table</td><td>–</td></tr>')
        elif g == "-":
            out.append(f'<tr data-c="{k}"><th scope="row">{escape(n)}</th><td>“-” in the table (no fee given)</td><td>–</td></tr>')
        else:
            out.append(f'<tr data-c="{k}"><th scope="row">{escape(n)}</th><td class="n">{escape(usd(int(g)))}</td><td class="n">{escape(con3(int(g)))}</td></tr>')
    return "".join(out)


def titoli_in(g):
    p = IN_PER[g["iso2"]]
    c = g["cittadini"].replace(" citizens", " Citizens").replace(" nationals", " Nationals")
    if p["tv"] is None:
        return [f"India e-Visa Fee for {c} ({ANNO}): e-Medical {usd(val_in(p, 'medico'))}", f"India e-Visa Fee for {c} ({ANNO})"]
    return [f"India e-Visa Fee for {c} ({ANNO}): 5 Years {usd(val_in(p, 'tv5'))}", f"India e-Visa Fee for {c} ({ANNO})",
            f"India e-Visa Fee: {g['titolo']} ({ANNO})"]


def descrizione_in(g):
    p = IN_PER[g["iso2"]]
    d = data_lunga(data_in())
    if p["tv"] is None:
        return scegli([f"India e-Visa fees for {g['cittadini']} from the official tables: e-Medical {usd(val_in(p, 'medico'))}. Checked on {d}. Pay only on indianvisaonline.gov.in."],
                      LIMITE_DESCRIZIONE)
    return scegli([f"India e-Visa fee for {g['cittadini']}: 30 days {usd(val_in(p, 'tv30_lug_mar'))}, 1 year {usd(val_in(p, 'tv1'))}, 5 years {usd(val_in(p, 'tv5'))}, "
                   f"e-Business {usd(val_in(p, 'business'))}. Official tables, checked on {d}.",
                   f"India e-Visa fee for {g['cittadini']} from the official tables, checked on {d}."], LIMITE_DESCRIZIONE)


DOMANDE_CAT_IN = {"generale": "How much is the India e-Visa for {c}?", "5anni": "How much is the 5-year India e-Visa for {c}?",
                  "1anno": "How much is the one-year India e-Visa for {c}?", "30giorni": "How much is the 30-day India e-Visa for {c}?",
                  "business": "How much is the India e-Business Visa for {c}?", "medico": "How much is the India e-Medical Visa for {c}?"}


def risposta_cat_in(g, cat):
    p, c = IN_PER[g["iso2"]], g["cittadini"]
    tab = f"In the official table dated {data_lunga(data_tab_in('fee_tv'))}"
    tab2 = f"In the official table dated {data_lunga(data_tab_in('fee_altri'))}"
    if cat in ("generale", "5anni", "1anno", "30giorni") and p["tv"] is None:
        return (f"{p['nome_pdf']} is not in the official e-Tourist Visa fee table. {tab2}, for {c} {altri_frase(p)}. "
                "For a tourist visa, check the official website before you apply.")
    if cat == "generale":
        return f"{tab}, the e-Tourist Visa for {c} costs {tv_frase(p)}. {tab2}, {altri_frase(p)}. A 3% bank charge is added."
    if cat == "5anni":
        return f"{tab}, the 5-year e-Tourist Visa for {c} costs {usd(val_in(p, 'tv5'))}; with the 3% bank charge that is {con3(val_in(p, 'tv5'))}."
    if cat == "1anno":
        return f"{tab}, the one-year e-Tourist Visa for {c} costs {usd(val_in(p, 'tv1'))}; with the 3% bank charge that is {con3(val_in(p, 'tv1'))}."
    if cat == "30giorni":
        return (f"{tab}, the 30-day e-Tourist Visa for {c} costs {usd(val_in(p, 'tv30_apr_giu'))} in the “April to June” column and "
                f"{usd(val_in(p, 'tv30_lug_mar'))} in the “July to March” column, plus a 3% bank charge.")
    k = "business" if cat == "business" else "medico"
    if grezzo_in(p, k) == "-":
        return f"{tab2}, the e-Business Visa for {c} shows “-”: the table gives no fee."
    nome_k = "e-Business" if k == "business" else "e-Medical"
    if val_in(p, k) == 0:
        base = f"{tab2}, the {nome_k} Visa for {c} shows $0: no fee."
    else:
        base = f"{tab2}, the {nome_k} Visa for {c} costs {usd(val_in(p, k))}; with the 3% bank charge that is {con3(val_in(p, k))}."
    return base + (f" The e-Medical Attendant Visa: {usd(val_in(p, 'accompagnatore'))}." if k == "medico" else "")


def voa_paese_in(iso):
    """Visto all'arrivo per nazionalità, dalle citazioni: 'si' (Giappone, Corea del Sud), 'condizionato' (Emirati), 'no'."""
    return {"JP": "si", "KR": "si", "AE": "condizionato"}.get(iso, "no")


def risposta_voa_in(g):
    c = g["cittadini"]
    s = voa_paese_in(g["iso2"])
    if s == "si":
        return f"Yes. {testo_cit_in(['ev_voa'])} {c[0].upper() + c[1:]} can also apply for an e-Visa online."
    if s == "condizionato":
        return f"Only if they have had an Indian e-Visa or paper visa before. {testo_cit_in(['ev_voa', 'voa_uae'])}"
    return f"No. {testo_cit_in(['ev_voa'])} {testo_cit_in(['ev_voa_altri'])}"


def faq_in(g):
    c = g["cittadini"]
    ordine = ["generale", "5anni", "1anno", "30giorni", "business", "medico"]
    out = [(DOMANDE_CAT_IN[f["categoria"]].format(c=c), risposta_cat_in(g, f["categoria"])) for f in sorted(g["faq"], key=lambda f: ordine.index(f["categoria"]))]
    if g.get("voa"):
        out.append((f"Can {c} get a visa on arrival in India?", risposta_voa_in(g)))
    return out


def link_governo_in(rel, iso):
    """Pagine del sito per chi ha il passaporto britannico, canadese o australiano: regole d'ingresso dell'India del proprio governo."""
    voci = []
    if iso == "GB" and "india" in UK_CON_PAGINA:
        voci.append(f'<a href="{rel}passport-validity/india/">India entry requirements (FCDO) for British passports</a>')
    for k, iso_k in (("ca", "CA"), ("au", "AU")):
        if iso == iso_k:
            v = next((v for v in VOCI.get(k, []) if v["slug"] == "india"), None)
            if v:
                voci.append(f'<a href="{rel}{v["url_pag"]}">India entry requirements for {ESTERI[k]["agg"]} passports</a>')
    pat = {"GB": "uk", "CA": "ca", "AU": "au"}.get(iso)
    if pat and PAT and "IN" in PAGINE_PAT.get(pat, []):
        voci.append(f'<a href="{rel}{url_pat(pat, "IN")}">Driving in India with a {escape(PATENTI[pat]["lic"])}</a>')
    if not voci:
        return ""
    return f'<p class="altri-pass">{ico("passport")}<span>Your own government’s advice: {" · ".join(voci)}</span></p>'


def link_india(rel, iso, k=None):
    """Riga 'India e-Visa fee' nelle pagine passaporto (britannica, canadese, australiana) dell'India: '' per ogni altra pagina."""
    if not IN or iso != "IN":
        return ""
    g = IN_PAG_PER.get({"uk": "GB", "ca": "CA", "au": "AU"}.get(k))
    if not g:
        return ""
    p = IN_PER[g["iso2"]]
    return (f'<p class="altri-pass">{ico("globe")}<span>Visa fee: <a href="{rel}{url_in(g)}">India e-Visa fee for {escape(g["cittadini"])}</a> '
            f'({usd(val_in(p, "tv5"))} for five years in the official table) · <a href="{rel}{IN_ARR}/">e-Arrival card</a></span></p>')


def link_voa_arr_in(rel):
    return (f'<p class="altri-pass">{ico("scan")}<span>Also before you fly to India: <a href="{rel}{IN_ARR}/">the e-Arrival card</a> (within 72 hours '
            f'before arrival) · <a href="{rel}{IN_VOA}/">who can get a visa on arrival</a></span></p>')


def griglia_in(rel, salta=None):
    return "".join(f'<a href="{rel}{url_in(g)}">{escape(IN_PER[g["iso2"]]["nome"])}<small>5 years: {escape(usd(val_in(IN_PER[g["iso2"]], "tv5")))}</small></a>'
                   if IN_PER[g["iso2"]]["tv"] else
                   f'<a href="{rel}{url_in(g)}">{escape(IN_PER[g["iso2"]]["nome"])}<small>e-Medical: {escape(usd(val_in(IN_PER[g["iso2"]], "medico")))}</small></a>'
                   for g in sorted(IN_PAGINE, key=lambda g: IN_PER[g["iso2"]]["nome"]) if g["iso2"] != salta)


NOTA_STAGIONI_IN = ("The official e-Tourist table has two columns for the 30-day visa, headed “April to June” and “July to March”; it does not say "
                    "whether the month is the month you apply or the month you arrive. Where the table shows “00” we show $0.")


def sezione_validita_in():
    return f'<h2>Which e-Tourist Visa: 30 days, one year or five years</h2>{blocco_cit_in(["ev_val30", "ev_val1_5", "ev_180", "ev_valb", "ev_passaporto"])}'


def sezione_pagare_in():
    return (f'<h2 id="how-to-pay">How and when to pay</h2><p>Asked whether any website other than the government’s can take your application, '
            f'the official e-Visa page answers:</p>{blocco_cit_in(["ev_ufficiale", "ev_intermediari"])}<p>When to apply and pay:</p>'
            f'{blocco_cit_in(["ev_4giorni", "ev_quando", "ev_3"])}<p>If your e-Visa is refused:</p>{blocco_cit_in(["ev_rimborso"])}'
            f'<p>Asked whether you have to pay anything else at the airport, the official e-Visa page answers:</p>{blocco_cit_in(["ev_aeroporto"])}')


def pagina_in(g):
    rel = "../../"
    p = IN_PER[g["iso2"]]
    c = g["cittadini"]
    faq_h, faq_ld = html_faq_in(faq_in(g))
    voa = ""
    if voa_paese_in(g["iso2"]) != "no":
        voa = (f'<h2>Visa on arrival</h2>{blocco_cit_in(["ev_voa"] + (["voa_uae"] if g["iso2"] == "AE" else []))}'
               f'<p><a href="{rel}{IN_VOA}/">Visa on arrival in India: cost, airports and conditions</a></p>')
    corpo = f"""{STILE_IN}<section class="hero">{h1_diviso(f"India e-Visa fee for {c} ({ANNO}): tourist, business and medical")}</section>
<section class="card summary" aria-label="Answer">
<div class="s-top"><span class="sq">{ico("passport")}</span><span>India e-Visa · {escape(p["nome"])}</span><span>{ANNO}</span></div>
<div class="s-body">
<p class="lead" id="answer">{escape(risposta_in(g))}</p>
<p class="small">{escape(confronto_in(p, c))}</p>
</div></section>
{avviso_in()}
<h2>e-Visa fees for {escape(c)}</h2>
<div class="tab tab-g tab-in1"><table><caption class="cap">{escape(p["nome"])} (“{escape(p["nome_pdf"])}” in the official tables): fee in US dollars</caption><thead><tr><th>e-Visa</th><th>Official fee</th><th>With 3% bank charge</th></tr></thead><tbody>{righe_tipi_in(p)}</tbody></table></div>
{fonte_tabelle_in()}
{blocco_cit_in(["pdf_3"])}
<p class="small">{escape(NOTA_STAGIONI_IN)} The second table’s title also names the e-Conference Visa, but the table has no separate column for it.</p>
{AD}
{sezione_validita_in()}
{sezione_pagare_in()}
{voa}
<p class="altri-pass">{ico("takeoff")}<span>Entering India with an e-Visa: <a href="{rel}{IN_BASE}/#ports">airports and seaports on the official lists</a> (not land borders)</span></p>
{link_voa_arr_in(rel)}
{link_governo_in(rel, g["iso2"])}
{box_assicurazione_in()}
<h2>Other nationalities</h2>
<div class="griglia">{griglia_in(rel, g["iso2"])}</div>
<p><a href="{rel}{IN_BASE}/">India e-Visa fees for all {len(IN_PAESI)} countries in the official tables</a></p>
{faq_h}
<p class="small">This page is information, not legal advice. Immigration officers at the border decide. Spotted a change? <a href="{rel}contact/?ref={IN_BASE}">Tell us</a>.</p>"""
    pagina(url_in(g), scegli(titoli_in(g), LIMITE_TITOLO_IN), descrizione_in(g), corpo,
           briciole=[("India e-Visa fee", f"{IN_BASE}/"), (p["nome"], url_in(g))], ld_extra=faq_ld)
    LASTMOD[url_in(g)] = data_in()


# ---- indice
def riga_in(p, rel):
    g = IN_PAG_PER.get(p["iso2"])
    nome = f'<a href="{rel}{url_in(g)}">{escape(p["nome_pdf"])}</a>' if g else escape(p["nome_pdf"])
    alias = " ".join([p["nome"], *p["alias"]])
    return (f'<tr data-voce id="{p["iso2"].lower()}" data-alias="{escape(alias)}"><td data-l="Country">{nome}</td>'
            + "".join(f'<td class="n" data-c="{k}" data-l="{escape(n)}">{cella_in(p, k)}</td>' for k, n in COL_IN) + "</tr>")


def prima_frase_in():
    return (f"According to the Government of India’s two official e-Visa fee tables (Bureau of Immigration), dated {data_lunga(data_tab_in('fee_tv'))} "
            f"and {data_lunga(data_tab_in('fee_altri'))} and checked on {data_lunga(data_in())}, the fee depends on your nationality: the table below "
            f"gives the e-Tourist, e-Business, e-Medical and e-Medical Attendant fees in US dollars for all {len(IN_PAESI)} countries and territories "
            "in the tables, and a 3% bank charge is added.")


def titoli_indice_in():
    return [f"India e-Visa Fee by Nationality ({ANNO}): Official Table, {len(IN_PAESI)} Countries", f"India e-Visa Fee by Nationality ({ANNO})"]


def nazioni_moda_in(k, valore):
    return [p for p in IN_PAESI if grezzo_in(p, k) not in (None, "-") and val_in(p, k) == valore]


UE_IN = ["AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK",
         "SI", "ES", "SE"]


def eccezioni_in(k, pp=None, n=None):
    """'UAE $415, Ecuador $240, ...': i Paesi con un valore diverso dal più frequente, dal più alto (al massimo n)."""
    m = moda_in(k)[0]
    pp = [p for p in (pp or IN_PAESI) if grezzo_in(p, k) not in (None, "-") and val_in(p, k) != m]
    pp.sort(key=lambda p: (-val_in(p, k), p["nome"]))
    return [f"{p['nome']} {usd(val_in(p, k))}" for p in pp[:n]] if n else [f"{p['nome']} {usd(val_in(p, k))}" for p in pp]


def faq_indice_in():
    m = {k: moda_in(k) for k, _ in COL_IN}
    tipici = [p for p in IN_PAESI if p["tv"] and all(val_in(p, k) == m[k][0] for k, _ in COL_TV)]
    risposte = {
        "prezzo": (f"It depends on your nationality and on the type of e-Visa. In the e-Tourist table dated {data_lunga(data_tab_in('fee_tv'))}, "
                   f"{len(tipici)} of the {len([p for p in IN_PAESI if p['tv']])} nationalities pay {usd(m['tv30_apr_giu'][0])} for 30 days (April to June), "
                   f"{usd(m['tv30_lug_mar'][0])} for 30 days (July to March), {usd(m['tv1'][0])} for one year and {usd(m['tv5'][0])} for five years; the "
                   "others pay different amounts, and some pay nothing. Find your nationality in the table above. A 3% bank charge is added."),
        "5anni": (f"{usd(m['tv5'][0])} for {m['tv5'][1]} of the {m['tv5'][2]} nationalities in the official e-Tourist table. The exceptions: "
                  + ", ".join(x for x in eccezioni_in("tv5") if not x.endswith(" $0"))
                  + f"; {len([p for p in IN_PAESI if p['tv'] and val_in(p, 'tv5') == 0])} nationalities pay $0 (see the table). A 3% bank charge is added."),
        "business": (f"{usd(m['business'][0])} for {m['business'][1]} of the {m['business'][2]} nationalities with a fee in the official table. The highest: "
                     + ", ".join(eccezioni_in("business", n=8)) + "; some nationalities pay $0 (see the table). A 3% bank charge is added."),
        "medico": (f"{usd(m['medico'][0])} for {m['medico'][1]} of the {m['medico'][2]} nationalities in the official table. The exceptions with a fee: "
                   + ", ".join(x for x in eccezioni_in("medico") if not x.endswith(" $0")) + "; some nationalities pay $0 (see the table). "
                   + ("For every nationality the table gives the e-Medical Attendant Visa the same fee as the e-Medical Visa. " if uguali_medico_accompagnatore() else "")
                   + "A 3% bank charge is added."),
        "ue": ue_frase_in(),
    }
    out = []
    for f in IN["faq"]["indice"]:
        if f["id"] in risposte:
            out.append((f["q"], risposte[f["id"]]))
        else:
            out += faq_cit_in([f])
    return out


def ue_frase_in():
    ue = [IN_PER[c] for c in UE_IN if c in IN_PER]
    m = {k: moda_in(k)[0] for k, _ in COL_IN}
    tv_ok = all(p["tv"] and all(val_in(p, k) == m[k] for k, _ in COL_TV) for p in ue)
    parti = []
    if tv_ok:
        parti.append(f"All {len(ue)} EU countries are in the official e-Tourist table with the same fees: {usd(m['tv30_apr_giu'])} for 30 days (April to June), "
                     f"{usd(m['tv30_lug_mar'])} for 30 days (July to March), {usd(m['tv1'])} for one year and {usd(m['tv5'])} for five years.")
    diverse = eccezioni_in("business", ue)
    parti.append(f"The e-Business Visa is {usd(m['business'])} for most EU citizens" + (", except " + ", ".join(diverse) if diverse else "") + ".")
    parti.append("A 3% bank charge is added.")
    return " ".join(parti)


def uguali_medico_accompagnatore():
    return all(val_in(p, "medico") == val_in(p, "accompagnatore") for p in IN_PAESI)


def fuori_in():
    voci = IN.get("fuori_tabella", [])
    if not voci:
        return ""
    nn = [v["nome"] for v in voci]
    nomi = ", ".join(nn[:-1]) + " and " + nn[-1] if len(nn) > 1 else nn[0]
    return (f'<h2 id="not-in-the-tables">Not in the tables</h2><p>People also search for the India e-Visa fee for nationals of {escape(nomi)}. '
            'None of these is in either official fee table. The e-Visa page says:</p>' + blocco_cit_in(["ev_idonei", "ev_pakistan", "ev_afghan"]))


def sezione_porti_in(rel):
    P = IN["porti"]
    aer = "".join(f"<li>{escape(x)}</li>" for x in P["aeroporti_faq"])
    porti = "".join(f"<li>{escape(x)}</li>" for x in P["porti_faq"])
    return f"""<h2 id="ports">Where you can enter India with an e-Visa</h2>
<p>The official e-Visa page gives two different lists, and we show both. Its answers to frequently asked questions say:</p>
{blocco_cit_in(["ev_porti_aerei", "ev_porti_partenza"])}
<p>The {len(P["aeroporti_faq"])} airports named there:</p><ul class="elenco-in">{aer}</ul>
<p>The {len(P["porti_faq"])} seaports named in the same answer:</p><ul class="elenco-in">{porti}</ul>
<p>The box “Authorized Immigration Checkposts” on the same page says something different:</p>
{blocco_cit_in(["ev_porti_37", "ev_porti_38"])}
<p>Its list of {len(P["aeroporti_faq"]) + len(P["aeroporti_solo_lista"])} airports adds {escape(", ".join(P["aeroporti_solo_lista"][:-1]))} and {escape(P["aeroporti_solo_lista"][-1])}. For cruise passengers, another answer on the same page names only five seaports, and land borders are not allowed:</p>
{blocco_cit_in(["ev_crociera", "ev_terra"])}
<p class="small">The official texts disagree on the number of airports and seaports. If you are arriving at an airport or port that is only on one of the lists, check with your airline, cruise line or the Bureau of Immigration before you travel.</p>"""


def piu_cercati_in(rel):
    """Scorciatoia sopra la tabella (lunga sul telefono): le nazionalità con più ricerche vere."""
    gg = sorted(IN_PAGINE, key=lambda g: -len(g["ricerche"]))[:6]
    return (f'<p class="altri-pass">{ico("passport")}<span>Most searched: '
            + " · ".join(f'<a href="{rel}{url_in(g)}">{escape(IN_PER[g["iso2"]]["nome"])}</a>' for g in gg) + "</span></p>")


def pagina_indice_in():
    rel = "../"
    d = data_lunga(data_in())
    righe = "".join(riga_in(p, rel) for p in sorted(IN_PAESI, key=lambda p: p["nome_pdf"].lower()))
    opzioni = '<option value="tutti">All types</option>' + "".join(f'<option value="{k}">{escape(n)}</option>' for k, n in COL_IN)
    faq_h, faq_ld = html_faq_in(faq_indice_in())
    n_tv = len([p for p in IN_PAESI if p["tv"]])
    corpo = f"""{STILE_IN}<section class="hero">{h1_diviso(f"India e-Visa fee by nationality ({ANNO}): the official table for every country")}
<p class="lead" id="answer">{escape(prima_frase_in())}</p></section>
{avviso_in()}
{piu_cercati_in(rel)}
<div class="filtri-in"><label>Your nationality<span class="cerca-box">{ico("search")}<input class="cerca" type="search" placeholder="e.g. UK, United States, Germany" data-in-cerca aria-label="Search your nationality"></span></label>
<label>Type of e-Visa<select data-in-tipo aria-label="Type of e-Visa">{opzioni}</select></label></div>
<p class="small" aria-live="polite">Showing <span data-in-n>{len(IN_PAESI)}</span> of {len(IN_PAESI)} countries and territories. Fees in US dollars, without the 3% bank charge.</p>
<div class="tab tab-b tab-srv tab-in" data-in-tab data-vista="tutti"><table><caption class="cap">India e-Visa fee by nationality in US dollars, from the official tables (checked on {d})</caption><thead><tr><th>Country (as in the tables)</th>{"".join(f'<th data-c="{k}">{escape(n)}</th>' for k, n in COL_IN)}</tr></thead><tbody>{righe}</tbody></table></div>
<ul>
<li>e-Tourist table: {n_tv} countries and territories, dated {data_lunga(data_tab_in("fee_tv"))}. Table for the e-Business, e-Medical and e-Medical Attendant Visas: {len(IN_PAESI)}, dated {data_lunga(data_tab_in("fee_altri"))}. Both files were updated on the official website on {data_lunga(data_file_in())}.</li>
<li>{escape(NOTA_STAGIONI_IN)} “-” means the table gives no fee; “not in table” means the country is not in the e-Tourist table.</li>
<li>The second table’s title also names the e-Conference Visa, but the table has no separate column for it. Other e-Visas (e-Student, e-Transit and others) are not in these two tables.</li>
</ul>
{fonte_tabelle_in("Every figure is copied from the two PDF tables by our script, which also checks that it has read every row", con_3=False)}
{blocco_cit_in(["pdf_3", "ev_paese"])}
{AD}
<h2>Fee pages by nationality</h2>
<div class="griglia">{griglia_in(rel)}</div>
<p class="altri-pass">{ico("globe")}<span lang="de"><a href="{rel}{IN_DE}/" hreflang="de">Indien e-Visum Kosten (auf Deutsch)</a></span> · <span lang="fr"><a href="{rel}{IN_FR}/" hreflang="fr">Prix du e-Visa pour l’Inde (en français)</a></span></p>
{fuori_in()}
{sezione_validita_in()}
{sezione_pagare_in()}
{sezione_porti_in(rel)}
<h2>Visa on arrival and the e-Arrival card</h2>
{blocco_cit_in(["ev_voa"])}
<p><a href="{rel}{IN_VOA}/">Visa on arrival in India: who is eligible, cost and airports</a> · <a href="{rel}{IN_ARR}/">India e-Arrival card: who must fill it in, and when</a></p>
{box_assicurazione_in()}
{faq_h}
<h2>How we check</h2>
<p>Our script downloads the two official PDF tables from indianvisaonline.gov.in, reads every row (serial number, country, fees) and stops if a row is missing, if the column headings or the note on the 3% bank charge change, or if a country name is not recognised; a second, independent reading of the same PDF must give the same countries and the same figures. We quote the official e-Visa pages word for word, in short extracts, with the date we checked them, and we link no visa agencies. More on the <a href="{rel}about/#{IN_BASE}">About page</a>. This page is information, not legal advice. Spotted a change? <a href="{rel}contact/?ref={IN_BASE}">Tell us</a>.</p>"""
    desc = scegli([f"India e-Visa fee for every nationality ({len(IN_PAESI)} countries): e-Tourist 30 days, 1 and 5 years, e-Business, e-Medical. Official tables, checked on {d}.",
                   f"India e-Visa fee by nationality from the official tables of the Government of India, checked on {d}."], LIMITE_DESCRIZIONE)
    pagina(f"{IN_BASE}/", scegli(titoli_indice_in(), LIMITE_TITOLO_IN), desc, corpo, briciole=[("India e-Visa fee", f"{IN_BASE}/")], js=IN_JS, ld_extra=faq_ld)
    LASTMOD[f"{IN_BASE}/"] = data_in()


# ---- visto all'arrivo
def prima_frase_voa_in():
    return (f"According to India’s official visa website and the Bureau of Immigration, checked on {data_lunga(data_in())}, a visa on arrival is only "
            "for nationals of Japan, South Korea and the UAE, and UAE nationals only if they have had an Indian e-Visa or paper visa before; "
            "everyone else who can get an e-Visa must apply online and wait for it to be granted before travelling.")


def pagina_voa_in():
    rel = "../"
    faq_h, faq_ld = html_faq_in(faq_cit_in(IN["faq"]["voa"]))
    jp, ae = IN_PAG_PER.get("JP"), IN_PAG_PER.get("AE")
    fee = " · ".join(f'<a href="{rel}{url_in(g)}">e-Visa fee for {escape(g["cittadini"])}</a>' for g in (jp, ae) if g)
    corpo = f"""<section class="hero">{h1_diviso(f"Visa on arrival in India ({ANNO}): who is eligible, cost and airports")}</section>
<section class="card summary" aria-label="Answer">
<div class="s-top"><span class="sq">{ico("passport")}</span><span>India · visa on arrival</span><span>{ANNO}</span></div>
<div class="s-body"><p class="lead" id="answer">{escape(prima_frase_voa_in())}</p></div></section>
{avviso_in()}
<h2>Who is eligible</h2>
{blocco_cit_in(["ev_voa", "ev_voa_altri"])}
<p>The official visa-on-arrival page lists further eligibility conditions (including six months of passport validity and a return or onward ticket). The first one sets the length and purpose of the visit, and the page also has advice for UAE nationals visiting India for the first time:</p>
{blocco_cit_in(["voa_scopo", "voa_uae"])}
<h2>Who cannot get it</h2>
{blocco_cit_in(["voa_pakistan", "voa_diplomatici"])}
<h2>Cost and form</h2>
{blocco_cit_in(["voa_costo", "voa_pagare", "voa_modulo"])}
{AD}
<h2>Airports</h2>
<p>The two official pages give different lists for UAE nationals. India’s visa website says:</p>
{blocco_cit_in(["voa_dove"])}
<p>The Bureau of Immigration says:</p>
{blocco_cit_in(["boi_voa_dove"])}
<p class="small">If you are a UAE national arriving at Cochin, Calicut or Ahmedabad, check with the Bureau of Immigration or your airline before you travel: only one of the two official pages lists these airports.</p>
<h2>How long it lasts</h2>
{blocco_cit_in(["voa_durata", "voa_non_estendibile"])}
<h2>No visa needed: Nepal, Bhutan and the Maldives</h2>
{blocco_cit_in(["boi_senza_visto", "boi_maldive"])}
<h2>Everyone else: the e-Visa</h2>
<p>If your country is not one of the three, you need an e-Visa (or a regular visa from an Indian embassy or consulate) before you travel. <a href="{rel}{IN_BASE}/">India e-Visa fee by nationality</a>{(" · " + fee) if fee else ""}.</p>
<p class="altri-pass">{ico("scan")}<span>Every foreign visitor, with or without a visa on arrival: <a href="{rel}{IN_ARR}/">fill in the e-Arrival card within 72 hours before arrival</a></span></p>
{box_assicurazione_in()}
{faq_h}
<p class="small">This page is information, not legal advice. Immigration officers at the border decide. Spotted a change? <a href="{rel}contact/?ref={IN_VOA}">Tell us</a>.</p>"""
    desc = scegli([f"Visa on arrival in India: only Japan, South Korea and the UAE (with a previous Indian visa). Cost, airports, 60 days. Official, checked on {data_lunga(data_in())}."],
                  LIMITE_DESCRIZIONE)
    pagina(f"{IN_VOA}/", scegli([f"Visa on Arrival in India ({ANNO}): Who Is Eligible, Cost and Airports", f"Visa on Arrival in India ({ANNO})"], LIMITE_TITOLO_IN),
           desc, corpo, briciole=[("Visa on arrival in India", f"{IN_VOA}/")], ld_extra=faq_ld)
    LASTMOD[f"{IN_VOA}/"] = data_in()


# ---- e-Arrival card
def prima_frase_arr_in():
    return (f"According to the Bureau of Immigration and India’s official visa website, checked on {data_lunga(data_in())}, foreigners and OCI "
            "cardholders must complete the e-Arrival card online within 72 hours before they arrive in India, at indianvisaonline.gov.in/earrival "
            "or in the official “Indian Visa Su-Swagatam” app; it is arrival information, not a visa.")


def pagina_arr_in():
    rel = "../"
    faq_h, faq_ld = html_faq_in(faq_cit_in(IN["faq"]["arrivo"]))
    corpo = f"""<section class="hero">{h1_diviso(f"India e-Arrival card ({ANNO}): who must fill it in, when and where")}</section>
<section class="card summary" aria-label="Answer">
<div class="s-top"><span class="sq">{ico("scan")}</span><span>India · e-Arrival card</span><span>{ANNO}</span></div>
<div class="s-body"><p class="lead" id="answer">{escape(prima_frase_arr_in())}</p>
<p class="noleggio-btn"><a class="btn" href="{IN_EARRIVAL}" rel="noopener">{ico("arrow")}Official e-Arrival card form</a></p></div></section>
{avviso_in(cosa="arrivo")}
<h2>Who and when</h2>
{blocco_cit_in(["home_arrivo_obbligo", "home_arrivo"])}
{blocco_cit_in(["gg_arrivo"])}
<p class="small">One sentence on India’s visa website says “can complete”, the other and the Bureau of Immigration say “must complete”. The official pages we read speak of foreigners and OCI cardholders and do not mention Indian passport holders.</p>
<h2>It is not a visa</h2>
{blocco_cit_in(["home_arrivo_cosa"])}
{blocco_cit_in(["gg_ingresso"])}
<p>You still need an e-Visa, another Indian visa or an OCI card, unless you are a citizen of Nepal, Bhutan or the Maldives (visa-free entry, according to the Bureau of Immigration). <a href="{rel}{IN_BASE}/">India e-Visa fee by nationality</a> · <a href="{rel}{IN_VOA}/">visa on arrival</a></p>
{AD}
<h2>Is there a fee?</h2>
<p>None of the official pages we read mentions a fee for the e-Arrival card, and the Government of India says it does not authorise agents to charge for it:</p>
{blocco_cit_in(["home_agenti"])}
<h2>The Air Suvidha self-declaration form</h2>
{blocco_cit_in(["home_suvidha"])}
{faq_h}
<p class="small">This page is information, not legal advice. Immigration officers at the border decide. Spotted a change? <a href="{rel}contact/?ref={IN_ARR}">Tell us</a>.</p>"""
    desc = scegli([f"India e-Arrival card: foreigners and OCI cardholders fill it in online within 72 hours before arrival. Official site and app, checked on {data_lunga(data_in())}."],
                  LIMITE_DESCRIZIONE)
    pagina(f"{IN_ARR}/", scegli([f"India e-Arrival Card ({ANNO}): Who Must Fill It In, When and Where", f"India e-Arrival Card ({ANNO})"], LIMITE_TITOLO_IN),
           desc, corpo, briciole=[("India e-Arrival card", f"{IN_ARR}/")], ld_extra=faq_ld)
    LASTMOD[f"{IN_ARR}/"] = data_in()


# ---- pagine in tedesco e francese (ricerche vere "indien visum kosten", "visa inde prix")
def usd_l(v, lingua):
    if v is None:
        return "–"
    return f"{v} US-Dollar" if lingua == "de" else f"{v} dollars US"


def con3_l(v, lingua):
    c = con3(v)[1:]
    return (c.replace(".", ",") + " US-Dollar") if lingua == "de" else (c.replace(".", ",") + " dollars US")


def tabella_lingua_in(paesi, lingua):
    nomi = NOMI_DE if lingua == "de" else NOMI_FR
    col = COL_DE if lingua == "de" else COL_FR
    testa = "Land" if lingua == "de" else "Pays"
    righe = "".join(f'<tr data-voce id="{p["iso2"].lower()}"><td data-l="{testa}">{escape(nomi[p["iso2"]])}</td>'
                    + "".join(f'<td class="n" data-l="{escape(col[k])}">{escape(usd(val_in(p, k)))}</td>' for k, _ in COL_IN) + "</tr>" for p in paesi)
    cap = ("Kosten des e-Visums für Indien in US-Dollar, aus den offiziellen Tabellen" if lingua == "de"
           else "Prix du e-Visa pour l’Inde en dollars US, d’après les tableaux officiels")
    return (f'<div class="tab tab-b tab-srv"><table><caption class="cap">{cap}</caption><thead><tr><th>{testa}</th>'
            + "".join(f"<th>{escape(col[k])}</th>" for k, _ in COL_IN) + f"</tr></thead><tbody>{righe}</tbody></table></div>")


def uguali_in(paesi, k):
    vv = {val_in(p, k) for p in paesi}
    return vv.pop() if len(vv) == 1 else None


def fonte_lingua_in(lingua):
    a, b = link_pdf_in("fee_tv"), link_pdf_in("fee_altri")
    if lingua == "de":
        return (f'<p class="fonte">Quelle: {a} vom {data_de(data_tab_in("fee_tv"))} und {b} vom {data_de(data_tab_in("fee_altri"))} (Bureau of Immigration, '
                f'Innenministerium, Regierung von Indien), auf der offiziellen Website aktualisiert am {data_de(data_file_in())}, geprüft am {data_de(data_in())}. '
                'Zahlen aus den offiziellen Tabellen übernommen; die Beträge mit 3 % Bankgebühr sind unsere Rechnung.</p>')
    return (f'<p class="fonte">Source : {a} du {data_fr(data_tab_in("fee_tv"))} et {b} du {data_fr(data_tab_in("fee_altri"))} (Bureau of Immigration, '
            f'ministère de l’Intérieur, gouvernement de l’Inde), mis à jour sur le site officiel le {data_fr(data_file_in())}, vérifié le {data_fr(data_in())}. '
            'Chiffres repris des tableaux officiels ; les montants avec les 3 % de frais bancaires sont notre calcul.</p>')


def faq_lingua_in(lingua, paesi):
    u = {k: uguali_in(paesi, k) for k, _ in COL_IN}
    L = lingua
    risposte = {}
    if L == "de":
        alle = "für Deutschland, Österreich, die Schweiz und Liechtenstein"
        risposte = {
            "kosten": (f"Laut der offiziellen Tabelle vom {data_de(data_tab_in('fee_tv'))} kostet das e-Tourist-Visum {alle} {usd_l(u['tv30_apr_giu'], L)} für 30 Tage "
                       f"(April bis Juni), {usd_l(u['tv30_lug_mar'], L)} für 30 Tage (Juli bis März), {usd_l(u['tv1'], L)} für ein Jahr und {usd_l(u['tv5'], L)} "
                       "für fünf Jahre, zuzüglich 3 % Bankgebühr."),
            "30tage": (f"{usd_l(u['tv30_apr_giu'], L)} in der Spalte „April to June“ und {usd_l(u['tv30_lug_mar'], L)} in der Spalte „July to March“ der offiziellen "
                       "Tabelle, zuzüglich 3 % Bankgebühr. Die Tabelle sagt nicht, ob der Monat der Antragstellung oder der Einreise gemeint ist."),
            "1jahr": f"{usd_l(u['tv1'], L)}, mit 3 % Bankgebühr {con3_l(u['tv1'], L)} (unsere Rechnung).",
            "business": (f"Laut der offiziellen Tabelle vom {data_de(data_tab_in('fee_altri'))} kostet das e-Business-Visum "
                         + (f"{alle} {usd_l(u['business'], L)}" if u["business"] is not None else
                            ", ".join(f"für {NOMI_DE[p['iso2']]} {usd_l(val_in(p, 'business'), L)}" for p in paesi)) + ", zuzüglich 3 % Bankgebühr."),
            "schweiz": (f"Für Schweizer Staatsangehörige{' gelten dieselben Beträge wie für Deutsche' if all(val_in(IN_PER['CH'], k) == val_in(IN_PER['DE'], k) for k, _ in COL_IN) else ''}: "
                        f"{usd_l(val_in(IN_PER['CH'], 'tv1'), L)} für das e-Tourist-Visum für ein Jahr, {usd_l(val_in(IN_PER['CH'], 'tv5'), L)} für fünf Jahre, "
                        f"{usd_l(val_in(IN_PER['CH'], 'business'), L)} für das e-Business-Visum, zuzüglich 3 % Bankgebühr."),
            "oesterreich": (f"Für österreichische Staatsangehörige: {usd_l(val_in(IN_PER['AT'], 'tv30_lug_mar'), L)} für 30 Tage (Juli bis März), "
                            f"{usd_l(val_in(IN_PER['AT'], 'tv1'), L)} für ein Jahr, {usd_l(val_in(IN_PER['AT'], 'tv5'), L)} für fünf Jahre, zuzüglich 3 % Bankgebühr."),
            "euro": ("Die offizielle Tabelle nennt nur US-Dollar. Wie viel Sie in Euro oder Franken zahlen, hängt vom Wechselkurs Ihrer Karte oder Bank ab; "
                     "dazu kommt die Bankgebühr von 3 %."),
            "offiziell": ("Die offizielle Website ist indianvisaonline.gov.in/evisa/. Die indische Regierung schreibt: „" + IN_CIT["ev_ufficiale"]["x"] + "“ "
                          "(Unsere Übersetzung: " + TRAD_IN["de"]["ev_ufficiale"] + ") Inoffizielle Websites verlangen mehr als die staatliche Gebühr."),
        }
    else:
        ref = IN_PER["FR"]
        risposte = {
            "prix": (f"Selon le tableau officiel du {data_fr(data_tab_in('fee_tv'))}, le e-Visa touristique coûte, pour les Français, {usd_l(val_in(ref, 'tv30_apr_giu'), L)} "
                     f"pour 30 jours (avril à juin), {usd_l(val_in(ref, 'tv30_lug_mar'), L)} pour 30 jours (juillet à mars), {usd_l(val_in(ref, 'tv1'), L)} pour un an "
                     f"et {usd_l(val_in(ref, 'tv5'), L)} pour cinq ans, plus 3 % de frais bancaires."),
            "30jours": (f"{usd_l(val_in(ref, 'tv30_apr_giu'), L)} dans la colonne « April to June » et {usd_l(val_in(ref, 'tv30_lug_mar'), L)} dans la colonne "
                        "« July to March » du tableau officiel, plus 3 % de frais bancaires. Le tableau ne dit pas s’il s’agit du mois de la demande ou de l’arrivée."),
            "1an": f"{usd_l(val_in(ref, 'tv1'), L)} pour les Français, soit {con3_l(val_in(ref, 'tv1'), L)} avec les 3 % de frais bancaires (notre calcul).",
            "5ans": f"{usd_l(val_in(ref, 'tv5'), L)} pour les Français, soit {con3_l(val_in(ref, 'tv5'), L)} avec les 3 % de frais bancaires (notre calcul).",
            "business": ("Selon le tableau officiel du " + data_fr(data_tab_in("fee_altri")) + " : "
                         + ", ".join(f"{NOMI_FR[p['iso2']]} {usd_l(val_in(p, 'business'), L)}" for p in paesi) + ", plus 3 % de frais bancaires."),
            "belgique": (f"Pour les Belges : {usd_l(val_in(IN_PER['BE'], 'tv30_lug_mar'), L)} pour 30 jours (juillet à mars), {usd_l(val_in(IN_PER['BE'], 'tv1'), L)} "
                         f"pour un an, {usd_l(val_in(IN_PER['BE'], 'tv5'), L)} pour cinq ans (e-Visa touristique), plus 3 % de frais bancaires."),
            "suisse": (f"Pour les Suisses : {usd_l(val_in(IN_PER['CH'], 'tv30_lug_mar'), L)} pour 30 jours (juillet à mars), {usd_l(val_in(IN_PER['CH'], 'tv1'), L)} "
                       f"pour un an, {usd_l(val_in(IN_PER['CH'], 'tv5'), L)} pour cinq ans (e-Visa touristique), plus 3 % de frais bancaires."),
            "maroc": (f"Pour les Marocains : {usd_l(val_in(IN_PER['MA'], 'tv30_lug_mar'), L)} pour 30 jours (juillet à mars), {usd_l(val_in(IN_PER['MA'], 'tv1'), L)} "
                      f"pour un an, {usd_l(val_in(IN_PER['MA'], 'tv5'), L)} pour cinq ans (e-Visa touristique), plus 3 % de frais bancaires."),
            "officiel": ("Le site officiel est indianvisaonline.gov.in/evisa/. Le gouvernement indien écrit : « " + IN_CIT["ev_ufficiale"]["x"] + " » "
                         "(Notre traduction : " + TRAD_IN["fr"]["ev_ufficiale"] + ") Les sites non officiels facturent plus que les frais du gouvernement."),
        }
    return [(f["q"], risposte[f["id"]]) for f in IN["faq"][lingua] if f["id"] in risposte]


def prima_frase_lingua_in(lingua, paesi):
    u = {k: uguali_in(paesi, k) for k, _ in COL_IN}
    L = lingua
    if L == "de":
        return (f"Laut den offiziellen Gebührentabellen der indischen Regierung (Bureau of Immigration) vom {data_de(data_tab_in('fee_tv'))} und vom "
                f"{data_de(data_tab_in('fee_altri'))}, geprüft am {data_de(data_in())}, kostet das e-Tourist-Visum für Indien für Staatsangehörige Deutschlands, "
                f"Österreichs, der Schweiz und Liechtensteins {usd_l(u['tv30_apr_giu'], L)} für 30 Tage (April bis Juni), {usd_l(u['tv30_lug_mar'], L)} für 30 Tage (Juli bis März), "
                f"{usd_l(u['tv1'], L)} für ein Jahr und {usd_l(u['tv5'], L)} für fünf Jahre, zuzüglich 3 % Bankgebühr.")
    ref = IN_PER["FR"]
    return (f"Selon les tableaux officiels des frais du gouvernement indien (Bureau of Immigration) du {data_fr(data_tab_in('fee_tv'))} et du "
            f"{data_fr(data_tab_in('fee_altri'))}, vérifiés le {data_fr(data_in())}, le e-Visa touristique pour l’Inde coûte pour les Français "
            f"{usd_l(val_in(ref, 'tv30_apr_giu'), L)} pour 30 jours (avril à juin), {usd_l(val_in(ref, 'tv30_lug_mar'), L)} pour 30 jours (juillet à mars), "
            f"{usd_l(val_in(ref, 'tv1'), L)} pour un an et {usd_l(val_in(ref, 'tv5'), L)} pour cinq ans, plus 3 % de frais bancaires"
            + (" ; les autres pays du tableau ci-dessous paient les mêmes montants pour le e-Visa touristique." if all(val_in(p, k) == val_in(ref, k) for p in paesi for k, _ in COL_TV)
               else " ; les montants des autres pays sont dans le tableau ci-dessous."))


def pagina_lingua_in(lingua):
    rel = "../../"
    PL = IN["pagine_lingua"][lingua]
    paesi = [IN_PER[c] for c in PL["paesi"]]
    url = (IN_DE if lingua == "de" else IN_FR) + "/"
    faq_h, faq_ld = html_faq_in(faq_lingua_in(lingua, paesi), "Fragen" if lingua == "de" else "Questions")
    if lingua == "de":
        h1 = f"Indien e-Visum Kosten ({ANNO}): offizielle Preise für Deutschland, Österreich und die Schweiz"
        titoli = [f"Indien e-Visum Kosten ({ANNO}): Deutschland, Österreich, Schweiz", f"Indien e-Visum Kosten ({ANNO})"]
        desc = f"Was kostet das e-Visum für Indien? Offizielle Tabelle: 30 Tage, 1 Jahr, 5 Jahre, e-Business, für DE, AT, CH. Geprüft am {data_de(data_in())}."
        testi = {"top": "Indien e-Visum · Kosten", "tab": "Kosten nach Staatsangehörigkeit (US-Dollar)",
                 "noti": ("Die offizielle Tabelle nennt nur US-Dollar. Für das 30-Tage-Visum hat sie zwei Spalten, „April to June“ und „July to March“; "
                          "sie sagt nicht, ob der Monat der Antragstellung oder der Einreise gemeint ist. Die Tabelle für die weiteren e-Visa nennt im Titel "
                          "auch das e-Conference-Visum, hat dafür aber keine eigene Spalte."),
                 "pagare": "Zahlung und Fristen", "en": "Alle Länder auf Englisch: India e-Visa fee by nationality",
                 "chiusura": "Diese Seite ist eine Information, keine Rechtsberatung. An der Grenze entscheiden die Einwanderungsbeamten."}
    else:
        h1 = f"Prix du e-Visa pour l’Inde ({ANNO}) : tarifs officiels pour la France, la Belgique, la Suisse et le Maroc"
        titoli = [f"Prix du e-Visa pour l’Inde ({ANNO}) : France, Belgique, Suisse", f"Prix du e-Visa pour l’Inde ({ANNO})"]
        desc = f"Prix du e-Visa pour l’Inde d’après le tableau officiel : 30 jours, 1 an, 5 ans, business, pour FR, BE, CH, LU, MC, MA. Vérifié le {data_fr(data_in())}."
        art_fr = {"Algérie": "l’Algérie", "République démocratique du Congo": "la République démocratique du Congo"}
        fuori = " et ".join(art_fr.get(NOMI_FR[x], NOMI_FR[x]) for x in PL.get("fuori", []))
        fuori = fuori[:1].upper() + fuori[1:]
        testi = {"top": "e-Visa Inde · prix", "tab": "Prix par nationalité (dollars US)",
                 "noti": ("Le tableau officiel donne les prix uniquement en dollars US. Pour le visa de 30 jours, il a deux colonnes, « April to June » et "
                          "« July to March » ; il ne dit pas s’il s’agit du mois de la demande ou de l’arrivée. Le titre du tableau des autres e-Visa cite "
                          f"aussi le e-Conference Visa, sans colonne à part. {fuori} ne figurent dans aucun des deux tableaux officiels."),
                 "pagare": "Paiement et délais", "en": "Tous les pays en anglais : India e-Visa fee by nationality",
                 "chiusura": "Cette page est une information, pas un conseil juridique. À la frontière, les agents de l’immigration décident."}
    corpo = f"""{STILE_IN}<section class="hero">{h1_diviso(h1)}</section>
<section class="card summary" aria-label="{"Antwort" if lingua == "de" else "Réponse"}">
<div class="s-top"><span class="sq">{ico("passport")}</span><span>{escape(testi["top"])}</span><span>{ANNO}</span></div>
<div class="s-body"><p class="lead" id="answer">{escape(prima_frase_lingua_in(lingua, paesi))}</p></div></section>
{avviso_in(lingua)}
<h2>{escape(testi["tab"])}</h2>
{tabella_lingua_in(paesi, lingua)}
{fonte_lingua_in(lingua)}
{blocco_cit_in(["pdf_3"], lingua)}
<p class="small">{escape(testi["noti"])}</p>
{AD}
<h2>{escape(testi["pagare"])}</h2>
<p>{"Auf die Frage, ob eine andere Website als die der Regierung den Antrag annehmen kann, antwortet die offizielle e-Visa-Seite:" if lingua == "de" else "À la question de savoir si un autre site que celui du gouvernement peut recevoir la demande, la page officielle du e-Visa répond :"}</p>
{blocco_cit_in(["ev_ufficiale"], lingua)}
{blocco_cit_in(["ev_4giorni", "ev_rimborso"], lingua)}
<p class="altri-pass">{ico("globe")}<span lang="en"><a href="{rel}{IN_BASE}/" hreflang="en">{escape(testi["en"])}</a> · <a href="{rel}{IN_ARR}/" hreflang="en">India e-Arrival card</a> · <a href="{rel}{IN_VOA}/" hreflang="en">Visa on arrival</a></span></p>
{faq_h}
<p class="small">{escape(testi["chiusura"])} <a href="{rel}contact/?ref={IN_BASE}">{"Fehler gefunden? Schreiben Sie uns" if lingua == "de" else "Une erreur ? Écrivez-nous"}</a>.</p>"""
    pagina(url, scegli(titoli, LIMITE_TITOLO_IN), scegli([desc], LIMITE_DESCRIZIONE), corpo,
           briciole=[("India e-Visa fee", f"{IN_BASE}/"), ("Deutsch" if lingua == "de" else "Français", url)], ld_extra=faq_ld, lingua=lingua)
    LASTMOD[url] = data_in()


def home_in():
    if not IN:
        return ""
    voci = "".join(f'<a href="{url_in(IN_PAG_PER[c])}">{escape(IN_PER[c]["nome"])}<small>5 years: {escape(usd(val_in(IN_PER[c], "tv5")))}</small></a>'
                   for c in ("GB", "US", "CA", "AU", "DE", "SG") if c in IN_PAG_PER)
    return (f'<h2>Going to India? The e-Visa fee by nationality</h2><p>The fee for every e-Visa type and nationality, from the Government of India’s '
            f'official tables: <a href="{IN_BASE}/">India e-Visa fee by nationality</a>, <a href="{IN_VOA}/">visa on arrival</a> and the '
            f'<a href="{IN_ARR}/">e-Arrival card</a>.</p><div class="griglia">{voci}</div>')


def about_in(rel):
    if not IN:
        return ""
    return f"""<h2 id="{IN_BASE}">India e-Visa fee, visa on arrival and e-Arrival card</h2>
<p>Sources: the Government of India’s two official fee tables in PDF on <a href="{IN_EVISA}" rel="noopener">indianvisaonline.gov.in</a> (“{escape(IN["fonti"]["fee_tv"]["titolo"])}”, dated {data_lunga(data_tab_in("fee_tv"))}, and “{escape(IN["fonti"]["fee_altri"]["titolo"])}”, dated {data_lunga(data_tab_in("fee_altri"))}), the e-Visa, visa on arrival and home pages of the same website, and two pages of the Bureau of Immigration (Ministry of Home Affairs) on boi.gov.in, {len(IN["fonti"])} sources in all, read on {data_lunga(data_in())}.</p>
<p>Rules: every fee is copied from the official PDF tables by our script, which checks that it has read every row and stops if anything changes; a second reading of the same files with a different method must give the same countries and figures. The Bureau of Immigration says that any use of its material beyond downloading needs its approval, so we publish the figures as facts and quote its texts only in short extracts, with the link and the date. We link only to the official website for applying and paying, never to visa agencies. A nationality gets its own page only when people search for the fee for it; the German and French pages exist because people search for the fee in those languages. This is information, not legal advice.</p>"""


def controlli_in():
    """Controlli della sezione India in genera.py (verifica.py, punto 27, ricontrolla tutto)."""
    errori = []
    if not IN:
        return errori
    for fid in ("fee_tv", "fee_altri"):
        F = IN["fonti"][fid]
        T = IN["tabelle"][fid]
        if F["http"] != 200 or F["righe"] != len(T["righe"]) or [r["n"] for r in T["righe"]] != list(range(1, len(T["righe"]) + 1)):
            errori.append(f"india {fid}: tabella non letta con HTTP 200 o righe non consecutive")
    for c in IN["citazioni"]:
        if IN["fonti"][c["f"]]["http"] != 200:
            errori.append(f"india: citazione {c['id']} da una fonte non letta con HTTP 200")
    ids = set(IN_CIT)
    for gruppo, ff in IN["faq"].items():
        for f in ff:
            if any(i not in ids for i in f.get("cit", [])):
                errori.append(f"india: FAQ {gruppo} «{f['q']}» con citazione sconosciuta")
    for g in IN_PAGINE:
        if g["iso2"] not in IN_PER:
            errori.append(f"india: pagina per {g['iso2']} senza dati")
        elif len(scegli(titoli_in(g), LIMITE_TITOLO_IN)) > LIMITE_TITOLO_IN:
            errori.append(f"india {g['iso2']}: titolo oltre {LIMITE_TITOLO_IN} caratteri")
    if len({IN_PER[g["iso2"]]["slug"] for g in IN_PAGINE}) != len(IN_PAGINE) or any(IN_PER[g["iso2"]]["slug"] in ("indien-e-visum-kosten", "prix-e-visa-inde") for g in IN_PAGINE):
        errori.append("india: slug delle pagine per nazionalità duplicati")
    if SW_IN and not SW_IN.startswith("https://safetywing.com/"):
        errori.append("india: link SafetyWing non valido in dati/affiliati.json (_safetywing_india)")
    for lingua in ("de", "fr"):
        for c in IN["pagine_lingua"][lingua]["paesi"]:
            if c not in IN_PER or not IN_PER[c]["tv"]:
                errori.append(f"india: pagina {lingua}, Paese {c} non nelle tabelle")
    return errori


# ---------------------------------------------------------------- Scooter e motorini in vacanza: quale patente? (31/10/2026)
# Regole per Paese scritte a mano in dati/scooter_manuali.json (citazioni parola per parola nella lingua originale, con la nostra traduzione),
# fonti rilette da raccolta/scooter.py (HTTP 200, data di lettura, impronta della zona citata) che scrive dati/scooter.json. Una pagina solo per
# i Paesi con la regola letta da una fonte ufficiale (codice della strada, regolamento delle patenti, portale dell'amministrazione, consigli di
# viaggio del governo britannico per la patente britannica); gli altri Paesi provati stanno nell'indice come "Not read" con il motivo. Nessun
# riquadro di affiliazione: DiscoverCars noleggia auto, non scooter, e il noleggio di moto (BikesBooking) passa da Travelpayouts, in pausa.
# Nessuna promessa: ogni pagina dice di controllare con il noleggiatore e con la pagina ufficiale. Controlli: verifica.py, punto 28.
SC_BASE = "scooter-rental-licence"
_f_sc = DATI / "scooter.json"
SC = json.loads(_f_sc.read_text(encoding="utf-8")) if _f_sc.exists() else None
SC_PAESI = SC["paesi"] if SC else []
SC_PER = {p["iso2"]: p for p in SC_PAESI}
LIMITE_TITOLO_SC = 70
ESITI_SC = {"si": ("Yes", "b-gratis"), "no": ("No", "b-no"), "condizioni": ("Only with conditions", "b-altre"), "non_detto": ("Not stated", "b-muto")}
CASI_SC = [("50", "Moped (up to 50 cc)"), ("125", "Scooter or light motorcycle up to 125 cc"), ("oltre", "Bigger than 125 cc")]
PATENTI_SC = [("uk", "UK licence"), ("ue", "Licence from another EU country"), ("extra", "Licence from outside Europe (US, Canada, Australia...)")]
AVVISO_SC = ('<p class="avviso"><strong>Licence rules for scooters differ from country to country and can change, and rental companies may ask for '
             'more than the law.</strong> We quote the official texts word for word, with the date we read them; this is information, not legal '
             'advice. Check with the rental company and the official page before you ride.</p>')


def url_sc(p=None):
    return f"{SC_BASE}/" + (f"{p['slug']}/" if p else "")


def fonti_sc(p):
    return list(dict.fromkeys(c["f"] for c in p["citazioni"]))


def data_sc(p):
    return max(SC["fonti"][f]["letto_il"] for f in fonti_sc(p))


def cit_sc(p, id_):
    return next(c for c in p["citazioni"] + SC["generali"] if c["id"] == id_)


def link_fonte_sc(fid):
    F = SC["fonti"][fid]
    return f'<a href="{escape(F["pagina"])}" rel="noopener">{escape(F["titolo"])}</a>'


def blocco_cit_sc(cc):
    """Citazioni raggruppate per fonte: virgolette, traduzione nostra (fonti non inglesi), fonte, ente e data di lettura."""
    out, gruppi = [], []
    for x in cc:
        if gruppi and gruppi[-1][0] == x["f"]:
            gruppi[-1][1].append(x)
        else:
            gruppi.append((x["f"], [x]))
    for fid, gg in gruppi:
        F = SC["fonti"][fid]
        h = "".join(f"<p>{escape(x['x'])}</p>" + (f'<p class="trad" lang="en"><em>Our translation:</em> {escape(x["tr"])}</p>' if x.get("tr") else "")
                    for x in gg)
        lingua = f' lang="{F["lingua"]}"' if F["lingua"] != "en" else ""
        agg = f", page updated on {data_lunga(F['aggiornata_il'])}" if F.get("aggiornata_il") else ""
        out.append(f'<blockquote class="cit"{lingua}>{h}</blockquote><p class="fonte">Source: {link_fonte_sc(fid)} ({escape(F["ente"])}{agg}), '
                   f'checked on {data_lunga(F["letto_il"])}. Quoted word for word.</p>')
    return "".join(out)


def risposta_sc(p):
    return f"According to {p['chi']}, checked on {data_lunga(data_sc(p))}, {p['risposta']}"


def badge_sc(e):
    return f'<span class="badge {ESITI_SC[e][1]}">{escape(ESITI_SC[e][0])}</span>'


def faq_sc(p):
    """Domande da ricerche vere: parole nostre (pre, post) + citazioni; le citazioni non inglesi entrano con la traduzione nostra."""
    out = []
    for f in p["faq"]:
        parti = [f["pre"]] if f["pre"] else []
        for i in f["cit"]:
            x = cit_sc(p, i)
            parti.append(f"“{x.get('tr') or x['x']}”" + (" (our translation)" if x.get("tr") else ""))
        if f["post"]:
            parti.append(f["post"])
        out.append((f["q"], " ".join(parti)))
    out.append(("Where does this answer come from?", f"From {p['chi']}, read on {data_lunga(data_sc(p))} and quoted word for word on this page "
                                                     "(with our translation when the text is not in English). Rental companies can ask for more "
                                                     "than the law: check with the rental company and the official page before you ride."))
    return out


def box_assicurazione_sc():
    """Riquadro "Travel insurance": la frase generale del governo britannico (consigli per la Thailandia), con la fonte."""
    if not SC or not SC["generali"]:
        return ""
    return (f'<h2 id="insurance">Travel insurance and scooters</h2><section class="card" aria-label="Travel insurance">'
            f'<p>Riding without the licence category the law asks for can also leave you without insurance cover. The UK government puts it this way '
            f'in its travel advice for Thailand:</p>{blocco_cit_sc(SC["generali"])}<p class="small">Read your policy before you ride.</p></section>')


def link_sc_pat(rel, iso2):
    """Riga 'Renting a scooter in X?' nelle pagine Driving abroad dei Paesi con una pagina scooter."""
    p = SC_PER.get(iso2)
    if not p:
        return ""
    return (f'<p class="altri-pass">{ico("car")}<span>Renting a scooter or a moped instead? <a href="{rel}{url_sc(p)}">{escape(p["nome"])}: '
            f'what a car licence covers (moped, 125 cc)</a></span></p>')


def tabella_casi_sc(p):
    righe = "".join(f'<tr data-voce data-caso="{k}"><td data-l="Vehicle">{escape(nome)}</td><td data-l="With a car licence">{badge_sc(p["casi"][k]["esito"])} '
                    f'{escape(p["casi"][k]["breve"])}</td></tr>' for k, nome in CASI_SC)
    return (f'<div class="tab tab-b"><table><caption class="cap">{escape(p["nome"])}: what a car licence covers, from the official text, checked on '
            f'{data_lunga(data_sc(p))}</caption><thead><tr><th>Vehicle</th><th>With a car licence</th></tr></thead><tbody>{righe}</tbody></table></div>')


def sezione_casi_sc(p):
    """Un sottotitolo per caso con le frasi ufficiali; una frase già mostrata per un caso precedente non si ripete (rimando "above")."""
    out, viste = [], set()
    for k, nome in CASI_SC:
        v = p["casi"][k]
        cc = [cit_sc(p, i) for i in v["cit"] if i not in viste]
        gia = [i for i in v["cit"] if i in viste]
        viste.update(v["cit"])
        out.append(f'<h3 id="case-{k}">{escape(nome)}: {escape(ESITI_SC[v["esito"]][0])}</h3>{blocco_cit_sc(cc) if cc else ""}'
                   + (f'<p class="small">Same official text as above{" (and the text below)" if cc else ""}.</p>' if gia and not cc else "")
                   + (f'<p class="small">{escape(v["nota"])}</p>' if v.get("nota") else ""))
    return "".join(out)


def etichette_fonti_sc(p, rel=""):
    """Link brevi alle fonti di un Paese (nome prima dei due punti del titolo), senza ripetizioni."""
    out = {}
    for f in fonti_sc(p):
        out.setdefault(SC["fonti"][f]["titolo"].split(":")[0], f)
    return " · ".join(f'<a href="{escape(SC["fonti"][f]["pagina"])}" rel="noopener">{escape(n)}</a>' for n, f in out.items())


def tabella_patenti_sc(p):
    righe = []
    for k, nome in PATENTI_SC:
        v = p["patenti"][k]
        righe.append(f'<tr data-voce data-patente="{k}"><td data-l="Your licence">{escape(nome)}</td><td data-l="What the official text says">{badge_sc(v["esito"])} '
                     f'{escape(v["breve"]) if v["esito"] != "non_detto" else ""}{(" " if v["esito"] != "non_detto" else "") + escape(v["nota"]) if v.get("nota") else ""}</td></tr>')
    return (f'<div class="tab tab-b"><table><caption class="cap">{escape(p["nome"])}: does the rule depend on where your licence is from?</caption>'
            f'<thead><tr><th>Your licence</th><th>What the official text says</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>')


def titolo_sc(p):
    return p["titolo"]


def descrizione_sc(p):
    e = p["casi"]["125"]["esito"]
    return scegli([f"{p['nome']}: can you ride a moped or a 125 cc scooter on a car licence? {ESITI_SC[e][0]}, from the official text, checked on {data_lunga(data_sc(p))}.",
                   f"{p['nome']}: moped and 125 cc scooter on a car licence, from the official text."], LIMITE_DESCRIZIONE)


def pagina_sc(p):
    rel = "../../"
    faq_h, faq_ld = html_faq_tr(faq_sc(p))
    e125 = p["casi"]["125"]["esito"]
    fonti = " · ".join(link_fonte_sc(f) for f in fonti_sc(p))
    altro = "".join(f'<h3>{escape(a["titolo"])}</h3>{blocco_cit_sc([cit_sc(p, i) for i in a["cit"]])}' for a in p["altro"])
    altri = "".join(f'<a href="{rel}{url_sc(q)}">{escape(q["nome"])}<small>125 cc: {escape(ESITI_SC[q["casi"]["125"]["esito"]][0])}</small></a>'
                    for q in SC_PAESI if q is not p)
    corpo = f"""<section class="hero">{h1_diviso(p["h1"])}</section>
<section class="card summary" aria-label="Answer">
<div class="s-top"><span class="sq">{ico("car")}</span><span>Scooter rental · {escape(p["nome"])}</span><span>{ANNO}</span></div>
<div class="s-body">
<div class="esito e-srv {({"si": "si", "no": "no"}).get(e125, "manuale")}">{ico("alert" if e125 != "si" else "check")}<strong>125 cc on a car licence: {escape(ESITI_SC[e125][0])}{escape(ambito_griglia_sc(p))}</strong></div>
<p class="lead" id="answer">{escape(risposta_sc(p))}</p>
<p class="small">Official source{"s" if len(fonti_sc(p)) > 1 else ""}: {fonti}.</p>
</div></section>
{AVVISO_SC}
<h2 id="cases">Moped, 125 cc or bigger: what a car licence covers</h2>
{tabella_casi_sc(p)}
{sezione_casi_sc(p)}
{AD}
<h2 id="licence">Does it depend on where your licence is from?</h2>
{tabella_patenti_sc(p)}
{blocco_cit_sc([cit_sc(p, i) for k, _ in PATENTI_SC for i in p["patenti"][k]["cit"] if p["patenti"][k]["esito"] != "non_detto" and i not in {j for kk, _ in CASI_SC for j in p["casi"][kk]["cit"]}])}
{f'<h2 id="also">Also in the official text</h2>{altro}' if altro else ""}
{box_assicurazione_sc()}
{link_guida(rel, p["iso2"])}
{faq_h}
<h2>Other countries</h2>
<div class="griglia">{altri}</div>
<p class="small">Spotted a change? <a href="{rel}contact/?ref=scooter-rental-licence">Tell us</a>. <a href="{rel}{SC_BASE}/">Scooter rental: every country we checked</a>.</p>"""
    pagina(url_sc(p), scegli([titolo_sc(p)], LIMITE_TITOLO_SC), descrizione_sc(p), corpo,
           briciole=[("Scooter rental: which licence?", url_sc()), (p["nome"], url_sc(p))], ld_extra=faq_ld)
    LASTMOD[url_sc(p)] = data_sc(p)


def ambito_riga_sc(p):
    """Paese con fonte limitata (Grecia: consigli britannici per patenti britanniche): avviso nella riga della tabella dell'indice."""
    return f'<br><small>{escape(p["ambito"])}</small>' if p.get("ambito") else ""


def ambito_griglia_sc(p):
    return f" ({p['ambito_breve']})" if p.get("ambito_breve") else ""


def elenco_sc(nomi):
    return ", ".join(nomi[:-1]) + " and " + nomi[-1] if len(nomi) > 1 else (nomi[0] if nomi else "")


def prima_frase_sc():
    nome = lambda p: p["nome"] + (f" ({p['ambito']})" if p.get("ambito") else "")  # noqa: E731
    per = {e: [nome(p) for p in SC_PAESI if p["casi"]["125"]["esito"] == e] for e in ESITI_SC}
    m_si = [p["nome"] for p in SC_PAESI if p["casi"]["50"]["esito"] == "si"]
    m_no = [nome(p) for p in SC_PAESI if p["casi"]["50"]["esito"] == "no"]
    pezzi = []
    if per["condizioni"]:
        pezzi.append(f"only under conditions in {elenco_sc(per['condizioni'])}")
    if per["no"]:
        pezzi.append(f"not at all in {elenco_sc(per['no'])}")
    if per["si"]:
        pezzi.append(f"without conditions in {elenco_sc(per['si'])}")
    moto = (f"; a moped is covered by a car licence in {elenco_sc(m_si)}" if m_si else "") + (f" but not in {elenco_sc(m_no)}" if m_no else "")
    return (f"Of the {len(SC_PAESI)} countries whose official rule we could read (last checked on {data_lunga(SC['controllato_il'])}), a car licence "
            f"covers a 125 cc scooter {' and '.join(pezzi)}{moto}; for {len(SC['non_letti'])} more countries we could not read an official rule yet.")


def titolo_indice_sc():
    return [f"Scooter Rental Abroad: 125cc on a Car Licence? By Country ({ANNO})", f"Scooter Rental: 125cc on a Car Licence? ({ANNO})"]


def pagina_indice_sc():
    rel = "../"
    righe = []
    for p in SC_PAESI:
        righe.append(f'<tr data-voce id="{p["slug"]}"><td data-l="Country"><a href="{rel}{url_sc(p)}">{escape(p["nome"])}</a>{ambito_riga_sc(p)}</td>'
                     + "".join(f'<td data-l="{escape(nome)}">{badge_sc(p["casi"][k]["esito"])}</td>' for k, nome in CASI_SC)
                     + f'<td data-l="Official source">{etichette_fonti_sc(p)}</td><td data-l="Checked">{data_lunga(data_sc(p))}</td></tr>')
    nl = "".join(f'<li id="not-read-{x["iso2"].lower()}"><strong>{escape(x["nome"])}</strong>: {escape(x["motivo"])}</li>' for x in SC["non_letti"])
    griglia = "".join(f'<a href="{rel}{url_sc(p)}">{escape(p["nome"])}<small>125 cc: {escape(ESITI_SC[p["casi"]["125"]["esito"]][0])}{escape(ambito_griglia_sc(p))}</small></a>' for p in SC_PAESI)
    faq = [faq_sc(p)[0] for p in SC_PAESI]
    faq_h, faq_ld = html_faq_tr(faq)
    d = data_lunga(SC["controllato_il"])
    corpo = f"""<section class="hero">{h1_diviso(f"Scooter and moped rental abroad: can you ride a 125 cc on a car licence? ({ANNO})")}
<p class="lead" id="answer">{escape(prima_frase_sc())}</p></section>
<div class="griglia">{griglia}</div>
{AVVISO_SC}
<h2>Every country we could read</h2>
<p>“Yes”, “No” and “Only with conditions” are our short summary of the official text; each country page quotes it word for word, with our translation, the link and the date. “Not stated” means the official text we read says nothing about that case.</p>
<div class="tab tab-b tab-srv"><table><caption class="cap">What a car licence covers for mopeds and scooters, from the official texts, checked on {d}</caption><thead><tr><th>Country</th>{"".join(f"<th>{escape(n)}</th>" for _, n in CASI_SC)}<th>Official source</th><th>Checked</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>
{AD}
{box_assicurazione_sc()}
{faq_h}
<h2 id="not-read">Countries we could not read yet</h2>
<p>We publish a country only when an official text (the highway code, the licence rules, the government's own information site, or the UK government's travel advice for UK licences) says which licence you need. For these countries we tried and could not read the rule:</p>
<ul>{nl}</ul>
<h2>How we check</h2>
<p>We read the official texts (and nothing else: no rental companies, forums or blogs), quote the rule word for word in its own language with our English translation, and give the date we read it. Each page links the official text. Driving a car instead? <a href="{rel}{PAT_BASE}/">Driving abroad: do you need an international driving permit?</a> More on the <a href="{rel}about/#scooter-rental-licence">About page</a>. Spotted a change? <a href="{rel}contact/?ref=scooter-rental-licence">Tell us</a>.</p>"""
    desc = scegli([f"Can you ride a moped or a 125 cc scooter on a car licence in {elenco_sc([p['nome'] for p in SC_PAESI])}? Official texts, checked on {d}.",
                   "Moped and 125 cc scooter on a car licence, country by country, from the official texts."], LIMITE_DESCRIZIONE)
    pagina(url_sc(), scegli(titolo_indice_sc(), LIMITE_TITOLO_SC), desc, corpo, briciole=[("Scooter rental: which licence?", url_sc())], ld_extra=faq_ld)
    LASTMOD[url_sc()] = SC["controllato_il"]


def home_sc():
    if not SC:
        return ""
    voci = "".join(f'<a href="{url_sc(p)}">{escape(p["nome"])}<small>125 cc: {escape(ESITI_SC[p["casi"]["125"]["esito"]][0])}{escape(ambito_griglia_sc(p))}</small></a>' for p in SC_PAESI)
    return (f'<h2>Renting a scooter: is a car licence enough?</h2><p>What the official texts say about mopeds and 125 cc scooters on a car licence, '
            f'quoted with the date: <a href="{SC_BASE}/">every country we checked</a>.</p><div class="griglia">{voci}</div>')


def about_sc(rel):
    if not SC:
        return ""
    enti = list(dict.fromkeys(F["ente"] for F in SC["fonti"].values()))
    return f"""<h2 id="scooter-rental-licence">Scooter rental: which licence?</h2>
<p>Sources: {escape("; ".join(enti))}; {len(SC["fonti"])} official pages in all, read on {data_lunga(SC["controllato_il"])}. Each country page links every text it quotes. UK government travel advice: Open Government Licence v3.0.</p>
<p>Rules: every sentence between quotation marks is copied word for word from the official text, in its own language, with our English translation. We publish a country only when an official text says which licence you need for a moped or a scooter; the countries we tried and could not read are listed with the reason. “Not stated” means the text says nothing about that case: we never fill a gap with what rental companies or forums say. This is information, not legal advice: check with the rental company and the official page before you ride.</p>"""


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
{home_ped()}
{home_gom()}
{home_big()}
{home_fl()}
{home_tr()}
{home_tb()}
{home_pet()}
{home_bb()}
{home_in()}
{home_sc()}
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
{about_ped(rel)}
{about_gom(rel)}
{about_big(rel)}
{about_fl(rel)}
{about_tr(rel)}
{about_tb(rel)}
{about_pet(rel)}
{about_bb(rel)}
{about_in(rel)}
{about_sc(rel)}
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
    # Cookie, link di affiliazione e pubblicità: con AdSense acceso (monetizzazione.json) o con link di affiliazione, il testo
    # comune di monetizzazione.py (GoatCounter senza cookie, pubblicità con il consenso di Google); altrimenti il testo di oggi.
    cookie = MON.privacy_cookie("en", SITO_ID, ci_sono_affiliati()) or """<h2>Cookies and visit counter</h2><p>This site does not use profiling cookies. To count visits we use <a href="https://www.goatcounter.com/" rel="noopener">GoatCounter</a>, a privacy-friendly counter: it sets no cookies and stores nothing in your browser, builds no profiles and does not store your IP address, your full browser signature or any identifier. It keeps only aggregate numbers (page, hour or day, browser, country, screen width) on servers in the European Union and shares nothing with third parties; see <a href="https://www.goatcounter.com/help/privacy" rel="noopener">GoatCounter's privacy policy</a>. If we add advertising or affiliate links in the future, we will update this notice and ask for your consent where required before any advertising cookies are used.</p>"""
    # Amazon Associates (dal 6/11/2026, solo con i link Amazon accesi nel bagaglio a mano): frase obbligatoria anche qui
    amazon = ("<h2>Amazon Associates</h2><p>Before You Fly is a participant in the Amazon Associates programmes of Amazon.co.uk and Amazon.com. "
              f"{AMAZON_FRASE} Our cabin bag pages link to Amazon searches for bags in the right size; the links are marked as affiliate links.</p>"
              if AMAZON_ACCESO else "")
    corpo = f"""<section class="hero"><h1>Privacy notice</h1><p class="small">Last updated: November 2026</p></section><div class="testo">
<h2>Who is responsible</h2><p>The data controller is Massimiliano Cori (Italy), who runs {NOME} as an independent project. You can contact us through the <a href="contact/">contact form</a>.</p>
<h2>What we collect</h2><p>Only what you type in the contact form: your email, the country or airport and your message. We also record the page or link you came from, to understand which pages need corrections. The passport checker runs in your browser: the dates you type are not sent to us.</p>
<h2>Why</h2><p>To answer your messages and correct the site. The legal basis is your consent (Art. 6(1)(a) GDPR), which you can withdraw at any time.</p>
<h2>Who processes data for us</h2><p>The site and its form are hosted by Netlify, Inc., which stores form data on our behalf and may process it outside the EU with the safeguards required by the GDPR (standard contractual clauses). We do not sell or share your data.</p>
{cookie}
{amazon}
<h2>How long</h2><p>Messages are kept for up to 12 months after our last exchange.</p>
<h2>Your rights</h2><p>You can ask for access, correction, deletion, restriction, portability and objection (Articles 15–22 GDPR) and you can complain to the Italian data protection authority (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>) or the authority in your country.</p></div>"""
    pagina("privacy.html", f"Privacy | {NOME}", f"Privacy notice of {NOME}.", corpo)


def extra():
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n")
    (SITO / f"{CHIAVE_INDEXNOW}.txt").write_text(CHIAVE_INDEXNOW)  # file chiave IndexNow: non in sitemap, non linkato
    MON.scrivi_ads_txt(SITO_ID, SITO)  # sito/ads.txt solo con AdSense acceso (monetizzazione.json)
    # lastmod: data vera dell'ultima lettura della fonte per le pagine "Available in?" (LASTMOD), data di oggi per le altre
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{LASTMOD.get(u, OGGI.isoformat())}</lastmod></url>" for u in URLS)
    (SITO / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n')
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Deploy only when something changed in beforeyoufly/sito.
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."

# Dominio proprio dall'8/11/2026: il vecchio indirizzo before-you-fly.netlify.app porta al nuovo, pagina per pagina.
[[redirects]]
  from = "https://before-you-fly.netlify.app/*"
  to = "https://before-you-fly.com/:splat"
  status = 301
  force = true

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
           'the <a href="/liquids/">liquids rules by airport</a>, the <a href="/cabin-bags/">cabin bag size by airline</a> <a href="/available-in/">apps and services by country</a> <a href="/driving-abroad/">driving abroad with your licence</a>, <a href="/tolls-rental-car/">tolls with a rental car</a>, <a href="/winter-tyres-rental-car/">winter tyres with a rental car</a>, <a href="/foreign-licence-canada-australia-nz/">driving in Canada, Australia and New Zealand on a foreign licence</a>, <a href="/ticket-release-dates/">when tickets go on sale at major attractions</a>, <a href="/public-transport-rules/">public transport fines and contactless payment by city</a>, <a href="/train-luggage-rules/">luggage rules on European trains</a>, <a href="/eurostar-check-in-times/">Eurostar check-in times</a>, <a href="/scooter-rental-licence/">which licence you need to rent a scooter</a>, <a href="/blue-badge-abroad/">where your UK Blue Badge is recognised abroad</a> or the <a href="/india-e-visa-fee/">India e-Visa fee by nationality</a>.</p></section>', indicizza=False, assoluto=True)


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
    if len({A["iata"] for A in AER["aeroporti"]}) != len(AER["aeroporti"]):
        errori.append("sigle IATA degli aeroporti duplicate")
    # aeroporti aggiunti dal 5/11/2026: lettura diretta (HTTP 200), impronta della zona citata, ricerca vera con il nome del titolo
    per_slug = {A["slug"]: A for A in AER["aeroporti"]}
    for A in AER["aeroporti"]:
        if A["slug"] not in LIQ_DOMANDA["aeroporti"] and "impronta" not in A:  # aeroporti di prima del 5/11/2026: niente impronta né ricerche salvate
            continue
        if A.get("gestore") == "aena" and (A["controllato_il"] != "2026-11-05" or not A.get("pagina_gestore") or A["pagina_gestore"].split("/")[-1] not in A.get("nota", "")):
            errori.append(f"aeroporto {A['slug']}: pagina Aena senza la data, la pagina del gestore o la nota comune alle altre")
        if A.get("lettura") != "diretta" or A.get("http") != 200 or not re.fullmatch(r"[0-9a-f]{16}", A.get("impronta") or "") \
                or not A["url"].startswith("https://"):
            errori.append(f"aeroporto {A['slug']}: aggiunto dal 5/11/2026 senza lettura diretta, HTTP 200, impronta o URL https")
        if A.get("fonte2") and not re.fullmatch(r"[0-9a-f]{16}", A["fonte2"].get("impronta") or ""):
            errori.append(f"aeroporto {A['slug']}: seconda fonte senza impronta")
        R = LIQ_DOMANDA["aeroporti"].get(A["slug"])
        sugg = (R or {}).get("uk", []) + (R or {}).get("us", [])
        if A["controllato_il"] == "2026-11-05" and A.get("gestore") == "aena" and not R:  # gli 11 Aena di ottobre: riletti il 5/11, già in pagina prima
            continue
        if not R or not any(x.startswith(R["ricerca"]) for x in sugg) or not R["ricerca"].startswith(nome_titolo(A).lower() + " airport liquid"):
            errori.append(f"aeroporto {A['slug']}: nessuna ricerca vera '<nome del titolo> airport liquid…' in dati/liquidi_domanda.json")
    for s_ in LIQ_DOMANDA["aeroporti"]:
        if s_ not in per_slug:
            errori.append(f"liquidi_domanda.json: {s_} non è tra gli aeroporti")
    # riquadri di guadagno: solo aeroporti di vacanza esistenti, mai di partenza o di transito; Stay22 solo con un link della stessa città
    if len(set(NOLEGGIO_LIQ)) != len(NOLEGGIO_LIQ):
        errori.append("affiliati.json: aeroporti duplicati nel riquadro noleggio dei liquidi")
    for s_ in NOLEGGIO_LIQ:
        A = per_slug.get(s_)
        if not A or A["area"] == "UK and Ireland" or A["paese"] in PAESI_PARTENZA_LIQ or s_ in SCALI_TRANSITO_LIQ:
            errori.append(f"affiliati.json: riquadro noleggio dei liquidi su {s_} (aeroporto inesistente, di partenza o di transito)")
    if NOLEGGIO_LIQ and NOLEGGIO_AUTO and (not MON.dominio_ammesso(NOLEGGIO_AUTO) or not MON.dominio_in(urlparse(NOLEGGIO_AUTO).hostname, ["discovercars.com"])):
        errori.append(f"liquidi: NOLEGGIO_AUTO non punta a discovercars.com: {NOLEGGIO_AUTO}")
    for s_, k in ALLOGGI_LIQ.items():
        A, v = per_slug.get(s_), STAY22_BIG.get(k)
        if not A or s_ not in NOLEGGIO_LIQ or not v or v["citta"] != A["citta"] or not v["url"].startswith("https://booking.stay22.com/massimilianocori/"):
            errori.append(f"affiliati.json: riquadro Stay22 dei liquidi su {s_} senza aeroporto di vacanza o senza link Stay22 della stessa città ({k})")
    if AMAZON_ACCESO:  # Amazon Associates nel bagaglio a mano: un tag per ciascuno dei due mercati, 'url' = ricerca generica britannica
        if set(AMAZON_TAG) != {"amazon.co.uk", "amazon.com"} or not all(re.fullmatch(r"[a-z0-9-]+-2[01]", v or "") for v in AMAZON_TAG.values()):
            errori.append(f"affiliati.json, bagagli: tag Amazon mancanti o non validi: {AMAZON_TAG}")
        elif AMAZON_BAG["url"] != amazon_link("amazon.co.uk", "cabin bag"):
            errori.append(f"affiliati.json, bagagli: 'url' diverso dalla ricerca generica attesa {amazon_link('amazon.co.uk', 'cabin bag')}")
        for C in COMPAGNIE:
            if C["area"] not in MERCATI_AREA:
                errori.append(f"compagnia {C['slug']}: area {C['area']} senza mercato Amazon dichiarato (MERCATI_AREA)")
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
        if NOLEGGIO_AUTO:  # dal 30/10/2026 riquadro "Hire a car" acceso: solo DiscoverCars, link valido, riga di trasparenza
            if not MON.dominio_ammesso(NOLEGGIO_AUTO) or not MON.dominio_in(urlparse(NOLEGGIO_AUTO).hostname, ["discovercars.com"]):
                errori.append(f"patenti: NOLEGGIO_AUTO non punta a discovercars.com: {NOLEGGIO_AUTO}")
            for nome, h in (("box_noleggio", box_noleggio()), ("home_noleggio", home_noleggio())):
                errori += [f"patenti: {e}" for e in MON.controlla_link_pagina(h, nome, "en")[0]]
    if PED:  # pedaggi con l'auto a noleggio: fonti lette con HTTP 200, citazioni e FAQ coerenti (verifica.py, punto 20, ricontrolla tutto)
        for p in PED_PAESI:
            if p["iso2"] not in PAESI_ISO:
                errori.append(f"pedaggi {p['iso2']}: codice non in paesi_iso.json")
            ids = [c["id"] for c in p["citazioni"]]
            if len(set(ids)) != len(ids):
                errori.append(f"pedaggi {p['iso2']}: id di citazione duplicati")
            for f in fonti_ped(p):
                if f not in PED["fonti"] or PED["fonti"][f]["http"] != 200:
                    errori.append(f"pedaggi {p['iso2']}: fonte {f} non letta con HTTP 200")
            for q in p["faq"]:
                if any(i not in ids for i in q["cit"]):
                    errori.append(f"pedaggi {p['iso2']}: FAQ «{q['q']}» con citazione sconosciuta")
            if (p["noleggio"] == "detto") != any(c["tema"] == "noleggio" and re.search(r"rent|hire|rental", c["x"], re.I) for c in p["citazioni"]):
                errori.append(f"pedaggi {p['iso2']}: 'noleggio' = {p['noleggio']} senza (o con) una frase ufficiale sulle auto a noleggio")
            if len(p["titolo"]) > LIMITE_TITOLO_PED or str(ANNO) not in p["titolo"]:
                errori.append(f"pedaggi {p['iso2']}: titolo oltre {LIMITE_TITOLO_PED} caratteri o senza l'anno")
        if NOLEGGIO_AUTO:
            errori += [f"pedaggi: {e}" for e in MON.controlla_link_pagina(box_noleggio_ped(), "box_noleggio_ped", "en")[0]]
    if GOM:  # gomme invernali e catene: fonti lette con HTTP 200, citazioni, traduzioni e FAQ coerenti (verifica.py, punto 21, ricontrolla tutto)
        for p in GOM_PAESI:
            ids = [c["id"] for c in p["citazioni"]]
            if p["iso2"] not in PAESI_ISO or p["obbligo"] not in OBBLIGO_GOM or p["noleggio"] not in ("detto", "non_detto"):
                errori.append(f"gomme {p['iso2']}: codice, obbligo o noleggio non validi")
            if len(set(ids)) != len(ids):
                errori.append(f"gomme {p['iso2']}: id di citazione duplicati")
            for f in fonti_gom(p):
                if f not in GOM["fonti"] or GOM["fonti"][f]["http"] != 200:
                    errori.append(f"gomme {p['iso2']}: fonte {f} non letta con HTTP 200")
                elif GOM["fonti"][f]["lingua"] != "en":
                    errori += [f"gomme {p['iso2']}: citazione {c['id']} senza traduzione" for c in p["citazioni"] if c["f"] == f and c["id"] not in p.get("traduzioni", {})]
            for q in p["faq"]:
                if any(i not in ids for i in q["cit"]):
                    errori.append(f"gomme {p['iso2']}: FAQ «{q['q']}» con citazione sconosciuta")
            if p["noleggio"] == "detto":
                errori.append(f"gomme {p['iso2']}: 'noleggio' = detto, ma la sezione non ha ancora frasi ufficiali sulle auto a noleggio")
            if len(p["titolo"]) > LIMITE_TITOLO_GOM or STAGIONE_GOM not in p["titolo"]:
                errori.append(f"gomme {p['iso2']}: titolo oltre {LIMITE_TITOLO_GOM} caratteri o senza la stagione {STAGIONE_GOM}")
        if NOLEGGIO_AUTO:
            errori += [f"gomme: {e}" for e in MON.controlla_link_pagina(box_noleggio_gom(), "box_noleggio_gom", "en")[0]]
    if BIG:  # biglietti delle attrazioni: fonti lette con HTTP 200, citazioni e regole coerenti (verifica.py, punto 22, ricontrolla tutto)
        for a in BIG_ATT:
            ids = [c["id"] for c in a["citazioni"]]
            if len(set(ids)) != len(ids):
                errori.append(f"biglietti {a['slug']}: id di citazione duplicati")
            for f in fonti_big(a):
                if f not in BIG["fonti"] or BIG["fonti"][f]["http"] != 200:
                    errori.append(f"biglietti {a['slug']}: fonte {f} non letta con HTTP 200")
            for r in a["uscite"] + a["uscite_testo"] + [a["chiusure"], a["orari"], a["biglietteria"]] + ([a["gratis"]] if a.get("gratis") else []) + a["orari_speciali"]:
                if (not r.get("cit") and not (r is a["chiusure"] and r.get("nota"))) or any(i not in ids for i in r.get("cit", [])):
                    errori.append(f"biglietti {a['slug']}: regola senza citazione o con citazione sconosciuta")
            for r in a["uscite"]:
                if r["tipo"] not in TIPI_USCITA_BIG or not (re.fullmatch(r"\d{2}:\d{2}", r["ora"] or "")
                                                            or (r["ora"] is None and r["tipo"] in ("mensile", "date"))):
                    errori.append(f"biglietti {a['slug']}: regola di uscita {r['id']} non valida")
            for q in a["faq"]:
                if q["tipo"] not in ("testo", "uscita", "gratis", "giorno") or any(i not in ids for i in q["cit"]):
                    errori.append(f"biglietti {a['slug']}: FAQ «{q['q']}» non valida")
            if len(a["titolo"]) > LIMITE_TITOLO_BIG or STAGIONE_BIG not in a["titolo"]:
                errori.append(f"biglietti {a['slug']}: titolo oltre {LIMITE_TITOLO_BIG} caratteri o senza gli anni {STAGIONE_BIG}")
        if VIATOR_TOUR:
            if not MON.dominio_ammesso(VIATOR_TOUR) or not MON.dominio_in(urlparse(VIATOR_TOUR).hostname, ["viator.com"]):
                errori.append(f"biglietti: VIATOR_TOUR non punta a viator.com: {VIATOR_TOUR}")
            errori += [f"biglietti: {e}" for e in MON.controlla_link_pagina(box_tour_big(), "box_tour_big", "en")[0]]
            for s_, u_ in VIATOR_PER_ATTRAZIONE.items():  # link per attrazione: attrazione esistente, https, viator.com, stesso pid
                if s_ not in BIG_PER or not viator_link_valido(u_):
                    errori.append(f"biglietti: link Viator non valido per {s_}: {u_}")
                else:
                    errori += [f"biglietti: {e}" for e in MON.controlla_link_pagina(box_tour_big(BIG_PER[s_]), f"box_tour_big {s_}", "en")[0]]
        elif VIATOR_PER_ATTRAZIONE:
            errori.append("biglietti: VIATOR_PER_ATTRAZIONE pieno con VIATOR_TOUR vuoto")
        for s, v in STAY22_BIG.items():  # Stay22: solo booking.stay22.com/massimilianocori/, solo attrazioni esistenti
            if s not in BIG_PER or not MON.dominio_ammesso(v["url"]) or not v["url"].startswith("https://booking.stay22.com/massimilianocori/"):
                errori.append(f"biglietti: link Stay22 non valido per {s}: {v['url']}")
            elif s in BIG_PER:
                errori += [f"biglietti: {e}" for e in MON.controlla_link_pagina(box_alloggio_big(BIG_PER[s]), "box_alloggio_big", "en")[0]]
    if SC:  # scooter: fonti lette con HTTP 200, citazioni note, esiti validi, titoli (verifica.py, punto 28, ricontrolla tutto)
        for p_ in SC_PAESI:
            ids = [c["id"] for c in p_["citazioni"]]
            if len(set(ids)) != len(ids):
                errori.append(f"scooter {p_['slug']}: id di citazione duplicati")
            for f in fonti_sc(p_):
                if f not in SC["fonti"] or SC["fonti"][f]["http"] != 200:
                    errori.append(f"scooter {p_['slug']}: fonte {f} non letta con HTTP 200")
            for k, v in list(p_["casi"].items()) + list(p_["patenti"].items()):
                if v["esito"] not in ESITI_SC or (v["esito"] != "non_detto" and not v["cit"]) or any(i not in ids for i in v["cit"]):
                    errori.append(f"scooter {p_['slug']}: voce {k} non valida")
            if set(p_["casi"]) != {k for k, _ in CASI_SC} or set(p_["patenti"]) != {k for k, _ in PATENTI_SC}:
                errori.append(f"scooter {p_['slug']}: casi o patenti mancanti")
            if len(p_["titolo"]) > LIMITE_TITOLO_SC or str(ANNO) not in p_["titolo"]:
                errori.append(f"scooter {p_['slug']}: titolo oltre {LIMITE_TITOLO_SC} caratteri o senza l'anno")
    if FL:  # patente straniera in Canada, Australia e NZ: fonti con HTTP 200, citazioni note, titoli (verifica.py, punto 23, ricontrolla tutto)
        ids_tutti = [c["id"] for g in FL_GIUR for c in g["citazioni"]]
        if len(set(ids_tutti)) != len(ids_tutti):
            errori.append("patente straniera: id di citazione duplicati")
        for g in FL_GIUR:
            if g["paese"] not in FL_PAESI or g["tipo"] not in FL_TIPO:
                errori.append(f"patente straniera {g['id']}: paese o tipo non validi")
            if not g["letta"]:
                if g.get("bloccata") not in FL["bloccate"] or g["citazioni"]:
                    errori.append(f"patente straniera {g['id']}: non letta senza pagina bloccata registrata, o con citazioni")
                continue
            ids = {c["id"] for c in g["citazioni"]}
            for f in fonti_fl(g):
                if f not in FL["fonti"] or FL["fonti"][f]["http"] != 200:
                    errori.append(f"patente straniera {g['id']}: fonte {f} non letta con HTTP 200")
            for k in ("visitatori", "residenti", "idp", "uk_breve", "us_breve", "risposta", "chi"):
                if not g.get(k):
                    errori.append(f"patente straniera {g['id']}: manca {k}")
            if g["uk"] not in SCAMBIO_FL or g["us"] not in SCAMBIO_FL or g["uk_cit"] not in ids or g["us_cit"] not in ids:
                errori.append(f"patente straniera {g['id']}: scambio UK/US non valido o senza citazione")
            for q in g["faq"]:
                if any(i not in ids for i in q["cit"]):
                    errori.append(f"patente straniera {g['id']}: FAQ «{q['q']}» con citazione sconosciuta")
            if g.get("fonte_non_letta") and g["fonte_non_letta"] not in FL["bloccate"]:
                errori.append(f"patente straniera {g['id']}: fonte non letta non registrata")
            if len(scegli(titoli_fl(g), LIMITE_TITOLO_FL)) > LIMITE_TITOLO_FL:
                errori.append(f"patente straniera {g['id']}: titolo oltre {LIMITE_TITOLO_FL} caratteri")
        if NOLEGGIO_AUTO:
            errori += [f"patente straniera: {e}" for e in MON.controlla_link_pagina(box_noleggio_fl(), "box_noleggio_fl", "en")[0]]
    if TR:  # trasporto pubblico per città: fonti con HTTP 200, citazioni e FAQ coerenti, titoli (verifica.py, punto 24, ricontrolla tutto)
        ids_tutti = [x["id"] for c in TR_CITTA for x in c.get("citazioni", [])]
        if len(set(ids_tutti)) != len(ids_tutti):
            errori.append("trasporti: id di citazione duplicati")
        if len({c["slug"] for c in TR_CITTA}) != len(TR_CITTA):
            errori.append("trasporti: slug duplicati")
        for c in TR_CITTA:
            if c["iso2"] not in PAESI_ISO:
                errori.append(f"trasporti {c['id']}: codice Paese non in paesi_iso.json")
            if not c["letta"]:
                if c.get("citazioni") or not c.get("motivo") or not c.get("url_provato") or c["id"] not in (TR.get("non_lette") or {}):
                    errori.append(f"trasporti {c['id']}: non letta con citazioni, senza motivo o senza la prova registrata")
                continue
            ids = {x["id"] for x in c["citazioni"]}
            for f in fonti_tr(c):
                if f not in TR["fonti"] or TR["fonti"][f]["http"] != 200:
                    errori.append(f"trasporti {c['id']}: fonte {f} non letta con HTTP 200")
                elif TR["fonti"][f]["lingua"] != "en":
                    errori += [f"trasporti {c['id']}: citazione {x['id']} senza traduzione" for x in c["citazioni"] if x["f"] == f and not x.get("tr")]
            for k in ("chi", "rete", "multa", "contactless_breve", "convalida_breve", "pagamento", "risposta"):
                if not c.get(k):
                    errori.append(f"trasporti {c['id']}: manca {k}")
            if c["contactless"] not in CONTACTLESS_TR or c["convalida"] not in CONVALIDA_TR:
                errori.append(f"trasporti {c['id']}: contactless o convalida non validi")
            if not any(x["tema"] == "multa" for x in c["citazioni"]):
                errori.append(f"trasporti {c['id']}: pagina senza una citazione sulla multa")
            if c.get("cambio") and (c["cambio"]["cit"] not in ids or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", c["cambio"]["data"])):
                errori.append(f"trasporti {c['id']}: cambio senza citazione o data")
            for q in c["faq"]:
                if not q["cit"] or any(i not in ids for i in q["cit"]):
                    errori.append(f"trasporti {c['id']}: FAQ «{q['q']}» senza citazioni o con citazione sconosciuta")
            if len(scegli(titoli_tr(c), LIMITE_TITOLO_TR)) > LIMITE_TITOLO_TR:
                errori.append(f"trasporti {c['id']}: titolo oltre {LIMITE_TITOLO_TR} caratteri")
    if TB:  # bagagli sui treni e orari Eurostar: fonti con HTTP 200, citazioni e FAQ coerenti, titoli (verifica.py, punto 25, ricontrolla tutto)
        tutte = [x for c in TB_COMP for x in c.get("citazioni", [])] + (TB_EUR["citazioni"] if TB_EUR else [])
        if len({x["id"] for x in tutte}) != len(tutte):
            errori.append("bagagli treni: id di citazione duplicati")
        if len({c["slug"] for c in TB_COMP}) != len(TB_COMP) or len({c["id"] for c in TB_COMP}) != len(TB_COMP):
            errori.append("bagagli treni: slug o id duplicati")
        for x in tutte:
            F = TB["fonti"].get(x["f"])
            if not F or F["http"] != 200:
                errori.append(f"bagagli treni: citazione {x['id']} da una fonte non letta con HTTP 200")
            elif F["lingua"] != "en" and not x.get("tr"):
                errori.append(f"bagagli treni: citazione {x['id']} senza traduzione")
            if x["tema"] not in {k for k, _ in TEMI_TB} | {"arrivo", "continente", "ees", "kiosk"}:
                errori.append(f"bagagli treni: citazione {x['id']} con tema sconosciuto")
        for c in TB_COMP:
            if not c["letta"]:
                if c.get("citazioni") or c.get("numero") or not c.get("motivo") or not c.get("url_provato") or c["id"] not in (TB.get("non_lette") or {}):
                    errori.append(f"bagagli treni {c['id']}: non letta con dati, senza motivo o senza la prova registrata")
                continue
            ids = {x["id"] for x in c["citazioni"]}
            for k in ("chi", "nome_titolo", "treni", "numero", "misure", "peso", "extra", "speciali", "risposta"):
                if not c.get(k):
                    errori.append(f"bagagli treni {c['id']}: manca {k}")
            if not any(x["tema"] == "numero" for x in c["citazioni"]) or not any(x["tema"] == "misure" for x in c["citazioni"]):
                errori.append(f"bagagli treni {c['id']}: mancano citazioni sul numero o sulle misure")
            for q in c["faq"]:
                if not q["cit"] or any(i not in ids for i in q["cit"]):
                    errori.append(f"bagagli treni {c['id']}: FAQ «{q['q']}» senza citazioni o con citazione sconosciuta")
            if len(scegli(titoli_tb(c), LIMITE_TITOLO_TB)) > LIMITE_TITOLO_TB:
                errori.append(f"bagagli treni {c['id']}: titolo oltre {LIMITE_TITOLO_TB} caratteri")
        if TB_EUR:
            if TB_EUR["fonte_tabella"] not in TB["fonti"] or TB["fonti"][TB_EUR["fonte_tabella"]]["http"] != 200:
                errori.append("Eurostar: tabella degli orari non letta con HTTP 200")
            for s in TB_EUR["stazioni"]:
                if s["chiusura_tipo"] not in ("gate", "checks") or any(not re.fullmatch(r"\d+(?:-\d+)?", v) for v in [*s["arrivo"].values(), *s["chiusura"].values()]):
                    errori.append(f"Eurostar {s['id']}: orari o tipo di chiusura non validi")
            ids_es = {x["id"] for x in TB_EUR["citazioni"]}
            for f in TB_EUR["faq"]:
                if not (f.get("stazione") in {s["id"] for s in TB_EUR["stazioni"]} or (f.get("cit") and all(i in ids_es for i in f["cit"]))):
                    errori.append(f"Eurostar: FAQ «{f['q']}» senza stazione o citazioni note")
            if len(scegli(titolo_es(), LIMITE_TITOLO_TB)) > LIMITE_TITOLO_TB:
                errori.append("Eurostar: titolo oltre il limite")
    if BB:  # Blue Badge all'estero: fonti con HTTP 200, citazioni note e tradotte, esiti, FAQ, titoli (verifica.py, punto 28, ricontrolla tutto)
        if len(BB_CIT) != len(BB["citazioni"]):
            errori.append("blue badge: id di citazione duplicati")
        if len({p["slug"] for p in BB_PAESI}) != len(BB_PAESI) or len({p["iso2"] for p in BB_PAESI}) != len(BB_PAESI):
            errori.append("blue badge: slug o codici duplicati")
        for x in BB["citazioni"]:
            F = BB["fonti"].get(x["f"])
            if not F or F["http"] != 200 or not F.get("impronta"):
                errori.append(f"blue badge: citazione {x['id']} da una fonte non letta con HTTP 200 o senza impronta")
            elif F["lingua"] != "en" and not x.get("tr"):
                errori.append(f"blue badge: citazione {x['id']} senza traduzione")
        if any(F["http"] != 200 for F in BB["fonti"].values()):
            errori.append("blue badge: fonte non letta con HTTP 200")
        for p in BB_PAESI:
            if p["esito"] not in ESITI_BB or p["iso2"] not in PAESI_ISO:
                errori.append(f"blue badge {p['iso2']}: esito o codice Paese non validi")
            if not p["pagina"]:
                continue
            for q in p["faq"]:
                if not q["cit"] or any(i not in BB_CIT for i in q["cit"]) or not q.get("query"):
                    errori.append(f"blue badge {p['iso2']}: FAQ «{q['q']}» senza citazioni note o senza ricerca")
                if any(BB["fonti"][BB_CIT[i]["f"]]["lingua"] != "en" for i in q["cit"]) and "our translation" not in q["pre"]:
                    errori.append(f"blue badge {p['iso2']}: FAQ «{q['q']}» con citazione tradotta senza dirlo")
                testo_faq = faq_bb([q])[0][1]
                for i in q["cit"]:
                    if BB_CIT[i].get("tr") and (BB_CIT[i]["tr"] not in testo_faq or BB_CIT[i]["x"] in testo_faq):
                        errori.append(f"blue badge {p['iso2']}: FAQ «{q['q']}» senza la traduzione di {i} (o con il testo originale)")
            if len(scegli(titoli_bb(p), LIMITE_TITOLO_BB)) > LIMITE_TITOLO_BB or str(ANNO) not in scegli(titoli_bb(p), LIMITE_TITOLO_BB):
                errori.append(f"blue badge {p['iso2']}: titolo oltre {LIMITE_TITOLO_BB} caratteri o senza l'anno")
            if any(i not in BB_CIT for i in ids_pagina_bb(p)):
                errori.append(f"blue badge {p['iso2']}: citazione sconosciuta nella pagina")
        for q in BB["faq_indice"] + BB["faq_carte"]:
            if not q["cit"] or any(i not in BB_CIT for i in q["cit"]):
                errori.append(f"blue badge: FAQ «{q['q']}» senza citazioni note")
    errori += controlli_in()
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
    if PED:
        pagina_indice_ped()
        for p in PED_PAESI:
            pagina_ped(p)
    if GOM:
        pagina_indice_gom()
        for p in GOM_PAESI:
            if ha_pagina_gom(p["iso2"]):
                pagina_gom(p)
    if BIG:
        pagina_indice_big()
        for a in BIG_ATT:
            pagina_big(a)
        scrivi_ics_big()
    if FL:
        pagina_indice_fl()
        for g in FL_LETTE:
            pagina_fl(g)
    if TR:
        pagina_indice_tr()
        for c in TR_LETTE:
            pagina_tr(c)
    if TB:
        pagina_indice_tb()
        for c in TB_LETTE:
            pagina_tb(c)
        if TB_EUR:
            pagina_es()
    if PET:
        pagina_indice_pet()
        pagina_calcolatore_pet()
        pagina_passaporto_pet()
        pagina_rotte_pet()
        for p in PET_PAGINE:
            pagina_paese_pet(p)
    if BB:
        pagina_indice_bb()
        pagina_carte_bb()
        for p in BB_PAGINE:
            pagina_paese_bb(p)
    if SC:
        pagina_indice_sc()
        for p in SC_PAESI:
            pagina_sc(p)
    if IN:
        pagina_indice_in()
        for g in IN_PAGINE:
            pagina_in(g)
        pagina_voa_in()
        pagina_arr_in()
        pagina_lingua_in("de")
        pagina_lingua_in("fr")
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
             f"({', '.join(f'{k} {len(PAGINE_PAT[k])}' for k in PATENTI)})" if PAT else "")
          + (f"; tolls with a rental car: indice + {len(PED_PAESI)} pagine Paese ({len(PED['fonti'])} fonti)" if PED else "")
          + (f"; winter tyres with a rental car: indice + {len(GOM_PAGINE & set(GOM_PER))} pagine Paese ({len(GOM['fonti'])} fonti)" if GOM else "")
          + (f"; ticket release dates: indice + {len(BIG_ATT)} pagine attrazione + {len(BIG_ATT)} calendari .ics ({len(BIG['fonti'])} fonti)" if BIG else "")
          + (f"; foreign licence Canada/Australia/NZ: indice + {len(FL_LETTE)} pagine ({len(FL_GIUR) - len(FL_LETTE)} giurisdizioni non lette, {len(FL['fonti'])} fonti)" if FL else "")
          + (f"; public transport rules: indice + {len(TR_LETTE)} pagine città ({len(TR_CITTA) - len(TR_LETTE)} città non lette, {len(TR['fonti'])} fonti)" if TR else "")
          + (f"; train luggage rules: indice + {len(TB_LETTE)} pagine compagnia ({len(TB_COMP) - len(TB_LETTE)} non lette, {len(TB['fonti'])} fonti)"
             + (f" + Eurostar check-in ({len(TB_EUR['stazioni'])} stazioni)" if TB_EUR else "") if TB else "")
          + (f"; pets UK to EU: indice + calcolatore + passaporto 2027 + rotte approvate ({len(PET['rotte']['aria'])} compagnie aeree, {PET['rotte']['charter']} charter contati) + {len(PET_PAGINE)} pagine Paese "
             f"({len(PET['fonti'])} fonti)" if PET else "")
          + (f"; India e-Visa: indice ({len(IN_PAESI)} Paesi) + {len(IN_PAGINE)} pagine per nazionalità + visto all'arrivo + e-Arrival card + pagine in tedesco e francese "
             f"({len(IN['fonti'])} fonti)" if IN else "")
          + (f"; blue badge abroad: indice + carte europee + {len(BB_PAGINE)} pagine Paese ({len(BB['fonti'])} fonti)" if BB else ""))


if __name__ == "__main__":
    main()
