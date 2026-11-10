# Verifica indipendente: decoder delle lettere di furto dati (USA), 10/11/2026

Idea verificata: n. 1 di `fronti-2026-11-10-rete-prima-sicurezza-digitale.md` (voto 6; 900 / 4.600 / 24.000 €/anno). Innesco per il 7: **(a)** prova su ~20 furti di dati medi che ClaimDepot non dà il monitoraggio gratuito e la scadenza per attivarlo; **(b)** un pagatore di protezione dell'identità.

Tutto letto con curl il 10/11/2026. Nessun blocco aggirato: dove un sito ha risposto 403 ci siamo fermati e lo scriviamo.

## 0. Verdetto in breve

**NO-GO come sito nuovo. Voto corretto: 5 su 10** (era 6). Stima a 18 mesi: **350 / 2.100 / 24.000 €/anno** (prudente / centrale / ottimista). La centrale resta sotto l'asticella dei 5.000 €.

- **La condizione (b) c'è**: IdentityIQ su Awin (dato letto da Massimiliano: conversione 9,09 %, approvazione 100 %, EPC 3,18 USD, pagamento a 30 giorni).
- **La condizione (a) NON c'è, anzi è smentita.** Su 24 furti di dati medi del 2026, ClaimDepot nomina il servizio di monitoraggio gratuito in **21 su 24**, mette la **copia ufficiale della lettera in 24 su 24**, il telefono in 17 su 24 e una **data precisa di scadenza in 8 su 24**. Noi, dalle copie che riusciamo a leggere, la data precisa la troviamo solo in **3 su 24**: nelle copie depositate la scadenza è quasi sempre un segnaposto vuoto (`<<ENROLLMENT DEADLINE>>`). ClaimDepot legge più Stati di noi (Maine, Massachusetts, Montana, New Hampshire, Rhode Island: a noi rispondono 403).
- **La domanda per le violazioni medie non è "la lettera"**: su 19 aziende medie, "‹azienda› data breach letter" dà suggerimenti in 4 casi (uno solo ciascuno), "free credit monitoring ‹azienda›" in **0 su 19**; la gente cerca "settlement", "lawsuit", "class action" (8 su 19). È il mestiere di ClaimDepot e di ClassAction.org.
- Il pagatore IdentityIQ resta buono e va tenuto per un'idea con più traffico nostro: da solo non basta a far passare questa.

## 1. Dati: quali portali ufficiali si leggono oggi

| Stato / ente | Indirizzo | Esito curl | Campi | Lettera PDF | Volume | Note |
|---|---|---|---|---|---|---|
| Washington (dati aperti) | `data.wa.gov/resource/sb4j-ca4h.json` | 200, JSON | azienda, date (inizio, scoperta, deposito), causa, tipo di attacco, residenti colpiti, settore, giorni alla notifica | no | 171 nel 2026 (9-23 al mese, ~4 a settimana) | Socrata; licenza non indicata nei metadati (dato pubblico dello Stato) |
| Washington (sito del procuratore) | `atg.wa.gov/data-breach-notifications` | 200, tabella HTML, 50 righe a pagina | azienda, date, residenti, **tipi di dati** | **sì** (su `agportal-s3bucket.s3.amazonaws.com`) | come sopra | la fonte più completa che leggiamo |
| California | `oag.ca.gov/privacy/databreach/list` + scheda `sb24-…` | 200, tabella HTML | azienda, date della violazione, data di deposito | **sì** (una per scheda) | ~50 al mese (450 righe dal 6/2 al 9/11) | robots.txt chiede **10 secondi** fra le richieste; nessun numero di persone |
| Oregon | `justice.oregon.gov/consumer/DataBreach/` | 200, 1.679 righe in una pagina | azienda, date, data di invio della lettera, persone colpite | no | 8-24 al mese | |
| Delaware | `attorneygeneral.delaware.gov/…/database/` | 200, tabella | azienda, date, residenti | sì | **fermo a luglio 2025** | non aggiornato |
| Hawaii | `cca.hawaii.gov/ocp/notices/security-breach/` | 200, tabella | azienda, tipo, residenti | sì | **fermo al 2024** | non aggiornato |
| Indiana | `in.gov/attorneygeneral/…/security-breaches/` | 200 | un PDF riassuntivo all'anno (anche 2026) | no | da estrarre dal PDF | |
| Texas | `oag.my.site.com/datasecuritybreachreport/…` | 200 ma i dati arrivano con JavaScript | (tipi di dati, texani colpiti) | no | non provato | non forzato |
| Iowa, Maryland, New York | pagine 200 | elenchi per anno o solo modulo | non verificato | | | NY non ha un elenco pubblico delle lettere sulla pagina letta |
| HHS OCR (sanità) | `ocrportal.hhs.gov/ocr/breach/breach_report.jsf` | 200, modulo JSF | non provato | no | | |
| **Maine** | `maine.gov/agviewer/…` | **403** | | | | fermati |
| **Massachusetts** | `mass.gov/lists/data-breach-notification-letters` | **403** | | | | fermati |
| **New Hampshire** | `doj.nh.gov/…` | **403** | | | | fermati |
| **Montana** | `dojmt.gov/…` | **403** (verifica anti-robot) | | | | fermati |
| Rhode Island | `riag.ri.gov/data-breaches` | **403** | | | | fermati |
| Vermont | indirizzi provati | 404 | | | | indirizzo giusto non trovato |
| Wisconsin | `datcp.wi.gov` | 401 | | | | |

