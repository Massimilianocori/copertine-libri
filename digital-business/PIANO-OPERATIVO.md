# Piano operativo — nuovo business di prodotti digitali

Documento fondativo. Stile e regole ereditate dal protocollo di lavoro dell'utente
(Massimiliano Cori): ogni numero o direzione è marcato **[VERIFICATO]** (con fonte) o
**[IPOTESI]** (inferenza non testata). Niente riempimento. Si cambia solo ciò che si decide
esplicitamente. Business e fatturato prima della coerenza estetica.

Data di stesura: 2026-09-11. Aggiornare questo documento a ogni verifica sul campo.

---

## 0. Perché questo business esiste (la lezione da PressedHeart)

`[VERIFICATO — skill pressedheart §9]` PressedHeart: 9 vendite totali con ~70 listing e una
pipeline di produzione eccellente, in circa un anno. Il collo di bottiglia **non è mai stato la
produzione** — è stato: (a) produrre prima di validare la domanda, (b) dipendere dalla ricerca
Etsy senza leva di traffico propria, (c) nessun canale di traffico di proprietà, nessuna mailing
list.

**Principio fondativo (inverte l'ordine di PressedHeart):**

> Domanda → Canale di traffico → Offerta → Storefront → (solo dopo) Ads.

Mai produrre il catalogo completo prima di aver dimostrato che qualcuno paga.

---

## 1. La nicchia (decisa su dati, 2026-09-11)

**Agenti immobiliari solo, mercato in lingua inglese (US-centrico).**

Motivazione dai dati dello sprint di selezione:

- `[VERIFICATO]` Nel 2026 l'immobiliare è di fatto un business di contenuti: i clienti scelgono
  l'agente dalle performance su TikTok/Reels/YouTube. Domanda strutturale e crescente.
- `[VERIFICATO]` Compratore con soldi e cronicamente senza tempo, che deve produrre contenuti in
  continuazione.
- `[VERIFICATO]` L'offerta esistente è dominata da **template Canva statici** (Agent Crate ~25k
  agenti, Coffee & Contracts, Photofy). Prodotti profession-specific hanno 3–7× la densità di
  domanda rispetto ai generici.
- `[IPOTESI da confermare sul campo]` Il bisogno si è spostato sul **video**, dove i venditori
  esistenti sono deboli e dove il vantaggio produttivo dell'utente (Higgsfield + Midjourney) è
  più forte. Questa è l'ipotesi che i primi 15–20 video valideranno con l'engagement.

**Onestà — non è un campo vuoto:** Agent Crate è ben finanziato. Il cuneo NON è battere il volume
di template, è il gap video-AI.

Scartate e perché: coach/consulenti (mercato saturo su entrambi i lati); venditori Etsy/POD
(offerta erosa da tool gratuiti — Mockey free, Nano Banana 2; inoltre claim di credibilità
rischiose con 9 vendite lifetime); salon/beauty (guerra di prezzo su bundle da 600–1000 template);
vendor matrimoni (buon budget ma speso in SaaS/CRM, non in file singoli) — tenuto come runner-up.

---

## 2. Il prodotto-bandiera v1

**"Listing → Reel System"** (nome di lavoro, da confermare col brand).

Un sistema che permette a un agente di trasformare qualunque annuncio in video short-form pronti,
in fretta. Contenuto:

1. Libreria di script/format short-form per immobiliare, struttura Hook → Problema → Demo → Prova
   → CTA `[VERIFICATO — struttura che converte, fonte funnel 2026]`.
2. Prompt-pack Midjourney/Higgsfield per generare b-roll, visual e thumbnail.
3. Workflow documentato Higgsfield / editing (es. CapCut).
4. Calendario contenuti 30 giorni.

**Prezzo `[IPOTESI, allineato ai dati earnings di nicchia]`:**
- One-time: **€39–59**.
- Upsell ricorrente "content drop mensile": **€19–29/mese** (modello Agent Crate, ma AI-video-native).

**Lead magnet gratuito:** "3 Reel di annuncio pronti + la formula degli hook" → cattura email.

Non costruire il catalogo completo prima che la v1 converta.

---

## 3. Stack deciso

- **Storefront: Lemon Squeezy.** `[VERIFICATO]` Merchant of Record vero: incassa lui, raccoglie e
  versa l'IVA UE automaticamente — niente registrazione OSS/MOSS, niente dichiarazioni trimestrali
  a carico dell'utente. Fee ~5% + $0,50/transazione.
  - Gumroad scartato: dal 2025 è MoR ma nel 2026 non gestisce l'IVA UE per la maggior parte dei
    creator.
  - Payhip scartato: gestisce l'IVA UE ma non è MoR (più admin).
