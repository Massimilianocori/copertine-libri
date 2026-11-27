"""Paga CCNL, pacchetto d'inverno del 27/11/2026 (studio-business/schede/2026-11-27-pagaccnl-inverno.md).

Dodici pagine, scritte da genera.py (che passa se stesso come G):
    /preavviso/                 indice: giorni di preavviso di dimissioni e licenziamento nei 5 contratti
    /preavviso/<contratto>/     giorni per livello e anzianità com'è scritto nel contratto, decorrenza, indennità sostitutiva in euro
    /tredicesima/               indice e calcolo (contratto, livello, mesi lavorati, part time)
    /tredicesima/<contratto>/   importo lordo per livello, dodicesimi, part time, quando si paga; quattordicesima dove esiste
più il riquadro «Preavviso e tredicesima» nelle pagine livello e contratto (riquadro(), fuori dall'impronta del lastmod).

Regole: i giorni e le frasi vengono solo da dati/inverno.json, cioè dal testo del contratto salvato in raccolta/_grezzi (mai da
siti terzi); ogni cifra in euro è calcolata dal minimo verificato su due fonti (G.valori), con la formula scritta in pagina;
niente netto e niente stime fiscali. Dove il contratto non scrive come passare dai giorni agli euro, la pagina lo dice e
dichiara il conto usato (mese di 30 giorni). Il calcolo del browser (JS_CALCOLO) usa window.PagaCCNL di stile.APP_JS;
verifica.py lo esegue con node per ogni livello e ogni numero di mesi e lo confronta con un ricalcolo da dati/estratti.json.
"""
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import genera_annuncio as AN

DATI = Path(__file__).resolve().parent / "dati"
I = json.loads((DATI / "inverno.json").read_text(encoding="utf-8"))
CI = I["contratti"]
AGGIORNATO = date.fromisoformat(I["aggiornato_il"])
LETTO = I["letto_il"]  # giorno in cui abbiamo letto gli articoli su preavviso e tredicesima (i file sono quelli scaricati al giro mensile)
PROC = I["procedura"]
CONSULENTE = "verifica con il tuo consulente"

P_PRE = "preavviso/"
P_TRE = "tredicesima/"
# nome breve per titoli e link (i nomi lunghi restano quelli di contratti_meta.json)
BREVE = {"terziario": "commercio", "metalmeccanici": "metalmeccanici", "multiservizi": "multiservizi", "logistica": "logistica", "domestico": "colf e badanti"}
CCNL = {"terziario": "CCNL commercio", "metalmeccanici": "CCNL metalmeccanici", "multiservizi": "CCNL multiservizi", "logistica": "CCNL logistica",
        "domestico": "CCNL lavoro domestico"}
PREDEF = {"terziario": "iv", "metalmeccanici": "c3", "multiservizi": "2", "logistica": "c3", "domestico": "cs"}
MESI_TAB = (1, 3, 6, 9)


def p_pre(G, cid):
    return f"{P_PRE}{G.C[cid]['slug']}/"


def p_tre(G, cid):
    return f"{P_TRE}{G.C[cid]['slug']}/"


def ha_14(G, cid):
    return G.C[cid]["mensilita"]["valore"] == 14


# ---------------------------------------------------------------- termini di preavviso (dati/inverno.json)
def tabelle(cid):
    """Le tabelle dei termini di un contratto. Una tabella «deriva» (dimissioni = metà del licenziamento) prende le voci
    dalla tabella di partenza e tiene la frazione scritta nel contratto (num/den)."""
    tt = CI[cid]["preavviso"]["tabelle"]
    per_id = {t["id"]: t for t in tt}
    out = []
    for t in tt:
        if t.get("deriva"):
            b = per_id[t["deriva"]]
            t = dict(b, **t)
        out.append(dict(t, num=t.get("num", 1), den=t.get("den", 1)))
    return out


def voci(tab):
    """[(banda, voce)] nell'ordine del testo."""
    return [(v.get("banda") or g["banda"], v) for g in tab["gruppi"] for v in g["voci"]]


def voce_di(tab, lid, banda):
    return next((v for b, v in voci(tab) if b == banda and lid in v["livelli"]), None)


def termine(v, num=1, den=1):
    """Il termine com'è nel contratto: «2 mesi e 15 giorni», «60 giorni di calendario», «6 giorni lavorativi»."""
    pezzi = []
    if v["mesi"]:
        pezzi.append("1 mese" if v["mesi"] == 1 else f"{v['mesi']} mesi")
    if v["giorni"]:
        pezzi.append(f"{v['giorni']} giorni")
    t = " e ".join(pezzi)
    t += {"lav": " lavorativi", "cal": " di calendario"}.get(v["unita"], "")  # «gg»: il contratto scrive solo mesi e giorni
    if (num, den) == (1, 2):
        chiara = meta_chiara(v)
        return f"la metà di {t}" + (f" ({chiara})" if chiara else "")
    return t


def meta_chiara(v):
    """La metà di un termine quando viene un numero intero: «15 giorni» (metà di 1 mese o di 30 giorni), «1 mese» (metà di 2 mesi).
    Con i giorni dispari (15 giorni, 2 mesi e 15 giorni) la metà non è intera e il contratto non dice come arrotondare: None."""
    if v["giorni"] % 2 or v["unita"] == "lav":
        return None
    mesi, giorni = v["mesi"] // 2, v["giorni"] // 2 + (15 if v["mesi"] % 2 else 0)
    return " e ".join((["1 mese" if mesi == 1 else f"{mesi} mesi"] if mesi else []) + ([f"{giorni} giorni"] if giorni else []))


def peso(v, num=1, den=1):
    return (v["mesi"] * 30 + v["giorni"]) * num / den


def sintesi(tab, livelli):
    """«da 15 a 120 giorni di calendario» per i livelli pubblicati, oppure il termine unico."""
    vv = [v for _, v in voci(tab) if set(v["livelli"]) & livelli]
    if not vv:
        return ""
    lo, hi = min(vv, key=peso), max(vv, key=peso)
    a, b = termine(lo), termine(hi)
    testo = a if a == b else (f"da {a.replace(' giorni di calendario', '')} a {b}" if a.endswith("giorni di calendario") and b.endswith("giorni di calendario") else f"da {a} a {b}")
    return "la metà dei termini del licenziamento" if (tab["num"], tab["den"]) == (1, 2) else testo


def ind_cent(m, v, num=1, den=1, div=30, ratei=0):
    """Indennità sostitutiva in centesimi dal minimo mensile m (centesimi), mezzo centesimo verso l'alto.
    mens: mensilità scritte nel contratto (metalmeccanici); giorni lavorativi: quota giornaliera del contratto (div 22 o 26);
    mesi e giorni di calendario: mese di 30 giorni. ratei: mensilità annue (14) se il contratto dice di contare i ratei
    (un dodicesimo di tredicesima e uno di quattordicesima per ogni mese: importo × 14 ÷ 12)."""
    if v.get("mens"):
        n, d = m * int(Decimal(v["mens"]) * 100) * num, 100 * den
    elif v["unita"] == "lav":
        n, d = m * v["giorni"] * num, div * den
    else:
        n, d = m * (v["mesi"] * 30 + v["giorni"]) * num, 30 * den
    c = (2 * n + d) // (2 * d)
    return (2 * c * ratei + 12) // 24 if ratei else c  # con i ratei: l'importo già arrotondato × mensilità ÷ 12


def formula(G, m, v, num=1, den=1, div=30):
    """La formula scritta, con le cifre: «1.234,56 € ÷ 30 × 15»."""
    e = G.euro(G.da_cent(m))
    meta = " ÷ 2" if (num, den) == (1, 2) else ""
    if v.get("mens"):
        return f"{e} × {v['mens'].replace('.', ',')}{meta}"
    if v["unita"] == "lav":
        return f"{e} ÷ {div} × {v['giorni']}{meta}"
    if v["mesi"] and not v["giorni"]:
        return f"{e} × {v['mesi']}{meta}"
    if v["mesi"]:
        return f"{e} × {v['mesi']} + {e} ÷ 30 × {v['giorni']}{meta}"
    return f"{e} ÷ 30 × {v['giorni']}{meta}"


# ---------------------------------------------------------------- cifre del giorno (le stesse delle pagine livello)
def base(G, cid, L):
    """Minimo del livello nel giorno G.OGGI in centesimi, oppure None se quel giorno la riga in vigore è sospesa
    («Cifra da aggiornare»): su una cifra superata non calcoliamo importi."""
    cur = G.stato_livello(cid, L)[0]
    if not (cur and cur["pubblicabile"]):
        return None
    v = G.valori(cid, L)
    if v["sospese"]:
        return None
    if cid == "domestico":
        return {"m": G.cent(v["conv_tot"]), "o": G.cent(v["oraria"]), "p": {o: G.cent(x) for o, x in v["p"].items()}, "dal": v["dal"], "ind": bool(v["ind"])}
    return {"m": G.cent(v["mensile"]), "p": {o: G.cent(x) for o, x in v["p"].items()}, "dal": v["dal"]}


def prossima_data(G, cid):
    dd = sorted({d for d in (G.prossimo_scatto(cid, L) for L in G.livelli_pubblicati(cid)) if d})
    return dd[0] if dd else None


def a_date(G, cid, nome, fn):
    """Blocco con cifre: quello di oggi e, nascosto fino a quel giorno, quello della prossima data in cui una tabella cambia
    (stesso metodo delle pagine livello: data-fino, data-dal). fn() scrive il blocco con le cifre del giorno G.OGGI.
    Il nome sta in un commento (<!--b:nome--> … <!--/b-->): verifica.py ritrova il blocco e ne ricalcola ogni cifra."""
    def div():
        t = fn()
        return f'<div class="a-data"><!--b:{nome}-->{t}<!--/b--></div>' if t else ""
    oggi = div()
    g = prossima_data(G, cid)
    if not g:
        return oggi
    dopo = G.al_giorno(g, div)
    if dopo == oggi:
        return oggi
    return (G.fino_al(g, oggi) if oggi else "") + G.dal_giorno(g, dopo)


DA_AGG = '<span class="small">da aggiornare</span>'
NOTA_DA_AGG = ('<p class="small">«Da aggiornare»: per quel livello la tabella in vigore non ha ancora passato i nostri due controlli e l\'ultima cifra verificata è superata. '
               'Su una cifra superata non calcoliamo importi: i dettagli sono nella pagina del livello.</p>')


def e_c(G, c):
    return G.euro(G.da_cent(c))


def anno_tabella(G, cid):
    L0 = G.livelli_pubblicati(cid)[0]
    return date.fromisoformat(G.valori(cid, L0)["dal"]).year


# ---------------------------------------------------------------- pezzi comuni
def riquadro(G, cid, L=None):
    """Riquadro «Preavviso e tredicesima» per pagine livello e pagine contratto. Sta tra due commenti (<!--inverno--> …
    <!--/inverno-->): non contiene cifre e non entra nell'impronta del lastmod, come il riquadro dell'annuncio."""
    e14 = " e quattordicesima" if ha_14(G, cid) else ""
    chi = "per colf e badanti" if cid == "domestico" else f"nel {CCNL[cid]}"
    return (f'<!--inverno--><aside class="nota info" aria-label="Preavviso e tredicesima">{G.ico("calendar")}'
            f'<p><strong>Dimissioni, licenziamento, tredicesima.</strong> Quanti giorni di preavviso servono {chi} e quanto vale la tredicesima{e14} di ogni livello: '
            f'<a href="/{p_pre(G, cid)}">giorni di preavviso</a> · <a href="/{p_tre(G, cid)}">tredicesima{e14}</a>.</p></aside><!--/inverno-->')


