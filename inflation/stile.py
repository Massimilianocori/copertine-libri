"""Aspetto e codice del browser di Inflation Calculator US·UK·DE: CSS, icone, marchio, motore JS e interfaccia del calcolatore.

MOTORE_JS è la copia di motore.py (stesse regole). verifica.py esegue il file pubblicato in sito/assets/ con node e lo
confronta con il Python. Nessuno script esterno oltre a AdSense e GoatCounter; caratteri di sistema (niente font da scaricare).
"""

CSS = """
:root{--bg:#F6F5F1;--card:#FFFFFF;--ink:#181A2A;--ink-2:#3A3D52;--ink-3:#5B5F76;--line:#E2E1DA;--line-2:#C9C8C0;
--deep:#161A33;--deep-2:#202652;--on-deep:#EEF0FA;--on-deep-2:#B9BEDB;--accent:#2F4FD0;--accent-h:#22399E;--accent-2:#E8ECFC;--on-accent:#FFFFFF;
--amber:#E8930C;--amber-ink:#8A4F00;--amber-2:#FFF1D9;--mute:#EFEEE8;--bar:#2F4FD0;--neg:#0E8A6A;--bad:#B3261E;
--sh-1:0 1px 2px rgba(22,26,51,.06),0 1px 1px rgba(22,26,51,.04);--sh-2:0 24px 48px -26px rgba(22,26,51,.45),0 2px 8px rgba(22,26,51,.06);
--r:14px;--r-s:10px;--serif:Charter,"Bitstream Charter","Iowan Old Style","Palatino Linotype",Georgia,serif;
--sans:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0D0F1C;--card:#151830;--ink:#E8EAF6;--ink-2:#C0C4DE;--ink-3:#9499B8;--line:#252A4A;--line-2:#363C63;
--deep:#080A16;--deep-2:#121633;--on-deep:#E8EAF6;--on-deep-2:#A7ACD0;--accent:#8EA2FF;--accent-h:#B5C2FF;--accent-2:#1C2350;--on-accent:#0B0E22;
--amber:#F5B347;--amber-ink:#F5B347;--amber-2:#2B2110;--mute:#1A1E38;--bar:#8EA2FF;--neg:#4FD1A8;--bad:#FF8A80;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 24px 48px -26px rgba(0,0,0,.85),0 2px 8px rgba(0,0,0,.4)}}
:root[data-theme="dark"]{--bg:#0D0F1C;--card:#151830;--ink:#E8EAF6;--ink-2:#C0C4DE;--ink-3:#9499B8;--line:#252A4A;--line-2:#363C63;
--deep:#080A16;--deep-2:#121633;--on-deep:#E8EAF6;--on-deep-2:#A7ACD0;--accent:#8EA2FF;--accent-h:#B5C2FF;--accent-2:#1C2350;--on-accent:#0B0E22;
--amber:#F5B347;--amber-ink:#F5B347;--amber-2:#2B2110;--mute:#1A1E38;--bar:#8EA2FF;--neg:#4FD1A8;--bad:#FF8A80;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 24px 48px -26px rgba(0,0,0,.85),0 2px 8px rgba(0,0,0,.4)}
*{box-sizing:border-box}[hidden]{display:none!important}html{-webkit-text-size-adjust:100%;scroll-padding-top:16px}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:17px;line-height:1.6;overflow-wrap:break-word}
a{color:var(--accent);text-underline-offset:2px;text-decoration-thickness:1px}a:hover{color:var(--accent-h)}
:focus-visible{outline:3px solid var(--amber);outline-offset:2px;border-radius:4px}
.skip{position:absolute;left:-9999px;top:8px;background:var(--card);color:var(--ink);padding:8px 14px;border-radius:8px;z-index:50}.skip:focus{left:12px}
.ico{width:1.15em;height:1.15em;flex:none;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;vertical-align:-.2em}
.wrap{max-width:1120px;margin:0 auto;padding:0 16px}
header.top{background:var(--deep);color:var(--on-deep);position:relative;z-index:20;border-bottom:1px solid rgba(255,255,255,.07)}
header.top .wrap{display:flex;align-items:center;gap:10px;min-height:62px}
.logo{display:flex;align-items:center;gap:10px;font-family:var(--serif);font-weight:700;font-size:1.18rem;color:var(--on-deep);text-decoration:none;white-space:nowrap;margin-right:auto;line-height:1.1}
.logo:hover{color:#fff}.logo img{width:32px;height:32px;flex:none;display:block}.logo b{color:var(--amber);font-weight:inherit}
nav.menu{display:flex;gap:2px;font-size:.93rem}
nav.menu a{color:var(--on-deep-2);text-decoration:none;padding:7px 11px;border-radius:8px;white-space:nowrap}
nav.menu a:hover,nav.menu a[aria-current]{color:#fff;background:rgba(255,255,255,.1)}
.tema{display:grid;place-items:center;width:40px;height:40px;border-radius:10px;border:1px solid rgba(255,255,255,.22);background:none;color:var(--on-deep);cursor:pointer;flex:none}
.tema:hover{border-color:var(--amber)}.tema .ico{width:19px;height:19px}
.tema .i-sun{display:none}:root[data-theme="dark"] .tema .i-sun{display:block}:root[data-theme="dark"] .tema .i-moon{display:none}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .tema .i-sun{display:block}:root:not([data-theme="light"]) .tema .i-moon{display:none}}
.nav-m{display:none}
.nav-m summary{list-style:none;cursor:pointer;display:grid;place-items:center;width:40px;height:40px;border:1px solid rgba(255,255,255,.25);border-radius:10px;color:var(--on-deep)}
.nav-m summary::-webkit-details-marker{display:none}.nav-m[open] summary{background:rgba(255,255,255,.1);border-color:var(--amber)}
.nav-m nav{position:absolute;left:16px;right:16px;top:calc(100% + 4px);background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-2);padding:8px;display:grid;grid-template-columns:1fr 1fr;gap:2px}
.nav-m nav a{padding:11px 12px;border-radius:8px;color:var(--ink);text-decoration:none;font-weight:700;font-size:.95rem}.nav-m nav a:hover{background:var(--accent-2)}
.band{background:var(--deep);color:var(--on-deep);position:relative;overflow:hidden}
.band::before{content:"";position:absolute;inset:0;background:radial-gradient(560px 320px at 96% -10%,rgba(232,147,12,.30),transparent 64%),radial-gradient(720px 340px at -6% 130%,rgba(142,162,255,.26),transparent 62%),linear-gradient(180deg,var(--deep) 0,var(--deep-2) 100%)}
.band::after{content:"";position:absolute;right:-30px;bottom:0;width:440px;height:170px;opacity:.16;background:linear-gradient(0deg,var(--on-deep) 0,transparent 100%);clip-path:polygon(0 100%,0 92%,10% 88%,20% 86%,30% 80%,40% 76%,50% 66%,60% 58%,70% 44%,80% 34%,90% 22%,100% 8%,100% 100%)}
.band-in{position:relative;z-index:1;padding:28px 16px 84px}
.band.corta .band-in{padding-bottom:44px}
.eyebrow{display:inline-flex;align-items:center;gap:8px;font-size:.78rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--amber);margin:0 0 12px}
h1,h2,h3{font-family:var(--serif);font-weight:700;letter-spacing:-.01em}
h1{font-size:clamp(1.8rem,5vw,2.8rem);line-height:1.12;margin:0 0 12px;text-wrap:balance;max-width:900px}
.band h1{color:#fff}
.sub{font-size:1.08rem;color:var(--on-deep-2);margin:0 0 16px;max-width:780px}.sub strong{color:#fff}
.trust{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:.88rem;color:var(--on-deep-2);margin:0;padding:0;list-style:none}
.trust li{display:inline-flex;align-items:center;gap:7px}.trust .ico{color:var(--amber)}
.briciole{font-size:.85rem;color:var(--on-deep-2);margin:0 0 14px}.briciole a{color:var(--on-deep)}
h2{font-size:clamp(1.36rem,3vw,1.68rem);line-height:1.22;margin:44px 0 12px;scroll-margin-top:16px;text-wrap:balance}
h3{font-size:1.13rem;margin:24px 0 8px}
p{margin:0 0 14px}
.small{font-size:.87rem;color:var(--ink-3)}
.testo p,.testo li{max-width:800px}.testo li{margin-bottom:8px}.testo ul,.testo ol{padding-left:22px}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:20px;min-width:0;box-shadow:var(--sh-1)}
.pull{margin-top:-60px;position:relative;z-index:2}
.risposta{box-shadow:var(--sh-2)}.risposta p{font-size:1.1rem;max-width:860px}.risposta p:last-child{margin:0}
.risposta .big{display:block;font-family:var(--serif);font-size:clamp(2rem,6vw,2.9rem);line-height:1.1;color:var(--accent);font-weight:700;margin:2px 0 6px;font-variant-numeric:tabular-nums}
.calc{box-shadow:var(--sh-2);padding:0!important;overflow:hidden}
.calc-h{display:flex;align-items:center;flex-wrap:wrap;gap:8px 12px;margin:0;padding:16px 20px;border-bottom:1px solid var(--line)}
.calc-h h2{display:flex;align-items:center;gap:10px;margin:0;font-size:1.25rem}.calc-h h2 .ico{color:var(--amber-ink);width:24px;height:24px}
.pill{display:inline-block;font-size:.74rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--accent);background:var(--accent-2);border-radius:999px;padding:3px 10px}
.calc-g{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr)}
.calc-in{padding:18px 20px;display:grid;gap:14px;align-content:start;border-right:1px solid var(--line);margin:0}
.calc-in fieldset{margin:0;padding:0;border:0;min-width:0}
.calc-in legend,.calc-in .lab{display:block;font-weight:800;font-size:.92rem;padding:0;margin-bottom:6px}
.calc-in label{display:block;min-width:0}
.campo{position:relative;display:block}.campo::before{content:attr(data-sym);position:absolute;left:12px;top:50%;transform:translateY(-50%);color:var(--ink-3);font-weight:700;pointer-events:none}
.campo.dopo::before{left:auto;right:12px}
.calc-in input[type=text],.calc-in select{font:inherit;font-weight:600;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:9px 11px;width:100%;min-height:46px;font-variant-numeric:tabular-nums}
.campo input{padding-left:30px!important;font-size:1.15rem!important}.campo.dopo input{padding-left:11px!important;padding-right:34px!important}
.calc-in input:focus,.calc-in select:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 22%,transparent)}
.calc-2{display:grid;grid-template-columns:6.4em minmax(0,1fr);gap:10px}
.radio{display:flex;flex-wrap:wrap;gap:8px 18px}.radio label{display:flex;gap:8px;align-items:center;font-weight:600}.radio input{width:18px;height:18px;accent-color:var(--accent);margin:0}
.nota-calc{margin:0;font-size:.86rem;color:var(--ink-2);background:var(--amber-2);border-left:3px solid var(--amber);border-radius:6px;padding:8px 10px}
.calc-out{padding:18px 20px;background:var(--accent-2);display:grid;align-content:start;gap:12px;min-width:0}
.ris-main{background:var(--card);border:1px solid color-mix(in srgb,var(--accent) 35%,var(--line));border-radius:var(--r-s);padding:14px 16px}
.ris-main span{display:block;font-size:.9rem;color:var(--ink-2);font-weight:600}
.ris-main b{display:block;font-family:var(--serif);font-size:clamp(2rem,6vw,2.7rem);line-height:1.1;color:var(--accent);font-variant-numeric:tabular-nums;margin:2px 0}
.mini{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:0;padding:0;list-style:none}
.mini li{background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:9px 11px;min-width:0}
.mini b{display:block;font-family:var(--serif);font-size:1.18rem;line-height:1.2;font-variant-numeric:tabular-nums}
.mini span{display:block;font-size:.76rem;color:var(--ink-3);font-weight:700;line-height:1.3}
.formula{font-family:var(--mono);font-size:.86rem;background:var(--mute);border:1px solid var(--line);border-radius:var(--r-s);padding:10px 12px;margin:0;overflow-x:auto;white-space:pre-wrap;line-height:1.55}
.calc-out .formula{background:var(--card)}
.calc-out p{margin:0;font-size:.93rem;color:var(--ink-2)}
.graf{margin:20px 0 0;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:14px 16px 34px 12px;min-width:0}
.calc-out .graf{margin:0}
.graf-area{position:relative;height:190px;margin-left:66px}
.graf-area svg{display:block;width:100%;height:100%;overflow:visible}
.graf .gy{position:absolute;left:-68px;width:60px;text-align:right;transform:translateY(-50%);font-size:12px;line-height:1;color:var(--ink-3);font-variant-numeric:tabular-nums;white-space:nowrap}
.graf .gx{position:absolute;top:calc(100% + 8px);transform:translateX(-50%);font-size:12px;line-height:1;color:var(--ink-3);white-space:nowrap;font-variant-numeric:tabular-nums}
.graf .gx.first{transform:none}.graf .gx.last{transform:translateX(-100%)}
.graf figcaption{font-size:.85rem;color:var(--ink-3);margin:30px 0 0}
.graf .lin{fill:none;stroke:var(--accent);stroke-width:2.5;stroke-linejoin:round;vector-effect:non-scaling-stroke}
.graf .area{fill:var(--accent);opacity:.12}.graf .gr{stroke:var(--line);stroke-width:1;vector-effect:non-scaling-stroke}.graf .zero{stroke:var(--line-2);stroke-width:1.5;vector-effect:non-scaling-stroke}
.graf .bp{fill:var(--bar)}.graf .bn{fill:var(--neg)}.graf .bh{fill:var(--amber)}
.graf.alta .graf-area{height:240px}
.azioni{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.calc-f{margin:0;padding:14px 20px;border-top:1px solid var(--line);font-size:.86rem;color:var(--ink-3)}
.btn{display:inline-flex;align-items:center;gap:8px;font:inherit;font-size:.92rem;font-weight:800;background:var(--accent);color:var(--on-accent);border:0;border-radius:var(--r-s);padding:9px 15px;cursor:pointer;min-height:42px;text-decoration:none}
.btn:hover{background:var(--accent-h);color:var(--on-accent)}
.btn.sec{background:var(--card);color:var(--accent);border:1.5px solid color-mix(in srgb,var(--accent) 50%,transparent)}.btn.sec:hover{background:var(--accent-2);color:var(--accent-h)}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0;padding:0;overflow:hidden}
.stat{padding:16px 18px;border-right:1px solid var(--line);min-width:0}.stat:last-child{border-right:0}
.stat b{display:block;font-family:var(--serif);font-size:clamp(1.35rem,3.4vw,1.85rem);line-height:1.1;font-variant-numeric:tabular-nums}
.stat span{display:block;font-size:.84rem;color:var(--ink-3);line-height:1.35;margin-top:6px}.stat.main b{color:var(--accent)}
.nota{position:relative;background:var(--amber-2);border:1px solid color-mix(in srgb,var(--amber) 45%,transparent);padding:13px 16px 13px 46px;border-radius:var(--r-s);font-size:.95rem;margin:20px 0;color:var(--ink)}
.nota .ico{position:absolute;left:15px;top:15px;color:var(--amber-ink);width:20px;height:20px}.nota p{margin:0 0 6px}.nota p:last-child{margin:0}
.nota.info{background:var(--accent-2);border-color:color-mix(in srgb,var(--accent) 35%,transparent)}.nota.info .ico{color:var(--accent)}
.tab{border:1px solid var(--line);border-radius:var(--r);background:var(--card);box-shadow:var(--sh-1);overflow-x:auto;-webkit-overflow-scrolling:touch;margin:0 0 8px}
.tab.alta{max-height:620px;overflow-y:auto}
table.dati{border-collapse:collapse;width:100%;font-size:.92rem}
table.dati th,table.dati td{text-align:left;padding:8px 12px;border-bottom:1px solid var(--line);vertical-align:top}
table.dati td.n,table.dati th.n{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
table.dati thead th{background:var(--mute);font-size:.73rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-2);vertical-align:bottom;position:sticky;top:0}
table.dati tbody tr:last-child td{border-bottom:0}table.dati td a{font-weight:700}
table.dati tr.evid td{background:var(--amber-2);font-weight:700}
table.dati td.na{color:var(--ink-3)}
.cols{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px}
.faq{border-top:1px solid var(--line);padding:4px 0 6px}.faq h3{margin:16px 0 6px;font-size:1.08rem}.faq p{margin:0 0 6px;max-width:800px}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin:0;padding:0;list-style:none}
.griglia a{display:flex;flex-direction:column;gap:3px;height:100%;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:13px 15px;text-decoration:none;color:var(--ink);font-weight:800;box-shadow:var(--sh-1);transition:border-color .15s,transform .15s}
.griglia a:hover{border-color:var(--accent);transform:translateY(-1px)}.griglia a small{font-weight:600;color:var(--ink-3);font-size:.86rem;line-height:1.4}
.griglia a b{font-family:var(--serif);font-size:1.2rem;color:var(--accent)}
.anni{display:flex;flex-wrap:wrap;gap:6px;margin:0;padding:0;list-style:none}
.anni a{display:inline-block;min-width:3.6em;text-align:center;padding:6px 8px;border:1px solid var(--line);border-radius:8px;background:var(--card);text-decoration:none;font-weight:700;font-variant-numeric:tabular-nums}
.anni a:hover{border-color:var(--accent)}.anni a[aria-current]{background:var(--accent);color:var(--on-accent);border-color:var(--accent)}
.decade{margin:0 0 10px}.decade h3{margin:12px 0 6px;font-size:1rem;font-family:var(--sans)}
.vicini{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;margin:24px 0 0}
.fonti-box{margin-top:44px;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:var(--r-s);padding:16px 20px;font-size:.9rem;color:var(--ink-2)}
.fonti-box h2{display:flex;align-items:center;gap:8px;font-size:1.12rem;margin:0 0 8px;color:var(--ink)}.fonti-box h2 .ico{color:var(--accent)}
.fonti-box ol{margin:0 0 8px;padding-left:22px}.fonti-box li{margin-bottom:6px}.fonti-box a{overflow-wrap:anywhere}
.disclaimer{margin:28px 0 0;font-size:.88rem;color:var(--ink-2);background:var(--mute);border-radius:var(--r-s);padding:12px 16px}
.ad-slot{margin:24px 0}.ad-slot:empty{display:none}
footer{margin-top:60px;background:var(--deep);color:var(--on-deep-2);font-size:.88rem;padding:40px 0 34px}
footer a{color:var(--on-deep)}footer a:hover{color:var(--amber)}
footer .f-grid{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1fr) minmax(0,1fr);gap:28px}
footer .logo{margin-bottom:12px}footer p{margin:0 0 10px;max-width:640px}footer strong{color:var(--on-deep)}
footer ul{list-style:none;margin:0;padding:0;display:grid;gap:7px}
footer h2{font-family:var(--sans);font-size:.76rem;letter-spacing:.12em;text-transform:uppercase;color:var(--amber);margin:4px 0 12px}
footer .f-base{border-top:1px solid rgba(255,255,255,.12);margin-top:24px;padding-top:16px;font-size:.82rem;max-width:none}
@media (max-width:920px){.calc-g{grid-template-columns:1fr}.calc-in{border-right:0;border-bottom:1px solid var(--line)}.stats{grid-template-columns:repeat(2,minmax(0,1fr))}
.stat:nth-child(2){border-right:0}.stat:nth-child(-n+2){border-bottom:1px solid var(--line)}.cols{grid-template-columns:1fr}footer .f-grid{grid-template-columns:1fr 1fr}footer .f-grid>div:first-child{grid-column:1/-1}}
@media (max-width:820px){nav.menu{display:none}.nav-m{display:block}header.top .wrap{min-height:58px}.band-in{padding-top:20px}}
@media (max-width:560px){.card,.calc-in,.calc-out{padding:16px}.calc-h{padding:14px 16px}.calc-f{padding:12px 16px}.mini{grid-template-columns:1fr 1fr}.mini li:last-child{grid-column:1/-1}
table.dati{font-size:.86rem}table.dati th,table.dati td{padding:7px 8px}.logo{font-size:1.02rem;gap:8px}.logo img{width:28px;height:28px}
.griglia{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.griglia a{padding:11px 12px}.stat{padding:13px}footer .f-grid{grid-template-columns:1fr}.anni a{min-width:3.3em;padding:5px 6px}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
@media print{header.top,footer,.nav-m,.tema,.azioni,.ad-slot{display:none!important}.band{background:none;color:#000}.band h1,.sub{color:#000}}
"""

