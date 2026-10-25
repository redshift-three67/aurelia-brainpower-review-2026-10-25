# RadiWorks – Speicherzulassung: begrenzter Quellabgleich

Stand: 16.10.2026. Fortsetzung des vorhandenen Security-Befundberichts; ausschließlich Quellprüfung im unabhängigen Pilotcheckout. Kein Produktpatch, kein geschlossener Security-Befund, keine Lastprobe und keine Kapazitätszusage. Die [Umgebungszuordnung](../AURELIA_MANDANTEN_KAPAZITAET_2026-10-16.md) bleibt maßgeblich: begrenzte Teilprüfungen auf dem VPS, vollständige Plattformabnahme auf dem bereitgestellten Hauptserver.

## Nachgewiesene Schreib- und Annahmegrenzen

Quellbasis: `runtime/rw-pilot-session-fix-20261016/engine/src/radiworks/`. Zeilen beziehen sich ausschließlich auf die unten hashgebundenen Dateien.

| Bereich | Beobachtung im gelesenen Pfad | Für den folgenden Schutzblock erhalten bzw. berücksichtigen |
|---|---|---|
| Atomisches JSON | `persistence.py:52–73`: temporäre Datei im Zielverzeichnis, vollständige JSON-Ausgabe, Datei-fsync, replace, Verzeichnis-fsync best effort, temporäre Bereinigung. Kein Platzbudget in dieser Funktion. | Vorübergehend existieren alte und neue Datei nebeneinander. Ein Budget nur für die Nettozunahme unterschätzt diesen Schreibbedarf. Atomarer Dateiaustausch allein ist keine reservierte Speicherplatzgarantie. |
| Mehrdatei-Recovery | `persistence.py:100–112`: vorbereitetes Recovery-Dokument vor Beginn der Zieländerungen; ausstehender Marker sperrt weitere Operation. Weitere Phasen hier nicht vollständig erneut geprüft. | Recovery-Marker und Wiederherstellung benötigen eigenes Schreibbudget. Keine pauschale Sperre aller Schreibvorgänge bei knappen Ressourcen und keine Behauptung einer vollständigen Recovery-Abnahme aus diesem Ausschnitt. |
| Einzel-Broadcast | `core/broadcast.py:247–302`: Eingabeprüfung, Provider-/Emittervorbereitung vor Queue-Lock; Annahmebeleg, Entropiecheckpoint, Queueaufnahme und Threadstart innerhalb des Locks; Fehler entfernt Queueeintrag und versucht Abbruchbeleg. | Ablehnung muss auch vor teurer Vorbereitung greifen. Nach begonnener Persistenz vorhandene Abbruch-/Recovery-Reihenfolge erhalten. Keine bereits verbrauchte Entropie still neu erzeugen. |
| Broadcast-Batch | `core/broadcast.py:339–378`: vorbereitete Elemente und Sequenzen; Annahmebelege, Checkpoints und Queueaufnahme; Fehlerpfad mit Abbruchbelegen. | Gesamtmenge und Gesamtbytes vor vollständiger Materialisierung begrenzen; ein gemeinsames Zulassungs-/Reservierungsverfahren für Einzel- und Batchpfad vorsehen. Keine Teilannahme als erfolgreiche vollständige Annahme melden. |
| Annahmebeleg | `core/broadcast_target.py:226–244`: Präsentationsbeleg auflösen, validieren, vollständigen Annahmebeleg atomisch schreiben, erst danach indexieren. | Ziel-, Scope-, Präsentations- und Digestbindung erhalten. Budget umfasst den tatsächlichen serialisierten Beleg einschließlich aufgelöster Präsentation. |
| Entropie und Abschluss | `core/broadcast_target.py:201–224,246–269`: Entropiecheckpoint atomisch vor Speicherübernahme; Endstatus wird separat gespeichert. `main.py:163–176` verbindet diese Methoden mit dem Manager. | Annahmebudget allein reicht nicht: laufende Jobs brauchen Platz für weitere Checkpoints und Abschluss-/Abbruchstatus. Terminalbelege dürfen durch eine allgemeine Neuarbeitssperre nicht ausgeschlossen werden. |
| Bildablage | `core/context_images.py:83–100`: PNG-Prüfung, inhaltsadressierter Pfad, bei vorhandenem Bild Bytevergleich und Rückgabe, sonst temporäre Datei mit fsync/replace. Einzelbildgrenze 5.000.000 Bytes vorhanden. | Bereits identische Bilddaten nicht erneut als zusätzliche gespeicherte Nutzdaten zählen; parallele Uploads und temporäre Dateien dennoch berücksichtigen. Einzelbildgrenze ersetzt kein Gesamtbudget. |
| Stick-Pad | `core/stickpad.py:108–114,140–160`: neue Positionsliste, gesamtes Dokument vor Speicherübernahme schreiben; Clear schreibt ebenfalls. Originalmodus erfasst Zeit/Seeds vor diesem Commit. | Ablehnung vor zusätzlicher Aufnahme planen; bestehenden Zustand und ursprüngliche Zeit-/Seedbindung bewahren. Auch Clear ist kein schreibfreier Notausgang. Ein fehlgeschlagener Commit darf nicht als gespeicherte Position gelten. |

