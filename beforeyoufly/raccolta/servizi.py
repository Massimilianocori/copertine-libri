"""Legge le liste ufficiali dei Paesi dei servizi digitali e scrive dati/servizi.json (sezione "Is [service] available in [country]?").

Uso (dalla radice del repository):
    python3 -I beforeyoufly/raccolta/servizi.py             legge le fonti, scrive dati/servizi.json (e dati/servizi_cambi.json se una lista cambia)
    python3 -I beforeyoufly/raccolta/servizi.py --domanda   rilegge anche l'autocompletamento di Google e riscrive dati/servizi_domanda.json

Regole (decise il 28/10/2026):
  - Solo servizi con una lista dei Paesi pubblicata dal fornitore stesso e leggibile con una richiesta HTTP normale (niente browser, niente
    JavaScript): Starlink (file JSON della mappa ufficiale), Apple (pagina "Availability of Apple Media Services" e pagina Apple Pay),
    YouTube Premium (pagina di aiuto di Google), Spotify (pagina di aiuto). Nessun assistente di intelligenza artificiale (regola di Massimiliano).
    Dal 7/11/2026 anche Google Wallet (menu dei Paesi della pagina di aiuto, una pagina per Paese con le funzioni, e lista "Google Pay" per i
    pagamenti online), Wise (tabella "hold money", elenco dei Paesi non serviti, lista dei Paesi verso cui si invia), Uber (pagina "Uber Cities"),
    Stripe (pagina "Global availability"). Scartati il 7/11: Revolut (403, controllo anti-bot), Disney+ (pagina solo JavaScript), Prime Video
    (Amazon 503/403 ai robot), PayPal (solo il selettore dei siti nazionali), Netflix (elenca solo dove NON è disponibile), Samsung Wallet,
    Payoneer, Crunchyroll (nessuna lista trovata), Tidal (controllo anti-bot); assistenti di intelligenza artificiale per regola.
  - Si salva SOLO cosa dice la fonte: "si" = il Paese è nella lista con il servizio; "no" = la fonte nomina il Paese ma dice che il servizio non
    c'è (es. YouTube "Russia - temporarily unavailable", Apple elenca il Paese senza Apple Music, Starlink senza servizio sulla mappa);
    "in_arrivo" = Starlink "Coming soon"; "per_regione" = Starlink colora il Paese regione per regione (stato "exclude"). Un Paese che la fonte non nomina NON compare: le pagine dicono "not on the list", mai "vietato".
  - Nomi dei Paesi normalizzati sui codici ISO 3166-1 alfa-2 di dati/paesi_iso.json (gli stessi del Canada e della sezione italiana).
    Un nome che non si riconosce ferma lo script (va aggiunto a mano come alias o in REGIONI).
  - Ogni lista ha un'impronta SHA-256 (della lista normalizzata, non dell'HTML, che cambia a ogni richiesta). Se l'impronta cambia, le
    differenze vanno in dati/servizi_cambi.json e "cambiato_il" prende la data di oggi.
  - Le frasi citate nelle pagine (FRASI) devono esserci parola per parola; se una manca, o se una lista perde più del 20 % dei Paesi,
    lo script NON sovrascrive dati/servizi.json ed esce con 1: si controlla a mano.
  - Pagine grezze in raccolta/.cache/servizi/ (esclusa da git: testi dei fornitori senza licenza aperta).
"""
import hashlib
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import date
from html import unescape
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
CACHE = Path(__file__).resolve().parent / ".cache" / "servizi"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
ACCETTA = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"

# ---------------------------------------------------------------- fonti
FONTI = {
    "starlink": {"url": "https://api.starlink.com/public-files/availability.json", "tipo": "json"},
    "apple_media": {"url": "https://support.apple.com/en-us/118205", "tipo": "html"},
    "apple_pay": {"url": "https://support.apple.com/en-us/102775", "tipo": "html"},
    "youtube": {"url": "https://support.google.com/youtube/answer/6307365?hl=en", "tipo": "html"},
    "spotify": {"url": "https://support.spotify.com/us/article/where-spotify-is-available/", "tipo": "html"},
    "spotify_estero": {"url": "https://support.spotify.com/us/article/cant-play-abroad/", "tipo": "html"},
    # dal 7/11/2026
    "google_wallet": {"url": "https://support.google.com/wallet/answer/12060037?hl=en", "tipo": "html"},
    # una pagina per ogni Paese del menu (parametro co=...): si salva solo la tabella "Here's what is available in your country" di ognuna
    "google_wallet_paesi": {"url": "https://support.google.com/wallet/answer/12060037?hl=en&co=ADWORDS.BillingCountryCode%3D{}", "tipo": "json",
                            "derivata": "google_wallet"},
    "google_pay": {"url": "https://support.google.com/googlepay/answer/12429287?hl=en", "tipo": "html"},
    "wise": {"url": "https://wise.com/help/articles/2813542/where-do-i-need-to-live-to-hold-money-with-wise", "tipo": "html"},
    "wise_dove": {"url": "https://wise.com/help/articles/2978049/where-can-i-use-wise", "tipo": "html"},
    "wise_invio": {"url": "https://wise.com/help/articles/2571942/what-countriesregions-can-i-send-to", "tipo": "html"},
    "uber": {"url": "https://www.uber.com/global/en/cities/", "tipo": "html"},
    "stripe": {"url": "https://stripe.com/global", "tipo": "html"},
}

