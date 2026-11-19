function pagaMin(r,od){return {sett:Math.floor((r*od+5)/10),mese:Math.floor((r*od*52+60)/120),anno:Math.floor((r*od*52+5)/10)};}

(function(){
  var f=document.querySelector('[data-pay]');if(!f)return;
  var D=JSON.parse(document.getElementById('pay-dati').textContent),out=document.querySelector('[data-pay-out]');
  function gbp(p){return '£'+(p/100).toLocaleString('en-GB',{minimumFractionDigits:2,maximumFractionDigits:2});}
  function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function ore(v){v=String(v||'').trim().replace(/[\s,]/g,'');var m=/^(\d{1,3})(?:\.(\d))?$/.exec(v);if(!m)return NaN;
    var o=parseInt(m[1],10)*10+(m[2]?parseInt(m[2],10):0);return o>=10&&o<=1000?o:NaN;}
  function otxt(o){return (o/10).toLocaleString('en-GB',{maximumFractionDigits:1});}
  function calcola(){
    var o=ore(f.elements.h.value),a=D.fasce[f.elements.k.value];
    if(isNaN(o)||!a){out.innerHTML='<p class="ris-msg">'+esc(D.t.errore)+'</p>';return;}
    var p1=pagaMin(a[2],o),p0=pagaMin(a[1],o),d=p1.anno-p0.anno;
    var h='<div class="ris-main"><span>'+esc(D.t.titolo.replace('{h}',otxt(o)).replace('{r}',gbp(a[2])))+'</span><b data-pay-sett>'+esc(gbp(p1.sett))+'</b><span>'+esc(D.t.sett)+'</span></div>';
    h+='<ul class="mini due"><li><b data-pay-mese>'+esc(gbp(p1.mese))+'</b><span>'+esc(D.t.mese)+'</span></li><li><b data-pay-anno>'+esc(gbp(p1.anno))+'</b><span>'+esc(D.t.anno)+'</span></li>'+
      '<li><b data-pay-prima>'+esc(gbp(p0.anno))+'</b><span>'+esc(D.t.prima.replace('{r}',gbp(a[1])))+'</span></li><li><b data-pay-diff>'+esc(gbp(d))+'</b><span>'+esc(d>0?D.t.piu:D.t.uguale)+'</span></li></ul>';
    h+='<p class="small">'+esc(D.t.nota)+'</p>';
    out.innerHTML=h;}
  try{var q=new URLSearchParams(location.search);
    if(q.get('h'))f.elements.h.value=q.get('h').slice(0,6);
    if(q.get('k')&&D.fasce[q.get('k')])f.elements.k.value=q.get('k');}catch(e){}
  f.addEventListener('input',calcola);f.addEventListener('change',calcola);f.addEventListener('submit',function(e){e.preventDefault();calcola();});
  f.addEventListener('click',function(e){var b=e.target.closest('[data-h]');if(!b)return;f.elements.h.value=b.getAttribute('data-h');calcola();});
  calcola();
})();
