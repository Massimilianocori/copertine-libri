"""Pagine delle sezioni /uk/ (ucraino) e /ro/ (rumeno) di EsameB1: testi tradotti dalle pagine italiane (e dalla versione
inglese già revisionata), cifre e date lette dai file dati. Struttura, lingue e controlli in genera_lingue.py.
Glossario fisso: le parole che il lettore trova sui moduli restano in italiano tra parentesi (Prefettura, Questura,
permesso di soggiorno, carta di soggiorno, kit postale, marca da bollo, patronato, CILS, CELI…)."""
import json
from decimal import Decimal
from html import escape

import genera_en as EN
import genera_lingue as LG
from genera_lingue import a, data, eur, eur_c, fonte, fonti_parola, num, pl_uk, pl_ro, iso_it, giorno_mese


def H(lg):
    return lg == "uk"


# ---------------------------------------------------------------- hub
def hub(G, lg, prossime):
    uk = H(lg)
    F = LG.fatti(G)
    R = G.REDDITI["cittadinanza"]
    p = prossime[0]
    v_sess = max(s["verificato_il"] for s in G.sessioni)
    ue, extra = LG.anni_residenza()
    if uk:
        P = LG.protezione()
        faq = [
            ("Який іспит з італійської потрібен для громадянства?",
             "Потрібен сертифікат з італійської мови рівня B1 або вищого від визнаної установи. Чотири основні установи з центрами по всій Італії: "
             "CILS (Університет для іноземців Сієни), CELI (Університет для іноземців Перуджі), PLIDA (Товариство Данте Аліґ’єрі) і CERT.IT (Університет Рим Тре). "
             "Vademecum Міністерства внутрішніх справ називає також Університет для іноземців «Dante Alighieri» у Реджо-Калабрії. "
             '<a href="zvilnennia-vid-ispytu/">Хто звільнений</a>.'),
            ("Чи можна скласти іспит B1 онлайн?",
             'Ні. Іспит складають особисто в екзаменаційному центрі, з документом, що посвідчує особу. <a href="ispyt-b1-dlia-hromadianstva/#online">Офіційні джерела</a>.'),
            ("Скільки коштує іспит B1?",
             f"CILS B1 Cittadinanza — {eur(lg, F['cils'], False)}, однаково всюди. CERT.IT B1 — {eur(lg, F['certit'], False)} в Університеті Рим Тре. "
             f"CELI і PLIDA: ціну встановлює кожен центр (наприклад, {eur(lg, F['celi_tot'], False)} за CELI 2 i cittadinanza в Міланському університеті). "
             '<a href="vartist-ispytu-b1/">Усі ціни з джерелами</a>.'),
            ("Який мінімальний дохід потрібен для громадянства Італії?",
             f"Для громадянства за проживанням — щонайменше {eur(lg, R['solo'])} оподатковуваного доходу на рік, якщо ви самі, {eur(lg, R['con_coniuge'])} з дружиною або чоловіком на утриманні "
             f'і ще {eur(lg, R["per_figlio"])} за кожну дитину на утриманні. <a href="dokhid-dlia-hromadianstva/">Таблиця і калькулятор</a>.'),
            ("До якої дати можна продовжити тимчасовий захист в Італії?",
             f"За даними Квестур Риму та Удіне (сторінку Риму оновлено {data(lg, P['roma_agg'])}), дозволи на проживання з тимчасовим захистом можна на ваш запит продовжити до {data(lg, P['fino'])}: "
             f"Квестури посилаються на декрет-закон № {P['dl']}, а в ЄС тимчасовий захист продовжено до цієї дати рішенням Ради ЄС {P['ue_dec']}. "
             f"У липні {P['im_anno']} Рада ЄС продовжила захист ще на рік, до {data(lg, P['im_fino'])} (урядовий портал Integrazione Migranti); Квестура Ареццо (сторінку оновлено {data(lg, P['arezzo_agg'])}) уже пише цю дату, "
             f'інші прочитані Квестури — ще {data(lg, P["fino"])}. Яка дата діє для вас, вирішує ваша Квестура. <a href="tymchasovyi-zakhyst/">Продовження, конвертація і перевірка дозволу</a>.'),
        ]
        h1 = "Громадянство Італії та іспит B1: посібники українською"
        lead = (f"За офіційними календарями CILS, CELI, PLIDA і CERT.IT (перевірено {data(lg, v_sess)}), найближчий іспит B1 в Італії — {data(lg, p['data'])} ({p['ente']}). "
                "Ці посібники українською пояснюють іспит, дохід для громадянства, заяву, carta di soggiorno і тимчасовий захист — на основі тих самих офіційних даних, що й наші сторінки італійською.")
        occh = "CILS · CELI · PLIDA · CERT.IT · українською"
        cifre = (f'<li>{G.ic("edificio")}<span><strong>{len(G.sedi)}</strong> {pl_uk(len(G.sedi), "екзаменаційний центр", "екзаменаційні центри", "екзаменаційних центрів")} в Італії</span></li>'
                 f'<li>{G.ic("cal")}<span><strong>{len(prossime)}</strong> {pl_uk(len(prossime), "запланована сесія", "заплановані сесії", "запланованих сесій")}</span></li>'
                 f'<li>{G.ic("doc")}<span>дані з офіційних джерел</span></li>')
        chi = "Префектура (громадянство) або Квестура (дозволи на проживання)"
        t_date, t_guide, t_tab = "Усі дати іспитів", "Посібники українською", "Найближча дата для кожної установи"
        nota_tab = (f"Кожен центр може встановити термін, раніший за національний. <strong>Перед реєстрацією завжди уточнюйте в центрі.</strong> "
                    f'<a href="daty-ispytu-b1/">Усі {len(prossime)} дат</a>.')
        sedi = ('Екзаменаційні центри за містами є лише італійською: <a href="../#citta" hreflang="it" lang="it">sedi per città</a> (адреси, телефони, сайти). '
                f'Правила звільнення від іспиту прочитано {data(lg, G.esoneri["verificato_il"])}.')
        titolo = G.titolo_pagina(f"Громадянство Італії та іспит B1: посібники українською",
                                 "Громадянство Італії та іспит B1 українською")
        descr = G.descrizione_pagina(
            f"Іспит B1 для громадянства Італії: найближча дата {data(lg, p['data'])} ({p['ente']}), вартість, дохід, заява, carta di soggiorno, тимчасовий захист.")
    else:
        faq = [
            ("Ce examen de limba italiană trebuie pentru cetățenie?",
             "Trebuie un certificat de limba italiană de nivel B1 sau superior, eliberat de o instituție recunoscută. Cele 4 instituții principale, cu centre în toată Italia, sunt "
             "CILS (Universitatea pentru Străini din Siena), CELI (Universitatea pentru Străini din Perugia), PLIDA (Societatea Dante Alighieri) și CERT.IT (Universitatea Roma Tre). "
             "Vademecum-ul Ministerului de Interne mai numește Universitatea pentru Străini «Dante Alighieri» din Reggio Calabria. "
             '<a href="scutire-test-italiana/">Cine este scutit</a>.'),
            ("Cetățenii români au nevoie de examenul B1?",
             "Da. Potrivit Vademecum-ului Ministerului de Interne, cetățenii Uniunii Europene trebuie să prezinte certificatul B1 (sau un titlu de studii în limba italiană): "
             'scutirea pentru carta di soggiorno UE pe termen lung nu îi privește. <a href="scutire-test-italiana/">Scutiri, cu sursele</a>.'),
            ("După câți ani pot cere cetățenia italiană?",
             f"Potrivit art. 9 din Legea 91/1992 (pagina Ministerului de Interne), un cetățean al unui stat membru UE poate cere cetățenia după cel puțin {ue} ani de rezidență legală în Italia; "
             f'un străin din afara UE, de exemplu din Republica Moldova, după cel puțin {extra} ani. Decide Prefectura. <a href="cetatenie-italiana/">Cererea, pas cu pas</a>.'),
            ("Cât costă examenul B1?",
             f"CILS B1 Cittadinanza: {eur(lg, F['cils'], False)}, aceeași taxă peste tot. CERT.IT B1: {eur(lg, F['certit'], False)} la Universitatea Roma Tre. "
             f"CELI și PLIDA: prețul îl stabilește fiecare centru (de exemplu {eur(lg, F['celi_tot'], False)} pentru CELI 2 i cittadinanza la Universitatea din Milano). "
             '<a href="cost-examen-b1/">Toate prețurile, cu surse</a>.'),
            ("Ce venit trebuie pentru cetățenia italiană?",
             f"Pentru cetățenia prin rezidență: cel puțin {eur(lg, R['solo'])} venit impozabil pe an dacă sunteți singur(ă), {eur(lg, R['con_coniuge'])} cu soțul sau soția în întreținere, "
             f'plus {eur(lg, R["per_figlio"])} pentru fiecare copil în întreținere. <a href="venit-minim-cetatenie/">Tabel și calculator</a>.'),
        ]
        h1 = "Cetățenia italiană și examenul B1: ghiduri în limba română"
        lead = (f"Potrivit calendarelor oficiale CILS, CELI, PLIDA și CERT.IT (verificate la {data(lg, v_sess)}), următorul examen B1 din Italia are loc pe {data(lg, p['data'])} ({p['ente']}). "
                "Aceste ghiduri în limba română explică examenul, venitul minim, cererea de cetățenie și rezidența în Italia, pe baza acelorași date oficiale ca paginile noastre în italiană.")
        occh = "CILS · CELI · PLIDA · CERT.IT · în română"
        cifre = (f'<li>{G.ic("edificio")}<span><strong>{len(G.sedi)}</strong> {pl_ro(len(G.sedi), "centru", "centre")} de examen în Italia</span></li>'
                 f'<li>{G.ic("cal")}<span><strong>{len(prossime)}</strong> {pl_ro(len(prossime), "sesiune programată", "sesiuni programate")}</span></li>'
                 f'<li>{G.ic("doc")}<span>date din surse oficiale</span></li>')
        chi = "Prefectura (cetățenia) sau Chestura (permisele de ședere)"
        t_date, t_guide, t_tab = "Toate datele de examen", "Ghiduri în română", "Următoarea dată pentru fiecare instituție"
        nota_tab = (f"Fiecare centru poate stabili un termen mai devreme decât cel național. <strong>Întrebați întotdeauna centrul înainte de înscriere.</strong> "
                    f'<a href="date-examen-b1/">Toate cele {len(prossime)} {pl_ro(len(prossime), "dată", "date")}</a>.')
        sedi = ('Centrele de examen pe orașe sunt doar în italiană: <a href="../#citta" hreflang="it" lang="it">sedi per città</a> (adrese, telefoane, site-uri). '
                f'Regulile privind scutirea au fost citite la {data(lg, G.esoneri["verificato_il"])}.')
        titolo = G.titolo_pagina("Cetățenie italiană și examenul B1: ghiduri în română",
                                 "Cetățenie italiană și examen B1 în română")
        descr = G.descrizione_pagina(
            f"Examenul B1 pentru cetățenia italiană: următoarea dată {data(lg, p['data'])} ({p['ente']}), cost, venit minim, cererea și rezidența pentru români.")
    faq_html, ld = LG.faq_blocco(G, faq)
    pd = LG.GUIDE[lg][0][0]
    corpo = f"""<section class="hero">
<span class="occhiello">{G.ic("scudo")}{occh}</span>
<h1>{h1}</h1>
<p class="lead">{lead}</p>
{LG.risposta(G, lg, prossime, "", pd)}
<div class="azioni"><a class="btn" href="{pd}">{G.ic("cal")}{t_date}</a><a class="btn btn-2" href="#guides">{G.ic("lista")}{t_guide}</a></div>
<ul class="cifre">{cifre}</ul>
</section>
{LG.decide(G, lg, chi)}
<div class="due">
<section id="dates">
<h2>{G.ic("cal")}{t_tab}</h2>
{tabella_prossime(G, lg, prossime)}
<p class="small">{nota_tab}</p>
</section>
<aside>{LG.modulo(G, lg, "../")}</aside>
</div>
<section id="guides">
<h2>{G.ic("lista")}{t_guide}</h2>
{LG.griglia_guide(G, lg, "")}
<p class="small">{sedi}</p>
</section>
{LG.faq_sezione(G, lg, faq_html)}
{LG.altre_lingue(G, lg, f"{lg}/", "../")}"""
    LG.pagina_l(G, lg, f"{lg}/", titolo, descr, corpo, jsonld=ld)


def tabella_prossime(G, lg, prossime):
    uk = H(lg)
    righe = []
    for e in G.ENTE:
        s = next((x for x in prossime if x["ente"] == e), None)
        sc = next((x for x in prossime if x["ente"] == e and x.get("scadenza") and LG.d(x["scadenza"]) >= G.OGGI), None)
        prima = (f'<time datetime="{s["data"]}">{data(lg, s["data"])}</time><br><span class="small">{escape(LG.esame(lg, s["esami"][0]))}</span>' if s
                 else ("нової дати ще немає" if uk else "nicio dată nouă publicată"))
        if sc:
            scad = (f'до {data(lg, sc["scadenza"])}<br><span class="small">для іспиту {giorno_mese(lg, sc["data"])}</span>' if uk
                    else f'până la {data(lg, sc["scadenza"])}<br><span class="small">pentru examenul din {giorno_mese(lg, sc["data"])}</span>')
        elif e in ("PLIDA", "CERT.IT"):
            scad = "встановлює кожен центр" if uk else "îl stabilește fiecare centru"
        else:
            scad = "немає відкритого національного терміну" if uk else "niciun termen național deschis"
        righe.append(f'<tr><td>{G.eb(e)}<br><span class="small">{escape(LG.NOME_ENTE[lg][e])}</span></td>'
                     f'<td data-l="{"Найближчий іспит" if uk else "Următorul examen"}">{prima}</td><td data-l="{"Реєстрація до" if uk else "Înscriere până la"}">{scad}</td></tr>')
    th = ("Установа", "Найближчий іспит", "Національний термін") if uk else ("Instituția", "Următorul examen", "Termen național")
    return (f'<div class="tab-wrap rc-tab"><table class="conf"><thead><tr><th scope="col">{th[0]}</th><th scope="col">{th[1]}</th>'
            f'<th scope="col">{th[2]}</th></tr></thead><tbody>{"".join(righe)}</tbody></table></div>')


# ---------------------------------------------------------------- date
def pagina_date(G, lg, prossime):
    uk = H(lg)
    v = max(s["verificato_il"] for s in G.sessioni)
    p = prossime[0]
    perc = f"{lg}/{LG.GUIDE[lg][0][0]}"
    if uk:
        h1 = f"Дати іспиту B1 для громадянства Італії {G.anni(prossime)}"
        lead = (f"За офіційними календарями чотирьох екзаменаційних установ (перевірено {data(lg, v)}), в Італії заплановано {len(prossime)} "
                f"{pl_uk(len(prossime), 'сесію', 'сесії', 'сесій')} іспиту B1, перша — {data(lg, p['data'])} ({p['ente']}). "
                "Дати іспитів національні: усі центри однієї установи проводять іспит того самого дня, але кожен центр може закрити реєстрацію раніше.")
        av = ("Кожен центр може мати термін, раніший за національний. <strong>Перед реєстрацією завжди перепитайте в центрі.</strong> "
              "Для вашої заяви на громадянство рішення ухвалює Префектура.")
        h2a, h2b = "Усі найближчі дати", "Перед реєстрацією"
        prima_reg = ("«Іспит для громадянства» позначає іспити B1, створені спеціально для заяви на громадянство (CILS B1 Cittadinanza, CELI 2 i cittadinanza). "
                     "Загальні іспити B1 (CILS B1 standard, CELI 2, PLIDA B1, CERT.IT B1) — теж сертифікати рівня B1. "
                     'Реєструються в екзаменаційному центрі, не на цьому сайті: <a href="../../#citta" hreflang="it" lang="it">знайдіть центр у своєму місті (італійською)</a>.')
        titolo = G.titolo_pagina(f"Дати іспиту B1 в Італії {G.anni(prossime)}: CILS, CELI, PLIDA, CERT.IT", f"Дати іспиту B1 в Італії {G.anni(prossime)}")
        descr = G.descrizione_pagina(f"Усі {len(prossime)} сесій іспиту B1 в Італії для громадянства від {data(lg, p['data'])}: дати CILS, CELI, PLIDA, CERT.IT і терміни реєстрації.")
        bric = "Дати іспиту B1"
    else:
        h1 = f"Datele examenului B1 pentru cetățenia italiană {G.anni(prossime)}"
        lead = (f"Potrivit calendarelor oficiale ale celor patru instituții de examinare (verificate la {data(lg, v)}), în Italia sunt programate {len(prossime)} "
                f"{pl_ro(len(prossime), 'sesiune', 'sesiuni')} ale examenului B1, prima pe {data(lg, p['data'])} ({p['ente']}). "
                "Datele sunt naționale: toate centrele aceleiași instituții țin examenul în aceeași zi, dar fiecare centru poate închide înscrierile mai devreme.")
        av = ("Fiecare centru poate avea un termen mai devreme decât cel național. <strong>Înainte de înscriere cereți întotdeauna confirmare centrului.</strong> "
              "Pentru cererea de cetățenie decide Prefectura.")
        h2a, h2b = "Toate datele următoare", "Înainte de înscriere"
        prima_reg = ("«Examen pentru cetățenie» marchează examenele B1 create pentru cererea de cetățenie (CILS B1 Cittadinanza, CELI 2 i cittadinanza). "
                     "Examenele B1 generale (CILS B1 standard, CELI 2, PLIDA B1, CERT.IT B1) sunt și ele certificate B1. "
                     'Vă înscrieți la centrul de examen, nu pe acest site: <a href="../../#citta" hreflang="it" lang="it">găsiți un centru în orașul dumneavoastră (în italiană)</a>.')
        titolo = G.titolo_pagina(f"Date examen B1 în Italia {G.anni(prossime)}: CILS, CELI, PLIDA, CERT.IT", f"Date examen B1 în Italia {G.anni(prossime)}")
        descr = G.descrizione_pagina(f"Toate cele {len(prossime)} sesiuni ale examenului B1 pentru cetățenie din {data(lg, p['data'])}: date CILS, CELI, PLIDA, CERT.IT și termene.")
        bric = "Date examen B1"
    corpo = f"""<section class="hero">
{LG.briciole(lg, "../", (bric, None))}
<h1>{h1}</h1>
<p class="lead">{lead}</p>
{LG.risposta(G, lg, prossime, "../", LG.GUIDE[lg][0][0])}
</section>
{G.avviso(av)}
<div class="due">
<section id="dates">
<h2>{G.ic("cal")}{h2a}</h2>
{LG.lista_sessioni(G, lg, prossime)}
</section>
<aside>{LG.modulo(G, lg, "../../")}</aside>
</div>
<section>
<h2>{G.ic("info")}{h2b}</h2>
<p>{prima_reg}</p>
{LG.griglia_guide(G, lg, "../", salta=LG.GUIDE[lg][0][0])}
</section>
{LG.altre_lingue(G, lg, perc, "../../", [f'<a href="../../#date" hreflang="it" lang="it">Italiano</a>'])}"""
    LG.pagina_l(G, lg, perc, titolo, descr, corpo)


# ---------------------------------------------------------------- esame
def tabella_durata(G, lg):
    uk = H(lg)
    righe = []
    for e in G.enti:
        p = e["fatti"]["durata"]["prove"]
        pp = "<br>".join(f'{LG.parti(lg, q["prove"])}: {LG.tempo(lg, q["tempo"])}' for q in p["parti"])
        righe.append(f'<tr><td>{G.eb(e["sigla"])}</td><td data-l="{"Частини" if uk else "Probe"}">{pp}</td>'
                     f'<td data-l="{"Загалом" if uk else "În total"}"><strong>{LG.totale(lg, p["totale"])}</strong></td></tr>')
    v = max(e["fatti"]["durata"]["verificato_il"] for e in G.enti)
    fonti_ = " · ".join(a(f["url"], f["nome"]) for e in G.enti for f in e["fatti"]["durata"]["fonti"][:1])
    th = ("Іспит", "Частини і час", "Загалом") if uk else ("Examen", "Probe și timp", "În total")
    return (f'<div class="tab-wrap rc-tab"><table class="conf"><thead><tr><th scope="col">{th[0]}</th><th scope="col">{th[1]}</th><th scope="col">{th[2]}</th></tr></thead>'
            f'<tbody>{"".join(righe)}</tbody></table></div>{fonte(G, lg, fonti_, v, fonti_parola(lg, 2))}')


