# P3 RadiFarben – synthetische Access-Vorprobe, 11.10.2026

## Stand und Umfang

RF-E1 ist **noch nicht bestanden**. Zwei begrenzte COM-Aktivierungsversuche scheiterten mit `0x80080005 / CO_E_SERVER_EXEC_FAILURE`, bevor ein Access-Automationsobjekt oder dessen Eigentumsbindung verfügbar war. Keine Datenbankaktion wurde vom Werkzeug aufgerufen. Form/Report/Modul/Makro/AutoExec/Query, Import/Export und Positivkontrollen sind **NOT_RUN**. Ein möglicher kurzzeitiger Serverstart während COM-Aktivierung wurde nicht kontinuierlich erfasst; nach beiden Versuchen wurden keine Access-Prozesse beobachtet. Dies ist keine Originalreferenzprüfung.

Betreiberklärung: Zentraler RMF ist die aktuell höchste Version und wird weiterentwickelt. Den aktuellen Quellenstand zunächst aufnehmen; spätere Stände vor der Aurelia-Integration getrennt sichern, vergleichen und nach betroffenen Referenzprüfungen übernehmen. Menüzuordnung und Versionsverfahren stehen in Planabschnitten15/16. Keine neue Formel oder semantische Versionsnummer aus Dateiänderungen ableiten.

## Quellenaufnahme

| Nachweis | Beobachteter Stand |
|---|---|
| Neue aktuelle Byte-Referenz | `2993247b0b06e84d5897870790a54b0800d8db701e3d1f004c3c26e54675a1c9` |
| Frühere Byte-Referenz | `2b48ce8dec5e0126072e0bc24f07b754b8b64af0651b080d257dcb1b0c8f13bc` |
| Herkunfts-/Kopierbeleg | `runtime/radifarben-source-versions/RF-20261011-080657Z/SOURCE_VERSION.json` |
| Rechte und erneute Hashprüfung | `checkpoints/RadiFarben-RMF-Plan-20261011-080315Z/VERSION_VERIFY.json`: Directory-Owner, Owner/SYSTEM-FullControl und Master-Vererbung exakt rückgelesen; Original und beide Masterhashes stimmen überein, Original-Lock fehlt. |
| Unveränderlichkeit | Hashgebundene Referenz, keine WORM-Speicherung oder lückenlose Schreibsperre. Owner kann den Master schreiben; vor jeder späteren Verwendung Hash erneut prüfen. |
| Frühere technische Belege | Bleiben am alten Hash gebunden. Neuer statischer Code-/Query-/Objektvergleich weiterhin erforderlich. |

Die erste Quellenaufnahme scheiterte im Security-Cmdlet-Modulimport vor dem Schreiben einer ACCDB-Kopie. Der nächste Lauf verwendete die .NET-Verzeichnis-ACL-API nur für den neu angelegten Ordner. Keine Systemmodule oder bestehenden Berechtigungen geändert. Frühere Fehlerspur/Helperversion und korrigierte Version bleiben erhalten. Veränderte Dateibytes beweisen keine geänderten Algorithmen.

Plan-/Versionssicherung `checkpoints/RadiFarben-RMF-Plan-20261011-080315Z`: 15/15 Manifestdateien frisch geprüft, komplette ältere Wiederaufnahme erhalten. Kein F:-Gesamtbackup.

## Geplanter Ablauf und echte Beleggrenzen

