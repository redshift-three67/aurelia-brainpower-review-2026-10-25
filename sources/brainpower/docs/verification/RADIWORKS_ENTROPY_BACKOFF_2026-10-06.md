# RadiWorks: Stochastic-Korrektur und Abschluss der isolierten Nachweise

Stand: 2026-10-06T00:16:04.872803+02:00. **Kandidat geprüft, noch keine Live-, Quell- oder Portableübernahme; keine Aurelia-Freigabe.**

## Fehler und minimale Korrektur
C23 wiederholte nach einer fehlgeschlagenen oder ungültigen random.org-Antwort den Abruf bei jeder folgenden Ziehung. Ein künstlicher aktiver Falllauf erreichte HTTP 200; ein weiterer blieb bis zum 45-Sekunden-Clienttimeout offen. Sein endgültiger Serverausgang ist unbekannt. Der eigene Prüfdienst wurde kontrolliert beendet.

Der RED-Test reproduziert zwei Abrufe statt eines nach einem synthetischen OSError. Ein weiterer RED-Test belegt konkurrierende Abrufe ohne Lock. Die Korrektur verwendet eine monotone Fehlersperre von 60 Sekunden ab Fehlerende und einen Lock für Nachladen und Cacheentnahme. Während der Sperre bleibt der vorhandene OS-Fallback nutzbar. Erfolg setzt die Sperre zurück.

Webcam-Vorrang, gesunde Cacheseeds, Java-Ziehungsalgorithmus, seeded und Journalschema bleiben unverändert. Der Cooldown gilt pro Sourceinstanz und wird beim Neustart zurückgesetzt. Er ist keine globale HTTP-Ratenbegrenzung. Der Lock macht den gesamten EntropyProvider nicht automatisch threadsicher.

## Produktbindung und Tests
- Manifest mit 131 Produktdateien: Root prüfte alle SHA-256 unabhängig. 130 Dateien sind bytegleich mit C23; nur `engine/src/radiworks/entropy.py` ist geändert. Neue Regressiontests liegen außerhalb der Produktliste.
- Provider-SHA: `964ee94c63c0c6026c6bf491e3a5660ddc9beb4bd5d1e8d511ec56c535d4f835`.
- Manifest-SHA: `60ca99f2fcb5e2a02cda2e7a81983e6b01a26edc4ffed8f981616d00d08b806a`.
- Finale fokussierte Suite: **21 bestanden**, einschließlich zwei ThreadPool-Tests.
- Vollständige normale Engine-Suite: **667 bestanden, 19 übersprungen, 1 Warnung**, Exit 0. Übersprungen: drei Windows-Symlinktests und 16 Tests ohne das optionale CPU-Profil. Bekannte Starlette/httpx-DeprecationWarning. Kein neuer vollständiger CPU-Profildurchlauf.
- Astra 6/medium prüfte unabhängig den konkreten Providerdiff mit diesem SHA: kein konkreter Defekt gefunden. Zusätzliche Paralleltests und finales Manifest lagen beim ursprünglichen Review noch nicht fertig vor; Ausführung und Manifestprüfung wurden danach von Luna und Root bestätigt. Review ist keine Freigabe.

## Eigener TCP- und Prozessneustartnachweis
Port 8111, eigener Dienst mit Identitätsprüfung, eigenes künstliches Home. Keine Mutation auf 8103–8109, 8090 oder 8110.

Drei verschiedene persönliche Kontexte mit gleichem Originalseed und Katalog ergaben exakt gleiche Raten. Anschließend liefen zwei Produktionsanalysen im Stochastic-Modus bei aktivem Fall erfolgreich: synthetischer HTTP-Fehler, realer OS-Fallback, nur ein fehlgeschlagener Callback vor dem Neustart und getrennte Sitzungen. Laufzeiten etwa 0,636 und 0,648 Sekunden. Kein externer Egress und keine physische Kamera. Dies ist kein allgemeiner Leistungsbenchmark.

Echter Childprozesswechsel 18940 → 34304: acht Fall-/Draftdateien blieben bytegleich. Die gespeicherte Sitzung wurde mit authentifiziertem Journalcheckpoint wieder geöffnet; eine weitere GV-Abfrage gelang. Die alte Queue blieb beendet. Derselbe Testschlüssel wurde vom Elternprozess im RAM an beide Prozesse vererbt. Das prüft keine externe Schlüsselverwahrung und keinen Windows-Neustart. Alle eigenen Prüfdienste sind beendet.

