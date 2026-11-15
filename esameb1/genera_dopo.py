"""Pagine «dopo l'esame» e prove d'esempio A2 e B2 di EsameB1 (15/11/2026).
Candidati n. 1 e n. 2 di studio-business/intelaiatura/fronti-2026-11-14-nostri-dati.md.

    /dopo-esame/                 indice: certificato, tempi dei risultati sessione per sessione, cosa fare se non superi
    /dopo-esame/<ente>/          una pagina per ente (cils, celi, plida, cert-it): certificato, validità, errori, recupero
    /dopo-esame/non-superato/    esame non superato: cosa si rifà con ogni ente
    /esempi/a2/  /esempi/b2/     prove d'esempio ufficiali di livello A2 e B2 (pagine e file degli enti)

Le pagine /risultati/<ente>/ (30/10/2026) restano la guida a «dove vedo il risultato»: queste pagine partono da lì e vanno avanti
(certificato, validità, recupero). Solo fatti scritti dagli enti: ogni testo tra «» è una frase di dati/dopo_esame.json presa con
Q() parola per parola (ricontrollata da raccolta/dopo_esame.py). Quello che l'ente non scrive è elencato in «Cosa non è scritto».
Le date «circa 3 mesi dopo» e «90 giorni lavorativi dopo» sono un nostro calcolo sulla regola scritta dall'ente e la pagina lo dice.
Le ricerche misurate sono in dati/parole_dopo_esame.json. Chiamato da main() di genera.py: genera(G, prossime) e controlli(G)."""
import calendar
import json
import re
from datetime import timedelta
from html import escape, unescape

D = None       # dati/dopo_esame.json
PAROLE = None  # dati/parole_dopo_esame.json
RICERCHE = {}  # pagina → ricerche misurate usate nelle domande frequenti
ORDINE = ["CILS", "CELI", "PLIDA", "CERT.IT"]
NOTA = ("Informazioni, non consulenza: questa pagina riporta quello che gli enti scrivono nelle loro pagine e nei loro documenti ufficiali. "
        "Per il tuo esame decide l'ente o il centro d'esame; per la domanda di cittadinanza decide la Prefettura.")


# ---------------------------------------------------------------- strumenti
def Q(k, inizio):
    """Frase citata parola per parola dalla fonte k: quella che comincia con «inizio». Se non c'è più, la generazione si ferma."""
    trovate = [c["testo"] for c in D["citazioni"] if c["fonte"] == k and c["testo"].lower().startswith(inizio.lower())]
    if len(trovate) != 1:
        raise SystemExit(f"genera_dopo: citazione di «{k}» che comincia con «{inizio}»: trovate {len(trovate)}")
    return "«" + escape(trovate[0]) + "»"


def A(k, testo=None):
    f = D["fonti"][k]
    return f'<a href="{escape(f["url"])}" rel="noopener">{escape(testo or f["nome"])}</a>'


def fonte(G, *chiavi):
    v = G.data_breve(D["verificato_il"])
    una = len(chiavi) == 1
    browser = " (pagina letta con un browser: il testo compare dopo il caricamento)" if any(D["fonti"][k].get("browser") for k in chiavi) else ""
    return (f'<div class="fonte">{G.ic("doc")}<span>{"Fonte" if una else "Fonti"}: {" · ".join(A(k) for k in chiavi)} · '
            f'{"letta" if una else "lette"} il {v}{browser}</span></div>')


def voce(G, titolo, testo, *chiavi):
    return f'<li><div><strong>{titolo}</strong><p>{testo}</p>{fonte(G, *chiavi)}</div></li>'


def scheda(G, icona, titolo, testo):
    return f'<div class="fatto"><div class="f-et">{G.ic(icona)}<span>{titolo}</span></div><p>{testo}</p></div>'


def faq(G, pagina, lista):
    """lista: (domanda, risposta, ricerca misurata o None). JSON-LD = testo visibile."""
    RICERCHE[pagina] = [r for *_, r in lista if r]
    return G.faq_html_e_jsonld([(q, a) for q, a, _ in lista])


def piu_mesi(x, n):
    m = x.month - 1 + n
    anno, mese = x.year + m // 12, m % 12 + 1
    return x.replace(year=anno, month=mese, day=min(x.day, calendar.monthrange(anno, mese)[1]))


def piu_lavorativi(x, n):
    while n:
        x += timedelta(days=1)
        if x.weekday() < 5:
            n -= 1
    return x


def data_it(G, x):
    return f"{x.day} {G.MESI[x.month - 1]} {x.year}"


def attesa(G, s):
    """(testo per la colonna «quando aspettarsi il risultato», già passato?) secondo la regola scritta dall'ente. None se l'ente non la scrive."""
    x = G.d(s["data"])
    if s["ente"] == "CILS":
        quando = piu_mesi(x, 3)
        return f"intorno al {data_it(G, quando)}", quando <= G.OGGI
    if s["ente"] == "CELI":
        quando = piu_lavorativi(x, 90)
        return f"intorno al {data_it(G, quando)} o più tardi", quando <= G.OGGI
    return None, None


def sessioni_vicine(G, sigla=None):
    """Sessioni degli ultimi 8 mesi e dei prossimi 4: quelle di cui si aspetta o si è appena avuto il risultato."""
    da, a = G.OGGI - timedelta(days=245), G.OGGI + timedelta(days=125)
    return sorted((s for s in G.sessioni if da <= G.d(s["data"]) <= a and (sigla is None or s["ente"] == sigla)),
                  key=lambda s: (s["data"], ORDINE.index(s["ente"])))


def tabella_sessioni(G, sigla=None):
    righe = []
    for s in sessioni_vicine(G, sigla):
        testo, passato = attesa(G, s)
        fatto = G.d(s["data"]) < G.OGGI
        if testo is None:
            quando = '<span class="small">l\'ente non scrive i tempi: chiedi al centro d\'esame</span>'
        elif passato:
            quando = f"{testo}: il tempo scritto dall'ente è passato. Se non vedi il risultato, chiedi al centro d'esame"
        else:
            quando = testo
        ente = f"<td>{G.eb(s['ente'])}</td>" if sigla is None else ""
        righe.append(f'<tr>{ente}<td data-l="Sessione"><strong>{G.data_breve(s["data"])}</strong>{"" if fatto else " (non ancora svolta)"}</td>'
                     f'<td data-l="Esami">{escape(", ".join(s.get("esami") or []))}</td><td data-l="Risultato (nostro calcolo)">{quando}</td></tr>')
    testa = ('<th scope="col">Ente</th>' if sigla is None else "") + ('<th scope="col">Sessione</th><th scope="col">Esami</th>'
                                                                       '<th scope="col">Quando aspettarsi il risultato (nostro calcolo)</th>')
    return f'<div class="tab-wrap ris-tab"><table class="conf"><thead><tr>{testa}</tr></thead><tbody>{"".join(righe)}</tbody></table></div>'


def nota_calcolo(G, sigla=None):
    parti = []
    if sigla in (None, "CILS"):
        parti.append(f"CILS: la data è il giorno dell'esame più 3 mesi, perché la pagina ufficiale scrive {Q('cils_risultati', 'I risultati degli esami saranno')}")
    if sigla in (None, "CELI"):
        parti.append("CELI: la data è il giorno dell'esame più 90 giorni lavorativi (senza sabati e domeniche, feste non tolte). Il Regolamento conta i giorni "
                     f"da quando le prove arrivano a Perugia, non dal giorno dell'esame, quindi il risultato può arrivare più tardi di questa data: {Q('celi_regolamento', 'Il CVCL provvede')}")
    if sigla in (None, "PLIDA", "CERT.IT"):
        chi = "PLIDA e CERT.IT" if sigla is None else sigla
        parti.append(f"{chi}: nelle pagine ufficiali lette non c'è un tempo scritto, quindi non mettiamo date")
    return ('<p class="ris-nota">Non sono date ufficiali: gli enti non pubblicano una data dei risultati per ogni sessione. ' + " ".join(x if x.endswith(".»") else x + "." for x in parti) + "</p>")