In pratica leggiamo bene **3 Stati** (Washington, California, Oregon): circa 1.000 depositi l'anno, 700-800 aziende diverse. Proprio gli Stati dove le lettere depositate hanno più spesso la data vera (Maine, Massachusetts, Vermont, New Hampshire) a noi sono chiusi.

### Prova di estrazione da 13 lettere PDF della California (depositi dal 13/8 al 9/11/2026)

Tutti e 13 i PDF hanno testo leggibile con `pdftotext` (nessuna scansione).

| Cosa cerchiamo | Risultato |
|---|---|
| C'è un'offerta di monitoraggio gratuito? | 10 su 13 sì, 3 no (Enara Health, Cotton Incorporated, Blueberry Pediatrics) |
| Nome del servizio (Kroll, IDX, Cyberscout, Epiq, Experian) | 10 su 10 |
| Durata fissa (12 o 24 mesi) | 5 su 10; in 2 è "12/24" a seconda della persona; in 3 è un segnaposto o manca |
| **Scadenza con data precisa** | **1 su 10** (Telecare: 22/1/2027) |
| Scadenza relativa ("entro 90 giorni dalla data della lettera") | 4 su 10 (tutte Cyberscout) |
| Scadenza = segnaposto vuoto | 3 su 10; assente in 2 |
| Telefono del centro chiamate | 12 su 13 |

Conclusione tecnica: servizio, durata e telefono si estraggono bene; **la scadenza no**. Il punto di forza promesso dall'idea ("fino a quando puoi attivarlo") nella maggior parte dei casi sarebbe "guarda la data sulla tua lettera".

## 2. Concorrenza: la prova chiesta dalla condizione (a)

Campione: 24 depositi a Washington nel 2026 con 1.500-100.000 residenti colpiti (violazioni medie), per cui esiste la pagina ClaimDepot. Per ognuno: lettera ufficiale (copia di Washington) contro pagina ClaimDepot. Controllo automatico con parole chiave, riletto a mano su 5 pagine (errore possibile ±2 righe).

ClaimDepot oggi: **2.787 pagine "data-breach" nella sitemap, 1.244 del 2026**, robots.txt aperto; ogni pagina elenca fino a 16 fonti (procuratori di CA, IN, IA, ME, MA, MT, NE, NH, OR, RI, SC, TX, VT, WA, più HHS e SEC).

