"""Liste ufficiali di università per i visti dei laureati: UK High Potential Individual (HPI), Hong Kong Top Talent Pass Scheme (TTPS),
Giappone J-Find (sezione /top-university-visas/, dal 5/11/2026). Scrive visaincome/dati/top_university.json.

Uso (dalla radice del repository):
    python3 visaincome/raccolta/top_university.py              # rilegge le liste e le pagine ufficiali
    python3 visaincome/raccolta/top_university.py --domanda    # rifà anche l'autocompletamento di Google

Fonti (lette il 5/11/2026, HTTP 200; i file grezzi vanno in raccolta/_grezzi/top_university/, esclusi da git):
1. GOV.UK, "High Potential Individual visa: global universities list" (Content API): pagina della raccolta e una pagina per anno
   (2021-2026, tabella HTML "università | Paese" e la frase con il periodo dei titoli). OGL v3.0.
2. GOV.UK, guida "High Potential Individual (HPI) visa" (Content API, tutte le parti): durata, 5 anni, limite annuale, tariffe.
3. Immigration Department di Hong Kong: pagina TTPS, pagina "New Fee Structure for Visa Applications under Specified Schemes",
   PDF "Aggregate List of Eligible Universities" (aggregate_list.pdf, letto con pdftotext -layout; asterisco = nuove; nota delle 4 tolte).
4. Immigration Services Agency del Giappone: pagina J-Find (giapponese), PDF della lista "As of October 2026" (001394994.pdf, tabelle lette
   con pdfplumber), PDF "Outline J-Find (English)".
Ogni frase usata nelle pagine ha il FRAMMENTO in LETTURE; se un frammento manca, o il numero di righe di una lista non torna, il JSON NON
viene aggiornato. Nomi delle università: una tabella di corrispondenze scritta a mano (ALIAS) unisce i nomi scritti in modo diverso nelle liste.
"""
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from infermieri import get, nuova_domanda, testo_html  # noqa: E402
from rifiuti import GREZZI, RADICE  # noqa: E402

USCITA = RADICE / "dati" / "top_university.json"
CART = GREZZI / "top_university"
API = "https://www.gov.uk/api/content"
HPI_RACCOLTA = "/government/publications/high-potential-individual-visa-global-universities-list"
HPI_ANNI = [2021, 2022, 2023, 2024, 2025, 2026]
HPI_GUIDA = "/high-potential-individual-visa"
TTPS_PAGINA = "https://www.immd.gov.hk/eng/services/visas/TTPS.html"
TTPS_TARIFFE = "https://www.immd.gov.hk/eng/specifiedschemes.html"
TTPS_PDF = "https://www.immd.gov.hk/pdf/aggregate_list.pdf"
JF_PAGINA = "https://www.moj.go.jp/isa/applications/status/designatedactivities51.html"
JF_PDF = "https://www.moj.go.jp/isa/content/001394994.pdf"
JF_OUTLINE = "https://www.moj.go.jp/isa/content/001401538.pdf"

