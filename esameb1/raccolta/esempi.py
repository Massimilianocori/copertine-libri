"""Controllo ripetibile della sezione /esempi/ e della pagina /esonero-test-italiano/ di EsameB1.

Uso (dalla radice del repository):
    python3 esameb1/raccolta/esempi.py            # controlla e stampa il rapporto; esce con 1 se qualcosa non va
    python3 esameb1/raccolta/esempi.py --salva    # in più, se è tutto a posto: aggiorna 'verificato_il' in
                                                  # dati/esempi.json e dati/esoneri.json, i byte dei file cambiati
                                                  # e scrive dati/esempi_controllo.json (esito di ogni link e frase)

Cosa controlla:
1. Ogni link ufficiale usato dalle pagine (pagine degli enti, file PDF/MP3/ZIP, fonti, condizioni d'uso, fonti delle
   esenzioni) risponde 200. I file grandi si controllano con HEAD o con una richiesta parziale (Range): non si scaricano.
2. Per i file degli esempi: tipo e dimensione uguali a quelli scritti in dati/esempi.json (se cambiano: AVVISO, il file
   sul sito dell'ente è stato aggiornato e la descrizione va riletta).
3. CERT.IT: la pagina ufficiale linka ancora uno zip e 3 MP3 (li cerchiamo nella pagina, ma il sito non li linka:
   note legali di Roma Tre sul deep linking).
4. Ogni "citazione" (frase copiata dalla fonte ufficiale su cui si basa un dato della pagina) è ancora presente nel
   testo della fonte: HTML ripulito dai tag, PDF letti con pdftotext. Spazi, a capo e virgolette tipografiche non contano.

I file scaricati restano in una cartella temporanea che si cancella alla fine. Nessuna dipendenza esterna oltre a
pdftotext (poppler-utils). Nessun dato personale.
"""
import html
import http.cookiejar
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

DATI = Path(__file__).resolve().parent.parent / "dati"
UA = "Mozilla/5.0 (X11; Linux x86_64) EsameB1-controllo-fonti/1.0 (+https://esameb1.netlify.app)"
MAX_TESTO = 12_000_000  # byte massimi scaricati per leggere una fonte (il Quaderno PLIDA è 2,9 MB)
OGGI = date.today().isoformat()

cookie = http.cookiejar.CookieJar()
apri = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
cache_testi = {}


def richiesta(url, metodo="GET", intestazioni=None, leggi=True, limite=MAX_TESTO, tentativi=2):
    """(stato, intestazioni, corpo). Stato 0 se la connessione non riesce."""
    for t in range(tentativi):
        req = urllib.request.Request(url, method=metodo, headers={"User-Agent": UA, **(intestazioni or {})})
        try:
            with apri.open(req, timeout=90) as r:
                corpo = r.read(limite) if leggi and metodo == "GET" else b""
                return r.status, dict(r.headers), corpo
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers or {}), b""
        except Exception as e:  # rete: un secondo tentativo dopo una pausa
            errore = str(e)
            time.sleep(3 * (t + 1))
    return 0, {"errore": errore}, b""


def controlla_file(url):
    """Stato, tipo e dimensione senza scaricare il file intero: HEAD, poi GET con Range se HEAD non va."""
    stato, h, _ = richiesta(url, "HEAD", leggi=False)
    byte = h.get("Content-Length")
    if stato != 200 or not byte:
        stato2, h2, _ = richiesta(url, "GET", {"Range": "bytes=0-0"}, limite=1)
        if stato2 in (200, 206):
            stato, h = 200, h2
            m = re.search(r"/(\d+)$", h2.get("Content-Range", ""))
            byte = m.group(1) if m else h2.get("Content-Length")
        else:
            stato = stato2 or stato
    return {"stato": stato, "tipo": (h.get("Content-Type") or "").split(";")[0].strip(),
            "byte": int(byte) if byte and str(byte).isdigit() else None, "modificato": h.get("Last-Modified")}


