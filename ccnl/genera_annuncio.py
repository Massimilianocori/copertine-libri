"""Paga CCNL per chi assume: prova di domanda del 27/11/2026 (studio-business/schede/2026-11-27-pagaccnl-annuncio.md).

Quattro pagine, scritte da genera.py (che passa se stesso come G):
    /annuncio-di-lavoro/                 strumento gratuito: la riga di retribuzione per l'annuncio, da contratto e livello
    /annuncio-di-lavoro/cosa-scrivere/   guida all'art. 5 del D.Lgs. 96/2026, con il testo citato parola per parola
    /per-consulenti-e-aziende/           «Paga CCNL Pro»: prezzi veri, NESSUNA VENDITA, modulo Netlify «pro» (lista d'attesa)
    /api/                                esempio JSON vero e modulo Netlify «api» (chiave di prova); nessun servizio in funzione
più il riquadro «Devi scrivere la paga nell'annuncio?» nelle pagine livello, contratto e home (riquadro()).

Regole: nessun pagamento e nessun link a un sistema di pagamento; ogni cifra viene dagli stessi dati delle pagine livello
(G.valori, G.prorata, G.orario52); i testi di legge sono i frammenti di dati/annuncio.json, mai riscritti a mano;
nessun importo di sanzione. Il calcolo del browser (JS_STRUMENTO) usa window.PagaCCNL di stile.APP_JS; verifica.py lo
esegue con node per tutti i livelli e lo confronta con un ricalcolo fatto da dati/estratti.json.

Misura (GoatCounter, eventi): clic/annuncio-calcolo (riga creata), clic/annuncio-copia (riga copiata), clic/pro-prezzo
(pulsanti «Mi interessa»), clic/api-chiave (pulsante «Chiedi una chiave di prova»). Moduli Netlify: «pro» e «api».
"""
import json
from datetime import date
from pathlib import Path

DATI = Path(__file__).resolve().parent / "dati"
A = json.loads((DATI / "annuncio.json").read_text(encoding="utf-8"))
LEGGE = A["legge"]
FR = LEGGE["frammenti"]
EV = A["eventi"]
PREZZI = A["prezzi"]

P_STRUMENTO = "annuncio-di-lavoro/"
P_GUIDA = "annuncio-di-lavoro/cosa-scrivere/"
P_PRO = "per-consulenti-e-aziende/"
P_API = "api/"
FILE_API = "api/esempio.json"
AGGIORNATO = date.fromisoformat(A["aggiornato_il"])  # data delle 4 pagine nuove e dell'ultimo aggiornamento della privacy
CONSULENTE = "verifica con il tuo consulente"  # frase fissa della scheda: sta nello strumento, nella guida e nelle pagine Pro e API


# ---------------------------------------------------------------- dati dello strumento (gli stessi delle pagine livello)
def _stato(G, cid, L):
    """Cifre del livello nel giorno G.OGGI, oppure None se quel giorno la pagina del livello non mostra un minimo in vigore
    (riga sospesa «Cifra da aggiornare», tabella del lavoro domestico dell'anno prima, livello senza cifra pubblicabile)."""
    cur = G.stato_livello(cid, L)[0]
    if not (cur and cur["pubblicabile"]):
        return None
    if cid == "domestico" and G.domestico_vecchio():
        return None
    v = G.valori(cid, L)
    if v["sospese"]:
        return None
    if cid == "domestico":
        return {"m": G.cent(v["conv_tot"]), "o": G.cent(v["oraria"]), "ind": 1 if v["ind"] else 0, "t": G.data_lunga(v["dal"])}
    return {"m": G.cent(v["mensile"]), "t": G.data_lunga(v["dal"])}


def _passi(G, cid, L):
    """Stato di oggi e di ogni data futura già scritta nei dati: il browser sceglie il passo del giorno (ora di Roma), così la
    riga non resta su una cifra superata se il sito non viene rigenerato il giorno dello scatto."""
    oggi = G.OGGI.isoformat()
    giorni = sorted({t["dal"] for t in G.tranche_livello(cid, L["id"]) if t["dal"] > oggi})
    if cid == "domestico":
        giorni = sorted(set(giorni) | {date(G.OGGI.year + 1, 1, 1).isoformat()})
    passi = []
    for g in [""] + giorni:
        s = _stato(G, cid, L) if not g else G.al_giorno(g, _stato, G, cid, L)
        p = dict(s, dal=g) if s else {"dal": g, "no": 1}
        if passi and {k: x for k, x in passi[-1].items() if k != "dal"} == {k: x for k, x in p.items() if k != "dal"}:
            continue
        passi.append(p)
    return passi


def dati_strumento(G):
    c = {}
    for cid in G.ORDINE:
        m = G.C[cid]
        c[cid] = {"n": m["nome"], "b": m["nome_breve"], "k": m["codice_cnel"], "s": m["slug"], "mens": m["mensilita"]["valore"],
                  "ore": 40 if cid == "domestico" else m["ore"]["valore"], "dom": 1 if cid == "domestico" else 0, "f": A["fonte_breve"][cid],
                  "l": [{"id": L["id"], "n": L["nome"], "s": L["slug"], "g": L.get("gruppo_nome", ""), "p": _passi(G, cid, L)}
                        for L in G.livelli_pubblicati(cid)]}
    return {"ctrl": G.data_lunga(G.CONTROLLO), "ordine": list(G.ORDINE), "c": c}


def riga(G, D, cid, lid, modo="pieno", n=0, oggi=None, off=0):
    """La riga per l'annuncio, in Python: stesso testo e stesse formule di JS_STRUMENTO (verifica.py confronta i due e li
    rifà da dati/estratti.json). modo: pieno | ore | pct (contratti con divisore); conv | aore (lavoro domestico).
    off: retribuzione mensile offerta in centesimi, se più alta del minimo (solo contratti con divisore): la riga dà la fascia.
    Ritorna testo (riga completa, per il fascicolo) e breve (le prime due frasi, per l'annuncio)."""
    oggi = oggi or G.OGGI.isoformat()
    c = D["c"][cid]
    L = next(x for x in c["l"] if x["id"] == lid)
    p = [x for x in L["p"] if not x["dal"] or oggi >= x["dal"]][-1]
    if p.get("no"):
        return None
    e = lambda x: G.euro(G.da_cent(x))  # noqa: E731
    dopo = ""
    if c["dom"]:
        if modo == "aore":
            m = G.cent(G.orario52(G.da_cent(p["o"]), n))
            testa = (f"{e(p['o'])} lordi l'ora; per {n} ore settimanali {e(m)} lordi al mese per {c['mens']} mensilità "
                     f"({e(m * c['mens'])} lordi l'anno), lavoratore non convivente.")
        else:
            m = p["m"]
            testa = f"{e(m)} lordi al mese per {c['mens']} mensilità ({e(m * c['mens'])} lordi l'anno), lavoratore convivente; vitto e alloggio a parte."
            if p["ind"]:
                dopo = ", indennità di funzione compresa"
    else:
        if modo == "ore":
            m, coda = G.cent(G.prorata(G.da_cent(p["m"]), n, c["ore"])), f"part time di {n} ore settimanali su {c['ore']}"
        elif modo == "pct":
            m, coda = G.cent(G.prorata(G.da_cent(p["m"]), n, 100)), f"part time al {n}%"
        else:
            m, coda = p["m"], f"tempo pieno ({c['ore']} ore settimanali)"
        if modo in ("ore", "pct"):
            dopo = ", riproporzionato all'orario"
        if off and off > m:
            testa = f"da {e(m)} a {e(off)} lordi al mese per {c['mens']} mensilità (da {e(m * c['mens'])} a {e(off * c['mens'])} lordi l'anno), {coda}."
        else:
            off = 0
            testa = f"{e(m)} lordi al mese per {c['mens']} mensilità ({e(m * c['mens'])} lordi l'anno), {coda}."
    nome = L["n"][0].lower() + L["n"][1:]
    breve = f"Retribuzione iniziale: {testa} Inquadramento: {nome}, CCNL {c['n']}, codice CNEL {c['k']}."
    importo = (f"fascia dal minimo del contratto in vigore dal {p['t']}{dopo} alla retribuzione offerta dall'azienda" if off
               else f"minimo del contratto in vigore dal {p['t']}{dopo}")
    testo = f"{breve} Importo: {importo}. Fonte: {c['f']}; cifre controllate il {D['ctrl']}."
    return {"testo": testo, "breve": breve, "mensile": m, "annuo": m * c["mens"]}


