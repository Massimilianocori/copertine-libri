# Outreach v2 — meno email, solo decisori verificati

2026-09-30. Richiesta diretta di Massimiliano: le email inviate non vengono aperte, la maggior parte
andava a caselle generiche (press@, info@), il tono era da elemosina. Serve trovare poche persone
che possono davvero dare lavoro, con un tono professionale (chi siamo, cosa facciamo, free sample).

---

## 1. Diagnosi

1. **Consegna**: Namecheap Private Email rifiuta l'invio oltre ~20 messaggi/ora
   (`554 5.7.1 Data command rejected: too many messages from sender in last 60 minutes`, in Gmail
   "CustomFromDenied"). 19 email non sono mai state consegnate. Un indirizzo (SuperGreen Tonik)
   aveva un vero hard bounce 550 5.1.1. L'invio in raffica dal tasto Gmail è la causa.
2. **Destinatari**: molte bozze andavano a info@/press@/hello@ — caselle che nessun decisore legge.
   Cancellate 42 bozze di questo tipo.
3. **Indirizzi non verificati**: dei 48 contatti nominali controllati, solo 2 hanno un indirizzo
   visto in una fonte pubblica (priscilla@cocokind.com, cb@noodleandboo.com). Gli altri 33 sono stati
   cancellati dalle bozze. Due (james@organicmuscle.com, bud@warlordbeardoil.com) restano in bozza in
   attesa di un controllo manuale sul sito.
4. **Testo**: adulazione + "happy to build a free sample if useful" = tono da supplica. Sostituito.
5. **Metrica sbagliata**: il tasso di apertura non è affidabile (Apple MPP, nessun pixel nei testi
   semplici). Contano risposte e bounce.

## 2. Standard di evidenza per un indirizzo email

- **Livello A**: indirizzo esatto visto in chiaro in una fonte pubblica (sito, press kit, comunicato,
  pagina privacy, annuncio di lavoro, pagina ospite podcast).
- **Livello B**: pattern aziendale confermato da ≥2 fonti indipendenti che mostrano indirizzi reali di
  altri dipendenti + persona confermata in azienda.
- **Da un tool con verifica (Apollo/Vibe Prospecting)**: indirizzo con stato "verified".
- **Scartati sempre**: info@, hello@, press@, support@, sales@, contact@, team@, marketing@,
  partnerships@, care@ e simili. Indirizzi "mascherati" (j***@) o dedotti da aggregatori non contano.

## 3. Target (ICP)

- Brand/app/agenzie con spesa paid social (fatturato ~$1M–$50M, team ~5–150 persone).
- Decisore: founder/CEO nei brand piccoli; Head of Growth/Performance/Creative/E-commerce/CMO nei
  più grandi; nelle agenzie founder o head of creative/paid social.
- Segnali d'acquisto: annunci Meta/TikTok attivi, assunzioni in ambito ads/creative strategy,
  TikTok Shop, lanci frequenti. Mercati: US/UK/CA/AU.
- Settori: salute/benessere/fitness, beauty/moda/pet/baby, app consumer e abbonamenti, agenzie
  (white-label), casa/lifestyle/food/outdoor.
- Segnale trovato: Jones Road Beauty assume un Paid Social Creative Strategist (SVP Marketing:
  Kirsten Walpert) — ottimo target, ma indirizzo ancora da verificare.

## 4. Template (professionale, niente adulazione)

```
Subject: Short-form video ads for {Company}

Hi {First},

I'm Massimiliano Cori, founder of Scrollcraft. We produce short-form video ads (UGC-style, 9:16)
for e-commerce brands using AI, so there are no shoots or creators to coordinate: concepts, hooks
and variations are delivered within days and formatted for Meta, TikTok and Reels.

{una riga fattuale di pertinenza}

Examples of our work:
www.scrollcraft.design{ANCHOR}

If this is relevant to {Company}, we're glad to produce a free sample ad on one of your products so
you can judge the quality before any commitment. Just reply with the product you'd like to see.

Best regards,
Massimiliano Cori
Founder, Scrollcraft
hello@scrollcraft.design · www.scrollcraft.design
```

Variante agenzie: capacità white-label / subappalto al posto del free sample sul prodotto.

## 5. Regole di invio

- Mai più di ~10 email/ora e ~20/giorno, distanziate; mai raffiche dal tasto Gmail.
- Follow-up unico dopo ~4 giorni (una riga), secondo dopo ~9 giorni, poi stop.
- Se cresce il volume: dominio/casella separati per il cold outreach (vedi `16-strategia-volume-outreach.md`).
- KPI: risposte, bounce, free sample accettati — non aperture.

## 6. Come ottenere indirizzi verificati (blocco attuale)

Da questo ambiente: WebFetch bloccato dal proxy, WebSearch solo a riassunti e limitato a 200
ricerche per agente. Quindi non si possono verificare email. Soluzioni, in ordine di efficacia:

1. Collegare **Apollo.io** (già installato, disconnesso) e abilitarlo in questa chat: ricerca
   persone + enrichment con stato "verified".
2. In alternativa **Vibe Prospecting** (installato, disconnesso).
3. Controllo manuale di Massimiliano con l'estensione Chrome di Apollo sui nomi candidati.
4. Percorso **LinkedIn-first** per chi non ha un indirizzo verificato (vedi `20-strategia-acquisizione-clienti.md`).

## 7. Candidati da verificare (azienda adatta, email non ancora confermata)

Organic Muscle (James Benefico), Warlord (Bud Hadley), Brickell (Josh Meyer), NULASTIN (Leah Garcia),
Pawstruck (Kyle Goguen), Dog Is Human (Tim Chen), Cure Hydration (Lauren Picasso), Fable & Mane
(Akash Mehta), Jones Road Beauty (Kirsten Walpert), LYS Beauty (Tisha Thompson), Bounce Curl
(Merian Odesho), Three Ships (Connie Lo), Bite (Lindsay McCormick), Bearaby (Kathrin Hamm),
WhyGolf (assume DTC creative strategist), Insight Timer, agenzie Y'all (Travis Halff), Hustler
Marketing, Linear Agency Group.
