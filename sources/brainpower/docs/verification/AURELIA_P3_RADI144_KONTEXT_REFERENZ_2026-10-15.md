# P3 – Radi144-Kontextreferenz: Werkzeug geprüft, Originallauf vor Start blockiert

Stand 15.10.2026. Betreiberfreigabe „Ja, fahre So fort“ gilt der unveränderten Charakterisierung der bekannten Zeittyp-/Registry-/ID-Inline-Befunde. Keine Produktreparatur. Prüfpunkt: `checkpoints/Aurelia-P3-Radi144-Context-20261015-062425Z`.

## Tatsächlich erreicht

| Schritt | Belegter Stand |
|---|---|
| Quellenbindung | Zehn benannte Quellhashes vor/nach dem gescheiterten Vorlauf stimmen mit den Pins überein; vollständige Kopien gesichert. |
| Werkzeugumfang | Acht ausgewählte AST-Definitionen unabhängig gebunden; zwölf synthetische Gruppen vorbereitet. Noch kein Originalkörper kompiliert/aufgerufen. |
| Werkzeugtests | Root führt aktuelle vier Werkzeuge mit vorhandenem Radi144-Python, `-I -S -B` und bereinigter Umgebung aus: 20 Tests bestanden, keine Skips; Hashes vor/nach gleich. |
| Unabhängiger Vorreview | Astra/medium prüft eingefrorenen SPEC→QUALITY-Stand und rechnet Hashes/Outputbelege nach: keine materiellen Werkzeugblocker. Review ist keine Ausführungserlaubnis. |
| Erster Ausführungsversuch | `context-run-1` wird angelegt, scheitert in der Git-Vorprüfung. `launch_attempted=false`: Der Probe-Kindprozess wird nicht gestartet, Originalaufrufe bleiben 0. |
| Folgelauf/Vollvergleich | Nicht ausgeführt. `context-run-2` nicht angelegt; kein numerischer Vergleich und keine neue Originalreferenzabnahme. |
| Zustand nach Halt | Gate wieder exakt geschlossen; vier Werkzeughashes gleich. Git-HEAD/-Status können in diesem Testkontext nicht bestätigt werden. |

## Ursache und Sicherheitsgrenze

Git meldet für alle drei reinen Leseprüfungen (`root`, `HEAD`, benannter Porcelainstatus) vor und nach dem Versuch `fatal: detected dubious ownership`. Repository-Eigentümer ist `Hubert111`, ausführendes isoliertes Konto `CodexSandboxOffline`. Das ist ein belegter Git-Vertrauens-/Eigentümerschaftsblock, kein belegter Radi144-Algorithmusfehler. Welche konkrete bisherige Gitkonfiguration im bereinigten Prozess fehlt, ist noch nicht nachgewiesen.

Primärbelege: `runs/context-run-1/controller.json` mit vollständigen Fehlermeldungen sowie `ROOT-EXECUTION-LAUNCHES.json`. Der ursprüngliche Vorprüffehler und der ebenfalls fehlgeschlagene Git-Nachcheck bleiben getrennt erhalten. Es gab keinen Timeout und keinen blinden Retry. Die zehn Quellbytes sind gleich; daraus folgt keine erfolgreich geprüfte Git-HEAD-/Indexgleichheit.

Wie vom Betreiber gefordert, bleibt die Ausführung bei diesem unerwarteten Problem angehalten. Laufkennung 1 ist als Vorprüfversuch verbraucht und wird nicht überschrieben. Keine globale Gitkonfiguration, Eigentümerschaft oder ACL wurde geändert.

## Empfehlung für den nächsten freizugebenden Schritt

Nur im neuen Prüfcontroller einen prozessbezogenen Git-Vertrauenseintrag für den exakten, zuvor auf gewöhnliche Pfadkomponenten geprüften Radi144-Pfad vorsehen (`-c safe.directory=C:/Users/Hubert111/Documents/Radi144`). Keine Wildcard, kein globaler Konfigurationseintrag und keine Änderung am Produktrepository. Das ist ein begrenzter Lösungsentwurf, noch keine getestete Korrektur.

