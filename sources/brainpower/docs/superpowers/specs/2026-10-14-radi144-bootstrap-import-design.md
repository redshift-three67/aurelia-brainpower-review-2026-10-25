# Radi144 P3 Bootstrap Importsemantik

Freigegebene Fortsetzung nach Entwurfsabgleich und Betreiberzustimmung zur empfohlenen Reihenfolge am14.10.2026. Gegenstand ist nur das lokale Prüfgerüst, kein Produktimport oder Algorithmuswechsel. Vorherpunkt: `checkpoints/Aurelia-P3-Radi144-Import-Status-20261014-200503Z`.

## Entscheidung und Alternativen

Gewählt: normale Abwesenheit optionaler Importwurzeln nachweisen und als `ModuleNotFoundError` behandeln. Bisher macht der Guard aus `pickle`'s optionaler Jython-Prüfung einen Abbruch. Weitere Einzelausnahmen würden dasselbe Grundproblem wiederholen. Eine allgemeine Importfreigabe würde vorhandene ungeprüfte Pakete zulassen und wird verworfen. Ein späterer isolierter Linuxlauf bleibt ein eigener Plattformnachweis, ist für diese begrenzte Windows-CPU-Probe nicht Voraussetzung.

## Vertrag

- Ausnahme ausschließlich in der Phase `native`, für ein echtes fünfargumentiges Importereignis ohne Dateiorigin. Bereits freigegebene Importwurzeln und das bestehende spezielle TQDM-Gate bleiben unverändert.
- Explizit verbotene Wurzeln bleiben immer gesperrt. Bei bisher unbekannter Wurzel wird nur der erste, gültige Python-Bezeichner geprüft; kein Unterpaketimport oder Paketinitialisierer.
- Suchpfad exakt `SITE_PACKAGES`, `BASE_PREFIX/Lib`, `BASE_PREFIX/DLLs`, dieselbe Reihenfolge wie im Kindprozess. Abweichende Suchpfade oder nichtstandardmäßige Importfinder erlauben keine Abwesenheitsbehauptung.
- PathFinder verwendet unveränderte anfängliche Standard-Pfadhooks und ausschließlich normale FileFinder oder leere Cacheeinträge für diese drei Pfade. Benutzerdefinierte PathEntryFinder verhindern den Abwesenheitsnachweis; keine versteckte Erweiterung des Resolververtrauens.
- Bereits geladene, eingebaute oder eingefrorene Wurzeln gelten nicht als abwesend. `PathFinder.find_spec(root, pinned_paths)` darf kein Paket initialisieren. Vorhandene Module sowie normale oder Namespacepakete bleiben gesperrt, auch wenn ein späteres Untermodul fehlen könnte.
- Nur ein tatsächliches `None`-Ergebnis ergibt `ModuleNotFoundError(name=root)`. Finderfehler bleiben Fehler; kein pauschales Abfangen von Importfehlern innerhalb vorhandener Pakete.
- Beobachtete Abwesenheiten werden im Ergebnis mit Modulname, Wurzel, Finder und gebundenen Suchpfaden dokumentiert. Keine neue Installations-, Datei-, DLL-, Netzwerk-, Prozess- oder Aufrufberechtigung. Python-Auditguard bleibt keine native OS-Sandbox.

## Durchführung

Root besitzt Code, Tests, Controller und Belegsicherung. Luna/max prüft den begrenzten Entwurf unabhängig; Astra/medium prüft die eingefrorene Fassung vor einer nativen Wiederholung. Keine rekursive Delegation, keine zusätzliche Bibliothek installieren.

1. Bestehende Dateien und Wiederaufnahme vor Änderung bytegenau sichern; neun benannte Dateien im Vorhermanifest. Originalquellen vor/nach weiterhin über zehn Dateihashes und benannten Gitstand binden.
2. Neue Regression zuerst rot ausführen: tatsächlich fehlende Wurzel wird noch falsch abgewiesen. Vorhandenes Paket mit absichtlich fehlschlagendem Initialisierer und Namespacepaket dürfen nicht initialisiert werden. Verbotene Wurzeln, fremde Suchpfade, geladene Wurzeln und Phasen bleiben gesperrt.
3. Minimale Korrektur und unveränderte bisherige Tests grün ausführen. Reales Auditereignis im isolierten Standardbibliotheks-Kindprozess nachweisen, nicht nur erfundene Tupel.
4. Freshlabels4/5 in Harness und äußerem Controller getrennt binden; alteVersuche1/2/3 und V7-Fassung erhalten. Gate vor Review geschlossen. Einfrieren und Hashmanifest vor dem nativen Start.
5. Nach positivem Review Quellen-/Paket-/Ressourcenbindungen frisch prüfen, maximal zwei neue CPU-Läufe mit bestehender technischer180s-Grenze. Originalfallgruppen bleiben die bisherigen14; keine Ersatzformeln oder allgemeinen Determinismusbehauptungen.
6. Bei neuem tatsächlichem Fehler keine weitere Patchfolge: vollständige Fehlerkette, Phase und erhaltener Quellen-/Werkzeugzustand dokumentieren; betroffenen Schritt stoppen. Bei Erfolg beide vollständigen stabilen Ergebnislisten vergleichen, Laufzeiten separat.
7. Abschlussbericht, laufenden P3-Plan und Wiederaufnahme anhand tatsächlicher Ergebnisse fortschreiben; gesicherte Dateien und historischer Bytesuffix rückprüfen. Gesamt-P3/P4/P5 und Produktfreigaben bleiben getrennt.

## Abnahmegrenze

Erfolgreiche Werkzeugtests beweisen nur das Prüfgerüst. Ein abgeschlossener Torch-Import und14 ausgeführte Originalfallgruppen müssen separat belegt sein. Vollständige Engineinitialisierung, erfolgreiche Gesamtberechnung, HTTP/UI/CLI, große Kandidatenpools, Hardware, Linux und klinische Aussagen sind nicht Teil dieses CPU-Kernnachweises.
