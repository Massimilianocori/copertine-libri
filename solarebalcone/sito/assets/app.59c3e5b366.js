function calcola(ey,w,quota,prezzo,kit){var prod=ey*w/800,auto=prod*quota/100,eur=auto*prezzo;
  return {prod:prod,auto:auto,eur:eur,anni:(eur>0&&kit>0)?kit/eur:null};}
function fmt(x,d,lang){d=d||0;var p=Math.pow(10,d),r=Math.floor(x*p+0.5)/p,l=String(lang||'it').slice(0,2),s=Math.abs(r).toFixed(d).split('.'),i=s[0];
  i=i.replace(/\B(?=(\d{3})+(?!\d))/g,l==='fr'?'\u202f':'.');
  return (r<0?'-':'')+i+(s[1]?','+s[1]:'');}

(function(){
  var b=document.querySelector('[data-tema]');
  if(b)b.addEventListener('click',function(){var r=document.documentElement,c=r.getAttribute('data-theme');
    if(!c)c=window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
    var n=c==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('sb-theme',n);}catch(e){}});
  var ref='';try{ref=new URLSearchParams(location.search).get('ref')||document.referrer||'direct';}catch(e){ref='direct';}
  document.querySelectorAll('input[name=source]').forEach(function(i){i.value=String(ref).slice(0,200);});
  document.querySelectorAll('form.ajax').forEach(function(form){form.addEventListener('submit',function(ev){ev.preventDefault();
    var err=form.querySelector('[data-errore]');err.hidden=true;if(!form.checkValidity()){form.reportValidity();return;}
    var bt=form.querySelector('button');bt.disabled=true;
    fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(new FormData(form)).toString()})
    .then(function(r){if(!r.ok)throw new Error(r.status);form.hidden=true;form.parentNode.querySelector('[data-ok]').hidden=false;})
    .catch(function(){err.hidden=false;bt.disabled=false;});});});
  var f=document.querySelector('[data-calc]');if(!f)return;
  var D=JSON.parse(document.getElementById('calc-dati').textContent),L=document.documentElement.lang||'it';
  function n(x,d){return fmt(x,d,L);}
  function v(name){var e=f.elements[name];return e?parseFloat(String(e.value).replace(',','.')):NaN;}
  function out(k,t){var e=f.querySelector('[data-o='+k+']');if(e)e.textContent=t;}
  function aggiorna(){
    var c=D.citta.filter(function(x){return x.s===f.elements.citta.value;})[0]||D.citta[0];
    var m=f.querySelector('input[name=mont]:checked').value,w=v('w'),q=v('quota'),p=v('prezzo'),k=v('kit');
    if(!(w>0))w=0;if(!(q>=0))q=0;if(!(p>=0))p=0;if(!(k>=0))k=0;
    var r=calcola(c[m],w,q,p,k);
    out('prod',n(r.prod));out('auto',n(r.auto));out('eur',n(r.eur));
    out('anni',r.anni===null?'–':n(r.anni,1));out('quota',n(q)+' %');
    var mesi=c[m==='a35'?'m35':'m90'],max=Math.max.apply(null,c.m35.concat(c.m90));
    f.querySelectorAll('.barre li').forEach(function(li,i){var val=mesi[i]*w/800;li.style.height=Math.max(2,Math.round(mesi[i]/max*100))+'%';
      li.title=D.mesi[i]+': '+n(val)+' kWh';});
    var av=f.querySelector('[data-oltre]');if(av)av.hidden=!(w>D.soglia);
  }
  f.addEventListener('input',aggiorna);f.addEventListener('change',aggiorna);f.addEventListener('submit',function(e){e.preventDefault();});
  aggiorna();
})();
