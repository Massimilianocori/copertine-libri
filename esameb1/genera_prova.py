"""Prova B1 online gratuita (/prova-b1-online/, 26/11/2026): prova di domanda «Pass EsameB1»
(studio-business/schede/2026-11-26-prova-pass-esameb1.md).

Una prova scritta DA NOI sul modello del CILS B1 Cittadinanza: la pagina lo dice in alto e nelle domande frequenti, e non
contiene materiale degli enti. La struttura dell'esame vero (prove, tempi, punti, criteri) viene da dati/esempi.json e
dati/risultati.json, con le loro fonti; testi, domande e spiegazioni stanno qui sotto.

- Parte 1: dialogo da leggere, 6 domande a scelta multipla (al posto dell'ascolto: non c'è l'audio, e la pagina lo dice).
- Parte 2: lettura, 12 frasi vero/falso (come la prova 1 di lettura dell'esame).
- Parte 3: testo da completare, 6 spazi a scelta multipla (come la prova 2: riflessione grammaticale).
- Parte 4: scrittura, due tracce per un'email di 80-120 parole, con contaparole (non corretta: criteri ufficiali per controllarsi).
- Parte 5: orale, solo la traccia.

Correzione nel browser (JS_PROVA): 1 punto per ogni risposta giusta, 0 per sbagliata o vuota, 24 in tutto. Nessun «promosso/bocciato»:
la soglia in punti del CILS non è pubblicata. Niente viene salvato o inviato.
Il riquadro «Pass EsameB1» lo mette genera.pagina() al posto del segnaposto <!--pass-->.
"""
import json
from html import escape

PERCORSO = "prova-b1-online/"
CLIC_LIBRO = "libro-prova-online"  # etichetta propria dei clic sul libro in questa pagina

# ---------------------------------------------------------------- parte 1: dialogo (scelta multipla)
DIALOGO_TITOLO = "Una telefonata al centro sportivo"
DIALOGO = [
    ("Segretaria", "Centro sportivo «Le Querce», buongiorno."),
    ("Amina", "Buongiorno, mi chiamo Amina Haddad. Vorrei iscrivere mio figlio al corso di nuoto. Ha otto anni."),
    ("Segretaria", "Certo. Suo figlio sa già nuotare?"),
    ("Amina", "Un po'. Ha fatto un corso due anni fa, ma poi abbiamo cambiato città e ha smesso."),
    ("Segretaria", "Allora va bene il gruppo intermedio. Le lezioni sono il martedì e il giovedì, dalle 17 alle 18."),
    ("Amina", "Il giovedì per noi è difficile, perché io lavoro fino alle 18. C'è un altro orario?"),
    ("Segretaria", "C'è il corso del sabato mattina, dalle 10 alle 11, ma è una sola lezione alla settimana."),
    ("Amina", "Il sabato va benissimo. Quanto costa?"),
    ("Segretaria", "Il corso del sabato costa 90 euro per tre mesi. Se paga tutto l'anno insieme c'è uno sconto: 240 euro invece di 270."),
    ("Amina", "Per ora preferisco pagare solo i primi tre mesi. Che cosa devo portare per l'iscrizione?"),
    ("Segretaria", "Un certificato medico e una fotografia del bambino. Il modulo lo compila qui da noi."),
    ("Amina", "Il certificato medico non ce l'ho ancora. Posso iscriverlo lo stesso?"),
    ("Segretaria", "Sì, può fare l'iscrizione subito, ma il bambino non può entrare in piscina senza il certificato. Lo porti prima della prima lezione."),
    ("Amina", "Va bene. Quando comincia il corso?"),
    ("Segretaria", "Sabato 10 ottobre. La segreteria è aperta dal lunedì al venerdì, dalle 9 alle 13 e dalle 15 alle 19."),
    ("Amina", "Allora passo domani pomeriggio, dopo il lavoro. Grazie mille."),
    ("Segretaria", "Grazie a lei. A domani."),
]
# (domanda, [opzioni a, b, c], lettera giusta, spiegazione)
SCELTA = [
    ("Perché Amina telefona al centro sportivo?",
     ["Per iscrivere suo figlio a un corso di nuoto.", "Per chiedere gli orari della piscina per sé.", "Per pagare un corso che suo figlio fa già."], "a",
     "All'inizio Amina dice: «Vorrei iscrivere mio figlio al corso di nuoto»."),
    ("Il figlio di Amina:",
     ["nuota già molto bene.", "non è mai entrato in piscina.", "ha già fatto un corso di nuoto."], "c",
     "Amina dice che sa nuotare «un po'» e che «ha fatto un corso due anni fa»."),
    ("Perché Amina non sceglie il corso del martedì e del giovedì?",
     ["Perché costa troppo.", "Perché il giovedì lavora fino alle 18.", "Perché il martedì suo figlio ha un altro corso."], "b",
     "Amina spiega: «Il giovedì per noi è difficile, perché io lavoro fino alle 18»."),
    ("Quanto vuole pagare Amina per ora?",
     ["90 euro.", "240 euro.", "270 euro."], "a",
     "Amina preferisce «pagare solo i primi tre mesi», e il corso del sabato costa 90 euro per tre mesi. 240 euro è il prezzo di tutto l'anno con lo sconto."),
    ("Senza il certificato medico il bambino:",
     ["non può fare l'iscrizione.", "non può entrare in piscina.", "deve pagare di più."], "b",
     "La segretaria dice che l'iscrizione si può fare subito, ma «il bambino non può entrare in piscina senza il certificato»."),
    ("Quando va Amina in segreteria?",
     ["Sabato mattina.", "Il giorno stesso della telefonata.", "Il giorno dopo, di pomeriggio."], "c",
     "Alla fine Amina dice: «Allora passo domani pomeriggio, dopo il lavoro»."),
]

