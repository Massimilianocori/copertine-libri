"""Controllo ripetibile delle pagine del 25/11/2026 di EsameB1: /esempi/cils-b1-standard/, /esempi/a1/, /esempi/c1/, /esempi/c2/.

Uso (dalla radice del repository):
    python3 esameb1/raccolta/esempi_livelli.py           # controlla fonti, frasi e file; esce con 1 se qualcosa non va
    python3 esameb1/raccolta/esempi_livelli.py --salva   # in più, se è tutto a posto, porta 'verificato_il' a oggi e aggiorna i byte cambiati

Cosa controlla (dati/esempi_livelli.json):
1. ogni fonte risponde 200 e ogni frase in "citazioni" è ancora nel testo della fonte (HTML senza tag, PDF con pdftotext);
2. ogni file con link diretto risponde 200; tipo e dimensione uguali a quelli scritti (se cambiano: AVVISO, rileggere la descrizione);
3. CILS: ogni file è ancora linkato dalla pagina ufficiale del suo gruppo, e la pagina non ha file nuovi (AVVISO se ne ha);
4. PLIDA: ogni file è ancora nell'elenco che la pagina «Preparati all'esame» legge dal sito (campo "elenco" della fonte), al suo livello;
5. CELI (nessun link diretto: i file stanno su www.unistrapg.it, che dal nostro server non si apre): la pagina del CVCL linka ancora
   gli zip attesi ("file_attesi"); i file non vengono aperti;
   CERT.IT (nessun link diretto): la pagina ufficiale linka ancora almeno lo zip e gli MP3 attesi, e rispondono 200;
6. prove CILS B1 Cittadinanza di altre sessioni: se la pagina «Prove Liv. B1 c» o «Esempi prove di esami» cambia l'elenco, AVVISO.
I file non si scaricano interi (HEAD o richiesta parziale). Usa le funzioni di raccolta/esempi.py. Nessun dato personale.
"""
import html
import json
import re
import sys
import tempfile
import urllib.parse
from datetime import date
from pathlib import Path

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import esempi as E  # noqa: E402

FILE = QUI.parent / "dati" / "esempi_livelli.json"


def link_file(url_pagina):
    """Indirizzi dei file (public/articoli) linkati con un testo nel corpo di una pagina «Prove Liv. …» del Centro CILS."""
    stato, _, corpo = E.richiesta(url_pagina)
    t = corpo.decode("utf-8", "replace")
    i = t.find("<h1")
    corpo_ = t[i:t.find("Leggi anche", i)]
    trovati = []
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', corpo_, re.S):
        if "public/articoli" in m.group(1) and re.sub(r"<[^>]+>|\s+", "", m.group(2)):
            trovati.append(urllib.parse.quote(html.unescape(m.group(1)), safe=":/%"))
    return stato, list(dict.fromkeys(trovati))


