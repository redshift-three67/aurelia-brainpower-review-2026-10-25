# Pause und Wiederaufnahme: RadiWorks-Engine-Sperre, 28.09.2026

Persönlicher lokaler Wiederherstellungspunkt: `checkpoints/Hermes-RadiWorks-20260928-EngineLock-Pause`. Bei normaler Fortsetzung die aktuellen Arbeitsdateien weiterverwenden; nur nach tatsächlichem Verlust gezielt aus dem geprüften Checkpoint zurückspielen. Der ältere Checkpoint `Hermes-RadiWorks-20260928-Pause` liegt vor den nachfolgenden RadiWorks-Arbeiten.

## Gesicherter Stand

- Die aktuelle RadiWorks-Funktionsmatrix steht in `docs/verification/RADIWORKS_FUNKTIONSMATRIX_2026-09-27.md`, insbesondere den Fortsetzungen vom 28.09.2026. Begrenzte Original-JAR-Vergleiche, persistierter Stick-Pad-Passport/Draft/Case, GV-Fortsetzung, Wiederanlauf und synthetische Browserproben sind dort mit ihren Grenzen festgehalten.
- Der dokumentierte Einzel-Engine-Vertrag ist nun durch eine OS-Sperre auf `.engine.lock` je aufgelöstem Runtime-Home erzwungen. Windows-Tests belegen gleiche-Home-Ablehnung, getrennte Homes und Freigabe nach erzwungenem Prozessende. Die vollständige RadiWorks-Engine-Suite bestand danach mit Exit 0. Die POSIX-Variante ist noch nicht auf Linux getestet.
- Externe Katalogschreiber teilen diese Sperre nicht. Eine echte dateiübergreifende Katalog-Momentaufnahme, der erzwungene Tenant-Scope, direkte Host-Wege und die Aurelia-Freigabe bleiben offen. Keine Hardware-, CUDA- oder Kozyrev-Abnahme.
- Governor war vor dem Checkpoint auf 8787 nicht erreichbar. Sein SQLite-Journal hatte `integrity_check=ok`, null aktive/auf Betreiber wartende Aufträge und `auto_review=false`. Der synthetische RadiWorks-Preview auf 8101 antwortete mit HTTP 200 und wurde nicht neu gestartet. Port 8090 war bei der aktuellen Abfrage nicht erreichbar; dies ist keine Radi144-Diagnose.
- RadiWorks enthält weiterhin uncommitteten WIP. Der Checkpoint ist eine lokale Kopie ausgewählter Quellen und Laufzeitdaten, kein Git-Commit, keine vollständige Produktrepository-, Windows-, Server- oder externe Datensicherung.

## Genau hier weiter

1. `VERIFY.json`, `SOURCE_STATE.json`, diese Notiz und die Funktionsmatrix lesen; vorhandenen WIP und aktuelle Port-/Prozesslage neu prüfen. Keine Aufträge automatisch wiederholen.
2. Das Katalog-Schreib-/Veröffentlichungsprotokoll mit unveränderlichem Versionsstand entwerfen und gegen gleichzeitige Änderungen prüfen. Bis dahin keine atomare Katalog-Momentaufnahme behaupten.
3. Vor Linux-/Aurelia-Einsatz den POSIX-Sperrpfad, Mandanten-/Hostvertrag und vollständigen lokalen Bedienablauf separat prüfen. Produkt- und Integrationsgates bleiben geschlossen.

Kein Low-/Medium-Wechsel offen. Automatische Modellreviews bleiben aus.
