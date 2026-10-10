"""Genera il sito statico EsamiDiStato in esamidistato/sito/ a partire da esamidistato/dati/.

Uso (dalla radice del repository):
    python3 esamidistato/genera.py

Dati: professioni.json e sessioni.json (curati a mano, con fonte), sedi.json (da raccolta/raccogli.py),
citta.json (pagine città). Nessuna dipendenza esterna. Stesso motore di esameb1/genera.py.
TODO (fase 2): percentuali di abilitati per ateneo, calcolate dagli elenchi pubblici degli atenei.
"""
import json
import shutil
from datetime import date
from html import escape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
URL_SITO = "https://esamidistato.netlify.app"  # cambiare qui se il nome del sito su Netlify è diverso
NOME = "EsamiDiStato"
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console, proprietà https://esamidistato.netlify.app — non rimuovere
OGGI = date.today()

MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
        "settembre", "ottobre", "novembre", "dicembre"]
GIORNI = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
MUR_PAGINA = "https://www.mur.gov.it/it/aree-tematiche/universita/professioni/esami-di-stato"
ENTI = {"MUR": "Ministero dell'Università e della Ricerca", "MIM": "Ministero dell'Istruzione e del Merito",
        "Giustizia": "Ministero della Giustizia"}

professioni = json.loads((DATI / "professioni.json").read_text())
sessioni = json.loads((DATI / "sessioni.json").read_text())
sedi = json.loads((DATI / "sedi.json").read_text())
citta = json.loads((DATI / "citta.json").read_text())
PROF = {p["slug"]: p for p in professioni}


def d(iso):
    return date.fromisoformat(iso)


def data_breve(iso):
    x = d(iso)
    return f"{'1°' if x.day == 1 else x.day} {MESI[x.month - 1]} {x.year}"


def il(iso):
    """Articolo davanti alla data: "il 21 ottobre", "l'11 novembre"."""
    return "l'" if d(iso).day in (8, 11) else "il "


def future(lista):
    return [s for s in lista if d(s["data"]) >= OGGI]


def verificato_ultimo():
    date_v = [s["verificato_il"] for s in sessioni] + [s["verificato_il"] for s in sedi]
    return data_breve(max(date_v))


def sedi_di(slug):
    return [s for s in sedi if slug in s["professioni"]]


def nome_sede(s):
    return s["ateneo"]


# ---------------------------------------------------------------- pezzi comuni
CSS = """
:root{--bg:#F6F7F9;--card:#FFFFFF;--ink:#13233A;--ink-2:#3F4E62;--ink-3:#66748A;--line:#DFE3EA;
--accent:#1F4E8C;--accent-2:#E7EEF8;--warn:#9A4A00;--warn-2:#FFF1E2;--mute:#ECEFF4;--radius:14px}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0E141C;--card:#151E29;--ink:#EEF2F7;
--ink-2:#B9C4D2;--ink-3:#8C99AA;--line:#253244;--accent:#7FB0F0;--accent-2:#16263B;--warn:#FFB367;--warn-2:#33240F;--mute:#1C2735}}
:root[data-theme="dark"]{--bg:#0E141C;--card:#151E29;--ink:#EEF2F7;--ink-2:#B9C4D2;--ink-3:#8C99AA;--line:#253244;
--accent:#7FB0F0;--accent-2:#16263B;--warn:#FFB367;--warn-2:#33240F;--mute:#1C2735}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;
font-size:17px;line-height:1.6}
a{color:var(--accent)}
.wrap{max-width:1000px;margin:0 auto;padding:0 16px}
header.top{border-bottom:1px solid var(--line);background:var(--card)}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:58px}
.logo{font-weight:800;font-size:1.15rem;color:var(--ink);text-decoration:none;letter-spacing:-.01em}
.logo span{color:var(--accent)}
nav.menu{display:flex;gap:14px;flex-wrap:wrap;font-size:.95rem}
nav.menu a{color:var(--ink-2);text-decoration:none}
nav.menu a:hover{color:var(--accent)}
.hero{padding:34px 0 10px}
h1{font-size:clamp(1.6rem,4.6vw,2.35rem);line-height:1.18;letter-spacing:-.02em;margin:0 0 12px}
h2{font-size:1.35rem;margin:36px 0 12px;letter-spacing:-.01em}
h3{font-size:1.08rem;margin:20px 0 8px}
.lead{font-size:1.08rem;color:var(--ink-2);max-width:740px;margin:0 0 6px}
.small{font-size:.9rem;color:var(--ink-3)}
.avviso{background:var(--warn-2);color:var(--ink);border-left:4px solid var(--warn);padding:12px 14px;border-radius:8px;font-size:.95rem;margin:16px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px}
.info dl{margin:0;display:grid;grid-template-columns:170px 1fr;gap:8px 16px}
.info dt{font-weight:700;color:var(--ink-2)}
.info dd{margin:0;min-width:0;overflow-wrap:anywhere}
.filtri{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:6px 0 14px}
.filtri select{font:inherit;padding:8px 10px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink);max-width:100%}
.sessioni{display:grid;gap:10px}
.sess{display:grid;grid-template-columns:150px 1fr;gap:4px 16px;background:var(--card);border:1px solid var(--line);
border-radius:var(--radius);padding:14px 16px}
.sess .quando{font-weight:700}
.sess .quando small{display:block;font-weight:400;color:var(--ink-3);font-size:.85rem}
.sess .cosa{min-width:0}
.badge{display:inline-block;font-size:.78rem;font-weight:700;letter-spacing:.02em;padding:2px 8px;border-radius:6px;
background:var(--mute);color:var(--ink-2);margin:0 6px 4px 0;vertical-align:1px;text-decoration:none}
a.badge:hover{color:var(--accent)}
.badge.ente{background:var(--accent-2);color:var(--accent)}
.scad{margin-top:4px;font-size:.93rem;color:var(--ink-2)}
.scad strong{color:var(--ink)}
.scad.urgente strong{color:var(--warn)}
.scad.chiusa{color:var(--ink-3)}
.fonte{font-size:.8rem;color:var(--ink-3)}
.fonte a{color:var(--ink-3)}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}
.griglia a{display:block;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px;
text-decoration:none;color:var(--ink);font-weight:600;overflow-wrap:anywhere}
.griglia a small{display:block;font-weight:400;color:var(--ink-3)}
.griglia a:hover{border-color:var(--accent)}
.sedi{list-style:none;padding:0;margin:0;display:grid;gap:8px}
.sedi li{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px}
.sedi .nome{font-weight:650;overflow-wrap:anywhere}
.sedi li,.sess{min-width:0;overflow-wrap:anywhere}
.sedi .det{font-size:.92rem;color:var(--ink-2)}
details{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin:8px 0}
details summary{cursor:pointer;font-weight:650}
details .sedi li{border-color:var(--line);background:var(--bg)}
.form{display:grid;gap:12px}
.form label{display:grid;gap:4px;font-weight:600;font-size:.95rem}
.form input,.form select{font:inherit;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink);width:100%;min-width:0}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:400;font-size:.9rem;color:var(--ink-2)}
.form .check input{width:18px;height:18px;padding:0;margin-top:4px;flex:none;accent-color:var(--accent)}
.btn{font:inherit;font-weight:700;background:var(--accent);color:var(--bg);border:0;border-radius:10px;padding:12px 18px;cursor:pointer}
.btn:disabled{opacity:.6;cursor:wait}
.hp{position:absolute;left:-9999px}
.ok{background:var(--accent-2);border:1px solid var(--accent);padding:14px;border-radius:10px}
.errore{color:var(--warn);font-weight:600}
.due{display:grid;grid-template-columns:1.45fr 1fr;gap:22px;align-items:start}
.due>*{min-width:0}
footer{margin-top:50px;border-top:1px solid var(--line);padding:22px 0 40px;font-size:.88rem;color:var(--ink-3)}
footer a{color:var(--ink-3)}
table.conf{width:100%;border-collapse:collapse;font-size:.95rem}
table.conf th,table.conf td{border-bottom:1px solid var(--line);padding:8px 6px;text-align:left;vertical-align:top}
.tab-wrap{overflow-x:auto}
.scadenza-top{background:var(--card);border:1px solid var(--accent);border-radius:var(--radius);padding:14px 16px;margin:14px 0}
.scadenza-top strong{color:var(--accent)}
@media (max-width:760px){.due{grid-template-columns:1fr}.sess{grid-template-columns:1fr}.info dl{grid-template-columns:1fr;gap:2px}
.info dd{margin-bottom:8px}header.top .wrap{flex-direction:column;align-items:flex-start;gap:4px;padding-top:10px;padding-bottom:10px}nav.menu{gap:14px;font-size:.92rem}}
.cta{display:inline-block;margin-top:10px;text-decoration:none}
"""

