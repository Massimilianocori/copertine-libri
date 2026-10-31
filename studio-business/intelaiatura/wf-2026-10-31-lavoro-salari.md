# Lavoro e salari: minimi, contratti, stipendi per professione, permessi stagionali (31/10/2026)

**Angolo assegnato:** settore lavoro. Salari minimi e contratti per Paese o regione, stipendi ufficiali per professione (BLS OES, ONS ASHE, ISTAT), permessi per lavoratori stagionali. Esclusi per ordine: le soglie nazionali dei visti di lavoro già in Visa Income Checker e il decreto flussi.

**Letto prima:** skill `rete-siti` (metodo, voto severo, asticella: siti nuovi solo con voto ≥ 7 e ≥ 5.000 €/anno nel caso centrale; sezioni se costano zero e il guadagno atteso è positivo), `REGOLE-FISSE.md` (regole del 31/10: fronti nuovi, conta il fatturato, niente lavori a ore di Massimiliano), `ESPLORATE.md` per intero e i rapporti di oggi (`wf-2026-10-31-*.md`, `fronti-2026-10-31-*.md`).

**Già chiusi e non rifatti:** CCNL (NO), salari per professione e città BLS/ONS (23/10, NO: `bls.gov` 403), salario minimo 2027 per Stato USA (22/10), visti stagionali UK/USA/Australia (22/10), salari H-1B e Davis-Bacon (14/10), award rates australiani (16/10), paghe pubbliche AU/NHS (18/10), working holiday (18/10, 28/10 e oggi in due rapporti), ore di lavoro degli studenti (29/10), paghetta degli au pair, stipendio netto per Paese, regimi per impatriati (oggi, `wf-2026-10-31-strumenti-calcolatori`), datore di lavoro USA Stato per Stato con Gusto (oggi, `fronti-2026-10-31-nicchie-ricche` e verifica), sussidi di disoccupazione USA (oggi, due rapporti).

## In breve

- **Nessuna idea passa l'asticella dei siti nuovi.** Il settore lavoro è il più presidiato visto finora: per ogni numero ufficiale (salario minimo, tariffa, contributo) ci sono già l'ente, i sindacati, i giornali e da 3 a 10 siti automatici (molti su `pages.dev`).
- **Una sola sezione da costruire, piccola:** "lavoro per professione" in Visa Income Checker (soglia per codice di professione nel Regno Unito, più gli elenchi ufficiali di Australia e Irlanda). Fonte perfetta (JSON ufficiale aggiornato il 29/10/2026), domanda vera per codice ("soc code 2136 salary", "chef skilled worker visa"), ma concorrenti automatici già in pagina. Voto 5,5; 15 / 120 / 700 €/anno.
- **Cambio di angolo provato (fronte nuovo B2B):** il costo di un dipendente Paese per Paese, con Deel che paga **500 $ per contatto qualificato + 1.000 $ per cliente** (letto sulla pagina ufficiale). È il pagatore più ricco visto nel settore, ma chi paga è anche chi occupa la prima pagina, e ci sono già una decina di calcolatori automatici. Voto 5; 35 / 2.000 / 19.000 €/anno, sotto l'asticella nel caso centrale.
- **Fatti nuovi utili alla rete:** (1) l'interfaccia aperta di Eurostat sui salari minimi risponde 200 (CC BY 4.0, aggiornata il 31/7/2026): serve a tenere aggiornate da sole le soglie di Spagna e Portogallo già in Visa Income; (2) il Giappone ha 47 date diverse di entrata in vigore del minimo 2026 (dal 1/10/2026 al 1/12/2026 e oltre), dato che nessuno in inglese ha in tabella; (3) l'ufficio pubblicazioni dell'UE risponde alle interrogazioni SPARQL anche quando EUR-Lex ha l'anti-robot (202 senza contenuto).

## Tabella delle idee

