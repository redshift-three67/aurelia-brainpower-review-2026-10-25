# Entwickler-Kurzübersicht: Morphic V1 in einfachen Worten

> Diese Datei ist bewusst einfach geschrieben – ohne Vorwissen über dieses Repository verständlich. Für Details mit exakten Datei-/Zeilenverweisen siehe die verlinkten Tiefendokumente.

## 1. Was ist Morphic V1 eigentlich?

Ein lokal laufendes Python-System (CLI + Web-Oberfläche), das aus Klientendaten (Name, Geburtsdatum, Geburtsort) und einem gewählten "Fokus"-Thema eine Resonanz-/Ähnlichkeitsanalyse gegen eine große Datenbank von homöopathischen Mitteln/Gruppen berechnet, daraus Berichte erzeugt und optional eine "Harmonisierung" (Hardware-gestützte Modulation) anstößt. Es ist **kein leeres Gerüst**, sondern ein funktionierendes, aber gewachsenes und an mehreren Stellen unaufgeräumtes Expertensystem.

## 2. Wie ist es aufgebaut?

```
apps/cli/     -> Kommandozeile (Haupt-Produktionslogik steckt hier drin, nicht nur "dünne" Befehle)
apps/web/     -> aktuelle Web-Oberfläche (FastAPI + statisches HTML/JS/CSS)
core/         -> Fachlogik: Profile, Resonanz, Hardware, Compliance, Quantum-Synergy
providers/    -> Hardware-/Entropie-Zugriff
services/     -> Hintergrund-Worker (z. B. Harmonisierung)
tools/        -> Berichte/Export-Nachbearbeitung
data/         -> Datenbanken, Laufzeit-Manifeste, Job-Dateien
tests/        -> große Testsuite (202 Tests)
```

Es gibt **zwei parallel existierende Web-Apps** (`apps/web/main.py` aktuell, `web_app.py` alt/deprecated) und **zwei UI-Linien** (`apps/web/static/*` neu, `web_ui/` alt). Für neue Arbeit ist immer `apps/web/main.py` + `apps/web/static/*` die richtige Stelle.

→ Details: `docs/deep-audit-2026-07-04/PHASE_1_CODEBASE_ARCHITEKTUR_UND_STRUKTUR.md`

## 3. Wie läuft der Workflow ab?

Es gibt **drei verschiedene, nicht identische** Wege, wie eine Analyse ablaufen kann – das ist der wichtigste strukturelle Befund überhaupt:

1. **Produktiver Weg (der tatsächlich benutzt wird):** `scan top3-scan` → screent alle Hauptprofile → wählt Top-N (3/5/7/9) → tiefer Scan pro Top-Profil → Berichte.
2. **12-Step-Workflow:** ein sauber strukturierter, aber separater Orchestrator (`apps/cli/workflow/step01..12`) mit eigenem Zustandsmodell. Wird von der Web-Oberfläche **nicht** als Hauptpfad benutzt.
3. **8-Step-Web-Wizard:** die aktuelle Bedienoberfläche im Browser (Preflight → Hinweise → Klient → Fokus → Profil → Freigabe → Berichte → Harmonisierung). Sie sieht wie ein eigener Workflow aus, startet technisch aber Weg 1.

**Für Entwickler heißt das konkret:** Bevor du an "dem Workflow" etwas änderst, kläre zuerst, welchen der drei Wege du wirklich meinst – sie teilen sich keine gemeinsame Fortschritts- oder Ergebnislogik.

→ Details: `docs/deep-audit-2026-07-04/PHASE_2_WORKFLOWS_STEPS_UND_SUBSTEPS.md`

## 4. Sicherheit & Zugriff (Auth/Multitenant)

**Einfach gesagt:** Es gibt aktuell **kein Login, keine Benutzerkonten, keine Rollen, keine Mandanten**. Es gibt einen optionalen API-Key (`X-API-Key`), der nur greift, wenn man ihn per Umgebungsvariable aktiviert – standardmäßig ist er **aus**. Wer die URL/`job_id`/`report_id` kennt, kann Berichte und Job-Status abrufen; es gibt keine Prüfung, "wem gehört das eigentlich".

**Fazit:** Das System ist heute technisch am ehrlichsten als *"lokale Experten-Workstation für eine Person"* zu beschreiben, nicht als Mandanten-/Multitenant-System. Sobald mehrere Personen oder ein Netzwerkzugriff dazukommen, ist das aktuell **nicht ausreichend abgesichert**.

