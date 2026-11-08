"""Genera il sito statico "Balcony Solar Europe" (fotovoltaico da balcone: regole ufficiali e calcolatore di produzione e
risparmio) in solarebalcone/sito/, in italiano, spagnolo e francese. Il tedesco (/de/) è previsto ma spento: si accende
quando Massimiliano conferma l'Impressum (vedi NOTE.md).

Uso (dalla radice del repository):
    python3 solarebalcone/raccolta/pvgis.py     # produzione PVGIS per città  -> dati/pvgis.json
    python3 solarebalcone/raccolta/prezzi.py    # prezzo Eurostat dell'elettricità -> dati/prezzi.json
    python3 solarebalcone/raccolta/domanda.py   # ricerche Google vere (città con pagina, FAQ) -> dati/domanda.json
    python3 solarebalcone/raccolta/fonti.py     # rilettura delle fonti delle regole -> dati/fonti.json
    python3 solarebalcone/genera.py             # pagine in solarebalcone/sito/
    python3 solarebalcone/verifica.py --browser # controlli prima di pubblicare

Dati: dati/citta.json (città del calcolatore), dati/regole.json (regole e FAQ con le fonti), dati/affiliati.json (riquadro
spento finché non ci sono link veri). Nessun dato personale. Nessun consiglio elettrico o legale.
"""
import hashlib
import json
import math
import re
import shutil
import sys
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote_plus

RADICE = Path(__file__).resolve().parent
DATI = RADICE / "dati"
SITO = RADICE / "sito"

URL_SITO = "https://balcony-solar-europe.netlify.app"  # unico punto da cambiare se il nome del sito su Netlify è diverso
GOOGLE_VERIFICA = "btXTQU_vAoe1K9f3q-43GisAXTiyKQCYcShozNhrAgI"  # Search Console (stesso account degli altri siti)
GOATCOUNTER_URL = "https://rete-siti.goatcounter.com/count"  # contatore condiviso della rete, senza cookie
SCRIPT_CONTATORE = ('<script>window.goatcounter={path:function(p){return location.host+p}}</script>'
                    f'<script data-goatcounter="{GOATCOUNTER_URL}" async src="https://gc.zgo.at/count.js"></script>')
CHIAVE_INDEXNOW = "b5a26a844a465f58552debee2c8a0114"  # = CHIAVE in studio-business/strumenti/indexnow.py
sys.path.append(str(RADICE.parent / "studio-business" / "strumenti"))
import monetizzazione as MON  # noqa: E402
SITO_ID = "solarebalcone"  # nome del sito in monetizzazione.json
ADSENSE_HEAD = MON.script_adsense(SITO_ID)

# Ipotesi del calcolatore (dichiarate in ogni pagina)
POTENZA_RIF = 800        # Wp del kit di riferimento (PVGIS è calcolato a 0,8 kWp)
QUOTA_DEF = 60           # % dell'energia prodotta usata in casa mentre il sole c'è (ipotesi, modificabile)
KIT_DEF = 500            # € prezzo di esempio del kit nel calcolatore (non è un prezzo rilevato)
QUOTE_TAB = [40, 60, 80]
KIT_TAB = [300, 500, 800]


def carica(nome):
    return json.loads((DATI / nome).read_text(encoding="utf-8"))


CITTA = carica("citta.json")
PVGIS = carica("pvgis.json")
PREZZI = carica("prezzi.json")
DOMANDA = carica("domanda.json")
REGOLE = carica("regole.json")
FONTI_ESITO = carica("fonti.json")["fonti"]
AFFILIATI = carica("affiliati.json")
VERIFICA = date.fromisoformat(REGOLE["verificato_il"])
PVGIS_DATA = date.fromisoformat(PVGIS["letto_il"])
OGGI = date.today()
ULTIMO_DATO = max(VERIFICA, PVGIS_DATA, date.fromisoformat(PREZZI["letto_il"]))

LINGUE_ATTIVE = ["it", "es", "fr"]  # "de": previsto, spento finché manca l'Impressum (REGOLE["paesi"]["de"]["attiva"])
PAESE = {"it": "IT", "es": "ES", "fr": "FR", "de": "DE"}


DUE_PUNTI = {"it": ": ", "es": ": ", "fr": "\u00a0: "}  # in francese spazio (indivisibile) prima dei due punti


def elidi(testo):
    """Italiano: articolo e preposizione elisi davanti ai numeri che si leggono «otto...» o «undici» (l'8 novembre, all'8° posto,
    dell'11, l'80%)."""
    return re.sub(r"\b(il|del|al|dal|nel)\s(8\d*|11)(?=[\s°%.,)]|$)",
                  lambda m: {"il": "l'", "del": "dell'", "al": "all'", "dal": "dall'", "nel": "nell'"}[m.group(1)] + m.group(2), testo)


def h(x):
    return escape(str(x), quote=True)


