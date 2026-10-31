"""Legge dal sito del Department of Home Affairs (Australia) l'attesa per la cerimonia di cittadinanza council per council
e i tempi ufficiali della cittadinanza, e scrive visaincome/dati/cerimonie.json (dal 31/10/2026).

Uso (dalla radice del repository):
    python3 visaincome/raccolta/cerimonie.py              # rilegge le fonti, aggiunge lo storico se i dati sono nuovi, scrive il JSON
    python3 visaincome/raccolta/cerimonie.py --domanda    # rifà anche l'autocompletamento di Google (gl=au) per i council

Fonti (tutte di Home Affairs, licenza Creative Commons Attribution 3.0 Australia, attribuzione "Australian Government Department
of Home Affairs", pagina "Copyright and disclaimer" riletta a ogni lancio):
1. Pagina "Ceremony wait times" (immi.homeaffairs.gov.au/citizenship/citizenship-processing-times/ceremony-wait-times): la tabella
   non è nell'HTML; la pagina la chiede a /_layouts/15/api/Data.aspx/GetListData con POST {"webUrl": "/", "listName":
   "citizenshipCeremony"} (parametri scritti nella pagina stessa, "endpointParm"). È una richiesta pubblica, senza chiave né
   captcha, la stessa del browser di chiunque apra la pagina. Fino al 21/10/2026 rispondeva "List data is currently unavailable";
   dal 31/10/2026 risponde 200 con 539 council. Lo script controlla: nomi e intestazioni delle colonne nella configurazione della
   pagina, frasi della pagina (date di riferimento, maschera "<5", indirizzo di residenza, invito circa 4 settimane prima),
   percentuali tra 0 e 100 con somma 97-103 (arrotondamenti), data "Modified" uguale per tutte le righe.
2. Pagina "Citizenship processing times": i numeri stanno in un campo nascosto della pagina (PageSchemaHiddenField, JSON con i
   blocchi HTML): frasi del 90%, tabella dei percentili 25/50/75/90, domande in lavorazione e ricevute nel mese.
3. Pagina "Copyright and disclaimer" di homeaffairs.gov.au (licenza CC BY 3.0 AU e attribuzione).

Storico: Home Affairs mostra solo l'ultimo aggiornamento. A ogni lancio, se la data di riferimento ("to 30 September 2026") è nuova,
le righe vanno in "storico" (chiave = data di riferimento); le date già salvate non si toccano. Lo stesso per i tempi nazionali.

Domanda (--domanda): autocompletamento di Google (client=firefox, hl=en, gl=au) per ogni council con almeno MIN_DOMANDA persone
in attesa: "<nome> citizenship ceremony" e "citizenship ceremony wait time <nome>"; per le capitali anche "<città> citizenship
ceremony dates". I suggerimenti grezzi restano in "domanda.query"; a ogni lancio ogni suggerimento con "citizenship" va al council
di cui contiene il nome di ricerca come parola intera (se più nomi ci stanno, il più lungo: "north sydney" va a North Sydney, non a
City of Sydney), esclusi i luoghi stranieri omonimi (ESCLUSI_DOMANDA). Nomi uguali in due Stati (Bayside, Campbelltown, Central Coast,
...): la domanda va al council con più persone in attesa. Quanti suggerimenti servono per avere una pagina lo decide genera.py.

Se un controllo fallisce, il JSON esistente NON viene toccato (esce con codice 1). Grezzi in raccolta/_grezzi/cerimonie/ (esclusi da git).
"""
import hashlib
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
GREZZI = Path(__file__).resolve().parent / "_grezzi" / "cerimonie"
USCITA = RADICE / "dati" / "cerimonie.json"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"}