| # | Idea | Dove | Voto | Prudente / centrale / ottimista €/anno a 18 mesi | Ore | Esito |
|---|---|---|---|---|---|---|
| 1 | Visto di lavoro per professione: soglia per codice SOC (UK, ~350 codici), elenco CSOL/MLTSSL per ANZSCO (Australia), elenchi critical skills (Irlanda) | sezione di Visa Income Checker | 5,5 | 15 / 120 / 700 | 16-24 | **SEZIONE in coda bassa** (rete fitta: costo zero, guadagno positivo) |
| 2 | Costo del datore di lavoro Paese per Paese (contributi, 13ª/14ª, minimo, preavviso) con Deel come pagatore | sito nuovo (nessun sito adatto) | 5 | 35 / 2.000 / 19.000 | 40-60 | **RISERVA** come fronte B2B: sotto l'asticella nel caso centrale |
| 3 | Recepimento della direttiva UE sulla trasparenza salariale (2023/970) Paese per Paese | sito nuovo | 4,5 | 50 / 300 / 1.600 | 25-35 | NO: studi legali e software HR con tracker aggiornati |
| 4 | Soglie dei visti legate al salario minimo aggiornate da Eurostat (Spagna SMI, Portogallo RMMG) | miglioria di Visa Income | 5 | 0 / 60 / 300 | 3-4 | **AGGIUNTA tecnica**, insieme al lavoro già annotato in `wf-2026-10-31-spagna-portogallo-latam` |
| 5 | Salari minimi dei cantoni svizzeri (Ginevra, Neuchâtel, Giura, Ticino, Basilea Città) per frontalieri, in IT/FR/DE | sezione (nessun sito adatto) | 4 | 20 / 150 / 800 | 12-18 | NO: Ticino 000 dal server, giornali e siti per frontalieri forti |
| 6 | Salario minimo del Giappone per prefettura con le 47 date di entrata in vigore, in inglese | sezione di Visa Income | 4,5 | 10 / 80 / 400 | 6-10 | NO come lavoro dedicato; al massimo una tabella se si fa una sezione Giappone |
| 7 | Congedo familiare pagato (PFML) Stato per Stato negli USA, con i programmi nuovi 2026-2028 | sito nuovo | 4 | 50 / 400 / 2.000 | 30-40 | NO: 4 fonti statali su 13 chiuse, calcolatori ufficiali, National Partnership |
| 8 | Minimi di settore in Germania 2027 (Branchenmindestlöhne: pulizie, cura, elettricisti…) | — | 3,5 | — | — | NO: solo in tedesco, DGB e siti di paghe; nessun sito della rete in tedesco |
| 9 | Tabelle GS 2027 per località (dipendenti federali USA) | — | 3 | — | — | NO: federalpay.org, OPM, FedSmith, GovExec |
| 10 | "Stipendio medio [Paese]" in italiano (Eurostat) e visti stagionali in Europa | — | 3-3,5 | — | — | NO: pubblico a bassa resa; i "visa sponsorship jobs" sono terreno di truffe |

## 1. Visto di lavoro per professione (voto 5,5, SEZIONE in coda bassa)

**Cosa sarebbe.** Una sezione "Work visa by occupation" in Visa Income Checker: una pagina per codice di professione del Regno Unito (SOC 2020) con la soglia ufficiale del visto Skilled Worker (tariffa piena, ridotta al 90 %, 80 %, 70 %, all'ora e all'anno), più l'indicazione se la professione è ammessa; per l'Australia, l'elenco ufficiale per codice ANZSCO (CSOL, MLTSSL, visti ammessi, ente che valuta le competenze); per l'Irlanda, gli elenchi critical skills. Pagine "per mestiere" che uniscono i tre Paesi (infermiere, cuoco, sviluppatore software, insegnante…). Non ripete la pagina esistente: oggi `uk-skilled-worker-visa` dà solo la soglia generale (41.700 £) e rimanda a GOV.UK per i codici.