| Azienda (residenti WA) | Lettera ufficiale: servizio, durata, scadenza | ClaimDepot: monitoraggio | servizio | durata | scadenza | telefono | PDF lettera |
|---|---|---|---|---|---|---|---|
| Del Monte Foods (4.821) | Kroll, 12 mesi, segnaposto | sì | sì | no | generica | sì | sì |
| Quantum Health (15.321) | Experian (copia breve) | sì | sì | no | generica | sì | sì |
| JM Bullion (2.366) | Experian, 12 mesi, **29/1/2027** | sì | sì | sì | **29/1/2027** | no | sì |
| Poppins Payroll (17.954) | Experian, 2 anni, manca | sì | sì | sì | generica | no | sì |
| CallonDoc (12.186) | Cyberscout, 1 anno, manca | **no** | **no** | no | generica | no | sì |
| OneMain Financial (2.928) | Experian, 12 mesi, segnaposto | sì | sì | sì | **31/12/2026** | sì | sì |
| LHC Group (6.602) | IDX, 2 anni, segnaposto | sì | sì | sì | **4/12/2026** | sì | sì |
| Catalyst Brands (4.015) | Experian, 2 anni, **31/12/2026** | sì | sì | sì | **31/12/2026** | sì | sì |
| Pan American Group (12.309) | Cyberscout, 1 anno, manca | sì | sì | no | generica | no | sì |
| Rockwood Retirement (7.136) | IDX/Cyberscout, 12 mesi, **20/11/2026** | sì | sì | sì | **20/11/2026** | sì | sì |
| Turner Construction (3.401) | IDX, 1 anno, segnaposto | sì | sì | no | **18/11/2026** | sì | sì |
| AdaptHealth (9.214) | Kroll, 12 mesi, segnaposto | sì | sì | no | no | sì | sì |
| Baylor Genetics (27.243) | IDX, 12 mesi, segnaposto | sì | sì | sì | no | sì | sì |
| Lennar Mortgage (11.417) | Kroll, 2 anni, manca | sì | sì | sì | no | sì | sì |
| Paylogix (28.449) | Cyberscout, 12 mesi, entro 90 giorni | sì | sì | sì | no | no | sì |
| Everside Health / Aesto (21.308) | Epiq, 12 mesi, manca | sì | sì | no | no | sì | sì |
| ADT (5.129) | Cyberscout, 12 mesi, entro 90 giorni | sì | sì | sì | generica | no | sì |
| JRK Property (5.667) | Experian, 12 mesi, segnaposto | sì | sì | sì | no | sì | sì |
| CareCloud (20.706) | IDX, 12 mesi, segnaposto | sì (IDX) | sì | no | **17/12/2026** | sì | sì |
| Medtronic (64.035) | Epiq, 24 mesi, segnaposto | **no** | **no** | no | no | no | sì |
| Plaza Home Mortgage (9.598) | CyEx, 12 mesi, manca | sì | sì | sì | generica | sì | sì |
| Caesars Entertainment (44.023) | IDX, 2 anni, segnaposto | sì (IDX) | sì | sì | **19/8/2026** | sì | sì |
| Nursa (13.168) | Cyberscout, 1 anno, manca | **no** | **no** | no | no | sì | sì |
| Mt. Spokane Pediatrics (29.410) | Cyberscout, manca | sì | sì | no | generica | sì | sì |

**Totali ClaimDepot su 24:** servizio di monitoraggio nominato **21** (88 %); durata 13; scadenza con data **8**, generica ("c'è una scadenza, è sulla lettera") 8, niente 8; telefono 17; **PDF della lettera 24**; totale nazionale delle persone colpite 19; elenco delle fonti statali 24. Guida "la lettera è vera?": **0**.

**Totali nostri possibili** (dalla copia di Washington): servizio 24; scadenza con data **3**, relativa 2, segnaposto 10, assente 9. In 5 casi ClaimDepot ha la data e la nostra copia no (OneMain, LHC, Turner, CareCloud, Caesars).

Esempio letto per intero (Catalyst Brands): "24 months of free identity protection and credit monitoring through Experian IdentityWorks… Enrollment must be completed by Dec. 31, 2026… toll-free line 833-918-1023". È già la nostra scheda.

Altri concorrenti:

| Sito | Esito | Monitoraggio e scadenza | Lettera ufficiale | "È vera?" |
|---|---|---|---|---|
| ClassAction.org (`/data-breach-lawsuits/‹azienda›-‹mese›-2026`) | 200 per 5 delle 12 aziende provate | no (pagina per raccogliere contatti per gli studi legali) | link al documento in alcuni casi | no |
| HIPAA Journal | **403** | non letto | | |
| databreaches.net | **403** | non letto | | |
| ITRC (idtheftcenter.org/notified) | **403** | non letto | | |
| Studi legali (Strauss Borrelli e simili) | 200, ricerca interna senza risultati utili | non verificato | | |

**Quello che resta scoperto** è poco: la guida "la lettera è vera?" (0 su 24), il 12 % di pagine dove ClaimDepot non nomina il servizio, una scheda senza l'invito "manda il reclamo allo studio legale". Non è un vantaggio che fa cambiare sito a chi cerca.

## 3. Domanda (autocomplete Google, gl=us, hl=en, oggi)

Generiche: "data breach letter" 9; "data breach letter legit" 10 (Conduent, DentaQuest, Aflac, Marquis: solo violazioni enormi); "is this data breach letter legit" 8; "notice of data breach letter" 10 (reddit, meaning, scam); "free credit monitoring data breach" 10 ("should i accept free credit monitoring after data breach"); "is kroll letter legit" 7; "cyberscout letter legit" 6; "experian identityworks letter" 6; "epiq privacy solutions" 10 (login, reviews); "is idx letter legit" 0; "credit monitoring enrollment deadline" 0; "should i enroll in free credit monitoring" 0.

