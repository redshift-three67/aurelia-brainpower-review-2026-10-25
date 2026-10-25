'use strict';
(() => {
  const key = 'governor-theme';
  const valid = value => ['system', 'light', 'dark'].includes(value);
  let choice = 'system';
  try {
    const saved = localStorage.getItem(key);
    if (valid(saved)) choice = saved;
  } catch { /* Storage may be unavailable; this session still supports themes. */ }
  const system = typeof window.matchMedia === 'function' ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  const apply = () => {
    document.documentElement.dataset.theme = choice === 'system' ? (system?.matches ? 'dark' : 'light') : choice;
  };
  // Run before the stylesheet and body are parsed to avoid a wrong-theme first paint.
  apply();
  const onSystemChange = () => { if (choice === 'system') apply(); };
  if (system?.addEventListener) system.addEventListener('change', onSystemChange);
  else if (system?.addListener) system.addListener(onSystemChange);
  document.addEventListener('DOMContentLoaded', () => {
    const select = document.getElementById('theme-choice');
    if (!select) return;
    select.value = choice;
    select.addEventListener('change', () => {
      if (!valid(select.value)) return;
      choice = select.value;
      apply();
      try { localStorage.setItem(key, choice); } catch { /* Keep the chosen theme for this page. */ }
    });
  });
})();
