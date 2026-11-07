"""Rilegge le fonti ufficiali della sezione "Health insurance for visas" (dal 7/11/2026) e scrive visaincome/dati/assicurazione.json.

Uso (dalla radice del repository):
    python3 visaincome/raccolta/assicurazione.py              # rilegge le fonti e scrive il JSON (domanda: quella già salvata)
    python3 visaincome/raccolta/assicurazione.py --domanda    # rifà anche l'autocompletamento di Google (circa 1 minuto)

Fonti (lette il 7/11/2026 con richieste HTTP dirette, nessun browser)
- Consolato generale di Spagna a Buenos Aires: pagine dei visti per nomadi digitali (teletrabajo), residenza non lucrativa e studio.
- BOE, Real Decreto 1155/2024 (regolamento stranieri): art. 35 (visto per studio) e art. 61 (residenza non lucrativa).
- MNE portoghese (vistos.mne.gov.pt): documenti per i visti di residenza (D7, D8 e studio usano la stessa lista generale).
- Gazzetta Ufficiale n. 79 del 4/4/2024 (decreto sui nomadi digitali) e Consolato generale d'Italia a Boston (pagina del visto).
- MUP croato (nomadi digitali), OIF ungherese (White Card), Service-Portal Berlin (Blue Card), BOI thailandese (LTR),
  GOV.UK (immigration health surcharge), Codice dei visti UE (art. 15) e pagina della Commissione "Applying for a Schengen visa".
- LETTURE: ogni valore letto A MANO il 7/11/2026 con il FRAMMENTO del testo ufficiale. A ogni lancio si controlla che ogni
  frammento sia ancora nella fonte: se ne manca uno il JSON NON si aggiorna (codice 1) finché qualcuno non rilegge la fonte.
- Le righe DTV (Thailandia), Messico e Study in Italy usano le letture già salvate in dtv.json, mexico.json e studio_italia.json
  (genera.py le prende da lì): qui non si rileggono.
"""
import hashlib
import html
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
USCITA = RADICE / "dati" / "assicurazione.json"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"}

