(function(){
  var b=document.querySelector('[data-tema]');
  if(b)b.addEventListener('click',function(){var r=document.documentElement,c=r.getAttribute('data-theme');
    if(!c)c=window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
    var n=c==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('fc-theme',n);}catch(e){}});
  var src=document.querySelectorAll('input[name=source]');var ref='';try{ref=new URLSearchParams(location.search).get('ref')||document.referrer||'direct';}catch(e){ref='direct';}
  src.forEach(function(i){i.value=String(ref).slice(0,200);});
  document.querySelectorAll('form.ajax').forEach(function(form){form.addEventListener('submit',function(ev){ev.preventDefault();
    var err=form.querySelector('[data-errore]');err.hidden=true;if(!form.checkValidity()){form.reportValidity();return;}
    var bt=form.querySelector('button');bt.disabled=true;
    fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(new FormData(form)).toString()})
    .then(function(r){if(!r.ok)throw new Error(r.status);form.hidden=true;form.parentNode.querySelector('[data-ok]').hidden=false;})
    .catch(function(){err.hidden=false;bt.disabled=false;});});});
  var ca=document.querySelector('[data-cerca-ca]');
  if(ca){(function(){
    var ci=ca.querySelector('input'),co=ca.querySelector('.risultati'),CD=null,cc=false,cq=null,crel=ca.getAttribute('data-rel')||'';
    function nr(s){return String(s||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,' ').trim();}
    function es(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
    function fm(x){return Number(x).toLocaleString('en-US');}
    function car(cb){if(CD)return cb();cq=cb;if(cc)return;cc=true;co.innerHTML='<p class="small">Loading the list…</p>';
      fetch(ca.getAttribute('data-url')).then(function(r){if(!r.ok)throw new Error(r.status);return r.json();}).then(function(d){CD=d;
        d.z.forEach(function(x){x.k=' '+nr(x[1])+' '+nr(x[2])+' '+nr(x[2]+' county');});if(cq)cq();})
      .catch(function(){co.innerHTML='<p class="errore">Could not load the list. Please try again.</p>';cc=false;});}
    function scheda(x){var t='ZIP '+x[0]+(x[1]?' · '+x[1]:'')+(x[2]?', '+x[2]+' County':'');var s=[];
      if(x[4]!=null)s.push(fm(x[4])+' FAIR Plan policies'+(x[3]!=null?' ('+fm(x[3])+' in 2022)':''));else s.push('not in the FAIR Plan report');
      if(x[5]!=null)s.push('average premium $'+fm(x[5])+' (owner-occupied home)');
      if(x[6]!=null)s.push(fm(x[6])+' not renewed or cancelled in 2023'+(x[7]!=null?' ('+x[7].toFixed(1)+'%)':''));
      var d='<b>'+es(t)+'</b><span>'+es(s.join(' · '))+'</span>';
      return x[8]?'<a href="'+es(crel+x[8])+'">'+d+'</a>':'<div class="ris">'+d+'</div>';}
    function cerca(){var q=ci.value.trim(),v=nr(q);if(v.length<2){co.innerHTML='';return;}
      car(function(){var r=[];
        if(/^\d{2,5}$/.test(v)){CD.z.forEach(function(x){if(r.length<10&&x[0].indexOf(v)===0)r.push(x);});}
        else{CD.z.forEach(function(x){if(x.k.indexOf(' '+v)>=0)r.push(x);});r.sort(function(a,b){return (b[4]||0)-(a[4]||0);});r=r.slice(0,12);}
        co.innerHTML=r.length?r.map(scheda).join(''):'<p class="small">Nothing found for "'+es(q)+'". Try a 5-digit California ZIP code, a place or a county.</p>';});}
    ci.addEventListener('input',cerca);ci.addEventListener('focus',function(){car(function(){});},{once:true});
    ca.querySelector('form').addEventListener('submit',function(e){e.preventDefault();cerca();});
  })();}
  var box=document.querySelector('[data-cerca]');if(!box)return;
  var inp=box.querySelector('input'),out=box.querySelector('.risultati'),D=null,carico=false,coda=null,rel=box.getAttribute('data-rel')||'';
  function norm(s){return String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,' ').trim();}
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function usd(x){return x==null?'–':'$'+Number(x).toLocaleString('en-US');}
  function carica(cb){if(D)return cb();coda=cb;if(carico)return;carico=true;out.innerHTML='<p class="small">Loading the index…</p>';
    fetch(box.getAttribute('data-url')).then(function(r){if(!r.ok)throw new Error(r.status);return r.json();}).then(function(d){D=d;
      d.s.forEach(function(x){x.k=norm(x[1]);});d.c.forEach(function(x){x.k=norm(x[0]);});if(coda)coda();})
    .catch(function(){out.innerHTML='<p class="errore">Could not load the search index. Please try again.</p>';carico=false;});}
  function riga(href,tit,info){return '<a href="'+esc(rel+href)+'"><b>'+esc(tit)+'</b><span>'+info+'</span></a>';}
  function cerca(){var q=inp.value.trim(),v=norm(q);if(v.length<2){out.innerHTML='';return;}
    carica(function(){var r=[];
      if(/^\d{3,5}$/.test(v)){Object.keys(D.z).forEach(function(z){if(r.length<8&&z.indexOf(v)===0){var x=D.z[z],c=x[1]>=0?D.c[x[1]]:null,st=D.s[x[0]];
          var href=x[4]?'zip/'+z+'/':(c&&c[2]?c[2]:(st?st[2]:''));
          var dove=(c?c[0]+', ':'')+(st?st[0]:'');var info=x[2].toLocaleString('en-US')+' home policies · median '+usd(x[3])+(x[4]?'':' · see '+(c&&c[2]?'county':'state')+' page');
          r.push(riga(href,'ZIP '+z+(dove?' · '+dove:''),info));}});
        if(!r.length)out.innerHTML='<p class="small">No ZIP code starting with '+esc(q)+' has at least 10 NFIP home policies in force. Try the county or state name.</p>';else out.innerHTML=r.join('');return;}
      D.s.forEach(function(s){if(r.length<10&&(s.k.indexOf(v)===0||norm(s[0])===v))r.push(riga(s[2],s[1],s[3].toLocaleString('en-US')+' home policies · median '+usd(s[4])));});
      D.c.forEach(function(c){if(r.length<12&&c.k.indexOf(v)===0){var st=D.s[c[1]];var href=c[2]||(st?st[2]:'');
        r.push(riga(href,c[0]+', '+(st?st[0]:''),c[3].toLocaleString('en-US')+' home policies · median '+usd(c[4])+(c[2]?'':' · see state page')));}});
      if(r.length<12)D.c.forEach(function(c){if(r.length<12&&c.k.indexOf(' '+v)>0){var st=D.s[c[1]];r.push(riga(c[2]||(st?st[2]:''),c[0]+', '+(st?st[0]:''),c[3].toLocaleString('en-US')+' home policies · median '+usd(c[4])));}});
      out.innerHTML=r.length?r.join(''):'<p class="small">Nothing found for "'+esc(q)+'". Try a 5-digit ZIP code, a county or a state.</p>';});}
  inp.addEventListener('input',cerca);inp.addEventListener('focus',function(){carica(function(){});},{once:true});
  box.querySelector('form').addEventListener('submit',function(e){e.preventDefault();var a=out.querySelector('a');if(a)location.href=a.href;else cerca();});
})();