# ---------------------------------------------------------------- testi per lingua
T = {
    "it": {
        "html": "it-IT", "og": "it_IT", "nome": "Solare da balcone", "logo": ("Solare", "da balcone"),
        "paese": "Italia", "nel_paese": "in Italia", "prezzo_medio": "prezzo medio italiano",
        "p_home": "it/", "p_regole": "it/regole-fotovoltaico-balcone/", "p_faq": "it/domande-frequenti/",
        "p_contatti": "it/contatti/", "p_privacy": "it/privacy/", "p_citta": "it/fotovoltaico-balcone-{s}/",
        "menu": [("regole", "Regole"), ("calc", "Calcolatore"), ("citta", "Città"), ("faq", "Domande")],
        "skip": "Vai al contenuto", "menu_lbl": "Menu", "tema": "Cambia tema chiaro o scuro", "lingua_lbl": "Lingua",
        "home_t": "Fotovoltaico da balcone: regole 2026 e calcolatore per città",
        "home_h1": "Fotovoltaico da balcone in Italia: le regole e quanto rende nella tua città",
        "home_eyebrow": "Italia · regole e calcolatore",
        "home_sub": ("Sotto 800 W basta la Comunicazione Unica al distributore, gratis (ARERA). A {citta} un kit da 800 Wp "
                     "inclinato verso sud produce circa <strong>{kwh} kWh l'anno</strong> (PVGIS)."),
        "home_d": "Fotovoltaico da balcone in Italia: Comunicazione Unica sotto 800 W, condominio, detrazioni e calcolatore di risparmio per {n} città con dati PVGIS.",
        "trust": ["Dati PVGIS della Commissione europea", "Prezzo dell'elettricità Eurostat {periodo}", "Fonti ufficiali lette il {data}"],
        "calc_h": "Calcola produzione e risparmio", "calc_citta": "Città", "calc_mont": "Montaggio",
        "m35": "Inclinato 35° verso sud", "m90": "Verticale sulla ringhiera (verso sud)",
        "calc_w": "Potenza dei pannelli (Wp)", "calc_quota": "Energia usata in casa mentre c'è il sole",
        "calc_prezzo": "Prezzo dell'elettricità (€/kWh)", "calc_kit": "Prezzo del kit (€)",
        "out_prod": "Produzione", "out_auto": "Usata in casa", "out_eur": "Risparmio", "out_anni": "Rientro",
        "u_kwh_anno": "kWh/anno", "u_eur_anno": "€/anno", "u_anni": "anni",
        "calc_mesi": "Produzione mese per mese (kWh)", "calc_oltre": "Oltre 800 W: controlla prima le regole.",
        "calc_nota": ("Formula: produzione PVGIS del kit da 800 Wp × potenza/800 × quota usata in casa × prezzo = risparmio l'anno; "
                      "prezzo del kit ÷ risparmio = anni di rientro. L'energia che non usi va in rete senza compenso."),
        "mesi": ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"],
        "mesi_l": ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"],
        "ipotesi_h": "Come calcoliamo",
        "ipotesi": [
            "Produzione: PVGIS 5.3 della Commissione europea (banca dati {db}, anni {anni}), kit da 0,8 kWp in silicio cristallino rivolto a sud, perdite di sistema del 14% (valore predefinito di PVGIS), ombre del terreno comprese, nessuna ombra di palazzi o alberi.",
            "Due montaggi: inclinato di 35° (su un supporto) o verticale, appeso alla ringhiera. Con un orientamento diverso dal sud la produzione scende.",
            "Prezzo: {prezzo} €/kWh, media Eurostat per le famiglie con consumi tra 2.500 e 5.000 kWh l'anno, tasse comprese ({periodo}). La tua bolletta può essere diversa: metti il tuo prezzo.",
            "Energia usata in casa: {quota}% di ipotesi, da cambiare. Conta solo l'energia che consumi mentre il sole c'è; con la Comunicazione Unica quella che va in rete non viene pagata.",
            "Rientro: prezzo del kit diviso per il risparmio del primo anno, senza interessi, manutenzione, calo dei pannelli nel tempo o variazioni del prezzo dell'energia.",
        ],
        "tab_h": "Quanto produce un kit da 800 Wp nelle città italiane",
        "tab_th": ["Città", "Inclinato 35°", "Verticale", "Risparmio*"],
        "tab_nota": "* Inclinato 35°, {quota}% usato in casa, {prezzo} €/kWh. kWh l'anno da PVGIS. Le città con il link hanno una pagina con i dati mese per mese.",
        "regole_breve_h": "Le regole in breve", "regole_tutte": "Tutte le regole, con le fonti",
        "faq_h": "Domande frequenti", "faq_tutte": "Tutte le domande",
        "fonti_h": "Fonti", "letta": "letta il {data} (HTTP 200)", "non_letta": "non letta: {motivo}",
        "fonte_nostra": "nota nostra", "centro_risorse": "centro di risorse, non un ente pubblico",
        "fonti_dati": ("Produzione: PVGIS © European Communities, 2001-2026, riuso libero citando la fonte. Prezzo: Eurostat, "
                       "nrg_pc_204, riuso autorizzato citando la fonte."),
        "regole_t": "Fotovoltaico da balcone: regole in Italia 2026",
        "regole_d": "Regole del fotovoltaico da balcone in Italia: sotto 800 W, Comunicazione Unica al distributore, CEI 0-21, condominio e detrazioni. Fonti del {data}.",
        "regole_eyebrow": "Regole · Italia", "regole_sub": "Cosa dicono ARERA, il Codice civile e l'Agenzia delle Entrate. Verificate il {data}.",
        "prima_h": "Prima di comprare",
        "prima": ["Controlla sulla scheda del kit la potenza dell'impianto e la conformità alla Norma CEI 0-21.",
                  "Invia la Comunicazione Unica al distributore della tua zona.",
                  "In condominio leggi il regolamento e, se tocchi parti comuni, scrivi all'amministratore."],
        "prima_nota": "Questo sito riassume fonti ufficiali: non è una consulenza elettrica o legale. Per l'impianto di casa chiedi a un elettricista abilitato.",
        "faq_t": "Fotovoltaico da balcone: domande frequenti (2026)",
        "faq_d": "Fotovoltaico da balcone: le domande più cercate in Italia, con risposte dalle fonti ufficiali (permessi, condominio, 800 W, batteria, incentivi).",
        "faq_eyebrow": "Domande · Italia", "faq_sub": "Le domande vengono dalle ricerche Google; le risposte dalle fonti ufficiali.",
        "citta_t": "Fotovoltaico da balcone a {c}: quanto produce e risparmio",
        "citta_h1": "Fotovoltaico da balcone a {c}: quanto produce e quanto fa risparmiare",
        "citta_eyebrow": "{c} · dati PVGIS",
        "citta_sub": ("A {c} un kit da 800 Wp rivolto a sud produce circa <strong>{k35} kWh l'anno</strong> inclinato a 35° e "
                      "{k90} kWh in verticale sulla ringhiera (PVGIS)."),
        "citta_d": "Fotovoltaico da balcone a {c}: un kit da 800 Wp produce circa {k35} kWh l'anno (PVGIS) e fa risparmiare {eur} € l'anno. Mese per mese e rientro.",
        "st_k35": "kWh l'anno, inclinato 35°", "st_k90": "kWh l'anno, verticale", "st_eur": "di risparmio l'anno*", "st_anni": "anni per un kit da {kit} €*",
        "st_nota": "* Inclinato 35°, {quota}% dell'energia usata in casa, {prezzo} €/kWh (Eurostat, {periodo}).",
        "mesi_h": "Mese per mese a {c}", "mesi_th": ["Mese", "Inclinato 35°", "Verticale"],
        "mesi_testo": "Il mese migliore è {best} ({vb} kWh inclinato), il peggiore {worst} ({vw} kWh). In verticale la produzione d'inverno cala meno: a dicembre è il {pdic}% di quella inclinata, a luglio il {plug}%.",
        "risp_h": "Quanto si risparmia a {c}", "risp_th": ["Energia usata in casa", "Inclinato 35°", "Verticale"],
        "risp_testo": "Euro l'anno al prezzo di {prezzo} €/kWh. Più energia usi mentre il sole c'è (frigorifero, router, lavatrice e lavastoviglie di giorno), più risparmi.",
        "rientro_h": "In quanti anni si ripaga", "rientro_th": ["Prezzo del kit", "Inclinato 35°", "Verticale"],
        "rientro_testo": "Anni di rientro con il {quota}% dell'energia usata in casa. Non sono prezzi di negozi: metti il prezzo del tuo kit nel calcolatore.",
        "conf_testo": "{c} è al {pos}° posto su {n} città italiane del calcolatore per produzione con il kit inclinato; la mediana delle città è {med} kWh.",
        "altre_h": "Altre città", "citta_faq_q1": "Quanto produce un pannello da balcone a {c}?",
        "citta_faq_a1": "Secondo PVGIS, a {c} un kit da 800 Wp rivolto a sud produce circa {k35} kWh l'anno inclinato a 35° e {k90} kWh in verticale. Con il {quota}% usato in casa a {prezzo} €/kWh il risparmio è di circa {eur} € l'anno.",
        "citta_faq_q2": "Servono permessi a {c}?",
        "citta_faq_a2": "Le regole sono nazionali: sotto 800 W basta la Comunicazione Unica al distributore, gratis (ARERA). In condominio l'impianto del singolo appartamento non è soggetto ad autorizzazione, se non tocca parti comuni: la facciata lo è (art. 1117 c.c.) e la ringhiera può esserlo secondo il regolamento di condominio. Se servono modifiche alle parti comuni, ne dai comunicazione all'amministratore (art. 1122-bis).",
        "citta_faq_s2": ["it-arera-scheda", "it-cc-1117", "it-cc-1122bis"],
        "aff_h": "Kit da balcone", "aff_tag": "Affiliazione",
        "aff_testo": "Prima di comprare, controlla le regole qui sopra: un kit in vendita non vuol dire che puoi collegarlo senza Comunicazione Unica.",
        "contatti_t": "Contatti | Solare da balcone", "contatti_h1": "Scrivici",
        "contatti_sub": "Hai trovato un errore o una regola cambiata? Scrivici: controlliamo sulla fonte ufficiale e correggiamo.",
        "contatti_d": "Contatti di Solare da balcone: segnala un errore o una regola cambiata sul fotovoltaico da balcone.",
        "f_email": "La tua email", "f_pagina": "Pagina o città (facoltativo)", "f_msg": "Messaggio", "f_hp": "Non compilare",
        "f_consenso": "Ho letto l'<a href=\"{priv}\">informativa privacy</a>.", "f_invia": "Invia",
        "f_err": "Non è andato a buon fine: riprova.", "f_ok": "<strong>Grazie.</strong> Controlliamo e ti rispondiamo per email.",
        "f_nota": "Non possiamo dire se il tuo impianto è a norma: per questo serve un elettricista abilitato o il distributore.",
        "privacy_t": "Privacy | Solare da balcone", "privacy_h1": "Informativa privacy",
        "privacy_d": "Informativa privacy di Solare da balcone: cosa raccogliamo con il modulo di contatto, il contatore visite senza cookie e la pubblicità.",
        "agg": "Ultimo aggiornamento", "footer": ("<strong>Solare da balcone</strong> riassume le regole ufficiali sul fotovoltaico da balcone e calcola la produzione con i dati PVGIS "
                   "della Commissione europea. È un sito indipendente, non legato a ARERA, GSE, distributori o venditori. Non è una consulenza elettrica o legale: "
                   "prima di collegare un kit verifica con il distributore e con un elettricista abilitato."),
        "esplora": "Esplora", "f_dati": "Dati: PVGIS © European Communities, 2001-2026 · Prezzi Eurostat ({periodo}) · Fonti verificate il {data}",
        "briciole_home": "Italia", "altre_lingue": "Altri Paesi",
        "sezione_regole": "Regole", "sezione_citta": "Città",
    },
    "es": {
        "html": "es-ES", "og": "es_ES", "nome": "Solar de balcón", "logo": ("Solar", "de balcón"),
        "paese": "España", "nel_paese": "en España", "prezzo_medio": "precio medio español",
        "p_home": "es/", "p_regole": "es/normativa-placas-solares-balcon/", "p_faq": "es/preguntas-frecuentes/",
        "p_contatti": "es/contacto/", "p_privacy": "es/privacidad/", "p_citta": "es/placas-solares-balcon-{s}/",
        "menu": [("regole", "Normativa"), ("calc", "Calculadora"), ("citta", "Ciudades"), ("faq", "Preguntas")],
        "skip": "Ir al contenido", "menu_lbl": "Menú", "tema": "Cambiar tema claro u oscuro", "lingua_lbl": "Idioma",
        "home_t": "Placas solares de balcón: normativa 2026 y calculadora",
        "home_h1": "Placas solares de balcón en España: la normativa y cuánto producen en tu ciudad",
        "home_eyebrow": "España · normativa y calculadora",
        "home_sub": ("Sin excedentes hace falta un mecanismo antivertido; por debajo de 800 VA no es obligatorio un circuito dedicado (IDAE). "
                     "En {citta}, un kit de 800 Wp inclinado hacia el sur produce unos <strong>{kwh} kWh al año</strong> (PVGIS)."),
        "home_d": "Placas solares de balcón en España: autoconsumo sin excedentes (RD 244/2019), kits enchufables, comunidad de vecinos y calculadora de ahorro en {n} ciudades.",
        "trust": ["Datos PVGIS de la Comisión Europea", "Precio de la electricidad Eurostat {periodo}", "Fuentes oficiales leídas el {data}"],
        "calc_h": "Calcula producción y ahorro", "calc_citta": "Ciudad", "calc_mont": "Montaje",
        "m35": "Inclinado 35° hacia el sur", "m90": "Vertical en la barandilla (hacia el sur)",
        "calc_w": "Potencia de los paneles (Wp)", "calc_quota": "Energía que usas en casa mientras hay sol",
        "calc_prezzo": "Precio de la electricidad (€/kWh)", "calc_kit": "Precio del kit (€)",
        "out_prod": "Producción", "out_auto": "Usada en casa", "out_eur": "Ahorro", "out_anni": "Amortización",
        "u_kwh_anno": "kWh/año", "u_eur_anno": "€/año", "u_anni": "años",
        "calc_mesi": "Producción mes a mes (kWh)", "calc_oltre": "Más de 800 W: revisa antes la normativa.",
        "calc_nota": ("Fórmula: producción PVGIS del kit de 800 Wp × potencia/800 × parte usada en casa × precio = ahorro anual; "
                      "precio del kit ÷ ahorro = años de amortización. Un kit sin excedentes no vierte la energía que sobra."),
        "mesi": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"],
        "mesi_l": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
        "ipotesi_h": "Cómo calculamos",
        "ipotesi": [
            "Producción: PVGIS 5.3 de la Comisión Europea (base de datos {db}, años {anni}), kit de 0,8 kWp de silicio cristalino orientado al sur, pérdidas del sistema del 14 % (valor por defecto de PVGIS), con las sombras del relieve y sin sombras de edificios o árboles.",
            "Dos montajes: inclinado 35° (sobre un soporte) o vertical, colgado de la barandilla. Con otra orientación la producción baja.",
            "Precio: {prezzo} €/kWh, media de Eurostat para hogares que consumen entre 2.500 y 5.000 kWh al año, impuestos incluidos ({periodo}). Tu factura puede ser distinta: pon tu precio.",
            "Energía usada en casa: hipótesis del {quota} %, cámbiala. Solo cuenta lo que consumes mientras hay sol; en la modalidad sin excedentes, lo que sobra no se vierte ni se paga.",
            "Amortización: precio del kit dividido por el ahorro del primer año, sin intereses, mantenimiento, pérdida de rendimiento de los paneles ni cambios en el precio de la luz.",
        ],
        "tab_h": "Cuánto produce un kit de 800 Wp en las ciudades españolas",
        "tab_th": ["Ciudad", "Inclinado 35°", "Vertical", "Ahorro*"],
        "tab_nota": "* Inclinado 35°, {quota} % usado en casa, {prezzo} €/kWh. kWh al año según PVGIS. Las ciudades con enlace tienen una página con los datos mes a mes. Canarias, Ceuta y Melilla tienen impuestos distintos: pon tu precio.",
        "regole_breve_h": "La normativa en breve", "regole_tutte": "Toda la normativa, con las fuentes",
        "faq_h": "Preguntas frecuentes", "faq_tutte": "Todas las preguntas",
        "fonti_h": "Fuentes", "letta": "leída el {data} (HTTP 200)", "non_letta": "no leída: {motivo}",
        "fonte_nostra": "nota nuestra", "centro_risorse": "centro de recursos, no un organismo público",
        "fonti_dati": ("Producción: PVGIS © European Communities, 2001-2026, reutilización libre citando la fuente. Precio: Eurostat, "
                       "nrg_pc_204, reutilización autorizada citando la fuente."),
        "regole_t": "Placas solares de balcón: normativa en España 2026",
        "regole_d": "Normativa de las placas solares de balcón en España: sin excedentes, antivertido, 800 VA (IDAE), registro, comunidad e IBI. Revisada el {data}.",
        "regole_eyebrow": "Normativa · España", "regole_sub": "Lo que dicen el BOE y la guía del IDAE. Revisado el {data}.",
        "prima_h": "Antes de comprar",
        "prima": ["Comprueba si el kit tiene mecanismo antivertido (sin excedentes) y qué documentación entrega el vendedor.",
                  "Consulta qué pide tu comunidad autónoma para el registro de autoconsumo.",
                  "En un piso, avisa antes a la comunidad y no cambies la fachada sin su acuerdo."],
        "prima_nota": "Este sitio resume fuentes oficiales: no es asesoramiento eléctrico ni legal. Para la instalación de casa, consulta a una empresa instaladora habilitada.",
        "faq_t": "Placas solares de balcón: preguntas frecuentes (2026)",
        "faq_d": "Las preguntas más buscadas sobre placas solares de balcón en España, con respuestas de fuentes oficiales: comunidad, 800 W, enchufe, batería y ahorro.",
        "faq_eyebrow": "Preguntas · España", "faq_sub": "Las preguntas salen de las búsquedas de Google; las respuestas, de las fuentes oficiales.",
        "citta_t": "Placas solares de balcón en {c}: producción y ahorro",
        "citta_h1": "Placas solares de balcón en {c}: cuánto producen y cuánto ahorras",
        "citta_eyebrow": "{c} · datos PVGIS",
        "citta_sub": ("En {c}, un kit de 800 Wp orientado al sur produce unos <strong>{k35} kWh al año</strong> inclinado 35° y "
                      "{k90} kWh en vertical en la barandilla (PVGIS)."),
        "citta_d": "Placas solares de balcón en {c}: un kit de 800 Wp produce unos {k35} kWh al año (PVGIS) y ahorra {eur} € al año. Mes a mes y amortización.",
        "st_k35": "kWh al año, inclinado 35°", "st_k90": "kWh al año, vertical", "st_eur": "de ahorro al año*", "st_anni": "años para un kit de {kit} €*",
        "st_nota": "* Inclinado 35°, {quota} % de la energía usada en casa, {prezzo} €/kWh (Eurostat, {periodo}).",
        "mesi_h": "Mes a mes en {c}", "mesi_th": ["Mes", "Inclinado 35°", "Vertical"],
        "mesi_testo": "El mejor mes es {best} ({vb} kWh inclinado) y el peor, {worst} ({vw} kWh). En vertical la producción baja menos en invierno: en diciembre es el {pdic} % de la inclinada y en julio, el {plug} %.",
        "risp_h": "Cuánto se ahorra en {c}", "risp_th": ["Energía usada en casa", "Inclinado 35°", "Vertical"],
        "risp_testo": "Euros al año al precio de {prezzo} €/kWh. Cuanta más energía uses mientras hay sol (nevera, router, lavadora y lavavajillas de día), más ahorras.",
        "rientro_h": "En cuántos años se amortiza", "rientro_th": ["Precio del kit", "Inclinado 35°", "Vertical"],
        "rientro_testo": "Años de amortización usando en casa el {quota} % de la energía. No son precios de tiendas: pon el precio de tu kit en la calculadora.",
        "conf_testo": "{c} ocupa el puesto {pos} de {n} ciudades españolas de la calculadora por producción con el kit inclinado; la mediana es de {med} kWh.",
        "altre_h": "Otras ciudades", "citta_faq_q1": "¿Cuánto produce una placa de balcón en {c}?",
        "citta_faq_a1": "Según PVGIS, en {c} un kit de 800 Wp orientado al sur produce unos {k35} kWh al año inclinado 35° y {k90} kWh en vertical. Usando en casa el {quota} % a {prezzo} €/kWh, el ahorro es de unos {eur} € al año.",
        "citta_faq_q2": "¿Qué normativa se aplica en {c}?",
        "citta_faq_a2": "La normativa básica es estatal: el Real Decreto 244/2019 exige un mecanismo antivertido para el autoconsumo sin excedentes, y la inscripción en el registro la hace de oficio la comunidad autónoma. En un piso, la Ley de Propiedad Horizontal obliga a avisar antes a la comunidad.",
        "citta_faq_s2": ["es-boe-rd244", "es-boe-lph"],
        "aff_h": "Kits de balcón", "aff_tag": "Afiliación",
        "aff_testo": "Antes de comprar, revisa la normativa: que un kit esté a la venta no significa que puedas conectarlo sin cumplir los requisitos.",
        "contatti_t": "Contacto | Solar de balcón", "contatti_h1": "Escríbenos",
        "contatti_sub": "¿Has visto un error o una norma que ha cambiado? Escríbenos: lo comprobamos en la fuente oficial y lo corregimos.",
        "contatti_d": "Contacto de Solar de balcón: avisa de un error o de una norma que ha cambiado sobre las placas solares de balcón.",
        "f_email": "Tu email", "f_pagina": "Página o ciudad (opcional)", "f_msg": "Mensaje", "f_hp": "No rellenar",
        "f_consenso": "He leído la <a href=\"{priv}\">política de privacidad</a>.", "f_invia": "Enviar",
        "f_err": "No se ha podido enviar: inténtalo de nuevo.", "f_ok": "<strong>Gracias.</strong> Lo comprobamos y te respondemos por email.",
        "f_nota": "No podemos decirte si tu instalación cumple la normativa: para eso hace falta una empresa instaladora habilitada.",
        "privacy_t": "Privacidad | Solar de balcón", "privacy_h1": "Política de privacidad",
        "privacy_d": "Política de privacidad de Solar de balcón: qué recogemos con el formulario de contacto, el contador de visitas sin cookies y la publicidad.",
        "agg": "Última actualización", "footer": ("<strong>Solar de balcón</strong> resume la normativa oficial sobre placas solares de balcón y calcula la producción con los datos PVGIS "
                   "de la Comisión Europea. Es un sitio independiente, sin relación con el MITECO, el IDAE, las distribuidoras ni los vendedores. No es asesoramiento eléctrico ni legal: "
                   "antes de conectar un kit, consulta a tu comunidad autónoma y a una empresa instaladora habilitada."),
        "esplora": "Explorar", "f_dati": "Datos: PVGIS © European Communities, 2001-2026 · Precios Eurostat ({periodo}) · Fuentes revisadas el {data}",
        "briciole_home": "España", "altre_lingue": "Otros países",
        "sezione_regole": "Normativa", "sezione_citta": "Ciudades",
    },
    "fr": {
        "html": "fr-FR", "og": "fr_FR", "nome": "Solaire de balcon", "logo": ("Solaire", "de balcon"),
        "paese": "France", "nel_paese": "en France", "prezzo_medio": "prix moyen français",
        "p_home": "fr/", "p_regole": "fr/reglementation-panneau-solaire-balcon/", "p_faq": "fr/questions-frequentes/",
        "p_contatti": "fr/contact/", "p_privacy": "fr/confidentialite/", "p_citta": "fr/panneau-solaire-balcon-{s}/",
        "menu": [("regole", "Réglementation"), ("calc", "Calculateur"), ("citta", "Villes"), ("faq", "Questions")],
        "skip": "Aller au contenu", "menu_lbl": "Menu", "tema": "Changer de thème clair ou sombre", "lingua_lbl": "Langue",
        "home_t": "Panneau solaire de balcon : réglementation 2026 et calcul",
        "home_h1": "Panneau solaire de balcon en France : la réglementation et ce qu’il produit dans votre ville",
        "home_eyebrow": "France · réglementation et calculateur",
        "home_sub": ("Même sans injection, le kit se déclare à Enedis (convention CACSI). "
                     "À {citta}, un kit de 800 Wc incliné plein sud produit environ <strong>{kwh} kWh par an</strong> (PVGIS)."),
        "home_d": "Panneau solaire de balcon en France : déclaration Enedis et CACSI, Consuel, mairie, copropriété et calculateur d’économies pour {n} villes (PVGIS).",
        "trust": ["Données PVGIS de la Commission européenne", "Prix de l’électricité Eurostat {periodo}", "Sources officielles lues le {data}"],
        "calc_h": "Calculez la production et l’économie", "calc_citta": "Ville", "calc_mont": "Pose",
        "m35": "Incliné à 35° plein sud", "m90": "À la verticale sur le garde-corps (plein sud)",
        "calc_w": "Puissance des panneaux (Wc)", "calc_quota": "Part consommée chez vous pendant qu’il y a du soleil",
        "calc_prezzo": "Prix de l’électricité (€/kWh)", "calc_kit": "Prix du kit (€)",
        "out_prod": "Production", "out_auto": "Consommée", "out_eur": "Économie", "out_anni": "Retour",
        "u_kwh_anno": "kWh/an", "u_eur_anno": "€/an", "u_anni": "ans",
        "calc_mesi": "Production mois par mois (kWh)", "calc_oltre": "Au-delà de 3 kVA, un nouveau circuit et un Consuel sont nécessaires.",
        "calc_nota": ("Formule : production PVGIS du kit de 800 Wc × puissance/800 × part consommée × prix = économie par an ; "
                      "prix du kit ÷ économie = années de retour. En autoconsommation sans injection, rien n’est payé pour le reste."),
        "mesi": ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."],
        "mesi_l": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"],
        "ipotesi_h": "Comment nous calculons",
        "ipotesi": [
            "Production : PVGIS 5.3 de la Commission européenne (base {db}, années {anni}), kit de 0,8 kWc en silicium cristallin orienté plein sud, pertes système de 14 % (valeur par défaut de PVGIS), ombres du relief comprises, sans ombre d’immeubles ou d’arbres.",
            "Deux poses : inclinée à 35° (sur un support) ou verticale, accrochée au garde-corps. Avec une autre orientation, la production baisse.",
            "Prix : {prezzo} €/kWh, moyenne Eurostat pour les ménages qui consomment entre 2 500 et 5 000 kWh par an, toutes taxes comprises ({periodo}). Votre facture peut être différente : indiquez votre prix.",
            "Part consommée : hypothèse de {quota} %, à modifier. Seule compte l’électricité utilisée pendant qu’il y a du soleil ; en autoconsommation totale, le reste n’est pas payé.",
            "Retour : prix du kit divisé par l’économie de la première année, sans intérêts, entretien, baisse de rendement des panneaux ni évolution du prix de l’électricité.",
        ],
        "tab_h": "Ce que produit un kit de 800 Wc dans les villes françaises",
        "tab_th": ["Ville", "Incliné 35°", "Vertical", "Économie*"],
        "tab_nota": "* Incliné à 35°, {quota} % consommé, {prezzo} €/kWh. kWh par an selon PVGIS. Les villes avec un lien ont une page avec les données mois par mois.",
        "regole_breve_h": "La réglementation en bref", "regole_tutte": "Toute la réglementation, avec les sources",
        "faq_h": "Questions fréquentes", "faq_tutte": "Toutes les questions",
        "fonti_h": "Sources", "letta": "lue le {data} (HTTP 200)", "non_letta": "non lue : {motivo}",
        "fonte_nostra": "note de notre part", "centro_risorse": "centre de ressources associatif, pas un organisme public",
        "fonti_dati": ("Production : PVGIS © European Communities, 2001-2026, réutilisation libre avec mention de la source. Prix : Eurostat, "
                       "nrg_pc_204, réutilisation autorisée avec mention de la source."),
        "regole_t": "Panneau solaire de balcon : réglementation en France 2026",
        "regole_d": "Réglementation des panneaux solaires de balcon en France : déclaration Enedis, CACSI, Consuel, 3 kVA, mairie et copropriété. Sources du {data}.",
        "regole_eyebrow": "Réglementation · France", "regole_sub": "Ce que disent Enedis et Service-Public.fr. Vérifié le {data}.",
        "prima_h": "Avant d’acheter",
        "prima": ["Vérifiez que l’onduleur est conforme à la norme NF EN 50549-1 et que le kit est livré assemblé.",
                  "Déclarez le kit sur Enedis-Connect et acceptez la CACSI avant de le brancher.",
                  "En copropriété, demandez au syndic avant de fixer le kit à la façade ou au garde-corps."],
        "prima_nota": "Ce site résume des sources officielles : ce n’est pas un conseil électrique ou juridique. Pour votre installation, demandez à un électricien qualifié.",
        "faq_t": "Panneau solaire de balcon : questions fréquentes (2026)",
        "faq_d": "Panneaux solaires de balcon : les questions les plus recherchées en France, avec les sources officielles (réglementation, mairie, copropriété, batterie).",
        "faq_eyebrow": "Questions · France", "faq_sub": "Les questions viennent des recherches Google ; les réponses, des sources officielles.",
        "citta_t": "Panneau solaire de balcon à {c} : production et économies",
        "citta_h1": "Panneau solaire de balcon à {c} : ce qu’il produit et ce qu’il fait économiser",
        "citta_eyebrow": "{c} · données PVGIS",
        "citta_sub": ("À {c}, un kit de 800 Wc plein sud produit environ <strong>{k35} kWh par an</strong> incliné à 35° et "
                      "{k90} kWh à la verticale sur le garde-corps (PVGIS)."),
        "citta_d": "Panneau solaire de balcon à {c} : un kit de 800 Wc produit environ {k35} kWh par an (PVGIS), soit {eur} € d’économie par an. Mois par mois et retour.",
        "st_k35": "kWh par an, incliné 35°", "st_k90": "kWh par an, vertical", "st_eur": "d’économie par an*", "st_anni": "ans pour un kit de {kit} €*",
        "st_nota": "* Incliné à 35°, {quota} % de l’électricité consommée chez vous, {prezzo} €/kWh (Eurostat, {periodo}).",
        "mesi_h": "Mois par mois à {c}", "mesi_th": ["Mois", "Incliné 35°", "Vertical"],
        "mesi_testo": "Le meilleur mois est {best} ({vb} kWh incliné), le moins bon {worst} ({vw} kWh). À la verticale, la production baisse moins en hiver : en décembre elle vaut {pdic} % de la pose inclinée, en juillet {plug} %.",
        "risp_h": "Ce que l’on économise à {c}", "risp_th": ["Part consommée", "Incliné 35°", "Vertical"],
        "risp_testo": "Euros par an au prix de {prezzo} €/kWh. Plus vous consommez pendant qu’il y a du soleil (réfrigérateur, box internet, lave-linge et lave-vaisselle en journée), plus vous économisez.",
        "rientro_h": "En combien d’années le kit est remboursé", "rientro_th": ["Prix du kit", "Incliné 35°", "Vertical"],
        "rientro_testo": "Années de retour avec {quota} % de l’électricité consommée chez vous. Ce ne sont pas des prix de magasins : indiquez le prix de votre kit dans le calculateur.",
        "conf_testo": "{c} est {pos_fr} sur {n} villes françaises du calculateur pour la production avec le kit incliné ; la médiane est de {med} kWh.",
        "altre_h": "Autres villes", "citta_faq_q1": "Combien produit un panneau de balcon à {c} ?",
        "citta_faq_a1": "Selon PVGIS, à {c}, un kit de 800 Wc plein sud produit environ {k35} kWh par an incliné à 35° et {k90} kWh à la verticale. Avec {quota} % consommé à {prezzo} €/kWh, l’économie est d’environ {eur} € par an.",
        "citta_faq_q2": "Quelles démarches à {c} ?",
        "citta_faq_a2": "Les règles sont nationales : selon Enedis, le kit doit être déclaré même sans injection, sur Enedis-Connect, avec la convention CACSI. Un kit assemblé en usine et conforme à la norme NF EN 50549-1 peut être dispensé de Consuel.",
        "citta_faq_s2": ["fr-enedis-autoconso"],
        "aff_h": "Kits de balcon", "aff_tag": "Affiliation",
        "aff_testo": "Avant d’acheter, lisez la réglementation : un kit en vente ne vous dispense pas de la déclaration à Enedis.",
        "contatti_t": "Contact | Solaire de balcon", "contatti_h1": "Nous écrire",
        "contatti_sub": "Vous avez vu une erreur ou une règle qui a changé ? Écrivez-nous : nous vérifions sur la source officielle et nous corrigeons.",
        "contatti_d": "Contact de Solaire de balcon : signalez une erreur ou une règle qui a changé sur les panneaux solaires de balcon.",
        "f_email": "Votre e-mail", "f_pagina": "Page ou ville (facultatif)", "f_msg": "Message", "f_hp": "Ne pas remplir",
        "f_consenso": "J’ai lu la <a href=\"{priv}\">politique de confidentialité</a>.", "f_invia": "Envoyer",
        "f_err": "L’envoi n’a pas fonctionné : réessayez.", "f_ok": "<strong>Merci.</strong> Nous vérifions et nous vous répondons par e-mail.",
        "f_nota": "Nous ne pouvons pas dire si votre installation est conforme : pour cela, il faut un électricien qualifié ou votre gestionnaire de réseau.",
        "privacy_t": "Confidentialité | Solaire de balcon", "privacy_h1": "Politique de confidentialité",
        "privacy_d": "Politique de confidentialité de Solaire de balcon : ce que nous collectons avec le formulaire de contact, le compteur de visites sans cookies et la publicité.",
        "agg": "Dernière mise à jour", "footer": ("<strong>Solaire de balcon</strong> résume la réglementation officielle des panneaux solaires de balcon et calcule la production avec les données PVGIS "
                   "de la Commission européenne. C’est un site indépendant, sans lien avec Enedis, la CRE, l’ADEME ou les vendeurs. Ce n’est pas un conseil électrique ou juridique : "
                   "avant de brancher un kit, déclarez-le à votre gestionnaire de réseau et demandez à un électricien qualifié."),
        "esplora": "Explorer", "f_dati": "Données : PVGIS © European Communities, 2001-2026 · Prix Eurostat ({periodo}) · Sources vérifiées le {data}",
        "briciole_home": "France", "altre_lingue": "Autres pays",
        "sezione_regole": "Réglementation", "sezione_citta": "Villes",
    },
}

