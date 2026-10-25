# Aurelia P3 – RadiFarben: kontrollierte Originalreferenz

Stand 10.10.2026. Vorbereitung der noch offenen gespeicherten Objektbindungen und Originalausgaben. Keine Access-Anwendung gestartet, keine Originaldatenbank in Access geöffnet, keine Windows-/Office-/Netzwerk-/Trustcenteränderung. Die bisherige statische Aufnahme und Algorithmen bleiben erhalten.

## Frischer lokaler Befund

Rein lesender Beleg `ACCESS_REFERENCE_PREREQUISITES.json` im privaten Punkt `runtime/aurelia-three-modules-20261009/reference-plan/p3-morphic-farben-20261010-152120Z`:

| Voraussetzung | Beobachtet | Grenze |
|---|---|---|
| Access-Datei | MSACCESS.EXE am geprüften Officepfad unter Program Files (x86) vorhanden, Dateiversion 16.0.20430.20146; keine Datei am anderen geprüften Officepfad | Pfad allein ist kein Binärarchitekturnachweis. Kein Start-, Lizenz-, Objektmodell- oder Exportnachweis. |
| COM-Registrierung | Unterschlüssel Access.Application/CLSID in beiden geprüften Registryansichten vorhanden; kein CLSID-Wert ausgelesen | Registrierung beweist keine isolierte Ausführung oder zwei Access-Architekturen. |
| Windows-Sandbox-Datei | WindowsSandbox.exe am geprüften System32-Pfad nicht vorhanden | Kein Nachweis, dass Sandbox nicht installierbar wäre; Edition/Feature/Virtualisierungszustand ungeprüft. Nichts aktiviert. |
| Ressourcenmomentaufnahme | Windows 10.0.19045, 15.995.984 KiB sichtbarer RAM, 2.576.376 KiB frei beim Probezeitpunkt | Schwankender Einzelwert; keine Ursache der WSL-Probleme und keine VM-Budgetfreigabe. Erste nicht eskalierte CIM-Leseprobe war verweigert, anschließende freigegebene Probe lieferte Werte. |

Access-Sandboxmodus oder ein Python-/COM-Wrapper ist nicht mit einer isolierten Windows-Gastumgebung gleichzusetzen. Eine VM wird nicht parallel zu den bestehenden Dauerinstanzen gestartet, solange deren Ressourcenbedarf und Isolationsgrenzen nicht geprüft sind. Ein Datenträgertausch oder eine zusätzliche Installation gehört nicht zu dieser Vorbereitung.

## Bevorzugter Referenzweg

Eine eigene Windows-Test-VM mit ausreichend geprüftem Budget oder ein dafür bereitgestellter separater Windows-Testrechner. Für den separaten Rechner gelten dieselben Anforderungen an Daten, Netz und Prozesspfade. Das ist eine Empfehlung, keine bereits verfügbare oder eingerichtete Umgebung.

Der Betreiber hat im laufenden Schritt zunächst die **lokale isolierte VM** gewählt, anschließend aber mangels Windows-/Access-Installationsmedien eine andere Lösung angefordert. Er bestätigt die lauffähige Anwendung im vorhandenen lokalen Access. Die VM wird deshalb zurückgestellt, nicht eingerichtet. Die erhaltene Leseprobe `LOCAL_VM_PREREQUISITES.json` erfasst Windows Enterprise, vorhandene Hyper-V-Komponenten mit InstallState=1, HypervisorPresent=True und vorhandene Hyper-V-/VirtualBox-Programmdateien. InstallState=1 bezeichnet aktiviert laut [Microsofts WMI-Vertrag](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-optionalfeature). Das beweist noch keinen erfolgreichen Gaststart oder eine intakte VM-Verwaltung. Die gleichzeitig gemeldeten False-Werte für VMMonitorModeExtensions/SLAT werden nicht als Anlass für BIOS-/Boot-/Sicherheitsänderungen verwendet.

Als ersten Kandidaten den bereits vorhandenen Hyper-V-Aufbau rein lesend verifizieren; keine zweite Virtualisierung parallel installieren. Der freigegebene Umfang ist die Vorbereitung, bisher keine VM angelegt oder gestartet. Momentan wurden 3.273.172 KiB freier RAM und ca. 23,1 GB freier C:-Speicher beobachtet. Ein vorläufiges Gastbudget von 4 GiB RAM und zwei virtuellen CPUs benötigt daher eine erneute Ressourcenprüfung und ausreichende Hostreserve. Kein geplanter Gaststart allein aufgrund des vorhandenen Hypervisors. Auf F: sind ca. 405,9 GB frei, seine Gast-I/O-Eignung wurde nicht geprüft; keine Laufwerke tauschen oder formatieren.

