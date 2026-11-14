"""Estrazione del testo dai file grezzi (PDF, HTML, XLSX) e normalizzazione per cercare le frasi alla lettera."""
import hashlib
import html
import re
import subprocess
import zipfile


def pdf(percorso, layout=False):
    cmd = ["pdftotext"] + (["-layout"] if layout else []) + [str(percorso), "-"]
    return subprocess.run(cmd, capture_output=True, check=True).stdout.decode("utf-8", errors="replace")


def pagina_html(percorso):
    s = open(percorso, encoding="utf-8", errors="replace").read()
    s = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(s)


def xlsx(percorso):
    z = zipfile.ZipFile(percorso)
    ss = re.findall(r"<si>(.*?)</si>", z.read("xl/sharedStrings.xml").decode("utf-8"), flags=re.S)
    return "\n".join(html.unescape(re.sub(r"<[^>]+>", "", x)) for x in ss)


def xlsx_righe(percorso):
    """Righe del primo foglio come liste di stringhe (numeri compresi)."""
    z = zipfile.ZipFile(percorso)
    ss = [html.unescape(re.sub(r"<[^>]+>", "", x)) for x in re.findall(r"<si>(.*?)</si>", z.read("xl/sharedStrings.xml").decode("utf-8"), flags=re.S)]
    righe = []
    for row in re.findall(r"<row[^>]*>(.*?)</row>", z.read("xl/worksheets/sheet1.xml").decode("utf-8"), flags=re.S):
        celle = []
        for attr, corpo in re.findall(r"<c ([^>]*?)(?:/>|>(.*?)</c>)", row, flags=re.S):
            v = re.search(r"<v>(.*?)</v>", corpo or "")
            if v:
                celle.append(ss[int(v.group(1))] if 't="s"' in attr else v.group(1))
        if celle:
            righe.append(celle)
    return righe


def testo(percorso):
    p = str(percorso)
    if p.endswith(".pdf"):
        return pdf(p)
    if p.endswith(".xlsx"):
        return xlsx(p)
    return pagina_html(p)


def norm(s):
    """Unisce le parole spezzate a fine riga (wa-\\nges), toglie i caratteri invisibili e riduce gli spazi."""
    s = s.replace("­", "").replace("​", "").replace(" ", " ").replace("‑", "-")
    s = re.sub(r"(\w)-\n\s*(\w)", r"\1\2", s)
    return re.sub(r"\s+", " ", s).strip()


def impronta_frasi(testo_norm, frasi):
    """Impronta delle frasi citate, così come si ritrovano nel testo della fonte (già passato da norm).

    Serve per le pagine HTML: i loro byte cambiano a ogni scarico (token, date, script), quindi l'impronta del file
    intero non dice niente; quella delle frasi cambia solo se cambia ciò che il sito cita. None se una frase manca.
    """
    righe = []
    for k in sorted(frasi):
        f = norm(frasi[k])
        if f not in testo_norm:
            return None
        righe.append(f"{k}\t{f}")
    return hashlib.sha256("\n".join(righe).encode("utf-8")).hexdigest()
