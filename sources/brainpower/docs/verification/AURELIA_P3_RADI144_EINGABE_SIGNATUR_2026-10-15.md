# P3 – Radi144: Eingaben und Signaturpfade

Stand 15.10.2026. Quellengebundene, rein lesende Aufnahme zur Wiederaufnahme nach der Pause. Keine Originalfunktion, Produktinitialisierung, Pydantic-Validierung, Rechenengine, HTTP-Anfrage oder echte Speicherung ausgeführt. Numerische Signaturparität ist damit nicht nachgewiesen. Astra/medium hat die neuen Quellbefunde unabhängig in SPEC→QUALITY geprüft und den Halt vor neuen numerischen Läufen empfohlen; Betreiberentscheidung zur Fortsetzung offen.

## Gesicherte Grundlage

Der Pausepunkt `Aurelia-P3-Pause-20261014-221235Z` wurde frisch nachgerechnet: 29 Manifestdateien stimmen; 61 ZIP-Einträge bestehen die CRC-Prüfung. Dies wiederholt keine Originalreferenzläufe. Die drei Quellen aus der letzten API-Probe haben weiterhin dieselben SHA-256. Radi144-HEAD: `b8ac33a1360f1cb56f06e602fcd37cbda2a9c641`; vorgemerktes `A AGENTS.md` bleibt erhalten, keine Aussage über ein insgesamt sauberes Repository.

Neuer lokaler Vorherpunkt: `checkpoints/Aurelia-P3-Radi144-Input-20261015-061349Z`. Zehn benannte Quelldateien sind vollständig als Bytes gesichert und gehasht; 22 ausgewählte Originalfunktionen statisch geparst und mit Zeilenbereichen/AST-Digests gebunden. Darunter die installierte Pydantic-Implementierung von `model_dump`, jedoch keine vollständige Paket- oder native Serializerprüfung. Keine Klienten-, Katalog-, Medien-, Schlüssel- oder Laufzeitdatensätze gelesen.

## Aktive Wege

Zeilen beziehen sich auf die unveränderten Quellen in `C:/Users/Hubert111/Documents/Radi144`; vollständige Hashliste in `SOURCE-BEFORE.json` des Prüfpunkts.

| Eingabe | Tatsächlicher Quellpfad | Noch erforderlicher Nachweis |
|---|---|---|
| Direkte Personendaten | `user_workflow.js:509–537,575–581` → `ClientBase` → API `_build_client_data:279–305` mit `model_dump()` → Engine `calculate_resonance:325–334` → `generate_signature` | Native Datum-/Zeittypen, Feldpräsenz und Originalformeln getrennt prüfen; bisheriger API-Double ersetzt diesen Übergang. |
| Gespeicherte Klienten-ID | API `_resolve_client_data_by_id:75–80` → Registry-Service `get_by_id:48–56` → Projektion `_client_data_from_registry_entry:65–72` | Gefunden/404 und tatsächlich geladener Feldumfang. Im geprüften JS kein `client_id`/`X-Client-ID` verwendet; damit API-Pfad, kein belegter Browserablauf. |
| Gruppe | JS `581–586` → API `_prepare_precomputed_signature:326–329` → `generate_group_signature:131–159` | Einzelmitglieder, Mittelwert, leere Gruppe, Änderung des Mitgliederdictionaries bei `place` → `birth_place`; echte Formeln getrennt. |
| Geo | JS `587–600` → API `351–367` → `calculate_geo_frequency:250–266` | Parsing, Radius, Zahlenvalidierung und Reihenfolge des Frequenzmischens; positive Radien benötigen echtes NumPy `log10`. |
| Bild | JS `601–613` → API `231–252,330–343,387–390` → `generate_image_signature:161–248` | API bevorzugt Base64 bei gemischtem Payload, JS den eingetragenen Pfad. Datei-/Temporärdatei-/Cleanup- und Pillow-Grenzen müssen separat geprüft werden. |
| Datenbank | JS `615–618` → API `369–381` → `vectorise_database_selection:268–302` | Tatsächlich vorhandene synthetische Datei, Encoding, Teilzeichenfolgensuche und Nichttreffer. Original sucht case-insensitiv nach dem Fokus als Teilzeichenfolge; keine semantische Suche. Ranking/Scan sind eigene Wege. |
| Zusammensetzung | API `308–390`: Gruppe vor Bild vor Standardsignatur; danach Geo, danach DB | Rohfelder und wirksamer Zweig unterscheiden. Die aufeinanderfolgenden Mittelungen sind keine gleichgewichtete Zusammenfassung aller Quellen. |

