// Controllo nel browser di US Paycheck Calculator: tutte le pagine a 375 e 1280 px (chiaro; home, California ed employer anche scuro):
// niente scorrimento orizzontale della pagina, niente errori JS, niente richieste fallite, testo >= 11 px.
// Ogni richiesta che non è del server locale viene bloccata (pubblicità e contatore compresi).
// Calcolatore: i 10 casi a mano passati da verifica.py in CASI_CALC (netto atteso), stipendio annuo, paga oraria, errori; calcolatore del datore.
// Screenshot in paycheck/cache/screenshot/ (cartella non salvata nel repository).
// Uso: python3 paycheck/verifica.py --browser
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
      const elenco = tema === 'light' ? tutte : ['/', '/california/', '/employer-payroll-taxes/'];
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
        if (['/', '/california/', '/employer-payroll-taxes/', '/federal-withholding/', '/texas/'].includes(p)) {
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
  // calcolatore della busta paga: i casi a mano di verifica.py
  const ctx = await browser.newContext({ viewport: { width: 375, height: 812 } });
  await ctx.route(u => !locale(u.toString()), r => r.abort());
  const page = await ctx.newPage();
  page.on('pageerror', e => problemi.push('calcolatore JS: ' + e.message));
  await page.goto(base + '/', { waitUntil: 'load' });
  const B = '[data-busta] ';
  const dollari = c => (c / 100).toFixed(2);
  for (const c of CASI) {
    const i = c.i;
    await page.selectOption(B + 'select[name=stato]', i.stato);
    await page.selectOption(B + 'select[name=periodo]', i.periodo);
    await page.selectOption(B + 'select[name=tipo]', 'periodo');
    await page.fill(B + 'input[name=importo]', dollari(i.lordo));
    await page.selectOption(B + 'select[name=fs]', i.fs);
    await page.setChecked(B + 'input[name=step2]', !!i.step2);
    await page.evaluate(() => { document.querySelector('[data-busta] details').open = true; });
    for (const k of ['step3', 'a4', 'b4', 'c4', 'ytd']) await page.fill(B + `input[name=${k}]`, dollari(i[k] || 0));
    if (i.stato === 'CA') { await page.selectOption(B + 'select[name=ca_fs]', i.ca_fs); await page.fill(B + 'input[name=ca_reg]', String(i.ca_reg)); await page.fill(B + 'input[name=ca_est]', String(i.ca_est)); }
    if (i.stato === 'IL') { await page.fill(B + 'input[name=il1]', String(i.il1)); await page.fill(B + 'input[name=il2]', String(i.il2)); }
    if (i.stato === 'NC') { await page.selectOption(B + 'select[name=nc_fs]', i.nc_fs); await page.fill(B + 'input[name=nc_all]', String(i.nc_all)); }
    const netto = ((await page.textContent(B + '[data-netto]').catch(() => '')) || '').trim();
    if (netto !== c.netto) problemi.push(`calcolatore ${i.stato} ${i.periodo} ${dollari(i.lordo)}: netto «${netto}», atteso «${c.netto}»`);
    const visibili = await page.evaluate(() => [...document.querySelectorAll('[data-busta] fieldset[data-solo]')].filter(e => !e.hidden).map(e => e.getAttribute('data-solo')));
    if (visibili.length !== 1 || !visibili[0].split(' ').includes(i.stato)) problemi.push(`calcolatore ${i.stato}: riquadri dello Stato visibili ${visibili}`);
  }
  // stipendio annuo, paga oraria ed errori (Texas, single): 52.000 l'anno e 25 $ × 80 ore = 2.000 ogni due settimane → 1.690,85
  await page.goto(base + '/texas/', { waitUntil: 'load' });
  await page.selectOption(B + 'select[name=tipo]', 'anno');
  await page.fill(B + 'input[name=importo]', '52,000');
  let t = ((await page.textContent(B + '[data-netto]').catch(() => '')) || '').trim();
  if (t !== '$1,690.85') problemi.push('stipendio annuo 52.000: netto ' + t);
  await page.selectOption(B + 'select[name=tipo]', 'ora');
  await page.fill(B + 'input[name=importo]', '25');
  await page.fill(B + 'input[name=ore]', '80');
  t = ((await page.textContent(B + '[data-netto]').catch(() => '')) || '').trim();
  if (t !== '$1,690.85') problemi.push('paga oraria 25 × 80: netto ' + t);
  await page.fill(B + 'input[name=importo]', 'abc');
  t = (await page.textContent(B + '[data-out]')) || '';
  if (!t.includes('Check the amounts')) problemi.push('importo non valido: nessun messaggio');
  await page.fill(B + 'input[name=importo]', '');
  t = (await page.textContent(B + '[data-out]')) || '';
  if (!t.includes('Enter your gross pay')) problemi.push('importo vuoto: nessun invito');
  // calcolatore del datore: 50.000 $ in Texas e in California; l'aliquota si aggiorna con lo Stato
  await page.goto(base + '/employer-payroll-taxes/', { waitUntil: 'load' });
  const D = '[data-datore] ';
  t = ((await page.textContent(D + '[data-tasse]')) || '').trim();
  if (t !== process.env.DATORE_TX) problemi.push(`datore Texas: ${t}, atteso ${process.env.DATORE_TX}`);
  await page.selectOption(D + 'select[name=stato]', 'CA');
  t = ((await page.textContent(D + '[data-tasse]')) || '').trim();
  if (t !== process.env.DATORE_CA) problemi.push(`datore California: ${t}, atteso ${process.env.DATORE_CA}`);
  if ((await page.inputValue(D + 'input[name=aliquota]')) !== '3.4') problemi.push('datore: aliquota non aggiornata per la California');
  await page.fill(D + 'input[name=aliquota]', 'x');
  if (!((await page.textContent(D + '[data-out]')) || '').includes('Check the figures')) problemi.push('datore: aliquota non valida senza messaggio');
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
