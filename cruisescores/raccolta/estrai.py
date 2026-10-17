"""Legge le pagine del CDC in cruisescores/cache/ e scrive i dati puliti in cruisescores/dati/.

Uso (dalla radice del repository, dopo scarica.py):
    python3 cruisescores/raccolta/estrai.py

Scrive:
    dati/navi.json      una voce per nave pubblicata: nome, compagnia, stato (attiva/archiviata), storia completa delle ispezioni
    dati/rapporti.json  le ultime N_RAPPORTI ispezioni di ogni nave: punti tolti per voce e infrazioni per esteso (senza nomi di persone)
    dati/epidemie.json  epidemie gastrointestinali pubblicate dal CDC (2023-oggi), collegate alle navi quando il nome coincide
    dati/ispezioni.json tutte le ispezioni di tutte le navi del modulo: [data, voto, nave, compagnia CDC, slug della pagina o ""]
    dati/escluse.json   navi del modulo CDC senza pagina, con il motivo
    dati/fonti.json     date (scarico, ultima ispezione), conteggi, controlli sulle pagine informative del CDC
Esce con errore se un controllo di coerenza non torna (es. 100 - punti tolti diverso dal voto).
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune as C  # noqa: E402

ERRORI = []
AVVISI = []


def slug(t):
    t = t.lower().replace("&", " and ").replace("'", "").replace("’", "").replace(".", "")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


# ------------------------------------------------------------------ testo dei rapporti
# Nel database del CDC gli apostrofi e i simboli dei gradi sono spesso diventati "?": si ripristinano solo i casi evidenti.
def pulisci(s):
    s = s.replace("\xa0", " ").replace("\r", " ")
    s = re.sub(r"(?<=[A-Za-z0-9])\?(?=s\b)", "’", s)                 # inspector?s -> inspector’s
    s = re.sub(r"(?<=[a-z]s)\?(?= [a-z])", "’", s)                   # manufacturers? recommendations
    s = re.sub(r"(?<=[A-Za-z])\?(?=(t|re|ll|ve|d|m)\b)", "’", s)     # don?t, they?re
    s = re.sub(r"(?<=\d)\s?\?(?=[CF]\b)", "°", s)                    # 128?F -> 128°F
    s = re.sub(r"(?:(?<=\s)|^)\?([^?\s][^?]{0,60}?)\?(?=[\s.,;:)]|$)", r"“\1”", s)  # ?Do not move? -> “Do not move”
    s = re.sub(r"(?<=\s)\?(?=\s)", "–", s)                          # Deck 10 ? Aqualina -> Deck 10 – Aqualina
    s = re.sub(r"(?<=[a-z])\?(?=[a-z])", "—", s)                       # items?such as -> items—such as
    s = re.sub(r"(?<=\d)\?(?=\d)|(?<=[a-z])\?(?=[A-Z][a-z])", "–", s)       # 0700?1100, February?April
    s = re.sub(r"(?<=\bO)\?(?=[A-Z][a-z])", "’", s)                    # O?Sheehan’s -> O’Sheehan’s
    s = re.sub(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\?(?=\d)", r"\1–", s)  # 19 April?3 May
    s = re.sub(r"\s+", " ", s).strip()
    return s


# Nomi di persone: il CDC non dovrebbe pubblicarne, ma per sicurezza si cercano titoli seguiti da un nome proprio e si tolgono.
# Solo titoli di cortesia o di grado seguiti da una parola con la maiuscola (es. "Mr. Rossi", "Captain Smith"): i ruoli
# ("the chief officer", "Officer Mess", "Supervisor Knowledge") non sono nomi e restano. verifica.py ricontrolla il testo pubblicato.
_TITOLI = r"(?:Mr|Mrs|Ms|Miss|Dr|Capt|Captain)"
_NON_NOMI = r"(?!On\b|In\b|The\b|And\b|Of\b|At\b|Was\b|Were\b|Is\b|Did\b|Had\b|Stated\b|Said\b|Mess\b|Office\b|Cabin\b|Deck\b|Bridge\b|Table\b|Galley\b|Pantry\b)"
RE_NOME = re.compile(r"\b" + _TITOLI + r"\.?\s+" + _NON_NOMI + r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)")


NON_PERSONE = {"Dr. Inks"}  # nomi di locali di bordo che sembrano nomi di persona (bar "Dr. Inks, PH.d." su Carnival Jubilee)
# nomi citati tra virgolette ("a passenger named 'Jack'", "'John S.'"): nome proprio + iniziale, o dopo "named"/"called"
RE_NOME_2 = re.compile(r"(?<=\bnamed )['‘“]?[A-Z][a-z]+(?: [A-Z]\.)?['’”]?|['‘“][A-Z][a-z]+ [A-Z]\.['’”]")


def togli_nomi(s, dove):
    def sost(m):
        if m.group(0) in NON_PERSONE:
            return m.group(0)
        AVVISI.append(f"{dove}: tolto un possibile nome di persona ('{m.group(0)}')")
        return m.group(0)[: m.start(1) - m.start(0)].rstrip() + " [name removed]"

    def sost2(m):
        AVVISI.append(f"{dove}: tolto un possibile nome di persona ('{m.group(0)}')")
        return "[name removed]"
    return RE_NOME_2.sub(sost2, RE_NOME.sub(sost, s))


def leggi_rapporto(det, summ, id_isp):
    """Rapporto (infrazioni) + riepilogo (punti per voce). Restituisce un dizionario o None se illeggibile."""
    t1, t2 = C.testo_semplice(det), C.testo_semplice(summ)
    m = re.search(r"Cruise Ship:\|(.*?)\|Cruise Line:\|(.*?)\|Inspection Date:\|(.*?)\|Inspection Score:\|(\d+)", t1)
    if not m:
        ERRORI.append(f"rapporto {id_isp}: intestazione illeggibile")
        return None
    nave, comp, d, voto = m.group(1).strip(), m.group(2).strip(), C.data_iso(m.group(3)), int(m.group(4))
    voci = []
    blocchi = re.split(r"<B>Item No\.:</B>", det)[1:]
    for b in blocchi:
        def campo(nome):
            mm = re.search(r"<B>" + nome + r":</B>(.*?)</font>", b, re.S)
            if not mm:
                return ""
            x = re.sub(r"<br\s*/?>", " ", mm.group(1), flags=re.I)
            x = re.sub(r"<[^>]+>", "", x)
            import html as _h
            return pulisci(_h.unescape(x))
        num = re.sub(r"<[^>]+>", "", b.split("</font>")[0]).strip()
        sito = campo("Site")
        viol = togli_nomi(campo("Violation"), f"rapporto {id_isp}")
        sito = togli_nomi(sito, f"rapporto {id_isp}")
        voci.append([num.zfill(2) if num.isdigit() else num, sito, viol])
    punti = []
    righe = re.findall(r"<tr[^>]*>\s*<td[^>]*>\s*(\d{1,2}[A-Za-z]?)\s*</td>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>\s*(\d+)\s*</td>\s*</tr>", summ, re.S)
    import html as _h
    for num, desc, p in righe:
        punti.append([num.zfill(2) if num.isdigit() else num, pulisci(_h.unescape(re.sub(r"<[^>]+>", "", desc))), int(p)])
    tolti = sum(p for _, _, p in punti)
    if 100 - tolti != voto:
        ERRORI.append(f"rapporto {id_isp} ({nave} {d}): voto {voto} ma punti tolti {tolti}")
    if not voci and voto < 100:
        AVVISI.append(f"rapporto {id_isp} ({nave} {d}): voto {voto} senza infrazioni elencate")
    return {"nave": nave, "compagnia": comp, "data": d, "voto": voto, "punti": punti, "voci": voci}


# ------------------------------------------------------------------ epidemie
def leggi_epidemie():
    out = []
    import html as _h
    for nome in ("epidemie", "epidemie-2025-2024", "epidemie-2023"):
        f = C.CACHE / "info" / f"{nome}.html"
        if not f.exists():
            AVVISI.append(f"pagina CDC {nome} non in cache: epidemie incomplete")
            continue
        t = f.read_text(encoding="utf-8", errors="replace")
        for tab in re.findall(r"<table.*?</table>", t, re.S):
            cap = re.search(r"<caption.*?</caption>", tab, re.S)
            cap = re.sub(r"<[^>]+>", "", cap.group(0)).strip() if cap else ""
            anno = re.search(r"(20\d\d)", cap)
            if not anno:
                continue
            anno = int(anno.group(1))
            if any(e["anno"] == anno for e in out):
                continue  # la tabella del 2023 compare in due pagine
            for riga in re.findall(r"<tr.*?</tr>", tab, re.S):
                celle_html = re.findall(r"<td[^>]*>(.*?)</td>", riga, re.S)
                if len(celle_html) < 4:
                    continue
                celle = [re.sub(r"\s+", " ", _h.unescape(re.sub(r"<[^>]+>", "", c))).strip() for c in celle_html]
                if {"cruise line", "cruise ship", "sailing dates"} & {c.lower() for c in celle} or not celle[1]:
                    continue  # riga d'intestazione (il CDC la scrive con <td>)
                link = re.search(r'href="([^"]+)"', riga)
                url = link.group(1) if link else ""
                if url.startswith("/"):
                    url = "https://www.cdc.gov" + url
                e = {"anno": anno, "compagnia": celle[0], "nave": celle[1], "date": celle[2].replace("–", "–"), "url": url}
                if len(celle) >= 7:
                    e.update({"agente": celle[4], "passeggeri": celle[5], "equipaggio": celle[6]})
                else:
                    e["agente"] = celle[3]
                out.append(e)
    return out


def main():
    oggi = date.today().isoformat()
    g = (C.CACHE / "greensheet.html").read_text(encoding="utf-8", errors="replace")
    verdi = C.leggi_green_sheet(g)
    navi_mod, comp_mod = C.leggi_elenchi((C.CACHE / "search.html").read_text(encoding="utf-8", errors="replace"))
    storie = {}
    for id_nave in navi_mod:
        f = C.CACHE / "navi" / f"{id_nave}.html"
        if f.exists():
            storie[id_nave] = C.leggi_storia(f.read_text(encoding="utf-8", errors="replace"))
        else:
            ERRORI.append(f"storia della nave {id_nave} ({navi_mod[id_nave]}) non scaricata")
    scelte = C.navi_da_pubblicare(navi_mod, storie, verdi)

    # ogni riga del Green Sheet deve corrispondere all'ultima ispezione di una nave pubblicata, con stessa data e voto
    per_isp = {st[0]["id_isp"]: (k, st[0]) for k, st in storie.items() if st}
    for v in verdi:
        if v["id_isp"] not in per_isp:
            ERRORI.append(f"Green Sheet: {v['nave']} ({v['data']}) non trovata nelle storie")
            continue
        k, x = per_isp[v["id_isp"]]
        if (x["data"], x["voto"]) != (v["data"], v["voto"]):
            ERRORI.append(f"Green Sheet: {v['nave']} {v['data']} {v['voto']} diverso dalla storia {x['data']} {x['voto']}")

    nomi_curati = json.loads((C.DATI / "compagnie.json").read_text(encoding="utf-8"))
    navi, rapporti, escluse = {}, {}, []
    slugs = {}
    for id_nave, st in storie.items():
        nome_mod = navi_mod[id_nave]
        if id_nave not in scelte:
            if not st:
                escluse.append([nome_mod, "", "", 0, "nessuna ispezione nel modulo"])
            else:
                motivo = (f"archiviata: ultima ispezione {st[0]['data']} (prima del {C.ARCHIVIATE_DAL})" if st[0]["data"] < C.ARCHIVIATE_DAL
                          else f"archiviata: solo {len(st)} ispezioni")
                escluse.append([nome_mod, st[0]["compagnia"], st[0]["data"], len(st), motivo])
            continue
        if any(x["id_nave"] != id_nave for x in st):
            ERRORI.append(f"nave {id_nave}: righe di altre navi nella storia")
        nome = st[0]["nave"].strip()
        # il Green Sheet e i risultati a volte usano maiuscole diverse ("Wonder Of The Seas"): si preferisce il nome del modulo
        if C.norm(nome) == C.norm(nome_mod):
            nome = nome_mod
        s = slug(nome)
        if s in slugs:
            ERRORI.append(f"slug duplicato {s}: {slugs[s]} e {id_nave}")
        slugs[s] = id_nave
        comp = st[0]["compagnia"]
        if comp not in nomi_curati:
            AVVISI.append(f"compagnia senza nome curato in dati/compagnie.json: '{comp}' (uso il nome del CDC)")
        altri_nomi = sorted({x["nave"] for x in st if C.norm(x["nave"]) != C.norm(nome)})
        altre_comp = sorted({x["compagnia"] for x in st if x["compagnia"] != comp})
        ids_rapp = []
        for x in st[:C.N_RAPPORTI]:
            det = C.CACHE / "rapporti" / f"{x['id_isp']}.detail.html"
            summ = C.CACHE / "rapporti" / f"{x['id_isp']}.summary.html"
            if not (det.exists() and summ.exists()):
                AVVISI.append(f"{nome}: rapporto {x['id_isp']} del {x['data']} non in cache")
                continue
            r = leggi_rapporto(det.read_text(encoding="utf-8", errors="replace"), summ.read_text(encoding="utf-8", errors="replace"), x["id_isp"])
            if r is None:
                continue
            if (r["data"], r["voto"]) != (x["data"], x["voto"]):
                ERRORI.append(f"{nome}: rapporto {x['id_isp']} dice {r['data']} {r['voto']}, la storia {x['data']} {x['voto']}")
            rapporti[x["id_isp"]] = r
            ids_rapp.append(x["id_isp"])
        navi[s] = {"id": id_nave, "nome": nome, "compagnia": comp, "stato": scelte[id_nave],
                   "altri_nomi": altri_nomi, "altre_compagnie": altre_comp,
                   "storia": [[x["data"], x["voto"], x["id_isp"]] for x in st], "rapporti": ids_rapp}

    # tutte le ispezioni di tutte le navi del modulo (anche quelle senza pagina), per le pagine degli anni e delle bocciature
    slug_per_id = {n["id"]: s for s, n in navi.items()}
    ispezioni = sorted(([x["data"], x["voto"], x["nave"], x["compagnia"], slug_per_id.get(k, "")] for k, st in storie.items() for x in st),
                       key=lambda r: (r[0], r[2]), reverse=True)

    # epidemie: collegate alla nave se il nome (o il nome senza il marchio davanti, es. "Insignia" per "Oceania Insignia") coincide
    epid = leggi_epidemie()
    per_nome = {}
    for s, n in navi.items():
        for nm in [n["nome"]] + n["altri_nomi"]:
            per_nome.setdefault(C.norm(nm), set()).add(s)
    for e in epid:
        k = C.norm(e["nave"])
        cand = per_nome.get(k, set())
        if not cand:
            cand = {s for s, n in navi.items() if C.norm(n["nome"]).endswith(" " + k) and len(k) > 4}
        e["slug"] = next(iter(cand)) if len(cand) == 1 else ""
        if not e["slug"]:
            AVVISI.append(f"epidemia {e['anno']} {e['nave']}: nessuna nave pubblicata con questo nome (mostrata senza link)")

    # controlli sulle pagine informative citate
    info = {}
    faq_f = C.CACHE / "info" / "faq.html"
    if faq_f.exists():
        faq = faq_f.read_text(encoding="utf-8", errors="replace")
        info["faq_85"] = "85 or below" in faq
        info["faq_due_ispezioni"] = "two unannounced inspections" in faq
        if not (info["faq_85"] and info["faq_due_ispezioni"]):
            ERRORI.append("FAQ del CDC cambiata: soglia 85 o 'two unannounced inspections' non trovate")
    else:
        ERRORI.append("FAQ del CDC non in cache (lanciare scarica.py)")
    if "85 or lower are NOT satisfactory" not in g:
        ERRORI.append("Green Sheet: la frase sulla soglia (85 or lower) non c'è più")

    tutte_date = [x[0] for n in navi.values() for x in n["storia"]]
    scaricato = (C.CACHE / "scaricato_il.txt").read_text().strip() if (C.CACHE / "scaricato_il.txt").exists() else oggi
    info_date = {}
    for nome in ("faq", "otto-aree", "ispezioni", "epidemie"):
        f = C.CACHE / "info" / f"{nome}.html"
        if f.exists():
            info_date[nome] = date.fromtimestamp(f.stat().st_mtime).isoformat()
    fonti = {
        "scaricato_il": scaricato,
        "green_sheet": {"navi": len(verdi), "ultima_ispezione": max(v["data"] for v in verdi)},
        "modulo": {"navi": len(navi_mod), "compagnie": len(comp_mod)},
        "pubblicate": {"attive": sum(1 for n in navi.values() if n["stato"] == "attiva"),
                       "archiviate": sum(1 for n in navi.values() if n["stato"] == "archiviata")},
        "ispezioni": len(tutte_date), "prima_ispezione": min(tutte_date), "rapporti": len(rapporti),
        "n_rapporti": C.N_RAPPORTI, "archiviate_dal": C.ARCHIVIATE_DAL, "archiviate_min": C.ARCHIVIATE_MIN_ISPEZIONI,
        "info_controllate_il": info_date, "controlli_info": info,
    }
    C.DATI.mkdir(exist_ok=True)
    dump = lambda nome, x: (C.DATI / nome).write_text(json.dumps(x, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")
    dump("navi.json", dict(sorted(navi.items())))
    dump("rapporti.json", dict(sorted(rapporti.items())))
    dump("epidemie.json", epid)
    dump("ispezioni.json", ispezioni)
    dump("escluse.json", sorted(escluse, key=lambda x: x[0].lower()))
    (C.DATI / "fonti.json").write_text(json.dumps(fonti, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for a in AVVISI[:80]:
        print("avviso:", a)
    if len(AVVISI) > 80:
        print(f"... altri {len(AVVISI) - 80} avvisi")
    print(f"Navi pubblicate: {fonti['pubblicate']}; ispezioni {len(tutte_date)}; rapporti {len(rapporti)}; epidemie {len(epid)}; escluse {len(escluse)}.")
    if ERRORI:
        print(f"{len(ERRORI)} ERRORI:")
        for e in ERRORI[:100]:
            print(" -", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
