// Controllo nel browser di FloodCost: 390 e 1280 px, tema chiaro e scuro; niente scorrimento orizzontale, niente errori JS,
// niente richieste fallite; la ricerca trova uno ZIP; il pulsante del tema cambia tema. Screenshot in floodcost/cache/screenshot/.
// Uso: node floodcost/verifica_browser.js   (lo lancia anche python3 floodcost/verifica.py --browser)
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');
// Pubblicità Google AdSense (accesa dal 30/10/2026): le richieste ai server degli annunci ricevono una risposta vuota,
// così la prova non dipende da annunci esterni e da beacon interrotti; lo script e il suo indirizzo li controlla monetizzazione.py.
const PUBBLICITA = /^https:\/\/([\w-]+\.)*(googlesyndication\.com|doubleclick\.net|googleadservices\.com|adtrafficquality\.google|fundingchoicesmessages\.google\.com)\//;

const SITO = path.join(__dirname, 'sito');
const SHOT = path.join(__dirname, 'cache', 'screenshot');
fs.mkdirSync(SHOT, { recursive: true });
const TIPI = { '.html': 'text/html; charset=utf-8', '.json': 'application/json', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2', '.xml': 'application/xml', '.txt': 'text/plain' };

function server() {
  return http.createServer((req, res) => {
    let p = decodeURIComponent(req.url.split('?')[0]);
    if (p.endsWith('/')) p += 'index.html';
    const f = path.join(SITO, p);
    if (!f.startsWith(SITO) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) {
      res.writeHead(404, { 'Content-Type': 'text/html' });
      res.end(fs.readFileSync(path.join(SITO, '404.html')));
      return;
    }
    res.writeHead(200, { 'Content-Type': TIPI[path.extname(f)] || 'application/octet-stream' });
    res.end(fs.readFileSync(f));
  });
}

function campione() {
  const pagine = ['/', '/states/', '/flood-zones/', '/flood-zones/zone-ae/', '/flood-zones/zone-x/', '/methodology/', '/about/', '/contact/', '/privacy.html', '/does-not-exist/'];
  const stati = fs.readdirSync(SITO).filter(d => fs.existsSync(path.join(SITO, d, 'index.html')) && !['states', 'flood-zones', 'methodology', 'about', 'contact', 'zip', 'data', 'assets'].includes(d));
  for (const s of ['florida', 'texas', 'louisiana', 'vermont'].filter(x => stati.includes(x))) pagine.push('/' + s + '/');
  const fl = path.join(SITO, 'florida');
  if (fs.existsSync(fl)) {
    const c = fs.readdirSync(fl).filter(d => fs.statSync(path.join(fl, d)).isDirectory()).slice(0, 3);
    c.forEach(d => pagine.push('/florida/' + d + '/'));
  }
  const zips = fs.existsSync(path.join(SITO, 'zip')) ? fs.readdirSync(path.join(SITO, 'zip')) : [];
  ['33904', '77002', '70458'].concat(zips.slice(0, 2)).filter(z => zips.includes(z)).forEach(z => pagine.push('/zip/' + z + '/'));
  return [...new Set(pagine)];
}

(async () => {
  const srv = server();
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const base = 'http://127.0.0.1:' + srv.address().port;
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const problemi = [];
  const pagine = campione();
  let n = 0;
  for (const [w, hgt] of [[390, 844], [1280, 900]]) {
    for (const tema of ['light', 'dark']) {
      const ctx = await browser.newContext({ viewport: { width: w, height: hgt }, colorScheme: tema, deviceScaleFactor: 1 });
      await ctx.route(PUBBLICITA, r => r.fulfill({ status: 200, contentType: 'text/javascript', body: '' }));
      for (const p of pagine) {
        const page = await ctx.newPage();
        const errori = [];
        page.on('pageerror', e => errori.push('JS: ' + e.message));
        page.on('console', m => { if (m.type() === 'error' && !(p === '/does-not-exist/' && /404/.test(m.text()))) errori.push('console: ' + m.text()); });
        page.on('requestfailed', r => { if (!PUBBLICITA.test(r.url())) errori.push('richiesta fallita: ' + r.url()); });
        page.on('response', r => { if (r.status() >= 400 && !(p === '/does-not-exist/' && r.url().endsWith(p))) errori.push(r.status() + ' ' + r.url()); });
        await page.goto(base + p, { waitUntil: 'networkidle' });
        await page.evaluate(() => document.fonts.ready);
        const larg = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
        if (larg.sw > larg.cw + 1) {
          const colpevoli = await page.evaluate(() => [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1)
            .slice(0, 3).map(e => e.tagName + '.' + e.className));
          errori.push(`scorrimento orizzontale ${larg.sw} > ${larg.cw}: ${colpevoli.join(', ')}`);
        }
        if (p === '/') {
          await page.fill('#q', '339');
          await page.waitForSelector('.risultati a', { timeout: 5000 }).catch(() => errori.push('ricerca: nessun risultato per 339'));
          await page.fill('#q', 'harris');
          await page.waitForTimeout(300);
          const r = await page.$$eval('.risultati a', a => a.length);
          if (!r) errori.push('ricerca: nessun risultato per harris');
          await page.fill('#q', '');
          await page.click('[data-tema]');
          const t = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
          const atteso = tema === 'light' ? 'dark' : 'light';
          if (t !== atteso) errori.push(`pulsante tema: atteso ${atteso}, trovato ${t}`);
          await page.evaluate(() => { document.documentElement.removeAttribute('data-theme'); try { localStorage.removeItem('fc-theme'); } catch (e) {} });
        }
        const nome = (p === '/' ? 'home' : p.replace(/\//g, '_').replace(/^_|_$/g, '')) + `-${w}-${tema}.png`;
        if (['/', '/florida/', '/flood-zones/zone-ae/', '/zip/33904/', '/methodology/', '/states/'].includes(p) || p.startsWith('/florida/') && p.split('/').length === 4 && !fs.existsSync(path.join(SHOT, 'contea-' + w + '-' + tema + '.png')))
          await page.screenshot({ path: path.join(SHOT, p.startsWith('/florida/') && p !== '/florida/' ? 'contea-' + w + '-' + tema + '.png' : nome), fullPage: true });
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
