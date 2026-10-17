"""Funzioni comuni a scarica.py ed estrai.py: lettura delle pagine del CDC e scelta delle navi da pubblicare."""
import base64
import html
import re
from datetime import date
from pathlib import Path
from urllib.parse import unquote

RADICE = Path(__file__).resolve().parent.parent
CACHE = RADICE / "cache"
DATI = RADICE / "dati"

N_RAPPORTI = 3  # rapporti completi scaricati e pubblicati per ogni nave (le ultime N ispezioni)
# Navi archiviate (non più nel Green Sheet perché non navigano più da porti USA): pagina solo se l'ultima ispezione
# è recente e la storia ha abbastanza ispezioni da dire qualcosa. Le altre restano fuori (elenco in NOTE.md).
ARCHIVIATE_DAL = "2023-01-01"
ARCHIVIATE_MIN_ISPEZIONI = 3


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", html.unescape(s).lower()).strip()


def testo_semplice(t):
    """HTML -> testo con '|' al posto dei tag (formato usato per leggere rapporti e riepiloghi)."""
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S | re.I)
    i = t.find('id="content"')
    if i > 0:
        t = t[i:]
    s = re.sub(r"<[^>]+>", "|", t)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"(\| ?)+", "|", s)
    return s


def id_da_token(token):
    """'MjM2ODA1MzQ%3d-JOylFCPtSUc%3d' -> '23680534' (la prima parte del token è il numero in base64)."""
    p = unquote(token).split("-")[0]
    p += "=" * (-len(p) % 4)
    return base64.b64decode(p).decode("ascii")


def data_iso(s):
    m, d, y = (int(x) for x in s.strip().split("/"))
    return date(y, m, d).isoformat()


def leggi_green_sheet(t):
    # Il CDC cambia il markup secondo il browser (con o senza <font>): si leggono le due celle dopo il link, senza tag.
    righe = []
    for m in re.finditer(r'href="?InspectionDetailReport\.aspx\?ColI=([^ >"]+)"?>(.*?)</a>(.*?)</tr>', t, re.S):
        celle = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", m.group(3), re.S)]
        celle = [c for c in celle if c]
        righe.append((m.group(1), re.sub(r"<[^>]+>", "", m.group(2)), celle[0], celle[1]))
    out = []
    for coli, nave, d, voto in righe:
        nave = html.unescape(nave).strip()
        out.append({"coli": coli, "id_isp": id_da_token(coli), "nave": nave, "nave_n": norm(nave),
                    "data": data_iso(d), "voto": int(voto.strip())})
    return out


def leggi_elenchi(t):
    def opzioni(nome):
        m = re.search(r'<select[^>]*name="ctl00\$ContentPlaceHolder1\$' + nome + r'"[^>]*>(.*?)</select>', t, re.S)
        return {v: html.unescape(n).strip() for v, n in re.findall(r'<option[^>]*value="([^"]*)"[^>]*>(.*?)</option>', m.group(1), re.S) if v != "0"}
    return opzioni("lbox_RegisteredName"), opzioni("lbox_CruiselineName")


def leggi_storia(t):
    """Righe dei risultati di ricerca: nave, compagnia, data, voto, token del rapporto. Dalla più recente."""
    righe = re.findall(r'<td align="left">(.*?)</td><td align="left">(.*?)</td><td align="center">(.*?)</td><td align="center">(.*?)</td>'
                       r'.*?InspectionScoresAll\.aspx\?ColV=([^"]+)".*?InspectionDetailReport\.aspx\?ColI=([^"]+)"', t, re.S)
    out = []
    for nave, comp, d, voto, colv, coli in righe:
        out.append({"nave": html.unescape(nave).strip(), "compagnia": html.unescape(comp).strip(), "data": data_iso(d),
                    "voto": int(voto.strip()), "coli": coli, "id_isp": id_da_token(coli), "id_nave": id_da_token(colv)})
    out.sort(key=lambda x: (x["data"], x["id_isp"]), reverse=True)
    return out


def navi_da_pubblicare(navi, storie, verdi):
    """Restituisce {id_nave: 'attiva' | 'archiviata'} per le navi che avranno una pagina."""
    ultime = {v["id_isp"] for v in verdi}
    out = {}
    for id_nave, st in storie.items():
        if not st:
            continue
        if st[0]["id_isp"] in ultime:
            out[id_nave] = "attiva"
        elif st[0]["data"] >= ARCHIVIATE_DAL and len(st) >= ARCHIVIATE_MIN_ISPEZIONI:
            out[id_nave] = "archiviata"
    return out
