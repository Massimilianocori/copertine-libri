"""Documenti e visti per chi ha la cittadinanza italiana: legge le schede Paese di Viaggiare Sicuri (Unità di Crisi del Ministero degli Affari
Esteri e della Cooperazione Internazionale) e scrive dati/documenti_it.json con i FATTI, non con i testi.

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/documenti_it.py              # scarica le schede nuove o più vecchie di 20 ore (223 richieste, 3-4 minuti)
    python3 -I beforeyoufly/raccolta/documenti_it.py --impronte EGY TUR   # stampa le impronte attuali dei campi (per dati/documenti_it_manuali.json)
    BYF_OFFLINE=1 python3 -I beforeyoufly/raccolta/documenti_it.py   # rilegge solo la cache, senza rete
    BYF_CACHE_ORE=0 python3 -I beforeyoufly/raccolta/documenti_it.py # riscarica tutto

Fonte (file JSON pubblici dell'applicazione www.viaggiaresicuri.it, robots.txt "Allow: /"):
    elenco:  https://www.viaggiaresicuri.it/schede_paese/lista_nazioni.json        (223 Paesi, codici ISO)
    scheda:  https://www.viaggiaresicuri.it/schede_paese/<ISO3>.json               (updateDate, cronologia, "Requisiti di ingresso")
    pagina:  https://www.viaggiaresicuri.it/find-country/country/<ISO3>            (link mostrato sul sito)
Campi usati: infoRequisitiIngresso > "Passaporto" e "Visto di ingresso"; infoPrimopiano > "Documenti e visti" solo come controllo
di coerenza (se dice il contrario dei Requisiti di ingresso, niente riassunto).

Licenza (verificata il 18/10/2026): viaggiaresicuri.it non indica una licenza; le note legali di esteri.it dicono che i testi sono protetti dal
diritto d'autore. Scelta prudente: il repository (pubblico) e il sito NON contengono i testi delle schede. La cache con i JSON grezzi sta in
raccolta/.cache/it/ (esclusa da git, come le altre cache); dati/documenti_it.json contiene solo, per ogni Paese: data della scheda, impronta
SHA-256 dei campi letti, i fatti ricavati (con parole nostre, da modelli fissi) e citazioni brevi (al massimo MAX_PAROLE parole) prese parola
per parola dal campo, che servono a mostrare su cosa si basa ogni fatto.

Regole prudenti (come per Canada e Australia):
  - documento: "passaporto o carta d'identità" SOLO se il campo Passaporto lo scrive con una formula fissa ("Passaporto oppure CIE",
    "in alternativa al passaporto è utilizzabile la CIE"...) e nessuna frase sulla carta d'identità pone condizioni (solo per turismo, per
    soggiorni fino a, purché, per via terra...); con condizioni: "solo a certe condizioni" (si legge la scheda). "Solo passaporto" se la scheda
    lo dice espressamente (unicamente, soltanto, esclusivamente, nessun altro documento) oppure se nei campi letti la carta d'identità non è
    mai nominata (e allora il sito dice proprio questo: la scheda indica il passaporto e non cita la carta d'identità);
  - validità: un numero di mesi o di giorni SOLO se tutte le frasi sulla validità residua (tolte quelle di rito "per eventuali variazioni...",
    quelle sui residenti e quelle sui documenti provvisori, "validità massima") danno lo stesso numero e nessuna ha parole di dubbio (circa,
    si consiglia, in caso di, salvo, tranne, visto, ETA...); altrimenti "per tutta la durata del soggiorno" o "in corso di validità" solo se
    sono le uniche indicazioni; altrimenti niente riassunto;
  - visto: "non serve" / "serve" SOLO se la prima frase sul visto è una formula riconosciuta, senza condizioni e senza parole di dubbio
    (temporaneo, fino al <data> salvo la sola data di scadenza dell'esenzione, preventivo, prima del viaggio, sospeso...); per "non serve", se
    il campo parla di autorizzazioni elettroniche (ESTA, eTA, ETA...), moduli, card d'arrivo, registrazioni, tasse o assicurazioni, ogni frase
    che ne parla deve essere riconosciuta (obbligo con il nome dell'autorizzazione o del modulo, oppure solo un consiglio, oppure un caso
    diverso: transiti, residenti, lavoro, soggiorni lunghi); se una sola non lo è, niente riassunto del visto. "Primo piano" non deve dire
    il contrario;
  - se un fatto non è inequivocabile: esito None e un motivo; il sito scrive "Consulta la scheda ufficiale" con il link.

Fatti scritti a mano (MANUALI): per pochi Paesi molto cercati la formula automatica non basta (es. Egitto: carta d'identità solo per turismo);
il fatto scritto a mano vale SOLO finché l'impronta del campo è quella letta il giorno della revisione: se la scheda cambia, il fatto manuale
viene scartato (si torna alla lettura automatica) e lo script lo segnala, così nessun testo scritto su una versione vecchia resta online.

Cache e ripresa: raccolta/.cache/it/ (riusa i file con meno di BYF_CACHE_ORE ore). Se legge meno dell'80 % dei Paesi dell'elenco,
dati/documenti_it.json NON viene sovrascritto (esce con 1). Le schede con data cambiata vanno in dati/documenti_it_cambi.json.
"""
import hashlib
import html as _html
import json
import os
import re
import sys
import time
import urllib.request
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
CACHE = Path(os.environ.get("BYF_CACHE") or (RADICE / "raccolta" / ".cache" / "it"))
OFFLINE = os.environ.get("BYF_OFFLINE") == "1"
CACHE_ORE = float(os.environ.get("BYF_CACHE_ORE", "20"))
BASE = "https://www.viaggiaresicuri.it/schede_paese/"
ELENCO = BASE + "lista_nazioni.json"
PAGINA = "https://www.viaggiaresicuri.it/find-country/country/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
QUOTA_MINIMA = 0.8
ROMA = ZoneInfo("Europe/Rome")
MAX_PAROLE = 20  # citazioni brevi: al massimo 20 parole (verifica.py controlla anche che nessuna pagina abbia più di 25 parole di fila della fonte)
CAMPI = {"passaporto": ("infoRequisitiIngresso", "Passaporto"), "visto": ("infoRequisitiIngresso", "Visto-di-ingresso"),
         "primo_piano": ("infoPrimopiano", "Documenti-e-visti")}
TITOLI_CAMPI = {"passaporto": "Passaporto", "visto": "Visto di ingresso", "primo_piano": "Documenti e visti (In primo piano)"}


def scarica(url, nome):
    f = CACHE / nome
    if f.exists() and (OFFLINE or time.time() - f.stat().st_mtime < CACHE_ORE * 3600):
        return json.loads(f.read_text(encoding="utf-8")), False
    if OFFLINE:
        raise FileNotFoundError(f"{nome} non è in cache")
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    for tentativo in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                corpo = r.read()
            j = json.loads(corpo)
            CACHE.mkdir(parents=True, exist_ok=True)
            f.write_bytes(corpo)
            return j, True
        except Exception:  # noqa: BLE001
            if tentativo == 3:
                raise
            time.sleep(3 + tentativo * 4)


