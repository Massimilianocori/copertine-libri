"""Unisce i risultati delle singole fonti in un unico elenco di avvisi (bandiposteggi/dati/avvisi-test.json).

Ingressi (file JSON prodotti dagli altri script, nella cartella di lavoro dei download):
  piemonte.json (bur_piemonte.py), lazio.json (bur_lazio.py), puglia2.json (bur_puglia.py),
  toscana2.json (bur_toscana.py), altri.json (bur_altri.py), comuni2.json (comuni_web.py)
più due voci lette a mano dai BUR con motore di ricerca (Lombardia, Veneto) descritte in EXTRA.

Revisione manuale: bandiposteggi/dati/revisione-manuale.json, con
  "escludi": {chiave: motivo}            candidati automatici scartati (falsi positivi, doppioni, anno sbagliato)
  "correggi": {chiave: {campo: valore}}  solo campi anagrafici (comune, provincia, regione, tipo)
  "verifica": {chiave: {...}}            controllo a campione: valori riletti sul documento
I campi "posteggi_auto" e "scadenza_auto" NON vengono mai corretti: restano quelli dell'estrazione
automatica, perché il test misura proprio quanto rende l'automatismo.

Uso:
  python3 -I consolida.py <cartella_lavoro> <revisione-manuale.json> <avvisi-test.json>
"""
import json
import os
import re
import sys
import time

PROV_TOSCANA = {"Arezzo": "AR", "Firenze": "FI", "Grosseto": "GR", "Livorno": "LI", "Lucca": "LU", "Massa Carrara": "MS",
                "Pisa": "PI", "Pistoia": "PT", "Prato": "PO", "Siena": "SI"}
RX_NOME = re.compile(r"(Responsabile\s*:|Dirigente\s*:|Sig\.(?:ra)?|Dott\.(?:ssa)?)\s*[A-ZÀ-Ü][a-zà-ü']+\s+[A-ZÀ-Ü][a-zà-ü']+")
EXTRA = [
    {"chiave": "burl-458090158", "comune": "Borgosatollo", "provincia": "BS", "regione": "Lombardia",
     "oggetto": "Bando per l'assegnazione di n. 2 posteggi vacanti nel mercato settimanale - Settore non alimentare",
     "data_pubblicazione": "2026-04-01", "url": "https://www.consultazioniburl.servizirl.it/ConsultazioneBurl/api/download?id=458090158",
     "fonte": "BUR", "fonte_nome": "BURL Lombardia, Serie Avvisi e Concorsi n. 14 del 01/04/2026, p. 357",
     "trovato_con": "API di ricerca BURL (bur_altri.py), parola 'posteggi'", "file_testo": "lombardia/borgosatollo.txt"},
    {"chiave": "burv-580357", "comune": "Nervesa della Battaglia", "provincia": "TV", "regione": "Veneto",
     "oggetto": "Avviso di avvio delle procedure di selezione per l'assegnazione delle concessioni pluriennali dei posteggi liberi "
                "nel mercato settimanale del venerdì pomeriggio di Bavaria centro",
     "data_pubblicazione": "2026-04-24", "url": "https://bur.regione.veneto.it/BurvServices/pubblica/DettaglioAvviso.aspx?id=580357",
     "fonte": "BUR", "fonte_nome": "BUR Veneto n. 51 del 24/04/2026 (preavviso: il bando è solo all'albo comunale)",
     "trovato_con": "ricerca BURVET per oggetto (bur_altri.py), parola 'posteggi'", "file_testo": "altri/veneto-580357.txt"},
]


