# Aurelia P3 – RadiFarben: Formular-, Query-, Timer- und Berichtverträge

Stand 10.10.2026. Die bestehende aktuelle Extraktion wird frisch hashgebunden und gezielt erweitert. Keine Access-Anwendung, Formulare, Makros, VBA oder QueryDefs ausgeführt; keine Geschäftsdaten gelesen, Links geöffnet oder Produktdateien geändert. Grundlage ist der [aktuelle Charakterisierungsbericht vom09.10.](../RADIFARBEN_CHARAKTERISIERUNG_MODULBINDUNGEN_2026-10-09.md), nicht die abweichende historische Downloads-Kopie.

## Gebundene Aufnahme

Aktuelle ACCDB: `C:/Users/Hubert111/Documents/Radifarben/RadiFarben.accdb`, 86.454.272Bytes, SHA256 `2b48ce8dec5e0126072e0bc24f07b754b8b64af0651b080d257dcb1b0c8f13bc`. Vor diesem Block privat kopiert und rückgelesen. Alle100 kanonischen VBA-Dateien stimmen mit dem vorhandenen Manifest überein; keine erneute Parser- oder DAO-Auslese erforderlich. Source-/P-Code-Parität und gespeicherte Objektbindungen bleiben unbekannt.

Werkzeug `checkpoints/trace_radifarben_p3.py` erfasst die2228 deklarierten Prozeduren und187 Kandidaten mit Datenzugriffen, Ausgaben, Navigation oder Timern; diese Zahlen sind kein Erreichbarkeits-/Funktionsnachweis.47 gebundene SQL-Texte werden statisch nach bekannten Objektreferenzen und VBA-Funktionsnamen untersucht. Die Mustererkennung ist kein vollständiger VBA-/SQL-Parser: dynamische Namen, verschachtelte FROM-Konstruktionen und gekoppelte Objektvariablen können unvollständig sein. Funktionszuordnungen werden direkt aus den aktuellen hashgeprüften Quellzeilen erzeugt; gleichnamige Definitionen bleiben erhalten, ihre Laufzeitauflösung ist unbekannt. Endgültiger Nachweis `runtime/aurelia-three-modules-20261009/reference-plan/p3-morphic-farben-20261010-142545Z/FARBEN_STATIC_TRACE_V2.json` bindet Werkzeug und Metadaten zusätzlich mit SHA256. `FARBEN_UPDATE_RULES.json` enthält fünf redigierte SQL-Definitionen; Query-/VBA-Metadaten sind gegen das ursprüngliche Nachweismanifest rückgeprüft.

Persönliche Quelltextliterale werden nicht ausgegeben; der Trace enthält bekannte Schema-/Formular-/Report-/Funktionsbezeichner, Zeilen, technische Hash-/Pfad-/Zeitmetadaten und numerische Timerliterale. Drei kleine Prüfungen bestätigen die Lexerbehandlung von Rem-Kommentaren, Apostrophen innerhalb von Strings und verdoppelten Anführungszeichen; keine RadiFarben-Algorithmustests. Ein früher Inline-Aufruf dieser Werkzeugchecks scheiterte am Shellquoting und wurde durch eine eigene Prüfdatei ersetzt. Der Reviewhinweis zu angeblichen +02:00-Zeitstempeln wurde an den originalen JSON-Textbytes geprüft: beide früheren Traces enthalten +00:00; keine Artefakttransformation festgestellt.

## Gezielt bestätigte Quellverträge

Zeilen beziehen sich auf `runtime/radifarben-characterization-20261009/current-vba-acevariant`. Die folgenden Codekanten sind gezielt gelesen; ihre tatsächlich gespeicherte Event-/Menüerreichbarkeit wurde nicht ausgeführt.