def pagina_esame(G, lg, prossime):
    uk = H(lg)
    F = LG.fatti(G)
    Fe = G.esoneri["fonti"]
    v = G.esoneri["verificato_il"]
    p = prossime[0]
    perc = f"{lg}/{LG.GUIDE[lg][1][0]}"
    pd = LG.GUIDE[lg][0][0]
    nomi_esame = {"CILS": "CILS B1 Cittadinanza (також CILS B1 standard)" if uk else "CILS B1 Cittadinanza (și CILS B1 standard)",
                  "CELI": "CELI 2 i cittadinanza, лише в Італії (також CELI 2)" if uk else "CELI 2 i cittadinanza, doar în Italia (și CELI 2)",
                  "PLIDA": "PLIDA B1", "CERT.IT": LG.esame(lg, "CERT.IT B1 (sessione A2/B1)")}
    righe = "".join(
        f'<tr><td>{G.eb(e["sigla"])}<br><span class="small">{escape(LG.NOME_ENTE[lg][e["sigla"]])}</span></td>'
        f'<td data-l="{"Іспит для громадянства" if uk else "Examen pentru cetățenie"}">{escape(nomi_esame[e["sigla"]])}</td>'
        f'<td data-l="{"Центри в Італії" if uk else "Centre în Italia"}">{sum(1 for s in G.sedi if s["ente"] == e["sigla"])}</td>'
        f'<td data-l="{"Сайт" if uk else "Site"}">{a(e["sito"], "офіційний сайт" if uk else "site oficial")}</td></tr>' for e in G.enti)
    online = EN.online_fonti(G)
    fonti_legge = a(Fe["legge91"]["url"], Fe["legge91"]["nome"]) + " · " + a(Fe["vademecum"]["url"], Fe["vademecum"]["nome"])
    if uk:
        faq = [
            ("Хто має складати іспит B1 з італійської?",
             "Ті, хто подає заяву на громадянство Італії за проживанням або через шлюб, якщо вони не звільнені (наприклад, власники дозволу ЄС для довгострокових резидентів). "
             "Замість сертифіката можна подати документ про освіту, здобуту італійською мовою. Рішення ухвалює Префектура."),
            ("Що легше: CILS чи CELI?",
             "Ми не складаємо рейтингів. Іспити різняться тривалістю, структурою і ціною: порівняйте частини в таблиці на цій сторінці та зразки кожної установи."),
            ("Чи можна скласти іспит онлайн?", "Ні. Усі чотири установи проводять іспит особисто в екзаменаційному центрі."),
            ("Чи має сертифікат B1 термін дії?",
             "Сертифікати CELI і CILS не мають терміну дії, за їхніми офіційними сторінками. Для вашої заяви рішення про те, який сертифікат дійсний, ухвалює Префектура."),
        ]
        h1 = "Іспит B1 з італійської для громадянства: що це, вартість і звільнення"
        lead = (f"Згідно зі ст. 9.1 Закону 91/1992 і Міністерством внутрішніх справ (джерела прочитано {data(lg, v)}), хто подає заяву на громадянство Італії за проживанням або через шлюб, "
                "має довести знання італійської на рівні B1 або вище — сертифікатом визнаної установи або документом про освіту. Нижче — як працює іспит, простими словами.")
        s1 = ("Хто має складати іспит і хто звільнений", f'Вимога B1 стосується громадянства <strong>за проживанням</strong> і <strong>через шлюб</strong>. За законом і роз’ясненнями Міністерства, сертифікат не потрібен, якщо ви підписали угоду про інтеграцію '
              "(accordo di integrazione), якщо маєте <strong>дозвіл ЄС для довгострокових резидентів</strong> (carta di soggiorno) або якщо у вас серйозні труднощі з вивченням мови, підтверджені державною медичною установою. "
              f'Документ про освіту, здобуту італійською, може замінити сертифікат. <a href="../{LG.GUIDE[lg][4][0]}">Усі випадки звільнення з джерелами</a>.')
        s2 = "4 основні екзаменаційні установи"
        th = ("Установа", "Іспит для громадянства", "Центри в Італії", "Сайт")
        quinto = (f"Vademecum Міністерства внутрішніх справ (2025) називає також п’яту установу — Університет для іноземців «Dante Alighieri» у Реджо-Калабрії. Дійсний будь-який сертифікат B1 або вище від визнаної установи; "
                  f'найближчий іспит — {data(lg, p["data"])} ({p["ente"]}): <a href="../{pd}">усі дати</a>.')
        s3 = "Як зареєструватися"
        passi = [f'Оберіть дату в <a href="../{pd}">календарі іспитів</a>.',
                 'Оберіть екзаменаційний центр у своєму місті: <a href="../../#citta" hreflang="it" lang="it">центри за містами</a> (список італійською, з адресами й контактами).',
                 "Зв’яжіться з центром: там скажуть ціну, потрібні документи й останній день реєстрації. Деякі центри закривають реєстрацію раніше за національний термін.",
                 "Сплатіть і збережіть квитанцію. У день іспиту візьміть дійсний документ, що посвідчує особу."]
        s4, s4p = "Скільки триває іспит", "Спочатку письмова частина (аудіювання, читання, письмо), потім коротка усна частина з екзаменатором, зазвичай того самого дня."
        s5 = "Чи можна скласти іспит онлайн?"
        s5p = ("<strong>Ні.</strong> Іспит складають особисто в екзаменаційному центрі: PLIDA пише це в офіційних FAQ, CILS і CELI просять прийти з документом, а усна частина CERT.IT — очна. "
               "У Римі Тре письмову частину CERT.IT B1 виконують на комп’ютері, але завжди в центрі.")
        s6 = "Вартість і зразки"
        s6p = (f"CILS B1 Cittadinanza коштує {eur(lg, F['cils'], False)} всюди; CERT.IT B1 — {eur(lg, F['certit'], False)} в Університеті Рим Тре; для CELI і PLIDA ціну встановлює кожен центр. "
               f'<a href="../{LG.GUIDE[lg][2][0]}">Усі ціни</a> · <a href="../{LG.GUIDE[lg][3][0]}">Безкоштовні офіційні зразки</a> · '
               '<a href="../../risultati/" hreflang="it" lang="it">коли приходять результати (італійською)</a>.')
        titolo = G.titolo_pagina("Іспит B1 з італійської для громадянства: вартість, звільнення", "Іспит B1 з італійської для громадянства")
        descr = G.descrizione_pagina(f"Іспит B1 для громадянства Італії українською: 4 установи, частини, тривалість, вартість (CILS {eur(lg, F['cils'], False)}) і хто звільнений.")
        bric = "Іспит B1"
    else:
        faq = [
            ("Cine trebuie să dea examenul B1 de limba italiană?",
             "Cei care cer cetățenia italiană prin rezidență sau prin căsătorie, dacă nu sunt scutiți (de exemplu titularii permisului UE pe termen lung, situație care nu privește cetățenii români). "
             "În locul certificatului se poate prezenta un titlu de studii obținut în limba italiană. Decide Prefectura."),
            ("Ce e mai ușor: CILS sau CELI?",
             "Nu facem clasamente. Examenele diferă ca durată, structură și preț: comparați probele din tabelul de pe această pagină și modelele fiecărei instituții."),
            ("Pot da examenul online?", "Nu. Toate cele patru instituții țin examenul cu prezență fizică, la un centru de examen."),
            ("Certificatul B1 expiră?",
             "Certificatele CELI și CILS nu au dată de expirare, potrivit paginilor lor oficiale. Pentru cererea dumneavoastră, Prefectura decide ce certificat este valabil."),
        ]
        h1 = "Examenul B1 de limba italiană pentru cetățenie: ce este, cost și scutiri"
        lead = (f"Potrivit art. 9.1 din Legea 91/1992 și Ministerului de Interne (surse citite la {data(lg, v)}), cine cere cetățenia italiană prin rezidență sau prin căsătorie "
                "trebuie să dovedească cunoașterea limbii italiene la nivel B1 sau superior, cu un certificat de la o instituție recunoscută sau cu un titlu de studii. Iată cum funcționează examenul, pe înțelesul tuturor.")
        s1 = ("Cine trebuie să dea examenul și cine este scutit", "Cerința B1 se aplică cetățeniei <strong>prin rezidență</strong> și <strong>prin căsătorie</strong>, inclusiv pentru <strong>cetățenii români și ceilalți cetățeni UE</strong>. "
              "Potrivit legii și Ministerului, nu trebuie certificatul cine a semnat acordul de integrare (accordo di integrazione), cine are <strong>permisul UE pe termen lung</strong> (carta di soggiorno, pentru cetățenii din afara UE) "
              "sau cine are dificultăți grave de învățare a limbii, certificate de o unitate sanitară publică. "
              f'Un titlu de studii obținut în limba italiană poate înlocui certificatul. <a href="../{LG.GUIDE[lg][4][0]}">Toate scutirile, cu surse</a>.')
        s2 = "Cele 4 instituții principale"
        th = ("Instituția", "Examen pentru cetățenie", "Centre în Italia", "Site")
        quinto = (f"Vademecum-ul Ministerului de Interne (2025) mai numește o a cincea instituție, Universitatea pentru Străini «Dante Alighieri» din Reggio Calabria. Este valabil orice certificat B1 sau superior de la o instituție recunoscută; "
                  f'următorul examen are loc pe {data(lg, p["data"])} ({p["ente"]}): <a href="../{pd}">toate datele</a>.')
        s3 = "Cum vă înscrieți"
        passi = [f'Alegeți o dată din <a href="../{pd}">calendarul examenelor</a>.',
                 'Alegeți un centru de examen în orașul dumneavoastră: <a href="../../#citta" hreflang="it" lang="it">centre pe orașe</a> (listă în italiană, cu adrese și contacte).',
                 "Contactați centrul: vă spune prețul, actele necesare și ultima zi de înscriere. Unele centre închid înscrierile înainte de termenul național.",
                 "Plătiți și păstrați chitanța. În ziua examenului aduceți un act de identitate valabil."]
        s4, s4p = "Cât durează examenul", "Mai întâi partea scrisă (ascultare, citire, scriere), apoi o probă orală scurtă cu un examinator, de obicei în aceeași zi."
        s5 = "Se poate da examenul online?"
        s5p = ("<strong>Nu.</strong> Examenul se dă cu prezență fizică, la un centru de examen: PLIDA o spune în FAQ-ul oficial, CILS și CELI cer să veniți cu un act de identitate, iar proba orală CERT.IT este cu prezență fizică. "
               "La Roma Tre partea scrisă CERT.IT B1 se face pe calculator, dar tot la centru.")
        s6 = "Cost și modele"
        s6p = (f"CILS B1 Cittadinanza costă {eur(lg, F['cils'], False)} peste tot; CERT.IT B1 costă {eur(lg, F['certit'], False)} la Roma Tre; pentru CELI și PLIDA prețul îl stabilește fiecare centru. "
               f'<a href="../{LG.GUIDE[lg][2][0]}">Toate prețurile</a> · <a href="../{LG.GUIDE[lg][3][0]}">Modele oficiale gratuite</a> · '
               '<a href="../../risultati/" hreflang="it" lang="it">când apar rezultatele (în italiană)</a>.')
        titolo = G.titolo_pagina("Examen B1 de italiană pentru cetățenie: cost și scutiri", "Examen B1 de italiană pentru cetățenie")
        descr = G.descrizione_pagina(f"Examenul B1 pentru cetățenia italiană în română: 4 instituții, probe, durată, cost (CILS {eur(lg, F['cils'], False)}), obligatoriu și pentru români.")
        bric = "Examenul B1"
    faq_html, ld = LG.faq_blocco(G, faq)
    corpo = f"""<section class="hero">
{LG.briciole(lg, "../", (bric, None))}
<h1>{h1}</h1>
<p class="lead">{lead}</p>
</section>
{LG.decide(G, lg, "Префектура" if uk else "Prefectura")}
<h2>{G.ic("info")}{s1[0]}</h2>
<p>{s1[1]}</p>
{fonte(G, lg, fonti_legge, v, fonti_parola(lg, 2))}
<h2>{G.ic("scudo")}{s2}</h2>
<div class="tab-wrap rc-tab"><table class="conf"><thead><tr>{"".join(f'<th scope="col">{x}</th>' for x in th)}</tr></thead>
<tbody>{righe}</tbody></table></div>
<p class="small">{quinto}</p>
<h2>{G.ic("lista")}{s3}</h2>
<ol class="passi">{"".join(f"<li><span>{x}</span></li>" for x in passi)}</ol>
<h2 id="duration">{G.ic("orologio")}{s4}</h2>
<p>{s4p}</p>
{tabella_durata(G, lg)}
<h2 id="online">{G.ic("attenzione")}{s5}</h2>
<p>{s5p}</p>
<div class="fonte">{G.ic("doc")}<span>{fonti_parola(lg, 2)}: {online}</span></div>
<h2>{G.ic("euro")}{s6}</h2>
<p>{s6p}</p>
{LG.faq_sezione(G, lg, faq_html)}
{LG.due_colonne(G, lg, "../", "../../", LG.GUIDE[lg][1][0])}
{LG.altre_lingue(G, lg, perc, "../../")}"""
    LG.pagina_l(G, lg, perc, titolo, descr, corpo, jsonld=ld)


# ---------------------------------------------------------------- costo
def pagina_costo(G, lg):
    uk = H(lg)
    F = LG.fatti(G)
    E = G.ENTE
    v = max(e["fatti"]["costo"]["verificato_il"] for e in G.enti)
    perc = f"{lg}/{LG.GUIDE[lg][2][0]}"

    def scheda(sigla, breve, testo):
        f = E[sigla]["fatti"]["costo"]
        fonti_ = " · ".join(a(x["url"], x["nome"]) for x in f["fonti"])
        return (f'<div class="fatto"><div class="f-et">{G.eb(sigla)}<span>{escape(LG.NOME_ENTE[lg][sigla])}</span></div><div class="f-breve">{breve}</div>'
                f'<p>{testo}</p>{fonte(G, lg, fonti_, f["verificato_il"], fonti_parola(lg, len(f["fonti"])))}</div>')

    c = lambda x: eur(lg, x, False)  # noqa: E731
    if uk:
        schede = (scheda("CILS", f"{c(F['cils'])} (B1 Cittadinanza)",
                         f"CILS B1 Cittadinanza: {c(F['cils'])}, однаковий збір в Італії та за кордоном. Ціну CILS B1 standard уточнюйте в центрі (у Мовному центрі Падуанського університету — {c(F['padova'])}).")
                  + scheda("CELI", "встановлює центр",
                           f"Ціну встановлює кожен екзаменаційний центр за угодою з Університетом для іноземців Перуджі. Приклад: CELI 2 i cittadinanza — {c(F['celi_tot'])} у Міланському університеті "
                           f"({c(F['celi_tassa'])} екзаменаційний збір + {c(F['celi_spese'])} адміністративний збір, сесія {data(lg, F['celi_data'])}).")
                  + scheda("PLIDA", "встановлює центр", "Кожен центр PLIDA встановлює ціну і повідомляє її під час реєстрації.")
                  + scheda("CERT.IT", f"{c(F['certit'])} у Римі Тре",
                           f"B1: {c(F['certit'])} у центрі Університету Рим Тре (Via Ostiense 123-129, Рим). У партнерських центрах реєструються й платять у самому центрі, який повідомляє ціну."))
        h1 = "Скільки коштує іспит B1 для громадянства?"
        lead = (f"За офіційними сайтами чотирьох екзаменаційних установ (перевірено {data(lg, v)}), CILS B1 Cittadinanza коштує {c(F['cils'])} всюди, "
                f"CERT.IT B1 — {c(F['certit'])} в Університеті Рим Тре, а для CELI і PLIDA кожен екзаменаційний центр встановлює власну ціну.")
        av = (f"Перед оплатою завжди питайте в центрі <strong>остаточну ціну</strong>: деякі центри додають адміністративні збори (наприклад, у Міланському університеті "
              f"{c(F['celi_spese'])} із {c(F['celi_tot'])} за CELI 2 i cittadinanza).")
        h2 = "Знайдіть центр і запитайте ціну"
        p2 = 'Екзаменаційні центри за містами — на наших італійських сторінках, з адресою, телефоном, email і сайтом: <a href="../../#citta" hreflang="it" lang="it">sedi per città</a>.'
        titolo = G.titolo_pagina(f"Скільки коштує іспит B1 для громадянства: CILS {c(F['cils'])}")
        descr = G.descrizione_pagina(f"Іспит B1 для громадянства Італії: CILS B1 Cittadinanza {c(F['cils'])} всюди, CERT.IT B1 {c(F['certit'])} у Римі Тре, CELI і PLIDA — ціна центру. Офіційні джерела.")
        bric = "Вартість"
    else:
        schede = (scheda("CILS", f"{c(F['cils'])} (B1 Cittadinanza)",
                         f"CILS B1 Cittadinanza: {c(F['cils'])}, aceeași taxă în Italia și în străinătate. Pentru CILS B1 standard întrebați centrul (la Centrul Lingvistic al Universității din Padova costă {c(F['padova'])}).")
                  + scheda("CELI", "îl stabilește centrul",
                           f"Prețul îl stabilește fiecare centru de examen, conform acordului cu Universitatea pentru Străini din Perugia. Exemplu: CELI 2 i cittadinanza {c(F['celi_tot'])} la Universitatea din Milano "
                           f"({c(F['celi_tassa'])} taxă de examen + {c(F['celi_spese'])} taxe administrative, sesiunea din {data(lg, F['celi_data'])}).")
                  + scheda("PLIDA", "îl stabilește centrul", "Fiecare centru PLIDA stabilește prețul și vi-l comunică la înscriere.")
                  + scheda("CERT.IT", f"{c(F['certit'])} la Roma Tre",
                           f"B1: {c(F['certit'])} la centrul Universității Roma Tre (Via Ostiense 123-129, Roma). La centrele partenere vă înscrieți și plătiți la centru, care vă spune prețul."))
        h1 = "Cât costă examenul B1 pentru cetățenie?"
        lead = (f"Potrivit site-urilor oficiale ale celor patru instituții de examinare (verificate la {data(lg, v)}), CILS B1 Cittadinanza costă {c(F['cils'])} peste tot, "
                f"CERT.IT B1 costă {c(F['certit'])} la Roma Tre, iar pentru CELI și PLIDA fiecare centru de examen își stabilește propriul preț.")
        av = (f"Întrebați întotdeauna centrul <strong>prețul final</strong> înainte de a plăti: unele centre adaugă taxe administrative (la Universitatea din Milano, de exemplu, "
              f"{c(F['celi_spese'])} din cei {c(F['celi_tot'])} pentru CELI 2 i cittadinanza).")
        h2 = "Găsiți un centru și întrebați prețul"
        p2 = 'Centrele de examen pe orașe sunt pe paginile noastre în italiană, cu adresă, telefon, e-mail și site: <a href="../../#citta" hreflang="it" lang="it">sedi per città</a>.'
        titolo = G.titolo_pagina(f"Cât costă examenul B1 pentru cetățenie: CILS {c(F['cils'])}")
        descr = G.descrizione_pagina(f"Examenul B1 pentru cetățenia italiană: CILS B1 Cittadinanza {c(F['cils'])} peste tot, CERT.IT B1 {c(F['certit'])} la Roma Tre, CELI și PLIDA după centru. Surse oficiale.")
        bric = "Cost"
    corpo = f"""<section class="hero">
{LG.briciole(lg, "../", (bric, None))}
<h1>{h1}</h1>
<p class="lead">{lead}</p>
</section>
{LG.nota_esame(G, lg)}
<div class="fatti">{schede}</div>
{G.avviso(av)}
<div class="due">
<section>
<h2>{G.ic("pin")}{h2}</h2>
<p>{p2}</p>
{LG.griglia_guide(G, lg, "../", salta=LG.GUIDE[lg][2][0])}
</section>
<aside>{LG.modulo(G, lg, "../../")}</aside>
</div>
{LG.altre_lingue(G, lg, perc, "../../")}"""
    LG.pagina_l(G, lg, perc, titolo, descr, corpo)


# ---------------------------------------------------------------- prove d'esempio
GLOSSE = {
    "uk": [("specifiche", "специфікація іспиту"), ("commentata", "письмове завдання з коментарями"), ("certit_b1", "зразок іспиту"), ("trascrizion", "транскрипція аудіо"),
           ("chiavi", "ключі відповідей"), ("criteri", "критерії оцінювання"), ("foglio", "бланк відповідей"), ("fogli", "бланки відповідей"), ("sillabo", "програма (силабус)"),
           ("produzione scritta", "письмове завдання"), ("produzione orale", "усне завдання"), ("input orale", "матеріали для усної частини"), ("descrizione", "опис іспиту"),
           ("quaderno", "зошит завдань"), ("audio", "аудіо для аудіювання"), ("esempio", "зразок іспиту"), ("parlato", "усна частина")],
    "ro": [("specifiche", "specificațiile examenului"), ("commentata", "proba scrisă comentată"), ("certit_b1", "model de examen"), ("trascrizion", "transcrierea audio"),
           ("chiavi", "cheia răspunsurilor"), ("criteri", "criterii de evaluare"), ("foglio", "foaie de răspunsuri"), ("fogli", "foi de răspunsuri"), ("sillabo", "programa (silabus)"),
           ("produzione scritta", "proba de scriere"), ("produzione orale", "proba orală"), ("input orale", "materiale pentru proba orală"), ("descrizione", "descrierea examenului"),
           ("quaderno", "caietul de examen"), ("audio", "audio pentru ascultare"), ("esempio", "model de examen"), ("parlato", "proba orală")],
}


