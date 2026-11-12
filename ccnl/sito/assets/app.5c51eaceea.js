(function(){
'use strict';
function eur(cent){var s=(Math.abs(cent)/100).toFixed(2).split('.');var i=s[0].replace(/\B(?=(\d{3})+(?!\d))/g,'.');return (cent<0?'-':'')+i+','+s[1]+' €';}
// mezzo su su interi: round(n/d) con n,d >= 0
function divArr(n,d){return Math.floor((2*n+d)/(2*d));}
function prorata(cent,ore,oreNorm){return divArr(cent*ore,oreNorm);}
function orario52(centOra,ore){return divArr(centOra*ore*52,12);}
window.PagaCCNL={prorata:prorata,orario52:orario52,eur:eur};
// tema
var b=document.querySelector('[data-tema]');
if(b){b.addEventListener('click',function(){var r=document.documentElement;var dark=r.getAttribute('data-theme')==='dark'||(!r.getAttribute('data-theme')&&window.matchMedia('(prefers-color-scheme: dark)').matches);var t=dark?'light':'dark';r.setAttribute('data-theme',t);try{localStorage.setItem('pc-tema',t);}catch(e){}});}
// calcolo in pagina
document.querySelectorAll('[data-calc]').forEach(function(box){
  var modo=box.getAttribute('data-modo');var cent=parseInt(box.getAttribute('data-cent'),10);var oreNorm=parseInt(box.getAttribute('data-ore-normali'),10);
  var mens=parseInt(box.getAttribute('data-mensilita'),10);var inp=box.querySelector('input[name=ore]');var out=box.querySelector('[data-out]');var outA=box.querySelector('[data-out-annuo]');
  var maxOre=parseInt(inp.getAttribute('max'),10);
  function aggiorna(){var ore=parseInt(inp.value,10);
    box.querySelectorAll('.chips button').forEach(function(x){x.setAttribute('aria-pressed',String(parseInt(x.getAttribute('data-ore'),10)===ore));});
    if(!(ore>=1&&ore<=maxOre)){out.textContent='—';if(outA)outA.textContent='—';return;}
    var m=modo==='orario52'?orario52(cent,ore):prorata(cent,ore,oreNorm);
    out.textContent=eur(m);if(outA)outA.textContent=eur(m*mens);}
  inp.addEventListener('input',aggiorna);
  box.querySelectorAll('.chips button').forEach(function(x){x.addEventListener('click',function(){inp.value=x.getAttribute('data-ore');aggiorna();});});
  aggiorna();
});
// ricerca nella tabella della home
var q=document.querySelector('[data-cerca]');
if(q){var righe=Array.prototype.slice.call(document.querySelectorAll('[data-riga]'));var vuoto=document.querySelector('[data-vuoto]');
  function norm(s){return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/°/g,' ').replace(/\s+/g,' ').trim();}
  q.addEventListener('input',function(){var parole=norm(q.value).split(' ').filter(Boolean);var n=0;
    righe.forEach(function(r){var t=norm(r.getAttribute('data-riga'));var ok=parole.every(function(p){return t.indexOf(p)>=0;});r.hidden=!ok;if(ok)n++;});
    document.querySelectorAll('[data-blocco]').forEach(function(bl){bl.hidden=!bl.querySelector('[data-riga]:not([hidden])');});
    if(vuoto)vuoto.hidden=n>0;});}
})();