# ------------------------------------------------------------------ testo dei campi
def righe(h):
    """HTML del campo -> righe di testo (un <br>, un paragrafo o una voce di elenco = una riga), spazi normalizzati."""
    h = re.sub(r"<br\s*/?>", "\n", h or "", flags=re.I)
    h = re.sub(r"</(?:p|li|div|h\d)>", "\n", h, flags=re.I)
    h = re.sub(r"<[^>]+>", "", h)
    h = _html.unescape(h).replace("\xa0", " ").replace("​", "")
    out = []
    for r in h.split("\n"):
        r = re.sub(r"\s+", " ", r).strip()
        if r:
            out.append(r)
    return out


def testo(rr):
    return "\n".join(rr)


def impronta(rr):
    return hashlib.sha256(testo(rr).encode("utf-8")).hexdigest()


def campo(j, nome):
    sez, nodo = CAMPI[nome]
    return righe(((j.get(sez) or {}).get("nodi") or {}).get(nodo, {}).get("contenuto", ""))


_SIGLE = re.compile(r"\b(?:N\.B|U\.S|U\.E|D\.L|n|es|ecc|art|c\.d|ca|gg|Tel|tel|Sig|St|Dott|Rep|Amm\.va|Prov|p\.es|S\.p\.A)\.$")


def frasi(riga):
    """Frasi di una riga: si spezza dopo "; " e dopo . ! ? seguiti da spazio e maiuscola (non dopo sigle come N.B., U.S., es.)."""
    finali = []
    for blocco in re.split(r"(?<=;)\s+", riga):
        out, cur = [], ""
        for pezzo in re.split(r"(?<=[.!?])\s+", blocco):
            cur = (cur + " " + pezzo).strip() if cur else pezzo
            if _SIGLE.search(cur):
                continue
            out.append(cur)
            cur = ""
        if cur:
            out.append(cur)
        # ricuci i pezzi che non cominciano con una maiuscola, una cifra o un segno (la frase precedente non era finita)
        for i, f in enumerate(out):
            if i and not re.match(r"^[A-ZÀ-Ý0-9\"“«(\-–•*]", f):
                finali[-1] += " " + f
            else:
                finali.append(f)
    return finali


def tutte_frasi(rr):
    return [f for r in rr for f in frasi(r)]


def parole(s):
    return re.findall(r"\S+", s)


def breve(s):
    """La stringa se ha al massimo MAX_PAROLE parole, altrimenti None."""
    return s if s and len(parole(s)) <= MAX_PAROLE else None


def frammento(frase, i, j, limite=MAX_PAROLE):
    """Pezzo esatto della frase tra i e j, allargato solo se i o j cadono a metà di una parola; None se supera il limite di parole."""
    while i > 0 and frase[i - 1].isalnum() and frase[i].isalnum():
        i -= 1
    while 0 < j < len(frase) and frase[j - 1].isalnum() and frase[j].isalnum():
        j += 1
    if frase[i:j].count("(") > frase[i:j].count(")") and frase[j:j + 1] == ")":
        j += 1
    s = frase[i:j].strip().rstrip(",;:").strip()
    if s.startswith("(") and s.endswith(")") and s.count("(") == 1:
        s = s[1:-1].strip()
    if s.endswith(")") and s.count("(") < s.count(")"):
        s = s[:-1].rstrip()
    if s.startswith("(") and s.count("(") > s.count(")"):
        s = s[1:].lstrip()
    return s if s and len(parole(s)) <= limite else None


# ------------------------------------------------------------------ rimando ad altra scheda (Guam, Marianne Settentrionali)
RIMANDO = re.compile(r"^Consultare la Scheda(?: Paese)?\s*(?:[“\"](?P<nome>[^”\"]+)[”\"]|https://www\.viaggiaresicuri\.it/find-country/country/(?P<iso>[A-Z]{3}))", re.I)
RIMANDO_NOMI = {"stati uniti": "USA"}


def rimando(rr):
    if not rr:
        return None
    m = RIMANDO.match(rr[0])
    if not m:
        return None
    return m.group("iso") or RIMANDO_NOMI.get((m.group("nome") or "").strip().lower())


# ------------------------------------------------------------------ documento: passaporto, carta d'identità
CIE_SI = re.compile(r"\bPassaporto\s*(?:oppure|/|o)\s*(?:con\s+)?CIE\b|\bPassaporto oppure CIE\b|\bpassaporto\s*/\s*in alternativa la CIE\b"
                    r"|\bIn alternativa al passaporto [èeé] utilizzabile la CIE\b", re.I)
NOMINA_CIE = re.compile(r"\bCIE\b|carta d['’]\s?identit[àa]|carta di identit[àa]|carte d['’]\s?identit[àa]|carte di identit[àa]|documento (?:di identit[àa] |d['’]\s?identit[àa] )?provvisori", re.I)
# frasi sulla carta d'identità che parlano di casi speciali (proroga, carta rinnovata, documento provvisorio, modello AT, patente, documenti
# danneggiati, furto, minori, residenti): non cambiano la regola per la CIE normale, ma il sito dice che la scheda ne parla
CASO_SPECIALE = re.compile(r"proroga|rinnovat|cedolino|provvisori|cartace|modello AT|tessera ferroviaria|\bAT\b|ATe\b|patente|danneggiat|deteriorat|integrit|"
                           r"integr[ae]|leggibil|smarriment|furto|minori|EU Settlement|settled|residen|scadut|cessato|transazion|bancari|pagamento con carte", re.I)
# condizioni sulla carta d'identità: le "forti" valgono anche nelle frasi sui casi speciali (Turchia: "in condizioni di perfetta integrità ...
# per: - coloro i quali facciano ingresso ... dal confine greco"), le "deboli" solo fuori dai casi speciali
CONDIZIONE_FORTE = re.compile(r"\bsolo\b|\bsola (?:CIE|carta)|soltanto|esclusivamente|purch[ée]|a condizione|per soggiorni|per via (?:aerea|terr|ferrov|marit)|dal confine|dai confini|confin|transit|"
                              r"accompagnat|per turismo|per:", re.I)
CONDIZIONE_DEBOLE = re.compile(r"tuttavia|non (?:sempre )?(?:viene |vengono |è |e['’] |é )?(?:accettat|riconosciut|consentit)|per recarsi|extra-?UE", re.I)
MAIUSCOLO_NON = re.compile(r"\bNON\b")


def SOLO_PROVVISORIO(x):
    """Frase sul documento provvisorio cartaceo che non nomina la CIE o la carta d'identità: caso speciale, non una condizione sulla CIE."""
    return bool(re.search(r"provvisori", x, re.I)) and not re.search(r"\bCIE\b|carta d['’]\s?identit|carta di identit", x, re.I)
ALTRI_CITTADINI = re.compile(r"cittadinanz|binazional|doppi cittadini|italo-|anche della cittadinanza|di residenza|residenti|identit[àa][’']? locale", re.I)
SOLO_PASSAPORTO = re.compile(r"(?:UNICAMENTE|unicamente|soltanto|esclusivamente) (?:con (?:il |un )?|ove in possesso di (?:un )?)?passaporto"
                             r"|Non [èe] ammesso alcun altro documento di viaggio", re.I)
