"""Rilegge le fonti ufficiali della sezione "Schengen visa from the UK / from Dubai" (residenti nel Regno Unito e negli Emirati,
non cittadini) e scrive visaincome/dati/schengen_residenti.json (dal 31/10/2026).

Uso (dalla radice del repository):
    python3 visaincome/raccolta/schengen_residenti.py              # rilegge le fonti, controlla i frammenti, scrive il JSON
    python3 visaincome/raccolta/schengen_residenti.py --domanda    # rifà anche l'autocompletamento di Google (gl=gb e gl=ae)

Cosa contiene il JSON (le cifre sui visti, invece, vengono da dati/rifiuti.json, cioè dal file della Commissione già in casa):
- tassa del visto (90 € adulti, 45 € bambini 6-12 anni) e regola del consolato competente per residenza: pagina della Commissione
  "Applying for a Schengen visa";
- assicurazione medica di viaggio, copertura minima 30.000 € (art. 15, par. 3 del Codice dei visti, Reg. (CE) 810/2009, testo consolidato):
  EUR-Lex risponde 202 senza contenuto al nostro server, quindi si legge lo stesso testo dal Publications Office (CELLAR, l'archivio
  ufficiale da cui EUR-Lex prende i documenti); nelle pagine si linka EUR-Lex. Anche l'art. 6 (consolato del luogo di residenza)
  e l'art. 21, par. 5 (mezzi di sussistenza valutati sugli importi di riferimento degli Stati);
- importi di riferimento per i mezzi di sussistenza fissati da ogni Stato (art. 6, par. 4 del Codice frontiere Schengen),
  tabella della Commissione "Reference amounts" (PDF dell'8/6/2026): per ogni Stato il frammento letto A MANO e gli importi;
- ancoraggio del dirham al dollaro (3,6725 AED per 1 USD): tabelle mensili della Banca centrale degli Emirati (CBUAE),
  "Exchange Rates against UAE Dirham" di agosto e settembre 2026 (PDF): ogni riga "US Dollar" deve valere 3.6725;
- fornitori dei servizi visti (VFS Global, TLScontact, BLS International) SOLO dove l'abbiamo letto sulla pagina ufficiale
  dell'ambasciata o del consolato (FORNITORI): per gli altri Stati le pagine dicono di controllare il sito dell'ambasciata.
A ogni lancio lo script riscarica le fonti e controlla che ogni frammento sia ancora nel testo (spazi normalizzati): se un frammento
manca, il JSON NON viene scritto (esce con codice 1) finché qualcuno non rilegge la fonte e aggiorna LETTURE/RIFERIMENTO/FORNITORI.
Fonti non raggiungibili dal server il 31/10/2026 (quindi nessun fornitore scritto per quegli Stati): france-visas.gouv.fr (403),
exteriores.gob.es (401), eda.admin.ch (403), norway.no (403), um.dk (520), finlandabroad.fi (403), mfa.gr (403), centralbank.ae (pagine HTML, 403).
"""
import hashlib
import html as H
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
USCITA = RADICE / "dati" / "schengen_residenti.json"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"}

