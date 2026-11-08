// Controllo nel browser di Balcony Solar Europe: 375 e 1280 px, tema chiaro e scuro; niente scorrimento orizzontale, niente errori
// JS, niente richieste fallite; il calcolatore cambia i numeri quando si cambia città, montaggio e potenza e dà gli stessi valori
// della formula (calcola/fmt del file app.*.js); il pulsante del tema cambia tema; il menu del telefono si apre.
// Screenshot in solarebalcone/cache/screenshot/ (oppure nella cartella della variabile SHOT_DIR).
// Uso: node solarebalcone/verifica_browser.js   (lo lancia anche python3 solarebalcone/verifica.py --browser)
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');
// Pubblicità e contatore: risposta vuota, così la prova non dipende da servizi esterni (lo script AdSense lo controlla monetizzazione.py)
const ESTERNI = /^https:\/\/([\w-]+\.)*(googlesyndication\.com|doubleclick\.net|googleadservices\.com|adtrafficquality\.google|fundingchoicesmessages\.google\.com|zgo\.at|goatcounter\.com)\//;

const SITO = path.join(__dirname, 'sito');
const SHOT = process.env.SHOT_DIR || path.join(__dirname, 'cache', 'screenshot');
fs.mkdirSync(SHOT, { recursive: true });
const TIPI = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2', '.xml': 'application/xml', '.txt': 'text/plain' };

function server() {
  return http.createServer((req, res) => {
    let p = decodeURIComponent(req.url.split('?')[0].split('#')[0]);
    if (p.endsWith('/')) p += 'index.html';
    const f = path.join(SITO, p);
    if (!f.startsWith(SITO) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) {
      res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(fs.readFileSync(path.join(SITO, '404.html')));
      return;
    }
    res.writeHead(200, { 'Content-Type': TIPI[path.extname(f)] || 'application/octet-stream' });
    res.end(fs.readFileSync(f));
  });
}

function tutte() {
  const out = [];
  (function giro(d) {
    for (const x of fs.readdirSync(d)) {
      const f = path.join(d, x);
      if (fs.statSync(f).isDirectory()) { if (x !== 'assets') giro(f); }
      else if (x === 'index.html') out.push('/' + path.relative(SITO, d).split(path.sep).join('/') + (d === SITO ? '' : '/'));
    }
  })(SITO);
  return out.map(u => u.replace('//', '/')).concat(['/non-esiste/']);
}

(async () => {
  const srv = server().listen(0);
  const base = 'http://127.0.0.1:' + srv.address().port;
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const errori = [];
  const pagine = tutte();
  let viste = 0;
  for (const [w, scuro] of [[375, false], [375, true], [1280, false], [1280, true]]) {
    const ctx = await browser.newContext({ viewport: { width: w, height: 860 }, colorScheme: scuro ? 'dark' : 'light' });
    await ctx.route(ESTERNI, r => r.fulfill({ status: 200, contentType: 'text/javascript', body: '' }));
    const p = await ctx.newPage();
    p.on('pageerror', e => errori.push(`${w}${scuro ? ' scuro' : ''} ${p.url()}: errore JS ${e.message}`));
    p.on('requestfailed', r => errori.push(`${w} ${p.url()}: richiesta fallita ${r.url()}`));
    for (const u of pagine) {
      const r = await p.goto(base + u, { waitUntil: 'load' });
      if (u !== '/non-esiste/' && r.status() !== 200) errori.push(`${u}: HTTP ${r.status()}`);
      await p.evaluate(() => document.fonts.ready);
      const largo = await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
      if (largo > 0) errori.push(`${w}${scuro ? ' scuro' : ''} ${u}: scorrimento orizzontale di ${largo} px`);
      viste++;
      if (['/', '/it/', '/es/', '/fr/', '/it/fotovoltaico-balcone-roma/', '/es/normativa-placas-solares-balcon/', '/fr/panneau-solaire-balcon-paris/', '/non-esiste/'].includes(u)) {
        const nome = (u.replace(/\//g, '_') || '_') + `${w}${scuro ? '-scuro' : ''}.png`;
        await p.screenshot({ path: path.join(SHOT, nome), fullPage: true });
      }
    }
    // calcolatore: valori attesi dalla stessa formula, poi cambio città, montaggio e potenza
    for (const u of ['/it/', '/es/placas-solares-balcon-barcelona/', '/fr/']) {
      await p.goto(base + u);
      const ris = await p.evaluate(() => {
        const f = document.querySelector('[data-calc]'), D = JSON.parse(document.getElementById('calc-dati').textContent);
        const L = document.documentElement.lang, leggi = k => f.querySelector('[data-o=' + k + ']').textContent;
        const prova = [];
        const casi = [[D.citta[D.citta.length - 1].s, 'a90', 600], [D.citta[0].s, 'a35', 800]];
        for (const [s, m, w] of casi) {
          f.elements.citta.value = s; f.querySelector('input[value=' + m + ']').checked = true; f.elements.w.value = w;
          f.dispatchEvent(new Event('change', { bubbles: true }));
          const c = D.citta.filter(x => x.s === s)[0];
          const r = calcola(c[m], w, parseFloat(f.elements.quota.value), parseFloat(f.elements.prezzo.value), parseFloat(f.elements.kit.value));
          prova.push([leggi('prod'), fmt(r.prod, 0, L), leggi('eur'), fmt(r.eur, 0, L), leggi('anni'), fmt(r.anni, 1, L)]);
        }
        f.elements.w.value = 5000; f.dispatchEvent(new Event('input', { bubbles: true }));
        const oltre = !f.querySelector('[data-oltre]').hidden;
        return { prova, oltre };
      });
      for (const r of ris.prova) if (r[0] !== r[1] || r[2] !== r[3] || r[4] !== r[5]) errori.push(`${w} ${u}: calcolatore mostra ${r[0]}/${r[2]}/${r[4]} invece di ${r[1]}/${r[3]}/${r[5]}`);
      if (!ris.oltre) errori.push(`${w} ${u}: l'avviso sopra la soglia di potenza non compare`);
    }
    // tema e menu del telefono
    await p.goto(base + '/it/');
    const prima = await p.evaluate(() => getComputedStyle(document.body).backgroundColor);
    await p.click('[data-tema]');
    const dopo = await p.evaluate(() => getComputedStyle(document.body).backgroundColor);
    if (prima === dopo) errori.push(`${w}: il pulsante del tema non cambia lo sfondo`);
    if (w === 375) {
      await p.click('.nav-m summary');
      const vis = await p.isVisible('.nav-m nav a');
      if (!vis) errori.push('375: il menu del telefono non si apre');
    }
    await ctx.close();
  }
  await browser.close();
  srv.close();
  console.log(`Browser: ${viste} viste (${pagine.length} pagine × 375/1280 px × chiaro/scuro), calcolatore provato su 3 pagine; screenshot in ${SHOT}`);
  if (errori.length) { console.error(errori.slice(0, 40).join('\n')); process.exit(1); }
})();
