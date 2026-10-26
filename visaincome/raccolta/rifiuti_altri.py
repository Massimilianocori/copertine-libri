"""Scarica e legge i file ufficiali su visti concessi e rifiutati per nazionalità in Australia, Nuova Zelanda e Canada
e scrive visaincome/dati/rifiuti_altri.json (la sezione Schengen/UK resta in dati/rifiuti.json, scritta da rifiuti.py).

Uso (dalla radice del repository):
    python3 visaincome/raccolta/rifiuti_altri.py            # scarica (o riusa i file già in raccolta/_grezzi/) e scrive il JSON
    python3 visaincome/raccolta/rifiuti_altri.py --nuovo    # riscarica sempre i file ufficiali

Fonti (vedi NOTE.md, sezione del 26/10/2026):
1. Australia, studenti: Department of Home Affairs, "BP0015 Student visa grant rates" su data.gov.au (licenza CC BY 2.5 AU,
   dichiarata nel catalogo). L'URL del file più recente si prende dall'API del catalogo (package_show id=student-visas).
   Il file è una tabella pivot: i dati stanno nella cache (xl/pivotCache/pivotCacheRecords1.xml, ~2 milioni di righe),
   letta qui riga per riga. Campi: anno fiscale, trimestre, mese, luogo del richiedente, canale, settore, tipo di richiedente,
   Stato, genere, nazionalità, età, concessi, rifiutati, totale. Controlli: totale = concessi + rifiutati su ogni riga;
   numero di righe = recordCount dichiarato.
2. Australia, turisti: Department of Home Affairs, rapporto semestrale BR0112 "Visitor visa program" (PDF; contenuti del sito
   con licenza CC BY 3.0 AU). Tabelle 3.02 (Tourist Visitor 600/676) e 3.03 (Sponsored Tourist 600): tasso di concessione per
   nazionalità, 5 trimestri. Il PDF non dà il numero di decisioni: per la soglia si usano le concessioni del trimestre dal file
   BP0018 (data.gov.au, CC BY 2.5 AU), che sono un limite inferiore delle decisioni.
3. Nuova Zelanda: Immigration New Zealand (MBIE), PDF mensili "Visitor / Student / Work applications decided", tabella
   "... decided (applications), by nationality and financial year of decision" (licenza CC BY 3.0 NZ, pagina Copyright del sito).
   "Declined" per INZ comprende anche le domande ritirate. Controlli: approvate + respinte = totale per ogni anno; somma = totale generale.
4. Canada: IRCC, dataset "Operational Processing – Monthly IRCC Updates" (Open Government Licence – Canada): permessi temporanei
   esaminati (approvati, rifiutati e ritirati) e approvati per Paese e mese; permessi di studio nuovi esaminati; visti turistici
   V-1 approvati. Numeri arrotondati a 5, "--" = da 1 a 4 (non pubblicati).

Se un controllo fallisce, il JSON esistente NON viene toccato (esce con codice 1).
I file grezzi stanno in raccolta/_grezzi/ (esclusi da git, si riscaricano con questo script).
"""
import io
import json
import re
import subprocess
import sys
import urllib.parse
import zipfile
from collections import defaultdict
from datetime import date
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rifiuti import GREZZI, RADICE, impronta  # noqa: E402
from rifiuti import scarica as _scarica  # noqa: E402


def scarica(url, dest=None, nuovo=False, tentativi=4):
    """Come rifiuti.scarica, con nuovi tentativi se la connessione cade (succede con immigration.govt.nz)."""
    import time
    for i in range(tentativi):
        try:
            return _scarica(url, dest, nuovo)
        except OSError:
            if i == tentativi - 1:
                raise
            time.sleep(5 * (i + 1))

USCITA = RADICE / "dati" / "rifiuti_altri.json"

