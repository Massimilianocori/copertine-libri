"""Rilegge le fonti ufficiali della sezione "Health insurance in Germany for visas and residence permits" (dal 14/11/2026)
e scrive visaincome/dati/assicurazione_de.json.

Uso (dalla radice del repository):
    python3 visaincome/raccolta/assicurazione_de.py              # rilegge le fonti e scrive il JSON (domanda: quella già salvata)
    python3 visaincome/raccolta/assicurazione_de.py --domanda    # rimisura anche i volumi di ricerca (circa 5 minuti)

Fonti (lette il 14/11/2026 con richieste HTTP dirette, nessun browser)
- Auswärtiges Amt: articolo "Health insurance cover for applications for national visas" (datato 21.08.2026): regola generale,
  cassa pubblica o assicurazione privata, e l'elenco per scopo del soggiorno (studio, lavoro, lavoro autonomo, Chancenkarte,
  ricongiungimento familiare...). FAQ "Visa for Germany" (consiglio per chi entra senza visto).
- Legge sul soggiorno (AufenthG), traduzione inglese del Ministero dell'Interno su gesetze-im-internet.de: art. 2 (3).
- Landesamt für Einwanderung di Berlino: pagine del servizio per Blue Card, lavoro autonomo (freelance) e studio; i due fogli
  informativi in PDF sull'assicurazione (LEA 4326a e LEA 4310b, 12/2024).
- Il Codice dei visti UE (art. 15, 30.000 €) NON si rilegge qui: genera.py usa le letture di dati/assicurazione.json.
- NON lette (e quindi non citate): make-it-in-germany.com (pagina di verifica del browser "Radware" su ogni URL, anche sui PDF:
  non aggirata), bamf.de (la pagina della Blue Card non parla di assicurazione), arbeitsagentur.de (nessuna pagina trovata
  con una regola sull'assicurazione per i visti).
- PARTNER: la home inglese di ottonova, solo per controllare che le parole del riquadro (spento) siano ancora sul loro sito.
- LETTURE: ogni frammento è stato letto A MANO il 14/11/2026. A ogni lancio si controlla che sia ancora nella fonte: se ne manca
  uno il JSON NON si aggiorna (codice 1) finché qualcuno non rilegge la fonte. Con "sezione" il frammento deve seguire subito
  il titolo numerato dell'elenco del ministero (es. "13. Opportunity card"): così una frase uguale in due voci resta legata alla sua.
- DOMANDA: volumi medi mensili (Google Ads) dello strumento dei volumi, per Paese. La chiave sta fuori dal repository e viene
  letta solo dentro la shell di curl: non passa da Python, non viene stampata né scritta.
"""
import hashlib
import html
import json
import os
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
USCITA = RADICE / "dati" / "assicurazione_de.json"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"}

