"""Scarica il file completo del College Scorecard (U.S. Department of Education) e il suo dizionario dei dati, ne registra
indirizzo, data, stato HTTP e impronta, e ne ricava l'estratto usato dalle schede delle università.

Uso (dalla radice del repository):
    python3 collegeaid/raccolta/scorecard.py            # scarica (curl con un nome di robot dichiarato; file pubblico, senza chiave)
    python3 collegeaid/raccolta/scorecard.py --locale   # non scarica: rilegge lo zip già in cache/scorecard/ e il dizionario in dati/grezzi/

Che cosa scrive:
- cache/scorecard/<nome>.zip          lo zip ufficiale (24 MB: NON va nel repository; ne restano indirizzo, data e sha256);
- dati/grezzi/scorecard_estratto.csv  tutte le righe del file (un istituto per riga) con le sole colonne di COLONNE, celle copiate
                                      carattere per carattere («NA» = dato assente, «PS» = soppresso per riservatezza);
- dati/grezzi/scorecard_data_dictionary.xlsx  il dizionario ufficiale: il foglio «Most_Recent_Inst_Cohort_Map» dice a quale anno
                                      si riferisce ogni colonna del file «most recent» (nel CSV l'anno non c'è);
- dati/fonti_scorecard.json           indirizzi, date, HTTP, sha256, numero di righe e colonne, anno di ogni colonna, etichette dei codici.

Nessuna cifra viene corretta, arrotondata o completata. Se una colonna manca, o il dizionario non ha l'anno di una colonna,
lo script si ferma e non scrive niente.
"""
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

QUI = Path(__file__).resolve().parent
RADICE = QUI.parent
DATI = RADICE / "dati"
GREZZI = DATI / "grezzi"
CACHE = RADICE / "cache" / "scorecard"
UA = "Mozilla/5.0 (X11; Linux x86_64) research-bot"

URL_ZIP = "https://ed-public-download.scorecard.network/downloads/Most-Recent-Cohorts-Institution_11022026.zip"
URL_DIZ = "https://collegescorecard.ed.gov/files/CollegeScorecardDataDictionary.xlsx"
CSV_NELLO_ZIP = "Most-Recent-Cohorts-Institution.csv"
ESTRATTO = GREZZI / "scorecard_estratto.csv"
DIZIONARIO = GREZZI / "scorecard_data_dictionary.xlsx"

FASCE = ["1", "2", "3", "4", "5"]
COLONNE = (["UNITID", "OPEID6", "INSTNM", "CITY", "STABBR", "ALIAS", "INSTURL", "NPCURL", "MAIN", "CURROPER", "CONTROL", "PREDDEG", "HIGHDEG", "ICLEVEL", "DISTANCEONLY",
            "UGDS", "ADM_RATE", "TUITIONFEE_IN", "TUITIONFEE_OUT", "COSTT4_A", "NPT4_PUB", "NPT4_PRIV"]
           + [f"NPT4{i}_PUB" for i in FASCE] + [f"NPT4{i}_PRIV" for i in FASCE] + ["C150_4", "GRAD_DEBT_MDN", "PLUS_DEBT_INST_MD"])
# colonne con una cifra mostrata in pagina: per ognuna serve l'anno scritto nel dizionario
CON_ANNO = [c for c in COLONNE if c not in ("UNITID", "OPEID6", "CITY", "STABBR", "ALIAS", "INSTURL", "MAIN", "CURROPER", "CONTROL", "PREDDEG", "HIGHDEG", "ICLEVEL", "DISTANCEONLY")]
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main", "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def scarica(url, dest):
    r = subprocess.run(["curl", "-sS", "-L", "-A", UA, "--max-time", "600", "-o", str(dest), "-w", "%{http_code}", url], capture_output=True, text=True)
    try:
        return int(r.stdout.strip()[-3:])
    except ValueError:
        return 0


def fogli_xlsx(percorso):
    """Lettura minima di un .xlsx con la sola libreria standard: {nome del foglio: righe di celle come testo}."""
    z = zipfile.ZipFile(percorso)
    condivise = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            condivise.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    rel = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    fogli = {}
    for s in ET.fromstring(z.read("xl/workbook.xml")).find("m:sheets", NS):
        bersaglio = rel[s.get("{%s}id" % NS["r"])].lstrip("/")
        bersaglio = bersaglio if bersaglio.startswith("xl/") else "xl/" + bersaglio
        righe = []
        for riga in ET.fromstring(z.read(bersaglio)).iter("{%s}row" % NS["m"]):
            celle = {}
            for c in riga.findall("m:c", NS):
                n = 0
                for ch in re.match(r"[A-Z]+", c.get("r")).group(0):
                    n = n * 26 + ord(ch) - 64
                v, t = c.find("m:v", NS), c.get("t")
                if t == "s" and v is not None:
                    val = condivise[int(v.text)]
                elif t == "inlineStr":
                    val = "".join(x.text or "" for x in c.iter("{%s}t" % NS["m"]))
                else:
                    val = v.text if v is not None and v.text else ""
                celle[n - 1] = val.strip()
            righe.append([celle.get(i, "") for i in range(max(celle) + 1)] if celle else [])
        fogli[s.get("name")] = righe
    return fogli