# ---------------------------------------------------------------- fonti (url = quello che si scarica; pubblico = quello che si linka)
FONTI = {
    "commissione": {"titolo": "European Commission, Applying for a Schengen visa", "formato": "html",
                    "url": "https://home-affairs.ec.europa.eu/policies/schengen/visa-policy/applying-schengen-visa_en"},
    "codice": {"titolo": "Regulation (EC) No 810/2009 (Visa Code), consolidated text of 2 February 2020", "formato": "html",
               "url": "https://publications.europa.eu/resource/cellar/82b7a82d-473e-11ea-b81b-01aa75ed71a1.0006.03/DOC_4",
               "accetta": "application/xhtml+xml",
               "pubblico": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02009R0810-20200202"},
    "riferimento": {"titolo": "European Commission, Reference amounts required for the crossing of the external border fixed by national authorities",
                    "formato": "pdf", "url": "https://home-affairs.ec.europa.eu/document/download/9bf9a98f-3bd1-4e14-9b39-c9087a08a32f_en?filename=Reference_amounts_table.pdf",
                    "pagina": "https://home-affairs.ec.europa.eu/policies/schengen/border-crossing_en"},
    "cbuae_ago": {"titolo": "Central Bank of the UAE, Exchange Rates against UAE Dirham, August 2026", "formato": "pdf",
                  "url": "https://centralbank.ae/media/jqkdbidg/fx_aug26_en.pdf"},
    "cbuae_set": {"titolo": "Central Bank of the UAE, Exchange Rates against UAE Dirham, September 2026", "formato": "pdf",
                  "url": "https://centralbank.ae/media/s1hdr5ms/fx_sep26_en.pdf"},
    # pagine ufficiali di ambasciate e consolati (fornitori dei servizi visti)
    "nl_uk": {"titolo": "NetherlandsWorldwide, Applying for a Schengen visa for the Netherlands in the United Kingdom", "formato": "html",
              "url": "https://www.netherlandsworldwide.nl/visa-the-netherlands/schengen-visa/apply-united-kingdom"},
    "nl_ae": {"titolo": "NetherlandsWorldwide, Applying for a Schengen visa for the Netherlands in the United Arab Emirates", "formato": "html",
              "url": "https://www.netherlandsworldwide.nl/visa-the-netherlands/schengen-visa/apply-united-arab-emirates"},
    "de_uk": {"titolo": "German Missions in the United Kingdom, Where can I apply for my visa?", "formato": "html",
              "url": "https://uk.diplo.de/uk-en/-/2448180"},
    "de_ae": {"titolo": "German Missions in the United Arab Emirates, Schengen visa", "formato": "html",
              "url": "https://uae.diplo.de/ae-en/service/05-VisaEinreise/-/1358934"},
    "it_uk": {"titolo": "Consulate General of Italy in London, Visas", "formato": "html",
              "url": "https://conslondra.esteri.it/en/servizi-consolari-e-visti/servizi-per-il-cittadino-straniero/visti/"},
    "it_ad": {"titolo": "Embassy of Italy in Abu Dhabi, Visas", "formato": "html",
              "url": "https://ambabudhabi.esteri.it/en/servizi-consolari-e-visti/servizi-per-il-cittadino-straniero/visti/"},
    "be_uk": {"titolo": "Embassy of Belgium in the United Kingdom, Visa for Belgium", "formato": "html",
              "url": "https://unitedkingdom.diplomatie.belgium.be/en/travel-belgium/visa-belgium"},
    "pt_uk": {"titolo": "Consulate General of Portugal in London", "formato": "html",
              "url": "https://londres.consuladoportugal.mne.gov.pt/en/"},
}

# ---------------------------------------------------------------- valori letti a mano (31/10/2026) con il frammento della fonte
LETTURE = {
    "tassa_adulti": {"valore": 90, "fonte": "commissione", "frammento": "€90 for adults"},
    "tassa_bambini": {"valore": 45, "fonte": "commissione", "frammento": "€45 for children aged 6-12"},
    "centri": {"fonte": "commissione", "frammento": "An additional fee may apply if you go through visa service centres, which collect applications on behalf of consulates in some cases."},
    "tempi": {"valore": [15, 45], "fonte": "commissione", "frammento": "The normal processing time for a visa application is 15 days. This period may be extended to up to 45 days"},
    "residenza": {"fonte": "commissione", "frammento": "you must apply for a Schengen visa at the consulate with territorial responsibility for the country where you are legally resident"},
    "assicurazione": {"fonte": "commissione", "frammento": "Medical insurance covering emergency medical care, hospitalisation and repatriation (including in the event of death)."},
    "copertura": {"valore": 30000, "fonte": "codice", "frammento": "The minimum coverage shall be EUR 30 000."},
    "assicurazione_residenza": {"fonte": "codice", "frammento": "Applicants shall, in principle, take out insurance in their country of residence."},
    "assicurazione_mev": {"fonte": "codice", "frammento": "shall prove that they are in possession of adequate and valid travel medical insurance covering the period of their first intended visit"},
    "art6": {"fonte": "codice", "frammento": "An application shall be examined and decided on by the consulate of the competent Member State in whose jurisdiction the applicant legally resides."},
    "art6_2": {"fonte": "codice", "frammento": "shall examine and decide on an application lodged by a third-country national legally present but not residing in its jurisdiction, if the applicant has provided justification for lodging the application at that consulate"},
    "art21_5": {"fonte": "codice", "frammento": "on the basis of the reference amounts set by the Member States in accordance with Article 34(1)(c) of the Schengen Borders Code. Proof of sponsorship and/or private accommodation may also constitute evidence of sufficient means of subsistence."},
    "riferimento_data": {"valore": "2026-06-08", "fonte": "riferimento", "frammento": "08/06/2026 REFERENCE AMOUNTS REQUIRED FOR THE CROSSING OF THE EXTERNAL BORDER FIXED BY NATIONAL AUTHORITIES"},
    "ancoraggio": {"valore": 3.6725, "fonte": "cbuae_set", "frammento": "30-Sep-2026 US Dollar 3.6725"},
}

# Importi di riferimento per Stato (tabella della Commissione, PDF dell'8/6/2026, testo letto con pdftotext -raw).
# frammento = parole della tabella; importi = [importo, valuta, a cosa si riferisce] (solo quelli scritti nel frammento).
RIFERIMENTO = {
    "Austria": {"frammento": "Austria* on a case-by-case basis", "importi": []},
    "Belgium": {"frammento": "Belgium* EUR 45 - aliens staying with a private individual EUR 95 - aliens staying at a hotel",
                "importi": [[45, "EUR", "a day if you stay with a private person"], [95, "EUR", "a day if you stay in a hotel"]]},
    "Bulgaria": {"frammento": "Bulgaria* EUR 50 EUR 500 - per stay", "importi": [[50, "EUR", "a day"], [500, "EUR", "per stay"]]},
    "Croatia": {"frammento": "Croatia EUR 70 EUR 30 – third-country national possessing a certified letter of guarantee by a natural or legal person from the Republic of Croatia, proof of a tourist booking or a similar document",
                "importi": [[70, "EUR", "a day"], [30, "EUR", "a day with a certified letter of guarantee, a tourist booking or a similar document"]]},
    "Czech Republic": {"frammento": "Czech Republic* • For stays not exceeding 30 days – 1.565 CZK per day",
                       "importi": [[1565, "CZK", "a day for stays of up to 30 days (longer stays: a fixed sum plus a monthly amount)"]]},
    "Denmark": {"frammento": "Denmark* DKK 350", "importi": [[350, "DKK", "a day"]]},
    "Estonia": {"frammento": "Estonia* EUR 70", "importi": [[70, "EUR", "a day"]]},
    "Finland": {"frammento": "Finland* on a case-by-case basis EUR 50 In addition to the funds, or tickets, required for the departure and accommodation during the stay",
                "importi": [], "nota": "The table puts “on a case-by-case basis” and “EUR 50” side by side, with the remark that the amount comes on top of the money or tickets for departure and accommodation."},
    "France": {"frammento": "France* EUR 65 EUR 32.50 - persons holding proof of accommodation EUR 120 – persons holding no proof of accommodation",
               "importi": [[120, "EUR", "a day without proof of accommodation"], [65, "EUR", "a day for the nights covered by a hotel booking"],
                           [32.5, "EUR", "a day with proof of accommodation"]]},
    "Germany": {"frammento": "Germany* EUR 45", "importi": [[45, "EUR", "a day"]]},
    "Greece": {"frammento": "Greece* EUR 50 EUR 25 – for minors EUR 300 - for a stay of up to 5 days",
               "importi": [[50, "EUR", "a day"], [25, "EUR", "a day for minors"], [300, "EUR", "for a stay of up to 5 days"]]},
    "Hungary": {"frammento": "Hungary* EUR 40", "importi": [[40, "EUR", "a day"]]},
    "Iceland": {"frammento": "Iceland* ISK 8000 ISK 40 000 - for each entry", "importi": [[8000, "ISK", "a day"], [40000, "ISK", "for each entry"]]},
    "Italy": {"frammento": "Italy* EUR 269.60 1 to 5 days overall fixed sum", "importi": [[269.6, "EUR", "fixed sum for a stay of 1 to 5 days"]]},
    "Latvia": {"frammento": "Latvia* EUR 14 No less than the minimum monthly wage (EUR 700), where the scheduled stay exceeds 30 days",
               "importi": [[14, "EUR", "a day"], [700, "EUR", "at least, for stays of more than 30 days (the minimum monthly wage)"]]},
    "Lithuania": {"frammento": "Lithuania* EUR 50", "importi": [[50, "EUR", "a day"]]},
    "Luxembourg": {"frammento": "Luxembourg EUR 67", "importi": [[67, "EUR", "a day"]]},
    "Malta": {"frammento": "Malta EUR 48", "importi": [[48, "EUR", "a day"]]},
    "Netherlands": {"frammento": "Netherlands* EUR 55", "importi": [[55, "EUR", "a day"]]},
    "Norway": {"frammento": "Norway* on a case-by-case basis NOK 300/day (hosted/pre-paid accommodation); NOK 1,300/day (no proof of accommodation). If >1 traveller: ≥ NOK 1,000 per person/day.",
               "importi": [[300, "NOK", "a day with hosted or pre-paid accommodation"], [1300, "NOK", "a day without proof of accommodation"],
                           [1000, "NOK", "at least, per person a day, if more than one traveller"]]},
    "Poland": {"frammento": "Poland* PLN 300 for stay not exceeding 4 days PLN 75 per day by stay exceeding 4 days",
               "importi": [[300, "PLN", "for a stay of up to 4 days"], [75, "PLN", "a day for stays of more than 4 days"]]},
    "Portugal": {"frammento": "Portugal* EUR 75 - for each entry EUR 40 - for each day spent on the territory",
                 "importi": [[75, "EUR", "for each entry"], [40, "EUR", "for each day in Portugal"]]},
    "Romania": {"frammento": "Romania* EUR 50, but no less then € 500 for the entire period, or equivalent",
                "importi": [[50, "EUR", "a day"], [500, "EUR", "at least, for the whole stay"]]},
    "Slovakia": {"frammento": "Slovakia* EUR 56", "importi": [[56, "EUR", "a day"]]},
    "Slovenia": {"frammento": "Slovenia* EUR 70 EUR 35 - for minors accompanied by their parents",
                 "importi": [[70, "EUR", "a day"], [35, "EUR", "a day for minors travelling with their parents"]]},
    "Spain": {"frammento": "Spain* 10% of the gross national minimum wage (EUR 122.10); 90% of the gross national minimum wage (EUR 1 098.90) - minimum amount at the disposal",
              "importi": [[122.1, "EUR", "a day (10% of the gross minimum wage)"], [1098.9, "EUR", "at least, in total (90% of the gross minimum wage)"]]},
    "Sweden": {"frammento": "Sweden SEK 700", "importi": [[700, "SEK", "a day"]]},
    "Switzerland": {"frammento": "Switzerland* CHF 100 CHF 30 - students", "importi": [[100, "CHF", "a day"], [30, "CHF", "a day for students"]]},
}

# Fornitori dei servizi visti letti sulla pagina ufficiale dell'ambasciata o del consolato (31/10/2026).
# paese = come nel file della Commissione; testo = frase pubblicata (inglese), frammento = parole della pagina ufficiale.
FORNITORI = [
    {"paese": "UNITED KINGDOM", "stato": "Netherlands", "fonte": "nl_uk", "fornitore": "VFS Global",
     "frammento": "To apply for a Schengen visa in the United Kingdom go to the VFS Global application centre in Birmingham, Edinburgh, London or Manchester.",
     "testo": "The Dutch government's page says to apply at the VFS Global application centre in Birmingham, Edinburgh, London or Manchester."},
    {"paese": "UNITED KINGDOM", "stato": "Germany", "fonte": "de_uk", "fornitore": "TLScontact",
     "frammento": "operated by our service provider, TLScontact, serve visa applicants residing in England (with exceptions, see below), Northern Ireland and Wales",
     "testo": "The German missions' page says the visa application centres in London and Manchester (for England, with exceptions, Northern Ireland and Wales) and Edinburgh (for Scotland) are operated by TLScontact."},
    {"paese": "UNITED KINGDOM", "stato": "Italy", "fonte": "it_uk", "fornitore": "VFS Global",
     "frammento": "Appointments are exclusively managed through our service partner, VFS Global.",
     "testo": "The Italian Consulate General in London says appointments are managed only through its service partner, VFS Global, which charges an extra service fee."},
    {"paese": "UNITED KINGDOM", "stato": "Belgium", "fonte": "be_uk", "fornitore": "TLScontact",
     "frammento": "For all general visa enquiries (application process, processing times, appointments, documentation required) please contact TLScontact",
     "testo": "The Belgian embassy's page sends questions about the application process, appointments and documents to TLScontact."},
    {"paese": "UNITED KINGDOM", "stato": "Portugal", "fonte": "pt_uk", "fornitore": "VFS Global",
     "frammento": "visa application center in London, operated by VFS Global",
     "testo": "The Portuguese Consulate General in London says its visa application centre in London is operated by VFS Global."},
    {"paese": "UNITED ARAB EMIRATES", "stato": "Netherlands", "fonte": "nl_ae", "fornitore": "VFS Global",
     "frammento": "To apply for a Schengen visa in the United Arab Emirates go to the VFS Global application centre in Abu Dhabi or Dubai.",
     "testo": "The Dutch government's page says to apply at the VFS Global application centre in Abu Dhabi or Dubai."},
    {"paese": "UNITED ARAB EMIRATES", "stato": "Germany", "fonte": "de_ae", "fornitore": "VFS Global",
     "frammento": "The Consulate works exclusively with the external service provider VFS Global. Visa applications can be submitted by appointment only at the VFS Global Germany Visa Application Centres in Abu Dhabi or Dubai.",
     "testo": "The German Consulate General in Dubai works only with VFS Global: applications by appointment at the VFS Global centres in Abu Dhabi or Dubai."},
    {"paese": "UNITED ARAB EMIRATES", "stato": "Italy", "fonte": "it_ad", "fornitore": "BLS International (Abu Dhabi), VFS Global (Dubai)",
     "frammento": "may apply to BLS International. Residents of the Emirate of Dubai and Northern Emirates are instead advised to contact the Dubai Consulate General which operates through the VFS Global Dubai office",
     "testo": "The Italian embassy in Abu Dhabi takes applications from holders of an Abu Dhabi residence visa through BLS International; residents of Dubai and the Northern Emirates go to the Consulate General in Dubai, which works through VFS Global."},
]

# ---------------------------------------------------------------- domanda (autocompletamento Google)
QUERY = {
    "gb": ["schengen visa from uk", "schengen visa from uk for", "easiest schengen visa from uk", "schengen visa uk residents",
           "schengen visa from uk cost", "schengen visa from uk for indian passport", "schengen visa from london", "schengen visa insurance uk",
           "schengen visa from uk processing time", "schengen visa from uk requirements"],
    "ae": ["schengen visa from dubai", "schengen visa from uae", "easiest schengen visa from dubai", "schengen visa from dubai cost",
           "schengen visa from dubai for indian passport", "schengen visa from abu dhabi", "schengen visa uae residents",
           "schengen visa from dubai processing time", "schengen visa from dubai requirements"],
}
STATI_DOMANDA = ["france", "spain", "italy", "germany", "netherlands", "greece", "portugal", "switzerland", "denmark", "iceland", "belgium",
                 "norway", "malta", "finland", "austria", "lithuania", "poland", "hungary", "czech", "bulgaria", "romania", "latvia",
                 "luxembourg", "estonia", "croatia", "sweden", "slovakia", "slovenia"]


def norm(t):
    t = re.sub(r"\s+", " ", t.replace(" ", " ").replace(" ", " ")).strip()
    return re.sub(r" ([,.;:)])", r"\1", t)


def scarica(u, accetta=None):
    h = dict(UA)
    if accetta:
        h["Accept"] = accetta
        h["Accept-Language"] = "eng"
    for i in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=90)
            return r.status, r.read()
        except Exception as e:  # noqa: BLE001
            st = getattr(e, "code", None)
            if st:
                return st, b""
            time.sleep(3)
    return None, b""