PASSAPORTO_SI = re.compile(r"^(?:Il passaporto [èe] necessario|Passaporto necessario|(?:[EÈ]['’]? |È |è |e['’] )?(?:necessari[oa]|obbligatori[oa]|richiest[oa])\b"
                           r"|(?:[EÈ]['’]?|È|è) (?:necessario|obbligatorio) (?:il|un) passaporto|Necessario il passaporto|È necessario (?:essere in possesso di|possedere) un passaporto"
                           r"|Il passaporto (?:in corso di validità )?è necessario|Il passporto in corso di validità è necessario|Passaporto,|passaporto in corso di validità\."
                           r"|passaporto necessario|E['’] necessario,|È richiesto|E['’] richiesto il passaporto|Per entrare in [^,]+, è necessario (?:il|un) passaporto"
                           r"|Passaporto con validit|Il passaporto deve (?:essere valido|avere)|Il passaporto italiano deve avere|Per [A-Z][^,]+, il passaporto italiano deve avere"
                           r"|La validit[àá] residua del passaporto)", re.I)
PASSAPORTO_ESPLICITO = re.compile(r"(?:[èeé]['’]?|È) necessario (?:il|un) passaporto", re.I)


def documento(pp, vv, prim):
    """Esito: 'cie' (passaporto o carta d'identità elettronica), 'cie_condizioni', 'solo_passaporto' (la scheda lo dice), 'passaporto'
    (la scheda indica il passaporto e nei campi letti non nomina mai la carta d'identità), None (non inequivocabile)."""
    if not pp:
        return {"esito": None, "motivo": "La scheda non ha il campo Passaporto."}
    ff = tutte_frasi(pp)
    for f in ff:
        m = SOLO_PASSAPORTO.search(f)
        if m:
            cit = breve(f) or frammento(f, m.start(), m.end())
            return {"esito": "solo_passaporto", "citazione": cit, "campo": "passaporto"}
    m = None
    for f in ff:
        m = CIE_SI.search(f)
        if m:
            break
    if m:
        cit = frammento(f, m.start(), m.end())
        sulla_cie = [x for x in ff if NOMINA_CIE.search(x) and not ALTRI_CITTADINI.search(x) and not SOLO_PROVVISORIO(x)]
        provvisorio = [x for x in ff if SOLO_PROVVISORIO(x)]
        condizioni = [x for x in sulla_cie if CONDIZIONE_FORTE.search(x) or
                      ((CONDIZIONE_DEBOLE.search(x) or MAIUSCOLO_NON.search(x)) and not CASO_SPECIALE.search(x))]
        speciali = [x for x in sulla_cie if CASO_SPECIALE.search(x) and x not in condizioni] + provvisorio
        if condizioni:
            c = condizioni[0]
            mc = CONDIZIONE_FORTE.search(c) or CONDIZIONE_DEBOLE.search(c) or MAIUSCOLO_NON.search(c)
            return {"esito": "cie_condizioni", "citazione": cit, "campo": "passaporto",
                    "condizione": breve(c) or frammento(c, max(0, mc.start() - 60), mc.end() + 60)}
        return {"esito": "cie", "citazione": cit, "campo": "passaporto", "note_speciali": bool(speciali)}
    nomina = [x for x in ff + tutte_frasi(vv) + tutte_frasi(prim) if NOMINA_CIE.search(x) and not ALTRI_CITTADINI.search(x)]
    if nomina:
        return {"esito": None, "motivo": "La scheda parla della carta d'identità in un modo che non si può riassumere in una riga."}
    f = ff[0]
    m = PASSAPORTO_SI.match(f) or PASSAPORTO_ESPLICITO.search(f)
    if not m:
        return {"esito": None, "motivo": "La scheda non dice in modo semplice quale documento serve."}
    fine = re.search(r"[,.;:]|$", f[m.end():])
    return {"esito": "passaporto", "citazione": frammento(f, m.start(), m.end() + fine.start()) or frammento(f, m.start(), m.end()), "campo": "passaporto"}


# ------------------------------------------------------------------ validità residua
NUMERI_P = {"un": 1, "uno": 1, "una": 1, "due": 2, "tre": 3, "quattro": 4, "cinque": 5, "sei": 6, "dodici": 12}
_N = r"(?P<n>\d+|due|tre|quattro|cinque|sei|dodici)(?:\s*\(\s*\w+\s*\))?"
_U = r"(?P<u>mesi|mese|giorni|gg|anni|anno)\b(?:\s*\([^)]{0,20}\))?"
_VAL = r"validit(?:à|á|a['’]|a)"
SCHEMI_VALIDITA = [
    re.compile(_VAL + r"(?:\s+residua)?(?:\s+minima)?\s+(?:di\s+|pari ad?\s+|non inferiore a\s+|superiore ai?\s+|di oltre\s+)?(?:almeno\s+|circa\s+|oltre\s+)?" + _N + r"\s+" + _U, re.I),
    re.compile(r"(?:almeno|minimo di)\s+" + _N + r"\s+" + _U + r"\s+di\s+" + _VAL + r"(?:\s+residua)?", re.I),
    re.compile(r"\bcon\s+" + _N + r"\s+" + _U + r"\s+di\s+" + _VAL + r"(?:\s+residua)?", re.I),
    re.compile(r"scadenza superiore di almeno\s+" + _N + r"\s+" + _U, re.I),
    re.compile(r"valid[oa] per almeno\s+" + _N + r"\s+" + _U, re.I),
    re.compile(r"validit[àaá] residua del passaporto,[^.;]{0,60}?pari ad almeno\s+" + _N + r"\s+" + _U, re.I),
]
# frasi da non considerare: le formule di rito ("per eventuali variazioni ... informarsi"), i residenti, i permessi di soggiorno, la validità
# massima dei documenti provvisori
DI_RITO = re.compile(r"variazion|modifich|informarsi|informazioni|si consiglia di informarsi|per ulteriori|aggiornamenti", re.I)
ALTRI_CASI_VAL = re.compile(r"residen|permesso di soggiorno|validit(?:à|a['’]|a) massima|provvisori|per recarsi|extra-?UE|Paesi terzi|in caso di (?:scalo|transito)|"
                            r"per spostarsi|pi[ùu] di \d+|oltre i? ?\d+ giorni|superior[ei] ai? \d+|registrare il soggiorno", re.I)
DUBBIO_VALIDITA = re.compile(r"\bcirca\b|consigli|suggeri|raccomand|in caso di|scadenza del visto|data del visto|domanda di visto|esenti da visto|ingressi esenti|"
                             r"\bETA\b|eVisa|per soggiorni|tranne|\bsalvo\b|in genere|non [èeé] pi[ùu]|non [èeé] richiest|(?<!non )inferiore|eccedere|"
                             r"preferibil|opportun|potrebb|possibilit", re.I)
SOGGIORNO = re.compile(r"(?:validit[àaá’']*|valid[oa]|scadenza)[^.;]{0,45}?(?:durata (?:prevista )?del soggiorno|periodo di permanenza|periodo di soggiorno|intero periodo"
                       r"|intera durata|tutta la durata|tutto il periodo)(?:\s+(?:di|del)\s+(?:soggiorno|permanenza))?(?:\s+(?:nel Paese|in [A-Z]\w+))?", re.I)
RIENTRO = re.compile(r"scadenza successiva alla data (?:prevista per il |del )?(?:rientro|ritorno)", re.I)
IN_CORSO = re.compile(r"in corso di validit[àaá]", re.I)
ARRIVO = re.compile(r"(?:alla|dalla) data (?:di |d['’]|prevista di )?(?:arrivo|ingresso)|al momento dell['’]\s?(?:arrivo|ingresso|entrata)|dal (?:momento|giorno) "
                    r"(?:dell['’]\s?|di )(?:arrivo|ingresso)|dalla data d['’]\s?ingresso|dal momento dell['’]entrata|dopo la data d['’]\s?ingresso|successivi alla "
                    r"data di ingresso|al momento dell['’] ingresso", re.I)
