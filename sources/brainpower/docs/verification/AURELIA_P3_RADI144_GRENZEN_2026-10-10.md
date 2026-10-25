# Aurelia P3 – Radi144: Dateieigentum, Löschung und Retry-Grenzen

Stand 10.10.2026. Sechs zusätzliche synthetische Charakterisierungen sind nach Werkzeugkorrektur und frischer Wiederholung bestanden. Sie ergänzen die [zwölf vorherigen Fälle](AURELIA_P3_RADI144_CHARAKTERISIERUNG_2026-10-10.md), ohne Originalformeln oder Produktdateien zu ändern. Ein bestandener Charakterisierungstest bestätigt das beobachtete Verhalten, nicht Fehlerfreiheit oder eine Integrationsfreigabe.

## Nachweis und Grenzen

Werkzeug: `checkpoints/Aurelia-P3-Radi144-20261010/characterize_boundaries.py`. Private Nachweise: `runtime/aurelia-three-modules-20261009/reference-plan/p3-boundaries-20261010-140025Z`. Die endgültigen Läufe `edge-hardened` und `edge-root-verification` liefern jeweils sechs bestandene Assertions, `fatalError: null` und 13/13 unveränderte Originalquellhashes. Beide verwenden die bestehende Radi144-Python-Testumgebung; genaue Versionen, Zeitstempel und synthetische IDs stehen in den jeweiligen `results.json`.

Unveränderte Service-, Modell- und Schemabytes werden kontrolliert geladen. Fünf genaue API-Funktionskörper werden über AST ohne Routingdekoration übernommen. Die globale API/Rechenengine wird nicht importiert. Die Mehrfokusprobe ersetzt nur die Analysegrenze durch eine synthetische, schemafähige Antwort und treibt die nicht suspendierende Coroutine direkt; jede unerwartete Suspendierung wäre ein Werkzeugfehler. Keine Aussage über echte Formeln, HTTP, Eventloop-/Thread-/Prozessparallelität, PDF-Rendering oder tatsächliche Browsererreichbarkeit.

| Schritt | Beobachtung in der Probe | Folgerung für P4/P5 | Aussagegrenze |
|---|---|---|---|
| R144-G1 – gleiche Namen | Zwei synthetische Klienten mit unterschiedlichem Geburtsdatum haben getrennte IDs/Sitzungen. Der Namenssuffix-Kollektor erfasst beide manuell zugeordneten Verzeichnisse; A-Löschung entfernt auch das B-Verzeichnis, während B-Datensätze erhalten bleiben. | Verzeichnis-/Asseteigentum an stabile IDs binden; erlaubte Löschziele explizit festhalten. | Verzeichnisbesitz ist Fixture-Voraussetzung; tatsächliche Verzeichniserzeugung und API-Erreichbarkeit nicht geprüft. |
| R144-G2 – gemeinsam referenzierte Datei | A und B referenzieren denselben synthetischen Pfad. Nach A-Löschung bleibt B's Manifestreferenz, die Datei ist entfernt. | Gemeinsame Referenzen und Löschregeln vor Assetbereinigung berücksichtigen. | Direkte Manifestservices; keine Behauptung, dass die UI gemeinsame Registrierung ermöglicht. |
| R144-G3 – alter Writer nach Löschung | Vorab geladene Client-/Session-Snapshots werden nach erfolgreicher Löschung gespeichert und stellen die alten Datensätze wieder her. | Löschrevision, Konfliktregel und Wiederaufnahmealter festlegen; alte Writer dürfen nicht unbemerkt neue Hoheit erhalten. | Deterministische Aufrufreihenfolge, kein realer Race-Test. |
| R144-G4 – Mehrfokus wiederholen | Zweiter Fokus scheitert einmal mit 500-Exception. Der vollständige Retry liefert zwei Resultate; dauerhaft liegen die Fokusse A,A,B mit drei IDs vor. | Gesamtauftrag, Fokusschritt und Versuch unterscheiden; Retry-Identität/Teilabschluss definieren. | Exakte Orchestrierung/Mirror, synthetische Engineantwort; keine HTTP-Antwort oder Formelparität. |
| R144-G5 – Sitzung fehlt nach Dateischreiben | Registrierung einer vorher erzeugten Platzhalterdatei mit fehlender Sitzung wirft 404; Datei bleibt liegen, Manifest bleibt leer. | Datei, Manifest und Sitzung gemeinsam nachvollziehbar veröffentlichen; Reste kontrolliert bereinigen können. | Kein PDF-Renderer oder Endpoint-Dateipfad getestet. |
| R144-G6 – Fehler nach Dateiersatz | Nach echtem `os.replace` wird künstlich ein Fehler ausgelöst. Erste Sitzung ist trotz Fehler gespeichert; Retry erzeugt eine zweite ID. | Bestätigungszustand von gespeichertem Zustand trennen; Wiederholung anhand stabiler Absicht erkennen. | Injizierter Fehler, kein Nachweis natürlichen OS-Verhaltens nach Commit, Stromausfall-/fsync-Durability oder Crash-Restore. |

