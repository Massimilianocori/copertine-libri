"""Estrae le date delle prove scritte EOI (lingua x livello x giorno) dalle fonti ufficiali.

Uso: python3 -I estrai.py <cartella_grezzi> <file_uscita.json>
La cartella è quella riempita da scarica.py (PDF già convertiti in .txt).

Un lettore per comunità, ma con pezzi comuni:
- `griglia()` per i calendari a griglia (giorni in colonna, lingue nelle celle):
  Andalucía, Comunitat Valenciana, Castilla-La Mancha;
- `blocchi()` per le tabelle con la lingua scritta una volta per gruppo di livelli:
  País Vasco, Canarias, Navarra;
- espressioni regolari per le tabelle e gli elenchi in prosa: Madrid (lettore del primo
  test, migliorato), Cataluña, Illes Balears, Aragón, Castilla y León, Región de Murcia,
  Principado de Asturias.
Le tappe (iscrizioni, liste, risultati) si leggono con regole per documento.
"""
import html, json, os, re, sys

MESI = {m: i + 1 for i, m in enumerate(
    "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split())}
MESI.update({"gener": 1, "febrer": 2, "març": 3, "abril": 4, "maig": 5, "juny": 6, "juliol": 7,
             "agost": 8, "setembre": 9, "octubre": 10, "novembre": 11, "desembre": 12,
             "xuño": 6, "maio": 5, "setiembre": 9})
MESE_RE = "|".join(sorted(MESI, key=len, reverse=True))

# nome scritto nella fonte -> nome normalizzato
LINGUE = [
    (r"espa[ñn]ol(?:\s+(?:para|como|per a)\s+(?:extranjeros|estrangers|lengua\s+extranjera))?|espanyol(?:\s+(?:per a estrangers|llengua estrangera))?", "español"),
    (r"alem[áa]n|alemany", "alemán"), (r"ingl[ée]s|angl[èe]s", "inglés"),
    (r"franc[ée]s|franc[èe]s", "francés"), (r"italiano|itali[àa]", "italiano"),
    (r"portugu[ée]s|portugu[èe]s", "portugués"), (r"[áàa]rabe|[àa]rab", "árabe"),
    (r"chino|xin[èe]s", "chino"), (r"japon[ée]s|japon[èe]s", "japonés"), (r"ruso|rus", "ruso"),
    (r"euskera|euskara|[èe]uscar", "euskera"), (r"catal[áa]n|catal[àa]", "catalán"),
    (r"gallego", "gallego"), (r"valenciano", "valenciano"), (r"griego|grec", "griego"),
    (r"neerland[ée]s|neerland[èe]s", "neerlandés"), (r"polaco", "polaco"), (r"fin[ée]s", "finés"),
    (r"rumano", "rumano"), (r"core[àa]|coreano", "coreano"),
]
LINGUA_RE = "(" + "|".join(p for p, _ in LINGUE) + ")"
LIVELLO_RE = r"(A1|A2|B1|B2|C1|C2)"


def norm_lingua(s):
    s = re.sub(r"\s+", " ", s.strip().lower())
    for pat, nome in LINGUE:
        if re.fullmatch(pat, s, flags=re.I):
            return nome
    return None


def iso(anno, mese, giorno):
    if isinstance(mese, str):
        mese = int(mese) if mese.isdigit() else MESI[mese.lower()]
    return f"{anno}-{int(mese):02d}-{int(giorno):02d}"


def leggi(cartella, nome):
    p = os.path.join(cartella, nome)
    if nome.endswith(".pdf"):
        p = p[:-4] + ".txt"
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        return None
    t = open(p, encoding="utf-8", errors="ignore").read()
    # caratteri di controllo nei PDF (il difetto trovato su Madrid al primo test)
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f­]", "", t)


def html_testo(t):
    t = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", "", t)
    t = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</tr>|</h\d>|</div>", "\n", t)
    t = html.unescape(re.sub("<[^>]+>", " ", t))
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n", t)


def rec(comunita, anno, conv, lingua, livello, data, ora="", fonte="", nota=""):
    return {"comunita": comunita, "anno": anno, "convocatoria": conv, "lingua": lingua,
            "livello": livello, "data": data, "ora": ora, "fonte": fonte, "nota": nota}


# ---------------------------------------------------------------- pezzi comuni

def pezzi(riga):
    """Spezza una riga 'layout' in pezzi separati da 2+ spazi: (inizio, fine, testo).
    Spezza anche 'VALENCIANO B1, VALENCIANO B2,' (due celle vicine separate da uno spazio
    dopo la virgola, se dopo viene il nome di una lingua)."""
    out = []
    for m in re.finditer(r"\S+(?: \S+)*", riga):
        a, t = m.start(), m.group(0)
        tagli = [0] + [x.end() for x in re.finditer(r", (?=" + LINGUA_RE + r"\b)", t, re.I)] + [len(t)]
        for i in range(len(tagli) - 1):
            pz = t[tagli[i]:tagli[i + 1]].strip()
            if pz:
                out.append((a + tagli[i], a + tagli[i] + len(pz), pz))
    return out


def coppie_lingua_livello(testo):
    """Da 'INGLÉS NA C2 ALEMÁN NI B1, NI B2' -> [(inglés, C2), (alemán, B1), (alemán, B2)].
    Accetta anche l'ordine inverso '16:00 B2 Inglés' (livello prima della lingua)."""
    out, lingua, ora, livelli_senza = [], None, "", []
    tok_re = re.compile(r"(\d{1,2}[:.]\s?\d{2})|" + LINGUA_RE + r"|\b" + LIVELLO_RE + r"\b|\b(ma[ñn]ana|tarde)\b", re.I)
    for m in tok_re.finditer(testo):
        if m.group(1):
            ora, lingua = re.sub(r"\s", "", m.group(1)).replace(".", ":"), None
        elif m.group(2):
            lingua = norm_lingua(m.group(2))
            for lv in livelli_senza:
                out.append((lingua, lv, ora))
            livelli_senza = []
        elif m.group(len(m.groups()) - 1):
            lv = m.group(len(m.groups()) - 1).upper()
            if lingua:
                out.append((lingua, lv, ora))
            else:
                livelli_senza.append(lv)
        else:
            ora, lingua = m.group(0).lower(), None
    return out


def griglia(righe, trova_intestazione, allinea="centro", scarta=()):
    """Calendari a griglia. trova_intestazione(i, righe) -> [(x, data_iso)] o None.
    Restituisce {data_iso: testo della colonna sotto quell'intestazione}."""
    colonne, testi = None, {}
    for i, r in enumerate(righe):
        h = trova_intestazione(i, righe)
        if h:
            colonne = h
            continue
        if not colonne:
            continue
        for a, b, t in pezzi(r):
            if t.strip().lower() in scarta:
                continue
            if allinea == "centro":
                x = (a + b) / 2
                col = min(colonne, key=lambda c: abs(c[0] - x))
            else:  # allineamento a sinistra: la colonna con l'inizio più vicino a sinistra del pezzo
                cand = [c for c in colonne if c[0] <= a + 3]
                col = max(cand, key=lambda c: c[0]) if cand else colonne[0]
            testi.setdefault(col[1], []).append(t)
    return {d: " ".join(v) for d, v in testi.items()}


def blocchi(righe, data_re, colonne_conv):
    """Tabelle con la lingua scritta una volta per gruppo di righe (spesso a metà gruppo).
    Un nuovo gruppo comincia quando il livello torna indietro (C1 -> A2/B1).
    data_re: espressione con un gruppo per la data; colonne_conv: [(x_min, convocatoria)]."""
    ordine = {"A1": 0, "A2": 1, "B1": 2, "B2": 3, "C1": 4, "C2": 5}
    gruppi, cur, prev, sospese = [], None, 99, []
    for r in righe:
        mlv = re.search(r"\b" + LIVELLO_RE + r"\)?\s", r + " ")
        mli = re.search(r"(?<![\w(])" + LINGUA_RE + r"(?![\w])", r, re.I)
        date = [(m.start(), m.group(1)) for m in re.finditer(data_re, r)]
        if mlv:
            lv = mlv.group(1)
            if ordine[lv] <= prev or cur is None:
                cur = {"lingua": None, "righe": []}
                gruppi.append(cur)
            prev = ordine[lv]
            cur["righe"].append((lv, sospese + date, r))
            sospese = []
        elif date:
            sospese = date  # date su una riga senza livello: vanno al livello successivo
        if mli and cur is not None and not cur["lingua"]:
            # lingua sulla riga di un livello o su una riga a sé dentro il gruppo
            if mlv or not date:
                nome = norm_lingua(mli.group(1))
                if nome:
                    # se la riga della lingua viene prima del primo livello del gruppo nuovo,
                    # la assegna al gruppo che sta per aprirsi
                    cur["lingua"] = nome
        elif mli and not mlv and cur is not None and cur["lingua"]:
            nome = norm_lingua(mli.group(1))
            if nome and nome != cur["lingua"]:
                cur = {"lingua": nome, "righe": []}
                gruppi.append(cur)
                prev = -1
    out = []
    for g in gruppi:
        for lv, date, r in g["righe"]:
            for x, d in date:
                conv = [c for xm, c in colonne_conv if x >= xm][-1]
                out.append((g["lingua"], lv, conv, d, r))
    return out


def tabella_due_colonne(righe, x, comunita, fonte, anno):
    """Tabelle 'data | cosa succede' su due colonne affiancate (Valencia anexo III, Asturias).
    Una riga nuova comincia quando la colonna sinistra apre con una data o con Desde/Del/Hasta."""
    gruppi = []
    for r in righe:
        sx, dx = r[:x].strip(), r[x:].strip()
        if re.match(r"(Desde|Del|Hasta|Entre|\d{1,2} de)", sx):
            gruppi.append([sx, dx])
        elif gruppi:
            gruppi[-1][0] += " " + sx
            gruppi[-1][1] += " " + dx
    out = []
    for sx, dx in gruppi:
        dx = re.sub(r"\s+", " ", dx).lower()
        date = re.findall(r"(\d{1,2}) (?:de )?(" + MESE_RE + r")(?: de (\d{4}))?", sx)
        if not date:
            continue
        if "alegaciones" in dx:
            tipo = "reclami alle liste"
        elif "provisional" in dx and ("admitid" in dx or "inscripción" in dx):
            tipo = "lista provvisoria"
        elif "definitiv" in dx and ("admitid" in dx or "inscripción" in dx):
            tipo = "lista definitiva"
        elif "inscripción" in dx or "matrícula" in dx or "matriculación" in dx:
            tipo = "iscrizione/matricola"
        elif "orales" in dx:
            tipo = "date delle prove orali pubblicate (da ogni EOI) entro"
        else:
            continue
        d0 = date[0]
        d1 = date[-1] if len(date) > 1 else None
        a0 = d0[2] or (d1[2] if d1 and d1[2] else anno)
        out.append(dict(comunita=comunita, tipo=tipo, data=iso(a0, d0[1], d0[0]),
                        fine=iso(d1[2] or a0, d1[1], d1[0]) if d1 else "", fonte=fonte))
    return out


# ---------------------------------------------------------------- lettori per comunità

def madrid(c):
    t = leggi(c, "mad_bocm_2026.pdf")
    if not t:
        return [], []
    esami = [rec("Madrid", 2026, "única (libre)", norm_lingua(m.group(2)), m.group(1),
                 iso(2026, m.group(4), m.group(3)), m.group(5), "mad_bocm_2026.pdf")
             for m in re.finditer(r"Nivel \w+\s*\((A2|B1|B2|C1|C2)\)\s+" + LINGUA_RE +
                                  r"\s+(\d{1,2}) de (\w+)\s+(\d{1,2}:\d{2})", t, re.I)]
    tappe = []
    prosa = re.sub(r"-\n\s*", "", t)
    prosa = re.sub(r"\s+", " ", prosa)
    m = re.search(r"inscribirse del (\d{1,2}) al (\d{1,2}) de (\w+) de (\d{4})", prosa)
    if m:
        tappe.append(("iscrizione", iso(m.group(4), m.group(3), m.group(1)), iso(m.group(4), m.group(3), m.group(2))))
    m = re.search(r"Con fecha (\d{1,2}) de (\w+) de (\d{4}), se publicará la lista provisional", prosa)
    if m:
        tappe.append(("lista provvisoria", iso(m.group(3), m.group(2), m.group(1)), ""))
    m = re.search(r"Con fecha (\d{1,2}) de (\w+) de (\d{4}), los solicitantes podrán acceder a la lista definitiva", prosa)
    if m:
        tappe.append(("lista definitiva", iso(m.group(3), m.group(2), m.group(1)), ""))
    m = re.search(r"efectuará del (\d{1,2}) al (\d{1,2}) de (\w+) de (\d{4})", prosa)
    if m:
        tappe.append(("matricola", iso(m.group(4), m.group(3), m.group(1)), iso(m.group(4), m.group(3), m.group(2))))
    return esami, [dict(comunita="Madrid", tipo=a, data=b, fine=e, fonte="mad_bocm_2026.pdf") for a, b, e in tappe]


def pais_vasco(c):
    esami = []
    for nome, anno in (("pv_cal_2027.pdf", 2027), ("pv_cal_2026.pdf", 2026)):
        t = leggi(c, nome)
        if not t:
            continue
        righe = [r.replace("ESPAÑOL PARA", "ESPAÑOL").replace("EXTRANJEROS", "") for r in t.splitlines()]
        for lingua, lv, conv, d, r in blocchi(righe, r"(\d{2}/\d{2}/\d{4})", [(0, "única (libre)")]):
            g, m_, a = d.split("/")
            esami.append(rec("País Vasco", anno, conv, lingua, lv, iso(a, m_, g), "", nome))
    tappe = []
    t = leggi(c, "pv_res_2027.pdf")
    if t:
        p = re.sub(r"\s+", " ", t)
        m = re.search(r"plazo para la solicitud de la matrícula será el comprendido entre el (\d{1,2}) de (\w+) y el (\d{1,2}) de (\w+)(?: de (\d{4}))?", p)
        if m:
            tappe.append(dict(comunita="País Vasco", tipo="iscrizione", data=iso(2027, m.group(2), m.group(1)),
                              fine=iso(2027, m.group(4), m.group(3)), fonte="pv_res_2027.pdf"))
        m = re.search(r"se harán publicas el día (\d{1,2}) de (\w+) de (\d{4})", p)
        if m:
            tappe.append(dict(comunita="País Vasco", tipo="lista definitiva", data=iso(m.group(3), m.group(2), m.group(1)),
                              fine="", fonte="pv_res_2027.pdf"))
    return esami, tappe


def cataluna(c):
    p = os.path.join(c, "cat_calendari_2027.html")
    if not os.path.exists(p):
        return [], []
    t = html_testo(open(p, encoding="utf-8", errors="ignore").read())
    esami, livello = [], None
    for r in t.splitlines():
        m = re.search(r"Certificat de nivell \w+ " + LIVELLO_RE, r)
        if m:
            livello = m.group(1)
            continue
        m = re.match(r"\s*" + LINGUA_RE + r"[^:]*:\s*(\d{1,2}) de (\w+) de (\d{4}), (al matí|a la tarda)", r, re.I)
        if m and livello:
            g = m.groups()
            esami.append(rec("Cataluña", int(g[3]), "ordinària", norm_lingua(g[0]), livello,
                             iso(g[3], g[2], g[1]), "10:00" if "matí" in g[4] else "16:00", "cat_calendari_2027.html"))
    tappe = []
    p1 = re.sub(r"\s+", " ", t)
    for tipo, pat in [("iscrizione", r"Inscripció del (\d{1,2}) de (\w+) .{0,40}?al (\d{1,2}) de (\w+) de (\d{4})"),
                      ("lista provvisoria", r"Llista provisional de persones admeses i excloses a partir de l'(\d{1,2}) de (\w+) de (\d{4})"),
                      ("lista definitiva", r"Llista definitiva de persones admeses i excloses a partir del (\d{1,2}) d'(\w+) de (\d{4})"),
                      ("risultati provvisori", r"Qualificacions provisionals (\d{1,2}) de (\w+) de (\d{4})"),
                      ("risultati definitivi", r"Qualificacions definitives (\d{1,2}) de (\w+) de (\d{4})")]:
        m = re.search(pat, p1)
        if m:
            g = m.groups()
            if tipo == "iscrizione":
                tappe.append(dict(comunita="Cataluña", tipo=tipo, data=iso(g[4], g[1], g[0]), fine=iso(g[4], g[3], g[2]), fonte="cat_calendari_2027.html"))
            else:
                tappe.append(dict(comunita="Cataluña", tipo=tipo, data=iso(g[2], g[1], g[0]), fine="", fonte="cat_calendari_2027.html"))
    return esami, tappe


def andalucia(c):
    t = leggi(c, "and_boja46_2026.pdf")
    if not t:
        return [], []
    a = t.find("ANEXO II\n")
    b = t.find("ANEXO III", a)
    righe = t[a:b].splitlines()
    conv = {"v": "ordinaria"}

    def intest(i, rr):
        r = rr[i]
        if "EXTRAORDINARIA" in r:
            conv["v"] = "extraordinaria"
        gg = [(m.start(), m.end(), int(m.group(2))) for m in
              re.finditer(r"(Lunes|Martes|Miércoles|Jueves|Viernes),\s*(\d{1,2})", r)]
        if len(gg) < 2:
            return None
        # il mese è sulla riga sopra (MAYO / JUNIO / SEPTIEMBRE), allineato alla colonna
        sopra = next(x for x in reversed(rr[:i]) if re.search(r"MAYO|JUNIO|SEPTIEMBRE", x))
        mesi = [(m.start(), m.group(1).lower()) for m in re.finditer(r"(MAYO|JUNIO|SEPTIEMBRE)", sopra)]
        out = []
        for s, e, g in gg:
            mese = min(mesi, key=lambda mm: abs(mm[0] - s))[1]
            out.append(((s + e) / 2, (iso(2026, mese, g), conv["v"])))
        return out

    col = griglia(righe, intest, "centro", scarta={"mañana", "tarde", "turno"})
    esami = []
    for (data, cv), testo in col.items():
        testo = re.sub(r"ESPAÑOL COMO\s+LENGUA EXTRANJERA", "ESPAÑOL", testo)
        for lingua, lv, _ in coppie_lingua_livello(testo):
            nota = "solo EOI Corduba" if (data == "2026-06-05" and lingua == "inglés") else ""
            esami.append(rec("Andalucía", 2026, cv, lingua, lv, data, "", "and_boja46_2026.pdf", nota))
    tappe = []
    m = re.search(r"Entre el (\d{1,2}) y el (\d{1,2}) de (\w+) de (\d{4})\s+Inscripción del alumnado", t)
    if m:
        tappe.append(dict(comunita="Andalucía", tipo="iscrizione", data=iso(m.group(4), m.group(3), m.group(1)),
                          fine=iso(m.group(4), m.group(3), m.group(2)), fonte="and_boja46_2026.pdf"))
    return esami, tappe


def valencia(c):
    t = leggi(c, "val_dogv_2026.pdf")
    if not t:
        return [], []
    esami = []
    for titolo, conv in (("ANEXO I\n", "ordinaria"), ("ANEXO II\n", "extraordinaria")):
        a = t.find(titolo)
        b = min(x for x in (t.find("ANEXO I", a + 10), t.find("LAS PRUEBAS ORALES", a)) if x > 0)
        righe = t[a:b].splitlines()

        def intest(i, rr):
            gg = [(m.start(), m.end(), m.group(1), m.group(2)) for m in
                  re.finditer(r"(\d{1,2}) (junio|septiembre)", rr[i])]
            if len(gg) < 2:
                return None
            return [((s + e) / 2, iso(2026, mes, g)) for s, e, g, mes in gg]

        col = griglia(righe, intest, "centro")
        for data, testo in col.items():
            for lingua, lv, ora in coppie_lingua_livello(testo):
                esami.append(rec("Comunitat Valenciana", 2026, conv, lingua, lv, data, ora, "val_dogv_2026.pdf"))
    a3 = t.find("ANEXO III\n")
    tappe = tabella_due_colonne(t[a3:].splitlines(), 62, "Comunitat Valenciana", "val_dogv_2026.pdf", 2026) if a3 > 0 else []
    return esami, tappe


def canarias(c):
    t = leggi(c, "can_apendice2_2026.pdf")
    esami = []
    if t:
        a = t.find("CALENDARIO Y TURNO DE LA PARTE ESCRITA")
        b = t.find("HORARIO DE LA PARTE ESCRITA", a)
        righe = t[a:b].splitlines()
        for lingua, lv, conv, d, r in blocchi(righe, r"(\d{2}-\d{2}-\d{4})", [(0, "ordinaria"), (100, "extraordinaria")]):
            g, m_, an = d.split("-")
            esami.append(rec("Canarias", 2026, conv, lingua, lv, iso(an, m_, g), "", "can_apendice2_2026.pdf"))
    tappe = []
    p = os.path.join(c, "can_pagina_2026.html")
    if os.path.exists(p):
        h = re.sub(r"\s+", " ", html_testo(open(p, encoding="utf-8", errors="ignore").read()))
        m = re.search(r"Fechas de inscripción Aspirantes libres de todos los niveles .*?: del (\d{1,2}) de (\w+) al (\d{1,2}) de (\w+) de (\d{4})", h)
        if m:
            tappe.append(dict(comunita="Canarias", tipo="iscrizione", data=iso(m.group(5), m.group(2), m.group(1)),
                              fine=iso(m.group(5), m.group(4), m.group(3)), fonte="can_pagina_2026.html"))
        m = re.search(r"listas definitivas de admitidos/as: Aspirantes libres .*?: (\d{1,2}) de (\w+) de (\d{4})", h)
        if m:
            tappe.append(dict(comunita="Canarias", tipo="lista definitiva", data=iso(m.group(3), m.group(2), m.group(1)), fine="", fonte="can_pagina_2026.html"))
    t1 = leggi(c, "can_apendice1_2026.pdf")
    if t1:
        for conv, pat in (("ordinaria", r"Publicación de las calificaciones de la convocatoria ordinaria\.\s+(\d{1,2}) de (\w+)"),
                          ("extraordinaria", r"Publicación de las calificaciones de la convocatoria extraordinaria\.\s+(\d{1,2}) de (\w+)")):
            m = re.search(pat, t1)
            if m:
                tappe.append(dict(comunita="Canarias", tipo="risultati " + conv, data=iso(2026, m.group(2), m.group(1)), fine="", fonte="can_apendice1_2026.pdf"))
    return esami, tappe


def murcia(c):
    t = leggi(c, "mur_borm181_2026.pdf")
    if not t:
        return [], []
    a = t.find("CALENDARIO DE REALIZACIÓN DE LAS PRUEBAS ESCRITAS NIVEL INTERMEDIO")
    b = t.find("El calendario de celebración de las pruebas es el mismo", a)
    righe = t[a:b].splitlines()
    cols = None
    esami = []
    for r in righe:
        if "NIB1" in r:
            cols = [(m.start(), {"NIB1": "B1", "NIB2": "B2", "NAC1": "C1", "NAC2": "C2"}[m.group(0)])
                    for m in re.finditer(r"NIB1|NIB2|NAC1|NAC2", r)]
            continue
        m = re.match(r"\s*" + LINGUA_RE + r"\s", r, re.I)
        if cols and m:
            for d in re.finditer(r"(\d{1,2}) de (\w+)", r):
                lv = min(cols, key=lambda cc: abs(cc[0] - d.start()))[1]
                esami.append(rec("Región de Murcia", 2026, "ordinaria", norm_lingua(m.group(1)), lv,
                                 iso(2026, d.group(2), d.group(1)), "16:30", "mur_borm181_2026.pdf"))
    tappe = []
    p = re.sub(r"\s+", " ", t)
    m = re.search(r"modalidad libre será desde el día (\d{1,2}) al (\d{1,2}) de (\w+) de (\d{4})", p)
    if m:
        tappe.append(dict(comunita="Región de Murcia", tipo="iscrizione", data=iso(m.group(4), m.group(3), m.group(1)),
                          fine=iso(m.group(4), m.group(3), m.group(2)), fonte="mur_borm181_2026.pdf"))
    m = re.search(r"El (\d{1,2}) de (\w+) de (\d{4}) se publicará la relación provisional", p)
    if m:
        tappe.append(dict(comunita="Región de Murcia", tipo="lista provvisoria", data=iso(m.group(3), m.group(2), m.group(1)), fine="", fonte="mur_borm181_2026.pdf"))
    return esami, tappe


def baleares(c):
    t = leggi(c, "bal_boib17_2026.pdf")
    esami = []
    if t:
        conv, lingua = None, None
        for r in t.splitlines():
            if "Convocatòria ordinària" in r:
                conv = "ordinària"
            elif "Convocatòria Extraordinària" in r:
                conv = "extraordinària"
            m = re.match(r"\s*" + LINGUA_RE + r"(?: llengua estrangera)?\s*$", r, re.I)
            if m and conv:
                lingua = norm_lingua(m.group(1))
                continue
            m = re.search(r"Certificat de nivell \w+ " + LIVELLO_RE + r": prova escrita dia (\d{1,2}) de (\w+), (\d{1,2})\.\s?(\d{2})", r)
            if m and conv and lingua:
                esami.append(rec("Illes Balears", 2026, conv, lingua, m.group(1), iso(2026, m.group(3), m.group(2)),
                                 f"{m.group(4)}:{m.group(5)}", "bal_boib17_2026.pdf"))
    tappe = []
    t = leggi(c, "bal_boib14_2026.pdf")
    if t:
        p = re.sub(r"\s+", " ", t)
        m = re.search(r"des de les 9\.00 hores del dia (\d{1,2}) de (\w+) a les 23\.59 del dia (\d{1,2}) de (\w+) de (\d{4})", p)
        if m:
            tappe.append(dict(comunita="Illes Balears", tipo="iscrizione", data=iso(m.group(5), m.group(2), m.group(1)),
                              fine=iso(m.group(5), m.group(4), m.group(3)), fonte="bal_boib14_2026.pdf"))
    return esami, tappe


def aragon(c):
    esami = []
    for nome, conv in (("ara_anexo2_2026.pdf", "ordinaria"), ("ara_anexo3_2026.pdf", "extraordinaria")):
        t = leggi(c, nome)
        if not t:
            continue
        livello = None
        for r in t.splitlines():
            m = re.search(r"Nivel " + LIVELLO_RE + r"\s*$", r)
            if m:
                livello = m.group(1)
            if re.search(r"Niveles C1 y C2", r):
                livello = None
            m = re.match(r"\s*" + LINGUA_RE + r"(?:\s+" + LIVELLO_RE + r")?\s+Oficial-Libre\s+\w+,\s+(\d{1,2}) de (\w+)\s+(.+)$", r, re.I)
            if m:
                lv = m.group(2) or livello
                ora = m.group(5).strip()
                esami.append(rec("Aragón", 2026, conv, norm_lingua(m.group(1)), lv, iso(2026, m.group(4), m.group(3)), ora, nome))
    tappe = []
    t = leggi(c, "ara_anexo5_2026.pdf")
    if t:
        m = re.search(r"Del \w+, (\d{1,2}) de (\w+) \(9:00\) al \w+, (\d{1,2}) de (\w+)", t)
        if m:
            tappe.append(dict(comunita="Aragón", tipo="preiscrizione", data=iso(2026, m.group(2), m.group(1)),
                              fine=iso(2026, m.group(4), m.group(3)), fonte="ara_anexo5_2026.pdf"))
        m = re.search(r"\w+, (\d{1,2}) de (\w+) \(14:00\)\s*\n\s*PREINSCRIPCIONES ADMITIDAS", t)
        if m:
            tappe.append(dict(comunita="Aragón", tipo="lista definitiva", data=iso(2026, m.group(2), m.group(1)), fine="", fonte="ara_anexo5_2026.pdf"))
    return esami, tappe


def castilla_leon(c):
    t = leggi(c, "cyl_bocyl_2026.pdf")
    if not t:
        return [], []
    a = t.find("CALENDARIO DE ACTIVIDADES DE LENGUA ESCRITAS")
    esami = []
    for r in t[a:a + 6000].splitlines():
        for i, m in enumerate(re.finditer(LINGUA_RE + r"\s+" + LIVELLO_RE + r"\s+(TARDE|MAÑANA)\s+(\d{1,2}) DE (\w+)", r, re.I)):
            conv = "ordinaria" if m.group(5).lower() != "septiembre" else "extraordinaria"
            esami.append(rec("Castilla y León", 2026, conv, norm_lingua(m.group(1)), m.group(2),
                             iso(2026, m.group(5), m.group(4)), m.group(3).lower(), "cyl_bocyl_2026.pdf"))
    tappe = []
    m = re.search(r"plazo para la presentación de solicitudes será el comprendido entre los días (\d{1,2})\s+a (\d{1,2}) de (\w+) de (\d{4})",
                  re.sub(r"\s+", " ", t))
    if m:
        tappe.append(dict(comunita="Castilla y León", tipo="iscrizione", data=iso(m.group(4), m.group(3), m.group(1)),
                          fine=iso(m.group(4), m.group(3), m.group(2)), fonte="cyl_bocyl_2026.pdf"))
    return esami, tappe


def castilla_mancha(c):
    t = leggi(c, "clm_docm_2026.pdf")
    if not t:
        return [], []
    a = t.find("Calendario de pruebas de certificación\n")
    if a < 0:
        a = t.find("Calendario de pruebas de certificación")
    b = t.find("Anexo II", a)
    righe = t[a:b].splitlines()
    stato = {"mese": None}

    def intest(i, rr):
        r = rr[i].strip()
        if r in ("Mayo", "Junio") or r.endswith("Septiembre"):
            stato["mese"] = r.split()[-1].lower()
            return None
        if re.fullmatch(r"\d{1,2}(\s+\d{1,2}){2,4}", r) and stato["mese"]:
            return [(m.start(), iso(2026, stato["mese"], m.group(0))) for m in re.finditer(r"\d{1,2}", rr[i])]
        return None

    col = griglia(righe, intest, "sinistra")
    esami = []
    for data, testo in col.items():
        testo = re.sub(r"Español\s+lengua\s+extranjera", "Español", testo)
        for m in re.finditer(r"(\d{1,2}):?\s?(\d{2}):?\s+" + LIVELLO_RE + r"\s+" + LINGUA_RE, testo, re.I):
            conv = "extraordinaria" if data[5:7] == "09" else "ordinaria"
            esami.append(rec("Castilla-La Mancha", 2026, conv, norm_lingua(m.group(4)), m.group(3), data,
                             f"{int(m.group(1)):02d}:{m.group(2)}", "clm_docm_2026.pdf"))
    return esami, []


def navarra(c):
    t = leggi(c, "nav_anexo2_2027.pdf")
    if not t:
        return [], []
    righe = t.splitlines()
    # colonne: ordinaria (sinistra), solo EOIDNA aprile/maggio (centro), straordinaria (destra)
    x_eoidna = next(r.find("abril/mayo") for r in righe if "abril/mayo" in r)
    x_extra = next(r.find("EXTRAORDINARIA") for r in righe if "EXTRAORDINARIA" in r)
    esami = []
    for lingua, lv, conv, d, r in blocchi(righe, r"(\d{1,2}/\d{1,2})(?!/)",
                                          [(0, "ordinaria"), (x_eoidna - 3, "ordinaria (solo EOIDNA, parte scritta anticipata)"),
                                           (x_extra - 3, "extraordinaria")]):
        g, m_ = d.split("/")
        nota = "solo EOI Tudela" if "EOIT" in r and conv == "ordinaria" and d == "8/5" else ""
        esami.append(rec("Navarra", 2027, conv, lingua, lv, iso(2027, m_, g), "", "nav_anexo2_2027.pdf", nota))
    return esami, []


def asturias(c):
    t = leggi(c, "ast_bopa_2026.pdf")
    if not t:
        return [], []
    a = t.find("CONVOCATORIA ORDINARIA")
    b = t.find("Horario de celebración", a)
    if b < 0:
        b = t.find("Decimoctavo", a)
    esami = []
    conv, livelli, lingue, date = None, [], [], []

    def chiudi():
        for k, d in enumerate(date):
            for lg in lingue[2 * k:2 * k + 2]:
                for lv in livelli:
                    esami.append(rec("Principado de Asturias", 2026, conv, lg[0], lv, d, lg[1], "ast_bopa_2026.pdf"))

    for r in t[a:b].splitlines():
        if "CONVOCATORIA ORDINARIA" in r or "CONVOCATORIA EXTRAORDINARIA" in r:
            if livelli:
                chiudi()
            conv = "ordinaria" if "ORDINARIA" in r and "EXTRA" not in r else "extraordinaria"
            livelli, lingue, date = [], [], []
            continue
        m = re.findall(r"Nivel \w+ " + LIVELLO_RE, r)
        if m:
            if livelli:
                chiudi()
            livelli, lingue, date = m, [], []
            continue
        if "Bloque 2" in r or "A partir del" in r:
            continue
        md = re.search(r"(\d{1,2}) de (\w+) de (\d{4})\.", r)
        if md and livelli:
            date.append(iso(md.group(3), md.group(2), md.group(1)))
        ml = re.search(r"\b(Alemán|Francés|Inglés|Italiano)\s+(Mañana|Tarde)\b", r)
        if ml and livelli:
            lingue.append((norm_lingua(ml.group(1)), ml.group(2).lower()))
    if livelli:
        chiudi()
    # Le tappe di Asturias (apartado decimosexto) sono in una tabella a due colonne con il testo
    # di destra sfalsato rispetto alla data: la lettura automatica attribuiva male 3 righe su 4,
    # quindi non le estraggo (servirebbe una regola scritta a mano per questo documento).
    tappe = []
    return esami, tappe


LETTORI = [madrid, pais_vasco, cataluna, andalucia, valencia, canarias, murcia, baleares,
           aragon, castilla_leon, castilla_mancha, navarra, asturias]


def main(cartella, uscita):
    tutti, tappe = [], []
    for f in LETTORI:
        e, tp = f(cartella)
        tutti += e
        tappe += tp
    conta = {}
    for r in tutti:
        k = r["comunita"]
        conta[k] = conta.get(k, 0) + 1
    with open(uscita, "w", encoding="utf-8") as fh:
        json.dump({"esami": tutti, "tappe": tappe, "conteggio_esami": conta}, fh, ensure_ascii=False, indent=1)
    for k, v in conta.items():
        print(f"{k:<24} {v:>4} date d'esame   {sum(1 for t in tappe if t['comunita'] == k)} tappe")
    print("totale", len(tutti), "date d'esame,", len(tappe), "tappe")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