def cita(G, cid, sez, k, rim):
    """Citazione dal contratto: il testo è quello di dati/inverno.json, tolti solo gli a capo con il trattino."""
    nodo = CI[cid][sez]
    c = nodo["quattordicesima"]["cit"][k[3:]] if k.startswith("14:") else nodo["cit"][k]
    return (f'<blockquote class="legge" data-cit="{cid}/{sez}/{k}"><p>«{G.h(G.pulisci_citazione(c["testo"]))}»</p>'
            f'<cite>{G.h(CCNL[cid])}, {G.h(c["dove"])}{rim.ref(c.get("fonte") or nodo["fonte"])}</cite></blockquote>')


RINNOVI = {
    # letti il 27/11/2026: ipotesi di accordo dei metalmeccanici (51 pagine) e ipotesi del multiservizi (14 pagine), per intero
    "metalmeccanici": ("Nel rinnovo del 22 novembre 2025, che abbiamo letto, {art} non {sono} tra quelli modificati.", {"preavviso": ("l'articolo sul preavviso", "è"), "tredicesima": ("l'articolo sulla tredicesima", "è")}),
    "multiservizi": ("L'ipotesi di rinnovo del 13 giugno 2025, che abbiamo letto, riscrive gli articoli 1, 33, 51, 52-bis, 72 e 73 (più il 73-bis e il 73-ter): {art} non {sono} tra questi. "
                     "Il rinnovo dell'8 giugno 2021 non lo abbiamo: non possiamo escludere modifiche.",
                     {"preavviso": ("l'articolo 57 sul preavviso", "è"), "tredicesima": ("gli articoli 20 e 21 su tredicesima e quattordicesima", "sono")}),
}


def nota_testo(G, cid, sez):
    """Quale testo leggiamo, subito sotto «In breve». Per i contratti con un rinnovo più recente del testo completo diciamo cosa
    abbiamo controllato nel rinnovo e cosa non abbiamo."""
    m = G.C[cid]
    t = G.FONTI_DEF[m["testo"]["fonte"]]["titolo"]
    if cid in RINNOVI:
        frase, per = RINNOVI[cid]
        art, sono = per[sez]
        extra = (" Per il part time citiamo l'articolo 33 nel testo del 2025." if (cid, sez) == ("multiservizi", "tredicesima") else "")
        return G.nota(f'<strong>Quale testo leggiamo.</strong> Le frasi vengono da: {G.h(t)}. È l\'ultimo testo completo del contratto che abbiamo. '
                      f'{frase.format(art=art, sono=sono)}{extra} Prima di decidere, {CONSULENTE} o con il sindacato.', "", "alert")
    return f'<p class="small">Le frasi vengono da: {G.h(t)}.</p>'


def fonti_box(G, rim, fonti):
    """Elenco delle fonti. Per i testi dei contratti citati in queste pagine la data è quella in cui abbiamo letto gli articoli
    (dati/inverno.json, letto_il); il file è quello scaricato al giro mensile, e lo diciamo."""
    out = rim.elenco()
    for fid in fonti:
        tit = G.h(G.FONTI_DEF[fid]["titolo"])
        i = out.find(tit)
        if i < 0:
            continue
        j = out.index("</li>", i)
        scaricato = G.data_lunga(G.FONTI[fid]["letto_il"])
        out = out[:i] + out[i:j].replace(f"Letto il {scaricato}.", f"Letto il {G.data_lunga(LETTO)}: articoli citati in questa pagina (file scaricato il {scaricato}).") + out[j:]
    # una sola riga con le due date, dette per quello che sono: i minimi del giro mensile, gli articoli letti per queste pagine
    vecchia = f"Controllato il {G.data_lunga(G.CONTROLLO)}."
    assert vecchia in out
    return out.replace(vecchia, f"Articoli del contratto letti il {G.data_lunga(LETTO)}; minimi in euro del giro di controllo del {G.data_lunga(G.CONTROLLO)}.")


def ferie_malattia(G, cid, rim):
    """Cosa dicono i testi che abbiamo su ferie, malattia e infortunio durante il preavviso: solo frasi citate; dove non c'è, lo diciamo."""
    c = CI[cid]["preavviso"]["cit"]
    out = ""
    for k, intro in (("ferie", "Sulle ferie il contratto dice:"), ("malattia", "Sulla malattia il contratto dice:"), ("infortunio", "Sull'infortunio:")):
        if k in c:
            out += f"<p>{intro}</p>" + cita(G, cid, "preavviso", k, rim)
    if cid == "terziario":
        return (out + '<p class="small">Sulle ferie durante il preavviso non c\'è una frase né negli articoli sul preavviso (251, 252 e 256) né in quelli sulle ferie (dal 162 al 168). '
                f'Non la aggiungiamo noi: se ti serve, {CONSULENTE} o con il sindacato.</p>')
    manca = [n for k, n in (("ferie", "le ferie"), ("malattia", "la malattia")) if k not in c]
    if manca:
        out += (f'<p class="small">Per {" e ".join(manca)} durante il preavviso non riportiamo altre frasi: le regole generali stanno negli articoli del contratto su quel tema, che qui non leggiamo.</p>')
    return out


def altri_contratti(G, cid, percorso, cosa):
    return ('<ul class="livelli">' + "".join(f'<li><a href="/{percorso(G, c)}"' + (' aria-current="page"' if c == cid else "") + f'>{cosa} {G.h(BREVE[c])}</a></li>'
                                             for c in G.ORDINE) + "</ul>")


def nomi_livelli(G, cid, ids):
    pub = [L for L in G.livelli_pubblicati(cid) if L["id"] in ids]
    return ", ".join(G.nome_corto(L) for L in pub)


# ---------------------------------------------------------------- 1. preavviso: pagina del contratto
INTRO_PRE = {
    "terziario": ("Nel commercio i giorni di preavviso cambiano per tre cose: chi chiude il rapporto (tu o l'azienda), il tuo livello e gli anni di servizio. "
                  "Per questo trovi numeri diversi da un sito all'altro: spesso è una riga sola di una tabella che ne ha ventiquattro. Qui sotto ci sono tutte, prese dal testo del contratto."),
    "metalmeccanici": ("Nell'industria metalmeccanica il preavviso è lo stesso per dimissioni e licenziamento. Cambia con il livello e con gli anni di servizio. "
                       "Il contratto scrive anche a quante mensilità corrisponde l'indennità se il preavviso non viene dato."),
    "multiservizi": ("Nel contratto delle pulizie e del multiservizi il preavviso dipende da due cose: se sei impiegato o operaio, e chi chiude il rapporto. "
                     "Per gli impiegati contano anche il livello e gli anni di servizio. Per gli operai il termine è uno solo."),
    "logistica": ("Nel contratto della logistica il preavviso cambia con la tua qualifica: impiegato o quadro, operaio, personale viaggiante. "
                  "Per impiegati e quadri contano il livello e gli anni di servizio; chi si dimette ha i termini ridotti della metà."),
    "domestico": ("Per colf, badanti e baby sitter il preavviso non dipende dal livello. Dipende dalle ore a settimana (25 o più, oppure meno di 25), "
                  "dagli anni con la stessa famiglia e da chi chiude il rapporto."),
}
DECORRE = {
    "terziario": ("Nel commercio il preavviso non parte dal giorno in cui consegni la lettera. Parte dal 1° o dal 16 del mese. "
                  "Esempio: se le dimissioni arrivano il 5, i giorni si contano dal 16; se arrivano il 20, dal 1° del mese dopo.", ["decorre", "decorre_dim"]),
    "metalmeccanici": ("Il preavviso si conta dal giorno dopo quello in cui la lettera di dimissioni o di licenziamento viene ricevuta. Non ci sono date fisse nel mese.", ["decorre"]),
    "multiservizi": ("Il contratto dice che i termini partono dalla metà e dalla fine del mese. Non scrive altro: se la tua data cade in mezzo, chiedi all'azienda o al sindacato come viene contata.", ["decorre"]),
    "logistica": ("Per impiegati e quadri il preavviso parte dal giorno 1 o dal giorno 16 del mese. Per operai e personale viaggiante parte da qualsiasi giorno della settimana.",
                  ["decorre", "operai"]),
    "domestico": ("L'articolo 40 non fissa un giorno del mese da cui contare. Scrive i giorni di calendario del preavviso e basta. "
                  "Conviene comunicare per iscritto, con una data certa.", []),
}
COME_IND = {
    "terziario": ("Il contratto dice a quale retribuzione corrisponde l'indennità (la retribuzione di fatto del periodo di preavviso, con i ratei di tredicesima e quattordicesima), "
                  "ma non scrive come passare dai giorni di calendario agli euro. <strong>Il conto che facciamo noi</strong>: minimo mensile ÷ 30 × giorni di preavviso. "
                  "Usiamo il mese di 30 giorni perché la retribuzione mensile copre tutti i giorni del mese di calendario. In busta paga il conto può essere fatto in un altro modo, "
                  "per esempio con la quota giornaliera sui giorni lavorativi del periodo: il risultato può cambiare di qualche euro.", ["indennita", "mese", "giornaliera"]),
    "metalmeccanici": ("Qui non serve nessuna ipotesi: il contratto scrive a quante mensilità corrisponde l'indennità per ogni termine di preavviso. "
                       "<strong>Il conto</strong>: minimo mensile × mensilità scritte nella tabella del contratto.", ["indennita"]),
    "multiservizi": ("Il contratto dice che l'indennità è pari alla retribuzione globale del periodo di preavviso, ma non scrive come passare dai mesi e dai giorni di calendario agli euro. "
                     "<strong>Il conto che facciamo noi</strong>: un mese di preavviso = una mensilità; un giorno di calendario = minimo mensile ÷ 30. "
                     "In busta paga il conto può essere fatto in un altro modo, per esempio con la quota giornaliera del contratto sui giorni lavorativi del periodo: il risultato può cambiare di qualche euro.",
                     ["indennita", "giornaliera"]),
    "logistica": ("Il contratto dice che l'indennità è pari alla retribuzione del periodo di preavviso. <strong>Il conto che facciamo noi</strong>: un mese di preavviso = una mensilità; "
                  "un giorno di calendario = minimo mensile ÷ 30 (il contratto non lo scrive: è il mese di 30 giorni). Per i sei giorni lavorativi degli operai usiamo la retribuzione giornaliera "
                  "scritta nel contratto: minimo ÷ 22, oppure ÷ 26 per chi non viaggia e lavora su sei giorni.", ["indennita", "giornaliera"]),
    "domestico": ("Qui il contratto scrive la regola: quando parla di «giorni di calendario» si contano i trentesimi della mensilità. "
                  "<strong>Il conto</strong>: retribuzione mensile ÷ 30 × giorni di preavviso. Per chi lavora a ore la retribuzione mensile è paga oraria × ore a settimana × 52 ÷ 12.",
                  ["indennita", "trentesimi", "ore"]),
}
ALTRE = {
    "terziario": [("Se il preavviso non lo dai tu, l'azienda può trattenere la stessa somma dalle tue competenze.", "trattenuta"),
                  ("Se chiedi di andare via subito, l'azienda può rinunciare al preavviso.", "rinuncia"),
                  ("Se invece è l'azienda a chiudere prima della fine del preavviso che hai dato, ti deve l'indennità per i giorni che restano.", "anticipo")],
    "metalmeccanici": [("Durante il preavviso di licenziamento hai diritto a permessi per cercare un altro lavoro.", "permessi"), ("Dimissioni e licenziamento vanno comunicati per iscritto.", "scritto")],
    "multiservizi": [("Se il preavviso non lo dai tu, l'azienda può trattenere la retribuzione di quel periodo.", "trattenuta"),
                     ("Chi riceve la disdetta può chiudere il rapporto anche prima, senza pagare il resto del preavviso.", "troncare")],
    "logistica": [("Se il preavviso non lo dai tu, l'azienda può trattenere la retribuzione di quel periodo.", "trattenuta"),
                  ("Chi riceve la disdetta può chiudere il rapporto anche prima, senza pagare il resto del preavviso.", "troncare"),
                  ("Durante il preavviso hai diritto a permessi per cercare un altro lavoro.", "permessi")],
    "domestico": [("Se la famiglia licenzia entro 30 giorni dalla fine del congedo di maternità, i termini raddoppiano.", "maternita"),
                  ("Chi ha un alloggio indipendente dato dalla famiglia (portieri privati, custodi di villa) ha termini più lunghi.", "portieri"),
                  ("Se ti dimetti per giusta causa, l'indennità di mancato preavviso spetta a te.", "giusta_causa")],
}
PARTTIME_PRE = {
    "terziario": ("Per il part time i giorni di preavviso sono gli stessi del tempo pieno e si contano in giorni di calendario. L'indennità segue la tua retribuzione: "
                  "per il part time parti dal minimo riproporzionato alle tue ore, che trovi nella pagina del tuo livello.", "parttime"),
}
BASI = {  # lavoro domestico: su quale retribuzione mensile si calcola l'indennità in tabella
    "lic25": [("Chi convive", "m"), ("A ore, 30 ore", 30)],
    "dim25": [("Chi convive", "m"), ("A ore, 30 ore", 30)],
    "meno25": [("A ore, 20 ore", 20)],
}