# ---------------------------------------------------------------- parte 2: lettura (vero/falso)
ARTICOLO_TITOLO = "La biblioteca del quartiere resta aperta anche la sera"
ARTICOLO = [
    "Da lunedì 3 marzo la biblioteca comunale di via dei Tigli ha un nuovo orario. Prima chiudeva alle 18; adesso resta aperta fino alle 22 "
    "dal lunedì al giovedì. Il venerdì e il sabato l'orario non cambia: dalle 9 alle 18. La domenica la biblioteca resta chiusa.",
    "La decisione nasce da una richiesta degli abitanti. L'anno scorso più di quattrocento persone hanno firmato una lettera al Comune: "
    "molti lavorano tutto il giorno e non riuscivano mai ad andare in biblioteca. «Finisco di lavorare alle 19 e trovavo sempre la porta chiusa», "
    "racconta Daniel, 34 anni, che lavora in un magazzino e abita nel quartiere da sei anni. «Adesso posso venire a studiare dopo cena.»",
    "Di sera la biblioteca offre anche nuovi servizi. Il martedì c'è un gruppo di conversazione in italiano per stranieri: è gratuito e non serve "
    "iscriversi, basta presentarsi alle 20. Il mercoledì, invece, alcuni volontari aiutano chi deve compilare un modulo o scrivere un curriculum; "
    "per questo servizio bisogna prenotare per telefono, perché i posti sono solo dieci.",
    "Per prendere in prestito i libri serve la tessera, che è gratuita: si fa in pochi minuti con un documento d'identità. Si possono prendere "
    "fino a cinque libri alla volta e tenerli per trenta giorni. Chi restituisce i libri in ritardo non paga una multa, ma non può prendere "
    "altri libri per due settimane.",
    "La direttrice, Paola Ferri, è soddisfatta: «Nelle prime settimane, di sera sono venute in media sessanta persone al giorno. "
    "Se i numeri restano questi, da settembre apriremo anche la domenica mattina.»",
]
# (frase, True = vero, spiegazione)
VERO_FALSO = [
    ("Adesso la biblioteca chiude alle 22 tutti i giorni.", False,
     "Resta aperta fino alle 22 solo «dal lunedì al giovedì»: il venerdì e il sabato chiude alle 18 e la domenica è chiusa."),
    ("Il sabato la biblioteca chiude alle 18.", True,
     "Il venerdì e il sabato l'orario è «dalle 9 alle 18»."),
    ("Sono stati gli abitanti del quartiere a chiedere il nuovo orario.", True,
     "«La decisione nasce da una richiesta degli abitanti», che hanno firmato una lettera al Comune."),
    ("La lettera al Comune è stata firmata da meno di quattrocento persone.", False,
     "L'hanno firmata «più di quattrocento persone»."),
    ("Daniel abita nel quartiere da sei anni.", True,
     "Il testo dice che Daniel «abita nel quartiere da sei anni»."),
    ("Prima del nuovo orario Daniel riusciva ad andare in biblioteca dopo il lavoro.", False,
     "Daniel finisce di lavorare alle 19 e trovava «sempre la porta chiusa»."),
    ("Per partecipare al gruppo di conversazione bisogna iscriversi.", False,
     "«Non serve iscriversi, basta presentarsi alle 20»."),
    ("Il gruppo di conversazione non costa niente.", True,
     "Il gruppo di conversazione «è gratuito»."),
    ("Per l'aiuto dei volontari, il mercoledì, bisogna prenotare.", True,
     "«Per questo servizio bisogna prenotare per telefono, perché i posti sono solo dieci»."),
    ("La tessera della biblioteca costa cinque euro.", False,
     "La tessera «è gratuita». Cinque è il numero dei libri che si possono prendere alla volta."),
    ("Chi riporta i libri in ritardo deve pagare una multa.", False,
     "Chi è in ritardo «non paga una multa», ma per due settimane non può prendere altri libri."),
    ("La direttrice pensa di aprire anche la domenica mattina, se continuano a venire tante persone.", True,
     "La direttrice dice: «Se i numeri restano questi, da settembre apriremo anche la domenica mattina»."),
]

