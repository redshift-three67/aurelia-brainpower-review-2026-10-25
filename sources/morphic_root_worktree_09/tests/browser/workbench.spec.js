const { test, expect } = require('@playwright/test');

function captureErrors(page) {
  const errors = [];
  page.on('console', msg => { if (msg.type() === 'error') errors.push(`console: ${msg.text()}`); });
  page.on('pageerror', err => errors.push(`pageerror: ${err.message}`));
  page.on('requestfailed', req => errors.push(`request: ${req.url()} ${req.failure()?.errorText || ''}`));
  page.on('response', response => {
    if (response.status() >= 400) errors.push(`response: ${response.status()} ${response.url()}`);
  });
  return errors;
}

const SCAN_PROFILE_FINGERPRINTS = Object.freeze({
  1: '1'.repeat(64),
  2: '2'.repeat(64),
  3: '3'.repeat(64),
  4: '4'.repeat(64),
  5: '5'.repeat(64),
});

function buildScanProfileCatalog({
  profileLevel = 3,
  profiles = [{id: `level-${profileLevel}`, label: `Level ${profileLevel}`}],
  activeSources = [],
  authority = {},
} = {}) {
  const fingerprint = authority.fingerprint || SCAN_PROFILE_FINGERPRINTS[profileLevel];
  return {
    schema_version: 1,
    profile_level: profileLevel,
    pool_authority: {
      source: authority.source || 'legacy',
      label: authority.label || 'Legacy',
      revision: authority.revision ?? null,
      revision_short: authority.revision_short ?? null,
      fingerprint,
      fingerprint_short: authority.fingerprint_short || fingerprint.slice(0, 12),
    },
    internal: {count: profiles.length, profiles},
    external: {
      count: 0,
      profiles: [],
      integration_status: 'registry_only',
      scan_effect: false,
      activation_available: false,
      activation_gate: 'gate_14',
      active_source_count: activeSources.length,
      active_sources: activeSources.map(source => ({
        ...source,
        scan_effect: false,
        reason_code: 'registry_metadata_only',
      })),
    },
    total_scan_profiles: profiles.length,
  };
}

function createDeferred() {
  let resolve;
  let released = false;
  const promise = new Promise(done => { resolve = done; });
  return {
    promise,
    release() {
      if (released) return false;
      released = true;
      resolve();
      return true;
    },
  };
}

async function releaseDeferredRoutes(page, ...deferreds) {
  deferreds.forEach(deferred => deferred.release());
  if (!page.isClosed()) await page.unrouteAll({behavior: 'ignoreErrors'});
}

async function waitForScanProfilePool(page) {
  await expect.poll(() => page.evaluate(() => {
    const state = window.MorphicWorkbenchState;
    const level = Number(document.querySelector('[name="profile_level"]')?.value || 3);
    const fingerprint = String(state?.scanProfileCatalog?.pool_authority?.fingerprint || '');
    return state?.scanProfileCatalogStatus === 'ready'
      && Number(state?.scanProfileCatalogLevel) === level
      && Number(state?.scanProfileCatalog?.profile_level) === level
      && /^[0-9a-f]{64}$/.test(fingerprint);
  })).toBe(true);
}

async function navigateToReview(page, {profileLevel} = {}) {
  await page.locator('#btn-next').click();
  await page.locator('[name="last_name"]').fill('Browser');
  await page.locator('[name="first_name"]').fill('Gate Three');
  await page.locator('[name="birth_date"]').fill('09041966');
  await page.locator('[name="birth_place"]').fill('Augsburg');
  await page.locator('#consent-local').check();
  await page.locator('#consent-safety').check();
  await page.locator('#btn-next').click();
  await page.locator('[name="focus"]').fill('Scanprofil-Pool prüfen');
  await page.locator('[name="main_symptom"]').fill('Registry-Quellen transparent prüfen');
  if (profileLevel !== undefined) {
    await page.locator('[name="profile_level"]').selectOption(String(profileLevel));
  }
  await page.locator('#btn-next').click();
  await page.locator('#btn-next').click();
  await page.locator('#btn-next').click();
  await expect(page.locator('.wizard-step.active')).toContainText('Review & Freigabe');
}

async function fillSyntheticScanStartForm(page, overrides = {}) {
  await waitForScanProfilePool(page);
  const values = {
    last_name: 'Browser', first_name: 'Synthetic', birth_date: '09041966',
    birth_place: 'Augsburg', focus: 'QA Fokus', main_symptom: 'QA Kontext',
    ...overrides,
  };
  await page.evaluate(fields => {
    Object.entries(fields).forEach(([name, value]) => {
      document.querySelector(`[name="${name}"]`).value = value;
    });
    document.querySelector('#consent-local').checked = true;
    document.querySelector('#consent-safety').checked = true;
  }, values);
}

async function prepareSyntheticHarmonizationStart(page, payload) {
  await page.evaluate(body => {
    const reportId = body.report_id;
    reportAuthority = createReportAuthorityState(caseGeneration);
    projectReportAuthority(reportAuthority);
    const catalogEffects = transitionReportAuthority({
      type: REPORT_AUTHORITY_EVENT.CATALOG_REQUESTED,
      generation: caseGeneration,
    });
    const catalogRequest = catalogEffects.find(effect => effect.type === 'LOAD_CATALOG').request;
    transitionReportAuthority({
      type: REPORT_AUTHORITY_EVENT.CATALOG_ACCEPTED,
      generation: caseGeneration,
      request: catalogRequest,
      entries: [{id: reportId, session_id: 'synthetic-harmonization', kind: 'TXT', size: 1}],
    });
    const previewEffects = transitionReportAuthority({
      type: REPORT_AUTHORITY_EVENT.PREVIEW_REQUESTED,
      generation: caseGeneration,
      reportId,
      intent: 'manual',
    });
    const previewRequest = previewEffects.find(effect => effect.type === 'LOAD_PREVIEW').request;
    transitionReportAuthority({
      type: REPORT_AUTHORITY_EVENT.PREVIEW_SUCCEEDED,
      request: previewRequest,
      view: {reportId, mode: 'text', kind: 'TXT', title: reportId, content: 'synthetic', size: 1},
    });
    syncReportHarmonizationEffect(reportAuthority.canHarmonize);
    MorphicWorkbenchState.workbenchMode = body.workbench_mode;
    const form = document.querySelector('#harmonization-form');
    Object.entries(body).forEach(([name, value]) => {
      if (name === 'report_id' || name === 'workbench_mode') return;
      const control = form.elements.namedItem(name);
      if (typeof value === 'boolean') control.checked = value;
      else control.value = String(value);
    });
  }, payload);
}

async function clearSyntheticHarmonizationRun(page) {
  if (page.isClosed()) return;
  await page.evaluate(() => {
    if (typeof harmonizationPollTimer !== 'undefined') {
      if (harmonizationPollTimer) clearTimeout(harmonizationPollTimer);
      harmonizationPollTimer = null;
    }
    const state = window.MorphicWorkbenchState;
    if (!state) return;
    reportAuthority = createReportAuthorityState(caseGeneration);
    projectReportAuthority(reportAuthority);
    state.activeHarmonizationJobId = null;
    state.harmonizationStartPending = false;
    state.harmonizationRunActive = false;
  });
}

async function clearSyntheticScanRun(page) {
  if (page.isClosed()) return;
  await page.evaluate(() => {
    if (typeof jobPollTimer !== 'undefined') {
      if (jobPollTimer) clearTimeout(jobPollTimer);
      jobPollTimer = null;
    }
    const state = window.MorphicWorkbenchState;
    if (!state) return;
    state.activeJobId = null;
    state.scanStartPending = false;
    state.scanRunActive = false;
  });
}

test('adaptive limits sind initial und nach neuem Fall bewusst aus', async ({ page }) => {
  const errors = captureErrors(page);
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');

  const adaptive = page.locator('[name="adaptive_limits"]');
  await expect(adaptive).not.toBeChecked();
  expect(await page.evaluate(() => formScanPayload().adaptive_limits)).toBe(false);

  await page.evaluate(() => enterStep(3, false));
  await adaptive.check();
  expect(await page.evaluate(() => formScanPayload().adaptive_limits)).toBe(true);
  await page.evaluate(() => MorphicWorkbenchRender.renderReviewCards(
    formScanPayload(), {components: {}}
  ));
  await expect(page.locator('#review-profile')).toContainText(
    'aktiv (Phase-2-Detail-Cap; höchstens 5 ownergebundene Top-Profile)'
  );

  expect(await page.evaluate(() => resetWorkbenchForNewCase())).toBe(true);
  await expect(adaptive).not.toBeChecked();
  expect(await page.evaluate(() => formScanPayload().adaptive_limits)).toBe(false);
  expect(errors).toEqual([]);
});

test('local AI is per-case default-off and reaches preview and start only after opt-in', async ({ page }) => {
  const errors = captureErrors(page);
  const previewBodies = [];
  const startBodies = [];
  const templateBodies = [];
  await page.route('**/api/workbench/templates', async route => {
    if (route.request().method() !== 'POST') return route.continue();
    templateBodies.push(route.request().postDataJSON());
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({
        template_id: 'tpl-local-ai', name: 'Session', draft: {},
        created_at: '2026-07-30T00:00:00Z', updated_at: '2026-07-30T00:00:00Z',
      }),
    });
  });
  await page.route('**/api/scan/preview', async route => {
    previewBodies.push(route.request().postDataJSON());
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({command: ['scan', 'preview', 'local-ai-opt-in']}),
    });
  });
  await page.route('**/api/scan/jobs', async route => {
    if (route.request().method() !== 'POST') return route.continue();
    startBodies.push(route.request().postDataJSON());
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({job_id: 'scan-local-ai'}),
    });
  });
  await page.route('**/api/scan/jobs/scan-local-ai', async route => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({
        status: 'running', progress_percent: 1,
        completed_substeps: [], completed_stage_ids: [],
      }),
    });
  });
  await page.route('**/api/scan/jobs/scan-local-ai/stop', async route => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({status: 'stopped'}),
    });
  });

  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    const localAi = page.locator('#local-ai-enabled');
    await expect(localAi).not.toBeChecked();
    expect(await page.evaluate(() => formScanPayload().local_ai_enabled)).toBe(false);

    await page.locator('#btn-next').click();
    await page.locator('[name="last_name"]').fill('Browser');
    await page.locator('[name="first_name"]').fill('Local AI');
    await page.locator('[name="birth_date"]').fill('09041966');
    await page.locator('[name="birth_place"]').fill('Augsburg');
    await page.locator('#consent-local').check();
    await page.locator('#consent-safety').check();
    await page.locator('#btn-next').click();
    await page.locator('[name="focus"]').fill('Lokale Deutung prüfen');
    await page.locator('[name="main_symptom"]').fill('Explizites Opt-in prüfen');
    await page.locator('#btn-next').click();
    await expect(page.locator('.wizard-step.active')).toContainText('Analyseprofil');
    await page.locator('#btn-next').click();
    await expect(page.locator('.wizard-step.active')).toContainText('Hardware & Realtime');
    await expect(localAi).toBeVisible();

    await localAi.check();
    expect(await page.evaluate(() => formScanPayload().local_ai_enabled)).toBe(true);
    await page.locator('#btn-next').click();
    await expect(page.locator('.wizard-step.active')).toContainText('Review & Freigabe');
    await expect(page.locator('#review-profile')).toContainText('Lokale KI');
    await expect(page.locator('#review-profile')).toContainText('aktiviert');
    await waitForScanProfilePool(page);

    await page.evaluate(() => {
      document.querySelector('#template-sensitive-consent').checked = true;
      document.querySelector('#save-template-button').click();
    });
    await expect.poll(() => templateBodies.length).toBe(1);
    expect(Object.prototype.hasOwnProperty.call(
      templateBodies[0].draft, 'local_ai_enabled'
    )).toBe(false);

    await page.locator('#preview-button').click();
    await expect.poll(() => previewBodies.length).toBe(1);
    await page.locator('#start-analysis-button').click();
    await expect.poll(() => startBodies.length).toBe(1);
    expect(previewBodies[0].local_ai_enabled).toBe(true);
    expect(startBodies[0].local_ai_enabled).toBe(true);
    await expect.poll(() => page.evaluate(() => ({
      activeJobId: MorphicWorkbenchState.activeJobId,
      scanStartPending: MorphicWorkbenchState.scanStartPending,
      pendingMutations: MorphicWorkbenchState.pendingMutations,
    }))).toEqual({
      activeJobId: 'scan-local-ai',
      scanStartPending: false,
      pendingMutations: 0,
    });

    expect(await page.evaluate(() => enterStep(10, false))).toBe(true);
    await expect(page.locator('#new-case-button')).toBeVisible();
    await expect(page.locator('#new-case-button')).toBeEnabled();
    await page.locator('#new-case-button').click();
    await expect(localAi).not.toBeChecked();
    expect(await page.evaluate(() => formScanPayload().local_ai_enabled)).toBe(false);
    expect(errors).toEqual([]);
  } finally {
    await clearSyntheticScanRun(page);
  }
});

test('client gate shows visible requirements and accepts empty optional context', async ({ page }) => {
  const errors = captureErrors(page);
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  await page.locator('#btn-next').click();

  await page.locator('[name="last_name"]').fill('QA');
  await page.locator('[name="first_name"]').fill('Optional');
  await page.locator('[name="birth_date"]').fill('01011990');
  await page.locator('[name="birth_place"]').fill('Teststadt');
  await expect(page.locator('[name="birth_time"]')).toHaveValue('');
  await expect(page.locator('[name="email"]')).toHaveValue('');
  await expect(page.locator('[name="notes"]')).toHaveValue('');

  await page.locator('#btn-next').click();
  await expect(page.locator('.wizard-step.active')).toContainText('Klient / Kontext');
  await expect(page.locator('#wizard-navigation-state')).toHaveText(
    'Bitte zuerst beide Einwilligungen in Phase 2 bestaetigen.'
  );

  await page.locator('#consent-local').check();
  await page.locator('#consent-safety').check();
  await page.locator('#btn-next').click();
  await expect(page.locator('.wizard-step.active')).toContainText('Fokus & Zielsetzung');
  await expect(page.locator('#wizard-navigation-state')).toHaveText('');
  expect(errors).toEqual([]);
});

