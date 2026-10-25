#!/usr/bin/env node
// Development-only browser smoke. It never uses an existing RadiWorks runtime.
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { existsSync } from 'node:fs';
import fs from 'node:fs/promises';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const engineDir = path.resolve(process.env.RW_ENGINE_DIR || path.join(scriptDir, '..', '..'));
const webappDir = path.resolve(engineDir, '..', 'webapp');
const python = process.env.RW_SMOKE_PYTHON || path.join(
  engineDir, process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python',
);
const tempRoot = path.resolve(process.env.RW_SMOKE_TMP_ROOT || os.tmpdir());
const host = '127.0.0.1';
const timeoutMs = 20000;
const pythonProgram = [
  'import sys',
  'from pathlib import Path',
  'import uvicorn',
  'from radiworks.main import create_app',
  'home, webapp, port = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])',
  'app = create_app(base_dir=home, data_dir=home / "data",',
  '                 materia_dir=home / "materiaMedica" / "Clarke", webapp_dir=webapp)',
  'uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning", access_log=False)',
].join('\n');

function freePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once('error', reject);
    server.listen(0, host, () => {
      const port = server.address().port;
      server.close((error) => error ? reject(error) : resolve(port));
    });
  });
}

async function waitReady(url, child) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (child.exitCode !== null) throw new Error('Isolated engine exited before readiness');
    try {
      const response = await fetch(url + '/ping', { signal: AbortSignal.timeout(1000) });
      if (response.ok && (await response.json()).result === 'pong') return;
    } catch { /* Wait for only the child server to start. */ }
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
  throw new Error('Isolated engine did not become ready');
}

async function stopChild(child) {
  if (!child || child.exitCode !== null || child.signalCode !== null) return;
  const closed = new Promise((resolve) => child.once('close', resolve));
  child.kill();
  await Promise.race([
    closed,
    new Promise((resolve) => setTimeout(resolve, 5000)),
  ]);
  if (child.exitCode === null && child.signalCode === null) {
    child.kill('SIGKILL');
    await Promise.race([
      closed,
      new Promise((resolve) => setTimeout(resolve, 5000)),
    ]);
  }
}

