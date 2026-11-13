"""Aspetto e codice del browser di "Statute of Limitations by State": CSS (chiaro e scuro), icone, marchio, tema, calcolatore.

Identità: blu notte (tribunale, carta intestata), ottone per gli accenti, carta avorio come sfondo; rosso solo per gli avvisi.
Caratteri OFL: Public Sans (testo) e Newsreader (titoli e citazioni di legge).
Il calcolatore (CALC_JS) è lo stesso codice usato nel browser e provato da verifica.py con node su più di 300 casi contro un
calcolo Python scritto a parte.
"""

CSS = """
@font-face{font-family:"Public Sans";src:url(/assets/fonts/public-sans.woff2) format("woff2");font-weight:100 900;font-style:normal;font-display:swap}
@font-face{font-family:"Newsreader";src:url(/assets/fonts/newsreader.woff2) format("woff2");font-weight:200 800;font-style:normal;font-display:swap}
:root{--bg:#F6F4EF;--card:#FFFFFF;--ink:#1A1F2B;--ink-2:#3A4152;--ink-3:#5A6171;--line:#E1DDD3;--line-2:#C9C3B6;
--deep:#16213A;--deep-2:#1F2C4A;--on-deep:#EEF1F7;--on-deep-2:#B9C2D6;--accent:#2449A6;--accent-h:#1A3780;--accent-2:#E8EDF8;--on-accent:#FFFFFF;
--warm:#B7791F;--warm-ink:#8A5A12;--warm-2:#FBF1DE;--red:#A3352B;--red-2:#FBEAE7;--ok:#2D6A4F;--ok-2:#E4F2EA;--mute:#EFECE4;
--sh-1:0 1px 2px rgba(22,33,58,.06),0 1px 1px rgba(22,33,58,.04);--sh-2:0 22px 44px -26px rgba(22,33,58,.45),0 2px 8px rgba(22,33,58,.06);
--r:14px;--r-s:10px;--serif:"Newsreader",Charter,Georgia,serif;--sans:"Public Sans",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0E1320;--card:#161D2E;--ink:#E7EAF1;--ink-2:#C0C6D4;--ink-3:#9AA2B4;--line:#26304A;--line-2:#36415E;
--deep:#0A0F1A;--deep-2:#121A2B;--on-deep:#E7EAF1;--on-deep-2:#A9B2C6;--accent:#8FB0FF;--accent-h:#B5CBFF;--accent-2:#1A2642;--on-accent:#0A1020;
--warm:#E3B25C;--warm-ink:#F0C77E;--warm-2:#2E2414;--red:#F08A7E;--red-2:#3A1D1A;--ok:#7FD1A6;--ok-2:#14291F;--mute:#1A2236;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 22px 44px -26px rgba(0,0,0,.85),0 2px 8px rgba(0,0,0,.4)}}
:root[data-theme="dark"]{--bg:#0E1320;--card:#161D2E;--ink:#E7EAF1;--ink-2:#C0C6D4;--ink-3:#9AA2B4;--line:#26304A;--line-2:#36415E;
--deep:#0A0F1A;--deep-2:#121A2B;--on-deep:#E7EAF1;--on-deep-2:#A9B2C6;--accent:#8FB0FF;--accent-h:#B5CBFF;--accent-2:#1A2642;--on-accent:#0A1020;
--warm:#E3B25C;--warm-ink:#F0C77E;--warm-2:#2E2414;--red:#F08A7E;--red-2:#3A1D1A;--ok:#7FD1A6;--ok-2:#14291F;--mute:#1A2236;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 22px 44px -26px rgba(0,0,0,.85),0 2px 8px rgba(0,0,0,.4)}
*{box-sizing:border-box}[hidden]{display:none!important}html{-webkit-text-size-adjust:100%;scroll-padding-top:16px}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:17px;line-height:1.62;overflow-wrap:break-word}
a{color:var(--accent);text-underline-offset:2px;text-decoration-thickness:1px}a:hover{color:var(--accent-h)}
:focus-visible{outline:3px solid var(--warm);outline-offset:2px;border-radius:4px}
.skip{position:absolute;left:-9999px;top:8px;background:var(--card);color:var(--ink);padding:8px 14px;border-radius:8px;z-index:50}.skip:focus{left:12px}
.ico{width:1.15em;height:1.15em;flex:none;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;vertical-align:-.2em}
.wrap{max-width:1100px;margin:0 auto;padding:0 16px}
header.top{background:var(--deep);color:var(--on-deep);position:relative;z-index:20;border-bottom:1px solid rgba(255,255,255,.07)}
header.top .wrap{display:flex;align-items:center;gap:10px;min-height:62px}
.logo{display:flex;align-items:center;gap:10px;font-family:var(--serif);font-weight:700;font-size:1.22rem;color:var(--on-deep);text-decoration:none;white-space:nowrap;margin-right:auto;line-height:1.1}
.logo:hover{color:#fff}.logo img{width:34px;height:34px;flex:none;display:block}.logo b{color:var(--warm);font-weight:inherit}
nav.menu{display:flex;gap:2px;font-size:.93rem}
nav.menu a{color:var(--on-deep-2);text-decoration:none;padding:7px 10px;border-radius:8px;white-space:nowrap}
nav.menu a:hover,nav.menu a[aria-current]{color:#fff;background:rgba(255,255,255,.09)}
.tema{display:grid;place-items:center;width:40px;height:40px;border-radius:10px;border:1px solid rgba(255,255,255,.22);background:none;color:var(--on-deep);cursor:pointer;flex:none}
.tema:hover{border-color:var(--warm)}.tema .ico{width:19px;height:19px}
.tema .i-sun{display:none}:root[data-theme="dark"] .tema .i-sun{display:block}:root[data-theme="dark"] .tema .i-moon{display:none}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .tema .i-sun{display:block}:root:not([data-theme="light"]) .tema .i-moon{display:none}}
.nav-m{display:none}
.nav-m summary{list-style:none;cursor:pointer;display:grid;place-items:center;width:40px;height:40px;border:1px solid rgba(255,255,255,.25);border-radius:10px;color:var(--on-deep)}
.nav-m summary::-webkit-details-marker{display:none}.nav-m[open] summary{background:rgba(255,255,255,.1);border-color:var(--warm)}
.nav-m nav{position:absolute;left:16px;right:16px;top:calc(100% + 4px);background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-2);padding:8px;display:grid;grid-template-columns:1fr 1fr;gap:2px}
.nav-m nav a{padding:11px 12px;border-radius:8px;color:var(--ink);text-decoration:none;font-weight:700;font-size:.95rem}.nav-m nav a:hover{background:var(--accent-2)}
.band{background:var(--deep);color:var(--on-deep);position:relative;overflow:hidden}
.band::before{content:"";position:absolute;inset:0;background:radial-gradient(560px 300px at 96% -12%,rgba(183,121,31,.34),transparent 64%),radial-gradient(700px 320px at -6% 130%,rgba(143,176,255,.18),transparent 62%),linear-gradient(180deg,var(--deep) 0,var(--deep-2) 100%)}
.band::after{content:"§";position:absolute;right:18px;bottom:-70px;font-family:var(--serif);font-size:260px;line-height:1;color:var(--on-deep);opacity:.06;pointer-events:none}
.band-in{position:relative;z-index:1;padding:28px 16px 80px}
.band.corta .band-in{padding-bottom:40px}
.eyebrow{display:inline-flex;align-items:center;gap:8px;font-size:.78rem;font-weight:800;letter-spacing:.11em;text-transform:uppercase;color:var(--warm);margin:0 0 10px}
h1,h2,h3{font-family:var(--serif);font-weight:700;letter-spacing:-.005em}
h1{font-size:clamp(1.85rem,5vw,2.75rem);line-height:1.12;margin:0 0 12px;text-wrap:balance;max-width:900px}
.band h1{color:#fff}
.sub{font-size:1.07rem;color:var(--on-deep-2);margin:0 0 14px;max-width:780px}.sub strong{color:#fff}
.briciole{font-size:.85rem;color:var(--on-deep-2);margin:0 0 14px}.briciole a{color:var(--on-deep)}
h2{font-size:clamp(1.38rem,3vw,1.7rem);line-height:1.22;margin:44px 0 12px;scroll-margin-top:16px;text-wrap:balance}
h3{font-size:1.14rem;margin:22px 0 8px}
p{margin:0 0 14px}
.small{font-size:.87rem;color:var(--ink-3)}
.testo p,.testo li{max-width:790px}.testo li{margin-bottom:8px}.testo ul,.testo ol{padding-left:22px}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:20px;min-width:0;box-shadow:var(--sh-1)}
.pull{margin-top:-58px;position:relative;z-index:2}
.cifre{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;padding:0;overflow:hidden;box-shadow:var(--sh-2)}
.cifra{padding:18px 20px;border-right:1px solid var(--line);min-width:0}.cifra:last-of-type{border-right:0}
.cifra b{display:block;font-family:var(--serif);font-size:clamp(1.4rem,3.4vw,1.95rem);line-height:1.1;font-variant-numeric:tabular-nums}
.cifra>span{display:block;font-size:.86rem;color:var(--ink-3);line-height:1.35;margin-top:6px}.cifra.main b{color:var(--accent)}
.asof{margin:0;padding:10px 20px;background:var(--mute);border-top:1px solid var(--line);font-size:.86rem;color:var(--ink-2);grid-column:1/-1}
.asof .ico{color:var(--ok)}
.avviso{position:relative;background:var(--red-2);border:1px solid color-mix(in srgb,var(--red) 40%,transparent);padding:13px 16px 13px 46px;border-radius:var(--r-s);font-size:.95rem;margin:18px 0;color:var(--ink)}
.avviso .ico{position:absolute;left:15px;top:15px;color:var(--red);width:20px;height:20px}.avviso p{margin:0 0 6px}.avviso p:last-child{margin:0}
.nota{position:relative;background:var(--warm-2);border:1px solid color-mix(in srgb,var(--warm) 40%,transparent);padding:13px 16px 13px 46px;border-radius:var(--r-s);font-size:.95rem;margin:18px 0;color:var(--ink)}
.nota .ico{position:absolute;left:15px;top:15px;color:var(--warm-ink);width:20px;height:20px}.nota p{margin:0 0 6px}.nota p:last-child{margin:0}
.nota.info{background:var(--accent-2);border-color:color-mix(in srgb,var(--accent) 35%,transparent)}.nota.info .ico{color:var(--accent)}
blockquote.legge{margin:12px 0 6px;padding:14px 18px;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--warm);border-radius:0 var(--r-s) var(--r-s) 0;font-family:var(--serif);font-size:1.06rem;line-height:1.55;color:var(--ink);max-width:860px}
blockquote.legge p{margin:0 0 8px}blockquote.legge p:last-child{margin:0}
blockquote.legge p+p::before{content:"[…] ";color:var(--ink-3)}
.cita{font-size:.88rem;color:var(--ink-3);margin:0 0 18px;max-width:860px}.cita a{font-weight:700}
.var{display:grid;gap:12px;margin:0 0 8px;padding:0;list-style:none}
.var>li{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:16px 18px;box-shadow:var(--sh-1)}
.var h3{margin:0 0 4px;display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 12px}
.periodo{font-family:var(--sans);font-size:.85rem;font-weight:800;color:var(--on-accent);background:var(--accent);border-radius:999px;padding:2px 11px;white-space:nowrap}
.tab{border:1px solid var(--line);border-radius:var(--r);background:var(--card);box-shadow:var(--sh-1);overflow-x:auto;-webkit-overflow-scrolling:touch;margin:0 0 8px}
table.dati{border-collapse:collapse;width:100%;font-size:.93rem}
table.dati th,table.dati td{padding:9px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
table.dati th{background:var(--mute);font-size:.74rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-2)}
table.dati td.n,table.dati th.n{white-space:nowrap;font-variant-numeric:tabular-nums}
table.dati tr:last-child td{border-bottom:0}
table.dati tr.qui td{background:var(--accent-2);font-weight:700}
table.dati caption{caption-side:bottom;text-align:left;padding:8px 12px;font-size:.84rem;color:var(--ink-3)}
table.dati td small{display:block;color:var(--ink-3);font-size:.8rem;line-height:1.35}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;margin:0;padding:0;list-style:none}
.griglia a{display:block;height:100%;background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:16px;text-decoration:none;color:var(--ink);box-shadow:var(--sh-1)}
.griglia a:hover{border-color:var(--accent)}.griglia b{display:block;font-family:var(--serif);font-size:1.12rem;margin-bottom:4px}
.griglia span{display:block;font-size:.88rem;color:var(--ink-3)}.griglia em{font-style:normal;color:var(--accent);font-weight:800;font-variant-numeric:tabular-nums}
.pillole{display:flex;flex-wrap:wrap;gap:6px;margin:0;padding:0;list-style:none}
.pillole a{display:inline-block;padding:6px 12px;border-radius:999px;border:1px solid var(--line-2);background:var(--card);text-decoration:none;font-weight:700;font-size:.9rem;color:var(--ink-2)}
.pillole a:hover,.pillole a[aria-current]{border-color:var(--accent);color:var(--accent)}
.ecc{border-top:1px solid var(--line);padding:6px 0 4px}.ecc h3{margin:16px 0 6px;font-size:1.08rem}
.faq{border-top:1px solid var(--line);padding:4px 0 6px}.faq h3{margin:16px 0 6px;font-size:1.06rem}
.fonti-box{margin-top:40px;padding:18px 20px;background:var(--card);border:1px solid var(--line);border-radius:var(--r)}
.fonti-box h2{margin:0 0 10px;font-size:1.2rem;display:flex;align-items:center;gap:9px}
.fonti-box ol{margin:0;padding-left:22px;font-size:.92rem}.fonti-box li{margin-bottom:8px}
.ref{font-size:max(.72em,11px);line-height:0;margin-left:1px}.ref a{text-decoration:none;font-weight:700}
.disclaimer{margin:34px 0 0;padding:14px 16px;border-radius:var(--r-s);background:var(--mute);font-size:.9rem;color:var(--ink-2)}
.ad-slot{min-height:0;margin:26px 0}
.calc{display:grid;gap:14px}
.calc form{display:grid;grid-template-columns:repeat(3,minmax(0,1fr)) auto;gap:12px;align-items:end}
.calc.uno form{grid-template-columns:minmax(0,1fr) auto;max-width:520px}
.calc label{display:grid;gap:6px;font-weight:700;font-size:.9rem;color:var(--ink-2)}
.calc select,.calc input{font:inherit;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:10px 12px;min-height:48px;width:100%}
.calc select:focus,.calc input:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 22%,transparent)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;font:inherit;font-size:.95rem;font-weight:800;background:var(--accent);color:var(--on-accent);border:0;border-radius:var(--r-s);padding:10px 18px;cursor:pointer;min-height:48px;text-decoration:none}
.btn:hover{background:var(--accent-h);color:var(--on-accent)}
.esito{border:1px solid var(--line);border-radius:var(--r);background:var(--bg);padding:16px 18px}
.esito h3{margin:0 0 10px;font-size:1.15rem}
.esito ol{list-style:none;margin:0 0 10px;padding:0;display:grid;gap:8px}
.esito ol>li{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:4px 14px;align-items:baseline;padding:10px 12px;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s)}
.esito ol>li b{font-family:var(--serif);font-size:1.25rem;white-space:nowrap;font-variant-numeric:tabular-nums}
.esito ol>li span{font-size:.9rem;color:var(--ink-2)}.esito ol>li small{grid-column:1/-1;color:var(--ink-3);font-size:.82rem}
.esito ol>li.rip b{color:var(--ink-2)}.esito ol>li.no b{color:var(--red);font-size:1rem;white-space:normal}
.esito .stato{font-weight:700}.esito .passato{color:var(--red)}
.esito ul{margin:6px 0 0;padding-left:20px;font-size:.93rem}
.due{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px}
footer{margin-top:56px;background:var(--deep);color:var(--on-deep-2);font-size:.9rem}
footer .wrap{padding-top:32px;padding-bottom:30px}
footer a{color:var(--on-deep)}footer h2{color:#fff;font-size:1rem;margin:0 0 8px}
.f-grid{display:grid;grid-template-columns:1.4fr 1fr 1fr;gap:28px}
footer ul{list-style:none;margin:0;padding:0}footer li{margin-bottom:6px}
.f-base{margin:24px 0 0;padding-top:16px;border-top:1px solid rgba(255,255,255,.12);font-size:.84rem}
@media (max-width:900px){nav.menu{display:none}.nav-m{display:block}.f-grid{grid-template-columns:1fr 1fr}.f-grid>div:first-child{grid-column:1/-1}.calc form{grid-template-columns:1fr 1fr}}
@media (max-width:720px){.cifre{grid-template-columns:1fr}.cifra{border-right:0;border-bottom:1px solid var(--line)}.due{grid-template-columns:1fr}}
@media (max-width:560px){.calc form,.calc.uno form{grid-template-columns:1fr}.esito ol>li{grid-template-columns:1fr}}
@media (max-width:480px){body{font-size:16px}.f-grid{grid-template-columns:1fr}.logo{font-size:1rem;white-space:normal}.logo span{max-width:200px}.cifra{padding:14px 14px}.band-in{padding-top:22px}
table.dati th,table.dati td{padding:8px 9px}.nav-m nav{grid-template-columns:1fr}blockquote.legge{padding:12px 14px;font-size:1rem}}
@media print{header.top,footer,.tema,.nav-m,.ad-slot{display:none}.band{background:none;color:#000}.band h1{color:#000}}
"""