# ---------------------------------------------------------------- parte 3: testo da completare (grammatica e lessico)
# {n} = spazio numero n. Maiuscole di cortesia (Le, Sua, La) come in una lettera formale.
EMAIL_OGGETTO = "Lavatrice che non funziona"
EMAIL = [
    "Gentile signor Bassi,",
    "Le scrivo perché da tre giorni la lavatrice dell'appartamento non funziona più. Quando la accendo, l'acqua entra, {1} la macchina non parte. "
    "Ho già controllato la spina e il rubinetto, ma non ho {2} nessun problema.",
    "Ieri ho chiamato un tecnico: può venire giovedì mattina, ma prima vuole sapere chi {3} la riparazione. Nel contratto c'è scritto che le "
    "riparazioni degli elettrodomestici sono a carico {4} proprietario: per questo Le chiedo di confermarmi che posso fissare l'appuntamento.",
    "Se preferisce mandare un tecnico di Sua fiducia, per me va bene: sono a casa tutti i pomeriggi {5} 17 in poi. Aspetto una Sua {6} e La ringrazio.",
    "Cordiali saluti,",
    "Olena Kovalenko",
]
# ([opzioni a, b, c], lettera giusta, spiegazione)
SPAZI = [
    (["perché", "ma", "quindi"], "b",
     "Le due frasi sono in contrasto: l'acqua entra, però la macchina non parte. «Perché» introduce una causa, «quindi» una conseguenza."),
    (["trovando", "trovata", "trovato"], "c",
     "Il passato prossimo si forma con «avere» e il participio passato: «non ho trovato». Qui il participio resta al maschile singolare."),
    (["pagherà", "pagava", "ha pagato"], "a",
     "La riparazione non è ancora stata fatta: per un'azione che deve ancora succedere serve il futuro, «pagherà»."),
    (["al", "del", "dal"], "b",
     "Si dice «essere a carico di qualcuno»: di + il = «del»."),
    (["alle", "nelle", "dalle"], "c",
     "«Dalle 17 in poi» indica l'ora da cui comincia qualcosa: da + le = «dalle»."),
    (["domanda", "risposta", "richiesta"], "b",
     "Olena ha fatto una richiesta al proprietario e adesso aspetta che lui risponda: aspetta una «risposta»."),
]

# ---------------------------------------------------------------- parte 4 e 5: tracce
TRACCE_SCRITTURA = [
    "Hai comprato un paio di scarpe su Internet, ma è arrivato un numero sbagliato. Scrivi un'email al servizio clienti del negozio: "
    "spiega che cosa è successo, di' se vuoi cambiare le scarpe o riavere i soldi e chiedi come devi rispedire il pacco.",
    "Vuoi iscriverti a un corso serale di informatica organizzato dal Comune. Scrivi un'email all'ufficio che organizza il corso: "
    "presentati, spiega perché il corso ti interessa e chiedi informazioni sugli orari, sul costo e sui documenti da portare.",
]
ORALE_DOMANDE = ["Che lavoro fai, o che cosa studi?", "Com'è una tua giornata normale?", "Che cosa ti piace fare nel tempo libero?",
                 "Com'è il quartiere dove abiti? Che cosa ti piace e che cosa cambieresti?"]
ORALE_DIALOGO = ("Devi prenotare una visita medica. Telefoni al centro prenotazioni: spiega di che visita hai bisogno, chiedi il giorno e l'ora "
                 "e domanda che cosa devi portare. Un'altra persona fa l'impiegato e ti risponde.")

PARTI = {"1": "Parte 1, dialogo", "2": "Parte 2, vero o falso", "3": "Parte 3, testo da completare"}
TESTI = {"giusto": "Giusto.", "sbagliato": "Sbagliato.", "vuota": "Nessuna risposta.", "risposta": "La risposta giusta è: {x}",
         "punteggio": "Il tuo punteggio: {n} su {tot}", "su": "{n} su {tot}", "parti": PARTI,
         "vuote1": "Hai lasciato 1 domanda senza risposta: conta come sbagliata.",
         "vuote": "Hai lasciato {n} domande senza risposta: contano come sbagliate.",
         "tutte": "Tutte le risposte sono giuste. Adesso prova la scrittura, qui sotto.",
         "rileggi": "Sotto ogni domanda trovi la risposta giusta e la spiegazione: rileggi quelle che hai sbagliato.",
         "nota": "Questo punteggio è nostro e non è quello dell'esame: serve solo a vedere dove sbagli.",
         "cp_vuoto": "Scrivi o incolla qui la tua email: servono da {min} a {max} parole.",
         "cp_sotto1": "Manca 1 parola per arrivare al minimo.", "cp_sotto": "Mancano {n} parole per arrivare al minimo.",
         "cp_sopra1": "Hai 1 parola oltre il massimo: accorcia il testo.", "cp_sopra": "Hai {n} parole oltre il massimo: accorcia il testo.",
         "cp_ok": "Sei dentro i limiti: da {min} a {max} parole."}

