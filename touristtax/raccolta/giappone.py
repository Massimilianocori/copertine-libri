"""Tasse di soggiorno in Giappone (宿泊税): controllo ripetibile delle fonti ufficiali (31/10/2026).

Uso (dalla radice del repository):
    python3 -I touristtax/raccolta/giappone.py            # solo controllo, non scrive nulla
    python3 -I touristtax/raccolta/giappone.py --scrivi   # aggiorna dati/giappone_elenco_mic.json (istantanea dell'elenco)

Cosa fa:
1. Scarica l'elenco del Ministero degli Affari interni (法定外税の状況, PDF) indicato in dati/giappone_tasse.json -> fonte_elenco,
   ne legge la data ("令和N年M月D日現在"), gli enti con il 宿泊税 in vigore (Prefetture e Comuni), quelli approvati ma non ancora
   in vigore (nota *7, con la data prevista) e le date di partenza della nota *2. Confronta con gli enti dei dati: segnala enti nuovi,
   enti spariti, stato o data diversi.
2. Cerca nei comunicati stampa del Ministero (s-news/01zeimu02_0200NNNN.html, dopo l'ultimo letto) i nuovi consensi a un 宿泊税
   (新設 o 変更) e ne stampa titolo e PDF: sono la fonte delle tariffe.
3. Riapre ogni fonte dei dati e stampa il codice HTTP; per i PDF del Ministero controlla che ogni importo in yen dei dati compaia nel testo.
Con --scrivi salva l'istantanea dell'elenco (letta da verifica.py, controllo 11). Non cambia mai le tariffe: quelle si aggiornano a mano
nei dati, leggendo il consenso del Ministro o la pagina dell'ente. Serve curl e pdftotext. Esce con 1 se trova differenze.
"""
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
ISTANTANEA = DATI / "giappone_elenco_mic.json"
COMUNICATI = "https://www.soumu.go.jp/menu_news/s-news/01zeimu02_0200{n:04d}.html"


def scarica(url, dest, tentativi=3):
    """Codice HTTP (0 = connessione fallita); riprova: alcuni server comunali chiudono a volte la connessione."""
    codice = 0
    for _ in range(tentativi):
        r = subprocess.run(["curl", "-sS", "-L", "-m", "90", "-A", "Mozilla/5.0", "-o", str(dest), "-w", "%{http_code}", url],
                           capture_output=True, text=True)
        codice = int(r.stdout.strip()) if r.stdout.strip().isdigit() else 0
        if codice == 200 or codice == 404:
            break
    return codice


def testo_pdf(f, raw=True):
    r = subprocess.run(["pdftotext"] + (["-raw"] if raw else []) + [str(f), "-"], capture_output=True, text=True)
    return unicodedata.normalize("NFKC", r.stdout)


def reiwa(t):
    """'令和8年10月1日' -> '2026-10-01' (anno del Reiwa + 2018)."""
    m = re.search(r"令和\s*(\d+)\s*年\s*(\d+)\s*月\s*(\d+)\s*日", t)
    return f"{2018 + int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}" if m else None


def nomi(testo):
    """Nomi di enti separati da '、' o spazi (non con una regex: '京都市' e '留寿都村' contengono '都')."""
    return [x for x in re.split(r"[、,\s]+", testo) if re.fullmatch(r"[一-龥ぁ-んァ-ヶー]+(?:都|道|府|県|市|町|村)", x)]


def leggi_elenco(t):
    """Dal testo (-raw) del PDF: data, enti in vigore (blocchi '宿泊税 ...' fino al numero del gettito), approvati e date."""
    out = {"alla_data": reiwa(re.search(r"令和\s*\d+\s*年\s*\d+\s*月\s*\d+\s*日現在", t).group(0)), "in_vigore": [], "approvati": {}, "partenze": {}}
    for m in re.finditer(r"宿泊税 (.*?)\n[\d.,]+\s*\n", t, re.S):
        out["in_vigore"] += nomi(re.sub(r"\(\*\s*\w\)", " ", m.group(1)))
    note = re.sub(r"\s+", "", t)
    n7 = re.search(r"\*7条例制定.*?である。", note)
    if n7:
        for gruppo, quando in re.findall(r"([^、。]*?(?:、[^、。]*?)*)は(令和\d+年\d+月(?:\d+日|以降))", n7.group(0).split("施行予定日は", 1)[-1]):
            d = reiwa(quando) or quando
            for x in nomi(gruppo):
                out["approvati"][x] = d
    n2 = re.search(r"\*2(.*?)徴収実績はない", note)
    if n2:
        for gruppo, quando in re.findall(r"宿泊税[（(]([^）)]*)[）)]は(令和\d+年\d+月\d+日)", n2.group(1)):
            for x in nomi(gruppo):
                out["partenze"][x] = reiwa(quando)
    return out