FONTI = {
    "attese": {"titolo": "Ceremony wait times", "editore": "Department of Home Affairs",
               "url": "https://immi.homeaffairs.gov.au/citizenship/citizenship-processing-times/ceremony-wait-times"},
    "lista": {"titolo": "Ceremony wait times: list data (citizenshipCeremony)", "editore": "Department of Home Affairs",
              "url": "https://immi.homeaffairs.gov.au/_layouts/15/api/Data.aspx/GetListData",
              "post": {"webUrl": "/", "listName": "citizenshipCeremony"}},
    "tempi": {"titolo": "Citizenship processing times", "editore": "Department of Home Affairs",
              "url": "https://immi.homeaffairs.gov.au/citizenship/citizenship-processing-times/citizenship-processing-times"},
    "licenza": {"titolo": "Copyright and disclaimer", "editore": "Department of Home Affairs",
                "url": "https://www.homeaffairs.gov.au/access-and-accountability/using-our-website/copyright-and-disclaimer"},
}
LICENZA_URL = "https://creativecommons.org/licenses/by/3.0/au/"

# colonne della lista come scritte nella configurazione della pagina (name -> heading)
COLONNE = {"Title": "Council name", "TotalApprovedApplicants": "Total approved applicants",
           "LessThanThreeMonths": "Wait time less than 3 months", "WaitTime3To6Months": "Wait time 3 to 6 months",
           "Wait_x0020_time_x0020_more_x0020": "Wait time more than 6 months"}
STATI = ["NSW", "VIC", "QLD", "WA", "SA", "TAS", "ACT", "NT"]

# frasi della pagina delle attese su cui si basano le pagine (spazi e caratteri invisibili normalizzati)
FRASI_ATTESE = {
    "consigli": "Citizenship ceremonies are usually organised by local government councils.",
    "indirizzo": "Which council-hosted ceremony you will attend is determined by your current residential address.",
    "scelta": "You cannot choose where and when to attend your ceremony.",
    "invito": "You will be invited to attend your ceremony about four weeks before the event.",
    "lettera": "You will receive a letter of invitation from either your local council or the Department of Home Affairs.",
    "domanda_locale": "The wait time for a ceremony depends on the demand in your local government area.",
    "famiglia": "Having family members linked to your application may also affect your wait time.",
    "maschera": 'the Department of Home Affairs policy is to mask numbers between 1 and 4 as "<5"',
    "arrotondamento": "the sum of some percentages may not equal 100% due to rounding.",
}
RE_PERIODO = re.compile(r"wait times shown are calculated from date of application approval to (\d{1,2} \w+ \d{4})")
RE_INVITATI = re.compile(r"the information includes applicants invited to a citizenship ceremony as at (\d{1,2} \w+ \d{4})")

FRASI_TEMPI = {
    "conferimento": "90% of applications are processed within {conf} months",
    "cerimonia": "90% of approved applicants will have the opportunity to attend a ceremony within {cer} months of approval.",
    "discendenza": "If you have applied for Australian citizenship by descent, 90% of applications are processed within {disc} months.",
    "prova": "If you have applied for Evidence of Australian citizenship, 90% of applications are processed within {prova} days.",
    "guida": "These percentile figures are intended to provide a guide only.",
    "nessuna_info": "if processing of your application is within the advertised processing times there is no further information that the Department can provide at this stage.",
}
FRASI_LICENZA = ["All material presented on this website is provided under a Creative Commons Attribution 3.0 Australia licence",
                 "You should attribute material you get from this website as Australian Government Department of Home Affairs."]

MIN_DOMANDA = 20   # persone in attesa minime per cercare la domanda di un council
CAPITALI = {"sydney": "City of Sydney", "melbourne": "City of Melbourne", "brisbane": "Brisbane City Council", "perth": "City of Perth",
            "adelaide": "City of Adelaide", "hobart": "Hobart City Council", "darwin": "City of Darwin",
            "canberra": "Office For Multicultural Affairs, ACT Government"}
BREVI = {"George Town Council": "George Town", "The Hills Shire Council": "The Hills Shire", "Office For Multicultural Affairs, ACT Government": "ACT"}
NOMI_RICERCA = {  # nome ufficiale -> nome usato nelle ricerche (dove la regola automatica non basta)
    "Office For Multicultural Affairs, ACT Government": "canberra",
    "Shire of Derby / West Kimberley": "derby",
    "Canterbury-Bankstown Council": "canterbury bankstown",
    "The Hills Shire Council": "the hills",
}


