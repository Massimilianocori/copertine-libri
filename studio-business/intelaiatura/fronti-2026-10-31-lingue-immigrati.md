# Fronte nuovo: le guide che funzionano, nelle lingue dei lettori (31/10/2026)

Domanda: le guide che oggi portano visite (EsameB1: esame B1, redditi, cittadinanza per Prefettura, carta di soggiorno; Visa Income: rifiuti e requisiti dei visti) rendono di più se le scriviamo nelle lingue degli stranieri che vivono in Italia? Quali lingue, in che forma, con quali soldi.

**Letti prima:** skill `rete-siti`, `REGOLE-FISSE.md`, `ESPLORATE.md` (in particolare: rifiuti dei visti in francese e arabo PASSA il 21/10; rifiuti in urdu, hindi, turco, russo, cinese NO il 21/10; rimesse in italiano NO il 31/10), `idee-2026-10-31-vincenti.md` (numeri GoatCounter), `idee-2026-10-31-lingue.md` (altro angolo: mercati esteri non inglesi), `esameb1/NOTE.md` (il generatore oggi non sa fare pagine in un'altra lingua), `CRUSCOTTO-RETE.md`.

**Metodo (tutto letto il 31/10/2026):**
- suggerimenti di Google (`suggestqueries.google.com`, `client=firefox`) con la lingua giusta (`hl`) e `gl=it`, poi lo stesso con il Paese d'origine (`gl=bd`, `pk`, `in`, `ma`, `eg`, `al`, `ua`, `pe`, `ph`) per capire se chi cerca vive in Italia o nel Paese d'origine; ~170 ricerche in 16 lingue/Paesi. "10" = 10 suggerimenti, il massimo;
- residenti stranieri per cittadinanza: dati ISTAT al 1/1/2025 (pubblicati per Paese su tuttitalia.it, pagina scaricata, HTTP 200; l'elenco dei flussi di `esploradati.istat.it` non ha la tabella per cittadinanza);
- prima pagina dei risultati con ricerca web (vista dagli USA: in Italia può essere un po' diversa);
- regole di Google lette alla fonte con `curl` (norme contro lo spam, contenuti generati, "risultati tradotti", lingue ammesse da AdSense);
- GoatCounter (`stats/locations` 17-31/10: le lingue del browser non vengono registrate, `stats/languages` = tutto "unknown").

Le stime sono stime, non dati: ognuna ha il calcolo. Voti con la griglia delle ricerche precedenti: domanda 0-3 · buco nei risultati 0-2 · fonte ufficiale 0-2 · chi paga 0-2 · rischi e ore 0-1.

---

## 0. In breve

1. **Gli stranieri del Sud dell'Asia cercano in inglese, non nella loro lingua.** In urdu, punjabi e hindi i suggerimenti su cittadinanza, permesso e carta di soggiorno sono **0** (anche "ਇਟਲੀ ਵੀਜ਼ਾ" in punjabi: 0). Pakistani e indiani scrivono "italy citizenship for pakistani" (9), "italy family visa processing time in pakistan" (10), "italy nationality requirements for pakistani" (10). I filippini cercano in inglese o in italiano ("carta di soggiorno meaning", "permesso di soggiorno status check"). Conferma dai nostri numeri: le 30 visite dal Pakistan sulla rete arrivano su pagine inglesi di Visa Income, quasi tutte da ChatGPT.
2. **Quindi la prima "lingua dei lettori" è l'inglese:** una versione inglese di EsameB1 raggiunge in un colpo bangladesi, pakistani, indiani, filippini, nigeriani, ghanesi e srilankesi (~1,0 milione di residenti) più i coniugi di italiani che vivono all'estero. Voto **7,5**.
3. **Le lingue con domanda vera nella lingua madre sono ucraino/russo, rumeno, arabo e cinese** (suggerimenti da 7 a 10). Tra queste, **ucraino e rumeno** sono le migliori anche per un fatto tecnico: Google **traduce già da solo** i risultati in arabo, bengalese, hindi e urdu, **ma non in ucraino, russo, rumeno, cinese e albanese**. Dove Google non traduce, una pagina nostra nella lingua non ha concorrenza dalle pagine inglesi e italiane.
4. **Albanese: no.** Domanda quasi nulla e **AdSense non ammette l'albanese** come lingua di un sito (pubblicità vietata su pagine soprattutto in albanese).
5. **Nessuna idea arriva a 5.000 €/anno nel caso centrale:** nessun sito nuovo. Tutto come **sezioni di EsameB1** (`/en/`, `/uk/`, `/ro/`…), che ha già 3.570 impressioni e posizione media 7,3. Il pacchetto di tutte le lingue utili vale **~350 / 1.640 / 7.570 €/anno** (prudente / centrale / ottimista); le prime tre (inglese, ucraino, rumeno) **~190 / 940 / 3.960 €/anno**.
6. **Traduzione fatta e controllata da agenti: sì, ma solo per le pagine guida (10-20 per lingua), mai per le 89 pagine città.** Nessuna lingua diversa dall'italiano ha domanda per città (0 suggerimenti per "b1 italian exam milan", "громадянство італії мілан", "examen b1 italiana milano", "意大利语b1考试 米兰"…). Tradurre tutto (147 pagine × 12 lingue = 1.764 pagine) sarebbe proprio l'esempio di "scaled content abuse" che Google scrive.

| # | Idea | Residenti (ISTAT 1/1/2025) | Domanda nella lingua | Chi paga | €/anno a 18 mesi (prudente / centrale / ottimista) | Ore | Voto |
|---|---|---|---|---|---|---|---|
| 1 | **EsameB1 in inglese** (`/en/`, ~25 pagine) | ~1,0 mln che leggono in inglese (Bangladesh, Pakistan, India, Filippine, Nigeria, Sri Lanka, Ghana…) + coniugi all'estero | forte (10 su quasi tutto) | AdSense, italki (18 $), Amazon/libro | 126 / 600 / 2.520 | 25-35 | **7,5** |
| 2 | **Ucraino (poi russo)** (`/uk/`, `/ru/`, ~15 pagine) | Ucraina 287.187 + Russia 43.119 (+ parte di Moldova e Georgia) | forte (10) | AdSense, italki, Wise | 30 / 168 / 720 | 12-18 | **7** |
| 3 | **Rumeno** (`/ro/`, ~12 pagine) | Romania 1.053.042 + Moldova 94.141 | forte sulla cittadinanza (10) | AdSense, italki, Wise | 36 / 168 / 720 | 8-12 | **6,5** |
| 4 | Arabo (`/ar/`, ~12 pagine) | Marocco 412.457 + Egitto 174.141 + Tunisia 123.828 | media (7-10 su permesso e ricongiungimento, 0 sulla cittadinanza) | AdSense, italki | 24 / 126 / 540 | 12-18 (scrittura da destra) | 6 |
| 5 | Cinese (`/zh/`, ~10 pagine) | 311.250 | media (10 su permesso lungo periodo, 7 su ricongiungimento) | AdSense, italki | 15 / 84 / 360 | 8-12 | 6 |
| 6 | Spagnolo (`/es/`) | Perù 116.169, Ecuador 57.980, Rep. Dominicana 30.200, Colombia 26.395, El Salvador 25.880, Venezuela 16.981 | media, ma soprattutto discendenti all'estero | AdSense, italki | 19 / 108 / 486 | 6-10 | 5,5 |
| 7 | Bangla (`/bn/`, 3-5 pagine) | 213.622 | media, ma da chi vive in Bangladesh (visti, "green card") | AdSense Bangladesh (poco) | 12 / 72 / 360 | 8-12 | 5 |
| 8 | Urdu, punjabi, hindi | Pakistan 171.179, India 171.429 | **0** sui nostri temi | – | – | – | **3,5 NO** (coperti dall'inglese) |
| 9 | Albanese | Albania 414.622 + Kosovo 36.180 | 0-6 | **AdSense vietato** | – | – | **3 NO** |
| 10 | Tagalog | Filippine 153.455 | 0 (cercano in inglese) | – | – | – | **3 NO** (coperto dall'inglese) |
| 11 | Rimesse (Wise, Remitly, WorldRemit) | 8,6 mld € inviati dall'Italia nel 2025, Bangladesh ~1,7 mld | 5-9 in inglese, 6 in bangla e arabo | Wise 10 £ a cliente nuovo; Remitly 1,60 $ (USA) | 85 / 313 / 1.865 (solo come riquadro nelle pagine lingua) | 2-3 | 4 come pagine, **sì come riquadro** |
| 12 | Assicurazione sanitaria per il permesso di soggiorno (pista nuova, in italiano) | – | 10 in italiano | da trovare (serve un programma con cifra scritta) | non stimata | – | 5,5 RISERVA |

---

## 1. I numeri ufficiali: chi sono i lettori

**Residenti stranieri al 1/1/2025: 5.371.251** (9,1 % della popolazione; dato ISTAT con il Censimento permanente, riportato per Paese da tuttitalia.it). Al 1/1/2026 ISTAT stima **~5,56 milioni** (Report "Indicatori demografici, anno 2025", marzo 2026).

| Cittadinanza | Residenti 1/1/2025 | Lingua in cui leggono (ipotesi) |
|---|---|---|
| Romania | 1.053.042 | rumeno, italiano |
| Albania | 414.622 | albanese, italiano (molti) |
| Marocco | 412.457 | arabo, francese, italiano |
| Cina | 311.250 | cinese |
| Ucraina | 287.187 (215.112 donne) | ucraino, russo |
| Bangladesh | 213.622 | bangla, inglese |
| Egitto | 174.141 | arabo |
| India | 171.429 | inglese, punjabi, hindi |
| Pakistan | 171.179 | inglese, urdu |
| Filippine | 153.455 | inglese, tagalog |
| Nigeria | 132.129 | inglese |
| Tunisia | 123.828 | arabo, francese |
| Senegal | 119.067 | francese, wolof |
| Perù | 116.169 | spagnolo |
| Sri Lanka | 113.705 | inglese, singalese, tamil |
| Moldova | 94.141 | rumeno, russo |
| Ecuador | 57.980 | spagnolo |
| Ghana | 46.327 | inglese |
| Federazione Russa | 43.119 | russo |
| Georgia | 36.490 | georgiano, russo |
| Kosovo | 36.180 | albanese |

**Per lingua (somma prudente):** rumeno ~1,15 mln · inglese come lingua di lettura ~1,0 mln (Bangladesh, India, Pakistan, Filippine, Nigeria, Sri Lanka, Ghana, Regno Unito 25.745) · arabo ~0,71 mln · albanese ~0,45 mln · ucraino/russo ~0,33-0,41 mln · cinese 0,31 mln · spagnolo ~0,30 mln · bangla 0,21 mln.

**Chi fa il passo che ci interessa:** acquisizioni di cittadinanza 2025: 196.955, di cui 88.533 per residenza e 22.845 per matrimonio (ISTAT, dato già in `idee-2026-10-31-vincenti.md`): sono loro che fanno il B1 e la domanda in Prefettura. Il dettaglio per cittadinanza d'origine non è nel flusso SDMX che risponde dal server (solo il totale "WORLD").

**Visitatori della rete per Paese (GoatCounter, 17-31/10, tutti i siti):** Italia 395, USA 63, Pakistan 30, Regno Unito 23, Germania 19, Tunisia 8, Turchia 8, Bangladesh 5, Nigeria 5, Marocco 4, India 3, Filippine 2, Albania 2, Romania 2. La lingua del browser non è registrata: chi vive in Italia e legge in bangla o in ucraino oggi è contato solo come "Italia".

---

## 2. Cosa cercano nella loro lingua (suggerimenti di Google, 31/10/2026)

| Lingua (hl/gl) | Ricerca di partenza | Suggerimenti | Cosa dicono |
|---|---|---|---|
| bangla bn/it | ইতালি নাগরিকত্ব (cittadinanza) | 3 | "come ottenerla", "quanti anni ci vogliono" |
| bn/it | ইতালি ফ্যামিলি ভিসা (visto familiare) | **10** | "cosa serve", "tempi in Bangladesh", "aggiornamento 2026" |
| bn/it | ইতালি গ্রীন কার্ড ("green card" = carta di soggiorno) | 4 | "cos'è", "quanti anni ci vogliono", "foto" |
| bn/it | ইতালি ভিসা / পারমিট | **10** / **10** | "modulo di domanda 2026", "in che data" (decreto flussi), "permesso di lavoro 2026, quanto costa" |
| bn/it | ইতালিয়ান ভাষা (lingua italiana) | **10** | "libro PDF", "corso", "centro di formazione" |
| bn/it | ইতালির ভাষা পরীক্ষা / পারমিট নবায়ন (esame / rinnovo) | 0 / 0 | – |
| bn/bd | stesse ricerche dal Bangladesh | quasi identiche | **chi cerca in bangla vive soprattutto in Bangladesh** |
| urdu ur/it | اٹلی شہریت (cittadinanza) / پرمیسو / فیملی ویزا / نیشنلٹی | **0** / 0 / 0 / 0 | – |
| ur/it | اٹلی ویزا (visto) | 10 | visto di lavoro dal Pakistan |
| punjabi pa/it | ਇਟਲੀ ਨਾਗਰਿਕਤਾ / ਵੀਜ਼ਾ / ਪੱਕੇ ("pakke", documenti) | **0** / 0 / 0 | in India: "italy de pakke paper" 1 |
| hindi hi/it | इटली नागरिकता / सिटीजनशिप | **0** / 0 | in India "इटली पीआर" 10 ma con i suggerimenti in inglese ("italy pr requirements") |
| inglese en/pk | italy citizenship / italy nationality / italy family visa / italy permesso / italy b1 test | **10** / **10** / **10** / **10** / **10** | "for pakistani", "processing time in pakistan", "permesso di soggiorno check online, renewal, photo size", "italian b1 test online free, pdf, example" |
| en/bd | italy green card / italy family visa / italy b1 exam | **10** / **10** / **10** | "italy green card time, requirements, bangla"; "family visa checklist, tracking"; "italian b1 exam dates 2026, past papers, preparation book" |
| en/in | italy citizenship / italy permanent residency | **10** / **10** | "for indian", "how many years", "permanent residence card" |
| arabo ar/it | اقامة ايطاليا (permesso) | **10** | "documenti", "quanto costa", "tessera" |
| ar/it | تجديد الاقامة في ايطاليا (rinnovo del permesso) | **9** | "permesso permanente", "condizioni", "costo" |
| ar/it | لم الشمل ايطاليا (ricongiungimento) | **10** | "condizioni", "legge", "durata", "2026" |
| ar/it | امتحان اللغة الايطالية (esame di italiano) | **10** | "b1", "per stranieri" (anche maturità egiziana) |
| ar/it | تصريح الاقامة ايطاليا (permesso) | 7 | "verifica online", "tracciamento" |
| ar/it, ar/eg, ar/ma | الجنسية الايطالية (cittadinanza) in 4 forme | **0** | – |
| albanese sq/it | nënshtetësia italiane / shtetësia italiane | 0 / 0 (senza accenti: 1) | – |
| sq/it | bashkim familjar itali / dokumentet per nenshtetesi | 6 / 4 | "documenti per la cittadinanza italiana" 2 |
| rumeno ro/it | cetatenie italiana | **10** | "pentru romani", "prin casatorie", "pentru moldoveni", "copii nascuti in Italia", "acte necesare", "dubla cetatenie", "avantaje" |
| ro/it | examen b1 italiana | 4 | "per cittadinanza italiana" |
| ro/it | rezidenta italia / pensie italia / somaj italia | **10** / **10** / **10** | residenza, pensione italiana in Moldova/Romania, disoccupazione (NASpI) |
| ucraino uk/it | громадянство Італії (cittadinanza) | **10** | "per ucraini", "per matrimonio", "documenti", "giuramento" |
| uk/it | тимчасовий захист Італія (protezione temporanea) | **10** | "pagamenti", "2026", "proroga", "per uomini"; altra ricerca: "продовження… до 2028" |
| uk/it | пермессо (permesso) | **10** | "verificare", "familiare", "conversione" |
| russo ru/it | гражданство Италии / пермессо ди соджорно / ВНЖ Италия | **10** / **10** / **10** | "per matrimonio", "verificare", "per ucraini 2026", "documenti" |
| cinese zh/it | 意大利长期居留 (permesso di lungo periodo) | **10** | "rinnovo: che documenti", "reddito", "differenza con il permanente", "posso lavorare in Germania" |
| zh/it | 意大利居留 (permesso) | **10** | "verifica", "come compilare il modulo 2025" |
| zh/it | 意大利家庭团聚 (ricongiungimento) | 7 | **"reddito 2026"**, "documenti", "nulla osta", "stato della pratica" |
| zh/it | 意大利国籍 / 入籍 (cittadinanza) | 3 / 2 | "condizioni" (la Cina non ammette la doppia cittadinanza) |
| tagalog tl/it, tl/ph | "carta di soggiorno", "permesso di soggiorno" | 10 / 10 | ma i suggerimenti sono in inglese e italiano ("meaning", "status check") |
| spagnolo es/it | examen b1 italiano / permiso de residencia italia | **10** / **10** | "ejemplo", "online gratis", "para ciudadanía", "fechas"; "para colombianos, peruanos, venezolanos" |
| es/it, es/pe | ciudadanía italiana por residencia | 4 | "requisitos"; il resto di "ciudadanía italiana" è per discendenza (bisnietos argentinos, Uruguay) |
| inglese en/it | b1 italian exam / b1 italian citizenship / cils b1 / celi b1 | **10** ciascuno | "for citizenship", "sample", "past papers", "exam dates", "results", "london", "uk" |
| en/it | italian citizenship by marriage / by residence / application / processing time | 10 / 10 / 10 / 8 | "language requirements", "requirements", "portal", "waiting time" |
| en/it | carta di soggiorno / permesso di soggiorno / family reunification italy | 10 / 10 / 10 | "requirements", "check online", "appointment" |
| en/it | cils exam dates / cils exam in | 10 / 6 | "2026", "2027", "dublin", "india", "fees in india" |

**Domanda per città fuori dall'italiano: zero.** "b1 italian exam milan/rome" 0, "italian citizenship exam milan" 0, "громадянство італії мілан" 0, "examen b1 italiana milano" 0, "意大利语b1考试 米兰" 0, "امتحان اللغة الايطالية للجنسية" 0, "b1 পরীক্ষা" 0. Il modello "una pagina per città" vale solo in italiano: nelle altre lingue si traducono le guide, non le città.

---

## 3. Chi c'è oggi nei risultati (ricerca web, 31/10/2026)

| Lingua | Ricerca provata | Chi c'è | Buco |
|---|---|---|---|
| inglese | "italian citizenship by residence income requirement prefettura B1 documents" | PDF in inglese della Prefettura, studi legali e consulenti (italiancitizenshipassistance, arlettipartners, italyhandbook, visafalcon), The Local, un blog di corsi di lingua (migaku) | nessuno mette insieme sedi, date, costi per città, redditi aggiornati e Prefettura |
| inglese | "carta di soggiorno requirements income 2026" | italyhandbook, migaku, due siti `pages.dev` di contenuti generati (wheretoemigrate, italopedia), Western Union blog in italiano, PDF Questura | **nessuno dà la cifra 2026** del reddito (assegno sociale) |
| inglese | "CILS B1 cittadinanza exam dates 2026 cost" | Istituti di cultura esteri (Melbourne, Sydney, Zurigo), università estere (Cardiff, Brema), IH London, Unipa, una guida di studio (open-exam-prep) | per le sedi **in Italia** quasi niente in inglese |
| bangla | "ইতালি গ্রীন কার্ড পেতে কত বছর লাগে" | solo pagine inglesi sulla green card USA e blog di investimento | nessuna pagina bangla seria; però Google traduce già i risultati in bengalese (sez. 4) |
| ucraino | "громадянство італії для українців документи" | una notizia di 24tv.ua, PDF di Caritas/AVSI/Bocconi (guide per i rifugiati), pagine di viaggio | **buco vero**: nessuna guida completa e aggiornata |
| cinese | "意大利长期居留更新需要什么材料 收入" | portale di notizie per cinesi in Europa (apearth.com), guide PDF in cinese della Regione Piemonte, The Local | la cifra del reddito non c'è |
| arabo | "تجديد الاقامة في ايطاليا شروط" | studyshoot, persmind, almaal: siti di contenuti con pubblicità, centrati sugli studenti | media: c'è concorrenza di bassa qualità; Google traduce anche in arabo |
| rumeno | "cetatenie italiana pentru romani acte necesare" | forum (avocatnet), notizie (gandul, adevarul), PDF di Comuni rumeni | **buco vero**: nessuna guida ordinata |

Il portale del Ministero del Lavoro per i migranti (`integrazionemigranti.gov.it`, 200) è in italiano con un solo link inglese. Le guide multilingue ufficiali sono PDF regionali (Piemonte) o di associazioni: utili come fonte, non ordinate per tema e non aggiornate per il 2026.

---

## 4. Traduzione automatica fatta e controllata da agenti: basta? Google l'accetta?

**Cosa scrive Google (letto il 31/10/2026, `developers.google.com/search/docs/essentials/spam-policies`, 200):** è "scaled content abuse" generare molte pagine "per manipolare il posizionamento e non per aiutare gli utenti", e tra gli esempi c'è "Scraping feeds, search results, or other content to generate many pages (including through automated transformations like synonymizing, **translating**, or other obfuscation techniques), **where little value is provided to users**". La pagina sui contenuti generati (`using-gen-ai-content`, 200) dice lo stesso: lo strumento è ammesso, il problema sono "many pages without adding value". **Tradurre non è vietato; è vietato tradurre in massa pagine senza valore per chi legge.**

**Fatto nuovo che cambia la scelta delle lingue** (`developers.google.com/search/docs/appearance/translated-results`, 200): Google traduce da solo titolo e anteprima dei risultati, e la pagina se l'utente clicca, quando chi cerca usa **arabo, bengalese, inglese, francese, tedesco, gujarati, hindi, indonesiano, kannada, coreano, malayalam, marathi, persiano, portoghese, spagnolo, tamil, telugu, thai, turco, urdu, vietnamita**. Quindi chi cerca in bangla, urdu, hindi o arabo **può già vedere le nostre pagine italiane o inglesi tradotte da Google**. **Ucraino, russo, rumeno, cinese e albanese non ci sono**: lì solo una pagina scritta in quella lingua compete.

**Qualità della traduzione da agenti (giudizio, non misura):** buona per inglese, spagnolo, rumeno, ucraino, russo, cinese (lingue con moltissimi testi in rete); discreta per arabo e bangla; più incerta per urdu e punjabi. Il rischio vero non è la grammatica ma il **contenuto legale sbagliato** in un tema delicato (cittadinanza e permessi: Google li tratta come temi "che toccano la vita delle persone"). Le regole per ridurlo:
1. **Si traducono solo le guide con domanda** (10-25 pagine per lingua), mai le 89 pagine città e le 30 Prefetture una per una: nelle altre lingue la domanda per città è zero (sez. 2). In inglese basta **una** pagina "Exam dates and centres in Italy" con la tabella di tutte le città.
2. **Numeri, date, importi e nomi degli uffici vengono dai file JSON** già usati per l'italiano (`sessioni.json`, `redditi.json`, `prefetture.json`…), non dal testo tradotto: un errore di traduzione non può cambiare una cifra.
3. **Le parole che il lettore trova sui moduli restano in italiano**, con spiegazione accanto: permesso di soggiorno, carta di soggiorno, Prefettura, Questura, kit postale, CILS, CELI. Un glossario fisso per lingua.
4. **Due agenti diversi:** uno traduce, un revisore indipendente ritraduce in italiano e confronta frase per frase con l'originale (lista di 30 fatti da ritrovare uguali), più il controllo di design come per ogni sezione (8,5/10).
5. **In alto su ogni pagina:** "Tradotto dalla versione italiana e controllato il [data]. In caso di dubbio vale la versione italiana" con il link. Niente nomi di strumenti.
6. `lang` giusto, `hreflang` tra le versioni, canonical su sé stessa; per l'arabo pagina da destra a sinistra.
7. **Soglia:** se una lingua a 45 giorni ha meno di 100 impressioni al mese, si congela (resta online, niente più lavoro); a 90 giorni sotto 300, si toglie dalla sitemap.

Con queste regole la traduzione è accettabile: pagine poche, con dati veri e utili a un pubblico che esiste. Senza (tutto il sito × 12 lingue in un giorno) è il caso che Google punisce, e il danno colpirebbe anche la parte italiana di EsameB1, che è il motore della rete.

---

## 5. Chi paga in queste lingue

**AdSense: lingue ammesse** (`support.google.com/adsense/answer/9727`, 200): arabo, bengalese, cinese, filippino, hindi, punjabi, rumeno, russo, spagnolo, ucraino, urdu, inglese, italiano sì. **Albanese no**: "Placing Google ad code on pages with content primarily in an unsupported language is not permitted". Pagine in albanese = zero pubblicità.

**Quanto vale AdSense (stima, nessun dato nostro: AdSense non ha ancora incassi).** Riferimento del cruscotto (30/10): 3-5 € ogni 1.000 visite in italiano, 6-10 € in inglese da USA/Regno Unito. Conta **dove sta** chi legge: chi legge in ucraino dall'Italia vede aste italiane (ma con pochi inserzionisti in ucraino); chi legge in bangla dal Bangladesh vale ~0,3-0,6 €. Stime usate: inglese misto 4 € ogni 1.000 pagine, rumeno dall'Italia 2-3 €, ucraino/russo e cinese dall'Italia 1,5-2,5 €, arabo e spagnolo misti 1,5-2,5 €, bangla misto 1-1,5 €.

**Altri pagatori:**
- **italki** (già attivo su EsameB1: 18 $ per nuovo studente al primo acquisto, `esameb1/dati/affiliati.json`): funziona in tutte le lingue, perché tutti devono passare l'orale del B1. È il pagatore principale delle pagine lingua. Preply e Babbel restano da iscrivere (ESPLORATE: 10-15 $ e fino a 75 €).
- **Rimesse.** Fatti: dall'Italia sono partiti **8,6 miliardi di € nel 2025** (+3,9 %), il Bangladesh primo con **~1,7 miliardi (19,6 %)** (Banca d'Italia, riportata da Avvenire e AziendaBanca). **Wise:** 10 £ per nuovo cliente privato che fa un'operazione tra valute (guida ufficiale per gli affiliati; Partnerize). **Remitly:** 1,60 $ al primo invio nel programma USA su FlexOffers; per l'Europa c'è un programma "ambassador" con cifra per Paese che non è pubblica. **WorldRemit:** cifra non trovata. Domanda: "send money from italy to pakistan" 7, "…to india" 9, "…to philippines" 5, "…to bangladesh" 3; in bangla "ইতালি থেকে বাংলাদেশে টাকা পাঠানোর নিয়ম" 6 (anche "su bKash"); in arabo "تحويل الاموال من ايطاليا الى المغرب / تونس / مصر" 6; rumeno "transfer bani italia romania" 5; ucraino 1. Le ricerche sul cambio ("euro to bdt taptap", "euro to pkr tap tap", "ইউরো রেট" 8) le vince il convertitore di Google e l'app più usata (Taptap Send) **non ha un programma di affiliazione pubblico**. Conclusione: niente pagine sulle rimesse (come il NO del 31/10 in italiano), ma **un riquadro Wise nelle pagine lingua** quando Massimiliano si iscrive.
- **Corsi di italiano:** "corso italiano b1 online" 6 in italiano, "italian course online b1" 7 in inglese, "ইতালিয়ান ভাষা শিক্ষা কোর্স" in bangla: stesso riquadro di italki.
- **Traduzioni giurate:** "italian sworn translation" 10 (anche "in islamabad"), "traduzione giurata" 10, ma sono servizi locali senza affiliazione; NO già del 26/10 confermato.
- **Assicurazioni:** pista nuova, in italiano: "assicurazione permesso di soggiorno" **10** ("sanitaria", "allianz", "studenti stranieri", "per rinnovo"). Serve per studenti, residenza elettiva e genitori ricongiunti over 65. Si apre solo se si trova un programma con commissione scritta: oggi **RISERVA** (riga 12).
- **Libro:** la collana KDP "Esame B1 cittadinanza" (`idee-2026-10-31-vincenti.md`, idea 3) avrebbe nella versione inglese di EsameB1 un secondo canale (coniugi all'estero: "b1 italian exam preparation book" è tra i suggerimenti da Bangladesh e India).

---

## 6. Le idee una per una

Formula: visite al mese a 18 mesi × 12 × € ogni 1.000 visite ÷ 1.000. € ogni 1.000 visite = AdSense (1,5 pagine a visita × € ogni 1.000 pagine) + italki + altro.

### Idea 1. EsameB1 in inglese (`/en/`) — voto 7,5

**Cosa:** ~25 pagine: home, how it works, cost, the four exams (CILS, CELI, PLIDA, CERT.IT), sample tests, results, exemptions, **una sola pagina "Exam dates and centres in Italy"** con la tabella di tutte le città (dai dati esistenti), income requirements 2026 con calcolatore (cittadinanza, carta di soggiorno, ricongiungimento), citizenship by residence, **citizenship by marriage and the B1 requirement**, applying at the Prefettura (una guida + tabella delle Prefetture), carta di soggiorno, family reunification. Link "English" in testata di ogni pagina italiana corrispondente.

**Numeri ufficiali:** ~1,0 milione di residenti che leggono in inglese (sez. 1); 22.845 cittadinanze per matrimonio nel 2025, una parte con coniuge che vive all'estero.
**Domanda:** 10 su "b1 italian exam", "b1 italian citizenship", "cils b1", "celi b1", "italian citizenship by marriage" ("language requirements"), "carta di soggiorno", "family reunification italy", "italy citizenship / nationality for pakistani", "italy family visa" (pk, bd); "cils exam dates" 10 ("2026", "2027").
**Concorrenza:** consulenti e studi legali (soprattutto discendenza), italyhandbook, The Local, siti di contenuti generati su `pages.dev`, Istituti di cultura all'estero. Nessuno ha sedi, date e costi delle sessioni **in Italia** né la cifra 2026 del reddito per la carta di soggiorno. Buco 1,5.
**Fonti:** le stesse dell'italiano; in più la Prefettura e la Questura hanno PDF ufficiali in inglese (`prefettura.interno.gov.it/.../in-_section_2_citizenship_by_residence.pdf`, `questure.poliziadistato.it/.../list-of-documents-required-for-issue--renewal-of-residence-permits.pdf`): il revisore può confrontare i termini.
**Canale in più:** ChatGPT, che oggi porta un terzo delle visite e cerca spesso in inglese (Visa Income: 94 visite su 130, Pakistan in testa).
**Chi paga:** AdSense (misto: Italia ~4 €, USA/Regno Unito 6-10 €, Sud dell'Asia ~0,5-1 € ogni 1.000 pagine), italki, Amazon/libro.

**Stima a 18 mesi:**
- Prudente: 1.500 visite/mese × 12 × 7 € (AdSense 1,5 × 3 € = 4,5 + italki 2 + altro 0,5) ÷ 1.000 = **126 €/anno**
- Centrale: 5.000 × 12 × 10 € (AdSense 1,5 × 4 € = 6 + italki 3 + altro 1) ÷ 1.000 = **600 €/anno**
- Ottimista: 15.000 × 12 × 14 € (AdSense 1,5 × 5,5 € = 8,3 + italki 4,5 + libro 1,2) ÷ 1.000 = **2.520 €/anno**
Base: EsameB1 in italiano è passato da 48 a 329 visite a settimana in tre settimane (~1.400 al mese); l'inglese ha più lettori ma più concorrenza e nessuna domanda per città.
**Primi soldi:** italki dal giorno della pubblicazione (già attivo); AdSense con l'indicizzazione (2-6 settimane).
**Ore:** 25-35, di cui 12-18 per insegnare al generatore le lingue (oggi `lang="it"`, testata, piede e modulo solo in italiano: tabella dei testi per lingua, percorsi `/en/`, `hreflang`, sitemap) e 10-15 per testi, revisione e design. Lavoro che serve poi a tutte le altre lingue. Esce con la pubblicazione del lunedì di EsameB1: nessun credito Netlify in più.
**Voto 7,5** (domanda 3 · buco 1,5 · fonte 2 · chi paga 0,5 · rischi e ore 0,5). Sotto i 5.000 €: sezione, non sito.

### Idea 2. Ucraino, poi russo (`/uk/`, `/ru/`) — voto 7

**Cosa:** ~15 pagine in ucraino, poi le stesse in russo (per chi viene da Ucraina dell'est, Russia, Moldova, Georgia): cittadinanza (residenza, matrimonio, documenti, giuramento), esame B1 (cos'è, quanto costa, come esercitarsi, date in tabella), permesso di soggiorno (verifica online, rinnovo, familiare), **protezione temporanea: scadenza, proroghe e conversione in permesso di lavoro**, carta di soggiorno, redditi 2026 con calcolatore.
**Numeri ufficiali:** Ucraina 287.187 residenti (**215.112 donne**, molte assistenti familiari con poco italiano scritto), Russia 43.119, Georgia 36.490, Moldova 94.141 (in parte russofona).
**Domanda:** "громадянство італії" 10 (anche da `gl=ua`), "тимчасовий захист італія" 10 (2026, proroga, "per uomini"), "пермессо" 10 ("verificare", "conversione"), russo "гражданство италии" 10, "пермессо ди соджорно" 10, "внж италия" 10.
**Concorrenza:** notizie (24tv.ua), PDF di Caritas, AVSI e Bocconi per i rifugiati. **Google non traduce i risultati in ucraino e russo**: le pagine inglesi e italiane non competono. Buco 1,5.
**Fonti:** DLCI, Prefetture, `redditi.json`, Questura; per la protezione temporanea le decisioni del Consiglio UE e le circolari del Ministero dell'Interno (da leggere al momento della costruzione: la data di fine va scritta solo con il documento in mano).
**Chi paga:** AdSense in ucraino/russo dall'Italia (stima 1,5-2,5 € ogni 1.000 pagine), italki, Wise (euro → grivnia; 10 £).
**Stima:** prudente 1.000 × 12 × 2,5 € = **30 €**; centrale 4.000 × 12 × 3,5 € = **168 €**; ottimista 12.000 × 12 × 5 € = **720 €/anno**. Picco possibile alla scadenza della protezione temporanea (molti dovranno convertire il permesso).
**Ore:** 8-12 per l'ucraino (dopo l'idea 1), 4-6 per il russo.
**Voto 7** (domanda 2,5 · buco 1,5 · fonte 2 · chi paga 0,5 · rischi e ore 0,5).

### Idea 3. Rumeno (`/ro/`) — voto 6,5

**Cosa:** ~12 pagine: cittadinanza per i cittadini UE (4 anni) e per i moldavi (10 anni), per matrimonio, figli nati in Italia, doppia cittadinanza, documenti, esame B1, redditi con calcolatore, iscrizione anagrafica dei cittadini UE.
**Numeri ufficiali:** Romania 1.053.042 + Moldova 94.141 = **la comunità più grande** (1,15 milioni).
**Domanda:** "cetatenie italiana" 10 ("pentru romani", "prin casatorie", "pentru moldoveni", "copii nascuti in italia", "acte necesare", "dubla cetatenie", "avantaje"), "rezidenta italia" 10, "examen b1 italiana" 4.
**Concorrenza:** forum e giornali, nessuna guida ordinata. **Google non traduce in rumeno.** Buco 1. Limite: molti rumeni leggono bene l'italiano (lingua vicina, anni di residenza): parte della domanda è già servita da EsameB1 in italiano.
**Chi paga:** AdSense rumeno dall'Italia (2-3 €), italki, Wise (euro → lei; "transfer bani italia romania" 5).
**Stima:** prudente 1.000 × 12 × 3 € = **36 €**; centrale 3.500 × 12 × 4 € = **168 €**; ottimista 10.000 × 12 × 6 € = **720 €/anno**.
**Ore:** 8-12. **Voto 6,5** (domanda 2,5 · buco 1 · fonte 2 · chi paga 0,5 · rischi e ore 0,5).

### Idea 4. Arabo (`/ar/`) — voto 6

**Numeri:** Marocco 412.457, Egitto 174.141, Tunisia 123.828 (~0,71 milioni).
**Domanda:** rinnovo del permesso 9, ricongiungimento 10, permesso 7-10, esame di italiano b1 nei suggerimenti; **cittadinanza 0 in quattro forme** (anche da Marocco ed Egitto).
**Concorrenza:** siti di contenuti con pubblicità (studyshoot, persmind, almaal); **Google traduce già in arabo**. Buco 1.
**Chi paga:** AdSense arabo misto (Italia e Nord Africa), italki. La parte visti è già in coda come rifiuti dei visti in arabo dentro Visa Income (PASSA del 21/10): costruirle insieme.
**Stima:** 800 × 12 × 2,5 € = **24 €**; 3.000 × 12 × 3,5 € = **126 €**; 9.000 × 12 × 5 € = **540 €/anno**. **Ore** 12-18 (pagina da destra a sinistra, caratteri). **Voto 6** (2 · 1 · 2 · 0,5 · 0,5).

### Idea 5. Cinese (`/zh/`) — voto 6

**Numeri:** 311.250. **Domanda:** permesso di lungo periodo 10 ("rinnovo", "reddito", "differenza con il permanente"), permesso 10 ("verifica"), ricongiungimento 7 ("**reddito 2026**", "documenti", "nulla osta"); cittadinanza 2-3 (la Cina non ammette la doppia cittadinanza: il B1 per la cittadinanza interessa poco, il B1/A2 per il lungo periodo sì).
**Concorrenza:** portali di notizie per cinesi in Europa, guide PDF regionali; molto passa da WeChat, fuori da Google. **Google non traduce in cinese.**
**Chi paga:** AdSense cinese semplificato, italki. **Stima:** 500 × 12 × 2,5 € = **15 €**; 2.000 × 12 × 3,5 € = **84 €**; 6.000 × 12 × 5 € = **360 €/anno**. **Ore** 8-12. **Voto 6** (2 · 1 · 2 · 0,5 · 0,5). Pagine giuste: redditi (lungo periodo e ricongiungimento), non la cittadinanza.

### Idea 6. Spagnolo (`/es/`) — voto 5,5

**Numeri:** ~0,27 milioni di latinoamericani residenti (Perù 116.169, Ecuador 57.980, Rep. Dominicana 30.200, Colombia 26.395, El Salvador 25.880, Venezuela 16.981) + Spagna 30.074.
**Domanda:** "examen b1 italiano" 10 (ma con città spagnole: "granada"), "permiso de residencia italia" 10, "reagrupación familiar italia" 7 ("ecuador"), "ciudadanía italiana por residencia" 4. Il grosso di "ciudadanía italiana" è per **discendenza** dall'estero, presidiato da agenzie. Gli ispanofoni leggono bene l'italiano. Google traduce in spagnolo.
**Stima:** 800 × 12 × 2 € = **19 €**; 3.000 × 12 × 3 € = **108 €**; 9.000 × 12 × 4,5 € = **486 €/anno**. **Ore** 6-10. **Voto 5,5** (1,5 · 1 · 2 · 0,5 · 0,5). Utile solo per il B1 dei coniugi all'estero (RISERVA del 21/10).

### Idea 7. Bangla (`/bn/`, poche pagine) — voto 5

**Numeri:** 213.622 residenti, primi per rimesse (~1,7 mld € nel 2025).
**Domanda:** forte sui **visti dal Bangladesh** (visto di lavoro, "in che data" = decreto flussi, visto familiare 10) e media sulla "green card" (= carta di soggiorno, 3-4) e sulla cittadinanza (3); **0 su esame, rinnovo, permesso**. I suggerimenti da `gl=it` e `gl=bd` sono quasi identici: cerca soprattutto chi vive in Bangladesh, che vale poco in pubblicità (~0,3-0,6 €) e non fa il B1. Chi vive in Italia cerca in inglese ("italy green card bangla", "italy citizenship for bangladeshi"). Google traduce in bengalese.
**Cosa farebbe senso:** 3-5 pagine ("ইতালি গ্রীন কার্ড": cos'è la carta di soggiorno, quanti anni, reddito; cittadinanza: quanti anni, B1; visto familiare: reddito del ricongiungimento), dopo l'inglese.
**Stima:** 500 × 12 × 2 € = **12 €**; 2.000 × 12 × 3 € = **72 €**; 6.000 × 12 × 5 € = **360 €/anno**. **Ore** 8-12 (caratteri bengalesi, revisione più incerta). **Voto 5** (1,5 · 1 · 2 · 0 · 0,5).

### Idea 8. Urdu, punjabi, hindi — NO (3,5)

Pakistan 171.179 e India 171.429 residenti, ma **0 suggerimenti** sui nostri temi in urdu (cittadinanza, permesso, carta, visto familiare), punjabi (anche "ਇਟਲੀ ਵੀਜ਼ਾ" 0) e hindi (cittadinanza 0). Le ricerche sono in inglese e Google traduce già in urdu e hindi. Conferma il NO del 21/10 per Visa Income in urdu e hindi. Coperti dall'idea 1. **Voto 3,5** (0 · 1 · 2 · 0 · 0,5).

### Idea 9. Albanese — NO (3)

414.622 + 36.180 residenti (molti con cittadinanza già acquisita o in corso), ma domanda 0-6 ("nenshtetesia italiane" 1, "dokumentet qe duhen per nenshtetesi italiane" 1, "bashkim familjar itali" 6) e soprattutto **AdSense non ammette l'albanese**. Gli albanesi in Italia leggono l'italiano. **Voto 3** (0,5 · 0,5 · 2 · 0 · 0).

### Idea 10. Tagalog — NO (3)

153.455 filippini, ma cercano in inglese e italiano (sez. 2). Coperti dall'idea 1. **Voto 3**.

### Idea 11. Rimesse — NO come pagine (4), SÌ come riquadro

Vedi sez. 5. Come pagine: domanda bassa in tutte le lingue (3-9), risultati di Wise, Remitly, Monito e banche, l'app più usata senza affiliazione. Come **riquadro Wise** dentro le pagine lingua (sotto "redditi" e "ricongiungimento", con la frase "per mandare soldi a casa"):
- Prudente: 6.100 visite/mese sulle pagine lingua (somma delle idee 1-7) × 0,01 % = 0,6 clienti nuovi × 11,6 € (10 £) × 12 = **85 €/anno**
- Centrale: 22.500 × 0,01 % = 2,25 × 11,6 × 12 = **313 €/anno**
- Ottimista: 67.000 × 0,02 % = 13,4 × 11,6 × 12 = **1.865 €/anno**
Serve l'iscrizione di Massimiliano a Wise (Partnerize). **Ore** 2-3. **Voto 4** come pagine (1,5 · 0 · 1 · 1 · 0,5).

### Idea 12. Assicurazione sanitaria per il permesso di soggiorno — RISERVA (5,5)

Scoperta di passaggio, in italiano: "assicurazione permesso di soggiorno" **10** ("sanitaria", "allianz", "studenti stranieri", "per rinnovo"). Si riapre come sezione di EsameB1 solo con un programma di affiliazione con commissione scritta, letto sulla pagina del programma. Prossimo passo: cercare il programma (non fatto oggi).

---

## 7. Conclusione: quali lingue fare per prime e come

**Ordine:**
1. **Inglese** (idea 1), subito dopo le sezioni già in coda su EsameB1 (redditi, Prefetture). È la lingua dei lettori del Sud dell'Asia, delle Filippine e dell'Africa occidentale, è la lingua in cui ChatGPT ci trova, e il lavoro sul generatore serve a tutte le lingue dopo.
2. **Ucraino, poi russo** (idea 2): domanda forte nella lingua madre, Google non traduce, lettrici con poco italiano scritto, scadenza della protezione temporanea in arrivo.
3. **Rumeno** (idea 3): la comunità più grande, "cetatenie italiana" 10, Google non traduce.
Arabo e cinese dopo, solo se le prime tre passano la soglia dei 45 giorni; l'arabo insieme ai rifiuti dei visti in arabo di Visa Income. Bangla con 3-5 pagine solo dopo l'inglese. Urdu, punjabi, hindi, tagalog, albanese: no.

**Come: sezioni di EsameB1 (`/en/`, `/uk/`, `/ru/`, `/ro/`), non siti separati.**
- Nessuna idea arriva a 5.000 €/anno nel centrale: un sito nuovo non passa l'asticella (voto ≥ 7 e ≥ 5.000 €).
- EsameB1 ha già la fiducia di Google (3.570 impressioni, posizione 7,3, crescita ×2,9 in una settimana): una sezione nuova parte da lì, un sito nuovo da zero.
- Nessun sito nuovo su Netlify da creare per Massimiliano e nessun credito in più: le pagine escono con la pubblicazione del lunedì.
- `hreflang` tra italiano e le altre lingue: Google mostra a ciascuno la versione giusta.

**Quanto vale (stima):** inglese + ucraino/russo + rumeno = **~190 / 940 / 3.960 €/anno** a 18 mesi (prudente / centrale / ottimista), più la quota del riquadro Wise. Tutte le lingue utili insieme (idee 1-7 e 11): **~350 / 1.640 / 7.570 €/anno**. Ore: ~45-65 per le prime tre lingue.

**Soglie scritte prima:** per ogni lingua, a 45 giorni ≥ 100 impressioni al mese in Search Console (filtro per cartella `/en/`, `/uk/`…), altrimenti si congela; a 90 giorni ≥ 300 impressioni, altrimenti si toglie dalla sitemap. La lingua successiva parte solo se la precedente passa i 45 giorni.

**Cosa serve da Massimiliano:** niente per costruire. Per guadagnare di più: l'iscrizione a Wise (Partnerize) quando si accende il riquadro; nessuna spesa.

---

## 8. Righe per ESPLORATE (da copiare dalla sessione principale)

| Nicchia | Esito | Studio |
|---|---|---|
| **EsameB1 in inglese** (`/en/`, ~25 pagine; ~1,0 mln residenti che leggono in inglese; "b1 italian exam", "cils b1", "italian citizenship by marriage", "carta di soggiorno", "italy family visa" 10; urdu/punjabi/hindi 0; nessuno ha sedi e date in Italia in inglese; PDF ufficiali in inglese di Prefettura e Questura) | **SEZIONE da costruire** (voto 7,5; 126 / 600 / 2.520 €/anno; 25-35 ore, di cui 12-18 per le lingue nel generatore) | fronti-2026-10-31-lingue-immigrati |
| **EsameB1 in ucraino, poi russo** (287.187 + 43.119 residenti; "громадянство італії" 10, "тимчасовий захист італія" 10, "пермессо" 10, "гражданство италии" 10; Google non traduce i risultati in ucraino e russo) | **SEZIONE in coda** dopo l'inglese (voto 7; 30 / 168 / 720 €/anno; 12-18 ore) | fronti-2026-10-31-lingue-immigrati |
| EsameB1 in rumeno (1.053.042 + 94.141 moldavi; "cetatenie italiana" 10 con "pentru romani/moldoveni"; Google non traduce in rumeno) | SEZIONE in coda (voto 6,5; 36 / 168 / 720 €/anno; 8-12 ore) | fronti-2026-10-31-lingue-immigrati |
| EsameB1 in arabo (permesso e ricongiungimento 7-10, cittadinanza 0; Google traduce in arabo; siti di contenuti in prima pagina) | dopo le prime tre, insieme ai rifiuti in arabo di Visa Income (voto 6; 24 / 126 / 540 €/anno) | fronti-2026-10-31-lingue-immigrati |
| EsameB1 in cinese (lungo periodo 10, ricongiungimento "reddito 2026" 7, cittadinanza 2-3) | dopo le prime tre (voto 6; 15 / 84 / 360 €/anno) | fronti-2026-10-31-lingue-immigrati |
| EsameB1 in spagnolo (domanda soprattutto per discendenza dall'estero) | RISERVA (5,5) | fronti-2026-10-31-lingue-immigrati |
| EsameB1 in bangla (domanda da chi vive in Bangladesh: visti, decreto flussi; "green card" 3-4; esame e rinnovo 0) | 3-5 pagine solo dopo l'inglese (voto 5) | fronti-2026-10-31-lingue-immigrati |
| Guide in urdu, punjabi, hindi, tagalog | NO (3-3,5): 0 suggerimenti sui nostri temi, cercano in inglese; Google traduce già in urdu e hindi | fronti-2026-10-31-lingue-immigrati |
| Guide in albanese | NO (3): domanda 0-6 e AdSense non ammette l'albanese | fronti-2026-10-31-lingue-immigrati |
| Pagine sulle rimesse nelle lingue (Wise 10 £, Remitly 1,60 $ USA; 8,6 mld € dall'Italia nel 2025, Bangladesh ~1,7 mld) | NO come pagine (4); **riquadro Wise** nelle pagine lingua dopo l'iscrizione (85 / 313 / 1.865 €/anno) | fronti-2026-10-31-lingue-immigrati |
| Assicurazione sanitaria per il permesso di soggiorno ("assicurazione permesso di soggiorno" 10) | RISERVA (5,5): manca un programma con commissione scritta | fronti-2026-10-31-lingue-immigrati |

---

## 9. Fonti lette (31/10/2026)

- Suggerimenti di Google: `https://suggestqueries.google.com/complete/search?client=firefox&hl=<lingua>&gl=<Paese>&q=<testo>` (~170 richieste; risultati salvati nella cartella temporanea della sessione, non nel repository).
- Residenti per cittadinanza al 1/1/2025 (dati ISTAT): `https://www.tuttitalia.it/statistiche/cittadini-stranieri-2025/` (200, 85,8 kB). Totale 1/1/2026: ISTAT, `https://www.istat.it/wp-content/uploads/2026/03/Report_Indicatori-demografici_Anno-2025.pdf` (da ricerca web).
- ISTAT SDMX: elenco dei flussi `https://esploradati.istat.it/SDMXWS/rest/dataflow/IT1` (200, 4,25 MB: nessun flusso "stranieri per cittadinanza"); acquisizioni `29_849_DF_DCIS_ACQCITIZ_3` (200, solo totale "WORLD").
- Google, norme contro lo spam: `https://developers.google.com/search/docs/essentials/spam-policies?hl=en` (200).
- Google, contenuti generati: `https://developers.google.com/search/docs/fundamentals/using-gen-ai-content?hl=en` (200).
- Google, risultati tradotti: `https://developers.google.com/search/docs/appearance/translated-results?hl=en` (200).
- AdSense, lingue ammesse: `https://support.google.com/adsense/answer/9727?hl=en` (200).
- Wise, guida per gli affiliati: `https://wise.com/gb/blog/affiliate-onboarding-guide` (da ricerca web: "CPA rates start at £10 for personal users").
- Remitly su FlexOffers: `https://www.flexoffers.com/affiliate-programs/remitly-affiliate-program` (da ricerca web: 1,60 $ al primo invio, USA); programma ambassador europeo: `https://www.remitly.com/home/ambassador-tnc`.
- Rimesse 2025: Avvenire, `https://www.avvenire.it/attualita/rimesse-dei-migranti-dallitalia-86-miliardi-alle-famiglie-dorigine_107005`; AziendaBanca, `https://www.aziendabanca.it/notizie/banche/rimesse-migranti-2025` (dati Banca d'Italia).
- PDF ufficiali in inglese: `https://prefettura.interno.gov.it/sites/default/files/98/2023-12/in-_section_2_citizenship_by_residence.pdf`; `https://questure.poliziadistato.it/statics/30/list-of-documents-required-for-issue--renewal-of-residence-permits.pdf` (da ricerca web).
- Portale migranti del Ministero del Lavoro: `https://www.integrazionemigranti.gov.it/it-it/` (200, 2,8 MB; un solo link `/en-gb/`).
- GoatCounter: `stats/locations` e `stats/languages`, 17-31/10/2026.
- Ricerche web (dagli USA) per la prima pagina: le 8 ricerche della sez. 3.