Diese Prüfung bestätigt Reihenfolgen im gelesenen Code. Sie beweist weder Freiheit von Race Conditions noch tatsächlich funktionierende Platzreserven oder bestandene ENOSPC-/Crashprüfungen.

## Konsequenzen für den nächsten Prüf- und Implementierungsblock

1. Neue Arbeit und notwendige Fortschritts-/Abschluss-/Recovery-Schreibvorgänge getrennt bilanzieren. Bei knappem Budget neue Arbeit verständlich ablehnen; vorhandene Historien nicht automatisch löschen oder kürzen.
2. Dateisystem-Freiraum, Ressourcenbudget der Anwendung, laufende Reservierungen und temporären Spitzenbedarf gemeinsam berücksichtigen. Ein freier Platzwert vor einem Write reserviert keine Bytes; ein einzelner Prozess-Lock schützt nicht vor anderen Schreibern auf demselben Dateisystem.
3. Endliche Eingabe-/Queue-/Positions- und Bytegrenzen vor teurer Materialisierung prüfen. Konkrete Standardwerte, Bilanzierungsumfang, Freigabe nach Fehler/Neustart und alle betroffenen Aufrufer sind vor Aktivierung festzulegen. Aus den 25 geplanten Nutzern oder den 128 GB Beispiel-RAM werden keine Grenzwerte abgeleitet.
4. Kleine isolierte Linux-Prüfungen vorbereiten: Grenze minus/equal/plus, gemeinsame Einzel-/Batchzulassung, identische/parallele Bilder, fehlgeschlagenes Schreiben/replace, Fehler nach Annahme vor Queueaufnahme, Abbruch-/Checkpointbedarf bei gesperrter Neuarbeit, Neustart mit ausstehender Recovery. Datei- und Beleginhalte sowie Seeds, Reihenfolge und Status nachweisen. Keine echte Testhost-Partition füllen.
5. Erst danach begrenzte Modul-Langlauf-/Wachstumsmessungen. Vollständige Mehrmandanten-/25-Nutzer-/Mehrmodullast bleibt Teil der späteren Hauptserverabnahme.

Offen: vollständiger Aufrufer-/Transaktionsabgleich außerhalb dieser sechs Dateien, fachlich passende Grenzwerte/Reserve, Implementierung und gezielte Linux-Regression. Entropiepuffer, Kataloge, Skript-Arbeitsbudgets und WebSocket-Zulassung bleiben im vorhandenen [Security-Bericht](AURELIA_RW_SECURITY_REVIEW_2026-10-16.md) erfasst; dieser Teilabgleich schließt sie nicht ab. Keine Änderung der Algorithmen, Windows-Liveinstanzen, Serverbudgets, Module_Templates oder GitHub-Stände.

## Herkunft der gelesenen Dateien

| Relativer Pfad unter `engine/src/radiworks/` | SHA-256 |
|---|---|
| `persistence.py` | `83e89d63bb58ee4e949a3a5f86bc99e95efd16c635465789a7f9315e538149c6` |
| `core/broadcast.py` | `679a34e95df2a11475c0b07fb32b2051e932345802f48033ee69d0a98d2d2f04` |
| `core/broadcast_target.py` | `4023fe0d73881e358bfde26cc1353c39dea9668eaceb8be4430f41715442d6ea` |
| `core/context_images.py` | `935f2fbab786efa84590b3698869d5c6a002a20ca732ed4180a5a293dafb3c87` |
| `core/stickpad.py` | `808302be39d5bfc9011eb7c4b6ad6a225b67384a375c0301a609792b665cfecd` |
| `main.py` | `3cef9e3bdfeebb2a7e2b79850678e2d632b7b346c50952e80a73eccd232571d2` |
