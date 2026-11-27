"""Pagina /per-le-scuole/ «EsameB1 per le sedi d'esame e le scuole» e pulsante «Sei questa sede?» sulle schede delle pagine città
(27/11/2026, studio-business/schede/2026-11-27-esameb1-sedi-scuole.md; ricerca-2026-11-26-grandi-b2b.md, sez. 2).

È una PROVA DI DOMANDA: misura se sedi d'esame private e scuole di italiano pagherebbero la licenza di classe del simulatore
(199 € l'anno per sede) o la scheda in evidenza (29 € al mese, una per città, segnata «sponsorizzato»).
- NIENTE VENDITA: i prezzi sono veri, ma i due pulsanti «Mi interessa» non vendono. Contano il clic (esameb1.eu/clic/scuole-licenza,
  esameb1.eu/clic/scuole-scheda) e portano al modulo Netlify «scuole» con l'interesse già scelto. Nessun link di pagamento.
- La pagina dice che cosa c'è oggi (prova gratis, schede gratuite con i dati ufficiali) e che cosa è solo in preparazione.
- Gancio gratuito: «Sei questa sede? Aggiungi gratis il tuo corso e le tue date». Il pulsante sulle schede (genera.scheda_sede,
  solo nelle pagine città) porta qui con ?citta=<slug>#modulo; lo script della pagina scrive la città nel modulo.
- Le risposte restano nei moduli Netlify: mai copiate nel repository. Niente contatti a freddo: aspettiamo che le scuole scrivano.
- Scuole pubbliche e CPIA comprano con il MEPA: fuori dalla prova, e la pagina lo dice.

genera(G) scrive la pagina; controlli(G) ferma la generazione se manca un pezzo. G è il modulo genera.py.
"""
import json
import re
from html import escape

import genera_prova as PV

PERCORSO = "per-le-scuole/"
MODULO = "scuole"  # nome del modulo Netlify
PREZZO_LICENZA = "199 €"
PREZZO_SCHEDA = "29 €"
SIMULAZIONI = 6
CLIC_SEDE = "esameb1.eu/clic/sede-sei-tu"
CLIC_LICENZA = "esameb1.eu/clic/scuole-licenza"
CLIC_SCHEDA = "esameb1.eu/clic/scuole-scheda"
RUOLI = ["Sede d'esame", "Scuola di italiano", "Cooperativa o associazione", "Altro"]
CANDIDATI = ["Meno di 20", "Da 20 a 50", "Da 51 a 100", "Da 101 a 300", "Più di 300", "Non lo so"]
INTERESSI = [("gratis", "Solo aggiungere corso e date, gratis"),  # per prima: è la scelta di chi arriva da una scheda (mai già scelta da noi)
             ("licenza", f"Licenza di classe del simulatore ({PREZZO_LICENZA} l'anno)"),
             ("scheda", f"Scheda in evidenza ({PREZZO_SCHEDA} al mese)")]

# Pulsante sulle schede delle pagine città. Lo stile va nel <head> delle sole pagine che hanno il pulsante (genera.pagina):
# il <head> non entra nell'impronta del lastmod, e il pulsante stesso ne è tolto da _RE_LIBRO (genera.py).
CSS_SEDE_TU = (".sede-tu{display:inline-flex;align-items:center;gap:6px;margin-top:10px;padding:6px 11px;min-height:32px;font-size:.8rem;"
               "font-weight:650;color:var(--ink-3);text-decoration:none;border:1px dashed var(--line-2);border-radius:999px}"
               ".sede-tu:hover,.sede-tu:focus-visible{color:var(--brand-ink);border-color:var(--brand);background:var(--brand-soft)}")


def pulsante_sede(slug_citta, in_provincia=False):
    """«Sei questa sede? Aggiungi corso e date»: ultimo elemento della scheda, dopo la fonte. Non tocca il resto della scheda.
    in_provincia=True: la sede è in un altro comune della provincia; il link porta &provincia=1 e il modulo non scrive la città."""
    return (f'<a class="sede-tu" href="../../{PERCORSO}?citta={slug_citta}{"&amp;provincia=1" if in_provincia else ""}#modulo" data-goatcounter-click="{CLIC_SEDE}" '
            f'data-goatcounter-title="Sei questa sede?">Sei questa sede? Aggiungi corso e date</a>')