CSS_PROVA = """
.prova{max-width:820px}
.prova h3{margin:26px 0 10px}
.testo-prova{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--brand);border-radius:var(--r);padding:16px 18px;margin:0 0 18px}
.testo-prova p{margin:0 0 10px}.testo-prova p:last-child{margin-bottom:0}
.testo-prova .tit{font-weight:800;font-size:1.08rem}
.testo-prova b{color:var(--brand-ink)}
.spazio{font-weight:700;white-space:nowrap}
.prova fieldset{border:1.5px solid var(--line-2);border-radius:var(--r);padding:10px 14px 14px;margin:0 0 12px;background:var(--surface);min-width:0}
.prova legend{font-weight:650;padding:0 6px;max-width:100%}
.prova .opz{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px}
.prova .opz.col{flex-direction:column}
.prova .opz label{display:flex;gap:10px;align-items:center;min-height:44px;padding:8px 14px;border:1.5px solid var(--line-2);border-radius:10px;background:var(--bg);cursor:pointer}
.prova .opz input{width:20px;height:20px;margin:0;flex:none;accent-color:var(--brand)}
.prova fieldset.giusta{border-color:var(--brand)}.prova fieldset.sbagliata{border-color:var(--rosso)}
.prova .opz label.la-giusta{border-color:var(--brand);background:var(--brand-soft);font-weight:650}
.prova .opz label.la-sbagliata{border-color:var(--rosso)}
.q-esito{font-weight:700;margin:12px 0 2px}.giusta .q-esito{color:var(--brand-ink)}.sbagliata .q-esito{color:var(--rosso)}
.q-spieg{margin:0;color:var(--ink-2)}
.prova-esito{border:2px solid var(--brand);border-radius:var(--r-l);background:var(--surface);padding:18px 20px;margin:18px 0 0}
.prova-esito:focus{outline:3px solid var(--brand-soft)}
.prova-esito h3{margin:0 0 8px;font-size:1.5rem}
.prova-esito ul{margin:0 0 10px;padding-left:1.2em}.prova-esito p{margin:6px 0 0}
.tracce{display:grid;gap:10px;margin:0 0 16px;padding:0;list-style:none}
.tracce li{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:12px 14px}
"""

JS_PROVA = """
(function(){
  var box=document.getElementById('prova');if(!box)return;
  var T=JSON.parse(box.getAttribute('data-testi'));
  var dom=[].slice.call(box.querySelectorAll('fieldset[data-giusta]')),esito=document.getElementById('prova-esito'),
      bC=box.querySelector('[data-azione=correggi]'),bR=box.querySelector('[data-azione=rifai]');
  function el(tag,testo){var e=document.createElement(tag);e.textContent=testo;return e;}
  function pulisci(){
    dom.forEach(function(f){
      f.classList.remove('giusta','sbagliata');
      f.querySelector('.q-esito').hidden=true;f.querySelector('.q-spieg').hidden=true;
      [].forEach.call(f.querySelectorAll('label'),function(l){l.classList.remove('la-giusta','la-sbagliata');});
      [].forEach.call(f.querySelectorAll('input'),function(i){i.disabled=false;});
    });
  }
  function correggi(){
    var tot=0,vuote=0,parti={};
    pulisci();
    dom.forEach(function(f){
      var g=f.getAttribute('data-giusta'),p=f.getAttribute('data-parte'),s=f.querySelector('input:checked'),ok=!!s&&s.value===g;
      var giusta=f.querySelector('input[value="'+g+'"]').parentNode,q=f.querySelector('.q-esito');
      parti[p]=parti[p]||[0,0];parti[p][1]++;
      if(ok){tot++;parti[p][0]++;}
      if(!s)vuote++;
      f.classList.add(ok?'giusta':'sbagliata');
      giusta.classList.add('la-giusta');
      if(s&&!ok)s.parentNode.classList.add('la-sbagliata');
      q.textContent=ok?T.giusto:((s?T.sbagliato:T.vuota)+' '+T.risposta.replace('{x}',giusta.textContent.trim()));
      q.hidden=false;f.querySelector('.q-spieg').hidden=false;
      [].forEach.call(f.querySelectorAll('input'),function(i){i.disabled=true;});
    });
    esito.textContent='';
    esito.appendChild(el('h3',T.punteggio.replace('{n}',tot).replace('{tot}',dom.length)));
    var ul=document.createElement('ul');
    Object.keys(parti).sort().forEach(function(p){ul.appendChild(el('li',T.parti[p]+': '+T.su.replace('{n}',parti[p][0]).replace('{tot}',parti[p][1])));});
    esito.appendChild(ul);
    if(vuote)esito.appendChild(el('p',vuote===1?T.vuote1:T.vuote.replace('{n}',vuote)));
    esito.appendChild(el('p',tot===dom.length?T.tutte:T.rileggi));
    esito.appendChild(el('p',T.nota));
    esito.hidden=false;bC.hidden=true;bR.hidden=false;
    try{esito.focus({preventScroll:true});esito.scrollIntoView({block:'center'});}catch(e){esito.focus();}
  }
  function rifai(){
    pulisci();
    dom.forEach(function(f){[].forEach.call(f.querySelectorAll('input'),function(i){i.checked=false;});});
    esito.hidden=true;esito.textContent='';bR.hidden=true;bC.hidden=false;
    try{box.scrollIntoView({block:'start'});}catch(e){}
  }
  bC.addEventListener('click',correggi);bR.addEventListener('click',rifai);
  /* contaparole della scrittura: conta e basta, il testo non esce dal browser */
  var cp=document.getElementById('prova-scrittura');
  if(cp){
    var area=cp.querySelector('textarea'),num=cp.querySelector('.cp-numero'),msg=cp.querySelector('.conta-esito'),
        min=+cp.getAttribute('data-min'),max=+cp.getAttribute('data-max');
    var lim=function(t){return t.replace('{min}',min).replace('{max}',max);};
    area.addEventListener('input',function(){
      var t=area.value.trim(),n=t?t.split(/\\s+/).length:0;
      num.textContent=n;msg.classList.remove('si','no');
      if(!n){msg.textContent=lim(T.cp_vuoto);}
      else if(n<min){msg.textContent=min-n===1?T.cp_sotto1:T.cp_sotto.replace('{n}',min-n);msg.classList.add('no');}
      else if(n>max){msg.textContent=n-max===1?T.cp_sopra1:T.cp_sopra.replace('{n}',n-max);msg.classList.add('no');}
      else{msg.textContent=lim(T.cp_ok);msg.classList.add('si');}
    });
  }
})();
"""


