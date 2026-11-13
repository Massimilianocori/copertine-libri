"""Aspetto e codice del browser di Military Pay Chart: CSS (caratteri di sistema, nessun file esterno), icone, marchio,
JS (tema chiaro/scuro e calcolatore). La funzione JS `calcola` è la copia di genera.calcola: verifica.py le confronta
su tutte le combinazioni grado × anzianità."""

CSS = """
:root{--bg:#F4F5F7;--card:#FFFFFF;--ink:#141B2D;--ink-2:#39435A;--ink-3:#5A6478;--line:#DDE1E8;--line-2:#C4CAD6;
--deep:#111A2E;--deep-2:#1B2742;--on-deep:#EEF1F7;--on-deep-2:#B5BED1;--accent:#1F4FA8;--accent-h:#163C82;--accent-2:#E6EDFA;--on-accent:#fff;
--brass:#B8862B;--brass-ink:#8A5F12;--brass-2:#FBF2DF;--warn:#8A4B00;--warn-2:#FFF4E0;--mute:#EEF0F4;--ok:#1E7A4C;
--sh-1:0 1px 2px rgba(17,26,46,.06);--sh-2:0 18px 40px -24px rgba(17,26,46,.45),0 2px 6px rgba(17,26,46,.06);--r:14px;--r-s:10px;
--sans:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;--serif:Charter,"Bitstream Charter","Iowan Old Style","Palatino Linotype",Georgia,serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0B1020;--card:#121A2E;--ink:#E6EAF3;--ink-2:#BCC4D6;--ink-3:#97A1B6;--line:#222D45;--line-2:#33405E;
--deep:#070B16;--deep-2:#0F1730;--on-deep:#E6EAF3;--on-deep-2:#A3AEC6;--accent:#8DB0F2;--accent-h:#B5CCF7;--accent-2:#16233F;--on-accent:#0B1020;
--brass:#E0B25A;--brass-ink:#E0B25A;--brass-2:#2A2112;--warn:#F2C177;--warn-2:#2A200F;--mute:#161F35;--ok:#6FD3A0;--sh-1:0 1px 2px rgba(0,0,0,.5);--sh-2:0 18px 40px -24px rgba(0,0,0,.9)}}
:root[data-theme="dark"]{--bg:#0B1020;--card:#121A2E;--ink:#E6EAF3;--ink-2:#BCC4D6;--ink-3:#97A1B6;--line:#222D45;--line-2:#33405E;
--deep:#070B16;--deep-2:#0F1730;--on-deep:#E6EAF3;--on-deep-2:#A3AEC6;--accent:#8DB0F2;--accent-h:#B5CCF7;--accent-2:#16233F;--on-accent:#0B1020;
--brass:#E0B25A;--brass-ink:#E0B25A;--brass-2:#2A2112;--warn:#F2C177;--warn-2:#2A200F;--mute:#161F35;--ok:#6FD3A0;--sh-1:0 1px 2px rgba(0,0,0,.5);--sh-2:0 18px 40px -24px rgba(0,0,0,.9)}
*{box-sizing:border-box}[hidden]{display:none!important}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:17px;line-height:1.6;overflow-wrap:break-word}
a{color:var(--accent);text-underline-offset:2px}a:hover{color:var(--accent-h)}
:focus-visible{outline:3px solid var(--brass);outline-offset:2px;border-radius:4px}
.skip{position:absolute;left:-9999px;top:8px;background:var(--card);color:var(--ink);padding:8px 14px;border-radius:8px;z-index:50}.skip:focus{left:12px}
.ico{width:1.1em;height:1.1em;flex:none;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;vertical-align:-.18em}
.wrap{max-width:1120px;margin:0 auto;padding:0 16px}
header.top{background:var(--deep);color:var(--on-deep);position:relative;z-index:20;border-bottom:1px solid rgba(255,255,255,.08)}
header.top .wrap{display:flex;align-items:center;gap:8px;min-height:60px}
.logo{display:flex;align-items:center;gap:9px;font-family:var(--serif);font-weight:700;font-size:1.13rem;color:var(--on-deep);text-decoration:none;white-space:nowrap;margin-right:auto;line-height:1.1}
.logo:hover{color:#fff}.logo img{width:32px;height:32px;display:block}.logo b{color:var(--brass);font-weight:inherit}
nav.menu{display:flex;gap:2px;font-size:.93rem}
nav.menu a{color:var(--on-deep-2);text-decoration:none;padding:7px 11px;border-radius:8px;white-space:nowrap}
nav.menu a:hover,nav.menu a[aria-current]{color:#fff;background:rgba(255,255,255,.09)}
.tema{display:grid;place-items:center;width:40px;height:40px;border-radius:10px;border:1px solid rgba(255,255,255,.22);background:none;color:var(--on-deep);cursor:pointer;flex:none}
.tema .i-sun{display:none}:root[data-theme="dark"] .tema .i-sun{display:block}:root[data-theme="dark"] .tema .i-moon{display:none}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .tema .i-sun{display:block}:root:not([data-theme="light"]) .tema .i-moon{display:none}}
.nav-m{display:none}
.nav-m summary{list-style:none;cursor:pointer;display:grid;place-items:center;width:40px;height:40px;border:1px solid rgba(255,255,255,.25);border-radius:10px;color:var(--on-deep)}
.nav-m summary::-webkit-details-marker{display:none}
.nav-m nav{position:absolute;left:16px;right:16px;top:calc(100% + 4px);background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-2);padding:8px;display:grid;grid-template-columns:repeat(4,1fr);gap:2px}
.nav-m nav a{padding:10px 8px;border-radius:8px;color:var(--ink);text-decoration:none;font-weight:700;font-size:.93rem;text-align:center}.nav-m nav a:hover{background:var(--accent-2)}
.nav-m nav a.w2{grid-column:span 2}.nav-m nav .sep{grid-column:1/-1;border-top:1px solid var(--line);margin:4px 0}
.band{background:linear-gradient(180deg,var(--deep) 0,var(--deep-2) 100%);color:var(--on-deep);position:relative;overflow:hidden}
.band::after{content:"";position:absolute;right:-60px;top:-40px;width:360px;height:360px;border-radius:50%;border:44px solid rgba(184,134,43,.13)}
.band-in{position:relative;z-index:1;padding:26px 16px 72px}.band.corta .band-in{padding-bottom:40px}
.eyebrow{display:inline-flex;align-items:center;gap:8px;font-size:.78rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--brass);margin:0 0 10px}
h1,h2,h3{font-family:var(--serif);font-weight:700;letter-spacing:-.01em}
h1{font-size:clamp(1.8rem,5vw,2.7rem);line-height:1.12;margin:0 0 12px;max-width:900px}.band h1{color:#fff}
.sub{font-size:1.06rem;color:var(--on-deep-2);margin:0 0 14px;max-width:780px}.sub strong{color:#fff}.sub a{color:#fff}
.briciole{font-size:.85rem;color:var(--on-deep-2);margin:0 0 12px}.briciole a{color:var(--on-deep)}
h2{font-size:clamp(1.35rem,3vw,1.65rem);line-height:1.2;margin:42px 0 12px}h3{font-size:1.12rem;margin:22px 0 8px}
p{margin:0 0 14px}.small{font-size:.87rem;color:var(--ink-3)}
.testo p,.testo li{max-width:800px}.testo li{margin-bottom:8px}.testo ul,.testo ol{padding-left:22px}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:18px;box-shadow:var(--sh-1);min-width:0}
.pull{margin-top:-52px;position:relative;z-index:2}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));padding:0;overflow:hidden;box-shadow:var(--sh-2)}
.stat{padding:16px 18px;border-right:1px solid var(--line);min-width:0}.stat:last-child{border-right:0}
.stat b{display:block;font-family:var(--serif);font-size:clamp(1.35rem,3.4vw,1.85rem);line-height:1.1;font-variant-numeric:tabular-nums}
.stat span{display:block;font-size:.84rem;color:var(--ink-3);line-height:1.35;margin-top:5px}.stat.main b{color:var(--accent)}
.asof{margin:0;padding:10px 18px;background:var(--mute);border-top:1px solid var(--line);font-size:.86rem;color:var(--ink-2);grid-column:1/-1}
.tab{border:1px solid var(--line);border-radius:var(--r);background:var(--card);box-shadow:var(--sh-1);overflow-x:auto;-webkit-overflow-scrolling:touch;margin:0 0 8px;max-width:100%}
table.dati{border-collapse:separate;border-spacing:0;width:100%;font-size:.9rem}
table.dati caption{text-align:left;padding:12px 14px;font-size:.88rem;color:var(--ink-2);border-bottom:1px solid var(--line)}
table.dati th,table.dati td{text-align:left;padding:8px 11px;border-bottom:1px solid var(--line);vertical-align:top}
table.dati td.n,table.dati th.n{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
table.dati thead th{background:var(--mute);font-size:.72rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-2);vertical-align:bottom;white-space:nowrap}
table.dati tbody tr:last-child td,table.dati tbody tr:last-child th{border-bottom:0}
table.dati th[scope=row]{background:var(--card);font-weight:800;white-space:nowrap}
table.dati td.na{color:var(--ink-3);text-align:center}
table.grande th[scope=row],table.grande thead th:first-child{position:sticky;left:0;z-index:1;box-shadow:1px 0 0 var(--line)}
table.grande thead th:first-child{background:var(--mute)}
table.dati tr.qui th,table.dati tr.qui td{background:var(--accent-2)}
.cap{color:var(--brass-ink);font-weight:800}
.nota{position:relative;background:var(--warn-2);border:1px solid color-mix(in srgb,var(--brass) 45%,transparent);padding:12px 16px 12px 46px;border-radius:var(--r-s);font-size:.95rem;margin:18px 0}
.nota .ico{position:absolute;left:16px;top:15px;color:var(--warn);width:19px;height:19px}.nota p{margin:0 0 6px}.nota p:last-child{margin:0}
.nota.info{background:var(--accent-2);border-color:color-mix(in srgb,var(--accent) 30%,transparent)}.nota.info .ico{color:var(--accent)}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(104px,1fr));gap:8px;margin:0;padding:0;list-style:none}
.griglia a{display:flex;flex-direction:column;gap:2px;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:10px 12px;text-decoration:none;color:var(--ink);box-shadow:var(--sh-1)}
.griglia a:hover{border-color:var(--accent)}.griglia a b{font-family:var(--serif);font-size:1.15rem;color:var(--accent)}.griglia a small{color:var(--ink-3);font-size:.8rem;font-variant-numeric:tabular-nums}
.griglia.larga{grid-template-columns:repeat(auto-fill,minmax(230px,1fr))}.griglia.larga a{font-weight:700}
.faq{border-top:1px solid var(--line);padding:4px 0 6px}.faq h3{margin:16px 0 6px;font-size:1.06rem}.faq p{margin:0 0 6px;max-width:800px}
sup.ref{font-size:max(.72em,11px);line-height:0;margin-left:1px}sup.ref a{text-decoration:none;font-weight:700}
.fonti-box{margin-top:40px;border-top:2px solid var(--line);padding-top:6px}.fonti-box ol{padding-left:22px;font-size:.9rem}.fonti-box li{margin-bottom:8px}
.fonti-box h2{display:flex;align-items:center;gap:8px}
.calc{padding:0!important;overflow:hidden;box-shadow:var(--sh-2)}
.calc-h{display:flex;align-items:center;gap:10px;margin:0;padding:14px 18px;border-bottom:1px solid var(--line)}.calc-h h2{margin:0;font-size:1.2rem;display:flex;gap:9px;align-items:center}
.calc-h .ico{color:var(--brass-ink)}
.calc-g{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.15fr)}
.calc-in{padding:16px 18px;display:grid;gap:14px;align-content:start;border-right:1px solid var(--line)}
.calc-in label{display:grid;gap:6px;font-weight:700;font-size:.92rem}
.calc-in select{font:inherit;font-weight:600;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:9px 11px;width:100%;min-height:46px}
.calc-in select:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 22%,transparent)}
.calc-out{padding:16px 18px;background:var(--accent-2);display:grid;gap:12px;align-content:start;min-width:0}
.tot{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:8px}
.tot div{background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:10px 12px;min-width:0}
.tot b{display:block;font-family:var(--serif);font-size:clamp(1.25rem,3.4vw,1.6rem);line-height:1.15;font-variant-numeric:tabular-nums}
.tot .main b{font-size:clamp(1.8rem,5.4vw,2.4rem);color:var(--accent)}.tot span{display:block;font-size:.8rem;color:var(--ink-3);font-weight:700;line-height:1.3}
.calc-out p{margin:0;font-size:.92rem;color:var(--ink-2)}
.calc-f{margin:0;padding:12px 18px;border-top:1px solid var(--line);font-size:.86rem;color:var(--ink-3)}
.btn{display:inline-flex;align-items:center;gap:8px;font:inherit;font-size:.92rem;font-weight:800;background:var(--accent);color:var(--on-accent);border:0;border-radius:var(--r-s);padding:9px 15px;cursor:pointer;min-height:42px;text-decoration:none}
.btn:hover{background:var(--accent-h);color:var(--on-accent)}.btn.sec{background:var(--card);color:var(--accent);border:1.5px solid color-mix(in srgb,var(--accent) 50%,transparent)}
.azioni{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}
.passi{list-style:none;padding:0;margin:0 0 14px;display:grid;gap:4px}.passi li{padding:6px 10px;background:var(--card);border:1px solid var(--line);border-radius:8px;font-variant-numeric:tabular-nums}
.ad-slot{min-height:0;margin:26px 0}
.form{display:grid;gap:12px;max-width:640px}.form label{display:grid;gap:6px;font-weight:700;font-size:.92rem}
.form input,.form textarea{font:inherit;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:9px 11px;width:100%}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:600}.form .check input{width:18px;height:18px;margin-top:3px;flex:none}.hp{position:absolute;left:-9999px}.form .btn{justify-self:start}.ok{background:var(--mute);border:1px solid var(--line-2);padding:14px;border-radius:var(--r-s);max-width:640px}.errore{color:var(--bad,#b3261e);font-weight:700;margin:0}
.disclaimer{margin:42px 0 0;padding:14px 16px;border-radius:var(--r-s);background:var(--mute);font-size:.88rem;color:var(--ink-2)}
footer{margin-top:46px;background:var(--deep);color:var(--on-deep-2);padding:32px 0 26px;font-size:.9rem}
footer a{color:var(--on-deep)}footer h2{font-size:1rem;color:#fff;margin:0 0 10px}footer ul{list-style:none;margin:0;padding:0;display:grid;gap:5px}
.f-grid{display:grid;grid-template-columns:1.4fr 1fr 1fr;gap:26px}.f-grid .logo{margin-bottom:10px}.f-base{border-top:1px solid rgba(255,255,255,.1);margin-top:22px;padding-top:14px;font-size:.84rem}
.f-gradi{grid-template-columns:repeat(4,auto)!important;gap:5px 14px!important}
@media (max-width:860px){nav.menu{display:none}.nav-m{display:block}.calc-g{grid-template-columns:1fr}.calc-in{border-right:0;border-bottom:1px solid var(--line)}
.stats{grid-template-columns:1fr 1fr}.stat:nth-child(2){border-right:0}.stat:nth-child(-n+2){border-bottom:1px solid var(--line)}.f-grid{grid-template-columns:1fr}}
@media (max-width:420px){body{font-size:16px}.logo span{font-size:1rem}.stat{padding:13px 13px}table.dati{font-size:.86rem}table.dati th,table.dati td{padding:7px 8px}}
"""