def tab_termini(G, cid, tab):
    """Tabella dei termini com'è nel contratto: una riga per gruppo di livelli, una colonna per fascia di anzianità."""
    bande = tab["bande"]
    righe, visti = [], []
    for _, v in voci(tab):
        if v["et"] in visti:
            continue
        visti.append(v["et"])
        celle = []
        for b in bande:
            x = next((w for bb, w in voci(tab) if bb == b["id"] and w["et"] == v["et"]), None)
            celle.append(termine(x, tab["num"], tab["den"]) if x else "—")
        righe.append((G.h(v["et"]), *celle))
    return G.tabella(["Chi"] + [G.h(b["et"]) for b in bande], righe, num=[])


def frasi_tabella(tab):
    """Le frasi del contratto che fanno la tabella. Tabella a matrice (metalmeccanici): intestazione e righe intere, termini e mensilità."""
    if tab.get("intestazione"):
        return [tab["intestazione"]] + [g["frase"] for g in tab["gruppi"]] + [g["frase_mens"] for g in tab["gruppi"]]
    return [v["frase"] for _, v in voci(tab)]


def righe_testo(G, cid, tab):
    """Le righe del contratto, parola per parola (dati/inverno.json): verifica.py le ritrova nel testo salvato."""
    voci_ = "".join(f'<li data-riga="{cid}/{tab["id"]}/{i}">«{G.h(G.pulisci_citazione(x))}»</li>' for i, x in enumerate(frasi_tabella(tab)))
    return f'<details class="testo"><summary>Le righe del contratto, parola per parola ({G.h(tab["dove"])})</summary><ul>{voci_}</ul></details>'


# Intestazioni corte per le tabelle in euro (sul telefono devono stare in 390 px): stesso significato delle fasce del contratto.
BANDA_CORTA = {"Fino a 5 anni di servizio": "Fino a 5 anni", "Fino a 5 anni di servizio compiuti": "Fino a 5 anni", "Oltre 5 e fino a 10 anni": "Oltre 5, fino a 10",
               "Oltre 5 e fino a 10 anni compiuti": "Oltre 5, fino a 10", "Oltre 10 anni": "Oltre 10", "Oltre 10 anni compiuti": "Oltre 10", "Qualsiasi anzianità": "Qualsiasi anzianità",
               "Fino a 5 anni con la stessa famiglia": "Fino a 5 anni", "Fino a 2 anni con la stessa famiglia": "Fino a 2 anni"}
STILE_EURO = ('<style>.t-euro table.dati{font-size:.8rem}.t-euro table.dati th,.t-euro table.dati td{padding:7px 5px}.t-euro table.dati th{white-space:normal;letter-spacing:0}'
              '.t-euro .ratei{display:inline-block;font-size:.72rem;line-height:1.25;color:var(--ink-3)}'
              '.t-euro table.dati td:first-child{overflow-wrap:anywhere}.t-euro.stretta table.dati{font-size:.74rem}.t-euro.stretta table.dati th,.t-euro.stretta table.dati td{padding:7px 3px}'
              '.t-euro.col-min th:nth-child(2),.t-euro.col-min td:nth-child(2){display:none}'
              '@media(min-width:700px){.t-euro table.dati{font-size:.93rem}.t-euro table.dati th,.t-euro table.dati td{padding:9px 12px}.t-euro .ratei br{display:none}'
              '.t-euro.col-min th:nth-child(2),.t-euro.col-min td:nth-child(2){display:table-cell}.t-euro.stretta table.dati{font-size:.93rem}'
              '.t-euro.stretta table.dati th,.t-euro.stretta table.dati td{padding:9px 12px}}</style>')  # sul telefono la colonna «Minimo» è nascosta: la cifra è nella pagina del livello


def tab_euro(G, cid, tab):
    """Indennità in euro per ogni livello pubblicato (cifre del giorno G.OGGI). Dove il contratto dice che l'indennità comprende
    i ratei di tredicesima e quattordicesima (commercio art. 252, logistica artt. 18-19), ogni termine ha anche la colonna «con i ratei»."""
    rr = CI[cid]["preavviso"]["ratei"]
    varianti = (0, rr["mensilita"]) if rr else (0,)
    bande = tab["bande"]
    basi = BASI.get(tab["id"]) if cid == "domestico" else [("", "m")]
    lav = any(v["unita"] == "lav" for _, v in voci(tab))
    cols = [(bn, bk, b, d) for bn, bk in basi for b in bande for d in ((22, 26) if lav else (30,))]
    righe, manca = [], False
    for L in G.livelli_pubblicati(cid):
        if not any(L["id"] in v["livelli"] for _, v in voci(tab)):
            continue
        s = base(G, cid, L)
        r = [f'<a href="/{G.pagina_url(cid, L)}">{G.h(L["nome"])}</a>']
        if len(basi) == 1 and cid != "domestico":
            r.append(e_c(G, s["m"]) if s else DA_AGG)
        for _, bk, b, d in cols:
            v = voce_di(tab, L["id"], b["id"])
            if not v:
                r.append("—")
            elif not s:
                r.append(DA_AGG)
                manca = True
            else:
                mc = s["m"] if bk == "m" else s["p"][bk]
                r.append(e_c(G, ind_cent(mc, v, tab["num"], tab["den"], d))
                         + (f'<br><span class="ratei">con ratei <br>{e_c(G, ind_cent(mc, v, tab["num"], tab["den"], d, rr["mensilita"]))}</span>' if rr else ""))
        righe.append(r)
    if not righe:
        return ""
    intest = ["Livello"] + (["Minimo al mese"] if len(basi) == 1 and cid != "domestico" else [])
    for bn, _, b, d in cols:
        et = BANDA_CORTA.get(b["et"], b["et"])
        if lav:
            et = f"Giornata ÷ {d}"
        intest.append(G.h(f"{bn}: {et[0].lower() + et[1:]}" if bn else et))
    una = len(basi) == 1 and cid != "domestico"
    if una:
        intest[1] = "Minimo"
    return f'<div class="t-euro{" col-min" if una else (" stretta" if len(cols) > 3 else "")}">{G.tabella(intest, righe)}</div>' + (NOTA_DA_AGG if manca else "")


def esempio_ind(G, cid):
    """Un conto svolto, con le cifre del giorno."""
    es = CI[cid]["preavviso"]["esempio"]
    tab = next(t for t in tabelle(cid) if t["id"] == es["tabella"])
    L = next(x for x in G.C[cid]["livelli"] if x["id"] == es["livello"])
    s = base(G, cid, L)
    v = voce_di(tab, L["id"], es["banda"])
    if not s or not v:
        return ""
    banda = next(b["et"] for b in tab["bande"] if b["id"] == es["banda"])
    chi = f'{L["nome"]}{", convivente" if cid == "domestico" else ""}, {banda[0].lower() + banda[1:]}: preavviso di {termine(v, tab["num"], tab["den"])}'
    div = 22 if v["unita"] == "lav" else 30
    out = (f'<div class="formula">{formula(G, s["m"], v, tab["num"], tab["den"], div)} = <strong>{e_c(G, ind_cent(s["m"], v, tab["num"], tab["den"], div))}</strong> lordi'
           f'<small>{G.h(chi)}. Minimo del livello in vigore dal {G.data_lunga(s["dal"])}.</small></div>')
    r = CI[cid]["preavviso"]["ratei"]
    if r:
        out += (f'<div class="formula">{e_c(G, ind_cent(s["m"], v, tab["num"], tab["den"], div))} × {r["mensilita"]} ÷ 12 = '
                f'<strong>{e_c(G, ind_cent(s["m"], v, tab["num"], tab["den"], div, r["mensilita"]))}</strong> lordi'
                f'<small>Lo stesso caso con i ratei di tredicesima e quattordicesima: ogni mese matura un dodicesimo di ciascuna, quindi il conto si moltiplica per {r["mensilita"]} e si divide per 12.</small></div>')
    return out


