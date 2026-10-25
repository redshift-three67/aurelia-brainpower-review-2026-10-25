export const OPTIONS_VERSION_KEY = 'broadcast.optionsVersion';
export const OPTIONS_VERSION = 'options-v1';

const LEGACY_POLICY_KEYS = new Set([
  'broadcast.single.rates.only',
  'broadcast.delta.time',
  'dynamic.adjustments',
]);

export const SETTING_DESCRIPTIONS = {
  'broadcast.localCompletionNotice': {
    type: 'boolean',
    name: 'Lokaler Abschluss-Hinweis',
    help: 'Zeigt nach einem erfolgreich beendeten Broadcast einen barrierefreien Hinweis mit einer gekürzten Auftragskennung. Keine System-, E-Mail- oder Desktop-Benachrichtigung.',
    default: false,
    active: true,
    group: 'general',
  },
  'broadcast.single.rates.only': {
    type: 'boolean',
    name: 'Einzelraten-Queue',
    help: 'Begrenzt die Zahl gleichzeitig laufender Broadcasts auf höchstens 1 statt 8. Bereits aktive Broadcasts laufen weiter; wartende starten erst, wenn ein Platz frei wird.',
    default: false,
    active: true,
    group: 'general',
  },
  'broadcast.delta.time': {
    type: 'boolean',
    name: 'Delta-Zeitregel',
    help: 'Bei direkten Broadcasts mit belegtem Original-GV aus Sitzung oder Entwurfsfall: Sind die eingegebenen Sekunden größer als der eingefrorene Fall-GV, wird dieser abgezogen; sonst bleibt die Eingabe unverändert. Gilt nicht für dynamische Folgeaufträge; Promote wendet die Zeitregel nicht erneut an.',
    default: false,
    active: true,
    group: 'general',
  },
  'dynamic.adjustments': {
    type: 'boolean',
    name: 'Begrenzte dynamische Folgeaufträge',
    help: 'Erlaubt zusätzliche, begrenzte Folgeschritte nur für sicher belegte Originalmodus-Aufträge. Höchstzahl und Mindestdauer stehen unten. Persönliche Matrixwerte sind kein GV; Auto-, Bild- und nicht belegte Aufträge erzeugen dadurch keine stillen Folgejobs.',
    default: false,
    active: true,
    group: 'general',
  },
  'broadcast.legacyMixMode': {
    type: 'boolean',
    name: 'Älteren direkten Mix-Ablauf erlauben',
    help: 'Erweiterte Kompatibilität für den älteren direkten API-Mix-Aufruf: Ein Prüfdraft kann nach serverseitigem CopyGuard ohne den getrennten sichtbaren Prüfen-/Freigeben-Schritt in die virtuelle Queue gelangen. Standardmäßig AUS; keine Hardwareausgabe.',
    default: false,
    active: true,
    group: 'advanced',
  },
  'play.binaural.sound': {
    type: 'boolean',
    name: 'Binauralen Ton abspielen',
    help: 'Bei passenden Resonanzereignissen versucht der Browser einen kurzen Ton abzuspielen. Browser und Lautsprecher können die Wiedergabe verhindern; Analysewerte bleiben unverändert.',
    default: false,
    active: true,
    group: 'general',
  },
  'analysis.very.high.max.hit': {
    type: 'boolean',
    name: 'Sehr hohen EW-Grenzwert vorbelegen',
    help: 'Ändert nur die Vorbelegung des EW-Grenzwerts im neuen Analyse-UI: AUS = 100, EIN = 1000. Eine manuelle Auswahl bleibt maßgeblich; die Zahl der angezeigten Treffer wird dadurch nicht festgelegt.',
    default: false,
    active: true,
    group: 'general',
  },
  'broadcast.adjustment.maxFollowups': {
    type: 'integer',
    name: 'Maximale Folgeaufträge',
    help: 'Obergrenze für zusätzliche dynamische Folgeaufträge im Originalmodus. 0 deaktiviert Folgeaufträge; höchstens 3 sind möglich.',
    default: 1,
    min: 0,
    max: 3,
    active: true,
    group: 'general',
  },
  'broadcast.adjustment.minSeconds': {
    type: 'integer',
    name: 'Mindestdauer je Folgeauftrag (Sekunden)',
    help: 'Untergrenze der Dauer eines dynamischen Originalmodus-Folgeauftrags. Zulässig sind 1 bis 86400 Sekunden.',
    default: 10,
    min: 1,
    max: 86400,
    active: true,
    group: 'general',
  },
  'entropy.defaultMode': {
    type: 'string',
    name: 'Standard-Entropiemodus',
    help: 'Gilt für neue Aufträge mit „Einstellung (Server)“. „seeded“ ist mit gleichem Seed und Katalog reproduzierbar. „stochastic“ nutzt nicht reproduzierbare Quellen; bei aktivem Fall ist dafür ein dauerhaft gesicherter Wiederherstellungsschlüssel nötig.',
    default: 'seeded',
    values: ['seeded', 'stochastic'],
    active: true,
    group: 'general',
  },
};

const TYPE_ORDER = ['booleans', 'integers', 'strings'];
const TYPE_NAMES = { booleans: 'boolean', integers: 'integer', strings: 'string' };

export function visibleKeys() {
  const result = {};
  for (const category of TYPE_ORDER) {
    const type = TYPE_NAMES[category];
    result[category] = Object.keys(SETTING_DESCRIPTIONS)
      .filter((key) => SETTING_DESCRIPTIONS[key].type === type);
  }
  return result;
}

export function displayValues(settings = {}) {
  const keys = visibleKeys();
  const stored = {
    booleans: objectOrEmpty(settings.booleans),
    integers: objectOrEmpty(settings.integers),
    strings: objectOrEmpty(settings.strings),
  };
  const versioned = stored.strings[OPTIONS_VERSION_KEY] === OPTIONS_VERSION;
  const result = { booleans: {}, integers: {}, strings: {} };

  for (const key of keys.booleans) {
    const definition = SETTING_DESCRIPTIONS[key];
    result.booleans[key] = LEGACY_POLICY_KEYS.has(key) && !versioned
      ? false
      : stored.booleans[key] === true;
    if (!Object.hasOwn(stored.booleans, key)) {
      result.booleans[key] = definition.default;
    }
  }
  for (const key of keys.integers) {
    const definition = SETTING_DESCRIPTIONS[key];
    const value = stored.integers[key];
    result.integers[key] = Number.isInteger(value)
      && value >= definition.min && value <= definition.max
      ? value
      : definition.default;
  }
  for (const key of keys.strings) {
    const definition = SETTING_DESCRIPTIONS[key];
    const value = stored.strings[key];
    result.strings[key] = definition.values.includes(value) ? value : definition.default;
  }
  return result;
}

export function buildSettingsUpdate(settings = {}, edits = {}) {
  const visible = visibleKeys();
  const result = {
    name: typeof settings.name === 'string' ? settings.name : 'Settings',
    booleans: { ...objectOrEmpty(settings.booleans) },
    integers: { ...objectOrEmpty(settings.integers) },
    strings: { ...objectOrEmpty(settings.strings) },
  };

  for (const category of TYPE_ORDER) {
    const allowed = new Set(visible[category]);
    for (const [key, value] of Object.entries(objectOrEmpty(edits[category]))) {
      if (allowed.has(key)) result[category][key] = value;
    }
  }
  result.strings[OPTIONS_VERSION_KEY] = OPTIONS_VERSION;
  return result;
}

function objectOrEmpty(value) {
  return value && typeof value === 'object' && !Array.isArray(value) ? value : {};
}