CSS_SCUOLE = (".sc-offerte{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(min(100%,290px),1fr));margin-top:16px}"
              ".sc-offerta{background:var(--surface);border:2px solid var(--brand);border-radius:var(--r-l);padding:20px;display:flex;flex-direction:column;min-width:0}"
              ".sc-offerta h3{margin:0 0 4px}.sc-offerta ul{padding-left:20px;margin:10px 0 16px}.sc-offerta li{margin:6px 0}"
              ".sc-prezzo{font-size:1.5rem;font-weight:800;margin:0}.sc-prezzo small{font-size:.9rem;font-weight:500;color:var(--ink-3)}"
              ".sc-stato{display:inline-block;align-self:flex-start;font-size:.78rem;font-weight:750;text-transform:uppercase;letter-spacing:.04em;"
              "background:var(--warn-soft);border-radius:999px;padding:3px 10px;margin-bottom:10px}"
              ".sc-offerta .btn{margin-top:auto;white-space:normal;text-align:center}"
              ".sc-modulo{max-width:680px;margin-top:28px}.sc-esempio{border:1px dashed var(--line-2);border-radius:12px;padding:12px 14px;margin:14px 0}"
              ".sc-esempio b{font-size:.78rem;text-transform:uppercase;letter-spacing:.04em;color:var(--ink-3)}"
              ".sc-arrivo{background:var(--brand-soft);border:1px solid var(--brand);border-radius:12px;padding:12px 14px;margin:14px 0 0}")
# Città dal link della scheda (?citta=<slug>) e interesse dai due pulsanti «Mi interessa». L'invio lo fa lo script comune (form.segnala).
JS_SCUOLE = ("(function(){var f=document.querySelector('form.scuole');if(!f)return;var C=%s;"
             "try{var q=new URLSearchParams(location.search),s=q.get('citta'),a=document.getElementById('sc-arrivo');if(s&&C[s]){"
             "if(q.get('provincia')){f.elements.arrivo.value='provincia:'+s;a.textContent='Arrivi dalla scheda di una sede in provincia. '+a.getAttribute('data-come');}"
             "else{f.elements.citta.value=C[s];f.elements.arrivo.value='scheda:'+s;a.textContent='Arrivi dalla scheda di una sede di '+C[s]+'. '+a.getAttribute('data-come');}"
             "a.hidden=false;}}catch(e){}"
             "document.querySelectorAll('[data-interesse]').forEach(function(b){b.addEventListener('click',function(){"
             "f.elements.interesse.value=b.getAttribute('data-interesse');});});})();")


_RE_SCHEDA = re.compile(r'<li class="s-[A-Z]+">(.*?)</li>', re.S)
_RE_PULSANTE = re.compile(r'<a class="sede-tu".*?</a>', re.S)


def schede_distinte(G):
    """Quante sedi diverse hanno una scheda nelle pagine città già scritte (una sede può stare in due pagine: conta una volta)."""
    viste = set()
    for f in sorted((G.SITO / "citta").glob("*/index.html")):
        viste.update(_RE_PULSANTE.sub("", x) for x in _RE_SCHEDA.findall(f.read_text(encoding="utf-8")))
    return len(viste)


