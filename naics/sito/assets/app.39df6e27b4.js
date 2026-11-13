(function(){
'use strict';
function norm(s){return String(s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,' ').trim();}
function cifre(s){return String(s||'').replace(/[^0-9]/g,'');}
function radice(w){return w.length>4?w.replace(/(ies|es|s|y)$/,'').replace(/enc?t?$/,'en'):w;}  // bakery/bakeries -> baker, agent/agency -> agen (prefix match)
var b=document.querySelector('[data-tema]');
if(b){b.addEventListener('click',function(){var r=document.documentElement;var dark=r.getAttribute('data-theme')==='dark'||(!r.getAttribute('data-theme')&&window.matchMedia('(prefers-color-scheme: dark)').matches);var t=dark?'light':'dark';r.setAttribute('data-theme',t);try{localStorage.setItem('nl-theme',t);}catch(e){}});}
// search: JSON index loaded on first focus. Entry: [code, title, url, type, note]; index entries (joined by "|") come from a second file
// type: 2..6 = NAICS 2022 level, "17" = 2017 code, "sic" = 1987 SIC code, "p" = guide page
var q=document.querySelector('[data-cerca]');
if(q){var out=document.querySelector('[data-risultati]');var indice=null,attesa=false,per={},frasi=0;
  var ETI={'2':'Sector','3':'Subsector','4':'Industry group','5':'NAICS industry','6':'2022 NAICS','17':'2017 code','sic':'SIC 1987','p':'Guide'};
  var PESO={'6':0,'5':1,'4':2,'3':3,'2':4,'p':5,'17':6,'sic':7};
  function cerca(v){var t=v.trim();if(!t)return [];var ris=[];
    if(/^[0-9][0-9 -]*$/.test(t)){var c=cifre(t);
      for(var i=0;i<indice.length;i++){var e=indice[i];if(e.c.indexOf(c)===0)ris.push({e:e,f:''});}
      ris.sort(function(a,b){return (a.e.c===c?0:1)-(b.e.c===c?0:1)||(a.e.c.length-b.e.c.length)||(PESO[a.e[3]]-PESO[b.e[3]])||(a.e[0]<b.e[0]?-1:1);});
      return ris.slice(0,12);}
    var p=norm(t).split(' ').filter(Boolean).map(radice);var a=[],z=[];
    for(var k=0;k<indice.length&&a.length+z.length<200;k++){var e=indice[k];var tt=' '+e.n;var okt=true;
      for(var m=0;m<p.length;m++){if(tt.indexOf(' '+p[m])<0){okt=false;break;}}
      if(okt){a.push({e:e,f:''});continue;}
      if(!e.f)continue;
      for(var j=0;j<e.f.length;j++){var ff=' '+e.f[j];var okf=true;for(var m2=0;m2<p.length;m2++){if(ff.indexOf(' '+p[m2])<0){okf=false;break;}}
        if(okf){z.push({e:e,f:e[5].split('|')[j]});break;}}}
    a.sort(function(x,y){return (PESO[x.e[3]]-PESO[y.e[3]])||(x.e[0]<y.e[0]?-1:1);});
    var tutti=a.slice(0,6).concat(z).concat(a.slice(6)).slice(0,12);
    // no NAICS code has every word: show the codes that have most of the words (words of 4+ letters), after the exact results
    if(p.length>1&&!tutti.some(function(r){return r.e[3].length===1;})){var lunghe=p.filter(function(w){return w.length>3;});var o=[];
      for(var k2=0;lunghe.length&&k2<indice.length;k2++){var e2=indice[k2];if(e2[3]!=='6')continue;var pt=0,fr='';var t2=' '+e2.n;
        for(var m3=0;m3<lunghe.length;m3++){var w=' '+lunghe[m3];if(t2.indexOf(w)>=0){pt+=2;continue;}
          if(e2.f){for(var j2=0;j2<e2.f.length;j2++){if((' '+e2.f[j2]).indexOf(w)>=0){pt+=1;if(!fr)fr=e2[5].split('|')[j2];break;}}}}
        if(pt)o.push({e:e2,f:fr,pt:pt});}
      o.sort(function(x,y){return (y.pt-x.pt)||(x.e[0]<y.e[0]?-1:1);});tutti=tutti.concat(o.slice(0,8)).slice(0,12);}
    return tutti;}
  function mostra(){out.innerHTML='';if(!q.value.trim()){out.hidden=true;return;}
    if(!indice){out.hidden=false;out.innerHTML='<li class="vuoto">Loading the code list…</li>';carica();return;}
    if(!frasi&&/[a-z]{2}/i.test(q.value))caricaFrasi();
    var ris=cerca(q.value);out.hidden=false;
    if(!ris.length){out.innerHTML='<li class="vuoto">No code found. Try another word (for example “bakery”, “software”, “plumbing”) or the first digits of a code.</li>';return;}
    ris.forEach(function(r){var e=r.e;var li=document.createElement('li');var a=document.createElement('a');a.href=e[2];var s=document.createElement('strong');s.textContent=e[0];
      var t=document.createElement('em');t.textContent=r.f?(e[1]+' — '+r.f):e[1];var sp=document.createElement('span');sp.textContent=e[4]||ETI[e[3]]||'';
      a.appendChild(s);a.appendChild(t);a.appendChild(sp);li.appendChild(a);out.appendChild(li);});}
  // two files: codes and titles on first focus (small); the official index entries of each 6-digit code (bigger) only when a word is typed,
  // so a search by code number never downloads them
  function carica(){if(attesa)return;attesa=true;fetch(q.getAttribute('data-indice')).then(function(r){return r.json();}).then(function(j){
      indice=j.map(function(e){e.c=cifre(e[0]);e.n=norm(e[0]+' '+e[1]);e.f=null;if(e[3]==='6')per[e[0]]=e;return e;});q.setAttribute('data-pronto','1');mostra();})
    .catch(function(){attesa=false;if(!indice)out.innerHTML='<li class="vuoto">The list could not be loaded: use the sector list below.</li>';});}
  function caricaFrasi(){if(frasi||!indice)return;frasi=1;fetch(q.getAttribute('data-frasi')).then(function(r){return r.json();}).then(function(fr){
      Object.keys(fr).forEach(function(c){var e=per[c];if(e){e[5]=fr[c];e.f=fr[c].split('|').map(norm);}});frasi=2;q.setAttribute('data-frasi-pronte','1');if(q.value.trim())mostra();})
    .catch(function(){frasi=0;});}
  q.addEventListener('input',mostra);q.addEventListener('focus',carica);
  var f=q.closest('form');if(f)f.addEventListener('submit',function(ev){ev.preventDefault();var a=out.querySelector('a');if(a)location.href=a.href;});}
// corrections form: sent without leaving the page
document.querySelectorAll('form[data-correzioni]').forEach(function(form){form.addEventListener('submit',function(ev){ev.preventDefault();
  var err=form.querySelector('[data-errore]');err.hidden=true;if(!form.checkValidity()){form.reportValidity();return;}
  var bt=form.querySelector('button');bt.disabled=true;
  fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(new FormData(form)).toString()})
    .then(function(r){if(!r.ok)throw new Error(r.status);form.hidden=true;var ok=form.parentNode.querySelector('[data-ok]');if(ok)ok.hidden=false;})
    .catch(function(){err.hidden=false;bt.disabled=false;});});});