Per azienda (19 medie + Conduent come confronto):

| Frase | Aziende medie con almeno un suggerimento (su 19) | Nota |
|---|---|---|
| "‹azienda› data breach" | 18 | da 1 a 10 suggerimenti; 8 aziende ne hanno 1-2 |
| "‹azienda› data breach letter" | 4 (Medtronic, Baylor Genetics, Quantum Health, AdaptHealth), **un solo suggerimento ciascuna** | Conduent: 10 |
| "‹azienda› data breach settlement / lawsuit / class action" | 8 | è l'intento dominante |
| "free credit monitoring ‹azienda›" | **0** | Conduent: 5 |

Lettura: per le violazioni medie la gente cerca il nome e poi **i soldi della causa**, non la lettera né il monitoraggio. La domanda "è vera?" esiste per le violazioni giganti (già coperte da TV e giornali) e per i **nomi dei fornitori** (Kroll, Cyberscout, Experian IdentityWorks, Epiq): 6-10 suggerimenti ciascuno, poche pagine sempreverdi.

**Stima delle visite a 18 mesi (metodo):** ~750 aziende nuove l'anno leggibili × ~1.500 ricerche totali ciascuna nella vita della notizia (ipotesi, coerente con 1-10 suggerimenti) = ~1,1 milioni di ricerche l'anno. Un sito nuovo dietro ClaimDepot, ClassAction.org, studi legali e giornali prende l'1-3 % → 11.000-34.000 visite. Più 5-6 pagine sui fornitori ("is Kroll letter legit") e 5 guide: 500-1.500 al mese se si posizionano. **Prudente 1.500 visite al mese, centrale 4.000, ottimista 25.000** (l'ottimista vale solo se una violazione enorme ci trova primi). Lo studio di partenza metteva 12.000 centrali: con (a) smentita non regge.

## 4. Soldi

| Programma | Cifra | Fonte |
|---|---|---|
| **IdentityIQ (USA), Awin** | conversione 9,09 %, approvazione 100 %, **EPC 3,18 USD**, pagamento medio 30 giorni (~35 USD a vendita) | letto da Massimiliano su Awin il 10/11 (dato preso per buono) |
| IdentityIQ, prezzi | da 8,49 a 34,99 USD al mese | https://www.identityiq.com/ (200) |
| Coveron (ex NordProtect) | 40 % a iscrizione + 30 % sui rinnovi | https://coveron.com/affiliate/ (200, riletto oggi) |
| Aura | 15 % a vita | elenco PartnerStack (studio del 10/11) |
| IdentityIQ, Aura, IdentityGuard, IDShield, Experian, DeleteMe: pagina "affiliates" | 404 | nessuna cifra pubblica |
| LifeLock/Norton, IdentityForce | 403 | non letti |
| Incogni | 200, pagina senza cifre | https://incogni.com/affiliate |

Attenzione all'EPC: 3,18 USD è la media degli editori Awin di IdentityIQ, in gran parte pagine "credit report / credit score" (autocomplete "identityiq": login, credit report, free trial). Il nostro lettore ha appena ricevuto 12-24 mesi di monitoraggio gratis: renderà meno. Per questo applico uno sconto.

**Formula:** € anno = visite × RPM/1.000 × 0,85 (blocco pubblicità) + visite × CTR verso l'offerta × EPC 3,18 USD × sconto di intento × 0,90 (cambio USD→EUR, ipotesi).

| Scenario | Visite/anno | RPM AdSense (ipotesi) | CTR offerta | Sconto | Pubblicità | Affiliazione | **Totale** |
|---|---|---|---|---|---|---|---|
| Prudente | 18.000 | 8 € | 1 % | 0,4 | 120 € | 205 € | **~350 €** |
| Centrale | 48.000 | 12 € | 2 % | 0,6 | 490 € | 1.650 € | **~2.100 €** |
| Ottimista | 300.000 | 15 € | 3 % | 0,8 | 3.825 € | 20.600 € | **~24.000 €** |

RPM AdSense: nessuna fonte pubblica letta oggi; 8-15 € è l'ipotesi dello studio di partenza (tema sicurezza/finanza, pubblico USA). Controprova: con il traffico centrale dello studio di partenza (144.000 visite) la stessa formula darebbe ~6.400 €: **il pagatore basterebbe, è il traffico che manca**.

## 5. Rischi