→ Details: `docs/deep-audit-2026-07-04/PHASE_3_SICHERHEIT_DSGVO_AUTH_MULTITENANT.md`

## 5. Datenschutz / DSGVO

**Gute Bausteine, die es schon gibt:**
- Pseudonyme Client-IDs, eine "Safe View" ohne Klarnamen, ein Audit-Log, eine Löschfunktion (Erasure) über die CLI.

**Konkreter Widerspruch, den man kennen sollte:**
- Genau daneben existiert ein Berichts-Katalog im Web, der Klienten weiterhin über Klarnamen + Geburtsdatum + Geburtsort identifiziert (`"Mustermann Klaus 09041966 Augsburg"`). Die eine Hälfte des Systems anonymisiert, die andere zeigt Klartext – das ist der wichtigste Datenschutz-Einzelbefund.
- Es gibt keine automatische Aufbewahrungsbegrenzung (Daten verfallen nicht von selbst) und keine nachweisbare Speicherung der Einwilligung (Consent wird abgefragt, aber nicht revisionssicher gespeichert).

→ Details: `docs/deep-audit-2026-07-04/PHASE_3_SICHERHEIT_DSGVO_AUTH_MULTITENANT.md`

## 6. Frontend / Bedienbarkeit (inkl. Google-2026-Maßstäbe)

Die Web-Oberfläche ist ein funktionierender, für einen internen Bediener brauchbarer 8-Schritt-Assistent – kein Mockup. Was fehlt, gemessen an aktuellen (2026 verifizierten) Google/web.dev-Qualitätsstandards:

- keine Messung von Ladezeit/Reaktionsfähigkeit/visueller Stabilität (Core Web Vitals: LCP/INP/CLS),
- kein "Sprung zum Inhalt"-Link (Skip-Link) und kein automatisches Fokus-Management beim Schrittwechsel,
- keine Berücksichtigung von "reduzierte Bewegung bevorzugt" (`prefers-reduced-motion`),
- Berichte werden schon beim Öffnen der Seite geladen, bevor sie gebraucht werden (unnötig und datenschutzmäßig unglücklich).

**Wichtige Klarstellung:** Da Morphic V1 keine öffentlich von Google auffindbare Website ist, geht es hier nicht um "Google-Ranking", sondern um anerkannte technische Qualitätsstandards für professionelle Webanwendungen – die trotzdem sinnvoll sind, u. a. wegen des deutschen Barrierefreiheitsstärkungsgesetzes (BFSG), falls das Tool je für Endkund:innen geöffnet wird.

→ Details: `docs/deep-audit-2026-07-04/PHASE_4_FRONTEND_UI_UX_UND_GOOGLE_2026.md`, `GOOGLE_2026_VERIFIKATION.md`

## 7. Echtzeit-Hardware – was ist wirklich "live"?

| Komponente | Ehrliche Kurzbeschreibung |
| --- | --- |
| CPU | echt genutzt – als Zeit-/Entropiequelle und in der Harmonisierung |
| RAM | echt gemessen, aber nur als Lastindikator |
| GPU | Status/Erkennung echt, die eigentliche "GPU-Modulation" ist laut Code-Kommentar **CPU-simuliert** |
| WebSocket (Echtzeit-Kanal) | technisch vorhanden, wird von der Haupt-Oberfläche aber kaum genutzt (es wird gepollt statt live gepusht) |
| Quartz | **nicht implementiert** (`use_quartz: False` überall im Code) |

**Merksatz:** "Realtime" und "Hardware" im Produktnamen/UI bedeuten aktuell öfter *Telemetrie und Kontext* als *echte, harte Wirkkopplung*.

→ Details: `docs/deep-audit-2026-07-04/PHASE_7_HARDWARE_ECHTZEIT_DETERMINISMUS.md`

## 8. Quantum-Framework – was ist wirklich "Quantum"?

`core/quantum_synergy/` enthält echten, sauber geschriebenen Code für einen Grover-Quantensuchalgorithmus (mit der Qiskit-Bibliothek). **Aber:** In der aktuell genutzten Entwicklungsumgebung ist Qiskit gar nicht installiert. Das bedeutet: Jede Nutzung läuft heute automatisch über einen klassischen Ersatzalgorithmus, nicht über echtes Quantencomputing – das System merkt das selbst und schaltet sauber um, aber niemand hat den "echten" Pfad hier je laufen lassen oder getestet.

