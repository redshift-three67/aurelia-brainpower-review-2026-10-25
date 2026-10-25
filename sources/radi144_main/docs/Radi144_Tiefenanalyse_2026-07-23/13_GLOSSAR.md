# 13 - Glossar

## API

Programmierschnittstelle. In Radi144 ist dies überwiegend FastAPI unter `/api/v1`.

## Artefakt

Eine erzeugte Datei wie PDF, XLSX, CSV, Log oder Audio. Das Artefaktmanifest speichert Metadaten zu einem Teil dieser Dateien.

## Backpressure

Mechanismus, der neue Arbeit begrenzt oder verzögert, wenn ein System bereits ausgelastet ist. Radi144 besitzt derzeit keine zentrale Backpressure für Analysen.

## Candidate / Kandidat

Eine zufällig erzeugte Ziffernmatrix, die gegen den Zielvektor bewertet wird.

## Client

Im Code ein Registryeintrag. Fachlich kann der Begriff Person, Gruppe, Bild, Ort oder generisches Analyseobjekt meinen; diese Mehrdeutigkeit ist eine Datenmodelllücke.

## Commit-Speicher

Unter Windows die Summe aus physischem Speicher und Auslagerungsdatei, die für Speicherzusagen verfügbar ist. Freier physischer RAM allein garantiert nicht, dass eine weitere Allokation möglich ist.

## CORS

Browserregel für Cross-Origin-Zugriffe. CORS ist kein Authentisierungs- oder Zugriffsschutz für beliebige Netzclients.

## Cosinusähnlichkeit

Mathematisches Maß für den Winkel zwischen zwei Vektoren. Der Wert kann sinnvoll sein, wenn der Vektorraum fachlich definiert ist. In Radi144 ist der Raum zufallsbasiert und nicht kalibriert.

## CSP

Content Security Policy. Browser-Sicherheitsrichtlinie, die unter anderem unerlaubte Skriptausführung einschränken kann.

## Deterministisch

Gleiche vollständige Eingabe und gleiche Ausführungsbedingungen liefern dasselbe Ergebnis. Radi144-Precision ist nur teilweise deterministisch.

## DPIA / DSFA

Datenschutz-Folgenabschätzung. Formale Prüfung hoher Datenschutzrisiken, insbesondere bei sensiblen Daten und neuer Technologie.

## Embedding

Vektorrepräsentation von Daten. Ein semantisches Embedding bildet ähnliche Bedeutungen typischerweise räumlich ähnlich ab. Radi144 verwendet hash-seedete Zufallsvektoren, keine trainierten semantischen Embeddings.

## EMF

Elektromagnetisches Feld. Das Radi144-Modul misst standardmäßig Systemtiming, Zufallsstatistik und Last als Proxy; dies ist keine kalibrierte Feldstärkemessung.

## Eventloop

Ausführungsschleife eines Async-Servers. Langer synchroner CPU-/GPU-Code blockiert den Eventloop eines Workers.

## Fail-closed

Bei fehlender/ungültiger Sicherheitskonfiguration wird Zugriff oder Start verweigert. Das Gegenteil ist fail-open.

## Ground Truth

Unabhängig bekannte korrekte Referenzwerte, gegen die ein Verfahren validiert wird. Für den Resonanzscore ist keine Ground Truth vorhanden.

## HMAC

Schlüsselbasierter Integritäts- und Authentizitätsnachweis. Im Gegensatz zu einfachem SHA-256 kann nicht jeder ohne Schlüssel gültige Werte erzeugen.

## Idempotent

Eine wiederholte Operation hat nach dem ersten erfolgreichen Durchlauf keinen zusätzlichen Effekt. Die Löschung ist nur teilweise idempotent, weil Teilausfälle den Retry erschweren.

## KI / Machine Learning

Modelle, die aus Daten gelernt wurden. Die untersuchte Kernengine enthält kein trainiertes KI-/ML-Modell.

