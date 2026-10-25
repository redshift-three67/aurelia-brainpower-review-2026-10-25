# S3c C1 – Rücknahmesperre, 18.09.2026

Status: C1 implementiert und gezielt verifiziert. S3c insgesamt offen; C2–C4 und abhängige Ausführung bleiben gesperrt.

## Nachweis

- TDD: Nicht-Spitzen-Rücknahme wurde vor Umsetzung unerwartet zugelassen; gezielter Test schlug fehl.
- Sechs neue Tests mit tatsächlichen temporären PilotApply-Dateiübernahmen: A vor B gesperrt; B/A korrekt zurückgenommen; Wiederholung ohne Ereignis-/Schreibduplikat; unbestätigte neuere Übernahme gesperrt; Fremdänderung und veränderter Transaktionsbeleg gesperrt; Journalfortschritt während physischer Rücknahme gesperrt; fehlgeschlagener Ereignis-Commit explizit ohne erneute Dateischreibvorgänge abschließbar.
- Bestehender Integrationstest angepasst: Rücknahmeereignis entsteht jetzt automatisch im physischen Rücknahmeabschluss, kein zweites manuelles Ereignis.
- Abschließende Regression: **93 Tests bestanden, keine Skips, 18.422 Sekunden**. Module: test_change_rollback, test_change_journal, test_change_chain_preview, test_change_chain, test_technical_completion, test_pilot_apply, test_pilot_actions. Log: `S3c_C1_2026-09-18_unittest.log`.

## Grenzen

Die Windows-Sandbox verweigerte temporäre Testverzeichnisse. Die aussagekräftigen Testläufe erfolgten mit genehmigter Sandbox-Ausnahme; keine ACL-Änderung. Ein erster Regressionstest erwartete noch das manuelle Rücknahmeereignis und wurde auf den neuen Vertrag umgestellt; obiger Abschlusslauf enthält die Korrektur.

Upstream-Test-/Review-/Abschlussbelege in den neuen Zweischritttests sind Fixtures. Keine vollständige abhängige End-to-End-Ausführung, kein neuer Gesamtsuitenlauf, keine Browseränderung, keine Live-Modell-, Server- oder NAS-Prüfung. Dateien und SQLite bilden keine gemeinsame atomare Transaktion: der persistierte Claim und explizite Wiederherstellungsstatus sichern die Lücke; gemischte Teilrücknahme bleibt zur manuellen Prüfung gesperrt. Keine automatische Wiederaufnahme. Der lokale Dienst wurde in diesem Schritt nicht gestartet.

Nächster Schritt C2: Belege unabhängig aus dauerhaften Quellen lesen und frisch an Auswahl, Quellenstand und explizite Entscheidungen binden. Danach C3 Ausführungspfade und C4 API/UI sowie gemeinsame Abnahme.
