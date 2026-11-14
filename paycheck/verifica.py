"""Controlli di US Paycheck Calculator. Uso (dalla radice del repository):
    python3 paycheck/verifica.py            # dati, calcoli e pagine
    python3 paycheck/verifica.py --browser  # in più: Playwright a 375 e 1280 px (richieste esterne bloccate)

I controlli NON usano motore.py né regole.json come verità:
- le tabelle federali e le aliquote attese sono trascritte a mano qui sotto dalle fonti (ATTESO_*);
- le tabelle della California sono rilette dal PDF con un'altra estrazione (pdftotext -raw) e un altro lettore;
- la busta paga di riferimento è calcolata con frazioni esatte, riga per riga come nei fogli di lavoro ufficiali;
- il JS provato è quello pubblicato (sito/assets/app.*.js) con i dati scritti nella pagina (dati-regole).
"""
import hashlib
import json
import random
import re
import subprocess
import sys
from fractions import Fraction as Fr
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent
SITO = RADICE / "sito"
DATI = RADICE / "dati"
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402

URL_SITO = "https://us-paycheck-calculator.netlify.app"
ERR, AVV = [], []
CASI_PER_STATO = 600


def err(m):
    ERR.append(m)


def ok(cond, m):
    if not cond:
        err(m)
    return cond


# ================================================================ valori attesi, trascritti a mano dalle fonti
# IRS Pub. 15-T (2026), pagina 12: (A at least, C tentative amount, D percentage). B è l'A della riga dopo.
ATTESO_FED = {
    "std": {
        "mfj": [(0, 0, 0), (19300, 0, 10), (44100, 2480, 12), (120100, 11600, 22), (230700, 35932, 24), (422850, 82048, 32), (531750, 116896, 35), (788000, "206583.50", 37)],
        "single": [(0, 0, 0), (7500, 0, 10), (19900, 1240, 12), (57900, 5800, 22), (113200, 17966, 24), (209275, 41024, 32), (263725, 58448, 35), (648100, "192979.25", 37)],
        "hoh": [(0, 0, 0), (15550, 0, 10), (33250, 1770, 12), (83000, 7740, 22), (121250, 16155, 24), (217300, 39207, 32), (271750, 56631, 35), (656150, 191171, 37)],
    },
    "step2": {
        "mfj": [(0, 0, 0), (16100, 0, 10), (28500, 1240, 12), (66500, 5800, 22), (121800, 17966, 24), (217875, 41024, 32), (272325, 58448, 35), (400450, "103291.75", 37)],
        "single": [(0, 0, 0), (8050, 0, 10), (14250, 620, 12), (33250, 2900, 22), (60900, 8983, 24), (108938, 20512, 32), (136163, 29224, 35), (328350, "96489.63", 37)],
        "hoh": [(0, 0, 0), (12075, 0, 10), (20925, 885, 12), (45800, 3870, 22), (64925, "8077.50", 24), (112950, "19603.50", 32), (140175, "28315.50", 35), (332375, "95585.50", 37)],
    },
}
ATTESO_1G = {"mfj": 12900, "altro": 8600}
PERIODI = {"weekly": 52, "biweekly": 26, "semimonthly": 24, "monthly": 12}
# IRS Pub. 15 (2026)
SS, SS_BASE, MED, ADDL, ADDL_SOGLIA = Fr("0.062"), 184500, Fr("0.0145"), Fr("0.009"), 200000
FUTA_LORDA, FUTA_BASE, FUTA_CREDITO, FUTA_NETTA = Fr("0.06"), 7000, Fr("0.054"), Fr("0.006")
FUTA_RIDUZIONE = {"CA": Fr("0.015")}       # Department of Labor, foglio finale 2026 (10/11/2026)
# Disoccupazione statale, datori nuovi: aliquota, base imponibile (agenzie statali, 2026)
SUTA = {"TX": (Fr("0.027"), 9000), "FL": (Fr("0.027"), 7000), "CA": (Fr("0.034"), 7000), "IL": (Fr("0.0335"), 14250), "NC": (Fr("0.01"), 34200)}
SUTA_ALTRO = {"TX": {"min": 0.0032, "max": 0.0632}, "CA": {"min": 0.015, "max": 0.062, "ett": 0.001, "ett_base": 7000}, "IL": {"fondo": 0.0055}, "NC": {"min": 0.0006, "max": 0.0576}, "FL": {}}
CA_ETT, CA_SDI, CA_SDI_2027 = Fr("0.001"), Fr("0.013"), 0.014
IL_ALIQUOTA, IL_RIGA1, IL_RIGA2 = Fr("0.0495"), 2925, 1000
NC_ALIQUOTA, NC_IMPOSTA = Fr("0.0409"), 0.0399
# NC-30 (2026), pagine 17-18: quota della deduzione standard (single, head of household) e importo per esenzione
NC = {"weekly": ("245.19", "367.79", "48.08"), "biweekly": ("490.38", "735.58", "96.15"), "semimonthly": ("531.25", "796.88", "104.17"), "monthly": ("1062.50", "1593.75", "208.33")}
# California Method B 2026, tabelle 1-4 (colonne: single, married 0-1, married 2+, head of household)
CA_ESENZIONE = {"weekly": (363, 363, 727, 727), "biweekly": (727, 727, 1454, 1454), "semimonthly": (787, 787, 1575, 1575), "monthly": (1575, 1575, 3149, 3149)}
CA_DEDUZIONE = {"weekly": (110, 110, 219, 219), "biweekly": (219, 219, 439, 439), "semimonthly": (238, 238, 476, 476), "monthly": (476, 476, 951, 951)}
CA_STIMATE = {"weekly": (19, 38, 58, 77, 96, 115, 135, 154, 173, 192), "biweekly": (38, 77, 115, 154, 192, 231, 269, 308, 346, 385),
              "semimonthly": (42, 83, 125, 167, 208, 250, 292, 333, 375, 417), "monthly": (83, 167, 250, 333, 417, 500, 583, 667, 750, 833)}
CA_CREDITO = {"weekly": ("0", "3.24", "6.47", "9.71", "12.95", "16.18", "19.42", "22.66", "25.89", "29.13", "32.37"),
              "biweekly": ("0", "6.47", "12.95", "19.42", "25.89", "32.37", "38.84", "45.31", "51.78", "58.26", "64.73"),
              "semimonthly": ("0", "7.01", "14.03", "21.04", "28.05", "35.06", "42.08", "49.09", "56.10", "63.11", "70.13"),
              "monthly": ("0", "14.03", "28.05", "42.08", "56.10", "70.13", "84.15", "98.18", "112.20", "126.23", "140.25")}