def leggi_dizionario(percorso):
    fogli = fogli_xlsx(percorso)
    for nome in ("README", "Institution_Data_Dictionary", "Most_Recent_Inst_Cohort_Map"):
        if nome not in fogli:
            raise SystemExit(f"dizionario: manca il foglio {nome}: la fonte ha cambiato forma")
    rilascio = next((c for r in fogli["README"] for c in r if c.startswith("Released ")), None)
    if not rilascio:
        raise SystemExit("dizionario: non trovo la riga «Released ...» nel foglio README")
    mappa = fogli["Most_Recent_Inst_Cohort_Map"]
    if mappa[0][:2] != ["variable", 'Cohort/Measure in "Most Recent" Datafile']:
        raise SystemExit(f"dizionario: intestazione inattesa della mappa degli anni: {mappa[0][:3]}")
    anni = {r[0]: r[1] for r in mappa[1:] if len(r) > 1 and r[0]}
    mancano = [c for c in CON_ANNO if not anni.get(c) or anni[c] == "NA"]
    if mancano:
        raise SystemExit(f"dizionario: nessun anno per {mancano}")
    diz = fogli["Institution_Data_Dictionary"]
    i_var, i_val, i_lab, i_nome, i_fonte = (diz[0].index(x) for x in ("VARIABLE NAME", "VALUE", "LABEL", "NAME OF DATA ELEMENT", "SOURCE"))
    etichette, nomi, origine, corrente = {"CONTROL": {}, "PREDDEG": {}}, {}, {}, None
    for r in diz[1:]:
        r = r + [""] * (len(diz[0]) - len(r))
        if r[i_var]:
            corrente = r[i_var]
            nomi[corrente], origine[corrente] = r[i_nome].split("\n")[0].strip(), r[i_fonte]
        if corrente in etichette and r[i_val] != "":
            etichette[corrente][r[i_val]] = r[i_lab]
    if etichette["CONTROL"] != {"1": "Public", "2": "Private nonprofit", "3": "Private for-profit"} or etichette["PREDDEG"].get("3") != "Predominantly bachelor's-degree granting":
        raise SystemExit(f"dizionario: codici di CONTROL o PREDDEG diversi dal previsto: {etichette}")
    return {"rilascio": rilascio.replace("Released ", ""), "anni": {c: anni[c] for c in CON_ANNO}, "nomi": {c: nomi[c] for c in CON_ANNO},
            "origine": {c: origine[c] for c in CON_ANNO}, "etichette": etichette}