def pagina_preavviso(G, cid):
    m, p = G.C[cid], CI[cid]["preavviso"]
    rim = G.Rimandi()
    fa, fb = m["fonte_a"], m["fonte_b"]
    pub = {L["id"] for L in G.livelli_pubblicati(cid)}
    tt = tabelle(cid)
    lic = [t for t in tt if t["caso"] in ("licenziamento", "entrambi")]
    dim = [t for t in tt if t["caso"] in ("dimissioni", "entrambi")]

    def elenco(lista):
        return "; ".join((f'{t["chi"]}: ' if t.get("chi") else "") + sintesi(t, pub) for t in lista if sintesi(t, pub))
    corpo = (f'<div class="card pull testo"><p><strong>In breve.</strong> {INTRO_PRE[cid]}</p><ul>'
             f'<li><strong>Se ti licenziano</strong>: {G.h(elenco(lic))}.</li>'
             f'<li><strong>Se ti dimetti</strong>: {G.h(elenco(dim))}.</li>'
             f'<li><strong>Da quando si conta</strong>: {G.h(p["decorre_breve"])}.</li>'
             f'<li><strong>Dove sta scritto</strong>: {G.h(p["dove"])}.{rim.ref(p["fonte"])}</li></ul></div>')
    corpo += nota_testo(G, cid, "preavviso")
    corpo += '<h2 id="giorni">Quanti giorni di preavviso</h2>'
    if "regola" in p["cit"]:
        corpo += "<p>Il contratto parte da questa regola:</p>" + cita(G, cid, "preavviso", "regola", rim)
    for t in tt:
        corpo += f'<h3 id="t-{t["id"]}">{G.h(t["titolo"])}</h3>'
        if t.get("deriva"):
            corpo += ("<p>Il contratto non scrive una seconda tabella: dice che i termini del licenziamento si riducono. La frase è questa:</p>" + cita(G, cid, "preavviso", t["cit"], rim))
        corpo += tab_termini(G, cid, t)
        if not t.get("deriva"):
            corpo += righe_testo(G, cid, t)
    if cid == "terziario":
        corpo += ('<p class="small">Nel testo depositato il 2° livello è scritto «Il» al posto di «II»: nelle righe qui sopra lo riportiamo com\'è. '
                  'Gli anni «compiuti» sono gli anni di servizio interi.</p>')
    if cid == "multiservizi":
        corpo += ('<p class="small">L\'articolo nomina gli impiegati dal 2° livello in su e gli «operai di qualsiasi livello». '
                  'Se non sai se sei inquadrato come impiegato o come operaio, lo trovi nella lettera di assunzione e in busta paga. '
                  'Nelle tabelle in euro degli operai mettiamo i livelli dal 1° al 5°: per il 6° e il 7° la declaratoria del contratto parla di funzioni di concetto e direttive.</p>')
    if cid == "metalmeccanici":
        corpo += ('<p class="small">La tabella del contratto è una sola e vale per chi si dimette e per chi viene licenziato: il titolo dell\'articolo è «Preavviso di licenziamento e di dimissioni». '
                  'Per i livelli D1, D2 e C1 il contratto scrive «10 giorni» e «20 giorni» senza dire se sono di calendario o lavorativi; la sua tabella dell\'indennità li fa valere 0,33 e 0,67 mensilità.</p>')
    if cid == "domestico":
        corpo += ('<p>La frase sulla riduzione per le dimissioni è scritta subito dopo i termini dei rapporti di almeno 25 ore:</p>' + cita(G, cid, "preavviso", "dimissioni", rim)
                  + '<p class="small">Per i rapporti sotto le 25 ore il testo non scrive una riduzione: per questo la tabella qui sopra dà gli stessi giorni a chi si dimette e a chi viene licenziato. '
                  'La metà di 15 giorni non è un numero intero: come si arrotonda il contratto non lo dice.</p>')
    nn = p.get("non_nominati")
    if nn:
        nomi = nomi_livelli(G, cid, nn["livelli"])
        corpo += G.nota(f'<strong>Driver e rider ({G.h(nomi)}).</strong> L\'articolo 36 nomina il personale viaggiante delle qualifiche 3 e 2 e, in generale, «gli operai non in prova». '
                        f'Non nomina la qualifica 1 (parametri G e H) né le lettere I e L. Non scegliamo noi quale riga vale: chiedilo all\'azienda o al sindacato e {CONSULENTE}.', "", "alert")
        corpo += cita(G, cid, "preavviso", "viaggianti", rim)
        corpo += ('<p class="small">Nelle tabelle in euro degli operai mettiamo i livelli dal 3° Super al 6°: per il 1° e il 2° livello la declaratoria del contratto (art. 6) '
                  'parla di impiegati con funzioni direttive e di mansioni di concetto. Conta sempre la qualifica scritta nella tua lettera di assunzione.</p>')
    # decorrenza
    testo_d, chiavi = DECORRE[cid]
    corpo += f'<h2 id="decorrenza">Da quando parte il preavviso</h2><p>{testo_d}</p>' + "".join(cita(G, cid, "preavviso", k, rim) for k in chiavi)
    corpo += G.AD
    # indennità
    testo_i, chiavi = COME_IND[cid]
    corpo += '<h2 id="indennita">Indennità sostitutiva del preavviso: quanto vale</h2>'
    corpo += ('<p>Se il preavviso non viene dato, o non viene lavorato fino in fondo, chi chiude il rapporto paga all\'altro una somma al posto dei giorni mancanti: '
              'è l\'indennità sostitutiva del preavviso. Vale nei due sensi: la deve il datore di lavoro se ti licenzia senza preavviso, la devi tu se ti dimetti senza darlo.</p>')
    corpo += cita(G, cid, "preavviso", chiavi[0], rim)
    corpo += f'<div class="testo"><p>{testo_i}</p></div>' + "".join(cita(G, cid, "preavviso", k, rim) for k in chiavi[1:])
    corpo += a_date(G, cid, "esempio", lambda: esempio_ind(G, cid))
    r = p["ratei"]
    if r and cid == "logistica":
        corpo += ('<p>Il contratto dice anche che tredicesima e quattordicesima contano per l\'indennità di preavviso:</p>'
                  + cita(G, cid, "preavviso", "ratei13", rim) + cita(G, cid, "preavviso", "ratei14", rim))
    corpo += (f'<p><strong>Sono importi minimi e lordi.</strong> Li calcoliamo sul minimo del livello, la cifra che questo sito verifica su due fonti{rim.ref([fa, fb])}. '
              'La tua indennità è più alta se in busta paga hai scatti di anzianità, superminimi o altre voci fisse'
              + '. Tasse e contributi non li calcoliamo.</p>'
              + ('<p>Nelle tabelle ogni termine ha due cifre: la prima è sul solo minimo; la seconda, «con i ratei», aggiunge i dodicesimi di tredicesima e quattordicesima '
                 f'che il contratto dice di contare nell\'indennità (× {r["mensilita"]} ÷ 12, come nel secondo conto qui sopra). '
                 'Le fasce sono quelle della tabella dei giorni: fino a 5 anni di servizio, oltre 5 e fino a 10, oltre 10.</p>' if r else "")
              + STILE_EURO)
    for t in tt:
        def blocco(t=t):
            te = tab_euro(G, cid, t)
            return (f'<h3>Indennità sul minimo – {G.h(t["titolo"][0].lower() + t["titolo"][1:])}</h3>' + te) if te else ""
        corpo += a_date(G, cid, f"euro-{t['id']}", blocco)
    if cid == "domestico":
        corpo += ('<p class="small">Per chi convive la base è il minimo mensile della tabella A (con l\'indennità di funzione per i livelli D e DS). '
                  'Per chi lavora a ore la base è paga oraria × ore × 52 ÷ 12: in tabella trovi 30 ore a settimana (rapporto di almeno 25 ore) e 20 ore a settimana (rapporto sotto le 25 ore) come esempi. Gli anni sono quelli con la stessa famiglia. '
                  'Il valore di vitto e alloggio fa parte della retribuzione globale di fatto ma qui non è sommato.</p>' + cita(G, cid, "preavviso", "globale", rim) + G.nota_domestico())
    # part time
    corpo += '<h2 id="part-time">E se lavori part time?</h2>'
    if cid in PARTTIME_PRE:
        corpo += f'<p>{PARTTIME_PRE[cid][0]}</p>' + cita(G, cid, "preavviso", PARTTIME_PRE[cid][1], rim)
    elif cid == "domestico":
        corpo += ('<p>Nel lavoro domestico le ore contano due volte: decidono quale tabella vale (25 ore o più, oppure meno di 25) e decidono la retribuzione su cui si calcola l\'indennità. '
                  'Il minimo per le tue ore lo calcoli nella pagina del tuo livello.</p>')
    else:
        corpo += ('<p>L\'articolo sul preavviso non ha una regola a parte per il part time: i termini sono quelli delle tabelle qui sopra. '
                  'L\'indennità segue la tua retribuzione: parti dal minimo riproporzionato alle tue ore, che trovi nella pagina del tuo livello, e fai lo stesso conto.</p>')
    # altre regole
    corpo += '<h2 id="altro">Altre cose scritte nello stesso articolo</h2>'
    for frase, k in ALTRE[cid]:
        corpo += f"<p>{frase}</p>" + cita(G, cid, "preavviso", k, rim)
    corpo += '<h2 id="ferie">Ferie e malattia durante il preavviso</h2>' + ferie_malattia(G, cid, rim)
    corpo += '<h2 id="limiti">Cosa non trovi in questa pagina</h2><div class="testo"><ul>'
    corpo += ('<li>il periodo di prova, il contratto a termine, l\'apprendistato e i dirigenti: hanno regole proprie;</li>'
              '<li>il licenziamento e le dimissioni per giusta causa;</li>'
              f'<li>come si presentano le dimissioni: la procedura è <a href="/{P_PRE}#procedura">online</a> e non dipende dal contratto;</li>'
              '<li>accordi aziendali o individuali, che possono cambiare i termini;</li>'
              '<li>il netto: tutte le cifre sono lorde.</li></ul>'
              f'<p>Questa pagina riporta il testo del contratto e fa conti dichiarati. Non è una consulenza: prima di firmare o di consegnare una lettera, {CONSULENTE} del lavoro, con il sindacato o con un patronato.</p></div>')
    corpo += (f'<h2 id="vedi">Vedi anche</h2><p>Quanto vale la tredicesima{" e la quattordicesima" if ha_14(G, cid) else ""} con questo contratto: '
              f'<a href="/{p_tre(G, cid)}">tredicesima {G.h(BREVE[cid])}</a>. Il minimo, la paga oraria e gli aumenti di ogni livello:</p>' + G.lista_livelli(cid))
    corpo += '<h3>Il preavviso negli altri contratti</h3>' + altri_contratti(G, cid, p_pre, "Preavviso")
    corpo += fonti_box(G, rim, [p["fonte"]])
    titolo, h1, descr = {
        "terziario": ("Preavviso CCNL commercio: dimissioni e licenziamento per livello", "Preavviso nel CCNL commercio: dimissioni e licenziamento",
                      "Giorni di preavviso del CCNL commercio per livello e anzianità (artt. 251 e 256), da quando partono e indennità sostitutiva in euro sul minimo."),
        "metalmeccanici": ("Preavviso metalmeccanici: giorni per livello e indennità", "Preavviso dei metalmeccanici: dimissioni e licenziamento",
                           "Preavviso del CCNL metalmeccanici industria per livello e anni di servizio, com'è scritto nel contratto, con l'indennità sostitutiva in euro sul minimo."),
        "multiservizi": ("Preavviso CCNL multiservizi e pulizie: giorni e indennità", "Preavviso nel CCNL multiservizi: dimissioni e licenziamento",
                         "Preavviso del CCNL multiservizi e pulizie: operai e impiegati, dimissioni e licenziamento (art. 57), decorrenza e indennità sostitutiva in euro."),
        "logistica": ("Preavviso CCNL logistica e trasporti: giorni e indennità", "Preavviso nel CCNL logistica: dimissioni e licenziamento",
                      "Preavviso del CCNL logistica e trasporto merci: impiegati, operai e personale viaggiante (art. 36), decorrenza e indennità sostitutiva in euro."),
        "domestico": ("Preavviso colf e badanti: giorni di dimissioni e licenziamento", "Preavviso di colf e badanti: dimissioni e licenziamento",
                      "Preavviso di colf e badanti: 8, 15 o 30 giorni secondo ore e anzianità (art. 40), metà per le dimissioni, indennità sostitutiva in euro per livello."),
    }[cid]
    testata = G.banda(f"{m['nome_breve']} · preavviso", h1, f"I giorni di preavviso come li scrive il contratto ({G.h(p['dove'])}), da quando si contano e quanto vale l'indennità sostitutiva sul minimo di ogni livello.",
                      icona="calendar")
    G.pagina(p_pre(G, cid), titolo, descr, corpo, testata, briciole=[("Home", ""), ("Preavviso", P_PRE), (m["nome_breve"], p_pre(G, cid))])