ICONE = {
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "moon": '<path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6 6 6M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4"/>',
    "check": '<circle cx="12" cy="12" r="9.5"/><path d="M8 12.5l2.8 2.8L16.5 9.5"/>',
    "info": '<circle cx="12" cy="12" r="9.5"/><path d="M12 11v6M12 7.5h.01"/>',
    "alert": '<path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17h.01"/>',
    "doc": '<path d="M14 2.5H6.5A2 2 0 0 0 4.5 4.5v15a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V8z"/><path d="M14 2.5V8h5.5M8 13h8M8 17h5"/>',
    "calc": '<rect x="4.5" y="2.5" width="15" height="19" rx="2.5"/><path d="M8 6.5h8M8 11h.01M12 11h.01M16 11h.01M8 14.5h.01M12 14.5h.01M16 14.5h.01M8 18h.01M12 18h4"/>',
    "shield": '<path d="M12 22s8-3.5 8-10V5.5L12 2.5 4 5.5V12c0 6.5 8 10 8 10z"/><path d="M8.5 12l2.5 2.5 4.5-4.5"/>',
    "lock": '<rect x="4.5" y="10.5" width="15" height="11" rx="2.5"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/>',
    "trend": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "calendar": '<rect x="3" y="4.5" width="18" height="17" rx="2.5"/><path d="M16 2.5v4M8 2.5v4M3 10h18"/>',
    "coins": '<ellipse cx="9" cy="7" rx="5.5" ry="2.5"/><path d="M3.5 7v4c0 1.4 2.5 2.5 5.5 2.5s5.5-1.1 5.5-2.5V7"/><path d="M9.5 16.3c.9.6 2.4 1 4 1 3 0 5.5-1.1 5.5-2.5v-4c0-1.2-1.8-2.2-4.3-2.4"/>',
    "link": '<path d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1 1"/><path d="M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1-1"/>',
    "globe": '<circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19M12 2.5c2.6 2.8 3.9 6 3.9 9.5s-1.3 6.7-3.9 9.5c-2.6-2.8-3.9-6-3.9-9.5s1.3-6.7 3.9-9.5z"/>',
}

