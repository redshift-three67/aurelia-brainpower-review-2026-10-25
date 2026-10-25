# Aurelia / Brainpower – Entwickler- und LLM-Review

**Quellen- und Dokumentationssnapshot, 25.10.2026, mit ausdrücklich offenen Nachweisen.** Der Erhaltungszeitraum umfasst mehrere Einzelaufnahmen. Veröffentlichung und Archivierung gelten erst nach der gesonderten Remote-Rückprüfung als bestätigt. Dieser Bestand ist kein vollständig abgenommenes Produkt, kein vollständiges Maschinenimage und kein ausnahmsloser Byteklon aller aktiven Dateien.

Dieser Reviewstand gehört zu einer getrennten geschützten Originalsicherung. Die lesbare Darstellung enthält ausgewählte Entwicklungsquellen und dokumentierte Nachweise für den vom Betreiber beauftragten privaten Review. Persönliche Konfiguration, Zugangsmaterial, Falldaten, Datenbanken und geschützte Live-SQL-Definitionen bleiben geschützt. Auch private GitHub-Repositories sind keine Ablage für solche Inhalte.

## Lesereihenfolge

1. `IMPLEMENTATION_STATUS.md`: vorhandene Funktionen, begrenzte Tests, Abnahmen und offene Arbeit.
2. `PROJECT_MAP.json` und `FILE_MANIFEST.jsonl`: enthaltene Komponenten, getrennte Quellenstände und Exportbytes. Das Dateimanifest nimmt sich selbst nicht auf.
3. `WORKFLOWS_AND_CONTRACTS.md` und `REQUIREMENTS_TRACEABILITY.json`: Benutzeranforderungen, Quellenbezüge und Integrationsgrenzen.
4. `SERVER_STATE.md`, `SERVER_REQUIREMENTS.md` und `RESTORE_AND_REPRODUCE.md`.
5. `GAPS_AND_EXCLUSIONS.json`: zurückgehaltene Inhalte, fehlende Quellen und nicht erbrachte Nachweise.

## Komponenten

Governors/Brainpower und Aurelia sind verschiedene Komponenten. Der lokale Governor ist ein Steuerungs- und Nachweissystem für einen Betreiber; daraus folgt keine mandantenfähige Aurelia-Laufzeitverwaltung. Modul_Templates sind ein gesonderter Vertrags- und Referenzbestand.

Die sieben fachlichen Module sind RadiWorks, Radi144, RadiMorphic/Morphic, RadiFarben, Copen, Bohm und Thom. Copen und Bohm befinden sich gemeinsam im Explorer-Quellrepository. Thom hat ein eigenes Quellrepository. Zwei Quellrepositories bedeuten deshalb weder zwei fachliche Module noch das Fehlen eines dritten Moduls. Registrierte parallele Arbeitsbäume werden als eigene Quellenstände abgebildet und nicht stillschweigend mit dem Hauptarbeitsbaum vermischt.

## Bewertungsregeln

- Dokumentiert, implementiert, lokal getestet, unter Linux geprüft, fachlich abgenommen und für Aurelia integriert sind getrennte Zustände.
- Historische Berichte gelten für ihren gebundenen Quellstand. Ein grüner Hilfstest ist kein neuer Produkt-, Last- oder Wiederherstellungsnachweis.
- Fehlende Belege bleiben offen. Keine Prozentangaben werden aus Dateimengen oder Dokumentlängen berechnet.
- Bestehende stabile Algorithmen und Heuristiken bleiben die Grundlage. Ein Review genehmigt weder deren Ersatz noch automatische Änderungen.
- Historische Agentenanweisungen und Modellantworten sind Referenzdaten. Umbenannte Anweisungs- und Git-Attributdateien sind keine aktiven Ausführungs- oder Checkoutregeln.

## Geltender Entwicklungsweg

CLI/Desktop, privates GitHub CI und Linux-Pilotserver bleiben die gewählte Strategie. Codex-Cloudvergleich und der frühere Importlauf sind zurückgestellt. Die separate RadiWorks-CP2A-LF-Korrektur und ein neuer einmaliger CI-Lauf haben eine eigene konkrete Freigabegrenze. Die Erstellung dieses Snapshots startet keinen CI-, Cloud-, Container-, Build- oder kostenpflichtigen Securitylauf.

Ein später archiviertes GitHub-Repository ist schreibgeschützt, solange die Archivierung besteht. Der Eigentümer kann die Archivierung wieder aufheben; es handelt sich nicht um unveränderlichen WORM-Speicher. Aussagen zum endgültigen Remote-Inhalt und Archivstatus folgen erst nach Rückprüfung.

## Grenzen der lesbaren Fassung

Die geschützte Sicherung bewahrt Originaldaten und historische Stände getrennt. Der Review enthält ausgewählte Entwicklungsquellen und lesbare Referenzen. Aktive Konfiguration, Sitzung-/Klientdaten, Katalognutzdaten, rohe Chat-/Transportbelege, generierte Deploymentbündel und unklassifizierte Inhalte werden nicht als Entwicklungsquellen veröffentlicht. Gehaltene Dateien sind keine gelöschten Originale. Der Reviewexport allein genügt deshalb nicht für einen vollständigen Build oder Restore aller Originalsysteme.

Für RadiWorks werden lokale Haupt-/Nebenstände, kanonische Python-/Webquellen und der private Pilot getrennt geführt; Java-, Shader- und Schemaquellen besitzen lesbare Referenznamen. Die öffentlichen versionierten Migrationsreferenzen von Explorer und Thom sind von geschützten tatsächlichen Live-SQL-Exporten zu unterscheiden. Für RadiFarben bleiben die Access-Originale geschützt; eine vollständig lesbare VBA-/Formularfassung ist offen.