# ---------------------------------------------------------------- Australia
CKAN_AU = "https://data.gov.au/data/api/3/action/package_show?id={}"
PAGINA_AU_STUDENTI = "https://data.gov.au/data/dataset/student-visas"
PAGINA_AU_TURISTI_GRANT = "https://data.gov.au/data/dataset/visitor-visas-granted-pivot-table"
PAGINA_AU_VISIT = "https://www.homeaffairs.gov.au/research-and-statistics/statistics/visa-statistics/visit"
COPYRIGHT_AU = "https://www.homeaffairs.gov.au/access-and-accountability/using-our-website/copyright-and-disclaimer"
LIC_AU_DATI = ("CC BY 2.5 AU", "https://creativecommons.org/licenses/by/2.5/au/")
LIC_AU_SITO = ("CC BY 3.0 AU", "https://creativecommons.org/licenses/by/3.0/au/")
ANNI_AU_DETTAGLIO = 3  # anni fiscali (dal più recente, compreso quello in corso) con mesi e settori
CAMPI_AU = ["Financial Year of Decision", "Financial Year Quarter", "Month", "Client Location", "Lodgement Channel", "Sector",
            "Applicant Type", "Education Provider Registered State", "Gender", "Citizenship Country", "Age Group",
            "Grant Total", "Refused Total", "Total"]
# chiave delle coppie [concessi, rifiutati] per anno: luogo × tipo di richiedente
COMBO_AU = [("Outside Australia", "Primary"), ("Outside Australia", "Secondary"), ("In Australia", "Primary"), ("In Australia", "Secondary")]


def cache_pivot(dati_xlsx):
    """Campi e valori condivisi della cache pivot, e un generatore delle righe (liste di indici o numeri)."""
    z = zipfile.ZipFile(io.BytesIO(dati_xlsx))
    defin = z.read("xl/pivotCache/pivotCacheDefinition1.xml").decode("utf-8")
    campi = []
    for m in re.finditer(r'<cacheField name="([^"]+)"[^>]*>(.*?)</cacheField>', defin, re.S):
        valori = [x.replace("&amp;", "&").replace("&apos;", "'") for x in re.findall(r'<s v="([^"]*)"', m.group(2))]
        campi.append((m.group(1).replace("&amp;", "&"), valori))
    attese = int(re.search(r'recordCount="(\d+)"', defin).group(1))
    aggiornato = re.search(r'refreshedDate="([\d.]+)"', defin)
    tok = re.compile(rb'<(x|n)(?: v="([^"]*)")?/>')

    def righe():
        buf = b""
        with z.open("xl/pivotCache/pivotCacheRecords1.xml") as f:
            while True:
                c = f.read(1 << 24)
                if not c:
                    break
                buf += c
                ultimo = buf.rfind(b"</r>")
                if ultimo < 0:
                    continue
                parte, buf = buf[:ultimo + 4], buf[ultimo + 4:]
                for r in re.finditer(rb"<r>(.*?)</r>", parte):
                    yield [(int(v) if k == b"x" else float(v)) for k, v in tok.findall(r.group(1))]
    return campi, attese, (aggiornato.group(1) if aggiornato else ""), righe


def risorsa_ckan(id_pacchetto, contiene):
    d = json.loads(scarica(CKAN_AU.format(id_pacchetto))[0])["result"]
    r = next(x for x in d["resources"] if contiene in x["name"].lower() and x["url"].endswith(".xlsx"))
    return d, r