# ---------------------------------------------------------------- contenuti per ente
def contenuti(G):
    """Per ogni ente: titoli, risposta in alto, schede, sezioni (liste di voci con frasi citate), cosa non è scritto, domande frequenti."""
    mail_cils = '<a href="mailto:trasparenzacertificazioni@unistrasi.it">trasparenzacertificazioni@unistrasi.it</a>'
    mail_celi = '<a href="mailto:certificazione@unistrapg.it">certificazione@unistrapg.it</a>'
    mail_certit = '<a href="mailto:certificazioneitaliano@uniroma3.it">certificazioneitaliano@uniroma3.it</a>'
    return {
        "CILS": {
            "titolo": "Certificato CILS B1: ritiro, validità, se non superi",
            "h1": "Dopo l'esame CILS B1: il certificato, i tempi e cosa fare se non lo superi",
            "risposta": ("Il certificato CILS si ritira nella sede dove hai fatto l'esame e si può anche scaricare dalla pagina dei risultati; "
                         "secondo il Centro CILS dell'Università per Stranieri di Siena non ha scadenza. Il risultato esce circa 3 mesi dopo l'esame."),
            "fonte_risposta": ("cils_risultati", "cils_faq"),
            "desc": "Certificato CILS: si ritira nella sede d'esame, non ha scadenza. Risultati circa 3 mesi dopo. B1 Cittadinanza non superato: si rifà tutto l'esame.",
            "schede": [("doc", "Il certificato", "Si ritira nella sede dove hai fatto l'esame. Dalla pagina dei risultati puoi anche scaricarlo."),
                       ("scudo", "Scadenza", "Nessuna: per il Centro CILS oggi il certificato non ha scadenza."),
                       ("attenzione", "Se non superi", "B1 Cittadinanza: rifai tutto l'esame. B1 standard: recuperi solo le abilità non superate.")],
            "certificato": [
                voce(G, "Dove lo ritiri", f"Nella sede dove hai fatto l'esame. La pagina dei risultati scrive: {Q('cils_risultati', 'Per il ritiro')} "
                     f"Le Linee guida spiegano perché: {Q('cils_linee', 'I certificati vengono inviati')}", "cils_risultati", "cils_linee"),
                voce(G, "Puoi anche scaricarlo", "Entri nella pagina dei risultati con il numero di matricola e la data di nascita. "
                     f"Le FAQ del Centro CILS scrivono: {Q('cils_faq', 'Potrai così')}", "cils_faq"),
                voce(G, "Cosa c'è scritto sopra", "Il livello CILS, il tuo nome e cognome, la data di nascita e la cittadinanza. Poi i punti: "
                     f"{Q('cils_linee', 'Sono indicate altresì')}", "cils_linee"),
                voce(G, "Quando arriva", f"Dopo la valutazione, che il Centro CILS fa a Siena per tutte le sedi: {Q('cils_valutazione', 'I risultati degli esami CILS')} "
                     f"{Q('cils_risultati', 'Non si eseguono')} Le sedi ricevono i risultati per email ({Q('cils_linee', 'Alle sedi di esame')}) e il Centro "
                     f"non li dice al telefono ({Q('cils_linee', 'Non vengono comunicati')}).", "cils_valutazione", "cils_risultati", "cils_linee"),
                voce(G, "Se sul certificato c'è un errore nei tuoi dati", f"Le Linee guida prevedono un certificato nuovo: l'Università {Q('cils_linee', 'rilascia un nuovo certificato')}.",
                     "cils_linee"),
            ],
            "validita": (f"<p>Alla domanda sulla scadenza le FAQ del Centro CILS rispondono: {Q('cils_faq', 'Attualmente non ha')} Le Linee guida scrivono: "
                         f"{Q('cils_linee', 'La validità del certificato')}</p>"
                         f"<p>Per la cittadinanza serve il livello B1: nelle stesse FAQ il B1 è descritto come livello {Q('cils_faq', 'richiesto anche')}. "
                         "Il Centro CILS ha un esame fatto apposta, il CILS B1 Cittadinanza.</p>",
                         ("cils_faq", "cils_linee")),
            "non_superato": [
                voce(G, "CILS B1 Cittadinanza: si rifà tutto", f"La pagina ufficiale dell'esame scrive: {Q('cils_b1c', 'Per questo livello')} "
                     f"Se non superi un'abilità, {Q('cils_b1c', 'si dovrà sostenere')}. Sulla stessa pagina: {Q('cils_b1c', 'La tassa di esame')} "
                     "La pagina non indica uno sconto per chi ripete l'esame.", "cils_b1c"),
                voce(G, "CILS B1 standard: recuperi solo le abilità non superate", f"{Q('cils_valutazione', 'I candidati che non ottengono')} "
                     f"{Q('cils_valutazione', 'In questo attestato')} {Q('cils_valutazione', 'Entro 18 mesi')} "
                     f"{Q('cils_valutazione', 'L’esame di capitalizzazione')}", "cils_valutazione"),
                voce(G, "Attenzione: 18 mesi o un anno?", "La pagina web «La valutazione» dice 18 mesi. Le Linee guida CILS, un PDF senza data, dicono invece: "
                     f"{Q('cils_linee', 'Le abilità capitalizzate')} I due testi non coincidono: prima di aspettare più di un anno chiedi conferma alla tua sede. "
                     f"Per ogni abilità da rifare si paga: chi ripete {Q('cils_linee', 'deve versare')}; l'importo non è scritto.", "cils_valutazione", "cils_linee"),
                voce(G, "Vedere le tue prove o fare reclamo", f"Hai 30 giorni: per vedere le prove scrivi al Centro CILS {Q('cils_risultati', 'entro 30 giorni')}, "
                     f"all'indirizzo {mail_cils}, con la copia di un documento valido e il pagamento della tassa per i diritti di accesso. "
                     f"Per i reclami le Linee guida scrivono: {Q('cils_linee', 'I reclami relativi ai risultati')} "
                     "Per il ricorso le FAQ del Centro CILS indicano lo stesso indirizzo email.", "cils_risultati", "cils_linee", "cils_faq"),
            ],
            "non_scritto": ["quanti giorni passano tra il risultato online e l'arrivo del certificato nella sede",
                            "se un'altra persona può ritirare il certificato con una delega",
                            "come avere un duplicato se perdi il certificato",
                            "quanto costa rifare una sola abilità del B1 standard"],
            "faq": [
                ("Dove si ritira il certificato CILS?",
                 "Nella sede dove hai fatto l'esame: lo scrivono la pagina «Risultati degli esami» e le FAQ del Centro CILS. Dalla pagina dei risultati, "
                 "con numero di matricola e data di nascita, puoi anche scaricarlo.", "certificato cils"),
                ("Il certificato CILS ha una scadenza?",
                 "No. Le FAQ del Centro CILS scrivono che oggi il certificato non ha una scadenza e le Linee guida CILS che la sua validità è illimitata.", "certificazione cils"),
                ("Quando escono i risultati CILS della mia sessione?",
                 "Circa 3 mesi dopo il giorno dell'esame, secondo la pagina ufficiale. Il Centro CILS non pubblica una data per ogni sessione e non fa valutazioni anticipate. "
                 "Nella tabella di questa pagina trovi il conto dei 3 mesi per ogni sessione.", "risultati cils"),
                ("Ho superato solo alcune parti del CILS B1 Cittadinanza: posso rifare solo le altre?",
                 "No. Per il CILS B1 Cittadinanza la capitalizzazione non è consentita: si rifà tutto l'esame nella sessione successiva. "
                 "Il recupero delle sole abilità non superate vale per il CILS B1 standard.", "risultati esami cils b1 cittadinanza"),
                ("Come faccio reclamo sul risultato CILS?",
                 "Le Linee guida CILS danno 30 giorni dalla pubblicazione dei risultati sul sito o dal ricevimento del certificato. Le FAQ del Centro CILS scrivono che "
                 "per fare ricorso basta un'email a trasparenzacertificazioni@unistrasi.it. Per vedere le tue prove scrivi allo stesso indirizzo entro 30 giorni dalla "
                 "pubblicazione dei risultati, con nome e cognome, luogo e data di nascita, numero di matricola, la copia di un documento valido e il pagamento "
                 "della tassa per i diritti di accesso.", None),
            ],
        },
        "CELI": {
            "titolo": "Certificato CELI B1: digitale, validità, se non superi",
            "h1": "Dopo l'esame CELI B1: il certificato digitale, i tempi e cosa fare se non lo superi",
            "risposta": ("Il certificato CELI è digitale: il CVCL dell'Università per Stranieri di Perugia lo manda al centro d'esame, che lo consegna a te. "
                         "Non ha scadenza. Se ti serve prima, dall'area riservata scarichi un documento provvisorio."),
            "fonte_risposta": ("celi_regolamento", "celi_esami"),
            "desc": "Certificato CELI: digitale con QR code, consegnato dal centro d'esame, senza scadenza. Se non superi scritto o orale: un anno per rifarlo al 70%.",
            "schede": [("doc", "Il certificato", "È un PDF con QR code. Il CVCL lo manda al centro d'esame, che lo dà a te."),
                       ("scudo", "Scadenza", "Nessuna: il CVCL scrive che i certificati CELI non hanno scadenza."),
                       ("attenzione", "Se non superi", "Entro un anno rifai solo lo scritto o solo l'orale, pagando il 70% della tassa.")],
            "certificato": [
                voce(G, "Come lo ricevi", f"Dal centro dove hai fatto l'esame. Il Regolamento scrive: {Q('celi_regolamento', 'I certificati in formato')} "
                     f"La pagina delle iscrizioni lo ripete: il CVCL {Q('celi_iscrizione', 'provvederà ad inviare')}.", "celi_regolamento", "celi_iscrizione"),
                voce(G, "È digitale, non di carta", f"Una dichiarazione firmata del CVCL attesta che il Centro {Q('celi_digitali', 'a partire dal mese')} "
                     f"e che questi certificati, {Q('celi_digitali', 'completi di QR')}. Se un ufficio ti chiede l'originale di carta, puoi mostrare questa dichiarazione.",
                     "celi_digitali"),
                voce(G, "Se ti serve prima: il documento provvisorio", f"{Q('celi_regolamento', 'I candidati che prima')} "
                     "Il Regolamento non dice se questo documento basta per la domanda di cittadinanza: chiedilo alla Prefettura.", "celi_regolamento"),
                voce(G, "Come si legge il risultato", f"Con una lettera. {Q('celi_regolamento', 'Tre sono i gradi')} {Q('celi_regolamento', 'I gradi D')} "
                     f"I punti di ogni parte li ha il centro: {Q('celi_regolamento', 'I risultati sono comunque')}", "celi_regolamento"),
                voce(G, "Se sul certificato c'è un errore nei tuoi dati", "I dati vengono dal foglio che controlli il giorno dell'esame. Per correggerli: "
                     f"{Q('celi_regolamento', 'Richieste di correzione')}", "celi_regolamento"),
            ],
            "validita": (f"<p>La pagina «Esami CELI» del CVCL scrive: {Q('celi_esami', 'i Certificati CELI')}.</p>"
                         f"<p>Per la cittadinanza l'esame è il CELI 2 i cittadinanza (B1). Tra gli scopi degli esami CELI i il CVCL mette: "
                         f"{Q('celi_immigrati', 'rappresentare un titolo')}, e nella stessa frase cita {Q('celi_immigrati', 'DLeg. 113/2018')}.</p>",
                         ("celi_esami", "celi_immigrati")),
            "non_superato": [
                voce(G, "Un anno per rifare solo la parte non superata", "L'esame ha due parti, scritto e orale. Chi ne supera una sola può "
                     f"{Q('celi_regolamento', 'capitalizzare per un anno')}.", "celi_regolamento"),
                voce(G, "Stesso livello e stesso tipo d'esame", f"{Q('celi_regolamento', 'Si specifica che')} "
                     "Per esempio: se hai fatto il CELI 2 i cittadinanza, rifai la parte mancante del CELI 2 i cittadinanza.", "celi_regolamento"),
                voce(G, "Quanto costa", "Il 70% della tassa intera. La tassa la comunica il centro: "
                     f"{Q('celi_iscrizione', 'Sarà cura del Centro')}", "celi_regolamento", "celi_iscrizione"),
                voce(G, "Domande sul risultato", f"{Q('celi_regolamento', 'Il candidato può chiedere')} Indirizzo: {mail_celi}.", "celi_regolamento"),
            ],
            "non_scritto": ["quanti giorni passano tra il risultato e l'arrivo del certificato al centro d'esame",
                            "se il documento provvisorio basta per la domanda di cittadinanza",
                            "come riavere il certificato digitale se lo perdi",
                            "cosa succede se non superi né lo scritto né l'orale (il Regolamento parla solo di chi ne supera uno dei due)"],
            "faq": [
                ("Quando escono i risultati CELI B1 cittadinanza?",
                 "Circa 90 giorni lavorativi dopo che le prove arrivano al CVCL di Perugia, secondo il Regolamento degli esami CELI. "
                 "Il CVCL non pubblica una data per ogni sessione: nella tabella di questa pagina trovi il conto dei 90 giorni lavorativi dal giorno dell'esame.",
                 "celi b1 cittadinanza risultati"),
                ("Dove vedo i risultati CELI sul sito del CVCL?",
                 "Nell'area riservata ai candidati del sito del CVCL, con il numero di matricola e la data di nascita. "
                 "I punti di ogni parte dell'esame li trovi anche al centro dove hai fatto la prova.", "www cvcl it risultati"),
                ("Il certificato CELI è di carta?",
                 "No. Da settembre 2022 il CVCL rilascia i certificati solo in formato digitale (PDF) con un QR code per verificarli: "
                 "il CVCL dichiara che hanno lo stesso valore dei certificati di carta di prima.", None),
                ("Come si leggono i risultati CELI: cosa vogliono dire le lettere?",
                 "A (ottimo), B (buono) e C (sufficiente) vogliono dire esame superato e certificato; D (insufficiente) ed E (gravemente insufficiente) esame non superato. "
                 "Per i livelli A1 e A2 il risultato è solo positivo o negativo.", "risultati celi"),
                ("Il certificato CELI scade?",
                 "No: la pagina «Esami CELI» del CVCL scrive che i certificati CELI non hanno scadenza.", None),
                ("Ho superato lo scritto ma non l'orale del CELI: cosa rifaccio?",
                 "Solo l'orale, entro un anno, pagando il 70% della tassa intera. Vale anche al contrario (orale superato, scritto no). "
                 "Deve essere lo stesso livello e lo stesso tipo d'esame.", None),
            ],
        },
        "PLIDA": {
            "titolo": "Certificato PLIDA B1: scaricarlo, validità, recupero",
            "h1": "Dopo l'esame PLIDA B1: il certificato, il recupero delle abilità e cosa non è scritto",
            "risposta": ("Il certificato PLIDA lo scarichi tu, online, da certificazioneplida.dante.global con la tua email e la tua password. "
                         "La Società Dante Alighieri scrive che il PLIDA B1 è valido per chiedere la cittadinanza; i tempi dei risultati non sono scritti."),
            "fonte_risposta": ("plida_faq", "plida_istruzioni"),
            "desc": "Certificato PLIDA: si scarica online con email e password. Se non superi da 1 a 3 abilità le recuperi in 18 mesi. Tempi dei risultati: non scritti.",
            "schede": [("doc", "Il certificato", "Lo scarichi online dal tuo account, nel menu dei tuoi certificati PLIDA."),
                       ("scudo", "Scadenza", "Non è scritta nelle pagine e nei documenti PLIDA che abbiamo letto."),
                       ("attenzione", "Se non superi", "Da 1 a 3 abilità non superate: le recuperi nei 18 mesi successivi.")],
            "certificato": [
                voce(G, "Dove lo scarichi", f"Le FAQ della Società Dante Alighieri scrivono: {Q('plida_faq', 'Per visualizzare')} "
                     f"Le istruzioni avvertono: {Q('plida_istruzioni', 'ATTENZIONE')}", "plida_faq", "plida_istruzioni"),
                voce(G, "Come fai", f"Dopo l'accesso apri l'elenco dei tuoi esami: {Q('plida_istruzioni', 'qui ci sono')}. "
                     f"Per il certificato apri l'elenco dei tuoi certificati e {Q('plida_istruzioni', 'fai click')}.", "plida_istruzioni"),
                voce(G, "Serve l'email data al centro", f"{Q('plida_faq', 'Ricorda di comunicare')} Si entra con quella email: se non ricordi quale hai usato, chiedila al centro.",
                     "plida_faq", "plida_istruzioni"),
            ],
            "validita": (f"<p>Nelle FAQ, alla domanda su cosa fare per avere un certificato B1 per la cittadinanza, la Società Dante Alighieri scrive: "
                         f"{Q('plida_faq', 'Il certificato PLIDA B1')}</p>"
                         "<p>Una scadenza del certificato non è scritta nelle FAQ, nelle istruzioni e nel Quaderno delle specifiche che abbiamo letto: "
                         "non scriviamo che non scade, perché l'ente non lo scrive.</p>", ("plida_faq",)),
            "non_superato": [
                voce(G, "Per superare servono 18 punti su 30 in ogni abilità", f"{Q('plida_quaderno', 'Per superare l’esame')} "
                     "Le abilità sono quattro: Ascoltare, Leggere, Scrivere e Parlare.", "plida_quaderno"),
                voce(G, "Recuperi solo le abilità non superate, in 18 mesi", f"{Q('plida_quaderno', 'I candidati che non superano')}; "
                     f"{Q('plida_quaderno', 'i candidati possono tentare')}.", "plida_quaderno"),
                voce(G, "Anche in un altro centro", f"{Q('plida_quaderno', 'Le prove di recupero')}: {Q('plida_quaderno', 'sarà sufficiente')}.", "plida_quaderno"),
            ],
            "non_scritto": ["dopo quanto tempo escono i risultati e il certificato",
                            "se il certificato ha una scadenza",
                            "quanto costa il recupero di una o più abilità (il prezzo lo dà il centro d'esame)",
                            "cosa succede se non superi nessuna delle quattro abilità (il recupero è scritto per «una o più abilità, fino a tre»)"],
            "faq": [
                ("Come scarico il certificato dell'esame PLIDA?",
                 "Vai su certificazioneplida.dante.global, entra con l'email che hai dato al centro d'esame e con la tua password, apri l'elenco dei tuoi certificati PLIDA "
                 "e clicca sull'icona della stampante. Non è lo stesso indirizzo usato per l'iscrizione.", "esame plida"),
                ("Il PLIDA B1 vale per la cittadinanza italiana?",
                 "La Società Dante Alighieri scrive nelle sue FAQ che il certificato PLIDA B1 è valido per richiedere la cittadinanza.",
                 "certificato b1 italiano per cittadinanza"),
                ("Non ho superato una parte del PLIDA B1: devo rifare tutto?",
                 "No, se le abilità non superate sono da una a tre: le recuperi nei 18 mesi successivi, in tutte le sessioni del calendario PLIDA, anche più volte "
                 "e anche in un altro centro, con il tuo Codice personale.", None),
                ("Quando escono i risultati PLIDA?",
                 "Nelle FAQ, nelle istruzioni e nel Quaderno delle specifiche PLIDA che abbiamo letto non c'è un tempo scritto. Chiedilo al centro dove hai fatto l'esame.", None),
            ],
        },
        "CERT.IT": {
            "titolo": "Certificato CERT.IT B1 Roma Tre: cosa dice il sito",
            "h1": "Dopo l'esame CERT.IT B1 (Roma Tre): certificato, sezioni da ripetere e cosa non è scritto",
            "risposta": ("Il sito CERT.IT dell'Università Roma Tre non spiega come e quando ricevi il certificato B1: chiedilo alla sede d'esame o alla segreteria. "
                         "Scrive però le regole per superare l'esame e, per il B2, quando viene rilasciato il certificato."),
            "fonte_risposta": ("certit_b1", "certit_iscrizione"),
            "desc": "Certificato CERT.IT (Roma Tre): il sito non spiega tempi e consegna. Cosa scrive su punteggio, sezioni da ripetere e quote, e cosa chiedere alla sede.",
            "schede": [("doc", "Il certificato", "Tempi e consegna non sono scritti sul sito: chiedi alla sede dove hai fatto l'esame."),
                       ("scudo", "Scadenza", "Non è scritta nelle pagine CERT.IT che abbiamo letto."),
                       ("attenzione", "Se non superi", "Per il B1 il sito indica solo la quota dell'esame intero: chiedi alla sede.")],
            "certificato": [
                voce(G, "Cosa scrive il sito", "Nelle pagine lette (home, livelli A2, B1 e B2, iscrizione, presentazione, contatti) non c'è una pagina sui risultati "
                     "o sulla consegna del certificato B1. Per le sedi convenzionate chiedi alla sede; per l'esame fatto a Roma Tre scrivi alla segreteria: "
                     f"{mail_certit}.", "certit_b1", "certit_contatti"),
                voce(G, "Quando il certificato viene rilasciato (scritto per il B2)", f"Nella pagina del livello B2: {Q('certit_b2', 'Il certificato verrà')} "
                     "Nella pagina del B1 questa frase non c'è.", "certit_b2"),
            ],
            "validita": (f"<p>La pagina del livello B1 ricorda che per la cittadinanza serve una conoscenza dell'italiano non inferiore al B1 e che "
                         f"{Q('certit_b1', 'i richiedenti saranno tenuti')}. Nella presentazione, Roma Tre si descrive come "
                         f"{Q('certit_presentazione', 'ente certificatore')} e dell'Istruzione, Università e Ricerca.</p>"
                         "<p>Una scadenza del certificato non è scritta nelle pagine lette.</p>", ("certit_b1", "certit_presentazione")),
            "non_superato": [
                voce(G, "Per superare il B1", f"{Q('certit_b1', 'L’esame è superato')}", "certit_b1"),
                voce(G, "Ripetere una sola sezione: scritto solo per B2, C1 e C2", f"La pagina delle iscrizioni scrive: {Q('certit_iscrizione', 'Qui di seguito')} "
                     f"Per il B1 c'è solo la quota intera ({Q('certit_iscrizione', 'B1: 80')}); per il B2 ci sono anche le sezioni: {Q('certit_iscrizione', 'B2: 140')}. "
                     "Il sito non dice se nel B1 si può ripetere una sola parte: chiedilo alla sede.", "certit_iscrizione"),
                voce(G, "La regola scritta per il B2", f"{Q('certit_b2', 'Laddove non venissero')} Vale per il B2: per il B1 il sito non scrive una regola uguale.",
                     "certit_b2"),
                voce(G, "A chi scrivere", f"{Q('certit_iscrizione', 'Chi deve iscriversi')} {mail_certit}.", "certit_iscrizione", "certit_contatti"),
            ],
            "non_scritto": ["dove e quando si vedono i risultati",
                            "come e quando si riceve il certificato B1",
                            "se il certificato ha una scadenza",
                            "se nel B1 si può ripetere solo lo scritto o solo l'orale"],
            "faq": [
                ("Dove vedo i risultati dell'esame CERT.IT di Roma Tre?",
                 "Il sito CERT.IT non ha una pagina dei risultati. Chiedi alla sede dove hai fatto l'esame; se l'hai fatto a Roma Tre scrivi a certificazioneitaliano@uniroma3.it.", None),
                ("Con quale punteggio si supera il CERT.IT B1?",
                 "Con il 60% dei punti nelle sezioni Ascolto, Lettura e Produzione scritta (contate insieme) e il 60% dei punti nella Produzione orale.", None),
                ("Nel CERT.IT B1 posso ripetere una sola sezione?",
                 "Il sito non lo scrive. La pagina delle iscrizioni indica le quote per singole sezioni solo per B2, C1 e C2; per il B1 c'è solo la quota intera di 80 €. "
                 "Chiedi alla sede o alla segreteria.", None),
                ("Il certificato CERT.IT B1 vale per la cittadinanza?",
                 "La pagina del livello B1 di Roma Tre ricorda che chi chiede la cittadinanza consegna una certificazione di lingua italiana rilasciata dall'ente certificatore; "
                 "Roma Tre si presenta come ente certificatore riconosciuto dai Ministeri degli Affari Esteri e dell'Istruzione, Università e Ricerca.",
                 "certificato di lingua italiana b1 per cittadinanza"),
            ],
        },
    }


