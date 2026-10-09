"""Genera il sito statico EsameB1 in esameb1/sito/ a partire da esameb1/dati/.

Uso (dalla radice del repository):
    python3 esameb1/genera.py

Dati: enti.json, sessioni.json (date curate a mano, con fonte), sedi.json (da raccolta/raccogli.py),
citta.json (pagine città). Nessuna dipendenza esterna.
"""
import json
import shutil
from datetime import date
from html import escape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"
URL_SITO = "https://esameb1.netlify.app"  # cambiare qui se il nome del sito su Netlify è diverso
NOME = "EsameB1"
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console, proprietà https://esameb1.netlify.app
OGGI = date.today()

MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
        "settembre", "ottobre", "novembre", "dicembre"]
GIORNI = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
PREFETTURA = ("https://prefettura.interno.gov.it/sites/default/files/24/2024-06/"
              "certificato_di_conoscenza_della_lingua_italiana_-ente_privato-.pdf")

enti = json.loads((DATI / "enti.json").read_text())
sessioni = json.loads((DATI / "sessioni.json").read_text())
sedi = json.loads((DATI / "sedi.json").read_text())
citta = json.loads((DATI / "citta.json").read_text())
ENTE = {e["sigla"]: e for e in enti}
SLUG_ENTE = {"CILS": "cils", "CELI": "celi", "PLIDA": "plida", "CERT.IT": "certit"}


def d(iso):
    return date.fromisoformat(iso)


def data_lunga(iso):
    x = d(iso)
    return f"{GIORNI[x.weekday()]} {x.day} {MESI[x.month - 1]} {x.year}"


def data_breve(iso):
    x = d(iso)
    return f"{x.day} {MESI[x.month - 1]} {x.year}"


def future(lista):
    return [s for s in lista if d(s["data"]) >= OGGI]


def verificato_ultimo():
    date_v = [s["verificato_il"] for s in sessioni] + [s["verificato_il"] for s in sedi]
    return data_breve(max(date_v))


