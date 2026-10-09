"""Raccoglie le sedi d'esame dei 4 enti e prepara esameb1/dati/sedi.json.

Uso (dalla radice del repository):
    python3 esameb1/raccolta/raccogli.py

Cosa fa:
1. scarica le fonti ufficiali (pagine regionali CILS, PDF centri CELI e CERT.IT, API PLIDA);
2. ne estrae le sedi in Italia, con fonte e data di verifica;
3. assegna a ogni sede provincia e regione usando l'elenco ISTAT dei comuni;
4. salva un'impronta di ogni pagina-calendario in dati/impronte.json: se una pagina cambia,
   lo segnala, perché le date in sessioni.json vanno ricontrollate a mano.

Le date d'esame NON si estraggono in automatico (i formati cambiano ogni anno): stanno in
dati/sessioni.json, curate a mano con fonte e data di verifica.
"""
import csv
import hashlib
import html
import io
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cils_sedi import CORREZIONI as CORREZIONI_CILS, Tabelle, pulisci_comune  # noqa: E402

RADICE = Path(__file__).resolve().parents[1]
DATI = RADICE / "dati"
OGGI = date.today().isoformat()
UA = {"User-Agent": "Mozilla/5.0 (compatible; esameb1-raccolta)"}

FONTI = {
    "cils_italia": "https://cils.unistrasi.it/1/84/68/Italia.htm",
    "celi_centri": "https://cvcl.unistrapg.it/MC-API/Risorse/StreamRisorsa.ashx?guid=322fe666-af88-4d67-a8bf-5300d7724134",
    "celi_centri_pagina": "https://cvcl.unistrapg.it/pagine/centri-desame-convenzionati-celi-000",
    "plida_api": "https://api.dante.global/danteheadquarter/list-not-secured",
    "plida_pagina": "https://www.dante.global/it/contatti/lista-contatti",
    "certit_centri": "https://certificazioneitaliano.uniroma3.it/wp-content/uploads/sites/30/file_locked/2025/09/Centri-convenzionati-italiani_202509.pdf",
    "istat_comuni": "https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv",
}

# Pagine-calendario da sorvegliare: se l'impronta cambia, sessioni.json va ricontrollato.
CALENDARI = {
    "CILS 2026": "https://cils.unistrasi.it/1/211/415/Le_date_degli_esami_2026.htm",
    "CILS 2027": "https://cils.unistrasi.it/1/213/428/Le_date_degli_esami_2027.htm",
    "CELI 2026-2027": "https://cvcl.unistrapg.it/pagine/calendario-esami-celi-e-dils-pg-000",
    "PLIDA esami": "https://plida.dante.global/it/esami-plida/",
    "CERT.IT home": "https://certificazioneitaliano.uniroma3.it/",
}

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")

REGIONI = {"abruzzo", "basilicata", "calabria", "campania", "emilia romagna", "friuli venezia giulia", "lazio",
           "liguria", "lombardia", "marche", "molise", "piemonte", "puglia", "sardegna", "sicilia", "toscana",
           "trentino alto adige", "umbria", "valle d'aosta", "veneto"}