USCITA = re.compile(r"rientro dall['’]|uscita dall[ae']|uscita/|partenza/uscita|lasciare il Paese|si prevede di lasciare", re.I)
OLTRE_SOGGIORNO = re.compile(r"oltre la durata del soggiorno|oltre il termine del periodo di soggiorno|oltre il periodo di soggiorno", re.I)
CODA_RIF = re.compile(r"^\s*,?\s*(?:al momento|alla data|dalla data|dal momento|dal giorno|a partire|oltre|rispetto|dopo|successivi|dalla scadenza)"
                      r"(?:(?! ed | e almeno| e con | e due | e \d)[^,;.(:])*", re.I)


def _norm_u(u):
    u = u.lower()
    return "mesi" if u.startswith("mes") else ("anni" if u.startswith("ann") else "giorni")


def validita(pp):
    """Esito: 'numero' (n, unità), 'soggiorno', 'rientro', 'in_corso', None."""
    if not pp:
        return {"esito": None, "motivo": "La scheda non ha il campo Passaporto."}
    ff = [f for f in tutte_frasi(pp) if not DI_RITO.search(f)]
    trovati = []  # (frase, match, valore)
    for f in ff:
        if ALTRI_CASI_VAL.search(f):
            continue
        for rx in SCHEMI_VALIDITA:
            for m in rx.finditer(f):
                if any(t[0] == f and t[1].start() <= m.start() < t[1].end() for t in trovati):
                    continue
                n = m.group("n").lower()
                trovati.append((f, m, (NUMERI_P.get(n) or int(n), _norm_u(m.group("u")))))
    if trovati:
        valori = {t[2] for t in trovati}
        if len(valori) > 1:
            return {"esito": None, "motivo": "La scheda indica più di una validità residua (per casi diversi)."}
        for f, m, _ in trovati:
            if DUBBIO_VALIDITA.search(f):
                return {"esito": None, "motivo": "La scheda indica la validità con condizioni o consigli che non si possono riassumere in una riga."}
        f, m, (n, u) = trovati[0]
        if u == "anni":
            return {"esito": None, "motivo": "Validità espressa in anni: leggi la scheda."}
        coda = CODA_RIF.match(f[m.end():])
        fine = m.end() + (coda.end() if coda else 0)
        cit = breve(f) or frammento(f, m.start(), fine) or frammento(f, m.start(), m.end())
        return {"esito": "numero", "n": n, "unita": u, "citazione": cit, "campo": "passaporto",
                "dall_ingresso": bool(ARRIVO.search(cit or "")), "dall_uscita": bool(USCITA.search(cit or "")),
                "oltre_soggiorno": bool(OLTRE_SOGGIORNO.search(cit or ""))}
    ss = [f for f in ff if SOGGIORNO.search(f) and not ALTRI_CASI_VAL.search(f)]
    rr = [f for f in ff if RIENTRO.search(f)]
    if ss and not rr:
        f = ss[0]
        if DUBBIO_VALIDITA.search(f):
            return {"esito": None, "motivo": "La scheda indica la validità con condizioni che non si possono riassumere in una riga."}
        m = SOGGIORNO.search(f)
        return {"esito": "soggiorno", "citazione": breve(f) or frammento(f, m.start(), m.end()), "campo": "passaporto"}
    if rr and not ss:
        f = rr[0]
        m = RIENTRO.search(f)
        if DUBBIO_VALIDITA.search(f):
            return {"esito": None, "motivo": "La scheda indica la validità con condizioni che non si possono riassumere in una riga."}
        return {"esito": "rientro", "citazione": breve(f) or frammento(f, m.start(), m.end()), "campo": "passaporto"}
    if ss or rr:
        return {"esito": None, "motivo": "La scheda dà più indicazioni sulla validità: leggila."}
    cc = [f for f in ff if IN_CORSO.search(f) and not ALTRI_CASI_VAL.search(f)]
    altre = [f for f in ff if re.search(r"validit|scadenz", f, re.I) and f not in cc and not ALTRI_CASI_VAL.search(f)]
    if cc and not altre:
        f = cc[0]
        m = IN_CORSO.search(f)
        return {"esito": "in_corso", "citazione": breve(f) or frammento(f, max(0, m.start() - 40), m.end()), "campo": "passaporto"}
    return {"esito": None, "motivo": "La scheda non indica in modo chiaro una validità residua minima."}


# ------------------------------------------------------------------ visto
_NON_E = r"non (?:(?:[èeé]['’]?|e['’])\s*)?(?:,\s*)?(?:(?:pertanto|quindi|invece),?\s*)?(?:pi[ùu] )?"
NEG_VISTO = re.compile(_NON_E + r"(?:necessari[oa]|richiest[oa]|obbligatori[oa])|non necessit|non (?:hanno|ha) bisogno|\besent[iea]\b|esentati|"
                       r"esenzione dal(?:l['’]obbligo (?:di|del))? visto|senza (?:necessit[àa] di |l['’]obbligo (?:di|del) |(?:dover )?richiedere (?:il |un )?)?visto|"
                       r"nessuna tipologia di visto|non (?:viene|è) (?:pi[ùu] )?richiest|non (?:serve|occorre)|non vi [èe] obbligo di visto|non è richiesto alcun visto", re.I)
NEC_VISTO = re.compile(r"^(?:(?:Il )?visto(?: d['’]\s?ingresso| di ingresso| turistico)? (?:[èe] )?(?:necessario|obbligatorio|richiesto)|"
                       r"(?:[EÈ]['’]?|È) (?:necessario|obbligatorio) (?:ottenere |richiedere |munirsi di )?(?:un |il )?visto(?: d['’]\s?ingresso| di ingresso)?|"
                       r"Necessari[oa]|Obbligatori[oa]|Visto obbligatorio)\b", re.I)
CONDIZ_NEC = re.compile(r"super|pi[ùu] di|oltre|diversi da|solo per i viaggiatori|eccedent|per una permanenza che|tranne|salvo|ad eccezione|eccetto|per scopi|"
                        r"autorizzazion", re.I)
# parole che rendono la frase "non serve il visto" non inequivocabile (visto all'arrivo, esenzione temporanea o preventiva, autorizzazioni...)
DUBBIO_VISTO = re.compile(r"temporane|sospes|in genere|generalmente|di norma|di solito|\bsalvo\b|tranne|eccetto|ad eccezione|\bpu[òo]\b|potrebb|"
                          r"consigli|suggeri|preventiv|prima del viaggio|prima di arrivare|all['’]\s?arrivo|in aeroporto|alla frontiera|ottenerl|rilasciat|timbro|"
                          r"autorizzazion|ricevono|pilota|sperimental|a partire dal gennaio|il provvedimento|caso per caso|valuter|(?-i:\bE?TA\b|\beTA\b|\bESTA\b)", re.I)
