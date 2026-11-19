"""Rilegge le fonti ufficiali della sezione "Teach English abroad: visa and salary rules by country" (dal 19/11/2026)
e scrive visaincome/dati/tefl.json.

Uso (dalla radice del repository):
    python3 visaincome/raccolta/tefl.py              # rilegge le fonti e scrive il JSON (domanda: quella già salvata)
    python3 visaincome/raccolta/tefl.py --domanda    # rimisura anche i volumi di ricerca (circa 3 minuti)

Fonti (lette il 19/11/2026 con richieste HTTP dirette, nessun browser; i file grezzi NON si salvano nel repository)
- Giappone: JET Program USA (jetprogramusa.org, il sito ufficiale del programma negli Stati Uniti, tenuto dall'Ambasciata del Giappone):
  requisiti, contratto e stipendio, posizioni, selezione. Il sito internazionale jetprogramme.org il 19/11/2026 era in manutenzione
  (pagina provvisoria); le pagine dei visti del Ministero degli Esteri giapponese e delle ambasciate rispondono 403: non aggirato.
- Spagna: Ministerio de Educación, Formación Profesional y Deportes, pagine NALCAP (auxiliares de conversación nordamericani).
- Corea del Sud: Korea Visa Portal (visa.go.kr, Ministero della Giustizia), schede E-2-1 ed E-2-2 in inglese. La scheda si apre con
  il modulo del sito (lingua + sigla del visto): lo script fa le stesse due richieste. epik.go.kr non risponde da qui (connessione
  chiusa o 403): nessuna cifra EPIK è pubblicata.
- Thailandia: Royal Thai Embassy, London, pagina "Non-Immigrant Visa (B) for employment as an academic staff/teacher in Thailand".
- Taiwan: Laws & Regulations Database of the Republic of China (law.moj.gov.tw), standard del Ministero del Lavoro per gli insegnanti
  stranieri dei centri di insegnamento privati (cram school), articoli 3, 5 e 5-1, in inglese (traduzione ufficiale) e in cinese (il testo
  che vale: la traduzione dice "meet one of the following qualifications", il cinese le chiede tutte e il certificato è in più).
- Cina: Ambasciata della Repubblica Popolare Cinese negli Stati Uniti, "Requirements and Procedures for Chinese Visa Application".
- LETTURE: ogni frammento è stato letto A MANO il 19/11/2026. A ogni lancio si controlla che sia ancora nella fonte: se ne manca
  uno il JSON NON si aggiorna (codice 1) finché qualcuno non rilegge.
- VALORI: le cifre (stipendi, ore, tariffe) non sono scritte a mano nelle pagine: si leggono dal frammento.
- DOMANDA: volumi medi mensili (Google Ads) dello strumento dei volumi, per Paese. La chiave sta fuori dal repository e viene
  letta solo dentro la shell di curl: non passa da Python, non viene stampata né scritta.
"""
import hashlib
import html
import http.cookiejar
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
USCITA = RADICE / "dati" / "tefl.json"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"}
JET = "https://jetprogramusa.org/"
NAL = "https://www.educacionfpydeportes.gob.es/eeuu/convocatorias-programas/convocatorias-eeuu/nalcap"
ED_JET = "JET Program USA (Embassy of Japan in the United States)"
ED_ES = "Ministerio de Educación, Formación Profesional y Deportes (Government of Spain)"
ED_KR = "Korea Visa Portal (Ministry of Justice, Republic of Korea)"
KVP = "https://www.visa.go.kr/openPage.do?MENU_ID=10102"

