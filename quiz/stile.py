"""Aspetto e codice del browser di Quiz Ufficiali: CSS (chiaro e scuro), icone, marchio e JavaScript.

APP_JS fa due cose, tutte nel browser e senza inviare niente:
- pulsante del tema chiaro/scuro (ricordato nel browser);
- simulatore: legge le domande dall'elenco della pagina (testo, risposte, indice della risposta ufficiale in data-e, pagina del PDF
  in data-p), estrae a caso il numero di domande dell'esame (data-n) o prende tutto un argomento, conta errori e tempo secondo le
  regole scritte nella pagina (data-max-errori, data-soglia, data-minuti) e alla fine mostra le risposte ufficiali delle domande sbagliate.
"""

CSS = """
@font-face{font-family:"Public Sans";src:url(/assets/fonts/public-sans.woff2) format("woff2");font-weight:100 900;font-style:normal;font-display:swap}
@font-face{font-family:"Source Serif 4";src:url(/assets/fonts/source-serif-4.woff2) format("woff2");font-weight:200 900;font-style:normal;font-display:swap}
:root{--bg:#F4F5F9;--card:#FFFFFF;--ink:#141A2E;--ink-2:#36405E;--ink-3:#566080;--line:#DDE1EC;--line-2:#C2C8DA;
--deep:#18213F;--deep-2:#222D54;--on-deep:#EEF1FA;--on-deep-2:#B7C0DC;--accent:#2E58C2;--accent-h:#22459E;--accent-2:#E5ECFB;--on-accent:#FFFFFF;
--warm:#C98A0B;--warm-ink:#8A5A00;--warm-2:#FBF1DC;--ok:#1E7A4F;--ok-2:#E3F3EA;--ko:#B3261E;--ko-2:#FBE7E5;--mute:#EEF0F5;
--sh-1:0 1px 2px rgba(24,33,63,.06),0 1px 1px rgba(24,33,63,.04);--sh-2:0 22px 44px -26px rgba(24,33,63,.45),0 2px 8px rgba(24,33,63,.06);
--r:14px;--r-s:10px;--serif:"Source Serif 4",Charter,Georgia,serif;--sans:"Public Sans",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0B0F1C;--card:#121A2E;--ink:#E6EAF5;--ink-2:#BAC3DD;--ink-3:#95A0C0;--line:#222D4A;--line-2:#33406A;
--deep:#070A14;--deep-2:#0F1528;--on-deep:#E6EAF5;--on-deep-2:#A3AED0;--accent:#8AA9FF;--accent-h:#B3C7FF;--accent-2:#17223F;--on-accent:#0A1230;
--warm:#F2C14E;--warm-ink:#F5CF73;--warm-2:#2E2410;--ok:#6FD3A0;--ok-2:#12291E;--ko:#FF8A80;--ko-2:#3A1513;--mute:#151D33;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 22px 44px -26px rgba(0,0,0,.85),0 2px 8px rgba(0,0,0,.4)}}
:root[data-theme="dark"]{--bg:#0B0F1C;--card:#121A2E;--ink:#E6EAF5;--ink-2:#BAC3DD;--ink-3:#95A0C0;--line:#222D4A;--line-2:#33406A;
--deep:#070A14;--deep-2:#0F1528;--on-deep:#E6EAF5;--on-deep-2:#A3AED0;--accent:#8AA9FF;--accent-h:#B3C7FF;--accent-2:#17223F;--on-accent:#0A1230;
--warm:#F2C14E;--warm-ink:#F5CF73;--warm-2:#2E2410;--ok:#6FD3A0;--ok-2:#12291E;--ko:#FF8A80;--ko-2:#3A1513;--mute:#151D33;
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
.band::before{content:"";position:absolute;inset:0;background:radial-gradient(520px 300px at 96% -12%,rgba(201,138,11,.30),transparent 64%),radial-gradient(700px 320px at -6% 130%,rgba(138,169,255,.20),transparent 62%),linear-gradient(180deg,var(--deep) 0,var(--deep-2) 100%)}
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
.ref{font-size:.72em;line-height:0;margin-left:1px}.ref a{text-decoration:none;font-weight:700}
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
.quiz{padding:0;overflow:hidden;box-shadow:var(--sh-2);margin-top:22px}
.quiz-h{margin:0;padding:15px 20px;border-bottom:1px solid var(--line);display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px}
.quiz-h h2{margin:0;font-size:1.2rem;display:flex;align-items:center;gap:9px}.quiz-h h2 .ico{color:var(--warm-ink)}
.quiz-avvio{padding:18px 20px;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px}
.quiz-avvio .blocco{display:grid;gap:10px;align-content:start;background:var(--bg);border:1px solid var(--line);border-radius:var(--r-s);padding:14px 16px}
.quiz-avvio .blocco h3{margin:0;font-size:1.05rem}.quiz-avvio .blocco p{margin:0;font-size:.92rem;color:var(--ink-2)}
.quiz-avvio label{display:grid;gap:6px;font-weight:700;font-size:.9rem}
.quiz-avvio select{font:inherit;font-weight:600;color:var(--ink);background:var(--card);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:8px 10px;width:100%;min-height:44px}
.quiz-avvio .scelte{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:12px}.quiz-avvio .scelte label{flex:1 1 220px}
.quiz-nojs{padding:14px 20px;margin:0;color:var(--ink-2)}
.quiz-gioco{padding:18px 20px}
.quiz-barra{display:flex;justify-content:space-between;gap:10px;font-size:.88rem;font-weight:700;color:var(--ink-3);margin:0 0 6px;font-variant-numeric:tabular-nums}
.quiz-prog{height:6px;background:var(--line);border-radius:99px;overflow:hidden;margin:0 0 16px}.quiz-prog i{display:block;height:100%;background:var(--accent);width:0;transition:width .2s}
.quiz-q{font-family:var(--serif);font-size:1.18rem;line-height:1.4;margin:0 0 14px;font-weight:700}
.quiz-q small{display:block;font-family:var(--sans);font-weight:600;font-size:.8rem;color:var(--ink-3);margin-bottom:4px;text-transform:uppercase;letter-spacing:.05em}
.quiz-opz{display:grid;gap:8px;margin:0 0 14px}
.quiz-opz button{font:inherit;text-align:left;display:flex;gap:10px;align-items:flex-start;width:100%;background:var(--card);color:var(--ink);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:11px 14px;cursor:pointer;min-height:48px;line-height:1.4}
.quiz-opz button b{flex:none;display:grid;place-items:center;width:26px;height:26px;border-radius:50%;background:var(--mute);font-size:.85rem}
.quiz-opz button:hover:not(:disabled){border-color:var(--accent)}
.quiz-opz button:disabled{cursor:default}
.quiz-opz button.giusta{border-color:var(--ok);background:var(--ok-2)}.quiz-opz button.giusta b{background:var(--ok);color:var(--card)}
.quiz-opz button.sbagliata{border-color:var(--ko);background:var(--ko-2)}.quiz-opz button.sbagliata b{background:var(--ko);color:var(--card)}
.quiz-fb{border-radius:var(--r-s);padding:10px 14px;margin:0 0 12px;font-size:.95rem}
.quiz-fb.ok{background:var(--ok-2);border:1px solid color-mix(in srgb,var(--ok) 35%,transparent)}
.quiz-fb.ko{background:var(--ko-2);border:1px solid color-mix(in srgb,var(--ko) 35%,transparent)}
.quiz-fb p{margin:0}.quiz-fb .small{margin-top:4px}
.quiz-azioni{display:flex;flex-wrap:wrap;gap:10px}
.quiz-fine{padding:18px 20px}
.quiz-fine .voto{font-family:var(--serif);font-size:clamp(1.6rem,5vw,2.3rem);font-weight:700;margin:0 0 6px;font-variant-numeric:tabular-nums}
.quiz-fine .voto.ok{color:var(--ok)}.quiz-fine .voto.ko{color:var(--ko)}
.quiz-fine ol{padding-left:20px}.quiz-fine li{margin-bottom:10px}
.sezione-dom{border:1px solid var(--line);border-radius:var(--r);background:var(--card);margin:0 0 10px;box-shadow:var(--sh-1)}
.sezione-dom>summary{cursor:pointer;padding:14px 18px;font-weight:800;display:flex;justify-content:space-between;gap:10px;list-style:none}
.sezione-dom>summary::-webkit-details-marker{display:none}
.sezione-dom>summary span{color:var(--ink-3);font-weight:700;font-size:.9rem;white-space:nowrap}
.sezione-dom[open]>summary{border-bottom:1px solid var(--line)}
ol.domande{list-style:none;margin:0;padding:6px 18px 10px}
ol.domande>li{padding:12px 0;border-bottom:1px solid var(--line)}ol.domande>li:last-child{border-bottom:0}
.dq{margin:0 0 6px;font-weight:700}.dq .num{color:var(--ink-3);font-variant-numeric:tabular-nums;margin-right:4px}
ol.opz{margin:0 0 4px;padding-left:24px}ol.opz li{margin:2px 0}
ol.opz li.esatta{font-weight:700}ol.opz li.esatta .tag{margin-left:6px}
.dmeta{margin:2px 0 0;font-size:.82rem;color:var(--ink-3)}
.tag.ko{background:var(--ko-2);color:var(--ko);border:1px solid color-mix(in srgb,var(--ko) 35%,transparent)}
.manuali .manuali-link{font-weight:800}
@media (max-width:720px){.quiz-avvio{grid-template-columns:1fr}}
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
    "calc": '<rect x="4.5" y="2.5" width="15" height="19" rx="2.5"/><path d="M8 6.5h8M8 11h.01M12 11h.01M16 11h.01M8 14.5h.01M12 14.5h.01M16 14.5h.01M8 18h.01M12 18h4"/>',
    "shield": '<path d="M12 22s8-3.5 8-10V5.5L12 2.5 4 5.5V12c0 6.5 8 10 8 10z"/><path d="M8.5 12l2.5 2.5 4.5-4.5"/>',
    "lock": '<rect x="4.5" y="10.5" width="15" height="11" rx="2.5"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/>',
    "clock": '<circle cx="12" cy="12" r="9.5"/><path d="M12 7v5l3 2"/>',
    "people": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14a6.5 6.5 0 0 1 3.5 6"/>',
    "trend": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "home": '<path d="M3.5 11 12 4l8.5 7"/><path d="M6 9.5V20h12V9.5"/><path d="M10 20v-5h4v5"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.2-4.2"/>',
    "euro": '<path d="M17.5 6.5A7 7 0 1 0 17.5 17.5"/><path d="M4 10.5h9M4 13.5h8"/>',
    "anchor": '<circle cx="12" cy="5" r="2.5"/><path d="M12 7.5V21M7.5 11h9M4 13.5a8 8 0 0 0 16 0"/><path d="M4 13.5 2.5 15M20 13.5l1.5 1.5"/>',
    "truffle": '<path d="M5 13.5c0-4.5 3-8 7-8s7 3.5 7 8-3 6-7 6-7-1.5-7-6z"/><path d="M9 10h.01M13.5 9h.01M15.5 13h.01M10.5 14.5h.01M12 12h.01"/>',
    "leaf": '<path d="M20 4C10 4 4 9 4 16c0 1.5.3 2.8.8 4 7-.5 15.2-4.5 15.2-16z"/><path d="M4.8 20c2.5-5 6-8.5 10.2-11"/>',
    "car": '<path d="M5 16.5h14M6.5 16.5V19M17.5 16.5V19M4.5 16.5v-4l2-5h11l2 5v4"/><path d="M4.5 12.5h15M8 14.5h.01M16 14.5h.01"/>',
    "play": '<circle cx="12" cy="12" r="9.5"/><path d="M10 8.5v7l5.5-3.5z"/>',
    "book": '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M4 20.5A2.5 2.5 0 0 0 6.5 23H20v-5"/>',
    "pill": '<rect x="2.8" y="8.2" width="18.4" height="7.6" rx="3.8" transform="rotate(-35 12 12)"/><path d="m9.2 8 5.6 8"/>',
}

# Marchio: tessera blu notte con un foglio a tre righe, la spunta e il timbro oro
MARCHIO = ('<rect width="40" height="40" rx="10" fill="#18213F"/>'
           '<rect x="10" y="8" width="17" height="22" rx="2.5" fill="none" stroke="#EEF1FA" stroke-width="2.4"/>'
           '<path d="M14 14h9M14 18.5h9M14 23h5" stroke="#EEF1FA" stroke-width="2.2" stroke-linecap="round"/>'
           '<circle cx="28.5" cy="28.5" r="7" fill="#C98A0B"/>'
           '<path d="M25.4 28.6l2.2 2.2 4-4.2" fill="none" stroke="#18213F" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
FAVICON_SVG = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">{MARCHIO}</svg>\n'

TEMA_JS = "(function(){try{var t=localStorage.getItem('qu-tema');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();"

APP_JS = r"""
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
var serie=[],i=0,risp=[],modo='',timer=null,scade=0;
function mescola(a){a=a.slice();for(var k=a.length-1;k>0;k--){var j=Math.floor(Math.random()*(k+1));var x=a[k];a[k]=a[j];a[j]=x;}return a;}
function escluse(){var ex={};scelte.forEach(function(g,gi){var sel=Q.querySelector('[data-scelta="'+gi+'"]');var v=sel?parseInt(sel.value,10):0;g.opzioni.forEach(function(o,oi){if(oi!==v&&o[1])o[1].forEach(function(s){ex[s]=1;});});});return ex;}
function inizia(m){modo=m;var ex=escluse();var pool=tutte.filter(function(d){return !ex[d.s];});
  if(m==='ripasso'){var s=parseInt(Q.querySelector('[data-sezione]').value,10);serie=pool.filter(function(d){return d.s===s;});if(!serie.length)serie=tutte.filter(function(d){return d.s===s;});}
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
  if(modo==='esame'){if(MAXERR!==null&&MAXERR!==''){superato=err<=parseInt(MAXERR,10);esito.textContent=(superato?'Superato':'Non superato')+': '+err+(err===1?' errore':' errori')+', il massimo ammesso è '+MAXERR+'.';}
    else if(SOGLIA){var serve=Math.ceil(serie.length*parseFloat(SOGLIA)/100);superato=giuste>=serve;esito.textContent=(superato?'Superato':'Non superato')+': servono almeno '+serve+' risposte giuste ('+SOGLIA+'%).';}
    else{esito.textContent='Esercitazione: la soglia per superare la prova non è scritta nei documenti dell\'ente.';}}
  else{esito.textContent='Ripasso di un argomento: '+err+(err===1?' errore.':' errori.');}
  if(scaduto){esito.textContent='Tempo scaduto: le domande senza risposta contano come errori. '+esito.textContent;}
  if(superato!==null)v.className='voto '+(superato?'ok':'ko');fine.appendChild(esito);
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
"""
