# Feldengine – Vollständiges Design Template
> Stand: 2026-03-05

---

## 1. Design-Philosophie

| Aspekt | Wert |
|--------|------|
| **Ton** | Wissenschaftlich-mystisch, deep dark UI |
| **Zielgruppe** | Therapeuten, Heilpraktiker, NLS-Anwender |
| **Differenzierung** | Katastrophentheorie × TCM × Frequenztherapie |
| **Modus** | Nur Dark Mode (kein Light Mode) |

---

## 2. Typografie

| Rolle | Font | Gewichte | Verwendung |
|-------|------|----------|------------|
| **Display** | Playfair Display | 400–700, Italic | H1–H6, Titel, Hero |
| **Body** | Inter | 300–700 | Fließtext, Labels, UI |

```css
/* Tailwind-Klassen */
.font-display  → Playfair Display, Georgia, serif
.font-body     → Inter, system-ui, sans-serif
```

**Import:** `@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Inter:wght@300;400;500;600;700&display=swap');`

---

## 3. Farbsystem (HSL)

### 3.1 Kern-Token (CSS Custom Properties)

| Token | HSL-Wert | Hex (ca.) | Verwendung |
|-------|----------|-----------|------------|
| `--background` | 222 47% 4% | #090d16 | Seiten-Hintergrund |
| `--foreground` | 210 40% 96% | #eff3f8 | Standard-Text |
| `--card` | 222 47% 6% | #0d1322 | Karten-Hintergrund |
| `--card-foreground` | 210 40% 96% | #eff3f8 | Karten-Text |
| `--popover` | 222 47% 8% | #111a2e | Popover-Hintergrund |
| `--popover-foreground` | 210 40% 96% | #eff3f8 | Popover-Text |
| `--muted` | 220 20% 15% | #1f2633 | Gedämpfte Flächen |
| `--muted-foreground` | 215 20% 60% | #8494a7 | Sekundärer Text |
| `--border` | 220 20% 18% | #252d3a | Rahmen |
| `--input` | 220 20% 15% | #1f2633 | Input-Hintergrund |
| `--ring` | 192 82% 45% | #14a8c9 | Fokus-Ring |
| `--radius` | – | 0.75rem | Border-Radius |

### 3.2 Semantische Farben

| Token | HSL | Rolle |
|-------|-----|-------|
| `--primary` | 192 82% 45% | Cyan/Teal – Feld-Energie, CTAs |
| `--primary-foreground` | 222 47% 4% | Text auf Primary |
| `--primary-glow` | 192 100% 60% | Glow-Effekte |
| `--secondary` | 38 92% 50% | Warm Gold – Chreoden/Attraktoren |
| `--secondary-foreground` | 222 47% 4% | Text auf Secondary |
| `--accent` | 270 60% 55% | Violett – Bifurkationen |
| `--accent-foreground` | 210 40% 98% | Text auf Accent |
| `--destructive` | 0 72% 51% | Rot – Fehler/Destruktiv |
| `--destructive-foreground` | 210 40% 98% | Text auf Destructive |

### 3.3 Feldengine-spezifische Farben

| Token | HSL | Tailwind-Klasse | Bedeutung |
|-------|-----|-----------------|-----------|
| `--field-deep` | 222 47% 4% | `field-deep` | Tiefster Hintergrund |
| `--field-surface` | 222 47% 8% | `field-surface` | Oberflächen-Ebene |
| `--field-elevated` | 222 40% 12% | `field-elevated` | Erhöhte Elemente |
| `--chreode` | 38 92% 50% | `chreode` | Chreoden-Pfade |
| `--chreode-glow` | 38 100% 65% | `chreode-glow` | Chreoden-Glow |
| `--attractor` | 192 82% 45% | `attractor` | Attraktor-Punkte |
| `--attractor-glow` | 192 100% 70% | `attractor-glow` | Attraktor-Glow |
| `--bifurkation` | 270 60% 55% | `bifurkation` | Bifurkations-Marker |
| `--katastrophe` | 350 80% 55% | `katastrophe` | Katastrophen-Warnung |

### 3.4 Sidebar-Token

| Token | HSL |
|-------|-----|
| `--sidebar-background` | 222 47% 6% |
| `--sidebar-foreground` | 210 40% 90% |
| `--sidebar-primary` | 192 82% 45% |
| `--sidebar-primary-foreground` | 222 47% 4% |
| `--sidebar-accent` | 220 20% 15% |
| `--sidebar-accent-foreground` | 210 40% 90% |
| `--sidebar-border` | 220 20% 18% |
| `--sidebar-ring` | 192 82% 45% |

---

## 4. Gradienten

| Name | CSS-Wert | Tailwind |
|------|----------|---------|
| Field | `linear-gradient(135deg, hsl(222 47% 4%) 0%, hsl(220 40% 10%) 50%, hsl(222 47% 4%) 100%)` | `bg-gradient-field` |
| Chreode | `linear-gradient(135deg, hsl(38 92% 50%) 0%, hsl(45 100% 60%) 100%)` | `bg-gradient-chreode` |
| Attractor | `linear-gradient(135deg, hsl(192 82% 45%) 0%, hsl(185 90% 55%) 100%)` | `bg-gradient-attractor` |
| Hero | `radial-gradient(ellipse at 50% 0%, hsl(192 82% 45% / 0.15) 0%, transparent 50%)` | `bg-gradient-hero` |
| Card | `linear-gradient(180deg, hsl(222 47% 8%) 0%, hsl(222 47% 6%) 100%)` | `bg-gradient-card` |

