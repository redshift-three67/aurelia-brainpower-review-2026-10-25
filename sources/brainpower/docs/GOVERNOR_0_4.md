# Governor 0.4: Rückfragen, Darstellung und kontrollierte Pilotübernahme

Diese Erweiterung führt den freigegebenen Plan A–D fort. Die allgemeine Steuerung und Umsetzung der fünf Produktprojekte ist damit noch nicht vollständig umgesetzt. Die vorhandenen Projektgates bleiben bestehen. Das vollständige Windows-Erstinstallationspaket folgt ausdrücklich erst nach der funktionalen Gesamtabnahme.

## Bedienung

Oben rechts lässt sich die Darstellung auf **Hell**, **Dunkel** oder **System** stellen. Die Auswahl bleibt im Browser gespeichert. System folgt dessen Betriebssystemeinstellung. Ohne verfügbaren Browserspeicher funktioniert die Auswahl für die laufende Seite.

Benötigt Terra während einer bereichsgebundenen Planung oder eines Pilot-Änderungsvorschlags eine Klärung, prüft der gewählte Supervisor zuerst die Frage. Nur eine relevante Frage ohne offene Sperrgründe erzeugt **Wartet auf deine Antwort**. Der Antwortbereich erscheint oberhalb der Matrix. Er nennt Projekt oder Gruppe, Auftrag, Frage, Grund und Supervisor. Fragen bleiben im lokalen Journal über einen Dienstneustart erhalten; sie belegen keinen laufenden Terminalprozess.

Nach **Antwort senden** prüft der Dienst zunächst die Quellen. Terra und der ausgewählte Supervisor müssen anschließend unabhängig bestätigen, dass die Antwort den vorhandenen Umfang nur klärt. Erst dann wird derselbe Auftrag mit derselben ID fortgesetzt. Neue Anforderungen, zusätzliche Dateien, veränderte Testkriterien oder unklare Auswirkungen führen zu **Neue Prüfung erforderlich**. Eine Antwort erteilt keine neue Produktfreigabe. Eine verworfene Antwort bleibt als Nachweis erhalten.

Es gibt höchstens drei Rückfragen pro Auftrag und maximal 4.000 Zeichen je Antwort. Während des Wartens bleibt der einzige Worker frei. Antwortentwürfe bleiben bei Live-Aktualisierungen und fehlgeschlagener Übermittlung in der geöffneten Seite erhalten. Ein Neuladen erhält die gespeicherte Frage, aber keinen noch nicht gesendeten Browserentwurf. Ein ausdrücklich abgebrochener Auftrag verwirft seinen Entwurf. Antwortprüfungen verursachen zusätzliche Modellaufrufe; es gibt keinen stillen Supervisorwechsel.

## Kontrollierte Rückübernahme im begrenzten Pilot

Voraussetzung ist ein aktives, unabhängiges Single-Projekt in einer ausdrücklich konfigurierten `staging_pilot_roots`-Liste. Gruppierte Projekte sowie die historischen fünf Produkte und überlappende Produktwurzeln sind ausgeschlossen. Der heutige Hauptbetrieb hat keine solche Pilotwurzel freigegeben. Eine allgemeine Projektfreigabe entsteht durch diese Softwarefunktion nicht.

1. Eine aktuelle quellengebundene Planauswahl bezeichnet den konkreten unabhängigen Änderungsschritt.
2. Terra und Supervisor prüfen einen Änderungsvorschlag. Die Änderungen entstehen in einer separaten, versiegelten Arbeitskopie.
3. Der eingeschränkte Standardbibliothek-unittest-Lauf und der unabhängige Nachreview müssen tatsächlich erfolgreich sein. Null Tests oder ausschließlich übersprungene Tests reichen nicht.
4. **Rückübernahme vorbereiten** erzeugt einen unveränderlich referenzierten Vorschlag. Zielordner, konkrete Dateien, Vorher-/Nachherhashes, vollständiger Diff und Testreferenz werden angezeigt. Noch wird keine Originaldatei verändert.
5. **Diese Änderungen im Pilotprojekt übernehmen** erteilt eine gesonderte Freigabe für genau diesen Vorschlag. Der einzige Worker prüft Hash, Quellen, aktuelle Planauswahl, Projektzuordnung und Testbeleg erneut, sichert die alten Bytes und übernimmt ausschließlich die angezeigten Änderungen.
6. Der Transaktionsbeleg ermöglicht **Eigene Pilotänderungen zurücknehmen**. Zwischenzeitliche fremde Änderungen sperren die Rücknahme. Nach einer Übernahme ist ein neuer Review erforderlich; keine Schrittfolge startet automatisch.

