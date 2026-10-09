"""Estrae le sedi CILS in Italia dalle pagine regionali di cils.unistrasi.it.

Uso: python3 cils_sedi.py <cartella con le pagine regionali .html> <file regioni.txt> > sedi_cils.json
Ogni pagina regionale contiene una tabella: Ente | Indirizzo | CAP | Comune e Provincia | Telefono | Mail.
"""
import html, json, re, sys
from html.parser import HTMLParser
from pathlib import Path


class Tabelle(HTMLParser):
    def __init__(self):
        super().__init__()
        self.righe, self.riga, self.cella, self.in_cella = [], None, [], False

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.riga = []
        elif tag in ("td", "th") and self.riga is not None:
            self.in_cella, self.cella = True, []
        elif tag == "br" and self.in_cella:
            self.cella.append(" ")

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.riga is not None and self.in_cella:
            testo = re.sub(r"\s+", " ", html.unescape("".join(self.cella))).replace("​", "").strip()
            self.riga.append(testo)
            self.in_cella = False
        elif tag == "tr" and self.riga is not None:
            if any(self.riga):
                self.righe.append(self.riga)
            self.riga = None

    def handle_data(self, data):
        if self.in_cella:
            self.cella.append(data)


EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


def pulisci_comune(testo):
    """'Albano Sant'Alessandro (Bergamo)' -> ('Albano Sant'Alessandro', 'Bergamo')."""
    m = re.match(r"^(.*?)\s*\(([^)]*)\)\s*$", testo)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return testo.strip(), ""


# Righe della fonte con colonne spostate o incomplete (verificate a mano il 9/10/2026).
CORREZIONI = {
    "Scuola Italia Aquila": {"citta": "L'Aquila", "provincia": "L'Aquila"},
    "Vida Società Cooperativa Sociale-Onlus": {"citta": "Rionero in Vulture", "provincia": "Potenza"},
    "ENAIP Borgomanero": {"citta": "Borgomanero", "provincia": "Novara"},
    "ENAIP Novara": {"citta": "Novara", "provincia": "Novara"},
    "Enaip Grugliasco": {"citta": "Grugliasco", "provincia": "Torino"},
}


def main():
    cartella, elenco = Path(sys.argv[1]), Path(sys.argv[2]).read_text().split()
    url_per_nome = {Path(u).stem: u for u in elenco}
    sedi = []
    for pagina in sorted(cartella.glob("*.html")):
        regione_nome = pagina.stem.replace("_", " ").replace("-", " ")
        parser = Tabelle()
        parser.feed(pagina.read_text(encoding="utf-8", errors="ignore"))
        for r in parser.righe:
            if len(r) < 4 or r[0].lower().startswith("ente"):
                continue
            ente, indirizzo, cap, comune = r[0], r[1], r[2], r[3]
            telefono = r[4] if len(r) > 4 else ""
            resto = " ".join(r[4:])
            mail = EMAIL.findall(resto)
            citta, prov = pulisci_comune(comune)
            if not ente or not citta:
                continue
            sede = {
                "ente": "CILS",
                "nome": ente,
                "indirizzo": indirizzo,
                "cap": re.sub(r"\D", "", cap)[:5],
                "citta": citta,
                "provincia": prov,
                "regione": regione_nome,
                "telefono": EMAIL.sub("", telefono).strip(),
                "email": mail[0] if mail else "",
                "fonte": url_per_nome.get(pagina.stem, ""),
            }
            if len(sede["cap"]) != 5:
                sede["cap"] = ""
            if re.search(r"\d", sede["citta"]) and not sede["telefono"]:
                sede["telefono"] = sede["citta"]
            for chiave, correzione in CORREZIONI.items():
                if sede["nome"].startswith(chiave):
                    sede.update(correzione)
            sedi.append(sede)
    json.dump(sedi, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
