"""Aspetto e codice del browser di Heat Pump Grants UK: CSS (chiaro e scuro), icone, marchio, tema e filtro delle tabelle.

Identità: blu-verde scuro (casa, aria), arancione (calore) e verde acqua per i dati. Caratteri OFL: Figtree (testo) e
Source Serif 4 (titoli). Colore delle barre validato per chiaro (#00897A) e scuro (#1FA08E) con lo strumento dei grafici.
"""

CSS = """
@font-face{font-family:"Figtree";src:url(/assets/fonts/figtree.woff2) format("woff2");font-weight:300 900;font-style:normal;font-display:swap}
@font-face{font-family:"Source Serif 4";src:url(/assets/fonts/source-serif-4.woff2) format("woff2");font-weight:200 900;font-style:normal;font-display:swap}
:root{--bg:#F5F6F3;--card:#FFFFFF;--ink:#14211F;--ink-2:#36474A;--ink-3:#566668;--line:#DDE3DF;--line-2:#C3CCC7;
--deep:#0E2A2F;--deep-2:#14373D;--on-deep:#ECF4F2;--on-deep-2:#B3C9C6;--accent:#0B6E78;--accent-h:#085660;--accent-2:#E3F0EF;--on-accent:#FFFFFF;
--warm:#E0662B;--warm-ink:#A9440F;--warm-2:#FCEBDF;--ok:#1E7A4F;--ok-2:#E3F3EA;--mute:#ECEFEB;--bar:#00897A;--bar-2:#C9DDD9;
--sh-1:0 1px 2px rgba(14,42,47,.06),0 1px 1px rgba(14,42,47,.04);--sh-2:0 22px 44px -26px rgba(14,42,47,.45),0 2px 8px rgba(14,42,47,.06);
--r:14px;--r-s:10px;--serif:"Source Serif 4",Charter,Georgia,serif;--sans:"Figtree",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0B1416;--card:#122023;--ink:#E5EFEE;--ink-2:#BCCDCB;--ink-3:#93A7A5;--line:#203336;--line-2:#31494C;
--deep:#071012;--deep-2:#0E1F22;--on-deep:#E5EFEE;--on-deep-2:#A1B8B5;--accent:#6FC7CF;--accent-h:#9ADBE0;--accent-2:#11313A;--on-accent:#04191C;
--warm:#F2925A;--warm-ink:#F5A877;--warm-2:#2F1C10;--ok:#6FD3A0;--ok-2:#12291E;--mute:#152629;--bar:#1FA08E;--bar-2:#25403F;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 22px 44px -26px rgba(0,0,0,.85),0 2px 8px rgba(0,0,0,.4)}}
:root[data-theme="dark"]{--bg:#0B1416;--card:#122023;--ink:#E5EFEE;--ink-2:#BCCDCB;--ink-3:#93A7A5;--line:#203336;--line-2:#31494C;
--deep:#071012;--deep-2:#0E1F22;--on-deep:#E5EFEE;--on-deep-2:#A1B8B5;--accent:#6FC7CF;--accent-h:#9ADBE0;--accent-2:#11313A;--on-accent:#04191C;
--warm:#F2925A;--warm-ink:#F5A877;--warm-2:#2F1C10;--ok:#6FD3A0;--ok-2:#12291E;--mute:#152629;--bar:#1FA08E;--bar-2:#25403F;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 22px 44px -26px rgba(0,0,0,.85),0 2px 8px rgba(0,0,0,.4)}
*{box-sizing:border-box}[hidden]{display:none!important}html{-webkit-text-size-adjust:100%;scroll-padding-top:16px}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:17px;line-height:1.6;overflow-wrap:break-word}
a{color:var(--accent);text-underline-offset:2px;text-decoration-thickness:1px}a:hover{color:var(--accent-h)}
:focus-visible{outline:3px solid var(--warm);outline-offset:2px;border-radius:4px}
.skip{position:absolute;left:-9999px;top:8px;background:var(--card);color:var(--ink);padding:8px 14px;border-radius:8px;z-index:50}.skip:focus{left:12px}
.ico{width:1.15em;height:1.15em;flex:none;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;vertical-align:-.2em}
.wrap{max-width:1100px;margin:0 auto;padding:0 16px}
header.top{background:var(--deep);color:var(--on-deep);position:relative;z-index:20;border-bottom:1px solid rgba(255,255,255,.07)}
header.top .wrap{display:flex;align-items:center;gap:10px;min-height:62px}
.logo{display:flex;align-items:center;gap:10px;font-family:var(--serif);font-weight:700;font-size:1.2rem;color:var(--on-deep);text-decoration:none;white-space:nowrap;margin-right:auto;line-height:1.1}
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
.band::before{content:"";position:absolute;inset:0;background:radial-gradient(520px 300px at 96% -12%,rgba(224,102,43,.34),transparent 64%),radial-gradient(700px 320px at -6% 130%,rgba(111,199,207,.20),transparent 62%),linear-gradient(180deg,var(--deep) 0,var(--deep-2) 100%)}
.band::after{content:"";position:absolute;right:-20px;bottom:-30px;width:360px;height:190px;opacity:.13;background:repeating-radial-gradient(circle at 100% 100%,var(--on-deep) 0 2px,transparent 2px 20px);-webkit-mask:linear-gradient(90deg,transparent 0,#000 100%);mask:linear-gradient(90deg,transparent 0,#000 100%)}
.band-in{position:relative;z-index:1;padding:28px 16px 80px}
.band.corta .band-in{padding-bottom:40px}
.eyebrow{display:inline-flex;align-items:center;gap:8px;font-size:.78rem;font-weight:800;letter-spacing:.11em;text-transform:uppercase;color:var(--warm);margin:0 0 10px}
h1,h2,h3{font-family:var(--serif);font-weight:700;letter-spacing:-.01em}
h1{font-size:clamp(1.8rem,5vw,2.7rem);line-height:1.12;margin:0 0 12px;text-wrap:balance;max-width:900px}
.band h1{color:#fff}
.sub{font-size:1.07rem;color:var(--on-deep-2);margin:0 0 14px;max-width:760px}.sub strong{color:#fff}
.briciole{font-size:.85rem;color:var(--on-deep-2);margin:0 0 14px}.briciole a{color:var(--on-deep)}
h2{font-size:clamp(1.35rem,3vw,1.66rem);line-height:1.22;margin:44px 0 12px;scroll-margin-top:16px;text-wrap:balance}
h3{font-size:1.12rem;margin:22px 0 8px}
p{margin:0 0 14px}
.small{font-size:.87rem;color:var(--ink-3)}
.testo p,.testo li{max-width:790px}.testo li{margin-bottom:8px}.testo ul,.testo ol{padding-left:22px}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:20px;min-width:0;box-shadow:var(--sh-1)}
.pull{margin-top:-58px;position:relative;z-index:2}
.cifre{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0;padding:0;overflow:hidden;box-shadow:var(--sh-2)}
.cifra{padding:18px 20px;border-right:1px solid var(--line);min-width:0}.cifra:last-of-type{border-right:0}
.cifra b{display:block;font-family:var(--serif);font-size:clamp(1.4rem,3.4vw,1.95rem);line-height:1.1;font-variant-numeric:tabular-nums}
.cifra span{display:block;font-size:.84rem;color:var(--ink-3);line-height:1.35;margin-top:6px}.cifra.main b{color:var(--accent)}
.asof{margin:0;padding:10px 20px;background:var(--mute);border-top:1px solid var(--line);font-size:.86rem;color:var(--ink-2);grid-column:1/-1}
.asof .ico{color:var(--ok)}
.nota{position:relative;background:var(--warm-2);border:1px solid color-mix(in srgb,var(--warm) 40%,transparent);padding:13px 16px 13px 46px;border-radius:var(--r-s);font-size:.95rem;margin:18px 0;color:var(--ink)}
.nota .ico{position:absolute;left:15px;top:15px;color:var(--warm-ink);width:20px;height:20px}.nota p{margin:0 0 6px}.nota p:last-child{margin:0}
.nota.info{background:var(--accent-2);border-color:color-mix(in srgb,var(--accent) 35%,transparent)}.nota.info .ico{color:var(--accent)}
.nota.ok{background:var(--ok-2);border-color:color-mix(in srgb,var(--ok) 35%,transparent)}.nota.ok .ico{color:var(--ok)}
.tab{border:1px solid var(--line);border-radius:var(--r);background:var(--card);box-shadow:var(--sh-1);overflow-x:auto;-webkit-overflow-scrolling:touch;margin:0 0 8px}
table.dati{border-collapse:collapse;width:100%;font-size:.93rem}
table.dati th,table.dati td{padding:9px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
table.dati th{background:var(--mute);font-size:.74rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-2)}
table.dati td.n,table.dati th.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
table.dati tr:last-child td{border-bottom:0}table.dati tfoot td{font-weight:800;background:var(--mute)}
table.dati tr.qui td{background:var(--accent-2);font-weight:700}
table.dati caption{caption-side:bottom;text-align:left;padding:8px 12px;font-size:.84rem;color:var(--ink-3)}
.barre{list-style:none;margin:0 0 8px;padding:14px 16px;display:grid;gap:7px}
.barre li{display:grid;grid-template-columns:8.6em minmax(0,1fr);align-items:center;gap:10px;font-size:.88rem}
.barre .et{color:var(--ink-2);font-variant-numeric:tabular-nums;white-space:nowrap}
.barre .tr{display:flex;align-items:center;gap:8px;min-width:0}
.barre .b{display:block;height:14px;min-width:2px;background:var(--bar);border-radius:0 4px 4px 0;flex:none}
.barre .b.zero{background:var(--bar-2)}
.barre .v{color:var(--ink);font-weight:700;font-variant-numeric:tabular-nums;white-space:nowrap}
.barre li:hover .b{filter:brightness(1.12)}
.card+.card{margin-top:14px}
.barre-h{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;padding:12px 16px 0;margin:0}
.barre-h h3{margin:0;font-size:1rem}
.cerca{display:flex;gap:8px;max-width:620px;margin:6px 0 12px}
.cerca input{font:inherit;flex:1;min-width:0;border-radius:var(--r-s);border:1.5px solid var(--line-2);background:var(--card);color:var(--ink);padding:11px 14px;min-height:48px}
.cerca input:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 22%,transparent)}
.band .cerca input{border-color:rgba(255,255,255,.3);background:rgba(255,255,255,.08);color:#fff}
.band .cerca input::placeholder{color:var(--on-deep-2)}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;margin:0;padding:0;list-style:none}
.griglia a{display:block;height:100%;background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:16px;text-decoration:none;color:var(--ink);box-shadow:var(--sh-1)}
.griglia a:hover{border-color:var(--accent)}.griglia b{display:block;font-family:var(--serif);font-size:1.12rem;margin-bottom:4px}
.griglia span{display:block;font-size:.88rem;color:var(--ink-3)}.griglia em{font-style:normal;color:var(--accent);font-weight:800;font-variant-numeric:tabular-nums}
.pillole{display:flex;flex-wrap:wrap;gap:6px;margin:0;padding:0;list-style:none}
.pillole a{display:inline-block;padding:6px 12px;border-radius:999px;border:1px solid var(--line-2);background:var(--card);text-decoration:none;font-weight:700;font-size:.9rem;color:var(--ink-2)}
.pillole a:hover,.pillole a[aria-current]{border-color:var(--accent);color:var(--accent)}
.grant{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:0 0 10px;padding:0;list-style:none}
.grant li{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--warm);border-radius:var(--r-s);padding:14px 16px;box-shadow:var(--sh-1)}
.grant b{display:block;font-family:var(--serif);font-size:1.6rem;line-height:1.1;font-variant-numeric:tabular-nums}
.grant span{display:block;font-size:.9rem;color:var(--ink-2);margin-top:4px}
.faq{border-top:1px solid var(--line);padding:4px 0 6px}.faq h3{margin:16px 0 6px;font-size:1.06rem}
.fonti-box{margin-top:40px;padding:18px 20px;background:var(--card);border:1px solid var(--line);border-radius:var(--r)}
.fonti-box h2{margin:0 0 10px;font-size:1.2rem;display:flex;align-items:center;gap:9px}
.fonti-box ol{margin:0;padding-left:22px;font-size:.92rem}.fonti-box li{margin-bottom:8px}
.ref{font-size:max(.72em,11px);line-height:0;margin-left:1px}.ref a{text-decoration:none;font-weight:700}
.disclaimer{margin:34px 0 0;padding:14px 16px;border-radius:var(--r-s);background:var(--mute);font-size:.88rem;color:var(--ink-2)}
.ad-slot{min-height:0;margin:26px 0}
.aff-box{margin:28px 0;padding:18px 20px;border:1px solid var(--line);border-left:4px solid var(--warm);border-radius:var(--r);background:var(--card);box-shadow:var(--sh-1)}
.aff-box h2{margin:0 0 8px;font-size:1.2rem}.aff-tag{font-family:var(--sans);font-size:.7rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--warm-ink);background:var(--warm-2);border-radius:999px;padding:2px 9px;vertical-align:middle}
.aff-box ul{margin:0 0 8px;padding-left:20px}
.form{display:grid;gap:12px;max-width:640px}.form label{display:grid;gap:6px;font-weight:700;font-size:.92rem}
.form input,.form textarea{font:inherit;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:9px 11px;width:100%}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:600}.form .check input{width:18px;height:18px;margin-top:3px;flex:none}
.hp{position:absolute;left:-9999px}
.btn{display:inline-flex;align-items:center;gap:8px;font:inherit;font-size:.93rem;font-weight:800;background:var(--accent);color:var(--on-accent);border:0;border-radius:var(--r-s);padding:10px 16px;cursor:pointer;min-height:44px;text-decoration:none;justify-self:start}
.btn:hover{background:var(--accent-h);color:var(--on-accent)}
.vuoto-ricerca{padding:14px;border:1px dashed var(--line-2);border-radius:var(--r-s);color:var(--ink-2)}
.due{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px}
footer{margin-top:56px;background:var(--deep);color:var(--on-deep-2);font-size:.9rem}
footer .wrap{padding-top:32px;padding-bottom:30px}
footer a{color:var(--on-deep)}footer h2{color:#fff;font-size:1rem;margin:0 0 8px}
.f-grid{display:grid;grid-template-columns:1.4fr 1fr 1fr;gap:28px}
footer ul{list-style:none;margin:0;padding:0}footer li{margin-bottom:6px}
.f-base{margin:24px 0 0;padding-top:16px;border-top:1px solid rgba(255,255,255,.12);font-size:.84rem}
@media (max-width:900px){nav.menu{display:none}.nav-m{display:block}.f-grid{grid-template-columns:1fr 1fr}.f-grid>div:first-child{grid-column:1/-1}}
@media (max-width:720px){.cifre{grid-template-columns:1fr 1fr}.cifra:nth-of-type(2){border-right:0}.cifra:nth-of-type(-n+2){border-bottom:1px solid var(--line)}.due{grid-template-columns:1fr}}
@media (max-width:560px){.nascondi-m{display:none}}
@media (max-width:480px){body{font-size:16px}.f-grid{grid-template-columns:1fr}.logo{font-size:1.04rem}.cifra{padding:14px 14px}.band-in{padding-top:22px}
table.dati th,table.dati td{padding:8px 9px}.nav-m nav{grid-template-columns:1fr}.barre li{grid-template-columns:8.2em minmax(0,1fr);font-size:.84rem}}
@media print{header.top,footer,.tema,.nav-m,.ad-slot,.aff-box{display:none}.band{background:none;color:#000}.band h1{color:#000}}
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
    "trend": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "home": '<path d="M3.5 11 12 4l8.5 7"/><path d="M6 9.5V20h12V9.5"/><path d="M10 20v-5h4v5"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.2-4.2"/>',
    "pound": '<path d="M16.5 6.5a4 4 0 0 0-7.5 2V18h8"/><path d="M6.5 12.5h7M6.5 18h1.5"/>',
    "fan": '<circle cx="12" cy="12" r="9.5"/><circle cx="12" cy="12" r="1.6"/><path d="M12 10.4c0-3 1-5.4 3.2-5.4 1.8 0 2.3 2.2.6 3.6l-2.4 1.8M13.6 12c3 0 5.4 1 5.4 3.2 0 1.8-2.2 2.3-3.6.6l-1.8-2.4M12 13.6c0 3-1 5.4-3.2 5.4-1.8 0-2.3-2.2-.6-3.6l2.4-1.8M10.4 12c-3 0-5.4-1-5.4-3.2 0-1.8 2.2-2.3 3.6-.6l1.8 2.4"/>',
    "solar": '<path d="M4 20l2.5-9h11L20 20z"/><path d="M5.3 15.5h13.4M9.7 11l-1 9M14.3 11l1 9"/><path d="M12 2.5v2.5M6.2 5l1.4 1.4M17.8 5l-1.4 1.4"/>',
    "map": '<path d="M9 4.5 3.5 6.5v13L9 17.5l6 2 5.5-2v-13L15 6.5z"/><path d="M9 4.5v13M15 6.5v13"/>',
}

# Marchio: casa con una spirale di calore arancione su tessera blu-verde
MARCHIO = ('<rect width="40" height="40" rx="10" fill="#0E2A2F"/>'
           '<path d="M9 19.5 20 10.5l11 9" fill="none" stroke="#ECF4F2" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>'
           '<path d="M12 18v12h16V18" fill="none" stroke="#ECF4F2" stroke-width="2.8" stroke-linejoin="round"/>'
           '<path d="M17 27c0-2 3-2 3-4s-3-2-3-4M21.5 27c0-2 3-2 3-4s-3-2-3-4" fill="none" stroke="#E0662B" stroke-width="2.2" stroke-linecap="round"/>')
FAVICON_SVG = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">{MARCHIO}</svg>\n'

TEMA_JS = "(function(){try{var t=localStorage.getItem('hp-tema');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();"

APP_JS = r"""
(function(){
'use strict';
var b=document.querySelector('[data-tema]');
if(b){b.addEventListener('click',function(){var r=document.documentElement;var dark=r.getAttribute('data-theme')==='dark'||(!r.getAttribute('data-theme')&&window.matchMedia('(prefers-color-scheme: dark)').matches);var t=dark?'light':'dark';r.setAttribute('data-theme',t);try{localStorage.setItem('hp-tema',t);}catch(e){}});}
function norm(s){return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9 ]+/g,' ').replace(/\s+/g,' ').trim();}
document.querySelectorAll('[data-cerca]').forEach(function(q){
  var dove=document.getElementById(q.getAttribute('data-cerca'));if(!dove)return;
  var righe=Array.prototype.slice.call(dove.querySelectorAll('[data-riga]'));var vuoto=dove.querySelector('[data-vuoto]');
  q.addEventListener('input',function(){var parole=norm(q.value).split(' ').filter(Boolean);var n=0;
    righe.forEach(function(r){var t=norm(r.getAttribute('data-riga'));var ok=parole.every(function(p){return t.indexOf(p)>=0;});r.hidden=!ok;if(ok)n++;});
    if(vuoto)vuoto.hidden=n>0;});
});
})();
"""
