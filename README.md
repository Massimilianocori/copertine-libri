# Rispondo — Landing page

Sito dell'assistente vocale AI **Rispondoio**: sito statico (homepage
`index.html`, pagine per settore in `per/`, file condivisi in `assets/`).
Nessuna build, nessun backend: il modulo di attivazione usa Netlify Forms.
Piano del business e decisioni aperte: vedi `PIANO.md`.

> **Nota sul nome:** "Rispondo" è un nome temporaneo. È sostituibile ovunque
> con un semplice *find-and-replace* della parola `Rispondo` in `index.html`.

---

## Come vedere la pagina sul tuo computer

Essendo un solo file, basta aprirlo nel browser:

1. Scarica `index.html` (dal repo su GitHub → file → **Download raw file**).
2. **Doppio clic** sul file: si apre in Safari/Chrome.

Oppure da Terminale (Mac):

```bash
git clone https://github.com/Massimilianocori/copertine-libri.git
cd copertine-libri
git checkout claude/script-explanation-structure-eefj7y
open index.html
```

Vedrai tutto il design. ⚠️ La **chiamata vocale demo non parte da un file
locale**: Retell richiede un dominio autorizzato (vedi sotto).

---

## Come mettere la pagina online (3 modi)

### Modo A — Netlify Drop (il più veloce, zero configurazione)

1. Vai su **https://app.netlify.com/drop**
2. Trascina **l'intera cartella** del sito nella pagina (non solo `index.html`).
3. In pochi secondi ottieni un indirizzo tipo `https://<nome>.netlify.app`.

Il file `netlify.toml` è già incluso: se preferisci collegare l'intero repo
a Netlify (deploy automatico a ogni push), funziona senza altre impostazioni.

### Modo B — GitHub Pages (automatico, a ogni modifica)

Il repo include già il workflow `.github/workflows/deploy.yml`.

1. Su GitHub: **Settings → Pages → Build and deployment → Source:
   "GitHub Actions"**.
2. Fai un push (o avvia il workflow manualmente da **Actions → Deploy sito su
   GitHub Pages → Run workflow**).
3. Il sito sarà online a:
   **https://massimilianocori.github.io/copertine-libri/**

### Modo C — Vercel

1. Su **https://vercel.com** → *Add New → Project* → importa questo repo.
2. Nessuna configurazione: `vercel.json` è già incluso. *Deploy*.

---

## Attivare la demo vocale (Retell)

La demo usa il widget vocale ufficiale di Retell (un solo tag `<script>`,
senza backend). Chiavi già inserite in fondo a `index.html`:

- **Public Key:** `public_key_30f48a75179b4474a40e7`
- **Voice Agent ID:** `agent_238b916f761b4882738071d0b5`

Per farla funzionare online:

1. **Metti il sito online** (Modo A, B o C): ti serve un dominio pubblico.
2. Nel **pannello Retell**, autorizza quel dominio per la chiave pubblica.
3. (Consigliato in produzione) Abilita **reCAPTCHA v3** sulla chiave pubblica
   per proteggere le chiamate demo dagli abusi.

> Se online comparisse una chat testuale invece della sola voce, verifica nel
> pannello Retell che l'agente collegato sia un **voice agent** e, se serve,
> incolla lo snippet di embed esatto generato da Retell (io lo allineo).

---

## Struttura del progetto

```
index.html                     Homepage (modulo attivazione + calcolatore inclusi)
per/                           Pagine per settore (GENERATE, non modificare a mano)
assets/rispondoio-lead.*       Modulo di attivazione e calcolatore (condivisi)
assets/rispondoio-settori.css  Stili delle pagine per settore
assets/rispondoio.css          CSS estratto da index.html (GENERATO)
privacy.html                   Informativa privacy
sitemap.xml, robots.txt        SEO (GENERATI)
strumenti/settori.py           Testi delle pagine per settore
strumenti/genera_pagine.py     Rigenera per/, assets/rispondoio.css, sitemap
netlify.toml / vercel.json     Config hosting
.github/workflows/deploy.yml   Deploy automatico su GitHub Pages
copertina.py                   Script Python separato (non legato al sito)
```

Dopo ogni modifica a `index.html` o a `strumenti/settori.py`:

```bash
python3 strumenti/genera_pagine.py
```

### Modulo di attivazione (Netlify Forms)

Le richieste arrivano solo se il sito è pubblicato su **Netlify**: in Netlify →
Forms attiva *Enable form detection*, poi in *Form notifications* aggiungi
l'email dove ricevere le richieste. Su altri hosting il modulo apre un'email
già compilata verso io@rispondoio.net.

---

## Checklist prima del lancio

- [ ] Scegliere il nome definitivo e sostituire `Rispondo`
- [ ] Verificare la disponibilità del dominio (`.it`, `.ai`, `.io`)
- [ ] Mettere il sito online su Netlify e autorizzare il dominio in Retell
- [ ] Attivare Netlify Forms e la notifica email delle richieste
- [ ] Aggiungere P.IVA e dati legali nel footer, rivedere `privacy.html`
- [ ] Abilitare reCAPTCHA v3 sulla chiave pubblica
- [ ] Far verificare a un legale le clausole di recesso dei piani con vincolo
