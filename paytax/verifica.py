"""Controlli di Payroll Tax by State (paytax/sito/) prima di pubblicare.

Uso (dalla radice del repository):
    python3 paytax/verifica.py              # controlli sui file (senza rete)
    python3 paytax/verifica.py --rete       # + rilettura di tutte le fonti ufficiali (HTTP 200 e frasi ancora presenti)
    python3 paytax/verifica.py --browser    # + Playwright: 375 e 1280 px, chiaro e scuro, calcolatore (verifica_browser.js)

Cosa controlla:
 1. Fonti: ogni fonte di dati/fonti.json letta con HTTP 200, impronta SHA-256 e tutte le frasi cercate trovate, oppure
    dichiarata non letta con il motivo (ATO, ACT Revenue Office, NT Treasury: 403 Cloudflare, mai aggirato).
    Con --rete le rilegge oggi; "Last updated" più recente del nostro controllo = avviso.
 2. Parametri: ogni cifra di dati/giurisdizioni.json (soglie, aliquote, rapporti) è scritta in una frase trovata
    nella sua pagina ufficiale; aliquote tra 0 e 10 %; anno fiscale non scaduto.
 3. Esempi ufficiali (dati/esempi_ufficiali.json): ricalcolati con motore.py e con il JS pubblicato; tabella RevenueSA,
    scaglioni ACT, regole NT, soglie mensili NSW, soglie delle sovrattasse VIC.
 4. JS = Python: il motore nel file app.*.js pubblicato e motore.py danno gli stessi numeri su 5.000 casi casuali
    (anni parziali, regionali, gruppi grandi, Stati a zero); coerenza (nessuna imposta negativa, soglia ripartita ≤ piena).
 5. Numeri stampati: risultato statico della home e dati del calcolatore uguali al motore; nessun segnaposto.
 6. FAQ: ogni domanda viene da una ricerca salvata (dati/domanda.json, gl=au); JSON-LD FAQPage = testo visibile.
 7. Struttura: canonical, titoli, descrizioni, link interni e ancore, sitemap = pagine con canonical, file accessori,
    contatore GoatCounter in ogni pagina, fonti con data di controllo in ogni pagina di contenuto; parole del contenuto proprio
    (solo <main>, senza calcolatore, fonti, griglie e avviso): almeno 500, almeno 900 per payday-super, regional-rates,
    what-changed-2026-27 e how-we-check; modulo Netlify "corrections" con honeypot e consenso; spazio pubblicitario
    sempre dopo il calcolatore.
 8. Monetizzazione: controlli comuni (monetizzazione.py); nessun link di affiliazione finché i riquadri sono spenti;
    il riquadro, se acceso, ha rel="sponsored noopener" e la riga di trasparenza.
 9. Niente dati personali, niente nomi di modelli AI nei file del sito e nel codice.
"""
import json
import math
import random
import re
import subprocess
import sys
import tempfile
from datetime import date
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
SITO = RADICE / "sito"
sys.path.insert(0, str(RADICE))
sys.path.insert(0, str(RADICE / "raccolta"))
import genera as G  # noqa: E402
import monetizzazione as MON  # noqa: E402
import motore  # noqa: E402

ERRORI = []
AVVISI = []


def errore(m):
    ERRORI.append(m)


def testo(html):
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", t))).strip()


def pagine():
    return sorted(SITO.rglob("*.html"))


def percorso_di(f):
    rel = f.relative_to(SITO).as_posix()
    return rel[:-len("index.html")] if rel.endswith("index.html") else rel


MESI = {m.lower(): i + 1 for i, m in enumerate(G.MESI)}


def data_agg(t):
    """'Last updated: 01 July 2026' / 'Updated: 29 September 2026' / 'Last updated on: 28/10/2026' -> date."""
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", t)
    if m:
        return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    m = re.search(r"(\d{1,2}) ([A-Za-z]+) (\d{4})", t)
    if m and m.group(2).lower() in MESI:
        return date(int(m.group(3)), MESI[m.group(2).lower()], int(m.group(1)))
    return None


