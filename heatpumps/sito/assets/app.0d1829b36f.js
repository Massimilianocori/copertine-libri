(function(){
'use strict';
var b=document.querySelector('[data-tema]');
if(b){b.addEventListener('click',function(){var r=document.documentElement;var dark=r.getAttribute('data-theme')==='dark'||(!r.getAttribute('data-theme')&&window.matchMedia('(prefers-color-scheme: dark)').matches);var t=dark?'light':'dark';r.setAttribute('data-theme',t);try{localStorage.setItem('hp-tema',t);}catch(e){}});}
function norm(s){return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9 ]+/g,' ').replace(/\s+/g,' ').trim();}
document.querySelectorAll('[data-cerca]').forEach(function(q){
  var dove=document.getElementById(q.getAttribute('data-cerca'));if(!dove)return;
  var righe=Array.prototype.slice.call(dove.querySelectorAll('[data-riga]'));var vuoto=dove.querySelector('[data-vuoto]');
  q.addEventListener('input',function(){var parole=norm(q.value).split(' ').filter(Boolean);var n=0;
    righe.forEach(function(r){var t=norm(r.getAttribute('data-riga'));var ok=parole.every(function(p){return t.indexOf(p)>=0;});r.hidden=!ok;if(ok)n++;});
    if(vuoto)vuoto.hidden=n>0;});
});
})();