# Il calcolo usa window.PagaCCNL (stile.APP_JS: interi in centesimi, mezzo verso l'alto). Le funzioni riga() e centesimi() sono pure:
# verifica.py le chiama con node per ogni livello. Gli eventi partono solo quando la riga è stata creata o copiata davvero.
JS_STRUMENTO = r"""
(function(){
'use strict';
function P(){return window.PagaCCNL;}
function trova(D,cid,lid){var c=D.c[cid];if(!c)return null;for(var i=0;i<c.l.length;i++){if(c.l[i].id===lid)return {c:c,L:c.l[i]};}return null;}
function passo(L,oggi){var p=null;L.p.forEach(function(x){if(!x.dal||oggi>=x.dal)p=x;});return p;}
function intero(v){var s=String(v==null?'':v).trim();return /^\d+$/.test(s)?parseInt(s,10):NaN;}
// «2.000,50», «2000,5», «2000.50», «2000» -> centesimi; '' -> 0; scritto male -> NaN
function centesimi(v){var s=String(v==null?'':v).replace(/[\s€]/g,'');if(!s)return 0;
  if(s.indexOf(',')>=0)s=s.replace(/\./g,'').replace(',','.');else if(/^\d{1,3}(\.\d{3})+$/.test(s))s=s.replace(/\./g,'');
  if(!/^\d+(\.\d{1,2})?$/.test(s))return NaN;var k=s.split('.');return parseInt(k[0],10)*100+(k[1]?parseInt((k[1]+'0').slice(0,2),10):0);}
function riga(D,cid,lid,o,oggi){
  var r=trova(D,cid,lid);if(!r)return null;var c=r.c,L=r.L,p=passo(L,oggi);
  if(!p||p.no)return {no:true};
  var e=P().eur,n=intero(o.n),off=o.off||0,m,testa,coda,dopo='';
  if(off!==off||off<0)return null;
  if(c.dom){
    if(off)return null;
    if(o.modo==='aore'){if(!(n>=1&&n<=40))return null;m=P().orario52(p.o,n);
      testa=e(p.o)+" lordi l'ora; per "+n+' ore settimanali '+e(m)+' lordi al mese per '+c.mens+' mensilità ('+e(m*c.mens)+" lordi l'anno), lavoratore non convivente.";}
    else{m=p.m;testa=e(m)+' lordi al mese per '+c.mens+' mensilità ('+e(m*c.mens)+" lordi l'anno), lavoratore convivente; vitto e alloggio a parte.";if(p.ind)dopo=', indennità di funzione compresa';}
  }else{
    if(o.modo==='ore'){if(!(n>=1&&n<c.ore))return null;m=P().prorata(p.m,n,c.ore);coda='part time di '+n+' ore settimanali su '+c.ore;}
    else if(o.modo==='pct'){if(!(n>=1&&n<=99))return null;m=P().prorata(p.m,n,100);coda='part time al '+n+'%';}
    else{m=p.m;coda='tempo pieno ('+c.ore+' ore settimanali)';}
    if(o.modo==='ore'||o.modo==='pct')dopo=", riproporzionato all'orario";
    if(off&&off<m)return {basso:true,mensile:m};
    if(off===m)off=0;
    if(off)testa='da '+e(m)+' a '+e(off)+' lordi al mese per '+c.mens+' mensilità (da '+e(m*c.mens)+' a '+e(off*c.mens)+" lordi l'anno), "+coda+'.';
    else testa=e(m)+' lordi al mese per '+c.mens+' mensilità ('+e(m*c.mens)+" lordi l'anno), "+coda+'.';
  }
  var breve='Retribuzione iniziale: '+testa+' Inquadramento: '+L.n.charAt(0).toLowerCase()+L.n.slice(1)+', CCNL '+c.n+', codice CNEL '+c.k+'.';
  var imp=off?'fascia dal minimo del contratto in vigore dal '+p.t+dopo+" alla retribuzione offerta dall'azienda":'minimo del contratto in vigore dal '+p.t+dopo;
  return {testo:breve+' Importo: '+imp+'. Fonte: '+c.f+'; cifre controllate il '+D.ctrl+'.',breve:breve,mensile:m,annuo:m*c.mens};
}
window.PagaAnnuncio={riga:riga,centesimi:centesimi};
function oggiRoma(){var g='';try{g=new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/Rome',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());}catch(x){}
  if(!/^\d{4}-\d{2}-\d{2}$/.test(g)){var d=new Date();g=d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2);}return g;}
function conta(p,t){try{if(window.goatcounter&&window.goatcounter.count)window.goatcounter.count({path:p,title:t,event:true});}catch(x){}}
function avvia(){
  var box=document.querySelector('[data-annuncio]'),dati=document.getElementById('annuncio-dati');if(!box||!dati)return;
  var D=JSON.parse(dati.textContent),oggi=oggiRoma();
  function q(s){return box.querySelector(s);}
  var sc=q('[name=contratto]'),sl=q('[name=livello]'),so=q('[name=orario]'),inN=q('[name=quanto]'),labN=q('[data-quanto]'),etN=q('[data-quanto-et]'),mens=q('[data-mens]'),
      inO=q('[name=offerta]'),labO=q('[data-offerta]');
  var vuoto=q('[data-attesa]'),esito=q('[data-esito]'),no=q('[data-no]'),err=q('[data-err]'),out=q('[data-riga]'),outB=q('[data-riga-breve]'),oM=q('[data-out-mese]'),oA=q('[data-out-anno]'),
      lk=q('[data-pagina-livello]'),lkNo=q('[data-pagina-no]'),ndom=q('[data-nota-dom]');
  function opt(v,t){var o=document.createElement('option');o.value=v;o.textContent=t;return o;}
  function livelli(sel){var c=D.c[sc.value];sl.textContent='';var gr={};
    c.l.forEach(function(L){var dove=sl;if(L.g){if(!gr[L.g]){gr[L.g]=document.createElement('optgroup');gr[L.g].label=L.g;sl.appendChild(gr[L.g]);}dove=gr[L.g];}dove.appendChild(opt(L.id,L.n));});
    if(sel&&trova(D,sc.value,sel))sl.value=sel;}
  function orari(){var c=D.c[sc.value];so.textContent='';
    if(c.dom){so.appendChild(opt('conv','Convivente (mensile)'));so.appendChild(opt('aore','Non convivente, a ore'));}
    else{so.appendChild(opt('pieno','Tempo pieno ('+c.ore+' ore a settimana)'));so.appendChild(opt('ore','Part time: ore a settimana'));so.appendChild(opt('pct','Part time: percentuale'));}
    labO.hidden=!!c.dom;if(c.dom)inO.value='';
    mens.textContent=c.mens+' mensilità, come dice il contratto';campo();}
  function campo(){var c=D.c[sc.value],m=so.value;labN.hidden=(m==='pieno'||m==='conv');
    if(m==='ore'){etN.textContent='Ore a settimana (da 1 a '+(c.ore-1)+')';inN.min=1;inN.max=c.ore-1;inN.value=24;}
    if(m==='pct'){etN.textContent='Percentuale del tempo pieno (da 1 a 99)';inN.min=1;inN.max=99;inN.value=50;}
    if(m==='aore'){etN.textContent='Ore a settimana (da 1 a 40)';inN.min=1;inN.max=40;inN.value=20;}}
  function alto(t){t.style.height='auto';t.style.height=(t.scrollHeight+4)+'px';}
  function azzera(){esito.hidden=true;no.hidden=true;err.hidden=true;vuoto.hidden=false;box.querySelectorAll('[data-copiato]').forEach(function(x){x.hidden=true;});}
  function sbaglio(t){err.hidden=false;err.textContent=t;}
  function crea(){var t=trova(D,sc.value,sl.value),off=t.c.dom?0:centesimi(inO.value);azzera();
    var url='/'+t.c.s+'/'+t.L.s+'/';
    // il campo numerico dà '' quando il valore non è un numero: si legge anche validity per dire «numero intero»
    var grezzo=(inN.validity&&inN.validity.badInput)?'x':inN.value;
    if(off!==off){sbaglio('Scrivi la retribuzione offerta in euro al mese, per esempio 2.000 oppure 2.000,50.');return;}
    var r=riga(D,sc.value,sl.value,{modo:so.value,n:grezzo,off:off},oggi);
    if(!r){sbaglio('Scrivi un numero intero tra '+inN.min+' e '+inN.max+'.');return;}
    if(r.basso){sbaglio('La retribuzione offerta non può essere più bassa del minimo del contratto ('+P().eur(r.mensile)+' al mese per questo orario).');return;}
    vuoto.hidden=true;
    if(r.no){no.hidden=false;lkNo.setAttribute('href',url);return;}
    out.value=r.testo;outB.value=r.breve;oM.textContent=P().eur(r.mensile);oA.textContent=P().eur(r.annuo);lk.setAttribute('href',url);ndom.hidden=!t.c.dom;esito.hidden=false;alto(out);alto(outB);
    conta(box.getAttribute('data-ev-calcolo'),'Riga per l\'annuncio creata');}
  function copia(b){var campo_=q(b.getAttribute('data-copia')==='breve'?'[data-riga-breve]':'[data-riga]'),segno=b.parentNode.querySelector('[data-copiato]'),t=campo_.value;if(!t)return;
    function fatto(){segno.hidden=false;conta(box.getAttribute('data-ev-copia'),'Riga per l\'annuncio copiata');}
    function vecchio(){campo_.focus();campo_.select();try{if(document.execCommand('copy'))fatto();}catch(x){}}
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(fatto,vecchio);}else{vecchio();}}
  var par={};try{location.search.replace(/^\?/,'').split('&').forEach(function(x){var k=x.split('=');if(k[0])par[k[0]]=decodeURIComponent(k[1]||'');});}catch(x){}
  if(par.c&&D.c[par.c])sc.value=par.c;
  livelli(par.l||sl.getAttribute('data-predef'));orari();
  sc.addEventListener('change',function(){livelli();orari();azzera();});
  sl.addEventListener('change',azzera);so.addEventListener('change',function(){campo();azzera();});inN.addEventListener('input',azzera);inO.addEventListener('input',azzera);
  q('[data-crea]').addEventListener('click',crea);box.querySelectorAll('[data-copia]').forEach(function(b){b.addEventListener('click',function(){copia(b);});});
  q('[data-crea]').disabled=false;
}
if(typeof document.addEventListener==='function'){if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',avvia);else avvia();}
})();
"""

