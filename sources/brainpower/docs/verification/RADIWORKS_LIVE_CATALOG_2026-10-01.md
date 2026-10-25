# RadiWorks: Live-Katalog und lokaler Wiederanlauf am 01.10.2026

## Befund und Ursache

Die frühere Vorschau auf Port 8102 war ein isolierter Test mit künstlichen Raten und wurde nach der Prüfung ausdrücklich beendet. Am 01.10. lauschte dort vor der Diagnose kein Prozess. Deshalb schlugen Browser-Fetch und WebSocket-Verbindung fehl; das sichtbare Wechseln zwischen online und offline war ein Verbindungsproblem. Der lokale RadiWorks-Laufzeitbaum enthielt außerdem keinen originalen Ratenkatalog. Wenige künstliche Datenbanken belegen keine Regression der Analyseengine, aber auch keine Originalparität.

Das dekompilierte AetherOnePi-`DataService` lädt den Katalog aus `data/radionics` und aktualisiert ihn aus dem [separaten Entwickler-Repository](https://github.com/isuretpolos/radionics-rates). Auch der Bytecode des lokalen 2.9.0-JAR enthält diese Repository-URL und die JGit-Pfade für Pull oder Clone; das JAR enthält die Ratenlisten nicht selbst. RadiWorks lädt im gegenwärtigen Aufbau keine fremden Daten ungefragt nach; `RADIOWORKS_DATA_DIR` muss für einen realen lokalen Katalog gesetzt sein.

## Getrennter Live-Stand

| Gegenstand | Nachweis |
| --- | --- |
| Quelle | `isuretpolos/radionics-rates`, Git-Commit `0a5c475b5e6028747ba4935d4864e4a775c2698e`; 77 `.txt`-Dateien. |
| Unveränderlicher lokaler Stand | `runtime/radiworks-catalog-releases/3c052ad0e9c0417e8aa1c29515fbba4e/data`; Manifest prüfte 79 Dateien und SHA-256. Die `FUNCTION_`-Datei wird wie im Original nicht als Datenbank gezählt. |
| Getrennte Laufzeit | `runtime/radiworks-live-8102`; der bestehende Radi144-Dienst auf 8090 wurde nicht verändert. |
| Browser | `http://127.0.0.1:8102/`; sichtbarer Playwright-Lauf nach Neustart: „Live“, 76 Datenbanken plus 8 Kategorie-Auswahlen in 9 Gruppen, 0 Seiten-/Netzwerkfehler. |
| Analyse | UI-Auswahl `HOMEOPATHY_ASTERALES`, Modus `seeded`, Seed `12345`, `max_hits=100`: 105 Raten wie die vorhandene Kürzungslogik, Draft erzeugt. REST-Beleg verwendet `analysis-request-catalog-v1`. |
| Gruppierte Analyse | Der sichtbare Kategorieknopf `HOMEOPATHY` setzte den Präfix-Selektor und lieferte im Browser 105 Raten bei Live-WebSocket und ohne Seitenfehler. |
| Freigabeprobe | Auf demselben isolierten Live-Stand wurde eine zweite seeded Analyse über `draft → ready → promoted` im Browser ausgeführt. Die virtuelle Broadcast-Queue enthielt einen aktiven und einen wartenden Eintrag; `DELETE /broadcast/all` räumte sie anschließend, danach `queued=0`. Keine Hardware aktiviert. |
| Wiederanlauf | [Start-RadiWorks-Live.cmd](../../Start-RadiWorks-Live.cmd) ruft den geprüften PowerShell-Starter auf. Ein frischer Start und ein bereits laufender Dienst wurden getrennt getestet. |

Die Katalogquelle und die veröffentlichte Kopie liegen in `runtime/` und werden nicht in Git eingecheckt. Für eine Wiederherstellung auf einem anderen Rechner müssen Quell-Commit, Katalogdateien beziehungsweise ein reproduzierbarer Neuimport und das Manifest gesondert mitgenommen werden. Der Starter prüft den festgelegten lokalen Pfad und verweigert einen fremd belegten Port 8102. Er startet den Dienst gezielt, aber richtet keinen automatischen Windows-Systemstart ein.

Die dekompilierte frühere AetherOne-GUI hat sechs direkte Analyse-Kategorieschalter (`HOMEOPATHY`, `BIOLOGICAL`, `SYMBOLISM`, `ESSENCES`, `CHEMICAL`, `ENERGY`). RadiWorks zeigt diese weiterhin und ergänzt `AGRICULTURE` und `ANALYSIS`; die neunte Gruppe fasst weitere Datenbanken. Die Gruppierungsdarstellung ist daher eine Web-UI-Erweiterung. Ihre vollständige Gleichwertigkeit mit der 2.9.0-GUI ist noch nicht abgenommen.

## Grenze vor Radi144

Dies ist ein **lokaler Funktionsnachweis für Start, Katalogauswahl und eine seeded Analyse**. Er bestätigt weder vollständige AetherOnePi-2.9.0-Funktionsgleichheit noch sämtliche realen Datenbanken, Hardware, stochastische Entropie, Broadcast, Langlauf, Original-GUI-Verhalten oder die spätere Aurelia-Integration. Eigene frühere Ratenlisten des Betreibers wurden nicht ersetzt oder als identisch behauptet. Die aktuelle Paritätsmatrix belegt Java-Vergleich nur für drei synthetische seeded REST-Fixtures; reale Kataloggrößen sind darin ausdrücklich offen.

Vor dem vom Betreiber gewünschten Übergang zu Radi144: Original- und RadiWorks-Funktionsinventar auf gleicher Katalogbasis abgleichen, die bisher funktionierenden RadiWorks-Abläufe mit realem Katalog und getrennten Testfällen erneut live prüfen, Abweichungen beheben und technische wie fachliche Abnahme getrennt festhalten. Radi144 behält anschließend eigene Fachlogik, eigenen Port und eigenen Runtime-Baum; Modulreferenzen und Designvorlage sind zusätzliche Verträge, keine Ersetzung seiner Funktionen.

Governor wurde separat auf 8787 gestartet: `/health` und die Browseroberfläche antworteten, die Matrixansicht zeigte fünf bestehende Projekte und keine JavaScript-Seitenfehler. Er ist eine Status-, Quellen-, Review- und Planungsoberfläche mit Gates; ein vollständiger Aurelia-Gruppenplan und automatische Produktintegration folgen erst nach den Modulprototypen und gesonderten Entscheidungen.

Zusätzlich antworteten die zehn lesenden RadiWorks-Pfade `/ping`, `/manifest`, `/databases`, `/settings`, `/cases`, `/entropy/status`, `/stickpad`, `/analysis/sessions`, `/broadcast/queue` und `/scripts` jeweils mit HTTP 200. Dies prüft Erreichbarkeit und Antwortstatus, nicht die semantische Korrektheit jedes Pfads.
