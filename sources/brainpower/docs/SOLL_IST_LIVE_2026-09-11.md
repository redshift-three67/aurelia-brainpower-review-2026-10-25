# Governor – Soll/Ist und reale Projektprüfung am 11.09.2026

Diese Prüfung folgt auf die ausdrückliche Erlaubnis des Betreibers, echte Projektinformationen über CC Switch an Terra, Sol und Astra zu übermitteln. Die Erlaubnis gilt für den Review; sie ist keine pauschale Produkt-, Integrations- oder Deploymentfreigabe. Die frühere Übermittlungsblockade ist für diese Prüfung damit aufgehoben. Automatische Reviews bleiben ausgeschaltet.

## Ergebnis und Aussagegrenze

Die Workbench ist eine laufende Beobachtungs- und Reviewoberfläche. Sie ist noch kein vollständig autonomer Entwicklungs-Governor. Die Projektmatrix enthält konfigurierte Planungswerte neben frisch gelesenen Quellen und Git-Fakten. Modellberichte werden separat im Auftrag gespeichert; sie aktualisieren weder die verbindlichen Projektstatus noch die zentralen Governor-Dateien automatisch.

Die reale Prüfung verwendet begrenzte Gedächtnisauszüge und Governance-Dokumente, keine vollständige erneute Quellcode- und Laufzeitprüfung aller fünf Produkte. `evidence_complete=true` bezeichnet die Vollständigkeit innerhalb des implementierten Beobachtungsumfangs; es bedeutet keine vollständige Produktabnahme.

## Funktionsmatrix

| Gewünschte Funktion | Früherer Snapshot / Ausgangsbefund | Tatsächlicher Zustand | Bewertung |
|---|---|---|---|
| Fünf Projekte zentral beobachten | Statusdokumente vorhanden; laufender Hintergrund-Governor nicht nachgewiesen | Lokaler Dienst und Windows-Anmeldeaufgabe laufen; Dateien 15 s, Git 60 s | Erfüllt im dokumentierten Beobachtungsumfang |
| Reale hybride Reviews aus der Oberfläche | Terra/Sol konfiguriert; dauerhafter Reviewprozess nicht belegt | Derselbe HTTP-Auftragsweg wie der UI-Button startet Hermes/Terra und einen separaten Supervisor | Reale Läufe werden unten dokumentiert |
| Astra medium optional | Nicht Bestandteil des Snapshot-Nachweises | Auswählbarer separater Supervisor | Angebunden; keine bewiesene allgemeine Überlegenheit |
| Aktuelle Matrix aus Prüfergebnissen ableiten | Historische Matrix mit teilweise zu starken Aussagen | Live-Fakten und Quellenabweichungen sichtbar; Status/next_step bleiben Planungsbasis | Teilweise; verbindliche Ergebnisübernahme fehlt |
| Optimale nächste Schritte | Beschreibende Projektpläne | Terra erzeugt Vorschläge; Supervisor prüft sie; Ausgabe derzeit als JSON im Auftrag | Teilweise; kein belastbar optimierter Ablaufplan |
| Aktuelle Betreiberfreigaben berücksichtigen | Historische Pausen-/Freigabedokumente | Neue Chatfreigabe wird nicht automatisch als aktuelle Autorität in Modellkontext übernommen | Offen; kann unnötige BLOCK-Empfehlungen verursachen |
| Permanente semantische Neubewertung | Nicht nachgewiesen | Begrenzter Automatikmodus vorhanden, derzeit aus; lokale Überwachung an | Noch nicht aktiviert oder als Dauerbetrieb abgenommen |
| Schritte ohne Copy/Paste ausführen | Manuelle Bedienung | Fest definierte Aktionen: Aktualisieren, Review, Modell-/Hermesprüfung, RadiWorks-Tests | Teilweise; keine beliebigen Implementierungs-, Commit- oder Migrationsaufträge |
| Projektgedächtnis bearbeiten | Vorhandene Dateien | Editor mit Hashprüfung, Konfliktschutz und Sicherung | Implementiert und zuvor isoliert getestet |
| Weitere Module integrieren | Noch keine Prototypen | Planungsobjekte mit Abhängigkeiten erfassbar | Planung möglich; Implementierung/Integration fehlt |
| Auf anderen Windows-PCs installieren | Keine geprüfte portable Oberfläche | Paket, Anleitung, separate lokale Installationsprüfung | Lokal geprüft; anderer physischer PC noch nicht abgenommen |

## Projektstände gegen die heutige historische Matrix

Die fünf aktuellen HEADs stimmen mit der vorausgegangenen Bestandsprüfung überein. `goals.json` und `governor_manifest.json` sind weiterhin byteidentisch zu den Snapshot-Kopien. Das macht widersprüchliche Aussagen innerhalb dieser Dokumente nicht automatisch richtig.