def norm(t):
    t = t.replace("​", "").replace("\xa0", " ").replace("‑", "-").replace("’", "'")
    return re.sub(r"\s+", " ", t).strip()


def testo_html(b):
    t = b.decode("utf-8", "replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S | re.I)
    return norm(html.unescape(re.sub(r"<[^>]+>", " ", t)))


def scarica(u, post=None):
    h = dict(UA)
    dati = None
    if post is not None:
        h["Content-Type"] = "application/json; charset=utf-8"
        dati = json.dumps(post).encode()
    for _ in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, data=dati, headers=h), timeout=120)
            return r.status, r.read()
        except Exception as e:  # noqa: BLE001
            st = getattr(e, "code", None)
            if st:
                return st, b""
            time.sleep(3)
    return None, b""


def breve(titolo):
    """Nome breve del council (senza 'City of', 'Shire Council'...), come lo cerca la gente."""
    s = re.sub(r"\s+-\s+(SA|TAS|NSW|VIC|QLD|WA|NT)$", "", titolo)
    s = re.sub(r"^(The )?(Regional Council|District Council|Rural City|City|Town|Shire|Municipality|Borough|Municipal Council) [Oo]f ", "", s)
    if titolo in BREVI:
        return BREVI[titolo]
    s = re.sub(r"\s+(Regional|Rural City|City|Shire|Municipal|Town|Aboriginal Shire|Rural|District|Community Government)?\s*Council$", "", s)
    s = re.sub(r"^The ", "", s)
    return s.replace(" - ", "-").strip()


def nome_ricerca(titolo):
    if titolo in NOMI_RICERCA:
        return NOMI_RICERCA[titolo]
    s = breve(titolo)
    s = re.sub(r"^Greater ", "", s)
    return re.sub(r"\s+", " ", s.lower().replace("-", " ").replace("'", "")).strip()


def pct(v, chi):
    v = norm(html.unescape(v))
    if not re.fullmatch(r"\d{1,3}%", v):
        raise ValueError(f"{chi}: percentuale non valida {v!r}")
    x = int(v[:-1])
    if x > 100:
        raise ValueError(f"{chi}: percentuale oltre 100 {v!r}")
    return x


def leggi_lista(b, errori):
    j = json.loads(b.decode("utf-8"))["d"]
    if not j.get("success") or not isinstance(j.get("data"), list):
        errori.append(f"lista: risposta senza dati ({j.get('message')!r})")
        return [], None
    righe, date_ = [], set()
    for r in j["data"]:
        nome = norm(html.unescape(r["Title"]))
        stato = norm(r["State"])
        tot = norm(html.unescape(r["TotalApprovedApplicants"]))
        if stato not in STATI:
            errori.append(f"lista: Stato sconosciuto {stato!r} ({nome})")
        if tot != "<5" and not re.fullmatch(r"\d+", tot.replace(",", "")):
            errori.append(f"lista: numero non valido {tot!r} ({nome})")
            continue
        try:
            p = [pct(r["LessThanThreeMonths"], nome), pct(r["WaitTime3To6Months"], nome), pct(r["Wait_x0020_time_x0020_more_x0020"], nome)]
        except ValueError as e:
            errori.append(f"lista: {e}")
            continue
        if norm(r.get("WaitTime6To12Months", "")):
            errori.append(f"lista: colonna 6-12 mesi non vuota per {nome}: rileggere la pagina")
        n = None if tot == "<5" else int(tot.replace(",", ""))
        if n and not 97 <= sum(p) <= 103:
            errori.append(f"lista: percentuali di {nome} sommano {sum(p)}")
        date_.add(r["Modified"])
        righe.append([nome, stato, n, *p])
    if len(date_) != 1:
        errori.append(f"lista: date di modifica diverse {sorted(date_)}")
    mod = datetime.strptime(date_.pop(), "%d/%m/%Y").date().isoformat() if len(date_) == 1 else None
    if len({r[0] for r in righe}) != len(righe):
        errori.append("lista: nomi di council ripetuti")
    return sorted(righe, key=lambda r: (STATI.index(r[1]) if r[1] in STATI else 9, r[0])), mod


