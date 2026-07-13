# Rispondoio — Handoff / Punto della situazione

Documento di continuità per riprendere il lavoro in una nuova chat.
Ultimo aggiornamento: 2026-07-13.

---

## 1. Cos'è il progetto
Landing page **premium, single-page, in italiano** per **Rispondoio**: assistente
**vocale + chat AI** che risponde a telefonate e messaggi delle piccole attività,
prende appuntamenti e li scrive in agenda. Integra il widget **Retell** (voce + chat).

- **Un solo file**: `index.html` (HTML + CSS + JS inline, font e widget via CDN). Nessun backend, nessuna build.
- **Dominio futuro**: `rispondoio.ai` (non ancora attivo).
- **Sito live attuale**: https://massimilianocori.github.io/copertine-libri/
- **Branch di sviluppo**: `claude/script-explanation-structure-eefj7y`
- **Repo**: `Massimilianocori/copertine-libri`

## 2. Brand
- **Nome**: Rispondoio (prima era "Rispondo").
- **Logo**: anello teal + barre onda-audio arancioni, ricostruito come **SVG inline**
  (nav, footer, favicon). Teal `#0F7A85` (nel footer scuro `#1FA5B0`), arancione `#F5822A`.
  Se il cliente fornisce il PNG originale si può sostituire.
- **Colori**: voce = blu `--accent:#0A6DD8`; chat = verde `#0FA968` / `#0B8A54`.
- **Font**: **Arimo** (clone Helvetica) incorporato come base64 `@font-face` (pesi 400/700).
- **Contatti**: email `io@rispondoio.net` (mailto attivo). Telefono: segnaposto "Presto disponibile" (numero non ancora disponibile).

## 3. Retell (chiavi e agenti)
- **Public key**: `public_key_30f48a75179b4474a40e7`
- **Voice agent**: `agent_238b916f761b4882738071d0b5`
- **Chat agent**: `agent_003d2188ae48906eb0bf581cd7`
- Widget: `<script id="retell-widget" src="https://dashboard.retellai.com/retell-widget-v2.js" type="module" data-*>` in fondo a `index.html`.
- Dominio autorizzato in Retell per far funzionare voce **e** chat (la chat funziona già live).

## 4. Struttura della pagina (ordine sezioni)
1. **Hero** (voce, blu) — call-card demo con sfera colorata rotante
2. Strip differenziale (trust)
3. **Settori**
4. **Come funziona** (3 step)
5. **Prezzi · Assistente vocale** (blu) — 3 piani
6. **Chat AI** (verde) — sezione gemella della hero, chat-card demo
7. **Prezzi · Chat AI** (verde) — piano Chat + bundle
8. **CTA finale** (scura)
9. **Contatti** (email + telefono)
10. Footer

Le sezioni voce (blu) e chat (verde) sono **gemelle**: stessa struttura, cambia solo il colore.

## 5. Prezzi (IVA esclusa)
Toggle Mensile/Annuale in **due punti** (voce + chat) sincronizzati sulla stessa modalità.

**Voce:**
| Piano | Mensile | Annuale | Minuti | Attivazione (annuale) |
|---|---|---|---|---|
| Basic | 79 | 67 | 200 | 149 → 74,50 (−50%) |
| Standard | 129 | 109 | 500 | gratis |
| Pro (featured) | 229 | 189 | 1.000 | gratis |
Extra: 100 minuti a € 25. Annuale con impegno 12 mesi.

**Chat AI:** 69/mese (annuale 57), attivazione € 99.
**Bundle voce+chat** (voce annuale + chat annuale): chat a **€ 39/mese**, **attivazione gratuita**, risparmio ~€ 360/anno.

I pulsanti dei piani ora mostrano solo un toast ("checkout in arrivo"): **da collegare ai link di pagamento (Stripe)**.

