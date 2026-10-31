"""Sezioni in ucraino (/uk/) e rumeno (/ro/) di EsameB1 (dal 31/10/2026) e lingue del sito (hreflang e menu per it/en/uk/ro).

Fronte: studio-business/intelaiatura/fronti-2026-10-31-lingue-immigrati.md, righe 2 e 3 (ucraino voto 7, rumeno voto 6,5).
Google non traduce da solo i risultati in ucraino e rumeno: chi cerca in queste lingue trova solo pagine scritte nella sua
lingua. Punto 7 del fronte: solo pagine guida (qui 11 in ucraino, 10 in rumeno), mai le pagine città; cifre e date dai file dati.

Regole (le stesse di genera_en.py):
- ogni cifra e ogni data viene dai file in dati/ (gli stessi delle pagine italiane); i fatti che le pagine italiane non
  scrivono (protezione temporanea, cittadini UE, anni di residenza per l'art. 9) vengono da dati/lingue.json, frase per frase
  (controllo dal vivo: raccolta/lingue.py); dove il dato è una frase italiana il numero si legge con num() e, se la frase
  cambia, la generazione si ferma;
- ogni pagina ha gli equivalenti nelle altre lingue (PAGINE, hreflang reciproci it/en/uk/ro e x-default = it, o en se
  l'italiano non c'è) e un menu delle lingue (menu_lingue()) usato anche da genera.py e genera_en.py;
- nessun riquadro italki/Amazon: la riga di trasparenza obbligatoria esiste solo in italiano e in inglese
  (studio-business/strumenti/monetizzazione.py) e Amazon non dà una frase ufficiale in ucraino o rumeno;
- controlli() gira dopo la generazione: cifre, importi e date di ogni pagina presenti nelle pagine italiane di riferimento
  (o nelle frasi di lingue.json indicate), hreflang reciproci su tutto il sito, calcolatore identico in 4 lingue,
  prima frase con fonte e data, «вирішує / decide» presente, nessun link sponsorizzato.

Usato da genera.py (G = il modulo genera): genera(G, prossime) scrive le pagine e restituisce gli URL per la sitemap.
"""
import json
import re
from datetime import date
from decimal import Decimal
from html import escape, unescape
from pathlib import Path

import genera_en as EN

DATI = Path(__file__).resolve().parent / "dati"
LING = json.loads((DATI / "lingue.json").read_text(encoding="utf-8"))

ORDINE = ["it", "en", "uk", "ro"]
NOME_LINGUA = {"it": "Italiano", "en": "English", "uk": "Українська", "ro": "Română"}
CODICE = {"it": "IT", "en": "EN", "uk": "УКР", "ro": "RO"}
HOME = {"it": "index.html", "en": "en/", "uk": "uk/", "ro": "ro/"}

# (pagina, equivalente italiano o None, equivalente inglese o None, pagine italiane di riferimento per le cifre,
#  fonti di dati/lingue.json le cui frasi possono dare cifre e date)
PAGINE = {
    "uk": [
        ("uk/", "index.html", "en/", ["come-funziona/index.html", "costo/index.html", "reddito-minimo-cittadinanza/index.html", "esonero-test-italiano/index.html"], ["questura_roma", "questura_udine", "questura_milano", "questura_arezzo", "im_2028"]),
        ("uk/ispyt-b1-dlia-hromadianstva/", "come-funziona/index.html", "en/italian-b1-exam-for-citizenship/", ["costo/index.html", "esonero-test-italiano/index.html", "index.html", "esenzioni-e-domande/index.html"], []),
        ("uk/daty-ispytu-b1/", None, "en/b1-exam-dates/", ["index.html"], []),
        ("uk/vartist-ispytu-b1/", "costo/index.html", "en/b1-exam-cost/", ["come-funziona/index.html"], []),
        ("uk/zrazky-ispytu-b1/", "esempi/index.html", "en/sample-papers/", ["esempi/cils/index.html", "esempi/celi/index.html", "esempi/plida/index.html", "esempi/certit/index.html", "come-funziona/index.html"], []),
        ("uk/zvilnennia-vid-ispytu/", "esonero-test-italiano/index.html", "en/language-test-exemptions/", [], []),
        ("uk/dokhid-dlia-hromadianstva/", "reddito-minimo-cittadinanza/index.html", "en/income-requirement-italian-citizenship/", [], []),
        ("uk/hromadianstvo-italii/", "cittadinanza/index.html", "en/apply-italian-citizenship-by-residence/", ["reddito-minimo-cittadinanza/index.html", "cittadinanza/genova/index.html"], ["dlci_residenza"]),
        ("uk/karta-di-soggiorno/", None, "en/carta-di-soggiorno-requirements/", ["reddito-minimo-cittadinanza/index.html", "esonero-test-italiano/index.html"], []),
        ("uk/vozziednannia-simi/", "reddito-ricongiungimento-familiare/index.html", "en/family-reunification-income/", [], []),
        ("uk/tymchasovyi-zakhyst/", None, None, [], ["questura_roma", "questura_udine", "questura_arezzo", "questura_milano", "prefettura_spezia", "polizia_verifica", "dlci_residenza", "normattiva_dl201", "im_2028"]),
    ],
    "ro": [
        ("ro/", "index.html", "en/", ["come-funziona/index.html", "costo/index.html", "reddito-minimo-cittadinanza/index.html", "esonero-test-italiano/index.html"], ["dlci_residenza"]),
        ("ro/examen-b1-cetatenie/", "come-funziona/index.html", "en/italian-b1-exam-for-citizenship/", ["costo/index.html", "esonero-test-italiano/index.html", "index.html", "esenzioni-e-domande/index.html"], []),
        ("ro/date-examen-b1/", None, "en/b1-exam-dates/", ["index.html"], []),
        ("ro/cost-examen-b1/", "costo/index.html", "en/b1-exam-cost/", ["come-funziona/index.html"], []),
        ("ro/modele-examen-b1/", "esempi/index.html", "en/sample-papers/", ["esempi/cils/index.html", "esempi/celi/index.html", "esempi/plida/index.html", "esempi/certit/index.html", "come-funziona/index.html"], []),
        ("ro/scutire-test-italiana/", "esonero-test-italiano/index.html", "en/language-test-exemptions/", [], []),
        ("ro/venit-minim-cetatenie/", "reddito-minimo-cittadinanza/index.html", "en/income-requirement-italian-citizenship/", [], []),
        ("ro/cetatenie-italiana/", "cittadinanza/index.html", "en/apply-italian-citizenship-by-residence/", ["reddito-minimo-cittadinanza/index.html", "esonero-test-italiano/index.html"], ["dlci_residenza"]),
        ("ro/carta-di-soggiorno/", None, "en/carta-di-soggiorno-requirements/", ["reddito-minimo-cittadinanza/index.html", "esonero-test-italiano/index.html"], []),
        ("ro/rezidenta-italia-cetateni-ue/", None, None, ["reddito-minimo-cittadinanza/index.html", "esonero-test-italiano/index.html"], ["polizia_ue", "dlci_residenza"]),
    ],
}

SCRITTE = []  # pagine scritte: {"lg", "p", "it", "en", "rif", "cit"} (per controlli())


# ---------------------------------------------------------------- gruppi di pagine equivalenti (hreflang e menu lingue)
def _gruppi():
    gruppi, indice = [], {}

    def aggiungi(voci):
        voci = {k: v for k, v in voci.items() if v}
        esistente = next((indice[(k, v)] for k, v in voci.items() if (k, v) in indice), None)
        if esistente is None:
            esistente = {}
            gruppi.append(esistente)
        for k, v in voci.items():
            if esistente.get(k, v) != v:
                raise SystemExit(f"genera_lingue: {k} ha due pagine equivalenti diverse: {esistente[k]} e {v}")
            esistente[k] = v
            indice[(k, v)] = esistente

    for en, it, _ in EN.COPPIE:
        aggiungi({"en": en, "it": it})
    for lg, righe in PAGINE.items():
        for p, it, en, _, _ in righe:
            aggiungi({lg: p, "it": it, "en": en})
    return indice


GRUPPI = _gruppi()


def gruppo(lg, percorso):
    """Pagine equivalenti {lingua: percorso} della pagina (lingua, percorso); {} se non ce ne sono."""
    g = GRUPPI.get((lg, percorso), {})
    return g if len(g) > 1 else {}