FONTI = {
    "jp_elig": {"paese": "japan", "titolo": "JET Program USA: Eligibility Criteria", "editore": ED_JET, "url": JET + "eligibility-criteria/"},
    "jp_contr": {"paese": "japan", "titolo": "JET Program USA: Contract, Salary & Benefits", "editore": ED_JET, "url": JET + "contract-information/"},
    "jp_pos": {"paese": "japan", "titolo": "JET Program USA: JET Program Positions", "editore": ED_JET, "url": JET + "positions/"},
    "jp_proc": {"paese": "japan", "titolo": "JET Program USA: Our Application & Departure Process", "editore": ED_JET, "url": JET + "application-departure/"},
    "es_nalcap": {"paese": "spain", "titolo": "North American Language and Culture Assistants Program (NALCAP): programme overview and eligibility", "editore": ED_ES, "url": NAL + ".html"},
    "es_visa": {"paese": "spain", "titolo": "NALCAP: applying for a visa", "editore": ED_ES, "url": NAL + "/applying-visa.html"},
    "es_apply": {"paese": "spain", "titolo": "NALCAP: applying to the program", "editore": ED_ES, "url": NAL + "/applying-program.html"},
    "kr_e21": {"paese": "south-korea", "titolo": "Korea Visa Portal: Foreign Language Instructor (General) (E-2-1)", "editore": ED_KR, "url": KVP, "kvp": "E-2-1"},
    "kr_e22": {"paese": "south-korea", "titolo": "Korea Visa Portal: Teaching Assistant (E-2-2)", "editore": ED_KR, "url": KVP, "kvp": "E-2-2"},
    "th_teach": {"paese": "thailand", "titolo": "Non-Immigrant Visa (B) for employment as an academic staff/teacher in Thailand", "editore": "Royal Thai Embassy, London",
                 "url": "https://london.thaiembassy.org/en/page/non-b-visa-for-employment-as-teachers"},
    "tw_cram": {"paese": "taiwan", "titolo": "Qualification and Criteria Standards for the Employment of Foreign Professionals as Teachers by Short-term Supplementary Learning Centers",
                "editore": "Laws & Regulations Database of the Republic of China (Taiwan), Ministry of Justice", "url": "https://law.moj.gov.tw/ENG/LawClass/LawAll.aspx?pcode=N0090054"},
    "tw_zh": {"paese": "taiwan", "titolo": "外國專業人才從事短期補習班教師工作資格及審查標準 (the same standards, Chinese text: the text that applies)",
              "editore": "Laws & Regulations Database of the Republic of China (Taiwan), Ministry of Justice", "url": "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=N0090054"},
    "cn_req": {"paese": "china", "titolo": "Requirements and Procedures for Chinese Visa Application (Updated September, 2025)",
               "editore": "Embassy of the People's Republic of China in the United States of America", "url": "https://us.china-embassy.gov.cn/eng/lsfw/zj/qz2021/202509/t20250920_11712385.htm"},
}
DOMINI_UFFICIALI = ("jetprogramusa.org", "educacionfpydeportes.gob.es", "visa.go.kr", "thaiembassy.org", "law.moj.gov.tw", "china-embassy.gov.cn")

