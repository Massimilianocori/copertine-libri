"""Controllo ripetibile della pagina /reddito-minimo-cittadinanza/ di EsameB1 (redditi minimi per stranieri).

Uso (dalla radice del repository):
    python3 esameb1/raccolta/redditi.py           # controlla fonti, frasi e calcolatore; esce con 1 se qualcosa non va
    python3 esameb1/raccolta/redditi.py --salva   # in più, se è tutto a posto, porta 'verificato_il' a oggi in dati/redditi.json

Cosa controlla:
1. Ogni fonte di dati/redditi.json (Vademecum del Ministero, PDF della Prefettura, pagina della Prefettura di Milano,
   art. 9 del Testo unico su Normattiva) e le fonti dell'assegno sociale in dati/ricongiungimento.json rispondono 200.
2. Ogni frase in "citazioni" è ancora nel testo della fonte (HTML senza tag, PDF con pdftotext; spazi e virgolette
   tipografiche non contano). Le soglie scritte nel JSON (8.263,31 / 11.362,05 / 516,00 e la tabella 1-4 figli)
   compaiono tali e quali nel PDF della Prefettura; ogni caso della tabella è uguale alla formula.
3. Calcolatore: la funzione JS `calcolaRedditi` della pagina generata (sito/reddito-minimo-cittadinanza/index.html)
   dà gli stessi centesimi della funzione Python `calcola_redditi` di genera.py su tutte le combinazioni
   (coniuge sì/no, 0-8 figli, redditi intorno a ogni soglia). Serve node (se manca: AVVISO, controllo saltato).

Usa le funzioni di lettura di raccolta/esempi.py. Nessun dato personale.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
sys.path.insert(0, str(QUI.parent))
import esempi as E  # noqa: E402  (richiesta, controlla_file, testo_di, normalizza)

DATI = QUI.parent / "dati"
PAGINA = QUI.parent / "sito" / "reddito-minimo-cittadinanza" / "index.html"


def euro_it(x):
    s = f"{Decimal(x):,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def prova_calcolatore(errori, avvisi):
    import genera as G  # solo le funzioni: main() non parte all'import
    if not PAGINA.exists():
        avvisi.append("pagina non ancora generata: calcolatore non provato (lanciare python3 esameb1/genera.py)")
        return
    node = shutil.which("node")
    if not node:
        avvisi.append("node non trovato: calcolatore JS non provato")
        return
    testo = PAGINA.read_text(encoding="utf-8")
    inizio = testo.find("/*calcolo-inizio*/")
    fine = testo.find("/*calcolo-fine*/")
    if inizio < 0 or fine < 0:
        errori.append("calcolatore: funzione calcolaRedditi non trovata nella pagina")
        return
    js = testo[inizio:fine]
    casi = []
    for coniuge in (False, True):
        for figli in range(0, 9):
            base = G.calcola_redditi(coniuge, figli, 0)
            soglie = [base["cittadinanza"]["soglia"], base["carta_solo"]["soglia"], base["carta_famiglia"]["soglia"]]
            for s in soglie:
                for delta in (-100, -1, 0, 1, 100):
                    casi.append((coniuge, figli, s + delta))
            casi.append((coniuge, figli, 0))
    attesi = [G.calcola_redditi(c, f, r) for c, f, r in casi]
    with tempfile.TemporaryDirectory() as cartella:
        f = Path(cartella) / "prova.js"
        f.write_text(js + "\nconst casi = " + json.dumps(casi) + ";\n"
                     "console.log(JSON.stringify(casi.map(c => calcolaRedditi(c[0], c[1], c[2]))));\n", encoding="utf-8")
        r = subprocess.run([node, str(f)], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        errori.append(f"calcolatore: node si è fermato: {r.stderr[:300]}")
        return
    ottenuti = json.loads(r.stdout)
    diversi = [(casi[i], attesi[i], ottenuti[i]) for i in range(len(casi)) if attesi[i] != ottenuti[i]]
    for c, a, o in diversi[:5]:
        errori.append(f"calcolatore: caso {c}: Python {a} ≠ JS {o}")
    print(f"  calcolatore: {len(casi)} casi, {len(casi) - len(diversi)} uguali tra Python e JS")


def main(salva=False):
    R = json.loads((DATI / "redditi.json").read_text(encoding="utf-8"))
    ric = json.loads((DATI / "ricongiungimento.json").read_text(encoding="utf-8"))
    errori, avvisi = [], []
    fonti = {**R["cittadinanza"]["fonti"], **R["carta_soggiorno"]["fonti"]}
    link = {f["url"]: k for k, f in fonti.items()}
    link[ric["assegno_sociale"]["url"]] = "assegno sociale (circolare INPS)"
    link[ric["assegno_sociale"]["url_allegato"]] = "assegno sociale (allegato INPS)"
    for url, k in link.items():
        r = E.controlla_file(url)
        print(f"  {'ok ' if r['stato'] == 200 else 'NO '} {k}: {r['stato']}")
        if r["stato"] != 200:
            errori.append(f"{k}: stato {r['stato']} ({url})")
    c = R["cittadinanza"]
    with tempfile.TemporaryDirectory() as cartella:
        n = 0
        for cit in R["citazioni"]:
            f = fonti[cit["fonte"]]
            testo = E.testo_di(f["url"], cartella)
            if testo is None:
                errori.append(f"{cit['fonte']}: fonte non leggibile ({f['url']})")
            elif E.normalizza(cit["testo"]) not in testo:
                errori.append(f"{cit['fonte']}: frase non trovata: «{cit['testo']}»")
            else:
                n += 1
        print(f"  frasi citate: {n}/{len(R['citazioni'])} trovate nelle fonti")
        pdf = E.testo_di(c["fonti"]["pdf_prefettura"]["url"], cartella) or ""
        for v in (c["solo"], c["con_coniuge"], c["per_figlio"]):
            if euro_it(v) not in pdf:
                errori.append(f"soglia {euro_it(v)} non trovata nel PDF della Prefettura")
        for caso in c["casi_pdf"]:
            atteso = Decimal(c["con_coniuge"] if caso["coniuge"] else c["solo"]) + Decimal(c["per_figlio"]) * caso["figli"]
            if atteso != Decimal(caso["importo"]):
                errori.append(f"caso {caso}: la formula dà {atteso}")
            imp = euro_it(caso["importo"])
            if imp not in pdf and imp.replace(".", "", 1) not in pdf:  # nel PDF «10327,31» è scritto senza punto
                errori.append(f"caso {caso}: importo {imp} non trovato nel PDF")
    prova_calcolatore(errori, avvisi)
    print(f"\nFonti: {len(link)}; frasi: {len(R['citazioni'])}; errori: {len(errori)}; avvisi: {len(avvisi)}")
    for a in avvisi:
        print("AVVISO:", a)
    for e in errori:
        print("ERRORE:", e)
    if errori:
        return 1
    if salva:
        oggi = date.today().isoformat()
        for f in fonti.values():
            f["verificato_il"] = oggi
        (DATI / "redditi.json").write_text(json.dumps(R, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("dati/redditi.json: verificato_il →", oggi)
    return 0


if __name__ == "__main__":
    sys.exit(main("--salva" in sys.argv))