def carica(cartella, nome):
    p = os.path.join(cartella, nome)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def candidati(cartella):
    """Converte ogni fonte nello stesso formato. Restituisce (lista, data_verifica per fonte)."""
    out = []
    d = carica(cartella, "piemonte.json")
    for c in d["candidati"]:
        out.append({"chiave": c["pagina"], "comune": c["comune"], "provincia": c["provincia"], "regione": "Piemonte",
                    "oggetto": c["oggetto"], "data_pubblicazione": c["data_bu"], "url": c["pdf"] or c["pagina"],
                    "fonte": "BUR", "fonte_nome": f"BUR Piemonte n. {c['numero_bu']}/2026, sezione {c['sezione']}",
                    "trovato_con": "indici settimanali BUR Piemonte (bur_piemonte.py)", "verificato_il": d["verificato_il"],
                    "tipo_auto": c["tipo_auto"], "posteggi_auto": c["posteggi_auto"], "scadenza_auto": c["scadenza_auto"]})
    d = carica(cartella, "lazio.json")
    for i, c in enumerate(d["avvisi"]):
        m = re.search(r"COMUNE DI ([A-Z' ]+)", c["ente"])
        out.append({"chiave": f"{c['pagina']}#{i}", "comune": m.group(1).title() if m else ("Roma" if "ROMA" in c["ente"] else None),
                    "provincia": None, "regione": "Lazio", "oggetto": c["oggetto"], "data_pubblicazione": c["data_bu"],
                    "url": c["pagina"], "fonte": "BUR", "fonte_nome": f"BUR Lazio n. {c['numero_bu']}/2026 (sintesi URP)",
                    "trovato_con": "sintesi URP del BUR Lazio (bur_lazio.py)", "verificato_il": d["verificato_il"],
                    "tipo_auto": c["tipo_auto"], "posteggi_auto": c["posteggi_auto"], "scadenza_auto": c["scadenza_auto"]})
    d = carica(cartella, "puglia2.json")
    for c in d["candidati"]:
        com = c["comune"] or (re.sub(r"^COMUNE DI\s*", "", c["ente"]).title() if c["ente"].startswith("COMUNE") else None)
        out.append({"chiave": f"{c['pdf']}#{com}", "comune": com, "provincia": None, "regione": "Puglia",
                    "oggetto": c["oggetto"], "data_pubblicazione": c["data_bu"], "url": c["pdf"], "fonte": "BUR",
                    "fonte_nome": f"BURP Puglia n. {c['numero_bu']}/2026" + (" (raccolta regionale dei bandi comunali)" if c.get("da_raccolta_regionale") else ""),
                    "trovato_con": "dettaglio dei numeri BURP (bur_puglia.py)", "verificato_il": d["verificato_il"],
                    "tipo_auto": c.get("tipo_auto"), "posteggi_auto": c.get("posteggi_auto"), "scadenza_auto": c.get("scadenza_auto")})
    d = carica(cartella, "toscana2.json")
    for c in d["avvisi"]:
        out.append({"chiave": f"{c['pdf']}#p{c['pagina_bu']}", "comune": c["comune"],
                    "provincia": PROV_TOSCANA.get(c["provincia_nome"] or "", None), "regione": "Toscana",
                    "oggetto": c["oggetto"], "data_pubblicazione": c["data_bu"], "url": c["pdf"], "fonte": "BUR",
                    "fonte_nome": f"BURT Toscana Parte III n. {c['parte_iii']}/2026, p. {c['pagina_bu']}",
                    "trovato_con": "sommario della Parte III del BURT (bur_toscana.py)", "verificato_il": d["verificato_il"],
                    "tipo_auto": c["tipo_auto"], "posteggi_auto": c["posteggi_auto"], "scadenza_auto": c["scadenza_auto"]})
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import comune as C
    for e in EXTRA:
        t = open(os.path.join(cartella, e["file_testo"]), encoding="utf-8").read()
        x = {k: v for k, v in e.items() if k != "file_testo"}
        x.update({"verificato_il": "2026-10-09", "tipo_auto": C.estrai_tipo(t), "posteggi_auto": C.estrai_numero(t),
                  "scadenza_auto": C.estrai_scadenza(t) or C.scadenza_da_relativa(t, e["data_pubblicazione"])})
        out.append(x)
    d = carica(cartella, "comuni2.json")
    for c in d["avvisi"]:
        out.append({"chiave": c["url"], "comune": c["comune"], "provincia": c["provincia"], "regione": c["regione"],
                    "oggetto": re.sub(r"\s+", " ", c["testo_inizio"][:220]).strip(), "data_pubblicazione": c["pubblicazione_auto"],
                    "url": c["url"], "fonte": "Comune", "fonte_nome": "sito del Comune" + (" (Municipium)" if "municipiumapp" in c["url"] else ""),
                    "trovato_con": c["trovato_con"] + " -> comuni_web.py", "verificato_il": d["verificato_il"],
                    "http": c["http"], "formato": c["formato"],
                    "tipo_auto": c["tipo_auto"], "posteggi_auto": c["posteggi_auto"], "scadenza_auto": c["scadenza_auto"]})
    return out