# ---------------------------------------------------------------- 1. fonti
def controlla_fonti(rete):
    lette = non_lette = frasi = 0
    controllo = G.CONTROLLO
    for fid, f in G.FONTI.items():
        e = G.ESITI.get(fid)
        if not e:
            errore(f"fonte {fid}: nessun esito in dati/fonti.json (lanciare raccolta/fonti.py)")
            continue
        if f.get("non_letta"):
            non_lette += 1
            if not (f.get("motivo") and e.get("motivo")):
                errore(f"fonte {fid}: non letta senza motivo scritto")
            continue
        lette += 1
        if e.get("http") != 200 or not re.fullmatch(r"[0-9a-f]{64}", e.get("sha256", "")):
            errore(f"fonte {fid}: HTTP {e.get('http')} o impronta mancante")
        trovate = e.get("trovate", {})
        mancano = [c for c, ok in trovate.items() if not ok]
        if mancano or set(trovate) != set(f.get("cerca", [])):
            errore(f"fonte {fid}: frasi non trovate o non controllate: {mancano or sorted(set(f.get('cerca', [])) - set(trovate))}")
        frasi += len(trovate)
        d = data_agg(e.get("aggiornata", "")) if e.get("aggiornata") else None
        if d and d > controllo:
            AVVISI.append(f"fonte {fid}: la pagina dice «{e['aggiornata']}», dopo il nostro controllo del {controllo}: rileggere le cifre")
    if rete:
        import fonti as RF
        for fid, f in G.FONTI.items():
            if f.get("non_letta"):
                continue
            nuovo = RF.controlla(fid, f)
            if nuovo["http"] != 200:
                errore(f"fonte {fid}: oggi HTTP {nuovo['http']} (registrata 200)")
                continue
            mancano = [c for c, ok in nuovo.get("trovate", {}).items() if not ok]
            if mancano:
                errore(f"fonte {fid}: oggi mancano le frasi {mancano}: la pagina è cambiata, ricontrollare le cifre")
            vecchia = G.ESITI.get(fid, {}).get("aggiornata")
            if nuovo.get("aggiornata") and nuovo.get("aggiornata") != vecchia:
                AVVISI.append(f"fonte {fid}: data della pagina cambiata ({vecchia} -> {nuovo['aggiornata']})")
            if nuovo.get("sha256") != G.ESITI.get(fid, {}).get("sha256"):
                AVVISI.append(f"fonte {fid}: il testo è cambiato dall'ultima lettura (le frasi controllate ci sono ancora)")
    print(f"1. Fonti: {lette} lette con HTTP 200 e impronta, {frasi} frasi trovate, {non_lette} non lette con motivo scritto"
          f"{' (rilette oggi in rete)' if rete else ''}.")


# ---------------------------------------------------------------- 2. parametri
def num_it(x, sep=","):
    return f"{x:,.0f}".replace(",", sep)


