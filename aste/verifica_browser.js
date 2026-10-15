// Controllo nel browser di Aste in Chiaro: 390 e 1280 px, tema chiaro e scuro; niente scorrimento orizzontale, niente errori JS,
// niente richieste fallite; pulsante del tema, filtri e ordinamento funzionanti; live.json (servito in locale al posto di GitHub)
// aggiorna i prezzi e nasconde le aste tolte. Screenshot di ogni tipo di pagina in aste/cache/screenshot/.
// Uso: node aste/verifica_browser.js   (lo lancia anche python3 aste/verifica.py --browser)
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const SITO = path.join(__dirname, 'sito');
const LIVE = path.join(__dirname, 'dati', 'live.json');
const SHOT = path.join(__dirname, 'cache', 'screenshot');
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

function dir(d) { return fs.existsSync(d) ? fs.readdirSync(d).filter(x => fs.statSync(path.join(d, x)).isDirectory()) : []; }

function campione() {
  // [percorso, tipo] per le schermate
  const p = [['/', 'home'], ['/citta/', 'indice-citta'], ['/auto-all-asta/', 'auto'], ['/guide/', 'guide'],
    ['/guide/come-funziona-asta-giudiziaria/', 'guida'], ['/guide/casa-occupata-all-asta/', 'guida2'], ['/metodologia/', 'metodo'],
    ['/chi-siamo/', 'chi-siamo'], ['/contatti/', 'contatti'], ['/privacy.html', 'privacy'], ['/pagina-inesistente/', '404']];
  const citta = dir(SITO).filter(d => fs.existsSync(path.join(SITO, d, 'index.html')) && !['citta', 'guide', 'metodologia', 'chi-siamo', 'contatti', 'auto-all-asta', 'assets'].includes(d));
  const scelte = ['roma', 'milano', 'napoli'].filter(c => citta.includes(c));
  // una città piccola (meno sotto-pagine)
  const piccola = citta.find(c => dir(path.join(SITO, c)).length === 0);
  scelte.forEach((c, i) => p.push(['/' + c + '/', i === 0 ? 'citta' : 'citta-' + c]));
  if (piccola) p.push(['/' + piccola + '/', 'citta-piccola']);
  const sub = scelte.length ? dir(path.join(SITO, scelte[0])) : [];
  const fascia = sub.find(d => d.startsWith('fino-a') || d.startsWith('da-') || d.startsWith('oltre'));
  const zona = sub.find(d => d.startsWith('zona-'));
  if (fascia) p.push(['/' + scelte[0] + '/' + fascia + '/', 'fascia']);
  if (zona) p.push(['/' + scelte[0] + '/' + zona + '/', 'zona']);
  return p;
}

