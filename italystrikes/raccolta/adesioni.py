"""Sindacati proclamanti e aderenti degli scioperi generali nazionali, dal calendario della Commissione di garanzia.

Perché: il registro del Ministero non risponde dal 23/10/2026 e le sue voci restano ferme a quel giorno (i campi delle
voci MIT non vengono mai sovrascritti: regola di NOTE.md). Per gli scioperi generali le adesioni cambiano fino all'ultimo
(es. 4/12/2026: USB e ORSA hanno aderito dopo). Questo script NON tocca dati/scioperi.json: scrive dati/adesioni.json,
che le pagine per data mostrano accanto alla voce del registro, con il link alla scheda della Commissione.

Abbinamento: voce MIT in arrivo, settore Generale, nazionale -> scheda CGSSE dello stesso giorno, «Generale nazionale»,
ambito nazionale, non revocata, con almeno 2 sigle proclamanti in comune (la scheda con più sigle in comune).
Uso: python3 italystrikes/raccolta/adesioni.py [file.jsonl]   (senza file scarica la copia onData, CC BY 4.0)
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fonte_cgsse as CG  # noqa: E402

DATI = Path(__file__).resolve().parent.parent / "dati"


def sigle(t):
    return {re.sub(r"[^A-Z0-9]", "", x.upper()) for x in re.split(r"[/,]", t) if x.strip()}


def main():
    oggi = datetime.now(CG.ROMA).date().isoformat()
    testo = Path(sys.argv[1]).read_text(encoding="utf-8") if len(sys.argv) > 1 else CG.scarica(CG.URL_COPIA)
    schede = CG.unisci(CG.leggi_jsonl(testo))
    scioperi = json.loads((DATI / "scioperi.json").read_text(encoding="utf-8"))
    voci = {}
    for s in scioperi.values():
        if s.get("fonte") == "cgsse" or s["settore"] != "Generale" or s["regione"].strip().upper() != "ITALIA" or s["fine"] < oggi:
            continue
        migliore, comuni = None, 1
        for num, r in schede.items():
            if r["revocato"] or (r.get("data_dal_iso") or r.get("data_iso")) != s["inizio"]:
                continue
            if r.get("settore") != "Generale nazionale" or (r.get("ambito_geografico") or "").upper() != "NAZIONALE":
                continue
            proc = (r.get("sindacato") or "").split("|")[0].replace("Proclamante:", "")
            n = len(sigle(proc) & sigle(s["sindacati"]))
            if n > comuni:
                migliore, comuni = (num, r), n
        if migliore:
            num, r = migliore
            parti = (r.get("sindacato") or "").split("|")
            voci[s["id"]] = {"cgsse": num, "url": r.get("dettagli_link", ""),
                             "proclamanti": parti[0].replace("Proclamante:", "").strip(),
                             "aderenti": parti[1].replace("Aderente:", "").strip() if len(parti) > 1 else "",
                             "letto_il": oggi}
            print(f"{s['id']} ({s['inizio']}) -> CGSSE {num}: {r.get('sindacato')}")
    (DATI / "adesioni.json").write_text(json.dumps(
        {"_nota": "Scritto da raccolta/adesioni.py: sindacati degli scioperi generali nazionali secondo la Commissione di garanzia "
                  "(copia onData, CC BY 4.0). Non modifica le voci del registro.", "voci": voci}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