ICONE = {
    "moon": '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "calc": '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 11h2M12 11h2M16 11h0M8 15h2M12 15h2M8 18h2M12 18h4"/>',
    "table": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M3 14h18M9 4v16"/>',
    "up": '<path d="M4 17l6-6 4 4 6-7"/><path d="M14 8h6v6"/>',
    "doc": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/>',
    "alert": '<path d="M12 3l9.5 17h-19z"/><path d="M12 10v4M12 17.5v.5"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "star": '<path d="M12 3l2.6 5.6 6.1.7-4.5 4.2 1.2 6L12 16.6 6.6 19.5l1.2-6L3.3 9.3l6.1-.7z"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    "cal": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
}

MARCHIO = ('<rect width="40" height="40" rx="9" fill="#111A2E"/>'
           '<path d="M10 13l10 6 10-6M10 19l10 6 10-6M10 25l10 6 10-6" fill="none" stroke="#E0B25A" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
FAVICON_SVG = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">{MARCHIO}</svg>\n'

TEMA_JS = "(function(){try{var t=localStorage.getItem('mp-theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();"

# calcola(dati, grado, colonna) -> {tabella, mese, anno, tetto, prossimo:{col, mese, piu}|null} oppure null se la cella è vuota
APP_JS = r"""
function calcola(D, g, c) {
  var r = D.righe[g]; if (!r) return null;
  var v = r[c]; if (v === null || v === undefined) return null;
  var tetto = null;
  if (D.tetto2.indexOf(g) >= 0 && v >= D.tetti.lvl2 - 0.001) tetto = D.tetti.lvl2;
  if (D.tetto5.indexOf(g) >= 0 && v >= D.tetti.lvl5 - 0.001) tetto = D.tetti.lvl5;
  var m = tetto === null ? v : Math.min(v, tetto);
  var pr = null;
  for (var j = c + 1; j < r.length; j++) {
    if (r[j] !== null) { var mj = r[j]; if (D.tetto2.indexOf(g) >= 0) mj = Math.min(mj, D.tetti.lvl2); if (D.tetto5.indexOf(g) >= 0) mj = Math.min(mj, D.tetti.lvl5);
      if (mj > m + 0.001) { pr = {col: j, mese: mj, piu: Math.round((mj - m) * 100) / 100}; break; } }
  }
  return {tabella: v, mese: m, anno: Math.round(m * 12 * 100) / 100, tetto: tetto, prossimo: pr};
}
if (typeof module !== 'undefined') module.exports = {calcola: calcola};
(function () {
  if (typeof document === 'undefined') return;
  var b = document.querySelector('[data-tema]');
  if (b) b.addEventListener('click', function () {
    var r = document.documentElement, scuro = r.getAttribute('data-theme') === 'dark' || (!r.getAttribute('data-theme') && matchMedia('(prefers-color-scheme: dark)').matches);
    var t = scuro ? 'light' : 'dark'; r.setAttribute('data-theme', t); try { localStorage.setItem('mp-theme', t); } catch (e) {}
  });
  document.querySelectorAll('form[data-correzioni]').forEach(function (form) { form.addEventListener('submit', function (ev) { ev.preventDefault();
    var err = form.querySelector('[data-errore]'); err.hidden = true; if (!form.checkValidity()) { form.reportValidity(); return; }
    var bt = form.querySelector('button'); bt.disabled = true;
    fetch('/', {method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: new URLSearchParams(new FormData(form)).toString()})
      .then(function (r) { if (!r.ok) throw new Error(r.status); form.hidden = true; var ok = form.parentNode.querySelector('[data-ok]'); if (ok) ok.hidden = false; })
      .catch(function () { err.hidden = false; bt.disabled = false; });
  }); });
  var box = document.querySelector('[data-calc]'); if (!box) return;
  var D = JSON.parse(document.getElementById('dati-paga').textContent);
  var sg = box.querySelector('select[name=g]'), sy = box.querySelector('select[name=y]'), out = box.querySelector('[data-out]');
  function soldi(x) { return '$' + x.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); }
  function leggiUrl() {
    var q = new URLSearchParams(location.search);
    if (q.get('g') && D.righe[q.get('g')]) sg.value = q.get('g');
    var y = q.get('y'); if (y !== null && D.slug_col.indexOf(y) >= 0) sy.value = String(D.slug_col.indexOf(y));
  }
  function aggiorna(scrivi) {
    var g = sg.value, c = +sy.value, nome = D.nomi[g], res = calcola(D, g, c), h = '';
    if (!res) {
      var prima = D.righe[g].findIndex(function (x) { return x !== null; });
      h = '<p class="vuoto"><strong>No rate in the 2026 table for ' + esc(nome) + ' with ' + esc(D.colonne[c].toLowerCase()) + ' years of service.</strong> The ' + esc(nome) +
        ' row of the official table starts at “' + esc(D.colonne[prima]) + '”' + (D.righe[g].slice(prima).some(function (x) { return x === null; }) ? ' and has gaps' : '') + '.</p>';
    } else {
      h = '<div class="tot"><div class="main"><span>Monthly basic pay</span><b>' + soldi(res.mese) + '</b></div><div><span>Per year (× 12)</span><b>' + soldi(res.anno) + '</b></div></div>';
      if (res.tetto !== null) h += '<p><span class="cap">At the monthly limit.</span> By law basic pay for this grade cannot go above ' + soldi(res.tetto) + ' a month in 2026; the table already stops there.</p>';
      h += res.prossimo ? '<p><strong>Next step in the table:</strong> “' + esc(D.colonne[res.prossimo.col]) + '” years, ' + soldi(res.prossimo.mese) + ' a month (+' + soldi(res.prossimo.piu) + ').</p>'
        : '<p><strong>Top of the ' + esc(nome) + ' table:</strong> no higher rate at longer service in 2026.</p>';
      h += '<p><a href="/' + D.pagine[g] + '/">Full ' + esc(nome) + ' pay table →</a></p>';
    }
    out.innerHTML = h;
    if (scrivi && history.replaceState) { var q = new URLSearchParams(); q.set('g', g); q.set('y', D.slug_col[c]); history.replaceState(null, '', location.pathname + '?' + q.toString()); }
  }
  leggiUrl(); aggiorna(false);
  sg.addEventListener('change', function () { aggiorna(true); }); sy.addEventListener('change', function () { aggiorna(true); });
})();
"""