CA_COL = {"single": 0, "married01": 1, "married2": 2, "hoh": 3}
NOMI = {"TX": ("Texas", "texas"), "FL": ("Florida", "florida"), "CA": ("California", "california"), "IL": ("Illinois", "illinois"), "NC": ("North Carolina", "north-carolina")}
STIPENDI = [30000, 50000, 75000, 100000, 150000]
PREDEFINITI = {"CA": {"ca_fs": "single", "ca_reg": 0, "ca_est": 0}, "IL": {"il1": 1, "il2": 0}, "NC": {"nc_fs": "single", "nc_all": 0}, "TX": {}, "FL": {}}
# nomi di modelli e di aziende di IA che non devono comparire nel sito (scritti a pezzi per non comparire nemmeno qui)
MODELLI_VIETATI = re.compile(r"\b(" + "|".join(a + b for a, b in [("cla", "ude"), ("chat", "gpt"), ("gpt", r"-?\d"), ("open", "ai"), ("anth", "ropic"), ("gem", "ini"), ("lla", "ma"), ("copi", "lot")]) + r")\b", re.I)
CHIAVE = "sd_" + "live"   # prefisso delle chiavi seodata: non deve comparire in nessun file


def arrotonda(x, passo=Fr(1, 100)):
    """Al più vicino multiplo di `passo`, con la metà esatta verso l'alto (x >= 0). Risultato in centesimi interi."""
    n = (x / passo + Fr(1, 2)).__floor__()
    return int(n * passo * 100)


def cent(x):
    return int(Fr(str(x)) * 100)


# ================================================================ California: seconda lettura del PDF (pdftotext -raw)
def california_raw():
    testo = subprocess.run(["pdftotext", "-raw", str(DATI / "grezzi" / "ca_26methb.pdf"), "-"], capture_output=True, check=True).stdout.decode("utf-8")
    righe = testo.split("\n")
    periodo_di = {"Weekly Payroll Period": "weekly", "Bi-weekly Payroll Period": "biweekly", "Semi-monthly Payroll Period": "semimonthly", "Monthly Payroll Period": "monthly",
                  "Annual Payroll Period": None, "Quarterly Payroll Period": None, "Semi-annual Payroll Period": None, "Daily / Miscellaneous Payroll Period": None}
    tab, periodo, stato, num = {}, "?", None, None
    for i, r in enumerate(righe):
        r = r.strip()
        if r in periodo_di and i + 1 < len(righe) and righe[i + 1].strip() == "Tax Rate Tables":
            periodo = periodo_di[r]
        m = re.match(r"Method B - Table (\d+): (Single|Married|Unmarried)", r)
        if m:
            num = int(m.group(1))
            stato = {"Single": "single", "Married": "married", "Unmarried": "hoh"}[m.group(2)] if num >= 5 else None
            if stato and periodo:
                tab.setdefault(periodo, {})[stato] = []
            continue
        if stato and periodo and periodo != "?":
            m = re.fullmatch(r"\$([\d,]+) \$([\d,]+) (\d+\.\d+)% \$([\d,]+) \$([\d,.]+)", r)
            if m:
                da, fino, p, oltre, piu = (x.replace(",", "") for x in m.groups())
                tab[periodo][stato].append((int(da), int(fino), Fr(p) / 100, Fr(piu)))
                ok(da == oltre, f"California {periodo}/{stato}: «over» {da} diverso da «of the amount over» {oltre}")
            m = re.fullmatch(r"N/A (\d+\.\d+)% \$([\d,]+) \$([\d,.]+)", r)
            if m:
                tab[periodo][stato].append((int(m.group(2).replace(",", "")), None, Fr(m.group(1)) / 100, Fr(m.group(3).replace(",", ""))))
    ok(sorted(tab) == sorted(PERIODI), f"California: periodi letti {sorted(tab)}")
    for per in PERIODI:
        for st in ("single", "married", "hoh"):
            v = tab.get(per, {}).get(st, [])
            if not ok(len(v) == 10, f"California {per}/{st}: {len(v)} righe invece di 10"):
                continue
            for a, b in zip(v, v[1:]):
                ok(a[1] == b[0], f"California {per}/{st}: scaglioni non contigui a {a[1]}")
                ok(abs(a[3] + (b[0] - a[0]) * a[2] - b[3]) <= Fr(3, 100), f"California {per}/{st}: «plus» {b[3]} incoerente")
    return tab


# ================================================================ calcolo di riferimento (frazioni esatte)
def rif_federale(i):
    P = PERIODI[i["periodo"]]
    lordo = Fr(i["lordo"], 100)
    l1c = lordo * P
    l1e = l1c + Fr(i.get("a4", 0), 100)
    l1g = 0 if i.get("step2") else (ATTESO_1G["mfj"] if i["fs"] == "mfj" else ATTESO_1G["altro"])
    l1h = Fr(i.get("b4", 0), 100) + l1g
    l1i = max(Fr(0), l1e - l1h)
    t = ATTESO_FED["step2" if i.get("step2") else "std"][i["fs"]]
    riga = [x for n, x in enumerate(t) if l1i >= x[0] and (n == len(t) - 1 or l1i < t[n + 1][0])]
    assert len(riga) == 1
    a, c, d = riga[0]
    l2g = Fr(str(c)) + (l1i - a) * Fr(d, 100)
    l2h = arrotonda(l2g / P)                                   # riga 2h, al centesimo (importo in dollari del foglio)
    l3b = arrotonda(Fr(i.get("step3", 0), 100) / P)            # riga 3b, al centesimo
    l3c = max(0, l2h - l3b)                                    # riga 3c
    return l3c + i.get("c4", 0)                                # riga 4b