| Schritt | Quellbefund | Für Aurelia/Modul_Templates erforderlich | Noch unbekannt |
|---|---|---|---|
| F-G1 Start | `bas_Autoexec.bas:21–100` prüft Rechner-/Verzeichniskonstellation, kann Formulare/Abfrage öffnen und Initialisierungsfunktionen aufrufen. Fehlerbehandlung enthält `On Error Resume Next`. Drei Makronamen vorhanden: Autoexec, AutoKeys und temporärer Makrocontainer. | Startbedingungen, Initialisierung und Seiteneffekte als ausdrücklichen Hostvertrag erfassen; keine Ausführung beliebiger importierter Startmakros. | Gespeicherter Autoexec-Inhalt/Bindung, tatsächlich gewählter Startpfad und externe Verzeichnisse nicht abgenommen. |
| F-G2 Menü | `Form_frmMen_.vba:35–149` delegiert Schaltflächen an `Behandle_Schaltfläche`; `:203,235,242,252` liest ein dynamisch gewähltes Steuer-Recordset und öffnet Formular/Report bzw. `Eval` eines Feldinhalts. | Menüdefinition und Rechte getrennt versionieren; spätere freigegebene Aktionen auf einen expliziten Adapterkatalog abbilden. Legacy-Eval nicht als allgemeine serverseitige Befehlsfreigabe übernehmen. | Menüzeilen wurden nicht gelesen; keine vollständige Liste aktuell erreichbarer Ziele oder Aktionen. |
| F-G3 Berichtauswahl | `Form_frmReporting.vba:35–83` verwendet Auswertungsspalten, Ansicht und Sortierung/OpenArgs, um Report oder Query zu öffnen. | Bericht-/Abfrageauswahl, Parameter, Ergebnis-/Vorlagen-/Rendererrevision und Archivartefakt getrennt halten. Queryöffnung kann eine Datenaktion sein; nur SELECT-Annahme genügt nicht. | Tatsächlich auswählbare Querytypen, gespeicherte RecordSource/Layouts, Druck-/PDF-Ergebnis und Archivwriter. |
| F-G4 Palettenbericht | `Report_rptFarbPaletten_colorhex.vba:26–85` erzeugt sechs RGB-Kanalpermutationen für fünf Farben im Report. | Originalpalettenreihenfolge, Darstellungstransformation und Ausgabeformat erhalten; keine automatische Gleichsetzung mit Rausch-/Frequenzprofilen. | Eventbindung, fertiges Layout und originalgerenderte Ausgabe. |
| F-G5 Aufstell-Symbole | `Form_FRMAufstellKeys.vba:39–49` entnimmt ein Zeichen, wechselt zu neuem Formularsatz und setzt Symbol; `:67–125` verknüpft Unicode-/Integer-/Hexdarstellung. | Zeichen, Codepunkt-/Darstellungsregeln und Originalspeicherung verlustfrei erfassen; gebundene Control-Feldzuordnung separat bestätigen. | Gespeicherte ControlSource; fehlende VBA-Zuordnung für anderes Formular `frmAufstellKeysAutoForm` und Report `rptAufstellKeys` bleibt offen. |
| F-G6 Timer |18 `Form_Timer`-Deklarationen im rekonstruierten Projekt, einschließlich ALT-/Sicherungsvarianten. `Form_frmStartUp.vba:108–154` verändert Sicht-/Zähler-/Textzustand; Matrix-/Besendungstimer sind im Vorbericht gebunden. | Anzeigeanimation, Berechnung, dauerhafte Beobachtung und Hintergrundauftrag trennen. Lebensdauer/Abbruch/Wiederaufnahme für spätere Jobs separat bestimmen. |18 Deklarationen sind keine18 aktiven Timer; Literalintervalle können überschrieben sein. Timerzustände belegen keine Klientenreaktion oder persistierte Trendhistorie. |
| F-G7 Audio | `mdlKlang.bas:16–27,60–81` verwendet Windows-Beep mit ganzzahligen Frequenz-/Dauerparametern. | Windowsabhängigkeit als eigene Fähigkeit erfassen; gemeinsame Aurelia-Audiofähigkeit muss Präzision, Profilrevision und bewusste Aktivierung getrennt anbieten. | Kein Audio abgespielt, keine Generatorparität oder vollständige Aufrufabdeckung. Keine stillschweigende Umstellung auf RadiWorks-Audio. |

## Fünf UPDATE-Abfragen benötigen VBA