def leggi_au_studenti(dati):
    errori = []
    campi, attese, _agg, righe = cache_pivot(dati)
    nomi = [c for c, _ in campi]
    if nomi != CAMPI_AU:
        return None, [f"AU studenti: campi della pivot inattesi {nomi}"]
    val = {c: v for c, v in campi}
    anni = val["Financial Year of Decision"]
    i_anno, i_mese, i_luogo, i_sett, i_tipo, i_naz = (nomi.index(c) for c in (
        "Financial Year of Decision", "Month", "Client Location", "Sector", "Applicant Type", "Citizenship Country"))
    usati = set()
    per_anno = defaultdict(lambda: [0, 0])
    per_mese = defaultdict(lambda: [0, 0])
    per_sett = defaultdict(lambda: [0, 0])
    n = 0
    for r in righe():
        n += 1
        g, rf, t = r[11], r[12], r[13]
        if abs(g + rf - t) > 1e-9:
            errori.append(f"AU studenti: riga {n} con totale {t} diverso da {g} + {rf}")
            if len(errori) > 20:
                break
        a, naz, luogo, tipo = r[i_anno], val["Citizenship Country"][r[i_naz]], val["Client Location"][r[i_luogo]], val["Applicant Type"][r[i_tipo]]
        usati.add(a)
        k = (naz, a, luogo, tipo)
        per_anno[k][0] += g; per_anno[k][1] += rf
        km = (naz, a, r[i_mese], luogo, tipo)
        per_mese[km][0] += g; per_mese[km][1] += rf
        ks = (naz, a, r[i_sett], luogo, tipo)
        per_sett[ks][0] += g; per_sett[ks][1] += rf
    if n != attese:
        errori.append(f"AU studenti: lette {n} righe, il file ne dichiara {attese}")
    ordine = [i for i in range(len(anni)) if i in usati]
    etichette = [anni[i] for i in ordine]
    if not etichette or not re.match(r"\d{4}-\d{2} to \d{1,2} \w+ \d{4}$", etichette[-1]):
        errori.append(f"AU studenti: ultimo anno inatteso {etichette[-1:]}")
    recenti = ordine[-ANNI_AU_DETTAGLIO:]
    naz_out = {}
    for naz in sorted({k[0] for k in per_anno}):
        y = {}
        for a in ordine:
            celle = [[int(per_anno.get((naz, a, l, t), [0, 0])[0]), int(per_anno.get((naz, a, l, t), [0, 0])[1])] for l, t in COMBO_AU]
            if any(c[0] or c[1] for c in celle):
                y[anni[a]] = celle
        m, s = {}, {}
        for a in recenti:
            mesi = {}
            for im, nome_m in enumerate(val["Month"]):
                celle = [[int(per_mese.get((naz, a, im, l, t), [0, 0])[0]), int(per_mese.get((naz, a, im, l, t), [0, 0])[1])] for l, t in COMBO_AU]
                if any(c[0] or c[1] for c in celle):
                    mesi[nome_m] = celle
            if mesi:
                m[anni[a]] = mesi
            sett = {}
            for isx, nome_s in enumerate(val["Sector"]):
                celle = [[int(per_sett.get((naz, a, isx, l, t), [0, 0])[0]), int(per_sett.get((naz, a, isx, l, t), [0, 0])[1])] for l, t in COMBO_AU]
                if any(c[0] or c[1] for c in celle):
                    sett[nome_s] = celle
            if sett:
                s[anni[a]] = sett
        if y:
            naz_out[naz] = {"y": y, "m": m, "s": s}
    if len(naz_out) < 150:
        errori.append(f"AU studenti: solo {len(naz_out)} nazionalità")
    return {"anni": etichette, "mesi": val["Month"], "combo": [f"{l} · {t}" for l, t in COMBO_AU], "naz": naz_out, "righe": n}, errori


def pdf_testo(percorso):
    return subprocess.run(["pdftotext", "-layout", str(percorso), "-"], capture_output=True, check=True).stdout.decode("utf-8", "replace")


def leggi_au_turisti(testo):
    """Tabelle 3.02 e 3.03 del rapporto BR0112: {tabella: {nazionalità: [5 tassi]}}, etichette dei trimestri."""
    errori, out, trimestri = [], {}, []
    for num in ("3.02", "3.03"):
        m = re.search(rf"\n{re.escape(num)} Grant rate for (.+?) visa applications decided.*?\n(.*?)\n(?:\d\.\d\d |\s*BR0112)", testo, re.S)
        if not m:
            errori.append(f"AU turisti: tabella {num} non trovata")
            continue
        blocco = m.group(2)
        date_t = re.findall(r"(\d\d/\d\d/\d\d) to", blocco)
        fine_t = re.findall(r"\b(\d\d/\d\d/\d\d)\b(?! to)", blocco)
        righe = {}
        for riga in blocco.splitlines():
            r = re.match(r"\s*(\S.*?\S)\s{2,}([\d.]+%)\s+([\d.]+%)\s+([\d.]+%)\s+([\d.]+%)\s+([\d.]+%)\s*$", riga)
            if r:
                righe[r.group(1)] = [float(x.rstrip("%")) / 100 for x in r.groups()[1:]]
        if len(righe) < 15 or not any(k.startswith("All ") for k in righe):
            errori.append(f"AU turisti: tabella {num} con {len(righe)} righe")
        if len(date_t) >= 5 and len(fine_t) >= 5:
            t = [f"{a}–{b}" for a, b in zip(date_t[:5], fine_t[:5])]
            if trimestri and t != trimestri:
                errori.append("AU turisti: trimestri diversi tra le tabelle")
            trimestri = t
        else:
            errori.append(f"AU turisti: date dei trimestri non lette nella tabella {num}")
        out[num] = {"nome": m.group(1).strip(), "righe": righe}
    return out, trimestri, errori