PRIVACY = {
    "it": """<h2>Chi è il titolare</h2><p>Il titolare del trattamento è il gestore di questo sito, una persona fisica con sede in Italia, che lo cura come progetto indipendente. Per qualsiasi richiesta usa il <a href="{contatti}">modulo di contatto</a>.</p>
<h2>Cosa raccogliamo</h2><p>Solo ciò che scrivi nel modulo di contatto: email, pagina o città e messaggio, più la pagina da cui arrivi. Il calcolatore funziona nel tuo browser: i numeri che inserisci non ci vengono inviati. Se cambi il tema chiaro o scuro, la scelta resta solo nel tuo browser.</p>
<h2>Perché</h2><p>Per rispondere ai messaggi e correggere il sito. La base giuridica è il tuo consenso (art. 6.1.a GDPR), che puoi revocare quando vuoi.</p>
<h2>Chi tratta i dati per noi</h2><p>Il sito e il modulo sono ospitati da Netlify, Inc., che conserva i messaggi per nostro conto e può trattarli fuori dall'UE con le garanzie previste dal GDPR (clausole contrattuali tipo). Netlify tiene registri tecnici del server (come gli indirizzi IP) per sicurezza. Non vendiamo né cediamo i tuoi dati.</p>
{cookie}
<h2>Per quanto tempo</h2><p>I messaggi si conservano fino a 12 mesi dall'ultimo scambio.</p>
<h2>I tuoi diritti</h2><p>Puoi chiedere accesso, rettifica, cancellazione, limitazione, portabilità e opposizione (artt. 15-22 GDPR) e puoi reclamare al Garante per la protezione dei dati personali (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>) o all'autorità del Paese in cui vivi.</p>""",
    "es": """<h2>Responsable</h2><p>El responsable del tratamiento es quien gestiona este sitio, una persona física establecida en Italia que lo mantiene como proyecto independiente. Para cualquier solicitud, usa el <a href="{contatti}">formulario de contacto</a>.</p>
<h2>Qué recogemos</h2><p>Solo lo que escribes en el formulario de contacto: email, página o ciudad y mensaje, además de la página desde la que llegas. La calculadora funciona en tu navegador: los números que introduces no se nos envían. Si cambias el tema claro u oscuro, la elección se guarda solo en tu navegador.</p>
<h2>Para qué</h2><p>Para responder a los mensajes y corregir el sitio. La base jurídica es tu consentimiento (art. 6.1.a del RGPD), que puedes retirar cuando quieras.</p>
<h2>Quién trata los datos por nosotros</h2><p>El sitio y el formulario están alojados en Netlify, Inc., que guarda los mensajes por nuestra cuenta y puede tratarlos fuera de la UE con las garantías del RGPD (cláusulas contractuales tipo). Netlify conserva registros técnicos del servidor (como direcciones IP) por seguridad. No vendemos ni cedemos tus datos.</p>
{cookie}
<h2>Durante cuánto tiempo</h2><p>Los mensajes se guardan hasta 12 meses después del último intercambio.</p>
<h2>Tus derechos</h2><p>Puedes pedir acceso, rectificación, supresión, limitación, portabilidad y oposición (arts. 15-22 del RGPD) y reclamar ante la Agencia Española de Protección de Datos (<a href="https://www.aepd.es" rel="noopener">aepd.es</a>) o ante la autoridad del país donde vives.</p>""",
    "fr": """<h2>Responsable du traitement</h2><p>Le responsable du traitement est la personne qui gère ce site, une personne physique établie en Italie qui le tient comme projet indépendant. Pour toute demande, utilisez le <a href="{contatti}">formulaire de contact</a>.</p>
<h2>Ce que nous collectons</h2><p>Seulement ce que vous écrivez dans le formulaire de contact : e-mail, page ou ville et message, ainsi que la page d’où vous venez. Le calculateur fonctionne dans votre navigateur : les chiffres que vous saisissez ne nous sont pas envoyés. Si vous changez de thème clair ou sombre, ce choix reste dans votre navigateur.</p>
<h2>Pourquoi</h2><p>Pour répondre aux messages et corriger le site. La base juridique est votre consentement (art. 6.1.a du RGPD), que vous pouvez retirer à tout moment.</p>
<h2>Qui traite les données pour nous</h2><p>Le site et le formulaire sont hébergés par Netlify, Inc., qui conserve les messages pour notre compte et peut les traiter hors de l’UE avec les garanties prévues par le RGPD (clauses contractuelles types). Netlify garde des journaux techniques du serveur (comme les adresses IP) pour la sécurité. Nous ne vendons ni ne cédons vos données.</p>
{cookie}
<h2>Combien de temps</h2><p>Les messages sont conservés jusqu’à 12 mois après le dernier échange.</p>
<h2>Vos droits</h2><p>Vous pouvez demander l’accès, la rectification, l’effacement, la limitation, la portabilité et vous opposer au traitement (art. 15 à 22 du RGPD), et saisir la CNIL (<a href="https://www.cnil.fr" rel="noopener">cnil.fr</a>) ou l’autorité du pays où vous vivez.</p>""",
}


