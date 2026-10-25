# S3 – Zwei abhängige Änderungen im isolierten Pilot

Status: Betreiber bestätigt den konkreten S3-Entwurf am 17.09.2026 mit „Bestätigt!“. S3a und die interne Journalbasis S3b sind implementiert und gezielt geprüft. S3c (vertrauenswürdige Controlleranbindung und abhängige Ausführung) bleibt offen. Ubuntu 24.04 bleibt Zielsystem. S1/S2 bleiben unverändert; keine Produkt-/Serveraktionen oder Modellaufrufe durch diesen Entwurf.

## Ziel und nachgewiesene Lücke

Die ersten drei Hermes-Bereiche sollen für den abgegrenzten ersten Betriebsumfang fertiggestellt werden: Grundplattform/Planung, Freigaben/Abschlussbelege und begrenzte Reparatur/Testketten. Keine pauschale Vollständigkeit aller fünf Produktadapter behaupten.

Quellenprüfung: `execution_policy.require_staging_pilot` sperrt Änderungsschritte mit Vorgängern. `PlanBook.execution_permission` sperrt Änderungsausführung nach dem ersten Quellenübergang. `change_chain.confirm` erlaubt nur einen Übergang pro Kandidat. `change_chain.valid` prüft einen aktuellen Nachher-Stand, keine historische Übergangskette. Bestehende Tests/Reviews binden sich an konkrete Quellen- und Vorgängerbelege. Diese Regeln dürfen nicht durch bloßes Entfernen von Bedingungen umgangen werden.

## Alternativen

| Ansatz | Vorteil | Grenze |
|---|---|---|
| **S3: zwei einzeln freigegebene abhängige Änderungen derselben Revision** | Prüft die fehlende Fortschrittssemantik am realen Problem. Empfehlung. | Neue historische Übergangsprüfung und Rücknahmesperren nötig. |
| Nach jeder Änderung neuen Plan erstellen | Bestehende Einzelschrittgrenzen bleiben bestehen. | Kein Abschluss der verlangten abhängigen Änderungsausführung; erneute Planung/Annahme nötig. |
| Beliebige Änderungsketten und Produktadapter gleichzeitig | Breiter Funktionsumfang. | Zu viele neue Sicherheits- und Ausführungsgrenzen in einer Abnahme; zurückstellen. |

## Begrenzter Umfang

- Ein aktiver, ausdrücklich erlaubter unabhängiger Pilot; ein aktueller Kandidat und unveränderte ausdrückliche Auswahl.
- Genau zwei Änderungsschritte A → B; keine Verzweigungen, Gruppen, Datenbankmigrationen, Deployment oder frei formulierten Kommandos.
- Zunächst disjunkte explizite Schreibumfänge; Überschneidungen blockieren. Fachliche Abhängigkeit bleibt möglich. Erweiterung auf überlappende Dateien benötigt einen eigenen Entwurf.
- Alle weiteren Voraussetzungen benötigen passende aktuelle Belege. Kein automatisches Forttragen alter Review-/Testbelege auf einen neuen Stand.
- Bestehender Modellversand für Änderungsvorschläge bleibt getrennt und ausdrücklich autorisiert; dieser Entwurf erlaubt keine Live-Modellbewertung. Medium bleibt Standard.

## Quellenstände und Belege

1. Vorschau bindet Kandidat, Auswahl, Schrittdefinitionen, Vorgänger, Wurzelidentität, konkrete Dateibytes und Adapter. B wird nur bedingt angezeigt.
2. A durchläuft die bestehenden separaten Vorschlags-, Test-/Review-, Übernahme-, Verifikations- und Abschlussentscheidungen.
3. Der ausdrücklich bestätigte Übergang H0 → H1 erhält eine unveränderliche Identität. A wird zum historischen kausalen Vorgänger; dies ist keine Behauptung, sein alter Test sei ein Test aller Dateien auf H1.
4. Vor B wird H1 frisch beobachtet und separat bestätigt. Der Vorschlag B bindet H1, A-Übergang und A-Abschlussbeleg. Kein automatisches Umschreiben der ursprünglichen Auswahl oder Vorschlagsrevision.
5. B benötigt eigene aktuelle Tests/Review und eine eigene Übernahmeentscheidung. Erst sein technischer Abschluss und die ausdrückliche Bestätigung ergeben H1 → H2.
6. Das neue Journal bindet jeden Übergang an den direkten Vorgänger, Ausgangs-/Zielstand und versiegelte Transaktionsnachweise. Historische Kontinuität und aktuelle Dateievidenz sind getrennte Prüfergebnisse. Der Kopf muss zum frisch beobachteten Gesamtumfang passen; Zwischenstände müssen aus den gespeicherten Nachweisen konsistent rekonstruierbar sein. Keine rückwirkende Fiktion erfolgreicher Tests.

