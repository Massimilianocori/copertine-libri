"""Aspetto e codice del browser di Payroll Tax by State: CSS, icone, marchio, motore JS del calcolatore e interfaccia.

Il motore JS (MOTORE_JS) è la copia esatta di motore.py: stesse formule, stesso ordine delle operazioni.
verifica.py lo esegue con node sul file pubblicato in sito/assets/ e lo confronta con il Python.
"""

CSS = """
@font-face{font-family:"Public Sans";src:url(/assets/fonts/public-sans.woff2) format("woff2");font-weight:100 900;font-style:normal;font-display:swap}
@font-face{font-family:"Source Serif 4";src:url(/assets/fonts/source-serif-4.woff2) format("woff2");font-weight:200 900;font-style:normal;font-display:swap}
:root{--bg:#F5F6F3;--card:#FFFFFF;--ink:#13201E;--ink-2:#36443F;--ink-3:#57655F;--line:#DFE4E0;--line-2:#C3CCC6;
--deep:#0C2F2B;--deep-2:#11403A;--on-deep:#EEF4F1;--on-deep-2:#B4C7C0;--accent:#0B6B5D;--accent-h:#07504A;--accent-2:#E1F1EC;--on-accent:#FFFFFF;
--ochre:#E0952B;--ochre-ink:#8F4F05;--ochre-2:#FCEFD9;--warn:#8A4B00;--warn-2:#FFF3DE;--warn-l:#E7B666;--mute:#EEF1EE;--bar:#0B6B5D;--bar-2:#E0952B;--bad:#B3261E;
--sh-1:0 1px 2px rgba(12,47,43,.06),0 1px 1px rgba(12,47,43,.04);--sh-2:0 24px 48px -26px rgba(12,47,43,.42),0 2px 8px rgba(12,47,43,.06);
--r:14px;--r-s:10px;--serif:"Source Serif 4",Charter,"Iowan Old Style",Georgia,serif;--sans:"Public Sans",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0A1412;--card:#111E1B;--ink:#E5EDEA;--ink-2:#BACAC4;--ink-3:#93A59E;--line:#1F302C;--line-2:#2F4540;
--deep:#061210;--deep-2:#0C211D;--on-deep:#E5EDEA;--on-deep-2:#9FB5AE;--accent:#4FC9B3;--accent-h:#83DECD;--accent-2:#10302B;--on-accent:#04201B;
--ochre:#F0AA4E;--ochre-ink:#F0AA4E;--ochre-2:#2A1F0E;--warn:#F2C177;--warn-2:#271E0F;--warn-l:#8A6420;--mute:#15241F;--bar:#4FC9B3;--bar-2:#F0AA4E;--bad:#FF8A80;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 24px 48px -26px rgba(0,0,0,.85),0 2px 8px rgba(0,0,0,.4)}}
:root[data-theme="dark"]{--bg:#0A1412;--card:#111E1B;--ink:#E5EDEA;--ink-2:#BACAC4;--ink-3:#93A59E;--line:#1F302C;--line-2:#2F4540;
--deep:#061210;--deep-2:#0C211D;--on-deep:#E5EDEA;--on-deep-2:#9FB5AE;--accent:#4FC9B3;--accent-h:#83DECD;--accent-2:#10302B;--on-accent:#04201B;
--ochre:#F0AA4E;--ochre-ink:#F0AA4E;--ochre-2:#2A1F0E;--warn:#F2C177;--warn-2:#271E0F;--warn-l:#8A6420;--mute:#15241F;--bar:#4FC9B3;--bar-2:#F0AA4E;--bad:#FF8A80;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 24px 48px -26px rgba(0,0,0,.85),0 2px 8px rgba(0,0,0,.4)}
*{box-sizing:border-box}[hidden]{display:none!important}html{-webkit-text-size-adjust:100%;scroll-padding-top:16px}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:17px;line-height:1.6;overflow-wrap:break-word;font-feature-settings:"tnum" 0}
a{color:var(--accent);text-underline-offset:2px;text-decoration-thickness:1px}a:hover{color:var(--accent-h)}
:focus-visible{outline:3px solid var(--ochre);outline-offset:2px;border-radius:4px}
.skip{position:absolute;left:-9999px;top:8px;background:var(--card);color:var(--ink);padding:8px 14px;border-radius:8px;z-index:50}.skip:focus{left:12px}
.ico{width:1.15em;height:1.15em;flex:none;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;vertical-align:-.2em}
.wrap{max-width:1120px;margin:0 auto;padding:0 16px}
header.top{background:var(--deep);color:var(--on-deep);position:relative;z-index:20;border-bottom:1px solid rgba(255,255,255,.07)}
header.top .wrap{display:flex;align-items:center;gap:10px;min-height:64px}
.logo{display:flex;align-items:center;gap:10px;font-family:var(--serif);font-weight:700;font-size:1.2rem;color:var(--on-deep);text-decoration:none;white-space:nowrap;margin-right:auto;line-height:1.1;letter-spacing:-.005em}
.logo:hover{color:#fff}.logo img{width:34px;height:34px;flex:none;display:block}.logo b{color:var(--ochre);font-weight:inherit}
nav.menu{display:flex;gap:2px;font-size:.93rem}
nav.menu a{color:var(--on-deep-2);text-decoration:none;padding:7px 11px;border-radius:8px;white-space:nowrap}
nav.menu a:hover,nav.menu a[aria-current]{color:#fff;background:rgba(255,255,255,.09)}
.tema{display:grid;place-items:center;width:40px;height:40px;border-radius:10px;border:1px solid rgba(255,255,255,.22);background:none;color:var(--on-deep);cursor:pointer;flex:none}
.tema:hover{border-color:var(--ochre)}.tema .ico{width:19px;height:19px}
.tema .i-sun{display:none}:root[data-theme="dark"] .tema .i-sun{display:block}:root[data-theme="dark"] .tema .i-moon{display:none}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .tema .i-sun{display:block}:root:not([data-theme="light"]) .tema .i-moon{display:none}}
.nav-m{display:none}
.nav-m summary{list-style:none;cursor:pointer;display:grid;place-items:center;width:40px;height:40px;border:1px solid rgba(255,255,255,.25);border-radius:10px;color:var(--on-deep)}
.nav-m summary::-webkit-details-marker{display:none}.nav-m[open] summary{background:rgba(255,255,255,.1);border-color:var(--ochre)}
.nav-m nav{position:absolute;left:16px;right:16px;top:calc(100% + 4px);background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-2);padding:8px;display:grid;grid-template-columns:1fr 1fr;gap:2px}
.nav-m nav a{padding:11px 12px;border-radius:8px;color:var(--ink);text-decoration:none;font-weight:700;font-size:.95rem}.nav-m nav a:hover{background:var(--accent-2)}
.nav-m nav .sep{grid-column:1/-1;border-top:1px solid var(--line);margin:4px 0}
.band{background:var(--deep);color:var(--on-deep);position:relative;overflow:hidden}
.band::before{content:"";position:absolute;inset:0;background:radial-gradient(560px 320px at 94% -10%,rgba(224,149,43,.34),transparent 64%),radial-gradient(720px 320px at -4% 130%,rgba(79,201,179,.20),transparent 62%),linear-gradient(180deg,var(--deep) 0,var(--deep-2) 100%)}
.band::after{content:"";position:absolute;right:-40px;bottom:-30px;width:420px;height:200px;opacity:.13;background:repeating-linear-gradient(90deg,var(--on-deep) 0 10px,transparent 10px 26px);-webkit-mask:linear-gradient(0deg,#000 0,transparent 100%);mask:linear-gradient(0deg,#000 0,transparent 100%);clip-path:polygon(0 100%,0 78%,8% 78%,8% 55%,16% 55%,16% 66%,24% 66%,24% 34%,32% 34%,32% 60%,40% 60%,40% 22%,48% 22%,48% 48%,56% 48%,56% 8%,64% 8%,64% 40%,100% 40%,100% 100%)}
.band-in{position:relative;z-index:1;padding:30px 16px 84px}
.band.corta .band-in{padding-bottom:44px}
.eyebrow{display:inline-flex;align-items:center;gap:8px;font-size:.78rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--ochre);margin:0 0 12px}
h1,h2,h3{font-family:var(--serif);font-weight:700;letter-spacing:-.012em}
h1{font-size:clamp(1.85rem,5vw,2.85rem);line-height:1.1;margin:0 0 12px;text-wrap:balance;max-width:900px}
.band h1{color:#fff}
.sub{font-size:1.08rem;color:var(--on-deep-2);margin:0 0 16px;max-width:760px}.sub strong{color:#fff}
.trust{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:.88rem;color:var(--on-deep-2);margin:0;padding:0;list-style:none}
.trust li{display:inline-flex;align-items:center;gap:7px}.trust .ico{color:var(--ochre)}
.briciole{font-size:.85rem;color:var(--on-deep-2);margin:0 0 14px}.briciole a{color:var(--on-deep)}
h2{font-size:clamp(1.38rem,3vw,1.7rem);line-height:1.2;margin:46px 0 12px;scroll-margin-top:16px;text-wrap:balance}
h3{font-size:1.14rem;margin:24px 0 8px}
p{margin:0 0 14px}
.lead{font-size:1.05rem;color:var(--ink-2);max-width:800px}
.small{font-size:.87rem;color:var(--ink-3)}
.testo p,.testo li{max-width:800px}.testo li{margin-bottom:8px}.testo ul,.testo ol{padding-left:22px}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:20px;min-width:0;box-shadow:var(--sh-1)}
.pull{margin-top:-60px;position:relative;z-index:2}
.calc{box-shadow:var(--sh-2);padding:0!important;overflow:hidden}
.calc-h{display:flex;align-items:center;flex-wrap:wrap;gap:8px 12px;margin:0;padding:16px 20px;border-bottom:1px solid var(--line)}
.calc-h h2{display:flex;align-items:center;gap:10px;margin:0;font-size:1.25rem}.calc-h h2 .ico{color:var(--ochre-ink);width:24px;height:24px}
.pill{display:inline-block;font-size:.74rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);background:var(--accent-2);border-radius:999px;padding:3px 10px}
.calc-g{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.08fr)}
.calc-in{padding:18px 20px;display:grid;gap:16px;align-content:start;border-right:1px solid var(--line)}
.calc-in fieldset{margin:0;padding:0;border:0;min-width:0}
.calc-in legend{font-weight:800;font-size:.92rem;padding:0;margin-bottom:8px}
.salari{display:grid;grid-template-columns:1fr 1fr;gap:8px 10px}
.salari label{display:grid;grid-template-columns:3.4em minmax(0,1fr);align-items:center;gap:6px;font-weight:800;font-size:.88rem;color:var(--ink-2)}
.salari label.largo{grid-column:1/-1;grid-template-columns:minmax(0,1fr);font-weight:700}
.campo{position:relative;display:block}.campo::before{content:"$";position:absolute;left:11px;top:50%;transform:translateY(-50%);color:var(--ink-3);font-weight:700;pointer-events:none}
.calc-in input[type=text],.calc-in input[type=number],.calc-in select{font:inherit;font-weight:600;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:9px 11px;width:100%;min-height:46px;font-variant-numeric:tabular-nums}
.campo input{padding-left:24px!important}
.calc-in input:focus,.calc-in select:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 22%,transparent)}
.calc-2{display:grid;grid-template-columns:1fr 1fr;gap:12px}.calc-2 label{display:grid;gap:6px;font-weight:700;font-size:.9rem}
.check{display:flex;gap:10px;align-items:flex-start;font-weight:600;font-size:.9rem;color:var(--ink-2);margin:0 0 8px;line-height:1.35}.check input{margin:2px 0 0;width:18px;height:18px;accent-color:var(--accent);flex:none}
.calc-out{padding:18px 20px;background:var(--accent-2);display:grid;align-content:start;gap:14px;min-width:0}
.tot{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.tot div{background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:10px 12px;min-width:0}
.tot div.main{grid-column:1/-1;display:flex;align-items:baseline;justify-content:space-between;flex-wrap:wrap;gap:4px 12px;border-color:color-mix(in srgb,var(--accent) 40%,var(--line))}
.tot b{display:block;font-family:var(--serif);font-size:clamp(1.2rem,3vw,1.45rem);line-height:1.15;font-variant-numeric:tabular-nums;color:var(--ink)}
.tot .main b{font-size:clamp(1.9rem,5.4vw,2.5rem);color:var(--accent)}
.tot span{display:block;font-size:.78rem;color:var(--ink-3);font-weight:700;line-height:1.3}
.ris{width:100%;border-collapse:collapse;font-size:.88rem;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);overflow:hidden}
.ris th,.ris td{padding:7px 8px;border-bottom:1px solid var(--line);text-align:right;font-variant-numeric:tabular-nums;vertical-align:top}
.ris th:first-child,.ris td:first-child{text-align:left}
.ris th{background:var(--mute);font-size:.7rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-2)}
.ris tfoot td{font-weight:800;border-bottom:0}.solo-m{display:none;font-weight:600;color:var(--ink-2)}.ris td small{display:block;color:var(--ink-3);font-size:.76rem;font-weight:600;text-align:left;margin-top:2px;white-space:normal}
.ris tr.extra td{color:var(--ink-2);font-size:.82rem}
.ris tr.has-sp td{border-bottom:0;padding-bottom:2px}.ris tr.sp td{text-align:left;font-size:.78rem;color:var(--ink-3);padding-top:0;font-weight:500;line-height:1.4}
.anteprima{display:none;margin:0;padding:10px 12px;border-radius:var(--r-s);background:var(--accent-2);font-weight:700;font-size:.92rem;color:var(--ink-2)}.anteprima b{color:var(--accent);font-family:var(--serif);font-size:1.15rem}.anteprima a{font-weight:700}
.ris .st{font-weight:800}.ris .zero{color:var(--ink-3)}
.avvisi{margin:0;padding:0;list-style:none;display:grid;gap:6px;font-size:.84rem;color:var(--ink-2)}
.avvisi li{background:var(--card);border-left:3px solid var(--ochre);border-radius:6px;padding:7px 10px}.avvisi li.forte{border-left-color:var(--bad)}
.azioni{display:flex;flex-wrap:wrap;gap:8px}
.calc-f{margin:0;padding:14px 20px;border-top:1px solid var(--line);font-size:.86rem;color:var(--ink-3)}
.calc-f details{margin-top:6px}.calc-f summary{cursor:pointer;font-weight:700;color:var(--ink-2)}
.calc-f ol{margin:8px 0 0;padding-left:20px}.calc-f li{margin-bottom:6px}
.vuoto{font-size:.92rem;color:var(--ink-2);background:var(--card);border:1px dashed var(--line-2);border-radius:var(--r-s);padding:14px}
.btn{display:inline-flex;align-items:center;gap:8px;font:inherit;font-size:.92rem;font-weight:800;background:var(--accent);color:var(--on-accent);border:0;border-radius:var(--r-s);padding:9px 15px;cursor:pointer;min-height:42px;text-decoration:none}
.btn:hover{background:var(--accent-h);color:var(--on-accent)}
.btn.sec{background:var(--card);color:var(--accent);border:1.5px solid color-mix(in srgb,var(--accent) 50%,transparent)}.btn.sec:hover{background:var(--accent-2);color:var(--accent-h)}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0;padding:0;overflow:hidden;box-shadow:var(--sh-2)}
.stat{padding:18px 20px;border-right:1px solid var(--line);min-width:0}.stat:last-child{border-right:0}
.stat b{display:block;font-family:var(--serif);font-size:clamp(1.45rem,3.6vw,2rem);line-height:1.1;font-variant-numeric:tabular-nums}
.stat span{display:block;font-size:.84rem;color:var(--ink-3);line-height:1.35;margin-top:6px}.stat.main b{color:var(--accent)}
.asof{margin:0;padding:10px 20px;background:var(--mute);border-top:1px solid var(--line);font-size:.86rem;color:var(--ink-2);grid-column:1/-1}
.nota{position:relative;background:var(--warn-2);border:1px solid color-mix(in srgb,var(--warn-l) 60%,transparent);padding:13px 16px 13px 48px;border-radius:var(--r-s);font-size:.95rem;margin:20px 0;color:var(--ink)}
.nota .ico{position:absolute;left:16px;top:15px;color:var(--warn);width:20px;height:20px}.nota p{margin:0 0 6px}.nota p:last-child{margin:0}
.nota.info{background:var(--accent-2);border-color:color-mix(in srgb,var(--accent) 35%,transparent)}.nota.info .ico{color:var(--accent)}
.tab{border:1px solid var(--line);border-radius:var(--r);background:var(--card);box-shadow:var(--sh-1);overflow-x:auto;-webkit-overflow-scrolling:touch;margin:0 0 8px}
table.dati{border-collapse:collapse;width:100%;font-size:.92rem}
table.dati th,table.dati td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
table.dati td.n,table.dati th.n{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
table.dati th{background:var(--mute);font-size:.73rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2);vertical-align:bottom}
table.dati tbody tr:last-child td{border-bottom:0}table.dati td a{font-weight:700}
table.dati td.na{color:var(--ink-3);font-style:italic}
table.dati th[scope=row]{vertical-align:top;background:var(--card);font-size:.95rem;text-transform:none;letter-spacing:0;color:var(--ink)}
.vuoto ol{margin:8px 0 0;padding-left:20px}.vuoto li{margin-bottom:4px}
.barre{display:grid;gap:8px;margin:6px 0 0;padding:0;list-style:none}
.barre li{display:grid;grid-template-columns:3.2em minmax(0,1fr) 6.6em;align-items:center;gap:10px;font-size:.88rem}
.barre li b{font-weight:800}.barre li i{display:block;height:12px;border-radius:6px;background:var(--bar);min-width:3px}.barre.r li i{background:var(--bar-2)}
.barre li span{text-align:right;font-variant-numeric:tabular-nums;font-weight:700;color:var(--ink-2)}
.cols{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px}
.formula{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.86rem;background:var(--mute);border:1px solid var(--line);border-radius:var(--r-s);padding:12px 14px;margin:0 0 14px;overflow-x:auto;white-space:pre-wrap;line-height:1.55}
.esempio{border:1px solid var(--line);border-left:4px solid var(--ochre);border-radius:var(--r-s);background:var(--card);padding:12px 16px;margin:0 0 12px}
.esempio p{margin:0 0 4px}.esempio .ok{color:var(--accent);font-weight:800}
.faq{border-top:1px solid var(--line);padding:4px 0 6px}.faq h3{margin:16px 0 6px;font-size:1.08rem}.faq p{margin:0 0 6px;max-width:800px}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;margin:0;padding:0;list-style:none}
.griglia a{display:flex;flex-direction:column;gap:3px;height:100%;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:13px 15px;text-decoration:none;color:var(--ink);font-weight:800;box-shadow:var(--sh-1);transition:border-color .15s,transform .15s}
.griglia a:hover{border-color:var(--accent);transform:translateY(-1px)}.griglia a small{font-weight:600;color:var(--ink-3);font-size:.86rem;line-height:1.4}
.griglia.stati a b{font-family:var(--serif);font-size:1.25rem;color:var(--accent)}
sup.ref{font-size:max(11px,.72em);line-height:0;margin-left:2px;white-space:nowrap}sup.ref a{text-decoration:none;font-weight:800}
.fonti-box{margin-top:46px;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:var(--r-s);padding:16px 20px;font-size:.9rem;color:var(--ink-2)}
.fonti-box h2{display:flex;align-items:center;gap:8px;font-size:1.12rem;margin:0 0 8px;color:var(--ink)}.fonti-box h2 .ico{color:var(--accent)}
.fonti-box ol{margin:0 0 8px;padding-left:22px}.fonti-box li{margin-bottom:6px}.fonti-box a{overflow-wrap:anywhere}
.fonti-box li:target{background:var(--ochre-2);border-radius:6px}
.disclaimer{margin:28px 0 0;font-size:.88rem;color:var(--ink-2);background:var(--mute);border-radius:var(--r-s);padding:12px 16px}
.form{display:grid;gap:14px;max-width:760px}.form label{display:grid;gap:6px;font-weight:700;font-size:.95rem}
.form input[type=text],.form input[type=url],.form input[type=email],.form textarea{font:inherit;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:10px 12px;width:100%;min-height:46px}
.form input:focus,.form textarea:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 22%,transparent)}
.form .check{display:flex;font-weight:500}.form .btn{justify-self:start}
.hp{position:absolute;left:-9999px}.ok{background:var(--accent-2);border:1px solid var(--accent);padding:14px;border-radius:var(--r-s);max-width:760px}.errore{color:var(--bad);font-weight:700;margin:0}
.ad-slot{margin:24px 0}.ad-slot:empty{display:none}
.aff-box{margin:20px 0;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--ochre);border-radius:var(--r);padding:16px 18px}
.aff-box h2,.aff-box h3{margin:0 0 6px;font-size:1.1rem}.aff-box p{margin:0 0 8px}.aff-box ul{margin:0 0 10px;padding-left:20px}
.aff-tag{display:inline-block;vertical-align:middle;margin-left:6px;font-family:var(--sans);font-size:.68rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);border:1px solid var(--line-2);border-radius:999px;padding:1px 8px}
.etich{display:inline-block;font-size:.7rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-3);border:1px solid var(--line-2);border-radius:999px;padding:0 7px;margin-left:4px;vertical-align:1px}
footer{margin-top:60px;background:var(--deep);color:var(--on-deep-2);font-size:.88rem;padding:40px 0 34px}
footer a{color:var(--on-deep)}footer a:hover{color:var(--ochre)}
footer .f-grid{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1fr) minmax(0,1fr);gap:28px}
footer .logo{margin-bottom:12px}footer p{margin:0 0 10px;max-width:640px}footer strong{color:var(--on-deep)}
footer ul{list-style:none;margin:0;padding:0;display:grid;gap:7px}
footer h2{font-family:var(--sans);font-size:.76rem;letter-spacing:.12em;text-transform:uppercase;color:var(--ochre);margin:4px 0 12px}
footer .f-base{border-top:1px solid rgba(255,255,255,.12);margin-top:24px;padding-top:16px;font-size:.82rem;max-width:none}
@media (max-width:920px){.calc-g{grid-template-columns:1fr}.calc-in{border-right:0;border-bottom:1px solid var(--line)}.stats{grid-template-columns:repeat(2,minmax(0,1fr))}
.stat:nth-child(2){border-right:0}.stat:nth-child(-n+2){border-bottom:1px solid var(--line)}.cols{grid-template-columns:1fr}footer .f-grid{grid-template-columns:1fr 1fr}footer .f-grid>div:first-child{grid-column:1/-1}}
@media (max-width:920px){.anteprima{display:block}}
@media (max-width:820px){nav.menu{display:none}.nav-m{display:block}header.top .wrap{min-height:60px}.band-in{padding-top:22px}}
@media (max-width:560px){.salari{grid-template-columns:1fr 1fr}.salari label{grid-template-columns:minmax(0,1fr);gap:4px}
table.stack thead{display:none}table.stack,table.stack tbody,table.stack tr,table.stack td,table.stack th{display:block;width:100%}
table.stack tr{border-bottom:1px solid var(--line);padding:10px 12px}table.stack tbody tr:last-child{border-bottom:0}
table.stack td,table.stack th{border:0!important;padding:3px 0!important;text-align:left!important;white-space:normal!important}
table.stack td[data-l]::before{content:attr(data-l) ": ";font-size:.86rem;font-weight:700;color:var(--ink-3)}
table.stack th[scope=row],table.stack td:first-child{font-size:1rem}table.stack caption{display:block}
.griglia{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.griglia a{padding:11px 12px}.calc-2{grid-template-columns:1fr}.card,.calc-in,.calc-out{padding:16px}.calc-h{padding:14px 16px}.calc-f{padding:12px 16px}
.tot{grid-template-columns:1fr 1fr}.solo-m{display:inline}.tot div.mensile{grid-column:1/-1}.stat{padding:14px}.ris{font-size:.8rem}.ris th,.ris td{padding:6px 5px}.ris .col-w{display:none}
table.dati{font-size:.86rem}table.dati th,table.dati td{padding:8px}.logo{font-size:1.03rem;gap:8px}.logo img{width:30px;height:30px}
.barre li{grid-template-columns:2.9em minmax(0,1fr) 5.6em}footer .f-grid{grid-template-columns:1fr}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
@media print{header.top,footer,.nav-m,.tema,.azioni,.ad-slot{display:none!important}.band{background:none;color:#000}.band h1,.sub{color:#000}}
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
    "scale": '<path d="M12 3v18M7 21h10M5 7h14M5 7l-3 7a3.5 3.5 0 0 0 6 0zM19 7l-3 7a3.5 3.5 0 0 0 6 0z"/>',
    "map": '<path d="M9 4 3.5 6v14L9 18l6 2 5.5-2V4L15 6z"/><path d="M9 4v14M15 6v14"/>',
    "copy": '<rect x="8.5" y="8.5" width="12" height="12" rx="2"/><path d="M15.5 8.5V5.5a2 2 0 0 0-2-2h-8a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h3"/>',
    "link": '<path d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1 1"/><path d="M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1-1"/>',
    "reset": '<path d="M3.5 12a8.5 8.5 0 1 0 2.5-6"/><path d="M3.5 4v5h5"/>',
    "clock": '<circle cx="12" cy="12" r="9.5"/><path d="M12 7v5l3 2"/>',
    "people": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14a6.5 6.5 0 0 1 3.5 6"/>',
    "trend": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
}

# Marchio: tessera verde notte con istogramma di otto barre (le otto giurisdizioni), una in ocra
MARCHIO = ('<rect width="40" height="40" rx="10" fill="#0C2F2B"/>'
           '<path d="M8 31h24" stroke="#4FC9B3" stroke-width="2" stroke-linecap="round" opacity=".55"/>'
           '<rect x="8.5" y="20" width="3.4" height="9" rx="1" fill="#4FC9B3"/>'
           '<rect x="14.2" y="15" width="3.4" height="14" rx="1" fill="#4FC9B3"/>'
           '<rect x="19.9" y="9" width="3.4" height="20" rx="1" fill="#E0952B"/>'
           '<rect x="25.6" y="13" width="3.4" height="16" rx="1" fill="#4FC9B3"/>')
FAVICON_SVG = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">{MARCHIO}</svg>\n'

TEMA_JS = "(function(){try{var t=localStorage.getItem('pt-theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();"

# ---------------------------------------------------------------- motore (copia di motore.py, stesso ordine delle operazioni)
MOTORE_JS = r"""
var ORDINE=['nsw','vic','qld','wa','sa','tas','act','nt'];
function pos(x){return x>0?x:0;}
function calcolaStato(s,P,w,W,f,rv,rq){
  var p=P[s],o={s:s,w:w,stato:'ok',soglia:0,imponibile:0,aliquota:null,tassa:0,extra:0,avvisi:[]};
  if(!(w>0)){o.stato='zero';return o;}
  var q=w/W,d,al,extra,i,r;
  if(s==='nsw'){
    d=p.soglia*q*f;o.soglia=d;o.imponibile=pos(w-d);o.aliquota=p.aliquota/100;o.tassa=o.imponibile*o.aliquota;
  }else if(s==='vic'){
    var d1=p.soglia*f*q;
    d=Math.min(d1,pos(d1-(w-p.phase_da*f*q)*(p.phase_quota/100)));
    if(W>p.phase_da*f)o.avvisi.push(d>0?'vic_phase':'vic_no_soglia');
    o.soglia=d;o.imponibile=pos(w-d);o.aliquota=(rv?p.regionale:p.aliquota)/100;o.tassa=o.imponibile*o.aliquota;
    extra=0;for(i=0;i<p.sovrattasse.length;i++){extra+=pos(w-p.sovrattasse[i][0]*q*f)*(p.sovrattasse[i][1]/100);}
    o.extra=extra;if(extra>0)o.avvisi.push('vic_sovrattasse');
  }else if(s==='qld'){
    var kf=p.soglia*f,ad=pos(q*(kf-(W-kf)/p.rapporto));
    o.soglia=ad;o.imponibile=pos(w-ad);
    al=W<=p.aliquota_alta_da?p.aliquota:p.aliquota_alta;
    if(rq){if(W<=p.regionale_max){al=al-p.sconto_regionale;}else{o.avvisi.push('qld_regionale_oltre');}}
    o.aliquota=al/100;o.tassa=o.imponibile*o.aliquota;
    extra=0;for(i=0;i<p.levy.length;i++){extra+=pos(w-p.levy[i][0]*q*f)*(p.levy[i][1]/100);}
    o.extra=extra;if(extra>0)o.avvisi.push('qld_levy');
  }else if(s==='wa'){
    var aat=p.soglia*f,aut=p.soglia_superiore*f;o.aliquota=p.aliquota/100;
    if(W<=aat){o.soglia=w;o.imponibile=0;}
    else if(W>=aut){o.soglia=0;o.imponibile=w;o.avvisi.push('wa_no_soglia');}
    else{var tv=p.soglia/(p.soglia_superiore-p.soglia);d=(aat-(W-aat)*tv)*q;o.soglia=d;o.imponibile=pos(w-d);}
    o.tassa=o.imponibile*o.aliquota;
  }else if(s==='sa'){
    if(W<=p.soglia*f){o.soglia=w;}
    else{
      var tarw=W/f;
      if(tarw>p.piena_da){r=p.aliquota/100;}else{r=(tarw-p.soglia)/(p.piena_da-p.soglia)*(p.aliquota/100);}
      d=q*p.deduzione*f;o.soglia=d;o.imponibile=pos(w-d);o.aliquota=r;o.tassa=o.imponibile*r;
      if(tarw<=p.piena_da)o.avvisi.push('sa_variabile');
    }
  }else if(s==='tas'){
    var t1=p.soglia*f,t2=p.soglia2*f;
    if(W<=t1){o.soglia=w;}
    else if(W<=t2){o.soglia=q*t1;o.imponibile=pos(w-q*t1);o.aliquota=p.aliquota1/100;o.tassa=o.imponibile*o.aliquota;}
    else{o.soglia=q*t1;o.imponibile=pos(w-q*t1);o.aliquota=null;
      o.tassa=(t2-t1)*q*(p.aliquota1/100)+pos(w-q*t2)*(p.aliquota2/100);o.avvisi.push('tas_due_fasce');}
  }else if(s==='act'){
    var tac=p.soglia*f;
    if(W<=tac){o.soglia=w;}
    else if(W<=p.soglia){o.stato='non_calcolato';o.avvisi.push('act_anno_parziale');}
    else{
      r=null;for(i=0;i<p.scaglioni.length;i++){var lim=p.scaglioni[i][0];if(lim===null||W<=lim){r=p.scaglioni[i][1]/100;break;}}
      d=q*tac;o.soglia=d;o.imponibile=pos(w-d);o.aliquota=r;o.tassa=o.imponibile*r;o.avvisi.push('act_su_tutto');
    }
  }else if(s==='nt'){
    var eta=p.soglia*f;
    if(W<=eta){o.soglia=w;}
    else{
      ad=pos(eta-(W-eta)/2);r=(W>=p.aliquota_alta_da?p.aliquota_alta:p.aliquota)/100;
      o.soglia=q*ad;o.imponibile=pos(w-q*ad);o.aliquota=r;o.tassa=o.imponibile*r;if(ad===0)o.avvisi.push('nt_no_soglia');
    }
  }
  if(o.stato==='ok'&&o.tassa<=0&&o.extra<=0)o.stato='sotto';
  return o;
}
function calcola(P,salari,giorni,giorniAnno,rv,rq){
  var W=0,k;for(k in salari){if(Object.prototype.hasOwnProperty.call(salari,k)){var v=salari[k];W+=v>0?v:0;}}
  var g=Math.min(Math.max(giorni,1),giorniAnno),f=g/giorniAnno,righe=[],tot=0,extra=0,nc=[];
  for(var i=0;i<ORDINE.length;i++){var s=ORDINE[i],w=salari[s]||0;if(!(w>0))continue;
    var r=calcolaStato(s,P,w,W,f,rv,rq);righe.push(r);
    if(r.stato==='non_calcolato'){nc.push(s);}else{tot+=r.tassa;extra+=r.extra;}}
  return {W:W,f:f,righe:righe,totale:tot,extra:extra,complessivo:tot+extra,mensile:(tot+extra)/(12*f),non_calcolati:nc};
}
"""

# ---------------------------------------------------------------- interfaccia (tema, calcolatore, copia, link)
APP_JS = MOTORE_JS + r"""
(function(){
  var b=document.querySelector('[data-tema]');
  if(b)b.addEventListener('click',function(){var r=document.documentElement,c=r.getAttribute('data-theme');
    if(!c)c=window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
    var n=c==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('pt-theme',n);}catch(e){}});
  document.querySelectorAll('form[data-correzioni]').forEach(function(form){form.addEventListener('submit',function(ev){ev.preventDefault();
    var err=form.querySelector('[data-errore]');err.hidden=true;if(!form.checkValidity()){form.reportValidity();return;}
    var bt=form.querySelector('button');bt.disabled=true;
    fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(new FormData(form)).toString()})
    .then(function(r){if(!r.ok)throw new Error(r.status);form.hidden=true;var ok=form.parentNode.querySelector('[data-ok]');if(ok)ok.hidden=false;})
    .catch(function(){err.hidden=false;bt.disabled=false;});});});
  var f=document.querySelector('[data-calc]');if(!f)return;
  var D=JSON.parse(document.getElementById('calc-dati').textContent),P=D.parametri;
  var M0=new Intl.NumberFormat('en-AU',{style:'currency',currency:'AUD',maximumFractionDigits:0,minimumFractionDigits:0});
  function $(x){return M0.format(Math.round(x));}
  function pc(x){if(x===null||x===undefined)return '';var v=Math.round(x*1e6)/1e4;return (Math.round(v*10000)/10000).toString()+'%';}
  function num(v){v=String(v||'').trim().toLowerCase().replace(/[$,\s]/g,'').replace(/aud$/,'');var m=1;
    if(/k$/.test(v)){m=1e3;v=v.slice(0,-1);}else if(/(m|mil|million)$/.test(v)){m=1e6;v=v.replace(/(m|mil|million)$/,'');}else if(/(b|bn)$/.test(v)){m=1e9;v=v.replace(/(b|bn)$/,'');}
    var x=parseFloat(v);return isFinite(x)&&x>0?Math.round(x*m*100)/100:0;}
  function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  var campi=D.campi,out=f.querySelector('[data-out]'),ant=f.querySelector('[data-anteprima]'),ultimo=null;
  function leggi(){var s={};campi.forEach(function(c){var e=f.elements[c];if(e)s[c]=num(e.value);});
    var g=parseInt(f.elements.giorni.value,10);if(!(g>=1))g=D.giorni_anno;if(g>D.giorni_anno)g=D.giorni_anno;
    return {salari:s,giorni:g,rv:!!(f.elements.rv&&f.elements.rv.checked),rq:!!(f.elements.rq&&f.elements.rq.checked),gruppo:!!(f.elements.gruppo&&f.elements.gruppo.value==='si')};}
  function spiega(r,res){var q=r.w/res.W,fr=res.f,p=P[r.s],sh=(q*100).toFixed(q<0.1?2:1)+'% of Australian wages',dy=Math.round(fr*D.giorni_anno)+'/'+D.giorni_anno+' days';
    if(r.stato==='non_calcolato')return D.testi.act_anno_parziale;
    if(r.stato==='sotto')return 'Total Australian wages are not above the '+D.nomi[r.s]+' threshold for the days you employed.';
    switch(r.s){
      case 'nsw':return '$1,200,000 × '+sh+' × '+dy+' = '+$(r.soglia)+'; tax = ('+$(r.w)+' − '+$(r.soglia)+') × 5.45%';
      case 'vic':return (res.W<=p.phase_da*fr?'$1,000,000 × '+sh+' × '+dy:r.soglia>0?'Threshold phased out at 50% above $3m × '+dy:'Threshold fully phased out ($5m × '+dy+' or more)')+' = '+$(r.soglia)+'; tax at '+pc(r.aliquota)+(r.extra>0?'; surcharges '+$(r.extra):'');
      case 'qld':return 'Deduction = '+sh+' × ($1.3m × '+dy+' − excess ÷ 7) = '+$(r.soglia)+'; rate '+pc(r.aliquota)+(r.extra>0?'; mental health levy '+$(r.extra):'');
      case 'wa':return r.soglia>0?'Diminishing threshold (2/13 taper) × '+sh+' = '+$(r.soglia)+'; tax at 5.5%':'No deductable amount at $7.5m or more; 5.5% on all WA wages';
      case 'sa':return 'Deduction = $600,000 × '+sh+' × '+dy+' = '+$(r.soglia)+'; rate '+pc(r.aliquota)+(r.aliquota<0.0495?' (variable band)':'');
      case 'tas':return 'Thresholds $1.25m and $2m × '+sh+' × '+dy+'; '+(r.aliquota===null?'4% on the band, 6.1% above':'4% above the lower threshold');
      case 'act':return '$1,750,000 × '+sh+' × '+dy+' = '+$(r.soglia)+'; '+pc(r.aliquota)+' (bracket set by total wages) on all ACT wages above it';
      case 'nt':return 'Deduction = '+sh+' × ($2.5m × '+dy+' − half the excess) = '+$(r.soglia)+'; rate '+pc(r.aliquota);
    }return '';}
  function render(){
    var v=leggi(),res=calcola(P,v.salari,v.giorni,D.giorni_anno,v.rv,v.rq);ultimo={v:v,res:res};
    if(!res.righe.length){out.innerHTML='<div class="vuoto">'+D.vuoto_html+'</div>';if(ant)ant.textContent=D.testi.vuoto;aggiornaUrl(v);return;}
    var esc_act=res.non_calcolati.length>0,etTot=esc_act?'Estimated payroll tax, '+D.anno+': total excludes ACT (not calculated)':'Estimated payroll tax, '+D.anno;
    var etMese=v.giorni<D.giorni_anno?'Per month employed ('+v.giorni+' days = '+(Math.round(v.giorni/D.giorni_anno*120)/10)+' months)':'Monthly average (annual ÷ 12)';
    var h='<div class="tot"><div class="main"><span>'+etTot+'</span><b>'+$(res.complessivo)+'</b>'+(esc_act?'<span>ACT: ask the <a href="https://www.revenue.act.gov.au/payroll-tax" rel="noopener">ACT Revenue Office</a></span>':'')+'</div>'+
      '<div class="mensile"><span>'+etMese+'</span><b>'+$(res.mensile)+'</b></div>'+
      '<div><span>Total Australian wages</span><b>'+$(res.W)+'</b></div>'+
      '<div><span>Share of wages</span><b>'+(res.W>0?(Math.round(res.complessivo/res.W*10000)/100).toFixed(2):'0.00')+'%</b></div></div>';
    h+='<table class="ris"><thead><tr><th scope="col">State</th><th scope="col" class="col-w">Wages</th><th scope="col">Threshold used</th><th scope="col">Rate</th><th scope="col">Tax</th></tr></thead><tbody>';
    var avv={};
    res.righe.forEach(function(r){
      r.avvisi.forEach(function(a){avv[a]=1;});
      var nome='<a href="/'+r.s+'/">'+D.brevi[r.s]+'</a>';
      if(r.stato==='non_calcolato'){h+='<tr class="has-sp"><td class="st">'+nome+'</td><td class="col-w">'+$(r.w)+'</td><td colspan="3">not calculated</td></tr><tr class="sp"><td colspan="5">'+esc(spiega(r,res))+'</td></tr>';return;}
      var rate=r.aliquota===null?(r.stato==='sotto'?'–':'4% / 6.1%'):pc(r.aliquota);
      h+='<tr class="has-sp"><td class="st">'+nome+'</td><td class="col-w">'+$(r.w)+'</td><td>'+$(r.soglia)+'</td><td>'+rate+'</td><td'+(r.stato==='sotto'?' class="zero"':'')+'>'+$(r.tassa)+'</td></tr>';
      h+='<tr class="sp"><td colspan="5">'+esc(spiega(r,res))+'</td></tr>';
      if(r.extra>0)h+='<tr class="extra"><td colspan="4">'+(r.s==='qld'?'Queensland mental health levy':'Victorian surcharges (mental health + COVID-19 debt)')+'</td><td>'+$(r.extra)+'</td></tr>';
    });
    h+='</tbody><tfoot><tr><td>Total'+(esc_act?' excl. ACT':'')+'<span class="solo-m"> · wages '+$(res.W)+'</span></td><td class="col-w">'+$(res.W)+'</td><td></td><td></td><td>'+$(res.complessivo)+'</td></tr></tfoot></table>';
    var L=[];Object.keys(avv).forEach(function(a){if(D.testi[a])L.push('<li'+(a==='act_anno_parziale'?' class="forte"':'')+'>'+D.testi[a]+'</li>');});
    if(v.gruppo)L.push('<li>'+D.testi.gruppo+'</li>');
    if(v.giorni<D.giorni_anno)L.push('<li>'+D.testi.parziale+'</li>');
    if(v.salari.altro>0)L.push('<li>'+D.testi.altro+'</li>');
    L.push('<li>'+D.testi.stima+'</li>');
    h+='<ul class="avvisi">'+L.join('')+'</ul>';
    out.innerHTML=h;
    if(ant)ant.innerHTML='Estimated payroll tax: <b>'+$(res.complessivo)+'</b> · <a href="#'+out.id+'">see the breakdown</a>';
    var aff=document.querySelector('[data-aff-calc]');if(aff)aff.hidden=!(res.complessivo>0);
    aggiornaUrl(v);
  }
  function aggiornaUrl(v){if(!D.url_stato)return;try{var u=new URLSearchParams();campi.forEach(function(c){if(v.salari[c]>0)u.set(c,String(v.salari[c]));});
    if(v.giorni<D.giorni_anno)u.set('d',String(v.giorni));if(v.rv)u.set('rv','1');if(v.rq)u.set('rq','1');if(v.gruppo)u.set('g','1');
    var s=u.toString();history.replaceState(null,'',location.pathname+(s?'?'+s:'')+location.hash);}catch(e){}}
  function daUrl(){try{var u=new URLSearchParams(location.search),c=false;campi.forEach(function(k){if(u.has(k)&&f.elements[k]){f.elements[k].value=Number(num(u.get(k))).toLocaleString('en-AU');c=true;}});
    if(c){campi.forEach(function(k){if(!u.has(k)&&f.elements[k])f.elements[k].value='';});}
    if(u.has('d'))f.elements.giorni.value=u.get('d');if(u.get('rv')==='1'&&f.elements.rv)f.elements.rv.checked=true;if(u.get('rq')==='1'&&f.elements.rq)f.elements.rq.checked=true;
    if(u.get('g')==='1'&&f.elements.gruppo)f.elements.gruppo.value='si';}catch(e){}}
  function testo(){if(!ultimo)return '';var r=ultimo.res,v=ultimo.v,t=['Payroll tax estimate '+D.anno+' ('+location.host+')','Total Australian wages: '+$(r.W)+'; days paid: '+v.giorni+'/'+D.giorni_anno];
    r.righe.forEach(function(x){t.push(D.brevi[x.s]+': wages '+$(x.w)+(x.stato==='non_calcolato'?' – not calculated (see the ACT Revenue Office)':', threshold used '+$(x.soglia)+', tax '+$(x.tassa)+(x.extra>0?' + '+$(x.extra)+(x.s==='qld'?' mental health levy':' surcharges'):'')));});
    t.push('Total'+(r.non_calcolati.length?' excluding ACT (not calculated)':'')+': '+$(r.complessivo)+(v.giorni<D.giorni_anno?' (per month employed ':' (monthly average ')+$(r.mensile)+')');t.push('Estimate only, not tax advice. Formulas and sources: '+location.origin+'/how-we-check/');return t.join('\n');}
  function copia(txt,bt){var ok=function(){var o=bt.textContent;bt.textContent='Copied';setTimeout(function(){bt.textContent=o;},1600);};
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(txt).then(ok,function(){fallback(txt);ok();});}else{fallback(txt);ok();}}
  function fallback(txt){var a=document.createElement('textarea');a.value=txt;a.setAttribute('readonly','');a.style.position='absolute';a.style.left='-9999px';document.body.appendChild(a);a.select();try{document.execCommand('copy');}catch(e){}document.body.removeChild(a);}
  f.addEventListener('input',render);f.addEventListener('change',render);f.addEventListener('submit',function(e){e.preventDefault();render();});
  f.querySelectorAll('input[data-soldi]').forEach(function(i){i.addEventListener('blur',function(){var x=num(i.value);i.value=x>0?x.toLocaleString('en-AU'):'';});});
  var bc=f.querySelector('[data-copia]');if(bc)bc.addEventListener('click',function(){copia(testo(),bc);});
  var bl=f.querySelector('[data-link]');if(bl)bl.addEventListener('click',function(){copia(location.href,bl);});
  var br=f.querySelector('[data-azzera]');if(br)br.addEventListener('click',function(){campi.forEach(function(c){if(f.elements[c])f.elements[c].value='';});f.elements.giorni.value=D.giorni_anno;
    if(f.elements.rv)f.elements.rv.checked=false;if(f.elements.rq)f.elements.rq.checked=false;if(f.elements.gruppo)f.elements.gruppo.value='no';render();var p=f.querySelector('input[data-soldi]');if(p)p.focus();});
  daUrl();render();
})();
"""