JS = """
(function(){
  var oggi=new Date();oggi.setHours(0,0,0,0);
  function giorni(iso){var p=iso.split('-');var x=new Date(+p[0],+p[1]-1,+p[2]);return Math.round((x-oggi)/86400000);}
  document.querySelectorAll('.sess').forEach(function(el){
    if(giorni(el.dataset.data)<0){el.remove();return;}
    var sc=el.querySelector('.scad[data-scadenza]');
    if(!sc)return;
    var g=giorni(sc.dataset.scadenza);var t=sc.querySelector('.stato');
    var ap=sc.dataset.apertura?giorni(sc.dataset.apertura):-1;
    sc.classList.remove('urgente','chiusa');
    if(g<0){sc.classList.add('chiusa');t.textContent=' — domande chiuse';}
    else if(ap>0){t.textContent=' — le domande si aprono tra '+ap+(ap===1?' giorno':' giorni');}
    else if(g===0){sc.classList.add('urgente');t.textContent=' — scade oggi';}
    else if(g<=15){sc.classList.add('urgente');t.textContent=' — mancano '+g+(g===1?' giorno':' giorni');}
    else{t.textContent=' — mancano '+g+' giorni';}
  });
  document.querySelectorAll('.sessioni').forEach(function(box){
    var v=box.parentNode.querySelector('[data-vuoto]');
    if(v&&!box.querySelector('.sess'))v.hidden=false;
  });
  var filtro=document.getElementById('filtro-prof');
  if(filtro)filtro.addEventListener('change',function(){
    var f=filtro.value;
    document.querySelectorAll('.sess').forEach(function(el){
      el.hidden=!(f===''||(' '+el.dataset.prof+' ').indexOf(' '+f+' ')>=0);
    });
  });
  var src=document.querySelectorAll('input[name=source]');
  var v='';try{var q=new URLSearchParams(location.search);v=q.get('ref')||q.get('utm_source')||document.referrer||'diretto';}catch(e){v='diretto';}
  src.forEach(function(i){i.value=String(v).slice(0,200);});
  document.querySelectorAll('form.avvisami').forEach(function(form){
    form.addEventListener('submit',function(ev){
      ev.preventDefault();
      var err=form.querySelector('[data-errore]');err.hidden=true;
      if(!form.checkValidity()){form.reportValidity();return;}
      var b=form.querySelector('button');b.disabled=true;
      fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},
        body:new URLSearchParams(new FormData(form)).toString()})
      .then(function(r){if(!r.ok)throw new Error(r.status);
        form.hidden=true;form.parentNode.querySelector('[data-ok]').hidden=false;})
      .catch(function(){err.hidden=false;b.disabled=false;});
    });
  });
})();
"""


