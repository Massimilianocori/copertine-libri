"""Raccoglie le sedi degli esami di Stato 2026 e prepara esamidistato/dati/sedi.json.

Uso (dalla radice del repository):
    python3 esamidistato/raccolta/raccogli.py

Cosa fa:
1. scarica le 3 ordinanze MUR 2026 (OM 692, 693, 694 del 27/5/2026) e ne legge con pdfplumber
   la "Tabella elenco delle sedi" (una lista di sedi per ogni professione);
2. legge dal decreto del Ministero della Giustizia del 3/9/2026 le sedi (Corti di appello)
   dell'esame di avvocato 2026;
3. assegna a ogni sede comune, provincia e regione con l'elenco ISTAT dei comuni;
4. salva il testo delle ordinanze in dati/fonti/ e un'impronta delle pagine ufficiali in
   dati/impronte.json: se una pagina cambia (per esempio escono le ordinanze 2027) lo segnala.

Le date e le scadenze NON si estraggono in automatico: stanno in dati/sessioni.json, curate a
mano con fonte e data di verifica.
"""
import csv
import hashlib
import html
import io
import json
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
DATI = RADICE / "dati"
OGGI = date.today().isoformat()
UA = {"User-Agent": "Mozilla/5.0 (compatible; esamidistato-raccolta)"}

MUR_PAGINA = "https://www.mur.gov.it/it/aree-tematiche/universita/professioni/esami-di-stato"
ORDINANZE = {
    "OM 694/2026": "https://www.mur.gov.it/sites/default/files/2026-05/Ordinanza%20Ministeriale%20n.%20694%20del%2027-05-2026.pdf",
    "OM 693/2026": "https://www.mur.gov.it/sites/default/files/2026-05/Ordinanza%20Ministeriale%20n.%20693%20del%2027-05-2026.pdf",
    "OM 692/2026": "https://www.mur.gov.it/sites/default/files/2026-05/Ordinanza%20Ministeriale%20n.%20692%20del%2027-05-2026.pdf",
}
AVVOCATO_DECRETO = "https://www.giustizia.it/giustizia/page/it/provvedimento_ministeriale_selezionato?contentId=SDC1519988"
ISTAT = "https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv"

# Pagine da sorvegliare: se l'impronta cambia, sessioni.json va ricontrollato a mano.
SORVEGLIATE = {
    "MUR esami di Stato": MUR_PAGINA,
    "Giustizia avvocato 2026": "https://www.giustizia.it/giustizia/it/mg_1_6_1.page?contentId=SCE1520061",
    "USR Veneto ordinanze MIM 2026": "https://istruzioneveneto.gov.it/20260513_41372/",
}

# Intestazioni delle tabelle MUR -> professione (slug di professioni.json).
INTESTAZIONI = [
    ("ATTUARIO", "attuario"), ("CHIMICO", "chimico"), ("INGEGNERE", "ingegnere"), ("ARCHITETTO", "architetto"),
    ("BIOLOGO", "biologo"), ("GEOLOGO", "geologo"), ("PSICOLOGO", "psicologo"), ("DOTTORE AGRONOMO", "agronomo"),
    ("ASSISTENTE SOCIALE", "assistente-sociale"), ("ODONTOIATRA", "odontoiatra"), ("FARMACISTA", "farmacista"),
    ("VETERINARIO", "veterinario"), ("FISICO", "fisico"), ("TECNOLOGO ALIMENTARE", "tecnologo-alimentare"),
]
# L'OM 692 ha una sola tabella, senza intestazione.
SENZA_INTESTAZIONE = {"OM 692/2026": "commercialista"}

# Nomi scritti nelle ordinanze -> comune ISTAT.
ALIAS_COMUNI = {"Reggio Calabria": "Reggio di Calabria"}

