import { personalRequest, personalPage } from '../personal-selection.js';

const LABELS = {
  queued: 'wartend',
  running: 'in Berechnung',
  completed: 'abgeschlossen',
  cancelled: 'abgebrochen',
  interrupted: 'nach Neustart unterbrochen',
  failed: 'fehlgeschlagen',
};
const ACTIVE_STATUSES = new Set(['queued', 'running']);

export function initPersonalAnalysis(api, eventBus, procedureSelect) {
  const status = document.getElementById('personal-analysis-status');
  const proof = document.getElementById('personal-analysis-proof');
  const result = document.getElementById('personal-result-body');
  const pager = document.getElementById('personal-pager');
  const history = document.getElementById('personal-history');
  const cancel = document.getElementById('personal-cancel');

  let current = null;
  let page = 1;
  let epoch = 0;
  let displayRevision = 0;
  let timer = null;
  let timerJobId = null;
  let activeJobId = null;
  let pending = null;
  let pendingDisplayRevision = null;
  let submissionInFlight = false;
  const jobsById = new Map();
  const pollsInFlight = new Set();
  const resumeAfterPoll = new Set();

  const selection = () => window.__RADIWORKS_CASE_BINDING__;
  const isActive = (job) => Boolean(job && ACTIVE_STATUSES.has(job.status));
  const activeJobs = () => [...jobsById.values()].filter(isActive);
  const node = (tag, text) => {
    const element = document.createElement(tag);
    element.textContent = text;
    return element;
  };

  function mergeJob(job) {
    if (!job?.id) return null;
    const existing = jobsById.get(job.id);
    if (!existing) {
      jobsById.set(job.id, job);
      return job;
    }

    // A job is immutable after it reaches a terminal state; stale list or poll
    // responses must never put it back into the active queue.
    if (!isActive(existing) && isActive(job)) return existing;
    const existingTime = Date.parse(existing.updatedAt || '') || 0;
    const incomingTime = Date.parse(job.updatedAt || '') || 0;
    if (incomingTime < existingTime) return existing;
    if (incomingTime === existingTime) {
      if (!isActive(existing) && isActive(job)) return existing;
      if ((job.completedRates || 0) < (existing.completedRates || 0)) return existing;
      if ((job.completedRates || 0) === (existing.completedRates || 0)) {
        const rank = { queued: 0, running: 1, completed: 2, cancelled: 2, interrupted: 2, failed: 2 };
        if ((rank[job.status] || 0) < (rank[existing.status] || 0)) return existing;
      }
    }
    jobsById.set(job.id, job);
    return job;
  }

  function syncActiveJob() {
    const active = activeJobs();
    if (activeJobId && active.some((job) => job.id === activeJobId)) return activeJobId;
    activeJobId = active[0]?.id || null;
    return activeJobId;
  }

  function clearTimer() {
    if (timer !== null) clearTimeout(timer);
    timer = null;
    timerJobId = null;
  }

  function schedulePoll(identifier, token, delay = 1500) {
    if (token !== epoch || !identifier || !isActive(jobsById.get(identifier))) return;
    const key = token + ':' + identifier;
    if (pollsInFlight.has(key)) {
      resumeAfterPoll.add(key);
      return;
    }
    if (timer !== null && timerJobId === identifier) return;
    clearTimer();
    timerJobId = identifier;
    timer = setTimeout(() => {
      timer = null;
      timerJobId = null;
      void poll(identifier, token);
    }, delay);
  }

  function render(job) {
    current = job;
    result.replaceChildren();
    pager.replaceChildren();
    cancel.hidden = !isActive(job);
    const progressHint = isActive(job)
      ? ' Auswahl oben gilt für den nächsten Auftrag. Die vollständige sortierte Ergebnisliste erscheint erst nach Abschluss; große Datenbanken können mehrere Minuten benötigen.'
      : '';
    status.textContent =
      'Persönlicher Auftrag ' + job.id.slice(0, 8) + ': ' + (LABELS[job.status] || job.status) +
      ' · ' + job.completedRates + '/' + job.totalRates + ' Raten.' +
      (job.error ? ' Fehler: ' + job.error : '') + progressHint;
    proof.textContent =
      api.catalogLabel(job.catalog.name) + ' · ' +
      (job.mode === 'seeded' ? 'reproduzierbar, Seed ' + job.seed : 'stochastisch') +
      ' · Quellen: ' + job.entropy.sources.join(', ') + ' · Kontextversion ' +
      job.contextVersion + ' · ' + job.procedure + '. Der Kontext dieses Auftrags bleibt unverändert.';

    const shown = personalPage(job, page);
    for (let i = 0; i < shown.length; i++) {
      const row = shown[i];
      const tr = document.createElement('tr');
      tr.append(
        node('td', String((page - 1) * 21 + i + 1)),
        node('td', row.rate),
        node('td', row.score.toFixed(6)),
        node('td', row.intensity.toFixed(4)),
      );
      const td = document.createElement('td');
      const button = node('button', 'Broadcast');
      button.type = 'button';
      button.className = 'btn';
      button.setAttribute('aria-label', 'Broadcast für persönliche Rate ' + ((page - 1) * 21 + i + 1));
      button.addEventListener('click', async () => {
        button.disabled = true;
        try {
          await api.broadcast({
            signature: row.rate,
            seconds: 60,
            multiplier: 1,
            source_personal_job_id: job.id,
            source_personal_input_index: row.inputIndex,
          });
          document.querySelector('.tab[data-tab="broadcast"]').click();
        } catch (error) {
          if (current?.id === job.id) status.textContent = 'Persönlicher Broadcast abgelehnt: ' + error.message;
        } finally {
          button.disabled = false;
        }
      });
      td.append(button);
      tr.append(td);
      result.append(tr);
    }

    if (job.status === 'completed') {
      for (let number = 1; number <= Math.ceil(job.rows.length / 21); number++) {
        const button = node('button', String(number));
        button.type = 'button';
        button.className = 'btn';
        button.setAttribute('aria-label', 'Persönliche Ergebnisseite ' + number);
        button.setAttribute('aria-current', number === page ? 'page' : 'false');
        button.addEventListener('click', () => {
          page = number;
          render(jobsById.get(job.id) || job);
        });
        pager.append(button);
      }
    }
  }

  function renderHistory(jobs) {
    history.replaceChildren();
    for (const snapshot of jobs) {
      const jobId = snapshot.id;
      const job = jobsById.get(jobId) || snapshot;
      const createdAt = (job.createdAt || '').slice(0, 19).replace('T', ' ');
      const button = node(
        'button',
        createdAt + ' · ' + (LABELS[job.status] || job.status) + ' · ' + api.catalogLabel(job.catalog.name),
      );
      button.type = 'button';
      button.className = 'btn';
      button.addEventListener('click', () => {
        const selected = jobsById.get(jobId) || snapshot;
        displayRevision++;
        page = 1;
        render(selected);
        const activeId = syncActiveJob();
        if (activeId) schedulePoll(activeId, epoch);
      });
      history.append(button);
    }
  }

  async function poll(identifier, token) {
    const ref = selection()?.ref;
    if (!ref || token !== epoch) return;
    const key = token + ':' + identifier;
    if (pollsInFlight.has(key)) return;
    pollsInFlight.add(key);
    let succeeded = false;
    try {
      const snapshot = await api.personalJob(identifier, ref);
      if (token !== epoch) return;
      const job = mergeJob(snapshot);
      succeeded = true;
      syncActiveJob();
      if (current?.id === job?.id) render(job);
      if (job && !isActive(job)) await refresh();
    } catch (error) {
      if (token === epoch && current?.id === identifier) {
        status.textContent =
          'Status nicht bestätigt: ' + error.message +
          ' Bitte „Aufträge / Status aktualisieren“ verwenden; der Auftrag wird nicht erneut gestartet.';
      }
    } finally {
      pollsInFlight.delete(key);
      const requestedWhileInFlight = resumeAfterPoll.delete(key);
      if (token !== epoch) return;
      const activeId = syncActiveJob();
      if (activeId === identifier && (succeeded || requestedWhileInFlight)) {
        schedulePoll(identifier, token, requestedWhileInFlight ? 0 : 1500);
      } else if (activeId && activeId !== identifier) {
        schedulePoll(activeId, token, 0);
      }
    }
  }

  async function refresh() {
    const ref = selection()?.ref;
    const token = epoch;
    const revisionAtRequest = displayRevision;
    if (!ref) {
      status.textContent = 'Bitte zuerst einen Fall speichern oder laden.';
      return;
    }
    try {
      const response = await api.personalJobs(ref);
      if (token !== epoch) return;

      const snapshots = response.jobs || [];
      const updated = snapshots.map(mergeJob).filter(Boolean);
      const listedIds = new Set(updated.map((job) => job.id));
      const historyJobs = [...updated];
      for (const job of jobsById.values()) {
        if (!listedIds.has(job.id)) historyJobs.push(job);
      }
      renderHistory(historyJobs);

      const found = pending ? updated.find((job) => job.requestId === pending) : null;
      if (found) {
        const shouldSelect = displayRevision === pendingDisplayRevision;
        pending = null;
        pendingDisplayRevision = null;
        if (shouldSelect) {
          page = 1;
          render(found);
        }
      }

      if (current) {
        const latest = jobsById.get(current.id);
        if (latest && current.id === latest.id) render(latest);
      } else if (historyJobs.length && revisionAtRequest === displayRevision) {
        page = 1;
        render(historyJobs[0]);
      }

      const activeId = syncActiveJob();
      if (activeId) schedulePoll(activeId, token);
      else if (pending && !submissionInFlight && !found && revisionAtRequest === displayRevision) {
        status.textContent =
          'Annahmestatus weiterhin unbestätigt. Bitte Status erneut abgleichen; den Auftrag nicht erneut starten.';
      }
    } catch (error) {
      if (token === epoch && revisionAtRequest === displayRevision) {
        status.textContent = 'Auftragshistorie nicht bestätigt: ' + error.message;
      }
    }
  }

  document.getElementById('personal-refresh').addEventListener('click', refresh);

  cancel.addEventListener('click', async () => {
    const jobId = current?.id;
    const ref = selection()?.ref;
    if (!jobId || !ref || !isActive(current)) return;
    const token = epoch;
    cancel.disabled = true;
    try {
      const snapshot = await api.cancelPersonal(jobId, ref);
      if (token !== epoch) return;
      const job = mergeJob(snapshot);
      syncActiveJob();
      if (current?.id === jobId) render(job);
      if (!isActive(job) && timerJobId === jobId) clearTimer();
      await refresh();
    } catch (error) {
      if (token === epoch && current?.id === jobId) {
        status.textContent = 'Abbruchstatus nicht bestätigt: ' + error.message + ' Bitte Status aktualisieren.';
      }
    } finally {
      cancel.disabled = false;
    }
  });

  eventBus.addEventListener('case.changed', () => {
    epoch++;
    displayRevision++;
    clearTimer();
    current = null;
    activeJobId = null;
    pending = null;
    pendingDisplayRevision = null;
    submissionInFlight = false;
    jobsById.clear();
    page = 1;
    result.replaceChildren();
    pager.replaceChildren();
    history.replaceChildren();
    proof.textContent = '';
    cancel.hidden = true;
    status.textContent = 'Fallauswahl geändert. Frühere persönliche Aufträge behalten ihren eigenen Kontext.';
    if (procedureSelect.value === 'personal') void refresh();
  });

  procedureSelect.addEventListener('change', () => {
    if (procedureSelect.value === 'personal') void refresh();
  });

  return {
    async start(params) {
      if (submissionInFlight || pending || activeJobs().length) {
        status.textContent = 'Ein Auftrag ist noch aktiv oder nicht bestätigt. Bitte Status abgleichen, nicht erneut starten.';
        return;
      }

      const token = epoch;
      const startRevision = displayRevision;
      const requestId = crypto.randomUUID().replaceAll('-', '');
      try {
        const body = personalRequest(selection(), { ...params, requestId });
        pending = requestId;
        pendingDisplayRevision = startRevision;
        submissionInFlight = true;
        status.textContent = 'Persönlicher Auftrag angefordert … Bitte nicht erneut starten.';

        const snapshot = await api.startPersonal(body);
        if (token !== epoch) return;
        submissionInFlight = false;
        pending = null;
        pendingDisplayRevision = null;
        const job = mergeJob(snapshot);
        syncActiveJob();
        if (displayRevision === startRevision) {
          page = 1;
          render(job);
        }
        const activeId = syncActiveJob();
        if (activeId) schedulePoll(activeId, token);
        void refresh();
      } catch (error) {
        if (token !== epoch) return;
        submissionInFlight = false;
        if (error.status) {
          pending = null;
          pendingDisplayRevision = null;
        }
        if (displayRevision === startRevision) {
          status.textContent =
            'Persönliche Analyse: ' + error.message +
            (pending ? ' Annahmestatus unklar; bitte Auftragshistorie abgleichen.' : '');
        }
        const activeId = syncActiveJob();
        if (activeId) schedulePoll(activeId, token);
      }
    },
    refresh,
  };
}