def pagina(percorso, titolo, descrizione, corpo, jsonld=None, base=None):
    """Scrive sito/<percorso> con la struttura comune. base: prefisso dei link (\"/\" per la 404)."""
    profondita = percorso.count("/")
    rel = base if base is not None else ("../" * profondita or "./")
    avvisami = "#avvisami" if 'id="avvisami"' in corpo else f"{rel}#avvisami"
    canonico = URL_SITO + "/" + (percorso[:-10] if percorso.endswith("index.html") else percorso)
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    verifica = f'<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">\n' if GOOGLE_VERIFICA else ""
    testo = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titolo)}</title>
<meta name="description" content="{escape(descrizione)}">
<link rel="canonical" href="{canonico}">
<meta property="og:title" content="{escape(titolo)}">
<meta property="og:description" content="{escape(descrizione)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{URL_SITO}/og.png">
<meta property="og:url" content="{canonico}">
<meta name="theme-color" content="#1F4E8C">
{verifica}<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%231F4E8C'/%3E%3Ctext x='32' y='42' font-family='Arial' font-weight='700' font-size='24' text-anchor='middle' fill='white'%3EES%3C/text%3E%3C/svg%3E">
<style>{CSS}</style>
{ld}
</head>
<body>
<header class="top"><div class="wrap">
<a class="logo" href="{rel}">EsamiDi<span>Stato</span></a>
<nav class="menu" aria-label="Menu">
<a href="{rel}#date">Date</a><a href="{rel}#professioni">Professioni</a><a href="{rel}#citta">Città</a><a href="{rel}come-funziona/">Come funziona</a><a href="{avvisami}">Avvisami</a>
</nav>
</div></header>
<main class="wrap">
{corpo}
</main>
<footer><div class="wrap">
<p><strong>{NOME}</strong> è un sito indipendente: non è affiliato al Ministero dell'Università e della Ricerca, al Ministero dell'Istruzione e del Merito,
al Ministero della Giustizia, alle università né agli Ordini professionali. I nomi delle università e degli enti appartengono ai rispettivi titolari.
Le informazioni vengono dalle fonti ufficiali indicate accanto a ogni dato. <strong>Prima di fare la domanda leggi sempre il bando della tua sede.</strong>
Questo sito non dà consulenza: per i casi particolari chiedi alla segreteria esami di Stato della tua università o al tuo Ordine.</p>
<p>Dati controllati il {verificato_ultimo()}. · <a href="{rel}privacy.html">Privacy</a> · <a href="{rel}come-funziona/">Come funziona</a></p>
</div></footer>
<script>{JS}</script>
</body>
</html>
"""
    dest = SITO / percorso
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo)


def link_prof(slug, rel):
    return f'<a class="badge" href="{rel}professione/{slug}/">{escape(PROF[slug]["nome"])}</a>'


def scheda_sessione(s, rel, solo=None):
    """solo: slug della professione della pagina (mostra solo quella nei badge)."""
    profs = [solo] if solo else s["professioni"]
    badge = "".join(link_prof(p, rel) for p in profs)
    ente = PROF[s["professioni"][0]]["ente"]
    apertura = f' data-apertura="{s["apertura"]}"' if s.get("apertura") else ""
    dal = f'Domande dal <strong>{data_breve(s["apertura"])}</strong> ' if s.get("apertura") else "Domande "
    scad = (f'<div class="scad" data-scadenza="{s["scadenza"]}"{apertura}>{dal}entro {il(s["scadenza"])}<strong>{data_breve(s["scadenza"])}</strong>'
            f'<span class="stato"></span><br><span class="small">{escape(s["nota_scadenza"])}</span></div>')
    nota = f'<div class="small">{escape(s["nota_data"])}</div>' if s.get("nota_data") else ""
    fonte = PROF[solo]["fonte"] if solo and ente == "MIM" else s["fonte"]
    termine = (f' · termine: <a href="{escape(s["fonte_scadenza"])}" rel="noopener">nota dell\'Ufficio scolastico regionale</a>'
               if s.get("fonte_scadenza") else "")
    return f"""<article class="sess" data-data="{s['data']}" data-prof="{' '.join(s['professioni'])}">
<div class="quando">{data_breve(s['data'])}<small>{GIORNI[d(s['data']).weekday()]} · inizio esame</small></div>
<div class="cosa"><span class="badge ente">{escape(s['sessione'])}</span>{badge}
<div><strong>{escape(s['chi'])}</strong></div>
{nota}
{scad}
<div class="fonte">Fonte: <a href="{escape(fonte)}" rel="noopener">atto ufficiale ({escape(ENTI[ente])})</a>, {escape(s['articolo'])}{termine} · controllato il {data_breve(s['verificato_il'])}</div>
</div>
</article>"""


def lista_sessioni(lista, rel, con_filtri=False, solo=None):
    filtri = ""
    if con_filtri:
        opz = "".join(f'<option value="{p["slug"]}">{escape(p["nome"])}</option>'
                      for p in sorted(professioni, key=lambda p: p["nome"]))
        filtri = (f'<div class="filtri"><label for="filtro-prof" class="small">Mostra solo:</label>'
                  f'<select id="filtro-prof"><option value="">Tutte le professioni</option>{opz}</select></div>')
    vuoto = ('<p data-vuoto hidden>Nessuna data futura pubblicata al momento. Le date 2027 escono di solito in primavera con le nuove '
             'ordinanze: controlliamo le fonti ufficiali ogni settimana. <a href="#avvisami">Avvisami</a>.</p>')
    return (filtri + '<div class="sessioni">' + "\n".join(scheda_sessione(s, rel, solo) for s in lista) + "</div>" + vuoto)


def modulo(rel, prof_scelta="", citta_scelta=""):
    opz_c = "".join(
        f'<option value="{escape(c["nome"])}"{" selected" if c["nome"] == citta_scelta else ""}>{escape(c["nome"])}</option>'
        for c in sorted(citta, key=lambda c: c["nome"]))
    opz_p = "".join(
        f'<option value="{escape(p["slug"])}"{" selected" if p["slug"] == prof_scelta else ""}>{escape(p["nome"])}</option>'
        for p in sorted(professioni, key=lambda p: p["nome"]))
    return f"""<section class="card" id="avvisami">
