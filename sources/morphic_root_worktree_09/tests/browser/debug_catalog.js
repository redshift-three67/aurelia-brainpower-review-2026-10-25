const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  const logs = [];
  const network = [];

  page.on('console', msg => logs.push({ type: msg.type(), text: msg.text() }));
  page.on('response', async resp => {
    const url = resp.url();
    if (url.includes('/api/')) {
      try {
        const body = await resp.text();
        network.push({ url, status: resp.status(), body: body.slice(0, 5000) });
      } catch (e) {
        network.push({ url, status: resp.status(), error: e.message });
      }
    }
  });

  await page.goto('http://127.0.0.1:8000/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // Click step 10 (Berichtskatalog & Export) if available
  const step10 = await page.$('[data-step="10"]');
  if (step10) await step10.click();
  await page.waitForTimeout(1500);

  // Read catalog state
  const catalogHtml = await page.$eval('#report-list', el => el.innerHTML).catch(() => 'no element');
  const reportsState = await page.$eval('#reports-state', el => el.textContent).catch(() => 'no state');

  const result = { logs, network, catalogHtml, reportsState };
  fs.writeFileSync('C:/Users/Hubert111/AppData/Local/Temp/workbench_debug_catalog.json', JSON.stringify(result, null, 2));
  console.log('debug written');
  await browser.close();
})().catch(err => { console.error(err.message); process.exit(1); });
