"""Controllo ripetibile delle fonti usate solo dalle sezioni in ucraino (/uk/) e rumeno (/ro/) di EsameB1.

Uso (dalla radice del repository):
    python3 esameb1/raccolta/lingue.py           # controlla fonti e frasi; esce con 1 se qualcosa non va
    python3 esameb1/raccolta/lingue.py --salva   # in più, se è tutto a posto, porta 'verificato_il' a oggi in dati/lingue.json

Cosa controlla: ogni fonte di dati/lingue.json (Questure e Prefettura sulla protezione temporanea per gli ucraini,
Polizia di Stato sui cittadini UE e sul controllo del permesso, pagina DLCI sull'art. 9 della legge 91/1992) risponde 200
e ogni frase in "citazioni" è ancora nel testo (spazi e virgolette tipografiche non contano). Se una frase non c'è più
(per esempio una Questura cambia la data della proroga), genera_lingue.py va riletto e aggiornato: le cifre delle pagine
/uk/ e /ro/ si leggono da queste frasi. Una richiesta ogni 1,5 secondi. Nessun dato personale.
"""
import json
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import esempi as E  # noqa: E402  (testo_di, normalizza)

FILE = QUI.parent / "dati" / "lingue.json"


def main(salva=False):
    dati = json.loads(FILE.read_text(encoding="utf-8"))
    errori = []
    with tempfile.TemporaryDirectory() as cartella:
        testi = {}
        for k, f in dati["fonti"].items():
            testi[k] = E.testo_di(f["url"], cartella)
            if testi[k] is None:
                errori.append(f"{k}: la fonte non risponde 200 ({f['url']})")
            time.sleep(1.5)
        trovate = 0
        for c in dati["citazioni"]:
            t = testi.get(c["fonte"])
            if t is None:
                continue
            if E.normalizza(c["testo"]) in t:
                trovate += 1
            else:
                errori.append(f"{c['fonte']}: frase non più presente: «{c['testo'][:120]}»")
    print(f"lingue.json: {len(dati['fonti'])} fonti, {trovate}/{len(dati['citazioni'])} frasi trovate, {len(errori)} errori")
    for e in errori:
        print("  -", e)
    if errori:
        return 1
    if salva:
        oggi = date.today().isoformat()
        dati["verificato_il"] = oggi
        for f in dati["fonti"].values():
            f["verificato_il"] = oggi
        FILE.write_text(json.dumps(dati, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"verificato_il → {oggi}")
    return 0


if __name__ == "__main__":
    sys.exit(main("--salva" in sys.argv[1:]))