def url_rel(percorso):
    """«index.html» → «», «come-funziona/index.html» → «come-funziona/», «uk/» → «uk/», «privacy.html» resta."""
    return percorso[:-10] if percorso.endswith("index.html") else percorso


def alternati(G, lg, percorso):
    """<link rel="alternate" hreflang=…> per tutte le lingue del gruppo, x-default = italiano (o inglese se manca)."""
    g = gruppo(lg, percorso)
    if not g:
        return ""
    righe = [f'\n<link rel="alternate" hreflang="{x}" href="{G.URL_SITO}/{url_rel(g[x])}">' for x in ORDINE if x in g]
    xd = g.get("it") or g.get("en")
    return "".join(righe) + f'\n<link rel="alternate" hreflang="x-default" href="{G.URL_SITO}/{url_rel(xd)}">'


ETICHETTA_MENU = {"it": "Lingua", "en": "Language", "uk": "Мова", "ro": "Limba"}


def menu_lingue(G, lg, percorso, rel_root):
    """Selettore lingua del menu (details/summary, nessun JS necessario): porta alla pagina equivalente o alla home della lingua."""
    g = gruppo(lg, percorso)
    voci = []
    for x in ORDINE:
        dest = g.get(x) or HOME[x]
        href = (rel_root + url_rel(dest)) or "./"
        corrente = ' aria-current="true"' if x == lg else ""
        voci.append(f'<li><a href="{href}" hreflang="{x}" lang="{x}"{corrente}>{NOME_LINGUA[x]}</a></li>')
    return (f'<details class="lingue"><summary aria-label="{ETICHETTA_MENU[lg]}: {NOME_LINGUA[lg]}">{G.ic("web")}'
            f'<span>{CODICE[lg]}</span></summary><ul>{"".join(voci)}</ul></details>')


def link_piede_lingue(lg, percorso, rel_root):
    """Voci del piede verso le altre lingue (equivalente o home)."""
    g = gruppo(lg, percorso)
    return "".join(f'<li><a href="{(rel_root + url_rel(g.get(x) or HOME[x])) or "./"}" hreflang="{x}" lang="{x}">{NOME_LINGUA[x]}</a></li>'
                   for x in ORDINE if x != lg)


# Font per le lingue (31/10/2026): Figtree non ha il cirillico né ă, ș, ț. Due file in più con unicode-range (il browser li
# scarica solo se la pagina contiene quei caratteri): Onest cirillico (OFL, stile vicino a Figtree) e Figtree latin-ext.
# Stessa famiglia e STESSO intervallo di pesi (300 900) della faccia principale: Chrome unisce solo facce con gli stessi
# intervalli; con 100 900 il cirillico finiva sul font di sistema (provato con Playwright).
CSS_FONT = ('@font-face{font-family:"Figtree";src:url("/fonts/figtree-latin-ext.woff2") format("woff2");font-weight:300 900;font-style:normal;font-display:swap;'
            'unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1E00-1E9F,U+20A0-20AB,U+20AD-20C0}\n'
            '@font-face{font-family:"Figtree";src:url("/fonts/onest-cyrillic.woff2") format("woff2");font-weight:300 900;font-style:normal;font-display:swap;'
            'unicode-range:U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116}\n')
CSS_MENU = """nav.menu details.lingue{position:relative;background:none;border:0;margin:0;border-radius:999px}
nav.menu details.lingue>summary{display:inline-flex;align-items:center;gap:5px;padding:8px 10px;border-radius:999px;color:var(--ink-2);font-weight:600;font-size:.97rem;justify-content:flex-start}
nav.menu details.lingue>summary:hover,nav.menu details.lingue[open]>summary{color:var(--brand-ink);background:var(--brand-soft)}
nav.menu details.lingue>summary .i{transform:none;color:inherit;width:18px;height:18px}
nav.menu details.lingue>ul{position:absolute;right:0;top:calc(100% + 6px);z-index:30;margin:0;padding:6px;list-style:none;background:var(--surface);border:1px solid var(--line);border-radius:12px;box-shadow:0 10px 28px rgba(0,0,0,.14);min-width:170px}
nav.menu details.lingue li{margin:0}
nav.menu details.lingue li a{display:block;padding:9px 12px;border-radius:8px}
nav.menu details.lingue li a[aria-current]{color:var(--brand-ink);background:var(--brand-soft)}
@media (max-width:640px){nav.menu details.lingue>summary{padding:8px 7px;font-size:.95rem;gap:4px}}
"""
# Chiude il menu delle lingue con un clic fuori (aggiunto in fondo al JS di ogni pagina).
JS_MENU = ("document.addEventListener('click',function(e){document.querySelectorAll('details.lingue[open]').forEach(function(x){"
           "if(!x.contains(e.target))x.open=false;});});")


# ---------------------------------------------------------------- testi e formati per lingua
MESI_GEN = {"uk": ["січня", "лютого", "березня", "квітня", "травня", "червня", "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"],
            "ro": ["ianuarie", "februarie", "martie", "aprilie", "mai", "iunie", "iulie", "august", "septembrie", "octombrie", "noiembrie", "decembrie"]}
MESI_BREVI = {"uk": ["січ", "лют", "бер", "квіт", "трав", "черв", "лип", "серп", "вер", "жовт", "лист", "груд"],
              "ro": ["ian", "feb", "mar", "apr", "mai", "iun", "iul", "aug", "sep", "oct", "noi", "dec"]}
GIORNI = {"uk": ["понеділок", "вівторок", "середа", "четвер", "п’ятниця", "субота", "неділя"],
          "ro": ["luni", "marți", "miercuri", "joi", "vineri", "sâmbătă", "duminică"]}
MESI_IT = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
NBSP = " "


def d(iso):
    return date.fromisoformat(iso)


def data(lg, iso):
    x = d(iso)
    return f"{x.day} {MESI_GEN[lg][x.month - 1]} {x.year}"


def data_lunga(lg, iso):
    x = d(iso)
    return f"{GIORNI[lg][x.weekday()]}, {x.day} {MESI_GEN[lg][x.month - 1]} {x.year}"


def giorno_mese(lg, iso):
    x = d(iso)
    return f"{x.day} {MESI_GEN[lg][x.month - 1]}"


def iso_it(testo):
    """«9 dicembre 2010», «1° gennaio 2026» o «11/03/2026» → «2010-12-09» (si ferma se non trova una data)."""
    m = re.search(r"(\d{1,2})°? (" + "|".join(MESI_IT) + r") (\d{4})", testo or "", re.I)
    if m:
        return date(int(m.group(3)), MESI_IT.index(m.group(2).lower()) + 1, int(m.group(1))).isoformat()
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", testo or "")
    if m:
        return date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
    raise SystemExit(f"genera_lingue: nessuna data in «{(testo or '')[:120]}»")


def eur(lg, x, decimali=True):
    """uk: «8 263,31 €» (spazio unificatore tra le migliaia); ro: «8.263,31 €»; con decimali=False e importo intero «250 €»."""
    x = Decimal(str(x))
    sep = NBSP if lg == "uk" else "."
    if not decimali and x == x.to_integral_value():
        intero, dec = f"{int(x):,}", ""
    else:
        intero, dec = f"{x.quantize(Decimal('0.01')):,.2f}".split(".")
        dec = "," + dec
    return intero.replace(",", sep) + dec + NBSP + "€"


def eur_c(lg, c):
    return eur(lg, Decimal(c) / 100)


def pl_uk(n, uno, pochi, molti):
    n = abs(int(n))
    if n % 10 == 1 and n % 100 != 11:
        return uno
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return pochi
    return molti


def pl_ro(n, uno, altri):
    n = abs(int(n))
    if n == 1:
        return uno
    return ("de " if n % 100 == 0 or n % 100 >= 20 else "") + altri


def num(testo, regola, gruppo=1):
    """Come genera_en.num (si ferma se la frase cambia), con più numeri in lettere («quattro», «due»…)."""
    g = EN.num(testo, regola, gruppo)
    return str(PAROLE_NUMERO[g]) if g in PAROLE_NUMERO else g


def citazioni(*fonti):
    """Testo delle frasi di dati/lingue.json delle fonti indicate."""
    return " ".join(c["testo"] for c in LING["citazioni"] if c["fonte"] in fonti)


def fonte_l(k):
    return LING["fonti"][k]