def slug(G, s):
    return G.SLUG_RISULTATI[s]


def altri_enti(G, s, rel=""):
    return "".join(f'<a href="{rel}{slug(G, x)}/">Dopo l\'esame {escape(x)}</a>' for x in ORDINE if x != s)


# ---------------------------------------------------------------- /dopo-esame/<ente>/
def pagina_ente(G, s, c, prossime):
    v = G.data_breve(D["verificato_il"])
    sl = slug(G, s)
    nome = escape(G.ENTE[s]["ente"])
    jsonld, faq_html = faq(G, f"dopo-esame/{sl}/", c["faq"])
    date_e = [x for x in prossime if x["ente"] == s]
    date_html = (G.lista_sessioni(date_e[:4], con_filtri=False) if date_e
                 else "<p>Nessuna data futura pubblicata dall'ente per ora. Controlliamo il calendario ufficiale ogni settimana.</p>")
    val_html, val_fonti = c["validita"]
    corpo = f"""<section class="hero">
{G.briciole(("EsameB1", "../../"), ("Dopo l'esame", "../"), (s, None))}
<span class="occhiello">{G.ic("doc")}{nome} · fonti lette il {v}</span>
<h1>{escape(c["h1"])}</h1>
<p class="lead">{escape(c["risposta"])} Fonti: {" · ".join(A(k) for k in c["fonte_risposta"])}, lette il {v}.</p>
<div class="azioni"><a class="btn" href="../../risultati/{sl}/">{G.ic("ok")}Dove vedere il risultato {escape(s)}</a><a class="btn btn-2" href="#non-superato">{G.ic("attenzione")}Se non hai superato</a></div>
</section>
<section class="ris-sez" aria-label="In breve"><div class="fatti">{"".join(scheda(G, i, t, escape(x)) for i, t, x in c["schede"])}</div></section>
<section>
<h2 id="sessioni">{G.ic("cal")}Sessione per sessione: quando aspettarsi il risultato {escape(s)}</h2>
{tabella_sessioni(G, s)}
{nota_calcolo(G, s)}
<p><a href="../../risultati/{sl}/">Risultati {escape(s)}: dove vederli, passo per passo</a></p>
</section>
<section>
<h2 id="certificato">{G.ic("doc")}Il certificato {escape(s)}: come lo ricevi</h2>
<ol class="passi">{"".join(c["certificato"])}</ol>
</section>
<section class="ris-sez">
<h2 id="validita">{G.ic("scudo")}Vale per la cittadinanza? Scade?</h2>
{val_html}
{fonte(G, *val_fonti)}
<p>Nella domanda di cittadinanza il certificato si allega insieme agli altri documenti: <a href="../../cittadinanza/">come si fa la domanda, prefettura per prefettura</a> ·
<a href="../../esonero-test-italiano/">quali titoli valgono e chi è esonerato</a>.</p>
</section>
<section>
<h2 id="non-superato">{G.ic("attenzione")}Se non hai superato l'esame {escape(s)}</h2>
<ol class="passi">{"".join(c["non_superato"])}</ol>
<p><a href="../non-superato/">Esame B1 non superato: le regole dei 4 enti a confronto</a> · <a href="../../esempi/{G.SLUG_ENTE[s]}/">Prova d'esempio {escape(s)} per esercitarti</a></p>
</section>
<section class="ris-sez">
<h2 id="non-scritto">{G.ic("info")}Cosa non è scritto nelle fonti {escape(s)}</h2>
<p>Abbiamo cercato queste informazioni nelle pagine e nei documenti ufficiali elencati in questa pagina e non le abbiamo trovate. Non le inventiamo: chiedile al centro d'esame.</p>
<ul>{"".join(f"<li>{escape(x[0].upper() + x[1:])}.</li>" for x in c["non_scritto"])}</ul>
</section>
<div class="due">
<section>
<h2 id="date">{G.ic("cal")}Devi rifare l'esame? Prossime date {escape(s)}</h2>
{date_html}
<p><a href="../../ente/{G.SLUG_ENTE[s]}/">{escape(G.NOME_RICERCA[s])}: tutte le date, il costo e le sedi</a></p>
</section>
<aside>{G.modulo()}</aside>
</div>
{G.riquadro_preparati("../../")}
<section>
<h2 id="domande">{G.ic("info")}Domande frequenti</h2>
{faq_html}
</section>
<section>
<p class="small">{NOTA}</p>
<h2>{G.ic("doc")}Dopo l'esame con gli altri enti</h2>
<div class="altre"><a href="../">Tutti gli enti</a>{altri_enti(G, s, "../")}<a href="../non-superato/">Esame non superato</a></div>
<h2>{G.ic("info")}Altre guide</h2>
{G.link_guide("../../")}
</section>"""
    G.pagina(f"dopo-esame/{sl}/index.html", G.titolo_pagina(c["titolo"]), G.descrizione_pagina(c["desc"]), corpo, jsonld)


