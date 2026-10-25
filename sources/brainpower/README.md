# Governor Workbench

**Hermes-Route B (26.09.2026):** In der Projekt-/Gruppenaufnahme stehen zusätzlich ein beratender Review und ein Matrixplan mit **GPT-6 Sol/high → GPT-6 Luna/max** bereit. **GPT-6 Astra/medium** prüft Matrixpläne immer zusätzlich und unabhängig; bei Reviews prüft Astra nach Risikosignal oder ausdrücklicher Auswahl. Der Betreiber wählt den alten oder neuen Weg bei jedem Auftrag ausdrücklich; eine gespeicherte Standardroute je Projekt/Modul gibt es nicht. Jeder Start verlangt die vorhandene Modellversandfreigabe; Matrixplanung verlangt vollständige Aufnahme. Der bestehende Terra-/Supervisor-Weg, seine Einstellungen und automatische Reviews bleiben eigenständig. Eine Route-B-Antwort ist keine Produktfreigabe; Strategieübernahme und Ausführung bleiben separate Schritte. [Vertrag und Grenzen](docs/verification/HERMES_ROUTE_B_2026-09-24.md).

**RH-1 (24.09.2026):** Einheitliche Reasoning-Auswahl für Hermes-Aufträge: Medium als Standard, optional Auto für ausdrücklich bestätigte unabhängige Dokumentationsroutinen, High/xHigh nur manuell. Aufrufdetails zeigen Auswahl, gesendete Stufe und Grund. Einstellungen ändern nicht diesen Codex-Chat; neue Auswahl kann gebundene Aufträge/Vorschauen ungültig machen. [Prüfbericht und Grenzen](docs/verification/RH1_2026-09-24.md).

**Version 0.5:** [Quellengebundene Aufnahmeentwürfe und ausdrückliche Strategieübernahme](docs/GOVERNOR_0_5.md). Fünf lokale Entwürfe sind zur Betreiberprüfung vorbereitet; allgemeine Produktausführung und vollständige Windows-Nullinstallation bleiben offen. Die bisherige Governance-Matrix und Produktgates werden nicht durch einen Planungskandidaten ersetzt.

**Nächste Betreiberreihenfolge (25.09.2026):** Beide Hermes-Modellwege und Rollen je Projekt/Modul funktional abnehmen → RadiWorks, Radi144, `morphic_v1` und ein neues Modul mit eigenem Pfad als getrennte Prototypen vorbereiten und live prüfen → vollständigen Produkt-Matrixplan erstellen und ausdrücklich prüfen → Aurelia auf dem verifizierten Linux-Zielsystem stufenweise implementieren und integrieren, jeweils nach geltenden Gates. [Modulübergang und Nachweise](docs/MODULUEBERGANG_UND_BETREIBERPRUEFUNG.md).

**Version 0.4:** [Hell/Dunkel/System, protokollierte Rückfragen und kontrollierte Übernahme im isolierten Pilot](docs/GOVERNOR_0_4.md). Der freigegebene Gesamtplan A–D ist noch nicht vollständig umgesetzt. Die fünf historischen Produktprojekte, automatische Schrittfolgen und allgemeine Live-Abnahmen bleiben von der Pilotübernahme ausgeschlossen. Die historischen Berichte beschreiben frühere Stände.

Lokale Windows-Steuerungsoberfläche für die fünf bestehenden Projekte und zusätzliche geplante Module. Beobachtung, Dateihashes, dokumentierte Gates, Testaufträge, Hermes/Terra-Orchestrierung, unabhängiger Sol- oder Astra-Review und Gedächtnis-Editor befinden sich in einer Oberfläche.

**Start:** `Start-Governor.cmd` doppelklicken, anschließend `http://127.0.0.1:8787` im Browser. **Stop:** `Stop-Governor.cmd`. Auf einem neuen PC zuerst die [Installationsanleitung](docs/WINDOWS_INSTALLATION.md) durcharbeiten. Die Anwendung braucht zur Laufzeit Python 3.11+, Git und einen Browser; keine zusätzlichen Python-Pakete, kein Node und kein Docker.

## Was tatsächlich ausgeführt wird

- Zwei direkte abhängige Änderungen eines erlaubten unabhängigen Piloten: H0 ausdrücklich festhalten, A separat prüfen/übernehmen/abschließen, H1 separat bestätigen, danach B ausdrücklich vorschlagen und mit eigenen Tests/Review übernehmen. Historie zeigt H0/H1/H2; Rücknahme nur B vor A. Jede Rücknahme verlangt eine neue Planrevision. Keine automatische Folgeausführung und keine allgemeine Produktfreigabe; historische externe Vorgänger bleiben gesperrt. [Aktuelle Abnahme und sechs Schritte](docs/FORTSETZUNG_SECHS_SCHRITTE_2026-09-18.md).

- Ausdrücklich genehmigte reine Testketten: unter „Vorgängerketten prüfen“ zwei bis fünf ausgewählte Testschritte eines erlaubten unabhängigen Piloten vorschauen und mit Begründung starten. Der feste Python-Testadapter läuft nacheinander auf isolierten Kopien; jeder Nachfolger benötigt aktuelle Abschlussbelege. Abbruch und Historie stehen bei den Aufträgen. Keine Modelle, Originaländerungen oder Produktfreigaben durch diese Kette.