test('desktop gates, mutation boundary, server stops and privacy reset', async ({ page }) => {
  const errors = captureErrors(page);
  const stopCalls = [];
  await page.route('**/api/scan/jobs/scan-sensitive/stop', async route => {
    stopCalls.push('scan');
    await route.fulfill({contentType: 'application/json', body: JSON.stringify({status: 'stopped'})});
  });
  await page.route('**/api/harmonization/jobs/harm-sensitive/stop', async route => {
    stopCalls.push('harmonization');
    await route.fulfill({contentType: 'application/json', body: JSON.stringify({status: 'stopped'})});
  });
  await page.route('**/api/workbench/draft', async route => {
    if (route.request().method() === 'PUT') {
      await new Promise(resolve => setTimeout(resolve, 250));
      await route.fulfill({contentType: 'application/json', body: JSON.stringify({draft: {}, updated_at: 'qa'})});
      return;
    }
    await route.continue();
  });
  await page.route('**/api/reports', async route => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({
        count: 3,
        root_count: 1,
        client_count: 1,
        clients: [{
          client_id: 'qa-client',
          label: 'QA Client',
          latest_modified_at: '2026-01-01T00:00:00Z',
          session_count: 1,
          file_count: 3,
          sessions: [{
            session_id: 'qa-session',
            label: 'QA Session',
            latest_modified_at: '2026-01-01T00:00:00Z',
            files: [
              {id: 'new-report', label: 'Deutung', file_name: 'new-case-report.html', kind: 'HTML', media_type: 'text/html; charset=utf-8', size: 1024, modified_at: '2026-01-01T00:00:00Z', root_name: 'qa-root', client_id: 'qa-client', session_id: 'qa-session', relative_path: 'QA/new-case-report.html'},
              {id: 'text-report', label: 'Text', file_name: 'new-case-report.txt', kind: 'TXT', media_type: 'text/plain; charset=utf-8', size: 24, modified_at: '2026-01-01T00:00:00Z', root_name: 'qa-root', client_id: 'qa-client', session_id: 'qa-session', relative_path: 'QA/new-case-report.txt'},
              {id: 'pdf-report', label: 'PDF', file_name: 'new-case-report.pdf', kind: 'PDF', media_type: 'application/pdf', size: 2048, modified_at: '2026-01-01T00:00:00Z', root_name: 'qa-root', client_id: 'qa-client', session_id: 'qa-session', relative_path: 'QA/new-case-report.pdf'},
            ],
          }],
        }],
      }),
    });
  });
  await page.route('**/api/reports/new-report/preview', async route => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({kind: 'html', mode: 'html', file_name: 'new-case-report.html', size: 1024, content: '<p>New Case Content</p>'}),
    });
  });
  await page.route('**/api/reports/text-report/preview', async route => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({kind: 'text', mode: 'text', file_name: 'new-case-report.txt', size: 24, content: 'Text Case Content'}),
    });
  });
  await page.route('**/api/reports/pdf-report/preview', async route => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({kind: 'PDF', mode: 'file', file_name: 'new-case-report.pdf', size: 2048}),
    });
  });

  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  await expect(page.locator('#health-pill')).toHaveText('Health: OK');
  await expect(page.locator('#profile-count')).not.toHaveText('[object Object]');
  await expect(page.locator('#source-list')).toHaveJSProperty('tagName', 'UL');
  await page.locator('#btn-next').click();
  await page.locator('[name="last_name"]').fill('QA');
  await page.locator('[name="first_name"]').fill('Synthetic');
  await page.locator('[name="birth_date"]').fill('09041966');
  await page.locator('[name="birth_place"]').fill('Augsburg');
  await page.locator('#consent-local').check();
  await page.locator('#consent-safety').check();
  await page.locator('#btn-next').click();
  await page.locator('[name="focus"]').fill('synthetischer QA Fokus');
  await page.locator('[name="main_symptom"]').fill('synthetischer QA Kontext');
  await page.locator('#btn-next').click();

  await page.locator('#profile-template-choices [aria-checked="true"]').focus();
  await page.keyboard.press('End');
  const focusedChoice = await page.evaluate(() => document.activeElement?.dataset?.value || null);
  const selectedChoice = await page.locator('#profile-template-choices [aria-checked="true"]').getAttribute('data-value');
  expect(focusedChoice).toBe(selectedChoice);
  await page.locator('#profile-template-choices [data-value="personal-focused"]').click();
  await page.locator('#entropy-mode-choices [data-value="hybrid"]').click();
  await page.locator('#image-file-input').setInputFiles({name: 'old-case.jpg', mimeType: 'image/jpeg', buffer: Buffer.from('qa')});
  await page.locator('#btn-next').click();
  await page.locator('#btn-next').click();
  await expect(page.locator('#review-focus')).toContainText('synthetischer QA Kontext');

  const mutation = page.evaluate(() => MorphicWorkbenchApi.saveDraft({draft: {focus: 'pending'}, persist_sensitive_data: true}));
  await expect(page.locator('#new-case-button')).toBeDisabled();
  expect(await page.evaluate(() => resetWorkbenchForNewCase())).toBe(false);
  await mutation;
  await expect(page.locator('#new-case-button')).toBeEnabled();

  await page.evaluate(() => {
    document.querySelector('#solfeggio-base-choices [data-value="528"]').click();
    document.querySelector('#group-identity-first-name').value = 'Sensitive';
    document.querySelector('#group-draft-label').value = 'Sensitive Group';
    MorphicWorkbenchState.activeJobId = 'scan-sensitive';
    MorphicWorkbenchState.activeReportId = 'report-sensitive';
    MorphicWorkbenchState.activeHarmonizationJobId = 'harm-sensitive';
    MorphicWorkbenchState.scanResults = {profiles: []};
    MorphicWorkbenchState.runTrace = {status: 'running'};
    document.querySelector('#results-metric-grid').textContent = 'Sensitive Metric';
    document.querySelector('#report-preview-frame').srcdoc = '<p>Sensitive Report</p>';
    document.querySelector('#report-preview-title').textContent = 'Sensitive Report';
    document.querySelector('#report-open-link').href = '/sensitive-report';
    document.querySelector('#group-analysis-strength').value = '0.75';
    document.querySelector('#job-id-label').textContent = 'scan-sensitive';
    document.querySelector('#job-status-label').textContent = 'laufend';
    document.querySelector('#job-returncode').textContent = '99';
    document.querySelector('#job-phase-label').textContent = 'Sensitive Phase';
    document.querySelector('#job-substep-label').textContent = 'Sensitive Substep';
    document.querySelector('#job-progress-label').textContent = '73%';
    document.querySelector('#job-progress-fill').style.width = '73%';
    document.querySelector('#job-progress-fill').setAttribute('aria-valuenow', '73');
    document.querySelector('#harmonization-job-id-label').textContent = 'harm-sensitive';
    document.querySelector('#harmonization-status-label').textContent = 'laufend';
    document.querySelector('#harmonization-mode-label').textContent = 'Sensitive Mode';
    document.querySelector('#harmonization-phase-label').textContent = 'Sensitive Harm Phase';
    document.querySelector('#harmonization-progress-label').textContent = '81%';
    document.querySelector('#harmonization-lease-label').textContent = 'Sensitive Heartbeat';
    document.querySelector('#harmonization-cycles-label').textContent = '8 / 10';
    document.querySelector('#harmonization-error-label').textContent = 'Sensitive Error';
    enterStep(10);
  });
  await page.locator('#new-case-button').click();

  await expect(page.locator('[name="first_name"]')).toHaveValue('');
  await expect(page.locator('#group-identity-first-name')).toHaveValue('');
  await expect(page.locator('#group-draft-label')).toHaveValue('');
  await expect(page.locator('#consent-local')).not.toBeChecked();
  await expect(page.locator('#consent-safety')).not.toBeChecked();
  await expect(page.locator('#image-file-input')).toHaveValue('');
  await expect(page.locator('#profile-template-select')).toHaveValue('phase1-default');
  await expect(page.locator('#entropy-mode-select')).toHaveValue('legacy');
  await expect(page.locator('#solfeggio-base-choices [aria-checked="true"]')).toHaveAttribute('data-value', '432');
  await expect(page.locator('#harmonization-form [name="target_frequency"]')).toHaveValue('432');
  expect(await page.evaluate(() => String(MorphicWorkbenchState.selectedSolfeggioBase))).toBe('432');
  await expect(page.locator('[name="profile_level"]')).toHaveValue('3');
  await expect(page.locator('[name="top_n"]')).toHaveValue('5');
  await expect(page.locator('#results-metric-grid')).toBeEmpty();
  await expect(page.locator('#report-preview-title')).toHaveText('Noch kein Bericht gewaehlt');
  await expect(page.locator('#report-preview-frame')).toHaveJSProperty('srcdoc', '');
  await expect(page.locator('#report-open-link')).toHaveAttribute('href', '#');
  await expect(page.locator('#group-analysis-strength')).toHaveValue('');
  await expect(page.locator('#job-id-label')).toHaveText('-');
  await expect(page.locator('#job-status-label')).toHaveText('nicht gestartet');
  await expect(page.locator('#job-returncode')).toHaveText('-');
  await expect(page.locator('#job-phase-label')).toHaveText('-');
  await expect(page.locator('#job-substep-label')).toHaveText('Warte auf Ausgabe...');
  await expect(page.locator('#job-progress-label')).toHaveText('wird aus Ausgabe abgeleitet');
  await expect(page.locator('#job-progress-fill')).toHaveAttribute('aria-valuenow', '0');
  expect(await page.locator('#job-progress-fill').evaluate(node => node.style.width)).toBe('0%');
  await expect(page.locator('#harmonization-job-id-label')).toHaveText('-');
  await expect(page.locator('#harmonization-status-label')).toHaveText('nicht gestartet');
  await expect(page.locator('#harmonization-mode-label')).toHaveText('-');
  await expect(page.locator('#harmonization-phase-label')).toHaveText('-');
  await expect(page.locator('#harmonization-progress-label')).toHaveText('-');
  await expect(page.locator('#harmonization-lease-label')).toHaveText('-');
  await expect(page.locator('#harmonization-cycles-label')).toHaveText('-');
  await expect(page.locator('#harmonization-error-label')).toHaveText('kein Fehler');
  expect(stopCalls.sort()).toEqual(['harmonization', 'scan']);

  await page.evaluate(() => loadReports());
  await page.evaluate(() => renderReportPreview('new-report'));
  await expect(page.locator('#report-preview-panel')).not.toHaveAttribute('hidden', '');
  await expect(page.locator('#report-preview-title')).toContainText('new-case-report.html');
  await expect(page.locator('#report-preview-frame')).toHaveJSProperty('srcdoc', '<p>New Case Content</p>');
  await page.evaluate(() => renderReportPreview('text-report'));
  await expect(page.locator('#report-preview-text')).toHaveText('Text Case Content');
  await expect(page.locator('#report-preview-frame')).toHaveJSProperty('srcdoc', '');
  await page.evaluate(() => renderReportPreview('new-report'));
  await expect(page.locator('#report-preview-text')).toBeEmpty();
  await expect(page.locator('#report-preview-state')).toHaveText('Vorschau geladen');
  await page.evaluate(() => renderReportPreview('pdf-report'));
  await expect(page.locator('#report-preview-text')).toContainText('PDF-Datei');
  await expect(page.locator('#report-preview-text')).toContainText('Datei öffnen');
  expect(errors).toEqual([]);
});

test('Scanprofil-Pool und Registry-Quellen bleiben transparent und an Preview und Start gebunden', async ({ page }) => {
  const errors = captureErrors(page);
  const previewBodies = [];
  const startBodies = [];
  const catalog = buildScanProfileCatalog({
    profiles: [
      {id: 'alpha-id', label: 'Alpha Belastungsprofil'},
      {id: 'beta-id', label: 'Beta Regulationsprofil'},
      {id: 'gamma-id', label: 'Gamma Resonanzprofil'},
      {id: 'delta-id', label: 'Delta Balanceprofil'},
      {id: 'epsilon-id', label: 'Epsilon Fokusprofil'},
    ],
    activeSources: [
      {id: 'registry-alpha', label: 'Registry Alpha'},
      {id: 'registry-beta', label: 'Registry Beta'},
    ],
  });
  await page.route('**/api/workbench/scan-profile-catalog?*', async route => {
    await route.fulfill({contentType: 'application/json', body: JSON.stringify(catalog)});
  });
  await page.route('**/api/scan/preview', async route => {
    previewBodies.push(route.request().postDataJSON());
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({command: ['scan', 'preview', 'gate-3']}),
    });
  });
  await page.route('**/api/scan/jobs', async route => {
    if (route.request().method() !== 'POST') return route.continue();
    startBodies.push(route.request().postDataJSON());
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({job_id: 'scan-gate-3-binding'}),
    });
  });
  await page.route('**/api/scan/jobs/scan-gate-3-binding', async route => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({
        status: 'running', progress_percent: 1,
        completed_substeps: [], completed_stage_ids: [],
      }),
    });
  });

  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    await navigateToReview(page);
    await expect.poll(() => page.evaluate(
      () => MorphicWorkbenchState.scanProfileCatalogStatus,
    )).toBe('ready');

    const review = page.locator('#review-scan-scope');
    await expect(review.locator('.scan-scope-summary')).toHaveText(
      'Level 3 prüft 5 interne Screening-Profile; anschließend werden Top-5 vollständig analysiert.'
    );
    await expect(review.locator('.scan-pool-badges')).toContainText('Poolquelle: Legacy');
    await expect(review.locator('.scan-pool-badges')).toContainText(
      `Fingerprint: ${catalog.pool_authority.fingerprint_short}`
    );

    const internalDetails = review.locator('.scan-pool-internal');
    await internalDetails.locator('summary').focus();
    await page.keyboard.press('Enter');
    await expect(internalDetails).toHaveAttribute('open', '');
    await expect(internalDetails.locator('.scan-profile-counter')).toHaveText('5 von 5 Profilen');

    const search = internalDetails.locator('#scan-profile-search');
    await search.focus();
    await page.keyboard.type('BETA-ID');
    await expect(internalDetails.locator('.scan-profile-counter')).toHaveText('1 von 5 Profilen');
    await expect(internalDetails.locator('.scan-profile-item:visible')).toHaveCount(1);
    await expect(internalDetails.locator('.scan-profile-item:visible')).toContainText('Beta Regulationsprofil');
    await page.keyboard.press('Control+A');
    await page.keyboard.type('kein-treffer');
    await expect(internalDetails.locator('.scan-profile-counter')).toHaveText('0 von 5 Profilen');
    await expect(internalDetails.locator('.scan-profile-item:visible')).toHaveCount(0);
    await expect(internalDetails.locator('.scan-profile-empty')).toBeVisible();

    const externalDetails = review.locator('.scan-pool-external');
    await externalDetails.locator('summary').focus();
    await page.keyboard.press('Enter');
    await expect(externalDetails).toHaveAttribute('open', '');
    await expect(externalDetails).toContainText(
      '2 Registry-Quellen sind betriebsbereit; 0 als Scanprofile freigegeben.'
    );
    await expect(externalDetails).toContainText('Keine Wirkung auf diesen Scan, Profilpool oder Score.');
    await expect(externalDetails).toContainText('Gate 14');
    await expect(externalDetails.locator('input, button')).toHaveCount(0);
    await expect(externalDetails.locator('.registry-source-item')).toHaveCount(2);
    for (const source of await externalDetails.locator('.registry-source-item').all()) {
      await expect(source).toContainText('keine Scanwirkung');
    }

    await expect(page.locator('#preview-button')).toBeEnabled();
    await expect(page.locator('#start-analysis-button')).toBeEnabled();
    await page.locator('#preview-button').click();
    await expect.poll(() => previewBodies.length).toBe(1);
    await page.locator('#start-analysis-button').click();
    await expect.poll(() => startBodies.length).toBe(1);
    await expect(page.locator('#job-status-label')).toHaveText('laeuft');

    for (const body of [previewBodies[0], startBodies[0]]) {
      expect(body.profile_level).toBe(3);
      expect(body.scan_profile_pool_fingerprint).toBe(catalog.pool_authority.fingerprint);
    }
    expect(await page.evaluate(() => ({
      level: MorphicWorkbenchState.scanProfileCatalog.profile_level,
      fingerprint: MorphicWorkbenchState.scanProfileCatalog.pool_authority.fingerprint,
    }))).toEqual({level: 3, fingerprint: catalog.pool_authority.fingerprint});
    expect(errors).toEqual([]);
  } finally {
    await clearSyntheticScanRun(page);
  }
});

test('Scanprofil-Pool Startantwort-Race sperrt Navigation und öffnet absolut den Analyse-Lauf', async ({ page }) => {
  const startGate = createDeferred();
  const startRequested = createDeferred();
  const previewBodies = [];
  const startBodies = [];
  let pollRequests = 0;
  const levelThreeCatalog = buildScanProfileCatalog({
    profileLevel: 3,
    profiles: Array.from({length: 5}, (_, index) => ({
      id: `start-level-3-${index + 1}`,
      label: `Start Level 3 ${index + 1}`,
    })),
  });
  await page.route('**/api/workbench/scan-profile-catalog?*', async route => {
    const level = Number(new URL(route.request().url()).searchParams.get('profile_level'));
    const catalog = level === 3
      ? levelThreeCatalog
      : buildScanProfileCatalog({profileLevel: level});
    await route.fulfill({contentType: 'application/json', body: JSON.stringify(catalog)});
  });
  await page.route('**/api/scan/preview', async route => {
    previewBodies.push(route.request().postDataJSON());
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({command: ['must-not-dispatch']}),
    });
  });
  await page.route('**/api/scan/jobs', async route => {
    if (route.request().method() !== 'POST') return route.continue();
    startBodies.push(route.request().postDataJSON());
    startRequested.release();
    await startGate.promise;
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({job_id: 'scan-start-response-race'}),
    });
  });
  await page.route('**/api/scan/jobs/scan-start-response-race', async route => {
    pollRequests += 1;
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({
        status: 'running', progress_percent: 1,
        completed_substeps: [], completed_stage_ids: [],
      }),
    });
  });

  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    await navigateToReview(page);
    await waitForScanProfilePool(page);
    await page.locator('#start-analysis-button').click();
    await startRequested.promise;

    expect(startBodies).toHaveLength(1);
    expect(startBodies[0].profile_level).toBe(3);
    expect(startBodies[0].scan_profile_pool_fingerprint).toBe(
      levelThreeCatalog.pool_authority.fingerprint
    );
    expect(await page.evaluate(() => ({
      pending: MorphicWorkbenchState.scanStartPending,
      step: MorphicWorkbenchState.currentStepIndex,
    }))).toEqual({pending: true, step: 5});
    await expect(page.locator('#preview-button')).toBeDisabled();
    expect(await page.evaluate(() => generatePreview())).toBe(false);
    expect(previewBodies).toHaveLength(0);
    await expect(page.locator('#preview-state')).toHaveText('Analyse wird gestartet...');
    await expect(page.locator('#wizard-navigation-state')).toHaveText(
      'Eine Analyse wird bereits gestartet oder ausgefuehrt.'
    );

    await page.locator('#wizard-step-2').click();
    const profileLevel = page.locator('[name="profile_level"]');
    if (await profileLevel.isVisible()) await profileLevel.selectOption('4');
    await page.locator('#btn-prev').click();

    expect.soft(await page.evaluate(() => ({
      step: MorphicWorkbenchState.currentStepIndex,
      level: document.querySelector('[name="profile_level"]').value,
      payloadLevel: formScanPayload().profile_level,
      payloadFingerprint: formScanPayload().scan_profile_pool_fingerprint,
    }))).toEqual({
      step: 5,
      level: '3',
      payloadLevel: 3,
      payloadFingerprint: levelThreeCatalog.pool_authority.fingerprint,
    });
    await expect.soft(page.locator('#wizard-navigation-state')).toContainText(
      'Analyse-Start wird bestätigt. Navigation bleibt bis zur Serverantwort gesperrt.'
    );

    startGate.release();
    await expect.poll(() => page.evaluate(() => MorphicWorkbenchState.activeJobId)).toBe(
      'scan-start-response-race'
    );
    await expect.poll(() => pollRequests).toBe(1);
    await expect(page.locator('#job-status-label')).toHaveText('laeuft');
    await expect(page.locator('#preview-button')).toBeDisabled();
    const confirmedRunStatus = await page.locator('#preview-state').textContent();
    expect(await page.evaluate(() => generatePreview())).toBe(false);
    expect(previewBodies).toHaveLength(0);
    await expect(page.locator('#preview-state')).toHaveText(confirmedRunStatus);
    expect(await page.evaluate(() => ({
      step: MorphicWorkbenchState.currentStepIndex,
      stepId: MorphicWorkbenchState.currentStepId,
      activeJobId: MorphicWorkbenchState.activeJobId,
      scanRunActive: MorphicWorkbenchState.scanRunActive,
      level: document.querySelector('[name="profile_level"]').value,
      payloadLevel: formScanPayload().profile_level,
      payloadFingerprint: formScanPayload().scan_profile_pool_fingerprint,
    }))).toEqual({
      step: 6,
      stepId: 'run',
      activeJobId: 'scan-start-response-race',
      scanRunActive: true,
      level: '3',
      payloadLevel: 3,
      payloadFingerprint: levelThreeCatalog.pool_authority.fingerprint,
    });
    await expect(page.locator('#wizard-step-6')).toHaveAttribute('aria-current', 'step');
    await expect(page.locator('.wizard-panel.active')).toContainText('Analyse-Lauf');
  } finally {
    startGate.release();
    startRequested.release();
    try {
      await clearSyntheticScanRun(page);
    } finally {
      await releaseDeferredRoutes(page, startGate, startRequested);
    }
  }
});

test('Scanprofil-Pool stays responsive and explains scan truth', async ({ page }) => {
  const errors = captureErrors(page);
  const catalog = buildScanProfileCatalog({
    profiles: [
      {
        id: `internal-${'profile-segment-'.repeat(10)}`,
        label: `Internes Profil mit langem Namen ${'ohne Randüberlauf '.repeat(8)}`,
      },
      {id: 'short-internal', label: 'Intern B'},
    ],
    activeSources: [
      {
        id: `external-${'registry-segment-'.repeat(10)}`,
        label: `Externe Registry-Quelle ${'mit langem nachvollziehbarem Label '.repeat(7)}`,
      },
    ],
  });
  await page.route('**/api/workbench/scan-profile-catalog?*', async route => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify(catalog),
    });
  });
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  await expect.poll(() => page.evaluate(
    () => MorphicWorkbenchState.scanProfileCatalogStatus,
  )).toBe('ready');

  await expect(page.locator('#source-analysis-integration')).toContainText('0 als Scanprofile freigegeben');
  await page.evaluate(() => enterStep(3, false));
  await expect(page.locator('#profile-template-choices .choice-card-hint').first()).not.toBeEmpty();
  await expect(page.locator('#entropy-mode-choices .choice-card-hint').first()).not.toBeEmpty();

  await page.evaluate(() => {
    MorphicWorkbenchRender.renderResults({
      status: 'completed', job_id: 'display-only',
      top_profiles: [{profile: 'Anzeigeprofil', score: 1.23456, top_resonances: [{label: 'Resonanz', score: 0.98765}]}],
    });
  });
  await expect(page.locator('.result-profile-score')).toHaveText('Score: 1,235');
  await expect(page.locator('#results-profile-list li')).toContainText('0,988');

  await page.evaluate(() => enterStep(4, false));
  await expect(page.locator('.emf-index-label')).toHaveText(
    'System-/Entropie-basierter EMF-Proxy-Index'
  );
  await expect(page.locator('.emf-index-card')).toContainText('keine Messung');

  for (const emfIndex of [null, 'ungueltig']) {
    await page.evaluate(value => {
      MorphicWorkbenchRender.renderHardwareTruth({
        components: {},
        realtime_calibration: {
          status: 'active',
          emf_index: value,
          entropy_score: 0.5,
          timing_jitter_ms: 0.25,
          system_load: 0.1,
        },
        gate_warnings: [],
      });
    }, emfIndex);
    await expect(page.locator('.emf-index-card')).toContainText('kein autoritativer Messwert');
    await expect(page.locator('.emf-index-gauge')).toHaveCount(0);
    await expect(page.locator('.emf-index-card')).not.toHaveAttribute('aria-valuenow', '0');
  }

  await page.evaluate(() => enterStep(5, false));
  await expect(page.locator('#review-scan-scope')).toContainText('2 interne Screening-Profile');
  await expect(page.locator('#review-scan-scope')).toContainText('0 als Scanprofile freigegeben');

  const responsiveMeasurements = [];
  for (const width of [1280, 768, 375, 320]) {
    await page.setViewportSize({width, height: 900});
    for (const step of [0, 3, 4, 5, 9]) {
      await page.evaluate(index => MorphicWorkbenchRender.showStep(index), step);
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      expect(overflow, `horizontal overflow at ${width}px`).toBeLessThanOrEqual(1);
    }
    await page.evaluate(() => enterStep(5, false));
    const review = page.locator('#review-scan-scope');
    await review.locator('.scan-pool-internal > summary').click();
    await review.locator('.scan-pool-external > summary').click();
    await expect(review.locator('.scan-pool-internal')).toHaveAttribute('open', '');
    await expect(review.locator('.scan-pool-external')).toHaveAttribute('open', '');
    const measurements = await page.evaluate(() => {
      const selectors = [
        '#review-scan-scope', '.scan-pool-badges', '.scan-pool-internal',
        '.scan-profile-search', '.scan-profile-list', '.scan-pool-external',
        '.registry-source-list',
      ];
      return {
        viewport: window.innerWidth,
        clientWidth: document.documentElement.clientWidth,
        scrollWidth: document.documentElement.scrollWidth,
        containers: selectors.map(selector => {
          const rect = document.querySelector(selector).getBoundingClientRect();
          return {selector, left: rect.left, right: rect.right, width: rect.width};
        }),
      };
    });
    responsiveMeasurements.push(measurements);
    expect(measurements.scrollWidth, `document overflow at ${width}px`).toBeLessThanOrEqual(
      measurements.clientWidth
    );
    for (const rect of measurements.containers) {
      expect(rect.left, `${rect.selector} left edge at ${width}px`).toBeGreaterThanOrEqual(-1);
      expect(rect.right, `${rect.selector} right edge at ${width}px`).toBeLessThanOrEqual(
        measurements.clientWidth + 1
      );
    }
  }
  console.log(`Gate-3 responsive measurements: ${JSON.stringify(responsiveMeasurements)}`);
  expect(errors).toEqual([]);
});

