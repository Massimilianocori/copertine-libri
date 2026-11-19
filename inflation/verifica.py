"""Controlli di Inflation Calculator (dati, motore, pagine, monetizzazione, browser).

I controlli tedeschi (Destatis, pagine /de/, casi DE nel browser) girano solo con genera.SEZIONE_DE = True; da spenta si controlla
invece che nessun file di sito/ nomini la sezione tedesca (vedi sezione_de_spenta()).

Uso (dalla radice del repository):
    python3 inflation/verifica.py            # dati + motore JS = Python + pagine
    python3 inflation/verifica.py --browser  # in più Playwright (375 e 1280 px, chiaro e scuro, casi del calcolatore)
Esce con codice 1 se c'è anche un solo errore.
"""
import json
import random
import re
import subprocess
import sys
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
sys.path.insert(0, str(RADICE))
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import genera as G  # noqa: E402
import pensione as PEN  # noqa: E402
import monetizzazione as MON  # noqa: E402
import motore as M  # noqa: E402
import serie  # noqa: E402

SEGNO_CHIAVE = "_".join(("sd", "live"))  # prefisso delle chiavi dello strumento dei volumi (scritto spezzato per non comparire nei file)

SITO = RADICE / "sito"
ERR, AVV, OK = [], [], []
S = G.S
DE = G.SEZIONE_DE
C = G.C if DE else {k: v for k, v in G.C.items() if k != "de"}  # da spenta il motore si controlla su USA e UK


def err(x):
    ERR.append(x)


def ok(x):
    OK.append(x)


# ---------------------------------------------------------------- 1. dati
def tolleranza(c, d0, d1, mezza_unita):
    """Scarto massimo (punti percentuali) tra un tasso calcolato da indici arrotondati e quello pubblicato dall'ufficio,
    che lo calcola dagli indici non arrotondati: errore di arrotondamento dei due indici + 0,05 di arrotondamento del tasso."""
    i0, i1 = M.indice(c, *d0), M.indice(c, *d1)
    return 100 * (i1 / i0) * (mezza_unita / i0 + mezza_unita / i1) + 0.051


def dati():
    # continuità
    for k, nome in ((("us", "USA CPI-U"), ("uk_cpi", "UK CPI"), ("uk_rpi", "UK RPI lungo"), ("uk_rpi87", "UK RPI 1987"))
                    + ((("de_vpi", "DE VPI"), ("de_west", "DE Ovest"), ("de", "DE verkettet")) if DE else ())):
        e = serie.continuita(S[k], nome)
        ERR.extend(e)
        if not e:
            a, m = sorted(S[k]["annuale"]), sorted(S[k]["mensile"])
            ok(f"continuità {nome}: anni {a[0]}-{a[-1]}, mesi {m[0][0]}-{m[0][1]:02d} … {m[-1][0]}-{m[-1][1]:02d}, mancanti dichiarati {len(S[k].get('mancanti', {}))}")
    if set(S["us"]["mancanti"]) != {(2025, 10)}:
        err(f"USA: mesi mancanti inattesi {S['us']['mancanti']}")
    # BLS: pagina dati = API, mese per mese
    api, api_manc = serie.bls_api()
    diff = [k for k in set(api) | set(S["us"]["mensile"]) if api.get(k) != S["us"]["mensile"].get(k)]
    if diff or set(api_manc) != set(S["us"]["mancanti"]):
        err(f"BLS: pagina dati e API diverse in {sorted(diff)[:5]} / mancanti {api_manc}")
    else:
        ok(f"BLS: pagina dati = API su {len(api)} mesi; ottobre 2025 assente in entrambe ({list(api_manc.values())[0]})")
    # medie annue ricalcolate
    for k, tol_vecchi in (("us", 0.1001), ("uk_cpi", 0.1001), ("uk_rpi", 0.25)) + ((("de_vpi", 0.1001), ("de_west", 0.1001)) if DE else ()):
        s, n, mx = S[k], 0, 0
        for y, v in s["annuale"].items():
            ms = [s["mensile"][(y, m)] for m in range(1, 13) if (y, m) in s["mensile"]]
            if len(ms) < 11 or (len(ms) == 11 and (y, 10) not in s.get("mancanti", {})):
                continue
            d = abs(sum(ms) / len(ms) - v)
            tol = 0.0006 if (k == "us" and y >= 2007) else tol_vecchi
            n += 1
            mx = max(mx, d)
            if d > tol:
                err(f"{k} {y}: media dei mesi {sum(ms) / len(ms):.4f} ≠ media annua pubblicata {v}")
        ok(f"{k}: {n} medie annue ricalcolate dai mesi, scarto massimo {mx:.4f}")
    # valori noti
    noti = [("us", 1913, 9.9), ("us", 1970, 38.8), ("us", 1980, 82.4), ("us", 2000, 172.2), ("us", 2020, 258.811), ("us", 2024, 313.689),
            ("uk_cpi", 2015, 100.0), ("uk_rpi87", 1987, 101.9)] + ([("de_vpi", 2020, 100.0)] if DE else [])
    for k, y, v in noti:
        if abs(S[k]["annuale"][y] - v) > 0.051:
            err(f"valore noto {k} {y}: {S[k]['annuale'][y]} invece di {v}")
    if abs(sum(S["uk_rpi87"]["mensile"][(1987, 1)] for _ in [0]) - 100.0) > 1e-9:
        err("RPI CHAW gennaio 1987 ≠ 100")
    if abs(S["uk_rpi"]["mensile"][(1974, 1)] - 100.0) > 1e-9:
        err("RPI CDKO gennaio 1974 ≠ 100")
    ok(f"{len(noti) + 2} valori noti (basi degli indici e medie annue BLS note) confermati")
    # calcolatore ufficiale BLS
    es = json.loads((RADICE / "dati" / "esempi_bls.json").read_text(encoding="utf-8"))["casi"]
    for c in es:
        a0, m0 = map(int, c["da"].split("-"))
        a1, m1 = map(int, c["a"].split("-"))
        r = M.calcola(C["us"], c["importo"], (a0, m0), (a1, m1))
        if c["risultato_ufficiale"] is None or abs(round(r["valore"], 2) - c["risultato_ufficiale"]) > 0.0051:
            err(f"calcolatore BLS {c}: nostro {r['valore']:.4f}")
    if len(es) < 10:
        err(f"calcolatore BLS: solo {len(es)} casi ufficiali (servono almeno 10, su decenni diversi)")
    ok(f"{len(es)} risultati del CPI Inflation Calculator ufficiale del BLS rifatti al centesimo")
    # ONS: tassi pubblicati
    cpi_r = S["uk_cpi_rate"]
    n, mx = 0, 0
    for (a, m), v in cpi_r["mensile"].items():
        t = M.tasso_12_mesi(C["uk_cpi"], a, m)
        if t is None:
            continue
        d = abs(t * 100 - v)
        n, mx = n + 1, max(mx, d)
        if d > tolleranza(C["uk_cpi"], (a - 1, m), (a, m), 0.05):
            err(f"UK CPI {a}-{m}: tasso calcolato {t * 100:.2f} ≠ ONS {v}")
    for a, v in cpi_r["annuale"].items():
        t = M.tasso_annuo(C["uk_cpi"], a)
        if t is not None and abs(t * 100 - v) > 0.15:
            err(f"UK CPI {a}: tasso annuo calcolato {t * 100:.2f} ≠ ONS {v}")
    ok(f"UK CPI: {n} tassi a 12 mesi calcolati = ONS D7G7 (scarto massimo {mx:.2f} punti, sempre entro l'arrotondamento degli indici a una cifra)")
    rpi_r = S["uk_rpi_rate"]
    n, mx = 0, 0
    for (a, m), v in rpi_r["mensile"].items():
        t = M.tasso_12_mesi(C["uk_rpi"], a, m)
        if t is None:
            continue
        d = abs(t * 100 - v)
        n, mx = n + 1, max(mx, d)
        if d > tolleranza(C["uk_rpi"], (a - 1, m), (a, m), 0.05 if a < 1988 else 0.2):
            err(f"UK RPI {a}-{m}: tasso dal CDKO {t * 100:.2f} ≠ ONS CZBH {v}")
    ok(f"UK RPI: {n} tassi a 12 mesi dal CDKO = ONS CZBH (scarto massimo {mx:.2f} punti)")
    rapp = [S["uk_rpi"]["mensile"][k] / v for k, v in S["uk_rpi87"]["mensile"].items()]
    if max(rapp) / min(rapp) - 1 > 0.0012:
        err(f"RPI: CDKO / CHAW non costante ({min(rapp):.4f}–{max(rapp):.4f})")
    else:
        ok(f"RPI: CDKO = CHAW × {sum(rapp) / len(rapp):.4f} su {len(rapp)} mesi (stessa serie, basi diverse)")
    if DE:
        dati_de()
    # fonti e frasi
    for fid, f in G.FONTI.items():
        if fid.startswith("_") or (not DE and fid in G.FONTI_DE):
            continue
        if f.get("http") != 200:
            err(f"fonte {fid}: HTTP {f.get('http')}")
        if f.get("trovate") and not all(f["trovate"].values()):
            err(f"fonte {fid}: frase non più presente")
        if fid.startswith(("ons", "destatis", "bls")) and fid != "bls_calc" and not f.get("licenza"):
            err(f"fonte {fid}: licenza non registrata")
        if not f.get("letto_il"):
            err(f"fonte {fid}: senza data di lettura")


def dati_de():
    """Destatis (solo con la sezione tedesca accesa)."""
    L, T = S["de_lange"], S["de_tabelle"]
    sov_m = [k for k in T["mensile"] if k in L["mensile"]]
    sov_a = [k for k in T["annuale"] if k in L["annuale"]]
    diff = [k for k in sov_m if L["mensile"][k] != T["mensile"][k]] + [k for k in sov_a if L["annuale"][k] != T["annuale"][k]]
    if diff or not sov_m:
        err(f"Destatis: lange Reihen e tabella attuale diverse in {diff[:5]}")
    else:
        ok(f"Destatis: lange Reihen = tabella attuale su {len(sov_m)} mesi e {len(sov_a)} anni in comune")
    R = S["de_rate_pubbl"]
    n = 0
    for a, v in R["vpi_jahr"].items():
        t = M.tasso_annuo(C["de"], a)
        if a >= 1992 and t is not None:
            n += 1
            if abs(t * 100 - v) > 0.1001:
                err(f"DE {a}: tasso dal VPI {t * 100:.2f} ≠ Destatis {v}")
    for (a, m), v in R["vpi_monat"].items():
        t = M.tasso_12_mesi(C["de"], a, m)
        n += 1
        if t is None or abs(t * 100 - v) > 0.1001:
            err(f"DE {a}-{m}: tasso mensile {t} ≠ Destatis {v}")
    for a, v in R["west_jahr"].items():
        w = S["de_west"]["annuale"]
        if a - 1 in w and a in w:
            n += 1
            if abs((w[a] / w[a - 1] - 1) * 100 - v) > 0.1001:
                err(f"DE Ovest {a}: tasso {(w[a] / w[a - 1] - 1) * 100:.2f} ≠ Destatis {v}")
    ok(f"Destatis: {n} tassi pubblicati (annui VPI e Ovest, mensili) rifatti dagli indici entro 0,1 punti")
    k = S["de"]["fattore"]
    if abs(S["de"]["annuale"][1990] - round(S["de_west"]["annuale"][1990] * k, 3)) > 1e-9 or S["de"]["annuale"][1991] != S["de_vpi"]["annuale"][1991]:
        err("DE: raccordo 1991 non applicato come descritto")
    # (revisione indipendente) fattore rifatto dall'anno di sovrapposizione e applicato a OGNI valore prima del 1991, anni e mesi
    k2 = S["de_vpi"]["annuale"][1991] / S["de_west"]["annuale"][1991]
    if abs(k - k2) > 1e-12 or f"{k2:.5f}" != "0.69551":
        err(f"DE: fattore di raccordo {k} ≠ VPI 1991 / Ovest 1991 = {k2:.5f} (se Destatis ha rivisto i dati, rileggere il testo della pagina)")
    sbagliati = [a for a, v in S["de_west"]["annuale"].items() if a < 1991 and abs(S["de"]["annuale"][a] - round(v * k2, 3)) > 1e-9]
    sbagliati += [x for x, v in S["de_west"]["mensile"].items() if x[0] < 1991 and abs(S["de"]["mensile"][x] - round(v * k2, 3)) > 1e-9]
    sbagliati += [x for x, v in S["de_vpi"]["annuale"].items() if S["de"]["annuale"][x] != v] + [x for x, v in S["de_vpi"]["mensile"].items() if S["de"]["mensile"][x] != v]
    if sbagliati or min(S["de"]["annuale"]) != 1962:
        err(f"DE: valori della serie verkettet diversi da Ovest × fattore o dal VPI: {sbagliati[:5]}")
    salto = S["de_vpi"]["mensile"][(1991, 1)] / (S["de_west"]["mensile"][(1991, 1)] * k2) - 1
    if abs(salto) > 0.006:
        err(f"DE: salto dic 1990 → gen 1991 del raccordo {salto:.4f} oltre lo 0,6 % (la pagina dice «rund 0,4 %»)")
    ok(f"DE: fattore di raccordo rifatto = {S['de_vpi']['annuale'][1991]} ÷ {S['de_west']['annuale'][1991]} = {k2:.5f}; "
       f"{sum(1 for a in S['de_west']['annuale'] if a < 1991)} anni e {sum(1 for x in S['de_west']['mensile'] if x[0] < 1991)} mesi prima del 1991 = Ovest × fattore; "
       f"scarto del raccordo a gennaio 1991 {salto * 100:.2f} %")