Danach gezielte negative Werkzeugtests für falschen Pfad und persistente Konfiguration, unabhängigen Vorreview und einen neuen Prüfpunkt mit zwei frischen Kennungen verwenden. Quellen-/AST-/Werkzeug-/HEAD-/Raw-XY-Prüfungen bleiben erforderlich. Keine frühere erfolgreiche Referenz oder nicht gestartete Probe als neuer Erfolg übernehmen.

## Nachweisqualität und historische Grenzen

Die erste Probe-Rotfassung dokumentiert einen erwarteten Fehler und acht Skips; sie ist kein erfolgreicher Werkzeugnachweis. Ein späterer historisch `green03` genannter Lauf besitzt tatsächlich zwei Fehlerwartungsfehlschläge und einen Fehler bei 14 synthetischen Tests. `context-probe-worker-green-20261015-02` besitzt ebenfalls Exit 1; seine Manifestphase wurde zwischenzeitlich geändert und zurückgesetzt. Exakte Zwischenmanifestbytes sind daher nicht belegt. Diese Verzeichnisse bleiben mit den tatsächlichen Fehlerausgaben und `WORKER-NOTES.json` erhalten und gelten nicht als finale Grünbelege. Maßgeblich sind die unveränderten vier Testkopien und der erfolgreiche isolierte Root-Lauf `ROOT-final-tooltests`.

Frühere Gitbelege wurden mit `strip()` gekürzt. Der neue frische Rohstatus lautet vor dem Ausführungsversuch ` A AGENTS.md` (Indexspalte leer, Arbeitsbaum A). Historische Bezeichnungen als „vorgemerkt“ beweisen keinen Indexzustand; eine behauptete Gleichsetzung unterschiedlicher XY-Zustände ist nicht belegt. `SOURCE-BASELINE.json` enthält eine ältere breitere 22-Definitionsaufnahme; der aktuelle Acht-Definitionsumfang ist separat in `CURRENT-FUNCTION-CONTRACT.json` gebunden.

Luna/max bereitet Werkzeug und synthetische Tests vor, Root führt die aktuelle isolierte Werkzeugsuite und den einmaligen Vorprüfversuch aus, Astra/medium prüft unabhängig. Ein überlappender Arbeiter wurde angehalten; alleinige Schreibzuständigkeit vor dem finalen Freeze hergestellt. Keine Originalmodule/-klassen, Pydantic, HTTP, Engine, echten Registry-/Sessionstores oder Datenbestände ausgeführt. Auditguard ist keine Betriebssystemsandbox.

## Fortgeltender Gesamtplan

Dieser Punkt schließt P3 nicht ab. Weitere Signatur-/Kontext-/Workflowreferenzen, führende Morphic-Quelle, RF-E1 und Linux-/Backendnachweise bleiben offen. Vollständige siebenmodulige P4-Matrix einschließlich Aurelia und Modul_Templates vor P5-Datenbankentscheidung; P6–P8/S4.8 separat. Keine Liveinstanzen-, Server-, WSL-, Access-, Cloud-, Routing-, Algorithmus- oder normative Templateänderung. Lokaler begrenzter Prüfpunkt; kein F:-, Server-, Schlüssel- oder Gesamtprojektbackup.


## Ergänzung – neue Freigabe und erfolgreicher getrennter Prüfpunkt

Die zuvor offene begrenzte Controllerkorrektur wurde vom Betreiber genehmigt. Neuer Punkt mit prozesslokaler, exakt pfadgebundener Git-Prüfung und23 erfolgreichen Werkzeugtests: zwei neue Referenzläufe mit je12 Gruppen/42 Erwartungen bestanden; vollständige Ergebnisse nur ohne Label gleich. Quellen/AST/Werkzeuge/HEAD/benannter Raw-XY vor/nach gebunden; Gate geschlossen. Unabhängiger Vor-/Ergebnisreview ohne materiellen Blocker. Der oben beschriebene alte Fehlversuch und seine Belege bleiben unverändert; keine nachträgliche Umwertung in einen Erfolg. Aktuelle Details im [neuen Ergebnisbericht](AURELIA_P3_RADI144_KONTEXT_GITSCOPE_2026-10-15.md). Keine Gesamt-P3-Abnahme oder Produktreparatur.
