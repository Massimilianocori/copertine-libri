"""Scarica le fonti IRS dei limiti di contribuzione (401(k), IRA, Roth, SIMPLE, HSA) in inflation/dati/grezzi/irs/ e le registra in dati/fonti.json.

Uso (dalla radice del repository), ogni novembre dopo il comunicato IRS sui limiti dell'anno dopo (e a maggio-giugno dopo la Rev. Proc. HSA):
    python3 -I inflation/raccolta/irs.py            # scarica tutto, scrive il testo, ricontrolla ogni frase citata in dati/limiti.json

Solo pagine e PDF di irs.gov (più la sezione 223 dello U.S. Code su govinfo.gov) che rispondono 200 al nostro server; nessun blocco aggirato. Per ogni fonte: URL, data di lettura, HTTP,
SHA-256 del file scaricato, testo estratto (grezzi/irs/<id>.txt, quello su cui verifica.py cerca le frasi). I PDF piccoli (< 300 KB) si
tengono anche interi; quelli grandi (pubblicazioni, Internal Revenue Bulletin) solo come testo, con lo SHA-256 dell'originale.
Le cifre pubblicate stanno in dati/limiti.json, ognuna con la sua fonte e la frase IRS da cui viene (scritte a mano dopo la lettura).
"""
import hashlib
import html
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
CARTELLA = RADICE / "dati" / "grezzi" / "irs"
FONTI = RADICE / "dati" / "fonti.json"
LIMITI = RADICE / "dati" / "limiti.json"
UA = "Mozilla/5.0 (compatible; static-data-site-check/1.0)"
OGGI = date.today().isoformat()
IRS = "https://www.irs.gov"
LIC_IRS = {"nome": "Public domain (U.S. federal government work, 17 U.S.C. § 105)",
           "nota": "IRS publications, notices, revenue procedures and news releases are works of the U.S. federal government."}

# Comunicati annuali dei limiti (pagine del newsroom IRS; trovati negli archivi mensili "news-releases-for-<mese>-<anno>")
COMUNICATI = {
    2015: ("IR-2014-99", "/newsroom/irs-announces-2015-pension-plan-limitations-taxpayers-may-contribute-up-to-18000-to-their-401k-plans-in-2015"),
    2016: ("IR-2015-118", "/newsroom/irs-announces-2016-pension-plan-limitations-401k-contribution-limit-remains-unchanged-at-18000-for-2016"),
    2017: ("IR-2016-141", "/newsroom/irs-announces-2017-pension-plan-limitations-401k-contribution-limit-remains-unchanged-at-18000-for-2017"),
    2018: ("IR-2017-177", "/newsroom/irs-announces-2018-pension-plan-limitations-401k-contribution-limit-increases-to-18500-for-2018"),
    2019: ("IR-2018-211", "/newsroom/401k-contribution-limit-increases-to-19000-for-2019-ira-limit-increases-to-6000"),
    2020: ("IR-2019-179", "/newsroom/401k-contribution-limit-increases-to-19500-for-2020-catch-up-limit-rises-to-6500"),
    2021: ("IR-2020-244", "/newsroom/income-ranges-for-determining-ira-eligibility-change-for-2021"),
    2022: ("IR-2021-216", "/newsroom/irs-announces-401k-limit-increases-to-20500"),
    2023: ("IR-2022-188", "/newsroom/401k-limit-increases-to-22500-for-2023-ira-limit-rises-to-6500"),
    2024: ("IR-2023-203", "/newsroom/401k-limit-increases-to-23000-for-2024-ira-limit-rises-to-7000"),
    2025: ("IR-2024-285", "/newsroom/401k-limit-increases-to-23500-for-2025-ira-limit-remains-7000"),
    2026: ("IR-2025-111", "/newsroom/401k-limit-increases-to-24500-for-2026-ira-limit-increases-to-7500"),
    2027: ("IR-2026-136", "/newsroom/401k-limit-increases-to-25500-for-2027-ira-limit-remains-7500"),
}
# Avvisi tecnici con tutti i limiti dell'anno (Notice). Il 2015 (Notice 2014-70) non è più in /irs-drop/ (404): si legge nell'IRB 2014-48.
AVVISI = {2015: ("Notice 2014-70", "/pub/irs-irbs/irb14-48.pdf", "Internal Revenue Bulletin 2014-48 (Notice 2014-70)"),
          2016: ("Notice 2015-75", "/pub/irs-drop/n-15-75.pdf", None), 2017: ("Notice 2016-62", "/pub/irs-drop/n-16-62.pdf", None),
          2018: ("Notice 2017-64", "/pub/irs-drop/n-17-64.pdf", None), 2019: ("Notice 2018-83", "/pub/irs-drop/n-18-83.pdf", None),
          2020: ("Notice 2019-59", "/pub/irs-drop/n-19-59.pdf", None), 2021: ("Notice 2020-79", "/pub/irs-drop/n-20-79.pdf", None),
          2022: ("Notice 2021-61", "/pub/irs-drop/n-21-61.pdf", None), 2023: ("Notice 2022-55", "/pub/irs-drop/n-22-55.pdf", None),
          2024: ("Notice 2023-75", "/pub/irs-drop/n-23-75.pdf", None), 2025: ("Notice 2024-80", "/pub/irs-drop/n-24-80.pdf", None),
          2026: ("Notice 2025-67", "/pub/irs-drop/n-25-67.pdf", None), 2027: ("Notice 2026-66", "/pub/irs-drop/n-26-66.pdf", None)}