T = {  # testi fissi dello scheletro
    "uk": {
        "og": "uk_UA", "salta": "Перейти до змісту", "home": "EsameB1 українською, головна сторінка", "date": "Дати", "guide": "Посібники", "guide_corto": "Теми",
        "avvisami": "Сповіщення", "qui": "Ви тут", "in_breve": "EsameB1 українською",
        "piede": ("<strong>{nome}</strong> — незалежний сайт, не пов’язаний з екзаменаційними установами, Міністерством внутрішніх справ, Префектурами чи Квестурами. "
                  "CILS, CELI, PLIDA і CERT.IT — торговельні марки їхніх власників. Кожна цифра взята з офіційного джерела, вказаного поруч. "
                  "<strong>Перш ніж реєструватися чи подавати документи, завжди перевіряйте в екзаменаційному центрі, Префектурі чи Квестурі: рішення ухвалюють вони.</strong> "
                  "Сайт не надає юридичних консультацій щодо громадянства чи дозволів на проживання: див. "
                  '<a href="https://www.interno.gov.it/it/temi/cittadinanza-e-altri-diritti-civili/cittadinanza" rel="noopener" hreflang="it">сторінку Міністерства внутрішніх справ (італійською)</a>.'),
        "dati": "Дані перевірено {data}.", "altri": "Інші безкоштовні інструменти",
        "strikes": "страйки на поїздах, літаках і міському транспорті в Італії за офіційним реєстром Міністерства (англійською та італійською). Ще один безкоштовний незалежний сайт того самого видавця.",
        "privacy": "Конфіденційність (італійською)", "privacy_en": "англійською",
    },
    "ro": {
        "og": "ro_RO", "salta": "Salt la conținut", "home": "EsameB1 în limba română, pagina principală", "date": "Date", "guide": "Ghiduri", "guide_corto": "Ghiduri",
        "avvisami": "Anunțuri", "qui": "Sunteți aici", "in_breve": "EsameB1 în română",
        "piede": ("<strong>{nome}</strong> este un site independent, fără legătură cu instituțiile de examinare, Ministerul de Interne, prefecturile sau chesturile. "
                  "CILS, CELI, PLIDA și CERT.IT sunt mărci ale titularilor lor. Fiecare cifră provine din sursa oficială indicată alături. "
                  "<strong>Înainte de a vă înscrie sau de a depune o cerere, verificați întotdeauna la centrul de examen, la Prefectură sau la Chestură: ele decid.</strong> "
                  "Site-ul nu oferă consultanță juridică privind cetățenia sau permisele de ședere: vedeți "
                  '<a href="https://www.interno.gov.it/it/temi/cittadinanza-e-altri-diritti-civili/cittadinanza" rel="noopener" hreflang="it">pagina Ministerului de Interne (în italiană)</a>.'),
        "dati": "Date verificate la {data}.", "altri": "Alte instrumente gratuite",
        "strikes": "grevele din trenuri, avioane și transportul local din Italia, după registrul oficial al Ministerului (în engleză și italiană). Un alt site gratuit și independent al aceluiași editor.",
        "privacy": "Confidențialitate (în italiană)", "privacy_en": "în engleză",
    },
}

NOME_ENTE = {"uk": {"CILS": "Університет для іноземців Сієни", "CELI": "Університет для іноземців Перуджі",
                    "PLIDA": "Товариство Данте Аліґ’єрі (Società Dante Alighieri)", "CERT.IT": "Університет Рим Тре (Roma Tre)"},
             "ro": {"CILS": "Universitatea pentru Străini din Siena", "CELI": "Universitatea pentru Străini din Perugia",
                    "PLIDA": "Societatea Dante Alighieri", "CERT.IT": "Universitatea Roma Tre"}}
PROVE = {"uk": {"ascolto": "аудіювання", "lettura": "читання", "scrittura": "письмо", "orale": "усна частина"},
         "ro": {"ascolto": "ascultare", "lettura": "citire", "scrittura": "scriere", "orale": "proba orală"}}


def tempo(lg, t):
    regole = {
        "uk": ((r"^(\d+(?:-\d+)?) min circa$", "близько {} хв"), (r"^(\d+) min \(con la grammatica\)$", "{} хв (разом із граматикою)"),
               (r"^(\d+(?:-\d+)?) min$", "{} хв"), (r"^([234]) ore, lettura e scrittura insieme$", "{} години (читання і письмо разом)"),
               (r"^(\d+) min in tutto, le tre prove insieme$", "{} хв загалом (три частини разом)")),
        "ro": ((r"^(\d+(?:-\d+)?) min circa$", "aproximativ {} min"), (r"^(\d+) min \(con la grammatica\)$", "{} min (cu gramatica)"),
               (r"^(\d+(?:-\d+)?) min$", "{} min"), (r"^([2-9]) ore, lettura e scrittura insieme$", "{} ore (citire și scriere împreună)"),
               (r"^(\d+) min in tutto, le tre prove insieme$", "{} min în total (cele trei probe împreună)")),
    }[lg]
    for regola, fmt in regole:
        m = re.match(regola, t)
        if m:
            return fmt.format(m.group(1))
    raise SystemExit(f"genera_lingue: tempo non riconosciuto «{t}»: aggiornare tempo()")


def totale(lg, t):
    m = re.match(r"^(circa )?(\d+) or[ae](?: e (\d+) min)? \((somma delle prove|dato ufficiale)\)$", t)
    if not m:
        raise SystemExit(f"genera_lingue: totale non riconosciuto «{t}»: aggiornare totale()")
    circa, ore, minuti, tipo = m.groups()
    if lg == "uk":
        s = f"{'близько ' if circa else ''}{ore} год{f' {minuti} хв' if minuti else ''}"
        return s + (" (сума частин)" if tipo == "somma delle prove" else " (офіційні дані)")
    s = f"{'aproximativ ' if circa else ''}{ore} h{f' {minuti} min' if minuti else ''}"
    return s + (" (suma probelor)" if tipo == "somma delle prove" else " (date oficiale)")


def esame(lg, x):
    return x.replace("(sessione A2/B1)", "(сесія A2/B1)" if lg == "uk" else "(sesiunea A2/B1)")


def parti(lg, prove):
    p = ", ".join(PROVE[lg][x] for x in prove)
    return p[0].upper() + p[1:]


# ---------------------------------------------------------------- JS comune tradotto
def _forme_uk(v, uno, pochi, molti):
    return (f"({v}%10===1&&{v}%100!==11?'{uno}':{v}%10>=2&&{v}%10<=4&&({v}%100<12||{v}%100>14)?'{pochi}':'{molti}')")


def _forme_ro(v, uno, altri):
    return f"({v}===1?'{uno}':({v}%100===0||{v}%100>=20?'de {altri}':'{altri}'))"


JS_SOST = {
    "uk": [
        ("el.textContent=g===0?'oggi':g===1?'domani':'tra '+g+' giorni';",
         "el.textContent=g===0?'сьогодні':g===1?'завтра':'через '+g+' '+" + _forme_uk("g", "день", "дні", "днів") + ";"),
        ("el.textContent=g===0?'scade oggi':'mancano '+g+(g===1?' giorno':' giorni');",
         "el.textContent=g===0?'закінчується сьогодні':'ще '+g+' '+" + _forme_uk("g", "день", "дні", "днів") + ";"),
        ("'termine nazionale passato: chiedi alla sede se accetta ancora iscrizioni'", "'національний термін минув: запитайте в центрі, чи ще приймають реєстрацію'"),
        ("'Mostra tutte le '+vis.length+' date'", "'Показати всі дати ('+vis.length+')'"),
        ("(vis.length===1?' sessione':' sessioni')", "(' '+" + _forme_uk("vis.length", "сесія", "сесії", "сесій") + ")"),
        ("' per la cittadinanza'", "' для громадянства'"),
    ],
    "ro": [
        ("el.textContent=g===0?'oggi':g===1?'domani':'tra '+g+' giorni';",
         "el.textContent=g===0?'astăzi':g===1?'mâine':'peste '+g+' '+" + _forme_ro("g", "zi", "zile") + ";"),
        ("el.textContent=g===0?'scade oggi':'mancano '+g+(g===1?' giorno':' giorni');",
         "el.textContent=g===0?'expiră astăzi':'încă '+g+' '+" + _forme_ro("g", "zi", "zile") + ";"),
        ("'termine nazionale passato: chiedi alla sede se accetta ancora iscrizioni'", "'termenul național a trecut: întrebați centrul dacă mai acceptă înscrieri'"),
        ("'Mostra tutte le '+vis.length+' date'", "'Arată toate datele ('+vis.length+')'"),
        ("(vis.length===1?' sessione':' sessioni')", "(' '+" + _forme_ro("vis.length", "sesiune", "sesiuni") + ")"),
        ("' per la cittadinanza'", "' pentru cetățenie'"),
    ],
}