def main():
    scrivi = "--scrivi" in sys.argv
    J = json.loads((DATI / "giappone_tasse.json").read_text(encoding="utf-8"))
    enti = {e["ja"]: e for e in J["enti"]}
    diff = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # 1. elenco del Ministero
        f = tmp / "elenco.pdf"
        http = scarica(J["fonte_elenco"]["url"], f)
        print(f"Elenco MIC: HTTP {http} {J['fonte_elenco']['url']}")
        if http != 200:
            sys.exit(1)
        E = leggi_elenco(testo_pdf(f))
        print(f"  al {E['alla_data']}: {len(E['in_vigore'])} enti in vigore, {len(E['approvati'])} approvati")
        for x in E["in_vigore"]:
            if x not in enti:
                diff.append(f"NUOVO ente in vigore nell'elenco, non nei dati: {x}")
            elif enti[x]["stato"] != "in_vigore":
                diff.append(f"{x}: nell'elenco è in vigore, nei dati '{enti[x]['stato']}'")
        for x, d in E["approvati"].items():
            if x not in enti:
                diff.append(f"NUOVO ente approvato nell'elenco, non nei dati: {x} (partenza {d})")
            elif enti[x]["stato"] != "approvato" or (enti[x].get("inizio") or "") != (d if len(d) == 10 else ""):
                diff.append(f"{x}: nell'elenco approvato dal {d}, nei dati {enti[x]['stato']} dal {enti[x].get('inizio')}")
        for x, e in enti.items():
            if x not in E["in_vigore"] and x not in E["approvati"]:
                diff.append(f"{x}: nei dati ma non più nell'elenco del Ministero")
        for x, d in E["partenze"].items():
            if x in enti and enti[x].get("inizio_da") == "mic" and enti[x].get("inizio") != d:
                diff.append(f"{x}: partenza {d} nell'elenco (nota *2), {enti[x].get('inizio')} nei dati")
        # 2. comunicati stampa nuovi
        ultimo = J.get("ultimo_comunicato", 476)
        vuoti = 0
        n = ultimo + 1
        while vuoti < 12:
            g = tmp / f"c{n}.html"
            if scarica(COMUNICATI.format(n=n), g) == 200:
                t = g.read_bytes().decode("shift_jis", "replace")
                tit = re.search(r"<title>([^<]*)", t)
                tit = tit.group(1) if tit else ""
                if "見つかりません" in tit:
                    vuoti += 1
                else:
                    vuoti = 0
                    if "宿泊税" in t:
                        pdf = sorted(set(re.findall(r'href="(/main_content/\d+\.pdf)"', t)))
                        diff.append(f"Comunicato nuovo sul 宿泊税 (n. {n}): {tit} {' '.join('https://www.soumu.go.jp' + p for p in pdf)}")
            else:
                vuoti += 1
            n += 1
        print(f"  comunicati controllati dal n. {ultimo + 1} al n. {n - 1}")
        # 3. fonti dei dati
        visti = {}
        for e in J["enti"]:
            for fo in e["fonti"]:
                u = fo["url"]
                if u not in visti:
                    p = tmp / f"f{len(visti)}"
                    visti[u] = (scarica(u, p), p)
                http, p = visti[u]
                if http != 200:
                    diff.append(f"{e['ja']}: fonte HTTP {http}: {u}")
                elif u.startswith("https://www.soumu.go.jp/main_content/") and "consent" in fo["titolo"] and u != J["fonte_elenco"]["url"]:
                    t = re.sub(r"[\s,]", "", testo_pdf(p, raw=False))
                    if e["ja"] not in t and e["ja"].rstrip("都道府県") not in t:
                        continue  # consenso di un altro ente (per esempio la Prefettura citata nella pagina del Comune)
                    importi = {int(x[2]) for r in e["regole"] if r["tipo"] == "bande" for x in r["bande"] if x[2]}
                    for v in importi:
                        if f"{v}円" not in t:
                            print(f"  attenzione: {e['ja']}: {v}円 non trovato nel consenso {u} (può essere una tariffa di un'altra fonte)")
        print(f"  fonti riaperte: {len(visti)}")
    for d in diff:
        print("  -", d)
    if scrivi:
        ist = {"alla_data": E["alla_data"], "controllato_il": date.today().isoformat(), "url": J["fonte_elenco"]["url"],
               "in_vigore": E["in_vigore"], "approvati": E["approvati"], "partenze": E["partenze"]}
        ISTANTANEA.write_text(json.dumps(ist, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Scritto {ISTANTANEA}")
    if diff:
        sys.exit(1)
    print("Nessuna differenza tra i dati e le fonti ufficiali.")


if __name__ == "__main__":
    main()
