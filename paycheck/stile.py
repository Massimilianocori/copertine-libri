"""Aspetto e codice del browser di US Paycheck Calculator: CSS (caratteri di sistema, nessun file esterno), icone, marchio,
JS (tema chiaro/scuro, calcolatore della busta paga e del costo per il datore di lavoro). Le funzioni JS `busta` e `datore`
fanno gli stessi conti di motore.py in centesimi interi: verifica.py le confronta con un calcolo indipendente."""

CSS = """
:root{--bg:#F5F6F2;--card:#FFFFFF;--ink:#15211C;--ink-2:#3A4A43;--ink-3:#586860;--line:#DCE2DB;--line-2:#C1CCC3;
--deep:#0E2A22;--deep-2:#17402F;--on-deep:#EDF5F0;--on-deep-2:#B7CDC1;--accent:#0F6B4A;--accent-h:#0A5038;--accent-2:#E3F2EA;--on-accent:#fff;
--brass:#C99A2E;--brass-ink:#85610F;--brass-2:#FBF3DC;--warn:#8A4B00;--warn-2:#FFF4E0;--mute:#ECF0EB;--ok:#1E7A4C;--bad:#B3261E;
--sh-1:0 1px 2px rgba(14,42,34,.06);--sh-2:0 18px 40px -24px rgba(14,42,34,.45),0 2px 6px rgba(14,42,34,.06);--r:14px;--r-s:10px;
--sans:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;--serif:Charter,"Bitstream Charter","Iowan Old Style","Palatino Linotype",Georgia,serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0A1410;--card:#111E18;--ink:#E4EEE8;--ink-2:#BACBC1;--ink-3:#93A69B;--line:#20322A;--line-2:#31493D;--deep:#06100C;--deep-2:#0D2219;--on-deep:#E4EEE8;--on-deep-2:#A3B8AC;--accent:#6FD3A0;--accent-h:#A5E6C5;--accent-2:#12291F;--on-accent:#06100C;--brass:#E3BC62;--brass-ink:#E3BC62;--brass-2:#2A2312;--warn:#F2C177;--warn-2:#2A200F;--mute:#14231C;--ok:#6FD3A0;--bad:#FF8A80;--sh-1:0 1px 2px rgba(0,0,0,.5);--sh-2:0 18px 40px -24px rgba(0,0,0,.9)}}
:root[data-theme="dark"]{--bg:#0A1410;--card:#111E18;--ink:#E4EEE8;--ink-2:#BACBC1;--ink-3:#93A69B;--line:#20322A;--line-2:#31493D;--deep:#06100C;--deep-2:#0D2219;--on-deep:#E4EEE8;--on-deep-2:#A3B8AC;--accent:#6FD3A0;--accent-h:#A5E6C5;--accent-2:#12291F;--on-accent:#06100C;--brass:#E3BC62;--brass-ink:#E3BC62;--brass-2:#2A2312;--warn:#F2C177;--warn-2:#2A200F;--mute:#14231C;--ok:#6FD3A0;--bad:#FF8A80;--sh-1:0 1px 2px rgba(0,0,0,.5);--sh-2:0 18px 40px -24px rgba(0,0,0,.9)}
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
.nav-m nav{position:absolute;left:16px;right:16px;top:calc(100% + 4px);background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-2);padding:8px;display:grid;grid-template-columns:repeat(4,1fr);gap:2px;max-height:calc(100vh - 80px);overflow:auto}
.nav-m nav a{padding:10px 8px;border-radius:8px;color:var(--ink);text-decoration:none;font-weight:700;font-size:.93rem;text-align:center}.nav-m nav a:hover{background:var(--accent-2)}
.nav-m nav a.w2{grid-column:span 2}.nav-m nav .sep{grid-column:1/-1;border-top:1px solid var(--line);margin:4px 0}
.band{background:linear-gradient(180deg,var(--deep) 0,var(--deep-2) 100%);color:var(--on-deep);position:relative;overflow:hidden}
.band::after{content:"";position:absolute;right:-60px;top:-40px;width:360px;height:360px;border-radius:50%;border:44px solid rgba(201,154,46,.14)}
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
.tab{border:1px solid var(--line);border-radius:var(--r);background:var(--card);box-shadow:var(--sh-1);overflow-x:auto;-webkit-overflow-scrolling:touch;margin:0 0 8px;max-width:100%;container-type:inline-size}
table.dati{border-collapse:separate;border-spacing:0;width:100%;font-size:.9rem}
table.dati caption{text-align:left;padding:12px 14px;font-size:.88rem;color:var(--ink-2);border-bottom:1px solid var(--line)}
@supports (width:100cqw){table.dati caption>span{display:block;position:sticky;left:14px;width:calc(100cqw - 28px)}}
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
.calc-in input{font:inherit;font-weight:600;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:9px 11px;width:100%;min-height:46px}
.calc-in input:focus,.cerca input:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 22%,transparent)}
.due{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.tot .main:first-child:nth-last-child(3){grid-column:1/-1}.calc-out small{color:var(--ink-3)}
.giorni{width:100%;border-collapse:collapse;font-size:.86rem;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);font-variant-numeric:tabular-nums}
.giorni th,.giorni td{padding:5px 8px;border-bottom:1px solid var(--line);text-align:right}.giorni th:first-child,.giorni td:first-child{text-align:left}
.giorni thead th{font-size:.72rem;text-transform:uppercase;letter-spacing:.04em;color:var(--ink-2);background:var(--mute)}
.giorni-box{max-height:320px;overflow:auto;border-radius:var(--r-s)}
.cerca{display:grid;gap:8px;max-width:640px}.cerca label{font-weight:700;font-size:.92rem}
.cerca input{font:inherit;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:10px 12px;width:100%;min-height:46px}
.cerca .small{margin:0}
.risultati{list-style:none;margin:10px 0 0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:8px;max-width:100%}
.risultati a{display:flex;flex-direction:column;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:9px 12px;text-decoration:none;color:var(--ink);box-shadow:var(--sh-1)}
.risultati a:hover{border-color:var(--accent)}.risultati b{color:var(--accent)}.risultati small{color:var(--ink-3);font-size:.8rem}
.griglia.stati{grid-template-columns:repeat(auto-fill,minmax(170px,1fr))}
@media (max-width:860px){nav.menu{display:none}.nav-m{display:block}.calc-g{grid-template-columns:1fr}.calc-in{border-right:0;border-bottom:1px solid var(--line)}
.stats{grid-template-columns:1fr 1fr}.stat:nth-child(2){border-right:0}.stat:nth-child(-n+2){border-bottom:1px solid var(--line)}.f-grid{grid-template-columns:1fr}}
@media (max-width:1000px) and (min-width:861px){nav.menu a{padding:7px 7px;font-size:.88rem}}
@media (max-width:420px){.due{grid-template-columns:1fr}body{font-size:16px}.logo span{font-size:1rem}.stat{padding:13px 13px}table.dati{font-size:.86rem}table.dati th,table.dati td{padding:7px 8px}}
.calc-in fieldset{border:0;margin:0;padding:0;display:grid;gap:12px;min-width:0}.calc-in legend{font-family:var(--serif);font-weight:700;font-size:1.02rem;padding:0;margin:0 0 8px}
.calc-in .check{display:flex;gap:10px;align-items:flex-start;font-weight:600}.calc-in .check input{width:20px;height:20px;min-height:0;margin-top:2px;flex:none;accent-color:var(--accent)}
.calc-in details{border:1px solid var(--line);border-radius:var(--r-s);padding:0 12px;background:var(--bg)}.calc-in details[open]{padding-bottom:12px}
.calc-in summary{cursor:pointer;font-weight:700;font-size:.92rem;padding:11px 0;color:var(--accent)}.calc-in details>div{display:grid;gap:12px}
.calc-in label small{font-weight:400;color:var(--ink-3);font-size:.82rem;line-height:1.35}
.calc-in hr{border:0;border-top:1px solid var(--line);margin:2px 0;width:100%}
.righe{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);font-size:.95rem;font-variant-numeric:tabular-nums}
.righe th,.righe td{padding:8px 11px;border-bottom:1px solid var(--line);text-align:left;font-weight:400}.righe td{text-align:right;white-space:nowrap}
.righe tr:last-child th,.righe tr:last-child td{border-bottom:0}.righe tr.netto th,.righe tr.netto td{font-weight:800;background:var(--mute)}
.righe small{display:block;color:var(--ink-3);font-size:.8rem}
.netto-box{background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:12px 14px}
.netto-box span{display:block;font-size:.8rem;color:var(--ink-3);font-weight:700}.netto-box b{display:block;font-family:var(--serif);font-size:clamp(2rem,6vw,2.6rem);line-height:1.1;color:var(--accent);font-variant-numeric:tabular-nums}
.netto-box em{font-style:normal;font-size:.88rem;color:var(--ink-2)}
blockquote.cit{margin:14px 0;padding:12px 16px;border-left:4px solid var(--brass);background:var(--card);border-radius:0 var(--r-s) var(--r-s) 0;max-width:800px;box-shadow:var(--sh-1)}
blockquote.cit p{margin:0 0 6px;font-family:var(--serif);font-size:1.02rem}blockquote.cit cite{font-style:normal;font-size:.85rem;color:var(--ink-3)}
.partner{border:1.5px solid color-mix(in srgb,var(--brass) 60%,transparent);background:var(--brass-2);border-radius:var(--r);padding:16px 18px;margin:26px 0;max-width:800px}
.partner .tag{font-size:.72rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--brass-ink);margin:0 0 6px}.partner h3{margin:0 0 6px}
.passi li b{font-variant-numeric:tabular-nums}
.griglia.stati a b{font-size:1.05rem}
ol.steps{padding-left:22px}ol.steps li{margin-bottom:8px;max-width:800px}
@media (max-width:420px){.righe{font-size:.9rem}.righe th,.righe td{padding:7px 8px}}
"""