def controlla_parametri():
    P = G.P
    trovate = {fid: [c for c, ok in G.ESITI.get(fid, {}).get("trovate", {}).items() if ok] for fid in G.FONTI}

    def deve(fid, frammento, cosa):
        if not any(frammento in c for c in trovate.get(fid, [])):
            errore(f"parametro {cosa}: «{frammento}» non è in nessuna frase trovata nella fonte {fid}")

    def pc(x):
        return f"{x:g}%"
    deve("nsw_rates", f"${num_it(P['nsw']['soglia'])}", "nsw.soglia")
    deve("nsw_rates", pc(P["nsw"]["aliquota"]), "nsw.aliquota")
    v = P["vic"]
    deve("vic_rates", f"${num_it(v['soglia'])}", "vic.soglia")
    deve("vic_rates", pc(v["aliquota"]), "vic.aliquota")
    deve("vic_rates", pc(v["regionale"]), "vic.regionale")
    deve("vic_rates", f"it is {v['phase_quota']:g}%", "vic.phase_quota")
    deve("vic_rates", f"between ${num_it(v['phase_da'])} and ${num_it(v['phase_a'])}", "vic.phase_da/a")
    deve("vic_rates", f"above ${v['sovrattasse'][0][0] / 1e6:g} million will pay a combined {v['sovrattasse'][0][1]:g}%", "vic.sovrattasse[0]")
    deve("vic_rates", f"above ${v['sovrattasse'][1][0] / 1e6:g} million will pay a combined {v['sovrattasse'][0][1] + v['sovrattasse'][1][1]:g}%", "vic.sovrattasse[1]")
    q = P["qld"]
    deve("qld_rates", f"${q['soglia'] / 1e6:g} million", "qld.soglia")
    deve("qld_deductions", f"$1 for every ${q['rapporto']}", "qld.rapporto")
    deve("qld_rates", f"{q['aliquota']:g}% for employers or groups of employers who pay ${q['aliquota_alta_da'] / 1e6:g} million or less", "qld.aliquota")
    deve("qld_rates", f"{q['aliquota_alta']:g}% for employers or groups of employers who pay more than", "qld.aliquota_alta")
    deve("qld_regional", f"{q['aliquota'] - q['sconto_regionale']:g}% for employers", "qld.sconto_regionale")
    deve("qld_regional", f"more than ${q['regionale_max'] / 1e6:g} million", "qld.regionale_max")
    deve("portal_rates", f"Additional {q['levy'][0][1]:g}% (primary rate) more than ${q['levy'][0][0] / 1e6:g} million", "qld.levy[0]")
    deve("portal_rates", f"+ {q['levy'][1][1]:g}% (additional rate) more than ${q['levy'][1][0] / 1e6:g} million", "qld.levy[1]")
    w = P["wa"]
    deve("wa_calc", f"${num_it(w['soglia'])} - [", "wa.soglia")
    deve("wa_calc", f"upper threshold of ${num_it(w['soglia_superiore'])}", "wa.soglia_superiore")
    deve("wa_calc", f"payroll tax rate is {w['aliquota']:g}%", "wa.aliquota")
    tv = w["soglia"] / (w["soglia_superiore"] - w["soglia"])
    if abs(tv - 2 / 13) > 1e-12:
        errore(f"wa: tapering value {tv} diverso da 2/13 scritto dall'ufficio")
    sa = P["sa"]
    deve("sa_act", f"TA or threshold amount is ${num_it(sa['soglia'], ' ')}", "sa.soglia")
    deve("sa_act", f"EA is ${num_it(sa['deduzione'], ' ')}", "sa.deduzione")
    deve("sa_act", f"more than ${num_it(sa['piena_da'], ' ')}, R is {sa['aliquota']:g}%", "sa.piena_da/aliquota")
    t = P["tas"]
    deve("tas_rates", f"0 to {num_it(t['soglia'], ' ')} 0 {num_it(t['soglia'] + 1, ' ')} to {num_it(t['soglia2'], ' ')} {t['aliquota1']:g} {num_it(t['soglia2'] + 1, ' ')} and above {t['aliquota2']:g}", "tas")
    a = P["act"]
    deve("act_det2026", f"is ${num_it(a['soglia'], ' ')}", "act.soglia")
    prec = a["soglia"]
    for lim, al in a["scaglioni"]:
        if lim is None:
            deve("act_det2026", f"more than ${prec / 1e6:g} million {al:g} per cent", "act.scaglione finale")
        else:
            deve("act_det2026", f"more than ${prec / 1e6:g} million but not more than ${lim / 1e6:g} million {al:g} per cent", f"act.scaglione {lim}")
            prec = lim
    n = P["nt"]
    deve("nt_act", f"TA or threshold amount means ${num_it(n['soglia'], ' ')}", "nt.soglia")
    deve("nt_act", f"the rate of payroll tax is {n['aliquota']:g}%", "nt.aliquota")
    deve("nt_act", f"is {n['aliquota_alta']:g}% if either", "nt.aliquota_alta")
    deve("nt_act", f"the threshold amount is ${num_it(n['aliquota_alta_da'], ' ')}", "nt.aliquota_alta_da")
    for s in motore.ORDINE:
        for k, x in P[s].items():
            if ("aliquota" in k and not k.endswith("_da")) or k == "regionale":
                if not 0 < x < 10:
                    errore(f"{s}.{k} = {x}: aliquota fuori scala")
    oggi = date.today()
    fine = date.fromisoformat(G.GJ["fine"])
    if oggi > fine:
        errore(f"oggi {oggi} è dopo la fine dell'anno fiscale {G.ANNO} ({fine}): aggiornare i dati (NOTE.md, procedura del 1° luglio)")
    if G.GIORNI_ANNO != (fine - date.fromisoformat(G.GJ["inizio"])).days + 1:
        errore("giorni_anno non coincide con le date dell'anno fiscale")
    print(f"2. Parametri {G.ANNO}: ogni soglia e aliquota delle 8 giurisdizioni è scritta nella sua fonte ufficiale; anno fiscale in corso.")


# ---------------------------------------------------------------- motore JS pubblicato
def js_motore():
    f = next((SITO / "assets").glob("app.*.js"))
    js = f.read_text(encoding="utf-8")
    parte = js.split("(function(){")[0]
    if "function calcola(" not in parte:
        errore("JS: motore non trovato nel file pubblicato")
    return parte


def esegui_js(casi):
    """casi: [{"P": parametri, "salari", "giorni", "rv", "rq"}] -> risultati del JS pubblicato."""
    prog = js_motore() + "\nconst fs=require('fs');const C=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));" \
        "console.log(JSON.stringify(C.map(function(c){return calcola(c.P,c.salari,c.giorni,365,c.rv,c.rq);})));"
    with tempfile.TemporaryDirectory() as d:
        pj, pc = Path(d) / "m.js", Path(d) / "c.json"
        pj.write_text(prog, encoding="utf-8")
        pc.write_text(json.dumps(casi), encoding="utf-8")
        r = subprocess.run(["node", str(pj), str(pc)], capture_output=True, text=True, timeout=300)
    if r.returncode:
        errore(f"node non esegue il motore JS: {r.stderr[:400]}")
        return None
    return json.loads(r.stdout)


def uguali(a, b):
    if a is None or b is None:
        return a is b
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


def confronta(py, js, nome):
    diff = []
    for k in ("W", "f", "totale", "extra", "complessivo", "mensile"):
        if not uguali(py[k], js[k]):
            diff.append(f"{k} {py[k]} vs {js[k]}")
    if py["non_calcolati"] != js["non_calcolati"] or len(py["righe"]) != len(js["righe"]):
        diff.append("righe o non calcolati diversi")
    else:
        for rp, rj in zip(py["righe"], js["righe"]):
            for k in ("soglia", "imponibile", "aliquota", "tassa", "extra"):
                if not uguali(rp[k], rj[k]):
                    diff.append(f"{rp['s']}.{k} {rp[k]} vs {rj[k]}")
            if rp["stato"] != rj["stato"] or rp["avvisi"] != rj["avvisi"]:
                diff.append(f"{rp['s']} stato/avvisi {rp['stato']}{rp['avvisi']} vs {rj['stato']}{rj['avvisi']}")
    if diff:
        errore(f"JS ≠ Python ({nome}): " + "; ".join(diff[:4]))
    return not diff


