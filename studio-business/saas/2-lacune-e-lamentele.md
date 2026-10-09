## Lacune di mercato documentate (ottobre 2026) — per micro-SaaS costruibile in 4-8 settimane

Nota metodologica: WebSearch non indicizza bene Reddit (operatore site: inefficace) e Trustpilot/BBC/VRT sono bloccati dal proxy; le prove Reddit sono quindi citate di seconda mano (BBC, Clockify, Prospeo). Dove scrivo **[V]** il dato è verificato da fonte citata; **[H]** = ipotesi mia.

### A. Prezzi alzati dal leader → utenti in fuga (categoria c)

**1. Harvest (time tracking + fatturazione per agenzie/consulenti)** — la lacuna più "calda".
- [V] Dopo l'acquisizione da Bending Spoons, Harvest è passato a "Flex usage billing" (tariffe per progetto/cliente/fattura NON pubblicate). Casi riportati da BBC e ripresi da [Silicon UK](https://www.silicon.co.uk/e-enterprise/merger-acquisition/harvest-price-shock-631249) e [Subscription Insider](https://www.subscriptioninsider.com/blog/harvest-pricing-change-sends-some-renewals-up-1-500): consulenza UK da $130 a $2.110/mese; utente USA da $2.800 a $23.000/anno; web designer da $211/anno a $2.547; utente Reddit da $12 a $116/mese; un altro Reddit (via [Clockify](https://clockify.me/blog/apps-tools/harvest-pricing/)) da $180 a $2.162/mese per 15 seat. Checkout preseleziona "Enterprise+annuale". Un utente ha dichiarato di aver ricostruito le funzioni con Claude Code.
- [V] Concorrenti già a caccia: Clockify, TimeCamp, Productive offrono migrazione gratuita.
- [V] Ma Clockify ha svuotato il piano free il 21/4/2026 ([Jibble](https://www.jibble.io/news/changes-clockify-free-pricing-users-impact), [forum Clockify "Death of the free plan"](https://forum.clockify.me/t/death-of-the-free-plan/10006)): export CSV/Excel, ore fatturabili, report condivisi passati a pagamento, API 30 richieste/ora; Trustpilot sceso a 3,1/5.
- Prezzi di riferimento: Harvest Teams $9-11/utente, Toggl $9-10/utente, Clockify $3,99-5,49/seat. Pubblico [H]: decine di migliaia di micro-agenzie (dato clienti Harvest non trovato).
- Dove raggiungerli: recensioni G2/Capterra di Harvest e Clockify, r/freelance, r/consulting, r/agency, thread "Harvest alternative"; copertura stampa anti-Bending-Spoons (Evernote, WeTransfer) genera SEO.
- Rischi: categoria affollata; Harvest potrebbe fare marcia indietro; servono integrazioni (Stripe, QuickBooks/Xero).

**2. Mailchimp** — [V] piano free tagliato a 250 contatti/500 invii dal 17/2/2026, +11-13% sui legacy ([Beehiiv](https://www.beehiiv.com/blog/navigating-mailchimp-s-new-free-limits-essential-updates-for-newsletter-owners)); 321 domini migrati a MailerLite in 90 giorni (tracker, metodo non chiaro). Verdetto: lacuna già colmata da MailerLite ($9), Brevo, Kit → **non consigliata**.

**3. QuickBooks Online** — [V] +17-25% nel 2026 (Plus $90→$110; UK Plus £34→£50) ([beancount](https://beancount.io/blog/2026/07/26/quickbooks-online-price-increase-2026-cost-breakdown-guide)). Troppo grande da ricostruire; utile solo come segnale per nicchie contigue (vedi n.6).

**4. Podium/Birdeye (recensioni Google per PMI locali)** — [V] Podium $249-599/mese + fee, 63 reclami BBB in 3 anni soprattutto per auto-rinnovo; Birdeye $299-449/sede ([CostBench](https://costbench.com/compare/birdeye-vs-podium/), [Prospeo](https://prospeo.io/s/podium-alternatives)). Alternative economiche esistono (NiceJob $75, WiserReview $9) → spazio per uno strumento "solo richiesta recensioni SMS/email" a $19-29/mese [H]. Rischio: registrazione 10DLC SMS negli USA, affollamento.

### B. Software di nicchia con recensioni negative (categoria b)

**5. Hubdoc (acquisizione ricevute, Xero)** — [V] Capterra 4,2/5 su 92 recensioni, assistenza 3,8 ([Capterra](https://capterra.com/p/165724/Hubdoc/reviews/)); forum idee Xero 6/5/2026: "5 years, no update? …dealbreaker that we ditch Xero"; Trustpilot 2024-26: "hardly processes invoices automatically", "clunky". Dext (alternativa) $25-34/mese con vincolo annuale e modello per-cliente definito "expensive" ([Datamolino](https://datamolino.com/blog/pricing-and-features-autoentry-vs-hubdoc-vs-dext-vs-datamolino-in-2026)). Lacuna [H]: estrazione AI a livello di riga → Xero/QBO per micro-imprese a $8-12/mese. Rischio: dipendenza da API partner Xero/Intuit, qualità OCR.

### C. Funzioni mancanti nei software più usati (categoria a)

**6. Shopify – IVA B2B UE / reverse charge per negozi non-Plus** — [V] Thread community: "Shopify ha alzato Plus da <$2.000 a $2.300 invece di sistemare questa funzione ultra-base" ([community](https://community.shopify.com/t/invoice-and-vat-option-on-checkout-for-europe/392729)). Changelog 25/2/2026: validazione IVA nativa solo con Shopify Tax + magazzino UE. App esistenti $4,99-49,99/mese con poche recensioni (33-38); Exemptify 3,3/5 con 17% a 1 stella; una recensione tedesca segnala che manca la "validazione qualificata" (indirizzo) richiesta dal fisco ([apps.shopify.com/exemptify](https://apps.shopify.com/exemptify)). Lacuna [H]: app con validazione VIES qualificata + fattura conforme + registro prove. Rischio: Shopify estende la funzione nativa.
- Altri gap Shopify documentati ma più deboli: modifica ordine post-acquisto (app Cleverific "pricey for small businesses"), campo P.IVA, metafield import/export.

### D. Nuovi obblighi di legge 2025-2027 (categoria d)

**7. Fatturazione elettronica Peppol — Belgio (già in vigore), Francia, Germania**
- [V] Belgio: obbligo B2B dal 1/1/2026, 1,06 M imprese registrate (89%); sondaggio Unizo ago 2026: solo il 38% ha trovato la transizione fluida ([VRT](https://www.vrt.be/vrtnws/en/2026/08/03/9-out-of-10-businesses-connect-to-peppol-invoice-network/)); sondaggio NSZ feb 2026 (~700 autonomi): metà dice che i costi sono saliti, 1/3 che richiede più tempo. Richiesta EEN di una PMI belga: "soluzioni troppo care per chi emette poche fatture". Prezzi: recommand.eu free 25 doc/mese poi €0,30, Starter €29; e-invoice.be €0,25/fattura; Accountable gratis ([recommand](https://www.mediaatelier.com/en/Posts/E-Invoices-Belgium/)). Deducibile al 120%.
- [V] Francia: dal 1/9/2026 TUTTE le imprese (anche micro in franchigia IVA) devono ricevere e-fatture via piattaforma agréée (137 PA); emissione micro dal 9/2027 ([Dougs](https://www.dougs.fr/blog/facturation-electronique-auto-entrepreneur/)).
- [V] Germania: ricezione dal 2025, emissione 2027 (>€800k) e 2028 (tutti); tool da €9,90/mese ([kostenlose-erechnung.de](https://kostenlose-erechnung.de/ratgeber/e-rechnung-kleinunternehmer/)).
- [V] Polonia: micro dal 1/2027 ma app governativa gratuita → poco spazio.
- Lacuna [H]: tool in inglese "Peppol inbox + converti PDF/CSV in UBL/ZUGFeRD/Factur-X + archivio 8-10 anni" per freelance/PMI estere che fatturano a clienti BE/FR/DE, appoggiato all'API di un access point certificato (recommand). Rischi: i locali offrono gratis; il vero dolore è la doppia immissione verso la contabilità.

**8. Cyber Resilience Act** — [V] dal 11/9/2026 obbligo di segnalare vulnerabilità sfruttate (24h/72h/14gg) per TUTTI i produttori software, nessuna esenzione per dimensione; ENISA: nessuna API della Single Reporting Platform ([ENISA](https://www.enisa.europa.eu/cra-srp/), [Advisori](https://www.advisori.de/blog/cra-single-reporting-platform-srp-registration)). Lacuna [H]: kit di triage, scadenze e bozze per micro-vendor. Domanda pagante NON provata.

**9. AI Act art. 50** — [V] in vigore dal 2/8/2026 (l'Omnibus ha rinviato solo l'alto rischio al 12/2027); sanzioni fino a €15M/3% ([Goodwin](https://goodwinlaw.com/en/insights/publications/2026/08/alerts-technology-dpc-eu-ai-act-transparency-obligations-now-in-force)). Tool esistenti: AI Disclosure Kit (0 upvote), Uixtra scanner. Domanda non provata.

**10. EAA, GPSR, DPP, NIS2, DAC7, MTD UK, EUDR** — [V] già coperti o prematuri: statement EAA su Shopify a $9,99-29/mese; app GPSR gratis/$15; DPP tessile solo 2027-28 (DPP Hero $57-289/mese); NIS2 tool €5-40k/anno ma micro-imprese fuori ambito; MTD UK (864k sole trader da 4/2026) ha già tool a £19,99/anno; EUDR micro dal 30/6/2027. DAC7: nessun tool lato venditore trovato → ipotesi pura.

### Le 5 lacune migliori

1. **Time tracking + fatture a prezzo fisso per micro-agenzie** (profughi Harvest/Clockify): domanda pagante provata ($9-14/utente), difetti documentati, raggiungibili su G2/Reddit/thread "alternative"; build 4-6 settimane (timer, progetti, report, fatture Stripe).
2. **Ponte Peppol/e-fattura in inglese per PMI che fatturano a BE/FR/DE**: obbligo certo, prezzo di riferimento €0,25-0,30/doc o €29/mese; raggiungibili via community expat/freelance (r/belgium, Malt, Indie Hackers); build 6-8 settimane su API access point.
3. **App Shopify IVA B2B UE con validazione qualificata** per negozi non-Plus: lamentele documentate, prezzi $9-25/mese, canale App Store + community; build 4-6 settimane.
4. **Estrazione ricevute/righe fattura economica per Xero/QBO** (gap Hubdoc): recensioni negative numerose, prezzo riferimento $12-34/mese, raggiungibili su community Xero e r/Bookkeeping; build 6-8 settimane (LLM vision + API Xero).
5. **Richiesta recensioni Google per servizi a domicilio** (profughi Podium): prezzi incumbent $249-599 vs target $19-29; raggiungibili su r/HVAC, r/Plumbing, gruppi Facebook contractor; build 4 settimane. Rischio maggiore: affollamento e SMS compliance.

Scartate per domanda non provata: CRA kit, AI Act badge, DAC7, DPP.