- **Concorrente automatico più completo di noi** (sez. 2): rischio principale, già avverato.
- **Fonti**: 3 Stati leggibili su ~17 provati; Delaware e Hawaii fermi; 6 portali con 403. La California chiede 10 secondi fra le richieste (600 schede l'anno: fattibile, ma lento).
- **Scadenza non estraibile** in ~80 % delle lettere depositate: il dato che doveva distinguerci.
- **YMYL / legale**: tema soldi e identità, sito nuovo senza autore riconoscibile; niente consigli legali; "la lettera è vera?" potrebbe solo rimandare alla copia ufficiale. Un errore su telefono o indirizzo di attivazione farebbe danno vero (rischio di aiutare un phishing).
- **Condizioni Awin / IdentityIQ**: non lette (serve il login). Di solito vietano il marchio negli annunci (noi non ne facciamo) e chiedono la dicitura di affiliazione. Da leggere prima di qualsiasi uso.
- **Domanda a picchi**: ogni pagina vive 4-8 settimane; servono centinaia di pagine nuove l'anno solo per restare fermi.

## 6. Domini (.com, RDAP Verisign, oggi)

| Nome | Esito |
|---|---|
| breachletterdecoder.com | 404 = libero |
| breachnoticecheck.com | 404 = libero |
| isthisbreachletterreal.com | 404 = libero |
| breachletterguide.com | 404 = libero |
| breachletterlookup.com | 404 = libero |
| breachletter.com, databreachletter.com | 200 = presi |

Non serve comprarli: il sito non si costruisce.

## 7. Voto e decisione

| Criterio | Giudizio |
|---|---|
| Dato ufficiale | buono su 3 Stati, chiuso sugli altri; scadenza quasi mai presente |
| Domanda | vera per il nome dell'azienda, ma l'intento è la causa collettiva |
| Concorrenza | ClaimDepot fa già la scheda, con più Stati e più date di noi |
| Pagatore | **buono** (IdentityIQ, EPC 3,18 USD) |
| Centrale a 18 mesi | ~2.100 € (asticella 5.000 €) |

**Voto 5 su 10. NO-GO.** Non si costruisce prima del sito australiano; la coda torna all'ordine precedente.

**Si riapre solo se** (tutte e due):
1. una prova su 20 violazioni medie in cui una nostra pagina di prova risulterebbe più completa di ClaimDepot su almeno 12 (oggi: 3 su 24), per esempio se Maine, Massachusetts e Vermont diventano leggibili senza blocchi;
2. un segnale di domanda per "‹azienda› data breach letter" o "free credit monitoring ‹azienda›" su almeno 8 aziende medie su 20 (oggi 4 e 0).

**Cosa si tiene:**
- **IdentityIQ su Awin** come pagatore pronto (EPC 3,18 USD) per la prossima idea USA su credito, identità o truffe con traffico nostro.
- Riserva piccola, non verificata sui risultati di Google: 5-6 pagine sempreverdi "is the Kroll / Cyberscout / Experian IdentityWorks / Epiq letter legit" (6-10 suggerimenti ciascuna). Nessun sito della rete ha oggi il tema giusto per ospitarle: restano in ESPLORATE.

## Fonti lette (curl, 10/11/2026)

- data.wa.gov `sb4j-ca4h` (200) · atg.wa.gov/data-breach-notifications pagine 0-3 (200) · 24 PDF su agportal-s3bucket.s3.amazonaws.com (200)
- oag.ca.gov/privacy/databreach/list pagine 0-6, 8, 12 (200) · 13 schede `sb24-…` e 13 PDF (200) · robots.txt (Crawl-delay 10)
- justice.oregon.gov/consumer/DataBreach/ (200) · attorneygeneral.delaware.gov (200) · cca.hawaii.gov (200) · in.gov (200) · oag.my.site.com Texas (200, JavaScript) · iowaattorneygeneral.gov (200) · marylandattorneygeneral.gov (200) · ag.ny.gov (200) · ocrportal.hhs.gov (200)
- 403: maine.gov, mass.gov, doj.nh.gov, dojmt.gov, riag.ri.gov, hipaajournal.com, databreaches.net, idtheftcenter.org, lifelock.norton.com, identityforce.com · 404: ago.vermont.gov (indirizzi provati) · 401: datcp.wi.gov
- claimdepot.com: robots.txt, sitemap.xml (2.787 pagine), 25 pagine "data-breach" (200) · classaction.org: indice e 12 indirizzi provati (5 con 200)
- suggestqueries.google.com (gl=us, hl=en): 17 frasi generiche, 20 aziende × 4 frasi
- identityiq.com (200) · coveron.com/affiliate (200) · incogni.com/affiliate (200) · pagine "affiliates" di Aura, IdentityGuard, IDShield, Experian, DeleteMe (404)
- rdap.verisign.com per 7 nomi