# Marchio: tessera blu notte con moneta e linea che sale (ambra)
MARCHIO = ('<rect width="40" height="40" rx="10" fill="#161A33"/>'
           '<circle cx="15" cy="23" r="8.5" fill="none" stroke="#8EA2FF" stroke-width="2.4"/>'
           '<path d="M15 18.5v9M12.6 20.6c0-1.2 1-2 2.4-2s2.4.7 2.4 1.8c0 2.6-4.8 1.6-4.8 4.1 0 1.1 1 1.9 2.4 1.9s2.4-.8 2.4-2" fill="none" stroke="#8EA2FF" stroke-width="1.6" stroke-linecap="round"/>'
           '<path d="M21 15l5-5 3 3 5-5" fill="none" stroke="#E8930C" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
           '<path d="M30 8h4v4" fill="none" stroke="#E8930C" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')
FAVICON_SVG = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">{MARCHIO}</svg>\n'

TEMA_JS = "(function(){try{var t=localStorage.getItem('ic-theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();"

# ---------------------------------------------------------------- motore (copia di motore.py)
MOTORE_JS = r"""
var DM_PER_EURO=1.95583,ANNO_EURO=2002;
function indice(c,anno,mese){var i;
  if(mese){i=(anno-c.m0[0])*12+(mese-c.m0[1]);return (i>=0&&i<c.m.length)?c.m[i]:null;}
  i=anno-c.a0;return (i>=0&&i<c.a.length)?c.a[i]:null;}
function fattoreValuta(daAnno,aAnno,inDm){var daDm=inDm&&daAnno<ANNO_EURO,aDm=aAnno<ANNO_EURO;
  if(daDm&&!aDm)return 1/DM_PER_EURO;if(!daDm&&aDm)return DM_PER_EURO;return 1.0;}
function calcola(c,importo,da,a,valuta){
  var i0=indice(c,da[0],da[1]),i1=indice(c,a[0],a[1]);
  if(!i0||!i1||importo===null||importo===undefined||!(importo>=0))return null;
  var f=(valuta===null||valuta===undefined)?1.0:fattoreValuta(da[0],a[0],valuta);
  var t0=da[0]+(da[1]?(da[1]-0.5)/12:0.5),t1=a[0]+(a[1]?(a[1]-0.5)/12:0.5),anni=t1-t0,r=i1/i0;
  var media=Math.abs(anni)>=1?Math.pow(r,1/anni)-1:null;
  return {valore:importo*r*f,i0:i0,i1:i1,rapporto:r,cumulata:r-1,media:media,anni:anni,fattore_valuta:f};}
"""