FINO_AL = re.compile(r"\b[Ff]ino al (\d{1,2})°? (gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre) (\d{4})")
MESI_IT = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
_D = r"(?:\d+|tre|sei|un|una|due|dodici|trenta)(?:\s*\(\s*\w+\s*\))?\s*(?:giorni|gg|mesi|mese|anno|settimane)\b"
DUR_QUALSIASI = re.compile(_D, re.I)
DURATA = re.compile(r"(?:(?:per|in caso di) (?:soggiorn[io]|un soggiorno|permanenze|un periodo|periodi|viaggi|brevi soggiorni)[^,.;:]{0,50}?|(?:fino|sino) ad? (?:un massimo di )?|"
                    r"inferiori? a(?:i|l)? |non superior[ei] a(?:i|l)? |massim[oa](?: consecutivo)? di |della durata massima[^,.;]{0,25}? di |per il periodo di |"
                    r"di una durata massima di |per un massimo di |entro |senza visto[^.;]{0,50}? è di )" + r"[^,.;:]{0,30}?" + _D, re.I)
CODA_DURATA = re.compile(r"^(?:\s*\([^)]{0,30}\))?(?:,? ?(?:ogni|nell['’]\s?arco di|in un periodo (?:totale )?di|su un arco di tempo di|all['’]interno di|in un semestre|"
                         r"nell['’]arco dell['’]anno|per anno|all['’]anno|l['’]anno|per entrata|per ingresso|per ciascun ingresso)[^,.;]{0,40})?", re.I)
# formalità: autorizzazioni elettroniche, moduli, card, registrazioni, tasse, assicurazioni
FORMALITA = re.compile(r"\bESTA\b|\beTA\b|\bETA\b|NZeTA|K-ETA|ETA-IL|\bTDAC\b|\bMDAC\b|\bED\b|\bQR\b|\bCard\b|"
                       r"(?i:Electronic Travel Authori[sz]ation|autorizzazione (?:elettronica|di viaggio|all['’]\s?ingresso)|\bmodul[oi]\b|formulari|Arrival Card|"
                       r"registra(?:re|rsi|zione)|dichiarazione|Declaration|\btass[ae]\b|\bfee\b|assicurazion|Entry Form|Travel Form|prearrival|pre-?registra|"
                       r"comunicare l['’]\s?indirizzo|residenza temporanea)")
OBBLIGO = re.compile(r"[èeé]['’]? (?:necessari|obbligatori|richiest)|obbligatori|\bobbligo\b|devono|dovranno|occorre|bisogna|[èe] richiesto|sono tenuti|tenuti a|deve essere|"
                     r"va (?:richiest|compilat|ottenut)|necessario (?:compilare|ottenere|richiedere|munirsi)", re.I)
CONSIGLIO = re.compile(r"si consiglia|consigliat|si invita|sono invitati|si invitano|raccomand|suggerisce|si suggerisce|facoltativ|è possibile", re.I)
# casi diversi dal turista che entra (non cambiano il riassunto; il sito dice che la scheda ne parla)
ALTRI_CASI_VISTO = re.compile(r"transit|\bscal[oi]\b|residen|lavor|studi|giornalist|soggiorni? (?:superior|oltre|pi[ùu] lung|prolungat)|oltre i \d+|pi[ùu] di \d+|"
                              r"superiore ai|Irlanda del Nord|doppi[ae] cittadinanz|binazional|diplomatic|di servizio|minori|animali|droni|persona non grata|overstay|espulsion", re.I)
TASSA_USCITA = re.compile(r"tass[ae] (?:aeroportual|di imbarco|di sicurezza aeroportuale|di partenza|in partenza|d['’]uscita)|in partenza dall['’]aeroporto|all['’]uscita dal Paese", re.I)
REGISTRAZIONE_LOCALE = re.compile(r"registra(?:re|rsi|zione)[^.]{0,80}(?:polizia|entro \d+ ore|dall['’]arrivo|albergo|alloggi|ufficio stranieri|ufficio del turismo)|"
                                  r"(?:polizia|albergo|alloggi)[^.]{0,80}registra|predetta registrazione|registrazione viene effettuata|"
                                  r"entro \d+ ore dall['’]arrivo[^.]{0,160}(?:comunicare l['’]\s?indirizzo|residenza temporanea)", re.I)
# frasi che parlano solo di tasse o costi (nessun modulo, card, registrazione o autorizzazione): il sito dice che la scheda cita tasse
SOLO_TASSA = re.compile(r"\btass[ae]\b|\bfee\b", re.I)
ALTRE_FORMALITA = re.compile(r"\bESTA\b|\beTA\b|\bETA\b|NZeTA|K-ETA|\bED\b|\bQR\b|\bCard\b|(?i:autorizzazion|modul[oi]|formulari|registra|dichiarazione|Declaration|assicurazion|tessera|tarjeta|Form\b)")
# nomi delle formalità obbligatorie riconosciute (per il riassunto): nome mostrato, tipo in parole nostre
NOMI_FORMALITA = [
    (re.compile(r"\bESTA\b"), "ESTA", "autorizzazione elettronica"), (re.compile(r"NZeTA"), "NZeTA", "autorizzazione elettronica"),
    (re.compile(r"K-ETA"), "K-ETA", "autorizzazione elettronica"), (re.compile(r"ETA-IL"), "ETA-IL", "autorizzazione elettronica"),
    (re.compile(r"\beTA\b"), "eTA", "autorizzazione elettronica"), (re.compile(r"\bETA\b"), "ETA", "autorizzazione elettronica"),
    (re.compile(r"Thailand Digital Arrival Card|\bTDAC\b"), "Thailand Digital Arrival Card (TDAC)", "carta d'arrivo digitale"),
    (re.compile(r"Malaysia Digital Arrival Card|\bMDAC\b"), "Malaysia Digital Arrival Card (MDAC)", "carta d'arrivo digitale"),
    (re.compile(r"SG Arrival Card"), "SG Arrival Card", "carta d'arrivo digitale"),
    (re.compile(r"e-Arrival Card"), "e-Arrival Card (eTravel)", "carta d'arrivo digitale"),
    (re.compile(r"modulo ED\b"), "modulo ED online (Embarkation/Disembarkation)", "modulo d'ingresso"),
]
INIZIO_VISTO = re.compile(r"^(?:[èe] )?(?:non )?(?:[èe] )?(?:necessari|obbligatori|richiest)", re.I)


def _frase_visto(vv):
    """Prima frase che parla del visto (salta titoli in maiuscolo e righe di soli link). La prima frase del campo vale anche senza la parola
    "visto" se dice "non è necessario"/"necessario" (il campo si chiama "Visto di ingresso": Malaysia "Per turismo, non è necessario, ...")."""
    ff = tutte_frasi(vv)
    if ff and not ff[0].isupper() and re.match(r"^(?:Per turismo,? )?" + _NON_E + r"(?:necessari|richiest)", ff[0], re.I):
        return ff[0]
    for f in ff:
        if f.isupper() or (len(parole(f)) < 2 and not INIZIO_VISTO.match(f)):
            continue
        if re.search(r"\bvist[oi]\b|\bvisa\b|esent", f, re.I) or INIZIO_VISTO.match(f):
            return f
    return None