# Servizi pubblicati: slug (URL), nome, fonte della lista, pagina da mostrare ai lettori, frase che definisce la lista.
SERVIZI = [
    {"slug": "starlink", "nome": "Starlink", "fornitore": "Starlink (SpaceX)", "fonte": "starlink",
     "pagina": "https://www.starlink.com/map", "titolo_fonte": "Starlink availability map",
     "cosa": "Starlink internet service"},
    {"slug": "apple-pay", "nome": "Apple Pay", "fornitore": "Apple", "fonte": "apple_pay",
     "pagina": "https://support.apple.com/en-us/102775", "titolo_fonte": "Apple Support: Countries and regions that support Apple Pay",
     "cosa": "adding cards from local banks to Apple Pay"},
    {"slug": "apple-music", "nome": "Apple Music", "fornitore": "Apple", "fonte": "apple_media",
     "pagina": "https://support.apple.com/en-us/118205", "titolo_fonte": "Apple Support: Availability of Apple Media Services",
     "cosa": "Apple Music"},
    {"slug": "apple-tv", "nome": "Apple TV", "fornitore": "Apple", "fonte": "apple_media",
     "pagina": "https://support.apple.com/en-us/118205", "titolo_fonte": "Apple Support: Availability of Apple Media Services",
     "cosa": "the Apple TV subscription"},
    {"slug": "youtube-premium", "nome": "YouTube Premium", "fornitore": "YouTube (Google)", "fonte": "youtube",
     "pagina": "https://support.google.com/youtube/answer/6307365?hl=en", "titolo_fonte": "YouTube Help: Premium memberships available locations & travel policies",
     "cosa": "YouTube Premium and YouTube Music Premium memberships"},
    {"slug": "spotify", "nome": "Spotify", "fornitore": "Spotify", "fonte": "spotify",
     "pagina": "https://support.spotify.com/us/article/where-spotify-is-available/", "titolo_fonte": "Spotify Support: Where is Spotify available?",
     "cosa": "signing up for Spotify"},
    # dal 7/11/2026 (in ordine di domanda: ricerche dell'autocompletamento del 7/11)
    {"slug": "google-wallet", "nome": "Google Wallet", "fornitore": "Google", "fonte": "google_wallet",
     "pagina": "https://support.google.com/wallet/answer/12060037?hl=en", "titolo_fonte": "Google Wallet Help: Supported countries for Google Wallet & tap to pay",
     "cosa": "the Google Wallet app"},
    {"slug": "wise", "nome": "Wise", "fornitore": "Wise", "fonte": "wise",
     "pagina": "https://wise.com/help/articles/2813542/where-do-i-need-to-live-to-hold-money-with-wise", "titolo_fonte": "Wise Help Centre: Where do I need to live to hold money with Wise?",
     "cosa": "holding money in a Wise account"},
    {"slug": "uber", "nome": "Uber", "fornitore": "Uber", "fonte": "uber",
     "pagina": "https://www.uber.com/global/en/cities/", "titolo_fonte": "Uber Cities: Use Uber in cities around the world",
     "cosa": "Uber rides"},
    {"slug": "stripe", "nome": "Stripe", "fornitore": "Stripe", "fonte": "stripe",
     "pagina": "https://stripe.com/global", "titolo_fonte": "Stripe global availability",
     "cosa": "opening a Stripe account for a business"},
]

# Testo che deve esserci perché la pagina letta sia quella giusta (altrimenti si riprova)
SEGNI = {"apple_media": "Availability of Apple Media Services", "apple_pay": "Countries and regions that support Apple Pay",
         "youtube": "Premium & Music Premium memberships available locations", "spotify": "Where is Spotify available?",
         "spotify_estero": "Can’t play abroad", "google_wallet": "Supported countries for Google Wallet & tap to pay",
         "google_pay": "Countries or regions where you can make payments with Google", "wise": "Where do I need to live to hold money with Wise?",
         "wise_dove": "Where can I use Wise?", "wise_invio": "What countries/regions can I send to?", "uber": "Use Uber in cities around the world",
         "stripe": "Stripe is currently supported in the following countries/regions"}

