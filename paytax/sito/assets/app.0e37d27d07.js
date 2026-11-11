var ORDINE=['nsw','vic','qld','wa','sa','tas','act','nt'];
function pos(x){return x>0?x:0;}
function calcolaStato(s,P,w,W,f,rv,rq){
  var p=P[s],o={s:s,w:w,stato:'ok',soglia:0,imponibile:0,aliquota:null,tassa:0,extra:0,avvisi:[]};
  if(!(w>0)){o.stato='zero';return o;}
  var q=w/W,d,al,extra,i,r;
  if(s==='nsw'){
    d=p.soglia*q*f;o.soglia=d;o.imponibile=pos(w-d);o.aliquota=p.aliquota/100;o.tassa=o.imponibile*o.aliquota;
  }else if(s==='vic'){
    var d1=p.soglia*f*q;
    if(W<=p.phase_da){d=d1;}
    else if(W<=p.phase_a){d=pos(d1-(w-p.phase_da*f*q)*(p.phase_quota/100));o.avvisi.push('vic_phase');}
    else{d=0;o.avvisi.push('vic_no_soglia');}
    o.soglia=d;o.imponibile=pos(w-d);o.aliquota=(rv?p.regionale:p.aliquota)/100;o.tassa=o.imponibile*o.aliquota;
    extra=0;for(i=0;i<p.sovrattasse.length;i++){extra+=pos(w-p.sovrattasse[i][0]*q*f)*(p.sovrattasse[i][1]/100);}
    o.extra=extra;if(extra>0)o.avvisi.push('vic_sovrattasse');
  }else if(s==='qld'){
    var kf=p.soglia*f,ad=pos(q*(kf-(W-kf)/p.rapporto));
    o.soglia=ad;o.imponibile=pos(w-ad);
    al=W<=p.aliquota_alta_da?p.aliquota:p.aliquota_alta;
    if(rq){if(W<=p.regionale_max){al=al-p.sconto_regionale;}else{o.avvisi.push('qld_regionale_oltre');}}
    o.aliquota=al/100;o.tassa=o.imponibile*o.aliquota;
    extra=0;for(i=0;i<p.levy.length;i++){extra+=pos(w-p.levy[i][0]*q*f)*(p.levy[i][1]/100);}
    o.extra=extra;if(extra>0)o.avvisi.push('qld_levy');
  }else if(s==='wa'){
    var aat=p.soglia*f,aut=p.soglia_superiore*f;o.aliquota=p.aliquota/100;
    if(W<=aat){o.soglia=w;o.imponibile=0;}
    else if(W>=aut){o.soglia=0;o.imponibile=w;o.avvisi.push('wa_no_soglia');}
    else{var tv=p.soglia/(p.soglia_superiore-p.soglia);d=(aat-(W-aat)*tv)*q;o.soglia=d;o.imponibile=pos(w-d);}
    o.tassa=o.imponibile*o.aliquota;
  }else if(s==='sa'){
    if(W<=p.soglia*f){o.soglia=w;}
    else{
      var tarw=W/f;
      if(tarw>p.piena_da){r=p.aliquota/100;}else{r=(tarw-p.soglia)/(p.piena_da-p.soglia)*(p.aliquota/100);}
      d=q*p.deduzione*f;o.soglia=d;o.imponibile=pos(w-d);o.aliquota=r;o.tassa=o.imponibile*r;
      if(tarw<=p.piena_da)o.avvisi.push('sa_variabile');
    }
  }else if(s==='tas'){
    var t1=p.soglia*f,t2=p.soglia2*f;
    if(W<=t1){o.soglia=w;}
    else if(W<=t2){o.soglia=q*t1;o.imponibile=pos(w-q*t1);o.aliquota=p.aliquota1/100;o.tassa=o.imponibile*o.aliquota;}
    else{o.soglia=q*t1;o.imponibile=pos(w-q*t1);o.aliquota=null;
      o.tassa=(t2-t1)*q*(p.aliquota1/100)+pos(w-q*t2)*(p.aliquota2/100);o.avvisi.push('tas_due_fasce');}
  }else if(s==='act'){
    var tac=p.soglia*f;
    if(W<=tac){o.soglia=w;}
    else if(W<=p.soglia){o.stato='non_calcolato';o.avvisi.push('act_anno_parziale');}
    else{
      r=null;for(i=0;i<p.scaglioni.length;i++){var lim=p.scaglioni[i][0];if(lim===null||W<=lim){r=p.scaglioni[i][1]/100;break;}}
      d=q*tac;o.soglia=d;o.imponibile=pos(w-d);o.aliquota=r;o.tassa=o.imponibile*r;o.avvisi.push('act_su_tutto');
    }
  }else if(s==='nt'){
    var eta=p.soglia*f;
    if(W<=eta){o.soglia=w;}
    else{
      ad=pos(eta-(W-eta)/2);r=(W>=p.aliquota_alta_da?p.aliquota_alta:p.aliquota)/100;
      o.soglia=q*ad;o.imponibile=pos(w-q*ad);o.aliquota=r;o.tassa=o.imponibile*r;if(ad===0)o.avvisi.push('nt_no_soglia');
    }
  }
  if(o.stato==='ok'&&o.tassa<=0&&o.extra<=0)o.stato='sotto';
  return o;
}
function calcola(P,salari,giorni,giorniAnno,rv,rq){
  var W=0,k;for(k in salari){if(Object.prototype.hasOwnProperty.call(salari,k)){var v=salari[k];W+=v>0?v:0;}}
  var g=Math.min(Math.max(giorni,1),giorniAnno),f=g/giorniAnno,righe=[],tot=0,extra=0,nc=[];
  for(var i=0;i<ORDINE.length;i++){var s=ORDINE[i],w=salari[s]||0;if(!(w>0))continue;
    var r=calcolaStato(s,P,w,W,f,rv,rq);righe.push(r);
    if(r.stato==='non_calcolato'){nc.push(s);}else{tot+=r.tassa;extra+=r.extra;}}
  return {W:W,f:f,righe:righe,totale:tot,extra:extra,complessivo:tot+extra,mensile:(tot+extra)/12,non_calcolati:nc};
}

