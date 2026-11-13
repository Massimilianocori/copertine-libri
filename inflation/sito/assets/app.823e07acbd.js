var DM_PER_EURO=1.95583,ANNO_EURO=2002;
function indice(c,anno,mese){var i;
  if(mese){i=(anno-c.m0[0])*12+(mese-c.m0[1]);return (i>=0&&i<c.m.length)?c.m[i]:null;}
  i=anno-c.a0;return (i>=0&&i<c.a.length)?c.a[i]:null;}
function fattoreValuta(daAnno,aAnno,inDm){var daDm=inDm&&daAnno<ANNO_EURO,aDm=aAnno<ANNO_EURO;
  if(daDm&&!aDm)return 1/DM_PER_EURO;if(!daDm&&aDm)return DM_PER_EURO;return 1.0;}
function calcola(c,importo,da,a,valuta){
  var i0=indice(c,da[0],da[1]),i1=indice(c,a[0],a[1]);
  if(!i0||!i1||importo===null||importo===undefined||!(importo>=0))return null;
  var f=(valuta===null||valuta===undefined)?1.0:fattoreValuta(da[0],a[0],valuta);
  var t0=da[0]+(da[1]?(da[1]-0.5)/12:0.5),t1=a[0]+(a[1]?(a[1]-0.5)/12:0.5),anni=t1-t0,r=i1/i0;
  var media=Math.abs(anni)>=1?Math.pow(r,1/anni)-1:null;
  return {valore:importo*r*f,i0:i0,i1:i1,rapporto:r,cumulata:r-1,media:media,anni:anni,fattore_valuta:f};}

