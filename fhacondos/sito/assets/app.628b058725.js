(function(){
  var b=document.querySelector('[data-tema]');
  if(b)b.addEventListener('click',function(){var r=document.documentElement,c=r.getAttribute('data-theme');
    if(!c)c=window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
    var n=c==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('ac-theme',n);}catch(e){}});
  var ref='';try{ref=new URLSearchParams(location.search).get('ref')||document.referrer||'direct';}catch(e){ref='direct';}
  document.querySelectorAll('input[name=source]').forEach(function(i){i.value=String(ref).slice(0,200);});
  document.querySelectorAll('form.ajax').forEach(function(form){form.addEventListener('submit',function(ev){ev.preventDefault();
    var err=form.querySelector('[data-errore]');err.hidden=true;if(!form.checkValidity()){form.reportValidity();return;}
    var bt=form.querySelector('button');bt.disabled=true;
    fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(new FormData(form)).toString()})
    .then(function(r){if(!r.ok)throw new Error(r.status);form.hidden=true;form.parentNode.querySelector('[data-ok]').hidden=false;})
    .catch(function(){err.hidden=false;bt.disabled=false;});});});
  function norm(s){return String(s==null?'':s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,' ').trim().replace(/\bsaint\b/g,'st');}
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  // filtro delle tabelle
  document.querySelectorAll('[data-filtro]').forEach(function(inp){
    var t=document.getElementById(inp.getAttribute('data-filtro'));if(!t)return;var rows=[].slice.call(t.tBodies[0].rows);
    var out=document.getElementById(inp.getAttribute('data-filtro')+'-n');rows.forEach(function(r){r._k=norm(r.textContent);});
    inp.addEventListener('input',function(){var v=norm(inp.value),n=0;rows.forEach(function(r){var ok=!v||r._k.indexOf(v)>=0;r.hidden=!ok;if(ok)n++;});
      if(out)out.textContent=v?(n+' of '+rows.length+' shown'):'';});});
  var box=document.querySelector('[data-cerca]');if(!box)return;
  var inp=box.querySelector('input'),out=box.querySelector('.risultati'),D=null,carico=false,coda=null,rel=box.getAttribute('data-rel')||'';
  var MESI=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  function dt(n){if(!n)return '';var s=String(n);return MESI[+s.slice(4,6)-1]+' '+(+s.slice(6,8))+', '+s.slice(0,4);}
  function carica(cb){if(D)return cb();coda=cb;if(carico)return;carico=true;out.innerHTML='<p class="small">Loading the list…</p>';
    fetch(box.getAttribute('data-url')).then(function(r){if(!r.ok)throw new Error(r.status);return r.json();}).then(function(d){D=d;
      d.c.forEach(function(x){x.k=' '+norm(x[0])+' ';x.t=norm(d.t[x[1]][0]);x.ts=x.t+' '+d.t[x[1]][1].toLowerCase();});d.p.forEach(function(x){x.k=norm(x[1]);});if(coda)coda();})
    .catch(function(){out.innerHTML='<p class="errore">Could not load the list. Please try again.</p>';carico=false;});}
  function stato(x){if(x[6]===0){return x[7]?'<span class="badge b-soon">Expires '+dt(x[5])+'</span>':'<span class="badge b-ok">Approved until '+dt(x[5])+'</span>';}
    if(x[6]===1)return '<span class="badge b-bad">Expired '+dt(x[5])+'</span>';if(x[6]===3)return '<span class="badge b-soon">Approval ends '+dt(x[5])+'</span>';return '<span class="badge b-mute">Withdrawn '+dt(x[5])+'</span>';}
  function riga(x){var t=D.t[x[1]],p=D.p[x[4]];return '<a href="'+esc(rel+p[0])+'#c-'+esc(x[8])+'"><b>'+esc(x[0])+'</b>'+stato(x)+
    '<span class="dove">'+esc(t[0])+', '+esc(t[1])+(x[2]?' '+esc(x[2]):'')+' · HUD ID '+esc(x[8])+'</span></a>';}
  function cerca(){var q=inp.value.trim(),v=norm(q);if(v.length<2){out.innerHTML='';return;}
    carica(function(){var r=[],luoghi=[],zip=/^\d{3,5}$/.test(v),idq=/^[a-z]\d{3,6}$/.test(v.replace(/ /g,''));
      if(!zip&&!idq){D.p.forEach(function(p){if(luoghi.length<6&&p[2]&&(p.k.indexOf(v)===0||p.k.indexOf(' '+v)>=0))luoghi.push(p);});}
      D.c.forEach(function(x){if(r.length>=40)return;var ok=false;
        if(zip)ok=String(x[2]).indexOf(v)===0;else if(idq)ok=x[8].toLowerCase().indexOf(v.replace(/ /g,''))===0;
        else ok=x.k.indexOf(' '+v)>=0||x.ts.indexOf(v)===0;if(ok)r.push(x);});
      r.sort(function(a,b){return a[6]-b[6]||(a[0]<b[0]?-1:1);});
      var html='';if(luoghi.length)html+='<p class="grp">Places</p>'+luoghi.map(function(p){return '<a href="'+esc(rel+p[0])+'"><b>'+esc(p[1])+'</b><span class="badge b-ok">'+p[3]+' approved</span></a>';}).join('');
      if(r.length)html+='<p class="grp">Condo projects'+(r.length>=40?' (first 40)':'')+'</p>'+r.slice(0,40).map(riga).join('');
      out.innerHTML=html||'<p class="small">Nothing found for “'+esc(q)+'”. Try one distinctive word of the name, the city or the 5-digit ZIP code. Not listed? It may not be approved: <a href="'+esc(rel)+'condo-not-fha-approved/">see your options</a>.</p>';});}
  inp.addEventListener('input',cerca);inp.addEventListener('focus',function(){carica(function(){});},{once:true});
  box.querySelector('form').addEventListener('submit',function(e){e.preventDefault();var a=out.querySelector('a');if(a)location.href=a.href;else cerca();});
  box.querySelectorAll('[data-es]').forEach(function(bt){bt.addEventListener('click',function(){inp.value=bt.getAttribute('data-es');inp.focus();cerca();});});
  try{var q0=new URLSearchParams(location.search).get('q');if(q0){inp.value=q0;cerca();}}catch(e){}
})();
