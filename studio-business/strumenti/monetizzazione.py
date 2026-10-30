"""Monetizzazione comune della rete di siti: pubblicità Google AdSense e link di affiliazione.

Le impostazioni stanno in un solo file, monetizzazione.json (accanto a questo). Ogni genera.py importa questo modulo:
    sys.path.insert(0, str(RADICE.parent / "studio-business" / "strumenti"))
    import monetizzazione as MON

Cosa fa, per ogni sito (identificato dal nome della sua cartella: "esameb1", "visaincome", ...):
- script_adsense(sito): lo script ufficiale di AdSense per il <head> (annunci automatici), oppure "" se AdSense è spento;
- scrivi_ads_txt(sito, cartella_sito): scrive sito/ads.txt solo con AdSense acceso (e lo toglie se è spento);
- privacy_cookie(lingua, sito, affiliati): le sezioni privacy su cookie, link di affiliazione e pubblicità, oppure "" se
  il sito non ha né pubblicità né link di affiliazione (in quel caso ogni sito tiene il suo testo di oggi, invariato);
- riga_trasparenza(html, lingua): la riga "Some links are affiliate links..." quando la pagina ha link rel="sponsored";
- controlla_sito(sito, cartella_sito): i controlli comuni usati da ogni verifica.py (link di affiliazione solo verso i
  domini ammessi, con rel="sponsored noopener" e la riga di trasparenza; AdSense, ads.txt e privacy coerenti).

Uso da riga di comando (dalla radice del repository):
    python3 studio-business/strumenti/monetizzazione.py stato
    python3 studio-business/strumenti/monetizzazione.py attiva ca-pub-XXXXXXXXXXXXXXXX esameb1 [altri siti...]
    python3 studio-business/strumenti/monetizzazione.py spegni esameb1          # toglie il sito dall'elenco AdSense
    python3 studio-business/strumenti/monetizzazione.py verifica [siti...]     # controlli comuni sulle cartelle sito/
Dopo "attiva" o "spegni" si rigenerano i siti interessati (python3 <cartella>/genera.py) e si lancia la verifica.
"""

import json
import re
import sys
from html import unescape
from pathlib import Path
from urllib.parse import urlparse

QUI = Path(__file__).resolve().parent
FILE = QUI / "monetizzazione.json"
RADICE_REPO = QUI.parent.parent

SITI = ["italystrikes", "touristtax", "visaincome", "beforeyoufly", "esameb1", "esamidistato",
        "floodcost", "aste", "fhacondos", "cruisescores"]

# Righe di trasparenza obbligatorie in ogni pagina con link di affiliazione (testo esatto: lo cerca anche controlla_sito)
RIGA_EN = "Some links are affiliate links: we may earn a commission at no extra cost to you."
RIGA_IT = "Alcuni link sono di affiliazione: potremmo ricevere una commissione, senza costi in più per te."

URL_ADSENSE_JS = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"
URL_PARTNER_SITES = "https://policies.google.com/technologies/partner-sites"
URL_ADS_SETTINGS = "https://adssettings.google.com"
ADS_TXT_CERT = "f08c47fec0942fa0"  # ID dell'autorità di certificazione di Google per ads.txt (uguale per tutti gli editori)


