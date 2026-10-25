# Aurelia REST-Profil – Vertrags-Testmatrix

Stand: 19.09.2026. Profilentwurf: `aurelia-rest/1.0-draft.1`.

Fortschreibung 20.09.: Die folgende Statusangabe beschreibt den historischen Entwurfsstand. Aktuelle lokale **Teilnachweise**, verbleibende Varianten und Grenzen stehen in [REST-Abdeckung](verification/REST_ABDECKUNG_2026-09-20.md); keine Fallfamilie dadurch pauschal abgenommen.

**Status aller Fälle: NICHT AUSGEFÜHRT.** Diese Matrix spezifiziert spätere Prüfungen; sie ist kein Testergebnis, keine Implementierungsfreigabe und keine S4-/Registry-/Produktionsabnahme. Die Vertragsrichtung ist angenommen, technische Details einschließlich Zahlen bleiben Vorschläge. Kein Erstmodul gewählt.

## Voraussetzungen und Nachweisregeln

- Ausschließlich isolierte synthetische Daten: zwei Mandanten A/B mit getrennten Akteuren, Objekten, Drafts und Caches; eigenes Test-Vertrauensmaterial. Keine Produktzertifikate, echten Klientendaten oder Hardwareansteuerung.
- Testadapter und Testdienst müssen separat freigegeben und implementiert sein. Fehlende Funktionen oder ungeklärte Vertragsdetails ergeben `BLOCKIERT`, niemals einen Erfolg. Mocks belegen nur ihre geprüfte Schicht; Ubuntu-/mTLS-Nachweise benötigen den tatsächlichen isolierten Transportpfad.
- Jede Tabellenzeile ist eine Fallfamilie. Jede genannte Variante erhält einen eigenen Ergebnisdatensatz; Erfolg einer Variante genügt nicht für die Familie.
- Jeder Lauf bindet Run-ID, Fall/Variante, UTC-Zeit, Testcode-/Fixturehash, vollständige Vertragsrevision, Manifest-/Schema-/Releasebezug, effektive nichtgeheime Konfiguration, Plattform-/Laufzeitversion, Soll/Ist, Ergebnis und begrenzte Belegpfade. Sensible Identitäten nur als synthetische Aliase; keine Schlüssel oder Berechtigungsnachweise im Bericht.
- Negative Fälle brauchen neben dem Fehler eine unabhängige Beobachtung: Aufrufzähler, Objektzustand oder Ausführungsjournal vor/nach der Aktion. Eine Fehlermeldung allein beweist weder Mandantentrennung noch fehlende Nebenwirkungen. Beobachterausfall ergibt unvollständige Evidenz.
- Laufstatus: `BESTANDEN`, `FEHLGESCHLAGEN`, `BLOCKIERT`, `NICHT AUSGEFÜHRT`. Übersprungene oder nicht anwendbare Fälle dürfen keine Vollabnahme erzeugen; begründete Nichtanwendbarkeit gehört in die explizite Scopeentscheidung.

## A – Zulassung, Transport und Berechtigung