(function(){
  var b=document.querySelector('[data-tema]');
  if(b)b.addEventListener('click',function(){var r=document.documentElement,c=r.getAttribute('data-theme');
    if(!c)c=window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
    var n=c==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('pt-theme',n);}catch(e){}});
  var f=document.querySelector('[data-calc]');if(!f)return;
  var D=JSON.parse(document.getElementById('calc-dati').textContent),P=D.parametri;
  var M0=new Intl.NumberFormat('en-AU',{style:'currency',currency:'AUD',maximumFractionDigits:0,minimumFractionDigits:0});
  function $(x){return M0.format(Math.round(x));}
  function pc(x){if(x===null||x===undefined)return '';var v=Math.round(x*1e6)/1e4;return (Math.round(v*10000)/10000).toString()+'%';}
  function num(v){v=String(v||'').trim().toLowerCase().replace(/[$,\s]/g,'').replace(/aud$/,'');var m=1;
    if(/k$/.test(v)){m=1e3;v=v.slice(0,-1);}else if(/(m|mil|million)$/.test(v)){m=1e6;v=v.replace(/(m|mil|million)$/,'');}else if(/(b|bn)$/.test(v)){m=1e9;v=v.replace(/(b|bn)$/,'');}
    var x=parseFloat(v);return isFinite(x)&&x>0?Math.round(x*m*100)/100:0;}
  function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  var campi=D.campi,out=f.querySelector('[data-out]'),ant=f.querySelector('[data-anteprima]'),ultimo=null;
  function leggi(){var s={};campi.forEach(function(c){var e=f.elements[c];if(e)s[c]=num(e.value);});
    var g=parseInt(f.elements.giorni.value,10);if(!(g>=1))g=D.giorni_anno;if(g>D.giorni_anno)g=D.giorni_anno;
    return {salari:s,giorni:g,rv:!!(f.elements.rv&&f.elements.rv.checked),rq:!!(f.elements.rq&&f.elements.rq.checked),gruppo:!!(f.elements.gruppo&&f.elements.gruppo.value==='si')};}
  function spiega(r,res){var q=r.w/res.W,fr=res.f,p=P[r.s],sh=(q*100).toFixed(q<0.1?2:1)+'% of Australian wages',dy=Math.round(fr*D.giorni_anno)+'/'+D.giorni_anno+' days';
    if(r.stato==='non_calcolato')return D.testi.act_anno_parziale;
    if(r.stato==='sotto')return 'Total Australian wages are not above the '+D.nomi[r.s]+' threshold for the days you employed.';
    switch(r.s){
      case 'nsw':return '$1,200,000 × '+sh+' × '+dy+' = '+$(r.soglia)+'; tax = ('+$(r.w)+' − '+$(r.soglia)+') × 5.45%';
      case 'vic':return (res.W<=p.phase_da?'$1,000,000 × '+sh+' × '+dy:res.W<=p.phase_a?'Phased-out threshold (50%) between $3m and $5m':'No threshold above $5m')+' = '+$(r.soglia)+'; tax at '+pc(r.aliquota)+(r.extra>0?'; surcharges '+$(r.extra):'');
      case 'qld':return 'Deduction = '+sh+' × ($1.3m × '+dy+' − excess ÷ 7) = '+$(r.soglia)+'; rate '+pc(r.aliquota)+(r.extra>0?'; mental health levy '+$(r.extra):'');
      case 'wa':return r.soglia>0?'Diminishing threshold (2/13 taper) × '+sh+' = '+$(r.soglia)+'; tax at 5.5%':'No deductable amount at $7.5m or more; 5.5% on all WA wages';
      case 'sa':return 'Deduction = $600,000 × '+sh+' × '+dy+' = '+$(r.soglia)+'; rate '+pc(r.aliquota)+(r.aliquota<0.0495?' (variable band)':'');
      case 'tas':return 'Thresholds $1.25m and $2m × '+sh+' × '+dy+'; '+(r.aliquota===null?'4% on the band, 6.1% above':'4% above the lower threshold');
      case 'act':return '$1,750,000 × '+sh+' × '+dy+' = '+$(r.soglia)+'; '+pc(r.aliquota)+' (bracket set by total wages) on all ACT wages above it';
      case 'nt':return 'Deduction = '+sh+' × ($2.5m × '+dy+' − half the excess) = '+$(r.soglia)+'; rate '+pc(r.aliquota);
    }return '';}
  function render(){
    var v=leggi(),res=calcola(P,v.salari,v.giorni,D.giorni_anno,v.rv,v.rq);ultimo={v:v,res:res};
    if(!res.righe.length){out.innerHTML='<div class="vuoto">'+D.vuoto_html+'</div>';if(ant)ant.textContent=D.testi.vuoto;aggiornaUrl(v);return;}
    var h='<div class="tot"><div class="main"><span>Estimated payroll tax, '+D.anno+'</span><b>'+$(res.complessivo)+'</b></div>'+
      '<div class="mensile"><span>Monthly average</span><b>'+$(res.mensile)+'</b></div>'+
      '<div><span>Total Australian wages</span><b>'+$(res.W)+'</b></div>'+
      '<div><span>Share of wages</span><b>'+(res.W>0?(Math.round(res.complessivo/res.W*10000)/100).toFixed(2):'0.00')+'%</b></div></div>';
    h+='<table class="ris"><thead><tr><th scope="col">State</th><th scope="col" class="col-w">Wages</th><th scope="col">Threshold used</th><th scope="col">Rate</th><th scope="col">Tax</th></tr></thead><tbody>';
    var avv={};
    res.righe.forEach(function(r){
      r.avvisi.forEach(function(a){avv[a]=1;});
      var nome='<a href="/'+r.s+'/">'+D.brevi[r.s]+'</a>';
      if(r.stato==='non_calcolato'){h+='<tr class="has-sp"><td class="st">'+nome+'</td><td class="col-w">'+$(r.w)+'</td><td colspan="3">not calculated</td></tr><tr class="sp"><td colspan="5">'+esc(spiega(r,res))+'</td></tr>';return;}
      var rate=r.aliquota===null?(r.stato==='sotto'?'–':'4% / 6.1%'):pc(r.aliquota);
      h+='<tr class="has-sp"><td class="st">'+nome+'</td><td class="col-w">'+$(r.w)+'</td><td>'+$(r.soglia)+'</td><td>'+rate+'</td><td'+(r.stato==='sotto'?' class="zero"':'')+'>'+$(r.tassa)+'</td></tr>';
      h+='<tr class="sp"><td colspan="5">'+esc(spiega(r,res))+'</td></tr>';
      if(r.extra>0)h+='<tr class="extra"><td colspan="4">'+(r.s==='qld'?'Queensland mental health levy':'Victorian surcharges (mental health + COVID-19 debt)')+'</td><td>'+$(r.extra)+'</td></tr>';
    });
    h+='</tbody><tfoot><tr><td>Total</td><td class="col-w">'+$(res.W)+'</td><td></td><td></td><td>'+$(res.complessivo)+'</td></tr></tfoot></table>';
    var L=[];Object.keys(avv).forEach(function(a){if(D.testi[a])L.push('<li'+(a==='act_anno_parziale'?' class="forte"':'')+'>'+D.testi[a]+'</li>');});
    if(v.gruppo)L.push('<li>'+D.testi.gruppo+'</li>');
    if(v.giorni<D.giorni_anno)L.push('<li>'+D.testi.parziale+'</li>');
    if(v.salari.altro>0)L.push('<li>'+D.testi.altro+'</li>');
    L.push('<li>'+D.testi.stima+'</li>');
    h+='<ul class="avvisi">'+L.join('')+'</ul>';
    out.innerHTML=h;
    if(ant)ant.innerHTML='Estimated payroll tax: <b>'+$(res.complessivo)+'</b> · <a href="#'+out.id+'">see the breakdown</a>';
    var aff=document.querySelector('[data-aff-calc]');if(aff)aff.hidden=!(res.complessivo>0);
    aggiornaUrl(v);
  }
  function aggiornaUrl(v){if(!D.url_stato)return;try{var u=new URLSearchParams();campi.forEach(function(c){if(v.salari[c]>0)u.set(c,String(v.salari[c]));});
    if(v.giorni<D.giorni_anno)u.set('d',String(v.giorni));if(v.rv)u.set('rv','1');if(v.rq)u.set('rq','1');if(v.gruppo)u.set('g','1');
    var s=u.toString();history.replaceState(null,'',location.pathname+(s?'?'+s:'')+location.hash);}catch(e){}}
  function daUrl(){try{var u=new URLSearchParams(location.search),c=false;campi.forEach(function(k){if(u.has(k)&&f.elements[k]){f.elements[k].value=Number(num(u.get(k))).toLocaleString('en-AU');c=true;}});
    if(c){campi.forEach(function(k){if(!u.has(k)&&f.elements[k])f.elements[k].value='';});}
    if(u.has('d'))f.elements.giorni.value=u.get('d');if(u.get('rv')==='1'&&f.elements.rv)f.elements.rv.checked=true;if(u.get('rq')==='1'&&f.elements.rq)f.elements.rq.checked=true;
    if(u.get('g')==='1'&&f.elements.gruppo)f.elements.gruppo.value='si';}catch(e){}}
  function testo(){if(!ultimo)return '';var r=ultimo.res,v=ultimo.v,t=['Payroll tax estimate '+D.anno+' ('+location.host+')','Total Australian wages: '+$(r.W)+'; days paid: '+v.giorni+'/'+D.giorni_anno];
    r.righe.forEach(function(x){t.push(D.brevi[x.s]+': wages '+$(x.w)+(x.stato==='non_calcolato'?' – not calculated (see the ACT Revenue Office)':', threshold used '+$(x.soglia)+', tax '+$(x.tassa)+(x.extra>0?' + '+$(x.extra)+(x.s==='qld'?' mental health levy':' surcharges'):'')));});
    t.push('Total: '+$(r.complessivo)+' (monthly average '+$(r.mensile)+')');t.push('Estimate only, not tax advice. Formulas and sources: '+location.origin+'/how-we-check/');return t.join('\n');}
  function copia(txt,bt){var ok=function(){var o=bt.textContent;bt.textContent='Copied';setTimeout(function(){bt.textContent=o;},1600);};
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(txt).then(ok,function(){fallback(txt);ok();});}else{fallback(txt);ok();}}
  function fallback(txt){var a=document.createElement('textarea');a.value=txt;a.setAttribute('readonly','');a.style.position='absolute';a.style.left='-9999px';document.body.appendChild(a);a.select();try{document.execCommand('copy');}catch(e){}document.body.removeChild(a);}
  f.addEventListener('input',render);f.addEventListener('change',render);f.addEventListener('submit',function(e){e.preventDefault();render();});
  f.querySelectorAll('input[data-soldi]').forEach(function(i){i.addEventListener('blur',function(){var x=num(i.value);i.value=x>0?x.toLocaleString('en-AU'):'';});});
  var bc=f.querySelector('[data-copia]');if(bc)bc.addEventListener('click',function(){copia(testo(),bc);});
  var bl=f.querySelector('[data-link]');if(bl)bl.addEventListener('click',function(){copia(location.href,bl);});
  var br=f.querySelector('[data-azzera]');if(br)br.addEventListener('click',function(){campi.forEach(function(c){if(f.elements[c])f.elements[c].value='';});f.elements.giorni.value=D.giorni_anno;
    if(f.elements.rv)f.elements.rv.checked=false;if(f.elements.rq)f.elements.rq.checked=false;if(f.elements.gruppo)f.elements.gruppo.value='no';render();var p=f.querySelector('input[data-soldi]');if(p)p.focus();});
  daUrl();render();
})();