# Limiti HSA (Revenue Procedure annuale, sezione 223). Rev. Proc. 2019-25 (2020) non è in /irs-drop/ (404): si legge nell'IRB 2019-22.
# Per il 2018 la Rev. Proc. 2018-27 rimette il limite famiglia a $6,900 (la Rev. Proc. 2018-18 lo aveva ridotto a $6,850; /irs-drop/ 404).
HSA = {2015: ("Rev. Proc. 2014-30", "/pub/irs-drop/rp-14-30.pdf", None), 2016: ("Rev. Proc. 2015-30", "/pub/irs-drop/rp-15-30.pdf", None),
       2017: ("Rev. Proc. 2016-28", "/pub/irs-drop/rp-16-28.pdf", None), 2018: ("Rev. Proc. 2017-37", "/pub/irs-drop/rp-17-37.pdf", None),
       "2018b": ("Rev. Proc. 2018-27", "/pub/irs-drop/rp-18-27.pdf", None), 2019: ("Rev. Proc. 2018-30", "/pub/irs-drop/rp-18-30.pdf", None),
       2020: ("Rev. Proc. 2019-25", "/pub/irs-irbs/irb19-22.pdf", "Internal Revenue Bulletin 2019-22 (Rev. Proc. 2019-25)"),
       2021: ("Rev. Proc. 2020-32", "/pub/irs-drop/rp-20-32.pdf", None), 2022: ("Rev. Proc. 2021-25", "/pub/irs-drop/rp-21-25.pdf", None),
       2023: ("Rev. Proc. 2022-24", "/pub/irs-drop/rp-22-24.pdf", None), 2024: ("Rev. Proc. 2023-23", "/pub/irs-drop/rp-23-23.pdf", None),
       2025: ("Rev. Proc. 2024-25", "/pub/irs-drop/rp-24-25.pdf", None), 2026: ("Rev. Proc. 2025-19", "/pub/irs-drop/rp-25-19.pdf", None),
       2027: ("Rev. Proc. 2026-24", "/pub/irs-drop/rp-26-24.pdf", None)}
