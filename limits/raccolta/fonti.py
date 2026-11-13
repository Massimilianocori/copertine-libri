"""Scarica i testi di legge ufficiali usati da "Statute of Limitations by State" e ne registra l'impronta.

Uso (dalla radice del repository):
    python3 limits/raccolta/fonti.py            # scarica tutto in limits/raccolta/_grezzi/ (fuori da git) e scrive limits/dati/fonti.json
    python3 limits/raccolta/fonti.py tx_cprc16  # solo alcune fonti

Ogni fonte è una pagina (o un PDF / XML) del sito ufficiale del parlamento dello Stato, o dell'eCFR per la regola federale.
Il file grezzo resta in _grezzi/<id>.<estensione>; in dati/fonti.json vanno indirizzo, data di lettura, codice HTTP, byte e
impronta SHA-256. genera.py e verifica.py leggono SOLO i file salvati (nessuna rete durante la generazione).
Nessun blocco anti-robot viene aggirato: California e New York non sono nel sito perché i loro siti rispondono 403 ai programmi
(vedi NOTE.md). Le richieste non portano nulla di nostro (nessun dato personale), una ogni 0,7 secondi.
"""
import gzip
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
GREZZI = Path(__file__).resolve().parent / "_grezzi"
FILE = RADICE / "dati" / "fonti.json"
UA = "Mozilla/5.0 (compatible; statute-check/1.0)"

TX = "https://tcss.legis.texas.gov/resources/{}/htm/{}.htm"
FL = "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL={}.html"
OH = "https://codes.ohio.gov/ohio-revised-code/section-{}"
WA = "https://app.leg.wa.gov/RCW/default.aspx?cite={}"
VA = "https://law.lis.virginia.gov/vacode/{}/"
NC = "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_{}/GS_{}.html"
MI = "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-{}"
AZ = "https://www.azleg.gov/ars/12/{}.htm"
MA = "https://malegislature.gov/Laws/GeneralLaws/PartIII/{}"
MN = "https://www.revisor.mn.gov/statutes/cite/{}"

