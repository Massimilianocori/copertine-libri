"""Scarica i file ufficiali del sito NAICS Code Lookup e ne registra indirizzo, HTTP, byte, SHA-256, data di lettura e frasi controllate.

Uso (dalla radice del repository):
    python3 -I naics/raccolta/fonti.py            # scarica solo i file che mancano in raccolta/_grezzi/
    python3 -I naics/raccolta/fonti.py --rete     # riscarica tutto (aggiornamento: impronta cambiata = file nuovo)

Fonti: U.S. Census Bureau (file NAICS 2022, tavole di concordanza 1997→2002→2007→2012→2017→2022, concordanza ufficiale
1987 SIC ↔ 1997 NAICS, manuale NAICS 2022 in PDF) e IRS (istruzioni dello Schedule C, codici di attività basati su NAICS).
Opere del governo federale USA: dominio pubblico. Le pagine HTML di census.gov rispondono 403 (Cloudflare) al nostro
server: non si aggirano, si leggono solo i file (rispondono 200). Pausa di 1 secondo tra le richieste. Nessun dato personale.
"""
import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
GREZZI = RADICE / "raccolta" / "_grezzi"
DATI = RADICE / "dati"
UA = "Mozilla/5.0 (compatible; naics-check/1.0)"
CB = "https://www.census.gov/naics/"

# Frasi del manuale NAICS 2022 (Office of Management and Budget) usate nei testi e nelle FAQ del sito.
FRASI_MANUALE = [
    "NAICS uses a six-digit coding system to identify industries and their placement in this hierarchical structure of the classification system.",
    "The first two digits of the code designate the sector, the third digit designates the subsector, the fourth digit designates the industry group, "
    "the fifth digit designates the NAICS industry, and the sixth digit designates the national industry.",
    "A zero as the sixth digit generally indicates that the NAICS industry and the U.S. industry are the same.",
    "NAICS classifies all economic activities into 20 sectors.",
    "With its inception in 1997, NAICS replaced the Standard Industrial Classification (1980) of Canada, the Mexican Classification of Activities "
    "and Products (1994), and the Standard Industrial Classification (1987) of the United States.",
    "The United States has adopted the revised classification in statistical programs for the reference year beginning in 2022.",
    "NAICS was revised in 2002, 2007, 2012, and 2017.",
    "This 2022 NAICS revision was undertaken to achieve one main goal—to modify or create industries to reflect new, emerging, or changing activities and technologies.",
    "To determine the correct NAICS code for your establishment, first identify the primary business activity.",
    "Next, read the full description of the industry (including the narrative, cross-references, and illustrative examples), and determine if that "
    "description fits the primary business activity of your establishment.",
    "There is no central government agency with the role of assigning, monitoring, or approving NAICS codes for establishments.",
    "Statistical agencies assign one NAICS code to each establishment based on its primary activity.",
    "the Social Security Administration assigns a NAICS code to new businesses based on information provided on their application for an Employer Identification Number.",
    "A business does not 'apply' for a NAICS code.",
    "Every five years NAICS is reviewed for potential revisions, so that the classification system can keep pace with the changing economy.",
    "The next scheduled review of NAICS will be for a potential 2027 revision.",
    "NAICS categories do not distinguish between small and large business",
    "The Small Business Administration (SBA) develops size standards for each NAICS category.",
    "The NAICS categories and definitions were not developed to meet the needs of procurement and/or regulatory applications.",
    "An establishment is classified in an industry when its primary activity meets the definition for that industry.",
    "the industry code is assigned based on the establishment's principal product or group of products produced or distributed, or services rendered.",
    "An establishment is generally a single, physical location at which economic activity occurs (e.g., store, factory, farm, etc.).",
    "NAICS ensures that such data are uniform and comparable among Canada, Mexico, and the United States.",
    "the NAICS treatment of electronic shopping in Retail Trade",
    "other federal agencies and other organizations have adopted NAICS for procurement and regulatory purposes even though it does not entirely fit their specific needs.",
]
FRASI_IRS = [
    "These codes for the Principal Business or Professional Activity classify sole proprietorships by the type of activity they are engaged in "
    "to facilitate the administration of the Internal Revenue Code.",
    "These six-digit codes are based on the NAICS.",
    "Now find the six-digit code assigned to this activity (for example, 531210, the code for offices of real estate agents and brokers) and enter it on Schedule C, line B.",
]

