// Display preview only. The server creates and validates the saved title and ID.
export function contextTitlePreview(personal = {}, focus = '') {
  const text = value => typeof value === 'string' ? value.normalize('NFC').trim() : '';
  const date = text(personal.birthDate);
  const birth = /^\d{4}-\d{2}-\d{2}$/.test(date) ? date.slice(8,10) + date.slice(5,7) + date.slice(0,4) : '';
  const place = ['birth','residence'].includes(personal.placeKind) ? text(personal.place) : '';
  const identity = [text(personal.firstName), text(personal.lastName), birth, place].filter(Boolean).join(' ');
  const topic = text(focus);
  return [identity, topic].filter(Boolean).join(' - ') || 'Neuer Fall (ID beim Speichern)';
}