# Frasi citate nelle pagine del sito: devono stare nella fonte parola per parola (testo normalizzato). chiave -> (fonte, frase)
FRASI = {
    "apple_pay_lista": ("apple_pay", "You can add your credit, debit, or prepaid cards from participating banks and card issuers in these countries and regions:"),
    "apple_pay_accettato": ("apple_pay", "Apple Pay is accepted anywhere you see these symbols and marks in stores, within apps, and on the web in Safari and third-party browsers."),
    "apple_pay_cash": ("apple_pay", "Sending and receiving money with Apple Pay and the Apple Cash card are available only in the U.S."),
    "apple_media_lista": ("apple_media", "Find your country or region below to see what's available to you."),
    "apple_media_varia": ("apple_media", "Depending on your country or region, you might not be able to buy, download, or subscribe to certain types of media."),
    "youtube_titolo": ("youtube", "Premium & Music Premium memberships available locations"),
    "youtube_lista": ("youtube", "YouTube Premium memberships are available in the countries/territories listed below."),
    "youtube_nota": ("youtube", "YouTube paid memberships may not be available in some provinces or territories, even if the governing country/region is listed above."),
    "youtube_paese": ("youtube", "Your YouTube Premium membership should be used predominantly in the country where you signed up for it (your subscription country)."),
    "youtube_viaggio_no": ("youtube", "If you travel to a country where Premium / Premium Lite is not available, you won’t be able to access your membership benefits."),
    "youtube_offline": ("youtube", "Any videos that you’ve downloaded before traveling will be available offline for 30 days."),
    "youtube_30": ("youtube", "If you are traveling for more than 30 days or move to a different country or territory, we may take action on your subscription, such as cancelling it."),
    "spotify_lista": ("spotify", "Check the list below for where you can sign up for Spotify."),
    "spotify_paese": ("spotify_estero", "The country or region of your Spotify account is based on where you were when you signed up."),
    "spotify_trasloco": ("spotify_estero", "If you've moved, update your account country and payment method to one that's valid where you live now."),
    # dal 7/11/2026
    "google_wallet_lista": ("google_wallet", "To verify if Google Wallet is available, select your country from the dropdown."),
    "google_wallet_assente": ("google_wallet", "If your country isn’t listed, Google Wallet isn’t available in your country yet."),
    "google_wallet_tocco": ("google_wallet", "You can use tap to pay to store forms of payments and make contactless transactions on the Google Wallet app."),
    "google_pay_varia": ("google_pay", "Some Google Pay and Google Wallet payments features are only available in certain countries or regions and on certain devices."),
    "google_pay_online": ("google_pay", "With participating websites and apps, you can use Google Pay in:"),
    "google_pay_invio": ("google_pay", "You can use Google Pay to send money in India and Singapore."),
    "wise_lista": ("wise", "You can hold money in your account if you live in one of the following countries and territories:"),
    "wise_nuovi": ("wise", "We sometimes need to make changes that only affect new accounts."),
    "wise_ovunque": ("wise_dove", "You can register and send money with Wise from most countries around the world"),
    "wise_no": ("wise_dove", "There are some places where we don’t offer our services:"),
    "wise_no_invio": ("wise_dove", "send or receive money to or from these countries and regions"),
    "wise_no_cosa": ("wise_dove", "log into your Wise account, register a new account, or use your Wise card if you’re in these countries and regions"),
    "wise_invio_lista": ("wise_invio", "Here’s a list of the countries/regions you can send money to with Wise."),
    "uber_lista": ("uber", "Get to your destination in more than 15,000 cities."),
    "stripe_lista": ("stripe", "Stripe is currently supported in the following countries/regions, with more to come."),
    "stripe_vendere": ("stripe", "Once Stripe is supported in your country/region, you’ll be able to sell to customers anywhere in the world."),
}

# Starlink: significato degli stati del file, letto il 28/10/2026 nel codice della mappa ufficiale (starlink.com/map, file page-*.js):
# legenda "Available" = launched, available (tooltip "Available Now"); legenda "Coming soon" ("Pending service coverage or regulatory approval.")
# = test, pending_regulatory, coming_soon, unknown; blacklisted = grigio (colore "blacklistedSolid", fuori legenda), nessun tooltip.
# exclude (revisione del 28/10/2026): il Paese intero non ha colore, ma le sue regioni (livello admin1 del file, id Mapbox) sì. Nel file del
# 28/10 gli exclude sono Ucraina, Georgia e Cipro, e le regioni admin1 sono 27 + 13 + 6 (le regioni di Ucraina, Georgia e Cipro); sulla mappa
# (schermata del 28/10) Ucraina, Georgia e Cipro del sud risultano "Available", Crimea, Abcasia/Ossezia del Sud e Cipro del nord no.
# Quindi exclude NON vuol dire "nessun servizio": si scrive "per_regione" ("By region" nelle pagine, con l'invito a controllare l'indirizzo).
# Uno stato nuovo nel file ferma lo script: va letto di nuovo il codice della mappa.
STATI_STARLINK = {"launched": "si", "available": "si", "coming_soon": "in_arrivo", "pending_regulatory": "in_arrivo", "unknown": "in_arrivo",
                  "test": "in_arrivo", "blacklisted": "no", "exclude": "per_regione"}
TOOLTIP_STARLINK = {"pending_regulatory": "Pending regulatory approval", "unknown": "Service date is unknown at this time"}

# Nomi della fonte che non sono un Paese ISO: parti di un Paese già elencato (si registrano come "regioni") o gruppi di territori.
REGIONI = {"azores": "PT", "madeira": "PT", "balearic islands": "ES", "canary islands": "ES", "ceuta": "ES", "melilla": "ES",
           "netherlands antilles": None}
# Nomi che valgono per un codice ISO che copre più territori (la fonte li elenca uno per uno)
PARTI = {"ascension": "SH", "tristan da cunha": "SH", "saint helena": "SH", "bonaire": "BQ", "saba": "BQ", "sint eustatius": "BQ",
         "svalbard": "SJ", "puerto rico": "PR",
         # Google Pay (7/11/2026): il Paese "e territori d'oltremare" vale per il Paese stesso (i territori non sono nominati uno per uno)
         "united kingdom and outlying territories": "GB", "united states and outlying territories": "US"}


def chiave(s):
    s = unicodedata.normalize("NFKD", unescape(s)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z ]", " ", s)
    s = re.sub(r"\bthe\b", " ", s)
    return " ".join(s.split())


ISO = json.loads((DATI / "paesi_iso.json").read_text(encoding="utf-8"))["paesi"]
PER_CHIAVE = {}
for _p in ISO:
    for _n in [_p["nome"]] + _p["alias"]:
        PER_CHIAVE[chiave(_n)] = _p["iso2"]
CODICI = {p["iso2"] for p in ISO}


def iso_di(nome):
    """Codice ISO di un nome della fonte; None se è una regione di un Paese (REGIONI); errore se sconosciuto."""
    k = chiave(nome)
    if k in PER_CHIAVE:
        return PER_CHIAVE[k]
    if k in PARTI:
        return PARTI[k]
    if k in REGIONI:
        return None
    if k.startswith("united states minor outlying islands"):
        return "UM"
    raise ValueError(f"nome sconosciuto: {nome!r}")