# ---------------------------------------------------------------- 2. preavviso: indice
def indice_preavviso(G):
    rim = G.Rimandi()
    righe = []
    for cid in G.ORDINE:
        m, p = G.C[cid], CI[cid]["preavviso"]
        pub = {L["id"] for L in G.livelli_pubblicati(cid)}
        tt = tabelle(cid)

        def col(casi):
            return "<br>".join(G.h((f'{t["chi"]}: ' if t.get("chi") else "") + sintesi(t, pub)) for t in tt if t["caso"] in casi and sintesi(t, pub))
        righe.append((f'<a href="/{p_pre(G, cid)}">{G.h(m["nome_breve"])}</a>', col(("licenziamento", "entrambi")), col(("dimissioni", "entrambi")),
                      G.h(p["decorre_breve"]), G.h(p["dove"]) + rim.ref(p["fonte"])))
    corpo = ('<div class="card pull testo"><p><strong>In breve.</strong> I giorni di preavviso li scrive il contratto collettivo. '
             'Cambiano da un contratto all\'altro e, dentro lo stesso contratto, con il livello, con gli anni di servizio e con chi chiude il rapporto. '
             'Qui trovi i termini di 5 contratti nazionali, copiati dal testo depositato al CNEL, con l\'articolo e la frase.</p></div>')
    corpo += '<h2 id="tabella">Preavviso nei 5 contratti</h2>'
    corpo += '<p>La tabella dà l\'intervallo, dal termine più corto al più lungo. Nella pagina di ogni contratto ci sono tutte le righe, livello per livello.</p>'
    corpo += G.tabella(["Contratto", "Se ti licenziano", "Se ti dimetti", "Da quando si conta", "Dove sta scritto"], righe, num=[])
    # perché i siti danno numeri diversi: le righe del commercio che valgono 15 e 45 giorni
    def casi_t(g):
        out = []
        for t in tabelle("terziario"):
            for b, v in voci(t):
                if v["giorni"] == g and not v["mesi"]:
                    banda = next(x["et"] for x in t["bande"] if x["id"] == b)
                    out.append(f'{"dimissioni" if t["caso"] == "dimissioni" else "licenziamento"}, {v["et"][0].lower() + v["et"][1:]}, {banda[0].lower() + banda[1:]}')
        return out
    corpo += '<h2 id="numeri">Perché sul commercio trovi «15 giorni» e «45 giorni»</h2><div class="testo">'
    corpo += ('<p>Tutti e due i numeri sono nel contratto del commercio. Sono righe diverse della stessa coppia di tabelle (art. 251 per il licenziamento, art. 256 per le dimissioni). '
              'Chi scrive un numero solo ha scelto una riga.</p><ul>'
              f'<li><strong>15 giorni di calendario</strong> vale per: {G.h("; ".join(casi_t(15)))}.</li>'
              f'<li><strong>45 giorni di calendario</strong> vale per: {G.h("; ".join(casi_t(45)))}.</li></ul>'
              f'<p>Per sapere il tuo numero servono tre dati: livello, anni di servizio compiuti e chi dà il preavviso. La tabella completa è nella pagina del '
              f'<a href="/{p_pre(G, "terziario")}">preavviso del commercio</a>.{rim.ref(CI["terziario"]["preavviso"]["fonte"])}</p></div>')
    corpo += G.AD
    corpo += '<h2 id="controlla">Tre cose da controllare prima di contare i giorni</h2><div class="testo"><ol>'
    corpo += ('<li><strong>La tua qualifica.</strong> In alcuni contratti (multiservizi, logistica) il termine cambia tra impiegati e operai. La qualifica è scritta nella lettera di assunzione e in busta paga.</li>'
              '<li><strong>Gli anni di servizio.</strong> Le fasce sono quasi sempre tre: fino a 5 anni, oltre 5 e fino a 10, oltre 10. Nel lavoro domestico sono due.</li>'
              '<li><strong>Il giorno da cui si conta.</strong> Nel commercio e per gli impiegati della logistica il preavviso parte dal 1° o dal 16 del mese; '
              'nei metalmeccanici dal giorno dopo il ricevimento della lettera. Consegnare la lettera un giorno dopo può spostare l\'inizio del preavviso anche di due settimane.</li></ol></div>')
    fr = PROC["frammenti"]
    corpo += '<h2 id="procedura">Come si presentano le dimissioni: la procedura online</h2>'
    corpo += ('<p>I giorni di preavviso li trovi nel contratto. Il modo di presentare le dimissioni invece è uguale per quasi tutti i lavoratori del settore privato: si fa online. '
              f'Il {G.h(PROC["chi"])} scrive:</p>'
              f'<blockquote class="legge" data-proc="telematiche"><p>«{G.h(fr["telematiche"])}»</p><cite>{G.h(PROC["chi"])}, pagina «{G.h(PROC["titolo"])}»</cite></blockquote>'
              '<div class="testo"><ul><li>Puoi inviare il modulo da solo, dal sito del Ministero, a cui si accede con SPID o CIE.</li>'
              '<li>Oppure puoi rivolgerti a un soggetto abilitato: patronato, organizzazione sindacale, ente bilaterale, commissioni di certificazione, consulenti del lavoro, sedi dell\'Ispettorato Nazionale del Lavoro.</li>'
              '<li>Hai 7 giorni dalla comunicazione per revocare le dimissioni.</li>'
              '<li>La procedura non riguarda il lavoro domestico e il lavoro nelle pubbliche amministrazioni: lo dice la stessa pagina.</li></ul></div>'
              f'<blockquote class="legge" data-proc="revoca"><p>«{G.h(fr["revoca"])}»</p><cite>{G.h(PROC["chi"])}, pagina «{G.h(PROC["titolo"])}»</cite></blockquote>'
              f'<p class="small">Fonte: <a href="{G.h(PROC["url"])}" rel="noopener">{G.h(PROC["titolo"])}</a> · {G.h(PROC["chi"])}. Letto il {G.data_lunga(PROC["letto_il"])}. '
              'La pagina del Ministero spiega la procedura, non i giorni di preavviso.</p>')
    corpo += '<h2 id="ferie">Ferie e malattia durante il preavviso</h2>'
    corpo += '<p>Qui sotto c\'è solo quello che dicono i testi dei contratti che abbiamo letto. Dove una frase non c\'è, lo scriviamo.</p>'
    for c in G.ORDINE:
        corpo += f'<h3>{G.h(G.C[c]["nome_breve"])}</h3>' + ferie_malattia(G, c, rim)
    corpo += '<h2 id="indennita">Indennità sostitutiva: come la calcoliamo</h2><div class="testo">'
    corpo += ('<p>Se il preavviso non viene dato, chi chiude il rapporto deve all\'altro la retribuzione di quel periodo. In ogni pagina trovi l\'importo in euro per livello, calcolato sul minimo che abbiamo verificato su due fonti. '
              'Il conto è sempre scritto:</p><ul>'
              '<li><strong>Metalmeccanici</strong>: il contratto scrive le mensilità (per esempio 1,5 mensilità per un mese e mezzo di preavviso). Minimo × mensilità.</li>'
              '<li><strong>Lavoro domestico</strong>: il contratto dice che i giorni di calendario si contano in trentesimi della mensilità. Minimo ÷ 30 × giorni.</li>'
              '<li><strong>Commercio, multiservizi, logistica</strong>: il contratto non scrive come passare dai giorni agli euro. Usiamo il mese di 30 giorni e lo diciamo in pagina; '
              'per i giorni lavorativi degli operai della logistica usiamo la retribuzione giornaliera del contratto.</li></ul>'
              f'<p>Sono importi minimi e lordi. Non contano scatti, superminimi e premi, e non sono il netto. Prima di decidere, {CONSULENTE} del lavoro o con il sindacato.</p></div>')
    corpo += '<h2 id="contratti">Scegli il tuo contratto</h2><ul class="griglia">' + "".join(
        f'<li><a href="/{p_pre(G, c)}"><b>Preavviso {G.h(BREVE[c])}</b><span>{G.h(G.C[c]["nome"])}</span><span>{G.h(CI[c]["preavviso"]["dove"])}</span></a></li>' for c in G.ORDINE) + "</ul>"
    corpo += ('<h2 id="limiti">Cosa non trovi qui</h2><div class="testo"><ul><li>gli altri contratti: pubblichiamo solo i cinque di cui abbiamo letto il testo;</li>'
              '<li>periodo di prova, contratti a termine, apprendisti e dirigenti;</li>'
              f'<li>il netto e le tasse.</li></ul><p>A dicembre serve anche sapere quanto vale la tredicesima: <a href="/{P_TRE}">tredicesima per contratto e livello, con il calcolo</a>.</p></div>')
    corpo += fonti_box(G, rim, [CI[c]["preavviso"]["fonte"] for c in G.ORDINE])
    testata = G.banda("Dimissioni e licenziamento", "Preavviso di dimissioni e licenziamento",
                      "I giorni di preavviso di 5 contratti nazionali, come li scrive il testo: per livello, anzianità e qualifica. Con l'indennità sostitutiva in euro.", icona="calendar")
    G.pagina(P_PRE, "Preavviso di dimissioni e licenziamento: giorni per contratto",
             "Giorni di preavviso per dimissioni e licenziamento in 5 CCNL: commercio, metalmeccanici, multiservizi, logistica, colf e badanti. Articolo, frase, indennità.",
             corpo, testata, briciole=[("Home", ""), ("Preavviso", P_PRE)])


# ---------------------------------------------------------------- 3. tredicesima: calcolo
def dati_calcolo(G):
    c = {}
    for cid in G.ORDINE:
        m = G.C[cid]
        c[cid] = {"b": m["nome_breve"], "mens": m["mensilita"]["valore"], "dom": 1 if cid == "domestico" else 0, "u": p_tre(G, cid), "q14": Q14_RIGA.get(cid, ""),
                  "l": [{"id": L["id"], "n": L["nome"], "g": L.get("gruppo_nome", ""), "p": AN._passi(G, cid, L)} for L in G.livelli_pubblicati(cid)]}
    return {"ordine": list(G.ORDINE), "c": c}


def calcola(G, D, cid, lid, mesi, modo="pieno", n=0, oggi=None):
    """Il calcolo in Python: stesse formule di JS_CALCOLO (verifica.py confronta il browser con un ricalcolo suo).
    modo: pieno | pct (contratti con divisore); conv | aore (lavoro domestico). Importi in centesimi."""
    oggi = oggi or G.OGGI.isoformat()
    c = D["c"][cid]
    L = next(x for x in c["l"] if x["id"] == lid)
    p = [x for x in L["p"] if not x["dal"] or oggi >= x["dal"]][-1]
    if p.get("no"):
        return None
    if modo == "aore":
        m = G.cent(G.orario52(G.da_cent(p["o"]), n))
    elif modo == "pct":
        m = G.cent(G.prorata(G.da_cent(p["m"]), n, 100))
    else:
        m = p["m"]
    t = G.cent(G.prorata(G.da_cent(m), mesi, 12))
    return {"mensile": m, "tred": t, "rateo": G.cent(G.prorata(G.da_cent(m), 1, 12)), "quatt": t if c["mens"] == 14 else None, "dal": p["t"]}