- **Landing page: custom** nel repo, deploy Netlify/Vercel (già in uso). Serve il funnel e la
  cattura email; il checkout/consegna file resta su Lemon Squeezy.
- **Canale primario: video short-form faceless.** `[VERIFICATO]` Voiceover + b-roll + screen
  recording + testo; niente faccia obbligatoria. Struttura Hook → Problema → Demo → Prova → CTA.
- **Canale secondario: Pinterest** (competenza già acquisita dall'utente).
- **Email:** asset centrale. `[VERIFICATO]` Chi costruisce una lista guadagna 40–60% in più e ha
  3–5× ricavo per follower rispetto a chi resta solo sulla piattaforma.
- **Motore creativo: Higgsfield.** `[VERIFICATO]` Marketing Studio (URL-to-video "Click to Ad"),
  hook generator, UGC factory, 100 varianti di ad programmatiche per A/B test. Usato per produrre
  in massa creativi organici e a pagamento — solo dopo che l'offerta converte.

---

## 4. Funnel

Video short-form → lead magnet gratuito → **email** → prodotto a pagamento → upsell (content drop
mensile) / bundle. TikTok/Reels guadagnano il click; la pagina propria chiude la vendita.

---

## 5. Budget e tempo

- **Budget:** mesi 1–2 ~50–100 €/mese (solo tool, zero ads). Dal mese 3, se l'offerta converte,
  100–300 €/mese di test ads con creativi Higgsfield. Mai ads su un funnel non validato.
- **Tempo:** target 10–15 h/settimana. È il minimo onesto perché il piano 90 giorni regga.

---

## 6. Numeri realistici (niente hype)

`[VERIFICATO — dati earnings creator di nicchia 2026]` Principianti 100–500 € nei primi mesi;
creator di nicchia consolidati 300–3.000 €/mese; top oltre 15k. **Obiettivo onesto a 12 mesi:
costruire verso 1–3k €/mese ricorrenti.** La velocità viene dall'eliminare in fretta i perdenti,
non dal produrre in fretta.

Timeline `[IPOTESI]`: mesi 1–2 validazione (fatturato ~0, voluto); mesi 3–6 prime vendite
consistenti se l'offerta è validata; mesi 6–12 scaling di un funnel che funziona.

---

## 7. Piano 90 giorni

- **Sett. 1–2:** confermare la nicchia con l'engagement dei primi contenuti; setup Lemon Squeezy +
  landing page + tool email; definire il prodotto-bandiera v1.
- **Sett. 3–4:** build v1 del prodotto + lead magnet; primi 10–20 video faceless
  (Hook→Problema→Demo→Prova→CTA).
- **Sett. 5–8:** traffico video → email → offerta; misurare la conversione. Se converte →
  varianti ad Higgsfield + micro-test 100–300 €/mese. Se non converte → cambiare offerta, non
  aumentare la produzione.
- **Sett. 9–12:** raddoppiare sui vincitori; prodotto #2 solo su domanda dimostrata; coltivare la
  lista email.

---

## 8. Cosa NON fare (guard-rail)

- Non produrre il catalogo completo prima che la v1 converta.
- Non attivare le ads su un funnel non validato.
- Non competere sul volume di template statici contro incumbent finanziati: il cuneo è il video-AI.
- Non presentare un'ipotesi come dato verificato.
- Non fare claim di "successo" non supportate dai propri numeri.
- Non aprire un secondo prodotto senza dati di domanda reali sul primo.

---

## 9. Fonti (sprint 2026-09-11)

- Payhip — 35 underserved digital product niches 2026:
  https://payhip.com/mjresell/blog/news/35-underserved-digital-product-niches-to-profit-from-in-2026
- Kupkaike — Notion template income data 2026:
  https://kupkaike.com/blog/notion-templates-passive-income-how-much-can-you-earn
- InsightRaider — profitable niches (152K products analyzed):
  https://insightraider.com/blog/profitable-niches-2026
- We Are Founders — Gumroad vs Payhip vs Lemon Squeezy 2026:
  https://www.wearefounders.uk/best-platforms-for-selling-digital-products-in-2026/
- Higgsfield features 2026:
  https://www.conceptbeans.com/complete-guide-higgsfield-features-pricing-tutorial-2026/
- Graphaize — short video funnel 2026:
  https://graphaize.com/short-video-marketing-funnel-full-funnel-marketing-2026/
- The Close / Coffee & Contracts / Photofy / Agent Crate — mercato template immobiliari (offerta).