def _domanda(n, parte, legenda, opzioni, giusta, spiegazione, colonna=False):
    """Una domanda chiusa: fieldset con i pulsanti di scelta; esito e spiegazione nascosti fino alla correzione."""
    voci = "".join(f'<label><input type="radio" name="d{n}" value="{v}">{escape(t)}</label>' for v, t in opzioni)
    return (f'<fieldset data-giusta="{giusta}" data-parte="{parte}"><legend>{legenda}</legend>'
            f'<div class="opz{" col" if colonna else ""}">{voci}</div>'
            f'<p class="q-esito" hidden></p><p class="q-spieg" hidden>{escape(spiegazione)}</p></fieldset>')


def domande_html():
    """Le tre parti chiuse, con la numerazione continua da 1 a 24. Restituisce (parte1, parte2, parte3, numero di domande)."""
    n = 0
    p1 = []
    for q, opz, g, sp in SCELTA:
        n += 1
        p1.append(_domanda(n, "1", f"{n}. {escape(q)}", [(l, f"{l}) {t}") for l, t in zip("abc", opz)], g, sp, colonna=True))
    p2 = []
    for frase, vero, sp in VERO_FALSO:
        n += 1
        p2.append(_domanda(n, "2", f"{n}. {escape(frase)}", [("v", "Vero"), ("f", "Falso")], "v" if vero else "f", sp))
    p3 = []
    primo_spazio = n + 1
    for i, (opz, g, sp) in enumerate(SPAZI, 1):
        n += 1
        p3.append(_domanda(n, "3", f"Spazio {n}", list(zip("abc", opz)), g, sp))
    return "".join(p1), "".join(p2), "".join(p3), primo_spazio, n


def controlli_dati():
    """Formato dichiarato nella pagina = formato dei dati: 6 + 12 + 6 domande, una sola risposta giusta, spazi tutti nel testo."""
    if (len(SCELTA), len(VERO_FALSO), len(SPAZI)) != (6, 12, 6):
        raise SystemExit("prova B1 online: le parti chiuse devono avere 6, 12 e 6 domande")
    for _, opz, g, _ in SCELTA:
        if len(opz) != 3 or len(set(opz)) != 3 or g not in "abc":
            raise SystemExit("prova B1 online: una domanda a scelta multipla non ha 3 opzioni diverse o una risposta valida")
    for opz, g, _ in SPAZI:
        if len(opz) != 3 or len(set(opz)) != 3 or g not in "abc":
            raise SystemExit("prova B1 online: uno spazio non ha 3 opzioni diverse o una risposta valida")
    testo = " ".join(EMAIL)
    if any(testo.count("{%d}" % i) != 1 for i in range(1, len(SPAZI) + 1)):
        raise SystemExit("prova B1 online: ogni spazio deve comparire una volta sola nell'email")