# Il calcolo usa window.PagaCCNL (stile.APP_JS: interi in centesimi, mezzo verso l'alto). calcola() è pura: verifica.py la chiama
# con node per ogni livello, ogni numero di mesi e ogni percentuale. Nessun dato lascia il browser.
JS_CALCOLO = r"""
(function(){
'use strict';
function P(){return window.PagaCCNL;}
function trova(D,cid,lid){var c=D.c[cid];if(!c)return null;for(var i=0;i<c.l.length;i++){if(c.l[i].id===lid)return {c:c,L:c.l[i]};}return null;}
function passo(L,oggi){var p=null;L.p.forEach(function(x){if(!x.dal||oggi>=x.dal)p=x;});return p;}
function intero(v){var s=String(v==null?'':v).trim();return /^\d+$/.test(s)?parseInt(s,10):NaN;}
function calcola(D,cid,lid,o,oggi){
  var r=trova(D,cid,lid);if(!r)return null;var c=r.c,p=passo(r.L,oggi);
  if(!p||p.no)return {no:true};
  var k=intero(o.mesi),n=intero(o.n),m;
  if(!(k>=1&&k<=12))return null;
  if(c.dom){
    if(o.modo==='aore'){if(!(n>=1&&n<=40))return null;m=P().orario52(p.o,n);}
    else if(o.modo==='conv'){m=p.m;}else return null;
  }else{
    if(o.modo==='pct'){if(!(n>=1&&n<=99))return null;m=P().prorata(p.m,n,100);}
    else if(o.modo==='pieno'){m=p.m;}else return null;
  }
  var t=P().prorata(m,k,12);
  return {mensile:m,tred:t,rateo:P().prorata(m,1,12),quatt:c.mens===14?t:null,dal:p.t,mesi:k};
}
window.PagaTredicesima={calcola:calcola};
function oggiRoma(){var g='';try{g=new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/Rome',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());}catch(x){}
  if(!/^\d{4}-\d{2}-\d{2}$/.test(g)){var d=new Date();g=d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2);}return g;}
function avvia(){
  var box=document.querySelector('[data-tredicesima]'),dati=document.getElementById('tredicesima-dati');if(!box||!dati)return;
  var D=JSON.parse(dati.textContent),oggi=oggiRoma();
  function q(s){return box.querySelector(s);}
  var sc=q('[name=contratto]'),sl=q('[name=livello]'),so=q('[name=orario]'),inN=q('[name=quanto]'),labN=q('[data-quanto]'),etN=q('[data-quanto-et]'),inM=q('[name=mesi]');
  var esito=q('[data-esito]'),no=q('[data-no]'),err=q('[data-err]'),oT=q('[data-out-tred]'),oR=q('[data-out-rateo]'),oQ=q('[data-out-quatt]'),rQ=q('[data-quatt]'),
      oB=q('[data-out-base]'),etT=q('[data-et-tred]'),lk=q('[data-pagina]');
  function opt(v,t){var o=document.createElement('option');o.value=v;o.textContent=t;return o;}
  function livelli(sel){var c=D.c[sc.value];sl.textContent='';var gr={};
    c.l.forEach(function(L){var dove=sl;if(L.g){if(!gr[L.g]){gr[L.g]=document.createElement('optgroup');gr[L.g].label=L.g;sl.appendChild(gr[L.g]);}dove=gr[L.g];}dove.appendChild(opt(L.id,L.n));});
    if(sel&&trova(D,sc.value,sel))sl.value=sel;}
  function orari(){var c=D.c[sc.value];so.textContent='';
    if(c.dom){so.appendChild(opt('conv','Convivente (mensile)'));so.appendChild(opt('aore','Non convivente, a ore'));}
    else{so.appendChild(opt('pieno','Tempo pieno'));so.appendChild(opt('pct','Part time: percentuale'));}
    campo();}
  function campo(){var m=so.value;labN.hidden=(m==='pieno'||m==='conv');
    if(m==='pct'){etN.textContent='Percentuale del tempo pieno (da 1 a 99)';inN.min=1;inN.max=99;inN.value=50;}
    if(m==='aore'){etN.textContent='Ore a settimana (da 1 a 40)';inN.min=1;inN.max=40;inN.value=20;}}
  function grezzo(i){return (i.validity&&i.validity.badInput)?'x':i.value;}
  function aggiorna(){var t=trova(D,sc.value,sl.value);esito.hidden=true;no.hidden=true;err.hidden=true;
    lk.setAttribute('href','/'+t.c.u);lk.textContent='Regole e tabella: tredicesima '+t.c.b.toLowerCase();
    var r=calcola(D,sc.value,sl.value,{mesi:grezzo(inM),modo:so.value,n:grezzo(inN)},oggi);
    if(!r){err.hidden=false;err.textContent=(function(){var k=intero(grezzo(inM));return (k>=1&&k<=12)?'Scrivi un numero intero tra '+inN.min+' e '+inN.max+'.':'Scrivi i mesi lavorati: un numero intero da 1 a 12.';})();return;}
    if(r.no){no.hidden=false;return;}
    etT.textContent='Tredicesima lorda sul minimo ('+r.mesi+(r.mesi===1?' mese':' mesi')+' su 12)';
    oT.textContent=P().eur(r.tred);oR.textContent=P().eur(r.rateo);rQ.hidden=(r.quatt===null);if(r.quatt!==null){oQ.textContent=P().eur(r.quatt);q('[data-et-quatt]').textContent=t.c.q14;}
    oB.textContent='Base: '+P().eur(r.mensile)+' lordi al mese, minimo in vigore dal '+r.dal+'.';esito.hidden=false;}
  if(D.c[box.getAttribute('data-predef-c')])sc.value=box.getAttribute('data-predef-c');
  livelli(sl.getAttribute('data-predef'));orari();
  sc.addEventListener('change',function(){livelli();orari();aggiorna();});
  sl.addEventListener('change',aggiorna);so.addEventListener('change',function(){campo();aggiorna();});inN.addEventListener('input',aggiorna);inM.addEventListener('input',aggiorna);
  box.querySelectorAll('[data-mesi]').forEach(function(b){b.addEventListener('click',function(){inM.value=b.getAttribute('data-mesi');aggiorna();});});
  aggiorna();
}
if(typeof document.addEventListener==='function'){if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',avvia);else avvia();}
})();
"""


def calcolatore(G, D, cid=None):
    pre_c = cid or "terziario"
    pre_l = PREDEF[pre_c]
    opz_c = "".join(f'<option value="{c}"{" selected" if c == pre_c else ""}>{G.h(D["c"][c]["b"])}</option>' for c in D["ordine"])
    opz_l = "".join(f'<option value="{x["id"]}"{" selected" if x["id"] == pre_l else ""}>{G.h(x["n"])}</option>' for x in D["c"][pre_c]["l"])
    opz_o = ('<option value="conv">Convivente (mensile)</option><option value="aore">Non convivente, a ore</option>' if pre_c == "domestico"
             else '<option value="pieno">Tempo pieno</option><option value="pct">Part time: percentuale</option>')
    return f"""<section class="card calc pull" data-tredicesima data-predef-c="{pre_c}" aria-labelledby="tre-h">
<div class="calc-h"><h2 id="tre-h">{G.ico("calc")}Calcola la tredicesima sul minimo</h2><span class="pill">Lordo</span></div>
<div class="calc-g"><div class="calc-in">
<label>Contratto<select name="contratto">{opz_c}</select></label>
<label>Livello<select name="livello" data-predef="{pre_l}">{opz_l}</select></label>
<label>Orario<select name="orario">{opz_o}</select></label>
<label data-quanto hidden><span data-quanto-et>Percentuale del tempo pieno (da 1 a 99)</span><input name="quanto" type="number" inputmode="numeric" min="1" max="99" step="1" value="50"></label>
<label>Mesi lavorati nell'anno (da 1 a 12)<input name="mesi" type="number" inputmode="numeric" min="1" max="12" step="1" value="12"></label>
<div class="chips" role="group" aria-label="Mesi lavorati">{"".join(f'<button type="button" data-mesi="{k}">{k} {"mese" if k == 1 else "mesi"}</button>' for k in (3, 6, 9, 12))}</div>
<p class="small" data-err hidden style="margin:0;color:var(--warm-ink);font-weight:700"></p>
</div><div class="calc-out" aria-live="polite">
<div data-no hidden><p style="margin:0"><strong>Per questo livello oggi non facciamo il calcolo.</strong> La tabella in vigore non ha ancora passato i nostri due controlli e l'ultima cifra verificata è superata. I dettagli sono nella pagina del livello.</p></div>
<div data-esito style="display:grid;gap:10px">
<div class="esito"><span data-et-tred>Tredicesima lorda sul minimo</span><b data-out-tred>—</b></div>
<div class="esito sec"><span>Un dodicesimo: quanto matura ogni mese</span><b data-out-rateo>—</b></div>
<div class="esito sec" data-quatt hidden><span data-et-quatt>Quattordicesima sul minimo di oggi</span><b data-out-quatt>—</b></div>
<p class="small" data-out-base style="margin:0"></p>
<p class="small" style="margin:0"><a data-pagina href="/{D["c"][pre_c]["u"]}">Regole e tabella del contratto</a></p>
</div></div></div>
<p class="calc-f">Formula: minimo mensile × mesi lavorati ÷ 12. Con il part time il minimo si riduce prima in proporzione all'orario. È un importo lordo sul minimo del contratto: senza scatti, superminimi e altre voci, e prima di tasse e contributi. Il calcolo avviene nel tuo browser: non inviamo niente.</p>
<noscript><p class="calc-f">Il calcolo ha bisogno di JavaScript. Senza, trovi gli stessi importi nelle tabelle delle pagine dei contratti.</p></noscript>
</section>
<script type="application/json" id="tredicesima-dati">{json.dumps(D, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")}</script>
<script id="tredicesima-js">{JS_CALCOLO.strip()}</script>"""


# ---------------------------------------------------------------- 4. tredicesima: pagina del contratto
QUANTO_TRE = {
    "terziario": "Nel commercio la tredicesima è una mensilità della «retribuzione di fatto»: il minimo del tuo livello più le altre voci fisse che hai in busta paga.",
    "metalmeccanici": "Nei metalmeccanici la tredicesima è ragguagliata alla «retribuzione globale di fatto»: il minimo del tuo livello più le altre voci fisse che hai in busta paga.",
    "multiservizi": "Nel multiservizi la tredicesima è pari alla retribuzione mensile globale: il minimo del tuo livello più le altre voci fisse che hai in busta paga.",
    "logistica": "Nella logistica la tredicesima è pari alla retribuzione globale mensile di novembre: minimo ed elemento professionale d'area (EPA) del tuo livello, più le altre voci fisse che hai in busta paga.",
    "domestico": "Per colf e badanti la tredicesima è una mensilità in più, pari alla retribuzione globale di fatto. Per chi convive comprende anche il valore di vitto e alloggio.",
}
FRAZIONI_TRE = {
    "terziario": "Contano i mesi interi di servizio. Una frazione di mese di 15 giorni o più conta come un mese intero; sotto i 15 giorni non conta. I mesi sono quelli del calendario.",
    "metalmeccanici": "Contano i mesi di anzianità nell'azienda. Una frazione di mese superiore a 15 giorni conta come un mese intero. Anche il periodo di prova conta.",
    "multiservizi": "Contano i mesi di servizio nel periodo. Le frazioni di mese fino a 15 giorni non contano; sopra i 15 giorni contano come un mese intero. L'articolo parla del lavoratore «non in prova».",
    "logistica": "Contano i mesi di servizio. Le frazioni di mese fino a 15 giorni non contano; sopra i 15 giorni contano come un mese intero. Vale anche se il contratto a termine finisce o se la prova non viene superata.",
    "domestico": "Si pagano tanti dodicesimi quanti sono i mesi di lavoro. Una frazione di mese di 15 giorni di calendario o più conta come un mese intero.",
}
PARTTIME_TRE = {
    "terziario": "Con il part time la tredicesima si riduce nella stessa proporzione dell'orario. Se nell'anno sei passato da tempo pieno a part time (o il contrario), ogni dodicesimo si calcola con l'orario di quel mese.",
    "metalmeccanici": "Chi lavora part time ha gli stessi diritti del tempo pieno, con un trattamento riproporzionato all'orario: anche la tredicesima.",
    "multiservizi": "Per il part time il trattamento economico si proporziona all'orario scritto nel contratto individuale: anche la tredicesima e la quattordicesima.",
    "logistica": "Il part time è pagato in proporzione all'orario, e così anche tredicesima e quattordicesima. Se nell'anno passi da tempo pieno a part time (o il contrario), i ratei si calcolano sui due periodi.",
}