# ---------------------------------------------------------------- pezzi comuni
CSS = """
:root{--bg:#F7F6F2;--card:#FFFFFF;--ink:#14263A;--ink-2:#41505F;--ink-3:#6A7682;--line:#E2DFD6;
--accent:#0E6E55;--accent-2:#E8F3EF;--warn:#9A4A00;--warn-2:#FFF1E2;--mute:#EEECE6;--radius:14px}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0F151B;--card:#161F27;--ink:#EEF2F5;
--ink-2:#BAC5CF;--ink-3:#8E9BA7;--line:#26323D;--accent:#5BC9A6;--accent-2:#16302A;--warn:#FFB367;--warn-2:#33240F;--mute:#1D2730}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;
font-size:17px;line-height:1.6}
a{color:var(--accent)}
.wrap{max-width:980px;margin:0 auto;padding:0 16px}
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
.lead{font-size:1.08rem;color:var(--ink-2);max-width:720px;margin:0 0 6px}
.small{font-size:.9rem;color:var(--ink-3)}
.avviso{background:var(--warn-2);color:var(--ink);border-left:4px solid var(--warn);padding:12px 14px;border-radius:8px;font-size:.95rem;margin:16px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px}
.filtri{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0 14px}
.filtri button{font:inherit;font-size:.92rem;border:1px solid var(--line);background:var(--card);color:var(--ink);
padding:6px 12px;border-radius:999px;cursor:pointer}
.filtri button[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:var(--bg)}
.sessioni{display:grid;gap:10px}
.sess{display:grid;grid-template-columns:150px 1fr;gap:4px 16px;background:var(--card);border:1px solid var(--line);
border-radius:var(--radius);padding:14px 16px}
.sess .quando{font-weight:700}
.sess .quando small{display:block;font-weight:400;color:var(--ink-3);font-size:.85rem}
.sess .cosa{min-width:0}
.badge{display:inline-block;font-size:.78rem;font-weight:700;letter-spacing:.02em;padding:2px 8px;border-radius:6px;
background:var(--mute);color:var(--ink-2);margin-right:6px;vertical-align:1px}
.badge.citt{background:var(--accent-2);color:var(--accent)}
.scad{margin-top:4px;font-size:.93rem;color:var(--ink-2)}
.scad strong{color:var(--ink)}
.scad.urgente strong{color:var(--warn)}
.scad.chiusa{color:var(--ink-3)}
.fonte{font-size:.8rem;color:var(--ink-3)}
.fonte a{color:var(--ink-3)}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}
.griglia a{display:block;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px;
text-decoration:none;color:var(--ink);font-weight:600}
.griglia a small{display:block;font-weight:400;color:var(--ink-3)}
.griglia a:hover{border-color:var(--accent)}
.sedi{list-style:none;padding:0;margin:0;display:grid;gap:8px}
.sedi li{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px}
.sedi .nome{font-weight:650;overflow-wrap:anywhere}
.sedi li,.sess{min-width:0;overflow-wrap:anywhere}
.sedi .det{font-size:.92rem;color:var(--ink-2)}
details{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin:8px 0}
details summary{cursor:pointer;font-weight:650}
.form{display:grid;gap:12px}
.form label{display:grid;gap:4px;font-weight:600;font-size:.95rem}
.form input,.form select{font:inherit;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink);width:100%}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:400;font-size:.9rem;color:var(--ink-2)}
.form .check input{width:auto;margin-top:4px}
.btn{font:inherit;font-weight:700;background:var(--accent);color:var(--bg);border:0;border-radius:10px;padding:12px 18px;cursor:pointer}
.btn:disabled{opacity:.6;cursor:wait}
.hp{position:absolute;left:-9999px}
.ok{background:var(--accent-2);border:1px solid var(--accent);padding:14px;border-radius:10px}
.errore{color:var(--warn);font-weight:600}
.due{display:grid;grid-template-columns:1.4fr 1fr;gap:22px;align-items:start}
footer{margin-top:50px;border-top:1px solid var(--line);padding:22px 0 40px;font-size:.88rem;color:var(--ink-3)}
footer a{color:var(--ink-3)}
table.conf{width:100%;border-collapse:collapse;font-size:.95rem}
table.conf th,table.conf td{border-bottom:1px solid var(--line);padding:8px 6px;text-align:left;vertical-align:top}
.tab-wrap{overflow-x:auto}
@media (max-width:760px){.due{grid-template-columns:1fr}.sess{grid-template-columns:1fr}header.top .wrap{flex-direction:column;align-items:flex-start;gap:4px;padding-top:10px;padding-bottom:10px}nav.menu{gap:14px;font-size:.92rem}}
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
    sc.classList.remove('urgente','chiusa');
    if(g<0){sc.classList.add('chiusa');t.textContent=' — termine nazionale passato: chiedi alla sede se accetta ancora iscrizioni';}
    else if(g===0){sc.classList.add('urgente');t.textContent=' — scade oggi';}
    else if(g<=15){sc.classList.add('urgente');t.textContent=' — mancano '+g+(g===1?' giorno':' giorni');}
    else{t.textContent='';}
  });
  var bott=document.querySelectorAll('.filtri button');
  bott.forEach(function(b){b.addEventListener('click',function(){
    bott.forEach(function(x){x.setAttribute('aria-pressed','false');});b.setAttribute('aria-pressed','true');
    var f=b.dataset.filtro;
    document.querySelectorAll('.sess').forEach(function(el){
      el.hidden=!(f==='tutti'||(f==='citt'&&el.dataset.tipo==='cittadinanza')||el.dataset.ente===f);
    });
  });});
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


def pagina(percorso, titolo, descrizione, corpo, jsonld=None):
    """Scrive sito/<percorso> con la struttura comune."""
    profondita = percorso.count("/")
    rel = "../" * profondita
    canonico = URL_SITO + "/" + (percorso[:-10] if percorso.endswith("index.html") else percorso)
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
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
<meta property="og:url" content="{canonico}">
<meta name="theme-color" content="#0E6E55">
<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230E6E55'/%3E%3Ctext x='32' y='42' font-family='Arial' font-weight='700' font-size='26' text-anchor='middle' fill='white'%3EB1%3C/text%3E%3C/svg%3E">
<style>{CSS}</style>
{ld}
</head>
<body>
<header class="top"><div class="wrap">
<a class="logo" href="{rel}">Esame<span>B1</span></a>
<nav class="menu" aria-label="Menu">
<a href="{rel}#date">Date</a><a href="{rel}#citta">Città</a><a href="{rel}come-funziona/">Come funziona</a><a href="#avvisami">Avvisami</a>
</nav>
</div></header>
<main class="wrap">
{corpo}
</main>
<footer><div class="wrap">
<p><strong>{NOME}</strong> è un sito indipendente, non affiliato agli enti certificatori. CILS, CELI, PLIDA e CERT.IT sono marchi dei rispettivi enti.
Le informazioni vengono dalle fonti ufficiali indicate accanto a ogni dato. <strong>Prima di iscriverti verifica sempre sul sito della sede.</strong>
Questo sito non dà consulenza sulla pratica di cittadinanza: per quella vedi la <a href="https://www.interno.gov.it/it/temi/cittadinanza-e-altri-diritti-civili/cittadinanza" rel="noopener">pagina del Ministero dell'Interno</a>.</p>
<p>Dati controllati il {verificato_ultimo()}. · <a href="{rel}privacy.html">Privacy</a> · <a href="{rel}come-funziona/">Come funziona</a></p>
</div></footer>
<script>{JS}</script>
</body>
</html>
"""
    dest = SITO / percorso
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo)