| Prüfschritt | Status |
|---|---|
| Host-freie Pfad-/Reparse-/PID-/Bewertungsprüfungen | Endfassung: Worker und Root je59 bestandene Assertions, null Skips/Fehler. Drei aktive PS-Dateien geparst. Erste42-Assertion-Fassung und frühe Fehlerbelege getrennt erhalten. |
| Leere Ausgangsliste bestehender Access-PIDs | Binding-Helfer und darüberliegender Projektguard korrigiert; echtes leeres Before-Array getestet. Leere COM-Sammelliste, flache null/ein Fehler-Ausgabe und fortgesetzter Cleanup-/Quit-Ablauf mit injizierten Schritten getestet. |
| Eigene COM-Instanz und sauberes Ende | Zwei Aktivierungsversuche fehlgeschlagen; kein erworbenes COM-Objekt, keine Eigentumsbindung oder eigener Quit. Nachkontrollen: keine Access-Prozesse. Kein bestandener Readiness-Nachweis. |
| Synthetischer Import und Text-Export: Form, Report, Module, Macro, Query | Noch nicht ausgeführt. |
| Ereignis-/Timer-/AutoExec-/Query-Positivkontrollen | Noch nicht ausgeführt; gesperrte oder fehlende Kontrolle bleibt Lücke. |
| Abschließender unabhängiger SPEC→QUALITY-Review | Begrenzte statische Nachprüfung abgeschlossen: vier zusätzlichen P1-Befunde behoben, keine verbleibenden Codebefunde im geprüften Umfang. Reviewer las Tests/Receipts und verifizierte Hashes, führte keine Access-/COM-Tests aus. Keine Freigabe zum Hostlauf. |

Hostbelege `checkpoints/RadiFarben-RMF-Plan-20261011-081812Z/HOST_BEFORE.json` und `HOST_AFTER.json`: keine Access-Prozesse; acht Listener auf8103–8109/8787 mit identischen PIDs/Adressen auf127.0.0.1. Erste Sandbox-Nachlese verweigerte Listenerzugriff; ihr Nullbestand in `HOST_AFTER_SANDBOX_DENIED.json` ist kein gültiger Vergleich. Erneute genehmigte reine Leseprobe mit Fehlerabbruch erfolgreich. `SOURCE_AFTER.json` bestätigt erneut Original-/beide Masterhashes, exakt rückgelesene Rechte und fehlenden Original-Lock. Beide Readiness-Werkzeuge nach den Läufen bytegleich zu ihrem Vorherhash (`READINESS_TOOL_AFTER.json`). Keine neue HTTP-/Broadcast-Funktionsabnahme aus einer Listenerprüfung ableiten.

## Tatsächliche begrenzte Startdiagnose

| Versuch/Befund | Ergebnis und Reichweite |
|---|---|
| Geprüfter 64-Bit-Controller / PowerShell7 | COM-Klassenfactory schlägt mit80080005 fehl. Controller endet ohne Timeout; keine Prozessbeendigung versucht. `readiness/RESULT.json` und `readiness-controller.json`. |
| 32-Bit-Skript als Standardaufruf | Ausführung durch die lokale Skriptrichtlinie gesperrt, bevor der Skriptinhalt lief. Kein Ersatz durch Inlineausführung oder stillen Bypass. |
| 32-Bit-Controller / STA / explizit erlaubtes RemoteSigned | Temporäre Richtlinie nur im neuen Prozess und dessen möglichen Kindern, keine persistente Windows-Richtlinie geändert. Wieder derselbe COM-Fehler, ohne Timeout/Prozessbeendigung. `attempt-32bit/readiness/RESULT.json`. |
| COM-Registryansichten | Gleiche CLSID in32/64-Bit; LocalServer32 nur in32-Bit und dort Office14. Die CLSID-Unterschlüssel des64-Bit-Zweigs enthalten Interopregistrierung, keinen ausgelesenen Startpfad. |
| Installationsmetadaten | Office14-Datei `14.0.7256.5000` und separate Office16-Datei `16.0.20430.20146` vorhanden; versionsbezogene ProgIDs14/16 zeigen auf dieselbe CLSID. Office15-ProgID in diesen Ansichten fehlt. |
| Schlussfolgerung | Registrierter Startpfad und neuere vorhandene Datei sind verschieden. Das ist ein Diagnoseansatz, keine bewiesene Ursache und kein Nachweis einer defekten manuellen Access-Nutzung. Kein weiterer identischer Startversuch oder stiller Versionsfallback. |