def pagina(G):
    controlli_dati()
    ic = G.ic
    cils = G.ES["CILS"]
    prove = {p["nome"]: p for p in cils["prove"]}
    compito = cils["scrittura"]["compiti"][0]
    letto = G.il_data(G.v_esempi(cils))
    p1, p2, p3, primo_spazio, n_dom = domande_html()

    qui = {
        "Ascolto": f'No: per questa prova non abbiamo un audio. Al suo posto c\'è un dialogo da leggere con {len(SCELTA)} domande a scelta multipla (parte 1). '
                   'Per l\'ascolto usa <a href="../esempi/ascolto/">gli audio ufficiali degli enti</a>.',
        "Lettura e grammatica": f'Sì, con lo stesso tipo di prove: {len(VERO_FALSO)} frasi vero/falso (parte 2) e un testo da completare con {len(SPAZI)} spazi (parte 3).',
        "Scrittura": f'Sì: due tracce per un\'email di {compito["min"]}-{compito["max"]} parole e il contaparole (parte 4). L\'email non viene corretta: la controlli tu con i criteri ufficiali.',
        "Orale": "Solo la traccia: una presentazione e un dialogo da provare ad alta voce (parte 5).",
    }
    righe = "".join(
        f'<tr><td><strong>{escape(p["nome"])}</strong></td><td data-l="All\'esame CILS B1 Cittadinanza">{escape(p["cosa"])} '
        f'<span class="small">({escape(p["tempo"])}, fino a {escape(p["punti"])} punti)</span></td>'
        f'<td data-l="In questa prova">{qui[p["nome"]]}</td></tr>' for p in cils["prove"])
    tabella = ('<div class="tab-wrap ris-tab"><table class="conf"><thead><tr><th scope="col">Prova</th><th scope="col">All\'esame CILS B1 Cittadinanza</th>'
               f'<th scope="col">In questa prova</th></tr></thead><tbody>{righe}</tbody></table></div>')

    dialogo = "".join(f"<p><b>{escape(chi)}:</b> {escape(frase)}</p>" for chi, frase in DIALOGO)
    articolo = "".join(f"<p>{escape(par)}</p>" for par in ARTICOLO)
    email = "".join("<p>" + escape(par).format(*[""] + [f'<span class="spazio">({primo_spazio + i}) ______</span>' for i in range(len(SPAZI))]) + "</p>"
                    for par in EMAIL)
    tracce = "".join(f"<li><strong>Traccia {l}.</strong> {escape(t)}</li>" for l, t in zip("AB", TRACCE_SCRITTURA))
    criteri = "".join(f"<li><span><strong>{escape(c)}</strong>: {escape(p)}</span></li>" for c, p in cils["scrittura"]["criteri"])
    orale_domande = "".join(f"<li>{escape(d)}</li>" for d in ORALE_DOMANDE)

    faq = [
        ("Questa prova B1 online è ufficiale?",
         "No. L'abbiamo scritta noi di EsameB1 per farti esercitare: i testi e le domande sono nostri e non vengono dagli enti certificatori. "
         "Segue il modello dell'esame CILS B1 Cittadinanza, descritto nel sillabo e nei criteri di valutazione dell'Università per Stranieri di Siena. "
         "Le prove d'esempio ufficiali, con audio e chiavi, sono nella nostra pagina «Prove d'esempio»."),
        ("Il punteggio di questa prova vale come quello dell'esame?",
         f"No. Qui contiamo le risposte giuste su {n_dom} domande: 1 punto per ogni risposta giusta. All'esame CILS B1 Cittadinanza funziona così. " + G.RISULTATI["enti"]["CILS"]["voci"]["punteggio"]["testo"]),
        ("Perché non c'è la prova di ascolto?",
         f"Perché per questa prova non abbiamo un audio. Al posto dell'ascolto c'è un dialogo da leggere, con {len(SCELTA)} domande a scelta multipla. "
         "Per allenare l'ascolto usa gli audio MP3 ufficiali degli enti: li trovi nella nostra pagina sull'ascolto."),
        ("La mia email viene corretta?",
         f"No. Il contaparole conta solo le parole: per l'email del CILS B1 Cittadinanza ne servono da {compito['min']} a {compito['max']}. "
         "Il testo resta nel tuo browser: non lo salviamo e non lo riceviamo. Per controllarlo usa i criteri ufficiali scritti sotto le tracce."),
        ("Devo registrarmi o pagare per fare la prova?",
         "No. La prova è gratis e non serve registrarsi. Le risposte vengono corrette nel tuo browser e non vengono salvate: se ricarichi la pagina, la prova ricomincia."),
    ]
    jsonld, faq_html = G.faq_html_e_jsonld(faq)
    fonti_struttura = G.link_fonti(cils["fonti_struttura"])

    corpo = f"""<section class="hero">
{G.briciole(("EsameB1", "../"), ("Prova B1 online", None))}
<span class="occhiello">{ic("matita")}Prova scritta da noi · gratis · non ufficiale</span>
<h1>Prova B1 online gratis per la cittadinanza, con correzione automatica</h1>
<p class="lead">Una prova completa di lettura, grammatica e scrittura, scritta da noi di {G.NOME} sul modello dell'esame CILS B1 Cittadinanza.
Rispondi alle {n_dom} domande, premi «Correggi la prova» e vedi subito il punteggio, con una spiegazione per ogni risposta. Non serve registrarsi.</p>
<div class="azioni"><a class="btn" href="#prova">{ic("matita")}Comincia la prova</a><a class="btn btn-2" href="../esempi/">{ic("libro")}Prove d'esempio ufficiali</a></div>
</section>
{G.avviso('Questa prova è nostra: <strong>non è un esame ufficiale</strong> e non viene dall\'Università per Stranieri di Siena né dagli altri enti. '
          'I testi e le domande li abbiamo scritti noi, per farti esercitare. Le prove d\'esempio ufficiali, con audio e chiavi, sono nella pagina <a href="../esempi/">Prove d\'esempio</a>.')}
<section>
<h2 id="formato">{ic("lista")}Com'è l'esame vero e che cosa trovi qui</h2>
<p>L'esame CILS B1 Cittadinanza ha quattro prove. Qui trovi quelle che si possono fare e correggere al computer o sul telefono.</p>
{tabella}
<p>All'esame, per le due prove di lettura e grammatica hai {escape(prove["Lettura e grammatica"]["tempo"].replace(" min", " minuti"))} e per la scrittura altri {escape(prove["Scrittura"]["tempo"].replace(" min", " minuti"))}.
Se vuoi allenarti con il tempo, usa il <a href="../esempi/simulazione/#cronometro">cronometro della simulazione</a>.</p>
<div class="fonte">{ic("doc")}<span>Fonti per la struttura dell'esame: {fonti_struttura} · controllate {letto}</span></div>
</section>
<section class="prova" id="prova" data-testi="{escape(json.dumps(TESTI, ensure_ascii=False))}">
<style>{CSS_PROVA}</style>
<h2>{ic("matita")}La prova</h2>
<p>Scegli una risposta per ogni domanda. Puoi cambiare risposta fino a quando premi «Correggi la prova», in fondo alla parte 3.</p>
<noscript><p class="small">La correzione automatica funziona con JavaScript attivo.</p></noscript>
<h3 id="parte-1">Parte 1 · Un dialogo da leggere</h3>
<p>Leggi la telefonata. Poi, per ogni domanda, scegli la risposta giusta: a, b o c.</p>
<div class="testo-prova"><p class="tit">{escape(DIALOGO_TITOLO)}</p>{dialogo}</div>
{p1}
<h3 id="parte-2">Parte 2 · Lettura: vero o falso</h3>
<p>Leggi l'articolo. Poi, per ogni frase, scegli «Vero» se la frase dice una cosa scritta nel testo, «Falso» se dice una cosa diversa.</p>
<div class="testo-prova"><p class="tit">{escape(ARTICOLO_TITOLO)}</p>{articolo}</div>
{p2}
<h3 id="parte-3">Parte 3 · Grammatica e lessico: completa l'email</h3>
<p>Nell'email mancano {len(SPAZI)} parole. Per ogni spazio scegli la parola giusta.</p>
<div class="testo-prova"><p class="tit">Oggetto: {escape(EMAIL_OGGETTO)}</p>{email}</div>
{p3}
<div class="azioni"><button class="btn" type="button" data-azione="correggi">{ic("ok")}Correggi la prova</button><button class="btn btn-2" type="button" data-azione="rifai" hidden>Rifai la prova</button></div>
<div class="prova-esito" id="prova-esito" tabindex="-1" role="status" hidden></div>
</section>
<!--pass-->
<section>
<h2 id="parte-4">{ic("matita")}Parte 4 · Scrittura: un'email di {compito["min"]}-{compito["max"]} parole</h2>
<p><strong>All'esame:</strong> {escape(prove["Scrittura"]["cosa"])}</p>
<p><strong>Qui:</strong> scegli una delle due tracce e scrivi la tua email. Le tracce le abbiamo scritte noi.</p>
<ul class="tracce">{tracce}</ul>
<div class="card contaparole form" id="prova-scrittura" data-min="{compito["min"]}" data-max="{compito["max"]}">
<label>La tua email<textarea rows="9" spellcheck="false" autocomplete="off"></textarea></label>
<p class="cp-riga"><span class="cp-numero" aria-live="polite">0</span> <span>parole</span></p>
<p class="conta-esito" aria-live="polite">{escape(TESTI["cp_vuoto"].replace("{min}", str(compito["min"])).replace("{max}", str(compito["max"])))}</p>
<p class="small">Il contaparole conta solo le parole. Il testo resta nel tuo browser: non lo salviamo e non lo riceviamo.</p>
</div>
<h3>Controlla la tua email con i criteri ufficiali</h3>
<p>Questa parte non viene corretta in automatico. All'esame la scrittura vale {escape(cils["scrittura"]["punti"].split(" (")[0])}, divisi così:</p>
<ul class="cifre" style="flex-direction:column;align-items:flex-start;gap:8px">{criteri}</ul>
<p>Rileggi il testo e chiediti: ho fatto tutto quello che chiede la traccia? Ho cominciato e finito l'email con un saluto adatto alla persona a cui scrivo? Un'altra persona capisce che cosa voglio?</p>
<div class="fonte">{ic("doc")}<span>Fonti: {G.link_fonti(cils["scrittura"]["fonti"])} · controllate {letto}</span></div>
<p><a href="../esempi/prova-scritta/">{ic("matita")} La prova scritta dei 4 esami: tracce ufficiali, parole e criteri</a></p>
</section>
<section>
<h2 id="parte-5">{ic("voce")}Parte 5 · Orale: la traccia</h2>
<p><strong>All'esame:</strong> {escape(prove["Orale"]["cosa"])}</p>
<p><strong>Qui:</strong> non possiamo ascoltarti. Prova ad alta voce, meglio se con un'altra persona. Anche questa traccia l'abbiamo scritta noi.</p>
<h3>Presentazione (circa 1 minuto)</h3>
<p>Parla di te. Puoi partire da due o tre di queste domande:</p>
<ul>{orale_domande}</ul>
<h3>Dialogo</h3>
<p>{escape(ORALE_DIALOGO)}</p>
<p><a href="../esempi/prova-orale/">{ic("voce")} La prova orale: le tracce e i file ufficiali, parte per parte</a></p>
</section>
<section>
<h2 id="punteggio">{ic("ok")}Come contiamo il punteggio</h2>
<p>Ogni risposta giusta vale 1 punto; una risposta sbagliata o lasciata vuota vale 0. In tutto sono {n_dom} punti: {len(SCELTA)} per il dialogo,
{len(VERO_FALSO)} per il vero/falso e {len(SPAZI)} per il testo da completare. La scrittura e l'orale non entrano nel punteggio.</p>
<p>Non scriviamo «promosso» o «bocciato», perché il nostro punteggio non è quello dell'esame. All'esame CILS B1 Cittadinanza funziona così. {escape(G.RISULTATI["enti"]["CILS"]["voci"]["punteggio"]["testo"])}</p>
{G.fonte_risultati("CILS", "punteggio")}
</section>
<section>
<h2 id="domande">{ic("info")}Domande frequenti</h2>
{faq_html}
</section>
<section>
<h2>{ic("libro")}Continua a prepararti</h2>
<div class="altre"><a href="../esempi/cils/">Prova d'esempio ufficiale CILS B1 Cittadinanza</a><a href="../esempi/">Le prove ufficiali dei 4 enti</a><a href="../esempi/ascolto/">L'ascolto, con gli audio ufficiali</a><a href="../esempi/confronto/">I 4 esami a confronto</a><a href="../#date">Le prossime date d'esame</a></div>
</section>
{G.riquadro_libro("../").replace("clic/libro-esempi", "clic/" + CLIC_LIBRO)}
<script>{JS_PROVA}</script>"""
    G.pagina(f"{PERCORSO}index.html",
             G.titolo_pagina("Prova B1 cittadinanza online gratis, con correzione automatica", "Prova B1 cittadinanza online gratis con correzione"),
             G.descrizione_pagina(f"Prova B1 online gratis scritta da EsameB1 sul modello del CILS B1 Cittadinanza: {n_dom} domande con correzione automatica. "
                                  "Non è un esame ufficiale."), corpo, jsonld)


