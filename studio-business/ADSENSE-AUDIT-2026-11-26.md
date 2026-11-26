# Audit AdSense del 26/11/2026 — Before You Fly, EsameB1, Visa Income Checker

Audit di sola lettura. Nessun sito è stato modificato. Nessun commit.

Il titolare ha ragione: Google usa criteri scritti. Qui sotto ci sono i criteri, la prova sito per sito e le correzioni.

## 0. In breve

- **Il problema è lo stesso su BYF e su Visa: il codice AdSense sta su centinaia di pagine fatte con un modello, con poche parole proprie.**
  - BYF: 1.552 pagine con il codice. 891 hanno meno di 100 parole proprie (57 %). 662 ne hanno meno di 50.
  - Visa: 803 pagine con il codice. 304 hanno meno di 100 parole proprie (38 %). 208 ne hanno meno di 50.
  - EsameB1: 212 pagine con il codice. 8 hanno meno di 100 parole proprie (4 %). Nessuna sotto 50.
- Google lo scrive chiaro: «Don't place the ad code on auto-generated pages or pages with little to no original content».
- La regola che il 12/11 abbiamo messo nei `genera.py` conta le parole **totali** (soglia 400). Non conta le parole **proprie**. Per questo le pagine a modello passano tutte: hanno 500-1.000 parole, ma quasi tutte uguali alle sorelle.
- Oggi nessuno dei tre siti è approvato. Quindi il codice sulle pagine deboli **non rende nulla e crea solo rischio**. Toglierlo non costa un euro.
- Togliere il codice è permesso dal fermo fino al 9/12. Non cambia URL, titoli o indice.
- Pagine obbligatorie, navigazione, ads.txt, pagine rotte, lingua: tutto a posto sui tre siti.
- Consenso UE: serve una CMP certificata da Google. Il cruscotto dice che il messaggio di Google è pubblicato dal 12/11. Da qui non si può vedere: serve un controllo a occhio del titolare (2 minuti, punto C12).

## 1. I criteri oggettivi di Google (fonti lette il 26/11/2026)

Tutte le frasi tra «» sono copiate dalle pagine ufficiali.

### 1.1 Fonti

| Sigla | Pagina | Indirizzo |
|---|---|---|
| F1 | AdSense Program policies (agg. 4/8/2026) | https://support.google.com/adsense/answer/48182 |
| F2 | Make sure your site's pages are ready for AdSense | https://support.google.com/adsense/answer/7299563 |
| F3 | Google AdSense content and user experience (pagina «Low value content») | https://support.google.com/adsense/answer/10015918 |
| F4 | Your AdSense account wasn't approved | https://support.google.com/adsense/answer/81904 |
| F5 | Google Publisher Policies | https://support.google.com/adsense/answer/10502938 |
| F6 | Ads on screens without publisher-content | https://support.google.com/publisherpolicies/answer/11112688 |
| F7 | Ads on screens with replicated content | https://support.google.com/publisherpolicies/answer/11190248 |
| F8 | More ads or paid promotional material than publisher-content | https://support.google.com/publisherpolicies/answer/11169917 |
| F9 | Spam policies for Google web search (versione per editori + testo completo) | https://support.google.com/publisherpolicies/answer/1348737 · https://developers.google.com/search/docs/essentials/spam-policies |
| F10 | Consent management requirements, EEA/UK/Switzerland | https://support.google.com/adsense/answer/13554116 |
| F11 | EU user consent policy | https://www.google.com/about/company/user-consent-policy/ |
| F12 | Eligibility requirements for AdSense | https://support.google.com/adsense/answer/9724 |

### 1.2 Le frasi che contano

**Contenuto proprio e sufficiente**
- F3: «make sure that your pages have enough unique content so that we can determine what your site is about. You should provide content that gives your users a reason to visit and return to your site.»
- F4, «Content quality issues»: «We believe that there isn't enough original, rich content that would be of value to users.»
- F4: «**Don't place the ad code on auto-generated pages or pages with little to no original content.**»
- F4, «Insufficient content»: «Your content should contain complete sentences and paragraphs, not only headlines.» «Test pages that are empty except for the code won't be approved.»
- F4: «Keep in mind that **we may review all pages of your site**, not just the sign-up URL where you placed the code.»
- F6: «We do not allow Google-served ads on screens: without publisher-content or with low-value content, that are under construction, that are used for alerts, navigation or other behavioral purposes.»
- F6: «**Don't place ads on automatically generated content without manual review or curation.**»
- F6: «Ads should not be placed on "dead end" or no content screens (e.g., Thank You, Exit, Error pages, etc.)»
- F1: gli annunci non possono essere «Placed on any non-content-based page» né «on pages published specifically for the purpose of showing ads».

