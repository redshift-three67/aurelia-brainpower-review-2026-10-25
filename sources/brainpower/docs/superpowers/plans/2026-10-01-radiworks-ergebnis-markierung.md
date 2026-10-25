# RadiWorks Ergebnis-Markierung Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Die bisher farblich markierten Wortwiederholungen im RadiWorks-Analyseergebnis werden für Nutzer verständlich und auch ohne Farbwahrnehmung erkennbar.

**Architecture:** Nur die vorhandene Analyseansicht des getrennten 8103-Kandidaten wird ergänzt. `recurrenceWords` und die Server-Engine bleiben unverändert. Ein synthetischer Browsercheck prüft die Erklärung und die Marker gegen die bereits erzeugte Zeilenklasse.

**Tech Stack:** HTML, Vanilla JS/CSS, vorhandener Playwright-Chrome-Test auf isoliertem Port 8104.

---

### Task 1: Erklärung und Marker

**Files:**
- Modify: `runtime/rw-s46-canonical-20260929/radiworks_port/webapp/index.html`
- Modify: `runtime/rw-s46-canonical-20260929/radiworks_port/webapp/js/views/analyze.js`
- Modify: `runtime/rw-s46-canonical-20260929/radiworks_port/webapp/css/app.css`
- Modify: `runtime/test_radiworks_dock_8104.cjs`

- [x] **Step 1: Browsererwartung zuerst schreiben.** Vor Analyse ist `#result-recurrence-hint` verborgen. Nach künstlicher seeded Analyse ist er sichtbar; `#result-body tr.row-recurrence` und `.recurrence-marker` haben dieselbe positive Anzahl, und jede nicht markierte Zeile hat keinen Marker.
- [x] **Step 2: Test rot prüfen.** Der isolierte Browsercheck scheiterte erwartungsgemäß am fehlenden `#result-recurrence-hint`.
- [x] **Step 3: Minimal ergänzen.** Erklärung, sichtbares `W` mit `aria-label="Wiederholung in Ratenbezeichnung"` und kleines Textbadge eingefügt. Der bestehende Zählalgorithmus blieb unverändert.
- [x] **Step 4: Grün prüfen.** JS-Syntax und isolierter Browsercheck bestanden; der vollständige synthetische Browser-Smoke bestand mit 19/19 Abschnitten. Auf 8103 gab es keine synthetischen Fall-/Analyseaufrufe. Der isolierte 8104-Prozess wurde nach Prüfung beendet.
- [x] **Step 5: Kandidatenbericht ergänzen.** Bedeutung und Nachweis dokumentiert; eine Betreiber-Sichtprüfung ist bei diesem neuen Hinweis noch nicht erfolgt. Originalinstanz 8102, Radi144 8090 und Governor 8787 blieben unberührt.

**Execution selection:** Inline, weil dieselbe laufende Kandidatenoberfläche und ein gemeinsamer Browsercheck betroffen sind. Kein weiterer Agent schreibt an diesen Dateien.