def data_iso(t):
    return datetime.strptime(t, "%d %B %Y").date().isoformat()


def leggi_attese(b, errori):
    grezzo = b.decode("utf-8", "replace")
    tx = testo_html(b)
    out = {}
    m = re.search(r'"endpointParm":\s*"\{\\"webUrl\\":\s*\\"/\\",\s*\\"listName\\":\\"(\w+)\\"\}"', grezzo)
    if not m or m.group(1) != FONTI["lista"]["post"]["listName"]:
        errori.append("attese: la pagina non chiede più la lista citizenshipCeremony")
    for nome, testa in COLONNE.items():
        if not re.search(r'"name":\s*"' + re.escape(nome) + r'",\s*"label":\s*"[^"]*",\s*"heading":\s*"' + re.escape(testa) + '"', grezzo):
            errori.append(f"attese: colonna {nome} senza l'intestazione {testa!r}")
    for k, f in FRASI_ATTESE.items():
        if norm(f) not in tx:
            errori.append(f"attese: frase mancante ({k}): {f!r}")
    p, i = RE_PERIODO.search(tx), RE_INVITATI.search(tx)
    if not p or not i:
        errori.append("attese: date di riferimento non trovate")
    else:
        out["al"], out["invitati_al"] = data_iso(p.group(1)), data_iso(i.group(1))
    m = re.search(r'id="pageModified"[^>]*>(\d{1,2}/\d{1,2}/\d{4})', grezzo)
    out["aggiornata"] = datetime.strptime(m.group(1), "%d/%m/%Y").date().isoformat() if m else None
    if not m:
        errori.append("attese: data 'Last updated' non trovata")
    out["frasi"] = FRASI_ATTESE
    return out


def celle(tr):
    return [norm(html.unescape(re.sub(r"<[^>]+>", " ", c))) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]


