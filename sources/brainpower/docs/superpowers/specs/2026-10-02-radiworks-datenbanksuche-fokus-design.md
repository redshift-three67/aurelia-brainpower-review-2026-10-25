# RadiWorks: Datenbanksuche und Fallfokus

Stand: 02.10.2026. Die bestehende Analyseberechnung und der laufende Dienst auf Port 8103 bleiben während der Entwicklung unverändert.

## Zweck und Grenze

Die 123 Katalognamen sollen in der Analyseansicht lokal durchsuchbar sein. Ein zusätzliches, optionales Feld „Fokus“ beschreibt die Fragestellung des Falls getrennt von der allgemeinen Beschreibung und der Absicht der letzten Sitzung. Der Fokus darf als ausdrücklich übernommener Suchtext die sichtbare Katalogliste eingrenzen. Er verändert weder Datenbank, Raten, Entropie, GV, Passport noch Broadcast automatisch. Eine bessere fachliche Trefferqualität wird nicht behauptet.

## Bedienung

- Die Datenbanksuche filtert die bereits geladene `/databases`-Liste nach Namen und vorhandenen Gruppennamen. Sie sendet Suchtext nicht an den Server und speichert ihn nicht in URL oder Browser-Speicher. Ein leerer Filter zeigt die volle bisherige Auswahl. Die gewählte Datenbank bleibt bis zu einer ausdrücklichen Auswahl erhalten; ein Filter darf keine Analyse auslösen.
- In „Fälle“ stehen Beschreibung und Fokus nebeneinander als getrennte Angaben. Der Fokus ist optional, begrenzt und erhält einen Hinweis zu privaten Daten und seiner Rolle als Auswahlhilfe. Der Dialog „Fall bearbeiten“ zeigt denselben Fallfokus, ohne die bestehende Sitzungsabsicht umzudeuten.
- „Fokus in Suche übernehmen“ kopiert den sichtbaren Fokus nur nach bewusstem Klick in das lokale Suchfeld. Kein Treffer wird als „passend“, „wirksam“ oder „diagnostisch“ bewertet. Ist kein Namensmatch vorhanden, bleibt die volle Auswahl über „Suche löschen“ erreichbar.

## Daten und Sicherheit

- `focus` ist ein getrenntes Feld im lokalen Falldokument. Der gezielte Metadaten-Endpunkt bewahrt unbekannte bestehende Fallfelder und schützt einen zurückgehaltenen CopyGuard-Platzhalter vor Überschreiben. Ein erwarteter, opaker Fallverweis stoppt ein Speichern nach Fallwechsel mit Konflikt statt den dann aktuellen Fall zu verändern.
- Ein neuer Analyse-Draft erhält den Fallfokus als Snapshot neben der bereits bestehenden Fall-/Absichtsangabe. Der Rechenkern und der Passport-Eingabehash bleiben unverändert. Bestehende Falldateien ohne Fokus bleiben lesbar. Fokus wird weder in Logs noch in Modellaufrufe übernommen.
- Der lexikalische CopyGuard ist keine Anonymisierung. Synthetische Tests verwenden keine Personen- oder Gesundheitsdaten. Aurelia-Host- und Mandantenfreigaben bleiben getrennt.

## Nachweise

Gezielte API-Tests prüfen Fokus speichern/laden, Fallwechsel-Konflikt, Platzhalter, fehlende Sitzung und gleiche Analysewerte bei gleicher Datenbank/Seed trotz unterschiedlichem Fokus. Ein isolierter Browsertest prüft Katalogsuche, explizite Auswahl, leere Treffer, Tastatur und den bewusst übernommenen Fokus. Danach folgen die bestehende Engine-Suite, JS-Syntax und der relevante Browser-Smoke. Port 8103 wird erst nach leerer Queue und kontrollierter Freigabe neu gestartet.