**Pagine simili e contenuto ripetuto**
- F3: «ensure that the same content is not duplicated in the same page or across multiple pages of your site.»
- F3: «**If you have many pages that are similar or have very similar content, consider expanding each page or consolidating the pages into one.** Also, try to minimize repeating long segments of text in different pages of your site.»
- F9: «Don't create "doorway" pages created just for search engines, or other "cookie cutter" approaches such as affiliate programs with little or no original content.»
- F9 (testo completo), «Scaled content abuse»: «many pages are generated for the primary purpose of manipulating search rankings and not helping users… If you're hosting such content on your site, exclude it from Search.»
- F9, «Doorway abuse»: «Creating substantially similar pages that are closer to search results than a clearly defined, browseable hierarchy».

**Contenuto copiato da altri**
- F7: «We do not allow Google-served ads on screens: with embedded or copied content from others without additional commentary, curation, or otherwise adding value to that content.»
- F7, esempi: «Mirroring, framing, scraping or rewriting of content from other sources without adding value; Automatically generated content without manual review or curation».
- F2: «It's really important that you contribute your own original content, whether it's specialist knowledge, improvement ideas, reviews, or your personal thoughts.»

**Affiliazioni e quantità di pubblicità**
- F4: «Your site shouldn't participate in affiliate programs without adding sufficient value to users. **Affiliate program content should form only a minor part of the content of your site** if the content adds no additional features.»
- F8: «We do not allow Google-served ads on screens: with more ads or other paid promotional material than publisher-content.» «Publisher-content… does not include whitespace, header or footer content, or links to other content on the site.»

**Navigazione**
- F4, «Site navigation issues»: «Potential navigation issues include: redirects, pages behind a login or restricted access, broken links, excessive pop-ups, dialers, and pages under construction or not yet launched.»
- F3: la barra di navigazione va controllata per «Alignment», «Readability», «Functionality», «Accuracy». Il sito non deve avere link verso «Missing pages» o «Irrelevant or misleading pages».
- F1: «Sites showing Google ads should be easy for users to navigate.»

**Privacy e consenso**
- F5, «Privacy disclosures»: «Publishers must: have and abide by a privacy policy that clearly discloses any data collection, sharing, and usage that takes place as a consequence of your use of Google products and services… The privacy policy must disclose to users that third parties may be placing and reading cookies on your users' browsers, or using web beacons or IP addresses to collect information as a result of ad serving on your website.»
- F10: i partner di AdSense «are required to use a consent management platform (CMP) that has been certified by Google and integrates with the IAB's Transparency and Consent Framework (TCF) when serving personalized ads to users in» SEE, Regno Unito (dal 16/1/2024) e Svizzera (dal 31/7/2024).
- F10: «Only traffic from a certified CMP is eligible for personalized ads.» «Traffic from a non-certified CMP may be eligible for non-personalized ads or limited ads».
- F11: «You must obtain end users' legally valid consent to: the use of cookies or other local storage where legally required; and the collection, sharing, and use of personal data for personalization of ads.»

**Altro**
- F5, «Authorized inventory»: niente annunci su un dominio con ads.txt dove l'editore non è tra i venditori autorizzati.
- F5: contenuto non «primarily in one of the supported languages» non ammesso.
- F4: «don't sign up while your site's still under construction or only consists of a site template.»
- F3: «When you've addressed the above points, submit your site for review… The review process usually takes a few days».

**Cosa Google NON scrive.** Non scrive un numero minimo di parole. Non scrive un numero minimo di pagine. Non chiede in modo esplicito una pagina «Chi siamo» o «Contatti» (chiede la privacy). Non scrive un tempo minimo tra due richieste. Le soglie in numeri qui sotto sono **nostre**: servono a rendere il criterio controllabile.

### 1.3 Lista dei criteri controllabili

| N. | Criterio | Come si controlla | Fonte |
|---|---|---|---|
| C1 | Nessun codice AdSense su pagine con poco testo proprio | Parole proprie per pagina (metodo al punto 2). Soglia nostra: 0 pagine con codice sotto 100 parole proprie | F4, F6 |
| C2 | Nessun codice su pagine quasi uguali tra loro | Somiglianza tra pagine della stessa famiglia. Soglia nostra: 0 pagine con codice con somiglianza ≥ 0,8; meno del 5 % con ≥ 0,6 | F3, F9 |
| C3 | Le pagine automatiche con il codice hanno una revisione a mano visibile | Testo scritto per quella pagina, non solo dati messi nel modello | F6, F7 |
| C4 | Nessun codice su pagine di servizio o senza contenuto | 404, contatti, grazie, privacy, pagine di soli link | F1, F6 |
| C5 | Il testo copiato da altri è minoranza e ha un commento nostro | Quota di parole dentro citazioni per famiglia. Soglia nostra: sotto il 30 % | F7 |
| C6 | Le affiliazioni sono una parte piccola | Link `rel="sponsored"` per pagina, contro le parole proprie | F4, F8 |
| C7 | Navigazione chiara e che funziona | Menu su ogni pagina, link interni rotti = 0, 404 vero | F3, F4 |
| C8 | Niente «in costruzione», niente pagine vuote | Ricerca nel testo; pagina con meno parole | F4, F6 |
| C9 | Niente redirect o blocchi sulle pagine in revisione | Home e pagine di punta rispondono 200 sul dominio richiesto | F4 |
| C10 | Privacy con la frase su cookie di terzi e pubblicità | Lettura di `privacy.html`, link in ogni piè di pagina | F5 |
| C11 | Chi siamo e Contatti presenti e raggiungibili | Non è un obbligo scritto. È prova di «background about the site» | F2, F3 |
| C12 | CMP certificata da Google per SEE/UK/Svizzera | Messaggio di consenso alla prima visita da un Paese UE | F10, F11 |
| C13 | ads.txt giusto | `/ads.txt` risponde 200 con il nostro codice editore | F5 |
| C14 | Codice AdSense sulla home e sulle pagine più viste | Sorgente della pagina in linea | F4 |
| C15 | Lingua supportata | Lingua delle pagine | F5 |
| C16 | Il sito dà un motivo per tornare ed è aggiornato | Date di controllo visibili, strumenti, contenuto scritto | F3 |

