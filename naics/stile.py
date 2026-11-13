"""Look and browser code of NAICS Code Lookup: CSS (light and dark), icons, brand mark and JavaScript.

APP_JS does three things, all in the browser, sending nothing:
- home search: loads /assets/index.<hash>.json (2022 codes and titles, official index entries, old 2017 codes, SIC codes, guides);
- filterable tables (2017 → 2022, SIC → NAICS): filter by code or word, 100 rows at a time;
- light/dark theme button (remembered in the browser).
"""

CSS = """
@font-face{font-family:"Public Sans";src:url(/assets/fonts/public-sans.woff2) format("woff2");font-weight:100 900;font-style:normal;font-display:swap}
@font-face{font-family:"Source Serif 4";src:url(/assets/fonts/source-serif-4.woff2) format("woff2");font-weight:200 900;font-style:normal;font-display:swap}
:root{--bg:#F3F6F6;--card:#FFFFFF;--ink:#13222A;--ink-2:#34474F;--ink-3:#556870;--line:#D9E2E4;--line-2:#BFCDD1;
--deep:#0E2B33;--deep-2:#123A44;--on-deep:#ECF5F6;--on-deep-2:#AFC6CB;--accent:#0B6B78;--accent-h:#08525C;--accent-2:#E1F0F1;--on-accent:#FFFFFF;
--warm:#D4891A;--warm-ink:#94560A;--warm-2:#FCF0DD;--ok:#1E7A4F;--ok-2:#E3F3EA;--mute:#ECF1F2;
--sh-1:0 1px 2px rgba(14,43,51,.06),0 1px 1px rgba(14,43,51,.04);--sh-2:0 22px 44px -26px rgba(14,43,51,.45),0 2px 8px rgba(14,43,51,.06);
--r:14px;--r-s:10px;--serif:"Source Serif 4",Charter,Georgia,serif;--sans:"Public Sans",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0A1619;--card:#102328;--ink:#E3EEF0;--ink-2:#B4C8CC;--ink-3:#8FA7AD;--line:#1E363C;--line-2:#2F4C53;
--deep:#061013;--deep-2:#0B1E23;--on-deep:#E3EEF0;--on-deep-2:#9BB5BB;--accent:#6CCFD9;--accent-h:#9FE1E8;--accent-2:#0F3138;--on-accent:#06262B;
--warm:#F2B54A;--warm-ink:#F5C46C;--warm-2:#2D2210;--ok:#6FD3A0;--ok-2:#12291E;--mute:#0F2025;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 22px 44px -26px rgba(0,0,0,.85),0 2px 8px rgba(0,0,0,.4)}}
:root[data-theme="dark"]{--bg:#0A1619;--card:#102328;--ink:#E3EEF0;--ink-2:#B4C8CC;--ink-3:#8FA7AD;--line:#1E363C;--line-2:#2F4C53;
--deep:#061013;--deep-2:#0B1E23;--on-deep:#E3EEF0;--on-deep-2:#9BB5BB;--accent:#6CCFD9;--accent-h:#9FE1E8;--accent-2:#0F3138;--on-accent:#06262B;
--warm:#F2B54A;--warm-ink:#F5C46C;--warm-2:#2D2210;--ok:#6FD3A0;--ok-2:#12291E;--mute:#0F2025;
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
.logo{display:flex;align-items:center;gap:10px;font-family:var(--serif);font-weight:700;font-size:1.22rem;color:var(--on-deep);text-decoration:none;white-space:nowrap;margin-right:auto;line-height:1.1}
.logo:hover{color:#fff}.logo img{width:34px;height:34px;flex:none;display:block}.logo b{color:var(--warm);font-weight:inherit}
nav.menu{display:flex;gap:2px;font-size:.92rem}
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
.band::before{content:"";position:absolute;inset:0;background:radial-gradient(520px 300px at 96% -12%,rgba(212,137,26,.26),transparent 64%),radial-gradient(700px 320px at -6% 130%,rgba(108,207,217,.18),transparent 62%),linear-gradient(180deg,var(--deep) 0,var(--deep-2) 100%)}
.band::after{content:"";position:absolute;right:-30px;bottom:-26px;width:380px;height:180px;opacity:.12;background:repeating-linear-gradient(0deg,var(--on-deep) 0 2px,transparent 2px 22px);-webkit-mask:linear-gradient(90deg,transparent 0,#000 100%);mask:linear-gradient(90deg,transparent 0,#000 100%)}
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
.cifra{padding:18px 20px;border-right:1px solid var(--line);min-width:0}.cifra:last-child{border-right:0}
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
table.dati th{background:var(--mute);font-size:.74rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-2);white-space:nowrap}
table.dati td.n,table.dati th.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
table.dati tr:last-child td{border-bottom:0}table.dati tfoot td{font-weight:800;background:var(--mute)}
table.dati tr.qui td{background:var(--accent-2);font-weight:700}
table.dati caption{caption-side:bottom;text-align:left;padding:8px 12px;font-size:.84rem;color:var(--ink-3)}
.formula{font-family:var(--serif);font-size:1.12rem;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:var(--r-s);padding:12px 16px;margin:0 0 12px;font-variant-numeric:tabular-nums}
.formula small{display:block;font-family:var(--sans);font-size:.84rem;color:var(--ink-3);margin-top:4px}
.calc{padding:0;overflow:hidden;box-shadow:var(--sh-2)}
.calc-h{margin:0;padding:15px 20px;border-bottom:1px solid var(--line);display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px}
.calc-h h2{margin:0;font-size:1.2rem;display:flex;align-items:center;gap:9px}.calc-h h2 .ico{color:var(--warm-ink)}
.pill{display:inline-block;font-size:.72rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--warm-ink);background:var(--warm-2);border-radius:999px;padding:3px 10px}
.calc-g{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.1fr)}
.calc-in{padding:18px 20px;display:grid;gap:14px;align-content:start;border-right:1px solid var(--line)}
.calc-in label{display:grid;gap:6px;font-weight:700;font-size:.92rem}
.calc-in input,.calc-in select{font:inherit;font-weight:600;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:9px 11px;width:100%;min-height:46px;font-variant-numeric:tabular-nums}
.calc-in input:focus,.calc-in select:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 22%,transparent)}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chips button{font:inherit;font-size:.9rem;font-weight:800;border:1.5px solid var(--line-2);background:var(--card);color:var(--ink-2);border-radius:999px;padding:6px 13px;cursor:pointer;min-height:38px}
.chips button[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:var(--on-accent)}
.calc-out{padding:18px 20px;background:var(--accent-2);display:grid;gap:10px;align-content:start;min-width:0}
.esito{background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:12px 14px}
.esito span{display:block;font-size:.8rem;color:var(--ink-3);font-weight:700}
.esito b{display:block;font-family:var(--serif);font-size:clamp(1.6rem,4.6vw,2.2rem);line-height:1.15;color:var(--accent);font-variant-numeric:tabular-nums}
.esito.sec b{font-size:1.25rem;color:var(--ink)}
.calc-f{margin:0;padding:12px 20px;border-top:1px solid var(--line);font-size:.85rem;color:var(--ink-3)}
.cerca{display:flex;gap:8px;max-width:620px;margin:6px 0 0}
.cerca input{font:inherit;flex:1;min-width:0;border-radius:var(--r-s);border:1.5px solid rgba(255,255,255,.3);background:rgba(255,255,255,.08);color:#fff;padding:11px 14px;min-height:48px}
.cerca input::placeholder{color:var(--on-deep-2)}.cerca input:focus{outline:none;border-color:var(--warm);background:rgba(255,255,255,.12)}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;margin:0;padding:0;list-style:none}
.griglia a{display:block;height:100%;background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:16px;text-decoration:none;color:var(--ink);box-shadow:var(--sh-1)}
.griglia a:hover{border-color:var(--accent)}.griglia b{display:block;font-family:var(--serif);font-size:1.12rem;margin-bottom:4px}
.griglia span{display:block;font-size:.88rem;color:var(--ink-3)}.griglia em{font-style:normal;color:var(--accent);font-weight:800;font-variant-numeric:tabular-nums}
.livelli{display:flex;flex-wrap:wrap;gap:6px;margin:0;padding:0;list-style:none}
.livelli a{display:inline-block;padding:6px 12px;border-radius:999px;border:1px solid var(--line-2);background:var(--card);text-decoration:none;font-weight:700;font-size:.9rem;color:var(--ink-2)}
.livelli a:hover,.livelli a[aria-current]{border-color:var(--accent);color:var(--accent)}
.faq{border-top:1px solid var(--line);padding:4px 0 6px}.faq h3{margin:16px 0 6px;font-size:1.06rem}
.fonti-box{margin-top:40px;padding:18px 20px;background:var(--card);border:1px solid var(--line);border-radius:var(--r)}
.fonti-box h2{margin:0 0 10px;font-size:1.2rem;display:flex;align-items:center;gap:9px}
.fonti-box ol{margin:0;padding-left:22px;font-size:.92rem}.fonti-box li{margin-bottom:8px}
.ref{font-size:max(.72em,11px);line-height:0;margin-left:1px}.ref a{text-decoration:none;font-weight:700}
.disclaimer{margin:34px 0 0;padding:14px 16px;border-radius:var(--r-s);background:var(--mute);font-size:.88rem;color:var(--ink-2)}
.ad-slot{min-height:0;margin:26px 0}
.form{display:grid;gap:12px;max-width:640px}.form label{display:grid;gap:6px;font-weight:700;font-size:.92rem}
.form input,.form textarea{font:inherit;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:9px 11px;width:100%}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:600}.form .check input{width:18px;height:18px;margin-top:3px;flex:none}
.hp{position:absolute;left:-9999px}
.btn{display:inline-flex;align-items:center;gap:8px;font:inherit;font-size:.93rem;font-weight:800;background:var(--accent);color:var(--on-accent);border:0;border-radius:var(--r-s);padding:10px 16px;cursor:pointer;min-height:44px;text-decoration:none;justify-self:start}
.btn:hover{background:var(--accent-h);color:var(--on-accent)}
.btn.sec{background:transparent;color:var(--accent);box-shadow:inset 0 0 0 2px var(--accent)}.btn.sec:hover{background:var(--accent-2);color:var(--accent)}
.altre{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 0}.altre[hidden]{display:none}
.contratto-h{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:6px 12px;margin:40px 0 10px}
.contratto-h h2{margin:0}
.vuoto-ricerca{padding:14px;border:1px dashed var(--line-2);border-radius:var(--r-s);color:var(--ink-2)}
footer{margin-top:56px;background:var(--deep);color:var(--on-deep-2);font-size:.9rem}
footer .wrap{padding-top:32px;padding-bottom:30px}
footer a{color:var(--on-deep)}footer h2{color:#fff;font-size:1rem;margin:0 0 8px}
.f-grid{display:grid;grid-template-columns:1.4fr 1fr 1fr;gap:28px}
footer ul{list-style:none;margin:0;padding:0}footer li{margin-bottom:6px}
.f-base{margin:24px 0 0;padding-top:16px;border-top:1px solid rgba(255,255,255,.12);font-size:.84rem}
@media (max-width:900px){nav.menu{display:none}.nav-m{display:block}.f-grid{grid-template-columns:1fr 1fr}.f-grid>div:first-child{grid-column:1/-1}}
@media (max-width:720px){.cifre{grid-template-columns:1fr 1fr}.cifra:nth-child(2){border-right:0}.cifra:nth-child(-n+2){border-bottom:1px solid var(--line)}
.calc-g{grid-template-columns:1fr}.calc-in{border-right:0;border-bottom:1px solid var(--line)}}
@media (max-width:560px){.nascondi-m{display:none}}
@media (max-width:480px){body{font-size:16px}.f-grid{grid-template-columns:1fr}.logo{font-size:1.08rem}.cifra{padding:14px 14px}.band-in{padding-top:22px}
table.dati th,table.dati td{padding:8px 9px}.nav-m nav{grid-template-columns:1fr}}
@media print{header.top,footer,.tema,.nav-m,.calc,.ad-slot{display:none}.band{background:none;color:#000}.band h1{color:#000}}
.tag{display:inline-block;font-size:.72rem;font-weight:800;letter-spacing:.04em;border-radius:999px;padding:2px 9px;white-space:nowrap;line-height:1.5}
.tag.car{background:var(--warm-2);color:var(--warm-ink);border:1px solid color-mix(in srgb,var(--warm) 45%,transparent)}
.tag.ok{background:var(--ok-2);color:var(--ok);border:1px solid color-mix(in srgb,var(--ok) 35%,transparent)}
.tag.neu{background:var(--mute);color:var(--ink-2);border:1px solid var(--line)}
table.resp7 th{white-space:normal}
table.dati tr.carente td{background:color-mix(in srgb,var(--warm-2) 70%,transparent)}
table.dati td small{display:block;color:var(--ink-3);font-size:.8rem;line-height:1.35;margin-top:2px}
table.dati th button{font:inherit;font-weight:800;letter-spacing:inherit;text-transform:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer;display:inline-flex;gap:4px;align-items:center}
table.dati th button::after{content:"↕";opacity:.45}table.dati th[aria-sort="ascending"] button::after{content:"↑";opacity:1}table.dati th[aria-sort="descending"] button::after{content:"↓";opacity:1}
.gruppo{margin-top:36px;padding-top:4px}.gruppo h2{margin-top:6px}
.gruppo-h{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:baseline;color:var(--ink-3);font-size:.88rem;margin:0 0 10px}
.det{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--warm);border-radius:var(--r-s);padding:12px 16px;margin:10px 0;font-size:.94rem}
.det p{margin:0 0 6px}.det p:last-child{margin:0}
.indice{columns:3 220px;column-gap:24px;margin:0;padding:0;list-style:none;font-size:.95rem}.indice li{break-inside:avoid;margin:0 0 6px}
.indice .small{margin-left:4px}
.filtri{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;margin:0 0 12px}
.filtri input[type=search]{font:inherit;flex:1 1 260px;min-width:0;border-radius:var(--r-s);border:1.5px solid var(--line-2);background:var(--card);color:var(--ink);padding:10px 12px;min-height:46px}
.filtri input[type=search]:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 22%,transparent)}
.filtri label.check{display:flex;gap:8px;align-items:center;font-weight:700;font-size:.92rem}.filtri label.check input{width:18px;height:18px}
.risultati{list-style:none;margin:8px 0 0;padding:0;max-width:620px;background:var(--card);border-radius:var(--r-s);box-shadow:var(--sh-2);overflow:hidden}
.risultati li a{display:flex;justify-content:space-between;gap:10px;padding:10px 14px;color:var(--ink);text-decoration:none;border-bottom:1px solid var(--line)}
.risultati li:last-child a{border-bottom:0}.risultati li a:hover,.risultati li a:focus{background:var(--accent-2)}
.risultati li a span{color:var(--ink-3);font-size:.84rem;text-align:right;flex:none;max-width:45%}
.risultati li.vuoto{padding:10px 14px;color:var(--ink-2)}
.conteggio{font-size:.88rem;color:var(--ink-3);margin:0 0 8px}
blockquote.legge{margin:0 0 14px;padding:12px 16px;border-left:4px solid var(--accent);background:var(--card);border-radius:0 var(--r-s) var(--r-s) 0;font-family:var(--serif);font-size:1.02rem;max-width:790px}
blockquote.legge cite{display:block;font-family:var(--sans);font-style:normal;font-size:.84rem;color:var(--ink-3);margin-top:6px}
@media (max-width:640px){table.resp thead,table.resp7 thead{display:none}table.resp,table.resp7{display:flex;flex-direction:column;width:100%}table.resp tbody,table.resp7 tbody{display:block;width:100%}table.resp caption{order:2}
table.resp tr{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-bottom:1px solid var(--line);padding:6px 0}
table.resp7 tr{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));border-bottom:1px solid var(--line);padding:6px 0}
table.resp tr[hidden],table.resp7 tr[hidden]{display:none}
table.resp td,table.resp7 td{display:block;border:0;padding:4px 12px;min-width:0}table.resp td.n{text-align:left;white-space:normal}
table.resp td:first-child,table.resp7 td:first-child,table.resp7 td:nth-child(2),table.resp7 td:nth-child(5){grid-column:1/-1}
table.resp td[data-l]::before,table.resp7 td[data-l]::before{content:attr(data-l);display:block;font-size:.7rem;font-weight:800;letter-spacing:.02em;text-transform:uppercase;color:var(--ink-3)}
table.resp .tag,table.resp7 .tag{white-space:normal}}
.pull+.livelli{margin-top:18px}.note .escl{padding-left:24px}
.cod{font-family:ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace;font-weight:700;font-variant-numeric:tabular-nums;letter-spacing:.01em;white-space:nowrap}
a.cod,.cod a{text-decoration:none}
.chip-cod{display:inline-block;font-family:ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace;font-weight:700;font-size:.86rem;background:var(--accent-2);color:var(--accent);border-radius:8px;padding:2px 8px;white-space:nowrap}
.band .chip-cod{background:rgba(255,255,255,.12);color:#fff}
.altre-lingue{font-size:.9rem;color:var(--on-deep-2);margin:-4px 0 14px;max-width:820px}.altre-lingue b{color:var(--on-deep);font-weight:700}
.voce{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:18px 20px 8px;margin:22px 0;box-shadow:var(--sh-1);scroll-margin-top:16px}
.voce>h2,.voce>h3{margin:0 0 4px;display:flex;flex-wrap:wrap;gap:4px 10px;align-items:baseline;font-size:1.22rem}
.voce .en{font-size:.86rem;color:var(--ink-3);margin:0 0 12px}
.voce:target{border-color:var(--accent);box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 25%,transparent)}
.cat-h{margin:40px 0 4px}.cat-h+.small{margin-bottom:6px}
.note h4{font-family:var(--sans);font-size:.78rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);margin:14px 0 6px}
.note ul{margin:0 0 10px;padding-left:20px}.note li{margin-bottom:5px;max-width:800px}.note p{max-width:800px}
.note .escl li::marker{content:"– "}
.note .op{background:var(--mute);border-radius:var(--r-s);padding:10px 14px;font-size:.93rem}
.coef{display:flex;flex-wrap:wrap;gap:6px 12px;align-items:baseline;border-top:1px dashed var(--line-2);margin-top:10px;padding:10px 0 6px;font-size:.93rem}
.coef b{font-family:var(--serif);font-size:1.15rem;color:var(--accent)}
.mini{font-size:.84rem;color:var(--ink-3)}
details.tutte{margin:4px 0}details.tutte summary{cursor:pointer;color:var(--accent);font-weight:700;font-size:.9rem}
details.tutte ul{margin:6px 0;padding-left:18px;font-size:.9rem}
.albero{list-style:none;margin:0;padding:0}.albero>li{border-bottom:1px solid var(--line);padding:9px 0;display:grid;grid-template-columns:7.2rem minmax(0,1fr);gap:4px 12px}
.albero>li:last-child{border-bottom:0}.albero .mini{grid-column:2}
.risultati li a strong{font-family:ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace;margin-right:8px;flex:none}
.risultati li a em{font-style:normal;flex:1;min-width:0}
.aff{margin:30px 0;padding:18px 20px;border:1px solid var(--line);border-radius:var(--r);background:var(--card)}
.comune{white-space:pre-line}
@media (max-width:480px){.albero>li{grid-template-columns:1fr}.albero .mini{grid-column:1}.voce{padding:14px 14px 6px}}
.lista-idx{columns:2 260px;column-gap:26px;margin:0;padding:0 0 0 18px;font-size:.95rem}.lista-idx li{break-inside:avoid;margin:0 0 5px}
.sic-tab td:first-child{white-space:nowrap}
.chips-cod{display:flex;flex-wrap:wrap;gap:6px;margin:4px 0 0;padding:0;list-style:none}
.fatti{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:0;padding:0;overflow:hidden;box-shadow:var(--sh-2)}
.fatto{padding:14px 18px;border-right:1px solid var(--line);border-bottom:1px solid var(--line);min-width:0}
.fatto span{display:block;font-size:.78rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);margin-bottom:4px}
.fatto b{font-family:var(--serif);font-size:1.15rem}
.cinque{border-left:4px solid var(--accent)}
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
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.2-4.2"/>',
    "tree": '<rect x="3" y="3.5" width="7" height="5" rx="1.2"/><rect x="14" y="10" width="7" height="5" rx="1.2"/><rect x="14" y="17" width="7" height="4.5" rx="1.2"/><path d="M6.5 8.5V19.2H14M6.5 12.5H14"/>',
    "swap": '<path d="M4 8h13l-3.5-3.5M20 16H7l3.5 3.5"/>',
    "percent": '<path d="M19 5 5 19"/><circle cx="7" cy="7" r="2.5"/><circle cx="17" cy="17" r="2.5"/>',
    "tag": '<path d="M3 12V4.5A1.5 1.5 0 0 1 4.5 3H12l9 9-9 9z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    "people": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14a6.5 6.5 0 0 1 3.5 6"/>',
}

# Brand mark: deep teal tile, five bars growing left to right (2 to 6 digits), amber dot on the last one
MARCHIO = ('<rect width="40" height="40" rx="10" fill="#0E2B33"/>'
           '<rect x="7" y="22" width="4" height="10" rx="2" fill="#ECF5F6" opacity=".55"/>'
           '<rect x="13" y="18" width="4" height="14" rx="2" fill="#ECF5F6" opacity=".7"/>'
           '<rect x="19" y="14" width="4" height="18" rx="2" fill="#ECF5F6" opacity=".85"/>'
           '<rect x="25" y="10" width="4" height="22" rx="2" fill="#ECF5F6"/>'
           '<circle cx="32.5" cy="9.5" r="3.4" fill="#F2B54A"/>')
FAVICON_SVG = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">{MARCHIO}</svg>\n'

TEMA_JS = "(function(){try{var t=localStorage.getItem('nl-theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();"

APP_JS = r"""
(function(){
'use strict';
function norm(s){return String(s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,' ').trim();}
function cifre(s){return String(s||'').replace(/[^0-9]/g,'');}
function radice(w){return w.length>4?w.replace(/(ies|es|s|y)$/,''):w;}  // bakery/bakeries -> baker (prefix match)
var b=document.querySelector('[data-tema]');
if(b){b.addEventListener('click',function(){var r=document.documentElement;var dark=r.getAttribute('data-theme')==='dark'||(!r.getAttribute('data-theme')&&window.matchMedia('(prefers-color-scheme: dark)').matches);var t=dark?'light':'dark';r.setAttribute('data-theme',t);try{localStorage.setItem('nl-theme',t);}catch(e){}});}
// search: JSON index loaded on first focus. Entry: [code, title, url, type, note]; index entries (joined by "|") come from a second file
// type: 2..6 = NAICS 2022 level, "17" = 2017 code, "sic" = 1987 SIC code, "p" = guide page
var q=document.querySelector('[data-cerca]');
if(q){var out=document.querySelector('[data-risultati]');var indice=null,attesa=false;
  var ETI={'2':'Sector','3':'Subsector','4':'Industry group','5':'NAICS industry','6':'2022 NAICS','17':'2017 code','sic':'SIC 1987','p':'Guide'};
  var PESO={'6':0,'5':1,'4':2,'3':3,'2':4,'p':5,'17':6,'sic':7};
  function cerca(v){var t=v.trim();if(!t)return [];var ris=[];
    if(/^[0-9][0-9 -]*$/.test(t)){var c=cifre(t);
      for(var i=0;i<indice.length;i++){var e=indice[i];if(e.c.indexOf(c)===0)ris.push({e:e,f:''});}
      ris.sort(function(a,b){return (a.e.c===c?0:1)-(b.e.c===c?0:1)||(a.e.c.length-b.e.c.length)||(PESO[a.e[3]]-PESO[b.e[3]])||(a.e[0]<b.e[0]?-1:1);});
      return ris.slice(0,12);}
    var p=norm(t).split(' ').filter(Boolean).map(radice);var a=[],z=[];
    for(var k=0;k<indice.length&&a.length+z.length<200;k++){var e=indice[k];var tt=' '+e.n;var okt=true;
      for(var m=0;m<p.length;m++){if(tt.indexOf(' '+p[m])<0){okt=false;break;}}
      if(okt){a.push({e:e,f:''});continue;}
      if(!e.f)continue;
      for(var j=0;j<e.f.length;j++){var ff=' '+e.f[j];var okf=true;for(var m2=0;m2<p.length;m2++){if(ff.indexOf(' '+p[m2])<0){okf=false;break;}}
        if(okf){z.push({e:e,f:e[5].split('|')[j]});break;}}}
    a.sort(function(x,y){return (PESO[x.e[3]]-PESO[y.e[3]])||(x.e[0]<y.e[0]?-1:1);});
    return a.slice(0,6).concat(z).concat(a.slice(6)).slice(0,12);}
  function mostra(){out.innerHTML='';if(!q.value.trim()){out.hidden=true;return;}
    if(!indice){out.hidden=false;out.innerHTML='<li class="vuoto">Loading the code list…</li>';carica();return;}
    var ris=cerca(q.value);out.hidden=false;
    if(!ris.length){out.innerHTML='<li class="vuoto">No code found. Try another word (for example “bakery”, “software”, “plumbing”) or the first digits of a code.</li>';return;}
    ris.forEach(function(r){var e=r.e;var li=document.createElement('li');var a=document.createElement('a');a.href=e[2];var s=document.createElement('strong');s.textContent=e[0];
      var t=document.createElement('em');t.textContent=r.f?(e[1]+' — '+r.f):e[1];var sp=document.createElement('span');sp.textContent=e[4]||ETI[e[3]]||'';
      a.appendChild(s);a.appendChild(t);a.appendChild(sp);li.appendChild(a);out.appendChild(li);});}
  // two files: codes and titles first (small), then the official index entries of each 6-digit code (bigger)
  function carica(){if(attesa)return;attesa=true;fetch(q.getAttribute('data-indice')).then(function(r){return r.json();}).then(function(j){
      var per={};indice=j.map(function(e){e.c=cifre(e[0]);e.n=norm(e[0]+' '+e[1]);e.f=null;if(e[3]==='6')per[e[0]]=e;return e;});mostra();
      return fetch(q.getAttribute('data-frasi')).then(function(r){return r.json();}).then(function(fr){
        Object.keys(fr).forEach(function(c){var e=per[c];if(e){e[5]=fr[c];e.f=fr[c].split('|').map(norm);}});q.setAttribute('data-pronto','1');if(q.value.trim())mostra();});})
    .catch(function(){if(!indice)out.innerHTML='<li class="vuoto">The list could not be loaded: use the sector list below.</li>';});}
  q.addEventListener('input',mostra);q.addEventListener('focus',carica);
  var f=q.closest('form');if(f)f.addEventListener('submit',function(ev){ev.preventDefault();var a=out.querySelector('a');if(a)location.href=a.href;});}
// filterable tables, 100 rows at a time
document.querySelectorAll('[data-tabella]').forEach(function(box){
  var tb=box.querySelector('tbody');var righe=Array.prototype.slice.call(tb.rows);var fi=box.querySelector('[data-filtro]');
  var cnt=box.querySelector('[data-conteggio]');var vuoto=box.querySelector('[data-vuoto]');var altre=box.querySelector('[data-altre]');var lim=100;
  righe.forEach(function(r){r._t=norm(r.textContent);r._c=cifre(r.cells[0].textContent);});
  function filtra(){var v=fi?fi.value.trim():'';var dig=/^[0-9][0-9 ]*$/.test(v)?cifre(v):null;var p=dig?[]:norm(v).split(' ').filter(Boolean);var n=0;
    righe.forEach(function(r){var ok=dig?r._c.indexOf(dig)===0:true;for(var k=0;ok&&k<p.length;k++){if(r._t.indexOf(p[k])<0)ok=false;}if(ok)n++;r.hidden=!ok||n>lim;});
    var vis=Math.min(n,lim);if(cnt)cnt.textContent=(n===righe.length?(n+' codes'):(n+' of '+righe.length+' codes'))+(vis<n?' · showing '+vis:'');
    if(vuoto)vuoto.hidden=n>0;if(altre)altre.hidden=vis>=n;}
  if(altre){altre.querySelector('[data-altre-piu]').addEventListener('click',function(){lim+=100;filtra();});altre.querySelector('[data-altre-tutte]').addEventListener('click',function(){lim=Infinity;filtra();});}
  if(fi){fi.addEventListener('input',function(){if(lim!==Infinity)lim=100;filtra();});var u=new URLSearchParams(location.search).get('q');if(u){fi.value=u;}
    var h=location.hash;if(h&&/^#(v|sic)-/.test(h)){fi.value=decodeURIComponent(h.replace(/^#(v|sic)-/,''));}}
  filtra();
  if(location.hash){var el=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(el)el.scrollIntoView();}
});
})();
"""
