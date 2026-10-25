# REST-Erstprofil: Betriebs- und Delegationsvertrag

Stand 19.09.2026, **Vorschlag zur technischen Ausgestaltung, nicht implementiert**. Ergänzt [Profildetails](AURELIA_REST_PROFIL_DETAILS_2026-09-19.md) und [Testmatrix](AURELIA_REST_TESTMATRIX_2026-09-19.md). Keine neue Produktfreigabe. Alle unten genannten Tests sind weiterhin nicht ausgeführt.

## Herkunft und Umfang

Bestehende Aurelia-Vorgaben: interne TLS-1.3-/mTLS-Verbindungen, getrennte Mandantenrollen, befristete ausdrückliche Freigaben und Systemidentitäten ohne interaktive Anmeldung. Quellen: Architektur/Sicherheit/Identität, gebunden in Vertragsvorschlag und Profildetails.

Neu vorgeschlagen sind die nachfolgenden Betriebsabläufe, Delegationsfelder, Fehlerzuordnung und Zustandsübergänge. Der enge Erstumfang umfasst direkte Aurelia-zu-Modul-Verbindungen und synchrone synthetische CPU-Analyse. Der Governor dokumentiert Entscheidungen und Nachweise; er ist weder Zertifikatsaussteller noch Laufzeit-Berechtigungsdienst. Sein lokaler Betrieb ist für diese Dokumentarbeit nicht erforderlich.

## 1. Zertifikatsbetrieb

| Thema | Konkreter Vorschlag | Testbezug |
|---|---|---|
| Vertrauensgrenze | Eigene Test-Vertrauensdomäne, getrennt von Produktion. Explizite Zuordnung von Dienstidentität, Umgebung, erlaubtem Ziel und Operation; keine pauschale Zulassung aller Zertifikate einer CA. | A06 |
| Verantwortung | Plattformadministration verantwortet Ausgabe, Sperre und Wiederherstellung. Dienste lesen nur ihren eigenen privaten Schlüssel; keine allgemeinen Adminschlüssel in Modulprozessen. | A06/A07 |
| Ausgabe | Zuerst Identitätszuordnung administrativ bestätigen, dann Zertifikat ausstellen und dessen öffentliche Kennung an die Zulassung binden. Keine automatische Ausgabe allein aufgrund eines Manifests. | A05/A06 |
| Rotation | Neue erlaubte Identität bereitstellen und prüfen; begrenztes Überlappungsfenster explizit konfigurieren. Danach alte Identität sperren, vorhandene Verbindungen schließen und alte lokale Schlüssel kontrolliert entfernen. | A07 |
| Sperre | Neben TLS-Prüfung bei jeder neuen Operation lokale aktuelle Zulassung/Sperrliste prüfen. Neue Anfragen gesperrter Identitäten ablehnen, auch auf bestehenden Verbindungen. Laufende Operationen in den belegten Abbruchpfad überführen. | A07/B05 |
| Veraltete Sperrdaten | Ablaufgrenze der lokal bestätigten Richtlinienrevision verbindlich konfigurieren. Nach Ablauf oder bei unlesbarer Richtlinie keine neue Ausführung. Kein Rückfall auf ungesicherten Transport. | A07 |
| Wiederherstellung | Vertrauensanker, öffentliche Identitätszuordnung und benötigtes Schlüsselmaterial mit getrennten Rechten sichern. Wiederhergestellte alte Zertifikate dürfen aktuelle Sperren nicht aufheben. | A07/B09 |

Noch vor einer Umsetzung festzulegen: vorhandene oder neue CA-Lösung, Zertifikatslaufzeit, Überlappungsfenster, maximale Richtlinienalterung und konkrete Schlüsselablage. Hier werden keine CA installiert, Schlüssel erzeugt oder bestehenden Backup-Schlüssel zweckentfremdet. Kurzlebige Zertifikate ersetzen keinen Sperrtest.

## 2. Delegation einer einzelnen Analyse