# ---------------------------------------------------------------- lettura
def leggi(url):
    # Accept come un browser: senza, uber.com risponde 406 "Not Acceptable" (7/11/2026)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9", "Accept": ACCETTA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.geturl(), r.read().decode("utf-8", "replace")


def testo(html_):
    t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", html_)
    t = re.sub(r"<sup>.*?</sup>", "", t)
    t = re.sub(r"</?(?:strong|b|em|i|a|span|abbr)\b[^>]*>", "", t)
    t = unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    return re.sub(r"\s+", " ", t)


def pulito(x):
    x = re.sub(r"<sup>.*?</sup>", "", x)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", x)).replace("\xa0", " ")).strip()


def data_pubblicazione(html_):
    """Apple: 'Published Date: October 27, 2026' -> '2026-10-27'."""
    m = re.search(r"Published Date:\s*([A-Z][a-z]+ \d{1,2}, \d{4})", testo(html_))
    if not m:
        return None
    from datetime import datetime
    return datetime.strptime(m.group(1), "%B %d, %Y").date().isoformat()


def aggiungi(paesi, regioni, nome_fonte, stato, nota=None):
    c = iso_di(nome_fonte)
    if c is None:
        regioni.append(nome_fonte)
        return
    v = paesi.setdefault(c, {"stato": stato, "nomi_fonte": []})
    if nome_fonte not in v["nomi_fonte"]:
        v["nomi_fonte"].append(nome_fonte)
    if v["stato"] != stato:
        raise ValueError(f"{c}: stati diversi nella stessa fonte ({v['stato']} / {stato})")
    if nota:
        v["nota"] = nota


def lista_starlink(raw):
    d = json.loads(raw)
    paesi, altri = {}, {}
    for cod, v in d["admin0"].items():
        st = v["status"]
        if st not in STATI_STARLINK:
            raise ValueError(f"Starlink: stato nuovo {st!r} per {cod}: rileggere il codice della mappa")
        voce = {"stato": STATI_STARLINK[st], "stato_fonte": st}
        tip = v.get("expected") or TOOLTIP_STARLINK.get(st)
        if voce["stato"] == "in_arrivo" and tip:
            voce["nota"] = tip
        (paesi if cod in CODICI else altri)[cod] = voce
    if any(v["stato"] == "per_regione" for v in paesi.values()) and not d.get("admin1"):
        raise ValueError("Starlink: Paesi 'exclude' ma nessuna regione admin1 nel file: rileggere il codice della mappa")
    return paesi, {"codici_non_iso": altri, "regioni_separate": len(d.get("admin1", {}))}


def lista_apple_media(html_):
    """Per ogni Paese (h3): servizi di primo livello e voci annidate. Restituisce {nome_fonte: {servizio: [voci]}}."""
    t = re.sub(r"<sup>.*?</sup>", "", html_)
    out = {}
    for m in re.finditer(r'<h3 class="gb-header">(.*?)</h3>\s*<ul role="list" class="list gb-list">(.*?)</ul>(?=\s*(?:<h3|</div>))', t, re.S):
        paese, blocco = pulito(m.group(1)), m.group(2)
        servizi = {}
        # elementi di primo livello: <li ...><p ...>Nome</p>(<ul>...</ul>)?</li>
        for li in re.finditer(r'<li role="listitem" class="gb-list_item"><p class="gb-paragraph">([^<]*)</p>(<ul role="list" class="list gb-list">.*?</ul>)?</li>', blocco, re.S):
            nome = pulito(li.group(1))
            figli = [pulito(x) for x in re.findall(r'<p class="gb-paragraph">([^<]*)</p>', li.group(2) or "")]
            servizi[nome] = figli
        out[paese] = servizi
    return out


def lista_apple_pay(html_):
    i = html_.find("prepaid cards from participating banks and card issuers in these countries and regions")
    j = html_.find("Sending and receiving money with Apple Pay")
    if i < 0 or j < 0:
        raise ValueError("Apple Pay: inizio o fine della lista non trovati")
    nomi = []
    for p in re.findall(r'<p class="gb-paragraph[^"]*">((?:<b>[^<]*</b>)+)</p>', html_[i:j]):
        parti = [pulito(x) for x in re.findall(r"<b>([^<]*)</b>", p)]
        if len(parti) == 2 and parti[1].startswith("and "):  # "The United States" + " and Puerto Rico"
            nomi += [parti[0], parti[1][4:]]
        else:
            nomi.append(" ".join(parti))
    return nomi


def lista_youtube(html_):
    i = html_.find("Premium &amp; Music Premium memberships available locations")
    j = html_.find("Premium Lite memberships available locations")
    if i < 0 or j < 0:
        raise ValueError("YouTube: tabella non trovata")
    return [pulito(x) for x in re.findall(r"<td>(.*?)</td>", html_[i:j], re.S) if pulito(x)]


def lista_spotify(html_):
    i = html_.find("Check the list below for where you can sign up for Spotify.")
    j = html_.find("Related Articles", i)
    if i < 0 or j < 0:
        raise ValueError("Spotify: lista non trovata")
    return [pulito(x) for x in re.findall(r"<li>(.*?)</li>", html_[i:j], re.S)]


CAMPI_IN_PIU = ("app", "tocco", "sito")  # Google Wallet: le tre righe della tabella di ogni Paese (dal 7/11/2026)
LISTE_IN_PIU = ("online", "invio")  # in "extra": Paesi della lista Google Pay online, Paesi verso cui Wise invia (dal 7/11/2026)


