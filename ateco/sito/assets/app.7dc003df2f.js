(function(){
'use strict';
function norm(s){return String(s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9.]+/g,' ').trim();}
function cifre(s){return String(s||'').replace(/[^0-9]/g,'');}
window.CodiciAteco={norm:norm};
var b=document.querySelector('[data-tema]');
if(b){b.addEventListener('click',function(){var r=document.documentElement;var dark=r.getAttribute('data-theme')==='dark'||(!r.getAttribute('data-theme')&&window.matchMedia('(prefers-color-scheme: dark)').matches);var t=dark?'light':'dark';r.setAttribute('data-theme',t);try{localStorage.setItem('ca-tema',t);}catch(e){}});}
// ricerca: indice JSON caricato alla prima digitazione. Voce: [codice, titolo, url, tipo (25|22), parole]
var q=document.querySelector('[data-cerca]');
if(q){var out=document.querySelector('[data-risultati]');var indice=null,attesa=false;
  function cerca(v){var t=v.trim();if(!t)return [];var ris=[];
    if(/^[0-9][0-9 .]*$/.test(t)){var c=cifre(t);
      for(var i=0;i<indice.length;i++){if(indice[i][5].indexOf(c)===0)ris.push(indice[i]);}
      ris.sort(function(a,b){return (a[5].length-b[5].length)||(a[3]<b[3]?-1:a[3]>b[3]?1:0)||(a[0]<b[0]?-1:1);});
      return unici(ris).slice(0,12);}
    if(/^[a-v]$/i.test(t)){for(var j=0;j<indice.length;j++){if(indice[j][0]===t.toUpperCase())return [indice[j]];}}
    // parole di 5 lettere o più senza la vocale finale: «pizzeria» trova anche «pizzerie», «idraulico» anche «idraulici»
    var p=norm(t).split(' ').filter(Boolean).map(function(w){return w.length>=5?w.replace(/[aeiou]$/,''):w;});var a=[],z=[];
    for(var k=0;k<indice.length&&a.length<40;k++){var e=indice[k];var tt=' '+e[6],ww=' '+e[7];var okt=true,okw=true;
      for(var m=0;m<p.length;m++){if(tt.indexOf(' '+p[m])<0)okt=false;if(ww.indexOf(' '+p[m])<0&&tt.indexOf(' '+p[m])<0)okw=false;}
      if(okt)a.push(e);else if(okw)z.push(e);}
    function pes(e){return e[3]==='p'?-100:(e[3]==='22'?100:0)+(8-e[0].length);}
    a.sort(function(x,y){return pes(x)-pes(y);});
    return unici(a.concat(z)).slice(0,12);}
  // stesso titolo nella stessa pagina (classe, categoria e sottocategoria con lo stesso nome): si tiene il primo
  function unici(l){var visti={},out=[];l.forEach(function(e){var k=e[1]+'|'+e[2].split('#')[0];if(!visti[k]){visti[k]=1;out.push(e);}});return out;}
  function mostra(){out.innerHTML='';if(!q.value.trim()){out.hidden=true;return;}
    if(!indice){out.hidden=false;out.innerHTML='<li class="vuoto">Carico l\'elenco dei codici…</li>';carica();return;}
    var ris=cerca(q.value);out.hidden=false;
    if(!ris.length){out.innerHTML='<li class="vuoto">Nessun codice trovato. Prova con un\'altra parola (per esempio «ristorante», «software», «idraulici») o con le prime cifre del codice.</li>';return;}
    ris.forEach(function(e){var li=document.createElement('li');var a=document.createElement('a');a.href=e[2];var s=document.createElement('strong');s.textContent=e[0];
      var t=document.createElement('em');t.textContent=e[1];var sp=document.createElement('span');sp.textContent=e[3]==='22'?'ATECO 2022 → '+e[4]:(e[3]==='p'?'Guida':'ATECO 2025');
      a.appendChild(s);a.appendChild(t);a.appendChild(sp);li.appendChild(a);out.appendChild(li);});}
  function carica(){if(attesa)return;attesa=true;fetch(q.getAttribute('data-indice')).then(function(r){return r.json();}).then(function(j){
      indice=j.map(function(e){return [e[0],e[1],e[2],e[3],e[4]||'',cifre(e[0]),norm(e[0]+' '+e[1]),norm(e[5]||'')];});mostra();})
    .catch(function(){out.innerHTML='<li class="vuoto">Elenco non disponibile: usa l\'elenco delle sezioni qui sotto.</li>';});}
  q.addEventListener('input',mostra);q.addEventListener('focus',carica);
  var f=q.closest('form');if(f)f.addEventListener('submit',function(ev){ev.preventDefault();var a=out.querySelector('a');if(a)location.href=a.href;});}
// tabella filtrabile (da ATECO 2022 a ATECO 2025), 100 righe alla volta
document.querySelectorAll('[data-tabella]').forEach(function(box){
  var tb=box.querySelector('tbody');var righe=Array.prototype.slice.call(tb.rows);var fi=box.querySelector('[data-filtro]');
  var cnt=box.querySelector('[data-conteggio]');var vuoto=box.querySelector('[data-vuoto]');var altre=box.querySelector('[data-altre]');var lim=100;
  righe.forEach(function(r){r._t=norm(r.cells[0].textContent+' '+r.cells[1].textContent);r._c=cifre(r.cells[0].textContent);});
  function filtra(){var v=fi?fi.value.trim():'';var dig=/^[0-9][0-9 .]*$/.test(v)?cifre(v):null;var p=dig?[]:norm(v).split(' ').filter(Boolean);var n=0;
    righe.forEach(function(r){var ok=dig?r._c.indexOf(dig)===0:true;for(var k=0;ok&&k<p.length;k++){if(r._t.indexOf(p[k])<0)ok=false;}if(ok)n++;r.hidden=!ok||n>lim;});
    var vis=Math.min(n,lim);if(cnt)cnt.textContent=(n===righe.length?(n+' codici'):(n+' codici su '+righe.length))+(vis<n?' · ne vedi '+vis:'');
    if(vuoto)vuoto.hidden=n>0;if(altre)altre.hidden=vis>=n;}
  if(altre){altre.querySelector('[data-altre-piu]').addEventListener('click',function(){lim+=100;filtra();});altre.querySelector('[data-altre-tutte]').addEventListener('click',function(){lim=Infinity;filtra();});}
  if(fi){fi.addEventListener('input',function(){if(lim!==Infinity)lim=100;filtra();});var u=new URLSearchParams(location.search).get('q');if(u){fi.value=u;}
    if(location.hash&&location.hash.indexOf('#v-')===0){fi.value=decodeURIComponent(location.hash.slice(3));}}
  filtra();
  if(location.hash){var el=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(el)el.scrollIntoView();}
});
})();