# ---------------------------------------------------------------- 3. esempi ufficiali
def parametri_con(over):
    par = json.loads(json.dumps(G.P))
    for s, v in (over or {}).items():
        par[s].update(v)
    return par


def controlla_esempi():
    E = G.ESEMPI
    casi_js, n = [], 0
    for c in E["casi"]:
        if c["fonte"] not in G.FONTI:
            errore(f"esempio {c['id']}: fonte {c['fonte']} inesistente")
        par = parametri_con(c.get("parametri"))
        giorni = c.get("giorni", 365)
        res = motore.calcola(par, c["salari"], giorni, 365)
        casi_js.append({"P": par, "salari": c["salari"], "giorni": giorni, "rv": False, "rq": False})
        per = {r["s"]: r for r in res["righe"]}
        for chiave, atteso in c["atteso"].items():
            s, campo = chiave.split(".")
            div = 1
            if "/" in campo:
                campo, d = campo.split("/")
                div = int(d)
            v = per[s][campo] / div
            n += 1
            if abs(v - atteso) > c["toll"]:
                errore(f"esempio ufficiale {c['id']}: {chiave} = {v:.4f}, l'ufficio scrive {atteso} (tolleranza {c['toll']})")
    js = esegui_js(casi_js)
    if js:
        for c, cj, r in zip(E["casi"], casi_js, js):
            confronta(motore.calcola(cj["P"], cj["salari"], cj["giorni"], 365), r, "esempio " + c["id"])
    # tabella indicativa RevenueSA: ogni riga entro 0,01 punti dalla formula della legge
    righe = E["sa_tabella"]["righe"]
    peggiore = 0.0
    for W, tab in righe:
        r = motore.calcola_stato("sa", G.P, W, W, 1.0)
        nostro = (r["aliquota"] or 0) * 100
        peggiore = max(peggiore, abs(nostro - tab))
        if abs(nostro - tab) > 0.01 + 1e-9:
            errore(f"SA: con ${W:,} la formula dà {nostro:.4f}%, la tabella RevenueSA {tab}%")
    if len(righe) != 200:
        errore(f"SA: attese 200 righe della tabella, trovate {len(righe)}")
    # scaglioni ACT
    for W, al in E["scaglioni_act"]["casi"]:
        r = motore.calcola_stato("act", G.P, W, W, 1.0)
        if not uguali(r["aliquota"], al / 100):
            errore(f"ACT: con ${W:,} aliquota {r['aliquota']} invece di {al}%")
    # regole NT
    for c in E["nt_legge"]["casi"]:
        W = c["W"]
        r = motore.calcola_stato("nt", G.P, W, W, 1.0)
        if "AD" in c and not uguali(r["soglia"], c["AD"]):
            errore(f"NT: con ${W:,} deduzione {r['soglia']} invece di {c['AD']}")
        if "R" in c and not uguali(r["aliquota"], c["R"] / 100):
            errore(f"NT: con ${W:,} aliquota {r['aliquota']} invece di {c['R']}%")
    for giorni, atteso in E["soglie_mensili_nsw"]["casi"]:
        if math.floor(G.P["nsw"]["soglia"] * giorni / 365 + 0.5) != atteso:
            errore(f"NSW: soglia mensile di {giorni} giorni diversa da {atteso}")
    for c in E["soglie_sovrattasse_vic"]["casi"]:
        v = c["lim"] * c["q"] * c["giorni"] / 365  # stessa espressione del motore (lim × q × f)
        if abs(v - c["atteso"]) > c["toll"]:
            errore(f"VIC sovrattasse: soglia {v:.2f} invece di {c['atteso']}")
    legge = sum(1 for c in E["casi"] if c.get("legge"))
    print(f"3. Esempi: {len(E['casi']) - legge} ufficiali + {legge} dalla formula della legge (VIC anno parziale), {n} cifre entro la tolleranza, anche nel JS; tabella RevenueSA {len(righe)} righe "
          f"(scarto massimo {peggiore:.4f} punti); {len(E['scaglioni_act']['casi'])} limiti ACT; {len(E['nt_legge']['casi'])} regole NT; soglie mensili NSW e sovrattasse VIC.")