def scheda_sessione(s):
    citt = s["tipo"] == "cittadinanza"
    esami = ", ".join(s["esami"])
    badge = '<span class="badge citt">Esame per la cittadinanza</span>' if citt else '<span class="badge">B1 valido per la cittadinanza</span>'
    if s.get("scadenza"):
        scad = (f'<div class="scad" data-scadenza="{s["scadenza"]}">Iscrizioni entro: <strong>{data_breve(s["scadenza"])}</strong>'
                f'<span class="stato"></span><br><span class="small">{escape(s["nota_scadenza"])}</span></div>')
    else:
        scad = f'<div class="scad">{escape(s["nota_scadenza"])}</div>'
    return f"""<article class="sess" data-data="{s['data']}" data-ente="{escape(s['ente'])}" data-tipo="{s['tipo']}">
<div class="quando">{data_breve(s['data'])}<small>{GIORNI[d(s['data']).weekday()]}</small></div>
<div class="cosa"><span class="badge">{escape(s['ente'])}</span>{badge}
<div><strong>{escape(esami)}</strong></div>
{scad}
<div class="fonte">Fonte: <a href="{escape(s['fonte'])}" rel="noopener">calendario ufficiale {escape(s['ente'])}</a> · controllato il {data_breve(s['verificato_il'])}</div>
</div>
</article>"""


def lista_sessioni(lista, con_filtri=True):
    filtri = ""
    if con_filtri:
        bottoni = ['<button type="button" data-filtro="tutti" aria-pressed="true">Tutte</button>',
                   '<button type="button" data-filtro="citt" aria-pressed="false">Solo esami "cittadinanza"</button>']
        bottoni += [f'<button type="button" data-filtro="{e}" aria-pressed="false">{e}</button>' for e in ENTE]
        filtri = f'<div class="filtri" role="group" aria-label="Filtra per ente">{"".join(bottoni)}</div>'
    return filtri + '<div class="sessioni">' + "\n".join(scheda_sessione(s) for s in lista) + "</div>"