def peso(lg, byte):
    if byte < 1_000_000:
        return f"{round(byte / 1000)} {'КБ' if lg == 'uk' else 'KB'}"
    return f"{byte / 1_000_000:.1f}".replace(".", ",") + (" МБ" if lg == "uk" else " MB")


def pagina_esempi(G, lg):
    uk = H(lg)
    v = G.esempi["verificato_il"]
    perc = f"{lg}/{LG.GUIDE[lg][3][0]}"
    blocchi = []
    for e in G.esempi["enti"]:
        sigla = e["sigla"]
        righe = []
        for f in e["file"]:
            dim = (f'{f["numero"]} × ' if f.get("numero") else "") + peso(lg, f["byte"])
            pg = []
            if f.get("pagine"):
                n = f["pagine"]
                pg = [f'{n} {pl_uk(n, "сторінка", "сторінки", "сторінок")}' if uk else f'{n} {pl_ro(n, "pagină", "pagini")}']
            det = " · ".join([dim] + pg)
            nome = a(f["url"], f["nome"]) if f.get("url") else f'<span class="nome">{escape(f["nome"])}</span>'
            gl = next((g for k, g in GLOSSE[lg] if k in f["nome"].lower()), "")
            nome += f' <span class="small">({gl})</span>' if gl else ""
            righe.append(f'<li><span class="fi">{G.ic(G.ICONA_FILE[f["formato"]])}</span><div>{nome}</div>'
                         f'<div class="meta"><strong>{f["formato"]}</strong><span>{escape(det)}</span></div></li>')
        nota = ""
        if e.get("link_diretti") is False:
            nota = ("<p class=\"small\">Юридичні примітки Університету Рим Тре забороняють прямі посилання на його файли з інших сайтів, тому ми даємо лише офіційну сторінку: "
                    "файли — внизу, у розділі «Esempio di esame».</p>" if uk else
                    "<p class=\"small\">Notele juridice ale Universității Roma Tre interzic linkurile directe către fișierele sale de pe alte site-uri, așa că dăm doar pagina oficială: "
                    "fișierele sunt jos, la «Esempio di esame».</p>")
        dur = G.ENTE[sigla]["fatti"]["durata"]["prove"]["totale"]
        n = len(e["file"])
        intro = (f'{n} {pl_uk(n, "файл", "файли", "файлів")} на офіційній сторінці установи «{escape(LG.NOME_ENTE[lg][sigla])}». Тривалість іспиту: {escape(LG.totale(lg, dur))}.' if uk
                 else f'{n} {pl_ro(n, "fișier", "fișiere")} pe pagina oficială a instituției «{escape(LG.NOME_ENTE[lg][sigla])}». Durata examenului: {escape(LG.totale(lg, dur))}.')
        blocchi.append(f"""<section class="card es-card" id="{G.SLUG_ENTE[sigla]}">
<h2>{G.eb(sigla)} {escape(e["esame"])}</h2>
<p>{intro}</p>
<div class="azioni"><a class="btn" href="{escape(e["pagina"]["url"])}" rel="noopener">{G.ic("web")}{"Офіційна сторінка" if uk else "Pagina oficială"} {sigla}</a></div>
<ul class="file-lista">{"".join(righe)}</ul>
{nota}
</section>""")
    vai = "".join(f'<a href="#{G.SLUG_ENTE[e["sigla"]]}">{G.eb(e["sigla"])}<small>{escape(e["esame"])}</small></a>' for e in G.esempi["enti"])
    if uk:
        h1 = "Безкоштовні офіційні зразки іспиту B1 для громадянства Італії"
        lead = (f"За офіційними сайтами CILS, CELI, PLIDA і CERT.IT (посилання перевірено {data(lg, v)}), кожна установа безкоштовно публікує зразок іспиту з аудіо та ключами відповідей. "
                "Назви файлів — італійською, як на офіційних сайтах; самі завдання мають справжній формат іспиту.")
        h2, punti = "Як тренуватися", [f'Виконайте зразок із таймером, за часом із <a href="../{LG.GUIDE[lg][1][0]}#duration">таблиці тривалості</a>.',
                                       "Слухайте кожен аудіофайл стільки разів, скільки дозволяє іспит (інструкції — у самому завданні).",
                                       "Перевірте відповіді за офіційним ключем, якщо він є.",
                                       "Тренуйте усну частину вголос: розкажіть про себе і про повсякденні теми."]
        diritti = "Зразки належать екзаменаційним установам: завантажуйте їх з офіційних сторінок і не копіюйте деінде."
        titolo = G.titolo_pagina("Зразки іспиту B1 для громадянства Італії: безкоштовні PDF")
        descr = G.descrizione_pagina("Безкоштовні офіційні зразки іспиту B1 для громадянства Італії: CILS, CELI, PLIDA і CERT.IT, з PDF, аудіо та ключами, пояснення українською.")
        bric = "Зразки іспиту"
    else:
        h1 = "Modele oficiale gratuite pentru examenul B1 de cetățenie italiană"
        lead = (f"Potrivit site-urilor oficiale CILS, CELI, PLIDA și CERT.IT (linkuri verificate la {data(lg, v)}), fiecare instituție publică gratuit un model de examen, cu audio și cheia răspunsurilor. "
                "Numele fișierelor sunt în italiană, ca pe site-urile oficiale; probele au formatul real al examenului.")
        h2, punti = "Cum să exersați", [f'Faceți modelul cu cronometrul, după timpii din <a href="../{LG.GUIDE[lg][1][0]}#duration">tabelul duratei</a>.',
                                        "Ascultați fiecare fișier audio de atâtea ori cât permite examenul (instrucțiunile sunt în probă).",
                                        "Verificați răspunsurile cu cheia oficială, acolo unde există.",
                                        "Exersați proba orală cu voce tare: prezentați-vă și vorbiți despre teme de zi cu zi."]
        diritti = "Modelele aparțin instituțiilor de examinare: descărcați-le de pe paginile lor și nu le copiați în altă parte."
        titolo = G.titolo_pagina("Modele de examen B1 pentru cetățenia italiană: PDF gratuite")
        descr = G.descrizione_pagina("Modele oficiale gratuite pentru examenul B1 de cetățenie italiană: CILS, CELI, PLIDA și CERT.IT, cu PDF, audio și chei, explicate în română.")
        bric = "Modele de examen"
    corpo = f"""<section class="hero">
{LG.briciole(lg, "../", (bric, None))}
<h1>{h1}</h1>
<p class="lead">{lead}</p>
<div class="es-vai">{vai}</div>
</section>
{LG.nota_esame(G, lg)}
{"".join(blocchi)}
<section>
<h2>{G.ic("lista")}{h2}</h2>
<ul>{"".join(f"<li>{x}</li>" for x in punti)}</ul>
<p class="small">{diritti}</p>
</section>
{LG.due_colonne(G, lg, "../", "../../", LG.GUIDE[lg][3][0])}
{LG.altre_lingue(G, lg, perc, "../../")}"""
    LG.pagina_l(G, lg, perc, titolo, descr, corpo)


# ---------------------------------------------------------------- esoneri
def pagina_esoneri(G, lg):
    uk = H(lg)
    Fe = G.esoneri["fonti"]
    v = G.esoneri["verificato_il"]
    A = EN.a2_test(G)
    dm = data(lg, iso_it(Fe["dm2021"]["nome"]))
    ce = data(lg, iso_it(EN.cit(G, "vademecum", r"rilasciato dal (\d{1,2} dicembre \d{4})")))
    sent = num(Fe["corte25"]["nome"], r"sentenza n\. (\d+) del")
    sent_a = num(Fe["corte25"]["nome"], r"del (\d{4})")
    circ = num(Fe["vademecum"]["nome"], r"circolare n\. (\d+)")
    circ_d = data(lg, iso_it(Fe["vademecum"]["nome"]))
    perc = f"{lg}/{LG.GUIDE[lg][4][0]}"

    def src(*k):
        return fonte(G, lg, " · ".join(a(Fe[x]["url"], Fe[x]["nome"]) for x in k), v, fonti_parola(lg, len(k)))

    def scheda(icona, titolo, testo, *k):
        return f'<div class="fatto"><div class="f-et">{G.ic(icona)}<span>{titolo}</span></div><p>{testo}</p>{src(*k)}</div>'

    if uk:
        tab = [("Підписана угода про інтеграцію", "Звільнений", "Складає тест, якщо в кредитах угоди не визнано рівень A2"),
               ("Дозвіл ЄС для довгострокових резидентів", "Звільнений", "Не потрібен: це дозвіл, який ви вже маєте"),
               ("Серйозні труднощі, підтверджені державною медичною установою", "Звільнений", "Звільнений"),
               ("Сертифікат A2 від визнаної установи", "Недостатньо: потрібен B1 або вище", "Тест не складає"),
               ("Сертифікат B1 від визнаної установи", "Дійсний", "Тест не складає"),
               ("Італійський атестат середньої школи (scuola media або superiore)", "Дійсний замість сертифіката (освіта італійською)", "Тест не складає"),
               (f"Дитина до {A['minori']} років", "У прочитаних джерелах не розглянуто", "Тест не складає"),
               ("Громадянин ЄС або член родини з «carta di soggiorno per familiare»", "Потрібен B1", "У прочитаних джерелах не розглянуто")]
        th = ("Ваш випадок", "Громадянство (сертифікат B1)", "Carta di soggiorno (тест A2)")
        cittad = (scheda("ok", "Ви підписали угоду про інтеграцію",
                         "Вимога не стосується вас, якщо ви підписали угоду про інтеграцію (ст. 4-bis Зведеного закону про імміграцію). Vademecum Міністерства уточнює, що йдеться про людей, які приїхали до Італії "
                         "через возз’єднання або збереження єдності сім’ї; вони підтверджують це довідкою Префектури (Sportello unico) і вписують дані угоди в заяву.", "legge91", "vademecum")
                  + scheda("ok", "У вас є дозвіл ЄС для довгострокових резидентів",
                           f"Ви звільнені, якщо маєте дозвіл ЄС для довгострокових резидентів («carta di soggiorno»). За Vademecum зараховується і старий дозвіл «CE» для довгострокових резидентів, виданий починаючи з {ce}, коли запровадили тест з італійської.",
                           "legge91", "vademecum")
                  + scheda("info", "У вас серйозні труднощі з вивченням мови",
                           f"Рішенням № {sent} {sent_a} року Конституційний суд звільнив людей із серйозними труднощами у вивченні мови через вік, хворобу чи інвалідність. "
                           "Потрібна довідка <strong>державної медичної установи</strong>: за Міністерством довідки сімейного лікаря недостатньо. Якщо ви живете в Італії й маєте іноземну медичну довідку, "
                           "додайте довідку італійської державної медичної установи; якщо живете за кордоном — подайте іноземну довідку з перекладом і легалізацією.", "corte25", "circ14605", "vademecum")
                  + scheda("doc", "Замість сертифіката: документ про освіту італійською",
                           "Якщо ви не звільнені, замість сертифіката B1 можна подати документ визнаного державного або прирівняного навчального закладу — від середньої школи (scuola media) і вище, "
                           "здобутий <strong>італійською</strong>. Для державної школи достатньо самодекларації з реквізитами; для приватної або прирівняної — засвідчена копія.", "legge91", "vademecum"))
        h1 = "Звільнення від тесту з італійської: громадянство (B1) і carta di soggiorno (A2)"
        lead = (f"Згідно зі ст. 9.1 Закону 91/1992 (чинний текст на Normattiva, прочитано {data(lg, v)}) і Vademecum Міністерства внутрішніх справ (циркуляр № {circ} від {circ_d}), сертифікат B1 для громадянства не потрібен, "
                "якщо ви підписали угоду про інтеграцію, маєте дозвіл ЄС для довгострокових резидентів або маєте серйозні труднощі, підтверджені державною медичною установою. "
                f"Для carta di soggiorno тест A2 у Префектурі не потрібен, наприклад, якщо у вас уже є сертифікат A2 або вище чи італійський шкільний атестат (декрет Міністра внутрішніх справ від {dm}).")
        chi = "Префектура (громадянство) або Квестура (дозвіл ЄС для довгострокових резидентів)"
        h2a, h2b = "Коротко: ваш випадок", "Громадянство: кому не потрібен сертифікат B1"
        p2b = "Хто подає заяву на громадянство через шлюб або за проживанням (статті 5 і 9 Закону 91/1992), має знати італійську на рівні B1 або вище. Закон і Міністерство роблять винятки:"
        h3a = "Кому B1 потрібен у будь-якому разі"
        p3a = ("За Vademecum Міністерства: громадянам Європейського Союзу; власникам «carta di soggiorno» для членів родини громадян Італії або ЄС (це не дозвіл ЄС для довгострокових резидентів); "
               "громадянам Великої Британії та членам їхніх родин із карткою проживання за Угодою про вихід («Brexit»).")
        h3b = "Які сертифікати зараховуються"
        p3b = ("Сертифікат B1 або вище від визнаної установи. Vademecum називає: Університет для іноземців Сієни (CILS), Університет для іноземців Перуджі (CELI), Університет Рим Тре (CERT.IT), Товариство Данте Аліґ’єрі (PLIDA) "
               "і Університет для іноземців «Dante Alighieri» у Реджо-Калабрії. Сертифікат можна отримати також у CPIA (державному центрі освіти дорослих). Сертифікати регіональних курсів професійної підготовки не зараховуються.")
        h2c = "Carta di soggiorno: тест з італійської A2"
        p2c = (f"Щоб отримати дозвіл ЄС для довгострокових резидентів («carta di soggiorno»), треба скласти тест з італійської (ст. 9, ч. 2-bis Зведеного закону про імміграцію) на рівні <strong>A2</strong>: "
               f"розуміти часто вживані речення й вирази. Правила — у декреті Міністра внутрішніх справ від {dm}.")
        passi = [f'Подайте заяву онлайн до Префектури провінції, де живете, на {a(Fe["portale"]["url"], "Portale Servizi")} Міністерства внутрішніх справ.',
                 f"Префектура запрошує вас протягом {A['giorni_conv']} днів, із датою, часом і місцем.",
                 f"Тест проходить на комп’ютері або, на ваше прохання, на папері. Наприклад, Префектура Лекко описує три частини: аудіювання ({A['orale']} хв), читання ({A['scritta']} хв) і письмову взаємодію ({A['inter']} хв).",
                 f"Щоб скласти, потрібно щонайменше <strong>{A['soglia']}%</strong> від загальної кількості балів. Результат передають до Квестури, яка видає дозвіл, якщо інші вимоги виконано.",
                 f"Якщо не склали, можна подати заяву знову: за Міністерством — лише через {A['ripeti']} днів після попереднього тесту."]
        h3c = "Хто не складає тест A2"
        noa2 = [f"діти заявника і чоловіка/дружини віком до {A['minori']} років;",
                "люди із серйозними труднощами у вивченні мови через вік, хворобу чи інвалідність, підтвердженими державною медичною установою;",
                "власники сертифіката A2 або вище від визнаної установи (отже, і B1, складеного для громадянства);",
                "ті, хто має підсумковий сертифікат курсу CPIA рівня A2 або вище, або рівень A2, визнаний у кредитах угоди про інтеграцію;",
                "власники італійського атестата середньої школи (scuola media або superiore), студенти італійських університетів, аспіранти або слухачі університетських магістерських програм в Італії;",
                "деякі працівники (керівники і висококваліфіковані працівники, викладачі та дослідники університетів, перекладачі, акредитовані журналісти: ст. 27 Зведеного закону про імміграцію);",
                "власники міжнародного захисту та дозволів для досліджень в університетах і установах під наглядом Міністерства університетів."]
        p_carta = f'Дохід та інші вимоги для carta: <a href="../{LG.GUIDE[lg][7][0]}">вимоги до carta di soggiorno</a>.'
        titolo = G.titolo_pagina("Звільнення від тесту з італійської: громадянство B1, carta A2")
        descr = G.descrizione_pagina("Хто звільнений від тесту B1 для громадянства Італії і від тесту A2 для carta di soggiorno: закон і Міністерство внутрішніх справ, українською.")
        bric = "Звільнення"
    else:
        tab = [("Acord de integrare semnat", "Scutit", "Dă testul, dacă în creditele acordului nu este recunoscut nivelul A2"),
               ("Permis UE pe termen lung", "Scutit", "Nu e nevoie: este permisul pe care îl aveți deja"),
               ("Dificultăți grave certificate de o unitate sanitară publică", "Scutit", "Scutit"),
               ("Certificat A2 de la o instituție recunoscută", "Nu ajunge: trebuie B1 sau mai mult", "Nu dă testul"),
               ("Certificat B1 de la o instituție recunoscută", "Valabil", "Nu dă testul"),
               ("Diplomă de școală italiană (scuola media sau superiore)", "Valabilă în locul certificatului (studii în italiană)", "Nu dă testul"),
               (f"Copil sub {A['minori']} ani", "Situație netratată în sursele citite", "Nu dă testul"),
               ("Cetățean UE (de exemplu român) sau membru de familie cu «carta di soggiorno per familiare»", "Trebuie să aibă B1", "Situație netratată în sursele citite")]
        th = ("Cazul dumneavoastră", "Cetățenie (certificat B1)", "Carta di soggiorno (test A2)")
        cittad = (scheda("ok", "Ați semnat acordul de integrare",
                         "Cerința nu vi se aplică dacă ați semnat acordul de integrare (art. 4-bis din Textul unic privind imigrația). Vademecum-ul Ministerului precizează că este vorba de persoane venite în Italia "
                         "prin reîntregirea sau coeziunea familiei; ele o dovedesc cu adeverința Prefecturii (Sportello unico) și trec datele acordului în cerere.", "legge91", "vademecum")
                  + scheda("ok", "Aveți permisul UE pe termen lung",
                           f"Sunteți scutit(ă) dacă aveți permisul UE pentru rezidenți pe termen lung («carta di soggiorno»), pe care îl primesc doar cetățenii din afara UE. Potrivit Vademecum-ului contează și vechiul permis «CE» pe termen lung, dacă a fost eliberat începând cu {ce}, când a intrat în vigoare testul de italiană.",
                           "legge91", "vademecum")
                  + scheda("info", "Aveți dificultăți grave în învățarea limbii",
                           f"Prin sentința nr. {sent} din {sent_a}, Curtea Constituțională a scutit persoanele cu dificultăți grave în învățarea limbii din cauza vârstei, a bolii sau a unei dizabilități. "
                           "Trebuie un certificat de la o <strong>unitate sanitară publică</strong>: potrivit Ministerului, certificatul medicului de familie nu ajunge. Dacă locuiți în Italia și aveți un certificat medical străin, "
                           "adăugați unul de la o unitate sanitară publică italiană; dacă locuiți în străinătate, prezentați certificatul străin tradus și legalizat.", "corte25", "circ14605", "vademecum")
                  + scheda("doc", "În locul certificatului: un titlu de studii în italiană",
                           "Dacă nu sunteți scutit(ă), în locul certificatului B1 puteți prezenta un titlu de la o școală publică sau echivalentă recunoscută, de la gimnaziu (scuola media) în sus, "
                           "obținut <strong>în limba italiană</strong>. Pentru o școală publică ajunge o declarație pe proprie răspundere cu datele; pentru o școală privată sau echivalentă trebuie o copie legalizată.", "legge91", "vademecum"))
        h1 = "Scutirea de testul de italiană: cetățenie (B1) și carta di soggiorno (A2)"
        lead = (f"Potrivit art. 9.1 din Legea 91/1992 (text în vigoare pe Normattiva, citit la {data(lg, v)}) și Vademecum-ului Ministerului de Interne (circulara nr. {circ} din {circ_d}), certificatul B1 pentru cetățenie nu este necesar "
                "pentru cine a semnat acordul de integrare, are permisul UE pe termen lung sau are dificultăți grave certificate de o unitate sanitară publică. "
                f"Cetățenii români și ceilalți cetățeni UE trebuie însă să aibă certificatul B1. Pentru carta di soggiorno, testul A2 de la Prefectură nu este necesar, de exemplu, cu un certificat A2 sau superior ori cu o diplomă școlară italiană (decretul ministrului de Interne din {dm}).")
        chi = "Prefectura (cetățenia) sau Chestura (permisul UE pe termen lung)"
        h2a, h2b = "Pe scurt: cazul dumneavoastră", "Cetățenie: cine nu are nevoie de certificatul B1"
        p2b = "Cine cere cetățenia prin căsătorie sau prin rezidență (articolele 5 și 9 din Legea 91/1992) trebuie să cunoască limba italiană la nivel B1 sau superior. Legea și Ministerul exclud aceste cazuri:"
        h3a = "Cine are nevoie oricum de B1 (și românii)"
        p3a = ("Potrivit Vademecum-ului Ministerului: <strong>cetățenii Uniunii Europene</strong>, deci și cetățenii români; titularii «carta di soggiorno» pentru membrii de familie ai cetățenilor italieni sau UE (nu este permisul UE pe termen lung); "
               "cetățenii britanici și membrii familiilor lor cu cartea de ședere din Acordul de retragere («Brexit»).")
        h3b = "Ce certificate sunt valabile"
        p3b = ("Un certificat B1 sau superior de la o instituție recunoscută. Vademecum-ul numește: Universitatea pentru Străini din Siena (CILS), Universitatea pentru Străini din Perugia (CELI), Universitatea Roma Tre (CERT.IT), Societatea Dante Alighieri (PLIDA) "
               "și Universitatea pentru Străini «Dante Alighieri» din Reggio Calabria. Certificatul se poate obține și la un CPIA (centru public pentru educația adulților). Certificatele cursurilor regionale de formare profesională nu sunt valabile.")
        h2c = "Carta di soggiorno: testul de italiană A2 (pentru cetățenii din afara UE)"
        p2c = (f"Pentru permisul UE pe termen lung («carta di soggiorno»), pe care îl cer cetățenii din afara UE (de exemplu din Republica Moldova), trebuie promovat un test de italiană (art. 9, alin. 2-bis din Textul unic privind imigrația) la nivel <strong>A2</strong>: "
               f"înțelegerea propozițiilor și expresiilor folosite des. Regulile sunt în decretul ministrului de Interne din {dm}.")
        passi = [f'Faceți cererea online la Prefectura provinciei în care locuiți, pe {a(Fe["portale"]["url"], "Portale Servizi")} al Ministerului de Interne.',
                 f"Prefectura vă convoacă în {A['giorni_conv']} {pl_ro(A['giorni_conv'], 'zi', 'zile')}, cu ziua, ora și locul.",
                 f"Testul se dă pe calculator sau, la cerere, pe hârtie. De exemplu, Prefectura din Lecco descrie trei probe: ascultare ({A['orale']} {pl_ro(A['orale'], 'minut', 'minute')}), citire ({A['scritta']} {pl_ro(A['scritta'], 'minut', 'minute')}) și interacțiune scrisă ({A['inter']} {pl_ro(A['inter'], 'minut', 'minute')}).",
                 f"Pentru a promova trebuie cel puțin <strong>{A['soglia']}%</strong> din punctajul total. Rezultatul ajunge la Chestură, care eliberează permisul dacă sunt îndeplinite celelalte cerințe.",
                 f"Dacă nu promovați, puteți face din nou cererea: potrivit Ministerului, doar după {A['ripeti']} {pl_ro(A['ripeti'], 'zi', 'zile')} de la testul anterior."]
        h3c = "Cine nu dă testul A2"
        noa2 = [f"copiii sub {A['minori']} ani ai solicitantului și ai soțului/soției;",
                "persoanele cu dificultăți grave de învățare din cauza vârstei, a bolii sau a unei dizabilități, certificate de o unitate sanitară publică;",
                "titularii unui certificat A2 sau superior de la o instituție recunoscută (deci și B1 dat pentru cetățenie);",
                "cine are certificatul final al unui curs CPIA de nivel A2 sau superior, ori nivelul A2 recunoscut în creditele acordului de integrare;",
                "cine are o diplomă de școală italiană (scuola media sau superiore), studenții unei universități italiene, doctoranzii sau cei la un master universitar în Italia;",
                "unii lucrători (manageri și lucrători înalt calificați, profesori și cercetători universitari, traducători și interpreți, jurnaliști acreditați: art. 27 din Textul unic privind imigrația);",
                "titularii protecției internaționale și ai permiselor pentru cercetare la universități și instituții supravegheate de Ministerul Universităților."]
        p_carta = f'Venitul și celelalte cerințe pentru carta: <a href="../{LG.GUIDE[lg][8][0]}">cerințele pentru carta di soggiorno</a>.'
        titolo = G.titolo_pagina("Scutirea de testul de italiană: cetățenie B1, carta A2")
        descr = G.descrizione_pagina("Cine e scutit de testul B1 pentru cetățenia italiană și de testul A2 pentru carta di soggiorno: legea și Ministerul. Românii (cetățeni UE) au nevoie de B1.")
        bric = "Scutiri"
    righe = "".join(f'<tr><td><strong>{escape(c_)}</strong></td><td data-l="{th[1]}">{escape(x)}</td><td data-l="{th[2]}">{escape(y)}</td></tr>' for c_, x, y in tab)
    corpo = f"""<section class="hero">
{LG.briciole(lg, "../", (bric, None))}
<h1>{h1}</h1>
<p class="lead">{lead}</p>
</section>
{LG.decide(G, lg, chi)}
<section>
<h2 id="summary">{G.ic("lista")}{h2a}</h2>
<div class="tab-wrap rc-tab"><table class="conf"><thead><tr>{"".join(f'<th scope="col">{x}</th>' for x in th)}</tr></thead>
<tbody>{righe}</tbody></table></div>
{src("legge91", "vademecum", "dm2021")}
</section>
<section>
<h2 id="citizenship">{G.ic("scudo")}{h2b}</h2>
<p>{p2b}</p>
<div class="fatti">{cittad}</div>
<h3>{h3a}</h3>
<p>{p3a}</p>
<h3>{h3b}</h3>
<p>{p3b}</p>
{src("vademecum", "domanda")}
</section>
<section>
<h2 id="carta-di-soggiorno">{G.ic("doc")}{h2c}</h2>
<p>{p2c}</p>
<ol class="passi">{"".join(f"<li><span>{x}</span></li>" for x in passi)}</ol>
{src("dm2021", "minint_test", "lecco")}
<h3 id="no-a2">{h3c}</h3>
<ul>{"".join(f"<li>{x}</li>" for x in noa2)}</ul>
{src("dm2021", "tu9")}
<p>{p_carta}</p>
</section>
{LG.due_colonne(G, lg, "../", "../../", LG.GUIDE[lg][4][0])}
{LG.altre_lingue(G, lg, perc, "../../")}"""
    LG.pagina_l(G, lg, perc, titolo, descr, corpo)