# ---------------------------------------------------------------- interfaccia
APP_JS = MOTORE_JS + r"""
(function(){
  var b=document.querySelector('[data-tema]');
  if(b)b.addEventListener('click',function(){var r=document.documentElement,c=r.getAttribute('data-theme');
    if(!c)c=window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
    var n=c==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('ic-theme',n);}catch(e){}});
  var box=document.querySelector('[data-calc]');if(!box)return;
  var D=JSON.parse(document.getElementById('calc-dati').textContent),T=D.t,f=box.querySelector('form'),out=box.querySelector('[data-out]'),nota=box.querySelector('[data-nota]');
  var fissa=D.fisso||null;
  function fmt(x,val){var cur=val||D.valuta;try{return new Intl.NumberFormat(D.locale,{style:'currency',currency:cur,minimumFractionDigits:2,maximumFractionDigits:2}).format(x).replace('DEM','DM');}catch(e){return cur+' '+x.toFixed(2);}}
  function num(x,d){return new Intl.NumberFormat(D.locale,{minimumFractionDigits:d,maximumFractionDigits:d}).format(x);}
  var DE=D.locale.indexOf('de')===0;
  function pc(x,d){d=d===undefined?1:d;var z=parseFloat(Math.abs(x*100).toFixed(d))===0;return (z?'':(x>=0?'+':'\u2212'))+num(Math.abs(x*100),d)+(DE?'\u00a0%':'%');}
  function dec(x){var s=String(x),i=s.indexOf('.');return i<0?1:Math.max(1,Math.min(3,s.length-i-1));}
  function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function parseImporto(v){v=String(v||'').trim().toLowerCase().replace(/[\s$£€]/g,'').replace(/^(usd|gbp|eur|dm)|(usd|gbp|eur|dm)$/g,'');var m=1;
    if(/k$/.test(v)){m=1e3;v=v.slice(0,-1);}else if(/(m|mio|mn|million)$/.test(v)){m=1e6;v=v.replace(/(m|mio|mn|million)$/,'');}
    if(DE){if(/,\d{1,2}$/.test(v)||(/\./.test(v)&&!/\.\d{1,2}$/.test(v)))v=v.replace(/\./g,'').replace(',','.');else v=v.replace(/,/g,'');}
    else{v=v.replace(/,/g,'');}
    var x=parseFloat(v);return isFinite(x)&&x>=0?x*m:null;}
  function serie(){var s=f.elements.s?f.elements.s.value:D.serie_def;return D.serie[s];}
  function nomeMese(m){return T.mesi[m-1];}
  function etichetta(y,m){return m?nomeMese(m)+' '+y:String(y)+(T.media_suffix?' '+T.media_suffix:'');}
  function aggiornaMesi(sel,ySel,c){var y=parseInt(ySel.value,10),cur=sel.value,ok=[];
    for(var i=0;i<sel.options.length;i++){var o=sel.options[i],m=o.value?parseInt(o.value,10):0,v=indice(c,y,m||undefined);
      var x=c.x&&m?c.x[y+'-'+(m<10?'0':'')+m]:null;o.disabled=!v;o.title=x||'';if(v)ok.push(o.value);}
    if(ok.indexOf(cur)<0){sel.value=ok.indexOf('')>=0?'':(ok.length?ok[ok.length-1]:'');}}
  function legge(){var c=serie(),fy=parseInt(f.elements.fy.value,10),ty=parseInt(f.elements.ty.value,10);
    var fm=f.elements.fm.value?parseInt(f.elements.fm.value,10):0,tm=f.elements.tm.value?parseInt(f.elements.tm.value,10):0;
    var val=null;if(D.dm){val=fy<ANNO_EURO?(f.elements.c&&f.elements.c.value==='eur'?false:true):false;}
    return {c:c,a:parseImporto(f.elements.a.value),da:[fy,fm||undefined],aa:[ty,tm||undefined],val:val};}
  var autoDa=null;
  function controllaSerie(ev){if(!f.elements.s)return;var mn=Math.min(parseInt(f.elements.fy.value,10),parseInt(f.elements.ty.value,10));
    if(ev&&ev.target===f.elements.s)autoDa=null;
    var s=f.elements.s.value,c=D.serie[s],alt=D.serie_alt[s];
    if(mn<c.a0&&alt){f.elements.s.value=alt;autoDa=s;}
    else if(autoDa&&mn>=D.serie[autoDa].a0){f.elements.s.value=autoDa;autoDa=null;}
    nota.hidden=!autoDa;if(autoDa)nota.textContent=T.cambio_serie;}
  function avvisoSerie(){if(!D.avviso)return;var mn=Math.min(parseInt(f.elements.fy.value,10),parseInt(f.elements.ty.value,10));
    nota.hidden=!(mn<D.avviso.prima);if(!nota.hidden)nota.textContent=D.avviso.testo;}
  function tacche(mn,mx){var span=(mx-mn)||Math.abs(mx)||1,bs=[1,2,2.5,5,10],p,a,b;
    for(var i=0;i<bs.length;i++){p=bs[i]*Math.pow(10,Math.floor(Math.log10(span/4)));a=Math.floor(mn/p+1e-9)*p;b=Math.ceil(mx/p-1e-9)*p;if((b-a)/p<=5.0001)break;}
    var n=Math.round((b-a)/p),o=[];for(var j=0;j<=n;j++)o.push(a+p*j);return o;}
  function grafico(c,ris,st){var pts=[],y0=st.da[0],y1=st.aa[0];if(y1-y0<2)return '';
    for(var y=y0;y<=y1;y++){var i=y===y0?ris.i0:(y===y1?ris.i1:indice(c,y));
      if(i)pts.push([y,st.a*i/ris.i0*ris.fattore_valuta]);}
    if(pts.length<3)return '';var mx=0,mn=0;pts.forEach(function(p){mx=Math.max(mx,p[1]);mn=Math.min(mn,p[1]);});var tk=tacche(mn,mx);mn=tk[0];mx=tk[tk.length-1];
    var vOut=D.dm?(y1<ANNO_EURO?'DEM':'EUR'):D.valuta;
    var sx=function(x){return (x-y0)/(y1-y0)*1000;},sy=function(v){return (1-(v-mn)/((mx-mn)||1))*300;};
    var d=pts.map(function(p,i){return (i?'L':'M')+sx(p[0]).toFixed(1)+' '+sy(p[1]).toFixed(1);}).join(' ');
    var g='<figure class="graf" role="img" aria-label="'+esc(T.grafico_aria)+'"><div class="graf-area"><svg viewBox="0 0 1000 300" preserveAspectRatio="none" aria-hidden="true">',lab='';
    for(var k=0;k<tk.length;k++){var v=tk[k],yy=sy(v);g+='<line class="gr" x1="0" x2="1000" y1="'+yy.toFixed(1)+'" y2="'+yy.toFixed(1)+'"/>';
      lab+='<span class="gy" style="top:'+(yy/3).toFixed(1)+'%">'+esc(fmt(v,vOut).replace(/[.,]\d\d(?=\D*$)/,''))+'</span>';}
    g+='<path class="area" d="'+d+' L1000 300 L0 300 Z"/><path class="lin" d="'+d+'"/></svg>'+lab;
    g+='<span class="gx first" style="left:0">'+y0+'</span><span class="gx last" style="left:100%">'+y1+'</span></div></figure>';return g;}
  function calcolaUi(ev){controllaSerie(ev);avvisoSerie();var c=serie();aggiornaMesi(f.elements.fm,f.elements.fy,c);aggiornaMesi(f.elements.tm,f.elements.ty,c);
    var st=legge();if(D.dm){var vb=box.querySelector('[data-valuta]');if(vb)vb.hidden=!(st.da[0]<ANNO_EURO);}
    var sym=box.querySelector('[data-sym]');if(sym&&D.dm)sym.setAttribute('data-sym',st.val?'DM':'€');
    if(st.a===null){out.innerHTML='<p>'+esc(T.importo_errato)+'</p>';return;}
    var r=calcola(st.c,st.a,st.da,st.aa,st.val);if(!r){out.innerHTML='<p>'+esc(T.manca)+'</p>';return;}
    var vIn=D.dm?(st.val?'DEM':'EUR'):D.valuta,vOut=D.dm?(st.aa[0]<ANNO_EURO?'DEM':'EUR'):D.valuta;
    var daE=etichetta(st.da[0],st.da[1]),aE=etichetta(st.aa[0],st.aa[1]);
    var h='<div class="ris-main"><span>'+esc(T.vale.replace('{importo}',fmt(st.a,vIn)).replace('{da}',daE))+'</span><b data-valore>'+esc(fmt(r.valore,vOut))+'</b><span>'+esc(T.in_.replace('{a}',aE))+'</span></div>';
    h+='<ul class="mini"><li><b>'+esc(pc(r.cumulata))+'</b><span>'+esc(r.cumulata>=0?T.cumulata:T.cumulata_neg)+'</span></li>';
    h+='<li><b>'+(r.media===null?'–':esc(pc(r.media,2)))+'</b><span>'+esc(T.media)+'</span></li>';
    h+='<li><b>'+esc(num(r.i0,dec(r.i0))+' → '+num(r.i1,dec(r.i1)))+'</b><span>'+esc(st.c.nome)+'</span></li></ul>';
    var fstr=num(st.a,2)+' × '+num(r.i1,dec(r.i1))+' ÷ '+num(r.i0,dec(r.i0));
    if(r.fattore_valuta!==1)fstr+=(r.fattore_valuta<1?' \u00f7 ':' \u00d7 ')+num(DM_PER_EURO,5);
    h+='<p class="formula">'+esc(fstr+' = '+num(r.valore,2))+'</p>';
    var inv=calcola(st.c,st.a,st.aa,st.da,D.dm?(st.aa[0]<ANNO_EURO):null);
    if(inv)h+='<p>'+esc(T.inverso.replace('{importo}',fmt(st.a,vOut)).replace('{a}',aE).replace('{valore}',fmt(inv.valore,vIn)).replace('{da}',daE))+'</p>';
    h+=grafico(st.c,r,st);
    h+='<div class="azioni"><button type="button" class="btn sec" data-copia>'+esc(T.copia)+'</button><span class="small" data-copiato hidden>'+esc(T.copiato)+'</span></div>';
    out.innerHTML=h;}
  function link(){var st=legge(),p=new URLSearchParams();p.set('a',f.elements.a.value.trim());p.set('f',st.da[0]+(st.da[1]?'-'+st.da[1]:''));p.set('t',st.aa[0]+(st.aa[1]?'-'+st.aa[1]:''));
    if(f.elements.s)p.set('s',f.elements.s.value);if(D.dm&&f.elements.c)p.set('c',f.elements.c.value);return location.origin+location.pathname+'?'+p.toString()+'#calc';}
  out.addEventListener('click',function(e){var t=e.target.closest('[data-copia]');if(!t)return;var u=link(),ok=out.querySelector('[data-copiato]');
    function fatto(){if(ok)ok.hidden=false;}
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(u).then(fatto,function(){window.prompt(T.copia,u);});}else{window.prompt(T.copia,u);}});
  try{var q=new URLSearchParams(location.search);
    if(q.get('a'))f.elements.a.value=q.get('a').slice(0,30);
    if(q.get('s')&&f.elements.s&&D.serie[q.get('s')])f.elements.s.value=q.get('s');
    [['f','fy','fm'],['t','ty','tm']].forEach(function(k){var v=q.get(k[0]);if(!v)return;var m=/^(\d{4})(?:-(\d{1,2}))?$/.exec(v);if(!m)return;
      if(f.elements[k[1]].querySelector('option[value="'+m[1]+'"]')){f.elements[k[1]].value=m[1];f.elements[k[2]].value=m[2]?String(parseInt(m[2],10)):'';}});
    if(q.get('c')&&f.elements.c){var rr=f.querySelector('input[name=c][value="'+(q.get('c')==='eur'?'eur':'dm')+'"]');if(rr)rr.checked=true;}}catch(e){}
  f.addEventListener('input',calcolaUi);f.addEventListener('change',calcolaUi);f.addEventListener('submit',function(e){e.preventDefault();calcolaUi();});
  calcolaUi();
})();
"""

