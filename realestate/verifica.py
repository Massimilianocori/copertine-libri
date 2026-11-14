"""Controlli di Real Estate Exam Pass Rates. Uso (dalla radice del repository):
    python3 realestate/verifica.py            # fonti, dati e pagine
    python3 realestate/verifica.py --browser  # in più: Playwright a 375 e 1280 px, chiaro e scuro (richieste esterne bloccate)

I controlli NON usano dati/tassi.json come verità: i numeri delle pagine sono confrontati con una seconda lettura dei file grezzi,
scritta qui in un altro modo rispetto a raccolta/fonti.py:
- Texas: il JSON ufficiale riletto qui, con la percentuale ricalcolata da esami e promossi;
- Alabama: le schede HTML rilette cella per cella (fonti.py le legge come testo);
- Hawaii: il PDF riletto con un'altra libreria (pypdf: righe «codice, esami, promossi, bocciati»; fonti.py usa pdftotext -layout), con la
  percentuale ricalcolata e troncata a un decimale come fa il bollettino;
- Nebraska (scansione, trascritta a mano): righe che tornano con l'aritmetica, confronto con la lettura automatica (tesseract) della scansione dove si legge
  pulito, e alcune cifre chiave ritrascritte qui sotto;
- ore, età, scadenze e tariffe della licenza: trascritte a mano qui sotto (ATTESO_LIC) dalle pagine delle commissioni.
Poi: frasi alla lettera, FAQ da ricerche misurate, link, titoli, modulo senza dati personali, regola dei campioni piccoli (numero di esami
accanto a ogni percentuale, etichetta sotto i 30 esami), riquadro del partner assente finché è spento, nessuna chiave, nessun nome di modello.
"""
import hashlib
import json
import re
import subprocess
import sys
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
SITO = RADICE / "sito"
DATI = RADICE / "dati"
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402

URL_SITO = "https://real-estate-exam-pass-rates.netlify.app"
ERR, AVV = [], []
SOGLIA = 30
MODELLI_VIETATI = re.compile(r"\b(" + "|".join(a + b for a, b in [("cla", "ude"), ("chat", "gpt"), ("gpt", r"-?\d"), ("open", "ai"), ("anth", "ropic"), ("gem", "ini"), ("lla", "ma"), ("copi", "lot")]) + r")\b", re.I)
FONTI_PARTNER = {"aceable"}
CHIAVE = "sd_" + "live"   # prefisso delle chiavi seodata: non deve comparire in nessun file
GIUDIZI = re.compile(r"\bbest\b|\bworst\b|top[- ]rated|\bcheapest\b|#1\b|we recommend|highly rated", re.I)
STATI = {"TX": ("Texas", "texas"), "AL": ("Alabama", "alabama"), "NE": ("Nebraska", "nebraska"), "HI": ("Hawaii", "hawaii")}
MISURE = {"TX": ["first"], "AL": ["first", "all"], "NE": ["national_first", "state_first", "national_all", "state_all"], "HI": ["national", "state"]}
DOMINI_UFFICIALI = r"https://(www\.trec\.texas\.gov|arec\.alabama\.gov|nrec\.nebraska\.gov|cca\.hawaii\.gov)/"