# Moduli della lista d'attesa: invio senza cambiare pagina, con il messaggio «non hai pagato niente». Senza JavaScript il
# modulo si invia nel modo normale di Netlify. I pulsanti «Mi interessa» scelgono anche il piano nel modulo.
JS_MODULI = ("(function(){document.querySelectorAll('[data-piano]').forEach(function(a){a.addEventListener('click',function(){"
             "var s=document.querySelector('select[name=piano]');if(s)s.value=a.getAttribute('data-piano');});});"
             "document.querySelectorAll('form[data-lista]').forEach(function(f){f.addEventListener('submit',function(e){"
             "if(!window.fetch||!window.URLSearchParams||!window.FormData)return;e.preventDefault();"
             "var ok=document.getElementById(f.getAttribute('data-lista')),er=f.querySelector('[data-errore]'),b=f.querySelector('button[type=submit]');"
             "b.disabled=true;er.hidden=true;fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},"
             "body:new URLSearchParams(new FormData(f)).toString()}).then(function(r){if(!r.ok)throw 0;f.hidden=true;ok.hidden=false;ok.focus();})"
             ".catch(function(){b.disabled=false;er.hidden=false;});});});})();")


# ---------------------------------------------------------------- pezzi comuni
def riquadro(G, cid=None, L=None):
    """Riquadro «Devi scrivere la paga nell'annuncio?» per pagine livello, pagine contratto e home. Sta tra due commenti
    (<!--annuncio--> … <!--/annuncio-->): non tocca tabelle e cifre, e resta riconoscibile per chi conta le modifiche della pagina."""
    href = f"/{P_STRUMENTO}" + (f"?c={cid}" + (f"&amp;l={L['id']}" if L else "") if cid else "")
    if cid == "domestico":
        testo = ("Per il lavoro domestico l'obbligo del D.Lgs. 96/2026 non vale (art. 2, comma 2), ma dire subito la paga aiuta chi cerca una colf o una badante. "
                 f'<a href="{href}">Crea la riga pronta</a>, gratis, con il contratto, la fonte e la data della tabella.')
    else:
        cosa = f"Crea la riga pronta per il {G.h(L['nome'][0].lower() + L['nome'][1:])}" if L else "Crea la riga pronta"
        testo = ("Dal 7 giugno 2026 negli annunci di lavoro vanno date indicazioni sulla retribuzione iniziale o sulla fascia e sul contratto "
                 f'collettivo applicato (D.Lgs. 96/2026, art. 5). <a href="{href}">{cosa}</a>: gratis, con il contratto, la fonte e la data della tabella.')
    return (f'<!--annuncio--><aside class="nota info" aria-label="Annuncio di lavoro">{G.ico("doc")}'
            f"<p><strong>Devi scrivere la paga nell'annuncio?</strong> {testo}</p></aside><!--/annuncio-->")


def _cita(G, chiave, dove):
    """Citazione di legge: il testo è il frammento di dati/annuncio.json, senza ritocchi."""
    return f'<blockquote class="legge" data-frammento="{chiave}"><p>«{G.h(FR[chiave])}»</p><cite>{G.h(LEGGE["sigla"])}, {G.h(dove)}</cite></blockquote>'


def _esempio(G, D, etichetta, cid, lid, modo="pieno", n=0):
    """Una riga d'esempio presa dai dati. Se per quel livello è già nota una data in cui la cifra cambia, la pagina contiene anche la
    riga di quel giorno (nascosta fino ad allora, come nelle pagine livello) oppure, se quel giorno la cifra non è verificata, la toglie."""
    def blocco(r):
        return f'<p class="riga-es" data-esempio="{cid}/{lid}/{modo}/{n}"><small>{G.h(etichetta)}</small>{G.h(r["testo"])}</p>' if r else ""
    oggi = G.OGGI.isoformat()
    L = next(x for x in D["c"][cid]["l"] if x["id"] == lid)
    ora = blocco(riga(G, D, cid, lid, modo, n, oggi))
    dopo = [p["dal"] for p in L["p"] if p["dal"] > oggi]
    if not ora or not dopo:
        return ora
    g = dopo[0]
    return G.fino_al(g, ora) + G.dal_giorno(g, blocco(riga(G, D, cid, lid, modo, n, g)))


def _fonti_legge(G):
    voci = "".join(f'<li><a href="{G.h(f["url"])}" rel="noopener">{G.h(f["titolo"])}</a> · {G.h(f["chi"])}. '
                   f'<span class="small">Letto il {G.data_lunga(f["letto_il"])}.</span></li>' for f in LEGGE["fonti"])
    return (f'<section class="fonti-box" aria-labelledby="fonti-h"><h2 id="fonti-h">{G.ico("doc")}Fonti</h2><ol>{voci}</ol>'
            '<p class="small">Il testo di legge è copiato parola per parola dal testo vigente. Le cifre degli esempi vengono dalle tabelle dei contratti: '
            '<a href="/come-lavoriamo/">come le controlliamo</a>.</p></section>')


def _numeri(G):
    return sum(len(G.livelli_pubblicati(c)) for c in G.ORDINE)


def _elenco(G, D, campo, unita):
    """«14 per commercio e terziario, …; 13 per …»: mensilità o ore del tempo pieno, lette dai dati dei contratti."""
    gruppi = {}
    for cid in D["ordine"]:
        if campo == "ore" and D["c"][cid]["dom"]:
            continue
        gruppi.setdefault(D["c"][cid][campo], []).append(D["c"][cid]["b"].lower())
    return "; ".join(f"{k}{unita} per {', '.join(v)}" for k, v in sorted(gruppi.items(), reverse=True))


def _campo_hp():
    return '<p class="hp"><label>Lascia vuoto questo campo <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>'


def _opzioni(voci):
    return '<option value="">Scegli…</option>' + "".join(f"<option>{v}</option>" for v in voci)