def modulo(citta_scelta=""):
    opzioni = "".join(
        f'<option value="{escape(c["nome"])}"{" selected" if c["nome"] == citta_scelta else ""}>{escape(c["nome"])}</option>'
        for c in sorted(citta, key=lambda c: c["nome"]))
    enti_opt = "".join(f'<option value="{e}">{e}</option>' for e in ENTE)
    return f"""<section class="card" id="avvisami">
<h2 style="margin-top:0">Avvisami quando ci sono nuove date</h2>
<p class="small" style="margin-top:-4px">Gratis. Ti scriviamo quando esce una nuova sessione o quando una scadenza sta per chiudere nella tua città.</p>
<form class="form avvisami" name="avvisami" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="avvisami">
<input type="hidden" name="source" value="">
<p class="hp"><label>Non compilare <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>La tua email<input type="email" name="email" required autocomplete="email" placeholder="nome@esempio.it"></label>
<label>Città dove vuoi fare l'esame
<select name="citta" required><option value="">Scegli la città</option>{opzioni}<option value="Altra città">Altra città</option></select></label>
<label>Ente preferito (facoltativo)
<select name="ente"><option value="">Nessuna preferenza</option>{enti_opt}</select></label>
<label class="check"><input type="checkbox" name="consenso" value="si" required>
<span>Accetto di ricevere email da {NOME} sulle date dell'esame B1. Posso cancellarmi quando voglio. Ho letto la <a href="/privacy.html">privacy</a>.</span></label>
<button class="btn" type="submit">Avvisami</button>
<p class="errore" data-errore hidden>Non è stato possibile inviare. Riprova tra poco.</p>
</form>
<div class="ok" data-ok hidden><strong>Fatto!</strong> Ti scriveremo quando ci sono novità per la tua città.</div>
</section>"""


def scheda_sede(s, con_citta=False):
    righe = [escape(s["indirizzo"])] if s["indirizzo"] else []
    luogo = " ".join(x for x in [s.get("cap", ""), s["citta"], f'({s["sigla"]})' if s.get("sigla") else ""] if x)
    if luogo:
        righe.append(escape(luogo))
    contatti = []
    if s.get("telefono"):
        contatti.append("Tel. " + escape(s["telefono"]))
    if s.get("email"):
        contatti.append(f'<a href="mailto:{escape(s["email"])}">{escape(s["email"])}</a>')
    if s.get("sito"):
        url = s["sito"] if s["sito"].startswith("http") else "https://" + s["sito"]
        contatti.append(f'<a href="{escape(url)}" rel="noopener nofollow">sito</a>')
    return f"""<li><div class="nome"><span class="badge">{escape(s['ente'])}</span>{escape(s['nome'])}</div>
<div class="det">{"<br>".join(righe)}</div>
{f'<div class="det">{" · ".join(contatti)}</div>' if contatti else ""}
<div class="fonte">Fonte: <a href="{escape(s['fonte'])}" rel="noopener">elenco ufficiale {escape(s['ente'])}</a></div></li>"""


def jsonld_sessioni(lista):
    eventi = []
    for s in lista[:20]:
        e = ENTE[s["ente"]]
        eventi.append({
            "@type": "EducationEvent", "name": f'Esame {", ".join(s["esami"])}', "startDate": s["data"],
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled",
            "location": {"@type": "Place", "name": f'Sedi d\'esame {s["ente"]} in Italia',
                         "address": {"@type": "PostalAddress", "addressCountry": "IT"}},
            "organizer": {"@type": "Organization", "name": e["ente"], "url": e["sito"]},
            "description": f'Sessione d\'esame {s["ente"]} di livello B1, valida per la domanda di cittadinanza italiana.',
        })
    return {"@context": "https://schema.org", "@graph": eventi}


