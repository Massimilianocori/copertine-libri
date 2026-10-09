**Studio: come i micro-SaaS trovano i primi 100 clienti (2025-2026)**

Nota metodologica: indiehackers.com e saasranger.com sono bloccati dal proxy; i dati da quei siti vengono dai riassunti di ricerca, non da lettura diretta. Pochissime fonti sono dataset primari; molte sono blog di vendor.

---

## 1. Canali che hanno funzionato (DATI VERIFICATI, con riserva sulla qualità delle fonti)

**Analisi di 326 micro-SaaS (SaaSRanger):** fonte del primo cliente = passaparola/rete personale 40, app marketplace 33, SEO 27, Reddit/comunità 20, outreach diretto 15, Product Hunt 8, **ads a pagamento solo 4 su 326**. (Fonte: saasranger.com; sample autoselezionato.)

**Reddit** (post Indie Hackers 2025-2026): un founder a 60 clienti paganti in 3 mesi rispondendo a thread con poco engagement; MediaFast a 2.000$ MRR quasi solo da Reddit (47 conversazioni → 4 paganti da un singolo thread); un terzo 47 clienti B2B a ~10 ore/settimana. Ricorrenti: cercare parole del *dolore* non della categoria, rispondere nelle prime ore, account con 30+ giorni e karma (account nuovi vengono filtrati; un founder bannato 2 volte in una settimana per link). Subreddit verticali da 10-50k membri > r/Entrepreneur.

**Product Hunt:** spike di 48 ore, conversione a pagante 1-5% dei signup; casi documentati: 450 upvote/100 signup/0 paganti; 1.000+ visitatori/0 paganti; HN ha portato 3× più traffico di PH per un founder. Utile per backlink e feedback, non per i primi 100 clienti.

**SEO/programmatic SEO:** nessun caso tracciato da zero per un indie. Casi agency: dominio nuovo → 13 lead inbound in 4 mesi; timeline tipiche 6-18 mesi. Proxycurl: 30-50% dei clienti 11-100 da SEO. Verdetto: canale di fase 2-3, non di partenza.

**Threads/X (build in public):** un founder a 100+ paganti solo da Threads, commentando più che postando (educa → agita il problema → presenta il prodotto).

**YouTube:** aneddoto: video da 370 view → 3 clienti (345$ MRR); video da 12.000 view → 213$ in 6 mesi. L'intento di ricerca conta più delle view.

**Affiliati (Rewardful, 68,4M$ analizzati):** commissione media 24%, conversione referral→vendita 0,8%, solo 1,28% degli affiliati genera almeno una vendita. Inutile prima di avere trazione.

**Newsletter sponsorship:** CPM B2B SaaS 90-150$ diretto; placement minimo ~1.100$. Fuori budget.

**Google Ads "alternative to [competitor]":** CPC d'esempio 1,97$ vs 21-80$ per keyword di categoria; un'agency riporta CPA -40% (non verificato). Con 100-300 €/mese fattibile **solo** su 3-5 keyword exact-match "X alternative".

## 2. CAC per piccolo SaaS B2B (DATI VERIFICATI, forte dispersione)

- SMB mediane (UnbuiltLab): SEO 120$, Google Ads 420$, LinkedIn Ads 700$.
- 939 aziende B2B (Optifai): inbound 200$, partner/referral 150$, paid 350$, outbound 400$.
- Data-Mania: SaaS small business 100-400$.
- Il CAC paid è sottostimato del 30-60% rispetto al blended (ClearBrand).
**Implicazione:** con prezzo 15-30 €/mese, i canali paid sono fuori payback; solo referral/comunità/marketplace stanno sotto 150$.

## 3. Conversione trial → pagante 2026 (DATI VERIFICATI)

