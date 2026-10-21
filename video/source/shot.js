const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [,, mode, a, b, out] = process.argv;
  const browser = await chromium.launch({ args: ['--font-render-hinting=none'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('pageerror', e => console.error('PAGEERR', e.message));
  await page.goto('file://' + path.join(__dirname, 'video.html'));
  await page.evaluate(() => document.fonts.ready);
  if (mode === 'times') {
    for (const t of a.split(',').map(Number)) {
      await page.evaluate(t => window.render(t), t);
      await page.screenshot({ path: `${out}/t${t.toFixed(1)}.png` });
    }
  } else {
    const fps = 30, s = +a, e = +b;
    for (let f = s; f < e; f++) {
      await page.evaluate(t => window.render(t), f / fps);
      await page.screenshot({ path: `${out}/f${String(f).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 93 });
    }
  }
  await browser.close();
})();