# ---------------------------------------------------------------- 1. strumento
def strumento(G, D):
    n_liv = _numeri(G)
    pre_c, pre_l = "terziario", "iv"
    opz_c = "".join(f'<option value="{c}"{" selected" if c == pre_c else ""}>{G.h(D["c"][c]["b"])}</option>' for c in D["ordine"])
    opz_l = "".join(f'<option value="{x["id"]}"{" selected" if x["id"] == pre_l else ""}>{G.h(x["n"])}</option>' for x in D["c"][pre_c]["l"])
    c0 = D["c"][pre_c]
    box = f"""<section class="card calc pull" data-annuncio data-ev-calcolo="{EV['calcolo']}" data-ev-copia="{EV['copia']}" aria-labelledby="ann-h">
<div class="calc-h"><h2 id="ann-h">{G.ico("doc")}La riga per il tuo annuncio</h2><span class="pill">Gratis</span></div>
<div class="calc-g"><div class="calc-in">
<label>Contratto<select name="contratto">{opz_c}</select></label>
<label>Livello<select name="livello" data-predef="{pre_l}">{opz_l}</select></label>
<label>Orario<select name="orario"><option value="pieno">Tempo pieno ({c0['ore']} ore a settimana)</option><option value="ore">Part time: ore a settimana</option><option value="pct">Part time: percentuale</option></select></label>
<label data-quanto hidden><span data-quanto-et>Ore a settimana</span><input name="quanto" type="number" inputmode="numeric" min="1" max="39" step="1" value="24"></label>
<label data-offerta>Retribuzione offerta, se più alta del minimo (facoltativa, euro lordi al mese)<input name="offerta" type="text" inputmode="decimal" maxlength="12" autocomplete="off" placeholder="Per esempio 2.000"></label>
<p class="small" style="margin:0">Mensilità: <strong data-mens>{c0['mens']} mensilità, come dice il contratto</strong></p>
<button type="button" class="btn" data-crea disabled>Crea la riga</button>
<p class="small" data-err hidden style="margin:0;color:var(--warm-ink);font-weight:700"></p>
</div><div class="calc-out" aria-live="polite">
<p data-attesa style="margin:0">Scegli contratto, livello e orario, poi premi «Crea la riga». Il calcolo avviene nel tuo browser: non inviamo niente.</p>
<div data-no hidden><p style="margin:0"><strong>Per questo livello oggi non diamo la riga.</strong> La tabella in vigore non ha ancora passato i nostri due controlli e la cifra
verificata è superata: in un annuncio sarebbe sbagliata. I dettagli sono nella <a data-pagina-no href="/">pagina del livello</a>.</p></div>
<div data-esito hidden style="display:grid;gap:10px">
<div class="esito"><span>Retribuzione iniziale lorda al mese (minimo del contratto)</span><b data-out-mese>—</b></div>
<div class="esito sec"><span>Lorda in un anno, con le mensilità del contratto</span><b data-out-anno>—</b></div>
<label style="display:grid;gap:6px;font-weight:700;font-size:.92rem">Riga breve per l'annuncio<textarea class="riga-out breve" data-riga-breve readonly rows="4"></textarea></label>
<div class="riga-az"><button type="button" class="btn" data-copia="breve">Copia la riga breve</button><span class="small" data-copiato hidden style="color:var(--ok);font-weight:700">Copiato.</span></div>
<label style="display:grid;gap:6px;font-weight:700;font-size:.92rem">Riga completa per il fascicolo (con data della tabella e fonte)<textarea class="riga-out" data-riga readonly rows="7"></textarea></label>
<div class="riga-az"><button type="button" class="btn" data-copia="completa">Copia la riga completa</button><span class="small" data-copiato hidden style="color:var(--ok);font-weight:700">Copiato.</span>
<a data-pagina-livello href="/">Voci e fonti di questo livello</a></div>
<p class="small" data-nota-dom hidden style="margin:0">Il D.Lgs. 96/2026 esclude i contratti di lavoro domestico (art. 2, comma 2): per colf e badanti la riga è una scelta, non un obbligo.</p>
</div></div></div>
<p class="calc-f">È il minimo lordo del contratto nazionale: se offri di più, scrivi la retribuzione offerta e la riga diventa una fascia «da… a…». Prima di pubblicare, {CONSULENTE} del lavoro.</p>
<noscript><p class="calc-f">Lo strumento ha bisogno di JavaScript. Senza, trovi le stesse cifre nelle pagine dei livelli e gli esempi qui sotto.</p></noscript>
</section>
<script type="application/json" id="annuncio-dati">{json.dumps(D, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")}</script>
<script id="annuncio-js">{JS_STRUMENTO.strip()}</script>"""
    corpo = box
    corpo += '<h2 id="cosa">Cosa c\'è nella riga</h2><div class="testo">'
    corpo += ('<p>Lo strumento prende il minimo del contratto nazionale per il livello che scegli e scrive una frase pronta da incollare nell\'annuncio di lavoro. '
              'Le righe sono due: una breve per l\'annuncio, con retribuzione, orario, contratto e livello, e una completa da tenere nel fascicolo, che aggiunge la data della tabella e la fonte.</p><ol>'
              '<li><strong>La retribuzione iniziale</strong>: lordo al mese, numero di mensilità del contratto e lordo in un anno (mese × mensilità). Se scrivi anche la retribuzione che offri, diventa una fascia dal minimo alla tua cifra.</li>'
              '<li><strong>L\'orario</strong>: tempo pieno con le ore del contratto, oppure part time in ore a settimana o in percentuale.</li>'
              '<li><strong>Il contratto e il livello</strong>: nome del contratto collettivo nazionale, codice del CNEL e livello di inquadramento.</li>'
              '<li><strong>La fonte e la data</strong> (solo nella riga completa): da quali documenti viene la cifra, da quando è in vigore la tabella e quando l\'abbiamo controllata.</li></ol>'
              f'<p>Le cifre sono le stesse delle <a href="/">pagine dei livelli</a>: oggi {n_liv} livelli di 5 contratti, ognuno con due fonti indipendenti (testo depositato al CNEL, tabella del Ministero del Lavoro o tabelle delle parti firmatarie) uguali al centesimo. '
              'Se il contratto che applichi non è tra questi cinque, qui non lo trovi: non stimiamo cifre che non abbiamo verificato.</p></div>')
    corpo += '<h2 id="esempi">Esempi con le tabelle di oggi</h2>'
    corpo += ('<p>Sono righe complete prodotte dallo strumento con i dati del sito. Puoi copiarle e adattarle.</p>'
              + _esempio(G, D, "Commercio, 4° livello, tempo pieno", "terziario", "iv")
              + _esempio(G, D, "Metalmeccanici, livello C3, tempo pieno", "metalmeccanici", "c3")
              + _esempio(G, D, "Multiservizi, 2° livello, part time di 20 ore", "multiservizi", "2", "ore", 20))
    corpo += G.AD
    corpo += '<h2 id="calcolo">Come calcoliamo part time e totale annuo</h2><div class="testo"><ul>'
    corpo += (f'<li><strong>Part time in ore</strong>: minimo mensile × ore a settimana ÷ ore del tempo pieno del contratto ({_elenco(G, D, "ore", " ore")}). '
              'È lo stesso calcolo delle pagine dei livelli.</li>'
              '<li><strong>Part time in percentuale</strong>: minimo mensile × percentuale ÷ 100.</li>'
              f'<li><strong>Totale annuo</strong>: importo mensile × mensilità del contratto ({_elenco(G, D, "mens", "")}).</li>'
              '<li><strong>Colf e badanti a ore</strong>: paga oraria della tabella × ore a settimana × 52 ÷ 12, come scrive il contratto del lavoro domestico.</li>'
              '<li><strong>Arrotondamento</strong>: al centesimo, con il mezzo centesimo verso l\'alto.</li></ul></div>')
    corpo += '<h2 id="limiti">Cosa la riga non dice</h2><div class="testo"><ul>'
    corpo += ('<li>Non comprende superminimi, premi, indennità, buoni pasto e contratti aziendali o territoriali: se li offri, aggiungili tu.</li>'
              '<li>Non è il netto: sono importi lordi, prima di contributi e tasse.</li>'
              '<li>Non sceglie il livello al posto tuo: il livello dipende dalle mansioni della posizione, e ogni pagina livello riporta la descrizione del contratto.</li>'
              '<li>Non è un parere: la legge chiede «la retribuzione iniziale o la relativa fascia» e le «pertinenti disposizioni del contratto collettivo», '
              f'ma non dà un modello di frase. La nostra riga è un modo ordinato di scriverle; {CONSULENTE}.</li></ul></div>')
    corpo += '<h2 id="legge">Perché serve dal 7 giugno 2026</h2>'
    corpo += ('<p>Il decreto legislativo n. 96 del 7 maggio 2026 chiede di dare ai candidati le indicazioni sulla retribuzione già negli avvisi e nei bandi. '
              'Il primo comma dell\'articolo 5 dice:</p>' + _cita(G, "art5_c1", "art. 5, comma 1")
              + f'<p>Chi riguarda, cosa non si può chiedere ai candidati e cosa non è scritto nel decreto: <a href="/{P_GUIDA}">la guida con il testo dell\'articolo</a>.</p>')
    corpo += '<h2 id="pro">Per chi lo usa ogni giorno</h2>'
    corpo += (f'<p>Stiamo valutando una versione per consulenti del lavoro, studi paghe, agenzie e uffici del personale, e un\'API per chi sviluppa programmi. '
              f'<strong>Non sono in vendita</strong>: oggi misuriamo solo l\'interesse. Prezzi e lista d\'attesa: <a href="/{P_PRO}">per consulenti e aziende</a> · '
              f'<a href="/{P_API}">API</a>.</p>')
    corpo += _fonti_legge(G)
    testata = G.banda("Per chi assume", "Retribuzione per l'annuncio di lavoro",
                      f"Scegli contratto e livello: ottieni la riga pronta con la retribuzione iniziale, le mensilità, il contratto, la fonte e la data. "
                      f"<strong>{n_liv} livelli</strong> di 5 contratti, gratis.", icona="doc")
    G.pagina(P_STRUMENTO, "Retribuzione per l'annuncio di lavoro: la riga pronta dal CCNL",
             "Strumento gratuito: scegli contratto e livello e copia la riga con la retribuzione iniziale lorda, le mensilità, il CCNL, la fonte e la data della tabella.",
             corpo, testata, briciole=[("Home", ""), ("Annuncio di lavoro", P_STRUMENTO)])