def rif_statale(i, CA):
    lordo, per = Fr(i["lordo"], 100), i["periodo"]
    if i["stato"] in ("TX", "FL"):
        return 0
    if i["stato"] == "IL":
        esenti = Fr(arrotonda(Fr(i.get("il1", 0) * IL_RIGA1 + i.get("il2", 0) * IL_RIGA2) / PERIODI[per]), 100)   # l'esempio ufficiale arrotonda qui (150,96)
        return arrotonda(max(Fr(0), lordo - esenti) * IL_ALIQUOTA)
    if i["stato"] == "NC":
        ded_s, ded_h, es = NC[per]
        netto = max(Fr(0), lordo - Fr(ded_h if i.get("nc_fs") == "hoh" else ded_s) - i.get("nc_all", 0) * Fr(es))
        return arrotonda(netto * NC_ALIQUOTA, Fr(1))
    fs, reg, est = i.get("ca_fs", "single"), i.get("ca_reg", 0), i.get("ca_est", 0)
    col = CA_COL[("married2" if reg >= 2 else "married01") if fs == "married" else fs]
    if lordo <= CA_ESENZIONE[per][col]:
        return 0
    stimate = 0 if est == 0 else (CA_STIMATE[per][est - 1] if est <= 10 else est * CA_STIMATE[per][0])
    imponibile = max(Fr(0), lordo - stimate - CA_DEDUZIONE[per][col])
    riga = CA[per][fs][0]
    for x in CA[per][fs]:
        if imponibile > x[0]:
            riga = x
    calcolata = riga[3] + Fr(arrotonda((imponibile - riga[0]) * riga[2]), 100)   # l'esempio ufficiale arrotonda il prodotto (5,96)
    credito = Fr(CA_CREDITO[per][reg]) if reg <= 10 else reg * Fr(CA_CREDITO[per][1])
    return arrotonda(max(Fr(0), calcolata - credito))


def rif_busta(i, CA):
    lordo, ytd = Fr(i["lordo"], 100), Fr(i.get("ytd", 0), 100)
    o = {"fed": rif_federale(i), "stato": rif_statale(i, CA)}
    o["ss"] = arrotonda(max(Fr(0), min(lordo, SS_BASE - ytd)) * SS)
    o["medicare"] = arrotonda(lordo * MED)
    o["addl"] = arrotonda((max(Fr(0), ytd + lordo - ADDL_SOGLIA) - max(Fr(0), ytd - ADDL_SOGLIA)) * ADDL)
    o["sdi"] = arrotonda(lordo * CA_SDI) if i["stato"] == "CA" else 0
    o["netto"] = i["lordo"] - sum(o.values())
    return o


def rif_datore(stato, lordo_c, ytd_c=0, aliquota=None):
    lordo, ytd = Fr(lordo_c, 100), Fr(ytd_c, 100)
    al, base = SUTA[stato]
    if aliquota is not None:
        al = Fr(aliquota, 100000)
    def fino(b):
        return max(Fr(0), min(lordo, b - ytd))
    o = {"ss": arrotonda(fino(SS_BASE) * SS), "medicare": arrotonda(lordo * MED),
         "futa": arrotonda(fino(FUTA_BASE) * (FUTA_NETTA + FUTA_RIDUZIONE.get(stato, 0))), "suta": arrotonda(fino(base) * al),
         "ett": arrotonda(fino(7000) * CA_ETT) if stato == "CA" else 0}
    o["totale"] = sum(o.values())
    return o


# ================================================================ casi
def caso(stato, lordo, periodo="biweekly", **extra):
    i = {"stato": stato, "periodo": periodo, "lordo": lordo, "fs": "single", "step2": False, "ytd": 0, "step3": 0, "a4": 0, "b4": 0, "c4": 0}
    i.update(PREDEFINITI[stato])
    i.update(extra)
    return i


# Dieci casi calcolati a mano (i conti sono scritti accanto). Importi in centesimi.
CASI_A_MANO = [
    # 1. TX, 2.000 ogni due settimane, single: 52.000 − 8.600 = 43.400; 1.240 + 12 % × 23.500 = 4.060; ÷ 26 = 156,15. SS 124,00; Medicare 29,00.
    (caso("TX", 200000), {"fed": 15615, "ss": 12400, "medicare": 2900, "addl": 0, "stato": 0, "sdi": 0, "netto": 169085}),
    # 2. FL, 1.000 a settimana, sposati: 52.000 − 12.900 = 39.100; 10 % × 19.800 = 1.980; ÷ 52 = 38,0769 → 38,08. SS 62,00; Medicare 14,50.
    (caso("FL", 100000, "weekly", fs="mfj"), {"fed": 3808, "ss": 6200, "medicare": 1450, "addl": 0, "stato": 0, "sdi": 0, "netto": 88542}),
    # 3. TX, 10.000 al mese, capofamiglia, casella Step 2: 120.000 (nessuna sottrazione); 19.603,50 + 32 % × 7.050 = 21.859,50; ÷ 12 = 1.821,625 → 1.821,63.
    (caso("TX", 1000000, "monthly", fs="hoh", step2=True), {"fed": 182163, "ss": 62000, "medicare": 14500, "addl": 0, "stato": 0, "sdi": 0, "netto": 741337}),
    # 4. FL, 3.000 due volte al mese, sposati, Step 3 = 4.000: 72.000 − 12.900 = 59.100; 2.480 + 12 % × 15.000 = 4.280; ÷ 24 = 178,33 (riga 2h); 4.000 ÷ 24 = 166,67 (riga 3b); 178,33 − 166,67 = 11,66 (riga 3c).
    (caso("FL", 300000, "semimonthly", fs="mfj", step3=400000), {"fed": 1166, "ss": 18600, "medicare": 4350, "addl": 0, "stato": 0, "sdi": 0, "netto": 275884}),
    # 5. TX, 8.000 ogni due settimane, single, già pagati 180.000: SS solo su 4.500 = 279,00; Medicare 116,00; 208.000 − 8.600 = 199.400; 17.966 + 24 % × 86.200 = 38.654; ÷ 26 = 1.486,69.
    (caso("TX", 800000, ytd=18000000), {"fed": 148669, "ss": 27900, "medicare": 11600, "addl": 0, "stato": 0, "sdi": 0, "netto": 611831}),
    # 6. FL, 20.000 al mese, single, già pagati 190.000: SS 0; Medicare 290,00; Additional 0,9 % × 10.000 = 90,00; 240.000 − 8.600 = 231.400; 41.024 + 32 % × 22.125 = 48.104; ÷ 12 = 4.008,67.
    (caso("FL", 2000000, "monthly", ytd=19000000), {"fed": 400867, "ss": 0, "medicare": 29000, "addl": 9000, "stato": 0, "sdi": 0, "netto": 1561133}),
    # 7. CA, 3.000 ogni due settimane, single, 1 esenzione: fed 78.000 − 8.600 = 69.400; 5.800 + 22 % × 11.500 = 8.330; ÷ 26 = 320,38. CA: 3.000 − 219 = 2.781; 84,16 + 8,8 % × 567 (49,90) = 134,06; − 6,47 = 127,59. SDI 39,00.
    (caso("CA", 300000, ca_reg=1), {"fed": 32038, "ss": 18600, "medicare": 4350, "addl": 0, "stato": 12759, "sdi": 3900, "netto": 228353}),
    # 8. IL, 1.200 a settimana, 1 esenzione riga 1: fed 62.400 − 8.600 = 53.800; 1.240 + 12 % × 33.900 = 5.308; ÷ 52 = 102,08. IL: 2.925 ÷ 52 = 56,25; 1.143,75 × 4,95 % = 56,62.
    (caso("IL", 120000, "weekly"), {"fed": 10208, "ss": 7440, "medicare": 1740, "addl": 0, "stato": 5662, "sdi": 0, "netto": 94950}),
    # 9. NC, 5.000 al mese, capofamiglia (federale e NC), 1 esenzione: fed 60.000 − 8.600 = 51.400; 1.770 + 12 % × 18.150 = 3.948; ÷ 12 = 329,00. NC: 5.000 − 1.593,75 − 208,33 = 3.197,92; × 4,09 % = 130,79 → 131.
    (caso("NC", 500000, "monthly", fs="hoh", nc_fs="hoh", nc_all=1), {"fed": 32900, "ss": 31000, "medicare": 7250, "addl": 0, "stato": 13100, "sdi": 0, "netto": 415750}),
    # 10. CA, 6.000 al mese, sposati (federale MFJ; CA married, 2 esenzioni): fed 59.100 → 4.280; ÷ 12 = 356,67. CA: 6.000 − 951 = 5.049; 75,95 + 4,4 % × 673 (29,61) = 105,56; − 28,05 = 77,51. SDI 78,00.
    (caso("CA", 600000, "monthly", fs="mfj", ca_fs="married", ca_reg=2), {"fed": 35667, "ss": 37200, "medicare": 8700, "addl": 0, "stato": 7751, "sdi": 7800, "netto": 502882}),
]
# Esempi stampati dalle agenzie (solo la ritenuta statale): California Method B esempi A-D, Illinois IL-700-T, North Carolina NC-30
ESEMPI_UFFICIALI = [
    ("California, esempio A", caso("CA", 21000, "weekly", ca_reg=1), 0),
    ("California, esempio B", caso("CA", 160000, "biweekly", ca_fs="married", ca_reg=2, ca_est=1), 238),
    ("California, esempio C", caso("CA", 510000, "monthly", ca_fs="married", ca_reg=5), 82),
    ("California, esempio D", caso("CA", 95000, "weekly", ca_fs="hoh", ca_reg=3), 169),
    ("Illinois, esempio di Alice", caso("IL", 80000, "weekly", il1=2, il2=2), 3213),
    ("North Carolina, esempio NC-30", caso("NC", 45000, "weekly", nc_all=2), 400),
]


