# Aurelia REST-Profil: technischer Zusatz

Stand 19.09.2026. Die Richtung „separates versioniertes REST-Profil neben Python/WASM“ ist angenommen. Folgende Ausgestaltung ist ein prüfbarer Planungsvorschlag, keine laufende Konfiguration oder Implementierungsfreigabe. Keine Auswahl des ersten Moduls.

## Dienstidentität und Mandantenberechtigung

Aurelias Architektur und Sicherheitsvorgaben verlangen intern mTLS und TLS 1.3. Dieses Profil übernimmt diese Vorgabe, statt eine zweite konkurrierende Transportauthentifizierung einzuführen.

| Grenze | Vorgeschlagener Vertrag | Erforderlicher späterer Nachweis |
|---|---|---|
| Aurelia → Modul | TLS 1.3 mit beidseitiger Zertifikatsprüfung, eigener Dienstidentität pro Dienst/Umgebung und expliziter Zuordnung erlaubter Aufrufer. Keine bloße Prüfung „von derselben CA ausgestellt“. | Falsche Identität, unbekannte CA, abgelaufene Zertifikate und falsches Serverziel werden abgewiesen. |
| Zertifikatsbetrieb | Keine Schlüssel im Manifest/Repository. Vor Start verantwortliche Ausgabestelle, geschützte Ablage, Rotation und Sperrverfahren festlegen; gesperrte Identität auch bei bestehenden Verbindungen ausschließen. | Rotation ohne ungesicherten Fallback; Sperre und Wiederanlauf testen. CA-Technik noch nicht ausgewählt. |
| Benutzer → Aurelia | Bestehende Plattformidentität liefert Mandant, Rechte und gegebenenfalls Step-up. mTLS authentifiziert einen Dienst, nicht automatisch den Benutzer oder dessen Berechtigung. | Unangemeldete, fremde und entzogene Berechtigung abweisen. |
| Delegation → Modul | Kontrollierter Aurelia-Dienst erzeugt den minimalen Aufrufkontext: Mandant, Akteur, erlaubte Operation, Zielmodul, Request-ID und kurze Gültigkeit. Clientseitige Kontextfelder werden nicht durchgereicht. Modul akzeptiert den Kontext ausschließlich vom dafür zugelassenen mTLS-Aufrufer. | Body-/Header-Widerspruch und falsches Ziel abweisen; direkte Umgehung des delegierenden Dienstes sperren. |
| Hintergrundjob/WS | Kontext serverseitig an Job/Objekt und Mandant binden; bei Ausführung, Wiederverbindung und Abruf erneut autorisieren. Abgelaufene Delegation nicht als dauerhafte Berechtigung speichern. | Mandantenwechsel, Rechteentzug, Neustart und Replay-Gap testen. |

Der erste Vertragsentwurf setzt eine direkte authentifizierte Verbindung zum Modul voraus. Bei TLS-Terminierung in einem Zwischenproxy muss dessen Vertrauens- und Delegationsgrenze eigens spezifiziert werden; weitergereichte freie Header allein genügen nicht. Kein neuer Tokenstandard und keine neue Auth-Bibliothek werden hier festgelegt.

## Vertragsrevision und Releasebindung

Vorgeschlagene Kennung: `aurelia-rest/1.0-draft.1`. Sie ist getrennt von bestehendem `abi_version=v1`, Modulversion und Passportversion. Erst eine geprüfte Freigabe könnte daraus `aurelia-rest/1.0` machen. Unbekannte oder nicht ausdrücklich zugelassene Kombinationen bleiben gesperrt; kein automatisches Upgrade/Downgrade.

Der spätere Zulassungsbeleg bindet mindestens Profilrevision, Kernel-ID/-Version, Manifest-/Schemahashes, Operationsmenge, internen Ziel-/Dienstidentitätsbezug, Artefakt-/Abhängigkeitsbeleg, nichtgeheime Konfigurationsrevision und effektive Limits an dieselbe geprüfte Freigabe. Geheimnisse selbst gehören nicht hinein. Änderungen benötigen eine neue Prüfung; ein Quellcodehash allein belegt kein vollständiges Deployment.

