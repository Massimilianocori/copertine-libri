# Rispondoio — Handoff / Punto della situazione

Documento di continuità per riprendere il lavoro in una nuova chat.
Ultimo aggiornamento: 2026-07-15. Sostituisce le versioni precedenti.

---

## 1. Cos'è il progetto
Landing page **premium, single-page, in italiano** per **Rispondoio**: assistente
**vocale + chat AI** che risponde a telefonate e messaggi delle piccole attività,
prende appuntamenti e li scrive in agenda. Integra il widget **Retell** (voce + chat).

- **Un solo file**: `index.html` (HTML + CSS + JS inline; font e widget via base64/CDN). Nessun backend, nessuna build. ~1325 righe.
- **Dominio futuro**: `rispondoio.ai` (non ancora attivo).
- **Sito live**: https://massimilianocori.github.io/copertine-libri/
- **Repo**: `Massimilianocori/copertine-libri`
- **Branch di sviluppo (questa sessione)**: `claude/install-ui-ux-pro-max-skill-5ji5hb`
  (⚠️ in sessioni precedenti era `claude/script-explanation-structure-eefj7y`)

## 2. Deploy (IMPORTANTE)
- GitHub Pages serve dal branch **`main`**. Il sito live = `index.html` su `main`.
- **Per pubblicare**: `git push origin <branch>:main` (fast-forward del tip del branch su main).
- La CDN di Pages impiega **~10-15 min**; per saltare la cache aprire con `?v=N` (cambiando N) e **hard refresh** (Cmd+Shift+R). Il browser tende a servire l'index.html vecchio: senza hard refresh sembra "non aggiornato".
- Sviluppo sul branch designato, poi push su main.

## 3. Brand (aggiornato in questa sessione)
- **Nome**: Rispondoio. **Logo**: anello teal + barre onda-audio arancioni, SVG inline (nav, footer). Teal `#0F7A85` (footer `#1FA5B0`), arancione `#F5822A`.
- **Arancione del brand** = `--brand-orange:#F5822A` (con `--brand-orange-strong:#E06A12`, `--brand-orange-soft:#FFF1E6`). **Ora usato come bordo su TUTTE le "finestre"/card** del sito (hero call-card, chat-card, settori, come funziona, piani, chat-plan, bundle, contatti) + badge "Il più scelto".
- **Colori funzionali**: voce = blu `--accent:#0A6DD8`; chat = verde `#0FA968`/`#0B8A54`.
- **Font**:
  - Corpo = **Arimo** (clone Helvetica), base64 `@font-face` (pesi 400/700).
  - **Titoli** = **Fraunces** (serif display, subset latin, opsz 144, pesi 600-700), incorporato base64 offline. Applicato a `.display` via `--font-display`. Da qui il look "editoriale premium".
- **Contatti**: email `io@rispondoio.net` (mailto attivo). Telefono: "Presto disponibile".

## 4. Retell (chiavi e agenti)
- **Public key**: `public_key_30f48a75179b4474a40e7`
- **Voice agent**: `agent_238b916f761b4882738071d0b5`
- **Chat agent**: `agent_003d2188ae48906eb0bf581cd7`
- Widget: `<script id="retell-widget" src="https://dashboard.retellai.com/retell-widget-v2.js" type="module" data-*>` in fondo a `index.html`. `data-title` e `data-bot-name` = "Rispondoio".

### 4a. Rimozione branding "Retell" (RISOLTO — vedi §9)
Il widget monta il suo pannello in **UN shadow root** sulla pagina (NON un iframe → raggiungibile via DOM). La struttura reale (scoperta con la diagnostica `?diag=1`):
- L'header "Retell" è un **logo SVG** (87×24, `fill #00122E`) dentro `div._headerBrand_<hash>` — **niente testo, niente attributo "retell"** → la sostituzione testuale non lo toccava.
- Il "Powered by" è un `<a href="https://www.retellai.com/?utm_source=widget">`.