## Rücknahme, Abbruch und Neustart

Nur das jüngste übernommene Glied darf zunächst zurückgenommen werden: B vor A. Kein automatisches kaskadierendes Rollback. Rücknahmen werden angehängt, nicht aus der Historie gelöscht. Nach Rücknahme bleiben betroffene Nachfolger ungültig; keine automatische Reaktivierung alter Freigaben, auch bei identischen Bytes. Erneute Änderungsausführung verlangt einen neuen ausdrücklich angenommenen Plan. Wiederanlauf startet keine Änderung erneut; unvollständige Transaktionen verlangen Klärung. Der gemeinsame Ausführungsplatz bleibt verbindlich.

## Umsetzung und Abnahme

- **S3a:** schreibfreie Vorschau/Diagnostik; vorhandene Ausführungssperren bleiben bestehen. Klare Sperrgründe für fehlende Belege, Überlappung, Drift und unzulässige Pilotwurzeln. Keine Modelle oder Zielschreibvorgänge.
- **S3b:** separates unveränderliches Übergangs-/Rücknahmejournal, Konsistenzprüfung historischer Kanten gegen aktuelle Spitze. Bestehende Einzelschrittbelege nicht still umdeuten. Transaktionen, Konkurrenz, manipulierte/vertauschte Vorgänger, Neustart und alte Datenbestände prüfen.
- **S3c:** einzeln gebundene Vorschlags-/Test-/Übernahme-/Abschlusswege für B anbinden; UI zeigt Ausgangsstand, Vorgänger, eigene Freigabe und Rücknahmegrenzen. Keine automatische Änderungskette.
- Echte temporäre Pilotdateien: A → H1 → B → H2; anschließende getrennte Rücknahme B und A. Originaldateien nur in ausdrücklich freigegebenen Übernahme-/Rücknahmeaktionen verändern.
- Negative Nachweise: geänderte Auswahl/Adapter/Wurzel, fremde Dateiänderung, ersetzte Vorgänger, nicht erfolgreiche Tests, Überlappung, veralteter Start, wiederholte Anfrage und Teilabbruch. Kein Folgeschritt bei unklarer Evidenz.
- Bestehende S1/S2-, Einzelübernahme-, Testbeleg- und HTTP-Schutzregression sowie Browserprüfung. Erst dann gemeinsame Abnahme der ersten drei Bereiche für diesen Betriebsumfang; keine universelle Produktabnahme.

## Bestätigte weitere Betriebsreihenfolge

Nach Abschluss der ersten drei Bereiche: erstes tatsächlich einzusetzendes Modul und dessen Adapterbedarf bestimmen; vorhandenen Ubuntu-24.04-Server aktuell prüfen; SMB-Dateisicherung und nötige konsistente Datenbanksicherung mit echtem Restore abnehmen; isolierte Übertragung/Dienstbetrieb/Neustart/Rücknahme testen; danach separate Produktfreigabe. Windows-Erstinstallation auf einem fremden Rechner, zusätzliche Module, RH-1, zweiter SMB-Speicher und nicht benötigte GPU-/CMS-Funktionen dürfen nachgeordnet bleiben. Funktionsabnahme auf dem vorhandenen Windows-Rechner ist nicht entbehrlich.

Selbstprüfung: kein neuer Produktzugriff, keine pauschale Prozent- oder Fertigstellungsbehauptung; historische und aktuelle Belege getrennt; Rücknahme linear begrenzt; Überschneidung explizit blockiert. Die konkrete Designbestätigung liegt vor. Nachweise: ../../verification/S3a_2026-09-17_verification.md und ../../verification/S3b_2026-09-17_verification.md. S3b prüft archivierte interne Belege und Rücknahmeeinträge; die Durchsetzung vor tatsächlichen Schreibvorgängen sowie aktuelle Freigabe-/Belegprüfung gehören zu S3c.