# chiave -> (fonte, frammento | [pezzi di un elenco puntato], opzioni). "valori": le cifre scritte nel frammento, usate dalle pagine.
LETTURE = {
    # ------------------------------------------------------------ Giappone (JET Program, candidati dagli Stati Uniti)
    "jp_cittadino": ("jp_elig", "Be a citizen of the United States by the application deadline."),
    "jp_altri_paesi": ("jp_elig", "Please contact the Embassy of Japan in your home country for information."),
    "jp_laurea": ("jp_elig", "Hold at least a Bachelor's degree or obtain such qualifications by June 25th, 2027"),
    "jp_lingua": ("jp_elig", "Have excellent standard pronunciation, rhythm, intonation in the English language and possess excellent language ability that can be applied accurately and appropriately"),
    "jp_tefl": ("jp_elig", "Be strongly motivated to learn about the teaching of English as a foreign language. To that end, possessing teaching qualifications will be a benefit on your application, although it is not required."),
    "jp_penale": ("jp_elig", "When it is determined that an individual's criminal history renders them unsuitable for participation on the JET Program"),
    "jp_penale2": ("jp_elig", "Have finished any periods of legal probation and/or paid any fines by the application deadline if a jail term was suspended."),
    "jp_vissuto": ("jp_elig", "Not have lived in Japan for a six (6) or more years in total since 2017."),
    "jp_gia": ("jp_elig", "Have not participated on the JET Program since 2024 or have not participated on the JET program for more than five (5) years in total."),
    "jp_stipendio": ("jp_contr", "Salary before tax for each contract year is, as of April 2026: Year 1: ¥4,020,000 Year 2: ¥4,140,000 Year 3: ¥4,260,000 Year 4/5: ¥4,320,000",
                     {"valori": [4020000, 4140000, 4260000, 4320000], "al": "April 2026"}),
    "jp_stipendio_regola": ("jp_contr", "The JET participant's salary is determined by the number of years of participation on the JET Program."),
    "jp_trattenute": ("jp_contr", "In Japan, joining the national social (health) insurance, contributing to the pension fund program and paying employment insurance are mandatory. A part of these costs are borne by the participant and deducted from the monthly post-tax remuneration each month on payday."),
    "jp_ore": ("jp_contr", "Participants are expected to be at work approximately thirty-five hours a week, excluding lunch breaks."),
    "jp_durata": ("jp_contr", "The 2026 JET contract is for roughly 12 months and commences on the day after the designated arrival date.", {"valori": [12]}),
    "jp_rinnovo": ("jp_contr", "The contracting organization may reappoint the JET participant for an additional one-year contract, with a maximum of five years total."),
    "jp_ferie": ("jp_contr", "The amount of paid leave per year differs among contracting organizations, but all participants are guaranteed to have at least ten days."),
    "jp_altro_lavoro": ("jp_contr", "Participants are prohibited from taking on any work other than that of this Program for the duration of their appointment."),
    "jp_visto": ("jp_contr", "The JET Program Office will provide the necessary work visa for candidates who are selected to participate on the JET Program."),
    "jp_familiari": ("jp_contr", "Please note that only legal spouses as recognized by Japanese law and children under the age of 18 are eligible for a dependent's visa."),
    "jp_datore": ("jp_contr", "Contracting organizations (COs) are the entities which employ JETs (rather than the JET Program itself)."),
    "jp_condizioni": ("jp_contr", "The following is a general outline of the terms and conditions, though they may vary from one CO to another."),
    "jp_alt": ("jp_pos", "ALTs are engaged in language instruction and make up over 90% of all JET Program participants."),
    "jp_alt_dove": ("jp_pos", "They are mainly assigned to local boards of education or elementary, junior high or senior high schools"),
    "jp_domanda": ("jp_proc", "The JET Program application is open once a year between late September to mid-November."),
    "jp_colloqui": ("jp_proc", "Interviews are typically held in late January or early February."),
    "jp_esito": ("jp_proc", "Candidates typically receive notification of their results in late March to mid April."),
    # ------------------------------------------------------------ Spagna (NALCAP: auxiliares de conversación dagli Stati Uniti)
    "es_cosa": ("es_nalcap", "American college students and graduates - who are native-like speakers of English - partner with elementary and secondary schools in Spain to bolster language programs, as language assistants (TAs) under the supervision and guidance of teachers in Spain."),
    "es_periodo": ("es_nalcap", "Placements are offered across Spain, in practically every city and town in the country, running from November 1st to May 31st for most assignments."),
    "es_stipendio": ("es_nalcap", "Depending on the assigned region, NALCAP recipients receive a monthly stipend of 800 to 1000 euros and medical insurance from either the Ministry of Education of Spain or the regional governments of Spain.",
                     {"valori": [800, 1000]}),
    "es_ore": ("es_nalcap", "Hours of assistant teaching range from 14 to 16 hours per week also depending on the assignment awarded.", {"valori": [14, 16]}),
    "es_anno": ("es_nalcap", "NALCAP CONDITIONS – 2026-2027 SCHOOL YEAR"),
    "es_cittadino": ("es_nalcap", "Be a U.S. citizen and have a valid passport through November 1st, 2027"),
    "es_laurea": ("es_nalcap", "Have a conferred college degree or be currently enrolled as a 2nd year or higher college student."),
    "es_laurea2": ("es_nalcap", "Only college studies undertaken completely in English will be accepted."),
    "es_laurea_us": ("es_nalcap", "NALCAP applicants must have a college degree from an accredited university in the US or Canada."),
    "es_eta2": ("es_nalcap", "You must be at least 18 years old as of January 1, 2026 and not be 45 or over on January 1, 2027, to participate in the program."),
    "es_madrelingua": ("es_nalcap", "Be a native-like speaker of English."),
    "es_salute": ("es_nalcap", "Be in good physical and mental health."),
    "es_penale": ("es_nalcap", "Have a clean background check."),
    "es_eta": ("es_nalcap", "Be aged 18 - 45.", {"valori": [18, 45]}),
    "es_spagnolo": ("es_nalcap", "Participants in the program should have a basic level of Spanish to use in everyday life in Spain"),
    "es_canada": ("es_nalcap", "Canadian citizens: Please visit the NALCAP Canada website for specific information pertaining to Canadian applicants."),
    "es_visto_obbligo": ("es_visa", "You must apply for a visa to participate in the NALCAP program"),
    "es_visto_tipo": ("es_visa", "You will be applying for a Student/Study National Visa. This is the category of visa assigned for the NALCAP program."),
    "es_visto_dove": ("es_visa", "You must apply for a visa at your local Consulate of Spain in the US. You cannot apply for a visa once in Spain."),
    "es_visto_quando": ("es_visa", "Please be aware that you will not be able to submit your application for your visa under any circumstance until you have received your Placement Letter (Carta de Nombramiento)."),
    "es_visto_consolati": ("es_visa", "Visas are issued by the Consulates General of Spain in the U.S. under the jurisdiction of the MInistry of Foreign Affairs of Spain, not the Ministry of Education."),
    "es_precedenza": ("es_visa", "Please keep in mind that specific instructions from each consulate overrule any information provided by NALCAP."),
    "es_apostille": ("es_visa", "You may begin to gather your paperwork such as the background check - with its corresponding apostille and official translation - as soon as you have a PLAZA ACEPTADA status on the PROFEX portal."),
    "es_volo": ("es_visa", "We strongly suggest NOT buying your airline tickets to Spain until you have received the visa and it is in your custody."),
    "es_doc": ("es_apply", ["A copy of the main page of your valid U.S. passport", "An official college transcript or a copy of your diploma", "A signed statement of purpose",
                            "A letter of recommendation", "Health Statement and Statutory Declaration"]),
    "es_profex": ("es_apply", "PROFEX 2 is the new Ministry of Education of Spain's online portal used to apply for NALCAP."),
    # ------------------------------------------------------------ Corea del Sud (Korea Visa Portal)
    "kr_e21_nome": ("kr_e21", "Foreign Language Instructor (General)"),
    "kr_e21": ("kr_e21", "A person who meets the qualifications determined by the Minister of Justice, and plans to teach conversational language at a foreign language institute, affiliated- language research institute or educational institute of higher than elementary school, or language training institute affiliated with an enterprise or broadcasting company, or other equivalent organization."),
    "kr_e22_nome": ("kr_e22", "Teaching Assistant"),
    "kr_e22": ("kr_e22", "A person who meets the qualifications determined by the Minister of Justice of ROK and has signed an employment contract with the Minister of Education (or superintendent of a school district) to teach foreign language at an elementary, middle, or high school as an assistant teacher"),
    "kr_rifiuto": ("kr_e21", "Even if the foreigner has the valid visa or is subject to visa-free entry, he/she may be denied entry to the Republic of Korea if he's found inadmissible by an immigration officer at the port of entry."),
    # ------------------------------------------------------------ Thailandia (ambasciata di Londra)
    "th_cosa": ("th_teach", "A Non-Immigrant Visa (B) or Non-B Visa allows foreign nationals to work in academia and the formal education system in Thailand."),
    "th_chi": ("th_teach", ["are employed by a Thai school, international school, or university,", "hold valid ordinary passports,",
                            "hold citizenship or valid proof of immigration status in the UK, Ireland, or British Overseas Territories, and",
                            "currently reside in the UK, Ireland, or British Overseas Territories."]),
    "th_validita": ("th_teach", "Non-B Visa is valid for a single entry within 90 days from the date of issue.", {"valori": [90]}),
    "th_soggiorno": ("th_teach", "Visa holders will be permitted to stay in Thailand for up to 90 days from the date of entry.", {"valori": [90]}),
    "th_tariffa": ("th_teach", "Fee: £60", {"valori": [60]}),
    "th_estensione": ("th_teach", "If Non-Immigrant visa holders wish to stay for longer than the permitted period or enter Thailand several times, they can request an extension of stay and re-entry permit by directly contacting the Immigration Bureau after arriving in Thailand."),
    "th_banca": ("th_teach", "Recent bank statements for the last 3 months issued in the UK, Ireland, or British Overseas Territories, with the applicant's name, address, and a minimum closing balance of £700", {"valori": [700, 3]}),
    "th_lettera": ("th_teach", "An official letter from the Ministry of Education, university, or international school"),
    "th_penale": ("th_teach", "Certificate of criminal record clearance issued within the last 6 months", {"valori": [6]}),
    "th_tempi": ("th_teach", "The current processing time is approximately 15 working days", {"valori": [15]}),
    "th_anticipo": ("th_teach", "Applicants are recommended to submit their visa applications at least 6-8 weeks before their departure."),
    "th_altri": ("th_teach", "However, they may receive the request for additional documents as deemed necessary."),
    # ------------------------------------------------------------ Taiwan (standard del Ministero del Lavoro, traduzione ufficiale)
    "tw_lavoro": ("tw_cram", "2. Full-time foreign language teaching work."),
    "tw_datore": ("tw_cram", "Employers hiring foreign professionals referred to in Subparagraph 2 or Subparagraph 3, Article 3 shall be short-term cram schools registered in accordance with the Supplementary Education Act."),
    "tw_req": ("tw_cram", "When employed to engage in work prescribed in Subparagraph 2, Article 3, the teaching-related weekly working hours of foreign professionals shall be no less than 14 hours and meet one of the following qualifications: 1. Have attained the age of majority. 2. Graduated from colleges or above. 3. The language to be taught by the foreign teacher is the official language used in the country specified in the passport of the teacher.",
               {"valori": [14]}),
    "tw_cert": ("tw_cram", "If the foreign nationals mentioned in the preceding paragraph have not obtained a bachelor's degree, they are required to have a qualification certificate for language teaching."),
    "tw_sei": ("tw_cram", "their weekly working hours in teaching-related work for each employers shall not be less than 6 hours.", {"valori": [6]}),
    "tw_max": ("tw_cram", "their total weekly working hours in teaching-related work shall not exceed 32 hours.", {"valori": [32]}),
    "tw_tre_anni": ("tw_cram", "none of the following circumstances must not have occurred in the three years prior to the application date: 1. He or she has engaged in work without obtaining an employment permit;"),
    # testo cinese dell'art. 5-1 (quello che vale): "且應具備下列資格" = tutte le qualifiche; "另應具有" = il certificato è in più
    "tw_zh_req": ("tw_zh", "每週從事教學相關工作時數不得少於十四小時，且應具備下列資格： 一、成年。 二、大專以上學校畢業。 三、教授之語文課程為該外籍教師護照國籍之官方語言。"),
    "tw_zh_cert": ("tw_zh", "前項外國人未取得學士學位者，另應具有語文師資訓練合格證書。"),
    "tw_zh_max": ("tw_zh", "第一項及前項外國人每週從事教學相關工作總時數，不得超過三十二小時。"),
    "tw_data": ("tw_cram", "Amended Date： 2022-10-27"),
    # ------------------------------------------------------------ Cina (ambasciata negli Stati Uniti)
    "cn_z": ("cn_req", "Issued to those who intend to work in China", {"contesto": "Z Issued to those who intend to work in China Notice for the Work Permit for Foreigners"}),
    "cn_z_doc": ("cn_req", "Notice for the Work Permit for Foreigners", {"contesto": "Z Issued to those who intend to work in China Notice for the Work Permit for Foreigners"}),
    "cn_cova": ("cn_req", "Visa applicants need to log on to the New COVA System (click to redirect) to fill in the forms and upload materials for preliminary review."),
    "cn_passaporto": ("cn_req", "Passport remaining validity must be more than 6 months with at least 2 blank visa pages", {"valori": [6, 2]}),
    "cn_tempi": ("cn_req", "Regular service: 4 business days Express service: 3 business days (urgent situation)", {"valori": [4, 3]}),
    "cn_tempi_nota": ("cn_req", "The above processing time is average and for reference only and is calculated from the date of passport submission."),
    "cn_caso": ("cn_req", "Since visa applications are processed on a case-by-case basis, please refer to the Chinese Embassy and Consulates-General in the United States for specifics."),
}