def js(G, lg):
    testo = G.JS
    for a_, b_ in JS_SOST[lg]:
        if a_ not in testo:
            raise SystemExit(f"genera_lingue: il JS di genera.py è cambiato, aggiornare JS_SOST: {a_}")
        testo = testo.replace(a_, b_)
    return testo


def testo_conta(lg, iso, modo, oggi):
    g = (d(iso) - oggi).days
    if lg == "uk":
        if modo == "esame":
            return "сьогодні" if g == 0 else "завтра" if g == 1 else f"через {g} {pl_uk(g, 'день', 'дні', 'днів')}"
        return "закінчується сьогодні" if g == 0 else f"ще {g} {pl_uk(g, 'день', 'дні', 'днів')}"
    if modo == "esame":
        return "astăzi" if g == 0 else "mâine" if g == 1 else f"peste {g} {pl_ro(g, 'zi', 'zile')}"
    return "expiră astăzi" if g == 0 else f"încă {g} {pl_ro(g, 'zi', 'zile')}"


# ---------------------------------------------------------------- pezzi di pagina
def a(url, testo):
    return f'<a href="{escape(url)}" rel="noopener">{escape(testo)}</a>'


def fonte(G, lg, link, data_iso, parola=None):
    parola = parola or ("Джерело (італійською)" if lg == "uk" else "Sursa (în italiană)")
    verb = "перевірено" if lg == "uk" else "verificat la"
    return f'<div class="fonte">{G.ic("doc")}<span>{parola}: {link} · {verb} {data(lg, data_iso)}</span></div>'


def fonti_parola(lg, n):
    if lg == "uk":
        return "Джерело (італійською)" if n == 1 else "Джерела (італійською)"
    return "Sursa (în italiană)" if n == 1 else "Surse (în italiană)"


def decide(G, lg, chi):
    if lg == "uk":
        return G.avviso("Ця сторінка коротко викладає офіційні джерела українською; це не юридична консультація. "
                        f"<strong>Рішення у вашій справі ухвалює {chi}.</strong> Щодо вашої ситуації звертайтеся туди або до патронату "
                        "(patronato — безкоштовна служба консультацій).")
    return G.avviso("Această pagină rezumă în limba română surse oficiale; nu este consultanță juridică. "
                    f"<strong>Decizia în cazul dumneavoastră o ia {chi}.</strong> Pentru situația dumneavoastră întrebați acolo sau la un patronato "
                    "(birou de asistență gratuită).")


def nota_esame(G, lg):
    if lg == "uk":
        return G.avviso("Сайт незалежний і не надає юридичних консультацій. Дати, ціни й терміни підтверджує екзаменаційний центр; "
                        "<strong>для заяви на громадянство рішення ухвалює Префектура</strong>: саме вона вирішує, який сертифікат дійсний.")
    return G.avviso("Site-ul este independent și nu oferă consultanță juridică. Datele, prețurile și termenele le confirmă centrul de examen; "
                    "<strong>pentru cererea de cetățenie decide Prefectura</strong> ce certificat este valabil.")


def briciole(lg, rel, *voci):
    tutte = [(T[lg]["in_breve"], rel)] + list(voci)
    parti_ = [f'<a href="{h}">{escape(t)}</a>' if h else f'<span aria-current="page">{escape(t)}</span>' for t, h in tutte]
    return f'<nav class="briciole" aria-label="{T[lg]["qui"]}">{" <span aria-hidden=\"true\">›</span> ".join(parti_)}</nav>'


def altre_lingue(G, lg, percorso, rel_root, extra_it=None):
    """Riga visibile con i link alla stessa pagina nelle altre lingue (italiano per primo: è la versione di riferimento)."""
    g = gruppo(lg, percorso)
    voci = []
    for x in ORDINE:
        if x == lg or x not in g:
            continue
        voci.append(f'<a href="{rel_root + url_rel(g[x]) or "./"}" hreflang="{x}" lang="{x}">{NOME_LINGUA[x]}</a>')
    if extra_it:
        voci = extra_it + voci
    if not voci:
        return ""
    testa = "Ця сторінка іншими мовами:" if lg == "uk" else "Această pagină în alte limbi:"
    nota = (" Італійська версія — основна: у разі сумнівів вона має перевагу." if lg == "uk"
            else " Versiunea italiană este cea de referință: în caz de îndoială, ea are prioritate.")
    return f'<p class="small lingua-alt">{G.ic("web")}<span>{testa}</span> {" · ".join(voci)}.{nota if "it" in g or extra_it else ""}</p>'


def faq_blocco(G, faq):
    html_faq = "".join(G.domanda(q, t) for q, t in faq)
    return html_faq, {"@context": "https://schema.org"} | G.faq_jsonld(faq)


def nota_scad(lg, s):
    """Nota sulla scadenza, letta dalla nota italiana di sessioni.json (date comprese)."""
    n = s["nota_scadenza"]
    e = s["ente"]
    if e == "CILS":
        num(n, r"(Università per Stranieri di Siena)")
        return ("Термін, вказаний Університетом для іноземців Сієни: екзаменаційні центри можуть закрити реєстрацію раніше." if lg == "uk"
                else "Termen stabilit de Universitatea pentru Străini din Siena: centrele de examen pot închide înscrierile mai devreme.")
    if e == "CELI":
        num(n, r"(Università per Stranieri di Perugia)")
        return ("Термін, вказаний Університетом для іноземців Перуджі: центри можуть закрити реєстрацію раніше." if lg == "uk"
                else "Termen stabilit de Universitatea pentru Străini din Perugia: centrele pot închide înscrierile mai devreme.")
    if e == "PLIDA":
        num(n, r"(ogni centro PLIDA)")
        return ("Кожен центр PLIDA сам встановлює кінцевий термін: запитайте в обраному центрі." if lg == "uk"
                else "Fiecare centru PLIDA își stabilește propriul termen: întrebați la centrul ales.")
    if e == "CERT.IT":
        quando = data(lg, iso_it(num(n, r"Iscrizioni aperte dal?l?.?(\d{1,2} \w+ \d{4})")))
        return (f"Реєстрація відкривається {quando} у партнерських центрах, які встановлюють кінцевий термін. Точний день уточніть у центрі." if lg == "uk"
                else f"Înscrierile se deschid pe {quando} la centrele partenere, care stabilesc termenul. Confirmați ziua exactă cu centrul.")
    raise SystemExit(f"genera_lingue: ente sconosciuto {e}")


def scheda_sessione(G, lg, s):
    citt = s["tipo"] == "cittadinanza"
    if lg == "uk":
        badge_t, reg, fonte_t, verif = ("Іспит для громадянства" if citt else "B1, дійсний для громадянства"), "Реєстрація до", "офіційний календар", "перевірено"
    else:
        badge_t, reg, fonte_t, verif = ("Examen pentru cetățenie" if citt else "B1 valabil pentru cetățenie"), "Înscriere până la", "calendarul oficial", "verificat la"
    badge = f'<span class="tag{" citt" if citt else ""}">{G.ic("ok")}{badge_t}</span>'
    nota = "" if G.nota_comune(s) else f'<div class="nota">{escape(nota_scad(lg, s))}</div>'
    scad = (f'<span class="scad" data-scadenza="{s["scadenza"]}">{G.ic("orologio")}{reg} <strong>{data(lg, s["scadenza"])}</strong>'
            f'<span class="stato conta"></span></span>') if s.get("scadenza") else ""
    x = d(s["data"])
    tile = (f'<div class="tile" aria-hidden="true"><span class="tm">{MESI_BREVI[lg][x.month - 1]}</span>'
            f'<span class="td">{x.day}</span><span class="ty">{x.year}</span></div>')
    sorgente = "Джерело" if lg == "uk" else "Sursa"
    return f"""<article class="sess" data-data="{s['data']}" data-ente="{escape(s['ente'])}" data-tipo="{s['tipo']}">
{tile}
<div class="cosa"><div class="testa">{G.eb(s['ente'])}<span class="nome">{escape(", ".join(esame(lg, e) for e in s["esami"]))}</span>{badge}</div>
<div class="quando"><time datetime="{s['data']}">{data_lunga(lg, s['data'])}</time>{scad}</div>
{nota}
<div class="fonte">{G.ic("doc")}<span>{sorgente}: <a href="{escape(s['fonte'])}" rel="noopener">{fonte_t} {escape(s['ente'])}</a> · {verif} {data(lg, s['verificato_il'])}</span></div>
</div>
</article>"""


