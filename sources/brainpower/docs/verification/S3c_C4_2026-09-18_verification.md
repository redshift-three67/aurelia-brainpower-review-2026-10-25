# C4 und begrenzte Hermes-Abnahme – 18.09.2026

## Ergebnis

Direktes A→B-Profil eines erlaubten unabhängigen Piloten mit getrennten Schreibbereichen: geschützte API und explizite Oberfläche implementiert und geprüft. Keine allgemeine Produktketten- oder Serverfreigabe.

| Prüfung | Nachweis |
|---|---|
| Python-Gesamtregression | 659 Tests in 261,371 s; 657 erfolgreich, 2 wegen fehlender Windows-Symlinkrechte ausgelassen. `S3c_C4_2026-09-18_full_final.log`; Exit 0. |
| C3b-Regression | 204 gezielte Tests bestanden, siehe separater C3b-Bericht. |
| HTTP-A/B-Integration | Echte temporäre Dateiübernahmen bis H2, getrennte Bestätigungen und Rücknahme B vor A; Modell-/Reviewberichte simuliert. Geschützte Routen verweigern falsche Sitzung/Origin/CSRF und Zusatzfelder. |
| JavaScript | `node --check governor_workbench/static/app.js`; `node tests/test_change_chain_ui.cjs`: Routing, getrennte Entscheidungen, Notizpersistenz und exakte Fixture-Funktionsparität bestanden. |
| Echter Browser | Unveränderte Produktionsdialogfunktion in lokaler synthetischer Fixture: Öffnen nur lesend; H0 mit Pflichtnotiz; H1 bestätigen erzeugt null B-Vorschläge; separater Klick erzeugt genau einen simulierten B-Vorschlag; Reload erzeugt keinen weiteren. H0/H1/H2 korrekt, B-vor-A sichtbar, nach Rücknahme neue Planrevision und gesperrter Vorschlagsbutton. Keine Konsolenfehler. CSP verbietet Netzwerkzugriffe der Fixture. |
| Laufender lokaler Dienst | Regulär neu gestartet; `/state` 200, Zusatzfeld 400, fremder Origin 403. Null aktive Aufträge, automatische Reviews false, Supervisor gpt-6-astra. App nach Reload ohne gemeldete Konsolenfehler. Keine echten Modellaufträge oder Ketten gestartet. |
| Hermes | Lokale `probe_only=True`-Prüfung: null Werkzeuge; kein Live-Modellnachweis. |
| Vertrag | `docs/LLM_OPERATING_CONTRACT.json` erfolgreich geparst. |

## Gefundene und behobene Fehler

1. C3b-Review: neuere B-Vorschläge mussten ältere Quellen auch vor Test/Modelltransport/Übernahme entwerten. Regression zunächst rot, danach korrigiert; Nachreview ohne weitere konkrete Befunde.
2. C4-Review: UI las H1/H2 aus einem nicht vorhandenen direkten Feld. Echte Struktur `event.evidence.technical_receipt.binding.observed_scope_hash` verwendet; Fixture entsprechend korrigiert, Regression rot→grün, tatsächliche Browseranzeige geprüft.
3. Erster Gesamtlauf nicht bestanden: Quellen-Drift-Test mockte nach Umstrukturierung nur den alten PlanBook-Import. Beide verwendeten Bindungspunkte auf denselben Testmock gesetzt; Produktionsprüfungen unverändert.
4. Derselbe Lauf meldete eine Thread-Ausnahme: HTTP-Test ersetzte die App-Konfiguration, bevor Beobachter/Worker beendet waren. Jetzt vor Abhängigkeitstausch regulär schließen und auf Threadende prüfen. Acht gezielte Tests danach bestanden; abschließender Gesamtlauf ohne Fehler oder Thread-Ausnahme.

## Grenzen / Folgeschritte

Historische externe Vorgänger nach Quellenwechsel sind weiterhin gesperrt. Der ursprüngliche weitergehende C3-Plan ist insoweit nicht vollständig erledigt; aktuelle Abnahme umfasst nur das direkte unabhängige Zweischrittprofil. Zwei Symlink-Prüfungen bleiben auf diesem Windows-Host unbelegt. Browserfixture, temporäre HTTP-Dateiübernahme und lokale Dienstprüfung sind getrennte Nachweise, kein vollständiger Live-Modell-Produktlauf.

Betreiberpriorität danach: zuerst Aurelia-/Modul-Templates-Voraussetzungen klären. Lesender Quellenabgleich dokumentiert; bestehende Aurelia-Augustdokumente sind gegenüber den späteren Serverarbeiten veraltet, aber nicht automatisch freigegeben.

Serverzugangsprüfung: SSH durch WireGuard zu 10.77.0.1 validiert den gespeicherten Hostschlüssel mit Alias 185.242.115.210. Lokale Standardschlüssel abgelehnt; anschließend der bereits eingerichtete temporäre Schlüssel erfolgreich als klaus999. Am 18.09.2026 10:45 UTC: Ubuntu 24.04.5 LTS / Kernel 6.8.0-139-generic, beide RAID1 [UU], null fehlgeschlagene Units, Firewall und wg-admin aktiv. CIFS-Werkzeuge/Restic vorhanden, kein CIFS-Mount; tatsächlich benannter aurelia-backup-files.timer deaktiviert. Health-Unit letzter Result=success / ExecMainStatus=0 (keine vollständige Sicherheitsabnahme). sudo -n verlangt Passwort. Weitere privilegierte SMB-/Restorearbeit benötigt Root-KVM. Keine Passwortversuche, keine SSH-/Firewall-/Serveränderungen, keine Backup-/Restorebehauptung.

Temporäre Browserfixture geschlossen, ihr HTTP-Testdienst beendet. Governor bleibt lokal aktiv. Kein neuer ZIP-Checkpoint erstellt; letzter ZIP vor C1–C4 enthält diese Änderungen nicht.
