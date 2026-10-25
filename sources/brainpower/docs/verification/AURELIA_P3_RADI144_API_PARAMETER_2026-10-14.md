# P3 – Radi144: API-Parameterfluss und Teilabschluss

Stand15.10.2026 (Fortsetzung vom14.10.): **Begrenzte Original-API-Referenz bestanden: zwei frische Läufe mit je acht Fallgruppen und36 verifizierten Erwartungen; vollständige Ergebnisobjekte bis auf die Laufkennung identisch.** Betreiber bestätigt die Empfehlung, den Originalstand zu erhalten und die bekannte Parameterlücke als Ist-Abweichung zu führen. Eine neue CUDA-/Quantum-/Iterationssteuerung wurde nicht implementiert.

## Prüfgrenze

Genau acht Originalfunktionskörper aus `app/api/resonance.py`: `analyze_matrix_resonance`, `_build_client_data`, `_requires_precomputed_signature`, `_mirror_api_session`, `_split_focus_sequence`, `_build_response`, `_apply_request_amplifier`, `_restore_request_amplifier`. Routingdekoration wird beim AST-Laden ausgelassen; Funktionskörper und Zukunftsannotationsemantik bleiben erhalten. Schema und Engine nur hashgebunden gelesen. Kein Import des Produktmoduls, kein Enginekonstruktor, kein HTTP-/Pydantic-/Torch-/GPU-/Dateistore-/Auth-/Rechte-/Linuxnachweis.

Engineberechnung, Client-/Sessionservices, Signaturvorbereitung, Responsekonstruktor, Logger und IDs/Uhrzeit sind kontrollierte synthetische Grenzen. Insbesondere Geräte-/Zeit-/UUID-/Klienten-/Sitzungsangaben sind synthetische Markierungen, keine Livebeobachtungen. Signaturfall prüft nur Originalgate und Übergabe des kontrollierten Sentinelobjekts; keine Gruppen-/Geo-/Bild-/Katalogformel.

Die Originalcoroutine muss ohne Eventloop in einem Schritt abschließen. Der Auditguard sperrt während Originalaufrufen I/O, Imports, erzeugten Code, Netzwerk, Prozesse, Registry und ctypes; stdin/stdout/stderr sind in dieser Phase gesperrt. Keine Betriebssystem-Sandboxgarantie. Nur der äußere Controller schreibt Nachweise in frische eigene Laufverzeichnisse.

## Feste Fallgruppen

| Gruppe | Tatsächlich charakterisierter Ist-Vertrag |
|---|---|
| 01 Erfolg | Vollständige Engine-Kwargs, gespeicherte Anfragekonfiguration, Antwort/IDs und Amplifier-Rücknahme |
| 02 Nur Wunschflags/Iterationen ändern | Gleiche Engine-Kwargs; geänderte Requestflags gespeichert, Iterationen dort nicht enthalten |
| 03 Modus unabhängig | calculation_mode wird übernommen, getrennt vom Quantumwunschflag; keine echte Stochastikprobe |
| 04 Vorbereitete Signatur | Originalgate und exakte Weitergabe des synthetischen Sentinelobjekts |
| 05 Fehlende Eingabe |400, keine Berechnung/Sitzung, Amplifier-Rücknahme|
| 06 Enginefehler |500, keine Sitzung, Amplifier-Rücknahme|
| 07 Sessionfehler |500 nach Berechnung, keine Antwortheader, Amplifier-Rücknahme|
| 08 Antwortfehler |500 nach synthetischer Sitzungserstellung und Headern; Teilabschluss sichtbar|

## Werkzeug- und Quellenbelege

Drei Originalquellhashes und HEAD entsprechen dem [Parameterbefund](AURELIA_P3_RADI144_PARAMETER_2026-10-14.md); der Status genau dieser drei getrackten Pfade ist leer. Vorhandenes vorgemerktes AGENTS.md bleibt erhalten; keine Aussage über ein insgesamt sauberes Repository. Der frühere CPU-Teilnachweis ist separat unverändert:26 Manifestdateien frisch nachgerechnet,245 Archiveinträge im vorigen Abschluss verifiziert.

Rootcontroller zuerst mit fünf erwarteten RED-Fehlern, danach fünf bestandenen Tests. Astra fand die Abhängigkeit der Gate-Testwiederholung vom echten Binding. Zusätzliche Regression: genau ein erwarteter Fehler unter sechs Tests. Anschließend isolierte Controllerkopie mit garantiert geschlossenem eigenem Binding; alle sechs Tests erfolgreich. Keine Originalausführung in diesen Werkzeugtests. Rot-/Grünbytes, Ausgaben und Exitcodes erhalten.

Luna/max besitzt neues Werkzeug/Tests; Root Controller/Dokumentation/Ausführung; Astra/medium unabhängigen SPEC→QUALITY-Vorreview und Ergebnisreview. Keine rekursive Delegation oder Produktkorrektur. Astra prüfte den eingefrorenen Kandidaten vor Ausführung und bestätigte danach beide vollständigen Ergebnisobjekte und vier Datei-SHA256 unabhängig. Eine zusätzliche Regression für das Session-Double scheitert zunächst wie erwartet (sieben Tests, genau ein Assertionfehler) und besteht nach minimaler Korrektur: Rückgabe-Objekt mit client_id/client_name, getrennte gespeicherte Dictionarykopie und Prüfung späterer Eingabemutation. Sieben Werkzeugtests und sechs Controllerprüfungen erfolgreich. Keine Produktkorrektur; die ursprüngliche fehlerhafte Doublefassung wurde nie mit Originalkörpern ausgeführt.