def normalizza(testo):
    t = testo.replace("­", "").replace(" ", " ")
    for a, b in (("’", "'"), ("‘", "'"), ("`", "'"), ("“", '"'), ("”", '"'), ("«", '"'), ("»", '"'), ("–", "-"), ("—", "-")):
        t = t.replace(a, b)
    t = re.sub(r"-\s*\n\s*", "-", t)
    return re.sub(r"\s+", " ", t).strip().lower()


def testo_di(url, cartella):
    """Testo leggibile della fonte (HTML senza tag, PDF con pdftotext), normalizzato. None se non si scarica."""
    if url in cache_testi:
        return cache_testi[url]
    stato, h, corpo = richiesta(url)
    if stato != 200 or not corpo:
        cache_testi[url] = None
        return None
    tipo = (h.get("Content-Type") or "").lower()
    if corpo[:5] == b"%PDF-" or "pdf" in tipo:
        f = Path(cartella) / f"fonte{len(cache_testi)}.pdf"
        f.write_bytes(corpo)
        r = subprocess.run(["pdftotext", str(f), "-"], capture_output=True, timeout=120)
        testo = r.stdout.decode("utf-8", "replace")
    else:
        grezzo = corpo.decode("utf-8", "replace")
        grezzo = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", grezzo)
        testo = html.unescape(re.sub(r"<[^>]+>", " ", grezzo))
    cache_testi[url] = normalizza(testo)
    return cache_testi[url]