def casi_casuali(stato, n, seme):
    rnd = random.Random(seme)
    out = []
    for k in range(n):
        per = rnd.choice(list(PERIODI))
        P = PERIODI[per]
        modo = k % 10
        if modo < 6:
            lordo = rnd.randint(100, 15000000 // P)           # fino a 150.000 l'anno
        elif modo < 8:
            lordo = rnd.randint(15000000 // P, 120000000 // P)  # fino a 1,2 milioni l'anno
        elif modo == 8:
            lordo = rnd.choice([1, 99, 100, 36300, 36301, 72700, 72701, 157500, 314900, 314901]) + rnd.randint(0, 2)
        else:
            lordo = rnd.randint(1, 60000) * 100                 # dollari tondi
        i = caso(stato, lordo, per, fs=rnd.choice(["single", "mfj", "hoh"]), step2=rnd.random() < 0.3)
        if rnd.random() < 0.35:
            i["step3"] = rnd.choice([0, 50000, 220000, 400000, 440000, 1000000])
        if rnd.random() < 0.25:
            i["a4"] = rnd.randint(0, 3000000)
        if rnd.random() < 0.25:
            i["b4"] = rnd.randint(0, 4000000)
        if rnd.random() < 0.2:
            i["c4"] = rnd.randint(0, 50000)
        if rnd.random() < 0.3:
            i["ytd"] = rnd.choice([rnd.randint(0, 30000000), 18450000 - rnd.randint(0, lordo), 20000000 - rnd.randint(0, lordo), 18450000, 20000000, 18449999])
            i["ytd"] = max(0, i["ytd"])
        if stato == "CA":
            i.update(ca_fs=rnd.choice(["single", "married", "hoh"]), ca_reg=rnd.choice([0, 0, 1, 1, 2, 2, 3, 4, 5, 10, 11, 15]), ca_est=rnd.choice([0, 0, 0, 1, 2, 5, 10, 11, 12]))
        elif stato == "IL":
            i.update(il1=rnd.choice([0, 1, 1, 2, 3, 5]), il2=rnd.choice([0, 0, 1, 2]))
        elif stato == "NC":
            i.update(nc_fs=rnd.choice(["single", "hoh"]), nc_all=rnd.choice([0, 0, 1, 2, 3, 6]))
        out.append(i)
    return out


def js_pubblicato():
    js = sorted((SITO / "assets").glob("app.*.js"))
    assert len(js) == 1, "un solo app.*.js in sito/assets"
    pag = (SITO / "index.html").read_text(encoding="utf-8")
    m = re.search(r'<script type="application/json" id="dati-regole">(.*?)</script>', pag, re.S)
    assert m, "dati-regole nella home"
    return js[0], json.loads(m.group(1)), m.group(1)


def esegui_js(js, R, casi, datori):
    prog = ("const A=require(%s);const R=%s;const I=JSON.parse(require('fs').readFileSync(0,'utf8'));"
            "const o={b:I.casi.map(i=>{const r=A.busta(R,i);return {fed:r.fed,ss:r.ss,medicare:r.medicare,addl:r.addl,stato:r.stato,sdi:r.sdi,netto:r.netto};}),"
            "d:I.datori.map(x=>{const r=A.datore(R,x[0],x[1],x[2],x[3]);return {ss:r.ss,medicare:r.medicare,futa:r.futa,suta:r.suta,ett:r.ett,totale:r.totale};})};"
            "process.stdout.write(JSON.stringify(o));") % (json.dumps(str(js)), json.dumps(R))
    p = subprocess.run(["node", "-e", prog], input=json.dumps({"casi": casi, "datori": datori}), capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit("node: " + p.stderr[:2000])
    return json.loads(p.stdout)


# ================================================================ controlli sui dati
def norm(s):
    s = s.replace("­", "").replace("​", "").replace(" ", " ").replace("‑", "-")
    s = re.sub(r"(\w)-\n\s*(\w)", r"\1\2", s)
    return re.sub(r"\s+", " ", s).strip()


def testo_grezzo(p):
    if p.suffix == ".pdf":
        return subprocess.run(["pdftotext", str(p), "-"], capture_output=True, check=True).stdout.decode("utf-8", errors="replace")
    if p.suffix == ".xlsx":
        import zipfile
        return "\n".join(unescape(re.sub(r"<[^>]+>", "", x)) for x in re.findall(r"<si>(.*?)</si>", zipfile.ZipFile(p).read("xl/sharedStrings.xml").decode("utf-8"), flags=re.S))
    s = p.read_text(encoding="utf-8", errors="replace")
    s = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", s)
    return unescape(re.sub(r"<[^>]+>", " ", s))


def controlla_fonti():
    F = json.loads((DATI / "fonti.json").read_text(encoding="utf-8"))["fonti"]
    testi = {}
    for fid, f in F.items():
        p = RADICE / f["file"]
        if not ok(p.exists(), f"fonte {fid}: manca {f['file']}"):
            continue
        dinamica = p.suffix == ".html"   # i byte di una pagina HTML cambiano a ogni scarico: fa fede l'impronta delle frasi citate
        ok(f.get("impronta") == ("frasi" if dinamica else "file"), f"fonte {fid}: tipo di impronta sbagliato in fonti.json")
        if not dinamica:
            ok(hashlib.sha256(p.read_bytes()).hexdigest() == f["sha256"], f"fonte {fid}: impronta SHA-256 del file diversa da fonti.json")
        ok(f["http"] == 200 and re.fullmatch(r"\d{4}-\d\d-\d\d", f["letto_il"]) and f["url"].startswith("https://"), f"fonte {fid}: url, data o HTTP non validi")
        testi[fid] = norm(testo_grezzo(p))
        for k, frase in f["frasi"].items():
            ok(norm(frase) in testi[fid], f"fonte {fid}: frase «{k}» non è alla lettera nel file grezzo")
        # impronta delle frasi ricalcolata qui (non con raccolta/testo.py): chiave, tabulazione, frase normalizzata, in ordine di chiave
        attesa = hashlib.sha256("\n".join(f"{k}\t{norm(f['frasi'][k])}" for k in sorted(f["frasi"])).encode("utf-8")).hexdigest()
        ok(f.get("sha256_frasi") == attesa, f"fonte {fid}: impronta delle frasi diversa da fonti.json")
    ufficiali = [f["url"] for fid, f in F.items() if fid != "patriot"]
    ok(all(re.match(r"https://([\w.-]+\.)?(irs\.gov|doleta\.gov|texas\.gov|floridarevenue\.com|ca\.gov|illinois\.gov|ncdor\.gov|nc\.gov)/", u) for u in ufficiali), "una fonte non è su un dominio ufficiale")
    return F, testi


def controlla_regole(CA):
    G = json.loads((DATI / "regole.json").read_text(encoding="utf-8"))
    ok(G["anno"] == 2026 and G["periodi"] == PERIODI, "regole: anno o periodi")
    ok(G["federale"]["riga_1g"] == ATTESO_1G, "regole: riga 1g")
    for lato, t in ATTESO_FED.items():
        for st, righe in t.items():
            v = G["federale"]["tabelle"][lato][st]
            letto = [(r["da"], Fr(str(r["base"])), r["pct"]) for r in v]
            ok(letto == [(a, Fr(str(c)), d) for a, c, d in righe], f"regole: tabella federale {lato}/{st} diversa dalla trascrizione a mano")
            ok([r["fino"] for r in v] == [x[0] for x in righe[1:]] + [None], f"regole: colonna B di {lato}/{st}")
    f = G["fica"]
    ok((Fr(str(f["ss"])), f["ss_base"], Fr(str(f["medicare"])), Fr(str(f["addl"])), f["addl_soglia"]) == (SS, SS_BASE, MED, ADDL, ADDL_SOGLIA), "regole: FICA")
    u = G["futa"]
    ok((Fr(str(u["aliquota"])), u["base"], Fr(str(u["credito_max"])), Fr(str(u["netta"]))) == (FUTA_LORDA, FUTA_BASE, FUTA_CREDITO, FUTA_NETTA), "regole: FUTA")
    ok({k: Fr(str(v)) for k, v in u["riduzione_credito"].items()} == FUTA_RIDUZIONE, "regole: riduzione del credito FUTA")
    ok(FUTA_LORDA - FUTA_CREDITO == FUTA_NETTA, "FUTA: 6,0 − 5,4 ≠ 0,6")
    ok(sorted(G["stati"]) == sorted(NOMI), "regole: Stati")
    for s, (al, base) in SUTA.items():
        st = G["stati"][s]
        ok((st["nome"], st["slug"]) == NOMI[s], f"regole: nome di {s}")
        ok((Fr(str(st["suta"]["nuovo"])), st["suta"]["base"]) == (al, base), f"regole: disoccupazione statale di {s}")
        ok({k: v for k, v in st["suta"].items() if k not in ("fonte", "nome", "nuovo", "base")} == SUTA_ALTRO[s], f"regole: altri valori della disoccupazione di {s}")
    ok(G["stati"]["TX"]["imposta_reddito"] is None and G["stati"]["FL"]["imposta_reddito"] is None, "regole: Texas e Florida senza imposta")
    ok(G["stati"]["CA"]["sdi"]["aliquota"] == float(CA_SDI) and G["stati"]["CA"]["sdi"]["aliquota_2027"] == CA_SDI_2027, "regole: SDI California")
    il = G["stati"]["IL"]["imposta_reddito"]
    ok((Fr(str(il["aliquota"])), il["riga1"], il["riga2"]) == (IL_ALIQUOTA, IL_RIGA1, IL_RIGA2), "regole: Illinois")
    nc = G["stati"]["NC"]["imposta_reddito"]
    ok(Fr(str(nc["aliquota_ritenuta"])) == NC_ALIQUOTA and nc["aliquota_imposta"] == NC_IMPOSTA, "regole: aliquote North Carolina")
    for per, (ds, dh, es) in NC.items():
        p = nc["periodi"][per]
        ok((cent(p["single"]["deduzione"]), cent(p["hoh"]["deduzione"]), cent(p["single"]["esenzione"]), cent(p["hoh"]["esenzione"])) == (cent(ds), cent(dh), cent(es), cent(es)), f"regole: North Carolina {per}")
    ca = G["stati"]["CA"]["imposta_reddito"]
    for per in PERIODI:
        ok(tuple(ca["esenzione_basso_reddito"][per][k] for k in CA_COL) == CA_ESENZIONE[per], f"regole: California tabella 1 {per}")
        ok(tuple(ca["deduzione_standard"][per][k] for k in CA_COL) == CA_DEDUZIONE[per], f"regole: California tabella 3 {per}")
        ok(tuple(int(x) for x in ca["deduzioni_stimate"][per]) == CA_STIMATE[per], f"regole: California tabella 2 {per}")
        ok([cent(x) for x in ca["credito_esenzioni"][per]] == [cent(x) for x in CA_CREDITO[per]], f"regole: California tabella 4 {per}")
        for st in ("single", "married", "hoh"):
            letto = [(r["da"], Fr(str(r["pct"])) / 100, Fr(str(r["base"]))) for r in ca["scaglioni"][per][st]]
            ok(letto == [(x[0], x[2], x[3]) for x in CA.get(per, {}).get(st, [])], f"regole: California scaglioni {per}/{st} diversi dalla seconda lettura del PDF")
    # i crediti per esenzione sono coerenti tra i periodi (annuo 168,30 per esenzione: 168,30/52 = 3,24 ecc.)
    for per, P in PERIODI.items():
        ok(cent(CA_CREDITO[per][1]) == arrotonda(Fr("168.30") / P), f"California: credito per esenzione {per} non è 168,30 ÷ {P}")
    return G


# ================================================================ controlli sui calcoli
def controlla_calcoli(CA):
    js, R, _ = js_pubblicato()
    casi, etichette = [], []
    for i, _ in CASI_A_MANO:
        casi.append(i)
    for nome, i, _ in ESEMPI_UFFICIALI:
        casi.append(i)
    n0 = len(casi)
    for n, s in enumerate(NOMI):
        casi += casi_casuali(s, CASI_PER_STATO, 20261114 + n)
    # esempi delle pagine
    for s in NOMI:
        for sal in STIPENDI:
            casi.append(caso(s, arrotonda(Fr(sal) / 26)))
    rnd = random.Random(77)
    datori = []
    for s in NOMI:
        datori.append([s, 5000000, 0, None])
        for _ in range(300):
            lordo = rnd.choice([rnd.randint(1, 3000000), rnd.randint(1, 40000000), 700000, 900000, 1425000, 3420000, 18450000, 18450001])
            datori.append([s, lordo, rnd.choice([0, 0, rnd.randint(0, 20000000)]), rnd.choice([None, None, rnd.randint(0, 9000)])])
    out = esegui_js(js, R, casi, datori)
    campi = ("fed", "ss", "medicare", "addl", "stato", "sdi", "netto")
    diversi = 0
    for i, r in zip(casi, out["b"]):
        atteso = rif_busta(i, CA)
        if any(r[k] != atteso[k] for k in campi):
            diversi += 1
            if diversi <= 5:
                err(f"JS ≠ riferimento: {i} → JS {r} · riferimento {atteso}")
    ok(diversi == 0, f"calcolatore JS diverso dal calcolo indipendente in {diversi} casi su {len(casi)}")
    for n, (i, atteso) in enumerate(CASI_A_MANO, 1):
        r = out["b"][n - 1]
        ok({k: r[k] for k in campi} == atteso, f"caso a mano {n}: JS {r} · atteso {atteso}")
        ok({k: v for k, v in rif_busta(i, CA).items()} == atteso, f"caso a mano {n}: il calcolo di riferimento dà {rif_busta(i, CA)}")
    for n, (nome, i, atteso) in enumerate(ESEMPI_UFFICIALI):
        ok(out["b"][len(CASI_A_MANO) + n]["stato"] == atteso, f"{nome}: JS {out['b'][len(CASI_A_MANO) + n]['stato']} centesimi, la fonte dà {atteso}")
    dd = 0
    for x, r in zip(datori, out["d"]):
        atteso = rif_datore(*x)
        if r != atteso:
            dd += 1
            if dd <= 5:
                err(f"datore JS ≠ riferimento: {x} → JS {r} · riferimento {atteso}")
    # casi a mano del datore: 50.000 $ in Texas: 3.100 + 725 + 42 + 243 = 4.110; in California: 3.100 + 725 + 147 (2,1 % × 7.000) + 238 (3,4 %) + 7 (ETT) = 4.217
    ok(rif_datore("TX", 5000000)["totale"] == 411000 and rif_datore("CA", 5000000)["totale"] == 421700, "datore: casi a mano di Texas o California")
    # motore.py (usato da genera.py per i testi) deve dare gli stessi numeri
    sys.path.insert(0, str(RADICE))
    import motore
    for i in casi[:n0] + casi[n0::37]:
        m = motore.busta(R, i)
        ok(all(m[k] == rif_busta(i, CA)[k] for k in campi), f"motore.py ≠ riferimento: {i}")
    return len(casi), len(datori), R


# ================================================================ controlli sulle pagine
def soldi(c):
    return ("−" if c < 0 else "") + f"${abs(c) // 100:,}.{abs(c) % 100:02d}"


def visibile(html):
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", s)))


def controlla_pagine(F, testi, G, CA, R, dati_home):
    pagine = {}
    for p in sorted(SITO.rglob("*.html")):
        if p.name.startswith("google"):
            continue
        pagine["/" + str(p.relative_to(SITO)).replace("index.html", "")] = p.read_text(encoding="utf-8")
    attese = {"/", "/404.html", "/employer-payroll-taxes/", "/federal-withholding/", "/how-we-check/", "/about/", "/privacy/"} | {f"/{v[1]}/" for v in NOMI.values()}
    ok(set(pagine) == attese, f"pagine: {sorted(set(pagine) ^ attese)}")
    titoli, descr = {}, {}
    sitemap = re.findall(r"<loc>(.*?)</loc>", (SITO / "sitemap.xml").read_text(encoding="utf-8"))
    ok(sorted(sitemap) == sorted(URL_SITO + u for u in pagine if u != "/404.html"), "sitemap diversa dalle pagine indicizzabili")
    frasi_fonti = {(fid, k): f["frasi"][k] for fid, f in F.items() for k in f["frasi"]}
    dom = {r["frase"]: r["volume_mese"] for r in json.loads((DATI / "domanda.json").read_text(encoding="utf-8"))["ricerche"]}
    for u, html in pagine.items():
        t = re.findall(r"<title>(.*?)</title>", html)
        d = re.findall(r'<meta name="description" content="(.*?)">', html)
        ok(len(t) == 1 and len(d) == 1 and len(re.findall(r"<h1[ >]", html)) == 1, f"{u}: title, description o h1 non unici")
        t, d = unescape(t[0]), unescape(d[0])
        if u != "/404.html":
            ok(len(t) <= 65, f"{u}: titolo di {len(t)} caratteri")
            ok(40 <= len(d) <= 160, f"{u}: descrizione di {len(d)} caratteri")
            ok(t not in titoli.values() and d not in descr.values(), f"{u}: titolo o descrizione doppi")
            titoli[u], descr[u] = t, d
            ok(f'<link rel="canonical" href="{URL_SITO}{u}">' in html and "noindex" not in html, f"{u}: canonical")
        else:
            ok('content="noindex, follow"' in html, "404 senza noindex")
        ok('lang="en-US"' in html and "goatcounter" in html and "not tax, legal or payroll advice" in html, f"{u}: lingua, contatore o avvertenza")
        ok(CHIAVE not in html and not MODELLI_VIETATI.search(visibile(html)), f"{u}: chiave o nome di modello nel testo")
        # link interni
        for href in re.findall(r'href="(/[^"#]*)(?:#[^"]*)?"', html):
            if href.startswith("/assets/"):
                ok((SITO / href[1:]).exists(), f"{u}: risorsa mancante {href}")
            else:
                ok(href in pagine, f"{u}: link interno rotto {href}")
        for anc in re.findall(r'<a [^>]*href="(/[^"#]*)#([^"]+)"', html):
            ok(f'id="{anc[1]}"' in pagine.get(anc[0], ""), f"{u}: ancora #{anc[1]} assente in {anc[0]}")
        for n in re.findall(r'href="#(f\d+)"', html):
            ok(f'id="{n}"' in html, f"{u}: rimando {n} senza fonte")
        # link esterni: solo le fonti registrate, GoatCounter e le pagine Google della privacy
        for href in set(re.findall(r'<a [^>]*href="(https?://[^"]+)"', html)):
            ok(href in {f["url"] for f in F.values()} or re.match(r"https://(www\.goatcounter\.com|policies\.google\.com|adssettings\.google\.com|www\.google\.com|support\.google\.com)(/|$)", href),
               f"{u}: link esterno non previsto {href}")
        # citazioni: alla lettera nelle fonti e nel file grezzo
        for fid, k, frase in re.findall(r'<blockquote class="cit" data-fonte="([\w]+)" data-frase="([\w]+)"><p>“<span data-cit>(.*?)</span>”</p>', html, re.S):
            ok(unescape(frase) == frasi_fonti.get((fid, k)) and norm(unescape(frase)) in testi[fid], f"{u}: citazione {fid}/{k} non alla lettera")
        ok(html.count("<blockquote") == html.count('<blockquote class="cit" data-fonte='), f"{u}: citazione senza fonte")
        # FAQ: JSON-LD = testo visibile; ogni domanda da una ricerca misurata
        vis = [(unescape(q), unescape(re.sub(r"<sup.*?</sup>", "", a, flags=re.S))) for q, a in re.findall(r'<div class="faq" data-ricerca="[^"]*"><h3>(.*?)</h3><p>(.*?)</p></div>', html, re.S)]
        ld = []
        for blocco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            j = json.loads(blocco)
            if j.get("@type") == "FAQPage":
                ld += [(x["name"], x["acceptedAnswer"]["text"]) for x in j["mainEntity"]]
        ok(vis == ld, f"{u}: FAQ visibili ({len(vis)}) diverse dal JSON-LD ({len(ld)})")
        for ric in re.findall(r'<div class="faq" data-ricerca="([^"]*)"', html):
            ok(dom.get(unescape(ric), 0) > 0, f"{u}: FAQ senza ricerca misurata: {ric}")
        ok(all("<" not in a for _, a in vis), f"{u}: HTML dentro una risposta FAQ")
        # dati del calcolatore uguali in tutte le pagine che lo hanno
        m = re.search(r'<script type="application/json" id="dati-regole">(.*?)</script>', html, re.S)
        if "data-busta" in html or "data-datore" in html:
            ok(m and m.group(1) == dati_home, f"{u}: dati del calcolatore assenti o diversi dalla home")
            ok("Estimate" in html or "estimate" in html, f"{u}: manca la parola estimate")
        # affiliazione spenta: nessun link a Patriot, nessun riquadro
        aff = json.loads((DATI / "affiliati.json").read_text(encoding="utf-8"))["patriot"]
        if not aff["attivo"]:
            ok("data-partner" not in html and 'rel="sponsored' not in html and "patriotsoftware" not in html and "Patriot" not in html, f"{u}: riquadro Patriot presente con interruttore spento")
        else:
            ok(aff["link"].startswith("https://") and "DA-INSERIRE" not in aff["link"], "affiliati.json: attivo senza link")
    ok(len(set(titoli.values())) == len(titoli) == 11, f"titoli unici: {len(titoli)}")

    # ---- cifre delle pagine contro i valori trascritti a mano
    home = visibile(pagine["/"])
    for pezzo in ["6.2%", "$184,500", "1.45%", "0.9%", "$200,000", "$8,600", "$12,900", "$1,690.85", "$156.15", "$124.00", "$29.00"]:
        ok(pezzo in home, f"home: manca {pezzo}")
    fed = pagine["/federal-withholding/"]
    for lato, t in ATTESO_FED.items():
        for st, righe in t.items():
            m = re.search(rf'<table class="dati" data-fed="{lato}-{st}">.*?<tbody>(.*?)</tbody>', fed, re.S)
            celle = [re.findall(r'<td class="n">(.*?)</td>', r) for r in re.findall(r"<tr>(.*?)</tr>", m.group(1), re.S)] if m else []
            attese_c = [[f"${a:,}", (f"${righe[n + 1][0]:,}" if n < 7 else "–"), soldi(cent(c)), f"{d}%", f"${a:,}"] for n, (a, c, d) in enumerate(righe)]
            ok(celle == attese_c, f"federal-withholding: tabella {lato}/{st} diversa dalla trascrizione a mano")
    # esempio svolto della pagina federale: 3.000 × 24 = 72.000 − 12.900 = 59.100 → 4.280 → 178,33 (riga 2h); − 166,67 (riga 3b) = 11,66 (caso a mano 4)
    ok("$11.66" in visibile(fed) and "$11.67" not in visibile(fed) and "$178.33" in visibile(fed) and "$166.67" in visibile(fed), "federal-withholding: esempio svolto")
    dat = pagine["/employer-payroll-taxes/"]
    for s, (al, base) in SUTA.items():
        m = re.search(rf'<tr data-suta="{s}">(.*?)</tr>', dat, re.S)
        celle = re.findall(r'<td class="n">(.*?)</td>', m.group(1)) if m else []
        pc = f"{float(al) * 100:.3f}".rstrip("0").rstrip(".") + "%"
        ok(celle == [pc, f"${base:,}", soldi(arrotonda(base * al)), soldi(rif_datore(s, 5000000)["totale"])], f"employer-payroll-taxes: riga {s} = {celle}")
    for pezzo in ["6%", "$7,000", "5.4%", "0.6%", "2.1%", "1.5%", "$42.00", "$147.00", "$4,110.00", "$4,217.00", "7.65%"]:
        ok(pezzo in visibile(dat), f"employer-payroll-taxes: manca {pezzo}")
    for s, (nome, sl) in NOMI.items():
        html = pagine[f"/{sl}/"]
        vis_s = visibile(html)
        m = re.search(rf'<table class="dati" data-esempi="{s}">.*?<tbody>(.*?)</tbody>', html, re.S)
        righe = re.findall(r'<tr data-stipendio="(\d+)">(.*?)</tr>', m.group(1), re.S) if m else []
        ok([int(a) for a, _ in righe] == STIPENDI, f"{sl}: righe degli esempi")
        for sal, r in righe:
            lordo = arrotonda(Fr(int(sal)) / 26)
            b = rif_busta(caso(s, lordo), CA)
            attese_c = [soldi(lordo), soldi(b["fed"]), soldi(b["ss"] + b["medicare"])] + ([soldi(b["stato"])] if s in ("CA", "IL", "NC") else []) + ([soldi(b["sdi"])] if s == "CA" else []) + [soldi(b["netto"])]
            celle = [re.sub(r"<[^>]+>", "", c) for c in re.findall(r'<td class="n">(.*?)</td>', r)]
            ok(celle == attese_c, f"{sl}: esempio {sal} = {celle}, atteso {attese_c}")
        al, base = SUTA[s]
        pc = f"{float(al) * 100:.3f}".rstrip("0").rstrip(".") + "%"
        ok(pc in vis_s and f"${base:,}" in vis_s and soldi(arrotonda(base * al)) in vis_s, f"{sl}: aliquota o base della disoccupazione statale")
        ok(f"{nome} paycheck calculator 2026" in vis_s, f"{sl}: h1")
        ok(f'<option value="{s}" selected>' in html, f"{sl}: Stato non preselezionato")
    for sl, pezzi in {"texas": ["2.7%", "0.32%", "6.32%", "$243.00"], "florida": ["2.7%", "$189.00"],
                      "california": ["1.3%", "1.4%", "3.4%", "0.1%", "2.1%", "$147.00", "$2.38", "$1,123.00", "$15.33", "$12.95", "1.5%", "6.2%"],
                      "illinois": ["4.95%", "$2,925", "$1,000", "$32.13", "$150.96", "$649.04", "3.35%", "0.55%", "$477.38"],
                      "north-carolina": ["4.09%", "3.99%", "$490.38", "$735.58", "$96.15", "$4.00", "$108.65", "1%", "$342.00", "0.06%", "5.76%"]}.items():
        for pezzo in pezzi:
            ok(pezzo in visibile(pagine[f"/{sl}/"]), f"{sl}: manca {pezzo}")
    # ---- file accessori
    ok((SITO / "ads.txt").read_text().strip() == "google.com, pub-3750093987658434, DIRECT, f08c47fec0942fa0", "ads.txt")
    ok((SITO / "robots.txt").read_text() == f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n", "robots.txt")
    ok((SITO / "b5a26a844a465f58552debee2c8a0114.txt").read_text() == "b5a26a844a465f58552debee2c8a0114", "file della chiave IndexNow")
    ok('ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."' in (SITO / "netlify.toml").read_text(), "netlify.toml senza la regola ignore")
    ok((SITO / "assets" / "og.png").exists(), "manca assets/og.png")
    ok("ca-pub-3750093987658434" in pagine["/"], "AdSense assente nella home")
    modulo = re.search(r'<form name="corrections".*?</form>', pagine["/how-we-check/"], re.S)
    ok(modulo and not re.search(r'name="(name|email|nome)"|type="email"', modulo.group(0)), "modulo delle correzioni: campo personale")
    errori, _info = MON.controlla_sito("paycheck", SITO)
    for e in errori:
        err(f"monetizzazione: {e}")
    # nessuna chiave in tutta la cartella
    for p in RADICE.rglob("*"):
        if p.is_file() and p.suffix in (".py", ".js", ".json", ".md", ".html", ".txt", ".toml", ".xml", ".css", ".svg") and CHIAVE in p.read_text(encoding="utf-8", errors="ignore"):
            err(f"chiave seodata in {p}")
    return len(pagine)


def strumenti():
    idx = (RADICE.parent / "studio-business" / "strumenti" / "indexnow.py").read_text(encoding="utf-8")
    ok('("us-paycheck-calculator.netlify.app", "paycheck")' in idx, "indexnow.py: sito non registrato")
    mj = json.loads((RADICE.parent / "studio-business" / "strumenti" / "monetizzazione.json").read_text(encoding="utf-8"))
    ok("paycheck" in mj["adsense_siti"] and "paycheck" in mj["_siti_della_rete"] and "paycheck" in MON.SITI, "monetizzazione: sito non registrato")


def main():
    if not SITO.exists():
        raise SystemExit("manca paycheck/sito: lanciare prima genera.py")
    CA = california_raw()
    F, testi = controlla_fonti()
    G = controlla_regole(CA)
    n_casi, n_dat, R = controlla_calcoli(CA)
    _, _, dati_home = js_pubblicato()
    n_pag = controlla_pagine(F, testi, G, CA, R, dati_home)
    strumenti()
    if "--browser" in sys.argv and not ERR:
        import os
        casi = []
        for i, atteso in CASI_A_MANO:
            casi.append({"i": i, "netto": soldi(atteso["netto"])})
        env = dict(os.environ, CASI_CALC=json.dumps(casi), DATORE_TX=soldi(rif_datore("TX", 5000000)["totale"]), DATORE_CA=soldi(rif_datore("CA", 5000000)["totale"]))
        p = subprocess.run(["node", str(RADICE / "verifica_browser.js")], env=env, capture_output=True, text=True)
        print(p.stdout.strip())
        if p.returncode != 0:
            err("browser: " + (p.stderr.strip()[-1500:] or "errori sopra"))
    for a in AVV:
        print("AVVISO:", a)
    for e in ERR:
        print("ERRORE:", e)
    print(f"{len(F)} fonti e {sum(len(f['frasi']) for f in F.values())} frasi alla lettera · {n_casi} buste paga JS = calcolo indipendente ({CASI_PER_STATO} casuali per Stato, {len(CASI_A_MANO)} a mano, "
          f"{len(ESEMPI_UFFICIALI)} esempi ufficiali) · {n_dat} casi del datore · {n_pag} pagine · {len(ERR)} errori, {len(AVV)} avvisi")
    sys.exit(1 if ERR else 0)


if __name__ == "__main__":
    main()