def firma(v):
    """Ciò che conta di una voce: stato, nota e (solo dove ci sono) i campi in più. Le voci senza campi in più restano come prima del 7/11."""
    f = [v["stato"], v.get("nota")]
    piu = {k: v[k] for k in CAMPI_IN_PIU if k in v}
    return f + [piu] if piu else f


def menu_google_wallet(html_):
    """Menu dei Paesi della pagina Google Wallet: [(codice della fonte, nome)], senza doppioni. Il Paese di chi legge (Stati Uniti dal nostro
    server) è l'opzione selected="selected": va contata anche quella (errore corretto il 7/11/2026, gli Stati Uniti mancavano)."""
    out = []
    for cod, nome in re.findall(r'<option (?:selected="selected" )?value="https://support\.google\.com/wallet/answer/12060037\?hl=en&amp;co=ADWORDS\.BillingCountryCode%3D([A-Z]{2})">([^<]*)</option>', html_):
        if (cod, pulito(nome)) not in out:
            out.append((cod, pulito(nome)))
    if len(out) < 100:
        raise ValueError(f"Google Wallet: menu dei Paesi con {len(out)} voci")
    return out


def tabella_google_wallet(html_):
    """Tabella 'Here's what is available in your country' di una pagina Paese: titolo e righe [(funzione, testo alternativo dell'icona)]."""
    tit = re.search(r"<title>([^<]*)</title>", html_)
    art = html_[html_.find("<article"):html_.find("</article>")]
    i = art.find("Here’s what is available in your country:")
    m = re.search(r"<table.*?</table>", art[i:], re.S) if i >= 0 else None
    if not tit or not m:
        raise ValueError("Google Wallet: tabella del Paese non trovata")
    return {"titolo": pulito(tit.group(1)), "tabella": re.sub(r"\s+", " ", m.group(0))}


def righe_google_wallet(tabella):
    return [(pulito(a), re.findall(r'alt="([^"]*)"', b)) for a, b in re.findall(r"<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>", tabella, re.S)]


ICONE_GW = {"Green checkmark": True, "Red crossmark": False}
FUNZIONI_GW = {"Google Wallet app": "app", "Tap to pay": "tocco", "Google Wallet website": "sito"}


def lista_google_pay(html_):
    i = html_.find("With participating websites and apps, you can use Google Pay in:")
    j = html_.find("Paying in Chrome with info saved to Chrome", i)
    if i < 0 or j < 0:
        raise ValueError("Google Pay: lista 'Pay online or in apps' non trovata")
    return [pulito(x) for x in re.findall(r"<li>(.*?)</li>", html_[i:j], re.S)]


def lista_wise(html_):
    """Tabella 'hold money': [(Paese, restrizione o '')]."""
    i = html_.find("following countries and territories:")
    j = html_.find("</table>", i)
    if i < 0 or j < 0:
        raise ValueError("Wise: tabella 'hold money' non trovata")
    out = []
    for a, b in re.findall(r"<tr><td>(.*?)</td><td>(.*?)</td></tr>", html_[i:j], re.S):
        b = re.sub(r"\s*<a [^>]*>Learn more here</a>", "", b)  # India: link "Learn more here" dopo la frase
        out.append((pulito(a), pulito(b)))
    return out


def lista_wise_no(html_):
    """'There are some places where we don't offer our services:' -> (Paesi, regioni dell'Ucraina)."""
    m = re.search(r"There are some places where we don’t offer our services:\s*</p>\s*<p>(.*?)</p>", html_, re.S)
    if not m:
        raise ValueError("Wise: elenco dei Paesi non serviti non trovato")
    t = pulito(m.group(1)).rstrip(". ")
    paesi, _, regioni = t.partition(", and the Ukraine regions:")
    if not regioni:
        raise ValueError("Wise: forma dell'elenco dei Paesi non serviti cambiata")
    return [x.strip() for x in paesi.split(",")], [x.strip() for x in regioni.split(",")]


def lista_wise_invio(html_):
    i = html_.find("Here’s a list of the countries/regions you can send money to with Wise.", html_.find("<body"))
    j = html_.find("</table>", i)
    if i < 0 or j < 0:
        raise ValueError("Wise: lista dei Paesi verso cui si invia non trovata")
    return [pulito(x) for x in re.findall(r'<td><a href="[^"]*">(.*?)</a></td>', html_[i:j])]


def lista_uber(html_):
    i = html_.find("Use Uber in cities around the world")
    j = html_.find("Visit Help Center", i)
    if i < 0 or j < 0:
        raise ValueError("Uber: lista dei Paesi non trovata")
    return [pulito(x) for x in re.findall(r'<a data-baseweb="link" href="https://www\.uber\.com/global/en/r/[a-z0-9-]+/cities/" data-testid="list-text-links-link"[^>]*>([^<]*)</a>', html_[i:j])]


def lista_stripe(html_):
    """[(nome, codice della bandiera, nota)] dalla lista 'Global availability'."""
    i = html_.find('class="GlobalCountryList GlobalCountries"')
    j = html_.find("</ul>", i)
    if i < 0 or j < 0:
        raise ValueError("Stripe: lista dei Paesi non trovata")
    out = []
    for li in re.findall(r'<li class="GlobalCountryListItem">(.*?)</li>', html_[i:j], re.S):
        cod = re.search(r'alt="([A-Z]{2})"', li)
        badge = re.search(r'GlobalCountryListItem__badge[^>]*>(.*?)</span>', li, re.S)
        nome = pulito(re.sub(r"(?s)<span.*?</span>", "", re.sub(r"(?s)<img.*?>", "", li)))
        out.append((nome, cod.group(1) if cod else None, pulito(badge.group(1)) if badge else None))
    return out