def concessi_bp0018(dati, anno, trimestre):
    """Concessioni del trimestre per nazionalità dal file BP0018: {(gruppo): {nazionalità: n}} per i visti 600/676."""
    campi, attese, _agg, righe = cache_pivot(dati)
    nomi = [c for c, _ in campi]
    val = {c: v for c, v in campi}
    attesi = ["Financial Year of Visa Grant", "Financial Year Quarter", "Month", "Visa Subclass", "Visa Type", "Visa Group",
              "Client Location", "Citizenship Country", "Total"]
    if nomi != attesi:
        return None, [f"AU BP0018: campi inattesi {nomi}"]
    out = defaultdict(lambda: defaultdict(int))
    n = 0
    for r in righe():
        n += 1
        if val[nomi[0]][r[0]] != anno or val[nomi[1]][r[1]] != trimestre:
            continue
        sub, gruppo = val["Visa Subclass"][r[3]], val["Visa Group"][r[5]]
        naz = val["Citizenship Country"][r[7]]
        if sub in ("600 Visitor", "676 Tourist") and gruppo == "Tourist":
            out["3.02"][naz] += int(r[8])
        if sub == "600 Visitor" and gruppo == "Sponsored Family":
            out["3.03"][naz] += int(r[8])
    errori = [] if n == attese else [f"AU BP0018: lette {n} righe su {attese}"]
    return {k: dict(v) for k, v in out.items()}, errori


# ---------------------------------------------------------------- Nuova Zelanda
PAGINA_NZ = "https://www.immigration.govt.nz/about-us/research-and-statistics/immigration-statistics/statistics/"
COPYRIGHT_NZ = "https://www.immigration.govt.nz/about-us/about-this-site/copyright/"
LIC_NZ = ("CC BY 3.0 NZ", "https://creativecommons.org/licenses/by/3.0/nz/")
FILE_NZ = {"visitor": "statistics-visitor-applications-decided.pdf", "student": "statistics-student-applications-decided.pdf",
           "work": "statistics-work-applications-decided.pdf"}
TITOLI_NZ = {"visitor": "Visitors Visas decided (applications), by nationality and financial year of decision",
             "student": "Student Visas decided (applications), by nationality and financial year of decision",
             "work": "Work Visas decided (applications), by nationality and financial year of decision"}
NUM = r"\d{1,3}(?:,\d{3})*"