- Senza carta: 4-6% "buono", 10-15% ottimo; mediana opt-in ~8,9%; First Page Sage (50+ clienti B2B): **18,2%** opt-in vs **48,8%** con carta.
- Modello ChartMogul per 1.000 visitatori: senza carta 45 signup → 3,6 paganti; con carta 35 signup → **10,5 paganti** (~3×).
- Mediana generale freemium/free-to-paid: 8%.
**Ipotesi:** per un prodotto a basso prezzo, carta richiesta + trial 7-14 giorni massimizza i paganti; senza carta massimizza feedback. Testare per 1.000 visitatori, non per %.

## 4. Marketplace: clienti organici e commissioni (DATI VERIFICATI)

| Marketplace | Commissione | Note |
|---|---|---|
| Shopify App Store | 0% fino a 1M$ **lifetime** (non più annuale dal 2025), poi 15% + 2,9% processing | Ricerca organica "quasi nulla a zero recensioni"; i primi 100 install vengono da fuori store |
| WordPress.org + Freemius | Directory gratis; Freemius 4,7%+2,3% WP (~10,5% con gateway) dal 1/10/2025 | WP Umbrella bootstrapped a 110k$ MRR nel 2025 |
| Atlassian Marketplace | Forge: 0% fino a 1M$ lifetime dal 1/1/2026 (poi 16-17%); Connect: 20% → 25% dal 7/2026 | Possibile vendita diretta senza revenue share |
| HubSpot | 0 fee listing/transazione; billing a carico tuo | Dal 22/9/2025 app non listate limitate a 25 install → listarsi conviene |
| Chrome Web Store | 5$ una tantum; pagamenti interni rimossi nel 2021 → Stripe/Paddle/ExtensionPay (~5%) | Nessun dato su install organici per app nuove |
| Zapier | Nessuna fee; landing page dedicate per integrazione; tier su utenti attivi | Distribuzione, non vendite dirette |
| Slack / Notion | Nessuna fee trovata; Notion ora self-serve (review 5-10 gg) | Dati clienti organici: assenti |

**Ipotesi:** per un'app nuova, il marketplace che paga di più è quello dove il problema è *già cercato* dentro la piattaforma (Shopify, WordPress, Atlassian); Chrome/Notion/Slack sono vetrine, non motori di vendita.

## 5. Errori ricorrenti dai post-mortem (DATI qualitativi; il "70% sotto 1k$ MRR" NON è tracciabile a uno studio; BigIdeasDB: su 3.787 startup con revenue, mediana 145$ MRR)

1. Nessuna distribuzione pianificata prima del build ("ho ignorato il marketing, pensavo fosse per altri": 11$ in un anno).
2. Problema non sentito in prima persona, validato solo con ricerche/AI.
3. Troppi canali insieme (7 → ridotti a 2-3 per funzionare).
4. Insistere su UX/onboarding invece di verificare la domanda.
5. Bug di billing (utenti cancellati che mantengono Pro) scambiati per "nessuna domanda".
6. Launch-day spike (PH/HN) scambiato per trazione: 90% dei signup non torna.

## Strategia consigliata in 3 fasi (budget ~0)

**Fase 1 — primi 10 (settimane 1-6), manuale.** Massimiliano: 15-20 messaggi/settimana a persone già interessate (LinkedIn, comunità, rete), 10-15 telefonate di scoperta, risposte su Reddit/forum verticali (account da maturare *ora*). Claude: elenco quotidiano di thread con intento d'acquisto, bozze di risposte, landing con prova con carta, onboarding, metriche funnel per 1.000 visitatori.
**Fase 2 — da 10 a 50 (mesi 2-5), un marketplace + un canale.** Scegliere *un* marketplace dove il problema è cercato (WordPress/Shopify/Atlassian Forge, tutti a 0%) e *un* canale di contenuti (Threads/X o YouTube su query specifiche). Claude: listing, screenshot, docs, 5-10 pagine "X alternative"/comparazione, risposte supporto, raccolta recensioni. Massimiliano: chiede recensioni e referral a ogni cliente (referral CAC ~150$ è il più basso), post settimanali in prima persona.
**Fase 3 — da 50 a 100 (mesi 5-10), compounding.** Test Google Ads 100-300 €/mese solo su 3-5 keyword exact "competitor alternative"; SEO programmatica solo se la fase 2 mostra query ripetute; affiliati solo con 50+ clienti e churn noto. Claude: pagine SEO, A/B trial con/senza carta, report CAC per canale. Massimiliano: le telefonate di churn e upgrade.