_BA = "https://www.exteriores.gob.es/Consulados/buenosaires/es/ServiciosConsulares/Paginas/index.aspx?scca=Visados&scco=Argentina&scd=40&scs="
FONTI = {
    "es_nd": {"titolo": "Consulate General of Spain in Buenos Aires, Residence visa for remote work (digital nomad)", "editore": "Spanish Ministry of Foreign Affairs",
              "url": _BA + "Visados+Nacionales+-+Visado+de+residencia+para+teletrabajo+%28n%C3%B3mada+digital%29", "lingua": "es"},
    "es_nl": {"titolo": "Consulate General of Spain in Buenos Aires, Non-lucrative residence visa", "editore": "Spanish Ministry of Foreign Affairs",
              "url": _BA + "Visados+Nacionales+-+Visado+de+residencia+no+lucrativa", "lingua": "es"},
    "es_es": {"titolo": "Consulate General of Spain in Buenos Aires, Study visa", "editore": "Spanish Ministry of Foreign Affairs",
              "url": _BA + "Visados+Nacionales+-+Visado+de+estudios", "lingua": "es"},
    "es_rd": {"titolo": "Royal Decree 1155/2024, Regulation of the Organic Law 4/2000 on foreigners (BOE, consolidated text)", "editore": "Boletín Oficial del Estado",
              "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2024-24099", "lingua": "es"},
    "es_dgsfp": {"titolo": "Directorate General for Insurance and Pension Funds (DGSFP), register of insurance companies", "editore": "Spanish Ministry of Economy",
                 "url": "https://dgsfp.mineco.gob.es/es/Entidades/Paginas/rrpp.aspx", "lingua": "es"},
    "pt_res": {"titolo": "Portuguese Ministry of Foreign Affairs, National visas: necessary documentation, Residency", "editore": "Ministério dos Negócios Estrangeiros",
               "url": "https://vistos.mne.gov.pt/en/national-visas/necessary-documentation/residency", "lingua": "en"},
    "it_dn": {"titolo": "Decree of 29 February 2024 on digital nomads and remote workers, Gazzetta Ufficiale no. 79 of 4 April 2024", "editore": "Gazzetta Ufficiale della Repubblica Italiana",
              "url": "https://www.gazzettaufficiale.it/eli/gu/2024/04/04/79/sg/pdf", "lingua": "it", "formato": "pdf"},
    "it_boston": {"titolo": "Consulate General of Italy in Boston, Digital nomad / remote worker visa", "editore": "Italian Ministry of Foreign Affairs",
                  "url": "https://consboston.esteri.it/en/servizi-consolari-e-visti/servizi-per-il-cittadino-straniero/visti/digital-nomad-remote-worker/", "lingua": "en"},
    "hr_mup": {"titolo": "Croatian Ministry of the Interior, Temporary stay of digital nomads", "editore": "Ministarstvo unutarnjih poslova",
               "url": "https://mup.gov.hr/aliens-281621/stay-and-work/temporary-stay-of-digital-nomads/286833", "lingua": "en"},
    "hu_oif": {"titolo": "National Directorate-General for Aliens Policing, White Card (digital nomad stay)", "editore": "Országos Idegenrendészeti Főigazgatóság",
               "url": "https://oif.gov.hu/tajekoztatok/feher-kartya-digitalis-nomad-tartozkodas", "lingua": "hu"},
    "de_berlin": {"titolo": "Service-Portal Berlin, EU Blue Card", "editore": "State of Berlin, Landesamt für Einwanderung",
                  "url": "https://service.berlin.de/dienstleistung/324659/en/", "lingua": "en"},
    "th_ltr": {"titolo": "Thailand Board of Investment, Long-Term Resident (LTR) Visa", "editore": "Thailand Board of Investment",
               "url": "https://ltr.boi.go.th/", "lingua": "en"},
    "th_ltr_doc": {"titolo": "Thailand Board of Investment, LTR visa required documents checklist (Wealthy Pensioners, 6 November 2025; the same insurance text is in the other three checklists)",
                   "editore": "Thailand Board of Investment", "url": "https://ltr.boi.go.th/documents/Required-docs-Wealthy-Pensioners-06-11-2025.pdf",
                   "pagina": "https://ltr.boi.go.th/page/required-documents.html", "lingua": "en", "formato": "pdf"},
    "uk_ihs": {"titolo": "GOV.UK, Pay for UK healthcare as part of your immigration application", "editore": "UK Visas and Immigration",
               "url": "https://www.gov.uk/healthcare-immigration-application", "lingua": "en"},
    "uk_ihs_costo": {"titolo": "GOV.UK, Pay for UK healthcare as part of your immigration application: how much you have to pay", "editore": "UK Visas and Immigration",
                     "url": "https://www.gov.uk/healthcare-immigration-application/how-much-pay", "lingua": "en"},
    "ue_codice": {"titolo": "Regulation (EC) No 810/2009 (Visa Code), consolidated text of 2 February 2020, Article 15", "editore": "Publications Office of the European Union",
                  "url": "https://publications.europa.eu/resource/cellar/82b7a82d-473e-11ea-b81b-01aa75ed71a1.0006.03/DOC_4",
                  "pubblico": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02009R0810-20200202", "lingua": "en"},
    "ue_commissione": {"titolo": "European Commission, Applying for a Schengen visa", "editore": "European Commission",
                       "url": "https://home-affairs.ec.europa.eu/policies/schengen/visa-policy/applying-schengen-visa_en", "lingua": "en"},
}

# chiave -> (fonte, frammento, valore facoltativo). Frammenti copiati dal testo normalizzato (spazi unici, entità HTML sciolte).
LETTURE = {
    # Spagna, nomadi digitali (Buenos Aires)
    "es_nd_seguro": ("es_nd", "certificado de seguro de enfermedad público o privado contratado con una entidad aseguradora autorizada a operar en España"),
    "es_nd_riesgos": ("es_nd", "El seguro debe cubrir todos los riesgos asegurados por el sistema público de salud en España."),
    "es_nd_ss": ("es_nd", "No es necesario presentar el seguro de enfermedad si se prueba la cobertura por el sistema público de la Seguridad Social española."),
    "es_nd_convenio": ("es_nd", "en lugar del seguro de enfermedad, se presentará un certificado de derecho de cobertura emitido por la institución competente del Estado en cuyo sistema de Seguridad Social esté asegurado"),
    # Spagna, residenza non lucrativa
    "es_nl_seguro": ("es_nl", "certificado de seguro de enfermedad público o privado contratado con una entidad aseguradora autorizada a operar en España. El seguro debe cubrir todos los riesgos asegurados por el sistema público de salud en España."),
    "es_nl_100": ("es_nl", "Se deberá contratar una cobertura médica durante el primer año de residencia que cubra el 100% de los gastos médicos, sin copagos y sin carencias."),
    "es_rd_61": ("es_rd", "sin necesidad de desarrollar ninguna actividad laboral o profesional, de conformidad con lo dispuesto en este capítulo. b) Contar con un seguro de enfermedad."),
    "es_rd_64": ("es_rd", "Haber mantenido durante la vigencia de la autorización que se pretende renovar y continuar con un seguro de enfermedad."),
    # Spagna, studio
    "es_es_seguro": ("es_es", "certificado de seguro de enfermedad público o privado contratado con una entidad aseguradora autorizada a operar en España, con prestaciones similares las concedidas por la cartera común básica de servicios asistenciales del Sistema Nacional de Salud, válido para la duración de la estancia prevista."),
    "es_es_viaje": ("es_es", "no son válidos los seguros de viajero ni asociados a tarjetas de crédito"),
    "es_es_100": ("es_es", "ha de cubrir 100% de los gastos médicos hospitalarios y extrahospitalarios, sin copagos ni carencias."),
    "es_rd_35": ("es_rd", "i) Contar con un seguro de enfermedad, concertado con una entidad aseguradora autorizada para operar en España, con prestaciones similares a las concedidas por la cartera común básica de servicios asistenciales del Sistema Nacional de Salud, válido para la duración de la estancia prevista."),
    # Portogallo, visti di residenza (D7, D8, studio)
    "pt_viagem": ("pt_res", "Valid travel insurance, covering necessary medical expenses, including urgent medical assistance and possible repatriation"),
    "pt_acordo": ("pt_res", "this requirement may be waived in the case of a Bilateral/International Agreement between Portugal and the country of origin concerning medical assistance that qualifies certain beneficiaries with recognized insurance, as for example in the case of Brazil (PB4) and the United Kingdom (S1)."),
    "pt_estudantes": ("pt_res", "Higher education students admitted to a higher education institution officially recognized under the terms of the legislation in force (Article 91-B of Law 23/2007) are exempt from presenting health insurance or equivalent"),
    "pt_formacao": ("pt_res", "if they prove they have the means, travel insurance and insurance of health."),
    # Italia, nomadi digitali
    "it_dn_decreto": ("it_dn", "dispongano di una assicurazione sanitaria per cure mediche e ricovero ospedaliero valida per il territorio nazionale e per il periodo del soggiorno"),
    "it_boston_polizza": ("it_boston", "Letter or certificate of travel medical insurance showing coverage for medical expenses, hospitalization costs and repatriation for medical reasons, for the days you are outside the United States."),
    "it_boston_minimo": ("it_boston", "Insurance coverage must not be less than 30,000 Euro (or $50,000).", 30000),
    # Croazia
    "hr_seguro": ("hr_mup", "proof of health insurance for the period of time that you plan to be in Croatia (travel or private health insurance must cover the territory of the Republic of Croatia)"),
    # Ungheria
    "hu_biztositas": ("hu_oif", "Önnek okirattal igazolnia kell, hogy az egészségügyi ellátások teljes körére biztosítottnak minősül, vagy az egészségügyi ellátás költségeit biztosítani képes."),
    "hu_megelhetes": ("hu_oif", "a megélhetését igazoló okiratok alapján egészségügyi ellátása költségeit biztosítani képes."),
    # Germania, Blue Card (Berlino)
    "de_seguro": ("de_berlin", "You have health insurance in Germany, either in the statutory health insurance system or a comparable private health insurance."),
    "de_estero": ("de_berlin", "Foreign health insurance is not sufficient."),
    # Thailandia, LTR
    "th_ltr_seguro": ("th_ltr", "Insured under a health insurance covering a minimum of USD 50,000 OR currently receiving social security benefits in Thailand OR deposit and maintain at least USD 100,000 in bank account balance", 50000),
    "th_ltr_mantenere": ("th_ltr", "Every condition and requirement must be maintained during the length of the visa, including investment amounts, employment status, bank account balances, and insurance coverage."),
    "th_ltr_durata": ("th_ltr_doc", "Must cover the entire duration of stay in Thailand for hospitalization and medical treatment at least USD 50,000 with a remaining coverage period of at least 10 months.", 50000),
    "th_ltr_viaggio": ("th_ltr_doc", "Life insurance without health insurance and travel insurance are not accepted."),
    # Regno Unito, IHS
    "uk_ihs": ("uk_ihs", "Most people need to pay the immigration health surcharge"),
    "uk_ihs_nhs": ("uk_ihs", "You can start using the NHS free of charge from the date your visa starts."),
    "uk_ihs_studenti": ("uk_ihs_costo", "£776 per year for students, their dependants, and those on a Youth Mobility Scheme visa", 776),
    "uk_ihs_minori": ("uk_ihs_costo", "£776 per year for visa and immigration applicants who are under the age of 18 at time of application", 776),
    "uk_ihs_breve": ("uk_ihs_costo", "You do not need to pay the surcharge if you’re applying from outside the UK for 6 months or less."),
    "uk_ihs_altri": ("uk_ihs_costo", "£1,035 per year for all other visa and immigration applications", 1035),
    # UE, visto Schengen (art. 15 del Codice dei visti)
    "ue_15_1": ("ue_codice", "Applicants for a uniform visa for one or two entries shall prove that they are in possession of adequate and valid travel medical insurance to cover any expenses which might arise in connection with repatriation for medical reasons, urgent medical attention and/or emergency hospital treatment or death, during their stay(s) on the territory of the Member States."),
    "ue_15_2": ("ue_codice", "Applicants for a multiple-entry visa shall prove that they are in possession of adequate and valid travel medical insurance covering the period of their first intended visit."),
    "ue_15_2_dich": ("ue_codice", "In addition, such applicants shall sign the statement, set out in the application form, declaring that they are aware of the need to be in possession of travel medical insurance for subsequent stays."),
    "ue_15_3": ("ue_codice", "The insurance shall be valid throughout the territory of the Member States and cover the entire period of the person’s intended stay or transit."),
    "ue_15_3_minimo": ("ue_codice", "The minimum coverage shall be EUR 30 000.", 30000),
    "ue_15_3_ltv": ("ue_codice", "When a visa with limited territorial validity covering the territory of more than one Member State is issued, the insurance cover shall be valid at least in the Member States concerned."),
    "ue_15_4_terzi": ("ue_codice", "When another person takes out insurance in the name of the applicant, the conditions set out in paragraph 3 shall apply."),
    "ue_15_6": ("ue_codice", "The insurance requirement may be considered to have been met where it is established that an adequate level of insurance may be presumed in the light of the applicant’s professional situation. The exemption from presenting proof of travel medical insurance may concern particular professional groups, such as seafarers, who are already covered by travel medical insurance as a result of their professional activities."),
    "ue_15_7": ("ue_codice", "Holders of diplomatic passports shall be exempt from the requirement to hold travel medical insurance."),
    "ue_15_4": ("ue_codice", "Applicants shall, in principle, take out insurance in their country of residence. Where this is not possible, they shall seek to obtain insurance in any other country."),
    "ue_15_5": ("ue_codice", "When assessing whether the insurance cover is adequate, consulates shall ascertain whether claims against the insurance company would be recoverable in a Member State."),
    "ue_commissione": ("ue_commissione", "Medical insurance covering emergency medical care, hospitalisation and repatriation (including in the event of death)."),
}

# autocompletamento: ricerca -> ragione (le pagine per visto si fanno solo se la loro ricerca restituisce suggerimenti)
QUERY = {"us": ["health insurance for spain visa", "health insurance for spain non lucrative visa", "health insurance for spain digital nomad visa",
                "health insurance for spain student visa", "health insurance for portugal visa", "health insurance for portugal d7 visa",
                "health insurance for portugal d8 visa", "health insurance for portugal student visa", "insurance for d7 visa",
                "health insurance for italy visa", "health insurance for italy digital nomad visa", "health insurance for croatia digital nomad",
                "health insurance for hungary white card", "health insurance for germany blue card", "health insurance for ltr visa thailand",
                "health insurance for dtv visa thailand", "insurance for dtv", "schengen visa insurance", "schengen visa insurance requirements",
                "travel insurance for schengen visa"],
         "in": ["schengen visa insurance", "schengen visa insurance requirements", "travel insurance for schengen visa"],
         "gb": ["schengen visa insurance", "health insurance for spain visa", "health insurance for portugal visa"]}


def get(u, tentativi=4):
    for i in range(tentativi):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120)
            return r.status, r.read()
        except Exception as e:  # noqa: BLE001
            c = getattr(e, "code", 0)
            if c in (403, 404, 410):
                return c, b""
            time.sleep(5 + 10 * i)  # service.berlin.de risponde 429 se si insiste
    return 0, b""


