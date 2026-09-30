# Passaggio di consegne — outreach Scrollcraft (2026-09-30)

Da leggere insieme a `22-outreach-v2.md`. Serve a una nuova sessione per riprendere senza perdere contesto.

## Chi è l'utente e come lavorare con lui
- Massimiliano Cori, italiano, fondatore solo di **Scrollcraft** (video ad UGC generati con AI per brand DTC). Rispondere **sempre in italiano**, breve, passo per passo: non è tecnico e vuole essere guidato.
- **Mai inviare email.** Solo bozze Gmail. Invio solo con un suo via libera esplicito nel momento. Ha detto: "prima di fare qualcosa ricordati di chiedere".
- **Mai spendere crediti** (Vibe, Apollo) senza dirgli prima il costo e avere il suo ok.
- Mittente: `hello@scrollcraft.design` (alias Gmail via Namecheap Private Email).
- Sito/portfolio: www.scrollcraft.design, con ancore #skincare, #mens-grooming, #pet-supplements, #fragrance.

## Cosa è successo e perché
- Le email inviate non venivano aperte. Cause trovate: (1) Namecheap blocca oltre ~20 invii/ora ("554 5.7.1 too many messages from sender in last 60 minutes", in Gmail "CustomFromDenied"), 19 email mai consegnate; (2) molti destinatari erano caselle generiche (info@, press@); (3) testo con adulazione e tono da supplica.
- Sua richiesta: **20 email di persone che possono dare lavoro**, non caselle generiche; anche meno di 20 se non affidabili; settori ampi; lavoro organizzato da marketer professionista; testo professionale (chi siamo, cosa facciamo, free sample se interessati), niente elemosina né finto interesse.
- Fatto finora: cancellate 42 bozze con caselle generiche e 33 con indirizzo non verificato. Restano 4 bozze riscritte con il nuovo testo:
  - `priscilla@cocokind.com` (Livello A, da un blog del 2016, potrebbe essere vecchio)
  - `cb@noodleandboo.com` (Livello A, da un atto 2023)
  - `james@organicmuscle.com` e `bud@warlordbeardoil.com`: indirizzo letto solo in riassunti di ricerca, **da far controllare a lui sul sito** (pagina wholesale / pagina privacy).
- Ricerca dalla vecchia sessione: WebFetch bloccato dal proxy e WebSearch solo a riassunti con tetto di 200 ricerche, quindi non si poteva verificare nessuna email. Per questo si usano Apollo/Vibe.

## Stato strumenti
- **Apollo**: piano Free. `apollo_mixed_people_api_search` è **bloccata** (API_INACCESSIBLE). 182 crediti lead rimasti. Utile solo per arricchire/verificare un nome già noto (`apollo_people_match`).
- **Vibe Prospecting**: `fetch-entities` funziona (entity_type "prospects"), il campione costa circa 1 credito a riga. Test fatto: 700 decisori corrispondenti. I filtri erano troppo larghi (uscivano B2B come Tiny Health e Journey e ruoli non adatti): restringere a founder/CEO dei brand piccoli e head of growth/performance/creative dei più grandi. Il saldo crediti di Vibe è **ignoto**: chiederglielo.
- Gmail: `update_draft` con `draftId`, `to` come array, `subject`, `body`; `delete_draft` con `draftId`. Paginare sempre `list_drafts` (50 per pagina).

## Regole di evidenza e di invio
Vedi `22-outreach-v2.md` §2, §4, §5. In breve: indirizzo personale, mai generico né mascherato; massimo ~10 email/ora e ~20/giorno, distanziate.

## Da fare adesso
1. Chiedere a Massimiliano il saldo crediti Vibe.
2. Cercare con filtri stretti 25-30 decisori, mostrare lista e costo esatto.
3. Con il suo ok sbloccare le email solo dei migliori 20, poi creare bozze con il template v2 (mai inviare).
4. Dopo i nuovi risultati: aggiornare la routine giornaliera `trig_01FQTjpGhpFALewwcAE4ac8V` (oggi gira nella vecchia sessione `session_01N4SsNUgx6UyDCxNf1LooSj`, dove Vibe/Apollo non sono disponibili). Va spostata nella nuova sessione (ricrearla con `create_trigger` sul session corrente e cancellare la vecchia) solo con il suo ok.
5. Brand già contattati: controllare **Gmail → Inviata** e le bozze prima di proporre qualsiasi nome, per non ricontattare.

## Candidati già emersi (azienda adatta, email non verificata)
Jones Road Beauty (Kirsten Walpert, SVP Marketing, assume Paid Social Creative Strategist), Brickell (Josh Meyer), NULASTIN (Leah Garcia), Pawstruck (Kyle Goguen), Dog Is Human (Tim Chen), Cure Hydration (Lauren Picasso), Fable & Mane (Akash Mehta), LYS Beauty, Bounce Curl, Three Ships, Bite, Bearaby, WhyGolf, Supergoop! (Nicky Powell, dir. digital marketing), REFY.