test('latest profile-level selection remains authoritative when catalog responses reorder', async ({ page }) => {
  const levelThreeGate = createDeferred();
  const levelThreeRequested = createDeferred();
  let levelThreeRequests = 0;
  const levelThreeCatalog = buildScanProfileCatalog({
    profileLevel: 3,
    profiles: [{id: 'level-3-stale', label: 'Level 3 Stale'}],
  });
  const levelFourCatalog = buildScanProfileCatalog({
    profileLevel: 4,
    profiles: [
      {id: 'level-4-alpha', label: 'Level 4 Alpha'},
      {id: 'level-4-beta', label: 'Level 4 Beta'},
      {id: 'level-4-gamma', label: 'Level 4 Gamma'},
      {id: 'level-4-delta', label: 'Level 4 Delta'},
      {id: 'level-4-epsilon', label: 'Level 4 Epsilon'},
    ],
  });
  await page.route('**/api/workbench/scan-profile-catalog?*', async route => {
    const level = Number(new URL(route.request().url()).searchParams.get('profile_level'));
    if (level === 3) {
      levelThreeRequests += 1;
      if (levelThreeRequests === 2) {
        levelThreeRequested.release();
        await levelThreeGate.promise;
      }
    }
    const catalog = level === 4
      ? levelFourCatalog
      : levelThreeCatalog;
    await route.fulfill({contentType: 'application/json', body: JSON.stringify(catalog)});
  });
  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    await waitForScanProfilePool(page);
    await navigateToReview(page);
    await page.evaluate(() => {
      window.__lateLevelThreeCatalogPromise = loadScanProfileCatalog(3);
    });
    await levelThreeRequested.promise;
    await page.evaluate(() => {
      const select = document.querySelector('[name="profile_level"]');
      select.value = '4';
      select.dispatchEvent(new Event('change', {bubbles: true}));
    });
    await expect.poll(() => page.evaluate(
      () => MorphicWorkbenchState.scanProfileCatalog?.profile_level,
    )).toBe(4);

    const review = page.locator('#review-scan-scope');
    const assertLevelFourAuthority = async () => {
      await expect(review.locator('.scan-scope-summary')).toContainText(
        'Level 4 prüft 5 interne Screening-Profile'
      );
      await expect(review.locator('.scan-pool-badges')).toContainText(
        `Fingerprint: ${levelFourCatalog.pool_authority.fingerprint_short}`
      );
      const internalDetails = review.locator('.scan-pool-internal');
      if (await internalDetails.getAttribute('open') === null) {
        await internalDetails.locator('summary').click({force: true});
      }
      await expect(internalDetails).toHaveAttribute('open', '');
      await expect(internalDetails.locator('.scan-profile-list')).toContainText('Level 4 Alpha');
      await expect(internalDetails.locator('.scan-profile-list')).toContainText('Level 4 Beta');
      await expect(internalDetails.locator('.scan-profile-list')).not.toContainText('Level 3 Stale');
      await expect(page.locator('#preview-button')).toBeEnabled();
      await expect(page.locator('#start-analysis-button')).toBeEnabled();
      expect(await page.evaluate(() => ({
        selectedLevel: document.querySelector('[name="profile_level"]').value,
        catalogLevel: MorphicWorkbenchState.scanProfileCatalog?.profile_level,
        catalogStateLevel: MorphicWorkbenchState.scanProfileCatalogLevel,
        catalogFingerprint: MorphicWorkbenchState.scanProfileCatalog?.pool_authority?.fingerprint,
        payloadLevel: formScanPayload().profile_level,
        payloadFingerprint: formScanPayload().scan_profile_pool_fingerprint,
      }))).toEqual({
        selectedLevel: '4',
        catalogLevel: 4,
        catalogStateLevel: 4,
        catalogFingerprint: levelFourCatalog.pool_authority.fingerprint,
        payloadLevel: 4,
        payloadFingerprint: levelFourCatalog.pool_authority.fingerprint,
      });
    };
    await assertLevelFourAuthority();

    levelThreeGate.release();
    await page.evaluate(() => window.__lateLevelThreeCatalogPromise);
    await assertLevelFourAuthority();
  } finally {
    await releaseDeferredRoutes(page, levelThreeGate, levelThreeRequested);
  }
});

test('scan-profile catalog failure is terminal in review and retry recovers', async ({ page }) => {
  let catalogRequests = 0;
  const initialCatalogGate = createDeferred();
  const retryCatalogGate = createDeferred();
  const initialRequest = createDeferred();
  const retryRequest = createDeferred();
  const recoveredCatalog = buildScanProfileCatalog({
    profiles: [
      {id: 'recovered-a', label: 'Wiederhergestellt A'},
      {id: 'recovered-b', label: 'Wiederhergestellt B'},
      {id: 'recovered-c', label: 'Wiederhergestellt C'},
      {id: 'recovered-d', label: 'Wiederhergestellt D'},
      {id: 'recovered-e', label: 'Wiederhergestellt E'},
    ],
    activeSources: [{id: 'registry-recovered', label: 'Registry wiederhergestellt'}],
  });
  await page.route('**/api/workbench/scan-profile-catalog?*', async route => {
    catalogRequests += 1;
    if (catalogRequests === 1) {
      initialRequest.release();
      await initialCatalogGate.promise;
      await route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({detail: 'C:\\sensitive\\profile-catalog.json ist nicht verfügbar.'}),
      });
      return;
    }
    retryRequest.release();
    await retryCatalogGate.promise;
    await route.fulfill({contentType: 'application/json', body: JSON.stringify(recoveredCatalog)});
  });

  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    await initialRequest.promise;
    await navigateToReview(page);
    const review = page.locator('#review-scan-scope');
    const loading = review.locator('.scan-pool-loading');
    await expect(loading).toHaveText('Scanprofil-Pool wird geladen.');
    await expect(review.locator('.scan-scope-summary, .scan-profile-counter')).toHaveCount(0);
    await expect(page.locator('#preview-button')).toBeDisabled();
    await expect(page.locator('#start-analysis-button')).toBeDisabled();

    initialCatalogGate.release();
    await expect.poll(() => page.evaluate(() => MorphicWorkbenchState.scanProfileCatalogStatus)).toBe('error');
    await expect(review.locator('.scan-pool-error')).toContainText('HTTP 503');
    await expect(review).not.toContainText('sensitive');
    await expect(review).not.toContainText(/0 (?:interne |externe )?Profile/);
    await expect(review).not.toContainText('Scanprofil-Pool wird geladen.');
    await expect(review).toContainText('Keine Wirkung auf diesen Scan, Profilpool oder Score.');
    await expect(review).toContainText('Gate 14');
    await expect(page.locator('#preview-button')).toBeDisabled();
    await expect(page.locator('#start-analysis-button')).toBeDisabled();

    const retry = review.getByRole('button', {name: 'Scanprofil-Pool erneut laden'});
    await retry.focus();
    await page.keyboard.press('Enter');
    await retryRequest.promise;
    await expect(review.locator('.scan-pool-loading')).toBeFocused();
    await expect(review.locator('.scan-scope-summary, .scan-profile-counter')).toHaveCount(0);
    await expect(page.locator('#preview-button')).toBeDisabled();
    await expect(page.locator('#start-analysis-button')).toBeDisabled();

    retryCatalogGate.release();
    await expect.poll(() => page.evaluate(() => MorphicWorkbenchState.scanProfileCatalogStatus)).toBe('ready');
    await expect(review.locator('.scan-scope-summary')).toContainText('5 interne Screening-Profile');
    await expect(review.locator('.scan-pool-internal-summary')).toBeFocused();
    await expect(page.locator('#preview-button')).toBeEnabled();
    await expect(page.locator('#start-analysis-button')).toBeEnabled();
    expect(catalogRequests).toBe(2);
  } finally {
    await releaseDeferredRoutes(
      page,
      initialCatalogGate,
      retryCatalogGate,
      initialRequest,
      retryRequest
    );
  }
});

test('Scanprofil-Pool 409 invalidates preview authority and reloads once without replay', async ({ page }) => {
  let catalogRequests = 0;
  const previewBodies = [];
  const reloadGate = createDeferred();
  const reloadRequest = createDeferred();
  const catalogA = buildScanProfileCatalog({
    profiles: Array.from({length: 5}, (_, index) => ({
      id: `stale-bound-profile-a-${index + 1}`,
      label: `Gebundenes Profil A ${index + 1}`,
    })),
    authority: {fingerprint: 'a'.repeat(64)},
  });
  const catalogB = buildScanProfileCatalog({
    profiles: Array.from({length: 5}, (_, index) => ({
      id: `recovered-bound-profile-b-${index + 1}`,
      label: `Gebundenes Profil B ${index + 1}`,
    })),
    authority: {fingerprint: 'b'.repeat(64)},
  });
  await page.route('**/api/workbench/scan-profile-catalog?*', async route => {
    catalogRequests += 1;
    if (catalogRequests === 2) {
      reloadRequest.release();
      await reloadGate.promise;
    }
    const catalog = catalogRequests === 1 ? catalogA : catalogB;
    await route.fulfill({contentType: 'application/json', body: JSON.stringify(catalog)});
  });
  await page.route('**/api/scan/preview', async route => {
    previewBodies.push(route.request().postDataJSON());
    if (previewBodies.length === 1) {
      await route.fulfill({
        status: 409,
        headers: {'X-Morphic-Scan-Profile-Pool': 'stale'},
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Scanprofil-Pool hat sich geändert. Bitte neu laden und erneut prüfen.',
        }),
      });
      return;
    }
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({command: ['scan', 'preview', 'recovered-gate-3']}),
    });
  });

  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    await navigateToReview(page);
    await expect.poll(() => page.evaluate(
      () => MorphicWorkbenchState.scanProfileCatalogStatus,
    )).toBe('ready');
    await expect(page.locator('.scan-pool-badges')).toContainText(
      `Fingerprint: ${catalogA.pool_authority.fingerprint_short}`
    );
    await expect(page.locator('#preview-button')).toBeEnabled();
    await expect(page.locator('#start-analysis-button')).toBeEnabled();

    await page.locator('#preview-button').click();
    await reloadRequest.promise;
    expect(previewBodies).toHaveLength(1);
    expect(previewBodies[0].scan_profile_pool_fingerprint).toBe(
      catalogA.pool_authority.fingerprint
    );
    expect(catalogRequests).toBe(2);
    expect(await page.evaluate(() => ({
      catalog: MorphicWorkbenchState.scanProfileCatalog,
      status: MorphicWorkbenchState.scanProfileCatalogStatus,
      payloadFingerprint: formScanPayload().scan_profile_pool_fingerprint,
    }))).toEqual({catalog: null, status: 'loading', payloadFingerprint: ''});
    await expect(page.locator('#preview-button')).toBeDisabled();
    await expect(page.locator('#start-analysis-button')).toBeDisabled();

    reloadGate.release();
    await expect.poll(() => page.evaluate(
      () => MorphicWorkbenchState.scanProfileCatalogStatus,
    )).toBe('ready');
    await expect(page.locator('.scan-pool-badges')).toContainText(
      `Fingerprint: ${catalogB.pool_authority.fingerprint_short}`
    );
    expect(await page.evaluate(() => formScanPayload().scan_profile_pool_fingerprint)).toBe(
      catalogB.pool_authority.fingerprint
    );
    await expect(page.locator('#preview-button')).toBeEnabled();
    await expect(page.locator('#start-analysis-button')).toBeEnabled();
    expect(previewBodies).toHaveLength(1);
    expect(catalogRequests).toBe(2);

    await page.locator('#preview-button').click();
    await expect.poll(() => previewBodies.length).toBe(2);
    expect(previewBodies[1].scan_profile_pool_fingerprint).toBe(
      catalogB.pool_authority.fingerprint
    );
    await expect(page.locator('#preview-state')).toHaveText('Vorschau bereit');
    await expect(page.locator('#command-preview')).toContainText('recovered-gate-3');
    expect(catalogRequests).toBe(2);
  } finally {
    await releaseDeferredRoutes(page, reloadGate, reloadRequest);
  }
});

test('Level 1 Top-9 bleibt fail-closed und Top-5 stellt Aktionen wieder her', async ({ page }) => {
  const previewBodies = [];
  await page.route('**/api/workbench/scan-profile-catalog?*', async route => {
    const level = Number(new URL(route.request().url()).searchParams.get('profile_level'));
    const count = level === 1 ? 5 : 9;
    const profiles = Array.from({length: count}, (_, index) => ({
      id: `level-${level}-profile-${index + 1}`,
      label: `Level ${level} Profil ${index + 1}`,
    }));
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify(buildScanProfileCatalog({profileLevel: level, profiles})),
    });
  });
  await page.route('**/api/scan/preview', async route => {
    previewBodies.push(route.request().postDataJSON());
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({command: ['scan', 'preview', 'level-1-top-5']}),
    });
  });

  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  await navigateToReview(page, {profileLevel: 1});
  await expect.poll(() => page.evaluate(
    () => MorphicWorkbenchState.scanProfileCatalog?.profile_level,
  )).toBe(1);

  const topN = page.locator('[name="top_n"]');
  await expect(topN.locator('option[value="5"]')).not.toHaveAttribute('disabled', '');
  await expect(topN.locator('option[value="7"]')).toHaveAttribute('disabled', '');
  await expect(topN.locator('option[value="9"]')).toHaveAttribute('disabled', '');
  await page.evaluate(() => {
    const select = document.querySelector('[name="top_n"]');
    select.value = '9';
    select.dispatchEvent(new Event('change', {bubbles: true}));
  });

  await expect(topN).toHaveValue('9');
  await expect(page.locator('#preview-button')).toBeDisabled();
  await expect(page.locator('#start-analysis-button')).toBeDisabled();
  const invalidReviewState = await page.evaluate(() => ({
    currentStepIndex: MorphicWorkbenchState.currentStepIndex,
    currentStepType: typeof MorphicWorkbenchState.currentStepIndex,
    topNSupported: scanProfilePoolSupportsCurrentTopN(),
    summary: document.querySelector('.scan-scope-summary')?.textContent,
  }));
  expect(invalidReviewState).toEqual({
    currentStepIndex: 5,
    currentStepType: 'number',
    topNSupported: false,
    summary: 'Level 1 prüft 5 interne Screening-Profile.',
  });
  await expect(page.locator('.scan-pool-topn-warning')).toHaveText(
    'Top-N überschreitet den bestätigten Scanprofil-Pool. Bitte Auswahl anpassen.'
  );
  await expect(page.locator('.scan-scope-summary')).not.toContainText('Top-9 vollständig analysiert');
  await page.evaluate(() => generatePreview());
  expect(previewBodies).toHaveLength(0);

  await page.evaluate(() => {
    const select = document.querySelector('[name="top_n"]');
    select.value = '5';
    select.dispatchEvent(new Event('change', {bubbles: true}));
  });
  await expect(topN).toHaveValue('5');
  await expect(page.locator('.scan-pool-topn-warning')).toHaveCount(0);
  await expect(page.locator('.scan-scope-summary')).toContainText('Top-5 vollständig analysiert');
  await expect(page.locator('#preview-button')).toBeEnabled();
  await expect(page.locator('#start-analysis-button')).toBeEnabled();
  await page.locator('#preview-button').click();
  await expect.poll(() => previewBodies.length).toBe(1);
  expect(previewBodies[0].profile_level).toBe(1);
  expect(previewBodies[0].top_n).toBe(5);
});

test('late registry hydration preserves the authoritative wizard step', async ({ page }) => {
  const registryGate = createDeferred();
  await page.route('**/api/workbench/registry', async route => {
    await registryGate.promise;
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({
        steps: Array.from({length: 11}, (_, index) => ({
          id: `step-${index}`,
          label: index === 1 ? 'Klient / Kontext' : `Phase ${index + 1}`,
        })),
      }),
    });
  });

  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    await page.evaluate(() => enterStep(1, false));
    await expect(page.locator('.wizard-step.active')).toContainText('Klient / Kontext');
    registryGate.release();

    await expect.poll(() => page.evaluate(() => MorphicWorkbenchState.registry?.steps?.length)).toBe(11);
    await expect(page.locator('.wizard-step.active')).toContainText('Klient / Kontext');
    await expect(page.locator('.wizard-step.active')).toHaveAttribute('aria-current', 'step');
    await expect(page.locator('.wizard-step.active')).toHaveAttribute('tabindex', '0');
  } finally {
    await releaseDeferredRoutes(page, registryGate);
  }
});

test('sources hydrate independently while the health read is delayed', async ({ page }) => {
  const healthGate = createDeferred();
  await page.route('**/api/health', async route => {
    await healthGate.promise;
    await route.fulfill({contentType: 'application/json', body: JSON.stringify({ok: true, profiles: {}, databases: []})});
  });
  await page.route('**/api/sources', async route => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({count: 1, status_counts: {active: 1}, sources: [{id: 'independent', label: 'Independent', status: 'active'}]}),
    });
  });

  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    await expect(page.locator('#source-pill')).toContainText('Quellen: 1');
    healthGate.release();
    await expect(page.locator('#health-pill')).toContainText('Health: OK');
  } finally {
    await releaseDeferredRoutes(page, healthGate);
  }
});