# ---------------------------------------------------------------- domanda (strumento dei volumi)
PAESI_DOMANDA = ["us", "gb"]
QUERY = ["teach english abroad", "teaching english abroad", "teach english abroad requirements", "teach english abroad salary", "teach english abroad without a degree",
         "teach english abroad programs", "how to teach english abroad", "best countries to teach english",
         "teach english in korea", "teach english in south korea", "teaching english in korea", "teaching english in korea salary", "epik", "epik korea", "epik salary",
         "e2 visa korea", "e-2 visa korea", "teach english in korea requirements",
         "teach english in japan", "teaching english in japan", "teaching english in japan salary", "jet program", "jet programme", "jet program salary",
         "jet program requirements", "teach english in japan requirements", "english teacher in japan salary",
         "teach english in china", "teaching english in china", "teach english in china requirements", "z visa china", "china work visa", "teach english in china salary",
         "teach english in vietnam", "teaching english in vietnam", "teach english in vietnam requirements", "vietnam work permit",
         "teach english in thailand", "teaching english in thailand", "teach english in thailand requirements", "teaching english in thailand salary", "non b visa thailand",
         "teach english in spain", "teaching english in spain", "auxiliares de conversacion", "auxiliar de conversacion", "nalcap", "nalcap spain", "language assistant spain",
         "auxiliares de conversacion salary", "teach english in taiwan", "teaching english in taiwan", "teach english in taiwan requirements",
         "teach english in dubai", "teaching english in dubai", "teach english in uae", "teach english in czech republic", "teach english in prague",
         "teach english in colombia", "teach english in mexico", "teach english in france", "tapif", "tapif salary", "teach english in hong kong", "net scheme hong kong",
         "teach english in italy", "teach english in germany", "tefl certification", "tefl certificate", "tefl", "is tefl required to teach english abroad",
         "teach english abroad visa", "english teacher visa", "teach english in europe", "teach english in saudi arabia", "teach english in costa rica"]