def _durata(f):
    """Pezzo della frase con la durata ammessa; None se nella frase ci sono durate fuori da quel pezzo (frase con più casi)."""
    mm = list(DURATA.finditer(f))
    if not mm:
        return None
    i, j = mm[0].start(), mm[-1].end()
    coda = CODA_DURATA.match(f[j:])
    if coda:
        j += coda.end()
    if any(d.start() < i or d.end() > j for d in DUR_QUALSIASI.finditer(f)):
        return None
    k = f.find(" è di ", i, j)  # "Il limite per il soggiorno ... senza visto di ingresso è di 90 giorni ...": si cita dal numero
    if k >= 0:
        i = k + len(" è di ")
    return frammento(f, i, j)


def _citazione_neg(f):
    """Citazione breve di una frase "non serve il visto": tutta la frase se breve, altrimenti dall'inizio fino alla parola visto (o alla negazione),
    altrimenti solo il pezzo tra negazione e "visto"."""
    if breve(f):
        return f
    m = NEG_VISTO.search(f)
    v = min((x for x in re.finditer(r"\bvist[oi]\b[^,.;:()]{0,25}?(?=[,.;:(]|\s+per\b|\s+se\b|$)", f, re.I)),
            key=lambda x: abs(x.start() - m.end()), default=None)
    i, j = m.start(), m.end()
    if v and abs(v.start() - m.end()) < 60:
        i, j = min(i, v.start()), max(j, v.end())
    return frammento(f, 0, j) or frammento(f, i, j) or frammento(f, m.start(), m.end())


def _cit_formalita(fr, rx):
    m = rx.search(fr)
    fine = re.search(r"[,.;:]|$", fr[m.end():])
    return breve(fr) or frammento(fr, 0, m.end() + fine.start()) or frammento(fr, max(0, m.start() - 70), m.end())


def _formalita(vv):
    """Classifica ogni frase del campo Visto che parla di formalità: 'obbligo' (con il nome riconosciuto), 'spiega' (dettagli della stessa),
    'consiglio', 'altro' (transiti, residenti, lavoro, soggiorni lunghi...), 'tassa_uscita', 'registrazione_locale', '?' (non riconosciuta)."""
    out, precedente = [], None
    for f in tutte_frasi(vv):
        prev, precedente = precedente, f
        if not FORMALITA.search(f):
            continue
        nome = next(((n, t, rx) for rx, n, t in NOMI_FORMALITA if rx.search(f)), None)
        if (TASSA_USCITA.search(f) or SOLO_TASSA.search(f)) and not nome and not ALTRE_FORMALITA.search(f):
            out.append(("tassa_uscita", None, None, f))
            continue
        if ALTRI_CASI_VISTO.search(f) and not re.search(r"tutti i (?:viaggiatori|passeggeri)|cittadini italiani|turist|\bil visitatore\b|residenza temporanea", f, re.I):
            out.append(("altro", None, None, f))
            continue
        if REGISTRAZIONE_LOCALE.search(f) and not nome:
            out.append(("registrazione_locale", None, None, f))
            continue
        if CONSIGLIO.search(f) and not OBBLIGO.search(f):
            out.append(("consiglio", None, None, f))
            continue
        if OBBLIGO.search(f) and nome and not re.search(r"\bnon\b|potrebb|\bpu[òo]\b|in caso di|se:|\bse\b", f, re.I):
            out.append(("obbligo", nome[0], nome[1], f))
            continue
        if nome and any(o[0] == "obbligo" and o[1] == nome[0] for o in out) and not OBBLIGO.search(f):
            out.append(("spiega", nome[0], None, f))
            continue
        # dettagli della frase appena prima (stesso modulo: "Una volta compilati i campi richiesti, si genererà un file PDF con un codice QR...")
        if out and out[-1][0] in ("obbligo", "consiglio", "spiega") and out[-1][3] == prev and not OBBLIGO.search(f):
            out.append(("spiega", out[-1][1], None, f))
            continue
        out.append(("?", None, None, f))
    return out


PP_NECESSARIO = re.compile(r"(?:[èeé]['’]? |È )(?:necessari|obbligatori)[oa] (?:il |un |ottenere (?:il |un )?|richiedere (?:il |un )?)?visto|"
                           r"\bvisto(?: d['’]\s?ingresso| di ingresso| turistico)? (?:[èeé] )?(?:necessari|obbligatori)[oa]|^Visto(?: d['’]\s?ingresso| di ingresso)?: (?:necessari|obbligatori)", re.I)


def _esito_primo_piano(prim):
    """Esito del visto secondo 'In primo piano': insieme di 'non_necessario' / 'necessario' (vuoto se non lo dice)."""
    ee = set()
    for f in tutte_frasi(prim):
        if not re.search(r"\bvist[oi]\b|esent", f, re.I):
            continue
        if NEG_VISTO.search(f):
            ee.add("non_necessario")
        elif PP_NECESSARIO.search(f) and not CONDIZ_NEC.search(f) and not re.search(r"\bnon\b", f, re.I):
            ee.add("necessario")
    return ee


PP_SALTA = re.compile(r"^Consult|^Si (?:consulti|rimanda)|passaporto|\bCIE\b|carta d['’]\s?identit", re.I)


def obblighi_primo_piano(prim, nomi_noti=()):
    """Obblighi (moduli, dichiarazioni, card, registrazioni, assicurazioni) che il riquadro "In primo piano" scrive come obbligatori per tutti i
    viaggiatori e che il campo Visto non nomina con un nome riconosciuto: il sito li mostra con una citazione breve (al massimo MAX_PAROLE parole,
    un inizio di frase seguito da "(…)" se la frase è più lunga), così la pagina non tace un obbligo scritto solo lì."""
    out = []
    for f in tutte_frasi(prim):
        if not FORMALITA.search(f) or not OBBLIGO.search(f) or PP_SALTA.search(f):
            continue
        if ALTRI_CASI_VISTO.search(f) and not re.search(r"tutti i (?:viaggiatori|passeggeri|cittadini stranieri)|cittadini italiani|turist", f, re.I):
            continue
        if CONSIGLIO.search(f) and not re.search(r"obbligatori|necessari|devono|tenuti", f, re.I):
            continue
        if re.search(r"\bnon\b[^.]{0,30}(?:obbligatori|necessari|richiest)", f, re.I):
            continue
        if any(rx.search(f) and n in nomi_noti for rx, n, _ in NOMI_FORMALITA):
            continue
        q = breve(f)
        if not q:
            testa = " ".join(parole(f)[:MAX_PAROLE - 1])
            if OBBLIGO.search(testa) and FORMALITA.search(testa):  # l'obbligo è nelle prime parole: inizio della frase
                q = testa.rstrip(",;:") + " " + ELISIONE
            else:  # altrimenti dalla parola dell'obbligo in poi
                i = f.rfind(" ", 0, OBBLIGO.search(f).start()) + 1
                ww = parole(f[i:])
                q = ELISIONE + " " + " ".join(ww[:MAX_PAROLE]).rstrip(",;:") + (" " + ELISIONE if len(ww) > MAX_PAROLE else "")
        out.append(pulisci_citazione(q) if ELISIONE not in q else q)
    return out