## 2. Metodo di misura

- Ho letto tutte le pagine HTML delle cartelle `sito/`: BYF 1.863, Visa 1.310, EsameB1 221.
- Le cartelle `sito/` sono uguali ai siti in linea. Ho confrontato le tre home: cambia solo il link `/privacy` riscritto da Netlify.
- Da ogni pagina ho tolto testata, menu, piè di pagina, script, stili e menu a tendina.
- **Parole proprie**: divido il testo in gruppi di 5 parole di fila. Un gruppo è «comune» se compare in almeno 3 pagine del sito. Una parola è «propria» se non sta in nessun gruppo comune.
- **Somiglianza**: quota di gruppi di 5 parole in comune tra due pagine della stessa famiglia (indice di Jaccard). 1,0 = pagine identiche.
- **Limite del metodo.** È severo. Un numero in una tabella conta come 1 parola. Una pagina di soli dati ufficiali diversi ha quindi poche «parole proprie» anche se i dati sono unici. Ma è anche il modo in cui la vede un revisore: stesso testo, cambia un nome e qualche cifra.
- Visite: file `studio-business/dati-recupero/visite-*.json` (GoatCounter).
- Siti in linea controllati con richieste dirette il 26/11: home, ads.txt, privacy, robots, sitemap, 404, pagine di punta, vecchi indirizzi netlify.

## 3. Before You Fly — RIFIUTATO il 24/11 («Low value content»)

### 3.1 Numeri

1.863 pagine. 1.552 con il codice AdSense. 309 in noindex (tutte senza codice: giusto).

| Famiglia | Pagine con codice | Parole totali (mediana) | Parole proprie (mediana) | Sotto 100 proprie | Somiglianza ≥ 0,6 | Con visite |
|---|---|---|---|---|---|---|
| available-in | 449 | 534 | **15** | **444** | **424** | 98 |
| canadian-passport | 229 | 729 | 79 | 136 | 95 | 35 |
| passport-validity | 225 | 813 | 118 | 89 | 38 | 18 |
| australian-passport | 173 | 1.124 | 180 | 33 | 46 | 22 |
| driving-abroad | 116 | 648 | 58 | 89 | 7 | 22 |
| liquids | 102 | 1.133 | 125 | 44 | 53 | 41 |
| cabin-bags | 53 | 1.597 | 469 | 10 | 10 | 14 |
| india-e-visa-fee | 25 | 1.289 | **24** | 21 | 23 | 15 |
| blue-badge-abroad | 24 | 1.230 | 104 | 12 | 19 | 3 |
| pets | 17 | 1.497 | **17** | 13 | 14 | 5 |
| ticket-release-dates | 33 | 1.418 | 715 | 0 | 0 | 13 |
| pagine principali (root) | 25 | 1.893 | 866 | 0 | 0 | 16 |
| public-transport, train-luggage, tolls, winter-tyres, foreign-licence, scooter, dog-airlines | 81 | 740-1.870 | 390-1.420 | 1 | 0 | 33 |
| **Totale** | **1.552** | | | **891** | **729** | 334 |

- Mediana della quota di parole proprie sulle pagine con codice: **9 %**.
- 1.218 pagine con codice non hanno nessuna visita nel file. 714 di queste hanno anche meno di 100 parole proprie.
- Coppie quasi identiche (≥ 0,9): `india-e-visa-fee/ghana` e `/italy` (0,93, 10 parole proprie); `/vietnam` e `/germany` (0,92); `cabin-bags/size/40x30x20` e `/40x20x25` (0,90).
- Esempio: `available-in/google-fi/india/` ha 680 parole. Di proprie ne restano una decina: cambia il nome del Paese e il «Yes».
- 6 delle 20 pagine più viste sono deboli: `available-in/starlink/saudi-arabia` (23 parole proprie), `/starlink/turkey` (11), `/starlink/germany` (9), `available-in/apple-pay/` (44), `liquids/barcelona` (85), `india-e-visa-fee/australia` (19).