async function main() {
  assert(existsSync(path.join(engineDir, 'src', 'radiworks', 'main.py')), 'RadiWorks engine missing');
  assert(existsSync(path.join(webappDir, 'index.html')), 'RadiWorks webapp missing');
  assert(existsSync(python), 'Engine venv Python missing; install engine dev dependencies first');
  const resolvedRoot = await fs.realpath(tempRoot);
  const home = path.join(resolvedRoot, 'radiworks-browser-smoke-' + randomUUID());
  assert.equal(path.dirname(home), resolvedRoot);
  let created = false;
  let child;
  let browser;
  let childOutput = '';
  try {
    await fs.mkdir(home, { mode: 0o755 });
    created = true;
    await fs.mkdir(path.join(home, 'data', 'radionics'), { recursive: true });
    await fs.mkdir(path.join(home, 'materiaMedica', 'Clarke'), { recursive: true });
    await fs.writeFile(path.join(home, 'data', 'radionics', 'HOMEOPATHY_SmokeSafe.txt'), 'Arnica\n', 'utf8');
    await fs.writeFile(path.join(home, 'data', 'radionics', 'HOMEOPATHY_SmokeBlocked.txt'), 'Heilt garantiert\n', 'utf8');
    await fs.writeFile(path.join(home, 'data', 'radionics', 'HOMEOPATHY_SmokePage.txt'),
      Array.from({ length: 47 }, (_, index) => `Synthetic sample ${String(index).padStart(2, '0')}`).join('\n') + '\n', 'utf8');
    const port = await freePort();
    const url = 'http://' + host + ':' + port;
    const env = { ...process.env,
      RADIOWORKS_HOME: home,
      RADIOWORKS_DATA_DIR: path.join(home, 'data'),
      RADIOWORKS_SCOPE_MODE: 'local',
      RADIOWORKS_LOCAL_TENANT_ID: 'smoke',
      RADIOWORKS_LOCAL_CLIENT_ID: 'preview',
      RADIOWORKS_LOCAL_JOB_ID: 'smoke',
    };
    delete env.RADIOWORKS_JOURNAL_KEY;
    child = spawn(python, ['-c', pythonProgram, home, webappDir, String(port)], {
      cwd: engineDir, env, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'],
    });
    for (const stream of [child.stdout, child.stderr]) {
      stream.on('data', (chunk) => { childOutput = (childOutput + chunk.toString()).slice(-8000); });
    }
    await waitReady(url, child);
    browser = await chromium.launch({ channel: process.env.RW_SMOKE_BROWSER || 'chrome', headless: false });
    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, permissions: [] });
    await context.route('**/*', (route) => {
      const target = new URL(route.request().url());
      if (target.hostname === host && target.port === String(port)) return route.continue();
      return route.abort();
    });
    const page = await context.newPage();
    const pageErrors = [];
    page.on('pageerror', (error) => pageErrors.push(error.message));
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: timeoutMs });
    await page.locator('#ws-status.online').waitFor({ timeout: timeoutMs });
    assert.match(await page.title(), /RadiWorks/);
    console.log('PASS isolated engine, webapp and WebSocket on allocated loopback port');

    await page.keyboard.press('Tab');
    const headerContrast = await page.evaluate(() => {
      const root = document.documentElement;
      const oldMode = root.getAttribute('data-mode');
      const oldAccent = root.getAttribute('data-accent');
      const header = document.querySelector('.app-header');
      const modeToggle = document.querySelector('#mode-toggle');
      const accentSelect = document.querySelector('#accent-select');
      const canvas = document.createElement('canvas');
      canvas.width = 1;
      canvas.height = 1;
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      const color = (css) => {
        ctx.clearRect(0, 0, 1, 1);
        ctx.fillStyle = css;
        ctx.fillRect(0, 0, 1, 1);
        const [r, g, b, alpha] = ctx.getImageData(0, 0, 1, 1).data;
        return [r, g, b, alpha / 255];
      };
      const blend = (top, bottom, alpha) => top.slice(0, 3).map((v, i) =>
        v * alpha + bottom[i] * (1 - alpha));
      const luminance = (rgb) => [0.2126, 0.7152, 0.0722].reduce((sum, weight, i) => {
        const component = rgb[i] / 255;
        return sum + weight * (component <= 0.04045
          ? component / 12.92 : ((component + 0.055) / 1.055) ** 2.4);
      }, 0);
      const ratio = (a, b) => {
        const [light, dark] = [luminance(a), luminance(b)].sort((x, y) => y - x);
        return (light + 0.05) / (dark + 0.05);
      };
      const samples = [];
      try {
        for (const mode of ['light', 'dark']) {
          root.setAttribute('data-mode', mode);
          for (const accent of ['sage', 'wellenreiter', 'sunrise']) {
            root.setAttribute('data-accent', accent);
            const background = color(getComputedStyle(header).backgroundColor);
            for (const [name, selector] of [
              ['brand-sub', '.brand-sub'],
              ['accent-label', '.header-controls .control-label'],
              ['case-badge', '#case-badge'],
            ]) {
              const style = getComputedStyle(document.querySelector(selector));
              const opacity = Number(style.opacity);
              const text = blend(color(style.color), background, opacity);
              const surface = name === 'case-badge'
                ? blend(color(style.backgroundColor), background,
                  color(style.backgroundColor)[3] * opacity)
                : background;
              samples.push({ mode, accent, name, ratio: ratio(text, surface), minimum: 4.5 });
            }
            for (const [name, target] of [['mode-focus', modeToggle], ['accent-focus', accentSelect]]) {
              target.focus();
              if (!target.matches(':focus-visible')) throw new Error('Keyboard focus not visible on ' + name);
              const focus = getComputedStyle(target);
              samples.push({ mode, accent, name,
                ratio: focus.outlineStyle === 'none' ? 0
                  : ratio(color(focus.outlineColor), background), minimum: 3 });
            }
          }
        }
      } finally {
        if (oldMode === null) root.removeAttribute('data-mode');
        else root.setAttribute('data-mode', oldMode);
        if (oldAccent === null) root.removeAttribute('data-accent');
        else root.setAttribute('data-accent', oldAccent);
      }
      return samples;
    });
    const contrastFailures = headerContrast.filter((sample) => sample.ratio < sample.minimum)
      .map((sample) => `${sample.mode}/${sample.accent}/${sample.name}=${sample.ratio.toFixed(2)} < ${sample.minimum}`);
    assert.deepEqual(contrastFailures, [], 'Header text/focus contrast too low: ' + contrastFailures.join(', '));
    console.log('PASS header text and keyboard focus contrast in six mode/accent combinations');
    if (process.env.RW_SMOKE_CONTRAST_ONLY === '1') return;

    const tabNav = page.locator('nav.tabs');
    assert.equal(await tabNav.getAttribute('role'), 'tablist');
    for (const tab of await tabNav.locator('[role="tab"]').all()) {
      const controls = await tab.getAttribute('aria-controls');
      assert(controls && await page.locator(`#${controls}`).count() === 1, 'Tab has no associated panel');
    }
    await page.locator('#tab-start').focus();
    await page.keyboard.press('ArrowRight');
    assert.equal(await page.evaluate(() => document.activeElement?.id), 'tab-analyse');
    assert.equal(await page.locator('#tab-analyse').getAttribute('aria-selected'), 'true');
    assert.equal(await page.locator('#view-analyse').isVisible(), true);
    await page.keyboard.press('End');
    assert.equal(await page.evaluate(() => document.activeElement?.id), 'tab-info');
    await page.keyboard.press('Home');
    assert.equal(await page.evaluate(() => document.activeElement?.id), 'tab-start');
    assert.equal(await page.locator('#tab-start').getAttribute('tabindex'), '0');
    assert.equal(await page.locator('#tab-analyse').getAttribute('tabindex'), '-1');
    console.log('PASS tab semantics, keyboard navigation and selected panel state');
    await page.locator('#tab-analyse').click();
    await page.evaluate(() => {
      window.__keyboardActions = { submit: 0, gv: 0 };
      document.querySelector('#analyze-form button[type="submit"]').addEventListener('click', (event) => {
        window.__keyboardActions.submit += 1;
        event.preventDefault();
        event.stopImmediatePropagation();
      }, { capture: true, once: true });
      document.querySelector('#gv-btn').addEventListener('click', (event) => {
        window.__keyboardActions.gv += 1;
        event.preventDefault();
        event.stopImmediatePropagation();
      }, { capture: true, once: true });
    });
    await page.locator('#analyze-form button[type="submit"]').focus();
    await page.keyboard.press('Enter');
    assert.deepEqual(await page.evaluate(() => window.__keyboardActions), { submit: 1, gv: 0 },
      'Enter on the analysis submit button must activate that button, not the global GV shortcut');
    console.log('PASS Enter activates the focused analysis button without GV shortcut');
    await page.evaluate(() => document.activeElement.blur());
    await page.keyboard.press('Enter');
    assert.deepEqual(await page.evaluate(() => window.__keyboardActions), { submit: 1, gv: 1 },
      'Enter outside interactive controls must retain the global GV shortcut');
    await page.evaluate(() => document.querySelector('#edit-dialog').showModal());
    await page.locator('#edit-cancel-btn').focus();
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('#edit-dialog').isVisible(), false,
      'Enter on the dialog cancel button must close the modal');
    console.log('PASS body shortcut remains available and modal button keeps native Enter behavior');
    await page.locator('#tab-start').click();
    await page.setViewportSize({ width: 320, height: 640 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1), true,
      'The 320px page has unintended horizontal overflow');
    assert.equal(await tabNav.evaluate((nav) => nav.scrollWidth > nav.clientWidth), true,
      'Mobile tabs should scroll within their own navigation');
    await page.locator('#tab-start').focus();
    await page.keyboard.press('End');
    assert.equal(await page.evaluate(() => {
      const nav = document.querySelector('nav.tabs').getBoundingClientRect();
      const selected = document.querySelector('#tab-info').getBoundingClientRect();
      return selected.left >= nav.left - 1 && selected.right <= nav.right + 1;
    }), true, 'Keyboard-selected final tab is outside the visible tab strip');
    const accessibility = await context.newCDPSession(page);
    const narrowFailures = [];
    const unnamedControls = [];
    const namedRoles = new Set([
      'button', 'textField', 'textbox', 'comboBox', 'checkBox', 'radioButton', 'slider', 'link', 'tab',
    ]);
    await page.locator('#settings-booleans input').first().waitFor({ state: 'attached' });
    await page.locator('#manifest-list dt').first().waitFor({ state: 'attached' });
    for (const tab of await tabNav.locator('[role="tab"]').all()) {
      await tab.click();
      const tabName = (await tab.textContent()).trim();
      await page.locator(`#${await tab.getAttribute('aria-controls')}`).waitFor({ state: 'visible' });
      const width = await page.evaluate(() => ({
        content: document.documentElement.scrollWidth,
        viewport: window.innerWidth,
      }));
      if (width.content > width.viewport + 1) narrowFailures.push({ tab: tabName, ...width });
      const { nodes } = await accessibility.send('Accessibility.getFullAXTree');
      for (const node of nodes) {
        if (node.ignored || !node.backendDOMNodeId || !namedRoles.has(node.role?.value)) continue;
        if ((node.name?.value || '').trim()) continue;
        const { node: domNode } = await accessibility.send('DOM.describeNode', {
          backendNodeId: node.backendDOMNodeId,
        });
        const attrs = Object.fromEntries(Array.from({ length: domNode.attributes.length / 2 }, (_, i) => [
          domNode.attributes[i * 2], domNode.attributes[i * 2 + 1],
        ]));
        unnamedControls.push({ tab: tabName, role: node.role.value, tag: domNode.nodeName,
          id: attrs.id || '', type: attrs.type || '' });
      }
    }
    await accessibility.detach();
    assert.deepEqual(narrowFailures, [], 'Narrow viewport overflows in module view(s)');
    assert.deepEqual(unnamedControls, [], 'Visible interactive controls lack accessible names');
    await page.setViewportSize({ width: 390, height: 844 });
    console.log('PASS 320px reflow across ten views, accessible control names and keyboard-visible tabs');
    await page.locator('#tab-images').click();
    assert.equal(await page.getByLabel('Bilddateien für Schichten auswählen', { exact: true }).count(), 1);
    assert.equal(await page.getByLabel('Bild für Area-Scan auswählen', { exact: true }).count(), 1);
    console.log('PASS image file inputs have specific accessible names');

    await page.locator('#tab-cases').click();
    await page.waitForFunction(() => document.querySelector('#case-list-empty')?.textContent === 'Noch keine Fälle.');
    assert.equal(await page.locator('#case-list').isVisible(), false);
    assert.equal(await page.locator('#case-refresh-btn').isVisible(), false);
    console.log('PASS empty case list is distinguishable from loading and error');

    await page.locator('#tab-analyse').click();
    await page.waitForFunction(() =>
      [...document.querySelectorAll('#db-select option')].some((option) =>
        option.value === 'HOMEOPATHY_SmokeSafe'));
    await page.locator('#db-select').selectOption('HOMEOPATHY_SmokePage');
    await page.locator('#db-search').fill('SmokeSafe');
    assert.equal(await page.locator('#db-select').inputValue(), 'HOMEOPATHY_SmokePage');
    assert.equal(await page.locator('#db-select option:not([data-group="true"])').count(), 2,
      'Filtered list should retain only the prior selection and matching database');
    await page.locator('#db-select').selectOption('HOMEOPATHY_SmokeSafe');
    assert.equal(await page.evaluate(() => localStorage.getItem('radiworks_selected_db')),
      'HOMEOPATHY_SmokeSafe');
    await page.locator('#db-search-clear').click();
    assert.equal(await page.locator('#db-select').inputValue(), 'HOMEOPATHY_SmokeSafe');
    console.log('PASS filtered database selection persists and supplies analysis');
    await page.locator('#seed-input').fill('7');
    await page.locator('#mode-select').selectOption('seeded');
    await page.locator('#analyze-form button[type="submit"]').click();
    await page.locator('#result-body').getByText('Arnica', { exact: false }).waitFor();
    assert.match(await page.locator('#draft-copyguard').textContent(), /allow/);
    await page.locator('#draft-ready-btn').click();
    await page.waitForFunction(() => document.querySelector('#draft-status')?.textContent?.includes('ready'));
    await page.locator('#draft-promote-btn').click();
    await page.waitForFunction(() => document.querySelector('#draft-hint')?.textContent?.includes('Freigegeben'));
    const queued = await (await fetch(url + '/broadcast/queue')).json();
    assert(queued.queued.length + queued.active.length > 0, 'Promote did not create a virtual queue entry');
    assert.equal((await fetch(url + '/broadcast/all', { method: 'DELETE' })).status, 200);
    console.log('PASS seeded analysis, explicit ready/promote, virtual queue and stop');

    const createdCase = await fetch(url + '/cases', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'S4 Browser Fall', description: 'Synthetisch' }),
    });
    assert.equal(createdCase.status, 200, 'Synthetic case creation failed');

    await page.locator('#tab-analyse').click();
    await page.locator('#db-select').selectOption('HOMEOPATHY_SmokeBlocked');
    await page.locator('#analyze-form button[type="submit"]').click();
    await page.locator('#result-body').getByText('[CopyGuard: Text zurückgehalten]', { exact: true }).waitFor();
    assert.match(await page.locator('#draft-copyguard').textContent(), /block/);
    const blockedVisible = await page.locator('#result-body').getByText('Heilt garantiert', { exact: false }).count();
    assert.equal(await page.locator('#result-body .btn-broadcast').first().isDisabled(), true,
      'Redacted rate still has an active direct broadcast button');
    const current = await (await fetch(url + '/analysis/current')).json();
    assert.equal(JSON.stringify(current).includes('Heilt garantiert'), false,
      'Current analysis API exposes the blocked rate');
    await page.locator('#draft-ready-btn').click();
    await page.waitForFunction(() => document.querySelector('#draft-status')?.textContent?.includes('ready'));
    let reportRejection;
    const rejectionPromise = new Promise((resolve) => { reportRejection = resolve; });
    page.once('dialog', async (dialog) => {
      const message = dialog.message();
      await dialog.dismiss();
      reportRejection(message);
    });
    await page.locator('#draft-promote-btn').click();
    const rejection = await Promise.race([
      rejectionPromise,
      new Promise((_, reject) => setTimeout(() => reject(new Error('Promote rejection dialog missing')), 10000)),
    ]);
    const finalQueue = await (await fetch(url + '/broadcast/queue')).json();
    assert.equal(finalQueue.queued.length + finalQueue.active.length, 0, 'Blocked draft reached queue');
    assert.match(rejection, /Promote blockiert/);
    assert.deepEqual(pageErrors, [], 'Browser JavaScript errors');
    console.log('PASS blocked draft rejected before queue; browser JavaScript errors: 0');
    assert.equal(blockedVisible, 0, 'S4 BLOCK: CopyGuard-blocked rate name is visible in analysis result');
    console.log('PASS CopyGuard-blocked rate hidden in browser and current API; direct action disabled');

    await page.locator('#edit-case-btn').click();
    await page.locator('#edit-desc').fill('Heilt garantiert');
    let resolveEditAlert;
    const editAlert = new Promise((resolve) => { resolveEditAlert = resolve; });
    page.once('dialog', async (dialog) => {
      const message = dialog.message();
      await dialog.dismiss();
      resolveEditAlert(message);
    });
    await page.locator('#edit-save-btn').click();
    const editMessage = await Promise.race([
      editAlert,
      new Promise((_, reject) => setTimeout(() => reject(new Error('Case edit rejection not shown')), 5000)),
    ]);
    assert.match(editMessage, /Fall konnte nicht gespeichert werden/);
    assert.equal(await page.locator('#edit-dialog').isVisible(), true);
    await page.locator('#edit-desc').fill('Sicherer Text');
    await page.locator('#edit-save-btn').click();
    await page.locator('#edit-dialog').waitFor({ state: 'hidden' });
    const savedCase = await (await fetch(url + '/cases/current')).json();
    assert.equal(savedCase.description, 'Sicherer Text');
    assert.equal(JSON.stringify(savedCase).includes('Heilt garantiert'), false);
    assert.deepEqual(pageErrors, [], 'Browser JavaScript errors after case edit');
    console.log('PASS rejected case edit is explained; safe metadata edit preserves projected analysis');

    await page.locator('#tab-cases').click();
    await page.locator('#case-name').fill('S4 Browser Fall');
    await page.locator('#case-desc').fill('Fälle-Ansicht geprüft');
    await page.locator('#case-save-btn').click();
    await page.waitForFunction(async () => {
      const response = await fetch('/cases/current');
      return (await response.json()).description === 'Fälle-Ansicht geprüft';
    });
    const caseViewSaved = await (await fetch(url + '/cases/current')).json();
    assert.equal(JSON.stringify(caseViewSaved).includes('Heilt garantiert'), false);
    assert.deepEqual(pageErrors, [], 'Browser JavaScript errors after Cases view save');
    console.log('PASS Cases view saves metadata without exposing the blocked analysis');

    await page.locator('#tab-images').click();
    const syntheticPng = Buffer.from(
      'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScL/nwAAAABJRU5ErkJggg==',
      'base64',
    );
    await page.locator('#img-files').setInputFiles({
      name: 'Heilt garantiert.png', mimeType: 'image/png', buffer: syntheticPng,
    });
    assert.equal(await page.locator('#img-files').inputValue(), '',
      'S4 BLOCK: native file input still exposes the local filename');
    assert.match(await page.locator('#img-selection').textContent(), /1 Bild ausgewählt/);
    await page.locator('#img-analyze-btn').click();
    await page.locator('#img-body tr').first().waitFor();
    assert.equal((await page.locator('#img-body').textContent()).includes('Heilt garantiert'), false,
      'S4 BLOCK: local image filename appears in analysis table');
    assert.match(await page.locator('#img-body').textContent(), /Bild 1/);
    await page.locator('#area-file').setInputFiles({
      name: 'Heilt garantiert.png', mimeType: 'image/png', buffer: syntheticPng,
    });
    assert.equal(await page.locator('#area-file').inputValue(), '',
      'S4 BLOCK: area file input still exposes the local filename');
    await page.waitForFunction(() => document.querySelector('#area-out')?.textContent?.includes('Geladen:'));
    assert.equal((await page.locator('#area-out').textContent()).includes('Heilt garantiert'), false,
      'S4 BLOCK: area status exposes the local filename');
    assert.deepEqual(pageErrors, [], 'Browser JavaScript errors after image analysis');
    console.log('PASS local image filenames withheld in file controls, table and area status');

    await page.locator('#tab-rates').click();
    await page.waitForFunction(() =>
      [...document.querySelectorAll('#pad-db option')].some((option) =>
        option.value === 'HOMEOPATHY_SmokeBlocked'));
    await page.locator('#pad-db').selectOption('HOMEOPATHY_SmokeBlocked');
    const stickPosition = await fetch(url + '/stickpad/position', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ x: 640, y: 400 }),
    });
    assert.equal(stickPosition.status, 200);
    await page.locator('#pad-analyze-btn').click();
    await page.locator('#pad-result-body').getByText('[CopyGuard: Text zurückgehalten]').waitFor();
    assert.equal((await page.locator('#pad-result-body').textContent()).includes('Heilt garantiert'), false,
      'S4 BLOCK: Stick-Pad table exposes a blocked rate');
    const stickQueue = await (await fetch(url + '/broadcast/queue')).json();
    assert.equal(stickQueue.queued.length + stickQueue.active.length, 0);
    assert.deepEqual(pageErrors, [], 'Browser JavaScript errors after Stick-Pad analysis');
    console.log('PASS Stick-Pad blocked rate projected in browser; virtual queue remains empty');

    for (const name of ['Heilt garantiert', 'Diagnose sicher']) {
      const response = await fetch(url + '/cases', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description: 'Synthetischer Fall' }),
      });
      assert.equal(response.status, 200);
    }
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.locator('#tab-cases').click();
    const protectedRows = page.locator('#case-list .case-row').filter({ hasText: '[CopyGuard: Text zurückgehalten]' });
    await protectedRows.first().waitFor();
    assert.equal(await protectedRows.count(), 2, 'Two protected cases must remain independently selectable');
    const loadNames = [];
    const statisticsNames = [];
    for (let index = 0; index < 2; index += 1) {
      const actions = protectedRows.nth(index).getByRole('button');
      loadNames.push(await actions.nth(0).ariaSnapshot());
      statisticsNames.push(await actions.nth(1).ariaSnapshot());
    }
    assert.notEqual(loadNames[0], loadNames[1], 'Protected case load buttons need distinct accessible names');
    assert.notEqual(statisticsNames[0], statisticsNames[1], 'Protected case statistics buttons need distinct accessible names');
    assert(![...loadNames, ...statisticsNames].some((name) => /Heilt garantiert|Diagnose sicher/.test(name)),
      'Case action names must not disclose the protected raw names');
    const listedCases = await (await fetch(url + '/cases')).json();
    const protectedRefs = listedCases.entries
      .filter((entry) => entry.name === '[CopyGuard: Text zurückgehalten]')
      .map((entry) => entry.ref);
    assert.equal(protectedRefs.length, 2);
    const references = [];
    for (let index = 0; index < 2; index += 1) {
      await protectedRows.nth(index).getByRole('button').first().click();
      await page.waitForFunction((expected) => localStorage.getItem('radiworks_active_case') === `ref:${expected}`,
        protectedRefs[index]);
      await page.waitForFunction(async (expected) => {
        const response = await fetch('/cases/current/ref');
        return response.ok && (await response.json()).ref === expected;
      }, protectedRefs[index]);
      await page.waitForFunction(() => document.querySelector('#case-name')?.value === '[CopyGuard: Text zurückgehalten]');
      await page.waitForFunction((ordinal) =>
        document.querySelector('#case-load-status')?.textContent === `Fall ${ordinal} geladen.`, index + 1);
      await protectedRows.nth(index).getByRole('button').nth(1).click();
      await page.waitForFunction((ordinal) =>
        document.querySelector('#case-load-status')?.textContent ===
          `Für Fall ${ordinal} sind noch keine Analyseergebnisse vorhanden.`, index + 1);
      const currentRef = await (await fetch(url + '/cases/current/ref')).json();
      references.push(currentRef.ref);
    }
    assert.notEqual(references[0], references[1], 'Protected cases collapsed to one identity');
    await page.waitForFunction((expected) => localStorage.getItem('radiworks_active_case') === `ref:${expected}`,
      references[1]);
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForFunction(async (expected) => {
      const response = await fetch('/cases/current/ref');
      return response.ok && (await response.json()).ref === expected;
    }, references[1]);
    assert.equal((await page.locator('#case-list').textContent()).includes('Heilt garantiert'), false);
    assert.deepEqual(pageErrors, [], 'Browser JavaScript errors after protected case reload');
    console.log('PASS distinct protected cases load, statistics and local reload without raw name');

    await page.evaluate(() => {
      Object.defineProperty(navigator, 'mediaDevices', { configurable: true, value: {
        getUserMedia: async () => new MediaStream(),
        enumerateDevices: async () => [{ kind: 'videoinput', deviceId: 'synthetic-camera', label: 'Heilt garantiert' }],
      } });
    });
    await page.locator('#tab-entropy').click();
    await page.locator('#cam-start-btn').click();
    await page.locator('#cam-select option').filter({ hasText: 'Webcam 1' }).waitFor({ state: 'attached' });
    assert.equal((await page.locator('#cam-select').textContent()).includes('Heilt garantiert'), false);
    await page.locator('#cam-stop-btn').click();
    await page.evaluate(() => {
      Object.defineProperty(navigator, 'mediaDevices', { configurable: true, value: {
        getUserMedia: async () => { throw new DOMException('Heilt garantiert', 'NotAllowedError'); },
      } });
    });
    await page.locator('#cam-start-btn').click();
    await page.waitForFunction(() => document.querySelector('#cam-status')?.textContent === 'Kamera-Zugriff verweigert.');
    assert.equal((await page.locator('#cam-status').textContent()).includes('Heilt garantiert'), false);
    assert.deepEqual(pageErrors, [], 'Browser JavaScript errors after camera error');
    console.log('PASS camera label and browser error withheld from visible text');

    await page.addInitScript(() => {
      const NativeWebSocket = window.WebSocket;
      window.__smokeSockets = [];
      window.WebSocket = class extends NativeWebSocket {
        constructor(...args) {
          super(...args);
          window.__smokeSockets.push(this);
        }
      };
    });
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.locator('#ws-status.online').waitFor({ timeout: 10000 });
    await page.evaluate(() => window.__smokeSockets.at(-1).close());
    await page.locator('#ws-status.offline').waitFor({ timeout: 10000 });
    await page.locator('#ws-status.online').waitFor({ timeout: 15000 });
    assert.deepEqual(pageErrors, [], 'Browser JavaScript errors after WebSocket reconnect');
    console.log('PASS WebSocket offline indicator and automatic reconnect');

    await context.close(); // Release first-view sockets before the separate failure-state probe.
    const errorContext = await browser.newContext({ viewport: { width: 390, height: 844 } });
    await errorContext.route('**/*', (route) => {
      const target = new URL(route.request().url());
      if (target.hostname === host && target.port === String(port)) return route.continue();
      return route.abort();
    });
    const errorPage = await errorContext.newPage();
    const errorPageErrors = [];
    errorPage.on('pageerror', (error) => errorPageErrors.push(error.message));
    let releaseCasesRequest;
    const casesRequestGate = new Promise((resolve) => { releaseCasesRequest = resolve; });
    await errorPage.route('**/cases', async (route) => {
      await casesRequestGate;
      await route.abort();
    });
    await errorPage.goto(url, { waitUntil: 'domcontentloaded' });
    await errorPage.locator('#tab-cases').click();
    await errorPage.waitForFunction(() =>
      document.querySelector('#case-list-empty')?.textContent?.includes('wird geladen'));
    releaseCasesRequest();
    await errorPage.waitForFunction(() =>
      document.querySelector('#case-list-empty')?.textContent?.includes('nicht erreichbar'));
    assert.equal(await errorPage.locator('#case-refresh-btn').isVisible(), true);
    await errorPage.unroute('**/cases');
    await errorPage.locator('#case-refresh-btn').click();
    await errorPage.locator('#case-list .case-row').first().waitFor();
    assert.equal(await errorPage.locator('#case-refresh-btn').isVisible(), false);
    await errorPage.route('**/cases/ref/*/activate', (route) => route.abort());
    await errorPage.locator('#case-list .case-row').first().getByRole('button', { name: 'Laden' }).click();
    await errorPage.waitForFunction(() =>
      document.querySelector('#case-load-status')?.textContent?.includes('nicht geladen'));
    await errorPage.unroute('**/cases/ref/*/activate');
    await errorPage.locator('#case-list .case-row').first().getByRole('button', { name: 'Laden' }).click();
    await errorPage.waitForFunction(() =>
      localStorage.getItem('radiworks_active_case')?.startsWith('ref:') &&
      document.querySelector('#case-load-status')?.textContent === 'Fall 1 geladen.');
    assert.deepEqual(errorPageErrors, [], 'Browser JavaScript errors after case error/retry');
    await errorPage.locator('#tab-analyse').click();
    await errorPage.locator('#db-select').selectOption('HOMEOPATHY_SmokePage');
    await errorPage.locator('#analyze-form button[type="submit"]').click();
    await errorPage.waitForFunction(() => document.querySelector('#result-count')?.textContent === '47 Raten');
    assert.equal(await errorPage.locator('#result-body .recurrence-marker').count() > 0, true);
    assert.equal(await errorPage.locator('#result-body tr.row-recurrence').first().locator('td').first()
      .evaluate((cell) => getComputedStyle(cell).backgroundColor), 'rgba(0, 0, 0, 0)');
    assert.match(await errorPage.locator('#result-gv-hint').textContent(), /keine zeitliche Entwicklung/);
    assert.match(await errorPage.locator('#draft-panel').textContent(), /eigene Abläufe/);
    await errorPage.locator('#gv-btn').click();
    await errorPage.waitForFunction(() => document.querySelector('#gv-manual-steps')?.textContent?.endsWith('1'));
    await errorPage.locator('#gv-btn').click();
    await errorPage.waitForFunction(() => document.querySelector('#gv-manual-steps')?.textContent?.endsWith('2'));
    const prior = await errorPage.evaluate(() => Number(document.querySelector('#result-body [data-rate-gv]')?.dataset.rateGv));
    assert(prior > 0, 'First-page measured rate GV missing before page fork');
    await errorPage.locator('.pager-btn', { hasText: /^2$/ }).click();
    await errorPage.locator('#gv-later-page-btn').click();
    await errorPage.waitForFunction(() =>
      document.querySelector('#gv-page-status')?.textContent?.includes('Seite 2 abgeschlossen'),
      null, { timeout: 45000 });
    assert.equal(await errorPage.evaluate(() => Number(document.querySelector('#result-body [data-rate-gv]')?.dataset.rateGv) > 0), true);
    const after = await errorPage.request.get(url + '/cases/current');
    assert.equal(after.ok(), true);
    const sessions = (await after.json()).sessionList;
    assert.equal(sessions.length >= 2, true);
    assert.equal(sessions.at(-1).analysisResult.rateObjects[0].gv, prior);
    assert.equal(sessions.at(-1).gvState.pageStart, 21);
    await errorPage.locator('#session-prev').click();
    await errorPage.waitForFunction((draftId) =>
      document.querySelector('#draft-body')?.dataset.draftId === draftId,
      sessions.at(-2).draftId);
    await errorPage.locator('#session-next').click();
    await errorPage.waitForFunction((draftId) =>
      document.querySelector('#draft-body')?.dataset.draftId === draftId,
      sessions.at(-1).draftId);
    assert.deepEqual(errorPageErrors, [], 'Browser JavaScript errors after later-page GV round');
    console.log('PASS later-page GV creates full successor session and preserves first-page GV');
    await errorPage.locator('#tab-settings').click();
    assert.match(await errorPage.locator('#settings-booleans').textContent(), /dynamic\.adjustments.*ohne Wirkung im Prototyp/s);
    await errorContext.close();
    console.log('PASS case list unavailable, explicit retry and failed case load feedback');
  } catch (error) {
    console.error('FAIL ' + error.message);
    if (childOutput) console.error('Engine output (tail):\n' + childOutput);
    process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
    await stopChild(child);
    if (created) {
      for (let attempt = 0; attempt < 10; attempt += 1) {
        try {
          await fs.rm(home, { recursive: true, force: true });
          break;
        } catch (error) {
          if (!['EBUSY', 'EPERM'].includes(error.code) || attempt === 9) throw error;
          await new Promise((resolve) => setTimeout(resolve, 300));
        }
      }
    }
    console.log('CLEANUP isolated browser and runtime home');
  }
}

await main();
