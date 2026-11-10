# Verifica indipendente: misura del filtro aria della caldaia dal numero di modello (USA), 10/11/2026

Idea verificata: n. 1 di `fronti-2026-11-07-classifiche-reti.md` (voto 6; 900 / 4.500 / 17.000 €/anno), terza nella coda di `DA-PUBBLICARE.md`. Condizioni poste per riaprirla: **(a)** i manuali dei produttori danno la regola modello → misura; **(b)** Filterbuy (30 $ a cliente) accetta un affiliato italiano.

Tutto letto con curl il 10/11/2026 (più la ricerca web solo per trovare gli indirizzi dei PDF ufficiali). Nessun blocco aggirato: dove un sito ha risposto con una verifica anti-robot ci siamo fermati e lo scriviamo.

## 0. Verdetto in breve

**NO-GO come terzo della coda e come sito da 300-500 pagine. Voto corretto: 4,5 su 10** (era 6). Stima a 18 mesi: **20 / 400 / 3.500 €/anno** (prudente / centrale / ottimista; era 900 / 4.500 / 17.000). Per la regola del 10/11 (nessuna soglia, ordine per €/ora) non è scartata: **scende in fondo alla riserva costruibile in versione compatta** (~15 ore, ~27 €/ora), dopo router e soglia 1099.

Le 4 prove:

| Prova | Esito | In una riga |
|---|---|---|
| 1. Domanda vera | **SÌ** (per marca), **a metà** (per serie) | "‹marca› furnace filter size" dà 5-10 suggerimenti per 14 marche; per serie la domanda è vera solo in 11 casi su 24 (soprattutto Trane) |
| 2. Dati leggibili | **SÌ, ma rispondono a un'altra domanda** | 18 PDF ufficiali su 18 letti con la tabella dei filtri (Carrier/Bryant/ICP, Trane, Lennox, Goodman/Amana). Però la tabella dà la misura **consigliata al mobiletto della caldaia**, non il filtro che c'è in casa: i manuali stessi scrivono "filtro non fornito", "può stare altrove" |
| 3. Pagatore attivo | **A METÀ** | Amazon US 3 % confermato. **Filterbuy 30 $: non per noi** (programma per ditte USA: il modulo chiede lo Stato USA e il telefono aziendale). Trovato al suo posto Filter King su Awin: 7,5 %, ordine medio 100 $ (circa 7,5 $ a vendita, non 30) |
| 4. Nessun concorrente che lo fa meglio | **NO** | Filterbuy e Atomic Filters hanno già le pagine "filter size by model number" per marca (2026), con la regola del mobiletto, e dicono la cosa vera: "il numero di modello non decide la misura". Resta scoperto solo il dettaglio per serie con la pagina del manuale citata |