# ---------------------------------------------------------------- pagine
def home(prossime):
    per_citta = {c["slug"]: sum(1 for s in sedi if s["provincia"] == c["provincia"]) for c in citta}
    griglia = "".join(
        f'<a href="citta/{c["slug"]}/">{escape(c["nome"])}<small>{per_citta[c["slug"]]} sedi</small></a>'
        for c in sorted(citta, key=lambda c: c["nome"]))
    prima = prossime[0] if prossime else None
    corpo = f"""<section class="hero">
<h1>Esame di italiano B1 per la cittadinanza: tutte le date 2026 e 2027</h1>
<p class="lead">Per chiedere la cittadinanza italiana per residenza o matrimonio serve un certificato di italiano di livello B1.
Qui trovi in un solo posto <strong>le date, le scadenze e le sedi</strong> dei 4 enti riconosciuti: CILS, CELI, PLIDA e CERT.IT.</p>
<p class="small">{len(sedi)} sedi d'esame in Italia · {len(prossime)} sessioni in programma · dati presi dalle fonti ufficiali{f" · prossimo esame: {data_breve(prima['data'])}" if prima else ""}</p>
<a class="btn cta" href="#avvisami">Avvisami per la mia città</a>
</section>
<div class="avviso">Ogni sede può avere una scadenza diversa da quella nazionale. <strong>Prima di iscriverti, chiedi sempre conferma alla sede.</strong></div>
<div class="due">
<section id="date">
<h2>Prossime date d'esame</h2>
{lista_sessioni(prossime)}
</section>
<aside>
{modulo()}
<section id="citta">
<h2>Sedi per città</h2>
<div class="griglia">{griglia}</div>
<p class="small">La tua città non c'è? Guarda le sedi per regione nelle pagine
{", ".join(f'<a href="ente/{SLUG_ENTE[e]}/">{e}</a>' for e in ENTE)}.</p>
</section>
</aside>
</div>
<section>
<h2>Domande frequenti</h2>
<details><summary>Quale esame devo fare per la cittadinanza?</summary>
<p>Serve un certificato di italiano almeno di livello B1, rilasciato da uno dei 4 enti riconosciuti: CILS (Università per Stranieri di Siena), CELI (Università per Stranieri di Perugia), PLIDA (Società Dante Alighieri) e CERT.IT (Università Roma Tre). Fonte: <a href="{PREFETTURA}" rel="noopener">Prefettura – Ministero dell'Interno</a>. Per i casi particolari (titoli di studio italiani, esenzioni) chiedi alla Prefettura.</p></details>
<details><summary>Che differenza c'è tra "B1 cittadinanza" e B1 normale?</summary>
<p>CILS e CELI hanno un esame B1 pensato per la cittadinanza, con più sessioni durante l'anno. Il B1 "normale" degli stessi enti, il PLIDA B1 e il CERT.IT B1 sono anch'essi certificati di livello B1. Leggi la <a href="come-funziona/">pagina Come funziona</a>.</p></details>
<details><summary>Come mi iscrivo?</summary>
<p>Ci si iscrive presso la sede d'esame, non su questo sito. Scegli una sede nella tua città, contattala e chiedi costo, documenti e scadenza.</p></details>
<details><summary>Quanto costa l'esame?</summary>
<p>Il prezzo lo decide la sede. Per esempio: CELI 2 i cittadinanza 90 € all'Università degli Studi di Milano (febbraio 2026), CILS B1 Cittadinanza 100 € all'Università di Padova. Chiedi il prezzo alla sede che scegli.</p></details>
</section>"""
    pagina("index.html", "Esame B1 cittadinanza: date 2026-2027, scadenze e sedi | EsameB1",
           "Tutte le date dell'esame di italiano B1 per la cittadinanza (CILS, CELI, PLIDA, CERT.IT), scadenze di iscrizione e "
           f"{len(sedi)} sedi in Italia, in un solo posto.", corpo, jsonld_sessioni(prossime))


