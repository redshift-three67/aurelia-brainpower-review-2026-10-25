# 05 – Entwickler- und LLM-Übergabe

## Kopierbarer Einstieg für eine neue Sitzung

> Prüfe zunächst die aktuelle Freigabe und die Projektregeln. Lies im Paket `docs/planungsreviews/2026-09-07_11-29-58_CEST` zuerst README, danach 01, 02 und 03. Dieses Paket ist ein Vorschlag, keine eigenständige Ausführungsfreigabe. Der untersuchte Implementierungsstand liegt in `.worktrees/aurelia-konsolidierung` auf Branch `codex/aurelia-konsolidierung`, nicht im älteren Haupt-Worktree. Der Review-Snapshot ist `1185a68ed984b525686764f995513355701929e3`; dazu lagen Änderungen an `package.json` und die unversionierten Dateien `scripts/test-runner.mjs` sowie `scripts/test-runner.test.mjs` vor. Prüfe HEAD und Arbeitskopie frisch und erhalte vorhandene Änderungen. Nicht auf diesen Snapshot zurücksetzen.
>
> Tasks 5 und 6 sind als Änderungen bereits committed; Task 7 ist begonnen und nicht abschließend verifiziert. Historische Übergabe und Task-Ledger sind teilweise überholt. Der empfohlene erste Schritt ist E0, anschließend E1. Starte keine Implementierung, solange die Übernahme der betreffenden Empfehlung und ihr Scope nicht aus der aktuellen Betreiberanweisung oder einer fortgeltenden Freigabe hervorgehen. Produktpause, Servergate und Publikationsgrenzen bleiben unverändert. Fehlende Evidenz ist kein PASS. Prüfe nur den relevanten Umfang und berichte belegt, knapp und mit klaren Grenzen.

## Verbindliche Unterscheidungen

| Begriff | Bedeutung |
|---|---|
| Alter Plan vorhanden | Original ist über Dateipfad und SHA-256 rekonstruierbar |
| Neuer Plan empfohlen | Dokument 03 ist noch nicht automatisch normativ |
| Implementiert | Änderung vorhanden; sagt nichts über vollständige Abnahme |
| Committed | Lokales Git-Objekt vorhanden; keine implizite Publikationsfreigabe |
| Geprüft | Benannter Nachweis am passenden Quellstand vorhanden |
| Historisch geprüft | Alter Nachweis; nicht als frisches Ergebnis ausgeben |
| K1 lokal abgenommen | Nur lokaler freigegebener Scope; keine Server-/Produktionsfreigabe |
| Gate genehmigt | Erfordert dafür zuständige Entscheidung und Nachweise |

## Wiederaufnahmeprotokoll

1. Arbeitsverzeichnis und Branch prüfen.
2. Aktuellen HEAD, Status und relevante unversionierte Dateien inventarisieren; Änderungen seit dem Review bewerten.
3. Quellenmanifest als Vergleich verwenden. Hashabweichung ist ein Anlass zur Prüfung, kein Anlass zum Wiederherstellen alter Dateien.
4. Fortgeltende Betreiberfreigaben von historischen Statusbehauptungen unterscheiden. Keine Freigabe allein aus einem Commit oder einer Checkbox ableiten.
5. Genau ein nächstes Paket bestimmen; Voraussetzungen und zulässige Nebenwirkungen nennen.
6. Bei reiner Dokumentationsfreigabe nur die freigegebenen Dokumente bearbeiten. Bestehende Code-/Datenbank-/Servergrenzen bleiben bestehen.
7. Bei freigegebener kritischer Umsetzung Vertrag und Negativtests vor Code fixieren; Spec-Review vor Quality-Review, gemäß QUALITY-ROUTING.
8. Ergebnisse mit Datum, Quellstand, Exitcode und Aussagegrenze festhalten. Nicht durch wiederholte Komplettlektüre unveränderter Quellen Zeit und Tokens verbrauchen.

## Nicht ausführen aufgrund dieses Pakets

- Kein Reset/Clean zur Beseitigung des Task-7-Diffs.
- Kein Push, PR, Merge, Rebase, History-Rewrite oder Credentialwechsel.
- Kein Serverzugriff, keine Partitionierung oder Installation.
- Kein `npm run build` mit nachgelagerter Migration.
- Keine Auth-/Produktivkonfiguration ändern, um Tests grün zu machen.
- Keine Sperre des Browserwerkzeugs durch CDP oder alternative Wege umgehen.
- Keine automatische Übernahme von RadiWorks-Analyseempfehlungen.
- Keine Bearbeitung der historischen HTML-Statusdatei unter der hier nur für den neuen Ordner erteilten Schreibfreigabe.

## Empfohlene nächste Entscheidung

E0/E1 als abgegrenzte Wiederaufnahme und Plan-/Statuskonsolidierung übernehmen. Anschließend E2 am vorhandenen Runner fortsetzen. Der E5-Instanz-/Cleanup-Vertrag benötigt eine explizite fachliche Entscheidung vor Implementierung. Server Ground Zero und spätere Produktionsabnahme bleiben eigene Pakete.

## Berichtsformat für den Entwickler

```text
Paket:
Freigegebener Scope und Quelle:
Geprüfter Branch/HEAD und Dirty-Dateien:
Geändert oder nur gelesen:
Prüfungen mit Exitcode:
Nicht geprüfte Bereiche:
Offene Befunde/Blocker:
Nächster zulässiger Schritt:
```

Leere Felder nicht durch Vermutungen füllen. Fehlende Information als fehlend kennzeichnen; nur notwendige Rückfragen stellen. Bereits belegte fortgeltende Freigaben nicht erneut anfordern.