test('latest same-generation hardware and report requests remain authoritative', async ({ page }) => {
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  await expect.poll(() => page.evaluate(() => Boolean(MorphicWorkbenchState.hardwareTruth))).toBe(true);

  const hardwareResult = await page.evaluate(async () => {
    const base = MorphicWorkbenchState.hardwareTruth;
    let releaseOld;
    MorphicWorkbenchApi.loadHardware = mode => {
      if (mode === 'standard') {
        return new Promise(resolve => {
          releaseOld = () => resolve({...base, review_marker: 'old-standard'});
        });
      }
      return Promise.resolve({...base, review_marker: 'new-expert'});
    };
    MorphicWorkbenchState.workbenchMode = 'standard';
    const oldRequest = loadHardwareTruth();
    MorphicWorkbenchState.workbenchMode = 'expert';
    await loadHardwareTruth();
    releaseOld();
    await oldRequest;
    return MorphicWorkbenchState.hardwareTruth.review_marker;
  });
  expect(hardwareResult).toBe('new-expert');

  const reportResult = await page.evaluate(async () => {
    const payload = label => ({
      count: 1,
      root_count: 1,
      client_count: 1,
      clients: [{
        client_id: `client-${label}`,
        label,
        session_count: 1,
        file_count: 1,
        sessions: [{
          session_id: `session-${label}`,
          label: `Session ${label}`,
          files: [{
            id: `report-${label}`,
            label,
            file_name: label,
            kind: 'HTML',
            media_type: 'text/html; charset=utf-8',
            size: 1,
            modified_at: '2026-01-01T00:00:00Z',
            client_id: `client-${label}`,
            session_id: `session-${label}`,
            relative_path: `${label}.html`,
          }],
        }],
      }],
    });
    let releaseOld;
    let call = 0;
    MorphicWorkbenchApi.loadReports = () => {
      call += 1;
      if (call === 1) {
        return new Promise(resolve => { releaseOld = () => resolve(payload('OLD')); });
      }
      return Promise.resolve(payload('NEW'));
    };
    const oldRequest = loadReports();
    await loadReports();
    releaseOld();
    await oldRequest;
    return document.querySelector('#report-list').textContent;
  });
  expect(reportResult).toContain('NEW');
  expect(reportResult).not.toContain('OLD');
});

test('scan start is single-flight and cannot create competing poll loops', async ({ page }) => {
  const startGate = createDeferred();
  const startRequested = createDeferred();
  let startCalls = 0;
  await page.route('**/api/scan/jobs', async route => {
    if (route.request().method() !== 'POST') return route.continue();
    startCalls += 1;
    startRequested.release();
    await startGate.promise;
    await route.fulfill({contentType: 'application/json', body: JSON.stringify({job_id: 'scan-single'})});
  });
  await page.route('**/api/scan/jobs/scan-single', async route => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({status: 'running', progress_percent: 1, completed_substeps: [], completed_stage_ids: []}),
    });
  });
  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    await waitForScanProfilePool(page);
    await page.evaluate(() => {
      const values = {
        last_name: 'Single', first_name: 'Flight', birth_date: '09041966',
        birth_place: 'Augsburg', focus: 'QA Fokus', main_symptom: 'QA Kontext',
      };
      Object.entries(values).forEach(([name, value]) => {
        document.querySelector(`[name="${name}"]`).value = value;
      });
      document.querySelector('#consent-local').checked = true;
      document.querySelector('#consent-safety').checked = true;
      window.__firstScanStart = startScanJob();
      window.__secondScanStart = startScanJob();
    });
    await startRequested.promise;
    await expect(page.locator('#start-analysis-button')).toBeDisabled();
    expect(startCalls).toBe(1);
    startGate.release();
    await page.evaluate(() => Promise.all([window.__firstScanStart, window.__secondScanStart]));
    expect(startCalls).toBe(1);
  } finally {
    startGate.release();
    startRequested.release();
    try {
      await clearSyntheticScanRun(page);
    } finally {
      await releaseDeferredRoutes(page, startGate, startRequested);
    }
  }
});

test('frontend authority: ambiguous scan 422 retains the same operation key across reload', async ({ page }) => {
  const operationKeys = [];
  const requestPayloads = [];
  await page.route('**/api/scan/jobs', async route => {
    if (route.request().method() !== 'POST') return route.continue();
    operationKeys.push(route.request().headers()['idempotency-key']);
    requestPayloads.push(route.request().postDataJSON());
    await route.fulfill({
      status: 422,
      contentType: 'application/json',
      body: JSON.stringify({detail: 'ambiguous validation response'}),
    });
  });
  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    expect(await page.evaluate(
      () => localStorage.getItem('morphic_scan_start_operation_id'),
    )).toBeNull();
    await fillSyntheticScanStartForm(page, {last_name: 'Ambiguous'});

    expect(await page.evaluate(() => startScanJob())).toBe(false);
    const originalKey = await page.evaluate(
      () => localStorage.getItem('morphic_scan_start_operation_id'),
    );
    expect(originalKey).toBeTruthy();
    expect(originalKey).toBe(operationKeys[0]);

    await page.reload();
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    await fillSyntheticScanStartForm(page, {last_name: 'Ambiguous'});
    expect(await page.evaluate(() => startScanJob())).toBe(false);

    expect(operationKeys).toHaveLength(2);
    expect(operationKeys[0]).toBeTruthy();
    expect(operationKeys[1]).toBe(operationKeys[0]);
    expect(requestPayloads[1]).toEqual(requestPayloads[0]);
    expect(await page.evaluate(
      () => localStorage.getItem('morphic_scan_start_operation_id'),
    )).toBe(originalKey);
  } finally {
    await clearSyntheticScanRun(page);
  }
});

test('frontend authority: scan safe-to-replace replaces the stale operation key on retry', async ({ page }) => {
  const operationKeys = [];
  await page.route('**/api/scan/jobs', async route => {
    if (route.request().method() !== 'POST') return route.continue();
    operationKeys.push(route.request().headers()['idempotency-key']);
    await route.fulfill({
      status: 404,
      headers: {'X-Morphic-Start-Operation': 'safe-to-replace'},
      contentType: 'application/json',
      body: JSON.stringify({detail: 'synthetic precreation failure'}),
    });
  });
  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    expect(await page.evaluate(
      () => localStorage.getItem('morphic_scan_start_operation_id'),
    )).toBeNull();
    await fillSyntheticScanStartForm(page, {last_name: 'Replace'});

    expect(await page.evaluate(() => startScanJob())).toBe(false);
    expect(await page.evaluate(
      () => localStorage.getItem('morphic_scan_start_operation_id'),
    )).toBeNull();

    expect(await page.evaluate(() => startScanJob())).toBe(false);
    expect(operationKeys).toHaveLength(2);
    expect(operationKeys[0]).toBeTruthy();
    expect(operationKeys[1]).toBeTruthy();
    expect(operationKeys[1]).not.toBe(operationKeys[0]);
    expect(await page.evaluate(
      () => localStorage.getItem('morphic_scan_start_operation_id'),
    )).toBeNull();
  } finally {
    await clearSyntheticScanRun(page);
  }
});

test('lost scan response reload adopts the committed job after pool drift without a second start', async ({ page }, testInfo) => {
  const operationKeys = [];
  let startCalls = 0;
  let reconcileCalls = 0;
  let committedJobId = null;
  let poolDrifted = false;
  let allowReconcile = false;
  let primaryError = null;
  const catalogB = buildScanProfileCatalog({
    profileLevel: 3,
    profiles: Array.from({length: 9}, (_, index) => ({
      id: `pool-b-${index + 1}`,
      label: `Pool B ${index + 1}`,
    })),
    authority: {fingerprint: 'b'.repeat(64)},
  });
  await page.route('**/api/workbench/scan-profile-catalog?*', async route => {
    if (!poolDrifted) return route.continue();
    await route.fulfill({contentType: 'application/json', body: JSON.stringify(catalogB)});
  });
  await page.route('**/api/scan/start-operation/reconcile', async route => {
    reconcileCalls += 1;
    expect(route.request().method()).toBe('POST');
    expect(route.request().postData()).toBeNull();
    if (!allowReconcile) {
      await route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({detail: 'synthetic reconciliation outage'}),
      });
      return;
    }
    await route.continue();
  });
  await page.route('**/api/scan/jobs', async route => {
    if (route.request().method() !== 'POST') return route.continue();
    startCalls += 1;
    operationKeys.push(route.request().headers()['idempotency-key']);
    const committed = await route.fetch();
    expect(committed.ok()).toBeTruthy();
    committedJobId = (await committed.json()).job_id;
    poolDrifted = true;
    await route.abort('failed');
  });
  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    await fillSyntheticScanStartForm(page, {last_name: 'Reconcile'});

    expect(await page.evaluate(() => startScanJob())).toBe(false);
    const durableKey = await page.evaluate(
      () => localStorage.getItem('morphic_scan_start_operation_id'),
    );
    expect(durableKey).toBe(operationKeys[0]);
    allowReconcile = true;
    await page.reload();
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');

    expect(startCalls).toBe(1);
    expect(operationKeys).toHaveLength(1);
    expect(operationKeys[0]).toBeTruthy();
    expect(committedJobId).toBeTruthy();
    expect(await page.evaluate(() => MorphicWorkbenchState.activeJobId)).toBe(committedJobId);
    expect(await page.evaluate(() => MorphicWorkbenchState.currentStepIndex)).toBe(6);
    expect(await page.evaluate(
      () => MorphicWorkbenchState.scanProfileCatalog?.pool_authority?.fingerprint,
    )).toBe(catalogB.pool_authority.fingerprint);
    expect(await page.evaluate(
      () => localStorage.getItem('morphic_scan_start_operation_id'),
    )).toBe(durableKey);
    expect(reconcileCalls).toBeGreaterThanOrEqual(2);

    expect(await page.evaluate(() => stopActiveScanJob())).toBe(true);
    expect(await page.evaluate(
      () => localStorage.getItem('morphic_scan_start_operation_id'),
    )).toBeNull();
  } catch (error) {
    primaryError = error;
    throw error;
  } finally {
    const cleanupErrors = [];
    if (committedJobId) {
      try {
        const stopped = await page.request.post(`/api/scan/jobs/${committedJobId}/stop`);
        if (stopped.status() !== 404) {
          if (!stopped.ok()) {
            throw new Error(`scan cleanup returned HTTP ${stopped.status()}`);
          }
          const stoppedJob = await stopped.json();
          if (stoppedJob.job_id !== committedJobId) {
            throw new Error(`scan cleanup stopped unexpected job ${stoppedJob.job_id || '<missing>'}`);
          }
          if (!['stopped', 'completed', 'failed'].includes(stoppedJob.status)) {
            throw new Error(`scan cleanup left non-terminal status ${stoppedJob.status || '<missing>'}`);
          }
        }
      } catch (error) {
        cleanupErrors.push(error);
      }
    }
    try {
      await clearSyntheticScanRun(page);
    } catch (error) {
      cleanupErrors.push(error);
    }
    if (cleanupErrors.length) {
      try {
        await testInfo.attach('scan-cleanup-errors', {
          body: Buffer.from(cleanupErrors.map(error => error.stack || String(error)).join('\n\n')),
          contentType: 'text/plain',
        });
      } catch (_) {
        // Preserve the primary test error if attaching cleanup diagnostics also fails.
      }
      if (!primaryError) throw new AggregateError(cleanupErrors, 'scan cleanup failed');
    }
  }
});

test('scan start timeout releases pending state and later reconciliation adopts the committed job', async ({ page }, testInfo) => {
  const responseGate = createDeferred();
  const committedGate = createDeferred();
  let allowReconcile = false;
  let startCalls = 0;
  let committedJobId = null;
  let primaryError = null;
  await page.addInitScript(() => {
    window.MORPHIC_SCAN_START_TIMEOUT_MS = 5;
  });
  await page.route('**/api/scan/start-operation/reconcile', async route => {
    if (!allowReconcile) {
      await route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({detail: 'synthetic reconciliation outage'}),
      });
      return;
    }
    await route.continue();
  });
  await page.route('**/api/scan/jobs', async route => {
    if (route.request().method() !== 'POST') return route.continue();
    startCalls += 1;
    const committed = await route.fetch();
    expect(committed.ok()).toBeTruthy();
    committedJobId = (await committed.json()).job_id;
    committedGate.release();
    await responseGate.promise;
    await route.fulfill({response: committed});
  });
  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    await fillSyntheticScanStartForm(page, {last_name: 'Timeout'});

    const started = await page.evaluate(() => startScanJob());
    await committedGate.promise;
    expect(started).toBe(false);
    expect(startCalls).toBe(1);
    const unresolved = await page.evaluate(() => ({
      pending: MorphicWorkbenchState.scanStartPending,
      mutations: MorphicWorkbenchState.pendingMutations,
      activeJobId: MorphicWorkbenchState.activeJobId,
      key: localStorage.getItem('morphic_scan_start_operation_id'),
    }));
    expect(unresolved.pending).toBe(false);
    expect(unresolved.mutations).toBe(0);
    expect(unresolved.activeJobId).toBeNull();
    expect(unresolved.key).toBeTruthy();

    responseGate.release();
    allowReconcile = true;
    const reconciled = await page.evaluate(async () => {
      window.MORPHIC_SCAN_START_TIMEOUT_MS = 1000;
      return reconcileExistingScanStartOperation();
    });
    expect(reconciled.disposition).toBe('job');
    expect(reconciled.job_id).toBe(committedJobId);
    expect(await page.evaluate(() => MorphicWorkbenchState.activeJobId)).toBe(committedJobId);
    expect(await page.evaluate(
      () => localStorage.getItem('morphic_scan_start_operation_id'),
    )).toBe(unresolved.key);
    expect(startCalls).toBe(1);

    expect(await page.evaluate(() => stopActiveScanJob())).toBe(true);
    expect(await page.evaluate(
      () => localStorage.getItem('morphic_scan_start_operation_id'),
    )).toBeNull();
  } catch (error) {
    primaryError = error;
    throw error;
  } finally {
    responseGate.release();
    committedGate.release();
    const cleanupErrors = [];
    if (committedJobId) {
      try {
        const stopped = await page.request.post(`/api/scan/jobs/${committedJobId}/stop`);
        if (![200, 404].includes(stopped.status())) {
          throw new Error(`scan cleanup returned HTTP ${stopped.status()}`);
        }
      } catch (error) {
        cleanupErrors.push(error);
      }
    }
    try {
      await clearSyntheticScanRun(page);
    } catch (error) {
      cleanupErrors.push(error);
    }
    await releaseDeferredRoutes(page, responseGate, committedGate);
    if (cleanupErrors.length) {
      try {
        await testInfo.attach('scan-timeout-cleanup-errors', {
          body: Buffer.from(cleanupErrors.map(error => error.stack || String(error)).join('\n\n')),
          contentType: 'text/plain',
        });
      } catch (_) {
        // Preserve the primary test error if attaching cleanup diagnostics also fails.
      }
      if (!primaryError) throw new AggregateError(cleanupErrors, 'scan timeout cleanup failed');
    }
  }
});

test('payload mismatch keeps the original scan operation key fail closed', async ({ page }) => {
  const operationKeys = [];
  let startCalls = 0;
  await page.route('**/api/scan/jobs', async route => {
    if (route.request().method() !== 'POST') return route.continue();
    startCalls += 1;
    operationKeys.push(route.request().headers()['idempotency-key']);
    if (startCalls === 1) {
      await route.abort('failed');
      return;
    }
    await route.fulfill({
      status: 409,
      contentType: 'application/json',
      body: JSON.stringify({detail: 'start operation identity mismatch'}),
    });
  });
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  await waitForScanProfilePool(page);
  const fillStartForm = async focus => page.evaluate(value => {
    const values = {
      last_name: 'Mismatch', first_name: 'Synthetic', birth_date: '09041966',
      birth_place: 'Augsburg', focus: value, main_symptom: 'QA Kontext',
    };
    Object.entries(values).forEach(([name, fieldValue]) => {
      document.querySelector(`[name="${name}"]`).value = fieldValue;
    });
    document.querySelector('#consent-local').checked = true;
    document.querySelector('#consent-safety').checked = true;
  }, focus);
  await fillStartForm('QA Fokus A');

  expect(await page.evaluate(() => startScanJob())).toBe(false);
  const originalKey = await page.evaluate(
    () => localStorage.getItem('morphic_scan_start_operation_id'),
  );
  expect(originalKey).toBeTruthy();

  await page.reload();
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  await waitForScanProfilePool(page);
  await fillStartForm('QA Fokus B');
  expect(await page.evaluate(() => startScanJob())).toBe(false);

  expect(startCalls).toBe(2);
  expect(operationKeys[1]).toBe(operationKeys[0]);
  expect(await page.evaluate(
    () => localStorage.getItem('morphic_scan_start_operation_id'),
  )).toBe(originalKey);
});

test('New Case is blocked until a delayed scan start returns authoritative job id', async ({ page }) => {
  const startGate = createDeferred();
  const startRequested = createDeferred();
  await page.route('**/api/scan/jobs', async route => {
    if (route.request().method() !== 'POST') return route.continue();
    startRequested.release();
    await startGate.promise;
    await route.fulfill({contentType: 'application/json', body: JSON.stringify({job_id: 'scan-delayed'})});
  });
  await page.route('**/api/scan/jobs/scan-delayed', async route => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({status: 'running', progress_percent: 1, completed_substeps: [], completed_stage_ids: []}),
    });
  });
  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    await waitForScanProfilePool(page);
    await page.evaluate(() => {
      const values = {
        last_name: 'Delayed', first_name: 'Authority', birth_date: '09041966',
        birth_place: 'Augsburg', focus: 'QA Fokus', main_symptom: 'QA Kontext',
      };
      Object.entries(values).forEach(([name, value]) => {
        document.querySelector(`[name="${name}"]`).value = value;
      });
      document.querySelector('#consent-local').checked = true;
      document.querySelector('#consent-safety').checked = true;
      window.__generationBeforeDelayedStart = caseGeneration;
      window.__delayedScanStart = startScanJob();
    });
    await startRequested.promise;

    const resetResult = await page.evaluate(() => resetWorkbenchForNewCase());
    expect(resetResult).toBe(false);
    expect(await page.evaluate(() => caseGeneration)).toBe(
      await page.evaluate(() => window.__generationBeforeDelayedStart),
    );

    startGate.release();
    await page.evaluate(() => window.__delayedScanStart);
    expect(await page.evaluate(() => MorphicWorkbenchState.activeJobId)).toBe('scan-delayed');
  } finally {
    startGate.release();
    startRequested.release();
    try {
      await clearSyntheticScanRun(page);
    } finally {
      await releaseDeferredRoutes(page, startGate, startRequested);
    }
  }
});