## Begrenztes synthetisches Erstprüfprofil

Diese Zahlen sind **vorgeschlagene Testgrenzen, nicht gemessene Kapazitäten oder produktive Zusagen**. Sie gelten nur für einen isolierten synchronen CPU-Analysepfad. Hardware, Promote, allgemeine Jobs und WebSocket-Ausführung werden dadurch nicht freigegeben.

| Parameter | Startvorschlag | Verhalten an der Grenze |
|---|---|---|
| JSON-Request | 1 MiB UTF-8; keine komprimierten Bodies im Erstprofil | Vor Verarbeitung begrenzt lesen, größere Bodies abweisen. |
| JSON-Antwort | 4 MiB | Begrenzt lesen; Überschreitung als Fehler, niemals als abgeschnittenen Erfolg behandeln. |
| Verbindungsaufbau einschließlich TLS | 3 Sekunden | Abbruch ohne Transportfallback. |
| Gesamte Anfrage | 15 Sekunden ab Annahme, einschließlich Verbindung/Lesen | Timeout meldet unbestätigten Ausgang; bedeutet nicht, dass der Server aufgehört hat. |
| Aktive Analyse | Eine pro Modulinstanz, keine Warteschlange im Erstprofil | Weitere Anfragen explizit als ausgelastet abweisen. |
| Automatische Wiederholung | Null, auch bei Verbindungsabbruch | Kein verdeckter Doppelauftrag. Request-ID allein ist keine Idempotenzgarantie. |
| Delegationsgültigkeit | Höchstens 30 Sekunden; bei Annahme und vor Ausführung prüfen | Abgelaufener Kontext wird abgewiesen; Uhrabweichung als Betriebsfehler behandeln. |

Ein abgebrochener Client gibt den serverseitigen Ausführungsslot nicht automatisch frei. Der Slot bleibt bis zum belegten Ende/Abbruch belegt. CPU-/RAM-Prozesslimits und Abbruchfähigkeit müssen nach Modulwahl anhand synthetischer Messungen konkretisiert und durchgesetzt werden. `cpu_ms_est` ist eine Schätzung, keine harte Laufzeitgrenze. Ohne diesen Nachweis kein produktiver Betriebsstart.

Keine Nutzdaten, Zertifikatschlüssel oder delegierten Berechtigungen in Logs. Protokolliert werden nur begrenzte Request-ID, Operation, Vertrags-/Artefaktbezug, Ergebniscode, Dauer und notwendige Auditmetadaten gemäß Aufbewahrungsregel.

## Nächste Schritte und verbleibende Entscheidungen

1. Aus diesem Entwurf eine quellengebundene Vertrags-Testmatrix vorbereiten: positiver Analysepfad sowie Identitäts-, Mandanten-, Versions-, Größen-, Timeout-, Drift- und Abbruchfälle. Zunächst nur Spezifikation mit synthetischen Daten.
2. Vor Umsetzung CA-/Rotationsbetrieb, konkrete Delegationsrepräsentation, modulbezogene Ressourcenlimits und kanonische Vertragsübernahme festlegen. D18/Promote und WS bleiben getrennte Teilabnahmen.
3. Erst nach passender Produktfreigabe in den zuständigen Repositories implementieren und auf einem isolierten Ubuntu-Testpfad nachweisen. Danach S4-/Registryentscheidung; Produktions- und Recoverygates separat.

Prüfstand: vorhandene Dokumentvorgaben abgeglichen; keine TLS-, Last-, Mandanten- oder Modullaufzeittests dieses Profils ausgeführt. Server und Produktrepositories unverändert.

## Zusätzliche Quellenbindung

- Aurelia/docs/02-architecture.md: SHA256 `021c98be598abc8f11a2ff4b5410794d11da03234501ea1bd40973ea814efe8d`.
- Aurelia/docs/03-security-dsgvo.md: SHA256 `7d31a620dbb662968b9d882a1985604a4f90b7b4768366502cee26b2c908a7a6`.
- Weitere ABI-, Identitäts-, D18- und Manifestquellen: [ursprünglicher Vertragsvorschlag](AURELIA_REST_VERTRAGSVORSCHLAG_2026-09-19.md).