def impronta(paesi, extra=None):
    s = json.dumps({k: firma(v) for k, v in sorted(paesi.items())}, ensure_ascii=False, sort_keys=True)
    piu = {k: sorted(extra[k]) for k in LISTE_IN_PIU if extra and k in extra}
    if piu:
        s += json.dumps(piu, sort_keys=True)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- servizi
def costruisci(slug, grezzi):
    """Lista del servizio dalla pagina grezza: (paesi, extra)."""
    paesi, regioni, extra = {}, [], {}
    if slug == "starlink":
        paesi, extra = lista_starlink(grezzi["starlink"])
    elif slug in ("apple-music", "apple-tv"):
        for nome, servizi in lista_apple_media(grezzi["apple_media"]).items():
            if slug == "apple-music":
                aggiungi(paesi, regioni, nome, "si" if "Apple Music" in servizi else "no")
            else:
                # "si" solo con la voce "Apple TV subscription" sotto "Apple TV app"; altrimenti "no" con le voci dell'app (es. "Synced videos only")
                tv = servizi.get("Apple TV app")
                if tv is not None and "Apple TV subscription" in tv:
                    aggiungi(paesi, regioni, nome, "si")
                else:
                    aggiungi(paesi, regioni, nome, "no", "; ".join(tv) if tv else None)
                    if iso_di(nome):
                        paesi[iso_di(nome)]["app_tv"] = tv is not None
    elif slug == "apple-pay":
        for nome in lista_apple_pay(grezzi["apple_pay"]):
            aggiungi(paesi, regioni, nome, "si")
    elif slug == "youtube-premium":
        for nome in lista_youtube(grezzi["youtube"]):
            m = re.match(r"^(.*?)\s+-\s+(.*)$", nome)
            if m and "temporarily unavailable" in m.group(2).lower():
                aggiungi(paesi, regioni, m.group(1), "no", m.group(2))  # "Russia - temporarily unavailable"
            elif m:
                aggiungi(paesi, regioni, m.group(1), "si", m.group(2))  # "South Korea - Paid memberships only"
            else:
                aggiungi(paesi, regioni, nome, "si")
    elif slug == "spotify":
        for nome in lista_spotify(grezzi["spotify"]):
            aggiungi(paesi, regioni, nome, "si")  # "Svalbard" vale per SJ (Svalbard e Jan Mayen): il nome della fonte resta in nomi_fonte
    elif slug == "google-wallet":
        # "si" = il Paese è nel menu della pagina ("If your country isn't listed, Google Wallet isn't available in your country yet.") con la
        # spunta verde sulla riga "Google Wallet app"; "no" = nel menu ma con la croce rossa sull'app. Le tre righe (app, tap to pay, sito) restano
        # nella voce come vero/falso. Codice ISO = quello del parametro co= della fonte, controllato con il nome.
        per_paese = json.loads(grezzi["google_wallet_paesi"])
        for cod, nome in menu_google_wallet(grezzi["google_wallet"]):
            if cod not in CODICI:
                raise ValueError(f"Google Wallet: codice {cod} ({nome}) non ISO")
            P = per_paese.get(cod)
            if not P or f"- {nome} -" not in P["titolo"]:
                raise ValueError(f"Google Wallet: pagina di {nome} ({cod}) mancante o di un altro Paese")
            righe = dict(righe_google_wallet(P["tabella"]))
            if set(righe) != set(FUNZIONI_GW) or any(len(x) != 1 or x[0] not in ICONE_GW for x in righe.values()):
                raise ValueError(f"Google Wallet: tabella di {nome} cambiata: {righe}")
            f = {FUNZIONI_GW[k]: ICONE_GW[x[0]] for k, x in righe.items()}
            paesi[cod] = {"stato": "si" if f["app"] else "no", "nomi_fonte": [nome], **f}
        extra["online"] = sorted({c for c in (iso_di(n) for n in lista_google_pay(grezzi["google_pay"])) if c})
    elif slug == "wise":
        # "si" = nella tabella "hold money" (nota = "Additional restrictions"); "no" = tra i Paesi dove Wise non offre i servizi;
        # extra["invio"] = Paesi della lista "countries/regions you can send money to" (il gruppo "Europe" resta in extra["gruppi"]).
        for nome, restr in lista_wise(grezzi["wise"]):
            aggiungi(paesi, regioni, nome, "si", restr or None)
        no, reg_ua = lista_wise_no(grezzi["wise_dove"])
        for nome in no:
            aggiungi(paesi, regioni, nome, "no")
        extra["regioni_non_servite"] = ["Ukraine: " + ", ".join(reg_ua)]
        invio, gruppi = set(), []
        for nome in lista_wise_invio(grezzi["wise_invio"]):
            if nome in GRUPPI_WISE:
                gruppi.append(nome)
            else:
                invio.update(iso_di(x) for x in re.split(r" and (?=Liechtenstein$)", nome))
        extra["invio"], extra["gruppi"] = sorted(invio), gruppi
    elif slug == "uber":
        for nome in lista_uber(grezzi["uber"]):
            aggiungi(paesi, regioni, nome, "si")
    elif slug == "stripe":
        for nome, cod, nota in lista_stripe(grezzi["stripe"]):
            if cod and iso_di(nome) != cod:
                raise ValueError(f"Stripe: {nome} ha la bandiera {cod}")
            aggiungi(paesi, regioni, nome, "si", nota)
    if regioni:
        extra["regioni"] = regioni
    return paesi, extra


