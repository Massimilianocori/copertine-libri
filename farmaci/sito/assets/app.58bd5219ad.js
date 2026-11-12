(function(){
'use strict';
function norm(s){return String(s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,' ').trim();}
window.FarmacoEq={norm:norm};
// tema
var b=document.querySelector('[data-tema]');
if(b){b.addEventListener('click',function(){var r=document.documentElement;var dark=r.getAttribute('data-theme')==='dark'||(!r.getAttribute('data-theme')&&window.matchMedia('(prefers-color-scheme: dark)').matches);var t=dark?'light':'dark';r.setAttribute('data-theme',t);try{localStorage.setItem('fe-tema',t);}catch(e){}});}
// ricerca della home (indice JSON caricato alla prima digitazione)
var q=document.querySelector('[data-cerca]');
if(q){var out=document.querySelector('[data-risultati]');var indice=null,attesa=false;
  function mostra(){var p=norm(q.value).split(' ').filter(Boolean);out.innerHTML='';if(!p.length){out.hidden=true;return;}
    if(!indice){out.hidden=false;out.innerHTML='<li class="vuoto">Carico l\'elenco…</li>';carica();return;}
    var ris=[];for(var i=0;i<indice.length&&ris.length<12;i++){var e=indice[i],t=e[3];var ok=true;for(var k=0;k<p.length;k++){if((' '+t).indexOf(' '+p[k])<0){ok=false;break;}}if(ok)ris.push(e);}
    out.hidden=false;
    if(!ris.length){out.innerHTML='<li class="vuoto">Nessun farmaco trovato con questo nome nelle liste AIFA. Prova con il principio attivo.</li>';return;}
    ris.forEach(function(e){var li=document.createElement('li');var a=document.createElement('a');a.href=e[2];var s=document.createElement('strong');s.textContent=e[0];var sp=document.createElement('span');sp.textContent=e[1];a.appendChild(s);a.appendChild(sp);li.appendChild(a);out.appendChild(li);});}
  function carica(){if(attesa)return;attesa=true;fetch(q.getAttribute('data-indice')).then(function(r){return r.json();}).then(function(j){indice=j.map(function(e){return [e[0],e[1],e[2],norm(e[0]+' '+(e[3]||''))];});mostra();}).catch(function(){out.innerHTML='<li class="vuoto">Elenco non disponibile: usa l\'indice dei principi attivi qui sotto.</li>';});}
  q.addEventListener('input',mostra);q.addEventListener('focus',carica);
  var f=q.closest('form');if(f)f.addEventListener('submit',function(ev){ev.preventDefault();var a=out.querySelector('a');if(a)location.href=a.href;});}
// tabella filtrabile e ordinabile
document.querySelectorAll('[data-tabella]').forEach(function(box){
  var tb=box.querySelector('tbody');var righe=Array.prototype.slice.call(tb.rows);var fi=box.querySelector('[data-filtro]');var so=box.querySelector('[data-solo-eq]');
  var cnt=box.querySelector('[data-conteggio]');var vuoto=box.querySelector('[data-vuoto]');
  righe.forEach(function(r){r._t=norm(r.textContent);});
  function filtra(){var p=fi?norm(fi.value).split(' ').filter(Boolean):[];var n=0;
    righe.forEach(function(r){var ok=(!so||!so.checked||r.getAttribute('data-eq')==='1');for(var k=0;ok&&k<p.length;k++){if(r._t.indexOf(p[k])<0)ok=false;}r.hidden=!ok;if(ok)n++;});
    if(cnt)cnt.textContent=n===righe.length?(n+' confezioni'):(n+' confezioni su '+righe.length);if(vuoto)vuoto.hidden=n>0;}
  if(fi){fi.addEventListener('input',filtra);var u=new URLSearchParams(location.search).get('q');if(u){fi.value=u;}}
  if(so)so.addEventListener('change',filtra);
  box.querySelectorAll('th[data-col]').forEach(function(th){var bt=th.querySelector('button');if(!bt)return;bt.addEventListener('click',function(){
    var c=parseInt(th.getAttribute('data-col'),10);var asc=th.getAttribute('aria-sort')!=='ascending';
    box.querySelectorAll('th[data-col]').forEach(function(x){x.removeAttribute('aria-sort');});th.setAttribute('aria-sort',asc?'ascending':'descending');
    righe.sort(function(a,b){var x=a.cells[c].getAttribute('data-v')||a.cells[c].textContent,y=b.cells[c].getAttribute('data-v')||b.cells[c].textContent;return (x<y?-1:x>y?1:0)*(asc?1:-1);});
    var fr=document.createDocumentFragment();righe.forEach(function(r){fr.appendChild(r);});tb.appendChild(fr);});});
  filtra();
});
})();