Alle fünf schreiben nach SQL-Definition auf `tblFarbPaletten_colorhex`; die Parameterermittlung bleibt bei ihnen verweigert, wie insgesamt bei17/47 QueryDefs. Die SQL-Texte sind erfasst, die Abfragen wurden nicht ausgeführt. Die statisch zugeordneten Funktionen sind:

| Abfrage | Funktionsdefinition | Bestehende Auswahl-/Schreibregel laut SQL |
|---|---|---|
| FarbAbstandMinimum | `mdlFarben.bas:882` – `FarbAbstand_von5Farben_Minimum` | Setzt Mindestabstand bei `NULL` im Zielfeld. |
| FarbAbstandSumme | `mdlFarben.bas:957` – `FarbAbstand_von5Farben_Summe` | Setzt Abstandssumme bei `NULL` im Zielfeld. |
| FarbenAnzahl | `mdlFarbPaletten_colorhex.bas:872` – `FarbenAnzahl_inColorHexPalette` | Zählt anhand fünf RGB-Werte bei `NULL` in der Anzahl. |
| Kontrast | `mdlFarben.bas:830` – `Kontrast_RGB` | Setzt alle vier benachbarten Kontrastwerte, wenn mindestens einer `NULL` ist. |
| Kontrast_PosMax | `mdlFarben.bas:1457` – `PositionVonKontrastMaximum` | Setzt Maximumposition bei `NULL` im Zielfeld. |

Abfragenamen im Trace tragen jeweils das vollständige Präfix `qupdFarbPaletten_colorhex_`. Diese Funktionsabhängigkeit verhindert eine unveränderte Übernahme als reines PostgreSQL-SQL. Eine spätere äquivalente Modulberechnung oder DB-Funktion verlangt Originalreferenzausgaben, Fehler-/Null-/Rundungsverhalten, Funktionsversion und transaktionale Veröffentlichungsregeln. Aktuell keine der beiden Varianten gewählt oder implementiert. Insbesondere darf die Kontrastabfrage nicht unbemerkt auf „nur fehlende Einzelspalten ergänzen“ geändert werden.

## Restpunkte und Strukturfolgen

Für P4 ergänzen: ausführbare Query-/Funktionsrevision gegenüber Katalogdaten, dynamische Menü-/Reportkonfiguration, Zeichen-/Stringpräzision, gespeicherte Objektbindings, Animation gegenüber Ereignisarchiv und externe Hostfähigkeiten. Bestehende Farben-/Raten-/Matrix-/Klienten-/Rechte-/Importalgorithmen bleiben als getrennte Originalverträge erhalten. Keine universelle Heuristik oder semantische KI-Suche eingeführt.

P3-RadiFarben bleibt offen: gespeicherte Formular-/Makro-/Record-/Control-/Eventbindungen,17 Parameterlisten, fünf verknüpfte Quellen, vollständiger aktiver Aufrufgraph, Abbruch/Teilfehler/Restore sowie kontrollierte synthetische Originalausgaben. Keine VBA-Neuimplementierung anhand plausibler Beispielwerte und keine unkontrollierte Originalanwendungsöffnung. Erst sichere Originalreferenzumgebung und klar abgegrenzte synthetische Pfade festlegen.

Die statische Ergänzung ist ein abgeschlossener Teilblock. Leitung wiederholte den endgültigen Trace frisch; beide Ergebnisse sind außer dem UTC-Zeitstempel identisch. Werkzeug-/Metadatenbindungen und fünf UPDATE-Hashes rückgeprüft; drei Lexerchecks erneut bestanden. Beleg `FARBEN_REPEAT_VERIFY.json`. Astra6/medium prüfte nach Korrektur der Indexbindung auch alle fünf redigierten UPDATE-Regeln; keine verbleibenden materiellen Befunde im begrenzten statischen Umfang. Den Zeitstempelbefund zog der Review zurück: seine PowerShell-Ausgabe hatte den UTC-Zeitwert konvertiert.

Zentrale Datenbankentscheidung weiterhin nach der vollständigen gemeinsamen Modulmatrix; normative Modul_Templates und Aurelia-Kern unverändert. Private Dokument-/Quell-/Prüfsicherung im genannten Nachweisordner, keine neue F:-Gesamtsicherung. Liveinstanzen und Governors bleiben erhalten.