<h2 style="margin-top:0">Avvisami su date e scadenze</h2>
<p class="small" style="margin-top:-4px">Gratis. Ti scriviamo quando escono le nuove date della tua professione o quando una scadenza sta per chiudere.</p>
<form class="form avvisami" name="avvisami" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="avvisami">
<input type="hidden" name="source" value="">
<p class="hp"><label>Non compilare <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>La tua email<input type="email" name="email" required autocomplete="email" placeholder="nome@esempio.it"></label>
<label>Professione
<select name="professione" required><option value="">Scegli la professione</option>{opz_p}</select></label>
<label>Città dove vuoi fare l'esame
<select name="citta" required><option value="">Scegli la città</option>{opz_c}<option value="Altra città">Altra città</option></select></label>
<label class="check"><input type="checkbox" name="consenso" value="si" required>
<span>Accetto di ricevere email da {NOME} sulle date degli esami di Stato. Posso cancellarmi quando voglio. Ho letto la <a href="{rel}privacy.html">privacy</a>.</span></label>
<button class="btn" type="submit">Avvisami</button>
<p class="errore" data-errore hidden>Non è stato possibile inviare. Riprova tra poco.</p>
</form>
<div class="ok" data-ok hidden><strong>Fatto!</strong> Ti scriveremo quando ci sono novità per la tua professione.</div>
</section>"""


def scheda_sede(s, rel, prof=None, con_prof=True):
    righe = [escape(f'{s["citta"]} ({s["sigla"]}) · {s["regione"]}')]
    if prof and s["note"].get(prof):
        righe.append(escape(s["note"][prof]))
    if con_prof:
        righe.append("Esami di Stato per: " + " ".join(link_prof(p, rel) for p in s["professioni"]))
    link = []
    if s.get("url_esami_stato"):
        link.append(f'<a href="{escape(s["url_esami_stato"])}" rel="noopener">pagina esami di Stato</a>')
    if s.get("sito"):
        link.append(f'<a href="{escape(s["sito"])}" rel="noopener">sito ufficiale</a>')
    fonti = " · ".join(f'<a href="{escape(f)}" rel="noopener">{"decreto" if "giustizia" in f else "ordinanza"}</a>'
                       for f in s["fonti"])
    return f"""<li><div class="nome">{escape(nome_sede(s))}</div>
<div class="det">{"<br>".join(righe)}</div>
{f'<div class="det">{" · ".join(link)}</div>' if link else ""}
<div class="fonte">Fonte: {fonti} · controllato il {data_breve(s['verificato_il'])}</div></li>"""


def jsonld_sessioni(lista):
    eventi = []
    for s in lista[:20]:
        nomi = ", ".join(PROF[p]["nome"] for p in s["professioni"])
        ente = PROF[s["professioni"][0]]["ente"]
        eventi.append({
            "@type": "EducationEvent", "name": f"Esame di Stato {nomi} – {s['sessione']}", "startDate": s["data"], "endDate": s["data"], "image": URL_SITO + "/og.png",
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled",
            "location": {"@type": "Place", "name": "Sedi d'esame in Italia",
                         "address": {"@type": "PostalAddress", "addressCountry": "IT"}},
            "organizer": {"@type": "Organization", "name": ENTI[ente]},
            "performer": {"@type": "Organization", "name": ENTI[ente]},
            "offers": {"@type": "Offer", "url": s["fonte"] if isinstance(s.get("fonte"), str) else URL_SITO + "/", "availability": "https://schema.org/InStock", "validFrom": s["verificato_il"]},
            "description": f"{s['chi']}. Domande entro {il(s['scadenza'])}{data_breve(s['scadenza'])}.",
        })
    return {"@context": "https://schema.org", "@graph": eventi}


def prossima_scadenza(prossime):
    aperte = sorted((s for s in prossime if d(s["scadenza"]) >= OGGI), key=lambda s: s["scadenza"])
    return aperte[0] if aperte else None


def griglia_prof(rel):
    return "".join(
        f'<a href="{rel}professione/{p["slug"]}/">{escape(p["nome"])}<small>'
        f'{f"{len(sedi_di(p["slug"]))} sedi" if sedi_di(p["slug"]) else "istituti tecnici"}</small></a>'
        for p in sorted(professioni, key=lambda p: p["nome"]))


def griglia_citta(rel):
    return "".join(
        f'<a href="{rel}citta/{c["slug"]}/">{escape(c["nome"])}<small>{sum(1 for s in sedi if s["citta"] == c["comune"])} sedi</small></a>'
        for c in sorted(citta, key=lambda c: c["nome"]))


# ---------------------------------------------------------------- pagine
def home(prossime):
    ps = prossima_scadenza(prossime)
    box = ""
    if ps:
        stesse = [s for s in prossime if s["scadenza"] == ps["scadenza"]]
        nomi = sorted({p for s in stesse for p in s["professioni"]}, key=lambda p: PROF[p]["nome"])
        box = (f'<div class="scadenza-top">Prossima scadenza: <strong>{data_breve(ps["scadenza"])}</strong> — domande per la '
               f'{escape(ps["sessione"].lower())} ({len(nomi)} professioni: {", ".join(escape(PROF[p]["nome"]) for p in nomi[:6])}'
               f'{"…" if len(nomi) > 6 else ""}). <a href="#date">Vedi le date</a></div>')
    n_atenei = len({s["ateneo"].split(" - Campus")[0] for s in sedi if s["tipo"] == "ateneo"})
    corpo = f"""<section class="hero">