GRUPPI_WISE = {"Europe"}  # voce della lista "send to" che non è un Paese (rimanda alla pagina dei trasferimenti in euro)


def leggi_google_wallet(menu):
    """Legge una pagina per ogni Paese del menu Google Wallet (gzip, una richiesta al secondo). Restituisce {codice: {titolo, tabella}}."""
    import gzip
    out = {}
    for n, (cod, nome) in enumerate(menu):
        url = FONTI["google_wallet_paesi"]["url"].format(cod)
        for tentativo in range(4):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9", "Accept": ACCETTA, "Accept-Encoding": "gzip"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    raw = r.read()
                    if r.headers.get("Content-Encoding") == "gzip":
                        raw = gzip.decompress(raw)
                P = tabella_google_wallet(raw.decode("utf-8", "replace"))
                if f"- {nome} -" in P["titolo"]:
                    out[cod] = P
                    break
            except Exception as e:  # si riprova; se manca ancora, costruisci() si ferma
                print(f"  google_wallet {cod}: {e}")
            time.sleep(5 + 10 * tentativo)
        time.sleep(1)
        if n % 50 == 49:
            print(f"  google_wallet: {n + 1}/{len(menu)} pagine Paese")
    return out


def domanda(solo=None):
    """Autocompletamento di Google (client=firefox, hl=en): quali coppie servizio × Paese la gente cerca davvero."""
    famiglie = {"starlink": ["starlink"], "apple-pay": ["apple pay"], "apple-music": ["apple music"], "apple-tv": ["apple tv", "apple tv+"],
                "youtube-premium": ["youtube premium", "youtube music"], "spotify": ["spotify", "spotify premium"],
                "google-wallet": ["google wallet", "google pay"], "wise": ["wise"], "uber": ["uber"], "stripe": ["stripe"]}
    if solo:  # --domanda=slug1,slug2: rilegge solo questi servizi e lascia com'erano le coppie degli altri (le loro pagine restano)
        famiglie = {s: famiglie[s] for s in solo}
    modelli = ["is {} available in", "{} available in", "is {} in", "{} not available in", "does {} work in", "can i use {} in", "is {} available in the"]
    paesi_gl = ["us", "gb", "in", "pk", "ng", "ph", "ca", "au", "ae", "za"]
    out = {s: {} for s in famiglie}
    for s, nomi in famiglie.items():
        for n in nomi:
            for m in modelli:
                q = m.format(n)
                for gl in paesi_gl:
                    url = ("https://suggestqueries.google.com/complete/search?client=firefox&gl=%s&hl=en&q=%s" % (gl, urllib.parse.quote(q + " ")))
                    try:
                        _, _, raw = leggi(url)
                        sugg = json.loads(raw)[1]
                    except Exception as e:  # una richiesta persa non ferma la raccolta
                        print(f"  autocompletamento {gl} {q!r}: {e}")
                        continue
                    for x in sugg:
                        if not x.startswith(q + " "):
                            continue
                        r = chiave(x[len(q):])
                        r = " ".join(w for w in r.split() if not re.fullmatch(r"20\d\d|now|reddit|yet|today", w))
                        c = PER_CHIAVE.get(r)
                        if c:
                            out[s].setdefault(c, [])
                            if x not in out[s][c]:
                                out[s][c].append(x)
                    time.sleep(0.3)
    f_dom = DATI / "servizi_domanda.json"
    prima = json.loads(f_dom.read_text(encoding="utf-8")) if (solo and f_dom.exists()) else {}
    oggi = date.today().isoformat()
    letto = {s: prima.get("letto_il", oggi) for s in prima.get("servizi", {})}
    letto.update(prima.get("letto_il_servizi", {}))
    letto.update({s: oggi for s in out})
    doc = {"_nota": "Ricerche vere (autocompletamento di Google, client=firefox, hl=en) che nominano un Paese: una pagina servizio × Paese "
                    "esiste solo per queste coppie. Riscritto da raccolta/servizi.py --domanda (--domanda=slug,slug rilegge solo quei servizi).",
           "letto_il": oggi, "letto_il_servizi": dict(sorted(letto.items())), "modelli": modelli, "gl": paesi_gl,
           "famiglie": {**prima.get("famiglie", {}), **famiglie},
           "servizi": {**prima.get("servizi", {}), **{s: dict(sorted(v.items())) for s, v in out.items()}}}
    f_dom.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("domanda:", {s: len(v) for s, v in out.items()})