### 3.2 Esito per criterio

| N. | Esito | Prova |
|---|---|---|
| C1 | **NO** | 891 pagine con codice sotto 100 parole proprie |
| C2 | **NO** | 729 pagine con codice con somiglianza ≥ 0,6; 66 con ≥ 0,8 |
| C3 | **NO** | available-in, india-e-visa-fee, pets, driving-abroad: dati nel modello, nessun testo scritto per la pagina |
| C4 | SÌ | 404, contatti e privacy senza codice. Indice `available-in/` è all'82 % link ma ha testo (9.130 parole) |
| C5 | **NO** in 2 famiglie | Citazioni: australian-passport 50 %, canadian-passport 35 %. Le altre 13-31 % |
| C6 | **NO** | 1.171 pagine con codice hanno link di affiliazione. **643 hanno 3 riquadri eSIM (Awin)** su pagine con 15-180 parole proprie. 2.231 link Awin in tutto |
| C7 | SÌ | Menu su ogni pagina. 0 link interni rotti. 404 vero |
| C8 | SÌ | Nessun «in costruzione». «Coming soon» è un dato (servizio non ancora nel Paese). Pagina più corta con codice: 335 parole |
| C9 | SÌ | Dominio nuovo risponde 200. Vecchio netlify fa 301 (è il motivo «Navigation» sul vecchio indirizzo, non su questo) |
| C10 | SÌ | `privacy.html`: sezione «Advertising (Google AdSense)», cookie di terzi, link «partner-sites», CMP. Link in ogni piè di pagina |
| C11 | SÌ | `/about/` (5.030 parole), `/how-we-check/`, `/contact/` |
| C12 | DA VERIFICARE | Cruscotto: messaggio pubblicato dal titolare il 12/11. Da qui non visibile |
| C13 | SÌ | `google.com, pub-3750093987658434, DIRECT, f08c47fec0942fa0` |
| C14 | SÌ | Codice sulla home e su tutte le 20 pagine più viste |
| C15 | SÌ | Inglese. La parte italiana è in noindex e senza codice |
| C16 | PARZIALE | Home con strumento e date di controllo: bene. Ma il 57 % delle pagine con codice è a modello |

### 3.3 Cose che non vanno, in ordine di rischio

**1. Codice AdSense su 891 pagine a modello con meno di 100 parole proprie (C1, C3). Rischio: altissimo. È il motivo scritto del rifiuto.**
- Correzione: togliere lo script AdSense da tutte le pagine sotto 100 parole proprie. Restano 661 pagine con codice.
- In pratica escono: quasi tutta available-in (444 su 449), india-e-visa-fee (21), pets (13), driving-abroad (89), canadian-passport (136), passport-validity (89), liquids (44), australian-passport (33), blue-badge (12), cabin-bags/size (10).
- File: `beforeyoufly/dati/noindex.json`, lista `senza_pubblicita` (oggi ha solo 3 voci). La legge `beforeyoufly/genera.py` righe 638-643. Poi `verifica.py` punto 33.
- Meglio: una regola stabile. Dopo la generazione, uno script misura le parole proprie e riscrive la lista. Così le pagine nuove non sfuggono.
- **Permessa ora: SÌ.** È posizionamento del codice. Non cambia URL, titoli, indice.
- Costo: zero. Il sito non è approvato, quindi quelle pagine oggi non rendono nulla.

**2. Pagine quasi uguali ancora in indice (C2). Rischio: alto. Google dice «we may review all pages of your site».**
- Togliere il codice (punto 1) risponde alla frase «don't place the ad code». Non cambia il fatto che il sito ha 892 pagine deboli indicizzabili. **Ipotesi mia**: il giudizio «low value» è sul sito intero, quindi il punto 1 da solo può non bastare.
- Correzione: `noindex` per le famiglie morte, poi unione nell'indice di sezione, come dice F3 («consolidating the pages into one»).
- File: `beforeyoufly/dati/noindex.json` (`fuori_indice`), `genera.py`.
- **Permessa ora: NO.** È una nuova ondata di noindex. Si fa solo dentro l'azione 7 della strategia (2/12, oppure 9/12). L'unione con 301 solo dal 23/12.

**3. Tre riquadri di affiliazione eSIM su 643 pagine deboli (C6). Rischio: alto.**
- Su `canadian-passport/japan/` ci sono 3 riquadri eSIM (Roamable, Vodafone, Pocket) con la stessa frase. Su una pagina con 79 parole proprie la promozione pesa più del contenuto. Con AdSense sopra, la pagina rischia F8.
- Correzione: al massimo 1 riquadro per pagina. Nessun riquadro sulle pagine sotto 100 parole proprie.
- File: `beforeyoufly/genera.py` (funzioni dei riquadri «Before you go»), `beforeyoufly/dati/affiliati.json`.
- **Permessa ora: SÌ per la lettera del fermo** (non è URL, titolo, noindex, sezione). Ma tocca 640 pagine: va nella stessa unica pubblicazione del punto 1, non in una a parte.