Die Dateien müssen in bereits vorhandenen Elternverzeichnissen liegen. Es gibt keine automatische Verzeichnisanlage, Löschpatches, Git-Commits, Migration oder Installation. Mehrere Dateien werden nicht als eine atomare Dateisystemtransaktion geschrieben. Bei erkannten Teilfehlern versucht der Dienst nur eigene Änderungen zurückzunehmen. Ein harter Prozessabbruch hinterlässt eine dauerhafte Sperre und benötigt eine gesonderte Wiederherstellungsprüfung; der Auftrag wird nicht automatisch wiederholt. Python-Auditbeschränkungen sind keine Betriebssystem-Sandbox gegen feindlichen nativen Code.

## Entwicklervertrag

Produktionsabhängigkeiten bleiben Python-Standardbibliothek und Vanilla-JavaScript/CSS. `theme.js` wird vor dem Stylesheet geladen. Alle Schreibendpunkte behalten Host-, Origin-, Session- und CSRF-Prüfungen. Es gibt weiterhin einen Worker.

| Schnittstelle | Exakter Inhalt | Wirkung |
|---|---|---|
| `POST /api/questions/answer` | `question_id`, `answer`, `scope_hash` | Antwort atomar speichern, denselben Auftrag für hybride Umfangsprüfung einreihen |
| `POST /api/jobs/cancel` | `id` | Laufenden Auftrag abbrechen oder wartende Frage dauerhaft schließen |
| `POST /api/pilot/prepare` | `verified_test_job_id` | Vorbereitung als Auftrag; keine Produktdatei schreiben |
| `POST /api/pilot/apply` | `proposal_id`, `proposal_hash` | Explizite, gebundene Übernahme über den Worker |
| `POST /api/pilot/rollback` | `transaction_id` | Konfliktgeprüfte Rücknahme eigener Pilotänderungen |

`operator_questions.py` speichert offene und unveränderliche beantwortete/abgebrochene Fragen in SQLite. `question_llm.py` trennt Frageprüfung von der unabhängigen Antwortprüfung beider Rollen. Strukturierte Antworten mit doppelten JSON-Feldern werden verworfen. Bei Patchfragen werden zusätzlich die exakten Hashes sämtlicher ausgewählter Dateien einschließlich nicht vorhandener und ungetrackter Dateien gebunden und vor Fortsetzung erneut geprüft.

`pilot_actions.py` bindet die Ausführung an aktuelle Registeridentität, Planrevision, Dateiumfang und tatsächlichen Testnachweis. `pilot_apply.py` hält Vorschlag, Transaktionsanspruch, Sicherungen und Wiederherstellungsstatus fest. Eine bereits beanspruchte Arbeitskopie wird nicht erneut ausgeführt. Ein neuer Vorschlag für dieselbe Arbeitskopie umgeht diese Sperre nicht.

## Weiterhin offene Arbeit

Der vollständige hybride Gruppenabgleich mit bestätigter Strategieübernahme, allgemeine Ausführungsfreigaben für Produktprojekte, begrenzte Reparaturschleifen, Fortschrittsführung und genehmigte Schrittfolgen, allgemeine Live-Testadapter, Vault-Rückspiegelung und ein leerer Erststart benötigen weitere Umsetzung und Abnahme. Sie dürfen nicht aus den erfolgreichen Pilotnachweisen abgeleitet werden. Der vollständige Windows-Bootstrap installiert künftig unterstützte Voraussetzungen soweit möglich; CC Switch V3 bleibt ausgenommen. Das vorhandene portable ZIP bleibt zunächst ein Quellpaket mit Dienst, Oberfläche und einfachen Einrichtungsskripten.