# chiave -> (fonte, valore, frammento): il frammento deve essere nel testo della fonte (spazi normalizzati)
LETTURE = {
    # GOV.UK, guida HPI
    "hpi_durata": ("hpi_guida", 2, "An HPI visa lasts for 2 years. If you have a PhD or other doctoral qualification, it will last for 3 years."),
    "hpi_5anni": ("hpi_guida", 5, "To apply, you must have been awarded a qualification by an eligible university in the last 5 years."),
    "hpi_limite": ("hpi_guida", True, "There is a yearly limit on applications for this visa. The application year runs between 1 November and 31 October."),
    "hpi_mese": ("hpi_guida", True, "Check the list of eligible universities for the month and year you were awarded your qualification"),
    "hpi_uk": ("hpi_guida", True, "UK universities are not eligible."),
    "hpi_classifiche": ("hpi_guida", True, "The list of eligible universities is based on rankings of universities from around the world."),
    "hpi_livello": ("hpi_guida", True, "Your qualification must be at the same level as: a UK bachelor’s degree a UK postgraduate degree a UK PhD or doctorate"),
    "hpi_ecctis_uni": ("hpi_guida", True, "Ecctis will not check if your university is eligible."),
    "hpi_offerta": ("hpi_guida", True, "You do not need to have a job offer to apply."),
    "hpi_una_volta": ("hpi_guida", True, "You can only apply for an HPI visa once."),
    "hpi_proroga": ("hpi_guida", True, "You cannot extend your HPI visa."),
    "hpi_graduate": ("hpi_guida", True, "you have already been given a Graduate visa"),
    "hpi_tassa": ("hpi_guida", 880, "pay the £880 application fee"),
    "hpi_ecctis": ("hpi_guida", 252, "pay £252 for Ecctis to check your qualification is valid (this includes VAT)"),
    "hpi_ihs": ("hpi_guida", 1035, "pay the healthcare surcharge - this is usually £1,035 for each year you’ll be in the UK"),
    "hpi_ihs2": ("hpi_guida", 2070, "2 years - it will cost £2,070"),
    "hpi_fondi": ("hpi_guida", 1270, "you’ll usually need to have at least £1,270 available (unless you’re exempt)"),
    "hpi_inglese": ("hpi_guida", "B2", "to at least level B2 on the Common European Framework of Reference for Languages (CEFR) scale"),
    "hpi_tempi": ("hpi_guida", 3, "3 weeks, if you’re outside the UK"),
    "hpi_nov2021": ("hpi_guida", "2021-11-01", "1 November 2021 to 31 October 2022 UK universities are not eligible."),
    # GOV.UK, pagina della raccolta
    "hpi_rimossa2020": ("hpi_raccolta", True, "Removed the High Potential Individual visa: global universities list 2020 as it is outdated."),
    "hpi_5anni_raccolta": ("hpi_raccolta", True, "You can apply for the HPI route if you have graduated from an eligible international university in the 5 years immediately before your application."),
    # Hong Kong, pagina TTPS
    "ttps_durata": ("ttps_pagina", 24, "Successful TTPS applicant will normally be granted an initial stay of 36 months (Category A) / 24 months (Categories B and C) on time limitation only without other conditions of stay."),
    "ttps_offerta": ("ttps_pagina", True, "are not required to have secured an offer of employment in the HKSAR upon application"),
    "ttps_a": ("ttps_pagina", 2500000, "reaching HK$2.5 million or above"),
    "ttps_b": ("ttps_pagina", 3, "with at least three years of work experience"),
    "ttps_c": ("ttps_pagina", 3, "with less than three years of work experience"),
    "ttps_quota": ("ttps_pagina", True, "subject to an annual quota which is to be allotted on a first-come, first-served basis (Category C)"),
    "ttps_c_locali": ("ttps_pagina", True, "Category C does not apply to those non-local students"),
    "ttps_5anni": ("ttps_pagina", 5, "Graduation in the past five years is counted by “year of graduation”."),
    "ttps_bachelor": ("ttps_pagina", True, "must be equivalent to the recognised Hong Kong standard of bachelor’s degrees"),
    "ttps_rami": ("ttps_pagina", True, "the branch schools, the extension schools or the subsidiary schools, etc., established by the eligible universities will not be accepted"),
    "ttps_esclusi": ("ttps_pagina", True, "The TTPS does not apply to nationals of Afghanistan, Cuba and Korea (Democratic People's Republic of)."),
    "ttps_tempi": ("ttps_pagina", 4, "It normally takes four weeks to process visa/entry permit applications under the TTPS"),
    "ttps_lista_lwb": ("ttps_pagina", True, "which is compiled by the Labour and Welfare Bureau"),
    "ttps_classifiche": ("ttps_pagina", True, "the top 100 universities/institutions in four designated world university rankings"),
    "ttps_verifica": ("ttps_pagina", True, "Applicants are required to submit verification proof issued by a third-party credential verification organisation or the awarding institution"),
    # Hong Kong, tariffe dei "Specified Schemes"
    "ttps_tassa_domanda": ("ttps_tariffe", 600, "Principal applicant or Dependant Application fee Note 3 600"),
    "ttps_tassa_visto": ("ttps_tariffe", 1300, "of more than 180 days 1,300"),
    "ttps_tariffe_dal": ("ttps_tariffe", "2025-02-26", "With effect from 11 a.m. on 26 February 2025"),
    "ttps_tariffe_schema": ("ttps_tariffe", True, "Specified Scheme Top Talent Pass Scheme"),
    # Hong Kong, PDF della lista
    "ttps_nuove": ("ttps_pdf", True, "*denotes the universities newly added to the list."),
    "ttps_tolte": ("ttps_pdf", ["Ecole Polytechnique", "Université Grenoble Alpes", "Universite Sorbonne Paris Cite-USPC", "University of Freiburg"],
                   "Remarks: Ecole Polytechnique, Université Grenoble Alpes, Universite Sorbonne Paris Cite-USPC and University of Freiburg are removed from the list."),
    "ttps_tolte_dal": ("ttps_pdf", "2026-01-01", "From 1 January 2026, bachelor degree graduates from these four universities/institutions will no longer be eligible for applications under Categories B and C of the TTPS."),
    # Giappone, pagina J-Find (giapponese) e PDF
    "jf_durata": ("jf_pagina", 2, "最長２年間の在留が可能となります"),
    "jf_classifiche": ("jf_pagina", True, "３つの世界大学ランキング（※１）中、２つ以上で１００位以内にランクインしている大学"),
    "jf_5anni": ("jf_pagina", 5, "を授与された日から５年以内の方"),
    "jf_fondi": ("jf_pagina", 200000, "申請人の預貯金の額が日本円に換算して２０万円以上あること"),
    "jf_lista_data": ("jf_pagina", "2026-10", "未来創造人材制度の対象となる大学一覧（PDF）（令和８年１０月時点）"),
    "jf_controllo": ("jf_pdf", True, "令和８年10月時点のランキングに基づき作成されているため、申請の際は、必ず最新の３つの世界大学ランキングも合わせて御確認ください。"),
    "jf_as_of": ("jf_pdf", "2026-10", "As of October 2026"),
    "jf_en_durata": ("jf_outline", 2, "Maximum period of stay is 2 years"),
    "jf_en_classifiche": ("jf_outline", True, "Graduated from a university ranked in the"),
    "jf_en_5anni": ("jf_outline", 5, "Within 5 years after graduation"),
    "jf_en_fondi": ("jf_outline", 200000, "Possession of 200,000 yen for living"),
    "jf_en_attivita": ("jf_outline", True, "Start-up preparation activities"),
}