# Siti degli atenei: home verificata a mano il 9/10/2026 (HTTP 200). La pagina "esami di Stato"
# si cerca in automatico nella home (link che contiene "esami di stato" / "esame di stato").
SITI_ATENEO = {}  # riempito da siti_atenei.json se presente
FILE_SITI = Path(__file__).resolve().parent / "siti_atenei.json"

RIGHE_DA_SALTARE = re.compile(r"^(Il Ministro dell.università e della ricerca|\d+|TABELLA ELENCO.*|PROFESSIONALE CHE SI SVOLGERANNO.*)$")
RIGA_SEDE = re.compile(r"^([A-ZÀÈÉÌÒÙ’' ]+?(?:\s*\([A-Z]{2}\))?)\s+[–-]\s+(.+)$")
INIZIO_ATENEO = re.compile(r"^(Università|Universita|Libera Università|Politecnico|Scuola|Istituto)")


def scarica(url, tentativi=3):
    for i in range(tentativi):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:  # rete instabile: riprova
            if i == tentativi - 1:
                raise RuntimeError(f"download fallito: {url}: {e}")
            time.sleep(2 * (i + 1))


def norm(s):
    return re.sub(r"\s+", " ", (s or "").replace("﻿", "").replace("​", "")).strip()


def chiave(s):
    """Chiave di confronto: minuscole, senza accenti, virgolette e trattini."""
    s = norm(s).lower().replace("’", "'").replace("`", "'")
    for a, b in (("à", "a"), ("è", "e"), ("é", "e"), ("ì", "i"), ("ò", "o"), ("ù", "u")):
        s = s.replace(a, b)
    s = re.sub(r"[“”\"«»]", "", s).replace("-", " ")
    return re.sub(r"\s+", " ", s).strip()


def chiave_comune(s):
    s = chiave(re.sub(r"\(.*?\)", "", s))
    return re.sub(r"[^a-z' ]", "", s).strip()


def titolo_citta(s):
    s = norm(re.sub(r"\(.*?\)", "", s)).lower()
    return re.sub(r"(^|[\s'’])(\w)", lambda m: m.group(1) + m.group(2).upper(), s)


# ---------- ISTAT ----------
def carica_comuni():
    grezzo = scarica(ISTAT).decode("latin-1")
    lettore = csv.reader(io.StringIO(grezzo), delimiter=";")
    intestazione = next(lettore)
    idx_nome = intestazione.index("Denominazione in italiano")
    idx_reg = intestazione.index("Denominazione Regione")
    idx_prov = [i for i, h in enumerate(intestazione) if h.startswith("Denominazione dell'Unit")][0]
    idx_sigla = intestazione.index("Sigla automobilistica")
    comuni = {}
    for r in lettore:
        if len(r) <= idx_sigla:
            continue
        comuni[chiave_comune(r[idx_nome])] = {
            "comune": r[idx_nome], "provincia": r[idx_prov], "sigla": r[idx_sigla], "regione": r[idx_reg],
        }
    return comuni


def localizza(citta, comuni):
    alias = {chiave_comune(k): v for k, v in ALIAS_COMUNI.items()}
    k = chiave_comune(citta)
    return comuni.get(chiave_comune(alias.get(k, citta)))


# ---------- ordinanze MUR ----------
def testo_pdf(dati_pdf):
    import pdfplumber
    with pdfplumber.open(io.BytesIO(dati_pdf)) as pdf:
        return "\n".join((p.extract_text() or "") for p in pdf.pages)