def modulo_html(G):
    ic = G.ic
    opz = lambda voci: "".join(f'<option value="{escape(v)}">{escape(v)}</option>' for v in voci)
    interessi = "".join(f'<option value="{v}">{escape(t)}</option>' for v, t in INTERESSI)
    return f"""<section class="card sc-modulo" id="modulo">
<div class="modulo-testa"><span class="bolla">{ic("mail")}</span><div>
<h2>Scrivici</h2>
<p class="small" style="margin:4px 0 0">Nessun pagamento e nessun impegno. Per le due offerte ti scriviamo quando sono pronte; per corso e date ti rispondiamo entro 7 giorni.</p></div></div>
<p class="sc-arrivo" id="sc-arrivo" data-come="Per aggiungere corso e date scegli «Solo aggiungere corso e date, gratis»: non costa niente." hidden></p>
<form class="form segnala scuole" name="{MODULO}" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="{MODULO}">
<input type="hidden" name="source" value="">
<input type="hidden" name="arrivo" value="">
<p class="hp"><label>Non compilare <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>Nome della scuola o della sede<input type="text" name="scuola" required maxlength="200" autocomplete="organization"></label>
<label>Città<input type="text" name="citta" required maxlength="100" placeholder="per esempio: Torino"></label>
<label>Tipo di struttura
<select name="ruolo" required><option value="">Scegli</option>{opz(RUOLI)}</select></label>
<label>Candidati all'esame B1 in un anno, più o meno
<select name="candidati" required><option value="">Scegli</option>{opz(CANDIDATI)}</select></label>
<label>Che cosa ti interessa
<select name="interesse" required><option value="">Scegli</option>{interessi}</select></label>
<label>Email a cui risponderti<input type="email" name="email" required autocomplete="email" placeholder="nome@scuola.it"></label>
<label>Messaggio (facoltativo)<textarea name="messaggio" maxlength="3000" placeholder="Per corso e date: il link alla pagina del tuo sito dove sono scritti"></textarea></label>
<p class="small" style="margin:0">Usiamo questi dati solo per risponderti su queste offerte e sulla tua scheda. Li cancelliamo dopo averti risposto; se aspetti un'offerta, quando ti abbiamo scritto che è pronta o che non la facciamo. Non li pubblichiamo e non li diamo ad altri. <a href="/privacy.html">Privacy</a>.</p>
<button class="btn" type="submit">{ic("mail")}Invia</button>
<p class="errore" data-errore hidden>Non è stato possibile inviare. Riprova tra poco.</p>
</form>
<div class="ok" data-ok hidden>{ic("ok")}<span><strong>Ricevuto, grazie!</strong> Ti rispondiamo all'email che hai lasciato. Non hai comprato niente e non devi pagare niente.</span></div>
</section>"""