FONTI = {
    "aa_kv": {"titolo": "Federal Foreign Office, Health insurance cover for applications for national visas (article dated 21 August 2026)",
              "editore": "Auswärtiges Amt", "url": "https://www.auswaertiges-amt.de/en/2804434-2804434", "lingua": "en"},
    "aa_faq": {"titolo": "Federal Foreign Office, FAQ: Visa for Germany", "editore": "Auswärtiges Amt",
               "url": "https://www.auswaertiges-amt.de/en/visa-service/buergerservice/faq/606848-606848", "lingua": "en"},
    "aufenthg": {"titolo": "Residence Act (Aufenthaltsgesetz), English translation by the Federal Ministry of the Interior, section 2 (3)",
                 "editore": "Federal Ministry of Justice, gesetze-im-internet.de",
                 "url": "https://www.gesetze-im-internet.de/englisch_aufenthg/englisch_aufenthg.html", "lingua": "en"},
    "be_bc": {"titolo": "Service-Portal Berlin, EU Blue Card", "editore": "State of Berlin, Landesamt für Einwanderung",
              "url": "https://service.berlin.de/dienstleistung/324659/en/", "lingua": "en"},
    "be_free": {"titolo": "Service-Portal Berlin, Residence permit for a freelance employment", "editore": "State of Berlin, Landesamt für Einwanderung",
                "url": "https://service.berlin.de/dienstleistung/328332/en/", "lingua": "en"},
    "be_stud": {"titolo": "Service-Portal Berlin, Residence permit for the purpose of full-time studies", "editore": "State of Berlin, Landesamt für Einwanderung",
                "url": "https://service.berlin.de/dienstleistung/305244/en/", "lingua": "en"},
    "lea_kv": {"titolo": "Landesamt für Einwanderung, Information sheet on required health insurance cover for granting / extension of residence permits (LEA 4326a, 12/2024)",
               "editore": "State of Berlin, Landesamt für Einwanderung",
               "url": "https://www.berlin.de/einwanderung/_assets/merkblatt_zur_krankenversicherung__englisch_.pdf", "lingua": "en", "formato": "pdf"},
    "lea_stud": {"titolo": "Landesamt für Einwanderung, Information for students on adequate health insurance (LEA 4310b, 12/2024)",
                 "editore": "State of Berlin, Landesamt für Einwanderung",
                 "url": "https://www.berlin.de/einwanderung/_assets/krankenversicherung-fuer-studierende-englisch.pdf", "lingua": "en", "formato": "pdf"},
    "ottonova": {"titolo": "ottonova, English home page (the company's own description; not an official source)", "editore": "ottonova",
                 "url": "https://www.ottonova.de/en", "lingua": "en", "partner": True},
}

_MIN = ("Insurance must at least cover the reimbursement of costs for outpatient and inpatient treatment and must not be restricted to emergencies. "
        "That is why travel health insurance is as a rule not enough.")
_PONTE = "Incoming insurance or travel health insurance valid in Germany for the first three months of your stay is sufficient."
_INCOMING = "In the visa process, you need to submit proof of private health insurance (often called incoming insurance) which is valid for the entire duration of your visa."