# ---------------------------------------------------------------- /dopo-esame/
def riga_indice(G, s, c):
    cert, scad, non = (x for _, _, x in c["schede"])
    return (f'<tr><td>{G.eb(s)}<strong>{escape(G.RISULTATI["enti"][s]["esame"])}</strong><br><a class="ris-guida" href="{slug(G, s)}/">Dopo l\'esame {escape(s)} {G.ic("freccia")}</a></td>'
            f'<td data-l="Il certificato">{escape(cert)}</td><td data-l="Scadenza">{escape(scad)}</td><td data-l="Se non superi">{escape(non)}</td></tr>')


def pagina_indice(G, C, prossime):
    v = G.data_breve(D["verificato_il"])
    domande = [
        ("Dopo l'esame B1, quando arriva il certificato di italiano?",
         "Dipende dall'ente. CILS: il risultato esce circa 3 mesi dopo l'esame e il certificato si ritira nella sede. CELI: il risultato esce circa 90 giorni lavorativi dopo "
         "l'arrivo delle prove a Perugia e il certificato digitale passa dal centro d'esame. PLIDA: il certificato si scarica online, i tempi non sono scritti. "
         "CERT.IT: il sito non lo spiega.", "certificato b1 italiano"),
        ("Il certificato B1 di italiano scade?",
         "Il Centro CILS scrive che oggi il certificato non ha scadenza e il CVCL di Perugia che i certificati CELI non hanno scadenza. "
         "Per PLIDA e CERT.IT una scadenza non è scritta nelle pagine ufficiali che abbiamo letto.", "certificato b1"),
        ("Quale certificato di lingua italiana B1 serve per la cittadinanza?",
         "Un certificato di livello B1 di un ente certificatore riconosciuto. Gli enti di questa guida scrivono: CILS, il B1 è richiesto anche per la cittadinanza; "
         "CELI, il CELI 2 i cittadinanza è un titolo per gli obblighi di legge; PLIDA, il certificato B1 è valido per richiedere la cittadinanza. "
         "L'elenco dei titoli e degli esoneri è nella pagina sull'esonero.", "certificato di lingua italiana b1 per cittadinanza"),
        ("Dove vedo i risultati CILS e CELI?",
         "CILS: nella pagina dei risultati dell'Università per Stranieri di Siena, con matricola e data di nascita. CELI: nell'area riservata ai candidati del CVCL, "
         "con matricola e data di nascita. Le guide passo per passo sono nella sezione Risultati.", "esame cils risultati"),
        ("Se non supero l'esame B1 devo rifarlo tutto?",
         "CILS B1 Cittadinanza: sì. CELI: no, entro un anno rifai solo lo scritto o solo l'orale. PLIDA: no, entro 18 mesi recuperi da una a tre abilità. "
         "CERT.IT: per il B1 il sito non lo scrive.", None),
    ]
    jsonld, faq_html = faq(G, "dopo-esame/", domande)
    guide = "".join(f'<a href="{slug(G, s)}/">{G.ic("doc")}<span>Dopo l\'esame {escape(s)}<small>certificato, validità, recupero</small></span></a>' for s in ORDINE)
    corpo = f"""<section class="hero">
{G.briciole(("EsameB1", "../"), ("Dopo l'esame", None))}
<span class="occhiello">{G.ic("doc")}Fonti ufficiali degli enti · lette il {v}</span>
<h1>Dopo l'esame B1: il certificato di italiano, i tempi e cosa fare se non lo superi</h1>
<p class="lead">Il certificato CILS si ritira nella sede d'esame, il certificato CELI è digitale e arriva dal centro d'esame, il certificato PLIDA si scarica online;
il sito CERT.IT non spiega la consegna. CILS e CELI scrivono che il certificato non ha scadenza. Fonti: pagine e documenti ufficiali dei 4 enti, letti il {v}.</p>
<div class="azioni"><a class="btn" href="#enti">{G.ic("lista")}Ente per ente</a><a class="btn btn-2" href="non-superato/">{G.ic("attenzione")}Esame non superato</a></div>
</section>
<section>
<h2 id="enti">{G.ic("lista")}Certificato, scadenza e recupero: risposta rapida</h2>
<div class="tab-wrap ris-tab"><table class="conf"><thead><tr><th scope="col">Ente</th><th scope="col">Il certificato</th><th scope="col">Scadenza</th><th scope="col">Se non superi</th></tr></thead>
<tbody>{"".join(riga_indice(G, s, C[s]) for s in ORDINE)}</tbody></table></div>
<p class="small">Ogni riga viene dalle fonti citate nella pagina dell'ente. Dove l'ente non scrive un dato lo diciamo, senza metterne uno nostro.</p>
</section>
<section>
<h2 id="sessioni">{G.ic("cal")}Sessione per sessione: quando aspettarsi il risultato</h2>
<p>Le sessioni degli ultimi 8 mesi e dei prossimi 4, con il tempo scritto da ogni ente contato dal giorno dell'esame.</p>
{tabella_sessioni(G)}
{nota_calcolo(G)}
<p><a href="../risultati/">Risultati: dove vederli, ente per ente</a></p>
</section>
<section>
<h2 id="guide">{G.ic("info")}Le guide ente per ente</h2>
<div class="griglia link3">{guide}<a href="non-superato/">{G.ic("attenzione")}<span>Esame non superato<small>cosa si rifà con ogni ente</small></span></a></div>
</section>
<section class="ris-sez">
<h2 id="cittadinanza">{G.ic("edificio")}Con il certificato in mano: la domanda di cittadinanza</h2>
<p>Il certificato B1 è uno dei documenti della domanda. <a href="../cittadinanza/">Come si fa la domanda di cittadinanza, prefettura per prefettura</a> ·
<a href="../esonero-test-italiano/">quali titoli valgono e chi è esonerato dal B1</a> · <a href="../reddito-minimo-cittadinanza/">il reddito minimo</a> ·
<a href="../pratica-cittadinanza/">lo stato della pratica e il giuramento</a>.</p>
</section>
<div class="due">
<section>
<h2 id="date">{G.ic("cal")}Devi rifare l'esame? Le prossime date</h2>
{G.lista_sessioni(prossime[:6], con_filtri=False)}
<p><a href="../#date">Tutte le date</a></p>
</section>
<aside>{G.modulo()}</aside>
</div>
<section>
<h2 id="domande">{G.ic("info")}Domande frequenti</h2>
{faq_html}
</section>
<section>
<p class="small">{NOTA}</p>
<h2>{G.ic("info")}Altre guide</h2>
{G.link_guide("../")}
</section>"""
    G.pagina("dopo-esame/index.html", G.titolo_pagina("Dopo l'esame B1: certificato, tempi, se non lo superi"),
             G.descrizione_pagina("Certificato B1 di italiano: come si riceve con CILS, CELI, PLIDA e CERT.IT, se scade, quando escono i risultati di ogni sessione e cosa rifare."),
             corpo, jsonld)


