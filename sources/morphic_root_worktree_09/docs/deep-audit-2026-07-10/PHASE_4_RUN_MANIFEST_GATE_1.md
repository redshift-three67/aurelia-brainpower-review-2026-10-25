# Phase 4 – Gate 1: Additiver Run-Manifest-Builder

**Status:** Reiner, nicht verdrahteter Manifest-Builder grün; kein Scan-, Report- oder
Jobverhalten geändert.
**Ziel:** Ein späterer Lauf kann ein versioniertes, maschinenlesbares und pseudonymes
Manifest erhalten, ohne den heutigen Defaultlauf zu beeinflussen.

## 1. Implementierte, enge Grenze

`core/compliance/run_manifest.py` bietet ausschließlich
`build_run_manifest(...)`. Die Funktion führt keinen Scan aus, liest keine
Produktionsdatei, schreibt keine Datei und akzeptiert keine Klarnamen-,
Geburtsdaten-, Geburtsort- oder Fokusfelder.

Der Builder erzeugt deterministisch:

- `schema_version`, `run_id` und expliziten ISO-Zeitstempel,
- Software-Commit,
- kanonische pseudonyme Tenant-/Client-IDs,
- Profil- und Daten-SHA-256-Hashes,
- Seed-Modus und Parameter-Version,
- optionale Artefakt-SHA-256-Hashes sowie
- einen SHA-256 über den kanonischen Manifestinhalt.

Alle Identifier und Hashes werden validiert. Nichtkanonische Identitäten sowie
ungültige Digests werden vor dem Aufbau abgewiesen.

## 2. Nicht geändert

- keine Resonanz-, NLS-, Profil-, Gruppen-, Multiplex- oder Scoringlogik,
- kein CLI- oder Web-Launcher-Command,
- kein Runtime-Manifest, Workbench-Run-Trace oder Web-Jobstore,
- kein Export- oder Reportwriter und
- kein produktiver Speicherpfad.

Damit bleibt der bestehende Defaultlauf fachlich und technisch unverändert. Die
Integration in einen realen Lauf ist ausdrücklich ein späterer Gate-Schritt.

## 3. TDD-Nachweis

`tests/test_run_manifest.py` wurde vor dem Modul erstellt und schlug zunächst
mit `ModuleNotFoundError` fehl. Danach belegt er:

1. deterministische Wiederholung bei identischen, synthetischen Eingaben,
2. vollständige Manifestblöcke inklusive Artefakthashes und Manifesthash,
3. ausschließlich pseudonyme Identitätsstruktur ohne Klartextfelder und
4. fail-closed bei nichtkanonischer Client-ID oder ungültigem SHA-256.

## 4. Nächste Phase-4-Gates

1. Den Builder mit einer expliziten, getesteten Quelle für Commit-, Profil- und
   Datenhashes verbinden, ohne Parameter oder Scoreberechnung zu verändern.
2. Das Manifest nach erfolgreichem Lauf additiv schreiben und seine
   Artefakthashes aus tatsächlichen Ausgaben ableiten.
3. Erst danach ein persistentes Web-Jobmanifest mit redigiertem Command,
   Owner/Tenant, Zeitstempeln, Exitstatus und Logpfaden ergänzen.
4. Recovery bleibt bis zu einem eigenen Test read-only; JSONL-Progress und
   Mehrprozess-/Lock-Entscheidungen bleiben nachgelagert.

Keine dieser Folgestufen ist durch dieses Gate freigegeben.