| ID | Aufbau / Aktion | Eindeutiges Erfolgskriterium | Benötigter Nachweis / Voraussetzung |
|---|---|---|---|
| A01 | Gültiges synthetisches REST-Manifest, zugelassenes Ziel, Mandant A; eine Analyse | Genau ein Aufruf; Request/Response schema-konform; Passport zu Input/Kernel passend, ausdrücklich unsigned; kein Promote/Hardwareaufruf | Adapter-, Dienstzähler, Schema-/Passportprüfung und Zustandsvergleich; erwartetes Fixture-Ergebnis unabhängig festlegen |
| A02 | Unbekannte Profil-/ABI-/Passportversion, fehlendes Schema, falscher Typ oder unzulässige Operation einzeln einsetzen | Zulassung vor Modulausführung gesperrt; keine automatische Versionsanpassung | Validatorergebnis plus null Analyseaufrufe |
| A03 | REST-entry auf ausführbaren Sentinel setzen; Python/WASM getrennt prüfen | REST führt entry nie aus; vorhandene freigegebene Python-/WASM-Aufrufwege bleiben getrennt funktionsfähig | Sentinelzähler null; eigene Regressionstests je tatsächlich unterstütztem Profil; fehlende Fixtures bleiben offen |
| A04 | Manifest mit fremdem Ziel, Redirectantwort oder externem Schema-Verweis | Kein nichtzugelassener Netzwerkzugriff, kein Redirect-/Schema-Fetch | Isolierte Netzwerkbeobachtung plus Sentinelziel; auch geänderte Zielauflösung muss die Ziel-/Identitätsbindung wahren |
| A05 | Quell-, Schema-, Abhängigkeits-, Ziel- oder Konfigurationsdrift nach Zulassungsbeleg | Vor nächster Ausführung gesperrt; alter Beleg bleibt historisch, keine automatische Neuzulassung | Je Änderung eigener Lauf mit Vorher-/Nachherhash und Aufrufzähler |
| A06 | TLS 1.3 mit erlaubten Gegenstellen; separat fehlendes/falsches Zertifikat, fremde CA, Ablauf, falsche Serveridentität, nichtzugelassener Dienst derselben CA | Nur erlaubte Identität akzeptiert; übrige Varianten ohne Analyse; kein unsicherer Fallback | Echte TLS-Handshakes und serverseitiger Aufrufzähler; CA-/Identitätsvertrag erforderlich |
| A07 | Zertifikatsrotation und Sperre bei neuer sowie bestehender Verbindung | Rotierte erlaubte Identität nutzbar; gesperrte Identität kann keine weiteren Operationen starten | Festgelegtes Rotations-/Sperrverfahren; bereits laufende Operationen separat nach Abbruchvertrag behandeln |
| A08 | Gültige Dienstidentität, aber fehlende Sitzung, fremder Mandant, entzogene Rechte oder unzulässige Operation | Keine Datenfreigabe oder Objektänderung; mTLS allein verleiht keine Benutzerrechte | Autorisierungsentscheid und synthetische A/B-Zustandsvergleiche |
| A09 | Client fälscht Mandant/Akteur/Ziel in Body oder Header; Kontext fehlt/widerspricht sich; direkter Modulzugriff | Freie Clientwerte werden nicht zur Autorität; Widerspruch/Umgehung abgewiesen | Konkrete Delegationsrepräsentation erforderlich; kontrollierte direkte Negativversuche |
| A10 | Delegation unmittelbar vor, auf und nach Ablauf; überlange Gültigkeit; Rechteentzug vor Ausführung | Abgelaufene/überlange Delegation gesperrt; Berechtigung bei Ausführung aktuell; kein dauerhaftes Recht aus altem Kontext | Kontrollierte Testuhr, präzise festgelegte Ablaufsemantik und getrennte Echttransportprobe |
| A11 | Mandant A liest/ändert B-Objekt oder B-Draft; identische Cache-Schlüssel unter A/B | Keine B-Nutzdaten in Antwort, Cache oder Fehler; keine B-Zustandsänderung | Zwei synthetische Mandanten, Objekt-/Cachebeobachtung; alle angebotenen Operationen einzeln |
| A12 | Fehler und Erfolg mit markierten synthetischen Nutzdaten/Geheimnissen auslösen | Marker erscheinen nicht in Logs/Fehlerantworten; erlaubte begrenzte Auditmetadaten bleiben nutzbar | Erfasste App-, Adapter- und Proxylogs; unzugängliche Logschichten explizit offen |

## B – Grenzen, Abbruch und Wiederanlauf

Zahlen beziehen sich ausschließlich auf den vorgeschlagenen Erstprüfentwurf: 1 MiB Request, 4 MiB Response, 3 s Verbindungsaufbau, 15 s Gesamtfrist, eine aktive Analyse, keine Warteschlange/automatische Wiederholung. Vor Ausführung müssen Definitionen und Mess-Toleranzen im Testplan feststehen; keine nachträgliche Lockerung zugunsten eines Erfolgs.

| ID | Aufbau / Aktion | Eindeutiges Erfolgskriterium | Benötigter Nachweis / Voraussetzung |
|---|---|---|---|
| B01 | Schema-gültige UTF-8-Bodies bei Grenze minus 1, genau Grenze, plus 1 Byte; Streaming ohne Längenangabe; Kompression | Gültige Bodies bis Grenze zulässig, darüber abgewiesen; Streaming ebenfalls begrenzt; Kompression im Erstprofil abgewiesen | Exakte Bytezählung statt Zeichenzahl; begrenztes Lesen und null Analyse bei zu großem Request |
| B02 | Response analog an 4-MiB-Grenze, ohne Längenangabe oder mit irreführender Länge; ungültiges JSON/Schema | Überschreitung/Fehler nie als abgeschnittener Erfolg oder gültiger Draft übernommen | Begrenzt lesender Adapter, Speicherbeobachtung und keine Ergebnisübernahme |
| B03 | Verbindung/TLS verzögern; langsame Antwort einschließlich stetiger kleiner Datenpakete | Verbindungs- und Gesamtfrist greifen getrennt; Fortschritt setzt Gesamtfrist nicht zurück | Monotone Zeitmessung und kontrollierte Verzögerungen; festgelegte Toleranz vor Lauf |
| B04 | Zweite Anfrage während aktiver Analyse, auch von anderem Mandanten | Höchstens eine aktive Analyse pro Instanz; zweite explizit ausgelastet, keine versteckte Warteschlange | Dienstseitiger Parallelitätszähler und Ausführungsjournal |
| B05 | Client abbrechen oder Timeout während serverseitiger Ausführung | Ausgang als unbestätigt sichtbar; Slot bis belegtem Ende/Abbruch belegt; kein zweiter Start durch vorzeitige Freigabe | Unabhängige Dienst-/Slotbeobachtung; allein geschlossener Socket genügt nicht |
| B06 | Verbindungsabbruch vor/nach möglicher Annahme; wiederholte Request-ID | Adapter wiederholt nicht automatisch; keine Behauptung von Idempotenz allein wegen Request-ID | Aufrufzähler plus Transportjournal; Verhalten einer ausdrücklich neuen manuellen Anfrage getrennt dokumentieren |
| B07 | CPU-/RAM-Grenze und nicht kooperierenden Abbruch simulieren | Vereinbarte Prozesslimits/Beendigung durchgesetzt; keine konkurrierende Folgeausführung solange Ende unklar | BLOCKIERT bis modulbezogene harte Limits und Prozess-/Abbruchvertrag festgelegt sind |
| B08 | Testdienst/Adapter während eines Auftrags stoppen und neu starten | Kein automatisches Replay; ungeklärter Auftrag bleibt erkennbar; Slot erst nach sicherer Rekonstruktion freigegeben | Persistenz-/Wiederanlaufvertrag und isolierte Prozessbeobachtung; kein Neustart des Produktservers |
| B09 | Freigegebenes Testartefakt starten, prüfen, isoliert zurücknehmen | Identität entspricht Beleg; Rücknahme entfernt nur eigene Testinstanz; fremde Dienste/Daten unverändert | Isolierter Ubuntu-Testpfad, Vorher-/Nachherinventar und gezielte Readinessprüfung; kein Live-Restore |