test('harmonization start is single-flight and keeps one active poll authority', async ({ page }) => {
  const startGate = createDeferred();
  const startRequested = createDeferred();
  let startCalls = 0;
  let pollCalls = 0;
  const pollGate = createDeferred();
  const pollRequested = createDeferred();
  await page.route('**/api/harmonization/jobs', async route => {
    if (route.request().method() !== 'POST') return route.continue();
    startCalls += 1;
    startRequested.release();
    await startGate.promise;
    await route.fulfill({contentType: 'application/json', body: JSON.stringify({job_id: 'harm-single'})});
  });
  await page.route('**/api/harmonization/jobs/harm-single', async route => {
    pollCalls += 1;
    pollRequested.release();
    await pollGate.promise;
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({status: 'running', progress_percent: 1, cycles_completed: 0, total_cycles: 2}),
    });
  });
  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    await prepareSyntheticHarmonizationStart(page, {
      report_id: 'report-single',
      workbench_mode: 'standard',
    });
    await page.evaluate(() => {
      window.__firstHarmonizationStart = startHarmonizationJob();
      window.__secondHarmonizationStart = startHarmonizationJob();
    });
    await startRequested.promise;
    await expect(page.locator('#harmonization-start-button')).toBeDisabled();
    expect(startCalls).toBe(1);
    startGate.release();
    await page.evaluate(() => Promise.all([
      window.__firstHarmonizationStart,
      window.__secondHarmonizationStart,
    ]));
    expect(startCalls).toBe(1);
    expect(await page.evaluate(() => MorphicWorkbenchState.activeHarmonizationJobId)).toBe('harm-single');
    await pollRequested.promise;
    await page.evaluate(() => {
      window.__manualHarmonizationPollA = pollHarmonizationJob('harm-single');
      window.__manualHarmonizationPollB = pollHarmonizationJob('harm-single');
    });
    expect(pollCalls).toBe(1);
    pollGate.release();
    await page.evaluate(() => Promise.all([
      window.__manualHarmonizationPollA,
      window.__manualHarmonizationPollB,
    ]));
    expect(pollCalls).toBe(1);
  } finally {
    startGate.release();
    startRequested.release();
    pollGate.release();
    pollRequested.release();
    try {
      await clearSyntheticHarmonizationRun(page);
    } finally {
      await releaseDeferredRoutes(
        page,
        startGate,
        startRequested,
        pollGate,
        pollRequested
      );
    }
  }
});

test('frontend authority: mocked harmonization response loss reuses the key across reload', async ({ page }) => {
  const operationKeys = [];
  const requestPayloads = [];
  // This transport state machine proves browser authority only; backend durability is covered separately.
  let committed = null;
  let startCalls = 0;
  let pollCalls = 0;
  await page.route('**/api/harmonization/jobs', async route => {
    if (route.request().method() !== 'POST') return route.continue();
    startCalls += 1;
    const operationKey = route.request().headers()['idempotency-key'];
    operationKeys.push(operationKey);
    requestPayloads.push(route.request().postDataJSON());
    if (startCalls === 1) {
      committed = {jobId: 'harm-frontend-authority', operationKey};
      await route.abort('failed');
      return;
    }
    if (operationKey !== committed.operationKey) {
      await route.fulfill({
        status: 409,
        contentType: 'application/json',
        body: JSON.stringify({detail: 'mocked harmonization authority mismatch'}),
      });
      return;
    }
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({job_id: committed.jobId}),
    });
  });
  await page.route('**/api/harmonization/jobs/harm-frontend-authority', async route => {
    pollCalls += 1;
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({
        status: 'running', progress_percent: 1, cycles_completed: 0,
        total_cycles: 2, phase: 'pulse', lease: {},
      }),
    });
  });
  const harmonizationPayload = {
    intention: 'clearing',
    target_frequency: 528,
    use_cpu: true,
    use_gpu: false,
    use_ram: true,
    use_websocket: false,
    use_driver_layer: false,
    pulse_seconds: 1.5,
    pause_seconds: 0.5,
    duration_factor: 2,
    report_id: 'report-frontend-authority',
    workbench_mode: 'expert',
  };
  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    expect(await page.evaluate(
      () => localStorage.getItem('morphic_harmonization_start_operation_id'),
    )).toBeNull();
    await prepareSyntheticHarmonizationStart(page, harmonizationPayload);
    await expect(page.locator('#harmonization-start-button')).toBeEnabled();
    expect(await page.evaluate(() => formHarmonizationPayload())).toEqual(harmonizationPayload);

    await page.evaluate(() => startHarmonizationJob());
    const originalKey = await page.evaluate(
      () => localStorage.getItem('morphic_harmonization_start_operation_id'),
    );
    expect(originalKey).toBeTruthy();
    expect(originalKey).toBe(committed.operationKey);

    await page.reload();
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    expect(await page.evaluate(
      () => localStorage.getItem('morphic_harmonization_start_operation_id'),
    )).toBe(originalKey);
    await prepareSyntheticHarmonizationStart(page, harmonizationPayload);
    await expect(page.locator('#harmonization-start-button')).toBeEnabled();
    expect(await page.evaluate(() => formHarmonizationPayload())).toEqual(harmonizationPayload);
    await page.evaluate(() => startHarmonizationJob());

    expect(startCalls).toBe(2);
    expect(operationKeys).toEqual([originalKey, originalKey]);
    expect(requestPayloads).toEqual([harmonizationPayload, harmonizationPayload]);
    expect(await page.evaluate(
      () => localStorage.getItem('morphic_harmonization_start_operation_id'),
    )).toBeNull();
    expect(await page.evaluate(
      () => MorphicWorkbenchState.activeHarmonizationJobId,
    )).toBe(committed.jobId);
    await expect(page.locator('#harmonization-job-id-label')).toHaveText(committed.jobId);
    await expect(page.locator('#harmonization-status-label')).toHaveText('laeuft');
    expect(pollCalls).toBe(1);
  } finally {
    await clearSyntheticHarmonizationRun(page);
  }
});

test('frontend authority: harmonization safe-to-replace clears the operation key', async ({ page }) => {
  const operationKeys = [];
  const requestPayloads = [];
  await page.route('**/api/harmonization/jobs', async route => {
    if (route.request().method() !== 'POST') return route.continue();
    operationKeys.push(route.request().headers()['idempotency-key']);
    requestPayloads.push(route.request().postDataJSON());
    await route.fulfill({
      status: 404,
      headers: {'X-Morphic-Start-Operation': 'safe-to-replace'},
      contentType: 'application/json',
      body: JSON.stringify({detail: 'synthetic report not found'}),
    });
  });
  const harmonizationPayload = {
    intention: 'protection',
    target_frequency: 432,
    use_cpu: true,
    use_gpu: false,
    use_ram: false,
    use_websocket: false,
    use_driver_layer: true,
    pulse_seconds: 2,
    pause_seconds: 1,
    duration_factor: 1,
    report_id: 'report-safe-to-replace',
    workbench_mode: 'standard',
  };
  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    expect(await page.evaluate(
      () => localStorage.getItem('morphic_harmonization_start_operation_id'),
    )).toBeNull();
    await prepareSyntheticHarmonizationStart(page, harmonizationPayload);
    await expect(page.locator('#harmonization-start-button')).toBeEnabled();
    expect(await page.evaluate(() => formHarmonizationPayload())).toEqual(harmonizationPayload);

    await page.evaluate(() => startHarmonizationJob());

    expect(operationKeys).toHaveLength(1);
    expect(operationKeys[0]).toBeTruthy();
    expect(requestPayloads).toEqual([harmonizationPayload]);
    expect(await page.evaluate(() => ({
      stored: localStorage.getItem('morphic_harmonization_start_operation_id'),
      memory: MorphicWorkbenchState.harmonizationStartOperationId,
    }))).toEqual({stored: null, memory: null});
  } finally {
    await clearSyntheticHarmonizationRun(page);
  }
});

test('latest report selection wins when preview responses complete out of order', async ({ page }) => {
  const reportAGate = createDeferred();
  const reportARequested = createDeferred();
  await page.route('**/api/reports/report-a/preview', async route => {
    reportARequested.release();
    await reportAGate.promise;
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({mode: 'text', kind: 'TXT', title: 'A', size: 1, content: 'Report A'}),
    });
  });
  await page.route('**/api/reports/report-b/preview', async route => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({mode: 'text', kind: 'TXT', title: 'B', size: 1, content: 'Report B'}),
    });
  });
  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    await page.evaluate(() => { window.__previewA = renderReportPreview('report-a'); });
    await reportARequested.promise;
    await page.evaluate(() => { window.__previewB = renderReportPreview('report-b'); });
    await page.evaluate(() => window.__previewB);
    await expect(page.locator('#report-preview-text')).toHaveText('Report B');
    reportAGate.release();
    await page.evaluate(() => window.__previewA);
    await expect(page.locator('#report-preview-text')).toHaveText('Report B');
    expect(await page.evaluate(() => MorphicWorkbenchState.activeReportId)).toBe('report-b');
  } finally {
    await releaseDeferredRoutes(page, reportAGate, reportARequested);
  }
});

test('Gate 4 report catalog supports exact auto preview, roving focus and mobile orientation', async ({ page }) => {
  const errors = captureErrors(page);
  const previewRequests = [];
  let catalog = {
    clients: [{
      client_id: 'active-client',
      label: 'Aktiver Klient',
      sessions: [{
        session_id: 'session-active',
        label: 'Aktive Session',
        files: [
          {id: 'active-html', kind: 'HTML', file_name: 'Aktiv.html', modified_at: '2026-08-01T10:00:00Z', size: 100},
          {id: 'active-json', kind: 'JSON', file_name: 'Aktiv.json', modified_at: '2026-08-01T10:03:00Z', size: 80},
          {id: 'active-pdf', kind: 'PDF', file_name: 'Aktiv.pdf', modified_at: '2026-08-01T10:05:00Z', size: 120},
        ],
      }],
    }, {
      client_id: 'other-client',
      label: 'Anderer Klient',
      sessions: [{
        session_id: 'session-other',
        label: 'Neuere Fremd-Session',
        files: [{id: 'other-html', kind: 'HTML', file_name: 'Fremd.html', modified_at: '2026-08-01T12:00:00Z', size: 110}],
      }],
    }],
  };
  await page.route('**/api/scan/jobs/gate4-report/results', async route => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({report_session_id: 'session-active', top_profiles: []}),
    });
  });
  await page.route('**/api/workbench/run-trace/gate4-report', async route => {
    await route.fulfill({contentType: 'application/json', body: JSON.stringify({status: 'completed'})});
  });
  await page.route('**/api/reports', async route => {
    await route.fulfill({contentType: 'application/json', body: JSON.stringify(catalog)});
  });
  await page.route('**/api/reports/*/preview', async route => {
    const reportId = decodeURIComponent(new URL(route.request().url()).pathname.split('/').at(-2));
    previewRequests.push(reportId);
    const mode = reportId.endsWith('html') ? 'html' : reportId.endsWith('pdf') ? 'file' : 'text';
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({
        mode,
        kind: reportId.endsWith('pdf') ? 'PDF' : reportId.endsWith('json') ? 'JSON' : 'HTML',
        title: reportId,
        file_name: `${reportId}.txt`,
        content: mode === 'html' ? `<p>${reportId}</p>` : `preview:${reportId}`,
        size: 10,
      }),
    });
  });

  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  await page.evaluate(async () => {
    MorphicWorkbenchState.activeJobId = 'gate4-report';
    MorphicWorkbenchState.scanRunActive = true;
    await loadScanResults('gate4-report', caseGeneration, true);
    MorphicWorkbenchState.activeJobId = null;
    MorphicWorkbenchState.scanRunActive = false;
    await loadReports(caseGeneration, true);
    enterStep(10, false);
  });

  await expect(page.locator('a[href="/workflow-stepping"]')).toHaveCount(0);
  await expect(page.locator('#report-list')).toHaveAttribute('role', 'toolbar');
  await expect(page.locator('#report-list')).toHaveAttribute('aria-orientation', 'horizontal');
  await expect(page.locator('.report-item[aria-pressed="true"]')).toHaveAttribute('data-report-id', 'active-html');
  expect(previewRequests).toEqual(['active-html']);

  const selected = page.locator('.report-item[aria-pressed="true"]');
  await selected.focus();
  await page.keyboard.press('ArrowRight');
  expect(await page.evaluate(() => document.activeElement?.dataset?.reportId)).toBe('active-json');
  expect(previewRequests).toEqual(['active-html']);
  await page.keyboard.press('Enter');
  await expect(page.locator('.report-item[aria-pressed="true"]')).toHaveAttribute('data-report-id', 'active-json');
  expect(previewRequests).toEqual(['active-html', 'active-json']);
  await page.keyboard.press('Home');
  expect(await page.evaluate(() => document.activeElement?.dataset?.reportId)).toBe('active-html');
  await page.keyboard.press('ArrowLeft');
  expect(await page.evaluate(() => document.activeElement?.dataset?.reportId)).toBe('active-html');
  await page.keyboard.press('End');
  expect(await page.evaluate(() => document.activeElement?.dataset?.reportId)).toBe('other-html');
  await page.keyboard.press('ArrowRight');
  expect(await page.evaluate(() => document.activeElement?.dataset?.reportId)).toBe('other-html');
  expect(previewRequests).toEqual(['active-html', 'active-json']);

  catalog = {...catalog, clients: catalog.clients.map(client => ({...client}))};
  await page.evaluate(() => loadReports(caseGeneration, true));
  await expect(page.locator('.report-item[aria-pressed="true"]')).toHaveAttribute('data-report-id', 'active-json');
  await expect(page.locator('.report-item[tabindex="0"]')).toHaveAttribute('data-report-id', 'other-html');
  expect(await page.evaluate(() => MorphicWorkbenchState.reportFocusId)).toBe('other-html');
  expect(previewRequests).toEqual(['active-html', 'active-json']);

  await page.setViewportSize({width: 375, height: 812});
  await expect(page.locator('#report-list')).toHaveAttribute('aria-orientation', 'vertical');
  await page.locator('.report-item[aria-pressed="true"]').focus();
  await page.keyboard.press('ArrowDown');
  expect(await page.evaluate(() => document.activeElement?.dataset?.reportId)).toBe('active-pdf');
  expect(await page.evaluate(() => document.documentElement.scrollWidth === document.documentElement.clientWidth)).toBe(true);

  await page.evaluate(() => enterStep(10, false));
  await expect(page.locator('#new-case-button')).toBeEnabled();
  await page.locator('#new-case-button').click();
  await expect(page.locator('#report-list .report-item')).toHaveCount(0);
  await expect(page.locator('#report-preview-frame')).toHaveJSProperty('srcdoc', '');
  await expect(page.locator('#report-open-link')).toHaveAttribute('href', '#');
  expect(await page.evaluate(() => ({
    session: MorphicWorkbenchState.activeReportSessionId,
    report: MorphicWorkbenchState.activeReportId,
    focus: MorphicWorkbenchState.reportFocusId,
    auto: MorphicWorkbenchState.reportAutoSelectionKey,
  }))).toEqual({session: null, report: null, focus: null, auto: null});

  const workflowResponse = await page.goto('/workflow-stepping');
  expect(workflowResponse.status()).toBe(200);
  await expect(page.locator('.workflow-step')).toHaveCount(12);
  expect(errors).toEqual([]);
});

test('browser auth retries without persisting the API key and unlocks through cookie session', async ({ page }) => {
  let loginAttempts = 0;
  await page.route('**/api/auth/status', async route => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({required: true, authenticated: false}),
    });
  });
  await page.route('**/api/auth/session', async route => {
    loginAttempts += 1;
    if (loginAttempts === 1) {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({detail: 'Invalid or missing API key'}),
      });
      return;
    }
    await route.fulfill({
      contentType: 'application/json',
      headers: {'Set-Cookie': 'morphic_session=opaque-test-token; HttpOnly; SameSite=Strict; Path=/'},
      body: JSON.stringify({status: 'authenticated'}),
    });
  });

  await page.goto('/');
  await expect(page.locator('#auth-session-panel')).toBeVisible();
  await expect(page.locator('#main-content')).toHaveAttribute('aria-hidden', 'true');
  await page.locator('#auth-session-form [name="api_key"]').fill('wrong-key');
  await page.locator('#auth-session-form button[type="submit"]').click();
  await expect(page.locator('#auth-session-state')).toContainText('Invalid');
  await expect(page.locator('#auth-session-form [name="api_key"]')).toHaveValue('');

  await page.locator('#auth-session-form [name="api_key"]').fill('qa-secret-key');
  await page.locator('#auth-session-form button[type="submit"]').click();

  await expect(page.locator('#auth-session-panel')).toBeHidden();
  await expect(page.locator('#main-content')).toHaveAttribute('aria-hidden', 'false');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  expect(loginAttempts).toBe(2);
  expect(await page.evaluate(() => localStorage.length)).toBe(0);
});

test('pending harmonization keeps polling and updates progress through terminal state', async ({ page }) => {
  const statuses = [
    {status: 'pending', progress_percent: 7, cycles_completed: 0, total_cycles: 2, phase: 'pending'},
    {status: 'running', progress_percent: 67, cycles_completed: 1, total_cycles: 2, phase: 'pause'},
    {status: 'completed', progress_percent: 100, cycles_completed: 2, total_cycles: 2, phase: 'completed'},
  ];
  let polls = 0;
  await page.route('**/api/harmonization/jobs/harm-poll', async route => {
    const payload = statuses[Math.min(polls, statuses.length - 1)];
    polls += 1;
    await route.fulfill({contentType: 'application/json', body: JSON.stringify(payload)});
  });
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  await page.evaluate(() => {
    const nativeSetTimeout = window.setTimeout.bind(window);
    window.setTimeout = (callback, delay) => nativeSetTimeout(callback, Math.min(delay, 20));
    MorphicWorkbenchState.activeHarmonizationJobId = 'harm-poll';
    pollHarmonizationJob('harm-poll');
  });
  await expect.poll(() => polls).toBeGreaterThanOrEqual(3);
  await expect(page.locator('#harmonization-progress')).toHaveAttribute('aria-valuenow', '100');
  await expect(page.locator('#harmonization-status-label')).toHaveText('abgeschlossen');
});

test('failed New Case teardown preserves generation and authoritative polling', async ({ page }) => {
  const firstPollGate = createDeferred();
  const firstPollRequested = createDeferred();
  let pollCalls = 0;
  await page.route('**/api/scan/jobs/scan-live', async route => {
    pollCalls += 1;
    if (pollCalls === 1) {
      firstPollRequested.release();
      await firstPollGate.promise;
    }
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({status: 'running', progress_percent: 25, completed_substeps: [], completed_stage_ids: []}),
    });
  });
  await page.route('**/api/scan/jobs/scan-live/stop', async route => {
    await route.fulfill({status: 500, contentType: 'application/json', body: JSON.stringify({detail: 'synthetic stop failure'})});
  });
  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
    await page.evaluate(() => {
      const nativeSetTimeout = window.setTimeout.bind(window);
      window.setTimeout = (callback, delay) => nativeSetTimeout(callback, Math.min(delay, 20));
      MorphicWorkbenchState.activeJobId = 'scan-live';
      window.__livePoll = pollScanJob('scan-live');
    });
    await firstPollRequested.promise;
    expect(await page.evaluate(() => resetWorkbenchForNewCase())).toBe(false);
    firstPollGate.release();
    await page.evaluate(() => window.__livePoll);
    await expect.poll(() => pollCalls).toBeGreaterThanOrEqual(2);
    expect(await page.evaluate(() => MorphicWorkbenchState.activeJobId)).toBe('scan-live');
  } finally {
    firstPollGate.release();
    firstPollRequested.release();
    try {
      await clearSyntheticScanRun(page);
    } finally {
      await releaseDeferredRoutes(page, firstPollGate, firstPollRequested);
    }
  }
});