def leggi_tabella(testo, nome_om):
    """Restituisce una lista di righe {professione, citta, ateneo_testo} dalla tabella delle sedi."""
    inizio = testo.find("TABELLA ELENCO DELLE SEDI")
    if inizio < 0:
        raise RuntimeError(f"{nome_om}: tabella delle sedi non trovata")
    righe, professione, intestazione, citta = [], SENZA_INTESTAZIONE.get(nome_om), [], None
    for riga in testo[inizio:].splitlines():
        riga = norm(riga)
        if not riga or RIGHE_DA_SALTARE.match(riga):
            continue
        # una sede spezzata su più righe (parentesi aperta)
        if righe and righe[-1]["ateneo_testo"].count("(") > righe[-1]["ateneo_testo"].count(")"):
            righe[-1]["ateneo_testo"] += " " + riga
            continue
        m = RIGA_SEDE.match(riga)
        if m and not intestazione:
            if not professione:
                raise RuntimeError(f"{nome_om}: sede senza professione: {riga}")
            citta = norm(m.group(1))
            righe.append({"professione": professione, "citta": citta, "ateneo_testo": norm(m.group(2))})
            continue
        if INIZIO_ATENEO.match(riga) and citta and not intestazione:
            righe.append({"professione": professione, "citta": citta, "ateneo_testo": riga})
            continue
        # intestazione di professione (può stare su più righe e finisce con ":")
        intestazione.append(riga)
        if riga.endswith(":"):
            testo_int = " ".join(intestazione).upper()
            trovata = [slug for parola, slug in INTESTAZIONI if testo_int.startswith(parola)]
            if not trovata:
                raise RuntimeError(f"{nome_om}: intestazione sconosciuta: {testo_int}")
            professione, intestazione, citta = trovata[0], [], None
    if intestazione:
        raise RuntimeError(f"{nome_om}: righe non riconosciute: {intestazione}")
    return righe


def separa_note(ateneo_testo):
    """'Università X (settore ...)' -> ('Università X', 'settore ...')."""
    m = re.match(r"^(.*?)\s*\((.*)\)\s*$", ateneo_testo)
    if m and not m.group(1).endswith("del"):
        return norm(m.group(1)), norm(m.group(2))
    return ateneo_testo, ""


def sedi_mur():
    righe = []
    for nome_om, url in ORDINANZE.items():
        testo = testo_pdf(scarica(url))
        (DATI / "fonti" / (nome_om.replace(" ", "").replace("/", "-").lower() + ".txt")).write_text(
            f"Fonte: {url}\nScaricato il {OGGI}\n\n{testo}")
        for r in leggi_tabella(testo, nome_om):
            r["ordinanza"], r["fonte"] = nome_om, url
            righe.append(r)
        time.sleep(0.5)
    return righe


# ---------- avvocato ----------
def sedi_avvocato():
    pagina = scarica(AVVOCATO_DECRETO).decode("utf-8", "ignore")
    pagina = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", pagina, flags=re.S)
    testo = norm(html.unescape(re.sub(r"<[^>]+>", " ", pagina)))
    m = re.search(r"presso le sedi delle Corti di appello di (.+?) e presso la Sezione distaccata di (\w+) "
                  r"della Corte di appello di (\w+)", testo)
    if not m:
        raise RuntimeError("avvocato: elenco delle Corti di appello non trovato nel decreto")
    righe = [{"professione": "avvocato", "citta": norm(c), "ateneo_testo": f"Corte di appello di {norm(c)}"}
             for c in m.group(1).split(",")]
    righe.append({"professione": "avvocato", "citta": m.group(2),
                  "ateneo_testo": f"Corte di appello di {m.group(3)} – Sezione distaccata di {m.group(2)}"})
    for r in righe:
        r["ordinanza"], r["fonte"] = "DM Giustizia 3/9/2026", AVVOCATO_DECRETO
    return righe


