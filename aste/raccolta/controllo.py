"""Controllo a campione: 10 lotti pubblicati confrontati con le fonti, senza usare la cache.

Uso: python3 aste/raccolta/controllo.py [--seme N]
Per ogni lotto (città diverse, con confronto OMI):
- PVP: rilegge la scheda pubblica del lotto (dettaglio) e confronta prezzo base, offerta minima, data e superficie nel testo;
  se il PVP non risponde lo dice (nessun dato inventato);
- OMI: rilegge dalla consultazione pubblica GEOPOI la scheda della zona e confronta minimo e massimo della tipologia usata.
Stampa una tabella Markdown da copiare in NOTE.md.
"""
import json
import random
import re
import sys
from html import unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aggiorna as A  # noqa: E402
import rete  # noqa: E402


def main():
    seme = int(sys.argv[sys.argv.index("--seme") + 1]) if "--seme" in sys.argv else 2026
    dati = json.loads((A.DATI / "lotti.json").read_text(encoding="utf-8"))
    omi = json.loads((A.DATI / "omi.json").read_text(encoding="utf-8"))
    con = [L for L in dati["lotti"] if L.get("sconto_min") is not None]
    random.seed(seme)
    random.shuffle(con)
    scelti, citta = [], set()
    for L in sorted(con, key=lambda L: L["comune"] not in ("Roma", "Milano", "Napoli", "Torino", "Palermo", "Bari", "Catania", "Genova")):
        if L["comune"] not in citta:
            scelti.append(L)
            citta.add(L["comune"])
        if len(scelti) == 10:
            break
    try:
        ep = rete.endpoint_pvp()
    except Exception:  # noqa: BLE001
        ep = json.loads((A.CACHE / "endpoint.json").read_text())
    righe = []
    for L in scelti:
        esito_pvp = "PVP non raggiungibile"
        try:
            g = rete.chiedi("GET", f"{ep['vendite']}/vendite/{L['id']}/restricted", tentativi=2)
            d = rete.dettaglio_pulito(g)
            g_, m_, a_ = d["dataVendita"].split("/")
            data = f"{a_}-{m_}-{g_}T{d['oraVendita']}"
            ok = [round(float(d["impoBaseAsta"])) == L["base"], round(float(d["impoOffertaMinima"])) == L["minima"], data == L["data"]]
            testo = " ".join([str(d["lotto"].get("descLotto") or "")] + [str(b.get("descrizione") or "") for b in d["beni"]])
            mq_ok = str(L["mq"]) in testo.replace(".", "") or str(L["mq"]) in testo or any(
                str(L["mq"]) == str(round(A.numero(b.get("superficie")) or 0)) for b in d["beni"])
            esito_pvp = ("ok" if all(ok) else "DIVERSO: " + ", ".join(n for n, v in zip(["base", "minima", "data"], ok) if not v)) + \
                        ("; m² nel testo ok" if mq_ok else "; m² DA VERIFICARE")
        except Exception as e:  # noqa: BLE001
            esito_pvp = f"PVP non raggiungibile ({str(e)[:40]})"
        cod, z = L["zona"]
        Z = omi["comuni"][cod]["zone"][z]
        tip = L["omi"][0]
        esito_omi = "?"
        try:
            # coordinate non pubblicate: si usa il centro fittizio, la scheda dipende solo da comune, zona e semestre
            t = rete.chiedi("GET", f"{rete.GEOPOI}/zoneomi.php?richiesta=3&codcom={cod}")
            link = next(x["LINK_ZONA"] for x in t if x["ZONA"] == z)
            html = rete.chiedi("GET", f"{rete.GEOPOI}/stampaomi.php?{cod}/{link}/{omi['semestre']}/R/{z}/0/0", testo=True)
            celle = [re.sub(r"\s+", " ", unescape(c)).strip() for c in re.sub(r"<[^>]+>", "|", html).split("|") if c.strip()]
            i = next(k for k in range(len(celle) - 3) if celle[k] == tip and celle[k + 1].lower() == L["omi"][4])
            vmin, vmax = int(celle[i + 2]), int(celle[i + 3])
            esito_omi = "ok" if (vmin, vmax) == (L["omi"][1], L["omi"][2]) else f"DIVERSO ({vmin}-{vmax})"
        except Exception as e:  # noqa: BLE001
            esito_omi = f"non verificato ({str(e)[:40]})"
        n = lambda x: f"{x:,}".replace(",", ".")  # noqa: E731
        righe.append(f"| [{L['id']}](https://pvp.giustizia.it/pvp/it/detail_annuncio.page?idAnnuncio={L['id']}) | {L['comune']}"
                     f"{', ' + L['via'] if L.get('via') else ''} | {n(L['base'])} / {n(L['minima'])} | {L['data'][:10]} | {L['mq']} | "
                     f"{z}: {tip.lower()} {n(L['omi'][1])}-{n(L['omi'][2])} (media {n(L['omi'][3])}) | "
                     f"{L['sconto_min']}% | {esito_pvp} | {esito_omi} |")
    print("| Lotto PVP | Dove | Base / minima € | Asta | m² | Zona OMI e valori €/m² | Sconto min. | Controllo PVP | Controllo OMI |")
    print("|---|---|---|---|---|---|---|---|---|")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