# ---------------------------------------------------------------- 2. guida
def guida(G, D):
    corpo = ('<div class="card pull testo"><p style="margin:0"><strong>In breve.</strong> Dal 7 giugno 2026 chi cerca personale deve dare ai candidati, già nell\'annuncio, '
             'le indicazioni sulla retribuzione iniziale (o sulla fascia) e sul contratto collettivo applicato. Lo dice l\'articolo 5 del decreto legislativo n. 96 del 2026 (esclusi lavoro domestico e lavoro intermittente, art. 2 comma 2). '
             'Qui trovi il testo com\'è scritto, a chi si applica, quattro esempi di riga e quello che il decreto non dice.</p></div>')
    corpo += '<h2 id="testo">Cosa dice l\'articolo 5</h2>'
    corpo += (f'<p>Il {G.h(LEGGE["atto"]).lower()} attua la {G.h(LEGGE["direttiva"])} sulla parità di retribuzione tra uomini e donne. È pubblicato nella '
              f'{G.h(LEGGE["gazzetta"])} ed è in vigore dal {G.data_lunga(LEGGE["in_vigore_dal"])}. L\'articolo 5 ha per titolo «{G.h(LEGGE["rubriche"]["5"])}» '
              'e ha tre commi. Il primo riguarda l\'annuncio:</p>' + _cita(G, "art5_c1", "art. 5, comma 1"))
    corpo += ('<div class="testo"><p>In parole semplici, il comma chiede due informazioni e dice dove metterle.</p><ul>'
              '<li><strong>La retribuzione iniziale o la relativa fascia</strong> della posizione. Una cifra sola oppure un minimo e un massimo.</li>'
              '<li><strong>Le pertinenti disposizioni del contratto collettivo applicato</strong> dal datore di lavoro per quella posizione.</li>'
              '<li><strong>Dove</strong>: «negli avvisi e nei bandi con cui vengono rese note le opportunità di lavoro». Cioè nell\'annuncio, non solo al colloquio.</li></ul>'
              '<p>Il decreto non dà un modello di frase e non elenca le «pertinenti disposizioni». Scrivere il nome del contratto e il livello di inquadramento è '
              'il modo più diretto di indicarle, ma è una nostra lettura, non una regola scritta nel testo. La lettura si appoggia all\'articolo 6, che per l\'informativa data '
              'all\'assunzione nomina proprio questi elementi:</p></div>' + _cita(G, "art6_c2_p1", "art. 6, comma 2, primo periodo"))
    corpo += '<h2 id="chi">A chi si applica</h2>'
    corpo += ('<p>L\'ambito del decreto è scritto nell\'articolo 2. Riguarda i datori di lavoro pubblici e privati e i contratti di lavoro subordinato; '
              'il terzo comma estende l\'articolo 5 ai candidati.</p>'
              + _cita(G, "art2_c1", "art. 2, comma 1") + _cita(G, "art2_c2", "art. 2, comma 2") + _cita(G, "art2_c3", "art. 2, comma 3"))
    corpo += ('<div class="testo"><ul>'
              '<li><strong>Piccole imprese</strong>: nell\'articolo 5 non c\'è una soglia di dipendenti. Le soglie del decreto riguardano altri obblighi '
              '(per esempio i criteri di progressione economica, da cui l\'articolo 6 esonera chi ha meno di cinquanta dipendenti).</li>'
              '<li><strong>Tempo determinato e part time</strong>: sono compresi, lo dice il comma 2.</li>'
              '<li><strong>Lavoro domestico e lavoro intermittente</strong>: sono esclusi, lo dice lo stesso comma. Per colf e badanti indicare la paga resta una buona '
              'pratica, non un obbligo di questo decreto.</li>'
              '<li><strong>Annunci già pubblicati prima del 7 giugno 2026</strong>: nel testo letto non c\'è una regola transitoria.</li></ul></div>')
    corpo += '<h2 id="esempi">Esempi di righe con i minimi dei contratti</h2>'
    corpo += ('<p>Queste righe indicano la retribuzione iniziale, le mensilità, l\'orario, il contratto, il livello, la fonte e la data. Usano il minimo del contratto '
              'nazionale: se l\'azienda offre di più, la cifra da scrivere è quella offerta, oppure una fascia che parte dal minimo.</p>'
              + _esempio(G, D, "Commercio, 4° livello, tempo pieno", "terziario", "iv")
              + _esempio(G, D, "Metalmeccanici, livello C3, tempo pieno", "metalmeccanici", "c3")
              + _esempio(G, D, "Multiservizi, 2° livello, part time di 20 ore", "multiservizi", "2", "ore", 20)
              + _esempio(G, D, "Logistica, livello C3 del personale viaggiante, tempo pieno", "logistica", "c3")
              + f'<p><a class="btn" href="/{P_STRUMENTO}">Crea la riga per il tuo contratto e livello</a></p>'
              f'<p class="small">Lo strumento copre oggi {_numeri(G)} livelli di 5 contratti: commercio, metalmeccanici, multiservizi, logistica e lavoro domestico.</p>')
    corpo += G.AD
    corpo += '<h2 id="colloquio">Cosa non si può chiedere al candidato</h2>'
    corpo += ('<p>Il secondo comma vieta di chiedere quanto il candidato guadagna o guadagnava, anche tramite chi fa la selezione per conto dell\'azienda.</p>'
              + _cita(G, "art5_c2", "art. 5, comma 2")
              + '<p>Il terzo comma riguarda il modo di scrivere annunci e bandi:</p>' + _cita(G, "art5_c3", "art. 5, comma 3")
              + '<p>In pratica: titoli professionali e requisiti scritti in modo neutro rispetto al genere, e nessuna domanda sulla busta paga precedente nei moduli di candidatura.</p>')
    corpo += '<h2 id="sanzioni">Sanzioni: cosa c\'è scritto e cosa no</h2>'
    corpo += ('<p>Il decreto parla di conseguenze in due articoli. L\'articolo 13 («' + G.h(LEGGE["rubriche"]["13"]) + '») ha un solo comma:</p>' + _cita(G, "art13_c1", "art. 13, comma 1")
              + '<p>Per far valere i diritti del decreto davanti al giudice c\'è l\'articolo 12 («' + G.h(LEGGE["rubriche"]["12"]) + '»), che al primo comma dice:</p>'
              + _cita(G, "art12_c1_p1", "art. 12, comma 1, primo periodo")
              + '<div class="testo"><p>Il rinvio dell\'articolo 13 riguarda le discriminazioni accertate; quello dell\'articolo 12 le regole del processo. <strong>Nelle fonti che abbiamo letto non è indicato un importo di sanzione '
              'specifico per l\'annuncio pubblicato senza la retribuzione</strong>: per questo qui non scriviamo cifre. Se un articolo o un servizio ne indica una, '
              f'chiedi da quale norma viene e {CONSULENTE} del lavoro.</p></div>')
    corpo += '<h2 id="lista">Prima di pubblicare l\'annuncio</h2><div class="testo"><ol>'
    corpo += ('<li>Scegli il contratto collettivo che l\'azienda applica e il livello giusto per le mansioni.</li>'
              '<li>Decidi la cifra: il minimo del livello oppure la retribuzione che offri davvero, se è più alta. In alternativa una fascia.</li>'
              '<li>Scrivi che la cifra è lorda, se è al mese o all\'anno, e quante mensilità.</li>'
              '<li>Indica l\'orario: tempo pieno o part time, con le ore.</li>'
              '<li>Scrivi il contratto e il livello di inquadramento.</li>'
              '<li>Rileggi i requisiti: devono essere neutri rispetto al genere.</li>'
              '<li>Togli dai moduli di candidatura le domande sulla retribuzione attuale o passata.</li></ol>'
              '<p>Queste sono informazioni generali, non una consulenza. Circolari e chiarimenti del Ministero del Lavoro possono precisare come applicare la norma: '
              'aggiorniamo la pagina quando escono.</p></div>')
    corpo += _fonti_legge(G)
    testata = G.banda("Guida per chi assume", "Cosa scrivere nell'annuncio di lavoro dal 7 giugno 2026",
                      "L'articolo 5 del D.Lgs. 96/2026 parola per parola: retribuzione iniziale o fascia, contratto collettivo, a chi si applica e cosa il decreto non dice.",
                      icona="doc")
    G.pagina(P_GUIDA, "Annuncio di lavoro dal 7 giugno 2026: cosa scrivere sulla paga",
             "D.Lgs. 96/2026, art. 5: negli annunci di lavoro vanno indicate la retribuzione iniziale o la fascia e il contratto collettivo. Testo, esclusioni ed esempi.",
             corpo, testata, briciole=[("Home", ""), ("Annuncio di lavoro", P_STRUMENTO), ("Cosa scrivere", P_GUIDA)])