# ---------------------------------------------------------------- /dopo-esame/non-superato/
def pagina_non_superato(G, C, prossime):
    v = G.data_breve(D["verificato_il"])
    righe = [
        ("CILS", "Tutto l'esame (B1 Cittadinanza). Nel B1 standard solo le abilità non superate.", "B1 standard: 18 mesi secondo la pagina web, un anno secondo le Linee guida.",
         "B1 Cittadinanza: la tassa è 100 euro. Abilità singole del B1 standard: importo non scritto."),
        ("CELI", "Solo lo scritto o solo l'orale, se hai superato l'altra parte.", "Un anno.", "Il 70% della tassa intera; la tassa la comunica il centro."),
        ("PLIDA", "Solo le abilità non superate, da una a tre.", "18 mesi, anche più tentativi, anche in un altro centro.", "Non scritto: lo dice il centro d'esame."),
        ("CERT.IT", "Per il B1 il sito non lo scrive.", "Per il B1 non scritto (per il B2: due anni).", "B1: solo la quota intera, 80 € a Roma Tre."),
    ]
    tab = "".join(f'<tr><td>{G.eb(s)}<br><a class="ris-guida" href="../{slug(G, s)}/#non-superato">Le regole {escape(s)} {G.ic("freccia")}</a></td>'
                  f'<td data-l="Cosa rifai">{escape(a)}</td><td data-l="Entro quando">{escape(b)}</td><td data-l="Quanto costa">{escape(c)}</td></tr>' for s, a, b, c in righe)
    domande = [
        ("Non ho superato l'esame B1 per la cittadinanza: devo rifare tutto?",
         "Dipende dall'ente. CILS B1 Cittadinanza: sì, si rifà tutto l'esame nella sessione successiva. CELI: entro un anno rifai solo lo scritto o solo l'orale. "
         "PLIDA: entro 18 mesi recuperi da una a tre abilità. CERT.IT: per il B1 il sito non lo scrive, chiedi alla sede.", None),
        ("Che cos'è la capitalizzazione nell'esame CILS?",
         "È la possibilità di tenere le abilità già superate e rifare solo le altre. Chi non ha la sufficienza in tutte le abilità riceve un attestato di capitalizzazione. "
         "Per il CILS B1 Cittadinanza la capitalizzazione non è consentita.", "cils b1 cittadinanza"),
        ("Posso vedere il mio esame CILS dopo i risultati?",
         "Sì: entro 30 giorni dalla pubblicazione dei risultati scrivi al Centro CILS (trasparenzacertificazioni@unistrasi.it) con i tuoi dati, la copia di un documento valido "
         "e il pagamento della tassa per l'accesso.", "risultati cils b1 cittadinanza"),
        ("Posso cambiare ente per rifare l'esame?",
         "Ogni ente scrive le regole del recupero per il proprio esame: nelle pagine lette nessun ente prevede di contare le parti superate "
         "con un altro ente. Se ti iscrivi all'esame B1 di un altro ente, ti iscrivi all'esame intero.", None),
        ("Quanto devo aspettare per rifare l'esame B1?",
         "Fino alla prossima sessione dell'ente che scegli. Nelle pagine lette nessun ente scrive un tempo minimo di attesa tra un esame e l'altro. "
         "Le prossime date sono in questa pagina.", None),
    ]
    jsonld, faq_html = faq(G, "dopo-esame/non-superato/", domande)
    sezioni = "".join(
        f'<section><h2 id="{slug(G, s)}">{G.eb(s)} Esame {escape(s)} non superato</h2><ol class="passi">{"".join(C[s]["non_superato"])}</ol>'
        f'<p><a href="../{slug(G, s)}/">Dopo l\'esame {escape(s)}: certificato e tempi</a> · <a href="../../esempi/{G.SLUG_ENTE[s]}/">Prova d\'esempio {escape(s)}</a></p></section>'
        for s in ORDINE)
    corpo = f"""<section class="hero">
{G.briciole(("EsameB1", "../../"), ("Dopo l'esame", "../"), ("Esame non superato", None))}
<span class="occhiello">{G.ic("attenzione")}Fonti ufficiali degli enti · lette il {v}</span>
<h1>Esame B1 non superato: cosa devi rifare con CILS, CELI, PLIDA e CERT.IT</h1>
<p class="lead">Con il CILS B1 Cittadinanza si rifà tutto l'esame; con il CELI hai un anno per rifare solo lo scritto o solo l'orale, pagando il 70% della tassa;
con il PLIDA hai 18 mesi per recuperare da una a tre abilità. Per il CERT.IT B1 il sito di Roma Tre non scrive la regola. Fonti: documenti ufficiali degli enti, letti il {v}.</p>
</section>
<section>
<h2 id="confronto">{G.ic("lista")}Cosa rifai, entro quando, quanto costa</h2>
<div class="tab-wrap ris-tab"><table class="conf"><thead><tr><th scope="col">Ente</th><th scope="col">Cosa rifai</th><th scope="col">Entro quando</th><th scope="col">Quanto costa</th></tr></thead>
<tbody>{tab}</tbody></table></div>
</section>
<section>
<h2 id="passi">{G.ic("ok")}Cosa fare adesso, in 4 passi</h2>
<ol class="passi">
<li><div><strong>Guarda quali parti non hai superato</strong><p>Lo vedi nel risultato; se non è chiaro, chiedi al centro d'esame. <a href="../../risultati/">Dove vedere il risultato, ente per ente</a>.</p></div></li>
<li><div><strong>Controlla se puoi rifare solo quelle</strong><p>Dipende dall'ente e dal tipo d'esame: la tabella qui sopra e le regole qui sotto, con le frasi degli enti.</p></div></li>
<li><div><strong>Segna la scadenza del recupero</strong><p>Un anno per il CELI, 18 mesi per il PLIDA: la regola del recupero vale solo entro quel tempo.</p></div></li>
<li><div><strong>Iscriviti alla prossima sessione ed esercitati sulle prove ufficiali</strong><p><a href="#date">Le prossime date</a> ·
<a href="../../esempi/">le prove d'esempio ufficiali</a> · <a href="../../esempi/simulazione/">la simulazione con il cronometro</a> ·
<a href="../../esempi/prova-scritta/">la prova scritta</a> · <a href="../../esenzioni-e-domande/">l'orale</a>.</p></div></li>
</ol>
</section>
{sezioni}
<div class="due">
<section>
<h2 id="date">{G.ic("cal")}Le prossime date d'esame</h2>
{G.lista_sessioni(prossime[:8], con_filtri=False)}
<p><a href="../../#date">Tutte le date</a> · <a href="../../costo/">Quanto costa l'esame</a></p>
</section>
<aside>{G.modulo()}</aside>
</div>
{G.riquadro_preparati("../../")}
<section>
<h2 id="domande">{G.ic("info")}Domande frequenti</h2>
{faq_html}
</section>
<section>
<p class="small">{NOTA}</p>
<h2>{G.ic("doc")}Dopo l'esame, ente per ente</h2>
<div class="altre"><a href="../">Tutti gli enti</a>{altri_enti(G, None, "../")}</div>
<h2>{G.ic("info")}Altre guide</h2>
{G.link_guide("../../")}
</section>"""
    G.pagina("dopo-esame/non-superato/index.html", G.titolo_pagina("Esame B1 non superato: cosa rifare con CILS, CELI, PLIDA"),
             G.descrizione_pagina("Esame B1 cittadinanza non superato: CILS si rifà tutto, CELI un anno per scritto o orale al 70%, PLIDA 18 mesi per le abilità. Le regole con le fonti."),
             corpo, jsonld)