def pagina_citta(c, prossime):
    qui = [s for s in sedi if s["provincia"] == c["provincia"]]
    in_citta = [s for s in qui if s["citta"] == c["provincia"] or s["citta"] == c["nome"]]
    in_prov = [s for s in qui if s not in in_citta]
    blocchi = []
    for e in ENTE:
        lista = [s for s in in_citta if s["ente"] == e]
        if lista:
            blocchi.append(f'<h3>{e} a {escape(c["nome"])} ({len(lista)})</h3><ul class="sedi">{"".join(scheda_sede(s) for s in lista)}</ul>')
    mancano = [e for e in ENTE if not any(s["ente"] == e for s in qui)]
    if in_prov:
        blocchi.append(f'<details><summary>Altre sedi in provincia di {escape(c["nome"])} ({len(in_prov)})</summary>'
                       f'<ul class="sedi">{"".join(scheda_sede(s) for s in in_prov)}</ul></details>')
    nota_mancano = ""
    if mancano:
        nota_mancano = (f'<p class="small">In provincia di {escape(c["nome"])} non risultano sedi {", ".join(mancano)}: '
                        f'guarda le sedi nelle province vicine nelle pagine {", ".join(f'<a href="../../ente/{SLUG_ENTE[e]}/">{e}</a>' for e in mancano)}.</p>')
    altre = " · ".join(f'<a href="../{x["slug"]}/">{escape(x["nome"])}</a>' for x in sorted(citta, key=lambda x: x["nome"]) if x != c)
    corpo = f"""<section class="hero">
<h1>Esame B1 per la cittadinanza a {escape(c['nome'])}: date e sedi 2026-2027</h1>
<p class="lead">A {escape(c['nome'])} e provincia ci sono <strong>{len(qui)} sedi</strong> dove puoi fare l'esame di italiano B1 per la cittadinanza
({", ".join(f"{sum(1 for s in qui if s['ente'] == e)} {e}" for e in ENTE if any(s['ente'] == e for s in qui))}).
Le date d'esame sono le stesse in tutta Italia; la scadenza per iscriversi può cambiare da sede a sede.</p>
<a class="btn cta" href="#avvisami">Avvisami per {escape(c['nome'])}</a>
</section>
<div class="avviso">Contatta la sede prima di iscriverti: ti dice costo, documenti e ultimo giorno per iscriverti.</div>
<div class="due">
<section>
<h2>Sedi d'esame a {escape(c['nome'])}</h2>
{"".join(blocchi) or "<p>Nessuna sede trovata nelle fonti ufficiali.</p>"}
{nota_mancano}
<h2 id="date">Prossime date (valide anche a {escape(c['nome'])})</h2>
{lista_sessioni(prossime)}
</section>
<aside>
{modulo(c['nome'])}
<section><h2>Altre città</h2><p class="small">{altre}</p></section>
</aside>
</div>"""
    pagina(f"citta/{c['slug']}/index.html",
           f"Esame B1 cittadinanza {c['nome']}: date 2026-2027 e {len(qui)} sedi | EsameB1",
           f"Dove fare l'esame di italiano B1 per la cittadinanza a {c['nome']}: {len(qui)} sedi CILS, CELI, PLIDA e CERT.IT, "
           "prossime date e scadenze di iscrizione.", corpo)


def pagina_ente(e, prossime):
    sigla = e["sigla"]
    sue = [s for s in sedi if s["ente"] == sigla]
    regioni = sorted({s["regione"] for s in sue})
    blocchi = "".join(
        f'<details><summary>{escape(r)} ({sum(1 for s in sue if s["regione"] == r)})</summary>'
        f'<ul class="sedi">{"".join(scheda_sede(s) for s in sue if s["regione"] == r)}</ul></details>'
        for r in regioni)
    date_ente = [s for s in prossime if s["ente"] == sigla]
    corpo = f"""<section class="hero">
<h1>{escape(e['nome'])}: date B1 per la cittadinanza e sedi in Italia</h1>
<p class="lead">{escape(e['cittadinanza'])} {escape(e['iscrizione'])}</p>
<p class="small">Ente: {escape(e['ente'])} · <a href="{escape(e['sito'])}" rel="noopener">sito ufficiale</a> ·
<a href="{escape(e['pagina_date'])}" rel="noopener">calendario ufficiale</a> · <a href="{escape(e['pagina_sedi'])}" rel="noopener">elenco ufficiale delle sedi</a></p>
</section>
<div class="due">
<section>
<h2 id="date">Prossime date {escape(sigla)} (livello B1)</h2>
{lista_sessioni(date_ente, con_filtri=False) if date_ente else "<p>Nessuna data futura pubblicata al momento. Controlliamo il calendario ufficiale ogni settimana.</p>"}
<h2>Sedi {escape(sigla)} in Italia ({len(sue)})</h2>
{blocchi}
</section>
<aside>{modulo()}</aside>
</div>"""
    pagina(f"ente/{SLUG_ENTE[sigla]}/index.html",
           f"Esame {sigla} B1 cittadinanza: date e {len(sue)} sedi in Italia | EsameB1",
           f"Date dell'esame {sigla} di livello B1 per la cittadinanza, scadenze e le {len(sue)} sedi in Italia divise per regione.",
           corpo)