# ---------------------------------------------------------------- redditi e calcolatore
JS_UI = {
    "uk": """(function(){
  var f=document.getElementById('calc-redditi');if(!f)return;
  function eur(c){var n=Math.abs(c),e=Math.floor(n/100),d=String(n%100).padStart(2,'0');return e.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g,'\\u00a0')+','+d+'\\u00a0\\u20ac';}
  function leggiEuro(t){t=String(t||'').replace(/[\\s\\u00a0\\u20ac]/g,'');if(!t)return null;
    if(/,\\d{1,2}$/.test(t)){t=t.replace(/\\./g,'').replace(',','.');}else if(/\\.\\d{1,2}$/.test(t)&&t.split('.').length===2){}else{t=t.replace(/[.,]/g,'');}
    var v=Number(t);return isFinite(v)&&v>=0?Math.round(v*100):null;}
  var out=document.getElementById('calc-esito');
  function riga(id,titolo,x,chi){var el=out.querySelector('[data-r="'+id+'"]');if(!el)return;
    el.hidden=false;el.className='c-riga '+(x.sopra?'si':'no');
    el.querySelector('.c-tit').textContent=titolo;
    el.querySelector('.c-soglia').textContent='Поріг: '+eur(x.soglia)+' на рік';
    el.querySelector('.c-esito').textContent=x.sopra?('Ви вище порогу на '+eur(x.differenza)+'.'):('Ви нижче порогу: бракує '+eur(-x.differenza)+'.');
    el.querySelector('.c-chi').textContent=chi;}
  function calcola(ev){if(ev)ev.preventDefault();
    var coniuge=f.coniuge.checked,figli=Math.max(0,Math.min(20,parseInt(f.figli.value,10)||0));
    var reddito=leggiEuro(f.reddito.value),err=f.querySelector('[data-errore]');
    if(reddito===null){err.hidden=false;out.hidden=true;return;}
    err.hidden=true;out.hidden=false;
    var r=calcolaRedditi(coniuge,figli,reddito);
    riga('cittadinanza','Громадянство Італії за проживанням',r.cittadinanza,'Рішення ухвалює Префектура: вона дивиться на ваш оподатковуваний дохід IRPEF за останні 3 роки.');
    riga('carta_solo','Carta di soggiorno (дозвіл ЄС для довгострокових резидентів), лише для вас',r.carta_solo,'Рішення ухвалює Квестура.');
    var fam=out.querySelector('[data-r="carta_famiglia"]');
    if(r.familiari>0){riga('carta_famiglia','Carta di soggiorno також для '+(r.familiari===1?'1 члена родини':r.familiari+' членів родини'),r.carta_famiglia,'Рішення ухвалює Квестура.');}else{fam.hidden=true;}
    out.querySelector('[data-quattordici]').hidden=figli<2;
  }
  f.addEventListener('submit',calcola);
  f.addEventListener('change',function(){if(f.reddito.value)calcola();});
})();""",
    "ro": """(function(){
  var f=document.getElementById('calc-redditi');if(!f)return;
  function eur(c){var n=Math.abs(c),e=Math.floor(n/100),d=String(n%100).padStart(2,'0');return e.toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g,'.')+','+d+'\\u00a0\\u20ac';}
  function leggiEuro(t){t=String(t||'').replace(/[\\s\\u00a0\\u20ac]/g,'');if(!t)return null;
    if(/,\\d{1,2}$/.test(t)){t=t.replace(/\\./g,'').replace(',','.');}else if(/\\.\\d{1,2}$/.test(t)&&t.split('.').length===2){}else{t=t.replace(/[.,]/g,'');}
    var v=Number(t);return isFinite(v)&&v>=0?Math.round(v*100):null;}
  var out=document.getElementById('calc-esito');
  function membri(n){return n===1?'1 membru de familie':n+(n%100===0||n%100>=20?' de membri de familie':' membri de familie');}
  function riga(id,titolo,x,chi){var el=out.querySelector('[data-r="'+id+'"]');if(!el)return;
    el.hidden=false;el.className='c-riga '+(x.sopra?'si':'no');
    el.querySelector('.c-tit').textContent=titolo;
    el.querySelector('.c-soglia').textContent='Pragul: '+eur(x.soglia)+' pe an';
    el.querySelector('.c-esito').textContent=x.sopra?('Sunteți peste prag cu '+eur(x.differenza)+'.'):('Sunteți sub prag: lipsesc '+eur(-x.differenza)+'.');
    el.querySelector('.c-chi').textContent=chi;}
  function calcola(ev){if(ev)ev.preventDefault();
    var coniuge=f.coniuge.checked,figli=Math.max(0,Math.min(20,parseInt(f.figli.value,10)||0));
    var reddito=leggiEuro(f.reddito.value),err=f.querySelector('[data-errore]');
    if(reddito===null){err.hidden=false;out.hidden=true;return;}
    err.hidden=true;out.hidden=false;
    var r=calcolaRedditi(coniuge,figli,reddito);
    riga('cittadinanza','Cetățenie italiană prin rezidență',r.cittadinanza,'Decide Prefectura: se uită la venitul impozabil IRPEF din ultimii 3 ani.');
    riga('carta_solo','Carta di soggiorno (permis UE pe termen lung, doar pentru cetățenii din afara UE), doar pentru dumneavoastră',r.carta_solo,'Decide Chestura.');
    var fam=out.querySelector('[data-r="carta_famiglia"]');
    if(r.familiari>0){riga('carta_famiglia','Carta di soggiorno și pentru '+membri(r.familiari),r.carta_famiglia,'Decide Chestura.');}else{fam.hidden=true;}
    out.querySelector('[data-quattordici]').hidden=figli<2;
  }
  f.addEventListener('submit',calcola);
  f.addEventListener('change',function(){if(f.reddito.value)calcola();});
})();""",
}


def js_calcolo(G, lg, js_soglie):
    """Il blocco di calcolo è quello italiano (tra /*calcolo-inizio*/ e /*calcolo-fine*/), identico: cambiano solo i testi."""
    it = G.JS_REDDITI % js_soglie
    return it[: it.index("/*calcolo-fine*/") + len("/*calcolo-fine*/")] + "\n" + JS_UI[lg]


def tabella_carta(G, lg):
    uk = H(lg)
    anno = G.RICONG["anno"]
    annuo = G.cent(G.RICONG["assegno_sociale"]["annuo"])
    meta = annuo // 2
    righe = []
    for n in range(0, 6):
        if uk:
            chi = "лише для вас" if n == 0 else f"ви і {n} {pl_uk(n, 'член', 'члени', 'членів')} родини"
            pers = f"{n + 1} {pl_uk(n + 1, 'особа', 'особи', 'осіб')}"
        else:
            chi = "doar pentru dumneavoastră" if n == 0 else f"dumneavoastră și {n} {pl_ro(n, 'membru', 'membri')} de familie"
            pers = f"{n + 1} {pl_ro(n + 1, 'persoană', 'persoane')}"
        righe.append(f'<tr><td><strong>{chi}</strong></td><td data-l="{"Осіб" if uk else "Persoane"}">{pers}</td>'
                     f'<td data-l="{"На рік" if uk else "Pe an"}"><strong>{eur_c(lg, annuo + meta * n)}</strong></td>'
                     f'<td data-l="{"На місяць, із 12" if uk else "Pe lună, din 12"}">{eur_c(lg, round((annuo + meta * n) / 12))}</td></tr>')
    if uk:
        cap, th = f"Мінімальний дохід {anno} для carta di soggiorno (дозвіл ЄС для довгострокових резидентів)", ("Для кого carta", "Осіб", "Мінімальний дохід на рік", "На місяць, із 12 місяців")
    else:
        cap, th = f"Venitul minim {anno} pentru carta di soggiorno (permis UE pe termen lung)", ("Pentru cine este carta", "Persoane", "Venit minim pe an", "Pe lună, din 12 luni")
    return (f'<div class="tab-wrap rc-tab"><table class="conf"><caption class="small">{cap}</caption>'
            f'<thead><tr>{"".join(f"<th scope=\"col\">{x}</th>" for x in th)}</tr></thead><tbody>{"".join(righe)}</tbody></table></div>')