test('partial New Case teardown clears stopped scan authority and retains live harmonization', async ({ page }) => {
  await page.route('**/api/scan/jobs/scan-partial/stop', async route => {
    await route.fulfill({contentType: 'application/json', body: JSON.stringify({status: 'stopped'})});
  });
  await page.route('**/api/harmonization/jobs/harm-partial/stop', async route => {
    await route.fulfill({status: 500, contentType: 'application/json', body: JSON.stringify({detail: 'synthetic harmonization stop failure'})});
  });
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  const beforeGeneration = await page.evaluate(() => {
    MorphicWorkbenchState.activeJobId = 'scan-partial';
    MorphicWorkbenchState.scanRunActive = true;
    MorphicWorkbenchState.activeHarmonizationJobId = 'harm-partial';
    MorphicWorkbenchState.harmonizationRunActive = true;
    return caseGeneration;
  });

  expect(await page.evaluate(() => resetWorkbenchForNewCase())).toBe(false);

  const state = await page.evaluate(() => ({
    scan: MorphicWorkbenchState.activeJobId,
    scanActive: MorphicWorkbenchState.scanRunActive,
    harmonization: MorphicWorkbenchState.activeHarmonizationJobId,
    harmonizationActive: MorphicWorkbenchState.harmonizationRunActive,
    resetInProgress: MorphicWorkbenchState.resetInProgress,
    generation: caseGeneration,
  }));
  expect(state).toEqual({
    scan: null,
    scanActive: false,
    harmonization: 'harm-partial',
    harmonizationActive: true,
    resetInProgress: false,
    generation: beforeGeneration,
  });
  await expect(page.locator('#preview-state')).toContainText('Teilweiser Fallwechsel');
});

test('reset mutation fence blocks competing writes before fetch', async ({ page }) => {
  let draftWrites = 0;
  await page.route('**/api/workbench/draft', async route => {
    if (route.request().method() === 'PUT') draftWrites += 1;
    await route.continue();
  });
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');

  const result = await page.evaluate(async () => {
    MorphicWorkbenchState.resetInProgress = true;
    try {
      await MorphicWorkbenchApi.saveDraft({draft: {}, persist_sensitive_data: false});
      return 'unexpected-success';
    } catch (error) {
      return error.message;
    } finally {
      MorphicWorkbenchState.resetInProgress = false;
    }
  });

  expect(result).toContain('Fallwechsel');
  expect(draftWrites).toBe(0);
});

test('stale bootstrap response cannot rehydrate a reset case', async ({ page }) => {
  const registryGate = createDeferred();
  const registryRequested = createDeferred();
  await page.route('**/api/workbench/registry', async route => {
    registryRequested.release();
    await registryGate.promise;
    await route.fulfill({contentType: 'application/json', body: JSON.stringify({steps: [{id: 'stale', label: 'Stale'}]})});
  });

  let navigation = null;
  try {
    navigation = page.goto('/', {waitUntil: 'domcontentloaded'});
    await registryRequested.promise;
    await page.waitForFunction(() => typeof resetWorkbenchForNewCase === 'function');
    expect(await page.evaluate(() => resetWorkbenchForNewCase())).toBe(true);
    registryGate.release();
    await navigation;
    await page.waitForTimeout(100);

    const state = await page.evaluate(() => ({
      registry: MorphicWorkbenchState.registry,
      step: MorphicWorkbenchState.currentStepIndex,
      job: MorphicWorkbenchState.activeJobId,
    }));
    expect(state).toEqual({registry: null, step: 0, job: null});
  } finally {
    registryGate.release();
    registryRequested.release();
    try {
      if (navigation) await navigation.catch(() => {});
    } finally {
      await releaseDeferredRoutes(page, registryGate, registryRequested);
    }
  }
});

test('stale health, sources and hardware loaders cannot rehydrate a reset case', async ({ browser, baseURL }) => {
  for (const scenario of ['health', 'sources', 'hardware']) {
    let page = null;
    let navigation = null;
    const routeGate = createDeferred();
    const requestStarted = createDeferred();
    try {
      page = await browser.newPage({baseURL});
      const pattern = scenario === 'health'
        ? '**/api/health'
        : scenario === 'sources'
          ? '**/api/sources'
          : '**/api/workbench/hardware*';
      await page.route(pattern, async route => {
        requestStarted.release();
        await routeGate.promise;
        const body = scenario === 'health'
          ? {python: {version: 'STALE-PYTHON'}, profiles: {count: 999}, databases: {}}
          : scenario === 'sources'
            ? {count: 999, sources: [{id: 'STALE-SOURCE', status: 'active'}], status_counts: {active: 999}}
            : {components: {}, marker: 'STALE-HARDWARE'};
        await route.fulfill({contentType: 'application/json', body: JSON.stringify(body)});
      });

      navigation = page.goto('/', {waitUntil: 'domcontentloaded'});
      await requestStarted.promise;
      await page.waitForFunction(() => typeof resetWorkbenchForNewCase === 'function');
      expect(await page.evaluate(() => resetWorkbenchForNewCase())).toBe(true);
      routeGate.release();
      await navigation;
      await page.waitForTimeout(100);

      if (scenario === 'health') {
        await expect(page.locator('#python-version')).not.toHaveText('STALE-PYTHON');
      } else if (scenario === 'sources') {
        await expect(page.locator('#source-pill')).not.toContainText('999');
        await expect(page.locator('#source-list')).not.toContainText('STALE-SOURCE');
      } else {
        expect(await page.evaluate(() => MorphicWorkbenchState.hardwareTruth)).toBeNull();
      }
    } finally {
      routeGate.release();
      requestStarted.release();
      try {
        if (navigation) await navigation.catch(() => {});
      } finally {
        if (page) {
          try {
            await releaseDeferredRoutes(page, routeGate, requestStarted);
          } finally {
            await page.close();
          }
        }
      }
    }
  }
});

test('completed scans ignore optional run-trace sync and load failures', async ({ page }) => {
  const statuses = [404, 409, 429, 500, 503];
  const calls = new Map();
  for (const status of statuses) {
    const jobId = `scan-trace-optional-${status}`;
    calls.set(jobId, {sync: 0, load: 0});
    await page.route(`**/api/scan/jobs/${jobId}`, async route => {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'completed', progress_percent: 100, completed_substeps: [],
          completed_stage_ids: [], current_stage_id: null,
        }),
      });
    });
    await page.route(`**/api/scan/jobs/${jobId}/sync-trace`, async route => {
      calls.get(jobId).sync += 1;
      await route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify({detail: 'optional trace sync unavailable'}),
      });
    });
    await page.route(`**/api/scan/jobs/${jobId}/results`, async route => {
      await route.fulfill({contentType: 'application/json', body: JSON.stringify({top_profiles: []})});
    });
    await page.route(`**/api/workbench/run-trace/${jobId}`, async route => {
      calls.get(jobId).load += 1;
      await route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify({detail: 'optional trace load unavailable'}),
      });
    });
  }
  await page.route('**/api/reports', async route => {
    await route.fulfill({contentType: 'application/json', body: JSON.stringify({clients: []})});
  });
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');

  for (const status of statuses) {
    const jobId = `scan-trace-optional-${status}`;
    const result = await page.evaluate(async id => {
      const originalTimeout = window.setTimeout;
      window.setTimeout = () => 1;
      try {
        showInlineState('', 'neutral');
        MorphicWorkbenchState.activeJobId = id;
        MorphicWorkbenchState.scanRunActive = true;
        await pollScanJob(id, caseGeneration, 0);
        return {
          status: document.querySelector('#job-status-label').textContent,
          inline: document.querySelector('#preview-state').textContent,
          active: MorphicWorkbenchState.scanRunActive,
        };
      } finally {
        window.setTimeout = originalTimeout;
        MorphicWorkbenchState.activeJobId = null;
      }
    }, jobId);
    expect(result.status).toBe('abgeschlossen');
    expect(result.inline).not.toContain('nicht erreichbar');
    expect(result.active).toBe(false);
    expect(calls.get(jobId)).toEqual({sync: 1, load: 1});
  }
});

test('completed scans ignore optional run-trace network failures', async ({ page }) => {
  const jobId = 'scan-trace-optional-network';
  const calls = {sync: 0, load: 0};
  await page.route(`**/api/scan/jobs/${jobId}`, async route => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({
        status: 'completed', progress_percent: 100, completed_substeps: [],
        completed_stage_ids: [], current_stage_id: null,
      }),
    });
  });
  await page.route(`**/api/scan/jobs/${jobId}/sync-trace`, async route => {
    calls.sync += 1;
    await route.abort();
  });
  await page.route(`**/api/scan/jobs/${jobId}/results`, async route => {
    await route.fulfill({contentType: 'application/json', body: JSON.stringify({top_profiles: []})});
  });
  await page.route(`**/api/workbench/run-trace/${jobId}`, async route => {
    calls.load += 1;
    await route.abort();
  });
  await page.route('**/api/reports', async route => {
    await route.fulfill({contentType: 'application/json', body: JSON.stringify({clients: []})});
  });
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');

  const result = await page.evaluate(async id => {
    const originalTimeout = window.setTimeout;
    window.setTimeout = () => 1;
    try {
      showInlineState('', 'neutral');
      MorphicWorkbenchState.activeJobId = id;
      MorphicWorkbenchState.scanRunActive = true;
      await pollScanJob(id, caseGeneration, 0);
      return {
        status: document.querySelector('#job-status-label').textContent,
        inline: document.querySelector('#preview-state').textContent,
        active: MorphicWorkbenchState.scanRunActive,
      };
    } finally {
      window.setTimeout = originalTimeout;
      MorphicWorkbenchState.activeJobId = null;
    }
  }, jobId);
  expect(result.status).toBe('abgeschlossen');
  expect(result.inline).not.toContain('nicht erreichbar');
  expect(result.active).toBe(false);
  expect(calls).toEqual({sync: 1, load: 1});
});

test('run-trace sync and load authentication failures pause completed polling', async ({ page }) => {
  const scenarios = [
    {jobId: 'scan-trace-sync-401', target: 'sync', status: 401},
    {jobId: 'scan-trace-sync-403', target: 'sync', status: 403},
    {jobId: 'scan-trace-load-401', target: 'load', status: 401},
    {jobId: 'scan-trace-load-403', target: 'load', status: 403},
  ];
  for (const scenario of scenarios) {
    await page.route(`**/api/scan/jobs/${scenario.jobId}`, async route => {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'completed', progress_percent: 100, completed_substeps: [],
          completed_stage_ids: [], current_stage_id: null,
        }),
      });
    });
    await page.route(`**/api/scan/jobs/${scenario.jobId}/sync-trace`, async route => {
      const status = scenario.target === 'sync' ? scenario.status : 200;
      await route.fulfill({status, contentType: 'application/json', body: JSON.stringify({})});
    });
    await page.route(`**/api/scan/jobs/${scenario.jobId}/results`, async route => {
      await route.fulfill({contentType: 'application/json', body: JSON.stringify({top_profiles: []})});
    });
    await page.route(`**/api/workbench/run-trace/${scenario.jobId}`, async route => {
      const status = scenario.target === 'load' ? scenario.status : 200;
      await route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify(status === 200 ? {status: 'completed'} : {detail: 'auth'}),
      });
    });
  }
  await page.route('**/api/reports', async route => {
    await route.fulfill({contentType: 'application/json', body: JSON.stringify({clients: []})});
  });
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');

  for (const scenario of scenarios) {
    const result = await page.evaluate(async id => {
      const originalTimeout = window.setTimeout;
      window.setTimeout = () => 1;
      try {
        showInlineState('', 'neutral');
        MorphicWorkbenchState.activeJobId = id;
        MorphicWorkbenchState.scanRunActive = true;
        await pollScanJob(id, caseGeneration, 0);
        return {
          status: document.querySelector('#job-status-label').textContent,
          inline: document.querySelector('#preview-state').textContent,
          refreshDisabled: document.querySelector('#scan-refresh-button').disabled,
        };
      } finally {
        window.setTimeout = originalTimeout;
        MorphicWorkbenchState.activeJobId = null;
      }
    }, scenario.jobId);
    expect(result.status).toContain('Anmeldung erforderlich');
    expect(result.inline).toContain('erneuter Anmeldung');
    expect(result.refreshDisabled).toBe(false);
  }
});

test('poll failures become visible, back off and pause on auth or retry exhaustion', async ({ page }) => {
  await page.route('**/api/scan/jobs/scan-offline', async route => {
    await route.fulfill({status: 503, contentType: 'application/json', body: JSON.stringify({detail: 'offline'})});
  });
  await page.route('**/api/harmonization/jobs/harm-auth', async route => {
    await route.fulfill({status: 401, contentType: 'application/json', body: JSON.stringify({detail: 'auth'})});
  });
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');

  const scan = await page.evaluate(async () => {
    MorphicWorkbenchState.activeJobId = 'scan-offline';
    const delays = [];
    const original = window.setTimeout;
    window.setTimeout = (callback, delay) => { delays.push(delay); return 1; };
    try {
      await pollScanJob('scan-offline', caseGeneration, 0);
      const first = document.querySelector('#job-status-label').textContent;
      await pollScanJob('scan-offline', caseGeneration, 5);
      return {first, final: document.querySelector('#job-status-label').textContent, delays};
    } finally {
      window.setTimeout = original;
      MorphicWorkbenchState.activeJobId = null;
    }
  });
  expect(scan.first).toContain('Verbindung');
  expect(scan.final).toContain('pausiert');
  expect(scan.delays).toEqual([2000]);

  const harmonization = await page.evaluate(async () => {
    MorphicWorkbenchState.activeHarmonizationJobId = 'harm-auth';
    const delays = [];
    const original = window.setTimeout;
    window.setTimeout = (callback, delay) => { delays.push(delay); return 1; };
    try {
      await pollHarmonizationJob('harm-auth', caseGeneration, 0);
      return {
        error: document.querySelector('#harmonization-error-label').textContent,
        delays,
      };
    } finally {
      window.setTimeout = original;
      MorphicWorkbenchState.activeHarmonizationJobId = null;
    }
  });
  expect(harmonization.error).toContain('Anmeldung');
  expect(harmonization.delays).toEqual([]);
});

test('successful polls clear owned degradation and scan auth pause has explicit retry', async ({ page }) => {
  let scanTransientCalls = 0;
  let harmonizationTransientCalls = 0;
  let scanAuthCalls = 0;
  const runningScan = {
    status: 'running', progress_percent: 10, completed_substeps: [], completed_stage_ids: [],
    current_stage_id: null, stdout_tail: '', stderr_tail: '',
  };
  const runningHarmonization = {
    status: 'running', progress_percent: 10, cycles_completed: 0, total_cycles: 1,
    phase: 'pulse', error_message: null, lease: {},
  };
  await page.route('**/api/scan/jobs/scan-transient', async route => {
    scanTransientCalls += 1;
    await route.fulfill({
      status: scanTransientCalls === 1 ? 503 : 200,
      contentType: 'application/json',
      body: JSON.stringify(scanTransientCalls === 1 ? {detail: 'offline'} : runningScan),
    });
  });
  await page.route('**/api/harmonization/jobs/harm-transient', async route => {
    harmonizationTransientCalls += 1;
    await route.fulfill({
      status: harmonizationTransientCalls === 1 ? 503 : 200,
      contentType: 'application/json',
      body: JSON.stringify(harmonizationTransientCalls === 1 ? {detail: 'offline'} : runningHarmonization),
    });
  });
  await page.route('**/api/scan/jobs/scan-auth-retry', async route => {
    scanAuthCalls += 1;
    await route.fulfill({
      status: scanAuthCalls === 1 ? 401 : 200,
      contentType: 'application/json',
      body: JSON.stringify(scanAuthCalls === 1 ? {detail: 'auth'} : runningScan),
    });
  });
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');

  const recovery = await page.evaluate(async () => {
    const original = window.setTimeout;
    window.setTimeout = () => 1;
    try {
      MorphicWorkbenchState.activeJobId = 'scan-transient';
      await pollScanJob('scan-transient', caseGeneration, 0);
      const scanBad = document.querySelector('#preview-state').textContent;
      await pollScanJob('scan-transient', caseGeneration, 1);
      const scanClear = document.querySelector('#preview-state').textContent;

      MorphicWorkbenchState.activeHarmonizationJobId = 'harm-transient';
      await pollHarmonizationJob('harm-transient', caseGeneration, 0);
      const harmBad = document.querySelector('#preview-state').textContent;
      await pollHarmonizationJob('harm-transient', caseGeneration, 1);
      const harmClear = document.querySelector('#preview-state').textContent;
      return {scanBad, scanClear, harmBad, harmClear};
    } finally {
      window.setTimeout = original;
      MorphicWorkbenchState.activeJobId = null;
      MorphicWorkbenchState.activeHarmonizationJobId = null;
    }
  });
  expect(recovery.scanBad).toContain('nicht erreichbar');
  expect(recovery.scanClear).not.toContain('nicht erreichbar');
  expect(recovery.scanClear).toContain('Scan bei Bedarf manuell stoppen');
  expect(recovery.harmBad).toContain('nicht erreichbar');
  expect(recovery.harmClear).toBe('');

  await page.evaluate(async () => {
    MorphicWorkbenchState.activeJobId = 'scan-auth-retry';
    document.querySelectorAll('.wizard-panel').forEach(node => node.classList.remove('active'));
    document.querySelector('#run-phase').classList.add('active');
    document.querySelector('#job-status-panel').hidden = false;
    await pollScanJob('scan-auth-retry', caseGeneration, 0);
  });
  const retry = page.locator('#scan-refresh-button');
  await expect(retry).toBeVisible();
  await expect(retry).toBeEnabled();
  await page.evaluate(() => {
    const button = document.querySelector('#scan-refresh-button');
    button.click();
    button.click();
  });
  await expect(page.locator('#job-status-label')).toHaveText('laeuft');
  expect(scanAuthCalls).toBe(2);
});


