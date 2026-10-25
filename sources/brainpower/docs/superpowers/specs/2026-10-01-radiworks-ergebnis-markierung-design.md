# RadiWorks: Erklärung der markierten Analysezeilen

Stand: 01.10.2026. Der Betreiber wählte eine kurze Erklärung über dem Analyseergebnis und ein sichtbares „W“ je farblich markierter Zeile. Nur der getrennte RadiWorks-Kandidat auf Port 8103 wird verändert.

## Bestehende Bedeutung

`recurrenceWords(rates)` zählt durch Leerzeichen getrennte Textteile mit mindestens drei Zeichen in den Ratenbezeichnungen **des ganzen Analyseergebnisses**; darunter können auch Zahlenblöcke sein. Eine Zeile erhält `row-recurrence`, wenn mindestens einer ihrer Textteile mehr als einmal vorkommt, auch innerhalb einer einzigen Bezeichnung. Die Einfärbung ist daher eine Wiederholungs-Texthilfe. Sie bewertet weder General Vitality (GV), HIT, Wirksamkeit noch eine Diagnose. Ein Ergebnis kann auch ohne markierte Zeilen vorliegen.

## Bestätigte Darstellung

Über der Tabelle steht bei vorhandenem Ergebnis: „**W = Wiederholung:** Mindestens ein Wort oder Zahlenblock ab drei Zeichen kommt in den Ratenbezeichnungen dieses Analyseergebnisses mehrfach vor, auch über Seitengrenzen hinweg. Die Markierung ist eine Texthilfe; sie bewertet weder GV/HIT noch Wirksamkeit oder Diagnosen.“ Jede bisher gefärbte Zeile erhält unmittelbar bei der Ratenbezeichnung ein sichtbares, textlich zugängliches „W“ mit zugänglicher Bezeichnung „Wiederholung in Ratenbezeichnung“. Farbe und Zählalgorithmus bleiben unverändert. Bei leerem Ergebnis sind Hinweis und Marker verborgen.

## Grenze und Nachweis

Es gibt keine Änderung an Analyse, GV-Runde, Auto-Modus, Fallpersistenz oder Broadcast. Ein isolierter Browserlauf mit künstlichen Daten muss zeigen: vor der Analyse kein Hinweis, danach sichtbarer Hinweis; Zahl der W-Marker entspricht der Zahl gefärbter Zeilen; nicht markierte Zeilen erhalten keinen Marker. JS-Syntax und vorhandene funktionale Browserpfade bleiben gültig. Die Bedienfrage zur Wiederholung der 21er-GV-Runde bei Auto AN wird separat bewertet und ist kein Teil dieser Änderung.