def pagina_redditi(G, lg):
    uk = H(lg)
    c, ca = G.REDDITI["cittadinanza"], G.REDDITI["carta_soggiorno"]
    Fr = {**c["fonti"], **ca["fonti"]}
    A = G.RICONG["assegno_sociale"]
    anno = G.RICONG["anno"]
    cent = G.cent
    solo, con, fig = cent(c["solo"]), cent(c["con_coniuge"]), cent(c["per_figlio"])
    annuo = cent(A["annuo"])
    meta = annuo // 2
    v = min(f["verificato_il"] for f in Fr.values())
    anni_tre = num(" ".join(x["testo"] for x in G.REDDITI["citazioni"]), r"negli ultimi (tre) anni")
    anni_carta = num(" ".join(x["testo"] for x in G.REDDITI["citazioni"] if x["fonte"] == "tu9"), r"da almeno (cinque) anni")
    circ = num(A["fonte"], r"circolare n\. (\d+)")
    circ_d = data(lg, iso_it(A["fonte"]))
    vad_d = data(lg, iso_it(Fr["vademecum"]["nome"]))
    perc = f"{lg}/{LG.GUIDE[lg][5][0]}"
    E = lambda x: eur_c(lg, x)  # noqa: E731

    def src(*k, extra=""):
        return fonte(G, lg, " · ".join(a(Fr[x]["url"], Fr[x]["breve"]) for x in k) + extra, max(Fr[x]["verificato_il"] for x in k), fonti_parola(lg, len(k) + bool(extra)))

    if uk:
        inps = f' · соціальна допомога {anno}: {a(A["url"], f"INPS, циркуляр № {circ} від {circ_d}")} ({a(A["url_allegato"], "таблиця A")})'
    else:
        inps = f' · alocația socială {anno}: {a(A["url"], f"INPS, circulara nr. {circ} din {circ_d}")} ({a(A["url_allegato"], "tabelul A")})'
    ex3a, ex3b = G.calcola_redditi(True, 1, 0)["cittadinanza"]["soglia"], G.calcola_redditi(False, 2, 0)["cittadinanza"]["soglia"]
    ex4a = G.calcola_redditi(True, 2, 0)["cittadinanza"]["soglia"]
    righe_c = []
    for n in range(0, 5):
        etich = (f"{n} {pl_uk(n, 'дитина', 'дитини', 'дітей')} на утриманні" if uk else f"{n} {pl_ro(n, 'copil', 'copii')} în întreținere")
        righe_c.append(f'<tr><td><strong>{etich}</strong></td>'
                       f'<td data-l="{"Без чоловіка/дружини" if uk else "Fără soț/soție"}">{E(G.calcola_redditi(False, n, 0)["cittadinanza"]["soglia"])}</td>'
                       f'<td data-l="{"З чоловіком/дружиною на утриманні" if uk else "Cu soț/soție în întreținere"}">{E(G.calcola_redditi(True, n, 0)["cittadinanza"]["soglia"])}</td></tr>')
    if uk:
        th_c = ("Діти (або інші члени родини) на утриманні", "Без чоловіка/дружини", "З чоловіком/дружиною на утриманні")
        cap_c = "Мінімальний оподатковуваний дохід на рік для громадянства за проживанням"
    else:
        th_c = ("Copii (sau alți membri de familie) în întreținere", "Fără soț/soție", "Cu soț/soție în întreținere")
        cap_c = "Venitul impozabil minim pe an pentru cetățenia prin rezidență"
    tab_c = (f'<div class="tab-wrap rc-tab"><table class="conf"><caption class="small">{cap_c}</caption>'
             f'<thead><tr>{"".join(f"<th scope=\"col\">{x}</th>" for x in th_c)}</tr></thead><tbody>{"".join(righe_c)}</tbody></table></div>')
    js_soglie = json.dumps({"solo": solo, "conCon": con, "figlio": fig, "annuo": annuo})
    if uk:
        faq = [
            (f"Який мінімальний дохід потрібен для громадянства Італії у {anno} році?",
             f"Для громадянства за проживанням потрібно щонайменше {E(solo)} оподатковуваного доходу на рік, якщо ви самі, {E(con)} з чоловіком або дружиною на утриманні, і ще {E(fig)} за кожну дитину "
             f"чи іншого члена родини на утриманні. Ці пороги Міністерство внутрішніх справ записало у Vademecum від {vad_d}; щороку вони не змінюються."),
            ("Дохід для громадянства — брутто чи нетто?",
             "Зараховується оподатковуваний дохід IRPEF, задекларований в Італії. У декларації 730 це «Reddito imponibile» у розділі «Prospetto di liquidazione», як пояснює Префектура. Це не ваша зарплата «на руки»."),
            ("Який дохід потрібен для громадянства на 3 або 4 особи?",
             f"3 особи: з чоловіком/дружиною і 1 дитиною на утриманні — {E(ex3a)}, або самі з 2 дітьми на утриманні — {E(ex3b)}. 4 особи (ви, чоловік/дружина і 2 дитини на утриманні): {E(ex4a)}. Суми на рік."),
            ("Чи зараховується дохід чоловіка, дружини чи партнера?",
             "Так — чоловіка чи дружини, партнера в цивільному союзі та інших членів родини, названих у ст. 433 Цивільного кодексу. За Vademecum Міністерства дохід партнера без юридичного зв’язку не зараховується, "
             "навіть якщо є спільні діти, як і дохід чоловіка чи дружини, які живуть за кордоном. Партнер із договором про спільне проживання зараховується."),
            (f"Який дохід потрібен для carta di soggiorno у {anno} році?",
             f"Щонайменше соціальна допомога {anno} року (assegno sociale): {E(annuo)} на рік лише для вас. Якщо подаєте заяву й на членів родини, додайте половину ({E(meta)}) за кожного: "
             f"для 4 осіб (ви і 3 члени родини) — {E(annuo + meta * 3)}. Рішення ухвалює Квестура."),
        ]
        h1 = f"Дохід для громадянства Італії та carta di soggiorno {anno}"
        lead = (f"Згідно з Vademecum Міністерства внутрішніх справ від {vad_d} (прочитано {data(lg, v)}), для громадянства Італії за проживанням потрібен оподатковуваний дохід щонайменше {E(solo)} на рік, якщо ви самі, "
                f"{E(con)} з чоловіком або дружиною на утриманні і ще {E(fig)} за кожну дитину на утриманні. Для carta di soggiorno потрібна щонайменше соціальна допомога {anno} року — {E(annuo)} на рік (ст. 9 Зведеного закону про імміграцію).")
        occh = f"Офіційні джерела · {data(lg, v)}"
        slot = (f'<div class="slot"><div class="r-et">{G.ic("scudo")}Громадянство (Префектура)</div><div class="r-data">{E(solo)} <small>на рік</small></div>'
                f'<div class="r-cosa">самі · {E(con)} з чоловіком/дружиною на утриманні · + {E(fig)} за дитину</div></div>'
                f'<div class="slot"><div class="r-et">{G.ic("doc")}Carta di soggiorno (Квестура)</div><div class="r-data">{E(annuo)} <small>на рік</small></div>'
                f'<div class="r-cosa">лише для вас · + {E(meta)} за кожного члена родини</div></div>'
                f'<div class="r-piede"><a href="#calculate">Перевірте дохід вашої родини {G.ic("freccia")}</a><span>{G.ic("doc")}Джерела: Міністерство внутрішніх справ, Префектура, закон про імміграцію, INPS</span></div>')
        av = ("Ця сторінка порівнює ваш дохід з офіційними порогами, але це не юридична консультація. <strong>Щодо громадянства рішення ухвалює Префектура; щодо carta di soggiorno — Квестура.</strong> "
              "Щодо вашого випадку звертайтеся туди або до патронату (patronato).")
        f_ = ("Калькулятор: ви вище чи нижче порогів?", "Мій чоловік/дружина (або партнер у цивільному союзі) у мене на утриманні",
              "Якщо чоловік чи дружина має власний дохід і не перебуває на утриманні, не ставте позначку, а додайте його оподатковуваний дохід до вашого в полі нижче (вищий поріг діє лише «за наявності чоловіка/дружини на утриманні», пише Vademecum).",
              "Діти (або інші члени родини) на утриманні", "Оподатковуваний дохід родини на рік, у євро", "наприклад 12\u00a0500", "Порівняти з порогами",
              "Напишіть дохід у євро, наприклад 12\u00a0500 або 12500,50.")
        quattordici = f"Якщо у вас 2 або більше дітей до 14 років, для возз’єднання сім’ї закон вимагає щонайменше {E(annuo * 2)} на рік: щодо carta di soggiorno запитайте в Квестурі, чи це стосується і вас."
        solo_ufficiali = ("Калькулятор використовує лише офіційні пороги. Він не знає, чи ваш дохід «оподатковуваний», за які роки він і чи в порядку ваші документи: "
                          "<strong>рішення ухвалює Префектура (громадянство) або Квестура (carta di soggiorno)</strong>. "
                          f'Щоб привезти родину до Італії, див. <a href="../{LG.GUIDE[lg][8][0]}">дохід для возз’єднання сім’ї</a>.')
        privato = "Розрахунок відбувається у вашому браузері: ми нічого не зберігаємо."
        h2c = "Громадянство за проживанням: який дохід"
        p2c = (f"Міністерство внутрішніх справ використовує як пороги межі доходу для звільнення пенсіонерів від медичних зборів: <strong>{E(solo)}</strong>, якщо ви самі, "
               f"<strong>{E(con)}</strong> з чоловіком або дружиною на утриманні і <strong>ще {E(fig)}</strong> за кожну дитину чи члена родини на утриманні.")
        p5 = f"Для 5 і більше дітей: додайте {E(fig)} за кожну дитину. Цифри в таблиці такі самі, як у PDF Префектури."
        h3a = "Який дохід зараховується: брутто чи нетто?"
        p3a = (f"Зараховується лише <strong>оподатковуваний дохід IRPEF, задекларований в Італії</strong> за <strong>останні {anni_tre} роки</strong>; дохід, отриманий за кордоном, не зараховується. У декларації 730 це «Reddito imponibile» у «Prospetto di liquidazione»; "
               "для декларації «Redditi PF» і «Certificazione Unica» Префектура пояснює, які рядки додавати.")
        h3b = "Дохід родини"
        p3b = ("Можна додати дохід членів родини, названих у ст. 433 Цивільного кодексу, які записані у вашому складі родини (stato di famiglia): чоловік чи дружина (або партнер у цивільному союзі чи партнер із письмовим договором про спільне проживання), діти, батьки, зяті й невістки, тесті й свекри, брати й сестри. "
               "<strong>Не зараховується</strong>, за Vademecum: партнер без юридичного зв’язку (навіть зі спільними дітьми), вітчим чи мачуха, чоловік або дружина, які живуть за кордоном.")
        h3c = "Що не вважається доходом"
        nonred = ["«reddito» або «pensione di cittadinanza»;", "гроші на банківському рахунку;", "пенсія, отримана й оподаткована за кордоном;", "допомога по безробіттю (NASpI), хоч вона й оподатковується."]
        p3c = ("Якщо ваш дохід знизився в якийсь один рік, Vademecum пише, що Префектура може оцінити його «in via equitativa» (за справедливістю). Але заяву із задекларованим доходом нижче порогів можуть <strong>одразу відхилити онлайн</strong>, "
               "а дохід треба <strong>зберігати до присяги</strong>.")
        h2k = "Carta di soggiorno (дозвіл ЄС для довгострокових резидентів): який дохід"
        p2k = (f"Закон вимагає щонайменше <strong>{anni_carta} років</strong> із дозволом на проживання і дохід <strong>не нижчий за соціальну допомогу</strong>: у {anno} році це <strong>{E(annuo)} на рік</strong>. "
               f"Якщо ви подаєте заяву й на членів родини, дохід рахують за правилом возз’єднання сім’ї: соціальна допомога <strong>+ {E(meta)} за кожного члена родини</strong>. Також потрібне придатне житло.")
        p_mese = ("«На місяць» — лише для порівняння: закон говорить про річний дохід. Які документи й доходи дійсні, вирішує Квестура. "
                  f'<a href="../{LG.GUIDE[lg][7][0]}">Усі вимоги до carta di soggiorno</a>.')
        h2n = "Що далі"
        titolo = G.titolo_pagina(f"Дохід для громадянства Італії {anno}: калькулятор", f"Дохід для громадянства Італії {anno}")
        descr = G.descrizione_pagina(f"Дохід для громадянства Італії {anno}: {E(solo)} самі, {E(con)} у шлюбі, + {E(fig)} за дитину. Carta di soggiorno: {E(annuo)}. Калькулятор.",
                                     f"Дохід для громадянства Італії {anno}: {E(solo)} самі, {E(con)} у шлюбі, + {E(fig)} за дитину. Калькулятор.")
        bric = "Дохід"
    else:
        faq = [
            (f"Care este venitul minim pentru cetățenia italiană în {anno}?",
             f"Pentru cetățenia prin rezidență trebuie un venit impozabil de cel puțin {E(solo)} pe an dacă sunteți singur(ă), {E(con)} cu soțul sau soția în întreținere, plus {E(fig)} pentru fiecare copil "
             f"sau alt membru de familie în întreținere. Sunt pragurile scrise de Ministerul de Interne în Vademecum-ul din {vad_d}; nu se schimbă în fiecare an."),
            ("Venitul pentru cetățenie este brut sau net?",
             "Contează venitul impozabil IRPEF declarat în Italia. În declarația 730 este «Reddito imponibile» din «Prospetto di liquidazione», cum explică Prefectura. Nu este salariul net."),
            ("Ce venit trebuie pentru cetățenie pentru 3 sau 4 persoane?",
             f"3 persoane: cu soț/soție și 1 copil în întreținere {E(ex3a)}, sau singur(ă) cu 2 copii în întreținere {E(ex3b)}. 4 persoane (dumneavoastră, soțul/soția și 2 copii în întreținere): {E(ex4a)}. Sume pe an."),
            ("Contează venitul soțului, al soției sau al partenerului?",
             "Da pentru soț sau soție, partenerul din uniunea civilă și ceilalți membri de familie numiți la art. 433 din Codul civil. Potrivit Vademecum-ului Ministerului, venitul unui partener fără legătură juridică nu contează, "
             "nici cu copii împreună, nici cel al soțului sau soției care locuiește în străinătate. Contează partenerul cu contract de conviețuire."),
            (f"Ce venit trebuie pentru carta di soggiorno în {anno}?",
             f"Carta di soggiorno (permisul UE pe termen lung) privește doar cetățenii din afara UE, de exemplu din Republica Moldova. Trebuie cel puțin alocația socială {anno} (assegno sociale): {E(annuo)} pe an doar pentru dumneavoastră. "
             f"Dacă cereți și pentru membrii familiei, adăugați jumătate ({E(meta)}) pentru fiecare: pentru 4 persoane (dumneavoastră și 3 membri de familie) {E(annuo + meta * 3)}. Decide Chestura."),
        ]
        h1 = f"Venitul minim pentru cetățenia italiană și carta di soggiorno {anno}"
        lead = (f"Potrivit Vademecum-ului Ministerului de Interne din {vad_d} (citit la {data(lg, v)}), cetățenia italiană prin rezidență cere un venit impozabil de cel puțin {E(solo)} pe an dacă sunteți singur(ă), "
                f"{E(con)} cu soțul sau soția în întreținere și încă {E(fig)} pentru fiecare copil în întreținere. Pentru carta di soggiorno (doar cetățenii din afara UE) trebuie cel puțin alocația socială {anno}, {E(annuo)} pe an (art. 9 din Textul unic privind imigrația).")
        occh = f"Surse oficiale · {data(lg, v)}"
        slot = (f'<div class="slot"><div class="r-et">{G.ic("scudo")}Cetățenie (Prefectura)</div><div class="r-data">{E(solo)} <small>pe an</small></div>'
                f'<div class="r-cosa">singur(ă) · {E(con)} cu soț/soție în întreținere · + {E(fig)} pe copil</div></div>'
                f'<div class="slot"><div class="r-et">{G.ic("doc")}Carta di soggiorno (Chestura)</div><div class="r-data">{E(annuo)} <small>pe an</small></div>'
                f'<div class="r-cosa">doar pentru dumneavoastră · + {E(meta)} pentru fiecare membru de familie</div></div>'
                f'<div class="r-piede"><a href="#calculate">Verificați venitul familiei {G.ic("freccia")}</a><span>{G.ic("doc")}Surse: Ministerul de Interne, Prefectura, legea imigrației, INPS</span></div>')
        av = ("Această pagină compară venitul dumneavoastră cu pragurile oficiale, dar nu este consultanță juridică. <strong>Pentru cetățenie decide Prefectura; pentru carta di soggiorno decide Chestura.</strong> "
              "Pentru cazul dumneavoastră întrebați acolo sau la un patronato.")
        f_ = ("Calculator: sunteți peste sau sub praguri?", "Soțul/soția (sau partenerul din uniunea civilă) este în întreținerea mea",
              "Dacă soțul sau soția are venit propriu și nu este în întreținerea dumneavoastră, nu bifați căsuța și adăugați venitul său impozabil la al dumneavoastră în câmpul de mai jos (pragul mai mare se aplică doar «în prezența soțului în întreținere», scrie Vademecum-ul).",
              "Copii (sau alți membri de familie) în întreținere", "Venitul impozabil al familiei pe an, în euro", "de exemplu 12.500", "Comparați cu pragurile",
              "Scrieți venitul în euro, de exemplu 12.500 sau 12500,50.")
        quattordici = f"Cu 2 sau mai mulți copii sub 14 ani, pentru reîntregirea familiei legea cere cel puțin {E(annuo * 2)} pe an: pentru carta di soggiorno întrebați Chestura dacă se aplică și în cazul dumneavoastră."
        solo_ufficiali = ("Calculatorul folosește doar pragurile oficiale. Nu poate ști dacă venitul dumneavoastră este «impozabil», la ce ani se referă sau dacă actele sunt în regulă: "
                          "<strong>decide Prefectura (cetățenia) sau Chestura (carta di soggiorno)</strong>. Rândurile despre carta di soggiorno privesc doar cetățenii din afara UE: cetățenii români nu au nevoie de ea.")
        privato = "Calculul rămâne în browserul dumneavoastră: nu salvăm nimic."
        h2c = "Cetățenia prin rezidență: ce venit"
        p2c = (f"Ministerul de Interne folosește ca praguri limitele de venit pentru scutirea pensionarilor de taxele medicale: <strong>{E(solo)}</strong> dacă sunteți singur(ă), "
               f"<strong>{E(con)}</strong> cu soțul sau soția în întreținere și <strong>încă {E(fig)}</strong> pentru fiecare copil sau membru de familie în întreținere.")
        p5 = f"Pentru 5 sau mai mulți copii: adăugați {E(fig)} pentru fiecare copil. Cifrele din tabel sunt aceleași ca în PDF-ul Prefecturii."
        h3a = "Ce venit contează: brut sau net?"
        p3a = (f"Contează doar <strong>venitul impozabil IRPEF declarat în Italia</strong> în <strong>ultimii {anni_tre} ani</strong>; venitul câștigat în străinătate nu contează. În declarația 730 este «Reddito imponibile» din «Prospetto di liquidazione»; "
               "pentru declarația «Redditi PF» și pentru «Certificazione Unica» Prefectura explică ce rânduri se adună.")
        h3b = "Venitul familiei"
        p3b = ("Puteți adăuga venitul membrilor de familie numiți la art. 433 din Codul civil care sunt în certificatul de familie (stato di famiglia): soțul sau soția (ori partenerul din uniunea civilă sau partenerul cu contract scris de conviețuire), copiii, părinții, ginerii și nurorile, socrii, frații și surorile. "
               "<strong>Nu contează</strong>, potrivit Vademecum-ului: partenerul fără legătură juridică (nici cu copii împreună), părintele vitreg, soțul sau soția care locuiește în străinătate.")
        h3c = "Ce nu se consideră venit"
        nonred = ["«reddito» sau «pensione di cittadinanza»;", "banii din contul bancar;", "o pensie primită și impozitată în străinătate;", "indemnizația de șomaj (NASpI), deși este impozitată."]
        p3c = ("Dacă venitul scade într-un singur an, Vademecum-ul spune că Prefectura îl poate evalua «in via equitativa» (echitabil). Dar o cerere cu venit declarat sub praguri poate fi <strong>respinsă online imediat</strong>, "
               "iar venitul trebuie <strong>păstrat până la jurământ</strong>.")
        h2k = "Carta di soggiorno (permisul UE pe termen lung, doar pentru cetățenii din afara UE): ce venit"
        p2k = (f"Legea cere cel puțin <strong>{anni_carta} ani</strong> cu permis de ședere și un venit <strong>nu mai mic decât alocația socială</strong>: în {anno} înseamnă <strong>{E(annuo)} pe an</strong>. "
               f"Dacă cereți și pentru membrii familiei, venitul urmează regula reîntregirii familiei: alocația socială <strong>+ {E(meta)} pentru fiecare membru de familie</strong>. Este nevoie și de o locuință corespunzătoare.")
        p_mese = ("«Pe lună» este doar un ajutor pentru comparație: legea vorbește de venit anual. Chestura decide ce acte și ce venituri sunt valabile. "
                  f'<a href="../{LG.GUIDE[lg][8][0]}">Toate cerințele pentru carta di soggiorno</a>.')
        h2n = "Pașii următori"
        titolo = G.titolo_pagina(f"Venit minim pentru cetățenia italiană {anno}: calculator", f"Venit minim cetățenie italiană {anno}")
        descr = G.descrizione_pagina(f"Venitul minim pentru cetățenia italiană {anno}: {E(solo)} singur, {E(con)} cu soț/soție, + {E(fig)} pe copil. Carta di soggiorno: {E(annuo)}. Calculator.")
        bric = "Venit minim"
    faq_html, ld = LG.faq_blocco(G, [(escape(q), escape(t)) for q, t in faq])
    corpo = f"""<section class="hero">
{LG.briciole(lg, "../", (bric, None))}
<span class="occhiello">{G.ic("euro")}{occh}</span>
<h1>{h1}</h1>
<p class="lead">{lead}</p>
<div class="risposta">{slot}</div>
</section>
{G.avviso(av)}
<section>
<h2 id="calculate">{G.ic("lista")}{f_[0]}</h2>
<form class="form calc card" id="calc-redditi" novalidate>
<label class="check"><input type="checkbox" name="coniuge"><span>{f_[1]}</span></label>
<p class="small">{f_[2]}</p>
<label>{f_[3]}<input type="number" name="figli" min="0" max="20" value="0" inputmode="numeric"></label>
<label>{f_[4]}<input type="text" name="reddito" inputmode="decimal" placeholder="{f_[5]}" autocomplete="off"></label>
<button class="btn" type="submit">{G.ic("euro")}{f_[6]}</button>
<p class="errore" data-errore hidden>{f_[7]}</p>
</form>
<div class="calc-esito" id="calc-esito" aria-live="polite" hidden>
<div data-r="cittadinanza" hidden><div class="c-tit"></div><div class="c-soglia"></div><div class="c-esito"></div><div class="c-chi small"></div></div>
<div data-r="carta_solo" hidden><div class="c-tit"></div><div class="c-soglia"></div><div class="c-esito"></div><div class="c-chi small"></div></div>
<div data-r="carta_famiglia" hidden><div class="c-tit"></div><div class="c-soglia"></div><div class="c-esito"></div><div class="c-chi small"></div></div>
<p class="small" data-quattordici hidden>{quattordici}</p>
<p class="small">{solo_ufficiali}</p>
</div>
<p class="small">{privato}</p>
</section>
<section>
<h2 id="citizenship">{G.ic("scudo")}{h2c}</h2>
<p>{p2c}</p>
{src("vademecum", "pdf_prefettura")}
{tab_c}
<p class="small">{p5}</p>
<h3 id="which-income">{h3a}</h3>
<p>{p3a}</p>
{src("pdf_prefettura", "vademecum")}
<h3 id="family">{h3b}</h3>
<p>{p3b}</p>
<h3 id="not-income">{h3c}</h3>
<ul>{"".join(f"<li>{x}</li>" for x in nonred)}</ul>
<p>{p3c}</p>
{src("vademecum")}
</section>
<section>
<h2 id="carta-di-soggiorno">{G.ic("doc")}{h2k}</h2>
<p>{p2k}</p>
{src("tu9", extra=inps)}
{tabella_carta(G, lg)}
<p class="small">{p_mese}</p>
</section>
{LG.faq_sezione(G, lg, faq_html)}
<div class="due">
<section><h2>{G.ic("lista")}{h2n}</h2>{LG.griglia_guide(G, lg, "../", salta=LG.GUIDE[lg][5][0])}</section>
<aside>{LG.modulo(G, lg, "../../")}</aside>
</div>
{LG.altre_lingue(G, lg, perc, "../../")}
<script>{js_calcolo(G, lg, js_soglie)}</script>"""
    LG.pagina_l(G, lg, perc, titolo, descr, corpo, jsonld=ld)


# ---------------------------------------------------------------- domanda di cittadinanza
GIORNI_ACC = {"uk": {"lunedì": "понеділок", "martedì": "вівторок", "mercoledì": "середу", "giovedì": "четвер", "venerdì": "п’ятницю", "sabato": "суботу", "domenica": "неділю"},
              "ro": {"lunedì": "lunea", "martedì": "marțea", "mercoledì": "miercurea", "giovedì": "joia", "venerdì": "vinerea", "sabato": "sâmbăta", "domenica": "duminica"}}