Vorgeschlagen ist ein separates versioniertes JSON-Kontextobjekt neben dem unveränderten fachlichen Analyse-Payload. Die genaue HTTP-Repräsentation wird im Adaptervertrag festgelegt; nicht stillschweigend als zusätzliches Feld in ein vorhandenes Modul-Inputschema einfügen. Es ist kein eigenständig nutzbares Bearer-Token: Vertrauen entsteht ausschließlich am erlaubten direkten mTLS-Aufrufpfad. Bei einem Zwischenproxy muss die Vertrauensgrenze neu spezifiziert werden.

| Feld | Bedeutung und Prüfung |
|---|---|
| context_version | Exakt zugelassene Kontextrevision; unbekannte Revision sperren. |
| request_id | Vom kontrollierten Aurelia-Dienst erzeugte eindeutige Korrelations-ID; keine Idempotenzzusage. |
| tenant_id, actor_id | Aus geprüfter Sitzung bzw. explizit erlaubter Systemidentität; keine Übernahme frei gesetzter Browserwerte. |
| audience, operation | Exakt zugelassenes Modul und Operation; kein freies Ziel, kein Wildcard-Scope. |
| issued_at, expires_at | UTC-Zeit; vorgeschlagen maximal 30 Sekunden Gültigkeit. Ungültig bei now < issued_at oder now >= expires_at; keine verdeckte Toleranz. |
| authorization_revision | Bezieht sich auf die vom vertrauenswürdigen Autorisierungsdienst aktuell geprüfte Berechtigung. Eine vom Client behauptete Revision ist kein Beleg. |
| profile_revision, release_id | Bindung an den freigegebenen Vertrags-/Artefaktbeleg. Drift sperrt. |

Empfangsreihenfolge: Transportidentität → begrenztes Parsing → Kontext/Version/Ziel → aktuelle Berechtigung → fachliches Schema → Slotreservierung → erneute Berechtigungs-/Ablaufprüfung direkt vor Ausführung. Doppelte JSON-Feldnamen und widersprüchliche Kontext-/Payloadwerte abweisen. Ein fehlender Mandant wird niemals durch einen globalen Default ersetzt.

Für den späteren Testpfad wird eine synchrone aktuelle Berechtigungsprüfung beim kontrollierten Aurelia-Autorisierungsdienst vorgeschlagen. Ist sie nicht verfügbar, beginnt keine Analyse. Das Modul erhält keine allgemeine Vollmacht aus einem gültigen Transportzertifikat. Ein Rechteentzug unmittelbar nach der Prüfung bleibt ein definierter Konkurrenzfall: vor Ergebnisfreigabe erneut autorisieren; bei erkanntem Entzug keine Ausgabe, Abbruch anfordern. Ein späteres Verfahren für sofortige Unterbrechung benötigt einen eigenen Nachweis; es wird hier nicht behauptet.

Kein Browser-Sessiontoken, Passwort, vollständiges Rollenprofil oder private Zertifikatsmaterial wird an das Modul weitergereicht. Der Delegationskontext gehört nicht ins normale Log. Zu prüfen: A08–A12; Ablaufgrenzen mit kontrollierter Testuhr und einer getrennten Echttransportprobe.

## 3. Abbruch, Auftragseigentum und Wiederanlauf

| Zustand | Eintritt / zulässiger Übergang | Invariante |
|---|---|---|
| geprüft | Alle Annahmeprüfungen bestanden; Slot noch nicht vergeben | Keine fachliche Ausführung. |
| reserviert | Exklusiver Slot und minimaler Auftragsbeleg dauerhaft geschrieben | Beleg vor Ausführungsstart; parallele Reservierung abweisen. |
| läuft | Eigener Ausführungskontext eindeutig zugeordnet | Slot belegt; keine Warteschlange, kein automatischer Retry. |
| Abbruch angefordert | Clientabbruch, Zeitgrenze, Sperre oder erkannter Rechteentzug | Aufforderung ist kein Nachweis erfolgter Beendigung. |
| erfolgreich / fehlgeschlagen / abgebrochen | Ergebnis validiert bzw. Ende/Beendigung tatsächlich nachgewiesen | Terminalen Beleg dauerhaft schreiben, dann Slot freigeben. Ergebnisfreigabe benötigt aktuelle Berechtigung. |
| ungeklärt | Prozessverlust, widersprüchlicher Zustand oder fehlender Abschlussbeleg | Slot gesperrt; kein Replay und kein angenommener Erfolg. |

