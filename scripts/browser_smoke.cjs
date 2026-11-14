// QA opcional: Playwright externo ao projeto + Chrome instalado, sem dependência de produção.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');

async function main() {
  const base = process.env.SKYFETCH_BASE_URL || 'http://127.0.0.1:5055';
  const browser = await chromium.launch({
    executablePath: process.env.SKYFETCH_CHROME || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
  });
  const evidence = path.join(__dirname, '../.nexus/plans/implementacao/evidence');
  fs.mkdirSync(evidence, { recursive: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  async function settled() {
    await page.waitForFunction(() => document.querySelector('#results-list').getAttribute('aria-busy') === 'false');
  }
  async function search(query) {
    await page.locator('#search-input').fill(query);
    await page.locator('#search-input').press('Enter');
    await settled();
  }
  try {
    for (const [name, width, height] of [['desktop', 1280, 900], ['tablet', 768, 1024], ['mobile', 390, 844]]) {
      await page.setViewportSize({ width, height });
      await page.goto(base + '/?q=voos');
      await settled();
      assert.equal(await page.locator('.flight-card').count(), 5);
      assert.equal(await page.locator('#result-count').textContent(), '05');
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
      await page.screenshot({ path: path.join(evidence, name + '.png'), fullPage: true, animations: 'disabled' });
      console.log(`OK: ${name}, cinco resultados reais, sem overflow horizontal`);
    }
    await page.setViewportSize({ width: 1280, height: 900 });
    for (const query of ['?q=latam&q=gol', '?q=&q=latam']) {
      await page.goto(base + '/' + query); await settled();
      assert.equal(new URL(page.url()).search, query);
      assert.equal(await page.locator('.flight-card').count(), 0);
      assert.match(await page.locator('#results-list').textContent(), /apenas uma vez/);
    }
    await search('voos');
    const colors = await page.evaluate(() => ['.meta-label', '.results-footer', '.dataset-note', '.footer-inner', '#search-input'].map((selector) => {
      return getComputedStyle(document.querySelector(selector), selector === '#search-input' ? '::placeholder' : null).color;
    }));
    for (const color of colors) {
      const linear = color.match(/[\d.]+/g).slice(0, 3).map(Number).map((v) => {
        v /= 255; return v <= .04045 ? v/12.92 : ((v+.055)/1.055)**2.4;
      });
      const lum = linear[0]*.2126 + linear[1]*.7152 + linear[2]*.0722;
      assert(1.05/(lum+.05) >= 4.5);
    }
    console.log('OK: q duplicado rejeitado sem reescrita e cinco contrastes >= 4,5:1');
    await page.goto(base + '/?other=kept&q=latam#results'); await settled();
    const historyLength = await page.evaluate(() => history.length);
    await search('voos gol');
    assert.equal(await page.locator('.flight-card').count(), 1);
    assert.equal(new URL(page.url()).searchParams.get('other'), 'kept');
    assert.equal(new URL(page.url()).hash, '#results');
    assert.equal(await page.evaluate(() => history.length), historyLength);
    await page.reload(); await settled();
    assert.equal(await page.locator('#search-input').inputValue(), 'voos gol');
    await search('voos latam xyz');
    assert.match(await page.locator('#results-list').textContent(), /não reconhecido/);
    await search('voos latam manaus');
    assert.match(await page.locator('#results-list').textContent(), /Nenhum resultado/);
    await page.goto(base + '/?q='); await settled();
    assert.equal(await page.locator('#search-input').inputValue(), '');
    assert.match(await page.locator('#search-summary').textContent(), /Digite uma frase/);
    await page.locator('[data-search="voos latam"]').click(); await settled();
    assert.equal(await page.locator('.flight-card').count(), 3);
    assert(await page.locator('#search-input').evaluate((input) => input === document.activeElement));
    await page.goto(base + '/?q=' + 'a'.repeat(151)); await settled();
    assert.equal((await page.locator('#search-input').inputValue()).length, 151);
    assert.match(await page.locator('#results-list').textContent(), /150 caracteres/);
    await search('<img src=x onerror=window.injected=1>');
    assert.equal(await page.locator('#results-list img').count(), 0);
    assert.equal(await page.evaluate(() => window.injected), undefined);
    console.log('OK: Enter, chips, foco, URL, refresh, vazio, consulta longa, inválida e XSS');

    let mode = 'normal';
    let releaseOld, oldReady;
    await page.route('**/api/search?*', async (route) => {
      if (mode === 'hang') return;
      if (mode === 'offline') return route.abort('failed');
      if (mode === 'json') return route.fulfill({ status: 200, contentType: 'text/html', body: '<h1>erro</h1>' });
      if (mode === '503' || mode === '500') {
        return route.fulfill({ status: Number(mode), json: {
          status: mode === '503' ? 'service-unavailable' : 'internal-error',
          query: 'voos', items: [], total: 0, isDemoData: true,
          error: { code: 'TEST', message: 'Erro seguro.' },
        } });
      }
      if (mode === 'race' && new URL(route.request().url()).searchParams.get('q') === 'voos latam') {
        const response = await route.fetch();
        await new Promise((resolve) => { releaseOld = resolve; oldReady(); });
        return route.fulfill({ response });
      }
      return route.continue();
    });
    for (const fault of ['503', '500', 'json', 'offline']) {
      mode = fault; await search('voos');
      assert.equal(await page.locator('.flight-card').count(), 0);
      assert.match(await page.locator('#results-list').textContent(), /Tente novamente/);
      mode = 'normal'; await search('voos');
      assert.equal(await page.locator('.flight-card').count(), 5);
    }
    mode = 'race';
    const ready = new Promise((resolve) => { oldReady = resolve; });
    await page.locator('#search-input').fill('voos latam');
    await page.locator('#search-input').press('Enter'); await ready;
    assert.equal(await page.locator('#results-list').getAttribute('aria-busy'), 'true');
    await search('voos gol');
    const oldResponse = page.waitForResponse((response) => new URL(response.url()).searchParams.get('q') === 'voos latam');
    releaseOld(); await oldResponse;
    await page.evaluate(() => new Promise(requestAnimationFrame));
    assert.equal(await page.locator('.flight-card').count(), 1);
    assert.match(await page.locator('.flight-card').textContent(), /GOL/);
    assert.equal(await page.locator('#results-list').getAttribute('aria-busy'), 'false');
    console.log('OK: loading, 503, 500, JSON inválido, offline, retry e respostas fora de ordem');
    mode = 'hang';
    await search('voos');
    assert.match(await page.locator('#results-list').textContent(), /Tente novamente/);
    assert.equal(await page.locator('.flight-card').count(), 0);
    mode = 'normal'; await search('voos');
    assert.equal(await page.locator('.flight-card').count(), 5);
    console.log('OK: prazo real de 15 segundos encerra loading e permite retry');
    await page.emulateMedia({ reducedMotion: 'reduce' });
    assert(await page.evaluate(() => parseFloat(getComputedStyle(document.querySelector('.flight-card')).animationDuration) < 0.001));
    assert.deepEqual(errors, []);
    fs.writeFileSync(path.join(evidence, 'browser-result.json'), JSON.stringify({
      passed: true, engine: await browser.version(), widths: [1280, 768, 390], uncaughtErrors: errors,
      checks: ['PostgreSQL ponta a ponta', 'teclado', 'chips', 'URL/refresh/vazio', 'XSS', 'loading',
        '503/500/JSON/offline/retry', 'respostas fora de ordem', 'reduced motion', 'sem overflow',
        'q duplicado sem reescrita', 'contraste minimo 4.5', 'timeout real 15s e retry'],
    }, null, 2));
    console.log('OK: redução de movimento; nenhum erro JavaScript não tratado');
  } finally {
    await browser.close();
  }
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