def norm(t):
    t = re.sub(r"\s+", " ", (t or "").replace("\xa0", " ")).strip()
    return re.sub(r" ([.,;:])", r"\1", t)


def testo(b):
    if b[:4] == b"%PDF":
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "doc.pdf"
            f.write_bytes(b)
            return norm(subprocess.run(["pdftotext", str(f), "-"], capture_output=True, text=True, timeout=180).stdout)
    t = b.decode("utf-8", "replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
    return norm(html.unescape(re.sub(r"<[^>]+>", " ", t)))


def sha(b):
    return hashlib.sha256(b).hexdigest()


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
        for q in qs:
            out[f"{gl}|{q}"] = autocompleta(q, gl)
            time.sleep(0.3)
    return {"data": date.today().isoformat(), "metodo": "https://suggestqueries.google.com/complete/search?client=firefox&gl=<us|in|gb>&hl=en&q=…", "query": out}


def main():
    vecchio = json.loads(USCITA.read_text(encoding="utf-8")) if USCITA.exists() else {}
    oggi = date.today().isoformat()
    fonti, testi, errori = {}, {}, []
    for k, f in FONTI.items():
        st, b = get(f["url"])
        fonti[k] = {**f, "http": st, "letto_il": oggi, "byte": len(b), "sha256": sha(b) if b else None}
        fonti[k].setdefault("formato", "html")
        testi[k] = testo(b) if st == 200 and b else ""
        if st != 200:
            errori.append(f"{k}: HTTP {st} ({f['url']})")
        time.sleep(1)
    letture = {}
    for k, v in LETTURE.items():
        fonte, fr = v[0], v[1]
        if fr not in testi.get(fonte, ""):
            errori.append(f"{k}: frammento non trovato in {fonte}: {fr[:80]}…")
        letture[k] = {"fonte": fonte, "frammento": fr, **({"valore": v[2]} if len(v) > 2 else {})}
    # la fonte del registro DGSFP serve solo come link: basta che risponda
    if errori:
        print("NON aggiornato:\n  " + "\n  ".join(errori))
        sys.exit(1)
    domanda = nuova_domanda() if "--domanda" in sys.argv else vecchio.get("domanda", {})
    if not domanda:
        domanda = nuova_domanda()
    for k in fonti:
        fonti[k]["sha256_testo"] = sha(testi[k].encode()) if testi[k] else None
    cont = {"url": {k: f["url"] for k, f in fonti.items()}, "letture": letture, "domanda": domanda}
    out = {"_nota": "Generato da raccolta/assicurazione.py: non modificare a mano. Le letture sono frammenti dei testi ufficiali, ricontrollati a ogni lancio.",
           "letto_il": oggi, "fonti": fonti, "letture": letture, "domanda": domanda}
    out["impronta"] = hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20]
    USCITA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Scritto {USCITA}: {len(fonti)} fonti, {len(letture)} letture, domanda del {domanda.get('data')}")


if __name__ == "__main__":
    main()