Die Folgerungen sind Anforderungen für die spätere Strukturentscheidung, keine ausgewählte DB-Technik und keine ausgeführte Reparatur am Original. Zuordnungen über Namen allein genügen nicht als Plattformidentität.

## Werkzeugreview

Der erste Lauf `edge-first` stoppt nach drei Fällen: Windows-Asyncio wollte für den Eventloop einen internen Loopback-Kanal öffnen, den die Netzsperre ablehnte. Das ist ein Werkzeugfehler. `edge-corrected` besteht sechs Fälle, besitzt aber noch die früheren Guardgrenzen; deshalb ist es nicht der endgültige Sicherheitsbeleg.

Astra6/medium fand zwei Guardmängel: Der früh geladene Helper importierte Drittbibliotheken vor der Sperre; `socket.connect` allein blockierte nicht alle Netzwerkwege. Außerdem konnten vor `lstat` aufgelöste Pfade ursprüngliche Reparse-Komponenten verbergen. Beide wurden korrigiert und unabhängig erneut geprüft: Sperre vor Helper-/Drittimport, alle `socket.*`-Auditereignisse sowie externe Prozesse gesperrt; ursprüngliche absolute Komponenten inklusive Vorfahren vor Auflösung/Verzeichnisanlage geprüft.

Negativproben belegen die Ablehnung von Socketerzeugung, DNS-Auflösung, Pfadüberschreitung und injizierten Reparse-Metadaten. Letztere ist ausdrücklich eine `lstat`-Simulation, keine echte Windows-Junction. Subprozesssperre nur statisch geprüft. Keine Garantie gegen konkurrierende Pfadänderungen oder native Umgehungen. Schreib-/Löschoperationen bleiben auf frische synthetische Scratch-Unterpfade begrenzt. Vollständige Fehlerursachen der Zwischenläufe sind erhalten.

## Stand und Fortsetzung

Der ergänzende Radi144-Grenzblock ist abgeschlossen. Insgesamt liegen jetzt 18 synthetische Charakterisierungen vor, weiterhin keine vollständige Modulabnahme. Offen: vollständige Engine-/API-/UI-/CLI-/PowerShell-/Abbruch-/Restoreprüfung und Workflow-/Writer-/Kontextmatrix. Die [Morphic-Quellaufnahme](AURELIA_P3_MORPHIC_QUELLVERTRAG_2026-10-10.md) ergänzt parallel die Owner-/Lease-/Kataloganforderungen; aktuelle RadiFarben-VBA-/Query-/Formular-/Timer-/Berichtsreferenzen folgen.

P0-Linux-Runtime, P1/P2 und die vollständige siebenmodulige P4-Matrix bleiben offen; P5-Betreiberentscheidung und P6–P8-Integrationen behalten ihre Gates. Normative Modul_Templates, Governors-Routing und Liveinstanzen unverändert. Der private Nachweispunkt enthält Vorher-/Nachher-Dokumente, gebundene Testwerkzeuge und rückgelesene Manifestnachweise; er ersetzt keine F:-Gesamt- oder Server-/Schlüsselwiederherstellung. Tatsächliche Helfer: Luna6/max für Morphic, Astra6/medium für Radi144-Werkzeug-/Befundreview.