def main(salva=False):
    esempi = json.loads((DATI / "esempi.json").read_text(encoding="utf-8"))
    esoneri = json.loads((DATI / "esoneri.json").read_text(encoding="utf-8"))
    risultati = json.loads((DATI / "risultati.json").read_text(encoding="utf-8"))
    errori, avvisi, esito_link, esito_frasi = [], [], {}, []
    cambiati = {}

    # 1-2. link ufficiali usati dalle pagine
    link = {}
    for e in esempi["enti"]:
        link[e["pagina"]["url"]] = f'{e["sigla"]}: pagina ufficiale'
        for x in e.get("fonti_prova", []) + e.get("fonti_struttura", []):
            link[x["url"]] = f'{e["sigla"]}: {x["nome"]}'
        for c in e.get("come_usare", []):
            for x in c["fonti"]:
                link[x["url"]] = f'{e["sigla"]}: {x["nome"]}'
        for k in ("punteggio", "non_superato"):  # le pagine ente citano anche queste voci di risultati.json
            for chiave in risultati["enti"][e["sigla"]]["voci"][k]["fonti"]:
                f = risultati["enti"][e["sigla"]]["fonti"][chiave]
                link[f["url"]] = f'{e["sigla"]}: {f["nome"]}'
    for u in esempi.get("uso", []):
        link[u["url"]] = f'condizioni d\'uso {u["ente"]}'
    for k, f in esoneri["fonti"].items():
        link[f["url"]] = f"esonero: {f['nome']}"

    for e in esempi["enti"]:
        for f in e["file"]:
            if not f.get("url"):
                continue
            r = controlla_file(f["url"])
            esito_link[f["url"]] = r
            nome = f'{e["sigla"]} · {f["nome"]}'
            if r["stato"] != 200:
                errori.append(f"{nome}: stato {r['stato']} ({f['url']})")
                continue
            if r["byte"] and r["byte"] != f["byte"]:
                avvisi.append(f"{nome}: dimensione cambiata {f['byte']} → {r['byte']} byte: il file è stato aggiornato, rileggere la descrizione")
                cambiati[f["url"]] = r["byte"]
            if r["tipo"] and f.get("tipo") and r["tipo"] != f["tipo"] and not (f["formato"] == "ZIP" and "zip" in r["tipo"]):
                avvisi.append(f"{nome}: tipo {r['tipo']} (atteso {f['tipo']})")
            print(f"  ok  {nome}: {r['stato']} {r['tipo']} {r['byte']}")

    for url, cosa in link.items():
        if url in esito_link:
            continue
        r = controlla_file(url)
        esito_link[url] = r
        if r["stato"] != 200:
            errori.append(f"{cosa}: stato {r['stato']} ({url})")
        else:
            print(f"  ok  {cosa}: 200")

    # 3. CERT.IT: i file dell'esempio sono ancora sulla pagina ufficiale? (solo controllo, il sito non li linka)
    cert = next(e for e in esempi["enti"] if e["sigla"] == "CERT.IT")
    stato, _, corpo = richiesta(cert["pagina"]["url"])
    pagina = corpo.decode("utf-8", "replace")
    file_cert = sorted(set(re.findall(r'href="([^"]+\.(?:zip|mp3))"', pagina, re.I)))
    zip_n = sum(1 for u in file_cert if u.lower().endswith(".zip"))
    mp3_n = sum(1 for u in file_cert if u.lower().endswith(".mp3"))
    if zip_n < 1 or mp3_n < 3:
        errori.append(f"CERT.IT: nella pagina ufficiale trovati {zip_n} zip e {mp3_n} mp3 (attesi 1 e 3)")
    for u in file_cert:
        r = controlla_file(u)
        if r["stato"] != 200:
            errori.append(f"CERT.IT: file della pagina ufficiale non raggiungibile ({r['stato']})")
    print(f"  ok  CERT.IT: pagina ufficiale con {zip_n} zip e {mp3_n} mp3")

    # 4. frasi citate
    with tempfile.TemporaryDirectory() as cartella:
        frasi = [(e["sigla"], c["url"], c["testo"]) for e in esempi["enti"] for c in e.get("citazioni", [])]
        dm = esoneri["fonti"]["dm2021"]
        for c in esoneri["citazioni"]:
            f = esoneri["fonti"][c["fonte"]]
            url = dm["articoli"][str(c["art"])] if c.get("art") else f["url"]
            frasi.append((f"esonero/{c['fonte']}" + (f" art. {c['art']}" if c.get("art") else ""), url, c["testo"]))
        richiesta(dm["url"])  # la Gazzetta Ufficiale mostra gli articoli solo dopo la pagina dell'atto (cookie di sessione)
        for chi, url, frase in frasi:
            testo = testo_di(url, cartella)
            presente = bool(testo) and normalizza(frase) in testo
            esito_frasi.append({"chi": chi, "url": url, "testo": frase, "presente": presente})
            if testo is None:
                errori.append(f"{chi}: fonte non leggibile ({url})")
            elif not presente:
                errori.append(f"{chi}: frase non trovata nella fonte: «{frase}» ({url})")
        print(f"  frasi citate: {sum(1 for x in esito_frasi if x['presente'])}/{len(esito_frasi)} trovate nelle fonti")

    print(f"\nLink controllati: {len(esito_link)}; frasi: {len(esito_frasi)}; errori: {len(errori)}; avvisi: {len(avvisi)}")
    for a in avvisi:
        print("AVVISO:", a)
    for e in errori:
        print("ERRORE:", e)
    if errori:
        return 1
    if salva:
        for e in esempi["enti"]:
            for f in e["file"]:
                if f.get("url") in cambiati:
                    f["byte"] = cambiati[f["url"]]
        esempi["verificato_il"] = OGGI
        esoneri["verificato_il"] = OGGI
        (DATI / "esempi.json").write_text(json.dumps(esempi, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (DATI / "esoneri.json").write_text(json.dumps(esoneri, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (DATI / "esempi_controllo.json").write_text(json.dumps(
            {"data": OGGI, "link": esito_link, "frasi": esito_frasi, "avvisi": avvisi}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"Salvato: verificato_il = {OGGI} in esempi.json ed esoneri.json, esito in esempi_controllo.json")
    return 0


if __name__ == "__main__":
    sys.exit(main(salva="--salva" in sys.argv))