Der erste TCP-Harnessstart scheiterte an seiner hinter dem Static-Mount registrierten Testidentitätsroute, bevor Fallmutationen liefen. Nur der Harness wurde korrigiert; erster Testhomebestand und Fehlerbeleg blieben erhalten. Die erfolgreiche Wiederholung verwendete ein frisches Home. Ein früherer Passport-KeyError gehörte ebenfalls zum Harness. Fehlgeschlagene Versuche wurden nicht als erfolgreich gewertet.

Eigene HTTP-Proben bestätigen fehlende persönliche ContextReference bei Direct- und Image-Broadcast. Die Auto-Lücke ist aus dem konkreten Enqueue-Aufruf belegt. BC1 bleibt der separate Entwurf im [Vektor-/Datenrestplan](RADIWORKS_VEKTOR_DATENVERTRAG_RESTPLAN_2026-10-05.md).

## Echter GV2-Langlauf im unveränderten C23
Drei getrennte künstliche Fall-/Sitzungsbindungen, reale Produktionsuhr und Worker sowie unabhängige OS-Beobachtungsziehungen. Zwei tatsächliche 1260-Sekunden-Zyklen erzeugten sechs Historienzeilen: zuerst drei Baselines, danach drei Vergleiche mit Richtung und Delta. Sechs ursprüngliche Fall-/Draftdateien blieben bytegleich.

Die Historie blieb nach einem App-Neustart erhalten; Intervalle waren aus und die Queue leer. Dieser GV2-Harness belegt keinen Prozess- oder Windows-Recoverytest. Testschlüssel nur im RAM. Zahlenänderungen sind kein Nachweis gesundheitlicher Wirkung.

## Offene Grenzen
1. Der Kandidat ist noch nicht in den sieben Dauerinstanzen, im kanonischen RadiWorks, in Modul_Templates oder Portable5 rc1. Die Übernahme muss aktive Aufträge und Fälle bewahren; keine stillen Stops oder Umstellungen.
2. USB-Kameraprobe über drei Minuten: 1 von 200 Kandidaten, Feed 0. Kein Hotbits-Qualitäts- oder Kamera-Stochastic-Nachweis. Frage zur tatsächlichen bewegten Umgebung offen.
3. BC1: gemeinsame Zielbindung für alle Broadcast-Startwege. Danach ausgewählte Originaleinstellungen als getrennte Erweiterungen mit erklärter Wirkung.
4. Zentraler Modul-, Katalog-, Owner-, Abo- und Jobdatenvertrag vor TXT-Nutzerimport. Ein Postgres ist Sollplanung, keine implementierte Hostautorisierung. Modulformate nicht ungeprüft vereinheitlichen.
5. Keine S4.8-, Matrix- oder Aurelia-Integrationsfreigabe. Ego Cleaner ausgeschlossen, nur reservierter Erweiterungspunkt im Plan. Komfortpaket zurückgestellt; neue CPU/CUDA-, Kozyrev- und Hardwareanbindungen optional.

## Nachvollzug
Belege unter `runtime/rw-entropy-backoff-20261005/evidence` und dessen Produktmanifest sowie `runtime/rw-local-closeout-20261005`: COMPLETE, TWO_CYCLES, TCP_FALLBACK_COMPLETE, CHECKS_SUMMARY, VECTOR_STOCHASTIC_LIMITATION, LIVE_READONLY und PRODUCT_UNCHANGED.

Für diese Proben wurden keine echten Fallinhalte oder externen Schlüssel gelesen. Tatsächliche Helfer: Luna 6/max für Korrektur, Regressionen, Manifest und Datenplan; Astra 6/medium für Daten- und Providerreview. Root führte Browser-, Kamera-, Vektor-, TCP- und GV2-Nachweise aus und konsolidierte sie. Gewählte Chatleitung Sol 6.1/high; keine gemessene Tokenersparnis und kein geändertes Hermes-Anwendungsrouting.

Diese neuen Belege sind noch nicht in den abgeschlossenen F:-Archiven `20261005-185205`.