**4. Testo copiato dai governi oltre un terzo della pagina (C5). Rischio: medio.**
- australian-passport: metà delle parole sono citazioni di Smartraveller. canadian-passport: 35 %.
- La licenza permette la copia. Ma F7 chiede «additional commentary, curation».
- Correzione: sulle pagine che tengono il codice, accorciare la citazione al punto che conta e aggiungere 2-3 frasi nostre (cosa cambia per chi parte, confronto con la regola UK). Partire dalle 22 + 35 pagine con visite.
- File: `beforeyoufly/genera.py`, sezioni australian-passport e canadian-passport.
- **Permessa ora: SÌ se pagina per pagina** (correzione di singole pagine). No come riscrittura in blocco.

**5. Le pagine più viste sono deboli (C1, C14). Rischio: medio.**
- Il revisore entra dalla home e dai link «Most used». Trova `available-in/starlink/…` con 9-23 parole proprie.
- Correzione: arricchire a mano le 6 pagine deboli tra le prime 20 (elenco al punto 3.1). Finché non sono arricchite, toglierle dal blocco «Most used» della home.
- File: `beforeyoufly/genera.py` (blocco `usate-home`), dati della sezione available-in.
- **Permessa ora: SÌ** (singole pagine).

**6. Consenso UE da verificare (C12). Rischio: basso per l'approvazione, alto per la legge.**
- Vedi punto 6.

## 4. Visa Income Checker — «Getting ready»

### 4.1 Numeri

1.310 pagine. 803 con il codice. 497 in noindex (senza codice).

| Famiglia | Pagine con codice | Parole totali (mediana) | Parole proprie (mediana) | Sotto 100 proprie | Somiglianza ≥ 0,6 | Con visite |
|---|---|---|---|---|---|---|
| australian-citizenship-ceremony-wait-times | 173 | 943 | **30** | **168** | **165** | 73 |
| visa-refusal-rates | 153 | 1.757 | 469 | 1 | 0 | 103 |
| moved-to | 94 | 1.057 | 151 | 8 | 0 | 45 |
| uk-english-test | 84 | 1.591 | 109 | 40 | **75** | 50 |
| h1b-wage-level | 55 | 1.171 | 390 | 18 | 20 | 11 |
| pagine principali (root) | 45 | 1.290 | 661 | 0 | 2 | 28 |
| es/visados | 29 | 775 | **26** | **28** | 15 | 7 |
| thailand-dtv-visa | 22 | 893 | 131 | 8 | 5 | 4 |
| nurses-abroad | 16 | 1.380 | 170 | 0 | 4 | 6 |
| mexico-residency | 12 | 1.104 | 138 | 4 | 8 | 2 |
| top-university-visas | 12 | 1.298 | 93 | 7 | 8 | 7 |
| schengen-visa-from-uk + from-dubai | 17 | 1.280-1.380 | 83-94 | 11 | 17 | 4 |
| country | 5 | 421 | 41 | 5 | 0 | — |
| es, pt (altre) | 33 | 800-880 | 205-355 | 4 | 9 | 13 |
| altre (study-in-italy, australia-visas, salute, OPT…) | 53 | 680-3.020 | 165-2.635 | 2 | 2 | — |
| **Totale** | **803** | | | **304** | **330** | 364 |

- Mediana della quota di parole proprie: **15 %**.
- Coppie quasi identiche: `uk-english-test/exeter` e `/coventry` (0,90, 19 parole proprie), `/maidstone`, `/southampton`, `/milton-keynes` (0,90). 35 pagine di uk-english-test sopra 0,8. 37 pagine dei consigli australiani sopra 0,8.
- La sezione forte è `visa-refusal-rates`: 153 pagine, 469 parole proprie, 508 visite. Qui il codice sta bene.

### 4.2 Esito per criterio

| N. | Esito | Prova |
|---|---|---|
| C1 | **NO** | 304 pagine con codice sotto 100 parole proprie |
| C2 | **NO** | 330 pagine con somiglianza ≥ 0,6; 77 con ≥ 0,8 |
| C3 | **NO** | Consigli australiani, uk-english-test, es/visados: solo dati nel modello |
| C4 | PARZIALE | 404 e contatti senza codice. **`privacy.html` ha il codice** (su BYF no) |
| C5 | SÌ | Citazioni sotto il 30 % quasi ovunque (germany-health-insurance 36 %, 7 pagine) |
| C6 | PARZIALE | 427 pagine con link di affiliazione, quasi tutte con 1-2. **`schengen-visa-insurance/` ne ha 12** |
| C7 | SÌ | Menu e piè di pagina completi. 0 link rotti. 404 vero |
| C8 | SÌ | Nessun «in costruzione». Pagina più corta con codice: 368 parole |
| C9 | SÌ | Dominio 200. Vecchio netlify 301 |
| C10 | SÌ | Privacy con AdSense, cookie di terzi, CMP, Grow |
| C11 | SÌ | `/about/` (1.955 parole), `/how-it-works/`, `/contact/` |
| C12 | DA VERIFICARE | Come BYF |
| C13 | SÌ | ads.txt giusto |
| C14 | SÌ | Codice sulla home e sulle 20 pagine più viste |
| C15 | SÌ | Inglese, spagnolo, portoghese |
| C16 | PARZIALE | Calcolatore e sezione rifiuti: bene. 38 % delle pagine con codice a modello |