# chiave -> (fonte, frammento[, opzioni]). Frammenti copiati dal testo normalizzato (spazi unici, entità HTML sciolte).
LETTURE = {
    # Auswärtiges Amt, regola generale
    "aa_data": ("aa_kv", "21.08.2026 - Article"),
    "aa_obbligo": ("aa_kv", "In Germany, health insurance is generally compulsory. Anyone resident in Germany is required to take out health insurance with a company licensed to do business in Germany to cover their medical costs."),
    "aa_prova": ("aa_kv", "As a rule, proof of sufficient health insurance cover also needs to be presented when applying for a visa."),
    "aa_90": ("aa_kv", "In the case of longer stays of more than 90 days within a period of 180 days, travel health insurance for the Schengen area does not as a rule suffice."),
    "aa_gkv": ("aa_kv", "You always have sufficient health insurance cover if you are insured in the German statutory health insurance system."),
    "aa_gkv_conferma": ("aa_kv", "If you are going to be insured within the statutory health insurance system, the provider you choose can issue you with written confirmation which you can submit in the visa process."),
    "aa_gkv_inizio": ("aa_kv", "In the statutory health insurance system, your insurance cover generally does not begin as soon as you arrive in Germany. To make sure you are covered from day one, you therefore also need travel health insurance or alternatively incoming insurance."),
    "aa_ponte": ("aa_kv", "The insurance must have at least the scope of a Schengen travel health insurance policy. The insurance should as a rule be valid for three months.", {"valore": 3}),
    "aa_ponte_valida": ("aa_kv", "Please make sure that this travel health insurance or incoming insurance is valid despite your planned longer stay (ensure cover is not excluded if you plan to take up residence)."),
    "aa_pkv": ("aa_kv", "In principle, private health insurance has to provide the same protection as statutory health insurance. That means that insurance cannot to any major extent exclude treatment or impose limits on amounts to be reimbursed in the case of illness."),
    "aa_pkv_clausole": ("aa_kv", "It must not, as a rule, contain clauses that terminate insurance upon you reaching a certain age, ending a work contract, changing the purpose of a stay or losing residence status thus leaving you without health insurance cover."),
    "aa_incoming": ("aa_kv", "For certain temporary stays, though, for example a language course or an opportunity card, insurance is generally only taken out for a certain period of time; however, this insurance must be valid for at least the entire duration of the visa you applied for. Insurance for these stays is usually called incoming or expat insurance."),
    "aa_minimo": ("aa_kv", _MIN),
    "aa_cronico": ("aa_kv", "Please make sure that any chronic or underlying illnesses as well as (if applicable) care during pregnancy are covered."),
    "aa_lavoretto": ("aa_kv", "If you are applying for a visa to study or engage in training, to look for a university or training position or receive an opportunity card, you can take up employment to a limited extent. You need to ensure that you have adequate health insurance to also cover incidents connected to this employment."),
    "aa_bafin": ("aa_kv", "The only providers authorised to offer such private health insurance are insurance companies subject to supervision by the Federal Financial Supervisory Authority (BaFin) and those from European countries who are registered as EEA service providers."),
    "aa_libero": ("aa_kv", "Provided your insurance provider meets this criterion, you are free to choose. The Federal Foreign Office is not allowed to recommend insurance providers."),
    "aa_non_esaustivo": ("aa_kv", "This is not an exhaustive list. Exceptions are possible in individual cases."),
    # Auswärtiges Amt, elenco per scopo (con il titolo numerato della voce)
    "aa_formazione": ("aa_kv", "Trainees completing an apprenticeship have statutory health insurance.", {"sezione": "1. Vocational training and continuing vocational training"}),
    "aa_formazione_ponte": ("aa_kv", "In the visa process, you also need to present documentation regarding health insurance before your statutory health insurance cover begins. Incoming insurance or travel health insurance valid for the first three months of your stay in Germany is sufficient.", {"valore": 3}),
    "aa_formazione_privata": ("aa_kv", "If you are not working as part of your vocational training, you will normally not be eligible for statutory health insurance."),
    "aa_studenti": ("aa_kv", "Students up to the age of 30 who are enrolled at a state or state-recognised university are insured in the statutory health insurance system upon matriculation.", {"sezione": "3. Students", "valore": 30}),
    "aa_studenti_ponte": ("aa_kv", "In the visa process, you need to present documentation regarding health insurance before your statutory health insurance cover begins. " + _PONTE, {"valore": 3}),
    "aa_studenti_30": ("aa_kv", "Students aged 30 and older are generally no longer eligible for statutory health insurance. Younger students are free to choose and can opt for adequate private health insurance instead.", {"valore": 30}),
    "aa_studenti_durata": ("aa_kv", "Insurance documentation has to be presented in the visa process and insurance must be valid for at least the entire duration of your visa."),
    "aa_studenti_kolleg": ("aa_kv", "Please note that you are not covered in the statutory health insurance system if you are attending a Studienkolleg preparatory course or a language course to prepare for studies"),
    "aa_kolleg": ("aa_kv", "While you attend a Studienkolleg preparatory course, you are not covered by the statutory health insurance system.", {"sezione": "4. Studienkolleg preparatory course"}),
    "aa_lingua": ("aa_kv", "If you are attending a language course, you need private health insurance (often called incoming insurance) which is valid for the entire duration of your visa.", {"sezione": "5. Language course"}),
    "aa_cerca_uni": ("aa_kv", _INCOMING, {"sezione": "7. Looking for a place at university/vocational training"}),
    "aa_lavoro": ("aa_kv", "People who work in Germany are in many cases obliged to join the statutory health insurance system. You can choose your insurance provider yourself.", {"sezione": "8. Taking up employment"}),
    "aa_lavoro_cert": ("aa_kv", "Usually the insurance provider can issue a certificate confirming that you will be insured once your term of employment begins."),
    "aa_lavoro_ponte": ("aa_kv", "In the visa process, you also need to submit proof of insurance for the period before you enter the statutory health insurance system. " + _PONTE, {"valore": 3}),
    "aa_lavoro_esenzione": ("aa_kv", "There are exemptions from compulsory insurance, for example, if your earnings exceed a certain amount. If you are not going to be insured through the statutory health insurance system, you need to provide proof that you will be privately insured and on what terms. A non-binding quote from an insurance provider is usually not enough."),
    "aa_autonomi": ("aa_kv", "As a rule, self-employed persons need to have private health insurance. Insurance documentation has to be presented in the visa process and insurance must be valid for at least the entire duration of your visa. " + _MIN, {"sezione": "9. Self-employment"}),
    "aa_aupair": ("aa_kv", "As an au pair, you need private health insurance that also covers treatment relating to pregnancy and childbirth.", {"sezione": "10. Au-pair stays"}),
    "aa_whv": ("aa_kv", "In the visa process, proof of travel health insurance or incoming insurance which complies with Article 15 of the Visa Code is, as a rule, sufficient. The insurance must be valid for the entire duration of the stay.", {"sezione": "11. Working holiday/youth mobility agreements"}),
    "aa_whv_gkv": ("aa_kv", "Please note that depending on your type of employment, you may be subject to mandatory statutory health insurance."),
    "aa_ricerca": ("aa_kv", "Researchers with an employment contract are subject to mandatory statutory health insurance (see number 8). Researchers who have a scholarship for coming to Germany or are financing their own stay as a rule need private health insurance with proof being provided that it is valid for the entire duration of the visa.", {"sezione": "12. Conducting research"}),
    "aa_chance": ("aa_kv", _INCOMING + " " + _MIN, {"sezione": "13. Opportunity card"}),
    "aa_famiglia_gkv": ("aa_kv", "Persons being reunified with a spouse or parent (applies only to minors) who is insured through the statutory health insurance system, can also benefit from their cover.", {"sezione": "16. Family reunification"}),
    "aa_famiglia_ponte": ("aa_kv", "You should take out travel health insurance or incoming insurance for the period until statutory health insurance takes effect so that you have insurance cover for your journey and the first period in Germany. You should present proof of this in the visa process."),
    "aa_famiglia_pkv": ("aa_kv", "If the family member you are moving to join is privately insured in Germany, you also as a rule need private health insurance. Please present the relevant documentation in the visa process."),
    "aa_famiglia_tedesco": ("aa_kv", "If family members are coming to Germany to join a German citizen, they generally do not need to prove health insurance cover. Do, however, make sure you have adequate health insurance."),
    "aa_accordi": ("aa_kv", "Germany has concluded social security agreements that also apply to the field of health insurance with the following countries: Bosnia and Herzegovina, North Macedonia, Montenegro, Serbia, Turkey and Tunisia.", {"sezione": "17. Social security agreements"}),
    "aa_accordi_cert": ("aa_kv", "If you continue to be insured in your home country, you can apply for a certificate confirming your cover from your health insurance provider. This must then be presented in the visa process."),
    # Auswärtiges Amt, FAQ (chi entra senza visto)
    "aa_faq_domanda": ("aa_faq", "I don't need a visa for my trip to Germany, but are there other things I should bear in mind?"),
    "aa_faq_consiglio": ("aa_faq", "You are advised to take out health insurance before your trip which also covers return transport to your home country."),
    "aa_faq_90": ("aa_faq", "visits to the Schengen area are restricted to 90 days in any period of 180 days", {"valore": 90}),
    # Legge sul soggiorno, art. 2 (3)
    "ag_2_3": ("aufenthg", "Foreigners have a secure subsistence if they are able to earn a living, including sufficient health insurance coverage, without recourse to public funds."),
    "ag_2_3_gkv": ("aufenthg", "A foreigner who is enrolled in a statutory health insurance fund is deemed to have sufficient health insurance coverage."),
    "ag_versione": ("aufenthg", "Version information: The translation includes the amendment(s) to the Act by Article 3 of the Act of 8 May 2024 (Federal Law Gazette 2024 I No. 152)"),
    # Berlino, pagine del servizio
    "be_bc_kv": ("be_bc", "You have health insurance in Germany, either in the statutory health insurance system or a comparable private health insurance. Foreign health insurance is not sufficient."),
    "be_free_kv": ("be_free", "You have health insurance in Germany, either in the statutory health insurance system or a comparable private health insurance. Foreign health insurance is not sufficient."),
    "be_stud_kv": ("be_stud", "You have health insurance in Germany, either in the statutory health insurance system or a comparable private health insurance. Foreign health insurance is not sufficient."),
    "be_stud_mezzi": ("be_stud", "Sufficient funds to secure your livelihood, including adequate health insurance coverage, are required."),
    # Berlino, foglio informativo generale (LEA 4326a)
    "lea_gkv": ("lea_kv", "They need only provide proof of their relevant membership in the statutory health insurance."),
    "lea_adeguata": ("lea_kv", "The health insurance cover provided by such a health insurance policy is considered adequate if it corresponds in terms of type and scope to that of the statutory health insurance"),
    "lea_franchigia": ("lea_kv", "in principle require a higher deductible from the insured person in the event of sickness than €300 per annum", {"valore": 300}),
    "lea_franchigia_alta": ("lea_kv", "A higher deductible under Article 152 par. 1 of the German Insurance Supervision Act (Versicherungsaufsichtsgesetz – VAG) may be permitted following an assessment of the individual case."),
    "lea_estero": ("lea_kv", "Such insurance cover may also be provided by an insurer with its registered office abroad."),
    "lea_bafin": ("lea_kv", "Insurance cover must always be deemed to be adequate if the Federal Financial Supervisory Authority (BaFin) has confirmed to the insurance company that on the basis of the respective insurance agreement it fulfils the statutory requirements with regard to health insurance under Article 257 par. 2a SGB V and the health insurer certifies this."),
    "lea_continuita": ("lea_kv", "in the event of extensions of residence permits all persons who do not have statutory insurance must submit a confirmation from the health insurer that the insurance cover has existed continuously and has not been terminated in the meantime."),
    "lea_rifiuto": ("lea_kv", "The granting or extension of the residence document may then be refused."),
    # Berlino, foglio informativo per studenti (LEA 4310b)
    "leas_permesso": ("lea_stud", "A residence permit will not be granted unless proof of adequate health insurance has been submitted."),
    "leas_due": ("lea_stud", "Health insurance may be covered by the German statutory health insurance or by a private health insurance company."),
    "leas_257": ("lea_stud", "In the event that a private health insurance does not fulfil the conditions under § 257 Section 2 a SGB V, as a matter of principle, it is not regarded as adequate health insurance in the sense of § 2 Section 3 Section 1 of the Residence Act, also if, otherwise, the type and scope of the insurance coverage is equivalent to that of the statutory health insurance."),
    "leas_anno": ("lea_stud", "Private health insurance must cover a period of at least one year.", {"valore": 1}),
    "leas_eta": ("lea_stud", "Regardless of age, also when confirmation of enrolment is presented, proof of adequate insurance cover must be submitted."),
    "leas_viaggio": ("lea_stud", "Travel health insurance is only sufficient for short stays, for example, in the case of exchange students."),
    # Partner (parole del loro sito: servono solo al riquadro, oggi spento)
    "otto_pkv": ("ottonova", "Private health insurance"),
    "otto_expat": ("ottonova", "Expat tariff"),
}