# ---------------------------------------------------------------- 4. JS = Python su casi casuali + coerenza
def casi_casuali(n, seme=20261111):
    rnd = random.Random(seme)
    scale = [0, 50_000, 300_000, 900_000, 1_250_000, 1_600_000, 2_400_000, 4_000_000, 7_000_000, 12_000_000, 60_000_000, 140_000_000, 400_000_000]
    casi = []
    for i in range(n):
        sal = {}
        k = rnd.choice([1, 1, 2, 3, 4, 8])
        for s in rnd.sample(motore.ORDINE, k):
            base = rnd.choice(scale)
            sal[s] = round(base * rnd.uniform(0.5, 1.6), rnd.choice([0, 2])) if base else 0
        if rnd.random() < 0.25:
            sal["altro"] = rnd.choice([0, 500_000, 3_000_000, 20_000_000])
        giorni = rnd.choice([365] * 6 + [1, 31, 120, 184, 200, 300, 364])
        casi.append({"P": G.P, "salari": sal, "giorni": giorni, "rv": rnd.random() < 0.3, "rq": rnd.random() < 0.3})
    # casi limite scritti a mano: soglie esatte e confini degli scaglioni
    for s, W in [("nsw", 1_200_000), ("vic", 3_000_000), ("vic", 5_000_000), ("qld", 6_500_000), ("qld", 10_400_000), ("wa", 1_000_000), ("wa", 7_500_000),
                 ("sa", 1_500_000), ("sa", 1_700_000), ("tas", 1_250_000), ("tas", 2_000_000), ("act", 1_750_000), ("act", 20_000_000), ("act", 150_000_001),
                 ("nt", 2_500_000), ("nt", 7_500_000), ("nt", 100_000_000), ("qld", 350_000_001), ("vic", 100_000_001)]:
        for giorni in (365, 200):
            casi.append({"P": G.P, "salari": {s: W}, "giorni": giorni, "rv": True, "rq": True})
    return casi


def controlla_js_python():
    casi = casi_casuali(5000)
    js = esegui_js(casi)
    if js is None:
        return
    ok = 0
    incoerenti = 0
    piene = {"nsw": "soglia", "vic": "soglia", "qld": "soglia", "wa": "soglia", "sa": "deduzione", "tas": "soglia", "act": "soglia", "nt": "soglia"}
    for i, (c, rj) in enumerate(zip(casi, js)):
        py = motore.calcola(c["P"], c["salari"], c["giorni"], 365, c["rv"], c["rq"])
        if confronta(py, rj, f"caso casuale {i}"):
            ok += 1
        for r in py["righe"]:
            if r["tassa"] < 0 or r["extra"] < 0 or r["imponibile"] < 0 or r["soglia"] < 0:
                incoerenti += 1
                errore(f"caso {i}: valori negativi in {r['s']}: {r}")
            elif r["stato"] in ("ok",) and r["soglia"] > G.P[r["s"]][piene[r["s"]]] + 1e-6 and r["s"] != "qld":
                incoerenti += 1
                errore(f"caso {i}: soglia ripartita {r['soglia']:.2f} oltre la soglia piena di {r['s']}")
            elif r["aliquota"] is not None and not 0 <= r["aliquota"] < 0.1:
                incoerenti += 1
                errore(f"caso {i}: aliquota {r['aliquota']} fuori scala in {r['s']}")
        if len(ERRORI) > 40:
            break
    print(f"4. Calcolatore: JS pubblicato e motore.py uguali in {ok} casi su {len(casi)} (casuali e limite); {incoerenti} incoerenze.")


# ---------------------------------------------------------------- 5. numeri stampati
def controlla_stampati():
    t = (SITO / "index.html").read_text(encoding="utf-8")
    res = motore.calcola(G.P, G.ESEMPIO_HOME, 365, 365)
    m = re.search(r'data-o="totale">([^<]+)<', t)
    if not m or m.group(1) != G.soldi(res["complessivo"]):
        errore(f"home: totale stampato {m.group(1) if m else '?'} invece di {G.soldi(res['complessivo'])}")
    for r in res["righe"]:
        m = re.search(rf'data-o="tassa-{r["s"]}">([^<]+)<', t)
        if not m or m.group(1) != G.soldi(r["tassa"]):
            errore(f"home: imposta {r['s']} stampata {m.group(1) if m else '?'} invece di {G.soldi(r['tassa'])}")
    n = 0
    for f in pagine():
        h = f.read_text(encoding="utf-8")
        for blocco in re.findall(r'<script type="application/json" id="calc-dati">(.*?)</script>', h, re.S):
            d = json.loads(blocco)
            n += 1
            if d["parametri"] != G.P or d["giorni_anno"] != G.GIORNI_ANNO:
                errore(f"{f.relative_to(SITO)}: parametri del calcolatore diversi da dati/giurisdizioni.json")
            for c in d["campi"]:
                if not re.search(rf'name="{c}"', h):
                    errore(f"{f.relative_to(SITO)}: campo {c} del calcolatore assente")
        if re.search(r"\{(bc|s|g|ANNO)\}|\[\[[a-z_, ]+\]\]|\bNone\b|\bnan\b", testo(h)):
            errore(f"{f.relative_to(SITO)}: segnaposto o valore vuoto nel testo")
    print(f"5. Numeri stampati: risultato della home uguale al motore; {n} calcolatori con i parametri di {G.ANNO}; nessun segnaposto.")