**Soluzione attiva** (in `index.html`):
1. Shim in `<head>` che intercetta `Element.prototype.attachShadow` e forza `mode:"open"` (per raggiungere anche shadow root "closed"). Deve girare prima del widget (script classico prima del module deferito).
2. `widgetRoots()` raccoglie ricorsivamente document + tutti gli shadow root.
3. CSS iniettato in ogni shadow root (`HIDE_CSS`): nasconde `a[href*=retell]`, powered-by/watermark/branding, **nasconde `[class*="headerBrand"] svg/img` e ci mette "Rispondoio" via `::after`** (teal, regge i re-render React).
4. `rebrandRetell()` sostituisce testo/attributi "Retell"→"Rispondoio" e nasconde loghi; gira ogni 300ms + `MutationObserver` (debounce rAF).
5. Il selettore usa `[class*="headerBrand"]` (robusto ai cambi di hash tra versioni del widget).
- ⚠️ Se una futura versione del widget cambia la classe `_headerBrand_*`, ripristinare la diagnostica (vedi §9) per ritrovare il nuovo selettore.

## 5. Struttura pagina (ordine sezioni)
1. **Hero** (voce, blu) — call-card demo con onda audio
2. Strip differenziale (Setup/Configurato/Assistenza)
3. **Settori** (`#settori`)
4. **Come funziona** (`#come-funziona`, 3 step)
5. **Prezzi · Assistente vocale** (`#prezzi`, blu) — 3 piani
6. **Chat AI** (`#chat`, verde) — sezione gemella, su **desktop layout speculare** (card a sinistra, testo a destra) per differenziarla dalla voce
7. **Prezzi · Chat AI** (`#prezzi-chat`, verde) — piano Chat + bundle
8. **CTA finale** (`#final`, scura)
9. **Contatti** (`#contatti`)
10. Footer

## 6. Prezzi (aggiornati in questa sessione — IVA esclusa)
Toggle in due punti (voce + chat) sincronizzati. **Non più "Mensile": ora "Trimestrale" (impegno minimo 3 mesi) vs "Annuale".** Ragione: nessuno paga attivazione €149 + canone per un mese solo.

**Voce** (prezzo /mese; il toggle cambia trimestrale↔annuale via `data-monthly`/`data-annual`):
| Piano | Trimestrale | Annuale | Minuti | Attivazione (annuale) |
|---|---|---|---|---|
| Basic | 79 | 67 | 200 | 149 → 74,50 (−50%) |
| Standard | 129 | 109 | 500 | gratis |
| Pro (featured, badge arancione) | 229 | 189 | 1.000 | gratis |
Nota impegno su tutti i piani: **"Impegno minimo 3 mesi."** (era "Disdicibile dopo il primo mese").

**Chat AI**: 69/mese (annuale 57), attivazione € 99.
**Bundle voce+chat**: chat a **€ 39/mese**, **attivazione chat gratuita** (richiede piano voce annuale).

- I pulsanti dei piani ("Inizia con…", "Aggiungi Chat AI") mostrano un toast placeholder → **da collegare a Stripe/PayPal**.

## 7. Modale configuratore bundle (NUOVO in questa sessione)
"Attiva il bundle" apre una **modale in 2 passi** (`#bundleModal`):
- **Passo 1**: Chat AI mostrata come inclusa (€39/mese, attivazione gratuita) + scelta di uno dei 3 piani voce annuali (radio, Pro preselezionato, evidenziato arancione). Bottone "Vai al riepilogo".
- **Passo 2** (checkout): righe di costo (voce, chat, attivazione voce, attivazione chat), **Canone mensile**. Bottone "Procedi al pagamento" (placeholder), "← Modifica la scelta". Chiusura con X / click fuori / Esc. Responsive.
- Dati piani e calcolo in JS: `BM_PLANS`, `BM_CHAT=39`, `eur()` (formato it-IT). Handler: `bmOpen/bmClose/bmStep`, `#bmNext`, `#bmBack`, `#bmPay`.
- ⚠️ **Il "Totale primo anno" è stato RIMOSSO su richiesta**: nel riepilogo si mostra solo il canone mensile e le voci, NON il totale annuale. Vale per tutte le finestre di pagamento.

## 8. Comportamenti JS del widget (già implementati)
IIFE in fondo a `index.html`:
- **Apertura widget** dai pulsanti "Prova la voce"/"Prova la chat": clicca il launcher fisso del widget.
- **Chat pulita**: on-load pulisce lo storage Retell; alla chiusura ricrea il widget da zero.
- **Chiusura automatica**: alla conferma dell'appuntamento il pannello si chiude dopo **60 secondi** (era 5s — troppo poco per leggere il riassunto).
- **Niente asterischi**: `cleanRetellText()` rimuove il markdown **solo dentro il widget**.
- **Rebranding**: vedi §4a.