**Ipotesi chiave:** i primi 10 clienti decidono tutto; qualunque canale scalabile prima di quelli è spreco (coerente con 326 progetti e con i post-mortem).

**Fonti principali:** [SaaSRanger 326 progetti](https://saasranger.com/blog/how-to-get-your-first-micro-saas-customers-6-channels-that-actually-worked/) · [IH Reddit 3 founder](https://www.indiehackers.com/post/3-founders-who-found-100-customers-on-reddit-real-numbers-real-stories-534dd26fec) · [IH 60 clienti Reddit](https://www.indiehackers.com/post/how-i-got-my-first-60-customers-from-reddit-without-spending-a-dime-on-ads-3d19b2c47c) · [IH Threads 0→100](https://www.indiehackers.com/post/from-0-to-100-paying-users-the-exact-threads-content-strategy-i-used-to-launch-my-saas-e4c127ff30) · [PH forum conversioni](https://www.producthunt.com/p/general/what-s-your-real-conversion-outcome-from-a-product-hunt-launch) · [Kirro trial benchmark](https://kirro.io/free-trial-conversion-rate) · [Userpilot](https://userpilot.com/blog/saas-average-conversion-rate/) · [UnbuiltLab CAC](https://unbuiltlab.com/learn/benchmarks/saas-cac-benchmarks) · [Optifai CAC](https://optif.ai/learn/questions/cac-by-channel/) · [Shopify rev share](https://shopify.dev/docs/apps/launch/distribution/revenue-share) · [BetaKit Shopify lifetime](https://betakit.com/shopify-app-developers-will-no-longer-be-exempt-from-sharing-their-first-1-million-usd-in-revenue-every-year/) · [Atlassian 2026](https://www.atlassian.com/blog/development/updates-to-marketplace-revenue-share-2026) · [Freemius pricing 2025](https://freemius.com/blog/new-freemius-pricing-2025/) · [HubSpot install cap](https://developers.hubspot.com/changelog/new-marketplace-distribution-app-install-limits) · [Chrome paid ext. removed](https://www.neowin.net/news/google-is-permanently-removing-paid-extensions-from-the-chrome-web-store/) · [Zapier Partner Program](https://docs.zapier.com/integrations/publish/partner-program) · [Notion gallery](https://developers.notion.com/docs/publishing-integrations-to-notions-integration-gallery) · [Rewardful affiliati](https://rewardful.com/articles/state-of-saas-affiliate-programs-report) · [Dupple newsletter CPM](https://dupple.com/learn/newsletter-advertising-cost-2026) · [SaaSHero competitor ads](https://saashero.net/google-ppc/how-to-run-profitable-google-ads-competitor-campaigns-for-saas/) · [Post-mortem patterns](https://shubhq.com/saas/research/saas-failure-postmortem/) · [IH 4 lessons failing](https://www.indiehackers.com/post/4-lessons-learned-trying-and-failing-to-build-a-saas-startup-946d64b833) · [IH HN zero signups](https://www.indiehackers.com/post/i-built-a-saas-in-9-days-for-200-launched-on-hn-to-zero-signups-heres-what-actually-happened-87c39638c6) · [BigIdeasDB mediana MRR](https://bigideasdb.com/first-1k-mrr-micro-saas-side-project) · [AdsX Shopify first 100](https://adsx.com/blog/shopify-app-marketing-first-100-installs) · [IH WP Umbrella 2025](https://www.indiehackers.com/post/what-2025-taught-me-about-growing-a-bootstrapped-saas-to-110k-mrr-wp-umbrella-8cd8c4bc1d)