def leggi_nz(testo, tipo):
    """Prima tabella "<tipo> decided (applications), by nationality and financial year": {nazionalità: {anno: [approvate, respinte]}}."""
    errori = []
    i = testo.find(TITOLI_NZ[tipo])
    if i < 0:
        return None, None, [f"NZ {tipo}: tabella per nazionalità non trovata"]
    j = testo.find("(people), by nationality", i)
    blocco = testo[i:j if j > 0 else None]
    periodo = re.search(r"Date of decision between (\d{1,2} \w+ \d{4}) and (\d{1,2} \w+ \d{4})", blocco)
    preparato = re.search(r"(?:Date Prepared|Report prepared):\s*(\d{1,2} \w+ \d{4})", testo)
    anni = []
    for a in re.findall(r"\b(20\d\d/\d\d)\b", blocco):
        if a not in anni:
            anni.append(a)
    attesi = len(anni) * 3 + 1  # per anno approvate, respinte, totale; poi totale generale
    pezzi = defaultdict(list)
    ordine = []
    linee = blocco.splitlines()
    solo_testo = lambda k: 0 <= k < len(linee) and bool(re.match(r"[A-Za-z][^\d]*$", linee[k])) and not linee[k].startswith(" ")  # noqa: E731
    solo_numeri = lambda k: 0 <= k < len(linee) and bool(re.match(rf"\s+(?:{NUM}\s*)+$", linee[k]))  # noqa: E731
    for i_l, riga in enumerate(linee):
        r = re.match(rf"\s*([A-Za-z][^\d]*?)\s{{2,}}((?:{NUM}\s*)+)$", riga)
        if r:
            nome = re.sub(r"\s+", " ", r.group(1)).strip()
            # nome su due righe ("Bosnia &" + "Herzegovina"): la riga subito sotto ha solo testo (e non è l'inizio di un nome su tre righe)
            if solo_testo(i_l + 1) and not solo_numeri(i_l + 2):
                nome = f"{nome} {linee[i_l + 1].strip()}"
        elif solo_numeri(i_l) and solo_testo(i_l - 1):
            # nome su tre righe: "British Indian Ocean" / numeri / "Territory"
            nome = linee[i_l - 1].strip() + (f" {linee[i_l + 1].strip()}" if solo_testo(i_l + 1) else "")
            r = re.match(r"(\s*)(.*)$", riga)
        else:
            continue
        if nome.startswith(("Data for period", "Nationality Country")):
            continue
        numeri = [int(x.replace(",", "")) for x in re.findall(NUM, r.group(2))]
        if nome not in pezzi:
            ordine.append(nome)
        pezzi[nome].append(numeri)
    out = {}
    for nome in ordine:
        numeri = [x for p in pezzi[nome] for x in p]
        if len(numeri) != attesi:
            errori.append(f"NZ {tipo}: {nome} ha {len(numeri)} numeri invece di {attesi}")
            continue
        v = {}
        for k, a in enumerate(anni):
            ap, de, to = numeri[3 * k:3 * k + 3]
            if ap + de != to:
                errori.append(f"NZ {tipo}: {nome} {a}: {ap} + {de} ≠ {to}")
            v[a] = [ap, de]
        if sum(a + d for a, d in v.values()) != numeri[-1]:
            errori.append(f"NZ {tipo}: {nome}: somma degli anni diversa dal totale {numeri[-1]}")
        out[nome] = v
    tot = out.pop("Total", None)
    if not tot:
        errori.append(f"NZ {tipo}: riga Total non letta")
    else:
        for a in anni:
            s = [sum(v[a][0] for v in out.values()), sum(v[a][1] for v in out.values())]
            if s != tot[a]:
                errori.append(f"NZ {tipo} {a}: somma delle nazionalità {s} diversa dalla riga Total {tot[a]}")
    if len(out) < 100:
        errori.append(f"NZ {tipo}: solo {len(out)} nazionalità lette")
    info = {"anni": anni, "periodo": [periodo.group(1), periodo.group(2)] if periodo else [], "preparato": preparato.group(1) if preparato else ""}
    return out, info, errori


# ---------------------------------------------------------------- Canada
CKAN_CA = "https://open.canada.ca/data/api/3/action/package_show?id=9b34e712-513f-44e9-babf-9df4f7256550"
PAGINA_CA = "https://open.canada.ca/data/en/dataset/9b34e712-513f-44e9-babf-9df4f7256550"
LIC_CA = ("Open Government Licence – Canada", "https://open.canada.ca/en/open-government-licence-canada")
FILE_CA = {"tr_processed": "Open Data - OPS TR Processed en.xlsx", "tr_approved": "Open Data - OPS TR Approved en.xlsx",
           "sp_processed": "Open Data - OPS SP Processed en.xlsx", "trv_approved": "Open Data - OPS TRV V-1 Approved en.xlsx"}
MESI_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def leggi_ca(percorso, chiave):
    """{Paese: {"AAAA-MM": numero o None}} da un file mensile IRCC; controlla il totale annuo dichiarato quando è possibile."""
    errori = []
    ws = openpyxl.load_workbook(percorso, read_only=True, data_only=True).worksheets[0]
    righe = [list(r) for r in ws.iter_rows(values_only=True)]
    titolo = next((str(r[0]) for r in righe[:6] if r and r[0]), "")
    i_anni = next(i for i, r in enumerate(righe) if any(isinstance(x, int) and 2000 < x < 2100 for x in r[1:]))
    r_anni, r_mesi = righe[i_anni], righe[i_anni + 1]
    colonne, anno = [], None
    for c in range(1, len(r_mesi)):
        if isinstance(r_anni[c], int):
            anno = r_anni[c]
        m = str(r_mesi[c] or "").strip()
        if m in MESI_EN:
            colonne.append((c, f"{anno}-{MESI_EN.index(m) + 1:02d}", anno))
        elif m == "Total":
            colonne.append((c, f"{anno}-tot", anno))
    out, totali, note = {}, {}, []
    for r in righe[i_anni + 2:]:
        if not r or r[0] is None:
            continue
        nome = str(r[0]).strip()
        if all(x is None for x in r[1:]):
            if nome:
                note.append(nome)
            continue
        v, tot = {}, {}
        for c, k, a in colonne:
            x = r[c] if c < len(r) else None
            n = None if (x is None or (isinstance(x, str) and x.strip() in ("--", "–", "-", ""))) else int(x)
            if k.endswith("-tot"):
                tot[a] = n
            else:
                v[k] = n
        out[nome] = v
        totali[nome] = {str(a): n for a, n in tot.items()}
        for a, t in tot.items():
            mesi = [x for k, x in v.items() if k.startswith(f"{a}-")]
            # totale dichiarato: se nessun mese è soppresso, la somma deve stare entro l'arrotondamento a 5 di ogni cella
            if t is not None and mesi and all(x is not None for x in mesi) and abs(sum(mesi) - t) > 5 * len(mesi):
                errori.append(f"CA {chiave}: {nome} {a}: somma dei mesi {sum(mesi)} lontana dal totale {t}")
    if len(out) < 150:
        errori.append(f"CA {chiave}: solo {len(out)} Paesi")
    mesi = [k for _, k, _ in colonne if not k.endswith("-tot")]
    return {"titolo": re.sub(r"\s+", " ", titolo), "mesi": mesi, "paesi": out, "totali": totali, "note": note}, errori