### 4.3 Cose che non vanno, in ordine di rischio

**1. Codice su 304 pagine a modello sotto 100 parole proprie (C1, C3). Rischio: altissimo. È lo stesso profilo per cui BYF è stato rifiutato due giorni fa, e la revisione è in corso.**
- Correzione: togliere lo script da quelle 304 pagine **subito**, prima che arrivi il verdetto. Restano 499 pagine con codice.
- Escono: consigli australiani (168 su 173), uk-english-test (40), es/visados (28), h1b (18), schengen-from (11), thailand (8), moved-to (8), top-university (7), country (5), mexico (4), altre (7).
- La strategia lo diceva già: «Su Visa applicare comunque il punto 1». Non è stato fatto.
- File: `visaincome/genera.py` riga 1052 (`MIN_PAROLE_ADSENSE`) e riga 1082 (scelta dello script). La soglia sulle parole totali non basta. Serve una lista `senza_pubblicita` come su BYF, riempita dalla misura delle parole proprie.
- **Permessa ora: SÌ.**

**2. Pagine quasi uguali in indice: uk-english-test e consigli australiani (C2). Rischio: alto.**
- 75 pagine uk-english-test e 165 pagine dei consigli sopra 0,6.
- Correzione piena: noindex o unione nell'indice di sezione (la tabella con tutti i consigli c'è già).
- **Permessa ora: NO** (ondata di noindex, poi cambio URL). Solo con l'azione 7, poi dal 23/12.
- Correzione permessa ora: sulle pagine con visite (73 + 50), aggiungere testo vero pagina per pagina. Esempio per i consigli: andamento rispetto al trimestre prima, prossima cerimonia annunciata dal consiglio, con fonte. SÌ se a piccoli gruppi.

**3. es/visados: 28 pagine su 29 con 26 parole proprie (C1, C3). Rischio: medio-alto.**
- Stesso testo, cambia nazionalità e Paese. È il caso «cookie cutter» di F9.
- Correzione: rientra nel punto 1 (via il codice). Poi 3-4 frasi specifiche per pagina solo sulle 7 con visite.
- File: `visaincome/genera.py`, sezione spagnola.
- **Permessa ora: SÌ** (codice e singole pagine).

**4. `schengen-visa-insurance/` con 12 link di affiliazione (C6). Rischio: medio.**
- F4: le affiliazioni devono essere «only a minor part».
- Correzione: ridurre a 3-4 link, tenere il confronto in tabella con criteri nostri. Oppure togliere il codice AdSense da quella pagina.
- File: `visaincome/genera.py`, pagina schengen-visa-insurance; `visaincome/dati/affiliati.json`.
- **Permessa ora: SÌ** (singola pagina).

**5. Codice AdSense su `privacy.html` (C4). Rischio: basso.**
- F1: niente annunci «on any non-content-based page». BYF lo ha già tolto.
- Correzione: aggiungere `privacy.html` alle pagine senza pubblicità.
- File: `visaincome/genera.py` riga 1082.
- **Permessa ora: SÌ.**

## 5. EsameB1 — «Getting ready» (revisione in corso)

Precedente: `esameb1.netlify.app` è stato rifiutato l'8/11 per «contenuti di scarso valore». Il motivo erano le pagine città. Dal 13/11 le città sono state riordinate e 7 comuni uniti.

### 5.1 Numeri

221 pagine. 212 con il codice. 7 in noindex.

| Famiglia | Pagine con codice | Parole totali (mediana) | Parole proprie (mediana) | Sotto 100 proprie | Sotto 200 | Somiglianza ≥ 0,6 | Visite |
|---|---|---|---|---|---|---|---|
| citta | 81 | 1.218 | 162 | **8** | 56 | 17 | 920 |
| cittadinanza (Prefetture) | 30 | 712 | 217 | 0 | 12 | 0 | 30 |
| guide principali (root) | 25 | 1.602 | 1.029 | 0 | 0 | 0 | 571 |
| en | 17 | 828 | 444 | 0 | 1 | 0 | 105 |
| esempi | 13 | 1.694 | 608 | 0 | 0 | 2 | 289 |
| cpia | 12 | 1.475 | 290 | 0 | 2 | 2 | 0 |
| uk, ro | 21 | 983-1.031 | 706-709 | 0 | 0 | 0 | 10 |
| dopo-esame, risultati, ente | 13 | 1.128-3.879 | 383-1.989 | 0 | 0 | 0 | 178 |
| **Totale** | **212** | | | **8** | 71 | 21 | 2.103 |

