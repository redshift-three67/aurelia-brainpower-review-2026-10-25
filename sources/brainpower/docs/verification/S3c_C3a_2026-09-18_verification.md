# S3c C3a – eigene H1-Zustimmung für B

18.09.2026: Erster C3-Baustein implementiert. **C3 insgesamt bleibt offen**; B-Ausführung und geschützte Bedienwege sind noch nicht angebunden.

## Verhalten

`change_successor.preview` beobachtet H1 zweimal ohne Schema-/Auftragsanlage. Der exakt gespeicherte erste A-Übergang wird anhand aktueller dauerhafter Transaktion, versiegeltem Staging, neuestem Test, neuestem Verify und technischem Abschluss erneut geprüft. Ursprünglicher H0-Plan und effektiver H1-Kontext bleiben getrennt. Bindung umfasst Originalauswahl, B-Definition, A-Ereignis-/Beleghashes, Wurzel, alle expliziten Dateihashes, Adapter und Pilotumgebung.

`acknowledge` verlangt Vorschauhash und ausdrückliche Begründung. Ein unveränderlicher versiegelter Zustimmungseintrag pro Kette/Spitze wird gemeinsam mit dem terminalen Auftragsstatus gespeichert. Bestehende gemeinsame Ausführungsreservierung, DB-Version-/Adapter-/Konfigurations-/Registry-Abgleich und Abbruchprüfung bleiben wirksam. Gleiche aktuelle Zustimmung erzeugt keinen zweiten Beleg. `require_current` prüft den gespeicherten Beleg frisch; er erteilt keine zeitlich unbegrenzte Ausführungsfreigabe.

## Nachweise

**125 gezielte Tests bestanden, keine Skips, 33.672 Sekunden.** Davon 14 neue H1-Tests. Vollständiges gezieltes Log: `S3c_C3a_2026-09-18_unittest.log`.

Module: test_change_successor, test_change_controller, test_change_rollback, test_change_journal, test_change_chain_preview, test_change_chain, test_technical_completion, test_pilot_apply, test_pilot_actions.

Geprüft: vollständig schreibfreie Vorschau auch ohne Journal; Zustimmung ohne Plan-/Dateiänderung; identische Wiederholung; fehlender bestätigter Übergang; Fremdänderung; neue Test-/Verify-Versuche; neue Auswahl; A-Rücknahme; fehlende Pilotfreigabe; Abbruch vor und unmittelbar beim Commit; belegter Ausführungsplatz; unveränderliche Zustimmung; fehlgeschlagener Insert ohne erfolgreichen Claim; Drift zwischen Beobachtungen; weiterhin gesperrte bestehende B-Ausführung.

TDD: neuer Einstieg war vor Implementierung nicht vorhanden; Tests zunächst entsprechend fehlgeschlagen. Reale temporäre Staging-/Apply-/Verify-/Abschlusswege, Upstream-Test-/Reviewberichte als Fixtures. Keine echten Modellaufrufe. Tests mit genehmigter Sandbox-Ausnahme wegen des bekannten temporären Windows-Zugriffsfehlers; keine ACL-Änderung. Unabhängiger begrenzter statischer Review ohne konkrete neue Befunde, mittlere Prüfsicherheit; Reviewer führte die Tests nicht nochmals aus. JSON-Betriebsvertrag eingelesen.

## Grenzen / nächste Arbeit

C3b: B-Vorschlag, eigener Staging-Test/Review, Übernahme und technische Nachprüfung müssen diese aktuelle H1-Zustimmung an jeder relevanten Grenze verlangen. Kein Umschreiben ursprünglicher Auswahl oder pauschales Ersetzen von Quellenhashes. Historische externe Vorgänger bleiben ebenfalls noch gesperrt. Danach C4 API/UI und gemeinsame Abnahme.

Keine neue Gesamtsuite oder Browserprüfung; keine UI-Verhaltensänderung, kein Dienstneustart, keine Live-Journalaktivierung und keine Produkt-/Server-/NAS-Arbeiten. Beobachtungen sind kein atomarer Dateisystem-Snapshot. Letzter geprüfter ZIP-Checkpoint bleibt S3b und enthält C1/C2/C3a nicht.