# ---------------------------------------------------------------- 2. motore JS = Python
def motore():
    js_file = next((SITO / "assets").glob("app.*.js"))
    js = js_file.read_text(encoding="utf-8")
    motore_js = js[:js.index("(function(){")]
    rnd = random.Random(7)
    casi = []
    for k in C:
        c = C[k]
        anni = list(range(c["a0"], c["a0"] + len(c["a"])))
        for _ in range(1500):
            def data():
                if rnd.random() < 0.5:
                    return [rnd.choice(anni), None]
                i = rnd.randrange(len(c["m"]))
                return [c["m0"][0] + (c["m0"][1] - 1 + i) // 12, (c["m0"][1] - 1 + i) % 12 + 1]
            casi.append([k, round(rnd.uniform(0, 100000), 2), data(), data(), (rnd.random() < 0.5) if k == "de" else None])
    casi += [["us", 100, [2025, 10], [2026, 10], None], ["us", 100, [1913, None], [1913, None], None], ["uk_rpi", 1, [1800, None], [2026, 9], None]]
    if DE:
        casi += [["de", 100, [1990, None], [2002, None], True], ["de", 100, [2005, None], [1980, None], False]]
    prog = motore_js + "\nvar C=" + json.dumps(C) + ";var K=" + json.dumps(casi) + (
        ";var o=K.map(function(x){var r=calcola(C[x[0]],x[1],[x[2][0],x[2][1]||undefined],[x[3][0],x[3][1]||undefined],x[4]);return r?r.valore:null;});"
        "process.stdout.write(JSON.stringify(o));")
    p = subprocess.run(["node", "-"], input=prog, capture_output=True, text=True)
    if p.returncode:
        err("node: " + p.stderr[:300])
        return
    js_out = json.loads(p.stdout)
    diversi = 0
    for (k, imp, da, a, v), j in zip(casi, js_out):
        r = M.calcola(C[k], imp, tuple(da), tuple(a), v)
        py = r["valore"] if r else None
        if (py is None) != (j is None) or (py is not None and abs(py - j) > 1e-6 * max(1, abs(py))):
            diversi += 1
            if diversi < 4:
                err(f"JS ≠ Python: {k} {imp} {da}→{a} {v}: {j} / {py}")
        if py is not None and py < 0:
            err("valore negativo")
    if not diversi:
        ok(f"motore JS pubblicato ({js_file.name}) = Python su {len(casi)} casi (ottobre 2025 USA = nessun risultato in entrambi)")


# ---------------------------------------------------------------- 3. pagine
TITOLI, DESCR = {}, {}
CONSIGLI = re.compile(r"\b(you should|should you|we recommend|best (account|plan|ira|401\(k\))|best investment|guaranteed? return|financial advice:|invest in|"
                      r"sollten Sie (kaufen|verkaufen|anlegen|investieren)|wir empfehlen|Anlagetipp)\b", re.I)


def _righe(rel):
    """Righe delle tabelle di una pagina: liste di celle (testo)."""
    t = (SITO / rel).read_text(encoding="utf-8")
    return [[re.sub(r"\s+", " ", testo(c)).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)] for r in re.findall(r"<tr.*?</tr>", t, re.S)]


def _pc(x):
    return float(x.replace("−", "-").replace("+", "").replace("%", "").replace("\xa0", "").replace("*", "").replace(",", ".").strip())


def tassi_pubblicati():
    """(revisione indipendente) Dove l'ufficio pubblica un tasso annuo, la pagina stampa quello pubblicato (non uno ricalcolato da indici
    arrotondati, che in 14 anni su 77 del RPI dava 0,1-0,2 punti di differenza) e due pagine non danno mai due tassi diversi per lo stesso anno."""
    cpi, rpi = S["uk_cpi_rate"]["annuale"], S["uk_rpi_rate"]["annuale"]
    n = 0
    for r in _righe("uk/inflation-rate-by-year/index.html"):
        if not r or not re.fullmatch(r"\d{4}", r[0]):
            continue
        y = int(r[0])
        if len(r) == 4:  # tabella CPI: anno, indice, tasso ONS, valore di 1 £
            n += 1
            if abs(_pc(r[2]) - cpi[y]) > 1e-9:
                err(f"UK tassi: CPI {y} stampato {r[2]} ≠ ONS D7G7 {cpi[y]}")
        elif len(r) == 3:  # tabella RPI
            n += 1
            atteso = rpi[y] if y in rpi else round(M.tasso_annuo(C["uk_rpi"], y) * 100, 1)
            if abs(_pc(r[2]) - atteso) > 1e-9 or (("*" in r[2]) != (y not in rpi)):
                err(f"UK tassi: RPI {y} stampato {r[2]} ≠ {'ONS CZBH' if y in rpi else 'calcolato'} {atteso}")
    for r in _righe("uk/rpi-calculator/index.html"):
        if r and re.fullmatch(r"\d{4}", r[0]) and len(r) == 3:
            n += 1
            y = int(r[0])
            if abs(_pc(r[1]) - rpi[y]) > 1e-9 or abs(_pc(r[2]) - cpi[y]) > 1e-9:
                err(f"RPI calculator: {y} stampato {r[1]} / {r[2]} ≠ ONS {rpi[y]} / {cpi[y]}")
    R = S["de_rate_pubbl"]
    for r in (_righe("de/inflationsrate-deutschland/index.html") if DE else []):
        if r and re.fullmatch(r"\d{4}", r[0]) and len(r) == 3:
            y = int(r[0])
            n += 1
            atteso = R["west_jahr"][y] if y <= 1991 else R["vpi_jahr"][y]
            if abs(_pc(r[2]) - atteso) > 1e-9:
                err(f"DE Inflationsrate: {y} stampato {r[2]} ≠ Destatis {atteso}")
    us = 0
    for r in _righe("us/inflation-rate-by-year/index.html"):
        if r and re.fullmatch(r"\d{4}", r[0]) and len(r) == 5:
            y = int(r[0])
            us += 1
            a, d = S["us"]["annuale"], S["us"]["mensile"]
            if abs(_pc(r[2]) - round((a[y] / a[y - 1] - 1) * 100, 1)) > 1e-9 or abs(_pc(r[3]) - round((d[(y, 12)] / d[(y - 1, 12)] - 1) * 100, 1)) > 1e-9:
                err(f"US tassi: {y} stampato {r[2]} / {r[3]} ≠ indici BLS")
    if n < (330 if DE else 270) or us < 112:
        err(f"tassi stampati: lette solo {n} righe UK/DE e {us} USA (struttura delle tabelle cambiata?)")
    ok(f"tassi annui stampati: {n} righe {'UK/DE' if DE else 'UK'} = tassi pubblicati da ONS (D7G7, CZBH){' e Destatis' if DE else ''} (prima del 1949 RPI calcolato e segnato con *); "
       f"{us} anni USA × 2 = indici BLS")
    # nota sulla Banca d'Inghilterra con l'esempio rifatto a mano
    a, y0, y1, _, _, boe = G.BOE
    nostro = G.soldi(a * S["uk_rpi"]["annuale"][y1] / S["uk_rpi"]["annuale"][y0], "GBP")
    for rel in ("uk/index.html", "uk/rpi-calculator/index.html"):
        vis = re.sub(r"\s+", " ", testo((SITO / rel).read_text(encoding="utf-8")))
        if "Bank of England" not in vis or nostro not in vis or G.soldi(boe, "GBP") not in vis or "RPI long-run series for both dates" not in vis:
            err(f"{rel}: manca la spiegazione CPI/RPI con il confronto con la Banca d'Inghilterra ({G.soldi(boe, 'GBP')} contro {nostro})")
    if not all(G.FONTI.get("boe_calc", {}).get("trovate", {"": False}).values()):
        err("boe_calc: le frasi citate non sono più nella pagina della Banca d'Inghilterra")
    if DE:
        de = re.sub(r"\s+", " ", testo((SITO / "de/inflationsrechner/index.html").read_text(encoding="utf-8")))
        for frase in ("0,69551", "eigene Berechnung", "kein amtlicher Index", "1 Euro = 1,95583 DM", "nimmt der Rechner den Jahresdurchschnitt"):
            if frase not in de:
                err(f"de/inflationsrechner: manca «{frase}»")
    home = re.sub(r"\s+", " ", testo((SITO / "index.html").read_text(encoding="utf-8")))
    for frase in ("annual average", "One month is missing: October 2025", "does not invent a value"):
        if frase not in home:
            err(f"home: manca «{frase}»")
    ok(f"spiegazioni presenti: CPI→RPI senza concatenare e differenza con la Banca d'Inghilterra ({G.soldi(boe, 'GBP')} contro {nostro}), "
       f"{'raccordo tedesco come calcolo nostro, ' if DE else ''}ottobre 2025, media annua o mese")


def pagine_anno():
    """(revisione indipendente) Ogni pagina anno ha il suo valore dal motore e numeri suoi: nessuna coppia con la stessa impronta
    (media annua + 12 mesi + tasso); gli anni con la stessa media annua lo dichiarano e si collegano."""
    impronte, n_gemelli = {}, 0
    for y in G.ANNI_US:
        t = (SITO / "us" / f"{y}-dollars-today" / "index.html").read_text(encoding="utf-8")
        vis = re.sub(r"\s+", " ", testo(t))
        atteso = G.soldi(G.vale_oggi("us", y), "USD")
        if f'<span class="big">{atteso}</span>' not in t:
            err(f"pagina {y}: valore di $1 non uguale al motore ({atteso})")
        mesi = tuple(S["us"]["mensile"].get((y, m)) for m in range(1, 13))
        for m, v in enumerate(mesi, 1):
            if v and f"<td>{G.MESI['en'][m - 1]}</td><td class=\"n\">{G.idx(v)}</td>" not in t:
                err(f"pagina {y}: indice di {G.MESI['en'][m - 1]} ≠ BLS {v}")
        imp = (S["us"]["annuale"][y], mesi, M.tasso_annuo(C["us"], y))
        if imp in impronte:
            err(f"pagine anno {impronte[imp]} e {y}: stessi numeri (pagina doppia)")
        impronte[imp] = y
        gemelli = [a for a in G.ANNI_US if a != y and S["us"]["annuale"][a] == S["us"]["annuale"][y]]
        n_gemelli += bool(gemelli)
        for a in gemelli:
            if f'href="/us/{a}-dollars-today/">{a}</a>' not in t or "annual average CPI-U was also" not in vis:
                err(f"pagina {y}: non dichiara la stessa media annua del {a}")
        if len(vis.split()) < 450:
            err(f"pagina {y}: solo {len(vis.split())} parole")
    ok(f"{len(impronte)} pagine anno: valore di $1 e 12 indici mensili = BLS, nessuna con gli stessi numeri di un'altra; "
       f"{n_gemelli} anni con una media annua uguale a un altro anno lo dichiarano")

