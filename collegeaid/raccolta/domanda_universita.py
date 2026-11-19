"""Domanda misurata per le schede delle università: sceglie le N università con più ricerche «<nome> tuition» e «<nome> cost».

Uso (dalla radice del repository):
    python3 collegeaid/raccolta/domanda_universita.py frasi <cartella>      # scrive <cartella>/frasi.tsv (id <TAB> frase) dai nomi del file Scorecard
    # le ricerche si fanno con curl, mai da Python; la chiave non va mai scritta né stampata:
    cut -f1,2 <cartella>/frasi.tsv | while IFS=$'\t' read -r id frase; do [ -s "<cartella>/$id.json" ] || \
      curl -s -G "https://api.seodata.dev/v1/keyword" --data-urlencode "q=$frase" --data-urlencode "country=us" \
           -H "Authorization: Bearer $(cat /root/.config/seodata/key)" -o "<cartella>/$id.json"; done
    python3 collegeaid/raccolta/domanda_universita.py riunisci <cartella>   # scrive dati/domanda_universita.json

Candidate: istituti del file con PREDDEG = 3 (in prevalenza lauree di primo livello), aperti, con almeno SOGLIA studenti dei corsi di laurea
(o almeno SOGLIA_SELETTIVE se ammettono meno del 30 %).
Nomi cercati per ogni università (tutti in minuscolo, seguiti da « tuition» e da « cost»):
  1. il nome ufficiale del file (INSTNM), senza «The» iniziale e senza «-Main Campus»; con il campus se c'è («university of california los angeles»);
  2. il nome senza campus, solo se nel file appartiene a una sola università o a una sola sede principale, oppure alla sede che ha
     almeno 10.000 studenti e almeno il doppio di ogni altra sede con lo stesso nome («university of michigan» = Ann Arbor;
     «university of california» non è di nessuna);
  3. il nome senza la parola finale «University», solo se nessun altro istituto del file comincia con le stesse parole e se non è il nome
     di una città o di uno Stato («harvard», «michigan state»; non «boston», «miami», «new york»); se resta una parola sola
     si misura solo con «tuition» («rice cost» può voler dire altro);
  4. gli altri nomi scritti nella colonna ALIAS del file: sigle di 3-6 lettere solo se sono le iniziali del nome e nessun altro istituto
     del file ha la stessa sigla (né tra i suoi alias né come iniziali); nomi di più parole solo se condividono una parola con il nome
     ufficiale e nessun altro istituto comincia con le stesse parole;
  5. «uc <campus>» e «cal state <campus>» per i due sistemi pubblici della California.
Una frase che potrebbe indicare due università del file non viene attribuita a nessuna.
Domanda di un'università = volume della sua frase più cercata, «tuition» o «cost» (non la somma: per molte università lo strumento
dà lo stesso numero alle due frasi, segno che Google Ads le conta insieme). La somma delle due resta nel file come tetto.
È una misura per ordinare, non un numero di visitatori.
"""
import csv
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

DATI = Path(__file__).resolve().parent.parent / "dati"
N_PAGINE = 200
SOGLIA, SOGLIA_SELETTIVE = 2500, 900
PICCOLE = {"of", "at", "and", "the", "in", "for", "a", "an", "on"}
SUFFISSI = ("tuition", "cost")
GENERICHE = {"post"}   # nomi corti che sono parole comuni: «post tuition» non indica Post University
SIGLE_AMBIGUE = {"UNI", "RIC", "SOU", "SVA", "UWA", "ULM"}   # sigle che in una ricerca vogliono dire anche altro («uni» = università in genere; UWA e ULM sono anche atenei esteri)