def pagina_domanda(G, lg):
    import re
    uk = H(lg)
    C = G.CITT
    Fc, po = C["fonti"], C["polo_orienta"]
    v = max(f["verificato_il"] for f in Fc.values())
    contrib = eur(lg, C["contributo_eur"], False)
    citaz = " ".join(x["testo"] for x in C["citazioni"])
    m24 = num(citaz, r"(ventiquattro) mesi")
    m36 = num(citaz, r"massimo di (trentasei) mesi")
    dal = data(lg, iso_it(num(citaz, r"a partire dal (\d{1,2} \w+ \d{4})")))
    mb1 = num(citaz, r"dimensione di (\d+) MB")
    mb2 = num(citaz, r"complessivo di (\d+) ?MB")
    giorni = num(po["giorni"], r"^(.*) dalle")
    gg = [GIORNI_ACC[lg][x] for x in re.split(r", | e ", giorni)]
    giorni_l = (", ".join(gg[:-1]) + (" та " if uk else " și ") + gg[-1]) if len(gg) > 1 else gg[0]
    ore = re.findall(r"\d{1,2}\.\d{2}", po["giorni"])
    if len(ore) != 2:
        raise SystemExit("genera_lingue: orari Polo Orienta non letti")
    ue, extra = LG.anni_residenza()
    res = LG.fonte_l("dlci_residenza")
    con_pagina = sorted((sl for sl in G.PREF if G.ha_pagina_pref(sl)), key=lambda x: G.PREF[x]["nome"])
    pref_link = ", ".join(f'<a href="../../cittadinanza/{G.pref_url(sl)}/" hreflang="it" lang="it">{escape(G.PREF[sl]["nome"])}</a>' for sl in con_pagina)
    perc = f"{lg}/{LG.GUIDE[lg][6][0]}"
    g_esame, g_esoneri, g_redditi = LG.GUIDE[lg][1][0], LG.GUIDE[lg][4][0], LG.GUIDE[lg][5][0]
    if uk:
        gen = G.PREF_LOC["prefetture"]["genova"]
        punto = next(x for x in gen["punti"] if x["titolo"] == "Cittadini ucraini")
        fine_esonero = data(lg, iso_it(punto["testo"]))
        faq = [
            ("Скільки років треба прожити в Італії, щоб отримати громадянство?",
             f"За ст. 9 Закону 91/1992 (сторінка Міністерства внутрішніх справ), іноземець із країни поза ЄС, зокрема громадянин України, може подати заяву після щонайменше {extra} років законного проживання в Італії; "
             f"громадянин країни ЄС — після {ue} років. Закон передбачає й інші випадки (наприклад, для народжених в Італії). Рішення ухвалює Префектура."),
            ("Де подавати заяву на громадянство Італії?",
             "Лише онлайн, на Portale Servizi Міністерства внутрішніх справ (ALI Cittadinanza), через SPID або CIE. Потім заяву розглядає Префектура провінції, де ви живете."),
            ("Скільки коштує заява на громадянство?",
             f"Збір (contributo) — {contrib}: квитанцію про оплату додають до заяви. Також потрібні реквізити електронної гербової марки (marca da bollo telematica)."),
            ("Скільки триває розгляд заяви на громадянство Італії?",
             f"Для заяв, поданих починаючи з {dal}, закон (ст. 9-ter Закону 91/1992) встановлює строк {m24} {pl_uk(m24, 'місяць', 'місяці', 'місяців')}, який можна продовжити максимум до {m36} {pl_uk(m36, 'місяця', 'місяців', 'місяців')} від дати подання. "
             "Це строк за законом, а не прогноз для вашої заяви."),
            ("Чи потрібні громадянам України свідоцтво про народження і довідка про несудимість?",
             f"Так. Префектура Генуї пише, що звільнення громадян України від документів країни походження припинилося {fine_esonero}: свідоцтво про народження і довідка про несудимість потрібні й для заяв, які ще розглядаються. "
             "Рішення ухвалює Префектура."),
        ]
        h1 = "Громадянство Італії за проживанням: роки, документи, заява онлайн"
        lead = (f"За даними Міністерства внутрішніх справ (сторінку прочитано {data(lg, v)}), заяву на громадянство Італії подають лише онлайн, на Portale Servizi Міністерства (ALI Cittadinanza) через SPID або CIE, а збір становить {contrib}. "
                f"Іноземцю з країни поза ЄС, зокрема громадянину України, закон дозволяє подати заяву після щонайменше {extra} років законного проживання в Італії.")
        occh = f"Після іспиту B1 · джерела прочитано {data(lg, v)}"
        slot = (f'<div class="slot"><div class="r-et">{G.ic("orologio")}Проживання</div><div class="r-data">{extra} років <small>щонайменше</small></div><div class="r-cosa">для громадян країн поза ЄС (ст. 9 Закону 91/1992)</div></div>'
                f'<div class="slot"><div class="r-et">{G.ic("euro")}Збір</div><div class="r-data">{contrib} <small>contributo</small></div><div class="r-cosa">онлайн, через SPID або CIE, плюс електронна гербова марка</div></div>'
                f'<div class="r-piede"><a href="#steps">Кроки {G.ic("freccia")}</a><span>{G.ic("doc")}Джерела: Міністерство внутрішніх справ і Префектури</span></div>')
        av = ("Цей сайт не належить Міністерству чи Префектурам і не консультує щодо вашої заяви. <strong>Рішення ухвалює Префектура.</strong> "
              "Щодо вашого випадку пишіть до відділу громадянства Префектури або зверніться до патронату (patronato).")
        h2y = "Скільки років проживання потрібно"
        py = (f"Стаття 9 Закону 91/1992, як її наводить Департамент громадянських свобод та імміграції Міністерства внутрішніх справ: громадянство можна надати "
              f"<strong>іноземцю, який законно проживає в Італії щонайменше {extra} років</strong>, і <strong>громадянину країни ЄС — після {ue} років</strong>. "
              "Закон називає й інші випадки (наприклад, народжені в Італії, усиновлені, особи без громадянства). Чи враховується ваш період проживання, вирішує Префектура.")
        h2s = "Як подати заяву, крок за кроком"
        passi = [f'<strong>Лише онлайн</strong>, на {a(Fc["portale"]["url"], "Portale Servizi Міністерства внутрішніх справ")} (ALI Cittadinanza), через <strong>SPID або CIE</strong>.',
                 f'<strong>Документи</strong>: документ, що посвідчує особу, свідоцтво про народження і довідка про несудимість із країни походження, сертифікат з італійської рівня <a href="../{g_esame}">B1</a> або вище (якщо ви не <a href="../{g_esoneri}">звільнені</a>), квитанція про сплату збору, реквізити електронної гербової марки.',
                 f"<strong>Збір {contrib}</strong>: додайте квитанцію про оплату.",
                 f'<strong>Дохід</strong>: потрібен щонайменше <a href="../{g_redditi}">поріг Міністерства</a> (для громадянства за проживанням).',
                 "<strong>Після подання</strong>: заява отримує номер K10; її стан перевіряють онлайн з тими самими обліковими даними."]
        ucr = (f"<strong>Для громадян України.</strong> Префектура Генуї пише, що звільнення громадян України від документів країни походження <strong>припинилося {fine_esonero}</strong>: "
               "свідоцтво про народження і довідка про несудимість потрібні й для заяв, що ще розглядаються; хто має заяву в процесі, може надіслати їх через PEC, вказавши номер K10 у темі листа. "
               f'Деталі — на <a href="../../cittadinanza/genova/" hreflang="it" lang="it">нашій сторінці про Префектуру Генуї (італійською)</a>. Запитайте у своїй Префектурі.')
        h2a = "Після подання: строк і стан заяви"
        dopo = [f"<strong>Строк:</strong> для заяв, поданих починаючи з {dal}, закон встановлює <strong>{m24} {pl_uk(m24, 'місяць', 'місяці', 'місяців')}, із можливістю продовження максимум до {m36} {pl_uk(m36, 'місяця', 'місяців', 'місяців')}</strong> від дати подання ({a(Fc['legge']['url'], 'ст. 9-ter Закону 91/1992')}). Це строк за законом, а не прогноз: ваша заява може тривати інакше.",
                "<strong>Стан:</strong> онлайн, з тими самими обліковими даними, що й для подання.",
                f'<strong>Листування:</strong> Міністерство вказує адресу PEC <a href="mailto:{C["pec_ministero"]}">{C["pec_ministero"]}</a>, одна заява на лист, номер K10 у темі; вкладення у PDF, TIFF або JPEG до {mb1} МБ кожне і до {mb2} МБ загалом.',
                f'<strong>Polo Orienta</strong> (контакт-центр Міністерства): тел. {po["telefono"]}, у {giorni_l} з {ore[0]} до {ore[1]}, PEC <a href="mailto:{po["pec"]}">{po["pec"]}</a>. Тримайте під рукою номер K10 і документ, що посвідчує особу.']
        h2p = "Ваша Префектура"
        pp = (f'Email і PEC відділів громадянства всіх {len(G.PREF)} Префектур — на нашій італійській сторінці: <a href="../../cittadinanza/#elenco" hreflang="it" lang="it">le {len(G.PREF)} Prefetture: contatti</a>. '
              f"Для цих Префектур ми наводимо також те, що пише їхня власна сторінка (контакти, години, місцеві правила), італійською: {pref_link}.")
        h2e, pe = "Ще немає сертифіката B1?", (f'Див. <a href="../{LG.GUIDE[lg][0][0]}">усі дати іспиту</a>, <a href="../{LG.GUIDE[lg][2][0]}">скільки він коштує</a> і <a href="../{g_esoneri}">хто звільнений</a>.')
        titolo = G.titolo_pagina("Громадянство Італії для українців: роки, документи, заява")
        descr = G.descrizione_pagina(f"Громадянство Італії українською: {extra} років проживання, заява онлайн на ALI через SPID або CIE, збір {contrib}, строк {m24}-{m36} місяців, документи.")
        bric = "Громадянство"
        chi_dec = "Префектура"
    else:
        faq = [
            ("După câți ani de rezidență pot cere cetățenia italiană ca cetățean român?",
             f"Potrivit art. 9 din Legea 91/1992 (pagina Ministerului de Interne), cetățeanul unui stat membru UE, deci și cetățeanul român, poate cere cetățenia după cel puțin {ue} ani de rezidență legală în Italia. "
             f"Un străin din afara UE, de exemplu din Republica Moldova, după cel puțin {extra} ani. Decide Prefectura."),
            ("Unde se depune cererea de cetățenie italiană?",
             "Doar online, pe Portale Servizi al Ministerului de Interne (ALI Cittadinanza), cu SPID sau CIE. Cererea este apoi analizată de Prefectura provinciei în care locuiți."),
            ("Cât costă cererea de cetățenie?",
             f"Contribuția (contributo) este de {contrib}: atașați chitanța de plată la cerere. Mai sunt necesare datele timbrului fiscal electronic (marca da bollo telematica)."),
            ("Cât durează cetățenia italiană?",
             f"Pentru cererile depuse începând cu {dal}, legea (art. 9-ter din Legea 91/1992) stabilește un termen de {m24} de luni, care poate fi prelungit până la maximum {m36} de luni de la data cererii. "
             "Este un termen legal, nu o estimare pentru cererea dumneavoastră."),
            ("Și pentru cetățenia prin căsătorie trebuie examenul B1?",
             "Da. Legea cere cunoașterea limbii italiene la nivel B1 sau superior atât pentru cetățenia prin căsătorie, cât și pentru cea prin rezidență (articolele 5 și 9 din Legea 91/1992), și pentru cetățenii UE. Decide Prefectura."),
        ]
        h1 = "Cetățenia italiană prin rezidență pentru români: ani, acte, cerere online"
        lead = (f"Potrivit Ministerului de Interne (pagină citită la {data(lg, v)}), cererea de cetățenie italiană se depune doar online, pe Portale Servizi al Ministerului (ALI Cittadinanza), cu SPID sau CIE, iar contribuția este de {contrib}. "
                f"Pentru cetățenii UE, deci și pentru români, legea cere cel puțin {ue} ani de rezidență legală în Italia.")
        occh = f"După examenul B1 · surse citite la {data(lg, v)}"
        slot = (f'<div class="slot"><div class="r-et">{G.ic("orologio")}Rezidență</div><div class="r-data">{ue} ani <small>cel puțin</small></div><div class="r-cosa">pentru cetățenii UE (art. 9 din Legea 91/1992)</div></div>'
                f'<div class="slot"><div class="r-et">{G.ic("euro")}Contribuție</div><div class="r-data">{contrib} <small>contributo</small></div><div class="r-cosa">online, cu SPID sau CIE, plus timbrul fiscal electronic (marca da bollo)</div></div>'
                f'<div class="r-piede"><a href="#steps">Pașii {G.ic("freccia")}</a><span>{G.ic("doc")}Surse: Ministerul de Interne și prefecturile</span></div>')
        av = ("Acest site nu aparține Ministerului sau prefecturilor și nu oferă consultanță pentru cererea dumneavoastră. <strong>Decide Prefectura.</strong> "
              "Pentru cazul dumneavoastră scrieți biroului de cetățenie al Prefecturii sau mergeți la un patronato.")
        h2y = "Câți ani de rezidență sunt necesari"
        py = (f"Articolul 9 din Legea 91/1992, așa cum îl redă Departamentul pentru libertăți civile și imigrație al Ministerului de Interne: cetățenia poate fi acordată "
              f"<strong>cetățeanului unui stat membru UE care locuiește legal în Italia de cel puțin {ue} ani</strong> (deci și românilor) și <strong>străinului din afara UE după cel puțin {extra} ani</strong> (de exemplu cetățenilor Republicii Moldova). "
              f'Legea mai numește și alte cazuri (de exemplu cei născuți în Italia, adoptații, apatrizii). Despre șederea cetățenilor UE în Italia (înscrierea la anagrafe, șederea permanentă): <a href="../{LG.GUIDE[lg][7][0]}">rezidența pentru cetățenii UE</a>. Ce perioadă de rezidență vi se recunoaște decide Prefectura.')
        h2s = "Cum depuneți cererea, pas cu pas"
        passi = [f'<strong>Doar online</strong>, pe {a(Fc["portale"]["url"], "Portale Servizi al Ministerului de Interne")} (ALI Cittadinanza), cu <strong>SPID sau CIE</strong>.',
                 f'<strong>Actele de atașat</strong>: act de identitate, certificat de naștere și cazier judiciar din țara de origine, certificat de limba italiană de nivel <a href="../{g_esame}">B1</a> sau superior (obligatoriu și pentru cetățenii UE, dacă nu sunteți <a href="../{g_esoneri}">scutit(ă)</a>), chitanța contribuției, datele timbrului fiscal electronic (marca da bollo telematica).',
                 f"<strong>Contribuția de {contrib}</strong>: atașați chitanța de plată.",
                 f'<strong>Venitul</strong>: trebuie cel puțin <a href="../{g_redditi}">pragurile Ministerului</a> (pentru cetățenia prin rezidență).',
                 "<strong>După trimitere</strong>: cererea primește un număr K10; starea ei se verifică online cu aceleași date de acces."]
        ucr = ""
        h2a = "După depunere: termen și starea cererii"
        dopo = [f"<strong>Termen:</strong> pentru cererile depuse începând cu {dal}, legea stabilește <strong>{m24} de luni, care pot fi prelungite până la maximum {m36} de luni</strong> de la data cererii ({a(Fc['legge']['url'], 'art. 9-ter din Legea 91/1992')}). Este un termen legal, nu o estimare: cererea dumneavoastră poate dura altfel.",
                "<strong>Starea:</strong> online, cu aceleași date de acces folosite la depunere.",
                f'<strong>Comunicări:</strong> Ministerul indică adresa PEC <a href="mailto:{C["pec_ministero"]}">{C["pec_ministero"]}</a>, o singură cerere pe mesaj, cu numărul K10 în subiect; atașamente în PDF, TIFF sau JPEG de maximum {mb1} MB fiecare și {mb2} MB în total.',
                f'<strong>Polo Orienta</strong> (centrul de contact al Ministerului): tel. {po["telefono"]}, {giorni_l}, între {ore[0]} și {ore[1]}, PEC <a href="mailto:{po["pec"]}">{po["pec"]}</a>. Țineți la îndemână numărul K10 și un act de identitate.']
        h2p = "Prefectura dumneavoastră"
        pp = (f'Adresele de e-mail și PEC ale birourilor de cetățenie ale tuturor celor {len(G.PREF)} de prefecturi sunt pe pagina noastră în italiană: <a href="../../cittadinanza/#elenco" hreflang="it" lang="it">le {len(G.PREF)} Prefetture: contatti</a>. '
              f"Pentru aceste prefecturi redăm și ce scrie pagina lor (contacte, program, reguli locale), în italiană: {pref_link}.")
        h2e, pe = "Nu aveți încă certificatul B1?", (f'Vedeți <a href="../{LG.GUIDE[lg][0][0]}">toate datele de examen</a>, <a href="../{LG.GUIDE[lg][2][0]}">cât costă</a> și <a href="../{g_esoneri}">cine este scutit</a>.')
        titolo = G.titolo_pagina(f"Cetățenie italiană pentru români: {ue} ani, acte, cerere online", "Cetățenie italiană pentru români: ani, acte, cerere")
        descr = G.descrizione_pagina(f"Cetățenia italiană pentru români: {ue} ani de rezidență, B1 obligatoriu, cerere online pe ALI cu SPID sau CIE, contribuție {contrib}, termen {m24}-{m36} luni.")
        bric = "Cetățenie"
        chi_dec = "Prefectura"
    faq_html, ld = LG.faq_blocco(G, [(escape(q), escape(t)) for q, t in faq])
    corpo = f"""<section class="hero">
{LG.briciole(lg, "../", (bric, None))}
<span class="occhiello">{G.ic("edificio")}{occh}</span>
<h1>{h1}</h1>
<p class="lead">{lead}</p>
<div class="risposta">{slot}</div>
</section>
{G.avviso(av)}
<section>
<h2 id="years">{G.ic("orologio")}{h2y}</h2>
<p>{py}</p>
{fonte(G, lg, a(res["url"], res["nome"]), res["verificato_il"], fonti_parola(lg, 1))}
</section>
<section>
<h2 id="steps">{G.ic("lista")}{h2s}</h2>
<ol class="passi">{"".join(f"<li><div>{x}</div></li>" for x in passi)}</ol>
{fonte(G, lg, a(Fc["domanda"]["url"], Fc["domanda"]["nome"]) + " · " + a(Fc["consulta"]["url"], Fc["consulta"]["nome"]), max(Fc["domanda"]["verificato_il"], Fc["consulta"]["verificato_il"]), fonti_parola(lg, 2))}
{f"<p>{ucr}</p>" if ucr else ""}
</section>
<section>
<h2 id="after">{G.ic("orologio")}{h2a}</h2>
<ul>{"".join(f"<li>{x}</li>" for x in dopo)}</ul>
{fonte(G, lg, " · ".join(a(Fc[k]["url"], Fc[k]["nome"]) for k in ("legge", "residenza", "domanda", "consulta")), v, fonti_parola(lg, 4))}
</section>
<section>
<h2 id="prefectures">{G.ic("pin")}{h2p}</h2>
<p>{pp}</p>
</section>
{LG.faq_sezione(G, lg, faq_html)}
<div class="due">
<section>
<h2 id="exam">{G.ic("cal")}{h2e}</h2>
<p>{pe}</p>
{LG.griglia_guide(G, lg, "../", salta=LG.GUIDE[lg][6][0])}
</section>
<aside>{LG.modulo(G, lg, "../../")}</aside>
</div>
{LG.altre_lingue(G, lg, perc, "../../")}"""
    if chi_dec not in corpo:
        raise SystemExit("genera_lingue: manca chi decide")
    LG.pagina_l(G, lg, perc, titolo, descr, corpo, jsonld=ld)