# ---------------------------------------------------------------- /esempi/a2/ e /esempi/b2/
def file_html(G, gruppo):
    v = G.data_breve(D["verificato_il"])
    righe = "".join(
        f'<li><span class="fi">{G.ic(G.ICONA_FILE[f["formato"]])}</span><div><a href="{escape(f["url"])}" rel="noopener">{escape(f["nome"])}</a>'
        f'<span class="cosa">{escape(f["contenuto"][0].upper() + f["contenuto"][1:])}.</span></div>'
        f'<div class="meta"><strong>{f["formato"]}</strong><span>{escape(G.peso(f["byte"]))}</span></div></li>' for f in D["esempi"][gruppo])
    return (f'<ul class="file-lista">{righe}</ul><div class="fonte">{G.ic("ok")}<span>Link controllati il {v}: i {len(D["esempi"][gruppo])} file si aprono '
            'sul sito cils.unistrasi.it (stato 200), con il formato e la dimensione indicati.</span></div>')


def scheda_ente(G, s, titolo, corpo, bottone_k, bottone_testo=None):
    return (f'<div class="es-card es-{s.replace(".", "")}" id="{G.SLUG_ENTE[s]}"><h3>{G.eb(s)} {titolo}</h3>{corpo}'
            f'<p><a class="btn btn-2" href="{escape(D["fonti"][bottone_k]["url"])}" rel="noopener">{G.ic("freccia")}{escape(bottone_testo or "Pagina ufficiale " + s)}</a></p></div>')