# Trascritto a mano dalle pagine delle commissioni il 14/11/2026 (non da tassi.json).
ATTESO_LIC = {
    # TREC, «Become a Real Estate Sales Agent»: 180 classroom hours (sei corsi da 30), 18 anni; Fee Schedule Effective September 1, 2026:
    # Sales Agent Original Application 150.00 + 6.00 + 40.00 + 10.00 = 206.00; Sales Examination Fee 58.00; Fingerprint Fee 40.00
    "TX": {"ore": 180, "eta": 18, "domanda": {"tassa": 15000, "texas_online": 600, "centro_ricerca": 4000, "fondo": 1000, "totale": 20600}, "esame": 5800, "impronte": 4000},
    # AREC, «Become a Licensed Real Estate Professional»: 60 clock hour prelicense course, 6 months to pass, 30 hour post license, 19 anni; domanda entro 90 giorni
    "AL": {"ore": 60, "mesi_esame": 6, "ore_post": 30, "eta": 19, "giorni_domanda": 90},
    # NREC: 96 HOURS TOTAL (6 + 90), 19 anni; Fee Schedule: Application 175.00, Examination 150.00 per exam, Retake 150.00, Salesperson Original License 90.00,
    # Salesperson Renewal 2 Year 180.00; soglie 60/80 e 38/50
    "NE": {"ore": 96, "ore_standard": 6, "ore_corsi": 90, "eta": 19, "domanda": 17500, "esame": 15000, "ripetizione": 15000, "licenza": 9000, "rinnovo": 18000,
           "soglia_nazionale": [60, 80], "soglia_statale": [38, 50]},
    # Hawaii REC: 60 hour prelicensing course, 18 anni alla data dell'esame; Salesperson: Odd numbered year $382, Even numbered year $282, Renewal $268; attesa 24 ore
    "HI": {"ore": 60, "eta": 18, "licenza_dispari": 38200, "licenza_pari": 28200, "rinnovo": 26800, "ore_attesa": 24, "ore_formazione_continua": 20},
}
# Cifre che ogni pagina della licenza deve mostrare (testo visibile), scritte a mano come devono apparire
ATTESO_TESTO_LIC = {
    "TX": ["180 hours", "$206", "$150 fee + $6 Texas Online fee + $40 Texas A&M Research Center + $10 Real Estate Recovery fee", "$58", "$40", "$304", "September 1, 2026", "at least 18 years old", "Pearson"],
    "AL": ["60 hours", "6 months", "90 days", "30 hour post license course", "at least 19", "Pearson"],
    "NE": ["96 hours", "$175", "$150", "$90", "$415", "$180", "60 of 80", "38 of 50", "At least 19 years old", "Pearson"],
    "HI": ["60 hours", "$382", "$282", "$268", "At least 18 years old", "PSI", "24 hours"],
}
# Totali e righe chiave trascritti a mano dalle fonti (letti negli originali, non in tassi.json)
ATTESO_TOTALI = {
    "TX": {"first": (29980, 16824, "56.12%")},          # riga «Overall Provider Statistics»: 29,980 esami, 16,824 promossi, 56.12%
    "HI": {"national": (1986, 721, "36.3%"), "state": (2300, 712, "30.9%")},   # righe Total, 10/1/2025 - 9/30/2026
}
ATTESO_RIGHE = {
    "TX": {"aceableagent": {"first": (8516, 5604, "65.81%")}, "champions school of real estate ltd": {"first": (15547, 8278, "53.24%")},
           "kaplan real estate education": {"first": (1280, 681, "53.20%")}, "the ce shop llc": {"first": (1077, 608, "56.45%")}, "360training.com inc.": {"first": (290, 138, "47.59%")}},
    "AL": {"360training.com, inc.": {"first": (33, 11, "33.3%"), "all": (101, 22, "21.8%")}, "academy of real estate": {"first": (42, 37, "88.1%"), "all": (50, 38, "76%")},
           "colibri real estate, llc": {"first": (272, 222, "81.6%"), "all": (388, 269, "69.3%")}},
    # Nebraska, 1° trimestre 2026 (rapporto collegato dall'indice ufficiale), riletto dalle immagini delle pagine 2, 4 e 5 nella revisione del 14/11/2026
    "NE": {"randall school of real estate": {"national_first": (32, 18, "56%"), "state_first": (32, 12, "38%"), "national_all": (72, 30, "42%"), "state_all": (93, 30, "32%")},
           "360training.com, inc dba van education center": {"national_first": (33, 21, "64%"), "state_first": (33, 4, "12%"), "national_all": (63, 31, "49%"), "state_all": (111, 27, "24%")},
           "reesults coaching": {"national_first": (15, 10, "67%"), "state_first": (15, 6, "40%"), "national_all": (32, 16, "50%"), "state_all": (45, 18, "40%")},
           "colibri real estate llc": {"national_first": (16, 12, "75%"), "state_first": (16, 5, "31%"), "national_all": (26, 18, "69%"), "state_all": (38, 12, "32%")}},
    "HI": {"abe lee seminars (online)": {"national": (504, 156, "30.9%"), "state": (576, 152, "26.3%")}, "the ce shop, inc. (online)": {"national": (293, 134, "45.7%"), "state": (407, 136, "33.4%")},
           "colibri real estate, llc (online)": {"national": (209, 85, "40.6%"), "state": (271, 75, "27.6%")}},
}
MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
PERIODI = {"TX": "December 1, 2023 to November 30, 2025", "NE": "January 1 to March 31, 2026", "HI": "October 1, 2025 to September 30, 2026"}


def err(m):
    ERR.append(m)


def ok(cond, m):
    if not cond:
        err(m)
    return cond


def norm(s):
    s = s.replace("­", "").replace("​", "").replace(" ", " ").replace("‑", "-")
    s = re.sub(r"(\w)-\n\s*(\w)", r"\1\2", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r" +([,.;:)])", r"\1", s)     # spazio lasciato da un link prima della punteggiatura
    return re.sub(r"\( +", "(", s)


def testo_grezzo(p):
    if p.suffix == ".pdf":
        t = subprocess.run(["pdftotext", str(p), "-"], capture_output=True, check=True).stdout.decode("utf-8", errors="replace")
        if len(t.strip()) > 200:
            return t
        # scansione senza strato di testo (rapporto del Nebraska): lettura automatica delle pagine
        sys.path.insert(0, str(RADICE / "raccolta"))
        import testo as T_ocr
        return T_ocr.pdf_ocr(p)
    s = p.read_text(encoding="utf-8", errors="replace")
    s = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", s)
    return unescape(re.sub(r"<[^>]+>", " ", s))


def controlla_fonti():
    F = json.loads((DATI / "fonti.json").read_text(encoding="utf-8"))["fonti"]
    testi = {}
    for fid, f in F.items():
        p = RADICE / f["file"]
        if not ok(p.exists(), f"fonte {fid}: manca {f['file']}"):
            continue
        dinamica = p.suffix == ".html" and fid != "al_tassi"   # pagine HTML senza numeri: fa fede l'impronta delle frasi citate
        ok(f.get("impronta") == ("frasi" if dinamica else "file"), f"fonte {fid}: tipo di impronta sbagliato in fonti.json")
        if not dinamica:
            ok(hashlib.sha256(p.read_bytes()).hexdigest() == f["sha256"], f"fonte {fid}: impronta SHA-256 del file diversa da fonti.json")
        ok(f["http"] == 200 and re.fullmatch(r"\d{4}-\d\d-\d\d", f["letto_il"]) and f["url"].startswith("https://"), f"fonte {fid}: url, data o HTTP non validi")
        testi[fid] = norm(testo_grezzo(p))
        for k, frase in f["frasi"].items():
            ok(norm(frase) in testi[fid], f"fonte {fid}: frase «{k}» non è alla lettera nel file grezzo")
        attesa = hashlib.sha256("\n".join(f"{k}\t{norm(f['frasi'][k])}" for k in sorted(f["frasi"])).encode("utf-8")).hexdigest()
        ok(f.get("sha256_frasi") == attesa, f"fonte {fid}: impronta delle frasi diversa da fonti.json")
    ufficiali = [f["url"] for fid, f in F.items() if fid not in FONTI_PARTNER]
    ok(all(re.match(DOMINI_UFFICIALI, u) for u in ufficiali), "una fonte non è sul sito di una commissione")
    ok(len(ufficiali) == 19, f"fonti ufficiali: {len(ufficiali)}")
    return F, testi