# ---------------------------------------------------------------- 6. FAQ
def controlla_faq():
    tutte = set()
    for v in json.loads((RADICE / "dati" / "domanda.json").read_text(encoding="utf-8"))["radici"].values():
        if isinstance(v, list):
            tutte |= set(v)
    for x in G.FAQ:
        if x["ricerca"] not in tutte:
            errore(f"FAQ «{x['q']}»: la ricerca «{x['ricerca']}» non è nell'autocompletamento salvato")
        for i in x["fonti"]:
            if i not in G.FONTI:
                errore(f"FAQ «{x['q']}»: fonte {i} inesistente")
    n = 0
    for f in pagine():
        t = f.read_text(encoding="utf-8")
        for blocco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
            d = json.loads(blocco)
            if d.get("@type") != "FAQPage":
                continue
            visibile = re.sub(r"\s*\[\d+\](,\[\d+\])*", "", testo(t))
            for q in d["mainEntity"]:
                n += 1
                if re.sub(r"\s+", " ", q["name"]) not in visibile:
                    errore(f"{f.relative_to(SITO)}: domanda JSON-LD non visibile: {q['name']}")
                if re.sub(r"\s+", " ", q["acceptedAnswer"]["text"]) not in visibile:
                    errore(f"{f.relative_to(SITO)}: risposta JSON-LD diversa dal testo: {q['name']}")
    if n != len(G.FAQ):
        errore(f"FAQ: {n} domande nelle pagine, {len(G.FAQ)} in dati/faq.json")
    print(f"6. FAQ: {n} domande da ricerche vere (Google gl=au); JSON-LD FAQPage uguale al testo visibile.")


# ---------------------------------------------------------------- 7. struttura
SENZA_FONTI = {"about/", "privacy/", "404.html"}
CONTEGGI = {}
PAGINE_900 = {"payday-super/", "regional-rates/", "what-changed-2026-27/", "how-we-check/"}


def parole_uniche(html):
    """Parole del contenuto proprio della pagina: solo <main>, senza il calcolatore (uguale in più pagine), l'elenco delle fonti,
    le griglie delle guide e degli Stati e l'avviso finale (blocchi ripetuti)."""
    m = re.search(r"<main\b.*?</main>", html, re.S)
    t = m.group(0) if m else html
    t = re.sub(r'<section class="card calc[^"]*".*?</section>', " ", t, flags=re.S)
    t = re.sub(r'<section class="fonti-box".*?</section>', " ", t, flags=re.S)
    t = re.sub(r'<h2>(Guides|Other states and territories)</h2>\s*<ul class="griglia[^"]*">.*?</ul>', " ", t, flags=re.S)
    t = re.sub(r'<p class="disclaimer">.*?</p>', " ", t, flags=re.S)
    return len(testo(t).split())