## 9. Diagnostica widget (rimossa, ma da riusare se serve)
Per capire la struttura del widget (bloccato nel mio sandbox) è stato usato un overlay temporaneo `?diag=1` (poi rimosso). Se "Retell" ricompare (nuova versione widget), ricreare uno script gated su `?diag=1` che: elenca iframe+src, conta hit testo/attributi "retell", e **dumpa svg/img con class+parent.class e l'HTML dello shadow root** (senza style/script; NB: `ShadowRoot` non è clonabile → usare regex sul `innerHTML`). L'utente apre `?diag=1`, apre la chat, e manda screenshot del box scuro in alto a sinistra.

## 10. Da fare (aperti)
1. **Pagamenti Stripe/PayPal**: collegare i pulsanti "Inizia con…", "Aggiungi Chat AI" e "Procedi al pagamento" della modale bundle ai link di checkout reali (passando piano + canone selezionato).
2. **Email istantanea**: l'email dell'appuntamento arriva dopo qualche minuto → renderla istantanea. Lato **Make** (MCP Make disponibile): passare a flusso webhook-triggered.
3. **Prenotazione reale della chat**: verificare che l'agente chat abbia le stesse function/tool→webhook dell'agente voce (Retell function → webhook Make → Google Calendar + email).
4. **Asterischi alla fonte**: nel prompt dell'agente **chat** su Retell istruire risposte in testo semplice (senza markdown). Il sito ha già una pulizia di sicurezza.
5. **Verifiche sul sito live** (io non posso testare il widget): rebranding "Retell"→"Rispondoio" su header e menu launcher, reset chat, timing chiusura automatica (60s).
6. (Opzionale) sezione "Chi siamo / credibilità".

## 11. Note tecniche / trappole (per chi riprende)
- **Il mio ambiente NON può testare il widget Retell** (dominio `retellai.com` bloccato dal proxy → 403). **Anche `github.io` è bloccato dal proxy (403)**: non posso verificare il sito live via curl → mi affido agli screenshot dell'utente e a Playwright headless sul file locale.
- **Playwright headless funziona** sul file locale: `require('/opt/node22/lib/node_modules/playwright')`, `chromium.launch({executablePath:'/opt/pw-browsers/chromium'})`. Per screenshot fedeli forzare i reveal: `.reveal,.stagger,.stagger>*{opacity:1!important;transform:none!important}` (altrimenti le sezioni fuori viewport risultano vuote per via dell'IntersectionObserver).
- **Font Fraunces**: scaricato da Google Fonts (subset latin, opsz 144, wght 600-700), un unico woff2 variabile ~33KB, incorporato base64. Gli accenti italiani (à è é ì ò ù) sono nel range latin U+0000-00FF.
- **CSS `clamp()`**: servono spazi attorno a `+`/`-` (`1.3rem + 5.2vw`) o la regola è ignorata.
- **`scroll-margin-top:5.25rem`** su `.section`: evita che i titoli finiscano sotto la nav sticky (71px) arrivando da link ancora.
- **Spaziatura sezioni**: `--section-y:clamp(2.5rem,4.5vw,3.75rem)` (ridotto per eliminare i vuoti verticali doppi ai confini di sezione).
- **Mai modificare i text node di tutta la pagina**: il `<style>` contiene `*` e altri caratteri; gli script del widget (clean/rebrand) sono **scoped solo al widget/shadow root**.
- **Read di `index.html` fallisce** se leggi tutto (file grande / righe base64): usare `offset`/`limit` o `grep`.

## 12. Cronologia commit di questa sessione (dal più recente)
- `a13c016` Checkout: rimosso "Totale primo anno"
- `8279087` Bottoni Basic/Standard blu + modale configuratore bundle con riepilogo
- `4f69356` Bordo arancione su tutte le card; mensile→minimo 3 mesi (Trimestrale)
- `6a31cfe` Bundle button → piani annuali; rimossa diagnostica temporanea
- `9e87fab` Header widget: logo "Retell" → "Rispondoio" (via `_headerBrand`)
- `ba5622d`/`d02b763` Diagnostica `?diag=1` (poi rimossa)
- `6d56714` Nascondi "Retell" anche se logo/SVG/link
- `67a9a91` Font Fraunces per i titoli + sezione chat speculare
- `b223fed` Fix vuoti tra sezioni + scroll-margin + badge Pro arancione
- `2b2db9b` Auto-close widget a 60s
- `9c2f203`/`f3eb3a8`/`9d7f05b` Rebranding widget "Retell"→"Rispondoio" (shadow DOM)