ICONE = {
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "moon": '<path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6 6 6M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4"/>',
    "check": '<circle cx="12" cy="12" r="9.5"/><path d="M8 12.5l2.8 2.8L16.5 9.5"/>',
    "calendar": '<rect x="3" y="4.5" width="18" height="17" rx="2.5"/><path d="M16 2.5v4M8 2.5v4M3 10h18"/>',
    "alert": '<path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17h.01"/>',
    "info": '<circle cx="12" cy="12" r="9.5"/><path d="M12 11v6M12 7.5h.01"/>',
    "doc": '<path d="M14 2.5H6.5A2 2 0 0 0 4.5 4.5v15a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V8z"/><path d="M14 2.5V8h5.5M8 13h8M8 17h5"/>',
    "shield": '<path d="M12 22s8-3.5 8-10V5.5L12 2.5 4 5.5V12c0 6.5 8 10 8 10z"/><path d="M8.5 12l2.5 2.5 4.5-4.5"/>',
    "lock": '<rect x="4.5" y="10.5" width="15" height="11" rx="2.5"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/>',
    "scale": '<path d="M12 3v18M7 21h10M5 7h14M5 7l-3 7a3 3 0 0 0 6 0zM19 7l-3 7a3 3 0 0 0 6 0z"/>',
    "hourglass": '<path d="M6 2.5h12M6 21.5h12M7 2.5c0 5 5 6.5 5 9.5s-5 4.5-5 9.5M17 2.5c0 5-5 6.5-5 9.5s5 4.5 5 9.5"/>',
    "map": '<path d="M9 4.5 3.5 6.5v13L9 17.5l6 2 5.5-2v-13L15 6.5z"/><path d="M9 4.5v13M15 6.5v13"/>',
    "pause": '<circle cx="12" cy="12" r="9.5"/><path d="M10 8.5v7M14 8.5v7"/>',
    "building": '<path d="M3 21h18M5 21V9l7-5 7 5v12M9 21v-6h6v6M8.5 11h.01M15.5 11h.01"/>',
    "history": '<path d="M3.5 12a8.5 8.5 0 1 0 2.6-6.1"/><path d="M3 4v4.5h4.5M12 7.5V12l3 2"/>',
}