def pagina(G):
    ic = G.ic
    n_citta = len(G.citta)
    n_schede = schede_distinte(G)
    oltre = n_schede // 100 * 100  # «oltre 600»: numero tondo sotto il conto vero delle schede nelle pagine città (non le 644 sedi dei dati)
    if oltre < 100 or oltre >= n_schede + 1:
        raise SystemExit(f"per le scuole: conto delle schede nelle pagine città non valido ({n_schede})")
    n_dom = len(PV.SCELTA) + len(PV.VERO_FALSO) + len(PV.SPAZI)
    mappa = json.dumps({c["slug"]: c["nome"] for c in sorted(G.citta, key=lambda c: c["slug"])}, ensure_ascii=False).replace("</", "<\\/")
    faq = [
        ("Quando saranno pronte la licenza e la scheda in evidenza?",
         "Non c'è ancora una data. Le costruiamo solo se abbastanza scuole ci dicono che sono interessate: per questo prima chiediamo. "
         "Se lasci i tuoi dati ti scriviamo quando sono pronte, oppure per dirti che abbiamo deciso di non farle."),
        ("Lasciare i dati mi impegna a comprare?",
         "No. Il modulo non è un ordine e non chiede dati di pagamento. Quando il servizio è pronto ti scriviamo il prezzo definitivo, con l'IVA chiarita, e decidi tu."),
        ("Le simulazioni sono prove ufficiali?",
         "No. Le scriviamo noi, sul modello delle prove pubblicate dagli enti. Non usiamo e non copiamo i file degli enti, che restano sui loro siti: "
         f'li trovi nella pagina delle <a href="../esempi/">prove d\'esempio ufficiali</a>. Un esempio del nostro lavoro è la <a href="../{PV.PERCORSO}">prova online gratuita</a>.'),
        ("Chi paga la scheda in evidenza sale nell'elenco delle sedi?",
         "No. L'elenco delle sedi resta quello degli elenchi ufficiali degli enti, nello stesso ordine per tutti. La scheda in evidenza sta in un riquadro separato, con la scritta «sponsorizzato»."),
        ("Siamo una scuola pubblica o un CPIA: possiamo scrivere?",
         "Sì, per aggiungere gratis corso e date alla vostra scheda. Le due offerte a pagamento per ora non sono per voi, perché non siamo sul MEPA."),
    ]
    corpo = f"""<section class="hero">
<style>{CSS_SCUOLE}</style>
{G.briciole(("EsameB1", "../"), ("Per le scuole", None))}
<h1>EsameB1 per le sedi d'esame e le scuole</h1>
<p class="lead"><strong>Prepari persone all'esame di italiano B1 per la cittadinanza?</strong> In questa pagina trovi che cosa {G.NOME} offre già oggi, gratis,
e due servizi a pagamento che stiamo preparando per le scuole: una licenza di classe del simulatore e una scheda in evidenza nella pagina della tua città.</p>
{G.avviso("<strong>Oggi non vendiamo niente e non chiediamo pagamenti.</strong> I prezzi scritti qui sono quelli previsti. Se un servizio ti interessa, lascia i tuoi dati nel <a href=\"#modulo\">modulo</a>: ti scriviamo quando è pronto.")}
<div class="azioni"><a class="btn" href="#offerte">{ic("euro")}Le due offerte e i prezzi</a><a class="btn btn-2" href="#gratis">{ic("edificio")}Sei una sede? Aggiungi corso e date</a></div>
</section>
<section>
<h2 id="per-chi">{ic("info")}Per chi è</h2>
<ul class="passi-lista">
<li><span><strong>Sedi d'esame private</strong> che organizzano le sessioni CILS, CELI, PLIDA o CERT.IT e vogliono candidati più preparati.</span></li>
<li><span><strong>Scuole di italiano per stranieri</strong> che fanno corsi di preparazione al B1.</span></li>
<li><span><strong>Cooperative e associazioni</strong> che tengono corsi di italiano B1 per chi chiede la cittadinanza.</span></li>
</ul>
<p><strong>Scuole pubbliche e CPIA.</strong> Di solito comprano attraverso il MEPA, il mercato elettronico della pubblica amministrazione. {G.NOME} per ora non è sul MEPA:
le due offerte a pagamento, all'inizio, non sono per le scuole pubbliche. Resta per tutti, anche per loro, l'<a href="#gratis">aggiunta gratuita di corso e date</a> alla scheda.</p>
</section>
<section>
<h2 id="oggi">{ic("ok")}Che cosa c'è già oggi, gratis</h2>
<ul class="passi-lista">
<li><span><strong>Una prova B1 online con {n_dom} domande e correzione automatica.</strong> L'abbiamo scritta noi, sul modello del CILS B1 Cittadinanza, e non è un esame ufficiale.
Per ora è senza audio: al posto dell'ascolto c'è un dialogo da leggere, poi frasi vero o falso su un testo e un testo da completare.
I tuoi studenti possono farla dal telefono, senza registrarsi: <a href="../{PV.PERCORSO}">prova B1 online gratis</a>.</span></li>
<li><span><strong>Le schede di oltre {oltre} sedi d'esame, in {n_citta} pagine città.</strong> Ogni scheda ha nome, indirizzo e contatti presi dall'elenco ufficiale dell'ente, con il link alla fonte.
Sono gratuite e restano gratuite: nessuna sede paga per esserci. Trovi la tua nell'<a href="../#citta">elenco delle città</a>.
Se la tua sede non è in una pagina città, scrivici lo stesso.</span></li>
</ul>
</section>
<section>
<h2 id="gratis">{ic("edificio")}Sei una sede d'esame? Aggiungi gratis il tuo corso e le tue date</h2>
<p>Gli elenchi ufficiali degli enti dicono dove si trova una sede, ma non dicono se fa un corso di preparazione, quando comincia e in quali giorni raccoglie le iscrizioni.
Se la sede è la tua, queste informazioni puoi darcele tu.</p>
<ol>
<li>Compila il <a href="#modulo">modulo</a> e scegli «Solo aggiungere corso e date, gratis».</li>
<li>Nel messaggio metti il link alla pagina del tuo sito dove corso e date sono scritti.</li>
<li>Noi controlliamo su quella pagina e aggiungiamo le informazioni sotto la tua scheda, con la fonte e il giorno del controllo.</li>
</ol>
<p>È gratis e resta gratis. La scheda non cambia posto nell'elenco. Aggiungiamo solo quello che possiamo controllare su una pagina pubblica della sede:
se una cosa non è scritta da nessuna parte, non la pubblichiamo.</p>
</section>
<section>
<h2 id="offerte">{ic("euro")}Le due offerte in preparazione</h2>
<p>Nessuna delle due è in vendita adesso. I pulsanti qui sotto non aprono un pagamento: portano al modulo, con l'offerta già scelta.</p>
<div class="sc-offerte">
<article class="sc-offerta" id="licenza">
<span class="sc-stato">In preparazione</span>
<h3>Licenza di classe del simulatore</h3>
<p class="sc-prezzo">{PREZZO_LICENZA} <small>l'anno per sede, studenti illimitati</small></p>
<ul>
<li><strong>{SIMULAZIONI} simulazioni complete</strong> dell'esame B1, scritte da noi. Mai i file degli enti.</li>
<li><strong>Correzione automatica</strong> di ascolto e lettura (l'ascolto con audio è in preparazione).</li>
<li><strong>Griglie di valutazione</strong> per la prova scritta e per l'orale, da usare in classe.</li>
<li><strong>Un codice classe</strong> da dare agli studenti e <strong>un riepilogo dei risultati</strong> per l'insegnante.</li>
<li><strong>Nessun conto personale per gli studenti</strong>: entrano con il codice, senza email e senza password.</li>
</ul>
<a class="btn" href="#modulo" data-interesse="licenza" data-goatcounter-click="{CLIC_LICENZA}" data-goatcounter-title="Scuole: licenza {PREZZO_LICENZA}">Mi interessa la licenza</a>
</article>
<article class="sc-offerta" id="scheda">
<span class="sc-stato">In preparazione</span>
<h3>Scheda in evidenza nella pagina della città</h3>
<p class="sc-prezzo">{PREZZO_SCHEDA} <small>al mese, una sola per città</small></p>
<ul>
<li><strong>Un riquadro con il tuo corso di preparazione</strong> nella pagina della tua città: nome della scuola, corso, date, contatti.</li>
<li><strong>Una sola scuola per città</strong>: il posto è uno.</li>
<li><strong>Sempre con la scritta «sponsorizzato»</strong>, ben visibile.</li>
<li><strong>Mai dentro l'elenco ufficiale delle sedi</strong>: sta in un riquadro a parte e non cambia l'ordine delle sedi.</li>
</ul>
<a class="btn" href="#modulo" data-interesse="scheda" data-goatcounter-click="{CLIC_SCHEDA}" data-goatcounter-title="Scuole: scheda in evidenza {PREZZO_SCHEDA}">Mi interessa la scheda</a>
</article>
</div>
<p class="small">I prezzi sono quelli previsti oggi. Non abbiamo ancora deciso se sono con o senza IVA: te lo scriviamo insieme al prezzo definitivo, quando il servizio è pronto e prima di qualsiasi ordine.
Per la scheda in evidenza, prima di qualsiasi ordine ti scriviamo quante visite ha avuto la pagina della tua città nell'ultimo mese.</p>
</section>
<section>
<h2 id="regole">{ic("scudo")}Le regole della scheda in evidenza</h2>
<p>Chi cerca una sede d'esame deve poter distinguere subito un dato ufficiale da uno spazio a pagamento. Per questo la scheda in evidenza avrà sempre queste regole:</p>
<ul>
<li>porta sempre la scritta <strong>«sponsorizzato»</strong>;</li>
<li>è <strong>una per città</strong>;</li>
<li>sta in un riquadro separato: <strong>non entra mai nell'elenco ufficiale delle sedi e non ne cambia l'ordine</strong>;</li>
<li>l'elenco delle sedi resta quello degli elenchi ufficiali degli enti, uguale per chi paga e per chi non paga;</li>
<li>non è un consiglio dell'ente e non dice che una scuola è migliore di un'altra.</li>
</ul>
<div class="sc-esempio"><b>Esempio di come sarà segnata</b><p style="margin:6px 0 0">Sponsorizzato · Scuola di esempio: corso di preparazione al B1, 20 ore. Questo è un esempio: oggi nessuna scheda del sito è a pagamento.</p></div>
</section>
<section>
<h2 id="chi-siamo">{ic("attenzione")}Che cosa non siamo</h2>
<p><strong>{G.NOME} è un sito indipendente: non è affiliato a CILS, CELI, PLIDA o CERT.IT</strong>, che sono marchi dei rispettivi enti, e non è un ente certificatore.
Le nostre simulazioni non sono prove ufficiali e non sostituiscono quelle pubblicate dagli enti. Non promettiamo che chi le fa supera l'esame.
<a href="../chi-siamo/">Chi siamo</a> · <a href="../come-lavoriamo/">come raccogliamo e controlliamo i dati</a>.</p>
</section>
{modulo_html(G)}
<section>
<h2 id="domande">{ic("info")}Domande frequenti</h2>
{"".join(G.domanda(q, a) for q, a in faq)}
</section>
<script>{JS_SCUOLE % mappa}</script>"""
    G.pagina(f"{PERCORSO}index.html",
             "EsameB1 per le sedi d'esame e le scuole di italiano",  # senza titolo_pagina(): il nome del sito è già in testa
             G.descrizione_pagina("Per sedi d'esame e scuole di italiano: prova B1 gratis, schede gratuite delle sedi e due offerte in preparazione, "
                                  "con i prezzi. Nessuna vendita ora."), corpo)


