"""Aggiorna dati/uma.json con il valore ufficiale della UMA (INEGI) dell'anno nuovo, per il Visitax del Quintana Roo (2,50 UMA).

Uso (dalla radice del repository, da inizio gennaio):
    python3 -I touristtax/raccolta/uma.py            # prova l'anno in "prossima" di dati/uma.json
    python3 -I touristtax/raccolta/uma.py --prova    # legge e stampa, non scrive nulla
poi:
    python3 touristtax/genera.py && python3 touristtax/verifica.py

Cosa fa:
1. scarica il comunicato INEGI dell'anno (URL in uma.json, "prossima"); lo accetta solo se è un PDF che contiene
   "a partir del 1 de febrero de <anno>" e la riga della tabella "<anno>  diario  mensual  anual", con mensual = diario × 30.4
   e anual = mensual × 12 (regola INEGI); altrimenti non scrive nulla (a fine ottobre il percorso 2027 risponde 200 con una
   pagina HTML "Página no encontrada");
2. aggiunge il valore a "valori" (dal = 1 febbraio dell'anno, fonte con HTTP e data del controllo) e sposta "prossima" all'anno dopo;
3. controlla se il Congresso del Quintana Roo ha pubblicato una versione nuova della Ley de Derechos (elenco /leyes/195/) o se la
   Ley Federal de Derechos ha una riforma nuova: in quel caso stampa un AVVISO (le regole si rileggono a mano, niente si cambia da solo).
Serve curl e pdftotext. Esce con codice 0 anche quando il comunicato non c'è ancora (stampa cosa ha trovato).
"""
import json
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
F_UMA = RADICE / "dati" / "uma.json"
F_MX = RADICE / "dati" / "messico.json"
LFD_RIFORMA = "07-11-2025"  # ultima riforma della Ley Federal de Derechos letta il 30/10/2026


def scarica(url, dest):
    """(codice HTTP, content-type) con curl; il file va in dest."""
    r = subprocess.run(["curl", "-sS", "-L", "-m", "90", "-A", "Mozilla/5.0", "-o", str(dest), "-w", "%{http_code} %{content_type}", url],
                       capture_output=True, text=True)
    parti = (r.stdout or "000 ").split(" ", 1)
    return int(parti[0] or 0), (parti[1] if len(parti) > 1 else "")


def testo_pdf(f):
    r = subprocess.run(["pdftotext", "-layout", str(f), "-"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def leggi_uma(anno, url, cartella):
    f = Path(cartella) / f"uma{anno}.pdf"
    http, tipo = scarica(url, f)
    if http != 200 or not f.exists() or f.read_bytes()[:4] != b"%PDF":
        return None, f"comunicato {anno} non ancora pubblicato (HTTP {http}, {tipo or 'nessun tipo'}, non è un PDF)"
    t = testo_pdf(f)
    if f"1 de febrero de {anno}" not in t:
        return None, f"il PDF non dice 'a partir del 1 de febrero de {anno}'"
    m = re.search(rf"^\s*{anno}\s+(\d{{2,4}}\.\d\d)\s+([\d ]+\.\d\d)\s+([\d ]+\.\d\d)\s*$", t, re.M)
    if not m:
        return None, f"riga '{anno} diario mensual anual' non trovata nel PDF"
    diario, mensual, anual = (float(x.replace(" ", "")) for x in m.groups())
    if abs(diario * 30.4 - mensual) > 0.011 or abs(mensual * 12 - anual) > 0.011:
        return None, f"valori incoerenti: diario {diario}, mensual {mensual}, anual {anual}"
    return {"anno": anno, "diario": diario, "dal": f"{anno}-02-01",
            "fonte": {"titolo": f"INEGI - Unidad de Medida y Actualización (UMA) {anno}, press release", "url": url, "http": 200,
                      "controllato_il": date.today().isoformat()}}, f"UMA {anno}: {diario} pesos al giorno dal 1/2/{anno}"


def controlla_leggi(cartella):
    avvisi = []
    mx = json.loads(F_MX.read_text(encoding="utf-8"))
    legge = mx["visitax"]["legge"]
    f = Path(cartella) / "elenco195.html"
    http, _ = scarica(legge["elenco_versioni"], f)
    if http == 200:
        versioni = sorted(set(re.findall(r"L195-[^\"'<>\s]+\.pdf", f.read_text(encoding="utf-8", errors="ignore"))))
        if versioni and versioni[-1] != legge["file_versione"]:
            avvisi.append(f"AVVISO: nuova versione della Ley de Derechos del Quintana Roo: {versioni[-1]} (dati: {legge['file_versione']}). "
                          "Rileggere l'art. 51-Octies (2,50 UMA) e il 51-Nonies (crociere) e aggiornare dati/messico.json e destinazioni.json.")
    else:
        avvisi.append(f"elenco delle versioni della legge non leggibile (HTTP {http}): controllo a mano")
    f = Path(cartella) / "lfd.pdf"
    http, _ = scarica(mx["federali"]["dnr"]["url"], f)
    if http == 200:
        testa = testo_pdf(f)[:3000]
        m = re.search(r"Última Reforma DOF (\d\d-\d\d-\d{4})", testa)
        agg = re.search(r"Cantidades actualizadas por Resolución Miscelánea Fiscal DOF (\d\d-\d\d-\d{4})", testa)
        if m and m.group(1) != LFD_RIFORMA:
            avvisi.append(f"AVVISO: Ley Federal de Derechos riformata (DOF {m.group(1)}): rileggere art. 8 (DNR), 11 e 12.")
        if agg:
            print(f"Ley Federal de Derechos: importi aggiornati dalla Resolución Miscelánea Fiscal DOF {agg.group(1)} "
                  f"(se è di fine dicembre, gli importi valgono per l'anno nuovo: controllare DNR e art. 12 in dati/messico.json)")
    else:
        avvisi.append(f"Ley Federal de Derechos non leggibile (HTTP {http}): controllo a mano")
    return avvisi


def main(argv):
    prova = "--prova" in argv
    uma = json.loads(F_UMA.read_text(encoding="utf-8"))
    p = uma["prossima"]
    with tempfile.TemporaryDirectory() as tmp:
        if any(v["anno"] == p["anno"] for v in uma["valori"]):
            print(f"UMA {p['anno']} già nei dati.")
            nuovo = None
        else:
            nuovo, msg = leggi_uma(p["anno"], p["url"], tmp)
            print(msg)
        for a in controlla_leggi(tmp):
            print(a)
    if nuovo and not prova:
        uma["valori"].append(nuovo)
        uma["valori"].sort(key=lambda v: v["dal"])
        a = p["anno"] + 1
        uma["prossima"] = {"anno": a, "dal": f"{a}-02-01",
                           "url": p["url"].replace(str(p["anno"]), str(a)),
                           "attesa": p.get("attesa", "INEGI publishes the new UMA in the first half of January.")}
        F_UMA.write_text(json.dumps(uma, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"Scritto {F_UMA}: Visitax dal 1/2/{p['anno']} = 2,50 × {nuovo['diario']}. Ora: python3 touristtax/genera.py && python3 touristtax/verifica.py")


if __name__ == "__main__":
    main(sys.argv[1:])