def pagina_livello(G, livello, prossime):
    v = G.data_breve(D["verificato_il"])
    celi_nota = ("I file stanno sul sito www.unistrapg.it, che dal nostro server non si apre (certificato del sito incompleto): "
                 "per questo qui c'è solo il link alla pagina ufficiale del CVCL, dove li scarichi.")
    certit_nota = "Per le note legali di Roma Tre non mettiamo link diretti ai file: li scarichi dalla pagina ufficiale."
    if livello == "a2":
        nome, altro = "A2", "b2"
        h1 = "Esame di italiano A2: le prove d'esempio ufficiali, con PDF e audio"
        titolo = "Esame italiano A2: prove d'esempio ufficiali, PDF e audio"
        desc = "Test di italiano A2: le prove d'esempio ufficiali di CILS (14 file PDF e MP3), CELI, PLIDA e CERT.IT, con ascolto e orale, e i punti per superare."
        lead = ("Il Centro CILS dell'Università per Stranieri di Siena pubblica gratis due esempi completi dell'esame A2, con audio dell'ascolto e tracce dell'orale: "
                "A2 standard (7 file) e A2 integrazione in Italia (7 file). CELI, PLIDA e CERT.IT pubblicano i loro esempi A2 sulle loro pagine ufficiali.")
        schede = [
            scheda_ente(G, "CILS", "CILS A2 integrazione in Italia",
                        f"<p>L'esame A2 del Centro CILS per chi vive in Italia. Per superare: nel modulo per l'integrazione le Linee guida scrivono "
                        f"{Q('cils_linee', 'Per superare le abilità di comprensione')}, e 7 punti per lettura e scrittura.</p>{file_html(G, 'cils_a2i')}"
                        f"{fonte(G, 'cils_a2i', 'cils_linee')}", "cils_a2i", "Pagina ufficiale CILS A2 integrazione"),
            scheda_ente(G, "CILS", "CILS A2 standard",
                        f"<p>L'esame A2 generale, con cinque abilità. Le Linee guida scrivono: {Q('cils_linee', 'Per superare un’abilità')}</p>{file_html(G, 'cils_a2')}"
                        f"{fonte(G, 'cils_a2', 'cils_linee')}", "cils_a2", "Pagina ufficiale CILS A2 standard").replace('id="cils"', 'id="cils-standard"'),
            scheda_ente(G, "CELI", "CELI 1 i (A2, immigrati) e CELI 1 (A2)",
                        f"<p>La pagina «Esami CELI immigrati» del CVCL elenca per il CELI 1 i: {Q('celi_immigrati', 'prova d')}, più la descrizione dell'esame, "
                        f"i criteri di valutazione, gli input dell'orale e le risposte. {Q('celi_immigrati', 'Durata totale')}. Per il CELI 1 generico la pagina «Esami CELI generici» "
                        f"elenca: {Q('celi_generici', 'prova d')}. Il risultato A2 è senza lettere: {Q('celi_regolamento', 'Per i livelli A1 e A2')}</p>"
                        f'<p class="ris-nota">{celi_nota}</p><p><a href="{escape(D["fonti"]["celi_generici"]["url"])}" rel="noopener">Pagina ufficiale CELI generici (CELI 1)</a></p>'
                        f"{fonte(G, 'celi_immigrati', 'celi_generici', 'celi_regolamento')}", "celi_immigrati", "Pagina ufficiale CELI immigrati (CELI 1 i)"),
            scheda_ente(G, "PLIDA", "PLIDA A2 inItalia",
                        f"<p>È l'esame PLIDA per il permesso di soggiorno UE: {Q('plida_a2', 'Puoi fare questo esame')}. Sulla pagina ufficiale trovi la guida all'esame e il link "
                        f"{Q('plida_a2', 'Scarica qui la Prova')}. Nelle FAQ la Società Dante Alighieri scrive: {Q('plida_faq', 'Il certificato PLIDA A2')} "
                        "I file si scaricano dalla pagina ufficiale con un indirizzo che cambia: per questo non mettiamo link diretti.</p>"
                        f"{fonte(G, 'plida_a2', 'plida_faq')}", "plida_a2", "Pagina ufficiale PLIDA A2 inItalia"),
            scheda_ente(G, "CERT.IT", "CERT.IT A2 (Roma Tre)",
                        f"<p>{Q('certit_a2', 'In fondo alla pagina')} Lì trovi l'esempio di esame e 4 file audio della prova di ascolto. "
                        f"{Q('certit_a2', 'Le sezioni Ascolto')} {Q('certit_a2', 'La sezione Produzione orale')} {Q('certit_a2', 'L’esame è superato')} "
                        f"Quota a Roma Tre: {Q('certit_iscrizione', 'A2: 40')}.</p><p class=\"ris-nota\">{certit_nota}</p>{fonte(G, 'certit_a2', 'certit_iscrizione')}",
                        "certit_a2"),
        ]
        usi = ('<p>Il livello A2 serve per il permesso di soggiorno UE per soggiornanti di lungo periodo (carta di soggiorno). '
               '<a href="../../test-italiano-a2/">Il test di italiano A2 in Prefettura: come funziona</a> · <a href="../../carta-di-soggiorno/">Carta di soggiorno: requisiti e documenti</a> · '
               '<a href="../../esonero-test-italiano/">chi è esonerato dal test</a>. Per la cittadinanza serve invece il B1: <a href="../">le prove d\'esempio B1</a>.</p>')
        domande = [
            ("Dove trovo un esempio dell'esame di italiano A2 in PDF?",
             "Sul sito del Centro CILS (Università per Stranieri di Siena): le pagine «Prove Liv. A2 standard» e «Prove Liv. A2 integrazione in Italia» hanno il quaderno, "
             "le tracce di scrittura e orale e i criteri in PDF, più l'audio in MP3. CELI, PLIDA e CERT.IT hanno i loro esempi A2 sulle loro pagine ufficiali.",
             "test italiano a2 pdf"),
            ("Le prove d'esame CILS A2 in PDF hanno le soluzioni?",
             "L'esempio CILS A2 standard sì: tra i file c'è il PDF delle soluzioni. Nell'esempio CILS A2 integrazione in Italia la pagina ufficiale elenca quaderno, audio, "
             "trascrizioni, tracce e criteri di valutazione, senza un file di soluzioni.", "cils a2 prove d'esame pdf"),
            ("C'è l'audio della prova di ascolto A2?",
             "Sì. Il Centro CILS pubblica un file MP3 per l'A2 standard e uno per l'A2 integrazione, con le trascrizioni in PDF. "
             "La pagina CERT.IT del livello A2 ha 4 file audio della prova di ascolto.", "test italiano a2 esempio"),
            ("Quanti punti servono per superare l'esame CILS A2?",
             "Secondo le Linee guida CILS, nel modulo A2 per l'integrazione in Italia servono almeno 10 punti in ascolto e in produzione orale e almeno 7 in lettura e in scrittura; "
             "nell'A2 standard almeno 7 punti in ogni abilità.", "cils a2"),
            ("L'esame A2 serve per la cittadinanza?",
             "No: per la cittadinanza serve il livello B1. L'A2 serve per il permesso di soggiorno UE per soggiornanti di lungo periodo.", "esame italiano a2"),
        ]
    else:
        nome, altro = "B2", "a2"
        h1 = "Esame di italiano B2: le prove d'esempio ufficiali, con PDF e audio"
        titolo = "Esame italiano B2: prove d'esempio ufficiali, PDF e audio"
        desc = "Test di italiano B2: l'esempio ufficiale CILS DUE-B2 (7 file PDF e MP3) e le pagine ufficiali di CELI 3, PLIDA B2 e CERT.IT B2, con ascolto e orale."
        lead = ("Il Centro CILS dell'Università per Stranieri di Siena pubblica gratis un esempio completo dell'esame CILS DUE-B2: 7 file, con l'audio dell'ascolto, "
                "le tracce dell'orale e le soluzioni. CELI 3, PLIDA B2 e CERT.IT B2 hanno i loro esempi sulle loro pagine ufficiali.")
        schede = [
            scheda_ente(G, "CILS", "CILS DUE-B2",
                        f"<p>Cinque abilità da 20 punti. Le Linee guida scrivono: {Q('cils_linee', 'Per superare una abilità')} {Q('cils_linee', 'Il punteggio totale massimo ottenibile è 100')}</p>"
                        f"{file_html(G, 'cils_b2')}{fonte(G, 'cils_b2', 'cils_linee')}", "cils_b2", "Pagina ufficiale CILS B2"),
            scheda_ente(G, "CELI", "CELI 3 (B2)",
                        f"<p>La pagina «Esami CELI generici» del CVCL elenca per il CELI 3: {Q('celi_generici', 'prova d')}, più competenze richieste, struttura della prova, "
                        f"valutazione e punteggi. Il Ministero {Q('celi_generici', 'riconosce il CELI 3')}.</p><p class=\"ris-nota\">{celi_nota}</p>{fonte(G, 'celi_generici')}",
                        "celi_generici", "Pagina ufficiale CELI generici (CELI 3)"),
            scheda_ente(G, "PLIDA", "PLIDA B2",
                        "<p>Nella pagina «Preparati all'esame» scegli il livello B2 e scarichi i materiali. Nelle FAQ la Società Dante Alighieri scrive che i certificati PLIDA "
                        f"si possono presentare per {Q('plida_faq', 'richiedere il visto')} e per {Q('plida_faq', 'iscriversi all’Università')}. "
                        "I file si scaricano dalla pagina ufficiale con un indirizzo che cambia: per questo non mettiamo link diretti.</p>"
                        f"{fonte(G, 'plida_prepara', 'plida_faq')}", "plida_prepara", "Pagina ufficiale PLIDA: Preparati all'esame"),
            scheda_ente(G, "CERT.IT", "CERT.IT B2 (Roma Tre)",
                        f"<p>{Q('certit_b2', 'In fondo alla pagina')} Lì trovi l'esempio di esame e 3 file audio della prova di ascolto. "
                        f"{Q('certit_b2', 'Le sezioni Ascolto, Lettura e Produzione scritta')} {Q('certit_b2', 'La sezione Produzione orale')} "
                        f"Per superare: {Q('certit_b2', 'L’esame è superato')}. {Q('certit_b2', 'Laddove non venissero')} "
                        f"Quote a Roma Tre: {Q('certit_iscrizione', 'B2: 140')}.</p><p class=\"ris-nota\">{certit_nota}</p>{fonte(G, 'certit_b2', 'certit_iscrizione')}",
                        "certit_b2"),
        ]
        usi = ('<p>Il B2 è il livello chiesto di solito per iscriversi all\'università in Italia; per la cittadinanza basta il B1. '
               '<a href="../">Le prove d\'esempio B1 per la cittadinanza</a> · <a href="../confronto/">i 4 esami B1 a confronto</a> · '
               '<a href="../../esonero-test-italiano/">quali titoli esonerano dal B1</a>.</p>')
        domande = [
            ("Dove trovo le prove d'esame CILS B2 in PDF?",
             "Sulla pagina ufficiale «Prove Liv. B2» del Centro CILS (Università per Stranieri di Siena): quaderno del candidato, trascrizione, tracce dell'orale, "
             "soluzioni e criteri di valutazione in PDF, più l'audio dell'ascolto in MP3.", "cils b2 prove d'esame pdf"),
            ("Quanti punti servono per superare il CILS B2?",
             "Secondo le Linee guida CILS ogni abilità vale al massimo 20 punti e si supera con almeno 11; il totale massimo è 100 e il minimo 55.", "cils b2"),
            ("Dove trovo un test di italiano B2 ufficiale gratis?",
             "Gli enti certificatori pubblicano i loro esempi: CILS DUE-B2 con link diretti a PDF e MP3, CELI 3 sulla pagina «Esami CELI generici» del CVCL, "
             "PLIDA B2 nella pagina «Preparati all'esame», CERT.IT B2 in fondo alla pagina del livello B2 di Roma Tre.", "test italiano b2"),
            ("L'esame di italiano B2 serve per la cittadinanza?",
             "Per la cittadinanza è richiesto il livello B1. Il B2 serve soprattutto per l'università: il CVCL scrive che il Ministero riconosce il CELI 3 "
             "per iscriversi all'università in Italia.", "esame italiano b2"),
            ("Nel PLIDA B2 e nel CERT.IT B2 si può rifare solo una parte?",
             "CERT.IT B2: sì, le sezioni superate si possono capitalizzare entro due anni dal superamento della prima. "
             "Per il PLIDA B2 non abbiamo letto un documento ufficiale con la regola del livello B2: chiedi al centro d'esame.", "plida b2"),
        ]
    jsonld, faq_html = faq(G, f"esempi/{livello}/", domande)
    corpo = f"""<section class="hero">
{G.briciole(("EsameB1", "../../"), ("Prove d'esempio", "../"), (f"Livello {nome}", None))}
<span class="occhiello">{G.ic("libro")}Fonti ufficiali degli enti · controllato il {v}</span>
<h1>{escape(h1)}</h1>
<p class="lead">{escape(lead)} Pagine ufficiali controllate il {v}.</p>
<div class="azioni"><a class="btn" href="#cils">{G.ic("archivio")}I file CILS {nome}</a><a class="btn btn-2" href="../">{G.ic("libro")}Prove d'esempio B1</a></div>
</section>
<section>
<h2 id="enti">{G.ic("archivio")}Le prove d'esempio {nome}, ente per ente</h2>
<p class="small">Ogni link apre la pagina o il file sul sito dell'ente: qui non copiamo niente. I file sono gratis e si scaricano senza registrazione.</p>
{"".join(schede)}
</section>
<section class="ris-sez">
<h2 id="a-cosa-serve">{G.ic("info")}A cosa serve il livello {nome}</h2>
{usi}
</section>
<section>
<h2 id="come-usare">{G.ic("matita")}Come usare un esempio d'esame</h2>
<ol class="passi">
<li><div><strong>Fai la prova con i tempi veri</strong><p>Stampa o apri il quaderno, fai partire l'audio una volta sola e non fermarlo: all'esame non puoi.</p></div></li>
<li><div><strong>Correggi con le soluzioni, dove ci sono</strong><p>Guarda quali prove sbagli di più: ascolto, lettura o grammatica.</p></div></li>
<li><div><strong>Scrivi e parla davvero</strong><p>Fai le tracce di scrittura contando le parole e registra la tua risposta alle tracce dell'orale.</p></div></li>
</ol>
</section>
<div class="due">
<section>
<h2 id="date">{G.ic("cal")}Le prossime date dell'esame B1</h2>
{G.lista_sessioni(prossime[:4], con_filtri=False)}
<p><a href="../../#date">Tutte le date B1</a>. Le date di {nome} sono nei calendari ufficiali degli enti.</p>
</section>
<aside>{G.modulo()}</aside>
</div>
<section>
<h2 id="domande">{G.ic("info")}Domande frequenti</h2>
{faq_html}
</section>
<section>
<p class="small">{NOTA}</p>
<h2>{G.ic("libro")}Altri esempi</h2>
<div class="altre"><a href="../">Prove d'esempio B1</a><a href="../{altro}/">Prove d'esempio {altro.upper()}</a><a href="../confronto/">I 4 esami B1 a confronto</a><a href="../simulazione/">Simulazione</a></div>
<h2>{G.ic("info")}Altre guide</h2>
{G.link_guide("../../", salta="esempi/")}
</section>"""
    G.pagina(f"esempi/{livello}/index.html", G.titolo_pagina(titolo), G.descrizione_pagina(desc), corpo, jsonld)