# ---------------------------------------------------------------- principale
def main():
    nuovo = "--nuovo" in sys.argv
    oggi = date.today().isoformat()
    errori, fonti = [], {}

    # Australia, studenti
    pacc, ris = risorsa_ckan("student-visas", "grant rate")
    b, meta = scarica(ris["url"], GREZZI / "au-bp0015-grant-rates.xlsx", nuovo)
    au, e = leggi_au_studenti(b)
    errori += e
    fonti["au_studenti"] = {
        "titolo": ris["name"], "editore": "Australian Government Department of Home Affairs", "url": ris["url"], "pagina": PAGINA_AU_STUDENTI,
        "formato": "XLSX", "file": ris["url"].rsplit("/", 1)[-1], "byte": len(b), "sha256": impronta(b),
        "scaricato_il": meta.get("scaricato_il", oggi), "last_modified": meta.get("last_modified", ""),
        "aggiornato_catalogo": (ris.get("last_modified") or "")[:10], "licenza": LIC_AU_DATI[0], "licenza_url": LIC_AU_DATI[1],
        "licenza_catalogo": pacc.get("license_title", ""),
        "attribuzione": "Source: Australian Government Department of Home Affairs, BP0015 Student visa grant rates, data.gov.au, CC BY 2.5 AU. "
                        "The Department is not responsible for our analysis of the data.",
        "righe": au["righe"] if au else 0, "ultimo_periodo": au["anni"][-1] if au else ""}
    if pacc.get("license_id") != "cc-by-2.5":
        errori.append(f"AU studenti: licenza del catalogo cambiata ({pacc.get('license_id')})")

    # Australia, turisti (rapporto BR0112) e concessioni BP0018 per la soglia
    pag, _ = scarica(PAGINA_AU_VISIT)
    pdfs = re.findall(r'href="(/research-and-stats/files/visitor-visa-[a-z]+-\d{4}\.pdf)"', pag.decode("utf-8", "replace"))
    if not pdfs:
        errori.append("AU turisti: nessun PDF BR0112 sulla pagina")
        tur, trim = {}, []
        url_vis = ""
    else:
        url_vis = "https://www.homeaffairs.gov.au" + pdfs[0]  # la pagina li elenca dal più recente
        bv, metav = scarica(url_vis, GREZZI / "au-br0112-visitor.pdf", nuovo)
        testo = pdf_testo(GREZZI / "au-br0112-visitor.pdf")
        data_rapp = re.search(r"Program Report\s*\n\s*(\d{1,2} \w+ \d{4})", testo)
        tur, trim, e = leggi_au_turisti(testo)
        errori += e
        fonti["au_turisti"] = {
            "titolo": "BR0112 Visitor visa program report" + (f", {data_rapp.group(1)}" if data_rapp else ""),
            "editore": "Australian Government Department of Home Affairs", "url": url_vis, "pagina": PAGINA_AU_VISIT, "formato": "PDF",
            "byte": len(bv), "sha256": impronta(bv), "scaricato_il": metav.get("scaricato_il", oggi), "last_modified": metav.get("last_modified", ""),
            "data_rapporto": data_rapp.group(1) if data_rapp else "", "licenza": LIC_AU_SITO[0], "licenza_url": LIC_AU_SITO[1], "copyright": COPYRIGHT_AU,
            "attribuzione": "Source: Australian Government Department of Home Affairs, BR0112 Visitor visa program report, CC BY 3.0 AU."}
    concessi = {}
    if trim:
        # ultimo trimestre del rapporto -> anno fiscale e trimestre del file BP0018
        g, m_, a2 = trim[-1].split("–")[1].split("/")
        anno_cal, mese = 2000 + int(a2), int(m_)
        fy = f"{anno_cal if mese >= 7 else anno_cal - 1}-{str((anno_cal + 1) if mese >= 7 else anno_cal)[2:]}"
        qn = {9: "Q1 (Jul-Sep)", 12: "Q2 (Oct-Dec)", 3: "Q3 (Jan-Mar)", 6: "Q4 (Apr-Jun)"}[mese]
        pacc2, ris2 = risorsa_ckan("visitor-visas-granted-pivot-table", "granted")
        b2, meta2 = scarica(ris2["url"], GREZZI / "au-bp0018-visitor-granted.xlsx", nuovo)
        concessi, e = concessi_bp0018(b2, fy, qn)
        errori += e
        # controllo incrociato: concessioni "Sponsored Tourist" dell'anno fiscale nel PDF (tabella 2.04) = BP0018 (600, Sponsored Family)
        i204 = testo.find("2.04 Number of Tourism Visitor visa applications granted")
        m204 = re.search(r"\n\s*Sponsored Tourist\s+([\d,]+)\s+([\d,]+)\s+-?[\d.]+%", testo[i204:i204 + 4000]) if i204 >= 0 else None
        if m204:
            trimestri_fy = ["Q1 (Jul-Sep)", "Q2 (Oct-Dec)", "Q3 (Jan-Mar)", "Q4 (Apr-Jun)"]
            tot_sf = sum(sum(concessi_bp0018(b2, fy, q)[0]["3.03"].values()) for q in trimestri_fy[:trimestri_fy.index(qn) + 1])
            if tot_sf != int(m204.group(2).replace(",", "")):
                errori.append(f"AU turisti: Sponsored Tourist nel PDF {m204.group(2)} diverso da BP0018 {tot_sf}")
            controllo_204 = f"Sponsored Tourist {fy} fino a {qn}: PDF {m204.group(2)} = BP0018 {tot_sf:,}"
        else:
            errori.append("AU turisti: tabella 2.04 (Sponsored Tourist) non letta")
            controllo_204 = ""
        fonti["au_turisti_concessi"] = {
            "titolo": ris2["name"], "editore": "Australian Government Department of Home Affairs", "url": ris2["url"], "pagina": PAGINA_AU_TURISTI_GRANT,
            "formato": "XLSX", "byte": len(b2), "sha256": impronta(b2), "scaricato_il": meta2.get("scaricato_il", oggi),
            "licenza": LIC_AU_DATI[0], "licenza_url": LIC_AU_DATI[1], "licenza_catalogo": pacc2.get("license_title", ""),
            "uso": f"solo controllo della soglia: concessioni di {fy} {qn} (limite inferiore delle decisioni)", "controllo": controllo_204,
            "anno_trimestre": [fy, qn]}

    # Nuova Zelanda
    nz, info_nz = {}, {}
    for tipo, nome in FILE_NZ.items():
        url = "https://www.immigration.govt.nz/assets/inz/documents/statistics/" + nome
        bn, metan = scarica(url, GREZZI / f"nz-{nome}", nuovo)
        dati_nz, info, e = leggi_nz(pdf_testo(GREZZI / f"nz-{nome}"), tipo)
        errori += e
        nz[tipo] = dati_nz
        info_nz[tipo] = info
        fonti[f"nz_{tipo}"] = {
            "titolo": TITOLI_NZ[tipo], "editore": "Immigration New Zealand, Ministry of Business, Innovation and Employment", "url": url,
            "pagina": PAGINA_NZ, "formato": "PDF", "byte": len(bn), "sha256": impronta(bn), "scaricato_il": metan.get("scaricato_il", oggi),
            "last_modified": metan.get("last_modified", ""), "preparato": (info or {}).get("preparato", ""), "periodo": (info or {}).get("periodo", []),
            "licenza": LIC_NZ[0], "licenza_url": LIC_NZ[1], "copyright": COPYRIGHT_NZ,
            "attribuzione": "Crown copyright, Immigration New Zealand (MBIE), immigration.govt.nz, licensed under CC BY 3.0 NZ."}
    if info_nz and len({tuple(i["anni"]) for i in info_nz.values() if i}) != 1:
        errori.append("NZ: anni diversi tra i tre PDF")

    # Canada
    pc = json.loads(scarica(CKAN_CA)[0])["result"]
    if "open-government-licence-canada" not in (pc.get("license_url") or ""):
        errori.append(f"CA: licenza del dataset cambiata ({pc.get('license_url')})")
    ca = {}
    for k, nome in FILE_CA.items():
        url = "https://www.ircc.canada.ca/opendata-donneesouvertes/data/" + urllib.parse.quote(nome)
        bc, metac = scarica(url, GREZZI / f"ca-{k}.xlsx", nuovo)
        d, e = leggi_ca(GREZZI / f"ca-{k}.xlsx", k)
        errori += e
        ca[k] = d
        fonte_dati = next((x for x in d["note"] if x.startswith("Data Source")), "")
        fonti[f"ca_{k}"] = {
            "titolo": d["titolo"], "editore": "Immigration, Refugees and Citizenship Canada (IRCC)", "url": url, "pagina": PAGINA_CA, "formato": "XLSX",
            "byte": len(bc), "sha256": impronta(bc), "scaricato_il": metac.get("scaricato_il", oggi), "last_modified": metac.get("last_modified", ""),
            "dati_al": fonte_dati.replace("Data Source: MBR as of ", ""), "licenza": LIC_CA[0], "licenza_url": LIC_CA[1],
            "attribuzione": "Contains information licensed under the Open Government Licence – Canada.", "note": d["note"]}
    if ca and len({tuple(d["mesi"]) for d in ca.values()}) != 1:
        errori.append("CA: mesi diversi tra i file")
    if "tr_processed" in ca and "tr_approved" in ca:
        for p, v in ca["tr_processed"]["paesi"].items():
            a = ca["tr_approved"]["paesi"].get(p, {})
            for mese, x in v.items():
                y = a.get(mese)
                if x is not None and y is not None and y > x + 5:
                    errori.append(f"CA: {p} {mese}: approvati {y} più degli esaminati {x}")

    if errori:
        print("ERRORI: il file dei dati NON è stato aggiornato")
        for x in errori[:40]:
            print(" -", x)
        sys.exit(1)
    uscita = {
        "_nota": "Generato da raccolta/rifiuti_altri.py: non modificare a mano. au.naz[n].y[anno] = 4 coppie [concessi, rifiutati] nell'ordine di au.combo "
                 "(luogo · tipo di richiedente); .m[anno][mese] e .s[anno][settore] uguali, solo per gli ultimi anni. au_turisti: tassi di concessione "
                 "(0-1) per trimestre. nz[tipo][nazionalità][anno] = [approvate, respinte (comprese le ritirate)]. ca[file].paesi[Paese][AAAA-MM] = persone "
                 "(None = da 1 a 4, non pubblicato); ca[file].totali[Paese][AAAA] = colonna Total del file (arrotondata da IRCC sui dati non arrotondati).",
        "generato_il": oggi, "fonti": fonti,
        "au": {k: v for k, v in au.items() if k != "righe"},
        "au_turisti": {"trimestri": trim, "tabelle": tur, "concessi_ultimo_trimestre": concessi},
        "nz": {"info": info_nz, "tipi": nz},
        "ca": {k: {"mesi": d["mesi"], "paesi": d["paesi"], "totali": d["totali"]} for k, d in ca.items()},
    }
    USCITA.write_text(json.dumps(uscita, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Scritto {USCITA}: AU studenti {au['anni'][0]}–{au['anni'][-1]}, {len(au['naz'])} nazionalità, {au['righe']:,} righe; "
          f"AU turisti {len(trim)} trimestri, tabelle {', '.join(tur)}; NZ {', '.join(f'{t} {len(v)}' for t, v in nz.items())} nazionalità; "
          f"CA {len(ca['tr_processed']['mesi'])} mesi, {len(ca['tr_processed']['paesi'])} Paesi.")


if __name__ == "__main__":
    main()