# id: (stato, indirizzo, titolo mostrato, chi pubblica)
FONTI = {
    # ---- Texas
    "tx_cprc16": ("TX", TX.format("CP", "CP.16"), "Civil Practice and Remedies Code, Chapter 16 (Limitations)", "Texas Legislature"),
    "tx_cprc74": ("TX", TX.format("CP", "CP.74"), "Civil Practice and Remedies Code, Chapter 74 (Medical Liability)", "Texas Legislature"),
    "tx_cprc101": ("TX", TX.format("CP", "CP.101"), "Civil Practice and Remedies Code, Chapter 101 (Tort Claims)", "Texas Legislature"),
    "tx_fin392": ("TX", TX.format("FI", "FI.392"), "Finance Code, Chapter 392 (Debt Collection)", "Texas Legislature"),
    "tx_gov81": ("TX", TX.format("GV", "GV.81"), "Government Code, Chapter 81 (State Bar)", "Texas Legislature"),
    # ---- Florida
    "fl_95_11": ("FL", FL.format("0000-0099/0095/Sections/0095.11"), "Florida Statutes § 95.11", "Florida Legislature"),
    "fl_95_051": ("FL", FL.format("0000-0099/0095/Sections/0095.051"), "Florida Statutes § 95.051", "Florida Legislature"),
    "fl_95_04": ("FL", FL.format("0000-0099/0095/Sections/0095.04"), "Florida Statutes § 95.04", "Florida Legislature"),
    "fl_768_28": ("FL", FL.format("0700-0799/0768/Sections/0768.28"), "Florida Statutes § 768.28", "Florida Legislature"),
    "fl_766_106": ("FL", FL.format("0700-0799/0766/Sections/0766.106"), "Florida Statutes § 766.106", "Florida Legislature"),
    "fl_law_2023_15": ("FL", "https://laws.flrules.org/2023/15", "Laws of Florida, chapter 2023-15 (HB 837)", "Florida Department of State"),
    # ---- Ohio
    "oh_2305_10": ("OH", OH.format("2305.10"), "Ohio Revised Code § 2305.10", "Ohio Legislative Service Commission"),
    "oh_2305_113": ("OH", OH.format("2305.113"), "Ohio Revised Code § 2305.113", "Ohio Legislative Service Commission"),
    "oh_2305_06": ("OH", OH.format("2305.06"), "Ohio Revised Code § 2305.06", "Ohio Legislative Service Commission"),
    "oh_2305_06_2012": ("OH", OH.format("2305.06/9-28-2012"), "Ohio Revised Code § 2305.06, version of September 28, 2012", "Ohio Legislative Service Commission"),
    "oh_2305_07": ("OH", OH.format("2305.07"), "Ohio Revised Code § 2305.07", "Ohio Legislative Service Commission"),
    "oh_2305_07_1993": ("OH", OH.format("2305.07/7-1-1993"), "Ohio Revised Code § 2305.07, version of July 1, 1993", "Ohio Legislative Service Commission"),
    "oh_2305_09": ("OH", OH.format("2305.09"), "Ohio Revised Code § 2305.09", "Ohio Legislative Service Commission"),
    "oh_2305_15": ("OH", OH.format("2305.15"), "Ohio Revised Code § 2305.15", "Ohio Legislative Service Commission"),
    "oh_2305_16": ("OH", OH.format("2305.16"), "Ohio Revised Code § 2305.16", "Ohio Legislative Service Commission"),
    "oh_2305_19": ("OH", OH.format("2305.19"), "Ohio Revised Code § 2305.19", "Ohio Legislative Service Commission"),
    "oh_2125_02": ("OH", OH.format("2125.02"), "Ohio Revised Code § 2125.02", "Ohio Legislative Service Commission"),
    "oh_sb13": ("OH", "https://search-prod.lis.state.oh.us/api/v2/general_assembly_134/legislation/sb13/05_EN/pdf/",
                "Senate Bill 13 as enrolled, 134th General Assembly (transition rule, sections 4 and 5)", "Ohio General Assembly"),
    "oh_2744_04": ("OH", OH.format("2744.04"), "Ohio Revised Code § 2744.04", "Ohio Legislative Service Commission"),
    # ---- Washington
    "wa_4_16": ("WA", WA.format("4.16") + "&full=true", "Revised Code of Washington, chapter 4.16 RCW", "Washington State Legislature"),
    "wa_bennett": ("WA", "https://www.courts.wa.gov/opinions/pdf/1013001.pdf",
                   "Bennett v. United States, No. 101300-1, opinion filed December 7, 2023", "Washington Supreme Court (Washington Courts)"),
    "wa_4_96_020": ("WA", WA.format("4.96.020"), "RCW 4.96.020", "Washington State Legislature"),
    # ---- Virginia
    "va_8_01_243": ("VA", VA.format("title8.01/chapter4/section8.01-243"), "Code of Virginia § 8.01-243", "Virginia General Assembly"),
    "va_8_01_243_1": ("VA", VA.format("title8.01/chapter4/section8.01-243.1"), "Code of Virginia § 8.01-243.1", "Virginia General Assembly"),
    "va_8_01_244": ("VA", VA.format("title8.01/chapter4/section8.01-244"), "Code of Virginia § 8.01-244", "Virginia General Assembly"),
    "va_8_01_246": ("VA", VA.format("title8.01/chapter4/section8.01-246"), "Code of Virginia § 8.01-246", "Virginia General Assembly"),
    "va_8_01_229": ("VA", VA.format("title8.01/chapter4/section8.01-229"), "Code of Virginia § 8.01-229", "Virginia General Assembly"),
    "va_8_01_230": ("VA", VA.format("title8.01/chapter4/section8.01-230"), "Code of Virginia § 8.01-230", "Virginia General Assembly"),
    "va_8_01_195_7": ("VA", VA.format("title8.01/chapter3.1/section8.01-195.7"), "Code of Virginia § 8.01-195.7", "Virginia General Assembly"),
    "va_15_2_209": ("VA", VA.format("title15.2/chapter2/section15.2-209"), "Code of Virginia § 15.2-209", "Virginia General Assembly"),
    # ---- North Carolina
    "nc_1_52": ("NC", NC.format("1", "1-52"), "N.C. General Statutes § 1-52", "North Carolina General Assembly"),
    "nc_1_53": ("NC", NC.format("1", "1-53"), "N.C. General Statutes § 1-53", "North Carolina General Assembly"),
    "nc_1_15": ("NC", NC.format("1", "1-15"), "N.C. General Statutes § 1-15", "North Carolina General Assembly"),
    "nc_1_17": ("NC", NC.format("1", "1-17"), "N.C. General Statutes § 1-17", "North Carolina General Assembly"),
    "nc_1_47": ("NC", NC.format("1", "1-47"), "N.C. General Statutes § 1-47", "North Carolina General Assembly"),
    "nc_1_26": ("NC", NC.format("1", "1-26"), "N.C. General Statutes § 1-26", "North Carolina General Assembly"),
    "nc_143_299": ("NC", NC.format("143", "143-299"), "N.C. General Statutes § 143-299", "North Carolina General Assembly"),
    # ---- Michigan
    "mi_5805": ("MI", MI.format("600-5805"), "Michigan Compiled Laws 600.5805", "Michigan Legislature"),
    "mi_5807": ("MI", MI.format("600-5807"), "Michigan Compiled Laws 600.5807", "Michigan Legislature"),
    "mi_5838a": ("MI", MI.format("600-5838a"), "Michigan Compiled Laws 600.5838a", "Michigan Legislature"),
    "mi_5851": ("MI", MI.format("600-5851"), "Michigan Compiled Laws 600.5851", "Michigan Legislature"),
    "mi_5852": ("MI", MI.format("600-5852"), "Michigan Compiled Laws 600.5852", "Michigan Legislature"),
    "mi_5853": ("MI", MI.format("600-5853"), "Michigan Compiled Laws 600.5853", "Michigan Legislature"),
    "mi_5855": ("MI", MI.format("600-5855"), "Michigan Compiled Laws 600.5855", "Michigan Legislature"),
    "mi_5856": ("MI", MI.format("600-5856"), "Michigan Compiled Laws 600.5856", "Michigan Legislature"),
    "mi_2912b": ("MI", MI.format("600-2912b"), "Michigan Compiled Laws 600.2912b", "Michigan Legislature"),
    "mi_6431": ("MI", MI.format("600-6431"), "Michigan Compiled Laws 600.6431", "Michigan Legislature"),
    # ---- Arizona
    "az_12_541": ("AZ", AZ.format("00541"), "Arizona Revised Statutes § 12-541", "Arizona State Legislature"),
    "az_12_542": ("AZ", AZ.format("00542"), "Arizona Revised Statutes § 12-542", "Arizona State Legislature"),
    "az_12_543": ("AZ", AZ.format("00543"), "Arizona Revised Statutes § 12-543", "Arizona State Legislature"),
    "az_12_544": ("AZ", AZ.format("00544"), "Arizona Revised Statutes § 12-544", "Arizona State Legislature"),
    "az_12_548": ("AZ", AZ.format("00548"), "Arizona Revised Statutes § 12-548", "Arizona State Legislature"),
    "az_12_501": ("AZ", AZ.format("00501"), "Arizona Revised Statutes § 12-501", "Arizona State Legislature"),
    "az_12_502": ("AZ", AZ.format("00502"), "Arizona Revised Statutes § 12-502", "Arizona State Legislature"),
    "az_12_504": ("AZ", AZ.format("00504"), "Arizona Revised Statutes § 12-504", "Arizona State Legislature"),
    "az_12_508": ("AZ", AZ.format("00508"), "Arizona Revised Statutes § 12-508", "Arizona State Legislature"),
    "az_12_821": ("AZ", AZ.format("00821"), "Arizona Revised Statutes § 12-821", "Arizona State Legislature"),
    "az_12_821_01": ("AZ", AZ.format("00821-01"), "Arizona Revised Statutes § 12-821.01", "Arizona State Legislature"),
    # ---- Massachusetts
    "ma_260_2": ("MA", MA.format("TitleV/Chapter260/Section2"), "General Laws, chapter 260, section 2", "Massachusetts Legislature"),
    "ma_260_2a": ("MA", MA.format("TitleV/Chapter260/Section2A"), "General Laws, chapter 260, section 2A", "Massachusetts Legislature"),
    "ma_260_4": ("MA", MA.format("TitleV/Chapter260/Section4"), "General Laws, chapter 260, section 4", "Massachusetts Legislature"),
    "ma_260_7": ("MA", MA.format("TitleV/Chapter260/Section7"), "General Laws, chapter 260, section 7", "Massachusetts Legislature"),
    "ma_260_9": ("MA", MA.format("TitleV/Chapter260/Section9"), "General Laws, chapter 260, section 9", "Massachusetts Legislature"),
    "ma_260_12": ("MA", MA.format("TitleV/Chapter260/Section12"), "General Laws, chapter 260, section 12", "Massachusetts Legislature"),
    "ma_260_13": ("MA", MA.format("TitleV/Chapter260/Section13"), "General Laws, chapter 260, section 13", "Massachusetts Legislature"),
    "ma_229_2": ("MA", MA.format("TitleII/Chapter229/Section2"), "General Laws, chapter 229, section 2", "Massachusetts Legislature"),
    "ma_258_4": ("MA", MA.format("TitleIV/Chapter258/Section4"), "General Laws, chapter 258, section 4", "Massachusetts Legislature"),
    # ---- Minnesota
    "mn_541_05": ("MN", MN.format("541.05"), "Minnesota Statutes § 541.05", "Minnesota Office of the Revisor of Statutes"),
    "mn_541_07": ("MN", MN.format("541.07"), "Minnesota Statutes § 541.07", "Minnesota Office of the Revisor of Statutes"),
    "mn_541_076": ("MN", MN.format("541.076"), "Minnesota Statutes § 541.076", "Minnesota Office of the Revisor of Statutes"),
    "mn_541_053": ("MN", MN.format("541.053"), "Minnesota Statutes § 541.053", "Minnesota Office of the Revisor of Statutes"),
    "mn_541_13": ("MN", MN.format("541.13"), "Minnesota Statutes § 541.13", "Minnesota Office of the Revisor of Statutes"),
    "mn_541_15": ("MN", MN.format("541.15"), "Minnesota Statutes § 541.15", "Minnesota Office of the Revisor of Statutes"),
    "mn_573_02": ("MN", MN.format("573.02"), "Minnesota Statutes § 573.02", "Minnesota Office of the Revisor of Statutes"),
    "mn_466_05": ("MN", MN.format("466.05"), "Minnesota Statutes § 466.05", "Minnesota Office of the Revisor of Statutes"),
    # ---- federale
    "cfr_1006_26": ("US", "https://www.ecfr.gov/api/versioner/v1/full/2026-11-01/title-12.xml?part=1006&section=1006.26",
                    "12 CFR 1006.26 (Regulation F): collection of time-barred debts", "eCFR, Office of the Federal Register"),
}
# indirizzo da mostrare ai lettori quando quello scaricato è un'API
LINK_LETTORE = {"cfr_1006_26": "https://www.ecfr.gov/current/title-12/chapter-X/part-1006/subpart-B/section-1006.26"}