def come_funziona():
    righe = "".join(
        f"<tr><td><strong>{escape(e['sigla'])}</strong><br><span class='small'>{escape(e['ente'])}</span></td>"
        f"<td>{escape(e['cittadinanza'])}</td><td>{sum(1 for s in sedi if s['ente'] == e['sigla'])}</td>"
        f"<td><a href='../ente/{SLUG_ENTE[e['sigla']]}/'>date e sedi</a></td></tr>" for e in enti)
    corpo = f"""<section class="hero">
<h1>Esame B1 per la cittadinanza: come funziona</h1>
<p class="lead">Spiegato in modo semplice: chi deve farlo, quali esami valgono, come ci si iscrive.</p>
</section>
<h2>Chi deve fare l'esame</h2>
<p>Dal 4 dicembre 2018 chi chiede la cittadinanza italiana <strong>per residenza o per matrimonio</strong> deve dimostrare di conoscere l'italiano
almeno al livello B1 (art. 9.1 della legge 91/1992). Si può farlo con un titolo di studio italiano oppure con un certificato di un ente riconosciuto.
Fonte: <a href="{PREFETTURA}" rel="noopener">Prefettura – Ministero dell'Interno</a>. Per il tuo caso specifico chiedi alla Prefettura: questo sito non dà consulenza.</p>
<h2>I 4 enti riconosciuti</h2>
<div class="tab-wrap"><table class="conf"><thead><tr><th>Ente</th><th>Esame per la cittadinanza</th><th>Sedi in Italia</th><th></th></tr></thead>
<tbody>{righe}</tbody></table></div>
<h2>Come ci si iscrive</h2>
<ol>
<li>Scegli una data dal <a href="../#date">calendario</a>.</li>
<li>Scegli una sede nella tua città (<a href="../#citta">elenco per città</a>).</li>
<li>Contatta la sede: ti dice costo, documenti e ultimo giorno per iscriverti. Alcune sedi chiudono le iscrizioni prima della scadenza nazionale.</li>
<li>Paga e conserva la ricevuta. Il giorno dell'esame porta un documento d'identità valido.</li>
</ol>
<h2>Quanto costa</h2>
<p>Lo decide la sede. Esempi reali: CELI 2 i cittadinanza 90 € all'Università degli Studi di Milano (sessione del 18 febbraio 2026),
CILS B1 Cittadinanza 100 € al Centro Linguistico dell'Università di Padova.</p>
{modulo()}"""
    pagina("come-funziona/index.html", "Esame B1 cittadinanza: come funziona, quali esami valgono | EsameB1",
           "Chi deve fare l'esame di italiano B1 per la cittadinanza, i 4 enti riconosciuti (CILS, CELI, PLIDA, CERT.IT), "
           "come ci si iscrive e quanto costa.", corpo)