Vorbereitet wird ein ausgeschalteter Gast ohne virtuellen Netzwerkadapter und ohne automatische Startaktionen, Hostfreigaben, Zwischenablage-/Geräteweitergabe oder Hostzugangsdaten. Windows-/Access-Version und Nutzbarkeit im Gast sowie Installationsmedien sind noch zu klären; vorhandenes Host-Office ist kein Nachweis einer nutzbaren Gastinstallation. Eine bestätigte Start-/Isolationsprobe geht der Originalprüfung voraus. Bis dahin laufen die unabhängigen Morphic-Tests weiter.

Der letzte Absatz beschreibt den zurückgestellten VM-Kandidaten. Es besteht kein neuer Auftrag, ISO/Office zu installieren, Hyper-V zu reparieren, Ressourcen freizuräumen oder vorhandene Gäste zu verändern. Ein zusätzlicher lesender `Get-VMHost`-Aufruf war nicht verfügbar (HRESULT -2146233088); der VMMS-Dienst wurde als laufend beobachtet. Die Fehlerursache wurde nicht bestimmt.

## Aktuelle Alternative: begrenzter Definitionsexport im vorhandenen Access

**Betreiberklärung vom 11.10.2026:** Zentraler aktueller Referenzworkflow ist Menüpunkt1 „Raten-Matrix-Formular“ (RMF). Punkte3–7 (Matrix, Test Matrix, Bruce-Copen-Algorithmus, Farben, Farb-Paletten) sind laut Betreiber bereits darin enthalten und als RMF-Teilfunktionen zu erfassen. Punkt2 ist der alte, nicht weiterentwickelte RMF-Stand; Punkt8 hat keine eigene Weiterentwicklungspriorität. Punkt9 liefert nur die ergänzend benötigten Stammdaten/Informationen, soweit nicht bereits im RMF enthalten. Vollständige Zuordnung und Folgen stehen im konsolidierten Phasenplan, Abschnitt15.

RF-E1 bleibt die erste synthetische Sicherheits-/Machbarkeitsprobe. Danach bei der Definitionserfassung die gespeicherte Menüpunkt1→Formularbindung und RMF-Aufrufe zuerst belegen, anschließend Teilfunktionen und Punkt9-Abhängigkeiten zuordnen. Betreiberbestätigung und Bild sind Planungsbelege, keine eigene Originalausführung. Der angezeigte Menütitel allein ist noch kein technisch gebundener Access-Objektname. Historischen Bestand und tatsächlich benötigte Abhängigkeiten erhalten; keine Funktionen/Algorithmen durch diese Priorisierung löschen oder verändern.

**Weitere Betreiberklärung:** RMF ist die aktuell höchste Version, wird noch weiterentwickelt und bildet zunächst die Ausgangsbasis. Weitere Versionen bis zur Aurelia-Integration separat aufnehmen, Unterschiede und erforderliche Referenzprüfungen dokumentieren, alte Belege/Arbeitsstände erhalten. Ablauf im Phasenplan Abschnitt16. Neue Dateibytes am11.10. separat gesichert (`2993247b…` gegenüber bisher `2b48ce8d…`); keine Formeländerung allein daraus ableiten. Vorherige Extraktionen und Prüfungen sind weiterhin nur an die alte Referenz gebunden. Quelle-/Objektvergleich des neuen Stands noch offen. Die synthetische RF-E1-Probe benötigt keinen dieser Originalstände als Access-Eingabe.

Die Betreiberbestätigung der lokalen Lauffähigkeit wird als solche festgehalten, nicht als bereits protokollierter Funktions-/Exporttest. Als enger Kandidat kommt eine frisch erzeugte leere Access-Zieldatenbank in Betracht: ausgewählte **Objekte** aus einer hashgebundenen privaten Quellenkopie importieren und ihre Definitionen als Text exportieren, ohne diese Quellenkopie als aktuelle Anwendung zu öffnen. Noch kein Access-Start oder Import durchgeführt.