# ---------------------------------------------------------------- carta di soggiorno
def pagina_carta(G, lg):
    uk = H(lg)
    ca = G.REDDITI["carta_soggiorno"]
    tu9 = ca["fonti"]["tu9"]
    A = G.RICONG["assegno_sociale"]
    anno = G.RICONG["anno"]
    annuo = G.cent(A["annuo"])
    meta = annuo // 2
    T = EN.a2_test(G)
    Fe = G.esoneri["fonti"]
    anni_carta = num(" ".join(x["testo"] for x in G.REDDITI["citazioni"] if x["fonte"] == "tu9"), r"da almeno (cinque) anni")
    circ = num(A["fonte"], r"circolare n\. (\d+)")
    circ_d = data(lg, iso_it(A["fonte"]))
    v = tu9["verificato_il"]
    E = lambda x: eur_c(lg, x)  # noqa: E731
    idx = 7 if uk else 8
    perc = f"{lg}/{LG.GUIDE[lg][idx][0]}"
    g_red, g_eso, g_dom = LG.GUIDE[lg][5][0], LG.GUIDE[lg][4][0], LG.GUIDE[lg][6][0]
    fonti_a2 = a(Fe["dm2021"]["url"], Fe["dm2021"]["nome"]) + " · " + a(Fe["minint_test"]["url"], Fe["minint_test"]["nome"]) + " · " + a(Fe["lecco"]["url"], Fe["lecco"]["nome"])
    if uk:
        h1 = "Carta di soggiorno (карта ді соджорно): роки, дохід і тест з італійської A2"
        lead = (f"Згідно зі ст. 9 Зведеного закону Італії про імміграцію (прочитано на Normattiva {data(lg, v)}), дозвіл ЄС для довгострокових резидентів, відомий як «carta di soggiorno», вимагає щонайменше {anni_carta} років із дійсним дозволом на проживання, "
                f"дохід не нижчий за соціальну допомогу ({E(annuo)} на рік у {anno} році) і складений тест з італійської (рівень A2, встановлений декретом Міністра внутрішніх справ).")
        slot = (f'<div class="slot"><div class="r-et">{G.ic("orologio")}Дозвіл на проживання</div><div class="r-data">{anni_carta} років <small>щонайменше</small></div><div class="r-cosa">з дійсним дозволом</div></div>'
                f'<div class="slot"><div class="r-et">{G.ic("euro")}Дохід {anno}</div><div class="r-data">{E(annuo)} <small>на рік</small></div><div class="r-cosa">лише для вас · + {E(meta)} за члена родини</div></div>'
                f'<div class="r-piede"><a href="#a2">Тест A2 {G.ic("freccia")}</a><span>{G.ic("doc")}Джерела: закон про імміграцію, INPS, Міністерство внутрішніх справ</span></div>')
        chi = "Квестура"
        req_t = "Вимоги коротко"
        req = [f"<strong>щонайменше {anni_carta} років</strong> із дійсним дозволом на проживання;",
               "<strong>дохід</strong> не нижчий за річну соціальну допомогу (assegno sociale); якщо подаєте заяву й на членів родини, діє правило возз’єднання сім’ї (+ половина допомоги за кожного);",
               "<strong>придатне житло</strong>;", "складений <strong>тест з італійської A2</strong>, якщо ви не звільнені."]
        art = "ст. 9 Зведеного закону про імміграцію (Normattiva)"
        h_inc = f"Мінімальний дохід {anno}"
        p_inc = f"Соціальна допомога {anno} року — {E(annuo)} на рік ({a(A['url'], f'INPS, циркуляр № {circ} від {circ_d}')}). За кожного члена родини, включеного в заяву, додайте половину: {E(meta)}."
        p_mese = (f"«На місяць» — лише для порівняння: закон говорить про річний дохід. Які документи й доходи дійсні, вирішує Квестура. Якщо у вас 2 або більше дітей до {T['minori']} років, запитайте в Квестурі, чи діє для вас правило возз’єднання сім’ї про подвійну допомогу ({E(annuo * 2)}). "
                  f'<a href="../{g_red}#calculate">Калькулятор доходу</a>.')
        h_a2 = "Тест з італійської A2"
        passi = [f'Подайте заяву онлайн до Префектури за місцем проживання, на {a(Fe["portale"]["url"], "Portale Servizi")} Міністерства внутрішніх справ.',
                 f"Префектура запрошує вас протягом {T['giorni_conv']} днів.",
                 f"Тест перевіряє, чи ви розумієте короткі тексти й можете спілкуватися; наприклад, у Лекко: аудіювання ({T['orale']} хв), читання ({T['scritta']} хв), письмова взаємодія ({T['inter']} хв).",
                 f"Тест складено, якщо набрано щонайменше <strong>{T['soglia']}%</strong> балів; якщо ні, подати заяву знову можна лише через {T['ripeti']} днів після попереднього тесту."]
        no_a2 = (f"<strong>Тест не складають</strong>, наприклад, ті, хто вже має сертифікат A2 або вище від визнаної установи (також B1 для громадянства), італійський шкільний атестат або серйозні труднощі з навчанням, підтверджені державною медичною установою; діти до {T['minori']} років теж звільнені. "
                 f'<a href="../{g_eso}#carta-di-soggiorno">Усі звільнення від A2</a>.')
        h_c = "Carta di soggiorno і громадянство"
        p_c = (f'Якщо у вас є дозвіл ЄС для довгострокових резидентів, при заяві на громадянство сертифікат B1 подавати не треба (ст. 9.1 Закону 91/1992): <a href="../{g_eso}#citizenship">звільнення від B1</a> · '
               f'<a href="../{g_dom}">як подати заяву на громадянство</a>. Тимчасовий захист — окремий дозвіл: <a href="../{LG.GUIDE[lg][9][0]}">тимчасовий захист в Італії</a>.')
        titolo = G.titolo_pagina(f"Carta di soggiorno {anno}: вимоги, дохід і тест A2")
        descr = G.descrizione_pagina(f"Carta di soggiorno (дозвіл ЄС для довгострокових резидентів) українською: {anni_carta} років із дозволом, дохід від {E(annuo)} на рік у {anno}, тест A2.")
        bric = "Carta di soggiorno"
    else:
        h1 = "Carta di soggiorno: ani, venit și testul de italiană A2 (pentru cetățenii din afara UE)"
        lead = (f"Potrivit art. 9 din Textul unic italian privind imigrația (citit pe Normattiva la {data(lg, v)}), permisul UE pentru rezidenți pe termen lung, numit «carta di soggiorno», cere cel puțin {anni_carta} ani cu un permis de ședere valabil, "
                f"un venit nu mai mic decât alocația socială ({E(annuo)} pe an în {anno}) și promovarea unui test de italiană (nivel A2, stabilit printr-un decret al ministrului de Interne). "
                "Îl cer cetățenii din afara UE, de exemplu din Republica Moldova; cetățenii români nu au nevoie de el.")
        slot = (f'<div class="slot"><div class="r-et">{G.ic("orologio")}Permis de ședere</div><div class="r-data">{anni_carta} ani <small>cel puțin</small></div><div class="r-cosa">cu permis valabil</div></div>'
                f'<div class="slot"><div class="r-et">{G.ic("euro")}Venit {anno}</div><div class="r-data">{E(annuo)} <small>pe an</small></div><div class="r-cosa">doar pentru dumneavoastră · + {E(meta)} pe membru de familie</div></div>'
                f'<div class="r-piede"><a href="#a2">Testul A2 {G.ic("freccia")}</a><span>{G.ic("doc")}Surse: legea imigrației, INPS, Ministerul de Interne</span></div>')
        chi = "Chestura"
        req_t = "Cerințele pe scurt"
        req = [f"<strong>cel puțin {anni_carta} ani</strong> cu un permis de ședere valabil;",
               "<strong>un venit</strong> nu mai mic decât alocația socială anuală (assegno sociale); dacă cereți și pentru membrii familiei, se aplică regula reîntregirii familiei (+ jumătate din alocație pentru fiecare);",
               "<strong>o locuință corespunzătoare</strong>;", "promovarea <strong>testului de italiană A2</strong>, dacă nu sunteți scutit(ă)."]
        art = "art. 9 din Textul unic privind imigrația (Normattiva)"
        h_inc = f"Venitul minim {anno}"
        p_inc = f"Alocația socială {anno} este de {E(annuo)} pe an ({a(A['url'], f'INPS, circulara nr. {circ} din {circ_d}')}). Pentru fiecare membru de familie inclus în cerere adăugați jumătate: {E(meta)}."
        p_mese = (f"«Pe lună» este doar un ajutor pentru comparație: legea vorbește de venit anual. Chestura decide ce acte și ce venituri sunt valabile. Cu 2 sau mai mulți copii sub {T['minori']} ani, întrebați Chestura dacă vi se aplică regula reîntregirii familiei cu alocația dublă ({E(annuo * 2)}). "
                  f'<a href="../{g_red}#calculate">Calculatorul de venit</a>.')
        h_a2 = "Testul de italiană A2"
        passi = [f'Faceți cererea online la Prefectura unde locuiți, pe {a(Fe["portale"]["url"], "Portale Servizi")} al Ministerului de Interne.',
                 f"Prefectura vă convoacă în {T['giorni_conv']} {pl_ro(T['giorni_conv'], 'zi', 'zile')}.",
                 f"Testul verifică dacă înțelegeți texte scurte și puteți comunica; de exemplu la Lecco: ascultare ({T['orale']} {pl_ro(T['orale'], 'minut', 'minute')}), citire ({T['scritta']} {pl_ro(T['scritta'], 'minut', 'minute')}), interacțiune scrisă ({T['inter']} {pl_ro(T['inter'], 'minut', 'minute')}).",
                 f"Promovați cu cel puțin <strong>{T['soglia']}%</strong> din punctaj; dacă nu, puteți face din nou cererea doar după {T['ripeti']} {pl_ro(T['ripeti'], 'zi', 'zile')} de la testul anterior."]
        no_a2 = (f"<strong>Nu dați testul</strong> dacă, de exemplu, aveți deja un certificat A2 sau superior de la o instituție recunoscută (și B1 pentru cetățenie), o diplomă școlară italiană sau dificultăți grave de învățare certificate de o unitate sanitară publică; copiii sub {T['minori']} ani sunt și ei scutiți. "
                 f'<a href="../{g_eso}#carta-di-soggiorno">Toate scutirile de A2</a>.')
        h_c = "Carta di soggiorno și cetățenia"
        p_c = (f'Cine are permisul UE pe termen lung nu trebuie să prezinte certificatul B1 la cererea de cetățenie (art. 9.1 din Legea 91/1992): <a href="../{g_eso}#citizenship">scutirile de B1</a> · '
               f'<a href="../{g_dom}">cum se cere cetățenia</a>. Pentru cetățenii români: <a href="../{LG.GUIDE[lg][7][0]}">rezidența pentru cetățenii UE</a>.')
        titolo = G.titolo_pagina(f"Carta di soggiorno {anno}: cerințe, venit și testul A2")
        descr = G.descrizione_pagina(f"Carta di soggiorno (permis UE pe termen lung) în română: {anni_carta} ani cu permis, venit de la {E(annuo)} pe an în {anno}, testul A2. Pentru cetățenii din afara UE.")
        bric = "Carta di soggiorno"
    corpo = f"""<section class="hero">
{LG.briciole(lg, "../", (bric, None))}
<h1>{h1}</h1>
<p class="lead">{lead}</p>
<div class="risposta">{slot}</div>
</section>
{LG.decide(G, lg, chi)}
<section>
<h2 id="requirements">{G.ic("lista")}{req_t}</h2>
<ul>{"".join(f"<li>{x}</li>" for x in req)}</ul>
{fonte(G, lg, a(tu9["url"], art), v, fonti_parola(lg, 1))}
</section>
<section>
<h2 id="income">{G.ic("euro")}{h_inc}</h2>
<p>{p_inc}</p>
{tabella_carta(G, lg)}
<p class="small">{p_mese}</p>
</section>
<section>
<h2 id="a2">{G.ic("voce")}{h_a2}</h2>
<ol class="passi">{"".join(f"<li><span>{x}</span></li>" for x in passi)}</ol>
{fonte(G, lg, fonti_a2, G.esoneri["verificato_il"], fonti_parola(lg, 3))}
<p>{no_a2}</p>
</section>
<section>
<h2 id="citizenship">{G.ic("scudo")}{h_c}</h2>
<p>{p_c}</p>
</section>
{LG.due_colonne(G, lg, "../", "../../", LG.GUIDE[lg][idx][0])}
{LG.altre_lingue(G, lg, perc, "../../", [f'<a href="../../reddito-minimo-cittadinanza/#carta-di-soggiorno" hreflang="it" lang="it">Italiano (reddito minimo)</a>', f'<a href="../../esonero-test-italiano/#carta-di-soggiorno" hreflang="it" lang="it">Italiano (test A2)</a>'])}"""
    LG.pagina_l(G, lg, perc, titolo, descr, corpo)


# ---------------------------------------------------------------- ricongiungimento (solo ucraino)
def pagina_ricongiungimento(G, lg):
    R = G.RICONG
    A, r, sp = R["assegno_sociale"], R["regola"], R["sportello"]
    anno = R["anno"]
    annuo = Decimal(A["annuo"])
    righe_t = G.tabella_ricongiungimento()
    uno = righe_t[0]
    tre = next(x for x in righe_t if x[0] == 3)
    circ = num(A["fonte"], r"circolare n\. (\d+)")
    circ_d = data(lg, iso_it(A["fonte"]))
    giorni_no = num(r["domanda"], r"nulla osta entro (\d+) giorni")
    over = num(sp["testo"], r"ultra (\d+)enni")
    anno_perm = num(sp["testo"], r"non inferiore a (un) anno")
    minori = num(r["testo"], r"agli anni (quattordici)")
    v = A["verificato_il"]
    E = lambda x: eur(lg, x)  # noqa: E731
    perc = f"{lg}/{LG.GUIDE[lg][8][0]}"
    righe = "".join(
        f'<tr><td><strong>{n} {pl_uk(n, "член", "члени", "членів")} родини</strong></td><td data-l="Осіб у родині">{n + 1} {pl_uk(n + 1, "особа", "особи", "осіб")}</td>'
        f'<td data-l="На рік"><strong>{E(tot)}</strong></td><td data-l="На місяць, із 12">{E(m12)}</td><td data-l="На місяць, із 13">{E(m13)}</td></tr>'
        for n, tot, m12, m13 in righe_t)
    doppio = annuo * 2
    righe += (f'<tr><td><strong>2 або більше дітей до {minori} років</strong></td><td data-l="Осіб у родині">–</td><td data-l="На рік"><strong>{E(doppio)}</strong></td>'
              f'<td data-l="На місяць, із 12">{E(doppio / 12)}</td><td data-l="На місяць, із 13">{E(doppio / 13)}</td></tr>')
    fonte_inps = a(A["url"], f"INPS, циркуляр № {circ} від {circ_d}")
    fonte_tu = a(r["url"], "ст. 29 Зведеного закону про імміграцію")
    corpo = f"""<section class="hero">
{LG.briciole(lg, "../", ("Возз’єднання сім’ї", None))}
<span class="occhiello">{G.ic("euro")}Офіційні джерела · {data(lg, v)}</span>
<h1>Возз’єднання сім’ї в Італії: дохід {anno}</h1>
<p class="lead">Згідно з циркуляром INPS № {circ} від {circ_d} і ст. 29 Зведеного закону про імміграцію (перевірено {data(lg, v)}), у {anno} році для возз’єднання сім’ї потрібен дохід щонайменше {E(uno[1])} на рік з 1 членом родини
і ще {E(annuo / 2)} за кожного наступного. Це соціальна допомога {anno} року ({E(annuo)} на рік), збільшена на половину за кожного члена родини.</p>
<div class="risposta">
<div class="slot"><div class="r-et">{G.ic("pin")}З 1 членом родини</div><div class="r-data">{E(uno[1])} <small>на рік</small></div><div class="r-cosa">дружина, чоловік або 1 дитина · близько {E(uno[2])} на місяць із 12 місяців</div></div>
<div class="slot"><div class="r-et">{G.ic("euro")}Кожен наступний</div><div class="r-data">+ {E(annuo / 2)}</div><div class="r-cosa">половина соціальної допомоги {anno} року ({E(annuo)} на рік)</div></div>
<div class="r-piede"><a href="#table">Таблиця за кількістю членів родини {G.ic("freccia")}</a><span>{G.ic("doc")}Джерела: INPS і закон про імміграцію</span></div>
</div>
</section>
{LG.decide(G, lg, "Єдине імміграційне віконце Префектури (Sportello unico per l'immigrazione)")}
<section>
<h2 id="table">{G.ic("lista")}Таблиця {anno}: мінімальний дохід за кількістю членів родини</h2>
<p>У першій колонці рахуйте лише тих членів родини, яких хочете привезти до Італії. Друга колонка враховує і вас: наприклад, «4 особи» — це ви, дружина і 2 дитини, тобто 3 члени родини, яких треба привезти.</p>
<div class="tab-wrap rc-tab"><table class="conf"><thead><tr><th scope="col">Члени родини, яких привозите</th><th scope="col">Осіб у родині, разом із вами</th><th scope="col">Мінімальний дохід на рік</th><th scope="col">На місяць, із 12</th><th scope="col">На місяць, із 13</th></tr></thead>
<tbody>{righe}</tbody></table></div>
{fonte(G, lg, f"соціальна допомога {anno}: {fonte_inps} ({a(A['url_allegato'], 'додаток 2, таблиця A')}) · правило: {fonte_tu}", v, fonti_parola(lg, 2))}
<p class="small">Закон говорить про <strong>річний</strong> дохід: колонки «на місяць» лише допомагають порівняти із зарплатою.
Приклад: дружина і 2 дитини = 3 члени родини: {E(annuo)} + 3 × {E(annuo / 2)} = {E(tre[1])} на рік.</p>
</section>
<section>
<h2 id="rules">{G.ic("info")}Правила</h2>
<h3>Двоє або більше дітей до {minori} років</h3>
<p>Закон додає: для возз’єднання двох або більше дітей до {minori} років «у будь-якому разі» потрібен дохід щонайменше <strong>у подвійному розмірі річної соціальної допомоги</strong>: {E(doppio)} у {anno} році.
Якщо разом із дітьми приїжджають інші члени родини або дітей троє чи більше, як поєднуються два правила, вирішує Sportello unico.</p>
<h3>Що вважається доходом</h3>
<p>Закон вимагає річного доходу «із законних джерел» і додає дохід членів родини, які вже живуть із вами. Які документи це підтверджують і за який рік, вирішує Sportello unico вашої Префектури.</p>
<h3>Кого можна привезти</h3>
<p>За Міністерством внутрішніх справ подати заяву можна, якщо ви законно живете в Італії з дозволом на проживання строком щонайменше {anno_perm} рік, для: чоловіка чи дружини (повнолітніх, не розлучених юридично); неповнолітніх неодружених дітей — за згодою іншого з батьків;
повнолітніх дітей на утриманні з повною інвалідністю; батьків на утриманні, якщо в країні походження в них немає інших дітей, або батьків старше {over} років, чиї інші діти не можуть їх утримувати через серйозні проблеми зі здоров’ям.</p>
<h3>Куди подавати</h3>
<p>Заяву на nulla osta (дозвіл) подають онлайн до Sportello unico per l'immigrazione Префектури за місцем проживання, з документами про дохід і житло, на {a(sp["portale_url"], "Portale Servizi Міністерства внутрішніх справ")} через SPID або CIE.
За законом nulla osta мають видати протягом {giorni_no} днів від подання заяви. Також потрібне придатне житло, яке перевіряє муніципалітет (Comune).</p>
{fonte(G, lg, a(sp["url"], sp["nome"]) + " · " + fonte_tu, sp["verificato_il"], fonti_parola(lg, 2))}
</section>
{LG.due_colonne(G, lg, "../", "../../", LG.GUIDE[lg][8][0])}
{LG.altre_lingue(G, lg, perc, "../../")}"""
    titolo = G.titolo_pagina(f"Возз’єднання сім’ї в Італії {anno}: дохід, таблиця")
    descr = G.descrizione_pagina(f"Возз’єднання сім’ї в Італії {anno}: щонайменше {E(uno[1])} на рік з 1 членом родини, + {E(annuo / 2)} за кожного наступного. Таблиця, правила, джерела.")
    LG.pagina_l(G, lg, perc, titolo, descr, corpo)


