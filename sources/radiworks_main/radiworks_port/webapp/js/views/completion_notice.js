const OPAQUE_ID = /^[a-f0-9]{32}$/i;
const NOTICE_PREFERENCE = 'broadcast.localCompletionNotice';
const MAX_DEDUPE_ENTRIES = 1024;

export function isFinishedBroadcast(payload) {
  return Boolean(payload && typeof payload === 'object'
    && payload.finished === true
    && payload.stopped !== true
    && payload.failed !== true);
}

export function completionNoticeText(payload) {
  if (!isFinishedBroadcast(payload) || !isOpaqueId(payload.broadcastId)) return null;
  const jobId = payload.targetReference?.jobId;
  if (isOpaqueId(jobId)) {
    return `Broadcast abgeschlossen · Auftrag ${jobId.slice(0, 8)}.`;
  }
  return `Broadcast abgeschlossen · Broadcast ${payload.broadcastId.slice(0, 8)}.`;
}

export function createCompletionDeduper(limit = 128) {
  const capacity = Number.isInteger(limit) && limit > 0
    ? Math.min(limit, MAX_DEDUPE_ENTRIES)
    : 128;
  const recent = new Set();
  return {
    accept(broadcastId) {
      if (!isOpaqueId(broadcastId) || recent.has(broadcastId)) return false;
      recent.add(broadcastId);
      if (recent.size > capacity) recent.delete(recent.values().next().value);
      return true;
    },
    get size() {
      return recent.size;
    },
  };
}

export function initCompletionNotice(api, eventBus) {
  const node = globalThis.document?.getElementById('broadcast-completion-notice');
  if (!node || !eventBus?.addEventListener) return () => {};

  node.setAttribute('role', 'status');
  node.setAttribute('aria-live', 'polite');
  node.setAttribute('aria-atomic', 'true');
  node.hidden = true;

  const deduper = createCompletionDeduper();
  let enabled = false;
  let settingsRevision = 0;
  let disposed = false;

  function setEnabledFrom(settings) {
    enabled = settings?.booleans?.[NOTICE_PREFERENCE] === true;
    if (!enabled) node.textContent = '';
    if (!enabled || !node.textContent) node.hidden = true;
  }

  async function refreshPreference(revision = settingsRevision) {
    try {
      const settings = await api.settings();
      if (!disposed && revision === settingsRevision) setEnabledFrom(settings);
    } catch (_) {
      if (!disposed && revision === settingsRevision) setEnabledFrom(null);
    }
  }

  function onSettingsChanged(event) {
    settingsRevision += 1;
    const settings = event?.detail;
    if (settings?.booleans && Object.hasOwn(settings.booleans, NOTICE_PREFERENCE)) {
      setEnabledFrom(settings);
    } else {
      setEnabledFrom(null);
      void refreshPreference(settingsRevision);
    }
  }

  function onBroadcastProgress(event) {
    const payload = event?.detail;
    if (!enabled || !isFinishedBroadcast(payload)) return;
    const text = completionNoticeText(payload);
    if (!text) {
      node.textContent = '';
      node.hidden = true;
      return;
    }
    if (!deduper.accept(payload.broadcastId)) return;
    node.textContent = text;
    node.hidden = false;
  }
  eventBus.addEventListener('settings.changed', onSettingsChanged);
  eventBus.addEventListener('broadcast.progress', onBroadcastProgress);
  void refreshPreference();

  return () => {
    disposed = true;
    eventBus.removeEventListener?.('settings.changed', onSettingsChanged);
    eventBus.removeEventListener?.('broadcast.progress', onBroadcastProgress);
  };
}

function isOpaqueId(value) {
  return typeof value === 'string' && OPAQUE_ID.test(value);
}