def estensione(tipo, url):
    if "pdf" in tipo or url.rstrip("/").endswith(("/pdf", ".pdf")) or "laws.flrules.org" in url:
        return "pdf"
    if "xml" in tipo:
        return "xml"
    return "html"


def scarica(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            dati = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                dati = gzip.decompress(dati)
            return r.status, r.headers.get("Content-Type", ""), dati
    except urllib.error.HTTPError as e:
        return e.code, "", b""


def main(argv):
    GREZZI.mkdir(parents=True, exist_ok=True)
    vecchio = json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else {}
    scelte = argv or list(FONTI)
    oggi = date.today().isoformat()
    for fid in scelte:
        stato, url, titolo, chi = FONTI[fid]
        http, tipo, dati = scarica(url)
        voce = {"stato": stato, "url": url, "link": LINK_LETTORE.get(fid, url), "titolo": titolo, "chi": chi, "letto_il": oggi, "http": http}
        if http == 200 and dati:
            est = estensione(tipo, url)
            for f in GREZZI.glob(f"{fid}.*"):
                f.unlink()
            (GREZZI / f"{fid}.{est}").write_bytes(dati)
            voce.update({"file": f"{fid}.{est}", "byte": len(dati), "sha256": hashlib.sha256(dati).hexdigest()})
        else:
            print(f"ATTENZIONE {fid}: HTTP {http}")
            if fid in vecchio:
                voce = dict(vecchio[fid], ultimo_errore={"il": oggi, "http": http})
        vecchio[fid] = voce
        print(f"{fid:16} {http} {voce.get('byte', 0):>8} byte")
        time.sleep(0.7)
    ordinato = {k: vecchio[k] for k in FONTI if k in vecchio}
    FILE.write_text(json.dumps(ordinato, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(ordinato)} fonti -> {FILE}")


if __name__ == "__main__":
    main(sys.argv[1:])