def controlla_struttura():
    esistenti = {percorso_di(f) for f in pagine()}
    canonici = set()
    for f in pagine():
        t = f.read_text(encoding="utf-8")
        nome = str(f.relative_to(SITO))
        p = percorso_di(f)
        m = re.search(r'<link rel="canonical" href="([^"]+)"', t)
        if m:
            canonici.add(m.group(1))
            if m.group(1) != f"{G.URL_SITO}/{p}":
                errore(f"{nome}: canonical {m.group(1)} diverso dall'indirizzo")
        elif f.name != "404.html":
            errore(f"{nome}: né canonical né 404")
        tit = re.search(r"<title>(.*?)</title>", t)
        if not tit or len(unescape(tit.group(1))) > 65:
            errore(f"{nome}: titolo assente o oltre 65 caratteri ({unescape(tit.group(1)) if tit else ''})")
        des = re.search(r'<meta name="description" content="([^"]*)"', t)
        if m and (not des or not 70 <= len(unescape(des.group(1))) <= 165):
            errore(f"{nome}: descrizione assente o di lunghezza strana ({len(unescape(des.group(1))) if des else 0})")
        if t.count("<h1") != 1:
            errore(f"{nome}: {t.count('<h1')} titoli h1")
        if G.GOATCOUNTER_URL not in t:
            errore(f"{nome}: manca il contatore GoatCounter")
        if 'lang="en-AU"' not in t:
            errore(f"{nome}: lingua della pagina non en-AU")
        if m and p not in SENZA_FONTI:
            if 'class="fonti-box"' not in t or not re.search(r"checked \d{1,2} [A-Z][a-z]+ 20\d\d", testo(t)):
                errore(f"{nome}: pagina di contenuto senza elenco delle fonti con data di controllo")
        if "General information, not tax advice" not in t:
            errore(f"{nome}: manca l'avviso «General information, not tax advice»")
        for href in re.findall(r'href="([^"]+)"', t):
            href = unescape(href)
            if href.startswith(("http", "mailto:", "//")):
                continue
            if href.startswith("#"):
                if f'id="{href[1:]}"' not in t:
                    errore(f"{nome}: ancora {href} inesistente")
                continue
            if not href.startswith("/"):
                errore(f"{nome}: link relativo {href}")
                continue
            path, _, anc = href[1:].partition("#")
            path = path.split("?")[0]
            if path.startswith("assets/"):
                if not (SITO / path.split("#")[0]).exists():
                    errore(f"{nome}: risorsa mancante {href}")
                continue
            if path not in esistenti:
                errore(f"{nome}: link interno rotto {href}")
            elif anc:
                dest = SITO / (path + "index.html" if path.endswith("/") or path == "" else path)
                if f'id="{anc}"' not in dest.read_text(encoding="utf-8"):
                    errore(f"{nome}: ancora #{anc} inesistente in {path}")
    sm = set(re.findall(r"<loc>([^<]+)</loc>", (SITO / "sitemap.xml").read_text(encoding="utf-8")))
    if sm != canonici:
        errore(f"sitemap ≠ pagine con canonical: in più {sorted(sm - canonici)[:5]}, mancano {sorted(canonici - sm)[:5]}")
    attese = ["", "calculator/"] + [f"{s}/" for s in motore.ORDINE] + ["interstate-wages/", "grouping/", "regional-rates/", "thresholds-history/", "due-dates/",
                                                                       "what-changed-2026-27/", "payday-super/", "over-the-threshold/", "about/", "how-we-check/", "privacy/"]
    for p in attese:
        if f"{G.URL_SITO}/{p}" not in canonici:
            errore(f"pagina richiesta dal piano mancante: /{p}")
    for nome in ("robots.txt", "netlify.toml", "404.html", f"{G.CHIAVE_INDEXNOW}.txt", "assets/og.png", "sitemap.xml"):
        if not (SITO / nome).exists():
            errore(f"manca {nome}")
    if (SITO / f"{G.CHIAVE_INDEXNOW}.txt").read_text(encoding="utf-8") != G.CHIAVE_INDEXNOW:
        errore("file della chiave IndexNow diverso dalla chiave")
    hw = (SITO / "how-we-check" / "index.html").read_text(encoding="utf-8")
    for pezzo in ('name="corrections"', 'data-netlify="true"', 'netlify-honeypot="bot-field"', 'name="bot-field"', 'name="form-name" value="corrections"',
                  'name="consent"', 'id="corrections"'):
        if pezzo not in hw:
            errore(f"modulo correzioni: manca {pezzo}")
    if 'name="email" maxlength="200" autocomplete="email">' not in hw or 'type="email" name="email" maxlength="200" autocomplete="email" required' in hw:
        errore("modulo correzioni: l'email deve esserci ed essere facoltativa")
    if 'href="/how-we-check/#corrections"' not in (SITO / "privacy" / "index.html").read_text(encoding="utf-8"):
        errore("privacy: non spiega il modulo correzioni")
    for f in pagine():
        t = f.read_text(encoding="utf-8")
        i, j = t.find('class="ad-slot"'), t.find('id="calculator"')
        if i >= 0 and j >= 0 and i < j:
            errore(f"{f.relative_to(SITO)}: spazio pubblicitario prima del calcolatore")
    robots = (SITO / "robots.txt").read_text(encoding="utf-8")
    if f"Sitemap: {G.URL_SITO}/sitemap.xml" not in robots:
        errore("robots.txt senza la sitemap")
    conteggi = {percorso_di(f): parole_uniche(f.read_text(encoding="utf-8")) for f in pagine() if f.name != "404.html" and percorso_di(f) not in SENZA_FONTI}
    # minimo 500 parole proprie per ogni pagina di contenuto; 900 per le guide segnalate dalla revisione del 11/11/2026
    piccole = {p: n for p, n in conteggi.items() if n < (900 if p in PAGINE_900 else 500)}
    if piccole:
        errore(f"pagine con poco contenuto proprio (solo <main>, senza calcolatore, fonti, guide, avviso): {piccole}")
    global CONTEGGI
    CONTEGGI = conteggi
    minimo = min(CONTEGGI.items(), key=lambda x: x[1]) if CONTEGGI else ("", 0)
    print(f"7. Struttura: {len(esistenti)} pagine, {len(canonici)} con canonical = sitemap; tutte le 21 pagine del piano; link e ancore validi; fonti datate e avviso in ogni pagina; "
          f"contenuto proprio (solo <main>, senza blocchi ripetuti) minimo {minimo[1]} parole (/{minimo[0]}), ≥ 900 per {', '.join(sorted(PAGINE_900))}.")