# ---------------------------------------------------------------- ingresso
def carica(G):
    global D, PAROLE
    D = json.loads((G.DATI / "dopo_esame.json").read_text(encoding="utf-8"))
    PAROLE = json.loads((G.DATI / "parole_dopo_esame.json").read_text(encoding="utf-8"))


def genera(G, prossime):
    carica(G)
    C = contenuti(G)
    pagina_indice(G, C, prossime)
    urls = ["dopo-esame/"]
    for s in ORDINE:
        pagina_ente(G, s, C[s], prossime)
        urls.append(f"dopo-esame/{slug(G, s)}/")
    pagina_non_superato(G, C, prossime)
    urls.append("dopo-esame/non-superato/")
    for livello in ("a2", "b2"):
        pagina_livello(G, livello, prossime)
        urls.append(f"esempi/{livello}/")
    return urls


def controlli(G):
    """Ogni testo tra «» delle pagine è una frase citata (o il nome di una fonte o di una pagina ufficiale); ogni ricerca delle domande
    frequenti è misurata con volume maggiore di 0; ogni domanda del JSON-LD è visibile. Si ferma al primo problema."""
    da_fonti = (" ".join(c["testo"] for c in D["citazioni"]) + " " + " ".join(f["nome"] for f in D["fonti"].values())).lower()
    misurate = {**PAROLE["simili"], **PAROLE["parole"]}
    errori = []
    for p, ricerche in RICERCHE.items():
        h = (G.SITO / p / "index.html").read_text(encoding="utf-8")
        main = h[h.find("<main"):h.find("</main>")]
        testo = unescape(re.sub(r"<[^>]+>", "", main))
        for frase in re.findall(r"«([^»]+)»", testo):
            if frase.lower() not in da_fonti:
                errori.append(f"{p}: il testo tra virgolette «{frase}» non è tra le frasi citate")
        for r in ricerche:
            if not misurate.get(r):
                errori.append(f"{p}: la ricerca «{r}» di una domanda frequente non è misurata (dati/parole_dopo_esame.json)")
        ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
        for q in json.loads(ld.group(1))["mainEntity"]:
            if escape(q["name"]) not in main or escape(q["acceptedAnswer"]["text"]) not in main:
                errori.append(f"{p}: domanda frequente non visibile: {q['name']}")
    if errori:
        raise SystemExit("ERRORI NELLE PAGINE «DOPO L'ESAME» (genera_dopo.py):\n" + "\n".join(errori))
    return len(RICERCHE)
