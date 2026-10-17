(function(){
  var b=document.querySelector('[data-tema]');
  if(b)b.addEventListener('click',function(){var r=document.documentElement,c=r.getAttribute('data-theme');
    if(!c)c=window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
    var n=c==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('chs-theme',n);}catch(e){}});
  var src=document.querySelectorAll('input[name=source]');var ref='';try{ref=new URLSearchParams(location.search).get('ref')||document.referrer||'direct';}catch(e){ref='direct';}
  src.forEach(function(i){i.value=String(ref).slice(0,200);});
  document.querySelectorAll('form.ajax').forEach(function(form){form.addEventListener('submit',function(ev){ev.preventDefault();
    var err=form.querySelector('[data-errore]');err.hidden=true;if(!form.checkValidity()){form.reportValidity();return;}
    var bt=form.querySelector('button');bt.disabled=true;
    fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(new FormData(form)).toString()})
    .then(function(r){if(!r.ok)throw new Error(r.status);form.hidden=true;form.parentNode.querySelector('[data-ok]').hidden=false;})
    .catch(function(){err.hidden=false;bt.disabled=false;});});});
  var box=document.querySelector('[data-cerca]');if(!box)return;
  var inp=box.querySelector('input'),out=box.querySelector('.risultati'),D=null,carico=false,coda=null;
  function norm(s){return String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,' ').trim();}
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function cl(v){return v>=100?'s100':v>=95?'s95':v>=90?'s90':v>=86?'s86':'sf';}
  function carica(cb){if(D)return cb();coda=cb;if(carico)return;carico=true;
    fetch(box.getAttribute('data-url')).then(function(r){if(!r.ok)throw new Error(r.status);return r.json();}).then(function(d){D=d;
      d.forEach(function(x){x.k=norm(x[0]+' '+(x[6]||''));x.l=norm(x[2]);});if(coda)coda();})
    .catch(function(){out.innerHTML='<p class="errore">Could not load the list of ships. Please try again.</p>';carico=false;});}
  function riga(x){return '<a href="/ships/'+esc(x[1])+'/"><span><b>'+esc(x[0])+'</b><small>'+esc(x[2])+' · inspected '+esc(x[4])+(x[5]?'':' · no longer in the CDC list')+'</small></span><span class="sc '+cl(x[3])+'">'+x[3]+'</span></a>';}
  function cerca(){var q=inp.value,v=norm(q);if(v.length<2){out.innerHTML='';return;}
    carica(function(){var a=[],b=[],c=[];
      D.forEach(function(x){if(x.k.indexOf(v)===0)a.push(x);else if((' '+x.k).indexOf(' '+v)>=0)b.push(x);else if(x.l.indexOf(v)===0||(' '+x.l).indexOf(' '+v)>=0)c.push(x);});
      var r=a.concat(b,c).slice(0,10);
      out.innerHTML=r.length?r.map(riga).join(''):'<p class="small">No ship found for "'+esc(q)+'". Try part of the name, such as "Wonder" or "Carnival". Ships that left U.S. waters long ago are not listed.</p>';});}
  inp.addEventListener('input',cerca);inp.addEventListener('focus',function(){carica(function(){});},{once:true});
  box.querySelector('form').addEventListener('submit',function(e){e.preventDefault();var a=out.querySelector('a');if(a)location.href=a.href;else cerca();});
})();
