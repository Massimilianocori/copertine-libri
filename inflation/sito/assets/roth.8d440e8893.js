function rothLimite(y,stato,magiC,over50,compC,altreC){
  var L=(y.ira+(over50?y.cu:0))*100,base=(compC===null||compC===undefined)?L:Math.min(L,compC),lo,hi,W;
  if(stato==='mfj'){lo=y.mfj[0];hi=y.mfj[1];W=10000;}else if(stato==='mfs'){lo=y.mfs[0];hi=y.mfs[1];W=10000;}else{lo=y.single[0];hi=y.single[1];W=15000;}
  var l10=Math.max(0,base-(altreC||0)),esito,l8,num=null,den=null;
  if(magiC<=lo*100){esito='full';l8=base;}
  else if(magiC>=hi*100){esito='none';l8=0;}
  else{var Wc=W*100,d=magiC-lo*100;num=base*(Wc-d);den=Wc;l8=Math.ceil(num/(den*1000))*1000;if(l8>0&&l8<20000)l8=20000;esito='partial';}
  var lim=esito==='none'?0:Math.min(l8,l10);
  return {esito:esito,limite:lim,lo:lo,hi:hi,W:W,L:L,base:base,l8:l8,l10:l10};}

(function(){
  var f=document.querySelector('[data-roth]');if(!f)return;
  var D=JSON.parse(document.getElementById('roth-dati').textContent),out=document.querySelector('[data-roth-out]');
  function usd(c){return '$'+(c/100).toLocaleString('en-US',{minimumFractionDigits:c%100?2:0,maximumFractionDigits:2});}
  function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function cent(v){v=String(v||'').trim().replace(/[\s$,]/g,'');if(v==='')return null;var m=1;if(/k$/i.test(v)){m=1000;v=v.slice(0,-1);}
    if(!/^\d+(\.\d{0,2})?$/.test(v))return NaN;return Math.round(parseFloat(v)*m*100);}
  function calcola(){
    var anno=f.elements.y.value,y=D.anni[anno],stato=f.elements.s.value,magi=cent(f.elements.m.value),comp=cent(f.elements.c.value),altre=cent(f.elements.o.value),o50=f.elements.e.checked;
    if(magi===null||isNaN(magi)){out.innerHTML='<p class="ris-msg">'+esc(D.t.magi)+'</p>';return;}
    if(isNaN(comp)||isNaN(altre)){out.innerHTML='<p class="ris-msg">'+esc(D.t.importo)+'</p>';return;}
    var r=rothLimite(y,stato,magi,o50,comp,altre===null?0:altre),nome=D.stati[stato];
    var tit=r.esito==='full'?(r.limite<r.L?D.t.full_meno:D.t.full):(r.esito==='partial'?D.t.partial:D.t.none);
    var h='<div class="ris-main roth-'+r.esito+'"><span>'+esc(tit.replace('{anno}',anno))+'</span><b data-roth-limite>'+esc(usd(r.limite))+'</b><span>'+esc((altre?D.t.sotto_altre:D.t.sotto).replace('{anno}',anno))+'</span></div>';
    h+='<ul class="mini due"><li><b>'+esc(usd(r.lo*100))+' – '+esc(usd(r.hi*100))+'</b><span>'+esc(D.t.fascia.replace('{anno}',anno))+'</span></li>';
    h+='<li><b>'+esc(usd(r.L))+'</b><span>'+esc(o50?D.t.max50:D.t.max)+'</span></li></ul>';
    var righe=[['1',D.t.r1,usd(magi)],['2',D.t.r2,usd(r.lo*100)],['4',D.t.r4,usd(r.W*100)],['6',D.t.r6,usd(r.base)]];
    if(r.esito==='partial'){var rap=(magi-r.lo*100)/(r.W*100);righe.splice(2,0,['3',D.t.r3,usd(magi-r.lo*100)]);righe.push(['5',D.t.r5,rap.toFixed(4)]);righe.push(['8',D.t.r8,usd(r.l8)]);}
    righe.push(['10',D.t.r10,usd(r.l10)]);
    h+='<details class="foglio"><summary>'+esc(D.t.foglio)+'</summary><table class="dati"><tbody>'+righe.map(function(x){return '<tr><td>'+x[0]+'</td><td>'+esc(x[1])+'</td><td class="n">'+esc(x[2])+'</td></tr>';}).join('')+'</tbody></table></details>';
    h+='<p class="small">'+esc(nome)+'. '+esc(D.t.nota)+'</p>';
    out.innerHTML=h;}
  try{var q=new URLSearchParams(location.search);
    if(q.get('y')&&D.anni[q.get('y')])f.elements.y.value=q.get('y');
    if(q.get('s')&&D.stati[q.get('s')])f.elements.s.value=q.get('s');
    if(q.get('m'))f.elements.m.value=q.get('m').slice(0,14);}catch(e){}
  f.addEventListener('input',calcola);f.addEventListener('change',calcola);f.addEventListener('submit',function(e){e.preventDefault();calcola();});
  calcola();
})();