# ---------------------------------------------------------------- seconda lettura dei file grezzi
def mezzo_su(num, den, decimali):
    """num/den in percento, arrotondato a `decimali` cifre, .5 in su, con interi."""
    k = 10 ** decimali
    return (2 * 100 * k * num + den) // (2 * den), k


def fmt(v, k, decimali):
    return f"{v // k}.{v % k:0{decimali}d}%" if decimali else f"{v}%"


def rif_texas(F):
    d = json.loads((RADICE / F["tx_tassi"]["file"]).read_text(encoding="utf-8"))
    righe = {}
    for chiave, lista in d.items():
        if chiave in ("dates", "passrates0"):
            continue
        for x in lista:
            if "*" in x["SchlNm"]:
                continue
            n, p = x["SALEExmCnt"], x["SALEExmPssdCnt"]
            v, k = mezzo_su(p, n, 2) if n else (0, 100)
            nome = x["SchlNm"].strip("! ").lower()
            ok(nome not in righe, f"Texas: nome doppio {nome}")
            righe[nome] = {"first": (n, p, fmt(v, k, 2) if n else None)}
            ok(not n or x["SALEPC"] == fmt(v, k, 2), f"Texas/{nome}: la percentuale del file ({x['SALEPC']}) non è promossi ÷ esami")
    t = d["passrates0"][0]
    ok((d["dates"][0]["BgnDt"], d["dates"][0]["EndDt"]) == ("12/1/2023", "11/30/2025"), "Texas: il periodo del file non è più 12/1/2023 - 11/30/2025: aggiornare PERIODI e le cifre a mano")
    return righe, {"first": (t["SALEExmCnt"], t["SALEExmPssdCnt"], t["SALEPC"])}


def rif_alabama(F):
    s = (RADICE / F["al_tassi"]["file"]).read_text(encoding="utf-8", errors="replace")
    righe, formati = {}, {}
    schede = list(re.finditer(r'SchoolDetail/(\d+)">\s*(.*?)\s*</a>', s, re.S))
    for i, m in enumerate(schede):
        blocco = s[m.end():schede[i + 1].start() if i + 1 < len(schede) else len(s)]
        celle = [unescape(c).strip() for c in re.findall(r'text-center">([^<]*)</div>', blocco)]
        # 16 celle per scheda: «1st», «All», poi Total, Passed, % Passed (2 valori ciascuno) per Salesperson e poi per Broker
        if not ok(len(celle) == 16 and celle[0:2] == ["1st", "All"] and celle[8:10] == ["1st", "All"], f"Alabama: scheda {m.group(1)} con {len(celle)} celle"):
            continue
        nome = norm(unescape(m.group(2))).lower()
        n1, na, p1, pa = int(celle[2]), int(celle[3]), int(celle[4]), int(celle[5])
        chiave = (nome, m.group(1))
        righe[chiave] = {"first": (n1, p1, celle[6] if n1 else None), "all": (na, pa, celle[7] if na else None)}
        for (n, p, pc) in righe[chiave].values():
            if n:
                v, k = mezzo_su(p, n, 1)
                ok(abs(float(pc.rstrip("%")) * 10 - v) <= 0.01, f"Alabama/{nome}: {pc} non è {p} ÷ {n}")
        formati[chiave] = re.findall(r'badge[^>]*>\s*(\w+)\s*<', blocco)
    return righe, formati


def rif_hawaii(F):
    import pypdf
    testo = "\n".join(p.extract_text() for p in pypdf.PdfReader(str(RADICE / F["hi_tassi"]["file"])).pages)
    tabelle, attuale = [], []
    for riga in testo.splitlines():
        m = re.match(r"^(\d+) (\d+) (\d+) (\d+)(?: |$)", riga.strip())
        if m and int(m[3]) + int(m[4]) == int(m[2]) and (len(m[1]) == 4 or m[1] == "0"):
            attuale.append((m[1], int(m[2]), int(m[3])))
            continue
        m = re.match(r"^Total (\d+) (\d+) (\d+)", riga.strip())
        if m and attuale:
            tabelle.append((attuale, (int(m[1]), int(m[2]))))
            attuale = []
    if not ok(len(tabelle) == 8, f"Hawaii: {len(tabelle)} tabelle lette con pypdf, attese 8"):
        return {}, {}, {}
    for righe_t, (n, p) in tabelle:
        ok(sum(r[1] for r in righe_t) == n and sum(r[2] for r in righe_t) == p, "Hawaii: un totale non è la somma delle righe (pypdf)")

    def tronca(p, n):
        v = (1000 * p) // n
        return f"{v // 10}.{v % 10}%"
    naz, sta = tabelle[6], tabelle[7]      # ordine del bollettino: trimestre (4 tabelle), poi anno mobile: broker naz., broker stat., agente naz., agente stat.
    righe = {}
    for chiave, (righe_t, _) in (("national", naz), ("state", sta)):
        for cod, n, p in righe_t:
            righe.setdefault(cod, {"national": (0, 0, None), "state": (0, 0, None)})[chiave] = (n, p, tronca(p, n) if n else None)
    non_scuole = {c: righe.pop(c) for c in ("0", "5555", "7777", "8888", "9999") if c in righe}
    tot = {"national": (naz[1][0], naz[1][1], tronca(naz[1][1], naz[1][0])), "state": (sta[1][0], sta[1][1], tronca(sta[1][1], sta[1][0]))}
    return righe, tot, non_scuole