<h1>Esami di Stato 2026: date, scadenze e sedi per ogni professione</h1>
<p class="lead">Ingegnere, architetto, psicologo, commercialista, biologo, farmacista, avvocato e altre professioni:
in un solo posto <strong>le date d'esame, l'ultimo giorno per fare la domanda e le università dove si può sostenere</strong>,
prese dalle ordinanze ufficiali.</p>
<p class="small">{len(professioni)} professioni · {n_atenei} università e {sum(1 for s in sedi if s["tipo"] == "corte_appello")} Corti di appello sede d'esame · {len(prossime)} date in programma</p>
{box}
<a class="btn cta" href="#avvisami">Avvisami per la mia professione</a>
</section>
<div class="avviso">Le date valgono in tutta Italia. Ogni università pubblica poi un bando con le sue regole (domanda online, contributo, calendario delle prove).
<strong>Prima di fare la domanda leggi sempre il bando della tua sede.</strong></div>
<div class="due">
<section id="date">
<h2>Prossime date degli esami di Stato</h2>
{lista_sessioni(prossime, "", con_filtri=True)}
<p class="small">Le date 2027 non sono ancora uscite (controllato il {data_breve(max(s["verificato_il"] for s in sessioni))}): di solito le ordinanze escono in primavera.</p>
</section>
<aside>
{modulo("")}
<section id="professioni">
<h2>Professioni</h2>
<div class="griglia">{griglia_prof("")}</div>
</section>
<section id="citta">
<h2>Sedi per città</h2>
<div class="griglia">{griglia_citta("")}</div>
<p class="small">La tua città non c'è? Ogni pagina professione ha l'elenco completo delle sedi, regione per regione.</p>
</section>
</aside>
</div>
<section>
<h2>Domande frequenti</h2>
<details><summary>Dove faccio la domanda?</summary>
<p>Per le professioni delle ordinanze del Ministero dell'Università (ingegnere, architetto, psicologo, commercialista, farmacista…) la domanda si consegna
alla segreteria dell'università dove vuoi fare l'esame, entro la data indicata. Puoi scegliere una sola sede. Per geometra, perito agrario e agrotecnico
la domanda passa dal Collegio; per avvocato si fa solo online sul sito del Ministero della Giustizia. Tutti i dettagli nella <a href="come-funziona/">pagina Come funziona</a>.</p></details>
<details><summary>Quanto costa?</summary>
<p>Per le professioni universitarie c'è una tassa di 49,58 € più il contributo deciso da ogni ateneo (lo trovi nel bando). Per avvocato il totale è 90,91 €.
Fonti: <a href="{escape(PROF["ingegnere"]["fonte"])}" rel="noopener">OM 694/2026, art. 3</a>, <a href="{escape(PROF["avvocato"]["fonte"])}" rel="noopener">decreto 3/9/2026, art. 3</a>.</p></details>
<details><summary>Ho fatto domanda per la prima sessione ma non mi sono presentato: cosa faccio?</summary>
<p>Puoi presentarti alla seconda sessione facendo una nuova domanda entro il 21 ottobre 2026, usando i documenti già consegnati (art. 3 delle ordinanze MUR 2026).</p></details>
<details><summary>E il medico?</summary>
<p>La professione di medico non compare nelle ordinanze MUR 2026 sugli esami di Stato, quindi non ha date in queste sessioni.</p></details>
</section>"""
    pagina("index.html", "Esami di Stato 2026: date, scadenze e sedi per professione | EsamiDiStato",
           "Date degli esami di Stato 2026 (seconda sessione dal 16 novembre), scadenze delle domande e università sede d'esame "
           "per ingegnere, architetto, psicologo, commercialista, farmacista, avvocato e altre professioni.", corpo, jsonld_sessioni(prossime))


def pagina_professione(p, prossime):
    slug = p["slug"]
    sue = sedi_di(slug)
    rel = "../../"
    date_p = [s for s in sessioni if slug in s["professioni"]]
    date_p.sort(key=lambda s: s["data"])
    regioni = sorted({s["regione"] for s in sue})
    if sue:
        tipo = "Corti di appello" if slug == "avvocato" else "università"
        fonte_elenco = ("Elenco dell'art. 1 del decreto" if slug == "avvocato"
                        else "Elenco della tabella allegata all'ordinanza")
        blocchi = "".join(
            f'<details{" open" if len(regioni) <= 3 else ""}><summary>{escape(r)} ({sum(1 for s in sue if s["regione"] == r)})</summary>'
            f'<ul class="sedi">{"".join(scheda_sede(s, rel, slug, con_prof=False) for s in sue if s["regione"] == r)}</ul></details>'
            for r in regioni)
        sedi_html = (f'<h2 id="sedi">Dove si fa l\'esame: {len(sue)} {tipo}</h2>'
                     f'<p class="small">{fonte_elenco}, con la città indicata lì. Apri la regione per vedere le sedi.</p>{blocchi}')
    else:
        sedi_html = (f'<h2 id="sedi">Dove si fa l\'esame</h2><p>{escape(p["nota"])} L\'elenco degli istituti disponibili è nella Tabella A '
                     f'dell\'<a href="{escape(p["fonte"])}" rel="noopener">ordinanza</a>.</p>')
    righe = [("Come è organizzato", p["sezioni"]), ("Come fare la domanda", p["domanda"]), ("Quanto costa", p["costo"])]
    if p["sede_tedesco"]:
        righe.append(("Esame in tedesco", f"Per i cittadini UE residenti in Italia che vogliono l'esame in lingua tedesca: sede di {p['sede_tedesco']}."))
    if p["nota"] and sue:
        righe.append(("Da sapere", p["nota"]))
    righe.append(("Atto ufficiale", None))
    dl = "".join(
        f"<dt>{escape(k)}</dt><dd>{escape(v) if v is not None else f'<a href=\"{escape(p['fonte'])}\" rel=\"noopener\">{escape(p['atto'])}</a> · <a href=\"{escape(p['pagina_fonte'])}\" rel=\"noopener\">pagina ufficiale</a>'}</dd>"
        for k, v in righe)
    future_p = [s for s in date_p if d(s["data"]) >= OGGI]
    gia = [s for s in date_p if d(s["data"]) < OGGI]
    passate = (f'<p class="small">Già svolta: {escape(gia[0]["sessione"].lower())}, iniziata il '
               f'{" e il ".join(data_breve(s["data"]) for s in gia)}.</p>' if gia else "")
    prima = future_p[0] if future_p else None
    sottotitolo = (f"Prossimo esame: <strong>{data_breve(prima['data'])}</strong>, domande entro {il(prima['scadenza'])}<strong>{data_breve(prima['scadenza'])}</strong>."
                   if prima else "Le date del prossimo anno non sono ancora uscite.")
    titolo_h1 = f"Esame di Stato {p['nome'].lower() if slug != 'commercialista' else 'commercialista ed esperto contabile'} 2026: date, scadenze e sedi"
    corpo = f"""<section class="hero">