PAROLE_EN = re.compile(r"\b(the|and|with|from|year|price|prices|which|this|that|calculator)\b", re.I)
_NOMI = [x[::-1] for x in ("edualc", "ciporhtna", "tpgtahc", "ianepo", "inimeg", "amall", "supo", "tennos", "ukiah")]  # nomi di modelli AI da non pubblicare (scritti al contrario: questo file non li contiene)
MODELLI = re.compile(r"\b(" + "|".join(_NOMI) + r"|gpt-?\d)\b", re.I)


def testo(html_):
    return unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b.*?</\1>", " ", html_, flags=re.S)))


def pagine():
    files = sorted(SITO.rglob("*.html"))
    canon, noindex = {}, []
    tutti_link = set()
    for f in files:
        rel = str(f.relative_to(SITO))
        t = f.read_text(encoding="utf-8")
        percorso = "" if rel == "index.html" else rel[:-len("index.html")] if rel.endswith("index.html") else rel
        tit = re.search(r"<title>(.*?)</title>", t).group(1)
        des = re.search(r'<meta name="description" content="([^"]*)"', t).group(1)
        if re.search(r'name="robots" content="noindex"', t):
            noindex.append(rel)
        else:
            m = re.search(r'<link rel="canonical" href="([^"]+)"', t)
            if not m or m.group(1) != f"{G.URL_SITO}/{percorso}":
                err(f"{rel}: canonical errato")
            canon[m.group(1)] = rel
            if not (20 <= len(unescape(tit)) <= 65):
                err(f"{rel}: titolo di {len(unescape(tit))} caratteri")
            if not (70 <= len(unescape(des)) <= 165):
                err(f"{rel}: descrizione di {len(unescape(des))} caratteri")
        TITOLI.setdefault(unescape(tit), []).append(rel)
        DESCR.setdefault(unescape(des), []).append(rel)
        vis = re.sub(r"\s+", " ", testo(t))
        # (revisione indipendente) attribuzione della fonte in ogni pagina con i suoi dati, avviso, niente consigli, niente refusi noti
        if rel.startswith("uk/") and "Source: Office for National Statistics licensed under the Open Government Licence v.3.0" not in vis:
            err(f"{rel}: manca l'attribuzione OGL dell'ONS")
        if rel.startswith("uk/") and "nationalarchives.gov.uk/doc/open-government-licence/version/3/" not in t:
            err(f"{rel}: manca il link alla licenza OGL v3.0")
        if rel.startswith("de/") and not ("Quelle: Statistisches Bundesamt (Destatis)" in vis and "mit Quellenangabe gestattet" in vis
                                          and "Datenlizenz Deutschland – Namensnennung – Version 2.0" in vis and "govdata.de/dl-de/by-2-0" in t):
            err(f"{rel}: citazione Destatis / dl-de/by-2-0 incompleta")
        if rel.startswith("us/") and "U.S. Bureau of Labor Statistics" not in vis:
            err(f"{rel}: manca la fonte BLS")
        if rel != "404.html" and not ("not financial or investment advice" in vis or "keine Finanz- oder Anlageberatung" in vis):
            err(f"{rel}: manca l'avviso «non è consulenza finanziaria»")
        m = CONSIGLI.search(vis)
        if m:
            err(f"{rel}: frase da consiglio finanziario «{m.group(0)}»")
        m = re.search(r"[+−-]0[.,]0+\s?%", vis)
        if m:
            err(f"{rel}: zero con il segno «{m.group(0)}»")
        m = re.search(r"December (\d{4}) to December \1\b", vis)
        if m:
            err(f"{rel}: confronto di un dicembre con sé stesso «{m.group(0)}»")
        if t.count("<h1") != 1:
            err(f"{rel}: {t.count('<h1')} h1")
        if "gc.zgo.at/count.js" not in t:
            err(f"{rel}: manca GoatCounter")
        if "{" in testo(t).replace("{}", "") and re.search(r"\{[a-z_]+\}", testo(t)):
            err(f"{rel}: segnaposto non sostituito {re.search(r'{[a-z_]+}', testo(t)).group(0)}")
        if MODELLI.search(t):
            err(f"{rel}: nome di modello AI ({MODELLI.search(t).group(0)})")
        if SEGNO_CHIAVE in t:
            err(f"{rel}: chiave nel sito")
        for m in re.finditer(r'href="(/[^"#?]*)', t):
            tutti_link.add((rel, m.group(1)))
        # JSON-LD
        lds = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)]
        for ld in lds:
            if ld.get("@type") == "FAQPage":
                vis = re.findall(r'<div class="faq"><h3>(.*?)</h3><p>(.*?)</p></div>', t, re.S)
                if len(vis) != len(ld["mainEntity"]):
                    err(f"{rel}: FAQ visibili {len(vis)} ≠ JSON-LD {len(ld['mainEntity'])}")
                for (q, a), e in zip(vis, ld["mainEntity"]):
                    if unescape(q) != e["name"] or re.sub(r"\s+", " ", testo(a)).strip() != re.sub(r"\s+", " ", e["acceptedAnswer"]["text"]).strip():
                        err(f"{rel}: FAQ JSON-LD diversa dal testo visibile ({e['name'][:40]})")
        # lingua tedesca
        if rel.startswith("de/"):
            if 'lang="de-DE"' not in t:
                err(f"{rel}: lang non tedesco")
            main = t[t.index("<main"):t.index("</main>")]
            main = re.sub(r'<section class="fonti-box".*?</section>', "", main, flags=re.S)
            main = re.sub(r'<ul class="griglia">.*?</ul>', "", main, flags=re.S)
            main = re.sub(r'<script type="application/json".*?</script>', "", main, flags=re.S)
            parole = PAROLE_EN.findall(testo(main))
            if parole:
                err(f"{rel}: parole inglesi nel testo tedesco: {sorted(set(parole))}")
            for sbagliata in ("Jahresdurchschnit ", "Inflationrate", "Verbraucherpreisindexes", " dass dass"):
                if sbagliata in testo(main):
                    err(f"{rel}: '{sbagliata}'")
    for nome, mappa in (("titolo", TITOLI), ("descrizione", DESCR)):
        for testo_, dove in mappa.items():
            if len(dove) > 1:
                err(f"{nome} uguale in {dove[:3]}: «{testo_[:60]}»")
    tassi_pubblicati()
    pagine_anno()
    pensione()
    riscaldamento()
    import verifica_2027 as V27  # sezioni /uk/…-2027/ e /rent-increase-cap/ (cifre GOV.UK e tetti agli affitti)
    pagine_2027 = V27.controlla(err, ok, G, SITO)
    # link interni
    rotti = set()
    for rel, l in tutti_link:
        p = SITO / l.lstrip("/")
        if not ((p / "index.html").exists() if l.endswith("/") else p.exists()):
            rotti.add(f"{rel} -> {l}")
    for r in sorted(rotti)[:10]:
        err(f"link rotto {r}")
    # sitemap
    sm = re.findall(r"<loc>([^<]+)</loc>", (SITO / "sitemap.xml").read_text(encoding="utf-8"))
    if set(sm) != set(canon) or len(sm) != len(set(sm)):
        err(f"sitemap ({len(sm)}) ≠ pagine con canonical ({len(canon)})")
    if noindex != ["404.html"]:
        err(f"pagine noindex inattese: {noindex}")
    attese = ["", "uk/", "uk/rpi-calculator/", "uk/inflation-rate-by-year/", "us/inflation-rate-by-year/"]
    attese += ["de/inflationsrechner/", "de/inflationsrate-deutschland/"] if DE else []
    attese += list(PEN.PAGINE.values())
    import riscaldamento as RIS
    attese += [k["slug"] for k in RIS.COMB.values()] + [RIS.percorso(c, n) for c, _, n, _, _ in RIS.pagine_stato(G)]
    attese += pagine_2027
    attese += [f"us/{y}-dollars-today/" for y in G.ANNI_US] + [f"us/{x}-dollars-in-{y}/" for x in G.IMPORTI_PAGINA for y in G.DECENNI_IMPORTO]
    mancano = [a for a in attese if f"{G.URL_SITO}/{a}" not in canon]
    if mancano:
        err(f"pagine mancanti {mancano[:5]}")
    ok(f"{len(files)} file HTML: {len(canon)} con canonical = sitemap, solo 404 noindex; {len(tutti_link)} link interni controllati, titoli, descrizioni, h1, JSON-LD")
    # file accessori
    for nome, cerca in (("robots.txt", f"Sitemap: {G.URL_SITO}/sitemap.xml"), (f"{G.CHIAVE_INDEXNOW}.txt", G.CHIAVE_INDEXNOW), ("netlify.toml", 'ignore = "git diff --quiet'),
                        ("ads.txt", "google.com, pub-")):
        if cerca not in (SITO / nome).read_text(encoding="utf-8"):
            err(f"{nome}: manca «{cerca}»")
    if not (SITO / "assets" / "og.png").exists():
        err("og.png assente")
    # FAQ da ricerche vere
    dom = json.loads((RADICE / "dati" / "domanda.json").read_text(encoding="utf-8"))
    vol = {}
    for r in dom["richieste"]:
        vol[(r["frase"].lower(), r["paese"])] = max(vol.get((r["frase"].lower(), r["paese"]), 0), r["volume"] or 0)
        for s in r["simili"]:
            vol[(s["frase"].lower(), r["paese"])] = max(vol.get((s["frase"].lower(), r["paese"]), 0), s["volume"] or 0)
    faq = json.loads((RADICE / "dati" / "faq_generate.json").read_text(encoding="utf-8"))["faq"]
    for x in faq:
        if vol.get((x["ricerca"].lower(), x["paese"]), 0) <= 0:
            err(f"FAQ «{x['domanda']}»: la ricerca «{x['ricerca']}» non ha volume misurato")
    ok(f"{len(faq)} FAQ, ognuna da una ricerca con volume misurato ({', '.join(sorted({x['ricerca'] for x in faq})[:4])}…)")
    # numeri stampati = motore
    for y in (1913, 1950, 1970, 1980, 2025):
        t = (SITO / "us" / f"{y}-dollars-today" / "index.html").read_text(encoding="utf-8")
        atteso = G.soldi(G.vale_oggi("us", y), "USD")
        if f'<span class="big">{atteso}</span>' not in t:
            err(f"pagina {y}: valore di $1 non uguale al motore ({atteso})")
    for x, y in ((100, 1970), (1000, 1980)):
        t = (SITO / "us" / f"{x}-dollars-in-{y}" / "index.html").read_text(encoding="utf-8")
        if G.soldi(x * G.vale_oggi("us", y), "USD") not in t:
            err(f"pagina ${x} {y}: valore non uguale al motore")
    for rel, k, imp, da, a, v in ((("index.html", "us", 100, (1970, None), G.ULT["us"], None), ("uk/index.html", "uk_cpi", 100, (1990, None), G.ULT["uk_cpi"], None))
                                  + ((("de/inflationsrechner/index.html", "de", 100, (2002, None), G.ULT["de"], False),) if DE else ())):
        t = (SITO / rel).read_text(encoding="utf-8")
        m = re.search(r"<b data-valore>([^<]+)</b>", t)
        r = M.calcola(C[k], imp, da, a, v)
        valuta = "EUR" if k == "de" else ("GBP" if k.startswith("uk") else "USD")
        if not m or unescape(m.group(1)) != G.soldi(r["valore"], valuta):
            err(f"{rel}: risultato statico {m and m.group(1)} ≠ motore {r['valore']:.2f}")
    ok(f"numeri stampati (pagine anno, pagine importo, risultato iniziale dei {'tre' if DE else 'due'} calcolatori) = motore")
    if not DE:
        sezione_de_spenta()
    # monetizzazione
    e, info = MON.controlla_sito(G.SITO_ID, SITO)
    ERR.extend(e)
    if not e:
        ok(MON.riepilogo(G.SITO_ID, info, e))
    # chiave e nomi di modello nei sorgenti
    for f in RADICE.rglob("*"):
        if f.is_file() and f.suffix in (".py", ".js", ".json", ".md", ".html", ".csv", ".txt", ".toml") and "cache" not in f.parts:
            t = f.read_text(encoding="utf-8", errors="replace")
            if SEGNO_CHIAVE in t:
                err(f"{f}: chiave nel repository")
            if f.suffix != ".csv" and MODELLI.search(t):
                err(f"{f.relative_to(RADICE)}: nome di modello AI")