## C – Separate Erweiterungsabnahmen

Diese Fälle sind vorgeschriebene spätere Prüfungen der jeweiligen Erweiterung. Sie sind keine Voraussetzungen, um bereits A/B spezifizieren zu dürfen, und dürfen nicht als erfolgreiches Merkmal des engen synchronen Erstprofils dargestellt werden.

| ID | Aufbau / Aktion | Eindeutiges Erfolgskriterium | Noch benötigte Grundlage |
|---|---|---|---|
| C01 | Draft/Review/Ready/Promote; verbotene Übergänge, CopyGuard-Block, fehlendes/abgelaufenes Step-up | Nur ausdrücklich erlaubter Übergang; Block verändert keinen geschützten Zustand; Analyse startet keine Hardware | Bestätigter D18-Zustands-/Berechtigungsvertrag; rein synthetische Wirkungssenke |
| C02 | Mutierenden Befehl doppelt senden; Antwortverlust nach Commit | Definierte Idempotenz einschließlich Mandant/Operation/Inhalt oder eindeutige Sperre; kein doppelter Effekt | Separater Idempotenz-/Transaktionsvertrag; bis dahin keine automatischen Wiederholungen |
| C03 | WS-Verbindung, fremder Mandant, Rechteentzug, Reconnect, neue Bootkennung, Replay-Gap | Kein fremdes Ereignis; Rechteentzug berücksichtigt; Lücke explizit und autorisierter Neuabruf statt erfundener Vollständigkeit | WS-Auth-/Replay-/Größen-/Verbindungsgrenzen festlegen |
| C04 | Hintergrundjob nach Rechteentzug, Ablauf, Neustart oder Mandantenwechsel | Neuautorisierung vor Ausführung/Abruf; kein Replay oder Zugriff aus altem Kontext | Jobpersistenz-, Scheduling- und Autorisierungsvertrag |

## Auswertungs- und Freigabereihenfolge

1. Offene Protokolldetails entscheiden: CA/Rotation/Sperre, Delegationsformat/Ablaufsemantik, konkrete Fehlercodes, hartes Ressourcen-/Abbruchverhalten und Wiederanlauf. Größen-/Zeitgrenzen zunächst bestätigen oder begründet revidieren; Quellenbindung dabei erneuern.
2. Nach Implementierungsfreigabe Validator-/Adaptertests mit synthetischen Fixtures; anschließend tatsächliche Transport- und Isolationsprüfungen auf dem freigegebenen Ubuntu-Testpfad. Tests nicht allein aus erfolgreichen Mockantworten ableiten.
3. Bericht pro Fall/Variante auswerten. Fehlende/negative Evidenz sperrt die betroffene Eigenschaft. A/B-Erfolg erlaubt nur eine Bewertung dieses engen Profils; C bleibt separat sichtbar.
4. S4-Bewertung, Registryaufnahme, Erstmodulwahl sowie Infrastruktur-/Recovery-/Produktionsfreigaben sind weiterhin eigenständige Entscheidungen. Kein Prozentwert oder grüner Test ersetzt diese Entscheidungen.

## Quellenbindung dieser Fassung

| Quelle | SHA256 der zugrunde gelegten Datei |
|---|---|
| [Vertragsvorschlag](AURELIA_REST_VERTRAGSVORSCHLAG_2026-09-19.md) | `1b8b3168ee5935118b7bbb3fb5b47138f2e5a3a7fafc3341da4cea42039346db` |
| [Technischer Zusatz](AURELIA_REST_PROFIL_DETAILS_2026-09-19.md) | `9293b27197893d0da29199d06415bfbfafd8ce12ca83bd9c6742e88c3b103fd9` |

Die dort gebundenen externen Architektur-/ABI-Quellen sind Herkunft des Entwurfs, kein Nachweis aktueller Laufzeitimplementierung. Bei relevanter Quellenänderung Matrix erneut abgleichen; historische Belege nicht umdeuten.