Der minimale Beleg enthält Request-ID, Mandanten-/Akteurbezug unter Zugriffsschutz, Vertrags-/Releasebindung, Instanzkennung, Status und Zeitpunkte; keine fachlichen Nutzdaten oder Zugangsschlüssel. Aufbewahrung, Löschung und Speichergrenzen sind vor Betrieb festzulegen. Bei vollem/unbeschreibbarem Journal keine neue Arbeit annehmen.

Beim Wiederanlauf neue Instanzkennung verwenden, offene Belege als ungeklärt kennzeichnen und Eigentum/Existenz alter Ausführungskontexte prüfen. Eine PID allein genügt nicht zur Identifikation. Erst belegtes Ende erlaubt die technische Slotfreigabe; der verlorene fachliche Ausgang kann trotzdem unbekannt bleiben. Ein erneuter Auftrag ist eine ausdrückliche neue Aktion mit neuer Request-ID, kein Wiederbeleben des alten Belegs.

CPU-/RAM-Grenzen, Prozessisolation, maximale Abbruchfrist und sichere Beendigung sind modulabhängig. Ohne diese Festlegung bleibt B07 blockiert; keine erfundenen produktiven Kapazitäten. Der 15-Sekunden-Clienttimeout ist keine Behauptung, dass ein Modulprozess innerhalb dieser Frist endet.

## 4. Fehlervertrag am Aurelia-Adapter

Vorgeschlagene Klassifikation; bestehende Modulfehler werden explizit übersetzt, nicht ungeprüft weitergereicht. HTTP-Codes gelten nur, wenn eine HTTP-Antwort überhaupt möglich ist. TLS-/Verbindungsfehler dürfen keine erfundene Modulantwort erzeugen.

| Fehler | HTTP-Vorschlag | Interne Kategorie / Wirkung |
|---|---|---|
| Ungültiger Kontext oder JSON-/Inputvertrag | 400 | invalid_request; keine Ausführung |
| Fehlende Plattformanmeldung | 401 | unauthenticated; keine Ausführung |
| Verweigerte Berechtigung / unzulässige Delegation | 403 | forbidden; keine fremden Objektinformationen |
| Vertrags-/Releaseabweichung | 409 | contract_conflict; erneute Prüfung erforderlich |
| Request zu groß / unzulässige Kompression | 413 / 415 | payload_limit / unsupported_encoding; keine Ausführung |
| Instanz ausgelastet oder sicher gesperrt | 503 | busy / recovery_required; keine automatische Wiederholung |
| Autorisierung/Richtlinie nicht verlässlich verfügbar | 503 | authorization_unavailable; keine neue Ausführung |
| Ungültige oder übergroße Modulantwort | 502 | invalid_upstream_response; keine Ergebnisübernahme |
| Frist abgelaufen | 504 am Adapter, sofern Antwort möglich | deadline_exceeded; Ausgang möglicherweise unbestätigt |

Fehlerkörper nur mit stabiler Kategorie und sicherer Korrelations-ID, ohne Stacktrace, fremde Objektkennungen oder Rohantworten. Die genaue Kompatibilität mit dem bestehenden Fehlerobjekt ist vor kanonischer Übernahme zu prüfen. Timeout kann mit bereits erfolgter Arbeit zusammenfallen; kein automatisches erneutes Senden.

## Abschlussstand und nächste Entscheidung

Das Betriebsverhalten ist damit als überprüfbarer Vorschlag beschrieben. Es bestehen keine Laufzeitnachweise. Vor einer Umsetzung ist ein begrenztes erstes Testpaket zu entscheiden: synthetischer CPU-Testdienst, direkter mTLS-Pfad, A/B-Matrix und konkrete CA-/Adapter-/Prozesslösungen. Dies erfordert noch keine Wahl eines echten Produktmoduls. C-Erweiterungen, Produktionsdaten, Hardware und Produktdeployment bleiben außerhalb dieses Pakets.

Die nächste sinnvolle Arbeit ist eine kompakte Paketabgrenzung mit den verbleibenden Technikentscheidungen und vorhandenen Wiederverwendungsmöglichkeiten. Keine weitere allgemeine Konzeptausweitung und keine automatische Änderung der fünf Produktrepositories.
