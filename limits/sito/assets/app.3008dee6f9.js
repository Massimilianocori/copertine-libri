var SOL=(function(){
'use strict';
function bis(a){return (a%4===0&&a%100!==0)||a%400===0;}
function pad(n){return (n<10?'0':'')+n;}
function parte(s){var m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(s||'');if(!m)return null;var a=+m[1],me=+m[2],g=+m[3];
  var gm=[31,bis(a)?29:28,31,30,31,30,31,31,30,31,30,31];if(me<1||me>12||g<1||g>gm[me-1])return null;return [a,me,g];}
function iso(p){return p[0]+'-'+pad(p[1])+'-'+pad(p[2]);}
function piuAnni(s,n){var p=parte(s);var a=p[0]+n,me=p[1],g=p[2];if(me===2&&g===29&&!bis(a))g=28;return iso([a,me,g]);}
function piuGiorni(s,n){var p=parte(s);var d=new Date(Date.UTC(p[0],p[1]-1,p[2]));d.setUTCDate(d.getUTCDate()+n);
  return iso([d.getUTCFullYear(),d.getUTCMonth()+1,d.getUTCDate()]);}
function calcola(cella,data){
  if(!parte(data))return null;
  var out={varianti:[],repose:null};
  cella.v.forEach(function(v){
    if(v.tr&&data<v.tr.data){out.varianti.push({l:v.l,cit:v.cit,errore:v.tr.msg});return;}
    var anni=v.a,l=v.l,cit=v.cit;
    if(v.prima&&data<=v.prima.fino){anni=v.prima.a;l=v.prima.l;cit=v.prima.cit;}
    var inizio=v.g?piuGiorni(data,v.g):data;
    out.varianti.push({l:l,cit:cit,anni:anni,scadenza:piuAnni(inizio,anni),nd:v.nd||''});
  });
  if(cella.r)out.repose={l:cella.r.l,cit:cella.r.cit,anni:cella.r.a,scadenza:piuAnni(data,cella.r.a)};
  return out;
}
return {calcola:calcola,piuAnni:piuAnni,piuGiorni:piuGiorni,parte:parte};
})();
if(typeof module!=='undefined'){module.exports=SOL;}
(function(){
'use strict';
if(typeof document==='undefined')return;
var b=document.querySelector('[data-tema]');
if(b){b.addEventListener('click',function(){var r=document.documentElement;var dark=r.getAttribute('data-theme')==='dark'||(!r.getAttribute('data-theme')&&window.matchMedia('(prefers-color-scheme: dark)').matches);var t=dark?'light':'dark';r.setAttribute('data-theme',t);try{localStorage.setItem('sol-tema',t);}catch(e){}});}
var MESI=['January','February','March','April','May','June','July','August','September','October','November','December'];
function lunga(s){var p=SOL.parte(s);return p[2]+' '+MESI[p[1]-1]+' '+p[0];}
function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function oggi(){var d=new Date();return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2);}
function giorniTra(a,b){var pa=SOL.parte(a),pb=SOL.parte(b);return Math.round((Date.UTC(pb[0],pb[1]-1,pb[2])-Date.UTC(pa[0],pa[1]-1,pa[2]))/864e5);}
var el=document.getElementById('dati-calc');if(!el)return;
var D=JSON.parse(el.textContent);
document.querySelectorAll('[data-calc]').forEach(function(box){
  var f=box.querySelector('form'),out=box.querySelector('.esito');
  var sS=f.querySelector('[name=stato]'),sC=f.querySelector('[name=causa]'),dI=f.querySelector('[name=data]'),lab=f.querySelector('[data-etichetta]');
  function cella(){var s=sS?sS.value:box.getAttribute('data-stato'),c=sC?sC.value:box.getAttribute('data-causa');return D.celle[s+'/'+c]||null;}
  function aggiornaEtichetta(){var c=sC?sC.value:box.getAttribute('data-causa');if(lab&&D.date[c])lab.textContent=D.date[c];
    if(sC&&sS){var ok=!!D.celle[sS.value+'/'+c];f.querySelector('[data-manca]').hidden=ok;}}
  if(sC)sC.addEventListener('change',aggiornaEtichetta);if(sS)sS.addEventListener('change',aggiornaEtichetta);aggiornaEtichetta();
  f.addEventListener('submit',function(ev){ev.preventDefault();
    var c=cella();if(!c){out.hidden=false;out.innerHTML='<p>We have not published this combination: the statute does not state its own deadline. Ask a licensed attorney in that state.</p>';return;}
    var r=SOL.calcola(c,dI.value);if(!r){out.hidden=false;out.innerHTML='<p>Enter a valid date.</p>';return;}
    var h='<h3>General deadline: '+esc(c.n)+'</h3><ol>';var t=oggi();
    r.varianti.forEach(function(v){
      if(v.errore){h+='<li class="no"><span>'+esc(v.l)+' · '+esc(v.cit)+'</span><b>'+esc(v.errore)+'</b></li>';return;}
      var g=giorniTra(t,v.scadenza);var st=g>=0?'<span class="stato">'+g+' days from today</span>':'<span class="stato passato">This general date is in the past. Exceptions can change it: talk to a licensed attorney.</span>';
      h+='<li><span>'+esc(v.l)+' · '+v.anni+(v.anni===1?' year':' years')+' · '+esc(v.cit)+'</span><b>'+lunga(v.scadenza)+'</b>'+'<small>'+st+(v.nd?' '+esc(v.nd):'')+'</small></li>';});
    if(r.repose)h+='<li class="rip"><span>'+esc(r.repose.l)+' (outer limit) · '+r.repose.anni+' years · '+esc(r.repose.cit)+'</span><b>'+lunga(r.repose.scadenza)+'</b><small>Counted from the date you entered. Many exceptions do not extend past this date.</small></li>';
    h+='</ol>';
    if(c.e&&c.e.length){h+='<p class="small"><strong>Exceptions that can move this date:</strong></p><ul>'+c.e.map(function(x){return '<li>'+esc(x)+'</li>';}).join('')+'</ul>';}
    h+='<p class="small">Estimate, not legal advice. Deadlines can be shorter or longer. Talk to a licensed attorney in your state. <a href="'+c.u+'">Read the statute and every exception</a>.</p>';
    out.hidden=false;out.innerHTML=h;});
});
})();
