# Verifikation Governor 0.2 – 12.09.2026

## Tatsächlich geprüft

- 115 automatisierte Anwendungstests erfolgreich; Ausgabe `artifacts/unit-tests-phase2.txt` (38,153 Sekunden im abschließenden Entwicklungsdurchlauf).
- Separat entpacktes Release im Pfad mit Leerzeichen und isoliertem Python: ebenfalls 115 Tests erfolgreich (32,915 Sekunden). Manifest und Ausschluss persönlicher Konfigurationen, Laufzeitdaten und echter Reviewkontexte geprüft.
- Entscheidungsjournal bleibt beim Neustart erhalten; Autorisierung, Widerruf, Abnahme und Zurückweisung sind getrennt. Veraltete Abnahme wird abgelehnt, abhängige Schritte bleiben gesperrt. Quellen- und Regelfingerabdruck sind vom Entscheidungsfingerprint getrennt.
- RadiWorks-Intake kann nach abgenommenem Quellenabgleich vor Aurelia-Ground-Zero stattfinden. Die spätere Integration bleibt von ihren fachlichen Voraussetzungen abhängig.
- Quellenbericht über echte UI-API erzeugt; authentifizierter Berichtsabruf HTTP200. Keine automatische fachliche Abnahme.
- Vergleich `26c4d99f13ef4d909deea703e40ba6b0`: ein echter Hermes/Terra-Plan, identische Eingaben an Sol und Astra. Beide Modelle antworteten erfolgreich mit `REVIEW_ONLY`; Quellen während des Laufs unverändert. Ergebnis lokal in `artifacts/real-comparison-final-2026-09-12.json`. Modellidentitäten wurden anhand der Antwortmetadaten geprüft. Keine Aussage allgemeiner Modelloptimalität.
- Die Modelle berücksichtigen aktuelle lesende Autorisierungen und behandeln die historische Pause nicht mehr als pauschalen Blocker. Die früheren 205 erfolgreichen RadiWorks-Tests bleiben im Kontext erhalten, auch nach mehr als zehn weiteren Aufträgen. Diese Produkttests wurden in dieser Erweiterung nicht erneut ausgeführt.
- Automatische Reviews nach ausdrücklicher separater Betreiberfreigabe aktiviert: max. vier Versuche pro UTC-Tag, mindestens 15 Minuten Abstand, nur bei Änderungen und vollständiger Erfassung. Begrenzung, Ausgangsstand beim Einschalten und Entscheidungsänderungen sind getestet. Ein mehrtägiger Dauerbetrieb ist noch kein ausgeführter Nachweis.
- Tatsächlicher Chrome-Start, CDP-Screenshot und Stop über die Governor-Auftrags-API erfolgreich. Screenshotabruf HTTP200 und an einen unveränderlichen Auftragspfad gebunden. Alle Testfenster danach geschlossen. Früher Fehler beim ersten Capture (Seite noch nicht gerendert und Loopback-DNS blockiert) reproduziert und behoben.
- Abschließender Browsercheck bei 1440 und 390 Pixeln: fünf Projekte, neun Schritte, zwei konfigurierte Live-Ziele, lesbare Vergleichsergebnisse, Screenshot- und Berichtsabruf HTTP200. Keine JavaScript-/Konsolenfehler, keine fehlgeschlagenen Requests und kein horizontaler Überlauf. Dieser Check führte keine POST-Aufträge aus. Bilder: `artifacts/ui-v02-desktop.png`, `artifacts/ui-v02-mobile.png`.
- Unabhängige Prüfung fand u.a. inkonsistente Entscheidungssnapshots, veränderliche Screenshotverweise und vorzeitige Fehlerkennzeichnung laufender Reviews; korrigiert. Abschließende Prüfung ohne weitere wichtige Befunde. Die Codeprüfung erfolgte durch getrennte Agentenkontexte desselben Anbieters; echte Produktreviews durch Terra/Sol/Astra.
- Abschließender Live-Status: Version0.2.0, fünf Projekte, neun Schritte, aktuelle Gegenprüfung, keine aktiven Aufträge, kein Beobachtungsfehler, Windows-Aufgabe Running. Leerlaufstichprobe über20 Sekunden:29,46 MiB Working Set,0,391 Prozent eines CPU-Kerns (`artifacts/idle-v02.json`); kein allgemeiner Hardwarebenchmark.

## Genaue Grenzen

Die fachlichen Projektgates sind nicht automatisch abgeschlossen. Der nächste Punkt ist die Prüfung/Abnahme des aktuellen Quellenabgleichs. Der generierte Quellenbericht ist ein Inventar mit Herkunft und Hashes, keine vollständige ABI-Feldmatrix und kein Ersatz für die jeweils vorgeschriebenen unabhängigen Fachreviews.

Eine allgemeine autonome Produkt-Codekorrektur, ein Git-Commit, eine Migration oder Serverbereitstellung ist nicht Teil des Ausführungsadapters. Die Workbench bietet begrenzte Berichts-, Review-, Test- und Browseraufträge sowie den konfliktgeprüften Gedächtniseditor.

Das Chrome-Ziel RadiWorks ist auf dem aus dessen README belegten Port8090 vorbereitet; bei dieser Abnahme lief dort kein RadiWorks-Server. Die tatsächliche Chrome-Prüfung verwendete die laufende Governor-Oberfläche. Produktserver werden nicht automatisch gestartet. CDP-Logs erfassen das Capture-Zeitfenster, keine vollständige Sitzungshistorie; externe Ressourcen sind im isolierten Browser blockiert.

Das portable Paket enthält keine persönlichen Entscheidungen, Zugangsdaten, echten Projektkontexte oder Laufzeitdaten. Ein anderer physischer Windows-PC bleibt separat zu prüfen.