def visto(vv, prim):
    if not vv:
        return {"esito": None, "motivo": "La scheda non ha il campo Visto di ingresso."}
    f = _frase_visto(vv)
    if not f:
        return {"esito": None, "motivo": "Il campo sul visto non dice in modo semplice se il visto serve."}
    pp = _esito_primo_piano(prim)
    out = {"campo": "visto", "turismo": bool(re.search(r"turis", f, re.I))}
    tutto = testo(vv)
    if NEG_VISTO.search(f) and not re.search(r"^(?:Il )?visto(?: d['’]\s?ingresso| di ingresso)? (?:è )?(?:necessario|obbligatorio)", f, re.I):
        fino = FINO_AL.search(f)
        if DUBBIO_VISTO.search(f) or (fino and not FINO_AL.match(f.strip())):
            return {"esito": None, "motivo": "La regola sul visto ha condizioni (per esempio un'esenzione temporanea, un visto all'arrivo o una richiesta prima della partenza) che non si possono riassumere in una riga."}
        if "necessario" in pp:
            return {"esito": None, "motivo": "Il riquadro “In primo piano” della scheda dice che il visto è necessario: leggi la scheda."}
        form = _formalita(vv)
        if any(x[0] == "?" for x in form):
            return {"esito": None, "motivo": "La scheda parla anche di autorizzazioni, moduli, registrazioni o tasse che non si possono riassumere in una riga: leggila per intero."}
        durata = _durata(f)
        if not durata:  # la durata a volte è nella frase dopo ("Il limite per il soggiorno ... senza visto di ingresso è di 90 giorni nell'arco di 6 mesi")
            ff = tutte_frasi(vv)
            k = ff.index(f)
            if k + 1 < len(ff) and re.search(r"senza visto", ff[k + 1], re.I) and not DUBBIO_VISTO.search(ff[k + 1]):
                durata = _durata(ff[k + 1])
        out.update({"esito": "non_necessario", "citazione": _citazione_neg(f), "durata": durata})
        if fino:
            out["fino_al"] = f"{fino.group(3)}-{MESI_IT.index(fino.group(2)) + 1:02d}-{int(fino.group(1)):02d}"
        obblighi = []
        for tipo, nome, gen, fr in form:
            if tipo == "obbligo" and nome not in [o["nome"] for o in obblighi]:
                rx = next(rx for rx, n, t in NOMI_FORMALITA if n == nome)
                obblighi.append({"nome": nome, "tipo": gen, "citazione": _cit_formalita(fr, rx)})
        out["formalita"] = obblighi
        out["consigli"] = any(x[0] == "consiglio" for x in form)
        out["registrazione_locale"] = any(x[0] == "registrazione_locale" for x in form)
        out["tasse"] = any(x[0] == "tassa_uscita" for x in form)
        out["altri_casi"] = any(x[0] == "altro" for x in form) or bool(re.search(r"per (?:periodi|soggiorni|permanenze) (?:superior|eccedent)|oltre i \d+", tutto, re.I))
        out["obblighi_pp"] = obblighi_primo_piano(prim, [o["nome"] for o in obblighi])
        return out
    m = NEC_VISTO.match(f)
    if m and not CONDIZ_NEC.search(f):
        if "non_necessario" in pp:
            return {"esito": None, "motivo": "Il riquadro “In primo piano” della scheda dice che il visto non è necessario: leggi la scheda."}
        fine = re.search(r"[,.;:(]|$", f[m.end():])
        out.update({"esito": "necessario", "citazione": frammento(f, 0, m.end() + fine.start()) or frammento(f, 0, m.end())})
        out["eccezioni"] = bool(re.search(r"non necessit|esent|non (?:[èe] )?necessari|non (?:è |e['’] )?richiest|eccezion|\btranne\b|\bsalvo\b|non hanno bisogno", tutto, re.I))
        arrivo = online = False
        for x in tutte_frasi(vv):
            neg = re.search(r"\bnon\b|nessun|sconsiglia|sospes", x, re.I)
            if not neg and re.search(r"vist|visa", x, re.I):
                arrivo = arrivo or bool(re.search(r"all['’]\s?arrivo|in aeroporto|negli aeroporti|alla frontiera|in frontiera|on arrival", x, re.I))
                online = online or bool(re.search(r"\bonline\b|on line|on-line|e-?visa|evisa|portale|piattaforma|via internet|telematic|modalità elettronica", x, re.I))
        out["arrivo"] = arrivo
        out["online"] = online
        out["obblighi_pp"] = obblighi_primo_piano(prim)
        return out
    return {"esito": None, "motivo": "La scheda descrive il visto con condizioni, casi diversi o altre formalità che non si possono riassumere in una riga."}


# ------------------------------------------------------------------ fatti scritti a mano (dati/documenti_it_manuali.json, legati all'impronta del campo)
# Ogni Paese: "campi" = {campo: prime 16 cifre dello SHA-256 del campo letto il giorno della revisione}, poi i fatti (documento, validita,
# visto, note_extra) con "sintesi" (parole nostre), "citazioni" (parola per parola dal campo, al massimo MAX_PAROLE parole) e "campo".
FILE_MANUALI = DATI / "documenti_it_manuali.json"
_MAN = json.loads(FILE_MANUALI.read_text(encoding="utf-8")) if FILE_MANUALI.exists() else {}
MANUALI = _MAN.get("paesi", {})
MANUALI_RIVISTI_IL = _MAN.get("rivisto_il")  # data di scrittura dei fatti che non ne hanno una propria ("scritto_il")


def applica_manuali(iso, rec, imp):
    """Sostituisce i fatti automatici con quelli scritti a mano, solo se il campo su cui sono scritti non è cambiato."""
    usati, scaduti = [], []
    voce = MANUALI.get(iso)
    if not voce:
        return usati, scaduti
    for fatto in ("documento", "validita", "visto", "note_extra"):
        if fatto not in voce:
            continue
        val = voce[fatto]
        campi = {x["campo"] for x in (val if isinstance(val, list) else [val])}
        if all(imp.get(c, "").startswith(voce["campi"][c]) for c in campi):
            data = lambda x: x.get("scritto_il") or voce.get("scritto_il") or MANUALI_RIVISTI_IL
            rec[fatto] = ([dict(x, manuale=True, scritto_il=data(x)) for x in val] if isinstance(val, list)
                          else dict(val, manuale=True, scritto_il=data(val)))
            usati.append(fatto)
        else:
            scaduti.append(fatto)
    return usati, scaduti


# ------------------------------------------------------------------ lettura di un Paese
def data_scheda(s):
    """'2026-07-20T22:00:00Z' -> data in Italia ('2026-07-21')."""
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(ROMA).date().isoformat()
    except Exception:  # noqa: BLE001
        return None


def cronologia(j):
    rr = righe((((j.get("infoCronologiaAggiornamenti") or {}).get("nodi") or {}).get("Cronologia-aggiornamenti") or {}).get("contenuto", ""))
    out = []
    for r in rr:
        m = re.match(r"^(\d{2})/(\d{2})/(\d{4})\s*-\s*(.*)$", r)
        if m and len(parole(m.group(4))) <= 12:
            out.append({"data": f"{m.group(3)}-{m.group(2)}-{m.group(1)}", "nota": m.group(4).strip()})
    return out[:6]


ELISIONE = "(…)"
_URL_TRA_PARENTESI = re.compile(r"\s*\((?:https?://|www\.)[^)]*\)")
_URL_IN_CODA = re.compile(r"[\s:]*(?:https?://|www\.)\S+\s*$")


def pulisci_citazione(q):
    """Citazione senza gli indirizzi web tra parentesi (sostituiti da "(…)") o in coda: resta parola per parola, pezzo per pezzo."""
    if not q:
        return q
    q = _URL_TRA_PARENTESI.sub(" " + ELISIONE, q)
    q = _URL_IN_CODA.sub("", q).rstrip(" :")
    return q