# ---------------------------------------------------------------- calcolatore Roth IRA (copia di pensione.roth_limite)
# Metodo: IRS Publication 590-A, Worksheet 2-2. Tutto in centesimi interi: rapporto esatto (il foglio chiede «almeno tre decimali»),
# limite ridotto arrotondato per eccesso ai 10 $, minimo 200 $ se è sopra zero, poi il minore tra riga 8 e riga 10.
ROTH_MOTORE_JS = r"""
function rothLimite(y,stato,magiC,over50,compC,altreC){
  var L=(y.ira+(over50?y.cu:0))*100,base=(compC===null||compC===undefined)?L:Math.min(L,compC),lo,hi,W;
  if(stato==='mfj'){lo=y.mfj[0];hi=y.mfj[1];W=10000;}else if(stato==='mfs'){lo=y.mfs[0];hi=y.mfs[1];W=10000;}else{lo=y.single[0];hi=y.single[1];W=15000;}
  var l10=Math.max(0,base-(altreC||0)),esito,l8,num=null,den=null;
  if(magiC<=lo*100){esito='full';l8=base;}
  else if(magiC>=hi*100){esito='none';l8=0;}
  else{var Wc=W*100,d=magiC-lo*100;num=base*(Wc-d);den=Wc;l8=Math.ceil(num/(den*1000))*1000;if(l8>0&&l8<20000)l8=20000;esito='partial';}
  var lim=esito==='none'?0:Math.min(l8,l10);
  return {esito:esito,limite:lim,lo:lo,hi:hi,W:W,L:L,base:base,l8:l8,l10:l10};}
"""

