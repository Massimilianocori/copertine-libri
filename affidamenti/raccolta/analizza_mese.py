"""Soglie 2, 3 e 5: conta CIG, importi, aggiudicatari ed enti nei file mensili ANAC.

Legge in streaming (senza estrarre gli zip) i file "aggiornamenti delta" della
BDNCP scaricati con scarica.py:
  - CIG:            .../dataset/cig/filesystem/AAAAMMGG-cig_json.zip
  - aggiudicatari:  .../dataset/aggiudicatari/filesystem/AAAAMMGG-aggiudicatari_json.zip
  - aggiudicazioni: .../dataset/aggiudicazioni/filesystem/AAAAMMGG-aggiudicazioni_json.zip
  - anagrafica:     .../dataset/stazioni-appaltanti/filesystem/stazioni-appaltanti_json.zip
Ogni file è JSON a righe (una riga per record, righe vuote ignorate). Un CIG può
comparire più volte (più CPV, o aggiornato in un delta successivo): vale l'ultima
occorrenza nell'ordine dei file passati (passare i file dal più vecchio al più nuovo).

Per ciascun mese di pubblicazione richiesto (--mesi 2026-09 ...) calcola:
  - CIG distinti; quota con importo del lotto < 40.000 e < 5.000 euro;
  - quota con aggiudicatario presente (nei file aggiudicatari caricati) e con
    aggiudicazione (importo e data), totale e sotto 40.000 euro;
  - stazioni appaltanti distinte (codice fiscale) e Comuni distinti
    (denominazione "COMUNE DI ..." o "COMUNE ..." nell'anagrafica ANAC);
  - quota di aggiudicatari con codice fiscale di 16 caratteri (persone fisiche /
    ditte individuali: dato personale, da NON pubblicare in pagine dedicate);
  - ritardo tra data di aggiudicazione definitiva e data di pubblicazione del file.
Scrive anche un indice compatto TSV (--indice) di tutti i CIG letti, per il
controllo di verità con cerca_cig.py, e un piccolo campione casuale (--campione)
di affidamenti di Comuni con aggiudicatario impresa (niente persone fisiche).

Uso:
    python3 -I analizza_mese.py --cig F1.zip [F2.zip ...] --aggiudicatari A1.zip [...] \
        --aggiudicazioni G1.zip [...] --stazioni S.zip --mesi 2026-09 2026-08 \
        --uscita riassunto.json [--indice indice.tsv] [--campione campione.json]
Tempo (secondi_totali) e memoria massima (memoria_max_MB, da resource) sono nel riassunto.
"""
import argparse
import collections
import datetime as dt
import json
import random
import re
import resource
import time
import zipfile

RE_COMUNE = re.compile(r"^(COMUNE|CITTA'?|CITTÀ|MUNICIPIO)( DI| DELLA| DEL| DEGLI| D')?\b")
RE_NON_COMUNE = re.compile(r"UNIONE|CONSORZIO|MONTANA|AZIENDA|ISTITUZIONE|FONDAZIONE|SOCIETA|S\.P\.A|S\.R\.L")


def righe(path):
    """Restituisce i record JSON di uno zip ANAC (primo file interno), uno alla volta."""
    z = zipfile.ZipFile(path)
    with z.open(z.infolist()[0]) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except ValueError:
                    continue