# Marchio: tessera blu notte con il segno di paragrafo e una clessidra stilizzata in ottone
MARCHIO = ('<rect width="40" height="40" rx="10" fill="#16213A"/>'
           '<path d="M12 9.5h16M12 30.5h16" stroke="#E3B25C" stroke-width="2.6" stroke-linecap="round"/>'
           '<path d="M13.5 9.5c0 6 6.5 6.8 6.5 10.5s-6.5 4.5-6.5 10.5M26.5 9.5c0 6-6.5 6.8-6.5 10.5s6.5 4.5 6.5 10.5" fill="none" stroke="#EEF1F7" stroke-width="2.2" stroke-linecap="round"/>'
           '<path d="M16.5 28.5c1-2.4 2.3-3.4 3.5-3.4s2.5 1 3.5 3.4z" fill="#E3B25C"/>')
FAVICON_SVG = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">{MARCHIO}</svg>\n'

TEMA_JS = "(function(){try{var t=localStorage.getItem('sol-tema');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();"

# Calcolo della scadenza: stesso codice nel browser e nella prova con node (verifica.py). Date come stringhe AAAA-MM-GG.
CALC_JS = r"""
var SOL=(function(){
'use strict';
function bis(a){return (a%4===0&&a%100!==0)||a%400===0;}
function pad(n){return (n<10?'0':'')+n;}
function parte(s){var m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(s||'');if(!m)return null;var a=+m[1],me=+m[2],g=+m[3];
  var gm=[31,bis(a)?29:28,31,30,31,30,31,31,30,31,30,31];if(me<1||me>12||g<1||g>gm[me-1])return null;return [a,me,g];}
function iso(p){return p[0]+'-'+pad(p[1])+'-'+pad(p[2]);}
function piuAnni(s,n){var p=parte(s);var a=p[0]+n,me=p[1],g=p[2];if(me===2&&g===29&&!bis(a))g=28;return iso([a,me,g]);}
function piuGiorni(s,n){var p=parte(s);var d=new Date(Date.UTC(p[0],p[1]-1,p[2]));d.setUTCDate(d.getUTCDate()+n);
  return iso([d.getUTCFullYear(),d.getUTCMonth()+1,d.getUTCDate()]);}
function calcola(cella,data){
  if(!parte(data))return null;
  var out={varianti:[],repose:null};
  cella.v.forEach(function(v){
    if(v.tr&&data<v.tr.data){out.varianti.push({l:v.l,cit:v.cit,errore:v.tr.msg});return;}
    var anni=v.a,l=v.l,cit=v.cit;
    if(v.prima&&data<=v.prima.fino){anni=v.prima.a;l=v.prima.l;cit=v.prima.cit;}
    var inizio=v.g?piuGiorni(data,v.g):data;
    out.varianti.push({l:l,cit:cit,anni:anni,scadenza:piuAnni(inizio,anni),nd:v.nd||''});
  });
  if(cella.r)out.repose={l:cella.r.l,cit:cella.r.cit,anni:cella.r.a,scadenza:piuAnni(data,cella.r.a)};
  return out;
}
return {calcola:calcola,piuAnni:piuAnni,piuGiorni:piuGiorni,parte:parte};
})();
if(typeof module!=='undefined'){module.exports=SOL;}
"""