def lista_sessioni(G, lg, lista, con_filtri=True):
    righe, viste = [], set()
    for e in G.ENTE:
        for s in lista:
            if s["ente"] == e and G.nota_comune(s) and s["nota_scadenza"] not in viste:
                viste.add(s["nota_scadenza"])
                righe.append(f'<li>{G.eb(e)}<span>{escape(nota_scad(lg, s))}</span></li>')
    uk = lg == "uk"
    note = f'<ul class="note-scad" aria-label="{"Як читати терміни" if uk else "Cum se citesc termenele"}">{"".join(righe)}</ul>' if righe else ""
    filtri = ""
    if con_filtri:
        bottoni = [f'<button type="button" data-filtro="tutti" aria-pressed="true">{"Усі" if uk else "Toate"}</button>',
                   f'<button type="button" data-filtro="citt" aria-pressed="false">{G.ic("ok")}{"Лише для громадянства" if uk else "Doar pentru cetățenie"}</button>']
        bottoni += [f'<button type="button" data-filtro="{e}" aria-pressed="false"><span class="pt" style="background:var(--{e.replace(".", "").lower()})"></span>{e}</button>'
                    for e in G.ENTE]
        filtri = (f'<div class="filtri chips" role="group" aria-label="{"Фільтр за установою" if uk else "Filtru după instituție"}">{"".join(bottoni)}</div>'
                  '<p class="esito" aria-live="polite"></p>')
    return (f'<div data-elenco>{note}{filtri}<div class="sessioni">' + "\n".join(scheda_sessione(G, lg, s) for s in lista)
            + f'</div><button class="btn btn-2 mostra" type="button" hidden>{"Показати всі дати" if uk else "Arată toate datele"}</button></div>')


def risposta(G, lg, prossime, rel, pagina_date):
    uk = lg == "uk"
    opz_e = []
    for i, s in enumerate(prossime[:12]):
        x = d(s["data"])
        opz_e.append(f"""<div data-fino="{s['data']}"{"" if i == 0 else " hidden"}>
<div class="r-data">{x.day} {MESI_GEN[lg][x.month - 1]} <small>{x.year}</small></div>
<div class="r-cosa">{G.eb(s['ente'])}<span>{escape(", ".join(esame(lg, e) for e in s['esami']))}</span></div>
<p style="margin:12px 0 0"><span class="conta {G.classe_conta(s['data'], 'esame')}" data-conta="{s['data']}" data-modo="esame">{testo_conta(lg, s['data'], 'esame', G.OGGI)}</span></p>
</div>""")
    con_scad = sorted((s for s in prossime if s.get("scadenza")), key=lambda s: (s["scadenza"], s["data"]))
    opz_s, primo = [], True
    for s in con_scad:
        visibile = primo and d(s["scadenza"]) >= G.OGGI
        if visibile:
            primo = False
        per = (f'для іспиту {G.eb(s["ente"])} <strong>{giorno_mese(lg, s["data"])}</strong>' if uk
               else f'pentru examenul {G.eb(s["ente"])} din <strong>{giorno_mese(lg, s["data"])}</strong>')
        opz_s.append(f"""<div data-fino="{s['scadenza']}"{"" if visibile else " hidden"}>
<div class="r-data"><small>{"до" if uk else "până la"}</small> {data(lg, s['scadenza'])}</div>
<div class="r-cosa">{per}</div>
<p style="margin:12px 0 0"><span class="conta {G.classe_conta(s['scadenza'], 'scad')}" data-conta="{s['scadenza']}" data-modo="scad">{testo_conta(lg, s['scadenza'], 'scad', G.OGGI)}</span></p>
<p class="r-nota">{"Це національний термін: центр може закрити реєстрацію раніше. Завжди перепитайте." if uk else "Acesta este termenul național: centrul poate închide mai devreme. Cereți întotdeauna confirmare."}</p>
</div>""")
    riserva = (f'<p data-riserva class="r-nota"{"" if primo else " hidden"}>'
               + ("Зараз немає відкритого національного терміну: для PLIDA і CERT.IT термін встановлює кожен центр. Запитайте в центрі." if uk
                  else "Acum nu este deschis niciun termen național: pentru PLIDA și CERT.IT termenul îl stabilește fiecare centru. Întrebați centrul.")
               + "</p>")
    return f"""<div class="risposta">
<div class="slot" data-slot><div class="r-et">{G.ic("cal")}{"Найближчий іспит" if uk else "Următorul examen"}</div>{"".join(opz_e)}</div>
<div class="slot" data-slot><div class="r-et">{G.ic("orologio")}{"Реєстрація ще відкрита" if uk else "Înscrieri încă deschise"}</div>{"".join(opz_s)}{riserva}</div>
<div class="r-piede"><a href="{rel}{pagina_date}">{"Усі дати" if uk else "Toate datele"} {G.ic("freccia")}</a><span>{G.ic("info")}{"Дати іспитів однакові по всій Італії." if uk else "Datele examenelor sunt aceleași în toată Italia."}</span></div>
</div>"""


def modulo(G, lg, rel_root):
    uk = lg == "uk"
    altra = "Інше місто" if uk else "Alt oraș"
    opzioni = "".join(f'<option value="{escape(c["nome"])}">{escape(c["nome"])}</option>' for c in sorted(G.citta, key=lambda c: c["nome"]))
    enti_opt = "".join(f'<option value="{e}">{e}</option>' for e in G.ENTE)
    priv = (f'<a href="{rel_root}privacy.html" hreflang="it" lang="it">{"повідомлення про конфіденційність (італійською)" if uk else "nota de confidențialitate (în italiană)"}</a> '
            f'{"або" if uk else "sau"} <a href="{rel_root}en/privacy/" hreflang="en" lang="en">{"англійською" if uk else "în engleză"}</a>')
    if uk:
        testi = ("Повідомте мене про нові дати", "Безкоштовно. Ми пишемо, коли з’являється нова сесія іспиту або коли у вашому місті закінчується термін реєстрації. Листи — італійською.",
                 "Не заповнюйте", "Ваш email", "Місто, де хочете складати іспит", "Оберіть місто", "Бажана установа (необов’язково)", "Без переваг",
                 f"Я погоджуюся отримувати листи від {G.NOME} про дати іспиту B1 і можу відписатися будь-коли. Я прочитав(-ла) {priv}.",
                 "Повідомляти мене", "Не вдалося надіслати. Спробуйте ще раз за хвилину.", "Готово!", "Ми напишемо, коли будуть новини для вашого міста.")
    else:
        testi = ("Anunțați-mă când apar date noi", "Gratuit. Vă scriem când se publică o nouă sesiune de examen sau când în orașul dumneavoastră se apropie termenul de înscriere. E-mailurile sunt în italiană.",
                 "Nu completați", "E-mailul dumneavoastră", "Orașul în care vreți să dați examenul", "Alegeți orașul", "Instituția preferată (opțional)", "Nicio preferință",
                 f"Sunt de acord să primesc e-mailuri de la {G.NOME} despre datele examenului B1 și mă pot dezabona oricând. Am citit {priv}.",
                 "Anunțați-mă", "Trimiterea nu a reușit. Încercați din nou peste un minut.", "Gata!", "Vă scriem când apar noutăți pentru orașul dumneavoastră.")
    return f"""<section class="card" id="avvisami">
<div class="modulo-testa"><span class="bolla">{G.ic("campana")}</span><div>
<h2>{testi[0]}</h2>
<p class="small" style="margin:4px 0 0">{testi[1]}</p></div></div>
<form class="form avvisami" name="avvisami" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="avvisami">
<input type="hidden" name="source" value="">
<p class="hp"><label>{testi[2]} <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>{testi[3]}<input type="email" name="email" required autocomplete="email" placeholder="nome@esempio.it"></label>
<label>{testi[4]}
<select name="citta" required><option value="">{testi[5]}</option>{opzioni}<option value="Altra città">{altra}</option></select></label>
<label>{testi[6]}
<select name="ente"><option value="">{testi[7]}</option>{enti_opt}</select></label>
<label class="check"><input type="checkbox" name="consenso" value="si" required>
<span>{testi[8]}</span></label>
<button class="btn" type="submit">{G.ic("campana")}{testi[9]}</button>
<p class="errore" data-errore hidden>{testi[10]}</p>
</form>
<div class="ok" data-ok hidden>{G.ic("ok")}<span><strong>{testi[11]}</strong> {testi[12]}</span></div>
</section>"""