# ---------------------------------------------------------------- 3b. limiti IRS (401(k), IRA, Roth, SIMPLE, HSA)
def _norm(t):
    import importlib.util
    spec = importlib.util.spec_from_file_location("irs_raccolta", RADICE / "raccolta" / "irs.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.normalizza(t)


# Fonti di legge ammesse (non irs.gov): id → (voci che possono citarla, frase che estende la cifra a tutti gli anni)
LEGGE_USA = {"usc_223": (("hsa_catchup",), "2009 and thereafter $1,000")}


def _usd_in(x, frase):
    return f"${x:,}" in frase or f"$ {x:,}" in frase


def pensione():
    """Ogni cifra di dati/limiti.json contro la frase IRS citata; frasi nel testo della fonte; fonte dell'anno giusto; controprove sui comunicati
    e sulle tabelle COLA dell'IRS; coerenza interna; cifre stampate nelle pagine = limiti.json; motore Roth JS pubblicato = Python."""
    import hashlib
    L = PEN.LIM
    testi, n_cifre, n_frasi, n_mostra = {}, 0, 0, 0

    def testo_fonte(fid):
        if fid not in testi:
            f = G.FONTI.get(fid)
            p = RADICE / "dati" / "grezzi" / "irs" / f"{fid}.txt"
            if not f or f.get("http") != 200 or not f.get("sha256") or not f.get("letto_il") or not p.exists():
                err(f"limiti: fonte {fid} senza registrazione completa in fonti.json o senza testo")
                testi[fid] = ""
            else:
                testi[fid] = p.read_text(encoding="utf-8")
                if f.get("originale"):
                    b = (RADICE / "dati" / f["originale"]).read_bytes()
                    if hashlib.sha256(b).hexdigest() != f["sha256"]:
                        err(f"limiti: {fid}: SHA-256 del PDF conservato ≠ fonti.json")
                atteso_url = "https://www.govinfo.gov/content/pkg/USCODE-" if fid in LEGGE_USA else "https://www.irs.gov/"
                if not f["url"].startswith(atteso_url):
                    err(f"limiti: {fid} non è una pagina {atteso_url} ({f['url']})")
        return testi[fid]
    for fid, segno in L["identita"].items():
        if segno not in testo_fonte(fid):
            err(f"limiti: {fid} non contiene «{segno}» (documento di un altro anno?)")
    for y, voci in L["anni"].items():
        for k, x in voci.items():
            t = testo_fonte(x["fonte"])
            n_frasi += 1
            if _norm(x["frase"]) not in t:
                err(f"limiti {y} {k}: frase non trovata in {x['fonte']}")
            for val in (x["valore"] if isinstance(x["valore"], list) else [x["valore"]]):
                n_cifre += 1
                if not _usd_in(val, x["frase"]):
                    err(f"limiti {y} {k}: {val} non è nella frase citata")
                if x.get("mostra") and not _usd_in(val, x["mostra"]):
                    err(f"limiti {y} {k}: {val} non è nella frase mostrata")
            if x.get("mostra"):
                # «mostra» = «frase» senza un solo numero di pagina del PDF (es. «high -2deductible» → «high deductible»): niente altro può cambiare
                senza = {re.sub(r"\s+", " ", x["frase"][:m.start()] + x["frase"][m.end():]) for m in re.finditer(r"-?\d{1,2}-? ?", x["frase"])}
                n_mostra += 1
                if x["mostra"] not in senza or not x["fonte"].startswith("irs_rp_"):
                    err(f"limiti {y} {k}: la frase mostrata non è la frase IRS senza il numero di pagina")
            if x["fonte"] in LEGGE_USA:
                # cifra fissata dalla legge, non da un documento dell'anno: solo le voci ammesse e solo con la frase che la estende a ogni anno
                if k not in LEGGE_USA[x["fonte"]][0] or LEGGE_USA[x["fonte"]][1] not in x["frase"]:
                    err(f"limiti {y} {k}: la legge {x['fonte']} non può essere la fonte di questa voce")
                continue
            anno_fonte = re.search(r"_(\d{4})b?$", x["fonte"])
            if not anno_fonte or anno_fonte.group(1) != y:
                err(f"limiti {y} {k}: la fonte {x['fonte']} è di un altro anno")
    for k, x in L["testi"].items():
        n_frasi += 1
        if _norm(x["frase"]) not in testo_fonte(x["fonte"]):
            err(f"limiti testo {k}: frase non trovata in {x['fonte']}")
    # controprova 1: il comunicato dell'anno (documento diverso dal Notice) contiene le stesse cifre
    A, n_cp = PEN.A, 0
    for y in PEN.ANNI:
        t = testo_fonte(f"irs_ir_{y}")
        for k in ("k401", "catchup", "catchup_6063", "ira", "ira_catchup", "roth_single", "roth_mfj", "ded_single", "ded_mfj", "ded_spouse", "simple"):
            if k in A[y]:
                for val in (A[y][k]["valore"] if isinstance(A[y][k]["valore"], list) else [A[y][k]["valore"]]):
                    n_cp += 1
                    if f"${val:,}" not in t:
                        err(f"limiti {y} {k}: {val} non compare nel comunicato IRS dell'anno")
    # controprova 2: tabelle COLA dell'IRS (pagina 2023-2026 e PDF degli anni precedenti, 2020-2025)
    cola_p, cola_t = testo_fonte("irs_cola_pagina"), testo_fonte("irs_cola_tabella")
    seq = lambda k, anni, pre="": " ".join(f"{pre}{PEN.v(a, k):,}" for a in anni)  # noqa: E731
    pag = [2026, 2025, 2024, 2023]
    controlli_cola = [("Elective deferrals " + seq("k401", pag), cola_p), ("IRA contribution limit " + seq("ira", pag, "$"), cola_p),
                      ("IRA catch-up contributions " + seq("ira_catchup", pag), cola_p), ("SIMPLE maximum contributions " + seq("simple", pag), cola_p),
                      ("Defined contribution plan limit " + seq("dc415c", pag), cola_p), ("457 elective deferrals " + seq("k457", pag), cola_p),
                      ("Joint return " + " ".join(f"{PEN.v(a, 'ded_mfj')[0]:,}" for a in pag), cola_p),
                      ("Single or head of household " + " ".join(f"{PEN.v(a, 'ded_single')[0]:,}" for a in pag), cola_p)]
    tab = [2025, 2024, 2023, 2022, 2021, 2020]
    controlli_cola += [(seq("k401", tab), cola_t), (seq("simple", tab), cola_t), (seq("dc415c", tab), cola_t), (seq("ira", tab), cola_t),
                       (seq("simple_catchup", tab), cola_t), (" ".join(f"--{PEN.v(a, 'catchup'):,}" for a in tab), cola_t),
                       (seq("simple", [2019, 2018, 2017, 2016, 2015]), cola_t)]
    for frase, t in controlli_cola:
        if frase not in t:
            err(f"limiti: le tabelle COLA dell'IRS non danno «{frase}»")
    # coerenza interna
    for y in PEN.ANNI:
        if PEN.v(y, "k457") != PEN.v(y, "k401"):
            err(f"limiti {y}: 457(b) ≠ 402(g) (la pagina 401(k) dice che sono uguali in ogni anno)")
        for k, w in (("roth_single", 15000), ("roth_mfj", 10000), ("roth_mfs", 10000), ("ded_single", 10000), ("ded_mfj", 20000), ("ded_spouse", 10000)):
            lo, hi = PEN.v(y, k)
            if hi - lo != w:
                err(f"limiti {y} {k}: ampiezza {hi - lo} invece di {w}")
        if PEN.v(y, "roth_mfs") != [0, 10000]:
            err(f"limiti {y}: Roth MFS ≠ 0-10.000")
        if y > PEN.PRIMO:
            for k in ("k401", "catchup", "ira", "dc415c", "simple", "hsa_self", "hsa_family"):
                if PEN.v(y, k) < PEN.v(y - 1, k):
                    err(f"limiti {y} {k}: più basso dell'anno prima")
    # contributo HSA dai 55 anni: 1.000 $ in ogni anno (legge: «2009 and thereafter $1,000», non indicizzato perché § 223(g) nomina solo (b)(2) e (c)(2)(A))
    usc = testo_fonte("usc_223")
    for y in PEN.ANNI:
        if PEN.v(y, "hsa_catchup") != 1000:
            err(f"limiti {y}: contributo HSA 55+ = {PEN.v(y, 'hsa_catchup')} invece dei 1.000 $ fissati dalla sezione 223(b)(3)(B)")
    if "2009 and thereafter $1,000" not in usc or "Each dollar amount in subsections (b)(2) and (c)(2)(A) shall be increased" not in usc or "(b)(3)" in \
            usc[usc.find("(g) Cost-of-living adjustment"):usc.find("(h) Reports")]:
        err("limiti: la sezione 223 letta non fissa più a 1.000 $ non indicizzati il contributo HSA 55+")
    # soglia salariale del catch-up Roth: la frase del Notice dell'anno dopo parte dalla cifra dell'anno prima
    for y in PEN.ANNI:
        if "roth_catchup_soglia" in A[y] and "roth_catchup_soglia" in A.get(y - 1, {}):
            if f"from ${PEN.v(y - 1, 'roth_catchup_soglia'):,} to ${PEN.v(y, 'roth_catchup_soglia'):,}" not in A[y]["roth_catchup_soglia"]["frase"]:
                err(f"limiti {y}: soglia del catch-up Roth non coerente con l'anno prima")
    if f"${PEN.v(2026, 'roth_catchup_soglia'):,} (for 2026)" not in L["testi"]["roth_catchup_salario"]["frase"]:
        err("limiti: la pagina IRS sui catch-up non dà la soglia Roth 2026 del Notice")
    # Publication 590-A (2025): soglie e metodo coerenti con i limiti 2025
    r25 = PEN.v(2025, "roth_mfj"), PEN.v(2025, "roth_single")
    if not (_usd_in(r25[0][1], L["testi"]["roth_chi"]["frase"]) and _usd_in(r25[1][1], L["testi"]["roth_chi"]["frase"])
            and _usd_in(r25[0][0], L["testi"]["roth_riga2"]["frase"]) and _usd_in(r25[1][0], L["testi"]["roth_riga2"]["frase"])):
        err("Publication 590-A (2025): soglie Roth diverse da quelle del Notice 2024-80")
    ok(f"limiti IRS: {n_cifre} cifre in {sum(len(a) for a in L['anni'].values())} voci ({PEN.PRIMO}-{PEN.ULTIMO}) e {len(L['testi'])} frasi di metodo: "
       f"{n_frasi} frasi ritrovate nel testo IRS della fonte dell'anno giusto, ogni cifra dentro la sua frase ({n_mostra} frasi mostrate senza il numero di pagina del PDF); {len(L['identita'])} documenti con il loro anno; "
       f"{n_cp} cifre ritrovate anche nel comunicato IRS dell'anno; {len(controlli_cola)} serie uguali alle tabelle COLA dell'IRS; ampiezze delle fasce e crescita coerenti")
    # pagine: ogni cella con data-k = limiti.json
    n_celle = 0
    for chiave, perc in PEN.PAGINE.items():
        t = (SITO / perc / "index.html").read_text(encoding="utf-8")
        vis = re.sub(r"\s+", " ", testo(t))
        for anno, riga in re.findall(r'<tr data-anno="(\d{4})"[^>]*>(.*?)</tr>', t, re.S):
            for k, cell in re.findall(r'<td class="n[^"]*" data-k="([\w.]+)">([^<]*)</td>', riga):
                base, _, i = k.partition(".")
                val = PEN.v(int(anno), base)
                if val is not None and i:
                    val = val[int(i)]
                atteso = "–" if val is None else (PEN.fascia(val) if isinstance(val, list) else PEN.usd(val))
                n_celle += 1
                if unescape(cell) != atteso:
                    err(f"{perc} {anno} {k}: stampato {cell} ≠ IRS {atteso}")
            m = re.search(r'data-tot="(\d+)"', riga)
            if m and int(m.group(1)) != PEN.v(int(anno), "k401") + PEN.v(int(anno), "catchup"):
                err(f"{perc} {anno}: totale con catch-up sbagliato")
        for k, c0, c1 in re.findall(r'<tr data-riga="(\w+)">.*?<td class="n[^"]*" data-k="\w+">([^<]*)</td><td class="n[^"]*" data-k="\w+">([^<]*)</td>', t, re.S):
            for anno, cell in ((PEN.CORRENTE, c0), (PEN.ULTIMO, c1)):
                val = PEN.v(anno, k)
                n_celle += 1
                if unescape(cell) != ("–" if val is None else PEN.fascia(val) if isinstance(val, list) else PEN.usd(val)):
                    err(f"{perc} sintesi {k} {anno}: {cell}")
        if "Internal Revenue Service" not in vis or "not financial or investment advice" not in vis or "We do not promote any account" not in vis:
            err(f"{perc}: manca la fonte IRS o l'avviso")
        if "irs.gov/" not in t:
            err(f"{perc}: nessun link a irs.gov")
        for x in re.findall(r'<blockquote class="citaz">“(.*?)\.”<cite>', t, re.S):
            n_celle += 0
            if not any(_norm(unescape(x)) == _norm(v.get("mostra") or v["frase"]) for a in L["anni"].values() for v in a.values()) and \
                    not any(_norm(unescape(x)) == _norm(v["frase"]) for v in L["testi"].values()):
                err(f"{perc}: citazione non presa da limiti.json «{unescape(x)[:60]}»")
    # pagina 401(k): le spiegazioni (somma tra piani, 457(b) a parte, catch-up «if permitted by the plan», 415(c) senza catch-up, soglia Roth)
    # sono citate dalle pagine IRS, non scritte da noi
    t401 = (SITO / PEN.PAGINE["401k"] / "index.html").read_text(encoding="utf-8")
    for k in ("k401_somma", "k401_457", "k401_piano_limite", "k401_catchup_piano", "k401_415c", "roth_catchup_salario"):
        if G.h(L["testi"][k]["frase"]) not in t401:
            err(f"401k-limit/: manca la frase IRS «{k}» che regge la spiegazione")
    for vecchia in ("to one person", "to one account", "if the plan allows it"):
        if vecchia in t401:
            err(f"401k-limit/: è tornata una spiegazione non citata («{vecchia}»)")
    thsa = (SITO / PEN.PAGINE["hsa"] / "index.html").read_text(encoding="utf-8")
    if 'class="n vuoto"' in thsa or G.h(L["testi"]["hsa_55_legge"]["frase"]) not in thsa or "govinfo.gov" not in thsa:
        err("hsa-limit/: contributo 55+ senza la legge come fonte, o celle vuote")
    if n_celle < 400:
        err(f"limiti: solo {n_celle} celle lette nelle pagine (struttura cambiata?)")
    # tabella limiti e inflazione: valori in dollari di oggi = CPI-U
    t = (SITO / PEN.PAGINE["indice"] / "index.html").read_text(encoding="utf-8")
    r = G.val("us", G.ULTIMO_ANNO_US) / G.val("us", PEN.PRIMO)
    righe_cpi = re.findall(r'<tr data-k="(\w+)"><td>[^<]*</td><td class="n">[^<]*</td><td class="n" data-cpi>([^<]*)</td>', t)
    for k, cell in righe_cpi:
        if cell != G.soldi(PEN.v(PEN.PRIMO, k) * r, "USD", 0):
            err(f"limiti e inflazione: {k} {cell} ≠ CPI-U")
    if len(righe_cpi) != 5 or f"/?a={PEN.v(PEN.PRIMO, 'k401')}&amp;f={PEN.PRIMO}&amp;t={G.ULTIMO_ANNO_US}#calc" not in t:
        err("limiti e inflazione: tabella o link al calcolatore mancanti")
    ok(f"pagine dei limiti: {n_celle} celle (tabelle per anno e sintesi {PEN.CORRENTE}/{PEN.ULTIMO}) = limiti.json; citazioni = frasi IRS registrate; "
       f"{len(righe_cpi)} limiti {PEN.PRIMO} in dollari {G.ULTIMO_ANNO_US} = CPI-U; avviso e link irs.gov in tutte le {len(PEN.PAGINE)} pagine")
    roth_motore()


def roth_casi():
    rnd = random.Random(11)
    casi = []
    for y in PEN.ANNI:
        for stato in PEN.STATI:
            lo, hi = PEN.roth_dati(y)[PEN.FASCIA_STATO[stato]]
            for o50 in (False, True):
                magi = [0, lo * 100 - 1, lo * 100, lo * 100 + 1, hi * 100 - 1, hi * 100, hi * 100 + 1, (lo + hi) * 50, 99999999]
                magi += [rnd.randrange(max(0, lo * 100 - 300000), hi * 100 + 300000) for _ in range(25)]
                magi += [(lo + rnd.randrange(0, hi - lo)) * 100 for _ in range(10)]  # dollari tondi: arrotondamenti esatti ai 10 $
                for m in magi:
                    casi.append([y, stato, m, o50, None, 0])
                casi.append([y, stato, (lo + hi) * 50, o50, 300000, 0])           # compenso sotto il limite
                casi.append([y, stato, lo * 100 + 10, o50, 15000, 0])              # compenso piccolissimo: riga 11 = riga 10
                casi.append([y, stato, hi * 100 - 500, o50, None, 0])              # sotto i 200 $: diventa 200 $
                casi.append([y, stato, (lo + hi) * 50, o50, None, 250000])         # già versati 2.500 $ in un IRA tradizionale
                casi.append([y, stato, lo * 100 - 100, o50, None, PEN.v(y, "ira") * 100])  # tutto già versato altrove
    return casi


def roth_motore():
    """Motore Roth pubblicato (sito/assets/roth.*.js) = pensione.roth_limite su ogni anno, stato, età, ai bordi delle fasce e a caso;
    esempio del foglio IRS (2025, single, MAGI 151.000 $ → 6.540 $); risultato iniziale della pagina = Python."""
    js_file = next((SITO / "assets").glob("roth.*.js"))
    js = js_file.read_text(encoding="utf-8")
    motore_js = js[:js.index("(function(){")]
    casi = roth_casi()
    dati = {str(y): PEN.roth_dati(y) for y in PEN.ANNI}
    prog = motore_js + "\nvar D=" + json.dumps(dati) + ";var K=" + json.dumps(casi) + (
        ";process.stdout.write(JSON.stringify(K.map(function(c){var r=rothLimite(D[c[0]],c[1],c[2],c[3],c[4],c[5]);return [r.esito,r.limite];})));")
    p = subprocess.run(["node", "-"], input=prog, capture_output=True, text=True)
    if p.returncode:
        err("node (Roth): " + p.stderr[:300])
        return
    diversi, esiti = 0, {"full": 0, "partial": 0, "none": 0}
    minimi = 0
    for c, (e, lim) in zip(casi, json.loads(p.stdout)):
        r = PEN.roth_limite(PEN.roth_dati(c[0]), c[1], c[2], c[3], c[4], c[5])
        esiti[r["esito"]] += 1
        minimi += r["esito"] == "partial" and r["l8"] == 20000
        if (e, lim) != (r["esito"], r["limite"]):
            diversi += 1
            if diversi < 4:
                err(f"Roth JS ≠ Python: {c}: {e} {lim} / {r['esito']} {r['limite']}")
        lo, hi = PEN.roth_dati(c[0])[PEN.FASCIA_STATO[c[1]]]
        atteso = "full" if c[2] <= lo * 100 else "none" if c[2] >= hi * 100 else "partial"
        if r["esito"] != atteso or r["limite"] < 0 or r["limite"] > r["L"] or (r["esito"] == "partial" and r["limite"] % 1000 and r["limite"] != r["l10"]):
            err(f"Roth: risultato incoerente {c} → {r}")
    es = PEN.roth_limite(PEN.roth_dati(2025), "single", 15100000, False)
    if es["limite"] != 654000:
        err(f"Roth: esempio del foglio IRS 2025 (MAGI 151.000 $) = {es['limite'] / 100} invece di 6.540 $")
    t = (SITO / PEN.PAGINE["roth"] / "index.html").read_text(encoding="utf-8")
    ini = PEN.roth_limite(PEN.roth_dati(PEN.CORRENTE), "single", 16000000, False)
    if f"<b data-roth-limite>{PEN.usd(ini['limite'] // 100)}</b>" not in t or "$6,540" not in t:
        err("Roth: risultato iniziale della pagina o esempio IRS diversi dal motore")
    if not diversi:
        ok(f"calcolatore Roth pubblicato ({js_file.name}) = Python su {len(casi)} casi ({esiti['full']} pieni, {esiti['partial']} ridotti, {esiti['none']} nulli; "
           f"bordi delle fasce al centesimo, {minimi} casi al minimo di 200 $, compenso basso, versamenti ad altri IRA); esempio del foglio IRS 2025 = 6.540 $")


# ---------------------------------------------------------------- 3c. prezzi EIA di gasolio da riscaldamento e propano
EIA_DIR = RADICE / "dati" / "grezzi" / "eia"
EIA_PRODOTTO = {"oil": ("EPD2F", "heating_oil", "rh"), "propane": ("EPLLPA", "propane", "rp")}
EIA_CONSIGLI = re.compile(r"\b(buy now|best time to (buy|fill|order)|lock in|pre-?buy|cheapest|best (supplier|dealer|company|price)|"
                          r"should (buy|fill|order|wait)|we recommend|top up now|prices will (rise|fall|go))\b", re.I)


def _eia_xls(comb):
    """Lettura indipendente dell'XLS grezzo (non usa raccolta/eia.py né riscaldamento.py): (date, {area: {data: millesimi}}, nomi, errori)."""
    import xlrd
    from datetime import date as _d
    prodotto, nome, _ = EIA_PRODOTTO[comb]
    libro = xlrd.open_workbook(str(EIA_DIR / f"{nome}.xls"))
    f = libro.sheet_by_name("Data 1")
    e = []
    date_ = []
    for r in range(3, f.nrows):
        d = xlrd.xldate_as_datetime(f.cell_value(r, 0), libro.datemode).date()
        if d.weekday() != 0:
            e.append(f"{comb}: {d} non è un lunedì")
        date_.append(d)
    if date_ != sorted(set(date_)) or date_[0] != _d(1990, 10, 1):
        e.append(f"{comb}: date non crescenti o inizio diverso dal 1/10/1990")
    aree, nomi = {}, {}
    for j in range(1, f.ncols):
        chiave, titolo = f.cell_value(1, j), f.cell_value(2, j)
        m = re.fullmatch(rf"W_{prodotto}_PRS_(?:(NUS|R\w\w)|S(\w\w))_DPG", chiave)
        if not m or not re.search(r"Residential Price\s+\(Dollars per Gallon\)$", titolo) or not titolo.startswith("Weekly "):
            e.append(f"{comb}: colonna {chiave} / {titolo}: non è un prezzo residenziale in dollari per gallone")
            continue
        cod = m.group(1) or m.group(2)
        nomi[cod] = (chiave, re.sub(r"\s+(No\. 2 Heating Oil|Propane) Residential Price.*$", "", re.sub(r"^(Weekly )+", "", titolo)))
        aree[cod] = {}
        for r in range(3, f.nrows):
            c = f.cell(r, j)
            if c.ctype == xlrd.XL_CELL_NUMBER:
                mill = round(c.value * 1000)
                if not (300 < mill < 15000) or abs(c.value * 1000 - mill) > 1e-6:
                    e.append(f"{comb} {cod} {date_[r - 3]}: valore fuori scala o con più di tre decimali ({c.value})")
                aree[cod][date_[r - 3]] = mill
            elif c.ctype != xlrd.XL_CELL_EMPTY and str(c.value).strip():
                e.append(f"{comb} {cod} {date_[r - 3]}: cella inattesa {c.value!r}")
    return date_, aree, nomi, e


def _eia_anno_prima(v, d):
    from datetime import timedelta
    for g in (364, 371, 357):
        if d - timedelta(days=g) in v:
            return d - timedelta(days=g)
    return None


def _mezzo_su(fr):
    """Arrotonda una frazione all'intero più vicino, il mezzo per eccesso."""
    import math
    from fractions import Fraction
    return math.floor(fr + Fraction(1, 2))


def _eia_stagione(d):
    return d.year if d.month >= 10 else d.year - 1 if d.month <= 3 else None


def riscaldamento():
    n_err = len(ERR)
    _riscaldamento()
    if len(ERR) > n_err:  # con anche un solo errore nessuna riga «ok» della sezione resta
        OK[:] = [x for x in OK if not (x.startswith("EIA:") or x.startswith("costo del pieno"))]


def _riscaldamento():
    import hashlib
    from datetime import date as _d, timedelta
    from fractions import Fraction
    import riscaldamento as RIS
    fonti = G.FONTI
    # A. file grezzi = fonti.json (SHA-256), frasi ancora presenti
    ids = [k for k in fonti if k.startswith("eia_")]
    for k in ids:
        f = fonti[k]
        b = (RADICE / "dati" / f["file"]).read_bytes()
        if hashlib.sha256(b).hexdigest() != f["sha256"] or f["http"] != 200 or len(b) != f["byte"] or not f["url"].startswith("https://www.eia.gov/"):
            err(f"EIA {k}: file grezzo diverso da fonti.json (SHA-256, byte, HTTP o indirizzo)")
        if f.get("cerca"):
            t = re.sub(r"\s+", " ", testo(b.decode("utf-8", "replace")))
            for nome, frase in f["cerca"].items():
                if frase not in t:
                    err(f"EIA {k}: frase «{nome}» non più nel file")
    if len(ids) != 7:
        err(f"EIA: {len(ids)} fonti invece di 7")
    # B. XLS riletti da zero; eia_prezzi.json = XLS valore per valore
    X = {}
    prezzi = json.loads((RADICE / "dati" / "eia_prezzi.json").read_text(encoding="utf-8"))
    n_val = 0
    for comb in EIA_PRODOTTO:
        date_, aree, nomi, e = _eia_xls(comb)
        ERR.extend(e)
        X[comb] = (date_, aree, nomi)
        pj = prezzi["combustibili"][comb]
        if pj["date"] != [d.isoformat() for d in date_] or set(pj["aree"]) != set(aree):
            err(f"EIA {comb}: date o aree di eia_prezzi.json diverse dall'XLS")
            continue
        for cod, a in pj["aree"].items():
            for d, x in zip(date_, a["valori"]):
                if (None if x is None else round(x * 1000)) != aree[cod].get(d):
                    err(f"EIA {comb} {cod} {d}: eia_prezzi.json {x} ≠ XLS {aree[cod].get(d)}")
                n_val += x is not None
        if fonti[f"eia_{comb}_xls"].get("ultima_settimana") != date_[-1].isoformat():
            err(f"EIA {comb}: ultima settimana in fonti.json diversa dall'XLS")
    attivi = {comb: sorted(c for c, v in X[comb][1].items() if len(c) == 2 and any(d in v for d in X[comb][0][-3:])) for comb in X}
    if (len(X["oil"][1]), len(X["propane"][1])) != (29, 46) or (len(attivi["oil"]), len(attivi["propane"])) != (21, 38):
        err(f"EIA: serie {len(X['oil'][1])}/{len(X['propane'][1])} (attese 29/46), Stati con prezzo corrente {len(attivi['oil'])}/{len(attivi['propane'])} (attesi 21/38)")
    if X["oil"][0][-1] != X["propane"][0][-1]:
        err("EIA: gasolio e propano non hanno la stessa ultima settimana")
    ultima = X["oil"][0][-1]
    ok(f"EIA: 7 file grezzi = fonti.json (SHA-256) con le frasi su tasse, stagione, revisioni e dominio pubblico; XLS riletti da zero: gasolio {len(X['oil'][0])} "
       f"settimane e {len(X['oil'][1])} serie, propano {len(X['propane'][0])} e {len(X['propane'][1])}, tutti lunedì dal 1/10/1990 al {ultima.strftime('%d/%m/%Y')}, "
       f"dollari per gallone a tre decimali; {n_val} valori di eia_prezzi.json = XLS; Stati con prezzo corrente {len(attivi['oil'])} e {len(attivi['propane'])}")
    # C. tabelle HTML dell'EIA (ultime 6 settimane) = XLS
    n_tab = 0
    for comb, (_, nome, _) in EIA_PRODOTTO.items():
        t = (EIA_DIR / f"{nome}.htm").read_text(encoding="latin-1")
        if "(Dollars per Gallon Excluding Taxes)" not in t:
            err(f"EIA {comb}: la tabella non dice più «Dollars per Gallon Excluding Taxes»")
        dd = [_d(2000 + int(x[6:8]), int(x[0:2]), int(x[3:5])) for x in re.findall(r'<th class="Series5">(\d\d/\d\d/\d\d)</th>', t)]
        if dd != X[comb][0][-6:]:
            err(f"EIA {comb}: settimane della tabella HTML ≠ ultime 6 dell'XLS")
        per_chiave = {v[0]: c for c, v in X[comb][2].items()}
        righe = t.split('<tr class="DataRow">')[1:]
        if len(righe) != len(X[comb][1]):
            err(f"EIA {comb}: {len(righe)} righe nella tabella HTML, {len(X[comb][1])} serie nell'XLS")
        for r in righe:
            ch = re.search(r"[?&;]s=(W_\w+_DPG)", r).group(1)
            celle = [unescape(c).replace("\xa0", "").strip() for c in re.findall(r'class="(?:DataB|Current2)">(.*?)</td>', r, re.S)]
            for d, c in zip(dd, celle):
                x = X[comb][1][per_chiave[ch]].get(d)
                if (round(float(c) * 1000) if re.fullmatch(r"\d+\.\d{3}", c) else None) != x:
                    err(f"EIA {comb} {ch} {d}: tabella HTML «{c}» ≠ XLS {x}")
                n_tab += x is not None
    # D. pagina "Heating Oil and Propane Update": ultimo prezzo, variazione sulla settimana e sull'anno = nostre regole (7 giorni; 52 settimane)
    up = (EIA_DIR / "update.htm").read_text(encoding="utf-8")
    n_up = 0
    for comb, (_, _, tid) in EIA_PRODOTTO.items():
        seg = up[up.index(f'id="{tid}"'):]
        seg = seg[:seg.index("</table>")]
        m = re.search(r"<th>(\d\d)/(\d\d)/(\d\d)</th>", seg)
        if not m or _d(2000 + int(m.group(3)), int(m.group(1)), int(m.group(2))) != ultima:
            err(f"EIA update {comb}: data della tabella diversa dall'ultima settimana dell'XLS")
        per_nome = {v[1]: c for c, v in X[comb][2].items()}
        per_nome.update({"U.S. Average": "NUS", "Midwest (PADD 2)": per_nome.get("PADD 2", per_nome.get("Midwest (PADD 2)"))})
        for r in re.findall(r"<tr[^>]*>(.*?)</tr>", seg, re.S):
            c = [re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", x))).strip() for x in re.findall(r"<td>(.*?)</td>", r, re.S)]
            if len(c) != 4 or not re.fullmatch(r"\d+\.\d{3}", c[1]):
                continue
            if c[0] not in per_nome:
                err(f"EIA update {comb}: area «{c[0]}» non trovata nell'XLS")
                continue
            v = X[comb][1][per_nome[c[0]]]
            att = [v.get(ultima)]
            w, y = ultima - timedelta(days=7), _eia_anno_prima(v, ultima)
            att.append(v[ultima] - v[w] if ultima in v and w in v else None)
            att.append(v[ultima] - v[y] if ultima in v and y else None)
            letti = [round(float(x) * 1000) if re.fullmatch(r"-?\d+\.\d{3}", x) else None for x in c[1:]]
            if letti != att:
                err(f"EIA update {comb} {c[0]}: pagina EIA {c[1:]} ≠ XLS con le nostre regole {att}")
            n_up += 1
    ok(f"EIA: tabelle HTML (6 settimane) = XLS su {n_tab} valori; pagina Update dell'EIA: ultimo prezzo, variazione sulla settimana e sull'anno prima "
       f"uguali ai nostri conti per {n_up} aree (anno prima = 52 settimane prima)")

    # E. pagine: ogni prezzo stampato rifatto dall'XLS
    def prezzo(comb, cod, iso):
        return X[comb][1][cod].get(_d.fromisoformat(iso))

    def p3(m):
        return f"${m / 1000:.3f}"

    def stag(comb, cod, s):
        return [m for d, m in sorted(X[comb][1][cod].items()) if _eia_stagione(d) == s]

    def coppie(comb, cod, s):
        v = X[comb][1][cod]
        return [(v[d], v[_eia_anno_prima(v, d)]) for d in sorted(v) if _eia_stagione(d) == s and _eia_anno_prima(v, d)]

    def db(d):
        return f"{G.MESI['en'][d.month - 1][:3]} {d.day}, {d.year}"

    def dl(d):
        return f"{G.MESI['en'][d.month - 1]} {d.day}, {d.year}"

    def atteso(tipo, chiave):
        k = chiave.split("|")
        comb, cod = k[0], k[1]
        if tipo == "p":
            return p3(prezzo(comb, cod, k[2]))
        if tipo in ("d", "r"):
            a, b = prezzo(comb, cod, k[2]), prezzo(comb, cod, k[3])
            if tipo == "d":
                return ("+" if a > b else "−" if a < b else "") + p3(abs(a - b))
            r10 = _mezzo_su(Fraction(1000 * (a - b), b))
            if abs(r10 / 10 - (a / b - 1) * 100) > 0.0501:
                return "?"
            return ("+" if r10 > 0 else "−" if r10 < 0 else "") + f"{abs(r10) / 10:.1f}%"
        if tipo == "m":
            v = stag(comb, cod, int(k[2]))
            return p3(_mezzo_su(Fraction(sum(v), len(v))))
        if tipo == "mp":
            v = [x[0 if k[3] == "cur" else 1] for x in coppie(comb, cod, int(k[2]))]
            return p3(_mezzo_su(Fraction(sum(v), len(v))))
        if tipo == "cpi":
            v = stag(comb, cod, int(k[2]))
            r = M.calcola(G.C["us"], _mezzo_su(Fraction(sum(v), len(v))) / 1000, (int(k[2]) + 1, 1), G.US_LU)
            return f"${r['valore']:.2f}"
        if tipo == "t":
            return f"${_mezzo_su(Fraction(int(k[3]) * prezzo(comb, cod, k[2]), 100)) / 100:,.2f}"
        return "?"
    ps = RIS.pagine_stato(G)
    pagine_ = [(comb, "NUS", None, RIS.COMB[comb]["slug"]) for comb in EIA_PRODOTTO] + [(c, cod, nome, RIS.percorso(c, nome)) for c, cod, nome, _, _ in ps]
    conta = {"p": 0, "d": 0, "r": 0, "m": 0, "mp": 0, "cpi": 0, "t": 0}
    n_date = n_json = 0
    for comb, cod, nome, perc in pagine_:
        f = SITO / perc / "index.html"
        if not f.exists():
            err(f"EIA: pagina {perc} mancante")
            continue
        t = f.read_text(encoding="utf-8")
        v = X[comb][1][cod]
        ult = max(v)
        if ult != ultima:  # l'EIA può non pubblicare uno Stato per una settimana (NA): la pagina mostra la data del suo ultimo prezzo
            AVV.append(f"{perc}: l'ultimo prezzo dell'area è del {ult}, non dell'ultima settimana {ultima}")
        for m in re.finditer(r'<(\w+)[^>]*? data-(p|d|r|m|mp|cpi|t)="([^"]+)"[^>]*>(.*?)</\1>', t, re.S):
            tipo, chiave, mostrato = m.group(2), m.group(3), unescape(m.group(4))
            try:
                a = atteso(tipo, chiave)
            except Exception as ex:  # noqa: BLE001
                a = f"errore {ex!r}"
            if mostrato != a:
                err(f"{perc}: data-{tipo}={chiave}: stampato «{mostrato}», dall'XLS «{a}»")
            conta[tipo] += 1
        # la data accanto a ogni prezzo delle tabelle è quella della sua settimana
        for m in re.finditer(r'<td class="nw[^"]*">([^<]+)</td><td class="n" data-p="\w+\|\w+\|([\d-]+)">', t):
            if m.group(1) != db(_d.fromisoformat(m.group(2))):
                err(f"{perc}: data «{m.group(1)}» accanto al prezzo del {m.group(2)}")
            n_date += 1
        # apertura: prezzo dell'ultima settimana dell'area, con la sua data; titolo e descrizione con lo stesso prezzo
        apre = re.search(r'<span class="big"><span data-p="([^"]+)">', t)
        if not apre or apre.group(1) != f"{comb}|{cod}|{ult.isoformat()}" or f"on Monday, {dl(ult)}, excluding taxes" not in t:
            err(f"{perc}: il prezzo d'apertura non è quello dell'ultima settimana ({ult}) o manca la data")
        tit = unescape(re.search(r"<title>(.*?)</title>", t).group(1))
        des = unescape(re.search(r'<meta name="description" content="([^"]*)"', t).group(1))
        if f"{p3(v[ult])}/Gallon, {db(ult)}" not in tit or f"{p3(v[ult])} per gallon on {db(ult)}" not in des or len(tit) > 65 or len(des) > 160:
            err(f"{perc}: titolo o descrizione senza il prezzo e la data dell'ultima settimana, o troppo lunghi ({len(tit)}/{len(des)})")
        y = _eia_anno_prima(v, ult)
        m = re.search(r"(\d+\.\d)% (higher|lower) than a year earlier", des)
        if nome and y and (not m or f"{'+' if m.group(2) == 'higher' else '−'}{m.group(1)}%" != atteso("r", f"{comb}|{cod}|{ult.isoformat()}|{y.isoformat()}")):
            err(f"{perc}: variazione sull'anno nella descrizione diversa dall'XLS")
        if nome and (nome not in tit or t.count(f"in {nome}") < 3):
            err(f"{perc}: il nome dello Stato manca dal titolo o dal testo")
        # calcolatore: dati nel JSON = XLS; risultato iniziale = Python
        dj = json.loads(re.search(r'<script type="application/json" id="tank-dati">(.*?)</script>', t, re.S).group(1))
        if set(dj["aree"]) != set(attivi[comb]) | {"NUS"}:
            err(f"{perc}: aree del calcolatore diverse dagli Stati con prezzo corrente")
        for c2, a in dj["aree"].items():
            v2 = X[comb][1][c2]
            u2 = max(v2)
            y2 = _eia_anno_prima(v2, u2)
            if a[1:] != [v2[u2], dl(u2), v2[y2] if y2 else None, dl(y2) if y2 else None] or (c2 != "NUS" and a[0] != X[comb][2][c2][1]):
                err(f"{perc}: calcolatore, {c2}: {a} ≠ XLS")
            n_json += 1
        gd = RIS.COMB[comb]["gal"] * 10
        calc = t[t.index('<section class="card calc" id="tank">'):t.index('<script type="application/json" id="tank-dati">')]
        c0 = f"${RIS.costo_pieno(gd, v[ult]) / 100:,.2f}"
        if f'data-t="{comb}|{cod}|{ult.isoformat()}|{gd}">{c0}</b>' not in calc or f"gallons × {p3(v[ult])} = {c0}</p>" not in calc or f'<option value="{cod}" selected>' not in calc:
            err(f"{perc}: risultato iniziale del calcolatore diverso da galloni × ultimo prezzo")
        if y and f"<b data-tank-prima>${RIS.costo_pieno(gd, v[y]) / 100:,.2f}</b>" not in calc:
            err(f"{perc}: calcolatore, costo al prezzo di un anno prima diverso dall'XLS")
        # nessun prezzo a tre decimali fuori dalle celle etichettate (tolti testa, script e il riquadro del calcolatore, controllati qui sopra)
        resto = t[t.index("<body"):].replace(calc, "")
        resto = re.sub(r"<script\b.*?</script>", "", resto, flags=re.S)
        resto = re.sub(r'<span class="gy"[^>]*>[^<]*</span>', "", resto)  # tacche dell'asse dei grafici (numeri tondi, non prezzi)
        resto = re.sub(r'<(\w+)[^>]*? data-(?:p|d|r|m|mp|cpi|t)="[^"]+"[^>]*>.*?</\1>', "", resto, flags=re.S)
        liberi = re.findall(r"\$\d[\d,]*\.\d{2,3}\b", unescape(resto))
        if liberi:
            err(f"{perc}: importi non etichettati (non verificabili): {liberi[:5]}")
        vis = re.sub(r"\s+", " ", testo(t))
        m = EIA_CONSIGLI.search(vis)
        if m:
            err(f"{perc}: frase da consiglio d'acquisto «{m.group(0)}»")
        for serve in ("U.S. Energy Information Administration", "excluding taxes", "not a price quote", "Public domain (work of the U.S. federal government)",
                      "our own calculation", f"release of {dl(_d.fromisoformat(prezzi['combustibili'][comb]['uscita']))}" if RIS.IN_STAGIONE else "start again in October"):
            if serve not in vis:
                err(f"{perc}: manca «{serve}»")
        if t.count("<svg viewBox") < 2 or 'class="lin2"' not in t:
            err(f"{perc}: mancano i due grafici (inverno in corso e scorso, storia)")
        if f"/assets/{G.TANK_FILE}" not in t:
            err(f"{perc}: manca lo script del calcolatore")
    # F. pagine per Stato = Stati con domanda misurata ≥ 100 (controllo indipendente dalla regola del generatore)
    frasi = {}
    for r in json.loads((RADICE / "dati" / "domanda.json").read_text(encoding="utf-8"))["richieste"]:
        if r.get("gruppo") == "riscaldamento":
            for x in [r] + r["simili"]:
                frasi[x["frase"].lower()] = max(frasi.get(x["frase"].lower(), 0), x["volume"] or 0)
    for comb, cod, nome, vol, frase in ps:
        parola = "propane" if comb == "propane" else "oil"
        if frasi.get(frase, 0) != vol or vol < RIS.SOGLIA or parola not in frase or not re.search(r"price|cost", frase) or not (
                nome.lower() in frase or cod.lower() in frase.split()):
            err(f"EIA: pagina {comb}/{nome} senza una frase misurata ≥ {RIS.SOGLIA} che nomini Stato, combustibile e prezzo («{frase}», {vol})")
        if cod not in attivi[comb]:
            err(f"EIA: pagina {comb}/{nome} per uno Stato senza prezzo corrente")
    con = {(c, n) for c, _, n, _, _ in ps}
    for comb in EIA_PRODOTTO:
        for cod in attivi[comb]:
            nome = X[comb][2][cod][1]
            diretta = frasi.get(("heating oil prices " if comb == "oil" else "propane prices ") + nome.lower(), 0)
            if diretta >= RIS.SOGLIA and (comb, nome) not in con:
                err(f"EIA: {nome} ({comb}) ha {diretta} ricerche al mese ma non ha la pagina")
            esiste = (SITO / RIS.percorso(comb, nome) / "index.html").exists()
            if esiste != ((comb, nome) in con):
                err(f"EIA: pagina {comb}/{nome}: esiste={esiste}, attesa={(comb, nome) in con}")
    # G. serie finite (gasolio: Illinois e District of Columbia): l'indice le nomina con la data dell'ultimo prezzo, rifatta dall'XLS
    for comb in EIA_PRODOTTO:
        vis = re.sub(r"\s+", " ", testo((SITO / RIS.COMB[comb]["slug"] / "index.html").read_text(encoding="utf-8")))
        finite = [c for c, v in X[comb][1].items() if len(c) == 2 and c not in attivi[comb] and v]
        for c in finite:
            if f"{X[comb][2][c][1]} (last price: {dl(max(X[comb][1][c]))})" not in vis:
                err(f"EIA: l'indice {comb} non dichiara la serie finita di {X[comb][2][c][1]} con la data dell'ultimo prezzo")
        if finite and f"not counted among the {len(attivi[comb])} states" not in vis:
            err(f"EIA: l'indice {comb} non dice che le serie finite non sono tra i {len(attivi[comb])} Stati")
        if not finite and "series that ha" in vis:
            err(f"EIA: l'indice {comb} parla di serie finite che nell'XLS non ci sono")
        if "second Monday" not in vis:
            err(f"EIA: l'indice {comb} non dice che da aprile a settembre l'EIA rileva un prezzo al mese")
    # H. dati non aggiornati: in stagione le pagine dicono «the next release is scheduled for …»; se quella data è passata da più di una
    # settimana e il file non è stato riletto, le pagine restano ferme senza che nessuno se ne accorga
    for comb in EIA_PRODOTTO:
        pross = _d.fromisoformat(prezzi["combustibili"][comb]["prossima_uscita"])
        if RIS.IN_STAGIONE and (_d.today() - pross).days > 7:
            err(f"EIA: {comb}, la prossima uscita annunciata ({pross}) è passata da {(_d.today() - pross).days} giorni e i prezzi non sono stati "
                f"riletti: lanciare python3 -I inflation/raccolta/eia.py e rigenerare (le pagine dicono ancora «next release … {dl(pross)}»)")
        if RIS.IN_STAGIONE != (RIS.stagione(RIS.ULTIMA) is not None and RIS.stagione(RIS.ULTIMA + timedelta(days=7)) is not None
                               and (RIS.LETTO - RIS.ULTIMA).days <= 14):
            err("EIA: riscaldamento.IN_STAGIONE non segue la regola (ultimo prezzo e lunedì successivo tra ottobre e marzo, letto da non più di 14 giorni)")
    n_o, n_p = sum(c == "oil" for c, _ in con), sum(c == "propane" for c, _ in con)
    ok(f"EIA: {len(pagine_)} pagine (2 indici, {n_o} Stati gasolio, {n_p} Stati propano, ognuno con una frase misurata ≥ {RIS.SOGLIA}/mese): "
       f"{conta['p']} prezzi settimanali, {conta['d']} differenze, {conta['r']} variazioni %, {conta['m'] + conta['mp']} medie per inverno, {conta['cpi']} importi "
       f"in dollari di oggi (CPI-U) e {conta['t']} costi del pieno rifatti dall'XLS, 0 diversi; {n_date} date accanto ai prezzi; nessun importo fuori dalle celle "
       f"etichettate; titolo, descrizione e apertura = ultima settimana; {n_json} aree dei calcolatori = XLS; fonte, tasse escluse, «not a price quote», nessun consiglio")
    tank_motore(X)


def tank_motore(X):
    """Motore del costo del pieno pubblicato (sito/assets/tank.*.js) = riscaldamento.costo_pieno, anche con ogni prezzo corrente dell'XLS."""
    import riscaldamento as RIS
    from fractions import Fraction
    js_file = next((SITO / "assets").glob("tank.*.js"))
    js = js_file.read_text(encoding="utf-8")
    motore_js = js[:js.index("(function(){")]
    rnd = random.Random(23)
    casi = [[rnd.randrange(10, 100001), rnd.randrange(300, 15000)] for _ in range(4000)]
    casi += [[gd, m] for gd in (10, 15, 995, 1375, 2000, 2755, 100000) for m in (1005, 2826, 5667, 5915, 9995)]  # mezzi centesimi compresi
    for comb in X:
        for v in X[comb][1].values():
            casi.append([RIS.COMB[comb]["gal"] * 10, v[max(v)]])
    p = subprocess.run(["node", "-"], input=motore_js + "\nvar K=" + json.dumps(casi) + ";process.stdout.write(JSON.stringify(K.map(function(c){return costoPieno(c[0],c[1]);})));",
                       capture_output=True, text=True)
    if p.returncode:
        err("node (pieno): " + p.stderr[:300])
        return
    diversi = 0
    for (gd, m), j in zip(casi, json.loads(p.stdout)):
        py = RIS.costo_pieno(gd, m)
        if py != j or py != _mezzo_su(Fraction(gd * m, 100)):
            diversi += 1
            if diversi < 4:
                err(f"costo del pieno JS ≠ Python: {gd / 10} gal × {m / 1000}: {j} / {py}")
    if RIS.costo_pieno(2000, 5667) != 113340:
        err("costo del pieno: 200 gal × $5.667 ≠ $1,133.40")
    if not diversi:
        ok(f"costo del pieno pubblicato ({js_file.name}) = Python = galloni × prezzo al centesimo su {len(casi)} casi (mezzi centesimi e ogni prezzo corrente)")


VIETATE_SENZA_DE = ("/de/", "Inflationsrechner", "Destatis", 'lang="de', "Germany")


def sezione_de_spenta():
    """Con SEZIONE_DE = False nessun file di sito/ (HTML, sitemap, netlify.toml, JS, CSS, immagini) nomina la sezione tedesca:
    niente link o redirect a /de/, niente pagine in tedesco, niente attribuzione Destatis, niente "Germany" nei testi."""
    if (SITO / "de").exists():
        err("sezione tedesca spenta ma sito/de/ esiste ancora")
    n = 0
    for f in sorted(SITO.rglob("*")):
        if not f.is_file():
            continue
        n += 1
        b = f.read_bytes()
        for parola in VIETATE_SENZA_DE:
            if parola.encode("utf-8") in b:
                err(f"sezione tedesca spenta ma {f.relative_to(SITO)} contiene «{parola}»")
    ok(f"sezione tedesca spenta (SEZIONE_DE = False): nessuno dei {n} file di sito/ contiene "
       + ", ".join(f"«{p}»" for p in VIETATE_SENZA_DE) + "; sito/de/ assente")


# ---------------------------------------------------------------- 4. browser
def browser():
    lu, uk, de = G.ULT["us"], G.ULT["uk_cpi"], G.ULT["de"]
    casi = [
        {"descr": "US 100 1970 → ultimo mese", "pagina": "/", "importo_testo": "100", "da": [1970, None], "a": list(lu), "k": "us", "foto": "us"},
        {"descr": "US 1,500 gennaio 1980 → 2000 media", "pagina": "/", "importo_testo": "1,500", "da": [1980, 1], "a": [2000, None], "k": "us"},
        {"descr": "US BLS ufficiale 1000 gen 1980 → set 2025", "pagina": "/", "importo_testo": "1000", "da": [1980, 1], "a": [2025, 9], "k": "us", "ufficiale": 4174.81},
        {"descr": "UK CPI 250 2005 → ultimo", "pagina": "/uk/", "importo_testo": "250", "serie": "uk_cpi", "da": [2005, None], "a": list(uk), "k": "uk_cpi", "foto": "uk"},
        {"descr": "UK 1 1950 → ultimo (passa a RPI)", "pagina": "/uk/", "importo_testo": "1", "serie": "uk_cpi", "da": [1950, None], "a": list(uk), "k": "uk_rpi",
         "serie_finale": "uk_rpi"},
        {"descr": "RPI 1000 2000 → ultimo", "pagina": "/uk/rpi-calculator/", "importo_testo": "1000", "da": [2000, None], "a": list(G.ULT["uk_rpi"]), "k": "uk_rpi"},
    ]
    casi_de = [
        {"descr": "DE 1.000 DM 1980 → ultimo", "pagina": "/de/inflationsrechner/", "importo_testo": "1.000", "da": [1980, None], "a": list(de), "k": "de", "valuta": "dm",
         "de": True, "dm": True, "foto": "de"},
        {"descr": "DE 50 € 2010 → 2020", "pagina": "/de/inflationsrechner/", "importo_testo": "50", "da": [2010, None], "a": [2020, None], "k": "de", "de": True, "dm": False},
        {"descr": "DE 100 € 1995 → ultimo", "pagina": "/de/inflationsrechner/", "importo_testo": "100", "da": [1995, None], "a": list(de), "k": "de", "valuta": "eur",
         "de": True, "dm": False},
    ]
    if DE:
        casi += casi_de
    pagine_b = ["/", "/uk/", "/retirement-limits/", "/roth-ira-income-limit/", "/hsa-limit/", "/401k-limit/", "/us/1970-dollars-today/", "/us/inflation-rate-by-year/", "/us/100-dollars-in-1970/", "/uk/inflation-rate-by-year/",
                "/uk/rpi-calculator/", "/how-we-check/", "/does-not-exist/"]
    if DE:
        pagine_b[2:2] = ["/de/inflationsrechner/"]
        pagine_b[-2:-2] = ["/de/inflationsrate-deutschland/"]
    for c in casi:
        imp = float(c["importo_testo"].replace(",", "").replace(".", "")) if c.get("de") else float(c["importo_testo"].replace(",", ""))
        r = M.calcola(C[c["k"]], imp, tuple(c["da"]), tuple(c["a"]), c.get("dm"))
        c["atteso"] = round(r["valore"], 2)
        if c.get("ufficiale") and abs(c["atteso"] - c["ufficiale"]) > 0.005:
            err(f"caso {c['descr']}: motore {c['atteso']} ≠ BLS {c['ufficiale']}")
    link = round(M.calcola(C["us"], 250, (1985, None), (2000, None))["valore"], 2)
    casi_roth = []
    for y, stato, magi, o50, comp in ((PEN.CORRENTE, "single", "160,000", False, ""), (PEN.ULTIMO, "mfj", "255000", True, ""), (2025, "single", "151000", False, ""),
                                      (PEN.CORRENTE, "mfs", "9,990", False, ""), (PEN.ULTIMO, "single", "120000", True, "5000"), (PEN.CORRENTE, "mfj", "300000", False, ""), (PEN.ULTIMO, "mfs_sep", "165,000", False, "")):
        r = PEN.roth_limite(PEN.roth_dati(y), stato, int(magi.replace(",", "")) * 100, o50, int(comp) * 100 if comp else None)
        casi_roth.append({"y": str(y), "s": stato, "m": magi, "e": o50, "c": comp, "atteso": r["limite"] / 100, "esito": r["esito"]})
    # costo del pieno: prezzi letti dall'XLS grezzo dell'EIA (non dal generatore)
    from fractions import Fraction
    casi_tank = []
    xo, xp = _eia_xls("oil")[1], _eia_xls("propane")[1]
    for pagina_, x, g, chip, s, s_def in (("/heating-oil-prices/", xo, "275.5", None, "CT", "NUS"), ("/heating-oil-prices/connecticut/", xo, None, "150", None, "CT"),
                                          ("/heating-oil-prices/connecticut/", xo, "1,000", None, "NUS", "CT"), ("/propane-prices/maine/", xp, "400", None, None, "ME"),
                                          ("/propane-prices/maine/", xp, "0.5", None, None, "ME"), ("/propane-prices/", xp, "abc", None, "WI", "NUS"),
                                          ("/propane-prices/", xp, "137.5", None, "WI", "NUS")):
        v = x[s or s_def]
        u = max(v)
        y = _eia_anno_prima(v, u)
        try:
            gd = round(float((chip or g).replace(",", "")) * 10)
        except ValueError:
            gd = 0
        valido = 10 <= gd <= 100000
        casi_tank.append({"pagina": pagina_, "g": g, "chip": chip, "s": s, "atteso": _mezzo_su(Fraction(gd * v[u], 100)) / 100 if valido else None,
                          "prima": _mezzo_su(Fraction(gd * v[y], 100)) / 100 if valido and y else None, "foto": pagina_ == "/propane-prices/maine/" and g == "400"})
    pagine_b[4:4] = ["/heating-oil-prices/", "/propane-prices/", "/heating-oil-prices/connecticut/", "/propane-prices/maine/"]
    # sezioni 2027: paga minima (ore × tariffa GOV.UK) e affitto massimo (affitto × tetto ufficiale), rifatti qui con le frazioni
    uk27 = json.loads((RADICE / "dati" / "uk_2027.json").read_text(encoding="utf-8"))
    aff27 = json.loads((RADICE / "dati" / "affitti.json").read_text(encoding="utf-8"))
    tar = {v["k"]: v for v in uk27["paga_minima"]["voci"]}
    casi_pay = []
    for k, h_, chip in (("nlw", "40", None), ("nmw_18_20", None, "20"), ("nmw_u18", "12.5", None), ("nmw_app", "abc", None), ("nlw", "0", None), ("nlw", "37.5", None)):
        try:
            od = round(float(chip or h_) * 10)
        except ValueError:
            od = 0
        valido = 10 <= od <= 1000
        f_ = lambda r, per: int(Fraction(r * od * (52 if per != "sett" else 1), 120 if per == "mese" else 10) + Fraction(1, 2)) / 100
        casi_pay.append({"k": k, "h": h_, "chip": chip, "sett": f_(tar[k]["dopo"], "sett") if valido else None, "mese": f_(tar[k]["dopo"], "mese") if valido else None,
                         "anno": f_(tar[k]["dopo"], "anno") if valido else None, "prima": f_(tar[k]["prima"], "anno") if valido else None})
    voci27 = {v["k"]: v for x in aff27["luoghi"] for v in x["voci"]}
    casi_rent = []
    for pagina_, k, per, r_ in (("/rent-increase-cap/", "ca_sf", 1, "3,250"), ("/rent-increase-cap/", "wa", 0, "1234.57"), ("/rent-increase-cap/", "nyc_2", 0, "2100"),
                                ("/rent-increase-cap/", "nyc_1", 1, "2100"), ("/rent-increase-cap/", "on", 1, "abc"), ("/rent-increase-cap/california/", "ca_altre", 0, "1,999.99"),
                                ("/rent-increase-cap/british-columbia/", None, 1, "1850"), ("/rent-increase-cap/saint-paul/", None, 0, "1400")):
        pagina_voci = [k] if k else [v["k"] for x in aff27["luoghi"] if "/rent-increase-cap/" + x["slug"] + "/" == pagina_ for v in x["voci"]][:1]
        t_ = voci27[pagina_voci[0]]["periodi"][per]["tetto"]
        try:
            c_ = round(float(r_.replace(",", "")) * 100)
        except ValueError:
            c_ = None
        inc = int(Fraction(c_ * t_, 100000)) if c_ else None
        casi_rent.append({"pagina": pagina_, "v": k, "p": str(per), "r": r_, "nuovo": (c_ + inc) / 100 if c_ else None, "aumento": inc / 100 if c_ else None,
                          "pct": f"{t_ / 1000:.3f}".rstrip("0").rstrip(".") + "%", "foto": pagina_ == "/rent-increase-cap/" and k == "ca_sf"})
    pagine_b[4:4] = ["/uk/rates-april-2027/", "/uk/minimum-wage-2027/", "/uk/state-pension-2027/", "/uk/benefit-rates-2027/", "/uk/statutory-sick-pay-2027/",
                     "/rent-increase-cap/"] + ["/rent-increase-cap/" + x["slug"] + "/" for x in aff27["luoghi"]]
    env = {"CASI_CALC": json.dumps(casi), "CASI_ROTH": json.dumps(casi_roth), "CASI_TANK": json.dumps(casi_tank), "CASI_PAY": json.dumps(casi_pay), "CASI_RENT": json.dumps(casi_rent), "ATTESO_LINK": str(link), "PAGINE": ",".join(pagine_b), "PATH": "/usr/bin:/bin:/usr/local/bin"}
    import os
    env = dict(os.environ, **env)
    p = subprocess.run(["node", str(RADICE / "verifica_browser.js")], capture_output=True, text=True, env=env, timeout=900)
    try:
        out = json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        err("browser: " + (p.stderr or p.stdout)[-400:])
        return
    for x in out["problemi"]:
        err("browser: " + x)
    if not out["problemi"]:
        ok(f"browser: {out['viste']} viste ({len(pagine_b)} pagine × 375/1280 px × chiaro/scuro) senza scorrimento orizzontale, errori JS o testo < 11 px; "
           f"{out.get('roth', 0)} casi del calcolatore Roth × 2 larghezze = Python; {out.get('pay', 0)} casi della paga minima e {out.get('rent', 0)} dell'affitto massimo × 2 larghezze = conto rifatto; {out.get('tank', 0)} casi del costo del pieno × 2 larghezze = galloni × prezzo dell'XLS EIA (anche pulsanti, altro Stato, valori non validi); {out['casi']} casi del calcolatore × 2 larghezze uguali al motore (anche 1000 $ gen 1980 → set 2025 = 4.174,81 del BLS), cambio CPI→RPI e ritorno al CPI, ottobre 2025 non selezionabile, link condiviso, link «in dollari di oggi» delle pagine EIA = calcolatore, tema")


def main():
    dati()
    motore()
    pagine()
    if "--browser" in sys.argv:
        browser()
    for x in OK:
        print("ok  ", x)
    for x in AVV:
        print("AVV ", x)
    for x in ERR:
        print("ERR ", x)
    print(f"\n{len(ERR)} errori, {len(AVV)} avvisi")
    sys.exit(1 if ERR else 0)


if __name__ == "__main__":
    main()