# ---------------------------------------------------------------- 8. monetizzazione
def controlla_monetizzazione():
    err, info = MON.controlla_sito(G.SITO_ID, SITO)
    for e in err:
        errore("monetizzazione: " + e)
    if not G.ci_sono_affiliati() and info["link_affiliati"]:
        errore(f"affiliati spenti ma {info['link_affiliati']} link di affiliazione nel sito")
    for k, v in G.AFF.items():
        if k.startswith("_"):
            continue
        u = (v.get("url") or "").strip()
        if u and not u.startswith("https://"):
            errore(f"affiliati.json {k}: url non valido")
        if v.get("attivo") and u and not MON.dominio_ammesso(u):
            errore(f"affiliati.json {k}: dominio non ammesso in monetizzazione.json ({u})")
    finto = {"employment_hero": {**G.AFF["employment_hero"], "attivo": True, "url": "https://example.partnerstack.test/eh"},
             "myob": {**G.AFF["myob"], "attivo": True, "url": "https://example.myob.test/aff"}}
    box = G.box_affiliati("payday-super", aff=finto)
    if 'rel="sponsored noopener"' not in box or MON.RIGA_EN not in box or box.count("<li>") != 2:
        errore("riquadro affiliati (prova con programmi accesi): rel, riga di trasparenza o voci mancanti")
    if G.box_affiliati("payday-super") != "":
        errore("riquadro affiliati presente ma i programmi sono spenti")
    print(MON.riepilogo(G.SITO_ID, info, err) + f"; riquadri affiliati {'accesi' if G.ci_sono_affiliati() else 'preparati e spenti (prova di resa superata)'}.")


# ---------------------------------------------------------------- 9. parole vietate
def controlla_parole():
    vietate = re.compile(r"Massimiliano|\bCori\b|@[a-z0-9-]+\.(it|com|fr|es|au)\b|\+39|Cl[a]ude|Anthr[o]pic|\bOp[u]s\b|\bSonn[e]t\b|\bG[P]T\b|Chat[G]PT|Gem[i]ni", re.I)
    file = list(pagine()) + [SITO / "sitemap.xml", SITO / "robots.txt"] + list(RADICE.glob("*.py")) + list((RADICE / "raccolta").glob("*.py")) \
        + list((RADICE / "dati").glob("*.json")) + [RADICE / "verifica_browser.js"] + ([RADICE / "NOTE.md"] if (RADICE / "NOTE.md").exists() else [])
    for f in file:
        t = f.read_text(encoding="utf-8")
        if f.name == "verifica.py":
            t = re.sub(r"vietate = re\.compile\(.*", "", t)
        if f.name in ("fonti.json", "fonti.py"):
            t = t.replace("payrolltax.feedback@treasury.tas.gov.au", "")
        for m in vietate.finditer(t):
            errore(f"{f.name}: parola vietata «{m.group(0)}»")
    print("9. Nessun dato personale, nessun nome di modello AI nei file del sito, nei dati e nel codice.")


# ---------------------------------------------------------------- browser
def browser():
    def euro(x):
        return "$" + f"{math.floor(x + 0.5):,}"
    casi = []
    for pagina, sal, giorni, rv, rq in [("/calculator/", {"nsw": 1500000}, 365, False, False),
                                        ("/calculator/", {"nsw": 2400000, "vic": 1100000, "qld": 900000, "wa": 650000}, 365, True, False),
                                        ("/calculator/", {"sa": 1600000, "tas": 2400000, "nt": 9000000}, 200, False, False),
                                        ("/calculator/", {"qld": 112000000, "vic": 30000000}, 365, False, True),
                                        ("/act/", {"act": 1000000}, 200, False, False),
                                        ("/vic/", {"vic": 4200000, "altro": 800000}, 300, True, False),
                                        ("/vic/", {"vic": 2900000}, 183, False, False),
                                        ("/calculator/", {"act": 1000000, "nsw": 400000}, 200, False, False),
                                        ("/qld/", {"qld": 3000000}, 365, False, True)]:
        res = motore.calcola(G.P, sal, giorni, 365, rv, rq)
        casi.append({"pagina": pagina, "salari": sal, "giorni": giorni, "rv": rv, "rq": rq, "atteso": euro(res["complessivo"]),
                     "non_calcolato": bool(res["non_calcolati"])})
    import os
    env = dict(os.environ, CASI_CALC=json.dumps(casi))
    r = subprocess.run(["node", str(RADICE / "verifica_browser.js")], capture_output=True, text=True, timeout=1500, env=env)
    print(r.stdout.strip())
    if r.returncode:
        errore("browser: " + (r.stderr.strip() or r.stdout.strip())[-2500:])


def main():
    rete = "--rete" in sys.argv
    controlla_fonti(rete)
    controlla_parametri()
    controlla_esempi()
    controlla_js_python()
    controlla_stampati()
    controlla_faq()
    controlla_struttura()
    controlla_monetizzazione()
    controlla_parole()
    if "--browser" in sys.argv:
        browser()
    for a in AVVISI:
        print("   avviso:", a)
    if ERRORI:
        print(f"\n{len(ERRORI)} ERRORI:")
        for e in ERRORI[:80]:
            print(" -", e)
        sys.exit(1)
    print(f"\nTutti i controlli superati ({len(AVVISI)} avvisi).")


if __name__ == "__main__":
    main()