`db_path` allein erfüllt nicht das Eingabegate der Analyse (`resonance.py:423–434`). Ein gesetztes `use_planetary` kann eine vorbereitete Signatur anfordern, macht den Gruppen-/Bildzweig aber nicht zur normalen persönlichen Planetary-Berechnung. Keine hypothetischen Mischpayloads als UI-Verhalten ausgeben.

## Neue Vertragsbefunde – vor weiteren Rechenläufen klären

| Befund | Konkrete Quellen | Bedeutung und Grenze |
|---|---|---|
| Geburtszeittyp passt nicht zur Formelgrenze | `ClientBase.birth_time` ist `datetime.time` (`app/schemas/klienten.py:11`); API `281` ruft `model_dump()` auf. Installiertes Pydantic `main.py:427–477` verwendet standardmäßig Python-Modus. Signatur `329–336` ruft `birth_time.split(':')` in einem abgefangenen inneren Fehlerpfad auf. | Für ein natives `time`-Objekt scheitert dieser Zugriff; der Zeitanteil bleibt bei seinem Initialwert 0. Ein synthetischer Stringtest wäre kein Beleg des echten Schemaübergangs. Quelllokaler Befund, keine ausgeführte HTTP-/Pydantic-Reproduktion. |
| Registry-Projektion hat geringeren Kontextumfang | API `65–72` liefert nur `first_name`, `last_names`, `birth_date`, `birth_place`, `planet`; die benannten Registry-/Identitätsfelder enthalten keine Geburtszeit oder Geolocation. | Direkte Personendaten und ID-Auflösung sind nicht automatisch kontextgleich. Freies `metadata` existiert, wird aber in dieser Projektion nicht übernommen. Keine Aussage über tatsächlich gespeicherte Daten oder jeden anderen Modulpfad. |
| Gemischter ID-/Inline-Payload hat unterschiedliche Vorränge | API `_build_client_data:280–283` bevorzugt Inline-Daten; `_mirror_api_session:86–89` bevorzugt eine gesetzte Klienten-ID. | Ein solcher API-Payload kann Berechnungskontext und Sitzungszuordnung aus unterschiedlichen Eingaben ableiten. Keine nachgewiesene produktive Fehlzuordnung; der untersuchte JS-Builder erzeugt diese Kombination nicht. Rechteprüfung und Mandantensicherheit sind damit nicht getestet. |

Diese Befunde sind keine Erlaubnis, Serialisierung, Registry oder Formeln still zu reparieren. Die bereits bestätigte CUDA-/Quantum-/Iterationslücke bleibt ein eigener, unveränderter Istbefund aus dem [Parameterbericht](AURELIA_P3_RADI144_PARAMETER_2026-10-14.md).

Präzisierungen aus dem unabhängigen Review: Der abgefangene Fehler setzt nur den Geburtszeitanteil auf 0, nicht die ganze Geburtsfrequenz. Native Datumsobjekte werden von der bestehenden Datumsformel akzeptiert. Auch ein Zeitstring `HH:MM:SS` passt nicht zur Zweierzuweisung des Originalcodes; ein Wechsel auf JSON-Serialisierung allein ist daher keine belegte Reparatur. `calculate_planetary_influence` verwendet seinen Parameter `geolocation` im untersuchten Funktionskörper nicht. Dessen Auslassung aus der Registry-Projektion ist ein Kontextbefund, kein belegter numerischer Unterschied. Das separate Feld `geo_coords` hat einen anderen Verarbeitungspfad.

