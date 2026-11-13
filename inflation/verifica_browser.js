// Controllo nel browser di Inflation Calculator: pagine scelte a 375 e 1280 px, tema chiaro e scuro; niente scorrimento
// orizzontale, niente errori JS, niente richieste fallite, niente testo sotto 11 px; i calcolatori danno i numeri attesi (calcolati
// con motore.py e passati da verifica.py in CASI_CALC). Tutte le richieste non locali sono bloccate (AdSense e contatore compresi).
// Uso: python3 inflation/verifica.py --browser (passa PAGINE e CASI_CALC: le pagine e i casi tedeschi solo con genera.SEZIONE_DE = True).
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const SITO = path.join(__dirname, 'sito');
const SHOT = path.join(__dirname, 'cache', 'screenshot');
fs.mkdirSync(SHOT, { recursive: true });
const TIPI = { '.html': 'text/html; charset=utf-8', '.json': 'application/json', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.xml': 'application/xml', '.txt': 'text/plain' };
const CASI = process.env.CASI_CALC ? JSON.parse(process.env.CASI_CALC) : [];
// Senza PAGINE: solo USA e UK (la sezione tedesca è spenta, genera.SEZIONE_DE = False).
const PAGINE = (process.env.PAGINE || '/,/uk/,/us/1970-dollars-today/,/us/inflation-rate-by-year/,/us/100-dollars-in-1970/,/uk/inflation-rate-by-year/,/uk/rpi-calculator/,/how-we-check/,/does-not-exist/').split(',');

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

function numero(t, de) {
  t = t.replace(/[^\d.,−-]/g, '');
  if (de) t = t.replace(/\./g, '').replace(',', '.'); else t = t.replace(/,/g, '');
  return parseFloat(t.replace('−', '-'));
}

(async () => {
  const srv = server();
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const base = 'http://127.0.0.1:' + srv.address().port;
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const problemi = [];
  let n = 0;
  for (const [w, hgt] of [[375, 812], [1280, 900]]) {
    for (const tema of ['light', 'dark']) {
      const ctx = await browser.newContext({ viewport: { width: w, height: hgt }, colorScheme: tema, deviceScaleFactor: 1 });
      await ctx.route(u => !u.toString().startsWith(base), r => r.abort());
      for (const p of PAGINE) {
        const page = await ctx.newPage();
        const errori = [];
        page.on('pageerror', e => errori.push('JS: ' + e.message));
        page.on('console', m => { if (m.type() === 'error' && !/net::ERR_FAILED|404/.test(m.text())) errori.push('console: ' + m.text()); });
        page.on('requestfailed', r => { if (r.url().startsWith(base)) errori.push('richiesta fallita: ' + r.url()); });
        page.on('response', r => { if (r.status() >= 400 && !(p === '/does-not-exist/' && r.url().endsWith(p))) errori.push(r.status() + ' ' + r.url()); });
        await page.goto(base + p, { waitUntil: 'load' });
        const info = await page.evaluate(() => {
          const sw = document.documentElement.scrollWidth, cw = document.documentElement.clientWidth;
          const piccoli = [];
          for (const el of document.querySelectorAll('body *')) {
            if (!el.childNodes.length || ![...el.childNodes].some(c => c.nodeType === 3 && c.textContent.trim())) continue;
            const cs = getComputedStyle(el);
            if (cs.display === 'none' || cs.visibility === 'hidden' || el.closest('[hidden],details:not([open]),.skip,.hp')) continue;
            const r = el.getBoundingClientRect();
            if (r.width === 0) continue;
            if (parseFloat(cs.fontSize) < 11) piccoli.push(el.tagName + ':' + el.textContent.trim().slice(0, 30) + ' ' + cs.fontSize);
          }
          return { sw, cw, piccoli: piccoli.slice(0, 5) };
        });
        if (info.sw > info.cw + 1) errori.push(`scorrimento orizzontale ${info.sw} > ${info.cw}`);
        if (info.piccoli.length) errori.push('testo < 11px: ' + info.piccoli.join(' | '));
        const nome = (p.replace(/\//g, '_') || '_') + `${w}_${tema}`;
        if (tema === 'light' || w === 375) await page.screenshot({ path: path.join(SHOT, nome + '.png'), fullPage: false });
        for (const e of errori) problemi.push(`${p} ${w}px ${tema}: ${e}`);
        await page.close();
        n++;
      }
      // calcolatori: casi attesi (solo una volta per larghezza)
      if (tema === 'light') {
        for (const c of CASI) {
          const page = await ctx.newPage();
          const errori = [];
          page.on('pageerror', e => errori.push('JS: ' + e.message));
          await page.goto(base + c.pagina, { waitUntil: 'load' });
          await page.fill('input[name=a]', c.importo_testo);
          if (c.serie) await page.selectOption('select[name=s]', c.serie);
          await page.selectOption('select[name=fy]', String(c.da[0]));
          await page.selectOption('select[name=fm]', c.da[1] ? String(c.da[1]) : '');
          await page.selectOption('select[name=ty]', String(c.a[0]));
          await page.selectOption('select[name=tm]', c.a[1] ? String(c.a[1]) : '');
          if (c.valuta) await page.check(`input[name=c][value=${c.valuta}]`);
          await page.waitForTimeout(50);
          const t = await page.textContent('[data-out] [data-valore]').catch(() => null);
          const v = t === null ? null : numero(t, c.de);
          if (v === null || Math.abs(v - c.atteso) > 0.006) errori.push(`calcolatore: atteso ${c.atteso}, letto ${t}`);
          if (c.serie_finale) {
            const s = await page.inputValue('select[name=s]');
            if (s !== c.serie_finale) errori.push(`serie ${s} invece di ${c.serie_finale}`);
          }
          if (w === 375 && c.foto) await page.screenshot({ path: path.join(SHOT, 'calc_' + c.foto + '.png'), fullPage: false, clip: { x: 0, y: 200, width: 375, height: 812 } }).catch(() => {});
          for (const e of errori) problemi.push(`caso ${JSON.stringify(c.descr)} ${w}px: ${e}`);
          await page.close();
        }
      }
      await ctx.close();
    }
  }
  // pulsante del tema
  {
    const ctx = await browser.newContext({ viewport: { width: 375, height: 800 }, colorScheme: 'light' });
    await ctx.route(u => !u.toString().startsWith(base), r => r.abort());
    const page = await ctx.newPage();
    await page.goto(base + '/', { waitUntil: 'load' });
    await page.click('[data-tema]');
    const t = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
    if (t !== 'dark') problemi.push('pulsante tema: data-theme=' + t);
    // link condiviso: parametri letti all'apertura
    await page.goto(base + '/?a=250&f=1985&t=2000#calc', { waitUntil: 'load' });
    const v = await page.textContent('[data-valore]');
    const atteso = process.env.ATTESO_LINK ? parseFloat(process.env.ATTESO_LINK) : null;
    if (atteso !== null && Math.abs(numero(v, false) - atteso) > 0.006) problemi.push(`link condiviso: atteso ${atteso}, letto ${v}`);
    // (revisione indipendente) passaggio CPI -> RPI: automatico prima del 1988 con la nota visibile, ritorno al CPI quando le due date
    // tornano dal 1988 in poi; una scelta fatta a mano del RPI resta
    await page.goto(base + '/uk/', { waitUntil: 'load' });
    const stato = async () => ({ s: await page.inputValue('select[name=s]'), nota: await page.isVisible('[data-nota]'), v: await page.textContent('[data-valore]') });
    await page.selectOption('select[name=fy]', '1970');
    let st = await stato();
    if (st.s !== 'uk_rpi' || !st.nota) problemi.push('UK 1970: serie ' + st.s + ', nota visibile ' + st.nota);
    await page.fill('input[name=a]', '200');
    st = await stato();
    if (st.s !== 'uk_rpi' || !st.nota) problemi.push('UK 1970 dopo un altro importo: la nota sul RPI sparisce (' + st.s + ', ' + st.nota + ')');
    await page.selectOption('select[name=fy]', '1995');
    st = await stato();
    if (st.s !== 'uk_cpi' || st.nota) problemi.push('UK 1995 dopo il 1970: resta ' + st.s + ' (nota ' + st.nota + ') invece di tornare al CPI');
    await page.selectOption('select[name=s]', 'uk_rpi');
    await page.selectOption('select[name=fy]', '2000');
    st = await stato();
    if (st.s !== 'uk_rpi') problemi.push('UK: il RPI scelto a mano non resta');
    // ottobre 2025 (USA): mese non selezionabile, nessun numero inventato
    await page.goto(base + '/?a=100&f=2025-10&t=2026-10#calc', { waitUntil: 'load' });
    const ott = await page.evaluate(() => ({ dis: document.querySelector('select[name=fm] option[value="10"]').disabled, fm: document.querySelector('select[name=fm]').value }));
    if (!ott.dis || ott.fm === '10') problemi.push('ottobre 2025 selezionabile nel calcolatore USA: ' + JSON.stringify(ott));
    await ctx.close();
  }
  await browser.close();
  srv.close();
  console.log(JSON.stringify({ viste: n, casi: CASI.length, problemi }));
})();