def main():
    locale = "--locale" in sys.argv
    CACHE.mkdir(parents=True, exist_ok=True)
    GREZZI.mkdir(parents=True, exist_ok=True)
    zip_dest = CACHE / URL_ZIP.rsplit("/", 1)[1]
    vecchie = json.loads((DATI / "fonti_scorecard.json").read_text(encoding="utf-8"))["fonti"] if (DATI / "fonti_scorecard.json").exists() else {}
    oggi = date.today().isoformat()
    stato = {}
    for fid, url, dest in (("scorecard", URL_ZIP, zip_dest), ("scorecard_diz", URL_DIZ, DIZIONARIO)):
        if locale:
            if not dest.exists() or fid not in vecchie:
                raise SystemExit(f"--locale: manca {dest} o la sua registrazione: lanciare senza --locale")
            stato[fid] = (vecchie[fid]["http"], vecchie[fid]["letto_il"])
            continue
        tmp = dest.with_suffix(dest.suffix + ".nuovo")
        http = scarica(url, tmp)
        if http != 200 or not zipfile.is_zipfile(tmp):
            tmp.unlink(missing_ok=True)
            raise SystemExit(f"{fid}: HTTP {http} o file non valido da {url}: niente è stato cambiato")
        tmp.replace(dest)
        stato[fid] = (http, oggi)

    # ---- zip: il CSV dentro, riga per riga, senza toccare le celle
    grezzo_zip = zip_dest.read_bytes()
    z = zipfile.ZipFile(io.BytesIO(grezzo_zip))
    if CSV_NELLO_ZIP not in z.namelist():
        raise SystemExit(f"zip: manca {CSV_NELLO_ZIP} (contenuto: {z.namelist()})")
    grezzo_csv = z.read(CSV_NELLO_ZIP)
    righe = list(csv.reader(io.StringIO(grezzo_csv.decode("utf-8-sig"), newline="")))
    testa, corpo = righe[0], righe[1:]
    mancano = [c for c in COLONNE if c not in testa]
    if mancano:
        raise SystemExit(f"file Scorecard: mancano le colonne {mancano}")
    idx = [testa.index(c) for c in COLONNE]
    if len({r[idx[0]] for r in corpo}) != len(corpo) or any(len(r) != len(testa) for r in corpo):
        raise SystemExit("file Scorecard: UNITID ripetuti o righe di lunghezza diversa")
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(COLONNE)
    for r in corpo:
        w.writerow([r[i] for i in idx])
    estratto = buf.getvalue().encode("utf-8")
    # valori ammessi nelle colonne numeriche: un numero, NA o PS (PrivacySuppressed)
    strani = {}
    for c in ("UGDS", "ADM_RATE", "TUITIONFEE_IN", "TUITIONFEE_OUT", "COSTT4_A", "NPT4_PUB", "NPT4_PRIV", "C150_4", "GRAD_DEBT_MDN", "PLUS_DEBT_INST_MD") + tuple(c for c in COLONNE if re.match(r"NPT4\d_", c)):
        i = testa.index(c)
        for r in corpo:
            if r[i] not in ("NA", "PS") and not re.fullmatch(r"-?\d+(\.\d+)?", r[i]):
                strani.setdefault(c, set()).add(r[i])
    if strani:
        raise SystemExit(f"file Scorecard: valori non previsti {strani}")

    diz = leggi_dizionario(DIZIONARIO)
    m = re.search(r"_(\d{2})(\d{2})(\d{4})\.zip$", URL_ZIP)
    fonti = {
        "scorecard": {"url": URL_ZIP, "file": f"cache/scorecard/{zip_dest.name}", "titolo": "College Scorecard, Most Recent Institution-Level Data (data file)",
                      "chi": "U.S. Department of Education, College Scorecard", "sha256": hashlib.sha256(grezzo_zip).hexdigest(), "byte": len(grezzo_zip),
                      "http": stato["scorecard"][0], "letto_il": stato["scorecard"][1], "aggiornato_il": f"{m[3]}-{m[1]}-{m[2]}",
                      "csv": CSV_NELLO_ZIP, "csv_sha256": hashlib.sha256(grezzo_csv).hexdigest(), "csv_byte": len(grezzo_csv), "istituti": len(corpo), "colonne": len(testa),
                      "estratto": "dati/grezzi/scorecard_estratto.csv", "estratto_sha256": hashlib.sha256(estratto).hexdigest(), "estratto_colonne": COLONNE,
                      "pagina": "https://collegescorecard.ed.gov/data/", "frasi": {}, "trovate": {}},
        "scorecard_diz": {"url": URL_DIZ, "file": "dati/grezzi/scorecard_data_dictionary.xlsx", "titolo": f"College Scorecard Data Dictionary (released {diz['rilascio']}), sheet “Most_Recent_Inst_Cohort_Map”",
                          "chi": "U.S. Department of Education, College Scorecard", "sha256": hashlib.sha256(DIZIONARIO.read_bytes()).hexdigest(), "byte": DIZIONARIO.stat().st_size,
                          "http": stato["scorecard_diz"][0], "letto_il": stato["scorecard_diz"][1], "pagina": "https://collegescorecard.ed.gov/data/data-documentation/", "frasi": {}, "trovate": {}},
    }
    ESTRATTO.write_bytes(estratto)
    for fid, f in fonti.items():
        v = vecchie.get(fid)
        if v and v["sha256"] != f["sha256"]:
            print(f"{fid}: file cambiato dall'ultima lettura (rileggere le cifre: rilanciare genera.py e verifica.py)")
    (DATI / "fonti_scorecard.json").write_text(json.dumps({
        "_nota": "Generato da raccolta/scorecard.py. Lo zip ufficiale (24 MB) resta in cache/ e non va nel repository: fanno fede indirizzo, data, HTTP e sha256. "
                 "dati/grezzi/scorecard_estratto.csv ha tutte le righe del file con le sole colonne usate, celle copiate carattere per carattere (NA = assente, PS = soppresso per riservatezza). "
                 "anni = foglio Most_Recent_Inst_Cohort_Map del dizionario ufficiale, testo copiato.",
        "fonti": fonti, "anni": diz["anni"], "nomi": diz["nomi"], "origine": diz["origine"], "etichette": diz["etichette"]}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Scorecard: HTTP {fonti['scorecard']['http']}, {len(grezzo_zip):,} byte, sha256 {fonti['scorecard']['sha256'][:16]}…, {len(corpo)} istituti, {len(testa)} colonne; "
          f"estratto di {len(COLONNE)} colonne ({len(estratto):,} byte). Dizionario: HTTP {fonti['scorecard_diz']['http']}, rilasciato {diz['rilascio']}.")


if __name__ == "__main__":
    main()