def leggi_tempi(b, errori):
    grezzo = b.decode("utf-8", "replace")
    m = re.search(r'id="ctl00_PlaceHolderMain_PageSchemaHiddenField_Input" value="([^"]*)"', grezzo)
    if not m:
        errori.append("tempi: campo nascosto con i contenuti non trovato")
        return {}
    blocchi = {norm(x["text"]): x["block"] for x in json.loads(html.unescape(m.group(1)))["content"]}
    out = {}
    pt = blocchi.get("Processing times", "")
    tx = norm(html.unescape(re.sub(r"<[^>]+>", " ", pt)))
    rx = {"conf": r"90% of applications are processed within (\d+) months", "cer": r"attend a ceremony within (\d+) months of approval",
          "disc": r"citizenship by descent, 90% of applications are processed within (\d+) months",
          "prova": r"Evidence of Australian citizenship, 90% of applications are processed within (\d+) days"}
    v = {}
    for k, r in rx.items():
        mm = re.search(r, tx)
        if not mm:
            errori.append(f"tempi: frase del 90% non trovata ({k})")
        else:
            v[k] = int(mm.group(1))
    if len(v) == 4:
        for k, f in FRASI_TEMPI.items():
            if norm(f.format(**v)) not in tx:
                errori.append(f"tempi: frase mancante ({k}): {f.format(**v)!r}")
    out["novanta"] = {"conferimento_mesi": v.get("conf"), "cerimonia_mesi": v.get("cer"), "discendenza_mesi": v.get("disc"), "prova_giorni": v.get("prova")}
    righe = [celle(tr) for tr in re.findall(r"<tr.*?</tr>", pt, re.S)]
    if not righe or righe[0] != ["Application type", "Period counted", "25% of applications are processed in:", "50% of applications are processed in:",
                                 "75% of applications are processed in:", "90% of applications are processed in:"]:
        errori.append(f"tempi: intestazione della tabella dei percentili cambiata: {righe[:1]}")
    attese = [("conferimento", "decisione", "Australian citizenship by conferral (general eligibility and other situations)", "From date of application to decision"),
              ("conferimento", "approvazione_cerimonia", None, "From date of approval to ceremony"),
              ("conferimento", "domanda_cerimonia", None, "From date of application to ceremony"),
              ("discendenza", "decisione", "Australian citizenship by descent", "From date of application to decision"),
              ("prova", "decisione", "Evidence of Australian citizenship", "From date of application to decision")]
    perc = {}
    for (tipo, periodo, nome, etichetta), r in zip(attese, righe[1:]):
        r = [re.sub(r" \d$", "", c) for c in r]   # note a piè di pagina (1, 2...)
        if nome:
            if r[0] != nome:
                errori.append(f"tempi: riga {r[0]!r} al posto di {nome!r}")
            r = r[1:]
        if r[0] != etichetta or len(r) != 5 or not all(re.fullmatch(r"\d+ (days|months|day|month)", c) for c in r[1:]):
            errori.append(f"tempi: riga dei percentili non valida {r}")
            continue
        perc.setdefault(tipo, {})[periodo] = r[1:]
    if len(righe) != 6:
        errori.append(f"tempi: {len(righe) - 1} righe di percentili invece di 5")
    out["percentili"] = perc
    if v and perc.get("conferimento", {}).get("decisione", [""] * 4)[3] != f"{v.get('conf')} months":
        errori.append("tempi: il 90° percentile della tabella non coincide con la frase")
    for chiave, titolo, rx_data in (("in_lavorazione", "Number of applications we have", r"how many applications we had on hand on (\d{1,2} \w+ \d{4})"),
                                    ("ricevute", "Number of applications received", r"received between (\d{1,2} \w+(?: \d{4})?) and (\d{1,2} \w+ \d{4})")):
        b2 = blocchi.get(titolo, "")
        t2 = norm(html.unescape(re.sub(r"<[^>]+>", " ", b2)))
        md = re.search(rx_data, t2)
        rr = [celle(tr) for tr in re.findall(r"<tr.*?</tr>", b2, re.S)][1:]
        nums = {}
        for r in rr:
            nome = re.sub(r" \d$", "", r[0])
            k = {"Australian citizenship by conferral (general eligibility and other situations)": "conferimento",
                 "Australian citizenship by descent": "discendenza", "Evidence of Australian citizenship": "prova"}.get(nome)
            if not k or not re.fullmatch(r"[\d,]+", r[1]):
                errori.append(f"tempi: riga non valida in {titolo!r}: {r}")
                continue
            nums[k] = int(r[1].replace(",", ""))
        if not md or len(nums) != 3:
            errori.append(f"tempi: tabella {titolo!r} non letta")
            continue
        if chiave == "in_lavorazione":
            out[chiave] = {"al": data_iso(md.group(1)), **nums}
        else:
            fine = data_iso(md.group(2))
            inizio = md.group(1) if re.search(r"\d{4}$", md.group(1)) else md.group(1) + " " + fine[:4]
            out[chiave] = {"dal": data_iso(inizio), "al": fine, **nums}
    out["frasi"] = {k: f.format(**v) for k, f in FRASI_TEMPI.items()} if len(v) == 4 else {}
    m = re.search(r'id="pageModified"[^>]*>(\d{1,2}/\d{1,2}/\d{4})', grezzo)
    out["aggiornata"] = datetime.strptime(m.group(1), "%d/%m/%Y").date().isoformat() if m else None
    if not m:
        errori.append("tempi: data 'Last updated' non trovata")
    return out


# ---------------------------------------------------------------- domanda (autocompletamento Google, gl=au)
def autocompleta(q):
    u = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode({"client": "firefox", "gl": "au", "hl": "en", "q": q})
    for _ in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20)
            return json.loads(r.read().decode("utf-8", "replace"))[1]
        except Exception:  # noqa: BLE001
            time.sleep(2)
    return None