GUIDE = {
    "uk": [("daty-ispytu-b1/", "cal", "Дати іспиту B1", "усі сесії, за установами"),
           ("ispyt-b1-dlia-hromadianstva/", "lista", "Іспит B1 для громадянства", "що це, установи, тривалість"),
           ("vartist-ispytu-b1/", "euro", "Скільки коштує іспит", "офіційні ціни"),
           ("zrazky-ispytu-b1/", "libro", "Безкоштовні зразки іспиту", "офіційні PDF і аудіо"),
           ("zvilnennia-vid-ispytu/", "scudo", "Хто звільнений від іспиту", "B1 для громадянства, A2 для carta"),
           ("dokhid-dlia-hromadianstva/", "euro", "Дохід для громадянства", "і для carta di soggiorno, калькулятор"),
           ("hromadianstvo-italii/", "edificio", "Громадянство Італії", "роки, документи, заява онлайн"),
           ("karta-di-soggiorno/", "doc", "Carta di soggiorno", "роки, дохід, тест A2"),
           ("vozziednannia-simi/", "pin", "Возз’єднання сім’ї", "дохід за кількістю членів родини"),
           ("tymchasovyi-zakhyst/", "scudo", "Тимчасовий захист", "продовження, конвертація, перевірка")],
    "ro": [("date-examen-b1/", "cal", "Datele examenului B1", "toate sesiunile, pe instituții"),
           ("examen-b1-cetatenie/", "lista", "Examenul B1 pentru cetățenie", "ce este, instituții, durată"),
           ("cost-examen-b1/", "euro", "Cât costă examenul", "prețuri oficiale"),
           ("modele-examen-b1/", "libro", "Modele de examen gratuite", "PDF și audio oficiale"),
           ("scutire-test-italiana/", "scudo", "Cine e scutit de test", "B1 pentru cetățenie, A2 pentru carta"),
           ("venit-minim-cetatenie/", "euro", "Venitul minim pentru cetățenie", "și pentru carta di soggiorno, calculator"),
           ("cetatenie-italiana/", "edificio", "Cetățenia italiană", "ani, acte, cererea online"),
           ("rezidenta-italia-cetateni-ue/", "pin", "Rezidența pentru cetățenii UE", "anagrafe, ședere permanentă"),
           ("carta-di-soggiorno/", "doc", "Carta di soggiorno", "pentru cetățenii din afara UE")],
}


def griglia_guide(G, lg, rel, salta=None):
    return '<div class="griglia link3">' + "".join(
        f'<a href="{rel}{h}">{G.ic(i)}<span>{t}<small>{sm}</small></span></a>' for h, i, t, sm in GUIDE[lg] if h != salta) + "</div>"


def due_colonne(G, lg, rel, rel_root, salta):
    tit = "Інші посібники" if lg == "uk" else "Alte ghiduri"
    return (f'<div class="due">\n<section><h2>{G.ic("info")}{tit}</h2>{griglia_guide(G, lg, rel, salta=salta)}</section>\n'
            f'<aside>{modulo(G, lg, rel_root)}</aside>\n</div>')


def faq_sezione(G, lg, faq_html):
    return f'<section>\n<h2>{G.ic("info")}{"Часті запитання" if lg == "uk" else "Întrebări frecvente"}</h2>\n{faq_html}\n</section>'


# ---------------------------------------------------------------- struttura della pagina
def pagina_l(G, lg, percorso, titolo, descrizione, corpo, jsonld=None):
    voce = next((r for r in PAGINE[lg] if r[0] == percorso), None)
    if voce is None:
        raise SystemExit(f"genera_lingue: {percorso} non è in PAGINE[{lg}]")
    if len(titolo) > G.MAX_TITOLO or len(descrizione) > G.MAX_DESC:
        raise SystemExit(f"{percorso}: titolo {len(titolo)}/{G.MAX_TITOLO} o description {len(descrizione)}/{G.MAX_DESC} troppo lunghi")
    if 'rel="sponsored' in corpo:
        raise SystemExit(f"{percorso}: link sponsorizzato in una pagina {lg} (riga di trasparenza non tradotta in monetizzazione.py)")
    t = T[lg]
    profondita = percorso.count("/")
    rel_root = "../" * profondita
    rel = "../" * (profondita - 1) or "./"
    canonico = G.URL_SITO + "/" + percorso
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    avvisami = "#avvisami" if 'id="avvisami"' in corpo else f"{rel}#avvisami"
    guide_piede = "".join(f'<li><a href="{rel}{h}">{tt}</a></li>' for h, _, tt, _ in GUIDE[lg])
    verificato = data(lg, max([s["verificato_il"] for s in G.sessioni] + [s["verificato_il"] for s in G.sedi]))
    testo = f"""<!DOCTYPE html>
<html lang="{lg}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titolo)}</title>
<meta name="description" content="{escape(descrizione)}">
<link rel="canonical" href="{canonico}">{alternati(G, lg, percorso)}
<meta property="og:title" content="{escape(titolo)}">
<meta property="og:description" content="{escape(descrizione)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="{t["og"]}">
<meta property="og:image" content="{G.URL_SITO}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="{canonico}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0B6B4F">
<meta name="google-site-verification" content="{G.GOOGLE_VERIFICA}">{G.ADSENSE_HEAD}
<link rel="icon" href="{G.FAVICON}">
<link rel="preload" href="/fonts/figtree.woff2" as="font" type="font/woff2" crossorigin>
<style>{G.CSS}</style>
{ld}
</head>
<body>
{G.SPRITE}
<a class="salta" href="#contenuto">{t["salta"]}</a>
<header class="top"><div class="wrap">
<a class="logo" href="{rel}" aria-label="{t["home"]}">{G.MARCHIO}<span class="logo-testo">Esame<b>B1</b></span></a>
<nav class="menu" aria-label="Menu">
<a href="{rel}{GUIDE[lg][0][0]}">{t["date"]}</a><a href="{rel}#guides"><span class="lungo">{t["guide"]}</span><span class="corto">{t["guide_corto"]}</span></a>{menu_lingue(G, lg, percorso, rel_root)}<a class="nav-cta" href="{avvisami}" aria-label="{t["avvisami"]}">{G.ic("campana")}<span class="lungo">{t["avvisami"]}</span></a>
</nav>
</div></header>
<main class="wrap" id="contenuto">
{corpo}
</main>
<footer class="piede"><div class="wrap">
<div class="piede-griglia">
<div>
<a class="logo" href="{rel}">{G.MARCHIO}<span class="logo-testo">Esame<b>B1</b></span></a>
<ul class="piede-link">
<li><a href="{rel}">{t["in_breve"]}</a></li>{guide_piede}{link_piede_lingue(lg, percorso, rel_root)}<li><a href="{rel_root}privacy.html" hreflang="it" lang="it">{t["privacy"]}</a> · <a href="{rel_root}en/privacy/" hreflang="en" lang="en">{t["privacy_en"]}</a></li>
</ul>
</div>
<div>
<p>{t["piede"].format(nome=G.NOME)}</p>
<p><span class="dati">{G.ic("scudo")}{t["dati"].format(data=verificato)}</span></p>
</div>
</div>
<div class="piede-altri"><h2>{t["altri"]}</h2><ul><li><a href="https://italy-strikes-today.netlify.app/" rel="noopener">Italy Strikes Today</a>: {t["strikes"]}</li></ul></div>
</div></footer>
<script>{js(G, lg)}</script>
{G.SCRIPT_CONTATORE}
</body>
</html>
"""
    dest = G.SITO / percorso / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")
    SCRITTE.append({"lg": lg, "p": percorso + "index.html", "it": voce[1], "en": voce[2], "rif": voce[3], "cit": voce[4]})


# ---------------------------------------------------------------- dati comuni (dagli stessi file delle pagine italiane)
def fatti(G):
    E = G.ENTE
    celi_t = E["CELI"]["fatti"]["costo"]["testo"]
    return {
        "cils": E["CILS"]["prezzo_eur"],
        "padova": num(E["CILS"]["fatti"]["costo"]["testo"], r"Padova costa (\d+) €"),
        "certit": num(E["CERT.IT"]["fatti"]["costo"]["breve"], r"^(\d+) €"),
        "celi_tot": num(celi_t, r"(\d+) € all'Università degli Studi di Milano"),
        "celi_tassa": num(celi_t, r"\((\d+) € di tassa d'esame"),
        "celi_spese": num(celi_t, r"\+ (\d+) € di spese amministrative"),
        "celi_data": iso_it(num(celi_t, r"sessione del (\d{1,2} \w+ \d{4})")),
    }


