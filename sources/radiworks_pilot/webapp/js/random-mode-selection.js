/** Adopt a saved default once; explicit user choice always wins later refreshes. */
export function isRandomMode(value) { return value === 'seeded' || value === 'stochastic'; }
export function initRandomModeSelection(select, status) {
 let chosen = false;
 select.value = '';
 status.textContent = 'Servervorgabe wird geladen. Sie k\u00f6nnen den Zufallsmodus auch selbst ausw\u00e4hlen.';
 const label = value => value === 'seeded' ? 'Reproduzierbar (seeded)' : 'Stochastisch';
 select.addEventListener('change', () => {
  chosen = isRandomMode(select.value);
  status.textContent = chosen ? `Ihre Auswahl: ${label(select.value)}. Sie gilt f\u00fcr neue Auftr\u00e4ge.` : 'Bitte einen Zufallsmodus ausw\u00e4hlen.';
 });
 return {
  ready: () => chosen && isRandomMode(select.value),
  adopt(defaultMode) {
   if (chosen) return;
   if (isRandomMode(defaultMode)) {
    select.value = defaultMode; chosen = true;
    status.textContent = `Beim \u00d6ffnen aus der Servervorgabe vorbelegt: ${label(defaultMode)}. Sie k\u00f6nnen die Auswahl \u00e4ndern.`;
   } else {
    status.textContent = 'Servervorgabe nicht verf\u00fcgbar. Bitte den Zufallsmodus selbst ausw\u00e4hlen.';
   }
  },
 };
}