APP_JS = r"""
(function(){
'use strict';
if(typeof document==='undefined')return;
var b=document.querySelector('[data-tema]');
if(b){b.addEventListener('click',function(){var r=document.documentElement;var dark=r.getAttribute('data-theme')==='dark'||(!r.getAttribute('data-theme')&&window.matchMedia('(prefers-color-scheme: dark)').matches);var t=dark?'light':'dark';r.setAttribute('data-theme',t);try{localStorage.setItem('sol-tema',t);}catch(e){}});}
var MESI=['January','February','March','April','May','June','July','August','September','October','November','December'];
function lunga(s){var p=SOL.parte(s);return p[2]+' '+MESI[p[1]-1]+' '+p[0];}
function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function oggi(){var d=new Date();return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2);}
function giorniTra(a,b){var pa=SOL.parte(a),pb=SOL.parte(b);return Math.round((Date.UTC(pb[0],pb[1]-1,pb[2])-Date.UTC(pa[0],pa[1]-1,pa[2]))/864e5);}
var el=document.getElementById('dati-calc');if(!el)return;
var D=JSON.parse(el.textContent);
document.querySelectorAll('[data-calc]').forEach(function(box){
  var f=box.querySelector('form'),out=box.querySelector('.esito');
  var sS=f.querySelector('[name=stato]'),sC=f.querySelector('[name=causa]'),dI=f.querySelector('[name=data]'),lab=f.querySelector('[data-etichetta]');
  function cella(){var s=sS?sS.value:box.getAttribute('data-stato'),c=sC?sC.value:box.getAttribute('data-causa');return D.celle[s+'/'+c]||null;}
  function aggiornaEtichetta(){var c=sC?sC.value:box.getAttribute('data-causa');if(lab&&D.date[c])lab.textContent=D.date[c];
    if(sC&&sS){var ok=!!D.celle[sS.value+'/'+c];f.querySelector('[data-manca]').hidden=ok;}}
  if(sC)sC.addEventListener('change',aggiornaEtichetta);if(sS)sS.addEventListener('change',aggiornaEtichetta);aggiornaEtichetta();
  f.addEventListener('submit',function(ev){ev.preventDefault();
    var c=cella();if(!c){out.hidden=false;out.innerHTML='<p>We have not published this combination: the statute does not state its own deadline. Ask a licensed attorney in that state.</p>';return;}
    var r=SOL.calcola(c,dI.value);if(!r){out.hidden=false;out.innerHTML='<p>Enter a valid date.</p>';return;}
    var h='<h3>General deadline: '+esc(c.n)+'</h3><ol>';var t=oggi();
    r.varianti.forEach(function(v){
      if(v.errore){h+='<li class="no"><span>'+esc(v.l)+' · '+esc(v.cit)+'</span><b>'+esc(v.errore)+'</b></li>';return;}
      var g=giorniTra(t,v.scadenza);var st=g>=0?'<span class="stato">'+g+' days from today</span>':'<span class="stato passato">This general date is in the past. Exceptions can change it: talk to a licensed attorney.</span>';
      h+='<li><span>'+esc(v.l)+' · '+v.anni+(v.anni===1?' year':' years')+' · '+esc(v.cit)+'</span><b>'+lunga(v.scadenza)+'</b>'+'<small>'+st+(v.nd?' '+esc(v.nd):'')+'</small></li>';});
    if(r.repose)h+='<li class="rip"><span>'+esc(r.repose.l)+' (outer limit) · '+r.repose.anni+' years · '+esc(r.repose.cit)+'</span><b>'+lunga(r.repose.scadenza)+'</b><small>Counted from the date you entered. Many exceptions do not extend past this date.</small></li>';
    h+='</ol>';
    if(c.e&&c.e.length){h+='<p class="small"><strong>Exceptions that can move this date:</strong></p><ul>'+c.e.map(function(x){return '<li>'+esc(x)+'</li>';}).join('')+'</ul>';}
    h+='<p class="small">Estimate, not legal advice. Deadlines can be shorter or longer. Talk to a licensed attorney in your state. <a href="'+c.u+'">Read the statute and every exception</a>.</p>';
    out.hidden=false;out.innerHTML=h;});
});
})();
"""
