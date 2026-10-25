# Radi144 – Exakter präziser Wortlaut für den Start einer neuen Session

Stand: 2026-06-05 00:15:49
Projekt: Radi144
Projektpfad: `C:\Users\Hubert111\Documents\Radi144`
Aktueller Projekt-Branch: `main`
Commit-Basis: noch kein Commit im neuen projektlokalen Repository

## Exakter Wortlaut für die neue Session

```text
Bitte starte in dieser neuen Session mit einer präzisen verifizierten Ist-Prüfung des Projekts `C:\Users\Hubert111\Documents\Radi144`.

Wichtiger Kontext zum aktuellen Stand:
- Radi144 ist jetzt ein eigenes Git-Repository unter `C:\Users\Hubert111\Documents\Radi144\.git`.
- Das frühere Home-Repo unter `C:\Users\Hubert111\.git` ist für die Projektbewertung nicht mehr maßgeblich.
- Es existiert aktuell noch kein erster Commit im neuen projektlokalen Repository.
- Eine konservative projektlokale `.gitignore` ist angelegt und ignoriert u. a. `.venv/`, `build_env/`, `__pycache__/`, `.pytest_cache/`, `.hermes*.txt`, `Analysen/`, `data/runtime/`, `RestorePoints/`, `restore_points/`, `dev_results.txt`, `debug_output.txt`, `focus_history.txt` und `last_session.json`.
- Die Vollsuite ist zuletzt verifiziert grün: `29 passed, 9 warnings in 3.80s`.
- Ein Import-Smoketest ist verifiziert erfolgreich: `from main import app` liefert Titel `12x12 Resonance Matrix Standalone` und Version `1.5.0`.
- Die zuvor kritischen Blocker wurden bereits behoben: API-`client_id` als echte Runtime-Registry-ID, Session-/Artefakt-Spiegelung unter `data/runtime/`, PDF-Manifest-Anbindung, `tests/__init__.py` gegen Test-Shadowing sowie defensiver CPU-RAM-Guard im Precision-CPU-Pfad.

Arbeitsdisziplin für diese neue Session:
- Kritische Erkenntnisse bitte vor kritischen Änderungen benennen.
- Akkuranz und Stabilität haben Vorrang.
- Minimal invasive, testgetriebene Schritte bevorzugen.
- Keine Annahmen über Git-Historie treffen, solange im neuen Repo noch kein Initial-Commit existiert.

Bitte arbeite in genau dieser Reihenfolge:
1. Verifiziere den projektlokalen Git-Status im neuen Repo.
2. Prüfe trocken, was ein erster Commit tatsächlich aufnehmen würde.
3. Bewerte, ob vor einem Initial-Commit noch minimale Repo-Hygiene oder Warning-Bereinigung notwendig ist.
4. Gib danach eine präzise Lagebewertung: was ist bereits stabil, was ist noch offen, und welcher nächste Schritt ist fachlich und technisch am sinnvollsten.

Wichtig:
Bitte beginne nicht mit großen Refactorings oder breiten Dokumentationsumschreibungen. Starte ausschließlich mit einer konservativen Ist-Prüfung und leite daraus die nächsten minimalen Schritte ab.
```

## Kurzfassung

```text
Bitte starte in der neuen Session mit einer konservativen Ist-Prüfung von `C:\Users\Hubert111\Documents\Radi144`: projektlokales Git-Repo verifizieren, trockene Erstaufnahme prüfen, verbleibende offene Punkte bewerten und erst danach die nächsten minimalen stabilen Schritte empfehlen.
```

## Zweck dieser Fassung

Diese Fassung ist auf die aktuelle Projektlage zugeschnitten und dient nicht dem UI-Text der Anwendung, sondern als exakter Startwortlaut für eine inhaltliche neue Arbeits-Session zu Radi144.