ROTH_JS = ROTH_MOTORE_JS + r"""
(function(){
  var f=document.querySelector('[data-roth]');if(!f)return;
  var D=JSON.parse(document.getElementById('roth-dati').textContent),out=document.querySelector('[data-roth-out]');
  function usd(c){return '$'+(c/100).toLocaleString('en-US',{minimumFractionDigits:c%100?2:0,maximumFractionDigits:2});}
  function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function cent(v){v=String(v||'').trim().replace(/[\s$,]/g,'');if(v==='')return null;var m=1;if(/k$/i.test(v)){m=1000;v=v.slice(0,-1);}
    if(!/^\d+(\.\d{0,2})?$/.test(v))return NaN;return Math.round(parseFloat(v)*m*100);}
  function calcola(){
    var anno=f.elements.y.value,y=D.anni[anno],stato=f.elements.s.value,magi=cent(f.elements.m.value),comp=cent(f.elements.c.value),altre=cent(f.elements.o.value),o50=f.elements.e.checked;
    if(magi===null||isNaN(magi)){out.innerHTML='<p class="ris-msg">'+esc(D.t.magi)+'</p>';return;}
    if(isNaN(comp)||isNaN(altre)){out.innerHTML='<p class="ris-msg">'+esc(D.t.importo)+'</p>';return;}
    var r=rothLimite(y,stato,magi,o50,comp,altre===null?0:altre),nome=D.stati[stato];
    var tit=r.esito==='full'?(r.limite<r.L?D.t.full_meno:D.t.full):(r.esito==='partial'?D.t.partial:D.t.none);
    var h='<div class="ris-main roth-'+r.esito+'"><span>'+esc(tit.replace('{anno}',anno))+'</span><b data-roth-limite>'+esc(usd(r.limite))+'</b><span>'+esc((altre?D.t.sotto_altre:D.t.sotto).replace('{anno}',anno))+'</span></div>';
    h+='<ul class="mini due"><li><b>'+esc(usd(r.lo*100))+' – '+esc(usd(r.hi*100))+'</b><span>'+esc(D.t.fascia.replace('{anno}',anno))+'</span></li>';
    h+='<li><b>'+esc(usd(r.L))+'</b><span>'+esc(o50?D.t.max50:D.t.max)+'</span></li></ul>';
    var righe=[['1',D.t.r1,usd(magi)],['2',D.t.r2,usd(r.lo*100)],['4',D.t.r4,usd(r.W*100)],['6',D.t.r6,usd(r.base)]];
    if(r.esito==='partial'){var rap=(magi-r.lo*100)/(r.W*100);righe.splice(2,0,['3',D.t.r3,usd(magi-r.lo*100)]);righe.push(['5',D.t.r5,rap.toFixed(4)]);righe.push(['8',D.t.r8,usd(r.l8)]);}
    righe.push(['10',D.t.r10,usd(r.l10)]);
    h+='<details class="foglio"><summary>'+esc(D.t.foglio)+'</summary><table class="dati"><tbody>'+righe.map(function(x){return '<tr><td>'+x[0]+'</td><td>'+esc(x[1])+'</td><td class="n">'+esc(x[2])+'</td></tr>';}).join('')+'</tbody></table></details>';
    h+='<p class="small">'+esc(nome)+'. '+esc(D.t.nota)+'</p>';
    out.innerHTML=h;}
  try{var q=new URLSearchParams(location.search);
    if(q.get('y')&&D.anni[q.get('y')])f.elements.y.value=q.get('y');
    if(q.get('s')&&D.stati[q.get('s')])f.elements.s.value=q.get('s');
    if(q.get('m'))f.elements.m.value=q.get('m').slice(0,14);}catch(e){}
  f.addEventListener('input',calcola);f.addEventListener('change',calcola);f.addEventListener('submit',function(e){e.preventDefault();calcola();});
  calcola();
})();
"""