**Text-Gradienten:**
- `.text-gradient-primary` → Cyan 135° (192→185)
- `.text-gradient-secondary` → Gold 135° (38→45)

---

## 5. Schatten & Glow

| Name | CSS-Wert | Tailwind |
|------|----------|---------|
| Glow Primary | `0 0 60px hsl(192 82% 45% / 0.3)` | `shadow-glow-primary` |
| Glow Secondary | `0 0 40px hsl(38 92% 50% / 0.25)` | `shadow-glow-secondary` |
| Card | `0 4px 24px hsl(222 47% 4% / 0.5)` | `shadow-card` |
| Elevated | `0 8px 32px hsl(222 47% 4% / 0.6)` | `shadow-elevated` |

**Utility-Klassen:**
- `.glow-primary` → 40px + 80px Cyan Glow
- `.glow-secondary` → 30px + 60px Gold Glow
- `.border-glow` → 1px Cyan Border + Inset-Glow

---

## 6. Animationen

| Name | Klasse | Dauer | Beschreibung |
|------|--------|-------|-------------|
| Float | `.animate-float` | 6s | Schwebe-Effekt mit leichter Rotation |
| Pulse Glow | `.animate-pulse-glow` | 3s | Opacity + Scale Pulsieren |
| Flow | `.animate-flow` | 8s | Horizontale Laufbewegung |
| Field Wave | `.animate-field-wave` | 4s | Wellenförmige Verschiebung |
| Chreode Pulse | `.animate-chreode-pulse` | 2.5s | Gold-Shadow Pulsieren |
| Attractor Orbit | `.animate-attractor-orbit` | 8s | Orbitale Kreisbewegung |
| Fade In Up | `.animate-fade-in-up` | 0.8s | Einblenden von unten |
| Grid Flow | `.animate-grid-flow` | 20s | Hintergrund-Gitter Animation |

**Stagger-Klassen:** `.stagger-1` bis `.stagger-5` (100ms–500ms delay)

---

## 7. Hintergrund-Patterns

| Klasse | Beschreibung |
|--------|-------------|
| `.bg-field-pattern` | 3-Layer Radial-Gradient (Cyan 8%, Gold 6%, Violett 4%) |
| `.bg-grid` | Linien-Gitter 50×50px mit Border-Color bei 50% Opacity |

---

## 8. Scrollbar

```css
::-webkit-scrollbar         → 8×8px
::-webkit-scrollbar-track   → hsl(222 47% 6%) = Card-Hintergrund
::-webkit-scrollbar-thumb   → hsl(220 20% 25%), hover: Primary/50%
```

---

## 9. Border Radius

| Token | Wert |
|-------|------|
| `lg` | 0.75rem (var(--radius)) |
| `md` | calc(0.75rem - 2px) = ~0.625rem |
| `sm` | calc(0.75rem - 4px) = ~0.5rem |

---

## 10. Breakpoints & Container

| Breakpoint | Wert |
|-----------|------|
| Container Max | 1400px (2xl) |
| Container Padding | 2rem |

---

## 11. Komponenten-Bibliothek

Basis: **shadcn/ui** (Radix UI + Tailwind)

Installierte Komponenten:
Accordion, Alert, Alert Dialog, Aspect Ratio, Avatar, Badge, Breadcrumb, Button, Calendar, Card, Carousel, Chart, Checkbox, Collapsible, Command, Context Menu, Dialog, Drawer, Dropdown Menu, Form, Hover Card, Input, Input OTP, Label, Menubar, Navigation Menu, Pagination, Popover, Progress, Radio Group, Resizable, Scroll Area, Select, Separator, Sheet, Sidebar, Skeleton, Slider, Sonner (Toast), Switch, Table, Tabs, Textarea, Toast, Toggle, Toggle Group, Tooltip

---

## 12. 3D-System

| Bibliothek | Version |
|-----------|---------|
| Three.js | ^0.170.0 |
| @react-three/fiber | ^8.18.0 |
| @react-three/drei | ^9.122.0 |

**Normalisierung:**
- Target Bounds: y: -0.15 bis 0.95, center x/z: 0
- Automatische Skalierung auf Zielhöhe
- Label: `distanceFactor: 3`, `pointer-events: none`
- Atem-Animation: `sin(t * 0.8) * 0.01`
- OrbitControls Target: `[0, 0.4, 0]`

---

## 13. NLS Dysregulations-Farbskala (6-Stufen)

| Stufe | Label | Farbe (HSL) |
|-------|-------|-------------|
| 1 | Norm | 142 70% 45% (Grün) |
| 2 | Leicht | 48 90% 50% (Gelb) |
| 3 | Mittel | 25 95% 53% (Orange) |
| 4 | Deutlich | 0 72% 51% (Rot) |
| 5 | Stark | 280 60% 50% (Violett) |
| 6 | Schwer | 0 0% 20% (Dunkelgrau) |

---

## 14. Organ-Scan Farbzuordnung

| Organ | Farbe |
|-------|-------|
| heart | #ef4444 |
| lung | #3b82f6 |
| liver | #22c55e |
| kidney | #f59e0b |
| stomach | #f97316 |
| spleen | #a855f7 |
| intestine | #14b8a6 |
| brain | #ec4899 |
| thyroid | #06b6d4 |
| pancreas | #84cc16 |

---

## 15. Framer Motion Standards

- Page transitions: `opacity 0→1`, `y: 20→0`
- Card hover: `scale(1.02)`, `shadow-glow`
- Stagger children: 100ms delay
- AnimatePresence für Ein-/Ausblendungen
- `layout` prop für Layout-Animationen