def get(u, tentativi=5, dati=None, apri=None):
    apri = apri or urllib.request.urlopen
    for i in range(tentativi):
        try:
            r = apri(urllib.request.Request(u, headers=UA, data=dati), timeout=120)
            return r.status, r.read()
        except Exception as e:  # noqa: BLE001
            c = getattr(e, "code", 0)
            if c in (403, 404, 410):
                return c, b""
            time.sleep(5 + 10 * i)
    return 0, b""


def get_kvp(sigla):
    """Korea Visa Portal: come fa il modulo del sito, prima la lingua (inglese), poi la scheda del visto. Nessun accesso riservato."""
    for i in range(4):
        jar = http.cookiejar.CookieJar()
        op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
        st, _ = get("https://www.visa.go.kr/cmm/openLang.do", tentativi=3, dati=b"LANG=EN&LOW_LANG=en&MENU_ID=10102", apri=op.open)
        if st == 200:
            st, b = get("https://www.visa.go.kr/openPage.do?MENU_ID=1010201", tentativi=3,
                        dati=f"IN_SOJ_QUAL_GRP={sigla}&TRAN_TYPE=ComSubmit&SE_FLAG_YN=&LANG_TYPE=EN".encode(), apri=op.open)
            if st == 200 and b:
                return st, b
        time.sleep(10 + 10 * i)
    return st, b""