def rif_nebraska(F):
    """La trascrizione a mano: ogni riga deve tornare; dove la lettura automatica della scansione (tesseract) è pulita deve dire le stesse cifre."""
    m = json.loads((DATI / "manuali" / "ne_q1_2026.json").read_text(encoding="utf-8"))
    pdf = RADICE / F["ne_tassi"]["file"]
    ok(hashlib.sha256(pdf.read_bytes()).hexdigest() == m["sha256_pdf"], "Nebraska: la trascrizione non è legata a questo PDF")
    # Regola: solo un rapporto collegato dall'indice ufficiale della Commissione (mai un indirizzo indovinato).
    import pypdf
    collegati = set()
    for pagina in pypdf.PdfReader(str(RADICE / F["ne_indice"]["file"])).pages:
        for a in pagina.get("/Annots", []) or []:
            az = a.get_object().get("/A")
            if az and "/URI" in az:
                collegati.add(str(az["/URI"]))
    ok(F["ne_tassi"]["url"] in collegati, "Nebraska: il rapporto usato non è tra i collegamenti dell'indice ufficiale (examperformancebyschool.pdf)")
    if any(re.search(r"(second|third|fourth)\s*(%20)*quarter(%20)*2026", u, re.I) for u in collegati) and "firstquarter2026" in F["ne_tassi"]["url"]:
        AVV.append("Nebraska: l'indice ufficiale ora collega un trimestre 2026 più recente del primo: rifare la trascrizione su quello")
    # La scansione non ha strato di testo: seconda lettura automatica delle pagine (tesseract), indipendente dalla trascrizione a mano.
    sys.path.insert(0, str(RADICE / "raccolta"))
    import testo as T_ocr
    ocr = T_ocr.pdf_ocr(pdf)
    ok("01-Jan-2026 to 31-Mar-2026" in ocr and (m["periodo"]["dal"], m["periodo"]["al"]) == ("2026-01-01", "2026-03-31"), "Nebraska: periodo")
    blocchi = re.split(r"School Nam\S*\s*", ocr)[1:]
    ok(len(blocchi) == len(m["scuole"]) == 12, f"Nebraska: {len(blocchi)} scuole nella lettura automatica, {len(m['scuole'])} trascritte")
    righe, pulite, diverse, illeggibili = {}, 0, 0, 0
    quindici = re.compile(r"(?<![\w%])" + r"\s+".join([r"(\d+)\s+(\d+)\s+(\d+)%\s+(\d+)\s+(\d+)%"] * 3) + r"\s*$")
    for s in m["scuole"]:
        blocco = next((b for b in blocchi if f"({s['codice']})" in b[:120]), None)
        if not ok(blocco is not None, f"Nebraska: codice {s['codice']} non trovato nella lettura automatica del PDF"):
            continue
        attese = {tuple(r["first"] + r["repeat"] + r["all"]) for r in s["righe"].values()}
        for riga in blocco.splitlines():
            mm = quindici.search(riga)
            if mm:
                t = tuple(int(x) for x in mm.groups())
                if t in attese:
                    pulite += 1
                elif not all(t[i + 1] + t[i + 3] == t[i] and (not t[i] or (abs(100 * t[i + 1] / t[i] - t[i + 2]) <= 0.5 and abs(100 * t[i + 3] / t[i] - t[i + 4]) <= 0.5)) for i in (0, 5, 10)) \
                        or (t[0] + t[5], t[1] + t[6]) != (t[10], t[11]):
                    illeggibili += 1     # la riga letta dalla macchina non torna con la sua stessa aritmetica (es. un 1 letto come 4): è rumore, non una seconda lettura
                else:
                    diverse += 1
                    AVV.append(f"Nebraska/{s['nome']}: la lettura automatica della scansione legge {t}, che non è tra le righe trascritte (controllare a occhio sul PDF)")
        for nome_riga, r in s["righe"].items():
            for g in ("first", "repeat", "all"):
                n, p, pc, f, fc = r[g]
                ok(p + f == n and (not n or (abs(100 * p / n - pc) <= 0.5 and abs(100 * f / n - fc) <= 0.5)), f"Nebraska/{s['nome']}/{nome_riga}/{g}: la riga non torna")
            ok(r["first"][0] + r["repeat"][0] == r["all"][0] and r["first"][1] + r["repeat"][1] == r["all"][1], f"Nebraska/{s['nome']}/{nome_riga}: first + repeat ≠ all")
        v = {}
        for chiave, riga in (("national", "sales_national"), ("state", "sales_state")):
            r = s["righe"].get(riga)
            for g, coda in (("first", "_first"), ("all", "_all")):
                v[chiave + coda] = (r[g][0], r[g][1], f"{r[g][2]}%" if r[g][0] else None) if r else (0, 0, None)
        righe[(s["nome"].lower(), s["codice"])] = v
    ok(pulite >= 20, f"Nebraska: solo {pulite} righe della trascrizione confermate dalla lettura automatica della scansione")
    return righe, pulite, diverse


# ---------------------------------------------------------------- pagine
def visibile(html):
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", s)))


def leggi_tabella(html, s):
    """Righe della tabella pubblicata: [(nome minuscolo, sotto-nome, attributi, [(pc, p, n) per misura])] e la riga del totale."""
    m = re.search(r'<table class="dati tassi">.*?</table>', html, re.S)
    if not ok(m, f"{s}: tabella assente"):
        return [], None
    righe, totale = [], None
    for tr in re.findall(r"<tr[^>]*>.*?</tr>", m.group(0), re.S):
        if "<td" not in tr:
            continue
        celle = []
        for td in re.findall(r"<td class=\"r[^\"]*\">.*?</td>", tr, re.S):
            if 'class="r zero"' in td:
                ok(visibile(td).strip() == "– no exams", f"{s}: cella vuota scritta male")
                celle.append((None, 0, 0, False))
                continue
            pc = re.search(r'<span class="pc">(.*?)</span>', td).group(1)
            nn = re.search(r'<span class="nn">([\d,]+) of ([\d,]+) passed</span>', td)
            if not ok(nn, f"{s}: percentuale {pc} senza il numero di esami accanto"):
                continue
            celle.append((unescape(pc), int(nn[1].replace(",", "")), int(nn[2].replace(",", "")), "small sample" in td))
        ok(len(celle) == len(MISURE[s]), f"{s}: riga con {len(celle)} celle")
        th = re.search(r'<th scope="row">(.*?)</th>', tr, re.S).group(1)
        nome = unescape(re.sub(r"<small>.*?</small>", "", th, flags=re.S))
        sotto = unescape("".join(re.findall(r"<small>(.*?)</small>", th, re.S)))
        if 'class="tot-riga"' in tr:
            totale = (nome, celle)
        else:
            attr = dict(re.findall(r'data-([np]-\w+)="(\d+)"', tr))
            dn = re.search(r'data-nome="([^"]*)"', tr)
            ok(dn and unescape(dn.group(1)) == nome.lower(), f"{s}: data-nome diverso dal nome ({nome})")
            fm = re.search(r'data-formati="([^"]*)"', tr).group(1).split()
            righe.append((nome.lower(), sotto, attr, celle, fm))
    return righe, totale