def _carica():
    try:
        return json.loads(FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Manca {FILE}: è il file comune della monetizzazione della rete.")


CONFIG = _carica()


def _cliente(valore):
    """Normalizza il codice editore: accetta 'ca-pub-123…' o 'pub-123…'; '' se vuoto. Errore se il formato è sbagliato."""
    v = (valore or "").strip()
    if not v:
        return ""
    if v.startswith("pub-"):
        v = "ca-" + v
    if not re.fullmatch(r"ca-pub-\d{10,20}", v):
        raise SystemExit(f"monetizzazione.json: adsense_client '{valore}' non valido (atteso ca-pub- seguito dalle cifre del codice editore)")
    return v


ADSENSE_CLIENT = _cliente(CONFIG.get("adsense_client", ""))
ADSENSE_SITI = list(CONFIG.get("adsense_siti", []))
_ignoti = [s for s in ADSENSE_SITI if s not in SITI]
if _ignoti:
    raise SystemExit(f"monetizzazione.json: siti sconosciuti in adsense_siti: {_ignoti} (nomi ammessi: {', '.join(SITI)})")
DOMINI_AFFILIAZIONE = [d.strip().lower() for d in CONFIG.get("domini_affiliazione", []) if d.strip()]
DOMINI_BLOCCATI = [d.strip().lower() for d in CONFIG.get("domini_bloccati", []) if d.strip()]
for _d in DOMINI_AFFILIAZIONE + DOMINI_BLOCCATI:
    if "/" in _d or "?" in _d or "=" in _d or " " in _d:
        raise SystemExit(f"monetizzazione.json: '{_d}' non è un dominio (solo domini, nessun percorso o ID)")


# ---------------------------------------------------------------- AdSense

def adsense_attivo(sito):
    """AdSense acceso per questo sito: codice editore compilato E sito nell'elenco adsense_siti."""
    if sito not in SITI:
        raise SystemExit(f"monetizzazione: sito sconosciuto '{sito}'")
    return bool(ADSENSE_CLIENT) and sito in ADSENSE_SITI


def tag_adsense(sito):
    """Il tag <script> ufficiale di AdSense (annunci automatici), oppure '' se spento."""
    if not adsense_attivo(sito):
        return ""
    return f'<script async src="{URL_ADSENSE_JS}?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>'


def script_adsense(sito):
    """Da mettere subito dopo il meta di verifica Google nel <head>: '' se spento (l'output resta identico),
    altrimenti un a capo seguito dal tag di AdSense."""
    t = tag_adsense(sito)
    return "\n" + t if t else ""


def riga_ads_txt(sito):
    if not adsense_attivo(sito):
        return ""
    return f"google.com, {ADSENSE_CLIENT[3:]}, DIRECT, {ADS_TXT_CERT}\n"


def scrivi_ads_txt(sito, cartella_sito):
    """Scrive sito/ads.txt con AdSense acceso; con AdSense spento lo toglie se c'è (di solito non c'è)."""
    f = Path(cartella_sito) / "ads.txt"
    riga = riga_ads_txt(sito)
    if riga:
        f.write_text(riga, encoding="utf-8")
    elif f.exists():
        f.unlink()


# ---------------------------------------------------------------- affiliazioni

def dominio_in(host, domini):
    host = (host or "").lower().rstrip(".")
    return bool(host) and any(host == d or host.endswith("." + d) for d in domini)


def dominio_ammesso(url):
    """True se l'URL punta a un dominio di affiliazione ammesso (e non bloccato)."""
    host = urlparse(url if "//" in url else "https://" + url).hostname or ""
    return dominio_in(host, DOMINI_AFFILIAZIONE) and not dominio_in(host, DOMINI_BLOCCATI)


def ha_link_sponsorizzati(html):
    return bool(re.search(r'<a\b[^>]*\brel="[^"]*\bsponsored\b', html, re.I))


def testo_visibile(html):
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", t)))


def riga(lingua):
    return RIGA_IT if lingua == "it" else RIGA_EN


def nota_trasparenza(lingua, classe="small"):
    """Il paragrafo con la riga di trasparenza (per i riquadri di affiliazione)."""
    return f'<p class="{classe} aff-nota">{riga(lingua)}</p>'


def riga_trasparenza(html, lingua, classe="small"):
    """Riquadro di trasparenza della pagina: '' finché la pagina non ha link rel="sponsored" (o se la riga c'è già)."""
    if not ha_link_sponsorizzati(html) or riga(lingua) in testo_visibile(html):
        return ""
    return nota_trasparenza(lingua, classe)


# ---------------------------------------------------------------- privacy

_GC_EN = ('To count visits we use <a href="https://www.goatcounter.com/" rel="noopener">GoatCounter</a>, a privacy-friendly counter: '
          "it sets no cookies and stores nothing in your browser, builds no profiles and does not store your IP address, your full browser "
          "signature or any identifier. It keeps only aggregate numbers (page, hour or day, browser, country, screen width) on servers in the "
          "European Union and shares nothing with third parties; see "
          '<a href="https://www.goatcounter.com/help/privacy" rel="noopener">GoatCounter\'s privacy policy</a>.')
_GC_IT = ('Per contare le visite usiamo <a href="https://www.goatcounter.com/" rel="noopener">GoatCounter</a>, un contatore rispettoso della '
          "privacy: non usa cookie e non salva nulla nel browser, non crea profili e non conserva l'indirizzo IP, la firma completa del browser "
          "né altri identificativi. Tiene solo numeri aggregati (pagina, ora o giorno, browser, Paese, larghezza dello schermo) su server "
          "nell'Unione europea e non cede nulla a terzi; vedi "
          '<a href="https://www.goatcounter.com/help/privacy" rel="noopener">l\'informativa privacy di GoatCounter</a>.')

_AFF_EN = ("<h2>Affiliate links</h2><p>Some links are affiliate links and are marked as such: if you buy through them we may earn a commission, "
           "at no extra cost to you. Our site sets no cookie for these links. If you click one, you go to the partner's website, which may use "
           "its own cookies, under its own privacy policy, to record that you came from us. We receive only aggregate reports (clicks, sales, "
           "commissions), never your name or contact details. Partners never decide what we publish.</p>")
_AFF_IT = ("<h2>Link di affiliazione</h2><p>Alcuni link sono di affiliazione e sono segnalati come tali: se acquisti tramite questi link "
           "potremmo ricevere una commissione, senza costi in più per te. Il nostro sito non usa cookie per questi link. Se ne apri uno, arrivi "
           "sul sito del partner, che può usare i propri cookie, secondo la propria informativa, per registrare che arrivi da noi. Riceviamo "
           "solo resoconti aggregati (clic, vendite, commissioni), mai il tuo nome o i tuoi recapiti. I partner non decidono mai cosa "
           "pubblichiamo.</p>")

_ADS_EN = ("<h2>Advertising (Google AdSense)</h2>"
           "<p>This site shows ads served by Google AdSense. Google and the advertising partners it works with use cookies and similar "
           "technologies (such as advertising identifiers and your browser's local storage) to show ads, limit how often you see the same ad, "
           "measure results, prevent fraud and, only if you allow it, personalise ads based on your visits to this and other websites. "
           "For these ads Google is an independent controller of the data it collects.</p>"
           "<p>If you are in the European Economic Area, the United Kingdom or Switzerland, a consent message appears on your first visit. "
           "It is Google's own certified consent management platform (Google “Privacy &amp; messaging”, certified under the IAB Transparency "
           "&amp; Consent Framework): advertising cookies and identifiers are used only with your consent, and you can change or withdraw your "
           "choice at any time from the privacy and cookie settings link that the message leaves on the page. If you say no, you may still see "
           "ads that are not personalised. The legal basis is your consent (Art. 6(1)(a) GDPR and the ePrivacy rules on cookies).</p>"
           f'<p>How Google uses information from sites that show its ads: <a href="{URL_PARTNER_SITES}" rel="noopener">'
           "policies.google.com/technologies/partner-sites</a>. You can turn off personalised ads from Google at any time in "
           f'<a href="{URL_ADS_SETTINGS}" rel="noopener">Google\'s ad settings</a>. Google may process data outside the EU with the '
           "safeguards required by the GDPR.</p>")
_ADS_IT = ("<h2>Pubblicità (Google AdSense)</h2>"
           "<p>Questo sito mostra annunci forniti da Google AdSense. Google e i partner pubblicitari con cui lavora usano cookie e tecnologie "
           "simili (come gli identificatori pubblicitari e la memoria locale del browser) per mostrare gli annunci, limitare quante volte vedi "
           "lo stesso annuncio, misurarne i risultati, prevenire le frodi e, solo se lo consenti, personalizzarli in base alle tue visite a "
           "questo e ad altri siti. Per questi annunci Google tratta i dati che raccoglie come titolare autonomo.</p>"
           "<p>Se ti trovi nello Spazio economico europeo, nel Regno Unito o in Svizzera, alla prima visita compare un messaggio di consenso: "
           "è la piattaforma di gestione del consenso certificata di Google («Privacy e messaggi», certificata nel Transparency &amp; Consent "
           "Framework di IAB). Cookie e identificatori pubblicitari si usano solo con il tuo consenso, e puoi cambiare o ritirare la scelta "
           "quando vuoi dal link alle impostazioni di privacy e cookie che il messaggio lascia nella pagina. Se rifiuti, potresti comunque "
           "vedere annunci non personalizzati. La base giuridica è il tuo consenso (art. 6.1.a GDPR e art. 122 del Codice privacy).</p>"
           f'<p>Come Google usa i dati dei siti che mostrano i suoi annunci: <a href="{URL_PARTNER_SITES}" rel="noopener">'
           "policies.google.com/technologies/partner-sites</a>. Puoi disattivare gli annunci personalizzati di Google quando vuoi dalle "
           f'<a href="{URL_ADS_SETTINGS}" rel="noopener">impostazioni annunci di Google</a>. Google può trattare i dati fuori dall\'UE con '
           "le garanzie previste dal GDPR.</p>")


def privacy_cookie(lingua, sito, affiliati=False):
    """Sezioni privacy su cookie, contatore, link di affiliazione e pubblicità.
    Restituisce '' se il sito non ha né AdSense acceso né link di affiliazione: in quel caso il genera.py usa il suo testo di oggi."""
    ads = adsense_attivo(sito)
    if not ads and not affiliati:
        return ""
    it = lingua == "it"
    if ads:
        fine = (" Il contatore non usa cookie; la pubblicità descritta qui sotto sì." if it else
                " The visit counter uses no cookies; the advertising described below does.")
    else:
        fine = (" Il sito non usa cookie di profilazione e non mostra pubblicità." if it else
                " This site does not use profiling cookies and shows no advertising.")
    testo = (f"<h2>{'Cookie e contatore visite' if it else 'Cookies and visit counter'}</h2>"
             f"<p>{_GC_IT if it else _GC_EN}{fine}</p>")
    if affiliati:
        testo += "\n" + (_AFF_IT if it else _AFF_EN)
    if ads:
        testo += "\n" + (_ADS_IT if it else _ADS_EN)
    return testo


def frase_california(sito):
    """Siti per il pubblico USA (FloodCost, ApprovedCondos, Cruise Health Scores): con AdSense acceso la frase di oggi
    "we do not sell or share personal information" non basta più; '' se AdSense è spento (resta la frase di oggi)."""
    if not adsense_attivo(sito):
        return ""
    return ("California residents: we do not sell personal information. Personalised Google ads are explained in the advertising "
            "section above, and you can opt out of them at any time in Google's ad settings.")


def privacy_breve(lingua, sito, affiliati=False):
    """Frase breve per sottotitoli e meta description delle pagine privacy che oggi dicono "no cookies":
    '' se nulla è attivo (resta il testo di oggi)."""
    if adsense_attivo(sito):
        return ("Cosa raccogliamo, il contatore visite senza cookie e i cookie pubblicitari di Google, solo con il tuo consenso." if lingua == "it"
                else "What we collect, a visit counter without cookies, and Google's advertising cookies, used only with your consent.")
    if affiliati:
        return ("Cosa raccogliamo (pochissimo), il contatore visite senza cookie e i link di affiliazione." if lingua == "it"
                else "What we collect (very little), a visit counter without cookies, and how affiliate links work.")
    return ""


# ---------------------------------------------------------------- controlli comuni (usati da ogni verifica.py)

_RE_A = re.compile(r"<a\b[^>]*>", re.I)
_RE_ATTR = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')


def link_affiliati(html):
    """Elenco dei link della pagina da trattare come affiliati: rel con 'sponsored', oppure verso un dominio
    di affiliazione ammesso o bloccato. Ogni voce: (href, host, token di rel)."""
    voci = []
    for m in _RE_A.finditer(html):
        a = {k.lower(): unescape(v) for k, v in _RE_ATTR.findall(m.group(0))}
        href = a.get("href", "")
        rel = set(a.get("rel", "").lower().split())
        host = ""
        if href.startswith(("http://", "https://", "//")):
            host = (urlparse(href if not href.startswith("//") else "https:" + href).hostname or "").lower()
        if "sponsored" in rel or dominio_in(host, DOMINI_AFFILIAZIONE) or dominio_in(host, DOMINI_BLOCCATI):
            voci.append((href, host, rel))
    return voci


def controlla_link_pagina(html, nome, lingua=None):
    """Errori sui link di affiliazione di una pagina (lista vuota se è tutto a posto)."""
    errori = []
    if lingua is None:
        lingua = "it" if re.search(r'<html[^>]*\blang="it', html, re.I) else "en"
    voci = link_affiliati(html)
    for href, host, rel in voci:
        if dominio_in(host, DOMINI_BLOCCATI):
            errori.append(f"{nome}: link verso un dominio bloccato ({host})")
            continue
        if not host:
            errori.append(f"{nome}: link rel=\"sponsored\" senza indirizzo esterno ({href[:80]})")
            continue
        if not dominio_in(host, DOMINI_AFFILIAZIONE):
            errori.append(f"{nome}: link di affiliazione verso un dominio non ammesso ({host}): aggiungerlo a monetizzazione.json solo se è un programma vero")
        if "sponsored" not in rel or "noopener" not in rel:
            errori.append(f"{nome}: link di affiliazione senza rel=\"sponsored noopener\" ({host})")
        if dominio_in(host, ["amazon.it"]) and not re.search(r"[?&]tag=[^&]+", href):
            errori.append(f"{nome}: link Amazon.it senza il tag di affiliazione (tag=)")
    if voci and riga(lingua) not in testo_visibile(html):
        errori.append(f"{nome}: link di affiliazione senza la riga di trasparenza «{riga(lingua)}»")
    return errori, len(voci)


def controlla_sito(sito, cartella_sito):
    """Controlli comuni di monetizzazione su tutta la cartella sito/. Restituisce la lista degli errori."""
    cartella = Path(cartella_sito)
    errori = []
    attivo = adsense_attivo(sito)
    tag = tag_adsense(sito)
    pagine = sorted(cartella.rglob("*.html"))
    privacy, n_aff, pagine_aff = [], 0, 0
    for f in pagine:
        nome = str(f.relative_to(cartella))
        t = f.read_text(encoding="utf-8", errors="replace")
        if f.name == "privacy.html" or (f.name == "index.html" and f.parent.name == "privacy"):
            privacy.append((nome, t))
        fine_testa = t.lower().find("</head>")
        if fine_testa >= 0 and not re.fullmatch(r"google[0-9a-f]+\.html", f.name):
            testa = t[:fine_testa]
            if attivo:
                if testa.count(tag) != 1:
                    errori.append(f"{nome}: script AdSense assente, doppio o con un codice editore diverso nel <head>")
            elif "adsbygoogle" in t or "googlesyndication.com" in t:
                errori.append(f"{nome}: codice AdSense presente ma AdSense è spento per {sito} in monetizzazione.json")
        e, n = controlla_link_pagina(t, nome)
        errori += e
        n_aff += n
        pagine_aff += bool(n)
    ads = cartella / "ads.txt"
    if attivo:
        if not ads.exists() or ads.read_text(encoding="utf-8") != riga_ads_txt(sito):
            errori.append(f"ads.txt assente o diverso da «{riga_ads_txt(sito).strip()}»")
    elif ads.exists():
        errori.append("ads.txt presente ma AdSense è spento in monetizzazione.json")
    if not privacy:
        errori.append("nessuna pagina privacy trovata (privacy.html)")
    for nome, t in privacy:
        testo = testo_visibile(t)
        if attivo:
            for u in (URL_PARTNER_SITES, URL_ADS_SETTINGS):
                if f'href="{u}"' not in t:
                    errori.append(f"{nome}: AdSense acceso ma manca il link a {u}")
            if "AdSense" not in testo or ("consenso" not in testo and "consent" not in testo):
                errori.append(f"{nome}: AdSense acceso ma manca la sezione sulla pubblicità e sul consenso")
        elif URL_ADS_SETTINGS in t:
            errori.append(f"{nome}: sezione AdSense presente ma AdSense è spento")
        if n_aff and not re.search(r"affiliate link|di affiliazione", testo, re.I):
            errori.append(f"{nome}: il sito ha link di affiliazione ma la privacy non li spiega")
    return errori, {"adsense": attivo, "pagine": len(pagine), "link_affiliati": n_aff, "pagine_con_affiliati": pagine_aff}


def riepilogo(sito, info, errori):
    return (f"Monetizzazione ({sito}): AdSense {'acceso' if info['adsense'] else 'spento'}, "
            f"ads.txt {'atteso' if info['adsense'] else 'assente'}, {info['link_affiliati']} link di affiliazione in "
            f"{info['pagine_con_affiliati']} pagine su {info['pagine']}: {len(errori)} errori")


# ---------------------------------------------------------------- riga di comando

def _salva(cfg):
    FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, resto = argv[0], argv[1:]
    if cmd == "stato":
        print(f"adsense_client: {ADSENSE_CLIENT or '(vuoto: AdSense spento ovunque)'}")
        for s in SITI:
            print(f"  {s:13} AdSense {'ACCESO' if adsense_attivo(s) else 'spento'}")
        print(f"domini di affiliazione ammessi: {len(DOMINI_AFFILIAZIONE)}; bloccati: {', '.join(DOMINI_BLOCCATI)}")
        return 0
    if cmd == "attiva":
        if not resto:
            raise SystemExit("uso: attiva ca-pub-XXXXXXXXXXXXXXXX sito [altri siti...]   (oppure: attiva sito, se il codice c'è già)")
        cfg = json.loads(FILE.read_text(encoding="utf-8"))
        if re.match(r"(ca-)?pub-", resto[0]):
            cfg["adsense_client"] = _cliente(resto[0])
            resto = resto[1:]
        elif not _cliente(cfg.get("adsense_client", "")):
            raise SystemExit("manca il codice editore: attiva ca-pub-XXXXXXXXXXXXXXXX sito")
        for s in resto:
            if s not in SITI:
                raise SystemExit(f"sito sconosciuto '{s}' (nomi ammessi: {', '.join(SITI)})")
            if s not in cfg["adsense_siti"]:
                cfg["adsense_siti"].append(s)
        _salva(cfg)
        print(f"Salvato. AdSense acceso per: {', '.join(cfg['adsense_siti']) or 'nessun sito'}. "
              f"Ora rigenera i siti ({'; '.join(f'python3 {s}/genera.py' for s in resto)}) e lancia la verifica.")
        return 0
    if cmd == "spegni":
        cfg = json.loads(FILE.read_text(encoding="utf-8"))
        cfg["adsense_siti"] = [s for s in cfg["adsense_siti"] if s not in resto] if resto else []
        _salva(cfg)
        print(f"Salvato. AdSense acceso per: {', '.join(cfg['adsense_siti']) or 'nessun sito'}. Rigenera i siti tolti.")
        return 0
    if cmd == "verifica":
        siti = resto or SITI
        totale = 0
        for s in siti:
            if s not in SITI:
                raise SystemExit(f"sito sconosciuto '{s}'")
            errori, info = controlla_sito(s, RADICE_REPO / s / "sito")
            print(riepilogo(s, info, errori))
            for e in errori[:30]:
                print("   -", e)
            totale += len(errori)
        return 1 if totale else 0
    raise SystemExit(f"comando sconosciuto '{cmd}' (stato, attiva, spegni, verifica)")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