def pulisci(t):
    return re.sub(r"\s+", " ", t.lower().replace("-", " ").replace("'", "")).strip()


ESCLUSI_DOMANDA = ["palmerston north", "north somerset", "cambridge private", "perth and kinross", "british citizenship",  # luoghi stranieri omonimi
                   "upon thames", "upon tyne",
                   "south yarra"]   # quartiere di Melbourne (City of Stonnington / City of Melbourne), non della City of Yarra
ALIAS_RICERCA = {"port adelaide": "City of Port Adelaide Enfield", "redlands": "Redland City Council"}   # altri nomi usati nelle ricerche


def per_nome_ricerca(righe, minimo=0):
    """nome di ricerca -> council; se due council hanno lo stesso nome vale quello con più persone in attesa."""
    per_nome = {}
    for r in sorted(righe, key=lambda r: (-(r[2] or 0), r[0])):
        if (r[2] or 0) >= minimo:
            per_nome.setdefault(nome_ricerca(r[0]), r[0])
    return per_nome


def attribuisci(query, righe):
    """Da ogni suggerimento al council che nomina: nome intero (non dentro un'altra parola) e, se più nomi ci stanno,
    il più lungo ('north sydney' va a North Sydney, non a City of Sydney; 'swan hill' a Swan Hill, non a City of Swan)."""
    nomi = per_nome_ricerca(righe)
    nomi.update({a: t for a, t in ALIAS_RICERCA.items() if a not in nomi})
    rx = {n: re.compile(r"(?<![a-z])" + re.escape(n) + r"(?![a-z])") for n in nomi}
    council = {t: [] for t in per_nome_ricerca(righe, MIN_DOMANDA).values()}
    for q, sugg in query.items():
        for x in sugg or []:
            px = pulisci(x)
            if "citizenship" not in px or any(e in px for e in ESCLUSI_DOMANDA):
                continue
            trovati = [n for n in nomi if rx[n].search(px)]
            if not trovati:
                continue
            t = nomi[max(trovati, key=len)]
            if t in council and x not in council[t]:
                council[t].append(x)
    citta = {c: {"council": t, "suggerimenti": [x for x in query.get(f"{c} citizenship ceremony dates") or []
                                                if re.search(r"(?<![a-z])" + c + r"(?![a-z])", pulisci(x))]} for c, t in CAPITALI.items()}
    return council, citta


def nuova_domanda(righe):
    generali = ["citizenship ceremony wait time", "citizenship ceremony wait times by council", "australian citizenship processing time",
                "australian citizenship ceremony", "citizenship ceremony dates", "how long after citizenship approval is the ceremony"]
    query = {q: autocompleta(q) for q in generali}
    for nome in per_nome_ricerca(righe, MIN_DOMANDA):
        for q in (f"{nome} citizenship ceremony", f"citizenship ceremony wait time {nome}"):
            query[q] = autocompleta(q)
            time.sleep(0.3)
    for c in CAPITALI:
        q = f"{c} citizenship ceremony dates"
        query[q] = autocompleta(q)
        time.sleep(0.3)
    if sum(1 for v in query.values() if v is None) > len(query) / 4:
        sys.exit("ERRORE: autocompletamento non raggiungibile per più di un quarto delle ricerche")
    return {"data": date.today().isoformat(), "metodo": "https://suggestqueries.google.com/complete/search?client=firefox&gl=au&hl=en&q=…",
            "minimo_attesa": MIN_DOMANDA, "query": query}


