# Wiederherstellung und Reproduktion

**Kein ausgeführter Gesamt-Restore.** Die folgenden Hinweise erklären die Sicherungsform und Voraussetzungen. Sie sind keine Anweisung zum Überschreiben laufender Programme, zur automatischen Wiederholung unterbrochener Jobs oder zur Freigabe eines Produktstands.

## Geschützter Erhaltungsstand

Die Originalsicherung enthält getrennte Gitspiegel, aktuelle Arbeitsbaumdateien, frühere Stände, Datenbanksicherungen und private Metadatenbelege. Die vollständige Quellzuordnung mit vertraulichen Pfaden und Geheimnishashes bleibt ausschließlich geschützt. Die Reviewfassung enthält davon nur ausgewählte Dateizuordnungen und neutrale Ausschlusskategorien.

Dateiarchive speichern die Originaldatenströme als numerisch benannte Blobs und ihre Zuordnung in `MANIFEST.json`. `relative` bezeichnet den Originalpfad innerhalb der jeweiligen Quelle; der Standarddatenstrom und gegebenenfalls zusätzliche NTFS-Datenströme besitzen eigene Bytezahlen und SHA-256. Ein abgeschlossenes ZIP allein ist kein ausreichender Nachweis: Es müssen der separate Abschlussbeleg, die erwartete Dateimenge und die Rücklesehashes passen. Fehlgeschlagene Teilarchive bleiben ausdrücklich unbestätigt.

Geschlossene Datenbankgruppen besitzen einen zusätzlichen Gruppenbeleg für Hauptdatei und bekannte Begleitdateien. Absichtlich leere, beschädigte oder undurchsichtige historische Testfixtures wurden unverändert erhalten; der Dateierhalt ist keine semantische Datenbankreparatur. Die separat erstellten logischen SQLite-Sicherungen wurden als selbstständige Datenbanken geprüft. Sie sind keine bytegleichen physischen Quellkopien und keine gemeinsame atomare Momentaufnahme aller Datenbanken.

Aktive Protokolle sind abgegrenzte, zweimal hashgleich beobachtete Präfixe. Spätere Logzeilen fehlen. Zwei gleiche Beobachtungen beweisen keine durchgehend unveränderte Quelle. Genau benannte aktive Instanzsperren besitzen nur Metadatenbelege; deren ungelesene Nutzbytes dürfen nicht durch erfundene „Originalbytes“ ersetzt werden. Betriebssystemsperren entstehen bei einem neuen Anwendungsstart neu.

## Sichere Rückprüfung

1. Zuerst den endgültigen Umfang, die Quellenmanifeste und alle offenen Ausnahmen lesen. Keine unbestätigten Teilarchive als vollständige Quelle verwenden.
2. Ausschließlich in ein neues isoliertes Ziel zurücklesen. Relative Pfade, Zielgrenzen, Dateikollisionen, Symlinks und Junctions vor einer Rekonstruktion prüfen.
3. Blobgrößen und SHA-256 gegen die gebundenen Manifeste prüfen. Erst danach Dateien ihren ursprünglichen relativen Namen zuordnen.
4. Windows-Datenströme und ACL-Metadaten erfordern geeignete NTFS-/Berechtigungsvoraussetzungen. Die Sicherung ist kein vollständiges NTFS- oder Maschinenimage; unter anderem SACLs, physische Sparse-/Kompressionsbelegung und jede Verzeichniseigenschaft sind nicht vollständig reproduziert.
5. Datenbanken nur im isolierten Ziel und mit geeigneten Modul-/Schemaversionen öffnen. Erforderliches Zugangsmaterial bleibt getrennt geschützt. Einen neuen Governor-Store nicht zu Diagnosezwecken gegen das aktive Originaljournal starten.
6. Build, Tests, Recovery und fachliche Abnahme im vorgesehenen CI-/Pilotpfad nachholen. Historische Testergebnisse sind an ihre ursprünglichen Quellen gebunden.

## Git- und Quellstände

Die vollständigen lokalen und entfernten Projekt-Gitspiegel sind von den jeweils gesicherten Index-/Arbeitsbaumständen zu unterscheiden. Für Brainpower wurde das übergeordnete persönliche Profilrepository bewusst nicht vollständig geklont. Die eine projektrelevante Historienänderung, ihr Original-Commitobjekt, der eine projektrelevante Indexeintrag und sein Originalblob wurden getrennt erhalten. Die gefilterte Git-Rekonstruktion kann Commit-IDs ändern; sie ist kein bytegleicher Clone des persönlichen Profil-Git.

Das ältere Governors-Archiv ist für seine 300.543 ursprünglich manifestierten Dateien erneut gegen deren ursprüngliche SHA-256 erhalten. Der erste Versuch hielt beim 60-Sekunden-Quellbudget einer 1,65-GB-Datei an. Das fehlgeschlagene Teilarchiv bleibt unbestätigt. Die separate Fortsetzung bestätigte genau die übrigen 5.543 Dateien; nur die große Einzeldatei erhielt ein geprüftes kooperatives 600-Sekunden-Quellbudget. Rücklesen und Nachprüfungen liegen außerhalb dieses Quellbudgets; ein harter Gesamtlaufzeitdeckel wird nicht behauptet. Eine vollständige frische Verzeichnisinventur dieses Altarchivs bleibt davon verschieden und offen. Die 44 oberen Original-Kontroll-/Manifestdateien sowie weitere 26 historische beziehungsweise ausgelagerte Bereiche mit 173.389 Dateien sind getrennt erhalten.

Historische Gitlink-Verweise können Inhalte außerhalb eines Hauptrepositories benötigen. Fehlende referenzierte Inhalte bleiben in der Lückenliste offen. Das bloße Fehlen von LFS-Pointern beweist nicht, dass alle externen Datenbank-/Storage-/Medienobjekte enthalten sind.

## Reviewdateien

Anweisungsdateien werden in der lesbaren Fassung als Referenzdateien umbenannt. Die Manifeste müssen solche Namensänderungen ausweisen; ihre Inhalte werden dadurch nicht zu neuen Ausführungsregeln. Vor einer absichtlichen isolierten Reproduktion sind ursprüngliche Pfade, Abhängigkeiten, Versionen und Rechte anhand der geschützten Quellenzuordnung zu prüfen. Der Reviewexport allein enthält weder alle Laufzeitdaten noch alle Zugangsvoraussetzungen.

## Server und Ausfallgrenzen

Die VPS-Aufnahme umfasst begrenzte aktuelle Metadaten und Konfiguration. Vollständige persistente Serverdaten, Provider-/Maschinenbackup und getesteter Gesamtwiederanlauf sind gesonderte offene Nachweise. Der Hauptserver ist nur historisch plus Zielanforderungen erfasst.

Neue Kopien älterer F:-Archive auf demselben Laufwerk schaffen keine unabhängige Absicherung gegen einen Ausfall dieses Datenträgers. Ein getrenntes Ausfallmedium beziehungsweise ein entsprechend geprüftes externes Backup ist durch diesen lokalen Erhaltungsstand nicht nachgewiesen.
