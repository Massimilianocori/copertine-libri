# Portfolio page A1 (Scrollcraft — placeholder)

Pagina di vendita per l'outreach A1 (AI UGC video ads per brand DTC). Sito statico, un file.

## Personalizzare (3 punti)
1. **Nome brand:** in `index.html` cambia il testo "Scrollcraft" (header, footer) e il `<title>`.
2. **Colore accento:** in `<style>`, variabile `--accent`.
3. **Email/form:** sostituisci `hello@scrollcraft.com` e l'`action` del form con un endpoint
   Formspree (gratis su formspree.io). Aggiungi il link Calendly se vuoi le call.

## Aggiungere i video campione
Metti i file in questa cartella come `1.mp4 … 5.mp4` (verticali 9:16). Gli slot si popolano da
soli (il placeholder sparisce quando il video carica). Aggiorna i testi in `figcaption`/`.ph`.

## Deploy
- **Netlify:** nuovo sito → base directory `digital-business/portfolio`, publish `.` → deploy.
- **Vercel:** nuovo progetto → root `digital-business/portfolio` (framework: Other/static).
- È indipendente dal sito copertine-libri nella root del repo.

Nota: usa Google Fonts (Inter) via CDN; tutto il resto è inline, nessun'altra dipendenza.
