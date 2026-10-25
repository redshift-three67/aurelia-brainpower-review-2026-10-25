# Session-Sicherung – 2026-07-10T15:40:56+02:00

Diese Sicherung enthält ausschließlich Arbeitskontext, Handoff und Git-Evidenz – keine Secrets, `.env`-Dateien, Runtime-Inhalte oder Klientenexporte.

## Enthalten

- `SESSION_HANDOFF.md` – vollständiger Fortsetzungsauftrag, Architekturentscheidungen, Grenzen, Testergebnisse und nächster P0-Schritt.
- `GIT_EVIDENCE.md` – Branch, HEAD, Arbeitsbaum- und Diff-Statistik.

## Nicht enthalten

- `.git/`, `.venv/`, Caches
- `Benutzer_Archive__ws-...` und andere Klientenexporte
- Runtime-/Job-/Harmonization-Daten
- Umgebungsvariablen und Credentials

## Wiederaufnahme

Zuerst `SESSION_HANDOFF.md` vollständig lesen. Anschließend Branch, Git-Status und Testbasis neu prüfen. Kein Commit/Push oder Export-/Datenmutation ohne explizite Nutzerfreigabe.
