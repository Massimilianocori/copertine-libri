"""Controllo ripetibile delle pagine del 13/11/2026 di EsameB1: /test-italiano-a2/, /carta-di-soggiorno/,
/cittadinanza-per-matrimonio/, /pratica-cittadinanza/.

Uso (dalla radice del repository):
    python3 esameb1/raccolta/guide.py           # controlla fonti e frasi; esce con 1 se qualcosa non va
    python3 esameb1/raccolta/guide.py --salva   # in più, se è tutto a posto, porta 'verificato_il' a oggi

Cosa controlla: ogni fonte di dati/guide_cittadinanza.json risponde 200 e ogni frase in "citazioni" è ancora nel testo
della fonte (HTML senza tag, PDF con pdftotext; spazi e virgolette tipografiche non contano). Usa le funzioni di
lettura di raccolta/esempi.py. Nessun dato personale.
"""
import json
import sys
import tempfile
from datetime import date
from pathlib import Path

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import esempi as E  # noqa: E402

FILE = QUI.parent / "dati" / "guide_cittadinanza.json"


def main(salva=False):
    D = json.loads(FILE.read_text(encoding="utf-8"))
    errori = []
    with tempfile.TemporaryDirectory() as cartella:
        for k, f in D["fonti"].items():
            testo = E.testo_di(f["url"], cartella)
            print(f"  {'ok ' if testo else 'NO '} {k}")
            if not testo:
                errori.append(f"{k}: fonte non leggibile ({f['url']})")
        n = 0
        for cit in D["citazioni"]:
            testo = E.testo_di(D["fonti"][cit["fonte"]]["url"], cartella)
            if testo and E.normalizza(cit["testo"]) in testo:
                n += 1
            elif testo:
                errori.append(f"{cit['fonte']}: frase non trovata: «{cit['testo']}»")
        print(f"  frasi citate: {n}/{len(D['citazioni'])} trovate nelle fonti")
    print(f"\nFonti: {len(D['fonti'])}; frasi: {len(D['citazioni'])}; errori: {len(errori)}")
    for e in errori:
        print("ERRORE:", e)
    if errori:
        sys.exit(1)
    if salva:
        D["verificato_il"] = date.today().isoformat()
        FILE.write_text(json.dumps(D, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("verificato_il aggiornato")


if __name__ == "__main__":
    main("--salva" in sys.argv)