| Projekt | Historische Matrix | Aktuell belegbar | Nächster fachlicher Rahmen |
|---|---|---|---|
| Aurelia | Wartend; Ground Zero | HEAD `8706186`; Ground-Zero-Abnahme nicht nachgewiesen; keine getrackte Änderung beobachtet | Ground-Zero-/Restore-Nachweise klären; Adapter bleiben gesperrt |
| RadiWorks | Bereit; 203 Tests; Persistenz aktiv | HEAD `866f521`; bereits zuvor tatsächlich 205 Tests erfolgreich, UI-WIP vorhanden; keine daraus folgende Integrationsfreigabe | Lesenden ABI-/Contract-Intake priorisieren; technische Integration erst nach den eigenen und Aurelia-Gates |
| Modul_Templates | Gesperrtes Planungsdokument | HEAD `041ae65`; sechs Vertrags-/Übergabedateien verändert; goals.json sagt Pending_Sync, Snapshot gesperrt | Vertragsautorität und maßgeblichen Status klären |
| Radi144 | Gesichert; Gedächtnisse in Git geschützt | HEAD `b8ac33`; beide Gedächtnisse staged, nicht in HEAD; unabhängige Checkpoint-Abnahme nicht nachgewiesen | Checkpoint und Reviewnachweise prüfen; Staging nicht als abgeschlossenen Commit ausweisen |
| morphic_v1 | Option-B abgeschlossen; G0 Authority Freeze offen | HEAD `151e2bb` im korrekten Worktree; dokumentierter Scan bestätigt denselben Rahmen; keine vollständige Laufzeitprüfung | Lesende Authority-Freeze-Matrix als nächsten getrennten Schritt behandeln |

## Erkannte Grenzen der Modellzusammenarbeit

Der erste reale Sol-Lauf korrigiert Terra: unterschiedliche Formulierungen bei Aurelia und Morphic sind nicht bereits sachliche Widersprüche. Das ist ein konkreter Nutzen der zweiten Prüfung.

Gleichzeitig werden historische Dokumente teilweise überbewertet. Die Snapshot-Pause ist kein Beweis einer weiterhin gültigen Pause, nachdem der Betreiber ausdrücklich die Fortsetzung und diesen Review erlaubt hat. Auch `approval_granted=false` soll bedeuten, dass ein Modell kein GO erteilt; daraus darf nicht abgeleitet werden, dass der Betreiber niemals einen lesenden Review erlaubt hat. Diese Unterscheidung fehlt im aktuellen Modellkontext.

Die einfache Projektabhängigkeit RadiWorks → Aurelia unterscheidet nicht zwischen dem vorgezogenen lesenden Contract-Intake und der erst später erlaubten technischen Integration. Sie benötigt eine Zuordnung zu konkreten Schritten/Gates. Ebenso ist die Änderung von 203 auf 205 Testfälle zunächst eine Differenz zwischen einem historischen und einem neueren Nachweis, kein Beweis eines fachlichen Fehlers.

Deshalb lautet die Bewertung: technisch lauffähig, praktisch für Beobachtung und beratende Reviews nutzbar, noch nicht als autonome, präzise Gesamtprojektsteuerung abgenommen. Vor deren Aktivierung sind aktuelle Betreiberentscheidungen, Schritt-Abhängigkeiten und eine nachvollziehbare Übernahme von Reviewbefunden in die Matrix zu ergänzen.

## Nachweise

Beide echten Läufe sind abgeschlossen und im UI-Auftragsjournal sichtbar:

| Kombination (jeweils medium) | Zeitfenster MESZ | Ergebnis | Quellen nach Lauf |
|---|---|---|---|
| Hermes/Terra → Sol | 23:19:13–23:21:11 | Technisch erfolgreich; Supervisor BLOCK für Implementierungsfreigabe | Unverändert, stale=false |
| Hermes/Terra → Astra | 23:22:08–23:23:13 | Technisch erfolgreich; Supervisor BLOCK für Implementierungsfreigabe | Unverändert, stale=false |

Beide Läufe verwenden den Quellenfingerprint `cabe8add9b0be8365a44dfe97f143c4ad3d2f94d86192e1086e9ceb46b426544`. Hermes meldet jeweils genau einen API-Aufruf und null Werkzeuge; die Antwortmetadaten bestätigen die angeforderten Modellnamen. Terra wurde je Vergleich neu aufgerufen, weshalb die vorgeschlagenen Pläne nicht wortgleich sind. Das ist kein kontrollierter Benchmark mit identischem Supervisor-Prompt.

Astra qualifiziert die 203/205-Differenz ausdrücklich als möglichen Unterschied von Zeitstand und Prüfumfang und erkennt fehlende konkrete Contract-Intake-Schritte. Sol korrigiert insbesondere die übertriebene Widerspruchsbehauptung bei Aurelia/Morphic, übernimmt aber die historische Pause zu stark. Beide Prüfungen sind nützlich; zwei Einzelläufe beweisen keine optimale Modellkombination. Die Empfehlung bleibt, Sol als vorhandenen Standard beizubehalten und Astra für zusätzliche Gegenprüfung zu nutzen, bis die Kontext-/Autoritätslücken geschlossen und mehr vergleichbare Fälle bewertet wurden.

- `artifacts/real-review-sol.json`: realer Auftragsbericht mit Plan, Gegenprüfung, Modellmetadaten und Quellenbindung.
- `artifacts/real-review-astra.json`: zweiter realer Auftragsbericht auf demselben Quellenfingerprint.
- Die zuvor dokumentierten 58 Anwendungstests und 205 RadiWorks-Tests sind Nachweise des vorherigen Implementierungsdurchlaufs; sie wurden für diesen reinen Statusbericht nicht erneut ausgeführt.
- An dieser Prüfung wurden keine Produktdateien oder Projektfreigaben verändert.
