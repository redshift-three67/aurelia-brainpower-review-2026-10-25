# Entscheidung nach dem physischen Grundlagenlauf

Der freigegebene Lauf ist sicher abgeschlossen und unabhängig ohne materiellen Widerspruch geprüft. Aktuelle interne DB-Pfade, Dateibelegung und lokale Programm-/Paketzuordnung sind beobachtet. Der vollständige zusätzliche physische FS-/DB-/Temp-/Recovery-Bedarf ist weiterhin unbekannt. Weitere reine Bestandsinventuren sind nicht vorgeschlagen.

| Weg | Inhalt und Grenze |
| --- | --- |
| **A — begrenzten Praxisnachweis vorbereiten (Empfehlung)** | Einen isolierten Import-/Laufzeitversuch mit Abbruch, Fehlererhalt und Wiederherstellung konkret planen, lokal implementieren/testen und unabhängig prüfen. Feste Eingaben, byte-/inode-/zeit-/ressourcenbezogene Schutzgrenzen und ausreichendes Kontroll-/Recovery-Budget müssen vor einem Start belegt bzw. als Restunsicherheit ausdrücklich entschieden werden. Tatsächliche Import-/Daemon-/Container-/Schreib-/Cleanup-Aktionen erhalten erst danach eine neue konkrete Einmalfreigabe. |
| **B — theoretische Belege vertiefen** | Weitere quellengebundene Allokations-/Implementierungsbelege untersuchen. Fehlende privilegierte Ext4-Metadaten oder tatsächlich wirksame Laufzeitoptionen benötigen jeweils einen gesonderten vorbereiteten und freigegebenen Zugriff. Kein zugesicherter vollständiger Obergrenzennachweis aus den bisher vorhandenen Quellen. |

Die Entscheidung betrifft zunächst nur die Vorbereitung des gewählten Weges. Sie erlaubt keinen Serverstart, Rootzugriff, Import, Producer-Lauf, Build, Ressourcenwechsel, Löschvorgang oder kostenpflichtigen Scan.

Für Weg A sind vor einer Ausführung mindestens erforderlich:

- Unveränderte Produkt-/Archivgrundlage und festgelegte Test-Implementierung/Optionen; keine Klientendatenübernahme.
- Deterministischer OCI-Producer/Validator mit synthetischen Fehler-/Integritätstests; keine implizite Importausführung.
- Vollständiger eigener Schreib-/Aufbewahrungsumfang und Schutzgrenzen für Daten, Metadaten, Inodes, temporäre Dateien und Kontrollbelege.
- Geprüfte Abbruch-/Stop-/Fehlererhalt-/Wiederaufbau- oder Restore-Schritte; keine automatische Löschung alter Images, interner DBs oder Marker.
- Unabhängiger Review des konkreten Pakets; anschließend genaue neue Ausführungsfreigabe.

Gemessene Höchststände hängen von Arbeitslast und Messabdeckung ab. Sie sind keine universelle mathematische Maximalgarantie. Diese Einschränkung darf weder durch eine Reservekonstante noch durch einen erfolgreichen Prozess-Exit verdeckt werden.

[Gebundene Entscheidungsgrundlage](../../runtime/rw-physical-basis-execution-20261024/NEXT_DECISION.json), [Ausführungsergebnis](../../runtime/rw-physical-basis-execution-20261024/RESULT.json), [unabhängiger Review](../../runtime/rw-physical-basis-execution-20261024/INDEPENDENT_REVIEW.json).