def genera(G):
    pagina(G)
    return [PERCORSO]


def controlli(G):
    """La pagina dice che la prova è nostra, ha le 24 domande con una risposta giusta ciascuna, un solo riquadro del Pass con
    l'etichetta dei clic e il modulo «avvisami» con fonte=pass; nessun link ai file degli enti dentro la prova."""
    import re
    h = (G.SITO / PERCORSO / "index.html").read_text(encoding="utf-8")
    dom = re.findall(r'<fieldset data-giusta="([abcvf])" data-parte="([123])">(.*?)</fieldset>', h, re.S)
    if len(dom) != 24 or any(f'value="{g}"' not in corpo for g, _, corpo in dom):
        raise SystemExit("prova B1 online: servono 24 domande, ognuna con la sua risposta giusta tra le opzioni")
    if "non è un esame ufficiale" not in h or h.count('id="pass"') != 1:
        raise SystemExit("prova B1 online: manca l'avviso «non è un esame ufficiale» o il riquadro del Pass non è uno solo")
    prova = h[h.find('<section class="prova"'):h.find('id="prova-esito"')]
    if "unistrasi.it" in prova or "unistrapg.it" in prova or "uniroma3.it" in prova or "dante.global" in prova:
        raise SystemExit("prova B1 online: dentro la prova non devono esserci link agli enti")