# ---------------------------------------------------------------- numeri e date
def arrotonda(x, dec=0):
    """Arrotondamento a metà per eccesso, identico al JS del calcolatore (Math.floor(x*10^d+0.5)/10^d)."""
    p = 10 ** dec
    return math.floor(x * p + 0.5) / p


def fmt_num(x, lingua, dec=0):
    s = f"{arrotonda(x, dec):,.{dec}f}"  # 1,234.5
    intero, _, frazione = s.partition(".")
    cifre = intero.replace(",", "")
    neg = cifre.startswith("-")
    cifre = cifre.lstrip("-")
    sep = " " if lingua == "fr" else "."  # separatore delle migliaia sempre, anche in spagnolo (1.295)
    gruppi = ""
    while len(cifre) > 3:
        gruppi = sep + cifre[-3:] + gruppi
        cifre = cifre[:-3]
    gruppi = cifre + gruppi
    return ("-" if neg else "") + gruppi + ("," + frazione if frazione else "")


def data_lunga(d, lingua):
    m = T[lingua]["mesi_l"][d.month - 1]
    if lingua == "fr":
        return f"{'1er' if d.day == 1 else d.day} {m} {d.year}"
    if lingua == "es":
        return f"{d.day} de {m} de {d.year}"
    return f"{d.day} {m} {d.year}"


def periodo(lingua):
    p = PREZZI["paesi"][PAESE[lingua]]["periodo"]  # 2026-S1
    anno, sem = p.split("-")
    return {"it": f"{'primo' if sem == 'S1' else 'secondo'} semestre {anno}",
            "es": f"{'primer' if sem == 'S1' else 'segundo'} semestre de {anno}",
            "fr": f"{'premier' if sem == 'S1' else 'second'} semestre {anno}"}[lingua]


def prezzo(lingua):
    return PREZZI["paesi"][PAESE[lingua]]["eur_kwh"]


# ---------------------------------------------------------------- calcolatore (stessa formula del JS, controllata da verifica.py)
def calcola(e_y, watt, quota, prezzo_kwh, kit):
    prod = e_y * watt / POTENZA_RIF
    auto = prod * quota / 100
    eur = auto * prezzo_kwh
    anni = kit / eur if eur > 0 and kit > 0 else None
    return {"prod": prod, "auto": auto, "eur": eur, "anni": anni}


CALC_JS = r"""
function calcola(ey,w,quota,prezzo,kit){var prod=ey*w/800,auto=prod*quota/100,eur=auto*prezzo;
  return {prod:prod,auto:auto,eur:eur,anni:(eur>0&&kit>0)?kit/eur:null};}
function fmt(x,d,lang){d=d||0;var p=Math.pow(10,d),r=Math.floor(x*p+0.5)/p,l=String(lang||'it').slice(0,2),s=Math.abs(r).toFixed(d).split('.'),i=s[0];
  i=i.replace(/\B(?=(\d{3})+(?!\d))/g,l==='fr'?'\u202f':'.');
  return (r<0?'-':'')+i+(s[1]?','+s[1]:'');}
"""


def pv(lingua, slug):
    return PVGIS["citta"][f"{lingua}/{slug}"]


def risultato(lingua, slug, mont="a35", quota=QUOTA_DEF, kit=KIT_DEF):
    return calcola(pv(lingua, slug)[mont]["E_y"], POTENZA_RIF, quota, prezzo(lingua), kit)


def kwh(lingua, slug, mont="a35"):
    return fmt_num(pv(lingua, slug)[mont]["E_y"], lingua)


def eur(lingua, slug, mont="a35", quota=QUOTA_DEF):
    return fmt_num(risultato(lingua, slug, mont, quota)["eur"], lingua)


def anni(lingua, slug, kit=KIT_DEF, mont="a35", quota=QUOTA_DEF):
    return fmt_num(risultato(lingua, slug, mont, quota, kit)["anni"], lingua, 1)


# ---------------------------------------------------------------- città con pagina (domanda vera + dato PVGIS proprio)
def citta_con_pagina(lingua):
    out = []
    for c in CITTA[lingua]:
        dom = DOMANDA["lingue"][lingua]["citta"].get(c["slug"], {}).get("domanda") or []
        if dom and f"{lingua}/{c['slug']}" in PVGIS["citta"]:
            out.append(dict(c, domanda=dom))
    return out


PAGINE_CITTA = {l: citta_con_pagina(l) for l in LINGUE_ATTIVE}


def url_citta(lingua, slug):
    return T[lingua]["p_citta"].format(s=slug)


def ha_pagina(lingua, slug):
    return any(c["slug"] == slug for c in PAGINE_CITTA[lingua])


def nome_citta(lingua, slug):
    return next(c["nome"] for c in CITTA[lingua] if c["slug"] == slug)


# ---------------------------------------------------------------- segnaposto nei testi di regole.json
def riempi(testo, lingua):
    def sost(m):
        parti = m.group(1).split(":")
        k = parti[0]
        if k == "prezzo":
            return fmt_num(prezzo(lingua), lingua, 4)
        if k == "periodo":
            return periodo(lingua)
        if k == "kwh35":
            return kwh(lingua, parti[1], "a35")
        if k == "kwh90":
            return kwh(lingua, parti[1], "a90")
        if k == "eur":
            return eur(lingua, parti[1])
        if k == "anni":
            return anni(lingua, parti[1], int(parti[2]))
        raise SystemExit(f"segnaposto sconosciuto: {m.group(0)}")
    return re.sub(r"\{([a-z0-9]+(?::[a-z0-9-]+)*)\}", sost, testo)