## Tatsächliche Ausführung und Vergleich

| Lauf | Gruppen / Erwartungen | Controllerdauer | Ergebnis |
|---|---|---|---|
| api-run-1 |8 /36|52.031s|Exit0, stderr leer, kein Timeout/Nachprüffehler|
| api-run-2 |8 /36|66.359s|Exit0, stderr leer, gleiche vollständige Ergebnisobjekte|

Verglichen wurden alle JSON-Bereiche ausschließlich ohne die jeweilige Laufkennung: AST, Fallnamen, vollständige Fallobjekte, Einschränkungen, Werkzeugbindung, Scope, Quellenhashes und synthetische Werte. Vergleichshash `9db62e43fb5744955a8d2671bbe3f9454fbe9bd19fca0febcb2bc38d06279213`. Zeit-/Ausführungs-/Gitbeobachtungen stehen separat in den Controllerbelegen, sie werden nicht als deterministische Werte gefordert. Quell-/Werkzeughashes, HEAD und Status genau der drei benannten getrackten Pfade vor/nach beiden Läufen gleich. Nach Verbrauch beider Laufkennungen Gate geschlossen.

Ergebnisinterpretation: CUDA-/Quantum-Wunschflags und Iterationen ändern die Spy-Engine-Kwargs nicht; die beiden Flags, jedoch nicht Iterationen, erscheinen in der synthetischen Sessionkonfiguration. Der Analysemodus wird unabhängig übergeben. Die Planetary-Gateprobe führt einmal None und einmal genau den kontrollierten Signatur-Sentinel weiter; daraus keine Abnahme aller Signaturzweige ableiten.400 bei fehlenden Eingaben und500 bei den drei absichtlich injizierten Grenzfehlern; Amplifierzustand wiederhergestellt.

**Fall07:** `session_config` im Bericht ist hier ausschließlich der erfolglose Speicherungsversuch; `sessions` ist leer. **Fall08:** Session und gesetzte Header existieren in der synthetischen Umgebung bereits vor dem Fehler des Responsekonstruktors. Keine echte DBpersistenz, HTTPantwort oder tatsächliche Übertragung dieser Header bewiesen. Die Probe misst Originalkontrollfluss und sein Teilabschlussverhalten mit klar ausgewiesenen Testgrenzen.

Luna berichtet zwischen initialem RED und finalem Kandidaten weitere Testloader-/ast.dump-Testfehler. Deren genaue Zwischenbytefassungen sind nicht gesondert eingefroren. Initiale Rot-Testbytes/Ausgaben/Exit1 und unabhängige aktuelle Root-Grünkopien bleiben erhalten; keine umfassende reproduzierbare Zwischenhistorie behauptet. Details `ROOT-WORKER-EVIDENCE-LIMITS.json`. Die beiden späteren Reviewkorrekturen sind jeweils separat rot/grün bytegebunden. Originalfunktionskörper wurden erst nach unabhängigem Vorreview aufgerufen.

## Bedarf für P4

| Ebene | Für die spätere Struktur getrennt halten |
|---|---|
| Anfrage | Unveränderliche Wunschwerte und originale Feldpräsenz; gespeicherte Requestflags sind kein Wirkungsnachweis |
| Wirksamer Vertrag | Tatsächlich an die Berechnung übergebene Parameter und Rezept-/Quellrevision; kontrollierte Grenzen ausdrücklich markieren |
| Beobachtung | Tatsächliche Runtime-/Hardware-/Ergebnisangaben mit Herkunft; in diesem Paket ausschließlich synthetische Antwortdaten |
| Speicherung | Versuchte Konfiguration, tatsächlich gespeicherter Zustand und bestätigte Speicherung getrennt; Fall07 ist kein gespeichertes Ergebnis |
| Abschluss | Berechnungs-, Sessionpersistenz-, Antwortkonstruktion und tatsächliche Übertragung getrennt; Abbruch-/Fehlerphase und ursprüngliche Ursache erhalten |

P4-Siebenermatrix einschließlich Aurelia/Modul_Templates bleibt vor P5-Strukturentscheidung; keine neue DB- oder normative Templateentscheidung. Vollständige P3-, API-/UI-/CLI-/Parallelitäts-/Produktabnahme bleibt offen. Keine Server-/WSL-/SSH-/Access-/Cloud-/Live-/Routingänderung.

Lokaler Punkt `checkpoints/Aurelia-P3-Radi144-API-Parameter-20261014-213342Z`, Abschluss ausschließlich durch finalen Manifest-/Archiv-/Rücklesebeleg. Tatsächlicher Abschluss und Umfang werden ausschließlich durch diesen finalen Rücklesebeleg bestätigt. Kein F:-/Server-/Schlüssel-/Gesamtprojektbackup.
