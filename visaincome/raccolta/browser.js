// Legge pagine ufficiali con Chromium (Playwright) e stampa un JSON {url: {http, testo, aggiornata}} su stdout.
// Serve a raccolta/opt.py: uscis.gov, ice.gov e studyinthestates.dhs.gov rispondono 403 alle richieste senza browser
// (protezione Akamai), ma si leggono normalmente con un browser vero.
// Uso: node visaincome/raccolta/browser.js URL [URL ...]
//   Un URL che finisce con "#fee=<id>" (pagina G-1055) seleziona quel modulo nel menu delle tariffe e restituisce il testo
//   della tabella che compare (id 97312 = I-765).
// Variabili: PW_MODULO (percorso di playwright, predefinito /opt/node-tools/node_modules/playwright),
//            PW_CHROMIUM (eseguibile, predefinito /opt/pw-browsers/chromium).
const { chromium } = require(process.env.PW_MODULO || '/opt/node-tools/node_modules/playwright');

(async () => {
  const b = await chromium.launch({ executablePath: process.env.PW_CHROMIUM || '/opt/pw-browsers/chromium' });
  const p = await b.newPage();
  const out = {};
  for (const u of process.argv.slice(2)) {
    const [base, frag] = u.split('#');
    try {
      const r = await p.goto(base, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await p.waitForTimeout(1500);
      let testo;
      if (frag && frag.startsWith('fee=')) {
        const id = frag.slice(4);
        await p.evaluate((id) => { jQuery('#form-fee-title').val(id).trigger('change'); }, id);
        await p.waitForTimeout(5000);
        testo = await p.evaluate(() => {
          const t = document.querySelector('main').innerText;
          const i = t.indexOf('Select a Form for Fee Information');
          return i >= 0 ? t.slice(i) : '';
        });
      } else {
        // textContent: comprende anche il testo dei riquadri chiusi (fisarmoniche) delle pagine USCIS
        testo = await p.evaluate(() => (document.querySelector('main') || document.body).textContent);
      }
      const aggiornata = await p.evaluate(() => {
        const t = document.body.innerText;
        const m = t.match(/Last Reviewed\/Updated:\s*(\d{2}\/\d{2}\/\d{4})/) || t.match(/Last updated:\s*([A-Z][a-z]+ \d{1,2}, \d{4})/) || t.match(/Updated:\s*(\d{2}\/\d{2}\/\d{4})/);
        return m ? m[1] : '';
      });
      out[u] = { http: r.status(), testo: testo.replace(/\s+/g, ' ').trim(), aggiornata };
    } catch (e) {
      out[u] = { http: 0, testo: '', errore: String(e.message || e).slice(0, 200) };
    }
  }
  await b.close();
  process.stdout.write(JSON.stringify(out));
})();