# ---------------------------------------------------------------- CSS, icone, JS
CSS = """
@font-face{font-family:"Fraunces";src:url(/assets/fonts/fraunces.woff2) format("woff2");font-weight:600 800;font-style:normal;font-display:swap}
@font-face{font-family:"Manrope";src:url(/assets/fonts/manrope.woff2) format("woff2");font-weight:400 800;font-style:normal;font-display:swap}
:root{--bg:#FAF7F0;--card:#FFFFFF;--ink:#172033;--ink-2:#3A4458;--ink-3:#5A6478;--line:#E4DFD3;--line-2:#CCC5B5;
--deep:#13203B;--deep-2:#1D2F55;--on-deep:#F3F1EA;--on-deep-2:#B9C1D6;--accent:#0B6B63;--accent-h:#07514B;--accent-2:#DDF0EC;--on-accent:#FFFFFF;
--sun:#F2A71B;--sun-2:#FFF1D2;--sun-ink:#8A5300;--warn:#8A4B00;--warn-2:#FFF0D6;--warn-l:#E9B35A;--mute:#F1ECE1;--bar1:#F2A71B;--bar2:#2E7D9A;
--sh-1:0 1px 2px rgba(19,32,59,.06),0 1px 1px rgba(19,32,59,.04);--sh-2:0 22px 44px -24px rgba(19,32,59,.38),0 2px 8px rgba(19,32,59,.06);
--r:14px;--r-s:10px;--serif:Fraunces,Georgia,"Times New Roman",serif;--sans:Manrope,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0C1220;--card:#131C2E;--ink:#E8EBF2;--ink-2:#BCC4D4;--ink-3:#97A1B5;--line:#232E45;--line-2:#33405C;
--deep:#080D18;--deep-2:#111B32;--on-deep:#E8EBF2;--on-deep-2:#A6B0C6;--accent:#5CCFC2;--accent-h:#8FE2D8;--accent-2:#11302E;--on-accent:#04201D;
--sun:#F6B941;--sun-2:#2E2410;--sun-ink:#F6B941;--warn:#F2BE6B;--warn-2:#2B2112;--warn-l:#8A6420;--mute:#18223A;--bar1:#F6B941;--bar2:#5BB6D6;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 22px 44px -24px rgba(0,0,0,.8),0 2px 8px rgba(0,0,0,.4)}}
:root[data-theme="dark"]{--bg:#0C1220;--card:#131C2E;--ink:#E8EBF2;--ink-2:#BCC4D4;--ink-3:#97A1B5;--line:#232E45;--line-2:#33405C;
--deep:#080D18;--deep-2:#111B32;--on-deep:#E8EBF2;--on-deep-2:#A6B0C6;--accent:#5CCFC2;--accent-h:#8FE2D8;--accent-2:#11302E;--on-accent:#04201D;
--sun:#F6B941;--sun-2:#2E2410;--sun-ink:#F6B941;--warn:#F2BE6B;--warn-2:#2B2112;--warn-l:#8A6420;--mute:#18223A;--bar1:#F6B941;--bar2:#5BB6D6;
--sh-1:0 1px 2px rgba(0,0,0,.45);--sh-2:0 22px 44px -24px rgba(0,0,0,.8),0 2px 8px rgba(0,0,0,.4)}
*{box-sizing:border-box}[hidden]{display:none!important}html{-webkit-text-size-adjust:100%;scroll-padding-top:16px}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:17px;line-height:1.6;overflow-wrap:break-word}
a{color:var(--accent);text-underline-offset:2px;text-decoration-thickness:1px}a:hover{color:var(--accent-h)}
:focus-visible{outline:3px solid var(--sun);outline-offset:2px;border-radius:4px}
.skip{position:absolute;left:-9999px;top:8px;background:var(--card);color:var(--ink);padding:8px 14px;border-radius:8px;z-index:50}.skip:focus{left:12px}
.ico{width:1.15em;height:1.15em;flex:none;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;vertical-align:-.2em}
.wrap{max-width:1100px;margin:0 auto;padding:0 16px}
header.top{background:var(--deep);color:var(--on-deep);position:relative;z-index:20;border-bottom:1px solid rgba(255,255,255,.06)}
header.top .wrap{display:flex;align-items:center;gap:10px;min-height:64px}
.logo{display:flex;align-items:center;gap:10px;font-family:var(--serif);font-weight:700;font-size:1.18rem;color:var(--on-deep);text-decoration:none;white-space:nowrap;margin-right:auto;line-height:1.1}
.logo:hover{color:#fff}.logo img{width:34px;height:34px;flex:none;display:block}.logo b{color:var(--sun);font-weight:inherit}
nav.menu{display:flex;gap:2px;font-size:.93rem}
nav.menu a{color:var(--on-deep-2);text-decoration:none;padding:7px 11px;border-radius:8px;white-space:nowrap}
nav.menu a:hover,nav.menu a[aria-current]{color:#fff;background:rgba(255,255,255,.08)}
.lingue{display:flex;gap:2px;font-size:.8rem;font-weight:800;letter-spacing:.04em}
.lingue a,.lingue span{color:var(--on-deep-2);text-decoration:none;padding:6px 7px;border-radius:7px}
.lingue span{color:var(--deep);background:var(--sun)}.lingue a:hover{color:#fff;background:rgba(255,255,255,.1)}
.tema{display:grid;place-items:center;width:40px;height:40px;border-radius:10px;border:1px solid rgba(255,255,255,.22);background:none;color:var(--on-deep);cursor:pointer;flex:none}
.tema:hover{border-color:var(--sun)}.tema .ico{width:19px;height:19px}
.tema .i-sun{display:none}:root[data-theme="dark"] .tema .i-sun{display:block}:root[data-theme="dark"] .tema .i-moon{display:none}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .tema .i-sun{display:block}:root:not([data-theme="light"]) .tema .i-moon{display:none}}
.nav-m{display:none}
.nav-m summary{list-style:none;cursor:pointer;display:grid;place-items:center;width:40px;height:40px;border:1px solid rgba(255,255,255,.25);border-radius:10px;color:var(--on-deep)}
.nav-m summary::-webkit-details-marker{display:none}.nav-m[open] summary{background:rgba(255,255,255,.1);border-color:var(--sun)}
.nav-m nav{position:absolute;left:16px;right:16px;top:calc(100% + 4px);background:var(--card);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh-2);padding:8px;display:grid}
.nav-m nav a{padding:12px 14px;border-radius:8px;color:var(--ink);text-decoration:none;font-weight:700}.nav-m nav a:hover{background:var(--accent-2)}
.lingue-m{display:flex;gap:6px;border-top:1px solid var(--line);margin-top:6px;padding:10px 8px 4px}.lingue-m a,.lingue-m span{padding:6px 12px!important;border-radius:8px;font-weight:800;font-size:.9rem;text-decoration:none}
.lingue-m span{background:var(--sun);color:#13203B}.lingue-m a{border:1px solid var(--line-2)}
.band{background:var(--deep);color:var(--on-deep);position:relative;overflow:hidden}
.band::before{content:"";position:absolute;inset:0;background:radial-gradient(520px 320px at 92% -12%,rgba(242,167,27,.42),transparent 64%),radial-gradient(700px 300px at 0% 130%,rgba(46,125,154,.25),transparent 60%),linear-gradient(180deg,var(--deep) 0,var(--deep-2) 100%)}
.band::after{content:"";position:absolute;left:0;right:0;bottom:0;height:46px;background:repeating-linear-gradient(90deg,rgba(255,255,255,.07) 0 2px,transparent 2px 26px);-webkit-mask:linear-gradient(0deg,#000,transparent);mask:linear-gradient(0deg,#000,transparent)}
.band-in{position:relative;z-index:1;padding:30px 16px 80px}
.band.corta .band-in{padding-bottom:44px}
.eyebrow{display:inline-flex;align-items:center;gap:8px;font-size:.78rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--sun);margin:0 0 12px}
h1,h2,h3{font-family:var(--serif);font-weight:700;letter-spacing:-.01em}
h1{font-size:clamp(1.8rem,5vw,2.75rem);line-height:1.12;margin:0 0 12px;text-wrap:balance;max-width:880px}
.band h1{color:#fff}
.sub{font-size:1.08rem;color:var(--on-deep-2);margin:0 0 16px;max-width:740px}.sub strong{color:#fff}
.trust{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:.88rem;color:var(--on-deep-2);margin:0;padding:0;list-style:none}
.trust li{display:inline-flex;align-items:center;gap:7px}.trust .ico{color:var(--sun)}
.briciole{font-size:.85rem;color:var(--on-deep-2);margin:0 0 14px}.briciole a{color:var(--on-deep)}
h2{font-size:clamp(1.35rem,3vw,1.62rem);line-height:1.22;margin:44px 0 12px;scroll-margin-top:16px}
h3{font-size:1.12rem;margin:22px 0 8px}
.lead{font-size:1.04rem;color:var(--ink-2);max-width:780px;margin:0 0 14px}
.small{font-size:.87rem;color:var(--ink-3)}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:20px;min-width:0;box-shadow:var(--sh-1)}
.pull{margin-top:-58px;position:relative;z-index:2}
.card.calc{box-shadow:var(--sh-2);padding:0!important;overflow:hidden}
.calc-h{display:flex;align-items:center;gap:10px;margin:0;padding:16px 20px;border-bottom:1px solid var(--line);font-size:1.2rem}
.calc-h .ico{color:var(--sun-ink);width:24px;height:24px}
.calc-g{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:0}
.calc-in{padding:18px 20px;display:grid;gap:14px;border-right:1px solid var(--line)}
.calc-in label,.calc-in fieldset{display:grid;gap:6px;font-weight:700;font-size:.92rem;margin:0;padding:0;border:0;min-width:0}
.calc-in legend{padding:0;margin-bottom:6px}
.calc-in select,.calc-in input[type=number]{font:inherit;font-weight:600;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:9px 12px;width:100%;min-height:46px}
.calc-in select:focus,.calc-in input:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 22%,transparent)}
.calc-2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.seg{display:grid;grid-template-columns:1fr 1fr;gap:6px}
.seg label{display:flex;gap:8px;align-items:flex-start;font-weight:600;font-size:.88rem;background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:9px 10px;cursor:pointer;line-height:1.3}
.seg input{margin:2px 0 0;accent-color:var(--accent)}.seg label:has(input:checked){border-color:var(--accent);background:var(--accent-2)}
.range{display:flex;align-items:center;gap:12px}.range input{flex:1;accent-color:var(--accent);min-width:0}.range output{font-weight:800;min-width:3.2em;text-align:right;font-variant-numeric:tabular-nums}
.calc-out{padding:18px 20px;background:var(--sun-2);display:grid;align-content:start;gap:12px}
.ris{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.ris div{background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:10px 12px;min-width:0}
.ris b{display:block;font-family:var(--serif);font-size:clamp(1.35rem,3.6vw,1.75rem);line-height:1.1;font-variant-numeric:tabular-nums;color:var(--ink)}
.ris span{display:block;font-size:.8rem;color:var(--ink-3);font-weight:700}
.ris .top b{color:var(--accent)}
.barre{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:3px;align-items:end;height:92px;margin:4px 0 0;padding:0;list-style:none}
.barre li{background:var(--bar1);border-radius:4px 4px 0 0;min-height:2px;position:relative}
.barre-l{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:3px;font-size:.66rem;color:var(--ink-3);text-align:center;margin:3px 0 0;padding:0;list-style:none}
.calc-f{margin:0;padding:12px 20px;border-top:1px solid var(--line);font-size:.84rem;color:var(--ink-3)}
.avviso-w{font-size:.84rem;color:var(--warn);font-weight:700;margin:0}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0;padding:0;overflow:hidden;box-shadow:var(--sh-2)}
.stat{padding:18px 20px;border-right:1px solid var(--line);min-width:0}.stat:last-child{border-right:0}
.stat b{display:block;font-family:var(--serif);font-size:clamp(1.6rem,4vw,2.1rem);line-height:1.08;font-variant-numeric:tabular-nums}
.stat span{display:block;font-size:.84rem;color:var(--ink-3);line-height:1.35;margin-top:6px}.stat.main b{color:var(--accent)}
.asof{margin:0;padding:10px 20px;background:var(--mute);border-top:1px solid var(--line);font-size:.86rem;color:var(--ink-2);grid-column:1/-1}
.nota{position:relative;background:var(--warn-2);border:1px solid color-mix(in srgb,var(--warn-l) 60%,transparent);padding:13px 16px 13px 48px;border-radius:var(--r-s);font-size:.94rem;margin:20px 0;color:var(--ink)}
.nota .ico{position:absolute;left:16px;top:15px;color:var(--warn);width:20px;height:20px}.nota p{margin:0 0 6px}.nota p:last-child{margin:0}
.nota.info{background:var(--accent-2);border-color:color-mix(in srgb,var(--accent) 35%,transparent)}.nota.info .ico{color:var(--accent)}
.tab{border:1px solid var(--line);border-radius:var(--r);background:var(--card);box-shadow:var(--sh-1);overflow-x:auto;-webkit-overflow-scrolling:touch}
table{border-collapse:collapse;width:100%;font-size:.93rem}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
td.n,th.n{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
th{background:var(--mute);font-size:.74rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2);vertical-align:bottom}
tbody tr:last-child td{border-bottom:0}
td .bar{display:inline-block;height:8px;border-radius:4px;background:var(--bar1);vertical-align:middle;margin-right:8px}
td .bar.v{background:var(--bar2)}
.sintesi{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px 18px;margin:0;padding:0}
.sintesi div{border-left:3px solid var(--sun);padding:2px 0 2px 12px}
.sintesi dt{font-size:.74rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3)}.sintesi dd{margin:2px 0 0;font-weight:700}
.testo p,.testo li{max-width:790px}.testo li{margin-bottom:8px}
.punti{margin:0 0 8px;padding-left:20px}.punti li{margin-bottom:9px}.punti li.nostra{list-style:circle;color:var(--ink-2)}
.etich{display:inline-block;font-size:.7rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-3);border:1px solid var(--line-2);border-radius:999px;padding:0 7px;margin-left:4px;vertical-align:1px}
sup.ref{font-size:.72em;line-height:0;margin-left:2px;white-space:nowrap}sup.ref a{text-decoration:none;font-weight:800}
.faq{border-top:1px solid var(--line);padding:4px 0 6px}.faq h3{margin:16px 0 6px}.faq p{margin:0 0 6px;max-width:790px}
.griglia{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin:0;padding:0;list-style:none}
.griglia a{display:flex;flex-direction:column;gap:2px;height:100%;background:var(--card);border:1px solid var(--line);border-radius:var(--r-s);padding:12px 14px;text-decoration:none;color:var(--ink);font-weight:800;box-shadow:var(--sh-1);transition:border-color .15s,transform .15s}
.griglia a:hover{border-color:var(--accent);transform:translateY(-1px)}.griglia a small{font-weight:600;color:var(--ink-3);font-size:.86rem}
.cols{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px}
.prima{border-left:4px solid var(--sun)}.prima h2{margin-top:0;font-size:1.2rem}.prima ol{margin:0 0 10px;padding-left:20px}.prima li{margin-bottom:6px}
.fonti-box{margin-top:44px;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:var(--r-s);padding:16px 20px;font-size:.9rem;color:var(--ink-2)}
.fonti-box h2{display:flex;align-items:center;gap:8px;font-size:1.1rem;margin:0 0 8px;color:var(--ink)}.fonti-box h2 .ico{color:var(--accent)}
.fonti-box ol{margin:0 0 8px;padding-left:22px}.fonti-box li{margin-bottom:6px}.fonti-box p{margin:6px 0}.fonti-box a{overflow-wrap:anywhere}
.fonti-box li:target{background:var(--sun-2);border-radius:6px}
.btn{display:inline-flex;align-items:center;gap:8px;font:inherit;font-weight:800;background:var(--accent);color:var(--on-accent);border:0;border-radius:var(--r-s);padding:11px 18px;cursor:pointer;min-height:46px;text-decoration:none}
.btn:hover{background:var(--accent-h);color:var(--on-accent)}.btn:disabled{opacity:.6;cursor:wait}
.btn.sec{background:none;color:var(--accent);border:1.5px solid color-mix(in srgb,var(--accent) 55%,transparent)}.btn.sec:hover{background:var(--accent-2);color:var(--accent-h)}
.ad-slot{margin:24px 0}.ad-slot:empty{display:none}
.aff-box{margin:24px 0;background:var(--accent-2);border:1px solid color-mix(in srgb,var(--accent) 30%,transparent);border-radius:var(--r);padding:18px 20px}
.aff-box h2{margin:0 0 8px;font-size:1.2rem}.aff-box ul{margin:0 0 10px;padding-left:20px}.aff-box p{margin:0 0 8px}
.aff-tag{display:inline-block;vertical-align:middle;margin-left:6px;font-family:var(--sans);font-size:.68rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);border:1px solid var(--line-2);border-radius:999px;padding:1px 8px}
.paesi{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.paesi a{display:flex;flex-direction:column;gap:6px;text-decoration:none;color:var(--ink);height:100%}
.paesi b{font-family:var(--serif);font-size:1.3rem}.paesi span{color:var(--ink-2);font-size:.95rem}.paesi em{font-style:normal;font-weight:800;color:var(--accent);margin-top:auto}
a.card:hover{border-color:var(--accent)}
.form{display:grid;gap:14px}.form label{display:grid;gap:6px;font-weight:700;font-size:.95rem}
.form input,.form textarea{font:inherit;color:var(--ink);background:var(--bg);border:1.5px solid var(--line-2);border-radius:var(--r-s);padding:10px 12px;width:100%;min-height:46px}
.form .check{display:flex;gap:10px;align-items:flex-start;font-weight:500;font-size:.9rem;color:var(--ink-2)}.form .check input{width:auto;min-height:0;margin-top:4px}
.hp{position:absolute;left:-9999px}.ok{background:var(--accent-2);border:1px solid var(--accent);padding:14px;border-radius:var(--r-s)}.errore{color:#B3261E;font-weight:700}
footer{margin-top:56px;background:var(--deep);color:var(--on-deep-2);font-size:.88rem;padding:40px 0 34px}
footer a{color:var(--on-deep)}footer a:hover{color:var(--sun)}
footer .f-grid{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(0,1fr);gap:28px}
footer .logo{margin-bottom:12px}footer p{margin:0 0 10px;max-width:680px}footer strong{color:var(--on-deep)}
footer ul{list-style:none;margin:0;padding:0;display:grid;gap:8px}
footer h2{font-family:var(--sans);font-size:.76rem;letter-spacing:.12em;text-transform:uppercase;color:var(--sun);margin:4px 0 12px}
footer .f-base{border-top:1px solid rgba(255,255,255,.12);margin-top:24px;padding-top:16px;font-size:.82rem;max-width:none}
@media (max-width:880px){.stats{grid-template-columns:repeat(2,minmax(0,1fr))}.stat:nth-child(2){border-right:0}.stat:nth-child(-n+2){border-bottom:1px solid var(--line)}.cols,.paesi{grid-template-columns:1fr}
.calc-g{grid-template-columns:1fr}.calc-in{border-right:0;border-bottom:1px solid var(--line)}}
@media (max-width:780px){nav.menu{display:none}.nav-m{display:block}header.top .wrap{min-height:60px}footer .f-grid{grid-template-columns:1fr}.band-in{padding-top:22px}}
@media (max-width:480px){header.top .lingue{display:none}}
@media (max-width:560px){.calc-2,.seg{grid-template-columns:1fr}.card,.calc-in,.calc-out{padding:16px}.calc-h{padding:14px 16px}.calc-f{padding:12px 16px}
.stat{padding:14px}.griglia{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.griglia a{padding:10px 12px;font-size:.95rem}
th,td{padding:8px 8px}table{font-size:.88rem}.logo{font-size:1.02rem;gap:8px}.logo img{width:30px;height:30px}.lingue a,.lingue span{padding:5px 5px}
td .bar{display:none}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""
CSS = re.sub(r"\n", "", CSS)

ICONE = {
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "moon": '<path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6 6 6M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4"/>',
    "check": '<circle cx="12" cy="12" r="9.5"/><path d="M8 12.5l2.8 2.8L16.5 9.5"/>',
    "calendar": '<rect x="3" y="4.5" width="18" height="17" rx="2.5"/><path d="M16 2.5v4M8 2.5v4M3 10h18"/>',
    "alert": '<path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17h.01"/>',
    "info": '<circle cx="12" cy="12" r="9.5"/><path d="M12 11v6M12 7.5h.01"/>',
    "doc": '<path d="M14 2.5H6.5A2 2 0 0 0 4.5 4.5v15a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V8z"/><path d="M14 2.5V8h5.5M8 13h8M8 17h5"/>',
    "panel": '<path d="M4 4h16l-2 10H6z"/><path d="M5 9h14M10 4l-1 10M14 4l1 10M12 14v5M8 20h8"/>',
    "plug": '<path d="M9 3v5M15 3v5M6.5 8h11v3a5.5 5.5 0 0 1-11 0zM12 16.5V21"/>',
    "shield": '<path d="M12 22s8-3.5 8-10V5.5L12 2.5 4 5.5V12c0 6.5 8 10 8 10z"/><path d="M8.5 12l2.5 2.5 4.5-4.5"/>',
    "pin": '<path d="M12 21.5s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="9.5" r="2.5"/>',
}
SPRITE = ('<svg xmlns="http://www.w3.org/2000/svg">' +
          "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONE.items()) + "</svg>\n")
ICONS_FILE = f"icons.{hashlib.sha256(SPRITE.encode()).hexdigest()[:10]}.svg"


def ico(nome, cls="ico"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="/assets/{ICONS_FILE}#i-{nome}"/></svg>'


# Marchio: sole che sorge dietro la ringhiera di un balcone (tessera blu notte, sole ambra)
MARCHIO = ('<rect width="40" height="40" rx="10" fill="#13203B"/>'
           '<circle cx="20" cy="21" r="8" fill="#F2A71B"/>'
           '<path d="M20 7.5v3M9.8 11.6l2.1 2.1M30.2 11.6l-2.1 2.1M6.5 21h3M30.5 21h3" stroke="#F2A71B" stroke-width="2.2" stroke-linecap="round"/>'
           '<rect x="6" y="23" width="28" height="11" rx="1.5" fill="#13203B"/>'
           '<path d="M6.5 24h27M6.5 33.5h27M11 24v9.5M16.5 24v9.5M23.5 24v9.5M29 24v9.5" stroke="#F3F1EA" stroke-width="2" stroke-linecap="round"/>')
FAVICON_SVG = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">{MARCHIO}</svg>\n'

TEMA_JS = "(function(){try{var t=localStorage.getItem('sb-theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();"
APP_JS = CALC_JS + r"""
(function(){
  var b=document.querySelector('[data-tema]');
  if(b)b.addEventListener('click',function(){var r=document.documentElement,c=r.getAttribute('data-theme');
    if(!c)c=window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
    var n=c==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('sb-theme',n);}catch(e){}});
  var ref='';try{ref=new URLSearchParams(location.search).get('ref')||document.referrer||'direct';}catch(e){ref='direct';}
  document.querySelectorAll('input[name=source]').forEach(function(i){i.value=String(ref).slice(0,200);});
  document.querySelectorAll('form.ajax').forEach(function(form){form.addEventListener('submit',function(ev){ev.preventDefault();
    var err=form.querySelector('[data-errore]');err.hidden=true;if(!form.checkValidity()){form.reportValidity();return;}
    var bt=form.querySelector('button');bt.disabled=true;
    fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(new FormData(form)).toString()})
    .then(function(r){if(!r.ok)throw new Error(r.status);form.hidden=true;form.parentNode.querySelector('[data-ok]').hidden=false;})
    .catch(function(){err.hidden=false;bt.disabled=false;});});});
  var f=document.querySelector('[data-calc]');if(!f)return;
  var D=JSON.parse(document.getElementById('calc-dati').textContent),L=document.documentElement.lang||'it';
  function n(x,d){return fmt(x,d,L);}
  function v(name){var e=f.elements[name];return e?parseFloat(String(e.value).replace(',','.')):NaN;}
  function out(k,t){var e=f.querySelector('[data-o='+k+']');if(e)e.textContent=t;}
  function aggiorna(){
    var c=D.citta.filter(function(x){return x.s===f.elements.citta.value;})[0]||D.citta[0];
    var m=f.querySelector('input[name=mont]:checked').value,w=v('w'),q=v('quota'),p=v('prezzo'),k=v('kit');
    if(!(w>0))w=0;if(!(q>=0))q=0;if(!(p>=0))p=0;if(!(k>=0))k=0;
    var r=calcola(c[m],w,q,p,k);
    out('prod',n(r.prod));out('auto',n(r.auto));out('eur',n(r.eur));
    out('anni',r.anni===null?'–':n(r.anni,1));out('quota',n(q)+' %');
    var mesi=c[m==='a35'?'m35':'m90'],max=Math.max.apply(null,c.m35.concat(c.m90));
    f.querySelectorAll('.barre li').forEach(function(li,i){var val=mesi[i]*w/800;li.style.height=Math.max(2,Math.round(mesi[i]/max*100))+'%';
      li.title=D.mesi[i]+': '+n(val)+' kWh';});
    var av=f.querySelector('[data-oltre]');if(av)av.hidden=!(w>D.soglia);
  }
  f.addEventListener('input',aggiorna);f.addEventListener('change',aggiorna);f.addEventListener('submit',function(e){e.preventDefault();});
  aggiorna();
})();
"""


def _impronta(testo):
    return hashlib.sha256(testo.encode("utf-8")).hexdigest()[:10]


ASSET = {
    f"site.{_impronta(CSS)}.css": CSS,
    f"app.{_impronta(APP_JS)}.js": APP_JS.strip() + "\n",
    f"favicon.{_impronta(FAVICON_SVG)}.svg": FAVICON_SVG,
    ICONS_FILE: SPRITE,
}
CSS_FILE, JS_FILE, FAVICON_FILE, _ = ASSET
LOGO = f'<img src="/assets/{FAVICON_FILE}" width="34" height="34" alt="">'


# ---------------------------------------------------------------- fonti e rimandi numerati
class Rimandi:
    """Numera le fonti citate in una pagina, nell'ordine in cui compaiono."""

    def __init__(self, lingua):
        self.lingua = lingua
        self.ordine = []

    def ref(self, ids):
        if not ids:
            return ""
        nums = []
        for i in ids:
            if i not in REGOLE["fonti"]:
                raise SystemExit(f"fonte sconosciuta: {i}")
            if i not in self.ordine:
                self.ordine.append(i)
            nums.append(self.ordine.index(i) + 1)
        return '<sup class="ref">' + ",".join(f'<a href="#f{n}">[{n}]</a>' for n in sorted(set(nums))) + "</sup>"

    def elenco(self, extra=True):
        L = T[self.lingua]
        if extra:
            for i in ("pvgis-licenza", "eurostat-copyright"):
                if i not in self.ordine:
                    self.ordine.append(i)
        voci = []
        for n, i in enumerate(self.ordine, 1):
            f = REGOLE["fonti"][i]
            es = FONTI_ESITO.get(i, {})
            if f.get("non_letta"):
                stato = L["non_letta"].format(motivo=h(f["motivo"]))
            elif es.get("http") == 200:
                stato = L["letta"].format(data=data_lunga(date.fromisoformat(es["letto_il"]), self.lingua))
            else:
                stato = L["non_letta"].format(motivo=h(es.get("motivo", "?")))
            tipo = f' <span class="etich">{h(L["centro_risorse"])}</span>' if f.get("tipo") == "centro_risorse" else ""
            tit = f["titolo"][self.lingua] if isinstance(f["titolo"], dict) else f["titolo"]
            voci.append(f'<li id="f{n}"><a href="{h(f["url"])}" rel="noopener">{h(tit)}</a>{tipo}. <span class="small">{stato}</span></li>')
        return (f'<section class="fonti-box" aria-labelledby="fonti-h"><h2 id="fonti-h">{ico("doc")}{h(L["fonti_h"])}</h2>'
                f'<ol>{"".join(voci)}</ol><p class="small">{h(L["fonti_dati"])}</p></section>')