# ---------------------------------------------------------------- 3. per consulenti e aziende (Pro)
def _modulo_pro(G):
    ruoli = ["Titolare o socio dello studio", "Consulente o collaboratore", "Addetto paghe", "Responsabile del personale", "Selezionatore", "Sviluppatore o prodotto", "Altro"]
    tipi = ["Studio di consulenza del lavoro", "Studio paghe o commercialista", "Agenzia per il lavoro o di selezione", "Azienda (ufficio del personale)",
            "Programma per il personale o sito di annunci", "Associazione di categoria", "Altro"]
    quanti = ["Da 1 a 5", "Da 6 a 20", "Da 21 a 50", "Più di 50"]
    return f"""<form name="pro" method="POST" data-netlify="true" netlify-honeypot="bot-field" class="form card" data-lista="pro-ok" id="avvisami">
<input type="hidden" name="form-name" value="pro">
{_campo_hp()}
<label>Nome<input type="text" name="nome" required maxlength="120" autocomplete="name"></label>
<label>Il tuo ruolo<select name="ruolo" required>{_opzioni(ruoli)}</select></label>
<label>Tipo di studio o azienda<select name="tipo" required>{_opzioni(tipi)}</select></label>
<label>Annunci o assunzioni al mese<select name="volume" required>{_opzioni(quanti)}</select></label>
<label>Piano che ti interessa<select name="piano"><option value="annuale">Pro, {PREZZI['pro_anno']} € l'anno</option><option value="mensile">Pro, {PREZZI['pro_mese']} € al mese</option><option value="non-so">Non lo so ancora</option></select></label>
<label>Email<input type="email" name="email" required maxlength="200" autocomplete="email" placeholder="nome@studio.it"></label>
<label>Contratti che ti servono<textarea name="contratti" rows="3" maxlength="1500" placeholder="Per esempio: studi professionali, turismo, edilizia, cooperative sociali"></textarea></label>
<label class="check"><input type="checkbox" name="consenso" value="si" required><span>Accetto che questi dati siano conservati per scrivermi una volta, quando Paga CCNL Pro apre o se decidiamo di non farlo. Non è un acquisto (base giuridica: il tuo consenso; dettagli e tempi nella <a href="/privacy/#lista">privacy</a>).</span></label>
<button type="submit" class="btn">Avvisami all'apertura</button>
<p class="small" data-errore hidden style="margin:0;color:var(--warm-ink);font-weight:700">Invio non riuscito. Riprova tra poco.</p>
</form>
<div class="nota ok" id="pro-ok" tabindex="-1" hidden>{G.ico("check")}<p><strong>Ricevuto.</strong> Ti scriviamo una volta, quando Pro apre o se decidiamo di non farlo. Non hai pagato niente e non hai preso impegni.</p></div>"""