def main():
    oggi = date.today().isoformat()
    errori, fonti, grezzi = [], {}, {}
    for k, F in FONTI.items():
        st, b = scarica(F["url"], F.get("post"))
        if st != 200 or not b:
            errori.append(f"{k}: HTTP {st} ({F['url']})")
            continue
        grezzi[k] = b
        fonti[k] = {**F, "http": st, "letto_il": oggi, "byte": len(b), "sha256": hashlib.sha256(b).hexdigest()}
    if errori:
        sys.exit("ERRORE, JSON non aggiornato:\n" + "\n".join(errori))
    righe, modificata = leggi_lista(grezzi["lista"], errori)
    attese = leggi_attese(grezzi["attese"], errori)
    tempi = leggi_tempi(grezzi["tempi"], errori)
    tl = testo_html(grezzi["licenza"])
    for f in FRASI_LICENZA:
        if norm(f) not in tl:
            errori.append(f"licenza: frase mancante {f!r}")
    if len(righe) < 450:
        errori.append(f"lista: solo {len(righe)} council (erano 539 il 31/10/2026)")
    if sum(r[2] or 0 for r in righe) < 20000:
        errori.append("lista: totale delle persone in attesa troppo basso")
    if errori:
        sys.exit("ERRORE, JSON non aggiornato:\n" + "\n".join(errori))
    GREZZI.mkdir(parents=True, exist_ok=True)
    (GREZZI / f"lista-{attese['al']}.json").write_bytes(grezzi["lista"])
    (GREZZI / f"tempi-{tempi['aggiornata']}.html").write_bytes(grezzi["tempi"])
    vecchio = json.loads(USCITA.read_text(encoding="utf-8")) if USCITA.exists() else {}
    storico = vecchio.get("storico", {})
    if attese["al"] not in storico:
        storico[attese["al"]] = {"pubblicato": modificata, "righe": {r[0]: r[2:] for r in righe}}
    storico_tempi = vecchio.get("storico_tempi", {})
    if tempi["aggiornata"] not in storico_tempi:
        storico_tempi[tempi["aggiornata"]] = {k: tempi[k] for k in ("novanta", "percentili", "in_lavorazione", "ricevute")}
    domanda = nuova_domanda(righe) if "--domanda" in sys.argv else vecchio.get("domanda")
    if not domanda:
        sys.exit("ERRORE: nessuna domanda salvata: lanciare con --domanda")
    domanda = {k: domanda[k] for k in ("data", "metodo", "minimo_attesa", "query")}
    domanda["council"], domanda["citta"] = attribuisci(domanda["query"], righe)
    dati = {
        "_nota": "Generato da raccolta/cerimonie.py: non modificare a mano. Righe: [council, Stato, persone approvate in attesa (null = '<5'), "
                 "% in attesa da meno di 3 mesi, % da 3 a 6 mesi, % da oltre 6 mesi].",
        "letto_il": oggi,
        "fonti": fonti,
        "licenza": {"nome": "Creative Commons Attribution 3.0 Australia", "url": LICENZA_URL, "attribuzione": "Australian Government Department of Home Affairs"},
        "lista": {"al": attese["al"], "invitati_al": attese["invitati_al"], "modificata": modificata, "pagina_aggiornata": attese["aggiornata"],
                  "frasi": attese["frasi"], "colonne": COLONNE, "righe": righe,
                  "nomi": {r[0]: {"breve": breve(r[0]), "ricerca": nome_ricerca(r[0])} for r in righe}},
        "tempi": tempi,
        "storico": dict(sorted(storico.items())),
        "storico_tempi": dict(sorted(storico_tempi.items())),
        "domanda": domanda,
    }
    cont = {k: dati[k] for k in ("fonti", "lista", "tempi", "storico", "storico_tempi")}
    dati["impronta"] = hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20]
    USCITA.write_text(json.dumps(dati, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    n_dom = sum(1 for v in domanda["council"].values() if v)
    print(f"Scritto {USCITA}: {len(righe)} council, {sum(r[2] or 0 for r in righe):,} persone in attesa al {attese['al']} "
          f"(pubblicata il {modificata}); tempi aggiornati il {tempi['aggiornata']}; storico: {len(storico)} date; "
          f"domanda del {domanda['data']}: {n_dom} council con suggerimenti.")


if __name__ == "__main__":
    main()