Le due condizioni di riapertura: **(a) sì a metà** (la regola c'è in tutti i manuali letti, ma è una misura consigliata e ha solo 4 larghezze); **(b) no**.

## 1. Dati: i manuali ufficiali si leggono?

### 1.1 Prova su 18 documenti ufficiali (tutti 200, testo estratto con `pdftotext`, nessuna scansione)

| Marca (gruppo) | Documento | Indirizzo | Cosa dice sul filtro |
|---|---|---|---|
| Carrier | 59SC5B, dati di prodotto | `shareddocs.com/hvac/docs/1009/Public/0C/59SC5B-08PD.pdf` | "Field Supplied Filter"; telai esterni 14,5×25, 16×25, 20×25, 24,5×24; filtri lavabili 16×25×3/4, 20×25×3/4, 24×25×3/4; oltre 1.800 CFM minimo 20×25 |
| Carrier | 59SC5B, installazione | `…/Public/06/59SC5B-04SI.pdf` | tabella per larghezza: 14-3/16" → lato 16×25×3/4, fondo 14×25×3/4; 17-1/2" → 16×25×3/4 e 16×25×3/4; poi 20×25 e 24×25 |
| Carrier | 59SC6A, installazione | `…/Public/0A/59SC6A-01SI.pdf` | stessa tabella + perdita di carico dei filtri |
| Carrier | 58SC0A, installazione | `…/Public/0C/58SC0A-05SI.pdf` | Tabella 14: 14-1/2" → lato 16×25×3/4, fondo 14×25×3/4, tipo lavabile |
| ICP (Heil, Tempstar, Comfortmaker, Day & Night) | R9MSB e 440 01 4300 04 | `shareddocs.com/hvac/docs/1011/Public/09/44001600105.pdf`, `…/0C/44001430004.pdf` | "Filter Size Information" per larghezza, lato e fondo, come Carrier |
| Trane / American Standard | S9V2-VS, guida dell'installatore 18-CE19D1-1B-EN (108 pagine) | `elibrary.tranetechnologies.com/public/residential-hvac/Literature/Installation/18-CE19D1-1B-EN_02072022.pdf` | "Filters are not factory supplied". Flusso verso l'alto: 17-1/2" → 1 da 16×25×1; 21" → 1 da 20×25×1; 24-1/2" → 1 da 24×25×1. Flusso verso il basso: 2 da 14×20×1; 2 da 16×20×1; 2 da 16×20×1 |
| Trane | guida del proprietario 32-5064 | `trane.com/content/dam/Trane/residential/downloads/manuals/32-5064-WEB01_Indoor_Units.pdf` | fondo: 17×25×1 (17-1/2"), 20×25×1 (21"), 24×25×1 (24-1/2"): **diverso dalla guida dell'installatore** per il mobiletto da 17-1/2" (17×25 contro 16×25) |
| Trane | manuale del proprietario dalla pagina S9V2 | `trane-assets-grd.s3.amazonaws.com/…/32-5083-1B-EN-Gas-Furnace.pdf` | nessuna misura: "chiedi al tuo installatore dov'è il filtro" |
| Lennox | EL296DFV e EL296DFE (schede di servizio 1126, 1247) | `lennox.com/dA/5440a706f5/1126.pdf`, `lennox.com/dA/f608317319/1247k.pdf` | 17-1/2" e 21" → 16×25×1; mobiletto filtro per flusso verso il basso: 2 da 16×20×1 |
| Lennox | ML180UH, SL280UHV, ML196UHEK (5/2026), ML180UHV | `lennox.com/dA/ecebc37664/507323e.pdf`, `…/0891b8032a/508245-01b.pdf`, `…/505848b344/508569-01.pdf`, `tech.lennoxintl.com/C03e7o14l/VIu12Ch2uV/507945-01a.pdf` | A 14-1/2" → lato 16×25×1, fondo 14×25×1; B 17-1/2" → 16×25×1 e 16×25×1; C 21" → 16×25×1 e 20×25×1; D 24-1/2" → 2 da 16×25×1 e 24×25×1 |
| Goodman / Amana | GMVC96, GMSS96, GMEC96, AMSS96, ADSH8 (schede tecniche) | `apps.goodmanmfg.com/brochures/files/5fd39c5932010SS-GMVC96.pdf` e simili | "Minimum Filter Sizes" per modello: GMVC96 0403-0804 → 1 da 16×25 (lato o fondo); 1005-1205 → 1 da 20×25 (fondo) o 2 da 16×25 (lato). Nota: "Other size filters of equal or greater dimensions may be used. Filters may also be centrally located" |

**Non letti:** York/Coleman/Luxaire (`york.com` risponde con la verifica anti-robot Incapsula: fermati; le copie trovate sono su siti di rivenditori, non ufficiali); Rheem/Ruud (nessun PDF ufficiale trovato: solo siti che ripubblicano manuali). `goodmanmfg.com/robots.txt` vieta `/docs/*`: per Goodman si usano solo i PDF di `apps.goodmanmfg.com` (nessun robots.txt).

### 1.2 Cosa vuol dire per lo strumento

- **La regola esiste ed è quasi uguale per tutti:** il numero di modello contiene la larghezza del mobiletto (Carrier "…E17…" = 17,5"; Lennox e Goodman lettera A/B/C/D; Trane lettera A-D) e il manuale dà la misura consigliata per larghezza. In pratica **4 larghezze → 6 risposte** (14×25, 16×25, 20×25, 24×25, due da 16×25, due da 16×20), spessore 3/4" o 1".
- **Ma non è "la misura del filtro di casa tua".** Tutti i manuali dicono che il filtro non è fornito, è esterno e può stare altrove (griglia di ritorno, mobiletto da 4-5"). Chi ha un mobiletto filtrante (Carrier EZ Flex, Trane Perfect Fit/QuikBox, Lennox X6670) compra un filtro che il numero della caldaia non indica.
- **Una risposta sola con 4 righe copre tutto:** un negozio o il riquadro di risposta di Google la possono dare in una tabella. Non serve un decodificatore da 300 pagine.
- **Le fonti non sempre coincidono** (Trane 17×25 contro 16×25 per lo stesso mobiletto): ogni cifra va citata con documento e pagina.
- **Elenco dei modelli:** l'API ENERGY STAR (`data.energystar.gov/resource/i97v-e8au.json`, 200, aggiornata il 10/11/2026) dà **3.879 numeri di modello** di caldaie certificate (Carrier 149, Heil/Bryant/Comfortmaker/Day & Night 139 ciascuna, Lennox 77, Payne 71, York 62, Goodman 54, Amana 51, Ruud 49). Mancano i modelli vecchi e quelli all'80 %, che sono proprio quelli cercati (Trane XR80, XE80). AHRI (`ahridirectory.org`): applicazione JavaScript con condizioni d'uso sul riuso: non usata.
- **Raccolta non automatica:** gli indirizzi dei PDF hanno codici non prevedibili (`/0C/`, `/dA/5440a706f5/`, `5fd39c5932010SS-…`) e le pagine prodotto ufficiali non li elencano nell'HTML (Carrier li carica con script, Lennox e Trane mostrano solo brochure). Vanno trovati a mano, serie per serie: realistico per 30-40 serie, non per migliaia di modelli.
- **Diritti:** le misure sono fatti; si citano con nome del documento, numero e data, senza copiare tabelle intere né disegni; link al PDF ufficiale.

**Copertura realistica della v1:** 4 gruppi (Carrier/Bryant/Payne + ICP, Trane/American Standard, Lennox, Goodman/Amana/Daikin), 30-40 serie, circa 2.000 numeri di modello riconosciuti con le regole di decodifica. Fuori: York e Rheem/Ruud.

## 2. Concorrenza: chi risponde già

| Chi | Cosa ha (letto oggi) | Giudizio |
|---|---|---|
| **Filterbuy** (il pagatore proposto) | Pagina marca con titolo "Carrier Filter Size Lookup by Model Number"; guida Goodman che nomina GMVC96, GM9S96, GMSS96 e scrive "The cabinet letter predicts filter size. A 'B' cabinet takes a 16x25 filter; a 'C' cabinet takes a 20x25 or two 16x25s"; 2.344 pagine di guide nella sitemap | Risponde per marca, onesto: "Your furnace model number doesn't determine your filter size. The filter cabinet does". Non cita il manuale. La regola Goodman è semplificata (per il manuale la 0804 con mobiletto C sta nel gruppo 16×25) |
| **Atomic Filters** (negozio con telefono) | 201 articoli; "‹marca› Furnace Filter Size by Model Number" per Carrier, Bryant, Trane (pubblicati il 6/3/2026, aggiornati a luglio 2026), Lennox, più "Air Filter Size Chart: by Brand & Model Number". Nomina 59SC5, 59TP6, 58STA, S9V2, XR95, XV95, XR80, S8X1 | Il più completo. Dice: "your Carrier furnace model number does NOT directly tell you your filter size". Dà i codici dei mobiletti filtranti con misure reali. Nessuna citazione del manuale |
| Risultati di ricerca per "goodman furnace filter size by model number", "trane xr95 furnace filter size", "lennox furnace filter size by model number lookup" | Atomic (fino a 10 risultati su 14), Filterbuy, airfilters.com, Walmart, siti che ripubblicano manuali, **pagine spam ospitate su siti altrui** (lboro.ac.uk, steelcase.com, londoncouncils.gov.uk, hss.ge) | Per marca: negozi forti. Per serie: risultati deboli e spam, quindi spazio c'è, ma con poca domanda (sez. 3) |
| PickHVAC | pagina sul filtro Goodman: "dipende dalla configurazione del ritorno, non dal modello" | conferma |
| Second Nature, FilterSnap, Discount Filters, AC Direct, strumento "fits" di Amazon | pagine provate: 404 o non trovate; Filter King 403 sul sito (letto solo su Awin) | non verificati |

Controllo sulle serie: su 26 serie cercate nei testi (59SC5, 59TP6, 58STA, 59SC6, S9V2, XR95, XV95, XR80, S8X1, EL296, ML180, ML195, ML196, SL280, G61, GMVC96, GMEC96, GM9S96, GMSS96, R96V, R801, 925, 915, TM9V, ARUF, FB4C) i due negozi ne nominano **12**; **nessuno dà la tabella del manuale con documento e pagina**; nessuno copre Lennox per serie, Rheem, York, i ventilconvettori.

**Il vuoto vero:** pagine per serie con la misura del manuale, il documento citato e l'avviso onesto. È un vuoto piccolo, e i due negozi lo possono chiudere quando vogliono (pubblicano su questo tema da marzo 2026).

## 3. Domanda

Autocomplete Google (`suggestqueries.google.com`, `gl=us`, `hl=en`), 53 ricerche: 28 con 8-10 suggerimenti, 21 con 10.

- **Per marca (domanda vera):** "furnace filter size by model number" 10 (Lennox, Goodman, Bryant, Heil, Carrier, anche "pdf" e "canada"); "‹marca› furnace filter size" 10 per Carrier, Trane, Lennox, Goodman, Rheem, Bryant; 8 per York, Payne, Ruud; 7 per American Standard e Amana; 5 per Heil; "trane filter size by model number" 10; "what size filter for my furnace" 10; "goodman air handler filter size" 10 (per tonnellate).
- **Per serie:** su 24 serie provate, solo **11** hanno la ricerca esatta tra i suggerimenti: Trane XR80, XR95, XV95 (10 ciascuna), S9V2 e XE80 (9), Carrier 59TP6 (8), FB4C (7), Lennox EL296V e Goodman GMEC96 (5), Lennox G61, Trane TEM4. Nelle altre **13** (GMVC96, GM9S96, GMSS96, 59SC5, 58STA, ML180, ML195, SL280, R96V, R801, Bryant 925 e 915, ARUF37C14) Google restituisce solo code generiche ("… chart", "… sizes", "… and weight", "… and type") senza la ricerca stessa: segno di domanda quasi nulla.

**Stima delle visite (metodo dichiarato, senza strumento di volumi: è una stima, non una misura).** Ricerche al mese sul gruppo: 14 ricerche per marca a 300-1.500 l'una (centro ~9.000) + ~40 serie vere a 30-150 l'una (~3.000) = **~12.000 al mese**, con stagione (ottobre-gennaio, giugno-agosto). Quota per un sito nuovo senza autorità, con due negozi forti sopra: 1 % / 12 % / 50 % → **150 / 1.500 / 6.000 visite al mese** a 18 mesi. Base di confronto in casa: i nostri tre siti USA a pagine generate sono a 0-21 visite a settimana dopo un mese (FloodCost 27 impressioni, ApprovedCondos posizione media 77,8), quindi lo scenario prudente è il più vicino a ciò che abbiamo visto finora.

## 4. Soldi

| Pagatore | Cifra letta oggi | Fonte | Per noi |
|---|---|---|---|
| Amazon.com Associates | **3,00 %** per "Home, Home Improvement, … Tools" (4,50 % solo Automotive) | `affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ` (200) | attivo (`beforeyoufl08-20`); confezioni da 4-6 filtri a 35-60 $ (ipotesi, non letta oggi) → **1,0-1,8 $ a vendita** |
| Filterbuy Partner Program | "$30 for each new residential customer referred, paid on the customer's first order"; pagamento con Stripe | `filterbuy.com/partner/` (200) | **No.** È il programma per installatori: "Import your customers", modulo `filterbuy.com/partner/apply/` con e-mail e **telefono aziendale** e un elenco chiuso dei 50 **Stati USA**, nessun campo Paese. Un sito italiano non rientra senza dichiarare il falso |
| Filterbuy su Impact | "fino al 25 % sui nuovi clienti, ordine medio 110 $" solo da un riassunto della ricerca web | `filterbuy.com/earn-with-filterbuy` → **404** oggi | non confermato; non contare |
| **Filter King** (Awin) | **7,5 %**, ordine medio 100 $+, cookie 30 giorni, ultimo clic | `ui.awin.com/merchant-profile/125512` (200) | ~**7,5 $ a vendita**; Awin è già la nostra rete; accettazione del nostro sito da chiedere |
| Nordic Pure (Awin) | cookie 120 giorni; 5 % (dal riassunto della ricerca, non visibile nel testo letto) | `ui.awin.com/merchant-profile/88957` (200) | riserva |
| DiscountFilterStore (Awin) | "Basic rates start at 5%", cookie 30 giorni | `ui.awin.com/merchant-profile/126373` (200) | riserva |
| AdSense | 8 € ogni 1.000 visite (ipotesi della rete per il pubblico USA casa; non leggibile da fuori) | — | 6 / 8 / 12 nei tre scenari |

Il riacquisto (ogni 1-3 mesi) va al negozio, non a noi: Amazon paga solo entro 24 ore dal clic, Filter King entro 30 giorni.

**Formula** (cambio 0,92 €/$): € ogni 1.000 visite = clic verso i negozi × (quota Amazon × conversione × carrello × 3 % + quota Filter King × conversione × 100 $ × 7,5 %) × 0,92 + pubblicità.

| Scenario | Visite/mese | Clic | Amazon | Filter King | Pubblicità | € ogni 1.000 visite | **€/anno** |
|---|---|---|---|---|---|---|---|
| Prudente | 150 | 8 % | 100 % dei clic, 6 % × 40 $ | non accettati | 6 € | 11 | **~20** |
| Centrale | 1.500 | 12 % | 60 %, 7 % × 45 $ | 40 %, 2,5 % × 100 $ | 8 € | 22,5 | **~400** |
| Ottimista | 6.000 | 18 % | 50 %, 8 % × 50 $ | 50 %, 4 % × 110 $ | 12 € | 49 | **~3.500** |

Anche con le 4.000 visite al mese della stima originale il centrale sarebbe ~1.100 €/anno: la differenza la fa il pagatore (7,5 $ o 1,4 $ a vendita invece di 30 $ a cliente).

## 5. Rischi

1. **Misura sbagliata → reso e sfiducia.** La misura del manuale è quella del telaio alla caldaia; in molte case il filtro è alla griglia o in un mobiletto da 4-5". Rimedio: mai scrivere "il tuo filtro è"; scrivere "il manuale consiglia … per il mobiletto da …", citare documento e pagina, e mettere per primo "leggi la misura stampata sul filtro che togli".
2. **Concorrenza dei negozi**: hanno il prodotto, l'autorità e pubblicano già su queste ricerche; Filterbuy ha `llms.txt` e 2.344 guide.
3. **Copertura**: York e Rheem/Ruud fuori; i modelli vecchi (i più cercati: XR80, XE80, G61) hanno manuali più difficili da trovare in copia ufficiale.
4. **Pagine generate in serie** con 6 risposte possibili: contenuto quasi uguale tra le pagine, a rischio con gli aggiornamenti di Google. Da qui la versione compatta (poche pagine dense).
5. **Amazon**: dichiarazione "As an Amazon Associate I earn from qualifying purchases" su ogni pagina con link; niente prezzi scritti a mano; link alla ricerca per misura con il tag, non a prodotti con prezzo.
6. **Risposta diretta di Google**: una tabella di 4 righe si presta al riquadro in cima ai risultati senza clic.

## 6. Dove metterla

- **Non in FloodCost né in ApprovedCondos.** Sono congelati dal 6/11 (0 visite; 27 e 89 impressioni; posizione media 69 e 77): non hanno autorità da prestare, il tema (assicurazione alluvioni, mutui FHA) non c'entra con i filtri, e la decisione del 6/11 dice "niente lavoro" finché non arrivano a 30 visite a settimana.
- **Se si costruisce: sito nuovo piccolo** su indirizzo `.netlify.app` (regola del 17/10: nessun dominio prima delle visite). Nomi .com liberi oggi (RDAP Verisign 404): `filtersizebymodel.com`, `furnacefilterlookup.com`, `hvacfiltersize.com`, `filtersizelookup.com`, `filterbymodel.com`, `whichfurnacefilter.com`. Occupati (200): `furnacefiltersize.com`, `furnacefilterfinder.com`, `whatsizefilter.com`, `myfurnacefilter.com`.

## 7. Verdetto

**NO-GO** come terzo in coda e nella forma proposta (decodificatore da 300-500 pagine, 35-45 ore, 4.500 € centrali). Motivi, in ordine di peso:

1. il pagatore da 30 $ non è accessibile, e senza di lui una vendita vale 1,4-7,5 $;
2. il dato ufficiale non risponde alla domanda dell'utente ("che filtro compro?"), e i due negozi in cima ai risultati lo dicono già apertamente;
3. la domanda per serie è vera in meno della metà dei casi.

**Voto 4,5.** Per la regola del 10/11 resta in **riserva costruibile, versione compatta: ~400 €/anno centrali, ~15 ore, ~27 €/ora** (sotto router ~90 e soglia 1099 ~80). Nessun danno per l'utente se si rispettano gli avvisi della sez. 5.

**Si riapre più in alto se:** (1) Filter King (o un altro negozio con ≥ 7 %) accetta un nostro sito e (2) uno dei tre siti USA della rete supera le 30 visite a settimana, cioè abbiamo la prova che un nostro sito USA a pagine generate viene letto da Google.

## 8. Piano della versione compatta (da usare solo quando la riserva arriva a questa riga)

**Promessa onesta:** "What your furnace's manual says about filter size, by model number — and how to check what's actually in your house."

**Pagine (~45, non 300):**
- home con il campo "incolla il numero di modello" (nel browser, senza server) → marca, serie, larghezza del mobiletto, misura consigliata dal manuale per ritorno laterale e dal fondo, documento e pagina, tre passi per controllare (misura stampata sul filtro; etichetta del mobiletto filtrante; misura della fessura arrotondata al pollice);
- 4 pagine gruppo (Carrier/Bryant/Payne/ICP, Trane/American Standard, Lennox, Goodman/Amana/Daikin) con la tabella larghezza → misura e come leggere la larghezza nel numero di modello;
- ~30 pagine serie, **prima quelle con domanda vera**: Trane XR80, XR95, XV95, S9V2, XE80, TEM4; Carrier 59TP6, 59SC5, FB4C; Lennox EL296V, G61, ML180, SL280; Goodman GMEC96, GMVC96, ventilconvettori per tonnellate;
- 4 guide: misura nominale e reale; quale MERV (con la nota dei manuali Lennox e Carrier sulla perdita di carico); dov'è il filtro; mobiletti da 4-5" e i loro codici;
- pagina "Sources and method" con l'elenco dei PDF, numero e data di ogni documento.

**Raccolta dati (`raccolta/`):**
1. `fonti.json` scritto a mano: per ogni serie indirizzo del PDF ufficiale, numero e data del documento, pagina della tabella (solo `shareddocs.com`, `elibrary.tranetechnologies.com`, `trane.com`, `lennox.com/dA`, `tech.lennoxintl.com`, `apps.goodmanmfg.com`; mai `goodmanmfg.com/docs/`, mai York);
2. `scarica.py`: curl con pausa di 2 secondi, salva il PDF e il suo SHA-256; se la risposta non è 200 o non è un PDF si ferma e segnala;
3. `estrai.py`: `pdftotext -layout`, cerca la tabella ("Filter Size", "Minimum Filter Sizes", "Filter Qty and Size") e produce `dati/serie.json` con larghezza → misura per lato e fondo; ogni riga riletta a mano una volta prima della pubblicazione;
4. `decodifica.json`: per ogni serie l'espressione regolare che estrae la larghezza dal numero di modello (Carrier: le due cifre dopo la lettera del gas, 14/17/21/24; Lennox, Goodman, Trane: lettera A/B/C/D);
5. elenco dei modelli da ENERGY STAR (`i97v-e8au`) per provare la decodifica su numeri veri.

**`verifica.py` (blocca la pubblicazione se fallisce):**
- vettori di prova dai manuali letti oggi:
  - Lennox ML180UH (507323-01, 7/2018): A → lato 16×25×1, fondo 14×25×1; B → 16×25×1 e 16×25×1; C → 16×25×1 e 20×25×1; D → 2 da 16×25×1 e 24×25×1;
  - Lennox ML196UHEK (508569-01, 5/2026): 17-1/2" → 16×25×1 e 16×25×1; 21" → 16×25×1 e 20×25×1;
  - Trane S9V2-VS (18-CE19D1-1B-EN): flusso verso l'alto 17-1/2" → 1 da 16×25×1; 21" → 1 da 20×25×1; 24-1/2" → 1 da 24×25×1; verso il basso 17-1/2" → 2 da 14×20×1; 21" e 24-1/2" → 2 da 16×20×1;
  - Carrier 59SC5B (59SC5B-04SI): 14-3/16" → lato 16×25×3/4, fondo 14×25×3/4; 17-1/2" → 16×25×3/4 e 16×25×3/4;
  - Carrier 58SC0A (58SC0A-05SI, Tabella 14): 14-1/2" → lato 16×25×3/4, fondo 14×25×3/4;
  - Goodman GMVC96 (SS-GMVC96, 12/20): `GMVC960603BN` e `GMVC960804CN` → 1 da 16×25; `GMVC961005CN` e `GMVC961205DN` → 1 da 20×25 dal fondo o 2 da 16×25 dal lato;
  - decodifica: `59SC6A080M17--16` → 17,5"; `59SC6A100M21--22` → 21"; `S9V2B080U4…` → B = 17,5" (corrispondenza lettera-larghezza di Trane da confermare sulla tabella delle dimensioni del manuale prima di pubblicare); un numero inventato → "modello non riconosciuto", mai una misura;
- ogni misura in pagina ha documento, data e link; nessuna pagina contiene "your filter is" o "exact size" senza "recommended by the manual";
- ogni pagina con link a un negozio ha la dichiarazione Amazon e `rel="sponsored nofollow"`; nessun prezzo scritto a mano;
- dove due documenti ufficiali non coincidono (Trane 17×25 e 16×25) la pagina mostra tutti e due con la fonte;
- niente York né Rheem finché non c'è una fonte ufficiale leggibile; link interni senza 404; sitemap completa.

**Guadagno in pagina:** sotto la risposta due pulsanti per la misura trovata: "See 16x25x1 filters on Amazon" (ricerca Amazon per misura con `tag=beforeyoufl08-20`) e, dopo l'accettazione, Filter King (link Awin alla misura); riquadro MERV 8 / 11 / 13 con gli stessi link; AdSense sotto la tabella e a fine pagina, mai sopra la risposta. Dichiarazione in fondo a ogni pagina e nella pagina "Sources and method": "As an Amazon Associate I earn from qualifying purchases. We may also earn a commission from other filter retailers. Sizes come from the manufacturers' manuals cited on each page; always check the size printed on your current filter before ordering."

**Ore:** agenti ~15 (raccolta di 30 PDF 5, estrazione e controlli 4, pagine e strumento 4, revisione 2). Passi del titolare: creare il sito su Netlify; chiedere Filter King su Awin (10 minuti), solo a sito online.
