# UI_DESIGN_STANDARD — Einheitliche HTML-Modul-Oberfläche für die Aurelia-Plattform

> Erfasst am 2026-08-29 aus den Betreiberanforderungen (RadiWorks-P3-Vorbereitung).
> Gilt für ALLE RadiX-Module: gleiche Integrationsstruktur, adaptive Farbgebung,
> E-E-A-T-fähige Semantik. Basis: Aurelia `docs/08-ui-a11y.md`, `AGENTS.project.md`
> (Hard Rules 1, 9), `docs/18-clipboard.md`.

**Planungsnachtrag 30.09.2026:** Der Betreiber hat anschließend das sichtbare Hermes-/Governor-Design als spätere **visuelle Vorlage** für Aurelia und ihre Module festgelegt; Routing, Datenmodelle und Freigaben gehören ausdrücklich nicht zu dieser Übertragung. Brainpower `docs/AURELIA_DESIGN_TEMPLATE.md` definiert dafür D0–D4 und getrennte modulweise Akzentpaletten. Die folgenden Tokens und Layoutregeln sind der ältere Modul-Entwurf, **noch kein** aus Hermes und Aurelias aktuellem UI-Bestand abgenommener D1-Vertrag. Vor einer gemeinsamen Revision werden beide Oberflächen inventarisiert, Token-/Komponentenzuständigkeit versioniert und Kontrast, Hell/Dunkel, Tastatur, Mobilansichten sowie Modulwechsel geprüft. Die lokale RadiWorks-19/19-Browserprobe und gezielte hörende Fallaktionsprobe ersetzen diese plattformweite Designabnahme nicht.

## 1. Adaptive Farbgebungsstruktur (Token-Layer)

Drei Layer, kaskadierende CSS-Custom-Properties — steuerbar aus Aurelia UND aus
dem Modul selbst:

```css
:root {                        /* Layer 1: Plattform-Basis (Aurelia) */
  --aur-parchment: #F3EFE6;    /* Pergament  */
  --aur-ink:       #1C241E;    /* Tinte      */
  --aur-sage:      #2C4A3E;    /* Sage       */
  --aur-sage-soft: color-mix(in srgb, var(--aur-sage) 18%, var(--aur-parchment));
  --aur-radius: 10px;
  --aur-font-display: "Fraunces Variable", serif;
  --aur-font-body: "Source Sans 3 Variable", sans-serif;
}
[data-module-theme="radiworks"] {   /* Layer 2: Modul-Akzent (Aurelia setzt) */
  --mod-accent: var(--aur-sage);
}
[data-module-theme="radiworks"][data-accent="wellenreiter"] {  /* Layer 3: Modul-intern */
  --mod-accent: #2C5E7A;             /* modul-eigene Nuance, ableitbar aus Basis */
}
```

- **Alle** Farben leiten sich aus den drei Aurelia-Tokens ab (`color-mix`), keine
  freien Farbwerte → kein Lila, kein Gold-Glow, kein Neon (08-ui-a11y).
- Umstellung: Aurelia setzt `data-module-theme`/`data-accent` am Container
  (Plattformsteuerung); das Modul setzt dieselben Attribute intern (Autarkie).
  Beide Wege greifen auf dieselben Variablen zu — „adaptiv über Aurelia oder das Modul".
- `prefers-color-scheme: dark` als eigene Token-Belegung, gleiche Hue-Familie.
- `prefers-reduced-motion`: statischer Frame + Textstatus (docs/15-live.md).

## 2. Einheitliche Integrationsstruktur je Modul („Blaupause")

```
webapp/
├── index.html            # lädt js/boot.js; setzt data-module-theme="<modul>"
├── css/tokens.css        # Layer 1 (Plattform-Basis, kopiert aus diesem Standard)
├── css/module-theme.css  # Layer 2/3 (Modul-Akzent)
├── css/app.css           # Layout/Komponenten nur mit Var-Nutzung
├── js/boot.js            # Konfiguration + Theme-Injection + API/WS-Verbindaufbau
└── js/...                # Views (ES-Module, keine Framework-Pflicht)
```

**Vertrag an die Plattform (alle Module identisch):**