def pro(G, D):
    n_liv = _numeri(G)
    corpo = (f'<div class="card pull testo" id="stato"><p style="margin:0"><strong>Non è ancora in vendita.</strong> Paga CCNL Pro e l\'API sono in valutazione: qui trovi cosa '
             f'darebbero e quanto costerebbero. Oggi il sito ha <strong>5 contratti e {n_liv} livelli</strong>, non di più. Con questa pagina misuriamo l\'interesse: '
             'se basta, aggiungiamo altri contratti e apriamo. Se non basta, il sito resta com\'è, gratuito.</p></div>')
    corpo += '<h2 id="oggi">Cosa c\'è già, gratis</h2><div class="testo"><ul>'
    corpo += (f'<li>La <a href="/{P_STRUMENTO}">riga di retribuzione per l\'annuncio di lavoro</a>, da contratto e livello, con fonte e data.</li>'
              f'<li>Le <a href="/">tabelle dei minimi</a> di {n_liv} livelli: commercio, metalmeccanici, multiservizi, logistica e lavoro domestico.</li>'
              '<li>Per ogni livello: voci del minimo, paga oraria con il divisore del contratto, part time, aumenti già firmati e documenti ufficiali.</li>'
              f'<li>La <a href="/{P_GUIDA}">guida all\'articolo 5 del D.Lgs. 96/2026</a>, con il testo citato parola per parola.</li></ul>'
              '<p>Queste pagine restano gratuite anche se Pro apre.</p></div>')
    corpo += '<h2 id="pro">Cosa darebbe Paga CCNL Pro</h2>'
    corpo += ('<p>Pro è pensato per chi scrive annunci e lettere di assunzione ogni settimana: consulenti del lavoro, studi paghe, agenzie di selezione, uffici del personale.</p>'
              '<div class="testo"><ul>'
              '<li><strong>Tutti i contratti del sito</strong>, anche quelli che aggiungeremo, nello stesso strumento.</li>'
              '<li><strong>Uso senza limite</strong>, per più posizioni e più clienti.</li>'
              '<li><strong>La riga dell\'annuncio in PDF</strong>, con la fonte e la data, da tenere nel fascicolo.</li>'
              '<li><strong>Avviso per email</strong> quando un contratto si rinnova o scatta un aumento.</li>'
              '<li><strong>Storico degli aumenti</strong> di ogni livello, con le date.</li></ul></div>')
    corpo += f"""<div class="prezzi">
<div class="card prezzo"><h3>Pro annuale</h3><p class="cifra-p">{PREZZI['pro_anno']} € <small>l'anno</small></p>
<p class="small" style="margin:0">Prezzo previsto. Nessun pagamento oggi.</p>
<a class="btn" href="#avvisami" data-piano="annuale" data-goatcounter-click="{EV['pro']}" data-goatcounter-title="Pro {PREZZI['pro_anno']} € l'anno">Mi interessa</a></div>
<div class="card prezzo"><h3>Pro mensile</h3><p class="cifra-p">{PREZZI['pro_mese']} € <small>al mese</small></p>
<p class="small" style="margin:0">Prezzo previsto. Nessun pagamento oggi.</p>
<a class="btn" href="#avvisami" data-piano="mensile" data-goatcounter-click="{EV['pro']}" data-goatcounter-title="Pro {PREZZI['pro_mese']} € al mese">Mi interessa</a></div>
<div class="card prezzo"><h3>API</h3><p class="cifra-p">{PREZZI['api_mese']} € <small>al mese</small></p>
<p class="small" style="margin:0">Chiave senza trattativa, quando il servizio esiste. In valutazione.</p>
<a class="btn" href="/{P_API}" data-goatcounter-click="{EV['api_prezzo']}" data-goatcounter-title="API {PREZZI['api_mese']} € al mese">Vedi l'esempio JSON</a></div>
</div>"""
    corpo += ('<p class="small">I pulsanti «Mi interessa» non vendono niente: portano al modulo qui sotto e contano un clic, senza cookie. '
              'Il prezzo definitivo, l\'IVA e le condizioni li scriviamo qui prima dell\'apertura.</p>')
    corpo += '<h2 id="limiti">I limiti di oggi, detti chiari</h2><div class="testo"><ul>'
    corpo += (f'<li><strong>Cinque contratti.</strong> I contratti collettivi nazionali sono centinaia; noi ne abbiamo cinque, con {n_liv} livelli.</li>'
              '<li><strong>Solo cifre con due fonti.</strong> Aggiungiamo un contratto solo se troviamo due fonti indipendenti (testo depositato al CNEL, tabella del Ministero del Lavoro o tabelle delle parti firmatarie) uguali al centesimo: per alcuni contratti '
              'oggi la seconda fonte non c\'è.</li>'
              '<li><strong>Solo minimi nazionali lordi.</strong> Niente netto, niente costo del lavoro, niente contratti aziendali o territoriali.</li>'
              f'<li><strong>Non sostituisce il professionista.</strong> Le cifre sono informazioni generali: prima di usarle, {CONSULENTE} del lavoro (o, se il consulente sei tu, con il testo del contratto).</li></ul></div>')
    corpo += G.AD
    corpo += '<h2 id="lista-attesa">Avvisami all\'apertura</h2>'
    corpo += ('<p>Lascia i tuoi dati se Pro ti servirebbe. Ci dici quali contratti ti mancano e noi partiamo da quelli. Ti scriviamo una sola volta. '
              'Non chiediamo carte né pagamenti.</p>' + _modulo_pro(G))
    corpo += '<h2 id="domande">Domande</h2>'
    corpo += ('<div class="faq"><h3>Posso pagare adesso?</h3><p>No. Non c\'è nessun modo di pagare su questo sito. Chi lascia l\'email entra solo in una lista d\'attesa.</p></div>'
              '<div class="faq"><h3>Quando apre?</h3><p>Non c\'è una data. Decidiamo dopo aver contato quante persone usano lo strumento e quante lasciano l\'email. '
              'Se l\'interesse è poco, non apriamo e lo scriviamo a chi è in lista.</p></div>'
              '<div class="faq"><h3>Quali contratti aggiungerete?</h3><p>Quelli più chiesti nel modulo, se hanno due fonti indipendenti leggibili. Non promettiamo un contratto '
              'finché le sue cifre non hanno passato i controlli.</p></div>'
              '<div class="faq"><h3>Lo strumento gratuito resta?</h3><p>Sì. La riga per l\'annuncio e le pagine dei livelli restano gratuite per i contratti che coprono oggi.</p></div>')
    corpo += f"<script>{JS_MODULI}</script>"
    testata = G.banda("Per consulenti e aziende", "Paga CCNL Pro: per consulenti del lavoro, studi paghe e aziende",
                      f"Tutti i contratti del sito, la riga dell'annuncio in PDF, avvisi sui rinnovi. <strong>Non ancora in vendita</strong>: {PREZZI['pro_anno']} € l'anno previsti, "
                      "oggi solo lista d'attesa.", corta=False, icona="people")
    G.pagina(P_PRO, "Paga CCNL Pro per consulenti e aziende: prezzi e lista d'attesa",
             f"Paga CCNL Pro, non ancora in vendita: {PREZZI['pro_anno']} € l'anno o {PREZZI['pro_mese']} € al mese previsti. Riga dell'annuncio in PDF, avvisi sui rinnovi, storico. Lista d'attesa.",
             corpo, testata, briciole=[("Home", ""), ("Per consulenti e aziende", P_PRO)])


# ---------------------------------------------------------------- 4. API
def esempio_api(G, D):
    """Risposta d'esempio dell'API, generata dai dati veri di un livello (dati/annuncio.json dice quale)."""
    cid, lid = A["esempio_api"]["contratto"], A["esempio_api"]["livello"]
    m = G.C[cid]
    L = next(x for x in m["livelli"] if x["id"] == lid)
    v = G.valori(cid, L)
    n2 = lambda x: f"{G.arr(x):.2f}"  # noqa: E731
    fonti = [{"titolo": G.FONTI_DEF[f]["titolo"], "editore": G.FONTI_DEF[f]["chi"], "url": G.url_fonte(f), "letto_il": G.FONTI[f]["letto_il"],
              "sha256": G.FONTI[f]["sha256"]} for f in (m["fonte_a"], m["fonte_b"])]
    return {
        "versione": "bozza",
        "contratto": {"id": m["slug"], "nome": m["nome"], "codice_cnel": m["codice_cnel"], "scadenza": m["testo"]["scadenza"]},
        "livello": {"id": L["slug"], "nome": L["nome"]},
        "valuta": "EUR",
        "in_vigore_dal": v["dal"],
        "minimo_mensile_lordo": n2(v["mensile"]),
        "voci": [{"nome": n, "importo": n2(x)} for n, x in v["cur"]["parti"]],
        "mensilita": m["mensilita"]["valore"],
        "minimo_annuo_lordo": n2(v["annuo"]),
        "ore_settimanali": v["ore_norm"],
        "divisore_orario": m["divisore_orario"]["valore"],
        "paga_oraria_lorda": n2(v["oraria"]),
        "prossimi_minimi": [{"dal": t["dal"], "minimo_mensile_lordo": n2(G.totale(t))} for t in v["future"] if t["pubblicabile"]],
        "riga_annuncio": riga(G, D, cid, lid)["testo"],
        "fonti": fonti,
        "controllato_il": G.CONTROLLO.isoformat(),
    }


def _modulo_api(G):
    usi = ["Programma per il personale o paghe", "Sito o portale di annunci", "Calcolatore sul mio sito", "Uso interno in azienda o in studio", "Altro"]
    quante = ["Meno di 1.000", "Da 1.000 a 10.000", "Più di 10.000", "Non lo so"]
    return f"""<form name="api" method="POST" data-netlify="true" netlify-honeypot="bot-field" class="form card" data-lista="api-ok" id="chiave">
<input type="hidden" name="form-name" value="api">
{_campo_hp()}
<label>Nome<input type="text" name="nome" required maxlength="120" autocomplete="name"></label>
<label>Azienda o progetto<input type="text" name="azienda" required maxlength="200" autocomplete="organization"></label>
<label>Email<input type="email" name="email" required maxlength="200" autocomplete="email" placeholder="nome@azienda.it"></label>
<label>Dove la useresti<select name="uso" required>{_opzioni(usi)}</select></label>
<label>Richieste al mese (stima)<select name="richieste">{_opzioni(quante)}</select></label>
<label>Contratti che ti servono<textarea name="contratti" rows="3" maxlength="1500" placeholder="Per esempio: commercio, metalmeccanici, turismo, studi professionali"></textarea></label>
<label class="check"><input type="checkbox" name="consenso" value="si" required><span>Accetto che questi dati siano conservati per rispondere alla richiesta e scrivermi quando la chiave di prova è pronta, o se decidiamo di non fare l'API. Non è un acquisto (base giuridica: il tuo consenso; dettagli e tempi nella <a href="/privacy/#lista">privacy</a>).</span></label>
<button type="submit" class="btn">Invia la richiesta</button>
<p class="small" data-errore hidden style="margin:0;color:var(--warm-ink);font-weight:700">Invio non riuscito. Riprova tra poco.</p>
</form>
<div class="nota ok" id="api-ok" tabindex="-1" hidden>{G.ico("check")}<p><strong>Richiesta ricevuta.</strong> L'API è in valutazione: ti scriviamo quando la chiave di prova è pronta, o se decidiamo di non farla. Non hai pagato niente.</p></div>"""