def punti_html(punti, rim, lingua):
    li = []
    for p in punti:
        t = h(riempi(p["t"], lingua))
        if p.get("nota"):
            li.append(f'<li class="nostra">{t} <span class="etich">{h(T[lingua]["fonte_nostra"])}</span></li>')
        else:
            li.append(f"<li>{t}{rim.ref(p['s'])}</li>")
    return f'<ul class="punti">{"".join(li)}</ul>'


def faq_html(voci, rim, lingua):
    """voci: [(domanda, risposta già riempita, fonti)] -> (html, JSON-LD FAQPage con lo stesso testo)."""
    blocchi, ld = [], []
    for q, a, s in voci:
        blocchi.append(f'<div class="faq"><h3>{h(q)}</h3><p>{h(a)}{rim.ref(s)}</p></div>')
        ld.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}})
    return "".join(blocchi), {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": ld}


# ---------------------------------------------------------------- scheletro di pagina
URLS = []  # (percorso, lastmod)
AD = '<div class="ad-slot" aria-hidden="true"></div>'
GRUPPI = {}  # chiave del gruppo hreflang -> {lingua: percorso}


def gruppo(chiave):
    g = {}
    for l in LINGUE_ATTIVE:
        g[l] = {"home": T[l]["p_home"], "regole": T[l]["p_regole"], "faq": T[l]["p_faq"], "contatti": T[l]["p_contatti"],
                "privacy": T[l]["p_privacy"]}[chiave]
    return g


def alternati(chiave):
    if not chiave:
        return ""
    g = gruppo(chiave)
    righe = [f'<link rel="alternate" hreflang="{T[l]["html"]}" href="{URL_SITO}/{p}">' for l, p in g.items()]
    if chiave == "home":
        righe.append(f'<link rel="alternate" hreflang="x-default" href="{URL_SITO}/">')
    return "\n".join(righe) + "\n"


def menu_html(lingua, percorso):
    L = T[lingua]
    dest = {"regole": L["p_regole"], "calc": L["p_home"] + "#calcolatore", "citta": L["p_home"] + "#citta", "faq": L["p_faq"]}
    return "".join(f'<a href="/{dest[k]}"' + (' aria-current="page"' if dest[k] == percorso else "") + f">{h(t)}</a>" for k, t in L["menu"])


def lingue_html(lingua, chiave, mobile=False):
    if chiave:
        g = gruppo(chiave)
    else:
        g = {l: T[l]["p_home"] for l in LINGUE_ATTIVE}
    voci = []
    for l in LINGUE_ATTIVE:
        if l == lingua:
            voci.append(f'<span aria-current="true">{l.upper()}</span>')
        else:
            voci.append(f'<a href="/{g[l]}" hreflang="{T[l]["html"]}" lang="{T[l]["html"]}" title="{h(T[l]["nome"])}">{l.upper()}</a>')
    if mobile:
        return f'<div class="lingue-m" aria-label="{h(T[lingua]["lingua_lbl"])}">{"".join(voci)}</div>'
    return f'<nav class="lingue" aria-label="{h(T[lingua]["lingua_lbl"])}">{"".join(voci)}</nav>'


def pagina(lingua, percorso, titolo, descrizione, corpo, testata="", chiave=None, briciole=None, jsonld=None, indicizza=True, lastmod=None):
    L = T[lingua]
    file = percorso if percorso.endswith(".html") else percorso + "index.html"
    url_pag = f"{URL_SITO}/{percorso}"
    if indicizza:
        URLS.append((percorso, (lastmod or ULTIMO_DATO).isoformat()))
    ld = list(jsonld or [])
    bc = ""
    if briciole:
        voci = [{"@type": "ListItem", "position": i, "name": n, "item": f"{URL_SITO}/{p}"} for i, (n, p) in enumerate(briciole, 1)]
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": voci})
        bc = ('<nav class="briciole" aria-label="breadcrumb">' + " › ".join(
            [f'<a href="/{p}">{h(n)}</a>' for n, p in briciole[:-1]] + [h(briciole[-1][0])]) + "</nav>")
    testata = testata.replace("{bc}", bc)
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    menu = menu_html(lingua, percorso)
    piede = "".join(f'<li><a href="/{u}">{h(t)}</a></li>' for u, t in [
        (L["p_home"], L["nome"]), (L["p_regole"], L["sezione_regole"]),
        (L["p_faq"], L["faq_h"]), (L["p_contatti"], L["contatti_h1"]), (L["p_privacy"], L["privacy_h1"])])
    altri_paesi = " · ".join(f'<a href="/{T[l]["p_home"]}" lang="{T[l]["html"]}">{h(T[l]["paese"])}</a>' for l in LINGUE_ATTIVE if l != lingua)
    corpo_tr = corpo + MON.riga_trasparenza(corpo, lingua)
    testo = f"""<!DOCTYPE html>
<html lang="{L['html']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">{ADSENSE_HEAD}
<title>{h(titolo)}</title>
<meta name="description" content="{h(descrizione)}">
{f'<link rel="canonical" href="{url_pag}">' if indicizza else '<meta name="robots" content="noindex">'}
{alternati(chiave) if indicizza else ""}<meta property="og:title" content="{h(titolo)}">
<meta property="og:description" content="{h(descrizione)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url_pag}">
<meta property="og:site_name" content="{h(L['nome'])}">
<meta property="og:locale" content="{L['og']}">
<meta property="og:image" content="{URL_SITO}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#13203B">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="/assets/{FAVICON_FILE}" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/manrope.woff2" as="font" type="font/woff2" crossorigin>
<script>{TEMA_JS}</script>
<link rel="stylesheet" href="/assets/{CSS_FILE}">
{ld_html}
</head>
<body>
<a class="skip" href="#main">{h(L['skip'])}</a>
<header class="top"><div class="wrap">
<a class="logo" href="/{L['p_home']}">{LOGO}<span>{h(L['logo'][0])} <b>{h(L['logo'][1])}</b></span></a>
<nav class="menu" aria-label="{h(L['menu_lbl'])}">{menu}</nav>
{lingue_html(lingua, chiave)}
<button type="button" class="tema" data-tema aria-label="{h(L['tema'])}">{ico("moon", "ico i-moon")}{ico("sun", "ico i-sun")}</button>
<details class="nav-m"><summary aria-label="{h(L['menu_lbl'])}">{ico("menu")}</summary><nav aria-label="{h(L['menu_lbl'])}">{menu}{lingue_html(lingua, chiave, mobile=True)}</nav></details>
</div></header>
<main id="main">
{testata}
<div class="wrap">
{corpo_tr}
</div>
</main>
<footer><div class="wrap">
<div class="f-grid"><div>
<a class="logo" href="/{L['p_home']}">{LOGO}<span>{h(L['logo'][0])} <b>{h(L['logo'][1])}</b></span></a>
<p>{L['footer']}</p>
<p>{h(L['altre_lingue'])}{DUE_PUNTI[lingua]}{altri_paesi}</p>
</div><div>
<h2>{h(L['esplora'])}</h2>
<ul>{piede}</ul>
</div></div>
<p class="f-base">{h(L['f_dati'].format(periodo=periodo(lingua), data=data_lunga(VERIFICA, lingua)))}</p>
</div></footer>
<script src="/assets/{JS_FILE}" defer></script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    if lingua == "it":
        testo = elidi(testo)
    dest = SITO / file
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(testo, encoding="utf-8")


def banda(eyebrow, titolo, sub, extra="", corta=False, icona="sun"):
    return f"""<section class="band{' corta' if corta else ''}"><div class="wrap band-in">{{bc}}
<p class="eyebrow">{ico(icona)}{h(eyebrow)}</p>
<h1>{h(titolo)}</h1>
<p class="sub">{sub}</p>{extra}
</div></section>"""


def trust(lingua):
    L = T[lingua]
    v = [t.format(periodo=periodo(lingua), data=data_lunga(VERIFICA, lingua)) for t in L["trust"]]
    icone = ["panel", "plug", "shield"]
    return '<ul class="trust">' + "".join(f"<li>{ico(i)}{h(t)}</li>" for i, t in zip(icone, v)) + "</ul>"


# ---------------------------------------------------------------- componenti
def calcolatore(lingua, slug_def, rim):
    L = T[lingua]
    dati = {"citta": [{"s": c["slug"], "n": c["nome"], "a35": pv(lingua, c["slug"])["a35"]["E_y"], "a90": pv(lingua, c["slug"])["a90"]["E_y"],
                       "m35": pv(lingua, c["slug"])["a35"]["E_m"], "m90": pv(lingua, c["slug"])["a90"]["E_m"]} for c in CITTA[lingua]],
            "mesi": L["mesi"], "soglia": 3000 if lingua == "fr" else 800}
    opzioni = "".join(f'<option value="{c["slug"]}"{" selected" if c["slug"] == slug_def else ""}>{h(c["nome"])}</option>'
                      for c in sorted(CITTA[lingua], key=lambda c: c["nome"]))
    r = risultato(lingua, slug_def)
    p = pv(lingua, slug_def)
    mx = max(p["a35"]["E_m"] + p["a90"]["E_m"])
    barre = "".join(f'<li style="height:{max(2, round(v / mx * 100))}%" title="{h(L["mesi"][i])}: {fmt_num(v, lingua)} kWh"></li>'
                    for i, v in enumerate(p["a35"]["E_m"]))
    etich = "".join(f"<li>{h(m[:1].upper())}</li>" for m in L["mesi"])
    passo = "0.0001"
    oltre = (f'<p class="avviso-w" data-oltre hidden>{ico("alert")} {h(L["calc_oltre"])} <a href="/{L["p_regole"]}">{h(L["sezione_regole"])}</a></p>')
    return f"""<section class="card calc pull" id="calcolatore" aria-labelledby="calc-h">
<h2 class="calc-h" id="calc-h">{ico("panel")}{h(L['calc_h'])}</h2>
<form data-calc class="calc-g">
<div class="calc-in">
<label>{h(L['calc_citta'])}<select name="citta">{opzioni}</select></label>
<fieldset><legend>{h(L['calc_mont'])}</legend><div class="seg">
<label><input type="radio" name="mont" value="a35" checked>{h(L['m35'])}</label>
<label><input type="radio" name="mont" value="a90">{h(L['m90'])}</label></div></fieldset>
<div class="calc-2">
<label>{h(L['calc_w'])}<input type="number" name="w" value="{POTENZA_RIF}" min="0" max="5000" step="10" inputmode="numeric"></label>
<label>{h(L['calc_kit'])}<input type="number" name="kit" value="{KIT_DEF}" min="0" max="20000" step="10" inputmode="numeric"></label>
</div>
<label>{h(L['calc_quota'])}<span class="range"><input type="range" name="quota" min="10" max="100" step="5" value="{QUOTA_DEF}"><output data-o="quota">{QUOTA_DEF} %</output></span></label>
<label>{h(L['calc_prezzo'])}<input type="number" name="prezzo" value="{prezzo(lingua)}" min="0" max="2" step="{passo}" inputmode="decimal"></label>
</div>
<div class="calc-out" aria-live="polite">
<div class="ris">
<div class="top"><span>{h(L['out_eur'])}</span><b data-o="eur">{fmt_num(r['eur'], lingua)}</b><span>{h(L['u_eur_anno'])}</span></div>
<div class="top"><span>{h(L['out_anni'])}</span><b data-o="anni">{fmt_num(r['anni'], lingua, 1)}</b><span>{h(L['u_anni'])}</span></div>
<div><span>{h(L['out_prod'])}</span><b data-o="prod">{fmt_num(r['prod'], lingua)}</b><span>{h(L['u_kwh_anno'])}</span></div>
<div><span>{h(L['out_auto'])}</span><b data-o="auto">{fmt_num(r['auto'], lingua)}</b><span>{h(L['u_kwh_anno'])}</span></div>
</div>
<div><span class="small">{h(L['calc_mesi'])}</span><ul class="barre" aria-hidden="true">{barre}</ul><ul class="barre-l" aria-hidden="true">{etich}</ul></div>
{oltre}
</div>
</form>
<p class="calc-f">{h(L['calc_nota'])}{rim.ref(["pvgis-api", "eurostat-dati"])}</p>
<script type="application/json" id="calc-dati">{json.dumps(dati, ensure_ascii=False, separators=(",", ":"))}</script>
</section>"""


def ipotesi(lingua, rim):
    L = T[lingua]
    p0 = next(iter(PVGIS["citta"].values()))
    li = "".join(f"<li>{h(t.format(db=p0['db'], anni=p0['anni'].replace('-', '–'), prezzo=fmt_num(prezzo(lingua), lingua, 4), periodo=periodo(lingua), quota=QUOTA_DEF))}</li>"
                 for t in L["ipotesi"])
    return f'<h2 id="ipotesi">{h(L["ipotesi_h"])}</h2><div class="testo"><ul class="punti">{li}</ul></div><p class="small">{rim.ref(["pvgis-api", "pvgis-licenza", "eurostat-dati"])}</p>'


def sintesi(lingua):
    s = REGOLE["paesi"][lingua]["sintesi"]
    return '<dl class="sintesi">' + "".join(f"<div><dt>{h(x['k'])}</dt><dd>{h(x['v'])}</dd></div>" for x in s) + "</dl>"


def prima(lingua):
    L = T[lingua]
    li = "".join(f"<li>{h(x)}</li>" for x in L["prima"])
    return (f'<section class="card prima" style="margin-top:28px"><h2>{ico("shield")} {h(L["prima_h"])}</h2><ol>{li}</ol>'
            f'<p class="small">{h(L["prima_nota"])}</p></section>')


# Frase richiesta da Amazon Associates nella lingua del programma (si mostra solo con un link Amazon acceso)
FRASE_AMAZON = {"it": "In qualità di Affiliato Amazon, ricevo un guadagno dagli acquisti idonei.",
                "es": "En calidad de Afiliado de Amazon, obtengo ingresos por las compras adscritas que cumplen los requisitos aplicables.",
                "fr": "En tant que Partenaire Amazon, je réalise un bénéfice sur les achats remplissant les conditions requises."}


def blocco_affiliati(lingua):
    """Riquadro affiliati: '' finché nessuna voce di dati/affiliati.json ha un url (mai inventarlo)."""
    L = T[lingua]
    voci = []
    for v in AFFILIATI.get(lingua, []):
        u = (v.get("url") or "").strip()
        if not u:
            continue
        if v["id"] == "amazon":
            if not (v.get("tag") or "").strip():
                continue
            dom = {"it": "www.amazon.it", "es": "www.amazon.es", "fr": "www.amazon.fr"}[lingua]
            u = f"https://{dom}/s?k={quote_plus(v['ricerca'])}&tag={quote_plus(v['tag'])}"
        if not MON.dominio_ammesso(u):
            raise SystemExit(f"affiliati.json: {u} non è in un dominio ammesso (monetizzazione.json)")
        voci.append(f'<li><a href="{h(u)}" rel="sponsored noopener">{h(v["testo"])}</a></li>')
    if not voci:
        return ""
    amazon = f'<p class="small">{h(FRASE_AMAZON[lingua])}</p>' if any("amazon." in v for v in voci) else ""
    return (f'<aside class="aff-box"><h2>{h(L["aff_h"])}<span class="aff-tag">{h(L["aff_tag"])}</span></h2><p>{h(L["aff_testo"])}</p>'
            f'<ul>{"".join(voci)}</ul>{MON.nota_trasparenza(lingua)}{amazon}</aside>')


def ci_sono_affiliati(lingua):
    return bool(blocco_affiliati(lingua))


def tabella_citta(lingua):
    L = T[lingua]
    righe = []
    ordinate = sorted(CITTA[lingua], key=lambda c: -pv(lingua, c["slug"])["a35"]["E_y"])
    mx = max(pv(lingua, c["slug"])["a35"]["E_y"] for c in CITTA[lingua])
    for c in ordinate:
        p = pv(lingua, c["slug"])
        nome = (f'<a href="/{url_citta(lingua, c["slug"])}">{h(c["nome"])}</a>' if ha_pagina(lingua, c["slug"]) else h(c["nome"]))
        righe.append(f'<tr><td>{nome}</td><td class="n"><span class="bar" style="width:{round(p["a35"]["E_y"] / mx * 60)}px"></span>{kwh(lingua, c["slug"])}</td>'
                     f'<td class="n">{kwh(lingua, c["slug"], "a90")}</td><td class="n">{eur(lingua, c["slug"])} €</td></tr>')
    th = L["tab_th"]
    return (f'<div class="tab"><table><thead><tr><th>{h(th[0])}</th><th class="n">{h(th[1])}</th><th class="n">{h(th[2])}</th><th class="n">{h(th[3])}</th></tr></thead>'
            f'<tbody>{"".join(righe)}</tbody></table></div>'
            f'<p class="small">{h(L["tab_nota"].format(quota=QUOTA_DEF, prezzo=fmt_num(prezzo(lingua), lingua, 4)))}</p>')


def faq_voci(lingua):
    return [(f["q"], riempi(f["a"], lingua), f["s"]) for f in REGOLE["paesi"][lingua]["faq"]]


# ---------------------------------------------------------------- pagine
def home(lingua):
    L = T[lingua]
    rim = Rimandi(lingua)
    rif = {"it": "roma", "es": "madrid", "fr": "paris"}[lingua]
    sub = L["home_sub"].format(citta=h(nome_citta(lingua, rif)), kwh=kwh(lingua, rif))
    testata = banda(L["home_eyebrow"], L["home_h1"], sub, trust(lingua))
    regole_breve = (f'<h2 id="regole">{h(L["regole_breve_h"])}</h2>{sintesi(lingua)}'
                    f'<p style="margin-top:14px"><a class="btn sec" href="/{L["p_regole"]}">{ico("doc")}{h(L["regole_tutte"])}</a></p>')
    voci = faq_voci(lingua)[:3]
    faq_breve = "".join(f'<li><a href="/{L["p_faq"]}">{h(q)}</a></li>' for q, _, _ in voci)
    pag_c = "".join(f'<li><a href="/{url_citta(lingua, c["slug"])}"><span>{h(c["nome"])}</span><small>{kwh(lingua, c["slug"])} kWh · {eur(lingua, c["slug"])} €</small></a></li>'
                    for c in PAGINE_CITTA[lingua])
    corpo = "\n".join([
        calcolatore(lingua, rif, rim), AD, regole_breve,
        f'<h2 id="citta">{h(L["tab_h"])}</h2>',
        f'<ul class="griglia" style="margin-bottom:16px">{pag_c}</ul>' if pag_c else "",
        tabella_citta(lingua),
        f'<h2>{h(L["faq_h"])}</h2><ul class="punti">{faq_breve}</ul><p><a href="/{L["p_faq"]}">{h(L["faq_tutte"])}</a></p>',
        ipotesi(lingua, rim), rim.elenco()])
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": L["nome"], "url": f"{URL_SITO}/{L['p_home']}", "inLanguage": L["html"]},
          {"@context": "https://schema.org", "@type": "WebApplication", "name": L["calc_h"], "applicationCategory": "UtilitiesApplication",
           "operatingSystem": "Web", "url": f"{URL_SITO}/{L['p_home']}#calcolatore", "inLanguage": L["html"],
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}}]
    pagina(lingua, L["p_home"], L["home_t"], L["home_d"].format(n=len(CITTA[lingua])), corpo, testata, chiave="home", jsonld=ld)


def pagina_regole(lingua):
    L = T[lingua]
    P = REGOLE["paesi"][lingua]
    rim = Rimandi(lingua)
    sez = "".join(f'<h2 id="{s["id"]}">{h(s["titolo"])}</h2>{punti_html(s["punti"], rim, lingua)}' for s in P["sezioni"])
    corpo = "\n".join([f'<div class="card pull">{sintesi(lingua)}</div>', f'<div class="testo">{sez}</div>', prima(lingua),
                       blocco_affiliati(lingua), AD,
                       f'<p class="lead" style="margin-top:26px">{ico("panel")} <a href="/{L["p_home"]}#calcolatore">{h(L["calc_h"])}</a> · <a href="/{L["p_faq"]}">{h(L["faq_h"])}</a></p>',
                       rim.elenco(extra=False)])
    descr = L["regole_d"].format(data=data_lunga(VERIFICA, lingua))
    testata = banda(L["regole_eyebrow"], P["titolo_pagina"], h(L["regole_sub"].format(data=data_lunga(VERIFICA, lingua))), trust(lingua), icona="doc")
    art = {"@context": "https://schema.org", "@type": "Article", "headline": P["titolo_pagina"], "description": descr, "inLanguage": L["html"],
           "dateModified": VERIFICA.isoformat(), "author": {"@type": "Organization", "name": L["nome"], "url": f"{URL_SITO}/{L['p_home']}"},
           "publisher": {"@type": "Organization", "name": L["nome"], "url": f"{URL_SITO}/{L['p_home']}"}, "mainEntityOfPage": f"{URL_SITO}/{L['p_regole']}"}
    pagina(lingua, L["p_regole"], L["regole_t"], descr, corpo, testata, chiave="regole",
           briciole=[(L["briciole_home"], L["p_home"]), (L["sezione_regole"], L["p_regole"])], jsonld=[art], lastmod=VERIFICA)


def pagina_faq(lingua):
    L = T[lingua]
    rim = Rimandi(lingua)
    html_f, ld = faq_html(faq_voci(lingua), rim, lingua)
    corpo = "\n".join([f'<div class="card pull">{html_f}</div>', AD,
                       f'<p class="lead" style="margin-top:26px">{ico("doc")} <a href="/{L["p_regole"]}">{h(L["regole_tutte"])}</a> · <a href="/{L["p_home"]}#calcolatore">{h(L["calc_h"])}</a></p>',
                       rim.elenco()])
    testata = banda(L["faq_eyebrow"], L["faq_h"], h(L["faq_sub"]), corta=True, icona="info")
    pagina(lingua, L["p_faq"], L["faq_t"], L["faq_d"], corpo, testata, chiave="faq",
           briciole=[(L["briciole_home"], L["p_home"]), (L["faq_h"], L["p_faq"])], jsonld=[ld], lastmod=VERIFICA)


def ordinale_fr(n):
    return "1re" if n == 1 else f"{n}e"


def pagina_citta(lingua, c):
    L = T[lingua]
    s, nome = c["slug"], c["nome"]
    p = pv(lingua, s)
    rim = Rimandi(lingua)
    pz = fmt_num(prezzo(lingua), lingua, 4)
    k35, k90, e = kwh(lingua, s), kwh(lingua, s, "a90"), eur(lingua, s)
    stats = (f'<div class="card stats pull">'
             f'<div class="stat main"><b>{k35}</b><span>{h(L["st_k35"])}</span></div>'
             f'<div class="stat"><b>{k90}</b><span>{h(L["st_k90"])}</span></div>'
             f'<div class="stat"><b>{e} €</b><span>{h(L["st_eur"])}</span></div>'
             f'<div class="stat"><b>{anni(lingua, s)}</b><span>{h(L["st_anni"].format(kit=KIT_DEF))}</span></div>'
             f'<p class="asof">{h(L["st_nota"].format(quota=QUOTA_DEF, prezzo=pz, periodo=periodo(lingua)))}{rim.ref(["pvgis-api", "eurostat-dati"])}</p></div>')
    m35, m90 = p["a35"]["E_m"], p["a90"]["E_m"]
    mx = max(m35 + m90)
    righe_m = "".join(f'<tr><td>{h(L["mesi_l"][i].capitalize())}</td>'
                      f'<td class="n"><span class="bar" style="width:{round(m35[i] / mx * 60)}px"></span>{fmt_num(m35[i], lingua)}</td>'
                      f'<td class="n"><span class="bar v" style="width:{round(m90[i] / mx * 60)}px"></span>{fmt_num(m90[i], lingua)}</td></tr>' for i in range(12))
    ib, iw = max(range(12), key=lambda i: m35[i]), min(range(12), key=lambda i: m35[i])
    mt = L["mesi_testo"].format(best=L["mesi_l"][ib], vb=fmt_num(m35[ib], lingua), worst=L["mesi_l"][iw], vw=fmt_num(m35[iw], lingua),
                                pdic=round(m90[11] / m35[11] * 100), plug=round(m90[6] / m35[6] * 100))
    th = L["mesi_th"]
    mesi = (f'<h2 id="mesi">{h(L["mesi_h"].format(c=nome))}</h2><p class="lead">{h(mt)}</p>'
            f'<div class="tab"><table><thead><tr><th>{h(th[0])}</th><th class="n">{h(th[1])}</th><th class="n">{h(th[2])}</th></tr></thead><tbody>{righe_m}</tbody></table></div>')
    rr = "".join(f'<tr><td>{q} %</td><td class="n">{eur(lingua, s, "a35", q)} €</td><td class="n">{eur(lingua, s, "a90", q)} €</td></tr>' for q in QUOTE_TAB)
    th = L["risp_th"]
    risp = (f'<h2 id="risparmio">{h(L["risp_h"].format(c=nome))}</h2><div class="cols"><div><div class="tab"><table><thead><tr><th>{h(th[0])}</th><th class="n">{h(th[1])}</th>'
            f'<th class="n">{h(th[2])}</th></tr></thead><tbody>{rr}</tbody></table></div><p class="small">{h(L["risp_testo"].format(prezzo=pz))}</p></div>')
    rk = "".join(f'<tr><td>{fmt_num(k, lingua)} €</td><td class="n">{anni(lingua, s, k)}</td><td class="n">{anni(lingua, s, k, "a90")}</td></tr>' for k in KIT_TAB)
    th = L["rientro_th"]
    risp += (f'<div><div class="tab"><table><thead><tr><th>{h(th[0])}</th><th class="n">{h(th[1])}</th><th class="n">{h(th[2])}</th></tr></thead>'
             f'<tbody>{rk}</tbody></table></div><p class="small">{h(L["rientro_testo"].format(quota=QUOTA_DEF))}</p></div></div>')
    valori = sorted((pv(lingua, x["slug"])["a35"]["E_y"] for x in CITTA[lingua]), reverse=True)
    pos = valori.index(p["a35"]["E_y"]) + 1
    n = len(valori)
    med = valori[n // 2] if n % 2 else (valori[n // 2 - 1] + valori[n // 2]) / 2
    conf = L["conf_testo"].format(c=nome, pos=pos, pos_fr=ordinale_fr(pos) if lingua == "fr" else pos, n=n, med=fmt_num(med, lingua))
    q1, a1 = L["citta_faq_q1"].format(c=nome), L["citta_faq_a1"].format(c=nome, k35=k35, k90=k90, quota=QUOTA_DEF, prezzo=pz, eur=e)
    q2, a2 = L["citta_faq_q2"].format(c=nome), L["citta_faq_a2"]
    regole_breve = (f'<h2 id="regole">{h(L["regole_breve_h"])}</h2>{sintesi(lingua)}'
                    f'<p style="margin-top:12px"><a href="/{L["p_regole"]}">{h(L["regole_tutte"])}</a></p>')
    fh, fld = faq_html([(q1, a1, ["pvgis-api", "eurostat-dati"]), (q2, a2, L["citta_faq_s2"])], rim, lingua)
    altre = "".join(f'<li><a href="/{url_citta(lingua, x["slug"])}"><span>{h(x["nome"])}</span><small>{kwh(lingua, x["slug"])} kWh</small></a></li>'
                    for x in PAGINE_CITTA[lingua] if x["slug"] != s)
    altre_html = f'<h2>{h(L["altre_h"])}</h2><ul class="griglia">{altre}</ul>' if altre else ""
    corpo = "\n".join([stats, calcolatore(lingua, s, rim).replace(" pull", "", 1).replace('class="card calc"', 'class="card calc" style="margin-top:24px"'),
                       AD, mesi, risp, f'<p class="lead" style="margin-top:18px">{ico("pin")} {h(conf)}</p>',
                       regole_breve, blocco_affiliati(lingua), f'<h2>{h(L["faq_h"])}</h2>{fh}', altre_html,
                       f'<p class="small" style="margin-top:20px"><a href="/{L["p_home"]}#citta">{h(L["tab_h"])}</a></p>',
                       ipotesi(lingua, rim), rim.elenco()])
    sub = L["citta_sub"].format(c=h(nome), k35=k35, k90=k90)
    testata = banda(L["citta_eyebrow"].format(c=nome), L["citta_h1"].format(c=nome), sub, trust(lingua), icona="pin")
    descr = L["citta_d"].format(c=nome, k35=k35, eur=e, quota=QUOTA_DEF)
    pagina(lingua, url_citta(lingua, s), L["citta_t"].format(c=nome), descr, corpo, testata,
           briciole=[(L["briciole_home"], L["p_home"]), (L["sezione_citta"], L["p_home"] + "#citta"), (nome, url_citta(lingua, s))],
           jsonld=[fld], lastmod=PVGIS_DATA)


def contatti(lingua):
    L = T[lingua]
    corpo = f"""<section class="card pull"><form class="form ajax" name="contatto" method="POST" action="/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="contatto"><input type="hidden" name="lingua" value="{lingua}"><input type="hidden" name="source" value="">
<p class="hp"><label>{h(L['f_hp'])} <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<label>{h(L['f_email'])}<input type="email" name="email" required autocomplete="email"></label>
<label>{h(L['f_pagina'])}<input type="text" name="pagina" maxlength="200"></label>
<label>{h(L['f_msg'])}<textarea name="messaggio" rows="6" required maxlength="4000"></textarea></label>
<label class="check"><input type="checkbox" name="consenso" value="si" required><span>{L['f_consenso'].format(priv='/' + L['p_privacy'])}</span></label>
<button class="btn" type="submit">{h(L['f_invia'])}</button><p class="errore" data-errore hidden>{h(L['f_err'])}</p></form>
<div class="ok" data-ok hidden>{L['f_ok']}</div></section>
<p class="small" style="margin-top:16px">{h(L['f_nota'])}</p>"""
    testata = banda(L["contatti_h1"], L["contatti_h1"], h(L["contatti_sub"]), corta=True, icona="info")
    pagina(lingua, L["p_contatti"], L["contatti_t"], L["contatti_d"], corpo, testata, chiave="contatti",
           briciole=[(L["briciole_home"], L["p_home"]), (L["contatti_h1"], L["p_contatti"])])


def privacy(lingua):
    L = T[lingua]
    aff = ci_sono_affiliati(lingua)
    cookie = MON.privacy_cookie(lingua, SITO_ID, aff)
    if not cookie:
        raise SystemExit("privacy: con AdSense spento e senza affiliati serve un testo proprio sui cookie (oggi AdSense è acceso)")
    corpo = (f'<div class="testo"><p class="small" style="margin-top:28px">{h(L["agg"])}{DUE_PUNTI[lingua]}{data_lunga(OGGI, lingua)}</p>'
             + PRIVACY[lingua].format(contatti="/" + L["p_contatti"], cookie=cookie) + "</div>")
    breve = MON.privacy_breve(lingua, SITO_ID, aff)
    testata = banda(L["privacy_h1"], L["privacy_h1"], h(breve), corta=True, icona="shield")
    pagina(lingua, L["p_privacy"], L["privacy_t"], L["privacy_d"], corpo, testata, chiave="privacy",
           briciole=[(L["briciole_home"], L["p_home"]), (L["privacy_h1"], L["p_privacy"])])


RADICE_TESTI = {
    "it": ("Fotovoltaico da balcone in Italia", "Comunicazione Unica sotto 800 W, condominio e calcolatore per città.", "Apri"),
    "es": ("Placas solares de balcón en España", "Autoconsumo sin excedentes, kits enchufables y calculadora por ciudad.", "Abrir"),
    "fr": ("Panneau solaire de balcon en France", "Déclaration Enedis, Consuel, copropriété et calculateur par ville.", "Ouvrir"),
}


def pagina_radice():
    """Pagina di scelta del Paese (x-default), in inglese con i titoli nelle lingue dei Paesi."""
    carte = "".join(
        f'<a class="card" href="/{T[l]["p_home"]}" lang="{T[l]["html"]}" hreflang="{T[l]["html"]}"><b>{h(RADICE_TESTI[l][0])}</b>'
        f'<span>{h(RADICE_TESTI[l][1])}</span><span class="small">{kwh(l, {"it": "roma", "es": "madrid", "fr": "paris"}[l])} kWh · '
        f'{h(nome_citta(l, {"it": "roma", "es": "madrid", "fr": "paris"}[l]))} (PVGIS)</span><em>{h(RADICE_TESTI[l][2])} →</em></a>'
        for l in LINGUE_ATTIVE)
    alt = "\n".join([f'<link rel="alternate" hreflang="{T[l]["html"]}" href="{URL_SITO}/{T[l]["p_home"]}">' for l in LINGUE_ATTIVE]
                    + [f'<link rel="alternate" hreflang="x-default" href="{URL_SITO}/">'])
    titolo = "Balcony Solar Europe: rules and yield calculator by country"
    descr = "Balcony solar (plug-in PV) in Italy, Spain and France: the official rules in each country's language and a yield and savings calculator with EU PVGIS data."
    testo = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="{GOOGLE_VERIFICA}">{ADSENSE_HEAD}
<title>{h(titolo)}</title>
<meta name="description" content="{h(descr)}">
<link rel="canonical" href="{URL_SITO}/">
{alt}
<meta property="og:title" content="{h(titolo)}">
<meta property="og:description" content="{h(descr)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{URL_SITO}/">
<meta property="og:image" content="{URL_SITO}/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#13203B">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="/assets/{FAVICON_FILE}" type="image/svg+xml">
<script>{TEMA_JS}</script>
<link rel="stylesheet" href="/assets/{CSS_FILE}">
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "WebSite", "name": "Balcony Solar Europe", "url": URL_SITO + "/"})}</script>
</head>
<body>
<header class="top"><div class="wrap">
<a class="logo" href="/">{LOGO}<span>Balcony <b>Solar Europe</b></span></a>
<button type="button" class="tema" data-tema aria-label="Switch light or dark theme">{ico("moon", "ico i-moon")}{ico("sun", "ico i-sun")}</button>
</div></header>
<main id="main">
<section class="band"><div class="wrap band-in">
<p class="eyebrow">{ico("sun")}Italia · España · France</p>
<h1>Balcony solar in Europe: the rules and what a kit yields in your city</h1>
<p class="sub">Official rules read on government and regulator sites, and a yield and savings calculator with the European Commission's PVGIS data. Choose your country.</p>
</div></section>
<div class="wrap"><div class="paesi pull">{carte}</div>
<p class="small" style="margin-top:22px">Data: PVGIS © European Communities, 2001-2026 · Eurostat household electricity prices. Not electrical or legal advice.</p></div>
</main>
<footer><div class="wrap"><p class="f-base" style="border:0;margin:0;padding:0">Balcony Solar Europe · {" · ".join(f'<a href="/{T[l]["p_privacy"]}" lang="{T[l]["html"]}">{h(T[l]["privacy_h1"])}</a>' for l in LINGUE_ATTIVE)}</p></div></footer>
<script src="/assets/{JS_FILE}" defer></script>
{SCRIPT_CONTATORE}
</body>
</html>
"""
    (SITO / "index.html").write_text(testo, encoding="utf-8")
    URLS.insert(0, ("", ULTIMO_DATO.isoformat()))


def pagina_404():
    carte = "".join(f'<li><a href="/{T[l]["p_home"]}" lang="{T[l]["html"]}"><span>{h(RADICE_TESTI[l][0])}</span><small>{h(T[l]["paese"])}</small></a></li>' for l in LINGUE_ATTIVE)
    testo = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">{ADSENSE_HEAD}
<title>404 · Balcony Solar Europe</title>
<meta name="color-scheme" content="light dark">
<link rel="icon" href="/assets/{FAVICON_FILE}" type="image/svg+xml">
<script>{TEMA_JS}</script>
<link rel="stylesheet" href="/assets/{CSS_FILE}">
</head>
<body>
<header class="top"><div class="wrap"><a class="logo" href="/">{LOGO}<span>Balcony <b>Solar Europe</b></span></a></div></header>
<main id="main">
<section class="band corta"><div class="wrap band-in">
<p class="eyebrow">{ico("alert")}404</p>
<h1 lang="it">Pagina non trovata · <span lang="es">Página no encontrada</span> · <span lang="fr">Page introuvable</span></h1>
</div></section>
<div class="wrap"><ul class="griglia" style="margin-top:24px">{carte}</ul></div>
</main>
<script src="/assets/{JS_FILE}" defer></script>
</body>
</html>
"""
    (SITO / "404.html").write_text(testo, encoding="utf-8")


# ---------------------------------------------------------------- file accessori
def extra():
    (SITO / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL_SITO}/sitemap.xml\n", encoding="utf-8")
    (SITO / f"{CHIAVE_INDEXNOW}.txt").write_text(CHIAVE_INDEXNOW, encoding="utf-8")
    MON.scrivi_ads_txt(SITO_ID, SITO)
    voci = "".join(f"<url><loc>{URL_SITO}/{u}</loc><lastmod>{d}</lastmod></url>" for u, d in URLS)
    (SITO / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{voci}</urlset>\n',
                                      encoding="utf-8")
    (SITO / "netlify.toml").write_text("""[build]
  publish = "."
  command = ""
  # Pubblica solo se è cambiato qualcosa in solarebalcone/sito (ogni pubblicazione consuma crediti Netlify).
  # Impostazioni del sito su Netlify: Base directory = solarebalcone/sito, Build command vuoto, Publish directory = "."
  ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- ."

[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    X-Frame-Options = "DENY"
    Permissions-Policy = "camera=(), microphone=(), geolocation=()"

[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=604800"
""", encoding="utf-8")


def copia_grafica():
    (SITO / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    for f in (RADICE / "grafica" / "fonts").glob("*.woff2"):
        shutil.copy(f, SITO / "assets" / "fonts" / f.name)
    og = RADICE / "grafica" / "og.png"
    if og.exists():
        shutil.copy(og, SITO / "assets" / "og.png")
    for nome, testo in ASSET.items():
        (SITO / "assets" / nome).write_text(testo, encoding="utf-8")


def controlli():
    err = []
    for l in LINGUE_ATTIVE:
        for c in CITTA[l]:
            if f"{l}/{c['slug']}" not in PVGIS["citta"]:
                err.append(f"{l}/{c['slug']}: manca il dato PVGIS (lanciare raccolta/pvgis.py)")
        for s in REGOLE["paesi"][l]["sezioni"]:
            for p in s["punti"]:
                if not p.get("nota") and not p.get("s"):
                    err.append(f"{l}/{s['id']}: affermazione senza fonte: {p['t'][:60]}")
        for fid, f in REGOLE["fonti"].items():
            es = FONTI_ESITO.get(fid)
            if not es:
                err.append(f"fonte {fid} mai letta: lanciare raccolta/fonti.py")
            elif not f.get("non_letta") and es.get("http") != 200:
                err.append(f"fonte {fid}: HTTP {es.get('http')} all'ultima lettura: rileggere prima di pubblicare")
    if REGOLE["paesi"]["de"].get("attiva"):
        err.append("de attiva in regole.json ma la versione tedesca non è ancora scritta (serve l'Impressum)")
    if err:
        raise SystemExit("ERRORI NEI DATI:\n" + "\n".join(err))


def main():
    controlli()
    conserva = {}
    if SITO.exists():
        conserva = {p.name: p.read_bytes() for p in SITO.glob("google*.html")}
        shutil.rmtree(SITO)
    SITO.mkdir()
    for nome, contenuto in conserva.items():
        (SITO / nome).write_bytes(contenuto)
    copia_grafica()
    conti = {}
    for l in LINGUE_ATTIVE:
        home(l)
        pagina_regole(l)
        pagina_faq(l)
        for c in PAGINE_CITTA[l]:
            pagina_citta(l, c)
        contatti(l)
        privacy(l)
        conti[l] = len(PAGINE_CITTA[l])
    pagina_radice()
    pagina_404()
    extra()
    print(f"Sito generato in {SITO}: {len(URLS)} pagine indicizzabili; pagine città {conti}. "
          f"PVGIS letto il {PVGIS['letto_il']}, prezzi {PREZZI['paesi']['IT']['periodo']}, fonti verificate il {VERIFICA}.")


if __name__ == "__main__":
    main()