# Nomi scritti nelle fonti -> comune ISTAT (frazioni, abbreviazioni, refusi). Verificati a mano il 9/10/2026.
ALIAS_COMUNI = {
    "Reggio Emilia": "Reggio nell'Emilia", "Reggio Calabria": "Reggio di Calabria",
    "Castel Lagopesole": "Avigliano", "Arcavacata di Rende": "Rende", "Catona": "Reggio di Calabria",
    "San.Benedetto del Tronto": "San Benedetto del Tronto", "Torrette": "Ancona",
    "Ceglie Mesasapica": "Ceglie Messapica", "Oriolo Frazione Voghera": "Voghera",
    "Biadene di Montebelluna": "Montebelluna", "Verona-Legnago": "Legnago", "Conegliano Veneto": "Conegliano",
    "Mestre": "Venezia", "S.Bonifacio": "San Bonifacio", "Ponte S.Giovanni": "Perugia", "Massa Carrara": "Massa",
    "Castelnuovo Garfagnana": "Castelnuovo di Garfagnana", "Marina di Carrara": "Carrara",
    "Montecatini Terme": "Montecatini-Terme", "Rosignano Solvay": "Rosignano Marittimo",
    "S.Croce sull'Arno": "Santa Croce sull'Arno", "Caltagirone Catania": "Caltagirone", "Bari-Bat": "Bari",
    "Bra- Fraz. Pollenzo": "Bra", "Corigliano Rossano": "Corigliano-Rossano", "Alatri Frosinone": "Alatri",
    "Cinisello": "Cinisello Balsamo", "Cepegatti - Pescara": "Cepagatti", "Ripalimolisani": "Ripalimosani",
    "Ugento- Lecce": "Ugento", "Magliano Fr. Di Carmiano": "Carmiano", "Mongrotto Terme": "Montegrotto Terme",
    "Ponte nelle Apli": "Ponte nelle Alpi",
}

# Sedi con il comune mancante nella fonte (ricavato dall'indirizzo pubblicato nella stessa fonte).
COMUNE_PER_NOME = {
    "Centro Linguistico di Ateneo dell'Università degli Studi Federico II": "Napoli",
    "Accademia Lingua Italiana Assisi": "Assisi",
}


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


def testo_pdf(dati_pdf):
    import pdfplumber
    with pdfplumber.open(io.BytesIO(dati_pdf)) as pdf:
        return [riga for pagina in pdf.pages for tab in pagina.extract_tables() for riga in tab]


def norm(s):
    return re.sub(r"\s+", " ", (s or "").replace("﻿", "").replace("​", "")).strip()