(function(){
  var b=document.querySelector('[data-tema]');
  if(b)b.addEventListener('click',function(){var r=document.documentElement,c=r.getAttribute('data-theme');
    if(!c)c=window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
    var n=c==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('ic-theme',n);}catch(e){}});
  var box=document.querySelector('[data-calc]');if(!box)return;
  var D=JSON.parse(document.getElementById('calc-dati').textContent),T=D.t,f=box.querySelector('form'),out=box.querySelector('[data-out]'),nota=box.querySelector('[data-nota]');
  var fissa=D.fisso||null;
  function fmt(x,val){var cur=val||D.valuta;try{return new Intl.NumberFormat(D.locale,{style:'currency',currency:cur,minimumFractionDigits:2,maximumFractionDigits:2}).format(x).replace('DEM','DM');}catch(e){return cur+' '+x.toFixed(2);}}
  function num(x,d){return new Intl.NumberFormat(D.locale,{minimumFractionDigits:d,maximumFractionDigits:d}).format(x);}
  var DE=D.locale.indexOf('de')===0;
  function pc(x,d){d=d===undefined?1:d;var z=parseFloat(Math.abs(x*100).toFixed(d))===0;return (z?'':(x>=0?'+':'\u2212'))+num(Math.abs(x*100),d)+(DE?'\u00a0%':'%');}
  function dec(x){var s=String(x),i=s.indexOf('.');return i<0?1:Math.max(1,Math.min(3,s.length-i-1));}
  function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function parseImporto(v){v=String(v||'').trim().toLowerCase().replace(/[\s$£€]/g,'').replace(/^(usd|gbp|eur|dm)|(usd|gbp|eur|dm)$/g,'');var m=1;
    if(/k$/.test(v)){m=1e3;v=v.slice(0,-1);}else if(/(m|mio|mn|million)$/.test(v)){m=1e6;v=v.replace(/(m|mio|mn|million)$/,'');}
    if(DE){if(/,\d{1,2}$/.test(v)||(/\./.test(v)&&!/\.\d{1,2}$/.test(v)))v=v.replace(/\./g,'').replace(',','.');else v=v.replace(/,/g,'');}
    else{v=v.replace(/,/g,'');}
    var x=parseFloat(v);return isFinite(x)&&x>=0?x*m:null;}
  function serie(){var s=f.elements.s?f.elements.s.value:D.serie_def;return D.serie[s];}
  function nomeMese(m){return T.mesi[m-1];}
  function etichetta(y,m){return m?nomeMese(m)+' '+y:String(y)+(T.media_suffix?' '+T.media_suffix:'');}
  function aggiornaMesi(sel,ySel,c){var y=parseInt(ySel.value,10),cur=sel.value,ok=[];
    for(var i=0;i<sel.options.length;i++){var o=sel.options[i],m=o.value?parseInt(o.value,10):0,v=indice(c,y,m||undefined);
      var x=c.x&&m?c.x[y+'-'+(m<10?'0':'')+m]:null;o.disabled=!v;o.title=x||'';if(v)ok.push(o.value);}
    if(ok.indexOf(cur)<0){sel.value=ok.indexOf('')>=0?'':(ok.length?ok[ok.length-1]:'');}}
  function legge(){var c=serie(),fy=parseInt(f.elements.fy.value,10),ty=parseInt(f.elements.ty.value,10);
    var fm=f.elements.fm.value?parseInt(f.elements.fm.value,10):0,tm=f.elements.tm.value?parseInt(f.elements.tm.value,10):0;
    var val=null;if(D.dm){val=fy<ANNO_EURO?(f.elements.c&&f.elements.c.value==='eur'?false:true):false;}
    return {c:c,a:parseImporto(f.elements.a.value),da:[fy,fm||undefined],aa:[ty,tm||undefined],val:val};}
  var autoDa=null;
  function controllaSerie(ev){if(!f.elements.s)return;var mn=Math.min(parseInt(f.elements.fy.value,10),parseInt(f.elements.ty.value,10));
    if(ev&&ev.target===f.elements.s)autoDa=null;
    var s=f.elements.s.value,c=D.serie[s],alt=D.serie_alt[s];
    if(mn<c.a0&&alt){f.elements.s.value=alt;autoDa=s;}
    else if(autoDa&&mn>=D.serie[autoDa].a0){f.elements.s.value=autoDa;autoDa=null;}
    nota.hidden=!autoDa;if(autoDa)nota.textContent=T.cambio_serie;}
  function avvisoSerie(){if(!D.avviso)return;var mn=Math.min(parseInt(f.elements.fy.value,10),parseInt(f.elements.ty.value,10));
    nota.hidden=!(mn<D.avviso.prima);if(!nota.hidden)nota.textContent=D.avviso.testo;}
  function tacche(mn,mx){var span=(mx-mn)||Math.abs(mx)||1,bs=[1,2,2.5,5,10],p,a,b;
    for(var i=0;i<bs.length;i++){p=bs[i]*Math.pow(10,Math.floor(Math.log10(span/4)));a=Math.floor(mn/p+1e-9)*p;b=Math.ceil(mx/p-1e-9)*p;if((b-a)/p<=5.0001)break;}
    var n=Math.round((b-a)/p),o=[];for(var j=0;j<=n;j++)o.push(a+p*j);return o;}
  function grafico(c,ris,st){var pts=[],y0=st.da[0],y1=st.aa[0];if(y1-y0<2)return '';
    for(var y=y0;y<=y1;y++){var i=y===y0?ris.i0:(y===y1?ris.i1:indice(c,y));
      if(i)pts.push([y,st.a*i/ris.i0*ris.fattore_valuta]);}
    if(pts.length<3)return '';var mx=0,mn=0;pts.forEach(function(p){mx=Math.max(mx,p[1]);mn=Math.min(mn,p[1]);});var tk=tacche(mn,mx);mn=tk[0];mx=tk[tk.length-1];
    var vOut=D.dm?(y1<ANNO_EURO?'DEM':'EUR'):D.valuta;
    var sx=function(x){return (x-y0)/(y1-y0)*1000;},sy=function(v){return (1-(v-mn)/((mx-mn)||1))*300;};
    var d=pts.map(function(p,i){return (i?'L':'M')+sx(p[0]).toFixed(1)+' '+sy(p[1]).toFixed(1);}).join(' ');
    var g='<figure class="graf" role="img" aria-label="'+esc(T.grafico_aria)+'"><div class="graf-area"><svg viewBox="0 0 1000 300" preserveAspectRatio="none" aria-hidden="true">',lab='';
    for(var k=0;k<tk.length;k++){var v=tk[k],yy=sy(v);g+='<line class="gr" x1="0" x2="1000" y1="'+yy.toFixed(1)+'" y2="'+yy.toFixed(1)+'"/>';
      lab+='<span class="gy" style="top:'+(yy/3).toFixed(1)+'%">'+esc(fmt(v,vOut).replace(/[.,]\d\d(?=\D*$)/,''))+'</span>';}
    g+='<path class="area" d="'+d+' L1000 300 L0 300 Z"/><path class="lin" d="'+d+'"/></svg>'+lab;
    g+='<span class="gx first" style="left:0">'+y0+'</span><span class="gx last" style="left:100%">'+y1+'</span></div></figure>';return g;}
  function calcolaUi(ev){controllaSerie(ev);avvisoSerie();var c=serie();aggiornaMesi(f.elements.fm,f.elements.fy,c);aggiornaMesi(f.elements.tm,f.elements.ty,c);
    var st=legge();if(D.dm){var vb=box.querySelector('[data-valuta]');if(vb)vb.hidden=!(st.da[0]<ANNO_EURO);}
    var sym=box.querySelector('[data-sym]');if(sym&&D.dm)sym.setAttribute('data-sym',st.val?'DM':'€');
    if(st.a===null){out.innerHTML='<p>'+esc(T.importo_errato)+'</p>';return;}
    var r=calcola(st.c,st.a,st.da,st.aa,st.val);if(!r){out.innerHTML='<p>'+esc(T.manca)+'</p>';return;}
    var vIn=D.dm?(st.val?'DEM':'EUR'):D.valuta,vOut=D.dm?(st.aa[0]<ANNO_EURO?'DEM':'EUR'):D.valuta;
    var daE=etichetta(st.da[0],st.da[1]),aE=etichetta(st.aa[0],st.aa[1]);
    var h='<div class="ris-main"><span>'+esc(T.vale.replace('{importo}',fmt(st.a,vIn)).replace('{da}',daE))+'</span><b data-valore>'+esc(fmt(r.valore,vOut))+'</b><span>'+esc(T.in_.replace('{a}',aE))+'</span></div>';
    h+='<ul class="mini"><li><b>'+esc(pc(r.cumulata))+'</b><span>'+esc(r.cumulata>=0?T.cumulata:T.cumulata_neg)+'</span></li>';
    h+='<li><b>'+(r.media===null?'–':esc(pc(r.media,2)))+'</b><span>'+esc(T.media)+'</span></li>';
    h+='<li><b>'+esc(num(r.i0,dec(r.i0))+' → '+num(r.i1,dec(r.i1)))+'</b><span>'+esc(st.c.nome)+'</span></li></ul>';
    var fstr=num(st.a,2)+' × '+num(r.i1,dec(r.i1))+' ÷ '+num(r.i0,dec(r.i0));
    if(r.fattore_valuta!==1)fstr+=(r.fattore_valuta<1?' \u00f7 ':' \u00d7 ')+num(DM_PER_EURO,5);
    h+='<p class="formula">'+esc(fstr+' = '+num(r.valore,2))+'</p>';
    var inv=calcola(st.c,st.a,st.aa,st.da,D.dm?(st.aa[0]<ANNO_EURO):null);
    if(inv)h+='<p>'+esc(T.inverso.replace('{importo}',fmt(st.a,vOut)).replace('{a}',aE).replace('{valore}',fmt(inv.valore,vIn)).replace('{da}',daE))+'</p>';
    h+=grafico(st.c,r,st);
    h+='<div class="azioni"><button type="button" class="btn sec" data-copia>'+esc(T.copia)+'</button><span class="small" data-copiato hidden>'+esc(T.copiato)+'</span></div>';
    out.innerHTML=h;}
  function link(){var st=legge(),p=new URLSearchParams();p.set('a',f.elements.a.value.trim());p.set('f',st.da[0]+(st.da[1]?'-'+st.da[1]:''));p.set('t',st.aa[0]+(st.aa[1]?'-'+st.aa[1]:''));
    if(f.elements.s)p.set('s',f.elements.s.value);if(D.dm&&f.elements.c)p.set('c',f.elements.c.value);return location.origin+location.pathname+'?'+p.toString()+'#calc';}
  out.addEventListener('click',function(e){var t=e.target.closest('[data-copia]');if(!t)return;var u=link(),ok=out.querySelector('[data-copiato]');
    function fatto(){if(ok)ok.hidden=false;}
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(u).then(fatto,function(){window.prompt(T.copia,u);});}else{window.prompt(T.copia,u);}});
  try{var q=new URLSearchParams(location.search);
    if(q.get('a'))f.elements.a.value=q.get('a').slice(0,30);
    if(q.get('s')&&f.elements.s&&D.serie[q.get('s')])f.elements.s.value=q.get('s');
    [['f','fy','fm'],['t','ty','tm']].forEach(function(k){var v=q.get(k[0]);if(!v)return;var m=/^(\d{4})(?:-(\d{1,2}))?$/.exec(v);if(!m)return;
      if(f.elements[k[1]].querySelector('option[value="'+m[1]+'"]')){f.elements[k[1]].value=m[1];f.elements[k[2]].value=m[2]?String(parseInt(m[2],10)):'';}});
    if(q.get('c')&&f.elements.c){var rr=f.querySelector('input[name=c][value="'+(q.get('c')==='eur'?'eur':'dm')+'"]');if(rr)rr.checked=true;}}catch(e){}
  f.addEventListener('input',calcolaUi);f.addEventListener('change',calcolaUi);f.addEventListener('submit',function(e){e.preventDefault();calcolaUi();});
  calcolaUi();
})();
