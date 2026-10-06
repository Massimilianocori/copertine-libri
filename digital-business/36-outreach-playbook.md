# Outreach playbook Scrollcraft (5/10/2026)

Scopo: un solo documento che dice come si fa prospecting e outreach da zero fino all'acconto, con soglie di allarme e i punti in cui oggi ci discostiamo dalle buone pratiche.
Legenda: **[V]** verificato con fonte (URL) · **[S]** dato letto nel repo o in Gmail (sola lettura) · **[I]** ipotesi / da provare.
Limite onesto: le fonti web sono quasi tutte blog di fornitori di strumenti di cold email (Instantly, lemlist, Smartlead, ecc.), che hanno interesse a vendere. I numeri sono ordini di grandezza, non verità. WebFetch era bloccato dal proxy: i numeri vengono dai riassunti di WebSearch, non dalle pagine aperte (non ho potuto aprire la pagina Google ufficiale).

---

## 1. Cosa abbiamo oggi (stato verificato)

| Voce | Fatto | Fonte |
|---|---|---|
| Canale | Email a freddo da `hello@scrollcraft.design` (Namecheap Private Email, alias in Gmail), dominio in riscaldamento dal 17/9 | [S] `00-STATO-PROGETTO.md`, `16-` |
| Risultati | ~60 email in 2 settimane, 1 risposta (rifiuto Kin+Kind 21/9), 0 clienti; il 30/9 ~40 invii con una dozzina di rimbalzi | [S] `25-piano-cambio-strategia.md` |
| Cause del 30/9 | Limite Namecheap (554 5.7.1, ~20/ora), indirizzi generici info@/press@, un hard bounce 550 5.1.1 (19/9, cs@supergreentonik.com) | [S] `22-`, `23-`, Gmail |
| Dopo la svolta (v2) | Solo indirizzi personali verificati: 15 invii l'1/10, 13 il 2/10, 10 il 5/10 (conteggio da Gmail Inviata, pagina 1 di 4). Nessun rimbalzo trovato nei tre giorni | [S] Gmail |
| Risposte in Gmail | Nessuna risposta di prospect dopo il 21/9. Il 5/10 c'è una nostra risposta a Jacob (Outlandish Agency, white-label) con listino e pilota $450: l'email di Jacob non è in Gmail (forse nella webmail Namecheap) | [S] Gmail |
| Offerta in vigore | Niente lavoro gratis dal 5/10; pilota 3 video $450; Holiday Ad Pack 10 video + 10 hook $1.490; white-label $150/$130/$115 per video e hook $35/$30/$25 | [S] `PROCEDURE.md` |
| Tetto invii | 25/giorno dal 5/10, 30 dal 12/10, 40 dal 19/10, follow-up inclusi | [S] `PROCEDURE.md` |
| Routine | Ricerca + bozze ogni giorno 07:00 UTC; l'invio non è mai automatico (blocco "Real-World Transactions") | [S] `00-`, `24-` |

Nota: i file 25, 28 e 29 contengono ancora la vecchia offerta (5 annunci $250, mensile $900): è superata da `PROCEDURE.md`.

---

## 2. Processo end-to-end

```
1 ICP e segnali -> 2 lista verificata -> 3 controllo qualità -> 4 LinkedIn (tocco leggero) -> 5 email 1
-> 6 follow-up giorno 4 -> 7 follow-up giorno 9 -> 8 stop 90 giorni
Risposta -> 9 classificare -> 10 rispondere entro la giornata -> 11 preventivo -> 12 fattura Stripe acconto 50% -> 13 produzione -> 14 consegna e saldo -> 15 caso studio
```