def anni_residenza():
    """Anni di residenza legale per la cittadinanza (art. 9 L. 91/1992 sulla pagina DLCI): UE e stranieri non UE."""
    t = citazioni("dlci_residenza")
    return num(t, r"Comunità europee se risiede legalmente da almeno (quattro) anni"), num(t, r"straniero che risiede legalmente da almeno (dieci) anni")


def protezione():
    """Fatti sulla protezione temporanea, letti dalle frasi di lingue.json (Questure, Prefettura, Polizia di Stato)."""
    roma, udine, arezzo = citazioni("questura_roma"), citazioni("questura_udine"), citazioni("questura_arezzo")
    milano, norm, im = citazioni("questura_milano"), citazioni("normattiva_dl201"), citazioni("im_2028")
    im_data = iso_it(num(im, r"^(\d{1,2} luglio \d{4})"))
    return {
        "dl": num(roma, r"Il D\.L\. n\. (\d+/\d+) ha stabilito"),
        # Revisione 31/10/2026: il D.L. 201/2025 (art. 1 c. 2) riguarda i permessi per protezione speciale degli ucraini presenti prima del
        # 24/2/2022 e «ferma restando» la proroga della protezione temporanea al 4/3/2027 decisa dal Consiglio UE (decisione 2025/1460);
        # la proroga al 4/3/2028 è una decisione del Consiglio UE del 15/7/2026 (portale Integrazione Migranti), senza atto nazionale trovato.
        "ue_dec": num(milano, r"Decisione di esecuzione \(UE\) (\d{4}/\d{4}) del Consiglio"),
        "ue_dec_data": iso_it(num(milano, r"Consiglio dell.Unione Europea del (\d{1,2} \w+ \d{4}) la protezione temporanea")),
        "ue_fino": iso_it(num(milano, r"prorogata di un ulteriore anno fino al (\d{1,2} \w+ \d{4})")),
        "dl_conv_n": num(norm, r"legge di conversione \d{1,2} \w+ \d{4}, n\. (\d+)"),
        "dl_conv_data": iso_it(num(norm, r"legge di conversione (\d{1,2} \w+ \d{4}), n\. \d+")),
        "dl_presenti": iso_it(num(norm, r"in data antecedente al (\d{1,2} \w+ \d{4}), possono")),
        "dl_fino": iso_it(num(norm, r"a richiesta dell'interessato, fino al (\d{1,2} \w+ \d{4}), ferma restando")),
        "dl_ue_dec": num(norm, r"Decisione di esecuzione \(UE\) (\d{4}/\d{4}) del Consiglio"),
        "im_data": im_data, "im_anno": str(d(im_data).year),
        "im_giorno": num(im, r"Lo scorso (\d{1,2}) luglio, il Consiglio"),
        "im_fino": iso_it(num(im, r"fino al (\d{1,2} \w+ \d{4}), la protezione temporanea")),
        "fino": iso_it(num(roma, r"con scadenza sino al (\d{1,2} \w+ \d{4})")),
        "fino_udine": iso_it(num(udine, r"con scadenza sino al (\d{1,2} \w+ \d{4})")),
        "roma_agg": iso_it(num(roma, r"modificato il (\d{2}/\d{2}/\d{4})")),
        "udine_agg": iso_it(num(udine, r"^.*?(\d{2}/\d{2}/\d{4})")),
        "arezzo_fino": iso_it(num(arezzo, r"fino al (\d{1,2} \w+ \d{4})")),
        "arezzo_agg": iso_it(num(arezzo, r"modificato il (\d{2}/\d{2}/\d{4})")),
        "milano_agg": iso_it(num(citazioni("questura_milano"), r"modificato il (\d{2}/\d{2}/\d{4})")),
        "bollo": num(udine, r"Marca da bollo da (\d+) €"),
        "bollettino": num(udine, r"bollettino postale di (\d+,\d{2}) €"),
        "minori": num(arezzo, r"minori di età inferiore ai (\d+) anni"),
        "legge": num(arezzo, r"All'art 1, comma (\d+)"), "legge_n": num(arezzo, r"legge di bilancio nr\. (\d+) del"),
        "legge_data": iso_it(num(arezzo, r"legge di bilancio nr\. \d+ del (\d{1,2} \w+ \d{4})")),
        "conv_bollo": num(arezzo, r"modulo di domanda con marca da bollo da € (\d+)"),
        "conv_vers": num(arezzo, r"versamento di € (\d+,\d{2})"),
        "spezia_dopo": iso_it(num(citazioni("prefettura_spezia"), r"rilasciati dopo il (1° \w+ \d{4})")),
        "spezia_entro": iso_it(num(citazioni("prefettura_spezia"), r"entro il (\d{1,2} \w+ \d{4})")),
        "spezia_dl": num(citazioni("prefettura_spezia"), r"Decreto Legge 27 dicembre 2024, n\. (\d+)"),
        "spezia_dl_data": iso_it(num(citazioni("prefettura_spezia"), r"Decreto Legge (\d{1,2} \w+ \d{4}), n\.")),
        "spezia_art": num(citazioni("prefettura_spezia"), r"L’art\. (\d+), comma"),
        "pratica": num(citazioni("polizia_verifica"), r"numero di pratica \((\d+) caratteri\)"),
        "assicurata": num(citazioni("polizia_verifica"), r"numero di assicurata \((\d+) caratteri\)"),
    }


def controlla_protezione(P):
    """Coerenza tra le fonti sulla protezione temporanea: se una data o un numero di decisione cambia, fermarsi e rileggere le pagine."""
    if not (P["fino"] == P["fino_udine"] == P["ue_fino"] == P["dl_fino"]):
        raise SystemExit(f"genera_lingue: le fonti non concordano più sulla scadenza 2027 della protezione temporanea: {P['fino']}, {P['fino_udine']}, {P['ue_fino']}, {P['dl_fino']}")
    if P["ue_dec"] != P["dl_ue_dec"]:
        raise SystemExit("genera_lingue: Questura di Milano e Normattiva citano decisioni UE diverse")
    if P["arezzo_fino"] != P["im_fino"]:
        raise SystemExit(f"genera_lingue: Questura di Arezzo ({P['arezzo_fino']}) e portale Integrazione Migranti ({P['im_fino']}) non concordano sulla data 2028")


def euro_it_str(s):
    """«30,46» → Decimal('30.46')."""
    return Decimal(s.replace(".", "").replace(",", "."))


# ---------------------------------------------------------------- controlli dopo la generazione
RE_ALT = re.compile(r'<link rel="alternate" hreflang="([a-zA-Z-]+)" href="([^"]+)">')
RE_CANON = re.compile(r'<link rel="canonical" href="([^"]+)">')
RE_EUR_L = re.compile(r"(\d{1,3}(?:[. ]\d{3})+(?:,\d{2})?|\d+(?:,\d{2})?) ?€")
LIVELLI = re.compile(r"\b[ABC][12]\b")
PAROLE_NUMERO = {"due": 2, "tre": 3, "quattro": 4, "cinque": 5, "dieci": 10, "dodici": 12, "quattordici": 14, "ventiquattro": 24,
                 "trentasei": 36, "sessanta": 60, "ottanta": 80}


def testo_main_l(html):
    """Come genera_en.testo_main, ma lo spazio unificatore delle migliaia (8 263,31 €) resta: serve a leggere le cifre."""
    m = html[html.find("<main"): html.find("</main>")]
    m = re.sub(r"<(script|style|select)\b.*?</\1>", " ", m, flags=re.S | re.I)
    return re.sub(r"[ \t\r\n]+", " ", unescape(re.sub(r"<[^>]+>", " ", m)))


def senza_migliaia(t):
    return re.sub(r"(?<=\d)[  ](?=\d{3}\b)", "", t)


def cifre_l(t):
    return EN.cifre(LIVELLI.sub(" ", senza_migliaia(t)))


def euro_l(t):
    return {Decimal(x.replace(".", "").replace(NBSP, "").replace(",", ".")) for x in RE_EUR_L.findall(t)}


