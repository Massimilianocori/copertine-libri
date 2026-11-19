function costoPieno(gd,mill){return Math.floor((gd*mill+50)/100);}

(function(){
  var f=document.querySelector('[data-tank]');if(!f)return;
  var D=JSON.parse(document.getElementById('tank-dati').textContent),out=document.querySelector('[data-tank-out]');
  function usd(c){return '$'+(c/100).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});}
  function p3(m){return '$'+(m/1000).toFixed(3);}
  function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function gal(v){v=String(v||'').trim().replace(/[\s,]/g,'');var m=/^(\d{1,5})(?:\.(\d))?$/.exec(v);if(!m)return NaN;
    var g=parseInt(m[1],10)*10+(m[2]?parseInt(m[2],10):0);return g>=10&&g<=100000?g:NaN;}
  function gtxt(g){return (g/10).toLocaleString('en-US',{maximumFractionDigits:1});}
  function calcola(){
    var g=gal(f.elements.g.value),a=D.aree[f.elements.s.value];
    if(isNaN(g)||!a){out.innerHTML='<p class="ris-msg">'+esc(D.t.errore)+'</p>';return;}
    var c=costoPieno(g,a[1]),G=gtxt(g);
    var h='<div class="ris-main"><span>'+esc(D.t.titolo.replace('{g}',G).replace('{area}',a[0]))+'</span><b data-tank-costo>'+esc(usd(c))+'</b><span>'+
      esc(D.t.sotto.replace('{p}',p3(a[1])).replace('{data}',a[2]))+'</span></div>';
    h+='<p class="formula">'+esc(G+' gallons × '+p3(a[1])+' = '+usd(c))+'</p>';
    if(a[3]){var c0=costoPieno(g,a[3]),d=c-c0;
      h+='<ul class="mini due"><li><b data-tank-prima>'+esc(usd(c0))+'</b><span>'+esc(D.t.prima.replace('{p}',p3(a[3])).replace('{data}',a[4]))+'</span></li>'+
        '<li><b>'+esc(usd(Math.abs(d)))+'</b><span>'+esc(d>0?D.t.piu:(d<0?D.t.meno:D.t.uguale))+'</span></li></ul>';}
    h+='<p class="small">'+esc(D.t.nota)+'</p>';
    out.innerHTML=h;}
  try{var q=new URLSearchParams(location.search);
    if(q.get('g'))f.elements.g.value=q.get('g').slice(0,8);
    if(q.get('s')&&D.aree[q.get('s')])f.elements.s.value=q.get('s');}catch(e){}
  f.addEventListener('input',calcola);f.addEventListener('change',calcola);f.addEventListener('submit',function(e){e.preventDefault();calcola();});
  f.addEventListener('click',function(e){var b=e.target.closest('[data-g]');if(!b)return;f.elements.g.value=b.getAttribute('data-g');calcola();});
  calcola();
})();