def norm(t):
    t = (t or "").replace("​", "").replace("\xa0", " ").replace("‑", "-").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    t = re.sub(r"\s+", " ", t).strip()
    return re.sub(r" ([.,;:])", r"\1", t)


def testo(b):
    t = b.decode("utf-8", "replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", " ", t, flags=re.S | re.I)
    t = norm(html.unescape(re.sub(r"<[^>]+>", " ", t)))
    return t.replace("( ", "(").replace(" )", ")")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def leggi_fonti():
    oggi = date.today().isoformat()
    fonti, testi, errori = {}, {}, []
    for k, f in FONTI.items():
        st, b = get_kvp(f["kvp"]) if f.get("kvp") else get(f["url"])
        fonti[k] = {"paese": f["paese"], "titolo": f["titolo"], "editore": f["editore"], "url": f["url"], "http": st, "letto_il": oggi, "byte": len(b)}
        if f.get("kvp"):
            fonti[k]["scheda"] = f["kvp"]
        testi[k] = testo(b) if st == 200 and b else ""
        fonti[k]["sha256_testo"] = sha(testi[k].encode()) if testi[k] else None
        if st != 200:
            errori.append(f"{k}: HTTP {st} ({f['url']})")
        time.sleep(1.5)
    return fonti, testi, errori