def privacy():
    corpo = f"""<section class="hero"><h1>Informativa privacy</h1><p class="small">Ultimo aggiornamento: ottobre 2026</p></section>
<h2>Chi tratta i dati</h2><p>Titolare del trattamento è Massimiliano Cori (Italia), che gestisce {NOME} come progetto indipendente. Puoi scriverci rispondendo a qualsiasi email che ti mandiamo.</p>
<h2>Quali dati raccogliamo</h2><p>Solo se compili il modulo "Avvisami": la tua email, la città e l'ente che scegli, e la pagina o il link da cui arrivi (per capire quali canali funzionano).</p>
<h2>Perché</h2><p>Per mandarti avvisi sulle date e sulle scadenze dell'esame B1. La base giuridica è il tuo consenso (art. 6.1.a GDPR), che puoi ritirare quando vuoi.</p>
<h2>Chi li gestisce per noi</h2><p>Il sito e il modulo sono ospitati da Netlify, Inc., che conserva i dati del modulo per nostro conto. Netlify può trattare i dati fuori dall'UE con le garanzie previste dal GDPR (clausole contrattuali standard). Non vendiamo né cediamo i tuoi dati.</p>
<h2>Cookie</h2><p>Questo sito non usa cookie di profilazione né strumenti di statistica.</p>
<h2>Per quanto tempo</h2><p>Finché resti iscritto agli avvisi. Se chiedi la cancellazione, cancelliamo i tuoi dati.</p>
<h2>I tuoi diritti</h2><p>Puoi chiedere accesso, correzione, cancellazione, limitazione, portabilità e opposizione (artt. 15-22 GDPR) e puoi fare reclamo al Garante per la protezione dei dati personali (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>).</p>"""
    pagina("privacy.html", "Privacy | EsameB1", "Informativa privacy del sito EsameB1.", corpo)


def extra(urls):
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n")
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{OGGI.isoformat()}</lastmod></url>" for u in urls)
    (SITO / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n')
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in esameb1/sito (ogni pubblicazione consuma crediti Netlify).
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."

[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    X-Frame-Options = "DENY"
    Permissions-Policy = "camera=(), microphone=(), geolocation=()"
""")
    pagina("404.html", "Pagina non trovata | EsameB1", "Pagina non trovata.",
           '<section class="hero"><h1>Pagina non trovata</h1><p class="lead">Torna al <a href="/">calendario delle date</a>.</p></section>')


def controlli(prossime):
    errori = []
    for s in sessioni:
        if not s.get("fonte") or not s.get("verificato_il"):
            errori.append(f"sessione senza fonte: {s}")
        if s.get("scadenza") and d(s["scadenza"]) >= d(s["data"]):
            errori.append(f"scadenza non prima dell'esame: {s['ente']} {s['data']}")
    for s in sedi:
        if not s.get("fonte") or not s.get("citta"):
            errori.append(f"sede incompleta: {s['ente']} {s['nome']}")
    for c in citta:
        if not any(s["provincia"] == c["provincia"] for s in sedi):
            errori.append(f"città senza sedi: {c['nome']}")
    if not prossime:
        errori.append("nessuna sessione futura")
    if errori:
        raise SystemExit("ERRORI NEI DATI:\n" + "\n".join(errori))


def main():
    prossime = sorted(future(sessioni), key=lambda s: (s["data"], s["ente"]))
    controlli(prossime)
    if SITO.exists():
        conserva = {p.name: p.read_bytes() for p in SITO.glob("google*.html")}  # verifica Search Console
        shutil.rmtree(SITO)
    else:
        conserva = {}
    SITO.mkdir()
    for nome, contenuto in conserva.items():
        (SITO / nome).write_bytes(contenuto)
    home(prossime)
    urls = [""]
    for c in citta:
        pagina_citta(c, prossime)
        urls.append(f"citta/{c['slug']}/")
    for e in enti:
        pagina_ente(e, prossime)
        urls.append(f"ente/{SLUG_ENTE[e['sigla']]}/")
    come_funziona()
    urls.append("come-funziona/")
    privacy()
    urls.append("privacy.html")
    extra(urls)
    print(f"Sito generato in {SITO}: {len(urls)} pagine, {len(prossime)} sessioni future, {len(sedi)} sedi.")


if __name__ == "__main__":
    main()
