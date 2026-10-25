# S3c C2 – interne Beleg- und Freigabebindung

Stand 18.09.2026: C2 für explizite Basisanlage und ersten unabhängigen Übergang A implementiert. C3/C4 bleiben offen; keine abhängige Ausführung freigeschaltet.

## Implementierung

- `change_controller.begin`: ursprüngliche Zweischrittvorschau frisch nachprüfen, vollständige Vorschau und Originalauswahl unveränderlich an die Journalbasis binden.
- `confirm`: ausschließlich Referenzen, beobachteten Quellenhash, Auswahl und Begründung entgegennehmen. Transaktion, versiegeltes Manifest, neuesten Staging-Test, neuesten Nachprüfungsauftrag und technischen Abschluss selbst lesen. Zwei Beobachtungen müssen übereinstimmen; auch unveränderte Dateien des zweiten Schritts prüfen.
- Gemeinsamer Ausführungsplatz durch synchronen `change_journal_commit`-Auftrag mit Status `running`; kein Worker-Dispatch. S1/S2/manuelle Aufträge werden über die bestehende gemeinsame Zulassung ausgeschlossen.
- Unmittelbar im abschließenden Schreibvorgang Datenbankversion, Implementierung, Pilotkonfiguration und Registry erneut prüfen. Journalereignis und terminalen Auftragsstatus gemeinsam committen. Identische Bestätigung liefert nur das historische Ereignis.
- Abbruch, Neustart, fehlgeschlagener Commit und neuere unbestätigte Übernahmen verhindern Fortschritt. Keine automatische Wiederholung oder Weiterführung.

## Verifikation

**111 gezielte Tests bestanden, keine Skips, 25.570 Sekunden.** Davon 18 neue Controllerprüfungen. Log: `S3c_C2_2026-09-18_unittest.log`.

Ausgeführt: `tests.test_change_controller`, `tests.test_change_rollback`, `tests.test_change_journal`, `tests.test_change_chain_preview`, `tests.test_change_chain`, `tests.test_technical_completion`, `tests.test_pilot_apply`, `tests.test_pilot_actions`.

Die neue Zweischritt-Testvorbereitung verwendet tatsächliche temporäre Staging-/Apply-/Verify-/Abschlusswege. Upstream-Test-/Reviewberichte sind Fixtures; keine Modellbewertung behauptet. Negative Fälle: alte Vorschau, neue Auswahl, neue fehlgeschlagene Test-/Verify-Versuche, fremde Dateibytes, geänderte Berichte/Manifest/Adapter/Allowlist, konkurrierender Auftrag, Abbruch beim Commit, Datenänderung beim Commit, neuer unbestätigter Transfer, Neustart, fehlgeschlagener Ereignis-Insert und unveränderte historische Wiederholung.

Ein zusätzlicher Regressionstest deckte zunächst einen fehlenden letzten Allowlist-Abgleich auf (erwartete Ablehnung blieb aus). Nach Ergänzung der Konfigurations-/Registry-Bindung bestand dieser Test zusammen mit dem Abschlusslauf. JSON-Betriebsvertrag eingelesen. Unabhängige, begrenzte statische Prüfung durch Review-Agent ohne belastbare Findings; kein eigener zweiter Testlauf des Reviewers.

Die Windows-Sandbox blockierte wieder temporäre Testordner. Verwertbare Testläufe erfolgten mit genehmigter Sandbox-Ausnahme; keine ACL-/Windows-Konfiguration geändert. Frühere Testläufe mit fehlerhafter Sequenz-Fixture zählen nicht als Abschlussnachweis.

## Grenzen und nächster Schritt

Keine HTTP-/UI-Anbindung oder Live-Journalaktivierung. B und historische externe Vorgänger bleiben durch den bisherigen technischen Verifier beziehungsweise eine ausdrückliche Sperre geschlossen. C3 muss eigene H1-Zustimmung und aktuelle B-Belege anbinden; C4 liefert geschützte Bedienwege und gemeinsame Abnahme. C2 ist kein kompletter abhängiger End-to-End-Nachweis.

Jeder fremde Datenbank-Commit während der Beobachtung blockiert konservativ, auch wenn fachlich unabhängig; ausdrücklich neu prüfen, nicht automatisch wiederholen. Dateibeobachtungen sind kein atomarer Dateisystem-Snapshot. Keine neue Gesamtsuite, Browserprüfung, echten Modellaufrufe, Produkt-/Server-/NAS-Änderungen oder Dienstneustart. Letzter ZIP-Checkpoint bleibt S3b und enthält C1/C2 nicht.
