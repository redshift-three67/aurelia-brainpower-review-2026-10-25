# Radi144 Projektzielbild: Standalone-System und Referenzmodul

Stand: 2026-06-06

## 1. Nutzerbestaetigtes Zielbild

Radi144 ist die Weiterentwicklung des urspruenglichen Prototyps.

Es soll zwei Rollen gleichzeitig erfuellen:

1. **Standalone-System**
   - lokal lauffaehig,
   - voll funktional gemaess Nutzeranforderungen,
   - stabil, reproduzierbar und bedienbar,
   - mit eigenstaendiger API/CLI/Browser-/PowerShell-Nutzung,
   - ohne Abhaengigkeit davon, dass das uebergeordnete Radiquant-/Wellbeing-System aktiv laeuft.

2. **Referenz- und Informationsmodul fuer das uebergeordnete Radionik-Wellbeing-/Radiquant-Projekt**
   - akkurate, praezise und nachvollziehbare Informationsquelle,
   - technische und konzeptionelle Referenz fuer Radi144 als Modul im groesseren System,
   - Orientierungspunkt fuer spaetere Integration, Datenmodelle, Referenzdaten, Workflows und UI-/API-Verhalten.

## 2. Architektur-Konsequenzen

Radi144 darf nicht nur als historischer Prototyp behandelt werden.

Fuer weitere Arbeit gilt:

- Standalone-Funktionalitaet bleibt Pflicht.
- Modul-/Referenzfaehigkeit fuer das uebergeordnete Projekt bleibt Pflicht.
- Kernengine, Matrixlogik, Resonanzscore, DB-Ranking, EMF-/Audio-/Harmonizer-Funktion werden nur nach expliziter Freigabe geaendert.
- Verbesserungen sollen phase-gated, testbar und rueckwaertsvertraeglich erfolgen.
- Historische Artefakte duerfen dokumentiert werden, aber nicht unkritisch als aktueller SSOT gelten.

## 3. Baseline-Konsequenzen

In die kuratierte Initial-Baseline gehoeren bevorzugt:

- produktiver Standalone-Kern,
- Tests,
- aktuelle API-/CLI-/Browser-/PowerShell-Entrypoints,
- produktiv genutzte Referenzdaten,
- aktuelle Dokumentation,
- neutrale Konfigurations-/Example-Dateien.

Nicht in die Initial-Baseline gehoeren:

- lokale Runtime-/Session-/Analyse-Daten,
- echte Secrets oder lokale Deploy-Overrides,
- historische Debug-/Fix-/Verify-Einmaldateien,
- stale Restore-/Packaging-Skripte mit altem Pre-Bugfix-Kontext,
- ungesicherte In-Repo-Backup-Artefakte.

## 4. Naechste Entwicklungslogik

Nach Abschluss der Baseline-Kuratierung folgt:

1. Initial-Baseline nur nach expliziter Nutzerfreigabe.
2. Danach Phase-4-/PowerShell-/Metadaten-Anbindung adapterartig und rueckwaertsvertraeglich.
3. Anschliessend gezielte Standalone-Qualitaetserhoehung und Referenzmodul-Haertung.
4. Jede funktionale Aenderung mit TDD/Regressionstest und voller Verifikation.