def numeri(fr):
    """Numeri scritti nel frammento: '¥4,020,000' -> 4020000, '800 to 1000 euros' -> 800, 1000, '6-8 weeks' -> 6, 8."""
    return [int(x.replace(",", "")) for x in re.findall(r"\d{1,3}(?:,\d{3})+|\d+", fr)]


def volume(q, paese):
    """Una frase, un Paese. La chiave è letta dalla shell dentro curl: non entra mai in Python."""
    url = "https://api.seodata.dev/v1/keyword?q=" + urllib.parse.quote(q) + "&country=" + paese
    for i in range(4):
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
        time.sleep(20 * (i + 1))
    raise SystemExit(f"strumento dei volumi: risposta {codice} per «{q}» ({paese}): domanda non aggiornata")


def nuova_domanda():
    out = {}
    for p in PAESI_DOMANDA:
        for q in QUERY:
            out[f"{p}|{q}"] = volume(q, p)
            time.sleep(0.3)
    return {"data": date.today().isoformat(), "metodo": "strumento dei volumi (api.seodata.dev /v1/keyword): volume medio mensile di Google Ads e costo per clic, per Paese; null = frase non nel database",
            "paesi": PAESI_DOMANDA, "query": out}


def main():
    vecchio = json.loads(USCITA.read_text(encoding="utf-8")) if USCITA.exists() else {}
    fonti, testi, errori = leggi_fonti()
    for k, f in fonti.items():
        host = urllib.parse.urlsplit(f["url"]).netloc
        if not f["url"].startswith("https://") or not host.endswith(DOMINI_UFFICIALI):
            errori.append(f"{k}: fonte su un dominio non previsto ({host})")
    letture = {}
    for k, v in LETTURE.items():
        fonte, fr = v[0], v[1]
        opz = dict(v[2]) if len(v) > 2 else {}
        if isinstance(fr, list):   # elenco puntato della fonte: i pezzi, uno dopo l'altro, devono dare il testo della fonte
            opz["elenco"] = fr
            fr = " ".join(fr)
        if fr not in testi.get(fonte, ""):
            errori.append(f"{k}: frammento non trovato in {fonte}: {fr[:90]}…")
        if opz.get("contesto") and opz["contesto"] not in testi.get(fonte, ""):
            errori.append(f"{k}: contesto non trovato in {fonte}: {opz['contesto'][:90]}…")
        for n in opz.get("valori", []):
            if n not in numeri(fr):
                errori.append(f"{k}: il valore {n} non è scritto nel frammento")
        letture[k] = {"fonte": fonte, "frammento": fr, **opz}
    if errori:
        print("NON aggiornato:\n  " + "\n  ".join(errori))
        sys.exit(1)
    domanda = nuova_domanda() if "--domanda" in sys.argv else vecchio.get("domanda", {})
    if not domanda:
        domanda = nuova_domanda()
    cont = {"url": {k: f["url"] for k, f in fonti.items()}, "letture": letture, "domanda": domanda}
    out = {"_nota": "Generato da raccolta/tefl.py: non modificare a mano. Le letture sono frammenti dei testi ufficiali, ricontrollati a ogni lancio; le cifre si leggono dai frammenti.",
           "letto_il": date.today().isoformat(), "fonti": fonti, "letture": letture, "domanda": domanda}
    out["impronta"] = hashlib.sha256(json.dumps(cont, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20]
    USCITA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Scritto {USCITA}: {len(fonti)} fonti, {len(letture)} letture, domanda del {domanda.get('data')}")


if __name__ == "__main__":
    main()