<h1>{escape(titolo_h1)}</h1>
<p class="lead">{escape(p['nome_completo'])}. {sottotitolo}
{f"L'esame si può fare in {len(sue)} sedi in Italia." if sue else ""}</p>
<a class="btn cta" href="#avvisami">Avvisami per {escape(p['nome'].lower())}</a>
</section>
<div class="avviso">Ogni sede pubblica un bando con le sue regole e il calendario delle prove. <strong>Leggi il bando della tua sede prima di fare la domanda.</strong></div>
<div class="due">
<section>
<h2 id="date">Date {escape(p['nome'].lower())} 2026</h2>
{lista_sessioni(future_p, rel, solo=slug)}
{passate}
<p class="small">Date 2027: non ancora pubblicate (controllato il {data_breve(p['verificato_il'])}).</p>
<section class="card info"><h2 style="margin-top:0">In breve</h2><dl>{dl}</dl></section>
{sedi_html}
</section>
<aside>
{modulo(rel, prof_scelta=slug)}
<section><h2>Altre professioni</h2><p class="small">{" · ".join(f'<a href="../{x["slug"]}/">{escape(x["nome"])}</a>' for x in sorted(professioni, key=lambda x: x["nome"]) if x != p)}</p></section>
</aside>
</div>"""
    n = f" e {len(sue)} sedi" if sue else ""
    pagina(f"professione/{slug}/index.html",
           f"Esame di Stato {p['nome'].lower()} 2026: date, scadenze{n} | EsamiDiStato",
           f"Esame di Stato {p['nome'].lower()} 2026: date d'inizio, ultimo giorno per la domanda"
           f"{f', le {len(sue)} sedi in Italia' if sue else ''}, costi e fonti ufficiali.",
           corpo, jsonld_sessioni([s for s in prossime if slug in s["professioni"]]))


def pagina_citta(c, prossime):
    qui = [s for s in sedi if s["citta"] == c["comune"]]
    regione = qui[0]["regione"]
    rel = "../../"
    prof_qui = {p for s in qui for p in s["professioni"]}
    atenei = [s for s in qui if s["tipo"] == "ateneo"]
    corti = [s for s in qui if s["tipo"] == "corte_appello"]
    blocchi = f'<ul class="sedi">{"".join(scheda_sede(s, rel) for s in atenei + corti)}</ul>'
    mancano = [p for p in sorted(professioni, key=lambda p: p["nome"]) if p["slug"] not in prof_qui and sedi_di(p["slug"])]
    righe_m = []
    for p in mancano:
        vicine = [s for s in sedi_di(p["slug"]) if s["regione"] == regione]
        dove = ", ".join(f'{escape(s["ateneo"])} ({escape(s["citta"])})' for s in vicine) or "nessuna sede nella regione"
        righe_m.append(f'<li><a href="../../professione/{p["slug"]}/">{escape(p["nome"])}</a>: {dove}</li>')
    nota_mancano = ""
    nota_avv = (" Per avvocato la Corte di appello giusta dipende dal distretto del tuo Consiglio dell'ordine: leggi il bando."
                if any(p["slug"] == "avvocato" for p in mancano) else "")
    if righe_m:
        nota_mancano = (f'<h2>Professioni senza sede a {escape(c["nome"])}</h2>'
                        f'<p class="small">Sedi nella stessa regione ({escape(regione)}).{nota_avv}</p><ul>{"".join(righe_m)}</ul>')
    date_c = [s for s in prossime if any(p in prof_qui for p in s["professioni"])]
    tabella = "".join(
        f'<tr><td><a href="../../professione/{p}/">{escape(PROF[p]["nome"])}</a></td><td>'
        f'{"<br>".join(escape(s["ateneo"]) for s in qui if p in s["professioni"])}</td></tr>'
        for p in sorted(prof_qui, key=lambda x: PROF[x]["nome"]))
    altre = " · ".join(f'<a href="../{x["slug"]}/">{escape(x["nome"])}</a>' for x in sorted(citta, key=lambda x: x["nome"]) if x != c)
    corpo = f"""<section class="hero">