Die Readiness-Skripte verlangen einen erfolgreichen `CurrentProject.ProjectType=acNull`-Getter als leeren Zustand; beliebige COM-Fehler werden nicht als leere Datenbank gewertet. [Microsoft-API](https://learn.microsoft.com/en-us/office/vba/api/access.currentproject.projecttype), [Enum](https://learn.microsoft.com/en-us/office/vba/api/access.acprojecttype). Beide Einstiege starten standardmäßig kein Access. Controller begrenzt90Sekunden; bei Timeout dürfte ausschließlich sein eigener direkter PowerShell-Child beendet werden, niemals ein geratenes Access-PID. Access-Cleanup wäre dann ausdrücklich unbestätigt. Dieser Timeout trat nicht auf.

Unabhängiger Astra-Review des Readiness-Codes fand zwei Cleanup-/Belegrobustheitslücken. Korrigiert und vor tatsächlicher Ausführung geprüft: ein simuliertes Freigabeversagen wird protokolliert und nachfolgendes Cleanup bleibt erreichbar; drei Python-Fault-Injection-Proben für Killfehler, Waitfehler und regulären Timeout bestanden. Vorherige rote Proben scheiterten an der noch fehlenden Cleanupfunktion bzw. verhinderten den Import des noch aktiven Controllers. Der Review der korrigierten Fassung fand keinen weiteren konkreten Befund im begrenzten Umfang; dies erteilt keine Genehmigung oder Laufzeitabnahme.

Die prozessgebundene Richtlinie gilt für die Sitzung und Kinder, nicht allein für diese eine Datei; sie wird nicht persistent gespeichert und setzt Gruppenrichtlinien nicht außer Kraft. [Microsoft-Dokumentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies?view=powershell-5.1). Vor Anwendung wurde die konkrete temporäre Einstellung im Ausführungstool ausdrücklich zur Zustimmung gestellt.

## Review des vollständigen synthetischen Harness

Statische Erstprüfung fand deterministische Makroparameter-/Objektbenennungsfehler, überschreibbare Makrobelegaggregation, irreführende Ergebnisflags und unvollständiges Cleanup. Zusätzlich ist vor jeder Datenbankanlage der Einfluss benutzerdefinierter Blank-Datenbankvorlagen zu klären; Form-/Reportoptionen allein reichen dafür nicht. Der vollständige Harness wurde **nicht** im Host ausgeführt; Änderungen daran wurden nur statisch und mit Host-freien Regressionen geprüft.

Die erste korrigierte Fassung (`c332fa98…5893190`) bestand42 Host-freie Assertions bei Worker und Leitung, darunter echte Reparse-, leere PID-, falsche Objektkategorie-, fehlende Kontroll- und monotone Markerbindungsfälle. Neuer ASTRA-Review fand trotzdem noch vier materielle latente P1-Probleme im Hostpfad: leere Sammellisten/Projektguardparameter, verschachtelte Freigabefehlerarray, HWND-Methodenaufruf und Null-/Singleton-Kontrollaggregation unter StrictMode. Diese Fassung samt Workerreceipt/Log bleibt getrennt in `harness-first-hostfree`; Review in `ASTRA_CORRECTION_REVIEW_1.json`. Nicht alle Hostpfade waren durch die42 Assertions abgedeckt.

Endfassung: Harness `22edd219f8f0f46a1806315d6e8d85c0190524d83945b521551fadc82c22f675`, Guards `c72b602ad1ca8ddef14b3bcc4f177e3b482be0bb263d46cb6d27a6de1aa79aec`, Tests `98f4746439a685b8e6981d23ec4834ef6001e0f15ec46e2094cb402995758252`. Worker und Leitung je59 Assertions bestanden, keine Skips/Fehler; alle drei aktiven PS-Dateien geparst. Neue Negativ-/Normalfälle prüfen tatsächliche leere Wrapperparameter, unbekannte/fehlerhafte ProjectType-Auskunft, flache null/ein Freigabefehler, fortgesetzten Cleanup-/Quit-Plan nach Vorlagenabbruch und trotz Freigabefehler sowie Kontrollaggregation mit null/einem/mehreren Fällen. Cleanupschritte sind injiziert: kein tatsächliches COM-Quit oder Prozessende daraus ableiten. Defaultaufruf startet kein Access.

Abschließender Astra6/medium-Review verifizierte die gehashte Endfassung, tatsächliche Aufrufstellen und Regressionen: vier zusätzlichen P1-Befunde behoben, keine neuen Codebefunde im begrenzten Umfang. Review selbst ohne Test-/Access-Ausführung; Leitungs-Testlauf unabhängig. `ASTRA_FINAL_REVIEW.json`, `ROOT_HOSTFREE_POSTREVIEW_TEST.txt` und `WORKER_RESULT_POSTREVIEW.json` im Prüfpunkt binden Nachweise. Frühe postreview-Testfehler bleiben erhalten; Logs sind keine vollständige Kopie der Tooltranskripte.

Vorlagenabdeckung ist ausdrücklich **UNKNOWN**. Die Produktionsgrenze des Prüfwerkzeugs verweigert `NewCurrentDatabase`, solange die vollständige Einflussgrenze nicht belegt ist; synthetische Kandidatenpfade allein erzeugen keinen Nachweis. Keine unbekannte Vorlagenwirkung wird durch einen booleschen Betreiberfreigabeschalter übergangen. Ein äußerer begrenzter Controller für den Vollharness ist vor einem späteren Lauf ebenfalls noch vorzubereiten.

Die beiden getrennten Startfehlversuche und die vorhandenen Office-Dateien berechtigen nicht zur Office-Reparatur, COM-Neuregistrierung oder Änderung von Trustcenter/Benutzer-/Maschinenrichtlinien. Eine konkrete nötige Umgebungsänderung ist ein eigener vorzubereitender Schritt. Unabhängige statische RMF-Versionsaufnahme und weitere begrenzte P3-Pakete bleiben möglich.

## Grenzen und Folge

Die Probe verwendet ausschließlich selbst erzeugte lokale Objekte und Marker. Aktuelle und ältere RadiFarben-ACCDB werden weder geöffnet noch in Access importiert. Keine Trustcenter-, Office-, Windows-, Netzwerk- oder Produktionsänderung. Bei unklarem Eigentum keine fremde Instanz schließen; eine blockierte Positivkontrolle nicht als Sicherheitsnachweis werten. Importnormalisierung ist keine Byte- oder Laufzeitparität. Vollständige gespeicherte RMF-/Menü-/Event-/Controlbindungen, Originalausgaben, Links/Parameterlisten, P-Code, Fehler/Abbruch/Restore bleiben spätere Schritte.

P0/P3 bleiben offen; P4 siebenmodulige Matrix vor P5 Datenbankentscheidung. Normative Aurelia-/Modul_Template-Anpassungen und Integration sind P6–P8/S4.8, keine Freigabe durch diese Probe. RadiWorks-Wartung bleibt in der bestehenden Priorisierung. Tatsächlich eingesetzte Hilfsmodelle: Luna6/max (Worker), Astra6/medium (unabhängige Vorprüfung); Root führt und verifiziert. Ein versehentlich zusätzlich gestarteter Ersatzworker wurde vor Arbeit unterbrochen, damit keine Doppeländerungen erfolgen.


### Zeitliche Präzisierung der Abschlusskontrolle

Abschlussmetadaten um09:48UTC: ein später gestarteter Access-Prozess (PID37784, Start09:06:20UTC, Office16, Sitzung1) vorhanden. Die unmittelbar nach den COM-Versuchen aufgenommenen Nullbestände bleiben zeitbezogene Befunde. Ursache/Eigentum und eine mögliche Datenbanköffnung dieses späteren Prozesses sind unbekannt; keine Bedienung oder Beendigung vorgenommen. Alle acht Listeneridentitäten unverändert; SOURCE_FINAL.json bestätigt weiterhin die drei Quellenhashes, Rechte und fehlenden Original-Lock. Daraus keine lückenlose Prozess-/Originalöffnungsbeobachtung ableiten.