def main():
    cartella, rev_path, uscita = sys.argv[1], sys.argv[2], sys.argv[3]
    rev = json.load(open(rev_path, encoding="utf-8"))
    tutti = candidati(cartella)
    tenuti, scartati = [], []
    for c in tutti:
        k = c["chiave"]
        if k in rev["escludi"]:
            scartati.append({"chiave": k, "comune": c["comune"], "regione": c["regione"], "fonte": c["fonte"], "motivo": rev["escludi"][k]})
            continue
        c.update(rev["correggi"].get(k, {}))
        c["tipo"] = c.pop("tipo_rivisto", None) or c["tipo_auto"]
        if k in rev["verifica"]:
            c["verifica_a_campione"] = rev["verifica"][k]
        tenuti.append(c)
    for i, c in enumerate(tenuti, 1):
        c["id"] = i
        # nessun nome di persona nell'oggetto (ad es. "Responsabile: Cognome Nome" nelle intestazioni)
        c["oggetto"] = RX_NOME.sub(r"\1 [nome omesso]", c["oggetto"] or "")
    per_regione, per_fonte = {}, {}
    for c in tenuti:
        per_regione[c["regione"]] = per_regione.get(c["regione"], 0) + 1
        per_fonte[c["fonte"]] = per_fonte.get(c["fonte"], 0) + 1
    camp = [c["verifica_a_campione"] for c in tenuti if "verifica_a_campione" in c]
    esito = {
        "campione": len(camp),
        "scadenza_corretta": sum(1 for v in camp if v["scadenza_ok"]),
        "posteggi_corretto": sum(1 for v in camp if v["posteggi_ok"]),
        "entrambi_corretti": sum(1 for v in camp if v["scadenza_ok"] and v["posteggi_ok"]),
    }
    with open(uscita, "w", encoding="utf-8") as f:
        json.dump({
            "descrizione": "Avvisi 2026 di assegnazione posteggi (mercati, fiere, sagre, isolati, chioschi, edicole, spunta) "
                           "raccolti nel test tecnico BandiPosteggi. posteggi_auto e scadenza_auto sono l'estrazione automatica "
                           "senza correzioni; verifica_a_campione riporta i valori riletti a mano sul documento.",
            "generato_il": time.strftime("%Y-%m-%d"),
            "campi": {"tipo": "tipo_auto corretto a mano solo dove indicato in revisione-manuale.json",
                      "data_pubblicazione": "data del BUR, oppure data indicata nella pagina comunale (può mancare)",
                      "fonte": "BUR = trovato nel Bollettino regionale; Comune = sito comunale trovato con ricerca web"},
            "conteggi": {"avvisi": len(tenuti), "regioni": len(per_regione), "per_regione": per_regione, "per_fonte": per_fonte,
                         "candidati_automatici": len(tutti), "scartati": len(scartati)},
            "controllo_a_campione": esito,
            "avvisi": tenuti, "scartati": scartati}, f, ensure_ascii=False, indent=1)
    print(json.dumps({"avvisi": len(tenuti), "regioni": per_regione, "fonti": per_fonte, "scartati": len(scartati), "campione": esito}, ensure_ascii=False))


if __name__ == "__main__":
    main()