- Mediana della quota di parole proprie: **29 %** (BYF 9 %, Visa 15 %).
- Nessuna coppia sopra 0,8. La più alta: `citta/treviglio` e `citta/crema` (0,66).
- Le 8 città sotto 100 parole proprie: treviglio (53), crema (55), arzignano (65), busto-arsizio (84), novara (88), grosseto (92), isernia (97), belluno (98). Sono città con 1 sola sede.
- Le 20 pagine più viste hanno tutte il codice. Nessuna è debole.

### 5.2 Esito per criterio

| N. | Esito | Prova |
|---|---|---|
| C1 | QUASI | 8 pagine con codice sotto 100 parole proprie (4 %) |
| C2 | SÌ (al limite) | 0 sopra 0,8. 17 città sopra 0,6 (8 %) |
| C3 | SÌ | Città con sedi, indirizzi, telefoni, Prefettura. Guide scritte a mano |
| C4 | PARZIALE | 404 e contatti senza codice. **`privacy.html` ha il codice** |
| C5 | SÌ | Nessuna famiglia con citazioni sopra il 12 % |
| C6 | SÌ | 108 pagine con 2 link (il libro su Amazon). Parte piccola |
| C7 | SÌ | Menu, lingue, piè di pagina completo. 0 link rotti |
| C8 | SÌ | Nessun «in costruzione». Pagina più corta con codice: 462 parole |
| C9 | SÌ | esameb1.eu 200. `/iscrizione/` (pubblicata oggi) 200 con codice |
| C10 | SÌ | Privacy con «Pubblicità (Google AdSense)», cookie di terzi, CMP |
| C11 | SÌ | `/chi-siamo/`, `/come-lavoriamo/`, `/contatti/` |
| C12 | DA VERIFICARE | Come gli altri |
| C13 | SÌ | ads.txt giusto |
| C14 | SÌ | Home, Milano, esempi/cils, ente/cils, costo: tutte con codice |
| C15 | SÌ | Italiano, inglese, ucraino, romeno: tutte lingue supportate |
| C16 | SÌ | Date d'esame aggiornate, avvisi, guide. 2.103 visite nel file |

### 5.3 Cosa fare ORA su esameb1.eu

**C'è qualcosa che rischia il rifiuto? Sì, una cosa sola: le città piccole.** È lo stesso tipo di pagina del rifiuto dell'8/11. Oggi sono molto migliori (parole proprie da 44-66 a 162 di mediana). Restano 8 pagine sotto 100 e 17 simili tra loro oltre 0,6. Il rischio è **medio-basso**, non zero.

Correzioni da pubblicare oggi. EsameB1 non è sotto il fermo.

1. **Togliere il codice AdSense dalle 8 città sotto 100 parole proprie.** Le pagine restano in linea, in indice e nei link. Si toglie solo lo script.
   - File: `esameb1/genera.py`, `testa_adsense()` (righe 58-73). Aggiungere una lista di percorsi senza pubblicità, oppure una seconda soglia sulle parole proprie.
   - Rischio della modifica: nullo. La home e le pagine forti tengono il codice.
2. **Togliere il codice da `privacy.html`** (e dalle privacy in en/uk/ro se ci sono). Stessa funzione.
3. **Non toccare altro fino al verdetto.** Niente pagine città nuove. Niente nuovi comuni CPIA in blocco: la famiglia `cpia` ha 12 pagine con 0 visite, va bene così ma non va allargata adesso.
4. **Controllo C12 del titolare** (punto 6). Due minuti.
5. Facoltativo, entro la settimana: 2-3 frasi vere su ognuna delle 8 città (come si arriva alla sede, se la sede risponde al telefono, costo chiesto dalla sede). Poi il codice può tornare.

Cosa NON fare: non togliere il codice dalla home. Non cambiare l'URL richiesto in AdSense. Non rimandare la richiesta: la revisione è già partita.

## 6. Consenso per i visitatori UE (C12)

- **È obbligatoria una CMP certificata da Google?** Sì, per mostrare annunci personalizzati a utenti di SEE, Regno Unito e Svizzera (F10). Senza CMP certificata il traffico può avere solo annunci non personalizzati o limitati.
- In più F11 chiede sempre il consenso per i cookie «where legally required». In Italia è richiesto.
- **L'abbiamo?** Nelle pagine non c'è nessun banner nostro. È giusto così: la CMP di Google («Privacy e messaggi») è caricata dallo script `adsbygoogle.js` ed è già certificata.
- `CRUSCOTTO-RETE.md` (riga del 12/11) dice: messaggio «European regulations» pubblicato dal titolare il 12/11 sui 3 domini, con Consent / Do not consent / Manage options.
- Le tre privacy lo descrivono in modo corretto.
- **Da qui non posso vederlo.** Il messaggio esce solo in un browser vero con indirizzo europeo. E non so se Google lo mostra già su un sito in «Getting ready» o rifiutato.
- **Controllo del titolare:** aprire esameb1.eu, visaincomechecker.com e before-you-fly.com in una finestra anonima dall'Italia. Deve comparire il messaggio di Google. Se non compare: AdSense → Privacy e messaggi → Regolamenti europei → controllare che i 3 domini siano nella lista dei siti del messaggio e che lo stato sia «Pubblicato».
- Nota fuori da AdSense: BYF e Visa caricano anche Grow (Mediavine) su ogni pagina. La privacy lo dichiara. Non è un criterio AdSense. Resta da capire se Grow scrive nel browser prima del consenso: è un tema di legge sui cookie, da guardare a parte.