# Frasi misurate (strumento dei volumi): Paese -> frasi
PAESI_DOMANDA = ["us", "gb", "de", "in"]
QUERY = ["health insurance germany", "german health insurance", "private health insurance germany", "public health insurance germany",
         "statutory health insurance germany", "public vs private health insurance germany", "expat health insurance germany",
         "health insurance for expats in germany", "health insurance germany for foreigners", "health insurance germany cost",
         "how much is health insurance in germany", "student health insurance germany", "health insurance for students in germany",
         "health insurance for international students in germany", "travel insurance germany", "travel insurance for germany visa",
         "travel health insurance germany", "incoming health insurance germany", "health insurance for germany visa", "health insurance germany visa",
         "germany visa insurance", "is travel insurance mandatory for germany",
         # frasi per tipo di visto: misurate per sapere se esistono (il 14/11/2026 nessuna ha un volume)
         "health insurance for blue card germany", "blue card germany health insurance", "opportunity card germany health insurance",
         "chancenkarte health insurance", "job seeker visa germany health insurance", "freelance visa germany health insurance",
         "health insurance for freelancers in germany", "family reunion visa germany health insurance", "health insurance for spouse visa germany",
         "german student visa health insurance", "health insurance for work visa germany", "health insurance for visitors to germany"]


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
            t = subprocess.run(["pdftotext", str(f), "-"], capture_output=True, text=True, timeout=180).stdout
            # le righe di piè di pagina dei fogli LEA spezzano le frasi a cavallo di due pagine: si tolgono
            return norm(re.sub(r"LEA \d+[a-z] – [^\n]*\n", " ", t))
    t = b.decode("utf-8", "replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
    return norm(html.unescape(re.sub(r"<[^>]+>", " ", t)))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def volume(q, paese):
    """Una frase, un Paese. La chiave è letta dalla shell dentro curl: non entra mai in Python."""
    url = "https://api.seodata.dev/v1/keyword?q=" + urllib.parse.quote(q) + "&country=" + paese
    r = subprocess.run(["bash", "-c", 'curl -s -m 60 -w "\\n%{http_code}" "$U" -H "Authorization: Bearer $(cat /root/.config/seodata/key)"'],
                       env={**os.environ, "U": url}, capture_output=True, text=True, timeout=90)
    corpo, _, codice = r.stdout.rpartition("\n")
    try:
        d = json.loads(corpo)
    except ValueError:
        d = {}
    if codice == "200" and "volume" in d:
        return {"volume": d.get("volume"), "cpc": d.get("cpc")}
    if codice == "404":
        return {"volume": None, "cpc": None}   # frase non nel database: nessun volume misurato
    raise SystemExit(f"strumento dei volumi: risposta {codice} per «{q}» ({paese}): domanda non aggiornata")


def nuova_domanda():
    out = {}
    for p in PAESI_DOMANDA:
        for q in QUERY:
            out[f"{p}|{q}"] = volume(q, p)
            time.sleep(0.2)
    return {"data": date.today().isoformat(), "metodo": "strumento dei volumi (api.seodata.dev /v1/keyword): volume medio mensile di Google Ads e costo per clic, per Paese; null = frase non nel database",
            "paesi": PAESI_DOMANDA, "query": out}


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
        time.sleep(2)
    letture = {}
    for k, v in LETTURE.items():
        fonte, fr = v[0], v[1]
        opz = v[2] if len(v) > 2 else {}
        cerca = (opz["sezione"] + " " + fr) if opz.get("sezione") else fr
        if cerca not in testi.get(fonte, ""):
            errori.append(f"{k}: frammento non trovato in {fonte}: {cerca[:90]}…")
        letture[k] = {"fonte": fonte, "frammento": fr, **opz}
    if errori:
        print("NON aggiornato:\n  " + "\n  ".join(errori))
        sys.exit(1)
    domanda = nuova_domanda() if "--domanda" in sys.argv else vecchio.get("domanda", {})
    if not domanda:
        domanda = nuova_domanda()
    for k in fonti:
        fonti[k]["sha256_testo"] = sha(testi[k].encode()) if testi[k] else None
    cont = {"url": {k: f["url"] for k, f in fonti.items()}, "letture": letture, "domanda": domanda}
    out = {"_nota": "Generato da raccolta/assicurazione_de.py: non modificare a mano. Le letture sono frammenti dei testi ufficiali, ricontrollati a ogni lancio.",
           "letto_il": oggi, "fonti": fonti, "letture": letture, "domanda": domanda}
    out["impronta"] = hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20]
    USCITA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Scritto {USCITA}: {len(fonti)} fonti, {len(letture)} letture, domanda del {domanda.get('data')}")


if __name__ == "__main__":
    main()