- Begrenzte genehmigte Pilot-Prüffolge: vorhandenen versiegelten Änderungsvorschlag ausdrücklich mit Begründung starten, isoliert testen und vom Supervisor prüfen lassen, anschließend lokale Nachweisprüfung. Danach zwingender Halt vor jeder Übernahme. Vorschau, Abbruch und Historie sind in „Aufträge & Ergebnisse“ verfügbar; dies ist keine allgemeine Ausführung der Projektmatrix.
- Der Governor beobachtet bekannte Quellen alle 15 Sekunden und Git alle 60 Sekunden. Er läuft auch ohne geöffneten Browser. Es werden keine ganzen Laufwerke oder großen ungetrackten Morphic-Verzeichnisbäume rekursiv durchsucht.
- Aufträge laufen nacheinander, mit Rückgabecode, Laufzeitgrenze und Protokoll. „RadiWorks-Tests“ führt den fest definierten isolierten Testlauf aus. Die Suite wurde über diesen Bedienweg mit 205 erfolgreichen Tests nachgewiesen.
- Der hybride Review nutzt standardmäßig **Hermes → GPT-5.6 Terra medium → separater GPT-5.6 Sol medium**. **GPT-6 Astra medium** ist als Supervisor auswählbar. Es handelt sich um neue Modellaufrufe mit kontrolliertem Kontext, nicht um eine Fernsteuerung des laufenden Codex-Chats.
- Die Hermes-Instanz eines Reviews hat nach geprüfter Initialisierung null Werkzeuge. Produktcode wird durch diese Version nicht automatisch verändert. Ein Review ist Beratung, kein Implementierungs-GO.
- Neue Module lassen sich als geplante Einträge mit Beschreibung und Abhängigkeiten erfassen. Dafür wird kein Prototyp und kein Ordner erfunden oder automatisch erstellt.
- Bestehende Markdown-Gedächtnisse können explizit bearbeitet werden. Die Anwendung prüft den gelesenen Hash, sichert den alten Inhalt und liest die gespeicherte Datei zur Kontrolle zurück.

## Modellaufrufe und Projektinhalte

Der Beobachtungsbetrieb sendet keine Projekttexte an Modelle. Modellprüfungen verwenden synthetische Governance-Fälle. Ein ausdrücklich gestarteter alter oder Route-B-Review liest die ausgewählten Projektgedächtnisse vor Modellversand erneut vollständig und prüft Inventar und SHA-256 gegen die Aufnahme; außerdem werden Git-/Gate-Metadaten, Governance-Quellen und gegebenenfalls passende Prüfnachweise über CC Switch übermittelt. Passt der vollständige Kontext nicht in die Reviewgrenze, lesen zwei Rollen jede Originalpassage in gebundenen Abschnitten und der Schlussreview erhält ihre begrenzten Belege mit verifizierten Originalzitaten und Dokumentgliederung. Identische Zwischenbelege dürfen nur mit identischem Quellenhash, Modell, Reasoning und Regelversion wiederverwendet werden. Die Schlussmodelle sehen in diesem Fall nicht den gesamten Rohtext; die Auftragsanzeige kennzeichnet das ausdrücklich. Fehlende Belege oder ein weiterhin zu großer Kontext stoppen ohne stille Kürzung. Der Reviewtext kann Daten außerhalb dieses PCs verarbeiten lassen. Die lokale Routeradresse bedeutet nicht, dass die Modellinferenz lokal stattfindet. [Gedächtnisprüfung und Gruppengrenze](docs/verification/HERMES_MEMORY_2026-09-25.md), [Release-Abgleich und Stufenverfahren](docs/verification/HERMES_MEMORY_STAGES_2026-09-26.md).

**Automatische Reviews sind standardmäßig aus.** Bei ihrer ausdrücklichen Aktivierung sind höchstens vier automatisch gestartete Reviews je UTC-Tag und mindestens 15 Minuten Abstand vorgesehen. Fehler zählen mit; es gibt keinen verdeckten Modellfallback. Bei unvollständiger Vergleichsevidenz startet kein automatischer Review. Auch manuelle Reviews können Kosten oder Kontingent verbrauchen.

Der Betreiber hat den Versand echter Projektinformationen, den erweiterten Vergleichskontext und am 12.09.2026 auch zukünftige automatische Reviews der bestehenden Fünfergruppe ausdrücklich erlaubt. Die während der Pause gespeicherte Abschaltung bleibt bei einem Update erhalten. Den tatsächlichen Schalterzustand zeigt die Oberfläche. Neue Installationen starten ohne automatische Modellaufrufe; neue Projekte und Vault-Quellen benötigen eine gespeicherte Versandfreigabe. Echte Kontextpakete, persönliche Entscheidungen und Reviewberichte bleiben lokal und gehören nicht zum transportablen Releasepaket.

## Dokumentation

- [Windows installieren, einrichten und wiederherstellen](docs/WINDOWS_INSTALLATION.md)
- [Governor 0.2: Bedienung und Grenzen](docs/GOVERNOR_0_2.md)
- [Verifikation Version 0.2](docs/VERIFICATION_0_2.md)
- [Entwicklerarchitektur, API und Tests](docs/DEVELOPER_GUIDE.md)
- [LLM-Betriebsvertrag](docs/LLM_OPERATING_CONTRACT.json)
- [Modellintegration und Evaluation](docs/MODEL_INTEGRATION.md)
- [Bestandsprüfung vor der Umsetzung](docs/GOVERNOR_BESTANDSPRUEFUNG_2026-09-11.md)
- [Verifikation und bekannte Grenzen](docs/VERIFICATION.md)

Die historischen Bestands- und Entwurfsdokumente beschreiben den Ausgangspunkt. Den aktuellen implementierten Funktionsumfang beschreiben diese README, die Entwickleranleitung und der Verifikationsbericht.