def tab_tredicesima(G, cid):
    righe, manca = [], False
    for L in G.livelli_pubblicati(cid):
        s = base(G, cid, L)
        nome = f'<a href="/{G.pagina_url(cid, L)}">{G.h(L["nome"])}</a>'
        if not s:
            manca = True
            righe.append([nome] + [DA_AGG] * (1 + len(MESI_TAB)))
            continue
        righe.append([nome, e_c(G, s["m"])] + [e_c(G, G.cent(G.prorata(G.da_cent(s["m"]), k, 12))) for k in MESI_TAB])
    return G.tabella(["Livello", "Tredicesima intera (12 mesi)"] + [f"{k} {'mese' if k == 1 else 'mesi'}" for k in MESI_TAB], righe) + (NOTA_DA_AGG if manca else "")


def tab_parttime(G, cid):
    ore = None
    righe = []
    for L in G.livelli_pubblicati(cid):
        s = base(G, cid, L)
        nome = f'<a href="/{G.pagina_url(cid, L)}">{G.h(L["nome"])}</a>'
        if not s:
            continue
        ore = [o for o in s["p"] if cid == "domestico" or o != G.C[cid]["ore"]["valore"]]
        righe.append([nome] + [e_c(G, s["p"][o]) for o in ore])
    if not righe:
        return ""
    return G.tabella(["Livello"] + [f"{o} ore a settimana" for o in ore], righe)


def giorno_14(G):
    """Il prossimo 30 giugno: la quattordicesima di luglio si calcola sulla retribuzione di quel giorno."""
    a = G.OGGI.year if G.OGGI <= date(G.OGGI.year, 6, 30) else G.OGGI.year + 1
    return date(a, 6, 30)


def tab_quattordicesima(G, cid):
    """Quattordicesima intera di luglio: il minimo che le tabelle già firmate prevedono per il 30 giugno (stesse regole di
    pubblicazione delle pagine livello, viste a quella data). Riga sospesa a quella data: «da aggiornare»."""
    g = giorno_14(G)
    righe, manca = [], False
    for L in G.livelli_pubblicati(cid):
        s = G.al_giorno(g, base, G, cid, L)
        nome = f'<a href="/{G.pagina_url(cid, L)}">{G.h(L["nome"])}</a>'
        if not s:
            manca = True
            righe.append([nome, DA_AGG, "—"])
        else:
            righe.append([nome, e_c(G, s["m"]), G.data_lunga(s["dal"])])
    return G.tabella(["Livello", f"Quattordicesima intera di luglio {g.year}", "Tabella in vigore dal"], righe, num=[1]) + (NOTA_DA_AGG if manca else "")


Q14_TESTO = {
    "terziario": "La quattordicesima è una mensilità come la tredicesima, ma si calcola sulla retribuzione in vigore al 30 giugno: quella di luglio {anno} userà il minimo di quel giorno, non quello di oggi.",
    "logistica": "La quattordicesima è una mensilità come la tredicesima, ma si calcola sulla retribuzione in vigore al 30 giugno: quella di luglio {anno} userà il minimo di quel giorno, non quello di oggi.",
    "multiservizi": ("La quattordicesima è una mensilità come la tredicesima. L'articolo 21 non dice di quale mese sia la retribuzione da usare: "
                     "noi mettiamo in tabella il minimo previsto per il 30 giugno {anno}, ultimo giorno del periodo di riferimento, non quello di oggi."),
}
Q14_RIGA = {  # etichetta della riga della quattordicesima nel calcolo
    "terziario": "Quattordicesima sul minimo di oggi (quella vera usa il minimo al 30 giugno)",
    "logistica": "Quattordicesima sul minimo di oggi (quella vera usa il minimo al 30 giugno)",
    "multiservizi": "Quattordicesima sul minimo di oggi (prima di luglio il minimo può cambiare)",
}


def esempio_tre(G, cid):
    L = next(x for x in G.C[cid]["livelli"] if x["id"] == PREDEF[cid])
    s = base(G, cid, L)
    if not s:
        return ""
    return (f'<div class="formula">{e_c(G, s["m"])} × 7 ÷ 12 = <strong>{e_c(G, G.cent(G.prorata(G.da_cent(s["m"]), 7, 12)))}</strong> lordi'
            f'<small>{G.h(L["nome"])}{", convivente" if cid == "domestico" else ", tempo pieno"}, 7 mesi lavorati nell\'anno. Minimo in vigore dal {G.data_lunga(s["dal"])}.</small></div>')


def pagina_tredicesima(G, cid, D):
    m, t = G.C[cid], CI[cid]["tredicesima"]
    q = t["quattordicesima"]
    rim = G.Rimandi()
    fa, fb = m["fonte_a"], m["fonte_b"]
    anno = G.OGGI.year
    e14 = " e quattordicesima" if q else ""
    corpo = (f'<div class="card cifre pull"><div class="cifra main"><b>{m["mensilita"]["valore"]}</b><span>mensilità in un anno: {"tredicesima e quattordicesima" if q else "c\'è la tredicesima, non la quattordicesima"}</span></div>'
             f'<div class="cifra"><b>{G.h(t["quando_breve"])}</b><span>quando si paga la tredicesima</span></div>'
             + (f'<div class="cifra"><b>{G.h(q["quando_breve"])}</b><span>quando si paga la quattordicesima</span></div>' if q else
                '<div class="cifra"><b>1/12</b><span>matura per ogni mese lavorato</span></div>')
             + f'<div class="cifra"><b>15 giorni</b><span>{G.h(t["frazione_breve"])}</span></div>'
             f'<p class="asof">{G.ico("check")} Regole dal testo del contratto ({G.h(t["dove"])}){rim.ref(t["fonte"])}; importi dal minimo verificato su due fonti{rim.ref([fa, fb])}. Articoli letti il {G.data_lunga(LETTO)}.</p></div>')
    corpo += nota_testo(G, cid, "tredicesima")
    corpo += calcolatore(G, D, cid)
    corpo += f'<h2 id="quando">Quando arriva la tredicesima</h2><p>Il contratto dice: {G.h(t["quando_breve"])}.</p>'
    corpo += cita(G, cid, "tredicesima", "quando" if "quando" in t["cit"] else "quanto", rim)
    corpo += f'<h2 id="importo">Quanto vale: importo lordo per livello</h2><p>{QUANTO_TRE[cid]}</p>'
    if "quando" in t["cit"]:
        corpo += cita(G, cid, "tredicesima", "quanto", rim)
    if "retribuzione" in t["cit"]:
        corpo += cita(G, cid, "tredicesima", "retribuzione", rim)
    corpo += (f'<p>Noi conosciamo solo il minimo del livello, cioè la cifra che abbiamo verificato su due fonti{rim.ref([fa, fb])}. La tabella parte da lì: '
              '<strong>è la tredicesima minima di chi ha lavorato tutto il periodo senza assenze non retribuite</strong>; è più alta se hai scatti di anzianità, superminimi o altre voci fisse. Sono importi lordi' + ("" if cid == "domestico" else " a tempo pieno") + '.</p>')
    if cid == "domestico":
        corpo += ('<p>Per colf e badanti la tabella usa il minimo mensile di chi convive (tabella A, con l\'indennità di funzione per i livelli D e DS). '
                  'Chi lavora a ore trova gli importi più sotto.</p>')
    corpo += a_date(G, cid, "tredicesima", lambda: tab_tredicesima(G, cid))
    if cid == "domestico":
        f_tot = G.EST["domestico"]["A"]["BS"]["F_totale"]
        corpo += G.nota_domestico()
        corpo += ('<p>Per chi convive, alla cifra della tabella va aggiunto il valore di vitto e alloggio, che fa parte della retribuzione globale di fatto. '
                  f'La tabella F del {anno_tabella(G, cid)} lo fissa in {G.euro(f_tot)} al giorno{rim.ref([fa, fb])}; quanti giorni contare nella tredicesima il contratto non lo scrive, '
                  f'quindi non lo sommiamo noi: {CONSULENTE} o con chi ti fa la busta paga.</p>' + cita(G, cid, "tredicesima", "globale", rim))
    if q:
        corpo += '<p class="small">Per la quattordicesima il minimo che conta non è quello di oggi: vedi <a href="#quattordicesima">più sotto</a>.</p>'
    corpo += G.AD
    corpo += f'<h2 id="mesi">Se hai lavorato solo una parte dell\'anno</h2><p>{FRAZIONI_TRE[cid]}</p>'
    corpo += cita(G, cid, "tredicesima", "prorata", rim) + cita(G, cid, "tredicesima", "frazioni", rim)
    if "prova" in t["cit"]:
        corpo += cita(G, cid, "tredicesima", "prova", rim)
    corpo += "<p>Il conto è: tredicesima intera × mesi che contano ÷ 12. Un esempio con il minimo:</p>" + a_date(G, cid, "esempio", lambda: esempio_tre(G, cid))
    if "assenze" in t["cit"]:
        corpo += "<p>La tredicesima matura anche in alcuni periodi di assenza:</p>" + cita(G, cid, "tredicesima", "assenze", rim)
    # part time
    if cid == "domestico":
        corpo += '<h2 id="part-time">Colf e badanti a ore</h2>'
        corpo += ('<p>Chi non convive è pagato a ore. La retribuzione mensile si ottiene così: paga oraria × ore a settimana × 52 ÷ 12. La tredicesima intera è pari a questa mensilità. '
                  'Qui sotto trovi il minimo per alcuni orari; per le tue ore usa il calcolo in alto.</p>' + cita(G, cid, "tredicesima", "ore", rim))
        corpo += a_date(G, cid, "orari", lambda: tab_parttime(G, cid))
    else:
        corpo += f'<h2 id="part-time">Tredicesima{e14} con il part time</h2><p>{PARTTIME_TRE[cid]}</p>' + cita(G, cid, "tredicesima", "parttime", rim)
        if "parttime_anno" in t["cit"]:
            corpo += cita(G, cid, "tredicesima", "parttime_anno", rim)
        corpo += (f'<p>La tabella dà la tredicesima intera sul minimo per tre orari. Il conto è quello delle pagine dei livelli: minimo × ore ÷ {m["ore"]["valore"]} '
                  f'(l\'orario del tempo pieno in questo contratto è di {m["ore"]["valore"]} ore).</p>')
        corpo += a_date(G, cid, "orari", lambda: tab_parttime(G, cid))
    # quattordicesima
    corpo += '<h2 id="quattordicesima">Quattordicesima</h2>'
    if q:
        corpo += (f'<p>Questo contratto prevede anche la quattordicesima ({G.h(q["dove"])}). Si paga {G.h(q["quando_breve"])} ed è una mensilità, come la tredicesima. '
                  f'Il periodo in cui matura non è l\'anno solare: sono {G.h(q["periodo_breve"])}.</p>')
        corpo += "".join(cita(G, cid, "tredicesima", f"14:{k}", rim) for k in q["cit"])
        corpo += f'<p>{Q14_TESTO[cid].format(anno=giorno_14(G).year)}</p>'
        corpo += (f'<p>La tabella dà la quattordicesima intera sul minimo che le tabelle già firmate prevedono per il 30 giugno {giorno_14(G).year}{rim.ref([fa, fb])}. '
                  'Se prima di quel giorno un rinnovo o un adeguamento cambia i minimi, cambia anche la quattordicesima.</p>')
        corpo += a_date(G, cid, "quattordicesima", lambda: tab_quattordicesima(G, cid))
        corpo += ('<p>Per chi non ha lavorato tutto il periodo valgono gli stessi dodicesimi: quattordicesima intera × mesi che contano ÷ 12. '
                  'Nel calcolo in alto la riga della quattordicesima usa il minimo di oggi e lo stesso numero di mesi che scrivi per la tredicesima: '
                  'per la cifra di luglio parti dalla tabella qui sopra, e se nei due periodi hai mesi diversi fai due conti.</p>')
    else:
        corpo += (f'<p>Il {G.h(CCNL[cid])} prevede 13 mensilità ({G.h(m["mensilita"]["dove"])}){rim.ref(m["mensilita"]["fonte"])}: la quattordicesima nel contratto nazionale non c\'è. '
                  'Un accordo aziendale o individuale può prevedere altri premi: qui non li trattiamo.</p>')
    corpo += '<h2 id="limiti">Cosa non c\'è in queste cifre</h2><div class="testo"><ul>'
    corpo += ('<li>scatti di anzianità, superminimi, indennità fisse e premi: fanno salire la tua tredicesima, ma dipendono dalla tua busta paga;</li>'
              '<li>i mesi di assenza non retribuita, che possono ridurre i dodicesimi;</li>'
              '<li>tasse e contributi: sono importi lordi, e il netto qui non lo calcoliamo;</li>'
              '<li>accordi aziendali che pagano la tredicesima a rate ogni mese.</li></ul>'
              f'<p>Sono informazioni generali prese dal testo del contratto. Per la tua busta paga, {CONSULENTE} del lavoro, con il sindacato o con un patronato.</p></div>')
    corpo += (f'<h2 id="vedi">Vedi anche</h2><p>Se stai per cambiare lavoro: <a href="/{p_pre(G, cid)}">giorni di preavviso {G.h(BREVE[cid])}</a>. '
              'Il minimo, la paga oraria e gli aumenti di ogni livello:</p>' + G.lista_livelli(cid))
    corpo += '<h3>La tredicesima negli altri contratti</h3>' + altri_contratti(G, cid, p_tre, "Tredicesima")
    corpo += fonti_box(G, rim, [t["fonte"]] + [c["fonte"] for c in t["cit"].values() if c.get("fonte")])
    titolo, h1, descr = {
        "terziario": (f"Tredicesima e quattordicesima commercio {anno}: importi e calcolo", f"Tredicesima e quattordicesima del commercio {anno}",
                      "Tredicesima e quattordicesima del CCNL commercio: importo lordo per livello sul minimo, dodicesimi per i mesi lavorati, part time e date di pagamento."),
        "metalmeccanici": (f"Tredicesima metalmeccanici {anno}: importo per livello e calcolo", f"Tredicesima dei metalmeccanici {anno}",
                           "Tredicesima dei metalmeccanici: quando arriva, importo lordo per livello da D1 ad A1 sul minimo, dodicesimi per i mesi lavorati e part time."),
        "multiservizi": (f"Tredicesima e quattordicesima multiservizi {anno}: importi", f"Tredicesima e quattordicesima del multiservizi {anno}",
                         "Tredicesima (entro il 20 dicembre) e quattordicesima (entro il 15 luglio) del CCNL multiservizi e pulizie: importi lordi per livello e part time."),
        "logistica": (f"Tredicesima e quattordicesima logistica {anno}: importi", f"Tredicesima e quattordicesima della logistica {anno}",
                      "Tredicesima e quattordicesima del CCNL logistica e trasporto merci: quando si pagano, importo lordo per livello sul minimo, dodicesimi e part time."),
        "domestico": (f"Tredicesima colf e badanti {anno}: calcolo e importi per livello", f"Tredicesima di colf e badanti {anno}",
                      "Tredicesima di colf e badanti: si paga entro dicembre, importo lordo per livello per chi convive e per chi lavora a ore, dodicesimi per i mesi lavorati."),
    }[cid]
    testata = G.banda(f"{m['nome_breve']} · tredicesima", h1,
                      f"Quando si paga, quanto vale sul minimo di ogni livello e come si riduce per i mesi lavorati e per il part time. Regole dal testo del contratto ({G.h(t['dove'])}).", icona="euro")
    G.pagina(p_tre(G, cid), titolo, descr, corpo, testata, briciole=[("Home", ""), ("Tredicesima", P_TRE), (m["nome_breve"], p_tre(G, cid))])


