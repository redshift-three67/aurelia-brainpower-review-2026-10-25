# Hermes: Entscheidungsvorlage und Pause, 24.09.2026

## Auftrag und heutige Grenze

Heute persönlicher Wiederherstellungspunkt, Bestandsanalyse und Übergabe; keine Funktionsänderung, Migration oder Veröffentlichung. Morgen zuerst den gemeinsamen Plan erstellen, danach die drei Abschlussblöcke abarbeiten. Anschließend gemeinsam über Aurelia-Module und Matrix entscheiden. Empfehlungen unten sind keine bereits umgesetzten Eigenschaften oder pauschalen Produktfreigaben.

## Empfehlung: zunächst Windows als Steuerungsrechner

Hermes/Governor zunächst unter Windows vervollständigen. Aurelia über WireGuard/SSH als getrenntes Ausführungsziel anbinden und die dafür vorgesehenen Adapter gezielt abnehmen. Diese Empfehlung besagt nicht, dass beliebige entfernte Arbeitsabläufe bereits unterstützt werden.

Eine Dateikopie auf Linux wäre möglich; eine unveränderte, vollständig funktionsgleiche Übertragung ist derzeit nicht nachgewiesen. Konkrete Bindungen: Windows-Start-/Stoppskripte, Windows-Jobobjekte in `governor_workbench/process_tree.py`, abweichende Prozessbeendigung in `jobs.py`, Windows-Unterstützungsprüfung in `runtime_profiles.py`, `.exe`- und `venv/Scripts`-Erwartungen in `hermes.py`. Absolute Pfade und an Quellen gebundene Freigaben müssen nach einem Umzug neu geprüft werden. Python als Implementierungssprache allein beseitigt diese Abhängigkeiten nicht.

Der bisher geprüfte Aurelia-Server läuft mit Ubuntu 24.04.5 LTS, nicht mit der Distribution Debian. Diese Vorlage versteht „Debian-Server“ als diesen vorhandenen Linux-Server. Bei einem anderen Ziel ist vor einer Migration dessen Identität und Plattform zu klären.

Vorteil jetzt: bestehende Bedienung und lokale Modellanbindung bleiben nutzbar, während die Linux-Ausführung schrittweise überprüft wird. Einschränkung: Bei ausgeschaltetem Windows-PC läuft die lokale Steuerung nicht weiter. Bereits eigenständig eingerichtete Server-Sicherungsdienste sind davon unabhängig. Ein späterer ständig verfügbarer Linux-Controller wäre ein separates Portierungs- und Abnahmepaket. Governor bleibt zunächst auf Loopback; kein öffentlich freigegebener Steuerungsport.

Codex unterstützt entfernte Projekte über SSH; das ersetzt keine Portierung der eigenen Anwendung. Offizielle Dokumentation: https://learn.chatgpt.com/docs/remote-connections . Codex-Anmeldung und Laufzeit auf dem Ziel sind gesonderte Voraussetzungen.

## Drei Abschlussblöcke ab morgen

1. Iststand und konkrete Funktionslücken mit `HERMES_APP_ABSCHLUSS.md` abgleichen; nachvollziehbare Abnahmekriterien für die unterstützten Arbeitsabläufe festlegen. Bestehende begrenzte Pilot-/Testketten nicht als universelle Projektumsetzung ausgeben.
2. RH-1: Modell-/Reasoning-Auswahl konsistent durch Oberfläche, Konfiguration, Aufträge und Hermes-Anbindung führen. Aktuell bestehen Medium-Bindungen in Konfiguration und Hermes-Anbindung. Start und verifizierten Abschluss ausdrücklich melden; Nullwerkzeug-Eigenschaft erneut prüfen. Keine stillen Modellwechsel oder automatischen Reviews.
3. Durchgängige Abnahme von Registrierung/Anforderungen über Planung, Prüfung und ausdrückliche Ausführung bis Ergebnis, Abbruch und Wiederaufnahme. Konkrete Adapter und Windows-Erststart prüfen; Umfang morgen festlegen. Produkt-/Deploymentfreigaben bleiben eigene Entscheidungen.

## Eigenständige Projekte und Gruppenmatrix

Die Grundlagen existieren in `registry.py`, `scopes.py` und der Projektauswahl: eigenständige Projekte, Gruppenmitglieder, begrenzte Kontexte und gebundene Nachweise. Die Anwendung teilt jedoch Konfiguration, Journal und einen Worker; dies ist keine Betriebssystem-Isolation fremden Codes. Gruppenmitgliedschaft ist derzeit dauerhaft und ein Projekt gehört höchstens einer Gruppe an. Ein beliebiger späterer Wechsel der Mitgliedschaft ist deshalb keine vorhandene Funktion. Registrierung eines bestehenden Verzeichnisses ist außerdem nicht gleich vollständige Projektneuanlage.