def testo_di(b, formato):
    if formato == "pdf":
        return norm(subprocess.run(["pdftotext", "-raw", "-", "-"], input=b, capture_output=True).stdout.decode("utf-8", "replace"))
    t = b.decode("utf-8", "replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S | re.I)
    return norm(H.unescape(re.sub(r"<[^>]+>", " ", t)))


def autocompleta(q, gl):
    u = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode({"client": "firefox", "gl": gl, "hl": "en", "q": q})
    for _ in range(3):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20)
            return json.loads(r.read().decode("utf-8", "replace"))[1]
        except Exception:  # noqa: BLE001
            time.sleep(2)
    return None


def nuova_domanda():
    out = {}
    for gl, qs in QUERY.items():
        dove = "uk" if gl == "gb" else "dubai"
        for q in qs + [f"{s} visa from {dove}" for s in STATI_DOMANDA]:
            out[f"{gl}|{q}"] = autocompleta(q, gl)
            time.sleep(0.3)
    return {"data": date.today().isoformat(), "metodo": "https://suggestqueries.google.com/complete/search?client=firefox&gl=<gb|ae>&hl=en&q=…", "query": out}


def main():
    oggi = date.today().isoformat()
    errori = []
    testi, fonti = {}, {}
    for k, F in FONTI.items():
        st, b = scarica(F["url"], F.get("accetta"))
        if st != 200 or not b:
            errori.append(f"{k}: HTTP {st} ({F['url']})")
            continue
        tx = testo_di(b, F["formato"])
        testi[k] = tx
        fonti[k] = {**{c: F[c] for c in F if c != "accetta"}, "http": st, "letto_il": oggi, "byte": len(b),
                    "sha256": hashlib.sha256(b).hexdigest()}
    if errori:
        sys.exit("ERRORE, JSON non aggiornato:\n" + "\n".join(errori))
    for k, L in LETTURE.items():
        if norm(L["frammento"]) not in testi[L["fonte"]]:
            errori.append(f"frammento non trovato ({k}, {L['fonte']}): {L['frammento']!r}")
    for s, R in RIFERIMENTO.items():
        if norm(R["frammento"]) not in testi["riferimento"]:
            errori.append(f"importo di riferimento non trovato ({s}): {R['frammento']!r}")
        for imp, val, _ in R["importi"]:
            forme = {f"{val} {imp:g}", f"{val} {imp:,.2f}", f"{imp:g} {val}", f"{val} {imp:,g}".replace(",", " "), f"{val} {imp:,g}",
                     f"{val} {imp:.2f}", f"{imp:,g}".replace(",", ".") + f" {val}", f"{val} " + f"{imp:,.2f}".replace(",", " ")}
            if val == "EUR":
                forme.add(f"€ {imp:g}")
            if not any(x in R["frammento"] for x in forme):
                errori.append(f"importo {val} {imp} non scritto nel frammento di {s}")
    for F in FORNITORI:
        if norm(F["frammento"]) not in testi[F["fonte"]]:
            errori.append(f"fornitore non trovato ({F['stato']}, {F['paese']}): {F['frammento']!r}")
    # ancoraggio AED/USD: tutte le righe "US Dollar" dei due PDF della CBUAE valgono 3.6725
    righe_usd = []
    for k in ("cbuae_ago", "cbuae_set"):
        xs = re.findall(r"(\d{2}-\w{3}-\d{4}) US Dollar (\d+\.\d+)", testi[k])
        if len(xs) < 15:
            errori.append(f"{k}: solo {len(xs)} righe US Dollar")
        righe_usd += xs
    diversi = [x for x in righe_usd if float(x[1]) != LETTURE["ancoraggio"]["valore"]]
    if diversi:
        errori.append(f"CBUAE: righe US Dollar diverse da 3.6725: {diversi[:3]}")
    if errori:
        sys.exit("ERRORE, JSON non aggiornato:\n" + "\n".join(errori))
    vecchio = json.loads(USCITA.read_text(encoding="utf-8")) if USCITA.exists() else {}
    domanda = nuova_domanda() if "--domanda" in sys.argv else vecchio.get("domanda")
    if not domanda:
        sys.exit("ERRORE: nessuna domanda salvata: lanciare con --domanda")
    dati = {
        "_nota": "Generato da raccolta/schengen_residenti.py: non modificare a mano. Cifre sui visti in dati/rifiuti.json.",
        "letto_il": oggi,
        "fonti": fonti,
        "letture": {k: {c: L[c] for c in L} for k, L in LETTURE.items()},
        "riferimento": RIFERIMENTO,
        "fornitori": FORNITORI,
        "ancoraggio_righe": {"giorni": len(righe_usd), "dal": righe_usd[0][0], "al": righe_usd[-1][0]},
        "domanda": domanda,
    }
    cont = {k: dati[k] for k in ("fonti", "letture", "riferimento", "fornitori", "ancoraggio_righe")}
    dati["impronta"] = hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20]
    USCITA.write_text(json.dumps(dati, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Scritto {USCITA}: {len(fonti)} fonti, {len(LETTURE)} letture, {len(RIFERIMENTO)} Stati con importi di riferimento, "
          f"{len(FORNITORI)} fornitori letti, ancoraggio 3.6725 su {len(righe_usd)} giorni; domanda del {domanda['data']}.")


if __name__ == "__main__":
    main()