(async () => {
  const srv = server();
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const base = 'http://127.0.0.1:' + srv.address().port;
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const problemi = [];
  const pagine = campione();
  // live.json di prova: più recente della pagina, con il primo lotto della home tolto e il secondo con prezzi nuovi
  const vero = JSON.parse(fs.readFileSync(LIVE, 'utf8'));
  const homeHtml = fs.readFileSync(path.join(SITO, 'index.html'), 'utf8');
  const idsHome = [...homeHtml.matchAll(/data-id="(\d+)"/g)].map(m => m[1]);
  const finto = JSON.parse(JSON.stringify(vero));
  finto.letto_il = new Date(Date.now() + 3600e3).toISOString();
  const tolto = idsHome[0], cambiato = idsHome[1];
  if (tolto) delete finto.lotti[tolto];
  if (cambiato && finto.lotti[cambiato]) { finto.lotti[cambiato] = [finto.lotti[cambiato][0], finto.lotti[cambiato][1] - 1000, finto.lotti[cambiato][2]]; }
  let n = 0;
  for (const [w, hgt] of [[390, 844], [1280, 900]]) {
    for (const tema of ['light', 'dark']) {
      const ctx = await browser.newContext({ viewport: { width: w, height: hgt }, colorScheme: tema, deviceScaleFactor: 1 });
      await ctx.route(/raw\.githubusercontent\.com\/.*live\.json/, r => r.fulfill({ status: 200, contentType: 'application/json', headers: { 'Access-Control-Allow-Origin': '*' }, body: JSON.stringify(finto) }));
      for (const [p, tipo] of pagine) {
        const page = await ctx.newPage();
        const errori = [];
        page.on('pageerror', e => errori.push('JS: ' + e.message));
        page.on('console', m => { if (m.type() === 'error' && !(tipo === '404' && /404/.test(m.text()))) errori.push('console: ' + m.text()); });
        page.on('requestfailed', r => errori.push('richiesta fallita: ' + r.url()));
        page.on('response', r => { if (r.status() >= 400 && !(tipo === '404' && r.url().endsWith(p))) errori.push(r.status() + ' ' + r.url()); });
        await page.goto(base + p, { waitUntil: 'networkidle' });
        await page.evaluate(() => document.fonts.ready);
        const larg = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
        if (larg.sw > larg.cw + 1) {
          const colpevoli = await page.evaluate(() => [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1)
            .slice(0, 3).map(e => e.tagName + '.' + e.className));
          errori.push(`scorrimento orizzontale ${larg.sw} > ${larg.cw}: ${colpevoli.join(', ')}`);
        }
        if (tipo === 'home') {
          if (tolto) {
            const nasc = await page.evaluate(id => { const e = document.querySelector('[data-id="' + id + '"]'); return e ? e.hidden : null; }, tolto);
            if (nasc !== true) errori.push(`live.json: il lotto ${tolto} tolto dal PVP non è stato nascosto`);
          }
          if (cambiato && vero.lotti[cambiato]) {
            const t = await page.evaluate(id => { const e = document.querySelector('[data-id="' + id + '"] [data-v=min]'); return e ? e.textContent : null; }, cambiato);
            const atteso = String(vero.lotti[cambiato][1] - 1000).replace(/\B(?=(\d{3})+(?!\d))/g, '.') + ' €';
            if (t !== atteso) errori.push(`live.json: offerta minima del lotto ${cambiato} non aggiornata (${t} invece di ${atteso})`);
          }
          await page.click('[data-tema]');
          const t = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
          const atteso = tema === 'light' ? 'dark' : 'light';
          if (t !== atteso) errori.push(`pulsante tema: atteso ${atteso}, trovato ${t}`);
          await page.evaluate(() => { document.documentElement.removeAttribute('data-theme'); try { localStorage.removeItem('aste-tema'); } catch (e) {} });
        }
        if (tipo === 'citta') {
          const lib = await page.$('[data-f=liberi]');
          if (lib) {
            await lib.click();
            const ko = await page.evaluate(() => [...document.querySelectorAll('#lista [data-id]')].filter(e => !e.hidden && e.dataset.disp !== 'libero').length);
            if (ko) errori.push(`filtro «Solo libere»: ${ko} schede non libere visibili`);
            await page.click('[data-f=tutti]');
          }
          await page.selectOption('[data-ordina]', 'prezzo');
          const ordinati = await page.evaluate(() => { const v = [...document.querySelectorAll('#lista [data-id]')].map(e => +e.dataset.min); return v.every((x, i) => !i || v[i - 1] <= x); });
          if (!ordinati) errori.push('ordinamento per offerta minima non funziona');
          await page.selectOption('[data-ordina]', 'sconto');
        }
        const shot = (w === 390 || ['home', 'citta', 'zona', 'fascia', 'auto', 'guida', 'metodo', 'indice-citta', 'citta-piccola', '404'].includes(tipo));
        if (shot) await page.screenshot({ path: path.join(SHOT, `${tipo}-${w}-${tema}.png`), fullPage: true });
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
