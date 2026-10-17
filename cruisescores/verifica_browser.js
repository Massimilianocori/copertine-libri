// Controllo nel browser di Cruise Health Scores: 375 e 1280 px, tema chiaro e scuro; niente scorrimento orizzontale, niente errori JS,
// niente richieste fallite; la ricerca trova una nave; il pulsante del tema cambia tema. Screenshot nella cartella SHOT
// (variabile d'ambiente CHS_SCREENSHOT, altrimenti cruisescores/cache/screenshot/).
// Uso: node cruisescores/verifica_browser.js   (lo lancia anche python3 cruisescores/verifica.py --browser)
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const SITO = path.join(__dirname, 'sito');
const SHOT = process.env.CHS_SCREENSHOT || path.join(__dirname, 'cache', 'screenshot');
fs.mkdirSync(SHOT, { recursive: true });
const TIPI = { '.html': 'text/html; charset=utf-8', '.json': 'application/json', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2', '.xml': 'application/xml', '.txt': 'text/plain' };

function server() {
  return http.createServer((req, res) => {
    let p = decodeURIComponent(req.url.split('?')[0]);
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

function esiste(p) { return fs.existsSync(path.join(SITO, p, 'index.html')); }

function campione() {
  const anno = fs.readdirSync(path.join(SITO, 'years')).filter(d => /^\d{4}$/.test(d)).sort().pop();
  const pagine = ['/', '/ships/', '/cruise-lines/', '/rankings/', '/rankings/failed-inspections/', `/rankings/perfect-scores-${anno}/`,
    `/rankings/lowest-scores-${anno}/`, '/years/', `/years/${anno}/`, '/outbreaks/', '/how-cdc-cruise-ship-inspections-work/',
    '/methodology/', '/about/', '/contact/', '/privacy.html', '/does-not-exist/'];
  for (const s of ['norwegian-dawn', 'adventure-of-the-seas', 'carnival-breeze', 'wonder-of-the-seas', 'villa-vie-odyssey', 'msc-magnifica', 'balmoral'])
    if (esiste('ships/' + s)) pagine.push('/ships/' + s + '/');
  for (const c of ['carnival-cruise-line', 'royal-caribbean-international', 'viking', 'villa-vie-residences'])
    if (esiste('cruise-lines/' + c)) pagine.push('/cruise-lines/' + c + '/');
  return pagine;
}

const DA_FOTOGRAFARE = ['/', '/ships/norwegian-dawn/', '/ships/adventure-of-the-seas/', '/cruise-lines/carnival-cruise-line/', '/cruise-lines/', '/rankings/',
  '/outbreaks/', '/how-cdc-cruise-ship-inspections-work/', '/ships/msc-magnifica/', '/contact/'];

(async () => {
  const srv = server();
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const base = 'http://127.0.0.1:' + srv.address().port;
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const problemi = [];
  const pagine = campione();
  let n = 0;
  for (const [w, hgt] of [[375, 812], [1280, 900]]) {
    for (const tema of ['light', 'dark']) {
      const ctx = await browser.newContext({ viewport: { width: w, height: hgt }, colorScheme: tema, deviceScaleFactor: 1 });
      for (const p of pagine) {
        const page = await ctx.newPage();
        const errori = [];
        page.on('pageerror', e => errori.push('JS: ' + e.message));
        page.on('console', m => { if (m.type() === 'error' && !(p === '/does-not-exist/' && /404/.test(m.text()))) errori.push('console: ' + m.text()); });
        page.on('requestfailed', r => errori.push('richiesta fallita: ' + r.url()));
        page.on('response', r => { if (r.status() >= 400 && !(p === '/does-not-exist/' && r.url().endsWith(p))) errori.push(r.status() + ' ' + r.url()); });
        await page.goto(base + p, { waitUntil: 'networkidle' });
        await page.evaluate(() => document.fonts.ready);
        const larg = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
        if (larg.sw > larg.cw + 1) {
          const colpevoli = await page.evaluate(() => [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1)
            .slice(0, 4).map(e => e.tagName + '.' + e.className));
          errori.push(`scorrimento orizzontale ${larg.sw} > ${larg.cw}: ${colpevoli.join(', ')}`);
        }
        // elementi che escono dallo schermo anche dentro contenitori con overflow nascosto (testi lunghi, tabelle)
        const fuori = await page.evaluate(() => [...document.querySelectorAll('main *')].filter(e => {
          const r = e.getBoundingClientRect(); if (!r.width || e.closest('.hp,.skip,.sr')) return false;
          let a = e.parentElement; while (a) { const s = getComputedStyle(a); if (/(auto|scroll)/.test(s.overflowX)) return false; a = a.parentElement; }
          return r.right > document.documentElement.clientWidth + 1 || r.left < -1;
        }).slice(0, 3).map(e => e.tagName + '.' + e.className));
        if (fuori.length) errori.push('fuori dallo schermo: ' + fuori.join(', '));
        if (p === '/') {
          await page.fill('#q', 'wonder');
          await page.waitForSelector('.risultati a', { timeout: 5000 }).catch(() => errori.push('ricerca: nessun risultato per "wonder"'));
          const primo = await page.$eval('.risultati a', a => a.getAttribute('href')).catch(() => '');
          if (!primo.startsWith('/ships/')) errori.push('ricerca: primo risultato senza link a una nave: ' + primo);
          await page.fill('#q', 'carnival');
          await page.waitForTimeout(250);
          const r = await page.$$eval('.risultati a', a => a.length);
          if (r < 5) errori.push('ricerca: troppo pochi risultati per "carnival": ' + r);
          await page.fill('#q', 'zzzz');
          await page.waitForTimeout(250);
          const vuoto = await page.$eval('.risultati', e => e.textContent);
          if (!/No ship found/.test(vuoto)) errori.push('ricerca: manca il messaggio "No ship found"');
          await page.fill('#q', '');
          await page.click('[data-tema]');
          const t = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
          const atteso = tema === 'light' ? 'dark' : 'light';
          if (t !== atteso) errori.push(`pulsante tema: atteso ${atteso}, trovato ${t}`);
          await page.evaluate(() => { document.documentElement.removeAttribute('data-theme'); try { localStorage.removeItem('chs-theme'); } catch (e) {} });
        }
        if (DA_FOTOGRAFARE.includes(p)) {
          const nome = (p === '/' ? 'home' : p.replace(/\//g, '_').replace(/^_|_$/g, '')) + `-${w}-${tema}.png`;
          await page.screenshot({ path: path.join(SHOT, nome), fullPage: true });
          if (w === 375 || p === '/') await page.screenshot({ path: path.join(SHOT, 'top-' + nome), fullPage: false });
        }
        errori.forEach(e => problemi.push(`${w}px ${tema} ${p}: ${e}`));
        await page.close();
        n++;
      }
      await ctx.close();
    }
  }
  await browser.close();
  srv.close();
  console.log(`Playwright: ${n} caricamenti (${pagine.length} pagine × 2 larghezze × 2 temi). Screenshot in ${SHOT}`);
  if (problemi.length) {
    console.log(problemi.join('\n'));
    process.exit(1);
  }
  console.log('Browser: nessun problema.');
})();