Zusätzlich beschreibt eine interne Dokumentationsdatei ein weiteres Modul ("QAOA-Optimizer"), das im Code **gar nicht existiert**.

**Wichtig für die Einordnung:** Bei der aktuellen Datenmenge (ein paar Tausend Einträge) würde echte Quanten-Hardware heute ohnehin **keinen** praktischen Geschwindigkeitsvorteil bringen – die klassische Suche ist bereits schnell genug. "Quantum-ready", aber aktuell nicht "quantum-aktiv" ist die ehrlichste Beschreibung.

→ Details: `PHASE_8_QUANTUM_FRAMEWORK_TIEFENANALYSE.md`, `PHASE_9_INNOVATIONEN_ECHTZEIT_UND_QUANTUM.md`

## 9. Die 5 größten Baustellen (einfach zusammengefasst)

1. **Drei Workflows statt einem** – erst festlegen, welcher der offizielle ist.
2. **Kein echtes Login/Rollen/Mandanten-Modell**, obwohl mit personenbezogenen Daten gearbeitet wird.
3. **Datenschutz-Widerspruch**: pseudonymisierte Safe-View vs. Klartext-Report-Katalog.
4. **Instabile Testumgebung**: volle Testsuite lief heute erneut mit `21 von 202` fehlgeschlagenen Tests, verursacht durch akute Speicherknappheit auf dem Rechner (kein Logikfehler, aber ein reales Betriebsrisiko für numpy-lastige Abläufe).
5. **Dokumentation hinkt dem Code hinterher** – mehrere zentrale Dateien (`README.md`, `CLAUDE.md`, `PROJECT_MEMORY/00_CURRENT_STATE.md`) beschreiben einen älteren Zustand (z. B. "153 Tests" statt real 202, "main.py 72 Zeilen" nicht mehr exakt zutreffend).

## 10. Was ist gerade schon in Arbeit?

Es läuft bereits – in einem separaten Git-Worktree (`.worktrees/operator-workbench-phase1`), noch nicht auf `master` gemerged – ein Umbau der 8-Schritt-Web-Oberfläche zu einer neuen **"Operator Workbench"** mit 10 Phasen, echtem Review-Schritt vor dem Start, Speicherung von Entwürfen/Vorlagen und einer "Hardware-Wahrheits"-API. Backend-Grundgerüst (Registry, Hardware-Truth, Runtime-Speicher) ist fertig und getestet; die neue Bedienoberfläche selbst ist noch nicht gebaut.

→ Details: `Entwicklung/04_AKTIVE_UMSETZUNG_OPERATOR_WORKBENCH.md`, `docs/superpowers/specs/2026-07-05-morphic-operator-workbench-design.md`

## 11. Wo finde ich was? (Lesewegweiser)

| Frage | Dokument |
| --- | --- |
| Wie ist das Projekt strukturell aufgebaut? | `docs/deep-audit-2026-07-04/PHASE_1_...md` |
| Wie läuft ein Scan/Workflow im Detail ab? | `docs/deep-audit-2026-07-04/PHASE_2_...md` |
| Wie steht es um Security/Auth/DSGVO? | `docs/deep-audit-2026-07-04/PHASE_3_...md` |
| Wie steht es um Frontend/UX/Google-2026? | `docs/deep-audit-2026-07-04/PHASE_4_...md` + `GOOGLE_2026_VERIFIKATION.md` |
| Was sind die größten Lücken und allgemeine Verbesserungsideen? | `docs/deep-audit-2026-07-04/PHASE_5_...md` |
| Was kann man von "Radi144" lernen? | `docs/deep-audit-2026-07-04/PHASE_6_...md` |
| Wie real ist die Hardware-/Echtzeit-Integration? | `docs/deep-audit-2026-07-04/PHASE_7_...md` |
| Wie real ist das Quantum-Framework? | `PHASE_8_QUANTUM_FRAMEWORK_TIEFENANALYSE.md` |
| Welche Innovationen werden für Echtzeit/Quantum vorgeschlagen? | `PHASE_9_INNOVATIONEN_ECHTZEIT_UND_QUANTUM.md` |
| Was ist der aktuelle Gesamtstand inkl. laufender Umsetzung? | `Entwicklung/00_AKTUELLER_GESAMTSTAND.md` |