# Publication 969 (HSA, contributo aggiuntivo di $1,000 dai 55 anni) per anno d'imposta: edizioni in /irs-prior/
PUB969 = {y: (f"Publication 969 ({y})", f"/pub/irs-prior/p969--{y}.pdf") for y in range(2015, 2026)}
ALTRE = {
    "irs_p590a": ("Publication 590-A (2025), Contributions to Individual Retirement Arrangements (IRAs)", "/pub/irs-pdf/p590a.pdf"),
    "irs_cola_tabella": ("Cost-of-Living Adjustments for Retirement Items (prior years table)", "/pub/foia/ig/tege/cola-table-dci005ma4578824.pdf"),
    "irs_cola_pagina": ("COLA increases for dollar limitations on benefits and contributions", "/retirement-plans/cola-increases-for-dollar-limitations-on-benefits-and-contributions"),
    # pagine IRS da cui vengono le frasi di spiegazione della pagina 401(k) (somma dei differimenti tra piani, catch-up e limite 415(c), "if permitted by the plan")
    "irs_401k_limiti": ("Retirement topics: 401(k) and profit-sharing plan contribution limits",
                        "/retirement-plans/plan-participant-employee/retirement-topics-401k-and-profit-sharing-plan-contribution-limits"),
    "irs_piu_piani": ("How much salary can you defer if you're eligible for more than one retirement plan?",
                      "/retirement-plans/how-much-salary-can-you-defer-if-youre-eligible-for-more-than-one-retirement-plan"),
    "irs_catchup": ("Retirement topics: catch-up contributions", "/retirement-plans/plan-participant-employee/retirement-topics-catch-up-contributions"),
    # HSA dal 2026: piani bronze e catastrophic trattati come HDHP (legge del 4/7/2025)
    "irs_n_hsa_obbba": ("Notice 2026-5: expanded availability of health savings accounts under the One, Big, Beautiful Bill Act", "/pub/irs-drop/n-26-05.pdf"),
}
# Legge (non IRS): il contributo HSA aggiuntivo dai 55 anni è fissato dalla sezione 223(b)(3)(B) («2009 and thereafter $1,000») e la sezione 223(g)
# indicizza solo (b)(2) e (c)(2)(A): vale per ogni anno anche prima che esca la Publication 969. Testo: U.S. Code, edizione 2024, su govinfo.gov (GPO).
LEGGE = {
    "usc_223": ("26 U.S.C. § 223 (U.S. Code, 2024 edition)", "Internal Revenue Code, section 223: Health savings accounts",
                "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/html/USCODE-2024-title26-subtitleA-chap1-subchapB-partVII-sec223.htm"),
}
LIC_LEGGE = {"nome": "Public domain (U.S. federal government work, 17 U.S.C. § 105)",
             "nota": "The United States Code is a work of the U.S. federal government, published by the Government Publishing Office."}
NON_LETTE = {
    "irs_n_2014_70": {"url": IRS + "/pub/irs-drop/n-14-70.pdf", "motivo": "HTTP 404; the same notice is read in Internal Revenue Bulletin 2014-48"},
    "irs_rp_2019_25": {"url": IRS + "/pub/irs-drop/rp-19-25.pdf", "motivo": "HTTP 404; the same revenue procedure is read in Internal Revenue Bulletin 2019-22"},
    "irs_rp_2018_18": {"url": IRS + "/pub/irs-drop/rp-18-18.pdf", "motivo": "HTTP 404; Rev. Proc. 2018-27 (read) restores the 2018 family HSA limit and cites it"},
}


def elenco():
    """[(id, chi, titolo, url, nome_breve)]"""
    out = []
    for y, (num, p) in COMUNICATI.items():
        out.append((f"irs_ir_{y}", f"IRS news release {num}", f"IRS news release {num}: retirement plan limits for {y}", IRS + p))
    for y, (num, p, tit) in AVVISI.items():
        out.append((f"irs_n_{y}", num, tit or f"{num}: cost-of-living adjustments for retirement items, {y}", IRS + p))
    for y, (num, p, tit) in HSA.items():
        out.append((f"irs_rp_{y}", num, tit or f"{num}: HSA inflation adjusted amounts for {str(y)[:4]}", IRS + p))
    for y, (num, p) in PUB969.items():
        out.append((f"irs_p969_{y}", num, f"{num}, Health Savings Accounts and Other Tax-Favored Health Plans", IRS + p))
    for k, (tit, p) in ALTRE.items():
        out.append((k, "Internal Revenue Service", tit, IRS + p))
    for k, (chi, tit, url) in LEGGE.items():
        out.append((k, chi, tit, url))
    return out