Microsoft unterstützt den Objektimport zwischen Access-Datenbanken über `TransferDatabase`; `StructureOnly` betrifft ausschließlich Tabellen und ist keine universelle Ausführungssperre. Ein Tabellenimport könnte sogar bestehende Links übernehmen. Deshalb keine Tabellen, Links, Import-/Exportspezifikationen oder Menüs übernehmen; Querydefinitionen ausdrücklich als Queries, niemals als Tabellen/resultierende Datensätze behandeln. [Microsoft: TransferDatabase](https://learn.microsoft.com/en-us/office/vba/api/access.docmd.transferdatabase).

| Alternativschritt | Vorbereitung und Aussagegrenze |
|---|---|
| RF-E0 Eigentum | Neue eigene Access-Instanz und leere Zielkopie je Probe/Batch. Bereits vom Nutzer geöffnete Accessprozesse, Originaldatei und Liveinstanzen nicht schließen oder verändern. Quelle vor/nach hashprüfen; nur eigene PID-/Dateiziele bedienen. Keine Host-Sandbox behaupten. |
| RF-E1 Synthetische Importprobe | Künstliche AutoExec-, Formular-/Report-/Timer- und Querymarker mit festen lokalen Kontrollpfaden. Erst den konkreten Import-/Text-Exportweg auf ungewollte Marker und Änderungen prüfen. Nur definierte synthetische Objekte, keine Netz-/Shell-/Löschaktionen im Marker. Markerabwesenheit ist ein begrenzter empirischer Befund, keine generelle Aussage über unbekannte ActiveX-/Link-/Kompilierungseffekte. |
| RF-E2 Begrenzter Export | Nur nach geklärten Importgrenzen eine private Original-Arbeitskopie als Objektquelle verwenden. Niemals Form/Report anzeigen oder Makros/Queries/Anwendungsfunktionen ausführen. Ein importiertes AutoExec nicht durch Wiederöffnung der Zielkopie aktivieren. Rohdefinitionen bleiben privat. Access liest dabei Quellenbytes; „nicht als aktuelle Datenbank geöffnet“ bedeutet nicht „von Access nicht gelesen“. |
| RF-E3 Herkunft | Originalobjekt → importiertes Objekt → Textexport mit Namen, Typ, Instanz, Version, Datei-/Exporthash getrennt binden. Import kann Definitionen normalisieren/umbenennen; keine Byte-, P-Code- oder vollständige Laufzeitparität daraus ableiten. 105 bekannte Objektzuordnungen und Queryinventar separat abgleichen. |
| RF-E4 Berechnungsreferenz | Definitionsexport allein erlaubt keine beliebigen Originalabläufe. Danach nur gezielte, zuvor quellengeprüfte Berechnungen an synthetischen Eingaben planen. Je Funktion Seiteneffekte/Abhängigkeiten, Fehler, Abbruch und Rundung erfassen; volle Anwendungs-/Restoreparität bleibt ein eigener Nachweis. |

`AutomationSecurityForceDisable` wird nicht als allgemeiner Schutz verwendet: Microsofts Access-Dokumentation beschreibt abhängig vom Sicherheitsniveau sowohl fehlende Wirkung als auch unterbundenes Datenbanköffnen. Das Verhalten der installierten Version muss gezielt geprüft werden; keine globale Absenkung der Makrosicherheit. [Microsoft: AutomationSecurity](https://learn.microsoft.com/en-us/office/vba/api/access.application.automationsecurity).

Dieser Weg ist eine vorbereitete Alternative, noch kein durchgeführter nebenwirkungsfreier Export. Die synthetische Importprobe und die Beurteilung eventuell vorhandener ActiveX-/externer Objektbindungen gehen der Originalkopie voraus. Wenn dieser Weg die konkreten Grenzen nicht erfüllt, verbleiben die Bindungen offen; es wird keine Ersatzformel oder vorgetäuschte Originalabnahme erzeugt.

## Zurückgestellter ursprünglicher VM-Plan (RF-R0 bis RF-R5)

Die folgende Tabelle dokumentiert den ursprünglichen Gastweg. Er ist mangels Installationsmedien zurückgestellt und wird derzeit nicht ausgeführt. Aktueller nächster Kandidat ist RF-E1 im vorhandenen Access; die Gastschritte sind keine gleichzeitig aktive Umsetzungspflicht.

| Schritt | Konkreter Aufbau / Nachweis | Ergebnis vor dem nächsten Schritt |
|---|---|---|
| RF-R0 Umgebung | Eigene Testidentität, zur Referenz passende und zuvor tatsächlich geprüfte Access-Architektur; keine produktiven Zugangsdaten, keine Host-Laufwerke, keine beschreibbaren Hostfreigaben, keine Zwischenablage-/Geräteweitergabe. Nach Bereitstellung Netzadapter trennen; anschließend fehlende Netzwerkwege im Gast prüfen. | Gast-/Rechnerkonfiguration, Access-Version und beobachtete Netz-/Freigabegrenzen gebunden. OS-Trennung begrenzt den Hostzugriff, verhindert nicht automatisch jede lokale Nebenwirkung im Gast. |
| RF-R1 Master | Bereits gebundene private ACCDB-Kopie als Eingabe, SHA256 `2b48ce8dec5e0126072e0bc24f07b754b8b64af0651b080d257dcb1b0c8f13bc`. Unveränderliche Masterkopie getrennt von einer frischen Arbeitskopie. Keine vorhandenen Klientenzeilen exportieren oder als Testeingaben verwenden. | Dateihash/Größe vor Transfer, nach Transfer und vor jeder Arbeitskopie. Ursprung enthält Daten; das Kopieren einer ganzen Datei ist keine Anonymisierung. |
| RF-R2 Startgrenzen | Zuerst mit leerer synthetischer Accessdatei und künstlichen AutoExec-/Startformular-Markern prüfen, dass der gewählte Öffnungsweg diese nicht ausführt. Geplante Makrosperre und Start-Bypass getrennt nachweisen; keine pauschale globale Vertrauensfreigabe. Zusätzlich datenbankspezifische Start-/Bypasseigenschaften der Original-Arbeitskopie rein lesend ohne Access-Start erfassen und deren Abweichungen berücksichtigen. Eine getestete erzwungene Ausführungssperre muss auch bei deaktiviertem SHIFT-Bypass wirken; sie ist hier nicht eingerichtet oder nachgewiesen. | Synthetische Probe allein erlaubt keine Originalöffnung. Nicht ausführenden Öffnungsweg gegenüber den konkreten Originaleigenschaften nachweisen; andernfalls bleiben Originalöffnung und Export offen. |
| RF-R3 Definitionsexport | Erst im geprüften Aufbau Objektdefinitionen exportieren: Formulare, Reports, Makros, Module, Querydefinitionen. Keine Formulare/Reports zur Anzeige öffnen, keine Berechnungen oder Aktionsabfragen ausführen. Rohdefinitionen privat, nur bereinigte Bindungsmetadaten in den Modulbericht. | 105 bekannte Form-/Report-/Modul-/Scriptobjekte gegen eigenes Exportinventar; Querydefinitionen separat gegen den gebundenen Querybestand prüfen. Event-/RecordSource-/ControlSource-/Makroaufrufe samt Exporthash. Fehlende/gesperrte Objekte und P-Code-/Quellparität gesondert offen halten. |
| RF-R4 Synthetische Referenz | Frische abgeleitete Arbeitskopie mit nachgewiesen synthetischen Geschäftstabellen und explizit neutralisierten externen Links. Änderungen an Startup/Links/Inhalten einzeln diffen; aus dieser Kopie keine unveränderte Gesamtlaufzeitparität ableiten. Danach ausgewählte Berechnungen mit festen Eingaben und Fehler-/Abbruch-/Rundungsfällen. | Jede Referenzausgabe an Quell-/Query-/Funktionsrevision, Eingabe, Version und Testmodus binden. 17 Parameterlisten und fünf Linkziele vorher klären; keine Ersatzformel erfinden. |
| RF-R5 Wiederherstellung | Gast-/Umgebungssnapshot zurücksetzen; frische Masterableitung herstellen. Nur ausgewiesene Exportartefakte nach Stop der Gastprozesse in privaten Ablagebereich übernehmen, dort Hash und Inhaltsgrenzen prüfen. | Ursprüngliche Datei und dauerhafte Liveinstanzen unverändert; kein Nachweis durch bloßes Löschen einer Arbeitskopie. |

Die benötigte konkrete Umgebung und ihre Bereitstellung sind noch offen. Ein vorhandenes Startmenüsymbol, COM-Registrierung oder eine gehaltene Umschalttaste reicht dafür nicht aus.

## Fortschreibung vom 11.10.2026: RF-E1-Startgrenze

Die frühere Aussage „noch kein Access-Start“ beschreibt den Vorbereitungsstand vom10.10. Zwei tatsächliche COM-Aktivierungsversuche am11.10. scheiterten mit `80080005`, bevor ein Access-Automationsobjekt erworben oder eine Datenbankaktion aufgerufen wurde. Keine Originalöffnung oder Originalimport; nach den Versuchen kein Access-Prozess beobachtet. Ein möglicher kurzzeitiger Prozess während COM-Aktivierung wurde nicht kontinuierlich erfasst. Synthetischer Import/Export und Positivkontrollen bleiben **NOT_RUN**, RF-E1 ist nicht bestanden.

Aktueller Quellenstand separat gesichert; alte Extraktionen bleiben an die alte Byteversion gebunden. Vor erneutem Hostlauf Automationsumgebung und Blank-/Form-/Reportvorlagen prüfen. Kein Office-/COM-/Trustcenterumbau durch diese Fortschreibung. Rein statischer frischer RMF-Vergleich und unabhängige P3-Pakete können vorher fortgesetzt werden. Vollständige Belege und aktuelle Harness-/Reviewgrenzen im [RF-E1-Prüfbericht](AURELIA_P3_RADIFARBEN_SYNTHETISCHE_ACCESSPROBE_2026-10-11.md).

## Herstellerbelege und Grenzen des Exports

Microsoft beschreibt `Application.SaveAsText` für den Text-Export von Access-Objektdefinitionen. Das eignet sich als Exportkandidat im isolierten Aufbau; es ersetzt weder die Ausführungsprüfung noch einen unabhängigen P-Code-Vergleich. Für die installierte Version muss der tatsächliche Export erst bestätigt werden. [Microsoft: SaveAsText](https://learn.microsoft.com/en-us/office/client-developer/access/desktop-database-reference/application-save-as-text).

Microsoft beschreibt den SHIFT-Bypass von Startoptionen und AutoExec; `AllowBypassKey=False` kann ihn jedoch sperren. Deshalb wird die konkrete Sperr-/Bypasswirkung zuerst synthetisch nachgewiesen. Diese Bedienfunktion ersetzt keine Netz-/Hostisolation. [Microsoft: Startoptionen umgehen](https://support.microsoft.com/en-us/access/bypass-startup-options-when-you-open-a-database).

## Für P4/P5 mitnehmen

Objektdefinition, VBA-Quellrevision, unbekannter kompilierter Zustand, Query-/Parametervertrag, externe Referenz, Bildschirm-/Timerzustand und fachlicher Datensatz sind getrennte Bindungen. Eine spätere zentrale Datenbankentscheidung muss diese Aufnahme verwenden; noch keine Access-Formel portieren oder Modul_Template normativ erweitern. P3 insgesamt und P0 bleiben offen. Die nächsten unabhängigen Morphic-Katalogproben können ohne diesen Windows-Gast weiterlaufen.


### Zeitliche Präzisierung der Abschlusskontrolle

Abschlussmetadaten um09:48UTC: ein später gestarteter Access-Prozess (PID37784, Start09:06:20UTC, Office16, Sitzung1) vorhanden. Die unmittelbar nach den COM-Versuchen aufgenommenen Nullbestände bleiben zeitbezogene Befunde. Ursache/Eigentum und eine mögliche Datenbanköffnung dieses späteren Prozesses sind unbekannt; keine Bedienung oder Beendigung vorgenommen. Alle acht Listeneridentitäten unverändert; SOURCE_FINAL.json bestätigt weiterhin die drei Quellenhashes, Rechte und fehlenden Original-Lock. Daraus keine lückenlose Prozess-/Originalöffnungsbeobachtung ableiten.


## Klarstellung zur aktuellen Access Installation vom 11.10.2026

Aktuelles Access unterstützt das ACCDB-Format grundsätzlich. Der Betreiber bestätigt manuelle RadiFarben-Lauffähigkeit. Die bisherige RF-E1-Grenze betrifft COM-Aktivierung vor jeder Datenbankaktion; sie belegt keine Inkompatibilität der RadiFarben-Version. Office14-Registrystartpfad und vorhandenes Office16 bleiben ein konkreter Diagnoseansatz, keine bewiesene Ursache. VBA-/Referenz-/Steuerelement- und Architekturparität weiterhin gesondert prüfen. [Microsoft Dateiformate](https://support.microsoft.com/en-us/access/which-access-file-format-should-i-use), [32-/64-Bit-Kompatibilität](https://learn.microsoft.com/en-us/office/client-developer/shared/compatibility-between-the-32-bit-and-64-bit-versions-of-office). Keine Installation oder COM-/Trustcenteränderung in diesem Nachtrag.