def controlla_tassi(pagine, F):
    """Ogni cella delle quattro tabelle contro la seconda lettura dei file grezzi. Restituisce i valori attesi per le prove nel browser."""
    G = json.loads((DATI / "tassi.json").read_text(encoding="utf-8"))
    ok(G["soglia_campione"] == SOGLIA, "soglia dei campioni piccoli diversa da 30")
    tx, tx_tot = rif_texas(F)
    al, al_formati = rif_alabama(F)
    hi, hi_tot, hi_non = rif_hawaii(F)
    ne, ne_pulite, ne_diverse = rif_nebraska(F)
    rif = {"TX": {(k, None): v for k, v in tx.items()}, "AL": al, "NE": ne, "HI": hi}
    attesi_browser, n_celle = {}, 0
    for s, (nome_stato, slug) in STATI.items():
        html = pagine[f"/{slug}/"]
        righe, totale = leggi_tabella(html, s)
        mis = MISURE[s]
        ok(len(righe) == len(rif[s]) == len(G["stati"][s]["scuole"]), f"{s}: {len(righe)} righe in pagina, {len(rif[s])} nei file grezzi, {len(G['stati'][s]['scuole'])} in tassi.json")
        visti = set()
        for nome, sotto, attr, celle, fm in righe:
            if s == "TX":
                chiave = (nome, None)
            elif s == "HI":
                cod = re.search(r"school code (\d+)", sotto)
                chiave = cod.group(1) if cod else None
            else:
                cod = re.search(r"school code (\d+)", sotto)
                chiave = (nome, cod.group(1)) if cod else next((k for k in rif[s] if k[0] == nome and k not in visti), None)
            if not ok(chiave in rif[s] and chiave not in visti, f"{s}: scuola «{nome}» non ritrovata nei file grezzi (o doppia)"):
                continue
            visti.add(chiave)
            for k, (pc, p, n, piccolo) in zip(mis, celle):
                rn, rp, rpc = rif[s][chiave][k]
                ok((n, p, pc) == (rn, rp, rpc), f"{s}/{nome}/{k}: in pagina {pc} ({p} di {n}), nel file grezzo {rpc} ({rp} di {rn})")
                ok(piccolo == (0 < n < SOGLIA), f"{s}/{nome}/{k}: etichetta «small sample» sbagliata per {n} esami")
                ok(attr.get(f"n-{k}") == str(rn) and attr.get(f"p-{k}") == str(rp), f"{s}/{nome}/{k}: attributi dell'ordinamento diversi dal file grezzo")
                n_celle += 1
            if s == "AL":
                ok(fm == al_formati[chiave] and (not fm or " and ".join(fm).lower() in sotto.lower()), f"AL/{nome}: formato {fm} diverso dal file grezzo {al_formati[chiave]}")
        for nome, attese in ATTESO_RIGHE[s].items():
            trovate = [c for r_nome, _, _, c, _ in righe if r_nome == nome]
            ok(len(trovate) == 1 and [(pc, p, n) for pc, p, n, _ in trovate[0]] == [(attese[k][2], attese[k][1], attese[k][0]) for k in mis], f"{s}: la riga «{nome}» non ha le cifre trascritte a mano")
        # riga del totale
        if ok(totale, f"{s}: manca la riga del totale"):
            for k, (pc, p, n, _) in zip(mis, totale[1]):
                if s in ("TX", "HI"):
                    uff = (tx_tot if s == "TX" else hi_tot)[k]
                    ok((n, p, pc) == uff == ATTESO_TOTALI[s][k], f"{s}: totale ufficiale {k} in pagina {pc} ({p} di {n}), nel file {uff}, a mano {ATTESO_TOTALI[s][k]}")
                    ok("official" in totale[0], f"{s}: la riga del totale non dice che è ufficiale")
                else:
                    sn, sp = sum(v[k][0] for v in rif[s].values()), sum(v[k][1] for v in rif[s].values())
                    v, kk = mezzo_su(sp, sn, 1)
                    ok((n, p, pc) == (sn, sp, fmt(v, kk, 1)), f"{s}: somma {k} in pagina {pc} ({p} di {n}), ricalcolata {fmt(v, kk, 1)} ({sp} di {sn})")
                    ok("our sum" in totale[0], f"{s}: la riga del totale non dice che la somma è nostra")
        if s == "TX":
            ok(sum(v["first"][0] for v in tx.values()) == tx_tot["first"][0] and sum(v["first"][1] for v in tx.values()) == tx_tot["first"][1], "Texas: le scuole non sommano al totale (la pagina dice di sì)")
        if s == "HI":
            ok(sum(v["national"][0] for v in hi.values()) + sum(v["national"][0] for v in hi_non.values()) == hi_tot["national"][0], "Hawaii: scuole + categorie senza scuola ≠ totale")
            ok(f"{sum(v['national'][0] for v in hi_non.values())} national-part exams" in visibile(html), "Hawaii: il numero di esami senza scuola in pagina non è quello del file")
        vis = visibile(html)
        if s in PERIODI:
            ok(PERIODI[s] in vis, f"{s}: periodo «{PERIODI[s]}» assente")
        else:
            ok("previous 12 months" in vis and "updated the 10th of every month" in vis, "AL: periodo non spiegato")
        ok("small sample" in vis and "not a rating of a school" in vis and "do not rank or recommend schools" in vis, f"{s}: mancano le avvertenze sui campioni piccoli e sulla classifica")
        a_, m_, g_ = (int(x) for x in G["stati"][s]["letto_il"].split("-"))
        ok(f"official source read on {MESI[m_ - 1]} {g_}, {a_}" in vis, f"{s}: data di lettura assente")
        # valori attesi per il browser, dalla seconda lettura
        prim = mis[0]
        per_nome = {}
        for nome, sotto, attr, celle, fm in righe:
            per_nome[nome + "|" + sotto] = (nome, {k: (c[2], c[1]) for k, c in zip(mis, celle)}, fm)
        def chiave_esami(x):
            return (-x[1][prim][0], x[0])
        ordine_esami = [x[0] for x in sorted(per_nome.values(), key=chiave_esami)]
        per_tasso = {}
        for k in mis:
            def gruppo(x, k=k):
                n = x[1][k][0]
                return 0 if n >= SOGLIA else 1 if n > 0 else 2
            ordinati = sorted(per_nome.values(), key=lambda x, k=k: (gruppo(x), -(x[1][k][1] / x[1][k][0]) if x[1][k][0] else 1, -x[1][k][0], x[0]))
            lista, messo = [], False
            for x in ordinati:
                if not messo and gruppo(x) > 0 and ordinati and gruppo(ordinati[0]) == 0:
                    lista.append("--")
                    messo = True
                lista.append(x[0])
            per_tasso[k] = lista
        sopra = sum(1 for x in per_nome.values() if x[1][prim][0] >= SOGLIA)
        cerca = {"TX": "aceable", "AL": "colibri", "NE": "university", "HI": "maui"}[s]
        # ordine inverso: tra le scuole sopra soglia, la prima è quella con la percentuale più bassa (a parità: più esami, poi nome)
        sopra_l = [x for x in per_nome.values() if x[1][prim][0] >= SOGLIA]
        ultimo = sorted(sopra_l, key=lambda x: (x[1][prim][1] / x[1][prim][0], -x[1][prim][0], x[0]))[0][0] if sopra_l else None
        attesi_browser[slug] = {"primaria": prim, "per_esami": ordine_esami, "per_tasso": per_tasso, "sopra_soglia": sopra, "ultimo_sopra": ultimo, "cerca": cerca,
                                "cerca_n": sum(1 for x in per_nome.values() if cerca in x[0]),
                                "online": sum(1 for x in per_nome.values() if "Online" in x[2]) if s in ("AL", "HI") else None}
        # la tabella pubblicata è già nell'ordine per numero di esami
        ok([r[0] for r in righe] == ordine_esami or sorted(r[0] for r in righe) == sorted(ordine_esami), f"{s}: righe diverse")
        ordine_pagina = [(-r[3][0][2], r[0]) for r in righe]
        ok(ordine_pagina == sorted(ordine_pagina), f"{s}: la tabella pubblicata non parte dalle scuole con più esami")
    return G, attesi_browser, n_celle, ne_pulite, ne_diverse