def data_file(path):
    m = re.search(r"(20\d{6})-", path)
    return dt.date(int(m.group(1)[:4]), int(m.group(1)[4:6]), int(m.group(1)[6:8])) if m else None


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cig", nargs="+", required=True)
    ap.add_argument("--aggiudicatari", nargs="*", default=[])
    ap.add_argument("--aggiudicazioni", nargs="*", default=[])
    ap.add_argument("--stazioni", required=True)
    ap.add_argument("--mesi", nargs="+", required=True)
    ap.add_argument("--uscita", required=True)
    ap.add_argument("--indice")
    ap.add_argument("--campione")
    a = ap.parse_args()
    t0 = time.time()

    # anagrafica stazioni appaltanti
    staz = {}
    for r in righe(a.stazioni):
        den = (r.get("denominazione") or "").upper().strip()
        staz[r.get("codice_fiscale")] = {
            "den": den, "istat": r.get("citta_codice"),
            "comune": bool(RE_COMUNE.match(den)) and not RE_NON_COMUNE.search(den)}

    # CIG (l'ultima occorrenza vince; per i CPV multipli teniamo il prevalente)
    cig = {}
    righe_cig = 0
    file_di = {}
    for p in a.cig:
        df = data_file(p)
        for r in righe(p):
            righe_cig += 1
            c = r.get("cig")
            if not c:
                continue
            if c in cig and r.get("flag_prevalente") == 0 and file_di.get(c) == df:
                continue
            file_di.setdefault(c, df)  # primo file in cui compare
            cig[c] = (
                r.get("data_pubblicazione") or "", num(r.get("importo_lotto")),
                r.get("cf_amministrazione_appaltante") or "",
                (r.get("denominazione_amministrazione_appaltante") or "").strip(),
                (r.get("tipo_scelta_contraente") or "").strip(),
                (r.get("oggetto_lotto") or r.get("oggetto_gara") or "").replace("\t", " ").replace("\n", " ")[:300],
                r.get("stato") or "", r.get("oggetto_principale_contratto") or "",
                r.get("luogo_istat") or "")
    t_cig = time.time() - t0

    # aggiudicatari e aggiudicazioni
    agg = collections.defaultdict(list)
    for p in a.aggiudicatari:
        for r in righe(p):
            c = r.get("cig")
            if c:
                agg[c].append((r.get("codice_fiscale") or "", (r.get("denominazione") or "").strip(),
                               r.get("tipo_soggetto") or "", r.get("ruolo") or ""))
    aggz = {}
    for p in a.aggiudicazioni:
        df = data_file(p)
        for r in righe(p):
            c = r.get("cig")
            if c:
                aggz[c] = (r.get("data_aggiudicazione_definitiva") or "", num(r.get("importo_aggiudicazione")),
                           r.get("esito") or "", df.isoformat() if df else "")

    out = {"file_cig": a.cig, "file_aggiudicatari": a.aggiudicatari, "file_aggiudicazioni": a.aggiudicazioni,
           "righe_cig_lette": righe_cig, "cig_distinti_letti": len(cig),
           "aggiudicatari_cig_distinti": len(agg), "aggiudicazioni_cig_distinti": len(aggz),
           "stazioni_in_anagrafica": len(staz),
           "comuni_in_anagrafica_attivi": sum(1 for s in staz.values() if s["comune"]),
           "mesi": {}}
    # distribuzione per mese di pubblicazione (prime 15 voci)
    per_mese = collections.Counter(v[0][:7] for v in cig.values())
    out["cig_per_mese_pubblicazione_top"] = dict(per_mese.most_common(15))

    for m in a.mesi:
        sel = {c: v for c, v in cig.items() if v[0][:7] == m}
        n = len(sel)
        sotto40 = {c for c, v in sel.items() if v[1] is not None and v[1] < 40000}
        sotto5 = {c for c, v in sel.items() if v[1] is not None and v[1] < 5000}
        imp_null = sum(1 for v in sel.values() if v[1] is None)
        cancellati = sum(1 for v in sel.values() if v[6] and v[6] != "ATTIVO")
        con_agg = {c for c in sel if c in agg}
        con_aggz = {c for c in sel if c in aggz}
        enti = {v[2] for v in sel.values()}
        comuni = {v[2] for v in sel.values() if (staz.get(v[2]) or {}).get("comune")
                  or (v[2] not in staz and RE_COMUNE.match(v[3].upper()) and not RE_NON_COMUNE.search(v[3].upper()))}
        comuni_sotto40_agg = {sel[c][2] for c in sotto40 & con_agg if sel[c][2] in comuni}
        cf_agg = [x[0] for c in con_agg for x in agg[c]]
        pf = sum(1 for x in cf_agg if len(x) == 16 and not x.isdigit())
        tipi = collections.Counter(v[4] for v in sel.values())
        tipi40 = collections.Counter(sel[c][4] for c in sotto40)
        oggetti = collections.Counter(v[7] for v in sel.values())
        rit = sorted((dt.date.fromisoformat(aggz[c][3]) - dt.date.fromisoformat(aggz[c][0])).days
                     for c in con_aggz if aggz[c][0][:4].isdigit() and aggz[c][3])
        rit_pub = sorted((file_di[c] - dt.date.fromisoformat(sel[c][0])).days
                         for c in sel if file_di.get(c) and sel[c][0][:4].isdigit())

        def q(x, d):
            return round(100 * x / d, 1) if d else None

        def perc(lst, p):
            return lst[int(len(lst) * p)] if lst else None
        out["mesi"][m] = {
            "cig_distinti": n,
            "importo_assente": imp_null,
            "stato_non_attivo": cancellati,
            "sotto_40k": len(sotto40), "sotto_40k_%": q(len(sotto40), n),
            "sotto_5k": len(sotto5), "sotto_5k_%": q(len(sotto5), n),
            "con_aggiudicatario": len(con_agg), "con_aggiudicatario_%": q(len(con_agg), n),
            "sotto_40k_con_aggiudicatario": len(sotto40 & con_agg),
            "sotto_40k_con_aggiudicatario_%": q(len(sotto40 & con_agg), len(sotto40)),
            "sopra_40k_con_aggiudicatario_%": q(len(con_agg - sotto40), n - len(sotto40)),
            "con_aggiudicazione": len(con_aggz), "con_aggiudicazione_%": q(len(con_aggz), n),
            "stazioni_appaltanti_distinte": len(enti),
            "comuni_distinti": len(comuni),
            "comuni_distinti_con_affidamento_sotto40k_e_aggiudicatario": len(comuni_sotto40_agg),
            "cig_di_comuni": sum(1 for v in sel.values() if v[2] in comuni),
            "aggiudicatari_righe": len(cf_agg),
            "aggiudicatari_persone_fisiche_cf16": pf, "aggiudicatari_persone_fisiche_%": q(pf, len(cf_agg)),
            "tipo_scelta_top": dict(tipi.most_common(8)),
            "tipo_scelta_sotto_40k_top": dict(tipi40.most_common(5)),
            "oggetto_principale": dict(oggetti.most_common(5)),
            "giorni_da_aggiudicazione_a_file_mediana": perc(rit, 0.5),
            "giorni_da_aggiudicazione_a_file_p90": perc(rit, 0.9),
            "giorni_da_pubblicazione_cig_a_file_mediana": perc(rit_pub, 0.5),
        }
    out["secondi_lettura_cig"] = round(t_cig, 1)
    out["secondi_totali"] = round(time.time() - t0, 1)
    out["memoria_max_MB"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)

    if a.indice:
        with open(a.indice, "w", encoding="utf-8") as f:
            f.write("cig\tdata_pubblicazione\timporto_lotto\tcf_ente\tente\ttipo_scelta\toggetto\tstato\t"
                    "primo_file\taggiudicatari\tdata_aggiudicazione\timporto_aggiudicazione\tfile_aggiudicazione\n")
            for c, v in cig.items():
                ag = " | ".join(f"{x[1]} ({x[0]})" for x in agg.get(c, []))
                z = aggz.get(c, ("", None, "", ""))
                f.write("\t".join([c, v[0], "" if v[1] is None else str(v[1]), v[2], v[3], v[4], v[5], v[6],
                                   str(file_di.get(c) or ""), ag, z[0], "" if z[1] is None else str(z[1]), z[3]]) + "\n")
    if a.campione:
        m0 = a.mesi[0]
        pool = sorted(c for c, v in cig.items() if v[0][:7] == m0 and c in agg
                      and (staz.get(v[2]) or {}).get("comune")
                      and all(len(x[0]) == 11 and x[2] != "PERSONA FISICA" for x in agg[c]))
        rnd = random.Random(20261010)
        camp = []
        for c in rnd.sample(pool, min(40, len(pool))):
            v = cig[c]
            camp.append({"cig": c, "data_pubblicazione": v[0], "importo_lotto": v[1], "ente": v[3],
                         "tipo_scelta": v[4], "oggetto": v[5],
                         "aggiudicatari": [{"denominazione": x[1], "codice_fiscale": x[0]} for x in agg[c]],
                         "aggiudicazione": aggz.get(c),
                         "fonte": "https://dati.anticorruzione.it/opendata/dataset/cig (delta) + aggiudicatari"})
        with open(a.campione, "w", encoding="utf-8") as f:
            json.dump(camp, f, ensure_ascii=False, indent=1)
    with open(a.uscita, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
