(function(){
  var R=document.documentElement;
  var b=document.querySelector('[data-tema]');
  if(b)b.addEventListener('click',function(){var c=R.getAttribute('data-theme');
    if(!c)c=window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
    var n=c==='dark'?'light':'dark';R.setAttribute('data-theme',n);try{localStorage.setItem('aste-tema',n);}catch(e){}});
  var src=document.querySelectorAll('input[name=source]');var ref='';try{ref=new URLSearchParams(location.search).get('ref')||document.referrer||'diretto';}catch(e){ref='diretto';}
  src.forEach(function(i){i.value=String(ref).slice(0,200);});
  document.querySelectorAll('form.ajax').forEach(function(form){form.addEventListener('submit',function(ev){ev.preventDefault();
    var err=form.querySelector('[data-errore]');err.hidden=true;if(!form.checkValidity()){form.reportValidity();return;}
    var bt=form.querySelector('button');bt.disabled=true;
    fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(new FormData(form)).toString()})
    .then(function(r){if(!r.ok)throw new Error(r.status);form.hidden=true;form.parentNode.querySelector('[data-ok]').hidden=false;})
    .catch(function(){err.hidden=false;bt.disabled=false;});});});

  // ---- aste: numeri in formato italiano, ora di Roma, aggiornamento da live.json
  function num(x){return String(Math.round(x)).replace(/\B(?=(\d{3})+(?!\d))/g,'.');}
  function eur(x){return num(x)+' €';}
  function oraRoma(){try{var p=new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Rome',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false}).format(new Date());
    return p.replace(' ','T').slice(0,16);}catch(e){return new Date().toISOString().slice(0,16);}}
  var MESI=['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'];
  var GIORNI=['domenica','lunedì','martedì','mercoledì','giovedì','venerdì','sabato'];
  function dataAsta(s){var d=new Date(s.slice(0,10)+'T12:00:00Z');return GIORNI[d.getUTCDay()]+' '+d.getUTCDate()+' '+MESI[d.getUTCMonth()]+' '+d.getUTCFullYear()+(s.length>10?', ore '+s.slice(11,16):'');}
  function letto(s){var d=new Date(s);if(isNaN(d))return s;
    try{var p=new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Rome',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false}).format(d);
      return (+p.slice(8,10))+' '+MESI[+p.slice(5,7)-1]+' '+p.slice(0,4)+' alle '+p.slice(11,16);}catch(e){return d.toLocaleString('it-IT');}}
  function scTesto(s){return s<=-3?'sotto la media OMI di zona':(s>=3?'sopra la media OMI di zona':'in linea con la media OMI di zona');}
  function scCls(s){return s<=-3?'down':(s>=3?'up':'neu');}
  var lotti=[].slice.call(document.querySelectorAll('[data-id]'));
  function aggiornaLotto(el,v){
    var base=v[0],min=v[1],data=v[2];
    if(base)el.dataset.base=base;if(min)el.dataset.min=min;if(data)el.dataset.data=data;
    var q=function(s){return el.querySelector(s);};
    if(base&&q('[data-v=base]'))q('[data-v=base]').textContent=eur(base);
    if(min&&q('[data-v=min]'))q('[data-v=min]').textContent=eur(min);
    if(data&&q('[data-v=data]'))q('[data-v=data]').textContent=dataAsta(data);
    var mq=+el.dataset.mq,omi=+el.dataset.omi;
    if(mq&&omi&&el.dataset.sc!==''&&min&&base){
      var s=Math.round((min/mq/omi-1)*100);el.dataset.sc=s;
      var sc=q('.sc');if(sc){sc.className='sc '+scCls(s);sc.querySelector('b').textContent=(s>0?'+':(s<0?'−':''))+Math.abs(s)+'%';sc.querySelector('span').textContent=scTesto(s);}
      if(q('[data-v=mqmin]'))q('[data-v=mqmin]').textContent=num(min/mq);
      if(q('[data-v=mqbase]'))q('[data-v=mqbase]').textContent=num(base/mq);
      var sca=q('.scala');if(sca){var mx=+sca.dataset.max;var a=q('.m.min'),bb=q('.m.base');
        if(a)a.style.left=Math.min(100,min/mq/mx*100).toFixed(1)+'%';if(bb)bb.style.left=Math.min(100,base/mq/mx*100).toFixed(1)+'%';}
    }
  }
  function conta(){
    document.querySelectorAll('[data-lista]').forEach(function(ls){
      var vis=[].slice.call(ls.querySelectorAll('[data-id]')).filter(function(e){return !e.hidden;}).length;
      var box=ls.closest('[data-blocco]')||ls.parentNode;
      box.querySelectorAll('[data-conta]').forEach(function(c){c.textContent=num(vis);});
      box.querySelectorAll('[data-plur]').forEach(function(c){var f=c.dataset.plur.split('|');c.textContent=vis===1?f[0]:f[1];});
      var vu=box.querySelector('[data-vuoto]');if(vu)vu.hidden=vis>0;
    });
    var nas=lotti.filter(function(e){return e.classList.contains('passato');}).length;
    document.querySelectorAll('[data-nascosti]').forEach(function(n){if(nas){n.hidden=false;n.textContent=' · '+(nas===1?'nascosta 1 asta già svolta o tolta dal PVP':'nascoste '+num(nas)+' aste già svolte o tolte dal PVP');}});
  }
  function filtra(){
    document.querySelectorAll('[data-lista]').forEach(function(ls){
      var f=ls.dataset.filtro||'tutti';
      [].forEach.call(ls.querySelectorAll('[data-id]'),function(e){
        var ok=!e.classList.contains('passato')&&(f==='tutti'||(f==='liberi'&&e.dataset.disp==='libero')||(f==='omi'&&e.dataset.sc!==''));
        e.hidden=!ok;});
    });
    conta();
  }
  function scadenze(){var ora=oraRoma();lotti.forEach(function(e){if(e.dataset.data&&e.dataset.data<ora)e.classList.add('passato');});}
  scadenze();filtra();
  var gen=document.body.dataset.gen,url=document.body.dataset.live;
  if(url&&lotti.length&&window.fetch){
    fetch(url,{cache:'no-store'}).then(function(r){if(!r.ok)throw 0;return r.json();}).then(function(L){
      if(!L||!L.lotti||!(Date.parse(L.letto_il)>Date.parse(gen)))return;
      lotti.forEach(function(e){var v=L.lotti[e.dataset.id];if(v)aggiornaLotto(e,v);else e.classList.add('passato');});
      document.querySelectorAll('[data-letto]').forEach(function(x){x.textContent=letto(L.letto_il);});
      scadenze();filtra();ordinaTutte();
    }).catch(function(){});
  }
  function ordina(ls,how){
    var el=[].slice.call(ls.children);
    el.sort(function(a,b){
      var da=a.dataset.data||'',db=b.dataset.data||'';
      if(how==='data')return da<db?-1:(da>db?1:0);
      if(how==='prezzo')return (+a.dataset.min||+a.dataset.base)-(+b.dataset.min||+b.dataset.base)||(da<db?-1:1);
      var sa=a.dataset.sc===''?null:+a.dataset.sc,sb=b.dataset.sc===''?null:+b.dataset.sc;
      if(sa===null&&sb===null)return da<db?-1:(da>db?1:0);if(sa===null)return 1;if(sb===null)return -1;return sa-sb||(da<db?-1:1);});
    el.forEach(function(e){ls.appendChild(e);});
  }
  function ordinaTutte(){document.querySelectorAll('[data-lista][data-ordine]').forEach(function(ls){ordina(ls,ls.dataset.ordine);});}
  document.querySelectorAll('[data-filtri]').forEach(function(g){var ls=document.getElementById(g.dataset.filtri);var bt=g.querySelectorAll('button');
    bt.forEach(function(x){x.addEventListener('click',function(){bt.forEach(function(y){y.setAttribute('aria-pressed','false');});x.setAttribute('aria-pressed','true');ls.dataset.filtro=x.dataset.f;filtra();});});});
  document.querySelectorAll('[data-ordina]').forEach(function(s){var ls=document.getElementById(s.dataset.ordina);
    s.addEventListener('change',function(){ls.dataset.ordine=s.value;ordina(ls,s.value);});});
})();