ICONE = {
    'moon': '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
    'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>',
    'calc': '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 11h2M12 11h2M16 11h0M8 15h2M12 15h2M8 18h2M12 18h4"/>',
    'table': '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M3 14h18M9 4v16"/>',
    'doc': '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
    'info': '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/>',
    'alert': '<path d="M12 3l9.5 17h-19z"/><path d="M12 10v4M12 17.5v.5"/>',
    'shield': '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    'lock': '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    'cash': '<rect x="3" y="6" width="18" height="12" rx="2"/><circle cx="12" cy="12" r="2.6"/><path d="M6.5 9.5v.1M17.5 14.4v.1"/>',
    'build': '<path d="M4 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16M16 9h2a2 2 0 0 1 2 2v10M3 21h18M8 7h4M8 11h4M8 15h4"/>',
    'map': '<path d="M12 21s7-6.2 7-11a7 7 0 0 0-14 0c0 4.800 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>',
}

MARCHIO = ('<rect width="40" height="40" rx="9" fill="#0E2A22"/>'
           '<path d="M10 11h20v18l-3.3-2.2L23.3 29 20 26.8 16.7 29l-3.4-2.200L10 29z" fill="none" stroke="#E3BC62" stroke-width="2.6" stroke-linejoin="round"/>'
           '<path d="M15 17h10M15 21.500h6" fill="none" stroke="#6FD3A0" stroke-width="2.6" stroke-linecap="round"/>')
FAVICON_SVG = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">{MARCHIO}</svg>\n'

TEMA_JS = "(function(){try{var t=localStorage.getItem('pc-theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();"

from pathlib import Path  # noqa: E402

APP_JS = (Path(__file__).resolve().parent / "app.js").read_text(encoding="utf-8")