# ---------------------------------------------------------------- protezione temporanea (solo ucraino)
def pagina_protezione(G, lg):
    P = LG.protezione()
    LG.controlla_protezione(P)
    F = LG.LING["fonti"]
    v = LG.LING["verificato_il"]
    lg = "uk"
    anno_2028 = LG.d(P["im_fino"]).year
    perc = f"uk/{LG.GUIDE[lg][9][0]}"
    bollo, boll = eur(lg, P["bollo"], False), eur(lg, LG.euro_it_str(P["bollettino"]))
    c_bollo, c_vers = eur(lg, P["conv_bollo"], False), eur(lg, LG.euro_it_str(P["conv_vers"]))
    ue, extra = LG.anni_residenza()

    def src(*k):
        return fonte(G, lg, " · ".join(a(F[x]["url"], F[x]["nome"]) for x in k), max(F[x]["verificato_il"] for x in k), fonti_parola(lg, len(k)))

    faq = [
        ("До якої дати продовжено тимчасовий захист в Італії?",
         f"За даними Квестур Риму та Удіне (Державна поліція), дозволи на проживання з тимчасовим захистом для громадян України можна на ваш запит продовжити до {data(lg, P['fino'])}: "
         f"Квестури посилаються на декрет-закон № {P['dl']}, а в ЄС тимчасовий захист продовжено до цієї дати рішенням Ради ЄС {P['ue_dec']}. "
         f"У липні {P['im_anno']} Рада ЄС продовжила захист ще на рік, до {data(lg, P['im_fino'])} (так повідомляє урядовий портал Integrazione Migranti); "
         f"Квестура Ареццо (сторінку оновлено {data(lg, P['arezzo_agg'])}) уже пише про продовження до {data(lg, P['arezzo_fino'])}. Яка дата діє для вас, вирішує ваша Квестура."),
        ("Чи можна перевести тимчасовий захист у дозвіл для роботи?",
         f"Так, на ваш запит і якщо ви відповідаєте вимогам закону: дозвіл із тимчасовим захистом можна конвертувати в дозвіл на проживання для роботи, за фактичною діяльністю (ст. 1, ч. {P['legge']} закону № {P['legge_n']} від {data(lg, P['legge_data'])}). "
         "Заяву подають через поштовий набір (kit) у відділенні Poste Italiane зі службою «Sportello Amico». Рішення ухвалює Квестура."),
        ("Скільки коштує продовження дозволу з тимчасовим захистом?",
         f"За Квестурою Удіне: гербова марка (marca da bollo) {bollo} і оплата поштовим бланком {boll} за електронний документ. Квестура Ареццо уточнює, що марка не потрібна для дітей до {P['minori']} років, а перша видача дозволу безкоштовна."),
        ("Як перевірити, чи готовий мій дозвіл на проживання (пермессо)?",
         f"На сайті Державної поліції, також українською: введіть номер справи ({P['pratica']} символів) або номер «assicurata» ({P['assicurata']} символів) з квитанції. Коли дозвіл готовий, вам також надішлють SMS із днем, часом і місцем отримання."),
        ("Чи ще виплачують грошову допомогу (contributo di sostentamento)?",
         f"За Префектурою Ла-Спеції, декрет-закон № {P['spezia_dl']} від {data(lg, P['spezia_dl_data'])} (ст. {P['spezia_art']}, ч. 2) припинив допомогу для власників дозволів, виданих після {data(lg, P['spezia_dopo'])}; "
         f"для інших заяву можна було подати до {data(lg, P['spezia_entro'])}."),
    ]
    faq_html, ld = LG.faq_blocco(G, [(escape(q), escape(t)) for q, t in faq])
    corpo = f"""<section class="hero">
{LG.briciole(lg, "../", ("Тимчасовий захист", None))}
<span class="occhiello">{G.ic("scudo")}Квестури, Префектура і Державна поліція · прочитано {data(lg, v)}</span>
<h1>Тимчасовий захист в Італії для українців: продовження, конвертація і перевірка дозволу</h1>
<p class="lead">За даними Квестур Риму та Удіне (Державна поліція; сторінку Риму оновлено {data(lg, P['roma_agg'])}, прочитано {data(lg, F['questura_roma']['verificato_il'])}), дозволи на проживання з тимчасовим захистом (permesso di soggiorno per protezione temporanea; українською також «посвідка на проживання»), видані громадянам України, можна на ваш запит продовжити з терміном дії до {data(lg, P['fino'])}: Квестури посилаються на декрет-закон № {P['dl']}.
Нижче — що пишуть офіційні джерела про продовження до {anno_2028} року, вартість, перехід на дозвіл для роботи і перевірку готовності дозволу.</p>
<div class="risposta">
<div class="slot"><div class="r-et">{G.ic("orologio")}Продовження (Квестури)</div><div class="r-data">{LG.d(P['fino']).day} {LG.MESI_GEN[lg][LG.d(P['fino']).month - 1]} <small>{LG.d(P['fino']).year}</small></div><div class="r-cosa">рішення Ради ЄС {P['ue_dec']}; Квестури посилаються на декрет-закон № {P['dl']}; Ареццо вже пише {anno_2028}</div></div>
<div class="slot"><div class="r-et">{G.ic("doc")}Дозвіл для роботи</div><div class="r-data">kit <small>Poste Italiane</small></div><div class="r-cosa">конвертація на запит, якщо виконано вимоги</div></div>
<div class="r-piede"><a href="#renewal">Продовження {G.ic("freccia")}</a><span>{G.ic("doc")}Джерела: Квестури Риму, Удіне, Ареццо, Мілана; Normattiva; портал Integrazione Migranti; Префектура Ла-Спеції</span></div>
</div>
</section>
{LG.decide(G, lg, "Квестура (Questura) за місцем вашого проживання")}
<section>
<h2 id="renewal">{G.ic("cal")}Продовження: до якої дати</h2>
<ul>
<li><strong>До {data(lg, P['fino'])}.</strong> Квестури Риму (сторінку оновлено {data(lg, P['roma_agg'])}) і Удіне ({data(lg, P['udine_agg'])}) пишуть, що декрет-закон № {P['dl']} дозволяє продовжити дозволи з тимчасовим захистом, видані громадянам України, на запит, з терміном дії до {data(lg, P['fino_udine'])}.
Сам текст декрету-закону № {P['dl']} (ст. 1, ч. 2; перетворений законом № {P['dl_conv_n']} від {data(lg, P['dl_conv_data'])}, читаємо на Normattiva) говорить про дозволи зі «спеціальним захистом» (protezione speciale) громадян України, які були в Італії до {data(lg, P['dl_presenti'])}, і підтверджує, що тимчасовий захист продовжено до тієї самої дати рішенням Ради ЄС {P['ue_dec']} від {data(lg, P['ue_dec_data'])}; те саме рішення називає і Квестура Мілана.</li>
<li><strong>А {anno_2028}?</strong> Урядовий портал Integrazione Migranti (Міністерство праці та соціальної політики; новина від {data(lg, P['im_data'])}) повідомляє, що {P['im_giorno']} липня Рада ЄС ухвалила продовжити тимчасовий захист ще на рік, <strong>до {data(lg, P['im_fino'])}</strong>; за тим самим повідомленням, для нових заявників умовою стане виконання військового обов’язку в Україні, а тих, хто вже має тимчасовий захист, це не стосується.
Квестура Ареццо (сторінку оновлено {data(lg, P['arezzo_agg'])}) уже пише, що дозволи, термін яких спливає, можна ще раз продовжити на запит <strong>до {data(lg, P['arezzo_fino'])}</strong>. Квестури Риму та Удіне ще називають {data(lg, P['fino'])}, а національного акта (декрету чи циркуляра) про продовження дозволів до {anno_2028} року на сайтах Міністерства внутрішніх справ і Державної поліції ми не знайшли ({data(lg, v)}): <strong>запитайте у своїй Квестурі, яка дата діє для вас</strong>, і не пропускайте термін, указаний у вашому дозволі.</li>
<li><strong>Дозволи можуть припинити дію раніше.</strong> Квестура Мілана (сторінку оновлено {data(lg, P['milano_agg'])}) пише, що вони втрачають силу й анулюються навіть до закінчення строку, якщо Рада Європейського Союзу ухвалить рішення про припинення тимчасового захисту.</li>
</ul>
{src("questura_roma", "questura_udine", "normattiva_dl201", "questura_milano", "im_2028", "questura_arezzo")}
</section>
<section>
<h2 id="how">{G.ic("lista")}Як подати заяву на продовження</h2>
<p>Кожна Квестура має свій порядок запису: наприклад, у Ареццо — через платформу PrenotaFacile (потрібна реєстрація), у Римі — особисто в Імміграційному відділі (Ufficio Immigrazione). Перевірте сторінку своєї Квестури.
Квестури Удіне і Риму просять зазвичай: паспорт, дозвіл, термін якого сплив, фотографії, документ про місце проживання (довідка про реєстрацію, cessione di fabbricato, заява про надання житла або договір оренди), а також:</p>
<ul>
<li>гербову марку (marca da bollo) <strong>{bollo}</strong> — за Квестурою Ареццо, не потрібна для дітей до {P['minori']} років;</li>
<li>оплату поштовим бланком (bollettino) <strong>{boll}</strong> за електронний документ (для кожної особи, також дітей).</li>
</ul>
<p>Квестура Ареццо також пише, що <strong>перша видача</strong> дозволу з тимчасовим захистом безкоштовна. Кількість фотографій і точний перелік документів залежать від Квестури.</p>
{src("questura_udine", "questura_arezzo")}
</section>
<section>
<h2 id="work">{G.ic("doc")}Конвертація в дозвіл для роботи</h2>
<p>Ст. 1, ч. {P['legge']} закону № {P['legge_n']} від {data(lg, P['legge_data'])} (бюджетний закон) передбачає можливість на ваш запит <strong>конвертувати дозвіл із тимчасовим захистом у дозвіл на проживання для роботи</strong>, за фактично виконуваною діяльністю.
Квестура Удіне додає: якщо ви відповідаєте вимогам закону.</p>
<ol class="passi">
<li><span>Візьміть <strong>поштовий набір (kit)</strong> у відділенні Poste Italiane зі службою «Sportello Amico» і заповніть його.</span></li>
<li><span>Додайте: бланк заяви з гербовою маркою {c_bollo}, копію паспорта або посвідчення особи, копію електронного дозволу з тимчасовим захистом, копію документів про житло, оплату {c_vers} відповідним бланком і <strong>документи про вашу поточну роботу</strong>.</span></li>
<li><span>Відправте набір у поштовому відділенні і збережіть квитанцію: номер заяви з неї («assicurata») потрібен, щоб перевіряти стан справи.</span></li>
</ol>
<p>Які саме документи про роботу і дохід приймуть, вирішує Квестура: перед поданням зверніться до патронату (patronato) — це безкоштовно.</p>
{src("questura_arezzo", "questura_udine", "questura_roma")}
</section>
<section>
<h2 id="status">{G.ic("ok")}Перевірити, чи готовий дозвіл (пермессо)</h2>
<p>Державна поліція має онлайн-сервіс, також українською: {a(F['polizia_verifica']['url'], "перевірка дозволу на проживання")}. Введіть <strong>номер справи ({P['pratica']} символів)</strong> або <strong>номер «assicurata» ({P['assicurata']} символів)</strong> з квитанції вашої заяви.
Коли дозвіл готовий, вам також надішлють SMS із днем, часом і місцем отримання.</p>
{src("polizia_verifica")}
</section>
<section>
<h2 id="payments">{G.ic("euro")}Грошова допомога (contributo di sostentamento)</h2>
<p>За Префектурою Ла-Спеції (Міністерство внутрішніх справ), ст. {P['spezia_art']}, ч. 2 декрету-закону № {P['spezia_dl']} від {data(lg, P['spezia_dl_data'])} припинила допомогу для власників дозволів із тимчасовим захистом, <strong>виданих після {data(lg, P['spezia_dopo'])}</strong>;
для власників дозволів, виданих раніше, заяву можна було подати <strong>до {data(lg, P['spezia_entro'])}</strong>.</p>
{src("prefettura_spezia")}
</section>
<section>
<h2 id="after">{G.ic("scudo")}Надовго в Італії: carta di soggiorno і громадянство</h2>
<p>Тимчасовий захист має обмежений строк. Хто планує залишитися, може дізнатися про інші дозволи і про громадянство (закон вимагає для іноземців із країн поза ЄС щонайменше {extra} років законного проживання; чи зараховується період тимчасового захисту, вирішує Префектура):
<a href="../{LG.GUIDE[lg][7][0]}">carta di soggiorno</a> · <a href="../{LG.GUIDE[lg][6][0]}">громадянство Італії</a> · <a href="../{LG.GUIDE[lg][1][0]}">іспит B1</a>.</p>
</section>
{LG.faq_sezione(G, lg, faq_html)}
{LG.due_colonne(G, lg, "../", "../../", LG.GUIDE[lg][9][0])}"""
    titolo = G.titolo_pagina(f"Тимчасовий захист в Італії: продовження {LG.d(P['fino']).year}-{anno_2028}, конвертація",
                             "Тимчасовий захист в Італії: продовження і конвертація")
    descr = G.descrizione_pagina(f"Тимчасовий захист в Італії для українців: продовження дозволу до {data(lg, P['fino'])} (Квестури) і до {data(lg, P['im_fino'])} (рішення ЄС), вартість, конвертація в дозвіл для роботи.",
                                 f"Тимчасовий захист в Італії для українців: продовження дозволу до {LG.d(P['fino']).year} і {anno_2028}, вартість, конвертація в дозвіл для роботи, перевірка пермессо.")
    LG.pagina_l(G, lg, perc, titolo, descr, corpo, jsonld=ld)


# ---------------------------------------------------------------- rezidența pentru cetățenii UE (solo rumeno)
def pagina_rezidenta(G, lg):
    import re
    lg = "ro"
    F = LG.LING["fonti"]
    ue_f = F["polizia_ue"]
    t = LG.citazioni("polizia_ue")
    v = ue_f["verificato_il"]
    agg = data(lg, ue_f["aggiornata_il"])
    if not re.search(r"\btre mesi\b", t) or not re.search(r"per (cinque) anni", t) or not re.search(r"superiore a (due) anni consecutivi", t):
        raise SystemExit("genera_lingue: frasi della Polizia sui cittadini UE cambiate: aggiornare pagina_rezidenta()")
    cinque = num(t, r"per (cinque) anni nel territorio")
    due = num(t, r"superiore a (due) anni consecutivi")
    cinque_carta = num(t, r"validità di (cinque) anni dalla data del rilascio")
    annuo = G.RICONG["assegno_sociale"]["annuo"]
    anno = G.RICONG["anno"]
    ue, extra = LG.anni_residenza()
    perc = f"ro/{LG.GUIDE[lg][7][0]}"
    src = fonte(G, lg, a(ue_f["url"], ue_f["nome"]) + f" (pagina din {agg})", v, fonti_parola(lg, 1))
    faq = [
        ("Cetățenii români au nevoie de permis de ședere în Italia?",
         "Nu. Potrivit Poliției de Stat, cetățenii Uniunii Europene pot sta în Italia până la trei luni fără nicio condiție sau formalitate, cu un act de identitate valabil pentru călătorie; "
         "dacă rămân mai mult, au doar obligația să se înscrie la registrul populației (anagrafe) al primăriei unde locuiesc. Decide primăria (Comune)."),
        ("Ce este «carta di soggiorno» pentru români?",
         f"Cetățenii români nu primesc carta di soggiorno. O cer membrii lor de familie din afara UE: «carta di soggiorno di familiare di un cittadino dell'Unione», valabilă {cinque_carta} ani, la Chestură. "
         "Permisul UE pe termen lung (tot numit «carta di soggiorno») este doar pentru cetățenii din afara UE."),
        ("Ce acte trebuie pentru rezidența în Italia fără contract de muncă?",
         f"Pentru înscrierea la anagrafe fără un loc de muncă, Poliția de Stat cere dovada unor resurse economice suficiente, calculate după valoarea anuală a alocației sociale (în {anno}: {eur(lg, annuo)} pe an) în funcție de numărul membrilor de familie în întreținere, "
         "și o asigurare medicală care acoperă cheltuielile de sănătate. Decide primăria (Comune)."),
        ("Ce este rezidența permanentă în Italia?",
         f"După {cinque} ani de ședere legală și neîntreruptă în Italia, cetățeanul UE dobândește dreptul de ședere permanentă; la cerere, primăria de reședință eliberează un atestat. Dreptul se pierde după absențe din Italia de peste {due} ani consecutivi."),
        ("După câți ani de rezidență pot cere cetățenia italiană?",
         f"După cel puțin {ue} ani de rezidență legală, pentru cetățenii UE (art. 9 din Legea 91/1992). Trebuie și certificatul B1 și venitul minim. Decide Prefectura."),
    ]
    faq_html, ld = LG.faq_blocco(G, [(escape(q), escape(x)) for q, x in faq])
    corpo = f"""<section class="hero">
{LG.briciole(lg, "../", ("Rezidența UE", None))}
<span class="occhiello">{G.ic("pin")}Poliția de Stat · pagina din {agg} · citită la {data(lg, v)}</span>
<h1>Rezidența în Italia pentru cetățenii români: anagrafe, ședere permanentă și cetățenie</h1>
<p class="lead">Potrivit Poliției de Stat italiene (pagina «Cittadini della Unione Europea» din {agg}, citită la {data(lg, v)}), cetățenii români, ca toți cetățenii Uniunii Europene, nu au nevoie de permis de ședere: pot sta în Italia până la trei luni fără nicio condiție, cu un act de identitate valabil,
iar dacă rămân mai mult trebuie doar să se înscrie la registrul populației (anagrafe) al primăriei (Comune) unde locuiesc.</p>
<div class="risposta">
<div class="slot"><div class="r-et">{G.ic("pin")}Peste trei luni</div><div class="r-data">anagrafe <small>la primărie</small></div><div class="r-cosa">nu permis de ședere: înscriere la Comune</div></div>
<div class="slot"><div class="r-et">{G.ic("orologio")}Ședere permanentă</div><div class="r-data">{cinque} ani <small>legali, neîntrerupți</small></div><div class="r-cosa">atestat de la primărie, la cerere</div></div>
<div class="r-piede"><a href="#anagrafe">Ce acte cere primăria {G.ic("freccia")}</a><span>{G.ic("doc")}Sursa: Poliția de Stat (în italiană)</span></div>
</div>
</section>
{LG.decide(G, lg, "primăria (Comune) pentru anagrafe, Chestura pentru carta membrilor de familie și Prefectura pentru cetățenie")}
<p class="small">Pagina Poliției de Stat este din {agg}: regulile de bază sunt aceleași, dar actele exacte le spune primăria dumneavoastră. Întrebați la biroul de anagrafe înainte de a merge.</p>
<section>
<h2 id="anagrafe">{G.ic("lista")}Peste trei luni: înscrierea la anagrafe</h2>
<p>Cetățeanul UE are dreptul să stea în Italia mai mult de trei luni dacă:</p>
<ul>
<li>este <strong>lucrător salariat sau independent</strong> în Italia (la înscriere arată documentele despre activitatea sa);</li>
<li>are, pentru sine și pentru familie, <strong>resurse economice suficiente</strong>, calculate după valoarea anuală a alocației sociale (assegno sociale: {eur(lg, annuo)} pe an în {anno}) în funcție de numărul membrilor de familie în întreținere, și o <strong>asigurare medicală</strong> care acoperă cheltuielile de sănătate (resursele se pot declara și pe proprie răspundere);</li>
<li>este înscris la un curs de studii sau de formare profesională, cu resurse suficiente și asigurare medicală;</li>
<li>este membru de familie al unui cetățean UE care are acest drept.</li>
</ul>
<p>Cererea se face la <strong>primăria (Comune) unde locuiți</strong>; primăria vă dă o adeverință că ați depus cererea. Cât trebuie să fie resursele pentru familia dumneavoastră și ce acte sunt valabile decide primăria.</p>
{src}
</section>
<section>
<h2 id="permanent">{G.ic("orologio")}După {cinque} ani: dreptul de ședere permanentă</h2>
<p>Cetățeanul UE care a locuit legal și neîntrerupt <strong>{cinque} ani</strong> în Italia dobândește <strong>dreptul de ședere permanentă</strong>. La cerere, <strong>primăria de reședință eliberează un atestat</strong> care îl certifică.
Dreptul se pierde în orice caz după absențe din Italia de <strong>peste {due} ani consecutivi</strong>.</p>
{src}
</section>
<section>
<h2 id="family">{G.ic("doc")}Membrii familiei din afara UE: carta di soggiorno</h2>
<p>Membrii familiei care nu sunt cetățeni UE (de exemplu soțul sau soția din Republica Moldova) trebuie să ceară, pentru șederi de peste trei luni, <strong>«carta di soggiorno di familiare di un cittadino dell'Unione»</strong>, la Chestură sau prin poștă (kit).
Carta este valabilă <strong>{cinque_carta} ani</strong> de la eliberare. Atenție: pentru cetățenie, titularii acestei carta trebuie să aibă certificatul B1 (<a href="../{LG.GUIDE[lg][4][0]}">scutiri</a>).</p>
{src}
</section>
<section>
<h2 id="citizenship">{G.ic("scudo")}Și cetățenia italiană?</h2>
<p>Pentru cetățenii UE legea cere cel puțin <strong>{ue} ani de rezidență legală</strong> în Italia (art. 9 din Legea 91/1992), plus certificatul de limba italiană B1 și venitul minim:
<a href="../{LG.GUIDE[lg][6][0]}">cererea de cetățenie</a> · <a href="../{LG.GUIDE[lg][1][0]}">examenul B1</a> · <a href="../{LG.GUIDE[lg][5][0]}">venitul minim</a>. Decide Prefectura.</p>
{fonte(G, lg, a(F["dlci_residenza"]["url"], F["dlci_residenza"]["nome"]), F["dlci_residenza"]["verificato_il"], fonti_parola(lg, 1))}
</section>
{LG.faq_sezione(G, lg, faq_html)}
{LG.due_colonne(G, lg, "../", "../../", LG.GUIDE[lg][7][0])}"""
    titolo = G.titolo_pagina("Rezidența în Italia pentru români: anagrafe și ședere permanentă")
    descr = G.descrizione_pagina(f"Rezidența în Italia pentru cetățenii români (UE): fără permis de ședere, înscriere la anagrafe, acte fără contract de muncă, ședere permanentă după {cinque} ani.")
    LG.pagina_l(G, lg, perc, titolo, descr, corpo, jsonld=ld)


# ---------------------------------------------------------------- tutto
def genera(G, prossime):
    """Scrive le pagine /uk/ e /ro/ e restituisce i loro URL (per la sitemap)."""
    LG.SCRITTE.clear()
    for lg in ("uk", "ro"):
        hub(G, lg, prossime)
        pagina_date(G, lg, prossime)
        pagina_esame(G, lg, prossime)
        pagina_costo(G, lg)
        pagina_esempi(G, lg)
        pagina_esoneri(G, lg)
        pagina_redditi(G, lg)
        pagina_domanda(G, lg)
        pagina_carta(G, lg)
        if lg == "uk":
            pagina_ricongiungimento(G, lg)
            pagina_protezione(G, lg)
        else:
            pagina_rezidenta(G, lg)
    scritte = {p["p"][:-10] for p in LG.SCRITTE}
    attese = {r[0] for righe in LG.PAGINE.values() for r in righe}
    if scritte != attese:
        raise SystemExit(f"genera_lingue: pagine in PAGINE non scritte o in più: {sorted(scritte ^ attese)}")
    return sorted(attese)