## Lockfile

Datei mit exakt aufgelösten Dependencyversionen, häufig mit Hashes. Sie ermöglicht reproduzierbare Installationen.

## Lost Update

Zwei Prozesse lesen denselben Stand und speichern unterschiedliche Änderungen; der spätere Write überschreibt die Änderung des ersten Prozesses.

## Mandant

Abgegrenzte Organisation oder Nutzergruppe mit eigenen Daten und Rechten. Radi144 besitzt derzeit keine Mandantentrennung.

## Medizinprodukt

Rechtlich reguliertes Produkt mit medizinischer Zweckbestimmung. Ob Radi144 darunter fällt, muss anhand der tatsächlichen Zweckbestimmung und Vermarktung qualifiziert geprüft werden.

## Migration

Versionierter Übergang eines Daten- oder Datenbankschemas. Die aktuellen JSON-Versionen besitzen keine Migrationen.

## OOM

Out of Memory. Speicherallokation schlägt fehl. Im aktuellen Engine-Test trat ein OOM mit anschließendem nativen Prozessabbruch auf.

## PII

Personally Identifiable Information, also personenbezogene Daten wie Name, Geburtsdatum oder Kontaktdaten.

## Pseudonymisierung

Ersetzung direkter Identifikatoren durch ein Pseudonym. Die Person bleibt mit Zusatzwissen bestimmbar. Pseudonymisierung ist keine Anonymisierung.

## QMS

Qualitätsmanagementsystem. Für regulierte medizinische Software ist ein formaler QMS-Kontext typischerweise zentral.

## Rate Limit

Grenze für die Anzahl von Anfragen pro Zeit/Nutzer. Radi144 besitzt derzeit keine zentrale Rate-Limitierung.

## Readiness

Prüfung, ob eine Instanz tatsächlich Traffic verarbeiten kann. Ein statischer „active“-Text ist keine vollständige Readinessprüfung.

## Retention

Aufbewahrungsregel: welche Daten wie lange gespeichert und wann gelöscht werden.

## RPO

Recovery Point Objective. Maximal akzeptabler Datenverlust in Zeit, beispielsweise 15 Minuten.

## RTO

Recovery Time Objective. Maximal akzeptable Wiederherstellungsdauer.

## SBOM

Software Bill of Materials. Maschinenlesbare Liste aller Softwarekomponenten und Versionen.

## Scorekalibration

Nachweis, was ein Score quantitativ bedeutet. Ohne Kalibration darf ein Wert nicht wie eine Wahrscheinlichkeit oder Wirksamkeit interpretiert werden.

## Session

Logische Analysesitzung. In Radi144 wird der Begriff zwischen CLI, API und Browser unterschiedlich verwendet.

## SSOT

Single Source of Truth, die eindeutige führende Quelle. Radi144 hat bei Version, Konfiguration, Sessiondaten und Dokumentation mehrere konkurrierende Quellen.

## Transaktion

Mehrere Datenänderungen werden gemeinsam vollständig übernommen oder vollständig verworfen. Die JSON-Verwaltungsdomäne besitzt keine Mehrdateitransaktionen.

## Trust Boundary

Grenze zwischen unterschiedlich vertrauenswürdigen Komponenten oder Daten, beispielsweise Browser zu API oder API zu Dateisystem.

## WebSocket

Dauerhafte bidirektionale Netzwerkverbindung. HTTP-Middleware schützt WebSockets nicht automatisch.

## Worker

Separater Uvicorn-Prozess. Mehrere Worker erhöhen Parallelität, teilen aber keine Python-Objekte und schreiben aktuell in dieselben JSON-Dateien.

## Zufallsprojektion

Abbildung in einen Vektorraum mittels zufälliger Matrix. Sie kann mathematisch sinnvoll sein, besitzt ohne feste/versionierte Basis und Validierung aber keine automatisch fachliche Bedeutung.
