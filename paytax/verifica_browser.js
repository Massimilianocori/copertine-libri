// Controllo nel browser di Payroll Tax by State: 375 e 1280 px, tema chiaro e scuro; niente scorrimento orizzontale, niente errori JS,
// niente richieste fallite; il calcolatore dà i numeri attesi (calcolati con motore.py e passati da verifica.py in CASI_CALC);
// il pulsante del tema cambia tema; il caso ACT a anno parziale non viene calcolato. Screenshot in paytax/cache/screenshot/.
// Uso: python3 paytax/verifica.py --browser   (oppure: node paytax/verifica_browser.js, con i casi di default)
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');
// Pubblicità e contatore: risposta vuota, così la prova non dipende da servizi esterni (lo script AdSense lo controlla monetizzazione.py)
const ESTERNI = /^https:\/\/([\w-]+\.)*(googlesyndication\.com|doubleclick\.net|googleadservices\.com|adtrafficquality\.google|fundingchoicesmessages\.google\.com|gc\.zgo\.at|goatcounter\.com)\//;

const SITO = path.join(__dirname, 'sito');
const SHOT = path.join(__dirname, 'cache', 'screenshot');
fs.mkdirSync(SHOT, { recursive: true });
const TIPI = { '.html': 'text/html; charset=utf-8', '.json': 'application/json', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2', '.xml': 'application/xml', '.txt': 'text/plain' };
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
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const problemi = [];
  const tutte = pagine();
  let n = 0;
  for (const [w, hgt] of [[375, 812], [1280, 900]]) {
    for (const tema of ['light', 'dark']) {
      const ctx = await browser.newContext({ viewport: { width: w, height: hgt }, colorScheme: tema, deviceScaleFactor: 1 });
      await ctx.route(ESTERNI, r => r.fulfill({ status: 200, contentType: 'text/javascript', body: '' }));
      for (const p of tutte) {
        const page = await ctx.newPage();
        const errori = [];
        page.on('pageerror', e => errori.push('JS: ' + e.message));
        page.on('console', m => { if (m.type() === 'error' && !(p === '/does-not-exist/' && /404/.test(m.text()))) errori.push('console: ' + m.text()); });
        page.on('requestfailed', r => { if (!ESTERNI.test(r.url())) errori.push('richiesta fallita: ' + r.url()); });
        page.on('response', r => { if (r.status() >= 400 && !(p === '/does-not-exist/' && r.url().endsWith(p))) errori.push(r.status() + ' ' + r.url()); });
        await page.goto(base + p, { waitUntil: 'networkidle' });
        await page.evaluate(() => document.fonts.ready);
        const larg = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
        if (larg.sw > larg.cw + 1) {
          const colpevoli = await page.evaluate(() => [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1)
            .slice(0, 4).map(e => e.tagName + '.' + e.className));
          errori.push(`scorrimento orizzontale ${larg.sw} > ${larg.cw}: ${colpevoli.join(', ')}`);
        }
        // testo leggibile: nessun testo più piccolo di 11px
        const piccoli = await page.evaluate(() => [...document.querySelectorAll('main *')].filter(e => e.childNodes.length && [...e.childNodes].some(c => c.nodeType === 3 && c.textContent.trim()) &&
          parseFloat(getComputedStyle(e).fontSize) < 11 && e.offsetParent !== null).slice(0, 3).map(e => e.tagName + ':' + e.textContent.trim().slice(0, 30)));
        if (piccoli.length) errori.push('testo sotto 11px: ' + piccoli.join(' | '));
        if (tema === 'light' && w === 375 || p === '/' || p === '/calculator/' || p === '/act/') {
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
  // calcolatore: casi passati da verifica.py (numeri attesi dal motore Python)
  const ctx = await browser.newContext({ viewport: { width: 375, height: 812 } });
  await ctx.route(ESTERNI, r => r.fulfill({ status: 200, contentType: 'text/javascript', body: '' }));
  const page = await ctx.newPage();
  for (const c of CASI) {
    await page.goto(base + c.pagina, { waitUntil: 'networkidle' });
    await page.click('[data-azzera]');
    for (const [k, v] of Object.entries(c.salari)) await page.fill(`[data-calc] input[name="${k}"]`, String(v));
    await page.fill('[data-calc] input[name="giorni"]', String(c.giorni));
    if (c.rv) await page.check('[data-calc] input[name="rv"]');
    if (c.rq) await page.check('[data-calc] input[name="rq"]');
    await page.dispatchEvent('[data-calc] input[name="giorni"]', 'input');
    const tot = await page.textContent('[data-out] .tot .main b').catch(() => null);
    const nonCalc = await page.$$eval('[data-out] td', tds => tds.some(t => t.textContent.trim() === 'not calculated'));
    if (tot !== c.atteso) problemi.push(`calcolatore ${c.pagina} ${JSON.stringify(c.salari)} giorni ${c.giorni}: totale «${tot}» invece di «${c.atteso}»`);
    if (!!c.non_calcolato !== nonCalc) problemi.push(`calcolatore ${c.pagina}: riga "not calculated" ${nonCalc ? 'presente' : 'assente'} (attesa ${!!c.non_calcolato})`);
    const etichetta = await page.textContent('[data-out] .tot .main span').catch(() => '');
    if (!!c.non_calcolato !== /excludes ACT/.test(etichetta || '')) problemi.push(`calcolatore ${c.pagina}: etichetta del totale «${etichetta}» (ACT non calcolato: ${!!c.non_calcolato})`);
    const ricavi = await page.$eval('[data-out] tfoot .solo-m', e => getComputedStyle(e).display !== 'none' && e.textContent.includes('wages')).catch(() => false);
    if (!ricavi) problemi.push(`calcolatore ${c.pagina}: a 375 px la riga Total non mostra i salari`);
    const url = page.url();
    for (const k of Object.keys(c.salari)) if (!url.includes(k + '=')) problemi.push(`calcolatore ${c.pagina}: il link non contiene ${k}`);
  }
  // collegamento condivisibile: la pagina aperta con i parametri ricalcola lo stesso totale
  if (CASI.length) {
    const c = CASI[0];
    const q = new URLSearchParams(Object.entries(c.salari).map(([k, v]) => [k, String(v)])).toString();
    await page.goto(base + c.pagina + '?' + q + (c.giorni < 365 ? '&d=' + c.giorni : ''), { waitUntil: 'networkidle' });
    const tot = await page.textContent('[data-out] .tot .main b');
    if (tot !== c.atteso) problemi.push(`link condiviso: totale «${tot}» invece di «${c.atteso}»`);
  }
  // tema: il pulsante cambia data-theme
  await page.goto(base + '/', { waitUntil: 'networkidle' });
  const prima = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  await page.click('[data-tema]');
  const dopo = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  if (prima === dopo) problemi.push('il pulsante del tema non cambia i colori');
  await ctx.close();
  await browser.close();
  srv.close();
  console.log(`Browser: ${n} viste (${tutte.length} pagine × 375/1280 px × chiaro/scuro), ${CASI.length} casi del calcolatore; screenshot in ${SHOT}`);
  if (problemi.length) {
    console.log(problemi.length + ' PROBLEMI:\n - ' + problemi.slice(0, 60).join('\n - '));
    process.exit(1);
  }
})();
