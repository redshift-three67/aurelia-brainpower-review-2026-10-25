# Projektwechsel und getrennte Aufnahmeentwürfe — 24.09.2026

## Ergebnis

Ungespeicherte Aufnahmefelder bleiben beim Wechsel im geöffneten Tab erhalten, getrennt nach Umfangsart, Umfangs-ID und Mitglieds-ID. Einzelaufnahme eines Gruppenmitglieds und Gruppenaufnahme teilen keinen Formularentwurf. Die zuletzt gewählte Mitglieds-ID wird je Umfang gemerkt. Eine erfolgreiche Aufnahmebestätigung entfernt den zugehörigen lokalen Entwurf. Vault-Versanderlaubnis, Planauswahl und ausführbare Kandidaten werden nicht restauriert. Keine neue Persistenz, Backendänderung, Modellfreigabe oder automatische Ausführung.

Vom Dienst geladene Entwürfe behalten ihre ursprüngliche Quellenbindung; eine veraltete Bindung sperrt die Bestätigung weiterhin. Eigene unbestätigte Texte erhalten beim Quellenwechsel einen Prüfhinweis; ihre ausdrückliche Bestätigung verwendet den neu gelesenen Umfangshash. Neuladen/Schließen verwirft die tablokalen Texte, wie in der Oberfläche angegeben. Eine verspätete Fehlermeldung einer überholten Aufnahme verdrängt den aktuellen Kontext nicht mehr.

## Nachweise

- Neuer JavaScript-Test `tests/test_scope_ui.cjs` reproduzierte zuerst den Verlust der Auswahl/des A-Entwurfs. Nach Korrektur erfolgreich: A→B→A, gleicher Mitgliedsname in Einzel-/Gruppenkontext, Gruppenmitgliederwechsel, ursprüngliche Quellenbindung und tatsächliche Sperre eines veralteten Dienstentwurfs, Cache-Löschung nach Bestätigung, verspätete Aufnahme-/Planantworten und unverändertes Ziel eines laufenden Reviews. Der Test verwendet isolierte DOM-/Transportattrappen; produktive Funktionen werden aus der ausgelieferten Datei gelesen.
- `artifacts/project-context-backend.log`: 46 Tests in 163,090s, 45 erfolgreich, ein Skip. Registry, Scopes, registrierte Gedächtnisse und Store-Neustartverhalten geprüft. Skip: Windows erlaubt im Testkontext keine Symlinkanlage; dieser Symlinkfall ist hier nicht verifiziert.
- JavaScript-Syntax sowie vorhandene Routing-, Tokenanzeige- und Änderungsketten-UI-Prüfungen bestanden.
- Echte Browserprüfung mit produktivem HTML/JS gegen `tests/context_browser_fixture.py` auf Loopback-Port 8794. Ausschließlich synthetische A/B/C/D-Projekte und Gruppe G; keine Modellverbindung oder persistente Speicherung. Nachgewiesen: A-Text nach A→B→A erhalten, B zunächst leer/eigenständig; C→D→C innerhalb der Gruppe getrennt; Einzelaufnahme C erhält keinen Gruppentext; laufender synthetischer Review bleibt A zugeordnet, während B aufgenommen und dessen Text wiederhergestellt wird. Verspätete Antworten wurden deterministisch im JavaScript-Test geprüft, nicht zusätzlich durch kontrollierte Browser-Netzwerkverzögerungen abgenommen.
- Unabhängiger begrenzter Review fand keinen konkreten Fehler. Benannte Testlücken (Stale-Sperre, Cache-Löschung, zwei Gruppenmitglieder) anschließend ergänzt und erfolgreich geprüft. Reviewer führte keine eigenen Tests aus.

## Grenzen und nächster Schritt

Der bestehende vollständige Pilot-/Folgetest-/Rollbacknachweis aus `GOVERNOR_RUNTIME_2026-09-24.md` bleibt Referenz; dessen Backend wurde in diesem Paket nicht verändert. Keine erneute Gesamtsuite und keine neue Live-Providerbewertung. Gruppenplanung bedeutet weiterhin keine allgemeine Gruppenmatrix-Ausführung. Der sichtbare Governor bleibt auf Astra/Medium, automatische Reviews aus.

Nächster kleiner Abschnitt des bestätigten Blocks 3: kontextbezogene Schrittführung mit einer erkennbaren nächsten zulässigen Aktion und deren Sperrgrund; Farben ergänzen Text. Danach gemeinsame Funktionsabnahme vor neuen Aurelia-Adaptern oder neutralem Windows-Paket. Reasoning Medium, kein Low-Wechsel offen.