| Mechanismus | Bedeutung |
|---|---|
| `window.__MODULE_CONFIG__` | `{ apiBase, wsUrl, theme, locale }` — von Aurelia injizierbar; Fallback `?api=`/`?theme=`-URL-Parameter; niemals hardcodet |
| `data-module-theme` / `data-accent` | Theme-Schnittstelle (siehe §1) |
| DOM-Host | Modul läuft solo UND in Aurelias Preview-Host/iframe (`preview-host-bridge.tsx`) — kein Skript-Zugriff auf den Elternkontext |
| Semantische Landmarks | `<header>/<main>/<nav>/<section aria-labelledby>` — Aurelia-Shell kann navigieren |
| Lebenszyklus | `window.addEventListener("message")` für `{"type":"module:theme"…}`, WS-Close + `AudioContext.close()` bei Entladen (docs/15-live.md „Wischen") |

## 3. E-E-A-T-Konformität (Google-Qualitätssignale) — „heilsam & vertrauenswürdig"

| Signal | Umsetzung im Modul |
|---|---|
| **Experience** | Sessions/Verlaufsdokumentation mit Passports (jede Zahl mit Quelle `simulated/derived/...`) — nachvollziehbare Praxis statt Behauptung |
| **Expertise** | Klare Praktiker-Sprache, Quellenangaben (Raten-Datenbanken, Clarke-Korpus) sichtbar; keine Diagnose-/Therapie-Claims (CopyGuard, Hard Rule 1) |
| **Authoritativeness** | Impressums-/Herkunftsbereich: Kernel-Version, Kernel-Hash (aus `/manifest`), Datenquellen, Stand |
| **Trust** | Sichtbarer Hinweis „Kein Medizinprodukt — kein Ersatz ärztlicher Leistung" (08-ui-a11y-Pflicht), saubere Fehlerzustände, keine dunklen Muster |

Technische Trust-Signale für moderne Endgeräte: semantisches HTML5, ein
`<h1>` je View, Meta-Description, Offscreen-freie Kontraste (WCAG 2.2 AA =
mindestens 4.5:1 Text), Tastaturnavigation, 44-px-Ziele, Skip-Link,
sichtbarer Fokus (Layout nach `08-ui-a11y.md`).

## 4. Responsivität & moderne Endgeräte

- Mobile-first, ein Breakpoint-Set je Modul identisch (360 / 768 / 1080 / 1440).
- Touch-Ziele ≥ 44 px; Hover-Funktionen immer mit Tastatur-Alternative.
- Broadcast-Visualisierung als `<canvas>` mit devicePixelRatio-Skalierung;
  bei `prefers-reduced-motion` ein statischer Frame (docs/15-live.md).
- WebSocket-Reconnect an letzter Event-ID; Offline-Hinweis statt stiller Fehler.

## 5. Verifikation (P3-Abnahme)

1. **CDP-Live-Sicht:** Modul wird per Chrome DevTools Protocol im Chrome geöffnet
   und geprüft (Konsole fehlerfrei, Theme-Umschaltung via `data-accent`, WS-Events
   sichtbar, Screenshots für die Moduldokumentation).
2. Theme-Wechsel Aurelia-seitig simuliert (Container-Attribut setzen).
3. Kontrast-Check aller Token-Kombinationen (automatisiertes Skript empfohlen).
4. Tastatur-Durchlauf aller Kernworkflows.

## 6. Festlegungen (mit Betreiber abgestimmt, 2026-08-29)

- **Theme-Quelle Layer 1: „Kopie + Override"** — die kanonische `tokens.css`
  liegt in `Modul_Templates/standards/` und wird je Modul kopiert; Aurelia
  kann zur Laufzeit per `data-module-theme`/`data-accent` überschreiben.
  Module laufen autark, keine Versionierungsabhängigkeit beim Booten.
- **RadiWorks-Eigenfarbe (Layer 3): „Wellenreiter"** — Ableitung aus
  `#2C5E7A` × Sage per `color-mix`, Default-Akzent des Moduls.
- Offen bleibt: Schrift-Lizenzierung (Fraunces/Source Sans 3 self-hosted vs.
  System-Fallback im Solo-Betrieb) — Entscheidung vor Stufe 4.
