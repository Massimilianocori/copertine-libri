function affittoMax(c,t){var a=Math.floor(c*t/100000);return {aumento:a,nuovo:c+a};}

(function(){
  var f=document.querySelector('[data-rent]');if(!f)return;
  var D=JSON.parse(document.getElementById('rent-dati').textContent),out=document.querySelector('[data-rent-out]');
  function soldi(c){return '$'+(c/100).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});}
  function pc(t){return (t/1000).toLocaleString('en-US',{maximumFractionDigits:3})+'%';}
  function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function cent(v){v=String(v||'').trim().replace(/[\s$,]/g,'');if(!/^\d{1,7}(\.\d{1,2})?$/.test(v))return NaN;
    var p=v.split('.'),c=parseInt(p[0],10)*100+(p[1]?parseInt((p[1]+'0').slice(0,2),10):0);return c>=100&&c<=100000000?c:NaN;}
  function periodi(tieni){var v=D.voci[f.elements.v.value],s=f.elements.p,i,prima=tieni?s.value:null;
    s.innerHTML='';for(i=0;i<v.p.length;i++){var o=document.createElement('option');o.value=String(i);o.textContent=v.p[i][0];s.appendChild(o);}
    s.value=(prima!==null&&prima<v.p.length)?prima:String(v.d);}
  function calcola(){
    var v=D.voci[f.elements.v.value],c=cent(f.elements.r.value);
    if(!v){return;}
    var p=v.p[parseInt(f.elements.p.value,10)]||v.p[v.d];
    if(isNaN(c)){out.innerHTML='<p class="ris-msg">'+esc(D.t.errore)+'</p>';return;}
    var r=affittoMax(c,p[1]);
    var h='<div class="ris-main"><span>'+esc(D.t.titolo.replace('{luogo}',v.n))+'</span><b data-rent-nuovo>'+esc(soldi(r.nuovo))+'</b><span>'+
      esc((p[1]?D.t.sotto:D.t.zero).replace('{pct}',pc(p[1])).replace('{periodo}',p[0]).replace('{valuta}',v.c))+'</span></div>';
    h+='<p class="formula">'+esc(soldi(c)+' × '+pc(p[1])+' = '+soldi(r.aumento)+' · '+soldi(c)+' + '+soldi(r.aumento)+' = '+soldi(r.nuovo))+'</p>';
    h+='<ul class="mini due"><li><b data-rent-aumento>'+esc(soldi(r.aumento))+'</b><span>'+esc(D.t.aumento)+'</span></li><li><b data-rent-pct>'+esc(pc(p[1]))+'</b><span>'+esc(D.t.fonte.replace('{fonte}',v.f))+'</span></li></ul>';
    h+='<p class="small">'+esc(D.t.nota)+'</p>';
    out.innerHTML=h;}
  try{var q=new URLSearchParams(location.search);
    if(q.get('v')&&D.voci[q.get('v')])f.elements.v.value=q.get('v');
    periodi(false);
    if(q.get('r'))f.elements.r.value=q.get('r').slice(0,12);}catch(e){periodi(false);}
  f.elements.v.addEventListener('change',function(){periodi(false);});
  f.addEventListener('input',calcola);f.addEventListener('change',calcola);f.addEventListener('submit',function(e){e.preventDefault();calcola();});
  calcola();
})();