## Empfohlene nächste Probe und Grenzen

Originalstand erhalten; direkte Daten, ID-Projektion, Zeit als String/natives Objekt und gemischten ID-/Inline-Payload ausdrücklich als unterschiedliche Charakterisierungsfälle führen. Vor einem Eingriff getrennte Produktentscheidung und Regressionen. Keine stillschweigende Vereinheitlichung von Feldern oder Formelersetzung.

Für eine spätere numerische Probe die reinen Originalmethoden Name/Text/Geburt/Julian-Tag/Organuhr/Gewichtung und Gruppenaggregation mit synthetischen Daten und explizit festgehaltener Uhrzeit isolieren. Zeitquelle ist Recheninput: `generate_signature` ruft `datetime.now()` für die Organuhr und `utcnow()` für den Zeitstempel auf. Gleiche Person/Fokus/Seed allein belegen daher keine unbegrenzte Zeitinvarianz. Eine eingefrorene Prüfuhr ist ein ausgewiesener Testeingang, kein Produktfix.

NumPy-Methoden nicht durch `math` ersetzen und anschließend Originalparität behaupten. Geo mit positivem Radius und Planetary separat an gebundenem tatsächlichem NumPy prüfen; Bild mit realem synthetischem Medium/Pillow und Dateiberechtigungen separat. Synthetische Spygrenzen dürfen nur Übergabe/Kontrollfluss belegen. API-/Store-/Pydantic-/Bild-/HTTP-/Parallelitätsnachweise nicht aus einer reinen Formelprobe ableiten.

## Plan und Sicherung

Luna/max: begrenzte lesende Calleraufnahme. Leitung: Sicherungs-/Quellen-/ASTbindung und Konsolidierung. Astra/medium: unabhängiger SPEC→QUALITY-Review der neuen Vertragsbefunde abgeschlossen. Beide Helfer haben ausschließlich Quelltext gelesen. Noch keine neue Signaturreferenz ausgeführt; frühere Laufkennungen bleiben verbraucht und Gates geschlossen. Die Empfehlung zur Ist-Erhaltung ist noch keine neue Betreiberentscheidung und keine Reparaturfreigabe.

P3 insgesamt offen; danach vollständige P4-Siebenermatrix mit Aurelia/Modul_Templates vor P5-Strukturentscheidung. Führende Morphic-Quelle, RF-E1 und Linux-/Backendreferenzen behalten ihre eigenen Gates. Keine Original-/Live-/Routing-/normative Templateänderung, keine WSL-/Server-/Access-/Cloudaktion. Lokaler Prüfpunkt ersetzt keine F:-, Server-, Schlüssel- oder Gesamtprojektsicherung. Umfang/Abschluss erst nach erfolgreichem finalen Manifest-/Rücklesebeleg.


## Ergänzung – neue Betreiberentscheidung und blockierter Referenzversuch

Die zuvor offene Entscheidung wurde durch „Ja, fahre So fort“ erteilt: bekannte Originalbefunde unverändert charakterisieren. Neue Werkzeugvorbereitung mit20 isolierten Tests und unabhängigem Vorreview bestanden. Der folgende `context-run-1` scheitert jedoch bereits an der Git-Eigentümerschaftsprüfung vor Kindstart; Originalaufrufe weiterhin0. Keine neue numerische Signaturreferenz oder Reparatur. Git-/HEADstatus in diesem Prozess nicht bestätigt; Quellhashes unverändert. Details und nächster begrenzter Entscheidungsvorschlag im [Kontextbericht](AURELIA_P3_RADI144_KONTEXT_REFERENZ_2026-10-15.md). Der ältere Rohstatus war getrimmt; seine Bezeichnung als vorgemerkt beweist keinen Indexzustand. Aktuelle Aufnahme ` A AGENTS.md` ist ausdrücklich nur die frühere Rohbeobachtung, nicht der gescheiterte Nachcheck.