| # | Passo | Regola | Chi |
|---|---|---|---|
| 1 | ICP e segnali | Brand con spesa paid social (fatturato ~$1-50M, 5-150 persone), mercati US/UK/CA/AU. Segnali, in ordine di forza: annunci Meta/TikTok attivi, assunzione di creative strategist/paid social, lancio prodotto, TikTok Shop. Un segnale = motivo per scrivere oggi. Un annuncio attivo è il segnale più citato come affidabile, ma la fonte è un blog di un consulente [V debole] https://omnionlinestrategies.com/blog/best-b2b-intent-signals-2026 | Claude cerca, Massimiliano controlla Ad Library (10 s/brand) |
| 2 | Lista | Solo indirizzi nominali. Livello A (visto in chiaro in fonte pubblica) o "verified" da tool. Mai info@/hello@/press@/support@. Mai indovinati (causa dei rimbalzi 30/9) | Claude |
| 3 | Controllo qualità | Non già contattato (Gmail Inviata + bozze + tracker); non acquisito da gruppi/PE; ha almeno un segnale scritto; un hook fattuale verificabile in 1 riga | Claude |
| 4 | LinkedIn | Per chi ha profilo aperto: richiesta di collegamento senza pitch (vedi §5), DM solo dopo l'accettazione. Non mandare DM ed email lo stesso giorno | Massimiliano (manuale) |
| 5 | Email 1 | Testo semplice, <80 parole, 1 link, 1 sola richiesta, nessun pixel, indirizzo fisico e riga di opt-out (§6) | Bozza Claude, invio con "sì" di Massimiliano |
| 6-7 | Follow-up | Giorno 4 (1-2 righe, aggiunge un elemento nuovo) e giorno 9 (chiusura gentile). Poi stop | idem |
| 8 | Dopo lo stop | Nessun nuovo contatto per 90 giorni, salvo nuovo segnale (assunzione, lancio) | Claude |
| 9-10 | Risposta | Vedi §7: classificare, bozza di Claude, approvazione e invio di Massimiliano nella stessa giornata lavorativa | entrambi |
| 11-12 | Preventivo e acconto | Vedi §8 | Massimiliano firma, Claude prepara |
| 13 | Produzione | Si parte solo ad acconto incassato; rispetto di `CLAUDE.md` (brief approvato, permesso per ogni generazione Higgsfield) | Claude + Massimiliano |
| 14-15 | Consegna e caso | Saldo prima dei file finali senza filigrana [I]; chiedere permesso scritto per usare il lavoro come caso | Massimiliano |

