# Marketplace software per un solista con AI: analisi ottobre 2026

## Premessa
Ho verificato i dati con ricerche web. Le pagine apps.shopify.com, storeleads e letsmetrix sono bloccate dal proxy, quindi i numeri delle schede arrivano da snippet di ricerca e da aggregatori. Vanno ricontrollati a mano.

## Costi delle piattaforme (DATI VERIFICATI)
- **Shopify**: 0% di commissione sul primo milione di dollari incassato in tutta la vita dell'account (contato dal 1/1/2025). Sopra il milione la commissione è del 15%. A parte c'è un 2,9% di costo di elaborazione dei pagamenti e una registrazione una tantum di 19 $ ([shopify.dev](https://shopify.dev/docs/apps/launch/distribution/revenue-share)).
- **WooCommerce.com Marketplace**: allo sviluppatore va il 70% del netto ([businessbloomer](https://www.businessbloomer.com/would-i-launch-on-the-woocommerce-marketplace-today/)). Su WordPress.org il plugin gratuito si pubblica senza commissioni, ma la versione Pro va venduta con un proprio sistema di pagamento.
- **Gumroad**: 10% + 0,50 $, più i costi carta. Sale al 30% se la vendita arriva dalla vetrina Discover.
- **Etsy**: 6,5% sulla vendita, 3% + 0,25 $ di pagamento, 0,20 $ per inserzione. Le Offsite Ads costano dal 12 al 15% ([checkoutpage](https://checkoutpage.com/blog/etsy-fees)).
- **Framer**: 0% di commissione, più il 50% sugli abbonamenti dei clienti che arrivano dai template ([framer.com](https://www.framer.com/help/articles/how-the-creator-program-works/)).
- **Notion**: circa 10% secondo varie guide, dato non confermato.
- **Chrome Web Store**: non gestisce pagamenti, bisogna usare Stripe o simili. Secondo un'analisi su 112 estensioni, il 57% non guadagna nulla e solo il 6,3% supera 1.000 $ al mese ([konabayev](https://konabayev.com/blog/extension-monetization-statistics-2026/)).

## Dimensione del mercato italiano (VERIFICATO, stime di terzi)
- Negozi Shopify in Italia: tra 43.000 (StoreCensus, agosto 2026) e 55.300 (StoreLeads, maggio 2026), con crescita del 12% annuo.
- Negozi WooCommerce in Italia: circa 76.700 (StoreCensus, settembre 2026).

## Le opportunità

**1. App Shopify per fatturazione e corrispettivi italiani**
- **Dati verificati**:
  - Fatture Italia (Blhack): circa 19-20 recensioni, voto 4,1, prezzi da 6 a 50 $ al mese. Sul proprio sito dichiara "600+ merchant attivi", ma è un dato non verificato ([app](https://apps.shopify.com/fatture-italia)).
  - GetSync per Fatture in Cloud: 20-21 recensioni, da 12,50 a 59,50 $ al mese, "oltre 100 installazioni" dichiarate.
  - Fatturify (Nextools): 25 recensioni.
  - FatturaPRO: 6 recensioni, 490 $ l'anno.
  - Le app che raccolgono solo i dati al checkout (codice fiscale, PEC, codice SDI) hanno 0 recensioni.
- **Ipotesi**:
  - Il leader incassa forse 9-15.000 $ al mese (600 merchant per 15-25 $ di media). È il tetto della nicchia dopo anni di lavoro.
  - Un nuovo arrivato dovrebbe prendersi 250-350 clienti paganti per arrivare a 5.000 € al mese. È circa metà del leader, in 18 mesi.
- **Assistenza**: alta. Gli scarti dello SDI, i commercialisti e i casi IVA particolari (OSS, reverse charge) generano ticket in proporzione ai clienti.
- **Rischi**: responsabilità per errori fiscali, cambi delle specifiche dell'Agenzia delle Entrate (la v1.9.1 è in vigore da maggio 2026), cambi delle API Shopify.

**2. App Shopify per obblighi UE (Omnibus, GPSR, dichiarazione di accessibilità EAA, cookie)**
- **Dati verificati**:
  - Cookie: Pandectes ha 2.075 recensioni, Consentmo circa 1.870. Il piano gratuito c'è, i piani a pagamento vanno da 9 a 59 $ al mese.
  - Omnibus: la migliore ha circa 48 recensioni (da 14,90 $ al mese). Le altre 5-6 ne hanno 0.
  - GPSR: circa 10 app, tutte con 0 recensioni, da gratuite a 49 $ al mese ([meetanshi](https://meetanshi.com/blog/eu-gpsr-apps-shopify/)).
  - Accessibilità: AccessEz 64 recensioni, Accessibly 23.
- **Ipotesi**: per i cookie la domanda c'è ma il mercato è saturo. GPSR e Omnibus sono già invasi da cloni (molti probabilmente fatti con l'AI) senza trazione: la domanda pagante non è dimostrata.
- **Assistenza**: bassa o media.
- **Rischio**: Shopify può aggiungere la funzione direttamente nella piattaforma.

**3. Fatturazione elettronica in altri paesi UE (Peppol in Belgio, KSeF in Polonia, Francia dal 2026-27)**
- **Dati verificati**: è già presidiata da Sufio, POP e Commbilling (419 recensioni) ([sufio](https://sufio.com/news/einvoicing-peppol-belgium-shopify/)).
- **Ipotesi**: il mercato è più grande di quello italiano, ma richiede conoscenza fiscale di più paesi e molta assistenza. Per un solista non è adatto.

**4. Plugin WordPress gratuito con versione Pro per WooCommerce italiano**
- **Dati verificati**:
  - PDF Invoices Italian Add-on: circa 5.000 installazioni.
  - WFatture (Fatture in Cloud): 700-800 installazioni.
  - Easy Fattura Elettronica: 100-200 installazioni.
  - iubenda (cookie): oltre 100.000 installazioni, ma è un'azienda grande, non un solista.
  - Complianz Pro: da 59 $ l'anno.
- **Ipotesi**: se l'1-3% passa alla Pro, 5.000 installazioni danno 50-150 clienti a 50-80 € l'anno, cioè 200-1.000 € al mese. Non si arriva a 5.000.

**5. Template Framer e Notion (mercato globale, non italiano)**
- **Dati verificati**: prezzi tipici 19-79 $. Un caso documentato: 20.000 $ in 6 mesi con 2 template (2024, singolo caso).
- **Ipotesi**: per 5.000 € al mese servono circa 100 vendite al mese a 50 $. Il design richiede comunque gusto umano. Possibile ma incerto.

**6. Template B2B per Etsy e Gumroad in italiano**
- Nessun dato di domanda trovato.
- Il pubblico italiano su Etsy è piccolo. Gumroad senza traffico esterno vende poco.

**7. Estensioni Chrome e add-on Google Workspace**
- Nessun pagamento integrato, poca scoperta dal marketplace, nessun vantaggio specifico per l'Italia. Da scartare.

## Probabilità di base (DATO, ma vecchio)
Sulle app Shopify (analisi del 2021 su 2.265 sviluppatori): ricavo mediano di un'app 725 $ al mese, il 54,5% degli sviluppatori sotto 1.000 $ al mese, solo il 17,6% sopra 10.000 $ ([spur-i-t](https://spur-i-t.com/blog/shopify-app-store-analysis-2021/)).

## Classifica

| # | Opportunità | Domanda provata | 5k€ senza ore proporzionali | Clienti dal marketplace | Fatta in gran parte dall'AI |
|---|---|---|---|---|---|
| 1 | App Shopify fiscale IT | Sì, ma con un tetto basso | No (assistenza) | Sì | Sì |
| 2 | Template Framer | Parziale | Sì | Sì | Parziale |
| 3 | App Shopify obblighi UE | Solo cookie (saturo) | Sì | Debole | Sì |
| 4 | WordPress freemium IT | Sì (installazioni) | No (conversione) | Sì | Sì |
| 5 | Etsy / Gumroad / Notion IT | No | – | Debole | Sì |
| 6 | Chrome / Workspace | No | – | No | Sì |

## Verdetto
**Nessuna opportunità passa tutti e 4 i criteri con prove.**

Il limite delle nicchie solo italiane è strutturale. Il leader di quella più promettente, le app fiscali Shopify, sta probabilmente intorno ai 10.000 $ al mese dopo anni. Per raggiungere i 5.000 € servirebbe prendersi metà del suo mercato in 18 mesi, e l'assistenza fiscale cresce con il numero di clienti.

Le nicchie UE più semplici da costruire sono già piene di cloni con 0 recensioni.

Se Massimiliano vuole comunque provarci, l'opzione meno debole è la n. 1, ma con regole precise:
- **Proposta**: un'app che fa bene una cosa sola che i concorrenti fanno male (le recensioni a 1 stella del leader sono il 15%), a 15-29 $ al mese.
- **Criterio di stop**: meno di 30 installazioni e meno di 10 clienti paganti dopo 90 giorni.
- **Aspettativa realistica**: 1.000-3.000 € al mese a 18 mesi. Non 5.000.

Prima di partire va chiarito con il commercialista come trattare in regime forfettario i pagamenti in USD che arrivano da Shopify International (Irlanda).