# ---------------------------------------------------------------- 5. tredicesima: indice con il calcolo
def indice_tredicesima(G, D):
    rim = G.Rimandi()
    anno = G.OGGI.year
    n_liv = sum(len(G.livelli_pubblicati(c)) for c in G.ORDINE)
    righe = []
    for cid in G.ORDINE:
        m, t = G.C[cid], CI[cid]["tredicesima"]
        q = t["quattordicesima"]
        righe.append((f'<a href="/{p_tre(G, cid)}">{G.h(m["nome_breve"])}</a>', G.h(t["quando_breve"]), G.h(q["quando_breve"]) if q else "non prevista",
                      G.h(t["frazione_breve"]), G.h(t["dove"] + (f'; {q["dove"]}' if q else "")) + rim.ref(t["fonte"])))
    corpo = calcolatore(G, D)
    corpo += '<h2 id="come">Come si calcola la tredicesima</h2><div class="testo">'
    corpo += ('<p>La tredicesima è una mensilità in più, pagata a dicembre. Se hai lavorato tutto l\'anno è pari a un mese di retribuzione. '
              'Se hai lavorato solo una parte dell\'anno, ne prendi un dodicesimo per ogni mese che conta.</p>'
              '<div class="formula">retribuzione mensile × mesi lavorati ÷ 12 = tredicesima lorda<small>Con il part time la retribuzione mensile è già ridotta in proporzione all\'orario.</small></div>'
              f'<p>Il calcolo qui sopra usa il <strong>minimo mensile del tuo livello</strong>: è la cifra che questo sito verifica su due fonti ufficiali per {n_liv} livelli di 5 contratti. '
              'La tua retribuzione può essere più alta del minimo (scatti di anzianità, superminimi, indennità fisse): in quel caso anche la tredicesima è più alta. '
              'Quello che leggi qui è quindi il minimo lordo per chi ha lavorato tutto il periodo senza assenze non retribuite.</p></div>')
    corpo += '<h2 id="quando">Quando arriva la tredicesima, contratto per contratto</h2>'
    corpo += '<p>La data non è uguale per tutti: la scrive ogni contratto. Lo stesso vale per la quattordicesima, che esiste solo in alcuni contratti.</p>'
    corpo += G.tabella(["Contratto", "Tredicesima", "Quattordicesima", "Frazioni di mese", "Dove sta scritto"], righe, num=[])
    corpo += G.AD
    corpo += '<h2 id="mesi">Quali mesi contano</h2><div class="testo">'
    corpo += ('<p>Tutti e cinque i contratti contano i mesi di servizio e trattano le frazioni di mese con la soglia dei 15 giorni. C\'è una piccola differenza:</p><ul>'
              '<li>nel commercio e nel lavoro domestico una frazione di <strong>15 giorni o più</strong> conta come un mese intero;</li>'
              '<li>nei metalmeccanici, nel multiservizi e nella logistica conta come un mese intero la frazione <strong>superiore a 15 giorni</strong>.</li></ul>'
              '<p>Esempio: assunto il 10 settembre. Settembre ha 21 giorni di servizio e conta; i mesi sono 4 (settembre, ottobre, novembre, dicembre) e la tredicesima è di 4 dodicesimi. '
              'Nella pagina di ogni contratto trovi la frase esatta.</p></div>')
    corpo += '<h2 id="part-time">Part time</h2><div class="testo">'
    corpo += ('<p>Con il part time la tredicesima si riduce come lo stipendio: in proporzione all\'orario. Nel calcolo scegli «Part time: percentuale» e scrivi la tua percentuale del tempo pieno '
              '(per esempio 50 per 20 ore su 40). Per colf e badanti a ore scegli «Non convivente, a ore» e scrivi le ore a settimana: il mensile è paga oraria × ore × 52 ÷ 12.</p></div>')
    corpo += '<h2 id="contratti">Importi per livello</h2><ul class="griglia">' + "".join(
        f'<li><a href="/{p_tre(G, c)}"><b>Tredicesima {G.h(BREVE[c])}</b><span>{G.h(G.C[c]["nome"])}</span>'
        f'<span>{len(G.livelli_pubblicati(c))} livelli · {G.C[c]["mensilita"]["valore"]} mensilità</span></a></li>' for c in G.ORDINE) + "</ul>"
    corpo += '<h2 id="limiti">Cosa questo calcolo non fa</h2><div class="testo"><ul>'
    corpo += ('<li><strong>Non calcola il netto.</strong> Sulla tredicesima si pagano contributi e tasse: quanto, dipende dalla tua situazione. Non facciamo stime.</li>'
              '<li><strong>Non conosce la tua busta paga.</strong> Parte dal minimo del contratto, senza scatti, superminimi e premi.</li>'
              '<li><strong>Non conta le assenze.</strong> Alcune assenze non retribuite riducono i dodicesimi: dipende dal contratto e dal caso.</li>'
              '<li><strong>Copre cinque contratti.</strong> Se il tuo non c\'è, non lo stimiamo.</li></ul>'
              f'<p>Per la tua busta paga, {CONSULENTE} del lavoro, con il sindacato o con un patronato. Se stai pensando di cambiare lavoro, guarda anche i '
              f'<a href="/{P_PRE}">giorni di preavviso per contratto</a>.</p></div>')
    corpo += fonti_box(G, rim, [CI[c]["tredicesima"]["fonte"] for c in G.ORDINE])
    testata = G.banda(f"Tredicesima {anno}", "Tredicesima: calcolo per contratto e livello",
                      f"Scegli contratto e livello, scrivi i mesi lavorati e il part time: ottieni la tredicesima lorda sul minimo. <strong>{n_liv} livelli</strong> di 5 contratti, con la data di pagamento scritta in ognuno.",
                      icona="calc")
    G.pagina(P_TRE, f"Calcolo tredicesima {anno} per contratto e livello (lordo)",
             "Calcola la tredicesima lorda da contratto e livello: mesi lavorati, part time, quando arriva in 5 CCNL e in quali c'è anche la quattordicesima.",
             corpo, testata, briciole=[("Home", ""), ("Tredicesima", P_TRE)])


def genera(G):
    D = dati_calcolo(G)
    indice_preavviso(G)
    for cid in G.ORDINE:
        pagina_preavviso(G, cid)
    indice_tredicesima(G, D)
    for cid in G.ORDINE:
        pagina_tredicesima(G, cid, D)