## 6. Comportamenti JS del widget (già implementati)
Tutto in un IIFE in fondo a `index.html`:
- **Apertura widget** dai pulsanti "Prova la voce" / "Prova la chat": clicca il **launcher fisso** del widget (non controlli interni), riprova finché è montato.
- **Chat sempre pulita**: on-load cancella lo storage Retell; **alla chiusura del pannello ricrea il widget da zero** (rimuove i nodi creati dal widget via diff col body originale + reinietta lo `<script>` con cache-bust) → riapertura = chat vuota e scrivibile.
- **Chiusura automatica**: quando l'assistente conferma l'appuntamento (o la chat termina), il pannello si chiude da solo dopo ~5 s.
- **Niente asterischi**: `cleanRetellText()` rimuove il markdown (`**`, `*`, elenchi) dai messaggi. Scope **solo dentro il widget** (mai la pagina).
- **Rebranding**: `rebrandRetell()` sostituisce ogni "Retell"/"RetellAI" con **"Rispondoio"** (testo + attributi) e nasconde i loghi Retell + il "Powered by". "Retell" non deve mai comparire.

## 7. Deploy
- GitHub Actions `.github/workflows/deploy.yml`: trigger **solo su `main`**, `concurrency: cancel-in-progress:false` (evita i "cancelled").
- **Per pubblicare**: `git push origin <branch>:main` (fast-forward del tip del branch su main). La CDN di Pages impiega ~10-15 min; usare `?v=N` per saltare la cache.
- Sviluppo sempre su `claude/script-explanation-structure-eefj7y`, poi push su main.

## 8. Da fare (aperti)
1. **Email istantanea**: oggi l'email dell'appuntamento arriva dopo qualche minuto → renderla istantanea. È lato **Make** (probabile trigger a polling / step schedulato): passare a un flusso **webhook-triggered**. Serve accesso agli scenari Make (MCP Make disponibile).
2. **Prenotazione reale della chat**: verificare che l'**agente chat** abbia le stesse **function/tool → webhook** dell'agente voce (probabilmente configurate solo sul voce). Catena: Retell function → webhook Make → Google Calendar + email.
3. **Asterischi alla fonte**: nel prompt dell'agente **chat** su Retell aggiungere l'istruzione di rispondere in **testo semplice, senza markdown/asterischi/elenchi** (il testo pronto è stato fornito in chat). Il sito ha già una pulizia di sicurezza.
4. **Pagamenti**: collegare i pulsanti "Inizia con…", "Aggiungi Chat AI", "Attiva il bundle" ai **link Stripe**.
5. **Verifiche sul sito live** (io non posso testare il widget dal mio ambiente): reset chat alla riapertura, timing della chiusura automatica (~5 s, regolabile), rebranding "Retell"→"Rispondoio" su voce e chat.
6. (Opzionale, dal brief) sezione "Chi siamo / credibilità"; il claim hero non veritiero è già stato corretto.

## 9. Note tecniche / trappole (per chi riprende)
- **Il widget Retell NON è testabile dal sandbox** (dominio retellai.com bloccato dal proxy). Verifiche del widget → affidarsi agli screenshot dell'utente. Il resto è testabile con Playwright headless.
- **Playwright**: `require('/opt/node22/lib/node_modules/playwright')`, `executablePath:'/opt/pw-browsers/chromium'`.
- **CSS `clamp()`**: servono **spazi** attorno a `+`/`-` (`1.3rem + 5.4vw`) o la regola è invalida e ignorata.
- **Mai modificare i text node di tutta la pagina**: il `<style>` contiene `*` e altri caratteri; uno script che li altera corrompe il CSS e azzera le variabili (`--accent` ecc.). Gli script del widget (clean/rebrand) sono **scoped solo al widget**.
- **`.fluid svg{max-width:none}`** serve perché il reset globale `svg{max-width:100%}` altrimenti "incornicia" l'effetto fluido.
- **Read di `index.html` fallisce** (file grande / righe base64 lunghe): usare `offset`/`limit` o `grep`.
- La sfera colorata nella call-card ruota via `@keyframes orbspin` (gradiente conico multicolore ad alto contrasto).

## 10. Cronologia commit principali (branch)
- Logo + sezione chat proporzionata + Contatti
- Fix apertura widget dai pulsanti (launcher fisso)
- Sezioni chat/voce uniformate + piano Chat + bundle + rimozione markdown + fix corruzione CSS
- Split prezzi: voce sotto la parte blu, chat sotto la parte verde
- Chat pulita alla riapertura + chiusura automatica dopo conferma
- Rebranding "Retell" → "Rispondoio" + hide loghi Retell