def date_l(lg, t):
    return {(int(y), MESI_GEN[lg].index(m) + 1, int(g)) for g, m, y in re.findall(r"\b(\d{1,2}) (" + "|".join(MESI_GEN[lg]) + r") (\d{4})\b", t)}


def date_it_ext(testo, html):
    """Date italiane, anche «1° gennaio 2026»."""
    out = EN.date_it_testo(testo, html)
    out |= {(int(y), MESI_IT.index(m.lower()) + 1, int(g)) for g, m, y in re.findall(r"\b(\d{1,2})° (" + "|".join(MESI_IT) + r") (\d{4})\b", testo, re.I)}
    return out


def ammesse_da_citazioni(fonti):
    """Cifre, importi e date che le frasi (e le date delle fonti) di lingue.json mettono a disposizione."""
    t = citazioni(*fonti)
    extra = " ".join(f"{f.get('verificato_il', '')} {f.get('aggiornata_il', '')}" for k, f in LING["fonti"].items() if k in fonti)
    cif = EN.cifre(t) | {str(n) for w, n in PAROLE_NUMERO.items() if re.search(rf"\b{w}\b", t)}
    date_ = date_it_ext(t, "") | {tuple(int(x) for x in iso.split("-")) for iso in re.findall(r"\d{4}-\d{2}-\d{2}", extra)}
    cif |= {str(int(x)) for y, m, g in date_ for x in (y, g)}
    return cif, EN.euro_it(t), date_


PRIMA = {"uk": (r"^(За |Згідно з|Відповідно до)", r"(перевірено|прочитано|оновлено)"),
         "ro": (r"^(Potrivit|Conform)", r"(verificat|citit|actualizat)")}
DECIDE = {"uk": r"ухвалює|вирішує", "ro": r"\bdecid|\bdecizi"}


def controlli(G):
    """(1) cifre, importi in euro e date di ogni pagina /uk/ e /ro/ presenti nelle pagine italiane di riferimento o nelle frasi
    di lingue.json indicate in PAGINE; (2) hreflang reciproci su tutto il sito (it, en, uk, ro, x-default); (3) calcolatore
    identico in 4 lingue; (4) link visibili alla versione italiana; menu lingue in ogni pagina accoppiata; (5) prima frase con
    fonte e data, «вирішує/ухвалює» o «decide» presenti; nessun link sponsorizzato."""
    errori = []
    sito = G.SITO
    leggi = lambda p: (sito / p).read_text(encoding="utf-8")  # noqa: E731
    for p in SCRITTE:
        html = leggi(p["p"])
        rif = ([p["it"]] if p["it"] else []) + p["rif"]
        t_l = testo_main_l(html)
        t_it = " ".join(EN.testo_main(leggi(r)) for r in rif)
        html_it = " ".join(leggi(r) for r in rif)
        c_cit, e_cit, d_cit = ammesse_da_citazioni(p["cit"]) if p["cit"] else (set(), set(), set())
        manca = sorted(cifre_l(t_l) - EN.cifre(t_it) - c_cit, key=lambda x: (len(x), x))
        if manca:
            errori.append(f"{p['p']}: cifre assenti nelle pagine italiane {rif} e nelle frasi {p['cit']}: {manca}")
        manca_d = sorted(date_l(p["lg"], t_l) - date_it_ext(t_it, html_it) - d_cit)
        if manca_d:
            errori.append(f"{p['p']}: date assenti nelle fonti: {manca_d}")
        manca_e = sorted(euro_l(t_l) - EN.euro_it(t_it) - e_cit)
        if manca_e:
            errori.append(f"{p['p']}: importi in euro assenti nelle fonti: {manca_e}")
        if f'lang="{p["lg"]}"' not in html[:200]:
            errori.append(f"{p['p']}: manca lang=\"{p['lg']}\"")
        if p["it"] and not re.search(r'<main.*<a href="[^"]+" hreflang="it" lang="it">', html, re.S):
            errori.append(f"{p['p']}: manca il link visibile alla pagina italiana")
        lead = re.search(r'<p class="lead">(.*?)</p>', html, re.S)
        prima = re.split(r"(?<=[.])\s(?=[A-ZА-ЯІЇЄҐĂÂÎȘȚ])", re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", lead.group(1)))).strip() if lead else "")[0]
        fonte_re, data_re = PRIMA[p["lg"]]
        if not (lead and re.search(fonte_re, prima) and re.search(data_re, prima) and date_l(p["lg"], prima)):
            errori.append(f"{p['p']}: la prima frase non dice fonte e data: «{prima[:140]}»")
        if not re.search(DECIDE[p["lg"]], t_l, re.I):
            errori.append(f"{p['p']}: manca «decide la Prefettura/Questura» tradotto")
        if 'rel="sponsored' in html or "amazon." in html or "italki" in html:
            errori.append(f"{p['p']}: link di affiliazione in una pagina {p['lg']} senza riga di trasparenza tradotta")
        if not re.search(r'<nav class="menu".*?<details class="lingue">', html, re.S):
            errori.append(f"{p['p']}: manca il menu delle lingue")
    # hreflang reciproci su tutto il sito
    per_url, alt_di = {}, {}
    for f in sito.rglob("*.html"):
        t = f.read_text(encoding="utf-8")
        c = RE_CANON.search(t)
        if not c:
            continue
        per_url[c.group(1)] = f
        alt = RE_ALT.findall(t)
        if alt:
            alt_di[c.group(1)] = dict(alt)
        lang = re.search(r'<html lang="([a-z]+)"', t)
        rel_p = str(f.relative_to(sito))
        if lang and lang.group(1) != "it" and f.name == "index.html":
            rel_p = rel_p[:-10]
        if lang and lang.group(1) in ORDINE and f.name != "404.html":
            g = gruppo(lang.group(1), rel_p)
            attesi = {x: f"{G.URL_SITO}/{url_rel(v)}" for x, v in g.items()}
            if g:
                attesi["x-default"] = attesi.get("it") or attesi.get("en")
            if dict(alt) != attesi:
                errori.append(f"hreflang: {rel_p} ha {dict(alt)}, attesi {attesi}")
            if lang.group(1) != "it" or g:
                if not re.search(r'<nav class="menu".*?<details class="lingue">', t, re.S):
                    errori.append(f"{rel_p}: manca il menu delle lingue")
    for url, alt in alt_di.items():
        lingua = next((x for x in ("en", "uk", "ro") if f"{G.URL_SITO}/{x}/" in url), "it")
        if alt.get(lingua) != url:
            errori.append(f"hreflang: {url} non indica sé stessa come «{lingua}»")
        if "x-default" not in alt or alt["x-default"] != alt.get("it", alt.get("en")):
            errori.append(f"hreflang: {url} senza x-default corretto: {alt}")
        for lg, dest in alt.items():
            if dest not in per_url:
                errori.append(f"hreflang: {url} → {dest} ({lg}) non esiste")
            elif alt_di.get(dest) != alt:
                errori.append(f"hreflang: {url} → {dest} non reciproco")
    # calcolatore: stesso blocco di calcolo in 4 lingue
    blocco = lambda t: t[t.find("/*calcolo-inizio*/"): t.find("/*calcolo-fine*/")]  # noqa: E731
    pagine_calc = ["reddito-minimo-cittadinanza/index.html", "en/income-requirement-italian-citizenship/index.html",
                   "uk/dokhid-dlia-hromadianstva/index.html", "ro/venit-minim-cetatenie/index.html"]
    blocchi = {p: blocco(leggi(p)) for p in pagine_calc}
    if not blocchi[pagine_calc[0]] or len(set(blocchi.values())) != 1:
        errori.append("calcolatore: il blocco di calcolo non è identico nelle 4 lingue")
    # pagine italiane accoppiate: menu con i link alle lingue che hanno l'equivalente
    for lg, righe in PAGINE.items():
        for p_, it, _, _, _ in righe:
            if it and not re.search(rf'<details class="lingue">.*?href="[^"]*{re.escape(url_rel(p_))}" hreflang="{lg}"', leggi(it), re.S):
                errori.append(f"{it}: il menu lingue non porta a {p_}")
    if errori:
        raise SystemExit("ERRORI NELLE SEZIONI /uk/ e /ro/:\n" + "\n".join(errori))
    return {lg: sum(1 for p in SCRITTE if p["lg"] == lg) for lg in PAGINE}


from genera_lingue_pagine import genera  # noqa: E402,F401  (le pagine stanno in un file a parte; qui struttura, lingue e controlli)
