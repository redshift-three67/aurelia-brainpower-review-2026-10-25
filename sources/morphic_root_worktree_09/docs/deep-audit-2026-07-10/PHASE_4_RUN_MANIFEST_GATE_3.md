# Phase 4 – Gate 3: Synthetischer Manifest-Persistenznachweis

**Status:** Additiver Post-Success-Writer grün und weiterhin unverdrahtet.

`core/compliance/run_manifest_persistence.py` schreibt ein bereits gebautes
Manifest ausschließlich, wenn der explizite Snapshot `status == "completed"`
und `returncode == 0` enthält. Fehlgeschlagene oder laufende Snapshots erzeugen
keine Datei. Erfolgreiche synthetische Manifeste werden atomar über eine
kurzlebige Tempdatei geschrieben; ein bestehendes Ziel wird nicht überschrieben.

`tests/test_run_manifest_persistence.py` nutzt nur `tmp_path` und belegt:

1. Erfolgs-Snapshot erzeugt ein exakt lesbares JSON-Manifest ohne Temp-Rest.
2. Fehler- und Running-Snapshot erzeugen kein Manifest.

Nicht geändert: Scanner, Launcher, Scores, Export-/Reportwriter, Runtime-
Manifest, Web-Jobstore und reale Pfade. Die Anbindung an einen konkreten
Top-N-Lauf bleibt ein separates Gate mit PII-, Artefakt- und
Äquivalenznachweisen.