def scarica(url):
    p = subprocess.run(["curl", "-s", "-L", "--max-time", "120", "-A", UA, "-w", "\n%{http_code}", url], capture_output=True)
    corpo, _, codice = p.stdout.rpartition(b"\n")
    return int(codice or 0), corpo


def normalizza(t):
    """Testo su cui si cercano le frasi: spazi unici, virgolette e trattini semplici, niente trattino di sillabazione a fine riga."""
    t = t.replace("­", "").replace("‑", "-").replace("‐", "-").replace(" ", " ").replace(" ", " ")
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    t = re.sub(r"[\x00-\x08\x0b\x0e-\x1f\x7f]", "", t)  # caratteri di controllo dei PDF (es. \x08 nell'IRB 2019-22)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def testo(b):
    if b.startswith(b"%PDF"):
        p = subprocess.run(["pdftotext", "-enc", "UTF-8", "-", "-"], input=b, capture_output=True)
        return normalizza(p.stdout.decode("utf-8", "replace"))
    t = b.decode("utf-8", "replace")
    t = re.sub(r"<(script|style|noscript)\b.*?</\1>", " ", t, flags=re.S | re.I)
    m = re.search(r"<main\b.*?</main>", t, re.S | re.I)  # solo il contenuto della pagina, senza i menu
    t = m.group(0) if m else t
    t = re.sub(r"<li\b[^>]*>", " • ", t)  # voci di elenco come nei PDF («• »): una frase citata con un elenco resta leggibile
    return normalizza(html.unescape(re.sub(r"<[^>]+>", " ", t)))


def main():
    CARTELLA.mkdir(parents=True, exist_ok=True)
    fonti = json.loads(FONTI.read_text(encoding="utf-8"))
    errori = []
    for fid, chi, titolo, url in elenco():
        http, b = scarica(url)
        if http != 200 or len(b) < 1000:
            errori.append(f"{fid}: HTTP {http} ({url})")
            continue
        t = testo(b)
        (CARTELLA / f"{fid}.txt").write_text(t + "\n", encoding="utf-8")
        tiene = b.startswith(b"%PDF") and len(b) < 300_000
        if tiene:
            (CARTELLA / f"{fid}.pdf").write_bytes(b)
        fonti[fid] = {"chi": chi, "titolo": titolo, "url": url, "http": http, "letto_il": OGGI, "sha256": hashlib.sha256(b).hexdigest(),
                      "byte": len(b), "testo": f"grezzi/irs/{fid}.txt", "originale": f"grezzi/irs/{fid}.pdf" if tiene else None, "licenza": LIC_LEGGE if fid in LEGGE else LIC_IRS}
        print(f"{fid}: {http}, {len(b)} byte, testo {len(t)} caratteri")
    fonti["_non_lette"].update({k: dict(v, provato_il=OGGI) for k, v in NON_LETTE.items()})
    # frasi citate in dati/limiti.json: ancora presenti nel testo appena scaricato?
    if LIMITI.exists():
        lim = json.loads(LIMITI.read_text(encoding="utf-8"))
        cerca = {}
        for anno in lim["anni"].values():
            for v in anno.values():
                cerca.setdefault(v["fonte"], []).append(v["frase"])
        for x in lim.get("testi", {}).values():
            cerca.setdefault(x["fonte"], []).append(x["frase"])
        for fid, frasi in cerca.items():
            p = CARTELLA / f"{fid}.txt"
            t = p.read_text(encoding="utf-8") if p.exists() else ""
            fonti.setdefault(fid, {})["trovate"] = {f: (normalizza(f) in t) for f in dict.fromkeys(frasi)}
            mancano = [f for f, ok in fonti[fid]["trovate"].items() if not ok]
            if mancano:
                errori.append(f"{fid}: {len(mancano)} frasi non più nel testo, es. «{mancano[0][:80]}»")
    FONTI.write_text(json.dumps(fonti, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Scritto {FONTI}")
    if errori:
        raise SystemExit("ERRORI:\n" + "\n".join(errori))


if __name__ == "__main__":
    main()