test('scan polling coalesces timers and old completion cannot clear newer generation', async ({ page }) => {
  let sameCalls = 0;
  let newCalls = 0;
  const runningScan = {
    status: 'running', progress_percent: 10, completed_substeps: [], completed_stage_ids: [],
    current_stage_id: null, stdout_tail: '', stderr_tail: '',
  };
  await page.route('**/api/scan/jobs/scan-same', async route => {
    sameCalls += 1;
    await route.fulfill({status: 200, contentType: 'application/json', body: JSON.stringify(runningScan)});
  });
  await page.route('**/api/scan/jobs/scan-old', async route => {
    await new Promise(resolve => setTimeout(resolve, 50));
    await route.fulfill({status: 200, contentType: 'application/json', body: JSON.stringify(runningScan)});
  });
  await page.route('**/api/scan/jobs/scan-new', async route => {
    newCalls += 1;
    await new Promise(resolve => setTimeout(resolve, 200));
    await route.fulfill({status: 200, contentType: 'application/json', body: JSON.stringify(runningScan)});
  });
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');

  const result = await page.evaluate(async () => {
    const originalTimeout = window.setTimeout;
    const delays = [];
    window.setTimeout = (callback, delay) => { delays.push(delay); return 123; };
    try {
      MorphicWorkbenchState.activeJobId = 'scan-same';
      await Promise.all([
        pollScanJob('scan-same', caseGeneration, 0),
        pollScanJob('scan-same', caseGeneration, 0),
      ]);
      const sameDelays = [...delays];
      delays.length = 0;

      MorphicWorkbenchState.activeJobId = 'scan-old';
      const oldGeneration = caseGeneration;
      const oldPromise = pollScanJob('scan-old', oldGeneration, 0);
      caseGeneration += 1;
      MorphicWorkbenchState.activeJobId = 'scan-new';
      const newGeneration = caseGeneration;
      const newPromise = pollScanJob('scan-new', newGeneration, 0);
      await oldPromise;
      const coalescedNewPromise = pollScanJob('scan-new', newGeneration, 0);
      await Promise.all([newPromise, coalescedNewPromise]);
      return {sameDelays, newDelays: delays};
    } finally {
      window.setTimeout = originalTimeout;
      MorphicWorkbenchState.activeJobId = null;
    }
  });

  expect(sameCalls).toBe(1);
  expect(newCalls).toBe(1);
  expect(result.sameDelays).toEqual([2000]);
  expect(result.newDelays).toEqual([2000]);
});


test('old completion cannot overwrite a newer scan in the same case generation', async ({ page }) => {
  const syncGate = createDeferred();
  const syncRequested = createDeferred();
  let oldResultsCalls = 0;
  await page.route('**/api/scan/jobs/scan-old-same-generation', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        status: 'completed', progress_percent: 100, completed_substeps: [],
        completed_stage_ids: [], current_stage_id: null,
      }),
    });
  });
  await page.route('**/api/scan/jobs/scan-old-same-generation/sync-trace', async route => {
    syncRequested.release();
    await syncGate.promise;
    await route.fulfill({status: 200, contentType: 'application/json', body: '{}'});
  });
  await page.route('**/api/scan/jobs/scan-old-same-generation/results', async route => {
    oldResultsCalls += 1;
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({marker: 'old'}),
    });
  });
  try {
    await page.goto('/');
    await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');

    await page.evaluate(() => {
      MorphicWorkbenchState.activeJobId = 'scan-old-same-generation';
      window.__oldSameGenerationPoll = pollScanJob(
        'scan-old-same-generation', caseGeneration, 0
      );
    });
    await syncRequested.promise;
    await page.evaluate(() => {
      MorphicWorkbenchState.activeJobId = 'scan-new-same-generation';
      MorphicWorkbenchState.scanRunActive = true;
      MorphicWorkbenchState.scanResults = {marker: 'new'};
    });
    syncGate.release();
    await page.evaluate(() => window.__oldSameGenerationPoll);

    expect(oldResultsCalls).toBe(0);
    expect(await page.evaluate(() => ({
      activeJobId: MorphicWorkbenchState.activeJobId,
      scanRunActive: MorphicWorkbenchState.scanRunActive,
      scanResults: MorphicWorkbenchState.scanResults,
    }))).toEqual({
      activeJobId: 'scan-new-same-generation',
      scanRunActive: true,
      scanResults: {marker: 'new'},
    });
  } finally {
    syncGate.release();
    syncRequested.release();
    try {
      await clearSyntheticScanRun(page);
    } finally {
      await releaseDeferredRoutes(page, syncGate, syncRequested);
    }
  }
});


test('unresolved scan authority stays reserved until refresh or stop reports stopped', async ({ page }) => {
  const scenarios = [
    {label: 'authority-ambiguous', payload: {status: 'authority_ambiguous'}, action: 'refresh'},
    {label: 'rollback-failed', payload: {status: 'rollback_failed'}, action: 'stop'},
    {label: 'missing', payload: {}, action: 'refresh'},
    {label: 'non-string', payload: {status: 17}, action: 'refresh'},
    {label: 'unknown', payload: {status: 'unknown'}, action: 'stop'},
  ];
  const calls = new Map();
  for (const scenario of scenarios) {
    const jobId = `scan-unresolved-${scenario.label}`;
    calls.set(jobId, {poll: 0, stop: 0, sync: 0, results: 0});
    await page.route(`**/api/scan/jobs/${jobId}`, async route => {
      const current = calls.get(jobId);
      current.poll += 1;
      const body = current.poll === 1 ? scenario.payload : {status: 'stopped'};
      await route.fulfill({contentType: 'application/json', body: JSON.stringify(body)});
    });
    await page.route(`**/api/scan/jobs/${jobId}/stop`, async route => {
      calls.get(jobId).stop += 1;
      await route.fulfill({contentType: 'application/json', body: JSON.stringify({status: 'stopped'})});
    });
    await page.route(`**/api/scan/jobs/${jobId}/sync-trace`, async route => {
      calls.get(jobId).sync += 1;
      await route.fulfill({contentType: 'application/json', body: '{}'});
    });
    await page.route(`**/api/scan/jobs/${jobId}/results`, async route => {
      calls.get(jobId).results += 1;
      await route.fulfill({contentType: 'application/json', body: '{}'});
    });
  }
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');

  for (const scenario of scenarios) {
    const jobId = `scan-unresolved-${scenario.label}`;
    await page.evaluate(async id => {
      document.querySelectorAll('.wizard-panel').forEach(node => node.classList.remove('active'));
      document.querySelector('#run-phase').classList.add('active');
      document.querySelector('#job-status-panel').hidden = false;
      MorphicWorkbenchState.activeJobId = id;
      MorphicWorkbenchState.scanRunActive = true;
      await pollScanJob(id, caseGeneration, 0);
    }, jobId);

    expect(await page.evaluate(() => MorphicWorkbenchState.activeJobId)).toBe(jobId);
    expect(await page.evaluate(() => MorphicWorkbenchState.scanRunActive)).toBe(true);
    await expect(page.locator('#start-analysis-button')).toBeDisabled();
    await expect(page.locator('#scan-refresh-button')).toBeEnabled();
    await expect(page.locator('#scan-stop-button')).toBeVisible();
    await expect(page.locator('#scan-stop-button')).toBeEnabled();
    await expect(page.locator('#preview-state')).toContainText('Status erneut laden');
    await expect(page.locator('#preview-state')).toContainText('manuell stoppen');
    expect(calls.get(jobId).sync).toBe(0);
    expect(calls.get(jobId).results).toBe(0);

    await page.locator(scenario.action === 'stop' ? '#scan-stop-button' : '#scan-refresh-button').click();
    await expect.poll(() => page.evaluate(() => MorphicWorkbenchState.activeJobId)).toBeNull();
    expect(await page.evaluate(() => MorphicWorkbenchState.scanRunActive)).toBe(false);
    await expect(page.locator('#start-analysis-button')).toBeEnabled();
    await expect(page.locator('#scan-refresh-button')).toBeDisabled();
    await expect(page.locator('#scan-stop-button')).toBeDisabled();
    expect(calls.get(jobId).results).toBe(0);
  }
});


test('explicit scan stop retains authority on unresolved response and request failure', async ({ page }) => {
  const jobId = 'scan-unresolved-explicit-stop';
  let stopCalls = 0;
  await page.route(`**/api/scan/jobs/${jobId}`, async route => {
    await route.fulfill({contentType: 'application/json', body: JSON.stringify({status: 'rollback_failed'})});
  });
  await page.route(`**/api/scan/jobs/${jobId}/stop`, async route => {
    stopCalls += 1;
    if (stopCalls === 1) {
      await route.fulfill({contentType: 'application/json', body: JSON.stringify({status: 'rollback_failed'})});
    } else if (stopCalls === 2) {
      await route.abort();
    } else if (stopCalls === 3) {
      await route.fulfill({status: 403, contentType: 'application/json', body: JSON.stringify({detail: 'auth'})});
    } else {
      await route.fulfill({contentType: 'application/json', body: JSON.stringify({status: 'stopped'})});
    }
  });
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  await page.evaluate(async id => {
    document.querySelectorAll('.wizard-panel').forEach(node => node.classList.remove('active'));
    document.querySelector('#run-phase').classList.add('active');
    document.querySelector('#job-status-panel').hidden = false;
    MorphicWorkbenchState.activeJobId = id;
    MorphicWorkbenchState.scanRunActive = true;
    await pollScanJob(id, caseGeneration, 0);
  }, jobId);

  await page.locator('#scan-stop-button').click();
  await expect.poll(() => stopCalls).toBe(1);
  expect(await page.evaluate(() => MorphicWorkbenchState.activeJobId)).toBe(jobId);
  expect(await page.evaluate(() => MorphicWorkbenchState.scanRunActive)).toBe(true);
  await expect(page.locator('#scan-stop-button')).toBeEnabled();

  await page.locator('#scan-stop-button').click();
  await expect.poll(() => stopCalls).toBe(2);
  expect(await page.evaluate(() => MorphicWorkbenchState.activeJobId)).toBe(jobId);
  expect(await page.evaluate(() => MorphicWorkbenchState.scanRunActive)).toBe(true);
  await expect(page.locator('#start-analysis-button')).toBeDisabled();
  await expect(page.locator('#scan-stop-button')).toBeEnabled();

  await page.locator('#scan-stop-button').click();
  await expect.poll(() => stopCalls).toBe(3);
  expect(await page.evaluate(() => MorphicWorkbenchState.activeJobId)).toBe(jobId);
  expect(await page.evaluate(() => MorphicWorkbenchState.scanRunActive)).toBe(true);
  await expect(page.locator('#job-status-label')).toContainText('Anmeldung erforderlich');
  await expect(page.locator('#scan-stop-button')).toBeEnabled();

  await page.locator('#scan-stop-button').click();
  await expect.poll(() => page.evaluate(() => MorphicWorkbenchState.activeJobId)).toBeNull();
  expect(await page.evaluate(() => MorphicWorkbenchState.scanRunActive)).toBe(false);
});


test('harmonization progress exposes and resets accessible value', async ({ page }) => {
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  const progress = page.locator('#harmonization-progress');
  await expect(progress).toHaveAttribute('role', 'progressbar');
  await expect(progress).toHaveAttribute('aria-valuemin', '0');
  await expect(progress).toHaveAttribute('aria-valuemax', '100');
  await page.evaluate(() => {
    document.querySelector('#harmonization-progress').setAttribute('aria-valuenow', '67');
    document.querySelector('#harmonization-progress-fill').style.width = '67%';
  });
  expect(await page.evaluate(() => resetWorkbenchForNewCase())).toBe(true);
  await expect(progress).toHaveAttribute('aria-valuenow', '0');
  expect(await page.locator('#harmonization-progress-fill').evaluate(node => node.style.width)).toBe('0%');
});

test('optionale Funktionen haben verknuepfte Erklaerungen', async ({ page }) => {
  const errors = captureErrors(page);
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');

  for (const selector of [
    '#focus-history-consent',
    '[name="main_symptom"]',
    '#image-file-input',
    '[name="adaptive_limits"]',
    '#workbench-mode',
    '[name="duration_factor"]',
    '#template-sensitive-consent',
  ]) {
    const control = page.locator(selector);
    const describedBy = await control.getAttribute('aria-describedby');
    const ids = String(describedBy || '').split(/\s+/).filter(Boolean);
    expect(ids.length, selector).toBeGreaterThan(0);
    for (const id of ids) {
      await expect(page.locator(`#${id}`)).toContainText('Standard:');
    }
  }

  await page.evaluate(() => MorphicWorkbenchRender.showStep(3));
  const profile = page.locator('#profile-template-choices [data-value="phase1-default"]');
  const entropy = page.locator('#entropy-mode-choices [data-value="legacy"]');
  await expect(profile).toHaveAccessibleName('Phase-1 Standard');
  await expect(profile).toHaveAccessibleDescription(/Standard:/);
  await expect(entropy).toHaveAccessibleName('Legacy');
  await expect(entropy).toHaveAccessibleDescription(/Standard:/);

  await page.evaluate(() => MorphicWorkbenchRender.showStep(9));
  const solfeggio = page.locator('#solfeggio-base-choices [data-value="432"]');
  await expect(solfeggio).toHaveAccessibleName('432 Hz');
  await expect(solfeggio).toHaveAccessibleDescription(/Standard:/);

  await page.setViewportSize({width: 375, height: 812});
  expect(await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth
  )).toBe(false);
  expect(errors).toEqual([]);
});

test('choice cards behalten Tastaturfokus und Frequenzwahrheit', async ({ page }) => {
  const errors = captureErrors(page);
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');

  await page.evaluate(() => MorphicWorkbenchRender.showStep(3));
  const profile = page.locator('#profile-template-choices [data-value="phase1-default"]');
  await profile.focus();
  await profile.press('Space');
  expect(await page.evaluate(() => document.activeElement?.dataset?.value)).toBe('phase1-default');
  await profile.press('Enter');
  expect(await page.evaluate(() => document.activeElement?.dataset?.value)).toBe('phase1-default');

  await page.evaluate(() => MorphicWorkbenchRender.showStep(9));
  const frequency = page.locator('#harmonization-form [name="target_frequency"]');
  await page.locator('#solfeggio-base-choices [data-value="498.90"]').click();
  await expect(frequency).toHaveValue('498.90');
  await expect(page.locator('#solfeggio-base-choices [aria-checked="true"]')).toHaveAttribute('data-value', '498.90');
  await frequency.fill('437.5');
  await expect(page.locator('#solfeggio-base-choices [aria-checked="true"]')).toHaveCount(0);
  await expect(page.locator('#solfeggio-base-choices [data-value="432"]')).toHaveAttribute('tabindex', '0');
  await page.locator('#solfeggio-base-choices [data-value="432"]').focus();
  expect(await page.evaluate(() => document.activeElement?.dataset?.value)).toBe('432');
  await frequency.fill('432');
  await expect(page.locator('#solfeggio-base-choices [aria-checked="true"]')).toHaveAttribute('data-value', '432');
  expect(errors).toEqual([]);
});

test('441 Minuten erfordern eine ausdrueckliche Bestaetigung', async ({ page }) => {
  const errors = captureErrors(page);
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  await prepareSyntheticHarmonizationStart(page, {
    report_id: 'gate1-report',
    workbench_mode: 'standard',
  });
  await page.evaluate(() => {
    MorphicWorkbenchRender.showStep(9);
    window.__harmonizationStarts = 0;
    MorphicWorkbenchApi.startHarmonization = async () => {
      window.__harmonizationStarts += 1;
      return {job_id: 'gate1-duration'};
    };
    MorphicWorkbenchApi.pollHarmonization = async () => ({
      status: 'completed',
      progress_percent: 100,
      cycles_completed: 1,
      total_cycles: 1,
    });
    document.querySelector('[name="duration_factor"]').value = '21';
  });

  await page.locator('#harmonization-start-button').click();
  expect(await page.evaluate(() => window.__harmonizationStarts)).toBe(0);
  await expect(page.locator('#harmonization-confirmation-state')).toContainText('441 Minuten');

  await page.locator('[name="duration_factor"]').fill('20');
  await expect(page.locator('#harmonization-confirmation-state')).toBeEmpty();
  await page.locator('[name="duration_factor"]').fill('21');
  await page.locator('#harmonization-start-button').click();
  expect(await page.evaluate(() => window.__harmonizationStarts)).toBe(0);
  await page.locator('#harmonization-max-duration-confirmation').check();
  await expect(page.locator('#harmonization-confirmation-state')).toBeEmpty();
  await page.locator('#harmonization-start-button').click();
  await expect.poll(() => page.evaluate(() => window.__harmonizationStarts)).toBe(1);
  expect(errors).toEqual([]);
});

test('mobile optional disclosure has no horizontal overflow', async ({ page }) => {
  const errors = captureErrors(page);
  await page.setViewportSize({width: 375, height: 812});
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  await page.locator('#btn-next').click();
  const disclosure = page.locator('details.optional-group-workflow');
  await expect(disclosure).not.toHaveAttribute('open', '');
  await disclosure.locator('summary').click();
  await expect(disclosure).toHaveAttribute('open', '');
  expect(await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth)).toBe(false);
  expect(errors).toEqual([]);
});

test('workflow stepping is CSP-safe, aligned and interactive', async ({ page }) => {
  const errors = captureErrors(page);
  await page.goto('/workflow-stepping');
  await expect(page.locator('.workflow-step')).toHaveCount(12);
  await page.locator('.workflow-step').nth(11).click();
  await expect(page.locator('#workflow-panel-12')).toHaveClass(/active/);
  await expect(page.locator('#workflow-progress-label')).toHaveText('12 / 12');
  await page.locator('.workflow-step').nth(11).press('Home');
  await expect(page.locator('#workflow-panel-1')).toHaveClass(/active/);
  expect(errors).toEqual([]);
});