def main():
    oggi = date.today().isoformat()
    CACHE.mkdir(parents=True, exist_ok=True)
    f_dati = DATI / "servizi.json"
    prima = json.loads(f_dati.read_text(encoding="utf-8")) if f_dati.exists() else {"servizi": []}
    prima_per = {s["slug"]: s for s in prima["servizi"]}
    grezzi, letture, problemi = {}, {}, []
    for k, F in FONTI.items():
        if F.get("derivata"):
            continue
        # Spotify a volte risponde 200 con una pagina d'errore ("This page got tripped up"): si riprova finché c'è il segno atteso
        segno = SEGNI.get(k)
        raw = None
        for tentativo in range(4):
            try:
                stato, finale, raw = leggi(F["url"])
            except Exception as e:
                errore = e
                raw = None
            if raw is not None and (not segno or segno in testo(raw)):
                break
            time.sleep(5 + 10 * tentativo)
        if raw is None:
            problemi.append(f"{k}: lettura fallita ({errore})")
            continue
        (CACHE / f"{k}.{F['tipo']}").write_text(raw, encoding="utf-8")
        letture[k] = {"url": F["url"], "url_finale": finale, "http": stato, "byte": len(raw.encode("utf-8")),
                      "data_fonte": data_pubblicazione(raw) if "apple" in k else None}
        grezzi[k] = raw
        print(f"  {k}: HTTP {stato}, {letture[k]['byte']} byte" + (f", pubblicata il {letture[k]['data_fonte']}" if letture[k]["data_fonte"] else ""))
        if stato != 200:
            problemi.append(f"{k}: HTTP {stato}")
    if "google_wallet" in grezzi:
        try:
            pp = leggi_google_wallet(menu_google_wallet(grezzi["google_wallet"]))
        except ValueError as e:
            problemi.append(str(e))
            pp = {}
        grezzi["google_wallet_paesi"] = json.dumps(pp, ensure_ascii=False, indent=0, sort_keys=True)
        (CACHE / "google_wallet_paesi.json").write_text(grezzi["google_wallet_paesi"], encoding="utf-8")
        letture["google_wallet_paesi"] = {"url": FONTI["google_wallet_paesi"]["url"], "pagine": len(pp), "data_fonte": None}
    frasi = {}
    for k, (fonte, frase) in FRASI.items():
        if fonte not in grezzi:
            continue
        if frase not in testo(grezzi[fonte]):
            problemi.append(f"frase {k} non trovata in {fonte}: {frase!r}")
        frasi[k] = {"fonte": fonte, "url": FONTI[fonte]["url"], "frase": frase}
    servizi, cambi = [], []
    for S in SERVIZI:
        if S["fonte"] not in grezzi:
            problemi.append(f"{S['slug']}: fonte non letta")
            continue
        try:
            paesi, extra = costruisci(S["slug"], grezzi)
        except ValueError as e:
            problemi.append(f"{S['slug']}: {e}")
            continue
        si = sum(1 for v in paesi.values() if v["stato"] == "si")
        imp = impronta(paesi, extra)
        P = prima_per.get(S["slug"])
        if P:
            si_prima = sum(1 for v in P["paesi"].values() if v["stato"] == "si")
            if si < 0.8 * si_prima:
                problemi.append(f"{S['slug']}: {si} Paesi con il servizio contro {si_prima} della lettura precedente (oltre il 20 % in meno)")
        cambiato = P["cambiato_il"] if P and P["impronta"] == imp else oggi
        if P and P["impronta"] != imp:
            vecchi, nuovi = P["paesi"], paesi
            diff = [{"iso2": c, "prima": vecchi.get(c, {}).get("stato"), "dopo": nuovi.get(c, {}).get("stato"),
                     "nota_prima": vecchi.get(c, {}).get("nota"), "nota_dopo": nuovi.get(c, {}).get("nota")}
                    for c in sorted(set(vecchi) | set(nuovi))
                    if (firma(vecchi[c]) if c in vecchi else None) != (firma(nuovi[c]) if c in nuovi else None)]
            for k in LISTE_IN_PIU:  # liste in più (Google Pay online, Wise invio)
                a, b = set(P.get("extra", {}).get(k, [])), set(extra.get(k, []))
                if a != b:
                    diff.append({"lista": k, "tolti": sorted(a - b), "aggiunti": sorted(b - a)})
            cambi.append({"data": oggi, "servizio": S["slug"], "differenze": diff})
            print(f"  CAMBIATA la lista {S['slug']}: {len(diff)} Paesi")
        servizi.append({**S, "url_fonte": FONTI[S["fonte"]]["url"], "letto_il": oggi, "cambiato_il": cambiato,
                        "data_fonte": letture[S["fonte"]]["data_fonte"], "http": letture[S["fonte"]]["http"],
                        "impronta": imp, "conteggi": {st: sum(1 for v in paesi.values() if v["stato"] == st) for st in ("si", "no", "in_arrivo", "per_regione")},
                        "paesi": dict(sorted(paesi.items())), **({"extra": extra} if extra else {})})
        print(f"  {S['slug']}: {si} sì, {len(paesi) - si} altri stati, impronta {imp[:12]}")
    if problemi:
        print("NON SCRITTO dati/servizi.json. Da controllare a mano:\n  " + "\n  ".join(problemi))
        sys.exit(1)
    doc = {"_nota": "Liste ufficiali dei Paesi dei servizi digitali, lette da raccolta/servizi.py. stato: si = nella lista con il servizio; "
                    "no = la fonte nomina il Paese ma senza il servizio (motivo in 'nota'); in_arrivo = Starlink 'Coming soon'; per_regione = Starlink a livello di regione ('exclude'). "
                    "Paesi assenti = non nominati dalla fonte (mai 'vietato'). Codici ISO 3166-1 alfa-2 (dati/paesi_iso.json).",
           "letto_il": oggi, "letture": letture, "frasi": frasi, "servizi": servizi}
    f_dati.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    if cambi:
        f_c = DATI / "servizi_cambi.json"
        storico = json.loads(f_c.read_text(encoding="utf-8")) if f_c.exists() else {"cambi": []}
        storico["cambi"] = cambi + storico["cambi"]
        f_c.write_text(json.dumps(storico, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Scritto {f_dati.relative_to(RADICE.parent)}: {len(servizi)} servizi.")


if __name__ == "__main__":
    for a in sys.argv[1:]:
        if a == "--domanda":
            domanda()
        elif a.startswith("--domanda="):
            domanda(a.split("=", 1)[1].split(","))
    main()
