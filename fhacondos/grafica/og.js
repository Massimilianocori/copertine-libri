// Rigenera grafica/og.png (1200x630) da grafica/og.html con Playwright. Uso: node fhacondos/grafica/og.js
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.join(__dirname, 'og.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: path.join(__dirname, 'og.png') });
  await b.close();
})();