FILE = {
    "codici": {"url": CB + "2022NAICS/2-6%20digit_2022_Codes.xlsx", "nome": "2-6_digit_2022_Codes.xlsx",
               "titolo": "2022 NAICS 2–6 digit codes and titles (xlsx)"},
    "struttura": {"url": CB + "2022NAICS/2022_NAICS_Structure.xlsx", "nome": "2022_NAICS_Structure.xlsx",
                  "titolo": "2022 NAICS Structure, with change indicators (xlsx)"},
    "descrizioni": {"url": CB + "2022NAICS/2022_NAICS_Descriptions.xlsx", "nome": "2022_NAICS_Descriptions.xlsx",
                    "titolo": "2022 NAICS Descriptions (xlsx)"},
    "indice": {"url": CB + "2022NAICS/2022_NAICS_Index_File.xlsx", "nome": "2022_NAICS_Index_File.xlsx",
               "titolo": "2022 NAICS Index File (xlsx)"},
    "rimandi": {"url": CB + "2022NAICS/2022_NAICS_Cross_References.xlsx", "nome": "2022_NAICS_Cross_References.xlsx",
                "titolo": "2022 NAICS Cross-References (xlsx)"},
    "conteggi": {"url": CB + "2022NAICS/2022_NAICS_Structure_Summary_Table.xlsx", "nome": "2022_NAICS_Structure_Summary_Table.xlsx",
                 "titolo": "2022 NAICS Structure Summary Table: counts by sector (xlsx)"},
    "c22_17": {"url": CB + "concordances/2022_to_2017_NAICS.xlsx", "nome": "2022_to_2017_NAICS.xlsx",
               "titolo": "2022 NAICS matched to 2017 NAICS, full concordance (xlsx)"},
    "c17_22": {"url": CB + "concordances/2017_to_2022_NAICS.xlsx", "nome": "2017_to_2022_NAICS.xlsx",
               "titolo": "2017 NAICS matched to 2022 NAICS, full concordance (xlsx)"},
    "c12_17": {"url": CB + "concordances/2012_to_2017_NAICS.xlsx", "nome": "2012_to_2017_NAICS.xlsx",
               "titolo": "2012 NAICS matched to 2017 NAICS, full concordance (xlsx)"},
    "c07_12": {"url": CB + "concordances/2007_to_2012_NAICS.xls", "nome": "2007_to_2012_NAICS.xls",
               "titolo": "2007 NAICS matched to 2012 NAICS, full concordance (xls)"},
    "c02_07": {"url": CB + "concordances/2002_to_2007_NAICS.xls", "nome": "2002_to_2007_NAICS.xls",
               "titolo": "2002 NAICS matched to 2007 NAICS, full concordance (xls)"},
    "c97_02": {"url": CB + "concordances/1997_NAICS_to_2002_NAICS.xls", "nome": "1997_NAICS_to_2002_NAICS.xls",
               "titolo": "1997 NAICS matched to 2002 NAICS (xls)"},
    "naics97_sic": {"url": CB + "concordances/1997_NAICS_to_1987_SIC.xls", "nome": "1997_NAICS_to_1987_SIC.xls",
                    "titolo": "1997 NAICS matched to 1987 SIC (xls)"},
    "sic_naics97": {"url": CB + "concordances/1987_SIC_to_1997_NAICS.xls", "nome": "1987_SIC_to_1997_NAICS.xls",
                    "titolo": "1987 SIC matched to 1997 NAICS (xls)"},
    "manuale": {"url": CB + "reference_files_tools/2022_NAICS_Manual.pdf", "nome": "2022_NAICS_Manual.pdf",
                "titolo": "North American Industry Classification System, United States, 2022 (manual, PDF)", "chi": "Office of Management and Budget",
                "cerca": FRASI_MANUALE},
    "irs_sc": {"url": "https://www.irs.gov/pub/irs-pdf/i1040sc.pdf", "nome": "i1040sc.pdf",
               "titolo": "2025 Instructions for Schedule C (Form 1040), Principal Business or Professional Activity Codes (PDF)",
               "chi": "Internal Revenue Service", "cerca": FRASI_IRS},
}


def norm(t):
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("''", '"')
    return re.sub(r"\s+", " ", t).strip()


def testo_pdf(p):
    return norm(subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True, check=True).stdout)


def apri(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.status, r.read()


def main():
    rete = "--rete" in sys.argv
    GREZZI.mkdir(parents=True, exist_ok=True)
    oggi = date.today().isoformat()
    vecchio = json.loads((DATI / "fonti.json").read_text(encoding="utf-8")) if (DATI / "fonti.json").exists() else {"file": {}}
    out = {"_nota": "Scritto da raccolta/fonti.py. I file grezzi stanno in raccolta/_grezzi/ (fuori da git): verifica.py ne ricalcola l'impronta.",
           "licenza": "Works of the U.S. federal government (Census Bureau, OMB, IRS): public domain in the United States (17 U.S.C. 105).",
           "file": {}}
    for fid, f in FILE.items():
        dest = GREZZI / f["nome"]
        prima = vecchio["file"].get(fid, {})
        if rete or not dest.exists():
            st, b = apri(f["url"])
            dest.write_bytes(b)
            letto = oggi
            time.sleep(1)
        else:
            st, b, letto = prima.get("http", 200), dest.read_bytes(), prima.get("letto_il", oggi)
        rec = {"url": f["url"], "titolo": f["titolo"], "chi": f.get("chi", "U.S. Census Bureau"), "file": f["nome"], "http": st,
               "byte": len(b), "sha256": hashlib.sha256(b).hexdigest(), "letto_il": letto}
        if f.get("cerca"):
            t = testo_pdf(dest)
            rec["trovate"] = {c: norm(c) in t for c in f["cerca"]}
        out["file"][fid] = rec
        manca = [c[:50] for c, ok in rec.get("trovate", {}).items() if not ok]
        print(f"{fid}: HTTP {st}, {len(b)} byte, {rec['sha256'][:12]}" + (f", frasi mancanti: {manca or 'nessuna'}" if f.get("cerca") else ""))
    (DATI / "fonti.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
