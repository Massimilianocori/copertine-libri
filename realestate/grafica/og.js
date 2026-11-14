// Immagine di anteprima per la condivisione: node realestate/grafica/og.js -> realestate/grafica/og.png
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  await p.route(/^https?:/, r => r.abort());
  await p.goto('file://' + path.join(__dirname, 'og.html'));
  await p.screenshot({ path: path.join(__dirname, 'og.png') });
  await b.close();
})();