<h1>Esami di Stato a {escape(c['nome'])} 2026: sedi, date e scadenze</h1>
<p class="lead">A {escape(c['nome'])} si può sostenere l'esame di Stato per <strong>{len(prof_qui)} professioni</strong>
in {len(atenei)} {"università" if len(atenei) != 1 else "università"}{f" e alla Corte di appello (avvocato)" if corti else ""}.
Le date sono le stesse in tutta Italia; la domanda va fatta alla sede scelta.</p>
<a class="btn cta" href="#avvisami">Avvisami per {escape(c['nome'])}</a>
</section>
<div class="avviso">Ogni sede pubblica un bando con regole e calendario delle prove: <strong>leggilo prima di fare la domanda.</strong></div>
<div class="due">
<section>
<h2>Quale professione, dove</h2>
<div class="tab-wrap"><table class="conf"><thead><tr><th>Professione</th><th>Sede a {escape(c['nome'])}</th></tr></thead><tbody>{tabella}</tbody></table></div>
<h2>Sedi d'esame a {escape(c['nome'])}</h2>
{blocchi}
{nota_mancano}
<h2 id="date">Prossime date (valide anche a {escape(c['nome'])})</h2>
{lista_sessioni(date_c, rel)}
</section>
<aside>
{modulo(rel, citta_scelta=c['nome'])}
<section><h2>Altre città</h2><p class="small">{altre}</p></section>
</aside>
</div>"""
    pagina(f"citta/{c['slug']}/index.html",
           f"Esami di Stato {c['nome']} 2026: sedi, date e scadenze | EsamiDiStato",
           f"Dove fare l'esame di Stato a {c['nome']}: {len(qui)} sedi per {len(prof_qui)} professioni, "
           "date della seconda sessione 2026 e scadenze delle domande.", corpo)


def come_funziona():
    righe = "".join(
        f"<tr><td><a href='../professione/{p['slug']}/'>{escape(p['nome'])}</a></td><td>{escape(ENTI[p['ente']])}</td>"
        f"<td>{len(sedi_di(p['slug'])) or 'istituti tecnici'}</td><td><a href='{escape(p['fonte'])}' rel='noopener'>{escape(p['atto'].split(' (')[0])}</a></td></tr>"
        for p in sorted(professioni, key=lambda p: (p["ente"], p["nome"])))
    om = {n: PROF[s]["fonte"] for n, s in (("694", "ingegnere"), ("693", "farmacista"), ("692", "commercialista"))}
    corpo = f"""<section class="hero">
