/* Einstellungen-View: die Policy-Whitelist steuert Anzeige und Speichern. */
import {
  SETTING_DESCRIPTIONS,
  buildSettingsUpdate,
  displayValues,
  visibleKeys,
} from '../settings-policy.js';

function settingCopy(key, type) {
  const info = SETTING_DESCRIPTIONS[key];
  if (!info || info.type !== type) throw new Error('Unbekannte sichtbare Einstellung.');
  const content = document.createElement('span');
  content.className = 'setting-copy';
  const title = document.createElement('strong');
  title.textContent = info.name;
  const technical = document.createElement('code');
  technical.textContent = key;
  const help = document.createElement('span');
  help.className = 'setting-help';
  help.textContent = info.help;
  const status = document.createElement('span');
  status.className = 'setting-effect';
  status.textContent = info.active ? 'Aktiv in dieser Engine' : 'Derzeit nur gespeichert';
  content.append(title, technical, help, status);
  if (info.group === 'advanced') {
    content.classList.add('setting-copy-advanced');
    const advanced = document.createElement('span');
    advanced.className = 'setting-section';
    advanced.textContent = 'Erweiterte Einstellung';
    content.prepend(advanced);
  }
  if (type === 'boolean') {
    const current = document.createElement('span');
    current.className = 'setting-current';
    content.appendChild(current);
    return { content, current };
  }
  return { content };
}

export function initSettingsView(api, eventBus) {
  const boolBox = document.getElementById('settings-booleans');
  const intBox = document.getElementById('settings-integers');
  const strBox = document.getElementById('settings-strings');
  const saveBtn = document.getElementById('settings-save-btn');
  const out = document.getElementById('settings-out');

  let state = { name: 'Settings', booleans: {}, integers: {}, strings: {} };

  api.settings().then((data) => {
    state = normalizeSettings(data);
    render();
  }).catch((error) => {
    out.textContent = 'Einstellungen konnten nicht geladen werden: ' + error.message;
  });

  function render() {
    const keys = visibleKeys();
    const shown = displayValues(state);

    boolBox.innerHTML = '';
    for (const key of keys.booleans) {
      const row = document.createElement('label');
      row.className = 'settings-row settings-row-boolean';
      if (SETTING_DESCRIPTIONS[key].group === 'advanced') {
        row.classList.add('settings-row-advanced');
      }
      const box = document.createElement('input');
      box.type = 'checkbox';
      box.checked = shown.booleans[key];
      box.dataset.key = key;
      box.dataset.type = 'boolean';
      const { content, current } = settingCopy(key, 'boolean');
      const updateCurrent = () => {
        current.textContent = box.checked ? 'Eingeschaltet' : 'Ausgeschaltet';
      };
      updateCurrent();
      box.addEventListener('change', updateCurrent);
      row.append(box, content);
      boolBox.appendChild(row);
    }

    intBox.innerHTML = '';
    for (const key of keys.integers) {
      intBox.appendChild(numberRow(key, shown.integers[key]));
    }

    strBox.innerHTML = '';
    for (const key of keys.strings) {
      strBox.appendChild(textRow(key, shown.strings[key]));
    }
  }

  function numberRow(key, value) {
    const definition = SETTING_DESCRIPTIONS[key];
    const row = document.createElement('label');
    row.className = 'settings-row';
    const input = document.createElement('input');
    input.type = 'number';
    input.min = String(definition.min);
    input.max = String(definition.max);
    input.step = '1';
    input.required = true;
    input.value = String(value);
    input.dataset.key = key;
    input.dataset.type = 'integer';
    const { content } = settingCopy(key, 'integer');
    row.append(input, content);
    return row;
  }

  function textRow(key, value) {
    const definition = SETTING_DESCRIPTIONS[key];
    const row = document.createElement('label');
    row.className = 'settings-row settings-row-wide';
    const input = document.createElement('select');
    input.dataset.key = key;
    input.dataset.type = 'string';
    for (const choice of definition.values) {
      const option = document.createElement('option');
      option.value = choice;
      option.textContent = choice;
      option.selected = choice === value;
      input.appendChild(option);
    }
    const { content } = settingCopy(key, 'string');
    row.append(input, content);
    return row;
  }

  saveBtn.addEventListener('click', async () => {
    const edits = { booleans: {}, integers: {}, strings: {} };
    for (const input of document.querySelectorAll('#view-settings [data-key]')) {
      const { key, type } = input.dataset;
      if (type === 'boolean') edits.booleans[key] = input.checked;
      else if (type === 'integer') edits.integers[key] = Number(input.value);
      else edits.strings[key] = input.value;
    }

    const payload = buildSettingsUpdate(state, edits);
    try {
      const saved = await api.updateSettings(payload);
      state = normalizeSettings(saved || payload);
      const detail = saved || payload;
      window.dispatchEvent(new CustomEvent('radiworks:settings-saved', { detail }));
      eventBus?.dispatchEvent(new CustomEvent('settings.changed', { detail }));
      render();
      out.textContent = 'Gespeichert.';
      setTimeout(() => { out.textContent = ''; }, 2500);
    } catch (error) {
      out.textContent = 'Fehler: ' + error.message;
    }
  });
}

function normalizeSettings(value = {}) {
  return {
    name: typeof value.name === 'string' ? value.name : 'Settings',
    booleans: objectOrEmpty(value.booleans),
    integers: objectOrEmpty(value.integers),
    strings: objectOrEmpty(value.strings),
  };
}

function objectOrEmpty(value) {
  return value && typeof value === 'object' && !Array.isArray(value) ? value : {};
}