## 7. Lista che BYF deve passare prima di richiedere la revisione

Soglie nostre, costruite sulle frasi di Google. Stato al 26/11.

| N. | Criterio | Oggi | Esito |
|---|---|---|---|
| 1 | 0 pagine con codice sotto 100 parole proprie | 891 | **NO** |
| 2 | 0 pagine con codice con somiglianza ≥ 0,8 | 66 | **NO** |
| 3 | Meno del 5 % delle pagine con codice con somiglianza ≥ 0,6 | 47 % (729) | **NO** |
| 4 | Mediana delle parole proprie sulle pagine con codice ≥ 200 | 71 | **NO** |
| 5 | Al massimo 1 riquadro di affiliazione per pagina; nessuno sotto 100 parole proprie | 643 pagine con 3 | **NO** |
| 6 | Nessuna famiglia con codice con citazioni oltre il 30 % senza commento nostro | australian 50 %, canadian 35 % | **NO** |
| 7 | Le 20 pagine più viste hanno tutte ≥ 100 parole proprie | 6 sotto | **NO** |
| 8 | Codice sulla home e sulle pagine di punta | sì | SÌ |
| 9 | Nessun codice su 404, contatti, privacy, pagine noindex | 0 | SÌ |
| 10 | 0 link interni rotti; 404 vero; menu su ogni pagina | 0 | SÌ |
| 11 | Privacy con AdSense e cookie di terzi; link nel piè di pagina | sì | SÌ |
| 12 | Chi siamo, Come controlliamo, Contatti | sì | SÌ |
| 13 | ads.txt giusto | sì | SÌ |
| 14 | Messaggio di consenso di Google visibile dall'Italia | non verificato | **DA VERIFICARE** |
| 15 | Pagine deboli indicizzabili: meno del 20 % delle pagine in indice | 57 % (892 su 1.554) | **NO** (si può sistemare solo con l'azione 7) |
| 16 | Correzioni in linea da almeno 14 giorni; nessuna pubblicazione di massa nel frattempo (criteri 2 e 4 dell'azione 8) | non partito | **NO** |
| 17 | Almeno 20 delle 30 pagine di punta indicizzate (criterio 3 dell'azione 8) | da Search Console | **DA VERIFICARE** |

**Oggi: 6 SÌ, 9 NO, 2 da verificare. Non richiedere la revisione.** La data «non prima del 16/12» della strategia resta giusta solo se i punti 1-7 escono entro il 2/12.

## 8. Ordine di lavoro proposto

| Quando | Cosa | Sito | Fermo |
|---|---|---|---|
| Oggi | Via il codice da 8 città e dalla privacy | EsameB1 | non si applica |
| Oggi | Via il codice da 304 pagine sotto 100 parole proprie e dalla privacy | Visa | permesso |
| Oggi | Controllo del messaggio di consenso in finestra anonima | tutti (titolare) | — |
| Entro il 2/12, una sola pubblicazione | Via il codice da 891 pagine; 1 solo riquadro eSIM; pagine deboli fuori da «Most used» | BYF | permesso |
| Entro il 2/12 | Regola stabile nei tre `genera.py`: soglia sulle parole **proprie**, non sulle totali. Controllo nuovo in `verifica.py` | tutti | permesso |
| 2/12 o 9/12 | Azione 7: noindex delle famiglie morte | BYF, Visa | solo come azione 7 |
| Da subito, a piccoli gruppi | Testo vero sulle pagine deboli che hanno visite | BYF, Visa | permesso (singole pagine) |
| Dal 23/12 | Unione delle famiglie morte nell'indice di sezione | BYF, Visa | prima no |
| Non prima del 16/12 | Nuova richiesta di revisione BYF, se la lista del punto 7 è tutta SÌ | BYF | — |

## 9. Cosa non so

- Non so quali pagine ha guardato il revisore di BYF. Google non lo dice.
- Non so se togliere il codice dalle pagine deboli basta, o se Google giudica anche le pagine senza codice. La frase «we may review all pages of your site» fa pensare alla seconda. Per questo il punto 15 della lista.
- Le soglie (100 parole proprie, 0,6, 0,8, 30 %) sono mie. Google non dà numeri.
- Il messaggio di consenso non è verificato da qui.
- Il periodo esatto dei file delle visite non l'ho ricontrollato: ho usato i file così come sono in `dati-recupero/`.