Registro unico: ogni invio, risposta e rimbalzo in un solo file (la coda `invii-*.tsv` di ERRORI #15 + tracker). Oggi il foglio Google non lo aggiorna Claude (non può scrivere): ha già causato un doppio invio (Kin+Kind 19-21/9) e una quasi-duplicata (Camille Rose, 22/9) [S].

---

## 3. Consegnabilità (deliverability)

| Tema | Buona pratica | Stato nostro |
|---|---|---|
| SPF/DKIM/DMARC | Tutti e tre allineati, controllati con MXToolbox o con gli header "Mostra originale" di Gmail (`spf=pass dkim=pass dmarc=pass`). Google li richiede a tutti i mittenti verso Gmail; ai mittenti oltre 5.000/giorno anche l'unsubscribe con un clic [V] https://mailsuite.com/blog/google-sender-guidelines/ (riassunto di terzi) | Record previsti: SPF `v=spf1 include:spf.privateemail.com ~all` (record confermato come formato Namecheap [V] https://dmarcreport.com/blog/how-to-configure-an-spf-record-in-namecheap/), DKIM dal pannello, DMARC `p=none`. **Mai verificati da questo ambiente** (DNS bloccato) [S `25-`]. Da fare: Massimiliano invia una mail a un Gmail personale e controlla gli header |
| Policy DMARC | Si parte da `p=none` per leggere i report, poi `quarantine` quando i report sono puliti. Alcuni blog raccomandano subito `quarantine` [V debole] https://www.zeliq.com/blog/email-warmup | `p=none` con report a `hello@`: i report intasano la casella; usare un indirizzo dedicato o un lettore gratuito di report DMARC [I] |
| Spam | Reclami sotto 0,10%, mai a 0,30% (Google Postmaster) [V] https://mailsuite.com/blog/google-sender-guidelines/ | A 25 email/giorno un solo reclamo supera 0,30%: tolleranza zero. Postmaster Tools non ha dati con volumi così bassi [I] |
| Rimbalzi | <2% normale, 2-5% pulizia lista, >5% critico [V debole] Instantly via https://lemlist.com/blog/cold-email-benchmarks/ | v2: 0 su 38 invii in 3 giorni [S]. 30/9: ~12 su ~40 (30%) [S] |
| Riscaldamento | Dominio secondario: 14-21 giorni, poi 25-30 invii/casella/giorno; massimo 20-50 [V debole] https://www.zeliq.com/blog/email-warmup | Dominio principale in riscaldamento dal 17/9 (18 giorni). Tetto 25 oggi: in linea |
| Limiti provider | Private Email: 500/ora per casella (abbonamenti dal 2/6/2026), prova 20/ora [V] https://www.namecheap.com/support/knowledgebase/article.aspx/10811/2306/new-email-sending-and-usage-limits-for-private-email/ | Il limite di ~20/ora del 30/9 è coerente con un piano in prova [I]: controllare il piano |
| Dominio dedicato | Il cold si manda da un dominio secondario, non dal principale (+15-30% inbox placement dichiarato dai fornitori) [V debole] https://emailbison.com/blogs/cold-email-secondary-domains | **Mandiamo dal dominio principale**, che ospita sito e Stripe. Una cattiva reputazione colpirebbe anche la posta dei clienti |
| Contenuto | Testo semplice, 1 link, niente immagini, niente pixel di tracciamento | In linea. Il Garante italiano ha pubblicato il 21/4/2026 linee guida sui pixel di tracciamento nelle email (consenso nella maggior parte dei casi) [V debole] https://www.consentmo.com/blog-posts/12-5m-fine-and-new-email-rules-what-italys-april-2026-gdpr-decisions-mean-for-your-business: un motivo in più per non usare pixel |

---

## 4. Metriche e soglie di allarme

Aperture: non usarle (Apple MPP, nessun pixel) [S `22-`].
Con 10-25 invii al giorno i numeri sono piccoli: giudicare su finestre di 100-150 invii, non su un giorno.

| Metrica | Come si calcola | Riferimento esterno | Allarme (nostra regola) | Azione |
|---|---|---|---|---|
| Hard bounce | rimbalzi 5.x.x ÷ inviate, per lotto | media <2% [V debole] | Qualsiasi hard bounce: ferma il lotto e verifica l'indirizzo (regola già in `25-`). >2% su 100 invii: stop e pulizia | Non riprovare l'indirizzo; cancellarlo dalla lista |
| Errori di consegna del provider (4xx/554 rate limit) | messaggi respinti da Namecheap | n.d. | Anche 1: dimezza il ritmo del giorno | Spaziare 4+ minuti, mai raffiche |
| Reclami spam | segnalazioni (se visibili) | <0,10%, mai 0,30% [V] | Un reclamo o una risposta "spam/stop": sospendere quel segmento e rileggere il testo | Rimuovere subito, nessun follow-up |
| Inbox placement | invio di prova a 2-3 Gmail/Outlook personali, controllo cartella | n.d. | Spam/Promozioni nel 1 su 3: fermarsi, rivedere DNS e testo | Settimanale [I] |
| Tasso di risposta (tutte, "no" compresi) | risposte reali ÷ consegnate | media 3,43%, primo quartile 5,5%, top 10% 10,7% (Instantly 2026) [V debole] https://instantly.ai/blog/ai-sales-agent-benchmarks-2026-the-complete-performance-report/ | <1% dopo 100 consegnate: controllare prima consegna e lista, poi testo. 0 dopo 150: test di inbox placement prima di toccare l'offerta | Non cambiare più di una variabile alla volta |
| Risposte interessate | risposte che chiedono prezzo/call/esempi ÷ consegnate | n.d. | Criterio nostro (`29-`): >=8 su ~500 contatti scala; 3-7 cambia offerta; <=2 ripensa | Non decidere prima di 300 contatti |
| Accettazione LinkedIn | accettate ÷ inviate | ~28-30% [V debole] https://www.joinvalley.co/blog/linkedin-reply-rate-benchmarks-2026 | <15% su 50 richieste: rivedere profilo e nota [I] | Profilo curato prima di scrivere |
| Tempo di risposta | ore tra risposta del prospect e nostra bozza inviata | n.d. | >1 giorno lavorativo | Controllo inbox 2 volte al giorno, anche la webmail Namecheap |
| Conversione preventivo | preventivi inviati -> acconti incassati | n.d. | <20% su 5 preventivi [I] | Rivedere prezzo, pilota, tempi |
| Costo per pilota | crediti Higgsfield usati ÷ pilota venduto | n.d. | Costo >30% del prezzo [I] | Vedi nota capacità sotto |

Nota capacità [S]: un video 15 s 1080p con Seedance è costato 191,6 crediti (`00-STATO-PROGETTO.md`, 21/9); un pilota da 3 video sono ~575 crediti. Il saldo dichiarato il 3/10 era 24,8 crediti (`29-`). Prima di promettere "consegna in 5 giorni" verificare il saldo.

Sul test A/B dei segmenti (PROCEDURE: "confronto dopo 7 giorni"): a 20 invii/giorno e ~3% di risposte sono ~4 risposte in 7 giorni, troppo poche per distinguere due segmenti [calcolo mio, non una fonte]. Servono almeno 100-150 invii per segmento.

---

## 5. Frequenza, oggetto, lunghezza, personalizzazione, LinkedIn

| Tema | Pratica 2026 | Fonte | Nostra scelta |
|---|---|---|---|
| Follow-up | 4-7 passaggi totali, intervalli 3-4 giorni (3-7-7); ma altri dati dicono che da 4 email in su i reclami triplicano; 50-80% delle risposte arriva dai follow-up (un'altra fonte dice 58% dalla prima email: dati in conflitto) | [V debole] https://bouncezero.io/cold-email-follow-up-guide-2026 · https://instantly.ai/blog/ai-sales-agent-benchmarks-2026-the-complete-performance-report/ | 3 tocchi (giorno 0, 4, 9), poi stop: prudente per un dominio giovane |
| Lunghezza | sotto 80 parole; follow-up 2-4 frasi | [V debole] idem | Oggi ~110 parole: accorciare (§10) |
| Oggetto | 2-4 parole o <50 caratteri, specifico, niente urgenza/"ASAP" | [V debole] https://www.leadhaste.com/blog/cold-email-subject-lines-2026 | Oggi: "Short-form video ads for {Company}" (generico) |
| Personalizzazione | Oggetto/prima riga specifici: 7% di risposte contro 3% (studio Belkin 2025 su 5,5 milioni di email, citato da un blog); apertura basata su segnale (assunzione, lancio) 15-25% dichiarato | [V debole] https://prospeo.io/s/cold-email-personalization · https://omnionlinestrategies.com/blog/best-b2b-intent-signals-2026 | La v2 ha tolto la riga personale: da rimettere, ma fattuale e senza adulazione |
| LinkedIn prima dell'email | Multicanale ~+50% di risposte; un caso con LinkedIn prima dell'email: da 1,8% a 4,3% | [V debole] https://www.sproutworth.com/multichannel-cold-outreach/ · https://somethinginc.com/blog/coldiq-multichannel-reply-rate-case-study/ | Oggi email prima, LinkedIn dopo e poco eseguito. **Da testare** il contrario su un segmento [I] |

---

## 6. Regole legali minime (da far confermare a un legale)

| Regola | Fonte | Stato |
|---|---|---|
| USA, CAN-SPAM: indirizzo postale fisico valido in ogni email commerciale; opt-out semplice onorato entro 10 giorni lavorativi; sanzioni fino a $53.088 per email | [V] riassunto di https://www.ftc.gov/node/81459 (pagina FTC non aperta, WebFetch bloccato) | **Il nostro template non ha indirizzo né riga di opt-out** [S]. Applicabilità a un mittente italiano: da chiedere a un legale [I] |
| UK, PECR: B2B verso società ok; ditte individuali e alcune società di persone contano come privati e servono consenso/soft opt-in | [V debole] https://globallawexperts.com/b2b-email-marketing-rules-uk/ | Escludere contatti UK con ditte individuali [I] |
| Italia/GDPR: siamo titolari in Italia; il Garante è severo anche sul B2B | [V debole] https://overloop.com/it/blog/cold-email-legale | Informativa breve e opt-out; la pagina `privacy.html` esiste: linkarla [I] |
| Recensioni e testimonianze false, anche generate con AI, vietate dalla regola FTC (in vigore dal 21/10/2024) | [V] https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials | Già in `31-`: nessuna testimonianza sintetica, claim solo da lista approvata dal cliente |

---

## 7. Template per segmento

Regole comuni: inglese, testo semplice, firma con indirizzo fisico `{INDIRIZZO}` (da fornire, vedi §6), riga di opt-out, nessuna promessa di lavoro gratis (politica 5/10), nessuna affermazione su clienti che non abbiamo ("we work with..."), nessun elogio generico. `{HOOK}` = un fatto verificabile con fonte (annuncio attivo, assunzione, lancio). Se non c'è un fatto, non si scrive.
Il portfolio va presentato per quello che è: lavori dimostrativi (la risposta a Outlandish del 5/10 lo dice già: "concept pieces built on real products, not client deliverables" [S]).

### 7.1 Agenzie white-label (paid social, performance, creative)

Valore: capacità extra a volume con il loro marchio. Una agenzia vale più di molti brand [S `28-`].

**Email 1** (oggetto: `overflow video capacity`)
```
Hi {Nome},

{HOOK: es. "Saw {Agenzia} runs paid social for DTC brands such as {Cliente pubblico}."}

We're Scrollcraft, a small studio producing 9:16 video ads and hook variants for agencies, fully white-label. Per-video pricing from $150 (10 videos) down to $115 (100), hooks from $35. Minimum 3 videos, first batch in 5 business days.

Worth a short reply with what you'd test first? A paid 3-video pilot is $450.

Massimiliano Cori, Founder, Scrollcraft
www.scrollcraft.design
{INDIRIZZO}. Not relevant? Reply "no" and I won't write again.
```
**Follow-up giorno 4**: `Quick follow-up, {Nome}. Most agencies use us when a client needs 10+ hook variants in a week. Does that come up for {Agenzia}?`
**Follow-up giorno 9**: `Last note from me. If overflow production isn't a topic right now, no problem, I won't write again. Pricing is here if it ever is: www.scrollcraft.design`

### 7.2 DTC beauty (skincare, haircare, makeup)

Valore: più concetti e hook da testare ogni mese (cadenza di 8-12 nuovi creativi/mese citata per beauty [V debole] https://www.webtonic.io/blog/beauty-skincare-ad-creative-statistics). Mai promettere risultati di vendita.

**Email 1** (oggetto: `{Brand} hook variants`)
```
Hi {Nome},

{HOOK: es. "Noticed {Brand} is running new Meta ads for {prodotto}" oppure "Saw the open Paid Social Creative Strategist role."}

We make short 9:16 video ads (UGC-style, AI-produced, labelled as such) so a team can test more hooks without more shoots. Pilot: 3 videos for $450, delivered 5 business days after your brief. Examples: www.scrollcraft.design/#skincare

Would a pilot on {prodotto} be useful? A one-word reply is enough.

Massimiliano Cori, Founder, Scrollcraft
{INDIRIZZO}. Not relevant? Reply "no" and I won't write again.
```
**Follow-up giorno 4**: `Hi {Nome}, one addition: for {prodotto} I'd start with 3 different first-3-second hooks on the same product shot. Want the outline?` (se risponde sì: un outline scritto, non un video)
**Follow-up giorno 9**: `Closing the loop, {Nome}. If creative volume isn't a priority this quarter, I'll leave it here.`
**LinkedIn (nota, max 300 caratteri)**: `Hi {Nome}, I follow {Brand}'s work. I run Scrollcraft, a small studio making short-form video ads for beauty brands. Happy to connect.`

### 7.3 Moda e lusso (ipotesi, da testare con pochi invii)

Rischio verificato: i marchi del lusso che hanno pubblicato immagini AI, anche dichiarate, hanno avuto reazioni negative (Valentino, Gucci) e la ricerca accademica citata dice che la dichiarazione abbassa il valore percepito, salvo creatività molto alta [V] https://www.glossy.co/fashion/luxury/luxury-fashions-ai-marketing-experiments-hit-a-turning-point · https://www.tarleton.edu/cob/?p=4216. Quindi non si vende "AI" ma direzione creativa (posizionamento `29-`). Segmento da trattare come test piccolo (10 contatti), con meno volume e più cura.

**Email 1** (oggetto: `{Brand} {prodotto}, short film idea`)
```
Hi {Nome},

{HOOK: un fatto sul lancio/campagna reale, es. "Saw the {collezione} launch."}

I'm Massimiliano Cori, founder of Scrollcraft, an advertising studio with a photographer's art direction. I'd like to send you a one-page creative idea for {prodotto}: concept, light, framing, no AI buzzwords. It's a proposal, not a finished film.

Our latest piece is a concept spot built on a real fragrance (not a client job): www.scrollcraft.design

May I send the page?

Massimiliano Cori, Founder, Scrollcraft
{INDIRIZZO}. Not relevant? Reply "no" and I won't write again.
```
Attenzione: lo spot Tom Ford usa un marchio reale. Prima di allegarlo a terzi controllare la politica trademark in `00-STATO-PROGETTO.md` [I]. Il "creative page" richiede lavoro: ricerca e brief come da `CLAUDE.md`, nessuna generazione senza permesso.
**Follow-up giorno 4/9**: una riga, nessuna insistenza; un solo follow-up per questo segmento [I].

---

## 8. Obiezioni e risposte

Principio: riconoscere, fare una domanda, non attaccare i concorrenti, non promettere ciò che non si può mostrare [V debole su schema: riconosci-reindirizza-chiedi] https://instantly.ai/blog/3-scripts-for-b2b-cold-call-objections/.

| Obiezione | Risposta (breve) |
|---|---|
| "We already have an agency / creators" | `Makes sense. Most teams keep them. We're used for the extra volume, e.g. 10 hook variants of an existing winner. What's your current bottleneck, speed or number of variants?` |
| "Is it AI? Does it look fake?" | `Yes, and we label it as such. Every clip gets a frame-by-frame review (hands, labels, lip-sync). Examples are demonstration pieces, not client work. A 3-video pilot lets you judge on your product.` |
| "Send me more info" | `Happy to. So I send the right thing: is this for new concepts, hook variants of existing ads, or product photos?` |
| "What does it cost?" | Listino reale in una riga: pilota $450 (3 video), Holiday Ad Pack $1.490 (10 video + 10 hook, ordine entro 24/10, consegna entro 10/11), agenzie $150/$130/$115. Poi: `Which product would you start with?` |
| "Do you have a free sample?" | `We don't do free work anymore, to keep quality high. The paid 3-video pilot is the fastest way, $450, and I'd credit it against a larger order if you continue.` (lo sconto/credito è una decisione di Massimiliano: [I], non annunciarlo senza il suo ok) |
| "Not now / next quarter" | `Understood. I'll check back in {mese}. Anything specific that would make it a priority then, like a launch?` e mettere un promemoria con data |
| "Who have you worked with?" | Verità: studio nuovo, nessun cliente pubblico (regola `23-`). `We're new; the work online is demonstration. That's why the pilot is small and fixed-price.` Mai nomi inventati |
| "Can you use our product photos / brand rules?" | `Yes: we start from your official assets only and follow your claims list. You approve the brief before we produce anything.` |
| "Who owns the video?" | Diritti commerciali trasferiti al pagamento, white-label su richiesta (testo già usato con Outlandish) [S] |
| "Remove me" | Conferma in una riga, rimozione immediata, mai più follow-up |

---

## 9. Quando qualcuno risponde

| Tipo di risposta | Azione | Entro |
|---|---|---|
| Interessato / chiede prezzo / chiede una call | Bozza di risposta con 3 domande di brief (§10) e proposta di 2 orari | giornata lavorativa |
| Chiede un campione gratis | Risposta di §8; non produrre lavoro gratis (politica 5/10) | giornata |
| Obiezione | §8, una sola replica, poi stop se ripete il no | 1 giorno |
| "Non sono io, scrivi a X" | Ringraziare, scrivere a X citando il consiglio, aggiornare registro | 1 giorno |
| Fuori ufficio | Ripianificare il follow-up dopo il rientro | - |
| "No grazie" | Ringraziare in una riga, segnare "no" (è un dato), nessun altro contatto | - |
| Ostile / "spam" | Scusarsi in una riga, rimuovere, segnalare nel registro | subito |

Chi risponde è lavoro caldo: ha precedenza su ogni nuova ricerca. Claude prepara la bozza, Massimiliano approva e invia (nessun invio automatico).

### 9.1 Dal sì al preventivo

1. **Brief** (3-5 domande, per email o call di 15 minuti): prodotto e obiettivo, piattaforma e durata, quante varianti, consegne e scadenza, materiali ufficiali disponibili, claim ammessi, parole vietate. Senza foto prodotto ufficiali non si parte (ERRORI #5).
2. **Preventivo scritto** (una pagina): cosa si consegna (n. video, formato 9:16, durata), cosa è incluso (script, voce, sottotitoli, montaggio, 2 revisioni, come nella risposta a Outlandish), cosa serve dal cliente, tempi (da quando c'è acconto e brief), prezzo, validità 7 giorni, diritti, dichiarazione che il contenuto è generato con AI, nessuna testimonianza sintetica.
3. **Costo crediti**: se serve, preventivo interno Higgsfield (`PROCEDURE.md` punto 4) e "sì" di Massimiliano per ogni generazione.

### 9.2 Fattura Stripe con acconto 50%

| Passo | Dettaglio |
|---|---|
| Quale strumento | Fattura Stripe (Invoice) o Payment Link con importo su misura (`PROCEDURE.md`) |
| Come si divide | Due fatture, 50% acconto e 50% saldo, è lo schema comune; Stripe supporta anche piani di pagamento a più scadenze [V debole, fonti di terzi: https://www.orderspace.com/blog/support-insights-taking-deposits-and-part-payments]. Controllare nel pannello Stripe quale opzione è disponibile sul nostro account |
| Prerequisito [S] | Il modulo "Configura le fatture" di Stripe è rimasto incompleto (`00-STATO-PROGETTO.md`, 20/9): va completato prima della prima fattura. I 4 Payment Link del sito sono LIVE e non si toccano senza chiedere |
| Condizioni scritte | Acconto = condizione per iniziare; saldo a consegna; file finali senza filigrana dopo il saldo [I]; scadenza fattura 7 giorni |
| Regole | Nessuna produzione prima dell'acconto; il saldo parte alla consegna dell'anteprima approvata |
| Fiscale [I] | Fatturazione a clienti esteri (IVA, ricevute Stripe, registrazione dei ricavi): chiedere al commercialista prima della prima fattura |

---

## 10. Cosa NON fare

| Non fare | Perché |
|---|---|
| Inviare raffiche dal tasto Gmail, più di ~10 email/ora | Rate limit Namecheap, 19 email mai consegnate il 30/9 [S] |
| Scrivere a info@/press@/hello@/support@ o a indirizzi indovinati | Nessun decisore li legge; rimbalzi [S] |
| Copiare un indirizzo a memoria | Errore #15 (tim@somnee.com): copiare dalla coda |
| Elogi generici e tono da supplica | Già corretto in v2 [S] |
| Dire "we work with..." senza clienti reali | Non abbiamo clienti pubblici (`23-`); il testo attuale lo suggerisce, vedi §11 |
| Promettere lavoro gratis dopo il 5/10 | Politica `PROCEDURE.md` |
| Mostrare lavori su marchi reali come se fossero lavori per il marchio | Rischio trademark/credibilità [I] |
| Usare pixel di tracciamento, link accorciati, immagini, allegati pesanti | Consegnabilità e Garante [V debole] |
| Più di 3 tocchi per contatto, o ricontattare entro 90 giorni | Reclami e reputazione |
| Inviare in automatico senza qualcuno presente | Regola di sistema e di Massimiliano (`23-`) |
| Aumentare il tetto (30, poi 40) dopo un incidente di consegna senza 2 settimane pulite | Reputazione di un dominio di 18 giorni [I] |
| Decidere un segmento dopo 7 giorni con 4 risposte | Numeri troppo piccoli |
| Generare video/immagini per un prospect senza permesso e brief approvato | `CLAUDE.md` |
| Testimonianze, recensioni o esperienze in prima persona inventate | Regola FTC e `31-` |

---

## 11. Dove il nostro processo si discosta dalle buone pratiche

Gravità: alta = rischia reputazione/legalità/coerenza; media = costa risposte; bassa = ottimizzazione.

| # | Discostamento (con prova) | Buona pratica | Gravità | Correzione proposta |
|---|---|---|---|---|
| 1 | Email in uscita (1-5/10) ancora con "free sample ad on one of your products" [S Gmail], mentre dal 5/10 la politica è "niente lavoro gratis" | Un'offerta sola, coerente con il listino | Alta | Sostituire con il pilota $450 (§7); aggiornare `22-outreach-v2.md` |
| 2 | Frase "We work with independent beauty and cosmetics brands" / "supplement and wellness brands" [S Gmail] | Nessuna affermazione falsa (`23-`: nessun cliente reale) | Alta | Riformulare: "We make ads for..." |
| 3 | Nessun indirizzo postale né riga di opt-out nel template [S] | CAN-SPAM e uguale pratica UK/UE [V] | Alta | Aggiungere `{INDIRIZZO}` e opt-out; chiedere conferma a un legale |
| 4 | Cold dal dominio principale `scrollcraft.design` | Dominio secondario dedicato [V debole] | Alta | Quando il volume supera 25/giorno o dopo un nuovo incidente: dominio secondario con redirect al sito (`16-`, già in pausa) |
| 5 | **RISOLTO il 6/10:** test reale con header Gmail: `spf=pass`, `dkim=pass` (selettore `privateemail`), `dmarc=pass` (p=none). Il test era dalla webmail Namecheap; controllare lo stesso su una email inviata dal routine. [era: SPF/DKIM/DMARC mai verificati da test reale `25-`] | Verifica con header e MXToolbox | Alta | Massimiliano: invio di prova a Gmail personale, controllo `spf/dkim/dmarc=pass`, esito nel registro |
| 6 | Salita del tetto 25 -> 30 (12/10) -> 40 (19/10) a calendario fisso [S] | Salire solo con rimbalzi <2% e senza reclami [V debole: 25-30/casella dopo 14-21 giorni] | Media | Salita condizionata alle metriche di §4, non alla data |
| 7 | Email di ~110 parole, oggetto generico, riga personale tolta nella v2 [S Gmail] | <80 parole, oggetto specifico, 1 fatto verificabile [V debole] | Media | Template di §7 |
| 8 | Risposte possibili nella webmail Namecheap e non in Gmail; foglio aggiornato a mano [S] | Un solo registro, caselle monitorate | Media | Inoltrare la webmail a Gmail o controllarla 2 volte al giorno; un solo file registro (coda `.tsv`) |
| 9 | LinkedIn dopo l'email e mai eseguito con continuità [S `20-`] | LinkedIn per primo (+risposte) [V debole] | Media | Prova su un segmento: LinkedIn giorno 0, email giorno 2 |
| 10 | Follow-up del 26/9: "Just bumping this to the top of your inbox" [S Gmail], senza elemento nuovo, spediti anche a info@ e rimbalzati | Ogni follow-up aggiunge qualcosa | Media | Follow-up di §7 |
| 11 | Test A/B tra segmenti dopo 7 giorni [S PROCEDURE] | Campione sufficiente | Media | 100-150 invii per segmento prima di decidere |
| 12 | Capacità: 24,8 crediti il 3/10 [S `29-`] contro ~575 per un pilota | Promettere solo ciò che si può consegnare | Media | Verificare il saldo prima di dire "5 giorni" |
| 13 | Segnali d'acquisto: il controllo Meta Ad Library è previsto ma non risulta registrato per brand [S `29-`, nessuna traccia nel registro] | Un segnale documentato per contatto | Bassa | Colonna "segnale + fonte" nel registro |
| 14 | Rapporto con la vecchia offerta ($250 / $900) ancora in `25-`, `28-`, `29-` | Documenti coerenti | Bassa | Nota di "superato" in cima a quei file |
| 15 | Spot su prodotto reale (Tom Ford) mostrato a terzi [S risposta Outlandish] | Marchi reali: attenzione legale | Bassa | Controllare politica trademark in `00-` |

Punti già in linea con le buone pratiche: indirizzi nominali verificati, niente generici, testo semplice con un solo link, niente pixel, follow-up limitati a 2, invii distanziati, metrica = risposte e non aperture, nessuna testimonianza sintetica.

---

## Fonti

- Google, requisiti mittenti (via riassunto): https://mailsuite.com/blog/google-sender-guidelines/
- Benchmark 2026 (fornitori): https://instantly.ai/blog/ai-sales-agent-benchmarks-2026-the-complete-performance-report/ · https://lemlist.com/blog/cold-email-benchmarks/
- Follow-up: https://bouncezero.io/cold-email-follow-up-guide-2026
- Oggetto e personalizzazione: https://www.leadhaste.com/blog/cold-email-subject-lines-2026 · https://prospeo.io/s/cold-email-personalization
- Riscaldamento e domini secondari: https://www.zeliq.com/blog/email-warmup · https://emailbison.com/blogs/cold-email-secondary-domains
- Namecheap: https://www.namecheap.com/support/knowledgebase/article.aspx/10811/2306/new-email-sending-and-usage-limits-for-private-email/ · https://dmarcreport.com/blog/how-to-configure-an-spf-record-in-namecheap/
- Segnali d'acquisto: https://omnionlinestrategies.com/blog/best-b2b-intent-signals-2026
- LinkedIn e multicanale: https://www.sproutworth.com/multichannel-cold-outreach/ · https://somethinginc.com/blog/coldiq-multichannel-reply-rate-case-study/ · https://www.joinvalley.co/blog/linkedin-reply-rate-benchmarks-2026
- Legale: https://www.ftc.gov/node/81459 · https://globallawexperts.com/b2b-email-marketing-rules-uk/ · https://overloop.com/it/blog/cold-email-legale · https://www.consentmo.com/blog-posts/12-5m-fine-and-new-email-rules-what-italys-april-2026-gdpr-decisions-mean-for-your-business · https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials
- Lusso e AI: https://www.glossy.co/fashion/luxury/luxury-fashions-ai-marketing-experiments-hit-a-turning-point · https://www.tarleton.edu/cob/?p=4216
- Creativi beauty: https://www.webtonic.io/blog/beauty-skincare-ad-creative-statistics
- Obiezioni: https://instantly.ai/blog/3-scripts-for-b2b-cold-call-objections/
- Acconti Stripe (terzi): https://www.orderspace.com/blog/support-insights-taking-deposits-and-part-payments