# ---------- unione per sede ----------
def raggruppa(righe, comuni):
    sedi, nomi_visti = {}, {}
    for r in righe:
        ateneo, nota = separa_note(r["ateneo_testo"])
        # forma del nome più frequente nelle ordinanze
        nomi_visti.setdefault(chiave(ateneo), []).append(ateneo)
        info = localizza(r["citta"], comuni)
        if not info:
            raise RuntimeError(f"comune non trovato in ISTAT: {r['citta']}")
        k = (info["comune"], chiave(ateneo))
        s = sedi.setdefault(k, {
            "tipo": "corte_appello" if r["professione"] == "avvocato" else "ateneo",
            "ateneo": ateneo, "citta": info["comune"], "provincia": info["provincia"], "sigla": info["sigla"],
            "regione": info["regione"], "professioni": [], "note": {}, "fonti": [],
        })
        if r["professione"] not in s["professioni"]:
            s["professioni"].append(r["professione"])
        if nota:
            s["note"][r["professione"]] = f"Nell'ordinanza: «{nota}»"
        if r["fonte"] not in s["fonti"]:
            s["fonti"].append(r["fonte"])
    for s in sedi.values():
        forme = nomi_visti[chiave(s["ateneo"])]
        s["ateneo"] = max(set(forme), key=lambda f: (forme.count(f), "“" in f))
    return list(sedi.values())


def aggiungi_siti(sedi):
    siti = json.loads(FILE_SITI.read_text()) if FILE_SITI.exists() else {}
    senza = set()
    for s in sedi:
        info = siti.get(chiave(s["ateneo"]))
        if info:
            s.update({k: v for k, v in info.items() if v})
        elif s["tipo"] == "ateneo":
            senza.add(s["ateneo"])
    if senza:
        print(f"{len(senza)} atenei senza sito in siti_atenei.json:", "; ".join(sorted(senza)))


# ---------- impronte ----------
def controlla_pagine():
    file_impronte = DATI / "impronte.json"
    vecchie = json.loads(file_impronte.read_text()) if file_impronte.exists() else {}
    nuove, cambiate = {}, []
    for nome, url in SORVEGLIATE.items():
        try:
            corpo = scarica(url).decode("utf-8", "ignore")
        except RuntimeError as e:
            print("ATTENZIONE", e)
            nuove[nome] = vecchie.get(nome, {})
            continue
        corpo = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", corpo, flags=re.S)
        testo = norm(html.unescape(re.sub(r"<[^>]+>", " ", corpo)))
        if nome == "MUR esami di Stato":  # solo l'elenco delle ordinanze, non menu e notizie
            i = testo.find("Ordinanza Ministeriale")
            testo = testo[i:i + 3000] if i >= 0 else testo
            if "2027" in testo[:400]:
                print("ATTENZIONE: sulla pagina MUR compare il 2027: ordinanze nuove?")
        impronta = hashlib.sha256(testo.encode()).hexdigest()[:16]
        nuove[nome] = {"url": url, "impronta": impronta, "controllato_il": OGGI}
        if nome in vecchie and vecchie[nome].get("impronta") != impronta:
            cambiate.append(nome)
    file_impronte.write_text(json.dumps(nuove, ensure_ascii=False, indent=1))
    return cambiate


def main():
    (DATI / "fonti").mkdir(parents=True, exist_ok=True)
    comuni = carica_comuni()
    righe = sedi_mur() + sedi_avvocato()
    conteggio = {}
    for r in righe:
        conteggio[r["professione"]] = conteggio.get(r["professione"], 0) + 1
    print("Sedi per professione:", ", ".join(f"{k} {v}" for k, v in conteggio.items()))
    sedi = raggruppa(righe, comuni)
    aggiungi_siti(sedi)
    for s in sedi:
        s["verificato_il"] = OGGI
    sedi.sort(key=lambda s: (s["regione"], s["citta"], s["tipo"], s["ateneo"]))
    (DATI / "sedi.json").write_text(json.dumps(sedi, ensure_ascii=False, indent=1))
    print(f"Totale: {len(sedi)} sedi ({sum(s['tipo'] == 'ateneo' for s in sedi)} atenei, "
          f"{sum(s['tipo'] == 'corte_appello' for s in sedi)} Corti di appello) in dati/sedi.json")
    cambiate = controlla_pagine()
    if cambiate:
        print("PAGINE UFFICIALI CAMBIATE, ricontrollare sessioni.json:", ", ".join(cambiate))
    else:
        print("Pagine ufficiali: nessun cambiamento rispetto all'ultimo controllo.")


if __name__ == "__main__":
    main()
