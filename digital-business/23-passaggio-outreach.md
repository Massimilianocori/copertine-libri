# Passaggio di consegne — outreach Scrollcraft (2026-09-30)

Da leggere insieme a `22-outreach-v2.md`. Serve a una nuova sessione per riprendere senza perdere contesto.

## Chi è l'utente e come lavorare con lui
- Massimiliano Cori, italiano, fondatore solo di **Scrollcraft** (video ad UGC generati con AI per brand DTC). Rispondere **sempre in italiano**, breve, passo per passo: non è tecnico e vuole essere guidato.
- **Mai inviare email.** Solo bozze Gmail. Invio solo con un suo via libera esplicito nel momento. Ha detto: "prima di fare qualcosa ricordati di chiedere".
- **Mai spendere crediti** (Vibe, Apollo) senza dirgli prima il costo e avere il suo ok.
- Mittente: `hello@scrollcraft.design` (alias Gmail via Namecheap Private Email).
- Sito/portfolio: www.scrollcraft.design, con ancore #skincare, #mens-grooming, #pet-supplements, #fragrance.

## Il sito scrollcraft.design: dove sta e come modificarlo
- **Codice**: un solo file `digital-business/portfolio/index.html` (HTML statico, nessun backend) più le immagini/video nella stessa cartella (`photo-1.webp`…`photo-5.webp`, video `.mp4`). Istruzioni base in `digital-business/portfolio/README.md`.
- **Hosting**: Netlify, progetto `beamish-duckanoo-de8a46` (id `16652805-6970-4aef-98e4-c869446a87d6`), dominio principale **https://scrollcraft.design**. Pannello: https://app.netlify.com/projects/beamish-duckanoo-de8a46 (login con l'account di Massimiliano).
- **Come va online**: il sito è agganciato al repo GitHub `massimilianocori/copertine-libri`. Ogni push sul branch `claude/digital-files-business-plan-f8y8gd` ricostruisce il sito in pochi minuti. Quindi per cambiarlo: modificare `index.html`, fare commit e `git push` su quel branch. Nessun altro passaggio.
- **Anteprima del branch**: http://claude-digital-files-business-plan-f8y8gd--beamish-duckanoo-de8a46.netlify.app
- **Stato Netlify verificato il 30/9**: ultimo deploy in stato "ready", nessuna password sul sito, form Netlify non attivi.
- **Sezioni e ancore**: `#fragrance`, `#mens-grooming`, `#pet-supplements`, `#skincare`, `#sienna`, `#stills` (foto). Le ancore vanno usate nei link delle email.
- **Pagamenti**: sezione prezzi con 4 Payment Link Stripe in modalità LIVE (incassano soldi veri). Non toccare i link senza chiedere a Massimiliano.
- **Regole di contenuto**: nessuna affermazione falsa (non ha ancora clienti reali: niente "running on real ad accounts"); video pubblici solo de-brandizzati; niente trademark di brand reali (vedi `00-STATO-PROGETTO.md`, sezione trademark).
- **Prima di caricare o cambiare qualcosa sul sito, dire a Massimiliano cosa si vuole fare e aspettare il suo ok** (l'ha chiesto esplicitamente).
- Accessi (Netlify, Stripe, Namecheap, Gmail): sono account suoi, le password non sono e non devono essere nel repo. Se serve un accesso, chiedergli di fare il login lui o di collegare il connettore.

## Tutto il resto del progetto (per non ripartire da zero)
**Leggi per primo `00-STATO-PROGETTO.md`** (memoria persistente: regole fisse, configurazione email, tracker, criteri brand, politica trademark, Stripe). **Dove 22 e 23 contraddicono il 00, valgono 22 e 23.** In particolare sono superati: il "pattern info@/hello@/support@ se ci sono segnali" (ora vietato), l'obiettivo fisso di 20 bozze al giorno, il testo con adulazione, e i limiti di invio (ora ~10/ora, ~20/giorno distanziati).

- **Sienna** (personaggio AI di Scrollcraft, profili Instagram e TikTok): strategia e stato in `19-personaggio-ai-sienna.md`; algoritmo e piano giornaliero in `21-algoritmo-instagram-tiktok.md`. Regole decise: un solo video prodotto per Instagram, poi ripubblicato anche su TikTok con lo stesso file (un video al giorno costa troppo); su TikTok solo le foto educational ("Scoperta della settimana"), tutto il resto delle foto solo su Instagram. Video/immagini si generano con Higgsfield: prima leggere `18-higgsfield-workflow-guida.md`. La pubblicazione su TikTok passa dal connettore Higgsfield (`tiktok_prepare_publish`, dove lui conferma il widget).
- **Acquisizione clienti oltre l'email**: `20-strategia-acquisizione-clienti.md` (LinkedIn manuale, ticket Upwork #55547453 fermo dal 19/9, routine giornaliera). Marketplace UGC (Billo/Insense/JoinBrands) scartati.
- **Prezzi e offerta**: `11-strategia-prezzi.md`, `12-campione-gratuito.md`; stime `14-stime-fatturato-mesi-1-3.md`.
- **Tracker outreach**: Google Sheet "Scrollcraft - Outreach Tracker" (fileId `1emO4s9g4xKBl79JU0NfmKpfkbSBjLAsqiKrFHdum6uk`). Claude non può scrivere sulle celle: gli aggiornamenti li fa Massimiliano a mano.
- **Altri lavori suoi, non Scrollcraft**: negozio Etsy PressedHeart, libri KDP: sono altri progetti, non mescolarli con l'outreach.
- **Account/servizi collegati in Claude**: Gmail, Google Drive, Google Calendar, GitHub, Netlify, Higgsfield, Make, Canva, Apollo, Vibe Prospecting. Se uno strumento non compare nella sessione, chiedergli di controllarne l'interruttore nel "+" in basso a sinistra della chat; se non basta, aprire una nuova sessione.

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
