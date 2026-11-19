// Controllo nel browser di US College Aid: tutte le pagine a 375 e 1280 px, tema chiaro e scuro:
// niente scorrimento orizzontale della pagina, niente errori JS, niente richieste fallite, testo >= 11 px, contrasto >= 4,5.
// Ogni richiesta che non è del server locale viene bloccata (pubblicità e contatore compresi).
// Calcolatori: i casi di ATTESI (calcolati da verifica.py con un conto scritto a parte, non dalle pagine) vengono digitati
// nel calcolatore della rata, in quello del RAP e in quello del «buco»; poi messaggi d'errore, filtro delle scadenze, conto dei giorni
// con una data fissa, pulsante del tema, pagine senza JavaScript.
// Screenshot in collegeaid/cache/screenshot/ (cartella non salvata nel repository).
// Uso: python3 collegeaid/verifica.py --browser
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

function pagine(dir = SITO, pre = '/') {
  let p = fs.existsSync(path.join(dir, 'index.html')) ? [pre] : [];
  for (const d of fs.readdirSync(dir)) {
    const f = path.join(dir, d);
    if (d !== 'assets' && fs.statSync(f).isDirectory()) p = p.concat(pagine(f, pre + d + '/'));
  }
  return p;
}

(async () => {
  const srv = server();
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  const base = 'http://127.0.0.1:' + srv.address().port;
  const locale = u => u.startsWith(base);
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const problemi = [];
  const tutte = pagine().concat(['/does-not-exist/']);
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
          const colpevoli = await page.evaluate(() => [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > document.documentElement.clientWidth + 1 && !e.closest('.tab') && !e.closest('.formula'))
            .slice(0, 4).map(e => e.tagName + '.' + e.className));
          errori.push(`scorrimento orizzontale ${larg.sw} > ${larg.cw}: ${colpevoli.join(', ')}`);
        }
        const piccoli = await page.evaluate(() => [...document.querySelectorAll('main *')].filter(e => [...e.childNodes].some(c => c.nodeType === 3 && c.textContent.trim()) &&
          parseFloat(getComputedStyle(e).fontSize) < 11 && e.offsetParent !== null).slice(0, 3).map(e => e.tagName + ':' + e.textContent.trim().slice(0, 30)));
        if (piccoli.length) errori.push('testo sotto 11px: ' + piccoli.join(' | '));
        // contrasto del testo sul suo fondo (WCAG AA 4,5:1), nei due temi
        const contrasti = await page.evaluate(() => {
          const rgb = c => c.match(/[\d.]+/g).map(Number);
          const mix = (s, d) => { const a = s.length > 3 ? s[3] : 1; return [0, 1, 2].map(i => s[i] * a + d[i] * (1 - a)); };
          const lum = v => { const k = v.map(x => { x = x / 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); }); return 0.2126 * k[0] + 0.7152 * k[1] + 0.0722 * k[2]; };
          // fondo: colori pieni risalendo gli antenati; un fondo sfumato (testata) conta con tutti i suoi colori e vale il contrasto peggiore
          const fondi = e => { const strati = []; let basi = [[255, 255, 255]];
            while (e) { const cs = getComputedStyle(e), b = cs.backgroundColor, g = cs.backgroundImage;
              if (g && /gradient/.test(g)) { basi = g.match(/rgba?\([^)]+\)/g).map(rgb); break; }
              if (b && !/rgba\(0, 0, 0, 0\)|transparent/.test(b)) { const v = rgb(b); if (v.length < 4 || v[3] === 1) { basi = [v]; break; } strati.push(v); }
              e = e.parentElement; }
            return basi.map(c0 => { let c = c0.slice(0, 3); for (const s of strati.slice().reverse()) c = mix(s, c); return c; }); };
          const out = [];
          for (const sel of ['main .testo p', 'main .testo a', 'main .small', '.fatto span', '.fatto.main b', 'blockquote.cit cite', '.disclaimer', 'table.dati thead th', 'table.dati td', '.chip', '.chip.oro', '.chip.grigio', '.conto',
            '.ris-big', '.ris-lab', '.ris-nota', '.ris-righe li', '.calc .aiuto', '.date-l .cosa small', '.date-l .quando small', '.schede p', '.schede .big', '.nota p', '.faq p', '.formula', '.griglia a small', '.btn', '.btn.sec', 'footer p', '.band .sub', '.eyebrow']) {
            const e = [...document.querySelectorAll(sel)].find(x => x.offsetParent !== null && x.textContent.trim()); if (!e) continue;
            const a = lum(rgb(getComputedStyle(e).color).slice(0, 3)); const r = Math.min(...fondi(e).map(f => { const b = lum(f); return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05); }));
            if (r < 4.5) out.push(sel + ' ' + r.toFixed(2));
          }
          return out;
        });
        if (contrasti.length) errori.push('contrasto sotto 4,5: ' + contrasti.join(' | '));
        const nome = (p === '/' ? 'home' : p.replace(/^\/|\/$/g, '').replace(/\//g, '_')) + `-${w}-${tema}.png`;
        await page.screenshot({ path: path.join(SHOT, nome), fullPage: true });
        if (errori.length) problemi.push(`${p} @${w}px ${tema}: ` + errori.join(' ; '));
        n++;
        await page.close();
      }
      await ctx.close();
    }
  }

  // ---------------------------------------------------------------- calcolatori e strumenti
  const ctx = await browser.newContext({ viewport: { width: 375, height: 812 } });
  await ctx.route(u => !locale(u.toString()), r => r.abort());
  // orologio fermo al giorno scelto da verifica.py: il conto dei giorni non dipende da quando gira il controllo
  if (ATTESI.oggi) await ctx.addInitScript(`{ const F = new Date(${JSON.stringify(ATTESI.oggi)} + 'T12:00:00'); const D = Date; Date = class extends D { constructor(...a) { if (a.length) super(...a); else super(F.getTime()); } static now() { return F.getTime(); } }; }`);
  const page = await ctx.newPage();
  page.on('pageerror', e => problemi.push('strumenti JS: ' + e.message));
  let prove = 0;
  const testo = sel => page.evaluate(s => { const e = document.querySelector(s); return e ? e.textContent.trim() : null; }, sel);
  const visibile = sel => page.evaluate(s => { const e = document.querySelector(s); return !!e && !e.hidden && e.offsetParent !== null; }, sel);
  const scrivi = async (sel, v) => { await page.fill(sel, String(v)); };

  // rata
  await page.goto(base + '/student-loan-payment-calculator/', { waitUntil: 'load' });
  for (const c of ATTESI.rata || []) {
    await scrivi('[data-calc=rata] [name=saldo]', c.saldo); await scrivi('[data-calc=rata] [name=tasso]', c.tasso);
    await page.selectOption('[data-calc=rata] [name=piano]', c.piano);
    const got = { rata: await testo('[data-calc=rata] [data-o=rata]'), anni: await testo('[data-calc=rata] [data-o=anni]'), pagato: await testo('[data-calc=rata] [data-o=pagato]'), interessi: await testo('[data-calc=rata] [data-o=interessi]') };
    for (const k of Object.keys(got)) if (got[k] !== c.atteso[k]) problemi.push(`rata ${JSON.stringify([c.saldo, c.tasso, c.piano])}: ${k} = ${got[k]}, atteso ${c.atteso[k]}`);
    prove++;
  }
  // scelta del tipo di prestito -> tasso
  for (const [v] of ATTESI.tipi || []) {
    await page.selectOption('[data-calc=rata] [name=tipo]', v);
    const t = await page.inputValue('[data-calc=rata] [name=tasso]');
    if (t !== v) problemi.push(`rata: scelto il tipo ${v}, il campo del tasso dice ${t}`);
    prove++;
  }
  for (const [saldo, tasso] of [['', '6.52'], ['abc', '6.52'], ['0', '6.52'], ['10000', ''], ['10000', '25'], ['2000000', '5']]) {
    await scrivi('[data-calc=rata] [name=saldo]', saldo); await scrivi('[data-calc=rata] [name=tasso]', tasso);
    if (!(await visibile('[data-calc=rata] [data-errore]')) || (await visibile('[data-calc=rata] [data-uscita]'))) problemi.push(`rata: nessun messaggio d'errore con saldo «${saldo}» e tasso «${tasso}»`);
    prove++;
  }
  await scrivi('[data-calc=rata] [name=saldo]', '$27,000.00'); await scrivi('[data-calc=rata] [name=tasso]', '6.52%');
  if (await visibile('[data-calc=rata] [data-errore]')) problemi.push('rata: «$27,000.00» e «6.52%» non accettati');
  await page.screenshot({ path: path.join(SHOT, 'calc-rata-375.png') });

  // RAP
  await page.goto(base + '/repayment-assistance-plan/', { waitUntil: 'load' });
  for (const c of ATTESI.rap || []) {
    await scrivi('[data-calc=rap] [name=reddito]', c.reddito); await scrivi('[data-calc=rap] [name=carico]', c.carico);
    await scrivi('[data-calc=rap] [name=saldo]', c.saldo === null ? '' : c.saldo); await scrivi('[data-calc=rap] [name=tasso]', c.tasso);
    const got = await testo('[data-calc=rap] [data-o=rata]');
    if (got !== c.atteso.rata) problemi.push(`RAP ${JSON.stringify([c.reddito, c.carico])}: ${got}, atteso ${c.atteso.rata}`);
    if (c.saldo === null) { if (await visibile('[data-calc=rap] [data-mese]')) problemi.push('RAP: riquadro del mese visibile senza saldo'); }
    else for (const k of ['interessi', 'ainteressi', 'acapitale', 'nonaddebitati', 'aggiunta', 'nuovosaldo']) {
      const g = await testo(`[data-calc=rap] [data-o=${k}]`);
      if (g !== c.atteso[k]) problemi.push(`RAP ${JSON.stringify([c.reddito, c.carico, c.saldo, c.tasso])}: ${k} = ${g}, atteso ${c.atteso[k]}`);
    }
    prove++;
  }
  for (const [red, car] of [['', '0'], ['x', '0'], ['50000', '-1'], ['50000', '99']]) {
    await scrivi('[data-calc=rap] [name=reddito]', red); await scrivi('[data-calc=rap] [name=carico]', car);
    if (!(await visibile('[data-calc=rap] [data-errore]'))) problemi.push(`RAP: nessun messaggio d'errore con reddito «${red}» e persone a carico «${car}»`);
    prove++;
  }
  await scrivi('[data-calc=rap] [name=reddito]', '45,000'); await scrivi('[data-calc=rap] [name=carico]', '1');
  await page.screenshot({ path: path.join(SHOT, 'calc-rap-375.png') });

  // buco
  await page.goto(base + '/parent-plus-loans/', { waitUntil: 'load' });
  for (const c of ATTESI.buco || []) {
    await scrivi('[data-calc=buco] [name=costo]', c.costo); await page.selectOption('[data-calc=buco] [name=anni]', String(c.anni));
    const got = { resto: await testo('[data-calc=buco] [data-o=resto]'), studente: await testo('[data-calc=buco] [data-o=studente]'), genitori: await testo('[data-calc=buco] [data-o=genitori]'), costo: await testo('[data-calc=buco] [data-o=costo]') };
    for (const k of Object.keys(got)) if (got[k] !== c.atteso[k]) problemi.push(`buco ${JSON.stringify([c.costo, c.anni])}: ${k} = ${got[k]}, atteso ${c.atteso[k]}`);
    const righe = await page.evaluate(() => [...document.querySelectorAll('[data-calc=buco] [data-righe] tr')].map(tr => [...tr.cells].map(x => x.textContent.trim())));
    if (JSON.stringify(righe) !== JSON.stringify(c.atteso.righe)) problemi.push(`buco ${JSON.stringify([c.costo, c.anni])}: righe ${JSON.stringify(righe)}, attese ${JSON.stringify(c.atteso.righe)}`);
    prove++;
  }
  await scrivi('[data-calc=buco] [name=costo]', 'abc');
  if (!(await visibile('[data-calc=buco] [data-errore]'))) problemi.push("buco: nessun messaggio d'errore con un costo non numerico");
  await scrivi('[data-calc=buco] [name=costo]', '32,000');
  await page.screenshot({ path: path.join(SHOT, 'calc-buco-375.png') });

  // scadenze: filtro, ricerca, conto dei giorni con l'orologio fermo
  await page.goto(base + '/fafsa-deadlines/', { waitUntil: 'load' });
  const S = ATTESI.scadenze || {};
  const viste = () => page.evaluate(() => [...document.querySelectorAll('[data-scadenze] tbody tr')].filter(tr => !tr.hidden).map(tr => tr.getAttribute('data-sigla')));
  if (!(await visibile('[data-filtri]'))) problemi.push('scadenze: filtri nascosti con JavaScript acceso');
  for (const t of ['date', 'asap', 'check', '']) {
    await page.selectOption('[data-scadenze] [data-tipo]', t);
    const v = await viste();
    if (S.tipi && JSON.stringify(v) !== JSON.stringify(S.tipi[t || 'tutti'])) problemi.push(`scadenze: filtro «${t}» mostra ${v.length} righe, attese ${S.tipi[t || 'tutti'].length}`);
    prove++;
  }
  await scrivi('[data-scadenze] [data-cerca]', 'new'); let v = await viste();
  if (S.cerca_new && JSON.stringify(v) !== JSON.stringify(S.cerca_new)) problemi.push(`scadenze: la ricerca «new» mostra ${v}`);
  await scrivi('[data-scadenze] [data-cerca]', 'zzzz');
  if (!(await visibile('[data-scadenze] [data-vuoto]'))) problemi.push('scadenze: nessun messaggio con una ricerca senza risultati');
  await scrivi('[data-scadenze] [data-cerca]', '');
  for (const [iso, atteso] of S.giorni || []) {
    const g = await page.evaluate(d => { const e = document.querySelector(`[data-giorni="${d}"]`); return e ? [e.textContent, e.hidden] : null; }, iso);
    if (!g || g[0] !== atteso || g[1]) problemi.push(`conto dei giorni per ${iso}: ${JSON.stringify(g)}, atteso «${atteso}»`);
    prove++;
  }
  // tema
  const prima = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  await page.click('[data-tema]');
  const dopo = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  if (prima === dopo) problemi.push('il pulsante del tema non cambia i colori');
  await ctx.close();

  // senza JavaScript: tabelle complete, filtri e conto dei giorni nascosti, calcolatori che dicono che serve JavaScript
  const ctx2 = await browser.newContext({ viewport: { width: 375, height: 812 }, javaScriptEnabled: false });
  const p2 = await ctx2.newPage();
  await p2.goto(base + '/fafsa-deadlines/', { waitUntil: 'load' });
  const nojs = await p2.evaluate(() => ({ righe: document.querySelectorAll('[data-scadenze] tbody tr').length, filtri: getComputedStyle(document.querySelector('[data-filtri]')).display,
    conto: [...document.querySelectorAll('[data-giorni]')].filter(e => e.offsetParent !== null).length }));
  if (nojs.righe !== (S.tipi ? S.tipi.tutti.length : nojs.righe) || nojs.filtri !== 'none' || nojs.conto) problemi.push('scadenze senza JavaScript: ' + JSON.stringify(nojs));
  await ctx2.close();
  await browser.close();
  srv.close();
  console.log(`Browser: ${n} viste (${tutte.length} pagine a 375/1280 px, chiaro e scuro), ${prove} prove su calcolatori e strumenti, ${bloccate} richieste esterne bloccate; screenshot in ${SHOT}`);
  if (problemi.length) {
    console.log(problemi.length + ' PROBLEMI:\n - ' + problemi.slice(0, 60).join('\n - '));
    process.exit(1);
  }
})();