def controlla_licenza(pagine, G):
    L = G["licenza"]
    for s, (nome, slug) in STATI.items():
        for k, v in ATTESO_LIC[s].items():
            ok(L[s].get(k) == v, f"licenza {s}: {k} = {L[s].get(k)} in tassi.json, {v} trascritto a mano")
        vis = visibile(pagine[f"/{slug}-real-estate-license/"])
        for pezzo in ATTESO_TESTO_LIC[s]:
            ok(pezzo in vis, f"/{slug}-real-estate-license/: manca «{pezzo}»")
        ok("our sum" in vis or s in ("AL", "HI"), f"licenza {s}: la somma delle tariffe non è segnata come nostra")
        ok(f"/{slug}/" in pagine[f"/{slug}-real-estate-license/"] and f"/{slug}-real-estate-license/" in pagine[f"/{slug}/"], f"{s}: le due pagine non si collegano")
    ok("do not print the license fee or the exam fee" in visibile(pagine["/alabama-real-estate-license/"]), "Alabama: la pagina deve dire che le tariffe non sono nelle pagine lette")
    ok("exam fee is not on the commission’s pages" in visibile(pagine["/hawaii-real-estate-license/"]), "Hawaii: la pagina deve dire che la tassa d'esame non è nelle pagine lette")
    ok("2026 is an even-numbered year" in visibile(pagine["/hawaii-real-estate-license/"]), "Hawaii: anno pari")