// filterable tables, 100 rows at a time
document.querySelectorAll('[data-tabella]').forEach(function(box){
  var tb=box.querySelector('tbody');var righe=Array.prototype.slice.call(tb.rows);var fi=box.querySelector('[data-filtro]');
  var cnt=box.querySelector('[data-conteggio]');var vuoto=box.querySelector('[data-vuoto]');var altre=box.querySelector('[data-altre]');var lim=100;
  righe.forEach(function(r){r._t=norm(r.textContent);r._c=cifre(r.cells[0].textContent);});
  function filtra(){var v=fi?fi.value.trim():'';var dig=/^[0-9][0-9 ]*$/.test(v)?cifre(v):null;var p=dig?[]:norm(v).split(' ').filter(Boolean);var n=0;
    righe.forEach(function(r){var ok=dig?r._c.indexOf(dig)===0:true;for(var k=0;ok&&k<p.length;k++){if(r._t.indexOf(p[k])<0)ok=false;}if(ok)n++;r.hidden=!ok||n>lim;});
    var vis=Math.min(n,lim);if(cnt)cnt.textContent=(n===righe.length?(n+' codes'):(n+' of '+righe.length+' codes'))+(vis<n?' · showing '+vis:'');
    if(vuoto)vuoto.hidden=n>0;if(altre)altre.hidden=vis>=n;}
  if(altre){altre.querySelector('[data-altre-piu]').addEventListener('click',function(){lim+=100;filtra();});altre.querySelector('[data-altre-tutte]').addEventListener('click',function(){lim=Infinity;filtra();});}
  if(fi){fi.addEventListener('input',function(){if(lim!==Infinity)lim=100;filtra();});var u=new URLSearchParams(location.search).get('q');if(u){fi.value=u;}
    var h=location.hash;if(h&&/^#(v|sic)-/.test(h)){fi.value=decodeURIComponent(h.replace(/^#(v|sic)-/,''));}}
  filtra();
  if(location.hash){var el=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(el)el.scrollIntoView();}
});
})();