def main(salva=False):
    D = json.loads(FILE.read_text(encoding="utf-8"))
    errori, avvisi, cambiati = [], [], {}
    with tempfile.TemporaryDirectory() as cartella:
        for k, f in D["fonti"].items():
            testo = E.testo_di(f["url"], cartella)
            print(f"  {'ok ' if testo else 'NO '} {k}")
            if not testo:
                errori.append(f"{k}: fonte non leggibile ({f['url']})")
        n = 0
        for c in D["citazioni"]:
            testo = E.testo_di(D["fonti"][c["fonte"]]["url"], cartella)
            if testo and E.normalizza(c["testo"]) in testo:
                n += 1
            elif testo:
                errori.append(f"{c['fonte']}: frase non trovata: «{c['testo']}»")
        print(f"  frasi citate: {n}/{len(D['citazioni'])} trovate nelle fonti")

    n_file = 0
    for nome, g in D["gruppi"].items():
        for x in g["file"]:
            if not x.get("url"):
                continue
            r = E.controlla_file(x["url"])
            if r["stato"] != 200:
                errori.append(f"{nome} · {x['nome']}: stato {r['stato']} ({x['url']})")
                continue
            n_file += 1
            if r["byte"] and r["byte"] != x["byte"]:
                avvisi.append(f"{nome} · {x['nome']}: dimensione cambiata {x['byte']} → {r['byte']} byte: rileggere la descrizione")
                cambiati[x["url"]] = r["byte"]
            if r["tipo"] and r["tipo"] != x["tipo"] and not (x["formato"] == "ZIP" and "zip" in r["tipo"]):
                avvisi.append(f"{nome} · {x['nome']}: tipo {r['tipo']} (atteso {x['tipo']})")
    print(f"  file con link diretto: {n_file} rispondono 200")

    for nome, g in D["gruppi"].items():
        pagina = D["fonti"][g["fonte"]]
        if g["ente"] == "CILS":
            stato, sulla_pagina = link_file(pagina["url"])
            nostri = [x["url"] for x in g["file"]]
            for u in nostri:
                if u not in sulla_pagina:
                    errori.append(f"{nome}: file non più linkato dalla pagina ufficiale: {u}")
            for u in sulla_pagina:
                if u not in nostri:
                    avvisi.append(f"{nome}: la pagina ufficiale ha un file che non elenchiamo: {u}")
        elif g["ente"] == "PLIDA":
            stato, _, corpo = E.richiesta(pagina["elenco"])
            try:
                comp = json.loads(corpo.decode("utf-8"))["response"][0]["components"]
                elenco = [f for c in comp if isinstance(c.get("data"), dict) for f in (c["data"].get("files") or [])]
            except (ValueError, KeyError, IndexError, AttributeError):
                errori.append(f"{nome}: elenco dei materiali PLIDA non leggibile ({pagina['elenco']})")
                continue
            del_livello = [f["file"]["url"] for f in elenco if f.get("level") == g["livello_feed"]]
            for x in g["file"]:
                if x["url"] not in del_livello:
                    errori.append(f"{nome}: file non più nell'elenco PLIDA del livello: {x['url']}")
            for u in del_livello:
                if u not in [x["url"] for x in g["file"]]:
                    avvisi.append(f"{nome}: l'elenco PLIDA del livello ha un file che non elenchiamo: {u}")
        elif g["ente"] == "CELI":  # file su www.unistrapg.it (non si apre dal nostro server): solo che la pagina del CVCL li linki ancora
            stato, _, corpo = E.richiesta(pagina["url"])
            t = html.unescape(corpo.decode("utf-8", "replace"))
            for nome_file in g["file_attesi"]:
                if not re.search(r'href="[^"]*/' + re.escape(nome_file) + '"', t):
                    errori.append(f"{nome}: la pagina del CVCL non linka più {nome_file}")
            print(f"  ok  {nome}: la pagina del CVCL linka i {len(g['file_attesi'])} zip attesi (non aperti)")
        elif not g.get("link_diretti", True):
            stato, _, corpo = E.richiesta(pagina["url"])
            trovati = sorted(set(re.findall(r'href="([^"]+\.(?:zip|mp3))"', corpo.decode("utf-8", "replace"), re.I)))
            zip_n = sum(1 for u in trovati if u.lower().endswith(".zip"))
            mp3_n = sum(1 for u in trovati if u.lower().endswith(".mp3"))
            if zip_n < g["zip_attesi"] or mp3_n < g["mp3_attesi"]:
                errori.append(f"{nome}: nella pagina ufficiale {zip_n} zip e {mp3_n} mp3 (attesi {g['zip_attesi']} e {g['mp3_attesi']})")
            for u in trovati:
                if E.controlla_file(u)["stato"] != 200:
                    errori.append(f"{nome}: file della pagina ufficiale non raggiungibile")
            print(f"  ok  {nome}: pagina ufficiale con {zip_n} zip e {mp3_n} mp3")

    # 6. sessioni passate del B1 Cittadinanza: oggi non ci sono; se l'elenco delle pagine di esempi cambia, va riletto
    _, corpo = E.richiesta(D["fonti"]["cils_esempi"]["url"])[1:]
    voci = sorted(set(re.findall(r"/1/89/(\d+)/", corpo.decode("utf-8", "replace"))))
    attese = ["188", "189", "190", "191", "192", "193", "194", "195", "196", "197", "198", "199", "200", "202", "274", "382", "426"]
    if voci != attese:
        avvisi.append(f"CILS, «Esempi prove di esami»: l'elenco delle pagine è cambiato ({voci}): controllare se ci sono prove di altre sessioni")

    print(f"\nFonti: {len(D['fonti'])}; frasi: {len(D['citazioni'])}; file: {n_file}; errori: {len(errori)}; avvisi: {len(avvisi)}")
    for a in avvisi:
        print("AVVISO:", a)
    for e in errori:
        print("ERRORE:", e)
    if errori:
        return 1
    if salva:
        for g in D["gruppi"].values():
            for x in g["file"]:
                if x.get("url") in cambiati:
                    x["byte"] = cambiati[x["url"]]
        D["verificato_il"] = date.today().isoformat()
        FILE.write_text(json.dumps(D, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("verificato_il aggiornato")
    return 0


if __name__ == "__main__":
    sys.exit(main("--salva" in sys.argv))