def in_campo(q, testo_campo):
    """La citazione (eventualmente con "(…)") è nel campo, pezzo per pezzo e nell'ordine."""
    pos = 0
    for pezzo in [x.strip() for x in q.split(ELISIONE)]:
        if not pezzo:
            continue
        k = testo_campo.find(pezzo, pos)
        if k < 0:
            return False
        pos = k + len(pezzo)
    return True


def _pulisci_fatti(rec):
    for k in ("documento", "validita", "visto"):
        f = rec.get(k) or {}
        for c in ("citazione", "condizione", "durata"):
            if f.get(c):
                f[c] = pulisci_citazione(f[c])
        for x in f.get("formalita", []):
            x["citazione"] = pulisci_citazione(x["citazione"])


def leggi_paese(voce, j):
    iso = voce["Codice-3"]
    pp, vv, prim = campo(j, "passaporto"), campo(j, "visto"), campo(j, "primo_piano")
    imp = {"passaporto": impronta(pp), "visto": impronta(vv), "primo_piano": impronta(prim)}
    rec = {"iso3": iso, "iso2": voce.get("Codice-2"), "nome_fonte": voce["Nome"], "url": PAGINA + iso, "api": f"{BASE}{iso}.json",
           "aggiornata": data_scheda(j.get("updateDate", "")), "cronologia": cronologia(j), "impronte": imp}
    rim = rimando(pp) or rimando(vv)
    if rim:
        rec.update({"rimando": rim, "documento": {"esito": None, "motivo": "La scheda rimanda a un'altra scheda."},
                    "validita": {"esito": None, "motivo": "La scheda rimanda a un'altra scheda."},
                    "visto": {"esito": None, "motivo": "La scheda rimanda a un'altra scheda."}})
        return rec, [], []
    rec["documento"] = documento(pp, vv, prim)
    rec["validita"] = validita(pp)
    rec["visto"] = visto(vv, prim)
    _pulisci_fatti(rec)
    usati, scaduti = applica_manuali(iso, rec, imp)
    if rec["visto"].get("obblighi_pp") and rec.get("note_extra"):  # obbligo già spiegato in una nota scritta a mano (Georgia: assicurazione)
        gia = [c for x in rec["note_extra"] for c in x["citazioni"]]
        pulita = lambda q: q.replace(ELISIONE, "").strip()
        rec["visto"]["obblighi_pp"] = [q for q in rec["visto"]["obblighi_pp"] if not any(pulita(q)[:30] in c or c[:30] in q for c in gia)]
    return rec, usati, scaduti


def campi_da_cache(iso):
    """Righe dei tre campi dalla cache (per verifica.py)."""
    j = json.loads((CACHE / f"{iso}.json").read_text(encoding="utf-8"))
    return {k: campo(j, k) for k in CAMPI}, j


def main():
    oggi = date.today().isoformat()
    elenco, _ = scarica(ELENCO, "_lista.json")
    paesi, errori, scaricati, scaduti_tutti = [], [], 0, []
    for voce in elenco:
        iso = voce["Codice-3"]
        try:
            j, nuovo = scarica(f"{BASE}{iso}.json", f"{iso}.json")
            scaricati += nuovo
            rec, usati, scaduti = leggi_paese(voce, j)
            paesi.append(rec)
            scaduti_tutti += [f"{iso}:{c}" for c in scaduti]
            if nuovo:
                time.sleep(0.6)
        except Exception as e:  # noqa: BLE001
            errori.append(f"{iso}: {e}")
    print(f"Schede lette: {len(paesi)} su {len(elenco)} (scaricate ora: {scaricati}, dalla cache: {len(paesi) - scaricati}); errori: {len(errori)}")
    for e in errori:
        print("  ERRORE", e)
    if len(paesi) < QUOTA_MINIMA * len(elenco):
        print("Troppe schede non lette: dati/documenti_it.json NON aggiornato.")
        sys.exit(1)
    for s in scaduti_tutti:
        print(f"  FATTO MANUALE SCADUTO (la scheda è cambiata, rileggerla e aggiornare MANUALI): {s}")
    file = DATI / "documenti_it.json"
    vecchio = json.loads(file.read_text(encoding="utf-8")) if file.exists() else None
    nuovo = {"fonte": "Viaggiare Sicuri – Ministero degli Affari Esteri e della Cooperazione Internazionale (Unità di Crisi)",
             "fonte_url": "https://www.viaggiaresicuri.it/", "elenco_url": ELENCO, "controllato_il": oggi, "schede_elenco": len(elenco),
             "max_parole_citazione": MAX_PAROLE,
             "licenza": "Nessuna licenza indicata su viaggiaresicuri.it: il sito riporta solo fatti con parole proprie, citazioni brevi, data e link alla scheda.",
             "paesi": sorted(paesi, key=lambda p: p["nome_fonte"].lower())}
    if vecchio:
        prima = {p["iso3"]: p for p in vecchio["paesi"]}
        cambi_file = DATI / "documenti_it_cambi.json"
        storico = json.loads(cambi_file.read_text(encoding="utf-8")) if cambi_file.exists() else {"cambi": []}
        n = 0
        for p in paesi:
            q = prima.get(p["iso3"])
            if not q:
                continue
            campi = [c for c in ("passaporto", "visto") if q["impronte"].get(c) != p["impronte"].get(c)]
            if campi:
                storico["cambi"].insert(0, {"rilevato_il": oggi, "iso3": p["iso3"], "nome": p["nome_fonte"], "campi": campi,
                                            "scheda_prima": q["aggiornata"], "scheda_dopo": p["aggiornata"]})
                n += 1
        if n:
            cambi_file.write_text(json.dumps(storico, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Schede con il campo Passaporto o Visto cambiato rispetto al file precedente: {n}")
    file.write_text(json.dumps(nuovo, ensure_ascii=False, indent=1), encoding="utf-8")
    for k in ("documento", "validita", "visto"):
        c = {}
        for p in paesi:
            c[p[k]["esito"]] = c.get(p[k]["esito"], 0) + 1
        print(f"{k}: " + ", ".join(f"{e}: {n}" for e, n in sorted(c.items(), key=lambda x: str(x[0]))))


def stampa_impronte(isos):
    """Impronte (prime 16 cifre) dei campi in cache, da copiare in "campi" di dati/documenti_it_manuali.json dopo aver riletto la scheda;
    controlla anche che le citazioni dei fatti manuali di quei Paesi siano ancora nel campo."""
    for iso in isos:
        campi, _ = campi_da_cache(iso)
        print(iso, {k: impronta(v)[:16] for k, v in campi.items() if k != "primo_piano"})
        for fatto, val in (MANUALI.get(iso) or {}).items():
            if fatto == "campi":
                continue
            for x in (val if isinstance(val, list) else [val]):
                t = testo(campi[x["campo"]])
                qq = list(x.get("citazioni", [])) + list(x.get("citazioni_note", [])) + [y["citazione"] for y in x.get("formalita", [])] + \
                    ([x["durata"]] if x.get("durata") else [])
                for q in qq:
                    if not in_campo(q, t):
                        print(f"  {fatto}: citazione non più nel campo: {q}")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--impronte":
        stampa_impronte(sys.argv[2:])
    else:
        main()