CSS += """
.calc-in .spunta{display:flex;gap:10px;align-items:center;font-weight:600}.calc-in .spunta input{width:20px;height:20px;accent-color:var(--accent);margin:0;flex:none}
.calc-in .opz{font-weight:600;color:var(--ink-3);font-size:.84rem}
.ris-main.roth-none b{color:var(--bad)}.ris-main.roth-partial b{color:var(--amber-ink)}
.ris-msg{background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:12px 14px}
.foglio{background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:10px 12px}.foglio summary{cursor:pointer;font-weight:700;color:var(--accent)}
.foglio table.dati{margin-top:8px;font-size:.86rem}
.citaz{border-left:3px solid var(--line-2);margin:0 0 12px;padding:4px 0 4px 14px;color:var(--ink-2);font-size:.92rem;max-width:860px}
.citaz cite{display:block;font-style:normal;font-size:.82rem;color:var(--ink-3);margin-top:4px}
details.irs{margin:16px 0}details.irs>summary{cursor:pointer;font-weight:700;color:var(--accent);margin-bottom:10px}
table.dati td.vuoto{color:var(--ink-3)}
table.dati.sintesi td.n{white-space:normal}
.pull+.stats{margin-top:20px}table.dati td.src{white-space:nowrap}.mini.due{grid-template-columns:repeat(2,minmax(0,1fr))}.mini.due li:last-child{grid-column:auto}
@media (max-width:560px){table.dati.sintesi td:first-child{min-width:10.5em}}
"""
