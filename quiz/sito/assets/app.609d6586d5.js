(function(){
'use strict';
var b=document.querySelector('[data-tema]');
if(b){b.addEventListener('click',function(){var r=document.documentElement;var dark=r.getAttribute('data-theme')==='dark'||(!r.getAttribute('data-theme')&&window.matchMedia('(prefers-color-scheme: dark)').matches);var t=dark?'light':'dark';r.setAttribute('data-theme',t);try{localStorage.setItem('qu-tema',t);}catch(e){}});}
var Q=document.querySelector('[data-quiz]');
if(!Q)return;
var LET='abcd';
var tutte=Array.prototype.map.call(document.querySelectorAll('[data-dom]'),function(li){
  return {id:li.id,n:li.getAttribute('data-n'),s:parseInt(li.getAttribute('data-s'),10),e:parseInt(li.getAttribute('data-e'),10),p:li.getAttribute('data-p'),
    t:li.querySelector('.dq .t').textContent,r:Array.prototype.map.call(li.querySelectorAll('.opz .r'),function(x){return x.textContent;}),
    sez:li.getAttribute('data-sez')||''};});
var avvio=Q.querySelector('[data-avvio]'),gioco=Q.querySelector('[data-gioco]'),fine=Q.querySelector('[data-fine]');
var elQ=Q.querySelector('[data-q]'),elO=Q.querySelector('[data-opz]'),elF=Q.querySelector('[data-fb]'),elPos=Q.querySelector('[data-pos]'),elT=Q.querySelector('[data-tempo]'),elProg=Q.querySelector('[data-prog]'),btnAv=Q.querySelector('[data-avanti]');
var nojs=Q.querySelector('[data-nojs]');if(nojs)nojs.hidden=true;avvio.hidden=false;
var N=parseInt(Q.getAttribute('data-n'),10),MAXERR=Q.getAttribute('data-max-errori'),SOGLIA=Q.getAttribute('data-soglia'),MIN=Q.getAttribute('data-minuti');
var scelte=JSON.parse(Q.getAttribute('data-scelte')||'[]');
var QUOTE=JSON.parse(Q.getAttribute('data-quote')||'[]'),ORALE=Q.getAttribute('data-orale');
var serie=[],i=0,risp=[],modo='',timer=null,scade=0;
function mescola(a){a=a.slice();for(var k=a.length-1;k>0;k--){var j=Math.floor(Math.random()*(k+1));var x=a[k];a[k]=a[j];a[j]=x;}return a;}
function escluse(){var ex={};scelte.forEach(function(g,gi){var sel=Q.querySelector('[data-scelta="'+gi+'"]');var v=sel?parseInt(sel.value,10):0;g.opzioni.forEach(function(o,oi){if(oi!==v&&o[1])o[1].forEach(function(s){ex[s]=1;});});});return ex;}
function inizia(m){modo=m;var ex=escluse();var pool=tutte.filter(function(d){return !ex[d.s];});
  if(m==='ripasso'){var s=parseInt(Q.querySelector('[data-sezione]').value,10);serie=pool.filter(function(d){return d.s===s;});if(!serie.length)serie=tutte.filter(function(d){return d.s===s;});}
  else if(QUOTE.length){serie=[];QUOTE.forEach(function(q){serie=serie.concat(mescola(pool.filter(function(d){return d.s===q[0];})).slice(0,q[1]));});
    if(serie.length<Math.min(N,pool.length)){serie=mescola(pool).slice(0,Math.min(N,pool.length));}}
  else{serie=mescola(pool).slice(0,Math.min(N,pool.length));}
  i=0;risp=[];avvio.hidden=true;fine.hidden=true;gioco.hidden=false;
  if(timer){clearInterval(timer);timer=null;}elT.textContent='';
  if(m==='esame'&&MIN){scade=Date.now()+parseInt(MIN,10)*60000;timer=setInterval(tick,1000);tick();}
  mostra();gioco.scrollIntoView({block:'start'});}
function tick(){var r=Math.max(0,Math.round((scade-Date.now())/1000));elT.textContent='Tempo: '+Math.floor(r/60)+':'+('0'+r%60).slice(-2);if(r<=0){clearInterval(timer);timer=null;termina(true);}}
function mostra(){var d=serie[i];elPos.textContent='Domanda '+(i+1)+' di '+serie.length;elProg.style.width=(100*i/serie.length)+'%';
  elQ.innerHTML='';var sm=document.createElement('small');sm.textContent=(d.sez?d.sez+' · ':'')+'n. '+d.n;elQ.appendChild(sm);elQ.appendChild(document.createTextNode(d.t));
  elO.innerHTML='';d.r.forEach(function(t,k){var bt=document.createElement('button');bt.type='button';var bb=document.createElement('b');bb.textContent=LET[k];var sp=document.createElement('span');sp.textContent=t;bt.appendChild(bb);bt.appendChild(sp);bt.addEventListener('click',function(){scegli(k);});elO.appendChild(bt);});
  elF.hidden=true;btnAv.hidden=true;}
function scegli(k){var d=serie[i];risp[i]=k;var bt=elO.querySelectorAll('button');bt.forEach(function(x,j){x.disabled=true;if(j===d.e)x.classList.add('giusta');else if(j===k)x.classList.add('sbagliata');});
  var ok=k===d.e;elF.className='quiz-fb '+(ok?'ok':'ko');elF.innerHTML='';var p=document.createElement('p');var st=document.createElement('strong');st.textContent=ok?'Giusto. ':'Sbagliato. ';p.appendChild(st);
  p.appendChild(document.createTextNode('Risposta ufficiale: '+LET[d.e]+') '+d.r[d.e]));elF.appendChild(p);var s2=document.createElement('p');s2.className='small';s2.textContent='Pagina '+d.p+' del PDF ufficiale.';elF.appendChild(s2);
  elF.hidden=false;btnAv.hidden=false;btnAv.textContent=(i+1<serie.length)?'Avanti':'Vedi il risultato';btnAv.focus();}
btnAv.addEventListener('click',function(){i++;if(i<serie.length)mostra();else termina(false);});
function termina(scaduto){if(timer){clearInterval(timer);timer=null;}gioco.hidden=true;fine.hidden=false;elProg.style.width='100%';
  var giuste=0,errate=[];serie.forEach(function(d,k){if(risp[k]===d.e)giuste++;else errate.push([d,risp[k]]);});var err=serie.length-giuste;
  fine.innerHTML='';var v=document.createElement('p');v.className='voto';v.textContent=giuste+' giuste su '+serie.length;fine.appendChild(v);
  var esito=document.createElement('p');var superato=null;
  var orale=false;
  if(modo==='esame'){if(MAXERR!==null&&MAXERR!==''){superato=err<=parseInt(MAXERR,10);esito.textContent=(superato?'Superato':'Non superato')+': '+err+(err===1?' errore':' errori')+', il massimo ammesso è '+MAXERR+'.';
      if(ORALE&&superato&&err>=parseInt(ORALE,10)){orale=true;esito.textContent='Rimandato all\'orale: '+err+' errori. Nell\'autotest dell\'ente l\'esito è «idoneo» fino a '+(parseInt(ORALE,10)-1)+' errori, «rimandato all\'orale» da '+ORALE+' a '+MAXERR+', «non idoneo» oltre.';}
      else if(ORALE&&superato){esito.textContent='Superato (idoneo): '+err+(err===1?' errore':' errori')+'. Da '+ORALE+' a '+MAXERR+' errori si va all\'orale; oltre, non idoneo.';}}
    else if(SOGLIA){var serve=Math.ceil(serie.length*parseFloat(SOGLIA)/100);superato=giuste>=serve;esito.textContent=(superato?'Superato':'Non superato')+': servono almeno '+serve+' risposte giuste ('+SOGLIA+'%).';}
    else{esito.textContent='Esercitazione: la soglia per superare la prova non è scritta nei documenti dell\'ente.';}}
  else{esito.textContent='Ripasso di un argomento: '+err+(err===1?' errore.':' errori.');}
  if(scaduto){esito.textContent='Tempo scaduto: le domande senza risposta contano come errori. '+esito.textContent;}
  if(superato!==null&&!orale)v.className='voto '+(superato?'ok':'ko');fine.appendChild(esito);
  if(errate.length){var h=document.createElement('h3');h.textContent='Le risposte ufficiali alle domande sbagliate';fine.appendChild(h);var ol=document.createElement('ol');
    errate.forEach(function(x){var d=x[0],li=document.createElement('li');var a=document.createElement('a');a.href='#'+d.id;a.textContent='n. '+d.n;li.appendChild(a);
      li.appendChild(document.createTextNode(' '+d.t+' '));var r=document.createElement('strong');r.textContent='Risposta ufficiale: '+LET[d.e]+') '+d.r[d.e]+'.';li.appendChild(r);
      if(x[1]!==undefined){li.appendChild(document.createTextNode(' Avevi scelto '+LET[x[1]]+').'));}else{li.appendChild(document.createTextNode(' Senza risposta.'));}
      ol.appendChild(li);});fine.appendChild(ol);}
  var az=document.createElement('p');az.className='quiz-azioni';var b1=document.createElement('button');b1.type='button';b1.className='btn';b1.textContent='Rifai';b1.addEventListener('click',function(){inizia(modo);});
  var b2=document.createElement('button');b2.type='button';b2.className='btn sec';b2.textContent='Cambia modalità';b2.addEventListener('click',function(){fine.hidden=true;avvio.hidden=false;});az.appendChild(b1);az.appendChild(b2);fine.appendChild(az);
  fine.setAttribute('data-giuste',giuste);fine.setAttribute('data-totale',serie.length);}
Q.querySelectorAll('[data-avvia]').forEach(function(x){x.addEventListener('click',function(){inizia(x.getAttribute('data-avvia'));});});
})();