Für die gewünschte Nutzung empfehlen wir getrennte Projektwurzeln und eindeutig zugeordnete Anforderungen, Dateien, Pläne, Speicher, Aufträge, Freigaben und Ergebnisse. Eine Gruppenmatrix darf nur ausdrücklich zugeordnete Mitglieder zusammenführen. Beim Umschalten darf ein Auftrag weder Ziel noch Berechtigung wechseln. Abnahme insbesondere für A→B während eines Auftrags, verspätete UI-Antworten, offene Entwürfe, Neustart und gruppenfremde Quellen. Vorhandene Tests wurden als Quelltext untersucht; heute wurde keine neue funktionale Gesamtabnahme ausgeführt.

## Verteilung auf weitere Windows-PCs

Zuerst eine saubere projektlose Windows-Ausgabe mit geführter Einrichtung und Diagnose, anschließend bei Bedarf ein Installer um dieselbe Ausgabe. Kein eigener paralleler Produktzweig. Eigene Anmeldung und notwendige Laufzeiten/Modellanbindungen auf jedem PC bleiben erforderlich; keine Übernahme von Zugangsdaten, Auth-Dateien oder persönlichen Chat-Sitzungen.

`tools/build_release.py` und `scripts/Install-Windows.ps1` sind Ausgangspunkte, aber noch kein abgenommenes neutrales Komplettpaket: `config.example.json` enthält fünf konkrete Projekte und persönliche Pfadvorgaben, der ZIP-Bau nimmt den Dokumentationsordner breit mit. Für eine saubere Ausgabe sind leere Projektregistry, neutrale Standardwerte, gezielte Dokumentauswahl und Ausschluss persönlicher Laufzeit-/Projekt-/Serverdaten nötig. Der bestehende Installer erwartet Python und richtet nicht automatisch die vollständige externe Hermes-/Router-/Anmeldeumgebung ein.

Abnahme auf sauberem Windows-Profil/PC: Erststart, eigene Anmeldung, neues leeres Projekt, Kernablauf, Neustart, Update und sichere Erhaltung der Nutzerdaten. Ein vollständiger Installer ist realistisch, aber erst nach dieser Abnahme belastbar. Ein anderes Codex kann den Quellstand mit Dokumentation weiterbearbeiten; identische Funktionen entstehen durch korrekte Anwendungseinrichtung, nicht durch Kopieren einer Codex-Sitzung.

## Kleine Verbesserungen der Benutzerführung

Bestehendes Layout erhalten. Aktives Projekt bzw. aktive Gruppe dauerhaft sichtbar; eine kurze Schrittanzeige und genau eine hervorgehobene nächste zulässige Aktion. Blau für nächste Aktion, Grün für nachgewiesenen Abschluss, Gelb für offene Eingabe/Prüfung, Grau für derzeit gesperrt mit Begründung, Rot für Fehler/destruktive Handlung. Immer Text/Symbol zusätzlich zur Farbe und erkennbare Tastaturbedienung.

Schrittstatus aus bestehenden Fachzuständen ableiten, keine eigene widersprüchliche UI-Freigabelogik. Keine automatische Zustimmung. Dadurch bleibt der Eingriff begrenzt; ein universeller neuer Assistent wäre ein größerer separater Umfang. Neue Single-/Gruppenprojekte, Wechsel und Wiederaufnahme gemeinsam mit den Kernabläufen testen.

## Serverübergabe

Begrenzte Belastung und bisherige Betriebsnachweise: `SERVER_ABSCHLUSSBERICHT_2026-09-23.md`, Einstieg `SERVER_AKTUELL.md`. Nicht wiederholen. Offen bleiben ECC-Nachweis, Secure-Boot-/Installationsabweichung, Nachweis des ersten geplanten Retentionlaufs, Online-Backup vor laufender produktiver DB und vollständiger Wiederanlauf-/Datenverlustnachweis für die 12-Stunden-Ziele. Rescue, zweite Sicherungskopie und externe Ausfallüberwachung wurden ausdrücklich zurückgestellt. USV/KVM nach Betreiber-/Providerangabe abgesichert. Vor produktiver Aurelia-Übernahme diese Punkte erneut vorlegen; lokale Hermes-Fertigstellung kann vorher fortgesetzt werden.

## Wiederherstellungspunkt und Pause

`checkpoints/Hermes-20260924-Pause`: persönlicher lokaler Anwendungsstand mit Programm, Konfiguration, SQLite-Journal, zugehörigen Laufzeitdateien und ausgewählten Serverbelegen. Governor nach bestätigten null aktiven Aufträgen regulär beendet; automatische Reviews waren aus. Er bleibt für die Pause beendet. Keine Windows-/Server-Vollsicherung, keine unabhängige zweite Kopie, kein neutrales Verteilungspaket. Externe Produktrepositories, externe Installationen und Zugangsdaten sind nicht enthalten. Prüfprotokoll und Wiederherstellungsanleitung liegen im Checkpoint.

Reasoning-Arbeitsvorgabe bleibt Medium, kein Low-Wechsel angefordert oder offen; tatsächliche UI-Einstellung nicht technisch bestätigt. Morgen zuerst diese Vorlage lesen und den Plan besprechen. Noch keine Featurearbeit und kein Serverumzug gestartet.