def chiave_comune(s):
    s = norm(s).lower()
    s = re.sub(r"\(.*?\)", "", s)
    s = s.replace("’", "'").replace("`", "'")
    for a, b in (("à", "a"), ("è", "e"), ("é", "e"), ("ì", "i"), ("ò", "o"), ("ù", "u")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z' ]", "", s).strip()


# ---------- ISTAT ----------
def carica_comuni():
    grezzo = scarica(FONTI["istat_comuni"]).decode("latin-1")
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


def localizza(sede, comuni):
    """Completa comune, provincia, sigla e regione dal nome del comune (ISTAT)."""
    if not sede["citta"] and sede["nome"] in COMUNE_PER_NOME:
        sede["citta"] = COMUNE_PER_NOME[sede["nome"]]
    candidati = [sede["citta"]]
    # "Corigliano Rossano", "Reggio Calabria", "Bergamo (Ponte San Pietro)"
    m = re.match(r"^(.*?)\s*\((.*?)\)$", sede["citta"])
    if m:
        candidati = [m.group(2), m.group(1)]
    alias = {chiave_comune(k): v for k, v in ALIAS_COMUNI.items()}
    for c in candidati:
        info = comuni.get(chiave_comune(alias.get(chiave_comune(c), c)))
        if info:
            sede.update({"citta": info["comune"], "provincia": info["provincia"],
                         "sigla": info["sigla"], "regione": info["regione"]})
            return True
    return False


# ---------- CILS ----------
def sedi_cils():
    pagina = scarica(FONTI["cils_italia"]).decode("utf-8", "ignore")
    regioni = sorted(set(re.findall(r"https://cils\.unistrasi\.it/1/179/\d+/[^\"']+\.htm", pagina)))
    if not regioni:
        raise RuntimeError("CILS: nessuna pagina regionale trovata")
    sedi = []
    for url in regioni:
        parser = Tabelle()
        parser.feed(scarica(url).decode("utf-8", "ignore"))
        time.sleep(0.4)
        for r in parser.righe:
            if len(r) < 4 or r[0].lower().startswith("ente"):
                continue
            citta, prov = pulisci_comune(r[3])
            telefono = r[4] if len(r) > 4 else ""
            mail = EMAIL.findall(" ".join(r[4:]))
            sede = {
                "ente": "CILS", "nome": norm(r[0]), "indirizzo": norm(r[1]),
                "cap": re.sub(r"\D", "", r[2])[:5], "citta": citta, "provincia_fonte": prov,
                "telefono": norm(EMAIL.sub("", telefono)), "email": mail[0] if mail else "", "fonte": url,
            }
            if len(sede["cap"]) != 5:
                sede["cap"] = ""
            if re.search(r"\d", sede["citta"]):
                sede["telefono"] = sede["telefono"] or sede["citta"]
                sede["citta"] = ""
            for chiave, correzione in CORREZIONI_CILS.items():
                if sede["nome"].startswith(chiave):
                    sede["citta"] = correzione["citta"]
            if sede["nome"] and sede["citta"]:
                sedi.append(sede)
    return sedi


# ---------- CELI ----------
def sedi_celi():
    righe = testo_pdf(scarica(FONTI["celi_centri"]))
    sedi = []
    for r in righe:
        if not r or not r[0] or not re.match(r"^\d+$", norm(r[0])):
            continue
        codice, nome, stato, regione, citta, indirizzo, email = (norm(x) for x in (r + [""] * 7)[:7])
        if stato.lower() != "italia":
            continue
        if chiave_comune(citta) in REGIONI:  # colonne Regione/Città invertite nella fonte
            regione, citta = citta, regione
        sedi.append({
            "ente": "CELI", "nome": nome, "indirizzo": indirizzo, "cap": "", "citta": citta,
            "regione_fonte": regione, "telefono": "", "email": email.replace(" ", ""),
            "codice_centro": codice, "fonte": FONTI["celi_centri_pagina"],
        })
    return sedi


# ---------- PLIDA ----------
def sedi_plida():
    dati = json.loads(scarica(FONTI["plida_api"]))
    sedi = []
    for x in dati:
        if norm(x.get("country")).lower() != "italia" or not x.get("plida"):
            continue
        if (x.get("entityStatus") or "Published") != "Published":
            continue
        sedi.append({
            "ente": "PLIDA", "nome": norm(x.get("name")), "indirizzo": norm(x.get("address")),
            "cap": re.sub(r"\D", "", str(x.get("cap") or ""))[:5], "citta": norm(x.get("city")),
            "telefono": norm(x.get("phoneNumberPlida") or x.get("phoneNumber")),
            "email": (EMAIL.findall(x.get("emailPlida") or x.get("email") or "") or [""])[0],
            "sito": norm(x.get("webSite")), "fonte": FONTI["plida_pagina"],
        })
    return sedi


# ---------- CERT.IT ----------
# Righe che l'estrattore di tabelle non legge (cella unita nel PDF); copiate a mano dalla stessa fonte.
SUPPLEMENTI_CERTIT = [{
    "ente": "CERT.IT", "nome": "Fondazione Bonifacio VIII", "indirizzo": "Piazza Dante, 5", "cap": "03012",
    "citta": "Anagni", "regione_fonte": "Lazio", "telefono": "077 5739057",
    "email": "segreteria@istitutobonifacioottavo.edu.it",
}]


def sedi_certit():
    pdf = scarica(FONTI["certit_centri"])
    righe = testo_pdf(pdf)
    sedi, regione = [], ""
    for r in righe:
        r = [norm(x) for x in r]
        if not r or not r[0] or r[0].upper() == "CENTRO":
            continue
        if all(not x for x in r[1:]):
            regione = r[0].title()
            continue
        indirizzo = r[1]
        m = re.search(r"(\d{5})\s*([^()\d]+?)?\s*(?:\((\w{2})\))?$", indirizzo)
        cap, citta = (m.group(1), norm(m.group(2) or "")) if m else ("", "")
        via = norm(indirizzo[: m.start()]) if m else indirizzo
        sedi.append({
            "ente": "CERT.IT", "nome": r[0], "indirizzo": via, "cap": cap, "citta": citta,
            "regione_fonte": regione, "telefono": r[3] if len(r) > 3 else "",
            "email": (EMAIL.findall(r[2] if len(r) > 2 else "") or [""])[0], "fonte": FONTI["certit_centri"],
        })
    # controllo: ogni email del PDF deve appartenere a una sede letta
    import pdfplumber
    with pdfplumber.open(io.BytesIO(pdf)) as doc:
        email_pdf = {e.lower() for p in doc.pages for e in EMAIL.findall(p.extract_text() or "")}
    lette = " ".join(" ".join(s.values()) for s in sedi).lower()
    for extra in SUPPLEMENTI_CERTIT:
        if extra["email"].lower() not in lette:
            sedi.append(dict(extra, fonte=FONTI["certit_centri"]))
            lette += " " + extra["email"].lower()
    mancanti = [e for e in email_pdf if e not in lette and not any(e.split("@")[1] in x for x in lette.split())]
    if mancanti:
        print("ATTENZIONE CERT.IT: email nel PDF senza sede letta:", ", ".join(sorted(mancanti)))
    return sedi


# ---------- impronte dei calendari ----------
def controlla_calendari():
    file_impronte = DATI / "impronte.json"
    vecchie = json.loads(file_impronte.read_text()) if file_impronte.exists() else {}
    nuove, cambiate = {}, []
    for nome, url in CALENDARI.items():
        try:
            corpo = scarica(url).decode("utf-8", "ignore")
        except RuntimeError as e:
            print("ATTENZIONE", e)
            nuove[nome] = vecchie.get(nome, {})
            continue
        corpo = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", corpo, flags=re.S)
        testo = norm(html.unescape(re.sub(r"<[^>]+>", " ", corpo)))
        impronta = hashlib.sha256(testo.encode()).hexdigest()[:16]
        nuove[nome] = {"url": url, "impronta": impronta, "controllato_il": OGGI}
        if nome in vecchie and vecchie[nome].get("impronta") != impronta:
            cambiate.append(nome)
    file_impronte.write_text(json.dumps(nuove, ensure_ascii=False, indent=1))
    return cambiate


def main():
    DATI.mkdir(exist_ok=True)
    comuni = carica_comuni()
    tutte, non_localizzate = [], []
    for raccogli in (sedi_cils, sedi_celi, sedi_plida, sedi_certit):
        sedi = raccogli()
        print(f"{raccogli.__name__}: {len(sedi)} sedi")
        if not sedi:
            raise RuntimeError(f"{raccogli.__name__}: zero sedi, fonte cambiata?")
        for s in sedi:
            s["verificato_il"] = OGGI
            if not localizza(s, comuni):
                s.setdefault("provincia", s.pop("provincia_fonte", ""))
                s.setdefault("regione", s.pop("regione_fonte", ""))
                s.setdefault("sigla", "")
                non_localizzate.append(f'{s["ente"]}: {s["nome"]} — "{s["citta"]}"')
            s.pop("provincia_fonte", None)
            s.pop("regione_fonte", None)
        tutte.extend(sedi)
    tutte.sort(key=lambda s: (s["regione"], s["provincia"], s["citta"], s["ente"], s["nome"]))
    (DATI / "sedi.json").write_text(json.dumps(tutte, ensure_ascii=False, indent=1))
    print(f"Totale: {len(tutte)} sedi salvate in dati/sedi.json")
    if non_localizzate:
        print(f"{len(non_localizzate)} sedi senza comune ISTAT riconosciuto (restano con i dati della fonte):")
        for n in non_localizzate:
            print("  -", n)
    cambiate = controlla_calendari()
    if cambiate:
        print("CALENDARI CAMBIATI, ricontrollare sessioni.json:", ", ".join(cambiate))
    else:
        print("Calendari: nessun cambiamento rispetto all'ultimo controllo.")


if __name__ == "__main__":
    main()