def norm(s):
    s = s.lower().replace("&", " & ")
    s = re.sub(r"\ba\s*&\s*m\b", "a&m", s)
    s = re.sub(r"[^a-z0-9&' ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def parti(nome):
    """(nome di base, campus o None, «main» se il file dice che è la sede principale)."""
    n = re.sub(r"^The ", "", nome.strip())
    m = re.match(r"^(.*) (Campus|Digital) Immersion$", n)
    if m:
        return m[1], None, False
    m = re.match(r"^(.*\b(?:University|College|Institute)\b[^-]*?)\s*-\s*(.+)$", n)
    if not m:
        return n, None, False
    base, campus = m[1], re.sub(r"\s+Campus$", "", m[2]).strip()
    if campus in ("Main", "Main Campus"):
        return base, None, True
    return base, campus, False


def iniziali(nome):
    return "".join(w[0] for w in re.sub(r"[^A-Za-z ]", " ", nome).split() if w.lower() not in PICCOLE).upper()


def carica():
    with open(DATI / "grezzi" / "scorecard_estratto.csv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def candidata(r):
    if r["PREDDEG"] != "3" or r["CURROPER"] != "1" or not r["UGDS"].isdigit():
        return False
    u = int(r["UGDS"])
    return u >= SOGLIA or (u >= SOGLIA_SELETTIVE and re.fullmatch(r"\d+(\.\d+)?", r["ADM_RATE"]) and float(r["ADM_RATE"]) < 0.30)


def alias_del_file(r):
    """Pezzi della colonna ALIAS: (testo, è una sigla)."""
    if r["ALIAS"] in ("NA", ""):
        return []
    out = []
    for pezzo in re.split(r"[|;,]", r["ALIAS"]):
        pezzo = pezzo.strip()
        if not pezzo:
            continue
        for parola in pezzo.split():
            if re.fullmatch(r"[A-Z]{3,6}", parola):
                out.append((parola, True))
        if " " in pezzo and 4 <= len(pezzo) <= 45 and not re.fullmatch(r"[A-Z ]+", pezzo):
            out.append((pezzo, False))
    return out


def nomi_cercati(righe):
    """{unitid: [(nome in minuscolo, come lo si scrive, regola)]} per le candidate, con le regole di unicità sull'intero file."""
    tutti = [(r, parti(r["INSTNM"])) for r in righe]
    pieni, basi, sigle_altrui, luoghi = {}, {}, {}, set()
    for r, (base, campus, _main) in tutti:
        pieno = norm(f"{base} {campus}" if campus else base)
        pieni.setdefault(pieno, []).append(r["UNITID"])
        basi.setdefault(norm(base), []).append(r)
        luoghi.add(norm(r["CITY"]))
        for s in {iniziali(base), iniziali(f"{base} {campus}" if campus else base)} | {a for a, sig in alias_del_file(r) if sig}:
            sigle_altrui.setdefault(s, set()).add(r["UNITID"])
    luoghi |= {norm(x) for x in STATI_USA}
    nomi_norm = [(norm(re.sub(r"^The ", "", r["INSTNM"])), r["UNITID"]) for r in righe]
    alias_multi = {}
    for r in righe:
        for a, sig in alias_del_file(r):
            if not sig:
                alias_multi.setdefault(norm(a), set()).add(r["UNITID"])
    out = {}
    for r, (base, campus, main) in tutti:
        if not candidata(r):
            continue
        uid, voci = r["UNITID"], []
        parole_nome = {w for w in norm(r["INSTNM"]).split() if len(w) >= 4}
        pieno_scritto = f"{base} {campus}" if campus else base
        pieno = norm(pieno_scritto)
        if pieni[pieno] == [uid]:
            voci.append((pieno, pieno_scritto, "nome"))
        nb = norm(base)
        famiglia = [x for x, (b2, c2, _m) in tutti if (lambda n2: n2 == nb or n2.startswith(nb + " "))(norm(f"{b2} {c2}" if c2 else b2))]
        if campus or len(famiglia) > 1:
            stessi = famiglia
            principali = [x for x in stessi if x["MAIN"] == "1"]
            studenti = sorted((int(x["UGDS"]) if x["UGDS"].isdigit() else 0 for x in stessi if x["UNITID"] != uid), reverse=True)
            if main or len(stessi) == 1 or (len(principali) == 1 and principali[0]["UNITID"] == uid and not campus):
                voci.append((norm(base), base, "nome senza campus"))
            elif campus and studenti and int(r["UGDS"]) >= 2 * studenti[0] and int(r["UGDS"]) >= 10000:
                voci.append((norm(base), base, "nome senza campus: sede con almeno il doppio degli studenti di ogni altra"))
        # nome senza «University» finale
        if not campus and norm(base).endswith(" university"):
            corto = norm(base)[: -len(" university")]
            if (len(corto) >= 4 and corto not in luoghi and corto not in GENERICHE and not corto.startswith("university") and
                    not any(u != uid and (n == corto or n.startswith(corto + " ")) and not (main and n.startswith(norm(base))) for n, u in nomi_norm)
                    and not any(u != uid for u in alias_multi.get(corto, ()))):
                voci.append((corto, re.sub(r"\s+University$", "", base), "nome senza University"))
        for a, sigla in alias_del_file(r):
            if sigla:
                mie = {iniziali(base), iniziali(pieno_scritto), iniziali(base.replace("-", " ")), iniziali(pieno_scritto.replace("-", " "))}
                if a not in SIGLE_AMBIGUE and sigle_altrui.get(a, set()) <= {uid} and any(i == a or (len(a) >= 3 and i.startswith(a)) for i in mie):
                    voci.append((a.lower(), a, "sigla del file"))
            else:
                na = norm(a)
                if (alias_multi[na] == {uid} and pieni.get(na, [uid]) == [uid] and (parole_nome & set(na.split())) and na not in luoghi and len(na.split()) >= 2
                        and not any(u != uid and (n == na or n.startswith(na + " ")) and not (main and n.startswith(norm(base))) for n, u in nomi_norm)):
                    voci.append((na, a, "alias del file"))
        m = re.match(r"^University of California$", base)
        if m and campus:
            voci.append((norm(f"uc {campus}"), f"UC {campus}", "sistema UC"))
        if base == "California State University" and campus:
            voci.append((norm(f"cal state {campus}"), f"Cal State {campus}", "sistema CSU"))
        visti, pulite = set(), []
        for n, scritto, regola in voci:
            if n not in visti:
                visti.add(n)
                pulite.append((n, scritto, regola))
        out[uid] = pulite
    # una stessa frase per due università: non vale per nessuna
    conta = {}
    for uid, voci in out.items():
        for n, _, _ in voci:
            conta.setdefault(n, set()).add(uid)
    return {uid: [v for v in voci if len(conta[v[0]]) == 1] for uid, voci in out.items()}


STATI_USA = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas",
             "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
             "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas",
             "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming", "America", "American", "National", "Northern", "Southern", "Eastern", "Western", "Central",
             "Northeastern", "Northwestern", "Southeastern", "Southwestern", "Pacific", "Atlantic", "International", "Christian", "Catholic", "State", "Union", "Trinity", "Columbia", "Concordia"]


def suffissi_di(nome, regola):
    """Un nome corto di una parola sola («rice», «pace», «bentley») si misura solo con «tuition»: con «cost» può voler dire altro."""
    return ("tuition",) if regola == "nome senza University" and " " not in nome else SUFFISSI


def id_frase(frase):
    return hashlib.sha1(frase.encode("utf-8")).hexdigest()[:16]


def frasi(cartella):
    nomi = nomi_cercati(carica())
    righe = []
    for uid, voci in sorted(nomi.items()):
        for n, _, regola in voci:
            for s in suffissi_di(n, regola):
                righe.append(f"{id_frase(f'{n} {s}')}\t{n} {s}\t{uid}")
    cartella.mkdir(parents=True, exist_ok=True)
    (cartella / "frasi.tsv").write_text("\n".join(righe) + "\n", encoding="utf-8")
    print(f"{len(nomi)} università candidate, {len(righe)} frasi in {cartella / 'frasi.tsv'}")


def numero(v):
    return re.fullmatch(r"-?\d+(\.\d+)?", v) is not None


def riunisci(cartella):
    righe = carica()
    per_id = {r["UNITID"]: r for r in righe}
    nomi = nomi_cercati(righe)
    scuole, misurate, mancanti = [], 0, []
    for uid, voci in nomi.items():
        r = per_id[uid]
        mis = {s: [] for s in SUFFISSI}
        for n, scritto, regola in voci:
            for s in suffissi_di(n, regola):
                frase = f"{n} {s}"
                f = cartella / f"{id_frase(frase)}.json"
                if not f.exists():
                    mancanti.append(frase)
                    continue
                d = json.loads(f.read_text(encoding="utf-8"))
                if d.get("keyword", "").lower() != frase:
                    raise SystemExit(f"{f.name}: risposta per «{d.get('keyword')}» invece di «{frase}»")
                misurate += 1
                mis[s].append({"frase": frase, "nome": n, "scritto": scritto, "regola": regola, "volume_mese": d.get("volume") or 0, "cpc_usd": d.get("cpc") or 0})
        meglio = {s: max(mis[s], key=lambda x: x["volume_mese"], default=None) for s in SUFFISSI}
        domanda = max((m["volume_mese"] for m in meglio.values() if m), default=0)
        somma = sum(m["volume_mese"] for m in meglio.values() if m)
        scuole.append({"unitid": uid, "nome": r["INSTNM"], "stato": r["STABBR"], "studenti": int(r["UGDS"]), "domanda_mese": domanda, "somma_tuition_cost": somma,
                       "tuition": meglio["tuition"], "cost": meglio["cost"], "frasi": [{k: x[k] for k in ("frase", "regola", "volume_mese", "cpc_usd")} for s in SUFFISSI for x in mis[s]]})
    if mancanti:
        raise SystemExit(f"{len(mancanti)} frasi senza risposta (per esempio «{mancanti[0]}»): rilanciare il giro di curl")
    scuole.sort(key=lambda x: (-x["domanda_mese"], -x["somma_tuition_cost"], -x["studenti"], x["nome"]))
    scelte, escluse = [], []
    for s in scuole:
        r = per_id[s["unitid"]]
        prezzo = r["NPT4_PUB"] if r["CONTROL"] == "1" else r["NPT4_PRIV"]
        if len(scelte) < N_PAGINE and s["domanda_mese"] > 0:
            if not (numero(r["TUITIONFEE_IN"]) and numero(prezzo)):
                escluse.append({"unitid": s["unitid"], "nome": s["nome"], "domanda_mese": s["domanda_mese"], "motivo": "nel file mancano le tasse o il prezzo netto medio: la scheda non avrebbe il conto"})
                continue
            titolo = s["tuition"] if s["tuition"] and s["tuition"]["volume_mese"] >= (s["cost"]["volume_mese"] if s["cost"] else 0) else s["cost"]
            scelte.append(dict(s, posto=len(scelte) + 1, frase_titolo=titolo["frase"], frase_titolo_scritta=f'{titolo["scritto"]} {titolo["frase"].rsplit(" ", 1)[1].capitalize()}', volume_titolo=titolo["volume_mese"]))
    if len(scelte) < N_PAGINE:
        raise SystemExit(f"solo {len(scelte)} università con domanda misurata sopra zero")
    dentro = {s["unitid"] for s in scelte}
    altre = [{"unitid": s["unitid"], "nome": s["nome"], "stato": s["stato"], "studenti": s["studenti"], "domanda_mese": s["domanda_mese"],
              "frasi": [[x["frase"], x["volume_mese"]] for x in s["frasi"]]} for s in scuole if s["unitid"] not in dentro]
    testo = json.dumps({
        "_nota": f"Volumi medi mensili Google Ads (USA) letti con seodata.dev per {len(scuole)} università candidate del file College Scorecard ({misurate} frasi «<nome> tuition» e «<nome> cost»). "
                 "domanda_mese = volume della frase più cercata di quella università (non la somma: per molte università lo strumento dà lo stesso numero a «tuition» e a «cost», "
                 "segno che Google Ads le conta insieme); somma_tuition_cost = frase «tuition» più cercata + frase «cost» più cercata, solo come tetto. "
                 "Le frasi che potrebbero indicare due università non sono attribuite. "
                 f"scelte = le prime {N_PAGINE} per domanda_mese con tasse e prezzo netto nel file; altre = le candidate rimaste fuori, con le loro misure.",
        "letto_il": date.today().isoformat(), "paese": "us", "candidate": len(scuole), "frasi_misurate": misurate,
        "domanda_totale_scelte": sum(s["domanda_mese"] for s in scelte), "somma_tuition_cost_scelte": sum(s["somma_tuition_cost"] for s in scelte),
        "domanda_totale_candidate": sum(s["domanda_mese"] for s in scuole),
        "soglia_ultima_scelta": scelte[-1]["domanda_mese"], "scelte": scelte, "escluse_senza_dati": escluse, "altre": altre}, ensure_ascii=False, indent=1) + "\n"
    if ("sd_" + "live") in testo:
        raise SystemExit("chiave nel testo: non scrivo")
    (DATI / "domanda_universita.json").write_text(testo, encoding="utf-8")
    print(f"{len(scuole)} candidate, {misurate} frasi misurate; scelte {len(scelte)} (domanda {sum(s['domanda_mese'] for s in scelte):,} al mese sulla frase migliore, {sum(s['somma_tuition_cost'] for s in scelte):,} sommando tuition e cost; ultima {scelte[-1]['domanda_mese']:,}); "
          f"escluse per dati mancanti: {len(escluse)}")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("frasi", "riunisci"):
        raise SystemExit(__doc__)
    (frasi if sys.argv[1] == "frasi" else riunisci)(Path(sys.argv[2]))