# Paesi delle liste -> nome usato nelle pagine
PAESI = {"USA": "United States", "U.S.A.": "United States", "United States": "United States", "United States of America": "United States",
         "U.K.": "United Kingdom", "UK": "United Kingdom", "United Kingdom": "United Kingdom",
         "Chinese Mainland": "China", "China": "China", "Hong Kong SAR": "Hong Kong", "Hong Kong": "Hong Kong",
         "South Korea": "South Korea", "Korea": "South Korea"}

# Corrispondenze scritte a mano: chiave normalizzata -> identificativo comune (solo dove i nomi delle liste sono diversi)
ALIAS = {
    "ecole polytechnique federale de lausanne": "epfl", "epfl ecole polytechnique federale de lausanne": "epfl",
    "swiss federal institute of technology lausanne": "epfl",
    "eth zurich": "eth-zurich", "eth zurich swiss federal institute of technology": "eth-zurich", "swiss federal institute of technology zurich": "eth-zurich",
    "kaist korea advanced institute of science and technology": "kaist", "korea advanced institute of science and technology": "kaist",
    "lmu munchen": "lmu-munich", "lmu munich": "lmu-munich", "ludwig maximilians universitat munchen": "lmu-munich", "university of munich": "lmu-munich",
    "nanyang technological university": "nanyang-technological-university", "nanyang technological university singapore": "nanyang-technological-university",
    "ohio state university": "ohio-state-university", "ohio state university columbus": "ohio-state-university",
    "paris saclay university": "universite-paris-saclay", "universite paris saclay": "universite-paris-saclay",
    "paris sciences et lettres psl university": "psl-university", "psl research university paris": "psl-university", "psl university": "psl-university",
    "universite psl": "psl-university",
    "universitat heidelberg": "heidelberg-university", "heidelberg university": "heidelberg-university",
    "university of california los angles": "university-of-california-los-angeles", "university of california los angeles": "university-of-california-los-angeles",
    "university of minnesota": "university-of-minnesota", "university of minnesota twin cities": "university-of-minnesota",
    "university of north carolina chapel hill": "university-of-north-carolina-at-chapel-hill",
    "university of north carolina at chapel hill": "university-of-north-carolina-at-chapel-hill",
    "university of science and technology china": "university-of-science-and-technology-of-china",
    "university of science and technology of china": "university-of-science-and-technology-of-china",
}
# Nome nelle pagine per gli identificativi uniti a mano (gli altri prendono il nome più recente delle liste, senza "The")
NOMI = {
    "epfl": "EPFL (École Polytechnique Fédérale de Lausanne)", "eth-zurich": "ETH Zurich", "kaist": "KAIST (Korea Advanced Institute of Science and Technology)",
    "lmu-munich": "LMU Munich (Ludwig-Maximilians-Universität München)", "nanyang-technological-university": "Nanyang Technological University, Singapore",
    "ohio-state-university": "Ohio State University", "universite-paris-saclay": "Université Paris-Saclay", "psl-university": "PSL University (Université PSL)",
    "heidelberg-university": "Heidelberg University", "university-of-california-los-angeles": "University of California, Los Angeles (UCLA)",
    "university-of-minnesota": "University of Minnesota", "university-of-north-carolina-at-chapel-hill": "University of North Carolina at Chapel Hill",
    "university-of-science-and-technology-of-china": "University of Science and Technology of China",
}
QUERY = ["in|hpi visa university list", "ng|hpi visa university list", "us|hpi visa university list", "gb|hpi visa university list",
         "in|hpi visa", "ng|hpi visa", "gb|hpi visa", "us|hpi visa", "in|high potential individual visa university list",
         "in|hpi visa 2026", "gb|hpi visa list 2026", "in|hpi visa for indian", "in|hpi visa eligible universities",
         "in|top talent pass scheme university list", "us|top talent pass scheme university list", "in|top talent pass scheme", "us|top talent pass scheme",
         "in|ttps hong kong", "in|ttps hong kong university list",
         "in|j-find visa university list", "us|j-find visa university list", "in|j-find visa", "us|j-find visa", "ng|j-find visa", "gb|j-find visa",
         "in|j find visa"]


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def inglese(n):
    """Nome inglese della riga (la lista di Hong Kong aggiunge il nome cinese dopo ' / '), senza l'asterisco delle nuove."""
    return re.sub(r"\s+", " ", n.split(" / ")[0].rstrip("*").strip())