**Fonte (curl 31/10/2026).**
- GOV.UK, Immigration Rules Appendix Skilled Occupations, interfaccia dei contenuti `https://www.gov.uk/api/content/guidance/immigration-rules/immigration-rules-appendix-skilled-occupations` → **200**, 337 kB, JSON con 11 tabelle e 737 righe; aggiornata il **29/10/2026**. Esempio letto: codice 2136 "IT quality and testing professionals" 41.200 £ (21,13 £ l'ora), 37.100 £, 33.400 £, 33.400 £. Licenza OGL v3 (riuso libero con attribuzione).
- GOV.UK, "Skilled Worker visa: going rates for eligible occupation codes" → **200**.
- Home Affairs (Australia), `immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list` → **200**, 3,5 MB: i dati sono un JSON dentro la pagina (2.271 occorrenze "ANZSCO", 460 "CSOL"), con professione, codice, elenco ("MLTSSL;CSOL"), visti ammessi e ente di valutazione (es. Registered Nurse (Medical) 254418, ANMAC). Licenza CC BY 4.0 del sito.
- Irlanda, Department of Enterprise, elenco critical skills → **200** (26 kB).
- Germania (`make-it-in-germany.com`) **403**; Canada e Nuova Zelanda chiusi (rapporti di oggi). Restano 3 Paesi.

**Domanda (autocomplete Google, Regno Unito e India/Nigeria).** "skilled worker visa going rate" **10** (going rates for eligible occupation codes 2026, table); "soc code 2136" **7** (salary, uk, minimum salary for soc code 2136); "chef skilled worker visa" **10** (salary, "chefs removed from skilled worker visa"); "software engineer skilled worker visa" **10** ("going rate for software engineer uk skilled worker visa"); "skilled worker visa occupation" **10** (list with salary, code list, 2026); "core skills occupation list" **10** (2026, 482, home affairs); "critical skills occupation list" **10** (ireland 2026); "work visa for nurses" **10** (usa, australia, canada, uk, ireland, new zealand).

**Chi c'è su Google.** GOV.UK; per codice: tarve.co.uk (una pagina per codice SOC, automatica), huntukvisasponsors.com (una pagina per codice), DavidsonMorris, AYJ Solicitors, visahelpuk, recruitroo; alcune pagine hanno cifre vecchie (una guida cita ancora la soglia di 38.700 £). **Battibile a metà:** non sulle ricerche generali, sì sulla coda lunga per codice e sulle citazioni degli assistenti AI (fonte ufficiale, data di aggiornamento visibile, Regno Unito + Australia + Irlanda nella stessa pagina "per mestiere", che nessuno dei concorrenti ha).

**Chi paga.** AdSense (pubblico misto: Regno Unito e Paesi con poca pubblicità, India, Nigeria, Pakistan, Filippine). Wise, se iscritta: 10 £ per cliente (cifra già in `idee-grandi-2026-10-17`). Nessun pagatore diretto per chi cerca lavoro con sponsor (le "job board" con visto sono un terreno di annunci ingannevoli: non le mettiamo).

**Stima a 18 mesi (ipotesi, non dati).** RPM misto 5 € ogni 1.000 pagine viste (8 € nell'ottimista, più traffico britannico), 1,5 pagine per visita, Wise allo 0,1 % delle visite.
- Prudente: 150 visite/mese = 1.800/anno × 1,5 × 5 € / 1.000 = 14 € → **15 €**.
- Centrale: 500 visite/mese = 6.000 × 1,5 × 5 / 1.000 = 45 € + 6 clienti Wise × 11,5 € = 69 € → **≈ 120 €**.
- Ottimista: 2.500 visite/mese = 30.000 × 1,5 × 8 / 1.000 = 360 € + 30 × 11,5 € = 345 € → **≈ 700 €**.
- Primi soldi: dal giorno di AdSense sulla rete (oggi non attivo).

**Ore:** 16-24 (lettore JSON GOV.UK, lettore JSON Home Affairs, lettore Irlanda, ~350 + ~450 pagine generate con controllo di qualità, 20 pagine "per mestiere", aggiornamento automatico che pubblica solo se il JSON cambia, revisione). Attenzione ai crediti Netlify: una sola pubblicazione all'uscita.

**Voto 5,5.** Fonte ottima e gratuita, domanda vera per codice, costo zero. Pesano i concorrenti automatici per codice, il pubblico a bassa resa e l'assenza di un pagatore forte. Passa solo per la regola della rete fitta, in coda dopo le sezioni con stima più alta.

## 2. Costo del datore di lavoro Paese per Paese (voto 5, RISERVA come fronte B2B)

**Cosa sarebbe.** Un sito in inglese "quanto costa davvero assumere in [Paese] nel 2027": contributi a carico del datore (percentuali e tetti), 13ª e 14ª obbligatorie, salario minimo, ferie, preavviso, con calcolatore e fonte ufficiale per ogni numero; pubblico: piccole aziende USA/UK che assumono una persona all'estero. È un **fronte nuovo** (pubblico B2B, pagatore da 1.500 $).

**Fonte (curl 31/10).** OCSE SDMX `sdmx.oecd.org/public/rest/dataflow/OECD.CTP.TPS/all` → **200** (Taxing Wages, contributi per Paese; dati OCSE in CC BY 4.0); MISSOC, tabelle comparative della sicurezza sociale UE → **200**; Eurostat salari minimi `earn_mw_cur` → **200** (sotto, idea 4); pagina OCSE della banca dati fiscale **403**. Le aliquote nazionali andrebbero confermate sui siti delle agenzie di ogni Paese (lavoro di raccolta per ~30 Paesi).

**Domanda.** "employer cost calculator" **10** (uk, netherlands, ireland, germany, cyprus, spain, canada, belgium, france); "employer social security contributions" **10** (netherlands, belgium, uk, spain); "employer costs in germany" **7**; "cost of hiring an employee in" **5** (canada, australia, india); "13th month pay countries" **8**.

**Chi c'è su Google.** Proprio i pagatori e i loro concorrenti: Deel (guide per Paese e blog "employer costs in the Netherlands"), Remote (country explorer, 200, 2 MB), Playroll, Multiplier, Teamed, Topsource, Globalexpansion; più calcolatori automatici (`wagehourtools.pages.dev`, `dutch-salary-calculator.pages.dev`, yourincomecalculator, qureos). Le cifre si contraddicono (Paesi Bassi 15-35 % a seconda della fonte; tetto 79.409 o 79.412 €). **Battibile poco** su Google; il vantaggio possibile è la citazione degli assistenti AI con fonte e data.

**Chi paga.** **Deel, programma affiliati (pagina ufficiale `deel.com/affiliates/` letta, 200): "$500 USD for each sales qualified referral, and $1,000 USD for each new paying customer… $1,500 USD total per new customer"**, finestra di 90 giorni dal clic, gestito su PartnerStack (lo stesso account proposto per Gusto). Non letto: se accettano editori con sede in Italia e quali requisiti ha il "contatto qualificato" (dimensione dell'azienda). AdSense B2B (RPM ipotizzato 15 €).

**Stima a 18 mesi (ipotesi).** Conversione in contatti qualificati 1 ogni 4.000 visite nel centrale (ipotesi, nessun dato della rete), clienti = 1/3 dei contatti; cambio 1 $ = 0,92 €.
- Prudente: 150 visite/mese = 1.800/anno, nessun contatto (0,45 attesi: prudenza = zero) + AdSense 1.800 × 1,3 × 15 / 1.000 = 35 € → **35 €**.
- Centrale: 800 visite/mese = 9.600/anno → 2,4 contatti × 500 $ + 0,8 clienti × 1.000 $ = 2.000 $ ≈ 1.840 € + AdSense 190 € → **≈ 2.000 €**.
- Ottimista: 4.000 visite/mese = 48.000/anno, 1 contatto ogni 2.000 visite → 24 × 500 $ + 8 × 1.000 $ = 20.000 $ ≈ 18.400 € + AdSense 900 € → **≈ 19.000 €**.
- Primi soldi: non prima di 6-9 mesi (sito nuovo, B2B, ciclo di vendita di Deel).

**Ore:** 40-60 (30 Paesi, fonti nazionali, calcolatore, revisione dei fatti su percentuali che cambiano ogni gennaio). Serve un sito nuovo su Netlify (passaggio di Massimiliano) e l'iscrizione a PartnerStack.

**Voto 5.** Pagatore eccezionale e scritto, ma il caso centrale (2.000 €) è sotto i 5.000 € e la prima pagina è dei pagatori stessi più una decina di calcolatori automatici. Si tiene in RISERVA: si riapre se arriva un segnale che gli assistenti AI citano la rete su domande B2B (oggi nessuna pagina B2B nella rete) o se PartnerStack viene aperto per Gusto.

## 3. Trasparenza salariale UE, recepimento Paese per Paese (voto 4,5, NO)

**Fonte.** Direttiva (UE) 2023/970, termine di recepimento 7/6/2026. EUR-Lex risponde **202 senza contenuto** (anti-robot: non si aggira). L'endpoint SPARQL dell'ufficio pubblicazioni `publications.europa.eu/webapi/rdf/sparql` → **200** e restituisce le misure nazionali collegate alla direttiva (cellar `5bbb9daf-f470-11ed-a05c-01aa75ed71a1`), ma mescola leggi vecchie già esistenti (date dal 1992) con quelle nuove: serve lettura a mano per ogni Paese.

**Domanda.** Forte e in tutte le lingue: "pay transparency directive" **10** (ireland, malta, netherlands, denmark, sweden, germany); "eu pay transparency directive" **10** ("which countries have implemented", "tracker"); "entgelttransparenzrichtlinie" **10** ("umsetzung deutschland aktueller stand"); "direttiva trasparenza salariale" **10** ("recepimento", "quando entra in vigore"); "loontransparantie" **10** (wet 2027).

**Chi c'è.** Tracker di studi legali e consulenti aggiornati (Sorainen, Addleshaw Goddard, Linklaters, Taylor Wessing, Lockton 25/9/2026, Ogletree), software HR (Figures, Assessio "June 2026", Mirro), Euronews. Le cifre già divergono tra loro, ma sono fonti autorevoli con giuristi: noi non battiamo uno studio legale su un tema legale.

**Chi paga.** Solo AdSense B2B (RPM ipotizzato 20-25 €); nessun programma di affiliazione letto per i software di analisi salariale.

**Stima.** Prudente 200 visite/mese × 12 × 1,3 × 20 / 1.000 = 62 € → **50 €**; centrale 1.000/mese → 312 € → **300 €**; ottimista 4.000/mese × 12 × 1,3 × 25 / 1.000 = **1.600 €**. Ore 25-35, sito nuovo. **Voto 4,5: NO.**

## 4. Soglie dei visti legate al salario minimo, aggiornate da Eurostat (voto 5, AGGIUNTA tecnica)

**Fonte.** Eurostat `ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/earn_mw_cur?format=JSON&currency=EUR&time=2026-S2` → **200**, aggiornata il **31/7/2026**, CC BY 4.0. Letti (mensili su 12 mesi): Spagna 1.425 €, Portogallo 1.073 €, Germania 2.343 €, Francia 1.867 €, Paesi Bassi 2.338 €, Irlanda 2.391 €, Lussemburgo 2.771 €, Croazia 1.050 €, Polonia 1.119 € (e altri 21 Paesi).

**Perché serve.** In `visaincome/dati/programmi.json` le soglie della Spagna sono scritte come multipli del SMI ("75% of the SMI (€915.75 × 14)…") e quelle del Portogallo come multipli della RMMG. Quando escono i minimi 2027 (Spagna di solito tra gennaio e febbraio, Portogallo a fine anno) le pagine diventano vecchie. Un controllo automatico semestrale su Eurostat avvisa quando cambia il minimo; la cifra esatta si prende poi dal decreto nazionale (Eurostat ha un ritardo di mesi e media su 12 mensilità).

**Domanda.** "minimum wage in europe" **10** (by country, per hour, 2026); utile soprattutto per la freschezza delle pagine citate dagli assistenti AI ("2027" con data).

**Stima.** 0 / 60 / 300 €/anno (vale come difesa del traffico che c'è, non come traffico nuovo). Ore 3-4. Già toccata dal rapporto `wf-2026-10-31-spagna-portogallo-latam` per la Spagna: farla insieme, una volta sola.

## 5. Salari minimi dei cantoni svizzeri e frontalieri (voto 4, NO)

**Fonte.** Ginevra `ge.ch/appliquer-salaire-minimum-genevois/montant-calcul-du-salaire-minimum` → **200**: "Depuis le 1er janvier 2026… 24.59 fr. de l'heure… Il s'élèvera à **24.73 fr. en 2027**" (modificata il 7/10/2026). Ticino (`www4.ti.ch`, `m3.ti.ch`) → **000** dal server, cioè il cantone che conta per i frontalieri italiani è chiuso; pagine provate di Neuchâtel, Giura e Basilea Città → 404 (indirizzi cambiati, non ritrovati); `gavservice.ch` (contratti collettivi) 000.

**Domanda.** Buona in tre lingue: "salario minimo ticino" **10** (2026, 2027, frontalieri, mensile, calcolatore); "stipendio minimo svizzera" **10** (in euro, netto, ticino); "salaire minimum genève" **10** (2027, par mois, 42h); "salaire minimum suisse" **10**; "mindestlohn schweiz" **10** (2026, zürich, euro); "tassa salute frontalieri" **10** (lombardia, rinviata, retroattiva: è cronaca politica, non un numero stabile).

**Chi c'è.** Enti cantonali, lohncheck.ch, frontaliereticino.ch, frontaliers-grandest.eu, salerya.fr, rister.ch, tio.ch, RSI, laRegione. **Chi paga:** AdSense svizzero (alto), ma nessun sito della rete parla a lavoratori in Svizzera; un cambio valuta per frontalieri non ha domanda ("cambio franchi euro frontalieri" **0**).

**Stima.** 20 / 150 / 800 €/anno come sezione. Ore 12-18. **Voto 4: NO** (Ticino chiuso, pubblico fuori dalla rete).

## 6. Salario minimo del Giappone per prefettura, in inglese (voto 4,5, NO come lavoro dedicato)

**Fonte.** Ministero del lavoro giapponese, "令和8年度地域別最低賃金の全国一覧" → **200**; PDF `mhlw.go.jp/content/11200000/001753404.pdf` → **200**, 42 kB, testo leggibile. Letto: Tokyo 1.280 yen (da 1.226, +54) dal 1/10/2026; Hokkaido 1.131 dal 1/10; Aomori 1.090 dal 29/10; **Iwate 1.090 dal 1/12/2026**; Yamanashi 1.113 dal 1/11; Fukushima 1.094 dal 16/10. Le date di entrata in vigore sono diverse per quasi ogni prefettura: è il dato che manca in inglese. Termini d'uso del ministero compatibili con CC BY 4.0.

**Domanda.** "japan minimum wage" **10** (usd, per month, 2026); "minimum wage in japan by prefecture" **6** (2026); "minimum wage in tokyo" **10** (in usd, per month, 2026).

**Chi c'è.** Wikipedia, WageIndicator (con pagine aggiornate al 3/10/2026), nippon.com, Bloomberg Tax, siti per stranieri a Tokyo (tokyointernationalmeetup, hotelbank). **Chi paga:** AdSense (studenti e working holiday: poco).

**Stima.** 10 / 80 / 400 €/anno. Ore 6-10. **Voto 4,5:** al massimo una tabella dentro una futura sezione Giappone di Visa Income, non un lavoro a sé.

## 7. Congedo familiare pagato negli USA, Stato per Stato (voto 4, NO)

**Fonte (curl).** Minnesota `paidleave.mn.gov` **200**; California EDD **200**; Washington **200**; Oregon **200**; Connecticut **200**; New York **200**; New Jersey **200**; DC **200**; Delaware 200 ma 245 byte (pagina vuota); **Maine 403, Massachusetts 403, Colorado 403, Rhode Island 000**. Riepilogo privato: National Partnership for Women & Families (PDF 200, non riusabile come fonte ufficiale).

**Domanda.** "paid family leave by state" **10** (2026, maternity leave by state); "states with paid family leave" **10** (2026, shrm); "minnesota paid leave" **10** (2026, calculator); "paid family leave calculator" **10** (california, ny, washington, mn): gli Stati hanno già i loro calcolatori ufficiali.

**Chi c'è.** Gli enti statali, SHRM, National Partnership, Bipartisan Policy Center, società di paghe. **Chi paga:** AdSense; Gusto (300 $) vale per i datori, ma il blocco datori è già nel progetto "US Small Business by State" (riserva della verifica di oggi): non si duplica.

**Stima.** 50 / 400 / 2.000 €/anno. Ore 30-40, sito nuovo. **Voto 4: NO.**

## 8-10. Chiusi in fretta

- **Minimi di settore in Germania 2027** (pulizie 15 € dal 1/1/2026; minimo legale 13,90 € nel 2026 e 14,60 € dal 1/1/2027): "mindestlohn 2027" **10** con "reinigung", "reinigungskraft", "minijob grenze"; DGB, lohn-info, steuerprofis, giornali; pagine del Zoll provate 404 (indirizzi cambiati). Solo tedesco, nessun sito della rete in tedesco. **Voto 3,5, NO.**
- **Tabelle GS 2027 per località**: "gs pay scale 2027" **10** con città (san diego, san antonio, los angeles, hawaii); OPM 200, federalpay.org 403 dal server ma primo su Google con pagine automatiche per località; FedSmith e GovExec. Le tabelle 2027 escono a fine dicembre. **Voto 3, NO.**
- **"Stipendio medio [Paese]" in italiano** ("stipendio medio" **10**: germania, svizzera, spagna, francia, polonia) da Eurostat: giornali e blog, pubblico italiano a bassa resa, nessun pagatore. **Voto 3,5, NO.** **Visti stagionali in Europa** ("seasonal work visa europe" **10**, "for indian"): pubblico a bassissima pubblicità e ricerche dominate da annunci di "sponsorship" spesso ingannevoli; fonti nazionali sparse. **Voto 3, NO.** ISTAT esplora-dati risponde 200 (SDMX), ma non cambia il verdetto del 23/10 sugli stipendi per professione.

## Cosa fare

1. **Nessun messaggio a Massimiliano**: nessuna idea ha voto ≥ 7 e ≥ 5.000 €/anno centrali.
2. **Coda della rete fitta:** idea 1 (sezione "work visa by occupation" in Visa Income, 16-24 ore) in coda bassa, dopo le sezioni con stima più alta; idea 4 (controllo Eurostat delle soglie legate al minimo) insieme al lavoro sulla Spagna già annotato.
3. **Riserva:** idea 2 (costo del datore di lavoro con Deel) si riapre solo con l'account PartnerStack attivo e un primo segnale di citazioni AI su temi B2B.
4. **Lezione per i prossimi giri:** nel lavoro e nei salari i numeri ufficiali sono già ripresi da enti, sindacati e siti automatici; il buco vero è stato solo dove la fonte ufficiale ha un formato scomodo (JSON dentro la pagina, PDF giapponese) e la domanda è per codice o per luogo. Il prossimo giro su questo settore non serve: cambiare settore.

## Fonti provate (curl 31/10/2026)

| Indirizzo | Esito |
|---|---|
| `gov.uk/api/content/guidance/immigration-rules/immigration-rules-appendix-skilled-occupations` | 200, JSON 337 kB, aggiornato 29/10/2026, 737 righe, OGL |
| `gov.uk/government/publications/skilled-worker-visa-going-rates-for-eligible-occupations` | 200 |
| `immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list` | 200, 3,5 MB con JSON delle professioni |
| `enterprise.gov.ie/.../highly-skilled-eligible-occupations-list/` | 200 |
| `make-it-in-germany.com/en/visa-residence/types/eu-blue-card` | 403 |
| `deel.com/affiliates/` | 200: 500 $ per contatto qualificato + 1.000 $ per cliente, 90 giorni, PartnerStack |
| `remote.com/affiliate-program`, `oysterhr.com/affiliate-program` | 404 |
| `sdmx.oecd.org/public/rest/dataflow/OECD.CTP.TPS/all` | 200 |
| `missoc.org/missoc-database/comparative-tables/` | 200 |
| `oecd.org/en/data/datasets/oecd-tax-database.html` | 403 |
| `eur-lex.europa.eu/legal-content/EN/NIM/?uri=CELEX:32023L0970` | 202 senza contenuto (anti-robot) |
| `publications.europa.eu/webapi/rdf/sparql` | 200 (misure nazionali leggibili) |
| `ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/earn_mw_cur?...` | 200, aggiornato 31/7/2026 |
| `ge.ch/appliquer-salaire-minimum-genevois/montant-calcul-du-salaire-minimum` | 200 (24,59 CHF nel 2026, 24,73 nel 2027) |
| `www4.ti.ch/...`, `m3.ti.ch/...`, `gavservice.ch` | 000 |
| `mhlw.go.jp/stf/seisakunitsuite/bunya/koyou_roudou/roudoukijun/minimumichiran/` | 200 |
| `mhlw.go.jp/content/11200000/001753404.pdf` | 200, PDF 42 kB con 47 prefetture e date |
| `paidleave.mn.gov`, `edd.ca.gov/.../paid-family-leave/`, `paidleave.wa.gov`, `paidleave.oregon.gov`, `ctpaidleave.org`, `ny.gov/new-york-state-paid-family-leave`, `myleavebenefits.nj.gov`, `does.dc.gov/page/dc-paid-family-leave` | 200 |
| `maine.gov/paidleave`, `mass.gov/...pfml-benefits-calculator`, `famli.colorado.gov` | 403 |
| `paidleave.ri.gov` | 000 |
| `opm.gov/policy-data-oversight/pay-leave/salaries-wages/` | 200 |
| `federalpay.org/gs/2026`, `bls.gov/oes/` | 403 |
| `esploradati.istat.it/SDMXWS/rest/dataflow/IT1` | 200 |
| `ons.gov.uk/.../occupation2digitsocashetable2` | 200 |
