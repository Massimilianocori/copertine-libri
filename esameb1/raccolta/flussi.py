"""Controllo ripetibile della pagina /decreto-flussi-click-day/ di EsameB1 (date dei click day del decreto flussi).

Uso (dalla radice del repository):
    python3 esameb1/raccolta/flussi.py           # controlla fonti, frasi e impronte; esce con 1 se qualcosa non va
    python3 esameb1/raccolta/flussi.py --salva   # in più, se è tutto a posto, scrive in dati/flussi.json
                                                 # 'impronta' e 'letta_il' di ogni fonte

Cosa controlla:
1. Ogni fonte di dati/flussi.json (DPCM in Gazzetta Ufficiale, circolari congiunte su lavoro.gov.it, pagine del
   Ministero del Lavoro, del Ministero dell'Interno e del Portale Integrazione Migranti) e il Portale ALI rispondono 200.
2. Ogni frase in "citazioni" è ancora nel testo della sua fonte (HTML senza tag, PDF con pdftotext; spazi e virgolette
   tipografiche non contano).
3. Impronta: SHA-256 (primi 16 caratteri) del testo normalizzato. Se è diversa da quella salvata: AVVISO, la fonte è
   cambiata e la pagina va riletta (le frasi possono esserci ancora, ma può esserci altro di nuovo).

Usa le funzioni di lettura di raccolta/esempi.py. La Gazzetta Ufficiale a volte chiude la connessione: riprovare dopo.
"""
import hashlib
import json
import sys
import tempfile
from datetime import date
from pathlib import Path

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import esempi as E  # noqa: E402  (richiesta, testo_di, normalizza)

FILE = QUI.parent / "dati" / "flussi.json"


def impronta(testo):
    return hashlib.sha256(testo.encode("utf-8")).hexdigest()[:16]


def main(salva=False):
    F = json.loads(FILE.read_text(encoding="utf-8"))
    errori, avvisi, nuove = [], [], {}
    stato, _, _ = E.richiesta(F["portale"]["url"], leggi=False)
    print(f"  {'ok ' if stato == 200 else 'NO '} portale ALI: {stato}")
    if stato != 200:
        avvisi.append(f"portale ALI: stato {stato} (può essere momentaneo)")
    with tempfile.TemporaryDirectory() as cartella:
        testi = {}
        for k, f in F["fonti"].items():
            t = E.testo_di(f["url"], cartella)
            testi[k] = t
            if t is None:
                errori.append(f"{k}: fonte non leggibile ({f['url']})")
                print(f"  NO  {k}")
                continue
            nuove[k] = impronta(t)
            cambiata = f.get("impronta") and f["impronta"] != nuove[k]
            print(f"  ok  {k}: impronta {nuove[k]}{'  (CAMBIATA)' if cambiata else ''}")
            if cambiata:
                avvisi.append(f"{k}: impronta cambiata ({f['impronta']} → {nuove[k]}): rileggere la fonte {f['url']}")
        n = 0
        for c in F["citazioni"]:
            t = testi.get(c["fonte"])
            if c["fonte"] not in F["fonti"]:
                errori.append(f"citazione con fonte sconosciuta: {c['fonte']}")
            elif t is not None and E.normalizza(c["testo"]) not in t:
                errori.append(f"{c['fonte']}: frase non trovata: «{c['testo']}»")
            elif t is not None:
                n += 1
        print(f"  frasi citate: {n}/{len(F['citazioni'])} trovate nelle fonti")
    print(f"\nFonti: {len(F['fonti'])}; errori: {len(errori)}; avvisi: {len(avvisi)}")
    for a in avvisi:
        print("AVVISO:", a)
    for e in errori:
        print("ERRORE:", e)
    if errori:
        return 1
    if salva:
        oggi = date.today().isoformat()
        for k, f in F["fonti"].items():
            f["impronta"], f["letta_il"] = nuove[k], oggi
        F["portale"]["letta_il"] = oggi
        FILE.write_text(json.dumps(F, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("dati/flussi.json: impronte e letta_il →", oggi)
    return 0


if __name__ == "__main__":
    sys.exit(main("--salva" in sys.argv))