def chiave(n):
    s = unicodedata.normalize("NFKD", inglese(n))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"\(.*?\)", "", s).replace("&", " and ").replace("’", "'")
    s = re.sub(r"[-–,./']", " ", s)
    s = re.sub(r"\bthe\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def id_uni(n):
    k = chiave(n)
    return ALIAS.get(k) or slug(k)


def paese(p):
    p = re.sub(r"\s+", " ", p.split(" / ")[0]).strip()
    return PAESI.get(p, p)


def salva(nome, b):
    CART.mkdir(parents=True, exist_ok=True)
    (CART / nome).write_bytes(b)


def fonte(url, st, b, titolo, testo, oggi, **extra):
    return {"url": url, "http": st, "byte": len(b), "sha256_file": hashlib.sha256(b).hexdigest(), "sha256_testo": hashlib.sha256(testo.encode()).hexdigest(),
            "titolo": titolo, "letto_il": oggi, **extra}


def pdf_testo(b, layout=False):
    p = subprocess.run(["pdftotext"] + (["-layout"] if layout else []) + ["-", "-"], input=b, capture_output=True)
    return p.stdout.decode("utf-8", "replace")


def pdf_info(b):
    p = subprocess.run(["pdfinfo", "-"], input=b, capture_output=True)
    t = p.stdout.decode("utf-8", "replace")
    m = re.search(r"ModDate:\s+(.*)", t)
    return m.group(1).strip() if m else None


def leggi_hpi(body):
    """Righe (università, Paese) della tabella e frase del periodo dei titoli."""
    righe = re.findall(r"<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>", body, re.S)
    righe = [(testo_html(a), testo_html(c)) for a, c in righe]
    frase = testo_html(re.search(r"<p>(.*?)</p>", body, re.S).group(1))
    m = re.search(r"between (\d{1,2} \w+ \d{4}) (?:and|to) (\d{1,2} \w+ \d{4})", frase)
    return righe, frase, m


def data_iso(t):
    from datetime import datetime
    return datetime.strptime(t, "%d %B %Y").date().isoformat()


def leggi_ttps(b):
    t = pdf_testo(b, layout=True)
    righe = []
    candidati = 0
    for r in t.split("\n"):
        if re.search(r"\S\s{2,}\S", r) and re.search(r"[一-鿿]+\s*$", r) and not re.search(r"Name of University|國家", r):
            candidati += 1
        m = re.match(r"^(\S.*?)\s{2,}([A-Z][A-Za-z .]+?)\s{2,}(\S+)\s*$", r)
        if m and not m.group(1).startswith(("Name of", "Aggregate")):
            righe.append((m.group(1).strip(), m.group(2).strip()))
    return righe, candidati, t


def leggi_jf(percorso):
    import pdfplumber
    righe = []
    with pdfplumber.open(percorso) as p:
        for pg in p.pages:
            for tb in pg.extract_tables():
                for r in tb:
                    if r[0] and r[0].startswith("Name of University"):
                        continue
                    righe.append((re.sub(r"\s*\n\s*", " ", r[0]).strip(), re.sub(r"\s*\n\s*", " ", r[2]).strip(), re.sub(r"\s*\n\s*", "", r[1] or "").strip()))
    return righe


def norm(t):
    return re.sub(r"\s+", " ", t.replace("\xa0", " ")).strip()


def main():
    oggi = date.today().isoformat()
    errori = []
    fonti, testi, liste = {}, {}, {}
    # 1. GOV.UK: raccolta, liste per anno, guida
    st, b, _ = get(API + HPI_RACCOLTA)
    if st == 200:
        salva("hpi-raccolta.json", b)
        d = json.loads(b)
        testi["hpi_raccolta"] = norm(testo_html(d["details"]["body"]) + " " + " ".join(c["note"] for c in d["details"]["change_history"]))
        anni_pub = sorted(int(x["title"][-4:]) for x in d["links"].get("children", []))
        if anni_pub != HPI_ANNI:
            errori.append(f"HPI: liste pubblicate {anni_pub}, attese {HPI_ANNI} (aggiornare HPI_ANNI e le pagine)")
        fonti["hpi_raccolta"] = fonte("https://www.gov.uk" + HPI_RACCOLTA, st, b, d["title"], testi["hpi_raccolta"], oggi,
                                      aggiornata=d["public_updated_at"][:10], licenza="Open Government Licence v3.0",
                                      storia=[{"data": c["public_timestamp"][:10], "nota": norm(c["note"])} for c in d["details"]["change_history"]])
    else:
        errori.append(f"HPI raccolta: HTTP {st}")
    for a in HPI_ANNI:
        p = f"{HPI_RACCOLTA}/high-potential-individual-visa-global-universities-list-{a}"
        st, b, _ = get(API + p)
        if st != 200:
            errori.append(f"HPI {a}: HTTP {st}")
            continue
        salva(f"hpi-{a}.json", b)
        d = json.loads(b)
        righe, frase, m = leggi_hpi(d["details"]["body"])
        n_tr = len(re.findall(r"<tr>", d["details"]["body"])) - 1   # meno l'intestazione
        if len(righe) != n_tr or not righe:
            errori.append(f"HPI {a}: {len(righe)} righe lette su {n_tr} della tabella")
        if not m:
            errori.append(f"HPI {a}: frase del periodo non riconosciuta: {frase!r}")
            continue
        dal, al = data_iso(m.group(1)), data_iso(m.group(2))
        if dal != f"{a}-11-01" or al != f"{a + 1}-10-31":
            errori.append(f"HPI {a}: periodo {dal}–{al} diverso da 1/11/{a}–31/10/{a + 1}")
        k = f"hpi-{a}"
        testi[k] = norm(testo_html(d["details"]["body"]))
        fonti[k] = fonte("https://www.gov.uk" + p, st, b, d["title"], testi[k], oggi, aggiornata=d["public_updated_at"][:10], licenza="Open Government Licence v3.0")
        liste[k] = {"visto": "hpi", "anno": a, "titolo": d["title"], "frase": frase, "dal": dal, "al": al, "fonte": k,
                    "voci": [{"nome": n, "paese_lista": c, "id": id_uni(n), "paese": paese(c)} for n, c in righe]}
    st, b, _ = get(API + HPI_GUIDA)
    if st == 200:
        salva("hpi-guida.json", b)
        d = json.loads(b)
        testi["hpi_guida"] = norm(" ".join(f'{x["title"]}. {testo_html(x["body"])}' for x in d["details"]["parts"]))
        fonti["hpi_guida"] = fonte("https://www.gov.uk" + HPI_GUIDA, st, b, d["title"], testi["hpi_guida"], oggi, aggiornata=d["public_updated_at"][:10],
                                   licenza="Open Government Licence v3.0", parti={x["slug"]: x["title"] for x in d["details"]["parts"]})
    else:
        errori.append(f"HPI guida: HTTP {st}")
    # 2. Hong Kong
    for k, u, tit in (("ttps_pagina", TTPS_PAGINA, "Top Talent Pass Scheme"), ("ttps_tariffe", TTPS_TARIFFE, "New Fee Structure for Visa Applications under Specified Schemes")):
        st, b, _ = get(u)
        if st != 200:
            errori.append(f"{k}: HTTP {st}")
            continue
        salva(k + ".html", b)
        testi[k] = norm(testo_html(b))
        fonti[k] = fonte(u, st, b, tit, testi[k], oggi)
    st, b, _ = get(TTPS_PDF)
    if st == 200:
        salva("aggregate_list.pdf", b)
        righe, candidati, t = leggi_ttps(b)
        testi["ttps_pdf"] = norm(t)
        if len(righe) != candidati:
            errori.append(f"TTPS: {len(righe)} righe lette su {candidati} righe con il Paese in cinese")
        fonti["ttps_pdf"] = fonte(TTPS_PDF, st, b, "Aggregate List of Eligible Universities", testi["ttps_pdf"], oggi, modificato=pdf_info(b))
        liste["ttps"] = {"visto": "ttps", "anno": 2026, "titolo": "Aggregate List of Eligible Universities", "dal": "2026-01-01", "fonte": "ttps_pdf",
                         "voci": [{"nome": inglese(n), "nome_lista": n, "nuova": n.rstrip().endswith("*"), "paese_lista": c, "id": id_uni(n), "paese": paese(c)}
                                  for n, c in righe]}
    else:
        errori.append(f"TTPS PDF: HTTP {st}")
    # 3. Giappone
    st, b, _ = get(JF_PAGINA)
    if st == 200:
        salva("jfind.html", b)
        testi["jf_pagina"] = norm(testo_html(b))
        fonti["jf_pagina"] = fonte(JF_PAGINA, st, b, "優秀な海外大学等を卒業した者が起業活動・就職活動を行う場合（J-Find）", testi["jf_pagina"], oggi)
        if "/isa/content/001394994.pdf" not in b.decode("utf-8", "replace"):
            errori.append("J-Find: la pagina non collega più 001394994.pdf (nuova lista?)")
    else:
        errori.append(f"J-Find pagina: HTTP {st}")
    st, b, _ = get(JF_PDF)
    if st == 200:
        salva("jfind.pdf", b)
        testi["jf_pdf"] = norm(pdf_testo(b))
        righe = leggi_jf(CART / "jfind.pdf")
        n_pag = len(re.findall(r"\d/ 4", pdf_testo(b, layout=True)))
        fonti["jf_pdf"] = fonte(JF_PDF, st, b, "A list of Universities eligible for J-Find (As of October 2026)", testi["jf_pdf"], oggi, modificato=pdf_info(b), pagine=n_pag)
        jp_righe = [r for r in pdf_testo(b, layout=True).split("\n") if re.search(r"大学|研究所|院", r) and not re.search(r"大学名|大学一覧|ランキング", r)]
        if len(righe) < 80 or any(not r[0] or not r[1] for r in righe):
            errori.append(f"J-Find: {len(righe)} righe lette, o righe vuote")
        liste["j-find"] = {"visto": "jfind", "anno": 2026, "titolo": "A list of Universities eligible for J-Find", "dal": "2026-10", "fonte": "jf_pdf",
                           "voci": [{"nome": n, "nome_ja": j, "paese_lista": c, "id": id_uni(n), "paese": paese(c)} for n, c, j in righe]}
        if len(jp_righe) < len(righe) - 5:
            errori.append(f"J-Find: {len(jp_righe)} righe con nome giapponese nel testo, {len(righe)} nella tabella")
    else:
        errori.append(f"J-Find PDF: HTTP {st}")
    st, b, _ = get(JF_OUTLINE)
    if st == 200:
        salva("jfind-outline.pdf", b)
        testi["jf_outline"] = norm(pdf_testo(b))
        fonti["jf_outline"] = fonte(JF_OUTLINE, st, b, "Outline J-Find (English)", testi["jf_outline"], oggi, modificato=pdf_info(b))
    else:
        errori.append(f"J-Find outline: HTTP {st}")
    # 4. frammenti
    letture = {}
    for k, (f, v, fr) in LETTURE.items():
        if fr not in testi.get(f, ""):
            errori.append(f"{k}: frammento non trovato in {f}: {fr[:90]!r}")
        letture[k] = {"valore": v, "fonte": f, "frammento": fr}
    # 5. università: identificativo comune, Paese coerente, nome nelle pagine
    uni = {}
    ordine = [f"hpi-{a}" for a in reversed(HPI_ANNI)] + ["j-find", "ttps"]   # il nome più recente dell'HPI, poi J-Find, poi TTPS
    for lk in ordine:
        for x in liste.get(lk, {}).get("voci", []):
            u = uni.setdefault(x["id"], {"nome": NOMI.get(x["id"]) or re.sub(r"(\w)\(", r"\1 (", re.sub(r"^The ", "", inglese(x["nome"]))), "paese": x["paese"], "liste": {}})
            if u["paese"] != x["paese"]:
                errori.append(f"{x['id']}: Paese {x['paese']} in {lk}, {u['paese']} altrove")
            if lk in u["liste"]:
                errori.append(f"{x['id']}: due righe in {lk}")
            u["liste"][lk] = x["nome"]
    usati = {a for a in ALIAS.values()}
    if usati - set(uni):
        errori.append(f"ALIAS senza università: {sorted(usati - set(uni))}")
    vecchio = json.loads(USCITA.read_text(encoding="utf-8")) if USCITA.exists() else {}
    dom = nuova_domanda(QUERY) if "--domanda" in sys.argv else vecchio.get("domanda")
    if not dom or any(k not in dom["query"] for k in QUERY):
        errori.append("domanda: autocompletamento mancante o incompleto (lanciare con --domanda)")
    if errori:
        print("ERRORI: il file dei dati NON è stato aggiornato")
        for x in errori[:80]:
            print(" -", x)
        sys.exit(1)
    contenuto = {"letture": letture, "fonti": fonti, "liste": liste, "universita": dict(sorted(uni.items()))}
    uscita = {"_nota": "Generato da raccolta/top_university.py: non modificare a mano. liste: righe delle liste ufficiali (nome e Paese come scritti, id comune); "
                       "universita: id -> nome nelle pagine, Paese, liste in cui compare (con il nome scritto in quella lista). GOV.UK: OGL v3.0.",
              "generato_il": oggi, "letto_il": oggi,
              "impronta": hashlib.sha256(json.dumps(contenuto, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20],
              "domanda": dom, **contenuto}
    USCITA.write_text(json.dumps(uscita, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(f"Scritto {USCITA}: " + ", ".join(f"{k} {len(v['voci'])}" for k, v in liste.items()) + f"; {len(uni)} università; impronta {uscita['impronta']}.")


if __name__ == "__main__":
    main()
