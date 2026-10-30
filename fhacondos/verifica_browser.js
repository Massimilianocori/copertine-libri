// Controllo nel browser di FHA Approved Condos: 375 e 1280 px, tema chiaro e scuro; niente scorrimento orizzontale, niente errori JS,
// niente richieste fallite; la ricerca trova un CAP, una città e un nome; il filtro delle tabelle funziona; il pulsante del tema cambia tema.
// Screenshot in fhacondos/cache/screenshot/ (oppure nella cartella della variabile SHOT_DIR).
// Uso: node fhacondos/verifica_browser.js   (lo lancia anche python3 fhacondos/verifica.py --browser)
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');
// Pubblicità Google AdSense (accesa dal 30/10/2026): le richieste ai server degli annunci ricevono una risposta vuota,
// così la prova non dipende da annunci esterni e da beacon interrotti; lo script e il suo indirizzo li controlla monetizzazione.py.
const PUBBLICITA = /^https:\/\/([\w-]+\.)*(googlesyndication\.com|doubleclick\.net|googleadservices\.com|adtrafficquality\.google|fundingchoicesmessages\.google\.com)\//;

const SITO = path.join(__dirname, 'sito');
const SHOT = process.env.SHOT_DIR || path.join(__dirname, 'cache', 'screenshot');
fs.mkdirSync(SHOT, { recursive: true });
const TIPI = { '.html': 'text/html; charset=utf-8', '.json': 'application/json', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2', '.xml': 'application/xml', '.txt': 'text/plain' };

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

function sottocartelle(d) {
  const p = path.join(SITO, d);
  return fs.existsSync(p) ? fs.readdirSync(p).filter(x => fs.existsSync(path.join(p, x, 'index.html'))) : [];
}

function campione() {
  const pagine = ['/', '/states/', '/is-my-condo-fha-approved/', '/condo-not-fha-approved/', '/fha-vs-va-vs-warrantable-condos/',
    '/methodology/', '/about/', '/contact/', '/privacy.html', '/does-not-exist/'];
  for (const s of ['virginia', 'california', 'florida', 'colorado', 'alaska', 'louisiana', 'puerto-rico', 'district-of-columbia'])
    if (fs.existsSync(path.join(SITO, s, 'index.html'))) pagine.push('/' + s + '/');
  for (const [s, n] of [['virginia', 3], ['california', 3], ['maryland', 2], ['colorado', 2]])
    sottocartelle(s).slice(0, n).forEach(d => pagine.push('/' + s + '/' + d + '/'));
  for (const extra of ['/virginia/fairfax-county/', '/virginia/alexandria-city/', '/virginia/alexandria/'])
    if (fs.existsSync(path.join(SITO, extra, 'index.html'))) pagine.push(extra);
  return [...new Set(pagine)];
}

const SCATTI = { '/': 'home', '/states/': 'stati', '/virginia/': 'stato-virginia', '/florida/': 'stato-florida', '/louisiana/': 'stato-louisiana',
  '/virginia/fairfax-county/': 'contea-fairfax', '/virginia/alexandria/': 'citta-alexandria', '/is-my-condo-fha-approved/': 'guida-controllo',
  '/condo-not-fha-approved/': 'guida-non-approvato', '/fha-vs-va-vs-warrantable-condos/': 'guida-confronto', '/methodology/': 'metodologia',
  '/contact/': 'contatti', '/does-not-exist/': '404' };

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
      await ctx.route(PUBBLICITA, r => r.fulfill({ status: 200, contentType: 'text/javascript', body: '' }));
      for (const p of pagine) {
        const page = await ctx.newPage();
        const errori = [];
        page.on('pageerror', e => errori.push('JS: ' + e.message));
        page.on('console', m => { if (m.type() === 'error' && !(p === '/does-not-exist/' && /404/.test(m.text()))) errori.push('console: ' + m.text()); });
        page.on('requestfailed', r => { if (!PUBBLICITA.test(r.url())) errori.push('richiesta fallita: ' + r.url()); });
        page.on('response', r => { if (r.status() >= 400 && !(p === '/does-not-exist/' && r.url().endsWith(p))) errori.push(r.status() + ' ' + r.url()); });
        const resp = await page.goto(base + p, { waitUntil: 'networkidle' });
        if (p !== '/does-not-exist/' && resp.status() !== 200) errori.push('stato HTTP ' + resp.status());
        await page.evaluate(() => document.fonts.ready);
        const larg = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
        if (larg.sw > larg.cw + 1) {
          const colpevoli = await page.evaluate(() => [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1)
            .slice(0, 3).map(e => e.tagName + '.' + e.className));
          errori.push(`scorrimento orizzontale ${larg.sw} > ${larg.cw}: ${colpevoli.join(', ')}`);
        }
        if (p === '/') {
          for (const [q, atteso] of [['22003', 'CAP'], ['Denver', 'città'], ['harbor', 'nome']]) {
            await page.fill('#q', q);
            await page.waitForSelector('.risultati a', { timeout: 5000 }).catch(() => errori.push(`ricerca: nessun risultato per ${q} (${atteso})`));
            await page.waitForTimeout(150);
            const r = await page.$$eval('.risultati a', a => a.length);
            if (!r) errori.push(`ricerca: nessun risultato per ${q}`);
          }
          if (w === 375 && tema === 'light') {
            await page.fill('#q', 'Denver');
            await page.waitForTimeout(200);
            await page.screenshot({ path: path.join(SHOT, `home-ricerca-${w}-${tema}.png`) });
            // il primo risultato deve portare a una pagina esistente con la riga evidenziata
            const href = await page.$eval('.risultati a:not([href$="/"])', a => a.getAttribute('href')).catch(() => null);
            if (href) {
              const r2 = await page.goto(base + '/' + href.replace(/^\.\//, ''), { waitUntil: 'networkidle' });
              const id = href.split('#')[1];
              const c = await page.$('#' + id);
              if (r2.status() !== 200 || !c) errori.push('ricerca: il risultato non porta alla riga ' + href);
              await page.goto(base + p, { waitUntil: 'networkidle' });
            }
          }
          await page.fill('#q', '');
          await page.click('[data-tema]');
          const t = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
          const att = tema === 'light' ? 'dark' : 'light';
          if (t !== att) errori.push(`pulsante tema: atteso ${att}, trovato ${t}`);
          await page.evaluate(() => { document.documentElement.removeAttribute('data-theme'); try { localStorage.removeItem('ac-theme'); } catch (e) {} });
        }
        if (await page.$('[data-filtro="t-a"]')) {
          const tot = await page.$$eval('#t-a tbody tr', r => r.length);
          const primo = await page.$eval('#t-a tbody tr td.cz', td => td.textContent.trim());
          await page.fill('[data-filtro="t-a"]', primo);
          const vis = await page.$$eval('#t-a tbody tr', r => r.filter(x => !x.hidden).length);
          if (!(vis >= 1 && vis <= tot)) errori.push(`filtro: ${vis} righe visibili su ${tot} per ${primo}`);
          await page.fill('[data-filtro="t-a"]', '');
        }
        if (SCATTI[p]) await page.screenshot({ path: path.join(SHOT, `${SCATTI[p]}-${w}-${tema}.png`), fullPage: true });
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