def api(G, D):
    n_liv = _numeri(G)
    es = esempio_api(G, D)
    testo_json = json.dumps(es, ensure_ascii=False, indent=2)
    dest = G.SITO / FILE_API
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo_json + "\n", encoding="utf-8")
    corpo = (f'<div class="card pull testo" id="stato"><p style="margin:0"><strong>In valutazione: oggi non c\'è un servizio a cui collegarsi.</strong> Questa pagina mostra '
             f'come sarebbe la risposta, con i dati veri di un livello, e raccoglie le richieste di una chiave di prova. Dati disponibili oggi: 5 contratti, {n_liv} livelli. '
             f'Prezzo previsto: <strong>{PREZZI["api_mese"]} € al mese</strong>, chiave senza trattativa, quando il servizio esiste. Non è in vendita.</p>'
             f'<p style="margin:12px 0 0"><a class="btn" href="#chiave" data-goatcounter-click="{EV["api"]}" data-goatcounter-title="API: chiedi una chiave di prova">Chiedi una chiave di prova</a></p></div>')
    corpo += '<h2 id="cosa">Cosa darebbe l\'API</h2><div class="testo">'
    corpo += ('<p>Una richiesta con contratto e livello, una risposta in JSON con il minimo in vigore e tutto quello che serve per mostrarlo o per scrivere un annuncio.</p><ul>'
              '<li>Minimo mensile lordo del livello, con le voci che lo compongono e la data da cui è in vigore.</li>'
              '<li>Mensilità, minimo annuo, orario settimanale, divisore orario e paga oraria, come li fissa il contratto.</li>'
              '<li>Aumenti già firmati, con la data e il nuovo minimo.</li>'
              '<li>La riga pronta per l\'annuncio di lavoro, la stessa dello <a href="/' + P_STRUMENTO + '">strumento gratuito</a>.</li>'
              '<li>Le fonti: titolo, chi le pubblica, indirizzo, data di lettura e impronta del file letto.</li></ul>'
              '<p>Ogni cifra passerebbe gli stessi due controlli delle pagine del sito: somma delle voci uguale al totale stampato e seconda fonte uguale al centesimo. '
              'Una riga che non li passa non verrebbe restituita con una cifra stimata: la risposta direbbe che la cifra è sospesa.</p></div>')
    corpo += '<h2 id="esempio">Esempio di risposta</h2>'
    corpo += (f'<p>Questo JSON è generato dai dati del sito per il {G.h(es["livello"]["nome"])} del contratto {G.h(es["contratto"]["nome"])}. '
              f'Le cifre sono quelle della <a href="/{es["contratto"]["id"]}/{es["livello"]["id"]}/">pagina del livello</a>. '
              f'Lo stesso contenuto è in un <a href="/{FILE_API}">file di esempio</a>: è un file fermo, non un servizio.</p>'
              f'<pre class="codice" tabindex="0"><code id="api-esempio">{G.h(testo_json)}</code></pre>')
    corpo += '<h2 id="campi">I campi</h2>'
    corpo += G.tabella(["Campo", "Cosa contiene"], [
        ("<code>contratto</code>", "Nome del contratto collettivo nazionale, codice del CNEL e data di scadenza del testo."),
        ("<code>livello</code>", "Livello di inquadramento, con lo stesso nome usato nel sito."),
        ("<code>in_vigore_dal</code>", "Data da cui vale la tabella (anno-mese-giorno)."),
        ("<code>minimo_mensile_lordo</code>", "Minimo del contratto nazionale, lordo, in euro con due decimali, scritto come testo per non perdere centesimi."),
        ("<code>voci</code>", "Le voci stampate nella tabella: la loro somma è il minimo mensile."),
        ("<code>mensilita</code>, <code>minimo_annuo_lordo</code>", "Numero di mensilità del contratto e minimo mensile moltiplicato per le mensilità."),
        ("<code>ore_settimanali</code>, <code>divisore_orario</code>, <code>paga_oraria_lorda</code>", "Orario normale, divisore scritto nel contratto e minimo mensile diviso per il divisore."),
        ("<code>prossimi_minimi</code>", "Aumenti già firmati e verificati, con la data."),
        ("<code>riga_annuncio</code>", "Riga completa per l'annuncio di lavoro, a tempo pieno."),
        ("<code>fonti</code>, <code>controllato_il</code>", "I due documenti da cui viene la cifra e la data dell'ultimo controllo."),
    ], num=[])
    corpo += G.AD
    corpo += '<h2 id="prezzo">Prezzo e condizioni previste</h2><div class="testo"><ul>'
    corpo += (f'<li><strong>{PREZZI["api_mese"]} € al mese</strong>, prezzo pubblico, senza telefonate e senza preventivo, quando il servizio esiste.</li>'
              '<li>Chiave di prova gratuita prima di decidere.</li>'
              '<li>Nessun pagamento oggi: il prezzo definitivo, l\'IVA e i limiti d\'uso li scriviamo qui prima dell\'apertura.</li>'
              f'<li>Dati disponibili all\'inizio: quelli del sito, cioè 5 contratti e {n_liv} livelli. Altri contratti si aggiungono solo con due fonti indipendenti (testo depositato al CNEL, tabella del Ministero del Lavoro o tabelle delle parti firmatarie) uguali al centesimo.</li>'
              f'<li>Le cifre restano informazioni generali sui minimi nazionali: chi le mostra ai propri utenti dovrebbe dirlo, e per i casi concreti vale sempre «{CONSULENTE}».</li></ul></div>')
    corpo += '<h2 id="richiesta">Chiedi una chiave di prova</h2>'
    corpo += ('<p>Raccontaci dove useresti i dati e quali contratti ti servono. Se le richieste bastano, costruiamo il servizio e ti mandiamo la chiave. '
              'Se non bastano, te lo scriviamo.</p>' + _modulo_api(G))
    corpo += f"<script>{JS_MODULI}</script>"
    testata = G.banda("API · in valutazione", "API dei minimi CCNL in JSON",
                      f"Minimo, voci, mensilità, paga oraria, aumenti e fonti per contratto e livello. <strong>In valutazione, non ancora attiva</strong>: {PREZZI['api_mese']} € al mese previsti, "
                      "chiave senza trattativa quando il servizio esiste.", corta=False, icona="doc")
    G.pagina(P_API, "API CCNL in JSON: minimi per livello (non ancora attiva)",
             f"API dei minimi CCNL in valutazione: esempio JSON vero con minimo, voci, paga oraria, aumenti e fonti. {PREZZI['api_mese']} € al mese previsti. Chiedi una chiave di prova.",
             corpo, testata, briciole=[("Home", ""), ("API", P_API)])


# Frase per la pagina privacy (una sola, come chiede la scheda) e voce per «Chi siamo».
PRIVACY = ('<h2 id="lista">Moduli «Avvisami all\'apertura» e «Chiedi una chiave di prova»</h2><p>Se compili uno di questi due moduli riceviamo, tramite Netlify Forms, '
           'i dati che scrivi (nome, ruolo, tipo di studio o azienda, email e risposte) e li usiamo, con il tuo consenso (art. 6.1.a GDPR), solo per scriverti quando '
           'il servizio apre o se decidiamo di non farlo. Li cancelliamo dopo averti scritto, e comunque entro il 31 marzo 2027 se non apriamo; prima, se ce lo chiedi con il modulo delle segnalazioni. Lasciare i dati non è un acquisto.</p>')


def genera(G):
    D = dati_strumento(G)
    strumento(G, D)
    guida(G, D)
    pro(G, D)
    api(G, D)