def controlla_pagine(F, testi):
    pagine = {}
    for p in sorted(SITO.rglob("*.html")):
        if p.name.startswith("google"):
            continue
        pagine["/" + str(p.relative_to(SITO)).replace("index.html", "")] = p.read_text(encoding="utf-8")
    attese = ({"/", "/404.html", "/how-we-check/", "/about/", "/privacy/"} | {f"/{v[1]}/" for v in STATI.values()} | {f"/{v[1]}-real-estate-license/" for v in STATI.values()})
    aff = json.loads((DATI / "affiliati.json").read_text(encoding="utf-8"))
    accesi = [p for p in aff["partner"] if p["attivo"]]
    for p in accesi:
        ok(p["link"].startswith("https://") and MON.dominio_ammesso(p["link"]), f"affiliati.json: {p['id']} attivo senza un link tracciato ammesso")
    for p in aff["partner"]:
        if not p["attivo"]:
            ok(p["link"] == "", f"affiliati.json: {p['id']} è spento ma ha un link (i link non si inventano)")
    link_partner = {p["link"] for p in accesi}
    ok(set(pagine) == attese, f"pagine: {sorted(set(pagine) ^ attese)}")
    titoli, descr = {}, {}
    sitemap = re.findall(r"<loc>(.*?)</loc>", (SITO / "sitemap.xml").read_text(encoding="utf-8"))
    ok(sorted(sitemap) == sorted(URL_SITO + u for u in pagine if u != "/404.html"), "sitemap diversa dalle pagine indicizzabili")
    frasi_fonti = {(fid, k): f["frasi"][k] for fid, f in F.items() for k in f["frasi"]}
    dom = {r["frase"]: r["volume_mese"] for r in json.loads((DATI / "domanda.json").read_text(encoding="utf-8"))["ricerche"]}
    n_faq, n_cit = 0, 0
    for u, html in pagine.items():
        t = re.findall(r"<title>(.*?)</title>", html)
        d = re.findall(r'<meta name="description" content="(.*?)">', html)
        ok(len(t) == 1 and len(d) == 1 and len(re.findall(r"<h1[ >]", html)) == 1, f"{u}: title, description o h1 non unici")
        t, d = unescape(t[0]), unescape(d[0])
        if u != "/404.html":
            ok(len(t) <= 65, f"{u}: titolo di {len(t)} caratteri")
            ok(40 <= len(d) <= 160, f"{u}: descrizione di {len(d)} caratteri")
            ok(t not in titoli.values() and d not in descr.values(), f"{u}: titolo o descrizione doppi")
            titoli[u], descr[u] = t, d
            ok(f'<link rel="canonical" href="{URL_SITO}{u}">' in html and "noindex" not in html, f"{u}: canonical")
        else:
            ok('content="noindex, follow"' in html, "404 senza noindex")
        vis = visibile(html)
        ok('lang="en-US"' in html and "goatcounter" in html and "not affiliated with any real estate commission, school or exam company" in vis, f"{u}: lingua, contatore o avvertenza")
        ok('<meta name="google-site-verification" content="btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI">' in html, f"{u}: verifica Google")
        ok(CHIAVE not in html and not MODELLI_VIETATI.search(vis), f"{u}: chiave o nome di modello nel testo")
        ok(not GIUDIZI.search(vis), f"{u}: parola di giudizio o di classifica: {GIUDIZI.search(vis).group(0) if GIUDIZI.search(vis) else ''}")
        for href in re.findall(r'href="(/[^"#]*)(?:#[^"]*)?"', html):
            if href.startswith("/assets/"):
                ok((SITO / href[1:]).exists(), f"{u}: risorsa mancante {href}")
            else:
                ok(href in pagine, f"{u}: link interno rotto {href}")
        for anc in re.findall(r'<a [^>]*href="(/[^"#]*)#([^"]+)"', html):
            ok(f'id="{anc[1]}"' in pagine.get(anc[0], ""), f"{u}: ancora #{anc[1]} assente in {anc[0]}")
        for n in re.findall(r'href="#(f\d+)"', html):
            ok(f'id="{n}"' in html, f"{u}: rimando {n} senza fonte")
        for href in set(re.findall(r'<a [^>]*href="(https?://[^"]+)"', html)):
            ok(unescape(href) in {f["url"] for fid, f in F.items() if fid not in FONTI_PARTNER} or unescape(href) in link_partner
               or re.match(r"https://(www\.goatcounter\.com|policies\.google\.com|adssettings\.google\.com|www\.google\.com|support\.google\.com)(/|$)", href),
               f"{u}: link esterno non previsto {href}")
        for fid, k, frase in re.findall(r'<blockquote class="cit" data-fonte="([\w]+)" data-frase="([\w]+)"><p>“<span data-cit>(.*?)</span>”</p>', html, re.S):
            ok(fid not in FONTI_PARTNER and unescape(frase) == frasi_fonti.get((fid, k)) and norm(unescape(frase)) in testi[fid], f"{u}: citazione {fid}/{k} non alla lettera")
            n_cit += 1
        ok(html.count("<blockquote") == html.count('<blockquote class="cit" data-fonte='), f"{u}: citazione senza fonte")
        visf = [(unescape(q), unescape(re.sub(r"<sup.*?</sup>", "", a, flags=re.S))) for q, a in re.findall(r'<div class="faq" data-ricerca="[^"]*"><h3>(.*?)</h3><p>(.*?)</p></div>', html, re.S)]
        ld = []
        for blocco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            j = json.loads(blocco)
            if j.get("@type") == "FAQPage":
                ld += [(x["name"], x["acceptedAnswer"]["text"]) for x in j["mainEntity"]]
        ok(visf == ld, f"{u}: FAQ visibili ({len(visf)}) diverse dal JSON-LD ({len(ld)})")
        ricerche = [unescape(r) for r in re.findall(r'<div class="faq" data-ricerca="([^"]*)"', html)]
        for ric in ricerche:
            ok(dom.get(ric, 0) > 0, f"{u}: FAQ senza ricerca misurata: {ric}")
        ok(len(ricerche) == len(set(ricerche)), f"{u}: due FAQ dalla stessa ricerca")
        ok(all("<" not in a for _, a in visf), f"{u}: HTML dentro una risposta FAQ")
        n_faq += len(visf)
        # riquadro del partner: assente finché nessun partner è acceso; se acceso, solo nelle pagine degli Stati elencati, sotto la tabella
        sponsorizzati = re.findall(r'<a\b[^>]*\brel="[^"]*sponsored[^"]*"[^>]*>', html)
        stato_pag = next((s for s, v in STATI.items() if u == f"/{v[1]}/"), None)
        qui = [p for p in accesi if stato_pag in p["stati"]]
        if not qui:
            ok("data-partner" not in html and not sponsorizzati and "aceable.com" not in html, f"{u}: riquadro o link di un partner dove non deve esserci")
        else:
            box = re.findall(r'<aside class="partner" data-partner.*?</aside>', html, re.S)
            if ok(len(box) == 1, f"{u}: riquadro del partner assente o doppio"):
                ok(len(sponsorizzati) == len(qui) and all(a in box[0] for a in sponsorizzati), f"{u}: link sponsorizzati fuori dal riquadro")
                for a in sponsorizzati:
                    rel = re.search(r'rel="([^"]*)"', a).group(1).split()
                    ok({"sponsored", "nofollow", "noopener"} <= set(rel) and unescape(re.search(r'href="([^"]*)"', a).group(1)) in link_partner, f"{u}: link del partner senza rel sponsored nofollow noopener o non registrato")
                ok("Advertisement" in box[0] and "we may earn a commission" in box[0] and "have not tested" in box[0], f"{u}: riquadro senza etichetta di pubblicità o riga di trasparenza")
                ok(not re.search(r"\$\s?\d|\d\s?%", visibile(box[0])), f"{u}: prezzo o percentuale nel riquadro del partner")
                ok(html.index("</table>") < html.index("data-partner"), f"{u}: riquadro del partner sopra la tabella ufficiale")
    ok(len(titoli) == 12, f"pagine indicizzabili: {len(titoli)}")
    ok(n_faq >= 30, f"FAQ: {n_faq}")

    # ---- file accessori
    ok((SITO / "ads.txt").read_text().strip() == "google.com, pub-3750093987658434, DIRECT, f08c47fec0942fa0", "ads.txt")
    ok((SITO / "robots.txt").read_text() == f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n", "robots.txt")
    ok((SITO / "b5a26a844a465f58552debee2c8a0114.txt").read_text() == "b5a26a844a465f58552debee2c8a0114", "file della chiave IndexNow")
    ok('ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."' in (SITO / "netlify.toml").read_text(), "netlify.toml senza la regola ignore")
    ok((SITO / "assets" / "og.png").exists(), "manca assets/og.png")
    ok("ca-pub-3750093987658434" in pagine["/"], "AdSense assente nella home")
    modulo = re.search(r'<form name="corrections".*?</form>', pagine["/how-we-check/"], re.S)
    ok(modulo and not re.search(r'name="(name|email|nome)"|type="email"', modulo.group(0)) and 'netlify-honeypot="bot-field"' in modulo.group(0) and 'name="bot-field"' in modulo.group(0),
       "modulo delle correzioni: campo personale o trappola per i robot assente")
    errori, _info = MON.controlla_sito("realestate", SITO)
    for e in errori:
        err(f"monetizzazione: {e}")
    for p in RADICE.rglob("*"):
        if p.is_file() and "cache" not in p.parts and p.suffix in (".py", ".js", ".json", ".md", ".html", ".txt", ".toml", ".xml", ".css", ".svg") and CHIAVE in p.read_text(encoding="utf-8", errors="ignore"):
            err(f"chiave seodata in {p}")
    return pagine, n_faq, n_cit


def controlla_home(pagine, G, attesi):
    vis = visibile(pagine["/"])
    ok("56.12%" in vis and "16,824 of 29,980" in vis, "home: totale del Texas")
    ok("36.3%" in vis and "721 of 1,986" in vis, "home: totale delle Hawaii")
    ok("our sum" in vis and "not comparable with each other" in vis, "home: le somme nostre e l'avvertenza sul confronto tra Stati")
    for s, (nome, slug) in STATI.items():
        ok(f"{len(attesi[slug]['per_esami'])} schools" in vis, f"home: numero di scuole di {nome}")


def strumenti():
    idx = (RADICE.parent / "studio-business" / "strumenti" / "indexnow.py").read_text(encoding="utf-8")
    ok('("real-estate-exam-pass-rates.netlify.app", "realestate")' in idx, "indexnow.py: sito non registrato")
    mj = json.loads((RADICE.parent / "studio-business" / "strumenti" / "monetizzazione.json").read_text(encoding="utf-8"))
    ok("realestate" in mj["adsense_siti"] and "realestate" in mj["_siti_della_rete"] and "realestate" in MON.SITI, "monetizzazione: sito non registrato")
    ok(URL_SITO in (RADICE / "genera.py").read_text(encoding="utf-8"), "genera.py e verifica.py hanno due indirizzi diversi")


def main():
    if not SITO.exists():
        raise SystemExit("manca realestate/sito: lanciare prima genera.py")
    F, testi = controlla_fonti()
    pagine, n_faq, n_cit = controlla_pagine(F, testi)
    G, attesi, n_celle, ne_pulite, ne_diverse = controlla_tassi(pagine, F)
    controlla_licenza(pagine, G)
    controlla_home(pagine, G, attesi)
    strumenti()
    if "--browser" in sys.argv and not ERR:
        import os
        p = subprocess.run(["node", str(RADICE / "verifica_browser.js")], env=dict(os.environ, ATTESI=json.dumps(attesi)), capture_output=True, text=True)
        print(p.stdout.strip())
        if p.returncode != 0:
            err("browser: " + (p.stderr.strip()[-1500:] or "errori sopra"))
    for a in AVV:
        print("AVVISO:", a)
    for e in ERR:
        print("ERRORE:", e)
    print(f"{len(F)} fonti e {sum(len(f['frasi']) for f in F.values())} frasi alla lettera · {n_celle} celle delle tabelle = seconda lettura dei file grezzi "
          f"(Nebraska: {ne_pulite} righe confermate dalla lettura automatica della scansione, {ne_diverse} da guardare) · {n_cit} citazioni in pagina · {n_faq} FAQ · "
          f"{len(pagine)} pagine · {len(ERR)} errori, {len(AVV)} avvisi")
    sys.exit(1 if ERR else 0)


if __name__ == "__main__":
    main()