<h1>Esame di Stato: come funziona, passo per passo</h1>
<p class="lead">Spiegato in modo semplice: chi decide le date, dove si fa la domanda, quanto costa. Ogni regola ha accanto la fonte.</p>
</section>
<h2>Chi decide le date</h2>
<p>Per quasi tutte le professioni le date le fissa ogni anno il Ministero dell'Università e della Ricerca con tre ordinanze
(<a href="{escape(om['694'])}" rel="noopener">OM 694</a>, <a href="{escape(om['693'])}" rel="noopener">OM 693</a> e
<a href="{escape(om['692'])}" rel="noopener">OM 692</a> del 27 maggio 2026; elenco sulla <a href="{MUR_PAGINA}" rel="noopener">pagina del MUR</a>).
Nel 2026 ci sono due sessioni: luglio e novembre. Le date sono le stesse in tutte le sedi.</p>
<p>Fanno eccezione geometra, perito agrario e agrotecnico (ordinanze del Ministero dell'Istruzione e del Merito, una sessione l'anno)
e avvocato (bando del Ministero della Giustizia, una sessione l'anno).</p>
<h2>Come si fa la domanda (professioni universitarie)</h2>
<ol>
<li>Scegli <strong>una sola sede</strong> tra quelle dell'elenco della tua professione (art. 2 delle ordinanze).</li>
<li>Leggi il bando dell'università: ti dice come fare la domanda (di solito online), il contributo e il calendario delle prove.</li>
<li>Consegna la domanda entro la data dell'ordinanza: per la seconda sessione 2026 <strong>entro il 21 ottobre 2026</strong> (art. 3).</li>
<li>Paga la tassa di ammissione di 49,58 € e il contributo dell'ateneo (art. 3).</li>
<li>Presentati alla prima prova: nel 2026 la seconda sessione inizia il 16 novembre (laurea magistrale) o il 20 novembre (laurea triennale, titoli «iunior»).</li>
</ol>
<p>Se hai fatto domanda per la prima sessione ma eri assente, puoi rifare domanda per la seconda entro il 21 ottobre 2026 usando i documenti già consegnati (art. 3).</p>
<h2>Esame in lingua tedesca</h2>
<p>I cittadini dell'Unione europea residenti in Italia che vogliono sostenere l'esame in tedesco devono fare domanda in una sede precisa (art. 5 delle ordinanze):
la trovi nella pagina di ogni professione.</p>
<h2>Tutte le professioni</h2>
<div class="tab-wrap"><table class="conf"><thead><tr><th>Professione</th><th>Chi fissa le date</th><th>Sedi</th><th>Atto</th></tr></thead>
<tbody>{righe}</tbody></table></div>
<h2>Professioni che qui non trovi</h2>
<p><strong>Medico</strong>: non compare nelle ordinanze MUR 2026 sugli esami di Stato. <strong>Perito industriale</strong>: non abbiamo trovato l'ordinanza 2026; la aggiungeremo quando la troviamo nelle fonti ufficiali.</p>
{modulo("../")}"""
    pagina("come-funziona/index.html", "Esame di Stato: come funziona, domanda, costi e sedi | EsamiDiStato",
           "Come funziona l'esame di Stato di abilitazione: chi fissa le date, dove e quando fare la domanda, quanto costa, "
           "con le fonti ufficiali per ogni professione.", corpo)


def privacy():
    corpo = f"""<section class="hero"><h1>Informativa privacy</h1><p class="small">Ultimo aggiornamento: ottobre 2026</p></section>
<h2>Chi tratta i dati</h2><p>Titolare del trattamento è Massimiliano Cori (Italia), che gestisce {NOME} come progetto indipendente. Puoi scriverci rispondendo a qualsiasi email che ti mandiamo.</p>
<h2>Quali dati raccogliamo</h2><p>Solo se compili il modulo "Avvisami": la tua email, la professione e la città che scegli, e la pagina o il link da cui arrivi (per capire quali canali funzionano).</p>
<h2>Perché</h2><p>Per mandarti avvisi sulle date e sulle scadenze degli esami di Stato. La base giuridica è il tuo consenso (art. 6.1.a GDPR), che puoi ritirare quando vuoi.</p>
<h2>Chi li gestisce per noi</h2><p>Il sito e il modulo sono ospitati da Netlify, Inc., che conserva i dati del modulo per nostro conto. Netlify può trattare i dati fuori dall'UE con le garanzie previste dal GDPR (clausole contrattuali standard). Non vendiamo né cediamo i tuoi dati.</p>
<h2>Cookie</h2><p>Questo sito non usa cookie di profilazione né strumenti di statistica.</p>
<h2>Per quanto tempo</h2><p>Finché resti iscritto agli avvisi. Se chiedi la cancellazione, cancelliamo i tuoi dati.</p>
<h2>I tuoi diritti</h2><p>Puoi chiedere accesso, correzione, cancellazione, limitazione, portabilità e opposizione (artt. 15-22 GDPR) e puoi fare reclamo al Garante per la protezione dei dati personali (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>).</p>"""
    pagina("privacy.html", "Privacy | EsamiDiStato", "Informativa privacy del sito EsamiDiStato.", corpo)


def extra(urls):
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n")
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{OGGI.isoformat()}</lastmod></url>" for u in urls)
    (SITO / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n')
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in esamidistato/sito (ogni pubblicazione consuma crediti Netlify).
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."

[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    X-Frame-Options = "DENY"
    Permissions-Policy = "camera=(), microphone=(), geolocation=()"
""")
    pagina("404.html", "Pagina non trovata | EsamiDiStato", "Pagina non trovata.",
           '<section class="hero"><h1>Pagina non trovata</h1><p class="lead">Torna al <a href="/">calendario degli esami di Stato</a>.</p></section>',
           base="/")


def controlli(prossime):
    errori = []
    for s in sessioni:
        if not s.get("fonte") or not s.get("verificato_il"):
            errori.append(f"sessione senza fonte: {s['id']}")
        if d(s["scadenza"]) >= d(s["data"]):
            errori.append(f"scadenza non prima dell'esame: {s['id']}")
        if s.get("apertura") and d(s["apertura"]) > d(s["scadenza"]):
            errori.append(f"apertura dopo la scadenza: {s['id']}")
        errori += [f"professione sconosciuta {p} in {s['id']}" for p in s["professioni"] if p not in PROF]
    for p in professioni:
        if not any(p["slug"] in s["professioni"] for s in sessioni):
            errori.append(f"professione senza sessioni: {p['slug']}")
        if p["ente"] != "MIM" and not sedi_di(p["slug"]):
            errori.append(f"professione senza sedi: {p['slug']}")
    for s in sedi:
        if not s.get("fonti") or not s.get("citta") or not s.get("regione"):
            errori.append(f"sede incompleta: {s['ateneo']}")
        errori += [f"professione sconosciuta {p} in {s['ateneo']}" for p in s["professioni"] if p not in PROF]
    for c in citta:
        if not any(s["citta"] == c["comune"] for s in sedi):
            errori.append(f"città senza sedi: {c['nome']}")
    if not prossime:
        errori.append("nessuna sessione futura")
    if errori:
        raise SystemExit("ERRORI NEI DATI:\n" + "\n".join(errori))


def main():
    prossime = sorted(future(sessioni), key=lambda s: (s["data"], s["sessione"], s["id"]))
    controlli(prossime)
    if SITO.exists():
        conserva = {p.name: p.read_bytes() for p in SITO.glob("google*.html")}  # verifica Search Console
        shutil.rmtree(SITO)
    else:
        conserva = {}
    SITO.mkdir()
    shutil.copy(RADICE / "assets" / "og.png", SITO / "og.png")
    for nome, contenuto in conserva.items():
        (SITO / nome).write_bytes(contenuto)
    home(prossime)
    urls = [""]
    for p in professioni:
        pagina_professione(p, prossime)
        urls.append(f"professione/{p['slug']}/")
    for c in citta:
        pagina_citta(c, prossime)
        urls.append(f"citta/{c['slug']}/")
    come_funziona()
    urls.append("come-funziona/")
    privacy()
    urls.append("privacy.html")
    extra(urls)
    print(f"Sito generato in {SITO}: {len(urls)} pagine, {len(prossime)} sessioni future, {len(sedi)} sedi.")


if __name__ == "__main__":
    main()