test('Gate 5 EMF authority confirms mutations, source truth and responsive fallback', async ({ page }) => {
  const errors = captureErrors(page);
  const requests = [];
  const emfMutationPosts = [];
  let authoritativeActive = false;
  let pendingStatusActive = null;
  let enableAttempts = 0;
  let hardwareVariant = 'valid';
  let blockNextStatusConfirmation = false;
  const firstEnableStatusStarted = createDeferred();
  const firstEnableStatusGate = createDeferred();

  const statusPayload = value => ({
    active: value,
    activation_policy: 'until_manually_disabled',
    measurement_label: 'System-/Entropie-basierter EMF-Proxy-Index',
  });
  const components = {
    entropy: {
      id: 'entropy',
      label: 'Deterministische Entropiequelle',
      status: 'software_fallback',
      note: 'Isolierter Browser-Fallback.',
    },
  };
  const activeCalibration = () => ({
    status: 'active',
    emf_index: hardwareVariant === 'valid' ? 0.42 : 'ungueltig',
    entropy_score: 0.73,
    timing_jitter_ms: 0.18,
    system_load: 0.61,
    sensor_entropy: 0.5,
    source_health: {
      rng: 'ok',
      cpu_timing: 'partial',
      system_load: 'unknown',
      sensor_entropy: 'fallback',
    },
    replay: {algorithm: 'emf-profile-v2', sensor_source: 'fallback'},
  });
  const hardwarePayload = () => ({
    mode: 'standard',
    profile: 'isolated-browser',
    components,
    realtime_calibration: authoritativeActive
      ? activeCalibration()
      : {
        status: 'disabled',
        sensor_entropy: null,
        source_health: {
          rng: 'disabled',
          cpu_timing: 'disabled',
          system_load: 'disabled',
          sensor_entropy: 'disabled',
        },
        replay: {algorithm: 'emf-profile-v2', sensor_source: 'disabled'},
      },
    gate_warnings: [],
  });
  const record = request => {
    requests.push(`${request.method()} ${new URL(request.url()).pathname}`);
  };
  const storageSnapshot = () => page.evaluate(() => ({
    local: Object.keys(localStorage).sort().map(key => [key, localStorage.getItem(key)]),
    session: Object.keys(sessionStorage).sort().map(key => [key, sessionStorage.getItem(key)]),
  }));

  await page.addInitScript(() => {
    const writes = [];
    Object.defineProperty(window, '__gate5StorageWrites', {
      configurable: false,
      value: writes,
    });
    const originalSetItem = Storage.prototype.setItem;
    Storage.prototype.setItem = function setItem(key, value) {
      const storage = this === window.localStorage
        ? 'localStorage'
        : this === window.sessionStorage
          ? 'sessionStorage'
          : 'unknown';
      writes.push({storage, key: String(key), value: String(value)});
      return originalSetItem.call(this, key, value);
    };
  });
  page.on('request', request => {
    if (request.method() !== 'POST') return;
    const url = new URL(request.url());
    if (!/^\/api\/(?:v1\/)?emf\/(?:enable|disable)$/.test(url.pathname)) return;
    emfMutationPosts.push(`POST ${url.pathname}${url.search}`);
  });

  await page.route('**/api/emf/status', async route => {
    record(route.request());
    if (blockNextStatusConfirmation) {
      blockNextStatusConfirmation = false;
      firstEnableStatusStarted.release();
      await firstEnableStatusGate.promise;
    }
    if (typeof pendingStatusActive === 'boolean') {
      authoritativeActive = pendingStatusActive;
      pendingStatusActive = null;
    }
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify(statusPayload(authoritativeActive)),
    });
  });
  await page.route(/\/api\/emf\/enable(?:\?.*)?$/, async route => {
    record(route.request());
    enableAttempts += 1;
    pendingStatusActive = enableAttempts === 2;
    await route.fulfill({
      contentType: 'application/json',
      // Both responses contradict their confirming GET to prove GET ownership.
      body: JSON.stringify(statusPayload(enableAttempts === 1)),
    });
  });
  await page.route(/\/api\/emf\/disable(?:\?.*)?$/, async route => {
    record(route.request());
    pendingStatusActive = false;
    await route.fulfill({
      contentType: 'application/json',
      // The confirming status read, not this mutation body, owns the controls.
      body: JSON.stringify(statusPayload(true)),
    });
  });
  await page.route(/\/api\/v1\/emf\/(?:enable|disable)(?:\?.*)?$/, async route => {
    record(route.request());
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify(statusPayload(authoritativeActive)),
    });
  });
  await page.route('**/api/workbench/hardware?*', async route => {
    record(route.request());
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify(hardwarePayload()),
    });
  });

  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  await expect.poll(() => requests.filter(entry => entry === 'GET /api/emf/status').length).toBe(1);
  await expect.poll(() => requests.filter(entry => entry === 'GET /api/workbench/hardware').length).toBe(1);
  expect(requests.filter(entry => entry.startsWith('POST '))).toEqual([]);
  expect(emfMutationPosts).toEqual([]);
  await expect(page.locator('#emf-telemetry-state')).toHaveText('EMF-Telemetrie deaktiviert.');

  await page.locator('#btn-next').click();
  await page.locator('[name="last_name"]').fill('Browser');
  await page.locator('[name="first_name"]').fill('Gate Five');
  await page.locator('[name="birth_date"]').fill('09041966');
  await page.locator('[name="birth_place"]').fill('Augsburg');
  await page.locator('#consent-local').check();
  await page.locator('#consent-safety').check();
  await page.locator('#btn-next').click();
  await page.locator('[name="focus"]').fill('EMF authority');
  await page.locator('[name="main_symptom"]').fill('Source truth');
  await page.locator('#btn-next').click();
  await page.locator('#btn-next').click();
  await expect(page.locator('.wizard-step.active')).toContainText('Hardware & Realtime');

  const enableButton = page.locator('#emf-enable-button');
  const disableButton = page.locator('#emf-disable-button');
  await expect(enableButton).toBeEnabled();
  await expect(disableButton).toBeDisabled();
  const storageBeforeActivation = await storageSnapshot();

  const firstEnableHardwareBaseline = requests.filter(
    entry => entry === 'GET /api/workbench/hardware'
  ).length;
  blockNextStatusConfirmation = true;
  await enableButton.click();
  await firstEnableStatusStarted.promise;
  const firstEnableHardwareCountWhileBlocked = requests.filter(
    entry => entry === 'GET /api/workbench/hardware'
  ).length;
  expect(firstEnableHardwareCountWhileBlocked).toBe(firstEnableHardwareBaseline);
  try {
    await page.evaluate(() => new Promise(resolve => {
      requestAnimationFrame(() => requestAnimationFrame(resolve));
    }));
    expect(requests.filter(
      entry => entry === 'GET /api/workbench/hardware'
    )).toHaveLength(firstEnableHardwareCountWhileBlocked);
  } finally {
    firstEnableStatusGate.release();
  }
  await expect.poll(() => requests.filter(
    entry => entry === 'GET /api/workbench/hardware'
  ).length).toBe(firstEnableHardwareBaseline + 1);
  await expect(page.locator('#emf-telemetry-state')).toHaveText('EMF-Telemetrie deaktiviert.');
  await expect(enableButton).toBeEnabled();
  await expect(disableButton).toBeDisabled();
  await expect(page.locator('.emf-index-gauge')).toHaveCount(0);
  await expect(page.locator('.emf-index-value')).toHaveText('--');
  await expect(page.locator('.emf-source-row')).toHaveCount(0);

  const firstEnableStart = requests.indexOf('POST /api/emf/enable');
  expect(firstEnableStart).toBeGreaterThan(-1);
  expect(requests.slice(firstEnableStart, firstEnableStart + 3)).toEqual([
    'POST /api/emf/enable',
    'GET /api/emf/status',
    'GET /api/workbench/hardware',
  ]);

  await enableButton.click();
  const telemetryState = page.locator('#emf-telemetry-state');
  const aggregateLabel = page.locator('.emf-index-label');
  const aggregateValue = page.locator('.emf-index-value');
  const aggregateDisclosure = page.locator('.emf-index-derived');
  const sourceRows = page.locator('.emf-source-row');
  await expect(telemetryState).toBeVisible();
  await expect(telemetryState).toContainText('aktiv bis manuell deaktiviert');
  await expect(enableButton).toBeDisabled();
  await expect(disableButton).toBeEnabled();
  await expect(aggregateLabel).toBeVisible();
  await expect(aggregateLabel).toHaveText(
    'System-/Entropie-basierter EMF-Proxy-Index'
  );
  await expect(aggregateDisclosure).toBeVisible();
  await expect(aggregateDisclosure).toHaveText(
    'Abgeleiteter System-/Entropie-Proxy; keine physische Feldmessung.'
  );
  await expect(aggregateValue).toBeVisible();
  await expect(aggregateValue).toHaveText('0,42');
  await expect(page.locator('.emf-index-gauge')).toHaveCount(1);
  await expect(sourceRows).toHaveCount(4);
  for (let index = 0; index < 4; index += 1) {
    const row = sourceRows.nth(index);
    await expect(row).toBeVisible();
    await expect(row.locator('.emf-source-key')).toBeVisible();
    await expect(row.locator('.emf-source-status')).toBeVisible();
  }
  expect(await page.locator('.emf-source-key').allTextContents()).toEqual([
    'rng', 'cpu_timing', 'system_load', 'sensor_entropy',
  ]);
  expect(await page.locator('.emf-source-status').allTextContents()).toEqual([
    'ok', 'partial', 'unknown', 'fallback',
  ]);
  const fallbackSource = page.locator('.emf-source-row').filter({hasText: 'sensor_entropy'});
  await expect(fallbackSource.locator('.emf-source-value')).toBeVisible();
  await expect(fallbackSource.locator('.emf-source-value')).toHaveText('0,5');
  await expect(fallbackSource.locator('.emf-source-status')).toBeVisible();
  await expect(fallbackSource.locator('.emf-source-status')).toHaveText('fallback');

  const secondEnableStart = requests.indexOf('POST /api/emf/enable', firstEnableStart + 1);
  expect(secondEnableStart).toBeGreaterThan(firstEnableStart);
  expect(requests.slice(secondEnableStart, secondEnableStart + 3)).toEqual([
    'POST /api/emf/enable',
    'GET /api/emf/status',
    'GET /api/workbench/hardware',
  ]);

  hardwareVariant = 'invalid';
  await page.locator('#workbench-mode').selectOption('expert');
  await expect(page.locator('.emf-index-gauge')).toHaveCount(0);
  await expect(page.locator('.emf-index-value')).toHaveText('--');
  await expect(page.locator('.emf-index-value')).not.toHaveText('0');

  await page.setViewportSize({width: 375, height: 812});
  const mobileLayout = await page.evaluate(() => {
    const documentElement = document.documentElement;
    const cards = Array.from(document.querySelectorAll(
      '.emf-control-card, .emf-index-card, .hardware-card, .emf-source-row'
    )).map(node => {
      const rect = node.getBoundingClientRect();
      return {left: rect.left, right: rect.right, width: rect.width};
    });
    const sourceRows = Array.from(document.querySelectorAll('.emf-source-row')).map(row => (
      Array.from(row.children).map(child => {
        const rect = child.getBoundingClientRect();
        return rect.top + rect.height / 2;
      })
    ));
    return {
      clientWidth: documentElement.clientWidth,
      scrollWidth: documentElement.scrollWidth,
      cards,
      sourceRows,
    };
  });
  expect(mobileLayout.scrollWidth).toBe(mobileLayout.clientWidth);
  for (const card of mobileLayout.cards) {
    expect(card.left).toBeGreaterThanOrEqual(-1);
    expect(card.right).toBeLessThanOrEqual(mobileLayout.clientWidth + 1);
    expect(card.width).toBeLessThanOrEqual(mobileLayout.clientWidth + 1);
  }
  expect(mobileLayout.sourceRows).toHaveLength(4);
  for (const centers of mobileLayout.sourceRows) {
    expect(centers).toHaveLength(4);
    expect(Math.abs(centers[0] - centers[1])).toBeLessThanOrEqual(1);
    expect(Math.abs(centers[2] - centers[3])).toBeLessThanOrEqual(1);
    expect(centers[2]).toBeGreaterThan(centers[0]);
  }

  await disableButton.click();
  await expect(page.locator('#emf-telemetry-state')).toHaveText('EMF-Telemetrie deaktiviert.');
  await expect(enableButton).toBeEnabled();
  await expect(disableButton).toBeDisabled();
  await expect(page.locator('.emf-index-gauge')).toHaveCount(0);
  await expect(page.locator('.emf-index-value')).toHaveText('--');
  await expect(page.locator('.emf-index-value')).not.toHaveText('0');
  await expect(page.locator('.emf-source-row')).toHaveCount(0);

  const disableStart = requests.indexOf('POST /api/emf/disable');
  expect(disableStart).toBeGreaterThan(secondEnableStart);
  expect(requests.slice(disableStart, disableStart + 3)).toEqual([
    'POST /api/emf/disable',
    'GET /api/emf/status',
    'GET /api/workbench/hardware',
  ]);

  const modernResponse = await page.request.get('/api/emf/status');
  const legacyResponse = await page.request.get('/api/v1/emf/status');
  const modernAfterLegacyResponse = await page.request.get('/api/emf/status');
  expect(modernResponse.ok()).toBe(true);
  expect(legacyResponse.ok()).toBe(true);
  expect(modernAfterLegacyResponse.ok()).toBe(true);
  const modernStatus = await modernResponse.json();
  const legacyStatus = await legacyResponse.json();
  const modernAfterLegacyStatus = await modernAfterLegacyResponse.json();
  expect(legacyStatus).toEqual(modernStatus);
  expect(modernStatus).toEqual(statusPayload(false));
  expect(modernAfterLegacyStatus).toEqual(statusPayload(false));
  expect(emfMutationPosts).toEqual([
    'POST /api/emf/enable',
    'POST /api/emf/enable',
    'POST /api/emf/disable',
  ]);
  const storageWrites = await page.evaluate(() => window.__gate5StorageWrites);
  expect(storageWrites.filter(({key, value}) => (
    /emf|telemetr|activation|active|aktiv/i.test(`${key}\n${value}`)
  ))).toEqual([]);
  expect(await storageSnapshot()).toEqual(storageBeforeActivation);
  expect(errors).toEqual([]);
});

test('Gate 5 EMF timeout reconciliation keeps opposite status fenced until intent appears', async ({ page }) => {
  const errors = captureErrors(page);
  const requests = [];
  let authoritativeActive = false;
  let mutationStarted = false;
  let timeoutStatusReads = 0;
  let hardwareReads = 0;
  const firstTimeoutStatusStarted = createDeferred();
  const firstTimeoutStatusGate = createDeferred();

  await page.addInitScript(() => {
    window.MORPHIC_EMF_MUTATION_TIMEOUT_MS = 25;
  });
  await page.route('**/api/emf/status', async route => {
    requests.push('GET status');
    const observedActive = authoritativeActive;
    if (mutationStarted) {
      timeoutStatusReads += 1;
      if (timeoutStatusReads === 1) {
        firstTimeoutStatusStarted.release();
        await firstTimeoutStatusGate.promise;
      }
    }
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({active: observedActive}),
    });
  });
  await page.route(/\/api\/emf\/enable(?:\?.*)?$/, async route => {
    requests.push('POST enable');
    mutationStarted = true;
    await new Promise(resolve => setTimeout(resolve, 60));
    authoritativeActive = true;
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({active: true}),
    }).catch(() => {});
  });
  await page.route('**/api/workbench/hardware?*', async route => {
    requests.push('GET hardware');
    hardwareReads += 1;
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({components: {}, gate_warnings: []}),
    });
  });

  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.workbenchReady === 'true');
  await expect(page.locator('#emf-telemetry-state')).toHaveText('EMF-Telemetrie deaktiviert.');
  const hardwareBaseline = hardwareReads;
  await page.evaluate(() => {
    window.__gate5TimeoutOperation = setEmfTelemetryEnabled(true, caseGeneration);
  });
  await firstTimeoutStatusStarted.promise;
  const oppositeSnapshot = await page.evaluate(() => ({
    active: MorphicWorkbenchState.emfTelemetryActive,
    pending: MorphicWorkbenchState.emfTelemetryMutationPending,
    unresolved: MorphicWorkbenchState.emfTelemetryMutationUnresolved,
    enableDisabled: document.querySelector('#emf-enable-button').disabled,
    disableDisabled: document.querySelector('#emf-disable-button').disabled,
    newCaseDisabled: document.querySelector('#new-case-button').disabled,
  }));
  const hardwareReadsWhileOpposite = hardwareReads;
  firstTimeoutStatusGate.release();
  const operationResult = await page.evaluate(() => window.__gate5TimeoutOperation);
  expect(oppositeSnapshot).toEqual({
    active: false,
    pending: true,
    unresolved: true,
    enableDisabled: true,
    disableDisabled: true,
    newCaseDisabled: true,
  });
  expect(hardwareReadsWhileOpposite).toBe(hardwareBaseline);
  expect(hardwareReads).toBe(hardwareBaseline + 1);

  await expect(page.locator('#emf-telemetry-state')).toContainText('aktiv bis manuell deaktiviert');
  await expect.poll(() => hardwareReads).toBe(hardwareBaseline + 1);
  expect(operationResult).toBe(false);
  expect(await page.evaluate(() => ({
    active: MorphicWorkbenchState.emfTelemetryActive,
    pending: MorphicWorkbenchState.emfTelemetryMutationPending,
    unresolved: MorphicWorkbenchState.emfTelemetryMutationUnresolved,
    newCaseDisabled: document.querySelector('#new-case-button').disabled,
  }))).toEqual({active: true, pending: false, unresolved: false, newCaseDisabled: false});
  const mutationStart = requests.indexOf('POST enable');
  expect(requests.slice(mutationStart)).toEqual([
    'POST enable',
    'GET status',
    'GET status',
    'GET hardware',
  ]);
  expect(errors).toEqual([
    expect.stringMatching(/^request: .*\/api\/emf\/enable net::ERR_ABORTED$/),
  ]);
});

test('EMF monitor executes under CSP and renders a synthetic WebSocket update safely', async ({ page }) => {
  const errors = captureErrors(page);
  await page.addInitScript(() => {
    class SyntheticWebSocket {
      constructor(url) {
        this.url = url;
        window.__syntheticEmfSocket = this;
      }
      close() {}
    }
    window.WebSocket = SyntheticWebSocket;
  });
  await page.goto('/api/emf/monitor');
  await page.waitForFunction(() => Boolean(window.__syntheticEmfSocket));
  await page.evaluate(() => {
    window.__syntheticEmfSocket.onmessage({data: '{'});
  });
  await expect(page.locator('#connectionState')).toHaveText('Ungültige Messantwort verworfen');
  await page.evaluate(() => {
    window.__syntheticEmfSocket.onmessage({
      data: JSON.stringify({
        emf_index: 0.45678,
        entropy_score: 0.23456,
        timing_jitter_ms: 1.234,
        system_load: 0.34567,
        sensor_entropy: 0.5,
        source_health: {
          rng: 'ok',
          cpu_timing: 'partial',
          system_load: 'ok',
          sensor_entropy: 'fallback',
        },
        recommendation: '<img src=x onerror=alert(1)>',
        counter_frequencies: [432.04, 528.06],
      }),
    });
  });

  await expect(page.locator('#emf')).toHaveText('0.457');
  await expect(page.locator('#connectionState')).toHaveText('Verbunden');
  await expect(page.locator('#ent')).toHaveText('0.235');
  await expect(page.locator('#jit')).toHaveText('1.23');
  await expect(page.locator('#load')).toHaveText('0.346');
  await expect(page.locator('#sensor')).toHaveText('0.500');
  expect(await page.locator('.monitor-source-key').allTextContents()).toEqual([
    'rng', 'cpu_timing', 'system_load', 'sensor_entropy',
  ]);
  expect(await page.locator('.monitor-source-status').allTextContents()).toEqual([
    'ok', 'partial', 'ok', 'fallback',
  ]);
  await expect(page.locator('#entStatus')).toHaveClass(/status-ok/);
  await expect(page.locator('#jitStatus')).toHaveClass(/status-partial/);
  await expect(page.locator('#loadStatus')).toHaveClass(/status-ok/);
  await expect(page.locator('#sensorStatus')).toHaveClass(/status-fallback/);
  await expect(page.locator('#rec')).toHaveText('<img src=x onerror=alert(1)>');
  await expect(page.locator('#rec img')).toHaveCount(0);
  await expect(page.locator('#freq')).toHaveText('432.0 Hz, 528.1 Hz');
  await expect(page.locator('#emfBar')).toHaveJSProperty('value', 0.45678);
  await expect(page.locator('#emfBar')).toBeVisible();

  await page.evaluate(() => {
    window.__syntheticEmfSocket.onmessage({
      data: JSON.stringify({
        emf_index: 'ungueltig',
        entropy_score: null,
        timing_jitter_ms: 1.234,
        system_load: 0.34567,
        sensor_entropy: 0.5,
        source_health: {rng: 'partial', cpu_timing: 'healthy'},
      }),
    });
  });
  await expect(page.locator('#emf')).toHaveText('--');
  await expect(page.locator('#emfBar')).toBeHidden();
  await expect(page.locator('#emfBar')).not.toHaveAttribute('value');
  await expect(page.locator('#ent')).toHaveText('--');
  await expect(page.locator('#entStatus')).toHaveText('partial');
  await expect(page.locator('#jitStatus')).toHaveText('unknown');
  await expect(page.locator('#loadStatus')).toHaveText('unknown');
  await expect(page.locator('#sensorStatus')).toHaveText('unknown');

  await page.setViewportSize({width: 375, height: 812});
  expect(await page.evaluate(
    () => document.documentElement.scrollWidth === document.documentElement.clientWidth
  )).toBe(true);
  expect(errors).toEqual([]);
});
