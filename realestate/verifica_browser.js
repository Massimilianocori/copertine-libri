// Controllo nel browser di Real Estate Exam Pass Rates: tutte le pagine a 375 e 1280 px, tema chiaro e scuro:
// niente scorrimento orizzontale della pagina, niente errori JS, niente richieste fallite, testo >= 11 px.
// Ogni richiesta che non è del server locale viene bloccata (pubblicità e contatore compresi).
// Tabelle: ordine iniziale per numero di esami, ordinamento per percentuale con le scuole sotto soglia DOPO le altre (riga di stacco),
// ricerca, filtro «almeno 30 esami», filtro del formato, messaggio «nessuna scuola», pulsanti delle intestazioni. I valori attesi
// arrivano da verifica.py in ATTESI (calcolati dai file grezzi, non dalle pagine).
// Screenshot in realestate/cache/screenshot/ (cartella non salvata nel repository).
// Uso: python3 realestate/verifica.py --browser
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const SITO = path.join(__dirname, 'sito');
const SHOT = path.join(__dirname, 'cache', 'screenshot');
fs.mkdirSync(SHOT, { recursive: true });
const TIPI = { '.html': 'text/html; charset=utf-8', '.json': 'application/json', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.xml': 'application/xml', '.txt': 'text/plain' };
const ATTESI = process.env.ATTESI ? JSON.parse(process.env.ATTESI) : {};

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
      for (const p of tutte) {
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
        // contrasto del testo principale e dei link sul fondo della pagina (WCAG AA 4,5:1), nei due temi
        const contrasti = await page.evaluate(() => {
          const lum = c => { const v = c.match(/[\d.]+/g).slice(0, 3).map(x => { x = x / 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); }); return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
          const fondo = e => { while (e) { const b = getComputedStyle(e).backgroundColor; if (b && !/rgba\(0, 0, 0, 0\)|transparent/.test(b)) return b; e = e.parentElement; } return 'rgb(255,255,255)'; };
          const out = [];
          for (const sel of ['main .testo p', 'main .testo a', 'main .small', 'table.tassi .nn', 'table.tassi .pc', '.tag-s', '.fatto span', '.stati .lab', 'blockquote.cit cite', '.disclaimer', 'table.dati thead th']) {
            const e = document.querySelector(sel); if (!e) continue;
            const a = lum(getComputedStyle(e).color), b = lum(fondo(e)); const r = (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
            if (r < 4.5) out.push(sel + ' ' + r.toFixed(2));
          }
          return out;
        });
        if (contrasti.length) errori.push('contrasto sotto 4,5: ' + contrasti.join(' | '));
        const nome = (p === '/' ? 'home' : p.replace(/\//g, '')) + `-${w}-${tema}.png`;
        await page.screenshot({ path: path.join(SHOT, nome), fullPage: true });
        if (errori.length) problemi.push(`${p} @${w}px ${tema}: ` + errori.join(' ; '));
        n++;
        await page.close();
      }
      await ctx.close();
    }
  }
  // tabelle delle scuole
  const ctx = await browser.newContext({ viewport: { width: 375, height: 812 } });
  await ctx.route(u => !locale(u.toString()), r => r.abort());
  const page = await ctx.newPage();
  page.on('pageerror', e => problemi.push('tabella JS: ' + e.message));
  const nomi = () => page.evaluate(() => [...document.querySelectorAll('[data-tabella] tbody tr')].map(tr => tr.classList.contains('stacco') ? '--' : tr.classList.contains('tot-riga') ? '=tot' : tr.getAttribute('data-nome')));
  let prove = 0;
  for (const [slug, a] of Object.entries(ATTESI)) {
    const dove = '/' + slug + '/';
    await page.goto(base + dove, { waitUntil: 'load' });
    const T = '[data-tabella] ';
    if (await page.evaluate(() => document.querySelector('[data-strumenti]').hidden)) problemi.push(dove + ': strumenti nascosti con JavaScript attivo');
    let r = await nomi();
    if (r[0] !== '=tot') problemi.push(dove + ': la riga del totale non è la prima');
    if (JSON.stringify(r.slice(1)) !== JSON.stringify(a.per_esami)) problemi.push(dove + ': ordine iniziale diverso da quello per numero di esami');
    for (const [k, attesa] of Object.entries(a.per_tasso)) {
      await page.selectOption(T + '[data-ordina]', 'r:' + k);
      r = await nomi();
      if (JSON.stringify(r.slice(1)) !== JSON.stringify(attesa)) problemi.push(`${dove}: ordine per percentuale (${k}) diverso dall'atteso: ${r.slice(1, 4)} / ${attesa.slice(0, 3)}`);
      const st = (await page.textContent(T + '[data-stato]')) || '';
      if (!st.includes('smaller samples are listed after them')) problemi.push(dove + ': manca la frase sui campioni piccoli nello stato della tabella');
      prove++;
    }
    // pulsante dell'intestazione: un clic ordina per quella colonna, un altro inverte (le scuole sotto soglia restano dopo)
    await page.selectOption(T + '[data-ordina]', 'n');
    await page.click(T + `.ord[data-ord="r:${a.primaria}"]`);
    r = await nomi();
    if (JSON.stringify(r.slice(1)) !== JSON.stringify(a.per_tasso[a.primaria])) problemi.push(dove + ': il pulsante dell\'intestazione non ordina per percentuale');
    await page.click(T + `.ord[data-ord="r:${a.primaria}"]`);
    r = await nomi();
    const sopra = a.per_tasso[a.primaria].slice(0, a.sopra_soglia);
    if (a.sopra_soglia > 1 && (r[1] !== a.ultimo_sopra || r.slice(1, 1 + a.sopra_soglia).slice().sort().join('|') !== sopra.slice().sort().join('|'))) problemi.push(dove + ': ordine inverso sbagliato (le scuole sotto soglia devono restare dopo)');
    // filtro «almeno 30 esami»
    await page.selectOption(T + '[data-ordina]', 'n');
    await page.setChecked(T + '[data-min]', true);
    r = await nomi();
    if (r.length - 1 !== a.sopra_soglia) problemi.push(`${dove}: filtro dei 30 esami: ${r.length - 1} righe, attese ${a.sopra_soglia}`);
    await page.setChecked(T + '[data-min]', false);
    // ricerca
    await page.fill(T + '[data-cerca]', a.cerca);
    r = await nomi();
    if (r.length - 1 !== a.cerca_n) problemi.push(`${dove}: ricerca «${a.cerca}»: ${r.length - 1} righe, attese ${a.cerca_n}`);
    await page.fill(T + '[data-cerca]', 'zzzz-no-school');
    if (await page.evaluate(() => document.querySelector('[data-vuoto]').hidden)) problemi.push(dove + ': nessun messaggio quando la ricerca non trova scuole');
    await page.fill(T + '[data-cerca]', '');
    if (a.online !== null) {
      await page.selectOption(T + '[data-formato]', 'Online');
      r = await nomi();
      if (r.length - 1 !== a.online) problemi.push(`${dove}: filtro Online: ${r.length - 1} righe, attese ${a.online}`);
      await page.selectOption(T + '[data-formato]', '');
    }
    r = await nomi();
    if (r.length - 1 !== a.per_esami.length) problemi.push(dove + ': tolti i filtri non tornano tutte le scuole');
    prove += 5;
  }
  await page.goto(base + '/', { waitUntil: 'load' });
  const prima = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  await page.click('[data-tema]');
  const dopo = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  if (prima === dopo) problemi.push('il pulsante del tema non cambia i colori');
  await ctx.close();
  // senza JavaScript: tabella completa e leggibile, strumenti nascosti
  const ctx2 = await browser.newContext({ viewport: { width: 375, height: 812 }, javaScriptEnabled: false });
  const p2 = await ctx2.newPage();
  for (const [slug, a] of Object.entries(ATTESI)) {
    await p2.goto(base + '/' + slug + '/', { waitUntil: 'load' });
    const righe = await p2.evaluate(() => document.querySelectorAll('[data-tabella] tbody tr[data-nome]').length);
    const strum = await p2.evaluate(() => getComputedStyle(document.querySelector('[data-strumenti]')).display);
    if (righe !== a.per_esami.length || strum !== 'none') problemi.push(`/${slug}/ senza JavaScript: ${righe} righe, strumenti ${strum}`);
  }
  await ctx2.close();
  await browser.close();
  srv.close();
  console.log(`Browser: ${n} viste (${tutte.length} pagine a 375/1280 px, chiaro e scuro), ${prove} prove sulle tabelle, ${bloccate} richieste esterne bloccate; screenshot in ${SHOT}`);
  if (problemi.length) {
    console.log(problemi.length + ' PROBLEMI:\n - ' + problemi.slice(0, 60).join('\n - '));
    process.exit(1);
  }
})();
