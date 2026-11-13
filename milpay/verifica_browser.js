// Controllo nel browser di Military Pay Chart: tutte le pagine a 375 e 1280 px (chiaro; home, calcolatore ed E-5 anche scuro):
// niente scorrimento orizzontale della pagina, niente errori JS, niente richieste fallite, testo >= 11 px.
// Ogni richiesta che non è del server locale viene bloccata (pubblicità e contatore compresi).
// Calcolatore: casi passati da verifica.py in CASI_CALC (numeri attesi dal calcolo Python). Screenshot in milpay/cache/screenshot/.
// Uso: python3 milpay/verifica.py --browser
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const SITO = path.join(__dirname, 'sito');
const SHOT = path.join(__dirname, 'cache', 'screenshot');
fs.mkdirSync(SHOT, { recursive: true });
const TIPI = { '.html': 'text/html; charset=utf-8', '.json': 'application/json', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.xml': 'application/xml', '.txt': 'text/plain' };
const CASI = process.env.CASI_CALC ? JSON.parse(process.env.CASI_CALC) : [];

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

function pagine() {
  const p = ['/'];
  for (const d of fs.readdirSync(SITO)) if (fs.existsSync(path.join(SITO, d, 'index.html'))) p.push('/' + d + '/');
  p.push('/does-not-exist/');
  return p;
}

(async () => {
  const srv = server();
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const base = 'http://127.0.0.1:' + srv.address().port;
  const locale = u => u.startsWith(base);
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const problemi = [];
  const tutte = pagine();
  let n = 0, bloccate = 0;
  for (const [w, hgt] of [[375, 812], [1280, 900]]) {
    for (const tema of ['light', 'dark']) {
      const ctx = await browser.newContext({ viewport: { width: w, height: hgt }, colorScheme: tema, deviceScaleFactor: 1 });
      await ctx.route(u => !locale(u.toString()), r => { bloccate++; return r.abort(); });
      const elenco = tema === 'light' ? tutte : ['/', '/calculator/', '/e-5/'];
      for (const p of elenco) {
        const page = await ctx.newPage();
        const errori = [];
        page.on('pageerror', e => errori.push('JS: ' + e.message));
        page.on('console', m => { if (m.type() === 'error' && !/ERR_FAILED|404/.test(m.text())) errori.push('console: ' + m.text()); });
        page.on('requestfailed', r => { if (locale(r.url())) errori.push('richiesta fallita: ' + r.url()); });
        page.on('response', r => { if (r.status() >= 400 && !(p === '/does-not-exist/' && r.url().endsWith(p))) errori.push(r.status() + ' ' + r.url()); });
        await page.goto(base + p, { waitUntil: 'load' });
        const larg = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
        if (larg.sw > larg.cw + 1) {
          const colpevoli = await page.evaluate(() => [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1 && !e.closest('.tab'))
            .slice(0, 4).map(e => e.tagName + '.' + e.className));
          errori.push(`scorrimento orizzontale ${larg.sw} > ${larg.cw}: ${colpevoli.join(', ')}`);
        }
        const piccoli = await page.evaluate(() => [...document.querySelectorAll('main *')].filter(e => [...e.childNodes].some(c => c.nodeType === 3 && c.textContent.trim()) &&
          parseFloat(getComputedStyle(e).fontSize) < 11 && e.offsetParent !== null).slice(0, 3).map(e => e.tagName + ':' + e.textContent.trim().slice(0, 30)));
        if (piccoli.length) errori.push('testo sotto 11px: ' + piccoli.join(' | '));
        if (['/', '/calculator/', '/e-5/', '/2027-pay-raise/'].includes(p)) {
          const nome = (p === '/' ? 'home' : p.replace(/\//g, '')) + `-${w}-${tema}.png`;
          await page.screenshot({ path: path.join(SHOT, nome), fullPage: true });
        }
        if (errori.length) problemi.push(`${p} @${w}px ${tema}: ` + errori.join(' ; '));
        n++;
        await page.close();
      }
      await ctx.close();
    }
  }
  // calcolatore
  const ctx = await browser.newContext({ viewport: { width: 375, height: 812 } });
  await ctx.route(u => !locale(u.toString()), r => r.abort());
  const page = await ctx.newPage();
  page.on('pageerror', e => problemi.push('calcolatore JS: ' + e.message));
  await page.goto(base + '/calculator/', { waitUntil: 'load' });
  for (const c of CASI) {
    await page.selectOption('[data-calc] select[name=g]', c.g);
    await page.selectOption('[data-calc] select[name=y]', String(c.y));
    const out = (await page.textContent('[data-out]')) || '';
    for (const atteso of c.contiene) if (!out.includes(atteso)) problemi.push(`calcolatore ${c.g} col ${c.y}: manca «${atteso}» in «${out.slice(0, 160)}»`);
    if (!page.url().includes('g=' + c.g)) problemi.push(`calcolatore ${c.g}: il link non contiene la scelta`);
  }
  if (CASI.length) {
    const c = CASI[CASI.length - 1];
    await page.goto(base + '/calculator/?g=' + c.g + '&y=' + c.slug, { waitUntil: 'load' });
    const out = (await page.textContent('[data-out]')) || '';
    if (!out.includes(c.contiene[0])) problemi.push(`link condiviso ${c.g} ${c.slug}: manca «${c.contiene[0]}»`);
  }
  await page.goto(base + '/', { waitUntil: 'load' });
  const prima = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  await page.click('[data-tema]');
  const dopo = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  if (prima === dopo) problemi.push('il pulsante del tema non cambia i colori');
  await ctx.close();
  await browser.close();
  srv.close();
  console.log(`Browser: ${n} viste (${tutte.length} pagine a 375/1280 px, 3 anche in scuro), ${CASI.length} casi del calcolatore, ${bloccate} richieste esterne bloccate; screenshot in ${SHOT}`);
  if (problemi.length) {
    console.log(problemi.length + ' PROBLEMI:\n - ' + problemi.slice(0, 60).join('\n - '));
    process.exit(1);
  }
})();