def genera(G):
    pagina(G)
    return [PERCORSO]


def controlli(G):
    """Ferma la generazione se: manca il modulo «scuole» o un suo campo; i due pulsanti con il prezzo non portano al modulo; c'è un
    link di pagamento; manca la regola «sponsorizzato» o «non affiliato»; una scheda di una pagina città non ha il suo pulsante, o
    il pulsante è finito fuori dalle pagine città; il pulsante entra nell'impronta del lastmod."""
    h = (G.SITO / PERCORSO / "index.html").read_text(encoding="utf-8")
    form = re.search(rf'<form [^>]*name="{MODULO}"[^>]*>(.*?)</form>', h, re.S)
    if not form or 'data-netlify="true"' not in form.group(0) or 'netlify-honeypot="bot-field"' not in form.group(0):
        raise SystemExit("per le scuole: manca il modulo Netlify «scuole» con la trappola per i robot")
    for campo in ("form-name", "bot-field", "scuola", "citta", "ruolo", "candidati", "interesse", "email", "messaggio"):
        if f'name="{campo}"' not in form.group(1):
            raise SystemExit(f"per le scuole: nel modulo manca il campo {campo}")
    for clic, valore in ((CLIC_LICENZA, "licenza"), (CLIC_SCHEDA, "scheda")):
        if not re.search(rf'<a class="btn" href="#modulo" data-interesse="{valore}" data-goatcounter-click="{clic}"', h):
            raise SystemExit(f"per le scuole: il pulsante {clic} non porta al modulo")
    if re.search(r"stripe|paypal|gumroad|lemonsqueezy|checkout|buy\.", h, re.I):
        raise SystemExit("per le scuole: c'è un link di pagamento (niente vendita)")
    for frase in ("«sponsorizzato»", "non entra mai nell'elenco ufficiale delle sedi", "non è affiliato", "Oggi non vendiamo niente", PREZZO_LICENZA, PREZZO_SCHEDA, "MEPA", "senza audio", "con o senza IVA"):
        if frase not in h:
            raise SystemExit(f"per le scuole: manca «{frase}»")
    for f in sorted(G.SITO.rglob("*.html")):
        t = f.read_text(encoding="utf-8")
        rel = f.relative_to(G.SITO).as_posix()
        n = t.count('class="sede-tu"')
        if rel.startswith("citta/"):
            schede = re.findall(r'<li class="s-[A-Z]+">.*?</li>', t, re.S)
            attesi = tuple(pulsante_sede(rel.split("/")[1], x) + "</li>" for x in (False, True))
            if not schede or n != len(schede) or any(not s.endswith(attesi) for s in schede):
                raise SystemExit(f"{rel}: ogni scheda sede deve finire con il pulsante «Sei questa sede?» di questa città")
            if G.impronta_contenuto(t) != G.impronta_contenuto(t.replace(attesi[0], "</li>").replace(attesi[1], "</li>")):
                raise SystemExit(f"{rel}: il pulsante «Sei questa sede?» entra nell'impronta del lastmod")
        elif n:
            raise SystemExit(f"{rel}: pulsante «Sei questa sede?» fuori dalle pagine città")
